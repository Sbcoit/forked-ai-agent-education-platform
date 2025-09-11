#!/usr/bin/env python3
"""
Database Clearing Script
This script safely clears all data from the database by dropping and recreating tables
"""

import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.exc import SQLAlchemyError

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import database connection and models
from database.connection import engine, Base, settings
from database.models import *

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_database():
    """Clear all data from the database by dropping and recreating tables"""
    logger.info("🗑️  Starting database clearing process...")
    
    try:
        # Test connection first
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Get database URL for logging (partial for security)
        db_url_partial = settings.database_url.split('@')[0] + '@...'
        logger.info(f"🔗 Database URL: {db_url_partial}")
        
        # Confirm with user
        print("\n" + "="*60)
        print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
        print("="*60)
        print(f"Database: {db_url_partial}")
        print("This action cannot be undone!")
        print("="*60)
        
        response = input("\nAre you sure you want to clear the database? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            logger.info("❌ Database clearing cancelled by user")
            return False
        
        # Drop all tables
        logger.info("Dropping all tables...")
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            try:
                # Drop all tables in the correct order (respecting foreign key constraints)
                logger.info("Dropping tables in dependency order...")
                
                # Get all table names
                metadata = MetaData()
                metadata.reflect(bind=engine)
                table_names = list(metadata.tables.keys())
                
                logger.info(f"Found {len(table_names)} tables to drop: {', '.join(table_names)}")
                
                # Drop all tables at once (PostgreSQL handles dependencies)
                for table_name in table_names:
                    logger.info(f"Dropping table: {table_name}")
                    conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
                
                # Commit the transaction
                trans.commit()
                logger.info("✅ All tables dropped successfully")
                
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Error dropping tables: {e}")
                raise
        
        # Recreate all tables
        logger.info("Recreating all tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables recreated successfully")
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"✅ Verified {len(tables)} tables created: {', '.join(tables)}")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 Database cleared successfully!")
        logger.info("All tables have been dropped and recreated.")
        logger.info("The database is now empty and ready for fresh data.")
        logger.info("="*60)
        
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Database Clearing Script")
    logger.info("="*50)
    
    if clear_database():
        logger.info("✅ Database clearing completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Database clearing failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
