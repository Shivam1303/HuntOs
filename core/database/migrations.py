"""Alembic configuration helpers for application and integration tests."""

from pathlib import Path

from alembic.config import Config


def get_alembic_config(database_url: str) -> Config:
    """Return Alembic configuration using the supplied application database URL."""

    project_root = Path(__file__).resolve().parents[2]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    config.attributes["database_url"] = database_url
    return config
