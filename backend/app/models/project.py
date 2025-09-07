import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ulid import ULID

from app.core.database import Base


class ProjectMemberRole(enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(
        Boolean, default=False
    )  # Only one project per user can be default

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    project_id = Column(String(26), ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(26), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(ProjectMemberRole), default=ProjectMemberRole.MEMBER)

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<ProjectMember(project_id={self.project_id}, user_id={self.user_id}, role='{self.role.value}')>"
