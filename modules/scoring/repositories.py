"""PostgreSQL repository owned by the scoring module."""

from sqlalchemy.orm import Session

from modules.scoring.models import OpportunityScoreRecord
from modules.scoring.schemas import OpportunityScore


class PostgreSQLScoreRepository:
    """Persist deterministic opportunity scores."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_opportunity_score(
        self,
        *,
        raw_opportunity_id: str,
        score: OpportunityScore,
    ) -> OpportunityScoreRecord:
        """Store a score calculated by deterministic Python code."""

        record = OpportunityScoreRecord(
            raw_opportunity_id=raw_opportunity_id,
            **score.model_dump(),
        )
        self._session.add(record)
        self._session.flush()
        return record
