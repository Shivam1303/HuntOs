# PostgreSQL Development Guide

## Why PostgreSQL Replaced SQLite

SQLite was suitable for the initial local prototype, but PostgreSQL is now the application database because it provides production-grade concurrency, stronger constraint enforcement, reliable timezone-aware timestamp handling, and exact `Numeric`/`Decimal` storage for monetary values. The application uses SQLAlchemy 2.0 with Psycopg 3 through `DATABASE_URL`.

Schema changes are never created during application startup. Every schema change must be represented by a reviewed Alembic migration.

## Configuration

Copy `.env.example` to `.env` and set local values. For an API running on the host against Compose PostgreSQL, use:

```text
DATABASE_URL=postgresql+psycopg://hunter:hunter@localhost:5432/hunter
POSTGRES_DB=hunter
POSTGRES_USER=hunter
POSTGRES_PASSWORD=hunter
POSTGRES_PORT=5432
APP_HOST=0.0.0.0
APP_PORT=8000
```

Compose overrides `DATABASE_URL` for the API container so it uses `postgres` as the database host. Do not put credentials in Python source code.

## Start the Full Application

Build and start PostgreSQL plus the API:

```bash
docker compose up --build
```

The API service waits for the PostgreSQL health check, runs `alembic upgrade head`, and then starts Uvicorn. The health endpoint is available at `http://localhost:8000/health`.

## Start Only PostgreSQL

To run the API directly on the host while Docker provides PostgreSQL:

```bash
docker compose up -d postgres
docker compose ps
```

## Run the API Locally

After PostgreSQL is healthy, install dependencies and apply migrations:

```bash
pip install -e ".[dev]"
alembic upgrade head
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The host application uses the `localhost` database URL in `.env.example`; do not use the Compose-only `postgres` hostname from the host.

## Alembic Migrations

Apply all migrations:

```bash
alembic upgrade head
```

Create a reviewed migration after changing SQLAlchemy ORM metadata:

```bash
alembic revision --autogenerate -m "describe schema change"
```

Review the generated revision, especially constraints, indexes, `Numeric` precision, and timezone-aware columns, before committing it. Autogeneration is a draft, not an approval step.

Downgrade all schema revisions:

```bash
alembic downgrade base
```

To verify reversibility locally:

```bash
alembic downgrade base
alembic upgrade head
```

## Tests and Test Database Isolation

Run pure tests and configured checks:

```bash
pytest
ruff check .
mypy
```

PostgreSQL integration tests require a separate database URL. It must point to a database whose name ends in `_test`; the application rejects any other value to prevent tests from changing development data:

```bash
TEST_DATABASE_URL=postgresql+psycopg://hunter:hunter@localhost:5432/hunter_test pytest
```

Integration tests apply Alembic migrations to the test database and clean database tables between tests. They must never use `DATABASE_URL` for test writes.

## Schema Change Rule

Do not call `Base.metadata.create_all()` in application startup code. Do not edit a database manually and rely on it as application state. Any change to ORM models that affects schema, constraints, indexes, enums, or column types requires a new Alembic migration and an upgrade/downgrade verification.
