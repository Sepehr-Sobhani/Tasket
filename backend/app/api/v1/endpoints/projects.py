from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import current_active_user
from app.core.database import get_async_session
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.schemas.project import Project as ProjectSchema
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project import ProjectService

router = APIRouter()


@router.get("/", response_model=list[ProjectSchema])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get all projects for the current user"""
    project_service = ProjectService(session)
    projects = await project_service.get_user_projects(
        user_id=current_user.id, skip=skip, limit=limit
    )
    return projects


@router.get("/stats/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get dashboard statistics for the current user"""
    project_service = ProjectService(session)
    stats = await project_service.get_dashboard_stats(user_id=current_user.id)
    return stats


@router.post("/", response_model=ProjectSchema)
async def create_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_in: ProjectCreate,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Create new project"""
    project_service = ProjectService(session)
    project = await project_service.create_project(
        project_data=project_in, creator_id=current_user.id
    )

    if not project:
        raise HTTPException(status_code=403, detail="Failed to create project")

    return project


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get project by ID"""
    project_service = ProjectService(session)
    project = await project_service.get_project_by_id(
        project_id=project_id, user_id=current_user.id
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Update project"""
    project_service = ProjectService(session)
    project = await project_service.update_project(
        project_id=project_id, project_data=project_in, user_id=current_user.id
    )

    if not project:
        raise HTTPException(
            status_code=403, detail="Only project admins can update projects"
        )

    return project


@router.delete("/{project_id}")
async def delete_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Delete project"""
    project_service = ProjectService(session)
    success = await project_service.delete_project(
        project_id=project_id, user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=403, detail="Only project owners can delete projects"
        )

    return {"message": "Project deleted successfully"}
