# Simplified FastAPI Backend using CrewAI
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta

from database.connection import get_db, engine
from database.models import Base, User, Scenario, Simulation, SimulationMessage, Agent, Task
from database.schemas import (
    ScenarioCreate, SimulationCreate, ChatMessage, AgentCreate, AgentResponse, AgentUpdate,
    UserRegister, UserLogin, UserLoginResponse, UserResponse, UserUpdate, PasswordChange,
    TaskCreate, TaskResponse, TaskUpdate
)
from utilities.auth import (
    get_password_hash, authenticate_user, create_access_token, get_current_user, 
    get_current_user_optional, require_admin
)
from services.crew_executor import CrewExecutor

# Create database tables (only if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CrewAI Agent Builder Platform",
    description="Community-driven platform for building, sharing, and running AI agent simulations",
    version="2.0.0"
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
    return {"message": "CrewAI Agent Builder Platform - Build, Share, Simulate", "version": "2.0.0"}

# --- SCENARIO MANAGEMENT ---
@app.post("/scenarios/")
async def create_scenario(
    scenario: ScenarioCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new business scenario (requires authentication)"""
    db_scenario = Scenario(
        title=scenario.title,
        description=scenario.description,
        industry=scenario.industry,
        challenge=scenario.challenge,
        learning_objectives=scenario.learning_objectives,
        source_type=scenario.source_type,
        pdf_content=scenario.pdf_content,
        is_public=scenario.is_public,
        is_template=scenario.is_template,
        allow_remixes=scenario.allow_remixes,
        created_by=current_user.id  # Automatically link to authenticated user
    )
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

@app.get("/scenarios/")
async def get_scenarios(db: Session = Depends(get_db)):
    """Get all scenarios with their agents and tasks"""
    from sqlalchemy.orm import joinedload
    
    scenarios = db.query(Scenario)\
        .options(joinedload(Scenario.agents))\
        .options(joinedload(Scenario.tasks))\
        .all()
    
    return scenarios

@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get a specific scenario with its agents and tasks"""
    from sqlalchemy.orm import joinedload
    
    scenario = db.query(Scenario)\
        .options(joinedload(Scenario.agents))\
        .options(joinedload(Scenario.tasks))\
        .filter(Scenario.id == scenario_id)\
        .first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

# --- SIMULATION MANAGEMENT ---
@app.post("/simulations/")
async def start_simulation(
    simulation: SimulationCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new CrewAI simulation (requires authentication)"""
    # Get the scenario
    scenario = db.query(Scenario).filter(
        Scenario.id == simulation.scenario_id
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Create simulation session
    db_simulation = Simulation(
        scenario_id=simulation.scenario_id,
        user_id=current_user.id,  # Automatically link to authenticated user
        status="created"
    )
    
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    
    return {
        "simulation_id": db_simulation.id,
        "scenario": {
            "id": scenario.id,
            "title": scenario.title,
            "description": scenario.description,
            "industry": scenario.industry,
            "challenge": scenario.challenge
        },
        "status": "ready",
        "message": "Simulation started! Send your first message to interact with the crew."
    }

@app.post("/simulations/{simulation_id}/chat/")
async def chat_with_crew(
    simulation_id: int, 
    chat_message: ChatMessage, 
    db: Session = Depends(get_db)
):
    """Chat with the CrewAI business team using real agents and tasks"""
    # Get simulation
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    if simulation.status not in ["created", "running"]:
        raise HTTPException(status_code=400, detail="Simulation is not active")
    
    try:
        # Initialize CrewExecutor
        crew_executor = CrewExecutor(db)
        
        # Execute the crew simulation
        result = await crew_executor.execute_crew_simulation(
            simulation_id=simulation_id,
            user_message=chat_message.message
        )
        
        if result["success"]:
            # Save the conversation with crew output
            db_message = SimulationMessage(
                simulation_id=simulation_id,
                user_message=chat_message.message,
                crew_response=result["crew_output"]
            )
            db.add(db_message)
            
            # Save individual agent outputs as separate messages
            for output in result["individual_outputs"]:
                agent_message = SimulationMessage(
                    simulation_id=simulation_id,
                    user_message="",
                    crew_response=f"**{output['agent_name']}**: {output['output']}",
                    message_type="agent_output"
                )
                db.add(agent_message)
            
            db.commit()
            
            return {
                "simulation_id": simulation_id,
                "user_message": chat_message.message,
                "crew_response": result["crew_output"],
                "individual_outputs": result["individual_outputs"],
                "agents_used": result["agents_used"],
                "tasks_completed": result["tasks_completed"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Handle execution failure
            error_message = f"Crew execution failed: {result['error']}"
            
            db_message = SimulationMessage(
                simulation_id=simulation_id,
                user_message=chat_message.message,
                crew_response=error_message,
                message_type="error"
            )
            db.add(db_message)
            db.commit()
            
            raise HTTPException(status_code=500, detail=error_message)
        
    except Exception as e:
        # Handle unexpected errors
        error_message = f"Simulation error: {str(e)}"
        
        db_message = SimulationMessage(
            simulation_id=simulation_id,
            user_message=chat_message.message,
            crew_response=error_message,
            message_type="error"
        )
        db.add(db_message)
        db.commit()
        
        raise HTTPException(status_code=500, detail=error_message)

@app.get("/simulations/{simulation_id}/history/")
async def get_simulation_history(simulation_id: int, db: Session = Depends(get_db)):
    """Get conversation history for a simulation"""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    messages = db.query(SimulationMessage).filter(
        SimulationMessage.simulation_id == simulation_id
    ).order_by(SimulationMessage.timestamp).all()
    
    return {
        "simulation_id": simulation_id,
        "scenario": {
            "id": simulation.scenario.id,
            "title": simulation.scenario.title,
            "description": simulation.scenario.description,
            "industry": simulation.scenario.industry,
            "challenge": simulation.scenario.challenge
        },
        "messages": messages,
        "status": simulation.status
    }

@app.post("/simulations/{simulation_id}/complete/")
async def complete_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Mark a simulation as completed"""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulation.status = "completed"
    simulation.completed_at = datetime.now()
    db.commit()
    
    return {"message": "Simulation completed successfully"}

@app.post("/simulations/{simulation_id}/human-input/")
async def provide_human_input(
    simulation_id: int, 
    human_input: ChatMessage,
    db: Session = Depends(get_db)
):
    """Provide human input when CrewAI requests it"""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Save human input response
    db_message = SimulationMessage(
        simulation_id=simulation_id,
        user_message=human_input.message,
        crew_response="[HUMAN INPUT PROVIDED]",
        message_type="human_input_response"
    )
    db.add(db_message)
    db.commit()
    
    return {
        "simulation_id": simulation_id,
        "human_input": human_input.message,
        "message": "Human input received. Crew will continue execution.",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/simulations/{simulation_id}/status/")
async def get_simulation_status(simulation_id: int, db: Session = Depends(get_db)):
    """Get current simulation status including human input requests"""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Check for pending human input requests
    pending_human_input = db.query(SimulationMessage).filter(
        SimulationMessage.simulation_id == simulation_id,
        SimulationMessage.message_type == "human_input_request"
    ).order_by(SimulationMessage.timestamp.desc()).first()
    
    return {
        "simulation_id": simulation_id,
        "status": simulation.status,
        "started_at": simulation.started_at,
        "completed_at": simulation.completed_at,
        "pending_human_input": pending_human_input is not None,
        "human_input_request": {
            "message": pending_human_input.crew_response,
            "timestamp": pending_human_input.timestamp
        } if pending_human_input else None
    }

# --- AGENT MANAGEMENT ---
@app.post("/agents/", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI agent (requires authentication)"""
    db_agent = Agent(
        name=agent.name,
        role=agent.role,
        goal=agent.goal,
        backstory=agent.backstory,
        tools=agent.tools,
        verbose=agent.verbose,
        allow_delegation=agent.allow_delegation,
        reasoning=agent.reasoning,
        category=agent.category,
        tags=agent.tags,
        is_public=agent.is_public,
        is_template=agent.is_template,
        allow_remixes=agent.allow_remixes,
        version=agent.version,
        version_notes=agent.version_notes,
        created_by=current_user.id  # Automatically link to authenticated user
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@app.get("/agents/", response_model=List[AgentResponse])
async def get_agents(db: Session = Depends(get_db)):
    """Get all agents"""
    return db.query(Agent).all()

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get a specific agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    """Update an existing agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update only provided fields
    for field, value in agent_update.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    return agent

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Delete an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    return {"message": "Agent deleted successfully"}

@app.get("/agents/user/{user_id}", response_model=List[AgentResponse])
async def get_user_agents(user_id: int, db: Session = Depends(get_db)):
    """Get all agents created by a specific user"""
    return db.query(Agent).filter(Agent.created_by == user_id).all()

# --- TASK MANAGEMENT ---
@app.post("/tasks/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task (requires authentication)"""
    db_task = Task(
        title=task.title,
        description=task.description,
        expected_output=task.expected_output,
        tools=task.tools,
        context=task.context,
        agent_id=task.agent_id,
        category=task.category,
        tags=task.tags,
        is_public=task.is_public,
        is_template=task.is_template,
        allow_remixes=task.allow_remixes,
        created_by=current_user.id  # Automatically link to authenticated user
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    """Get all tasks"""
    return db.query(Task).all()

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update only provided fields
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

@app.get("/tasks/user/{user_id}", response_model=List[TaskResponse])
async def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    """Get all tasks created by a specific user"""
    return db.query(Task).filter(Task.created_by == user_id).all()

@app.get("/tasks/agent/{agent_id}", response_model=List[TaskResponse])
async def get_agent_tasks(agent_id: int, db: Session = Depends(get_db)):
    """Get all tasks assigned to a specific agent"""
    return db.query(Task).filter(Task.agent_id == agent_id).all()

# --- USER AUTHENTICATION & MANAGEMENT ---
@app.post("/users/register", response_model=UserResponse)
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        username=user.username,
        password_hash=hashed_password,
        bio=user.bio,
        avatar_url=user.avatar_url,
        profile_public=user.profile_public,
        allow_contact=user.allow_contact
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/users/login", response_model=UserLoginResponse)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    # Check if username is being changed and if it's available
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update only provided fields
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@app.post("/users/me/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    from utilities.auth import verify_password
    
    # Verify current password
    if not verify_password(password_change.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_change.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@app.get("/users/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get user profile (public profiles visible to all, private profiles only to owner/admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check privacy settings
    if not user.profile_public:
        if not current_user or (current_user.id != user.id and current_user.role != "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This profile is private"
            )
    
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile (own profile or admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if username is being changed and if it's available
    if user_update.username and user_update.username != user.username:
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update only provided fields
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting self
    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

# --- HEALTH CHECK ---
@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "framework": "CrewAI", "platform": "Agent Builder Community", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 