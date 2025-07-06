#!/usr/bin/env python3
"""
Simple script to add missing authentication columns to the users table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text
from database.connection import settings

def add_missing_columns():
    """Add missing authentication columns to the users table"""
    
    engine = create_engine(settings.database_url)
    
    # SQL commands to add missing columns
    alter_commands = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;", 
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;",
    ]
    
    try:
        with engine.connect() as conn:
            for command in alter_commands:
                print(f"Executing: {command}")
                conn.execute(text(command))
            conn.commit()
        
        print("✅ Successfully added missing columns to users table!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding missing authentication columns to users table...")
    success = add_missing_columns()
    
    if success:
        print("\n🎉 Database schema updated successfully!")
        print("You can now run the authentication tests.")
    else:
        print("\n💥 Schema update failed.") 