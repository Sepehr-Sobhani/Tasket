from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from app.models.user import User
from app.schemas.auth import GitHubAuthRequest, GoogleAuthRequest, LoginRequest, Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate
from app.services.github import GitHubService
from app.services.google import GoogleService

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Login with username and password"""
    user = authenticate_user(db, username=login_data.username, password=login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user.id,
        "username": user.username,
    }


@router.post("/register", response_model=UserSchema)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user"""
    # Check if user already exists
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        avatar_url=user_in.avatar_url,
        bio=user_in.bio,
    )
    user.set_password(user_in.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/github", response_model=Token)
def github_auth(
    auth_data: GitHubAuthRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Authenticate with GitHub OAuth"""
    github_service = GitHubService()

    try:
        # Exchange code for access token
        access_token = github_service.exchange_code_for_token(auth_data.code)

        # Get user info from GitHub
        github_user = github_service.get_user_info(access_token)

        # Find or create user
        user = db.query(User).filter(User.github_id == github_user["id"]).first()

        if not user:
            # Check if user exists with same email
            user = db.query(User).filter(User.email == github_user["email"]).first()
            if user:
                # Link existing user to GitHub
                user.github_id = str(github_user["id"])
                user.github_username = github_user["login"]
                user.github_access_token = access_token
            else:
                # Create new user
                user = User(
                    username=github_user["login"],
                    email=github_user["email"],
                    full_name=github_user["name"],
                    avatar_url=github_user["avatar_url"],
                    github_id=str(github_user["id"]),
                    github_username=github_user["login"],
                    github_access_token=access_token,
                )
                db.add(user)
        else:
            # Update existing user's GitHub info
            user.github_access_token = access_token
            user.github_username = github_user["login"]

        db.commit()
        db.refresh(user)

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=user.username, expires_delta=access_token_expires
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": user.id,
            "username": user.username,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub authentication failed: {str(e)}",
        ) from e


@router.post("/google", response_model=Token)
def google_auth(
    auth_data: GoogleAuthRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Authenticate with Google OAuth"""
    google_service = GoogleService()

    try:
        # Exchange code for access token
        access_token = google_service.exchange_code_for_token(auth_data.code, auth_data.redirect_uri)

        # Get user info from Google
        google_user = google_service.get_user_info(access_token)

        # Find or create user
        user = db.query(User).filter(User.google_id == google_user["id"]).first()

        if not user:
            # Check if user exists with same email
            user = db.query(User).filter(User.email == google_user["email"]).first()
            if user:
                # Link existing user to Google
                user.google_id = google_user["id"]
                user.google_email = google_user["email"]
                user.google_access_token = access_token
            else:
                # Create new user
                user = User(
                    username=google_user["email"].split("@")[0],  # Use email prefix as username
                    email=google_user["email"],
                    full_name=google_user.get("name", ""),
                    avatar_url=google_user.get("picture", ""),
                    google_id=google_user["id"],
                    google_email=google_user["email"],
                    google_access_token=access_token,
                )
                db.add(user)
        else:
            # Update existing user's Google info
            user.google_access_token = access_token
            user.google_email = google_user["email"]

        db.commit()
        db.refresh(user)

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=user.username, expires_delta=access_token_expires
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": user.id,
            "username": user.username,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}",
        ) from e


@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user information"""
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.username, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": current_user.id,
        "username": current_user.username,
    }


@router.get("/google/url")
def get_google_oauth_url(
    redirect_uri: str,
    state: str | None = None,
) -> dict[str, str]:
    """Get Google OAuth URL."""
    google_service = GoogleService()
    oauth_url = google_service.get_oauth_url(redirect_uri, state)
    return {"url": oauth_url}
