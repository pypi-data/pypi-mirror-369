"""MCP client implementation for Monkeybox."""

import asyncio
import sys
from collections.abc import Callable
from contextlib import AsyncExitStack
from dataclasses import dataclass
from enum import Enum
from itertools import chain
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CallToolResult
from mcp.types import Tool as MCPTool

from .exceptions import (
    MCPConnectionError,
    MCPError,
    MCPInitializationError,
    MCPProtocolError,
    MCPToolCallError,
    MCPToolDiscoveryError,
    MCPToolExecutionError,
    MCPToolTimeoutError,
)
from .logger import MonkeyboxLogger


class MCPTransport(Enum):
    """Supported MCP transport types."""

    STDIO = "stdio"
    HTTP = "http"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection."""

    name: str
    transport: MCPTransport | str = MCPTransport.STDIO
    command: str | None = None
    args: list[str] | None = None
    env: dict[str, str] | None = None
    url: str | None = None
    headers: dict[str, str] | None = None
    connection_timeout: float = 30.0  # seconds
    tool_timeout: float = 60.0  # seconds

    def __post_init__(self):
        """Convert string transport to enum if needed and validate timeouts."""
        if isinstance(self.transport, str):
            try:
                self.transport = MCPTransport(self.transport)
            except ValueError:
                raise ValueError(
                    f"Invalid transport: {self.transport}. Must be one of: {[t.value for t in MCPTransport]}",
                )

        # Validate timeout values
        if self.connection_timeout <= 0:
            raise ValueError(f"connection_timeout must be positive, got {self.connection_timeout}")
        if self.tool_timeout <= 0:
            raise ValueError(f"tool_timeout must be positive, got {self.tool_timeout}")


class _MCPClient:
    """Private MCP client that integrates with Monkeybox's tool system."""

    def __init__(self, exit_stack: AsyncExitStack):
        self.logger = MonkeyboxLogger("mcp")
        self.sessions: dict[str, ClientSession] = {}
        self.tools: list[Callable] = []
        self.exit_stack = exit_stack
        self._server_configs: dict[str, MCPServerConfig] = {}

    async def connect(self, configs: list[MCPServerConfig] | MCPServerConfig) -> None:
        """Connect to one or more MCP servers.

        Args:
            configs: List of MCP server configurations to connect to.

        """
        if isinstance(configs, MCPServerConfig):
            configs = [configs]

        seen_names = set()
        for config in configs:
            if not isinstance(config, MCPServerConfig):
                raise TypeError(f"Expected MCPServerConfig, got {type(config).__name__}")

            if config.name in seen_names:
                raise ValueError(
                    f"Duplicate server name '{config.name}' in configuration list. "
                    f"Each server must have a unique name.",
                )
            seen_names.add(config.name)

        for config in configs:
            await self._connect_server(config)
            # Store config for later use in tool creation
            self._server_configs[config.name] = config

        await self._discover_tools()

    async def _connect_server(self, config: MCPServerConfig) -> None:
        """Connect to a single MCP server."""
        if config.name in self.sessions:
            raise ValueError(
                f"MCP server with name '{config.name}' already connected. "
                f"Each server must have a unique name.",
            )

        transport_value = (
            config.transport.value
            if isinstance(config.transport, MCPTransport)
            else config.transport
        )
        self.logger.log_mcp_connect(config.name, transport_value)

        if config.transport == MCPTransport.STDIO:
            if not config.command:
                raise ValueError(f"Command required for stdio transport in {config.name}")

            server_params = StdioServerParameters(
                command=config.command,
                args=config.args or [],
                env=config.env,
            )
            try:
                transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                read_stream, write_stream = transport
            except Exception as e:
                raise MCPConnectionError(config.name, e)

        elif config.transport == MCPTransport.HTTP:
            if not config.url:
                raise ValueError(f"URL required for HTTP transport in {config.name}")

            try:
                transport = await self.exit_stack.enter_async_context(
                    streamablehttp_client(url=config.url, headers=config.headers or {}),
                )
                read_stream, write_stream, _status_func = transport
            except Exception as e:
                raise MCPConnectionError(config.name, e)

        else:
            raise ValueError(f"Unsupported transport: {config.transport}")

        try:
            session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream),
            )
        except Exception as e:
            raise MCPConnectionError(config.name, e)

        try:
            await asyncio.wait_for(session.initialize(), timeout=config.connection_timeout)
        except TimeoutError:
            raise MCPInitializationError(
                config.name,
                Exception(f"Timed out after {config.connection_timeout}s"),
            )
        except Exception as e:
            raise MCPInitializationError(config.name, e)

        self.sessions[config.name] = session
        self.logger.log_mcp_connect_success(config.name)

    def _create_mcp_tool_func(
        self,
        tool_obj: MCPTool,
        session_obj: ClientSession,
        server_name: str,
        config: MCPServerConfig,
    ) -> Callable[..., Any]:
        """Create a callable tool function from an MCP tool definition."""
        tool_name = f"{server_name}_{tool_obj.name}"
        tool_doc = tool_obj.description or f"MCP tool {tool_obj.name} from {server_name}"
        tool_schema = tool_obj.inputSchema

        async def mcp_tool_func(**kwargs: Any) -> str:
            try:
                # Validate session is still active
                if server_name not in self.sessions:
                    raise MCPToolCallError(
                        server_name,
                        tool_obj.name,
                        Exception("Session is no longer active"),
                    )

                result: CallToolResult = await asyncio.wait_for(
                    session_obj.call_tool(tool_obj.name, kwargs),
                    timeout=config.tool_timeout,
                )

                # Handle different content structures
                if not result.content:
                    content = ""
                elif isinstance(result.content, list):
                    # Handle list of content items
                    content_parts = []
                    for item in result.content:
                        if hasattr(item, "text") and item.text is not None:
                            content_parts.append(item.text)
                        elif hasattr(item, "data") and hasattr(item, "mimeType"):
                            # Handle embedded resources
                            content_parts.append(f"[{item.mimeType} data]")
                        else:
                            content_parts.append(str(item))
                    content = " ".join(content_parts)
                # Handle single content item
                elif hasattr(result.content, "text"):
                    content = result.content.text
                else:
                    content = str(result.content)

                if result.isError:
                    return f"Error calling {tool_obj.name}: {content}"
                return content

            except TimeoutError:
                self.logger.log_mcp_error(
                    server_name,
                    f"Tool {tool_obj.name} timed out after {config.tool_timeout}s",
                )
                raise MCPToolTimeoutError(server_name, tool_obj.name, config.tool_timeout)
            except MCPToolCallError:
                raise  # Re-raise MCP-specific errors
            except Exception as e:
                self.logger.log_mcp_error(
                    server_name,
                    f"Failed to call tool {tool_obj.name}: {e!s}",
                )
                raise MCPToolExecutionError(server_name, tool_obj.name, e)

        mcp_tool_func.__name__ = tool_name
        mcp_tool_func.__doc__ = tool_doc
        # Store schema as a private attribute with proper typing
        setattr(mcp_tool_func, "_input_schema", tool_schema)
        return mcp_tool_func

    async def _discover_tools(self) -> None:
        """Discover and wrap all tools from connected servers."""
        self.tools = []

        for server_name, session in self.sessions.items():
            try:
                tools_list = await session.list_tools()
                if not hasattr(tools_list, "tools"):
                    raise MCPProtocolError(
                        server_name,
                        "Invalid tool list response: missing 'tools' attribute",
                    )
            except Exception as e:
                if isinstance(e, MCPProtocolError):
                    raise
                raise MCPToolDiscoveryError(server_name, e)

            tool_names = [t.name for t in tools_list.tools]
            self.logger.log_mcp_discover_tools(server_name, tool_names)

            for tool in tools_list.tools:
                # Get the config for this server
                config = self._server_configs.get(server_name)
                if not config:
                    raise MCPToolDiscoveryError(
                        server_name,
                        Exception("No config found for server"),
                    )

                tool_func = self._create_mcp_tool_func(tool, session, server_name, config)

                if any(
                    existing_tool.__name__ == tool_func.__name__ for existing_tool in self.tools
                ):
                    self.logger.log_mcp_tool_conflict(server_name, tool_func.__name__)

                self.tools.append(tool_func)

    def get_tools(self) -> list[Callable]:
        """Get all discovered tools as callable functions."""
        return self.tools


class MCPContext:
    """Context manager for MCP server connections.

    Manages lifecycle of multiple MCP server connections and provides
    easy access to their tools.

    Example:
        async with MCPContext(filesystem_config, database_config) as mcp:
            fs_tools = mcp.get_tools("filesystem")
            all_tools = mcp.get_tools()

            agent = Agent(model, prompt, tools=all_tools)
            await agent.run("Do something")

    """

    def __init__(self, *configs: MCPServerConfig):
        """Initialize MCP context with server configurations.

        Args:
            *configs: Variable number of MCPServerConfig instances

        Raises:
            ValueError: If duplicate server names are provided

        """
        # Check for duplicate server names
        names = [config.name for config in configs]
        if len(names) != len(set(names)):
            duplicates = [name for name in names if names.count(name) > 1]
            raise ValueError(f"Duplicate server names found: {', '.join(set(duplicates))}")

        self.configs = {config.name: config for config in configs}
        self.clients: dict[str, _MCPClient] = {}
        self.tools: dict[str, list[Callable]] = {}
        self.exit_stack: AsyncExitStack | None = None

    async def __aenter__(self):
        """Connect to all configured MCP servers."""
        self.exit_stack = AsyncExitStack()
        await self.exit_stack.__aenter__()

        connected_servers = []
        try:
            for name, config in self.configs.items():
                client = _MCPClient(self.exit_stack)
                await client.connect(config)
                connected_servers.append(name)
                self.clients[name] = client
                self.tools[name] = client.get_tools()
            return self
        except Exception as e:
            # Log which servers were successfully connected before failure
            logger = MonkeyboxLogger("mcp")
            if connected_servers:
                logger.log_mcp_error(
                    "MCPContext",
                    f"Failed during connection. Successfully connected: {', '.join(connected_servers)}",
                )
            await self.exit_stack.__aexit__(*sys.exc_info())
            if isinstance(e, MCPError):
                raise  # Re-raise MCP-specific errors
            # Create a more specific error message
            failed_server = (
                list(self.configs.keys())[len(connected_servers)]
                if len(connected_servers) < len(self.configs)
                else "unknown"
            )
            raise MCPConnectionError(failed_server, e)

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        """Disconnect from all MCP servers."""
        cleanup_errors = []

        if self.exit_stack:
            try:
                await self.exit_stack.__aexit__(_exc_type, _exc_val, _exc_tb)
            except Exception as e:
                cleanup_errors.append(f"Exit stack cleanup failed: {e}")

        try:
            self.clients.clear()
            self.tools.clear()
        except Exception as e:
            cleanup_errors.append(f"Resource cleanup failed: {e}")

        if cleanup_errors:
            logger = MonkeyboxLogger("mcp")
            for error in cleanup_errors:
                logger.log_mcp_error("MCPContext", error)

    def get_tools(self, *server_names: str) -> list[Callable]:
        """Get tools from specified servers or all servers.

        Args:
            *server_names: Names of servers to get tools from.
                          If none specified, returns all tools.

        Returns:
            List of callable tool functions

        """
        if not server_names:
            # Return all tools from all servers
            return list(chain.from_iterable(self.tools.values()))

        invalid_names = [name for name in server_names if name not in self.tools]
        if invalid_names:
            logger = MonkeyboxLogger("mcp")
            logger.log_mcp_warning(
                "MCPContext",
                f"No servers found with names: {', '.join(invalid_names)}",
            )

        return list(
            chain.from_iterable(self.tools[name] for name in server_names if name in self.tools),
        )
