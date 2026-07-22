"""PostgreSQL database construction and transaction handling."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker


class PostgreSQLDatabase:
    """Own PostgreSQL engine and sessions without depending on business modules."""

    def __init__(self, database_url: str) -> None:
        if not database_url.startswith("postgresql+psycopg:"):
            raise ValueError("PostgreSQLDatabase requires a postgresql+psycopg URL")

        self._engine = create_engine(database_url, pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def engine(self) -> Engine:
        """Expose the engine for infrastructure-level integrations."""

        return self._engine

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
        """Release PostgreSQL connections held by the engine."""

        self._engine.dispose()

    def check_connection(self) -> None:
        """Raise a database exception when PostgreSQL is unavailable."""

        with self._engine.connect() as connection:
            connection.execute(text("SELECT 1"))
