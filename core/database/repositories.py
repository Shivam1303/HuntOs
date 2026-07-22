"""Core persistence repository using primitive types, not business schemas."""

from datetime import datetime
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.database.models import (
    ApplicationOutcomeRecord,
    Base,
    DeveloperProfileRecord,
    OpportunityScoreRecord,
    ParsedOpportunityRecord,
    ProposalDraftRecord,
    RawOpportunityRecord,
)

RecordType = TypeVar("RecordType", bound=Base)


class DuplicateOpportunityError(ValueError):
    """Raised when an opportunity fingerprint is already persisted."""


class LeadHuntingRepository:
    """Persist Lead Hunting MVP records without importing business modules."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_developer_profile(
        self,
        *,
        name: str,
        headline: str,
        skills: list[str],
        preferred_project_types: list[str],
        preferred_industries: list[str],
        minimum_budget: float | None,
        hourly_rate: float | None,
        portfolio_items: list[str],
        prohibited_claims: list[str],
    ) -> DeveloperProfileRecord:
        """Store profile evidence used by later business modules."""

        record = DeveloperProfileRecord(
            name=name,
            headline=headline,
            skills=skills,
            preferred_project_types=preferred_project_types,
            preferred_industries=preferred_industries,
            minimum_budget=minimum_budget,
            hourly_rate=hourly_rate,
            portfolio_items=portfolio_items,
            prohibited_claims=prohibited_claims,
        )
        return self._add_and_flush(record)

    def add_raw_opportunity(
        self,
        *,
        fingerprint: str,
        source_id: str | None,
        platform: str,
        title: str,
        description: str,
        budget_min: float | None,
        budget_max: float | None,
        client_name: str | None,
        client_history: str | None,
        proposal_count: int | None,
        posted_at: datetime | None,
        url: str | None,
    ) -> RawOpportunityRecord:
        """Store a raw opportunity unless its deterministic identity already exists."""

        if self.is_duplicate(fingerprint):
            raise DuplicateOpportunityError(
                "An opportunity with this fingerprint already exists"
            )

        record = RawOpportunityRecord(
            fingerprint=fingerprint,
            source_id=source_id,
            platform=platform,
            title=title,
            description=description,
            budget_min=budget_min,
            budget_max=budget_max,
            client_name=client_name,
            client_history=client_history,
            proposal_count=proposal_count,
            posted_at=posted_at,
            url=url,
        )
        return self._add_and_flush(record)

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
        required_skills: list[str],
        business_problem: str,
        expected_deliverables: list[str],
        experience_level: str | None,
        warning_signs: list[str],
        missing_information: list[str],
        clarification_questions: list[str],
    ) -> ParsedOpportunityRecord:
        """Store parsed data separately from the immutable raw opportunity."""

        record = ParsedOpportunityRecord(
            raw_opportunity_id=raw_opportunity_id,
            required_skills=required_skills,
            business_problem=business_problem,
            expected_deliverables=expected_deliverables,
            experience_level=experience_level,
            warning_signs=warning_signs,
            missing_information=missing_information,
            clarification_questions=clarification_questions,
        )
        return self._add_and_flush(record)

    def add_opportunity_score(
        self,
        *,
        raw_opportunity_id: str,
        total: int,
        skill_match: int,
        budget_quality: int,
        requirement_clarity: int,
        client_quality: int,
        portfolio_relevance: int,
        repeat_work_potential: int,
        competition: int,
        penalties: int,
        explanation: list[str],
    ) -> OpportunityScoreRecord:
        """Store a score calculated by deterministic code in a later phase."""

        record = OpportunityScoreRecord(
            raw_opportunity_id=raw_opportunity_id,
            total=total,
            skill_match=skill_match,
            budget_quality=budget_quality,
            requirement_clarity=requirement_clarity,
            client_quality=client_quality,
            portfolio_relevance=portfolio_relevance,
            repeat_work_potential=repeat_work_potential,
            competition=competition,
            penalties=penalties,
            explanation=explanation,
        )
        return self._add_and_flush(record)

    def add_proposal_draft(
        self,
        *,
        raw_opportunity_id: str,
        client_problem_summary: str,
        proposed_solution: str,
        relevant_evidence: list[str],
        questions: list[str],
        proposal_text: str,
        requires_human_approval: bool,
    ) -> ProposalDraftRecord:
        """Store a draft while retaining its required human-approval flag."""

        record = ProposalDraftRecord(
            raw_opportunity_id=raw_opportunity_id,
            client_problem_summary=client_problem_summary,
            proposed_solution=proposed_solution,
            relevant_evidence=relevant_evidence,
            questions=questions,
            proposal_text=proposal_text,
            requires_human_approval=requires_human_approval,
        )
        return self._add_and_flush(record)

    def add_application_outcome(
        self,
        *,
        raw_opportunity_id: str,
        status: str,
        notes: str | None,
    ) -> ApplicationOutcomeRecord:
        """Store a manually recorded outcome without any outbound behavior."""

        record = ApplicationOutcomeRecord(
            raw_opportunity_id=raw_opportunity_id,
            status=status,
            notes=notes,
        )
        return self._add_and_flush(record)

    def _add_and_flush(self, record: RecordType) -> RecordType:
        """Add one ORM record and assign its database-generated values."""

        self._session.add(record)
        self._session.flush()
        return record
