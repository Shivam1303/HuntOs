# Phase 1 - Data Models and Database

Status: complete. Raw-opportunity PostgreSQL integration is verified in Phase 2;
non-import adapter integration remains future work.

## Delivered changes

- Added Pydantic schemas for `DeveloperProfile`, `RawOpportunity`,
  `ParsedOpportunity`, `OpportunityScore`, `ProposalDraft`, and
  `ApplicationOutcome`.
- Enforced core input invariants: non-empty required text, non-negative money
  and proposal counts, ordered budget ranges, bounded score components, and a
  proposal draft that always requires human approval.
- Added PostgreSQL-only URL validation and a transaction-scoped
  `PostgreSQLDatabase` service using SQLAlchemy 2 and Psycopg 3.
- Added module-owned SQLAlchemy records and the initial Alembic migration for
  profiles, raw opportunities, parsed opportunities, scores, proposal drafts,
  and manual application outcomes.
- Added focused PostgreSQL repositories in `modules/opportunities`,
  `modules/scoring`, and `modules/proposals`. The opportunities module also
  exposes the `RawOpportunityRepository` protocol for dependency injection.
- Kept `core/database` limited to the engine, transaction, migration, and
  shared SQLAlchemy declarative-base primitives.
- Added deterministic duplicate fingerprints for raw opportunities. The
  fingerprint normalizes platform, source ID, URL, title, and description, and
  is protected by a unique database index.
- Added Docker, Compose, and database-development guidance for local
  PostgreSQL and reviewed Alembic migrations.

## Important contracts for later phases

### Raw opportunity persistence

`RawOpportunity` is the source record for every imported job. It requires
`platform`, `title`, and `description`; all other import fields are optional.
`RawOpportunityRecord.fingerprint` is required and unique. Use
`opportunity_fingerprint()` before calling
`PostgreSQLOpportunityRepository.add_raw_opportunity()`.

### Database discipline

- PostgreSQL is the application database; SQLite is not a supported runtime
  substitute.
- Supply `DATABASE_URL` in the `postgresql+psycopg://...` form.
- Apply schema changes through reviewed Alembic migrations only. Do not call
  `Base.metadata.create_all()` at application startup.
- Integration tests must use `TEST_DATABASE_URL` pointing to a database ending
  in `_test`, never the development database.

### Safety boundaries

Persisted proposal drafts retain `requires_human_approval=True`. Application
outcomes record manual results only; neither model nor repository performs an
outbound action. Scores are storage contracts at this point, not scoring
logic.

## Integration follow-up

Phase 2 now verifies raw-opportunity migrations, persistence, and duplicate
handling against an isolated `*_test` PostgreSQL database. Live integration
coverage for the profile, parsed-opportunity, scoring, and proposal adapters
remains future work in their owning feature phases.

## Phase 2 result

Phase 2 validates CSV rows into `RawOpportunity`, calculates the existing
fingerprint, and persists only valid, non-duplicate records through the
repository. Its completed delivery record is in
[02-csv-import-plan.md](02-csv-import-plan.md).
