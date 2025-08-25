from datetime import datetime

from app.models.project import ProjectMemberRole, ProjectVisibility
from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    visibility: ProjectVisibility | None = None
    is_active: bool | None = None


class Project(ProjectBase):
    id: int
    is_active: bool = True
    github_repo_id: str | None = None
    github_repo_name: str | None = None
    github_repo_owner: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    member_count: int = 0
    task_count: int = 0

    class Config:
        from_attributes = True


class ProjectMemberBase(BaseModel):
    role: ProjectMemberRole = ProjectMemberRole.MEMBER


class ProjectMemberCreate(ProjectMemberBase):
    user_id: int


class ProjectMember(ProjectMemberBase):
    id: int
    project_id: int
    user_id: int
    is_active: bool = True
    joined_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ProjectWithMembers(Project):
    members: list[ProjectMember] = []
