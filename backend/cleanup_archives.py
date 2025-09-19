#!/usr/bin/env python3
"""
Archive Cleanup Script
Cleans up old archived user progress records to prevent database bloat
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.soft_deletion import SoftDeletionService
from database.connection import get_db


def main():
    """Main cleanup function"""
    print("🧹 Archive Cleanup Script")
    print("=" * 50)
    
    # Get database connection
    db_gen = get_db()
    db = next(db_gen, None)
    if db is None:
        print("❌ Failed to get database connection")
        return 1
    service = SoftDeletionService(db)
    service = SoftDeletionService(db)
    
    try:
        # Get current archive stats
        print("\n📊 Current Archive Statistics:")
        stats = service.get_archive_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Get user input for cleanup
        print("\n🗑️  Cleanup Options:")
        print("1. Clean archives older than 30 days (default)")
        print("2. Clean archives older than 7 days")
        print("3. Clean archives older than 90 days")
        print("4. Show stats only (no cleanup)")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            days_old = 30
        elif choice == "2":
            days_old = 7
        elif choice == "3":
            days_old = 90
        elif choice == "4":
            print("\n✅ Stats displayed. No cleanup performed.")
            return
        else:
            print("❌ Invalid choice. Using default (30 days).")
            days_old = 30
        
        # Perform cleanup
        print(f"\n🧹 Cleaning up archives older than {days_old} days...")
        cleaned_count = service.cleanup_old_archives(days_old)
        
        print(f"✅ Cleanup completed!")
        print(f"📊 Records cleaned up: {cleaned_count}")
        
        # Show updated stats
        print("\n📊 Updated Archive Statistics:")
        stats = service.get_archive_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return 1
    
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
