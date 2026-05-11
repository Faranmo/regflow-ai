"""Retry policies for transient failures (network, LLM, DB).

Wraps tenacity with sensible defaults: exponential backoff, jitter, capped
attempts, and only retrying on known-transient exception types. Non-transient
errors (auth, validation) pass through immediately.
"""

from __future__ import annotations

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from src.core.errors import UpstreamError

TRANSIENT_EXCEPTIONS: tuple[type[BaseException], ...] = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.ReadError,
    httpx.RemoteProtocolError,
    UpstreamError,
)


def transient_retry(
    *,
    max_attempts: int = 3,
    initial_wait_seconds: float = 0.5,
    max_wait_seconds: float = 8.0,
) -> AsyncRetrying:
    """Async retry policy for transient upstream failures.

    Usage:
        async for attempt in transient_retry():
            with attempt:
                response = await client.post(...)
    """
    return AsyncRetrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential_jitter(
            initial=initial_wait_seconds,
            max=max_wait_seconds,
        ),
        retry=retry_if_exception_type(TRANSIENT_EXCEPTIONS),
        reraise=True,
    )
