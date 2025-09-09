#!/usr/bin/env python3
"""
Test script to verify PostgreSQL and Alembic setup
Run this script to test your PostgreSQL and Alembic configuration
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.connection import settings, engine, SessionLocal
from database.models import Base, User, Scenario

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """Test basic database connection"""
    logger.info("Testing PostgreSQL connection...")
    
    try:
        session = SessionLocal()
        
        # Test basic connection
        result = session.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        
        if test_value == 1:
            logger.info("✅ Basic connection test passed")
            return True
        else:
            logger.error("❌ Basic connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def test_alembic_version():
    """Test Alembic version table"""
    logger.info("Testing Alembic version table...")
    
    try:
        session = SessionLocal()
        
        # Check if alembic_version table exists
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            );
        """))
        table_exists = result.scalar()
        
        if table_exists:
            # Get current version
            result = session.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            logger.info(f"✅ Alembic version table exists, current version: {version}")
            return True
        else:
            logger.error("❌ Alembic version table not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Alembic version test failed: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def test_tables_exist():
    """Test if all required tables exist"""
    logger.info("Testing if all tables exist...")
    
    expected_tables = [
        'users', 'scenarios', 'scenario_personas', 'scenario_scenes',
        'scenario_files', 'scenario_reviews', 'user_progress',
        'scene_progress', 'conversation_logs', 'scene_personas'
    ]
    
    try:
        session = SessionLocal()
        
        for table in expected_tables:
            result = session.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                logger.info(f"✅ Table '{table}' exists")
            else:
                logger.error(f"❌ Table '{table}' not found")
                return False
        
        logger.info("✅ All required tables exist")
        return True
        
    except Exception as e:
        logger.error(f"❌ Table existence test failed: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def test_crud_operations():
    """Test basic CRUD operations"""
    logger.info("Testing basic CRUD operations...")
    
    try:
        session = SessionLocal()
        
        # Test INSERT
        test_user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password_hash="test_hash"
        )
        session.add(test_user)
        session.commit()
        logger.info("✅ INSERT test passed")
        
        # Test SELECT
        user = session.query(User).filter(User.email == "test@example.com").first()
        if user:
            logger.info("✅ SELECT test passed")
        else:
            logger.error("❌ SELECT test failed")
            return False
        
        # Test UPDATE
        user.full_name = "Updated Test User"
        session.commit()
        logger.info("✅ UPDATE test passed")
        
        # Test DELETE
        session.delete(user)
        session.commit()
        logger.info("✅ DELETE test passed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CRUD operations test failed: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def test_json_operations():
    """Test JSON field operations"""
    logger.info("Testing JSON field operations...")
    
    try:
        session = SessionLocal()
        
        # Test JSON field
        test_scenario = Scenario(
            title="Test Scenario",
            description="Test description",
            learning_objectives=["objective1", "objective2"],
            tags=["tag1", "tag2"]
        )
        session.add(test_scenario)
        session.commit()
        
        # Retrieve and verify JSON data
        scenario = session.query(Scenario).filter(Scenario.title == "Test Scenario").first()
        if scenario and scenario.learning_objectives == ["objective1", "objective2"]:
            logger.info("✅ JSON operations test passed")
        else:
            logger.error("❌ JSON operations test failed")
            return False
        
        # Clean up
        session.delete(scenario)
        session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ JSON operations test failed: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def test_indexes():
    """Test if indexes exist"""
    logger.info("Testing database indexes...")
    
    expected_indexes = [
        'idx_users_email', 'idx_users_username', 'idx_users_role',
        'idx_scenarios_title', 'idx_scenarios_industry', 'idx_scenarios_is_public'
    ]
    
    try:
        session = SessionLocal()
        
        for index in expected_indexes:
            result = session.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM pg_indexes 
                    WHERE indexname = '{index}'
                );
            """))
            index_exists = result.scalar()
            
            if index_exists:
                logger.info(f"✅ Index '{index}' exists")
            else:
                logger.warning(f"⚠️  Index '{index}' not found")
        
        logger.info("✅ Index test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Index test failed: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Run all tests"""
    logger.info("🧪 PostgreSQL and Alembic Setup Tests")
    logger.info("=" * 50)
    
    # Check if DATABASE_URL is set to PostgreSQL
    if not settings.database_url or not settings.database_url.startswith("postgresql"):
        logger.error("❌ DATABASE_URL is not set to PostgreSQL")
        logger.info("Please update your .env file with a PostgreSQL connection string")
        return False
    
    logger.info(f"Database URL: {settings.database_url[:50]}...")
    
    tests = [
        ("Connection Test", test_connection),
        ("Alembic Version Test", test_alembic_version),
        ("Tables Existence Test", test_tables_exist),
        ("Basic CRUD Operations Test", test_crud_operations),
        ("JSON Operations Test", test_json_operations),
        ("Indexes Test", test_indexes),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            logger.error(f"❌ {test_name} failed")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! PostgreSQL and Alembic are ready to use.")
        logger.info("\nYou can now:")
        logger.info("1. Start your application: python main.py")
        logger.info("2. Create new migrations: alembic revision --autogenerate -m 'description'")
        logger.info("3. Apply migrations: alembic upgrade head")
        return True
    else:
        logger.error("❌ Some tests failed. Please check your PostgreSQL and Alembic setup.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
