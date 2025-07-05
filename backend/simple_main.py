# Simplified FastAPI Backend using CrewAI
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn
from datetime import datetime

from database import get_db, engine
from simple_models import Base, User, BusinessScenario, SimulationSession, SimulationMessage
from simple_schemas import ScenarioCreate, SimulationCreate, ChatMessage
from crews.business_crew import BusinessCrew

# Create database tables (only if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CrewAI Education Platform",
    description="Simple educational platform using CrewAI for business simulations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CrewAI Education Platform - Simple & Effective"}

# --- SCENARIO MANAGEMENT ---
@app.post("/scenarios/")
async def create_scenario(scenario: ScenarioCreate, db: Session = Depends(get_db)):
    """Create a new business scenario"""
    db_scenario = BusinessScenario(
        title=scenario.title,
        description=scenario.description,
        industry=scenario.industry,
        challenge=scenario.challenge,
        learning_objectives=scenario.learning_objectives,
        created_by=scenario.created_by  # Will be None if not provided
    )
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

@app.get("/scenarios/")
async def get_scenarios(db: Session = Depends(get_db)):
    """Get all scenarios"""
    return db.query(BusinessScenario).all()

@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get a specific scenario"""
    scenario = db.query(BusinessScenario).filter(BusinessScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

# --- SIMULATION MANAGEMENT ---
@app.post("/simulations/")
async def start_simulation(simulation: SimulationCreate, db: Session = Depends(get_db)):
    """Start a new CrewAI simulation"""
    # Get the scenario
    scenario = db.query(BusinessScenario).filter(
        BusinessScenario.id == simulation.scenario_id
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Create simulation session
    db_simulation = SimulationSession(
        scenario_id=simulation.scenario_id,
        user_id=simulation.user_id,  # Will be None if not provided
        status="active"
    )
    
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    
    return {
        "simulation_id": db_simulation.id,
        "scenario": scenario,
        "status": "ready",
        "message": "Simulation started! Send your first message to interact with the crew."
    }

@app.post("/simulations/{simulation_id}/chat/")
async def chat_with_crew(
    simulation_id: int, 
    chat_message: ChatMessage, 
    db: Session = Depends(get_db)
):
    """Chat with the CrewAI business team"""
    # Get simulation
    simulation = db.query(SimulationSession).filter(
        SimulationSession.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    if simulation.status != "active":
        raise HTTPException(status_code=400, detail="Simulation is not active")
    
    # Get scenario context
    scenario = simulation.scenario
    scenario_context = {
        'title': scenario.title,
        'description': scenario.description,
        'industry': scenario.industry,
        'challenge': scenario.challenge
    }
    
    try:
        # Create and run the crew
        business_crew = BusinessCrew(scenario_context)
        crew_response = business_crew.run_simulation(chat_message.message)
        
        # Save the conversation
        db_message = SimulationMessage(
            simulation_id=simulation_id,
            user_message=chat_message.message,
            crew_response=crew_response
        )
        db.add(db_message)
        
        # Update simulation
        simulation.crew_output = crew_response
        db.commit()
        
        return {
            "simulation_id": simulation_id,
            "user_message": chat_message.message,
            "crew_response": crew_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crew execution failed: {str(e)}")

@app.get("/simulations/{simulation_id}/history/")
async def get_simulation_history(simulation_id: int, db: Session = Depends(get_db)):
    """Get conversation history for a simulation"""
    simulation = db.query(SimulationSession).filter(
        SimulationSession.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    messages = db.query(SimulationMessage).filter(
        SimulationMessage.simulation_id == simulation_id
    ).order_by(SimulationMessage.timestamp).all()
    
    return {
        "simulation_id": simulation_id,
        "scenario": simulation.scenario,
        "messages": messages,
        "status": simulation.status
    }

@app.post("/simulations/{simulation_id}/complete/")
async def complete_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Mark a simulation as completed"""
    simulation = db.query(SimulationSession).filter(
        SimulationSession.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulation.status = "completed"
    simulation.completed_at = datetime.now()
    db.commit()
    
    return {"message": "Simulation completed successfully"}

# --- HEALTH CHECK ---
@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "framework": "CrewAI", "approach": "simple"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 