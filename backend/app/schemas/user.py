from datetime import datetime

from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None


class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    password: str | None = None

    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserInDBBase(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    github_id: str | None = None
    github_username: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    last_login: datetime | None = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
    github_access_token: str | None = None
