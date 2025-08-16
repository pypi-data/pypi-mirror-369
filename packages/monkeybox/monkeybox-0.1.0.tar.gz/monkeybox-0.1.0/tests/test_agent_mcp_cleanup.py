"""Tests for Agent MCP cleanup and error scenarios."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from monkeybox.core.agent import Agent, AgentState
from monkeybox.core.mcp_client import MCPServerConfig


@pytest.fixture
def mock_model():
    """Create a mock model for testing."""
    model = MagicMock()
    model.model_name = "test-model"
    model.chat = AsyncMock()
    model.format_tool_results = MagicMock(return_value=[])
    return model


@pytest.fixture
def mcp_config():
    """Create a test MCP configuration."""
    return MCPServerConfig(
        name="test-server",
        transport="stdio",
        command="test",
        args=["arg1"],
    )


@pytest.mark.asyncio
async def test_mcp_initialization_failure_cleanup(mock_model, mcp_config):
    """Test that MCP resources are cleaned up if initialization fails."""
    with patch("monkeybox.core.agent.MCPContext") as mock_cls:
        mock_context = AsyncMock()
        mock_context.__aenter__.side_effect = Exception("Init failed")
        mock_context.__aexit__ = AsyncMock()
        mock_cls.return_value = mock_context

        agent = Agent(mock_model, "Test", mcp_configs=[mcp_config])

        # Initial state should be UNOPENED
        assert agent._state == AgentState.UNOPENED

        with pytest.raises(Exception, match="Init failed"):
            await agent.run("Test")

        # Verify cleanup was attempted
        assert agent._state == AgentState.CLOSED
        mock_context.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_concurrent_run_calls(mock_model, mcp_config):
    """Test that concurrent run calls don't cause race conditions."""
    with patch("monkeybox.core.agent.MCPContext") as mock_cls:
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock()
        mock_context.__aexit__ = AsyncMock()
        mock_context.get_tools = MagicMock(return_value=[])
        mock_cls.return_value = mock_context

        # Mock model to return a simple response
        response = MagicMock()
        response.thinking = None
        response.tool_calls = None
        response.text = "Response"
        response.message = {"role": "assistant", "content": "Response"}
        mock_model.chat.return_value = response

        agent = Agent(mock_model, "Test", mcp_configs=[mcp_config])

        # Simulate concurrent calls
        import asyncio

        results = await asyncio.gather(
            agent.run("Test 1"), agent.run("Test 2"), return_exceptions=True
        )

        # Both should succeed without race conditions
        assert all(isinstance(r, str) for r in results)

        # MCP should only be initialized once
        mock_cls.assert_called_once()
        mock_context.__aenter__.assert_called_once()


@pytest.mark.asyncio
async def test_aclose_idempotent(mock_model, mcp_config):
    """Test that aclose() can be called multiple times safely."""
    with patch("monkeybox.core.agent.MCPContext") as mock_cls:
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock()
        mock_context.__aexit__ = AsyncMock()
        mock_context.get_tools = MagicMock(return_value=[])
        mock_cls.return_value = mock_context

        agent = Agent(mock_model, "Test", mcp_configs=[mcp_config])

        async with agent:
            pass

        # First close
        await agent.aclose()
        assert agent._state == AgentState.CLOSED

        # Second close should be a no-op
        await agent.aclose()
        assert agent._state == AgentState.CLOSED

        # __aexit__ should only be called once (from context manager exit which calls aclose)
        # Second aclose is a no-op due to state check
        assert mock_context.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_context_manager_exception_cleanup(mock_model, mcp_config):
    """Test that MCP is cleaned up when exception occurs in context manager."""
    with patch("monkeybox.core.agent.MCPContext") as mock_cls:
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock()
        mock_context.__aexit__ = AsyncMock()
        mock_context.get_tools = MagicMock(return_value=[])
        mock_cls.return_value = mock_context

        agent = Agent(mock_model, "Test", mcp_configs=[mcp_config])

        with pytest.raises(ValueError, match="Test error"):
            async with agent:
                raise ValueError("Test error")

        # Verify cleanup happened
        assert agent._state == AgentState.CLOSED
        mock_context.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_partial_mcp_tool_loading_failure(mock_model, mcp_config):
    """Test handling when MCP tool loading partially fails."""
    with patch("monkeybox.core.agent.MCPContext") as mock_cls:
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock()
        mock_context.__aexit__ = AsyncMock()

        # Simulate partial tool loading failure
        def get_tools_with_error():
            raise Exception("Failed to get some tools")

        mock_context.get_tools = get_tools_with_error
        mock_cls.return_value = mock_context

        agent = Agent(mock_model, "Test", mcp_configs=[mcp_config])

        with pytest.raises(Exception, match="Failed to get some tools"):
            await agent.run("Test")

        # Agent should be closed after failure
        assert agent._state == AgentState.CLOSED
        mock_context.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_run_after_close_error_message(mock_model):
    """Test that error message is helpful when trying to use closed agent."""
    agent = Agent(mock_model, "Test")

    # Close the agent
    await agent.aclose()

    # Try to run after closing
    with pytest.raises(RuntimeError) as exc_info:
        await agent.run("Test")

    # Check for helpful error message
    assert "Cannot use a closed Agent" in str(exc_info.value)
    assert "Create a new Agent instance" in str(exc_info.value)


@pytest.mark.asyncio
async def test_double_context_manager_entry_error(mock_model):
    """Test helpful error when trying to enter context manager twice."""
    agent = Agent(mock_model, "Test")

    async with agent:
        with pytest.raises(RuntimeError) as exc_info:
            await agent.__aenter__()

        # Check for helpful error message
        assert "Cannot open an agent instance more than once" in str(exc_info.value)
        assert "already opened and active" in str(exc_info.value)
