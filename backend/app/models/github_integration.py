from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GitHubIntegration(Base):
    __tablename__ = "github_integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # OAuth tokens
    access_token = Column(String(500), nullable=False)
    refresh_token = Column(String(500), nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Repository information
    repo_owner = Column(String(100), nullable=True)
    repo_name = Column(String(100), nullable=True)
    repo_id = Column(String(100), nullable=True)

    # Webhook configuration
    webhook_id = Column(String(100), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    webhook_url = Column(String(500), nullable=True)

    # Sync settings
    sync_issues = Column(Boolean, default=True)
    sync_pull_requests = Column(Boolean, default=False)
    sync_comments = Column(Boolean, default=True)
    sync_labels = Column(Boolean, default=True)

    # Additional metadata
    integration_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User")
    project = relationship("Project")

    def __repr__(self):
        return f"<GitHubIntegration(id={self.id}, user_id={self.user_id}, repo='{self.repo_owner}/{self.repo_name}')>"
