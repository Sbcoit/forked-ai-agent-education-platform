# AI Agent Education Platform - Database Models
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON, Table, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

# Import pgvector if available
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    # Fallback for when pgvector is not available
    Vector = None

# Junction table for scene-persona relationships
scene_personas = Table(
    'scene_personas',
    Base.metadata,
    Column('scene_id', Integer, ForeignKey('scenario_scenes.id'), primary_key=True),
    Column('persona_id', Integer, ForeignKey('scenario_personas.id'), primary_key=True),
    Column('involvement_level', String, default='participant'),  # key, participant, mentioned
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    role = Column(String, default="user")  # admin, teacher, student, user
    
    # Community stats
    published_scenarios = Column(Integer, default=0)
    total_simulations = Column(Integer, default=0)
    reputation_score = Column(Float, default=0.0)
    
    # Settings
    profile_public = Column(Boolean, default=True)
    allow_contact = Column(Boolean, default=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenarios = relationship("Scenario", back_populates="creator")
    scenario_reviews = relationship("ScenarioReview", back_populates="reviewer")
    user_progress = relationship("UserProgress", back_populates="user")
    
    # PostgreSQL indexes for better performance
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_username', 'username'),
        Index('idx_users_role', 'role'),
        Index('idx_users_created_at', 'created_at'),
    )

class Scenario(Base):
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    challenge = Column(Text)
    industry = Column(String)
    learning_objectives = Column(JSON)
    
    # Source information
    source_type = Column(String, default="manual")  # manual, pdf_upload, template
    pdf_content = Column(Text, nullable=True)
    
    # Publishing metadata
    student_role = Column(String, nullable=True)
    category = Column(String, nullable=True)
    difficulty_level = Column(String, nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # PDF processing metadata
    pdf_title = Column(String, nullable=True)
    pdf_source = Column(String, nullable=True)
    processing_version = Column(String, default="1.0")
    
    # Community ratings
    rating_avg = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Sharing settings
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    allow_remixes = Column(Boolean, default=True)
    
    # Community metrics
    usage_count = Column(Integer, default=0)
    clone_count = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="scenarios")
    personas = relationship("ScenarioPersona", back_populates="scenario", cascade="all, delete-orphan")
    scenes = relationship("ScenarioScene", back_populates="scenario", cascade="all, delete-orphan")
    files = relationship("ScenarioFile", back_populates="scenario", cascade="all, delete-orphan")
    reviews = relationship("ScenarioReview", back_populates="scenario", cascade="all, delete-orphan")
    user_progress = relationship("UserProgress", back_populates="scenario")
    
    # PostgreSQL indexes for better performance
    __table_args__ = (
        Index('idx_scenarios_title', 'title'),
        Index('idx_scenarios_industry', 'industry'),
        Index('idx_scenarios_is_public', 'is_public'),
        Index('idx_scenarios_created_by', 'created_by'),
        Index('idx_scenarios_created_at', 'created_at'),
        Index('idx_scenarios_rating_avg', 'rating_avg'),
    )

class ScenarioPersona(Base):
    __tablename__ = "scenario_personas"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    # Persona details from AI processing
    name = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    background = Column(Text, nullable=True)
    correlation = Column(Text, nullable=True)
    
    # Goals and traits from AI
    primary_goals = Column(JSON, nullable=True)
    personality_traits = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenario = relationship("Scenario", back_populates="personas")
    scenes = relationship("ScenarioScene", secondary=scene_personas, back_populates="personas")
    conversation_logs = relationship("ConversationLog", back_populates="persona")

class ScenarioScene(Base):
    __tablename__ = "scenario_scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    # Scene details from AI processing
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    user_goal = Column(Text, nullable=True)
    scene_order = Column(Integer, default=0)
    estimated_duration = Column(Integer, nullable=True)
    
    # New fields for simulation control
    timeout_turns = Column(Integer, nullable=True)  # Number of turns before timeout
    success_metric = Column(String, nullable=True)  # How to measure scene success
    
    # Sequential simulation features
    max_attempts = Column(Integer, default=5)
    success_threshold = Column(Float, default=0.7)
    goal_criteria = Column(JSON, nullable=True)
    hint_triggers = Column(JSON, nullable=True)
    scene_context = Column(Text, nullable=True)
    persona_instructions = Column(JSON, nullable=True)
    
    # Visual assets
    image_url = Column(String, nullable=True)
    image_prompt = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenario = relationship("Scenario", back_populates="scenes")
    personas = relationship("ScenarioPersona", secondary=scene_personas, back_populates="scenes")
    scene_progress = relationship("SceneProgress", back_populates="scene")
    conversation_logs = relationship("ConversationLog", back_populates="scene")

class ScenarioFile(Base):
    __tablename__ = "scenario_files"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    filename = Column(String, nullable=False)  # Add missing filename field
    file_path = Column(String, nullable=True)  # Make nullable since we have filename
    file_size = Column(Integer, nullable=True)
    file_type = Column(String, nullable=True)
    original_content = Column(Text, nullable=True)
    processed_content = Column(Text, nullable=True)
    processing_status = Column(String, default="pending")
    processing_log = Column(JSON, nullable=True)
    llamaparse_job_id = Column(String, nullable=True)  # Add missing field from schema
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    scenario = relationship("Scenario", back_populates="files")

class ScenarioReview(Base):
    __tablename__ = "scenario_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    
    rating = Column(Integer)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    pros = Column(JSON, nullable=True)
    cons = Column(JSON, nullable=True)
    use_case = Column(String, nullable=True)
    
    # Helpful votes
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scenario = relationship("Scenario", back_populates="reviews")
    reviewer = relationship("User", back_populates="scenario_reviews")

# --- SEQUENTIAL SIMULATION SYSTEM MODELS ---

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Allow None for now
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    # Current simulation state
    current_scene_id = Column(Integer, ForeignKey("scenario_scenes.id"), nullable=True)
    simulation_status = Column(String, default="not_started")  # not_started, in_progress, completed, abandoned
    
    # Progress tracking
    scenes_completed = Column(JSON, default=list)
    total_attempts = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    forced_progressions = Column(Integer, default=0)
    
    # Orchestrator state for linear simulation
    orchestrator_data = Column(JSON, nullable=True)
    
    # Performance metrics
    completion_percentage = Column(Float, default=0.0)
    total_time_spent = Column(Integer, default=0)
    session_count = Column(Integer, default=0)
    final_score = Column(Float, nullable=True)
    
    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_progress")
    scenario = relationship("Scenario", back_populates="user_progress")
    current_scene = relationship("ScenarioScene", foreign_keys=[current_scene_id])
    scene_progress = relationship("SceneProgress", back_populates="user_progress")
    conversation_logs = relationship("ConversationLog", back_populates="user_progress")

class SceneProgress(Base):
    __tablename__ = "scene_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenario_scenes.id"), nullable=False)
    
    # Progress tracking
    status = Column(String, default="not_started")  # not_started, in_progress, completed, failed
    attempts = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    goal_achieved = Column(Boolean, default=False)
    forced_progression = Column(Boolean, default=False)
    
    # Performance metrics
    time_spent = Column(Integer, default=0)  # seconds
    messages_sent = Column(Integer, default=0)
    ai_responses = Column(Integer, default=0)
    goal_achievement_score = Column(Float, nullable=True)
    interaction_quality = Column(Float, nullable=True)
    scene_feedback = Column(Text, nullable=True)
    
    # Metadata
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_progress = relationship("UserProgress", back_populates="scene_progress")
    scene = relationship("ScenarioScene", back_populates="scene_progress")

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenario_scenes.id"), nullable=False)
    
    # Message details
    message_type = Column(String, nullable=False)  # user, ai_persona, system, hint
    sender_name = Column(String, nullable=True)
    persona_id = Column(Integer, ForeignKey("scenario_personas.id"), nullable=True)
    message_content = Column(Text, nullable=False)
    
    # Context and metadata
    message_order = Column(Integer, nullable=False)
    attempt_number = Column(Integer, default=1)
    is_hint = Column(Boolean, default=False)
    
    # AI processing context
    ai_context_used = Column(JSON, nullable=True)
    ai_model_version = Column(String, nullable=True)
    processing_time = Column(Float, nullable=True)
    
    # User interaction tracking
    user_reaction = Column(String, nullable=True)
    led_to_progress = Column(Boolean, default=False)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_progress = relationship("UserProgress", back_populates="conversation_logs")
    scene = relationship("ScenarioScene", back_populates="conversation_logs")
    persona = relationship("ScenarioPersona", back_populates="conversation_logs")


# ============================================================================
# LangChain Integration Models
# ============================================================================

class VectorEmbeddings(Base):
    """Store vector embeddings for similarity search"""
    __tablename__ = "vector_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, nullable=False, index=True)  # 'scenario', 'persona', 'conversation', etc.
    content_id = Column(Integer, nullable=False, index=True)  # ID of the original content
    content_hash = Column(String, nullable=False, index=True)  # Hash for deduplication
    embedding_vector = Column(Vector(1536) if PGVECTOR_AVAILABLE else Text, nullable=False)  # Vector embedding
    embedding_model = Column(String, nullable=False)  # 'openai-ada-002', 'sentence-transformers', etc.
    embedding_dimension = Column(Integer, nullable=False)  # Dimension of the vector
    original_content = Column(Text, nullable=False)  # Original text content
    content_metadata = Column(JSON, nullable=True)  # Additional metadata
    similarity_threshold = Column(Float, nullable=True)  # Threshold for similarity matching
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_vector_embeddings_content_type', 'content_type'),
        Index('idx_vector_embeddings_content_id', 'content_id'),
        Index('idx_vector_embeddings_content_hash', 'content_hash'),
        Index('idx_vector_embeddings_active', 'is_active'),
        Index('idx_vector_embeddings_created_at', 'created_at'),
    )


class SessionMemory(Base):
    """Store session-specific memory for LangChain agents"""
    __tablename__ = "session_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False, index=True)
    scene_id = Column(Integer, ForeignKey("scenario_scenes.id"), nullable=True, index=True)
    memory_type = Column(String, nullable=False, index=True)  # 'conversation', 'context', 'summary', 'insight'
    memory_content = Column(Text, nullable=False)  # The actual memory content
    memory_metadata = Column(JSON, nullable=True)  # Additional metadata
    parent_memory_id = Column(Integer, ForeignKey("session_memory.id"), nullable=True)  # For hierarchical memory
    related_persona_id = Column(Integer, ForeignKey("scenario_personas.id"), nullable=True)  # If memory is persona-specific
    importance_score = Column(Float, nullable=True, index=True)  # 0.0 to 1.0
    access_count = Column(Integer, default=0)  # How many times this memory was accessed
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_progress = relationship("UserProgress")
    scene = relationship("ScenarioScene")
    persona = relationship("ScenarioPersona")
    parent_memory = relationship("SessionMemory", remote_side=[id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_session_memory_session_id', 'session_id'),
        Index('idx_session_memory_user_progress_id', 'user_progress_id'),
        Index('idx_session_memory_scene_id', 'scene_id'),
        Index('idx_session_memory_type', 'memory_type'),
        Index('idx_session_memory_importance', 'importance_score'),
        Index('idx_session_memory_last_accessed', 'last_accessed'),
    )


class ConversationSummaries(Base):
    """Store AI-generated summaries of conversations"""
    __tablename__ = "conversation_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False, index=True)
    scene_id = Column(Integer, ForeignKey("scenario_scenes.id"), nullable=True, index=True)
    summary_type = Column(String, nullable=False, index=True)  # 'scene_completion', 'conversation', 'learning_moment'
    summary_text = Column(Text, nullable=False)  # The summary content
    key_points = Column(JSON, nullable=True)  # Extracted key points
    learning_moments = Column(JSON, nullable=True)  # Important learning moments
    insights = Column(JSON, nullable=True)  # AI-generated insights
    recommendations = Column(JSON, nullable=True)  # Recommendations for improvement
    conversation_count = Column(Integer, nullable=True)  # Number of conversations summarized
    message_count = Column(Integer, nullable=True)  # Number of messages summarized
    summary_metadata = Column(JSON, nullable=True)  # Additional metadata
    quality_score = Column(Float, nullable=True, index=True)  # Quality score of the summary
    relevance_score = Column(Float, nullable=True)  # Relevance to learning objectives
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_progress = relationship("UserProgress")
    scene = relationship("ScenarioScene")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_conversation_summaries_user_progress_id', 'user_progress_id'),
        Index('idx_conversation_summaries_scene_id', 'scene_id'),
        Index('idx_conversation_summaries_type', 'summary_type'),
        Index('idx_conversation_summaries_quality', 'quality_score'),
        Index('idx_conversation_summaries_created_at', 'created_at'),
    )


class AgentSessions(Base):
    """Store LangChain agent session information"""
    __tablename__ = "agent_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, unique=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False, index=True)
    agent_type = Column(String, nullable=False, index=True)  # 'persona', 'grading', 'summarization', 'retrieval'
    agent_id = Column(String, nullable=True, index=True)  # Specific agent identifier
    session_state = Column(JSON, nullable=True)  # Current session state
    session_config = Column(JSON, nullable=True)  # Session configuration
    session_metadata = Column(JSON, nullable=True)  # Additional metadata
    total_interactions = Column(Integer, default=0)  # Total number of interactions
    total_tokens_used = Column(Integer, default=0)  # Total tokens consumed
    average_response_time = Column(Float, nullable=True)  # Average response time in seconds
    error_count = Column(Integer, default=0)  # Number of errors encountered
    is_active = Column(Boolean, default=True, index=True)  # Whether session is active
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)  # Session expiration
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_progress = relationship("UserProgress")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_agent_sessions_session_id', 'session_id'),
        Index('idx_agent_sessions_user_progress_id', 'user_progress_id'),
        Index('idx_agent_sessions_agent_type', 'agent_type'),
        Index('idx_agent_sessions_active', 'is_active'),
        Index('idx_agent_sessions_last_activity', 'last_activity'),
    )


class CacheEntries(Base):
    """Store cached data for performance optimization"""
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, nullable=False, unique=True, index=True)
    cache_type = Column(String, nullable=False, index=True)  # 'embedding', 'response', 'summary', 'context'
    cache_data = Column(JSON, nullable=False)  # The cached data
    cache_size = Column(Integer, nullable=True)  # Size of cached data in bytes
    hit_count = Column(Integer, default=0)  # Number of cache hits
    miss_count = Column(Integer, default=0)  # Number of cache misses
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)  # Cache expiration
    is_expired = Column(Boolean, default=False, index=True)  # Whether cache is expired
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_cache_entries_key', 'cache_key'),
        Index('idx_cache_entries_type', 'cache_type'),
        Index('idx_cache_entries_expires_at', 'expires_at'),
        Index('idx_cache_entries_last_accessed', 'last_accessed'),
    )


# Alias for backward compatibility
EmbeddingStore = VectorEmbeddings 