"""Tests for the in-memory sliding-window rate limiter."""

from __future__ import annotations

from src.api.middleware.rate_limiter import InMemoryRateLimiter


def test_allows_up_to_limit_then_blocks() -> None:
    limiter = InMemoryRateLimiter(max_requests=3, window_seconds=60)
    for _ in range(3):
        allowed, _ = limiter.allow("client-a", now=0.0)
        assert allowed
    blocked, retry_after = limiter.allow("client-a", now=0.0)
    assert blocked is False
    assert retry_after >= 1


def test_window_slides() -> None:
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=10)
    assert limiter.allow("c", now=0.0)[0] is True
    assert limiter.allow("c", now=1.0)[0] is True
    assert limiter.allow("c", now=2.0)[0] is False
    # After the window passes, requests are allowed again.
    assert limiter.allow("c", now=20.0)[0] is True


def test_separate_keys_are_independent() -> None:
    limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
    assert limiter.allow("a", now=0.0)[0] is True
    assert limiter.allow("b", now=0.0)[0] is True
    assert limiter.allow("a", now=0.0)[0] is False
