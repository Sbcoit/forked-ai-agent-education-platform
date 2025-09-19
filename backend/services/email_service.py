"""
Email notification service for the AI Agent Education Platform
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import EmailQueue, CohortInvitation, User
from database.schemas import EmailTemplate
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@ai-agent-education.com')
        self.from_name = os.getenv('FROM_NAME', 'AI Agent Education Platform')
        
        # Email templates
        self.templates = {
            'cohort_invitation': {
                'subject': 'Invitation to Join Cohort: {cohort_title}',
                'body': '''
                <html>
                <body>
                    <h2>You're Invited to Join a Cohort!</h2>
                    <p>Hello,</p>
                    <p><strong>{professor_name}</strong> has invited you to join the cohort <strong>"{cohort_title}"</strong>.</p>
                    <p><strong>Course:</strong> {course_code}</p>
                    <p><strong>Semester:</strong> {semester} {year}</p>
                    {message}
                    <p>To accept this invitation and join the cohort, please click the link below:</p>
                    <p><a href="{accept_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accept Invitation</a></p>
                    <p>Or copy and paste this URL into your browser: {accept_url}</p>
                    <p>This invitation will expire on {expires_date}.</p>
                    <hr>
                    <p><small>If you don't want to join this cohort, you can ignore this email or <a href="{decline_url}">decline the invitation</a>.</small></p>
                    <p><small>This is an automated message from the AI Agent Education Platform.</small></p>
                </body>
                </html>
                '''
            },
            'invitation_accepted': {
                'subject': 'Student Joined Your Cohort: {cohort_title}',
                'body': '''
                <html>
                <body>
                    <h2>Student Joined Your Cohort!</h2>
                    <p>Hello {professor_name},</p>
                    <p><strong>{student_name}</strong> has accepted your invitation and joined the cohort <strong>"{cohort_title}"</strong>.</p>
                    <p>You can now view their progress and assign simulations through the cohort management dashboard.</p>
                    <p><a href="{cohort_url}" style="background-color: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Cohort</a></p>
                    <hr>
                    <p><small>This is an automated message from the AI Agent Education Platform.</small></p>
                </body>
                </html>
                '''
            },
            'invitation_declined': {
                'subject': 'Student Declined Invitation: {cohort_title}',
                'body': '''
                <html>
                <body>
                    <h2>Invitation Declined</h2>
                    <p>Hello {professor_name},</p>
                    <p><strong>{student_name}</strong> has declined your invitation to join the cohort <strong>"{cohort_title}"</strong>.</p>
                    <p>You can send a new invitation or contact the student directly if needed.</p>
                    <hr>
                    <p><small>This is an automated message from the AI Agent Education Platform.</small></p>
                </body>
                </html>
                '''
            },
            'assignment_due': {
                'subject': 'Assignment Due Soon: {assignment_title}',
                'body': '''
                <html>
                <body>
                    <h2>Assignment Due Soon</h2>
                    <p>Hello {student_name},</p>
                    <p>This is a reminder that your assignment <strong>"{assignment_title}"</strong> is due on {due_date}.</p>
                    <p>Cohort: {cohort_title}</p>
                    <p>Don't forget to complete your simulation and submit your work!</p>
                    <p><a href="{assignment_url}" style="background-color: #FF9800; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Assignment</a></p>
                    <hr>
                    <p><small>This is an automated message from the AI Agent Education Platform.</small></p>
                </body>
                </html>
                '''
            },
            'grade_posted': {
                'subject': 'Grade Posted: {assignment_title}',
                'body': '''
                <html>
                <body>
                    <h2>Your Grade is Available</h2>
                    <p>Hello {student_name},</p>
                    <p>Your grade for <strong>"{assignment_title}"</strong> has been posted.</p>
                    <p>Cohort: {cohort_title}</p>
                    <p>Check your dashboard to view your grade and feedback.</p>
                    <p><a href="{grade_url}" style="background-color: #9C27B0; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Grade</a></p>
                    <hr>
                    <p><small>This is an automated message from the AI Agent Education Platform.</small></p>
                </body>
                </html>
                '''
            }
        }
    
    def format_template(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, str]:
        """Format email template with variables"""
        if template_name not in self.templates:
            raise ValueError(f"Unknown email template: {template_name}")
        
        template = self.templates[template_name]
        subject = template['subject'].format(**variables)
        body = template['body'].format(**variables)
        
        return {'subject': subject, 'body': body}
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def queue_email(self, db: Session, to_email: str, email_type: str, variables: Dict[str, Any], scheduled_at: Optional[datetime] = None) -> bool:
        """Queue email for sending"""
        try:
            # Format template
            formatted = self.format_template(email_type, variables)
            
            # Create email queue entry
            email_queue = EmailQueue(
                to_email=to_email,
                subject=formatted['subject'],
                body=formatted['body'],
                email_type=email_type,
                status='pending',
                scheduled_at=scheduled_at or datetime.utcnow()
            )
            
            db.add(email_queue)
            db.commit()
            
            logger.info(f"Email queued for {to_email} (type: {email_type})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue email for {to_email}: {str(e)}")
            return False
    
    async def send_cohort_invitation(self, db: Session, invitation: CohortInvitation, base_url: str) -> bool:
        """Send cohort invitation email"""
        # Get cohort and professor info
        cohort = invitation.cohort
        professor = invitation.professor
        
        # Create invitation URLs
        accept_url = f"{base_url}/auth/invitation/{invitation.invitation_token}/accept"
        decline_url = f"{base_url}/auth/invitation/{invitation.invitation_token}/decline"
        
        variables = {
            'professor_name': professor.full_name,
            'cohort_title': cohort.title,
            'course_code': cohort.course_code,
            'semester': cohort.semester,
            'year': cohort.year,
            'message': f"<p><strong>Message:</strong> {invitation.message}</p>" if invitation.message else "",
            'accept_url': accept_url,
            'decline_url': decline_url,
            'expires_date': invitation.expires_at.strftime('%B %d, %Y at %I:%M %p')
        }
        
        return await self.queue_email(db, invitation.student_email, 'cohort_invitation', variables)
    
    async def send_invitation_response(self, db: Session, invitation: CohortInvitation, action: str, base_url: str) -> bool:
        """Send invitation response notification to professor"""
        cohort = invitation.cohort
        professor = invitation.professor
        student = invitation.student
        
        if not student:
            logger.warning(f"Cannot send invitation response notification: student not found for invitation {invitation.id}")
            return False
        
        template_name = 'invitation_accepted' if action == 'accept' else 'invitation_declined'
        
        variables = {
            'professor_name': professor.full_name,
            'student_name': student.full_name,
            'cohort_title': cohort.title,
            'cohort_url': f"{base_url}/professor/cohorts/{cohort.id}"
        }
        
        return await self.queue_email(db, professor.email, template_name, variables)
    
    async def process_email_queue(self, db: Session, batch_size: int = 10) -> int:
        """Process pending emails in the queue"""
        try:
            # Get pending emails
            pending_emails = db.query(EmailQueue).filter(
                EmailQueue.status == 'pending',
                EmailQueue.scheduled_at <= datetime.utcnow()
            ).limit(batch_size).all()
            
            sent_count = 0
            
            for email_queue in pending_emails:
                try:
                    # Send email
                    success = self.send_email(
                        email_queue.to_email,
                        email_queue.subject,
                        email_queue.body
                    )
                    
                    if success:
                        email_queue.status = 'sent'
                        email_queue.sent_at = datetime.utcnow()
                        sent_count += 1
                    else:
                        email_queue.retry_count += 1
                        if email_queue.retry_count >= email_queue.max_retries:
                            email_queue.status = 'failed'
                        else:
                            # Schedule retry in 5 minutes
                            email_queue.scheduled_at = datetime.utcnow() + timedelta(minutes=5)
                    
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_queue.id}: {str(e)}")
                    email_queue.retry_count += 1
                    email_queue.error_message = str(e)
                    
                    if email_queue.retry_count >= email_queue.max_retries:
                        email_queue.status = 'failed'
                    
                    db.commit()
            
            logger.info(f"Processed {sent_count} emails from queue")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error processing email queue: {str(e)}")
            return 0

# Global email service instance
email_service = EmailService()

async def send_cohort_invitation_email(db: Session, invitation: CohortInvitation, base_url: str) -> bool:
    """Convenience function to send cohort invitation email"""
    return await email_service.send_cohort_invitation(db, invitation, base_url)

async def send_invitation_response_email(db: Session, invitation: CohortInvitation, action: str, base_url: str) -> bool:
    """Convenience function to send invitation response email"""
    return await email_service.send_invitation_response(db, invitation, action, base_url)

async def process_email_queue_task(db: Session) -> int:
    """Convenience function to process email queue"""
    return await email_service.process_email_queue(db)
