# Freelance Opportunity Hunter Agent

A Codex-ready starter specification for building an AI-powered business development assistant for freelancers.

## Product Goal

The agent should help a developer:

1. Import freelance opportunities
2. Analyze and structure each opportunity
3. Score it with deterministic rules
4. Research the client when allowed
5. Generate a personalized proposal draft
6. Require human approval before any outbound action
7. Track outcomes and improve recommendations

## MVP Scope

The first version supports:

- CSV opportunity import
- Structured opportunity parsing
- Deterministic scoring
- Gemini-based analysis
- Proposal draft generation
- Streamlit review dashboard
- SQLite persistence
- Manual application tracking

The first version does **not** support:

- Automatic proposal submission
- Aggressive scraping
- Multi-agent orchestration
- Autonomous email sending
- Paid enrichment services
- Vector databases

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
app/
  api/
  database/
  llm/
  models/
  parser/
  proposal/
  research/
  scoring/
  services/
  prompts/
frontend/
tests/
data/
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
