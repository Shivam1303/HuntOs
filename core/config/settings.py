"""Environment-backed configuration shared by the API and Alembic."""

import os

from sqlalchemy.engine import URL, make_url


class DatabaseConfigurationError(ValueError):
    """Raised when a required PostgreSQL URL is absent or unsafe."""


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
