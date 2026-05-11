"""Tests for src.core.errors."""

from __future__ import annotations

from src.core.errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitExceeded,
    RegFlowError,
)


def test_base_error_serialises_to_dict() -> None:
    err = RegFlowError("boom", details={"hint": "check logs"})
    payload = err.to_dict()
    assert payload["error"]["code"] == "internal_error"
    assert payload["error"]["message"] == "boom"
    assert payload["error"]["details"] == {"hint": "check logs"}


def test_subclasses_carry_status_codes() -> None:
    assert AuthenticationError("nope").status_code == 401
    assert NotFoundError("missing").status_code == 404
    assert RateLimitExceeded("slow down").status_code == 429
