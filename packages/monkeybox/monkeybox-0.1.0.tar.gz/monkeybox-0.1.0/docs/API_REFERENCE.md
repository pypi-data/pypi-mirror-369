# API Reference

This document provides comprehensive API documentation for the Monkeybox framework.

## Core Classes

### Agent

The main orchestrator class for AI agents.

```python
from monkeybox import Agent, OpenAIModel

model = OpenAIModel("gpt-4o-mini")
agent = Agent(model, "You are a helpful assistant", tools=[...])
```

**Constructor Parameters**:
- `model`: LLM provider instance (OpenAIModel or AnthropicModel)
- `system_prompt`: System instructions for the agent
- `tools`: Optional list of callable tools (functions, agents, or MCP tools)
- `max_steps`: Maximum iteration limit (default: 15)
- `name`: Optional name for the agent (used in multi-agent scenarios)

**Methods**:
- `async run(user_input: str) -> str`: Execute conversation with tool calling
- `reset()`: Clear conversation history
- `@property as_tool`: Returns agent wrapped as a callable tool

### Model Classes

#### OpenAIModel

```python
from monkeybox import OpenAIModel

model = OpenAIModel(
    "gpt-4o",
    api_key="...",  # Optional, uses env var by default
    reasoning=True,  # Enable reasoning mode for O1 models
    base_url="..."   # Optional custom base URL
)

# Optional: specify reasoning_effort when calling chat (for O1 models)
result = await model.chat(messages, reasoning_effort="high")  # low, medium, high
```

#### AnthropicModel

```python
from monkeybox import AnthropicModel

model = AnthropicModel(
    "claude-3-5-sonnet-20241022",
    api_key="...",  # Optional, uses env var by default
    reasoning=True   # Enables thinking mode with automatic token budgeting
)

# The thinking budget is automatically set to 85% of max_tokens
# You can override this with budget_tokens in chat kwargs
result = await model.chat(messages, budget_tokens=10000)
```

### Provider Feature Comparison: Reasoning vs Thinking

**OpenAI Reasoning Mode** (O1 models):
- Enabled with `reasoning=True` in the constructor
- Controls advanced reasoning capabilities for O1 series models
- Can be fine-tuned per request with `reasoning_effort` parameter
- Three levels: "low", "medium" (default), "high"
- Higher effort = more compute time but potentially better results

**Anthropic Thinking Mode**:
- Enabled with `reasoning=True` in the constructor (auto-converts internally)
- Provides Claude's internal thought process before responses
- Automatically allocates thinking tokens (85% of max_tokens by default)
- Can be overridden with `budget_tokens` in chat kwargs
- Thinking content is logged separately for debugging

**Key Differences**:
- OpenAI: Reasoning happens internally, you control effort level
- Anthropic: Thinking is visible in logs, you control token budget
- Both improve quality for complex tasks but work differently

## Tool System

### Creating Tools

#### Python Function Tools

```python
def my_tool(param: str, count: int = 10) -> str:
    """Tool description for the LLM.

    Args:
        param: Description of the parameter
        count: Number of items to process
    """
    return f"Result for {param} with count {count}"

# Async functions also supported
async def async_tool(query: str) -> List[str]:
    """Search for items."""
    # ... async implementation
    return results

agent = Agent(model, "System prompt", tools=[my_tool, async_tool])
```

#### MCP Tools

```python
from monkeybox.core.mcp_client import MCPServerConfig, MCPContext

# Configure MCP servers
filesystem_config = MCPServerConfig(
    name="filesystem",
    transport="stdio",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    env={"VAR": "value"},  # Optional environment
    connection_timeout=30.0,  # Connection timeout in seconds
    tool_timeout=60.0  # Tool execution timeout in seconds
)

# HTTP transport
http_config = MCPServerConfig(
    name="api_server",
    transport="http",
    url="https://api.example.com/mcp",
    headers={"Authorization": "Bearer token"},
    connection_timeout=30.0,
    tool_timeout=60.0
)

# Use in context manager
async with MCPContext(filesystem_config, http_config) as mcp:
    mcp_tools = mcp.get_tools()
    agent = Agent(model, prompt, tools=[*mcp_tools])
```

#### Agent as Tool

```python
# Create specialized agents
calculator = Agent(OpenAIModel("gpt-4o-mini"), "Math specialist", [add])
formatter = Agent(AnthropicModel("claude-3-5-sonnet"), "Text specialist", [format_text])

# Use as tools in main agent
main_agent = Agent(
    model,
    "Coordinator",
    tools=[calculator, formatter]  # Agents become ask_Calculator, ask_Formatter
)
```

## Exception Handling

### Exception Hierarchy

```python
MonkeyboxError (base exception for all Monkeybox errors)
├── MaxStepsReachedException      # Agent iteration limit reached
├── ToolError (base for tool-related errors)
│   ├── ToolNotFoundError         # Unknown tool requested
│   ├── ToolExecutionError        # Tool execution failed
│   ├── ToolValidationError       # Invalid tool configuration
│   └── ToolResultSerializationError  # Result not JSON-serializable
├── ModelError (base for model-related errors)
│   ├── ModelCommunicationError   # API call failed
│   └── ModelResponseError        # Invalid response format
├── SchemaGenerationError         # Tool schema generation failed
└── MCPError (base for MCP-related errors)
    ├── MCPConnectionError        # Connection failed
    ├── MCPConnectionTimeoutError # Connection timed out
    ├── MCPInitializationError    # Session init failed
    ├── MCPProtocolError          # Protocol violation
    ├── MCPToolDiscoveryError     # Tool discovery failed
    ├── MCPToolExecutionError     # Tool execution failed
    └── MCPToolTimeoutError       # Tool call timed out
```

### Import All Exceptions

```python
from monkeybox import (
    # Base exceptions
    MonkeyboxError,
    MaxStepsReachedException,

    # Tool exceptions
    ToolError,
    ToolNotFoundError,
    ToolExecutionError,
    ToolValidationError,
    ToolResultSerializationError,

    # Model exceptions
    ModelError,
    ModelCommunicationError,
    ModelResponseError,

    # Schema exceptions
    SchemaGenerationError,

    # MCP exceptions
    MCPError,
    MCPConnectionError,
    MCPConnectionTimeoutError,
    MCPInitializationError,
    MCPProtocolError,
    MCPToolDiscoveryError,
    MCPToolExecutionError,
    MCPToolTimeoutError
)
```

### Exception Handling Examples

#### Max Steps Handling

```python
from monkeybox import MaxStepsReachedException

agent = Agent(model, prompt, tools=tools, max_steps=5)

try:
    result = await agent.run("Complex multi-step task")
except MaxStepsReachedException as e:
    print(f"Reached limit of {e.max_steps} steps")
    print(f"Original input: {e.current_input}")
```

#### Tool Validation

```python
# Invalid tool types are caught at initialization
try:
    agent = Agent(model, tools=["not_callable"])  # String is not callable
except ToolValidationError as e:
    print(f"Invalid tool: {e}")
```

#### Model Communication Errors

```python
try:
    result = await agent.run("Query")
except ModelCommunicationError as e:
    print(f"API error for {e.model_name}: {e.error}")
```

#### MCP Error Handling

```python
# Connection errors
try:
    async with MCPContext(config) as mcp:
        tools = mcp.get_tools()
except MCPConnectionTimeoutError as e:
    print(f"Server {e.server_name} timed out after {e.timeout}s")
except MCPConnectionError as e:
    print(f"Failed to connect to {e.server_name}: {e.error}")

# Tool execution errors
try:
    result = await mcp_tool(query="test")
except MCPToolTimeoutError as e:
    print(f"Tool {e.tool_name} on {e.server_name} timed out")
except MCPToolExecutionError as e:
    print(f"Tool {e.tool_name} on {e.server_name} failed: {e.error}")
```

## Common Patterns

### Multi-Tool Agent

```python
agent = Agent(
    model,
    "Multi-capable assistant",
    tools=[
        get_time,           # Python function
        calculator_agent,   # Subagent
        *mcp_tools         # MCP tools
    ]
)
```

### Specialized Agent Chain

```python
# Chain: User → Coordinator → Specialist Agents → Tools
coordinator = Agent(model, "Coordinates tasks", tools=[
    Agent(model, "Math specialist", [add, multiply]),
    Agent(model, "Text specialist", [format_text])
])
```

### MCP Tool Integration

```python
async with MCPContext(*configs) as mcp:
    all_tools = [*python_tools, *mcp.get_tools(), *agents]
    agent = Agent(model, prompt, tools=all_tools)
```

## Advanced Features

### Step Control & Loop Prevention

```python
agent = Agent(model, prompt, tools=tools, max_steps=5)  # Limit iterations

try:
    result = await agent.run("Complex task")
except MaxStepsReachedException as e:
    # Handle the case where agent couldn't complete task within limit
    print(f"Agent reached limit: {e}")
```

### Async Context Management

```python
async with agent:  # Automatic cleanup
    result = await agent.run("Task")
```

### History Management

```python
agent.reset()  # Clear conversation history
agent.history  # Access message history
```

### Provider-Specific Features

```python
# OpenAI reasoning mode (O1 models)
openai_model = OpenAIModel("gpt-4o", reasoning=True)
# Optional: control reasoning effort in chat call
result = await agent.run("task", reasoning_effort="high")

# Anthropic thinking mode
anthropic_model = AnthropicModel("claude-3-5-sonnet-20241022", reasoning=True)
# Automatically converts to thinking dict with smart token budgeting
```

## Troubleshooting

### Common Issues

**1. API Keys Missing**
- Set `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` environment variables
- Check `.env` file in project root

**2. Model Names**
- Use exact model names: `"gpt-4o-mini"`, `"claude-3-5-sonnet-20241022"`
- Check provider documentation for available models

**3. Tool Schema Errors**
- Ensure functions have proper type hints
- Add docstrings for tool descriptions
- Check MCP server schemas

**4. Max Steps Reached**
- `MaxStepsReachedException` is raised when agent cannot complete task within the limit
- Increase `max_steps` parameter if the task legitimately requires more steps
- Review tool outputs for infinite loops
- Simplify system prompts
- Handle the exception gracefully in your application

**5. MCP Connection Issues**
- Verify MCP server commands and paths
- Check network connectivity for HTTP servers
- Review MCP server logs

### Debugging Tips
- Rich logging is enabled by default for observability
- Check conversation history: `agent.history`
- Review tool call arguments and results
- Use `agent.reset()` to clear state
