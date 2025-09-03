from datetime import datetime

from pydantic import BaseModel

from app.models.project import ProjectVisibility


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
    id: str
    is_active: bool = True
    is_default: bool = False
    github_repo_id: str | None = None
    github_repo_name: str | None = None
    github_repo_owner: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    member_count: int = 0

    class Config:
        from_attributes = True


# ProjectMember schemas removed - using models directly instead of schemas
