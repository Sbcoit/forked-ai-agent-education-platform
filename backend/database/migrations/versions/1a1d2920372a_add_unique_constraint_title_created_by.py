"""add_unique_constraint_title_created_by

Revision ID: 1a1d2920372a
Revises: 6bced87afec5
Create Date: 2025-09-26 12:11:50.199227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a1d2920372a'
down_revision = '6bced87afec5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unique constraint to prevent duplicate scenarios with same title by same user
    # First, remove any existing duplicates by keeping only the most recent one
    connection = op.get_bind()
    
    # Find and remove duplicate scenarios (keep the most recent one)
    result = connection.execute(sa.text("""
        WITH duplicates AS (
            SELECT id, title, created_by, 
                   ROW_NUMBER() OVER (PARTITION BY title, created_by ORDER BY updated_at DESC) as rn
            FROM scenarios 
            WHERE deleted_at IS NULL
        )
        SELECT id FROM duplicates WHERE rn > 1
    """))
    
    duplicate_ids = [row[0] for row in result.fetchall()]
    if duplicate_ids:
        print(f"Found {len(duplicate_ids)} duplicate scenarios to remove")
        # Soft delete duplicates
        connection.execute(sa.text("""
            UPDATE scenarios 
            SET deleted_at = NOW(), deletion_reason = 'Duplicate removal for unique constraint'
            WHERE id = ANY(:duplicate_ids)
        """), {"duplicate_ids": duplicate_ids})
    
    # Add the unique constraint
    op.create_unique_constraint(
        'unique_title_per_user',
        'scenarios',
        ['title', 'created_by']
    )


def downgrade() -> None:
    # Remove the unique constraint
    op.drop_constraint('unique_title_per_user', 'scenarios', type_='unique')
