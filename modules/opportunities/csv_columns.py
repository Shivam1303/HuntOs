"""Canonical column names accepted by opportunity CSV imports."""

from typing import Final

REQUIRED_CSV_COLUMNS: Final[tuple[str, ...]] = (
    "platform",
    "title",
    "description",
)

OPTIONAL_CSV_COLUMNS: Final[tuple[str, ...]] = (
    "source_id",
    "budget_min",
    "budget_max",
    "client_name",
    "client_history",
    "proposal_count",
    "posted_at",
    "url",
)       

SUPPORTED_CSV_COLUMNS: Final[tuple[str, ...]] = (
    REQUIRED_CSV_COLUMNS + OPTIONAL_CSV_COLUMNS
)
