"""Unit tests for opportunity CSV header and row validation."""

from datetime import datetime

import pytest

from modules.opportunities.csv_validator import (
    CSVHeaderValidationError,
    CSVRowValidationError,
    validate_csv_headers,
    validate_csv_row,
)


def test_validate_csv_headers_accepts_supported_columns() -> None:
    """Allow required headers with any supported optional headers."""

    validate_csv_headers(("description", "platform", "title"))
    validate_csv_headers(
        (
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
    )


@pytest.mark.parametrize(
    ("headers", "message"),
    [
        (("platform", "title"), "missing required CSV columns: description"),
        (
            ("platform", "title", "description", "contact_email"),
            "unsupported CSV columns: contact_email",
        ),
        (
            ("platform", "title", "title", "description"),
            "duplicate CSV columns: title",
        ),
    ],
)
def test_validate_csv_headers_rejects_invalid_contracts(
    headers: tuple[str, ...], message: str
) -> None:
    """Reject headers that could cause required or supplied input to be lost."""

    with pytest.raises(CSVHeaderValidationError, match=message):
        validate_csv_headers(headers)


def test_validate_csv_row_converts_all_supported_values() -> None:
    """Convert CSV strings into the existing opportunity domain schema."""

    opportunity = validate_csv_row(
        {
            "platform": " Upwork ",
            "title": "Build an API",
            "description": "Implement a document service.",
            "source_id": " job-123 ",
            "budget_min": "500.25",
            "budget_max": "1000",
            "client_name": " Example Client ",
            "client_history": "10 hires",
            "proposal_count": "7",
            "posted_at": "2026-07-22T10:30:00+05:30",
            "url": " https://example.com/jobs/123 ",
        }
    )

    assert opportunity.platform == "Upwork"
    assert opportunity.source_id == "job-123"
    assert opportunity.budget_min == 500.25
    assert opportunity.budget_max == 1000.0
    assert opportunity.client_name == "Example Client"
    assert opportunity.proposal_count == 7
    assert opportunity.posted_at == datetime.fromisoformat(
        "2026-07-22T10:30:00+05:30"
    )
    assert opportunity.posted_at.utcoffset() is not None
    assert opportunity.url == "https://example.com/jobs/123"


def test_validate_csv_row_maps_blank_optional_cells_to_none() -> None:
    """Treat empty optional cells as absent values."""

    opportunity = validate_csv_row(
        {
            "platform": "Upwork",
            "title": "Build an API",
            "description": "Implement a document service.",
            "source_id": " ",
            "budget_min": "",
            "budget_max": None,
            "client_name": " ",
            "client_history": "",
            "proposal_count": " ",
            "posted_at": "",
            "url": None,
        }
    )

    assert opportunity.source_id is None
    assert opportunity.budget_min is None
    assert opportunity.budget_max is None
    assert opportunity.client_name is None
    assert opportunity.client_history is None
    assert opportunity.proposal_count is None
    assert opportunity.posted_at is None
    assert opportunity.url is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", " "),
        ("budget_min", "NaN"),
        ("budget_max", "not-money"),
        ("proposal_count", "2.5"),
        ("posted_at", "2026-07-22T10:30:00"),
    ],
)
def test_validate_csv_row_reports_the_invalid_field(field: str, value: str) -> None:
    """Attach a field name to conversion and domain validation failures."""

    row = {
        "platform": "Upwork",
        "title": "Build an API",
        "description": "Implement a document service.",
        field: value,
    }

    with pytest.raises(CSVRowValidationError) as error:
        validate_csv_row(row)

    assert error.value.field == field


def test_validate_csv_row_rejects_reversed_budget_range() -> None:
    """Retain the domain model's budget ordering invariant."""

    with pytest.raises(CSVRowValidationError, match="budget_max") as error:
        validate_csv_row(
            {
                "platform": "Upwork",
                "title": "Build an API",
                "description": "Implement a document service.",
                "budget_min": "1000",
                "budget_max": "500",
            }
        )

    assert error.value.field == "budget_max"
