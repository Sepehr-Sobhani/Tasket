from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.auth import current_active_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema
from app.services.task import TaskService

router = APIRouter()


@router.get("/", response_model=List[TaskSchema])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get all tasks for projects the user is a member of"""
    task_service = TaskService(session)
    tasks = await task_service.get_user_tasks(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return tasks


@router.post("/", response_model=TaskSchema)
async def create_task(
    *,
    session: AsyncSession = Depends(get_async_session),
    task_in: TaskCreate,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Create new task"""
    task_service = TaskService(session)
    task = await task_service.create_task(
        task_data=task_in,
        creator_id=current_user.id
    )
    
    if not task:
        raise HTTPException(status_code=403, detail="You must be a member of the project to create tasks")
    
    return task


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    *,
    session: AsyncSession = Depends(get_async_session),
    task_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get task by ID"""
    task_service = TaskService(session)
    task = await task_service.get_task_by_id(
        task_id=task_id,
        user_id=current_user.id
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    *,
    session: AsyncSession = Depends(get_async_session),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Update task"""
    task_service = TaskService(session)
    task = await task_service.update_task(
        task_id=task_id,
        task_data=task_in,
        user_id=current_user.id
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.delete("/{task_id}")
async def delete_task(
    *,
    session: AsyncSession = Depends(get_async_session),
    task_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Delete task"""
    task_service = TaskService(session)
    success = await task_service.delete_task(
        task_id=task_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}


@router.get("/project/{project_id}", response_model=List[TaskSchema])
async def get_tasks_by_project(
    *,
    session: AsyncSession = Depends(get_async_session),
    project_id: int,
    current_user: User = Depends(current_active_user),
) -> Any:
    """Get all tasks for a specific project"""
    task_service = TaskService(session)
    tasks = await task_service.get_project_tasks(
        project_id=project_id,
        user_id=current_user.id
    )
    
    if tasks is None:
        raise HTTPException(status_code=403, detail="You must be a member of the project to view tasks")
    
    return tasks
