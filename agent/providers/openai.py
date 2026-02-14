"""OpenAI provider adapter."""

import logging
from typing import Optional

import httpx

from agent.config import ProviderConfig
from agent.providers.base import CompletionResult, TokenUsage

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """OpenAI API provider adapter."""

    def __init__(self, config: ProviderConfig):
        """Initialize the OpenAI provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.api_key = config.get_api_key()
        if not self.api_key:
            raise ValueError(
                f"API key not found. Set environment variable: {config.api_key_env}"
            )

    async def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> CompletionResult:
        """Complete a prompt using OpenAI API.

        Args:
            prompt: The prompt text
            model: Optional model override
            max_tokens: Optional max tokens override
            temperature: Optional temperature override

        Returns:
            CompletionResult with the completion
        """
        url = f"{self.config.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model or self.config.model or "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or self.config.max_tokens or 1024,
        }

        if temperature is not None:
            payload["temperature"] = temperature

        logger.debug(f"Calling OpenAI API: {url}")

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        # Extract completion text
        text = data["choices"][0]["message"]["content"]

        # Extract usage information
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return CompletionResult(
            id=data["id"],
            text=text,
            model=data["model"],
            usage=usage,
        )
