# Quick Start Guide

This guide will help you get started with the Agent CLI quickly.

## Installation

1. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

   Or using pip:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

2. Set up your API keys:
   ```bash
   export OPENAI_API_KEY="sk-..."
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. Initialize the configuration:
   ```bash
   poetry run agent init
   ```

## Basic Usage

### One-off completion

Ask a quick question:
```bash
poetry run agent call --provider openai --prompt "Write a haiku about Python"
```

### Interactive chat

Start a conversation:
```bash
poetry run agent chat --provider openai
```

Type your messages and press Enter. Use `exit` or Ctrl+C to quit.

### Test providers

Check that all providers are working:
```bash
poetry run agent test
```

## Using the Mock MCP Server

1. Start the mock server:
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

   Or run directly:
   ```bash
   cd dev/mock_mcp
   pip install -r requirements.txt
   python server.py
   ```

2. Test it:
   ```bash
   poetry run agent call --provider local_mcp --prompt "Hello MCP!"
   ```

## Running Tests

```bash
poetry run pytest
```

Or with coverage:
```bash
poetry run pytest --cov=agent --cov-report=html
```

## Project Structure

```
agent/
├── agent/              # Main package
│   ├── cli.py         # CLI commands
│   ├── config.py      # Configuration management
│   ├── session.py     # Session/conversation management
│   └── providers/     # Provider adapters
│       ├── base.py
│       ├── openai.py
│       ├── anthropic.py
│       └── http_adapter.py
├── tests/             # Test suite
├── dev/               # Development tools
│   ├── mock_mcp/      # Mock MCP server
│   └── config.example.yaml
└── docker-compose.dev.yml
```

## Configuration

The config file is located at `~/.config/agent/config.yaml`. Example:

```yaml
default_provider: openai
providers:
  openai:
    base_url: https://api.openai.com
    api_key_env: OPENAI_API_KEY
    model: gpt-4o-mini
    max_tokens: 1024
  anthropic:
    base_url: https://api.anthropic.com
    api_key_env: ANTHROPIC_API_KEY
    model: claude-3-haiku-20240307
    max_tokens: 1024
  local_mcp:
    base_url: http://localhost:8080
    model: local-model
    max_tokens: 1024
```

## Tips

- Use `--help` on any command to see available options:
  ```bash
  poetry run agent --help
  poetry run agent call --help
  ```

- Override the default model:
  ```bash
  poetry run agent call --provider openai --model gpt-3.5-turbo --prompt "Hello"
  ```

- Set a custom config path:
  ```bash
  poetry run agent call --config /path/to/config.yaml --prompt "Hello"
  ```
