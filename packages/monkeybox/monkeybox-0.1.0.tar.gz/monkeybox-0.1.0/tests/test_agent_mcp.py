"""Tests for Agent MCP integration and resource management."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from monkeybox import Agent, OpenAIModel
from monkeybox.core.agent import AgentState
from monkeybox.core.mcp_client import MCPServerConfig


@pytest.fixture
def mock_model():
    """Create a mock model."""
    model = MagicMock(spec=OpenAIModel)
    model.model_name = "test-model"
    return model


@pytest.fixture
def mcp_config():
    """Create a test MCP config."""
    return MCPServerConfig(
        name="test",
        transport="stdio",
        command="test",
        args=["arg1"],
    )


class TestAgentMCPIntegration:
    """Test Agent MCP integration."""

    def test_agent_init_with_mcp_configs(self, mock_model, mcp_config):
        """Test agent initialization with MCP configs."""
        agent = Agent(
            mock_model,
            "Test prompt",
            mcp_configs=[mcp_config],
            name="TestAgent",
        )

        assert agent.mcp_configs == [mcp_config]
        assert agent._state == AgentState.UNOPENED
        assert agent._mcp_context is None
        assert agent._mcp_tools == []
        assert agent._base_tools == []

    async def test_agent_context_manager_lifecycle(self, mock_model, mcp_config):
        """Test agent lifecycle with context manager."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            # Make get_tools return a list, not a coroutine
            mock_context.get_tools = MagicMock(
                return_value=[
                    MagicMock(__name__="mcp_tool1"),
                    MagicMock(__name__="mcp_tool2"),
                ]
            )
            mock_cls.return_value = mock_context

            agent = Agent(
                mock_model,
                "Test prompt",
                mcp_configs=[mcp_config],
            )

            # Check initial state
            assert agent._state == AgentState.UNOPENED

            # Enter context
            async with agent:
                assert agent._state == AgentState.OPENED
                assert agent._mcp_context is not None
                mock_context.__aenter__.assert_called_once()
                assert len(agent._mcp_tools) == 2
                assert len(agent.tools) == 2

            # Exit context
            assert agent._state == AgentState.CLOSED
            mock_context.__aexit__.assert_called_once()
            assert agent._mcp_context is None

    async def test_agent_lazy_mcp_initialization(self, mock_model, mcp_config):
        """Test lazy MCP initialization on first run."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            # Make get_tools return a list, not a coroutine
            mock_context.get_tools = MagicMock(
                return_value=[
                    MagicMock(__name__="mcp_tool1"),
                    MagicMock(__name__="mcp_tool2"),
                ]
            )
            mock_cls.return_value = mock_context

            # Mock the model's chat method
            mock_response = AsyncMock()
            mock_response.message = {"role": "assistant", "content": "Test response"}
            mock_response.thinking = None
            mock_response.tool_calls = None
            mock_response.text = "Test response"
            mock_model.chat = AsyncMock(return_value=mock_response)

            agent = Agent(
                mock_model,
                "Test prompt",
                mcp_configs=[mcp_config],
            )

            # Initial state
            assert agent._state == AgentState.UNOPENED

            # First run should initialize MCP
            await agent.run("Test input")
            assert agent._state == AgentState.OPENED
            mock_context.__aenter__.assert_called_once()
            assert len(agent._mcp_tools) == 2

            # Second run should reuse connection
            await agent.run("Test input 2")
            assert agent._state == AgentState.OPENED
            # Still only called once
            assert mock_context.__aenter__.call_count == 1

            # Manual cleanup
            await agent.aclose()
            assert agent._state == AgentState.CLOSED
            mock_context.__aexit__.assert_called_once()

    async def test_agent_without_mcp(self, mock_model):
        """Test agent without MCP configs works normally."""
        # Mock the model's chat method
        mock_response = AsyncMock()
        mock_response.message = {"role": "assistant", "content": "Test response"}
        mock_response.thinking = None
        mock_response.tool_calls = None
        mock_response.text = "Test response"
        mock_model.chat = AsyncMock(return_value=mock_response)

        def dummy_tool(x):
            """Dummy tool for testing."""
            return x

        agent = Agent(
            mock_model,
            "Test prompt",
            tools=[dummy_tool],  # Named function instead of lambda
        )

        # No MCP configs
        assert agent.mcp_configs == []
        assert agent._state == AgentState.UNOPENED

        # Run without context manager
        result = await agent.run("Test input")
        assert result == "Test response"
        # State remains UNOPENED since no MCP
        assert agent._state == AgentState.UNOPENED

        # No cleanup needed
        await agent.aclose()
        assert agent._state == AgentState.CLOSED

    async def test_closed_agent_error(self, mock_model, mcp_config):
        """Test that closed agent cannot be used."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            mock_context.get_tools = MagicMock(return_value=[])
            mock_cls.return_value = mock_context

            agent = Agent(
                mock_model,
                "Test prompt",
                mcp_configs=[mcp_config],
            )

            # Close the agent
            async with agent:
                pass

            assert agent._state == AgentState.CLOSED

            # Try to use closed agent
            with pytest.raises(RuntimeError, match="Cannot use a closed Agent"):
                await agent.run("Test")

    async def test_agent_cannot_reopen(self, mock_model, mcp_config):
        """Test that agent cannot be reopened after closing."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            mock_context.get_tools = MagicMock(return_value=[])
            mock_cls.return_value = mock_context

            agent = Agent(
                mock_model,
                "Test prompt",
                mcp_configs=[mcp_config],
            )

            # Use and close
            async with agent:
                pass

            # Try to reopen
            with pytest.raises(RuntimeError, match="Cannot reopen a closed agent"):
                async with agent:
                    pass

    async def test_agent_cannot_open_twice(self, mock_model, mcp_config):
        """Test that agent cannot be opened twice."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            mock_context.get_tools = MagicMock(return_value=[])
            mock_cls.return_value = mock_context

            agent = Agent(
                mock_model,
                "Test prompt",
                mcp_configs=[mcp_config],
            )

            async with agent:
                # Try to open again while already open
                with pytest.raises(
                    RuntimeError, match="Cannot open an agent instance more than once"
                ):
                    await agent.__aenter__()

    def test_agent_as_tool_preserves_mcp_configs(self, mock_model, mcp_config):
        """Test that as_tool preserves MCP configs."""

        def dummy_tool():
            return "dummy"

        agent = Agent(
            mock_model,
            "Test prompt",
            tools=[dummy_tool],
            mcp_configs=[mcp_config],
            name="TestAgent",
        )

        # Get agent as tool
        agent_tool = agent.as_tool

        # Check it's a callable
        assert callable(agent_tool)
        assert agent_tool.__name__ == "ask_TestAgent"

    async def test_multiple_agents_with_mcp(self, mock_model, mcp_config):
        """Test multiple agents can have independent MCP contexts."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            # Create separate mock contexts for each agent
            mock_context1 = AsyncMock()
            mock_context1.get_tools = MagicMock(return_value=[MagicMock(__name__="tool1")])

            mock_context2 = AsyncMock()
            mock_context2.get_tools = MagicMock(return_value=[MagicMock(__name__="tool2")])

            mock_cls.side_effect = [mock_context1, mock_context2]

            agent1 = Agent(mock_model, "Agent 1", mcp_configs=[mcp_config])
            agent2 = Agent(mock_model, "Agent 2", mcp_configs=[mcp_config])

            # Use both agents
            async with agent1:
                async with agent2:
                    assert len(agent1.tools) == 1
                    assert len(agent2.tools) == 1
                    assert agent1.tools[0].__name__ == "tool1"
                    assert agent2.tools[0].__name__ == "tool2"

            # Both contexts should be cleaned up
            mock_context1.__aexit__.assert_called_once()
            mock_context2.__aexit__.assert_called_once()

    async def test_agent_exception_during_context_manager(self, mock_model, mcp_config):
        """Test that MCP cleanup happens even if exception occurs in context."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            mock_context.get_tools = MagicMock(return_value=[])
            mock_cls.return_value = mock_context

            agent = Agent(
                mock_model,
                "Test prompt",
                mcp_configs=[mcp_config],
            )

            with pytest.raises(ValueError, match="Test error"):
                async with agent:
                    assert agent._state == AgentState.OPENED
                    raise ValueError("Test error")

            # Agent should still be closed properly
            assert agent._state == AgentState.CLOSED
            mock_context.__aexit__.assert_called_once()

    async def test_agent_multiple_aclose_calls(self, mock_model, mcp_config):
        """Test that multiple aclose calls are safe."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            mock_context.get_tools = MagicMock(return_value=[])
            mock_cls.return_value = mock_context

            agent = Agent(
                mock_model,
                "Test prompt",
                mcp_configs=[mcp_config],
            )

            # Open the agent
            await agent.__aenter__()
            assert agent._state == AgentState.OPENED

            # Close multiple times
            await agent.aclose()
            assert agent._state == AgentState.CLOSED

            # Second close should be safe no-op
            await agent.aclose()
            assert agent._state == AgentState.CLOSED

            # MCP cleanup should only happen once
            assert mock_context.__aexit__.call_count == 1

    async def test_agent_mcp_connection_failure(self, mock_model, mcp_config):
        """Test handling of MCP connection failures."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            # Simulate connection failure
            mock_context.__aenter__.side_effect = Exception("MCP connection failed")
            mock_cls.return_value = mock_context

            agent = Agent(
                mock_model,
                "Test prompt",
                mcp_configs=[mcp_config],
            )

            # Context manager should propagate the exception
            with pytest.raises(Exception, match="MCP connection failed"):
                async with agent:
                    pass

    async def test_agent_verbose_flag_affects_logging(self, mock_model, mcp_config):
        """Test that verbose flag controls MCP logging."""
        with patch("monkeybox.core.agent.MCPContext") as mock_cls:
            mock_context = AsyncMock()
            mock_context.get_tools = MagicMock(return_value=[MagicMock(__name__="tool1")])
            mock_cls.return_value = mock_context

            with patch("monkeybox.core.agent.MonkeyboxLogger") as mock_logger_cls:
                mock_logger = MagicMock()
                mock_logger_cls.return_value = mock_logger

                # Create agent with verbose=False
                agent = Agent(
                    mock_model,
                    "Test prompt",
                    mcp_configs=[mcp_config],
                    verbose=False,
                )

                async with agent:
                    # MCP setup logging should not be called when verbose=False
                    mock_logger.log_mcp_setup.assert_not_called()

                # MCP cleanup logging should not be called when verbose=False
                mock_logger.log_mcp_cleanup.assert_not_called()

                # Create agent with verbose=True
                agent2 = Agent(
                    mock_model,
                    "Test prompt",
                    mcp_configs=[mcp_config],
                    verbose=True,
                )

                async with agent2:
                    # MCP setup logging should be called when verbose=True
                    mock_logger.log_mcp_setup.assert_called_once()

                # MCP cleanup logging should be called when verbose=True
                mock_logger.log_mcp_cleanup.assert_called_once()
