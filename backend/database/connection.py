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
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "")
    
    # Vector database configuration
    use_pgvector: bool = os.getenv("USE_PGVECTOR", "true").lower() == "true"
    
    class Config:
        env_file = project_root / ".env"  # Look for .env in project root

settings = Settings()

# Validate environment settings
def _validate_environment():
    """Validate environment settings for production"""
    if settings.environment == "production":
        if not settings.google_client_id or not settings.google_client_id.strip():
            raise RuntimeError("GOOGLE_CLIENT_ID is required in production environment")
        if not settings.google_client_secret or not settings.google_client_secret.strip():
            raise RuntimeError("GOOGLE_CLIENT_SECRET is required in production environment")
        if not settings.google_redirect_uri or not settings.google_redirect_uri.strip():
            raise RuntimeError("GOOGLE_REDIRECT_URI is required in production environment")
        if "localhost" in settings.google_redirect_uri:
            raise RuntimeError("GOOGLE_REDIRECT_URI cannot use localhost in production environment")

# Validation is now called from application startup instead of import time

# Print loaded settings securely
from utilities.secure_logging import secure_print_api_key_status, secure_print_database_url

print(f"🌍 Environment: {settings.environment}")
secure_print_api_key_status("OpenAI API Key", settings.openai_api_key, settings.environment)
secure_print_api_key_status("Secret Key", settings.secret_key, settings.environment)
secure_print_database_url(settings.database_url, settings.environment)

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
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )
else:
    raise ValueError("Unsupported database URL format. Only PostgreSQL and SQLite are supported.")

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