from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# For async operations, use asyncpg
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

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

# Create base class for models
Base = declarative_base()


async def get_async_session():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        yield session


# For testing purposes (PostgreSQL)
async def get_test_db():
    """Get test database session"""
    test_database_url = settings.DATABASE_URL.replace("/tasket", "/tasket_test")
    test_async_url = test_database_url.replace("postgresql://", "postgresql+asyncpg://")
    engine_test = create_async_engine(
        test_async_url,
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
