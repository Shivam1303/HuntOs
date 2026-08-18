"""Optional minimal Gemini smoke test excluded from the standard suite."""

import asyncio
import os

import pytest

from core.llm.gemini import GeminiLLMProvider


@pytest.mark.live_llm
def test_live_gemini_text_generation() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")
    if not api_key or not model:
        pytest.skip("GEMINI_API_KEY and GEMINI_MODEL are required")

    provider = GeminiLLMProvider(
        api_key=api_key,
        model=model,
        timeout_seconds=30,
        max_retries=0,
        max_output_tokens=8,
        temperature=0,
    )

    async def generate_and_close() -> str:
        try:
            return await provider.generate_text(
                system_prompt="Reply with one word.",
                user_prompt="Reply with: ready",
            )
        finally:
            await provider.aclose()

    assert asyncio.run(generate_and_close()).strip()
