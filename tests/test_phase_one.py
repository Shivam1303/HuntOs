"""Tests for Phase 1 data models and PostgreSQL migration contracts."""

from datetime import UTC, datetime
from unittest import TestCase
from uuid import uuid4

from pydantic import ValidationError

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
