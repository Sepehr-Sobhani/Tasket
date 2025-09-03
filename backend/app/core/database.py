from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# For async operations, use asyncpg
async_database_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Create async engine and session factory
async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# For sync operations, use psycopg2
sync_database_url = settings.DATABASE_URL
sync_engine = create_engine(
    sync_database_url,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get sync database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_session():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        yield session


# For testing purposes (PostgreSQL)
async def get_test_db():
    """Get test database session"""
    test_database_url = settings.DATABASE_URL.replace("/tasket", "/tasket_test")
    engine_test = create_async_engine(
        test_database_url,
        pool_pre_ping=True,
        echo=False,
    )
    TestingSessionLocal = async_sessionmaker(
        engine_test,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestingSessionLocal() as session:
        yield session
