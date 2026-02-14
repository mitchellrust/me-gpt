"""CLI for the agent."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import Prompt

from agent.config import AgentConfig, create_default_config
from agent.providers.anthropic import AnthropicProvider
from agent.providers.base import Provider
from agent.providers.http_adapter import HTTPProvider
from agent.providers.openai import OpenAIProvider
from agent.session import Session

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(
    name="me-gpt",
    help="A minimal LLM agent CLI for OpenAI, Anthropic, and containerized MCP servers",
)
console = Console()


def get_provider(provider_name: str, config: AgentConfig) -> Provider:
    """Get a provider instance by name.

    Args:
        provider_name: Name of the provider
        config: Agent configuration

    Returns:
        Provider instance

    Raises:
        ValueError: If provider not found or not configured
    """
    provider_config = config.get_provider(provider_name)
    if not provider_config:
        raise ValueError(
            f"Provider '{provider_name}' not found in config. "
            f"Available: {', '.join(config.providers.keys())}"
        )

    # Determine provider type based on configuration
    base_url = provider_config.base_url.lower()

    if "openai.com" in base_url:
        return OpenAIProvider(provider_config)
    elif "anthropic.com" in base_url:
        return AnthropicProvider(provider_config)
    else:
        # Assume it's a generic HTTP/MCP server
        return HTTPProvider(provider_config)


@app.command()
def init(
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Config file path (default: ~/.config/me-gpt/config.yaml)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
):
    """Initialize agent configuration file."""
    if config_path is None:
        config_path = AgentConfig.get_config_path()

    if config_path.exists() and not force:
        console.print(f"[yellow]Config already exists at: {config_path}[/yellow]")
        console.print("Use --force to overwrite")
        return

    config = create_default_config()
    config.save(config_path)
    console.print(f"[green]Config created at: {config_path}[/green]")
    console.print("\nDon't forget to set your API keys:")
    console.print("  export OPENAI_API_KEY='sk-...'")
    console.print("  export ANTHROPIC_API_KEY='sk-ant-...'")


@app.command()
def call(
    prompt: str = typer.Argument(..., help="The prompt to send"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider to use"),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Config file path (default: ~/.config/me-gpt/config.yaml)"
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model override"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Max tokens override"),
):
    """Make a one-off completion call."""
    asyncio.run(_call(prompt, provider, config_path, model, max_tokens))


async def _call(
    prompt: str,
    provider_name: Optional[str],
    config_path: Optional[Path],
    model: Optional[str],
    max_tokens: Optional[int],
):
    """Async implementation of call command."""
    try:
        config = AgentConfig.load(config_path)
        provider_name = provider_name or config.default_provider
        provider = get_provider(provider_name, config)

        console.print(f"\n[dim]Using provider: {provider_name}[/dim]")
        console.print(f"[dim]Prompt: {prompt}[/dim]\n")

        with console.status("[bold green]Thinking..."):
            result = await provider.complete(prompt, model=model, max_tokens=max_tokens)

        console.print(Panel(result.text, title="Response", border_style="green"))

        if result.usage:
            console.print(
                f"\n[dim]Tokens: {result.usage.prompt_tokens} prompt + "
                f"{result.usage.completion_tokens} completion = "
                f"{result.usage.total_tokens} total[/dim]"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Failed to complete prompt")
        sys.exit(1)


@app.command()
def chat(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider to use"),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Config file path (default: ~/.config/me-gpt/config.yaml)"
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model override"),
):
    """Start an interactive chat session (REPL)."""
    asyncio.run(_chat(provider, config_path, model))


async def _chat(provider_name: Optional[str], config_path: Optional[Path], model: Optional[str]):
    """Async implementation of chat command."""
    try:
        config = AgentConfig.load(config_path)
        provider_name = provider_name or config.default_provider
        provider = get_provider(provider_name, config)
        session = Session()

        console.print(
            Panel(
                f"[bold]Agent Chat[/bold]\n\n"
                f"Provider: {provider_name}\n"
                f"Type 'exit' or press Ctrl+C to quit",
                border_style="blue",
            )
        )

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

                if user_input.lower() in ["exit", "quit"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if not user_input.strip():
                    continue

                session.add_user_message(user_input)

                # Get completion
                with console.status("[bold green]Thinking..."):
                    result = await provider.complete(user_input, model=model)

                session.add_assistant_message(result.text)

                # Display response
                console.print(f"\n[bold green]Assistant[/bold green]: {result.text}")

                if result.usage:
                    console.print(
                        f"[dim]({result.usage.total_tokens} tokens)[/dim]"
                    )

            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                logger.exception("Error during chat")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Failed to start chat")
        sys.exit(1)


@app.command()
def test(
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Config file path (default: ~/.config/me-gpt/config.yaml)"
    ),
):
    """Test all configured providers with a simple prompt."""
    asyncio.run(_test(config_path))


async def _test(config_path: Optional[Path]):
    """Async implementation of test command."""
    try:
        config = AgentConfig.load(config_path)
        test_prompt = "Say 'Hello from agent!' and nothing else."

        console.print("[bold]Testing all providers...[/bold]\n")

        for provider_name in config.providers.keys():
            try:
                console.print(f"[cyan]Testing {provider_name}...[/cyan]")
                provider = get_provider(provider_name, config)

                result = await provider.complete(test_prompt, max_tokens=50)

                console.print(f"  [green]✓[/green] Response: {result.text[:100]}")
                if result.usage:
                    console.print(f"  [dim]Tokens: {result.usage.total_tokens}[/dim]")

            except Exception as e:
                console.print(f"  [red]✗[/red] Failed: {e}")

            console.print()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Failed to test providers")
        sys.exit(1)


if __name__ == "__main__":
    app()
