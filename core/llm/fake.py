"""Deterministic provider for unit and integration tests."""

from collections import deque
from collections.abc import Iterable
from typing import Literal, TypeVar

from pydantic import BaseModel, ValidationError

from core.llm.exceptions import (
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseValidationError,
    LLMTimeoutError,
)
from core.llm.models import LLMRequestRecord

ResponseT = TypeVar("ResponseT", bound=BaseModel)
FailureMode = Literal["timeout", "rate_limit", "provider"]


class FakeLLMProvider:
    """Return predefined responses and record every request deterministically."""

    def __init__(
        self,
        *,
        text_responses: Iterable[str] = (),
        structured_responses: Iterable[object] = (),
        failure: FailureMode | None = None,
    ) -> None:
        if failure not in (None, "timeout", "rate_limit", "provider"):
            raise ValueError(f"Unsupported fake LLM failure mode: {failure}")
        self._text_responses = deque(text_responses)
        self._structured_responses = deque(structured_responses)
        self._failure = failure
        self.requests: list[LLMRequestRecord] = []

    @property
    def call_count(self) -> int:
        """Return the number of generation calls made."""

        return len(self.requests)

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Return the next predefined plain-text response."""

        self.requests.append(
            LLMRequestRecord(
                kind="text",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        )
        self._raise_simulated_failure()
        if not self._text_responses:
            raise LLMProviderError("Fake LLM has no text response configured")
        return self._text_responses.popleft()

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ResponseT],
    ) -> ResponseT:
        """Return the next predefined response after Pydantic validation."""

        self.requests.append(
            LLMRequestRecord(
                kind="structured",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=response_model,
            )
        )
        self._raise_simulated_failure()
        if not self._structured_responses:
            raise LLMProviderError("Fake LLM has no structured response configured")

        response = self._structured_responses.popleft()
        try:
            if isinstance(response, str):
                return response_model.model_validate_json(response)
            if isinstance(response, BaseModel):
                return response_model.model_validate(response.model_dump())
            return response_model.model_validate(response)
        except (ValidationError, ValueError, TypeError) as error:
            raise LLMResponseValidationError(
                f"Fake LLM output failed {response_model.__name__} validation"
            ) from error

    def _raise_simulated_failure(self) -> None:
        if self._failure == "timeout":
            raise LLMTimeoutError("Fake LLM request timed out")
        if self._failure == "rate_limit":
            raise LLMRateLimitError("Fake LLM rate limit simulated")
        if self._failure == "provider":
            raise LLMProviderError("Fake LLM provider failure simulated")
