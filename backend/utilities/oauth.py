"""
OAuth utilities for Google authentication
"""
import httpx
from typing import Optional, Dict, Any
from database.connection import settings
from database.models import User
from sqlalchemy.orm import Session
from utilities.auth import create_access_token
import secrets
import hashlib
import base64

# Google OAuth configuration
GOOGLE_CLIENT_ID = settings.google_client_id
GOOGLE_CLIENT_SECRET = settings.google_client_secret
GOOGLE_REDIRECT_URI = settings.google_redirect_uri

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def generate_state() -> str:
    """Generate a random state parameter for OAuth security"""
    return secrets.token_urlsafe(32)

def verify_state(state: str, stored_state: str) -> bool:
    """Verify the OAuth state parameter"""
    return state == stored_state

def get_google_auth_url(state: str) -> str:
    """Generate Google OAuth authorization URL"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{GOOGLE_AUTH_URL}?{query_string}"

async def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access token"""
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GOOGLE_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error exchanging code for token: {e}")
            return None

async def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """Get user information from Google using access token"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(GOOGLE_USER_INFO_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error getting user info: {e}")
            return None

def find_existing_user_by_email(db: Session, email: str) -> Optional[User]:
    """Find existing user by email"""
    return db.query(User).filter(User.email == email).first()

def find_existing_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Find existing user by Google ID"""
    return db.query(User).filter(User.google_id == google_id).first()

def create_oauth_user(db: Session, google_data: Dict[str, Any]) -> User:
    """Create a new user from Google OAuth data"""
    # Generate username from email
    username = google_data["email"].split("@")[0]
    
    # Ensure username is unique
    original_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{original_username}{counter}"
        counter += 1
    
    user = User(
        email=google_data["email"],
        full_name=google_data.get("name", ""),
        username=username,
        password_hash=None,  # OAuth users don't have passwords
        avatar_url=google_data.get("picture"),
        google_id=google_data["id"],
        provider="google",
        is_verified=True,  # Google accounts are considered verified
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def link_google_to_existing_user(db: Session, user: User, google_data: Dict[str, Any]) -> User:
    """Link Google OAuth to existing user account"""
    user.google_id = google_data["id"]
    user.provider = "google"  # Update provider to google
    
    # Update profile data from Google if not already set
    if not user.avatar_url and google_data.get("picture"):
        user.avatar_url = google_data["picture"]
    
    db.commit()
    db.refresh(user)
    return user

def create_user_login_response(user: User) -> Dict[str, Any]:
    """Create login response for OAuth user"""
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "username": user.username,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "role": user.role,
            "published_scenarios": user.published_scenarios,
            "total_simulations": user.total_simulations,
            "reputation_score": user.reputation_score,
            "profile_public": user.profile_public,
            "allow_contact": user.allow_contact,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "provider": user.provider,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    }
