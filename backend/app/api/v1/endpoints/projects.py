from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_helpers import get_current_user_from_request
from app.core.database import get_async_session
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.schemas.dashboard import DashboardStats
from app.schemas.project import Project as ProjectSchema
from app.schemas.project import ProjectCreate

router = APIRouter()


@router.get("/default", response_model=ProjectSchema)
async def get_default_project(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get the user's default project"""
    # Get current user from request state (automatically authenticated by middleware)
    current_user = get_current_user_from_request(request)

    # Query for the user's default project
    query = (
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id, Project.is_default is True)
    )

    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="No default project found")

    return project


@router.get("/", response_model=list[ProjectSchema])
async def get_projects(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get all projects for the current user"""
    # Get current user from request state (automatically authenticated by middleware)
    current_user = get_current_user_from_request(request)

    # Query projects where the user is a member
    query = (
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )

    result = await session.execute(query)
    projects = result.scalars().unique().all()

    # Always return a list, even if empty
    return list(projects) if projects else []


@router.get("/stats/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get dashboard statistics for the current user"""
    # Get current user from request state (automatically authenticated by middleware)
    current_user = get_current_user_from_request(request)

    # Query projects where the user is a member
    query = (
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id)
    )

    result = await session.execute(query)
    projects = result.scalars().unique().all()

    # Always return a list, even if empty
    project_list = list(projects) if projects else []

    # Calculate unique team members across all projects
    unique_members = set()
    for project in project_list:
        # Get all members for this project
        member_query = select(ProjectMember).where(
            ProjectMember.project_id == project.id
        )
        member_result = await session.execute(member_query)
        members = member_result.scalars().all()
        unique_members.update([m.user_id for m in members])

    return DashboardStats(
        total_projects=len(project_list),
        unique_team_members=len(unique_members),
        active_projects=len([p for p in project_list if p.is_active]),
    )


@router.post("/", response_model=ProjectSchema)
async def create_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_in: ProjectCreate,
    request: Request,
) -> Any:
    """Create new project"""
    # Get current user from request state (automatically authenticated by middleware)
    current_user = get_current_user_from_request(request)

    project = Project(**project_in.dict())
    session.add(project)
    await session.commit()
    await session.refresh(project)

    # Add the creator as an admin member
    member = ProjectMember(
        user_id=current_user.id, project_id=project.id, role=ProjectMemberRole.ADMIN
    )
    session.add(member)
    await session.commit()

    return project


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_id: str,
    request: Request,
) -> Any:
    """Get project by ID"""
    # Get current user from request state (automatically authenticated by middleware)
    current_user = get_current_user_from_request(request)

    query = (
        select(Project)
        .join(ProjectMember)
        .where(Project.id == project_id, ProjectMember.user_id == current_user.id)
    )

    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project
