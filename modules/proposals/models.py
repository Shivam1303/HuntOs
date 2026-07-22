"""SQLAlchemy records owned by the proposals module."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models import Base, new_identifier, utc_now


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
