"""Monkeybox Showcase - All Features in One Example

This example demonstrates:
1. Python functions as tools
2. MCP servers (stdio and http)
3. Subagents working together
4. OpenAI and Anthropic models
5. New httpx-style context manager pattern for MCP
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import asyncio
import sys
from datetime import datetime

from monkeybox import Agent, MCPServerConfig, OpenAIModel


# Python function tools
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def get_time() -> str:
    """Get current time."""
    return datetime.now().strftime("%H:%M:%S")


def format_text(text: str, style: str = "upper") -> str:
    """Format text (upper, lower, title, reverse)."""
    if style == "upper":
        return text.upper()
    elif style == "lower":
        return text.lower()
    elif style == "title":
        return text.title()
    elif style == "reverse":
        return text[::-1]
    return text


async def main():
    """One comprehensive example showcasing all features."""
    print("🐒 Monkeybox Feature Showcase\n")

    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        sys.exit(1)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Please set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    # 1. Create subagents with different models
    calculator = Agent(
        OpenAIModel("gpt-4o-mini"),
        "You are a calculator specialist.",
        tools=[add],
        name="Calculator",
    )

    formatter = Agent(
        OpenAIModel("gpt-4o-mini"),
        "You are a text formatting specialist.",
        tools=[format_text],
        name="Formatter",
    )

    # 2. Set up MCP servers
    filesystem_config = MCPServerConfig(
        name="filesystem",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    )

    # HTTP MCP server - Context7 for web search and research
    http_config = MCPServerConfig(
        name="context7",
        transport="http",
        url="https://mcp.context7.com/mcp",
    )

    # 3. Create main agent with MCP configs (httpx-style pattern)
    # MCP tools will be automatically loaded when using the agent
    main_agent = Agent(
        OpenAIModel("gpt-4o-mini"),
        """You coordinate multiple capabilities:
        - Python tools for time and basic operations
        - MCP tools for file operations (stdio) and web search (http)
        - Subagents: Calculator for math, Formatter for text
        Keep responses brief and clear.""",
        tools=[
            # Python function tools
            get_time,
            # Subagents (different models)
            calculator,
            formatter,
        ],
        mcp_configs=[filesystem_config, http_config],
        name="MainAgent",
    )

    # Use the agent as a context manager (recommended pattern)
    async with main_agent:
        # 4. Run one comprehensive task that uses all tool types
        comprehensive_task = """
        I need you to complete a comprehensive task that showcases all your capabilities:

        1. First, get the current time
        2. Then calculate 25 + 17 using the calculator
        3. Search for information about 'the httpx python library'
        4. Format the text 'httpx showcase' in title case using the formatter
        5. Create a file /tmp/showcase_report.txt that contains:
            - Current time
            - The calculation result
            - A brief summary from the search
            - The formatted text
        6. Finally, read back the contents of the file to confirm it was created

        Complete all these steps in sequence and provide a summary of what was accomplished.
        """

        print("🎯 Comprehensive Task:")
        print("Creating a showcase report using all tool types...")
        print("=" * 50)

        result = await main_agent.run(comprehensive_task)
        print(f"\n✅ Final Result:\n{result}")

    # Alternative pattern: manual cleanup
    print("\n" + "=" * 50)
    print("\n🔄 Alternative Usage Pattern (manual cleanup):\n")

    # Create agent without context manager
    manual_agent = Agent(
        OpenAIModel("gpt-4o-mini"),
        "You are a simple assistant with MCP tools.",
        mcp_configs=[filesystem_config],
        name="ManualAgent",
    )

    # Use the agent (MCP will be initialized on first run)
    simple_result = await manual_agent.run("List the contents of /tmp directory")
    print(f"Manual agent result: {simple_result[:100]}...")

    # Must manually close when done
    await manual_agent.aclose()
    print("\n✅ Manual agent properly closed")


if __name__ == "__main__":
    asyncio.run(main())
