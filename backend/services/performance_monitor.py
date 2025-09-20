"""
Performance monitoring and metrics collection service
Tracks API response times, database query performance, and system metrics
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
from functools import wraps
import threading
from datetime import datetime, timedelta

# Performance monitoring
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    timestamp: datetime
    db_queries: int = 0
    db_time: float = 0.0
    ai_calls: int = 0
    ai_time: float = 0.0
    memory_usage: float = 0.0
    error: Optional[str] = None

@dataclass
class SystemStats:
    """System-wide performance statistics"""
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    total_requests: int = 0
    error_rate: float = 0.0
    peak_memory: float = 0.0
    concurrent_requests: int = 0
    db_connection_pool_size: int = 0
    cache_hit_rate: float = 0.0

class PerformanceMonitor:
    """Centralized performance monitoring system"""
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics: deque = deque(maxlen=max_metrics)
        self.active_requests: Dict[str, float] = {}
        self.endpoint_stats: Dict[str, List[float]] = defaultdict(list)
        self.system_stats = SystemStats()
        self._lock = threading.Lock()
        
        # Performance thresholds
        self.slow_request_threshold = 5.0  # 5 seconds
        self.db_slow_query_threshold = 1.0  # 1 second
        self.ai_slow_call_threshold = 10.0  # 10 seconds
        
        # Start background stats calculation
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks for metrics calculation"""
        def calculate_stats():
            while True:
                try:
                    self._calculate_system_stats()
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    logger.error(f"Error calculating stats: {e}")
        
        thread = threading.Thread(target=calculate_stats, daemon=True)
        thread.start()
    
    def start_request(self, endpoint: str, method: str) -> str:
        """Start tracking a request"""
        request_id = f"{endpoint}_{method}_{time.time()}"
        with self._lock:
            self.active_requests[request_id] = time.time()
            self.system_stats.concurrent_requests = len(self.active_requests)
        
        logger.debug(f"[PERF] Started tracking request: {request_id}")
        return request_id
    
    def end_request(
        self,
        request_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        db_queries: int = 0,
        db_time: float = 0.0,
        ai_calls: int = 0,
        ai_time: float = 0.0,
        memory_usage: float = 0.0,
        error: Optional[str] = None
    ):
        """End tracking a request and record metrics"""
        
        with self._lock:
            start_time = self.active_requests.pop(request_id, time.time())
            response_time = time.time() - start_time
            self.system_stats.concurrent_requests = len(self.active_requests)
        
        # Create metrics record
        metrics = PerformanceMetrics(
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            timestamp=datetime.now(),
            db_queries=db_queries,
            db_time=db_time,
            ai_calls=ai_calls,
            ai_time=ai_time,
            memory_usage=memory_usage,
            error=error
        )
        
        # Store metrics
        self.metrics.append(metrics)
        self.endpoint_stats[f"{method} {endpoint}"].append(response_time)
        
        # Log slow requests
        if response_time > self.slow_request_threshold:
            logger.warning(f"[PERF] Slow request: {endpoint} took {response_time:.3f}s")
        
        if db_time > self.db_slow_query_threshold:
            logger.warning(f"[PERF] Slow DB operations: {db_time:.3f}s ({db_queries} queries)")
        
        if ai_time > self.ai_slow_call_threshold:
            logger.warning(f"[PERF] Slow AI calls: {ai_time:.3f}s ({ai_calls} calls)")
        
        logger.info(f"[PERF] Request completed: {endpoint} in {response_time:.3f}s (DB: {db_time:.3f}s, AI: {ai_time:.3f}s)")
    
    def _calculate_system_stats(self):
        """Calculate system-wide performance statistics"""
        if not self.metrics:
            return
        
        with self._lock:
            # Get recent metrics (last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return
            
            response_times = [m.response_time for m in recent_metrics]
            error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
            
            # Calculate statistics
            self.system_stats.avg_response_time = sum(response_times) / len(response_times)
            self.system_stats.p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            self.system_stats.total_requests = len(recent_metrics)
            self.system_stats.error_rate = error_count / len(recent_metrics) if recent_metrics else 0.0
            self.system_stats.peak_memory = max((m.memory_usage for m in recent_metrics), default=0.0)
    
    def get_endpoint_stats(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Get performance stats for a specific endpoint"""
        key = f"{method} {endpoint}"
        times = self.endpoint_stats.get(key, [])
        
        if not times:
            return {"message": "No data available"}
        
        recent_times = times[-100:]  # Last 100 requests
        
        return {
            "endpoint": endpoint,
            "method": method,
            "total_requests": len(times),
            "recent_requests": len(recent_times),
            "avg_response_time": sum(recent_times) / len(recent_times),
            "min_response_time": min(recent_times),
            "max_response_time": max(recent_times),
            "p95_response_time": sorted(recent_times)[int(len(recent_times) * 0.95)] if len(recent_times) > 20 else max(recent_times)
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide performance statistics"""
        return {
            "avg_response_time": round(self.system_stats.avg_response_time, 3),
            "p95_response_time": round(self.system_stats.p95_response_time, 3),
            "total_requests": self.system_stats.total_requests,
            "error_rate": round(self.system_stats.error_rate * 100, 2),
            "concurrent_requests": self.system_stats.concurrent_requests,
            "peak_memory_mb": round(self.system_stats.peak_memory, 2),
            "metrics_stored": len(self.metrics),
            "slow_requests": len([m for m in self.metrics if m.response_time > self.slow_request_threshold])
        }
    
    def get_recent_slow_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow requests for debugging"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        slow_requests = [
            m for m in self.metrics 
            if m.timestamp >= cutoff_time and m.response_time > self.slow_request_threshold
        ]
        
        # Sort by response time (slowest first)
        slow_requests.sort(key=lambda x: x.response_time, reverse=True)
        
        return [
            {
                "endpoint": m.endpoint,
                "method": m.method,
                "response_time": round(m.response_time, 3),
                "db_time": round(m.db_time, 3),
                "ai_time": round(m.ai_time, 3),
                "status_code": m.status_code,
                "timestamp": m.timestamp.isoformat(),
                "error": m.error
            }
            for m in slow_requests[:limit]
        ]

def performance_tracker(endpoint_name: str = None):
    """Decorator to automatically track API endpoint performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            endpoint = endpoint_name or func.__name__
            method = "POST"  # Default, could be enhanced to detect HTTP method
            
            request_id = perf_monitor.start_request(endpoint, method)
            
            start_time = time.time()
            db_start_queries = 0  # Could integrate with DB monitoring
            ai_start_calls = 0    # Could integrate with AI call monitoring
            
            try:
                result = await func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200)
                error = None
            except Exception as e:
                result = None
                status_code = 500
                error = str(e)
                raise
            finally:
                total_time = time.time() - start_time
                perf_monitor.end_request(
                    request_id=request_id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    db_time=0.0,  # TODO: Integrate with actual DB monitoring
                    ai_time=0.0,  # TODO: Integrate with actual AI monitoring
                    error=error
                )
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            endpoint = endpoint_name or func.__name__
            method = "GET"  # Default
            
            request_id = perf_monitor.start_request(endpoint, method)
            
            try:
                result = func(*args, **kwargs)
                status_code = 200
                error = None
            except Exception as e:
                result = None
                status_code = 500
                error = str(e)
                raise
            finally:
                perf_monitor.end_request(
                    request_id=request_id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    error=error
                )
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

# Convenience functions
def track_db_operation(func):
    """Decorator to track database operation performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            operation_time = time.time() - start_time
            if operation_time > perf_monitor.db_slow_query_threshold:
                logger.warning(f"[DB_PERF] Slow operation {func.__name__}: {operation_time:.3f}s")
    return wrapper

def track_ai_operation(func):
    """Decorator to track AI operation performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            operation_time = time.time() - start_time
            if operation_time > perf_monitor.ai_slow_call_threshold:
                logger.warning(f"[AI_PERF] Slow operation {func.__name__}: {operation_time:.3f}s")
    return wrapper
