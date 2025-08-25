from datetime import datetime
from typing import Any

import structlog
from app.models.project import ProjectMember
from app.models.task import Task
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get a user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username"""
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(**user_data.model_dump())

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info("User created", user_id=user.id, email=user.email)
        return user

    async def update_user(
        self, user_id: int, user_data: UserUpdate, current_user_id: int
    ) -> User | None:
        """Update a user if the current user has permission"""
        # Users can only update their own profile
        if user_id != current_user_id:
            return None

        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Update user
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)

        logger.info("User updated", user_id=user_id)
        return user

    async def deactivate_user(self, user_id: int, current_user_id: int) -> bool:
        """Deactivate a user if the current user has permission"""
        # Users can only deactivate their own account
        if user_id != current_user_id:
            return False

        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return False

        # Deactivate user
        user.is_active = False
        user.updated_at = datetime.utcnow()

        # Deactivate all project memberships
        stmt = select(ProjectMember).where(ProjectMember.user_id == user_id)
        result = await self.db.execute(stmt)
        memberships = result.scalars().all()

        for membership in memberships:
            membership.is_active = False

        await self.db.commit()

        logger.info("User deactivated", user_id=user_id)
        return True

    async def get_user_projects(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get all projects for a specific user with basic info"""
        stmt = (
            select(ProjectMember.project_id, func.count(Task.id).label("task_count"))
            .join(Task, ProjectMember.project_id == Task.project_id, isouter=True)
            .where(ProjectMember.user_id == user_id, ProjectMember.is_active)
            .group_by(ProjectMember.project_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def get_user_stats(self, user_id: int) -> dict[str, int]:
        """Get statistics for a specific user"""
        # Count projects where user is a member
        projects_stmt = select(func.count(ProjectMember.project_id)).where(
            ProjectMember.user_id == user_id, ProjectMember.is_active
        )
        projects_result = await self.db.execute(projects_stmt)
        total_projects = projects_result.scalar()

        # Count tasks assigned to user
        assigned_tasks_stmt = select(func.count(Task.id)).where(
            Task.assignee_id == user_id
        )
        assigned_tasks_result = await self.db.execute(assigned_tasks_stmt)
        assigned_tasks = assigned_tasks_result.scalar()

        # Count tasks created by user
        created_tasks_stmt = select(func.count(Task.id)).where(
            Task.creator_id == user_id
        )
        created_tasks_result = await self.db.execute(created_tasks_stmt)
        created_tasks = created_tasks_result.scalar()

        return {
            "total_projects": total_projects,
            "assigned_tasks": assigned_tasks,
            "created_tasks": created_tasks,
        }

    async def search_users(
        self, query: str, current_user_id: int, skip: int = 0, limit: int = 50
    ) -> list[User]:
        """Search users by name, username, or email"""
        # Only search for active users
        stmt = (
            select(User)
            .where(
                User.is_active,
                User.id != current_user_id,  # Exclude current user
                (
                    User.full_name.ilike(f"%{query}%")
                    | User.username.ilike(f"%{query}%")
                    | User.email.ilike(f"%{query}%")
                ),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_users_by_ids(self, user_ids: list[int]) -> list[User]:
        """Get multiple users by their IDs"""
        if not user_ids:
            return []

        stmt = select(User).where(User.id.in_(user_ids))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.last_login = datetime.utcnow()
        await self.db.commit()

        return True

    async def check_user_exists(self, email: str, username: str) -> dict[str, bool]:
        """Check if email or username already exists"""
        email_exists = False
        username_exists = False

        if email:
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            email_exists = result.scalar_one_or_none() is not None

        if username:
            stmt = select(User).where(User.username == username)
            result = await self.db.execute(stmt)
            username_exists = result.scalar_one_or_none() is not None

        return {"email_exists": email_exists, "username_exists": username_exists}
