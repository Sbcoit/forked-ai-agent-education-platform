# Simple Pydantic Schemas for CrewAI Education Platform
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ScenarioCreate(BaseModel):
    title: str
    description: str
    industry: str
    challenge: str
    learning_objectives: List[str]
    created_by: Optional[int] = None

class ScenarioResponse(BaseModel):
    id: int
    title: str
    description: str
    industry: str
    challenge: str
    learning_objectives: List[str]
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SimulationCreate(BaseModel):
    scenario_id: int
    user_id: Optional[int] = None

class SimulationResponse(BaseModel):
    id: int
    scenario_id: int
    user_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    simulation_id: int
    user_message: str
    crew_response: str
    timestamp: str 