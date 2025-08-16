#!/usr/bin/env python3

import os
import sys
import json
import atexit
from pathlib import Path

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown


def get_config_dir() -> Path:
    """Return the configuration directory for tux-gpt based on OS."""
    if os.name == "nt":
        base = Path(
            os.getenv(
                "APPDATA",
                Path.home() / "AppData" / "Roaming"
            )
        )
    else:
        base = Path(
            os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")
        )
    return base / "tux-gpt"


CONFIG_DIR: Path = get_config_dir()
CONFIG_PATH: Path = CONFIG_DIR / "config.json"
HISTORY_PATH: Path = CONFIG_DIR / "history.json"
INPUT_HISTORY_PATH: Path = CONFIG_DIR / "input_history"
MAX_HISTORY: int = 20


def write_default_config() -> None:
    """Create default configuration file with default model."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    default_config: dict[str, str] = {"model": "gpt-4.1-mini"}
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2)


def load_config() -> dict[str, object]:
    """Load CLI configuration, writing default if missing."""
    if not CONFIG_PATH.exists():
        write_default_config()
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: failed to load config {CONFIG_PATH}: {e}")
        return {"model": "gpt-4.1-mini"}


def load_history() -> list[dict[str, str]]:
    """Load persisted conversation history (up to MAX_HISTORY)."""
    if not HISTORY_PATH.exists():
        return []
    try:
        with HISTORY_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: failed to load history {HISTORY_PATH}: {e}")
        return []


def save_history(history: list[dict[str, str]]) -> None:
    """Persist conversation history, keeping only last MAX_HISTORY messages."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with HISTORY_PATH.open("w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Warning: failed to save history {HISTORY_PATH}: {e}")


def main() -> None:
    """Main entry point for tux-gpt CLI."""
    console = Console()

    # ensure config directory exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # setup multi-line input session with Ctrl+Enter to submit
    session = None
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.history import FileHistory

        kb = KeyBindings()

        # Enter should insert a newline (multi-line support)
        @kb.add('enter')
        def _(event):  # pylint: disable=redefined-outer-name
            event.current_buffer.insert_text('\n')

        # Use Ctrl+J to submit the message (as terminals typically cannot distinguish Ctrl+Enter)
        @kb.add('c-j')
        def _(event):  # pylint: disable=redefined-outer-name
            event.app.current_buffer.validate_and_handle()

        session = PromptSession(
            multiline=True,
            key_bindings=kb,
            history=FileHistory(str(INPUT_HISTORY_PATH)),
        )
    except ImportError:
        console.print(
            "[red]Warning: prompt_toolkit not installed. "
            "Falling back to single-line input. "
            "Install prompt-toolkit for multi-line input.[/red]"
        )

    welcome_message = (
        "\n             Welcome to the tux-gpt!\n"
        " This is a terminal-based interactive tool using GPT.\n"
        "  Please visit https://github.com/fberbert/tux-gpt\n"
        " Type Ctrl+J to submit your input. Type 'exit' to quit.\n"
    )
    console.print(f"[bold blue]{welcome_message}[/bold blue]", justify="left")

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        console.print(
            "[red]Please set your OPENAI_API_KEY environment variable.[/red]"
        )
        sys.exit(1)

    config = load_config()
    model = config.get("model", "gpt-5-mini")
    supported_models = ("gpt-5-mini", "gpt-4.1", "gpt-4.1-mini")
    if model not in supported_models:
        console.print(
            f"[red]Model '{model}' not supported. Choose one of: "
            f"{', '.join(supported_models)}[/red]"
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    system_msg: dict[str, str] = {
        "role": "system",
        "content": (
            "You are a virtual assistant that can search the web. Always "
            "search the web when user asks for something data related. "
            "For example: 'What is the weather today?' or 'Which date is "
            "today?'. You are running in a Linux terminal. Return responses "
            "formatted in Markdown so they can be rendered in the terminal "
            "using rich."
        ),
    }

    persisted = load_history()

    while True:
        try:
            if session:
                user_input = session.prompt("> ")
            else:
                user_input = input("> ")
        except (EOFError, KeyboardInterrupt):
            console.print("\nExiting.")
            break

        if not user_input.strip():
            continue

        if user_input.strip().lower() in ("exit", "quit"):
            console.print("Exiting.")
            break

        call_history: list[dict[str, str]] = (
            [system_msg]
            + persisted
            + [{"role": "user", "content": user_input}]
        )

        try:
            with console.status("[bold green]", spinner="dots"):
                resp = client.responses.create(
                    model=model,
                    input=call_history,  # type: ignore[arg-type]
                    tools=[{"type": "web_search_preview"}],
                )
        except Exception as e:
            console.print(f"[red]Error calling OpenAI API: {e}[/red]")
            continue

        answer = resp.output_text.strip()
        console.print()
        console.print(Markdown(answer))
        console.print()

        persisted.append({"role": "user", "content": user_input})
        persisted.append({"role": "assistant", "content": answer})

        if len(persisted) > MAX_HISTORY:
            persisted = persisted[-MAX_HISTORY:]

        save_history(persisted)


if __name__ == "__main__":
    main()
