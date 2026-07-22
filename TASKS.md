# TASKS.md

Complete tasks in order. Do not skip ahead unless a dependency requires it.

## Phase 0 — Project Setup

- [x] Initialize Python project (create the empty importable MVP skeleton)
- [ ] Add `pyproject.toml`
- [ ] Add Ruff, MyPy, and Pytest configuration
- [ ] Add `.env.example`
- [ ] Add `.gitignore`
- [ ] Add package-level implementation as each setup and feature task requires it
- [ ] Add health-check endpoint
- [ ] Add basic CI workflow

## Phase 1 — Data Models and Database

- [ ] Define `DeveloperProfile`
- [ ] Define `RawOpportunity`
- [ ] Define `ParsedOpportunity`
- [ ] Define `OpportunityScore`
- [ ] Define `ProposalDraft`
- [ ] Define `ApplicationOutcome`
- [ ] Configure SQLite
- [ ] Create database models
- [ ] Add database migrations or initialization
- [ ] Add repository layer
- [ ] Add duplicate-detection logic

## Phase 2 — CSV Import

- [ ] Define supported CSV columns
- [ ] Implement CSV validator
- [ ] Implement CSV importer
- [ ] Return row-level validation errors
- [ ] Store valid opportunities
- [ ] Prevent duplicate imports
- [ ] Add CSV import tests
- [ ] Add sample CSV file

## Phase 3 — LLM Provider

- [ ] Define provider interface
- [ ] Implement Gemini provider
- [ ] Read API key from environment
- [ ] Add timeout handling
- [ ] Add retry policy
- [ ] Add structured-output validation
- [ ] Add fake provider for tests
- [ ] Add provider tests

## Phase 4 — Opportunity Parser

- [ ] Create opportunity parser prompt
- [ ] Parse required skills
- [ ] Parse business problem
- [ ] Parse deliverables
- [ ] Parse experience level
- [ ] Parse warning signs
- [ ] Store raw model output for debugging
- [ ] Validate parsed output
- [ ] Add parser tests

## Phase 5 — Deterministic Scoring

- [ ] Define scoring configuration
- [ ] Implement skill-match score
- [ ] Implement budget score
- [ ] Implement clarity score
- [ ] Implement client-quality score
- [ ] Implement portfolio-match score
- [ ] Implement repeat-work score
- [ ] Implement competition score
- [ ] Implement penalties
- [ ] Return score explanation
- [ ] Add unit tests for every rule

## Phase 6 — Proposal Generator

- [ ] Create proposal brief schema
- [ ] Generate client-problem summary
- [ ] Generate proposed solution
- [ ] Generate clarification questions
- [ ] Generate proposal draft
- [ ] Add hallucination guardrails
- [ ] Require profile evidence for claims
- [ ] Add proposal tests

## Phase 7 — Review Dashboard

- [ ] Build Streamlit opportunity list
- [ ] Add sorting by score
- [ ] Add filters
- [ ] Show extracted evidence
- [ ] Show score breakdown
- [ ] Show proposal draft
- [ ] Add approve, edit, reject actions
- [ ] Add applied status
- [ ] Add outcome tracking

## Phase 8 — Evaluation

- [ ] Create 30 synthetic opportunities
- [ ] Label strong, weak, and ambiguous cases
- [ ] Measure parsing accuracy
- [ ] Measure scoring consistency
- [ ] Measure false-positive rate
- [ ] Track proposal approval rate
- [ ] Add regression dataset

## Phase 9 — Optional Integrations

- [ ] Gmail job-alert ingestion
- [ ] Google Sheets export
- [ ] Public company website research
- [ ] Scheduled processing
- [ ] Notifications
