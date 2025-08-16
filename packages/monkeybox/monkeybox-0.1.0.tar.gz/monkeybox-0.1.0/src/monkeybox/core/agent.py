"""Simplified agent implementation."""

import asyncio
import enum
import json
import traceback
from collections.abc import Callable
from typing import Any
from uuid import uuid4

import weave

from .base_model import BaseModel
from .exceptions import (
    MaxStepsReachedException,
    ModelCommunicationError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolResultSerializationError,
    ToolValidationError,
)
from .logger import MonkeyboxLogger
from .mcp_client import MCPContext, MCPServerConfig


class AgentState(enum.Enum):
    UNOPENED = 1
    OPENED = 2
    CLOSED = 3


class Agent:
    """An AI agent that orchestrates interactions between language models and tools.

    The Agent class provides a high-level interface for building AI agents that can:
    - Execute Python functions as tools
    - Integrate with MCP (Model Context Protocol) servers
    - Use other agents as tools for multi-agent architectures
    - Handle complex, multi-step conversations with tool usage

    The agent manages the conversation flow, tool execution, and resource cleanup
    automatically. It supports both OpenAI and Anthropic models through a unified
    interface while preserving provider-specific features.

    Args:
        model: The language model to use (OpenAIModel or AnthropicModel)
        system_prompt: Initial system instructions for the agent
        tools: List of Python functions or other agents to use as tools
        mcp_configs: List of MCP server configurations for external tools
        name: Optional name for the agent (used in logging and as_tool)
        max_steps: Maximum number of tool call iterations (default: 15)
        verbose: Whether to enable detailed logging output (default: True)

    Example:
        >>> from monkeybox import Agent, OpenAIModel
        >>>
        >>> def add(a: int, b: int) -> int:
        ...     return a + b
        >>>
        >>> agent = Agent(
        ...     OpenAIModel("gpt-4o-mini"),
        ...     "You are a helpful math assistant.",
        ...     tools=[add]
        ... )
        >>>
        >>> async with agent:
        ...     result = await agent.run("What is 15 + 27?")
        ...     print(result)

    Note:
        - MCP resources are initialized lazily on first use
        - Use as a context manager for automatic resource cleanup
        - Agents are single-use; create new instances for new conversations
    """

    def __init__(
        self,
        model: BaseModel,
        system_prompt: str | None = None,
        tools: list[Callable] | None = None,
        mcp_configs: list[MCPServerConfig] | None = None,
        name: str | None = None,
        max_steps: int = 15,
        verbose: bool = True,
    ):
        if max_steps <= 0:
            raise ValueError(f"max_steps must be greater than 0, got {max_steps}")

        self.model = model
        self.name = name or f"agent_{uuid4()!s}"
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.mcp_configs = mcp_configs or []
        self.max_steps = max_steps
        self.verbose = verbose
        self.logger = MonkeyboxLogger(self.name, verbose=verbose)
        self.is_nested = False
        self.history: list[dict[str, object]] = []
        if system_prompt:
            self.history = [{"role": "system", "content": system_prompt}]

        self.tool_map: dict[str, Any] = {}
        self.tool_callables: list[Callable[..., Any]] = []

        self._state = AgentState.UNOPENED
        self._mcp_context: MCPContext | None = None
        self._mcp_tools: list[Callable] = []
        self._base_tools = list(self.tools)

        self._rebuild_tool_registry()

    def _process_tools(self) -> None:
        """Process and validate tools, building tool_map and tool_callables."""
        for tool in self.tools:
            if isinstance(tool, Agent):
                func_name = f"ask_{tool.name}"
                if func_name in self.tool_map:
                    self.logger.logger.warning(
                        f"Tool name conflict: {func_name} already exists, skipping",
                    )
                    continue
                self.tool_map[func_name] = tool.as_tool
                self.tool_callables.append(tool.as_tool)
            else:
                # Validate non-Agent tools
                if not callable(tool):
                    raise ToolValidationError(f"Tool {tool} is not callable")

                # Get tool name safely
                tool_name = getattr(tool, "__name__", None)
                if not tool_name or tool_name == "<lambda>":
                    raise ToolValidationError(f"Tool {tool} has no valid __name__ attribute")

                if tool_name in self.tool_map:
                    self.logger.logger.warning(
                        f"Tool name conflict: {tool_name} already exists, skipping",
                    )
                    continue

                self.tool_map[tool_name] = tool
                self.tool_callables.append(tool)

    def _rebuild_tool_registry(self) -> None:
        """Rebuild tool registry from current tools, avoiding duplicate warnings from prior state."""
        # Reset registries before processing current tools
        self.tool_map = {}
        self.tool_callables = []
        self._process_tools()

    @property
    def as_tool(self) -> Callable:
        """Return this agent as a callable tool function."""

        async def ask_agent(question: str) -> str:
            """Ask this agent a question."""
            new_agent = Agent(
                self.model,
                self.system_prompt,
                self._base_tools,
                self.mcp_configs,
                self.name,
                self.max_steps,
            )
            async with new_agent:
                new_agent.is_nested = True
                new_agent.logger.log_agent_call(new_agent.name, new_agent.model.model_name)
                try:
                    result = await new_agent.run(question)
                    return result
                finally:
                    new_agent.logger.log_agent_completion(
                        new_agent.name,
                        new_agent.model.model_name,
                    )

        ask_agent.__name__ = f"ask_{self.name}"
        ask_agent.__doc__ = f"Ask {self.name} agent: {self.system_prompt}"
        return ask_agent

    async def _handle_tool_calls(
        self,
        tool_calls: list[Any],
    ) -> list[dict[str, object]] | dict[str, object]:
        """Handle tool calls from the model, execute them, and return formatted results."""
        tool_results = []
        for tool_call in tool_calls:
            self.logger.log_tool_call(tool_call.name, tool_call.args, tool_call.id)
            result = await self._execute_tool(tool_call.name, tool_call.args)
            self.logger.log_tool_result(result)

            tool_results.append(
                {
                    "tool_call_id": tool_call.id,
                    "content": result,
                    "name": tool_call.name,
                },
            )

        return self.model.format_tool_results(tool_results)

    @weave.op(name="agent_run")
    async def run(self, user_input: str, **kwargs) -> str:
        """Run the agent with user input."""
        if self._state == AgentState.CLOSED:
            raise RuntimeError(
                "Cannot use a closed Agent.\n"
                "Reason: Agents are single-use to prevent state leakage between runs.\n"
                "Solution: Create a new Agent instance:\n"
                "  agent = Agent(model, prompt, mcp_configs=[...])"
            )

        # Initialize MCP if needed (lazy initialization)
        if self._state == AgentState.UNOPENED and self.mcp_configs:
            try:
                self._state = AgentState.OPENED
                self._mcp_context = MCPContext(*self.mcp_configs)
                await self._mcp_context.__aenter__()
                self._mcp_tools = self._mcp_context.get_tools()
                self.tools = self._base_tools + self._mcp_tools
                self._rebuild_tool_registry()

                if self.verbose:
                    self.logger.log_mcp_setup(len(self._mcp_tools))
            except Exception:
                # Clean up on initialization failure
                self._state = AgentState.CLOSED
                if self._mcp_context:
                    try:
                        await self._mcp_context.__aexit__(None, None, None)
                    except Exception:
                        pass  # Best effort cleanup
                    self._mcp_context = None
                raise

        self.history.append({"role": "user", "content": user_input})

        if not self.is_nested:
            self.logger.log_user_input(user_input)

        steps = 0
        result_text = ""

        while steps < self.max_steps:
            steps += 1

            if not self.is_nested:
                self.logger.log_step(steps, self.max_steps)

            try:
                response = await self.model.chat(self.history, tools=self.tool_callables, **kwargs)
            except ModelCommunicationError:
                # Re-raise ModelCommunicationError directly to avoid double-wrapping
                raise
            except Exception as e:
                self.logger.logger.error(f"Model communication error: {e}")
                raise ModelCommunicationError(self.model.model_name, e)

            self.history.append(response.message)

            if response.thinking:
                self.logger.log_thinking(self.name, self.model.model_name, response.thinking)

            if response.tool_calls:
                formatted_results = await self._handle_tool_calls(response.tool_calls)
                if isinstance(formatted_results, list):
                    self.history.extend(formatted_results)
                else:
                    self.history.append(formatted_results)
            elif response.text:
                if not self.is_nested:
                    self.logger.log_assistant_response(
                        self.name,
                        self.model.model_name,
                        response.text,
                    )
                result_text = response.text
                break

        if not result_text:
            self.logger.log_max_steps_reached(self.max_steps)
            raise MaxStepsReachedException(self.max_steps, user_input)

        if result_text and not self.is_nested:
            self.logger.log_final_response(result_text)

        return result_text

    @weave.op(name="tool_execution")
    async def _execute_tool(self, name: str, args: dict[str, object]) -> str:
        """Execute a tool by name with args and return a string result."""
        with weave.attributes(
            {
                "tool_name": name,
                "tool_type": "mcp"
                if hasattr(self, "_mcp_tools") and name in [t.__name__ for t in self._mcp_tools]
                else "python",
            }
        ):
            if name not in self.tool_map:
                available_tools = list(self.tool_map.keys())
                self.logger.logger.error(
                    f"Unknown tool: {name}. Available tools: {available_tools}"
                )
                raise ToolNotFoundError(name, available_tools)

            tool = self.tool_map[name]
            try:
                if asyncio.iscoroutinefunction(tool):
                    result = await tool(**args)
                else:
                    result = tool(**args)
            except (KeyboardInterrupt, SystemExit):
                # Re-raise critical exceptions
                raise
            except TypeError as e:
                # Provide better error message for argument mismatch
                error_msg = f"Tool {name} called with invalid arguments {args}: {e}"
                self.logger.logger.error(error_msg)
                raise ToolExecutionError(name, e)
            except Exception as e:
                # Log full traceback for debugging
                self.logger.logger.error(
                    f"Error executing tool {name}: {e}\n{traceback.format_exc()}"
                )
                raise ToolExecutionError(name, e)

            if isinstance(result, str):
                return result

            try:
                return json.dumps(result)
            except (TypeError, OverflowError) as e:
                self.logger.logger.error(
                    f"Could not serialize result from tool {name} to JSON: {e}\nResult type: {type(result)}",
                )
                raise ToolResultSerializationError(name, type(result))

    def reset(self) -> None:
        """Reset conversation history."""
        self.history = []
        if self.system_prompt:
            self.history.append({"role": "system", "content": self.system_prompt})

    async def __aenter__(self):
        """Async context manager entry."""
        if self._state != AgentState.UNOPENED:
            if self._state == AgentState.OPENED:
                raise RuntimeError(
                    "Cannot open an agent instance more than once.\n"
                    "Reason: Agent is already opened and active.\n"
                    "Solution: Use the existing agent or create a new instance."
                )
            else:  # CLOSED
                raise RuntimeError(
                    "Cannot reopen a closed agent.\n"
                    "Reason: Agents are single-use to prevent state leakage.\n"
                    "Solution: Create a new Agent instance:\n"
                    "  agent = Agent(model, prompt, mcp_configs=[...])"
                )

        self._state = AgentState.OPENED

        if self.mcp_configs:
            self._mcp_context = MCPContext(*self.mcp_configs)
            await self._mcp_context.__aenter__()

            self._mcp_tools = self._mcp_context.get_tools()
            self.tools = self._base_tools + self._mcp_tools
            self._rebuild_tool_registry()

            if self.verbose:
                self.logger.log_mcp_setup(len(self._mcp_tools))

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ARG002
        """Async context manager exit."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the agent and release resources."""
        if self._state == AgentState.CLOSED:
            return  # Already closed, no-op
        self._state = AgentState.CLOSED

        if self._mcp_context:
            await self._mcp_context.__aexit__(None, None, None)
            self._mcp_context = None

            if self.verbose:
                self.logger.log_mcp_cleanup()
