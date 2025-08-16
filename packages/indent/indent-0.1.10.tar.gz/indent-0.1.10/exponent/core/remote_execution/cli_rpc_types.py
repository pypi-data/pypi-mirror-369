import msgspec
import yaml
from typing import Any


class PartialToolResult(msgspec.Struct, tag_field="tool_name", omit_defaults=True):
    pass


class ToolInput(msgspec.Struct, tag_field="tool_name", omit_defaults=True):
    """Concrete subclasses describe the full input schema for a tool."""

    def to_llm(self) -> dict[str, Any]:
        """Convert ToolInput to LLM-friendly typed dict format.

        Returns a dictionary with the tool parameters, excluding the tool_name
        which is handled separately by the LLM integration layer.

        Returns:
            self by default, which msgspec will serialize appropriately.
        """
        return msgspec.to_builtins(self)  # type: ignore[no-any-return]


class ToolResult(msgspec.Struct, tag_field="tool_name", omit_defaults=True):
    """Concrete subclasses return data from a tool execution."""

    def to_text(self) -> str:
        """
        This provides a default textual representation of the tool result. Override it as needed for your tool."""
        d = msgspec.to_builtins(self)
        del d["tool_name"]
        return yaml.dump(d)


class ErrorToolResult(ToolResult, tag="error"):
    error_message: str


READ_TOOL_NAME = "read"


class ReadToolInput(ToolInput, tag=READ_TOOL_NAME):
    file_path: str
    offset: int | None = None
    limit: int | None = None


class ReadToolResult(ToolResult, tag=READ_TOOL_NAME):
    content: str
    num_lines: int
    start_line: int
    total_lines: int

    def to_text(self) -> str:
        lines = self.content.splitlines()
        lines = [
            f"{str(i).rjust(6)}→{line}"
            for i, line in enumerate(lines, start=self.start_line + 1)
        ]
        return "\n".join(lines)


LIST_TOOL_NAME = "ls"


class ListToolInput(ToolInput, tag=LIST_TOOL_NAME):
    path: str
    ignore: list[str] | None = None


class ListToolResult(ToolResult, tag=LIST_TOOL_NAME):
    files: list[str]
    truncated: bool = False


GLOB_TOOL_NAME = "glob"


class GlobToolInput(ToolInput, tag=GLOB_TOOL_NAME):
    pattern: str
    path: str | None = None


class GlobToolResult(ToolResult, tag=GLOB_TOOL_NAME):
    filenames: list[str]
    duration_ms: int
    num_files: int
    truncated: bool


WRITE_TOOL_NAME = "write"


class WriteToolInput(ToolInput, tag=WRITE_TOOL_NAME):
    file_path: str
    content: str


class WriteToolResult(ToolResult, tag=WRITE_TOOL_NAME):
    message: str


GREP_TOOL_NAME = "grep"


class GrepToolInput(ToolInput, tag=GREP_TOOL_NAME):
    pattern: str
    path: str | None = None
    include: str | None = None
    multiline: bool | None = None


class GrepToolResult(ToolResult, tag=GREP_TOOL_NAME):
    matches: list[str]
    truncated: bool = False


EDIT_TOOL_NAME = "edit"


# This is only used in the CLI. The server side type is edit_tool.py
class EditToolInput(ToolInput, tag=EDIT_TOOL_NAME):
    file_path: str
    old_string: str
    new_string: str
    replace_all: bool = False


class EditToolResult(ToolResult, tag=EDIT_TOOL_NAME):
    message: str


BASH_TOOL_NAME = "bash"


class BashToolInput(ToolInput, tag=BASH_TOOL_NAME):
    command: str
    timeout: int | None = None
    description: str | None = None


class PartialBashToolResult(PartialToolResult, tag=BASH_TOOL_NAME):
    shell_output: str | None = None


class BashToolResult(ToolResult, tag=BASH_TOOL_NAME):
    shell_output: str
    duration_ms: int
    exit_code: int | None
    timed_out: bool
    stopped_by_user: bool


class HttpRequest(msgspec.Struct, tag="http_fetch_cli"):
    url: str
    method: str = "GET"
    headers: dict[str, str] | None = None
    timeout: int | None = None


class HttpResponse(msgspec.Struct, tag="http_fetch_cli"):
    status_code: int | None = None
    content: str | None = None
    error_message: str | None = None
    duration_ms: int | None = None
    headers: dict[str, str] | None = None


ToolInputType = (
    ReadToolInput
    | WriteToolInput
    | ListToolInput
    | GlobToolInput
    | GrepToolInput
    | EditToolInput
    | BashToolInput
)
PartialToolResultType = PartialBashToolResult

ToolResultType = (
    ReadToolResult
    | WriteToolResult
    | ListToolResult
    | GlobToolResult
    | GrepToolResult
    | EditToolResult
    | BashToolResult
    | ErrorToolResult
)


class ToolExecutionRequest(msgspec.Struct, tag="tool_execution"):
    tool_input: ToolInputType


class GetAllFilesRequest(msgspec.Struct, tag="get_all_files"):
    pass


class TerminateRequest(msgspec.Struct, tag="terminate"):
    pass


class SwitchCLIChatRequest(msgspec.Struct, tag="switch_cli_chat"):
    new_chat_uuid: str


class BatchToolExecutionRequest(msgspec.Struct, tag="batch_tool_execution"):
    tool_inputs: list[ToolInputType]


class GetAllFilesResponse(msgspec.Struct, tag="get_all_files"):
    files: list[str]


class TerminateResponse(msgspec.Struct, tag="terminate"):
    pass


class BatchToolExecutionResponse(msgspec.Struct, tag="batch_tool_execution"):
    tool_results: list[ToolResultType]


class SwitchCLIChatResponse(msgspec.Struct, tag="switch_cli_chat"):
    pass


class CliRpcRequest(msgspec.Struct):
    request_id: str
    request: (
        ToolExecutionRequest
        | GetAllFilesRequest
        | TerminateRequest
        | HttpRequest
        | BatchToolExecutionRequest
        | SwitchCLIChatRequest
    )


class ToolExecutionResponse(msgspec.Struct, tag="tool_execution"):
    tool_result: ToolResultType


class ErrorResponse(msgspec.Struct, tag="error"):
    error_message: str


class CliRpcResponse(msgspec.Struct):
    request_id: str
    response: (
        ToolExecutionResponse
        | GetAllFilesResponse
        | ErrorResponse
        | TerminateResponse
        | BatchToolExecutionResponse
        | HttpResponse
        | SwitchCLIChatResponse
    )
