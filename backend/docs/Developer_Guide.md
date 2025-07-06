# Developer Guide - CrewAI Agent Builder Platform

## Table of Contents
1. [Quick Start](#quick-start)
2. [Development Setup](#development-setup)
3. [API Development](#api-development)
4. [Testing Strategy](#testing-strategy)
5. [Code Standards](#code-standards)
6. [Deployment Guide](#deployment-guide)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon cloud database)
- Git

### 5-Minute Setup

```bash
# Clone repository
git clone <repository-url>
cd AOM_2025

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd ../frontend
npm install
npm start
```

### Verify Installation
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Health Check: http://localhost:8000/health

---

## Development Setup

### Backend Environment Setup

#### 1. Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Unix/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Environment Variables
Create `.env` file in backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
SERPER_API_KEY=your-serper-key

# Email Service
EMAIL_SERVICE_API_KEY=your-email-key
EMAIL_FROM=noreply@yourplatform.com

# Environment
ENVIRONMENT=development
DEBUG=true
```

#### 3. Database Setup
```bash
# Using Neon PostgreSQL (recommended)
# 1. Create account at https://neon.tech
# 2. Create database
# 3. Copy connection string to .env

# Or local PostgreSQL
createdb crewai_platform
psql crewai_platform < schema.sql
```

#### 4. Run Backend Server
```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Environment Setup

#### 1. Install Dependencies
```bash
cd frontend
npm install
```

#### 2. Environment Variables
Create `.env` file in frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=2.0.0
```

#### 3. Run Frontend Server
```bash
# Development mode
npm start

# Production build
npm run build
npm run serve
```

---

## API Development

### Code Structure

```
backend/
├── main.py                 # FastAPI app and routes
├── database/
│   ├── connection.py       # Database connection
│   ├── models.py          # SQLAlchemy models
│   └── schemas.py         # Pydantic schemas
├── utilities/
│   └── auth.py            # Authentication utilities
└── crews/
    ├── business_crew.py   # CrewAI configurations
    └── config/
        ├── agents.yaml    # Agent definitions
        └── tasks.yaml     # Task definitions
```

### Adding New API Endpoints

#### 1. Define Pydantic Schema
```python
# database/schemas.py
from pydantic import BaseModel
from typing import Optional, List

class NewResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    is_public: bool = True

class NewResourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    tags: List[str]
    is_public: bool
    created_at: datetime
    
    class Config:
        orm_mode = True
```

#### 2. Define Database Model
```python
# database/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func

class NewResource(Base):
    __tablename__ = "new_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    tags = Column(JSON)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 3. Add API Endpoints
```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database import models, schemas
from utilities.auth import get_current_user

@app.post("/new-resources/", response_model=schemas.NewResourceResponse)
async def create_new_resource(
    resource: schemas.NewResourceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_resource = models.NewResource(
        name=resource.name,
        description=resource.description,
        tags=resource.tags,
        is_public=resource.is_public,
        created_by=current_user.id
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@app.get("/new-resources/", response_model=List[schemas.NewResourceResponse])
async def get_new_resources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    resources = db.query(models.NewResource).filter(
        models.NewResource.is_public == True
    ).offset(skip).limit(limit).all()
    return resources

@app.get("/new-resources/{resource_id}", response_model=schemas.NewResourceResponse)
async def get_new_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    resource = db.query(models.NewResource).filter(
        models.NewResource.id == resource_id,
        models.NewResource.is_public == True
    ).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
```

### Database Migrations

#### 1. Create Migration
```bash
# Install Alembic
pip install alembic

# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new resource table"

# Apply migration
alembic upgrade head
```

#### 2. Manual Migration Script
```python
# database/migrations/add_new_resource.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'new_resources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_new_resources_id'), 'new_resources', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_new_resources_id'), table_name='new_resources')
    op.drop_table('new_resources')
```

---

## Testing Strategy

### Test Structure

```
unit_tests/
├── conftest.py              # Test configuration & fixtures
├── auth/
│   └── test_authentication.py  # Authentication tests
├── api/
│   ├── test_scenarios.py       # Scenario API tests
│   ├── test_agents.py          # Agent API tests
│   └── test_simulations.py     # Simulation API tests
└── core/
    ├── test_health.py          # Health check tests
    └── test_root.py            # Root endpoint tests
```

### Running Tests

#### 1. Run All Tests
```bash
# From backend directory
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest unit_tests/api/test_agents.py

# Specific test function
pytest unit_tests/api/test_agents.py::test_create_agent
```

#### 2. Test Configuration
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base, get_db
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

#### 3. Example Test Case
```python
# unit_tests/api/test_agents.py
def test_create_agent(client, authenticated_user):
    agent_data = {
        "name": "Test Agent",
        "role": "Test Role",
        "goal": "Test goal",
        "backstory": "Test backstory",
        "tools": ["web_search"],
        "category": "business",
        "tags": ["test"],
        "is_public": True
    }
    
    response = client.post(
        "/agents/",
        json=agent_data,
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["role"] == "Test Role"
    assert data["is_public"] is True

def test_get_agents(client):
    response = client.get("/agents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

### Integration Testing

#### 1. Database Integration Tests
```python
# unit_tests/integration/test_database.py
def test_full_user_agent_workflow(db):
    # Create user
    user = models.User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password"
    )
    db.add(user)
    db.commit()
    
    # Create agent
    agent = models.Agent(
        name="Test Agent",
        role="Test Role",
        goal="Test goal",
        backstory="Test backstory",
        created_by=user.id
    )
    db.add(agent)
    db.commit()
    
    # Verify relationships
    assert agent.created_by == user.id
    assert len(user.agents) == 1
    assert user.agents[0].name == "Test Agent"
```

#### 2. API Integration Tests
```python
# unit_tests/integration/test_api_workflows.py
def test_complete_simulation_workflow(client, authenticated_user):
    # Create scenario
    scenario_data = {
        "title": "Test Scenario",
        "description": "Test description",
        "industry": "Technology",
        "challenge": "Test challenge",
        "is_public": True
    }
    scenario_response = client.post(
        "/scenarios/",
        json=scenario_data,
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    scenario_id = scenario_response.json()["id"]
    
    # Start simulation
    simulation_data = {
        "scenario_id": scenario_id,
        "process_type": "sequential"
    }
    simulation_response = client.post(
        "/simulations/",
        json=simulation_data,
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    simulation_id = simulation_response.json()["simulation_id"]
    
    # Send message
    message_data = {"message": "What should we do first?"}
    chat_response = client.post(
        f"/simulations/{simulation_id}/chat/",
        json=message_data,
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    
    assert chat_response.status_code == 200
    assert "crew_response" in chat_response.json()
```

---

## Code Standards

### Python Code Style

#### 1. Code Formatting
```bash
# Install formatting tools
pip install black isort flake8

# Format code
black .
isort .

# Lint code
flake8 .
```

#### 2. Type Hints
```python
# Good: Use type hints
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

def create_agent(
    agent_data: Dict[str, Any],
    user_id: int,
    db: Session
) -> Optional[Agent]:
    """Create a new agent with proper typing."""
    pass

# Good: Pydantic models with types
class AgentCreate(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = []
    is_public: bool = True
```

#### 3. Documentation
```python
def process_simulation_message(
    simulation_id: int,
    message: str,
    user_id: int,
    db: Session
) -> SimulationResponse:
    """
    Process a user message in a simulation and return crew response.
    
    Args:
        simulation_id: ID of the active simulation
        message: User's input message
        user_id: ID of the user sending the message
        db: Database session
        
    Returns:
        SimulationResponse with crew response and metadata
        
    Raises:
        HTTPException: If simulation not found or not active
        CrewAIException: If crew processing fails
    """
    pass
```

### Frontend Code Style

#### 1. TypeScript Standards
```typescript
// Good: Proper interfaces
interface Agent {
  id: number;
  name: string;
  role: string;
  goal: string;
  backstory: string;
  tools: string[];
  isPublic: boolean;
  createdAt: string;
  updatedAt: string;
}

// Good: Component with proper types
interface AgentBuilderProps {
  agent?: Agent;
  onSave: (agent: Agent) => void;
  onCancel: () => void;
}

const AgentBuilder: React.FC<AgentBuilderProps> = ({
  agent,
  onSave,
  onCancel
}) => {
  // Component implementation
};
```

#### 2. Code Organization
```typescript
// services/api.ts
class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async createAgent(agentData: AgentCreate): Promise<Agent> {
    const response = await fetch(`${this.baseUrl}/agents/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` })
      },
      body: JSON.stringify(agentData)
    });

    if (!response.ok) {
      throw new Error('Failed to create agent');
    }

    return response.json();
  }
}
```

---

## Deployment Guide

### Development Deployment

#### 1. Local Docker Setup
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/crewai_platform
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=crewai_platform
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 2. Run with Docker
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Deployment

#### 1. Environment Setup
```bash
# Create production environment file
cp .env.example .env.production

# Edit production values
vim .env.production
```

#### 2. Database Migration
```bash
# Apply migrations
alembic upgrade head

# Create initial data
python scripts/create_initial_data.py
```

#### 3. Production Server
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database connection
psql -h localhost -U username -d database_name

# Test connection in Python
python -c "
from database.connection import engine
try:
    engine.connect()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

#### 2. Authentication Issues
```bash
# Check JWT token
python -c "
from utilities.auth import decode_token
token = 'your_jwt_token_here'
try:
    payload = decode_token(token)
    print(f'Token valid: {payload}')
except Exception as e:
    print(f'Token invalid: {e}')
"
```

#### 3. CrewAI Issues
```bash
# Check AI API keys
python -c "
import os
print(f'OpenAI key: {os.getenv('OPENAI_API_KEY', 'Not set')}')
print(f'Anthropic key: {os.getenv('ANTHROPIC_API_KEY', 'Not set')}')
"

# Test CrewAI import
python -c "
try:
    from crewai import Agent, Task, Crew
    print('CrewAI import successful')
except Exception as e:
    print(f'CrewAI import failed: {e}')
"
```

#### 4. Frontend Issues
```bash
# Check API connection
curl -X GET http://localhost:8000/health

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Debug Mode

#### 1. Enable Debug Logging
```python
# main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response: {response.status_code}")
    return response
```

#### 2. Database Query Debugging
```python
# Enable SQLAlchemy logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Performance Monitoring

#### 1. API Response Times
```python
# Add timing middleware
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

#### 2. Database Connection Monitoring
```python
# Monitor database connections
from database.connection import engine

def get_db_stats():
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "invalid": pool.invalid(),
        "overflow": pool.overflow()
    }
```

---

## Contributing

### Development Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/crewai-platform.git
   cd crewai-platform
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

3. **Make Changes**
   - Follow code standards
   - Add tests for new features
   - Update documentation

4. **Test Changes**
   ```bash
   pytest
   black .
   flake8 .
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add new feature: description"
   git push origin feature/new-feature
   ```

6. **Create Pull Request**
   - Describe changes
   - Reference related issues
   - Ensure CI passes

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Database migrations included if needed

---

## Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Documentation](https://reactjs.org/docs/)

### Tools
- [Postman Collection](./postman_collection.json)
- [VS Code Extensions](./vscode_extensions.json)
- [Docker Compose Files](./docker/)

### Community
- [Discord Server](https://discord.gg/crewai)
- [GitHub Issues](https://github.com/yourusername/crewai-platform/issues)
- [Contributing Guidelines](./CONTRIBUTING.md) 