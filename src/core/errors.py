"""Application exception hierarchy.

A single base class (`RegFlowError`) lets API middleware translate any domain
exception to a JSON error response with the right HTTP status. Each subclass
carries its own status code so call sites don't need to know HTTP details.
"""

from __future__ import annotations

from typing import Any


class RegFlowError(Exception):
    """Base class for every application-raised error."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ConfigurationError(RegFlowError):
    status_code = 500
    code = "configuration_error"


class AuthenticationError(RegFlowError):
    status_code = 401
    code = "authentication_failed"


class AuthorizationError(RegFlowError):
    status_code = 403
    code = "forbidden"


class NotFoundError(RegFlowError):
    status_code = 404
    code = "not_found"


class ValidationError(RegFlowError):
    status_code = 422
    code = "validation_error"


class RateLimitExceeded(RegFlowError):  # noqa: N818 — domain-meaningful name, not an "Error"
    status_code = 429
    code = "rate_limit_exceeded"


class UpstreamError(RegFlowError):
    """An upstream dependency (LLM, DB, third-party API) failed."""

    status_code = 502
    code = "upstream_error"


class TimeoutError(RegFlowError):  # noqa: A001 — shadowing builtin is intentional here
    status_code = 504
    code = "timeout"
