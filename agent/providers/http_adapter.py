"""Generic HTTP adapter for MCP servers."""

import logging
from typing import Optional

import httpx

from agent.config import ProviderConfig
from agent.providers.base import CompletionResult, TokenUsage

logger = logging.getLogger(__name__)


class HTTPProvider:
    """Generic HTTP provider adapter for MCP servers."""

    def __init__(self, config: ProviderConfig):
        """Initialize the HTTP provider.

        Args:
            config: Provider configuration
        """
        self.config = config

    async def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> CompletionResult:
        """Complete a prompt using a generic HTTP MCP server.

        Args:
            prompt: The prompt text
            model: Optional model override
            max_tokens: Optional max tokens override
            temperature: Optional temperature override

        Returns:
            CompletionResult with the completion
        """
        url = f"{self.config.base_url}/v1/completions"
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": model or self.config.model or "default",
            "input": prompt,
            "max_tokens": max_tokens or self.config.max_tokens or 1024,
            "stream": False,
        }

        if temperature is not None:
            payload["temperature"] = temperature

        logger.debug(f"Calling MCP HTTP API: {url}")

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        # Extract completion text (MCP servers return 'output' field)
        text = data.get("output", "")

        # Extract usage information if available
        usage_data = data.get("token_usage", {})
        usage = None
        if usage_data:
            usage = TokenUsage(
                prompt_tokens=usage_data.get("prompt", 0),
                completion_tokens=usage_data.get("completion", 0),
                total_tokens=usage_data.get("prompt", 0) + usage_data.get("completion", 0),
            )

        return CompletionResult(
            id=data.get("id", "unknown"),
            text=text,
            model=payload["model"],
            usage=usage,
        )
