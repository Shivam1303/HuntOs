"""PostgreSQL integration tests for the Phase 2 CSV import workflow."""

from collections.abc import Iterator

import pytest
from sqlalchemy import delete, select

from alembic import command
from core.config.settings import DatabaseConfigurationError, get_test_database_url
from core.database.database import PostgreSQLDatabase
from core.database.migrations import get_alembic_config
from modules.opportunities.csv_importer import CSVImporter
from modules.opportunities.models import RawOpportunityRecord
from modules.opportunities.repositories import PostgreSQLOpportunityRepository


@pytest.fixture(scope="module")
def postgres_database() -> Iterator[PostgreSQLDatabase]:
    """Apply migrations to an explicit isolated test database."""

    try:
        database_url = get_test_database_url()
    except DatabaseConfigurationError as error:
        pytest.skip(str(error))

    command.upgrade(get_alembic_config(database_url), "head")
    database = PostgreSQLDatabase(database_url)
    database.check_connection()
    yield database
    database.dispose()


@pytest.fixture(autouse=True)
def clean_raw_opportunities(
    postgres_database: PostgreSQLDatabase,
) -> Iterator[None]:
    """Keep each integration test isolated without touching other databases."""

    with postgres_database.session() as session:
        session.execute(delete(RawOpportunityRecord))
    yield
    with postgres_database.session() as session:
        session.execute(delete(RawOpportunityRecord))


def test_csv_import_commits_only_valid_rows_to_postgresql(
    postgres_database: PostgreSQLDatabase,
) -> None:
    """Persist valid rows through the real adapter and commit their fields."""

    content = (
        "source_id,platform,title,description,budget_min,budget_max,"
        "client_name,client_history,proposal_count,posted_at,url\n"
        "job-1,Upwork,First job,Build an API,500,900,Client One,5 hires,"
        "4,2026-07-23T09:00:00+05:30,https://example.com/jobs/1\n"
        "job-2,Contra,Invalid job,Build reports,not-money,,,,,,\n"
        "job-3,Contra,Second job,Automate reports,1200,1500,Client Two,"
        "2 hires,8,2026-07-23T10:00:00Z,https://example.com/jobs/3\n"
    ).encode()

    with postgres_database.session() as session:
        result = CSVImporter(PostgreSQLOpportunityRepository(session)).import_csv(
            content
        )

    assert result.total_rows == 3
    assert result.stored_count == 2
    assert result.rejected_count == 1
    assert result.errors[0].row_number == 3
    assert result.errors[0].field == "budget_min"

    with postgres_database.session() as session:
        records = session.scalars(
            select(RawOpportunityRecord).order_by(RawOpportunityRecord.source_id)
        ).all()

    assert [record.source_id for record in records] == ["job-1", "job-3"]
    assert records[0].title == "First job"
    assert records[0].proposal_count == 4
    assert records[0].posted_at is not None
    assert records[0].posted_at.utcoffset() is not None


def test_csv_import_reports_records_already_committed_as_duplicates(
    postgres_database: PostgreSQLDatabase,
) -> None:
    """Skip a second import without inserting the opportunity twice."""

    content = (
        "source_id,platform,title,description\n"
        "job-existing,Upwork,Existing job,Build a workflow\n"
    ).encode()

    with postgres_database.session() as session:
        first = CSVImporter(PostgreSQLOpportunityRepository(session)).import_csv(
            content
        )
    with postgres_database.session() as session:
        second = CSVImporter(PostgreSQLOpportunityRepository(session)).import_csv(
            content
        )

    assert first.stored_count == 1
    assert second.stored_count == 0
    assert second.skipped_count == 1
    assert second.duplicates[0].row_number == 2
    assert second.duplicates[0].reason == "opportunity already exists"

    with postgres_database.session() as session:
        records = session.scalars(select(RawOpportunityRecord)).all()
    assert len(records) == 1
