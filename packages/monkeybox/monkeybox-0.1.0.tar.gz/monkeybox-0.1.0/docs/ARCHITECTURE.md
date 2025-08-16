# Monkeybox Architecture

This document provides a detailed technical overview of the Monkeybox framework architecture.

## Core Components

### 1. Agent (`src/monkeybox/core/agent.py`)
The main agent class that maintains conversation history and handles tool integration.

**Key Properties**:
- `model`: LLM provider instance (OpenAI/Anthropic)
- `system_prompt`: System instructions
- `tools`: List of callable tools (functions, agents, MCP)
- `max_steps`: Iteration limit (default: 15)
- `history`: Message history management

**Key Features**:
- Supports both function tools and other agents as tools
- Async implementation for performance
- Handles native SDK responses from different providers
- Configurable `max_steps` instance variable to limit tool calling iterations (raises `MaxStepsReachedException` when exceeded)
- Provider-aware response handling (OpenAI vs Anthropic formats)

**Key Methods**:
- `run(user_input)`: Execute conversation with tool calling
- `reset()`: Clear conversation history
- `as_tool`: Property that wraps agent as callable tool

### 2. Model Classes (Provider-specific implementations)

**BaseModel** (`src/monkeybox/core/base_model.py`):
- Abstract base class defining the interface
- `ChatResponse` dataclass standardizes responses across providers
- Three abstract methods: `chat()`, `format_tools_for_api()`, `format_tool_results()`

**OpenAIModel** (`src/monkeybox/core/openai_model.py`):
- OpenAI SDK implementation with native tool format
- Each tool result becomes separate message

**AnthropicModel** (`src/monkeybox/core/anthropic_model.py`):
- Anthropic SDK implementation with proper message formatting
- All tool results combined into single message

Each model handles its own tool formatting via `format_tools_for_api()`. Direct SDK usage provides full control over provider features.

### 3. Tool System (`src/monkeybox/core/tools.py`)
- Automatic schema generation using Pydantic's TypeAdapter
- Provider-agnostic tool definitions converted to provider format by models
- `ToolCall` dataclass for standardized tool invocations
- Support for MCP tools via `_input_schema` attribute detection

## Key Design Patterns

**Minimal Abstraction**: The framework avoids over-engineering. If the LLM can handle something natively, the framework doesn't add complexity.

## Model Providers

### Provider Differences
- **Tool Results**: OpenAI uses separate messages, Anthropic combines into single message
- **System Messages**: Anthropic requires separate handling
- **Reasoning**: Both use `reasoning=True` parameter, but different internal implementations
- **Response Format**: Different internal structures, unified via ChatResponse

### OpenAI Model Capabilities
- Reasoning mode for supported models
- Native tool calling format
- Custom base URL support

### Anthropic Model Capabilities
- Thinking/reasoning mode with budget control
- Automatic system message handling
- Native content block processing

## Tool System Architecture

The framework supports three types of tools seamlessly:

### 1. Python Function Tools
**Features**:
- Automatic schema generation via Pydantic TypeAdapter
- Support for sync and async functions
- Type hints used for validation
- Docstrings become tool descriptions

### 2. MCP (Model Context Protocol) Tools
- **MCPContext**: Async context manager for multiple MCP server connections
- **MCPServerConfig**: Configuration for stdio/HTTP transports
- **Transport Types**: STDIO (local processes) and HTTP (remote servers)

### 3. Agent-as-Tool Pattern
When an agent is used as a tool:
1. Creates fresh instance to prevent history pollution
2. Sets `is_nested = True` to avoid duplicate logging
3. Automatically named `ask_{agent_name}`
4. Returns string result from agent execution

### Tool Schema Generation
- **Python Functions**: Pydantic TypeAdapter generates JSON schema from type hints
- **MCP Tools**: Use pre-existing `_input_schema` attribute
- **Provider Formatting**: Each model formats tools for its API (OpenAI vs Anthropic)

## MCP Integration

### Tool Discovery Process
1. Connect to MCP servers via transport with configurable timeouts
2. Call `session.list_tools()` to discover available tools
3. Validate tool list response for protocol compliance
4. Create callable wrapper functions with naming: `{server}_{tool}`
5. Handle complex result content (text, embedded resources, lists)
6. Robust error handling for connection and execution failures

### MCP Server Configuration
- STDIO transport for local processes
- HTTP transport for remote servers
- Configurable connection and tool execution timeouts
- Support for environment variables and headers

## Multi-Agent Architecture

### Hierarchical Agent Architecture
```python
# Specialized agents
researcher = Agent(model, "Research specialist", tools=[web_search])
writer = Agent(model, "Writing specialist", tools=[format_text])
analyzer = Agent(model, "Analysis specialist", tools=[calculate])

# Coordinator agent
coordinator = Agent(
    model,
    "Coordinate multiple specialists",
    tools=[researcher, writer, analyzer],
    name="Coordinator"
)
```

### Best Practices
- **Specialization**: Give each agent focused responsibilities
- **Model Selection**: Different models for different capabilities
- **Clear Naming**: Descriptive agent names for tool generation
- **History Isolation**: Each agent-tool call gets fresh instance

## Logging & Observability

### MonkeyboxLogger (`src/monkeybox/core/logger.py`)
Built on Python's logging module with Rich terminal styling.

### Event Types & Styling
- **User Input**: `[bold blue]User:[/bold blue]`
- **Agent Steps**: `[bold white on blue] Step X/Y [/bold white on blue]`
- **Thinking**: `[bold yellow]Thinking [agent | model]:[/bold yellow]`
- **Tool Calls**: `[bold magenta]Tool:[/bold magenta]`
- **Tool Results**: `[bold green]Result:[/bold green]`
- **Agent Calls**: `[bold yellow]Calling [agent | model]:[/bold yellow]`
- **Errors**: `[bold red]Error:[/bold red]`

### Smart Logging Features
- **Content Truncation**: Prevents console flooding
- **Nested Agent Awareness**: Avoids duplicate logging
- **Context Information**: Agent/model names in all logs
- **MCP Integration**: Full MCP lifecycle logging

## File Locations Reference

**Core Components**:
- Agent logic: `src/monkeybox/core/agent.py` (144 statements, 97% coverage)
- Model interfaces: `src/monkeybox/core/base_model.py` (13 statements, 100% coverage)
- OpenAI implementation: `src/monkeybox/core/openai_model.py` (36 statements, 96% coverage)
- Anthropic implementation: `src/monkeybox/core/anthropic_model.py` (48 statements, 93% coverage)
- Tool system: `src/monkeybox/core/tools.py` (18 statements, 100% coverage)
- Logging: `src/monkeybox/core/logger.py` (61 statements, 96% coverage)
- MCP integration: `src/monkeybox/core/mcp_client.py` (212 statements, 91% coverage)
- Custom exceptions: `src/monkeybox/core/exceptions.py` (29 statements, 100% coverage)
