from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str


class LoginRequest(BaseModel):
    email: str
    password: str


# OAuth schemas removed - now handled by frontend
