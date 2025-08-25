from datetime import datetime

from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str
    project_id: int | None = None
    task_id: int | None = None


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    unread_count: int
