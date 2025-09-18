"""add_unique_id_to_scenarios

Revision ID: a6f09d4d781a
Revises: 010b1bf83ef4
Create Date: 2025-09-18 14:14:31.882707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6f09d4d781a'
down_revision = '010b1bf83ef4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unique_id column to scenarios table
    op.add_column('scenarios', sa.Column('unique_id', sa.String(), nullable=True))
    
    # Create index for unique_id
    op.create_index('ix_scenarios_unique_id', 'scenarios', ['unique_id'], unique=True)
    
    # Generate unique IDs for existing scenarios
    from sqlalchemy import text
    import secrets
    
    def generate_scenario_id():
        return f"SC-{secrets.token_urlsafe(8).upper()}"
    
    # Get all existing scenarios
    connection = op.get_bind()
    result = connection.execute(text("SELECT id FROM scenarios"))
    scenario_ids = [row[0] for row in result]
    
    # Generate unique IDs for existing scenarios
    for scenario_id in scenario_ids:
        unique_id = generate_scenario_id()
        connection.execute(
            text("UPDATE scenarios SET unique_id = :unique_id WHERE id = :id"),
            {"unique_id": unique_id, "id": scenario_id}
        )
    
    # Make unique_id NOT NULL after populating existing records
    op.alter_column('scenarios', 'unique_id', nullable=False)


def downgrade() -> None:
    # Drop the unique_id column
    op.drop_index('ix_scenarios_unique_id', table_name='scenarios')
    op.drop_column('scenarios', 'unique_id')
