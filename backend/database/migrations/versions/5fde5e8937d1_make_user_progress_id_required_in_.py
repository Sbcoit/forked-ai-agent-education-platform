"""make_user_progress_id_required_in_student_simulation_instances

Revision ID: 5fde5e8937d1
Revises: 27f7d40373ea
Create Date: 2025-09-26 10:34:33.503998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fde5e8937d1'
down_revision = '27f7d40373ea'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, we need to ensure all existing records have a user_progress_id
    # This is a data migration step - we'll need to create UserProgress records
    # for any StudentSimulationInstance records that don't have one
    
    # Get all StudentSimulationInstance records without user_progress_id
    connection = op.get_bind()
    
    # Check if student_simulation_instances table exists
    table_exists = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'student_simulation_instances'
        )
    """)).scalar()
    
    if not table_exists:
        # Table doesn't exist yet, skip the data migration
        print("student_simulation_instances table doesn't exist, skipping data migration")
    else:
        # Check if there are any records without user_progress_id
        result = connection.execute(sa.text("""
            SELECT COUNT(*) FROM student_simulation_instances 
            WHERE user_progress_id IS NULL
        """))
        
        count = result.scalar()
        
        if count > 0:
            # Create UserProgress records for existing StudentSimulationInstance records
            # that don't have one
            connection.execute(sa.text("""
                INSERT INTO user_progress (user_id, scenario_id, simulation_status, created_at, updated_at)
                SELECT 
                    ssi.student_id,
                    cs.simulation_id,
                    'not_started',
                    NOW(),
                    NOW()
                FROM student_simulation_instances ssi
                JOIN cohort_simulations cs ON ssi.cohort_assignment_id = cs.id
                WHERE ssi.user_progress_id IS NULL
            """))
            
            # Update StudentSimulationInstance records to link to the new UserProgress records
            connection.execute(sa.text("""
                UPDATE student_simulation_instances 
                SET user_progress_id = up.id
                FROM user_progress up
                JOIN cohort_simulations cs ON student_simulation_instances.cohort_assignment_id = cs.id
                WHERE student_simulation_instances.user_progress_id IS NULL
                AND up.user_id = student_simulation_instances.student_id
                AND up.scenario_id = cs.simulation_id
            """))
    
    # Now make the column NOT NULL (only if table exists)
    if table_exists:
        op.alter_column('student_simulation_instances', 'user_progress_id',
                        existing_type=sa.Integer(),
                        nullable=False)


def downgrade() -> None:
    # Make the column nullable again
    op.alter_column('student_simulation_instances', 'user_progress_id',
                    existing_type=sa.Integer(),
                    nullable=True)
