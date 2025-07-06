# CrewAI Agent Builder Platform - Complete API Reference

## Overview

The CrewAI Agent Builder Platform provides a comprehensive REST API for managing users, AI agents, business scenarios, and simulations. This API enables developers to build powerful applications on top of our community-driven platform.

**Base URL:** `http://localhost:8000`
**API Version:** 2.0.0
**Authentication:** JWT Bearer tokens

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Agent Management](#agent-management)
4. [Scenario Management](#scenario-management)
5. [Simulation Management](#simulation-management)
6. [System Endpoints](#system-endpoints)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## Authentication

### Overview
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the `Authorization` header for protected endpoints.

**Header Format:**
```
Authorization: Bearer <jwt_token>
```

### User Registration

**`POST /users/register`**

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "password": "securepassword123",
  "bio": "AI enthusiast and educator",
  "avatar_url": "https://example.com/avatar.jpg",
  "profile_public": true,
  "allow_contact": true
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "bio": "AI enthusiast and educator",
  "avatar_url": "https://example.com/avatar.jpg",
  "role": "user",
  "public_agents_count": 0,
  "public_tools_count": 0,
  "total_downloads": 0,
  "reputation_score": 0.0,
  "profile_public": true,
  "allow_contact": true,
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-01-06T12:00:00Z",
  "updated_at": "2025-01-06T12:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `400` - Email already registered or username taken
- `422` - Validation error

### User Login

**`POST /users/login`**

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "username": "johndoe",
    "role": "user"
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid credentials
- `400` - Account deactivated

---

## User Management

### Get Current User Profile

**`GET /users/me`** 🔒

Get the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "bio": "AI enthusiast and educator",
  "role": "user",
  "public_agents_count": 5,
  "total_downloads": 150,
  "reputation_score": 4.2,
  "profile_public": true,
  "created_at": "2025-01-06T12:00:00Z"
}
```

### Update Current User Profile

**`PUT /users/me`** 🔒

Update the authenticated user's profile.

**Request Body:**
```json
{
  "full_name": "John Smith",
  "bio": "Updated bio",
  "profile_public": false
}
```

### Change Password

**`POST /users/me/change-password`** 🔒

Change the authenticated user's password.

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

### Get User Profile (Public)

**`GET /users/{user_id}`**

Get a user's public profile information.

**Parameters:**
- `user_id` (integer) - User ID

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "full_name": "John Doe",
  "bio": "AI enthusiast and educator",
  "public_agents_count": 5,
  "reputation_score": 4.2,
  "created_at": "2025-01-06T12:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `403` - Private profile (not accessible)
- `404` - User not found

### Get All Users (Admin Only)

**`GET /users/`** 🔒👑

Get list of all users (admin access required).

**Query Parameters:**
- `skip` (integer, optional) - Number of records to skip (default: 0)
- `limit` (integer, optional) - Number of records to return (default: 100)

---

## Agent Management

### Create Agent

**`POST /agents/`**

Create a new AI agent.

**Request Body:**
```json
{
  "name": "Marketing Specialist",
  "role": "Senior Marketing Analyst",
  "goal": "Analyze market trends and create comprehensive marketing strategies",
  "backstory": "An expert in digital marketing with 10+ years of experience...",
  "tools": ["web_search", "data_analysis", "report_generator"],
  "verbose": true,
  "allow_delegation": false,
  "reasoning": true,
  "category": "business",
  "tags": ["marketing", "analysis", "strategy"],
  "is_public": true,
  "is_template": false,
  "allow_remixes": true,
  "version": "1.0.0",
  "version_notes": "Initial release",
  "created_by": 1
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Marketing Specialist",
  "role": "Senior Marketing Analyst",
  "goal": "Analyze market trends and create comprehensive marketing strategies",
  "backstory": "An expert in digital marketing...",
  "tools": ["web_search", "data_analysis", "report_generator"],
  "verbose": true,
  "allow_delegation": false,
  "reasoning": true,
  "category": "business",
  "tags": ["marketing", "analysis", "strategy"],
  "is_public": true,
  "usage_count": 0,
  "clone_count": 0,
  "average_rating": 0.0,
  "rating_count": 0,
  "version": "1.0.0",
  "created_by": 1,
  "created_at": "2025-01-06T12:00:00Z",
  "updated_at": "2025-01-06T12:00:00Z"
}
```

### Get All Agents

**`GET /agents/`**

Get list of all available agents.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Marketing Specialist",
    "role": "Senior Marketing Analyst",
    "category": "business",
    "tags": ["marketing", "analysis"],
    "is_public": true,
    "usage_count": 25,
    "average_rating": 4.5,
    "created_at": "2025-01-06T12:00:00Z"
  }
]
```

### Get Agent by ID

**`GET /agents/{agent_id}`**

Get detailed information about a specific agent.

**Parameters:**
- `agent_id` (integer) - Agent ID

### Update Agent

**`PUT /agents/{agent_id}`** 🔒

Update an existing agent (owner or admin only).

**Request Body:**
```json
{
  "name": "Updated Marketing Specialist",
  "tools": ["web_search", "data_analysis", "report_generator", "social_media"]
}
```

### Delete Agent

**`DELETE /agents/{agent_id}`** 🔒

Delete an agent (owner or admin only).

**Response:**
```json
{
  "message": "Agent deleted successfully"
}
```

### Get User's Agents

**`GET /agents/user/{user_id}`**

Get all agents created by a specific user.

---

## Scenario Management

### Create Scenario

**`POST /scenarios/`**

Create a new business scenario.

**Request Body:**
```json
{
  "title": "E-commerce Platform Launch",
  "description": "Launch a new e-commerce platform in competitive market",
  "industry": "Technology",
  "challenge": "Compete with established players while building customer trust",
  "learning_objectives": [
    "Market analysis and positioning",
    "Customer acquisition strategies",
    "Technology stack decisions"
  ],
  "source_type": "manual",
  "pdf_content": null,
  "is_public": true,
  "is_template": false,
  "allow_remixes": true,
  "created_by": 1
}
```

**Response:**
```json
{
  "id": 1,
  "title": "E-commerce Platform Launch",
  "description": "Launch a new e-commerce platform...",
  "industry": "Technology",
  "challenge": "Compete with established players...",
  "learning_objectives": [
    "Market analysis and positioning",
    "Customer acquisition strategies",
    "Technology stack decisions"
  ],
  "source_type": "manual",
  "is_public": true,
  "usage_count": 0,
  "clone_count": 0,
  "created_by": 1,
  "created_at": "2025-01-06T12:00:00Z"
}
```

### Get All Scenarios

**`GET /scenarios/`**

Get list of all available scenarios.

### Get Scenario by ID

**`GET /scenarios/{scenario_id}`**

Get detailed information about a specific scenario.

---

## Simulation Management

### Start Simulation

**`POST /simulations/`**

Start a new CrewAI simulation with a specific scenario.

**Request Body:**
```json
{
  "scenario_id": 1,
  "user_id": 1,
  "crew_configuration": {
    "process": "sequential"
  },
  "process_type": "sequential"
}
```

**Response:**
```json
{
  "simulation_id": 1,
  "scenario": {
    "id": 1,
    "title": "E-commerce Platform Launch",
    "description": "Launch a new e-commerce platform...",
    "industry": "Technology",
    "challenge": "Compete with established players..."
  },
  "status": "ready",
  "message": "Simulation started! Send your first message to interact with the crew."
}
```

### Chat with Crew

**`POST /simulations/{simulation_id}/chat/`**

Send a message to the AI crew and receive responses.

**Parameters:**
- `simulation_id` (integer) - Simulation ID

**Request Body:**
```json
{
  "message": "What should be our first step in market analysis?"
}
```

**Response:**
```json
{
  "simulation_id": 1,
  "user_message": "What should be our first step in market analysis?",
  "crew_response": "Based on the e-commerce platform launch scenario, I recommend starting with competitive analysis. We should identify the top 5 competitors, analyze their pricing strategies, user experience, and market positioning...",
  "timestamp": "2025-01-06T12:30:00Z"
}
```

**Status Codes:**
- `200` - Success
- `400` - Simulation not active
- `404` - Simulation not found

### Get Simulation History

**`GET /simulations/{simulation_id}/history/`**

Get the complete conversation history for a simulation.

**Response:**
```json
{
  "simulation_id": 1,
  "scenario": {
    "id": 1,
    "title": "E-commerce Platform Launch",
    "description": "Launch a new e-commerce platform..."
  },
  "messages": [
    {
      "id": 1,
      "user_message": "What should be our first step?",
      "crew_response": "Based on the scenario, I recommend...",
      "timestamp": "2025-01-06T12:30:00Z"
    }
  ],
  "status": "running"
}
```

### Complete Simulation

**`POST /simulations/{simulation_id}/complete/`**

Mark a simulation as completed.

**Response:**
```json
{
  "message": "Simulation completed successfully"
}
```

---

## System Endpoints

### Health Check

**`GET /health/`**

Check the system health and status.

**Response:**
```json
{
  "status": "healthy",
  "framework": "CrewAI",
  "platform": "Agent Builder Community",
  "version": "2.0.0"
}
```

### Root Endpoint

**`GET /`**

Get basic API information.

**Response:**
```json
{
  "message": "CrewAI Agent Builder Platform - Build, Share, Simulate",
  "version": "2.0.0"
}
```

---

## Error Handling

### Standard Error Response Format

All API errors follow a consistent format:

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

### Common HTTP Status Codes

- **200** - Success
- **201** - Created
- **400** - Bad Request (validation error, business logic error)
- **401** - Unauthorized (authentication required)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **422** - Unprocessable Entity (request format error)
- **500** - Internal Server Error

### Error Examples

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Could not validate credentials",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

**Permission Error (403):**
```json
{
  "detail": "Not enough permissions"
}
```

---

## Rate Limiting

### Default Limits
- **Authentication endpoints:** 5 requests per minute per IP
- **General API endpoints:** 100 requests per minute per user
- **Simulation endpoints:** 10 concurrent simulations per user

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1625097600
```

---

## SDKs and Integration

### Python SDK Example

```python
import requests

class CrewAIClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def login(self, email, password):
        response = self.session.post(
            f'{self.base_url}/users/login',
            json={'email': email, 'password': password}
        )
        data = response.json()
        self.token = data['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
        return data
    
    def create_agent(self, agent_data):
        return self.session.post(
            f'{self.base_url}/agents/',
            json=agent_data
        ).json()
    
    def start_simulation(self, scenario_id, user_id=None):
        return self.session.post(
            f'{self.base_url}/simulations/',
            json={
                'scenario_id': scenario_id,
                'user_id': user_id,
                'crew_configuration': {'process': 'sequential'},
                'process_type': 'sequential'
            }
        ).json()

# Usage
client = CrewAIClient('http://localhost:8000')
client.login('user@example.com', 'password')
simulation = client.start_simulation(scenario_id=1)
```

### JavaScript/Node.js Example

```javascript
class CrewAIClient {
  constructor(baseUrl, token = null) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers
    };

    const response = await fetch(url, { ...options, headers });
    return response.json();
  }

  async login(email, password) {
    const data = await this.request('/users/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    this.token = data.access_token;
    return data;
  }

  async createAgent(agentData) {
    return this.request('/agents/', {
      method: 'POST',
      body: JSON.stringify(agentData)
    });
  }

  async startSimulation(scenarioId, userId = null) {
    return this.request('/simulations/', {
      method: 'POST',
      body: JSON.stringify({
        scenario_id: scenarioId,
        user_id: userId,
        crew_configuration: { process: 'sequential' },
        process_type: 'sequential'
      })
    });
  }
}

// Usage
const client = new CrewAIClient('http://localhost:8000');
await client.login('user@example.com', 'password');
const simulation = await client.startSimulation(1);
```

---

## Webhooks (Coming Soon)

Future versions will support webhooks for real-time notifications:

- `simulation.completed` - When a simulation finishes
- `agent.shared` - When an agent is made public
- `user.verified` - When a user verifies their email

---

## API Versioning

The API uses URL-based versioning. Current version is `v2` (default).

Future versions will be available at:
- `http://localhost:8000/v2/` (current)
- `http://localhost:8000/v3/` (future)

---

## Support

For API support and questions:
- **Documentation:** [GitHub Repository](https://github.com/your-repo)
- **Issues:** Create an issue on GitHub
- **Community:** Join our Discord server

---

**Legend:**
- 🔒 = Authentication required
- 👑 = Admin access required 