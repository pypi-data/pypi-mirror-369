"""Example demonstrating different MCP usage patterns with the new Agent API.

This example shows:
1. Context manager pattern (recommended)
2. Manual cleanup pattern
3. No MCP pattern (regular tools only)
"""

import asyncio
import os

from monkeybox import Agent, MCPServerConfig, OpenAIModel


def calculate(expression: str) -> float:
    """Calculate a mathematical expression using a safe parser."""
    import ast
    import operator

    # Define allowed operations
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def eval_expr(node):
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](eval_expr(node.operand))
        else:
            raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    try:
        tree = ast.parse(expression, mode="eval")
        return eval_expr(tree.body)
    except (SyntaxError, ValueError, KeyError) as e:
        raise ValueError(f"Invalid mathematical expression: {e}")


async def main():
    print("🐒 Monkeybox MCP Usage Patterns\n")

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        return

    # MCP server configuration
    filesystem_config = MCPServerConfig(
        name="filesystem",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    )

    print("1️⃣ Context Manager Pattern (Recommended)\n")
    print("This is the preferred way to use agents with MCP tools:")
    print("-" * 50)

    # Create agent with MCP configs
    agent1 = Agent(
        OpenAIModel("gpt-4o-mini"),
        "You are a helpful assistant with filesystem access.",
        tools=[calculate],  # Python tools
        mcp_configs=[filesystem_config],  # MCP configs
        name="ContextAgent",
    )

    # Use as context manager - MCP tools are automatically loaded and cleaned up
    async with agent1:
        result = await agent1.run(
            "Create a file /tmp/context_example.txt with the result of calculate('2**10')"
        )
        print(f"Result: {result}\n")

    print("\n2️⃣ Manual Cleanup Pattern\n")
    print("For cases where context manager isn't suitable:")
    print("-" * 50)

    # Create agent without context manager
    agent2 = Agent(
        OpenAIModel("gpt-4o-mini"),
        "You are a helpful assistant with filesystem access.",
        mcp_configs=[filesystem_config],
        name="ManualAgent",
    )

    # MCP tools are loaded on first run
    result = await agent2.run("List the contents of /tmp directory")
    print(f"Result: {result[:200]}...")

    # Multiple runs reuse the same MCP connection
    result2 = await agent2.run("How many files are in /tmp?")
    print(f"Second result: {result2}\n")

    # Must manually close when done
    await agent2.aclose()
    print("✅ Agent manually closed\n")

    print("\n3️⃣ No MCP Pattern (Regular Tools Only)\n")
    print("For agents that only use Python function tools:")
    print("-" * 50)

    # Agent with only Python tools - no MCP
    agent3 = Agent(
        OpenAIModel("gpt-4o-mini"),
        "You are a calculator assistant.",
        tools=[calculate],
        name="SimpleAgent",
    )

    # No context manager needed, no cleanup required
    result = await agent3.run("What is calculate('100 * 25 + 10')?")
    print(f"Result: {result}\n")

    print("\n📝 Summary:")
    print("- Use context manager (async with) for best resource management")
    print("- Manual cleanup with aclose() when context manager isn't feasible")
    print("- No special handling needed for agents without MCP configs")


if __name__ == "__main__":
    asyncio.run(main())
