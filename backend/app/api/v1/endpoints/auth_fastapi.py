from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi_users import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth

from app.core.auth import fastapi_users, current_active_user, auth_backend
from app.core.database import get_async_session
from app.core.oauth import oauth
from app.models.user import User, OAuthAccount
from app.schemas.user import User as UserSchema
from app.core.config import settings
from app.core.auth import get_jwt_strategy

router = APIRouter()

# Include FastAPI Users routes
router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/jwt", tags=["auth"])
router.include_router(fastapi_users.get_register_router(schemas.UC, schemas.U), prefix="/register", tags=["auth"])
router.include_router(fastapi_users.get_reset_password_router(), prefix="/reset-password", tags=["auth"])
router.include_router(fastapi_users.get_verify_router(schemas.U), prefix="/verify", tags=["auth"])
router.include_router(fastapi_users.get_users_router(schemas.UC, schemas.U), prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    user: User = Depends(current_active_user),
) -> Any:
    """Get current user information"""
    return user


# OAuth routes
@router.get("/oauth/{provider}/login")
async def oauth_login(request: Request, provider: str):
    """Initiate OAuth login"""
    if provider not in ['google', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    try:
        # Generate the callback URL manually since url_for doesn't work with dynamic route names
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/api/v1/auth/oauth/{provider}/callback"
        
        # Check if OAuth client is properly configured
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(
                status_code=500, 
                detail=f"{provider.capitalize()} OAuth is not properly configured. Please check your environment variables."
            )
        
        # Ensure session is initialized
        if 'oauth_state' not in request.session:
            request.session['oauth_state'] = {}
        
        # Generate authorization URL manually
        auth_data = await client.create_authorization_url(redirect_uri)
        auth_url = auth_data['url']
        
        # Store state in session for verification
        state = auth_data.get('state')
        if state:
            request.session['oauth_state'][provider] = state
        
        # Redirect to the authorization URL
        return RedirectResponse(url=auth_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth configuration error: {str(e)}"
        )


@router.get("/oauth/test")
async def oauth_test():
    """Test endpoint to check OAuth configuration"""
    try:
        github_client = oauth.create_client('github')
        google_client = oauth.create_client('google')
        
        return {
            "github_configured": github_client is not None,
            "google_configured": google_client is not None,
            "github_client_id": getattr(github_client, 'client_id', None) if github_client else None,
            "google_client_id": getattr(google_client, 'client_id', None) if google_client else None,
        }
    except Exception as e:
        return {
            "error": str(e),
            "github_configured": False,
            "google_configured": False,
        }


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    request: Request, 
    provider: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Handle OAuth callback and redirect to frontend with token"""
    
    if provider not in ['google', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    try:
        client = oauth.create_client(provider)
        
        # Use the standard authlib method but handle state verification manually
        try:
            token = await client.authorize_access_token(request)
        except Exception as e:
            # If state verification fails, try without state verification for development
            if "state" in str(e).lower() and settings.ENVIRONMENT == "development":
                # Manually extract code and exchange for token
                code = request.query_params.get('code')
                if not code:
                    raise HTTPException(status_code=400, detail="No authorization code received")
                
                # Use the client's internal method to exchange code for token
                base_url = str(request.base_url).rstrip('/')
                redirect_uri = f"{base_url}/api/v1/auth/oauth/{provider}/callback"
                
                # Manual HTTP request to exchange code for token
                import httpx
                
                if provider == 'google':
                    token_url = "https://oauth2.googleapis.com/token"
                    token_data = {
                        "client_id": client.client_id,
                        "client_secret": client.client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri
                    }
                else:  # GitHub
                    token_url = "https://github.com/login/oauth/access_token"
                    token_data = {
                        "client_id": client.client_id,
                        "client_secret": client.client_secret,
                        "code": code,
                        "redirect_uri": redirect_uri
                    }
                
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.post(
                        token_url,
                        data=token_data,
                        headers={"Accept": "application/json"}
                    )
                    token_response = response.json()
                    
                    if "error" in token_response:
                        raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_response['error']}")
                    
                    token = token_response
            else:
                raise e
        
        # Get user info based on provider
        if provider == 'google':
            # For Google, get user info directly from the userinfo endpoint
            # This avoids the nonce requirement for ID token parsing
            resp = await client.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
            user_info = resp.json()
        else:  # GitHub
            resp = await client.get('user', token=token)
            user_info = resp.json()
        
        # Find or create user
        user = await get_or_create_oauth_user(session, provider, user_info, token)
        
        if user is None:
            raise HTTPException(status_code=500, detail="Failed to create or retrieve user")
        
        # Create JWT token using FastAPI Users strategy
        try:
            strategy = get_jwt_strategy()
            jwt_token = await strategy.write_token(user)
        except Exception as jwt_error:
            raise HTTPException(status_code=500, detail=f"JWT token creation failed: {str(jwt_error)}")
        
        # Redirect to frontend with token
        frontend_url = settings.FRONTEND_URL or "http://localhost:3000"
        redirect_url = f"{frontend_url}/auth/callback?token={jwt_token}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        frontend_url = settings.FRONTEND_URL or "http://localhost:3000"
        error_url = f"{frontend_url}/auth/callback?error=auth_failed&error_description={str(e)}"
        return RedirectResponse(url=error_url)


async def get_or_create_oauth_user(
    session: AsyncSession, 
    provider: str, 
    user_info: dict, 
    token: dict
) -> User:
    from sqlalchemy import select
    
    # Extract user info based on provider
    if provider == 'google':
        # Google userinfo endpoint returns: sub, email, name, picture, given_name, family_name
        account_id = user_info.get('sub')  # Google uses 'sub' for user ID
        email = user_info.get('email')
        username = user_info.get('email', '').split('@')[0] if email else None
        full_name = user_info.get('name')
        avatar_url = user_info.get('picture')
        
        # If sub is not available, use email as account_id (fallback)
        if not account_id and email:
            account_id = email
    else:  # GitHub
        account_id = str(user_info.get('id'))
        email = user_info.get('email')
        username = user_info.get('login') or (email.split('@')[0] if email else None)
        full_name = user_info.get('name')
        avatar_url = user_info.get('avatar_url')
    
    # Ensure we have a valid account_id
    if not account_id:
        raise HTTPException(
            status_code=400, 
            detail=f"Could not extract account ID from {provider} OAuth response"
        )
    
    # Convert expires_at to proper datetime if it's a timestamp
    expires_at = None
    if token.get('expires_at'):
        if isinstance(token['expires_at'], int):
            # Convert Unix timestamp to datetime
            expires_at = datetime.fromtimestamp(token['expires_at'])
        else:
            expires_at = token['expires_at']
    
    # Check if OAuth account exists
    stmt = select(OAuthAccount).where(
        OAuthAccount.oauth_name == provider,
        OAuthAccount.account_id == account_id
    )
    result = await session.execute(stmt)
    oauth_account = result.scalar_one_or_none()
    
    if oauth_account:
        # Update existing OAuth account
        oauth_account.access_token = token['access_token']
        oauth_account.expires_at = expires_at
        oauth_account.refresh_token = token.get('refresh_token')
        await session.commit()
        
        # Explicitly load the user object to avoid lazy loading issues
        stmt = select(User).where(User.id == oauth_account.user_id)
        result = await session.execute(stmt)
        user = result.scalar_one()
        
        return user
    
    # Check if user exists with same email
    if email:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # Link existing user to OAuth
            oauth_account = OAuthAccount(
                oauth_name=provider,
                access_token=token['access_token'],
                expires_at=expires_at,
                refresh_token=token.get('refresh_token'),
                account_id=account_id,
                account_email=email,
                user_id=user.id
            )
            session.add(oauth_account)
            await session.commit()
            return user
    
    # Create new user
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        avatar_url=avatar_url,
        is_verified=True  # OAuth users are verified
    )
    session.add(user)
    await session.flush()  # Get the user ID
    
    # Create OAuth account
    oauth_account = OAuthAccount(
        oauth_name=provider,
        access_token=token['access_token'],
        expires_at=expires_at,
        refresh_token=token.get('refresh_token'),
        account_id=account_id,
        account_email=email,
        user_id=user.id
    )
    session.add(oauth_account)
    await session.commit()
    
    return user 


 