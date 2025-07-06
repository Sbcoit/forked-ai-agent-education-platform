#!/usr/bin/env python3
"""
Script to fix the test database schema by adding missing authentication columns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text

# Test database URL
TEST_DATABASE_URL = "postgresql://nAIbleDataBase_owner:npg_3lD0MTKbBAsL@ep-spring-snow-a8hq9mjp-pooler.eastus2.azure.neon.tech/EdTechPlatfrom_TestBase?sslmode=require&channel_binding=require"

def fix_test_database():
    """Add missing authentication columns to the test database users table"""
    
    engine = create_engine(TEST_DATABASE_URL)
    
    # SQL commands to add missing columns
    alter_commands = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;", 
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;"
    ]
    
    try:
        with engine.connect() as conn:
            for command in alter_commands:
                print(f"Executing: {command}")
                conn.execute(text(command))
            conn.commit()
        
        print("✅ Successfully added missing columns to test database users table!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding missing authentication columns to TEST database...")
    success = fix_test_database()
    
    if success:
        print("\n🎉 Test database schema updated successfully!")
        print("You can now run the authentication tests.")
    else:
        print("\n💥 Test database schema update failed.") 