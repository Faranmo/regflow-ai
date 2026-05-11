"""Typed application settings loaded from environment variables.

Settings are loaded once at import time and validated by Pydantic. Importing
`settings` anywhere in the codebase gives a fully-typed singleton — no scattered
os.getenv calls, no string-typed config bugs.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LLMProvider = Literal["ollama", "azure_openai", "openai"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "regflow-ai"
    app_env: Environment = "development"
    debug: bool = True
    log_level: LogLevel = "INFO"

    # --- API security ---
    api_key: SecretStr = Field(
        default=SecretStr("dev-key-change-me"),
        description="Server-side API key required on every request.",
    )
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="Origins allowed for CORS. Restrict in production.",
    )

    # --- LLM ---
    llm_provider: LLMProvider = "ollama"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: SecretStr = SecretStr("ollama")
    llm_model: str = "llama3.1:8b"
    llm_api_version: str | None = None
    llm_request_timeout_seconds: float = 60.0

    # --- Database ---
    database_url: SecretStr = SecretStr(
        "postgresql+asyncpg://regflow:regflow_dev@localhost:5432/regflow_db"
    )

    # --- ChromaDB ---
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # --- Rate limiting ---
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
