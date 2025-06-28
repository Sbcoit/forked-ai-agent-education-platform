import openai
import anthropic
from typing import Dict, List, Any, Optional
import json
import asyncio
from database import settings

class AIService:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    async def generate_agent(
        self, 
        scenario_context: str, 
        role: str, 
        requirements: str,
        authority_level: str = "medium",
        conversation_style: str = "professional"
    ) -> Dict[str, Any]:
        """Generate an AI agent configuration based on scenario and requirements"""
        
        prompt = f"""
        You are an expert AI agent designer for educational business simulations. 
        Create a detailed AI agent configuration for the following scenario:

        **Business Scenario:** {scenario_context}
        **Agent Role:** {role}
        **Requirements:** {requirements}
        **Authority Level:** {authority_level}
        **Conversation Style:** {conversation_style}

        Generate a comprehensive agent configuration with:
        1. Agent name (professional, appropriate for role)
        2. Specific expertise areas
        3. Personality description (aligned with conversation style)
        4. Key responsibilities
        5. Decision-making criteria (as JSON object)
        6. 3 example responses this agent might give

        Return as a JSON object with these exact fields:
        - name
        - role
        - expertise
        - personality
        - responsibilities
        - decision_criteria (object)
        - suggested_responses (array)
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AI agent designer. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            agent_config = json.loads(content)
            
            return agent_config
            
        except Exception as e:
            # Fallback configuration
            return {
                "name": f"{role} Agent",
                "role": role,
                "expertise": f"Specialized in {role.lower()} for business scenarios",
                "personality": f"Professional and knowledgeable {role.lower()} specialist",
                "responsibilities": f"Handle all {role.lower()}-related decisions and recommendations",
                "decision_criteria": {
                    "authority_level": authority_level,
                    "primary_concerns": [f"{role.lower()}_optimization", "risk_management"],
                    "decision_factors": ["budget", "timeline", "resources"]
                },
                "suggested_responses": [
                    f"Based on my {role.lower()} analysis, I recommend...",
                    f"From a {role.lower()} perspective, we should consider...",
                    f"The {role.lower()} implications of this decision are..."
                ]
            }
    
    async def generate_agent_response(
        self,
        agent_config: Dict[str, Any],
        user_message: str,
        simulation_context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a response from an AI agent based on user input"""
        
        # Build conversation history
        messages = [
            {
                "role": "system", 
                "content": f"""
                You are {agent_config['name']}, a {agent_config['role']} in a business simulation.
                
                Your expertise: {agent_config['expertise']}
                Your personality: {agent_config['personality']}
                Your responsibilities: {agent_config['responsibilities']}
                
                Decision criteria: {json.dumps(agent_config.get('decision_criteria', {}))}
                
                Current business context: {json.dumps(simulation_context)}
                
                Respond as this character would, staying in role. Be helpful, specific, and provide 
                actionable business advice from your area of expertise. Include:
                1. Your professional opinion
                2. Specific recommendations
                3. Potential risks or concerns
                4. Next steps or requirements
                
                Keep responses concise but comprehensive (100-200 words).
                """
            }
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages for context
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            agent_response = response.choices[0].message.content
            
            # Analyze response sentiment and confidence
            confidence_score = await self._analyze_response_confidence(agent_response)
            response_type = await self._classify_response_type(agent_response)
            
            return {
                "agent_response": agent_response,
                "confidence_score": confidence_score,
                "response_type": response_type,
                "agent_name": agent_config['name'],
                "agent_role": agent_config['role']
            }
            
        except Exception as e:
            # Fallback response
            return {
                "agent_response": f"As your {agent_config['role']}, I need more information to provide a proper recommendation. Could you clarify the specific challenge you're facing?",
                "confidence_score": 60,
                "response_type": "clarification",
                "agent_name": agent_config['name'],
                "agent_role": agent_config['role']
            }
    
    async def generate_multi_agent_response(
        self,
        agents: List[Dict[str, Any]],
        user_message: str,
        simulation_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate responses from multiple agents simultaneously"""
        
        tasks = []
        for agent in agents:
            task = self.generate_agent_response(
                agent_config=agent,
                user_message=user_message,
                simulation_context=simulation_context
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return responses
    
    async def _analyze_response_confidence(self, response: str) -> int:
        """Analyze how confident the agent response sounds (1-100)"""
        confidence_indicators = [
            "recommend", "suggest", "should", "must", "will", "definitely",
            "clearly", "obviously", "certainly", "confident"
        ]
        uncertainty_indicators = [
            "might", "maybe", "possibly", "perhaps", "unclear", "unsure",
            "depends", "consider", "evaluate", "investigate"
        ]
        
        response_lower = response.lower()
        confidence_words = sum(1 for word in confidence_indicators if word in response_lower)
        uncertainty_words = sum(1 for word in uncertainty_indicators if word in response_lower)
        
        base_score = 70
        confidence_boost = min(confidence_words * 5, 25)
        uncertainty_penalty = min(uncertainty_words * 3, 20)
        
        return max(30, min(95, base_score + confidence_boost - uncertainty_penalty))
    
    async def _classify_response_type(self, response: str) -> str:
        """Classify the type of agent response"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ["recommend", "suggest", "propose"]):
            return "suggestion"
        elif any(word in response_lower for word in ["warning", "risk", "concern", "caution"]):
            return "warning"
        elif any(word in response_lower for word in ["approve", "support", "agree", "good"]):
            return "approval"
        elif any(word in response_lower for word in ["analyze", "review", "assess", "evaluate"]):
            return "analysis"
        else:
            return "information"
    
    async def generate_scenario_from_description(self, description: str) -> Dict[str, Any]:
        """Generate a complete business scenario from a brief description"""
        
        prompt = f"""
        Based on the following description, create a comprehensive business scenario for educational purposes:
        
        Description: {description}
        
        Generate a detailed scenario with:
        1. Company/Business name
        2. Industry category
        3. Detailed challenge description
        4. Learning objectives
        5. Key stakeholders
        6. 4 suggested AI agent roles
        7. Timeline and constraints
        
        Return as JSON with these fields:
        - title
        - industry
        - description
        - challenge
        - learning_objectives
        - key_stakeholders
        - suggested_agents
        - timeline
        - constraints
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content designer. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            scenario = json.loads(content)
            return scenario
            
        except Exception as e:
            return {
                "title": "Custom Business Scenario",
                "industry": "General Business",
                "description": description,
                "challenge": "Navigate complex business decisions in a competitive market",
                "learning_objectives": "Understand cross-functional business operations and strategic decision making",
                "key_stakeholders": ["Management", "Customers", "Employees", "Investors"],
                "suggested_agents": [
                    {"role": "Marketing", "focus": "Customer acquisition and brand management"},
                    {"role": "Finance", "focus": "Budget management and financial planning"},
                    {"role": "Operations", "focus": "Process optimization and supply chain"},
                    {"role": "Product", "focus": "Product development and innovation"}
                ],
                "timeline": "12 weeks",
                "constraints": "Limited budget and competitive market pressures"
            } 