# Agent

A minimal LLM agent CLI for OpenAI, Anthropic, and containerized MCP servers.

## Features

- Provider adapters for OpenAI, Anthropic, and generic HTTP (MCP servers)
- Terminal-first CLI with REPL chat and one-off calls
- Simple YAML + environment variable configuration
- In-memory conversation history
- Testable with local mock MCP servers

## Installation

### Using Poetry (recommended)

```bash
poetry install
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Configuration

Create a config file at `~/.config/agent/config.yaml`:

```yaml
default_provider: openai
providers:
  openai:
    base_url: https://api.openai.com
    api_key_env: OPENAI_API_KEY
  anthropic:
    base_url: https://api.anthropic.com
    api_key_env: ANTHROPIC_API_KEY
  local_mcp:
    base_url: http://localhost:8080
```

Set your API keys as environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### Initialize configuration

```bash
agent init
```

### One-off completion

```bash
agent call --provider openai --prompt "Write a haiku about code"
```

### Interactive chat (REPL)

```bash
agent chat --provider openai
```

Type your messages and press Enter. Use `exit` or Ctrl+C to quit.

### Test providers

```bash
agent test
```

## Development

### Running the mock MCP server

```bash
docker compose -f docker-compose.dev.yml up --build
```

Or run directly:

```bash
cd dev/mock_mcp
poetry run uvicorn server:app --reload --port 8080
```

### Running tests

```bash
poetry run pytest
```

## MCP Server HTTP Contract

Your containerized MCP servers should implement:

**Request:** POST `/v1/completions`

```json
{
  "model": "gpt-like",
  "input": "prompt text",
  "max_tokens": 256,
  "stream": false
}
```

**Response:**

```json
{
  "id": "completion-id",
  "output": "response text",
  "token_usage": {
    "prompt": 10,
    "completion": 20
  }
}
```

## License

MIT
