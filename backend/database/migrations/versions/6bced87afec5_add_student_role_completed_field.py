"""add_student_role_completed_field

Revision ID: 6bced87afec5
Revises: 7b088aebd544
Create Date: 2025-09-26 11:45:29.639880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bced87afec5'
down_revision = '7b088aebd544'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add student_role_completed field to scenarios table
    connection = op.get_bind()
    
    # Check if column already exists
    result = connection.execute(sa.text("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = 'scenarios' 
        AND column_name = 'student_role_completed'
    """))
    
    if result.scalar() == 0:
        # Add the column
        op.add_column('scenarios', sa.Column('student_role_completed', sa.Boolean(), nullable=True))
        
        # Set default values for existing records
        op.execute("UPDATE scenarios SET student_role_completed = FALSE WHERE student_role_completed IS NULL")
        
        # Make column NOT NULL with default FALSE
        op.alter_column('scenarios', 'student_role_completed', nullable=False, server_default='false')
        
        # Update existing scenarios that have a student_role to mark student_role_completed as true
        op.execute("""
            UPDATE scenarios 
            SET student_role_completed = TRUE 
            WHERE student_role IS NOT NULL 
            AND student_role != ''
        """)


def downgrade() -> None:
    # Remove student_role_completed field from scenarios table
    op.drop_column('scenarios', 'student_role_completed')
