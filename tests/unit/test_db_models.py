"""Tests for the audit_log model using an in-memory SQLite database."""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database import Base
from src.db.models import AuditLog


@pytest_asyncio.fixture()
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


@pytest.mark.asyncio
async def test_audit_log_persists(session: AsyncSession) -> None:
    entry = AuditLog(
        event_type="api.auth.failed",
        actor_id="anonymous",
        request_id="req-abc",
        summary="Invalid API key",
        payload={"path": "/v1/sessions"},
    )
    session.add(entry)
    await session.commit()

    result = await session.execute(select(AuditLog))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].event_type == "api.auth.failed"
    assert rows[0].payload == {"path": "/v1/sessions"}
    assert rows[0].id is not None  # default UUID assigned
    assert rows[0].created_at is not None  # default timestamp assigned


@pytest.mark.asyncio
async def test_audit_log_required_fields(session: AsyncSession) -> None:
    entry = AuditLog(event_type="x", summary="y")
    session.add(entry)
    await session.commit()
    assert entry.actor_id is None
    assert entry.payload is None
