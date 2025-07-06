# Enhanced Pydantic Schemas for CrewAI Agent Builder Platform
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- SCENARIO SCHEMAS ---
class ScenarioCreate(BaseModel):
    title: str
    description: str
    industry: str
    challenge: str
    learning_objectives: List[str]
    source_type: str = "manual"
    pdf_content: Optional[str] = None
    is_public: bool = False
    is_template: bool = False
    allow_remixes: bool = True

class ScenarioResponse(BaseModel):
    id: int
    title: str
    description: str
    industry: str
    challenge: str
    learning_objectives: List[str]
    source_type: str
    pdf_content: Optional[str]
    is_public: bool
    is_template: bool
    allow_remixes: bool
    usage_count: int
    clone_count: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ScenarioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    challenge: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    is_public: Optional[bool] = None
    allow_remixes: Optional[bool] = None

# --- AGENT SCHEMAS ---
class AgentCreate(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = []
    verbose: bool = True
    allow_delegation: bool = False
    reasoning: bool = True
    category: Optional[str] = None
    tags: List[str] = []
    is_public: bool = False
    is_template: bool = False
    allow_remixes: bool = True
    version: str = "1.0.0"
    version_notes: Optional[str] = None

class AgentResponse(BaseModel):
    id: int
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str]
    verbose: bool
    allow_delegation: bool
    reasoning: bool
    category: Optional[str]
    tags: Optional[List[str]]
    is_public: bool
    is_template: bool
    allow_remixes: bool
    original_agent_id: Optional[int]
    usage_count: int
    clone_count: int
    average_rating: float
    rating_count: int
    version: str
    version_notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    tools: Optional[List[str]] = None
    verbose: Optional[bool] = None
    allow_delegation: Optional[bool] = None
    reasoning: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    allow_remixes: Optional[bool] = None
    version: Optional[str] = None
    version_notes: Optional[str] = None

# --- TOOL SCHEMAS ---
class ToolCreate(BaseModel):
    name: str
    description: str
    tool_type: str
    configuration: Dict[str, Any] = {}
    required_credentials: Optional[List[str]] = None
    usage_instructions: Optional[str] = None
    code: Optional[str] = None
    requirements: List[str] = []
    category: Optional[str] = None
    tags: List[str] = []
    is_public: bool = False
    is_verified: bool = False
    allow_remixes: bool = True
    version: str = "1.0.0"
    version_notes: Optional[str] = None

class ToolResponse(BaseModel):
    id: int
    name: str
    description: str
    tool_type: str
    configuration: Dict[str, Any]
    required_credentials: Optional[List[str]]
    usage_instructions: Optional[str]
    code: Optional[str]
    requirements: Optional[List[str]]
    category: Optional[str]
    tags: Optional[List[str]]
    is_public: bool
    is_verified: bool
    allow_remixes: bool
    original_tool_id: Optional[int]
    usage_count: int
    clone_count: int
    average_rating: float
    rating_count: int
    version: str
    version_notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tool_type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    required_credentials: Optional[List[str]] = None
    usage_instructions: Optional[str] = None
    code: Optional[str] = None
    requirements: Optional[List[str]] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    allow_remixes: Optional[bool] = None
    version: Optional[str] = None
    version_notes: Optional[str] = None

# --- TASK SCHEMAS ---
class TaskCreate(BaseModel):
    title: str
    description: str
    expected_output: str
    tools: List[str] = []
    context: Optional[Dict[str, Any]] = None
    agent_id: Optional[int] = None
    category: Optional[str] = None
    tags: List[str] = []
    is_public: bool = False
    is_template: bool = False
    allow_remixes: bool = True

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    expected_output: str
    tools: Optional[List[str]]
    context: Optional[Dict[str, Any]]
    agent_id: Optional[int]
    category: Optional[str]
    tags: Optional[List[str]]
    is_public: bool
    is_template: bool
    allow_remixes: bool
    usage_count: int
    clone_count: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    expected_output: Optional[str] = None
    tools: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    agent_id: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    allow_remixes: Optional[bool] = None

# --- SIMULATION SCHEMAS ---
class SimulationCreate(BaseModel):
    scenario_id: int
    crew_configuration: Optional[Dict[str, Any]] = None
    process_type: str = "sequential"

class SimulationResponse(BaseModel):
    id: int
    scenario_id: int
    user_id: Optional[int]
    crew_configuration: Optional[Dict[str, Any]]
    process_type: str
    status: str
    crew_output: Optional[str]
    execution_log: Optional[Dict[str, Any]]
    error_details: Optional[Dict[str, Any]]
    missing_agents: Optional[List[int]]
    missing_tasks: Optional[List[int]]
    fallback_used: bool
    is_public: bool
    allow_sharing: bool
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SimulationFallbackCreate(BaseModel):
    scenario_id: int
    fallback_agents: List[int] = []
    fallback_tasks: List[int] = []
    fallback_strategy: str = "substitute"  # substitute, skip, fail

class SimulationFallbackResponse(BaseModel):
    id: int
    scenario_id: int
    fallback_agents: List[int]
    fallback_tasks: List[int]
    fallback_strategy: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- REVIEW SCHEMAS ---
class AgentReviewCreate(BaseModel):
    agent_id: int
    rating: int  # 1-5 stars
    review_text: Optional[str] = None
    pros: List[str] = []
    cons: List[str] = []
    use_case: Optional[str] = None

class AgentReviewResponse(BaseModel):
    id: int
    agent_id: int
    reviewer_id: int
    rating: int
    review_text: Optional[str]
    pros: Optional[List[str]]
    cons: Optional[List[str]]
    use_case: Optional[str]
    helpful_votes: int
    total_votes: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ToolReviewCreate(BaseModel):
    tool_id: int
    rating: int  # 1-5 stars
    review_text: Optional[str] = None
    pros: List[str] = []
    cons: List[str] = []
    use_case: Optional[str] = None

class ToolReviewResponse(BaseModel):
    id: int
    tool_id: int
    reviewer_id: int
    rating: int
    review_text: Optional[str]
    pros: Optional[List[str]]
    cons: Optional[List[str]]
    use_case: Optional[str]
    helpful_votes: int
    total_votes: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    email: str
    full_name: str
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "user"
    profile_public: bool = True
    allow_contact: bool = True

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    username: str
    bio: Optional[str]
    avatar_url: Optional[str]
    role: str
    public_agents_count: int
    public_tools_count: int
    total_downloads: int
    reputation_score: float
    profile_public: bool
    allow_contact: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_public: Optional[bool] = None
    allow_contact: Optional[bool] = None

# --- USER AUTHENTICATION SCHEMAS ---
class UserRegister(BaseModel):
    email: str
    full_name: str
    username: str
    password: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_public: bool = True
    allow_contact: bool = True

class UserLogin(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordReset(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# --- COLLECTION SCHEMAS ---
class CollectionCreate(BaseModel):
    name: str
    description: str
    agents: List[int] = []
    tools: List[int] = []
    scenarios: List[int] = []
    is_public: bool = False
    tags: List[str] = []

class CollectionResponse(BaseModel):
    id: int
    name: str
    description: str
    agents: Optional[List[int]]
    tools: Optional[List[int]]
    scenarios: Optional[List[int]]
    is_public: bool
    tags: Optional[List[str]]
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- LEGACY SCHEMAS (for backwards compatibility) ---
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    simulation_id: int
    user_message: str
    crew_response: str
    timestamp: str 