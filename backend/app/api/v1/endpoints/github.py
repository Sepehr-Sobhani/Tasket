import hashlib
import hmac
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session

router = APIRouter()

# GitHub integration endpoints will be implemented when needed
# Currently these are placeholder endpoints that are not used by the frontend
