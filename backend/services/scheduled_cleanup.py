"""
Scheduled Cleanup Service
Automatically cleans up old archived records on a schedule
"""

import schedule
import time
from datetime import datetime
from services.soft_deletion import SoftDeletionService
from database.connection import get_db


class ScheduledCleanupService:
    """Service for scheduled cleanup of archived records"""
    
    def __init__(self):
        self.cleanup_days = 30  # Default: clean archives older than 30 days
    
    def set_cleanup_days(self, days: int):
        """Set the number of days after which to clean up archives"""
        self.cleanup_days = days
    
    def run_cleanup(self):
        """Run the cleanup process"""
        print(f"[{datetime.now()}] 🧹 Starting scheduled cleanup...")
        
        try:
            db = next(get_db())
            service = SoftDeletionService(db)
            
            # Get stats before cleanup
            stats_before = service.get_archive_stats()
            print(f"📊 Archives before cleanup: {stats_before['total_archives']}")
            
            # Run cleanup
            cleaned_count = service.cleanup_old_archives(self.cleanup_days)
            
            # Get stats after cleanup
            stats_after = service.get_archive_stats()
            print(f"📊 Archives after cleanup: {stats_after['total_archives']}")
            print(f"✅ Cleaned up {cleaned_count} records")
            
            db.close()
            
        except Exception as e:
            print(f"❌ Error during scheduled cleanup: {e}")
    
    def start_daily_cleanup(self):
        """Start daily cleanup at 2 AM"""
        schedule.every().day.at("02:00").do(self.run_cleanup)
        print("📅 Daily cleanup scheduled for 2:00 AM")
    
    def start_weekly_cleanup(self):
        """Start weekly cleanup on Sundays at 2 AM"""
        schedule.every().sunday.at("02:00").do(self.run_cleanup)
        print("📅 Weekly cleanup scheduled for Sundays at 2:00 AM")
    
    def start_monthly_cleanup(self):
        """Start monthly cleanup on the 1st at 2 AM"""
        schedule.every().month.do(self.run_cleanup)
        print("📅 Monthly cleanup scheduled for the 1st at 2:00 AM")
    
    def run_scheduler(self):
        """Run the scheduler (blocking)"""
        print("🔄 Starting cleanup scheduler...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped")


def main():
    """Main function for running scheduled cleanup"""
    cleanup_service = ScheduledCleanupService()
    
    # Set cleanup to 30 days (archives older than 30 days)
    cleanup_service.set_cleanup_days(30)
    
    # Schedule daily cleanup
    cleanup_service.start_daily_cleanup()
    
    # Run the scheduler
    cleanup_service.run_scheduler()


if __name__ == "__main__":
    main()
