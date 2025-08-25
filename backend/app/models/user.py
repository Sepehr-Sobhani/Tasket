from fastapi_users.db import SQLAlchemyBaseUserTable
from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(
        String(255), nullable=True
    )  # Nullable for GitHub OAuth users
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # OAuth fields
    oauth_accounts = relationship("OAuthAccount", back_populates="user")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects = relationship("ProjectMember", back_populates="user")
    created_tasks = relationship(
        "Task", back_populates="creator", foreign_keys="Task.creator_id"
    )
    assigned_tasks = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )
    task_comments = relationship("TaskComment", back_populates="user")
    task_estimates = relationship("TaskEstimate", back_populates="user")
    task_votes = relationship("TaskVote", back_populates="user")
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    def verify_password(self, plain_password: str) -> bool:
        """Verify a plain password against the hashed password"""
        if not self.hashed_password:
            return False
        return pwd_context.verify(plain_password, self.hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def set_password(self, password: str):
        """Set a new password"""
        self.hashed_password = self.get_password_hash(password)

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.is_active and (self.hashed_password or self.github_id)

    def can_access_project(
        self, project_id: int, required_role: str = "member"
    ) -> bool:
        """Check if user can access a project with the required role"""
        if self.is_superuser:
            return True

        for project_member in self.projects:
            if project_member.project_id == project_id:
                if required_role == "admin":
                    return project_member.role == "admin"
                return project_member.role in ["admin", "member"]
        return False

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    oauth_name = Column(String(100), nullable=False)
    access_token = Column(String(500), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    account_id = Column(String(255), nullable=False)
    account_email = Column(String(255), nullable=True)

    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="oauth_accounts")

    def __repr__(self):
        return f"<OAuthAccount(id={self.id}, oauth_name='{self.oauth_name}', account_id='{self.account_id}')>"
