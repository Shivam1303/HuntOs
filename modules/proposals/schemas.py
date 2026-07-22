"""Pydantic schema for proposal drafts that always require human approval."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ProposalDraft(BaseModel):
    """A draft only; it cannot represent approval to send an outbound proposal."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    client_problem_summary: NonEmptyText
    proposed_solution: NonEmptyText
    relevant_evidence: list[NonEmptyText]
    questions: list[NonEmptyText]
    proposal_text: NonEmptyText
    requires_human_approval: Literal[True] = Field(default=True)
