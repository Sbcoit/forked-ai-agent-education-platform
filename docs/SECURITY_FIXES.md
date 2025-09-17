# Security Fixes and Configuration

This document outlines the security fixes implemented and the required configuration settings.

## Vector Database Configuration

### Environment Variable: USE_PGVECTOR

The application now uses an explicit configuration setting to determine the vector database column type:

- **USE_PGVECTOR=true** (default): Uses pgvector extension for vector operations
- **USE_PGVECTOR=false**: Uses JSON storage for vector data

### Required Setup

1. **For pgvector environments** (USE_PGVECTOR=true):
   ```bash
   # Install pgvector extension in PostgreSQL
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **For JSON environments** (USE_PGVECTOR=false):
   - No additional setup required
   - Vector data will be stored as JSON

### Startup Validation

The application now includes startup checks that validate:
- The pgvector extension is available when USE_PGVECTOR=true
- The vector_embeddings table column type matches the configuration
- Fails fast with clear error messages if there's a mismatch

## Security Fixes

### 1. Migration Chain Fix
- Fixed incorrect down_revision in `fix_vector_embeddings_column.py`
- Migration now properly depends on `add_langchain_integration_001`

### 2. SQL Injection Prevention
- Replaced f-string SQL queries with parameterized queries in `vector_store.py`
- Added input validation for collection names
- Collection names are now restricted to alphanumeric characters, underscores, and hyphens

### 3. Authentication Security
- **CRITICAL**: Removed unsafe localStorage-based token storage
- Added security warnings for remaining localStorage usage
- Implemented TODO comments for secure authentication implementation

### Required Authentication Implementation

The current authentication system is **NOT SECURE** and requires immediate implementation of:

1. **Authorization Code + PKCE Flow** for SPA
2. **Secure Cookie Storage**: Use Secure, HttpOnly, SameSite cookies for refresh tokens
3. **In-Memory Access Tokens**: Keep access tokens only in JavaScript memory (short-lived)
4. **Backend Token Management**: Handle token refresh via backend endpoints
5. **XSS Mitigations**: Implement Content Security Policy, input/output encoding
6. **CSRF Protection**: Add CSRF protections for cookie-based flows

### Security Warnings

The application currently displays security warnings in the console for:
- Unsafe localStorage token storage
- Access tokens not being stored securely

These warnings will continue until the secure authentication system is implemented.

## Configuration Summary

| Setting | Default | Description |
|---------|---------|-------------|
| USE_PGVECTOR | true | Enable pgvector extension for vector operations |
| DATABASE_URL | postgresql://localhost:5432/ai_agent_platform | Database connection URL |
| ENVIRONMENT | development | Application environment |

## Next Steps

1. **Immediate**: Implement secure authentication system
2. **Testing**: Verify all environments use consistent vector column types
3. **Monitoring**: Set up monitoring for authentication security
4. **Documentation**: Update deployment guides with security requirements
