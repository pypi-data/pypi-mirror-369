"""Database configuration and session management."""

import os
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from ..core.config import get_settings

# Create the declarative base
Base = declarative_base()

# Global variables for database
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None

settings = get_settings()


def get_database_url() -> str:
    """Get database URL from settings."""
    if settings.database_url:
        return settings.database_url
    
    # Fallback to SQLite for development
    db_path = os.path.join(os.getcwd(), "autogen_a2a.db")
    return f"sqlite:///{db_path}"


def get_async_database_url() -> str:
    """Get async database URL from settings."""
    url = get_database_url()
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://")
    elif url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


def init_db() -> None:
    """Initialize the database."""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    # Synchronous engine for migrations
    engine = create_engine(
        get_database_url(),
        connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {},
        echo=settings.database_echo,
    )
    
    # Asynchronous engine for application
    async_engine = create_async_engine(
        get_async_database_url(),
        echo=settings.database_echo,
    )
    
    # Session makers
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    if AsyncSessionLocal is None:
        init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db() -> None:
    """Close database connections."""
    global async_engine, engine
    
    if async_engine:
        await async_engine.dispose()
    
    if engine:
        engine.dispose()


async def create_tables() -> None:
    """Create all database tables."""
    if async_engine is None:
        init_db()
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all database tables."""
    if async_engine is None:
        init_db()
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def get_engine():
    """Get the database engine."""
    global engine
    if engine is None:
        init_db()
    return engine


def get_async_engine():
    """Get the async database engine."""
    global async_engine
    if async_engine is None:
        init_db()
    return async_engine
