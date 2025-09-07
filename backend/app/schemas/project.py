from datetime import datetime

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class Project(ProjectBase):
    id: str
    is_default: bool = False
    created_at: datetime
    updated_at: datetime | None = None
    member_count: int = 0

    class Config:
        from_attributes = True


# ProjectMember schemas removed - using models directly instead of schemas
