"""Base provider interface and data models."""

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class TokenUsage:
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class CompletionResult:
    """Result from a completion request."""

    id: str
    text: str
    model: str
    usage: Optional[TokenUsage] = None


class Provider(Protocol):
    """Protocol for LLM providers."""

    async def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> CompletionResult:
        """Complete a prompt with the LLM.

        Args:
            prompt: The prompt text
            model: Optional model override
            max_tokens: Optional max tokens override
            temperature: Optional temperature override

        Returns:
            CompletionResult with the completion
        """
        ...
