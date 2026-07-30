"""Persistence ports and PostgreSQL adapter for opportunities."""

from typing import Protocol, runtime_checkable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from modules.opportunities.models import (
    ApplicationOutcomeRecord,
    DeveloperProfileRecord,
    ParsedOpportunityRecord,
    RawOpportunityRecord,
)
from modules.opportunities.schemas import (
    ApplicationOutcome,
    DeveloperProfile,
    ParsedOpportunity,
    RawOpportunity,
)


class DuplicateOpportunityError(ValueError):
    """Raised when an opportunity fingerprint is already persisted."""


@runtime_checkable
class RawOpportunityRepository(Protocol):
    """Persistence operations required by opportunity import use cases."""

    def add_raw_opportunity(
        self,
        *,
        fingerprint: str,
        opportunity: RawOpportunity,
    ) -> RawOpportunityRecord:
        """Store one validated raw opportunity."""

    def get_raw_opportunity_by_fingerprint(
        self, fingerprint: str
    ) -> RawOpportunityRecord | None:
        """Return the opportunity identified by a fingerprint, if stored."""

    def is_duplicate(self, fingerprint: str) -> bool:
        """Return whether an opportunity fingerprint is already stored."""


class PostgreSQLOpportunityRepository:
    """Persist records owned by the opportunities module."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_developer_profile(
        self, profile: DeveloperProfile
    ) -> DeveloperProfileRecord:
        """Store evidence used by later scoring and proposal workflows."""

        record = DeveloperProfileRecord(**profile.model_dump())
        self._session.add(record)
        self._session.flush()
        return record

    def add_raw_opportunity(
        self,
        *,
        fingerprint: str,
        opportunity: RawOpportunity,
    ) -> RawOpportunityRecord:
        """Store one opportunity unless its deterministic identity exists."""

        if self.is_duplicate(fingerprint):
            raise DuplicateOpportunityError(
                "An opportunity with this fingerprint already exists"
            )

        record = RawOpportunityRecord(
            fingerprint=fingerprint,
            **opportunity.model_dump(),
        )
        try:
            with self._session.begin_nested():
                self._session.add(record)
                self._session.flush()
        except IntegrityError as error:
            if getattr(error.orig, "sqlstate", None) == "23505":
                raise DuplicateOpportunityError(
                    "An opportunity with this fingerprint already exists"
                ) from error
            raise
        return record

    def get_raw_opportunity_by_fingerprint(
        self, fingerprint: str
    ) -> RawOpportunityRecord | None:
        """Return the stored raw opportunity for an identity fingerprint."""

        statement = select(RawOpportunityRecord).where(
            RawOpportunityRecord.fingerprint == fingerprint
        )
        return self._session.scalar(statement)

    def is_duplicate(self, fingerprint: str) -> bool:
        """Return whether a raw opportunity identity is already stored."""

        return self.get_raw_opportunity_by_fingerprint(fingerprint) is not None

    def add_parsed_opportunity(
        self,
        *,
        raw_opportunity_id: str,
        opportunity: ParsedOpportunity,
    ) -> ParsedOpportunityRecord:
        """Store parsed data separately from the immutable raw opportunity."""

        record = ParsedOpportunityRecord(
            raw_opportunity_id=raw_opportunity_id,
            **opportunity.model_dump(),
        )
        self._session.add(record)
        self._session.flush()
        return record

    def add_application_outcome(
        self, outcome: ApplicationOutcome
    ) -> ApplicationOutcomeRecord:
        """Store a manually recorded outcome without outbound behavior."""

        record = ApplicationOutcomeRecord(
            raw_opportunity_id=str(outcome.opportunity_id),
            status=outcome.status.value,
            notes=outcome.notes,
            recorded_at=outcome.recorded_at,
        )
        self._session.add(record)
        self._session.flush()
        return record
