"""consolidated_schema

Revision ID: 0001
Revises: 
Create Date: 2025-09-18 22:00:00.000000

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
        sa.Column('user_id', sa.String(15), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('google_id', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('published_scenarios', sa.Integer(), nullable=True),
        sa.Column('total_simulations', sa.Integer(), nullable=True),
        sa.Column('reputation_score', sa.Float(), nullable=True),
        sa.Column('profile_public', sa.Boolean(), nullable=True),
        sa.Column('allow_contact', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id'),
        sa.UniqueConstraint('username')
    )
    
    # Create scenarios table
    op.create_table('scenarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unique_id', sa.String(), nullable=False),
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
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('is_draft', sa.Boolean(), nullable=True),
        sa.Column('published_version_id', sa.Integer(), nullable=True),
        sa.Column('draft_of_id', sa.Integer(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('clone_count', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['draft_of_id'], ['scenarios.id'], ),
        sa.ForeignKeyConstraint(['published_version_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unique_id')
    )
    
    # Create cohorts table
    op.create_table('cohorts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unique_id', sa.String(), nullable=False),
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
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unique_id')
    )
    
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
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
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
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create scene_personas junction table
    op.create_table('scene_personas',
        sa.Column('scene_id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('involvement_level', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['persona_id'], ['scenario_personas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('scene_id', 'persona_id')
    )
    
    # Create user_progress table
    op.create_table('user_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
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
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['current_scene_id'], ['scenario_scenes.id'], ),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create remaining tables
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
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
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
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
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
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
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
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['persona_id'], ['scenario_personas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create vector_embeddings table
    op.create_table('vector_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(), nullable=False),
        sa.Column('embedding_vector', sa.JSON(), nullable=False),  # Will be Vector type in production
        sa.Column('embedding_model', sa.String(), nullable=False),
        sa.Column('embedding_dimension', sa.Integer(), nullable=False),
        sa.Column('original_content', sa.Text(), nullable=False),
        sa.Column('content_metadata', sa.JSON(), nullable=True),
        sa.Column('similarity_threshold', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('session_memory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('user_progress_id', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=True),
        sa.Column('memory_type', sa.String(), nullable=False),
        sa.Column('memory_content', sa.Text(), nullable=False),
        sa.Column('memory_metadata', sa.JSON(), nullable=True),
        sa.Column('parent_memory_id', sa.Integer(), nullable=True),
        sa.Column('related_persona_id', sa.Integer(), nullable=True),
        sa.Column('importance_score', sa.Float(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['parent_memory_id'], ['session_memory.id'], ),
        sa.ForeignKeyConstraint(['related_persona_id'], ['scenario_personas.id'], ),
        sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('conversation_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_progress_id', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=True),
        sa.Column('summary_type', sa.String(), nullable=False),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('key_points', sa.JSON(), nullable=True),
        sa.Column('learning_moments', sa.JSON(), nullable=True),
        sa.Column('insights', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('conversation_count', sa.Integer(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('summary_metadata', sa.JSON(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('agent_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('user_progress_id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=True),
        sa.Column('session_state', sa.JSON(), nullable=True),
        sa.Column('session_config', sa.JSON(), nullable=True),
        sa.Column('session_metadata', sa.JSON(), nullable=True),
        sa.Column('total_interactions', sa.Integer(), nullable=True),
        sa.Column('total_tokens_used', sa.Integer(), nullable=True),
        sa.Column('average_response_time', sa.Float(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    
    op.create_table('cache_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cache_key', sa.String(), nullable=False),
        sa.Column('cache_type', sa.String(), nullable=False),
        sa.Column('cache_data', sa.JSON(), nullable=False),
        sa.Column('cache_size', sa.Integer(), nullable=True),
        sa.Column('hit_count', sa.Integer(), nullable=True),
        sa.Column('miss_count', sa.Integer(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_expired', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cache_key')
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    op.create_index('idx_users_google_id', 'users', ['google_id'])
    op.create_index('idx_users_provider', 'users', ['provider'])
    
    op.create_index('idx_scenarios_title', 'scenarios', ['title'])
    op.create_index('idx_scenarios_industry', 'scenarios', ['industry'])
    op.create_index('idx_scenarios_is_public', 'scenarios', ['is_public'])
    op.create_index('idx_scenarios_created_by', 'scenarios', ['created_by'])
    op.create_index('idx_scenarios_created_at', 'scenarios', ['created_at'])
    op.create_index('idx_scenarios_rating_avg', 'scenarios', ['rating_avg'])
    
    op.create_index('idx_cohorts_created_by', 'cohorts', ['created_by'])
    op.create_index('idx_cohorts_active', 'cohorts', ['is_active'])
    op.create_index('idx_cohorts_year', 'cohorts', ['year'])
    op.create_index('idx_cohorts_course_code', 'cohorts', ['course_code'])
    
    op.create_index('idx_cohort_students_cohort_id', 'cohort_students', ['cohort_id'])
    op.create_index('idx_cohort_students_student_id', 'cohort_students', ['student_id'])
    op.create_index('idx_cohort_students_status', 'cohort_students', ['status'])
    op.create_index('idx_cohort_students_enrollment_date', 'cohort_students', ['enrollment_date'])
    
    op.create_index('idx_cohort_simulations_cohort_id', 'cohort_simulations', ['cohort_id'])
    op.create_index('idx_cohort_simulations_simulation_id', 'cohort_simulations', ['simulation_id'])
    op.create_index('idx_cohort_simulations_assigned_by', 'cohort_simulations', ['assigned_by'])
    op.create_index('idx_cohort_simulations_due_date', 'cohort_simulations', ['due_date'])
    
    op.create_index('idx_vector_embeddings_content_type', 'vector_embeddings', ['content_type'])
    op.create_index('idx_vector_embeddings_content_id', 'vector_embeddings', ['content_id'])
    op.create_index('idx_vector_embeddings_content_hash', 'vector_embeddings', ['content_hash'])
    op.create_index('idx_vector_embeddings_active', 'vector_embeddings', ['is_active'])
    op.create_index('idx_vector_embeddings_created_at', 'vector_embeddings', ['created_at'])
    
    op.create_index('idx_session_memory_session_id', 'session_memory', ['session_id'])
    op.create_index('idx_session_memory_user_progress_id', 'session_memory', ['user_progress_id'])
    op.create_index('idx_session_memory_scene_id', 'session_memory', ['scene_id'])
    op.create_index('idx_session_memory_type', 'session_memory', ['memory_type'])
    op.create_index('idx_session_memory_importance', 'session_memory', ['importance_score'])
    op.create_index('idx_session_memory_last_accessed', 'session_memory', ['last_accessed'])
    
    op.create_index('idx_conversation_summaries_user_progress_id', 'conversation_summaries', ['user_progress_id'])
    op.create_index('idx_conversation_summaries_scene_id', 'conversation_summaries', ['scene_id'])
    op.create_index('idx_conversation_summaries_type', 'conversation_summaries', ['summary_type'])
    op.create_index('idx_conversation_summaries_quality', 'conversation_summaries', ['quality_score'])
    op.create_index('idx_conversation_summaries_created_at', 'conversation_summaries', ['created_at'])
    
    op.create_index('idx_agent_sessions_session_id', 'agent_sessions', ['session_id'])
    op.create_index('idx_agent_sessions_user_progress_id', 'agent_sessions', ['user_progress_id'])
    op.create_index('idx_agent_sessions_agent_type', 'agent_sessions', ['agent_type'])
    op.create_index('idx_agent_sessions_active', 'agent_sessions', ['is_active'])
    op.create_index('idx_agent_sessions_last_activity', 'agent_sessions', ['last_activity'])
    
    op.create_index('idx_cache_entries_key', 'cache_entries', ['cache_key'])
    op.create_index('idx_cache_entries_type', 'cache_entries', ['cache_type'])
    op.create_index('idx_cache_entries_expires_at', 'cache_entries', ['expires_at'])
    op.create_index('idx_cache_entries_last_accessed', 'cache_entries', ['last_accessed'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('cache_entries')
    op.drop_table('agent_sessions')
    op.drop_table('conversation_summaries')
    op.drop_table('session_memory')
    op.drop_table('vector_embeddings')
    op.drop_table('conversation_logs')
    op.drop_table('scene_progress')
    op.drop_table('cohort_simulations')
    op.drop_table('cohort_students')
    op.drop_table('scenario_reviews')
    op.drop_table('scenario_files')
    op.drop_table('user_progress')
    op.drop_table('scene_personas')
    op.drop_table('scenario_scenes')
    op.drop_table('scenario_personas')
    op.drop_table('cohorts')
    op.drop_table('scenarios')
    op.drop_table('users')
