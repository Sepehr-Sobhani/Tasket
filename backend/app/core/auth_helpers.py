"""
Authentication helper functions for automatic user access
"""

from fastapi import HTTPException, Request, status

from app.models.user import User


def get_current_user_from_request(request: Request) -> User:
    """
    Get the current authenticated user from request state.
    This works with the AuthMiddleware that automatically authenticates all requests.

    Usage in endpoints:
        @router.get("/some-endpoint")
        async def some_endpoint(request: Request):
            current_user = get_current_user_from_request(request)
            # Use current_user...
    """
    user = getattr(request.state, "current_user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
        )
    return user


def get_current_user_optional(request: Request) -> User | None:
    """
    Get the current authenticated user from request state, or None if not authenticated.
    Useful for endpoints that work for both authenticated and unauthenticated users.

    Usage in endpoints:
        @router.get("/some-endpoint")
        async def some_endpoint(request: Request):
            current_user = get_current_user_optional(request)
            if current_user:
                # User is authenticated
            else:
                # User is not authenticated
    """
    return getattr(request.state, "current_user", None)
