"""ORM models. Import this module from Alembic env so autogenerate sees them."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class AuditLog(Base):
    """Append-only record of meaningful system events.

    Financial regulators require traceability — every agent action, tool call,
    auth event, and admin operation should land here. Indexed by `created_at`
    and `event_type` for time-bounded queries; `actor_id` and `request_id` make
    it easy to reconstruct a single user's session.
    """

    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, index=True
    )
    request_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    summary: Mapped[str] = mapped_column(String(512), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
