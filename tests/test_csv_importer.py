"""Unit tests for reading opportunity CSV content into validated models."""

import pytest

from modules.opportunities.csv_importer import CSVImportError, import_csv
from modules.opportunities.csv_validator import (
    CSVHeaderValidationError,
)


def test_import_csv_reads_utf8_bom_quoted_fields_and_multiple_rows() -> None:
    """Read standard UTF-8 CSV while preserving quoted commas and newlines."""

    content = (
        "\ufeffplatform,title,description,budget_min,posted_at\r\n"
        'Upwork,"API, integration","Build an API\nwith OAuth",500,'
        "2026-07-22T10:30:00+05:30\r\n"
        'Contra,Automation,"Automate reports",,'
        "2026-07-23T08:00:00Z\r\n"
    ).encode()

    result = import_csv(content)
    opportunities = result.opportunities

    assert result.total_rows == 2
    assert result.valid_count == 2
    assert result.rejected_count == 0
    assert len(opportunities) == 2
    assert opportunities[0].platform == "Upwork"
    assert opportunities[0].title == "API, integration"
    assert opportunities[0].description == "Build an API\nwith OAuth"
    assert opportunities[0].budget_min == 500.0
    assert opportunities[1].platform == "Contra"
    assert opportunities[1].budget_min is None
    assert opportunities[1].posted_at is not None
    assert opportunities[1].posted_at.utcoffset() is not None


def test_import_csv_returns_no_opportunities_for_header_only_file() -> None:
    """A valid header with no data rows is a valid empty import."""

    result = import_csv(b"platform,title,description\n")

    assert result.total_rows == 0
    assert result.opportunities == ()
    assert result.errors == ()


def test_import_csv_rejects_missing_header() -> None:
    """Require a header row before attempting row conversion."""

    with pytest.raises(CSVHeaderValidationError, match="header row is required"):
        import_csv(b"")


def test_import_csv_delegates_header_validation() -> None:
    """Reject unsupported headers before reading opportunities."""

    with pytest.raises(CSVHeaderValidationError, match="unsupported CSV columns"):
        import_csv(b"platform,title,description,email\n")


def test_import_csv_returns_an_error_for_an_invalid_row() -> None:
    """Represent invalid data as a row-level result."""

    content = (
        "platform,title,description,budget_min\n"
        "Upwork,Valid job,Build an API,500\n"
        "Contra,Invalid job,Build automation,not-money\n"
    ).encode()

    result = import_csv(content)

    assert result.total_rows == 2
    assert result.valid_count == 1
    assert result.rejected_count == 1
    assert result.errors[0].row_number == 3
    assert result.errors[0].field == "budget_min"


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"\xffplatform,title,description\n", "valid UTF-8"),
        (
            b'platform,title,description\nUpwork,"unterminated,Description\n',
            "malformed CSV",
        ),
    ],
)
def test_import_csv_rejects_invalid_file_content(
    content: bytes, message: str
) -> None:
    """Surface encoding, row-shape, and CSV syntax failures explicitly."""

    with pytest.raises(CSVImportError, match=message):
        import_csv(content)
