# Phase 2 - CSV Import Plan

Status: planned. No CSV importer or validator has been implemented yet.

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
for imported data. Existing `sample_opportunities.csv` is illustrative only;
Phase 2 must update it to this exact header contract and include both valid
and intentionally problematic examples in tests rather than relying on the
sample for failure coverage.

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

## Risks to resolve during implementation

- Phase 1's PostgreSQL repository tests are currently skipped, so the test
  database fixture and migration lifecycle need to be completed before the
  importer can prove persistence behavior.
- CSV parsers can accept malformed dialects differently. Keep the first
  version deliberately narrow (standard comma-delimited UTF-8 CSV) and return
  a clear file-level error for parser failures.
- Do not use the sample file as evidence of successful persistence. Tests need
  an isolated PostgreSQL database and explicit assertions for stored rows.
