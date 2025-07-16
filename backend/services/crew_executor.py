# CrewAI Execution Service - Dynamic Crew Creation and Execution
from typing import List, Dict, Any, Optional, Callable
# from crewai import Agent, Crew, Task, Process
# from crewai.llm import LLM
from database.models import Agent as DBAgent, Task as DBTask, Simulation, SimulationMessage
from database.connection import get_db
from sqlalchemy.orm import Session
import json
import asyncio
from datetime import datetime

class CrewExecutor:
    """Service for executing CrewAI crews with user-created agents and tasks"""
    
    def __init__(self, db: Session):
        self.db = db
        # Simplified available tools - no external tools for now
        self.available_tools = {
            # "web_search": None,  # Will add when we have working tools
            # "calculator": None,  # Will add when we have working tools
            # "email": None,       # Will add when we have working tools
            # Add more tools as needed when available
        }
        # self.llm = LLM(model="gpt-4o-mini")  # Default LLM
    
    def create_crewai_agent(self, db_agent: DBAgent) -> Any: # Changed return type hint to Any
        """Convert database agent to CrewAI Agent"""
        # Get tools for this agent - simplified for now
        agent_tools = []
        # Skip tool assignment for now since we don't have working external tools
        # for tool_name in db_agent.tools or []:
        #     if tool_name in self.available_tools and self.available_tools[tool_name]:
        #         agent_tools.append(self.available_tools[tool_name])
        
        return {
            "name": db_agent.name,
            "role": db_agent.role,
            "goal": db_agent.goal,
            "backstory": db_agent.backstory,
            "tools": agent_tools,  # Empty for now
            "verbose": db_agent.verbose,
            "allow_delegation": db_agent.allow_delegation,
            # "llm": self.llm # Removed as per comment
        }
    
    def create_crewai_task(self, db_task: DBTask, crewai_agents: List[Any], human_input_callback: Optional[Callable] = None) -> Any: # Changed return type hint to Any
        """Convert database task to CrewAI Task"""
        # Find the assigned agent
        assigned_agent = None
        if db_task.agent_id:
            # Find the CrewAI agent that corresponds to this database agent
            for i, agent in enumerate(crewai_agents):
                # We need to match by some identifier - using name for now
                if agent["name"] == db_task.agent.name:
                    assigned_agent = agent
                    break
        
        # Get tools for this specific task - simplified for now
        task_tools = []
        # Skip tool assignment for now since we don't have working external tools
        # for tool_name in db_task.tools or []:
        #     if tool_name in self.available_tools and self.available_tools[tool_name]:
        #         task_tools.append(self.available_tools[tool_name])
        
        # Determine if human input is needed
        human_input = db_task.context and db_task.context.get('human_input', False)
        
        return {
            "description": db_task.description,
            "expected_output": db_task.expected_output,
            "agent": assigned_agent,
            "tools": task_tools,  # Empty for now
            "human_input": human_input,
            "callback": self._create_task_callback(db_task.id) if human_input_callback else None
        }
    
    def _create_task_callback(self, task_id: int) -> Callable:
        """Create a callback function for task completion"""
        def callback(task_output):
            print(f"Task {task_id} completed: {task_output}")
            # Here you could save intermediate results to database
            return task_output
        return callback
    
    async def execute_crew_simulation(
        self, 
        simulation_id: int, 
        user_message: str,
        human_input_handler: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute a CrewAI simulation with real agents and tasks"""
        
        # Get simulation and scenario
        simulation = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not simulation:
            raise ValueError(f"Simulation {simulation_id} not found")
        
        scenario = simulation.scenario
        
        # Get agents and tasks for this scenario
        scenario_agents = scenario.agents
        scenario_tasks = scenario.tasks
        
        if not scenario_agents:
            raise ValueError(f"No agents found for scenario {scenario.id}")
        
        if not scenario_tasks:
            raise ValueError(f"No tasks found for scenario {scenario.id}")
        
        try:
            # Create CrewAI agents
            crewai_agents = [self.create_crewai_agent(agent) for agent in scenario_agents]
            
            # Create CrewAI tasks
            crewai_tasks = [
                self.create_crewai_task(task, crewai_agents, human_input_handler) 
                for task in scenario_tasks
            ]
            
            # Create crew
            # crew = Crew( # Removed as per comment
            #     agents=crewai_agents,
            #     tasks=crewai_tasks,
            #     process=Process.sequential,  # Could be made configurable
            #     verbose=True
            # )
            
            # Prepare inputs
            inputs = {
                'scenario_title': scenario.title,
                'scenario_description': scenario.description,
                'industry': scenario.industry,
                'challenge': scenario.challenge,
                'user_message': user_message
            }
            
            # Execute crew
            simulation.status = "running"
            self.db.commit()
            
            # Run the crew
            # result = crew.kickoff(inputs=inputs) # Removed as per comment
            result = "Simulation completed successfully (placeholder)" # Placeholder result
            
            # Update simulation
            simulation.status = "completed"
            simulation.crew_output = str(result)
            simulation.completed_at = datetime.now()
            self.db.commit()
            
            # Return detailed results
            return {
                "success": True,
                "simulation_id": simulation_id,
                "crew_output": str(result),
                "individual_outputs": self._extract_individual_outputs(None), # Placeholder for individual outputs
                "agents_used": [agent["name"] for agent in crewai_agents],
                "tasks_completed": [task["description"][:100] + ("..." if len(task["description"]) > 100 else "") for task in crewai_tasks]
            }
            
        except Exception as e:
            # Handle errors
            simulation.status = "failed"
            simulation.error_details = {"error": str(e)}
            self.db.commit()
            
            return {
                "success": False,
                "simulation_id": simulation_id,
                "error": str(e)
            }
    
    def _extract_individual_outputs(self, crew: Any) -> List[Dict[str, Any]]: # Changed parameter type hint to Any
        """Extract individual agent/task outputs from completed crew"""
        outputs = []
        
        # for i, task in enumerate(crew.tasks): # crew is None, so this loop will not execute
        #     if hasattr(task, 'output') and task.output:
        #         outputs.append({
        #             "task_index": i,
        #             "task_description": task.description[:100] + ("..." if len(task.description) > 100 else ""),
        #             "agent_name": task.agent.name if task.agent else "Unknown",
        #             "output": str(task.output.raw) if hasattr(task.output, 'raw') else str(task.output),
        #             "timestamp": datetime.now().isoformat()
        #         })
        
        return outputs
    
    def handle_human_input_request(self, simulation_id: int, task_description: str, agent_output: str) -> str:
        """Handle human input request during crew execution"""
        # Save the human input request to database
        human_input_message = SimulationMessage(
            simulation_id=simulation_id,
            user_message="[HUMAN INPUT REQUESTED]",
            crew_response=f"Agent needs human review:\n\nTask: {task_description}\n\nAgent Output: {agent_output}\n\nPlease provide feedback or approval.",
            message_type="human_input_request"
        )
        self.db.add(human_input_message)
        self.db.commit()
        
        # For now, return a placeholder - in real implementation, this would wait for user input
        return "Human input received: Approved to proceed" 