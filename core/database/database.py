"""SQLite database construction and transaction handling."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from core.database.models import Base


class SQLiteDatabase:
    """Own SQLite engine and sessions without depending on business modules."""

    def __init__(self, database_url: str) -> None:
        if not database_url.startswith("sqlite:"):
            raise ValueError("SQLiteDatabase requires a sqlite database URL")

        self._engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )
        self._enable_foreign_keys()
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    @classmethod
    def for_file(cls, database_path: Path) -> "SQLiteDatabase":
        """Create a SQLite database wrapper for a local file path."""

        return cls(f"sqlite:///{database_path}")

    @property
    def engine(self) -> Engine:
        """Expose the engine for infrastructure-level integrations."""

        return self._engine

    def initialize(self) -> None:
        """Create all MVP tables when they do not already exist."""

        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Yield a transaction-scoped session and commit only on success."""

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        """Release SQLite connections held by the engine."""

        self._engine.dispose()

    def _enable_foreign_keys(self) -> None:
        """Enable SQLite foreign-key enforcement for this engine."""

        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_connection: Any, _: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
