"""FastAPI application factory.

Wires middleware in defense-in-depth order:
    request logging  -> rate limiting  -> API key auth  -> CORS  -> routes
(Starlette runs middleware bottom-up on the request and top-down on the
response, so the outermost middleware here sees every request first.)
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api.middleware.auth import APIKeyAuthMiddleware
from src.api.middleware.rate_limiter import RateLimitMiddleware
from src.api.middleware.request_logger import RequestLoggingMiddleware
from src.api.routes import health
from src.core.config import settings
from src.core.errors import RegFlowError
from src.core.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log = get_logger(__name__)
    log.info(
        "app.startup",
        app=settings.app_name,
        environment=settings.app_env,
        llm_provider=settings.llm_provider,
    )
    yield
    log.info("app.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="RegFlow AI",
        description=(
            "AI-native financial services platform — agentic compliance "
            "research, automated data analysis, and ML model monitoring."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS is registered first so it ends up innermost — it wraps the route
    # handlers and adds the right headers even on auth/rate-limit rejections.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
    )
    app.add_middleware(APIKeyAuthMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(health.router)

    @app.exception_handler(RegFlowError)
    async def regflow_error_handler(_: Request, exc: RegFlowError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    return app


app = create_app()
