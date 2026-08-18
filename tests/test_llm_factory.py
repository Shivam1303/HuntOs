"""Tests for environment-backed LLM configuration and provider selection."""

from unittest.mock import patch

import pytest
from pydantic import SecretStr, ValidationError

from core.config.settings import LLMSettings
from core.llm.base import LLMProvider
from core.llm.exceptions import LLMConfigurationError
from core.llm.factory import create_llm_provider
from core.llm.fake import FakeLLMProvider
from core.llm.gemini import GeminiLLMProvider


def test_llm_settings_read_environment_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-flash")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("LLM_MAX_RETRIES", "2")
    monkeypatch.setenv("LLM_MAX_OUTPUT_TOKENS", "512")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.1")

    settings = LLMSettings.from_env()

    assert settings.provider == "gemini"
    assert settings.gemini_api_key is not None
    assert settings.gemini_api_key.get_secret_value() == "test-key"
    assert settings.gemini_model == "gemini-test-flash"
    assert settings.timeout_seconds == 12.5
    assert settings.max_retries == 2
    assert settings.max_output_tokens == 512
    assert settings.temperature == 0.1


def test_llm_settings_reject_invalid_numeric_values() -> None:
    with pytest.raises(ValidationError):
        LLMSettings(timeout_seconds=0)


def test_factory_selects_fake_without_a_gemini_api_key() -> None:
    provider = create_llm_provider(LLMSettings(provider="fake"))

    assert isinstance(provider, FakeLLMProvider)
    assert isinstance(provider, LLMProvider)


def test_factory_selects_gemini_and_respects_the_configured_model() -> None:
    settings = LLMSettings(
        provider="gemini",
        gemini_api_key=SecretStr("test-key"),
        gemini_model="gemini-configured-flash",
        timeout_seconds=9,
        max_retries=1,
        max_output_tokens=321,
        temperature=0.3,
    )

    with patch("core.llm.gemini.genai.Client"):
        provider = create_llm_provider(settings)

    assert isinstance(provider, GeminiLLMProvider)
    assert isinstance(provider, LLMProvider)
    assert provider.model == "gemini-configured-flash"


@pytest.mark.parametrize(
    "settings",
    [
        LLMSettings(provider="gemini", gemini_model="gemini-test-flash"),
        LLMSettings(
            provider="gemini",
            gemini_api_key=SecretStr("test-key"),
            gemini_model="",
        ),
    ],
)
def test_factory_rejects_incomplete_gemini_configuration(
    settings: LLMSettings,
) -> None:
    with pytest.raises(LLMConfigurationError):
        create_llm_provider(settings)


def test_factory_rejects_an_unknown_provider() -> None:
    with pytest.raises(LLMConfigurationError, match="Unsupported LLM provider"):
        create_llm_provider(LLMSettings(provider="unknown"))
