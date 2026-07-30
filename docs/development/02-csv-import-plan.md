# Phase 2 - CSV Import Plan

Status: complete. CSV validation, persistence, row-level errors, duplicate
prevention, comprehensive tests, and the canonical sample file are delivered.

## Goal

Turn a user-supplied CSV into validated `RawOpportunity` records while making
every rejected or duplicate row visible. This phase ends at persistence; it
does not parse opportunities with an LLM, score them, generate proposals, or
send anything outbound.

## Supported CSV contract

The importer will read UTF-8 CSV (including an optional UTF-8 BOM) with a
header row. Canonical headers are:

| Column | Required | Conversion and validation |
| --- | --- | --- |
| `platform` | Yes | Non-empty text |
| `title` | Yes | Non-empty text |
| `description` | Yes | Non-empty text |
| `source_id` | No | Non-empty text or `None` |
| `budget_min` | No | Decimal-compatible, finite number greater than or equal to zero |
| `budget_max` | No | Decimal-compatible, finite number greater than or equal to zero; must not be below `budget_min` |
| `client_name` | No | Non-empty text or `None` |
| `client_history` | No | Non-empty text or `None` |
| `proposal_count` | No | Whole number greater than or equal to zero |
| `posted_at` | No | ISO 8601 timestamp with an explicit offset, stored as an aware datetime |
| `url` | No | Non-empty text or `None` |

Whitespace-only optional cells become `None`. Required header names are a
file-level contract: a file without one is rejected before persistence. An
unknown header is also a file-level error so ignored input cannot be mistaken
for imported data. `sample_opportunities.csv` uses this exact header contract and contains valid
illustrative rows. Intentionally problematic examples remain in tests rather
than the distributable sample.

The canonical order and its required/optional partitions are defined as
immutable tuples in `modules/opportunities/csv_columns.py`. The validator and importer consume that contract instead of maintaining their
own header lists.

## Delivered progress

- Defined all 11 supported CSV columns in canonical order.
- Marked `platform`, `title`, and `description` as required; the remaining
  columns are optional.
- Added unit coverage for exact ordering, partition membership, and ensuring
  the two partitions are disjoint and exhaustive.
- Added header validation for missing required, unsupported, and duplicate
  columns.
- Added single-row conversion into `RawOpportunity`, including optional blank
  normalization, finite numeric conversion, whole-number proposal counts,
  timezone-aware ISO 8601 timestamps, and existing schema invariants.
- Added field-aware validation exceptions consumed by importer result handling.
- Added a transport-only importer that decodes UTF-8 bytes with optional BOM,
  parses standard CSV quoting and multiline fields, validates the header, and
  returns validated `RawOpportunity` models in file order.
- Added explicit file-level failures for invalid UTF-8 and malformed CSV
  syntax.
- Added `CSVImportResult` and `CSVRowError` Pydantic response schemas. Invalid
  rows include their logical row number, field when known, and message; later
  valid rows continue processing. Extra cells are reported as a local row
  error. The result exposes total, valid, and rejected row counts.
- Added a `CSVImporter` service with an injected `RawOpportunityRepository`. It
  stores only validated opportunities, supplies deterministic fingerprints,
  and returns stored record IDs and a stored count. Persistence failures remain
  visible so the caller-owned transaction can roll back.
- Added duplicate reporting with row number and reason for repeated rows within
  one upload, opportunities already in the repository, and conflicts detected
  during storage. Duplicate rows are skipped while later valid rows continue.
- Wrapped PostgreSQL raw-opportunity inserts in a nested transaction and mapped
  SQLSTATE `23505` unique violations to `DuplicateOpportunityError`. Other
  integrity failures continue to propagate.
- Added isolated PostgreSQL integration coverage that applies Alembic, commits
  every supported field for valid rows, rejects invalid rows, and proves a
  second import is skipped without another database record.
- Updated `sample_opportunities.csv` to the exact canonical 11-column order
  with three valid examples, including optional blank values. A contract test
  executes the sample through the importer.

Verification for this slice:

```text
TEST_DATABASE_URL=postgresql+psycopg://hunter:hunter@localhost:5432/hunter_test PYTHONDONTWRITEBYTECODE=1 /tmp/huntos-phase2-uv/bin/python -m pytest -p no:cacheprovider
/tmp/huntos-phase2-uv/bin/ruff check .
/tmp/huntos-phase2-uv/bin/mypy
git diff --check
```

PostgreSQL import behavior was verified against the isolated `hunter_test`
database. The integration fixture refuses non-`*_test` URLs and cleans imported
rows around each test. Unit tests remain the default fast path and PostgreSQL
tests skip clearly when `TEST_DATABASE_URL` is absent.

## Behavior and result model

Create a small importer service in `modules/opportunities/` and keep the CSV
transport details out of the repository. Its public result should expose:

- total data rows read;
- number imported;
- number rejected for validation, each with the one-based CSV row number,
  field when known, and a clear message;
- number skipped as duplicates, each with its row number and reason; and
- identifiers for newly stored opportunities when useful to a later API.

Processing is row-isolated: a malformed row does not prevent later valid rows
from being imported. A row is persisted only after conversion and Pydantic
validation succeed. Blank physical lines are ignored and are not reported as
opportunities.

## Duplicate policy

For every valid row:

1. Build `RawOpportunity`.
2. Calculate `opportunity_fingerprint()`.
3. Detect duplicates already seen in this upload and duplicates already stored
   through the repository.
4. Report duplicates as skipped; never create another raw-opportunity record.

The database's unique fingerprint index remains the final protection against
concurrent imports. The importer must convert a uniqueness conflict into a
visible duplicate result, not discard it silently or return a server error.

## Smallest implementation slice

1. Add failing unit tests for supported headers, conversion, row errors, and
   the import result shape.
2. Implement a CSV-row validator that converts strings to the existing
   `RawOpportunity` schema without doing database work.
3. Implement the importer with an injected `RawOpportunityRepository` port;
   compose `PostgreSQLOpportunityRepository` at the API boundary.
4. Add isolated PostgreSQL integration tests for stored rows and duplicate
   conflicts; re-enable the Phase 1 repository tests as part of establishing
   this test infrastructure.
5. Update `sample_opportunities.csv` to the supported format and document how
   to use the importer when an API or frontend consumes it in a later phase.

An HTTP endpoint is not required for this phase's smallest testable slice. If
one is added, it must be a thin FastAPI adapter over the importer and return
the same row-level result; it must not duplicate validation or persistence
logic.

## Required tests

- A valid CSV imports all valid rows and maps every supported column.
- Missing required headers and unknown headers fail before any row is stored.
- Invalid required text, bad numeric values, a reversed budget range, invalid
  proposal counts, and invalid timestamps produce row-level errors.
- A mixed file stores valid rows while retaining errors for invalid rows.
- Empty optional cells become `None`.
- Duplicate rows in one upload and records already in PostgreSQL are reported
  as duplicates and not inserted twice.
- A database uniqueness conflict caused by concurrent work becomes a visible
  duplicate result.
- The sample CSV uses the final canonical headers.

## Definition of done

- Every Phase 2 item in `TASKS.md` is complete.
- Valid rows are stored in PostgreSQL through the established repository
  boundary.
- Every invalid or duplicate row is represented in the import result.
- No LLM, scoring, proposal, research, or outbound code is introduced.
- `pytest`, `ruff check .`, and `mypy` pass, including the restored isolated
  PostgreSQL integration coverage.

## Resolved and remaining risks

- The raw-opportunity PostgreSQL migration, persistence, and duplicate path is
  now covered against an isolated test database.
- CSV parsing is deliberately limited to standard comma-delimited UTF-8 input;
  malformed syntax and invalid encoding remain visible file-level failures.
- The sample file proves the public CSV contract, while persistence evidence
  comes from dedicated integration fixtures rather than sample execution.
- Verification currently emits upstream deprecation warnings for Starlette
  `httpx` compatibility and Alembic `path_separator`; neither affects Phase 2
  behavior.
