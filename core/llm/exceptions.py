"""Provider-neutral exceptions exposed by the shared LLM layer."""


class LLMError(Exception):
    """Base exception for every LLM-layer failure."""


class LLMConfigurationError(LLMError):
    """LLM provider settings are missing or invalid."""


class LLMProviderError(LLMError):
    """The selected provider failed permanently or unexpectedly."""


class LLMAuthenticationError(LLMProviderError):
    """The provider rejected configured credentials or access."""


class LLMTimeoutError(LLMProviderError):
    """The provider request exceeded its configured timeout."""


class LLMRateLimitError(LLMProviderError):
    """The provider rejected a request because of rate limits."""


class LLMTransientError(LLMProviderError):
    """A temporary provider or network failure remained after retries."""


class LLMResponseValidationError(LLMError):
    """Structured provider output did not satisfy the requested schema."""
