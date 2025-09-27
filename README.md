# 🎓 AI Agent Education Platform
An innovative educational platform that transforms business case studies into immersive AI-powered simulations. Upload PDF case studies, let AI extract key figures and scenarios, then engage students in **linear simulation experiences** with dynamic **ChatOrchestrator** system and intelligent **AI persona interactions**.

![AI Agent Education Platform](https://img.shields.io/badge/AI-Education-blue?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js%2015-TypeScript-000000?style=for-the-badge&logo=nextdotjs)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192?style=for-the-badge&logo=postgresql)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-009688?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai)

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and **pnpm**
- **Python** 3.11+
- **PostgreSQL** 14+
- **Redis** (optional, for caching)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd forked-ai-agent-education-platform
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../env_template.txt .env
# Edit .env with your actual values (database, API keys, etc.)

# Set up database (PostgreSQL)
python setup_dev_environment.py

# Run database migrations
alembic upgrade head

# Start the backend server
python main.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies (using pnpm)
pnpm install

# Start the development server
pnpm dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Environment Variables

Copy `env_template.txt` to `.env` in the backend directory and configure:

### Required Variables
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `SECRET_KEY`: Strong secret key for JWT tokens
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

### Optional Variables
- `REDIS_URL`: Redis connection for caching
- `CORS_ORIGINS`: Allowed CORS origins
- `ENVIRONMENT`: development/production

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **API Layer**: RESTful endpoints with automatic documentation
- **AI Agents**: LangChain-powered agents for personas, grading, and summarization
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT + Google OAuth integration
- **Vector Storage**: Semantic search and memory management

### Frontend (Next.js 15 + TypeScript)
- **Modern UI**: Tailwind CSS + shadcn/ui components
- **Real-time Chat**: Interactive simulation interface
- **State Management**: React Context + custom hooks
- **Authentication**: Google OAuth integration

## 🎯 Key Features

- **PDF-to-Simulation Pipeline**: Upload case studies and generate interactive scenarios
- **AI Persona System**: Dynamic characters with personality traits
- **Linear Simulation Flow**: Structured multi-scene learning progression
- **Community Marketplace**: Share and discover educational content
- **Progress Tracking**: Analytics and learning outcomes

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [Developer Guide](docs/Developer_Guide.md)
- [API Reference](docs/API_Reference.md)
- [Database Guide](docs/Database_Guide.md)
- [Features Overview](docs/Features_Overview.md)
- [Quick Start Guide](docs/QUICK_START.md)

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [documentation](docs/)
2. Review the [troubleshooting guide](docs/Developer_Guide.md#troubleshooting)
3. Create an issue in the repository

## 🏃‍♂️ Development Commands

### Backend
```bash
# Start development server with auto-reload
python main.py

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest

# Clear database (development only)
python clear_database.py
```

### Frontend
```bash
# Start development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run linting
pnpm lint
```

---

**Ready to transform education with AI?** Start building immersive learning experiences today! 🚀
