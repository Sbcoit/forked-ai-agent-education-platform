"""Fix vector_embeddings column type to ensure proper vector support

Revision ID: fix_vector_embeddings_001
Revises: add_langchain_integration_001
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = 'fix_vector_embeddings_001'
down_revision = '7d3a637d0a30'
branch_labels = None
depends_on = None


def upgrade():
    """Fix vector_embeddings column to ensure proper vector type"""
    
    # Ensure pgvector extension is enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Since we're clearing the database, we can simply ensure the column is the right type
    # Check if the table exists and has the right column type
    op.execute("""
        DO $$
        BEGIN
            -- Check if vector_embeddings table exists and has the right column type
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'vector_embeddings') THEN
                -- Ensure the column is of vector type
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'vector_embeddings' 
                    AND column_name = 'embedding_vector' 
                    AND data_type = 'USER-DEFINED'
                ) THEN
                    -- Alter the column to be vector type
                    ALTER TABLE vector_embeddings 
                    ALTER COLUMN embedding_vector TYPE vector(1536);
                END IF;
            END IF;
        END;
        $$;
    """)
    
    # Create the vector index if it doesn't exist
    op.execute('DROP INDEX IF EXISTS idx_vector_embeddings_embedding_vector')
    op.execute('CREATE INDEX IF NOT EXISTS idx_vector_embeddings_embedding_vector ON vector_embeddings USING ivfflat (embedding_vector vector_l2_ops) WITH (lists = 100)')


def downgrade():
    """Revert vector_embeddings column changes"""
    
    # Drop the vector index
    op.execute('DROP INDEX IF EXISTS idx_vector_embeddings_embedding_vector')
    
    # Convert vector back to JSON for compatibility
    op.add_column('vector_embeddings', 
                  sa.Column('embedding_vector_old', sa.JSON(), nullable=True))
    
    # Copy vector data to JSON format
    op.execute("""
        UPDATE vector_embeddings 
        SET embedding_vector_old = json_build_object('embedding', embedding_vector::text::json)
        WHERE embedding_vector IS NOT NULL
    """)
    
    # Drop the vector column
    op.drop_column('vector_embeddings', 'embedding_vector')
    
    # Rename the JSON column
    op.alter_column('vector_embeddings', 'embedding_vector_old', 
                    new_column_name='embedding_vector')
    
    # Make it not nullable
    op.alter_column('vector_embeddings', 'embedding_vector', nullable=False)
