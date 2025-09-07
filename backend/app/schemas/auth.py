from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: str
    password: str


# OAuth schemas removed - now handled by frontend
