"""End-to-end tests for the FastAPI app: middleware + health endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.core.config import settings


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_health_is_public(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == settings.app_name


def test_request_id_header_set(client: TestClient) -> None:
    response = client.get("/health")
    assert "x-request-id" in {k.lower() for k in response.headers}


def test_protected_route_requires_api_key(client: TestClient) -> None:
    # /openapi.json is public; / is also public. Hit a path that doesn't exist
    # but isn't on the public allow-list — auth should reject before routing.
    response = client.get("/v1/sessions")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_failed"


def test_protected_route_with_valid_key_passes_auth(client: TestClient) -> None:
    response = client.get(
        "/v1/sessions",
        headers={"X-API-Key": settings.api_key.get_secret_value()},
    )
    # No route defined yet, so auth passes and FastAPI returns 404.
    assert response.status_code == 404
