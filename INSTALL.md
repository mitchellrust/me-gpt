# Installation Guide

This guide covers different methods to install the `agent` CLI as a standalone executable.

## Prerequisites

- Homebrew (on MacOS) for pipx installation
- Python 3.14+
- Poetry (for development)

## Installation Methods

### Method 1: Install with pipx (Recommended)

`pipx` installs the CLI in an isolated environment and exposes it on your PATH.

```bash
# Install pipx if you don't have it
brew install pipx
pipx ensurepath

# Install agent from the repository
cd /path/to/me-gpt
pipx install .

# Verify installation
agent --help
```

**Advantages:**
- Clean, isolated environment
- No conflicts with system Python
- Easy to uninstall: `pipx uninstall agent`
- Automatic PATH management

### Method 2: Install with pip

```bash
# Install in development/editable mode (changes to code are reflected immediately)
pip install -e .

# Or install normally
pip install .

# Verify installation
agent --help
```

**Advantages:**
- Simple and familiar
- `-e` mode useful for development

**Disadvantages:**
- Installs into active Python environment (may conflict with other packages)
- Need to manage PATH yourself if using `--user`

### Method 3: Run via poetry (Development)

```bash
poetry install
poetry run agent --help
```

This is the standard development workflow and doesn't require any installation setup.

## Verifying Installation

After installation, test with:

```bash
# Show help
agent --help

# Test provider configuration
agent test

# One-off completion
agent call "What is 2+2?"

# Interactive chat
agent chat
```

## Package Entry Point

The package uses Poetry's scripts feature to define the CLI entry point:

```toml
[tool.poetry.scripts]
agent = "agent.cli:app"
```

This creates an executable wrapper that calls the `app` object in `agent/cli.py`.

## Troubleshooting

### Command not found

If `agent` is not found after installation:

- **pipx**: Run `pipx ensurepath` and restart your shell
- **pip --user**: Add `~/.local/bin` to PATH
- **symlink**: Ensure `/usr/local/bin` is on your PATH

### ImportError

If you see import errors when running `agent`:

- Ensure dependencies are installed: `poetry install` or `pip install -e .`
- Check that you're using the correct Python environment
- For the `bin/agent` shim, make sure you're in the poetry shell or have packages installed

## Uninstalling

```bash
# pipx
pipx uninstall agent

# pip
pip uninstall agent

# symlink
rm /usr/local/bin/agent
```
