"""
Student notification API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from database.connection import get_db
from database.models import User, CohortInvitation, Notification
from database.schemas import (
    InvitationResponse,
    CohortInvitationResponse,
    NotificationResponse
)
from middleware.role_auth import require_student
from services.email_service import email_service
from services.notification_service import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student", tags=["student-notifications"])

@router.get("/invitations")
async def get_pending_invitations(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get pending invitations for the current student"""
    
    # Get invitations by email (for students not yet registered)
    email_invitations = db.query(CohortInvitation).filter(
        CohortInvitation.student_email == current_user.email,
        CohortInvitation.status == 'pending'
    ).all()
    
    # Get invitations by user ID (for registered students)
    user_invitations = db.query(CohortInvitation).filter(
        CohortInvitation.student_id == current_user.id,
        CohortInvitation.status == 'pending'
    ).all()
    
    # Combine and deduplicate
    all_invitations = email_invitations + user_invitations
    unique_invitations = list({inv.id: inv for inv in all_invitations}.values())
    
    return {
        "invitations": [CohortInvitationResponse.from_orm(inv) for inv in unique_invitations]
    }

@router.post("/invitations/{invitation_id}/respond")
async def respond_to_invitation(
    invitation_id: int,
    response: InvitationResponse,
    request,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Respond to a cohort invitation (accept or decline)"""
    
    # Find the invitation
    invitation = db.query(CohortInvitation).filter(
        CohortInvitation.id == invitation_id,
        CohortInvitation.status == 'pending'
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already responded to"
        )
    
    # Verify the invitation is for this student
    if (invitation.student_email != current_user.email and 
        invitation.student_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is not for you"
        )
    
    # Check if invitation is expired
    from datetime import datetime
    if invitation.expires_at < datetime.utcnow():
        invitation.status = 'expired'
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has expired"
        )
    
    # Update invitation status
    invitation.status = 'accepted' if response.action == 'accept' else 'declined'
    invitation.student_id = current_user.id  # Link the student ID
    db.commit()
    
    # If accepted, create cohort enrollment
    if response.action == 'accept':
        from database.models import CohortStudent
        enrollment = CohortStudent(
            cohort_id=invitation.cohort_id,
            student_id=current_user.id,
            status='approved',
            enrollment_date=datetime.utcnow()
        )
        db.add(enrollment)
        db.commit()
        
        logger.info(f"Student {current_user.id} joined cohort {invitation.cohort_id}")
    
    # Send notification to professor
    try:
        base_url = str(request.base_url).rstrip('/')
        await email_service.send_invitation_response(db, invitation, response.action, base_url)
        notification_service.create_invitation_response_notification(db, invitation, response.action)
        logger.info(f"Sent {response.action} notification for invitation {invitation_id}")
    except Exception as e:
        logger.error(f"Failed to send response notification: {str(e)}")
    
    return {
        "message": f"Invitation {response.action}ed successfully",
        "action": response.action,
        "cohort_id": invitation.cohort_id
    }

@router.get("/notifications")
async def get_notifications(
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get notifications for the current student"""
    
    notifications = notification_service.get_user_notifications(
        db, current_user.id, limit=limit, offset=offset, unread_only=unread_only
    )
    
    return {
        "notifications": [NotificationResponse.from_orm(notif) for notif in notifications],
        "total": len(notifications)
    }

@router.get("/notifications/unread-count")
async def get_unread_notification_count(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    
    count = notification_service.get_unread_count(db, current_user.id)
    
    return {"unread_count": count}

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    
    success = notification_service.mark_notification_read(db, notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    
    success = notification_service.mark_all_notifications_read(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notifications as read"
        )
    
    return {"message": "All notifications marked as read"}

@router.get("/invitations/{invitation_token}")
async def get_invitation_by_token(
    invitation_token: str,
    db: Session = Depends(get_db)
):
    """Get invitation details by token (for email links)"""
    
    invitation = db.query(CohortInvitation).filter(
        CohortInvitation.invitation_token == invitation_token,
        CohortInvitation.status == 'pending'
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired"
        )
    
    # Check if invitation is expired
    from datetime import datetime
    if invitation.expires_at < datetime.utcnow():
        invitation.status = 'expired'
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has expired"
        )
    
    return {
        "invitation": CohortInvitationResponse.from_orm(invitation),
        "cohort": {
            "id": invitation.cohort.id,
            "title": invitation.cohort.title,
            "description": invitation.cohort.description,
            "course_code": invitation.cohort.course_code,
            "semester": invitation.cohort.semester,
            "year": invitation.cohort.year
        },
        "professor": {
            "id": invitation.professor.id,
            "full_name": invitation.professor.full_name,
            "email": invitation.professor.email
        }
    }

@router.post("/invitations/{invitation_token}/respond")
async def respond_to_invitation_by_token(
    invitation_token: str,
    response: InvitationResponse,
    request,
    db: Session = Depends(get_db)
):
    """Respond to invitation by token (for non-authenticated users)"""
    
    # Find the invitation
    invitation = db.query(CohortInvitation).filter(
        CohortInvitation.invitation_token == invitation_token,
        CohortInvitation.status == 'pending'
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already responded to"
        )
    
    # Check if invitation is expired
    from datetime import datetime
    if invitation.expires_at < datetime.utcnow():
        invitation.status = 'expired'
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has expired"
        )
    
    # Update invitation status
    invitation.status = 'accepted' if response.action == 'accept' else 'declined'
    db.commit()
    
    # If accepted, we need to check if the student exists in the system
    if response.action == 'accept':
        # Check if student exists with this email
        student = db.query(User).filter(
            User.email == invitation.student_email,
            User.role == 'student'
        ).first()
        
        if student:
            # Create cohort enrollment
            from database.models import CohortStudent
            enrollment = CohortStudent(
                cohort_id=invitation.cohort_id,
                student_id=student.id,
                status='approved',
                enrollment_date=datetime.utcnow()
            )
            db.add(enrollment)
            invitation.student_id = student.id
            db.commit()
            
            logger.info(f"Student {student.id} joined cohort {invitation.cohort_id}")
        else:
            # Student doesn't exist yet, they'll need to register first
            logger.info(f"Invitation accepted but student {invitation.student_email} not found in system")
    
    # Send notification to professor
    try:
        base_url = str(request.base_url).rstrip('/')
        await email_service.send_invitation_response(db, invitation, response.action, base_url)
        notification_service.create_invitation_response_notification(db, invitation, response.action)
        logger.info(f"Sent {response.action} notification for invitation {invitation.id}")
    except Exception as e:
        logger.error(f"Failed to send response notification: {str(e)}")
    
    return {
        "message": f"Invitation {response.action}ed successfully",
        "action": response.action,
        "cohort_id": invitation.cohort_id,
        "requires_registration": response.action == 'accept' and not invitation.student_id
    }
