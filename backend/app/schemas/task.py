from datetime import datetime

from app.models.task import TaskPriority, TaskStatus
from pydantic import BaseModel, validator


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.DRAFT
    priority: TaskPriority = TaskPriority.MEDIUM
    time_estimate: float | None = None
    story_points: int | None = None
    assignee_id: int | None = None
    epic_id: int | None = None
    milestone_id: int | None = None
    due_date: datetime | None = None

    @validator("time_estimate")
    def validate_time_estimate(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Time estimate must be positive")
        return v

    @validator("story_points")
    def validate_story_points(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Story points must be positive")
        return v


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None

    time_estimate: float | None = None
    story_points: int | None = None
    assignee_id: int | None = None
    epic_id: int | None = None
    milestone_id: int | None = None
    due_date: datetime | None = None
    position: int | None = None

    @validator("time_estimate")
    def validate_time_estimate(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Time estimate must be positive")
        return v

    @validator("story_points")
    def validate_story_points(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Story points must be positive")
        return v


class Task(TaskBase):
    id: int
    creator_id: int
    project_id: int
    github_issue_id: str | None = None
    github_issue_number: int | None = None
    position: int = 0
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class TaskCommentBase(BaseModel):
    content: str


class TaskCommentCreate(TaskCommentBase):
    pass


class TaskComment(TaskCommentBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class TaskEstimateBase(BaseModel):
    time_estimate: float | None = None
    story_points: int | None = None

    @validator("time_estimate")
    def validate_time_estimate(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Time estimate must be positive")
        return v

    @validator("story_points")
    def validate_story_points(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Story points must be positive")
        return v


class TaskEstimate(TaskEstimateBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class TaskVoteBase(BaseModel):
    vote_value: int

    @validator("vote_value")
    def validate_vote_value(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Vote value must be between 1 and 5")
        return v


class TaskVote(TaskVoteBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class TaskWithDetails(Task):
    comments: list[TaskComment] = []
    estimates: list[TaskEstimate] = []
    votes: list[TaskVote] = []
