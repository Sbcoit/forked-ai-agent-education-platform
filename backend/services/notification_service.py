"""
In-app notification service for the AI Agent Education Platform
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import Notification, User, CohortInvitation, Cohort, CohortStudent
from database.schemas import NotificationResponse

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing in-app notifications"""
    
    def __init__(self):
        self.notification_types = {
            'cohort_invitation': {
                'title_template': 'New Cohort Invitation',
                'message_template': 'You have been invited to join "{cohort_title}" by {professor_name}',
                'priority': 'high'
            },
            'invitation_accepted': {
                'title_template': 'Student Joined Cohort',
                'message_template': '{student_name} has accepted your invitation to join "{cohort_title}"',
                'priority': 'medium'
            },
            'invitation_declined': {
                'title_template': 'Invitation Declined',
                'message_template': '{student_name} has declined your invitation to join "{cohort_title}"',
                'priority': 'medium'
            },
            'assignment_due': {
                'title_template': 'Assignment Due Soon',
                'message_template': 'Assignment "{assignment_title}" is due on {due_date}',
                'priority': 'high'
            },
            'assignment_overdue': {
                'title_template': 'Assignment Overdue',
                'message_template': 'Assignment "{assignment_title}" is now overdue',
                'priority': 'high'
            },
            'grade_posted': {
                'title_template': 'Grade Posted',
                'message_template': 'Your grade for "{assignment_title}" is now available',
                'priority': 'medium'
            },
            'cohort_update': {
                'title_template': 'Cohort Updated',
                'message_template': 'The cohort "{cohort_title}" has been updated',
                'priority': 'low'
            },
            'simulation_assigned': {
                'title_template': 'New Simulation Assigned',
                'message_template': 'A new simulation "{simulation_title}" has been assigned to your cohort "{cohort_title}"',
                'priority': 'high'
            },
            'professor_message': {
                'title_template': 'Message from Professor',
                'message_template': 'You have received a message from {professor_name}: "{message_subject}"',
                'priority': 'medium'
            },
            'student_reply': {
                'title_template': 'Student Reply',
                'message_template': '{student_name} has replied to your message: "{message_subject}"',
                'priority': 'medium'
            },
            'student_message': {
                'title_template': 'Message from Student',
                'message_template': 'You have received a message from {student_name}: "{message_subject}"',
                'priority': 'medium'
            },
            'message_sent': {
                'title_template': 'Message Sent',
                'message_template': 'You sent a message to {recipient_name}: "{message_subject}"',
                'priority': 'low'
            }
        }
    
    def create_notification(
        self, 
        db: Session, 
        user_id: int, 
        notification_type: str, 
        variables: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Notification]:
        """Create a new notification for a user"""
        try:
            if notification_type not in self.notification_types:
                logger.error(f"Unknown notification type: {notification_type}")
                return None
            
            template = self.notification_types[notification_type]
            title = template['title_template'].format(**variables)
            message = template['message_template'].format(**variables)
            
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data or {}
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            logger.info(f"Created notification for user {user_id}: {notification_type}")
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create notification for user {user_id}: {str(e)}")
            db.rollback()
            return None
    
    def create_cohort_invitation_notification(self, db: Session, invitation: CohortInvitation) -> Optional[Notification]:
        """Create notification for cohort invitation"""
        # Check if student exists in the system
        student = db.query(User).filter(
            User.email == invitation.student_email,
            User.role == 'student'
        ).first()
        
        if not student:
            logger.info(f"Student with email {invitation.student_email} not found, skipping notification")
            return None
        
        variables = {
            'cohort_title': invitation.cohort.title,
            'professor_name': invitation.professor.full_name
        }
        
        data = {
            'invitation_id': invitation.id,
            'cohort_id': invitation.cohort_id,
            'professor_id': invitation.professor_id
        }
        
        return self.create_notification(
            db, student.id, 'cohort_invitation', variables, data
        )
    
    def create_invitation_response_notification(self, db: Session, invitation: CohortInvitation, action: str) -> Optional[Notification]:
        """Create notification for invitation response"""
        if not invitation.student:
            logger.warning(f"Cannot create response notification: student not found for invitation {invitation.id}")
            return None
        
        notification_type = 'invitation_accepted' if action == 'accept' else 'invitation_declined'
        
        variables = {
            'student_name': invitation.student.full_name,
            'cohort_title': invitation.cohort.title
        }
        
        data = {
            'invitation_id': invitation.id,
            'cohort_id': invitation.cohort_id,
            'student_id': invitation.student_id
        }
        
        return self.create_notification(
            db, invitation.professor_id, notification_type, variables, data
        )
    
    def create_assignment_due_notification(self, db: Session, student_id: int, assignment_title: str, due_date: datetime) -> Optional[Notification]:
        """Create notification for assignment due soon"""
        variables = {
            'assignment_title': assignment_title,
            'due_date': due_date.strftime('%B %d, %Y at %I:%M %p')
        }
        
        return self.create_notification(
            db, student_id, 'assignment_due', variables
        )
    
    def create_grade_posted_notification(self, db: Session, student_id: int, assignment_title: str, cohort_title: str) -> Optional[Notification]:
        """Create notification for grade posted"""
        variables = {
            'assignment_title': assignment_title,
            'cohort_title': cohort_title
        }
        
        data = {
            'student_id': student_id
        }
        
        return self.create_notification(
            db, student_id, 'grade_posted', variables, data
        )
    
    def create_simulation_assignment_notification(
        self, 
        db: Session, 
        student_id: int, 
        cohort_simulation, 
        scenario, 
        cohort
    ) -> Optional[Notification]:
        """Create notification for simulation assignment"""
        variables = {
            'simulation_title': scenario.title,
            'cohort_title': cohort.title
        }
        
        data = {
            'cohort_simulation_id': cohort_simulation.id,
            'simulation_id': scenario.id,
            'cohort_id': cohort.id,
            'due_date': cohort_simulation.due_date.isoformat() if cohort_simulation.due_date else None,
            'is_required': cohort_simulation.is_required
        }
        
        return self.create_notification(
            db, student_id, 'simulation_assigned', variables, data
        )
    
    def get_user_notifications(
        self, 
        db: Session, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    
    def mark_notification_read(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if not notification:
                return False
            
            notification.is_read = True
            db.commit()
            
            logger.info(f"Marked notification {notification_id} as read for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as read: {str(e)}")
            db.rollback()
            return False
    
    def mark_all_notifications_read(self, db: Session, user_id: int) -> bool:
        """Mark all notifications as read for a user"""
        try:
            updated = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).update({'is_read': True})
            
            db.commit()
            
            logger.info(f"Marked {updated} notifications as read for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark all notifications as read for user {user_id}: {str(e)}")
            db.rollback()
            return False
    
    def delete_old_notifications(self, db: Session, days_old: int = 30) -> int:
        """Delete notifications older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            deleted = db.query(Notification).filter(
                Notification.created_at < cutoff_date,
                Notification.is_read == True
            ).delete()
            
            db.commit()
            
            logger.info(f"Deleted {deleted} old notifications")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete old notifications: {str(e)}")
            db.rollback()
            return 0
    
    def create_bulk_assignment_due_notifications(self, db: Session, cohort_id: int, assignment_title: str, due_date: datetime) -> int:
        """Create notifications for all students in a cohort about assignment due"""
        try:
            # Get all approved students in the cohort
            students = db.query(User).join(CohortStudent).filter(
                CohortStudent.cohort_id == cohort_id,
                CohortStudent.status == 'approved',
                User.role == 'student'
            ).all()
            
            created_count = 0
            for student in students:
                notification = self.create_assignment_due_notification(
                    db, student.id, assignment_title, due_date
                )
                if notification:
                    created_count += 1
            
            logger.info(f"Created {created_count} assignment due notifications for cohort {cohort_id}")
            return created_count
            
        except Exception as e:
            logger.error(f"Failed to create bulk assignment notifications: {str(e)}")
            return 0
    
    def create_bulk_grade_notifications(self, db: Session, cohort_id: int, assignment_title: str) -> int:
        """Create notifications for all students in a cohort about grade posted"""
        try:
            # Get all approved students in the cohort
            students = db.query(User).join(CohortStudent).filter(
                CohortStudent.cohort_id == cohort_id,
                CohortStudent.status == 'approved',
                User.role == 'student'
            ).all()
            
            # Get cohort title
            cohort = db.query(Cohort).filter(Cohort.id == cohort_id).first()
            cohort_title = cohort.title if cohort else "Unknown Cohort"
            
            created_count = 0
            for student in students:
                notification = self.create_grade_posted_notification(
                    db, student.id, assignment_title, cohort_title
                )
                if notification:
                    created_count += 1
            
            logger.info(f"Created {created_count} grade posted notifications for cohort {cohort_id}")
            return created_count
            
        except Exception as e:
            logger.error(f"Failed to create bulk grade notifications: {str(e)}")
            return 0

# Global notification service instance
notification_service = NotificationService()

def create_cohort_invitation_notification(db: Session, invitation: CohortInvitation) -> Optional[Notification]:
    """Convenience function to create cohort invitation notification"""
    return notification_service.create_cohort_invitation_notification(db, invitation)

def create_invitation_response_notification(db: Session, invitation: CohortInvitation, action: str) -> Optional[Notification]:
    """Convenience function to create invitation response notification"""
    return notification_service.create_invitation_response_notification(db, invitation, action)

def get_user_notifications(db: Session, user_id: int, limit: int = 50, unread_only: bool = False) -> List[Notification]:
    """Convenience function to get user notifications"""
    return notification_service.get_user_notifications(db, user_id, limit=limit, unread_only=unread_only)

def get_unread_notification_count(db: Session, user_id: int) -> int:
    """Convenience function to get unread notification count"""
    return notification_service.get_unread_count(db, user_id)

def create_professor_message_notification(db: Session, professor: User, student: User, message_subject: str, cohort_id: Optional[int] = None) -> Optional[Notification]:
    """Convenience function to create professor message notification"""
    return notification_service.create_notification(
        db=db,
        user_id=student.id,
        notification_type='professor_message',
        variables={
            'professor_name': professor.full_name,
            'message_subject': message_subject
        },
        data={
            'professor_id': professor.id,
            'cohort_id': cohort_id,
            'message_type': 'professor_message'
        }
    )

def create_student_reply_notification(db: Session, student: User, professor: User, message_subject: str, cohort_id: Optional[int] = None) -> Optional[Notification]:
    """Convenience function to create student reply notification"""
    return notification_service.create_notification(
        db=db,
        user_id=professor.id,
        notification_type='student_reply',
        variables={
            'student_name': student.full_name,
            'message_subject': message_subject
        },
        data={
            'student_id': student.id,
            'cohort_id': cohort_id,
            'message_type': 'student_reply'
        }
    )

def create_message_sent_notification(db: Session, sender: User, recipient: User, message_subject: str, cohort_id: Optional[int] = None) -> Optional[Notification]:
    """Convenience function to create message sent notification"""
    return notification_service.create_notification(
        db=db,
        user_id=sender.id,
        notification_type='message_sent',
        variables={
            'recipient_name': recipient.full_name,
            'message_subject': message_subject
        },
        data={
            'recipient_id': recipient.id,
            'cohort_id': cohort_id,
            'message_type': 'message_sent'
        }
    )
