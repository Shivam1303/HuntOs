"""Gemini implementation isolated behind the provider-neutral LLM contract."""

from typing import TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from core.llm.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseValidationError,
    LLMTimeoutError,
    LLMTransientError,
)

ResponseT = TypeVar("ResponseT", bound=BaseModel)

_TRANSIENT_STATUS_CODES = [408, 429, 500, 502, 503, 504]
_AUTHENTICATION_STATUS_CODES = {401, 403}


class GeminiLLMProvider:
    """Asynchronous Google Gen AI SDK adapter with internal error translation."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        max_output_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> None:
        if not api_key.strip():
            raise LLMConfigurationError("GEMINI_API_KEY must be configured")
        if not model.strip():
            raise LLMConfigurationError("GEMINI_MODEL must be configured")
        if timeout_seconds <= 0:
            raise LLMConfigurationError("LLM timeout must be greater than zero")
        if max_retries < 0:
            raise LLMConfigurationError("LLM retries cannot be negative")
        if max_output_tokens <= 0:
            raise LLMConfigurationError(
                "LLM maximum output tokens must be greater than zero"
            )
        if not 0 <= temperature <= 2:
            raise LLMConfigurationError("LLM temperature must be between 0 and 2")

        self._model = model
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature
        retry_options = types.HttpRetryOptions(
            attempts=max_retries + 1,
            initial_delay=1.0,
            max_delay=8.0,
            exp_base=2.0,
            jitter=0.2,
            http_status_codes=_TRANSIENT_STATUS_CODES,
        )
        http_options = types.HttpOptions(
            timeout=round(timeout_seconds * 1000),
            retry_options=retry_options,
        )
        try:
            self._client = genai.Client(
                api_key=api_key,
                http_options=http_options,
            )
        except Exception as error:
            raise LLMConfigurationError(
                "Gemini client initialization failed"
            ) from error

    @property
    def model(self) -> str:
        """Return the configured model identifier without exposing credentials."""

        return self._model

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Generate plain text through the asynchronous SDK client."""

        config = self._generation_config(system_prompt=system_prompt)
        response = await self._generate(user_prompt=user_prompt, config=config)
        text = response.text
        if not text:
            raise LLMProviderError(f"Gemini returned no text (model={self._model})")
        return text

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ResponseT],
    ) -> ResponseT:
        """Generate JSON with an SDK schema and validate it in the application."""

        config = self._generation_config(
            system_prompt=system_prompt,
            response_model=response_model,
        )
        response = await self._generate(user_prompt=user_prompt, config=config)
        try:
            if response.parsed is not None:
                parsed = response.parsed
                if isinstance(parsed, BaseModel):
                    return response_model.model_validate(parsed.model_dump())
                return response_model.model_validate(parsed)
            if not response.text:
                raise ValueError("structured response contained no data")
            return response_model.model_validate_json(response.text)
        except (ValidationError, ValueError, TypeError) as error:
            raise LLMResponseValidationError(
                f"Gemini output failed {response_model.__name__} validation "
                f"(model={self._model})"
            ) from error

    async def aclose(self) -> None:
        """Release sync and async HTTP resources owned by the SDK client."""

        await self._client.aio.aclose()
        self._client.close()

    def _generation_config(
        self,
        *,
        system_prompt: str,
        response_model: type[BaseModel] | None = None,
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=self._max_output_tokens,
            temperature=self._temperature,
            response_mime_type=(
                "application/json" if response_model is not None else None
            ),
            response_schema=response_model,
        )

    async def _generate(
        self,
        *,
        user_prompt: str,
        config: types.GenerateContentConfig,
    ) -> types.GenerateContentResponse:
        try:
            return await self._client.aio.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=config,
            )
        except errors.APIError as error:
            raise self._translate_api_error(error) from error
        except (TimeoutError, httpx.TimeoutException) as error:
            raise LLMTimeoutError(
                f"Gemini request timed out (model={self._model})"
            ) from error
        except httpx.NetworkError as error:
            raise LLMTransientError(
                f"Gemini network request failed (model={self._model})"
            ) from error
        except Exception as error:
            raise LLMProviderError(
                "Gemini provider request failed "
                f"(model={self._model}, error_type={type(error).__name__})"
            ) from error

    def _translate_api_error(self, error: errors.APIError) -> LLMProviderError:
        status_code = error.code
        context = f"status={status_code}, model={self._model}"
        if status_code in _AUTHENTICATION_STATUS_CODES:
            return LLMAuthenticationError(f"Gemini authentication failed ({context})")
        if status_code == 408:
            return LLMTimeoutError(f"Gemini request timed out ({context})")
        if status_code == 429:
            return LLMRateLimitError(f"Gemini rate limit exceeded ({context})")
        if status_code is not None and 500 <= status_code < 600:
            return LLMTransientError(f"Gemini transient service failure ({context})")
        return LLMProviderError(f"Gemini request was rejected ({context})")
