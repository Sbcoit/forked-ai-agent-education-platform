"""
Google OAuth API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

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
    create_oauth_user,
    link_google_to_existing_user,
    create_user_login_response
)

router = APIRouter(prefix="/auth", tags=["oauth"])

# Store OAuth states temporarily (in production, use Redis)
oauth_states: Dict[str, str] = {}

def cleanup_expired_states():
    """Clean up expired OAuth states (older than 10 minutes)"""
    import time
    current_time = time.time()
    expired_states = []
    
    for state, data in oauth_states.items():
        if isinstance(data, str) and data == "pending":
            # Simple cleanup - remove states older than 10 minutes
            # In production, store timestamps with states
            continue
        elif isinstance(data, str) and data.startswith("{"):
            # JSON data - could add timestamp checking here
            continue
    
    # For now, just limit the number of states
    if len(oauth_states) > 100:
        # Keep only the most recent 50 states
        states_to_remove = list(oauth_states.keys())[:-50]
        for state in states_to_remove:
            oauth_states.pop(state, None)

@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    # Clean up expired states before creating new one
    cleanup_expired_states()
    
    state = generate_state()
    oauth_states[state] = "pending"
    
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
    
    # Check if user exists with this email
    existing_email_user = find_existing_user_by_email(db, user_info["email"])
    
    if existing_email_user:
        # Account linking scenario
        oauth_states[state] = json.dumps({
            "action": "link_required",
            "google_data": user_info,
            "existing_user_id": existing_email_user.id
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
                "email": user_info["email"],
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture")
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
    
    # Get existing user
    existing_user = db.query(User).filter(User.id == request.existing_user_id).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if request.action == "link":
        # Link Google account to existing user
        linked_user = link_google_to_existing_user(db, existing_user, request.google_data)
        return create_user_login_response(linked_user)
    
    elif request.action == "create_separate":
        # Create separate account with Google OAuth
        new_user = create_oauth_user(db, request.google_data)
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
    if state_data == "pending":
        return {"status": "pending"}
    
    try:
        return {"status": "completed", "data": json.loads(state_data)}
    except json.JSONDecodeError:
        return {"status": "completed", "data": state_data}
