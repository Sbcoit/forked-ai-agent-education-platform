"""add_cohorts_tables

Revision ID: 20241220_120000
Revises: fix_vector_embeddings_column
Create Date: 2024-12-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20241220_120000'
down_revision = 'fix_vector_embeddings_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cohorts table
    op.create_table('cohorts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('course_code', sa.String(), nullable=True),
        sa.Column('semester', sa.String(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('max_students', sa.Integer(), nullable=True),
        sa.Column('auto_approve', sa.Boolean(), nullable=True),
        sa.Column('allow_self_enrollment', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_cohorts_created_by', 'cohorts', ['created_by'], unique=False)
    op.create_index('idx_cohorts_active', 'cohorts', ['is_active'], unique=False)
    op.create_index('idx_cohorts_year', 'cohorts', ['year'], unique=False)
    op.create_index('idx_cohorts_course_code', 'cohorts', ['course_code'], unique=False)
    op.create_index(op.f('ix_cohorts_id'), 'cohorts', ['id'], unique=False)
    op.create_index(op.f('ix_cohorts_title'), 'cohorts', ['title'], unique=False)

    # Create cohort_students table
    op.create_table('cohort_students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cohort_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('enrollment_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['cohort_id'], ['cohorts.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_cohort_students_cohort_id', 'cohort_students', ['cohort_id'], unique=False)
    op.create_index('idx_cohort_students_student_id', 'cohort_students', ['student_id'], unique=False)
    op.create_index('idx_cohort_students_status', 'cohort_students', ['status'], unique=False)
    op.create_index('idx_cohort_students_enrollment_date', 'cohort_students', ['enrollment_date'], unique=False)
    op.create_index(op.f('ix_cohort_students_id'), 'cohort_students', ['id'], unique=False)

    # Create cohort_simulations table
    op.create_table('cohort_simulations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cohort_id', sa.Integer(), nullable=False),
        sa.Column('simulation_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['cohort_id'], ['cohorts.id'], ),
        sa.ForeignKeyConstraint(['simulation_id'], ['user_progress.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_cohort_simulations_cohort_id', 'cohort_simulations', ['cohort_id'], unique=False)
    op.create_index('idx_cohort_simulations_simulation_id', 'cohort_simulations', ['simulation_id'], unique=False)
    op.create_index('idx_cohort_simulations_assigned_by', 'cohort_simulations', ['assigned_by'], unique=False)
    op.create_index('idx_cohort_simulations_due_date', 'cohort_simulations', ['due_date'], unique=False)
    op.create_index(op.f('ix_cohort_simulations_id'), 'cohort_simulations', ['id'], unique=False)


def downgrade() -> None:
    # Drop cohort_simulations table
    op.drop_index(op.f('ix_cohort_simulations_id'), table_name='cohort_simulations')
    op.drop_index('idx_cohort_simulations_due_date', table_name='cohort_simulations')
    op.drop_index('idx_cohort_simulations_assigned_by', table_name='cohort_simulations')
    op.drop_index('idx_cohort_simulations_simulation_id', table_name='cohort_simulations')
    op.drop_index('idx_cohort_simulations_cohort_id', table_name='cohort_simulations')
    op.drop_table('cohort_simulations')

    # Drop cohort_students table
    op.drop_index(op.f('ix_cohort_students_id'), table_name='cohort_students')
    op.drop_index('idx_cohort_students_enrollment_date', table_name='cohort_students')
    op.drop_index('idx_cohort_students_status', table_name='cohort_students')
    op.drop_index('idx_cohort_students_student_id', table_name='cohort_students')
    op.drop_index('idx_cohort_students_cohort_id', table_name='cohort_students')
    op.drop_table('cohort_students')

    # Drop cohorts table
    op.drop_index(op.f('ix_cohorts_title'), table_name='cohorts')
    op.drop_index(op.f('ix_cohorts_id'), table_name='cohorts')
    op.drop_index('idx_cohorts_course_code', table_name='cohorts')
    op.drop_index('idx_cohorts_year', table_name='cohorts')
    op.drop_index('idx_cohorts_active', table_name='cohorts')
    op.drop_index('idx_cohorts_created_by', table_name='cohorts')
    op.drop_table('cohorts')
