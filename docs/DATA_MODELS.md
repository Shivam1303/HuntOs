# Data Models

## DeveloperProfile

```python
class DeveloperProfile(BaseModel):
    name: str
    headline: str
    skills: list[str]
    preferred_project_types: list[str]
    preferred_industries: list[str]
    minimum_budget: float | None
    hourly_rate: float | None
    portfolio_items: list[str]
    prohibited_claims: list[str] = []
```

## RawOpportunity

```python
class RawOpportunity(BaseModel):
    source_id: str | None
    platform: str
    title: str
    description: str
    budget_min: float | None
    budget_max: float | None
    client_name: str | None
    client_history: str | None
    proposal_count: int | None
    posted_at: datetime | None
    url: str | None
```

## ParsedOpportunity

```python
class ParsedOpportunity(BaseModel):
    required_skills: list[str]
    business_problem: str
    expected_deliverables: list[str]
    experience_level: str | None
    warning_signs: list[str]
    missing_information: list[str]
    clarification_questions: list[str]
```

## OpportunityScore

```python
class OpportunityScore(BaseModel):
    total: int
    skill_match: int
    budget_quality: int
    requirement_clarity: int
    client_quality: int
    portfolio_relevance: int
    repeat_work_potential: int
    competition: int
    penalties: int
    explanation: list[str]
```

## ProposalDraft

```python
class ProposalDraft(BaseModel):
    client_problem_summary: str
    proposed_solution: str
    relevant_evidence: list[str]
    questions: list[str]
    proposal_text: str
    requires_human_approval: bool = True
```
