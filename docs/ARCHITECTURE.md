# Lead Hunting MVP Architecture

## Scope and Technology

The MVP is limited to finding, assessing, researching, and drafting proposals for freelance opportunities. It does not include CRM, outreach, analytics, learning, scheduler, or multi-agent capabilities.

- Backend: FastAPI
- Review frontend: Streamlit
- Persistence: PostgreSQL
- Initial LLM provider: Gemini, behind a replaceable interface

No component may submit proposals or send email automatically.

## Project Layout

```text
core/
  config/       # Settings and configuration boundaries
  database/     # PostgreSQL connection and persistence primitives
  llm/          # Provider-neutral LLM contracts and Gemini adapter
modules/
  opportunities/ # Schemas, ORM models, repository, and use cases
  scoring/      # Models, repository, and deterministic scoring rules
  research/     # Permitted client research use cases
  proposals/    # Models, repository, and drafting use cases
api/            # Thin FastAPI controllers and dependency composition
frontend/       # Streamlit human-review interface
tests/          # Unit and integration tests
```

Business modules may depend on `core`. `core` must never depend on a business module. Each business module owns its schemas, SQLAlchemy records, repository port, and PostgreSQL adapter. The `api` and `frontend` layers compose dependencies and delegate work to modules; they must not become alternate homes for business logic.

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
Manual Application Outcome Recording
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

### Persistence Layer

`core/database` owns only shared PostgreSQL engine, transaction, Alembic, and SQLAlchemy declarative-base primitives. It contains no business repositories.

Each business module owns its table mappings and repository:

- `modules/opportunities`: profiles, raw and parsed opportunities, and manual outcomes;
- `modules/scoring`: deterministic score records;
- `modules/proposals`: human-reviewed proposal drafts.

Repository protocols support dependency injection into use cases. PostgreSQL adapters accept validated Pydantic schemas and persist module-owned ORM models. Alembic is the composition point that imports every module model before reading `Base.metadata`.

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
- Manual outcome record

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
