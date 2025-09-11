"""
Publishing API endpoints for PDF-to-Scenario functionality
Handles scenario publishing, marketplace browsing, cloning, and reviews
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
import json
from datetime import datetime

from database.connection import get_db
from utilities.rate_limiter import check_anonymous_review_rate_limit
from utilities.auth import get_current_user, get_current_user_optional
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
        print("[DEBUG] Saving scenario as draft...")
        print(f"[DEBUG] AI result keys: {list(ai_result.keys())}")
        print(f"[DEBUG] Scenario ID: {scenario_id}")
        print(f"[DEBUG] Current user: {current_user.id if current_user else 'None'}")
        
        # Check if we received the wrapper response instead of direct AI result
        if "ai_result" in ai_result and isinstance(ai_result["ai_result"], dict):
            print("[DEBUG] Detected wrapper response, extracting ai_result...")
            actual_ai_result = ai_result["ai_result"]
        else:
            actual_ai_result = ai_result
        
        print(f"[DEBUG] Actual AI result keys: {list(actual_ai_result.keys())}")
        print(f"[DEBUG] Key figures count: {len(actual_ai_result.get('key_figures', []))}")
        print(f"[DEBUG] Scenes count: {len(actual_ai_result.get('scenes', []))}")
        
        # Extract title from AI result
        title = actual_ai_result.get("title", "Untitled Scenario")
        print(f"[DEBUG] Extracted title: {title}")
        
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
            
            print(f"[DEBUG] Updating existing scenario with ID: {scenario.id}")
            scenario.title = title
            scenario.description = actual_ai_result.get("description", "")
            scenario.challenge = actual_ai_result.get("description", "")
            scenario.learning_objectives = actual_ai_result.get("learning_outcomes", [])
            scenario.student_role = actual_ai_result.get("student_role", "Business Analyst")
            scenario.updated_at = datetime.utcnow()
            db.flush()
            
            # Store existing scene and persona IDs for cleanup
            existing_scene_ids = [s.id for s in db.query(ScenarioScene.id).filter(ScenarioScene.scenario_id == scenario.id).all()]
            existing_persona_ids = [p.id for p in db.query(ScenarioPersona.id).filter(ScenarioPersona.scenario_id == scenario.id).all()]
            print(f"[DEBUG] Found {len(existing_scene_ids)} existing scenes and {len(existing_persona_ids)} existing personas to potentially clean up")
        
        # Handle create case: no scenario_id provided
        else:
            # Create scenario record as draft
            scenario = Scenario(
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
                created_by=current_user.id if current_user else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(scenario)
            db.flush()
            print(f"[DEBUG] Created draft scenario with ID: {scenario.id}")

        # Save personas
        persona_mapping = {}
        key_figures = actual_ai_result.get("key_figures", [])
        personas = actual_ai_result.get("personas", [])
        persona_list = key_figures if key_figures else personas
        print(f"[DEBUG] Saving {len(persona_list)} personas...")
        new_persona_ids = []
        for figure in persona_list:
            if isinstance(figure, dict) and figure.get("name"):
                # Debug: Log the traits being received
                traits = figure.get("personality_traits", {}) or figure.get("traits", {})
                print(f"[DEBUG] Persona {figure['name']} traits received: {traits}")
                
                persona = ScenarioPersona(
                    scenario_id=scenario.id,
                    name=figure.get("name", ""),
                    role=figure.get("role", ""),
                    background=figure.get("background", ""),
                    correlation=figure.get("correlation", ""),
                    primary_goals=figure.get("primary_goals", []) or figure.get("primaryGoals", []),
                    personality_traits=traits,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(persona)
                db.flush()
                persona_mapping[figure["name"]] = persona.id
                new_persona_ids.append(persona.id)
                print(f"[DEBUG] Created persona: {figure['name']} with ID: {persona.id} and traits: {persona.personality_traits}")

        # Save scenes
        scenes = actual_ai_result.get("scenes", [])
        print(f"[DEBUG] Saving {len(scenes)} scenes...")
        new_scene_ids = []
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
                scene_record = ScenarioScene(
                    scenario_id=scenario.id,
                    title=scene.get("title", ""),
                    description=scene.get("description", ""),
                    user_goal=scene.get("user_goal", ""),
                    scene_order=scene.get("sequence_order", i + 1),  # Use sequence_order from frontend, fallback to loop index
                    estimated_duration=scene.get("estimated_duration", 30),
                    image_url=scene.get("image_url", ""),
                    image_prompt=f"Business scene: {scene.get('title', '')}",
                    timeout_turns=int(scene.get("timeout_turns") or 15),
                    success_metric=success_metric,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(scene_record)
                db.flush()
                new_scene_ids.append(scene_record.id)
                print(f"[DEBUG] Saved scene: {scene_record.title}, success_metric: {scene_record.success_metric}")
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
                        print(f"[DEBUG] Linked persona {persona_name} to scene {scene['title']}")
        
        # Clean up old scenes and personas that are no longer needed (only for existing scenarios)
        if 'existing_scene_ids' in locals() and existing_scene_ids:
            # Find scenes that were deleted (exist in old but not in new)
            deleted_scene_ids = [sid for sid in existing_scene_ids if sid not in new_scene_ids]
            if deleted_scene_ids:
                print(f"[DEBUG] Cleaning up {len(deleted_scene_ids)} deleted scenes: {deleted_scene_ids}")
                # Delete scene-persona relationships for deleted scenes
                db.execute(scene_personas.delete().where(scene_personas.c.scene_id.in_(deleted_scene_ids)))
                # Delete the scenes themselves
                db.query(ScenarioScene).filter(ScenarioScene.id.in_(deleted_scene_ids)).delete()
                print(f"[DEBUG] Deleted scenes and their relationships")
        
        if 'existing_persona_ids' in locals() and existing_persona_ids:
            # Find personas that were deleted (exist in old but not in new)
            deleted_persona_ids = [pid for pid in existing_persona_ids if pid not in new_persona_ids]
            if deleted_persona_ids:
                print(f"[DEBUG] Cleaning up {len(deleted_persona_ids)} deleted personas: {deleted_persona_ids}")
                # Delete scene-persona relationships for deleted personas
                db.execute(scene_personas.delete().where(scene_personas.c.persona_id.in_(deleted_persona_ids)))
                # Delete the personas themselves
                db.query(ScenarioPersona).filter(ScenarioPersona.id.in_(deleted_persona_ids)).delete()
                print(f"[DEBUG] Deleted personas and their relationships")
        
        db.commit()
        print(f"[DEBUG] Successfully saved draft scenario {scenario.id}")
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
    
    print(f"[DEBUG] Publishing scenario {scenario_id}")
    print(f"[DEBUG] Found scenario title: '{scenario.title}'")
    print(f"[DEBUG] Found scenario description length: {len(scenario.description or '')}")
    print(f"[DEBUG] Scenario personas count: {len(scenario.personas)}")
    print(f"[DEBUG] Scenario scenes count: {len(scenario.scenes)}")
    
    # Validate scenario is ready for publishing
    if not scenario.title or not scenario.description:
        print(f"[DEBUG] Validation failed - title: '{scenario.title}', description: '{scenario.description}'")
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
    
    # Update scenario with publishing metadata
    scenario.category = publish_request.category
    scenario.difficulty_level = publish_request.difficulty_level
    scenario.tags = publish_request.tags
    scenario.estimated_duration = publish_request.estimated_duration
    scenario.is_public = True
    scenario.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(scenario)
    
    return {
        "status": "published",
        "scenario_id": scenario_id,
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
    scenario = db.query(Scenario).options(
        selectinload(Scenario.personas),
        selectinload(Scenario.scenes).selectinload(ScenarioScene.personas),
        selectinload(Scenario.files),
        selectinload(Scenario.creator)
    ).filter(Scenario.id == scenario_id).first()
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
    Delete a scenario and all related data by scenario ID.
    Only the scenario creator can delete their scenarios.
    """
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check if the current user owns this scenario
    if scenario.created_by != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only delete scenarios you created"
        )

    # Get all related IDs first
    scene_ids = [s.id for s in db.query(ScenarioScene.id).filter(ScenarioScene.scenario_id == scenario_id).all()]
    persona_ids = [p.id for p in db.query(ScenarioPersona.id).filter(ScenarioPersona.scenario_id == scenario_id).all()]
    user_progress_ids = [up.id for up in db.query(UserProgress.id).filter(UserProgress.scenario_id == scenario_id).all()]

    # Delete conversation logs first (they reference multiple tables)
    # Use OR condition to delete all related logs in one query
    from sqlalchemy import or_
    conditions = []
    if scene_ids:
        conditions.append(ConversationLog.scene_id.in_(scene_ids))
    if persona_ids:
        conditions.append(ConversationLog.persona_id.in_(persona_ids))
    if user_progress_ids:
        conditions.append(ConversationLog.user_progress_id.in_(user_progress_ids))
    
    if conditions:
        db.query(ConversationLog).filter(or_(*conditions)).delete(synchronize_session=False)

    # Delete scene progress (references user_progress and scenes)
    if user_progress_ids:
        db.query(SceneProgress).filter(SceneProgress.user_progress_id.in_(user_progress_ids)).delete()

    # Delete related user progress
    db.query(UserProgress).filter(UserProgress.scenario_id == scenario_id).delete()
    
    # Delete related scene_personas links
    if scene_ids:
        db.execute(scene_personas.delete().where(scene_personas.c.scene_id.in_(scene_ids)))
    
    # Delete related personas
    db.query(ScenarioPersona).filter(ScenarioPersona.scenario_id == scenario_id).delete()
    
    # Delete related scenes
    db.query(ScenarioScene).filter(ScenarioScene.scenario_id == scenario_id).delete()
    
    # Delete related files
    db.query(ScenarioFile).filter(ScenarioFile.scenario_id == scenario_id).delete()
    
    # Delete related reviews
    db.query(ScenarioReview).filter(ScenarioReview.scenario_id == scenario_id).delete()
    
    # Delete the scenario itself
    db.delete(scenario)
    db.commit()
    return {"status": "success", "message": f"Scenario {scenario_id} deleted."}

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
