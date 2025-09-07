from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ulid import ULID

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)

    # OAuth fields
    oauth_accounts = relationship("OAuthAccount", back_populates="user")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projects = relationship("ProjectMember", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(String(26), primary_key=True, default=lambda: str(ULID()), index=True)
    oauth_name = Column(String(100), nullable=False)
    account_id = Column(String(255), nullable=False)
    account_email = Column(String(255), nullable=True)

    # Foreign key to user
    user_id = Column(String(26), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="oauth_accounts")

    def __repr__(self):
        return f"<OAuthAccount(id={self.id}, oauth_name='{self.oauth_name}', account_id='{self.account_id}')>"
