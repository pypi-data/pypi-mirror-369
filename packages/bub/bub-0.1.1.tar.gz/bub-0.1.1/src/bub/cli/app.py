"""CLI main module for Bub."""

from contextlib import suppress
from pathlib import Path
from typing import Optional

import typer

from ..agent import Agent, ToolActionSubscriber, build_event_runtime
from ..config import Settings, get_settings
from .render import create_cli_renderer

app = typer.Typer(
    name="bub",
    help="Bub it. Build it.",
    add_completion=False,
    rich_markup_mode="rich",
)


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        # Default to chat mode
        chat()


renderer = create_cli_renderer()


def _exit_with_error(message: str) -> None:
    """Exit with error message."""
    renderer.error(message)
    raise typer.Exit(1)


def _validate_workspace(workspace_path: Path) -> None:
    """Validate workspace directory exists."""
    if not workspace_path.exists():
        _exit_with_error(f"Workspace directory does not exist: {workspace_path}")


def _validate_api_key(settings: Settings) -> None:
    """Validate API key is present."""
    if not settings.api_key:
        renderer.api_key_error()
        raise typer.Exit(1)


def _validate_model_config(settings: Settings) -> None:
    """Validate provider and model configuration."""
    if not settings.provider:
        _exit_with_error("Provider not configured. Set BUB_PROVIDER (e.g., 'openai', 'anthropic', 'ollama')")
    if not settings.model_name:
        _exit_with_error("Model name not configured. Set BUB_MODEL_NAME (e.g., 'gpt-4', 'claude-3', 'llama2')")


def _create_agent(
    settings: Settings, workspace_path: Path, model_override: Optional[str], max_tokens: Optional[int]
) -> Agent:
    """Create and return an Agent instance."""
    # Parse model override if provided (format: provider/model or just model)
    if model_override:
        if "/" in model_override:
            provider, model_name = model_override.split("/", 1)
        else:
            provider = settings.provider or "openai"
            model_name = model_override
    else:
        provider = settings.provider or "openai"
        model_name = settings.model_name or "gpt-3.5-turbo"

    # Build evented runtime
    event_log, bus, ctx, huey, context, registry, executor = build_event_runtime(str(workspace_path))
    # Attach subscriber to execute tools via Huey
    ToolActionSubscriber(bus, executor, huey, ctx)

    return Agent(
        provider=provider,
        model_name=model_name,
        api_key=settings.api_key or "",
        api_base=settings.api_base,
        max_tokens=max_tokens or settings.max_tokens,
        workspace_path=workspace_path,
        system_prompt=settings.system_prompt,
        bus=bus,
        event_log=event_log,
    )


def _handle_special_commands(user_input: str, agent: Agent) -> Optional[bool]:
    cmd = user_input.lower()
    if cmd in ["quit", "exit", "q"]:
        renderer.info("Goodbye!")
        return True  # break
    elif cmd == "reset":
        agent.reset_conversation()
        renderer.conversation_reset()
        return False  # continue
    elif cmd == "debug":
        renderer.toggle_debug()
        return False  # continue
    return None  # not a special command


def _handle_chat_loop(agent: Agent) -> None:
    """Handle the interactive chat loop."""
    while True:
        try:
            # Do not pre-echo; rely solely on user.input event for display
            user_input = renderer.get_user_input()
            if not user_input.strip():
                continue
            special = _handle_special_commands(user_input, agent)
            if special is True:
                break
            if special is False:
                continue

            # Align view mode with debug toggle for consistency
            # View mode follows debug toggle; initial announcement only
            renderer.set_view_mode("process" if renderer._show_debug else "conversation")

            # Let event bus drive rendering; no on_step mirroring
            agent.chat(user_input)
            renderer.info("")

        except (KeyboardInterrupt, EOFError):
            renderer.info("\nGoodbye!")
            break


@app.command()
def chat(
    workspace: Optional[Path] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> None:
    """Start interactive chat with Bub."""
    try:
        workspace_path = workspace or Path.cwd()
        _validate_workspace(workspace_path)

        settings = get_settings(workspace_path)
        _validate_api_key(settings)
        _validate_model_config(settings)

        agent = _create_agent(settings, workspace_path, model, max_tokens)

        # Subscribe to all events for rendering
        unsubscribe = None
        if getattr(agent, "bus", None):
            try:
                unsubscribe = agent.bus.subscribe("*", renderer.render_event)
            except Exception:
                unsubscribe = None

        renderer.welcome()
        renderer.usage_info(
            workspace_path=str(workspace_path),
            model=agent.model or "",  # ensure str
            tools=agent.tool_registry.list_tools(),
        )
        renderer.info("Type 'quit', 'exit', or 'q' to end the session.")
        renderer.info("Type 'reset' to clear conversation history.")
        renderer.info("Type 'debug' to toggle TAAO process visibility.")
        renderer.info("")

        _handle_chat_loop(agent)

        if unsubscribe:
            with suppress(Exception):
                unsubscribe()

    except Exception as e:
        renderer.error(f"Failed to start chat: {e!s}")
        raise typer.Exit(1) from e


@app.command()
def run(
    command: str,
    workspace: Optional[Path] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> None:
    """Run a single command with Bub."""
    try:
        workspace_path = workspace or Path.cwd()
        _validate_workspace(workspace_path)

        settings = get_settings(workspace_path)
        _validate_api_key(settings)
        _validate_model_config(settings)

        agent = _create_agent(settings, workspace_path, model, max_tokens)

        # Subscribe to all events for rendering
        unsubscribe = None
        if getattr(agent, "bus", None):
            try:
                unsubscribe = agent.bus.subscribe("*", renderer.render_event)
            except Exception:
                unsubscribe = None

        renderer.info(f"Executing: {command}")

        agent.chat(command)

        if unsubscribe:
            with suppress(Exception):
                unsubscribe()

    except Exception as e:
        renderer.error(f"Failed to execute command: {e!s}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
