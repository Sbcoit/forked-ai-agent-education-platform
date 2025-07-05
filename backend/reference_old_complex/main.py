from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
from typing import List, Optional
import json

from database import get_db, engine
from models import Base, User, BusinessScenario, AIAgent, SimulationSession
from schemas import (
    ScenarioCreate, ScenarioResponse, 
    AgentCreate, AgentResponse,
    SimulationCreate, SimulationResponse
)
from services.ai_service import AIService
from services.pdf_processor import PDFProcessor
from services.simulation_engine import SimulationEngine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Agent Education Platform",
    description="Create and manage AI agents for educational business simulations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIService()
pdf_processor = PDFProcessor()
simulation_engine = SimulationEngine()
security = HTTPBearer()

@app.get("/")
async def root():
    return {"message": "AI Agent Education Platform API"}

# Scenario Management Routes
@app.post("/scenarios/", response_model=ScenarioResponse)
async def create_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(get_db)
):
    """Create a new business scenario"""
    db_scenario = BusinessScenario(
        title=scenario.title,
        description=scenario.description,
        industry=scenario.industry,
        challenge=scenario.challenge,
        learning_objectives=scenario.learning_objectives,
        source_type=scenario.source_type or "custom",
        source_data=scenario.source_data,
        created_by=scenario.created_by
    )
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

@app.get("/scenarios/", response_model=List[ScenarioResponse])
async def get_scenarios(db: Session = Depends(get_db)):
    """Get all business scenarios"""
    scenarios = db.query(BusinessScenario).all()
    return scenarios

@app.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get a specific business scenario"""
    scenario = db.query(BusinessScenario).filter(BusinessScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

# PDF Processing Route
@app.post("/scenarios/upload-pdf/")
async def upload_pdf_scenario(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and analyze PDF case study"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Process PDF
    pdf_content = await file.read()
    analysis = await pdf_processor.analyze_pdf(pdf_content)
    
    # Create scenario from PDF analysis
    db_scenario = BusinessScenario(
        title=analysis["title"],
        description=analysis["description"],
        industry=analysis["industry"],
        challenge=analysis["challenge"],
        learning_objectives=analysis["learning_objectives"],
        source_type="pdf",
        source_data=json.dumps(analysis)
    )
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    
    return {
        "scenario": db_scenario,
        "suggested_agents": analysis["suggested_agents"],
        "analysis": analysis
    }

# Agent Management Routes
@app.post("/agents/", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db)
):
    """Create a new AI agent"""
    db_agent = AIAgent(
        name=agent.name,
        role=agent.role,
        expertise=agent.expertise,
        personality=agent.personality,
        authority_level=agent.authority_level,
        responsibilities=agent.responsibilities,
        scenario_id=agent.scenario_id
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@app.get("/scenarios/{scenario_id}/agents/", response_model=List[AgentResponse])
async def get_scenario_agents(scenario_id: int, db: Session = Depends(get_db)):
    """Get all agents for a specific scenario"""
    agents = db.query(AIAgent).filter(AIAgent.scenario_id == scenario_id).all()
    return agents

@app.post("/agents/generate/")
async def generate_agent(
    scenario_id: int,
    agent_role: str,
    requirements: str,
    db: Session = Depends(get_db)
):
    """AI-powered agent generation"""
    scenario = db.query(BusinessScenario).filter(BusinessScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    agent_config = await ai_service.generate_agent(
        scenario_context=scenario.description,
        role=agent_role,
        requirements=requirements
    )
    
    return agent_config

# Simulation Routes
@app.post("/simulations/", response_model=SimulationResponse)
async def start_simulation(
    simulation: SimulationCreate,
    db: Session = Depends(get_db)
):
    """Start a new simulation session"""
    db_simulation = SimulationSession(
        scenario_id=simulation.scenario_id,
        user_id=simulation.user_id,
        status="active"
    )
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    
    # Initialize simulation engine
    await simulation_engine.initialize_session(db_simulation.id, simulation.scenario_id)
    
    return db_simulation

@app.post("/simulations/{simulation_id}/interact/")
async def interact_with_agents(
    simulation_id: int,
    message: str,
    db: Session = Depends(get_db)
):
    """Send message to agents in simulation"""
    simulation = db.query(SimulationSession).filter(SimulationSession.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    response = await simulation_engine.process_user_input(simulation_id, message)
    return response

@app.get("/simulations/{simulation_id}/agents/")
async def get_simulation_agents(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """Get all agent responses in simulation"""
    responses = await simulation_engine.get_agent_responses(simulation_id)
    return responses

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 