from datetime import datetime

from pydantic import BaseModel


class EpicBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None


class EpicCreate(EpicBase):
    project_id: int


class EpicUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    is_active: bool | None = None


class Epic(EpicBase):
    id: int
    project_id: int
    is_active: bool = True
    github_issue_id: str | None = None
    github_issue_number: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
