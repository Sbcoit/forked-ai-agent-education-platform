"""Add user_id field and invitation system tables

Revision ID: XXXX
Revises: df317c1d90a5
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'XXXX'
down_revision = 'df317c1d90a5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_id field to users table
    op.add_column('users', sa.Column('user_id', sa.String(length=15), nullable=True))
    
    # Create unique index on user_id
    op.create_index('idx_users_user_id', 'users', ['user_id'], unique=True)
    
    # Create index on role for role-based queries
    op.create_index('idx_users_role', 'users', ['role'])
    
    # Create cohort_invitations table
    op.create_table('cohort_invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cohort_id', sa.Integer(), nullable=False),
        sa.Column('professor_id', sa.Integer(), nullable=False),
        sa.Column('student_email', sa.String(length=255), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=True),
        sa.Column('invitation_token', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cohort_id'], ['cohorts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['professor_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for cohort_invitations
    op.create_index('idx_cohort_invitations_cohort_id', 'cohort_invitations', ['cohort_id'])
    op.create_index('idx_cohort_invitations_professor_id', 'cohort_invitations', ['professor_id'])
    op.create_index('idx_cohort_invitations_student_email', 'cohort_invitations', ['student_email'])
    op.create_index('idx_cohort_invitations_token', 'cohort_invitations', ['invitation_token'], unique=True)
    op.create_index('idx_cohort_invitations_status', 'cohort_invitations', ['status'])
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for notifications
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_type', 'notifications', ['type'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])
    
    # Create email_queue table
    op.create_table('email_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('to_email', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('email_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=False, default=3),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for email_queue
    op.create_index('idx_email_queue_status', 'email_queue', ['status'])
    op.create_index('idx_email_queue_scheduled_at', 'email_queue', ['scheduled_at'])
    op.create_index('idx_email_queue_email_type', 'email_queue', ['email_type'])
    
    # Add role validation constraint
    op.create_check_constraint(
        'ck_users_role_valid',
        'users',
        "role IN ('admin', 'teacher', 'professor', 'student', 'user')"
    )
    
    # Add status validation constraint for invitations
    op.create_check_constraint(
        'ck_cohort_invitations_status_valid',
        'cohort_invitations',
        "status IN ('pending', 'accepted', 'declined', 'expired')"
    )


def downgrade() -> None:
    # Drop constraints
    op.drop_constraint('ck_cohort_invitations_status_valid', 'cohort_invitations', type_='check')
    op.drop_constraint('ck_users_role_valid', 'users', type_='check')
    
    # Drop email_queue table
    op.drop_index('idx_email_queue_email_type', table_name='email_queue')
    op.drop_index('idx_email_queue_scheduled_at', table_name='email_queue')
    op.drop_index('idx_email_queue_status', table_name='email_queue')
    op.drop_table('email_queue')
    
    # Drop notifications table
    op.drop_index('idx_notifications_created_at', table_name='notifications')
    op.drop_index('idx_notifications_is_read', table_name='notifications')
    op.drop_index('idx_notifications_type', table_name='notifications')
    op.drop_index('idx_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
    
    # Drop cohort_invitations table
    op.drop_index('idx_cohort_invitations_status', table_name='cohort_invitations')
    op.drop_index('idx_cohort_invitations_token', table_name='cohort_invitations')
    op.drop_index('idx_cohort_invitations_student_email', table_name='cohort_invitations')
    op.drop_index('idx_cohort_invitations_professor_id', table_name='cohort_invitations')
    op.drop_index('idx_cohort_invitations_cohort_id', table_name='cohort_invitations')
    op.drop_table('cohort_invitations')
    
    # Drop user_id related indexes and column
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_user_id', table_name='users')
    op.drop_column('users', 'user_id')
