"""Structured logging setup using structlog.

All logs are emitted as JSON in production and as readable key=value lines in
development. A request-scoped context (request_id, user_id, agent_id) is
carried automatically via contextvars so every log line within a request can be
correlated.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
from structlog.types import Processor

from src.core.config import settings

__all__ = [
    "configure_logging",
    "get_logger",
    "bind_request_context",
    "clear_request_context",
]


def _build_processors() -> list[Processor]:
    shared: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if settings.is_production:
        shared.append(structlog.processors.JSONRenderer())
    else:
        shared.append(structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty()))
    return shared


def configure_logging() -> None:
    """Initialise structlog and the stdlib logger. Safe to call multiple times."""
    level = logging.getLevelName(settings.log_level)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
        force=True,
    )

    structlog.configure(
        processors=_build_processors(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name) if name else structlog.get_logger()


def bind_request_context(**values: Any) -> None:
    """Bind request-scoped fields onto every log line for the current task."""
    bind_contextvars(**values)


def clear_request_context() -> None:
    clear_contextvars()
