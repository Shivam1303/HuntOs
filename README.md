# Lead Hunting MVP

An AI-assisted, human-reviewed lead-hunting tool for freelancers and small technical agencies.

## Product Goal

The MVP helps a developer:

1. Import freelance opportunities
2. Analyze and structure each opportunity
3. Score it with deterministic rules
4. Research the client when allowed
5. Generate a personalized proposal draft
6. Require human approval before any outbound action
7. Record review decisions manually

## MVP Scope

The Lead Hunting MVP is designed to support:

- CSV opportunity import
- Structured opportunity parsing
- Deterministic scoring
- Gemini-based analysis
- Proposal draft generation
- Streamlit review dashboard
- PostgreSQL persistence
- Manual review of proposal drafts

The first version does **not** support:

- Automatic proposal submission
- Aggressive scraping
- Multi-agent orchestration
- Autonomous email sending
- Paid enrichment services
- Vector databases
- CRM, outreach, analytics, learning, scheduler, or multi-agent modules

## Recommended Stack

- Python 3.12+
- FastAPI
- Streamlit
- PostgreSQL
- SQLAlchemy
- Pydantic
- Google Gemini API
- Pytest
- Ruff
- MyPy

## Repository Structure

```text
core/
  config/
  database/
  llm/
modules/
  opportunities/       # Schemas, models, repository, and use cases
  scoring/             # Models, repository, and deterministic rules
  research/
  proposals/           # Models, repository, and drafting use cases
api/                   # Thin FastAPI controllers
frontend/
tests/
docs/
prompts/
AGENTS.md
TASKS.md
README.md
```

## Start Here

1. Read `AGENTS.md`
2. Read `docs/PRODUCT_SPEC.md`
3. Read `docs/ARCHITECTURE.md`
4. Complete tasks in `TASKS.md` from top to bottom
5. Use `prompts/CODEX_STARTER_PROMPT.md` to begin development with Codex

## Core Principle

The LLM interprets text.

Python code makes measurable business decisions.

Human approval controls outbound actions.

## Dependency Direction

- Business modules own their Pydantic schemas, SQLAlchemy models, repositories, and use cases.
- `core/database` owns only shared engine, session, migration, and declarative-base primitives.
- Business modules may depend on `core`; `core` must never depend on business modules.
- FastAPI controllers live in `api`, compose module repositories, and remain thin transport adapters.
- `frontend` composes the application and does not contain scoring or LLM business rules.

Gemini is the first LLM provider behind a replaceable provider interface. PostgreSQL is the MVP datastore, FastAPI provides the backend, and Streamlit provides the minimal review frontend.

## LLM Provider Configuration

`core/llm` keeps application code independent of any provider SDK. Business
modules depend only on `LLMProvider`, which supports asynchronous plain-text
generation and structured Pydantic output. They must never import
`google.genai` directly. This boundary keeps provider errors, response objects,
timeouts, and authentication details out of business logic and makes offline
tests deterministic.

The Gemini adapter uses the current `google-genai` package, not the legacy
`google-generativeai` package. Copy `.env.example` to `.env` and configure:

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=an-available-gemini-flash-model
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=3
LLM_MAX_OUTPUT_TOKENS=2048
LLM_TEMPERATURE=0.2
```

`GEMINI_MODEL` is intentionally required rather than spread as a constant
throughout the codebase. Model names, availability, and free-tier quotas can
change. Select a currently available Flash model from the
[official Gemini models documentation](https://ai.google.dev/gemini-api/docs/models)
and set its exact model ID in the environment. Constructing a real provider
without both the API key and model raises `LLMConfigurationError`.

`create_llm_provider(LLMSettings.from_env())` creates a fresh provider suitable
for later FastAPI dependency injection. Set `LLM_PROVIDER=fake` in test-specific
settings when a factory-created offline provider is needed; unit tests can also
instantiate `FakeLLMProvider` with predefined responses and failures directly.

## LLM Tests

The standard suite mocks the Google SDK and never needs an API key:

```bash
pytest
ruff check .
mypy
```

An optional minimal live request is excluded by default. To run it explicitly,
export a valid key and a model currently available to that key:

```bash
export GEMINI_API_KEY=your-key
export GEMINI_MODEL=an-available-gemini-flash-model
pytest -m live_llm
```

The SDK receives the request timeout in milliseconds. Its single configured
retry layer makes the initial request plus at most `LLM_MAX_RETRIES` retries for
HTTP 408, 429, 500, 502, 503, and 504 responses and for supported timeout or
connection failures. Backoff starts at one second, doubles to an eight-second
cap, and includes small jitter. Authentication failures, permanent 4xx errors,
content-policy failures, and Pydantic validation failures are not retried.

To add another provider, implement `LLMProvider` in an isolated adapter, map its
SDK failures to `core.llm.exceptions`, add one explicit factory branch, and add
mocked contract tests. No business-module import needs to change.
