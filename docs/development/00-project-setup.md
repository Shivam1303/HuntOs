# Phase 0 - Project Setup

Status: complete.

## Delivered changes

- Created the Python 3.12 project, packaging metadata, and development-tool
  configuration in `pyproject.toml`.
- Established the dependency-oriented package layout: `api`, `core`, and the
  permitted Lead Hunting business modules.
- Added FastAPI application startup with `GET /health`, which returns
  `{ "status": "ok" }`.
- Added local-configuration and repository hygiene files, including
  `.env.example`, `.gitignore`, and `.dockerignore`.
- Added the baseline GitHub Actions workflow in `.github/workflows/ci.yml`.
- Added regression tests for the project structure, tool configuration,
  environment template, and health endpoint.

## Important implementation rules carried forward

- Keep new packages inside the approved MVP layout. Do not introduce CRM,
  outreach, analytics, learning, scheduler, or multi-agent modules.
- Configuration is environment-backed. `GEMINI_API_KEY` remains blank in the
  template and must never be committed.
- Ruff checks `E`, `F`, and import ordering; MyPy runs in strict mode for
  `api`, `core`, and `modules`.
- Preserve the health endpoint as a lightweight process-readiness check. It
  does not assert database availability.

## Verification baseline

The Phase 0 tests are in `tests/test_phase_zero.py` and
`tests/test_project_structure.py`. The normal verification set is:

```bash
pytest
ruff check .
mypy
```

## Handoff to Phase 1

Phase 1 added the durable data contracts and PostgreSQL persistence described
in [01-data-models-and-database.md](01-data-models-and-database.md). Features
that create or process opportunities must build on those contracts rather than
adding an alternate data store.
