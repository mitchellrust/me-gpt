# Agent Development Guide

This document provides guidelines for AI coding agents working in this repository.

## Project Overview

A minimal LLM agent CLI for OpenAI, Anthropic, and containerized MCP servers. Built with Python 3.11+, Poetry, Typer, and httpx.

## Build, Lint, and Test Commands

### Setup
```bash
poetry install                    # Install dependencies
poetry shell                      # Activate virtual environment
```

### Running Tests
```bash
poetry run pytest                                               # Run all tests
poetry run pytest tests/test_providers.py                       # Single test file
poetry run pytest tests/test_providers.py::test_openai_provider_complete  # Specific test
poetry run pytest --cov=agent --cov-report=html                 # With coverage
poetry run pytest -v                                            # Verbose output
poetry run pytest -k "openai"                                   # Match pattern
```

### Linting and Formatting
```bash
poetry run black agent/ tests/        # Format code
poetry run black --check agent/ tests/  # Check formatting
poetry run ruff agent/ tests/         # Lint
poetry run ruff --fix agent/ tests/   # Fix issues
```

### Running the Application
```bash
poetry run agent init                                    # Initialize config
poetry run agent call --provider openai --prompt "..."   # One-off completion
poetry run agent chat --provider openai                  # Interactive chat
poetry run agent test                                    # Test all providers
```

### Development Server
```bash
docker compose -f docker-compose.dev.yml up --build  # Run mock MCP server
```

## Code Style Guidelines

### Formatting
- **Line length**: 100 characters (black/ruff)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings

### Imports
Order: standard library → third-party → local. Alphabetically sorted within groups.

```python
import logging
from pathlib import Path
from typing import Optional

import httpx
from pydantic import BaseModel

from agent.config import ProviderConfig
from agent.providers.base import CompletionResult
```

### Type Hints
Always use type hints. Use `Optional[T]` for nullable types, `-> None` for no return value.

```python
async def complete(
    self,
    prompt: str,
    *,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> CompletionResult:
    """Complete a prompt with the LLM."""
    ...
```

### Naming Conventions
- **Classes**: PascalCase (`OpenAIProvider`, `TokenUsage`)
- **Functions/methods**: snake_case (`get_provider`, `add_user_message`)
- **Variables**: snake_case (`api_key`, `provider_name`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_MODEL`)
- **Private**: prefix with `_` (`_call`, `_chat`)

### Docstrings
Use Google-style docstrings for all public modules, classes, and functions.

```python
def get_provider(self, name: Optional[str] = None) -> Optional[ProviderConfig]:
    """Get provider config by name, falling back to default.
    
    Args:
        name: Provider name to retrieve. If None, uses default_provider.
        
    Returns:
        ProviderConfig if found, None otherwise.
    """
    ...
```

### Error Handling
- Use specific exception types (`ValueError`, `TypeError`, `KeyError`)
- Raise with descriptive messages
- Use `raise ... from e` to preserve chains
- Use `logging` module, never `print()`
- Handle httpx exceptions with `raise_for_status()`

```python
if not self.api_key:
    raise ValueError(
        f"API key not found. Set environment variable: {config.api_key_env}"
    )
```

### Async/Await
- Use `async def` for all I/O-bound operations
- Use `asyncio.run()` from sync contexts
- Mark async tests with `@pytest.mark.asyncio`

### Data Classes
- Use Pydantic `BaseModel` for config and validation
- Use `@dataclass` for simple data containers
- Prefer immutability (`frozen=True`)

### Testing
- Mirror package structure in `tests/`
- Prefix test files and functions with `test_`
- Use descriptive names
- Mock API calls with `respx`
- Test success and failure cases

```python
@pytest.mark.asyncio
@respx.mock
async def test_openai_provider_complete(monkeypatch):
    """Test OpenAI provider completion."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # Mock and assertions...
```

## Project Structure
```
agent/
├── agent/              # Main package
│   ├── cli.py         # CLI commands (Typer app)
│   ├── config.py      # Configuration management
│   ├── session.py     # Conversation session management
│   └── providers/     # Provider adapters
│       ├── base.py         # Protocol and data models
│       ├── openai.py       # OpenAI adapter
│       ├── anthropic.py    # Anthropic adapter
│       └── http_adapter.py # Generic HTTP/MCP adapter
├── tests/             # Test suite
├── dev/               # Development tools
│   └── mock_mcp/      # Mock MCP server
└── pyproject.toml     # Poetry configuration
```

## Key Dependencies
- **typer**: CLI framework
- **httpx**: Async HTTP client
- **pydantic**: Data validation
- **rich**: Terminal UI and formatting
- **pytest**: Testing framework
- **respx**: HTTP mocking for tests
- **black**: Code formatter
- **ruff**: Linter

## Configuration
- Config file: `~/.config/agent/config.yaml`
- API keys stored in environment variables
- Use `ProviderConfig` for provider-specific settings
- Support for multiple providers (OpenAI, Anthropic, HTTP/MCP)
