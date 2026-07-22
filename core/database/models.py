"""SQLAlchemy ORM records owned by the core database layer."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def new_identifier() -> str:
    """Create a portable string primary key for PostgreSQL records."""

    return str(uuid4())


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for record defaults."""

    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Base class for core-owned database records."""


class DeveloperProfileRecord(Base):
    """Persistence representation of developer profile evidence."""

    __tablename__ = "developer_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_identifier
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    skills: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    preferred_project_types: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    preferred_industries: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    minimum_budget: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    hourly_rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    portfolio_items: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    prohibited_claims: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class RawOpportunityRecord(Base):
    """Persistence representation of an imported opportunity and its identity."""

    __tablename__ = "raw_opportunities"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_identifier
    )
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    budget_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    budget_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposal_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    fingerprint: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class ParsedOpportunityRecord(Base):
    """Persistence representation of structured parsed opportunity data."""

    __tablename__ = "parsed_opportunities"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_identifier
    )
    raw_opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("raw_opportunities.id"), unique=True, nullable=False
    )
    required_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    business_problem: Mapped[str] = mapped_column(Text, nullable=False)
    expected_deliverables: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    experience_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    warning_signs: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    missing_information: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    clarification_questions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class OpportunityScoreRecord(Base):
    """Persistence representation of an explainable deterministic score."""

    __tablename__ = "opportunity_scores"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_identifier
    )
    raw_opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("raw_opportunities.id"), unique=True, nullable=False
    )
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_match: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    requirement_clarity: Mapped[int] = mapped_column(Integer, nullable=False)
    client_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    portfolio_relevance: Mapped[int] = mapped_column(Integer, nullable=False)
    repeat_work_potential: Mapped[int] = mapped_column(Integer, nullable=False)
    competition: Mapped[int] = mapped_column(Integer, nullable=False)
    penalties: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class ProposalDraftRecord(Base):
    """Persistence representation of a proposal draft awaiting human approval."""

    __tablename__ = "proposal_drafts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_identifier
    )
    raw_opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("raw_opportunities.id"), unique=True, nullable=False
    )
    client_problem_summary: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_solution: Mapped[str] = mapped_column(Text, nullable=False)
    relevant_evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    questions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    proposal_text: Mapped[str] = mapped_column(Text, nullable=False)
    requires_human_approval: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class ApplicationOutcomeRecord(Base):
    """Persistence representation of a manually recorded application result."""

    __tablename__ = "application_outcomes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_identifier
    )
    raw_opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("raw_opportunities.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
