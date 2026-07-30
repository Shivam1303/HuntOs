"""Pydantic schemas for freelance opportunities and manual outcomes."""

from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    model_validator,
)

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class OpportunitySchema(BaseModel):
    """Shared input constraints for the opportunities domain."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DeveloperProfile(OpportunitySchema):
    """Evidence the system may use when evaluating and drafting work."""

    name: NonEmptyText
    headline: NonEmptyText
    skills: list[NonEmptyText]
    preferred_project_types: list[NonEmptyText]
    preferred_industries: list[NonEmptyText]
    minimum_budget: float | None = Field(default=None, ge=0)
    hourly_rate: float | None = Field(default=None, ge=0)
    portfolio_items: list[NonEmptyText]
    prohibited_claims: list[NonEmptyText] = Field(default_factory=list)


class RawOpportunity(OpportunitySchema):
    """An opportunity exactly as supplied by an import source."""

    source_id: NonEmptyText | None = None
    platform: NonEmptyText
    title: NonEmptyText
    description: NonEmptyText
    budget_min: float | None = Field(default=None, ge=0)
    budget_max: float | None = Field(default=None, ge=0)
    client_name: NonEmptyText | None = None
    client_history: NonEmptyText | None = None
    proposal_count: int | None = Field(default=None, ge=0)
    posted_at: datetime | None = None
    url: NonEmptyText | None = None

    @model_validator(mode="after")
    def validate_budget_range(self) -> Self:
        """Reject an upper budget that is lower than its lower budget."""

        if (
            self.budget_min is not None
            and self.budget_max is not None
            and self.budget_min > self.budget_max
        ):
            raise ValueError("budget_max must be greater than or equal to budget_min")
        return self


class CSVRowError(OpportunitySchema):
    """A validation failure tied to one logical CSV data row."""

    row_number: int = Field(ge=2)
    field: NonEmptyText | None = None
    message: NonEmptyText


class CSVDuplicateRow(OpportunitySchema):
    """A valid CSV row skipped because its opportunity already exists."""

    row_number: int = Field(ge=2)
    reason: NonEmptyText


class CSVImportResult(OpportunitySchema):
    """Validated rows and visible failures from one CSV import attempt."""

    total_rows: int = Field(ge=0)
    opportunities: tuple[RawOpportunity, ...]
    opportunity_row_numbers: tuple[int, ...] = Field(exclude=True)
    errors: tuple[CSVRowError, ...]
    duplicates: tuple[CSVDuplicateRow, ...] = ()
    stored_opportunity_ids: tuple[NonEmptyText, ...] = ()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def valid_count(self) -> int:
        """Return the number of rows that produced valid opportunities."""

        return len(self.opportunities)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def rejected_count(self) -> int:
        """Return the number of rows rejected by validation."""

        return len(self.errors)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stored_count(self) -> int:
        """Return the number of valid opportunities persisted successfully."""

        return len(self.stored_opportunity_ids)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def skipped_count(self) -> int:
        """Return the number of valid rows skipped as duplicates."""

        return len(self.duplicates)


class ParsedOpportunity(OpportunitySchema):
    """Structured LLM interpretation retained separately from raw input."""

    required_skills: list[NonEmptyText]
    business_problem: NonEmptyText
    expected_deliverables: list[NonEmptyText]
    experience_level: NonEmptyText | None = None
    warning_signs: list[NonEmptyText]
    missing_information: list[NonEmptyText]
    clarification_questions: list[NonEmptyText]


class ApplicationOutcomeStatus(str, Enum):
    """Manual application outcomes; none trigger an outbound action."""

    APPLIED = "applied"
    WON = "won"
    LOST = "lost"
    WITHDRAWN = "withdrawn"


class ApplicationOutcome(OpportunitySchema):
    """A manually recorded result for one opportunity."""

    opportunity_id: UUID
    status: ApplicationOutcomeStatus
    notes: str | None = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
