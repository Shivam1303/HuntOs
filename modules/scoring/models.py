"""SQLAlchemy records owned by the scoring module."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models import Base, new_identifier, utc_now


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
