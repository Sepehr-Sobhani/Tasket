import enum

from app.core.database import Base
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class TaskStatus(enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.DRAFT)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)

    # Estimates
    time_estimate = Column(Float, nullable=True)  # in hours
    story_points = Column(Integer, nullable=True)

    # Assignments
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    epic_id = Column(Integer, ForeignKey("epics.id"), nullable=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)

    # GitHub integration
    github_issue_id = Column(String(100), nullable=True)
    github_issue_number = Column(Integer, nullable=True)

    # Position for drag-and-drop
    position = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    creator = relationship(
        "User", back_populates="created_tasks", foreign_keys=[creator_id]
    )
    assignee = relationship(
        "User", back_populates="assigned_tasks", foreign_keys=[assignee_id]
    )
    project = relationship("Project", back_populates="tasks")
    epic = relationship("Epic", back_populates="tasks")
    milestone = relationship("Milestone", back_populates="tasks")
    comments = relationship(
        "TaskComment", back_populates="task", cascade="all, delete-orphan"
    )
    estimates = relationship(
        "TaskEstimate", back_populates="task", cascade="all, delete-orphan"
    )
    votes = relationship(
        "TaskVote", back_populates="task", cascade="all, delete-orphan"
    )
    tags = relationship("TaskTag", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<Task(id={self.id}, title='{self.title}', status='{self.status.value}')>"
        )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=False)  # Hex color code
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="tags")
    task_tags = relationship(
        "TaskTag", back_populates="tag", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', project_id={self.project_id})>"


class TaskTag(Base):
    __tablename__ = "task_tags"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="tags")
    tag = relationship("Tag", back_populates="task_tags")

    def __repr__(self):
        return f"<TaskTag(task_id={self.task_id}, tag_id={self.tag_id})>"


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="task_comments")

    def __repr__(self):
        return f"<TaskComment(id={self.id}, task_id={self.task_id}, user_id={self.user_id})>"


class TaskEstimate(Base):
    __tablename__ = "task_estimates"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_estimate = Column(Float, nullable=True)  # in hours
    story_points = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    task = relationship("Task", back_populates="estimates")
    user = relationship("User", back_populates="task_estimates")

    def __repr__(self):
        return f"<TaskEstimate(id={self.id}, task_id={self.task_id}, user_id={self.user_id})>"


class TaskVote(Base):
    __tablename__ = "task_votes"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote_value = Column(Integer, nullable=False)  # 1-5 scale or custom values

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    task = relationship("Task", back_populates="votes")
    user = relationship("User", back_populates="task_votes")

    def __repr__(self):
        return f"<TaskVote(id={self.id}, task_id={self.task_id}, user_id={self.user_id}, vote={self.vote_value})>"
