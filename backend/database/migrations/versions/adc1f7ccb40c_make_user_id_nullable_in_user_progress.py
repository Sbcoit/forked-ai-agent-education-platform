"""make_user_id_nullable_in_user_progress

Revision ID: adc1f7ccb40c
Revises: 0001
Create Date: 2025-09-10 13:02:56.786754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adc1f7ccb40c'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, check if there are any existing user_progress records with NULL user_id
    # This is a safety check to ensure we don't lose data
    connection = op.get_bind()
    
    # Check for any existing NULL user_id values (shouldn't exist in current schema)
    result = connection.execute(sa.text("SELECT COUNT(*) FROM user_progress WHERE user_id IS NULL"))
    null_count = result.scalar() or 0
    if null_count > 0:
        print(f"WARNING: Found {null_count} existing NULL user_id values in user_progress table")
    
    # Make user_id nullable in user_progress table
    op.alter_column('user_progress', 'user_id',
                   existing_type=sa.Integer(),
                   nullable=True)
    
    # Add a comment to document the change
    op.execute(sa.text("COMMENT ON COLUMN user_progress.user_id IS 'User ID for authenticated users, NULL for anonymous users'"))


def downgrade() -> None:
    # Before making user_id NOT NULL, we need to handle any NULL values
    connection = op.get_bind()
    
    # Check for NULL user_id values
    result = connection.execute(sa.text("SELECT COUNT(*) FROM user_progress WHERE user_id IS NULL"))
    null_count = result.scalar()
    
    if null_count > 0:
        # Option 1: Delete anonymous progress (recommended for downgrade)
        print(f"WARNING: Found {null_count} user_progress records with NULL user_id")
        print("Deleting anonymous progress records to allow downgrade...")
        
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
    
    # Remove the comment
    op.execute(sa.text("COMMENT ON COLUMN user_progress.user_id IS NULL"))
    
    # Revert user_id to not nullable in user_progress table
    op.alter_column('user_progress', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)
