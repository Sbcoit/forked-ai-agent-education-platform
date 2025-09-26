"""remove_user_progress_archive_table

Revision ID: bc34e83863ca
Revises: 5fde5e8937d1
Create Date: 2025-09-26 11:15:30.329289

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'bc34e83863ca'
down_revision = '5fde5e8937d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the user_progress_archive table since it's no longer used
    # Check if table exists first to avoid errors
    connection = op.get_bind()
    result = connection.execute(
        text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_progress_archive')")
    )
    table_exists = result.scalar()
    
    if table_exists:
        op.drop_table('user_progress_archive')


def downgrade() -> None:
    # Recreate the user_progress_archive table if needed for rollback
    op.create_table('user_progress_archive',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('scenario_id', sa.Integer(), nullable=True),
        sa.Column('current_scene_id', sa.Integer(), nullable=True),
        sa.Column('simulation_status', sa.String(), nullable=True),
        sa.Column('scenes_completed', sa.JSON(), nullable=True),
        sa.Column('total_attempts', sa.Integer(), nullable=True),
        sa.Column('hints_used', sa.Integer(), nullable=True),
        sa.Column('forced_progressions', sa.Integer(), nullable=True),
        sa.Column('orchestrator_data', sa.JSON(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=True),
        sa.Column('total_time_spent', sa.Integer(), nullable=True),
        sa.Column('session_count', sa.Integer(), nullable=True),
        sa.Column('final_score', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('archived_reason', sa.String(), nullable=True),
        sa.Column('original_user_progress_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate indexes for archive table
    op.create_index('idx_user_progress_archive_scenario_id', 'user_progress_archive', ['scenario_id'])
    op.create_index('idx_user_progress_archive_user_id', 'user_progress_archive', ['user_id'])
    op.create_index('idx_user_progress_archive_archived_at', 'user_progress_archive', ['archived_at'])
    op.create_index('idx_user_progress_archive_original_id', 'user_progress_archive', ['original_user_progress_id'])
