"""
Startup Check Module
Automatically checks and sets up the development environment when the backend starts
"""

import os
import sys
import subprocess
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_setup_flag_file():
    """Get the path to the setup completion flag file"""
    return Path(__file__).parent / ".setup_completed"

def is_setup_completed():
    """Check if initial setup has been completed"""
    flag_file = get_setup_flag_file()
    return flag_file.exists()

def mark_setup_completed():
    """Mark that initial setup has been completed"""
    flag_file = get_setup_flag_file()
    flag_file.touch()
    logger.info("✅ Setup completion marked")

def should_run_full_setup():
    """Determine if we should run full setup (only on first run or if forced)"""
    if not is_setup_completed():
        return True
    
    # Check if forced via environment variable
    if os.getenv('FORCE_SETUP') == 'true':
        logger.info("🔄 Force setup requested via FORCE_SETUP environment variable")
        return True
    
    return False

def check_postgresql_connection():
    """Check if PostgreSQL is running and accessible"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ PostgreSQL is available: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ PostgreSQL is not accessible")
            return False
    except FileNotFoundError:
        logger.error("❌ PostgreSQL is not installed or not in PATH")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking PostgreSQL: {e}")
        return False

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        from database.connection import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("✅ Database connection successful")
                return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        logger.warning("⚠️  .env file not found")
        return False
    
    # Check for required environment variables
    required_vars = ['DATABASE_URL', 'OPENAI_API_KEY', 'SECRET_KEY']
    missing_vars = []
    
    with open(env_file, 'r') as f:
        env_lines = f.readlines()
    
    env_vars = set()
    for line in env_lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                var_name = line.split('=', 1)[0].strip()
                env_vars.add(var_name)
    
    for var in required_vars:
        if var not in env_vars:
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ .env file is properly configured")
    return True

def check_database_tables():
    """Check if database tables exist"""
    try:
        from database.connection import engine
        from sqlalchemy import text
        
        # Check if tables exist by trying to query a simple table
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.scalar()
            
            if table_count > 0:
                logger.info(f"✅ Database has {table_count} tables")
                return True
            else:
                logger.warning("⚠️  No tables found in database")
                return False
    except Exception as e:
        logger.error(f"❌ Failed to check database tables: {e}")
        return False

def check_vector_database_config():
    """Check if vector database configuration matches the actual database state"""
    try:
        from database.connection import engine, settings
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check if pgvector extension is available
            result = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
            pgvector_available = result.fetchone() is not None
            
            # Check if vector_embeddings table exists and what type its column is
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'vector_embeddings' 
                AND column_name = 'embedding_vector'
            """))
            column_type = result.fetchone()
            
            if column_type:
                is_vector_type = column_type[0] == 'USER-DEFINED'  # pgvector columns show as USER-DEFINED
                is_json_type = column_type[0] == 'json'
                
                # Validate configuration matches database state
                if settings.use_pgvector:
                    if not pgvector_available:
                        logger.error("❌ USE_PGVECTOR=true but pgvector extension is not available")
                        return False
                    if not is_vector_type:
                        logger.error("❌ USE_PGVECTOR=true but vector_embeddings.embedding_vector is not vector type")
                        return False
                    logger.info("✅ Vector database configuration matches database state")
                else:
                    if is_vector_type:
                        logger.error("❌ USE_PGVECTOR=false but vector_embeddings.embedding_vector is vector type")
                        return False
                    logger.info("✅ JSON database configuration matches database state")
                
                return True
            else:
                logger.info("✅ Vector database configuration check passed (no vector_embeddings table yet)")
                return True
                
    except Exception as e:
        logger.error(f"❌ Failed to check vector database configuration: {e}")
        return False

def run_startup_checks():
    """Run startup checks - lightweight for subsequent runs, full for first time"""
    if should_run_full_setup():
        logger.info("🔍 Running full startup checks (first time)...")
        return run_full_startup_checks()
    else:
        logger.info("🔍 Running lightweight startup checks...")
        return run_lightweight_checks()

def run_full_startup_checks():
    """Run comprehensive startup checks (first time only)"""
    issues_found = []
    
    # Check PostgreSQL
    if not check_postgresql_connection():
        issues_found.append("PostgreSQL is not installed or not running")
    
    # Check .env file
    if not check_env_file():
        issues_found.append(".env file is missing or incomplete")
    
    # Check database connection
    if not check_database_connection():
        issues_found.append("Cannot connect to database")
    
    # Check database tables
    if not check_database_tables():
        issues_found.append("Database tables are missing")
    
    # Check vector database configuration
    if not check_vector_database_config():
        issues_found.append("Vector database configuration mismatch")
    
    if issues_found:
        logger.error("❌ Startup checks failed!")
        logger.error("Issues found:")
        for issue in issues_found:
            logger.error(f"  - {issue}")
        
        logger.error("\n🔧 To fix these issues, run the setup script:")
        logger.error("  python backend/setup_dev_environment.py")
        logger.error("\nOr manually:")
        logger.error("  1. Install PostgreSQL")
        logger.error("  2. Copy env_template.txt to .env and fill in your values")
        logger.error("  3. Run: cd backend/database && alembic upgrade head")
        
        return False
    else:
        logger.info("✅ All startup checks passed!")
        return True

def run_lightweight_checks():
    """Run lightweight checks for subsequent startups"""
    # Just check database connection - the most critical check
    if not check_database_connection():
        logger.error("❌ Database connection failed!")
        logger.error("🔧 To fix this, run: python backend/setup_dev_environment.py")
        return False
    
    logger.info("✅ Lightweight startup checks passed!")
    return True

def auto_setup_if_needed():
    """Automatically run setup if needed (only for development and first time)"""
    if os.getenv('ENVIRONMENT') == 'development' and should_run_full_setup():
        logger.info("🔧 First-time development setup detected...")
        
        # Check if .env file is missing or database connection fails
        env_file = Path(__file__).parent.parent / ".env"
        needs_setup = not env_file.exists() or not check_database_connection()
        
        if needs_setup:
            logger.info("🚀 Auto-running development setup...")
            try:
                # Import and run the setup script in non-interactive mode
                setup_script = Path(__file__).parent / "setup_dev_environment.py"
                if setup_script.exists():
                    # Run setup in non-interactive mode
                    env = os.environ.copy()
                    env['NON_INTERACTIVE'] = 'true'
                    subprocess.run([sys.executable, str(setup_script)], check=True, env=env)
                    
                    # Mark setup as completed
                    mark_setup_completed()
                    logger.info("✅ Auto-setup completed successfully!")
                    return True
                else:
                    logger.warning("⚠️  Setup script not found")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Auto-setup failed: {e}")
                return False
        else:
            # Environment looks good, just mark as completed
            mark_setup_completed()
            logger.info("✅ Development environment already configured")
    
    return True
