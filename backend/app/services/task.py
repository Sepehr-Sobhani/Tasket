from datetime import datetime

import structlog
from app.models.project import ProjectMember, ProjectMemberRole
from app.models.task import Task, TaskComment
from app.schemas.task import TaskCreate, TaskUpdate
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        project_id: int | None = None,
    ) -> list[Task]:
        """Get all tasks for projects the user is a member of"""
        # Build base query
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id, ProjectMember.is_active)
        )

        # Add project filter if specified
        if project_id:
            stmt = stmt.where(Task.project_id == project_id)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_task_by_id(self, task_id: int, user_id: int) -> Task | None:
        """Get a specific task if user has access"""
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                Task.id == task_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_task(self, task_data: TaskCreate, creator_id: int) -> Task | None:
        """Create a new task if user is a member of the project"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == task_data.project_id,
            ProjectMember.user_id == creator_id,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return None

        # Create task
        task = Task(**task_data.model_dump(), creator_id=creator_id)

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        logger.info(
            "Task created",
            task_id=task.id,
            creator_id=creator_id,
            project_id=task_data.project_id,
        )
        return task

    async def update_task(
        self, task_id: int, task_data: TaskUpdate, user_id: int
    ) -> Task | None:
        """Update a task if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                Task.id == task_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Update task
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(task)

        logger.info("Task updated", task_id=task_id, user_id=user_id)
        return task

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete a task if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                Task.id == task_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return False

        # Check if user is task creator or project admin
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == ProjectMemberRole.ADMIN,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        admin_member = result.scalar_one_or_none()

        if not admin_member and task.creator_id != user_id:
            return False

        # Hard delete task
        await self.db.delete(task)
        await self.db.commit()

        logger.info("Task deleted", task_id=task_id, user_id=user_id)
        return True

    async def assign_task(
        self, task_id: int, assignee_id: int, user_id: int
    ) -> Task | None:
        """Assign a task to a user if the assigning user has permission"""
        # Check if assigning user is a member of the project
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                Task.id == task_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Check if assignee is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == assignee_id,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        assignee_member = result.scalar_one_or_none()

        if not assignee_member:
            return None

        # Update task assignment
        task.assignee_id = assignee_id
        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(task)

        logger.info(
            "Task assigned",
            task_id=task_id,
            assignee_id=assignee_id,
            assigned_by=user_id,
        )
        return task

    async def update_task_status(
        self, task_id: int, status: str, user_id: int
    ) -> Task | None:
        """Update task status if user has permission"""
        # Check if user is a member of the project
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                Task.id == task_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Update status
        task.status = status
        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(task)

        logger.info(
            "Task status updated", task_id=task_id, status=status, user_id=user_id
        )
        return task

    async def add_task_comment(
        self, task_id: int, content: str, user_id: int
    ) -> TaskComment | None:
        """Add a comment to a task if user has access"""
        # Check if user is a member of the project
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                Task.id == task_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Create comment
        comment = TaskComment(task_id=task_id, user_id=user_id, content=content)

        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)

        logger.info(
            "Task comment added",
            comment_id=comment.id,
            task_id=task_id,
            user_id=user_id,
        )
        return comment

    async def get_task_comments(
        self, task_id: int, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[TaskComment]:
        """Get comments for a task if user has access"""
        # Check if user is a member of the project
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                Task.id == task_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active,
            )
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return []

        # Get comments
        stmt = (
            select(TaskComment)
            .where(TaskComment.task_id == task_id)
            .order_by(TaskComment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def search_tasks(
        self,
        user_id: int,
        query: str,
        project_id: int | None = None,
        status: str | None = None,
        assignee_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Task]:
        """Search tasks with various filters"""
        # Build base query
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id, ProjectMember.is_active)
        )

        # Add text search
        if query:
            stmt = stmt.where(
                Task.title.ilike(f"%{query}%") | Task.description.ilike(f"%{query}%")
            )

        # Add filters
        if project_id:
            stmt = stmt.where(Task.project_id == project_id)

        if status:
            stmt = stmt.where(Task.status == status)

        if assignee_id:
            stmt = stmt.where(Task.assignee_id == assignee_id)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_user_assigned_tasks(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[Task]:
        """Get tasks assigned to a specific user"""
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                and_(
                    Task.assignee_id == user_id,
                    ProjectMember.user_id == user_id,
                    ProjectMember.is_active,
                )
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_user_created_tasks(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[Task]:
        """Get tasks created by a specific user"""
        stmt = (
            select(Task)
            .join(Task.project)
            .join(ProjectMember)
            .where(
                and_(
                    Task.creator_id == user_id,
                    ProjectMember.user_id == user_id,
                    ProjectMember.is_active,
                )
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_project_tasks(
        self, project_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Task] | None:
        """Get all tasks for a specific project if user has access"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return None

        # Get tasks for the project
        stmt = (
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()
