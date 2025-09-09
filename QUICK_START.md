# 🚀 Quick Start Guide

## Prerequisites
- **Python 3.11+** (recommended: 3.11 or higher)
- **Node.js 18+** (recommended: 18 or higher)
- **PostgreSQL** (primary database)
- **Git**
- **OpenAI API Key** (for AI features)
- **LlamaParse API Key** (for PDF processing)

## Complete Setup (5 minutes)

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd ai-agent-education-platform

# 2. Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up environment variables
cp env_template.txt .env
# Edit .env with your API keys

# 4. Initialize database (Alembic will handle this automatically)
cd backend/database
alembic upgrade head

# 5. Start the application
cd ..
uvicorn main:app --reload
```

**Access the application:**
- Frontend: http://localhost:3000 (start with `cd frontend && npm run dev`)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: PostgreSQL (primary database)

## Database Setup

### **PostgreSQL (Primary Database)**
The application uses PostgreSQL as the primary database for all environments.

**Local Development Setup:**
```bash
# Example for local PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/ai_agent_platform
```

**Production Setup:**
```bash
# Example for production PostgreSQL
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?sslmode=require
```

### **SQLite (Optional Development)**
SQLite is available only when explicitly configured:
```bash
# Only use if you specifically want SQLite for development
DATABASE_URL=sqlite:///./ai_agent_platform.db
```

### **Database Migrations**
The project uses Alembic for database migrations:

```bash
# Navigate to database directory
cd backend/database

# Check current migration status
alembic current

# Apply all pending migrations
alembic upgrade head

# Create new migration (when you modify models)
alembic revision --autogenerate -m "Description of changes"

# View migration history
alembic history
```

## Backend Setup

1. **Create and activate virtual environment:**
```bash
# From the root directory
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
# From the root directory
pip install -r requirements.txt
```

3. **Navigate to backend directory:**
```bash
cd backend
```

4. **Environment setup:**
```bash
# Copy template and edit with your API keys (from root directory)
cp env_template.txt .env

# Edit .env file with your API keys:
# OPENAI_API_KEY=your_openai_api_key_here
# LLAMAPARSE_API_KEY=your_llamaparse_api_key_here
# DATABASE_URL=postgresql://username:password@localhost:5432/ai_agent_platform  # Primary (PostgreSQL)
# DATABASE_URL=sqlite:///./ai_agent_platform.db  # Optional (SQLite)
```

5. **Initialize database:**
```bash
# Navigate to database directory and run migrations
cd backend/database
alembic upgrade head
cd ..
```

6. **Start backend:**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Backend runs at: http://127.0.0.1:8000

## Frontend Setup

1. **Navigate to frontend (new terminal):**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```
Frontend runs at: http://localhost:3000

**Note**: The frontend is now built with Next.js 15, TypeScript, and Tailwind CSS with shadcn/ui components.

## Frontend Tech Stack

The frontend has been restructured and modernized with:

- **Next.js 15**: Latest version with App Router for optimal performance
- **TypeScript**: Full type safety throughout the application
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **shadcn/ui**: Modern, accessible component library built on Radix UI
- **React Hook Form + Zod**: Robust form handling with validation
- **Next Themes**: Dark/light mode support with system preference detection
- **Lucide React**: Beautiful, customizable icons

## Key Features
- **Simulation Builder**: Upload PDF case studies and create AI-driven business simulations
- **Chat Interface**: Interactive student-agent conversations with ChatOrchestrator
- **Marketplace**: Browse and publish educational scenarios
- **Dashboard**: Track learning progress and analytics

## API Documentation
Visit http://127.0.0.1:8000/docs for interactive API documentation.

## Common Issues
- **Virtual env not found**: Ensure you're in the backend directory when activating
- **Port conflicts**: Backend uses 8000, frontend uses 3000
- **Database issues**: Ensure PostgreSQL is running and DATABASE_URL is correctly configured
- **API key errors**: Ensure .env file is properly configured with valid API keys
- **Migration errors**: Run `alembic upgrade head` in backend/database directory

## Project Structure
```
ai-agent-education-platform/
├── backend/                    # FastAPI + SQLAlchemy backend
│   ├── main.py                # Application entry point
│   ├── api/                   # API endpoints
│   │   ├── parse_pdf.py       # PDF processing
│   │   ├── simulation.py      # Simulation management
│   │   ├── chat_orchestrator.py # Chat system
│   │   └── publishing.py      # Marketplace features
│   ├── database/              # Database models and migrations
│   ├── services/              # Business logic
│   ├── utilities/             # Helper functions
│   ├── db_admin/              # Database admin interface
│   └── docs/                  # API documentation
├── frontend/                  # Next.js + TypeScript frontend
│   ├── app/                   # Next.js app router pages
│   │   ├── simulation-builder/  # PDF upload and simulation creation
│   │   ├── chat-box/          # Interactive chat interface
│   │   ├── marketplace/       # Community scenarios
│   │   ├── agent-builder/     # AI agent creation tools
│   │   ├── dashboard/         # User analytics
│   │   └── login/            # Authentication pages
│   ├── components/            # React components (shadcn/ui)
│   ├── lib/                   # Utilities and API clients
│   └── hooks/                 # Custom React hooks
├── .env                       # Environment variables (create from template)
├── .gitignore                 # Git ignore rules (consolidated)
├── requirements.txt           # Python dependencies
├── env_template.txt           # Environment variables template
├── README.md                  # Project documentation
├── QUICK_START.md             # This setup guide
├── CONTRIBUTING.md            # Contributor guidelines
└── LICENSE                    # MIT License
```

## Recent Improvements

### **Database & Migration System**
- ✅ **Alembic Integration**: Professional database migrations replacing custom scripts
- ✅ **PostgreSQL Support**: Production-ready database with optimized indexes
- ✅ **Cross-Database Compatibility**: Works with both SQLite (dev) and PostgreSQL (prod)
- ✅ **Migration Management**: Version control for database schema changes

### **Project Structure Cleanup**
- ✅ **Clean Root Directory**: Removed outdated documentation and duplicate files
- ✅ **Organized Backend**: Streamlined file structure with clear separation of concerns
- ✅ **Updated Documentation**: Current and accurate setup guides
- ✅ **Professional Appearance**: Clean, maintainable codebase

### **OpenAI Integration**
- ✅ **Comprehensive AI Features**: PDF processing, persona generation, scene creation
- ✅ **Real-time Chat**: Interactive AI personas with personality traits
- ✅ **Assessment System**: AI-powered grading and feedback
- ✅ **Image Generation**: DALL-E integration for scene visualization

## Development Workflow

1. **Install Dependencies**: `pip install -r requirements.txt` (from root)
2. **Start Backend**: `cd backend && uvicorn main:app --reload`
3. **Start Frontend**: `cd frontend && npm run dev`
4. **Access Application**: http://localhost:3000
5. **API Docs**: http://localhost:8000/docs

## Optional: Database Admin Interface

The project includes a Flask-based database admin interface for viewing and managing the database:

```bash
# Start the database admin interface
cd backend/db_admin
python simple_viewer.py
```

Access at: http://localhost:5001

## Next Steps
- Upload a business case study PDF to test the simulation builder
- Create your first AI-powered simulation
- Explore the marketplace for community scenarios
- Check out the comprehensive documentation in `backend/docs/`
- Use the database admin interface to inspect your data

Ready to build AI-powered educational experiences! 🎓 