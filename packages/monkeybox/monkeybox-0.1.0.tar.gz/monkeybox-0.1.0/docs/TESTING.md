# Testing Guide

This document covers the comprehensive testing approach used in the Monkeybox framework.

## Test Suite Overview

The framework has a comprehensive test suite across well-organized test files achieving **90%+ code coverage** with efficient, maintainable tests.

### Test Structure
```
tests/
├── __init__.py
├── conftest.py                      # Shared fixtures and mocks
├── test_agent.py                    # Agent core functionality with edge cases
├── test_base_model.py               # Abstract interface validation
├── test_models.py                   # OpenAI/Anthropic implementations
├── test_tools.py                    # Tool system & schema generation
├── test_logger.py                   # Rich logging functionality
├── test_mcp_client.py               # MCP client tests
├── test_mcp_error_handling.py       # MCP error handling and timeouts
├── test_mcp_content_handling.py     # MCP content processing edge cases
├── test_exceptions.py               # Custom exception hierarchy tests
└── test_integration.py              # Component interaction tests
```

## Testing Philosophy

Our testing approach follows these principles:

1. **Minimal Mocking**: We prefer testing real behavior over implementation details. Mocks are used only when necessary (external APIs, I/O operations).

2. **Comprehensive Coverage**: Every component must maintain 90%+ test coverage. Pre-commit hooks enforce this requirement.

3. **Test Categories**:
   - **Unit Tests**: Test individual components in isolation
   - **Integration Tests**: Test interactions between components
   - **Edge Case Tests**: Test boundary conditions and error scenarios

4. **Clear Documentation**: Each test has detailed docstrings explaining:
   - What is being tested
   - Why it matters
   - What specific behaviors are verified

5. **Fast Execution**: All tests run in <1 second by avoiding real I/O and API calls

## Testing Commands

```bash
# Run full test suite with coverage enforcement
uv run pytest --cov=src/monkeybox --cov-fail-under=90

# Generate detailed HTML coverage report
uv run pytest --cov=src/monkeybox --cov-report=html

# Run specific test categories
uv run pytest tests/test_agent.py -v
uv run pytest tests/test_mcp_comprehensive.py -v

# Run integration test
uv run python examples/showcase_example.py
```

## Coverage Requirements
- **Minimum Coverage**: 90% (enforced by pytest-cov)
- **Pre-commit Integration**: Coverage check runs automatically on commits
- **Current Coverage**: 94.37% across all components
- **Per-module Coverage**: Agent (97%), Models (93-96%), Logger (96%), Tools (100%), MCP Client (91%)

## Testing Best Practices

### 1. Test Naming Convention
```python
# Good: Descriptive and specific
test_agent_handles_concurrent_tool_execution()
test_anthropic_system_message_extraction()

# Bad: Vague or generic
test_agent_works()
test_error()
```

### 2. Mock Usage Guidelines
```python
# Good: Mock only external dependencies
with patch("monkeybox.core.openai_model.AsyncOpenAI"):
    model = OpenAIModel("gpt-4")

# Bad: Over-mocking implementation details
with patch("monkeybox.core.agent.Agent._process_tools"):
    # This tests mocks, not real behavior
```

### 3. Assertion Patterns
```python
# Good: Test behavior, not implementation
assert result == "Expected output"
assert "error" in result.lower()

# Bad: Testing internal state
assert agent._internal_var == some_value
```

## Adding New Tests

When adding features:
1. **Write tests first** (TDD approach)
2. **Target 90%+ coverage** for new code
3. **Include edge cases** and error scenarios
4. **Document complex tests** with detailed docstrings
5. **Run full test suite** before committing

## Test Organization

- **Unit Tests**: One test file per module (e.g., `test_agent.py` for `agent.py`)
- **Integration Tests**: Separate `test_integration.py` for cross-component tests
- **Fixtures**: Shared test utilities in `conftest.py`
- **Performance**: Keep tests fast by avoiding real I/O

## Common Test Patterns

### Testing Async Functions
```python
@pytest.mark.asyncio
async def test_async_tool_execution():
    """Test that async tools are executed correctly."""
    async def async_tool(x: int) -> int:
        await asyncio.sleep(0.01)
        return x * 2

    agent = Agent(model, "Test", tools=[async_tool])
    # Test implementation
```

### Testing Exception Handling
```python
def test_tool_not_found_error():
    """Test proper exception when tool is not found."""
    with pytest.raises(ToolNotFoundError) as exc_info:
        agent._execute_tool("nonexistent", {})

    assert exc_info.value.tool_name == "nonexistent"
    assert "available_tool" in exc_info.value.available_tools
```

### Testing with Mocked APIs
```python
@patch("monkeybox.core.openai_model.AsyncOpenAI")
def test_openai_api_call(mock_client):
    """Test OpenAI API interaction."""
    mock_response = create_mock_response()
    mock_client.return_value.chat.completions.create.return_value = mock_response

    model = OpenAIModel("gpt-4")
    # Test implementation
```

## Debugging Tests

- Use `-v` flag for verbose output
- Use `-s` flag to see print statements
- Use `--pdb` to drop into debugger on failures
- Review test logs for unexpected behavior
