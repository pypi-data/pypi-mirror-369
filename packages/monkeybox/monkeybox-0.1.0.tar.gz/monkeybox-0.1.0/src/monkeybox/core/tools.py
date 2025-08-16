"""Tool-related utilities for agent framework."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from pydantic import TypeAdapter

from .exceptions import SchemaGenerationError, ToolValidationError


@dataclass
class ToolCall:
    """Represents a tool call request from an LLM."""

    name: str
    args: dict[str, object]
    id: str


def _extract_function_schema(func: Callable) -> dict[str, object]:
    """Extract schema from function, handling both regular functions and MCPToolWrapper."""
    # Validate input is callable
    if not callable(func):
        raise ToolValidationError(f"Expected callable, got {type(func).__name__}")

    # Check for MCP tool with pre-existing schema
    if hasattr(func, "_input_schema"):
        schema = func._input_schema
        if not isinstance(schema, dict):
            raise ToolValidationError(
                f"Tool {getattr(func, '__name__', 'unknown')} has invalid _input_schema: expected dict, got {type(schema).__name__}",
            )
        return cast("dict[str, object]", schema)
    # Generate schema from function signature
    func_name = getattr(func, "__name__", "<unknown>")
    try:
        return TypeAdapter(func).json_schema()
    except Exception as e:
        raise SchemaGenerationError(func_name, e)


def openai_tool_schema(func: Callable) -> dict[str, object]:
    """Generate OpenAI-compatible tool schema from a function."""
    # Validate function name
    func_name = getattr(func, "__name__", None)
    if not func_name or func_name == "<lambda>":
        raise ToolValidationError(f"Tool must have a valid __name__ attribute, got: {func_name}")

    try:
        schema = _extract_function_schema(func)
    except (SchemaGenerationError, ToolValidationError):
        raise  # Re-raise our custom exceptions
    except Exception as e:
        raise SchemaGenerationError(func_name, e)

    return {
        "type": "function",
        "function": {
            "name": func_name,
            "description": getattr(func, "__doc__", ""),
            "parameters": schema,
        },
    }


def anthropic_tool_schema(func: Callable) -> dict[str, object]:
    """Generate Anthropic-compatible tool schema from a function."""
    # Validate function name
    func_name = getattr(func, "__name__", None)
    if not func_name or func_name == "<lambda>":
        raise ToolValidationError(f"Tool must have a valid __name__ attribute, got: {func_name}")

    try:
        schema = _extract_function_schema(func)
    except (SchemaGenerationError, ToolValidationError):
        raise  # Re-raise our custom exceptions
    except Exception as e:
        raise SchemaGenerationError(func_name, e)

    return {
        "name": func_name,
        "description": getattr(func, "__doc__", ""),
        "input_schema": schema,
    }
