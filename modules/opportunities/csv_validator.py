"""Validation and conversion for opportunity CSV headers and individual rows."""

from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal, InvalidOperation
from math import isfinite

from pydantic import ValidationError

from modules.opportunities.csv_columns import (
    OPTIONAL_CSV_COLUMNS,
    REQUIRED_CSV_COLUMNS,
    SUPPORTED_CSV_COLUMNS,
)
from modules.opportunities.schemas import RawOpportunity


class CSVHeaderValidationError(ValueError):
    """A CSV header row does not satisfy the supported-column contract."""


class CSVRowValidationError(ValueError):
    """A single CSV row cannot be converted into a raw opportunity."""

    def __init__(self, *, field: str | None, message: str) -> None:
        self.field = field
        self.message = message
        prefix = f"{field}: " if field is not None else ""
        super().__init__(f"{prefix}{message}")


def validate_csv_headers(headers: Sequence[str]) -> None:
    """Reject missing, unknown, or duplicate CSV column names."""

    counts = Counter(headers)
    duplicates = sorted(header for header, count in counts.items() if count > 1)
    if duplicates:
        raise CSVHeaderValidationError(
            f"duplicate CSV columns: {', '.join(duplicates)}"
        )

    supported = set(SUPPORTED_CSV_COLUMNS)
    unknown = sorted(set(headers) - supported)
    if unknown:
        raise CSVHeaderValidationError(
            f"unsupported CSV columns: {', '.join(unknown)}"
        )

    missing = sorted(set(REQUIRED_CSV_COLUMNS) - set(headers))
    if missing:
        raise CSVHeaderValidationError(
            f"missing required CSV columns: {', '.join(missing)}"
        )


def validate_csv_row(row: Mapping[str, str | None]) -> RawOpportunity:
    """Convert one CSV string row into a validated raw opportunity."""

    validate_csv_headers(tuple(row))
    values: dict[str, object | None] = {
        column: row[column] for column in REQUIRED_CSV_COLUMNS
    }

    for column in OPTIONAL_CSV_COLUMNS:
        if column in row:
            values[column] = _optional_text(row[column])

    values["budget_min"] = _optional_number(row.get("budget_min"), "budget_min")
    values["budget_max"] = _optional_number(row.get("budget_max"), "budget_max")
    values["proposal_count"] = _optional_integer(
        row.get("proposal_count"), "proposal_count"
    )
    values["posted_at"] = _optional_datetime(row.get("posted_at"), "posted_at")

    try:
        return RawOpportunity.model_validate(values)
    except ValidationError as error:
        first_error = error.errors()[0]
        location = first_error["loc"]
        field = str(location[0]) if location else _model_error_field(first_error["msg"])
        raise CSVRowValidationError(
            field=field,
            message=first_error["msg"],
        ) from error


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _optional_number(value: str | None, field: str) -> float | None:
    normalized = _optional_text(value)
    if normalized is None:
        return None
    try:
        decimal_value = Decimal(normalized)
    except InvalidOperation as error:
        raise CSVRowValidationError(field=field, message="must be a number") from error

    number = float(decimal_value)
    if not decimal_value.is_finite() or not isfinite(number):
        raise CSVRowValidationError(field=field, message="must be a finite number")
    return number


def _optional_integer(value: str | None, field: str) -> int | None:
    normalized = _optional_text(value)
    if normalized is None:
        return None
    try:
        return int(normalized)
    except ValueError as error:
        raise CSVRowValidationError(
            field=field, message="must be a whole number"
        ) from error


def _optional_datetime(value: str | None, field: str) -> datetime | None:
    normalized = _optional_text(value)
    if normalized is None:
        return None
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise CSVRowValidationError(
            field=field, message="must be an ISO 8601 timestamp"
        ) from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CSVRowValidationError(
            field=field, message="must include a timezone offset"
        )
    return parsed


def _model_error_field(message: str) -> str | None:
    if "budget_max" in message:
        return "budget_max"
    return None
