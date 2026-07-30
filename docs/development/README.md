# Development Record

This directory is the implementation record and handoff guide for the Lead
Hunting MVP. It supplements the product and architecture specifications; it
does not replace them.

## Phase status

| Phase | Status | Development record |
| --- | --- | --- |
| 0 - Project setup | Complete | [00-project-setup.md](00-project-setup.md) |
| 1 - Data models and database | Complete, with non-import adapter integration follow-up | [01-data-models-and-database.md](01-data-models-and-database.md) |
| 2 - CSV import | Complete | [02-csv-import-plan.md](02-csv-import-plan.md) |

The authoritative task checklist remains [TASKS.md](../../TASKS.md). Future
phases should receive a development record when work starts, then be updated
with the actual changed files, verification commands, and unresolved risks
before they are marked complete.

## Project-wide constraints

- Use Python 3.12+, Pydantic schemas, SQLAlchemy, PostgreSQL, and Alembic.
- Keep business rules in `modules/`; `core/` must not import business modules.
- The LLM interprets text only. Python calculates scores and controls workflow
  decisions.
- No feature may submit a proposal or send email automatically.
- Do not store secrets in source code or logs.

## How to use these records

Before starting a phase, read its plan together with the product,
architecture, data-model, and testing specifications. During implementation,
keep the phase record factual: distinguish confirmed behavior from a planned
decision, and capture anything that prevents the definition of done from being
met.
