"""Shared SQLAlchemy model primitives.

Business table mappings live in their owning modules.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import DeclarativeBase


def new_identifier() -> str:
    """Create a portable string primary key for PostgreSQL records."""

    return str(uuid4())


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for record defaults."""

    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Declarative base shared by module-owned database records."""
