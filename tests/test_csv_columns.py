"""Tests for the Phase 2 CSV column contract."""

from modules.opportunities.csv_columns import (
    OPTIONAL_CSV_COLUMNS,
    REQUIRED_CSV_COLUMNS,
    SUPPORTED_CSV_COLUMNS,
)


def test_supported_csv_columns_follow_the_canonical_order() -> None:
    """Expose every documented import field in one stable order."""

    assert SUPPORTED_CSV_COLUMNS == (
        "platform",
        "title",
        "description",
        "source_id",
        "budget_min",
        "budget_max",
        "client_name",
        "client_history",
        "proposal_count",
        "posted_at",
        "url",
    )


def test_csv_columns_identify_required_and_optional_fields() -> None:
    """Keep required headers distinct from optional import metadata."""

    assert REQUIRED_CSV_COLUMNS == ("platform", "title", "description")
    assert OPTIONAL_CSV_COLUMNS == SUPPORTED_CSV_COLUMNS[3:]
    assert set(REQUIRED_CSV_COLUMNS).isdisjoint(OPTIONAL_CSV_COLUMNS)
    assert REQUIRED_CSV_COLUMNS + OPTIONAL_CSV_COLUMNS == SUPPORTED_CSV_COLUMNS
