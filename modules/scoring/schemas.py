"""Pydantic schema for explainable deterministic opportunity scores."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class OpportunityScore(BaseModel):
    """The persisted result of deterministic scoring, without scoring logic."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    total: int = Field(ge=0, le=100)
    skill_match: int = Field(ge=0, le=25)
    budget_quality: int = Field(ge=0, le=15)
    requirement_clarity: int = Field(ge=0, le=10)
    client_quality: int = Field(ge=0, le=15)
    portfolio_relevance: int = Field(ge=0, le=15)
    repeat_work_potential: int = Field(ge=0, le=10)
    competition: int = Field(ge=0, le=10)
    penalties: int = Field(le=0)
    explanation: list[NonEmptyText]
