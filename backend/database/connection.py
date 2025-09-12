from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os
from pathlib import Path

# Get the project root directory where .env file is located
project_root = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    database_url: str = "postgresql://localhost:5432/ai_agent_platform"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    llamaparse_api_key: str | None = None
    gemini_api_key: str | None = None
    
    # Google OAuth settings
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    class Config:
        env_file = project_root / ".env"  # Look for .env in project root

settings = Settings()

# Print loaded settings for debugging (remove in production)
print(f"🔗 Database URL: {settings.database_url.split('@')[0]}@...")
print(f"🤖 OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
print(f"🔑 Secret Key: {'✅ Set' if settings.secret_key else '❌ Missing'}")
print(f"🌍 Environment: {settings.environment}")

# Database setup with SSL and connection pooling
if settings.database_url.startswith("postgresql"):
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        pool_size=5,         # Number of connections to maintain
        max_overflow=10,     # Maximum connections beyond pool_size
        connect_args={
            "connect_timeout": 30,  # Connection timeout
            "application_name": "AOM_2025_Backend"
        }
    )
elif settings.database_url.startswith("sqlite"):
    # Use simpler engine for SQLite (development only)
    print("⚠️  WARNING: Using SQLite for development. PostgreSQL recommended for production.")
    engine = create_engine(settings.database_url)
else:
    raise ValueError(f"Unsupported database URL format: {settings.database_url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 