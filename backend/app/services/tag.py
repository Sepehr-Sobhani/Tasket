from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.models.task import Tag, TaskTag
from app.models.project import ProjectMember
from app.models.task import Task
from app.schemas.tag import TagCreate, TagUpdate
import structlog

logger = structlog.get_logger()


class TagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_project_tags(
        self,
        project_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tag]:
        """Get all tags for a project if user has access"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()
        
        if not project_member:
            return []
        
        # Get tags with usage counts
        stmt = select(
            Tag,
            func.count(TaskTag.task_id).label('usage_count')
        ).join(TaskTag, Tag.id == TaskTag.tag_id, isouter=True
        ).join(Task, TaskTag.task_id == Task.id, isouter=True
        ).where(
            Tag.project_id == project_id,
            Tag.is_active == True
        ).group_by(Tag.id).order_by(Tag.name).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        # Attach usage count to each tag
        tags = []
        for row in rows:
            tag = row.Tag
            tag.usage_count = row.usage_count
            tags.append(tag)
        
        return tags

    async def get_tag_by_id(
        self,
        tag_id: int,
        user_id: int
    ) -> Optional[Tag]:
        """Get a specific tag if user has access"""
        stmt = select(Tag).join(ProjectMember).where(
            Tag.id == tag_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_tag(
        self,
        tag_data: TagCreate,
        creator_id: int
    ) -> Optional[Tag]:
        """Create a new tag if user is a member of the project"""
        # Check if user is a member of the project
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == tag_data.project_id,
            ProjectMember.user_id == creator_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        project_member = result.scalar_one_or_none()
        
        if not project_member:
            return None
        
        # Check if tag with same name already exists in project
        stmt = select(Tag).where(
            Tag.project_id == tag_data.project_id,
            Tag.name == tag_data.name,
            Tag.is_active == True
        )
        result = await self.db.execute(stmt)
        existing_tag = result.scalar_one_or_none()
        
        if existing_tag:
            return None  # Tag with same name already exists
        
        # Create tag
        tag = Tag(
            **tag_data.model_dump(),
            creator_id=creator_id
        )
        
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        
        logger.info("Tag created", tag_id=tag.id, creator_id=creator_id, project_id=tag_data.project_id)
        return tag

    async def update_tag(
        self,
        tag_id: int,
        tag_data: TagUpdate,
        user_id: int
    ) -> Optional[Tag]:
        """Update a tag if user has permission"""
        # Check if user is a member of the project
        stmt = select(Tag).join(ProjectMember).where(
            Tag.id == tag_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        tag = result.scalar_one_or_none()
        
        if not tag:
            return None
        
        # Check if new name conflicts with existing tag
        if tag_data.name and tag_data.name != tag.name:
            stmt = select(Tag).where(
                Tag.project_id == tag.project_id,
                Tag.name == tag_data.name,
                Tag.id != tag_id,
                Tag.is_active == True
            )
            result = await self.db.execute(stmt)
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                return None  # Name conflict
        
        # Update tag
        update_data = tag_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        tag.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(tag)
        
        logger.info("Tag updated", tag_id=tag_id, user_id=user_id)
        return tag

    async def delete_tag(
        self,
        tag_id: int,
        user_id: int
    ) -> bool:
        """Delete a tag if user has permission"""
        # Check if user is a member of the project
        stmt = select(Tag).join(ProjectMember).where(
            Tag.id == tag_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        tag = result.scalar_one_or_none()
        
        if not tag:
            return False
        
        # Check if tag is in use
        stmt = select(func.count(TaskTag.task_id)).where(TaskTag.tag_id == tag_id)
        result = await self.db.execute(stmt)
        usage_count = result.scalar()
        
        if usage_count > 0:
            return False  # Cannot delete tag that is in use
        
        # Soft delete tag
        tag.is_active = False
        tag.updated_at = datetime.utcnow()
        await self.db.commit()
        
        logger.info("Tag deleted", tag_id=tag_id, user_id=user_id)
        return True

    async def add_tag_to_task(
        self,
        tag_id: int,
        task_id: int,
        user_id: int
    ) -> Optional[TaskTag]:
        """Add a tag to a task if user has permission"""
        # Check if user is a member of the project
        stmt = select(Tag).join(ProjectMember).where(
            Tag.id == tag_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        tag = result.scalar_one_or_none()
        
        if not tag:
            return None
        
        # Get task
        stmt = select(Task).where(Task.id == task_id)
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task or task.project_id != tag.project_id:
            return None
        
        # Check if tag is already assigned to task
        stmt = select(TaskTag).where(
            TaskTag.tag_id == tag_id,
            TaskTag.task_id == task_id
        )
        result = await self.db.execute(stmt)
        existing_tag = result.scalar_one_or_none()
        
        if existing_tag:
            return existing_tag  # Tag already assigned
        
        # Create task tag relationship
        task_tag = TaskTag(
            tag_id=tag_id,
            task_id=task_id
        )
        
        self.db.add(task_tag)
        await self.db.commit()
        await self.db.refresh(task_tag)
        
        logger.info("Tag added to task", tag_id=tag_id, task_id=task_id, user_id=user_id)
        return task_tag

    async def remove_tag_from_task(
        self,
        task_id: int,
        tag_id: int,
        user_id: int
    ) -> bool:
        """Remove a tag from a task"""
        # Check if user is a member of the project
        stmt = select(TaskTag).join(Task).join(ProjectMember).where(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        task_tag = result.scalar_one_or_none()
        
        if not task_tag:
            return False
        
        # Check if user has permission to modify the task
        stmt = select(Task).join(ProjectMember).where(
            Task.id == task_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return False
        
        # Remove the tag from the task
        await self.db.delete(task_tag)
        await self.db.commit()
        
        return True

    async def get_task_tags(
        self,
        task_id: int,
        user_id: int
    ) -> List[Tag]:
        """Get all tags for a specific task"""
        # Check if user is a member of the project
        stmt = select(Task).join(ProjectMember).where(
            Task.id == task_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return []
        
        # Get tags for the task
        stmt = select(Tag).join(TaskTag).where(
            TaskTag.task_id == task_id,
            Tag.is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def search_tags(
        self,
        user_id: int,
        query: str,
        project_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Tag]:
        """Search tags by name"""
        # Build base query
        stmt = select(Tag).join(ProjectMember).where(
            ProjectMember.user_id == user_id,
            ProjectMember.is_active == True,
            Tag.is_active == True
        )
        
        # Add text search
        if query:
            stmt = stmt.where(Tag.name.ilike(f"%{query}%"))
        
        # Add project filter
        if project_id:
            stmt = stmt.where(Tag.project_id == project_id)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
