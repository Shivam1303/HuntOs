"""Unit tests for the deterministic provider-neutral LLM fake."""

import asyncio

import pytest
from pydantic import BaseModel, ConfigDict

from core.llm.exceptions import (
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseValidationError,
    LLMTimeoutError,
)
from core.llm.fake import FakeLLMProvider


class ExampleAnalysis(BaseModel):
    """Strict structured output used only to verify the LLM contract."""

    model_config = ConfigDict(extra="forbid", strict=True)

    summary: str
    confidence: float
    tags: list[str]


def test_fake_provider_returns_text_and_records_the_request() -> None:
    provider = FakeLLMProvider(text_responses=["A deterministic answer."])

    result = asyncio.run(
        provider.generate_text(
            system_prompt="Be concise.",
            user_prompt="Summarize this opportunity.",
        )
    )

    assert result == "A deterministic answer."
    assert provider.call_count == 1
    assert provider.requests[0].system_prompt == "Be concise."
    assert provider.requests[0].user_prompt == "Summarize this opportunity."
    assert provider.requests[0].response_model is None


def test_fake_provider_returns_validated_structured_output() -> None:
    provider = FakeLLMProvider(
        structured_responses=[
            {
                "summary": "Strong API fit.",
                "confidence": 0.9,
                "tags": ["python", "api"],
            }
        ]
    )

    result = asyncio.run(
        provider.generate_structured(
            system_prompt="Return an analysis.",
            user_prompt="Analyze this text.",
            response_model=ExampleAnalysis,
        )
    )

    assert result == ExampleAnalysis(
        summary="Strong API fit.",
        confidence=0.9,
        tags=["python", "api"],
    )
    assert provider.call_count == 1
    assert provider.requests[0].response_model is ExampleAnalysis


@pytest.mark.parametrize(
    "response",
    [
        {"summary": "Missing fields."},
        {"summary": "Wrong type.", "confidence": "high", "tags": ["api"]},
        {
            "summary": "Unexpected field.",
            "confidence": 0.8,
            "tags": ["api"],
            "score": 10,
        },
        "{not valid json",
    ],
)
def test_fake_provider_rejects_malformed_structured_output(response: object) -> None:
    provider = FakeLLMProvider(structured_responses=[response])

    with pytest.raises(LLMResponseValidationError):
        asyncio.run(
            provider.generate_structured(
                system_prompt="Return an analysis.",
                user_prompt="Analyze this text.",
                response_model=ExampleAnalysis,
            )
        )


@pytest.mark.parametrize(
    ("failure", "expected_exception"),
    [
        ("timeout", LLMTimeoutError),
        ("rate_limit", LLMRateLimitError),
        ("provider", LLMProviderError),
    ],
)
def test_fake_provider_simulates_failures(
    failure: str, expected_exception: type[Exception]
) -> None:
    provider = FakeLLMProvider(failure=failure)

    with pytest.raises(expected_exception):
        asyncio.run(
            provider.generate_text(
                system_prompt="Be concise.",
                user_prompt="Summarize this opportunity.",
            )
        )

    assert provider.call_count == 1
