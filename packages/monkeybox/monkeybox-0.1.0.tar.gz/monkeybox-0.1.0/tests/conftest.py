"""Shared test fixtures and utilities for monkeybox tests."""

import asyncio
from typing import Callable, Optional

import pytest

from monkeybox.core.base_model import BaseModel, ChatResponse
from monkeybox.core.tools import ToolCall


class MockModel(BaseModel):
    """Mock model for testing Agent functionality."""

    def __init__(self, model_name: str = "mock-model"):
        super().__init__(model_name)
        self.response_text = "Mock response"
        self.response_tool_calls = []

    async def chat(
        self, messages: list[dict[str, object]], tools: Optional[list[Callable]] = None, **kwargs
    ) -> ChatResponse:
        return ChatResponse(
            message={"role": "assistant", "content": self.response_text},
            text=self.response_text,
            tool_calls=self.response_tool_calls,
        )

    def format_tools_for_api(self, tools: list[Callable]) -> list[dict[str, object]]:
        return [{"type": "function", "function": {"name": tool.__name__}} for tool in tools]

    def format_tool_results(self, tool_results: list[dict[str, object]]) -> list[dict[str, object]]:
        return [{"role": "tool", "content": str(result["content"])} for result in tool_results]


@pytest.fixture
def mock_model():
    """Provide a mock model instance for testing."""
    return MockModel()


@pytest.fixture
def sample_tool():
    """Simple test tool function."""

    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    return add_numbers


@pytest.fixture
def async_sample_tool():
    """Simple async test tool function."""

    async def async_add(x: int, y: int) -> int:
        """Async add two numbers."""
        await asyncio.sleep(0.01)
        return x + y

    return async_add


@pytest.fixture
def sample_tool_call():
    """Sample ToolCall object for testing."""
    return ToolCall(name="test_tool", args={"param": "value"}, id="test_call_123")


@pytest.fixture
def mcp_tool():
    """Mock MCP tool with _input_schema attribute."""

    def mcp_tool_func():
        """Mock MCP tool function."""
        return "mcp result"

    # Fix: input_schema should match the function signature (no parameters)
    mcp_tool_func._input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    return mcp_tool_func
