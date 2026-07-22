"""Tests for module-owned PostgreSQL repositories."""

from unittest import TestCase
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from core.database.models import Base
from modules.opportunities.repositories import (
    DuplicateOpportunityError,
    PostgreSQLOpportunityRepository,
    RawOpportunityRepository,
)
from modules.opportunities.schemas import RawOpportunity
from modules.proposals.repositories import PostgreSQLProposalRepository
from modules.proposals.schemas import ProposalDraft
from modules.scoring.repositories import PostgreSQLScoreRepository
from modules.scoring.schemas import OpportunityScore


class RepositoryBoundaryTests(TestCase):
    """Keep persistence behavior inside its owning business module."""

    def test_postgresql_adapter_satisfies_opportunity_repository_port(self) -> None:
        repository = PostgreSQLOpportunityRepository(MagicMock(spec=Session))

        self.assertIsInstance(repository, RawOpportunityRepository)

    def test_module_models_share_registered_metadata(self) -> None:
        self.assertEqual(
            set(Base.metadata.tables),
            {
                "application_outcomes",
                "developer_profiles",
                "opportunity_scores",
                "parsed_opportunities",
                "proposal_drafts",
                "raw_opportunities",
            },
        )

    def test_opportunity_repository_maps_validated_schema_to_record(self) -> None:
        session = MagicMock(spec=Session)
        session.scalar.return_value = None
        repository = PostgreSQLOpportunityRepository(session)

        record = repository.add_raw_opportunity(
            fingerprint="a" * 64,
            opportunity=RawOpportunity(
                platform="Upwork",
                title="Build an API",
                description="Implement a validated FastAPI service.",
            ),
        )

        self.assertEqual(record.title, "Build an API")
        self.assertEqual(record.fingerprint, "a" * 64)
        session.add.assert_called_once_with(record)
        session.flush.assert_called_once_with()

    def test_opportunity_repository_rejects_existing_fingerprint(self) -> None:
        session = MagicMock(spec=Session)
        session.scalar.return_value = object()
        repository = PostgreSQLOpportunityRepository(session)

        with self.assertRaises(DuplicateOpportunityError):
            repository.add_raw_opportunity(
                fingerprint="a" * 64,
                opportunity=RawOpportunity(
                    platform="Upwork",
                    title="Build an API",
                    description="Implement a validated FastAPI service.",
                ),
            )

        session.add.assert_not_called()

    def test_score_and_proposal_repositories_preserve_safety_fields(self) -> None:
        session = MagicMock(spec=Session)
        score_record = PostgreSQLScoreRepository(session).add_opportunity_score(
            raw_opportunity_id="opportunity-id",
            score=OpportunityScore(
                total=80,
                skill_match=20,
                budget_quality=12,
                requirement_clarity=8,
                client_quality=12,
                portfolio_relevance=13,
                repeat_work_potential=7,
                competition=8,
                penalties=0,
                explanation=["Strong fit."],
            ),
        )
        proposal_record = PostgreSQLProposalRepository(session).add_proposal_draft(
            raw_opportunity_id="opportunity-id",
            draft=ProposalDraft(
                client_problem_summary="The client needs an API.",
                proposed_solution="Build a validated FastAPI service.",
                relevant_evidence=["Existing API project"],
                questions=["Which clients consume the API?"],
                proposal_text="I can build the reviewed API draft.",
            ),
        )

        self.assertEqual(score_record.total, 80)
        self.assertTrue(proposal_record.requires_human_approval)
        self.assertEqual(session.add.call_count, 2)
        self.assertEqual(session.flush.call_count, 2)
