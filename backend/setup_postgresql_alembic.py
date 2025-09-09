#!/usr/bin/env python3
"""
PostgreSQL and Alembic Setup Script
This script helps you set up PostgreSQL and initialize Alembic migrations
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_postgresql_installation():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ PostgreSQL is installed: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ PostgreSQL is not installed or not in PATH")
            return False
    except FileNotFoundError:
        logger.error("❌ PostgreSQL is not installed or not in PATH")
        return False

def install_postgresql_macos():
    """Install PostgreSQL on macOS using Homebrew"""
    logger.info("Installing PostgreSQL on macOS...")
    
    try:
        # Check if Homebrew is installed
        subprocess.run(['brew', '--version'], check=True, capture_output=True)
        logger.info("✅ Homebrew is installed")
        
        # Install PostgreSQL
        logger.info("Installing PostgreSQL...")
        subprocess.run(['brew', 'install', 'postgresql@15'], check=True)
        
        # Start PostgreSQL service
        logger.info("Starting PostgreSQL service...")
        subprocess.run(['brew', 'services', 'start', 'postgresql@15'], check=True)
        
        logger.info("✅ PostgreSQL installed and started successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install PostgreSQL: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ Homebrew is not installed. Please install Homebrew first.")
        return False

def create_database_and_user():
    """Create database and user for the application"""
    logger.info("Setting up database and user...")
    
    # Get database configuration from user
    db_name = input("Enter database name (default: ai_agent_platform): ").strip() or "ai_agent_platform"
    db_user = input("Enter database user (default: ai_agent_user): ").strip() or "ai_agent_user"
    db_password = input("Enter database password: ").strip()
    
    if not db_password:
        logger.error("❌ Database password is required")
        return False
    
    try:
        # Create user
        logger.info(f"Creating user '{db_user}'...")
        create_user_sql = f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{db_user}') THEN
                CREATE USER {db_user} WITH PASSWORD '{db_password}';
            END IF;
        END
        $$;
        """
        subprocess.run(['psql', 'postgres', '-c', create_user_sql], check=True)
        
        # Create database
        logger.info(f"Creating database '{db_name}'...")
        create_db_sql = f"""
        SELECT 'CREATE DATABASE {db_name} OWNER {db_user}'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{db_name}')\\gexec
        """
        subprocess.run(['psql', 'postgres', '-c', create_db_sql], check=True)
        
        # Grant privileges
        logger.info("Granting privileges...")
        grant_sql = f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"
        subprocess.run(['psql', 'postgres', '-c', grant_sql], check=True)
        
        logger.info("✅ Database and user created successfully")
        
        # Generate connection string
        connection_string = f"postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"
        logger.info(f"Database connection string: {connection_string}")
        
        return connection_string
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to create database/user: {e}")
        return False

def update_env_file(connection_string):
    """Update .env file with PostgreSQL connection string"""
    env_file = Path(__file__).parent.parent / ".env"
    
    logger.info("Updating .env file...")
    
    # Read existing .env file if it exists
    env_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
    
    # Update or add DATABASE_URL
    lines = env_content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            lines[i] = f'DATABASE_URL={connection_string}'
            updated = True
            break
    
    if not updated:
        lines.append(f'DATABASE_URL={connection_string}')
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    logger.info("✅ .env file updated with PostgreSQL connection string")

def run_alembic_migration():
    """Run Alembic migration to create tables"""
    logger.info("Running Alembic migration...")
    
    database_dir = Path(__file__).parent / "database"
    
    try:
        # Change to database directory and run migration
        result = subprocess.run([
            'alembic', 'upgrade', 'head'
        ], cwd=database_dir, check=True, capture_output=True, text=True)
        
        logger.info("✅ Alembic migration completed successfully")
        logger.info(f"Migration output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Alembic migration failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def test_database_connection():
    """Test the database connection"""
    logger.info("Testing database connection...")
    
    try:
        # Import and test connection
        sys.path.insert(0, str(Path(__file__).parent))
        from database.connection import engine, SessionLocal
        
        # Test connection
        session = SessionLocal()
        result = session.execute("SELECT 1 as test")
        test_value = result.scalar()
        session.close()
        
        if test_value == 1:
            logger.info("✅ Database connection test passed")
            return True
        else:
            logger.error("❌ Database connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 PostgreSQL and Alembic Setup")
    logger.info("=" * 50)
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installation():
        logger.info("PostgreSQL is not installed. Would you like to install it?")
        response = input("Install PostgreSQL? (y/N): ")
        if response.lower() == 'y':
            if sys.platform == "darwin":  # macOS
                if not install_postgresql_macos():
                    logger.error("Failed to install PostgreSQL")
                    return False
            else:
                logger.error("Automatic PostgreSQL installation is only supported on macOS.")
                logger.info("Please install PostgreSQL manually for your operating system.")
                return False
        else:
            logger.info("Please install PostgreSQL manually and run this script again.")
            return False
    
    # Create database and user
    connection_string = create_database_and_user()
    if not connection_string:
        logger.error("Failed to create database and user")
        return False
    
    # Update .env file
    update_env_file(connection_string)
    
    # Test database connection
    if not test_database_connection():
        logger.error("Database connection test failed")
        return False
    
    # Run Alembic migration
    if not run_alembic_migration():
        logger.error("Alembic migration failed")
        return False
    
    logger.info("\n" + "=" * 50)
    logger.info("🎉 Setup completed successfully!")
    logger.info("Your application is now configured to use PostgreSQL with Alembic migrations.")
    logger.info("\nNext steps:")
    logger.info("1. Start your application: python main.py")
    logger.info("2. To create new migrations: alembic revision --autogenerate -m 'description'")
    logger.info("3. To apply migrations: alembic upgrade head")
    logger.info("4. To rollback: alembic downgrade -1")

if __name__ == "__main__":
    main()
