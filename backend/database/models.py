# Enhanced Database Models for CrewAI Agent Builder Platform
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Junction tables for many-to-many relationships
scenario_agents = Table(
    'scenario_agents',
    Base.metadata,
    Column('scenario_id', Integer, ForeignKey('scenarios.id'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

scenario_tasks = Table(
    'scenario_tasks', 
    Base.metadata,
    Column('scenario_id', Integer, ForeignKey('scenarios.id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

# Junction tables for simulation execution tracking
simulation_agents = Table(
    'simulation_agents',
    Base.metadata,
    Column('simulation_id', Integer, ForeignKey('simulations.id'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('agent_snapshot', JSON, nullable=True),  # Store agent config at time of simulation
    Column('execution_order', Integer, default=0),  # Order in which agents execute
    Column('status', String, default='pending'),     # pending, running, completed, failed
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

simulation_tasks = Table(
    'simulation_tasks',
    Base.metadata,
    Column('simulation_id', Integer, ForeignKey('simulations.id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id'), nullable=True),  # Which agent is assigned
    Column('task_snapshot', JSON, nullable=True),   # Store task config at time of simulation
    Column('execution_order', Integer, default=0),  # Order in which tasks execute
    Column('status', String, default='pending'),    # pending, running, completed, failed
    Column('task_output', Text, nullable=True),     # Individual task result
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

# User favorites for agents and tools
user_favorite_agents = Table(
    'user_favorite_agents',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

user_favorite_tools = Table(
    'user_favorite_tools',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('tool_id', Integer, ForeignKey('tools.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    username = Column(String, unique=True, index=True)  # For public profile
    password_hash = Column(String)  # Hashed password for authentication
    bio = Column(Text, nullable=True)  # User bio for public profile
    avatar_url = Column(String, nullable=True)  # Profile picture
    role = Column(String, default="user")  # admin, teacher, student, user
    
    # Community stats
    public_agents_count = Column(Integer, default=0)
    public_tools_count = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)  # How many times their content was used
    reputation_score = Column(Float, default=0.0)  # Community reputation
    
    # Settings
    profile_public = Column(Boolean, default=True)  # Whether profile is public
    allow_contact = Column(Boolean, default=True)  # Whether others can contact them
    
    # Account status
    is_active = Column(Boolean, default=True)  # Account active status
    is_verified = Column(Boolean, default=False)  # Email verification status
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenarios = relationship("Scenario", back_populates="creator")
    agents = relationship("Agent", back_populates="creator")
    tasks = relationship("Task", back_populates="creator")
    tools = relationship("Tool", back_populates="creator")
    simulations = relationship("Simulation", back_populates="user")
    
    # Reviews given by this user
    agent_reviews = relationship("AgentReview", back_populates="reviewer")
    tool_reviews = relationship("ToolReview", back_populates="reviewer")
    
    # Favorites
    favorite_agents = relationship("Agent", secondary=user_favorite_agents, back_populates="favorited_by")
    favorite_tools = relationship("Tool", secondary=user_favorite_tools, back_populates="favorited_by")

class Scenario(Base):
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    challenge = Column(Text)  # The core challenge/problem to solve
    industry = Column(String)
    learning_objectives = Column(JSON)  # List of learning goals
    
    # Source information
    source_type = Column(String, default="manual")  # manual, pdf_upload, template
    pdf_content = Column(Text, nullable=True)  # Original PDF content if uploaded
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public scenarios can be used by anyone
    is_template = Column(Boolean, default=False)  # Template scenarios with suggested agents/tasks
    allow_remixes = Column(Boolean, default=True)  # Allow others to create variations
    
    # Community metrics
    usage_count = Column(Integer, default=0)  # How many times used
    clone_count = Column(Integer, default=0)  # How many times cloned
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="scenarios")
    simulations = relationship("Simulation", back_populates="scenario")
    
    # Many-to-many relationships
    agents = relationship("Agent", secondary=scenario_agents, back_populates="scenarios")
    tasks = relationship("Task", secondary=scenario_tasks, back_populates="scenarios")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)
    goal = Column(Text)
    backstory = Column(Text)
    tools = Column(JSON)  # List of tool IDs/names
    verbose = Column(Boolean, default=True)
    allow_delegation = Column(Boolean, default=False)
    reasoning = Column(Boolean, default=True)
    
    # Agent categorization
    category = Column(String, nullable=True)  # business, technical, creative, analytical
    tags = Column(JSON, nullable=True)  # Searchable tags
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public agents can be used by anyone
    is_template = Column(Boolean, default=False)  # Template agents for suggestions
    allow_remixes = Column(Boolean, default=True)  # Allow others to create variations
    original_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)  # If this is a remix
    
    # Community metrics
    usage_count = Column(Integer, default=0)  # How many times used in simulations
    clone_count = Column(Integer, default=0)  # How many times cloned
    average_rating = Column(Float, default=0.0)  # Average user rating
    rating_count = Column(Integer, default=0)  # Number of ratings
    
    # Version control
    version = Column(String, default="1.0.0")
    version_notes = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="agents")
    tasks = relationship("Task", back_populates="agent")
    reviews = relationship("AgentReview", back_populates="agent")
    original_agent = relationship("Agent", remote_side=[id])  # Self-referential for remixes
    
    # Many-to-many relationships
    scenarios = relationship("Scenario", secondary=scenario_agents, back_populates="agents")
    favorited_by = relationship("User", secondary=user_favorite_agents, back_populates="favorite_agents")
    simulations_used_in = relationship("Simulation", secondary=simulation_agents, back_populates="executed_agents")

class Tool(Base):
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    tool_type = Column(String)  # web_search, file_read, api_call, custom, etc.
    
    # Tool configuration
    configuration = Column(JSON)  # Tool-specific configuration
    required_credentials = Column(JSON, nullable=True)  # What API keys/credentials needed
    usage_instructions = Column(Text, nullable=True)  # How to use this tool
    
    # Code for custom tools
    code = Column(Text, nullable=True)  # Python code for custom tools
    requirements = Column(JSON, nullable=True)  # Python dependencies
    
    # Categorization
    category = Column(String, nullable=True)  # web, file, api, data, communication
    tags = Column(JSON, nullable=True)  # Searchable tags
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public tools can be used by anyone
    is_verified = Column(Boolean, default=False)  # Verified by platform admins
    allow_remixes = Column(Boolean, default=True)  # Allow others to create variations
    original_tool_id = Column(Integer, ForeignKey("tools.id"), nullable=True)  # If this is a remix
    
    # Community metrics
    usage_count = Column(Integer, default=0)  # How many times used
    clone_count = Column(Integer, default=0)  # How many times cloned
    average_rating = Column(Float, default=0.0)  # Average user rating
    rating_count = Column(Integer, default=0)  # Number of ratings
    
    # Version control
    version = Column(String, default="1.0.0")
    version_notes = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="tools")
    reviews = relationship("ToolReview", back_populates="tool")
    original_tool = relationship("Tool", remote_side=[id])  # Self-referential for remixes
    favorited_by = relationship("User", secondary=user_favorite_tools, back_populates="favorite_tools")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    expected_output = Column(Text)  # What the task should produce
    
    # Task configuration
    tools = Column(JSON, nullable=True)  # Specific tools for this task
    context = Column(JSON, nullable=True)  # Additional context or constraints
    
    # Agent assignment
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # Task categorization
    category = Column(String, nullable=True)  # analysis, research, planning, execution
    tags = Column(JSON, nullable=True)  # Searchable tags
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public tasks can be used by anyone
    is_template = Column(Boolean, default=False)  # Template tasks for suggestions
    allow_remixes = Column(Boolean, default=True)  # Allow others to create variations
    
    # Community metrics
    usage_count = Column(Integer, default=0)  # How many times used
    clone_count = Column(Integer, default=0)  # How many times cloned
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="tasks")
    agent = relationship("Agent", back_populates="tasks")
    
    # Many-to-many relationships
    scenarios = relationship("Scenario", secondary=scenario_tasks, back_populates="tasks")
    simulations_used_in = relationship("Simulation", secondary=simulation_tasks, back_populates="executed_tasks")

class AgentReview(Base):
    __tablename__ = "agent_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    
    rating = Column(Integer)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    pros = Column(JSON, nullable=True)  # List of positive aspects
    cons = Column(JSON, nullable=True)  # List of negative aspects
    use_case = Column(String, nullable=True)  # What they used it for
    
    # Helpful votes
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="reviews")
    reviewer = relationship("User", back_populates="agent_reviews")

class ToolReview(Base):
    __tablename__ = "tool_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    
    rating = Column(Integer)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    pros = Column(JSON, nullable=True)  # List of positive aspects
    cons = Column(JSON, nullable=True)  # List of negative aspects
    use_case = Column(String, nullable=True)  # What they used it for
    
    # Helpful votes
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tool = relationship("Tool", back_populates="reviews")
    reviewer = relationship("User", back_populates="tool_reviews")

class Simulation(Base):
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Simulation configuration
    crew_configuration = Column(JSON)  # Stores the actual CrewAI crew setup
    process_type = Column(String, default="sequential")  # sequential, hierarchical, consensus
    
    # Execution details
    status = Column(String, default="created")  # created, running, completed, failed, failed_missing_resources
    crew_output = Column(Text, nullable=True)  # Final crew result
    execution_log = Column(JSON, nullable=True)  # Detailed execution steps
    error_details = Column(JSON, nullable=True)  # Details about any errors (missing agents/tasks)
    
    # Resource availability tracking
    missing_agents = Column(JSON, nullable=True)  # List of agent IDs that couldn't be accessed
    missing_tasks = Column(JSON, nullable=True)   # List of task IDs that couldn't be accessed
    fallback_used = Column(Boolean, default=False)  # Whether fallback agents/tasks were used
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public simulations can be viewed by others
    allow_sharing = Column(Boolean, default=False)  # Allow others to see the results
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    scenario = relationship("Scenario", back_populates="simulations")
    user = relationship("User", back_populates="simulations")
    messages = relationship("SimulationMessage", back_populates="simulation")
    
    # Many-to-many relationships for execution tracking
    executed_agents = relationship("Agent", secondary=simulation_agents, back_populates="simulations_used_in")
    executed_tasks = relationship("Task", secondary=simulation_tasks, back_populates="simulations_used_in")

class SimulationMessage(Base):
    __tablename__ = "simulation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    
    # Message content
    user_message = Column(Text)
    crew_response = Column(Text)
    agent_responses = Column(JSON, nullable=True)  # Individual agent responses
    
    # Message metadata
    message_type = Column(String, default="chat")  # chat, system, error
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="messages")

# Collections/Bundles - Users can create curated collections
class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    
    # Collection contents
    agents = Column(JSON, nullable=True)  # List of agent IDs
    tools = Column(JSON, nullable=True)  # List of tool IDs
    scenarios = Column(JSON, nullable=True)  # List of scenario IDs
    
    # Sharing settings
    is_public = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")

# Template data for AI suggestions  
class AgentTemplate(Base):
    __tablename__ = "agent_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    goal = Column(Text)
    backstory = Column(Text)
    tools = Column(JSON)
    category = Column(String)  # business, technical, creative, analytical
    industries = Column(JSON)  # Which industries this agent is good for
    use_cases = Column(JSON)  # Common use cases
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TaskTemplate(Base):
    __tablename__ = "task_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    expected_output = Column(Text)
    category = Column(String)  # analysis, research, planning, execution
    agent_roles = Column(JSON)  # What agent roles this task is good for
    industries = Column(JSON)  # Which industries this task is good for
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Fallback configurations for graceful error handling
class SimulationFallback(Base):
    __tablename__ = "simulation_fallbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    
    # Fallback configurations
    fallback_agents = Column(JSON)  # List of public agent IDs to use as fallbacks
    fallback_tasks = Column(JSON)   # List of public task IDs to use as fallbacks
    fallback_strategy = Column(String, default="substitute")  # substitute, skip, fail
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenario = relationship("Scenario")
    creator = relationship("User") 