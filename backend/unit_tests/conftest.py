import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid
from unittest.mock import Mock, patch

# Mock problematic dependencies before any imports
mock_modules = {
    'crewai': Mock(),
    'crewai.Agent': Mock(),
    'crewai.Crew': Mock(),
    'crewai.Task': Mock(),
    'crewai.Process': Mock(),
    'crewai.llm': Mock(),
    'crewai.llm.LLM': Mock(),
    'chromadb': Mock(),
    'onnxruntime': Mock(),
}

# Apply all mocks to sys.modules before importing
for module_name, mock_module in mock_modules.items():
    sys.modules[module_name] = mock_module

# Import the app and database components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database.connection import get_db
from database.models import Base, User, Scenario, Agent, Task, Tool, Simulation

# Neon PostgreSQL test database configuration
TEST_DATABASE_URL = "postgresql://nAIbleDataBase_owner:npg_3lD0MTKbBAsL@ep-spring-snow-a8hq9mjp-pooler.eastus2.azure.neon.tech/EdTechPlatfrom_TestBase?sslmode=require&channel_binding=require"

# Create test database engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override the get_db dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    """Create and keep test database tables for inspection"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # COMMENTED OUT: Clean up - we want to keep data for inspection
    # Base.metadata.drop_all(bind=engine)
    print(f"🔍 Tables and data preserved in EdTechPlatfrom_TestBase for inspection")

@pytest.fixture(scope="function")
def client(test_db):
    """Create test client"""
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session(test_db):
    """Create database session for direct database operations"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    # Check if user already exists
    existing_user = db_session.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        return existing_user
        
    user = User(
        email="test@example.com",
        full_name="Test User",
        username="testuser",
        bio="Test bio",
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_scenario(db_session, sample_user):
    """Create a sample scenario for testing"""
    scenario = Scenario(
        title="Test Scenario",
        description="A test scenario for unit testing",
        industry="Technology",
        challenge="Test challenge",
        learning_objectives=["Learn testing", "Understand APIs"],
        source_type="manual",
        is_public=True,
        created_by=sample_user.id
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)
    return scenario

@pytest.fixture
def sample_agent(db_session, sample_user):
    """Create a sample agent for testing"""
    agent = Agent(
        name="Test Agent",
        role="Test Role",
        goal="Test goal",
        backstory="Test backstory",
        tools=["TestTool1", "TestTool2"],
        verbose=True,
        allow_delegation=False,
        reasoning=True,
        category="test",
        tags=["test", "unit"],
        is_public=True,
        version="1.0.0",
        created_by=sample_user.id
    )
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)
    return agent

@pytest.fixture
def sample_simulation(db_session, sample_user, sample_scenario):
    """Create a sample simulation for testing"""
    simulation = Simulation(
        scenario_id=sample_scenario.id,
        user_id=sample_user.id,
        status="created",
        crew_configuration={"process": "sequential"},
        process_type="sequential"
    )
    db_session.add(simulation)
    db_session.commit()
    db_session.refresh(simulation)
    return simulation

@pytest.fixture
def valid_scenario_data():
    """Valid scenario data for POST requests"""
    return {
        "title": "New Test Scenario",
        "description": "A new test scenario",
        "industry": "Education",
        "challenge": "Learn new things",
        "learning_objectives": ["Objective 1", "Objective 2"],
        "source_type": "manual",
        "is_public": False,
        "is_template": False,
        "allow_remixes": True,
        "created_by": None
    }

@pytest.fixture
def valid_agent_data():
    """Valid agent data for POST requests"""
    return {
        "name": "New Test Agent",
        "role": "Test Assistant",
        "goal": "Help with testing",
        "backstory": "An AI agent created for testing purposes",
        "tools": ["TestTool"],
        "verbose": True,
        "allow_delegation": False,
        "reasoning": True,
        "category": "test",
        "tags": ["test", "new"],
        "is_public": True,
        "is_template": False,
        "allow_remixes": True,
        "version": "1.0.0",
        "version_notes": "Initial version",
        "created_by": None
    }

@pytest.fixture
def valid_simulation_data(sample_scenario):
    """Valid simulation data for POST requests"""
    return {
        "scenario_id": sample_scenario.id,
        "user_id": None,
        "crew_configuration": {"process": "sequential"},
        "process_type": "sequential"
    }

@pytest.fixture
def valid_chat_message():
    """Valid chat message data"""
    return {
        "message": "Hello, this is a test message"
    }

# --- AUTHENTICATION TEST FIXTURES ---
@pytest.fixture
def sample_user_with_password(db_session):
    """Create a sample user with password for authentication testing"""
    from database.models import User
    from utilities.auth import get_password_hash
    
    # Check if user already exists
    existing_user = db_session.query(User).filter(User.email == "testauth@example.com").first()
    if existing_user:
        return {
            "user": existing_user,
            "email": existing_user.email,
            "password": "testpassword123"
        }
    
    user = User(
        email="testauth@example.com",
        full_name="Test Auth User",
        username="testauthuser",
        password_hash=get_password_hash("testpassword123"),
        bio="Test auth bio",
        role="user",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Return both user and password for testing
    return {
        "user": user,
        "email": user.email,
        "password": "testpassword123"
    }

@pytest.fixture
def authenticated_user(client, sample_user_with_password):
    """Create an authenticated user with access token"""
    from utilities.auth import create_access_token
    
    # Create access token
    token = create_access_token(data={"sub": str(sample_user_with_password["user"].id)})
    
    return {
        "user": sample_user_with_password["user"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }

@pytest.fixture
def admin_user(db_session, client):
    """Create an admin user with access token"""
    from database.models import User
    from utilities.auth import get_password_hash, create_access_token
    
    # Check if admin already exists
    existing_admin = db_session.query(User).filter(User.email == "admin@example.com").first()
    if existing_admin:
        token = create_access_token(data={"sub": str(existing_admin.id)})
        return {
            "user": existing_admin,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"}
        }
    
    admin = User(
        email="admin@example.com",
        full_name="Admin User",
        username="adminuser",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        is_verified=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    # Create access token
    token = create_access_token(data={"sub": str(admin.id)})
    
    return {
        "user": admin,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    } 