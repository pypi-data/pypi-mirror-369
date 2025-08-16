# CLAUDE.md - Monkeybox AI Agent Guide

This file provides essential guidance for AI agents working with the Monkeybox codebase.

**Documentation Maintenance Responsibility**: When you add new features, modify existing functionality, or change the codebase architecture, you MUST update this CLAUDE.md file and relevant documentation accordingly. This ensures future AI agents have accurate, up-to-date information.

## Project Overview

**Monkeybox** is a minimal, observable agent framework for building AI agents with OpenAI and Anthropic compatible models. It prioritizes **simplicity and observability** while remaining highly capable.

### Key Features
- **Minimal Abstraction**: Direct SDK usage preserving full provider features
- **Async-First**: Built for performance with async/await throughout
- **Provider Agnostic**: Unified interface supporting both OpenAI and Anthropic
- **Tool Flexible**: Any Python function, MCP server, or agent can be a tool
- **Observable**: Rich logging with color-coded terminal output

## Quick Start

### Prerequisites
- Python 3.11+
- API keys for OpenAI and/or Anthropic

### Setup
```bash
# Clone and install
git clone <repository-url>
cd monkeybox
uv sync

# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Basic Example
```python
from monkeybox import Agent, OpenAIModel

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Create agent
model = OpenAIModel("gpt-4o-mini")
agent = Agent(model, "You are a helpful math assistant.", tools=[add_numbers])

# Run agent
result = await agent.run("What is 15 + 27?")
print(result)
```

## Project Structure

```
monkeybox/
├── src/monkeybox/
│   ├── __init__.py          # Main exports
│   ├── core/
│   │   ├── agent.py         # Main Agent orchestrator
│   │   ├── base_model.py    # Abstract model interface
│   │   ├── openai_model.py  # OpenAI implementation
│   │   ├── anthropic_model.py # Anthropic implementation
│   │   ├── tools.py         # Tool system & schema generation
│   │   ├── logger.py        # Rich logging system
│   │   ├── mcp_client.py    # MCP integration
│   │   └── exceptions.py    # Custom exceptions
├── tests/                   # Comprehensive test suite (90%+ coverage)
├── examples/
│   ├── showcase_example.py  # Comprehensive example
├── docs/                    # Detailed documentation
│   ├── ARCHITECTURE.md      # Technical architecture
│   ├── API_REFERENCE.md     # API documentation
│   ├── TESTING.md          # Testing guide
│   └── CONTRIBUTING.md     # Contribution guidelines
└── pyproject.toml          # uv configuration
```

## Development Commands

```bash
# Install dependencies
uv sync

# Run example
uv run python examples/showcase_example.py

# Code quality
uv run ruff check . --fix
uv run ruff format .

# Type checking
uv run ty check src/monkeybox

# Testing with coverage (90% required)
uv run pytest --cov=src/monkeybox --cov-fail-under=90

# Pre-commit hooks
uv run pre-commit
```

## Coding Style

- **Type Hints**: Always use type hints for function parameters and returns
- **Docstrings**: Use Google-style docstrings for all public functions
- **Async**: Prefer async/await for all I/O operations
- **Imports**: Use absolute imports from `monkeybox` package
- **Line Length**: 100 characters (enforced by ruff)
- **Testing**: Maintain 90%+ test coverage

### Example Function Style
```python
async def process_data(input_data: str, count: int = 10) -> List[str]:
    """Process input data and return results.

    Args:
        input_data: The data to process
        count: Number of items to return

    Returns:
        List of processed results
    """
    # Implementation
    return results
```

## AI Agent Development Guidelines

1. **Test-Driven Development**: Write tests first, then implement features
2. **Maintain Coverage**: Never drop below 90% test coverage
3. **Update Documentation**: Keep CLAUDE.md and docs/ files current
4. **Follow Patterns**: Study existing code before making changes
5. **Use Provided Tools**: Always run ruff, ty, and tests before committing

## Architecture Principles

See [Architecture Guide](docs/ARCHITECTURE.md) and [Contributing Guide](docs/CONTRIBUTING.md#architecture-principles) for the framework's design principles.

## Essential Concepts

### Tools
- **Python Functions**: Any function with type hints becomes a tool
- **MCP Servers**: External tools via Model Context Protocol
- **Agent as Tool**: Agents can use other agents as tools

### Providers
- **OpenAI**: Full support including reasoning mode
- **Anthropic**: Full support including thinking mode
- Both use native SDKs with minimal abstraction


### Error Handling
- Comprehensive exception hierarchy (see `exceptions.py`)
- All errors inherit from `MonkeyboxError`
- Rich error context with structured attributes

## Documentation

For detailed information, see:
- [Architecture Guide](docs/ARCHITECTURE.md) - Technical deep dive
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Testing Guide](docs/TESTING.md) - Testing approach and practices
- [Contributing Guide](docs/CONTRIBUTING.md) - Development workflow

## MCP Tool Integration

Agents support MCP (Model Context Protocol) servers for extending functionality with external tools.

### Usage Patterns

**Context Manager Pattern (Recommended)**
```python
from monkeybox import Agent, OpenAIModel, MCPServerConfig

# Configure MCP servers
filesystem_config = MCPServerConfig(
    name="filesystem",
    transport="stdio",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
)

# Create agent with MCP configs
agent = Agent(
    OpenAIModel("gpt-4o-mini"),
    "Your system prompt here",
    tools=[my_python_tool],  # Regular Python tools
    mcp_configs=[filesystem_config],  # MCP configs
)

# Use as context manager - MCP tools are automatically loaded and cleaned up
async with agent:
    result = await agent.run("Create a file in /tmp")
```

**Manual Cleanup Pattern**
```python
# Create agent without context manager
agent = Agent(
    OpenAIModel("gpt-4o-mini"),
    "Your system prompt here",
    mcp_configs=[filesystem_config],
)

# MCP tools are loaded on first run
result = await agent.run("List files in /tmp")  # MCP initialized here

# Must manually close when done
await agent.aclose()
```

### Key Features
- **Lazy initialization**: MCP connections created only when needed
- **Resource safety**: Context managers guarantee cleanup
- **Thread-safe**: State transitions protected by locks
- **Clear error messages**: Actionable guidance on failures

See examples in `examples/` directory for practical usage.

## 📝 Documentation Status
- **Test Coverage**: 90%+ (comprehensive test suite)
- **Documentation Status**: Comprehensive and current
- **Next Required Update**: When any code changes are made

**Remember**: Future AI agents MUST update this documentation when modifying the codebase!

## Agent Parameters

- `model` - The LLM model to use (OpenAIModel or AnthropicModel)
- `system_prompt` - Initial system instructions for the agent
- `tools` - List of Python functions or other agents as tools
- `mcp_configs` - List of MCPServerConfig instances for MCP tools
- `name` - Optional name for the agent (for logging)
- `max_steps` (default: 15) - Maximum tool call iterations
- `verbose` (default: True) - Controls logging output level

## MCP Troubleshooting

**MCP Server Won't Start:**
- Ensure MCP server is installed: `npm install -g @modelcontextprotocol/server-filesystem`
- Check command paths and permissions
- Verify stdio/http transport configuration

**Agent State Errors:**
- "Cannot use a closed Agent" → Create new instance or use context manager
- "Cannot open twice" → Agent already opened, use as-is
- "Cannot reopen" → Agents are single-use after closing

**Resource Cleanup:**
- Always use `async with agent:` or call `await agent.aclose()`
- Context manager pattern guarantees cleanup
- MCP processes cleaned up automatically

**Tools Not Found:**
- MCP tools load on first run or context manager entry
- Check `agent.tool_map` after initialization
- Verify MCP server is returning tools correctly
