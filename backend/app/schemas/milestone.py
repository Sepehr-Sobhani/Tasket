from datetime import datetime

from pydantic import BaseModel


class MilestoneBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None


class MilestoneCreate(MilestoneBase):
    project_id: int


class MilestoneUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    is_active: bool | None = None


class Milestone(MilestoneBase):
    id: int
    project_id: int
    is_active: bool = True
    github_milestone_id: str | None = None
    github_milestone_number: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
