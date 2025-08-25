from datetime import datetime
from typing import Any

import structlog
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.models.task import Task
from app.schemas.dashboard import DashboardStats
from app.schemas.project import ProjectCreate, ProjectUpdate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_projects(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get all projects for a specific user with member and task counts"""
        stmt = (
            select(
                Project,
                func.count(ProjectMember.id).label("member_count"),
                func.count(Task.id).label("task_count"),
            )
            .join(ProjectMember, Project.id == ProjectMember.project_id, isouter=True)
            .join(Task, Project.id == Task.project_id, isouter=True)
            .where(ProjectMember.user_id == user_id, ProjectMember.is_active)
            .group_by(Project.id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Convert to list of dictionaries with counts
        projects = []
        for row in rows:
            project_dict = {
                "id": row.Project.id,
                "name": row.Project.name,
                "description": row.Project.description,
                "visibility": row.Project.visibility,
                "is_active": row.Project.is_active,
                "github_repo_id": row.Project.github_repo_id,
                "github_repo_name": row.Project.github_repo_name,
                "github_repo_owner": row.Project.github_repo_owner,
                "created_at": row.Project.created_at,
                "updated_at": row.Project.updated_at,
                "member_count": row.member_count,
                "task_count": row.task_count,
            }
            projects.append(project_dict)

        return projects

    async def get_dashboard_stats(self, user_id: int) -> DashboardStats:
        """Get dashboard statistics for a specific user"""
        # Get all projects where user is a member
        user_projects_stmt = (
            select(Project.id)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id, ProjectMember.is_active)
        )
        user_projects_result = await self.db.execute(user_projects_stmt)
        user_project_ids = [row[0] for row in user_projects_result.all()]

        if not user_project_ids:
            return DashboardStats(
                total_projects=0,
                unique_team_members=0,
                total_tasks=0,
                active_projects=0,
            )

        # Count unique team members across all user's projects
        unique_members_stmt = select(
            func.count(func.distinct(ProjectMember.user_id))
        ).where(
            ProjectMember.project_id.in_(user_project_ids),
            ProjectMember.is_active,
        )
        unique_members_result = await self.db.execute(unique_members_stmt)
        unique_team_members = unique_members_result.scalar()

        # Count total tasks across all user's projects
        total_tasks_stmt = select(func.count(Task.id)).where(
            Task.project_id.in_(user_project_ids)
        )
        total_tasks_result = await self.db.execute(total_tasks_stmt)
        total_tasks = total_tasks_result.scalar()

        # Count active projects (projects with at least one task)
        active_projects_stmt = select(func.count(func.distinct(Task.project_id))).where(
            Task.project_id.in_(user_project_ids)
        )
        active_projects_result = await self.db.execute(active_projects_stmt)
        active_projects = active_projects_result.scalar()

        return DashboardStats(
            total_projects=len(user_project_ids),
            unique_team_members=unique_team_members,
            total_tasks=total_tasks,
            active_projects=active_projects,
        )

    async def create_project(
        self, project_data: ProjectCreate, creator_id: int
    ) -> Project:
        project = Project(**project_data.model_dump())

        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)

        # Add creator as project admin
        project_member = ProjectMember(
            project_id=project.id,
            user_id=creator_id,
            role=ProjectMemberRole.ADMIN,
            is_active=True,
        )

        self.db.add(project_member)
        await self.db.commit()

        logger.info("Project created", project_id=project.id, creator_id=creator_id)
        return project

    async def update_project(
        self, project_id: int, project_data: ProjectUpdate, user_id: int
    ) -> Project | None:
        """Update a project if user has permission"""
        # Check if user is project admin
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == ProjectMemberRole.ADMIN,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return None

        # Get project
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()

        if not project:
            return None

        # Update project
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        project.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(project)

        logger.info("Project updated", project_id=project_id, user_id=user_id)
        return project

    async def delete_project(self, project_id: int, user_id: int) -> bool:
        """Delete a project if user is admin"""
        # Check if user is project admin
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == ProjectMemberRole.ADMIN,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()

        if not project_member:
            return False

        # Get project
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()

        if not project:
            return False

        # Soft delete project
        project.is_active = False
        project.updated_at = datetime.utcnow()

        # Deactivate all project members
        stmt = select(ProjectMember).where(ProjectMember.project_id == project_id)
        result = await self.db.execute(stmt)
        members = result.scalars().all()

        for member in members:
            member.is_active = False

        await self.db.commit()

        logger.info("Project deleted", project_id=project_id, user_id=user_id)
        return True

    async def add_project_member(
        self, project_id: int, user_id: int, role: ProjectMemberRole, added_by_id: int
    ) -> ProjectMember | None:
        """Add a member to a project"""
        # Check if user adding member has permission
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == added_by_id,
            ProjectMember.role == ProjectMemberRole.ADMIN,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        admin_member = result.scalar_one_or_none()

        if not admin_member:
            return None

        # Check if user is already a member
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        result = await self.db.execute(stmt)
        existing_member = result.scalar_one_or_none()

        if existing_member:
            if existing_member.is_active:
                return None  # Already an active member
            else:
                # Reactivate existing member
                existing_member.is_active = True
                existing_member.role = role
                await self.db.commit()
                await self.db.refresh(existing_member)
                return existing_member

        # Create new member
        project_member = ProjectMember(
            project_id=project_id, user_id=user_id, role=role, is_active=True
        )

        self.db.add(project_member)
        await self.db.commit()
        await self.db.refresh(project_member)

        logger.info(
            "Project member added", project_id=project_id, user_id=user_id, role=role
        )
        return project_member

    async def remove_project_member(
        self, project_id: int, user_id: int, removed_by_id: int
    ) -> bool:
        """Remove a member from a project"""
        # Check if user removing member has permission
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == removed_by_id,
            ProjectMember.role == ProjectMemberRole.ADMIN,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        admin_member = result.scalar_one_or_none()

        if not admin_member:
            return False

        # Check if trying to remove admin
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == ProjectMemberRole.ADMIN,
        )
        result = await self.db.execute(stmt)
        target_member = result.scalar_one_or_none()

        if target_member and target_member.role == ProjectMemberRole.ADMIN:
            return False  # Cannot remove admin

        # Remove member
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        result = await self.db.execute(stmt)
        member = result.scalar_one_or_none()

        if member:
            member.is_active = False
            await self.db.commit()

            logger.info(
                "Project member removed", project_id=project_id, user_id=user_id
            )
            return True

        return False

    async def get_project_members(
        self, project_id: int, user_id: int
    ) -> list[ProjectMember]:
        """Get all members of a project if user has access"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active,
        )
        result = await self.db.execute(stmt)
        user_member = result.scalar_one_or_none()

        if not user_member:
            return []

        # Get all active members
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.is_active
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def check_user_project_access(
        self,
        project_id: int,
        user_id: int,
        required_role: ProjectMemberRole | None = None,
    ) -> bool:
        """Check if user has access to a project with optional role requirement"""
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active,
        )

        if required_role:
            stmt = stmt.where(ProjectMember.role == required_role)

        result = await self.db.execute(stmt)
        member = result.scalar_one_or_none()

        return member is not None

    async def get_project_by_id(
        self, project_id: int, user_id: int
    ) -> dict[str, Any] | None:
        """Get a specific project with member and task counts if user has access"""
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

        # Get project with member and task counts
        stmt = (
            select(
                Project,
                func.count(ProjectMember.id).label("member_count"),
                func.count(Task.id).label("task_count"),
            )
            .outerjoin(ProjectMember, Project.id == ProjectMember.project_id)
            .outerjoin(Task, Project.id == Task.project_id)
            .where(Project.id == project_id)
            .group_by(Project.id)
        )

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return None

        # Convert to dictionary with counts
        project_dict = {
            "id": row.Project.id,
            "name": row.Project.name,
            "description": row.Project.description,
            "visibility": row.Project.visibility,
            "is_active": row.Project.is_active,
            "github_repo_id": row.Project.github_repo_id,
            "github_repo_name": row.Project.github_repo_name,
            "github_repo_owner": row.Project.github_repo_owner,
            "created_at": row.Project.created_at,
            "updated_at": row.Project.updated_at,
            "member_count": row.member_count,
            "task_count": row.task_count,
        }

        return project_dict
