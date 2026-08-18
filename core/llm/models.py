"""Small internal models shared by real and fake LLM providers."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class LLMRequestRecord(BaseModel):
    """Provider-neutral request details retained by test providers."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )

    kind: Literal["text", "structured"]
    system_prompt: str
    user_prompt: str
    response_model: type[BaseModel] | None = None
