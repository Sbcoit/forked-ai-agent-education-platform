"""Add LangChain integration tables

Revision ID: add_langchain_integration
Revises: adc1f7ccb40c
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = 'add_langchain_integration'
down_revision = 'adc1f7ccb40c'
branch_labels = None
depends_on = None


def upgrade():
    """Add LangChain integration tables"""
    
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create vector_embeddings table
    op.create_table('vector_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(), nullable=False),
        sa.Column('embedding_vector', Vector(1536), nullable=False),
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
    
    # Create indexes for vector_embeddings
    op.create_index('idx_vector_embeddings_content_type', 'vector_embeddings', ['content_type'])
    op.create_index('idx_vector_embeddings_content_id', 'vector_embeddings', ['content_id'])
    op.create_index('idx_vector_embeddings_content_hash', 'vector_embeddings', ['content_hash'])
    op.create_index('idx_vector_embeddings_active', 'vector_embeddings', ['is_active'])
    op.create_index('idx_vector_embeddings_created_at', 'vector_embeddings', ['created_at'])
    
    # Create vector index for similarity search
    op.execute('CREATE INDEX idx_vector_embeddings_embedding_vector ON vector_embeddings USING ivfflat (embedding_vector vector_l2_ops) WITH (lists = 100)')
    
    # Create session_memory table
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
        sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for session_memory
    op.create_index('idx_session_memory_session_id', 'session_memory', ['session_id'])
    op.create_index('idx_session_memory_user_progress_id', 'session_memory', ['user_progress_id'])
    op.create_index('idx_session_memory_scene_id', 'session_memory', ['scene_id'])
    op.create_index('idx_session_memory_type', 'session_memory', ['memory_type'])
    op.create_index('idx_session_memory_importance', 'session_memory', ['importance_score'])
    op.create_index('idx_session_memory_last_accessed', 'session_memory', ['last_accessed'])
    
    # Create conversation_summaries table
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
        sa.ForeignKeyConstraint(['scene_id'], ['scenario_scenes.id'], ),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for conversation_summaries
    op.create_index('idx_conversation_summaries_user_progress_id', 'conversation_summaries', ['user_progress_id'])
    op.create_index('idx_conversation_summaries_scene_id', 'conversation_summaries', ['scene_id'])
    op.create_index('idx_conversation_summaries_type', 'conversation_summaries', ['summary_type'])
    op.create_index('idx_conversation_summaries_quality', 'conversation_summaries', ['quality_score'])
    op.create_index('idx_conversation_summaries_created_at', 'conversation_summaries', ['created_at'])
    
    # Create agent_sessions table
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
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for agent_sessions
    op.create_index('idx_agent_sessions_session_id', 'agent_sessions', ['session_id'])
    op.create_index('idx_agent_sessions_user_progress_id', 'agent_sessions', ['user_progress_id'])
    op.create_index('idx_agent_sessions_agent_type', 'agent_sessions', ['agent_type'])
    op.create_index('idx_agent_sessions_active', 'agent_sessions', ['is_active'])
    op.create_index('idx_agent_sessions_last_activity', 'agent_sessions', ['last_activity'])
    
    # Create cache_entries table
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
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for cache_entries
    op.create_index('idx_cache_entries_key', 'cache_entries', ['cache_key'])
    op.create_index('idx_cache_entries_type', 'cache_entries', ['cache_type'])
    op.create_index('idx_cache_entries_expires_at', 'cache_entries', ['expires_at'])
    op.create_index('idx_cache_entries_last_accessed', 'cache_entries', ['last_accessed'])


def downgrade():
    """Remove LangChain integration tables"""
    
    # Drop tables in reverse order
    op.drop_table('cache_entries')
    op.drop_table('agent_sessions')
    op.drop_table('conversation_summaries')
    op.drop_table('session_memory')
    op.drop_table('vector_embeddings')
    
    # Note: We don't drop the pgvector extension as it might be used by other applications
