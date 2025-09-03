from datetime import datetime
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.schemas.dashboard import DashboardStats
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = structlog.get_logger()


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_projects(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get all projects for a specific user with member counts"""
        stmt = (
            select(
                Project,
                func.count(ProjectMember.id).label("member_count"),
            )
            .join(ProjectMember, Project.id == ProjectMember.project_id, isouter=True)
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
            }
            projects.append(project_dict)

        return projects

    async def get_dashboard_stats(self, user_id: str) -> DashboardStats:
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

        # Count total projects
        total_projects = len(user_project_ids)

        # Count active projects (all projects are considered active for now)
        active_projects = total_projects

        return DashboardStats(
            total_projects=total_projects,
            unique_team_members=unique_team_members,
            active_projects=active_projects,
        )

    async def create_project(
        self, project_data: ProjectCreate, creator_id: str
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
        self, project_id: str, project_data: ProjectUpdate, user_id: str
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

    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project if user has permission"""
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

        # Delete project (cascade will handle project members)
        await self.db.delete(project)
        await self.db.commit()

        logger.info("Project deleted", project_id=project_id, user_id=user_id)
        return True

    async def add_project_member(
        self, project_id: str, user_id: str, role: ProjectMemberRole
    ) -> bool:
        """Add a member to a project if user has permission"""
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

        # Check if member already exists
        existing_member_stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        existing_member_result = await self.db.execute(existing_member_stmt)
        existing_member = existing_member_result.scalar_one_or_none()

        if existing_member:
            # Update existing member
            existing_member.role = role
            existing_member.is_active = True
            existing_member.updated_at = datetime.utcnow()
        else:
            # Create new member
            new_member = ProjectMember(
                project_id=project_id,
                user_id=user_id,
                role=role,
                is_active=True,
            )
            self.db.add(new_member)

        await self.db.commit()

        logger.info(
            "Project member added/updated",
            project_id=project_id,
            user_id=user_id,
            role=role.value,
        )
        return True

    async def remove_project_member(
        self, project_id: str, user_id: str, member_id: str
    ) -> bool:
        """Remove a member from a project if user has permission"""
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

        # Get member to remove
        member_stmt = select(ProjectMember).where(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id,
        )
        member_result = await self.db.execute(member_stmt)
        member = member_result.scalar_one_or_none()

        if not member:
            return False

        # Deactivate member
        member.is_active = False
        member.updated_at = datetime.utcnow()
        await self.db.commit()

        logger.info("Project member removed", project_id=project_id, user_id=member_id)
        return True

    async def get_project_members(
        self, project_id: str, user_id: str
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
        project_id: str,
        user_id: str,
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
        self, project_id: str, user_id: str
    ) -> dict[str, Any] | None:
        """Get a specific project with member counts if user has access"""
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

        # Get project with member counts
        stmt = (
            select(
                Project,
                func.count(ProjectMember.id).label("member_count"),
            )
            .outerjoin(ProjectMember, Project.id == ProjectMember.project_id)
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
        }

        return project_dict
