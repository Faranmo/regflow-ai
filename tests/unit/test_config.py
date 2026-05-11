"""Tests for src.core.config."""

from __future__ import annotations

from src.core.config import Settings


def test_defaults_are_development_safe() -> None:
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.app_env == "development"
    assert s.debug is True
    assert s.is_production is False
    assert s.llm_provider == "ollama"
    assert s.rate_limit_requests > 0


def test_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.app_env == "production"
    assert s.debug is False
    assert s.log_level == "WARNING"
    assert s.is_production is True


def test_secret_values_not_in_repr() -> None:
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    rendered = repr(s)
    # SecretStr should mask the actual key value in any string rendering.
    assert "dev-key-change-me" not in rendered
