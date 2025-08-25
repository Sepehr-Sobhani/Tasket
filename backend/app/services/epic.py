from datetime import datetime
from typing import Any

import structlog
from app.models.epic import Epic
from app.models.project import ProjectMember, ProjectMemberRole
from app.models.task import Task
from app.schemas.epic import EpicCreate, EpicUpdate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class EpicService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_project_epics(
        self, project_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Epic]:
        """Get all epics for a project if user has access"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return []

        # Get epics with task counts
        stmt = (
            select(Epic, func.count(Task.id).label("task_count"))
            .join(Task, Epic.id == Task.epic_id, isouter=True)
            .where(Epic.project_id == project_id, Epic.is_active == True)
            .group_by(Epic.id)
            .order_by(Epic.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Attach task count to each epic
        epics = []
        for row in rows:
            epic = row.Epic
            epic.task_count = row.task_count
            epics.append(epic)

        return epics

    async def get_epic_by_id(self, epic_id: int, user_id: int) -> Epic | None:
        """Get a specific epic if user has access"""
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(
                Epic.id == epic_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_epic(self, epic_data: EpicCreate, creator_id: int) -> Epic | None:
        """Create a new epic if user is a member of the project"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == epic_data.project_id,
            ProjectMember.user_id == creator_id,
            ProjectMember.is_active == True,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return None

        # Create epic
        epic = Epic(**epic_data.model_dump(), creator_id=creator_id)

        self.db.add(epic)
        await self.db.commit()
        await self.db.refresh(epic)

        logger.info(
            "Epic created",
            epic_id=epic.id,
            creator_id=creator_id,
            project_id=epic_data.project_id,
        )
        return epic

    async def update_epic(
        self, epic_id: int, epic_data: EpicUpdate, user_id: int
    ) -> Epic | None:
        """Update an epic if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(
                Epic.id == epic_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        epic = result.scalar_one_or_none()

        if not epic:
            return None

        # Update epic
        update_data = epic_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(epic, field, value)

        epic.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(epic)

        logger.info("Epic updated", epic_id=epic_id, user_id=user_id)
        return epic

    async def delete_epic(self, epic_id: int, user_id: int) -> bool:
        """Delete an epic if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(
                Epic.id == epic_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        epic = result.scalar_one_or_none()

        if not epic:
            return False

        # Check if user is epic creator or project admin
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == epic.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == ProjectMemberRole.ADMIN,
            ProjectMember.is_active == True,
        )
        result = await self.db.execute(stmt)
        admin_member = result.scalar_one_or_none()

        if not admin_member and epic.creator_id != user_id:
            return False

        # Check if epic has tasks
        stmt = select(func.count(Task.id)).where(Task.epic_id == epic_id)
        result = await self.db.execute(stmt)
        task_count = result.scalar()

        if task_count > 0:
            return False  # Cannot delete epic with tasks

        # Soft delete epic
        epic.is_active = False
        epic.updated_at = datetime.utcnow()
        await self.db.commit()

        logger.info("Epic deleted", epic_id=epic_id, user_id=user_id)
        return True

    async def get_epic_tasks(
        self, epic_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        """Get all tasks for a specific epic if user has access"""
        # Check if user is a member of the project
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(
                Epic.id == epic_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        epic = result.scalar_one_or_none()

        if not epic:
            return []

        # Get tasks
        stmt = (
            select(Task)
            .where(Task.epic_id == epic_id)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def add_task_to_epic(
        self, epic_id: int, task_id: int, user_id: int
    ) -> Task | None:
        """Add a task to an epic if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(
                Epic.id == epic_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        epic = result.scalar_one_or_none()

        if not epic:
            return None

        # Get task
        stmt = select(Task).where(Task.id == task_id)
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task or task.project_id != epic.project_id:
            return None

        # Update task
        task.epic_id = epic_id
        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(task)

        logger.info(
            "Task added to epic", task_id=task_id, epic_id=epic_id, user_id=user_id
        )
        return task

    async def remove_task_from_epic(
        self, epic_id: int, task_id: int, user_id: int
    ) -> Task | None:
        """Remove a task from an epic if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(
                Epic.id == epic_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        epic = result.scalar_one_or_none()

        if not epic:
            return None

        # Get task
        stmt = select(Task).where(Task.id == task_id, Task.epic_id == epic_id)
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Remove task from epic
        task.epic_id = None
        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(task)

        logger.info(
            "Task removed from epic", task_id=task_id, epic_id=epic_id, user_id=user_id
        )
        return task

    async def get_epic_progress(
        self, epic_id: int, user_id: int
    ) -> dict[str, Any] | None:
        """Get progress statistics for an epic"""
        # Check if user is a member of the project
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(
                Epic.id == epic_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        epic = result.scalar_one_or_none()

        if not epic:
            return None

        # Get task statistics
        stmt = select(
            func.count(Task.id).label("total_tasks"),
            func.count(Task.id)
            .filter(Task.status == "completed")
            .label("completed_tasks"),
            func.count(Task.id)
            .filter(Task.status == "in_progress")
            .label("in_progress_tasks"),
            func.count(Task.id).filter(Task.status == "todo").label("todo_tasks"),
        ).where(Task.epic_id == epic_id)

        result = await self.db.execute(stmt)
        stats = result.one()

        total_tasks = stats.total_tasks
        if total_tasks == 0:
            progress_percentage = 0
        else:
            progress_percentage = (stats.completed_tasks / total_tasks) * 100

        return {
            "total_tasks": total_tasks,
            "completed_tasks": stats.completed_tasks,
            "in_progress_tasks": stats.in_progress_tasks,
            "todo_tasks": stats.todo_tasks,
            "progress_percentage": round(progress_percentage, 2),
        }

    async def search_epics(
        self,
        user_id: int,
        query: str,
        project_id: int | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Epic]:
        """Search epics with various filters"""
        # Build base query
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id, ProjectMember.is_active == True)
        )

        # Add text search
        if query:
            stmt = stmt.where(
                Epic.title.ilike(f"%{query}%") | Epic.description.ilike(f"%{query}%")
            )

        # Add filters
        if project_id:
            stmt = stmt.where(Epic.project_id == project_id)

        if status:
            stmt = stmt.where(Epic.status == status)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_epic_timeline(
        self, epic_id: int, user_id: int
    ) -> dict[str, Any] | None:
        """Get timeline information for an epic"""
        # Check if user is a member of the project
        stmt = (
            select(Epic)
            .join(ProjectMember)
            .where(
                Epic.id == epic_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        epic = result.scalar_one_or_none()

        if not epic:
            return None

        # Get earliest and latest task dates
        stmt = select(
            func.min(Task.created_at).label("earliest_task"),
            func.max(Task.updated_at).label("latest_update"),
        ).where(Task.epic_id == epic_id)

        result = await self.db.execute(stmt)
        timeline = result.one()

        return {
            "epic_start_date": epic.start_date,
            "epic_end_date": epic.end_date,
            "earliest_task_date": timeline.earliest_task,
            "latest_update_date": timeline.latest_update,
            "created_at": epic.created_at,
            "updated_at": epic.updated_at,
        }
