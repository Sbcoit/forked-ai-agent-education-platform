from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class AuthorityLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SimulationStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String, default="teacher")  # teacher, student, admin
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    created_scenarios = relationship("BusinessScenario", back_populates="creator")
    simulation_sessions = relationship("SimulationSession", back_populates="user")

class BusinessScenario(Base):
    __tablename__ = "business_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    industry = Column(String)
    challenge = Column(Text)
    learning_objectives = Column(JSON)
    source_type = Column(String, default="manual")  # manual, pdf, template
    source_data = Column(JSON)  # Store PDF analysis or template data
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_scenarios")
    agents = relationship("AIAgent", back_populates="scenario")
    simulation_sessions = relationship("SimulationSession", back_populates="scenario")

class AIAgent(Base):
    __tablename__ = "ai_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)  # Marketing, Finance, Product, Operations, etc.
    expertise = Column(Text)  # Specific areas of expertise
    personality = Column(Text)  # Personality description and tone
    authority_level = Column(Enum(AuthorityLevel))
    responsibilities = Column(Text)  # Key responsibilities
    decision_criteria = Column(JSON)  # Decision-making criteria and constraints
    conversation_style = Column(String, default="professional")  # professional, casual, energetic
    scenario_id = Column(Integer, ForeignKey("business_scenarios.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scenario = relationship("BusinessScenario", back_populates="agents")
    responses = relationship("AgentResponse", back_populates="agent")

class SimulationSession(Base):
    __tablename__ = "simulation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("business_scenarios.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(SimulationStatus), default=SimulationStatus.ACTIVE)
    current_stage = Column(String, default="initial")
    session_data = Column(JSON)  # Store simulation state and context
    decisions_made = Column(JSON)  # Track user decisions
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    scenario = relationship("BusinessScenario", back_populates="simulation_sessions")
    user = relationship("User", back_populates="simulation_sessions")
    agent_responses = relationship("AgentResponse", back_populates="simulation")

class AgentResponse(Base):
    __tablename__ = "agent_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulation_sessions.id"))
    agent_id = Column(Integer, ForeignKey("ai_agents.id"))
    user_message = Column(Text)  # The message/decision from user
    agent_response = Column(Text)  # Agent's response
    response_type = Column(String)  # suggestion, warning, approval, analysis
    confidence_score = Column(Integer)  # How confident the agent is (1-100)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("SimulationSession", back_populates="agent_responses")
    agent = relationship("AIAgent", back_populates="responses")

class ScenarioTemplate(Base):
    __tablename__ = "scenario_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)  # eco-friendly, healthcare, fintech, etc.
    template_data = Column(JSON)  # Pre-configured scenario data
    suggested_agents = Column(JSON)  # Recommended agent configurations
    is_public = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 