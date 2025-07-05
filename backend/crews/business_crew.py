# Business Crew for Educational Simulations
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai import LLM
import yaml
import os

@CrewBase
class BusinessCrew():
    """Business simulation crew for educational purposes"""
    
    def __init__(self, scenario_context: dict):
        self.scenario_context = scenario_context
        
        # Load configuration files
        self.agents_config = self._load_config('crews/config/agents.yaml')
        self.tasks_config = self._load_config('crews/config/tasks.yaml')
        
        super().__init__()
    
    def _load_config(self, config_path: str) -> dict:
        """Load YAML configuration file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            return {}
        except Exception as e:
            print(f"⚠️  Error loading config {config_path}: {e}")
            return {}
    
    @agent
    def marketing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['marketing_agent'],
            verbose=True,
            tools=[SerperDevTool()],
            llm=LLM(model="claude-3-haiku-20240307")
        )
    
    @agent
    def finance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['finance_agent'],
            verbose=True,
            llm=LLM(model="claude-3-haiku-20240307")
        )
    
    @agent
    def product_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['product_agent'],
            verbose=True,
            llm=LLM(model="claude-3-haiku-20240307")
        )
    
    @agent
    def operations_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['operations_agent'],
            verbose=True,
            llm=LLM(model="claude-3-haiku-20240307")
        )
    
    @task
    def market_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_analysis_task'],
            agent=self.marketing_agent()
        )
    
    @task
    def financial_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['financial_planning_task'],
            agent=self.finance_agent()
        )
    
    @task
    def product_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['product_strategy_task'],
            agent=self.product_agent()
        )
    
    @task
    def operations_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['operations_planning_task'],
            agent=self.operations_agent()
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the business simulation crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,    # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True
        )
    
    def run_simulation(self, user_input: str) -> str:
        """Run the business simulation with user input"""
        inputs = {
            'scenario_title': self.scenario_context.get('title', 'Business Challenge'),
            'scenario_description': self.scenario_context.get('description', ''),
            'industry': self.scenario_context.get('industry', 'General'),
            'challenge': self.scenario_context.get('challenge', ''),
            'user_input': user_input
        }
        
        result = self.crew().kickoff(inputs=inputs)
        return str(result) 