from datetime import timedelta
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_helpers import get_current_user_from_request
from app.core.config import settings
from app.core.database import get_async_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.models.user import OAuthAccount, User
from app.schemas.auth import RefreshTokenRequest, Token
from app.schemas.user import User as UserSchema

router = APIRouter()


@router.post("/oauth/user", response_model=UserSchema)
async def create_or_get_oauth_user(
    oauth_data: dict, session: AsyncSession = Depends(get_async_session)
):
    """Create or get user from OAuth provider data"""
    provider = oauth_data.get("provider")
    provider_id = oauth_data.get("provider_id")
    email = oauth_data.get("email")
    name = oauth_data.get("name")
    avatar_url = oauth_data.get("avatar_url")

    if not all([provider, provider_id, email]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required OAuth data",
        )

    # Check if user exists with this email
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # Update user info if needed
        if name and not user.full_name:
            user.full_name = name
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        await session.commit()
        return user

    # Create new user
    username = email.split("@")[0] if email else f"{provider}_{provider_id}"

    # Ensure username is unique
    counter = 1
    original_username = username
    while True:
        result = await session.execute(select(User).where(User.username == username))
        if not result.scalar_one_or_none():
            break
        username = f"{original_username}_{counter}"
        counter += 1

    user = User(
        email=email,
        username=username,
        full_name=name,
        avatar_url=avatar_url,
        is_verified=True,  # OAuth users are verified
        is_active=True,
    )

    session.add(user)
    await session.flush()  # Get the user ID

    # Create OAuth account record
    oauth_account = OAuthAccount(
        oauth_name=provider,
        account_id=provider_id,
        account_email=email,
        user_id=user.id,
    )
    session.add(oauth_account)
    await session.commit()

    return user


@router.post("/exchange-token", response_model=Token)
async def exchange_oauth_token(
    user_data: dict, session: AsyncSession = Depends(get_async_session)
):
    """Exchange OAuth user data for JWT token"""
    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user_id in request",
        )

    # Verify user exists
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Create JWT tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        "user_id": user.id,
        "username": user.username,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Refresh access token using refresh token"""
    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from None

    # Verify user exists and is active
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user.id,
        "username": user.username,
    }


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    request: Request,
) -> Any:
    """Get current user information"""
    # Get current user from request state (automatically authenticated by middleware)
    current_user = get_current_user_from_request(request)
    return current_user
