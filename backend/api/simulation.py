"""
Sequential Timeline Simulation API
Handles guided simulation with AI personas, goal validation, and progress tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any
import json
import time
from datetime import datetime, timedelta
import openai
import os

from database.connection import get_db
from database.models import (
    Scenario, ScenarioScene, ScenarioPersona, User,
    UserProgress, SceneProgress, ConversationLog
)
from database.schemas import (
    SimulationStartRequest, SimulationStartResponse, SimulationScenarioResponse,
    SimulationChatRequest, SimulationChatResponse,
    GoalValidationRequest, GoalValidationResponse,
    SceneProgressRequest, SceneProgressResponse,
    UserProgressResponse, SimulationAnalyticsResponse,
    ScenarioResponse, ScenarioSceneResponse, ScenarioPersonaResponse
)
from .chat_orchestrator import ChatOrchestrator, SimulationState

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/start", response_model=SimulationStartResponse)
async def start_simulation(
    request: SimulationStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new simulation or resume existing one"""
    
    # Verify scenario exists
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Get first scene in order
    first_scene = db.query(ScenarioScene).filter(
        ScenarioScene.scenario_id == request.scenario_id
    ).order_by(ScenarioScene.scene_order).first()
    
    if not first_scene:
        raise HTTPException(status_code=400, detail="Scenario has no scenes")
    
    # Check for existing progress
    existing_progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == request.user_id,
            UserProgress.scenario_id == request.scenario_id,
            UserProgress.simulation_status.in_(["not_started", "in_progress"])
        )
    ).first()
    
    if existing_progress:
        # Resume existing simulation
        user_progress = existing_progress
        user_progress.session_count += 1
        user_progress.last_activity = datetime.utcnow()
        
        # Get current scene
        if user_progress.current_scene_id:
            current_scene = db.query(ScenarioScene).filter(
                ScenarioScene.id == user_progress.current_scene_id
            ).first()
        else:
            current_scene = first_scene
            user_progress.current_scene_id = first_scene.id
            user_progress.simulation_status = "in_progress"
    else:
        # Get all scenes and personas for orchestrator setup
        all_scenes = db.query(ScenarioScene).filter(
            ScenarioScene.scenario_id == scenario.id
        ).order_by(ScenarioScene.order_index).all()
        
        all_personas = db.query(ScenarioPersona).filter(
            ScenarioPersona.scenario_id == scenario.id
        ).all()
        
        # Prepare scenario data for orchestrator
        scenario_data = {
            "id": scenario.id,
            "title": scenario.title,
            "description": scenario.description,
            "challenge": scenario.challenge,
            "scenes": [
                {
                    "id": scene.id,
                    "title": scene.title,
                    "description": scene.description,
                    "objectives": scene.objectives or ["Complete the scene interaction"],
                    "image_url": scene.image_url,
                    "agent_ids": [p.name.lower().replace(" ", "_") for p in all_personas],  # All personas available
                    "max_turns": 20,
                    "success_criteria": f"User achieves: {', '.join(scene.objectives or ['scene completion'])}"
                }
                for scene in all_scenes
            ],
            "personas": [
                {
                    "id": persona.name.lower().replace(" ", "_"),
                    "identity": {
                        "name": persona.name,
                        "role": persona.role,
                        "bio": persona.background or "Professional team member"
                    },
                    "personality": {
                        "goals": persona.goals or ["Support team objectives"],
                        "traits": persona.personality or "Professional and collaborative"
                    }
                }
                for persona in all_personas
            ]
        }
        
        # Create new progress record with orchestrator state
        user_progress = UserProgress(
            user_id=request.user_id,
            scenario_id=request.scenario_id,
            current_scene_id=first_scene.id,
            simulation_status="waiting_for_begin",  # Changed from "in_progress"
            session_count=1,
            scenes_completed=[],
            orchestrator_data=scenario_data,  # Store orchestrator data
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        db.add(user_progress)
        db.flush()  # Get ID
        
        # Create scene progress for first scene
        scene_progress = SceneProgress(
            user_progress_id=user_progress.id,
            scene_id=first_scene.id,
            status="in_progress",
            started_at=datetime.utcnow()
        )
        db.add(scene_progress)
        current_scene = first_scene
    
    db.commit()
    
    # Prepare response data
    scenario_data = SimulationScenarioResponse(
        id=scenario.id,
        title=scenario.title,
        description=scenario.description,
        challenge=scenario.challenge,
        industry=scenario.industry,
        learning_objectives=scenario.learning_objectives or [],
        student_role=scenario.student_role
    )
    
    # Get all personas for the scenario (not just scene-specific ones)
    scene_personas = db.query(ScenarioPersona).filter(
        ScenarioPersona.scenario_id == scenario.id
    ).all()
    
    personas_data = [
        ScenarioPersonaResponse(
            id=persona.id,
            scenario_id=persona.scenario_id,
            name=persona.name,
            role=persona.role,
            background=persona.background,
            correlation=persona.correlation,
            primary_goals=persona.primary_goals or [],
            personality_traits=persona.personality_traits or {},
            created_at=persona.created_at,
            updated_at=persona.updated_at
        ) for persona in scene_personas
    ]
    
    scene_data = ScenarioSceneResponse(
        id=current_scene.id,
        scenario_id=current_scene.scenario_id,
        title=current_scene.title,
        description=current_scene.description,
        user_goal=current_scene.user_goal,
        scene_order=current_scene.scene_order,
        estimated_duration=current_scene.estimated_duration,
        image_url=current_scene.image_url,
        image_prompt=current_scene.image_prompt,
        created_at=current_scene.created_at,
        updated_at=current_scene.updated_at,
        personas=personas_data
    )
    
    return SimulationStartResponse(
        user_progress_id=user_progress.id,
        scenario=scenario_data,
        current_scene=scene_data,
        simulation_status=user_progress.simulation_status
    )

@router.post("/chat", response_model=SimulationChatResponse)
async def chat_with_persona(
    request: SimulationChatRequest,
    db: Session = Depends(get_db)
):
    """Send message to AI persona and get response"""
    
    start_time = time.time()
    
    # Get user progress and validate
    user_progress = db.query(UserProgress).filter(
        UserProgress.id == request.user_progress_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    # Get scene and personas
    scene = db.query(ScenarioScene).filter(
        ScenarioScene.id == request.scene_id
    ).first()
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get all personas for the scenario
    scene_personas = db.query(ScenarioPersona).filter(
        ScenarioPersona.scenario_id == scene.scenario_id
    ).all()
    
    if not scene_personas:
        raise HTTPException(status_code=400, detail="No personas found for scene")
    
    # Determine target persona
    if request.target_persona_id:
        target_persona = next((p for p in scene_personas if p.id == request.target_persona_id), None)
        if not target_persona:
            raise HTTPException(status_code=400, detail="Target persona not found in scene")
    else:
        # Use first persona if none specified
        target_persona = scene_personas[0]
    
    # Get recent conversation context
    recent_messages = db.query(ConversationLog).filter(
        and_(
            ConversationLog.user_progress_id == request.user_progress_id,
            ConversationLog.scene_id == request.scene_id
        )
    ).order_by(desc(ConversationLog.message_order)).limit(10).all()
    
    # Get current attempt number
    scene_progress = db.query(SceneProgress).filter(
        and_(
            SceneProgress.user_progress_id == request.user_progress_id,
            SceneProgress.scene_id == request.scene_id
        )
    ).first()
    
    current_attempt = scene_progress.attempts if scene_progress else 1
    
    # Get next message order
    last_message = db.query(ConversationLog).filter(
        and_(
            ConversationLog.user_progress_id == request.user_progress_id,
            ConversationLog.scene_id == request.scene_id
        )
    ).order_by(desc(ConversationLog.message_order)).first()
    
    next_message_order = (last_message.message_order + 1) if last_message else 1
    
    # Log user message
    user_log = ConversationLog(
        user_progress_id=request.user_progress_id,
        scene_id=request.scene_id,
        message_type="user",
        sender_name="User",
        message_content=request.message,
        message_order=next_message_order,
        attempt_number=current_attempt,
        timestamp=datetime.utcnow()
    )
    db.add(user_log)
    db.flush()
    
    # Build AI context
    conversation_context = []
    for msg in reversed(recent_messages[-6:]):  # Last 6 messages for context
        role = "user" if msg.message_type == "user" else "assistant"
        conversation_context.append({
            "role": role,
            "content": msg.message_content
        })
    
    # Add current user message
    conversation_context.append({
        "role": "user",
        "content": request.message
    })
    
    # Create AI prompt with persona and scene context
    system_prompt = f"""You are {target_persona.name}, a {target_persona.role} in this business simulation.

PERSONA BACKGROUND:
{target_persona.background}

PERSONA CORRELATION TO CASE:
{target_persona.correlation}

PERSONALITY TRAITS: {json.dumps(target_persona.personality_traits)}

SCENE CONTEXT:
Title: {scene.title}
Description: {scene.description}
User Goal: {scene.user_goal}

SIMULATION INSTRUCTIONS:
- Stay in character as {target_persona.name}
- Respond naturally based on your role and personality
- Help guide the user toward the scene goal through realistic business interaction
- Don't directly give away answers, but provide realistic business insights
- Keep responses concise and professional
- If the user seems stuck, provide subtle hints through natural conversation
"""
    
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + conversation_context,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        processing_time = time.time() - start_time
        
        # Log AI response
        ai_log = ConversationLog(
            user_progress_id=request.user_progress_id,
            scene_id=request.scene_id,
            message_type="ai_persona",
            sender_name=target_persona.name,
            persona_id=target_persona.id,
            message_content=ai_response,
            message_order=next_message_order + 1,
            attempt_number=current_attempt,
            ai_model_version="gpt-4o",
            processing_time=processing_time,
            timestamp=datetime.utcnow()
        )
        db.add(ai_log)
        
        # Update scene progress
        if scene_progress:
            scene_progress.messages_sent += 1
            scene_progress.ai_responses += 1
        else:
            scene_progress = SceneProgress(
                user_progress_id=request.user_progress_id,
                scene_id=request.scene_id,
                status="in_progress",
                messages_sent=1,
                ai_responses=1,
                attempts=1,
                started_at=datetime.utcnow()
            )
            db.add(scene_progress)
        
        # Update user progress
        user_progress.last_activity = datetime.utcnow()
        
        db.commit()
        
        return SimulationChatResponse(
            message_id=ai_log.id,
            persona_name=target_persona.name,
            persona_response=ai_response,
            message_order=next_message_order + 1,
            processing_time=processing_time,
            ai_model_version="gpt-4o"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )

@router.post("/validate-goal", response_model=GoalValidationResponse)
async def validate_scene_goal(
    request: GoalValidationRequest,
    db: Session = Depends(get_db)
):
    """Check if user has achieved the scene goal"""
    
    # Get user progress and scene
    user_progress = db.query(UserProgress).filter(
        UserProgress.id == request.user_progress_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    scene = db.query(ScenarioScene).filter(
        ScenarioScene.id == request.scene_id
    ).first()
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get recent conversation
    recent_messages = db.query(ConversationLog).filter(
        and_(
            ConversationLog.user_progress_id == request.user_progress_id,
            ConversationLog.scene_id == request.scene_id
        )
    ).order_by(desc(ConversationLog.message_order)).limit(10).all()
    
    if not recent_messages:
        return GoalValidationResponse(
            goal_achieved=False,
            confidence_score=0.0,
            reasoning="No conversation yet",
            next_action="continue"
        )
    
    # Build conversation summary for AI evaluation
    conversation_summary = []
    for msg in reversed(recent_messages):
        speaker = msg.sender_name or "System"
        conversation_summary.append(f"{speaker}: {msg.message_content}")
    
    conversation_text = "\n".join(conversation_summary)
    
    # Get scene progress for attempt tracking
    scene_progress = db.query(SceneProgress).filter(
        and_(
            SceneProgress.user_progress_id == request.user_progress_id,
            SceneProgress.scene_id == request.scene_id
        )
    ).first()
    
    current_attempts = scene_progress.attempts if scene_progress else 0
    max_attempts = scene.max_attempts or 5
    
    # AI evaluation prompt
    evaluation_prompt = f"""Evaluate whether the user has achieved the scene goal based on the conversation.

SCENE GOAL: {scene.user_goal}

SCENE DESCRIPTION: {scene.description}

RECENT CONVERSATION:
{conversation_text}

CURRENT ATTEMPTS: {current_attempts}/{max_attempts}

Analyze the conversation and determine:
1. Has the user achieved the scene goal? (true/false)
2. Confidence score (0.0-1.0) 
3. Brief reasoning for your decision
4. Next recommended action: "continue", "progress", "hint", or "force_progress"
5. If action is "hint", provide a helpful hint message

Respond in JSON format:
{{
    "goal_achieved": boolean,
    "confidence_score": float,
    "reasoning": "string",
    "next_action": "string",
    "hint_message": "string or null"
}}
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": evaluation_prompt}],
            max_tokens=300,
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Update scene progress if goal achieved
        if result["goal_achieved"] and scene_progress:
            scene_progress.goal_achieved = True
            scene_progress.goal_achievement_score = result["confidence_score"] * 100
            
            # Mark conversation that led to progress
            if recent_messages:
                recent_messages[0].led_to_progress = True
        
        # Check if we should force progression
        if current_attempts >= max_attempts and not result["goal_achieved"]:
            result["next_action"] = "force_progress"
            result["hint_message"] = f"You've reached the maximum attempts ({max_attempts}). Let's move to the next scene with a summary."
        
        db.commit()
        
        return GoalValidationResponse(
            goal_achieved=result["goal_achieved"],
            confidence_score=result["confidence_score"],
            reasoning=result["reasoning"],
            next_action=result["next_action"],
            hint_message=result.get("hint_message")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Goal validation failed: {str(e)}"
        )

@router.post("/progress", response_model=SceneProgressResponse)
async def progress_to_next_scene(
    request: SceneProgressRequest,
    db: Session = Depends(get_db)
):
    """Move user to the next scene in the simulation"""
    
    # Get user progress
    user_progress = db.query(UserProgress).filter(
        UserProgress.id == request.user_progress_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    # Get current scene
    current_scene = db.query(ScenarioScene).filter(
        ScenarioScene.id == request.current_scene_id
    ).first()
    
    if not current_scene:
        raise HTTPException(status_code=404, detail="Current scene not found")
    
    # Update scene progress
    scene_progress = db.query(SceneProgress).filter(
        and_(
            SceneProgress.user_progress_id == request.user_progress_id,
            SceneProgress.scene_id == request.current_scene_id
        )
    ).first()
    
    if scene_progress:
        scene_progress.status = "completed"
        scene_progress.goal_achieved = request.goal_achieved
        scene_progress.forced_progression = request.forced_progression
        scene_progress.completed_at = datetime.utcnow()
        
        if request.forced_progression:
            user_progress.forced_progressions += 1
    
    # Update user progress - add completed scene
    completed_scenes = user_progress.scenes_completed or []
    if request.current_scene_id not in completed_scenes:
        completed_scenes.append(request.current_scene_id)
        user_progress.scenes_completed = completed_scenes
    
    # Find next scene
    next_scene = db.query(ScenarioScene).filter(
        and_(
            ScenarioScene.scenario_id == user_progress.scenario_id,
            ScenarioScene.scene_order > current_scene.scene_order
        )
    ).order_by(ScenarioScene.scene_order).first()
    
    if next_scene:
        # Move to next scene
        user_progress.current_scene_id = next_scene.id
        user_progress.last_activity = datetime.utcnow()
        
        # Create scene progress for next scene
        next_scene_progress = SceneProgress(
            user_progress_id=request.user_progress_id,
            scene_id=next_scene.id,
            status="in_progress",
            started_at=datetime.utcnow()
        )
        db.add(next_scene_progress)
        
        # Get all personas for the scenario
        scene_personas = db.query(ScenarioPersona).filter(
            ScenarioPersona.scenario_id == user_progress.scenario_id
        ).all()
        
        personas_data = [
            ScenarioPersonaResponse(
                id=persona.id,
                scenario_id=persona.scenario_id,
                name=persona.name,
                role=persona.role,
                background=persona.background,
                correlation=persona.correlation,
                primary_goals=persona.primary_goals or [],
                personality_traits=persona.personality_traits or {},
                created_at=persona.created_at,
                updated_at=persona.updated_at
            ) for persona in scene_personas
        ]
        
        next_scene_data = ScenarioSceneResponse(
            id=next_scene.id,
            scenario_id=next_scene.scenario_id,
            title=next_scene.title,
            description=next_scene.description,
            user_goal=next_scene.user_goal,
            scene_order=next_scene.scene_order,
            estimated_duration=next_scene.estimated_duration,
            image_url=next_scene.image_url,
            image_prompt=next_scene.image_prompt,
            created_at=next_scene.created_at,
            updated_at=next_scene.updated_at,
            personas=personas_data
        )
        
        db.commit()
        
        return SceneProgressResponse(
            success=True,
            next_scene=next_scene_data,
            simulation_complete=False
        )
    else:
        # Simulation complete
        user_progress.simulation_status = "completed"
        user_progress.completed_at = datetime.utcnow()
        user_progress.completion_percentage = 100.0
        
        # Calculate final score (simple average of scene scores)
        all_scene_progress = db.query(SceneProgress).filter(
            SceneProgress.user_progress_id == request.user_progress_id
        ).all()
        
        if all_scene_progress:
            scores = [sp.goal_achievement_score for sp in all_scene_progress if sp.goal_achievement_score]
            if scores:
                user_progress.final_score = sum(scores) / len(scores)
        
        db.commit()
        
        return SceneProgressResponse(
            success=True,
            simulation_complete=True,
            completion_summary="Congratulations! You have completed the simulation."
        )

@router.get("/progress/{user_progress_id}", response_model=UserProgressResponse)
async def get_user_progress(
    user_progress_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed user progress for a simulation"""
    
    user_progress = db.query(UserProgress).filter(
        UserProgress.id == user_progress_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    return UserProgressResponse(
        id=user_progress.id,
        user_id=user_progress.user_id,
        scenario_id=user_progress.scenario_id,
        current_scene_id=user_progress.current_scene_id,
        simulation_status=user_progress.simulation_status,
        scenes_completed=user_progress.scenes_completed or [],
        total_attempts=user_progress.total_attempts,
        hints_used=user_progress.hints_used,
        forced_progressions=user_progress.forced_progressions,
        completion_percentage=user_progress.completion_percentage,
        total_time_spent=user_progress.total_time_spent,
        session_count=user_progress.session_count,
        final_score=user_progress.final_score,
        started_at=user_progress.started_at,
        completed_at=user_progress.completed_at,
        last_activity=user_progress.last_activity
    ) 

@router.post("/linear-chat", response_model=SimulationChatResponse)
async def linear_simulation_chat(
    request: SimulationChatRequest,
    db: Session = Depends(get_db)
):
    """Handle orchestrated chat interactions in linear simulation"""
    try:
        # Get user progress
        user_progress = db.query(UserProgress).filter(
            UserProgress.user_id == request.user_id,
            UserProgress.scenario_id == request.scenario_id
        ).first()
        
        if not user_progress:
            raise HTTPException(status_code=404, detail="No active simulation found")
        
        if not user_progress.orchestrator_data:
            raise HTTPException(status_code=400, detail="Simulation not properly initialized")
        
        # Initialize orchestrator with stored data
        orchestrator = ChatOrchestrator(user_progress.orchestrator_data)
        
        # Handle "begin" command to start simulation
        if request.message.lower().strip() == "begin":
            if orchestrator.state.simulation_started:
                ai_response = "The simulation has already begun. Type 'help' for available commands."
            else:
                # Start simulation
                orchestrator.state.simulation_started = True
                orchestrator.state.user_ready = True
                user_progress.simulation_status = "in_progress"
                
                # Generate cinematic prologue
                scenario = user_progress.orchestrator_data
                prologue = f"""# {scenario['title']}

{scenario['description']}

**Challenge:** {scenario['challenge']}

You are about to enter a multi-scene simulation where you'll interact with various team members to achieve specific objectives. Each scene has its own goals and participants.

**Available Agents:**
"""
                for persona in scenario['personas']:
                    name = persona['identity']['name']
                    role = persona['identity']['role']
                    bio = persona['identity']['bio']
                    prologue += f"• @{persona['id']}: {name} ({role}) - {bio}\n"
                
                prologue += f"""
**Instructions:** Use @mentions to speak with specific agents (e.g., @{scenario['personas'][0]['id']}). Type 'help' for assistance.

{orchestrator.generate_scene_introduction()}

*The simulation begins now...*
"""
                ai_response = prologue
        
        elif request.message.lower().strip() == "help":
            ai_response = f"""**Help - Simulation Commands**

**@mention syntax:** Use @agent_id to speak with specific agents
**Current Goal:** {orchestrator._get_current_scene_goal()}
**Turns Remaining:** {orchestrator._get_turns_remaining()}

**Available Commands:**
• help - Show this help
• begin - Start the simulation (if not started)

**Current Scene:** Scene {orchestrator.state.current_scene_index + 1} of {len(orchestrator.scenes)}
"""
        
        else:
            # Regular chat interaction
            if not orchestrator.state.simulation_started:
                ai_response = """Welcome to the simulation! 

Please type **"begin"** when you're ready to start, or **"help"** for more information."""
            else:
                # Use OpenAI to generate orchestrated response
                system_prompt = orchestrator.get_system_prompt()
                
                # Make OpenAI API call
                import openai
                import os
                
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.message}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
                # Increment turn counter
                orchestrator.increment_turn()
        
        # Update orchestrator state in database (simplified for now)
        user_progress.last_activity = datetime.utcnow()
        
        # Log conversation
        conversation_log = ConversationLog(
            user_progress_id=user_progress.id,
            scene_id=request.scene_id or user_progress.current_scene_id,
            user_message=request.message,
            ai_response=ai_response,
            timestamp=datetime.utcnow()
        )
        db.add(conversation_log)
        db.commit()
        
        return SimulationChatResponse(
            message=ai_response,
            scene_id=request.scene_id or user_progress.current_scene_id,
            scene_completed=False,  # Let LLM determine this
            next_scene_id=None
        )
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Linear simulation chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}") 