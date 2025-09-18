"""add_unique_id_to_cohorts

Revision ID: 0696b2513238
Revises: c021eebcfd98
Create Date: 2025-09-17 22:48:18.256110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0696b2513238'
down_revision = 'c021eebcfd98'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unique_id column to cohorts table
    op.add_column('cohorts', sa.Column('unique_id', sa.String(), nullable=True))
    
    # Create index for unique_id
    op.create_index('ix_cohorts_unique_id', 'cohorts', ['unique_id'], unique=True)
    
    # Generate short, user-friendly IDs for existing cohorts
    import secrets
    import string
    from sqlalchemy import text
    
    def generate_cohort_id():
        """Generate a short, user-friendly cohort ID like CH-MAN8P1QS"""
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(secrets.choice(chars) for _ in range(8))
        return f"CH-{random_part}"
    
    # Get all existing cohorts and generate unique IDs
    connection = op.get_bind()
    result = connection.execute(text("SELECT id FROM cohorts"))
    cohorts = result.fetchall()
    
    for cohort in cohorts:
        unique_id = generate_cohort_id()
        connection.execute(
            text("UPDATE cohorts SET unique_id = :unique_id WHERE id = :id"),
            {"unique_id": unique_id, "id": cohort.id}
        )
    
    # Make unique_id NOT NULL after populating existing records
    op.alter_column('cohorts', 'unique_id', nullable=False)


def downgrade() -> None:
    # Drop the unique_id column
    op.drop_index('ix_cohorts_unique_id', table_name='cohorts')
    op.drop_column('cohorts', 'unique_id')
