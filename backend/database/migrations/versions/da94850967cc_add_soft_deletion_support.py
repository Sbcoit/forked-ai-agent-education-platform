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
    
    # Note: user_progress_archive table removed - using soft deletion instead


def downgrade() -> None:
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
