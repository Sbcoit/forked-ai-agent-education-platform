# AI Agent Education Platform - Architecture Diagram

## System Overview

This document provides a comprehensive visual representation of the AI Agent Education Platform architecture, showing the complete system from user interface to data storage, including the PDF-to-simulation pipeline and ChatOrchestrator integration.

## High-Level System Architecture

```mermaid
graph TB
    %% User Layer
    subgraph "User Interface Layer"
        WEB[Web Browser<br/>Next.js 15 Frontend]
        MOBILE[Mobile Interface<br/>Responsive Design]
    end
    
    %% Frontend Components
    subgraph "Frontend Application (Next.js 15)"
        DASHBOARD[Dashboard<br/>/dashboard]
        CHATBOX[Chat Interface<br/>/chat-box]
        SIMULATION_BUILDER[Simulation Builder<br/>/simulation-builder]
        AGENT_BUILDER[Agent Builder<br/>/agent-builder]
        SIGNUP[Signup Page<br/>/signup]
        LOGIN[Login Page<br/>/login]
        COHORTS[Cohorts<br/>/cohorts]
        RESOURCES[Resources<br/>/resources]
        PROFILE[Profile<br/>/profile]
    end
    
    %% API Gateway
    subgraph "API Gateway & Middleware"
        FASTAPI[FastAPI Server<br/>main.py]
        AUTH[Authentication<br/>JWT Middleware]
        CORS[CORS Middleware<br/>Cross-Origin Support]
        STATIC[Static Files<br/>/static]
    end
    
    %% API Routers
    subgraph "API Routers"
        PDF_ROUTER[PDF Router<br/>/api/parse-pdf]
        SIMULATION_ROUTER[Simulation Router<br/>/api/simulation]
        PUBLISHING_ROUTER[Publishing Router<br/>/api/scenarios]
    end
    
    %% Core Modules
    subgraph "Core Modules"
        CHAT_ORCHESTRATOR[ChatOrchestrator<br/>chat_orchestrator.py]
        SIMULATION_ENGINE[Simulation Engine<br/>simulation_engine.py]
        SESSION_MANAGER[Session Manager<br/>session_manager.py]
        SCENE_MEMORY[Scene Memory<br/>scene_memory.py]
        VECTOR_STORE[Vector Store<br/>vector_store.py]
        LANGCHAIN_CONFIG[LangChain Config<br/>langchain_config.py]
    end
    
    %% AI Agents
    subgraph "AI Agents"
        PERSONA_AGENT[Persona Agent<br/>persona_agent.py]
        SUMMARIZATION_AGENT[Summarization Agent<br/>summarization_agent.py]
        GRADING_AGENT[Grading Agent<br/>grading_agent.py]
    end
    
    %% External AI Services
    subgraph "External AI Services"
        OPENAI[OpenAI GPT-4<br/>Language Model]
        LLAMAPARSE[LlamaParse API<br/>PDF Processing]
        DALL_E[DALL-E 3<br/>Image Generation]
    end
    
    %% Data Layer
    subgraph "Data Storage Layer"
        POSTGRES[(PostgreSQL Database<br/>Primary Data Store)]
        FILE_STORAGE[File Storage<br/>PDFs & Images]
        ALEMBIC[Alembic<br/>Database Migrations]
    end
    
    %% Database Models
    subgraph "Database Models"
        USER_MODEL[User Model]
        SCENARIO_MODEL[Scenario Model]
        PERSONA_MODEL[ScenarioPersona Model]
        SCENE_MODEL[ScenarioScene Model]
        PROGRESS_MODEL[UserProgress Model]
        CONVERSATION_MODEL[ConversationLog Model]
    end
    
    %% User Interface Connections
    WEB --> DASHBOARD
    WEB --> CHATBOX
    WEB --> SIMULATION_BUILDER
    WEB --> AGENT_BUILDER
    WEB --> SIGNUP
    WEB --> COHORTS
    WEB --> RESOURCES
    WEB --> PROFILE
    MOBILE --> DASHBOARD
    
    %% Frontend to API Gateway
    DASHBOARD --> FASTAPI
    CHATBOX --> FASTAPI
    SIMULATION_BUILDER --> FASTAPI
    AGENT_BUILDER --> FASTAPI
    SIGNUP --> FASTAPI
    COHORTS --> FASTAPI
    RESOURCES --> FASTAPI
    PROFILE --> FASTAPI
    
    %% API Gateway Processing
    FASTAPI --> AUTH
    FASTAPI --> CORS
    FASTAPI --> STATIC
    
    %% API Router Connections
    FASTAPI --> PDF_ROUTER
    FASTAPI --> SIMULATION_ROUTER
    FASTAPI --> PUBLISHING_ROUTER
    
    %% Core Module Connections
    PDF_ROUTER --> CHAT_ORCHESTRATOR
    SIMULATION_ROUTER --> CHAT_ORCHESTRATOR
    SIMULATION_ROUTER --> SIMULATION_ENGINE
    CHAT_ORCHESTRATOR --> SESSION_MANAGER
    CHAT_ORCHESTRATOR --> SCENE_MEMORY
    SIMULATION_ENGINE --> VECTOR_STORE
    SIMULATION_ENGINE --> LANGCHAIN_CONFIG
    
    %% AI Agent Connections
    PERSONA_AGENT --> LANGCHAIN_CONFIG
    SUMMARIZATION_AGENT --> LANGCHAIN_CONFIG
    GRADING_AGENT --> LANGCHAIN_CONFIG
    LANGCHAIN_CONFIG --> OPENAI
    
    %% External Service Connections
    PDF_ROUTER --> LLAMAPARSE
    PDF_ROUTER --> OPENAI
    PDF_ROUTER --> DALL_E
    SIMULATION_ENGINE --> OPENAI
    CHAT_ORCHESTRATOR --> OPENAI
    
    %% Data Layer Connections
    PDF_ROUTER --> POSTGRES
    SIMULATION_ROUTER --> POSTGRES
    PUBLISHING_ROUTER --> POSTGRES
    POSTGRES --> ALEMBIC
    
    %% Database Model Connections
    POSTGRES --> USER_MODEL
    POSTGRES --> SCENARIO_MODEL
    POSTGRES --> PERSONA_MODEL
    POSTGRES --> SCENE_MODEL
    POSTGRES --> PROGRESS_MODEL
    POSTGRES --> CONVERSATION_MODEL
    
    %% File Storage Connections
    PDF_ROUTER --> FILE_STORAGE
    SIMULATION_ENGINE --> FILE_STORAGE
```

## PDF-to-Simulation Pipeline Architecture

```mermaid
graph TD
    A[PDF Upload] --> B[File Validation<br/>parse_pdf.py]
    B --> C[LlamaParse Processing<br/>extract_text_from_pdf]
    C --> D[Content Cleaning<br/>clean_and_preprocess_text]
    D --> E[First AI Call - GPT-4o<br/>extract_personas_and_metadata]
    E --> F[Second AI Call - GPT-4o<br/>generate_timeline_scenes]
    F --> G[DALL-E Image Generation<br/>generate_scene_images]
    G --> H[Structured JSON Response<br/>AIProcessingResult]
    
    E --> I[Title, Description, Student Role]
    E --> J[Key Figures with Traits]
    E --> K[Learning Outcomes]
    
    F --> L[Scene 1: Crisis Assessment]
    F --> M[Scene 2: Root Cause Analysis] 
    F --> N[Scene 3: Strategy Development]
    F --> O[Scene 4: Implementation]
    
    G --> P[Professional Scene Images]
    
    H --> Q[Save to Database<br/>save_scenario_draft]
    Q --> R[Scenario Created<br/>Ready for Simulation]
    
    %% API Endpoints
    subgraph "API Endpoints"
        API1[POST /api/parse-pdf/upload]
        API2[POST /api/parse-pdf/process]
        API3[POST /api/scenarios/save]
    end
    
    A --> API1
    API1 --> API2
    API2 --> API3
    API3 --> R
    
    style A fill:#e1f5fe
    style R fill:#c8e6c9
    style E fill:#fff3e0
    style F fill:#fff3e0
    style G fill:#f3e5f5
```

## ChatOrchestrator System Architecture

```mermaid
graph LR
    A[ChatOrchestrator Engine<br/>chat_orchestrator.py] --> B[SimulationState<br/>State Management]
    A --> C[Scene Progression<br/>Manager]
    A --> D[Persona Interaction<br/>Engine]
    A --> E[Command Processor<br/>Command Handling]
    
    B --> B1[Current Scene ID]
    B --> B2[Turn Count]
    B --> B3[Scene Completed]
    B --> B4[User Ready State]
    
    C --> C1[Scene Transition Logic]
    C --> C2[Progress Monitoring]
    C --> C3[Goal Achievement Detection]
    C --> C4[Next Scene Loading]
    
    D --> D1[AI Persona Responses<br/>generate_persona_response]
    D --> D2[Personality-Based Interactions<br/>personality_traits]
    D --> D3[@Mention Handling<br/>handle_mentions]
    D --> D4[Multi-Character Conversations<br/>conversation_history]
    
    E --> E1[begin Command<br/>start_simulation]
    E --> E2[help Command<br/>show_help]
    E --> E3[@mention Commands<br/>handle_persona_mention]
    E --> E4[Progress Commands<br/>check_progress]
    
    A --> F[Session Manager<br/>session_manager.py]
    A --> G[Scene Memory<br/>scene_memory.py]
    A --> H[LangChain Integration<br/>langchain_config.py]
    
    F --> I[Session State<br/>Persistence]
    G --> J[Scene Context<br/>Memory]
    H --> K[OpenAI GPT-4<br/>Integration]
    
    D1 --> K
    D2 --> K
    E1 --> L[Database State<br/>Persistence]
    C3 --> L
```

## Database Schema Architecture

```mermaid
erDiagram
    %% Core User System
    users {
        integer id PK
        string email UK
        string full_name
        string username UK
        string password_hash
        text bio
        string avatar_url
        string role
        integer published_scenarios
        integer total_simulations
        float reputation_score
        boolean profile_public
        boolean allow_contact
        boolean is_active
        boolean is_verified
        timestamp created_at
        timestamp updated_at
    }

    %% Scenario System (PDF-to-Simulation Pipeline)
    scenarios {
        integer id PK
        string title
        text description
        text challenge
        string industry
        jsonb learning_objectives
        string source_type
        text pdf_content
        string student_role
        string category
        string difficulty_level
        integer estimated_duration
        jsonb tags
        string pdf_title
        string pdf_source
        string processing_version
        float rating_avg
        integer rating_count
        boolean is_public
        boolean is_template
        boolean allow_remixes
        integer usage_count
        integer clone_count
        integer created_by FK
        timestamp created_at
        timestamp updated_at
    }

    %% AI Persona System
    scenario_personas {
        integer id PK
        integer scenario_id FK
        string name
        string role
        text background
        text correlation
        jsonb primary_goals
        jsonb personality_traits
        timestamp created_at
        timestamp updated_at
    }

    %% Scene Progression System
    scenario_scenes {
        integer id PK
        integer scenario_id FK
        string title
        text description
        text user_goal
        integer scene_order
        integer estimated_duration
        integer max_attempts
        float success_threshold
        jsonb goal_criteria
        jsonb hint_triggers
        text scene_context
        jsonb persona_instructions
        string image_url
        string image_prompt
        timestamp created_at
        timestamp updated_at
    }

    %% Linear Simulation System
    user_progress {
        integer id PK
        integer user_id FK
        integer scenario_id FK
        integer current_scene_id FK
        string simulation_status
        jsonb scenes_completed
        integer total_attempts
        integer hints_used
        integer forced_progressions
        jsonb orchestrator_data
        float completion_percentage
        integer total_time_spent
        integer session_count
        float final_score
        timestamp started_at
        timestamp completed_at
        timestamp last_activity
        timestamp created_at
        timestamp updated_at
    }

    %% ChatOrchestrator Conversation System
    conversation_logs {
        integer id PK
        integer user_progress_id FK
        integer scene_id FK
        string message_type
        string sender_name
        integer persona_id FK
        text message_content
        integer message_order
        integer attempt_number
        boolean is_hint
        jsonb ai_context_used
        string ai_model_version
        float processing_time
        string user_reaction
        boolean led_to_progress
        timestamp timestamp
    }

    %% Community Review System
    scenario_reviews {
        integer id PK
        integer scenario_id FK
        integer reviewer_id FK
        integer rating
        text review_text
        jsonb pros
        jsonb cons
        string use_case
        integer helpful_votes
        integer total_votes
        timestamp created_at
    }

    %% Relationships
    users ||--o{ scenarios : creates
    users ||--o{ scenario_reviews : writes
    users ||--o{ user_progress : tracks

    scenarios ||--o{ scenario_personas : contains
    scenarios ||--o{ scenario_scenes : contains
    scenarios ||--o{ scenario_reviews : receives
    scenarios ||--o{ user_progress : simulates

    scenario_personas ||--o{ conversation_logs : speaks_as

    scenario_scenes ||--o{ conversation_logs : contains

    user_progress ||--o{ conversation_logs : records
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as FastAPI
    participant PR as PDF Router
    participant SR as Simulation Router
    participant CO as ChatOrchestrator
    participant LP as LlamaParse
    participant AI as OpenAI
    participant DB as PostgreSQL
    
    %% PDF Processing Flow
    U->>F: Upload PDF case study
    F->>A: POST /api/parse-pdf/upload
    A->>PR: Process PDF file
    PR->>LP: Extract text & structure
    LP-->>PR: Parsed content
    PR->>AI: Analyze business case (GPT-4o)
    AI-->>PR: Structured scenario data
    PR->>AI: Generate personas & scenes (GPT-4o)
    AI-->>PR: Key figures with personalities
    PR->>AI: Generate scene images (DALL-E 3)
    AI-->>PR: Professional scene images
    PR->>DB: Save scenario, personas, scenes
    DB-->>PR: Scenario created (ID: 123)
    PR-->>A: Processing complete
    A-->>F: Scenario ready for simulation
    F-->>U: Show generated scenario preview
    
    %% Simulation Execution Flow
    U->>F: Start simulation (scenario_id: 123)
    F->>A: POST /api/simulation/start
    A->>SR: Initialize simulation
    SR->>DB: Load scenario, personas, scenes
    DB-->>SR: Simulation data
    SR->>CO: Initialize ChatOrchestrator
    CO-->>SR: Simulation state ready
    SR-->>A: Simulation initialized
    A-->>F: Simulation ready
    
    U->>F: Send "begin"
    F->>A: POST /api/simulation/linear-chat
    A->>SR: Process chat message
    SR->>CO: Handle user input
    CO->>AI: Generate scene introduction
    AI-->>CO: Scene context & persona introduction
    CO->>DB: Save interaction to ConversationLog
    CO-->>SR: Rich scene description
    SR-->>A: Response ready
    A-->>F: Immersive scene presentation
    F-->>U: Continue conversation
    
    loop Scene Interaction
        U->>F: Chat with personas
        F->>A: POST /api/simulation/linear-chat
        A->>SR: Process chat message
        SR->>CO: Handle persona interaction
        CO->>AI: Generate persona responses
        AI-->>CO: AI persona interactions
        CO->>CO: Check scene completion
        CO->>DB: Update UserProgress state
        CO-->>SR: Interactive response
        SR-->>A: Response ready
        A-->>F: Continue conversation
        F-->>U: AI persona response
    end
    
    CO->>CO: Scene objectives achieved
    CO->>DB: Mark scene complete in UserProgress
    CO->>CO: Load next scene
    CO-->>SR: Scene transition
    SR-->>A: Next scene ready
    A-->>F: Scene transition
    F-->>U: Progress to next scene
```

## Technology Stack Architecture

```mermaid
graph TB
    subgraph "Frontend Technologies"
        NEXTJS[Next.js 15<br/>React Framework]
        TYPESCRIPT[TypeScript<br/>Type Safety]
        TAILWIND[Tailwind CSS<br/>Styling]
        SHADCN[shadcn/ui<br/>Component Library]
        LUCIDE[Lucide React<br/>Icons]
        REACT_HOOK_FORM[React Hook Form<br/>Form Management]
        ZOD[Zod<br/>Validation]
    end
    
    subgraph "Backend Technologies"
        FASTAPI_TECH[FastAPI<br/>Web Framework]
        PYTHON[Python 3.11+<br/>Programming Language]
        SQLALCHEMY[SQLAlchemy<br/>ORM]
        PYDANTIC[Pydantic<br/>Data Validation]
        ALEMBIC[Alembic<br/>Database Migrations]
        UVICORN[Uvicorn<br/>ASGI Server]
    end
    
    subgraph "AI/ML Technologies"
        CHAT_ORCHESTRATOR_TECH[ChatOrchestrator<br/>Simulation Engine]
        OPENAI_TECH[OpenAI GPT-4o<br/>Language Model]
        LLAMAPARSE_TECH[LlamaParse<br/>PDF Processing]
        LANGCHAIN[LangChain<br/>AI Framework]
        DALL_E_TECH[DALL-E 3<br/>Image Generation]
    end
    
    subgraph "Database & Storage"
        POSTGRES_TECH[PostgreSQL<br/>Primary Database]
        FILE_STORAGE_TECH[File Storage<br/>PDFs & Images]
        PGVECTOR[pgvector<br/>Vector Extensions]
    end
    
    subgraph "Core Modules"
        SESSION_MANAGER_TECH[Session Manager<br/>session_manager.py]
        SCENE_MEMORY_TECH[Scene Memory<br/>scene_memory.py]
        VECTOR_STORE_TECH[Vector Store<br/>vector_store.py]
        SIMULATION_ENGINE_TECH[Simulation Engine<br/>simulation_engine.py]
    end
    
    subgraph "DevOps & Infrastructure"
        PYTEST[Pytest<br/>Testing Framework]
        BLACK[Black<br/>Code Formatting]
        FLAKE8[Flake8<br/>Linting]
        STARTUP_CHECK[Startup Check<br/>Environment Validation]
    end
    
    %% Technology Connections
    NEXTJS --> FASTAPI_TECH
    TYPESCRIPT --> NEXTJS
    TAILWIND --> NEXTJS
    SHADCN --> NEXTJS
    LUCIDE --> NEXTJS
    REACT_HOOK_FORM --> NEXTJS
    ZOD --> REACT_HOOK_FORM
    
    FASTAPI_TECH --> PYTHON
    SQLALCHEMY --> POSTGRES_TECH
    PYDANTIC --> FASTAPI_TECH
    ALEMBIC --> SQLALCHEMY
    UVICORN --> FASTAPI_TECH
    
    CHAT_ORCHESTRATOR_TECH --> OPENAI_TECH
    LLAMAPARSE_TECH --> OPENAI_TECH
    LANGCHAIN --> OPENAI_TECH
    DALL_E_TECH --> OPENAI_TECH
    SIMULATION_ENGINE_TECH --> OPENAI_TECH
    
    FASTAPI_TECH --> POSTGRES_TECH
    FASTAPI_TECH --> FILE_STORAGE_TECH
    POSTGRES_TECH --> PGVECTOR
    
    SESSION_MANAGER_TECH --> CHAT_ORCHESTRATOR_TECH
    SCENE_MEMORY_TECH --> CHAT_ORCHESTRATOR_TECH
    VECTOR_STORE_TECH --> SIMULATION_ENGINE_TECH
    SIMULATION_ENGINE_TECH --> LANGCHAIN
```

## Security Architecture

```mermaid
graph TD
    subgraph "Authentication & Authorization"
        JWT[JWT Token System<br/>auth.py]
        RBAC[Role-Based Access<br/>require_admin]
        SESSION[Session Management<br/>get_current_user]
        API_SEC[API Security<br/>CORS Middleware]
    end
    
    subgraph "Data Protection"
        ENCRYPTION[Data Encryption<br/>SSL/TLS Connections]
        HASHING[Password Hashing<br/>bcrypt]
        VALIDATION[Input Validation<br/>Pydantic Schemas]
        PRIVACY[Privacy Controls<br/>User Data Protection]
    end
    
    subgraph "AI Service Security"
        API_KEYS[API Key Management<br/>Environment Variables]
        CONTENT_FILTER[Content Filtering<br/>OpenAI Safety]
        MONITORING[Usage Monitoring<br/>Logging]
        ERROR_HANDLING[Secure Error<br/>HTTPException]
    end
    
    subgraph "Infrastructure Security"
        HTTPS[HTTPS/TLS<br/>Encrypted Communication]
        CORS_SEC[CORS Protection<br/>FastAPI Middleware]
        STATIC_SEC[Static File Security<br/>/static endpoint]
        DB_SEC[Database Security<br/>Connection Pooling]
    end
    
    %% Security Flow
    JWT --> RBAC
    RBAC --> SESSION
    SESSION --> API_SEC
    
    ENCRYPTION --> HASHING
    HASHING --> VALIDATION
    VALIDATION --> PRIVACY
    
    API_KEYS --> CONTENT_FILTER
    CONTENT_FILTER --> MONITORING
    MONITORING --> ERROR_HANDLING
    
    HTTPS --> CORS_SEC
    CORS_SEC --> STATIC_SEC
    STATIC_SEC --> DB_SEC
```

## Performance & Scalability Architecture

```mermaid
graph TB
    subgraph "Performance Optimization"
        ASYNC[Async Processing<br/>FastAPI Async/Await]
        CONNECTION_POOL[Connection Pooling<br/>SQLAlchemy Pool]
        DB_OPT[Database Optimization<br/>Indexes & Queries]
        STATIC_SERVING[Static File Serving<br/>FastAPI StaticFiles]
    end
    
    subgraph "Scalability Features"
        STATELESS[Stateless Design<br/>JWT Authentication]
        MODULAR[Modular Architecture<br/>API Routers]
        ALEMBIC_MIGRATIONS[Database Migrations<br/>Alembic Versioning]
        ENV_CONFIG[Environment Configuration<br/>Settings Management]
    end
    
    subgraph "AI Service Management"
        API_KEY_MGMT[API Key Management<br/>Environment Variables]
        ERROR_HANDLING[Error Handling<br/>HTTPException]
        LOGGING[Logging<br/>Python Logging]
        STARTUP_VALIDATION[Startup Validation<br/>startup_check.py]
    end
    
    subgraph "Monitoring & Analytics"
        HEALTH[Health Endpoints<br/>/health endpoint]
        ROOT_ENDPOINT[Root Endpoint<br/>/ endpoint]
        DB_CONNECTION[Database Connection<br/>Connection Testing]
        ENV_LOGGING[Environment Logging<br/>Settings Display]
    end
    
    %% Performance Flow
    ASYNC --> CONNECTION_POOL
    CONNECTION_POOL --> DB_OPT
    DB_OPT --> STATIC_SERVING
    
    STATELESS --> MODULAR
    MODULAR --> ALEMBIC_MIGRATIONS
    ALEMBIC_MIGRATIONS --> ENV_CONFIG
    
    API_KEY_MGMT --> ERROR_HANDLING
    ERROR_HANDLING --> LOGGING
    LOGGING --> STARTUP_VALIDATION
    
    HEALTH --> ROOT_ENDPOINT
    ROOT_ENDPOINT --> DB_CONNECTION
    DB_CONNECTION --> ENV_LOGGING
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        LOCAL[Local Development<br/>Python Virtual Environment]
        DEV_SETUP[Development Setup<br/>setup_dev_environment.py]
        TEST_DB[Test Database<br/>PostgreSQL/SQLite]
        DEV_TOOLS[Development Tools<br/>Black, Flake8, Pytest]
    end
    
    subgraph "Environment Configuration"
        ENV_FILE[Environment File<br/>.env configuration]
        STARTUP_CHECK[Startup Validation<br/>startup_check.py]
        AUTO_SETUP[Auto Setup<br/>Environment Detection]
        DB_MIGRATIONS[Database Migrations<br/>Alembic Management]
    end
    
    subgraph "Application Deployment"
        FASTAPI_APP[FastAPI Application<br/>main.py]
        UVICORN_SERVER[Uvicorn Server<br/>ASGI Server]
        STATIC_FILES[Static Files<br/>/static endpoint]
        API_ROUTERS[API Routers<br/>Modular Endpoints]
    end
    
    subgraph "Database Deployment"
        POSTGRES_DB[PostgreSQL Database<br/>Primary Data Store]
        ALEMBIC_MIGRATIONS[Database Migrations<br/>Version Control]
        CONNECTION_POOL[Connection Pooling<br/>SQLAlchemy Pool]
        BACKUP_STRATEGY[Backup Strategy<br/>Database Backups]
    end
    
    %% Deployment Flow
    LOCAL --> DEV_SETUP
    DEV_SETUP --> ENV_FILE
    ENV_FILE --> STARTUP_CHECK
    STARTUP_CHECK --> AUTO_SETUP
    
    AUTO_SETUP --> FASTAPI_APP
    FASTAPI_APP --> UVICORN_SERVER
    UVICORN_SERVER --> STATIC_FILES
    STATIC_FILES --> API_ROUTERS
    
    API_ROUTERS --> POSTGRES_DB
    POSTGRES_DB --> ALEMBIC_MIGRATIONS
    ALEMBIC_MIGRATIONS --> CONNECTION_POOL
    CONNECTION_POOL --> BACKUP_STRATEGY
```

## Key Architecture Principles

### 1. **PDF-to-Simulation Pipeline**
- Intelligent document processing using LlamaParse and OpenAI GPT-4o
- Two-stage AI processing: persona extraction and scene generation
- Automated extraction of business scenarios, personas, and learning objectives
- DALL-E 3 integration for professional scene visualization
- Structured transformation into interactive simulation experiences

### 2. **Linear Simulation Design**
- Sequential scene progression with clear learning objectives
- ChatOrchestrator managing multi-persona interactions
- Scene state management with progress tracking
- Adaptive difficulty and hint systems for optimal learning

### 3. **AI-Powered Personas**
- Personality-based AI responses using trait scoring
- Context-aware interactions based on business scenarios
- Natural conversation flow with @mention capabilities
- LangChain integration for enhanced AI interactions

### 4. **Modular API Architecture**
- FastAPI with modular router design (/api/parse-pdf, /api/simulation, /api/scenarios)
- Pydantic schemas for data validation
- JWT-based authentication with role-based access control
- Comprehensive error handling and logging

### 5. **Database-First Design**
- PostgreSQL with Alembic migrations for version control
- Comprehensive data models for scenarios, personas, scenes, and progress
- JSONB fields for flexible data storage
- Connection pooling for performance optimization

### 6. **Development & Deployment**
- Environment-based configuration with startup validation
- Automated development setup with dependency management
- Static file serving for images and assets
- Health monitoring and system status endpoints

### 7. **Security & Privacy**
- JWT-based authentication with role-based access control
- Secure API key management through environment variables
- Input validation and sanitization
- Secure AI service integration with content filtering

This architecture provides a robust, scalable, and secure foundation for transforming traditional business case studies into engaging, interactive learning experiences through AI-powered simulations.
