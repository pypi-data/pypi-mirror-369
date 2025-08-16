"""Rich-styled logging configuration for Monkeybox agents."""

import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console()

rich_handler = RichHandler(
    console=console,
    show_time=True,
    show_path=False,
    rich_tracebacks=True,
    markup=True,
)

logger = logging.getLogger("monkeybox")
logger.setLevel(logging.INFO)
logger.addHandler(rich_handler)

formatter = logging.Formatter(
    fmt="%(message)s",
    datefmt="[%X]",
)
rich_handler.setFormatter(formatter)


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance with rich styling."""
    if name:
        return logging.getLogger(f"monkeybox.{name}")
    return logger


class MonkeyboxLogger:
    """Rich-styled logging helper for all Monkeybox operations."""

    def __init__(self, name: str, verbose: bool = True):
        self.logger = get_logger(name)
        self.name = name
        self.verbose = verbose

    def log_user_input(self, message: str) -> None:
        """Log user input with proper formatting."""
        if self.verbose:
            self.logger.info(f"[bold blue]User:[/bold blue] {message}")

    def log_step(self, step: int, max_steps: int) -> None:
        """Log step progress."""
        if self.verbose:
            self.logger.info(f"[bold white on blue] Step {step}/{max_steps} [/bold white on blue]")

    def log_thinking(self, agent_name: str, model_name: str, thinking: str) -> None:
        """Log agent thinking/reasoning."""
        if self.verbose:
            self.logger.info(
                f"[bold yellow]Thinking [{agent_name} | {model_name}]:[/bold yellow] {thinking}",
            )

    def log_tool_call(self, tool_name: str, args: dict, tool_id: str) -> None:
        """Log tool call with arguments."""
        if self.verbose:
            if args:
                joined_args = ", ".join(f"{k}={v}" for k, v in args.items())
                if len(joined_args) > 50:
                    args_summary = f" ({joined_args[:50]}...)"
                else:
                    args_summary = f" ({joined_args})"
            else:
                args_summary = ""
            self.logger.info(f"[bold magenta]Tool:[/bold magenta] {tool_name}{args_summary}")

    def log_tool_result(self, result: str) -> None:
        """Log tool result."""
        if self.verbose:
            result_summary = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            self.logger.info(f"[bold green]Result:[/bold green] {result_summary}")

    def log_agent_call(self, agent_name: str, model_name: str) -> None:
        """Log agent delegation."""
        if self.verbose:
            self.logger.info(f"[bold yellow]Calling [{agent_name} | {model_name}]:[/bold yellow]")

    def log_agent_completion(self, agent_name: str, model_name: str) -> None:
        """Log agent completion."""
        if self.verbose:
            self.logger.info(f"[bold green]Completed [{agent_name} | {model_name}]:[/bold green]")

    def log_assistant_response(self, agent_name: str, model_name: str, message: str) -> None:
        """Log assistant response."""
        if self.verbose:
            message_summary = message[:200] + "..." if len(message) > 200 else message
            self.logger.info(
                f"[bold cyan]{agent_name} | {model_name}:[/bold cyan] {message_summary}",
            )

    def log_final_response(self, response: str) -> None:
        """Log final response."""
        if self.verbose:
            self.logger.info(f"[bold white]Final:[/bold white] {response}")

    def log_error(self, error: str) -> None:
        """Log error with proper formatting."""
        # Errors are always logged regardless of verbose setting
        self.logger.error(f"[bold red]Error:[/bold red] {error}")

    def log_max_steps_reached(self, max_steps: int) -> None:
        """Log when maximum steps are reached."""
        # This is an error condition, so always log it
        self.log_error(f"Reached maximum steps ({max_steps}) without completing the task")

    def log_mcp_connect(self, server_name: str, transport: str) -> None:
        """Log MCP server connection."""
        if self.verbose:
            self.logger.info(f"[bold green]MCP Connect:[/bold green] {server_name} via {transport}")

    def log_mcp_connect_success(self, server_name: str) -> None:
        """Log successful MCP connection."""
        if self.verbose:
            self.logger.info(f"[bold green]MCP Connected:[/bold green] {server_name}")

    def log_mcp_discover_tools(self, server_name: str, tool_names: list) -> None:
        """Log tool discovery."""
        if self.verbose:
            self.logger.info(
                f"[bold yellow]MCP Tools:[/bold yellow] {server_name} found {len(tool_names)} tools",
            )

    def log_mcp_tool_conflict(self, server_name: str, tool_name: str) -> None:
        """Log tool name conflict."""
        # Warnings are always shown regardless of verbose setting
        self.logger.warning(
            f"[bold orange]MCP Warning:[/bold orange] Tool conflict {tool_name} in {server_name}",
        )

    def log_mcp_error(self, server_name: str, error: str) -> None:
        """Log MCP error."""
        # Errors are always shown regardless of verbose setting
        self.logger.error(f"[bold red]MCP Error:[/bold red] {server_name} - {error}")

    def log_mcp_warning(self, context: str, message: str) -> None:
        """Log MCP warning."""
        # Warnings are always shown regardless of verbose setting
        self.logger.warning(f"[bold orange]MCP Warning:[/bold orange] {context} - {message}")

    def log_mcp_setup(self, tool_count: int) -> None:
        """Log MCP setup with tool count."""
        if not self.verbose:
            return
        self.logger.info(f"[bold blue]MCP Setup:[/bold blue] Loaded {tool_count} tools")

    def log_mcp_cleanup(self) -> None:
        """Log MCP cleanup."""
        if not self.verbose:
            return
        self.logger.info("[bold blue]MCP Cleanup:[/bold blue] Released MCP resources")
