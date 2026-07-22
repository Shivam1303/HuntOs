# Product Specification

## Product Name

Freelance Opportunity Hunter Agent

## Problem

Freelancers waste time:

- Reviewing low-quality opportunities
- Applying to poor-fit jobs
- Writing repetitive proposals
- Researching clients manually
- Tracking applications inconsistently

## Target User

A solo developer or small technical agency offering:

- AI automation
- Python development
- API integrations
- Internal tools
- Document processing
- Workflow automation

## User Outcome

The user should be able to upload a set of opportunities and quickly identify:

- Which jobs are worth applying to
- Why they are a good fit
- What risks exist
- What solution angle to use
- What proposal to send after review

## Primary Workflow

1. User imports opportunities
2. System validates and stores them
3. LLM extracts structured information
4. Scoring engine ranks opportunities
5. System generates proposal drafts for top opportunities
6. User reviews and approves manually
7. User records outcome

## Functional Requirements

### Opportunity Import

Support CSV input with:

- title
- description
- budget
- client_name
- client_history
- posted_at
- proposal_count
- url
- platform

### Opportunity Parsing

Extract:

- Required skills
- Business problem
- Expected deliverables
- Experience level
- Budget information
- Warning signs
- Missing information
- Suggested clarification questions

### Scoring

Score from 0 to 100.

Suggested weights:

- Skill match: 25
- Budget quality: 15
- Requirement clarity: 10
- Client quality: 15
- Portfolio relevance: 15
- Repeat-work potential: 10
- Competition: 10

Penalties:

- Unpaid test: -30
- Commission-only: -30
- Suspicious links: -20
- Unrealistic budget: -20
- Free complete work request: -25
- Very vague scope: -10

### Proposal Generation

Produce:

- Client problem summary
- Solution approach
- Relevant skills
- Two intelligent questions
- Concise proposal draft

### Human Approval

All outbound actions require approval.

## Non-Functional Requirements

- Parsed results must be reproducible where possible
- Scores must be explainable
- Invalid LLM output must not crash the system
- Duplicate opportunities must be detected
- Secrets must remain outside source control
- Processing failures must be visible

## Success Metrics

- Opportunity processing under 30 seconds
- Proposal generation under 60 seconds
- Zero automatic submissions
- Explainable score for every opportunity
- At least 80% agreement with manual labels on test data
