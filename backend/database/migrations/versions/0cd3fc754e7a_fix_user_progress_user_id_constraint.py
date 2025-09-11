"""fix_user_progress_user_id_constraint

Revision ID: 0cd3fc754e7a
Revises: add_langchain_integration
Create Date: 2025-09-11 01:10:20.158458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cd3fc754e7a'
down_revision = 'add_langchain_integration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Fix user_progress.user_id constraint to ensure simulations are properly constrained to user accounts.
    
    This migration:
    1. Removes any existing NULL user_id values (if any exist)
    2. Makes user_id NOT NULL to enforce the constraint
    3. Ensures all simulations are tied to user accounts
    """
    connection = op.get_bind()
    
    # First, check if there are any existing NULL user_id values
    result = connection.execute(sa.text("SELECT COUNT(*) FROM user_progress WHERE user_id IS NULL"))
    null_count = result.scalar()
    
    if null_count > 0:
        print(f"WARNING: Found {null_count} user_progress records with NULL user_id")
        print("Deleting anonymous progress records to enforce user constraint...")
        
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
    
    # Make user_id NOT NULL in user_progress table
    op.alter_column('user_progress', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    
    # Add a comment to document the constraint
    op.execute(sa.text("COMMENT ON COLUMN user_progress.user_id IS 'User ID - required to ensure simulations are constrained to user accounts'"))


def downgrade() -> None:
    """
    Revert user_progress.user_id to nullable (NOT RECOMMENDED for production).
    
    This downgrade allows anonymous simulations again, which may be a security concern.
    """
    # Remove the comment
    op.execute(sa.text("COMMENT ON COLUMN user_progress.user_id IS NULL"))
    
    # Revert user_id to nullable in user_progress table
    op.alter_column('user_progress', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)
