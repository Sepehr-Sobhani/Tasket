from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import current_active_user
from app.core.database import get_async_session
from app.models.epic import Epic
from app.models.project import ProjectMember
from app.models.user import User
from app.schemas.epic import Epic as EpicSchema
from app.schemas.epic import EpicCreate

router = APIRouter()


@router.get("/", response_model=list[EpicSchema])
async def get_epics(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get all epics for projects the user is a member of"""
    # Get epics from projects where user is a member
    stmt = (
        select(Epic)
        .join(Epic.project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id, ProjectMember.is_active)
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(stmt)
    epics = result.scalars().all()
    return epics


@router.get("/project/{project_id}", response_model=list[EpicSchema])
async def get_epics_by_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get all epics for a specific project"""
    # Check if user is a member of the project
    stmt = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.is_active,
    )
    result = await session.execute(stmt)
    project_member = result.scalar_one_or_none()

    if not project_member:
        raise HTTPException(
            status_code=403, detail="You must be a member of the project to view epics"
        )

    stmt = select(Epic).where(Epic.project_id == project_id, Epic.is_active)
    result = await session.execute(stmt)
    epics = result.scalars().all()
    return epics


@router.post("/", response_model=EpicSchema)
async def create_epic(
    *,
    session: AsyncSession = Depends(get_async_session),
    epic_in: EpicCreate,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Create new epic"""
    # Check if user is a member of the project
    stmt = select(ProjectMember).where(
        ProjectMember.project_id == epic_in.project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.is_active,
    )
    result = await session.execute(stmt)
    project_member = result.scalar_one_or_none()

    if not project_member:
        raise HTTPException(
            status_code=403,
            detail="You must be a member of the project to create epics",
        )

    epic = Epic(**epic_in.model_dump())
    session.add(epic)
    await session.commit()
    await session.refresh(epic)
    return epic


@router.get("/{epic_id}", response_model=EpicSchema)
async def get_epic(
    *,
    session: AsyncSession = Depends(get_async_session),
    epic_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get epic by ID"""
    # Check if user is a member of the project
    stmt = (
        select(Epic)
        .join(Epic.project)
        .join(ProjectMember)
        .where(
            Epic.id == epic_id,
            ProjectMember.user_id == current_user.id,
            ProjectMember.is_active,
        )
    )
    result = await session.execute(stmt)
    epic = result.scalar_one_or_none()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    return epic
