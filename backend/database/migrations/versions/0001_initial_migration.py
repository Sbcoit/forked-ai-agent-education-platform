"""Initial migration - Create all tables

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password_hash', sa.String(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('avatar_url', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('published_scenarios', sa.Integer(), nullable=True),
    sa.Column('total_simulations', sa.Integer(), nullable=True),
    sa.Column('reputation_score', sa.Float(), nullable=True),
    sa.Column('profile_public', sa.Boolean(), nullable=True),
    sa.Column('allow_contact', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index('idx_users_username', 'users', ['username'], unique=False)
    op.create_index('idx_users_role', 'users', ['role'], unique=False)
    op.create_index('idx_users_created_at', 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create scenarios table
    op.create_table('scenarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('challenge', sa.Text(), nullable=True),
    sa.Column('industry', sa.String(), nullable=True),
    sa.Column('learning_objectives', sa.JSON(), nullable=True),
    sa.Column('source_type', sa.String(), nullable=True),
    sa.Column('pdf_content', sa.Text(), nullable=True),
    sa.Column('student_role', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('difficulty_level', sa.String(), nullable=True),
    sa.Column('estimated_duration', sa.Integer(), nullable=True),
    sa.Column('tags', sa.JSON(), nullable=True),
    sa.Column('pdf_title', sa.String(), nullable=True),
    sa.Column('pdf_source', sa.String(), nullable=True),
    sa.Column('processing_version', sa.String(), nullable=True),
    sa.Column('rating_avg', sa.Float(), nullable=True),
    sa.Column('rating_count', sa.Integer(), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=True),
    sa.Column('is_template', sa.Boolean(), nullable=True),
    sa.Column('allow_remixes', sa.Boolean(), nullable=True),
    sa.Column('usage_count', sa.Integer(), nullable=True),
    sa.Column('clone_count', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenarios_id'), 'scenarios', ['id'], unique=False)
    op.create_index(op.f('ix_scenarios_title'), 'scenarios', ['title'], unique=False)
    op.create_index('idx_scenarios_title', 'scenarios', ['title'], unique=False)
    op.create_index('idx_scenarios_industry', 'scenarios', ['industry'], unique=False)
    op.create_index('idx_scenarios_is_public', 'scenarios', ['is_public'], unique=False)
    op.create_index('idx_scenarios_created_by', 'scenarios', ['created_by'], unique=False)
    op.create_index('idx_scenarios_created_at', 'scenarios', ['created_at'], unique=False)
    op.create_index('idx_scenarios_rating_avg', 'scenarios', ['rating_avg'], unique=False)

    # Create scenario_personas table
    op.create_table('scenario_personas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scenario_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('background', sa.Text(), nullable=True),
    sa.Column('correlation', sa.Text(), nullable=True),
    sa.Column('primary_goals', sa.JSON(), nullable=True),
    sa.Column('personality_traits', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenario_personas_id'), 'scenario_personas', ['id'], unique=False)
    op.create_index(op.f('ix_scenario_personas_name'), 'scenario_personas', ['name'], unique=False)

    # Create scenario_scenes table
    op.create_table('scenario_scenes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scenario_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('user_goal', sa.Text(), nullable=True),
    sa.Column('scene_order', sa.Integer(), nullable=True),
    sa.Column('estimated_duration', sa.Integer(), nullable=True),
    sa.Column('timeout_turns', sa.Integer(), nullable=True),
    sa.Column('success_metric', sa.String(), nullable=True),
    sa.Column('max_attempts', sa.Integer(), nullable=True),
    sa.Column('success_threshold', sa.Float(), nullable=True),
    sa.Column('goal_criteria', sa.JSON(), nullable=True),
    sa.Column('hint_triggers', sa.JSON(), nullable=True),
    sa.Column('scene_context', sa.Text(), nullable=True),
    sa.Column('persona_instructions', sa.JSON(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('image_prompt', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenario_scenes_id'), 'scenario_scenes', ['id'], unique=False)

    # Create scenario_files table
    op.create_table('scenario_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scenario_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(), nullable=False),
    sa.Column('file_path', sa.String(), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('file_type', sa.String(), nullable=True),
    sa.Column('original_content', sa.Text(), nullable=True),
    sa.Column('processed_content', sa.Text(), nullable=True),
    sa.Column('processing_status', sa.String(), nullable=True),
    sa.Column('processing_log', sa.JSON(), nullable=True),
    sa.Column('llamaparse_job_id', sa.String(), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenario_files_id'), 'scenario_files', ['id'], unique=False)

    # Create scenario_reviews table
    op.create_table('scenario_reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scenario_id', sa.Integer(), nullable=True),
    sa.Column('reviewer_id', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('review_text', sa.Text(), nullable=True),
    sa.Column('pros', sa.JSON(), nullable=True),
    sa.Column('cons', sa.JSON(), nullable=True),
    sa.Column('use_case', sa.String(), nullable=True),
    sa.Column('helpful_votes', sa.Integer(), nullable=True),
    sa.Column('total_votes', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenario_reviews_id'), 'scenario_reviews', ['id'], unique=False)

    # Create user_progress table
    op.create_table('user_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('scenario_id', sa.Integer(), nullable=False),
    sa.Column('current_scene_id', sa.Integer(), nullable=True),
    sa.Column('simulation_status', sa.String(), nullable=True),
    sa.Column('scenes_completed', sa.JSON(), nullable=True),
    sa.Column('total_attempts', sa.Integer(), nullable=True),
    sa.Column('hints_used', sa.Integer(), nullable=True),
    sa.Column('forced_progressions', sa.Integer(), nullable=True),
    sa.Column('orchestrator_data', sa.JSON(), nullable=True),
    sa.Column('completion_percentage', sa.Float(), nullable=True),
    sa.Column('total_time_spent', sa.Integer(), nullable=True),
    sa.Column('session_count', sa.Integer(), nullable=True),
    sa.Column('final_score', sa.Float(), nullable=True),
    sa.Column('started_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('last_activity', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['current_scene_id'], ['scenario_scenes.id'], ),
    sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_progress_id'), 'user_progress', ['id'], unique=False)

    # Create scene_progress table
    op.create_table('scene_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_progress_id', sa.Integer(), nullable=False),
    sa.Column('scene_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('attempts', sa.Integer(), nullable=True),
    sa.Column('hints_used', sa.Integer(), nullable=True),
    sa.Column('goal_achieved', sa.Boolean(), nullable=True),
    sa.Column('forced_progression', sa.Boolean(), nullable=True),
    sa.Column('time_spent', sa.Integer(), nullable=True),
    sa.Column('messages_sent', sa.Integer(), nullable=True),
    sa.Column('ai_responses', sa.Integer(), nullable=True),
    sa.Column('goal_achievement_score', sa.Float(), nullable=True),
    sa.Column('interaction_quality', sa.Float(), nullable=True),
    sa.Column('scene_feedback', sa.Text(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ),
    sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scene_progress_id'), 'scene_progress', ['id'], unique=False)

    # Create conversation_logs table
    op.create_table('conversation_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_progress_id', sa.Integer(), nullable=False),
    sa.Column('scene_id', sa.Integer(), nullable=False),
    sa.Column('message_type', sa.String(), nullable=False),
    sa.Column('sender_name', sa.String(), nullable=True),
    sa.Column('persona_id', sa.Integer(), nullable=True),
    sa.Column('message_content', sa.Text(), nullable=False),
    sa.Column('message_order', sa.Integer(), nullable=False),
    sa.Column('attempt_number', sa.Integer(), nullable=True),
    sa.Column('is_hint', sa.Boolean(), nullable=True),
    sa.Column('ai_context_used', sa.JSON(), nullable=True),
    sa.Column('ai_model_version', sa.String(), nullable=True),
    sa.Column('processing_time', sa.Float(), nullable=True),
    sa.Column('user_reaction', sa.String(), nullable=True),
    sa.Column('led_to_progress', sa.Boolean(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['persona_id'], ['scenario_personas.id'], ),
    sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ),
    sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_logs_id'), 'conversation_logs', ['id'], unique=False)

    # Create scene_personas association table
    op.create_table('scene_personas',
    sa.Column('scene_id', sa.Integer(), nullable=False),
    sa.Column('persona_id', sa.Integer(), nullable=False),
    sa.Column('involvement_level', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['persona_id'], ['scenario_personas.id'], ),
    sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ),
    sa.PrimaryKeyConstraint('scene_id', 'persona_id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('scene_personas')
    op.drop_index(op.f('ix_conversation_logs_id'), table_name='conversation_logs')
    op.drop_table('conversation_logs')
    op.drop_index(op.f('ix_scene_progress_id'), table_name='scene_progress')
    op.drop_table('scene_progress')
    op.drop_index(op.f('ix_user_progress_id'), table_name='user_progress')
    op.drop_table('user_progress')
    op.drop_index(op.f('ix_scenario_reviews_id'), table_name='scenario_reviews')
    op.drop_table('scenario_reviews')
    op.drop_index(op.f('ix_scenario_files_id'), table_name='scenario_files')
    op.drop_table('scenario_files')
    op.drop_index(op.f('ix_scenario_scenes_id'), table_name='scenario_scenes')
    op.drop_table('scenario_scenes')
    op.drop_index(op.f('ix_scenario_personas_name'), table_name='scenario_personas')
    op.drop_index(op.f('ix_scenario_personas_id'), table_name='scenario_personas')
    op.drop_table('scenario_personas')
    op.drop_index('idx_scenarios_rating_avg', table_name='scenarios')
    op.drop_index('idx_scenarios_created_at', table_name='scenarios')
    op.drop_index('idx_scenarios_created_by', table_name='scenarios')
    op.drop_index('idx_scenarios_is_public', table_name='scenarios')
    op.drop_index('idx_scenarios_industry', table_name='scenarios')
    op.drop_index('idx_scenarios_title', table_name='scenarios')
    op.drop_index(op.f('ix_scenarios_title'), table_name='scenarios')
    op.drop_index(op.f('ix_scenarios_id'), table_name='scenarios')
    op.drop_table('scenarios')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
