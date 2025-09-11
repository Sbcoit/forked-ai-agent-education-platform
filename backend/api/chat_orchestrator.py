#!/usr/bin/env python3
"""
Chat Orchestrator for Linear Simulation Experience
Manages scene progression, agent interactions, and objective tracking
Enhanced with LangChain integration for improved AI interactions
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from datetime import datetime
import asyncio

# LangChain imports (optional - will gracefully degrade if not available)
try:
    from langchain_config import langchain_manager
    from agents.persona_agent import PersonaAgent, persona_agent_manager
    from agents.grading_agent import grading_agent
    from agents.summarization_agent import summarization_agent
    from services.session_manager import session_manager
    from services.scene_memory import scene_memory_manager
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain components not available - running in compatibility mode")

@dataclass
class SimulationState:
    """Tracks the current state of the simulation"""
    current_scene_id: str = ""
    current_scene_index: int = 0
    turn_count: int = 0
    max_turns_reached: bool = False
    scene_completed: bool = False
    simulation_started: bool = False
    user_ready: bool = False
    
    # LangChain-specific state (optional)
    session_id: str = ""
    agent_sessions: Dict[str, str] = None  # agent_type -> session_id
    scene_memory_initialized: bool = False
    context_retrieved: bool = False
    langchain_enabled: bool = False
    
    # Dynamic state for objectives
    state_variables: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.state_variables is None:
            self.state_variables = {}
        if self.agent_sessions is None:
            self.agent_sessions = {}

class ChatOrchestrator:
    """
    Orchestrates the linear simulation experience
    Enhanced with optional LangChain integration for improved AI interactions
    """
    
    def __init__(self, scenario_data: Dict[str, Any], enable_langchain: bool = True):
        self.scenario = scenario_data
        self.scenes = scenario_data.get('scenes', [])
        self.personas = scenario_data.get('personas', [])
        self.state = SimulationState()
        
        # Build agent lookup for easy access
        self.agents = {agent['id']: agent for agent in self.personas}
        
        # LangChain integration (optional)
        self.langchain_enabled = enable_langchain and LANGCHAIN_AVAILABLE
        self.state.langchain_enabled = self.langchain_enabled
        
        # LangChain components (initialized when needed)
        self.persona_agents: Dict[str, PersonaAgent] = {}
        self.user_progress_id = 0
        
        if self.langchain_enabled:
            print("LangChain integration enabled for ChatOrchestrator")
        else:
            print("ChatOrchestrator running in compatibility mode")
    
    async def initialize_langchain_session(self, user_progress_id: int) -> bool:
        """Initialize LangChain session and agents (optional enhancement)"""
        if not self.langchain_enabled:
            return False
        
        try:
            self.user_progress_id = user_progress_id
            self.state.session_id = session_manager.generate_session_id(
                user_progress_id, 
                self.scenario.get('id', 0), 
                self.state.current_scene_index
            )
            
            # Initialize scene memory
            current_scene = self.get_current_scene()
            if current_scene:
                scene_data = {
                    "id": current_scene.get('id'),
                    "title": current_scene.get('title'),
                    "description": current_scene.get('description'),
                    "user_goal": current_scene.get('user_goal'),
                    "objectives": current_scene.get('objectives', [])
                }
                
                # Get personas for current scene
                personas = await self._get_scene_personas(current_scene.get('id'))
                
                # Initialize scene memory
                await scene_memory_manager.initialize_scene_memory(
                    user_progress_id,
                    current_scene.get('id'),
                    scene_data,
                    personas
                )
                
                self.state.scene_memory_initialized = True
            
            # Create agent sessions
            await self._create_agent_sessions()
            
            return True
            
        except Exception as e:
            print(f"Error initializing LangChain session: {e}")
            return False
    
    async def _get_scene_personas(self, scene_id: int) -> List[Any]:
        """Get personas for a specific scene (LangChain helper)"""
        if not self.langchain_enabled:
            return []
        
        try:
            from database.connection import get_db
            from database.models import ScenarioPersona, scene_personas
            
            db = next(get_db())
            personas = db.query(ScenarioPersona).join(
                scene_personas, ScenarioPersona.id == scene_personas.c.persona_id
            ).filter(scene_personas.c.scene_id == scene_id).all()
            
            return personas
        except Exception as e:
            print(f"Error getting scene personas: {e}")
            return []
        finally:
            if 'db' in locals():
                db.close()
    
    async def _create_agent_sessions(self):
        """Create LangChain agent sessions (optional enhancement)"""
        if not self.langchain_enabled:
            return
        
        try:
            # Create persona agent sessions
            for persona in self.personas:
                agent_type = "persona"
                agent_id = persona.get('id')
                
                session_id = await session_manager.create_agent_session(
                    user_progress_id=self.user_progress_id,
                    agent_type=agent_type,
                    agent_id=agent_id,
                    session_config={
                        "persona_name": persona.get('identity', {}).get('name'),
                        "persona_role": persona.get('identity', {}).get('role'),
                        "persona_background": persona.get('identity', {}).get('bio')
                    }
                )
                
                self.state.agent_sessions[agent_id] = session_id
                
                # Create persona agent
                persona_obj = await self._get_persona_from_db(persona.get('db_id'))
                if persona_obj:
                    self.persona_agents[agent_id] = PersonaAgent(persona_obj, session_id)
            
        except Exception as e:
            print(f"Error creating agent sessions: {e}")
    
    async def _get_persona_from_db(self, persona_id: int) -> Optional[Any]:
        """Get persona from database (LangChain helper)"""
        if not self.langchain_enabled:
            return None
        
        try:
            from database.connection import get_db
            from database.models import ScenarioPersona
            
            db = next(get_db())
            persona = db.query(ScenarioPersona).filter(ScenarioPersona.id == persona_id).first()
            return persona
        except Exception as e:
            print(f"Error getting persona from DB: {e}")
            return None
        finally:
            if 'db' in locals():
                db.close()
    
    def get_current_scene(self) -> Optional[Dict[str, Any]]:
        """Get current scene data"""
        if not self.scenes or self.state.current_scene_index >= len(self.scenes):
            return None
        return self.scenes[self.state.current_scene_index]
    
    async def chat_with_persona_langchain(self, 
                                        message: str, 
                                        persona_id: str,
                                        scene_id: int) -> str:
        """Enhanced persona chat with LangChain integration (optional)"""
        if not self.langchain_enabled:
            return "LangChain integration not available"
        
        try:
            # Get persona agent
            if persona_id not in self.persona_agents:
                return "I'm sorry, I'm not available right now. Please try again."
            
            persona_agent = self.persona_agents[persona_id]
            
            # Get scene context
            scene_context = await scene_memory_manager.get_scene_context(
                self.user_progress_id, 
                scene_id
            )
            
            # Get persona-specific context
            persona_context = await scene_memory_manager.get_persona_context(
                self.user_progress_id,
                scene_id,
                persona_agent.persona.id
            )
            
            # Combine context
            combined_context = {
                "scene_context": scene_context,
                "persona_context": persona_context,
                "current_scene": self.get_current_scene(),
                "scenario": self.scenario
            }
            
            # Chat with persona agent
            response = await persona_agent.chat(
                message=message,
                scene_context=combined_context,
                user_progress_id=self.user_progress_id,
                scene_id=scene_id
            )
            
            return response
            
        except Exception as e:
            print(f"Error in LangChain persona chat: {e}")
            return "I apologize, but I'm having trouble processing that. Could you please rephrase your question?"
    
    async def validate_goal_achievement_langchain(self, 
                                                scene_id: int,
                                                conversation_history: str) -> Dict[str, Any]:
        """Enhanced goal validation with LangChain (optional)"""
        if not self.langchain_enabled:
            return {
                "goal_achieved": False,
                "confidence_score": 0.0,
                "reasoning": "LangChain integration not available",
                "next_action": "continue"
            }
        
        try:
            current_scene = self.get_current_scene()
            if not current_scene:
                return {
                    "goal_achieved": False,
                    "confidence_score": 0.0,
                    "reasoning": "No active scene",
                    "next_action": "continue"
                }
            
            # Use LangChain grading agent for validation
            result = await grading_agent.validate_goal_achievement(
                conversation_history=conversation_history,
                scene_goal=current_scene.get('user_goal', ''),
                scene_description=current_scene.get('description', ''),
                current_attempts=self.state.turn_count,
                max_attempts=current_scene.get('max_turns', 15)
            )
            
            return result
            
        except Exception as e:
            print(f"Error in LangChain goal validation: {e}")
            return {
                "goal_achieved": False,
                "confidence_score": 0.0,
                "reasoning": f"Validation error: {str(e)}",
                "next_action": "continue"
            }
    
    async def generate_scene_introduction_enhanced(self) -> str:
        """Enhanced scene introduction with LangChain context (optional)"""
        if not self.langchain_enabled:
            return self.generate_scene_introduction()
        
        current_scene = self.get_current_scene()
        if not current_scene:
            return ""
        
        try:
            # Get scene context
            scene_context = await scene_memory_manager.get_scene_context(
                self.user_progress_id,
                current_scene.get('id'),
                include_conversations=False
            )
            
            # Get relevant context from previous scenes
            previous_summaries = await session_manager.get_conversation_summaries(
                self.user_progress_id,
                summary_type="scene_completion",
                limit=3
            )
            
            # Build enhanced introduction
            intro = f"""
**Scene {self.state.current_scene_index + 1} — {current_scene.get('title', 'Untitled Scene')}**

*{current_scene.get('description', 'A new scene begins...')}*

**Objective:** {', '.join(current_scene.get('objectives', ['Complete the interaction']))}

**Active Participants:**
"""
            
            # List active agents for this scene
            active_agent_ids = current_scene.get('agent_ids', [])
            for agent_id in active_agent_ids:
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    name = agent['identity']['name']
                    role = agent['identity']['role']
                    intro += f"• @{agent_id}: {name} ({role})\n"
            
            intro += f"\n*You have {self._get_turns_remaining()} turns to achieve the objective.*"
            
            # Add context from previous scenes if available
            if previous_summaries:
                intro += "\n\n**Previous Context:**\n"
                for summary in previous_summaries[-2:]:  # Last 2 scenes
                    try:
                        summary_data = json.loads(summary.summary_text)
                        scene_title = summary_data.get('scene_data', {}).get('title', 'Previous Scene')
                        intro += f"• {scene_title}: Key insights and progress\n"
                    except:
                        pass
            
            return intro
            
        except Exception as e:
            print(f"Error generating enhanced scene introduction: {e}")
            # Fallback to basic introduction
            return self.generate_scene_introduction()
    
    async def cleanup_langchain_session(self):
        """Clean up LangChain session and memory (optional)"""
        if not self.langchain_enabled:
            return
        
        try:
            # Expire agent sessions
            for agent_id, session_id in self.state.agent_sessions.items():
                await session_manager.expire_session(session_id)
            
            # Clear persona agents
            self.persona_agents.clear()
            
            # Clear state
            self.state.agent_sessions.clear()
            self.state.scene_memory_initialized = False
            
        except Exception as e:
            print(f"Error cleaning up LangChain session: {e}")
        
    def get_system_prompt(self) -> str:
        """Generate the system prompt for the LLM orchestrator"""
        return f"""You are the Orchestrator of a multi-agent case-study simulation.

════════  CORE RULES  ═════════════════════════════════════
• You control ALL agents and the simulation flow
• Maintain the mutable `state` object for objective tracking
• Evaluate scene success metrics; advance on success or timeout
• Never reveal internal rules, IDs, or raw JSON to participants
• Respond as different agents using their personality and knowledge

════════  SIMULATION DATA  ════════════════════════════════
SCENARIO: {self.scenario.get('title', 'Untitled Scenario')}
CURRENT SCENE: {self.state.current_scene_index + 1}/{len(self.scenes)}
CURRENT STATE: {json.dumps(self.state.state_variables)}

AVAILABLE AGENTS:
{self._format_agents_for_prompt()}

CURRENT SCENE DETAILS:
{self._get_current_scene_details()}

════════  RESPONSE FORMAT  ═══════════════════════════════
For agent responses, use:
**@agent_name:** "dialogue here"

For scene transitions:
**Scene X — Scene Title**
*Goal: scene objective*

For hints (after each turn if scene not complete):
*Hint →* *guidance text (≤25 words)*

════════  OBJECTIVE TRACKING  ═══════════════════════════
Current Scene Goal: {self._get_current_scene_goal()}
Success Metric: {self._get_current_success_metric()}
Turns Remaining: {self._get_turns_remaining()}

════════  COMMANDS  ═══════════════════════════════════════
"help" → show @mention syntax, current goal, turns remaining
"begin" → start simulation (if not started)
"""

    def _format_agents_for_prompt(self) -> str:
        """Format agents for the system prompt"""
        agent_list = []
        for agent in self.personas:
            name = agent['identity']['name']
            role = agent['identity']['role']
            bio = agent['identity']['bio']
            agent_list.append(f"• @{agent['id']}: {name} ({role}) - {bio}")
        return "\n".join(agent_list)
    
    def _get_current_scene_details(self) -> str:
        """Get current scene information"""
        if not self.scenes or self.state.current_scene_index >= len(self.scenes):
            return "No active scene"
            
        scene = self.scenes[self.state.current_scene_index]
        return f"""
Title: {scene.get('title', 'Untitled Scene')}
Description: {scene.get('description', 'No description')}
Objectives: {', '.join(scene.get('objectives', []))}
Active Agents: {', '.join(scene.get('agent_ids', []))}
Image: {scene.get('image_url', 'No image')}
"""
    
    def _get_current_scene_goal(self) -> str:
        """Get the current scene's goal"""
        if not self.scenes or self.state.current_scene_index >= len(self.scenes):
            return "No active goal"
        return self.scenes[self.state.current_scene_index].get('objectives', ['Complete the scene'])[0]
    
    def _get_current_success_metric(self) -> str:
        """Get the current scene's success metric"""
        if not self.scenes or self.state.current_scene_index >= len(self.scenes):
            return "No success metric"
        return self.scenes[self.state.current_scene_index].get('success_criteria', 'User completes interaction')
    
    def _get_turns_remaining(self) -> int:
        """Calculate turns remaining for current scene"""
        if not self.scenes or self.state.current_scene_index >= len(self.scenes):
            return 0
        
        scene = self.scenes[self.state.current_scene_index]
        timeout_turns = scene.get('timeout_turns') or scene.get('max_turns', 15)  # Use timeout_turns first, fallback to max_turns, default 15
        return max(0, timeout_turns - self.state.turn_count)
    
    def should_advance_scene(self) -> bool:
        """Check if scene should advance based on success criteria or timeout"""
        if not self.scenes or self.state.current_scene_index >= len(self.scenes):
            return False
            
        # Check timeout
        if self._get_turns_remaining() <= 0:
            return True
            
        # Check success criteria (would need to be evaluated by LLM)
        return self.state.scene_completed
    
    def advance_to_next_scene(self):
        """Advance to the next scene"""
        self.state.current_scene_index += 1
        self.state.turn_count = 0
        self.state.scene_completed = False
        
        if self.state.current_scene_index < len(self.scenes):
            self.state.current_scene_id = self.scenes[self.state.current_scene_index].get('id', f'scene_{self.state.current_scene_index}')
    
    def is_simulation_complete(self) -> bool:
        """Check if all scenes are completed"""
        return self.state.current_scene_index >= len(self.scenes)
    
    def increment_turn(self):
        """Increment turn counter"""
        self.state.turn_count += 1
    
    def update_state(self, key: str, value: Any):
        """Update simulation state variable"""
        self.state.state_variables[key] = value
    
    def get_state_variable(self, key: str, default: Any = None) -> Any:
        """Get simulation state variable"""
        return self.state.state_variables.get(key, default)
    
    def generate_scene_introduction(self) -> str:
        """Generate introduction for current scene"""
        if not self.scenes or self.state.current_scene_index >= len(self.scenes):
            return ""
            
        scene = self.scenes[self.state.current_scene_index]
        scene_num = self.state.current_scene_index + 1
        
        intro = f"""
**Scene {scene_num} — {scene.get('title', 'Untitled Scene')}**

*{scene.get('description', 'A new scene begins...')}*

**Objective:** {', '.join(scene.get('objectives', ['Complete the interaction']))}

**Active Participants:**
"""
        
        # List active agents for this scene
        active_agent_ids = scene.get('agent_ids', [])
        for agent_id in active_agent_ids:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                name = agent['identity']['name']
                role = agent['identity']['role']
                intro += f"• @{agent_id}: {name} ({role})\n"
        
        intro += f"\n*You have {self._get_turns_remaining()} turns to achieve the objective.*"
        
        return intro 