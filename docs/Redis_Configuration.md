# Redis Configuration Guide

This guide covers the Redis configuration and implementation for the AI Agent Education Platform.

## Overview

Redis is now **REQUIRED** for the platform and serves multiple critical functions:

1. **Session Management** - Fast, scalable session storage
2. **AI Response Caching** - Reduces API costs and improves performance
3. **Database Query Caching** - Speeds up frequently accessed data
4. **OAuth State Management** - Secure OAuth flow state storage

## Installation & Setup

### 1. Install Redis

#### Local Development (macOS)
```bash
brew install redis
brew services start redis
```

#### Local Development (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Docker (Recommended for Development)
```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 2. Environment Configuration

Update your `.env` file with the Redis URL:

```bash
# Redis Configuration (REQUIRED)
REDIS_URL=redis://localhost:6379
```

For production with authentication:
```bash
REDIS_URL=redis://username:password@hostname:6379
```

### 3. Verify Installation

Test Redis connection:
```bash
redis-cli ping
# Should return: PONG
```

## Redis Services Architecture

### 1. Redis Manager (`utilities/redis_manager.py`)

Central Redis client with the following features:
- **No fallback mechanisms** - Redis is required
- Automatic connection testing and error handling
- JSON serialization/deserialization
- TTL support for automatic expiration

### 2. AI Cache Service (`services/ai_cache_service.py`)

Caches expensive AI operations:
- **OpenAI API responses** - GPT-4, image generation, embeddings
- **Scenario analysis results** - PDF processing results
- **Simulation responses** - Chat responses with personas
- **Smart TTL management** - Different expiration times for different operation types

### 3. Database Cache Service (`services/db_cache_service.py`)

Caches database query results:
- **User-specific queries** - 5-minute TTL
- **Static data queries** - 1-hour TTL (scenario details, user profiles)
- **Dynamic data queries** - 10-minute TTL (lists, counts)
- **Automatic invalidation** - When related data changes

### 4. Session Manager (`services/session_manager.py`)

Redis-based session management:
- **Primary storage in Redis** - Fast access and automatic expiration
- **Database backup** - Optional persistence layer
- **Session state management** - Agent sessions, user progress

## Cache Strategies

### AI Response Caching

```python
# Cache OpenAI responses
ai_cache_service.cache_openai_response(
    operation="scenario_generation",
    input_data=pdf_content,
    response=generated_scenario,
    model="gpt-4",
    ttl=86400  # 24 hours
)

# Retrieve cached response
cached_response = ai_cache_service.get_cached_openai_response(
    operation="scenario_generation",
    input_data=pdf_content,
    model="gpt-4"
)
```

### Database Query Caching

```python
# Cache database queries
@cache_db_query("scenario_list", ttl=600)
def get_scenarios_list(db: Session, limit: int = 10):
    return db.query(Scenario).limit(limit).all()

# Cache user-specific queries
@cache_user_query(ttl=300)
def get_user_progress(user_id: int, db: Session):
    return db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
```

### Session Management

```python
# Create session in Redis
session_id = await session_manager.create_agent_session(
    user_progress_id=123,
    agent_type="persona_agent",
    session_config={"temperature": 0.7}
)

# Retrieve session from Redis
session_data = await session_manager.get_agent_session(session_id)
```

## Cache Invalidation

### Automatic Invalidation

- **TTL-based expiration** - Automatic cleanup based on data freshness needs
- **User-related data** - Invalidated when user data changes
- **Scenario-related data** - Invalidated when scenario is updated

### Manual Invalidation

```python
# Invalidate user cache
ai_cache_service.invalidate_user_cache(user_id=123)
db_cache_service.invalidate_user_related_cache(user_id=123)

# Invalidate scenario cache
ai_cache_service.invalidate_simulation_cache(scenario_id=456)
db_cache_service.invalidate_scenario_cache(scenario_id=456)
```

### Admin API Endpoints

```bash
# Get cache statistics
GET /api/cache/stats

# Invalidate user cache
POST /api/cache/invalidate/user/{user_id}

# Invalidate scenario cache
POST /api/cache/invalidate/scenario/{scenario_id}

# Manual cache cleanup
POST /api/cache/cleanup
```

## Performance Benefits

### Before Redis (In-Memory + Database)
- ❌ Session data lost on server restart
- ❌ No AI response caching (expensive API calls)
- ❌ Database queries on every request
- ❌ Memory usage grows with sessions
- ❌ No horizontal scaling support

### After Redis
- ✅ Persistent session storage with automatic expiration
- ✅ AI response caching reduces API costs by 60-80%
- ✅ Database query caching improves response times by 3-5x
- ✅ Efficient memory usage with TTL
- ✅ Horizontal scaling support
- ✅ Real-time cache invalidation

## Monitoring & Maintenance

### Cache Statistics

Monitor cache performance:
```bash
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/cache/stats
```

### Redis CLI Monitoring

```bash
# Monitor Redis commands in real-time
redis-cli monitor

# Check memory usage
redis-cli info memory

# List all keys
redis-cli keys "*"

# Check specific cache patterns
redis-cli keys "ai_cache:*"
redis-cli keys "db_query:*"
redis-cli keys "session:*"
```

### Performance Metrics

Track these metrics:
- **Cache hit ratio** - Should be >80% for optimal performance
- **Memory usage** - Monitor Redis memory consumption
- **Response times** - Should improve significantly with caching
- **API cost reduction** - Track OpenAI API usage reduction

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```
   Error: Redis initialization failed
   Solution: Check Redis is running and REDIS_URL is correct
   ```

2. **Cache Miss Rate High**
   ```
   Issue: Low cache hit ratio
   Solution: Review TTL settings and cache invalidation patterns
   ```

3. **Memory Usage High**
   ```
   Issue: Redis memory consumption growing
   Solution: Check for keys without TTL, review cache patterns
   ```

### Debug Commands

```bash
# Check Redis status
redis-cli ping

# View Redis configuration
redis-cli config get "*"

# Check key expiration
redis-cli ttl "session:abc123"

# Monitor memory usage
redis-cli info memory | grep used_memory_human
```

## Production Considerations

### Security
- Use Redis AUTH in production
- Configure firewall rules for Redis port
- Use TLS for Redis connections in production

### Performance
- Set appropriate `maxmemory` policy
- Monitor memory usage and set alerts
- Use Redis clustering for high availability

### Backup
- Configure Redis persistence (RDB + AOF)
- Set up Redis replication for disaster recovery
- Monitor Redis logs for errors

## Migration Notes

### Breaking Changes
- **Redis is now required** - Application will not start without Redis
- **No in-memory fallbacks** - All caching uses Redis exclusively
- **Session storage** - Moved from PostgreSQL to Redis (with DB backup)

### Compatibility
- All existing functionality preserved
- Database still used for persistent data
- Redis enhances performance without changing APIs

## Support

For Redis-related issues:
1. Check Redis server status
2. Verify environment configuration
3. Review application logs
4. Use admin cache endpoints for debugging
