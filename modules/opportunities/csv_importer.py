"""Read UTF-8 CSV content into validated raw opportunity models."""

import csv
from collections.abc import Mapping
from io import StringIO

from modules.opportunities.csv_validator import (
    CSVHeaderValidationError,
    CSVRowValidationError,
    validate_csv_headers,
    validate_csv_row,
)
from modules.opportunities.duplicate_detection import opportunity_fingerprint
from modules.opportunities.repositories import (
    DuplicateOpportunityError,
    RawOpportunityRepository,
)
from modules.opportunities.schemas import (
    CSVDuplicateRow,
    CSVImportResult,
    CSVRowError,
    RawOpportunity,
)


class CSVImportError(ValueError):
    """CSV content cannot be decoded or parsed safely."""


class CSVImporter:
    """Validate and persist CSV opportunities through an injected repository."""

    def __init__(self, repository: RawOpportunityRepository) -> None:
        self._repository = repository

    def import_csv(self, content: bytes) -> CSVImportResult:
        """Store unique valid rows and report duplicate rows."""

        result = import_csv(content)
        stored_ids: list[str] = []
        duplicates: list[CSVDuplicateRow] = []
        seen_fingerprints: set[str] = set()
        rows = zip(
            result.opportunity_row_numbers,
            result.opportunities,
            strict=True,
        )
        for row_number, opportunity in rows:
            fingerprint = opportunity_fingerprint(opportunity)
            if fingerprint in seen_fingerprints:
                duplicates.append(
                    CSVDuplicateRow(
                        row_number=row_number,
                        reason="duplicate within this CSV upload",
                    )
                )
                continue
            seen_fingerprints.add(fingerprint)

            if self._repository.is_duplicate(fingerprint):
                duplicates.append(
                    CSVDuplicateRow(
                        row_number=row_number,
                        reason="opportunity already exists",
                    )
                )
                continue

            try:
                record = self._repository.add_raw_opportunity(
                    fingerprint=fingerprint,
                    opportunity=opportunity,
                )
            except DuplicateOpportunityError:
                duplicates.append(
                    CSVDuplicateRow(
                        row_number=row_number,
                        reason="opportunity became duplicate during storage",
                    )
                )
                continue
            stored_ids.append(record.id)

        return CSVImportResult(
            total_rows=result.total_rows,
            opportunities=result.opportunities,
            opportunity_row_numbers=result.opportunity_row_numbers,
            errors=result.errors,
            duplicates=tuple(duplicates),
            stored_opportunity_ids=tuple(stored_ids),
        )


def import_csv(content: bytes) -> CSVImportResult:
    """Parse UTF-8 CSV bytes, retaining valid rows and row-level errors."""

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise CSVImportError("CSV content must be valid UTF-8") from error

    reader = csv.DictReader(StringIO(text, newline=""), strict=True)
    try:
        headers = reader.fieldnames
        if headers is None:
            raise CSVHeaderValidationError("CSV header row is required")
        validate_csv_headers(headers)

        opportunities: list[RawOpportunity] = []
        opportunity_row_numbers: list[int] = []
        errors: list[CSVRowError] = []
        total_rows = 0
        for row_number, row in enumerate(reader, start=2):
            total_rows += 1
            try:
                opportunities.append(validate_csv_row(_normalize_row(row)))
                opportunity_row_numbers.append(row_number)
            except CSVRowValidationError as error:
                errors.append(
                    CSVRowError(
                        row_number=row_number,
                        field=error.field,
                        message=error.message,
                    )
                )
    except csv.Error as error:
        raise CSVImportError(f"malformed CSV: {error}") from error

    return CSVImportResult(
        total_rows=total_rows,
        opportunities=tuple(opportunities),
        opportunity_row_numbers=tuple(opportunity_row_numbers),
        errors=tuple(errors),
    )


def _normalize_row(
    row: Mapping[str | None, str | list[str] | None],
) -> dict[str, str | None]:
    extra_values = row.get(None)
    if extra_values:
        raise CSVRowValidationError(
            field=None, message="CSV row contains more values than headers"
        )

    normalized: dict[str, str | None] = {}
    for column, value in row.items():
        if column is None:
            continue
        if isinstance(value, list):
            raise CSVRowValidationError(
            field=None, message="CSV row contains more values than headers"
        )
        normalized[column] = value
    return normalized
