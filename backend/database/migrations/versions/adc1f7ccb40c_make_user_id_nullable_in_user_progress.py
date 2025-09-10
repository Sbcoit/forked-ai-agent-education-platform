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
    # Make user_id nullable in user_progress table
    op.alter_column('user_progress', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade() -> None:
    # Revert user_id to not nullable in user_progress table
    op.alter_column('user_progress', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)
