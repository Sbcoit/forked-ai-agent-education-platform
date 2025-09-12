"""
LangChain Configuration for AI Agent Education Platform
Centralized configuration for all LangChain components
"""

import os
from typing import Optional, Dict, Any
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.schema import BaseMessage
from langchain.cache import RedisCache, InMemoryCache
from langchain.globals import set_llm_cache
import redis

class LangChainSettings(BaseSettings):
    """LangChain-specific settings"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # PostgreSQL with pgvector
    postgres_url: str
    vector_collection_name: str = "ai_agent_embeddings"
    
    # Redis Configuration for Caching
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = True
    
    # Embedding Configuration
    embedding_model: str = "openai"  # "openai" or "huggingface"
    huggingface_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Memory Configuration
    conversation_window_size: int = 10
    summary_threshold: int = 5
    max_token_limit: int = 2000
    
    # Performance Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_threshold: float = 0.7
    max_retrieval_docs: int = 5
    
    # Session Management
    session_timeout: int = 3600  # 1 hour
    cache_ttl: int = 1800  # 30 minutes
    
    class Config:
        env_file = ".env"
        env_prefix = "LANGCHAIN_"
        extra = "ignore"  # Ignore extra fields

# Use existing database connection settings
from database.connection import settings as db_settings

# Initialize settings with database values and environment overrides
settings = LangChainSettings(
    openai_api_key=db_settings.openai_api_key,
    postgres_url=db_settings.database_url,
    redis_enabled=False  # Disable Redis by default
)

class LangChainManager:
    """Centralized LangChain component manager"""
    
    def __init__(self):
        self._llm = None
        self._embeddings = None
        self._vectorstore = None
        self._redis_client = None
        self._cache = None
        
    @property
    def llm(self) -> ChatOpenAI:
        """Get or create OpenAI LLM instance"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0.7,
                max_tokens=1000,
                streaming=True
            )
        return self._llm
    
    @property
    def embeddings(self):
        """Get or create embeddings instance"""
        if self._embeddings is None:
            # support explicit provider setting, and fall back to legacy uses where embedding_model held the provider
            provider = getattr(settings, "embedding_provider", None)
            if provider is None and getattr(settings, "embedding_model", None) == "openai":
                provider = "openai"

            if provider == "openai":
                model_name = getattr(settings, "openai_embedding_model", getattr(settings, "embedding_model", None))
                self._embeddings = OpenAIEmbeddings(
                    model=model_name,
                    api_key=getattr(settings, "openai_api_key", None)
                )
            else:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=settings.huggingface_model
                )
        return self._embeddings
    
    @property
    def vectorstore(self) -> PGVector:
        """Get or create PostgreSQL vector store"""
        if self._vectorstore is None:
            self._vectorstore = PGVector(
                connection_string=settings.postgres_url,
                embedding_function=self.embeddings,
                collection_name=settings.vector_collection_name
            )
        return self._vectorstore
    
    @property
    def redis_client(self):
        """Get or create Redis client"""
        if self._redis_client is None and settings.redis_enabled:
            try:
                self._redis_client = redis.from_url(settings.redis_url)
                # Test connection
                self._redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}. Using in-memory cache.")
                self._redis_client = None
        return self._redis_client
    
    @property
    def cache(self):
        """Get or create cache instance"""
        if self._cache is None:
            if self.redis_client:
                self._cache = RedisCache(redis_client=self.redis_client)
            else:
                self._cache = InMemoryCache()
            set_llm_cache(self._cache)
        return self._cache
    
    def create_conversation_memory(self, 
                                 session_id: str,
                                 memory_type: str = "buffer_window"):
        """Create conversation memory for a session"""
        if memory_type == "buffer_window":
            return ConversationBufferWindowMemory(
                k=settings.conversation_window_size,
                return_messages=True,
                memory_key="chat_history"
            )
        elif memory_type == "summary_buffer":
            return ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=settings.max_token_limit,
                return_messages=True,
                memory_key="chat_history"
            )
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
    
    def get_session_key(self, user_id: int, scenario_id: int, scene_id: int) -> str:
        """Generate session key for caching"""
        return f"session:{user_id}:{scenario_id}:{scene_id}"
    
    def get_embedding_key(self, content_type: str, content_id: int) -> str:
        """Generate embedding key for caching"""
        return f"embedding:{content_type}:{content_id}"

# Global LangChain manager instance
langchain_manager = LangChainManager()

# Initialize cache
langchain_manager.cache

# Export commonly used components
llm = langchain_manager.llm
embeddings = langchain_manager.embeddings
vectorstore = langchain_manager.vectorstore
cache = langchain_manager.cache

def get_langchain_manager() -> LangChainManager:
    """Dependency injection for LangChain manager"""
    return langchain_manager
