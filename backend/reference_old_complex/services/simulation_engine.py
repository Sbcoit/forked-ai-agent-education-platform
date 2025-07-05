import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.ai_service import AIService

class SimulationEngine:
    def __init__(self):
        self.ai_service = AIService()
        self.active_sessions = {}  # In-memory storage (no Redis needed for development)
        print("🎮 Simulation Engine initialized (Development Mode - No Redis)")
    
    async def initialize_session(self, simulation_id: int, scenario_id: int) -> Dict[str, Any]:
        """Initialize a new simulation session with agents and context"""
        
        simulation_state = {
            "simulation_id": simulation_id,
            "scenario_id": scenario_id,
            "current_stage": "initialization",
            "business_context": {
                "budget": 500000,
                "timeline_weeks": 12,
                "market_conditions": "competitive",
                "team_morale": 80,
                "customer_satisfaction": 70
            },
            "decisions_history": [],
            "conversation_history": [],
            "simulation_metrics": {
                "decisions_made": 0,
                "business_impact_score": 0,
                "collaboration_score": 0,
                "risk_level": "medium"
            },
            "started_at": datetime.now().isoformat()
        }
        
        self.active_sessions[simulation_id] = simulation_state
        print(f"✅ Simulation {simulation_id} initialized")
        return simulation_state
    
    async def process_user_input(
        self, 
        simulation_id: int, 
        user_message: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process user input and generate agent responses"""
        
        simulation_state = self.active_sessions.get(simulation_id)
        if not simulation_state:
            raise ValueError(f"Simulation {simulation_id} not found")
        
        print(f"📝 Processing user input for simulation {simulation_id}")
        
        # Get agents for this simulation
        agents = await self._get_simulation_agents(simulation_state["scenario_id"])
        
        # Generate responses from all agents
        agent_responses = await self.ai_service.generate_multi_agent_response(
            agents=agents,
            user_message=user_message,
            simulation_context=simulation_state["business_context"]
        )
        
        # Update simulation state
        self._update_simulation_state(simulation_state, user_message, agent_responses)
        
        # Analyze business impact
        business_impact = self._analyze_business_impact(user_message, agent_responses)
        
        print(f"🤖 Generated {len(agent_responses)} agent responses")
        
        return {
            "agent_responses": agent_responses,
            "simulation_state": simulation_state,
            "business_impact": business_impact,
            "suggested_next_steps": self._generate_next_steps(simulation_state, agent_responses)
        }
    
    def _update_simulation_state(
        self,
        state: Dict[str, Any],
        user_message: str,
        agent_responses: List[Dict[str, Any]]
    ):
        """Update simulation state based on user input and agent responses"""
        
        # Add to conversation history
        state["conversation_history"].append({
            "type": "user",
            "message": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        for response in agent_responses:
            state["conversation_history"].append({
                "type": "agent",
                "agent_name": response["agent_name"],
                "message": response["agent_response"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Update metrics
        state["simulation_metrics"]["decisions_made"] += 1
        
        # Calculate collaboration score
        avg_confidence = sum(r["confidence_score"] for r in agent_responses) / len(agent_responses)
        state["simulation_metrics"]["collaboration_score"] = int(avg_confidence)
        
        print(f"📊 Updated simulation metrics: {state['simulation_metrics']['decisions_made']} decisions made")
    
    def _analyze_business_impact(
        self,
        user_message: str,
        agent_responses: List[Dict[str, Any]]
    ) -> str:
        """Analyze the business impact of the user's decision"""
        
        positive_responses = [r for r in agent_responses if r["response_type"] in ["approval", "suggestion"]]
        warning_responses = [r for r in agent_responses if r["response_type"] == "warning"]
        
        if len(positive_responses) > len(agent_responses) * 0.7:
            return "✅ Strong business decision with team alignment."
        elif len(warning_responses) > len(agent_responses) * 0.5:
            return "⚠️ High-risk decision with significant concerns."
        else:
            return "📊 Mixed feedback from your team."
    
    def _generate_next_steps(
        self,
        simulation_state: Dict[str, Any],
        agent_responses: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate suggested next steps based on current state"""
        
        return [
            "Review team recommendations carefully",
            "Consider the financial implications",
            "Address any operational concerns",
            "Monitor market response"
        ]
    
    async def _get_simulation_agents(self, scenario_id: int) -> List[Dict[str, Any]]:
        """Get agents for a specific scenario"""
        return [
            {
                "name": "Alex",
                "role": "Marketing",
                "expertise": "Digital marketing, brand strategy",
                "personality": "Professional marketing specialist",
                "responsibilities": "Marketing strategy, customer acquisition"
            },
            {
                "name": "Morgan", 
                "role": "Finance",
                "expertise": "Financial planning, budget management",
                "personality": "Analytical financial expert",
                "responsibilities": "Budget management, financial projections"
            },
            {
                "name": "Taylor",
                "role": "Product",
                "expertise": "Product development, innovation",
                "personality": "Creative product specialist", 
                "responsibilities": "Product development, user experience"
            },
            {
                "name": "Jordan",
                "role": "Operations",
                "expertise": "Operations management, supply chain",
                "personality": "Efficient operations manager",
                "responsibilities": "Operations optimization, process improvement"
            }
        ]
    
    async def get_agent_responses(self, simulation_id: int) -> List[Dict[str, Any]]:
        """Get all agent responses for a simulation"""
        state = self.active_sessions.get(simulation_id)
        if not state:
            return []
        
        return state.get("conversation_history", []) 