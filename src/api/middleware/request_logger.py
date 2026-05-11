"""Request/response logging middleware.

Generates a request id, binds it to the structlog context so every log line
inside the request handler carries it, and emits one summary line per request
with method, path, status, and duration.
"""

from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.logging import (
    bind_request_context,
    clear_request_context,
    get_logger,
)

REQUEST_ID_HEADER = "x-request-id"
_log = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        started = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            _log.exception("request.failed", duration_ms=round(duration_ms, 2))
            clear_request_context()
            raise

        duration_ms = (time.perf_counter() - started) * 1000
        _log.info(
            "request.completed",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        response.headers[REQUEST_ID_HEADER] = request_id
        clear_request_context()
        return response
