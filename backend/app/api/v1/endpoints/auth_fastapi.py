from typing import Any

from fastapi import APIRouter, Depends
from fastapi_users import schemas

from app.core.auth import (
    auth_backend,
    current_active_user,
    fastapi_users,
)
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

# Include FastAPI Users routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(schemas.UC, schemas.U),
    prefix="/register",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/reset-password", tags=["auth"]
)
router.include_router(
    fastapi_users.get_verify_router(schemas.U), prefix="/verify", tags=["auth"]
)
router.include_router(
    fastapi_users.get_users_router(schemas.UC, schemas.U),
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    user: User = Depends(current_active_user),
) -> Any:
    """Get current user information"""
    return user


# OAuth routes removed - now handled by frontend
