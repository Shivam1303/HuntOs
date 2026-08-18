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

Standard tests use `FakeLLMProvider` or a fully mocked Gemini SDK. They never
require `GEMINI_API_KEY` and never make a network request.

Provider tests cover:

- text and strict structured Pydantic responses;
- system prompt, user prompt, call count, and response-model recording;
- missing fields, incorrect types, extra fields, and malformed JSON;
- fake timeout, rate-limit, and provider failures;
- environment configuration and factory selection;
- Gemini client initialization, configured model, system instruction, and user
  content;
- request timeout and retry configuration; and
- provider-neutral translation of authentication, timeout, rate-limit,
  transient, validation, and generic SDK failures.

Run the offline suite and static checks with:

```bash
pytest
ruff check .
mypy
```

The `live_llm` marker is excluded by the default Pytest configuration. A
developer may explicitly run one minimal real request after selecting an
available model:

```bash
export GEMINI_API_KEY=your-key
export GEMINI_MODEL=an-available-gemini-flash-model
pytest -m live_llm
```

The live test is optional, must remain outside standard CI, and must not assume
that any particular model has free-tier quota.

Parser- and proposal-specific validation such as required opportunity fields,
maximum content lengths, warning-sign lists, and invented-claim prevention
belongs to their later phases rather than the provider contract tests.

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
