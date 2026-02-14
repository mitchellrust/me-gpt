"""Configuration management for the agent."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Configuration for a single provider."""

    base_url: str
    api_key_env: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    timeout: int = 60

    def get_api_key(self) -> Optional[str]:
        """Get API key from environment variable if specified."""
        if self.api_key_env:
            return os.getenv(self.api_key_env)
        return None


class AgentConfig(BaseModel):
    """Main agent configuration."""

    default_provider: str = "openai"
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict)

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the default config file path."""
        return Path.home() / ".config" / "agent" / "config.yaml"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "AgentConfig":
        """Load configuration from file with environment variable overrides."""
        if config_path is None:
            config_path = cls.get_config_path()

        if not config_path.exists():
            # Return default config if file doesn't exist
            return cls()

        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to file."""
        if config_path is None:
            config_path = self.get_config_path()

        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.safe_dump(self.model_dump(), f, default_flow_style=False)

    def get_provider(self, name: Optional[str] = None) -> Optional[ProviderConfig]:
        """Get provider config by name, falling back to default."""
        provider_name = name or self.default_provider
        return self.providers.get(provider_name)


def create_default_config() -> AgentConfig:
    """Create a default configuration with example providers."""
    return AgentConfig(
        default_provider="openai",
        providers={
            "openai": ProviderConfig(
                base_url="https://api.openai.com",
                api_key_env="OPENAI_API_KEY",
                model="gpt-4",
                max_tokens=1024,
            ),
            "anthropic": ProviderConfig(
                base_url="https://api.anthropic.com",
                api_key_env="ANTHROPIC_API_KEY",
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
            ),
            "local_mcp": ProviderConfig(
                base_url="http://localhost:8080",
                model="local-model",
                max_tokens=1024,
            ),
        },
    )
