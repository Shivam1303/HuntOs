"""Provider-neutral contract used by application and business layers."""

from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

ResponseT = TypeVar("ResponseT", bound=BaseModel)


@runtime_checkable
class LLMProvider(Protocol):
    """Minimal asynchronous text and structured-generation interface."""

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Generate plain text from system and user instructions."""

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ResponseT],
    ) -> ResponseT:
        """Generate and validate output against a requested Pydantic model."""
