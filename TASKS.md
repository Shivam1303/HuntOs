# TASKS.md

Complete tasks in order. Do not skip ahead unless a dependency requires it.

## Phase 0 — Project Setup

- [x] Initialize Python project (create the empty importable MVP skeleton)
- [x] Add `pyproject.toml`
- [x] Add Ruff, MyPy, and Pytest configuration
- [x] Add `.env.example`
- [x] Add `.gitignore`
- [x] Add package-level implementation as each setup and feature task requires it
- [x] Add health-check endpoint
- [x] Add basic CI workflow

## Phase 1 — Data Models and Database

- [x] Define `DeveloperProfile`
- [x] Define `RawOpportunity`
- [x] Define `ParsedOpportunity`
- [x] Define `OpportunityScore`
- [x] Define `ProposalDraft`
- [x] Define `ApplicationOutcome`
- [x] Configure PostgreSQL
- [x] Create database models
- [x] Add database migrations or initialization
- [x] Add repository layer
- [x] Add duplicate-detection logic

## Phase 2 — CSV Import

- [x] Define supported CSV columns
- [x] Implement CSV validator   
- [x] Implement CSV importer
- [x] Return row-level validation errors
- [x] Store valid opportunities
- [x] Prevent duplicate imports
- [x] Add CSV import tests
- [x] Add sample CSV file

## Phase 3 — LLM Provider

- [x] Define provider interface
- [x] Implement Gemini provider
- [x] Read API key from environment
- [x] Add timeout handling
- [x] Add retry policy
- [x] Add structured-output validation
- [x] Add fake provider for tests
- [x] Add provider tests

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
