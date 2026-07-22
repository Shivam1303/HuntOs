"""PostgreSQL repository owned by the proposals module."""

from sqlalchemy.orm import Session

from modules.proposals.models import ProposalDraftRecord
from modules.proposals.schemas import ProposalDraft


class PostgreSQLProposalRepository:
    """Persist proposal drafts without performing outbound actions."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_proposal_draft(
        self,
        *,
        raw_opportunity_id: str,
        draft: ProposalDraft,
    ) -> ProposalDraftRecord:
        """Store a draft that still requires human approval."""

        record = ProposalDraftRecord(
            raw_opportunity_id=raw_opportunity_id,
            **draft.model_dump(),
        )
        self._session.add(record)
        self._session.flush()
        return record
