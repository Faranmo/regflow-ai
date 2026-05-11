"""In-memory token-bucket-ish rate limiter keyed by API key (or client IP).

Production should swap this for a Redis-backed limiter so counters survive
restarts and are shared across replicas. The interface stays identical.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.api.middleware.auth import API_KEY_HEADER, DEFAULT_PUBLIC_PATHS
from src.core.config import settings
from src.core.errors import RateLimitExceeded


class InMemoryRateLimiter:
    """Sliding-window counter, one deque of timestamps per client key."""

    def __init__(self, *, max_requests: int, window_seconds: float) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, *, now: float | None = None) -> tuple[bool, int]:
        current = now if now is not None else time.monotonic()
        window_start = current - self._window
        hits = self._hits[key]
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= self._max:
            retry_after = max(1, int(hits[0] + self._window - current))
            return False, retry_after
        hits.append(current)
        return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        *,
        limiter: InMemoryRateLimiter | None = None,
    ) -> None:
        super().__init__(app)
        self._limiter = limiter or InMemoryRateLimiter(
            max_requests=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if request.url.path in DEFAULT_PUBLIC_PATHS:
            return await call_next(request)

        client_key = request.headers.get(API_KEY_HEADER) or (
            request.client.host if request.client else "anonymous"
        )

        allowed, retry_after = self._limiter.allow(client_key)
        if not allowed:
            err = RateLimitExceeded(
                "Too many requests.",
                details={"retry_after_seconds": retry_after},
            )
            return JSONResponse(
                status_code=err.status_code,
                content=err.to_dict(),
                headers={"Retry-After": str(retry_after)},
            )

        response: Response = await call_next(request)
        return response
