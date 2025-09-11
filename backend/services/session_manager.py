"""
Session Manager for AI Agent Education Platform
Handles session state, caching, and memory management with LangChain
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import hashlib
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from langchain_config import langchain_manager, settings
from database.connection import get_db
from database.models import UserProgress, ScenarioScene, ScenarioPersona
from database.models import (
    SessionMemory, ConversationSummaries, AgentSessions, CacheEntries, VectorEmbeddings
)

# Create aliases for easier usage
AgentSession = AgentSessions
CacheEntry = CacheEntries

class SessionManager:
    """Manages agent sessions, memory, and caching"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = settings.session_timeout
        self.cache_ttl = settings.cache_ttl
        
    def generate_session_id(self, user_id: int, scenario_id: int, scene_id: int) -> str:
        """Generate unique session ID"""
        timestamp = datetime.utcnow().isoformat()
        session_data = f"{user_id}_{scenario_id}_{scene_id}_{timestamp}"
        return hashlib.md5(session_data.encode()).hexdigest()
    
    def get_cache_key(self, content_type: str, content_id: int, additional_data: str = "") -> str:
        """Generate cache key for content"""
        cache_data = f"{content_type}_{content_id}_{additional_data}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    async def create_agent_session(self, 
                                 user_progress_id: int,
                                 agent_type: str,
                                 agent_id: Optional[str] = None,
                                 session_config: Optional[Dict[str, Any]] = None) -> str:
        """Create new agent session"""
        
        session_id = self.generate_session_id(
            user_progress_id, 0, 0  # Simplified for agent sessions
        )
        
        # Create session in database
        db = None
        try:
            db = next(get_db())
            agent_session = AgentSession(
                session_id=session_id,
                user_progress_id=user_progress_id,
                agent_type=agent_type,
                agent_id=agent_id,
                session_config=session_config or {},
                session_state={},
                expires_at=datetime.utcnow() + timedelta(seconds=self.session_timeout),
                is_active=True
            )
            
            db.add(agent_session)
            db.commit()
            
            # Store in memory for quick access
            self.active_sessions[session_id] = {
                "agent_type": agent_type,
                "agent_id": agent_id,
                "user_progress_id": user_progress_id,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "config": session_config or {}
            }
            
            return session_id
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error creating agent session: {e}")
            raise e
        finally:
            if db:
                db.close()
    
    async def get_agent_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get agent session by ID"""
        
        # Check memory first
        if session_id in self.active_sessions:
            session_data = self.active_sessions[session_id]
            
            # Check if session is expired
            if datetime.utcnow() - session_data["last_activity"] > timedelta(seconds=self.session_timeout):
                await self.expire_session(session_id)
                return None
            
            # Update last activity
            session_data["last_activity"] = datetime.utcnow()
            return session_data
        
        # Check database
        db = next(get_db())
        try:
            agent_session = db.query(AgentSession).filter(
                and_(
                    AgentSession.session_id == session_id,
                    AgentSession.is_active == True,
                    AgentSession.expires_at > datetime.utcnow()
                )
            ).first()
            
            if agent_session:
                # Restore to memory
                self.active_sessions[session_id] = {
                    "agent_type": agent_session.agent_type,
                    "agent_id": agent_session.agent_id,
                    "user_progress_id": agent_session.user_progress_id,
                    "created_at": agent_session.created_at,
                    "last_activity": agent_session.last_activity,
                    "config": agent_session.session_config or {}
                }
                
                return self.active_sessions[session_id]
            
            return None
            
        except Exception as e:
            print(f"Error getting agent session: {e}")
            return None
        finally:
            db.close()
    
    async def update_session_state(self, 
                                 session_id: str, 
                                 state_updates: Dict[str, Any]) -> bool:
        """Update session state"""
        
        # Update memory
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["last_activity"] = datetime.utcnow()
        
        # Update database
        db = next(get_db())
        try:
            agent_session = db.query(AgentSession).filter(
                AgentSession.session_id == session_id
            ).first()
            
            if agent_session:
                current_state = agent_session.session_state or {}
                current_state.update(state_updates)
                agent_session.session_state = current_state
                agent_session.last_activity = datetime.utcnow()
                
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            print(f"Error updating session state: {e}")
            return False
        finally:
            db.close()
    
    async def expire_session(self, session_id: str) -> bool:
        """Expire and clean up session"""
        
        # Remove from memory
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Update database
        db = next(get_db())
        try:
            agent_session = db.query(AgentSession).filter(
                AgentSession.session_id == session_id
            ).first()
            
            if agent_session:
                agent_session.is_active = False
                agent_session.expires_at = datetime.utcnow()
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            print(f"Error expiring session: {e}")
            return False
        finally:
            db.close()
    
    async def store_memory(self, 
                         session_id: str,
                         memory_type: str,
                         memory_content: str,
                         user_progress_id: int,
                         scene_id: Optional[int] = None,
                         persona_id: Optional[int] = None,
                         importance_score: float = 0.5,
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store memory in session"""
        
        db = next(get_db())
        try:
            memory = SessionMemory(
                session_id=session_id,
                user_progress_id=user_progress_id,
                scene_id=scene_id,
                memory_type=memory_type,
                memory_content=memory_content,
                memory_metadata=metadata or {},
                related_persona_id=persona_id,
                importance_score=importance_score,
                access_count=0
            )
            
            db.add(memory)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error storing memory: {e}")
            return False
        finally:
            db.close()
    
    async def retrieve_memories(self, 
                              session_id: str,
                              memory_type: Optional[str] = None,
                              limit: int = 10,
                              min_importance: float = 0.0) -> List[SessionMemory]:
        """Retrieve memories for session"""
        
        db = next(get_db())
        try:
            query = db.query(SessionMemory).filter(
                and_(
                    SessionMemory.session_id == session_id,
                    SessionMemory.importance_score >= min_importance
                )
            )
            
            if memory_type:
                query = query.filter(SessionMemory.memory_type == memory_type)
            
            memories = query.order_by(
                desc(SessionMemory.importance_score),
                desc(SessionMemory.created_at)
            ).limit(limit).all()
            
            # Update access count
            if memories:
                memory_ids = [m.id for m in memories]
                db.query(SessionMemory).filter(
                    SessionMemory.id.in_(memory_ids)
                ).update(
                    {
                        SessionMemory.access_count: SessionMemory.access_count + 1,
                        SessionMemory.last_accessed: datetime.utcnow()
                    },
                    synchronize_session=False
                )
                db.commit()
            return memories
            
        except Exception as e:
            db.rollback()
            print(f"Error retrieving memories: {e}")
            return []
        finally:
            db.close()
    
    async def store_conversation_summary(self, 
                                       user_progress_id: int,
                                       summary_type: str,
                                       summary_text: str,
                                       scene_id: Optional[int] = None,
                                       key_points: Optional[List[str]] = None,
                                       learning_moments: Optional[List[str]] = None,
                                       insights: Optional[List[str]] = None,
                                       recommendations: Optional[List[str]] = None,
                                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store conversation summary"""
        
        db = next(get_db())
        try:
            summary = ConversationSummaries(
                user_progress_id=user_progress_id,
                scene_id=scene_id,
                summary_type=summary_type,
                summary_text=summary_text,
                key_points=key_points or [],
                learning_moments=learning_moments or [],
                insights=insights or [],
                recommendations=recommendations or [],
                summary_metadata=metadata or {},
                quality_score=0.5,
                relevance_score=0.5
            )
            
            db.add(summary)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error storing conversation summary: {e}")
            return False
        finally:
            db.close()
    
    async def get_conversation_summaries(self, 
                                       user_progress_id: int,
                                       summary_type: Optional[str] = None,
                                       scene_id: Optional[int] = None,
                                       limit: int = 10) -> List[ConversationSummaries]:
        """Get conversation summaries"""
        
        db = next(get_db())
        try:
            query = db.query(ConversationSummaries).filter(
                ConversationSummaries.user_progress_id == user_progress_id
            )
            
            if summary_type:
                query = query.filter(ConversationSummaries.summary_type == summary_type)
            
            if scene_id:
                query = query.filter(ConversationSummaries.scene_id == scene_id)
            
            summaries = query.order_by(
                desc(ConversationSummaries.created_at)
            ).limit(limit).all()
            
            return summaries
            
        except Exception as e:
            print(f"Error getting conversation summaries: {e}")
            return []
        finally:
            db.close()
    
    async def cache_data(self, 
                        cache_key: str,
                        cache_type: str,
                        data: Any,
                        ttl_seconds: Optional[int] = None) -> bool:
        """Cache data with TTL"""
        
        ttl = ttl_seconds or self.cache_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        db = next(get_db())
        try:
            # Check if entry exists
            existing_entry = db.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if existing_entry:
                # Update existing entry
                existing_entry.cache_data = data
                existing_entry.expires_at = expires_at
                existing_entry.is_expired = False
                existing_entry.updated_at = datetime.utcnow()
            else:
                # Create new entry
                cache_entry = CacheEntry(
                    cache_key=cache_key,
                    cache_type=cache_type,
                    cache_data=data,
                    cache_size=len(str(data)),
                    expires_at=expires_at,
                    is_expired=False
                )
                db.add(cache_entry)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error caching data: {e}")
            return False
        finally:
            db.close()
    
    async def get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get cached data"""
        
        db = next(get_db())
        try:
            cache_entry = db.query(CacheEntry).filter(
                and_(
                    CacheEntry.cache_key == cache_key,
                    CacheEntry.is_expired == False,
                    CacheEntry.expires_at > datetime.utcnow()
                )
            ).first()
            
            if cache_entry:
                # Update access statistics
                cache_entry.hit_count += 1
                cache_entry.last_accessed = datetime.utcnow()
                db.commit()
                
                return cache_entry.cache_data
            
            # Update miss count for non-existent entries
            cache_entry = db.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if cache_entry:
                cache_entry.miss_count += 1
                db.commit()
            
            return None
            
        except Exception as e:
            print(f"Error getting cached data: {e}")
            return None
        finally:
            db.close()
    
    async def invalidate_cache(self, cache_key: str) -> bool:
        """Invalidate cache entry"""
        
        db = next(get_db())
        try:
            cache_entry = db.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if cache_entry:
                cache_entry.is_expired = True
                cache_entry.expires_at = datetime.utcnow()
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            print(f"Error invalidating cache: {e}")
            return False
        finally:
            db.close()
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and cache entries"""
        
        db = next(get_db())
        try:
            # Clean up expired agent sessions
            expired_sessions = db.query(AgentSession).filter(
                and_(
                    AgentSession.is_active == True,
                    AgentSession.expires_at < datetime.utcnow()
                )
            ).all()
            
            for session in expired_sessions:
                session.is_active = False
            
            # Clean up expired cache entries
            expired_cache = db.query(CacheEntry).filter(
                and_(
                    CacheEntry.is_expired == False,
                    CacheEntry.expires_at < datetime.utcnow()
                )
            ).all()
            
            for cache_entry in expired_cache:
                cache_entry.is_expired = True
            
            db.commit()
            
            # Clean up memory
            expired_session_ids = [s.session_id for s in expired_sessions]
            for session_id in expired_session_ids:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
            
            return len(expired_sessions) + len(expired_cache)
            
        except Exception as e:
            db.rollback()
            print(f"Error cleaning up expired sessions: {e}")
            return 0
        finally:
            db.close()
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session and cache statistics"""
        
        db = next(get_db())
        try:
            # Active sessions count
            active_sessions = db.query(AgentSession).filter(
                AgentSession.is_active == True
            ).count()
            
            # Cache statistics
            from sqlalchemy import func
            cache_stats = db.query(CacheEntry).with_entities(
                CacheEntry.cache_type,
                func.count(CacheEntry.id).label('count'),
                func.sum(CacheEntry.hit_count).label('total_hits'),
                func.sum(CacheEntry.miss_count).label('total_misses')
            ).group_by(CacheEntry.cache_type).all()
            
            # Memory statistics
            memory_stats = db.query(SessionMemory).with_entities(
                SessionMemory.memory_type,
                func.count(SessionMemory.id).label('count')
            ).group_by(SessionMemory.memory_type).all()
            
            return {
                "active_sessions": active_sessions,
                "memory_sessions": len(self.active_sessions),
                "cache_statistics": [
                    {
                        "type": stat.cache_type,
                        "count": stat.count,
                        "total_hits": stat.total_hits or 0,
                        "total_misses": stat.total_misses or 0
                    }
                    for stat in cache_stats
                ],
                "memory_statistics": [
                    {
                        "type": stat.memory_type,
                        "count": stat.count
                    }
                    for stat in memory_stats
                ]
            }
            
        except Exception as e:
            print(f"Error getting session statistics: {e}")
            return {}
        finally:
            db.close()
    
    def start_cleanup_task(self):
        """Start the background cleanup task"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, create the task
                asyncio.create_task(cleanup_task())
                print("✅ Session cleanup task started successfully")
            else:
                # If no event loop is running, we need to run it
                loop.run_until_complete(cleanup_task())
        except RuntimeError:
            # No event loop exists, create one
            asyncio.run(cleanup_task())
        except Exception as e:
            print(f"❌ Error starting cleanup task: {e}")
            raise e

# Global session manager instance
session_manager = SessionManager()

# Background task for cleanup
async def cleanup_task():
    """Background task to clean up expired sessions"""
    while True:
        try:
            cleaned = await session_manager.cleanup_expired_sessions()
            if cleaned > 0:
                print(f"Cleaned up {cleaned} expired sessions and cache entries")
        except Exception as e:
            print(f"Error in cleanup task: {e}")
        
        # Run cleanup every 5 minutes
        await asyncio.sleep(300)

# Cleanup task will be started when needed
