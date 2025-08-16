# Monkeybox 🐵

A minimal, observable agent framework for building AI agents with OpenAI and Anthropic compatible models.

## Features

- **Minimal abstraction** - Direct SDK usage preserving full provider features
- **Multi-agent support** - Agents can use other agents as tools seamlessly
- **Rich observability** - Beautiful terminal logging with color-coded output
- **Async first** - Built for performance with async/await throughout
- **Provider agnostic** - Native support for OpenAI and Anthropic models
- **MCP integration** - Model Context Protocol support for external tools
- **Tool flexibility** - Any Python function, MCP server, or agent can be a tool
- **Type safe** - Full Pydantic integration for schema generation

## Installation

```bash
# Install with uv (recommended)
uv add monkeybox

# Or with pip
pip install monkeybox
```

## Quick Start

```python
import asyncio
from monkeybox import Agent, OpenAIModel

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

async def main():
    model = OpenAIModel("gpt-4o-mini")
    agent = Agent(model, "You are a helpful calculator", tools=[add])

    async with agent:
        response = await agent.run("What's 25 + 17?")
        print(response)

asyncio.run(main())
```

## Using Different Providers

```python
from monkeybox import Agent, OpenAIModel, AnthropicModel

# OpenAI with reasoning support
openai_model = OpenAIModel("gpt-4o", reasoning=True)
openai_agent = Agent(openai_model, "You are a helpful assistant")
# Optional: specify reasoning_effort when calling chat
# result = await openai_agent.run("complex task", reasoning_effort="high")

# Anthropic with thinking mode
anthropic_model = AnthropicModel("claude-3-5-sonnet-20241022", reasoning=True)
anthropic_agent = Agent(anthropic_model, "You are a helpful assistant")
# Note: reasoning=True automatically enables thinking mode with smart token budgeting
```

## Multi-Agent Systems

Agents can use other agents as tools, creating sophisticated hierarchical systems:

```python
# Create specialized agents
calculator = Agent(
    OpenAIModel("gpt-4o-mini"),
    "You are a calculator specialist",
    tools=[add],
    name="Calculator"
)

formatter = Agent(
    AnthropicModel("claude-3-5-sonnet-20241022"),
    "You are a text formatting specialist",
    tools=[format_text],
    name="Formatter"
)

# Main agent coordinates others
coordinator = Agent(
    AnthropicModel("claude-3-5-sonnet-20241022"),
    "You coordinate multiple capabilities",
    tools=[calculator, formatter],  # Agents become ask_Calculator, ask_Formatter
    name="Coordinator"
)
```

## MCP (Model Context Protocol) Integration

Connect to external tools via Model Context Protocol:

```python
from monkeybox.core.mcp_client import MCPServerConfig, MCPContext

# Configure MCP servers
filesystem_config = MCPServerConfig(
    name="filesystem",
    transport="stdio",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
)

http_config = MCPServerConfig(
    name="web_search",
    transport="http",
    url="https://api.example.com/mcp"
)

# Use in agent
async with MCPContext(filesystem_config, http_config) as mcp:
    mcp_tools = mcp.get_tools()

    agent = Agent(
        model,
        "Assistant with external tools",
        tools=[*python_functions, *mcp_tools]
    )

    async with agent:
        result = await agent.run("Create a file and search for information")
```

## Tool Types

Monkeybox supports three types of tools seamlessly:

### 1. Python Functions
```python
def get_current_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().isoformat()

async def web_search(query: str) -> str:
    """Search the web asynchronously."""
    # Implementation here
    return f"Results for {query}"
```

### 2. MCP Server Tools
External tools via Model Context Protocol (see example above)

### 3. Other Agents
```python
agent = Agent(model, "Main agent", tools=[other_agent])
# Creates tool named "ask_other_agent"
```

## Rich Observability

Monkeybox provides beautiful terminal output with detailed execution visibility:

- **Color-coded logs** for different event types
- **Step-by-step progress** tracking
- **Tool call visualization** with arguments and results
- **Multi-agent coordination** tracking
- **Provider-specific features** like thinking traces
- **Smart content truncation** to prevent log spam

## Environment Setup

Set your API keys:
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

Or use a `.env` file:
```
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## Development

This project uses `uv` for dependency management. See [Contributing Guide](docs/CONTRIBUTING.md) for detailed development workflow and commands.

```bash
# Quick start
uv sync  # Install dependencies
uv run python examples/showcase_example.py  # Run example
```

## Examples

See `examples/showcase_example.py` for a comprehensive demonstration featuring:
- Multiple model providers (OpenAI + Anthropic)
- Python function tools
- MCP server integration (filesystem + HTTP)
- Multi-agent coordination
- Complex task orchestration

## Documentation

### Where to Start
- **New Users**: Start with this README, then see the [API Reference](docs/API_REFERENCE.md)
- **Contributors**: Read [Contributing Guide](docs/CONTRIBUTING.md) first
- **AI Agents**: Start with [CLAUDE.md](CLAUDE.md) for essential context
- **Understanding the Code**: See [Architecture Guide](docs/ARCHITECTURE.md)

### Documentation Overview
- **[CLAUDE.md](CLAUDE.md)** - Essential guide for AI agents working on this codebase
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture, design patterns, and component details
- **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[docs/TESTING.md](docs/TESTING.md)** - Testing philosophy, coverage requirements, and best practices
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Development workflow, code standards, and PR guidelines

## Architecture

Monkeybox follows a **minimal abstraction** philosophy:
- Direct SDK usage for full provider control
- Unified interfaces without over-engineering
- Provider-specific features preserved
- Clean separation of concerns

Core components:
- **Agent**: Main orchestrator managing conversations and tools
- **Models**: Provider-specific implementations (OpenAI, Anthropic)
- **Tools**: Automatic schema generation and execution
- **MCP**: External tool integration via Model Context Protocol
- **Logger**: Rich terminal output with structured logging

## License

MIT
