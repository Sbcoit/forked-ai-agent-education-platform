"""add_soft_deletion_support

Revision ID: da94850967cc
Revises: 0001
Create Date: 2025-09-18 22:20:41.167213

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da94850967cc'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add soft deletion support to scenarios table
    op.add_column('scenarios', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('scenarios', sa.Column('deleted_by', sa.Integer(), nullable=True))
    op.add_column('scenarios', sa.Column('deletion_reason', sa.String(), nullable=True))
    
    # Add index for soft deletion queries
    op.create_index('idx_scenarios_deleted_at', 'scenarios', ['deleted_at'])
    op.create_index('idx_scenarios_active', 'scenarios', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NULL'))
    
    # Add foreign key for deleted_by
    op.create_foreign_key('fk_scenarios_deleted_by', 'scenarios', 'users', ['deleted_by'], ['id'])
    
    # Add soft deletion support to user_progress table
    op.add_column('user_progress', sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user_progress', sa.Column('archived_reason', sa.String(), nullable=True))
    
    # Add index for archived user progress
    op.create_index('idx_user_progress_archived_at', 'user_progress', ['archived_at'])
    op.create_index('idx_user_progress_active', 'user_progress', ['archived_at'], postgresql_where=sa.text('archived_at IS NULL'))
    
    # Create user_progress_archive table for long-term storage
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
    
    # Create indexes for archive table
    op.create_index('idx_user_progress_archive_scenario_id', 'user_progress_archive', ['scenario_id'])
    op.create_index('idx_user_progress_archive_user_id', 'user_progress_archive', ['user_id'])
    op.create_index('idx_user_progress_archive_archived_at', 'user_progress_archive', ['archived_at'])
    op.create_index('idx_user_progress_archive_original_id', 'user_progress_archive', ['original_user_progress_id'])


def downgrade() -> None:
    # Drop archive table
    op.drop_table('user_progress_archive')
    
    # Drop indexes
    op.drop_index('idx_user_progress_active', 'user_progress')
    op.drop_index('idx_user_progress_archived_at', 'user_progress')
    op.drop_index('idx_scenarios_active', 'scenarios')
    op.drop_index('idx_scenarios_deleted_at', 'scenarios')
    
    # Drop foreign key
    op.drop_constraint('fk_scenarios_deleted_by', 'scenarios', type_='foreignkey')
    
    # Drop columns
    op.drop_column('user_progress', 'archived_reason')
    op.drop_column('user_progress', 'archived_at')
    op.drop_column('scenarios', 'deletion_reason')
    op.drop_column('scenarios', 'deleted_by')
    op.drop_column('scenarios', 'deleted_at')
