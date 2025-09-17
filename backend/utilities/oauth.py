"""
OAuth utilities for Google authentication
"""
import httpx
import logging
from typing import Optional, Dict, Any
from database.connection import settings
from database.models import User
from sqlalchemy.orm import Session
from utilities.auth import create_access_token
import secrets
import hashlib
import base64
import hmac
from google.auth.transport import requests
from google.oauth2 import id_token
from fastapi import HTTPException, status

# Set up logger
logger = logging.getLogger(__name__)

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
    return hmac.compare_digest(state or "", stored_state or "")

def get_google_auth_url(state: str) -> str:
    """Generate Google OAuth authorization URL"""
    # Validate required OAuth configuration
    if not GOOGLE_CLIENT_ID or not GOOGLE_REDIRECT_URI:
        raise ValueError("Google OAuth is not configured. Missing GOOGLE_CLIENT_ID or GOOGLE_REDIRECT_URI")
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account"
    }
    
    from urllib.parse import urlencode
    query_string = urlencode(params)
    return f"{GOOGLE_AUTH_URL}?{query_string}"

async def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access token and id_token"""
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(GOOGLE_TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error exchanging code for token: {e}")
            return None

def verify_google_id_token(id_token_str: str) -> Dict[str, Any]:
    """
    Verify Google ID token and return validated claims
    
    Args:
        id_token_str: The ID token string from Google
        
    Returns:
        Dict containing validated claims
        
    Raises:
        HTTPException: If token verification fails
    """
    try:
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(
            id_token_str, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Validate issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token issuer"
            )
        
        # Validate audience
        if idinfo['aud'] != GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token audience"
            )
        
        # Check email verification
        if not idinfo.get('email_verified', False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not verified"
            )
        
        # Return validated claims
        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
            "sub": idinfo.get("sub"),
            "id": idinfo.get("sub"),
            "email_verified": idinfo.get("email_verified", False)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token verification failed: {str(e)}"
        )

async def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """Get user information from Google using access token (fallback method)"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(GOOGLE_USER_INFO_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting user info: {e}")
            return None

def find_existing_user_by_email(db: Session, email: str) -> Optional[User]:
    """Find existing user by email"""
    return db.query(User).filter(User.email == email).first()

def find_existing_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Find existing user by Google ID"""
    return db.query(User).filter(User.google_id == google_id).first()

def find_oauth_user_by_original_email(db: Session, original_email: str) -> Optional[User]:
    """Find OAuth user by their original email (before +google suffix)"""
    # First try exact match
    user = db.query(User).filter(User.email == original_email).first()
    if user:
        return user
    
    # If not found, try to find OAuth user with modified email
    # Split email robustly with rsplit to handle multiple @ symbols
    email_parts = original_email.rsplit('@', 1)
    if len(email_parts) != 2:
        return None
    
    base_email, domain = email_parts
    
    # Escape special regex characters in base_email and domain
    import re
    escaped_base = re.escape(base_email)
    escaped_domain = re.escape(domain)
    
    # Create precise regex pattern: base_email+google followed by one or more digits
    pattern = f"^{escaped_base}\\+google\\d+@{escaped_domain}$"
    
    # Use dialect-aware regex matching
    from sqlalchemy import text
    from database.connection import engine
    
    # Detect database dialect and use appropriate regex operator
    dialect_name = engine.dialect.name
    if dialect_name == 'postgresql':
        # PostgreSQL uses ~ operator
        return db.query(User).filter(
            User.email.op('~')(pattern),
            User.provider == "google"
        ).first()
    elif dialect_name in ['mysql', 'mariadb']:
        # MySQL uses REGEXP operator
        return db.query(User).filter(
            User.email.op('REGEXP')(pattern),
            User.provider == "google"
        ).first()
    elif dialect_name == 'sqlite':
        # SQLite uses REGEXP operator (if extension is loaded) or fallback to LIKE
        try:
            return db.query(User).filter(
                User.email.op('REGEXP')(pattern),
                User.provider == "google"
            ).first()
        except Exception:
            # Fallback to LIKE-based pattern matching for SQLite
            like_pattern = f"{base_email}+google%@{domain}"
            return db.query(User).filter(
                User.email.like(like_pattern),
                User.provider == "google"
            ).first()
    else:
        # Fallback to LIKE-based pattern matching for unsupported dialects
        like_pattern = f"{base_email}+google%@{domain}"
        return db.query(User).filter(
            User.email.like(like_pattern),
            User.provider == "google"
        ).first()

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
    
    # Check if user already exists with this Google ID
    google_id_value = google_data.get("sub") or google_data.get("id")
    existing_user = db.query(User).filter(User.google_id == google_id_value).first()
    if existing_user:
        # User already exists, update their information
        existing_user.full_name = google_data.get("name", existing_user.full_name)
        existing_user.avatar_url = google_data.get("picture", existing_user.avatar_url)
        existing_user.provider = "google"
        existing_user.is_verified = True
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # Check if user exists with this email
    existing_email_user = db.query(User).filter(User.email == google_data["email"]).first()
    if existing_email_user:
        # Link the OAuth provider to the existing user
        return link_google_to_existing_user(db, existing_email_user, google_data)
    
    # Create new user with original email
    user = User(
        email=google_data["email"],  # Keep original email
        full_name=google_data.get("name", ""),
        username=username,
        password_hash=None,  # OAuth users don't have passwords
        avatar_url=google_data.get("picture"),
        google_id=google_data.get("sub") or google_data.get("id"),
        provider="google",
        is_verified=True,  # Google accounts are considered verified
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def link_google_to_existing_user(db: Session, user: User, google_data: Dict[str, Any]) -> User:
    """Link Google OAuth to existing user account"""
    user.google_id = google_data.get("sub") or google_data.get("id")
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
