"""Health endpoints. Public — no auth required."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from src.core.config import settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    version: str


@router.get("/health", response_model=HealthResponse)
@router.get("/healthz", response_model=HealthResponse, include_in_schema=False)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        environment=settings.app_env,
        version="0.1.0",
    )
