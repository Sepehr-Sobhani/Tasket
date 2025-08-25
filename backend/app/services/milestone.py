from datetime import datetime
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.milestone import Milestone
from app.models.project import ProjectMember, ProjectMemberRole
from app.models.task import Task
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate

logger = structlog.get_logger()


class MilestoneService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_project_milestones(
        self, project_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Milestone]:
        """Get all milestones for a project if user has access"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return []

        # Get milestones with task counts
        stmt = (
            select(Milestone, func.count(Task.id).label("task_count"))
            .join(Task, Milestone.id == Task.milestone_id, isouter=True)
            .where(Milestone.project_id == project_id, Milestone.is_active)
            .group_by(Milestone.id)
            .order_by(Milestone.due_date)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Attach task count to each milestone
        milestones = []
        for row in rows:
            milestone = row.Milestone
            milestone.task_count = row.task_count
            milestones.append(milestone)

        return milestones

    async def get_milestone_by_id(
        self, milestone_id: int, user_id: int
    ) -> Milestone | None:
        """Get a specific milestone if user has access"""
        stmt = (
            select(Milestone)
            .join(ProjectMember)
            .where(
                Milestone.id == milestone_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_milestone(
        self, milestone_data: MilestoneCreate, creator_id: int
    ) -> Milestone | None:
        """Create a new milestone if user is a member of the project"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == milestone_data.project_id,
            ProjectMember.user_id == creator_id,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return None

        # Create milestone
        milestone = Milestone(**milestone_data.model_dump(), creator_id=creator_id)

        self.db.add(milestone)
        await self.db.commit()
        await self.db.refresh(milestone)

        logger.info(
            "Milestone created",
            milestone_id=milestone.id,
            creator_id=creator_id,
            project_id=milestone_data.project_id,
        )
        return milestone

    async def update_milestone(
        self, milestone_id: int, milestone_data: MilestoneUpdate, user_id: int
    ) -> Milestone | None:
        """Update a milestone if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Milestone)
            .join(ProjectMember)
            .where(
                Milestone.id == milestone_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        milestone = result.scalar_one_or_none()

        if not milestone:
            return None

        # Update milestone
        update_data = milestone_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(milestone, field, value)

        milestone.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(milestone)

        logger.info("Milestone updated", milestone_id=milestone_id, user_id=user_id)
        return milestone

    async def delete_milestone(self, milestone_id: int, user_id: int) -> bool:
        """Delete a milestone if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Milestone)
            .join(ProjectMember)
            .where(
                Milestone.id == milestone_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        milestone = result.scalar_one_or_none()

        if not milestone:
            return False

        # Check if user is milestone creator or project admin
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == milestone.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == ProjectMemberRole.ADMIN,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        admin_member = result.scalar_one_or_none()

        if not admin_member and milestone.creator_id != user_id:
            return False

        # Check if milestone has tasks
        stmt = select(func.count(Task.id)).where(Task.milestone_id == milestone_id)
        result = await self.db.execute(stmt)
        task_count = result.scalar()

        if task_count > 0:
            return False  # Cannot delete milestone with tasks

        # Soft delete milestone
        milestone.is_active = False
        milestone.updated_at = datetime.utcnow()
        await self.db.commit()

        logger.info("Milestone deleted", milestone_id=milestone_id, user_id=user_id)
        return True

    async def get_milestone_tasks(
        self, milestone_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        """Get all tasks for a specific milestone if user has access"""
        # Check if user is a member of the project
        stmt = (
            select(Milestone)
            .join(ProjectMember)
            .where(
                Milestone.id == milestone_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        milestone = result.scalar_one_or_none()

        if not milestone:
            return []

        # Get tasks
        stmt = (
            select(Task)
            .where(Task.milestone_id == milestone_id)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def add_task_to_milestone(
        self, milestone_id: int, task_id: int, user_id: int
    ) -> Task | None:
        """Add a task to a milestone if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Milestone)
            .join(ProjectMember)
            .where(
                Milestone.id == milestone_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        milestone = result.scalar_one_or_none()

        if not milestone:
            return None

        # Get task
        stmt = select(Task).where(Task.id == task_id)
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task or task.project_id != milestone.project_id:
            return None

        # Update task
        task.milestone_id = milestone_id
        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(task)

        logger.info(
            "Task added to milestone",
            task_id=task_id,
            milestone_id=milestone_id,
            user_id=user_id,
        )
        return task

    async def remove_task_from_milestone(
        self, milestone_id: int, task_id: int, user_id: int
    ) -> Task | None:
        """Remove a task from a milestone if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Milestone)
            .join(ProjectMember)
            .where(
                Milestone.id == milestone_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        milestone = result.scalar_one_or_none()

        if not milestone:
            return None

        # Get task
        stmt = select(Task).where(Task.id == task_id, Task.milestone_id == milestone_id)
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Remove task from milestone
        task.milestone_id = None
        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(task)

        logger.info(
            "Task removed from milestone",
            task_id=task_id,
            milestone_id=milestone_id,
            user_id=user_id,
        )
        return task

    async def get_milestone_progress(
        self, milestone_id: int, user_id: int
    ) -> dict[str, Any] | None:
        """Get progress statistics for a milestone"""
        # Check if user is a member of the project
        stmt = (
            select(Milestone)
            .join(ProjectMember)
            .where(
                Milestone.id == milestone_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        milestone = result.scalar_one_or_none()

        if not milestone:
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
        ).where(Task.milestone_id == milestone_id)

        result = await self.db.execute(stmt)
        stats = result.one()

        total_tasks = stats.total_tasks
        if total_tasks == 0:
            progress_percentage = 0
        else:
            progress_percentage = (stats.completed_tasks / total_tasks) * 100

        # Check if milestone is overdue
        is_overdue = False
        if milestone.due_date and milestone.due_date < datetime.utcnow():
            is_overdue = True

        return {
            "total_tasks": total_tasks,
            "completed_tasks": stats.completed_tasks,
            "in_progress_tasks": stats.in_progress_tasks,
            "todo_tasks": stats.todo_tasks,
            "progress_percentage": round(progress_percentage, 2),
            "is_overdue": is_overdue,
            "due_date": milestone.due_date,
        }

    async def get_upcoming_milestones(
        self, project_id: int, user_id: int, days: int = 30, limit: int = 10
    ) -> list[Milestone]:
        """Get upcoming milestones for a project"""
        from datetime import timedelta

        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return []

        # Get upcoming milestones
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        stmt = (
            select(Milestone)
            .where(
                Milestone.project_id == project_id,
                Milestone.is_active,
                Milestone.due_date >= datetime.utcnow(),
                Milestone.due_date <= cutoff_date,
            )
            .order_by(Milestone.due_date)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_overdue_milestones(
        self, project_id: int, user_id: int, limit: int = 10
    ) -> list[Milestone]:
        """Get overdue milestones for a project"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return []

        # Get overdue milestones
        stmt = (
            select(Milestone)
            .where(
                Milestone.project_id == project_id,
                Milestone.is_active,
                Milestone.due_date < datetime.utcnow(),
            )
            .order_by(Milestone.due_date)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def search_milestones(
        self,
        user_id: int,
        query: str,
        project_id: int | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Milestone]:
        """Search milestones with various filters"""
        # Build base query
        stmt = (
            select(Milestone)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id, ProjectMember.is_active)
        )

        # Add text search
        if query:
            stmt = stmt.where(
                Milestone.title.ilike(f"%{query}%")
                | Milestone.description.ilike(f"%{query}%")
            )

        # Add filters
        if project_id:
            stmt = stmt.where(Milestone.project_id == project_id)

        if status:
            stmt = stmt.where(Milestone.status == status)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
