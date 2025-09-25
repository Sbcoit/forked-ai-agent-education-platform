"""
Publishing API endpoints for PDF-to-Scenario functionality
Handles scenario publishing, marketplace browsing, cloning, and reviews
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time

from database.connection import get_db
from utilities.rate_limiter import check_anonymous_review_rate_limit
from utilities.auth import get_current_user, get_current_user_optional
from utilities.debug_logging import debug_log
from database.models import (
    Scenario, ScenarioPersona, ScenarioScene, ScenarioFile, 
    ScenarioReview, User, scene_personas, UserProgress,
    ConversationLog, SceneProgress
)
from database.schemas import (
    ScenarioPublishingResponse, ScenarioPublishRequest, MarketplaceFilters,
    MarketplaceResponse, ScenarioReviewCreate, ScenarioReviewResponse,
    AIProcessingResult, ScenarioPersonaResponse, ScenarioSceneResponse
)

router = APIRouter(prefix="/api/scenarios", tags=["Publishing"])

# Performance optimization constants
DB_EXECUTOR = ThreadPoolExecutor(max_workers=4)
BATCH_SIZE = 100  # For bulk database operations

# --- SCENARIO PUBLISHING ENDPOINTS ---

@router.post("/save")
async def save_scenario_draft(
    ai_result: dict,
    scenario_id: Optional[int] = Query(None, description="Scenario ID for updates (requires authentication)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Save AI processing results as a draft scenario
    Called when user clicks "Save" button
    
    Security: 
    - If scenario_id is provided, requires authentication and ownership verification
    - If no scenario_id, creates a new scenario (create-only behavior)
    - No longer allows title-based lookups for security
    """
    
    try:
        debug_log("Saving scenario as draft...")
        debug_log(f"AI result keys: {list(ai_result.keys())}")
        debug_log(f"Scenario ID: {scenario_id}")
        debug_log(f"Current user: {current_user.id if current_user else 'None'}")
        debug_log(f"Scenario ID type: {type(scenario_id)}")
        debug_log(f"Scenario ID is None: {scenario_id is None}")
        
        # Check if we received the wrapper response instead of direct AI result
        if "ai_result" in ai_result and isinstance(ai_result["ai_result"], dict):
            debug_log("Detected wrapper response, extracting ai_result...")
            actual_ai_result = ai_result["ai_result"]
        else:
            actual_ai_result = ai_result
        
        debug_log(f"Actual AI result keys: {list(actual_ai_result.keys())}")
        debug_log(f"Key figures count: {len(actual_ai_result.get('key_figures', []))}")
        debug_log(f"Scenes count: {len(actual_ai_result.get('scenes', []))}")
        
        # Extract title from AI result
        title = actual_ai_result.get("title", "Untitled Scenario")
        debug_log(f"Extracted title: {title}")
        
        scenario = None
        
        # Handle update case: scenario_id provided
        if scenario_id is not None:
            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required to update existing scenarios"
                )
            
            # Find scenario and verify ownership
            scenario = db.query(Scenario).filter_by(id=scenario_id).first()
            if not scenario:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario with ID {scenario_id} not found"
                )
            
            # Verify ownership
            if scenario.created_by != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only update scenarios you created"
                )
            
            debug_log(f"Updating existing scenario with ID: {scenario.id}")
            scenario.title = title
            scenario.description = actual_ai_result.get("description", "")
            scenario.challenge = actual_ai_result.get("description", "")
            scenario.learning_objectives = actual_ai_result.get("learning_outcomes", [])
            scenario.student_role = actual_ai_result.get("student_role", "Business Analyst")
            scenario.status = "draft"  # Set status to draft when saving
            scenario.updated_at = datetime.utcnow()
            db.flush()
            # Store existing scene and persona IDs for cleanup
            existing_scene_ids = [id for (id,) in db.query(ScenarioScene.id).filter(ScenarioScene.scenario_id == scenario.id).all()]
            existing_persona_ids = [id for (id,) in db.query(ScenarioPersona.id).filter(ScenarioPersona.scenario_id == scenario.id).all()]
            debug_log(f"Found {len(existing_scene_ids)} existing scenes and {len(existing_persona_ids)} existing personas to potentially clean up")
        
        # Handle create case: no scenario_id provided
        else:
            # Generate unique ID for new scenario
            import secrets
            unique_id = f"SC-{secrets.token_urlsafe(8).upper()}"
            debug_log(f"Generated unique_id: {unique_id}")
            
            # Create scenario record as draft
            scenario = Scenario(
                unique_id=unique_id,
                title=title,
                description=actual_ai_result.get("description", ""),
                challenge=actual_ai_result.get("description", ""),
                industry="Business",
                learning_objectives=actual_ai_result.get("learning_outcomes", []),
                student_role=actual_ai_result.get("student_role", "Business Analyst"),
                source_type="pdf_upload",
                pdf_title=title,
                pdf_source="Uploaded PDF",
                processing_version="1.0",
                is_public=False,  # Draft - not public
                allow_remixes=True,
                status="draft",  # Set status to draft when creating
                is_draft=True,  # Mark as draft
                published_version_id=None,  # No published version yet
                draft_of_id=None,  # This is the original draft
                created_by=current_user.id if current_user else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(scenario)
            db.flush()
            debug_log(f"Created draft scenario with ID: {scenario.id}")

        # Save personas - optimized batch operations
        persona_mapping = {}
        key_figures = actual_ai_result.get("key_figures", [])
        personas = actual_ai_result.get("personas", [])
        persona_list = key_figures if key_figures else personas
        debug_log(f"[OPTIMIZED] Saving {len(persona_list)} personas in batch...")
        new_persona_ids = []
        
        # Get existing personas in one query
        existing_personas = {}
        if 'existing_persona_ids' in locals() and existing_persona_ids:
            existing_persona_records = db.query(ScenarioPersona).filter(
                ScenarioPersona.id.in_(existing_persona_ids)
            ).all()
            existing_personas = {p.name: p for p in existing_persona_records}
        
        # Batch process personas
        personas_to_update = []
        personas_to_create = []
        
        for figure in persona_list:
            if isinstance(figure, dict) and figure.get("name"):
                traits = figure.get("personality_traits", {}) or figure.get("traits", {})
                
                if figure["name"] in existing_personas:
                    # Prepare for batch update
                    existing_persona = existing_personas[figure["name"]]
                    existing_persona.role = figure.get("role", "")
                    existing_persona.background = figure.get("background", "")
                    existing_persona.correlation = figure.get("correlation", "")
                    existing_persona.primary_goals = figure.get("primary_goals", []) or figure.get("primaryGoals", [])
                    existing_persona.personality_traits = traits
                    existing_persona.updated_at = datetime.utcnow()
                    personas_to_update.append(existing_persona)
                    persona_mapping[figure["name"]] = existing_persona.id
                    new_persona_ids.append(existing_persona.id)
                else:
                    # Prepare for batch creation
                    persona_data = {
                        "scenario_id": scenario.id,
                        "name": figure.get("name", ""),
                        "role": figure.get("role", ""),
                        "background": figure.get("background", ""),
                        "correlation": figure.get("correlation", ""),
                        "primary_goals": figure.get("primary_goals", []) or figure.get("primaryGoals", []),
                        "personality_traits": traits,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    personas_to_create.append((figure["name"], persona_data))
        
        # Execute batch updates
        if personas_to_update:
            for persona in personas_to_update:
                db.add(persona)
            debug_log(f"[OPTIMIZED] Updated {len(personas_to_update)} existing personas")
        
        # Execute batch creation
        if personas_to_create:
            for name, persona_data in personas_to_create:
                persona = ScenarioPersona(**persona_data)
                db.add(persona)
                db.flush()  # Get ID
                persona_mapping[name] = persona.id
                new_persona_ids.append(persona.id)
            debug_log(f"[OPTIMIZED] Created {len(personas_to_create)} new personas")

        # Save scenes - optimized batch operations
        scenes = actual_ai_result.get("scenes", [])
        debug_log(f"[OPTIMIZED] Saving {len(scenes)} scenes in batch...")
        new_scene_ids = []
        
        # Get existing scenes in one query
        existing_scenes = {}
        if 'existing_scene_ids' in locals() and existing_scene_ids:
            existing_scene_records = db.query(ScenarioScene).filter(
                ScenarioScene.id.in_(existing_scene_ids)
            ).all()
            existing_scenes = {scene.title: scene for scene in existing_scene_records}
        
        for i, scene in enumerate(scenes):
            if isinstance(scene, dict) and scene.get("title"):
                # Robustly extract success_metric
                success_metric = (
                    scene.get("successMetric") or
                    scene.get("success_metric") or
                    scene.get("success_criteria")
                )
                if not success_metric and scene.get("objectives"):
                    success_metric = scene["objectives"][0]
                
                scene_title = scene.get("title", "")
                
                # Check if this scene already exists
                if scene_title in existing_scenes:
                    # Update existing scene
                    existing_scene = existing_scenes[scene_title]
                    existing_scene.description = scene.get("description", "")
                    existing_scene.user_goal = scene.get("user_goal", "")
                    existing_scene.scene_order = scene.get("sequence_order", i + 1)
                    existing_scene.estimated_duration = scene.get("estimated_duration", 30)
                    existing_scene.image_url = scene.get("image_url", "")
                    existing_scene.image_prompt = f"Business scene: {scene_title}"
                    existing_scene.timeout_turns = int(scene.get("timeout_turns") or 15)
                    existing_scene.success_metric = success_metric
                    existing_scene.updated_at = datetime.utcnow()
                    db.add(existing_scene)
                    new_scene_ids.append(existing_scene.id)
                    debug_log(f"Updated existing scene: {scene_title}, success_metric: {success_metric}")
                    
                    # Update scene-persona relationships
                    # First, remove existing relationships for this scene
                    db.execute(scene_personas.delete().where(scene_personas.c.scene_id == existing_scene.id))
                    
                    # Then add new relationships
                    personas_involved = scene.get("personas_involved", [])
                    unique_persona_names = set(personas_involved)
                    for persona_name in unique_persona_names:
                        if persona_name in persona_mapping:
                            persona_id = persona_mapping[persona_name]
                            db.execute(
                                scene_personas.insert().values(
                                    scene_id=existing_scene.id,
                                    persona_id=persona_id,
                                    involvement_level="participant"
                                )
                            )
                            debug_log(f"Updated persona {persona_name} link to scene {scene_title}")
                else:
                    # Create new scene
                    scene_record = ScenarioScene(
                        scenario_id=scenario.id,
                        title=scene_title,
                        description=scene.get("description", ""),
                        user_goal=scene.get("user_goal", ""),
                        scene_order=scene.get("sequence_order", i + 1),  # Use sequence_order from frontend, fallback to loop index
                        estimated_duration=scene.get("estimated_duration", 30),
                        image_url=scene.get("image_url", ""),
                        image_prompt=f"Business scene: {scene_title}",
                        timeout_turns=int(scene.get("timeout_turns") or 15),
                        success_metric=success_metric,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(scene_record)
                    db.flush()
                    new_scene_ids.append(scene_record.id)
                    debug_log(f"Created new scene: {scene_record.title}, success_metric: {scene_record.success_metric}")
                    
                    # Link only involved personas to each scene
                    personas_involved = scene.get("personas_involved", [])
                    unique_persona_names = set(personas_involved)
                    for persona_name in unique_persona_names:
                        if persona_name in persona_mapping:
                            persona_id = persona_mapping[persona_name]
                            db.execute(
                                scene_personas.insert().values(
                                    scene_id=scene_record.id,
                                    persona_id=persona_id,
                                    involvement_level="participant"
                                )
                            )
                            debug_log(f"Linked persona {persona_name} to scene {scene_title}")
        
        # Clean up old scenes and personas that are no longer needed (only for existing scenarios)
        if 'existing_scene_ids' in locals() and existing_scene_ids:
            # Find scenes that were deleted (exist in old but not in new)
            deleted_scene_ids = [sid for sid in existing_scene_ids if sid not in new_scene_ids]
            if deleted_scene_ids:
                debug_log(f"Checking if {len(deleted_scene_ids)} scenes can be safely deleted: {deleted_scene_ids}")
                
                # Check if any of these scenes are still referenced by user_progress or conversation_logs
                from database.models import UserProgress, ConversationLog
                referenced_by_user_progress = db.query(UserProgress.current_scene_id).filter(
                    UserProgress.current_scene_id.in_(deleted_scene_ids)
                ).distinct().all()
                referenced_by_conversation_logs = db.query(ConversationLog.scene_id).filter(
                    ConversationLog.scene_id.in_(deleted_scene_ids)
                ).distinct().all()
                
                referenced_scene_ids = set()
                referenced_scene_ids.update([r[0] for r in referenced_by_user_progress if r[0] is not None])
                referenced_scene_ids.update([r[0] for r in referenced_by_conversation_logs if r[0] is not None])
                
                # Only delete scenes that are not referenced
                safe_to_delete = [sid for sid in deleted_scene_ids if sid not in referenced_scene_ids]
                unsafe_to_delete = [sid for sid in deleted_scene_ids if sid in referenced_scene_ids]
                
                if unsafe_to_delete:
                    debug_log(f"Cannot delete {len(unsafe_to_delete)} scenes as they are still referenced by user_progress or conversation_logs: {unsafe_to_delete}")
                
                if safe_to_delete:
                    debug_log(f"Safely deleting {len(safe_to_delete)} scenes: {safe_to_delete}")
                    # Delete scene-persona relationships for safe-to-delete scenes
                    db.execute(scene_personas.delete().where(scene_personas.c.scene_id.in_(safe_to_delete)))
                # Delete the scenes themselves
                    db.query(ScenarioScene).filter(ScenarioScene.id.in_(safe_to_delete)).delete()
                    debug_log(f"Deleted safe scenes and their relationships")
        
        # Initialize deleted_persona_ids outside the if block
        deleted_persona_ids = []
        if 'existing_persona_ids' in locals() and existing_persona_ids:
            # Find personas that were deleted (exist in old but not in new)
            deleted_persona_ids = [pid for pid in existing_persona_ids if pid not in new_persona_ids]
            if deleted_persona_ids:
                debug_log(f"Checking if {len(deleted_persona_ids)} personas can be safely deleted: {deleted_persona_ids}")
        
        # Only proceed with deletion if there are personas to delete
        if deleted_persona_ids:
            # Check if any of these personas are still referenced by conversation_logs
            from database.models import ConversationLog
            referenced_by_conversation_logs = db.query(ConversationLog.persona_id).filter(
                ConversationLog.persona_id.in_(deleted_persona_ids)
            ).distinct().all()
            
            referenced_persona_ids = set([r[0] for r in referenced_by_conversation_logs if r[0] is not None])
            
            # Only delete personas that are not referenced
            safe_to_delete_personas = [pid for pid in deleted_persona_ids if pid not in referenced_persona_ids]
            unsafe_to_delete_personas = [pid for pid in deleted_persona_ids if pid in referenced_persona_ids]
            
            if unsafe_to_delete_personas:
                debug_log(f"Cannot delete {len(unsafe_to_delete_personas)} personas as they are still referenced by conversation_logs: {unsafe_to_delete_personas}")
            
            if safe_to_delete_personas:
                debug_log(f"Safely deleting {len(safe_to_delete_personas)} personas: {safe_to_delete_personas}")
                # Delete scene-persona relationships for safe-to-delete personas
                db.execute(scene_personas.delete().where(scene_personas.c.persona_id.in_(safe_to_delete_personas)))
                # Delete the personas themselves
                db.query(ScenarioPersona).filter(ScenarioPersona.id.in_(safe_to_delete_personas)).delete()
                debug_log(f"Deleted safe personas and their relationships")
        
        db.commit()
        debug_log(f"Successfully saved draft scenario {scenario.id}")
        return {
            "status": "saved",
            "scenario_id": scenario.id,
            "message": f"Scenario '{title}' saved as draft"
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to save scenario: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save scenario: {str(e)}")

@router.post("/publish/{scenario_id}")
async def publish_scenario(
    scenario_id: int,
    publish_request: ScenarioPublishRequest,
    db: Session = Depends(get_db)
):
    """
    Publish a scenario to the marketplace
    Converts a draft scenario to public with metadata
    """
    
    # Get scenario with all related data
    scenario = db.query(Scenario).options(
        selectinload(Scenario.personas),
        selectinload(Scenario.scenes),
        selectinload(Scenario.files)
    ).filter(Scenario.id == scenario_id).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    debug_log(f"Publishing scenario {scenario_id}")
    debug_log(f"Found scenario title: '{scenario.title}'")
    debug_log(f"Found scenario description length: {len(scenario.description or '')}")
    debug_log(f"Scenario personas count: {len(scenario.personas)}")
    debug_log(f"Scenario scenes count: {len(scenario.scenes)}")
    
    # Validate scenario is ready for publishing
    if not scenario.title or not scenario.description:
        debug_log(f"Validation failed - title: '{scenario.title}', description: '{scenario.description}'")
        raise HTTPException(
            status_code=400, 
            detail="Scenario must have title and description to publish"
        )
    
    if not scenario.personas:
        raise HTTPException(
            status_code=400,
            detail="Scenario must have at least one persona to publish"
        )
    
    if not scenario.scenes:
        raise HTTPException(
            status_code=400,
            detail="Scenario must have at least one scene to publish"
        )
    
    # Check if this draft already has a published version
    existing_published = None
    debug_log(f"Draft scenario {scenario.id} (unique_id: {scenario.unique_id}) has published_version_id: {scenario.published_version_id}")
    
    # Refresh the scenario from the database to get the latest published_version_id
    db.refresh(scenario)
    debug_log(f"After refresh - published_version_id: {scenario.published_version_id}")
    
    if scenario.published_version_id:
        existing_published = db.query(Scenario).filter(
            Scenario.id == scenario.published_version_id
        ).first()
        if existing_published:
            debug_log(f"Found existing published version: {existing_published.id} (unique_id: {existing_published.unique_id})")
        else:
            debug_log(f"Published version {scenario.published_version_id} not found - will create new one")
    else:
        debug_log(f"No published version exists - will create new one")
    
    # ALWAYS update the existing scenario instead of creating a new one
    debug_log(f"Publishing scenario {scenario.id} (unique_id: {scenario.unique_id})")
    debug_log(f"Converting draft to published - keeping same ID and unique_id")
    
    # Update the existing scenario to be published
    scenario.is_draft = False  # Convert to published
    scenario.is_public = True
    scenario.status = "active"
    scenario.category = publish_request.category
    scenario.difficulty_level = publish_request.difficulty_level
    scenario.tags = publish_request.tags
    scenario.estimated_duration = publish_request.estimated_duration
    scenario.updated_at = datetime.utcnow()
    
    # The scenario keeps its original ID and unique_id
    published_scenario = scenario
    
    debug_log(f"Converted scenario {scenario.id} to published with unique_id: {scenario.unique_id}")
    
    # No need to copy personas and scenes - we're using the same scenario
    debug_log(f"Using existing personas and scenes for published scenario {published_scenario.id}")
    
    db.commit()
    db.refresh(published_scenario)
    
    return {
        "status": "published",
        "scenario_id": published_scenario.id,
        "draft_id": scenario.id,
        "message": f"Scenario '{scenario.title}' has been published to the marketplace"
    }

@router.get("/marketplace", response_model=MarketplaceResponse)
async def get_marketplace_scenarios(
    category: Optional[str] = Query(None),
    difficulty_level: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),  # Comma-separated tags
    min_rating: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Browse published scenarios in the marketplace
    Supports filtering, search, and pagination
    """
    
    # Build query for published scenarios
    query = db.query(Scenario).filter(Scenario.is_public == True)
    
    # Apply filters
    if category:
        query = query.filter(Scenario.category == category)
    
    if difficulty_level:
        query = query.filter(Scenario.difficulty_level == difficulty_level)
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        # Check if any of the requested tags exist in the scenario tags
        for tag in tag_list:
            query = query.filter(Scenario.tags.contains([tag]))
    
    if min_rating:
        query = query.filter(Scenario.rating_avg >= min_rating)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Scenario.title.ilike(search_term),
                Scenario.description.ilike(search_term),
                Scenario.industry.ilike(search_term)
            )
        )
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination and ordering
    scenarios = query.options(
        selectinload(Scenario.personas),
        selectinload(Scenario.scenes),
        selectinload(Scenario.creator)
    ).order_by(
        desc(Scenario.rating_avg),
        desc(Scenario.usage_count),
        desc(Scenario.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return MarketplaceResponse(
        scenarios=scenarios,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{scenario_id}/full", response_model=ScenarioPublishingResponse)
async def get_scenario_full(
    scenario_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get full scenario details with personas, scenes, and reviews
    Increments usage count for public scenarios
    
    Security:
    - Public scenarios can be accessed by anyone
    - Private scenarios can only be accessed by their creator
    """
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check access permissions
    if not scenario.is_public:
        if not current_user:
            raise HTTPException(
                status_code=401, 
                detail="Authentication required to access private scenarios"
            )
        if scenario.created_by != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="You can only access scenarios you created"
            )
    
    if scenario.is_public:
        scenario.usage_count += 1
        db.commit()
    reviews = db.query(ScenarioReview).options(
        selectinload(ScenarioReview.reviewer)
    ).filter(
        ScenarioReview.scenario_id == scenario_id
    ).order_by(desc(ScenarioReview.created_at)).limit(10).all()
    scenario_dict = scenario.__dict__.copy()
    scenario_dict['reviews'] = reviews
    scenes = db.query(ScenarioScene).filter(ScenarioScene.scenario_id == scenario_id).order_by(ScenarioScene.scene_order).all()
    from database.schemas import ScenarioSceneResponse
    scene_dicts = []
    for scene in scenes:
        scene_data = scene.__dict__.copy()
        # Build personas as dicts and decode primary_goals
        persona_dicts = []
        if hasattr(scene, 'personas') and scene.personas:
            for persona in scene.personas:
                persona_data = persona.__dict__.copy()
                if 'primary_goals' in persona_data and isinstance(persona_data['primary_goals'], str):
                    try:
                        persona_data['primary_goals'] = json.loads(persona_data['primary_goals'])
                    except Exception:
                        persona_data['primary_goals'] = []
                persona_dicts.append(persona_data)
        scene_data['personas'] = persona_dicts
        scene_dicts.append(scene_data)
    scenario_dict['scenes'] = [ScenarioSceneResponse.model_validate(scene).model_dump() for scene in scene_dicts]
    # Ensure all required fields for ScenarioPublishingResponse are present
    required_fields = [
        'id', 'title', 'description', 'challenge', 'industry', 'learning_objectives',
        'student_role', 'category', 'difficulty_level', 'estimated_duration', 'tags',
        'pdf_title', 'pdf_source', 'processing_version', 'rating_avg', 'rating_count',
        'source_type', 'is_public', 'is_template', 'allow_remixes', 'usage_count',
        'clone_count', 'created_by', 'created_at', 'updated_at'
    ]
    for field in required_fields:
        if field not in scenario_dict:
            scenario_dict[field] = getattr(scenario, field, None)
    # Fix learning_objectives if it's a string
    if isinstance(scenario_dict.get('learning_objectives'), str):
        items = [item.strip() for item in scenario_dict['learning_objectives'].split('\n') if item.strip()]
        scenario_dict['learning_objectives'] = items
    return scenario_dict

@router.post("/{scenario_id}/clone")
async def clone_scenario(
    scenario_id: int,
    db: Session = Depends(get_db)
):
    """
    Clone a scenario for editing
    Creates a copy of the scenario with all personas and scenes
    """
    
    # Get original scenario with all related data
    original = db.query(Scenario).options(
        selectinload(Scenario.personas),
        selectinload(Scenario.scenes).selectinload(ScenarioScene.personas),
        selectinload(Scenario.files)
    ).filter(Scenario.id == scenario_id).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if not original.is_public and not original.allow_remixes:
        raise HTTPException(
            status_code=403, 
            detail="This scenario cannot be cloned"
        )
    
    # Create new scenario (clone)
    new_scenario = Scenario(
        title=f"{original.title} (Copy)",
        description=original.description,
        challenge=original.challenge,
        industry=original.industry,
        learning_objectives=original.learning_objectives,
        student_role=original.student_role,
        category=original.category,
        difficulty_level=original.difficulty_level,
        estimated_duration=original.estimated_duration,
        tags=original.tags,
        pdf_title=original.pdf_title,
        pdf_source=original.pdf_source,
        processing_version=original.processing_version,
        source_type="cloned",
        is_public=False,  # Clones start as private
        allow_remixes=True,
        created_by=None,  # No user authentication yet
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_scenario)
    db.flush()  # Get the new scenario ID
    
    # Clone personas
    persona_mapping = {}  # old_id -> new_id
    for persona in original.personas:
        new_persona = ScenarioPersona(
            scenario_id=new_scenario.id,
            name=persona.name,
            role=persona.role,
            background=persona.background,
            correlation=persona.correlation,
            primary_goals=persona.primary_goals,
            personality_traits=persona.personality_traits
        )
        db.add(new_persona)
        db.flush()
        persona_mapping[persona.id] = new_persona.id
    
    # Clone scenes
    for scene in original.scenes:
        new_scene = ScenarioScene(
            scenario_id=new_scenario.id,
            title=scene.title,
            description=scene.description,
            user_goal=scene.user_goal,
            scene_order=scene.scene_order,
            estimated_duration=scene.estimated_duration,
            image_url=scene.image_url,
            image_prompt=scene.image_prompt
        )
        db.add(new_scene)
        db.flush()
        
        # Clone scene-persona relationships
        for persona in scene.personas:
            if persona.id in persona_mapping:
                new_persona_id = persona_mapping[persona.id]
                # Add relationship through junction table
                db.execute(
                    scene_personas.insert().values(
                        scene_id=new_scene.id,
                        persona_id=new_persona_id,
                        involvement_level='participant'
                    )
                )
    
    # Clone files (metadata only, not actual file content)
    for file in original.files:
        new_file = ScenarioFile(
            scenario_id=new_scenario.id,
            filename=f"cloned_{file.filename}",
            file_type=file.file_type,
            original_content=file.original_content,
            processed_content=file.processed_content,
            processing_status="completed"
        )
        db.add(new_file)
    
    # Update clone count
    original.clone_count += 1
    
    db.commit()
    db.refresh(new_scenario)
    
    return {
        "status": "cloned",
        "original_scenario_id": scenario_id,
        "new_scenario_id": new_scenario.id,
        "message": f"Scenario cloned successfully as '{new_scenario.title}'"
    }

@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a scenario by marking it as deleted.
    Only the scenario creator can delete their scenarios.
    User progress data is preserved in the archive.
    """
    from services.soft_deletion import SoftDeletionService
    
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.deleted_at.is_(None)  # Only get non-deleted scenarios
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check if the current user owns this scenario
    if scenario.created_by != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only delete scenarios you created"
        )

    # Use soft deletion service
    service = SoftDeletionService(db)
    success = service.soft_delete_scenario(
        scenario_id=scenario_id,
        deleted_by=current_user.id,
        reason="User deletion"
    )
    
    if not success:
        raise HTTPException(
            status_code=500, 
            detail="Failed to delete scenario"
        )
    
    return {
        "status": "success", 
        "message": f"Scenario {scenario_id} deleted successfully. User progress data has been archived."
    }

@router.post("/cleanup/archives")
async def cleanup_archives(
    days_old: int = Query(30, ge=1, le=365, description="Days after which to clean up archives"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clean up old archived user progress records
    Only admin users can perform cleanup
    """
    from services.soft_deletion import SoftDeletionService
    
    # Check if user is admin (you can adjust this logic)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only admin users can perform cleanup"
        )
    
    service = SoftDeletionService(db)
    
    # Get stats before cleanup
    stats_before = service.get_archive_stats()
    
    # Run cleanup
    cleaned_count = service.cleanup_old_archives(days_old)
    
    # Get stats after cleanup
    stats_after = service.get_archive_stats()
    
    return {
        "status": "success",
        "message": f"Cleanup completed. Removed {cleaned_count} records older than {days_old} days.",
        "stats_before": stats_before,
        "stats_after": stats_after,
        "records_cleaned": cleaned_count
    }

@router.get("/cleanup/stats")
async def get_cleanup_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get archive statistics
    """
    from services.soft_deletion import SoftDeletionService
    
    service = SoftDeletionService(db)
    stats = service.get_archive_stats()
    
    return {
        "status": "success",
        "archive_stats": stats
    }

# --- SCENARIO REVIEW ENDPOINTS ---

@router.post("/{scenario_id}/reviews", response_model=ScenarioReviewResponse)
async def create_scenario_review(
    scenario_id: int,
    review: ScenarioReviewCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Create a review for a scenario
    Updates the scenario's average rating
    Includes rate limiting for anonymous reviews
    """
    
    # Check rate limit for anonymous reviews
    rate_limit_result = check_anonymous_review_rate_limit(request)
    
    # Check if scenario exists
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # For now, skip user validation since we don't have authentication
    # TODO: Implement proper user authentication for reviews
    
    # Create new review (without user validation for now)
    new_review = ScenarioReview(
        scenario_id=scenario_id,
        reviewer_id=None,  # No user authentication yet
        rating=review.rating,
        review_text=review.review_text,
        pros=review.pros,
        cons=review.cons,
        use_case=review.use_case
    )
    
    db.add(new_review)
    
    # Update scenario rating
    avg_rating = db.query(func.avg(ScenarioReview.rating)).filter(
        ScenarioReview.scenario_id == scenario_id
    ).scalar()
    
    rating_count = db.query(func.count(ScenarioReview.id)).filter(
        ScenarioReview.scenario_id == scenario_id
    ).scalar()
    
    scenario.rating_avg = round(float(avg_rating or 0), 2)
    scenario.rating_count = int(rating_count or 0) + 1  # Include the new review
    
    db.commit()
    db.refresh(new_review)
    
    # Add rate limit headers to response
    from utilities.rate_limiter import rate_limiter, ANONYMOUS_REVIEW_CONFIG
    headers = rate_limiter.get_rate_limit_headers(rate_limit_result, ANONYMOUS_REVIEW_CONFIG)
    for header_name, header_value in headers.items():
        response.headers[header_name] = header_value
    
    return new_review

@router.get("/{scenario_id}/reviews", response_model=List[ScenarioReviewResponse])
async def get_scenario_reviews(
    scenario_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get reviews for a scenario with pagination
    """
    
    reviews = db.query(ScenarioReview).options(
        selectinload(ScenarioReview.reviewer)
    ).filter(
        ScenarioReview.scenario_id == scenario_id
    ).order_by(
        desc(ScenarioReview.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return reviews

# --- UTILITY ENDPOINTS ---

@router.get("/categories")
async def get_scenario_categories(db: Session = Depends(get_db)):
    """
    Get available scenario categories
    """
    
    categories = db.query(Scenario.category).filter(
        Scenario.category.isnot(None),
        Scenario.is_public == True
    ).distinct().all()
    
    return {
        "categories": [cat[0] for cat in categories if cat[0]],
        "predefined": [
            "Leadership", "Strategy", "Operations", "Marketing", 
            "Finance", "Human Resources", "Technology", "Innovation"
        ]
    }

@router.get("/difficulty-levels")
async def get_difficulty_levels():
    """
    Get available difficulty levels
    """
    
    return {
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "descriptions": {
            "Beginner": "Suitable for students new to business case studies",
            "Intermediate": "Requires basic business knowledge and analytical skills",
            "Advanced": "Complex scenarios requiring deep business expertise"
        }
    } 
