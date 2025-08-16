"""Custom exceptions for the Monkeybox framework."""


class MonkeyboxError(Exception):
    """Base exception for all Monkeybox errors.

    This is the root exception class for the Monkeybox framework. All custom
    exceptions inherit from this class, allowing applications to catch all
    Monkeybox-specific errors with a single except block.

    Example:
        try:
            result = await agent.run("Complex task")
        except MonkeyboxError as e:
            # Handle any Monkeybox-specific error
            logger.error(f"Monkeybox error: {e}")

    """


# Agent-related exceptions
class MaxStepsReachedException(MonkeyboxError):
    """Raised when agent reaches maximum steps without completion.

    This exception indicates that the agent could not complete the requested
    task within the configured iteration limit. This often happens when:
    - The task is too complex for the current max_steps setting
    - The agent is stuck in a loop
    - Tool outputs aren't providing the expected results

    Attributes:
        max_steps: The maximum number of steps that was configured
        current_input: The original user input that triggered the task

    Example:
        try:
            result = await agent.run("Complex multi-step task")
        except MaxStepsReachedException as e:
            print(f"Task too complex, reached {e.max_steps} steps")
            # Consider increasing max_steps or simplifying the task

    """

    def __init__(self, max_steps: int, current_input: str):
        self.max_steps = max_steps
        self.current_input = current_input
        super().__init__(
            f"Agent reached maximum steps ({max_steps}) without completing task. Current input: {current_input[:100]}...",
        )


# Tool-related exceptions
class ToolError(MonkeyboxError):
    """Base exception for tool-related errors.

    Parent class for all tool-related exceptions. Use this to catch any
    error related to tool discovery, validation, execution, or serialization.

    Example:
        try:
            result = await agent._execute_tool("my_tool", {"arg": "value"})
        except ToolError as e:
            # Handle any tool-related error
            logger.error(f"Tool error: {e}")

    """


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not found.

    This exception occurs when the LLM requests a tool that doesn't exist
    in the agent's tool registry. This might happen due to:
    - Hallucination by the model
    - Mismatch between tool names and model expectations
    - Tools not properly registered with the agent

    Attributes:
        tool_name: The name of the tool that was requested
        available_tools: List of tools that are actually available

    Example:
        try:
            result = await agent._execute_tool("unknown_tool", {})
        except ToolNotFoundError as e:
            print(f"Tool '{e.tool_name}' not found. Available: {e.available_tools}")

    """

    def __init__(self, tool_name: str, available_tools: list[str]):
        self.tool_name = tool_name
        self.available_tools = available_tools
        super().__init__(
            f"Tool '{tool_name}' not found. Available tools: {', '.join(available_tools) if available_tools else 'none'}",
        )


class ToolExecutionError(ToolError):
    """Raised when tool execution fails.

    This exception wraps any error that occurs during tool execution,
    providing context about which tool failed and why. Common causes:
    - Invalid arguments passed to the tool
    - Tool internal logic errors
    - External dependencies (API calls, file I/O) failing

    Attributes:
        tool_name: The name of the tool that failed
        error: The original exception that was raised

    Example:
        try:
            result = await agent._execute_tool("calculator", {"invalid": "args"})
        except ToolExecutionError as e:
            print(f"Tool '{e.tool_name}' failed: {e.error}")

    """

    def __init__(self, tool_name: str, error: Exception):
        self.tool_name = tool_name
        self.error = error
        super().__init__(
            f"Failed to execute tool '{tool_name}': {type(error).__name__}: {error!s}",
        )


class ToolValidationError(ToolError):
    """Raised when tool validation fails.

    This exception occurs during agent initialization when a tool doesn't
    meet the framework's requirements. Common validation failures:
    - Tool is not callable
    - Tool lacks a proper __name__ attribute
    - Tool schema cannot be generated

    Example:
        try:
            agent = Agent(model, tools=["not_callable"])  # String isn't callable
        except ToolValidationError as e:
            print(f"Invalid tool: {e}")

    """


class ToolResultSerializationError(ToolError):
    """Raised when tool result cannot be serialized.

    Tools must return JSON-serializable values to be included in the
    conversation history. This exception occurs when a tool returns:
    - Custom objects without JSON representation
    - Circular references
    - Non-serializable types (e.g., file handles, lambdas)

    Attributes:
        tool_name: The name of the tool that returned non-serializable data
        result_type: The type of the problematic result

    Example:
        def bad_tool():
            return lambda x: x  # Lambdas aren't JSON-serializable

        # This will raise ToolResultSerializationError when executed

    """

    def __init__(self, tool_name: str, result_type: type):
        self.tool_name = tool_name
        self.result_type = result_type
        super().__init__(
            f"Tool '{tool_name}' returned non-serializable result of type {result_type.__name__}. "
            "Tools must return JSON-serializable values.",
        )


# Schema-related exceptions
class SchemaGenerationError(MonkeyboxError):
    """Raised when schema generation fails.

    The framework automatically generates JSON schemas from Python function
    signatures. This exception occurs when schema generation fails due to:
    - Unsupported type annotations
    - Complex generic types that can't be represented in JSON Schema
    - Missing or invalid function metadata

    Attributes:
        func_name: The name of the function that failed schema generation
        error: The original exception from the schema generator

    Example:
        def complex_tool(data: ComplexCustomType) -> Result:
            # If ComplexCustomType can't be converted to JSON Schema
            # SchemaGenerationError will be raised during agent init
            pass

    """

    def __init__(self, func_name: str, error: Exception):
        self.func_name = func_name
        self.error = error
        super().__init__(
            f"Failed to generate schema for function '{func_name}': {type(error).__name__}: {error!s}",
        )


# Model-related exceptions
class ModelError(MonkeyboxError):
    """Base exception for model-related errors.

    Parent class for all model/LLM-related exceptions. Use this to catch
    any error related to model communication or response processing.

    Example:
        try:
            response = await model.chat(messages)
        except ModelError as e:
            # Handle any model-related error
            logger.error(f"Model error: {e}")

    """


class ModelCommunicationError(ModelError):
    """Raised when communication with the model fails.

    This exception wraps API errors from OpenAI or Anthropic services.
    Common causes include:
    - Network connectivity issues
    - Invalid API keys
    - Rate limiting (though these are retried automatically)
    - Service outages

    Attributes:
        model_name: The name of the model that failed
        error: The original API error

    Example:
        try:
            response = await agent.run("Query")
        except ModelCommunicationError as e:
            if "authentication" in str(e.error).lower():
                print("Check your API key")

    """

    def __init__(self, model_name: str, error: Exception):
        self.model_name = model_name
        self.error = error
        super().__init__(
            f"Failed to communicate with model '{model_name}': {type(error).__name__}: {error!s}",
        )


class ModelResponseError(ModelError):
    """Raised when model response is invalid or unexpected.

    This exception occurs when the model returns a response that doesn't
    match the expected format or contains invalid data. This might indicate:
    - API changes in the provider
    - Corrupted response data
    - Incompatible model versions

    Attributes:
        model_name: The name of the model that returned invalid response
        reason: Description of what was invalid about the response

    Example:
        # Might occur if API response format changes
        try:
            response = await model.chat(messages)
        except ModelResponseError as e:
            print(f"Invalid response from {e.model_name}: {e.reason}")

    """

    def __init__(self, model_name: str, reason: str):
        self.model_name = model_name
        self.reason = reason
        super().__init__(f"Invalid response from model '{model_name}': {reason}")


# MCP-related exceptions
class MCPError(MonkeyboxError):
    """Base exception for MCP-related errors.

    Parent class for all Model Context Protocol (MCP) related exceptions.
    MCP enables integration with external tool servers. Use this to catch
    any MCP-related error.

    Example:
        try:
            async with MCPContext(config) as mcp:
                tools = mcp.get_tools()
        except MCPError as e:
            # Handle any MCP-related error
            logger.error(f"MCP error: {e}")

    """


class MCPConnectionError(MCPError):
    """Raised when MCP connection fails.

    This exception occurs when the framework cannot establish a connection
    to an MCP server. Common causes:
    - Server not running or unreachable
    - Invalid server configuration (wrong command/URL)
    - Network issues for HTTP transport
    - Process spawn failures for stdio transport

    Attributes:
        server_name: The name of the MCP server
        error: The original connection error

    Example:
        try:
            async with MCPContext(config) as mcp:
                pass
        except MCPConnectionError as e:
            print(f"Failed to connect to {e.server_name}: {e.error}")

    """

    def __init__(self, server_name: str, error: Exception):
        self.server_name = server_name
        self.error = error
        super().__init__(
            f"Failed to connect to MCP server '{server_name}': {type(error).__name__}: {error!s}",
        )


class MCPConnectionTimeoutError(MCPError):
    """Raised when MCP connection times out.

    This exception occurs when connection to an MCP server takes longer
    than the configured timeout. This might indicate:
    - Server is slow to start
    - Network latency issues
    - Server is hanging during initialization

    Attributes:
        server_name: The name of the MCP server
        timeout: The timeout value in seconds

    Example:
        config = MCPServerConfig(
            name="slow_server",
            connection_timeout=5.0  # 5 second timeout
        )
        # Raises MCPConnectionTimeoutError if connection takes > 5 seconds

    """

    def __init__(self, server_name: str, timeout: float):
        self.server_name = server_name
        self.timeout = timeout
        super().__init__(
            f"Connection to MCP server '{server_name}' timed out after {timeout} seconds",
        )


class MCPProtocolError(MCPError):
    """Raised when MCP protocol violation occurs.

    This exception indicates that an MCP server is not following the
    Model Context Protocol specification. This might happen when:
    - Server returns malformed responses
    - Required protocol fields are missing
    - Server uses incompatible protocol version

    Attributes:
        server_name: The name of the MCP server
        reason: Description of the protocol violation

    Example:
        # Might occur if server returns invalid tool list format
        try:
            tools = mcp.get_tools()
        except MCPProtocolError as e:
            print(f"Server {e.server_name} protocol error: {e.reason}")

    """

    def __init__(self, server_name: str, reason: str):
        self.server_name = server_name
        self.reason = reason
        super().__init__(f"MCP protocol error with server '{server_name}': {reason}")


class MCPToolDiscoveryError(MCPError):
    """Raised when MCP tool discovery fails.

    This exception occurs when the framework cannot retrieve the list of
    available tools from an MCP server. This might be due to:
    - Server not implementing the list_tools method
    - Server returning invalid tool definitions
    - Communication errors during discovery

    Attributes:
        server_name: The name of the MCP server
        error: The original error during discovery

    Example:
        try:
            tools = mcp.get_tools()
        except MCPToolDiscoveryError as e:
            print(f"Cannot discover tools from {e.server_name}: {e.error}")
            # Server may not have any tools or discovery failed

    """

    def __init__(self, server_name: str, error: Exception):
        self.server_name = server_name
        self.error = error
        super().__init__(
            f"Failed to discover tools from MCP server '{server_name}': {type(error).__name__}: {error!s}",
        )


class MCPInitializationError(MCPError):
    """Raised when MCP initialization fails.

    This exception occurs during the MCP session initialization phase,
    after connection but before the server is ready to use. Causes:
    - Server initialization logic failing
    - Required server resources unavailable
    - Protocol handshake failures

    Attributes:
        server_name: The name of the MCP server
        error: The original initialization error

    Example:
        # Server connects but fails during initialization
        try:
            async with MCPContext(config) as mcp:
                pass
        except MCPInitializationError as e:
            print(f"Server {e.server_name} failed to initialize: {e.error}")

    """

    def __init__(self, server_name: str, error: Exception):
        self.server_name = server_name
        self.error = error
        super().__init__(
            f"Failed to initialize MCP server '{server_name}': {type(error).__name__}: {error!s}",
        )


class MCPToolCallError(MCPError):
    """Raised when MCP tool call fails.

    This exception occurs when the framework cannot successfully call an
    MCP tool. This is typically due to communication issues rather than
    tool execution failures. Common causes:
    - Server connection lost during tool call
    - Malformed tool call request
    - Server doesn't recognize the tool

    Attributes:
        server_name: The name of the MCP server
        tool_name: The name of the tool being called
        error: The original error during the call

    Note: This is different from MCPToolExecutionError, which occurs when
    the tool executes but returns an error.

    """

    def __init__(self, server_name: str, tool_name: str, error: Exception):
        self.server_name = server_name
        self.tool_name = tool_name
        self.error = error
        super().__init__(
            f"Failed to call MCP tool '{tool_name}' on server '{server_name}': {type(error).__name__}: {error!s}",
        )


class MCPToolExecutionError(MCPError):
    """Raised when MCP tool execution fails.

    This exception occurs when an MCP tool executes but encounters an error
    during its operation. The tool was successfully called, but its internal
    logic failed. Common scenarios:
    - Tool arguments are invalid
    - Tool's external dependencies fail (API, database, etc.)
    - Tool encounters an internal error

    Attributes:
        server_name: The name of the MCP server
        tool_name: The name of the tool that failed
        error: The error returned by the tool

    Example:
        # Tool executes but fails internally
        try:
            result = await mcp_tool(invalid_args={"bad": "data"})
        except MCPToolExecutionError as e:
            print(f"Tool {e.tool_name} failed: {e.error}")

    """

    def __init__(self, server_name: str, tool_name: str, error: Exception):
        self.server_name = server_name
        self.tool_name = tool_name
        self.error = error
        super().__init__(
            f"Failed to execute MCP tool '{tool_name}' on server '{server_name}': {type(error).__name__}: {error!s}",
        )


class MCPToolTimeoutError(MCPError):
    """Raised when MCP tool call times out.

    This exception occurs when an MCP tool takes longer than the configured
    timeout to complete. This protects against:
    - Tools that hang indefinitely
    - Long-running operations without proper async handling
    - Network timeouts for tools making external calls

    Attributes:
        server_name: The name of the MCP server
        tool_name: The name of the tool that timed out
        timeout: The timeout value in seconds

    Example:
        config = MCPServerConfig(
            name="server",
            tool_timeout=30.0  # 30 second timeout per tool
        )
        # Tool calls that take > 30 seconds will raise this exception

    """

    def __init__(self, server_name: str, tool_name: str, timeout: float):
        self.server_name = server_name
        self.tool_name = tool_name
        self.timeout = timeout
        super().__init__(
            f"MCP tool '{tool_name}' on server '{server_name}' timed out after {timeout} seconds",
        )
