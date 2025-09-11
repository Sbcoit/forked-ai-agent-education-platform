"""enforce_user_data_separation

Revision ID: 40439b022f4a
Revises: 0cd3fc754e7a
Create Date: 2025-09-11 01:18:36.634052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40439b022f4a'
down_revision = '0cd3fc754e7a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Enforce user data separation by making user_id NOT NULL and adding performance indexes.
    
    This migration ensures:
    1. All simulations are tied to user accounts (user_id NOT NULL)
    2. Proper indexes for efficient user data queries
    3. Data separation between user accounts
    4. Performance optimization for user-specific queries
    """
    connection = op.get_bind()
    
    # Step 1: Clean up any existing NULL user_id values
    result = connection.execute(sa.text("SELECT COUNT(*) FROM user_progress WHERE user_id IS NULL"))
    null_count = result.scalar()
    
    if null_count > 0:
        print(f"WARNING: Found {null_count} user_progress records with NULL user_id")
        print("Cleaning up anonymous progress records...")
        
        # Delete all related data for anonymous progress
        connection.execute(sa.text("""
            DELETE FROM conversation_logs 
            WHERE user_progress_id IN (
                SELECT id FROM user_progress WHERE user_id IS NULL
            )
        """))
        
        connection.execute(sa.text("""
            DELETE FROM scene_progress 
            WHERE user_progress_id IN (
                SELECT id FROM user_progress WHERE user_id IS NULL
            )
        """))
        
        # Delete anonymous user_progress records
        connection.execute(sa.text("DELETE FROM user_progress WHERE user_id IS NULL"))
        print(f"Deleted {null_count} anonymous progress records")
    
    # Step 2: Make user_id NOT NULL to enforce data separation
    op.alter_column('user_progress', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    
    # Step 3: Add performance indexes for user data separation
    print("Adding indexes for user data separation...")
    
    # Index for user_progress queries by user_id
    op.create_index('idx_user_progress_user_id', 'user_progress', ['user_id'])
    
    # Composite index for user + scenario queries
    op.create_index('idx_user_progress_user_scenario', 'user_progress', ['user_id', 'scenario_id'])
    
    # Index for scene_progress by user (through user_progress)
    op.create_index('idx_scene_progress_user_progress', 'scene_progress', ['user_progress_id'])
    
    # Index for conversation_logs by user (through user_progress)
    op.create_index('idx_conversation_logs_user_progress', 'conversation_logs', ['user_progress_id'])
    
    # Index for session_memory by user
    op.create_index('idx_session_memory_user_progress', 'session_memory', ['user_progress_id'])
    
    # Index for conversation_summaries by user
    op.create_index('idx_conversation_summaries_user_progress', 'conversation_summaries', ['user_progress_id'])
    
    # Index for agent_sessions by user
    op.create_index('idx_agent_sessions_user_progress', 'agent_sessions', ['user_progress_id'])
    
    # Step 4: Add documentation
    op.execute(sa.text("""
        COMMENT ON COLUMN user_progress.user_id IS 
        'User ID - REQUIRED for data separation and account isolation. All simulations must be tied to user accounts.'
    """))
    
    print("✅ User data separation enforced successfully!")
    print("✅ All simulations now require user accounts")
    print("✅ Performance indexes added for user-specific queries")


def downgrade() -> None:
    """
    Revert user data separation (NOT RECOMMENDED for production).
    
    WARNING: This will allow anonymous simulations again, breaking data separation.
    """
    print("WARNING: Reverting user data separation - this may cause security issues!")
    
    # Remove indexes
    op.drop_index('idx_agent_sessions_user_progress', 'agent_sessions')
    op.drop_index('idx_conversation_summaries_user_progress', 'conversation_summaries')
    op.drop_index('idx_session_memory_user_progress', 'session_memory')
    op.drop_index('idx_conversation_logs_user_progress', 'conversation_logs')
    op.drop_index('idx_scene_progress_user_progress', 'scene_progress')
    op.drop_index('idx_user_progress_user_scenario', 'user_progress')
    op.drop_index('idx_user_progress_user_id', 'user_progress')
    
    # Remove comment
    op.execute(sa.text("COMMENT ON COLUMN user_progress.user_id IS NULL"))
    
    # Revert user_id to nullable
    op.alter_column('user_progress', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)
