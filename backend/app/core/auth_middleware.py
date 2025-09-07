"""
Authentication middleware for automatic protection of all routes
"""

from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.models.user import User


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically protect all routes except public ones"""

    def __init__(self, app: ASGIApp, public_paths: list[str] = None):
        super().__init__(app)
        self.public_paths = public_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/oauth/user",
            "/api/v1/auth/exchange-token",
            "/api/v1/auth/refresh",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        # Skip authentication for OPTIONS requests (CORS)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token
        token = auth_header.split(" ")[1]

        # Validate token and get user
        try:
            from sqlalchemy import select

            from app.core.database import get_async_session

            # Get database session
            async with get_async_session() as session:
                # Validate JWT token
                import jwt
                from jwt.exceptions import InvalidTokenError

                from app.core.config import settings

                try:
                    payload = jwt.decode(
                        token,
                        settings.SECRET_KEY,
                        algorithms=[settings.ALGORITHM],
                    )
                    user_id: str = payload.get("sub")
                    token_type: str = payload.get("type")

                    if user_id is None or token_type != "access":
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token",
                        )

                except InvalidTokenError:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid token"},
                    )

                # Get user from database
                result = await session.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()

                if user is None:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "User not found"},
                    )

                # Ensure user is active
                if not user.is_active:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "User account is inactive"},
                    )

                # Add user to request state for use in endpoints
                request.state.current_user = user

        except Exception:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication failed"},
            )

        # Continue to the actual endpoint
        return await call_next(request)
