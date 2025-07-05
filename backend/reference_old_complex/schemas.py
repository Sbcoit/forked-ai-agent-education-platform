from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AuthorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SimulationStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "teacher"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Business Scenario Schemas
class ScenarioBase(BaseModel):
    title: str
    description: str
    industry: str
    challenge: str
    learning_objectives: List[str]

class ScenarioCreate(ScenarioBase):
    source_type: Optional[str] = "custom"
    source_data: Optional[Dict[str, Any]] = None
    created_by: Optional[int] = None

class ScenarioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    challenge: Optional[str] = None
    learning_objectives: Optional[List[str]] = None

class ScenarioResponse(ScenarioBase):
    id: int
    source_type: str
    source_data: Optional[Dict[str, Any]] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# AI Agent Schemas
class AgentBase(BaseModel):
    name: str
    role: str
    expertise: str
    personality: str
    authority_level: AuthorityLevel
    responsibilities: str
    conversation_style: str = "professional"

class AgentCreate(AgentBase):
    scenario_id: int
    decision_criteria: Optional[Dict[str, Any]] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    expertise: Optional[str] = None
    personality: Optional[str] = None
    authority_level: Optional[AuthorityLevel] = None
    responsibilities: Optional[str] = None
    conversation_style: Optional[str] = None
    decision_criteria: Optional[Dict[str, Any]] = None

class AgentResponse(AgentBase):
    id: int
    scenario_id: int
    decision_criteria: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Simulation Schemas
class SimulationCreate(BaseModel):
    scenario_id: int
    user_id: int

class SimulationUpdate(BaseModel):
    status: Optional[SimulationStatus] = None
    current_stage: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None
    decisions_made: Optional[Dict[str, Any]] = None

class SimulationResponse(BaseModel):
    id: int
    scenario_id: int
    user_id: int
    status: SimulationStatus
    current_stage: str
    session_data: Optional[Dict[str, Any]] = None
    decisions_made: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Agent Response Schemas
class AgentResponseCreate(BaseModel):
    simulation_id: int
    agent_id: int
    user_message: str
    agent_response: str
    response_type: str
    confidence_score: int

class AgentResponseResponse(BaseModel):
    id: int
    simulation_id: int
    agent_id: int
    user_message: str
    agent_response: str
    response_type: str
    confidence_score: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# PDF Analysis Schemas
class PDFAnalysisResult(BaseModel):
    title: str
    description: str
    industry: str
    challenge: str
    learning_objectives: List[str]
    suggested_agents: List[Dict[str, str]]
    key_stakeholders: List[str]
    timeline: Optional[str] = None
    budget_info: Optional[str] = None

# Agent Generation Schemas
class AgentGenerationRequest(BaseModel):
    scenario_context: str
    role: str
    requirements: str
    authority_level: Optional[AuthorityLevel] = AuthorityLevel.MEDIUM
    conversation_style: Optional[str] = "professional"

class GeneratedAgentResponse(BaseModel):
    name: str
    role: str
    expertise: str
    personality: str
    responsibilities: str
    decision_criteria: Dict[str, Any]
    suggested_responses: List[str]

# Simulation Interaction Schemas
class UserInput(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class AgentInteractionResponse(BaseModel):
    agent_responses: List[Dict[str, Any]]
    simulation_state: Dict[str, Any]
    suggested_actions: List[str]
    business_impact: Optional[str] = None

# Template Schemas
class TemplateBase(BaseModel):
    name: str
    category: str
    template_data: Dict[str, Any]
    suggested_agents: List[Dict[str, Any]]

class TemplateCreate(TemplateBase):
    is_public: bool = True
    created_by: Optional[int] = None

class TemplateResponse(TemplateBase):
    id: int
    is_public: bool
    created_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 