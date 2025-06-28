#!/usr/bin/env python3
"""
AI Agent Education Platform - Development Setup Script
This script helps set up the development environment quickly.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"\n🚀 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        'python': 'python --version',
        'pip': 'pip --version',
        'node': 'node --version',
        'npm': 'npm --version'
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            print(f"✅ {tool} is installed")
        except subprocess.CalledProcessError:
            print(f"❌ {tool} is not installed")
            missing.append(tool)
    
    if missing:
        print(f"\n❌ Please install missing requirements: {', '.join(missing)}")
        return False
    
    return True

def setup_backend():
    """Set up the Python backend"""
    print("\n🐍 Setting up Python backend...")
    
    # Create virtual environment
    if not os.path.exists('venv'):
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            return False
    
    # Activate virtual environment and install dependencies
    if sys.platform.startswith('win'):
        activate_cmd = 'venv\\Scripts\\activate && '
    else:
        activate_cmd = 'source venv/bin/activate && '
    
    commands = [
        f'{activate_cmd}pip install --upgrade pip',
        f'{activate_cmd}pip install -r requirements.txt'
    ]
    
    for cmd in commands:
        description = cmd.split('&&')[-1].strip()
        if not run_command(cmd, f'Running: {description}'):
            return False
    
    return True

def setup_frontend():
    """Set up the React frontend"""
    print("\n⚛️ Setting up React frontend...")
    
    # Create React app if it doesn't exist
    if not os.path.exists('frontend'):
        commands = [
            'npx create-react-app frontend --template typescript',
            'cd frontend && npm install axios react-router-dom @types/react-router-dom',
            'cd frontend && npm install @tailwindcss/forms tailwindcss postcss autoprefixer',
            'cd frontend && npx tailwindcss init -p'
        ]
        
        for cmd in commands:
            if not run_command(cmd, f'Running: {cmd}'):
                return False
    else:
        print("✅ Frontend directory already exists")
    
    return True

def create_env_file():
    """Create .env file from template"""
    print("\n📝 Setting up environment variables...")
    
    if not os.path.exists('.env'):
        if os.path.exists('env_template.txt'):
            run_command('cp env_template.txt .env', 'Creating .env file from template')
            print("📝 Please edit .env file with your API keys and database settings")
        else:
            print("⚠️ env_template.txt not found, please create .env manually")
    else:
        print("✅ .env file already exists")

def setup_database():
    """Setup database instructions"""
    print("\n🗄️ Database setup instructions:")
    print("1. Install PostgreSQL and Redis")
    print("2. Create database: CREATE DATABASE ai_agent_platform;")
    print("3. Update DATABASE_URL in .env file")
    print("4. Run: python -m alembic init alembic")
    print("5. Run: python -m alembic revision --autogenerate -m 'initial'")
    print("6. Run: python -m alembic upgrade head")

def main():
    """Main setup function"""
    print("🎓 AI Agent Education Platform - Development Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Database setup instructions
    setup_database()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Setup PostgreSQL and Redis")
    print("3. Run backend: cd backend && python main.py")
    print("4. Run frontend: cd frontend && npm start")
    print("5. Visit http://localhost:3000")

if __name__ == "__main__":
    main() 