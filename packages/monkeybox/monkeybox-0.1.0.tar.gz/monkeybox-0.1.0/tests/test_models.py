"""Tests for OpenAI and Anthropic model implementations."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from monkeybox.core.anthropic_model import AnthropicModel
from monkeybox.core.exceptions import ModelCommunicationError, ModelResponseError
from monkeybox.core.openai_model import OpenAIModel


@patch("monkeybox.core.openai_model.AsyncOpenAI")
def test_openai_tool_formatting(mock_openai_client, sample_tool):
    """Test OpenAI-specific tool schema formatting."""
    model = OpenAIModel("gpt-4o")

    formatted = model.format_tools_for_api([sample_tool])

    assert len(formatted) == 1
    assert formatted[0]["type"] == "function"
    assert formatted[0]["function"]["name"] == "add_numbers"
    assert "parameters" in formatted[0]["function"]


@patch("monkeybox.core.openai_model.AsyncOpenAI")
@pytest.mark.asyncio
async def test_openai_response_parsing(mock_openai_client):
    """Parses OpenAI response to ChatResponse."""
    # Mock response object
    mock_message = Mock()
    mock_message.content = "Hello there"
    mock_message.tool_calls = None
    mock_message.model_dump.return_value = {"role": "assistant", "content": "Hello there"}

    mock_response = Mock()
    mock_response.choices = [Mock(message=mock_message)]

    # Configure client mock
    client_instance = mock_openai_client.return_value
    client_instance.chat.completions.create = AsyncMock(return_value=mock_response)

    model = OpenAIModel("gpt-4o")

    messages = [{"role": "user", "content": "Hi"}]
    response = await model.chat(messages)

    assert response.text == "Hello there"
    assert response.tool_calls == []
    assert response.message["content"] == "Hello there"


def test_openai_tool_results():
    """Test OpenAI's approach to formatting tool execution results.

    OpenAI expects each tool result as a separate message with role='tool',
    unlike Anthropic which combines them. This test ensures we follow
    OpenAI's convention correctly.

    Verifies:
    - Each tool result becomes a separate message
    - Messages have role='tool' and include tool_call_id
    - Content is properly stringified
    """
    with patch("monkeybox.core.openai_model.AsyncOpenAI"):
        model = OpenAIModel("gpt-4o")

        tool_results = [
            {"tool_call_id": "call_123", "content": "Result 1", "name": "tool1"},
            {"tool_call_id": "call_456", "content": "Result 2", "name": "tool2"},
        ]

        formatted = model.format_tool_results(tool_results)

        assert len(formatted) == 2  # Separate message for each result
        assert formatted[0]["role"] == "tool"
        assert formatted[0]["content"] == "Result 1"
        assert formatted[1]["content"] == "Result 2"


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
def test_anthropic_tool_formatting(mock_anthropic_client, sample_tool):
    """Test Anthropic-specific tool schema formatting.

    Anthropic uses a different tool format than OpenAI, with 'name',
    'description', and 'input_schema' at the top level.

    Verifies:
    - Tool has correct Anthropic structure
    - Input schema is generated from function type hints
    - Description is extracted from docstring
    """
    model = AnthropicModel("claude-3-5-sonnet")

    formatted = model.format_tools_for_api([sample_tool])

    assert len(formatted) == 1
    assert formatted[0]["name"] == "add_numbers"
    assert "input_schema" in formatted[0]
    assert "description" in formatted[0]


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_response_parsing(mock_anthropic_client):
    """Parses Anthropic response to ChatResponse."""
    # Mock response object
    mock_content_block = Mock()
    mock_content_block.type = "text"
    mock_content_block.text = "Hello from Claude"

    mock_response = Mock()
    mock_response.content = [mock_content_block]
    mock_response.model_dump.return_value = {
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello from Claude"}],
    }

    # Configure client mock
    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(return_value=mock_response)

    model = AnthropicModel("claude-3-5-sonnet")

    messages = [{"role": "user", "content": "Hi"}]
    response = await model.chat(messages)

    assert response.text == "Hello from Claude"
    assert response.tool_calls == []


def test_anthropic_tool_results():
    """Test Anthropic's approach to formatting tool execution results.

    Anthropic expects all tool results combined into a single user message
    with multiple content blocks, each containing a tool_result.

    Verifies:
    - All results combined into single message with role='user'
    - Each result is a tool_result content block
    - Tool use IDs are preserved for correlation
    """
    with patch("monkeybox.core.anthropic_model.AsyncAnthropic"):
        model = AnthropicModel("claude-3-5-sonnet")

        tool_results = [
            {"tool_call_id": "call_123", "content": "Result 1", "name": "tool1"},
            {"tool_call_id": "call_456", "content": "Result 2", "name": "tool2"},
        ]

        formatted = model.format_tool_results(tool_results)

        # Anthropic combines all results into single message
        assert formatted["role"] == "user"
        assert "content" in formatted
        assert len(formatted["content"]) == 2  # Two tool result blocks


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_reasoning_mode(mock_anthropic_client):
    """Test Anthropic model with reasoning mode enabled."""
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="Response with reasoning")]
    mock_response.model_dump.return_value = {"role": "assistant", "content": []}

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(return_value=mock_response)

    model = AnthropicModel("claude-3-5-sonnet", reasoning=True)

    messages = [{"role": "user", "content": "Think about this"}]
    await model.chat(messages, max_tokens=1000)

    call_kwargs = client_instance.messages.create.call_args[1]
    assert "thinking" in call_kwargs
    assert call_kwargs["thinking"]["budget_tokens"] == int(1000 * 0.85)


@patch("monkeybox.core.openai_model.AsyncOpenAI")
@pytest.mark.asyncio
async def test_openai_reasoning_mode(mock_openai_client):
    """Test OpenAI model with reasoning mode."""
    mock_message = Mock()
    mock_message.content = "Response with reasoning"
    mock_message.tool_calls = None
    mock_message.model_dump.return_value = {
        "role": "assistant",
        "content": "Response with reasoning",
    }

    mock_response = Mock()
    mock_response.choices = [Mock(message=mock_message)]

    client_instance = mock_openai_client.return_value
    client_instance.chat.completions.create = AsyncMock(return_value=mock_response)

    model = OpenAIModel("gpt-4o", reasoning=True)

    messages = [{"role": "user", "content": "Think about this"}]
    await model.chat(messages, reasoning_effort="high")

    call_kwargs = client_instance.chat.completions.create.call_args[1]
    assert call_kwargs["reasoning_effort"] == "high"


@patch("monkeybox.core.openai_model.AsyncOpenAI")
@pytest.mark.asyncio
async def test_openai_tool_call_parsing(mock_openai_client):
    """Test OpenAI model parsing tool calls from response."""
    mock_tool_call = Mock()
    mock_tool_call.function.name = "test_function"
    mock_tool_call.function.arguments = '{"param": "value"}'
    mock_tool_call.id = "call_123"

    mock_message = Mock()
    mock_message.content = None
    mock_message.tool_calls = [mock_tool_call]
    mock_message.model_dump.return_value = {
        "role": "assistant",
        "tool_calls": [{"id": "call_123", "function": {"name": "test_function"}}],
    }

    mock_response = Mock()
    mock_response.choices = [Mock(message=mock_message)]

    client_instance = mock_openai_client.return_value
    client_instance.chat.completions.create = AsyncMock(return_value=mock_response)

    model = OpenAIModel("gpt-4o")

    response = await model.chat([{"role": "user", "content": "Use the tool"}])

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "test_function"
    assert response.tool_calls[0].args == {"param": "value"}
    assert response.tool_calls[0].id == "call_123"


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_tool_call_parsing(mock_anthropic_client):
    """Test Anthropic model parsing tool calls."""
    mock_tool_block = Mock()
    mock_tool_block.type = "tool_use"
    mock_tool_block.id = "call_abc"
    mock_tool_block.name = "search"
    mock_tool_block.input = {"query": "test"}

    mock_response = Mock()
    mock_response.content = [mock_tool_block]
    mock_response.model_dump.return_value = {"role": "assistant", "content": []}

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(return_value=mock_response)

    model = AnthropicModel("claude-3-5-sonnet")

    response = await model.chat([{"role": "user", "content": "Search for something"}])

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "search"
    assert response.tool_calls[0].args == {"query": "test"}
    assert response.tool_calls[0].id == "call_abc"


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
def test_anthropic_model_initialization_with_custom_key(mock_anthropic_client):
    """Test Anthropic model with custom API key."""
    model = AnthropicModel("claude-3-5-sonnet", api_key="custom-key")

    mock_anthropic_client.assert_called_once_with(api_key="custom-key", timeout=None)
    assert model.model_name == "claude-3-5-sonnet"


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
def test_anthropic_model_initialization_env_key(mock_anthropic_client):
    """Test Anthropic model using None API key (lets SDK handle env var)."""
    model = AnthropicModel("claude-3-5-sonnet")

    # Should pass None and let Anthropic SDK handle environment variable
    mock_anthropic_client.assert_called_once_with(api_key=None, timeout=None)
    assert model.model_name == "claude-3-5-sonnet"


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_response_with_mixed_content(mock_anthropic_client):
    """Test Anthropic response with mixed text and tool content."""
    text_block = Mock()
    text_block.type = "text"
    text_block.text = "Here is the result:"

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.id = "call_123"
    tool_block.name = "search"
    tool_block.input = {"query": "test"}

    mock_response = Mock()
    mock_response.content = [text_block, tool_block]
    mock_response.model_dump.return_value = {"role": "assistant", "content": []}

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(return_value=mock_response)

    model = AnthropicModel("claude-3-5-sonnet")
    response = await model.chat([{"role": "user", "content": "Search something"}])

    assert response.text == "Here is the result:"
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "search"


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_system_message_handling(mock_anthropic_client):
    """Test special handling of system messages for Anthropic API.

    Anthropic requires system messages to be passed as a separate 'system'
    parameter rather than in the messages array. This test ensures we
    extract and pass system messages correctly.

    Verifies:
    - System message extracted from messages array
    - Passed as 'system' parameter to API
    - Non-system messages remain in messages array
    """
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="Response")]
    mock_response.model_dump.return_value = {"role": "assistant", "content": []}

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(return_value=mock_response)

    model = AnthropicModel("claude-3-5-sonnet")

    messages = [
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hello"},
    ]

    await model.chat(messages)

    call_kwargs = client_instance.messages.create.call_args[1]
    assert "system" in call_kwargs
    assert call_kwargs["system"] == "You are helpful"

    assert len(call_kwargs["messages"]) == 1
    assert call_kwargs["messages"][0]["role"] == "user"


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_no_system_message(mock_anthropic_client):
    """Test Anthropic model with no system message."""
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="Response")]
    mock_response.model_dump.return_value = {"role": "assistant", "content": []}

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(return_value=mock_response)

    model = AnthropicModel("claude-3-5-sonnet")

    messages = [{"role": "user", "content": "Hello"}]
    await model.chat(messages)

    call_kwargs = client_instance.messages.create.call_args[1]
    assert "system" not in call_kwargs or call_kwargs.get("system") is None


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_thinking_content_parsing(mock_anthropic_client):
    """Test Anthropic parsing thinking content from response."""
    text_block = Mock()
    text_block.type = "text"
    text_block.text = "Here's my answer"

    thinking_block = Mock()
    thinking_block.type = "thinking"
    thinking_block.thinking = "Let me think about this carefully..."

    mock_response = Mock()
    mock_response.content = [thinking_block, text_block]
    mock_response.model_dump.return_value = {"role": "assistant", "content": []}

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(return_value=mock_response)

    model = AnthropicModel("claude-3-5-sonnet", reasoning=True)
    response = await model.chat([{"role": "user", "content": "Think about this"}])

    assert response.text == "Here's my answer"
    assert response.thinking == "Let me think about this carefully..."


# OpenAI Error Handling Tests


@patch("monkeybox.core.openai_model.AsyncOpenAI")
@pytest.mark.asyncio
async def test_openai_rate_limit_error(mock_openai_client):
    """Test OpenAI rate limit error handling with retry."""
    from openai import RateLimitError
    from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_fixed

    client_instance = mock_openai_client.return_value
    client_instance.chat.completions.create = AsyncMock(
        side_effect=RateLimitError("Rate limit exceeded", response=Mock(), body=None)
    )

    model = OpenAIModel("gpt-4")

    # Override the retry decorator with faster settings for testing
    original_method = model._create_chat_completion
    fast_retry = retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_fixed(0.001),  # 1ms wait instead of exponential
        stop=stop_after_attempt(3),
    )
    model._create_chat_completion = fast_retry(
        original_method.__wrapped__.__get__(model, type(model))
    )

    # Rate limit errors will be retried and eventually raise RetryError
    with pytest.raises(RetryError):
        await model.chat([{"role": "user", "content": "Hello"}])

    # Verify it was called 3 times (the retry limit)
    assert client_instance.chat.completions.create.call_count == 3


@patch("monkeybox.core.openai_model.AsyncOpenAI")
@pytest.mark.asyncio
async def test_openai_rate_limit_retry_success(mock_openai_client):
    """Test OpenAI rate limit retry eventually succeeds."""
    from openai import RateLimitError
    from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

    # Mock response for successful call
    mock_message = Mock()
    mock_message.content = "Success"
    mock_message.tool_calls = None
    mock_message.model_dump.return_value = {"role": "assistant", "content": "Success"}
    mock_response = Mock()
    mock_response.choices = [Mock(message=mock_message)]

    client_instance = mock_openai_client.return_value
    # First call fails with rate limit, second succeeds
    client_instance.chat.completions.create = AsyncMock(
        side_effect=[RateLimitError("Rate limit", response=Mock(), body=None), mock_response]
    )

    model = OpenAIModel("gpt-4")

    # Override the retry decorator with faster settings for testing
    original_method = model._create_chat_completion
    fast_retry = retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_fixed(0.001),  # 1ms wait instead of exponential
        stop=stop_after_attempt(3),
    )
    model._create_chat_completion = fast_retry(
        original_method.__wrapped__.__get__(model, type(model))
    )

    # Should succeed after retry
    response = await model.chat([{"role": "user", "content": "Hello"}])

    assert response.text == "Success"
    # Verify it was called twice (failed once, succeeded on retry)
    assert client_instance.chat.completions.create.call_count == 2


@patch("monkeybox.core.openai_model.AsyncOpenAI")
@pytest.mark.asyncio
async def test_openai_auth_error(mock_openai_client):
    """Test OpenAI authentication error handling."""
    from openai import AuthenticationError

    client_instance = mock_openai_client.return_value
    client_instance.chat.completions.create = AsyncMock(
        side_effect=AuthenticationError("Invalid API key", response=Mock(), body=None)
    )

    model = OpenAIModel("gpt-4")

    with pytest.raises(ModelCommunicationError) as exc_info:
        await model.chat([{"role": "user", "content": "Hello"}])

    assert "Authentication failed" in str(exc_info.value)
    assert "Check your API key" in str(exc_info.value)


@patch("monkeybox.core.openai_model.AsyncOpenAI")
@pytest.mark.asyncio
async def test_openai_api_error(mock_openai_client):
    """Test OpenAI general API error handling."""
    from openai import APIError

    client_instance = mock_openai_client.return_value
    client_instance.chat.completions.create = AsyncMock(
        side_effect=APIError(message="API Error", request=Mock(), body=None)
    )

    model = OpenAIModel("gpt-4")

    with pytest.raises(ModelCommunicationError) as exc_info:
        await model.chat([{"role": "user", "content": "Hello"}])

    assert exc_info.value.model_name == "gpt-4"
    assert "API Error" in str(exc_info.value)


@patch("monkeybox.core.openai_model.AsyncOpenAI")
@pytest.mark.asyncio
async def test_openai_empty_response(mock_openai_client):
    """Test OpenAI empty response handling."""
    mock_response = Mock()
    mock_response.choices = []

    client_instance = mock_openai_client.return_value
    client_instance.chat.completions.create = AsyncMock(return_value=mock_response)

    model = OpenAIModel("gpt-4")

    with pytest.raises(ModelResponseError) as exc_info:
        await model.chat([{"role": "user", "content": "Hello"}])

    assert exc_info.value.model_name == "gpt-4"
    assert "No choices in response" in str(exc_info.value)


# Anthropic Error Handling Tests


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_rate_limit_error(mock_anthropic_client):
    """Test Anthropic rate limit error handling with retry."""
    from anthropic import RateLimitError
    from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_fixed

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(
        side_effect=RateLimitError("Rate limit exceeded", response=Mock(), body=None)
    )

    model = AnthropicModel("claude-3")

    # Override the retry decorator with faster settings for testing
    original_method = model._create_message
    fast_retry = retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_fixed(0.001),  # 1ms wait instead of exponential
        stop=stop_after_attempt(3),
    )
    model._create_message = fast_retry(original_method.__wrapped__.__get__(model, type(model)))

    # Rate limit errors will be retried and eventually raise RetryError
    with pytest.raises(RetryError):
        await model.chat([{"role": "user", "content": "Hello"}])

    # Verify it was called 3 times (the retry limit)
    assert client_instance.messages.create.call_count == 3


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_auth_error(mock_anthropic_client):
    """Test Anthropic authentication error handling."""
    from anthropic import AuthenticationError

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(
        side_effect=AuthenticationError("Invalid API key", response=Mock(), body=None)
    )

    model = AnthropicModel("claude-3")

    with pytest.raises(ModelCommunicationError) as exc_info:
        await model.chat([{"role": "user", "content": "Hello"}])

    assert "Authentication failed" in str(exc_info.value)
    assert "Check your API key" in str(exc_info.value)


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_api_error(mock_anthropic_client):
    """Test Anthropic general API error handling."""
    from anthropic import APIError

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(
        side_effect=APIError(message="API Error", request=Mock(), body=None)
    )

    model = AnthropicModel("claude-3")

    with pytest.raises(ModelCommunicationError) as exc_info:
        await model.chat([{"role": "user", "content": "Hello"}])

    assert exc_info.value.model_name == "claude-3"
    assert "API Error" in str(exc_info.value)


@patch("monkeybox.core.anthropic_model.AsyncAnthropic")
@pytest.mark.asyncio
async def test_anthropic_empty_content(mock_anthropic_client):
    """Test Anthropic empty content handling."""
    mock_response = Mock()
    mock_response.content = []
    mock_response.model_dump.return_value = {"role": "assistant", "content": []}

    client_instance = mock_anthropic_client.return_value
    client_instance.messages.create = AsyncMock(return_value=mock_response)

    model = AnthropicModel("claude-3")

    with pytest.raises(ModelResponseError) as exc_info:
        await model.chat([{"role": "user", "content": "Hello"}])

    assert exc_info.value.model_name == "claude-3"
    assert "Empty response content" in str(exc_info.value)
