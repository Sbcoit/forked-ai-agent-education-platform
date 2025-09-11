"""
Vector Store Service for LangChain Integration
Provides fallback implementations when pgvector is not available
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import hashlib
import pickle
import base64

try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False

from database.connection import get_db, settings
from database.models import VectorEmbeddings
from langchain_config import embeddings

class VectorStoreService:
    """
    Vector store service with fallback implementations
    """
    
    def __init__(self):
        self.pgvector_available = PGVECTOR_AVAILABLE
        self.embeddings_model = embeddings
        
    async def store_embedding(self, 
                            content: str, 
                            metadata: Dict[str, Any] = None,
                            collection_name: str = "default",
                            document_id: str = None) -> str:
        """
        Store text content as embedding with metadata
        """
        try:
            # Generate embedding
            embedding_vector = await self._generate_embedding(content)
            
            # Generate document ID if not provided
            if not document_id:
                document_id = self._generate_document_id(content, metadata)
            
            # Store in database
            if self.pgvector_available:
                return await self._store_with_pgvector(
                    content, embedding_vector, metadata, collection_name, document_id
                )
            else:
                return await self._store_with_fallback(
                    content, embedding_vector, metadata, collection_name, document_id
                )
                
        except Exception as e:
            print(f"Error storing embedding: {e}")
            return None
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            # Use LangChain embeddings
            embedding = await self.embeddings_model.aembed_query(text)
            
            # Ensure we have the right dimension (1536 for OpenAI, 384 for HuggingFace)
            if len(embedding) == 384:
                # Pad to 1536 dimensions for consistency
                embedding = embedding + [0.0] * (1536 - 384)
            elif len(embedding) != 1536:
                # Truncate or pad to 1536 dimensions
                if len(embedding) > 1536:
                    embedding = embedding[:1536]
                else:
                    embedding = embedding + [0.0] * (1536 - len(embedding))
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Fallback to simple hash-based embedding
            return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Generate a simple fallback embedding when OpenAI is not available"""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to 1536-dimensional vector (OpenAI embedding size)
        embedding = []
        for i in range(0, len(text_hash), 2):
            # Use hex pairs to generate values
            hex_pair = text_hash[i:i+2]
            value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
            embedding.append(value)
        
        # Pad or truncate to 1536 dimensions
        while len(embedding) < 1536:
            embedding.append(0.0)
        embedding = embedding[:1536]
        
        return embedding
    
    def _generate_document_id(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Generate a unique document ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if metadata:
            metadata_str = json.dumps(metadata, sort_keys=True)
            metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()
            return f"{content_hash}_{metadata_hash[:8]}"
        return content_hash
    
    async def _store_with_pgvector(self, 
                                 content: str, 
                                 embedding_vector: List[float], 
                                 metadata: Dict[str, Any],
                                 collection_name: str,
                                 document_id: str) -> str:
        """Store embedding using pgvector"""
        try:
            db = next(get_db())
            
            # Check if document already exists
            existing = db.query(VectorEmbeddings).filter(
                VectorEmbeddings.content_hash == document_id,
                VectorEmbeddings.content_type == collection_name
            ).first()
            
            if existing:
                # Update existing
                existing.original_content = content
                existing.embedding_vector = embedding_vector
                existing.content_metadata = metadata
                db.commit()
                return document_id
            
            # Create new embedding store entry
            embedding_store = VectorEmbeddings(
                content_type=collection_name,
                content_id=0,  # We'll use content_hash as the unique identifier
                content_hash=document_id,
                embedding_vector=embedding_vector,
                embedding_model="openai-ada-002",
                embedding_dimension=len(embedding_vector),
                original_content=content,
                content_metadata=metadata
            )
            
            db.add(embedding_store)
            db.commit()
            return document_id
            
        except Exception as e:
            print(f"Error storing with pgvector: {e}")
            # Fallback to non-vector storage
            return await self._store_with_fallback(
                content, embedding_vector, metadata, collection_name, document_id
            )
        finally:
            if 'db' in locals():
                db.close()
    
    async def _store_with_fallback(self, 
                                 content: str, 
                                 embedding_vector: List[float], 
                                 metadata: Dict[str, Any],
                                 collection_name: str,
                                 document_id: str) -> str:
        """Store embedding using fallback method (JSON storage)"""
        try:
            db = next(get_db())
            
            # Store as JSON in metadata field
            embedding_data = {
                "embedding": embedding_vector,
                "content": content,
                "metadata": metadata or {},
                "collection_name": collection_name,
                "document_id": document_id
            }
            
            # Check if document already exists
            existing = db.query(VectorEmbeddings).filter(
                VectorEmbeddings.content_hash == document_id,
                VectorEmbeddings.content_type == collection_name
            ).first()
            
            if existing:
                # Update existing
                existing.original_content = content
                existing.content_metadata = embedding_data
                db.commit()
                return document_id
            
            # Create new entry (store vector in metadata since pgvector column is required)
            embedding_store = VectorEmbeddings(
                content_type=collection_name,
                content_id=0,
                content_hash=document_id,
                embedding_vector=embedding_vector,  # Store the actual vector
                embedding_model="fallback",
                embedding_dimension=len(embedding_vector),
                original_content=content,
                content_metadata=embedding_data
            )
            
            db.add(embedding_store)
            db.commit()
            return document_id
            
        except Exception as e:
            print(f"Error storing with fallback: {e}")
            return None
        finally:
            if 'db' in locals():
                db.close()
    
    async def similarity_search(self, 
                              query: str, 
                              collection_name: str = "default",
                              k: int = 5,
                              score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform similarity search
        """
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            if self.pgvector_available:
                return await self._similarity_search_pgvector(
                    query_embedding, collection_name, k, score_threshold
                )
            else:
                return await self._similarity_search_fallback(
                    query_embedding, collection_name, k, score_threshold
                )
                
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    async def _similarity_search_pgvector(self, 
                                        query_embedding: List[float],
                                        collection_name: str,
                                        k: int,
                                        score_threshold: float) -> List[Dict[str, Any]]:
        """Similarity search using pgvector"""
        try:
            db = next(get_db())
            
            # Use pgvector similarity search
            results = db.execute(
                text("""
                    SELECT content_hash, original_content, content_metadata, 
                           1 - (embedding_vector <=> :query_embedding) as similarity_score
                    FROM vector_embeddings 
                    WHERE content_type = :collection_name
                    ORDER BY embedding_vector <=> :query_embedding
                    LIMIT :k
                """),
                {
                    "query_embedding": query_embedding,
                    "collection_name": collection_name,
                    "k": k
                }
            ).fetchall()
            
            # Filter by score threshold and format results
            filtered_results = []
            for row in results:
                if row.similarity_score >= score_threshold:
                    filtered_results.append({
                        "document_id": row.content_hash,
                        "content": row.original_content,
                        "metadata": row.content_metadata or {},
                        "score": row.similarity_score
                    })
            
            return filtered_results
            
        except Exception as e:
            print(f"Error in pgvector similarity search: {e}")
            # Fallback to non-vector search
            return await self._similarity_search_fallback(
                query_embedding, collection_name, k, score_threshold
            )
        finally:
            if 'db' in locals():
                db.close()
    
    async def _similarity_search_fallback(self, 
                                        query_embedding: List[float],
                                        collection_name: str,
                                        k: int,
                                        score_threshold: float) -> List[Dict[str, Any]]:
        """Similarity search using fallback method (cosine similarity)"""
        try:
            db = next(get_db())
            
            # Get all embeddings from collection
            embeddings_data = db.query(VectorEmbeddings).filter(
                VectorEmbeddings.content_type == collection_name
            ).all()
            
            if not embeddings_data:
                return []
            
            # Calculate similarities
            similarities = []
            for item in embeddings_data:
                if item.content_metadata and "embedding" in item.content_metadata:
                    stored_embedding = item.content_metadata["embedding"]
                    similarity = self._cosine_similarity(query_embedding, stored_embedding)
                    
                    if similarity >= score_threshold:
                        similarities.append({
                            "document_id": item.content_hash,
                            "content": item.original_content,
                            "metadata": item.content_metadata,
                            "score": similarity
                        })
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x["score"], reverse=True)
            return similarities[:k]
            
        except Exception as e:
            print(f"Error in fallback similarity search: {e}")
            return []
        finally:
            if 'db' in locals():
                db.close()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def get_document(self, document_id: str, collection_name: str = "default") -> Optional[Dict[str, Any]]:
        """Retrieve a specific document"""
        try:
            db = next(get_db())
            
            result = db.query(VectorEmbeddings).filter(
                VectorEmbeddings.content_hash == document_id,
                VectorEmbeddings.content_type == collection_name
            ).first()
            
            if result:
                return {
                    "document_id": result.content_hash,
                    "content": result.original_content,
                    "metadata": result.content_metadata or {},
                    "created_at": result.created_at
                }
            
            return None
            
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None
        finally:
            if 'db' in locals():
                db.close()
    
    async def delete_document(self, document_id: str, collection_name: str = "default") -> bool:
        """Delete a document"""
        try:
            db = next(get_db())
            
            result = db.query(VectorEmbeddings).filter(
                VectorEmbeddings.content_hash == document_id,
                VectorEmbeddings.content_type == collection_name
            ).first()
            
            if result:
                db.delete(result)
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
        finally:
            if 'db' in locals():
                db.close()
    
    async def get_collection_stats(self, collection_name: str = "default") -> Dict[str, Any]:
        """Get statistics for a collection"""
        try:
            db = next(get_db())
            
            total_docs = db.query(VectorEmbeddings).filter(
                VectorEmbeddings.content_type == collection_name
            ).count()
            
            return {
                "collection_name": collection_name,
                "total_documents": total_docs,
                "pgvector_available": self.pgvector_available
            }
            
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {
                "collection_name": collection_name,
                "total_documents": 0,
                "pgvector_available": self.pgvector_available,
                "error": str(e)
            }
        finally:
            if 'db' in locals():
                db.close()

# Global instance
vector_store_service = VectorStoreService()
