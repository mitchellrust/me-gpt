"""Tests for provider adapters."""

import pytest
import respx
from httpx import Response

from agent.config import ProviderConfig
from agent.providers.anthropic import AnthropicProvider
from agent.providers.http_adapter import HTTPProvider
from agent.providers.openai import OpenAIProvider


@pytest.mark.asyncio
@respx.mock
async def test_openai_provider_complete(monkeypatch):
    """Test OpenAI provider completion."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    config = ProviderConfig(
        base_url="https://api.openai.com", api_key_env="OPENAI_API_KEY", model="gpt-4o-mini"
    )

    provider = OpenAIProvider(config)

    # Mock the API response
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=Response(
            200,
            json={
                "id": "test-123",
                "model": "gpt-4o-mini",
                "choices": [{"message": {"content": "Hello, world!"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )
    )

    result = await provider.complete("Test prompt")

    assert result.id == "test-123"
    assert result.text == "Hello, world!"
    assert result.model == "gpt-4o-mini"
    assert result.usage is not None
    assert result.usage.total_tokens == 15


@pytest.mark.asyncio
@respx.mock
async def test_anthropic_provider_complete(monkeypatch):
    """Test Anthropic provider completion."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    config = ProviderConfig(
        base_url="https://api.anthropic.com",
        api_key_env="ANTHROPIC_API_KEY",
        model="claude-3-haiku-20240307",
    )

    provider = AnthropicProvider(config)

    # Mock the API response
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=Response(
            200,
            json={
                "id": "test-456",
                "model": "claude-3-haiku-20240307",
                "content": [{"text": "Greetings!"}],
                "usage": {"input_tokens": 8, "output_tokens": 3},
            },
        )
    )

    result = await provider.complete("Test prompt")

    assert result.id == "test-456"
    assert result.text == "Greetings!"
    assert result.model == "claude-3-haiku-20240307"
    assert result.usage is not None
    assert result.usage.prompt_tokens == 8
    assert result.usage.completion_tokens == 3


@pytest.mark.asyncio
@respx.mock
async def test_http_provider_complete():
    """Test HTTP provider completion."""
    config = ProviderConfig(base_url="http://localhost:8080", model="local-model")

    provider = HTTPProvider(config)

    # Mock the API response
    respx.post("http://localhost:8080/v1/completions").mock(
        return_value=Response(
            200,
            json={
                "id": "local-789",
                "output": "Response from local MCP",
                "token_usage": {"prompt": 12, "completion": 8},
            },
        )
    )

    result = await provider.complete("Test prompt")

    assert result.id == "local-789"
    assert result.text == "Response from local MCP"
    assert result.model == "local-model"
    assert result.usage is not None
    assert result.usage.total_tokens == 20


@pytest.mark.asyncio
async def test_openai_provider_missing_api_key():
    """Test OpenAI provider raises error when API key missing."""
    config = ProviderConfig(base_url="https://api.openai.com", api_key_env="MISSING_KEY")

    with pytest.raises(ValueError, match="API key not found"):
        OpenAIProvider(config)


@pytest.mark.asyncio
async def test_anthropic_provider_missing_api_key():
    """Test Anthropic provider raises error when API key missing."""
    config = ProviderConfig(base_url="https://api.anthropic.com", api_key_env="MISSING_KEY")

    with pytest.raises(ValueError, match="API key not found"):
        AnthropicProvider(config)
