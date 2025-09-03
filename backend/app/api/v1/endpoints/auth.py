from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)
from app.models.user import OAuthAccount, User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest, session: AsyncSession = Depends(get_async_session)
):
    """Login with email and password"""
    user = await authenticate_user(session, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


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


@router.post("/register", response_model=UserSchema)
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    """Register a new user"""
    # Check if user already exists
    result = await session.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Check if username already exists
    result = await session.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        avatar_url=user_data.avatar_url,
        bio=user_data.bio,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_verified=False,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user information"""
    return current_user
