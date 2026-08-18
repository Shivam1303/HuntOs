"""Gemini adapter tests with the Google SDK fully mocked."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from pydantic import BaseModel, ConfigDict

from core.llm.exceptions import (
    LLMAuthenticationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseValidationError,
    LLMTimeoutError,
    LLMTransientError,
)
from core.llm.gemini import GeminiLLMProvider


class ExampleAnalysis(BaseModel):
    """Strict contract proving application-side Pydantic validation."""

    model_config = ConfigDict(extra="forbid", strict=True)

    summary: str
    confidence: float
    tags: list[str]


class FakeGeminiAPIError(Exception):
    """Minimal SDK-shaped API exception for stable mapping tests."""

    def __init__(self, code: int, message: str = "SDK request failed") -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _mock_client(response: object) -> tuple[MagicMock, AsyncMock]:
    client = MagicMock()
    generate_content = AsyncMock(return_value=response)
    client.aio.models.generate_content = generate_content
    return client, generate_content


def test_gemini_initializes_one_client_with_timeout_and_transient_retries() -> None:
    client, generate_content = _mock_client(SimpleNamespace(text="A concise response."))

    with patch("core.llm.gemini.genai.Client", return_value=client) as client_type:
        provider = GeminiLLMProvider(
            api_key="test-key",
            model="gemini-test-flash",
            timeout_seconds=7.5,
            max_retries=2,
            max_output_tokens=456,
            temperature=0.25,
        )
        first = asyncio.run(
            provider.generate_text(
                system_prompt="Be concise.",
                user_prompt="First request.",
            )
        )
        second = asyncio.run(
            provider.generate_text(
                system_prompt="Be concise.",
                user_prompt="Second request.",
            )
        )

    assert first == "A concise response."
    assert second == "A concise response."
    client_type.assert_called_once()
    initialization = client_type.call_args.kwargs
    assert initialization["api_key"] == "test-key"
    http_options = initialization["http_options"]
    assert http_options.timeout == 7500
    assert http_options.retry_options.attempts == 3
    assert http_options.retry_options.http_status_codes == [
        408,
        429,
        500,
        502,
        503,
        504,
    ]
    assert generate_content.await_count == 2


def test_gemini_passes_model_prompts_and_generation_configuration() -> None:
    client, generate_content = _mock_client(SimpleNamespace(text="Generated text."))

    with patch("core.llm.gemini.genai.Client", return_value=client):
        provider = GeminiLLMProvider(
            api_key="test-key",
            model="gemini-configured-flash",
            timeout_seconds=30,
            max_retries=0,
            max_output_tokens=777,
            temperature=0.4,
        )
        result = asyncio.run(
            provider.generate_text(
                system_prompt="Follow the system instruction.",
                user_prompt="Use this user input.",
            )
        )

    assert result == "Generated text."
    call = generate_content.await_args
    assert call is not None
    assert call.kwargs["model"] == "gemini-configured-flash"
    assert call.kwargs["contents"] == "Use this user input."
    config = call.kwargs["config"]
    assert config.system_instruction == "Follow the system instruction."
    assert config.max_output_tokens == 777
    assert config.temperature == 0.4
    assert config.response_mime_type is None


def test_gemini_requests_and_validates_structured_output() -> None:
    client, generate_content = _mock_client(
        SimpleNamespace(
            parsed={
                "summary": "Strong fit.",
                "confidence": 0.95,
                "tags": ["python"],
            },
            text='{"summary":"Strong fit.","confidence":0.95,"tags":["python"]}',
        )
    )

    with patch("core.llm.gemini.genai.Client", return_value=client):
        provider = GeminiLLMProvider(
            api_key="test-key",
            model="gemini-test-flash",
        )
        result = asyncio.run(
            provider.generate_structured(
                system_prompt="Return structured analysis.",
                user_prompt="Analyze this text.",
                response_model=ExampleAnalysis,
            )
        )

    assert result.summary == "Strong fit."
    call = generate_content.await_args
    assert call is not None
    config = call.kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_schema is ExampleAnalysis


@pytest.mark.parametrize(
    "response",
    [
        SimpleNamespace(parsed=None, text='{"summary":"Missing fields."}'),
        SimpleNamespace(
            parsed=None,
            text='{"summary":"Wrong type.","confidence":"high","tags":["api"]}',
        ),
        SimpleNamespace(
            parsed=None,
            text=(
                '{"summary":"Extra field.","confidence":0.7,"tags":["api"],"score":5}'
            ),
        ),
        SimpleNamespace(parsed=None, text="{not valid json"),
    ],
)
def test_gemini_translates_invalid_structured_output(response: object) -> None:
    client, _ = _mock_client(response)

    with patch("core.llm.gemini.genai.Client", return_value=client):
        provider = GeminiLLMProvider(
            api_key="test-key",
            model="gemini-test-flash",
        )
        with pytest.raises(LLMResponseValidationError):
            asyncio.run(
                provider.generate_structured(
                    system_prompt="Return structured analysis.",
                    user_prompt="Analyze this text.",
                    response_model=ExampleAnalysis,
                )
            )


@pytest.mark.parametrize(
    ("code", "expected_exception"),
    [
        (401, LLMAuthenticationError),
        (403, LLMAuthenticationError),
        (408, LLMTimeoutError),
        (429, LLMRateLimitError),
        (500, LLMTransientError),
        (503, LLMTransientError),
        (400, LLMProviderError),
        (404, LLMProviderError),
    ],
)
def test_gemini_translates_sdk_api_errors(
    code: int, expected_exception: type[Exception]
) -> None:
    client, generate_content = _mock_client(SimpleNamespace(text="unused"))
    generate_content.side_effect = FakeGeminiAPIError(code)

    with (
        patch("core.llm.gemini.genai.Client", return_value=client),
        patch("core.llm.gemini.errors.APIError", FakeGeminiAPIError),
    ):
        provider = GeminiLLMProvider(
            api_key="test-key",
            model="gemini-test-flash",
        )
        with pytest.raises(expected_exception):
            asyncio.run(
                provider.generate_text(
                    system_prompt="Be concise.",
                    user_prompt="Generate text.",
                )
            )


@pytest.mark.parametrize(
    ("sdk_exception", "expected_exception"),
    [
        (TimeoutError("request timed out"), LLMTimeoutError),
        (httpx.ReadTimeout("read timed out"), LLMTimeoutError),
        (httpx.ConnectError("connection failed"), LLMTransientError),
        (RuntimeError("unexpected SDK failure"), LLMProviderError),
    ],
)
def test_gemini_translates_non_api_sdk_errors(
    sdk_exception: Exception, expected_exception: type[Exception]
) -> None:
    client, generate_content = _mock_client(SimpleNamespace(text="unused"))
    generate_content.side_effect = sdk_exception

    with patch("core.llm.gemini.genai.Client", return_value=client):
        provider = GeminiLLMProvider(
            api_key="test-key",
            model="gemini-test-flash",
        )
        with pytest.raises(expected_exception):
            asyncio.run(
                provider.generate_text(
                    system_prompt="Be concise.",
                    user_prompt="Generate text.",
                )
            )
