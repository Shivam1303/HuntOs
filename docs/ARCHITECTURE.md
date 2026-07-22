# Lead Hunting MVP Architecture

## Scope and Technology

The MVP is limited to finding, assessing, researching, and drafting proposals for freelance opportunities. It does not include CRM, outreach, analytics, learning, scheduler, or multi-agent capabilities.

- Backend: FastAPI
- Review frontend: Streamlit
- Persistence: SQLite
- Initial LLM provider: Gemini, behind a replaceable interface

No component may submit proposals or send email automatically.

## Project Layout

```text
core/
  config/       # Settings and configuration boundaries
  database/     # SQLite connection and persistence primitives
  llm/          # Provider-neutral LLM contracts and Gemini adapter
modules/
  opportunities/ # Opportunity-specific use cases and models
  scoring/      # Deterministic scoring rules
  research/     # Permitted client research use cases
  proposals/    # Evidence-constrained proposal drafting
api/            # FastAPI transport layer and dependency composition
frontend/       # Streamlit human-review interface
tests/          # Unit and integration tests
```

Business modules may depend on `core`. `core` must never depend on a business module. The `api` and `frontend` layers compose dependencies and delegate work to modules; they must not become alternate homes for business logic.

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
Manual Follow-up Outside the System
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

Only deterministic Python calculates scores and penalties. The LLM may parse, summarize, research, and draft, but it must not make scoring decisions.

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

The first frontend is a minimal Streamlit review interface. It presents information and records explicit human decisions; it never sends an outbound action.

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
