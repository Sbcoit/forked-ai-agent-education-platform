"""
Database optimization service for improved performance
Provides caching, connection pooling, and query optimization
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.pool import QueuePool
from sqlalchemy import text
import time
from functools import wraps

from database.models import (
    Scenario, ScenarioScene, ScenarioPersona, User,
    UserProgress, SceneProgress, ConversationLog
)

# Performance monitoring
logger = logging.getLogger(__name__)

# Thread pool for CPU-bound operations
DB_EXECUTOR = ThreadPoolExecutor(max_workers=8)

def async_db_operation(func):
    """Decorator to run database operations in thread pool"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(DB_EXECUTOR, func, *args, **kwargs)
    return wrapper

class DatabaseOptimizer:
    """Optimized database operations for simulation APIs"""
    
    def __init__(self):
        self._query_cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    @async_db_operation
    def get_simulation_data_optimized(self, db: Session, user_progress_id: int, scene_id: int) -> Dict[str, Any]:
        """Get all simulation data in a single optimized query batch"""
        start_time = time.time()
        
        try:
            # Batch multiple queries
            user_progress = db.query(UserProgress).filter(
                UserProgress.id == user_progress_id
            ).first()
            
            if not user_progress:
                raise ValueError("User progress not found")
            
            # Get scene with preloaded relationships
            scene = db.query(ScenarioScene).options(
                selectinload(ScenarioScene.personas)
            ).filter(ScenarioScene.id == scene_id).first()
            
            if not scene:
                raise ValueError("Scene not found")
            
            # Get all personas for the scenario in one query
            personas = db.query(ScenarioPersona).filter(
                ScenarioPersona.scenario_id == scene.scenario_id
            ).all()
            
            # Get recent conversation context in optimized way
            recent_messages = db.query(ConversationLog).filter(
                ConversationLog.user_progress_id == user_progress_id,
                ConversationLog.scene_id == scene_id
            ).order_by(ConversationLog.message_order.desc()).limit(10).all()
            
            # Get scene progress
            scene_progress = db.query(SceneProgress).filter(
                SceneProgress.user_progress_id == user_progress_id,
                SceneProgress.scene_id == scene_id
            ).first()
            
            query_time = time.time() - start_time
            logger.info(f"[DB_OPTIMIZED] Simulation data fetched in {query_time:.3f}s")
            
            return {
                "user_progress": user_progress,
                "scene": scene,
                "personas": personas,
                "recent_messages": recent_messages,
                "scene_progress": scene_progress,
                "query_time": query_time
            }
            
        except Exception as e:
            logger.error(f"[DB_ERROR] Failed to fetch simulation data: {e}")
            raise
    
    @async_db_operation
    def batch_create_conversation_logs(self, db: Session, log_entries: List[Dict[str, Any]]) -> bool:
        """Efficiently create multiple conversation log entries"""
        try:
            start_time = time.time()
            
            # Create entries in batch
            for entry in log_entries:
                log = ConversationLog(**entry)
                db.add(log)
            
            db.commit()
            
            batch_time = time.time() - start_time
            logger.info(f"[DB_OPTIMIZED] Created {len(log_entries)} conversation logs in {batch_time:.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"[DB_ERROR] Failed to create conversation logs: {e}")
            db.rollback()
            raise
    
    @async_db_operation
    def update_user_progress_optimized(self, db: Session, user_progress_id: int, updates: Dict[str, Any]) -> bool:
        """Optimized user progress update"""
        try:
            start_time = time.time()
            
            # Use bulk update for better performance
            db.query(UserProgress).filter(
                UserProgress.id == user_progress_id
            ).update(updates)
            
            db.commit()
            
            update_time = time.time() - start_time
            logger.info(f"[DB_OPTIMIZED] Updated user progress in {update_time:.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"[DB_ERROR] Failed to update user progress: {e}")
            db.rollback()
            raise
    
    async def get_cached_scenario_data(self, db: Session, scenario_id: int) -> Optional[Dict[str, Any]]:
        """Get scenario data with caching"""
        cache_key = f"scenario_{scenario_id}"
        
        # Check cache first
        if cache_key in self._query_cache:
            cached_data = self._query_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self._cache_ttl:
                logger.info(f"[CACHE_HIT] Scenario {scenario_id} data from cache")
                return cached_data["data"]
        
        # Fetch from database
        @async_db_operation
        def _fetch_scenario_data(db: Session, scenario_id: int):
            scenario = db.query(Scenario).options(
                selectinload(Scenario.personas),
                selectinload(Scenario.scenes)
            ).filter(Scenario.id == scenario_id).first()
            
            if not scenario:
                return None
            
            return {
                "id": scenario.id,
                "title": scenario.title,
                "description": scenario.description,
                "personas": [{"id": p.id, "name": p.name, "role": p.role} for p in scenario.personas],
                "scenes": [{"id": s.id, "title": s.title, "scene_order": s.scene_order} for s in scenario.scenes]
            }
        
        data = await _fetch_scenario_data(db, scenario_id)
        
        if data:
            # Cache the result
            self._query_cache[cache_key] = {
                "data": data,
                "timestamp": time.time()
            }
            logger.info(f"[CACHE_MISS] Scenario {scenario_id} data cached")
        
        return data
    
    def clear_cache(self):
        """Clear the query cache"""
        self._query_cache.clear()
        logger.info("[CACHE] Query cache cleared")

# Global instance
db_optimizer = DatabaseOptimizer()
