"""Async SQLAlchemy engine, session factory, and declarative base.

A single `Base` class is the parent of every ORM model. `get_session()` is the
FastAPI dependency that yields an `AsyncSession` per request and rolls back if
the handler raises.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


class Base(DeclarativeBase):
    """Declarative base for every ORM model in the app."""


def _build_engine() -> AsyncEngine:
    return create_async_engine(
        settings.database_url.get_secret_value(),
        echo=False,
        pool_pre_ping=True,
        future=True,
    )


engine: AsyncEngine = _build_engine()

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: one session per request, rollback on exception."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """Close the engine's connection pool. Call from app shutdown."""
    await engine.dispose()
