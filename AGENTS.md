# AGENTS.md

This file defines how Codex should work in this repository.

## Role

Act as a senior Python engineer implementing one small, testable task at a time.

Do not redesign the entire system unless explicitly requested.

## Working Method

For each task:

1. Read the relevant specification files
2. Identify the smallest implementation slice
3. Write or update tests first
4. Implement the feature
5. Run tests
6. Run linting and type checks
7. Summarize changed files and remaining risks

## Engineering Rules

- Use Python 3.12+
- Use type hints everywhere
- Use Pydantic for request, response, and LLM schemas
- Keep functions focused and small
- Keep modules under roughly 300 lines where practical
- Prefer explicit code over clever abstractions
- Do not hardcode prompts inside Python modules
- Do not calculate scores using an LLM
- Do not automatically send proposals or emails
- Do not store secrets in source code
- Add tests for every business rule
- Use dependency injection for external services
- Use interfaces for LLM providers
- Preserve provider independence

## Architecture Boundaries

### LLM responsibilities

The LLM may:

- Extract skills
- Identify business problems
- Summarize requirements
- Identify warning signs
- Draft proposal text
- Suggest clarification questions

### Deterministic code responsibilities

Python must:

- Calculate scores
- Apply penalties
- Validate required fields
- Enforce approval requirements
- Prevent duplicate processing
- Store workflow state
- Decide whether an outbound action is permitted

## Safety Rules

Never:

- Submit a proposal automatically
- Send an email automatically
- Claim experience the user does not have
- Invent portfolio projects
- Invent client details
- Scrape platforms in ways that violate their terms
- Hide failures or silently discard invalid data

## Testing Rules

Tests must cover:

- Valid CSV import
- Invalid CSV rows
- Duplicate opportunities
- Score calculation
- Penalty application
- Missing budget handling
- LLM parsing failures
- Proposal generation with missing profile data
- Approval requirement before outbound actions

## Output Expectations

When completing a task, report:

- Files changed
- Tests added
- Commands run
- Any unresolved issue
