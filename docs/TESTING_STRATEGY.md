# Testing Strategy

## Unit Tests

Test pure business logic:

- Skill normalization
- Skill matching
- Budget scoring
- Penalties
- Duplicate detection
- Status transitions

## Integration Tests

Test:

- CSV import to database
- Parser with fake LLM provider
- Score generation
- Proposal generation
- API endpoints

## LLM Contract Tests

Use a fake provider for normal tests.

Optionally run real Gemini tests manually.

Validate:

- Required fields
- Maximum lengths
- No invented claims
- Warning signs returned as a list
- Malformed output handled safely

## Evaluation Dataset

Create:

- 10 strong opportunities
- 10 weak opportunities
- 10 ambiguous opportunities

For each record include:

- Expected label
- Expected score range
- Expected warning signs
- Expected required skills

## Regression Rules

A change must not:

- Increase automatic approval
- Remove score explanations
- Produce invented experience
- Reduce parsing success without explanation
