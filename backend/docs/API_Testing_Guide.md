# 🚀 CrewAI Backend API Testing Guide

## 📋 Prerequisites

1. **Virtual Environment Activated**
   ```powershell
   venv\Scripts\Activate
   ```

2. **Server Running**
   ```powershell
   python simple_main.py
   ```

3. **Environment Variables Set** (create `.env` file if missing)
   ```env
   DATABASE_URL=your_database_url
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   SECRET_KEY=your_secret_key
   ```

## 🔧 Step-by-Step Testing Workflow

### Step 1: Health Check
**Test if server is running**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/"
Invoke-WebRequest -Uri "http://localhost:8000/health/"
```

**Expected Response:**
```json
{"message": "CrewAI Education Platform - Simple & Effective"}
{"status": "healthy", "framework": "CrewAI", "approach": "simple"}
```

### Step 2: Create a Business Scenario
**Endpoint:** `POST /scenarios/`

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/scenarios/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"title": "Eco-Friendly Startup Launch", "description": "Launch a new SaaS product in a competitive market", "industry": "Technology", "challenge": "How to compete with established players while building market share", "learning_objectives": ["Market analysis", "Financial planning", "Product strategy"]}'
```

**Expected Response:**
```json
{
  "id": 1,
  "title": "Tech Startup Launch",
  "description": "Launch a new SaaS product in a competitive market",
  "industry": "Technology",
  "challenge": "How to compete with established players while building market share",
  "learning_objectives": ["Market analysis", "Financial planning", "Product strategy"],
  "created_by": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Step 3: Get All Scenarios
**Endpoint:** `GET /scenarios/`

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/scenarios/"
```

### Step 4: Start a Simulation
**Endpoint:** `POST /simulations/`

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/simulations/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"scenario_id": 5}'
```

**Expected Response:**
```json
{
  "simulation_id": 1,
  "scenario": {...},
  "status": "ready",
  "message": "Simulation started! Send your first message to interact with the crew."
}
```

### Step 5: Chat with CrewAI Team
**Endpoint:** `POST /simulations/{simulation_id}/chat/`

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/simulations/1/chat/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"message": "We need to launch our SaaS product. What should our go-to-market strategy be?"}'
```

**What Happens:**
- Marketing Agent analyzes market conditions
- Finance Agent creates budget projections
- Product Agent defines product strategy
- Operations Agent plans operational requirements

### Step 6: Get Conversation History
**Endpoint:** `GET /simulations/{simulation_id}/history/`

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/simulations/1/history/"
```

### Step 7: Complete Simulation
**Endpoint:** `POST /simulations/{simulation_id}/complete/`

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/simulations/1/complete/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{}'
```

## 🎯 Example Learning Scenarios

### Scenario 1: Restaurant Chain Expansion
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/scenarios/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"title": "Restaurant Chain Expansion", "description": "Expand a successful local restaurant to multiple locations", "industry": "Food & Beverage", "challenge": "Scaling operations while maintaining quality and brand consistency", "learning_objectives": ["Expansion strategy", "Operations scaling", "Brand management"]}'
```

**Questions to Ask:**
- "Should we expand to new cities or increase density in current markets?"
- "What's our optimal budget allocation across marketing, operations, and growth?"
- "How should we adapt our menu for different regional preferences?"

### Scenario 2: E-commerce Platform Launch
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/scenarios/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"title": "E-commerce Platform Launch", "description": "Launch a new online marketplace connecting local businesses with customers", "industry": "E-commerce", "challenge": "Building two-sided marketplace with sellers and buyers", "learning_objectives": ["Platform strategy", "Network effects", "Revenue models"]}'
```

**Questions to Ask:**
- "How do we solve the chicken-and-egg problem of getting both sellers and buyers?"
- "What commission structure would attract sellers while ensuring profitability?"
- "Should we focus on specific product categories or be a general marketplace?"

### Scenario 3: Clean Energy Startup
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/scenarios/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"title": "Solar Energy Startup", "description": "Develop and sell residential solar panel systems", "industry": "Clean Energy", "challenge": "High upfront costs and long sales cycles", "learning_objectives": ["Financing models", "Customer acquisition", "Regulatory compliance"]}'
```

**Questions to Ask:**
- "What financing options should we offer to make solar affordable?"
- "How do we navigate different state regulations and incentives?"
- "Should we focus on direct sales or partner with installers?"

## 🛠 Troubleshooting

### Server Not Responding
```powershell
# Check if server is running
Get-Process | Where-Object {$_.ProcessName -eq "python"}

# Check port usage
netstat -ano | findstr :8000

# Restart server
python simple_main.py
```

### Internal Server Error (500)
1. **Check environment variables** in `.env` file
2. **Check database connection**
3. **Check server logs** in the terminal where server is running
4. **Restart server** after fixing issues

### Database Issues
```powershell
# Check database connection in the server logs
# Look for lines starting with "🔗 Database URL:" when server starts
```

### Missing Dependencies
```powershell
# Reinstall in virtual environment
pip install -r simple_requirements.txt
```

## 📊 Response Status Codes

- **200**: Success ✅
- **404**: Not Found (scenario/simulation doesn't exist)
- **422**: Validation Error (check your JSON format)
- **500**: Internal Server Error (check server logs)

## 🎓 Educational Usage Tips

1. **Start Simple**: Create basic scenarios first
2. **Ask Follow-ups**: Continue conversations to explore different aspects
3. **Compare Responses**: Ask the same question to different scenarios
4. **Explore Trade-offs**: Ask about different strategic options
5. **Focus on Learning**: Use the crew responses to understand business concepts

## 🔄 Complete Example Workflow

```powershell
# 1. Health check
Invoke-WebRequest -Uri "http://localhost:8000/health/"

# 2. Create scenario
Invoke-WebRequest -Uri "http://localhost:8000/scenarios/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"title": "Food Truck Business", "description": "Start a gourmet food truck in downtown area", "industry": "Food Service", "challenge": "Limited capital and high competition", "learning_objectives": ["Location strategy", "Cost management", "Menu optimization"]}'

# 3. Start simulation (use the ID from step 2 response)
Invoke-WebRequest -Uri "http://localhost:8000/simulations/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"scenario_id": 1}'

# 4. Chat with team (use simulation_id from step 3)
Invoke-WebRequest -Uri "http://localhost:8000/simulations/1/chat/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"message": "What location should we choose for our food truck and why?"}'

# 5. Continue conversation
Invoke-WebRequest -Uri "http://localhost:8000/simulations/1/chat/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"message": "How should we price our menu items to be competitive but profitable?"}'

# 6. View history
Invoke-WebRequest -Uri "http://localhost:8000/simulations/1/history/"

# 7. Complete simulation
Invoke-WebRequest -Uri "http://localhost:8000/simulations/1/complete/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{}'
```

---

**💡 Pro Tip**: Use a REST client (like Postman, Insomnia, or VS Code REST Client) for easier testing instead of PowerShell commands! 