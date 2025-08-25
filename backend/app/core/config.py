from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Tasket"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"  # pragma: allowlist secret
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = (
        "postgresql://tasket:tasket@localhost:5432/tasket"  # pragma: allowlist secret
    )

    # CORS
    ALLOWED_HOSTS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Frontend URL for OAuth redirects
    FRONTEND_URL: str = "http://localhost:3000"

    # GitHub Integration
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    # Google OAuth Integration
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    # Redis for WebSockets and caching
    REDIS_URL: str = "redis://localhost:6379"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Security Settings
    HTTPS_ONLY: bool = False  # Set to True in production for secure cookies

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
