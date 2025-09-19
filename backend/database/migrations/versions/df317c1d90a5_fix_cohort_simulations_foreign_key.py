"""fix_cohort_simulations_foreign_key

Revision ID: df317c1d90a5
Revises: da94850967cc
Create Date: 2025-09-19 00:22:41.543203

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df317c1d90a5'
down_revision = 'da94850967cc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing foreign key constraint
    op.drop_constraint('cohort_simulations_simulation_id_fkey', 'cohort_simulations', type_='foreignkey')
    
    # Add the new foreign key constraint pointing to scenarios.id
    op.create_foreign_key('cohort_simulations_simulation_id_fkey', 'cohort_simulations', 'scenarios', ['simulation_id'], ['id'])


def downgrade() -> None:
    # Drop the new foreign key constraint
    op.drop_constraint('cohort_simulations_simulation_id_fkey', 'cohort_simulations', type_='foreignkey')
    
    # Restore the original foreign key constraint pointing to user_progress.id
    op.create_foreign_key('cohort_simulations_simulation_id_fkey', 'cohort_simulations', 'user_progress', ['simulation_id'], ['id'])
