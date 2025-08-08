import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://chatbot:password@localhost:5432/chatbot_db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create engines
engine = create_engine(DATABASE_URL)
async_engine = create_async_engine(ASYNC_DATABASE_URL)

# Create session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


def create_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        yield session