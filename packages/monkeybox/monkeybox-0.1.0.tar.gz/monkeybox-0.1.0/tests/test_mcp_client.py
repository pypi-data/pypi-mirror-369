"""Tests for the MCP client."""

from contextlib import AsyncExitStack
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from monkeybox.core.exceptions import MCPToolDiscoveryError, MCPToolExecutionError
from monkeybox.core.mcp_client import MCPContext, MCPServerConfig, MCPTransport, _MCPClient


@pytest.fixture
def mock_mcp_tool():
    """Mock MCP tool object."""
    tool = Mock()
    tool.name = "test_tool"
    tool.description = "Test MCP tool"
    tool.inputSchema = {"type": "object", "properties": {"query": {"type": "string"}}}
    return tool


@pytest.fixture
def mock_session():
    """Mock MCP session."""
    session = Mock()
    session.initialize = AsyncMock()
    session.list_tools = AsyncMock()
    session.call_tool = AsyncMock()
    return session


@pytest.fixture
def mock_exit_stack():
    """Mock AsyncExitStack."""

    exit_stack = Mock(spec=AsyncExitStack)
    exit_stack.enter_async_context = AsyncMock()
    exit_stack.__aenter__ = AsyncMock()
    exit_stack.__aexit__ = AsyncMock()
    return exit_stack


@pytest.mark.parametrize(
    "transport_type,config_params,expected_attrs",
    [
        (
            "stdio",
            {"command": "npx", "args": ["-y", "server"]},
            {"command": "npx", "transport": MCPTransport.STDIO},
        ),
        (
            "http",
            {"url": "https://example.com/mcp"},
            {"url": "https://example.com/mcp", "transport": MCPTransport.HTTP},
        ),
        (
            MCPTransport.STDIO,
            {"command": "test_cmd"},
            {"command": "test_cmd", "transport": MCPTransport.STDIO},
        ),
        (
            MCPTransport.HTTP,
            {"url": "https://test.com"},
            {"url": "https://test.com", "transport": MCPTransport.HTTP},
        ),
    ],
)
def test_server_config_validation(transport_type, config_params, expected_attrs):
    """MCPServerConfig validates all transport types and required fields."""
    config = MCPServerConfig(name="test_server", transport=transport_type, **config_params)

    assert config.name == "test_server"
    for attr, expected_value in expected_attrs.items():
        assert getattr(config, attr) == expected_value


def test_server_config_invalid_transport():
    """MCPServerConfig rejects invalid transport types."""
    with pytest.raises(ValueError, match="Invalid transport"):
        MCPServerConfig(name="bad", transport="invalid")


def test_server_config_with_env():
    """MCPServerConfig accepts environment variables."""
    config = MCPServerConfig(
        name="env_server",
        transport="stdio",
        command="npx",
        env={"API_KEY": "secret", "DEBUG": "true"},
    )
    assert config.env["API_KEY"] == "secret"
    assert config.env["DEBUG"] == "true"


@pytest.mark.asyncio
async def test_context_manager():
    """MCPContext enters/exits cleanly."""
    config = MCPServerConfig(name="test", transport="stdio", command="echo", args=["hello"])

    with patch("monkeybox.core.mcp_client._MCPClient") as mock_client_class:
        with patch("monkeybox.core.mcp_client.AsyncExitStack") as mock_exit_stack_class:
            mock_client = Mock()
            mock_client.connect = AsyncMock()
            mock_tool = Mock()
            mock_tool.__name__ = "test_tool"
            mock_client.get_tools.return_value = [mock_tool]
            mock_client_class.return_value = mock_client

            mock_exit_stack = Mock()
            mock_exit_stack.__aenter__ = AsyncMock(return_value=mock_exit_stack)
            mock_exit_stack.__aexit__ = AsyncMock(return_value=None)
            mock_exit_stack_class.return_value = mock_exit_stack

            async with MCPContext(config) as mcp_context:
                # Verify context manager setup
                assert mcp_context is not None
                assert mcp_context.clients.get(config.name) == mock_client

                # Verify tools are stored correctly
                assert mcp_context.tools.get(config.name) == [mock_tool]

                assert mock_client.sessions.get(config.name) is not None

                # Verify client methods are called
                mock_client.connect.assert_called_once_with(config)
                mock_client.get_tools.assert_called_once()

                # Verify exit stack is properly managed
                mock_exit_stack.__aenter__.assert_called_once()

            # Verify proper cleanup on exit
            mock_exit_stack.__aexit__.assert_called_once()


@pytest.mark.parametrize(
    "num_servers,tools_per_server,filter_server",
    [
        (1, 1, None),  # 1 server, 1 tool, get all
        (1, 1, "server1"),  # 1 server, 1 tool, filter by server
        (1, 2, None),  # 1 server, 2 tools
        (2, 1, None),  # 2 servers, 1 tool each
        (2, 2, None),  # 2 servers, 2 tools each
        (2, 3, "server2"),  # 2 servers, 3 tools each, filter second server
        (3, 1, None),  # 3 servers, 1 tool each
        (3, 2, "server1"),  # 3 servers, 2 tools each, filter first server
    ],
)
def test_tool_discovery(num_servers, tools_per_server, filter_server):
    """Test get_tools() with various server and tool combinations."""
    with patch("monkeybox.core.mcp_client._MCPClient") as mock_client_class:
        # Create servers and tools
        servers = {}
        all_tools = {}

        for i in range(1, num_servers + 1):
            server_name = f"server{i}"
            server_tools = []

            for j in range(1, tools_per_server + 1):
                tool = Mock()
                tool.__name__ = f"{server_name}_tool{j}"
                server_tools.append(tool)

            mock_client = Mock()
            mock_client.get_tools.return_value = server_tools
            servers[server_name] = mock_client
            all_tools[server_name] = server_tools

        mock_client_class.return_value = mock_client

        context = MCPContext()
        context.clients = servers
        context.tools = all_tools

        # Test getting tools
        if filter_server:
            tools = context.get_tools(filter_server)
            expected_count = tools_per_server if filter_server in all_tools else 0
            assert len(tools) == expected_count
            if expected_count > 0:
                # Verify we got the right server's tools
                for tool in tools:
                    assert tool.__name__.startswith(filter_server)
        else:
            # Get all tools
            tools = context.get_tools()
            expected_total = num_servers * tools_per_server
            assert len(tools) == expected_total

            # Verify we got tools from all servers
            tool_names = {tool.__name__ for tool in tools}
            for server_name, server_tools in all_tools.items():
                for tool in server_tools:
                    assert tool.__name__ in tool_names


@pytest.mark.asyncio
async def test_mcp_client_init(mock_exit_stack):
    """Test _MCPClient initialization."""

    client = _MCPClient(mock_exit_stack)

    assert client.sessions == {}
    assert client.tools == []
    assert client.exit_stack == mock_exit_stack
    assert client.logger.name == "mcp"


@pytest.mark.parametrize(
    "transport,config_params,mock_transport_func,expected_error",
    [
        (MCPTransport.STDIO, {"command": "test_cmd", "args": ["--arg1"]}, "stdio_client", None),
        (
            MCPTransport.HTTP,
            {"url": "https://example.com/mcp", "headers": {"Auth": "Bearer token"}},
            "streamablehttp_client",
            None,
        ),
        (
            MCPTransport.STDIO,
            {"command": None},
            "stdio_client",
            "Command required for stdio transport",
        ),
        (
            MCPTransport.HTTP,
            {"url": None},
            "streamablehttp_client",
            "URL required for HTTP transport",
        ),
    ],
)
@pytest.mark.asyncio
async def test_mcp_client_server_connection(
    mock_exit_stack, mock_session, transport, config_params, mock_transport_func, expected_error
):
    """Test MCP client server connections for all transport types and error cases."""

    client = _MCPClient(mock_exit_stack)
    config = MCPServerConfig(name="test_server", transport=transport, **config_params)

    if expected_error:
        with pytest.raises(ValueError, match=expected_error):
            await client._connect_server(config)
    else:
        # Mock the transport layer
        transport_return = (
            (Mock(), Mock(), Mock()) if transport == MCPTransport.HTTP else (Mock(), Mock())
        )

        with patch(f"monkeybox.core.mcp_client.{mock_transport_func}") as mock_transport:
            with patch("monkeybox.core.mcp_client.ClientSession") as mock_client_session:
                mock_transport.return_value = transport_return
                mock_exit_stack.enter_async_context.side_effect = [transport_return, mock_session]
                mock_client_session.return_value = mock_session

                await client._connect_server(config)

                assert client.sessions.get(config.name) == mock_session
                mock_session.initialize.assert_called_once()


@pytest.mark.parametrize(
    "mock_result_config,expected_result",
    [
        ({"content": "Tool execution result", "isError": False}, "Tool execution result"),
        (
            {"content": "Tool error occurred", "isError": True},
            "Error calling test_tool: Tool error occurred",
        ),
        ({"content": None, "isError": False}, ""),
        ("exception", MCPToolExecutionError),  # Now raises exception instead of returning string
    ],
)
@pytest.mark.asyncio
async def test_mcp_tool_execution(
    mock_exit_stack, mock_session, mock_mcp_tool, mock_result_config, expected_result
):
    """Test MCP tool creation and execution with all result scenarios."""

    client = _MCPClient(mock_exit_stack)
    # Add the session to the client's sessions dict so validation passes
    client.sessions["test_server"] = mock_session

    if mock_result_config == "exception":
        mock_session.call_tool.side_effect = Exception("Connection failed")
    else:
        mock_result = Mock()
        mock_result.content = mock_result_config["content"]
        mock_result.isError = mock_result_config["isError"]
        mock_session.call_tool.return_value = mock_result

    # Create a config for the tool creation
    config = MCPServerConfig(name="test_server")
    tool_func = client._create_mcp_tool_func(mock_mcp_tool, mock_session, "test_server", config)

    # Handle exception case differently
    if isinstance(expected_result, type) and issubclass(expected_result, Exception):
        with pytest.raises(expected_result):
            await tool_func(query="test query")
    else:
        result = await tool_func(query="test query")
        assert result == expected_result

    assert tool_func.__name__ == f"test_server_{mock_mcp_tool.name}"
    assert hasattr(tool_func, "_input_schema")


@pytest.mark.asyncio
async def test_mcp_discover_tools(mock_exit_stack, mock_mcp_tool):
    """Test tool discovery process."""

    client = _MCPClient(mock_exit_stack)

    # Set up the session and server config before discovery
    mock_session = AsyncMock()
    tools_response = Mock()
    tools_response.tools = [mock_mcp_tool]
    mock_session.list_tools.return_value = tools_response

    client.sessions["test_server"] = mock_session
    client._server_configs["test_server"] = MCPServerConfig(name="test_server")

    await client._discover_tools()

    assert len(client.tools) == 1
    tool_func = client.tools[0]
    assert tool_func.__name__ == f"test_server_{mock_mcp_tool.name}"
    assert hasattr(tool_func, "_input_schema")

    # test missing config
    client._server_configs = {}
    with pytest.raises(MCPToolDiscoveryError, match="No config found for server"):
        await client._discover_tools()


@pytest.mark.asyncio
async def test_mcp_client_multiple_servers_connection(mock_exit_stack):
    """Test connecting to multiple MCP servers with different transport types."""

    configs = [
        MCPServerConfig(name="stdio_server", transport="stdio", command="echo", args=["hello"]),
        MCPServerConfig(name="http_server", transport="http", url="https://example.com/mcp"),
    ]

    def create_session_with_tools(tools=None):
        session = Mock()
        session.initialize = AsyncMock()
        session.list_tools = AsyncMock(return_value=Mock(tools=tools or []))
        return session

    client = _MCPClient(mock_exit_stack)

    def mock_tool1():
        return "tool1"

    def mock_tool2():
        return "tool2"

    mock_tool1.__name__ = "tool1"
    mock_tool2.__name__ = "tool2"

    with patch("monkeybox.core.mcp_client.stdio_client", return_value=(Mock(), Mock())):
        with patch(
            "monkeybox.core.mcp_client.streamablehttp_client", return_value=(Mock(), Mock(), Mock())
        ):
            with patch(
                "monkeybox.core.mcp_client.ClientSession",
                side_effect=[create_session_with_tools(), create_session_with_tools()],
            ):
                mock_exit_stack.enter_async_context = AsyncMock(side_effect=lambda x: x)

                await client.connect(configs)

                # Test multiple server connections
                assert len(client.sessions) == 2
                assert "stdio_server" in client.sessions
                assert "http_server" in client.sessions

                # Test get_tools method after populating tools
                client.tools = [mock_tool1, mock_tool2]
                all_tools = client.get_tools()
                assert len(all_tools) == 2
                assert mock_tool1 in all_tools
                assert mock_tool2 in all_tools


@pytest.mark.parametrize(
    "num_servers,server_configs",
    [
        (1, [("single_server", "stdio", {"command": "echo"})]),
        (
            2,
            [
                ("server1", "stdio", {"command": "echo"}),
                ("server2", "http", {"url": "https://example.com"}),
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_mcp_context_lifecycle(num_servers, server_configs):
    """Test MCPContext manager lifecycle with single and multiple servers."""
    configs = [
        MCPServerConfig(name=name, transport=transport, **params)
        for name, transport, params in server_configs
    ]

    def create_mock_tool(name):
        def tool():
            pass

        tool.__name__ = name
        return tool

    tools = [create_mock_tool(f"{name}_tool") for name, _, _ in server_configs]

    with patch("monkeybox.core.mcp_client._MCPClient") as mock_client_class:
        mock_clients = []
        for i in range(num_servers):
            mock_client = Mock()
            mock_client.connect = AsyncMock()
            mock_client.get_tools.return_value = [tools[i]] if i < len(tools) else []
            mock_clients.append(mock_client)

        mock_client_class.side_effect = mock_clients

        with patch("monkeybox.core.mcp_client.AsyncExitStack") as mock_exit_stack_class:
            mock_exit_stack = Mock()
            mock_exit_stack.__aenter__ = AsyncMock()
            mock_exit_stack.__aexit__ = AsyncMock()
            mock_exit_stack_class.return_value = mock_exit_stack

            async with MCPContext(*configs) as context:
                assert len(context.clients) == num_servers
                for name, _, _ in server_configs:
                    assert name in context.clients

                for i, (name, _, _) in enumerate(server_configs):
                    server_tools = context.get_tools(name)
                    assert len(server_tools) == 1  # Each server has 1 tool
                    assert server_tools[0] == tools[i]

                # Test getting all tools
                all_tools = context.get_tools()
                assert len(all_tools) == num_servers  # Each server contributes 1 tool

                # Verify all tools are included
                for tool in tools:
                    assert tool in all_tools

            # Verify cleanup
            mock_exit_stack.__aexit__.assert_called_once()


def test_mcp_context_duplicate_names():
    """Test MCPContext raises error for duplicate server names."""
    config1 = MCPServerConfig(name="duplicate", transport="stdio", command="echo")
    config2 = MCPServerConfig(name="duplicate", transport="http", url="https://example.com")
    config3 = MCPServerConfig(name="unique", transport="stdio", command="cat")

    # Test duplicate names raise ValueError
    with pytest.raises(ValueError, match="Duplicate server names found: duplicate"):
        MCPContext(config1, config2)

    # Test multiple duplicates
    with pytest.raises(ValueError, match="Duplicate server names found: duplicate"):
        MCPContext(config1, config2, config3, config1)

    # Test no duplicates works fine
    context = MCPContext(config1, config3)
    assert "duplicate" in context.configs
    assert "unique" in context.configs


@pytest.mark.asyncio
async def test_connection_timeout_stdio(mock_exit_stack):
    """Test connection timeout for STDIO transport during initialization."""
    import asyncio

    from monkeybox.core.exceptions import MCPInitializationError

    config = MCPServerConfig(
        name="test_server",
        transport=MCPTransport.STDIO,
        command="test_command",
        connection_timeout=0.1,  # 100ms timeout
    )

    client = _MCPClient(mock_exit_stack)

    # Mock successful connection but slow initialization
    mock_session = MagicMock()

    async def slow_init():
        await asyncio.sleep(1)  # Sleep longer than timeout

    mock_session.initialize = slow_init

    with patch("monkeybox.core.mcp_client.stdio_client"):
        with patch("monkeybox.core.mcp_client.ClientSession"):
            mock_exit_stack.enter_async_context.side_effect = [
                (MagicMock(), MagicMock()),  # transport streams
                mock_session,  # session
            ]

            with pytest.raises(MCPInitializationError) as exc_info:
                await client._connect_server(config)

            assert "Timed out after 0.1s" in str(exc_info.value)


@pytest.mark.asyncio
async def test_connection_timeout_http(mock_exit_stack):
    """Test connection timeout for HTTP transport during initialization."""
    import asyncio

    from monkeybox.core.exceptions import MCPInitializationError

    config = MCPServerConfig(
        name="test_server",
        transport=MCPTransport.HTTP,
        url="http://test.com",
        connection_timeout=0.1,
    )

    client = _MCPClient(mock_exit_stack)

    # Mock successful connection but slow initialization
    mock_session = MagicMock()

    async def slow_init():
        await asyncio.sleep(1)

    mock_session.initialize = slow_init

    with patch("monkeybox.core.mcp_client.streamablehttp_client"):
        with patch("monkeybox.core.mcp_client.ClientSession"):
            mock_exit_stack.enter_async_context.side_effect = [
                (MagicMock(), MagicMock(), MagicMock()),  # transport streams + status func
                mock_session,  # session
            ]

            with pytest.raises(MCPInitializationError) as exc_info:
                await client._connect_server(config)

            assert "Timed out after 0.1s" in str(exc_info.value)


@pytest.mark.asyncio
async def test_connection_error_stdio(mock_exit_stack):
    """Test connection error handling for STDIO transport."""
    from monkeybox.core.exceptions import MCPConnectionError

    config = MCPServerConfig(
        name="test_server", transport=MCPTransport.STDIO, command="test_command"
    )

    client = _MCPClient(mock_exit_stack)

    # Mock stdio_client to raise an error
    with patch("monkeybox.core.mcp_client.stdio_client"):
        mock_exit_stack.enter_async_context.side_effect = Exception("Network error")

        with pytest.raises(MCPConnectionError) as exc_info:
            await client._connect_server(config)

        assert "Failed to connect to MCP server 'test_server'" in str(exc_info.value)
        assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_session_initialization_timeout(mock_exit_stack):
    """Test session initialization timeout."""
    import asyncio

    from monkeybox.core.exceptions import MCPInitializationError

    config = MCPServerConfig(
        name="test_server",
        transport=MCPTransport.STDIO,
        command="test_command",
        connection_timeout=0.1,
    )

    client = _MCPClient(mock_exit_stack)

    # Mock successful connection but slow initialization
    mock_transport = (AsyncMock(), AsyncMock())
    mock_session = AsyncMock()

    async def slow_init():
        await asyncio.sleep(1)

    mock_session.initialize = slow_init

    with patch("monkeybox.core.mcp_client.stdio_client"):
        with patch("monkeybox.core.mcp_client.ClientSession"):
            mock_exit_stack.enter_async_context.side_effect = [
                mock_transport,  # First call for transport
                mock_session,  # Second call for session
            ]

            with pytest.raises(MCPInitializationError) as exc_info:
                await client._connect_server(config)

            assert "test_server" in str(exc_info.value)
            assert "Timed out after 0.1s" in str(exc_info.value)


@pytest.mark.asyncio
async def test_session_initialization_error(mock_exit_stack):
    """Test session initialization error handling."""
    from monkeybox.core.exceptions import MCPInitializationError

    config = MCPServerConfig(
        name="test_server", transport=MCPTransport.STDIO, command="test_command"
    )

    client = _MCPClient(mock_exit_stack)

    mock_transport = (AsyncMock(), AsyncMock())
    mock_session = AsyncMock()
    mock_session.initialize.side_effect = Exception("Init failed")

    with patch("monkeybox.core.mcp_client.stdio_client"):
        with patch("monkeybox.core.mcp_client.ClientSession"):
            mock_exit_stack.enter_async_context.side_effect = [
                mock_transport,  # First call for transport
                mock_session,  # Second call for session
            ]

            with pytest.raises(MCPInitializationError) as exc_info:
                await client._connect_server(config)

            assert "Failed to initialize MCP server 'test_server'" in str(exc_info.value)
            assert "Init failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tool_discovery_protocol_error(mock_exit_stack):
    """Test tool discovery with protocol error."""
    from monkeybox.core.exceptions import MCPProtocolError

    client = _MCPClient(mock_exit_stack)

    # Create a mock session with invalid response
    mock_session = AsyncMock()
    mock_session.list_tools.return_value = Mock(spec=[])  # Missing 'tools' attribute

    client.sessions = {"test_server": mock_session}
    client._server_configs = {"test_server": MCPServerConfig(name="test_server")}

    with pytest.raises(MCPProtocolError) as exc_info:
        await client._discover_tools()

    assert "MCP protocol error with server 'test_server'" in str(exc_info.value)
    assert "missing 'tools' attribute" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tool_discovery_error(mock_exit_stack):
    """Test tool discovery general error."""
    from monkeybox.core.exceptions import MCPToolDiscoveryError

    client = _MCPClient(mock_exit_stack)

    mock_session = AsyncMock()
    mock_session.list_tools.side_effect = Exception("Discovery failed")

    client.sessions = {"test_server": mock_session}
    client._server_configs = {"test_server": MCPServerConfig(name="test_server")}

    with pytest.raises(MCPToolDiscoveryError) as exc_info:
        await client._discover_tools()

    assert "Failed to discover tools from MCP server 'test_server'" in str(exc_info.value)
    assert "Discovery failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tool_execution_timeout(mock_exit_stack):
    """Test tool execution timeout."""
    import asyncio

    from monkeybox.core.exceptions import MCPToolTimeoutError

    client = _MCPClient(mock_exit_stack)

    # Setup
    mock_session = AsyncMock()
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "Test tool"
    mock_tool.inputSchema = {}

    config = MCPServerConfig(name="test_server", tool_timeout=0.1)

    # Mock slow tool execution
    async def slow_tool(*args, **kwargs):
        await asyncio.sleep(1)

    mock_session.call_tool = slow_tool

    # Add session to client
    client.sessions["test_server"] = mock_session

    # Create tool function
    tool_func = client._create_mcp_tool_func(mock_tool, mock_session, "test_server", config)

    with pytest.raises(MCPToolTimeoutError) as exc_info:
        await tool_func()

    assert "MCP tool 'test_tool' on server 'test_server' timed out after 0.1 seconds" in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_tool_execution_error(mock_exit_stack):
    """Test tool execution error handling."""
    from monkeybox.core.exceptions import MCPToolExecutionError

    client = _MCPClient(mock_exit_stack)

    mock_session = AsyncMock()
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "Test tool"
    mock_tool.inputSchema = {}

    config = MCPServerConfig(name="test_server")

    # Mock tool execution failure
    mock_session.call_tool.side_effect = Exception("Execution failed")

    # Add session to client
    client.sessions["test_server"] = mock_session

    # Create tool function
    tool_func = client._create_mcp_tool_func(mock_tool, mock_session, "test_server", config)

    with pytest.raises(MCPToolExecutionError) as exc_info:
        await tool_func()

    assert "Failed to execute MCP tool 'test_tool' on server 'test_server'" in str(exc_info.value)
    assert "Execution failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_context_cleanup_error_logging(mock_exit_stack):
    """Test that cleanup errors are logged."""
    context = MCPContext(MCPServerConfig(name="test"))
    context.exit_stack = mock_exit_stack

    # Mock cleanup to fail
    mock_exit_stack.__aexit__.side_effect = Exception("Cleanup failed")

    # Capture logs
    with patch("monkeybox.core.mcp_client.MonkeyboxLogger") as mock_logger_class:
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        await context.__aexit__(None, None, None)

        # Verify error was logged
        mock_logger.log_mcp_error.assert_called_with(
            "MCPContext", "Exit stack cleanup failed: Cleanup failed"
        )


@pytest.mark.asyncio
async def test_tool_result_with_text_attribute(mock_exit_stack):
    """Test handling of tool results with text attribute."""
    client = _MCPClient(mock_exit_stack)

    # Setup
    mock_session = AsyncMock()
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "Test tool"
    mock_tool.inputSchema = {}

    config = MCPServerConfig(name="test_server")

    # Mock result with text attribute
    mock_content = Mock()
    mock_content.text = "Text content from tool"

    mock_result = Mock()
    mock_result.content = mock_content
    mock_result.isError = False

    mock_session.call_tool.return_value = mock_result

    # Add session to client
    client.sessions["test_server"] = mock_session

    # Create and call tool function
    tool_func = client._create_mcp_tool_func(mock_tool, mock_session, "test_server", config)
    result = await tool_func()

    assert result == "Text content from tool"


@pytest.mark.asyncio
async def test_tool_result_with_list_content(mock_exit_stack):
    """Test handling of tool results with list content."""
    client = _MCPClient(mock_exit_stack)

    # Setup
    mock_session = AsyncMock()
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "Test tool"
    mock_tool.inputSchema = {}

    config = MCPServerConfig(name="test_server")

    # Mock result with list content
    text_item = Mock()
    text_item.text = "First part"

    data_item = Mock(spec=["data", "mimeType"])  # Only has data and mimeType
    data_item.data = b"binary data"
    data_item.mimeType = "image/png"

    string_item = "Plain string"

    mock_result = Mock()
    mock_result.content = [text_item, data_item, string_item]
    mock_result.isError = False

    mock_session.call_tool.return_value = mock_result

    # Add session to client
    client.sessions["test_server"] = mock_session

    # Create and call tool function
    tool_func = client._create_mcp_tool_func(mock_tool, mock_session, "test_server", config)
    result = await tool_func()

    assert result == "First part [image/png data] Plain string"


@pytest.mark.asyncio
async def test_tool_result_with_embedded_resource(mock_exit_stack):
    """Test handling of embedded resources in tool results."""
    client = _MCPClient(mock_exit_stack)

    # Setup
    mock_session = AsyncMock()
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "Test tool"
    mock_tool.inputSchema = {}

    config = MCPServerConfig(name="test_server")

    # Mock result with embedded resource
    resource_item = Mock(spec=["data", "mimeType", "text"])
    resource_item.data = b"binary data"
    resource_item.mimeType = "application/pdf"
    resource_item.text = None  # Has attribute but is None

    mock_result = Mock()
    mock_result.content = [resource_item]
    mock_result.isError = False

    mock_session.call_tool.return_value = mock_result

    # Add session to client
    client.sessions["test_server"] = mock_session

    # Create and call tool function
    tool_func = client._create_mcp_tool_func(mock_tool, mock_session, "test_server", config)
    result = await tool_func()

    assert result == "[application/pdf data]"


@pytest.mark.asyncio
async def test_tool_result_string_conversion(mock_exit_stack):
    """Test string conversion for non-text content."""
    client = _MCPClient(mock_exit_stack)

    # Setup
    mock_session = AsyncMock()
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "Test tool"
    mock_tool.inputSchema = {}

    config = MCPServerConfig(name="test_server")

    # Mock result with object that needs string conversion
    mock_content = {"key": "value", "number": 42}

    mock_result = Mock()
    mock_result.content = mock_content
    mock_result.isError = False

    mock_session.call_tool.return_value = mock_result

    # Add session to client
    client.sessions["test_server"] = mock_session

    # Create and call tool function
    tool_func = client._create_mcp_tool_func(mock_tool, mock_session, "test_server", config)
    result = await tool_func()

    assert "key" in result
    assert "value" in result


@pytest.mark.asyncio
async def test_context_partial_connection_failure(mock_exit_stack):
    """Test MCPContext handling partial connection failures."""
    from monkeybox.core.exceptions import MCPConnectionError

    config1 = MCPServerConfig(name="server1", transport="stdio", command="cmd1")
    config2 = MCPServerConfig(name="server2", transport="stdio", command="cmd2")

    context = MCPContext(config1, config2)

    # Mock first connection succeeds, second fails
    mock_client1 = Mock()
    mock_client1.get_tools.return_value = []

    with patch("monkeybox.core.mcp_client._MCPClient") as mock_client_class:
        instances = []

        def create_client(*args):
            client = Mock()
            instances.append(client)
            if len(instances) == 1:
                # First client succeeds
                client.connect = AsyncMock()
                client.get_tools.return_value = []
            else:
                # Second client fails
                client.connect = AsyncMock(side_effect=Exception("Connection failed"))
            return client

        mock_client_class.side_effect = create_client

        with pytest.raises(MCPConnectionError) as exc_info:
            async with context:
                pass

        # The error message should mention connection failure
        assert "Failed to connect to MCP server" in str(
            exc_info.value
        ) or "Connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_tools_with_invalid_server_names():
    """Test get_tools with invalid server names logs warning."""

    config = MCPServerConfig(name="server1", transport="stdio", command="cmd")
    context = MCPContext(config)

    # Manually set up the context as if it were entered
    context.tools = {"server1": [lambda: "tool1"]}

    with patch("monkeybox.core.mcp_client.MonkeyboxLogger") as mock_logger_class:
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        # Request tools from non-existent server
        tools = context.get_tools("server1", "invalid_server")

        # Should return tools from valid server only
        assert len(tools) == 1

        # Should log warning about invalid server
        mock_logger.log_mcp_warning.assert_called_once()
        call_args = mock_logger.log_mcp_warning.call_args[0]
        assert "MCPContext" in call_args[0]
        assert "invalid_server" in call_args[1]
