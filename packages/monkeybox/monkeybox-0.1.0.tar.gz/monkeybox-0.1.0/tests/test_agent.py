"""Tests for the Agent class."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from monkeybox.core.agent import Agent, MaxStepsReachedException, ModelCommunicationError
from monkeybox.core.base_model import ChatResponse
from monkeybox.core.exceptions import (
    ToolExecutionError,
    ToolNotFoundError,
    ToolResultSerializationError,
    ToolValidationError,
)
from monkeybox.core.tools import ToolCall
from tests.conftest import MockModel


@pytest.mark.asyncio
async def test_agent_basic_init(mock_model):
    """Test that Agent initializes correctly with required parameters.

    Verifies:
    - Model is properly stored
    - System prompt becomes first message in history
    - Default values (name, max_steps) are set correctly
    - History is initialized with system message
    """
    agent = Agent(model=mock_model, system_prompt="You are a helpful assistant", name="test_agent")

    assert agent.model == mock_model
    assert agent.system_prompt == "You are a helpful assistant"
    assert agent.name == "test_agent"
    assert agent.max_steps == 15
    assert len(agent.history) == 1
    assert agent.history[0]["role"] == "system"


def test_agent_max_steps_validation(mock_model):
    """Test that Agent validates max_steps parameter.

    Verifies:
    - max_steps must be greater than 0
    - ValueError is raised with clear message for invalid values
    - Agent can be created with valid positive values
    """
    # Test invalid values
    with pytest.raises(ValueError, match="max_steps must be greater than 0, got 0"):
        Agent(mock_model, max_steps=0)

    with pytest.raises(ValueError, match="max_steps must be greater than 0, got -5"):
        Agent(mock_model, max_steps=-5)

    # Test valid values work
    agent = Agent(mock_model, max_steps=1)
    assert agent.max_steps == 1

    agent = Agent(mock_model, max_steps=100)
    assert agent.max_steps == 100


@pytest.mark.asyncio
async def test_agent_tool_execution(mock_model, sample_tool):
    """Test tool execution flow including success and error cases.

    Verifies:
    - Tools are executed with correct arguments
    - Results are returned as strings
    - Unknown tools return error messages
    - Tool errors are handled gracefully
    - Tool function is actually called with correct parameters
    """
    # Wrap the sample tool with a mock to verify it's called
    original_func = sample_tool
    mock_tool = Mock(side_effect=original_func)
    mock_tool.__name__ = "add_numbers"
    mock_tool.__doc__ = "Add two numbers together."

    mock_model.response_tool_calls = [
        ToolCall(name="add_numbers", args={"a": 2, "b": 3}, id="call_123")
    ]

    agent = Agent(model=mock_model, tools=[mock_tool])

    result = await agent._execute_tool("add_numbers", {"a": 2, "b": 3})
    assert result == "5"

    mock_tool.assert_called_once_with(a=2, b=3)

    with pytest.raises(ToolNotFoundError) as exc_info:
        await agent._execute_tool("unknown_tool", {})
    assert exc_info.value.tool_name == "unknown_tool"
    assert "add_numbers" in exc_info.value.available_tools


@pytest.mark.asyncio
async def test_agent_history_management(mock_model):
    """Test conversation history management and reset functionality.

    Verifies:
    - Messages are added to history correctly
    - Reset clears all messages except system prompt
    - System prompt is preserved after reset
    """
    agent = Agent(
        model=mock_model,
        system_prompt="System prompt",
    )

    agent.history.append({"role": "user", "content": "Hello"})
    agent.history.append({"role": "assistant", "content": "Hi there"})

    expected_full_history = [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]
    assert agent.history == expected_full_history

    agent.reset()
    expected_reset_history = [{"role": "system", "content": "System prompt"}]
    assert agent.history == expected_reset_history


@pytest.mark.asyncio
async def test_agent_as_tool(mock_model):
    """Test that Agent.as_tool creates callable function and can be executed.

    Verifies:
    - Agent.as_tool creates callable function
    - Function has correct name and docstring
    - Function can be called and returns agent's response
    - Tool execution creates fresh instance without polluting original history
    """
    agent = Agent(model=mock_model, name="helper", system_prompt="I help")

    # Add some history to the original agent
    agent.history.append({"role": "user", "content": "Previous conversation"})
    original_history = [
        {"role": "system", "content": "I help"},
        {"role": "user", "content": "Previous conversation"},
    ]
    assert agent.history == original_history

    tool_func = agent.as_tool
    assert callable(tool_func)
    assert tool_func.__name__ == "ask_helper"
    assert "I help" in tool_func.__doc__

    # Test that the tool can be executed
    result = await tool_func("Help me with something")
    assert result == "Mock response"

    # Verify original agent history is unchanged (fresh instance used)
    assert agent.history == original_history


@pytest.mark.asyncio
async def test_agent_max_steps_prevents_infinite_loops(mock_model, sample_tool):
    """Test that max_steps prevents infinite loops by raising MaxStepsReachedException.

    Verifies:
    - Agent stops after reaching max_steps even when model continues requesting tools
    - MaxStepsReachedException is raised with proper details
    - Proper error logging when max steps reached
    - History contains expected messages up to the limit
    - Boundary testing (max_steps=1, 2)
    """
    with patch("monkeybox.core.agent.MonkeyboxLogger") as mock_logger_class:
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        # Create a mock that always returns tool calls without text
        # This simulates a model that keeps requesting tools indefinitely
        class InfiniteToolCallModel(MockModel):
            async def chat(self, messages, tools=None, **kwargs):
                return ChatResponse(
                    message={"role": "assistant", "content": None},
                    text=None,  # No text when tool calls are present
                    tool_calls=[ToolCall(name="add_numbers", args={"a": 1, "b": 1}, id="call_123")],
                )

        infinite_model = InfiniteToolCallModel()
        agent = Agent(model=infinite_model, tools=[sample_tool], max_steps=2)

        with pytest.raises(MaxStepsReachedException) as exc_info:
            await agent.run("Keep adding numbers")

        # Verify exception details
        exception = exc_info.value
        assert exception.max_steps == 2
        assert exception.current_input == "Keep adding numbers"
        assert "reached maximum steps (2)" in str(exception)
        assert "Keep adding numbers" in str(exception)

        expected_history = [
            {"role": "user", "content": "Keep adding numbers"},
            {"role": "assistant", "content": None},
            {"role": "tool", "content": "2"},
            {"role": "assistant", "content": None},
            {"role": "tool", "content": "2"},
        ]
        assert agent.history == expected_history

        # Verify max steps error was logged
        mock_logger.log_max_steps_reached.assert_called_with(2)

    # Test boundary conditions
    # max_steps=1: should execute exactly one step
    # Create another infinite tool call model for this test
    infinite_model_one = InfiniteToolCallModel()
    agent_one = Agent(infinite_model_one, tools=[sample_tool], max_steps=1)

    with pytest.raises(MaxStepsReachedException) as exc_info:
        await agent_one.run("Add numbers")

    # Verify exception details for max_steps=1
    exception = exc_info.value
    assert exception.max_steps == 1
    assert exception.current_input == "Add numbers"

    expected_history_one = [
        {"role": "user", "content": "Add numbers"},
        {"role": "assistant", "content": None},
        {"role": "tool", "content": "2"},
    ]
    assert agent_one.history == expected_history_one


@pytest.mark.asyncio
async def test_agent_context_manager_lifecycle(mock_model):
    """Test agent async context manager proper __aenter__ and __aexit__ behavior.

    Verifies:
    - __aenter__ returns the agent instance
    - __aexit__ is called on normal completion
    - __aexit__ is called even when errors occur (resource cleanup)
    - Agent functions normally within context
    - Consolidates resource cleanup error testing
    """
    cleanup_called = False
    enter_called = False

    class TestAgent(Agent):
        async def __aenter__(self):
            nonlocal enter_called
            enter_called = True
            return await super().__aenter__()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            nonlocal cleanup_called
            cleanup_called = True
            await super().__aexit__(exc_type, exc_val, exc_tb)

    agent = TestAgent(model=mock_model)

    # Test normal operation
    async with agent as ctx_agent:
        assert enter_called
        assert ctx_agent == agent
        result = await ctx_agent.run("test")
        assert result == "Mock response"

    assert cleanup_called

    # Test cleanup on error
    cleanup_called = False
    enter_called = False

    with pytest.raises(ValueError):
        async with TestAgent(mock_model):
            assert enter_called
            raise ValueError("Simulated error")

    # Verify cleanup was called despite error
    assert cleanup_called


@pytest.mark.asyncio
async def test_agent_json_serialization_error(mock_model):
    """Test graceful handling of tools that return non-JSON-serializable objects.

    Some tools might return complex Python objects that can't be serialized
    to JSON for the LLM. This test ensures we handle such cases gracefully.

    Verifies:
    - Non-serializable objects are caught
    - Error message is returned instead of crashing
    - Agent continues to function after serialization error
    """

    def bad_tool() -> object:
        """Tool that returns non-serializable object."""
        return object()

    agent = Agent(model=mock_model, tools=[bad_tool])

    with pytest.raises(ToolResultSerializationError) as exc_info:
        await agent._execute_tool("bad_tool", {})
    assert exc_info.value.tool_name == "bad_tool"
    assert exc_info.value.result_type is object


@pytest.mark.asyncio
async def test_agent_thinking_logging(mock_model):
    """Test that agent properly logs thinking/reasoning content from model responses.

    This test verifies the integration between the agent and logger when
    models return thinking content (e.g., Anthropic's thinking mode or
    OpenAI's reasoning traces).

    Verifies:
    - Thinking content is extracted from ChatResponse
    - Logger's log_thinking method is called with correct parameters
    - Response text is still returned normally
    """

    async def mock_chat(messages, tools=None, **kwargs):
        _ = messages, tools, kwargs  # Mark as used
        return ChatResponse(
            message={"role": "assistant", "content": "Response"},
            text="Final answer",
            tool_calls=[],
            thinking="Let me think about this...",
        )

    mock_model.chat = mock_chat

    with patch("monkeybox.core.agent.MonkeyboxLogger") as mock_logger_class:
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        agent = Agent(model=mock_model, system_prompt="Test")
        result = await agent.run("Question")

        mock_logger.log_thinking.assert_called_once_with(
            agent.name, mock_model.model_name, "Let me think about this..."
        )
        assert result == "Final answer"


@pytest.mark.asyncio
async def test_agent_sync_tool_execution(mock_model):
    """Agent handles sync/async tools correctly."""

    def sync_tool(msg: str) -> str:
        return f"sync: {msg}"

    async def async_tool(msg: str) -> str:
        return f"async: {msg}"

    agent = Agent(model=mock_model, tools=[sync_tool, async_tool])

    sync_result = await agent._execute_tool("sync_tool", {"msg": "hello"})
    assert sync_result == "sync: hello"

    async_result = await agent._execute_tool("async_tool", {"msg": "world"})
    assert async_result == "async: world"


@pytest.mark.asyncio
async def test_agent_tool_execution_errors(mock_model):
    """Test agent handling tool execution errors."""

    def failing_tool() -> str:
        raise ValueError("Tool failed!")

    agent = Agent(model=mock_model, tools=[failing_tool])

    with pytest.raises(ToolExecutionError) as exc_info:
        await agent._execute_tool("failing_tool", {})
    assert exc_info.value.tool_name == "failing_tool"
    assert isinstance(exc_info.value.error, ValueError)
    assert str(exc_info.value.error) == "Tool failed!"


@pytest.mark.asyncio
async def test_agent_concurrent_tool_execution(mock_model):
    """Test that agent handles concurrent tool executions properly."""
    call_count = 0

    async def slow_tool(delay: float) -> str:
        """Tool that simulates slow operation."""
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(delay)
        return f"Result after {delay}s"

    agent = Agent(mock_model, tools=[slow_tool])

    # Execute multiple tools concurrently
    tasks = []
    for _ in range(3):
        task = agent._execute_tool("slow_tool", {"delay": 0.01})
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    assert all("Result after" in r for r in results)
    assert call_count == 3


@pytest.mark.asyncio
async def test_tool_validation_non_callable():
    """Test that non-callable tools raise ToolValidationError."""
    model = Mock()
    model.model_name = "test-model"

    with pytest.raises(ToolValidationError, match="Tool .* is not callable"):
        Agent(model=model, tools=["not a function"])


@pytest.mark.asyncio
async def test_tool_validation_no_name():
    """Test that tools without __name__ raise ToolValidationError."""
    model = Mock()
    model.model_name = "test-model"

    # Create a mock callable with invalid __name__ (empty string)
    tool = Mock()
    tool.__name__ = ""  # Empty string is falsy but valid for __name__

    with pytest.raises(ToolValidationError, match="Tool .* has no valid __name__ attribute"):
        Agent(model=model, tools=[tool])

    # Also test with "<lambda>" which is considered invalid
    lambda_tool = Mock()
    lambda_tool.__name__ = "<lambda>"

    with pytest.raises(ToolValidationError, match="Tool .* has no valid __name__ attribute"):
        Agent(model=model, tools=[lambda_tool])


@pytest.mark.asyncio
async def test_tool_name_conflict_warning(mock_model, caplog):
    """Test that tool name conflicts log warnings."""

    def duplicate_tool():
        return "result1"

    def duplicate_tool():  # noqa: F811
        return "result2"

    agent = Agent(model=mock_model, tools=[duplicate_tool, duplicate_tool])

    # Check that warning was logged
    assert "Tool name conflict" in caplog.text
    assert "duplicate_tool already exists" in caplog.text

    # Verify only one tool is in the map
    assert len(agent.tool_map) == 1


@pytest.mark.asyncio
async def test_agent_tool_name_conflict_warning(mock_model, caplog):
    """Test that agent tool name conflicts log warnings."""
    # Create two agents with the same name
    sub_agent1 = Agent(model=mock_model, name="helper")
    sub_agent2 = Agent(model=mock_model, name="helper")

    agent = Agent(model=mock_model, tools=[sub_agent1, sub_agent2])

    # Check that warning was logged
    assert "Tool name conflict" in caplog.text
    assert "ask_helper already exists" in caplog.text

    # Verify only one tool is in the map
    assert len(agent.tool_map) == 1


@pytest.mark.asyncio
async def test_model_communication_error(mock_model):
    """Test that model communication errors are properly raised."""
    # Make the model raise an exception
    mock_model.chat = AsyncMock(side_effect=Exception("API error"))

    agent = Agent(model=mock_model, system_prompt="Test")

    with pytest.raises(
        ModelCommunicationError,
        match="Failed to communicate with model 'mock-model': Exception: API error",
    ):
        await agent.run("Test input")


@pytest.mark.asyncio
async def test_tool_type_error_handling(mock_model):
    """Test better error handling for tool argument mismatch."""

    def strict_tool(required_arg: str) -> str:
        return required_arg

    agent = Agent(model=mock_model, tools=[strict_tool])

    # Call tool with wrong arguments
    with pytest.raises(ToolExecutionError) as exc_info:
        await agent._execute_tool("strict_tool", {"wrong_arg": "value"})

    assert exc_info.value.tool_name == "strict_tool"
    assert isinstance(exc_info.value.error, TypeError)


@pytest.mark.asyncio
async def test_critical_exception_reraising(mock_model):
    """Test that critical exceptions are re-raised."""

    def interrupt_tool():
        raise KeyboardInterrupt()

    agent = Agent(model=mock_model, tools=[interrupt_tool])

    with pytest.raises(KeyboardInterrupt):
        await agent._execute_tool("interrupt_tool", {})


@pytest.mark.asyncio
async def test_context_manager_return_value(mock_model):
    """Test that __aexit__ returns None properly."""
    agent = Agent(model=mock_model)

    async with agent as a:
        assert a is agent

    # Test that __aexit__ returns None
    result = await agent.__aexit__(None, None, None)
    assert result is None


@pytest.mark.asyncio
async def test_last_response_stored_on_max_steps(mock_model):
    """Test that last response is stored when max steps reached."""
    # Configure model to always return tool calls
    tool_call = Mock()
    tool_call.name = "test_tool"
    tool_call.args = {}
    tool_call.id = "123"

    def test_tool():
        return "result"

    agent = Agent(model=mock_model, tools=[test_tool], max_steps=1)

    # Configure model to always return tool calls without text (to trigger max steps)
    mock_model.chat = AsyncMock(
        return_value=ChatResponse(
            message={"role": "assistant", "content": None},
            text=None,  # No text, only tool calls
            thinking=None,
            tool_calls=[tool_call],
        )
    )

    with pytest.raises(MaxStepsReachedException) as exc_info:
        await agent.run("Test")

    # Verify the exception was raised with correct params
    assert exc_info.value.max_steps == 1
    assert exc_info.value.current_input == "Test"


@pytest.mark.asyncio
async def test_tool_execution_full_traceback_logging(mock_model, caplog):
    """Test that full traceback is logged on tool execution errors."""

    def error_tool():
        raise ValueError("Detailed error message")

    agent = Agent(model=mock_model, tools=[error_tool])

    with pytest.raises(ToolExecutionError) as exc_info:
        await agent._execute_tool("error_tool", {})

    assert exc_info.value.tool_name == "error_tool"
    assert isinstance(exc_info.value.error, ValueError)
    assert str(exc_info.value.error) == "Detailed error message"

    # Check that traceback was logged
    assert "Traceback" in caplog.text
    assert "ValueError: Detailed error message" in caplog.text


@pytest.mark.asyncio
async def test_serialization_error_logging(mock_model, caplog):
    """Test that serialization errors include type information."""

    # Return a non-serializable object
    def bad_serialization_tool():
        return object()  # object() cannot be JSON serialized

    agent = Agent(model=mock_model, tools=[bad_serialization_tool])

    with pytest.raises(ToolResultSerializationError) as exc_info:
        await agent._execute_tool("bad_serialization_tool", {})

    assert exc_info.value.tool_name == "bad_serialization_tool"
    assert exc_info.value.result_type is object

    # Check that type was logged
    assert "Result type: <class 'object'>" in caplog.text


@pytest.mark.asyncio
async def test_intermediate_response_with_text_and_tools(mock_model):
    """Test that responses with both text and tool calls are treated as intermediate.

    This is a regression test for a bug where result_text was set prematurely
    when a response contained both text and tool calls. The correct behavior
    is that such responses should be treated as intermediate - the tool calls
    should be executed and the loop should continue.

    Verifies:
    - Responses with both text and tool calls don't end the conversation
    - Tool calls are executed even when text is present
    - Only responses with text but NO tool calls are final
    """
    # Tool that tracks if it was called
    tool_called = False

    def test_tool():
        nonlocal tool_called
        tool_called = True
        return "Tool executed"

    # Configure mock to return:
    # 1. First response: text + tool call (intermediate)
    # 2. Second response: text only (final)
    call_count = 0

    async def mock_chat(messages, tools=None, **kwargs):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            # First call: return both text and tool call
            return ChatResponse(
                message={"role": "assistant", "content": "Let me help you with that..."},
                text="Let me help you with that...",  # This should NOT be the final result
                tool_calls=[ToolCall(name="test_tool", args={}, id="call_1")],
                thinking=None,
            )
        else:
            # Second call: return only text (final response)
            return ChatResponse(
                message={"role": "assistant", "content": "Final answer after tool execution"},
                text="Final answer after tool execution",
                tool_calls=[],  # No tool calls - this is final
                thinking=None,
            )

    mock_model.chat = mock_chat
    agent = Agent(model=mock_model, tools=[test_tool])

    result = await agent.run("Test input")

    # Verify the tool was called
    assert tool_called, "Tool should have been executed even though first response had text"

    # Verify the final result is from the second response, not the first
    assert result == "Final answer after tool execution"
    assert "Let me help you" not in result  # First response text should NOT be the result

    # Verify we made exactly 2 model calls
    assert call_count == 2
