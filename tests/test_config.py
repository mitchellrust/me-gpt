"""Tests for config module."""

import os
from pathlib import Path

import pytest

from agent.config import AgentConfig, ProviderConfig, create_default_config


def test_provider_config_get_api_key(monkeypatch):
    """Test getting API key from environment."""
    monkeypatch.setenv("TEST_API_KEY", "test-key-123")

    config = ProviderConfig(base_url="https://api.test.com", api_key_env="TEST_API_KEY")

    assert config.get_api_key() == "test-key-123"


def test_provider_config_no_api_key():
    """Test provider config without API key."""
    config = ProviderConfig(base_url="https://api.test.com")
    assert config.get_api_key() is None


def test_agent_config_get_provider():
    """Test getting provider config by name."""
    config = AgentConfig(
        default_provider="test",
        providers={
            "test": ProviderConfig(base_url="https://api.test.com"),
        },
    )

    provider = config.get_provider("test")
    assert provider is not None
    assert provider.base_url == "https://api.test.com"


def test_agent_config_get_default_provider():
    """Test getting default provider when name not specified."""
    config = AgentConfig(
        default_provider="test",
        providers={
            "test": ProviderConfig(base_url="https://api.test.com"),
        },
    )

    provider = config.get_provider()
    assert provider is not None
    assert provider.base_url == "https://api.test.com"


def test_agent_config_get_nonexistent_provider():
    """Test getting nonexistent provider returns None."""
    config = AgentConfig(providers={})
    assert config.get_provider("nonexistent") is None


def test_create_default_config():
    """Test creating default configuration."""
    config = create_default_config()

    assert config.default_provider == "openai"
    assert "openai" in config.providers
    assert "anthropic" in config.providers
    assert "local_mcp" in config.providers

    # Check OpenAI config
    openai = config.providers["openai"]
    assert "openai.com" in openai.base_url
    assert openai.api_key_env == "OPENAI_API_KEY"

    # Check Anthropic config
    anthropic = config.providers["anthropic"]
    assert "anthropic.com" in anthropic.base_url
    assert anthropic.api_key_env == "ANTHROPIC_API_KEY"

    # Check local MCP config
    local_mcp = config.providers["local_mcp"]
    assert "localhost" in local_mcp.base_url
    assert local_mcp.api_key_env is None


def test_agent_config_save_and_load(tmp_path):
    """Test saving and loading configuration."""
    config_path = tmp_path / "config.yaml"

    # Create and save config
    config = create_default_config()
    config.save(config_path)

    # Load config
    loaded = AgentConfig.load(config_path)

    assert loaded.default_provider == config.default_provider
    assert loaded.providers.keys() == config.providers.keys()
