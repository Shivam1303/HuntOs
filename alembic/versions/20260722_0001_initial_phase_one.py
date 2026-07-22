"""Initial PostgreSQL schema for completed Phase 1."""

import sqlalchemy as sa

from alembic import op

revision = "20260722_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "developer_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("headline", sa.String(500), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("preferred_project_types", sa.JSON(), nullable=False),
        sa.Column("preferred_industries", sa.JSON(), nullable=False),
        sa.Column("minimum_budget", sa.Numeric(12, 2)),
        sa.Column("hourly_rate", sa.Numeric(12, 2)),
        sa.Column("portfolio_items", sa.JSON(), nullable=False),
        sa.Column("prohibited_claims", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "raw_opportunities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_id", sa.String(255)),
        sa.Column("platform", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("budget_min", sa.Numeric(12, 2)),
        sa.Column("budget_max", sa.Numeric(12, 2)),
        sa.Column("client_name", sa.String(255)),
        sa.Column("client_history", sa.Text()),
        sa.Column("proposal_count", sa.Integer()),
        sa.Column("posted_at", sa.DateTime(timezone=True)),
        sa.Column("url", sa.Text()),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_raw_opportunities_fingerprint",
        "raw_opportunities",
        ["fingerprint"],
        unique=True,
    )
    for name, columns in (
        (
            "parsed_opportunities",
            [
                "required_skills",
                "expected_deliverables",
                "warning_signs",
                "missing_information",
                "clarification_questions",
            ],
        ),
        ("opportunity_scores", ["explanation"]),
        ("proposal_drafts", ["relevant_evidence", "questions"]),
    ):
        op.create_table(
            name,
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "raw_opportunity_id",
                sa.String(36),
                sa.ForeignKey("raw_opportunities.id"),
                nullable=False,
                unique=True,
            ),
            *[sa.Column(column, sa.JSON(), nullable=False) for column in columns],
        )
    op.create_table(
        "application_outcomes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "raw_opportunity_id",
            sa.String(36),
            sa.ForeignKey("raw_opportunities.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.add_column(
        "parsed_opportunities", sa.Column("business_problem", sa.Text(), nullable=False)
    )
    op.add_column("parsed_opportunities", sa.Column("experience_level", sa.String(100)))
    op.add_column(
        "parsed_opportunities",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in (
        "total",
        "skill_match",
        "budget_quality",
        "requirement_clarity",
        "client_quality",
        "portfolio_relevance",
        "repeat_work_potential",
        "competition",
        "penalties",
    ):
        op.add_column(
            "opportunity_scores", sa.Column(column, sa.Integer(), nullable=False)
        )
    op.add_column(
        "opportunity_scores",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.add_column(
        "proposal_drafts",
        sa.Column("client_problem_summary", sa.Text(), nullable=False),
    )
    op.add_column(
        "proposal_drafts", sa.Column("proposed_solution", sa.Text(), nullable=False)
    )
    op.add_column(
        "proposal_drafts", sa.Column("proposal_text", sa.Text(), nullable=False)
    )
    op.add_column(
        "proposal_drafts",
        sa.Column("requires_human_approval", sa.Boolean(), nullable=False),
    )
    op.add_column(
        "proposal_drafts",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("application_outcomes")
    for name in ("proposal_drafts", "opportunity_scores", "parsed_opportunities"):
        op.drop_table(name)
    op.drop_index("ix_raw_opportunities_fingerprint", table_name="raw_opportunities")
    op.drop_table("raw_opportunities")
    op.drop_table("developer_profiles")
