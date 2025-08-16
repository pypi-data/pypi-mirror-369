"""Integration tests for component interactions in Monkeybox.

These tests verify that different components work together correctly
without excessive mocking. They test real interactions between agents,
models, and tools.
"""

import ast

import pytest

from monkeybox.core.agent import Agent
from tests.conftest import MockModel


@pytest.mark.asyncio
async def test_agent_with_multiple_tool_types():
    """Test agent using both sync and async tools together."""

    def sync_multiply(x: int, y: int) -> int:
        """Multiply two numbers synchronously."""
        return x * y

    async def async_divide(a: float, b: float) -> float:
        """Divide two numbers asynchronously."""
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

    # Create agent with mixed tool types
    model = MockModel()
    agent = Agent(model, "Math assistant", tools=[sync_multiply, async_divide])

    # Test sync tool execution
    sync_result = await agent._execute_tool("sync_multiply", {"x": 5, "y": 3})
    assert sync_result == "15"

    # Test async tool execution
    async_result = await agent._execute_tool("async_divide", {"a": 10.0, "b": 2.0})
    assert async_result == "5.0"

    # Test error handling in async tool
    from monkeybox.core.exceptions import ToolExecutionError

    with pytest.raises(ToolExecutionError) as exc_info:
        await agent._execute_tool("async_divide", {"a": 10.0, "b": 0.0})
    assert exc_info.value.tool_name == "async_divide"
    assert isinstance(exc_info.value.error, ValueError)
    assert str(exc_info.value.error) == "Division by zero"


@pytest.mark.asyncio
async def test_nested_agent_integration():
    """Test real interaction between main and nested agents."""

    def format_result(text: str, uppercase: bool = False) -> str:
        """Format text with optional uppercase."""
        return text.upper() if uppercase else text

    # Create specialized agent
    formatter_model = MockModel()
    formatter_model.response_text = "FORMATTED TEXT"
    formatter_agent = Agent(
        formatter_model, "I format text", tools=[format_result], name="formatter"
    )

    # Create main agent using formatter as tool
    main_model = MockModel()
    main_agent = Agent(
        main_model, "I coordinate tasks", tools=[formatter_agent], name="coordinator"
    )

    # Test nested agent execution
    result = await main_agent._execute_tool("ask_formatter", {"question": "Format this"})
    assert result == "FORMATTED TEXT"

    # Verify formatter agent was properly isolated (fresh instance used)
    expected_formatter_history = [{"role": "system", "content": "I format text"}]
    assert formatter_agent.history == expected_formatter_history


@pytest.mark.asyncio
async def test_agent_tool_chain_execution():
    """Test a chain of tool executions with state management."""

    state = {"counter": 0}

    def increment() -> int:
        """Increment the counter."""
        state["counter"] += 1
        return state["counter"]

    def get_count() -> int:
        """Get current counter value."""
        return state["counter"]

    def reset_count() -> str:
        """Reset the counter."""
        state["counter"] = 0
        return "Counter reset"

    agent = Agent(MockModel(), tools=[increment, get_count, reset_count])

    # Test individual tool executions to verify state management
    result1 = await agent._execute_tool("increment", {})
    assert result1 == "1"
    assert state["counter"] == 1

    result2 = await agent._execute_tool("increment", {})
    assert result2 == "2"
    assert state["counter"] == 2

    count_result = await agent._execute_tool("get_count", {})
    assert count_result == "2"
    assert state["counter"] == 2

    # Reset and verify
    reset_result = await agent._execute_tool("reset_count", {})
    assert reset_result == "Counter reset"
    assert state["counter"] == 0


@pytest.mark.asyncio
async def test_agent_error_recovery_flow():
    """Test how agents handle and recover from errors in tool execution."""

    call_log = []

    def unreliable_tool(fail: bool = False) -> str:
        """Tool that can be configured to fail."""
        call_log.append(fail)
        if fail:
            raise RuntimeError("Tool failed as requested")
        return "Success"

    model = MockModel()
    agent = Agent(model, tools=[unreliable_tool])

    # Test successful execution
    success_result = await agent._execute_tool("unreliable_tool", {"fail": False})
    assert success_result == "Success"
    assert call_log == [False]

    # Test failed execution with recovery
    call_log.clear()
    from monkeybox.core.exceptions import ToolExecutionError

    with pytest.raises(ToolExecutionError) as exc_info:
        await agent._execute_tool("unreliable_tool", {"fail": True})
    assert exc_info.value.tool_name == "unreliable_tool"
    assert isinstance(exc_info.value.error, RuntimeError)
    assert str(exc_info.value.error) == "Tool failed as requested"
    assert call_log == [True]

    # Verify agent can still execute after error
    call_log.clear()
    recovery_result = await agent._execute_tool("unreliable_tool", {"fail": False})
    assert recovery_result == "Success"
    assert call_log == [False]


@pytest.mark.asyncio
async def test_agent_with_mcp_style_tools():
    """Test agent handling tools with MCP-style _input_schema attribute."""

    def mcp_search(query: str, limit: int = 10) -> list:
        """Search with MCP-style schema."""
        return [f"Result {i} for '{query}'" for i in range(min(limit, 3))]

    # Add MCP-style schema
    mcp_search._input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Max results", "default": 10},
        },
        "required": ["query"],
    }

    model = MockModel()
    agent = Agent(model, tools=[mcp_search])

    # Test with required parameter
    result = await agent._execute_tool("mcp_search", {"query": "test"})
    assert "Result 0 for 'test'" in result
    assert "Result 1 for 'test'" in result

    # Test with optional parameter
    result_limited = await agent._execute_tool("mcp_search", {"query": "test", "limit": 1})
    parsed = ast.literal_eval(result_limited)
    assert len(parsed) == 1


@pytest.mark.asyncio
async def test_multi_agent_coordination():
    """Test complex multi-agent coordination scenario."""

    # Create a shared workspace
    workspace = {"tasks": [], "results": {}}

    def add_task(task: str) -> str:
        """Add a task to the workspace."""
        workspace["tasks"].append(task)
        return f"Added task: {task}"

    def complete_task(task: str, result: str) -> str:
        """Mark a task as complete with result."""
        if task in workspace["tasks"]:
            workspace["results"][task] = result
            return f"Completed: {task}"
        return f"Task not found: {task}"

    # Task manager agent
    task_model = MockModel()
    task_model.response_text = "Task added successfully"
    task_agent = Agent(task_model, "Task manager", tools=[add_task], name="tasker")

    # Worker agent
    worker_model = MockModel()
    worker_model.response_text = "Work completed"
    worker_agent = Agent(worker_model, "Worker", tools=[complete_task], name="worker")

    # Coordinator agent
    coord_model = MockModel()
    coordinator = Agent(
        coord_model, "Coordinator", tools=[task_agent, worker_agent], name="coordinator"
    )

    # Test coordinator using the other agents as tools
    task_result = await coordinator._execute_tool(
        "ask_tasker", {"question": "Add task: Process data"}
    )
    assert task_result == "Task added successfully"

    worker_result = await coordinator._execute_tool(
        "ask_worker", {"question": "Complete Process data task"}
    )
    assert worker_result == "Work completed"

    # Also test direct workspace operations to verify state management
    await task_agent._execute_tool("add_task", {"task": "Process data"})
    await worker_agent._execute_tool(
        "complete_task", {"task": "Process data", "result": "Processed"}
    )

    # Verify workspace state
    assert "Process data" in workspace["tasks"]
    assert workspace["results"]["Process data"] == "Processed"


@pytest.mark.asyncio
async def test_agent_history_isolation():
    """Test that agent history is properly isolated between instances."""

    model = MockModel()

    # Create first agent and add history
    agent1 = Agent(model, "Agent 1")
    await agent1.run("First message")
    expected_agent1_history = [
        {"role": "system", "content": "Agent 1"},
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "Mock response"},
    ]
    assert agent1.history == expected_agent1_history

    # Create second agent
    agent2 = Agent(model, "Agent 2")
    expected_agent2_initial = [{"role": "system", "content": "Agent 2"}]
    assert agent2.history == expected_agent2_initial

    # Verify histories are independent
    await agent2.run("Second message")
    # Agent1 history should be unchanged
    assert agent1.history == expected_agent1_history
    # Agent2 should have its own conversation
    expected_agent2_final = [
        {"role": "system", "content": "Agent 2"},
        {"role": "user", "content": "Second message"},
        {"role": "assistant", "content": "Mock response"},
    ]
    assert agent2.history == expected_agent2_final

    # Content verification is already covered by the comprehensive history comparisons above
