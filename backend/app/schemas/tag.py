from datetime import datetime

from pydantic import BaseModel, validator


class TagBase(BaseModel):
    name: str
    color: str  # Hex color code

    @validator("color")
    def validate_color(cls, v):
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return v


class TagCreate(TagBase):
    project_id: int


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None

    @validator("color")
    def validate_color(cls, v):
        if v is not None and (not v.startswith("#") or len(v) != 7):
            raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return v


class Tag(TagBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class TaskTagBase(BaseModel):
    pass


class TaskTagCreate(TaskTagBase):
    task_id: int
    tag_id: int


class TaskTag(TaskTagBase):
    id: int
    task_id: int
    tag_id: int
    created_at: datetime

    class Config:
        from_attributes = True
