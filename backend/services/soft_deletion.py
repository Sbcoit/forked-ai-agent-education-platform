"""
Soft Deletion Service
Handles soft deletion of scenarios and user progress archiving
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from database.models import Scenario, UserProgress, User
from database.connection import get_db


class SoftDeletionService:
    """Service for handling soft deletion of scenarios and user progress"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def soft_delete_scenario(
        self, 
        scenario_id: int, 
        deleted_by: int, 
        reason: str = "User deletion"
    ) -> bool:
        """
        Soft delete a scenario by marking it as deleted
        
        Args:
            scenario_id: ID of scenario to delete
            deleted_by: ID of user performing deletion
            reason: Reason for deletion
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the scenario
            scenario = self.db.query(Scenario).filter(
                Scenario.id == scenario_id,
                Scenario.deleted_at.is_(None)  # Only get non-deleted scenarios
            ).first()
            
            if not scenario:
                return False
            
            # Store scenario info before deletion
            scenario_title = scenario.title
            
            # Archive related user progress
            self._archive_user_progress_for_scenario(scenario_id, reason)
            
            # Immediately clean up the archived data (permanent deletion)
            self._immediate_cleanup_scenario_archives(scenario_id)
            
            # Hard delete the scenario and all related records
            self._hard_delete_scenario(scenario_id)
            
            self.db.commit()
            
            print(f"[DEBUG] Successfully deleted scenario '{scenario_title}' (ID: {scenario_id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error soft deleting scenario {scenario_id}: {e}")
            return False
    
    def _archive_user_progress_for_scenario(self, scenario_id: int, reason: str):
        """Archive user progress for a deleted scenario"""
        try:
            # Get all user progress for this scenario
            user_progress_records = self.db.query(UserProgress).filter(
                UserProgress.scenario_id == scenario_id,
                UserProgress.archived_at.is_(None)  # Only get non-archived records
            ).all()
            
            for progress in user_progress_records:
                # Archive the record
                progress.archived_at = datetime.utcnow()
                progress.archived_reason = f"Scenario deleted: {reason}"
                
                # Create archive record with proper JSON serialization
                archive_data = {
                    'user_id': progress.user_id,
                    'scenario_id': progress.scenario_id,
                    'current_scene_id': progress.current_scene_id,
                    'simulation_status': progress.simulation_status,
                    'scenes_completed': json.dumps(progress.scenes_completed) if progress.scenes_completed else None,
                    'total_attempts': progress.total_attempts,
                    'hints_used': progress.hints_used,
                    'forced_progressions': progress.forced_progressions,
                    'orchestrator_data': json.dumps(progress.orchestrator_data) if progress.orchestrator_data else None,
                    'completion_percentage': progress.completion_percentage,
                    'total_time_spent': progress.total_time_spent,
                    'session_count': progress.session_count,
                    'final_score': progress.final_score,
                    'started_at': progress.started_at,
                    'completed_at': progress.completed_at,
                    'last_activity': progress.last_activity,
                    'created_at': progress.created_at,
                    'updated_at': progress.updated_at,
                    'archived_at': datetime.utcnow(),
                    'archived_reason': f"Scenario deleted: {reason}",
                    'original_user_progress_id': progress.id
                }
                
                # Insert into archive table
                self.db.execute(
                    text("""
                    INSERT INTO user_progress_archive 
                    (user_id, scenario_id, current_scene_id, simulation_status, scenes_completed,
                     total_attempts, hints_used, forced_progressions, orchestrator_data,
                     completion_percentage, total_time_spent, session_count, final_score,
                     started_at, completed_at, last_activity, created_at, updated_at,
                     archived_at, archived_reason, original_user_progress_id)
                    VALUES 
                    (:user_id, :scenario_id, :current_scene_id, :simulation_status, :scenes_completed,
                     :total_attempts, :hints_used, :forced_progressions, :orchestrator_data,
                     :completion_percentage, :total_time_spent, :session_count, :final_score,
                     :started_at, :completed_at, :last_activity, :created_at, :updated_at,
                     :archived_at, :archived_reason, :original_user_progress_id)
                    """),
                    archive_data
                )
            
        except Exception as e:
            print(f"Error archiving user progress for scenario {scenario_id}: {e}")
            raise
    
    def _immediate_cleanup_scenario_archives(self, scenario_id: int):
        """Immediately delete archived data for a specific scenario"""
        try:
            # Use the existing immediate cleanup function
            from services.immediate_cleanup import immediate_cleanup_scenario_archives
            
            deleted_count, stats_after = immediate_cleanup_scenario_archives(scenario_id)
            print(f"[DEBUG] Immediately deleted {deleted_count} archived records for scenario {scenario_id}")
            
        except Exception as e:
            print(f"Error during immediate cleanup for scenario {scenario_id}: {e}")
            raise
    
    
    def _hard_delete_scenario(self, scenario_id: int):
        """Actually delete the scenario and all related records from the database"""
        try:
            # Delete related records first (in proper order to avoid foreign key violations)
            
            # 1. Delete scene-persona relationships
            self.db.execute(
                text("DELETE FROM scene_personas WHERE scene_id IN (SELECT id FROM scenario_scenes WHERE scenario_id = :scenario_id)"),
                {'scenario_id': scenario_id}
            )
            
            # 2. Delete conversation logs
            self.db.execute(
                text("DELETE FROM conversation_logs WHERE scene_id IN (SELECT id FROM scenario_scenes WHERE scenario_id = :scenario_id)"),
                {'scenario_id': scenario_id}
            )
            
            # 3. Delete scene progress
            self.db.execute(
                text("DELETE FROM scene_progress WHERE scene_id IN (SELECT id FROM scenario_scenes WHERE scenario_id = :scenario_id)"),
                {'scenario_id': scenario_id}
            )
            
            # 4. Delete session memory
            self.db.execute(
                text("DELETE FROM session_memory WHERE scene_id IN (SELECT id FROM scenario_scenes WHERE scenario_id = :scenario_id)"),
                {'scenario_id': scenario_id}
            )
            
            # 5. Delete conversation summaries
            self.db.execute(
                text("DELETE FROM conversation_summaries WHERE scene_id IN (SELECT id FROM scenario_scenes WHERE scenario_id = :scenario_id)"),
                {'scenario_id': scenario_id}
            )
            
            # 6. Delete agent sessions
            self.db.execute(
                text("DELETE FROM agent_sessions WHERE user_progress_id IN (SELECT id FROM user_progress WHERE scenario_id = :scenario_id)"),
                {'scenario_id': scenario_id}
            )
            
            # 7. Delete user progress (if any remaining)
            self.db.execute(
                text("DELETE FROM user_progress WHERE scenario_id = :scenario_id"),
                {'scenario_id': scenario_id}
            )
            
            # 8. Delete scenario personas
            self.db.execute(
                text("DELETE FROM scenario_personas WHERE scenario_id = :scenario_id"),
                {'scenario_id': scenario_id}
            )
            
            # 9. Delete scenario scenes
            self.db.execute(
                text("DELETE FROM scenario_scenes WHERE scenario_id = :scenario_id"),
                {'scenario_id': scenario_id}
            )
            
            # 10. Delete scenario files
            self.db.execute(
                text("DELETE FROM scenario_files WHERE scenario_id = :scenario_id"),
                {'scenario_id': scenario_id}
            )
            
            # 11. Delete scenario reviews
            self.db.execute(
                text("DELETE FROM scenario_reviews WHERE scenario_id = :scenario_id"),
                {'scenario_id': scenario_id}
            )
            
            # 12. Finally delete the scenario itself
            result = self.db.execute(
                text("DELETE FROM scenarios WHERE id = :scenario_id"),
                {'scenario_id': scenario_id}
            )
            
            deleted_count = result.rowcount
            print(f"[DEBUG] Hard deleted {deleted_count} scenario record and all related data for scenario {scenario_id}")
            
        except Exception as e:
            print(f"Error during hard deletion for scenario {scenario_id}: {e}")
            raise
    
    def get_active_scenarios(self, user_id: Optional[int] = None) -> List[Scenario]:
        """Get all active (non-deleted) scenarios"""
        query = self.db.query(Scenario).filter(Scenario.deleted_at.is_(None))
        
        if user_id:
            query = query.filter(Scenario.created_by == user_id)
        
        return query.all()
    
    def get_deleted_scenarios(self, user_id: Optional[int] = None) -> List[Scenario]:
        """Get all deleted scenarios"""
        query = self.db.query(Scenario).filter(Scenario.deleted_at.isnot(None))
        
        if user_id:
            query = query.filter(Scenario.created_by == user_id)
        
        return query.all()
    
    def restore_scenario(self, scenario_id: int, restored_by: int) -> bool:
        """Restore a soft-deleted scenario"""
        try:
            scenario = self.db.query(Scenario).filter(
                Scenario.id == scenario_id,
                Scenario.deleted_at.isnot(None)
            ).first()
            
            if not scenario:
                return False
            
            # Restore the scenario
            scenario.deleted_at = None
            scenario.deleted_by = None
            scenario.deletion_reason = None
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error restoring scenario {scenario_id}: {e}")
            return False
    
    def cleanup_old_archives(self, days_old: int = 30) -> int:
        """
        Clean up old archived user progress records
        
        Args:
            days_old: Number of days after which to clean up archives
            
        Returns:
            int: Number of records cleaned up
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Count records to be deleted
            count = self.db.execute(
                text("""
                SELECT COUNT(*) FROM user_progress_archive 
                WHERE archived_at < :cutoff_date
                """),
                {'cutoff_date': cutoff_date}
            ).scalar()
            
            # Delete old archives
            self.db.execute(
                text("""
                DELETE FROM user_progress_archive 
                WHERE archived_at < :cutoff_date
                """),
                {'cutoff_date': cutoff_date}
            )
            
            self.db.commit()
            return count
            
        except Exception as e:
            self.db.rollback()
            print(f"Error cleaning up old archives: {e}")
            return 0
    
    def get_archive_stats(self) -> Dict[str, Any]:
        """Get statistics about archived user progress"""
        try:
            stats = self.db.execute(
                text("""
                SELECT 
                    COUNT(*) as total_archives,
                    COUNT(DISTINCT scenario_id) as unique_scenarios,
                    COUNT(DISTINCT user_id) as unique_users,
                    MIN(archived_at) as oldest_archive,
                    MAX(archived_at) as newest_archive
                FROM user_progress_archive
                """)
            ).fetchone()
            
            return {
                'total_archives': stats[0] or 0,
                'unique_scenarios': stats[1] or 0,
                'unique_users': stats[2] or 0,
                'oldest_archive': stats[3],
                'newest_archive': stats[4]
            }
            
        except Exception as e:
            print(f"Error getting archive stats: {e}")
            return {}


def soft_delete_scenario_endpoint(scenario_id: int, user_id: int, reason: str = "User deletion"):
    """Endpoint helper for soft deleting a scenario"""
    db = next(get_db())
    service = SoftDeletionService(db)
    return service.soft_delete_scenario(scenario_id, user_id, reason)
