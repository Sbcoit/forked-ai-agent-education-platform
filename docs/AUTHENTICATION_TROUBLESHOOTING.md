# Authentication System Troubleshooting Guide

## Overview
This document covers common authentication issues and their solutions in the n-aible EdTech platform.

## Issue: Login Redirects Back to Login Page (Race Condition)

### Symptoms
- User enters correct credentials
- Backend logs show successful login (200 OK)
- User gets redirected back to login page immediately
- Backend logs show logout being called right after login

### Root Cause
**Race condition** between authentication cookie setting and frontend initialization:

1. **Login succeeds** → Backend sets HttpOnly cookie
2. **Frontend redirects** → Auth context initializes
3. **Inactivity check runs** → Makes API call before cookie is available
4. **API call fails** → Auth system assumes user is not authenticated
5. **Auto-logout triggered** → User redirected back to login

### Technical Details

#### The Problem Code (Before Fix)
```typescript
const checkInactivity = React.useCallback(() => {
  const lastActivity = sessionStorage.getItem('last_activity')
  
  if (!lastActivity) {
    // PROBLEM: This makes an API call during initialization
    updateLastActivity() // Calls /users/activity endpoint
    return false
  }
  // ... rest of function
}, [updateLastActivity])
```

#### The Solution (After Fix)
```typescript
const checkInactivity = React.useCallback(() => {
  const lastActivity = sessionStorage.getItem('last_activity')
  
  if (!lastActivity) {
    // SOLUTION: Use client-side only tracking during initialization
    updateLastActivityLocal() // No API call, just local storage
    return false
  }
  // ... rest of function
}, [updateLastActivityLocal])
```

### Files Modified
- `frontend/lib/auth-context.tsx` - Lines 126 and 150

### The Fix Explained

#### What `updateLastActivityLocal()` Does:
```typescript
const updateLastActivityLocal = React.useCallback(() => {
  const timestamp = Date.now().toString()
  
  // Store in sessionStorage (no API call)
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('last_activity', timestamp)
    
    // Broadcast to other tabs
    try {
      const channel = new BroadcastChannel('auth-activity')
      channel.postMessage({ type: 'activity_update', timestamp })
      channel.close()
    } catch (error) {
      localStorage.setItem('auth_activity_broadcast', timestamp)
    }
  }
}, [])
```

#### What `updateLastActivity()` Does:
```typescript
const updateLastActivity = React.useCallback(async () => {
  // Reuse client-side logic
  updateLastActivityLocal()
  
  // ALSO makes server API call (problematic during initialization)
  try {
    await apiClient.apiRequest('/users/activity', {
      method: 'POST',
      body: JSON.stringify({ timestamp: parseInt(timestamp) })
    }, true)
  } catch (error) {
    console.debug('Server activity tracking failed')
  }
}, [updateLastActivityLocal])
```

### Prevention Strategy

#### When to Use Each Function:
- **`updateLastActivityLocal()`**: During initialization, when authentication state is uncertain
- **`updateLastActivity()`**: During normal operation, when user is confirmed authenticated

#### Key Principle:
**Never make authenticated API calls during the authentication initialization process.**

## Cookie Authentication Configuration

### Development Settings (Current)
```typescript
// Backend: utilities/auth.py
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  // 30 days for development

// Backend: main.py (login/register endpoints)
response.set_cookie(
  key="access_token",
  value=access_token,
  httponly=True,  // Security: Not accessible via JavaScript
  secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",  // HTTP OK in dev
  samesite="lax", // CSRF protection
  max_age=30 * 24 * 60 * 60  // 30 days
)
```

### Why 30 Days for Development?
- **No interruptions** during long coding sessions
- **No lost progress** during simulations
- **Fewer authentication hassles** while developing
- **Still secure** with HttpOnly cookies

### Production Recommendations
For production, consider:
- **Shorter token lifetime** (8-24 hours)
- **Auto-refresh mechanism** on activity
- **Secure=true** for HTTPS environments
- **Regular security audits**

## Debugging Authentication Issues

### Backend Logs to Watch For
```bash
# Successful flow
INFO: POST /users/login HTTP/1.1" 200 OK
INFO: GET /users/me HTTP/1.1" 200 OK

# Race condition pattern (FIXED)
INFO: POST /users/login HTTP/1.1" 200 OK
INFO: POST /users/activity HTTP/1.1" 401 Unauthorized  # ← This was the problem
INFO: POST /users/logout HTTP/1.1" 200 OK
```

### Frontend Console Logs
```javascript
// Development mode shows detailed auth flow
console.log('Checking authentication status...')
console.log('Fresh session detected, setting activity timestamp (client-side only)')
console.log('User authenticated successfully:', user.email)
```

### Browser Developer Tools
1. **Application Tab** → **Cookies** → Check for `access_token` cookie
2. **Network Tab** → Watch for failed `/users/activity` calls
3. **Console** → Look for authentication-related errors

## Related Issues

### CORS Configuration
Ensure backend allows credentials:
```python
# Backend: main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend API Configuration
Ensure credentials are included:
```typescript
// Frontend: lib/api.ts
const response = await fetch(buildApiUrl(endpoint), {
  ...options,
  headers,
  credentials: 'include', // Required for cookies
})
```

## Testing Authentication

### Manual Test Steps
1. **Clear browser cookies** for localhost
2. **Login with valid credentials**
3. **Check browser dev tools** for `access_token` cookie
4. **Verify no immediate logout** occurs
5. **Navigate to different pages** to test persistence

### API Test Commands
```bash
# Register user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123", ...}'

# Login and save cookie
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email": "test@example.com", "password": "test123"}'

# Test authenticated endpoint
curl -X GET http://localhost:8000/users/me \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

## Future Improvements

### Recommended Enhancements
1. **Token Refresh Mechanism** - Auto-refresh tokens before expiry
2. **Activity-Based Extension** - Extend session on user activity
3. **Multi-Device Support** - Handle multiple active sessions
4. **Session Management UI** - Allow users to view/revoke sessions

### Security Considerations
1. **Regular Token Rotation** - Even in development
2. **Secure Headers** - Add security headers for production
3. **Rate Limiting** - Prevent brute force attacks
4. **Audit Logging** - Track authentication events

---

**Last Updated:** September 27, 2024  
**Issue Fixed:** Login redirect race condition  
**Status:** ✅ Resolved
