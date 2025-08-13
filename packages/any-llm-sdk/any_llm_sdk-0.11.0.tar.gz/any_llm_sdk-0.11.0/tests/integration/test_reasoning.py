from typing import Any

import httpx
import pytest
from openai import APIConnectionError

from any_llm import ProviderName, completion
from any_llm.exceptions import MissingApiKeyError
from any_llm.provider import ProviderFactory
from any_llm.types.completion import ChatCompletion


def test_reasoning_providers(
    provider: ProviderName,
    provider_reasoning_model_map: dict[ProviderName, str],
    provider_extra_kwargs_map: dict[ProviderName, dict[str, Any]],
) -> None:
    """Test that all supported providers can be loaded successfully."""
    providers_metadata = ProviderFactory.get_all_provider_metadata()
    provider_metadata = next(metadata for metadata in providers_metadata if metadata["provider_key"] == provider.value)
    if not provider_metadata["reasoning"]:
        pytest.skip(f"{provider.value} does not support completion reasoning, skipping")
    model_id = provider_reasoning_model_map[provider]
    extra_kwargs = provider_extra_kwargs_map.get(provider, {})
    try:
        result = completion(
            f"{provider.value}/{model_id}",
            **extra_kwargs,
            messages=[{"role": "user", "content": "Please say hello! Think before you respond."}],
        )
    except MissingApiKeyError:
        pytest.skip(f"{provider.value} API key not provided, skipping")
    except (httpx.HTTPStatusError, httpx.ConnectError, APIConnectionError):
        if provider in [ProviderName.OLLAMA, ProviderName.LMSTUDIO]:
            pytest.skip("Local Model host is not set up, skipping")
        raise
    assert isinstance(result, ChatCompletion)
    assert result.choices[0].message.content is not None
    assert result.choices[0].message.reasoning is not None
    assert result.choices[0].message.reasoning.content is not None
