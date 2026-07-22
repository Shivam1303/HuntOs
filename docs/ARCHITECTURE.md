# Architecture

## High-Level Flow

```text
CSV Import
   ↓
Validation
   ↓
Database
   ↓
LLM Opportunity Parser
   ↓
Deterministic Scoring Engine
   ↓
Proposal Brief Generator
   ↓
Proposal Draft Generator
   ↓
Human Review Dashboard
   ↓
Manual Application Tracking
```

## Main Components

### API Layer

Responsibilities:

- Import opportunities
- Return opportunity details
- Trigger parsing
- Trigger scoring
- Trigger proposal generation
- Save review actions

### Database Layer

Store:

- Raw opportunities
- Parsed opportunities
- Scores
- Proposal drafts
- Application outcomes
- Processing errors

### LLM Layer

Expose a provider-neutral interface.

```python
from typing import Protocol, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMProvider(Protocol):
    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        ...
```

Initial provider:

- Gemini

Future providers:

- OpenAI
- Anthropic
- Local models

### Scoring Layer

Pure Python functions.

No network calls.

No LLM calls.

Every score must include an explanation.

### Proposal Layer

Uses:

- Parsed opportunity
- Developer profile
- Score explanation
- Optional client research

The proposal generator must not invent experience.

### Frontend

Use Streamlit for MVP.

Views:

- Import
- Opportunity list
- Opportunity detail
- Proposal review
- Outcomes

## State Model

Suggested statuses:

```text
IMPORTED
PARSING
PARSED
SCORING
SCORED
DRAFTING
READY_FOR_REVIEW
APPROVED
REJECTED
APPLIED
WON
LOST
ERROR
```

## Error Handling

Store:

- Error type
- Error message
- Input reference
- Retry count
- Timestamp

## Security

- API keys in environment variables
- No secrets in logs
- No automatic outbound actions
- Validate URLs before fetching
- Add request timeouts
