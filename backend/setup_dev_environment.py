#!/usr/bin/env python3
"""
Development Environment Setup Script
Helps new developers set up their local development environment
"""

import os
import sys
import subprocess
from pathlib import Path
import logging
import psycopg2
from psycopg2 import sql
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_username(username):
    """Validate PostgreSQL username format"""
    if not username:
        raise ValueError("Username cannot be empty")
    
    # Check if username starts with letter or underscore
    if not re.match(r'^[a-zA-Z_]', username):
        raise ValueError("Username must start with a letter or underscore")
    
    # Check if username contains only allowed characters
    if not re.match(r'^[a-zA-Z0-9_$]+$', username):
        raise ValueError("Username can only contain letters, digits, underscores, and dollar signs")
    
    # Check length (PostgreSQL has a limit of 63 characters for identifiers)
    if len(username) > 63:
        raise ValueError("Username cannot exceed 63 characters")
    
    return True

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

def install_postgresql_windows():
    """Install PostgreSQL on Windows using winget or chocolatey"""
    logger.info("Installing PostgreSQL on Windows...")
    
    # Try winget first (Windows 10/11 built-in)
    try:
        logger.info("Trying winget (Windows Package Manager)...")
        subprocess.run(['winget', '--version'], check=True, capture_output=True)
        logger.info("✅ winget is available")
        
        # Install PostgreSQL using winget
        logger.info("Installing PostgreSQL via winget...")
        result = subprocess.run([
            'winget', 'install', 'PostgreSQL.PostgreSQL', '--accept-package-agreements', '--accept-source-agreements'
        ], check=True, capture_output=True, text=True)
        
        logger.info("✅ PostgreSQL installed successfully via winget")
        logger.info("⚠️  Please start PostgreSQL service manually:")
        logger.info("   - Open Services (services.msc)")
        logger.info("   - Find 'postgresql-x64-15' service")
        logger.info("   - Right-click and select 'Start'")
        logger.info("   - Or run: net start postgresql-x64-15")
        
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("winget not available, trying Chocolatey...")
        
        # Try Chocolatey
        try:
            subprocess.run(['choco', '--version'], check=True, capture_output=True)
            logger.info("✅ Chocolatey is available")
            
            # Install PostgreSQL using Chocolatey
            logger.info("Installing PostgreSQL via Chocolatey...")
            subprocess.run(['choco', 'install', 'postgresql', '-y'], check=True)
            
            logger.info("✅ PostgreSQL installed successfully via Chocolatey")
            logger.info("⚠️  Please start PostgreSQL service manually:")
            logger.info("   - Open Services (services.msc)")
            logger.info("   - Find 'postgresql-x64-15' service")
            logger.info("   - Right-click and select 'Start'")
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Neither winget nor Chocolatey is available")
            logger.error("Please install PostgreSQL manually:")
            logger.error("1. Download from: https://www.postgresql.org/download/windows/")
            logger.error("2. Or install Chocolatey: https://chocolatey.org/install")
            logger.error("3. Or install winget: https://docs.microsoft.com/en-us/windows/package-manager/winget/")
            return False

def install_postgresql_linux():
    """Install PostgreSQL on Linux using package managers"""
    logger.info("Installing PostgreSQL on Linux...")
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = f.read().lower()
    except FileNotFoundError:
        # Try alternative detection methods
        try:
            result = subprocess.run(['lsb_release', '-a'], capture_output=True, text=True)
            if result.returncode == 0:
                os_info = result.stdout.lower()
            else:
                logger.error("❌ Cannot detect Linux distribution")
                return False
        except FileNotFoundError:
            logger.error("❌ Cannot detect Linux distribution")
            return False
    except FileNotFoundError:
        logger.error("❌ Cannot detect Linux distribution")
        return False
    
    # Ubuntu/Debian
    if 'ubuntu' in os_info or 'debian' in os_info:
        try:
            logger.info("Detected Ubuntu/Debian, using apt...")
            
            # Update package list
            logger.info("Updating package list...")
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            
            # Install PostgreSQL
            logger.info("Installing PostgreSQL...")
            subprocess.run(['sudo', 'apt', 'install', '-y', 'postgresql', 'postgresql-contrib'], check=True)
            
            # Start and enable PostgreSQL service
            logger.info("Starting PostgreSQL service...")
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], check=True)
            
            logger.info("✅ PostgreSQL installed and started successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install PostgreSQL via apt: {e}")
            return False
    
    # CentOS/RHEL/Fedora
    elif 'centos' in os_info or 'rhel' in os_info or 'fedora' in os_info:
        try:
            if 'fedora' in os_info:
                logger.info("Detected Fedora, using dnf...")
                package_manager = 'dnf'
            else:
                logger.info("Detected CentOS/RHEL, using yum...")
                package_manager = 'yum'
            
            # Install PostgreSQL
            logger.info("Installing PostgreSQL...")
            subprocess.run(['sudo', package_manager, 'install', '-y', 'postgresql-server', 'postgresql-contrib'], check=True)
            
            # Initialize database (CentOS/RHEL only)
            if package_manager == 'yum':
                logger.info("Initializing PostgreSQL database...")
                subprocess.run(['sudo', 'postgresql-setup', 'initdb'], check=True)
            
            # Start and enable PostgreSQL service
            logger.info("Starting PostgreSQL service...")
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], check=True)
            
            logger.info("✅ PostgreSQL installed and started successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install PostgreSQL via {package_manager}: {e}")
            return False
    
    # Arch Linux
    elif 'arch' in os_info:
        try:
            logger.info("Detected Arch Linux, using pacman...")
            
            # Update package database
            logger.info("Updating package database...")
            subprocess.run(['sudo', 'pacman', '-Sy'], check=True)
            
            # Install PostgreSQL
            logger.info("Installing PostgreSQL...")
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'postgresql'], check=True)
            
            # Initialize database
            logger.info("Initializing PostgreSQL database...")
            subprocess.run(['sudo', '-u', 'postgres', 'initdb', '-D', '/var/lib/postgres/data'], check=True)
            
            # Start and enable PostgreSQL service
            logger.info("Starting PostgreSQL service...")
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], check=True)
            
            logger.info("✅ PostgreSQL installed and started successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install PostgreSQL via pacman: {e}")
            return False
    
    else:
        logger.error("❌ Unsupported Linux distribution")
        logger.error("Please install PostgreSQL manually for your distribution")
        return False

def create_database_and_user():
    """Create database and user for the application"""
    logger.info("Setting up database and user...")
    
    # Default values for development
    db_name = "ai_agent_platform_dev"
    db_user = "ai_agent_user"
    db_password = "dev_password_123"  # Change this in production!
    
    # Allow user to customize database name (only in interactive mode)
    non_interactive = os.getenv('NON_INTERACTIVE') == 'true'
    if not non_interactive:
        custom_db = input(f"Enter database name (default: {db_name}): ").strip()
        if custom_db:
            db_name = custom_db
    
    # Validate username before proceeding
    try:
        validate_username(db_user)
    except ValueError as e:
        logger.error(f"❌ Invalid username: {e}")
        return None
    
    try:
        # Connect to PostgreSQL as superuser (postgres)
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create user using safe SQL composition
        logger.info(f"Creating user '{db_user}'...")
        create_user_sql = sql.SQL("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = {username}) THEN
                CREATE USER {username} WITH PASSWORD {password};
            END IF;
        END
        $$;
        """).format(
            username=sql.Identifier(db_user),
            password=sql.Literal(db_password)
        )
        cursor.execute(create_user_sql)
        
        # Create database using safe SQL composition
        logger.info(f"Creating database '{db_name}'...")
        # Create database using safe SQL composition
        logger.info(f"Creating database '{db_name}'...")
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        if not cursor.fetchone():
            # Database doesn't exist, create it
            # Note: CREATE DATABASE cannot be parameterized, but we use sql.Identifier for safety
            create_db_sql = sql.SQL("CREATE DATABASE {dbname} OWNER {owner}").format(
                dbname=sql.Identifier(db_name),
                owner=sql.Identifier(db_user)
            )
            cursor.execute(create_db_sql)
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        # Grant privileges using safe SQL composition
        logger.info("Granting privileges...")
        grant_sql = sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {username};").format(
            dbname=sql.Identifier(db_name),
            username=sql.Identifier(db_user)
        )
        cursor.execute(grant_sql)
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Database and user created successfully")
        
        # Generate connection string
        connection_string = f"postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"
        logger.info(f"Database connection string: {connection_string}")
        
        return connection_string
        
    except (psycopg2.Error, Exception) as e:
        logger.error(f"❌ Failed to create database/user: {e}")
        return None

def create_env_file(connection_string):
    """Create .env file from template"""
    env_file = Path(__file__).parent.parent / ".env"
    env_template = Path(__file__).parent.parent / "env_template.txt"
    
    if env_file.exists():
        logger.info("✅ .env file already exists")
        return True
    
    if not env_template.exists():
        logger.error("❌ env_template.txt not found")
        return False
    
    logger.info("Creating .env file from template...")
    
    try:
        # Read template
        with open(env_template, 'r') as f:
            template_content = f.read()
        
        # Replace DATABASE_URL
        env_content = template_content.replace(
            'DATABASE_URL=postgresql://username:password@localhost:5432/ai_agent_platform',
            f'DATABASE_URL={connection_string}'
        )
        
        # Write .env file
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info("✅ .env file created successfully")
        logger.info("⚠️  Please update the .env file with your actual API keys!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create .env file: {e}")
        return False

def run_alembic_migration():
    """Run Alembic migration to create tables"""
    logger.info("Running Alembic migration...")
    
    database_dir = Path(__file__).parent / "database"
    
    try:
        # Change to database directory and run migration
        try:
            # Change to database directory and run migration
            result = subprocess.run([
                'alembic', 'upgrade', 'head'
            ], cwd=database_dir, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Alembic migration failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            # Attempt to show current migration status
            try:
                status_result = subprocess.run([
                    'alembic', 'current'
                ], cwd=database_dir, capture_output=True, text=True)
                logger.info(f"Current migration status: {status_result.stdout}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to get current migration status: {e}")
                if e.stderr:
                    logger.warning(f"Error output: {e.stderr}")
            except FileNotFoundError:
                logger.warning("Alembic command not found - cannot show current migration status")
            except OSError as e:
                logger.warning(f"OS error while checking migration status: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error while checking migration status: {e}")
            return False
        
        logger.info("✅ Alembic migration completed successfully")
        logger.info(f"Migration output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Alembic migration failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    logger.info("Installing Python dependencies...")
    
    try:
        requirements_file = Path(__file__).parent.parent / "requirements.txt"
        if not requirements_file.exists():
            logger.error("❌ requirements.txt not found")
            return False
        
        result = subprocess.run([
            'pip', 'install', '-r', str(requirements_file)
        ], check=True, capture_output=True, text=True)
        
        logger.info("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 AI Agent Education Platform - Development Setup")
    logger.info("=" * 60)
    
    # Check if running in non-interactive mode
    non_interactive = '--non-interactive' in sys.argv or os.getenv('NON_INTERACTIVE') == 'true'
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installation():
        if non_interactive:
            logger.error("❌ PostgreSQL is not installed. Please install it manually.")
            logger.error("Visit: https://www.postgresql.org/download/")
            return False
        
        logger.info("PostgreSQL is not installed. Would you like to install it?")
        response = input("Install PostgreSQL? (y/N): ")
        if response.lower() == 'y':
            if sys.platform == "darwin":  # macOS
                if not install_postgresql_macos():
                    logger.error("Failed to install PostgreSQL")
                    return False
            elif sys.platform == "win32":  # Windows
                if not install_postgresql_windows():
                    logger.error("Failed to install PostgreSQL")
                    return False
            elif sys.platform.startswith("linux"):  # Linux
                if not install_postgresql_linux():
                    logger.error("Failed to install PostgreSQL")
                    return False
            else:
                logger.error(f"Automatic PostgreSQL installation is not supported on {sys.platform}")
                logger.info("Please install PostgreSQL manually for your operating system.")
                logger.info("Visit: https://www.postgresql.org/download/")
                return False
        else:
            logger.info("Please install PostgreSQL manually and run this script again.")
            return False
    
    # Install Python dependencies
    if not install_python_dependencies():
        logger.error("Failed to install Python dependencies")
        return False
    
    # Create database and user
    connection_string = create_database_and_user()
    if not connection_string:
        logger.error("Failed to create database and user")
        return False
    
    # Create .env file
    if not create_env_file(connection_string):
        logger.error("Failed to create .env file")
        return False
    
    # Run Alembic migration
    if not run_alembic_migration():
        logger.error("Alembic migration failed")
        return False
    
    # Mark setup as completed
    setup_flag_file = Path(__file__).parent / ".setup_completed"
    setup_flag_file.touch()
    logger.info("✅ Setup completion marked")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 Development environment setup completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Update your .env file with actual API keys")
    logger.info("2. Start the backend: cd backend && python main.py")
    logger.info("3. Start the frontend: cd frontend && npm run dev")
    logger.info("\nFor database management:")
    logger.info("- Create migrations: cd backend/database && alembic revision --autogenerate -m 'description'")
    logger.info("- Apply migrations: cd backend/database && alembic upgrade head")
    logger.info("- Clear database: cd backend && python clear_database.py")
    logger.info("\nTo force re-setup: FORCE_SETUP=true python backend/main.py")

if __name__ == "__main__":
    main()
