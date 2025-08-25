
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str


class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class GitHubAuthRequest(BaseModel):
    code: str
    state: str | None = None


class GoogleAuthRequest(BaseModel):
    code: str
    state: str | None = None
    redirect_uri: str
