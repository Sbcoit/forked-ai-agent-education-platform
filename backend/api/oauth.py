# """
# Google OAuth API endpoints
# """
# from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
# from fastapi.responses import RedirectResponse, HTMLResponse
# from sqlalchemy.orm import Session
# from typing import Dict, Any, Optional
# import json
# import time
# import asyncio
# import logging
# import os
# import threading
# import base64
# from contextlib import asynccontextmanager
# from cryptography.fernet import Fernet

# from database.connection import get_db
# from database.models import User
# from database.schemas import (
#     GoogleOAuthRequest, 
#     AccountLinkingRequest, 
#     OAuthUserData,
#     UserLoginResponse,
#     RoleSelectionRequest
# )
# from utilities.oauth import (
#     generate_state,
#     verify_state,
#     get_google_auth_url,
#     exchange_code_for_token,
#     verify_google_id_token,
#     get_google_user_info,
#     find_existing_user_by_email,
#     find_existing_user_by_google_id,
#     find_oauth_user_by_original_email,
#     create_oauth_user,
#     link_google_to_existing_user,
#     create_user_login_response
# )
# from utilities.auth import create_access_token

# # Logger for OAuth operations
# logger = logging.getLogger(__name__)

# class OAuthStateStore:
#     """Persistent OAuth state storage using Redis"""
    
#     def __init__(self):
#         from utilities.redis_manager import redis_manager
#         self.redis = redis_manager
#         self._init_encryption()
    
#     def _init_encryption(self):
#         """Initialize encryption cipher for state payloads"""
#         encryption_key = os.getenv('OAUTH_ENCRYPTION_KEY')
#         if not encryption_key:
#             # Check if we're in production environment
#             is_production = (
#                 os.getenv('ENVIRONMENT', '').lower() == 'production' or
#                 os.getenv('ENV', '').lower() == 'production' or
#                 os.getenv('FLASK_ENV', '').lower() == 'production' or
#                 os.getenv('APP_ENV', '').lower() == 'production'
#             )
            
#             if is_production:
#                 raise ValueError("OAUTH_ENCRYPTION_KEY is required in production environment")
#             else:
#                 # Development mode: use or generate persistent key
#                 try:
#                     dev_key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.oauth_encryption_key')
#                     key = self._get_or_create_dev_key(dev_key_file)
#                     logger.warning("No OAUTH_ENCRYPTION_KEY found, using development key from file. Set OAUTH_ENCRYPTION_KEY in production!")
#                     self.cipher = Fernet(key)
#                 except Exception as e:
#                     logger.error(f"Failed to initialize development encryption: {e}")
#                     # Fallback to no encryption for development
#                     self.cipher = None
#         else:
#             # Validate and use provided key
#             try:
#                 # Convert string to bytes using UTF-8 encoding
#                 key_bytes = encryption_key.encode('utf-8')
#                 self.cipher = Fernet(key_bytes)
#             except Exception as e:
#                 raise ValueError(f"Invalid OAUTH_ENCRYPTION_KEY: {e}. Key must be a valid base64-encoded Fernet key.")
    
#     def _get_or_create_dev_key(self, key_file_path: str) -> bytes:
#         """Get existing dev key or create and persist a new one"""
#         try:
#             # Try to read existing key
#             if os.path.exists(key_file_path):
#                 with open(key_file_path, 'rb') as f:
#                     key = f.read()
#                 # Validate the key by trying to create a Fernet instance
#                 Fernet(key)  # This will raise an exception if invalid
#                 return key
#         except Exception as e:
#             logger.warning(f"Invalid or corrupted dev key file, generating new one: {e}")
        
#         # Generate new key and persist it
#         key = Fernet.generate_key()
#         try:
#             with open(key_file_path, 'wb') as f:
#                 f.write(key)
#             # Set restrictive permissions (owner read/write only)
#             os.chmod(key_file_path, 0o600)
#         except Exception as e:
#             logger.error(f"Failed to persist dev encryption key: {e}")
#             # Continue with the generated key even if we can't persist it
        
#         return key
    
    
#     def set_state(self, state: str, data: Dict[str, Any], ttl: int = 600) -> bool:
#         """Store OAuth state with TTL (default 10 minutes)"""
#         try:
#             # Add created_at timestamp
#             data['created_at'] = time.time()
            
#             # Encrypt the payload if cipher is available
#             if self.cipher:
#                 try:
#                     json_payload = json.dumps(data)
#                     encrypted_payload = self.cipher.encrypt(json_payload.encode())
#                     encrypted_data = base64.b64encode(encrypted_payload).decode('utf-8')
#                 except Exception as e:
#                     logger.error(f"Failed to encrypt state data: {e}")
#                     return False
#             else:
#                 # No encryption available, store as JSON
#                 encrypted_data = json.dumps(data)
            
#             # Use Redis manager to store the state
#             return self.redis.set(state, encrypted_data, ttl)
#         except Exception as e:
#             logger.error(f"Failed to store OAuth state: {e}")
#             return False
    
#     def get_state(self, state: str) -> Optional[Dict[str, Any]]:
#         """Retrieve OAuth state data"""
#         try:
#             encrypted_data = self.redis.get(state)
#             if not encrypted_data:
#                 return None
            
#             # Decrypt the payload if cipher is available
#             if self.cipher:
#                 try:
#                     # Redis returns strings with decode_responses=True, so use directly
#                     encrypted_payload = base64.b64decode(encrypted_data)
#                     decrypted_payload = self.cipher.decrypt(encrypted_payload)
#                     return json.loads(decrypted_payload.decode('utf-8'))
#                 except Exception as e:
#                     logger.error(f"Failed to decrypt state data: {e}")
#                     return None
#             else:
#                 # No encryption, parse as JSON
#                 return json.loads(encrypted_data)
#         except Exception as e:
#             logger.error(f"Failed to retrieve OAuth state: {e}")
#             return None
    
#     def delete_state(self, state: str) -> bool:
#         """Delete OAuth state"""
#         try:
#             return self.redis.delete(state)
#         except Exception as e:
#             logger.error(f"Failed to delete OAuth state: {e}")
#             return False

# # Create the OAuth router
# router = APIRouter(prefix="/auth", tags=["oauth"])

# # Initialize OAuth state store
# oauth_state_store = OAuthStateStore()

# # Global cache to track used authorization codes (in-memory, will reset on restart)
# used_authorization_codes = set()

# @router.post("/clear-cache")
# async def clear_oauth_cache():
#     """Clear the OAuth authorization code cache (for debugging)"""
#     global used_authorization_codes
#     cleared_count = len(used_authorization_codes)
#     used_authorization_codes.clear()
#     logger.info(f"Cleared {cleared_count} authorization codes from cache")
#     return {"message": f"Cleared {cleared_count} authorization codes from cache"}

# @router.get("/google/login")
# async def google_login():
#     """Initiate Google OAuth login"""
#     try:
#         state = generate_state()
#         auth_url = get_google_auth_url(state)
        
#         # Store initial state
#         oauth_state_store.set_state(state, {"status": "pending", "created_at": time.time()})
        
#         return {"auth_url": auth_url, "state": state}
#     except Exception as e:
#         logger.error(f"Google login initiation failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to initiate Google login"
#         )

# @router.post("/google/select-role")
# async def select_role_for_oauth(
#     role_data: RoleSelectionRequest,
#     response: Response,
#     db: Session = Depends(get_db)
# ):
#     """Select role for OAuth user after Google authentication"""
    
#     # Validate OAuth state
#     state_data = validate_oauth_state(role_data.state)
#     if not state_data:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired OAuth state"
#         )
    
#     # Check if this is a role selection request
#     if state_data.get("status") != "role_selection_required":
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Role selection not required for this OAuth flow"
#         )
    
#     # Get user info from state
#     user_info = state_data.get("user_info")
#     if not user_info:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Missing user information in OAuth state"
#         )
    
#     # Create new user with selected role
#     new_user = create_oauth_user(db, user_info, role=role_data.role)
    
#     # Set HttpOnly cookie for new user
#     access_token = create_access_token(data={"sub": str(new_user.id)})
#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#         httponly=True,  # HttpOnly cookie - not accessible via JavaScript
#         secure=False,    # Set to False for development (HTTP), True for production (HTTPS)
#         samesite="lax", # CSRF protection
#         max_age=30 * 60  # 30 minutes (same as token expiry)
#     )
    
#     # Clean up state
#     oauth_state_store.delete_state(role_data.state)
    
#     return create_user_login_response(new_user)

# def validate_oauth_state(state: str) -> Dict[str, Any]:
#     """Validate OAuth state and return state data if valid"""
#     if not state:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or missing OAuth state"
#         )
    
#     # Get state data from store
#     state_data = oauth_state_store.get_state(state)
#     if not state_data:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or missing OAuth state"
#         )
    
#     # Redis handles TTL expiration automatically
#     # If state_data is None, it means the state has expired or doesn't exist
    
#     return state_data

# async def periodic_cleanup():
#     """Periodic cleanup task that runs every 5 minutes"""
#     while True:
#         try:
#             await asyncio.sleep(300)  # 5 minutes
#             cleanup_expired_states()
#         except asyncio.CancelledError:
#             break
#         except Exception as e:
#             print(f"[ERROR] Periodic cleanup failed: {e}")

# @asynccontextmanager
# async def lifespan(app):
#     """FastAPI lifespan handler for startup and shutdown"""
#     global cleanup_task
#     # Startup
#     cleanup_task = asyncio.create_task(periodic_cleanup())
#     print("[INFO] Started OAuth state cleanup task")
#     yield
#     # Shutdown
#     if cleanup_task:
#         cleanup_task.cancel()
#         try:
#             await cleanup_task
#         except asyncio.CancelledError:
#             pass
#         print("[INFO] Stopped OAuth state cleanup task")

# def cleanup_expired_states():
#     """Clean up expired OAuth states (older than 10 minutes)"""
#     # For Redis, TTL is handled automatically
#     # Redis handles TTL expiration automatically
#     # No manual cleanup needed for Redis-based storage

# @router.get("/google/login")
# async def google_login():
#     """Initiate Google OAuth login"""
#     # Clean up expired states before creating new one
#     cleanup_expired_states()
    
#     state = generate_state()
#     oauth_state_store.set_state(state, {
#         "status": "pending",
#         "created_at": time.time()
#     })
    
#     auth_url = get_google_auth_url(state)
#     return {"auth_url": auth_url, "state": state}

# @router.post("/google/select-role")
# async def select_role_for_oauth(
#     role_data: RoleSelectionRequest,
#     response: Response,
#     db: Session = Depends(get_db)
# ):
#     """Select role for OAuth user after Google authentication"""
    
#     # Validate OAuth state
#     state_data = validate_oauth_state(role_data.state)
#     if not state_data:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired OAuth state"
#         )
    
#     # Check if this is a role selection request
#     if state_data.get("status") != "role_selection_required":
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Role selection not required for this OAuth flow"
#         )
    
#     # Get user info from state
#     user_info = state_data.get("user_info")
#     if not user_info:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Missing user information in OAuth state"
#         )
    
#     # Create new user with selected role
#     new_user = create_oauth_user(db, user_info, role=role_data.role)
    
#     # Set HttpOnly cookie for new user
#     access_token = create_access_token(data={"sub": str(new_user.id)})
#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#         httponly=True,  # HttpOnly cookie - not accessible via JavaScript
#         secure=False,    # Set to False for development (HTTP), True for production (HTTPS)
#         samesite="lax", # CSRF protection
#         max_age=30 * 60  # 30 minutes (same as token expiry)
#     )
    
#     # Clean up state
#     oauth_state_store.delete_state(role_data.state)
    
#     return create_user_login_response(new_user)

# @router.get("/google/callback")
# async def google_callback(
#     code: str = None,
#     state: str = None,
#     error: str = None,
#     response: Response = None,
#     db: Session = Depends(get_db)
# ):
#     """Handle Google OAuth callback"""
#     if error:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"OAuth error: {error}"
#         )
    
#     if not code or not state:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Missing authorization code or state"
#             )
#     # Validate OAuth state
#     state_data = validate_oauth_state(state)
#     if not state_data:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired state parameter. Please try logging in again."
#         )
    
#     # Check if this callback has already been processed
#     if state_data.get("status") == "completed":
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="OAuth callback has already been processed. Please try logging in again."
#         )
    
#     # Check if this authorization code has already been used globally
#     if code in used_authorization_codes:
#         logger.warning(f"Authorization code already used: {code[:10]}...")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Authorization code has already been used. Please try logging in again."
#         )
    
#     # Check if this authorization code has already been used for this state
#     if state_data.get("status") == "processing":
#         logger.warning(f"Authorization code already being processed for state: {state}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="OAuth callback is already being processed. Please wait."
#         )
    
#     # Mark state as being processed to prevent duplicate calls
#     # Don't add code to used set yet - only after successful user creation
#     oauth_state_store.set_state(state, {
#         **state_data,
#         "status": "processing",
#         "authorization_code": code  # Track the code to prevent reuse
#     })
    
#     # Exchange code for token
#     token_data = await exchange_code_for_token(code)
#     if not token_data:
#         # Clean up state on failure
#         oauth_state_store.delete_state(state)
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Failed to exchange code for token. The authorization code may have expired or been used already. Please try logging in again."
#         )
    
#     # Verify id_token for secure user authentication
#     if not token_data.get("id_token"):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Missing ID token in OAuth response"
#         )
    
#     try:
#         # Verify the ID token and get validated claims
#         user_info = verify_google_id_token(token_data["id_token"])
#     except HTTPException:
#         # Re-raise HTTP exceptions from verification
#         raise
#     except Exception as e:
#         logger.error(f"ID token verification failed: {e}")
#         # Fallback to userinfo endpoint if id_token verification fails
#         logger.warning("Falling back to userinfo endpoint")
#         user_info = await get_google_user_info(token_data["access_token"])
#         if not user_info:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Failed to get user information from Google"
#             )
    
#     # Extract Google ID using OIDC 'sub' claim with 'id' fallback
#     google_id = user_info.get("sub") or user_info.get("id")
#     if not google_id:
#         raise HTTPException(status_code=400, detail="Invalid Google user info (missing subject)")
    
#     # Check if user already exists with this Google ID
#     existing_google_user = find_existing_user_by_google_id(db, google_id)
#     if existing_google_user:
#         logger.info(f"Found existing user by Google ID: {existing_google_user.email} (ID: {existing_google_user.id})")
#         # User already linked, set HttpOnly cookie and redirect to frontend
#         access_token = create_access_token(data={"sub": str(existing_google_user.id)})
#         logger.info(f"Created access token for user {existing_google_user.id}")
#         response.set_cookie(
#             key="access_token",
#             value=access_token,
#             httponly=True,  # HttpOnly cookie - not accessible via JavaScript
#             secure=False,    # Set to False for development (HTTP), True for production (HTTPS)
#             samesite="lax", # CSRF protection
#             domain="localhost",  # Explicitly set domain for localhost
#             path="/",           # Set path to root
#             max_age=30 * 60  # 30 minutes (same as token expiry)
#         )
#         logger.info("Set HttpOnly cookie with access token")
#         oauth_state_store.delete_state(state)  # Clean up state
        
#         # Add CORS headers for cookie support
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        
#         # Return HTML page that processes the response and sends to parent window
#         user_login_response = create_user_login_response(existing_google_user)
#         logger.info(f"Sending OAuth success response: {user_login_response}")
#         return HTMLResponse(f"""
#         <!DOCTYPE html>
#         <html>
#         <head><title>Google OAuth Success</title></head>
#         <body>
#             <script>
#                 console.log('OAuth popup: Sending success message to parent window');
#                 console.log('OAuth popup: Data being sent:', {json.dumps(user_login_response)});
                
#                 // Always redirect to the callback page
#                 const redirectUrl = `http://localhost:3000/auth/google/callback?token=${{encodeURIComponent('{access_token}')}}&user=${{encodeURIComponent(JSON.stringify({json.dumps(user_login_response)}))}}`;
#                 console.log('OAuth popup: Redirecting to:', redirectUrl);
                
#                 // Try to redirect the main window
#                 try {{
#                     window.opener.location.href = redirectUrl;
#                 }} catch (e) {{
#                     console.log('OAuth popup: Redirect failed, trying direct navigation');
#                     // If redirect fails, navigate directly
#                     window.location.href = redirectUrl;
#                 }}
#                 // Close the popup after a short delay
#                 setTimeout(() => {{
#                     window.close();
#                 }}, 1000);
#             </script>
#             <p>Authentication successful! This window will close automatically.</p>
#         </body>
#         </html>
#         """)
    
#     # Check if user exists with this email (including OAuth users with modified emails)
#     existing_email_user = find_oauth_user_by_original_email(db, user_info.get("email", ""))
#     logger.info(f"Email lookup for {user_info.get('email', '')} found: {existing_email_user.email if existing_email_user else 'None'}")
    
#     if existing_email_user:
#         # Check if the existing user is already an OAuth user
#         if existing_email_user.provider == "google":
#             logger.info(f"Found existing Google user by email: {existing_email_user.email} (ID: {existing_email_user.id})")
#             # Update Google ID if it's missing (fix for existing users)
#             if not existing_email_user.google_id:
#                 logger.info(f"Updating missing Google ID for user {existing_email_user.email}")
#                 existing_email_user.google_id = google_id
#                 db.commit()
#                 db.refresh(existing_email_user)
            
#             # User already has a Google account, set HttpOnly cookie and redirect to frontend
#             access_token = create_access_token(data={"sub": str(existing_email_user.id)})
#             logger.info(f"Created access token for user {existing_email_user.id}")
#             response.set_cookie(
#                 key="access_token",
#                 value=access_token,
#                 httponly=True,  # HttpOnly cookie - not accessible via JavaScript
#                 secure=False,    # Set to False for development (HTTP), True for production (HTTPS)
#                 samesite="lax", # CSRF protection
#                 max_age=30 * 60  # 30 minutes (same as token expiry)
#             )
#             logger.info("Set HttpOnly cookie with access token")
#             oauth_state_store.delete_state(state)  # Clean up state
            
#             # Add CORS headers for cookie support
#             response.headers["Access-Control-Allow-Credentials"] = "true"
#             response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            
#             # Return HTML page that processes the response and sends to parent window
#             user_login_response = create_user_login_response(existing_email_user)
#             return HTMLResponse(f"""
#             <!DOCTYPE html>
#             <html>
#             <head><title>Google OAuth Success</title></head>
#             <body>
#                 <script>
#                     // Send success data to parent window
#                     if (window.opener) {{
#                         window.opener.postMessage({{
#                             type: 'GOOGLE_OAUTH_SUCCESS',
#                             data: {json.dumps(user_login_response)}
#                         }}, window.location.origin);
#                     }}
#                     // Don't close immediately - let parent window handle it
#                 </script>
#                 <p>Authentication successful! This window will close automatically.</p>
#             </body>
#             </html>
#             """)
#         else:
#             # Account linking scenario for non-OAuth users
#             existing_state = oauth_state_store.get_state(state) or {}
#             oauth_state_store.set_state(state, {
#                 "status": "link_required",
#                 "created_at": existing_state.get("created_at") if isinstance(existing_state, dict) else None,
#                 "payload": {
#                     "google_data": {
#                         "id": google_id,
#                         "email": user_info.get("email", ""),
#                         "name": user_info.get("name", ""),
#                         "picture": user_info.get("picture")
#                     },
#                     "existing_user_id": existing_email_user.id
#                 }
#             })
            
#             # Return HTML page for account linking
#             account_linking_data = {
#                 "link_required": True,
#                 "message": "An account with this email already exists. Would you like to link your Google account?",
#                 "existing_user": {
#                     "id": existing_email_user.id,
#                     "email": existing_email_user.email,
#                     "full_name": existing_email_user.full_name,
#                     "provider": existing_email_user.provider
#                 },
#                 "google_data": {
#                     "email": user_info.get("email", ""),
#                     "full_name": user_info.get("name", ""),
#                     "avatar_url": user_info.get("picture"),
#                     "google_id": google_id
#                 },
#                 "state": state
#             }
            
#             return HTMLResponse(f"""
#             <!DOCTYPE html>
#             <html>
#             <head><title>Account Linking Required</title></head>
#             <body>
#                 <script>
#                     // Always redirect to account linking page
#                     const redirectUrl = `http://localhost:3000/auth/google/account-linking?data=${{encodeURIComponent(JSON.stringify({json.dumps(account_linking_data)}))}}`;
#                     console.log('OAuth popup: Redirecting to account linking:', redirectUrl);
                    
#                     // Try to redirect the main window
#                     try {{
#                         window.opener.location.href = redirectUrl;
#                     }} catch (e) {{
#                         console.log('OAuth popup: Redirect failed, trying direct navigation');
#                         // If redirect fails, navigate directly
#                         window.location.href = redirectUrl;
#                     }}
#                     // Close the popup after a short delay
#                     setTimeout(() => {{
#                         window.close();
#                     }}, 1000);
#                 </script>
#                 <p>Account linking required! This window will close automatically.</p>
#             </body>
#             </html>
#             """)
    
#     # Check if role is selected in state
#     selected_role = state_data.get("role")
    
#     # If no role is selected, require role selection
#     if not selected_role:
#         # Store OAuth data in state for role selection
#         existing_state = oauth_state_store.get_state(state) or {}
#         oauth_state_store.set_state(state, {
#             "status": "role_selection_required",
#             "created_at": existing_state.get("created_at") if isinstance(existing_state, dict) else None,
#             "user_info": {
#                 "google_id": google_id,
#                 "email": user_info.get("email", ""),
#                 "name": user_info.get("name", ""),
#                 "picture": user_info.get("picture")
#             }
#         })
        
#         # Return HTML page for role selection
#         role_selection_data = {
#             "requires_role_selection": True,
#             "state": state,
#             "user_info": {
#                 "google_id": google_id,
#                 "email": user_info.get("email", ""),
#                 "name": user_info.get("name", ""),
#                 "picture": user_info.get("picture")
#             }
#         }
        
#         return HTMLResponse(f"""
#         <!DOCTYPE html>
#         <html>
#         <head><title>Role Selection Required</title></head>
#         <body>
#             <script>
#                 console.log('OAuth popup: Role selection required');
#                 console.log('OAuth popup: Role selection data:', {json.dumps(role_selection_data)});
                
#                 // Always redirect to role selection page
#                 const redirectUrl = `http://localhost:3000/auth/google/role-selection?data=${{encodeURIComponent(JSON.stringify({json.dumps(role_selection_data)}))}}`;
#                 console.log('OAuth popup: Redirecting to role selection:', redirectUrl);
                
#                 // Try to redirect the main window
#                 try {{
#                     window.opener.location.href = redirectUrl;
#                 }} catch (e) {{
#                     console.log('OAuth popup: Redirect failed, trying direct navigation');
#                     // If redirect fails, navigate directly
#                     window.location.href = redirectUrl;
#                 }}
#                 // Close the popup after a short delay
#                 setTimeout(() => {{
#                     window.close();
#                 }}, 1000);
#             </script>
#             <p>Role selection required! This window will close automatically.</p>
#         </body>
#         </html>
#         """)
    
#     # Create new user with selected role
#     new_user = create_oauth_user(db, {**user_info, "id": google_id}, role=selected_role)
    
#     # Set HttpOnly cookie for new user
#     access_token = create_access_token(data={"sub": str(new_user.id)})
#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#         httponly=True,  # HttpOnly cookie - not accessible via JavaScript
#         secure=False,    # Set to False for development (HTTP), True for production (HTTPS)
#         samesite="lax", # CSRF protection
#         max_age=30 * 60  # 30 minutes (same as token expiry)
#     )
    
#     oauth_state_store.delete_state(state)  # Clean up state
    
#     # Add CORS headers for cookie support
#     response.headers["Access-Control-Allow-Credentials"] = "true"
#     response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    
#     # Return HTML page that processes the response and sends to parent window
#     user_login_response = create_user_login_response(new_user)
#     return HTMLResponse(f"""
#     <!DOCTYPE html>
#     <html>
#     <head><title>Google OAuth Success</title></head>
#     <body>
#         <script>
#             // Send success data to parent window
#             if (window.opener) {{
#                 window.opener.postMessage({{
#                     type: 'GOOGLE_OAUTH_SUCCESS',
#                     data: {json.dumps(user_login_response)}
#                 }}, window.location.origin);
#             }}
#             // Don't close immediately - let parent window handle it
#         </script>
#         <p>Authentication successful! This window will close automatically.</p>
#     </body>
#     </html>
#     """)

# @router.post("/google/select-role")
# async def select_role_for_oauth(
#     request: dict,
#     response: Response,
#     db: Session = Depends(get_db)
# ):
#     """Handle role selection for new OAuth users"""
#     try:
#         role = request.get("role")
#         state = request.get("state")
#         user_info = request.get("user_info", {})
        
#         if not role or not state or not user_info:
#             raise HTTPException(status_code=400, detail="Missing required fields")
        
#         if role not in ["student", "professor"]:
#             raise HTTPException(status_code=400, detail="Invalid role")
        
#         # Create new user with selected role
#         new_user = create_oauth_user(db, {**user_info, "id": user_info.get("google_id")}, role=role)
        
#         # Set HttpOnly cookie for new user
#         access_token = create_access_token(data={"sub": str(new_user.id)})
#         response.set_cookie(
#             key="access_token",
#             value=access_token,
#             httponly=True,  # HttpOnly cookie - not accessible via JavaScript
#             secure=False,    # Set to False for development (HTTP), True for production (HTTPS)
#             samesite="lax", # CSRF protection
#             domain="localhost",  # Explicitly set domain for localhost
#             path="/",           # Set path to root
#             max_age=30 * 60  # 30 minutes (same as token expiry)
#         )
        
#         # Add CORS headers for cookie support
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        
#         # Clean up state
#         oauth_state_store.delete_state(state)
        
#         # Return user data
#         user_response = create_user_login_response(new_user)
#         return user_response
        
#     except Exception as e:
#         logger.error(f"Role selection error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to select role")

# @router.post("/google/link")
# async def link_google_account(
#     request: AccountLinkingRequest,
#     response: Response,
#     db: Session = Depends(get_db)
# ):
#     """Link Google account to existing user or create separate account"""
    
#     # Validate OAuth state and get server-stored google_data
#     state_data = validate_oauth_state(request.state)
    
#     # Extract google_data from server-stored state (not client-supplied)
#     if not isinstance(state_data, dict) or "payload" not in state_data:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid OAuth state - missing payload data"
#         )
    
#     payload = state_data["payload"]
#     if "google_data" not in payload:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid OAuth state - missing Google user data"
#         )
    
#     # Use server-stored google_data (prevents account takeover)
#     server_google_data = payload["google_data"]
    
#     # Get existing user
#     existing_user = db.query(User).filter(User.id == request.existing_user_id).first()
#     if not existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     if request.action == "link":
#         # Convert server-stored google_data to format expected by utility functions
#         google_user_data = {
#             "email": server_google_data["email"],
#             "name": server_google_data["name"],
#             "picture": server_google_data["picture"],
#             "sub": server_google_data["id"],
#             "id": server_google_data["id"]
#         }
#         # Link Google account to existing user
#         linked_user = link_google_to_existing_user(db, existing_user, google_user_data)
        
#         # Set HttpOnly cookie for linked user
#         access_token = create_access_token(data={"sub": str(linked_user.id)})
#         response.set_cookie(
#             key="access_token",
#             value=access_token,
#             httponly=True,  # HttpOnly cookie - not accessible via JavaScript
#             secure=False,    # Set to False for development (HTTP), True for production (HTTPS)
#             samesite="lax", # CSRF protection
#             domain="localhost",  # Explicitly set domain for localhost
#             path="/",           # Set path to root
#             max_age=30 * 60  # 30 minutes (same as token expiry)
#         )
        
#         oauth_state_store.delete_state(request.state)  # Clean up state
#         return create_user_login_response(linked_user)
    
#     elif request.action == "create_separate":
#         # Convert server-stored google_data to format expected by utility functions
#         google_user_data = {
#             "email": server_google_data["email"],
#             "name": server_google_data["name"],
#             "picture": server_google_data["picture"],
#             "sub": server_google_data["id"],
#             "id": server_google_data["id"]
#         }
#         # Create separate account with Google OAuth (default to student role for separate accounts)
#         new_user = create_oauth_user(db, google_user_data, force_create=True, role="student")
        
#         # Set HttpOnly cookie for new separate user
#         access_token = create_access_token(data={"sub": str(new_user.id)})
#         response.set_cookie(
#             key="access_token",
#             value=access_token,
#             httponly=True,  # HttpOnly cookie - not accessible via JavaScript
#             secure=False,    # Set to False for development (HTTP), True for production (HTTPS)
#             samesite="lax", # CSRF protection
#             domain="localhost",  # Explicitly set domain for localhost
#             path="/",           # Set path to root
#             max_age=30 * 60  # 30 minutes (same as token expiry)
#         )
        
#         oauth_state_store.delete_state(request.state)  # Clean up state
#         return create_user_login_response(new_user)
    
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid action. Must be 'link' or 'create_separate'"
#         )

# @router.get("/google/status/{state}")
# async def get_oauth_status(state: str):
#     """Get OAuth status for a given state"""
#     state_data = oauth_state_store.get_state(state)
#     if not state_data:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="OAuth state not found or expired"
#         )
    
#     if isinstance(state_data, dict):
#         link_required = state_data.get("link_required", False)
#         if state_data.get("status") == "pending":
#             return {"status": "pending", "link_required": link_required}
#         else:
#             return {"status": "completed", "data": state_data, "link_required": link_required}
#     else:
#         # Handle legacy string format
#         if state_data == "pending":
#             return {"status": "pending", "link_required": False}
        
#         try:
#             parsed = json.loads(state_data)
#             link_required = parsed.get("link_required", False)
#             return {"status": "completed", "data": parsed, "link_required": link_required}
#         except json.JSONDecodeError:
#             return {"status": "completed", "data": state_data, "link_required": False}

# @router.get("/auth/status")
# async def get_auth_status(
#     request: Request,
#     db: Session = Depends(get_db)
# ):
#     """Check current authentication status"""
#     try:
#         from utilities.auth import get_current_user
#         user = await get_current_user(request, db)
#         return {
#             "authenticated": True,
#             "user": {
#                 "id": user.id,
#                 "email": user.email,
#                 "full_name": user.full_name,
#                 "role": user.role,
#                 "provider": user.provider,
#                 "google_id": user.google_id,
#                 "is_active": user.is_active,
#                 "is_verified": user.is_verified
#             }
#         }
#     except HTTPException as e:
#         return {
#             "authenticated": False,
#             "error": e.detail,
#             "status_code": e.status_code
#         }
#     except Exception as e:
#         return {
#             "authenticated": False,
#             "error": str(e),
#             "status_code": 500
#         }

"""
Google OAuth API endpoints - Cleaned Version
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import time
import asyncio
import logging
import os
import base64
from contextlib import asynccontextmanager
from cryptography.fernet import Fernet

from database.connection import get_db
from database.models import User
from database.schemas import (
    GoogleOAuthRequest, 
    AccountLinkingRequest, 
    OAuthUserData,
    UserLoginResponse,
    RoleSelectionRequest
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
from utilities.auth import create_access_token

# Logger for OAuth operations
logger = logging.getLogger(__name__)

# Configuration from environment variables
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
COOKIE_DOMAIN = os.getenv('COOKIE_DOMAIN', 'localhost')
IS_PRODUCTION = os.getenv('ENVIRONMENT', '').lower() in ['production', 'prod']

class OAuthStateStore:
    """Persistent OAuth state storage using Redis"""
    
    def __init__(self):
        from utilities.redis_manager import redis_manager
        self.redis = redis_manager
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption cipher for state payloads"""
        encryption_key = os.getenv('OAUTH_ENCRYPTION_KEY')
        if not encryption_key:
            if IS_PRODUCTION:
                raise ValueError("OAUTH_ENCRYPTION_KEY is required in production environment")
            else:
                # Development mode: use or generate persistent key
                try:
                    dev_key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.oauth_encryption_key')
                    key = self._get_or_create_dev_key(dev_key_file)
                    logger.warning("No OAUTH_ENCRYPTION_KEY found, using development key from file. Set OAUTH_ENCRYPTION_KEY in production!")
                    self.cipher = Fernet(key)
                except Exception as e:
                    logger.error(f"Failed to initialize development encryption: {e}")
                    # Fallback to no encryption for development
                    self.cipher = None
        else:
            # Validate and use provided key - Fernet keys should be base64-encoded
            try:
                # First try to use the key as-is (assuming it's already base64-encoded)
                self.cipher = Fernet(encryption_key.encode('utf-8'))
            except Exception as e:
                raise ValueError(f"Invalid OAUTH_ENCRYPTION_KEY: {e}. Key must be a valid base64-encoded Fernet key. Generate one with: Fernet.generate_key().decode()")
    
    def _get_or_create_dev_key(self, key_file_path: str) -> bytes:
        """Get existing dev key or create and persist a new one"""
        try:
            # Try to read existing key
            if os.path.exists(key_file_path):
                with open(key_file_path, 'rb') as f:
                    key = f.read()
                # Validate the key by trying to create a Fernet instance
                Fernet(key)  # This will raise an exception if invalid
                return key
        except Exception as e:
            logger.warning(f"Invalid or corrupted dev key file, generating new one: {e}")
        
        # Generate new key and persist it
        key = Fernet.generate_key()
        try:
            with open(key_file_path, 'wb') as f:
                f.write(key)
            # Set restrictive permissions (owner read/write only)
            os.chmod(key_file_path, 0o600)
        except Exception as e:
            logger.error(f"Failed to persist dev encryption key: {e}")
            # Continue with the generated key even if we can't persist it
        
        return key
    
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
            
            # Use Redis manager to store the state
            return self.redis.set(state, encrypted_data, ttl)
        except Exception as e:
            logger.error(f"Failed to store OAuth state: {e}")
            return False
    
    def get_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Retrieve OAuth state data"""
        try:
            encrypted_data = self.redis.get(state)
            if not encrypted_data:
                return None
            
            # Decrypt the payload if cipher is available
            if self.cipher:
                try:
                    # Redis returns strings with decode_responses=True, so use directly
                    encrypted_payload = base64.b64decode(encrypted_data)
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
            return self.redis.delete(state)
        except Exception as e:
            logger.error(f"Failed to delete OAuth state: {e}")
            return False

# Create the OAuth router
router = APIRouter(prefix="/auth", tags=["oauth"])

# Initialize OAuth state store
oauth_state_store = OAuthStateStore()

# Global cache to track used authorization codes (in-memory, will reset on restart)
used_authorization_codes = set()

# Global cleanup task reference
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
            detail="Invalid or expired OAuth state"
        )
    
    return state_data

def add_cors_headers(response: Response):
    """Add CORS headers for cookie support"""
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL

def create_oauth_success_html(user_login_response: dict, access_token: str) -> str:
    """Create HTML response for successful OAuth"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Google OAuth Success</title></head>
    <body>
        <script>
            console.log('OAuth popup: Sending success message to parent window');
            console.log('OAuth popup: Data being sent:', {json.dumps(user_login_response)});
            
            // Always redirect to the callback page
            const redirectUrl = `{FRONTEND_URL}/auth/google/callback?token=${{encodeURIComponent('{access_token}')}}&user=${{encodeURIComponent(JSON.stringify({json.dumps(user_login_response)}))}}`;
            console.log('OAuth popup: Redirecting to:', redirectUrl);
            
            // Try to redirect the main window
            try {{
                window.opener.location.href = redirectUrl;
            }} catch (e) {{
                console.log('OAuth popup: Redirect failed, trying direct navigation');
                // If redirect fails, navigate directly
                window.location.href = redirectUrl;
            }}
            // Close the popup after a short delay
            setTimeout(() => {{
                window.close();
            }}, 1000);
        </script>
        <p>Authentication successful! This window will close automatically.</p>
    </body>
    </html>
    """

def create_account_linking_html(account_linking_data: dict) -> str:
    """Create HTML response for account linking"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Account Linking Required</title></head>
    <body>
        <script>
            // Always redirect to account linking page
            const redirectUrl = `{FRONTEND_URL}/auth/google/account-linking?data=${{encodeURIComponent(JSON.stringify({json.dumps(account_linking_data)}))}}`;
            console.log('OAuth popup: Redirecting to account linking:', redirectUrl);
            
            // Try to redirect the main window
            try {{
                window.opener.location.href = redirectUrl;
            }} catch (e) {{
                console.log('OAuth popup: Redirect failed, trying direct navigation');
                // If redirect fails, navigate directly
                window.location.href = redirectUrl;
            }}
            // Close the popup after a short delay
            setTimeout(() => {{
                window.close();
            }}, 1000);
        </script>
        <p>Account linking required! This window will close automatically.</p>
    </body>
    </html>
    """

def create_role_selection_html(role_selection_data: dict) -> str:
    """Create HTML response for role selection"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Role Selection Required</title></head>
    <body>
        <script>
            console.log('OAuth popup: Role selection required');
            console.log('OAuth popup: Role selection data:', {json.dumps(role_selection_data)});
            
            // Always redirect to role selection page
            const redirectUrl = `{FRONTEND_URL}/auth/google/role-selection?data=${{encodeURIComponent(JSON.stringify({json.dumps(role_selection_data)}))}}`;
            console.log('OAuth popup: Redirecting to role selection:', redirectUrl);
            
            // Try to redirect the main window
            try {{
                window.opener.location.href = redirectUrl;
            }} catch (e) {{
                console.log('OAuth popup: Redirect failed, trying direct navigation');
                // If redirect fails, navigate directly
                window.location.href = redirectUrl;
            }}
            // Close the popup after a short delay
            setTimeout(() => {{
                window.close();
            }}, 1000);
        </script>
        <p>Role selection required! This window will close automatically.</p>
    </body>
    </html>
    """

def set_auth_cookie(response: Response, access_token: str):
    """Set authentication cookie with proper security settings"""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # HttpOnly cookie - not accessible via JavaScript
        secure=IS_PRODUCTION,  # Secure flag for HTTPS in production
        samesite="lax",  # CSRF protection
        domain=COOKIE_DOMAIN,
        path="/",
        max_age=30 * 60  # 30 minutes (same as token expiry)
    )

async def periodic_cleanup():
    """Periodic cleanup task that runs every 5 minutes"""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            # Clear old authorization codes (keep only last 1000 to prevent memory bloat)
            global used_authorization_codes
            if len(used_authorization_codes) > 1000:
                # Keep only the most recent 500 codes
                used_authorization_codes = set(list(used_authorization_codes)[-500:])
                logger.info("Cleaned up old authorization codes")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Periodic cleanup failed: {e}")

@asynccontextmanager
async def lifespan(app):
    """FastAPI lifespan handler for startup and shutdown"""
    global cleanup_task
    # Startup
    cleanup_task = asyncio.create_task(periodic_cleanup())
    logger.info("Started OAuth state cleanup task")
    yield
    # Shutdown
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("Stopped OAuth state cleanup task")

# Route definitions (removing duplicates)

@router.post("/clear-cache")
async def clear_oauth_cache():
    """Clear the OAuth authorization code cache (for debugging)"""
    global used_authorization_codes
    cleared_count = len(used_authorization_codes)
    used_authorization_codes.clear()
    logger.info(f"Cleared {cleared_count} authorization codes from cache")
    return {"message": f"Cleared {cleared_count} authorization codes from cache"}

@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    try:
        state = generate_state()
        auth_url = get_google_auth_url(state)
        
        # Store initial state
        oauth_state_store.set_state(state, {"status": "pending", "created_at": time.time()})
        
        return {"auth_url": auth_url, "state": state}
    except Exception as e:
        logger.error(f"Google login initiation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login"
        )

@router.get("/google/callback")
async def google_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    response: Response = None,
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
    
    # Validate OAuth state
    state_data = validate_oauth_state(state)
    
    # Check if this callback has already been processed
    if state_data.get("status") == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth callback has already been processed. Please try logging in again."
        )
    
    # Check if this authorization code has already been used globally
    if code in used_authorization_codes:
        logger.warning(f"Authorization code already used: {code[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code has already been used. Please try logging in again."
        )
    
    # Check if this authorization code is already being processed
    if state_data.get("status") == "processing":
        logger.warning(f"Authorization code already being processed for state: {state}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth callback is already being processed. Please wait."
        )
    
    # Mark state as being processed to prevent duplicate calls
    oauth_state_store.set_state(state, {
        **state_data,
        "status": "processing",
        "authorization_code": code
    })
    
    try:
        # Exchange code for token
        token_data = await exchange_code_for_token(code)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token. The authorization code may have expired or been used already. Please try logging in again."
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
        
        # Mark authorization code as used (only after successful token exchange)
        used_authorization_codes.add(code)
        
        # Check if user already exists with this Google ID
        existing_google_user = find_existing_user_by_google_id(db, google_id)
        if existing_google_user:
            logger.info(f"Found existing user by Google ID: {existing_google_user.email} (ID: {existing_google_user.id})")
            
            # Create access token and set cookie
            access_token = create_access_token(data={"sub": str(existing_google_user.id)})
            set_auth_cookie(response, access_token)
            add_cors_headers(response)
            
            # Clean up state
            oauth_state_store.delete_state(state)
            
            user_login_response = create_user_login_response(existing_google_user)
            return HTMLResponse(create_oauth_success_html(user_login_response, access_token))
        
        # Check if user exists with this email (including OAuth users with modified emails)
        existing_email_user = find_oauth_user_by_original_email(db, user_info.get("email", ""))
        logger.info(f"Email lookup for {user_info.get('email', '')} found: {existing_email_user.email if existing_email_user else 'None'}")
        
        if existing_email_user:
            # Check if the existing user is already an OAuth user
            if existing_email_user.provider == "google":
                logger.info(f"Found existing Google user by email: {existing_email_user.email} (ID: {existing_email_user.id})")
                
                # Update Google ID if it's missing (fix for existing users)
                if not existing_email_user.google_id:
                    logger.info(f"Updating missing Google ID for user {existing_email_user.email}")
                    existing_email_user.google_id = google_id
                    db.commit()
                    db.refresh(existing_email_user)
                
                # Create access token and set cookie
                access_token = create_access_token(data={"sub": str(existing_email_user.id)})
                set_auth_cookie(response, access_token)
                add_cors_headers(response)
                
                # Clean up state
                oauth_state_store.delete_state(state)
                
                user_login_response = create_user_login_response(existing_email_user)
                return HTMLResponse(create_oauth_success_html(user_login_response, access_token))
            else:
                # Account linking scenario for non-OAuth users
                oauth_state_store.set_state(state, {
                    "status": "link_required",
                    "created_at": state_data.get("created_at"),
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
                
                account_linking_data = {
                    "link_required": True,
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
            
                return HTMLResponse(create_account_linking_html(account_linking_data))
        
        # Check if role is selected in state
        selected_role = state_data.get("role")
        
        # If no role is selected, require role selection
        if not selected_role:
            # Store OAuth data in state for role selection
            oauth_state_store.set_state(state, {
                "status": "role_selection_required",
                "created_at": state_data.get("created_at"),
                "user_info": {
                    "google_id": google_id,
                    "email": user_info.get("email", ""),
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture")
                }
            })
            
            role_selection_data = {
                "requires_role_selection": True,
                "state": state,
                "user_info": {
                    "google_id": google_id,
                    "email": user_info.get("email", ""),
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture")
                }
            }
            
            return HTMLResponse(create_role_selection_html(role_selection_data))
        
        # Create new user with selected role
        new_user = create_oauth_user(db, {**user_info, "id": google_id}, role=selected_role)
        
        # Create access token and set cookie
        access_token = create_access_token(data={"sub": str(new_user.id)})
        set_auth_cookie(response, access_token)
        add_cors_headers(response)
        
        # Clean up state
        oauth_state_store.delete_state(state)
        
        user_login_response = create_user_login_response(new_user)
        return HTMLResponse(create_oauth_success_html(user_login_response, access_token))
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"OAuth callback processing failed: {e}")
        # Clean up state on failure
        oauth_state_store.delete_state(state)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process OAuth callback"
        )

@router.post("/google/select-role")
async def select_role_for_oauth(
    role_data: RoleSelectionRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Select role for OAuth user after Google authentication"""
    
    # Validate OAuth state
    state_data = validate_oauth_state(role_data.state)
    
    # Check if this is a role selection request
    if state_data.get("status") != "role_selection_required":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role selection not required for this OAuth flow"
        )
    
    # Get user info from state
    user_info = state_data.get("user_info")
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user information in OAuth state"
        )
    
    # Create new user with selected role
    new_user = create_oauth_user(db, user_info, role=role_data.role)
    
    # Create access token and set cookie
    access_token = create_access_token(data={"sub": str(new_user.id)})
    set_auth_cookie(response, access_token)
    add_cors_headers(response)
    
    # Clean up state
    oauth_state_store.delete_state(role_data.state)
    
    return create_user_login_response(new_user)

@router.post("/google/link")
async def link_google_account(
    request: AccountLinkingRequest,
    response: Response,
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
    
    # Convert server-stored google_data to format expected by utility functions
    google_user_data = {
        "email": server_google_data["email"],
        "name": server_google_data["name"],
        "picture": server_google_data["picture"],
        "sub": server_google_data["id"],
        "id": server_google_data["id"]
    }
    
    if request.action == "link":
        # Link Google account to existing user
        linked_user = link_google_to_existing_user(db, existing_user, google_user_data)
        
        # Create access token and set cookie
        access_token = create_access_token(data={"sub": str(linked_user.id)})
        set_auth_cookie(response, access_token)
        
        oauth_state_store.delete_state(request.state)  # Clean up state
        return create_user_login_response(linked_user)
    
    elif request.action == "create_separate":
        # Create separate account with Google OAuth (default to student role for separate accounts)
        new_user = create_oauth_user(db, google_user_data, force_create=True, role="student")
        
        # Create access token and set cookie
        access_token = create_access_token(data={"sub": str(new_user.id)})
        set_auth_cookie(response, access_token)
        
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
        link_required = state_data.get("status") == "link_required"
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
            link_required = parsed.get("status") == "link_required"
            return {"status": "completed", "data": parsed, "link_required": link_required}
        except json.JSONDecodeError:
            return {"status": "completed", "data": state_data, "link_required": False}

@router.get("/auth/status")
async def get_auth_status(
    request: Request,
    db: Session = Depends(get_db)
):
    """Check current authentication status"""
    try:
        from utilities.auth import get_current_user
        user = await get_current_user(request, db)
        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "provider": user.provider,
                "google_id": user.google_id,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        }
    except HTTPException as e:
        return {
            "authenticated": False,
            "error": e.detail,
            "status_code": e.status_code
        }
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e),
            "status_code": 500
        }