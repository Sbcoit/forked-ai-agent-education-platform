# 🗄️ Database & Migrations Guide

## Overview

The AI Agent Education Platform uses PostgreSQL as the primary database with Alembic for migration management. The database is designed to support complex educational simulations with AI agents, user progress tracking, and community features.

## 🏗️ Database Architecture

### Core Design Principles
- **PostgreSQL First**: Optimized for PostgreSQL with fallback to SQLite for development
- **JSON Support**: Rich JSON fields for flexible data storage (personality traits, learning objectives)
- **Vector Support**: pgvector extension for semantic search and AI memory
- **Performance Optimized**: Comprehensive indexing and query optimization
- **Scalable Design**: Supports high-volume educational content and user interactions

### Database Technology Stack
- **Primary Database**: PostgreSQL 13+
- **Migration Tool**: Alembic
- **ORM**: SQLAlchemy with async support
- **Vector Extension**: pgvector for embeddings
- **Connection Pooling**: SQLAlchemy connection pooling
- **Backup Strategy**: Automated backups with point-in-time recovery

## 📊 Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ scenarios : creates
    users ||--o{ user_progress : tracks
    users ||--o{ scenario_reviews : writes
    users ||--o{ conversation_logs : participates
    
    scenarios ||--o{ scenario_personas : contains
    scenarios ||--o{ scenario_scenes : contains
    scenarios ||--o{ scenario_files : has
    scenarios ||--o{ user_progress : simulates
    scenarios ||--o{ scenario_reviews : receives
    
    scenario_personas ||--o{ scene_personas : participates_in
    scenario_scenes ||--o{ scene_personas : includes
    scenario_scenes ||--o{ scene_progress : tracks
    scenario_scenes ||--o{ conversation_logs : contains
    
    user_progress ||--o{ scene_progress : tracks
    user_progress ||--o{ conversation_logs : generates
    
    session_memory ||--o{ conversation_summaries : contains
    agent_sessions ||--o{ cache_entries : uses
    vector_embeddings ||--o{ cache_entries : stores
```

## 👥 User Management

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    username VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    bio TEXT,
    avatar_url VARCHAR,
    role VARCHAR DEFAULT 'user', -- admin, teacher, student, user
    
    -- Community stats
    published_scenarios INTEGER DEFAULT 0,
    total_simulations INTEGER DEFAULT 0,
    reputation_score FLOAT DEFAULT 0.0,
    
    -- Settings
    profile_public BOOLEAN DEFAULT TRUE,
    allow_contact BOOLEAN DEFAULT TRUE,
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Key Features:**
- **Unique Constraints**: Email and username uniqueness
- **Role-Based Access**: Support for different user types
- **Community Metrics**: Track user contributions and reputation
- **Privacy Controls**: Public/private profile settings
- **Account Management**: Active/verified status tracking

**Indexes:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);
```

## 📚 Scenario Management

### Scenarios Table
```sql
CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    challenge TEXT,
    industry VARCHAR,
    learning_objectives JSONB, -- Array of learning objectives
    
    -- Source information
    source_type VARCHAR DEFAULT 'manual', -- manual, pdf_upload, template
    pdf_content TEXT,
    
    -- Publishing metadata
    student_role VARCHAR,
    category VARCHAR,
    difficulty_level VARCHAR,
    estimated_duration INTEGER,
    tags JSONB, -- Array of tags
    
    -- PDF processing metadata
    pdf_title VARCHAR,
    pdf_source VARCHAR,
    processing_version VARCHAR DEFAULT '1.0',
    
    -- Community ratings
    rating_avg FLOAT DEFAULT 0.0,
    rating_count INTEGER DEFAULT 0,
    
    -- Sharing settings
    is_public BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    allow_remixes BOOLEAN DEFAULT TRUE,
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    clone_count INTEGER DEFAULT 0,
    
    -- Ownership
    created_by INTEGER REFERENCES users(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Key Features:**
- **Rich Metadata**: Comprehensive scenario information
- **JSON Fields**: Flexible storage for learning objectives and tags
- **Source Tracking**: Track how scenarios were created
- **Community Features**: Ratings, usage tracking, sharing controls
- **Version Control**: Processing version tracking for AI-generated content

**Indexes:**
```sql
CREATE INDEX idx_scenarios_title ON scenarios(title);
CREATE INDEX idx_scenarios_industry ON scenarios(industry);
CREATE INDEX idx_scenarios_is_public ON scenarios(is_public);
CREATE INDEX idx_scenarios_created_by ON scenarios(created_by);
CREATE INDEX idx_scenarios_rating_avg ON scenarios(rating_avg);
CREATE INDEX idx_scenarios_created_at ON scenarios(created_at);
```

## 🎭 AI Personas

### Scenario Personas Table
```sql
CREATE TABLE scenario_personas (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    background TEXT,
    correlation TEXT, -- How this persona relates to the scenario
    primary_goals JSONB, -- Array of primary goals
    personality_traits JSONB, -- Personality trait scores
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Personality Traits Structure:**
```json
{
    "analytical": 8,
    "creative": 6,
    "assertive": 7,
    "collaborative": 9,
    "detail_oriented": 8
}
```

**Primary Goals Structure:**
```json
[
    "Increase market share by 15%",
    "Improve customer satisfaction",
    "Reduce operational costs"
]
```

## 🎬 Scene Management

### Scenario Scenes Table
```sql
CREATE TABLE scenario_scenes (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    description TEXT,
    user_goal TEXT, -- What the user should achieve in this scene
    scene_order INTEGER NOT NULL,
    estimated_duration INTEGER, -- Duration in minutes
    image_url VARCHAR,
    image_prompt TEXT, -- Prompt used to generate the image
    timeout_turns INTEGER DEFAULT 20, -- Maximum turns before auto-progression
    success_metric TEXT, -- How success is measured
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Scene-Persona Relationships
```sql
CREATE TABLE scene_personas (
    scene_id INTEGER REFERENCES scenario_scenes(id) ON DELETE CASCADE,
    persona_id INTEGER REFERENCES scenario_personas(id) ON DELETE CASCADE,
    involvement_level VARCHAR DEFAULT 'participant', -- key, participant, mentioned
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (scene_id, persona_id)
);
```

## 📈 User Progress Tracking

### User Progress Table
```sql
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    current_scene_id INTEGER REFERENCES scenario_scenes(id),
    
    -- Progress tracking
    status VARCHAR DEFAULT 'in_progress', -- in_progress, completed, paused, abandoned
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    total_time_spent INTEGER DEFAULT 0, -- Total time in seconds
    
    -- Simulation state
    current_turn INTEGER DEFAULT 0,
    total_turns INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    
    -- Performance metrics
    scenes_completed INTEGER DEFAULT 0,
    total_scenes INTEGER,
    completion_percentage FLOAT DEFAULT 0.0,
    
    -- AI interaction data
    orchestrator_data JSONB, -- ChatOrchestrator state
    conversation_summary TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Scene Progress Table
```sql
CREATE TABLE scene_progress (
    id SERIAL PRIMARY KEY,
    user_progress_id INTEGER REFERENCES user_progress(id) ON DELETE CASCADE,
    scene_id INTEGER REFERENCES scenario_scenes(id) ON DELETE CASCADE,
    
    -- Scene completion
    status VARCHAR DEFAULT 'not_started', -- not_started, in_progress, completed, skipped
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_spent INTEGER DEFAULT 0, -- Time in seconds
    
    -- Interaction metrics
    turns_taken INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    goal_achieved BOOLEAN DEFAULT FALSE,
    
    -- Performance data
    completion_score FLOAT, -- 0.0 to 1.0
    feedback_data JSONB, -- Detailed feedback and assessment
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 💬 Conversation Management

### Conversation Logs Table
```sql
CREATE TABLE conversation_logs (
    id SERIAL PRIMARY KEY,
    user_progress_id INTEGER REFERENCES user_progress(id) ON DELETE CASCADE,
    scene_id INTEGER REFERENCES scenario_scenes(id) ON DELETE CASCADE,
    
    -- Message details
    message_type VARCHAR NOT NULL, -- user_message, ai_persona, system_message
    sender_name VARCHAR, -- Name of the persona or user
    message_content TEXT NOT NULL,
    
    -- Context information
    turn_number INTEGER,
    persona_id INTEGER REFERENCES scenario_personas(id),
    
    -- Metadata
    processing_time FLOAT, -- Time taken to generate response
    token_count INTEGER, -- Number of tokens used
    model_used VARCHAR, -- AI model used for generation
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🧠 AI Agent Memory System

### Session Memory Table
```sql
CREATE TABLE session_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    scene_id INTEGER REFERENCES scenario_scenes(id),
    
    -- Memory content
    memory_type VARCHAR NOT NULL, -- conversation, context, summary
    content TEXT NOT NULL,
    metadata JSONB, -- Additional context and metadata
    
    -- Memory management
    importance_score FLOAT DEFAULT 0.5, -- 0.0 to 1.0
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Conversation Summaries Table
```sql
CREATE TABLE conversation_summaries (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    user_progress_id INTEGER REFERENCES user_progress(id) ON DELETE CASCADE,
    
    -- Summary content
    summary_type VARCHAR NOT NULL, -- scene_summary, progress_summary, key_points
    content TEXT NOT NULL,
    key_points JSONB, -- Array of key points extracted
    
    -- Context
    scene_id INTEGER REFERENCES scenario_scenes(id),
    turn_range_start INTEGER,
    turn_range_end INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🤖 Agent Session Management

### Agent Sessions Table
```sql
CREATE TABLE agent_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR UNIQUE NOT NULL,
    user_progress_id INTEGER REFERENCES user_progress(id) ON DELETE CASCADE,
    
    -- Agent configuration
    agent_type VARCHAR NOT NULL, -- persona, summarization, grading
    agent_id VARCHAR, -- Specific agent identifier
    session_config JSONB, -- Agent-specific configuration
    
    -- Session state
    status VARCHAR DEFAULT 'active', -- active, paused, completed, error
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Performance metrics
    total_interactions INTEGER DEFAULT 0,
    average_response_time FLOAT,
    error_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Cache Entries Table
```sql
CREATE TABLE cache_entries (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR UNIQUE NOT NULL,
    content_type VARCHAR NOT NULL, -- response, embedding, summary
    
    -- Cache content
    content_data BYTEA, -- Serialized cache data
    content_text TEXT, -- Text content for search
    metadata JSONB, -- Cache metadata and tags
    
    -- Cache management
    ttl_seconds INTEGER, -- Time to live in seconds
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);
```

## 🔍 Vector Embeddings

### Vector Embeddings Table
```sql
CREATE TABLE vector_embeddings (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR NOT NULL, -- scenario, persona, scene, conversation
    content_id INTEGER, -- ID of the related entity
    
    -- Embedding data
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI embedding dimension
    metadata JSONB, -- Additional context and metadata
    
    -- Search optimization
    collection_name VARCHAR DEFAULT 'default',
    document_id VARCHAR, -- Unique identifier for the document
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Vector Search Example:**
```sql
-- Find similar content using vector similarity
SELECT content, metadata, 
       1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM vector_embeddings 
WHERE collection_name = 'scenarios'
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

## 📁 File Management

### Scenario Files Table
```sql
CREATE TABLE scenario_files (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    
    -- File information
    filename VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL, -- pdf, image, document
    file_size INTEGER, -- Size in bytes
    file_path VARCHAR NOT NULL,
    
    -- Processing status
    processing_status VARCHAR DEFAULT 'pending', -- pending, processing, completed, failed
    processing_metadata JSONB, -- Processing results and metadata
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## ⭐ Community Features

### Scenario Reviews Table
```sql
CREATE TABLE scenario_reviews (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Review content
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR,
    review_text TEXT,
    
    -- Review metadata
    helpful_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE, -- Verified purchase/usage
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(scenario_id, reviewer_id) -- One review per user per scenario
);
```

## 🔧 Database Migrations

### Alembic Configuration

**alembic.ini:**
```ini
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://user:password@localhost/ai_agent_platform

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME
```

### Creating Migrations

```bash
# Navigate to database directory
cd backend/database

# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Check current version
alembic current

# View migration history
alembic history
```

### Migration Best Practices

1. **Always Review Auto-Generated Migrations**
   ```python
   # Review the generated migration file
   # Ensure it matches your intended changes
   # Add any custom logic if needed
   ```

2. **Test Migrations on Development Data**
   ```bash
   # Test migration on development database
   alembic upgrade head
   # Verify data integrity
   # Test rollback if needed
   ```

3. **Use Descriptive Migration Messages**
   ```bash
   alembic revision --autogenerate -m "Add user progress tracking with scene completion metrics"
   ```

4. **Never Edit Existing Migration Files**
   - Create new migrations for changes
   - Use rollback and re-apply for corrections

## 🚀 Performance Optimization

### Indexing Strategy

**Primary Indexes:**
```sql
-- User table indexes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_username ON users(username);
CREATE INDEX CONCURRENTLY idx_users_role ON users(role);

-- Scenario table indexes
CREATE INDEX CONCURRENTLY idx_scenarios_public ON scenarios(is_public) WHERE is_public = true;
CREATE INDEX CONCURRENTLY idx_scenarios_industry ON scenarios(industry);
CREATE INDEX CONCURRENTLY idx_scenarios_rating ON scenarios(rating_avg DESC);

-- User progress indexes
CREATE INDEX CONCURRENTLY idx_user_progress_user ON user_progress(user_id);
CREATE INDEX CONCURRENTLY idx_user_progress_scenario ON user_progress(scenario_id);
CREATE INDEX CONCURRENTLY idx_user_progress_status ON user_progress(status);

-- Conversation logs indexes
CREATE INDEX CONCURRENTLY idx_conversation_logs_progress ON conversation_logs(user_progress_id);
CREATE INDEX CONCURRENTLY idx_conversation_logs_scene ON conversation_logs(scene_id);
CREATE INDEX CONCURRENTLY idx_conversation_logs_created ON conversation_logs(created_at);
```

**Composite Indexes:**
```sql
-- Multi-column indexes for common queries
CREATE INDEX CONCURRENTLY idx_scenarios_public_rating ON scenarios(is_public, rating_avg DESC);
CREATE INDEX CONCURRENTLY idx_user_progress_user_status ON user_progress(user_id, status);
CREATE INDEX CONCURRENTLY idx_conversation_logs_progress_scene ON conversation_logs(user_progress_id, scene_id);
```

### Query Optimization

**Common Query Patterns:**
```sql
-- Get public scenarios with ratings
SELECT s.*, u.username as creator_name
FROM scenarios s
JOIN users u ON s.created_by = u.id
WHERE s.is_public = true
ORDER BY s.rating_avg DESC, s.usage_count DESC
LIMIT 20;

-- Get user progress with scene details
SELECT up.*, s.title as scenario_title, sc.title as current_scene_title
FROM user_progress up
JOIN scenarios s ON up.scenario_id = s.id
LEFT JOIN scenario_scenes sc ON up.current_scene_id = sc.id
WHERE up.user_id = ? AND up.status = 'in_progress';

-- Get conversation history for a scene
SELECT cl.*, sp.name as persona_name
FROM conversation_logs cl
LEFT JOIN scenario_personas sp ON cl.persona_id = sp.id
WHERE cl.user_progress_id = ? AND cl.scene_id = ?
ORDER BY cl.created_at ASC;
```

## 🔒 Security Considerations

### Data Protection
- **Encryption at Rest**: Database-level encryption for sensitive data
- **Encryption in Transit**: SSL/TLS for all database connections
- **Access Control**: Role-based database access with minimal privileges
- **Audit Logging**: Track all database access and modifications

### Backup Strategy
```bash
# Daily automated backups
pg_dump -h localhost -U username -d ai_agent_platform > backup_$(date +%Y%m%d).sql

# Point-in-time recovery setup
# Configure WAL archiving for continuous backup
```

### Data Retention
- **Conversation Logs**: Retain for 1 year, then archive
- **User Progress**: Retain indefinitely for analytics
- **Cache Entries**: Auto-expire based on TTL
- **Session Memory**: Clean up inactive sessions after 30 days

## 📊 Monitoring & Maintenance

### Database Monitoring
```sql
-- Monitor database size
SELECT pg_size_pretty(pg_database_size('ai_agent_platform'));

-- Monitor table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Monitor slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Maintenance Tasks
```sql
-- Update table statistics
ANALYZE;

-- Reindex for performance
REINDEX DATABASE ai_agent_platform;

-- Vacuum for space reclamation
VACUUM ANALYZE;
```

---

*For API implementation details, see the [API Reference](API_Reference.md). For development setup, see the [Developer Guide](Developer_Guide.md).*
