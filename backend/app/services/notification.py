from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.notification import Notification
from app.core.websocket import manager
import structlog

logger = structlog.get_logger()


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        project_id: Optional[int] = None,
        task_id: Optional[int] = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            project_id=project_id,
            task_id=task_id,
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        # Send real-time notification via WebSocket
        try:
            await self._send_realtime_notification(user_id, notification)
        except Exception as e:
            logger.error("Failed to send real-time notification", error=str(e))
        
        logger.info("Notification created", notification_id=notification.id, user_id=user_id)
        return notification

    async def create_task_assigned_notification(self, task_id: int, assignee_id: int, project_id: int):
        from app.models.task import Task
        from app.models.project import Project
        
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if task and project:
            await self.create_notification(
                user_id=assignee_id,
                title=f"Task assigned: {task.title}",
                message=f"You have been assigned to '{task.title}' in project '{project.name}'",
                project_id=project_id,
                task_id=task_id
            )

    async def create_comment_notification(self, comment_id: int, task_id: int, project_id: int, mentioned_users: List[int]):
        from app.models.task import Task, TaskComment
        from app.models.project import Project
        
        result = await self.db.execute(select(TaskComment).where(TaskComment.id == comment_id))
        comment = result.scalar_one_or_none()
        
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if comment and task and project:
            # Notify task assignee and creator (if different from commenter)
            notify_users = set()
            if task.assignee_id and task.assignee_id != comment.user_id:
                notify_users.add(task.assignee_id)
            if task.creator_id != comment.user_id:
                notify_users.add(task.creator_id)
            
            # Add mentioned users
            notify_users.update(mentioned_users)
            
            for user_id in notify_users:
                await self.create_notification(
                    user_id=user_id,
                    title=f"New comment on: {task.title}",
                    message=f"'{comment.user.username}' commented: {comment.content[:100]}...",
                    project_id=project_id,
                    task_id=task_id
                )

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    async def mark_all_as_read(self, user_id: int) -> int:
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        notifications = result.scalars().all()
        
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        await self.db.commit()
        return len(notifications)

    async def get_user_notifications(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_unread_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        notifications = result.scalars().all()
        return len(notifications)

    async def _send_realtime_notification(self, user_id: int, notification: Notification):
        try:
            message = {
                "type": "notification",
                "data": {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "created_at": notification.created_at.isoformat(),
                    "project_id": notification.project_id,
                    "task_id": notification.task_id,
                    "is_read": notification.is_read
                }
            }
            await manager.send_personal_message(message, user_id)
        except Exception as e:
            logger.error("Failed to send real-time notification", error=str(e))
