from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import current_active_user
from app.core.database import get_async_session
from app.models.project import ProjectMember
from app.models.task import Tag
from app.models.user import User
from app.schemas.tag import Tag as TagSchema
from app.schemas.tag import TagCreate, TagUpdate

router = APIRouter()


@router.get("/project/{project_id}", response_model=list[TagSchema])
async def get_tags_by_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get all tags for a specific project"""
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
            status_code=403, detail="You must be a member of the project to view tags"
        )

    stmt = select(Tag).where(Tag.project_id == project_id)
    result = await session.execute(stmt)
    tags = result.scalars().all()
    return tags


@router.post("/", response_model=TagSchema)
async def create_tag(
    *,
    session: AsyncSession = Depends(get_async_session),
    tag_in: TagCreate,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Create new tag"""
    # Check if user is a member of the project
    stmt = select(ProjectMember).where(
        ProjectMember.project_id == tag_in.project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.is_active,
    )
    result = await session.execute(stmt)
    project_member = result.scalar_one_or_none()

    if not project_member:
        raise HTTPException(
            status_code=403, detail="You must be a member of the project to create tags"
        )

    tag = Tag(**tag_in.model_dump())
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


@router.put("/{tag_id}", response_model=TagSchema)
async def update_tag(
    *,
    session: AsyncSession = Depends(get_async_session),
    tag_id: int,
    tag_in: TagUpdate,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Update tag"""
    # Check if user is a member of the project
    stmt = (
        select(Tag)
        .join(ProjectMember)
        .where(
            Tag.id == tag_id,
            ProjectMember.user_id == current_user.id,
            ProjectMember.is_active,
        )
    )
    result = await session.execute(stmt)
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Update fields
    update_data = tag_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


@router.delete("/{tag_id}")
async def delete_tag(
    *,
    session: AsyncSession = Depends(get_async_session),
    tag_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Delete tag"""
    # Check if user is a member of the project
    stmt = (
        select(Tag)
        .join(ProjectMember)
        .where(
            Tag.id == tag_id,
            ProjectMember.user_id == current_user.id,
            ProjectMember.is_active,
        )
    )
    result = await session.execute(stmt)
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await session.delete(tag)
    await session.commit()
    return {"message": "Tag deleted successfully"}
