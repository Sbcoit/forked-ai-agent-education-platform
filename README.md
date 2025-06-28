# 🎓 AI Agent Education Platform

An innovative educational platform that allows teachers to create business simulations with AI agents, helping students learn through interactive scenarios. Inspired by modern AI-driven education and built with cutting-edge technology.

![AI Agent Education Platform](https://img.shields.io/badge/AI-Education-blue?style=for-the-badge)
![React](https://img.shields.io/badge/React-TypeScript-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql)

## 🌟 Features

### 📋 **Scenario Management**
- **Pre-defined Business Scenarios**: Ready-to-use scenarios like EcoFriendly Product Launch, Healthcare Innovation, FinTech Startup
- **PDF Case Study Upload**: Upload Harvard Business Review cases or custom PDFs for AI analysis
- **Custom Scenario Creation**: Build your own business challenges with learning objectives

### 🤖 **AI Agent Creation**
- **Intelligent Agent Design**: Create AI agents with unique personalities and expertise
- **Role-Based Specialists**: Marketing, Finance, Product, Operations experts
- **Customizable Personalities**: Define communication styles, responsibilities, and decision-making criteria
- **Real-time Agent Configuration**: Interactive forms with live preview

### 🎮 **Interactive Simulations**
- **Live Business Simulations**: Students interact with AI agents in real-time
- **Multi-Agent Collaboration**: Agents work together to solve business challenges
- **Progress Tracking**: Monitor student decisions and learning outcomes
- **Dynamic Scenarios**: Adaptive storylines based on student choices

### 🎨 **Modern UI/UX**
- **n-aible Design System**: Professional, clean interface inspired by modern AI companies
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Accessibility First**: WCAG compliant with keyboard navigation support
- **Dark/Light Mode**: Adaptive interface for different preferences

## 🏗️ Architecture

```mermaid
graph TB
    A[React Frontend] --> B[FastAPI Backend]
    B --> C[PostgreSQL Database]
    B --> D[OpenAI API]
    B --> E[Anthropic Claude API]
    B --> F[PDF Processing Service]
    
    subgraph "Frontend (React + TypeScript)"
        G[Scenario Builder]
        H[Agent Creator]
        I[Simulation Runner]
        J[Real-time Chat]
    end
    
    subgraph "Backend (FastAPI + Python)"
        K[REST API]
        L[AI Service Layer]
        M[Simulation Engine]
        N[PDF Processor]
    end
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (3.9 or higher)
- **PostgreSQL** (v12 or higher)
- **OpenAI API Key** (for AI agent functionality)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-agent-education-platform.git
cd ai-agent-education-platform
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_template.txt .env
# Edit .env with your database and API keys

# Create database tables
python recreate_db.py

# Create default scenarios
python create_default_scenarios.py

# Start the backend server
python main.py
```

The backend will be available at **http://localhost:8000**

### 3. Frontend Setup
```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at **http://localhost:3000**

## 🔧 Environment Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql://username:password@localhost:5432/ai_education
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SECRET_KEY=your_secret_key_here
ENVIRONMENT=development
```

### Database Setup
1. Create a PostgreSQL database
2. Update the `DATABASE_URL` in your `.env` file
3. Run the database setup scripts

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Key Endpoints
```
GET  /scenarios/              # List all scenarios
POST /scenarios/              # Create new scenario
POST /scenarios/upload-pdf/   # Upload PDF case study
GET  /scenarios/{id}/agents/  # Get agents for scenario
POST /agents/                 # Create new agent
POST /simulations/            # Start simulation
POST /simulations/{id}/interact/  # Chat with agents
```

## 🎓 Usage Guide

### For Teachers

1. **Create/Select Scenario**
   - Choose from pre-built scenarios
   - Upload your own PDF case studies
   - Build custom business challenges

2. **Design AI Agents**
   - Configure agent personalities
   - Set expertise areas and responsibilities
   - Define decision-making criteria

3. **Launch Simulation**
   - Students interact with AI agents
   - Monitor progress and decisions
   - Review learning outcomes

### For Students

1. **Join Simulation**
   - Access scenario overview
   - Understand business challenge
   - Review learning objectives

2. **Interact with Agents**
   - Chat with AI specialists
   - Make business decisions
   - Collaborate on solutions

3. **Learn and Reflect**
   - Receive real-time feedback
   - See decision impacts
   - Complete learning assessments

## 🛠️ Technology Stack

### Frontend
- **React 19** with TypeScript
- **TailwindCSS** for styling
- **React Router** for navigation
- **Axios** for API communication
- **Vite** for build tooling

### Backend
- **FastAPI** (Python web framework)
- **SQLAlchemy** (ORM)
- **PostgreSQL** (Database)
- **Pydantic** (Data validation)
- **Uvicorn** (ASGI server)

### AI Services
- **OpenAI GPT-4** for agent intelligence
- **Anthropic Claude** for enhanced reasoning
- **Custom PDF processing** for case study analysis

## 📁 Project Structure

```
ai-agent-education-platform/
├── backend/
│   ├── models.py              # Database models
│   ├── schemas.py             # Pydantic schemas
│   ├── main.py               # FastAPI application
│   ├── database.py           # Database configuration
│   ├── services/
│   │   ├── ai_service.py     # AI agent logic
│   │   ├── pdf_processor.py  # PDF analysis
│   │   └── simulation_engine.py  # Simulation logic
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API service layer
│   │   └── App.tsx          # Main application
│   ├── public/              # Static assets
│   └── package.json         # Node dependencies
└── README.md               # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8 with Black formatting
- **TypeScript**: Use Prettier with ESLint
- **Commits**: Use conventional commits format

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Inspired by **n-aible**'s innovative approach to AI education
- Built with modern web technologies and AI APIs
- Designed for educators and students worldwide

## 📞 Support

- **Documentation**: [Wiki](../../wiki)
- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

## 🗺️ Roadmap

- [ ] **Mobile App** (React Native)
- [ ] **Advanced Analytics** (Student performance tracking)
- [ ] **Multi-language Support** (i18n)
- [ ] **Voice Interaction** (Speech-to-text with agents)
- [ ] **VR/AR Integration** (Immersive simulations)
- [ ] **LMS Integration** (Canvas, Blackboard, Moodle)

---

<div align="center">

**[⭐ Star this repository](../../stargazers) • [🐛 Report Bug](../../issues) • [✨ Request Feature](../../issues)**

Made with ❤️ for educators and students worldwide

</div> 