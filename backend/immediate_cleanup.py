#!/usr/bin/env python3
"""
Immediate Cleanup Script
Permanently deletes all archived data immediately
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.soft_deletion import SoftDeletionService
from database.connection import get_db


def immediate_cleanup():
    """Immediately delete all archived data"""
    print("🗑️ IMMEDIATE CLEANUP - DELETING ALL ARCHIVED DATA")
    print("=" * 60)
    
    # Get database connection
    db = next(get_db())
    service = SoftDeletionService(db)
    
    try:
        # Get stats before cleanup
        print("\n📊 BEFORE CLEANUP:")
        stats_before = service.get_archive_stats()
        for key, value in stats_before.items():
            print(f"  {key}: {value}")
        
        # Run immediate cleanup (0 days = delete everything)
        print("\n🧹 Running immediate cleanup (0 days old)...")
        cleaned_count = service.cleanup_old_archives(0)
        
        # Get stats after cleanup
        print("\n📊 AFTER CLEANUP:")
        stats_after = service.get_archive_stats()
        for key, value in stats_after.items():
            print(f"  {key}: {value}")
        
        print(f"\n✅ CLEANUP COMPLETE!")
        print(f"📊 Records permanently deleted: {cleaned_count}")
        
        return cleaned_count
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return 0
    
    finally:
        db.close()


def main():
    """Main function"""
    print(f"🚀 Starting immediate cleanup at {datetime.now()}")
    
    cleaned_count = immediate_cleanup()
    
    if cleaned_count > 0:
        print(f"\n🎉 Successfully deleted {cleaned_count} archived records!")
    else:
        print("\n📭 No archived records found to delete.")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
