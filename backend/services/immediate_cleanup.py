"""
Immediate Cleanup Service
Programmatic functions for immediate data cleanup
"""

from datetime import datetime
from typing import Dict, Any, Tuple
from sqlalchemy import text
from services.soft_deletion import SoftDeletionService
from database.connection import get_db


def immediate_cleanup_all_archives() -> Tuple[int, Dict[str, Any], Dict[str, Any]]:
    """
    Immediately delete all archived data
    
    Returns:
        Tuple of (cleaned_count, stats_before, stats_after)
    """
    db = next(get_db())
    service = SoftDeletionService(db)
    
    try:
        # Get stats before cleanup
        stats_before = service.get_archive_stats()
        
        # Run immediate cleanup (0 days = delete everything)
        cleaned_count = service.cleanup_old_archives(0)
        
        # Get stats after cleanup
        stats_after = service.get_archive_stats()
        
        return cleaned_count, stats_before, stats_after
        
    except Exception as e:
        print(f"Error during immediate cleanup: {e}")
        return 0, {}, {}
    
    finally:
        db.close()


def immediate_cleanup_scenario_archives(scenario_id: int) -> Tuple[int, Dict[str, Any]]:
    """
    Immediately delete archived data for a specific scenario
    
    Args:
        scenario_id: ID of scenario to clean up
        
    Returns:
        Tuple of (cleaned_count, stats_after)
    """
    db = next(get_db())
    
    try:
        # Delete archived records for specific scenario
        result = db.execute(
            text("""
            DELETE FROM user_progress_archive 
            WHERE scenario_id = :scenario_id
            """),
            {'scenario_id': scenario_id}
        )
        
        cleaned_count = result.rowcount
        db.commit()
        
        # Get updated stats
        service = SoftDeletionService(db)
        stats_after = service.get_archive_stats()
        
        return cleaned_count, stats_after
        
    except Exception as e:
        print(f"Error cleaning up scenario {scenario_id}: {e}")
        return 0, {}
    
    finally:
        db.close()


def immediate_cleanup_user_archives(user_id: int) -> Tuple[int, Dict[str, Any]]:
    """
    Immediately delete archived data for a specific user
    
    Args:
        user_id: ID of user to clean up
        
    Returns:
        Tuple of (cleaned_count, stats_after)
    """
    db = next(get_db())
    
    try:
        # Delete archived records for specific user
        result = db.execute(
            text("""
            DELETE FROM user_progress_archive 
            WHERE user_id = :user_id
            """),
            {'user_id': user_id}
        )
        
        cleaned_count = result.rowcount
        db.commit()
        
        # Get updated stats
        service = SoftDeletionService(db)
        stats_after = service.get_archive_stats()
        
        return cleaned_count, stats_after
        
    except Exception as e:
        print(f"Error cleaning up user {user_id}: {e}")
        return 0, {}
    
    finally:
        db.close()


def get_cleanup_report() -> Dict[str, Any]:
    """
    Get a comprehensive cleanup report
    
    Returns:
        Dictionary with cleanup statistics and recommendations
    """
    db = next(get_db())
    service = SoftDeletionService(db)
    
    try:
        stats = service.get_archive_stats()
        
        # Calculate recommendations
        total_archives = stats.get('total_archives', 0)
        
        if total_archives == 0:
            recommendation = "No cleanup needed - no archived data found"
        elif total_archives < 10:
            recommendation = "Low archive count - cleanup not urgent"
        elif total_archives < 100:
            recommendation = "Moderate archive count - consider cleanup"
        else:
            recommendation = "High archive count - cleanup recommended"
        
        return {
            'archive_stats': stats,
            'recommendation': recommendation,
            'cleanup_available': total_archives > 0,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
    
    finally:
        db.close()


# Example usage functions
def example_immediate_cleanup():
    """Example of how to use immediate cleanup"""
    print("🗑️ Example: Immediate Cleanup")
    print("=" * 40)
    
    # Clean up all archives
    cleaned_count, stats_before, stats_after = immediate_cleanup_all_archives()
    
    print(f"Records deleted: {cleaned_count}")
    print(f"Before: {stats_before}")
    print(f"After: {stats_after}")


def example_scenario_cleanup(scenario_id: int):
    """Example of how to clean up specific scenario"""
    print(f"🗑️ Example: Scenario {scenario_id} Cleanup")
    print("=" * 40)
    
    cleaned_count, stats_after = immediate_cleanup_scenario_archives(scenario_id)
    
    print(f"Records deleted: {cleaned_count}")
    print(f"Updated stats: {stats_after}")


if __name__ == "__main__":
    # Run example
    example_immediate_cleanup()
