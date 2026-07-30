"""Tests for storing validated CSV opportunities through the repository port."""

from modules.opportunities.csv_importer import CSVImporter
from modules.opportunities.duplicate_detection import opportunity_fingerprint
from modules.opportunities.models import RawOpportunityRecord
from modules.opportunities.schemas import RawOpportunity


class RecordingOpportunityRepository:
    """Small repository test double that records persistence calls."""

    def __init__(self) -> None:
        self.stored: list[tuple[str, RawOpportunity]] = []

    def add_raw_opportunity(
        self,
        *,
        fingerprint: str,
        opportunity: RawOpportunity,
    ) -> RawOpportunityRecord:
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
        return False


class FailingOpportunityRepository(RecordingOpportunityRepository):
    """Test double for proving storage failures remain visible."""

    def add_raw_opportunity(
        self,
        *,
        fingerprint: str,
        opportunity: RawOpportunity,
    ) -> RawOpportunityRecord:
        raise RuntimeError("database unavailable")


def test_csv_importer_stores_only_valid_opportunities() -> None:
    """Persist validated rows with deterministic fingerprints and return IDs."""

    repository = RecordingOpportunityRepository()
    importer = CSVImporter(repository)
    content = (
        "platform,title,description,budget_min\n"
        "Upwork,First valid job,Build an API,500\n"
        "Contra,Invalid job,Build automation,not-money\n"
        "Upwork,Second valid job,Integrate payments,1200\n"
    ).encode()

    result = importer.import_csv(content)

    assert result.total_rows == 3
    assert result.valid_count == 2
    assert result.rejected_count == 1
    assert result.stored_count == 2
    assert result.stored_opportunity_ids == ("stored-1", "stored-2")
    assert [item.title for _, item in repository.stored] == [
        "First valid job",
        "Second valid job",
    ]
    assert [fingerprint for fingerprint, _ in repository.stored] == [
        opportunity_fingerprint(item) for item in result.opportunities
    ]


def test_csv_importer_does_not_hide_storage_failures() -> None:
    """Let the transaction owner see persistence failures and roll back."""

    importer = CSVImporter(FailingOpportunityRepository())
    content = b"platform,title,description\nUpwork,Job,Build an API\n"

    try:
        importer.import_csv(content)
    except RuntimeError as error:
        assert str(error) == "database unavailable"
    else:
        raise AssertionError("storage failure was silently discarded")
