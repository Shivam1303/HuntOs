"""Tests for structured row-level CSV validation results."""

from modules.opportunities.csv_importer import import_csv
from modules.opportunities.schemas import CSVImportResult


def test_import_csv_collects_errors_and_continues_after_invalid_rows() -> None:
    """Keep valid rows while reporting every invalid row in file order."""

    content = (
        "platform,title,description,budget_min,proposal_count\n"
        "Upwork,First valid job,Build an API,500,5\n"
        "Contra, ,Invalid missing title,750,3\n"
        "Upwork,Invalid count,Build automation,1000,2.5\n"
        "Contra,Second valid job,Integrate a CRM,1200,8\n"
    ).encode()

    result = import_csv(content)

    assert isinstance(result, CSVImportResult)
    assert result.total_rows == 4
    assert result.valid_count == 2
    assert result.rejected_count == 2
    assert [item.title for item in result.opportunities] == [
        "First valid job",
        "Second valid job",
    ]
    assert [(error.row_number, error.field) for error in result.errors] == [
        (3, "title"),
        (4, "proposal_count"),
    ]
    assert all(error.message for error in result.errors)


def test_import_csv_reports_extra_cells_as_a_row_error() -> None:
    """Treat a row-shape problem as local so later rows can still validate."""

    content = (
        "platform,title,description\n"
        "Upwork,Invalid job,Description,unexpected\n"
        "Contra,Valid job,Build automation\n"
    ).encode()

    result = import_csv(content)

    assert result.total_rows == 2
    assert result.valid_count == 1
    assert result.rejected_count == 1
    assert result.opportunities[0].title == "Valid job"
    assert result.errors[0].row_number == 2
    assert result.errors[0].field is None
    assert "more values than headers" in result.errors[0].message


def test_import_csv_result_serializes_counts_and_errors() -> None:
    """Expose stable response data for a later API or frontend adapter."""

    result = import_csv(
        b"platform,title,description\nUpwork, ,Missing title\n"
    )

    payload = result.model_dump()

    assert payload["total_rows"] == 1
    assert payload["valid_count"] == 0
    assert payload["rejected_count"] == 1
    assert payload["errors"][0]["row_number"] == 2
    assert payload["errors"][0]["field"] == "title"
