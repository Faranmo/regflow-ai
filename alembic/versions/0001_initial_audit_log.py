"""initial audit_log table

Revision ID: 0001
Revises:
Create Date: 2026-05-12

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("summary", sa.String(length=512), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
    )
    op.create_index(
        "ix_audit_log_created_at", "audit_log", ["created_at"], unique=False
    )
    op.create_index(
        "ix_audit_log_event_type", "audit_log", ["event_type"], unique=False
    )
    op.create_index(
        "ix_audit_log_actor_id", "audit_log", ["actor_id"], unique=False
    )
    op.create_index(
        "ix_audit_log_request_id", "audit_log", ["request_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_audit_log_request_id", table_name="audit_log")
    op.drop_index("ix_audit_log_actor_id", table_name="audit_log")
    op.drop_index("ix_audit_log_event_type", table_name="audit_log")
    op.drop_index("ix_audit_log_created_at", table_name="audit_log")
    op.drop_table("audit_log")
