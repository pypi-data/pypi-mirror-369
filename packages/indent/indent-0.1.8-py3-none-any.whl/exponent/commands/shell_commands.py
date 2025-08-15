import asyncio
import difflib
import os
import re
import select
import shutil
import sys
import time
from asyncio.events import AbstractEventLoop
from collections.abc import Callable, Coroutine, Iterable

from exponent.commands.theme import Theme, bg_color_seq, fg_color_seq, get_theme
from exponent.core.remote_execution.types import ChatSource
from exponent.core.remote_execution.utils import safe_read_file
from exponent.utils.version import check_exponent_version_and_upgrade

# Import termios and tty conditionally for Windows compatibility
try:
    import termios
    import tty

    POSIX_TERMINAL = True
except ImportError:
    POSIX_TERMINAL = False

import logging
from concurrent.futures import Future
from datetime import datetime
from enum import Enum
from typing import IO, Any

import click
import questionary
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    FuzzyCompleter,
)
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_processor import KeyPress
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.syntax import Syntax

from exponent.commands.common import (
    check_inside_git_repo,
    check_running_from_home_directory,
    check_ssl,
    create_chat,
    inside_ssh_session,
    redirect_to_login,
    start_client,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import (
    StrategyChoice,
    StrategyOption,
    exponent_cli_group,
)
from exponent.commands.utils import (
    ConnectionTracker,
    Spinner,
    ThinkingSpinner,
    start_background_event_loop,
)
from exponent.core.config import Environment, Settings
from exponent.core.graphql.client import GraphQLClient
from exponent.core.graphql.mutations import HALT_CHAT_STREAM_MUTATION
from exponent.core.graphql.queries import EVENTS_FOR_CHAT_QUERY
from exponent.core.graphql.subscriptions import (
    CONFIRM_AND_CONTINUE_SUBSCRIPTION,
    INDENT_EVENTS_SUBSCRIPTION,
)
from exponent.core.remote_execution.exceptions import ExponentError, RateLimitError
from exponent.core.remote_execution.files import FileCache
from exponent.core.types.generated.strategy_info import (
    ENABLED_STRATEGY_INFO_LIST,
)

from .utils import (
    ask_for_quit_confirmation,
    get_short_git_commit_hash,
    launch_exponent_browser,
)

logger = logging.getLogger(__name__)


SLASH_COMMANDS = {
    "/help": "Show available commands",
    "/autorun": "Toggle between autorun modes",
    "/web": "Move chat to a web browser",
    "/cmd": "Execute a terminal command directly and give the result as context",
    # Thinking is slow + not making chats better, disabling for now
    # "/thinking": "Toggle thinking mode to show/hide AI's thinking process",
}


class AutoConfirmMode(str, Enum):
    OFF = "off"
    READ_ONLY = "read_only"
    ALL = "all"


ATTACHMENT_PATH_PATTERN = re.compile(r"(^|\s)@[^\s]+")


@exponent_cli_group()
def shell_cli() -> None:
    pass


@shell_cli.command()
@click.option(
    "--model",
    help="LLM model",
    required=True,
    default="CLAUDE_4_SONNET",
)
@click.option(
    "--strategy",
    prompt=True,
    prompt_required=False,
    type=StrategyChoice(ENABLED_STRATEGY_INFO_LIST),
    cls=StrategyOption,
    default="NATURAL_EDIT_CLAUDE_3_7_XML",
)
@click.option(
    "--autorun",
    is_flag=True,
    help="Enable autorun mode",
)
@click.option(
    "--depth",
    type=click.IntRange(1, 30, clamp=True),
    help="Depth limit of the chat if autorun mode is enabled",
    default=5,
)
@click.option(
    "--chat-id",
    help="ID of an existing chat session to reconnect",
    required=False,
)
@click.option(
    "--prompt",
    help="Initial prompt",
)
@click.option(
    "--headless",
    is_flag=True,
    help="Run single prompt in headless mode",
)
@use_settings
def shell(
    settings: Settings,
    model: str,
    strategy: str,
    chat_id: str | None = None,
    autorun: bool = False,
    depth: int = 0,
    prompt: str | None = None,
    headless: bool = False,
) -> None:
    """Start an Exponent session in your current shell."""

    check_exponent_version_and_upgrade(settings)

    if not headless and not sys.stdin.isatty():
        print("Terminal not available, running in headless mode")
        headless = True

    if headless and not prompt:
        print("Error: --prompt option is required with headless mode")
        sys.exit(1)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    is_running_from_home_directory = check_running_from_home_directory(
        # We don't require a confirmation for exponent shell because it's more likely
        # there's a legitimate reason for running Exponent from home directory when using shell
        require_confirmation=False
    )

    loop = start_background_event_loop()

    if not is_running_from_home_directory:  # Prevent double warnings from being shown
        asyncio.run_coroutine_threadsafe(check_inside_git_repo(settings), loop).result()

    check_ssl()

    api_key = settings.api_key
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()
    gql_client = GraphQLClient(api_key, base_api_url, base_ws_url)
    parent_event_uuid: str | None = None
    checkpoints: list[dict[str, Any]] = []

    if chat_id is None:
        chat_uuid = asyncio.run_coroutine_threadsafe(
            create_chat(api_key, base_api_url, base_ws_url, ChatSource.CLI_SHELL), loop
        ).result()
    else:
        chat_uuid = chat_id

        # events = asyncio.run_coroutine_threadsafe(
        #     _get_events_for_chat(gql_client, chat_uuid), loop
        # ).result()
        # parent_event_uuid = _get_parent_event_uuid(events)
        # checkpoints = _get_checkpoints(events)

    if chat_uuid is None:
        sys.exit(1)

    working_directory = os.getcwd()
    file_cache = FileCache(working_directory)
    connection_tracker = ConnectionTracker()

    client_coro = start_client(
        api_key,
        settings.base_url,
        base_api_url,
        base_ws_url,
        chat_uuid,
        file_cache=file_cache,
        connection_tracker=connection_tracker,
    )

    theme = get_theme(settings.options.use_default_colors)

    if headless:
        assert prompt is not None

        chat = Chat(
            chat_uuid,
            parent_event_uuid,
            settings.base_url,
            working_directory,
            gql_client,
            model,
            strategy,
            autorun,
            depth,
            StaticView(theme),
            checkpoints=checkpoints,
            thinking=False,
        )

        client_task = loop.create_task(client_coro)
        turn_task = loop.create_task(chat.send_prompt(prompt))

        asyncio.run_coroutine_threadsafe(
            asyncio.wait({client_task, turn_task}, return_when=asyncio.FIRST_COMPLETED),
            loop,
        ).result()
    else:
        chat = Chat(
            chat_uuid,
            parent_event_uuid,
            settings.base_url,
            working_directory,
            gql_client,
            model,
            strategy,
            autorun,
            depth,
            LiveView(theme),
            checkpoints=checkpoints,
            thinking=False,
        )

        client_fut = asyncio.run_coroutine_threadsafe(client_coro, loop)
        input_handler = InputHandler(theme, loop, file_cache)
        _print_welcome_message(theme)

        shell = Shell(
            prompt, loop, input_handler, chat, connection_tracker, settings.environment
        )

        shell.run()
        client_fut.cancel()

    print("Jump back into this chat by running:")
    print(f"  exponent shell --chat-id {chat_uuid}")
    print()
    print("Or continue in a web browser at:")
    print(f"  {chat.url()}")
    print()


async def _get_events_for_chat(
    gql_client: GraphQLClient, chat_uuid: str
) -> list[dict[str, Any]]:
    result = await gql_client.execute(EVENTS_FOR_CHAT_QUERY, {"chatUuid": chat_uuid})
    return result.get("eventsForChat", {}).get("events", [])  # type: ignore


def _get_parent_event_uuid(events: list[dict[str, Any]]) -> str | None:
    if len(events) > 0:
        uuid = events[-1]["eventUuid"]
        assert isinstance(uuid, str)

        return uuid

    return None


def _get_checkpoints(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event for event in events if event.get("__typename") == "CheckpointCreatedEvent"
    ]


def _print_welcome_message(theme: Theme) -> None:
    print("╭─────────────────────────────────╮")
    print(
        f"│ ✨ Welcome to {bold_seq()}{fg_color_seq(theme.exponent_green)}Indent \x1b[4mSHELL{reset_attrs_seq()} ✨ │"
    )

    print("╰─────────────────────────────────╯")
    print()
    print(
        f"  Enter {bold_seq()}/help{not_bold_seq()} to see available commands and keyboard shortcuts"
    )
    print(
        f"  Enter {bold_seq()}q{not_bold_seq()}, {bold_seq()}exit{not_bold_seq()} or press {bold_seq()}<ctrl+c>{not_bold_seq()} to quit"
    )
    print()


def pause_spinner(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(self: "LiveView", *args: Any, **kwargs: Any) -> Any:
        self.spinner.hide()
        self.spinner = self.default_spinner
        result = func(self, *args, **kwargs)
        self.spinner.show()
        return result

    return wrapper


def stop_spinner(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(self: "LiveView", *args: Any, **kwargs: Any) -> Any:
        self.spinner.hide()
        self.spinner = self.default_spinner
        result = func(self, *args, **kwargs)
        return result

    return wrapper


class BaseView:
    def __init__(self, theme: Theme) -> None:
        self.theme = theme

    def render_event_summary(self, kind: str, event: dict[str, Any]) -> None:
        summary = event["messageData"]["__typename"]
        # if kind == "FileWriteEvent":
        #     summary = "Writing file..."

        # elif kind == "FileWriteResultEvent":
        #     summary = "File written"

        # elif kind == "CodeBlockEvent":
        #     summary = "Executing code..."

        # elif kind == "CodeExecutionEvent":
        #     summary = "Code executed"

        # elif kind == "CommandEvent":
        #     if event["data"]["type"] == "FILE_READ":
        #         summary = f"Reading file {event['data']['filePath']}..."
        #     elif event["data"]["type"] == "FILE_OPEN":
        #         summary = f"Opening file {event['data']['filePath']}..."
        #     else:
        #         summary = "Executing command..."

        # else:
        #     return

        seqs = [
            clear_line_seq(),
            self._render_block_footer(summary, status="running", nl=False),
        ]
        render(seqs)

    def _render_block_header(self, text: str) -> list[str]:
        return [
            bg_color_seq(self.theme.block_header_bg),
            erase_line_seq(),
            bold_seq(),
            "\r",  # Return to start of line
            f"  {text} ",
            reset_attrs_seq(),
            "\n",
        ]

    def _render_block_footer(
        self, text: str, status: str | None = None, nl: bool = True
    ) -> list[str]:
        seqs: list[Any] = [
            bg_color_seq(self.theme.block_footer_bg),
            erase_line_seq(),
            italic_seq(),
        ]

        if status == "completed":
            seqs.append(
                [
                    fg_color_seq(self.theme.green),
                    bold_seq(),
                    "  ✓ ",
                    not_bold_seq(),
                ]
            )
        elif status == "rejected":
            seqs.append(
                [
                    fg_color_seq(self.theme.red),
                    bold_seq(),
                    "  𐄂 ",
                    not_bold_seq(),
                ]
            )
        elif status == "running":
            seqs.append(
                [
                    fg_color_seq(self.theme.blue),
                    bold_seq(),
                    "  ",
                    not_bold_seq(),
                ]
            )
        else:
            seqs.append(
                [
                    bold_seq(),
                    "  ",
                    not_bold_seq(),
                ]
            )

        seqs.append([fg_color_seq(self.theme.block_footer_fg), text, reset_attrs_seq()])

        if nl:
            seqs.append(["\n"])

        return seqs

    def _render_natural_edit_diff(self, write: dict[str, Any]) -> list[Any]:
        diff = generate_diff(write.get("originalFile") or "", write["newFile"]).strip()

        highlighted_diff = highlight_code(diff, "udiff", self.theme)

        return [
            self._render_block_header("Diff"),
            bg_color_seq(self.theme.block_body_bg),
            erase_line_seq(),
            "\n",
            highlighted_diff,
            "\n",
        ]

    def _render_natural_edit_error(self, error: str) -> list[str]:
        return [
            fg_color_seq(1),
            f"\nError: {error.strip()}\n\n",
            reset_attrs_seq(),
        ]

    def _render_code_block_start(self, lang: str) -> list[Any]:
        return [
            self._render_block_header(lang.capitalize()),
        ]

    def _render_code_block_content(self, content: str, lang: str) -> str:
        return highlight_code(content.strip(), lang, self.theme)

    def _render_code_block_output(self, content: str) -> list[Any]:
        content = re.sub("\n+$", "", content)

        if content.strip() == "":
            result = [
                [
                    "  ",
                    fg_color_seq(self.theme.dimmed_text_fg),
                    bg_color_seq(self.theme.block_body_bg),
                    erase_line_seq(),
                    "-- no output --\n",
                ]
            ]
        else:
            lines = pad_left(content, "  ").split("\n")

            result = [
                [bg_color_seq(self.theme.block_body_bg), erase_line_seq(), line, "\n"]
                for line in lines
            ]

        return [
            self._render_block_header("Output"),
            bg_color_seq(self.theme.block_body_bg),
            erase_line_seq(),
            "\n",
            erase_line_seq(),
            result,
            bg_color_seq(self.theme.block_body_bg),
            erase_line_seq(),
            reset_attrs_seq(),
            "\n",
        ]

    def _render_file_write_block_start(self, path: str) -> list[Any]:
        return [
            self._render_block_header(f"Editing file {path}"),
        ]

    def _render_file_write_block_content(self, content: str, lang: str) -> str:
        return highlight_code(
            content.strip(),
            lang,
            self.theme,
        )

    def _render_file_write_block_result(self, result: str | None) -> list[Any]:
        result = result or "Edit applied"
        return [self._render_block_footer(f"{result}", status="completed")]

    def _render_command_block_start(self, type_: str) -> list[Any]:
        return [
            self._render_block_header(type_),
        ]

    def _render_command_block_content(self, data: dict[str, Any]) -> list[Any]:
        if data["type"] == "PROTOTYPE":
            content = data["contentRendered"]
        else:
            content = data["filePath"].strip()

        lines = pad_left(content, "  ").split("\n")
        seqs: list[Any] = [bg_color_seq(self.theme.block_body_bg)]
        seqs.append([[erase_line_seq(), line, "\n"] for line in lines])

        return seqs

    def _render_command_block_output(
        self, content: str, type_: str, lang: str
    ) -> list[Any]:
        if content.strip() == "":
            result = [
                "  ",
                fg_color_seq(self.theme.dimmed_text_fg),
                bg_color_seq(self.theme.block_body_bg),
                erase_line_seq(),
                "-- no output --\n",
            ]
        else:
            result = [
                highlight_code(
                    content.strip(),
                    lang,
                    self.theme,
                )
            ]

        return [
            self._render_block_header("Output"),
            bg_color_seq(self.theme.block_body_bg),
            erase_line_seq(),
            "\n",
            result,
            bg_color_seq(self.theme.block_body_bg),
            erase_line_seq(),
            "\n",
            self._render_block_footer(
                f"{bold_seq()}{type_}{not_bold_seq()} command executed",
                status="completed",
            ),
        ]

    def _render_checkpoint_created_block_start(self) -> list[Any]:
        header_text = "".join(
            [
                bold_seq(),
                "✓ ",
                not_bold_seq(),
                "checkpoint created",
            ]
        )
        return [
            self._render_block_header(header_text),
        ]

    def _render_checkpoint_content(self, content: str) -> list[Any]:
        return [
            highlight_code(
                content.strip(),
                "text",
                self.theme,
            ),
        ]

    def _render_checkpoint_created_block(self, event: dict[str, Any]) -> list[Any]:
        content = f"{get_short_git_commit_hash(event['commitHash'])}: {event['commitMessage']}"

        return [
            self._render_checkpoint_created_block_start(),
            self._render_checkpoint_content(content),
            "\n",
            "\n",
        ]

    def _render_checkpoint_rollback_block_start(self) -> list[Any]:
        header_text = "".join(
            [
                bold_seq(),
                "✓ ",
                not_bold_seq(),
                "checkpoint rollback",
            ]
        )
        return [
            self._render_block_header(header_text),
        ]

    def _render_checkpoint_rollback_block(self, event: dict[str, Any]) -> list[Any]:
        pretty_date = datetime.fromisoformat(
            event["gitMetadata"]["commit_date"]
        ).strftime("%Y-%m-%d %H:%M:%S")
        content = (
            f"{get_short_git_commit_hash(event['commitHash'])}: {event['commitMessage']}\n"
            f"{event['gitMetadata']['author_name']} <{event['gitMetadata']['author_email']}> {pretty_date}"
        )

        return [
            self._render_checkpoint_rollback_block_start(),
            self._render_checkpoint_content(content),
            "\n",
            "\n",
        ]

    def _render_checkpoint_error_block_start(self) -> list[Any]:
        return [
            self._render_block_header(
                f"{bold_seq()}𐄂 {not_bold_seq()}checkpoint error"
            ),
        ]

    def _render_checkpoint_error_block(self, event: dict[str, Any]) -> list[Any]:
        return [
            self._render_checkpoint_error_block_start(),
            self._render_checkpoint_content(event["message"]),
            "\n",
            "\n",
        ]

    def _render_step_block_start(self, title: str) -> list[Any]:
        return [
            self._render_block_header(f"Step: {title}"),
        ]

    def _render_step_block_content(self, content: str) -> list[str]:
        """Render step content with proper formatting and background color.
        Returns a list of formatted lines ready for rendering.
        """
        # First reset any previous formatting
        reset_seq = reset_attrs_seq()
        erase_line_seq_str = erase_line_seq()

        # Apply padding and wrap lines with proper escape sequences
        formatted_lines = []
        lines = content.strip().split("\n")

        for line in lines:
            # erase_line_seq fills the entire line with the background color
            # We need to return to start of line first with \r
            formatted_line = f"\r{erase_line_seq_str}  {line}{reset_seq}\n"
            formatted_lines.append(formatted_line)

        return formatted_lines

    def _render_step_result_content(self, content: str) -> list[Any]:
        formatted_content = pad_left(content, "  ")
        return [
            self._render_block_header("Step result"),
            formatted_content,
            "\n",
        ]


class LiveView(BaseView):
    def __init__(self, theme: Theme, render_user_messages: bool = False) -> None:
        super().__init__(theme)
        self.buffer: Buffer = NullBuffer()
        self.command_data: dict[str, Any] | None = None
        self.tool_uses: dict[str, dict[str, Any]] = {}
        self.confirmation_required: bool = True
        self.default_spinner = Spinner("Exponent is working...")
        self.msg_gen_spinner = Spinner("Exponent is thinking real hard...")
        (r, g, b) = theme.thinking_spinner_fg.rgb
        rgb = (round(r * 255), round(g * 255), round(b * 255))
        self.thinking_spinner = ThinkingSpinner(fg_color=rgb)
        self.step_spinner = Spinner("Exponent is working on a step...")
        self.thinking_start_time: float | None = None
        self.exec_spinner = Spinner(
            "Exponent is waiting for the code to finish running..."
        )
        self.diff_spinner = Spinner("Exponent is generating file diff...")
        self.spinner = self.default_spinner
        self.pending_event: dict[str, Any] | None = None
        self.pending_event_list: list[Any] = []
        self.render_user_messages = render_user_messages

    def render_event(self, kind: str, event: dict[str, Any]) -> None:
        message_type = event["messageData"]["__typename"]
        if kind == "UserEvent" and message_type == "TextMessage":
            self._handle_user_message_event(event)
        if (
            kind == "UserEvent" and message_type == "ToolResultMessage"
        ) or message_type == "PartialToolResultMessage":
            self._handle_command_result_event(event)
        elif kind == "AssistantEvent" and message_type == "TextMessage":
            self._handle_message_event(event)
        elif kind == "AssistantEvent" and message_type == "ToolCallMessage":
            self._handle_tool_call_event(event)
        elif kind == "SystemEvent" and message_type == "ToolPermissionStatusMessage":
            if event["messageData"]["permissionStatus"] == "requested":
                self._handle_confirmation_request_event(event)
            else:
                self._handle_confirmation_response_event(event)
        elif kind == "Error":
            print(event)
            # print(json.dumps(event))
        # elif kind == "CodeBlockEvent":
        #     self._handle_code_block_event(event)
        # elif (
        #     kind == "CommandChunkEvent"
        #     and event.get("data", {}).get("__typename") == "ThinkingCommandData"
        # ):
        #     # Start the thinking animation and record start time
        #     if self.spinner != self.thinking_spinner:
        #         if self.spinner:
        #             self.spinner.hide()
        #         self.spinner = self.thinking_spinner
        #         # Record the start time before showing spinner
        #         self.thinking_start_time = time.time()
        #         # Pass the start time to spinner
        #         self.thinking_spinner.start_time = self.thinking_start_time
        #         self.spinner.show()
        # elif (
        #     kind == "CommandEvent"
        #     and event.get("data", {}).get("__typename") == "ThinkingCommandData"
        # ):
        #     # Treat CommandEvent with ThinkingCommandData as ThinkingEvent
        #     self._handle_thinking_event(
        #         {
        #             "eventUuid": event["uuid"],
        #             "parentUuid": event.get("parentUuid"),
        #             "turnUuid": event.get("turnUuid"),
        #             "content": event["data"]["content"],
        #         }
        #     )
        # elif kind == "StepChunkEvent":
        #     self._handle_step_chunk_event(event)
        # elif kind == "StepEvent":
        #     self._handle_step_event(event)
        # elif kind == "StepConfirmationEvent":
        #     self._handle_step_confirmation_event(event)
        # elif kind == "StepExecutionStartEvent":
        #     self._handle_step_execution_start_event(event)
        # elif kind == "StepExecutionResultEvent":
        #     self._handle_step_execution_result_event(event)
        # elif kind == "FileWriteChunkEvent":
        #     self._handle_file_write_chunk_event(event)
        # elif kind == "FileWriteEvent":
        #     self._handle_file_write_event(event)
        # elif kind == "FileWriteConfirmationEvent":
        #     self._handle_file_write_confirmation_event(event)
        # elif kind == "FileWriteStartEvent":
        #     self._handle_file_write_start_event(event)
        # elif kind == "FileWriteResultEvent":
        #     self._handle_file_write_result_event(event)
        # elif kind == "CodeBlockChunkEvent":
        #     self._handle_code_block_chunk_event(event)
        # elif kind == "CodeBlockEvent":
        #     self._handle_code_block_event(event)
        # elif kind == "CodeBlockConfirmationEvent":
        #     self._handle_code_block_confirmation_event(event)
        # elif kind == "CodeExecutionStartEvent":
        #     self._handle_code_execution_start_event(event)
        # elif kind == "CodeExecutionEvent":
        #     self._handle_code_execution_event(event)
        # elif kind == "CommandChunkEvent":
        #     if event["data"]["type"] in ["FILE_READ", "FILE_OPEN", "PROTOTYPE"]:
        #         self._handle_command_chunk_event(event)
        # elif kind == "CommandEvent":
        #     if event["data"]["type"] in ["FILE_READ", "FILE_OPEN", "PROTOTYPE"]:
        #         self._handle_tool_call_event(event)
        # elif kind == "CommandConfirmationEvent":
        #     self._handle_command_confirmation_event(event)
        # elif kind == "CommandStartEvent":
        #     self._handle_command_start_event(event)
        # elif kind == "CommandResultEvent":
        #     self._handle_command_result_event(event)
        # elif kind == "Error" or kind == "ContextLimitExceededError":
        #     error_message = event["message"]
        #     raise ExponentError(error_message)
        # elif kind == "RateLimitError":
        #     error_message = event["message"]
        #     raise RateLimitError(error_message)
        # elif kind == "CheckpointCreatedEvent":
        #     self._handle_checkpoint_created_event(event)
        # elif kind == "CheckpointRollbackEvent":
        #     self._handle_checkpoint_rollback_event(event)
        # elif kind == "CheckpointError":
        #     self._handle_checkpoint_error_event(event)

    def start_turn(self) -> None:
        self.spinner.show()

    def end_turn(self) -> None:
        self.spinner.hide()

    @pause_spinner
    def _handle_message_start_event(self, event: dict[str, Any]) -> None:
        self.spinner = self.msg_gen_spinner

    @pause_spinner
    def _handle_thinking_start_event(self, event: dict[str, Any]) -> None:
        # Use ThinkingSpinner for a specialized thinking animation
        self.spinner = self.thinking_spinner
        self.spinner.show()
        # Record the start time
        self.thinking_start_time = time.time()

    @pause_spinner
    def _handle_thinking_event(self, event: dict[str, Any]) -> None:
        # This handles the thinking event completion
        if self.spinner == self.thinking_spinner:
            self.spinner.hide()
            self.spinner = self.default_spinner

        # Calculate thinking duration
        if self.thinking_start_time is not None:
            duration = time.time() - self.thinking_start_time
            # Format duration nicely
            if duration < 1:
                duration_str = f"{int(duration * 1000)}ms"
            elif duration < 60:
                # Round to nearest second to match spinner display
                duration_str = f"{int(duration)}s"
            else:
                mins = int(duration // 60)
                secs = int(duration % 60)
                duration_str = f"{mins}m {secs}s"

            # Improved message with more natural language and decorations
            # Use render() instead of print() to ensure proper terminal rendering
            render(
                f"\r  {fg_color_seq(self.theme.dimmed_text_fg)}Exponent thought for {duration_str}{reset_attrs_seq()}\n\n"
            )

            # Reset the start time
            self.thinking_start_time = None

    @stop_spinner
    def _handle_message_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["uuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = CharBuffer(event_uuid, get_term_width())

        assert isinstance(self.buffer, CharBuffer)

        seqs.append(self.buffer.render_new_chars(event["content"]))
        render(seqs)

    @pause_spinner
    def _handle_message_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["uuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = CharBuffer(event_uuid, get_term_width())

        assert isinstance(self.buffer, CharBuffer)

        seqs.append(self.buffer.render_new_chars(event["messageData"]["text"]))
        seqs.append(["\n\n"])
        render(seqs)

    def _handle_user_message_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["uuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = CharBuffer(event_uuid, get_term_width())

        assert isinstance(self.buffer, CharBuffer)

        seqs.append(self.buffer.render_new_chars(f"> {event['messageData']['text']}"))
        seqs.append(["\n\n"])
        render(seqs)

    @stop_spinner
    def _handle_file_write_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["uuid"]
        seqs: list[Any] = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)

            seqs.append(
                [
                    self._render_block_header(f"Editing file {event['filePath']}"),
                    bg_color_seq(self.theme.block_body_bg),
                    erase_line_seq(),
                    "\n",
                ]
            )

        assert isinstance(self.buffer, LineBuffer)

        write = event["writeContent"]
        content = write.get("naturalEdit") or write.get("content") or event["content"]

        formatted_content = self._render_file_write_block_content(
            content, event["language"]
        )

        seqs.append(self.buffer.render_new_lines(formatted_content, self.theme))

        if (
            "intermediateEdit" in write and write["intermediateEdit"] is not None
        ):  # natural edit
            # when intermediateEdit is present in writeContent dict
            # it indicates the server is generating original/new file pair
            seqs.append(["\n", "\n"])
            render(seqs)
            self.spinner = self.diff_spinner
            self.spinner.show()
        else:
            render(seqs)

    @pause_spinner
    def _handle_file_write_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["uuid"]
        seqs: list[Any] = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)
            seqs.append(self._render_file_write_block_start(event["filePath"]))

        assert isinstance(self.buffer, LineBuffer)

        write = event["writeContent"]

        if "newFile" in write:  # natural edit
            seqs.append(
                [
                    "\r",
                    move_cursor_up_seq(2),
                    erase_display_seq(),
                ]
            )

        content = write.get("naturalEdit") or write.get("content") or event["content"]

        formatted_content = self._render_file_write_block_content(
            content, event["language"]
        )

        seqs.append(
            [
                self.buffer.render_new_lines(formatted_content, self.theme),
                bg_color_seq(self.theme.block_body_bg),
                erase_line_seq(),
                "\n",
            ]
        )

        error = write.get("errorContent")

        if error is None:
            if write.get("newFile") is not None:
                seqs.append(self._render_natural_edit_diff(write))

            if event["requireConfirmation"]:
                seqs.append(
                    [
                        self._render_block_footer(
                            f"Confirm edit with {bold_seq()}<ctrl+y>{not_bold_seq()}, send a new message to dismiss code changes."
                        ),
                        "\n",
                    ]
                )
        else:
            seqs.append(self._render_natural_edit_error(error))

        render(seqs)
        self.confirmation_required = event["requireConfirmation"]

    @pause_spinner
    def _handle_file_write_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["fileWriteUuid"]:
            return

        seqs = []

        if event["accepted"]:
            seqs.append(
                [
                    move_cursor_up_seq(2),
                    self._render_block_footer("Applying edit...", status="running"),
                    "\n",
                ]
            )
        elif self.confirmation_required:
            # user entered new prompt, cursor moved down
            # therefore we need to move it up, redraw status, and move it
            # back where it was

            seqs.append(
                [
                    move_cursor_up_seq(4),
                    self._render_block_footer("Edit dismissed", status="rejected"),
                    "\n\n\n",
                ]
            )

        render(seqs)

    @pause_spinner
    def _handle_file_write_start_event(self, event: dict[str, Any]) -> None:
        return

    @pause_spinner
    def _handle_file_write_result_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["fileWriteUuid"]:
            return

        seqs: list[Any] = []

        if self.confirmation_required:
            seqs.append([move_cursor_up_seq(2)])

        seqs.append([self._render_file_write_block_result(event["content"]), "\n"])

        render(seqs)

    @stop_spinner
    def _handle_command_chunk_event(self, event: dict[str, Any]) -> None:
        data = event["data"]

        # Ignore thinking chunks
        if data["type"] == "THINKING":
            return

        if (
            data["type"] == "PROTOTYPE"
            and data["commandName"] in ["search_files", "glob"]
        ) or data["type"] == "FILE_READ":
            # We want to render the _final_ regex in the header, so we don't render any chunk,
            # instead we'll render the header below in _handle_command_event.
            return

        type_ = self._get_command_type(data)

        event_uuid = event["uuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = CommandBuffer(event_uuid)

            seqs.append(
                [
                    self._render_block_header(type_),
                    bg_color_seq(self.theme.block_body_bg),
                    erase_line_seq(),
                    "\n",
                ]
            )

        assert isinstance(self.buffer, CommandBuffer)

        # NOTE: not rendering the contentRendered here incrementally
        # because it's changing non-incrementally and breaks the layout

        render(seqs)

    @pause_spinner
    def _handle_confirmation_request_event(self, event: dict[str, Any]) -> None:
        self.pending_event = event
        self.pending_event_list.append(event)
        render(
            [
                self._render_block_footer(
                    f"Confirm with {bold_seq()}<ctrl+y>{not_bold_seq()}, send a new message to dismiss code changes."
                ),
                "\n",
            ]
        )

    @pause_spinner
    def _handle_confirmation_response_event(self, event: dict[str, Any]) -> None:
        self.pending_event_list.pop()

    @pause_spinner
    def _handle_tool_call_event(self, event: dict[str, Any]) -> None:
        data = event["messageData"]
        event_uuid = event["uuid"]
        command_name = data["toolName"]

        if self.buffer.event_uuid != event_uuid:
            if command_name == "read_file":
                self.buffer = CommandBuffer(event_uuid)
                self._handle_read_file_event(event)
                return
            elif command_name == "bash":
                self.buffer = LineBuffer(event_uuid)
                self._handle_bash_event(event)
                return

    @pause_spinner
    def _handle_command_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["commandUuid"]:
            return

        seqs = []

        if event["accepted"]:
            seqs.append(
                [
                    move_cursor_up_seq(2),
                    self._render_block_footer("Executing command...", status="running"),
                    "\n",
                ]
            )
        else:
            # user entered new prompt, cursor moved down
            # therefore we need to move it up, redraw status, and move it
            # back where it was

            seqs.append(
                [
                    move_cursor_up_seq(4),
                    self._render_block_footer(
                        "Command did not execute", status="rejected"
                    ),
                    "\n\n\n",
                ]
            )

        render(seqs)

    def _handle_command_start_event(self, event: dict[str, Any]) -> None:
        return

    @pause_spinner
    def _handle_command_result_event(self, event: dict[str, Any]) -> None:
        if self.command_data is None:
            return

        seqs: list[Any] = []

        # For FILE_READ commands, only show that the command ran successfully, not the file contents
        if self.command_data["toolName"] == "read_file":
            seqs.append(
                [
                    self._render_block_footer(
                        "File read successfully", status="completed"
                    ),
                    "\n",
                ]
            )
        else:
            seqs.append(
                [
                    self._render_command_block_output(
                        event["messageData"]["text"],
                        self.command_data["toolName"],
                        "bash",
                    ),
                    "\n",
                ]
            )

        render(seqs)
        self.command_data = None

    @stop_spinner
    def _handle_code_block_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["uuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)

            seqs.append(
                [
                    self._render_block_header(event["language"].capitalize()),
                    bg_color_seq(self.theme.block_body_bg),
                    erase_line_seq(),
                    "\n",
                ]
            )

        assert isinstance(self.buffer, LineBuffer)

        formatted_content = self._render_code_block_content(
            event["content"], event["language"]
        )

        seqs.append(self.buffer.render_new_lines(formatted_content, self.theme))
        render(seqs)

    @pause_spinner
    def _handle_read_file_event(self, event: dict[str, Any]) -> None:
        data = event["messageData"]
        tool_input = data["toolInput"]
        seqs: list[Any] = []

        path = tool_input["filePath"]
        seqs.append(self._render_command_block_start(f"Read file: {path}"))

        assert isinstance(self.buffer, CommandBuffer)

        render(seqs)
        self.command_data = data
        # self.tool_uses[tool_input["tool_use_id"]] =

    @pause_spinner
    def _handle_bash_event(self, event: dict[str, Any]) -> None:
        data = event["messageData"]
        event_uuid = event["uuid"]
        seqs: list[Any] = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)
            seqs.append(self._render_code_block_start("bash"))

        assert isinstance(self.buffer, LineBuffer)

        formatted_content = self._render_code_block_content(
            event["messageData"]["toolInput"]["command"], "bash"
        )

        seqs.append(
            [
                self.buffer.render_new_lines(formatted_content, self.theme),
                bg_color_seq(self.theme.block_body_bg),
                erase_line_seq(),
                "\n",
            ]
        )

        render(seqs)
        self.command_data = data

    @pause_spinner
    def _handle_code_block_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["uuid"]
        seqs: list[Any] = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)
            seqs.append(self._render_code_block_start(event["language"]))

        assert isinstance(self.buffer, LineBuffer)

        formatted_content = self._render_code_block_content(
            event["content"], event["language"]
        )

        seqs.append(
            [
                self.buffer.render_new_lines(formatted_content, self.theme),
                bg_color_seq(self.theme.block_body_bg),
                erase_line_seq(),
                "\n",
            ]
        )

        if event["requireConfirmation"]:
            seqs.append(
                [
                    self._render_block_footer(
                        f"Run it with {bold_seq()}<ctrl+y>{not_bold_seq()}, send a new message to cancel this request."
                    ),
                    "\n",
                ]
            )

        render(seqs)
        self.confirmation_required = event["requireConfirmation"]

    @pause_spinner
    def _handle_code_block_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["codeBlockUuid"]:
            return

        seqs = []

        if event["accepted"]:
            seqs.append(
                [
                    move_cursor_up_seq(2),
                    self._render_block_footer("Running code...", status="running"),
                    "\n",
                ]
            )
        else:
            # user entered new prompt, cursor moved down
            # therefore we need to move it up, redraw status, and move it
            # back where it was

            seqs.append(
                [
                    move_cursor_up_seq(4),
                    self._render_block_footer(
                        "Code did not execute", status="rejected"
                    ),
                    "\n\n\n",
                ]
            )

        render(seqs)

    @pause_spinner
    def _handle_code_execution_start_event(self, event: dict[str, Any]) -> None:
        self.spinner = self.exec_spinner

    @pause_spinner
    def _handle_code_execution_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["codeBlockUuid"]:
            return

        seqs: list[Any] = []

        if self.confirmation_required:
            seqs.append([move_cursor_up_seq(2)])

        seqs.append([self._render_code_block_output(event["content"]), "\n"])

        render(seqs)

    def _get_command_type(self, data: dict[str, Any]) -> str:
        if data["type"] == "PROTOTYPE":
            return " ".join(
                [word.capitalize() for word in data["commandName"].split("_")]
            )
        elif data["type"] == "FILE_READ":
            return "Read File"
        elif data["type"] == "FILE_OPEN":
            return "Open File"
        else:
            return str(data["type"]).title().replace("_", " ")

    def _handle_checkpoint_created_event(self, event: dict[str, Any]) -> None:
        render(self._render_checkpoint_created_block(event))

    def _handle_checkpoint_rollback_event(self, event: dict[str, Any]) -> None:
        render(self._render_checkpoint_rollback_block(event))

    def _handle_checkpoint_error_event(self, event: dict[str, Any]) -> None:
        render(self._render_checkpoint_error_block(event))

    @pause_spinner
    def _handle_step_chunk_event(self, event: dict[str, Any]) -> None:
        """Handle streaming chunks for step events.

        Simply shows a spinner while streaming step chunks.
        We'll let the final StepEvent handle the full rendering.
        """
        # Just show a spinner for step chunks coming in
        # Don't render partial content to avoid duplication
        self.spinner = self.step_spinner
        self.spinner.show()

    @pause_spinner
    def _handle_step_event(self, event: dict[str, Any]) -> None:
        """Handle a step event by rendering it with proper ANSI formatting.

        This is modeled after the file_write_event handler for consistency.
        """
        event_uuid = event["uuid"]
        seqs = []

        self.buffer = LineBuffer(event_uuid)

        # Get title with fallback
        title = event.get("stepTitle") or "Step"
        seqs.append(self._render_block_header(f"Step: {title}"))

        # Get content with fallbacks and format it
        content = (
            event.get("stepContent")
            or event.get("stepDescription", "")
            or event.get("description", "")
        )

        if content:
            # Format lines with proper background color
            lines = content.strip().split("\n")
            formatted_lines = []
            for line in lines:
                formatted_lines.append(
                    [
                        erase_line_seq(),
                        "  " + line,
                        reset_attrs_seq(),
                        "\n",
                    ]
                )
            seqs.extend(formatted_lines)

        seqs.append(["\n"])

        # Check if this step requires confirmation
        require_confirmation = event.get("requireConfirmation", False)
        if require_confirmation:
            seqs.append(
                [
                    *self._render_block_footer(
                        "Confirm step with <ctrl+y>. Sending a new message will cancel this step."
                    ),
                    "\n",
                ]
            )

        # Render it all at once
        render(seqs)

        # Store confirmation state and step event for later
        self.confirmation_required = require_confirmation
        if require_confirmation:
            self.pending_event = event

    @pause_spinner
    def _handle_step_confirmation_event(self, event: dict[str, Any]) -> None:
        """Handle confirmation events for steps.

        Updates the UI to show that a step has been confirmed or rejected.
        """
        # Copy exactly the file_write_confirmation_event handler pattern
        # This pattern is known to work correctly
        if self.buffer.event_uuid != event["stepUuid"]:
            return

        seqs = []

        if event["accepted"]:
            seqs.append(
                [
                    move_cursor_up_seq(2),
                    self._render_block_footer("Executing step...", status="running"),
                    "\n",
                ]
            )
        else:
            # user entered new prompt, cursor moved down
            # therefore we need to move it up, redraw status, and move it
            # back where it was
            seqs.append(
                [
                    move_cursor_up_seq(4),
                    self._render_block_footer(
                        "Step did not execute", status="rejected"
                    ),
                    "\n\n\n",
                ]
            )

        render(seqs)

        # If the step was rejected, clear pending state
        if not event["accepted"]:
            self.pending_event = None
            self.confirmation_required = False

    @pause_spinner
    def _handle_step_execution_start_event(self, event: dict[str, Any]) -> None:
        """Handle the start of step execution.

        Sets the appropriate spinner and does basic validation.
        """
        try:
            # Log the event UUID for debugging
            step_uuid = event.get("stepUuid")

            # Only change spinner if we have a step UUID
            if step_uuid and self.buffer.event_uuid.startswith("step-"):
                self.spinner = self.step_spinner
                self.spinner.show()
        except Exception as e:
            # Log the error but don't crash the entire UI
            render([f"\r\x1b[31mError handling step execution start: {e!s}\x1b[0m\n"])

    @pause_spinner
    def _handle_step_execution_result_event(self, event: dict[str, Any]) -> None:
        """Handle the result of a step execution.

        Shows the step output/result and marks the step as completed.
        This is modeled after the file_write_result_event handler.
        """
        # Display results regardless of UUID matching to ensure we always see them
        seqs = []

        # Check for result content with fallbacks
        result = event.get("stepOutputRaw") or event.get("stepSummary", "")
        if result:
            # Render a result block with proper formatting
            seqs.append(self._render_block_header("Step result"))

            # Format lines with proper background color
            lines = result.strip().split("\n")
            formatted_lines = []

            for line in lines:
                formatted_lines.append(
                    [
                        erase_line_seq(),
                        "  " + line,
                        reset_attrs_seq(),
                        "\n",
                    ]
                )

            seqs.extend(formatted_lines)
            seqs.append(["\n"])

        # Add the completion footer
        seqs.append(self._render_block_footer("Step completed", status="completed"))
        seqs.append(["\n"])

        render(seqs)

        # Reset all state now that execution is complete
        self.pending_event = None
        self.confirmation_required = False
        self.spinner = self.default_spinner

    def handle_checkpoint_interrupt(self, event: dict[str, Any]) -> None:
        self.buffer = NullBuffer()
        render(["Now back to it:", "\n", "\n"])
        self.render_event(event["__typename"], event)

        # rendering the event toggles on the spinner
        self.end_turn()


class StaticView(BaseView):
    def __init__(self, theme: Theme) -> None:
        super().__init__(theme)
        self.command_data: dict[str, Any] | None = None
        self.thinking_start_time: float | None = None
        self.pending_event: dict[str, Any] | None = None
        self.confirmation_required: bool = False

    def render_event(self, kind: str, event: dict[str, Any]) -> None:
        if kind == "MessageEvent":
            if event["role"] == "assistant":
                print(event["content"].strip())
                print()

        elif (
            kind == "CommandChunkEvent"
            and event.get("data", {}).get("__typename") == "ThinkingCommandData"
        ):
            # Record start time for thinking
            self.thinking_start_time = time.time()

        elif (
            kind == "CommandEvent"
            and event.get("data", {}).get("__typename") == "ThinkingCommandData"
        ):
            # Calculate thinking duration
            if self.thinking_start_time is not None:
                duration = time.time() - self.thinking_start_time
                # Format duration nicely
                if duration < 1:
                    duration_str = f"{int(duration * 1000)}ms"
                elif duration < 60:
                    # Round to nearest second to match spinner display
                    duration_str = f"{int(duration)}s"
                else:
                    mins = int(duration // 60)
                    secs = int(duration % 60)
                    duration_str = f"{mins}m {secs}s"

                # Improved message with more natural language and decorations
                # Use render() instead of print() to ensure proper terminal rendering
                render(
                    [
                        f"\x1b[2m\x1b[38;5;249m◇ Exponent thought for {duration_str} ◇\x1b[0m\n\n"
                    ]
                )

                # Reset the start time
                self.thinking_start_time = None

        elif kind == "StepChunkEvent" or kind == "StepEvent":
            title = event.get("stepTitle") or "Step"
            content = (
                event.get("stepContent")
                or event.get("stepDescription", "")
                or event.get("description", "")
            )

            if content:
                # For StaticView, we use simpler formatting without ANSI sequences
                formatted_content = ""
                for line in content.strip().split("\n"):
                    formatted_content += f"  {line}\n"

                seqs = [
                    self._render_block_header(f"Step: {title}"),
                    formatted_content,
                    "\n",
                ]

                # Store for confirmation if needed
                if kind == "StepEvent" and event.get("requireConfirmation", False):
                    self.pending_event = event
                    self.confirmation_required = True
                    seqs.append(
                        self._render_block_footer(
                            "Confirm step with <ctrl+y>. Sending a new message will cancel this step."
                        )
                    )

                render(seqs)

        elif kind == "StepExecutionResultEvent":
            result = event.get("stepOutputRaw") or event.get("stepSummary", "")
            if result:
                # For StaticView, we use simpler formatting without ANSI sequences
                formatted_result = ""
                for line in result.strip().split("\n"):
                    formatted_result += f"  {line}\n"

                seqs = [
                    self._render_block_header("Step result"),
                    formatted_result,
                    "\n",
                    self._render_block_footer("Step completed", status="completed"),
                    "\n",
                ]
                render(seqs)

                # Clear pending event and reset confirmation flag
                self.pending_event = None
                self.confirmation_required = False

        elif kind == "CommandEvent":
            if event.get("data", {}).get("__typename") == "ThinkingCommandData":
                # We already handled this case above
                pass
            elif event.get("data", {}).get("type") in ["FILE_READ", "FILE_OPEN"]:
                command_type = (
                    "Read File"
                    if event.get("data", {}).get("type") == "FILE_READ"
                    else "Open File"
                )

                seqs = [
                    self._render_command_block_start(command_type),
                    self._render_command_block_content(event["data"]),
                    "\n",
                ]

                render(seqs)
                self.command_data = event["data"]

        elif kind == "FileWriteEvent":
            write = event["writeContent"]

            content = (
                write.get("naturalEdit") or write.get("content") or event["content"]
            )

            seqs = [
                self._render_file_write_block_start(event["filePath"]),
                self._render_file_write_block_content(content, event["language"]),
                "\n",
            ]

            error = write.get("errorContent")

            if error is None:
                if write.get("newFile") is not None:
                    seqs.append(self._render_natural_edit_diff(write))
            else:
                seqs.append(self._render_natural_edit_error(error))

            render(seqs)

        elif kind == "FileWriteResultEvent":
            seqs = [self._render_file_write_block_result(event["content"]), "\n"]
            render(seqs)

        elif kind == "CodeBlockEvent":
            seqs = [
                self._render_code_block_start(event["language"]),
                self._render_code_block_content(event["content"], event["language"]),
                "\n",
            ]

            render(seqs)

        elif kind == "CodeExecutionEvent":
            render([self._render_code_block_output(event["content"]), "\n"])

        elif kind == "CommandEvent":
            if event["data"]["type"] not in ["FILE_READ", "FILE_OPEN"]:
                return

            command_type = (
                "Read File" if event["data"]["type"] == "FILE_READ" else "Open File"
            )

            seqs = [
                self._render_command_block_start(command_type),
                self._render_command_block_content(event["data"]),
                "\n",
            ]

            render(seqs)
            self.command_data = event["data"]

        elif kind == "CommandResultEvent":
            if self.command_data is not None:
                # For FILE_READ commands, only show that the command ran successfully
                if self.command_data["type"] == "FILE_READ":
                    seqs = [
                        self._render_block_footer(
                            "File read successfully", status="completed"
                        ),
                        "\n",
                    ]
                else:
                    command_type = (
                        "Read File"
                        if self.command_data["type"] == "FILE_READ"
                        else "Open File"
                    )
                    seqs = [
                        self._render_command_block_output(
                            event["content"],
                            command_type,
                            self.command_data["language"],
                        ),
                        "\n",
                    ]

                render(seqs)
                self.command_data = None

        elif kind == "Error":
            error_message = event["message"]
            print(event)
            print(f"Error: {error_message}")
            print()
        elif kind == "RateLimitError":
            error_message = event["message"]
            print(event)
            print(f"Error: {error_message}")
            print(
                "Visit https://www.exponent.run/settings to update your billing settings."
            )
            print()

        elif kind == "CheckpointError":
            print(f"Checkpoint error: {event['message']}")
            print()

        elif kind == "CheckpointCreatedEvent":
            render(self._render_checkpoint_created_block(event))

    def start_turn(self) -> None:
        pass

    def end_turn(self) -> None:
        pass

    def handle_checkpoint_interrupt(self, event: dict[str, Any]) -> None:
        pass


class Chat:
    def __init__(
        self,
        chat_uuid: str,
        parent_event_uuid: str | None,
        base_url: str,
        working_directory: str,
        gql_client: GraphQLClient,
        model: str,
        strategy: str,
        autorun: bool,
        depth: int,
        view: StaticView | LiveView,
        checkpoints: list[dict[str, Any]],
        thinking: bool = False,
    ) -> None:
        self.chat_uuid = chat_uuid
        self.base_url = base_url
        self.working_directory = working_directory
        self.gql_client = gql_client
        self.model = model
        self.strategy = strategy
        self.auto_confirm_mode: AutoConfirmMode = (
            AutoConfirmMode.ALL if autorun else AutoConfirmMode.OFF
        )
        self.depth = depth
        self.thinking = thinking
        self.view = view
        self.pending_event = None
        self.pending_event_list: list[Any] = []
        self.parent_uuid: str | None = parent_event_uuid
        self.block_row_offset = 0
        self.console = Console()
        self.checkpoints = checkpoints
        self.inside_step_execution = False

    async def send_prompt(self, prompt: str) -> None:
        self.view.start_turn()
        paths = self.extract_attachment_paths(prompt)
        attachments = [(await self.build_attachment(path)) for path in paths]

        await self.process_chat_subscription(
            {"prompt": {"message": prompt, "attachments": attachments}}
        )

    def extract_attachment_paths(self, prompt: str) -> list[str]:
        paths = [
            prompt[match.start() : match.end()].strip()[1:]
            for match in ATTACHMENT_PATH_PATTERN.finditer(prompt)
        ]

        return list(filter(os.path.isfile, paths))

    async def build_attachment(self, path: str) -> dict[str, Any]:
        content = await safe_read_file(path)

        return {
            "fileAttachment": {
                "file": {
                    "filePath": path,
                    "workingDirectory": self.working_directory,
                },
                "content": content,
            }
        }

    async def send_confirmation(self) -> None:
        self.view.start_turn()
        if not self.pending_event_list:
            return

        pending_event = self.pending_event_list.pop()
        await self.confirm_and_continue_subscription(
            {
                "requestUuid": pending_event["uuid"],
            }
        )

    async def send_direct_action(self, action_type: str, args: dict[str, Any]) -> None:
        self.view.start_turn()
        print()
        if action_type == "shell":
            await self.process_chat_subscription(
                {"directAction": {"shellDirectAction": args}}
            )
        elif action_type == "checkpoint":
            await self.process_chat_subscription(
                {"directAction": {"createCheckpointDirectAction": args}}
            )

            if self.pending_event:
                self.view.handle_checkpoint_interrupt(self.pending_event)
        elif action_type == "rollback":
            await self.process_chat_subscription(
                {"directAction": {"checkpointRollbackDirectAction": args}}
            )
        else:
            raise ValueError(f"Unsupported direct action type: {action_type}")

    def toggle_autorun(self) -> None:
        if self.auto_confirm_mode == AutoConfirmMode.OFF:
            self.auto_confirm_mode = AutoConfirmMode.READ_ONLY
        elif self.auto_confirm_mode == AutoConfirmMode.READ_ONLY:
            self.auto_confirm_mode = AutoConfirmMode.ALL
        else:
            self.auto_confirm_mode = AutoConfirmMode.OFF

    def toggle_thinking(self) -> bool:
        self.thinking = not self.thinking
        return self.thinking

    async def halt_stream(self) -> None:
        await self.gql_client.execute(
            HALT_CHAT_STREAM_MUTATION, {"chatUuid": self.chat_uuid}, "HaltChatStream"
        )

    def url(self) -> str:
        return f"{self.base_url}/chats/{self.chat_uuid}"

    async def process_chat_subscription(self, extra_vars: dict[str, Any]) -> None:
        vars = {
            "chatUuid": self.chat_uuid,
            "parentUuid": self.parent_uuid,
            "model": self.model,
            "strategyNameOverride": self.strategy,
            "requireConfirmation": self.auto_confirm_mode == AutoConfirmMode.OFF,
            "readOnly": self.auto_confirm_mode == AutoConfirmMode.READ_ONLY,
            "depthLimit": self.depth,
            "enableThinking": self.thinking,
        }

        vars.update(extra_vars)

        try:
            async for response in self.gql_client.subscribe(
                INDENT_EVENTS_SUBSCRIPTION, vars
            ):
                # print(response)
                event = response["indentChat"]
                kind = event["__typename"]
                message_kind = event["messageData"]["__typename"]
                message_data = event["messageData"]

                if event["isSidechain"]:
                    self.inside_step_execution = True
                else:
                    self.inside_step_execution = False

                if (
                    kind == "SystemEvent"
                    and message_kind == "ToolPermissionStatusMessage"
                ):
                    if message_data["permissionStatus"] == "REQUESTED":
                        self.pending_event_list.append(event)

                # Render the event
                if not self.inside_step_execution:
                    self.view.render_event(kind, event)
                else:
                    self.view.render_event_summary(kind, event)

                # # Track parent UUID for future requests
                self.parent_uuid = event.get("uuid") or self.parent_uuid

        except Exception as e:
            # Log subscription processing errors only if needed
            import traceback

            traceback.print_exc()
            render([f"\r\x1b[31mError: {e!s}\x1b[0m\n"])
        finally:
            self.view.end_turn()

    async def confirm_and_continue_subscription(
        self, extra_vars: dict[str, Any]
    ) -> None:
        vars = {
            "chatUuid": self.chat_uuid,
            "model": self.model,
            "strategyNameOverride": self.strategy,
            "requireConfirmation": self.auto_confirm_mode == AutoConfirmMode.OFF,
            "readOnly": self.auto_confirm_mode == AutoConfirmMode.READ_ONLY,
            "depthLimit": self.depth,
            "enableThinking": self.thinking,
        }

        vars.update(extra_vars)

        try:
            async for response in self.gql_client.subscribe(
                CONFIRM_AND_CONTINUE_SUBSCRIPTION, vars
            ):
                # print(response)
                event = response["confirmAndContinue"]
                kind = event["__typename"]
                message_kind = event["messageData"]["__typename"]
                message_data = event["messageData"]

                if event["isSidechain"]:
                    self.inside_step_execution = True
                else:
                    self.inside_step_execution = False

                if (
                    kind == "SystemEvent"
                    and message_kind == "ToolPermissionStatusMessage"
                ):
                    if message_data["permissionStatus"] == "requested":
                        self.pending_event_list.append(event)

                # Render the event
                if not self.inside_step_execution:
                    self.view.render_event(kind, event)
                else:
                    self.view.render_event_summary(kind, event)

                # # Track parent UUID for future requests
                self.parent_uuid = event.get("uuid") or self.parent_uuid

        except Exception as e:
            # Log subscription processing errors only if needed
            import traceback

            traceback.print_exc()
            render([f"\r\x1b[31mError: {e!s}\x1b[0m\n"])
        finally:
            self.view.end_turn()


class HighlightLexer(Lexer):
    def lex_document(self, document: Document) -> Any:
        def get_line(line_number: int) -> list[tuple[str, str]]:
            line_text = document.lines[line_number]
            tokens = []
            last_index = 0

            for match in ATTACHMENT_PATH_PATTERN.finditer(line_text):
                start, end = match.span()

                if start > last_index:
                    tokens.append(("", line_text[last_index:start]))

                tokens.append(("class:attachment-path", line_text[start:end]))
                last_index = end

            if last_index < len(line_text):
                tokens.append(("", line_text[last_index:]))

            return tokens

        return get_line


class InputHandler:
    def __init__(
        self, theme: Theme, loop: AbstractEventLoop, file_cache: FileCache
    ) -> None:
        self.theme = theme
        self.bindings = KeyBindings()
        self.shortcut = None
        self.default = ""

        self.session: PromptSession[Any] = PromptSession(
            completer=FuzzyCompleter(ExponentCompleter(loop, file_cache)),
            complete_while_typing=True,
            complete_in_thread=True,
            key_bindings=merge_key_bindings([load_key_bindings(), self.bindings]),
            lexer=HighlightLexer(),
        )

        self.style = Style.from_dict(
            {
                "bottom-toolbar": "noreverse",
                "attachment-path": "underline",
            }
        )

        handler = self

        @self.bindings.add("enter")
        def _(event: Any) -> None:
            buf = event.current_buffer
            state = buf.complete_state

            if state and state.current_completion:
                buf.apply_completion(state.current_completion)

                if event.app.current_buffer.document.text[0] == "/":
                    event.current_buffer.validate_and_handle()
            else:
                event.current_buffer.validate_and_handle()

        # shift-enter
        @self.bindings.add("escape", "[", "1", "3", ";", "2", "u")
        def _(event: Any) -> None:
            event.app.current_buffer.newline()

        @self.bindings.add("c-a")
        @self.bindings.add("escape", "[", "9", "7", ";", "5", "u")
        def _(event: Any) -> None:
            handler.default = event.app.current_buffer.document.text
            self.shortcut = "<c-a>"
            event.app.exit()

        @self.bindings.add("escape", "[", "9", "9", ";", "5", "u")
        def _(event: Any) -> None:
            self.shortcut = "<c-c>"
            event.app.exit()

        @self.bindings.add("c-d")
        @self.bindings.add("escape", "[", "1", "0", "0", ";", "5", "u")
        def _(event: Any) -> None:
            self.shortcut = "<c-d>"
            event.app.exit()

        @self.bindings.add("c-e")
        @self.bindings.add("escape", "[", "1", "0", "1", ";", "5", "u")
        def _(event: Any) -> None:
            event.app.current_buffer.open_in_editor()

        @self.bindings.add("escape", "[", "1", "0", "7", ";", "5", "u")
        def _(event: Any) -> None:
            event.app.key_processor.feed(KeyPress(Keys.ControlK))

        @self.bindings.add("escape", "[", "1", "0", "8", ";", "5", "u")
        def _(event: Any) -> None:
            event.app.key_processor.feed(KeyPress(Keys.ControlL))

        @self.bindings.add("escape", "[", "1", "1", "0", ";", "5", "u")
        def _(event: Any) -> None:
            event.app.key_processor.feed(KeyPress(Keys.ControlN))

        @self.bindings.add("escape", "[", "1", "1", "2", ";", "5", "u")
        def _(event: Any) -> None:
            event.app.key_processor.feed(KeyPress(Keys.ControlP))

        @self.bindings.add("escape", "[", "1", "1", "4", ";", "5", "u")
        def _(event: Any) -> None:
            pass

        @self.bindings.add("escape", "[", "1", "1", "5", ";", "5", "u")
        def _(event: Any) -> None:
            pass

        # Thinking is slow + not making chats better, disabling for now
        # @self.bindings.add("c-t")
        # @self.bindings.add("escape", "[", "1", "1", "6", ";", "5", "u")
        # def _(event: Any) -> None:
        #     handler.default = event.app.current_buffer.document.text
        #     self.shortcut = "<c-t>"
        #     event.app.exit()

        @self.bindings.add("c-y")
        @self.bindings.add("escape", "[", "1", "2", "1", ";", "5", "u")
        def _(event: Any) -> None:
            handler.default = event.app.current_buffer.document.text
            self.shortcut = "<c-y>"
            event.app.exit()

        @self.bindings.add("escape", "[", "1", "2", "7", ";", "3", "u")
        def _(event: Any) -> None:
            event.app.key_processor.feed(KeyPress(Keys.Escape))
            event.app.key_processor.feed(KeyPress(Keys.Backspace))

        @self.bindings.add("escape", "[", "1", "2", "7", ";", "5", "u")
        def _(event: Any) -> None:
            event.app.key_processor.feed(KeyPress(Keys.ControlH))

    def prompt(
        self, auto_confirm_mode: AutoConfirmMode, thinking: bool, seed: str
    ) -> str:
        toolbar = [("", "  ")]
        default_color = self.theme.statusbar_default_fg
        # thinking_on_color = self.theme.statusbar_thinking_on
        autorun_ro_color = self.theme.statusbar_autorun_ro
        autorun_all_color = self.theme.statusbar_autorun_all

        if auto_confirm_mode == AutoConfirmMode.ALL:
            toolbar.append((f"bold {autorun_all_color}", "➔ autorun "))
            toolbar.append((f"bold {autorun_all_color} reverse", " all "))
        elif auto_confirm_mode == AutoConfirmMode.READ_ONLY:
            toolbar.append((f"bold {autorun_ro_color}", "➔ autorun "))
            toolbar.append((f"bold {autorun_ro_color} reverse", " read only "))
        else:
            toolbar.append((f"bold {default_color}", "➔ autorun "))
            toolbar.append((f"bold {default_color} reverse", " off "))

        toolbar.append(("", " "))
        toolbar.append((f"{default_color}", "(toggle with "))
        toolbar.append((f"{default_color} bold", "<ctrl+a>"))
        toolbar.append((f"{default_color}", ")"))
        toolbar.append(("", "   "))

        # Thinking is slow + not making chats better, disabling for now
        # if thinking:
        #     toolbar.append((f"bold {thinking_on_color}", "⋯ thinking "))
        #     toolbar.append((f"bold {thinking_on_color} reverse", " on "))
        # else:
        #     toolbar.append((f"bold {default_color}", "⋯ thinking "))
        #     toolbar.append((f"bold {default_color} reverse", " off "))

        # toolbar.append(("", " "))
        # toolbar.append((f"{default_color}", "(toggle with "))
        # toolbar.append((f"{default_color} bold", "<ctrl+t>"))
        # toolbar.append((f"{default_color}", ")"))

        self.shortcut = None
        kitty_kbd_proto_enabled = enable_kitty_kbd_protocol()

        try:
            default = self.default or seed
            self.default = ""

            user_input = self.session.prompt(
                FormattedText([(f"bold {self.theme.exponent_green}", "∷ ")]),
                default=default,
                multiline=kitty_kbd_proto_enabled,
                bottom_toolbar=FormattedText(toolbar),
                style=self.style,
            )
        finally:
            if kitty_kbd_proto_enabled:
                disable_kitty_kbd_protocol()

        if self.shortcut is not None:
            return self.shortcut
        else:
            assert isinstance(user_input, str)
            return user_input


class Shell:
    def __init__(
        self,
        prompt: str | None,
        loop: asyncio.AbstractEventLoop,
        input_handler: InputHandler,
        chat: Chat,
        connection_tracker: ConnectionTracker,
        environment: Environment,
    ) -> None:
        self.prompt = prompt
        self.loop = loop
        self.input_handler = input_handler
        self.chat = chat
        self.environment = environment
        self.stream_fut: Future[Any] | None = None
        self.connection_tracker = connection_tracker

    def run(self) -> None:
        self._send_initial_prompt()
        seed = ""

        while True:
            try:
                self._wait_for_stream_completion()

                text = self.input_handler.prompt(
                    self.chat.auto_confirm_mode, self.chat.thinking, seed
                )

                seed = ""

                if text.startswith("/"):
                    self._run_command(text[1:].strip())
                elif text == "<c-y>":
                    if not self._confirm_execution():
                        seed = "yes"
                elif text == "<c-a>":
                    self._run_command("autorun")
                elif text == "<c-t>":
                    self._run_command("thinking")
                elif text in {"q", "exit"}:
                    print()
                    break
                elif text in ("<c-c>", "<c-d>"):
                    print()
                    do_quit = ask_for_quit_confirmation()
                    print()

                    if do_quit:
                        break
                elif text:
                    print()
                    self._send_prompt(text)

            except KeyboardInterrupt:
                if self._handle_keyboard_interrupt():
                    break

            except ExponentError as e:
                self._print_error_message(e)
                break
            except RateLimitError as e:
                self._print_rate_limit_error_message(e)
                break

    def _handle_keyboard_interrupt(self) -> bool:
        try:
            if self.stream_fut is not None:
                self._run_coroutine(self.chat.halt_stream()).result()
                return False
            return ask_for_quit_confirmation()
        except KeyboardInterrupt:
            return True

    def _ensure_connected(self) -> None:
        if not self.connection_tracker.is_connected():
            self._run_coroutine(self._wait_for_reconnection()).result()

    async def _wait_for_reconnection(self) -> None:
        render([clear_line_seq(), "Disconnected..."])
        await asyncio.sleep(1)
        spinner = Spinner("Reconnecting...")
        spinner.show()
        await self.connection_tracker.wait_for_reconnection()
        spinner.hide()
        render([fg_color_seq(2), bold_seq(), "✓ Reconnected"])
        await asyncio.sleep(1)
        render([clear_line_seq()])

    def _print_error_message(self, e: ExponentError) -> None:
        print(f"\n\n\x1b[1;31m{e}\x1b[0m")
        print("\x1b[3;33m")
        print("Reach out to team@exponent.run if you need support.")
        print("\x1b[0m")

    def _print_rate_limit_error_message(self, e: RateLimitError) -> None:
        print(f"\n\n\x1b[1;31m{e}\x1b[0m")
        print("\x1b[3;33m")
        print(
            "Visit https://www.exponent.run/settings to update your billing settings."
        )
        print("\x1b[0m")

    def _show_help(self) -> None:
        print()

        print(f"  {bold_seq()}Commands:{not_bold_seq()}")
        print()

        for command, description in sorted(SLASH_COMMANDS.items()):
            if command != "/help":
                print(f"    {bold_seq()}{command}{not_bold_seq()} - {description}")

        print()
        print(f"  {bold_seq()}Keyboard shortcuts:{not_bold_seq()}")
        print()
        print(
            f"    {bold_seq()}shift{not_bold_seq()}+{bold_seq()}enter{not_bold_seq()} - Add new line to the prompt (on supported terminals)"
        )
        print(
            f"    {bold_seq()}ctrl{not_bold_seq()}+{bold_seq()}a{not_bold_seq()} - Toggle between autorun modes"
        )
        print(
            f"    {bold_seq()}ctrl{not_bold_seq()}+{bold_seq()}c{not_bold_seq()} / {bold_seq()}ctrl{not_bold_seq()}+{bold_seq()}d{not_bold_seq()} - Quit Exponent"
        )
        print(
            f"    {bold_seq()}ctrl{not_bold_seq()}+{bold_seq()}e{not_bold_seq()} - Edit prompt in $EDITOR"
        )
        print(
            f"    {bold_seq()}ctrl{not_bold_seq()}+{bold_seq()}t{not_bold_seq()} - Toggle thinking mode"
        )
        print(
            f'    {bold_seq()}ctrl{not_bold_seq()}+{bold_seq()}y{not_bold_seq()} - Confirm action or insert "yes" into the prompt'
        )
        print()

        print(f"  {bold_seq()}Autorun modes:{not_bold_seq()}")
        print()
        print(
            f"    - {bold_seq()}off{not_bold_seq()} - You manually confirm each action (default)"
        )
        print(
            f"    - {bold_seq()}read only{not_bold_seq()} - Auto-confirm read-only actions like search and file access"
        )
        print(
            f"    - {bold_seq()}all{not_bold_seq()} - Auto-confirm all actions, including read, search, and edit"
        )
        print()

        print(
            f"  Tip: Type {bold_seq()}@{not_bold_seq()} to auto-complete project files."
        )
        print()

    def _run_command(self, command: str) -> None:
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "cmd":
            self._execute_shell_command(args)
        elif cmd == "help":
            self._show_help()
        elif cmd == "autorun":
            self._toggle_autorun()
        # Thinking is slow + not making chats better, disabling for now
        # elif cmd == "thinking":
        #     self._toggle_thinking()
        elif cmd == "web":
            self._switch_cli_chat_to_web()
        elif cmd == "c" or cmd == "checkpoint":
            self._create_checkpoint()
        elif cmd == "r" or cmd == "rollback":
            self._checkpoint_rollback(args)
        else:
            print(f"\n  Unknown command: /{command}\n")

    def _execute_shell_command(self, shell_command: str) -> None:
        if not shell_command:
            click.echo("\n  Error: Command command is empty. Usage: /cmd <command>\n")
            return

        self._ensure_connected()
        self.stream_fut = self._run_coroutine(
            self.chat.send_direct_action("shell", {"command": shell_command})
        )

    def _create_checkpoint(self) -> None:
        self._ensure_connected()
        self.stream_fut = self._run_coroutine(
            self.chat.send_direct_action("checkpoint", {"commitMessage": None})
        )

    def _checkpoint_rollback(self, args: str) -> None:
        self._ensure_connected()
        print()

        if not self.chat.checkpoints:
            print("No checkpoints to rollback to. Use /checkpoint to create one.\n")
            return

        choices = [
            questionary.Choice(
                title=f"{get_short_git_commit_hash(checkpoint['commitHash'])}: {checkpoint['commitMessage']}",
                value=index,
            )
            for index, checkpoint in enumerate(self.chat.checkpoints)
        ]
        checkpoint_index = questionary.select(
            "Chose a checkpoint to rollback to:",
            choices=choices,
            qmark="",
        ).ask()

        if checkpoint_index is None:
            print()
            return

        self.chat.checkpoints = self.chat.checkpoints[: checkpoint_index + 1]
        checkpoint_uuid = self.chat.checkpoints[-1]["eventUuid"]

        self.chat.parent_uuid = checkpoint_uuid
        self.stream_fut = self._run_coroutine(
            self.chat.send_direct_action(
                "rollback", {"checkpointCreatedEventUuid": checkpoint_uuid}
            )
        )

    def _toggle_autorun(self) -> None:
        self.chat.toggle_autorun()

        render(
            [
                "\r",
                move_cursor_up_seq(1),
                clear_line_seq(),
            ]
        )

    def _toggle_thinking(self) -> None:
        self.chat.toggle_thinking()

        render(
            [
                "\r",
                move_cursor_up_seq(1),
                clear_line_seq(),
            ]
        )

    def _switch_cli_chat_to_web(self) -> None:
        url = self.chat.url()
        print(f"\nThis chat has been moved to {url}\n")

        if not inside_ssh_session():
            launch_exponent_browser(
                self.environment, self.chat.base_url, self.chat.chat_uuid
            )

        while True:
            input()

    def _confirm_execution(self) -> bool:
        render(
            [
                "\r",
                move_cursor_up_seq(1),
                clear_line_seq(),
            ]
        )

        success = len(self.chat.pending_event_list) > 0
        self._ensure_connected()
        self.stream_fut = self._run_coroutine(self.chat.send_confirmation())

        return success

    def _send_initial_prompt(self) -> None:
        if self.prompt is not None:
            self._send_prompt(self.prompt)

    def _send_prompt(self, text: str) -> None:
        self._ensure_connected()
        self.stream_fut = self._run_coroutine(self.chat.send_prompt(text))

    def _wait_for_stream_completion(self) -> None:
        if self.stream_fut is not None:
            self.stream_fut.result()
            self.stream_fut = None

    def _run_coroutine(self, coro: Coroutine[Any, Any, Any]) -> Future[Any]:
        return asyncio.run_coroutine_threadsafe(coro, self.loop)


class ExponentCompleter(Completer):
    def __init__(self, loop: AbstractEventLoop, file_cache: FileCache):
        self.loop = loop
        self.file_cache = file_cache

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text = document.text

        if text.startswith("/"):
            for command in SLASH_COMMANDS:
                if command.startswith(text):
                    yield Completion(command, start_position=-len(text))

        elif text == "@" or text.endswith(" @"):
            for path in asyncio.run_coroutine_threadsafe(
                self.file_cache.get_files(), self.loop
            ).result():
                yield Completion(path + " ", start_position=0)


class Buffer:
    def __init__(self, event_uuid: str) -> None:
        self.event_uuid = event_uuid


class NullBuffer(Buffer):
    def __init__(self) -> None:
        super().__init__("")


class CharBuffer(Buffer):
    def __init__(self, event_uuid: str, term_width: int) -> None:
        super().__init__(event_uuid)
        self.term_width = term_width
        self.content_len = 0
        self.current_term_line_len = 0
        self.strip_next = False

    def render_new_chars(self, message: str) -> list[Any]:
        message = message.strip()
        new_text = message[self.content_len :]
        self.content_len = len(message)
        available_width = self.term_width - 3
        seqs = []

        while new_text:
            max_chunk_width = available_width - self.current_term_line_len
            chunk = new_text[0:max_chunk_width]
            new_text = new_text[max_chunk_width:]
            lines = chunk.split("\n")

            for idx, line in enumerate(lines):
                if self.current_term_line_len == 0:
                    seqs.append("  ")

                    if self.strip_next:
                        self.strip_next = False
                        line = line.lstrip()

                seqs.append(line)

                if idx < len(lines) - 1:
                    seqs.append("\n")
                    self.current_term_line_len = 0
                else:
                    self.current_term_line_len += len(line)

                    if self.current_term_line_len == available_width:
                        seqs.append("\n")
                        self.current_term_line_len = 0
                        self.strip_next = True

        return seqs


class LineBuffer(Buffer):
    def __init__(self, event_uuid: str) -> None:
        super().__init__(event_uuid)
        self.line_count = 0

    def render_new_lines(
        self,
        code: str,
        theme: Theme,
    ) -> list[Any]:
        seqs: list[Any] = []
        lines = code.split("\n")
        lines = lines[0 : len(lines) - 1]
        new_line_count = len(lines)

        seqs.append(bg_color_seq(theme.block_body_bg))

        if self.line_count > 0:
            seqs.append([move_cursor_up_seq(1), "\r"])
            lines = lines[self.line_count - 1 :]

        lines = [line + "\n" for line in lines]
        seqs.append(lines)
        self.line_count = new_line_count

        return seqs


# TODO maybe unify with LineBuffer?
class CommandBuffer(Buffer):
    def __init__(self, event_uuid: str) -> None:
        super().__init__(event_uuid)
        self.line_count = 0

    def render_new_lines(self, paths: list[Any]) -> list[Any]:
        seqs: list[Any] = []
        new_line_count = len(paths)

        if self.line_count > 0:
            seqs.append([move_cursor_up_seq(1), "\r"])
            paths = paths[self.line_count - 1 :]

        seqs.append(paths)
        self.line_count = new_line_count

        return seqs


def highlight_code(
    code: str,
    lang: str,
    theme: Theme,
    line_numbers: bool = False,
    padding: tuple[int, int] = (0, 2),
) -> str:
    syntax = Syntax(
        code,
        lang,
        theme=theme.hl_theme_name,
        line_numbers=line_numbers,
        word_wrap=True,
        padding=padding,
    )

    console = Console()

    with console.capture() as capture:
        console.print(syntax)

    result = capture.get()

    return (
        result.replace("\x1b[0m", f"\x1b[0m{bg_color_seq(theme.block_body_bg)}")
        + "\x1b[49m"
    )


def generate_diff(before_lines: str, after_lines: str) -> str:
    diff = difflib.unified_diff(
        before_lines.split("\n"),
        after_lines.split("\n"),
        fromfile="before",
        tofile="after",
        lineterm="",
    )

    return "\n".join(list(diff)[2:])


def pad_left(text: str, padding: str) -> str:
    return "\n".join([padding + line for line in text.strip().split("\n")])


def bold_seq() -> str:
    return "\x1b[1m"


def not_bold_seq() -> str:
    return "\x1b[22m"


def italic_seq() -> str:
    return "\x1b[3m"


def reverse_seq() -> str:
    return "\x1b[7m"


def not_reverse_seq() -> str:
    return "\x1b[27m"


def erase_line_seq() -> str:
    return "\x1b[2K"


def erase_display_seq() -> str:
    return "\x1b[0J"


def reset_attrs_seq() -> str:
    return "\x1b[0m"


def clear_line_seq() -> str:
    return f"\r{reset_attrs_seq()}{erase_line_seq()}"


def move_cursor_up_seq(n: int) -> str:
    if n > 0:
        return f"\x1b[{n}A"
    else:
        return ""


def move_cursor_down_seq(n: int) -> str:
    if n > 0:
        return f"\x1b[{n}B"
    else:
        return ""


def render(seqs: str | list[Any] | None) -> None:
    print(collect(seqs), end="")
    sys.stdout.flush()


def collect(seqs: str | list[Any] | None) -> str:
    if seqs is None:
        return ""

    if isinstance(seqs, str):
        return seqs

    assert isinstance(seqs, list)

    text = ""

    for seq in seqs:
        text += collect(seq)

    return text


def enable_kitty_kbd_protocol() -> bool:
    if not POSIX_TERMINAL or not sys.stdin.isatty():
        return False  # Not supported on Windows or when stdin is not a TTY

    with RawMode(sys.stdin.fileno()):
        stdin_fd = sys.stdin.fileno()
        stdout_fd = sys.stdout.fileno()

        if stdout_fd in select.select([], [stdout_fd], [])[1]:
            # Send the following sequences to the terminal:
            #   CSI >1u - enable kitty keyboard protocol
            #   CSI ?u - query status of kitty keyboard protocol
            #   CSI c - query device attributes (DA)
            os.write(stdout_fd, b"\x1b[>1u\x1b[?u\x1b[c")
            # If the terminal doesn't support the protocol then adding the
            # device attributes (DA) query forces it to respond anyway (it's
            # widely supported), which let's us check if the response includes
            # the kitty protocol status (CSI ?1u) without timing out.

        got_da_response = False
        kitty_proto_supported = False

        try:
            # Read terminal responses until we get DA response
            while not got_da_response:
                if stdin_fd in select.select([stdin_fd], [], [], 100)[0]:
                    reply = os.read(stdin_fd, 1024)
                    seqs = reply.split(b"\x1b[")

                    for seq in seqs:
                        if seq == b"?1u":
                            kitty_proto_supported = True
                        elif seq.endswith(b"c"):
                            got_da_response = True

        except Exception as e:
            logger.debug("Error enabling kitty kbd protocol", exc_info=e)

        return kitty_proto_supported


def disable_kitty_kbd_protocol() -> None:
    if POSIX_TERMINAL:
        sys.stdout.write("\x1b[<u")
        sys.stdout.flush()


class RawMode:
    def __init__(self, fd: IO[str] | int) -> None:
        self.fd = fd
        self.restore: bool = False
        self.mode: list[Any] | None = None

    def __enter__(self) -> None:
        if POSIX_TERMINAL:
            try:
                self.mode = termios.tcgetattr(self.fd)
                tty.setraw(self.fd)
                self.restore = True
            except (termios.error, AttributeError):
                pass
        # On Windows, we don't modify terminal settings
        # A more sophisticated implementation could use the Windows Console API

    def __exit__(self, _type: str, _value: str, _traceback: str) -> None:
        if self.restore and POSIX_TERMINAL:
            time.sleep(0.01)  # give the terminal time to send answerbacks
            assert isinstance(self.mode, list)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.mode)


def get_term_width() -> int:
    (cols, _) = shutil.get_terminal_size((80, 24))
    return cols
