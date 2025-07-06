# Database Schema

This Entity Relationship Diagram (ERD) shows the complete database schema for the CrewAI Agent Builder Platform, including all tables, fields, and relationships.

## Core Tables

### User Management
- **User**: Platform users with profiles, reputation, and community stats

### Content Creation
- **Agent**: AI agents with marketplace features (public sharing, ratings, versions)
- **Tool**: Custom tools and integrations with verification system
- **Task**: Task definitions that can be assigned to agents
- **Scenario**: Business scenarios that combine agents and tasks

### Simulation & Execution
- **Simulation**: CrewAI simulation sessions with configuration and results
- **SimulationMessage**: Chat messages during simulation execution

### Community Features
- **AgentReview**: User reviews and ratings for agents
- **ToolReview**: User reviews and ratings for tools
- **Collection**: Curated collections of agents, tools, and scenarios

### Templates & AI Suggestions
- **AgentTemplate**: Pre-built agent templates for AI suggestions
- **TaskTemplate**: Pre-built task templates for AI suggestions

## Key Relationships

### One-to-Many
- Users create multiple agents, tools, tasks, scenarios
- Agents receive multiple reviews
- Scenarios are used in multiple simulations

### Many-to-Many (via Junction Tables)
- Scenarios ↔ Agents (scenario_agents)
- Scenarios ↔ Tasks (scenario_tasks)  
- Users ↔ Favorite Agents (user_favorite_agents)
- Users ↔ Favorite Tools (user_favorite_tools)

### Self-Referential
- Agents can be remixed from other agents (original_agent_id)
- Tools can be forked from other tools (original_tool_id)

```mermaid
erDiagram
    User {
        int id PK
        string email UK
        string full_name
        string username UK
        text bio
        string avatar_url
        string role
        int public_agents_count
        int public_tools_count
        int total_downloads
        float reputation_score
        boolean profile_public
        boolean allow_contact
        datetime created_at
    }
    
    Agent {
        int id PK
        string name
        string role
        text goal
        text backstory
        json tools
        boolean verbose
        boolean allow_delegation
        boolean reasoning
        string category
        json tags
        boolean is_public
        boolean is_template
        boolean allow_remixes
        int original_agent_id FK
        int usage_count
        int clone_count
        float average_rating
        int rating_count
        string version
        text version_notes
        int created_by FK
        datetime created_at
        datetime updated_at
    }
    
    Tool {
        int id PK
        string name
        text description
        string tool_type
        json configuration
        json required_credentials
        text usage_instructions
        text code
        json requirements
        string category
        json tags
        boolean is_public
        boolean is_verified
        boolean allow_remixes
        int original_tool_id FK
        int usage_count
        int clone_count
        float average_rating
        int rating_count
        string version
        text version_notes
        int created_by FK
        datetime created_at
        datetime updated_at
    }
    
    Task {
        int id PK
        string title
        text description
        text expected_output
        json tools
        json context
        int agent_id FK
        string category
        json tags
        boolean is_public
        boolean is_template
        boolean allow_remixes
        int usage_count
        int clone_count
        int created_by FK
        datetime created_at
        datetime updated_at
    }
    
    Scenario {
        int id PK
        string title
        text description
        text challenge
        string industry
        json learning_objectives
        string source_type
        text pdf_content
        boolean is_public
        boolean is_template
        boolean allow_remixes
        int usage_count
        int clone_count
        int created_by FK
        datetime created_at
        datetime updated_at
    }
    
    Simulation {
        int id PK
        int scenario_id FK
        int user_id FK
        json crew_configuration
        string process_type
        string status
        text crew_output
        json execution_log
        json error_details
        json missing_agents
        json missing_tasks
        boolean fallback_used
        boolean is_public
        boolean allow_sharing
        datetime started_at
        datetime completed_at
    }
    
    SimulationFallback {
        int id PK
        int scenario_id FK
        json fallback_agents
        json fallback_tasks
        string fallback_strategy
        int created_by FK
        datetime created_at
        datetime updated_at
    }
    
    AgentReview {
        int id PK
        int agent_id FK
        int reviewer_id FK
        int rating
        text review_text
        json pros
        json cons
        string use_case
        int helpful_votes
        int total_votes
        datetime created_at
    }
    
    ToolReview {
        int id PK
        int tool_id FK
        int reviewer_id FK
        int rating
        text review_text
        json pros
        json cons
        string use_case
        int helpful_votes
        int total_votes
        datetime created_at
    }
    
    Collection {
        int id PK
        string name
        text description
        json agents
        json tools
        json scenarios
        boolean is_public
        json tags
        int created_by FK
        datetime created_at
        datetime updated_at
    }
    
    %% Relationships
    User ||--o{ Agent : creates
    User ||--o{ Tool : creates
    User ||--o{ Task : creates
    User ||--o{ Scenario : creates
    User ||--o{ Simulation : runs
    User ||--o{ Collection : curates
    User ||--o{ AgentReview : writes
    User ||--o{ ToolReview : writes
    
    Agent ||--o{ Task : "assigned to"
    Agent ||--o{ AgentReview : "receives"
    Agent ||--o{ Agent : "remixed from"
    
    Tool ||--o{ ToolReview : "receives"
    Tool ||--o{ Tool : "remixed from"
    
    Scenario ||--o{ Simulation : "used in"
    Scenario ||--o{ SimulationFallback : "has fallbacks"
    
    Simulation ||--o{ SimulationMessage : contains
    
    %% Many-to-many relationships (through junction tables)
    Scenario }|--|{ Agent : "scenario_agents"
    Scenario }|--|{ Task : "scenario_tasks"
    Simulation }|--|{ Agent : "simulation_agents"
    Simulation }|--|{ Task : "simulation_tasks"
    User }|--|{ Agent : "user_favorite_agents"
    User }|--|{ Tool : "user_favorite_tools"
```

## Database Features

### Marketplace Features
- **Public Sharing**: `is_public` flags allow content to be shared
- **Version Control**: Track versions and changes with `version` and `version_notes`
- **Attribution**: `original_agent_id` and `original_tool_id` track remixes
- **Community Metrics**: Usage counts, ratings, and review systems

### Content Organization
- **Categories**: Organize agents and tools by type
- **Tags**: Flexible tagging system for discovery
- **Collections**: User-curated bundles of related content

### User Experience
- **Favorites**: Users can save preferred agents and tools
- **Reputation**: Track user contributions and community impact
- **Reviews**: Detailed feedback system with pros/cons and helpful votes

### AI Features
- **Templates**: Pre-built templates for AI-powered suggestions
- **PDF Processing**: Store original PDF content for scenario creation
- **Execution Logs**: Detailed simulation tracking and debugging

### Graceful Error Handling
- **Resource Tracking**: Junction tables link simulations to actual agents/tasks used
- **Snapshot Storage**: Store agent/task configurations at time of execution
- **Missing Resource Detection**: Track which agents/tasks became unavailable
- **Fallback Strategies**: Automatic substitution with public alternatives
- **Error Transparency**: Detailed error logs and missing resource lists
- **Status Granularity**: Extended status codes for different failure types

## Simulation Resource Management

### The Problem
When a user publishes a public scenario, other users should be able to run it even if:
- Original agents/tasks are made private
- Original agents/tasks are deleted
- Original creator removes access

### The Solution
1. **Execution Snapshots**: Store full agent/task configuration when simulation starts
2. **Junction Tables**: Track which specific database records were used
3. **Fallback System**: Automatically substitute unavailable resources with public alternatives
4. **Transparent Errors**: Clear messaging about what resources were unavailable
5. **Graceful Degradation**: Simulation continues with available resources when possible

### Fallback Strategies
- **substitute**: Replace missing agents/tasks with public alternatives
- **skip**: Skip missing components and continue with available ones  
- **fail**: Stop execution and report missing resources

### Status Codes
- **created**: Simulation configured, ready to run
- **running**: Currently executing
- **completed**: Successfully completed with all resources
- **failed**: Technical failure during execution
- **failed_missing_resources**: Failed due to unavailable agents/tasks 