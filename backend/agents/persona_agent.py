"""
Persona Agent for AI Agent Education Platform
Handles persona-specific interactions with context awareness and memory
"""

from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult
import json
from datetime import datetime

from langchain_config import langchain_manager, settings
from database.models import ScenarioPersona, ConversationLog
from database.connection import get_db

class PersonaCallbackHandler(BaseCallbackHandler):
    """Callback handler for persona interactions"""
    
    def __init__(self, persona_id: int, user_progress_id: int, scene_id: int):
        self.persona_id = persona_id
        self.user_progress_id = user_progress_id
        self.scene_id = scene_id
        self.start_time = None
        self.tokens_used = 0
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts"""
        self.start_time = datetime.utcnow()
        
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLM ends"""
        if self.start_time:
            processing_time = (datetime.utcnow() - self.start_time).total_seconds()
            # Log the interaction
            self._log_conversation(response.generations[0][0].text, processing_time)
    
    def _log_conversation(self, response_text: str, processing_time: float):
        """Log conversation to database"""
        try:
            db = next(get_db())
            conversation_log = ConversationLog(
                user_progress_id=self.user_progress_id,
                scene_id=self.scene_id,
                message_type="ai_persona",
                sender_name="Persona",
                persona_id=self.persona_id,
                message_content=response_text,
                message_order=0,  # Will be set by the calling function
                ai_model_version=settings.openai_model,
                processing_time=processing_time,
                timestamp=datetime.utcnow()
            )
            db.add(conversation_log)
            db.commit()
        except Exception as e:
            print(f"Error logging conversation: {e}")

class PersonaAgent:
    """LangChain-based persona agent with context awareness and memory"""
    
    def __init__(self, persona: ScenarioPersona, session_id: str):
        self.persona = persona
        self.session_id = session_id
        self.memory = langchain_manager.create_conversation_memory(
            session_id, 
            memory_type="buffer_window"
        )
        self.llm = langchain_manager.llm
        self.vectorstore = langchain_manager.vectorstore
        
        # Create persona-specific tools
        self.tools = self._create_persona_tools()
        
        # Create agent prompt
        self.prompt = self._create_persona_prompt()
        
        # Create agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def _create_persona_tools(self) -> List[BaseTool]:
        """Create tools specific to this persona"""
        from langchain.tools import tool
        
        @tool
        def get_scene_context(scene_description: str) -> str:
            """Get relevant context about the current scene"""
            # This would retrieve scene-specific context from the vector store
            return f"Scene context: {scene_description}"
        
        @tool
        def get_conversation_history() -> str:
            """Get recent conversation history"""
            # This would retrieve recent conversation from memory
            return "Recent conversation history available"
        
        @tool
        def get_persona_knowledge(query: str) -> str:
            """Get persona-specific knowledge and background"""
            return f"Persona knowledge for {self.persona.name}: {self.persona.background}"
        
        return [get_scene_context, get_conversation_history, get_persona_knowledge]
    
    def _create_persona_prompt(self) -> ChatPromptTemplate:
        """Create persona-specific prompt template"""
        return ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt for the persona"""
        personality_traits = self.persona.personality_traits or {}
        primary_goals = self.persona.primary_goals or []
        
        return f"""You are {self.persona.name}, a {self.persona.role} in this business simulation.

PERSONA BACKGROUND:
{self.persona.background}

CORRELATION TO CASE:
{self.persona.correlation}

PERSONALITY TRAITS:
{json.dumps(personality_traits, indent=2)}

PRIMARY GOALS:
{chr(10).join(f"• {goal}" for goal in primary_goals)}

INSTRUCTIONS:
- Stay in character as {self.persona.name} at all times
- Respond based on your role, background, and personality traits
- Help guide the user toward scene objectives through realistic business interaction
- Don't directly give away answers, but provide realistic business insights
- Keep responses concise and professional
- Use your tools to access relevant context and knowledge
- If the user seems stuck, provide subtle hints through natural conversation

Remember: You are {self.persona.name}, not an AI assistant. Respond as this character would in a real business situation."""
    
    async def chat(self, 
                   message: str, 
                   scene_context: Dict[str, Any],
                   user_progress_id: int,
                   scene_id: int) -> str:
        """Process a chat message with the persona"""
        
        # Create callback handler for logging
        callback_handler = PersonaCallbackHandler(
            persona_id=self.persona.id,
            user_progress_id=user_progress_id,
            scene_id=scene_id
        )
        
        # Prepare input with scene context
        input_data = {
            "input": message,
            "scene_context": json.dumps(scene_context),
            "persona_name": self.persona.name,
            "persona_role": self.persona.role
        }
        
        try:
            # Execute the agent
            response = await self.agent_executor.ainvoke(
                input_data,
                callbacks=[callback_handler]
            )
            
            return response.get("output", "I'm not sure how to respond to that.")
            
        except Exception as e:
            print(f"Error in persona agent: {e}")
            return f"I apologize, but I'm having trouble processing that. Could you please rephrase your question?"
    
    def get_memory_summary(self) -> str:
        """Get a summary of the conversation memory"""
        if hasattr(self.memory, 'chat_memory'):
            messages = self.memory.chat_memory.messages
            if messages:
                return f"Recent conversation with {len(messages)} messages"
        return "No recent conversation"
    
    def clear_memory(self):
        """Clear the conversation memory"""
        if hasattr(self.memory, 'clear'):
            self.memory.clear()
    
    def update_persona_context(self, new_context: Dict[str, Any]):
        """Update persona context with new information"""
        # This could be used to update the persona's knowledge base
        # or modify their behavior based on new information
        pass

class PersonaAgentManager:
    """Manager for multiple persona agents"""
    
    def __init__(self):
        self.agents: Dict[str, PersonaAgent] = {}
    
    def get_or_create_agent(self, 
                           persona: ScenarioPersona, 
                           session_id: str) -> PersonaAgent:
        """Get existing agent or create new one"""
        agent_key = f"{persona.id}_{session_id}"
        
        if agent_key not in self.agents:
            self.agents[agent_key] = PersonaAgent(persona, session_id)
        
        return self.agents[agent_key]
    
    def clear_session_agents(self, session_id: str):
        """Clear all agents for a specific session"""
        keys_to_remove = [key for key in self.agents.keys() if key.endswith(f"_{session_id}")]
        for key in keys_to_remove:
            del self.agents[key]
    
    def get_agent_count(self) -> int:
        """Get total number of active agents"""
        return len(self.agents)

# Global persona agent manager
persona_agent_manager = PersonaAgentManager()
