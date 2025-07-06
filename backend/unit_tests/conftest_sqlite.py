import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os

# Import the app and database components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_db
from models import Base, User, Scenario, Agent, Task, Tool, Simulation

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
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
    """Create test database tables for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

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