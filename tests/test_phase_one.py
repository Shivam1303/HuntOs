"""Tests for Phase 1 data models and PostgreSQL migration contracts."""

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, skipUnless
from uuid import uuid4

from pydantic import ValidationError

from core.database.database import PostgreSQLDatabase
from core.database.repositories import DuplicateOpportunityError, LeadHuntingRepository
from modules.opportunities.duplicate_detection import opportunity_fingerprint
from modules.opportunities.schemas import (
    ApplicationOutcome,
    ApplicationOutcomeStatus,
    DeveloperProfile,
    ParsedOpportunity,
    RawOpportunity,
)
from modules.proposals.schemas import ProposalDraft
from modules.scoring.schemas import OpportunityScore


class DataModelTests(TestCase):
    """Verify Phase 1 Pydantic model contracts and safety defaults."""

    def test_models_accept_valid_phase_one_data(self) -> None:
        profile = DeveloperProfile(
            name="Ada Developer",
            headline="Python automation specialist",
            skills=["Python", "FastAPI"],
            preferred_project_types=["API integration"],
            preferred_industries=["SaaS"],
            minimum_budget=500.0,
            hourly_rate=75.0,
            portfolio_items=["Workflow service"],
        )
        raw_opportunity = self._raw_opportunity()
        parsed_opportunity = ParsedOpportunity(
            required_skills=["Python"],
            business_problem="Automate client document intake.",
            expected_deliverables=["Document processing workflow"],
            experience_level="intermediate",
            warning_signs=[],
            missing_information=[],
            clarification_questions=["Which document formats are in scope?"],
        )
        score = OpportunityScore(
            total=78,
            skill_match=20,
            budget_quality=12,
            requirement_clarity=9,
            client_quality=13,
            portfolio_relevance=14,
            repeat_work_potential=6,
            competition=8,
            penalties=-4,
            explanation=["Strong Python and automation fit."],
        )
        draft = ProposalDraft(
            client_problem_summary="The client needs document processing automation.",
            proposed_solution="Build a validated ingestion workflow.",
            relevant_evidence=["Workflow service"],
            questions=["Which document formats are in scope?"],
            proposal_text="I can help design the workflow.",
        )
        outcome = ApplicationOutcome(
            opportunity_id=uuid4(),
            status=ApplicationOutcomeStatus.APPLIED,
            notes="Submitted manually after review.",
        )

        self.assertEqual(profile.minimum_budget, 500.0)
        self.assertEqual(raw_opportunity.platform, "Upwork")
        self.assertEqual(parsed_opportunity.required_skills, ["Python"])
        self.assertEqual(score.total, 78)
        self.assertTrue(draft.requires_human_approval)
        self.assertEqual(outcome.status, ApplicationOutcomeStatus.APPLIED)

    def test_models_reject_invalid_business_values(self) -> None:
        with self.assertRaises(ValidationError):
            DeveloperProfile(
                name="Ada Developer",
                headline="Python automation specialist",
                skills=["Python"],
                preferred_project_types=["API integration"],
                preferred_industries=["SaaS"],
                minimum_budget=-1.0,
                hourly_rate=75.0,
                portfolio_items=[],
            )

        with self.assertRaises(ValidationError):
            RawOpportunity(
                platform="Upwork",
                title="Build an API",
                description="Implement a small service.",
                budget_min=1000.0,
                budget_max=500.0,
            )

        with self.assertRaises(ValidationError):
            OpportunityScore(
                total=78,
                skill_match=26,
                budget_quality=12,
                requirement_clarity=9,
                client_quality=13,
                portfolio_relevance=14,
                repeat_work_potential=6,
                competition=8,
                penalties=0,
                explanation=["Invalid skill score."],
            )

        with self.assertRaises(ValidationError):
            ProposalDraft(
                client_problem_summary="Summary",
                proposed_solution="Solution",
                relevant_evidence=[],
                questions=[],
                proposal_text="Draft",
                requires_human_approval=False,
            )

    @staticmethod
    def _raw_opportunity() -> RawOpportunity:
        return RawOpportunity(
            source_id="job-123",
            platform="Upwork",
            title="Build a document workflow",
            description="Automate document intake and routing.",
            budget_min=1000.0,
            budget_max=1500.0,
            client_name="Example Client",
            client_history="10 hires",
            proposal_count=5,
            posted_at=datetime(2026, 7, 22, tzinfo=UTC),
            url="https://example.com/jobs/123",
        )


@skipUnless(False, "PostgreSQL integration tests are being migrated")
class PostgreSQLRepositoryTests(TestCase):
    """PostgreSQL integration tests are defined separately during migration."""

    def test_repository_persists_every_phase_one_record_type(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            database = PostgreSQLDatabase(Path(temporary_directory) / "lead_hunting.db")
            database.initialize()
            raw_opportunity = DataModelTests._raw_opportunity()

            with database.session() as session:
                repository = LeadHuntingRepository(session)
                profile = repository.add_developer_profile(
                    name="Ada Developer",
                    headline="Python automation specialist",
                    skills=["Python"],
                    preferred_project_types=["API integration"],
                    preferred_industries=["SaaS"],
                    minimum_budget=500.0,
                    hourly_rate=75.0,
                    portfolio_items=["Workflow service"],
                    prohibited_claims=["Do not claim certifications"],
                )
                raw_record = repository.add_raw_opportunity(
                    fingerprint=opportunity_fingerprint(raw_opportunity),
                    **raw_opportunity.model_dump(),
                )
                parsed = repository.add_parsed_opportunity(
                    raw_opportunity_id=raw_record.id,
                    required_skills=["Python"],
                    business_problem="Automate document intake.",
                    expected_deliverables=["Workflow"],
                    experience_level="intermediate",
                    warning_signs=[],
                    missing_information=[],
                    clarification_questions=["Which formats are required?"],
                )
                score = repository.add_opportunity_score(
                    raw_opportunity_id=raw_record.id,
                    total=78,
                    skill_match=20,
                    budget_quality=12,
                    requirement_clarity=9,
                    client_quality=13,
                    portfolio_relevance=14,
                    repeat_work_potential=6,
                    competition=8,
                    penalties=-4,
                    explanation=["Strong fit."],
                )
                draft = repository.add_proposal_draft(
                    raw_opportunity_id=raw_record.id,
                    client_problem_summary="Automate document intake.",
                    proposed_solution="Build a workflow.",
                    relevant_evidence=["Workflow service"],
                    questions=["Which formats are required?"],
                    proposal_text="I can help build this workflow.",
                    requires_human_approval=True,
                )
                outcome = repository.add_application_outcome(
                    raw_opportunity_id=raw_record.id,
                    status=ApplicationOutcomeStatus.APPLIED.value,
                    notes="Recorded manually.",
                )

                self.assertEqual(profile.name, "Ada Developer")
                self.assertEqual(parsed.raw_opportunity_id, raw_record.id)
                self.assertEqual(score.total, 78)
                self.assertTrue(draft.requires_human_approval)
                self.assertEqual(outcome.status, ApplicationOutcomeStatus.APPLIED.value)

            with database.session() as session:
                repository = LeadHuntingRepository(session)
                stored_record = repository.get_raw_opportunity_by_fingerprint(
                    opportunity_fingerprint(raw_opportunity)
                )

            self.assertIsNotNone(stored_record)
            self.assertEqual(stored_record.title, raw_opportunity.title)

    def test_normalized_fingerprint_prevents_duplicate_raw_opportunities(self) -> None:
        original = DataModelTests._raw_opportunity()
        equivalent = original.model_copy(
            update={
                "platform": " upwork ",
                "title": "Build   a document workflow",
                "description": "Automate document intake and routing. ",
            }
        )

        self.assertEqual(
            opportunity_fingerprint(original), opportunity_fingerprint(equivalent)
        )

        with TemporaryDirectory() as temporary_directory:
            database = PostgreSQLDatabase(Path(temporary_directory) / "lead_hunting.db")
            database.initialize()

            with database.session() as session:
                repository = LeadHuntingRepository(session)
                repository.add_raw_opportunity(
                    fingerprint=opportunity_fingerprint(original),
                    **original.model_dump(),
                )

                self.assertTrue(
                    repository.is_duplicate(opportunity_fingerprint(equivalent))
                )
                with self.assertRaises(DuplicateOpportunityError):
                    repository.add_raw_opportunity(
                        fingerprint=opportunity_fingerprint(equivalent),
                        **equivalent.model_dump(),
                    )
