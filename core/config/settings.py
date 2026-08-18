"""Environment-backed configuration shared by the API and Alembic."""

import os

from pydantic import BaseModel, ConfigDict, Field, SecretStr
from sqlalchemy.engine import URL, make_url


class DatabaseConfigurationError(ValueError):
    """Raised when a required PostgreSQL URL is absent or unsafe."""


class LLMSettings(BaseModel):
    """Validated provider-neutral LLM settings read from the environment."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider: str = "gemini"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = ""
    timeout_seconds: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    max_output_tokens: int = Field(default=2048, gt=0)
    temperature: float = Field(default=0.2, ge=0, le=2)

    @classmethod
    def from_env(cls) -> "LLMSettings":
        """Build settings from environment variables without reading secret files."""

        api_key = os.getenv("GEMINI_API_KEY")
        return cls.model_validate(
            {
                "provider": os.getenv("LLM_PROVIDER", "gemini"),
                "gemini_api_key": api_key or None,
                "gemini_model": os.getenv("GEMINI_MODEL", ""),
                "timeout_seconds": os.getenv("LLM_TIMEOUT_SECONDS", "30"),
                "max_retries": os.getenv("LLM_MAX_RETRIES", "3"),
                "max_output_tokens": os.getenv("LLM_MAX_OUTPUT_TOKENS", "2048"),
                "temperature": os.getenv("LLM_TEMPERATURE", "0.2"),
            }
        )


def get_database_url() -> str:
    """Return the required Psycopg 3 PostgreSQL connection URL."""

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise DatabaseConfigurationError("DATABASE_URL must be configured")
    _validate_postgresql_url(database_url)
    return database_url


def get_test_database_url() -> str:
    """Return an explicit isolated PostgreSQL integration-test database URL."""

    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        raise DatabaseConfigurationError("TEST_DATABASE_URL must be configured")
    parsed_url = _validate_postgresql_url(database_url)
    if not parsed_url.database or not parsed_url.database.endswith("_test"):
        raise DatabaseConfigurationError(
            "TEST_DATABASE_URL must target a *_test database"
        )
    return database_url


def _validate_postgresql_url(database_url: str) -> URL:
    parsed_url = make_url(database_url)
    if parsed_url.drivername != "postgresql+psycopg":
        raise DatabaseConfigurationError("DATABASE_URL must use postgresql+psycopg")
    return parsed_url
