"""Tests for preventing duplicate CSV opportunity imports."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from modules.opportunities.csv_importer import CSVImporter
from modules.opportunities.duplicate_detection import opportunity_fingerprint
from modules.opportunities.models import RawOpportunityRecord
from modules.opportunities.repositories import (
    DuplicateOpportunityError,
    PostgreSQLOpportunityRepository,
)
from modules.opportunities.schemas import RawOpportunity


class DuplicateAwareRepository:
    """Repository double supporting existing and write-race duplicates."""

    def __init__(
        self,
        *,
        existing_fingerprints: set[str] | None = None,
        race_titles: set[str] | None = None,
    ) -> None:
        self.existing_fingerprints = existing_fingerprints or set()
        self.race_titles = race_titles or set()
        self.stored: list[tuple[str, RawOpportunity]] = []

    def add_raw_opportunity(
        self,
        *,
        fingerprint: str,
        opportunity: RawOpportunity,
    ) -> RawOpportunityRecord:
        if opportunity.title in self.race_titles:
            raise DuplicateOpportunityError("concurrent duplicate")
        self.stored.append((fingerprint, opportunity))
        return RawOpportunityRecord(
            id=f"stored-{len(self.stored)}",
            fingerprint=fingerprint,
            **opportunity.model_dump(),
        )

    def get_raw_opportunity_by_fingerprint(
        self, fingerprint: str
    ) -> RawOpportunityRecord | None:
        return None

    def is_duplicate(self, fingerprint: str) -> bool:
        return fingerprint in self.existing_fingerprints


def test_csv_importer_skips_all_duplicate_sources_and_continues() -> None:
    """Report upload, stored, and write-race duplicates without inserting them."""

    existing = RawOpportunity(
        source_id="existing-1",
        platform="Contra",
        title="Existing job",
        description="Build reporting automation",
    )
    repository = DuplicateAwareRepository(
        existing_fingerprints={opportunity_fingerprint(existing)},
        race_titles={"Concurrent job"},
    )
    importer = CSVImporter(repository)
    content = (
        "source_id,platform,title,description\n"
        "upload-1,Upwork,First job,Build an API\n"
        "UPLOAD-1, upwork , first job , build an api \n"
        "existing-1,Contra,Existing job,Build reporting automation\n"
        "race-1,Upwork,Concurrent job,Integrate payments\n"
        "unique-1,Contra,Unique job,Create a workflow\n"
    ).encode()

    result = importer.import_csv(content)

    assert result.total_rows == 5
    assert result.valid_count == 5
    assert result.rejected_count == 0
    assert result.stored_count == 2
    assert result.skipped_count == 3
    assert result.stored_opportunity_ids == ("stored-1", "stored-2")
    assert [opportunity.title for _, opportunity in repository.stored] == [
        "First job",
        "Unique job",
    ]
    assert [(item.row_number, item.reason) for item in result.duplicates] == [
        (3, "duplicate within this CSV upload"),
        (4, "opportunity already exists"),
        (5, "opportunity became duplicate during storage"),
    ]


class PostgreSQLUniqueViolation(Exception):
    """Minimal Psycopg-like unique violation for repository unit testing."""

    sqlstate = "23505"


def test_postgresql_repository_translates_unique_constraint_conflict() -> None:
    """Convert the final database duplicate guard into the domain exception."""

    session = MagicMock(spec=Session)
    session.scalar.return_value = None
    session.flush.side_effect = IntegrityError(
        "insert raw opportunity",
        {},
        PostgreSQLUniqueViolation(),
    )
    repository = PostgreSQLOpportunityRepository(session)

    with pytest.raises(DuplicateOpportunityError):
        repository.add_raw_opportunity(
            fingerprint="a" * 64,
            opportunity=RawOpportunity(
                platform="Upwork",
                title="Build an API",
                description="Implement a validated API.",
            ),
        )

    session.begin_nested.assert_called_once_with()
