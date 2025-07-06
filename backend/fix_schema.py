#!/usr/bin/env python3
"""
Script to automatically add missing authentication columns to the users table.
"""

from sqlalchemy import create_engine, text
from database import settings

def fix_users_table():
    """Add missing authentication columns to the users table"""
    
    engine = create_engine(settings.database_url)
    
    # SQL commands to add missing columns
    alter_commands = [
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
        
        print("✅ Successfully updated users table schema!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding missing authentication columns to users table...")
    print("=" * 60)
    
    success = fix_users_table()
    
    if success:
        print("\n🎉 Database schema updated successfully!")
        print("You can now run the authentication tests.")
    else:
        print("\n💥 Schema update failed. Check the error messages above.") 