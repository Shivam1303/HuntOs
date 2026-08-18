"""Construction boundary for selecting an LLM provider from settings."""

from core.config.settings import LLMSettings
from core.llm.base import LLMProvider
from core.llm.exceptions import LLMConfigurationError
from core.llm.fake import FakeLLMProvider
from core.llm.gemini import GeminiLLMProvider


def create_llm_provider(settings: LLMSettings) -> LLMProvider:
    """Create a new configured provider instance for dependency injection."""

    provider_name = settings.provider.casefold()
    if provider_name == "fake":
        return FakeLLMProvider()
    if provider_name == "gemini":
        if settings.gemini_api_key is None:
            raise LLMConfigurationError("GEMINI_API_KEY must be configured")
        if not settings.gemini_model:
            raise LLMConfigurationError("GEMINI_MODEL must be configured")
        return GeminiLLMProvider(
            api_key=settings.gemini_api_key.get_secret_value(),
            model=settings.gemini_model,
            timeout_seconds=settings.timeout_seconds,
            max_retries=settings.max_retries,
            max_output_tokens=settings.max_output_tokens,
            temperature=settings.temperature,
        )
    raise LLMConfigurationError(f"Unsupported LLM provider: {settings.provider!r}")
