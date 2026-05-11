"""API key authentication middleware.

Validates the `X-API-Key` header on every request except the public allow-list
(health, docs, openapi). Constant-time comparison prevents timing attacks
against the configured key.
"""

from __future__ import annotations

import hmac
from collections.abc import Iterable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.core.config import settings
from src.core.errors import AuthenticationError

API_KEY_HEADER = "x-api-key"

DEFAULT_PUBLIC_PATHS: frozenset[str] = frozenset(
    {"/health", "/healthz", "/", "/docs", "/redoc", "/openapi.json"}
)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        *,
        public_paths: Iterable[str] = DEFAULT_PUBLIC_PATHS,
    ) -> None:
        super().__init__(app)
        self._public_paths = frozenset(public_paths)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if request.url.path in self._public_paths:
            return await call_next(request)

        provided = request.headers.get(API_KEY_HEADER, "")
        expected = settings.api_key.get_secret_value()

        if not provided or not hmac.compare_digest(provided, expected):
            err = AuthenticationError("Missing or invalid API key.")
            return JSONResponse(status_code=err.status_code, content=err.to_dict())

        response: Response = await call_next(request)
        return response
