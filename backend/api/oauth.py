"""
Google OAuth API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import time
import asyncio
import logging
import os
import threading
import base64
from contextlib import asynccontextmanager
from cryptography.fernet import Fernet

from database.connection import get_db
from database.models import User
from database.schemas import (
    GoogleOAuthRequest, 
    AccountLinkingRequest, 
    OAuthUserData,
    UserLoginResponse
)
from utilities.oauth import (
    generate_state,
    verify_state,
    get_google_auth_url,
    exchange_code_for_token,
    verify_google_id_token,
    get_google_user_info,
    find_existing_user_by_email,
    find_existing_user_by_google_id,
    find_oauth_user_by_original_email,
    create_oauth_user,
    link_google_to_existing_user,
    create_user_login_response
)

# Logger for OAuth operations
logger = logging.getLogger(__name__)

class OAuthStateStore:
    """Persistent OAuth state storage with Redis or database fallback"""
    
    def __init__(self):
        self.redis_client = None
        self.fallback_to_memory = True
        self._init_redis()
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption cipher for state payloads"""
        try:
            encryption_key = os.getenv('OAUTH_ENCRYPTION_KEY')
            if not encryption_key:
                # Check if we're in production environment
                is_production = (
                    os.getenv('ENVIRONMENT', '').lower() == 'production' or
                    os.getenv('ENV', '').lower() == 'production' or
                    os.getenv('FLASK_ENV', '').lower() == 'production' or
                    os.getenv('APP_ENV', '').lower() == 'production'
                )
                
                if is_production:
                    raise ValueError("OAUTH_ENCRYPTION_KEY is required in production environment")
                else:
                    # Generate a new key for development only
                    key = Fernet.generate_key()
                    logger.warning("No OAUTH_ENCRYPTION_KEY found, using generated key for development. Set OAUTH_ENCRYPTION_KEY in production!")
                    self.cipher = Fernet(key)
            else:
                # Use provided key (should be base64 encoded)
                if len(encryption_key) != 44:  # Fernet keys are 44 chars when base64 encoded
                    raise ValueError("OAUTH_ENCRYPTION_KEY must be a valid Fernet key (44 characters)")
                self.cipher = Fernet(encryption_key.encode())
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            # Fallback to no encryption (not recommended for production)
            self.cipher = None
    
    def _init_redis(self):
        """Initialize Redis client if available"""
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.fallback_to_memory = False
            logger.info("OAuth state store initialized with Redis")
        except Exception as e:
            logger.warning(f"Redis not available, falling back to in-memory storage: {e}")
            self.redis_client = None
            self.fallback_to_memory = True
    
    def set_state(self, state: str, data: Dict[str, Any], ttl: int = 600) -> bool:
        """Store OAuth state with TTL (default 10 minutes)"""
        try:
            # Add created_at timestamp
            data['created_at'] = time.time()
            
            # Encrypt the payload if cipher is available
            if self.cipher:
                try:
                    json_payload = json.dumps(data)
                    encrypted_payload = self.cipher.encrypt(json_payload.encode())
                    encrypted_data = base64.b64encode(encrypted_payload).decode('utf-8')
                except Exception as e:
                    logger.error(f"Failed to encrypt state data: {e}")
                    return False
            else:
                # No encryption available, store as JSON
                encrypted_data = json.dumps(data)
            
            if self.redis_client and not self.fallback_to_memory:
                self.redis_client.setex(state, ttl, encrypted_data)
                return True
            else:
                # Fallback to in-memory storage
                with oauth_states_lock:
                    # Check if we need to clean up before adding new state
                    if len(oauth_states) >= 50:
                        # Sort by created_at and keep only the 50 most recent
                        def get_created_at(item):
                            value = item[1]
                            if isinstance(value, dict):
                                return value.get("created_at", 0)
                            else:
                                return 0
                        
                        sorted_states = sorted(oauth_states.items(), 
                                             key=get_created_at, 
                                             reverse=True)
                        oauth_states.clear()
                        for state_key, data in sorted_states[:50]:
                            oauth_states[state_key] = data
                    
                    oauth_states[state] = encrypted_data
                return True
        except Exception as e:
            logger.error(f"Failed to store OAuth state: {e}")
            return False
    
    def get_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Retrieve OAuth state data"""
        try:
            if self.redis_client and not self.fallback_to_memory:
                encrypted_data = self.redis_client.get(state)
                if not encrypted_data:
                    return None
            else:
                # Fallback to in-memory storage
                with oauth_states_lock:
                    encrypted_data = oauth_states.get(state)
                    if not encrypted_data:
                        return None
            
            # Decrypt the payload if cipher is available
            if self.cipher:
                try:
                    encrypted_payload = base64.b64decode(encrypted_data.encode('utf-8'))
                    decrypted_payload = self.cipher.decrypt(encrypted_payload)
                    return json.loads(decrypted_payload.decode('utf-8'))
                except Exception as e:
                    logger.error(f"Failed to decrypt state data: {e}")
                    return None
            else:
                # No encryption, parse as JSON
                return json.loads(encrypted_data)
        except Exception as e:
            logger.error(f"Failed to retrieve OAuth state: {e}")
            return None
    
    def delete_state(self, state: str) -> bool:
        """Delete OAuth state"""
        try:
            if self.redis_client and not self.fallback_to_memory:
                self.redis_client.delete(state)
                return True
            else:
                # Fallback to in-memory storage
                with oauth_states_lock:
                    oauth_states.pop(state, None)
                return True
        except Exception as e:
            logger.error(f"Failed to delete OAuth state: {e}")
            return False

# Initialize OAuth state store
oauth_state_store = OAuthStateStore()

# Fallback in-memory storage (used when Redis is not available)
oauth_states: Dict[str, Dict[str, Any]] = {}

# Lock for thread-safe access to oauth_states
oauth_states_lock = threading.Lock()

# Background cleanup task
cleanup_task = None

def validate_oauth_state(state: str) -> Dict[str, Any]:
    """Validate OAuth state and return state data if valid"""
    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing OAuth state"
        )
    
    # Get state data from store
    state_data = oauth_state_store.get_state(state)
    if not state_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing OAuth state"
        )
    
    # Check if state is still valid (not expired) - only for in-memory fallback
    if oauth_state_store.fallback_to_memory:
        if not isinstance(state_data, dict) or "created_at" not in state_data:
            # Invalid or malformed state data - treat as expired
            oauth_state_store.delete_state(state)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth state has expired or is invalid. Please try again."
            )
        
        if time.time() - state_data["created_at"] > 600:  # 10 minutes
            oauth_state_store.delete_state(state)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth state has expired. Please try again."
            )
    
    return state_data

async def periodic_cleanup():
    """Periodic cleanup task that runs every 5 minutes"""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            cleanup_expired_states()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[ERROR] Periodic cleanup failed: {e}")

@asynccontextmanager
async def lifespan(app):
    """FastAPI lifespan handler for startup and shutdown"""
    global cleanup_task
    # Startup
    cleanup_task = asyncio.create_task(periodic_cleanup())
    print("[INFO] Started OAuth state cleanup task")
    yield
    # Shutdown
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        print("[INFO] Stopped OAuth state cleanup task")

router = APIRouter(prefix="/auth", tags=["oauth"])

def cleanup_expired_states():
    """Clean up expired OAuth states (older than 10 minutes)"""
    # For Redis, TTL is handled automatically
    # For in-memory fallback, clean up expired states
    if oauth_state_store.fallback_to_memory:
        current_time = time.time()
        expired_states = []
        
        # Create a snapshot to avoid race conditions
        with oauth_states_lock:
            states_snapshot = list(oauth_states.items())
        
        for state, data in states_snapshot:
            if isinstance(data, dict) and "created_at" in data:
                # Check if state is older than 10 minutes (600 seconds)
                if current_time - data["created_at"] > 600:
                    expired_states.append(state)
        
        # Remove expired states
        for state in expired_states:
            oauth_state_store.delete_state(state)
        
        # Fallback: limit the number of states to 50 most recent
        with oauth_states_lock:
            if len(oauth_states) > 50:
                # Sort by created_at and keep only the 50 most recent
                # Handle both dict and string values safely
                def get_created_at(item):
                    value = item[1]
                    if isinstance(value, dict):
                        return value.get("created_at", 0)
                    else:
                        return 0
                
                sorted_states = sorted(oauth_states.items(), 
                                     key=get_created_at, 
                                     reverse=True)
                oauth_states.clear()
                for state, data in sorted_states[:50]:
                    oauth_states[state] = data

@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    # Clean up expired states before creating new one
    cleanup_expired_states()
    
    state = generate_state()
    oauth_state_store.set_state(state, {
        "status": "pending",
        "created_at": time.time()
    })
    
    auth_url = get_google_auth_url(state)
    return {"auth_url": auth_url, "state": state}

@router.get("/google/callback")
async def google_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code or state"
        )
    
    # Verify state using the store abstraction
    state_data = oauth_state_store.get_state(state)
    if not state_data:
        # Clean up expired states and try again
        cleanup_expired_states()
        state_data = oauth_state_store.get_state(state)
        if not state_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter. Please try logging in again."
            )
    
    # Validate OAuth state
    state_data = validate_oauth_state(state)
    
    # Exchange code for token
    token_data = await exchange_code_for_token(code)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token"
        )
    
    # Verify id_token for secure user authentication
    if not token_data.get("id_token"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing ID token in OAuth response"
        )
    
    try:
        # Verify the ID token and get validated claims
        user_info = verify_google_id_token(token_data["id_token"])
    except HTTPException:
        # Re-raise HTTP exceptions from verification
        raise
    except Exception as e:
        logger.error(f"ID token verification failed: {e}")
        # Fallback to userinfo endpoint if id_token verification fails
        logger.warning("Falling back to userinfo endpoint")
        user_info = await get_google_user_info(token_data["access_token"])
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google"
            )
    
    # Extract Google ID using OIDC 'sub' claim with 'id' fallback
    google_id = user_info.get("sub") or user_info.get("id")
    if not google_id:
        raise HTTPException(status_code=400, detail="Invalid Google user info (missing subject)")
    
    # Check if user already exists with this Google ID
    existing_google_user = find_existing_user_by_google_id(db, google_id)
    if existing_google_user:
        # User already linked, return login response
        oauth_state_store.delete_state(state)  # Clean up state
        return create_user_login_response(existing_google_user)
    
    # Check if user exists with this email (including OAuth users with modified emails)
    existing_email_user = find_oauth_user_by_original_email(db, user_info.get("email", ""))
    
    if existing_email_user:
        # Check if the existing user is already an OAuth user
        if existing_email_user.provider == "google":
            # User already has a Google account, just log them in
            oauth_state_store.delete_state(state)  # Clean up state
            return create_user_login_response(existing_email_user)
        else:
            # Account linking scenario for non-OAuth users
            existing_state = oauth_state_store.get_state(state) or {}
            oauth_state_store.set_state(state, {
                "status": "link_required",
                "created_at": existing_state.get("created_at") if isinstance(existing_state, dict) else None,
                "payload": {
                    "google_data": {
                        "id": google_id,
                        "email": user_info.get("email", ""),
                        "name": user_info.get("name", ""),
                        "picture": user_info.get("picture")
                    },
                    "existing_user_id": existing_email_user.id
                }
            })
            
            return {
                "action": "link_required",
                "message": "An account with this email already exists. Would you like to link your Google account?",
                "existing_user": {
                    "id": existing_email_user.id,
                    "email": existing_email_user.email,
                    "full_name": existing_email_user.full_name,
                    "provider": existing_email_user.provider
                },
                "google_data": {
                    "email": user_info.get("email", ""),
                    "full_name": user_info.get("name", ""),
                    "avatar_url": user_info.get("picture"),
                    "google_id": google_id
                },
                "state": state
            }
    
    # Create new user
    new_user = create_oauth_user(db, {**user_info, "id": google_id})
    oauth_state_store.delete_state(state)  # Clean up state
    
    return create_user_login_response(new_user)

@router.post("/google/link")
async def link_google_account(
    request: AccountLinkingRequest,
    db: Session = Depends(get_db)
):
    """Link Google account to existing user or create separate account"""
    
    # Validate OAuth state and get server-stored google_data
    state_data = validate_oauth_state(request.state)
    
    # Extract google_data from server-stored state (not client-supplied)
    if not isinstance(state_data, dict) or "payload" not in state_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state - missing payload data"
        )
    
    payload = state_data["payload"]
    if "google_data" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state - missing Google user data"
        )
    
    # Use server-stored google_data (prevents account takeover)
    server_google_data = payload["google_data"]
    
    # Get existing user
    existing_user = db.query(User).filter(User.id == request.existing_user_id).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if request.action == "link":
        # Convert server-stored google_data to format expected by utility functions
        google_user_data = {
            "email": server_google_data["email"],
            "name": server_google_data["name"],
            "picture": server_google_data["picture"],
            "sub": server_google_data["id"],
            "id": server_google_data["id"]
        }
        # Link Google account to existing user
        linked_user = link_google_to_existing_user(db, existing_user, google_user_data)
        oauth_state_store.delete_state(request.state)  # Clean up state
        return create_user_login_response(linked_user)
    
    elif request.action == "create_separate":
        # Convert server-stored google_data to format expected by utility functions
        google_user_data = {
            "email": server_google_data["email"],
            "name": server_google_data["name"],
            "picture": server_google_data["picture"],
            "sub": server_google_data["id"],
            "id": server_google_data["id"]
        }
        # Create separate account with Google OAuth
        new_user = create_oauth_user(db, google_user_data)
        oauth_state_store.delete_state(request.state)  # Clean up state
        return create_user_login_response(new_user)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'link' or 'create_separate'"
        )

@router.get("/google/status/{state}")
async def get_oauth_status(state: str):
    """Get OAuth status for a given state"""
    state_data = oauth_state_store.get_state(state)
    if not state_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth state not found or expired"
        )
    
    if isinstance(state_data, dict):
        link_required = state_data.get("link_required", False)
        if state_data.get("status") == "pending":
            return {"status": "pending", "link_required": link_required}
        else:
            return {"status": "completed", "data": state_data, "link_required": link_required}
    else:
        # Handle legacy string format
        if state_data == "pending":
            return {"status": "pending", "link_required": False}
        
        try:
            parsed = json.loads(state_data)
            link_required = parsed.get("link_required", False)
            return {"status": "completed", "data": parsed, "link_required": link_required}
        except json.JSONDecodeError:
            return {"status": "completed", "data": state_data, "link_required": False}
