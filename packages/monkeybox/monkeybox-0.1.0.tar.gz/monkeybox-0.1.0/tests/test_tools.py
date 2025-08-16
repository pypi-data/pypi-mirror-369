"""Tests for the tools system."""

from typing import Optional, Union

import pytest

from monkeybox.core.exceptions import SchemaGenerationError, ToolValidationError
from monkeybox.core.tools import ToolCall, anthropic_tool_schema, openai_tool_schema


def test_schema_generation(sample_tool):
    """Function with type hints generates complete schema."""
    openai_schema = openai_tool_schema(sample_tool)
    anthropic_schema = anthropic_tool_schema(sample_tool)

    expected_openai_schema = {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two numbers together.",
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "a": {"type": "integer", "title": "A"},
                    "b": {"type": "integer", "title": "B"},
                },
                "required": ["a", "b"],
            },
        },
    }

    expected_anthropic_schema = {
        "name": "add_numbers",
        "description": "Add two numbers together.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "a": {"type": "integer", "title": "A"},
                "b": {"type": "integer", "title": "B"},
            },
            "required": ["a", "b"],
        },
    }

    assert openai_schema == expected_openai_schema
    assert anthropic_schema == expected_anthropic_schema


@pytest.mark.parametrize(
    "name,args,tool_id",
    [
        ("simple_tool", {}, "call_123"),
        ("complex_tool", {"param1": "value1", "param2": 42, "param3": [1, 2, 3]}, "call_456"),
        ("string_tool", {"text": "hello world"}, "call_789"),
        ("nested_tool", {"config": {"enabled": True, "count": 5}}, "call_abc"),
    ],
)
def test_tool_call_dataclass(name, args, tool_id):
    """ToolCall creates with various id/name/args combinations."""
    tool_call = ToolCall(name=name, args=args, id=tool_id)

    assert tool_call.name == name
    assert tool_call.args == args
    assert tool_call.id == tool_id


def test_mcp_tool_detection(mcp_tool):
    """MCP tool with _input_schema detected."""
    openai_schema = openai_tool_schema(mcp_tool)
    anthropic_schema = anthropic_tool_schema(mcp_tool)

    expected_openai_schema = {
        "type": "function",
        "function": {
            "name": "mcp_tool_func",
            "description": "Mock MCP tool function.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    expected_anthropic_schema = {
        "name": "mcp_tool_func",
        "description": "Mock MCP tool function.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    }

    assert openai_schema == expected_openai_schema
    assert anthropic_schema == expected_anthropic_schema


@pytest.mark.parametrize(
    "func_def,expected_properties,expected_required",
    [
        # Basic types
        (
            "def test_func(value: float) -> float: '''Test float.'''; return value * 2.0",
            {"value": {"type": "number", "title": "Value"}},
            ["value"],
        ),
        (
            "def test_func(flag: bool) -> bool: '''Test bool.'''; return not flag",
            {"flag": {"type": "boolean", "title": "Flag"}},
            ["flag"],
        ),
        (
            "def test_func(text: str) -> str: '''Test string.'''; return text.upper()",
            {"text": {"type": "string", "title": "Text"}},
            ["text"],
        ),
        (
            "def test_func(num: int) -> int: '''Test int.'''; return num * 2",
            {"num": {"type": "integer", "title": "Num"}},
            ["num"],
        ),
        # Complex types
        (
            "def test_func(items: list[int]) -> list[int]: '''Test list[int].'''; return [n * 2 for n in items]",
            {"items": {"type": "array", "items": {"type": "integer"}, "title": "Items"}},
            ["items"],
        ),
        (
            "def test_func(mapping: dict[str, str]) -> dict[str, str]: '''Test dict.'''; return {k: v.upper() for k, v in mapping.items()}",
            {
                "mapping": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "title": "Mapping",
                }
            },
            ["mapping"],
        ),
        # Union types
        (
            "def test_func(value: Union[str, int, float]) -> str: '''Test Union.'''; return str(value)",
            {
                "value": {
                    "anyOf": [{"type": "string"}, {"type": "integer"}, {"type": "number"}],
                    "title": "Value",
                }
            },
            ["value"],
        ),
        # Optional parameters
        (
            "def test_func(required: str, optional: int = 42) -> str: '''Test optional.'''; return f'{required}_{optional}'",
            {
                "required": {"type": "string", "title": "Required"},
                "optional": {"type": "integer", "title": "Optional", "default": 42},
            },
            ["required"],
        ),
        (
            "def test_func(query: str, limit: Optional[int] = None, flag: bool = False) -> list[str]: '''Test multiple optional.'''; return []",
            {
                "query": {"type": "string", "title": "Query"},
                "limit": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "title": "Limit",
                },
                "flag": {"type": "boolean", "default": False, "title": "Flag"},
            },
            ["query"],
        ),
        # No parameters
        ("def test_func() -> str: '''No params.'''; return '2024-01-01'", {}, []),
        # No type hints
        (
            "def test_func(a, b): '''No type hints.'''; return a + b",
            {"a": {"title": "A"}, "b": {"title": "B"}},
            ["a", "b"],
        ),
    ],
)
def test_function_schema_generation(func_def, expected_properties, expected_required):
    """Test schema generation for various function signatures."""
    # Execute the function definition to create the function
    local_vars = {}
    exec(func_def, {"List": list, "Dict": dict, "Union": Union, "Optional": Optional}, local_vars)
    test_func = local_vars["test_func"]

    openai_schema = openai_tool_schema(test_func)
    anthropic_schema = anthropic_tool_schema(test_func)

    # Check OpenAI schema structure
    assert openai_schema["type"] == "function"
    assert openai_schema["function"]["name"] == "test_func"

    params = openai_schema["function"]["parameters"]
    assert params["type"] == "object"
    assert params["properties"] == expected_properties

    # Handle required field - if empty, it might be missing or empty list
    if expected_required:
        assert params["required"] == expected_required
    else:
        # For functions with no parameters, required might be missing or empty
        assert params.get("required", []) == []

    # Check Anthropic schema matches
    assert anthropic_schema["name"] == "test_func"
    assert anthropic_schema["input_schema"]["properties"] == expected_properties
    if expected_required:
        assert anthropic_schema["input_schema"]["required"] == expected_required
    else:
        assert anthropic_schema["input_schema"].get("required", []) == []


@pytest.mark.parametrize(
    "mcp_schema,expected_name,expected_desc",
    [
        (
            {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            "mcp_search_tool",
            "Search using MCP tool.",
        ),
        (
            {
                "type": "object",
                "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["file_path", "content"],
            },
            "mcp_write_file",
            "Write file using MCP.",
        ),
        (
            {"type": "object", "properties": {}, "required": []},
            "mcp_simple_tool",
            "Simple MCP tool.",
        ),
    ],
)
def test_mcp_tool_schemas(mcp_schema, expected_name, expected_desc):
    """Test MCP tools with various schemas."""

    def mcp_tool():
        return "result"

    # Dynamically set the name, description, and schema
    mcp_tool.__name__ = expected_name
    mcp_tool.__doc__ = expected_desc
    mcp_tool._input_schema = mcp_schema

    openai_schema = openai_tool_schema(mcp_tool)
    anthropic_schema = anthropic_tool_schema(mcp_tool)

    expected_openai = {
        "type": "function",
        "function": {"name": expected_name, "description": expected_desc, "parameters": mcp_schema},
    }

    expected_anthropic = {
        "name": expected_name,
        "description": expected_desc,
        "input_schema": mcp_schema,
    }

    assert openai_schema == expected_openai
    assert anthropic_schema == expected_anthropic


@pytest.mark.parametrize(
    "docstring_setup,expected_description",
    [
        ("tool.__doc__ = None", None),  # Completely removed docstring
        ("tool.__doc__ = ''", ""),  # Empty string docstring
        ("tool.__doc__ = '   '", "   "),  # Whitespace-only docstring
        ("pass", "Test function."),  # Normal docstring (from function definition)
    ],
)
def test_docstring_handling(docstring_setup, expected_description):
    """Test how different docstring scenarios are handled."""

    def tool(value: str) -> str:
        """Test function."""
        return value

    # Apply the docstring modification
    if docstring_setup != "pass":
        exec(docstring_setup)

    openai_schema = openai_tool_schema(tool)
    anthropic_schema = anthropic_tool_schema(tool)

    assert openai_schema["function"]["description"] == expected_description
    assert anthropic_schema["description"] == expected_description


@pytest.mark.parametrize(
    "func_code,expected_structure_checks",
    [
        # Complex nested types
        (
            """
def test_func(
    data: dict[str, list[dict[str, Union[str, int]]]],
    options: Optional[dict[str, bool]] = None
) -> list[dict[str, object]]:
    '''Process nested data.'''
    return [{"processed": True}]
            """,
            {
                "has_data_param": True,
                "has_options_param": True,
                "data_is_object": True,
                "options_has_default": True,
                "required_params": ["data"],
            },
        ),
        # List and Dict combinations
        (
            """
def test_func(items: list[str], metadata: dict[str, Union[str, int]], count: int) -> dict[str, object]:
    '''Process data with complex types.'''
    return {"processed": len(items)}
            """,
            {
                "items_is_array": True,
                "items_type_is_string": True,
                "metadata_is_object": True,
                "metadata_has_anyof": True,
                "count_is_integer": True,
                "required_params": ["items", "metadata", "count"],
            },
        ),
    ],
)
def test_complex_type_structures(func_code, expected_structure_checks):
    """Test complex type combinations and their schema structures."""
    local_vars = {}
    exec(func_code, {"Dict": dict, "List": list, "Union": Union, "Optional": Optional}, local_vars)
    test_func = local_vars["test_func"]

    openai_schema = openai_tool_schema(test_func)
    params = openai_schema["function"]["parameters"]

    # Check expected structure properties
    if expected_structure_checks.get("has_data_param"):
        assert "data" in params["properties"]

    if expected_structure_checks.get("has_options_param"):
        assert "options" in params["properties"]

    if expected_structure_checks.get("data_is_object"):
        assert params["properties"]["data"]["type"] == "object"

    if expected_structure_checks.get("options_has_default"):
        assert params["properties"]["options"]["default"] is None

    if expected_structure_checks.get("items_is_array"):
        assert params["properties"]["items"]["type"] == "array"

    if expected_structure_checks.get("items_type_is_string"):
        assert params["properties"]["items"]["items"]["type"] == "string"

    if expected_structure_checks.get("metadata_is_object"):
        assert params["properties"]["metadata"]["type"] == "object"

    if expected_structure_checks.get("metadata_has_anyof"):
        assert "anyOf" in params["properties"]["metadata"]["additionalProperties"]

    if expected_structure_checks.get("count_is_integer"):
        assert params["properties"]["count"]["type"] == "integer"

    # Check required parameters
    if "required_params" in expected_structure_checks:
        assert set(params["required"]) == set(expected_structure_checks["required_params"])


def test_tool_validation_errors():
    """Test that non-callable objects raise ToolValidationError."""
    # Test non-callable string - this will fail on name validation first
    with pytest.raises(ToolValidationError, match="Tool must have a valid __name__ attribute"):
        openai_tool_schema("not a function")

    # Test non-callable number - this will fail on name validation first
    with pytest.raises(ToolValidationError, match="Tool must have a valid __name__ attribute"):
        anthropic_tool_schema(123)


def test_tool_no_name_validation():
    """Test that tools without proper names raise ToolValidationError."""

    # Lambda functions
    def lambda_func(x):
        return x

    lambda_func.__name__ = "<lambda>"
    with pytest.raises(ToolValidationError, match="Tool must have a valid __name__ attribute"):
        openai_tool_schema(lambda_func)

    with pytest.raises(ToolValidationError, match="Tool must have a valid __name__ attribute"):
        anthropic_tool_schema(lambda_func)


def test_invalid_mcp_schema():
    """Test validation of MCP tools with invalid schemas."""

    def mock_mcp_tool():
        pass

    # Invalid schema type (not dict)
    mock_mcp_tool._input_schema = "not a dict"

    with pytest.raises(ToolValidationError, match="invalid _input_schema: expected dict"):
        openai_tool_schema(mock_mcp_tool)

    with pytest.raises(ToolValidationError, match="invalid _input_schema: expected dict"):
        anthropic_tool_schema(mock_mcp_tool)


def test_schema_generation_error():
    """Test that schema generation errors are properly wrapped."""

    # Create a function that will cause TypeAdapter to fail
    class UnserializableType:
        pass

    def bad_func(arg: UnserializableType) -> None:
        pass

    # This should raise SchemaGenerationError
    with pytest.raises(SchemaGenerationError) as exc_info:
        openai_tool_schema(bad_func)

    assert exc_info.value.func_name == "bad_func"
    assert exc_info.value.error is not None
