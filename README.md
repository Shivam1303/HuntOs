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
- SQLite persistence
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
- SQLite
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
  opportunities/
  scoring/
  research/
  proposals/
api/
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

- Business modules may depend on `core`.
- `core` must never depend on business modules.
- `api` and `frontend` compose the application; they do not contain scoring or LLM business rules.

Gemini is the first LLM provider behind a replaceable provider interface. SQLite is the MVP datastore, FastAPI provides the backend, and Streamlit provides the minimal review frontend.
