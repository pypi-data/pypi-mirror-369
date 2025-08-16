"""Tests for custom exceptions."""

from monkeybox.core.exceptions import (
    MaxStepsReachedException,
    MCPConnectionError,
    MCPConnectionTimeoutError,
    MCPInitializationError,
    MCPProtocolError,
    MCPToolCallError,
    MCPToolDiscoveryError,
    MCPToolExecutionError,
    MCPToolTimeoutError,
    ModelCommunicationError,
    ModelResponseError,
    MonkeyboxError,
    SchemaGenerationError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolResultSerializationError,
)


def test_base_exception():
    """Test MonkeyboxError is the base for all exceptions."""
    assert issubclass(MaxStepsReachedException, MonkeyboxError)
    assert issubclass(ToolNotFoundError, MonkeyboxError)
    assert issubclass(ModelCommunicationError, MonkeyboxError)
    assert issubclass(MCPConnectionError, MonkeyboxError)


def test_max_steps_exception():
    """Test MaxStepsReachedException attributes and message."""
    exc = MaxStepsReachedException(5, "Process data")
    assert exc.max_steps == 5
    assert exc.current_input == "Process data"
    assert "reached maximum steps (5)" in str(exc)
    assert "Process data" in str(exc)

    # Test long input truncation
    long_input = "x" * 200
    exc = MaxStepsReachedException(10, long_input)
    assert str(exc).endswith("...")
    assert len(str(exc)) < 200


def test_tool_not_found_error():
    """Test ToolNotFoundError attributes and message."""
    exc = ToolNotFoundError("missing_tool", ["tool1", "tool2"])
    assert exc.tool_name == "missing_tool"
    assert exc.available_tools == ["tool1", "tool2"]
    assert "Tool 'missing_tool' not found" in str(exc)
    assert "Available tools: tool1, tool2" in str(exc)

    # Test empty tools list
    exc = ToolNotFoundError("missing_tool", [])
    assert "Available tools: none" in str(exc)


def test_tool_execution_error():
    """Test ToolExecutionError attributes and message."""
    original_error = ValueError("Invalid input")
    exc = ToolExecutionError("my_tool", original_error)
    assert exc.tool_name == "my_tool"
    assert exc.error == original_error
    assert "Failed to execute tool 'my_tool'" in str(exc)
    assert "ValueError: Invalid input" in str(exc)


def test_tool_result_serialization_error():
    """Test ToolResultSerializationError attributes and message."""
    result_type = type(object())
    exc = ToolResultSerializationError("json_tool", result_type)
    assert exc.tool_name == "json_tool"
    assert exc.result_type is result_type  # Verify exact type match
    assert exc.result_type is type(object())  # Should be the object type
    assert "Tool 'json_tool' returned non-serializable result" in str(exc)
    assert "type object" in str(exc)


def test_schema_generation_error():
    """Test SchemaGenerationError attributes and message."""
    original_error = TypeError("Cannot generate schema")
    exc = SchemaGenerationError("complex_func", original_error)
    assert exc.func_name == "complex_func"
    assert exc.error == original_error
    assert "Failed to generate schema for function 'complex_func'" in str(exc)
    assert "TypeError: Cannot generate schema" in str(exc)


def test_model_communication_error():
    """Test ModelCommunicationError attributes and message."""
    original_error = ConnectionError("Network failure")
    exc = ModelCommunicationError("gpt-4", original_error)
    assert exc.model_name == "gpt-4"
    assert exc.error == original_error
    assert "Failed to communicate with model 'gpt-4'" in str(exc)
    assert "ConnectionError: Network failure" in str(exc)


def test_model_response_error():
    """Test ModelResponseError attributes and message."""
    exc = ModelResponseError("claude-3", "Empty response")
    assert exc.model_name == "claude-3"
    assert exc.reason == "Empty response"
    assert "Invalid response from model 'claude-3'" in str(exc)
    assert "Empty response" in str(exc)


def test_mcp_connection_error():
    """Test MCPConnectionError attributes and message."""
    original_error = OSError("Connection refused")
    exc = MCPConnectionError("filesystem", original_error)
    assert exc.server_name == "filesystem"
    assert exc.error == original_error
    assert "Failed to connect to MCP server 'filesystem'" in str(exc)
    assert "OSError: Connection refused" in str(exc)


def test_mcp_connection_timeout_error():
    """Test MCPConnectionTimeoutError attributes and message."""
    exc = MCPConnectionTimeoutError("remote_server", 30.0)
    assert exc.server_name == "remote_server"
    assert exc.timeout == 30.0
    assert "Connection to MCP server 'remote_server' timed out" in str(exc)
    assert "30.0 seconds" in str(exc)


def test_mcp_protocol_error():
    """Test MCPProtocolError attributes and message."""
    exc = MCPProtocolError("test_server", "Invalid response format")
    assert exc.server_name == "test_server"
    assert exc.reason == "Invalid response format"
    assert "MCP protocol error with server 'test_server'" in str(exc)
    assert "Invalid response format" in str(exc)


def test_mcp_tool_discovery_error():
    """Test MCPToolDiscoveryError attributes and message."""
    original_error = RuntimeError("Discovery failed")
    exc = MCPToolDiscoveryError("tool_server", original_error)
    assert exc.server_name == "tool_server"
    assert exc.error == original_error
    assert "Failed to discover tools from MCP server 'tool_server'" in str(exc)
    assert "RuntimeError: Discovery failed" in str(exc)


def test_mcp_initialization_error():
    """Test MCPInitializationError attributes and message."""
    original_error = Exception("Init failed")
    exc = MCPInitializationError("server", original_error)
    assert exc.server_name == "server"
    assert exc.error == original_error
    assert "Failed to initialize MCP server 'server'" in str(exc)
    assert "Exception: Init failed" in str(exc)


def test_mcp_tool_call_error():
    """Test MCPToolCallError attributes and message."""
    original_error = ValueError("Bad arguments")
    exc = MCPToolCallError("server", "tool", original_error)
    assert exc.server_name == "server"
    assert exc.tool_name == "tool"
    assert exc.error == original_error
    assert "Failed to call MCP tool 'tool' on server 'server'" in str(exc)
    assert "ValueError: Bad arguments" in str(exc)


def test_mcp_tool_execution_error():
    """Test MCPToolExecutionError attributes and message."""
    original_error = RuntimeError("Execution failed")
    exc = MCPToolExecutionError("exec_server", "exec_tool", original_error)
    assert exc.server_name == "exec_server"
    assert exc.tool_name == "exec_tool"
    assert exc.error == original_error
    assert "Failed to execute MCP tool 'exec_tool' on server 'exec_server'" in str(exc)
    assert "RuntimeError: Execution failed" in str(exc)


def test_mcp_tool_timeout_error():
    """Test MCPToolTimeoutError attributes and message."""
    exc = MCPToolTimeoutError("slow_server", "slow_tool", 60.0)
    assert exc.server_name == "slow_server"
    assert exc.tool_name == "slow_tool"
    assert exc.timeout == 60.0
    assert "MCP tool 'slow_tool' on server 'slow_server' timed out" in str(exc)
    assert "60.0 seconds" in str(exc)
