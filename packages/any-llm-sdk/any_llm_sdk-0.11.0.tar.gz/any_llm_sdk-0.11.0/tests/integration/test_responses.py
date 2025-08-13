from typing import Any

import httpx
import pytest
from openai import APIConnectionError

from any_llm import ProviderName, responses
from any_llm.exceptions import MissingApiKeyError
from any_llm.provider import ProviderFactory
from any_llm.types.responses import Response


def test_responses(
    provider: ProviderName,
    provider_reasoning_model_map: dict[ProviderName, str],
    provider_extra_kwargs_map: dict[ProviderName, dict[str, Any]],
) -> None:
    """Test that all supported providers can be loaded successfully."""
    providers_metadata = ProviderFactory.get_all_provider_metadata()
    provider_metadata = next(metadata for metadata in providers_metadata if metadata["provider_key"] == provider.value)
    if not provider_metadata["responses"]:
        pytest.skip(f"{provider.value} does not support responses, skipping")
    model_id = provider_reasoning_model_map[provider]
    extra_kwargs = provider_extra_kwargs_map.get(provider, {})
    try:
        result = responses(
            f"{provider.value}/{model_id}",
            **extra_kwargs,
            input_data="What's the capital of France? Please think step by step.",
        )
    except MissingApiKeyError:
        pytest.skip(f"{provider.value} API key not provided, skipping")
    except (httpx.HTTPStatusError, httpx.ConnectError, APIConnectionError):
        if provider in [ProviderName.OLLAMA, ProviderName.LMSTUDIO]:
            pytest.skip("Local Model host is not set up, skipping")
        raise
    assert isinstance(result, Response)
    assert result.output_text is not None
    assert result.reasoning is not None
