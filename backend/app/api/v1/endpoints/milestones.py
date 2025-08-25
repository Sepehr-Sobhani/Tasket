from typing import Any

from app.core.database import get_async_session
from app.models.milestone import Milestone
from app.schemas.milestone import Milestone as MilestoneSchema
from app.schemas.milestone import MilestoneCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/", response_model=list[MilestoneSchema])
async def get_milestones(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get all milestones"""
    stmt = select(Milestone).offset(skip).limit(limit)
    result = await session.execute(stmt)
    milestones = result.scalars().all()
    return milestones


@router.post("/", response_model=MilestoneSchema)
async def create_milestone(
    *,
    session: AsyncSession = Depends(get_async_session),
    milestone_in: MilestoneCreate,
) -> Any:
    """Create new milestone"""
    milestone = Milestone(**milestone_in.model_dump())
    session.add(milestone)
    await session.commit()
    await session.refresh(milestone)
    return milestone


@router.get("/{milestone_id}", response_model=MilestoneSchema)
async def get_milestone(
    *,
    session: AsyncSession = Depends(get_async_session),
    milestone_id: int,
) -> Any:
    """Get milestone by ID"""
    stmt = select(Milestone).where(Milestone.id == milestone_id)
    result = await session.execute(stmt)
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone
