"""Fix vector_embeddings column type to ensure proper vector support

Revision ID: fix_vector_embeddings_001
Revises: add_langchain_integration_001
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import os

# Import pgvector if available
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    Vector = None

# Use configuration to determine vector column type
def get_vector_column_type():
    """Get the appropriate column type based on configuration"""
    use_pgvector = os.getenv("USE_PGVECTOR", "true").lower() == "true"
    if use_pgvector and PGVECTOR_AVAILABLE:
        return Vector(1536)
    else:
        return sa.JSON()

# revision identifiers, used by Alembic.
revision = 'fix_vector_embeddings_001'
down_revision = 'add_langchain_integration_001'
branch_labels = None
depends_on = None


def upgrade():
    """Fix vector_embeddings column to ensure proper vector type"""
    
    # Ensure pgvector extension is enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Get the database connection and inspector
    connection = op.get_bind()
    from sqlalchemy import inspect
    inspector = inspect(connection)
    
    # Check if vector_embeddings table exists
    if 'vector_embeddings' in inspector.get_table_names():
        # Check current column type
        columns = inspector.get_columns('vector_embeddings')
        embedding_vector_col = next((col for col in columns if col['name'] == 'embedding_vector'), None)
        
        if embedding_vector_col:
            current_type = str(embedding_vector_col['type'])
            # Check if it's already a vector type
            if 'vector' not in current_type.lower():
                # Convert to vector type using proper SQLAlchemy approach
                from sqlalchemy.dialects.postgresql import ARRAY
                from sqlalchemy import Float
                
                # Use op.alter_column with proper type conversion
                op.alter_column('vector_embeddings', 'embedding_vector', 
                               type_=get_vector_column_type(),
                               existing_type=embedding_vector_col['type'])
    
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
    
    # Copy vector data to JSON format, handling nulls explicitly
    op.execute("""
        UPDATE vector_embeddings 
        SET embedding_vector_old = CASE 
            WHEN embedding_vector IS NOT NULL 
            THEN json_build_object('embedding', embedding_vector::text::json)
            ELSE json_build_object('embedding', '[]'::json)
        END
    """)
    
    # Drop the vector column
    op.drop_column('vector_embeddings', 'embedding_vector')
    
    # Rename the JSON column
    op.alter_column('vector_embeddings', 'embedding_vector_old', 
                    new_column_name='embedding_vector')
    
    # Ensure no null values exist before making column not nullable
    op.execute("""
        UPDATE vector_embeddings 
        SET embedding_vector = json_build_object('embedding', '[]'::json)
        WHERE embedding_vector IS NULL
    """)
    
    # Make it not nullable
    op.alter_column('vector_embeddings', 'embedding_vector', nullable=False)
