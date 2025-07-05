# 🚀 Simple CrewAI Education Platform

This is a **drastically simplified** version of the backend, following CrewAI best practices for **"Low Complexity, Low Precision"** use cases.

## 🎯 **What Changed**

### **❌ Removed (Over-engineered)**
- Multi-framework orchestration (LangGraph, AutoGen)
- Complex crew configurations and database models
- Tool manager service
- 50+ database tables
- Abstract orchestration layers

### **✅ Added (Simple & Effective)**
- Direct CrewAI crews following the [official pattern](https://docs.crewai.com/en)
- YAML-based configuration (like your working `basicAgents` project)
- Simple database models (4 tables instead of 15+)
- Direct crew execution without orchestration layers

## 🏗️ **New Architecture**

```
Simple FastAPI Backend
├── simple_models.py          # 4 simple database tables
├── simple_main.py            # Clean FastAPI endpoints
├── crews/
│   ├── business_crew.py      # Business simulation crew
│   └── config/
│       ├── business_agents.yaml    # Agent configurations
│       └── business_tasks.yaml     # Task configurations
└── simple_requirements.txt   # Minimal dependencies
```

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
cd backend
pip install -r simple_requirements.txt
```

### **2. Set Environment Variables**
```bash
# Create .env file
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/ai_education
```

### **3. Run the Backend**
```bash
python simple_main.py
```

### **4. Test the API**
```bash
# Health check
curl http://localhost:8000/health/

# Create a scenario
curl -X POST http://localhost:8000/scenarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "EcoFriendly Startup",
    "description": "Launch a sustainable products company",
    "industry": "Environmental",
    "challenge": "How to build a profitable green business?",
    "learning_objectives": ["Market analysis", "Financial planning"]
  }'

# Start a simulation
curl -X POST http://localhost:8000/simulations/ \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": 1, "user_id": 1}'

# Chat with the crew
curl -X POST http://localhost:8000/simulations/1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to launch an eco-friendly phone case business. What should I consider?"}'
```

## 📊 **API Endpoints**

### **Scenarios**
- `POST /scenarios/` - Create new scenario
- `GET /scenarios/` - List all scenarios
- `GET /scenarios/{id}` - Get specific scenario

### **Simulations**
- `POST /simulations/` - Start new simulation
- `POST /simulations/{id}/chat/` - Chat with crew
- `GET /simulations/{id}/history/` - Get conversation history
- `POST /simulations/{id}/complete/` - Mark as completed

### **Health**
- `GET /health/` - Health check

## 🎓 **How It Works**

1. **Teacher creates scenario** via `/scenarios/`
2. **Student starts simulation** via `/simulations/`
3. **Student chats with crew** via `/simulations/{id}/chat/`
4. **Crew responds collaboratively** using CrewAI's sequential process:
   - Marketing Agent analyzes market
   - Finance Agent creates budget
   - Product Agent designs strategy
   - Operations Agent plans execution

## 💡 **Benefits of This Approach**

### **Educational**
- Students see **real business collaboration**
- **Sequential decision-making** mirrors real companies
- **Cross-functional learning** (Marketing → Finance → Product → Operations)

### **Technical**
- **90% less code** than the complex version
- **Follows CrewAI best practices** from the [official docs](https://docs.crewai.com/en)
- **Easy to debug and maintain**
- **Faster development cycle**

## 🔧 **Customization**

### **Add New Scenarios**
Just modify the YAML configs in `crews/config/`:
- `business_agents.yaml` - Agent personalities
- `business_tasks.yaml` - Task descriptions

### **Add New Crew Types**
Create new crew classes following the same pattern as `BusinessCrew`

### **Add Tools**
Add CrewAI tools to agents:
```python
tools=[SerperDevTool(), YourCustomTool()]
```

## 📈 **Next Steps**

1. **Test this simple version** with students
2. **Gather feedback** on educational effectiveness
3. **Gradually add complexity** only when needed
4. **Scale up** using CrewAI Flows when you reach higher complexity

## 🎯 **Success Metrics**

- **Educational**: Students understand business collaboration
- **Technical**: 90% reduction in code complexity
- **Development**: Faster feature iteration
- **Reliability**: Fewer bugs, easier debugging

---

**This approach follows the CrewAI docs recommendation for your use case: Start simple, scale gradually! 🚀** 