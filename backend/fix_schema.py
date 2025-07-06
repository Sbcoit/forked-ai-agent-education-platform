#!/usr/bin/env python3
"""
Comprehensive script to fix all database schema issues.
"""

from sqlalchemy import create_engine, text, inspect
from database.connection import settings
import sys

def check_database_connection():
    """Test database connection and show database info"""
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
            # Check if we can see tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"📋 Found {len(tables)} tables: {', '.join(tables[:5])}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_table_schema():
    """Check current users table schema"""
    try:
        engine = create_engine(settings.database_url)
        inspector = inspect(engine)
        
        if 'users' not in inspector.get_table_names():
            print("⚠️  Users table doesn't exist - will be created")
            return []
        
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        print(f"📋 Current users table columns: {', '.join(column_names)}")
        return column_names
        
    except Exception as e:
        print(f"❌ Error checking table schema: {e}")
        return []

def fix_users_table_comprehensive():
    """Add ALL missing columns to users table"""
    
    engine = create_engine(settings.database_url)
    
    # Complete list of all columns that should exist
    required_columns = [
        ("username", "VARCHAR UNIQUE"),
        ("password_hash", "VARCHAR"), 
        ("bio", "TEXT"),
        ("avatar_url", "VARCHAR"),
        ("role", "VARCHAR DEFAULT 'user'"),
        ("public_agents_count", "INTEGER DEFAULT 0"),
        ("public_tools_count", "INTEGER DEFAULT 0"),
        ("total_downloads", "INTEGER DEFAULT 0"),
        ("reputation_score", "FLOAT DEFAULT 0.0"),
        ("profile_public", "BOOLEAN DEFAULT true"),
        ("allow_contact", "BOOLEAN DEFAULT true"),
        ("is_active", "BOOLEAN DEFAULT true"),
        ("is_verified", "BOOLEAN DEFAULT false"),
        ("updated_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
    ]
    
    alter_commands = []
    
    # Add missing columns
    for column_name, column_def in required_columns:
        alter_commands.append(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {column_def};")
    
    # Add indexes
    alter_commands.extend([
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);",
        "CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);",
        "CREATE INDEX IF NOT EXISTS ix_users_role ON users (role);",
    ])
    
    try:
        with engine.connect() as conn:
            for command in alter_commands:
                print(f"Executing: {command}")
                conn.execute(text(command))
                conn.commit()
        
        print("✅ Successfully updated users table schema!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

def create_all_tables():
    """Create all tables from models if they don't exist"""
    from database.models import Base
    
    try:
        engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def verify_fix():
    """Verify that all required columns now exist"""
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            # Try to select all columns that should exist
            test_query = """
            SELECT id, email, full_name, username, password_hash, bio, avatar_url, 
                   role, public_agents_count, public_tools_count, total_downloads, 
                   reputation_score, profile_public, allow_contact, is_active, 
                   is_verified, created_at, updated_at 
            FROM users LIMIT 1;
            """
            conn.execute(text(test_query))
            print("✅ All required columns exist and are accessible!")
            return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Comprehensive Database Schema Fix")
    print("=" * 60)
    
    # Step 1: Check database connection
    print("\n🔗 Testing database connection...")
    if not check_database_connection():
        print("💥 Cannot proceed without database connection!")
        sys.exit(1)
    
    # Step 2: Check current schema
    print("\n📋 Checking current table schema...")
    current_columns = check_table_schema()
    
    # Step 3: Create missing tables
    print("\n📋 Creating missing tables...")
    create_success = create_all_tables()
    
    # Step 4: Fix users table schema
    print("\n🔧 Adding missing columns to users table...")
    fix_success = fix_users_table_comprehensive()
    
    # Step 5: Verify the fix
    print("\n✅ Verifying schema fix...")
    verify_success = verify_fix()
    
    if create_success and fix_success and verify_success:
        print("\n🎉 Database schema completely fixed!")
        print("You can now register users successfully.")
    else:
        print("\n💥 Schema fix incomplete. Check the errors above.")
        sys.exit(1) 