"""
Google OAuth API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
import time
import asyncio
from contextlib import asynccontextmanager

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
    get_google_user_info,
    find_existing_user_by_email,
    find_existing_user_by_google_id,
    find_oauth_user_by_original_email,
    create_oauth_user,
    link_google_to_existing_user,
    create_user_login_response
)

# Store OAuth states temporarily (in production, use Redis)
oauth_states: Dict[str, Dict[str, Any]] = {}

# Background cleanup task
cleanup_task = None

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
    current_time = time.time()
    expired_states = []
    
    for state, data in oauth_states.items():
        if isinstance(data, dict) and "created_at" in data:
            # Check if state is older than 10 minutes (600 seconds)
            if current_time - data["created_at"] > 600:
                expired_states.append(state)
    
    # Remove expired states
    for state in expired_states:
        oauth_states.pop(state, None)
    
    # Fallback: limit the number of states to 50 most recent
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
    oauth_states[state] = {
        "status": "pending",
        "created_at": time.time()
    }
    
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
    
    # Verify state
    if state not in oauth_states:
        # Clean up expired states and try again
        cleanup_expired_states()
        if state not in oauth_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter. Please try logging in again."
            )
    
    # Check if state is still valid (not expired)
    state_data = oauth_states[state]
    if isinstance(state_data, dict) and "created_at" in state_data:
        if time.time() - state_data["created_at"] > 600:  # 10 minutes
            oauth_states.pop(state, None)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State has expired. Please try logging in again."
            )
    
    # Exchange code for token
    token_data = await exchange_code_for_token(code)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token"
        )
    
    # Get user info from Google
    user_info = await get_google_user_info(token_data["access_token"])
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user information from Google"
        )
    
    # Check if user already exists with this Google ID
    existing_google_user = find_existing_user_by_google_id(db, user_info["id"])
    if existing_google_user:
        # User already linked, return login response
        oauth_states.pop(state, None)  # Clean up state
        return create_user_login_response(existing_google_user)
    
    # Check if user exists with this email (including OAuth users with modified emails)
    existing_email_user = find_oauth_user_by_original_email(db, user_info["email"])
    
    if existing_email_user:
        # Check if the existing user is already an OAuth user
        if existing_email_user.provider == "google":
            # User already has a Google account, just log them in
            oauth_states.pop(state, None)  # Clean up state
            return create_user_login_response(existing_email_user)
        else:
            # Account linking scenario for non-OAuth users
            # Sanitize Google data to remove sensitive fields
            sanitized_google_data = {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "sub": user_info.get("sub") or user_info.get("id"),
                "id": user_info.get("sub") or user_info.get("id")
            }
            
            existing_state = oauth_states.get(state, {})
            if isinstance(existing_state, dict):
                oauth_states[state].update({
                    "status": "link_required",
                    "intent": "link",
                    "google_data": sanitized_google_data,
                    "existing_user_id": existing_email_user.id,
                    "link_required": True
                })
            else:
                # If existing state is not a dict, create new one with metadata
                oauth_states[state] = {
                    "status": "link_required",
                    "intent": "link",
                    "created_at": time.time(),
                    "google_data": sanitized_google_data,
                    "existing_user_id": existing_email_user.id,
                    "link_required": True
                }
            
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
                    "email": user_info["email"],
                    "full_name": user_info.get("name", ""),
                    "avatar_url": user_info.get("picture"),
                    "google_id": user_info.get("sub") or user_info.get("id", "")
                },
                "state": state
            }
    
    # Create new user
    new_user = create_oauth_user(db, user_info)
    oauth_states.pop(state, None)  # Clean up state
    
    return create_user_login_response(new_user)

@router.post("/google/link")
async def link_google_account(
    request: AccountLinkingRequest,
    db: Session = Depends(get_db)
):
    """Link Google account to existing user or create separate account"""
    
    # Validate OAuth state
    if not request.state or request.state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing OAuth state"
        )
    
    # Check if state is still valid (not expired)
    state_data = oauth_states.get(request.state)
    if not state_data or not isinstance(state_data, dict) or "created_at" not in state_data:
        # Invalid or malformed state data - treat as expired
        oauth_states.pop(request.state, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state has expired or is invalid. Please try again."
        )
    
    if time.time() - state_data["created_at"] > 600:  # 10 minutes
        oauth_states.pop(request.state, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state has expired. Please try again."
        )
    
    # Get existing user
    existing_user = db.query(User).filter(User.id == request.existing_user_id).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if request.action == "link":
        # Convert OAuthUserData to format expected by utility functions
        google_user_data = {
            "email": request.google_data.email,
            "name": request.google_data.full_name,
            "picture": request.google_data.avatar_url,
            "sub": request.google_data.google_id,
            "id": request.google_data.google_id
        }
        # Link Google account to existing user
        linked_user = link_google_to_existing_user(db, existing_user, google_user_data)
        oauth_states.pop(request.state, None)  # Clean up state
        return create_user_login_response(linked_user)
    
    elif request.action == "create_separate":
        # Convert OAuthUserData to format expected by utility functions
        google_user_data = {
            "email": request.google_data.email,
            "name": request.google_data.full_name,
            "picture": request.google_data.avatar_url,
            "sub": request.google_data.google_id,
            "id": request.google_data.google_id
        }
        # Create separate account with Google OAuth
        new_user = create_oauth_user(db, google_user_data)
        oauth_states.pop(request.state, None)  # Clean up state
        return create_user_login_response(new_user)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'link' or 'create_separate'"
        )

@router.get("/google/status/{state}")
async def get_oauth_status(state: str):
    """Get OAuth status for a given state"""
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth state not found or expired"
        )
    
    state_data = oauth_states[state]
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
