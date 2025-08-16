"""OpenAI model implementation."""

import json
from collections.abc import Callable

from openai import APIError, APITimeoutError, AsyncOpenAI, AuthenticationError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .base_model import BaseModel, ChatResponse
from .exceptions import ModelCommunicationError, ModelResponseError
from .logger import MonkeyboxLogger
from .tools import ToolCall, openai_tool_schema


class OpenAIModel(BaseModel):
    """OpenAI model implementation using the native OpenAI SDK.

    This class provides a concrete implementation of the BaseModel interface
    for OpenAI's language models, including GPT-4, GPT-3.5, and O1 series models.
    It handles message formatting, tool integration, and response parsing according
    to OpenAI's API specifications.

    Attributes:
        client: The AsyncOpenAI client instance for API communication.
        reasoning: Whether to enable reasoning mode for O1 models.

    """

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        base_url: str | None = None,
        reasoning: bool = False,
        timeout: float | None = None,
    ) -> None:
        """Initialize the OpenAI model.

        Args:
            model_name: The name of the OpenAI model to use (e.g., "gpt-4", "gpt-3.5-turbo").
            api_key: Optional API key for authentication. If not provided, uses the
                    OPENAI_API_KEY environment variable.
            base_url: Optional custom base URL for API requests. Useful for proxy
                     or alternative endpoints.
            reasoning: Whether to enable reasoning mode for O1 series models.
            timeout: Optional timeout in seconds for API requests. Defaults to 10 minutes.

        """
        super().__init__(model_name)
        self.client: AsyncOpenAI = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.reasoning: bool = reasoning
        self.logger = MonkeyboxLogger("openai")

    @retry(
        retry=retry_if_exception_type((RateLimitError, APITimeoutError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(3),
    )
    async def _create_chat_completion(self, **kwargs):
        """Create chat completion with retry logic for rate limits and timeouts."""
        return await self.client.chat.completions.create(**kwargs)

    async def chat(
        self,
        messages: list[dict[str, object]],
        tools: list[Callable] | None = None,
        **kwargs,
    ) -> ChatResponse:
        """Send messages to the model and get a response."""
        completion_args = {"model": self.model_name, "messages": messages, **kwargs}

        if tools:
            completion_args["tools"] = self.format_tools_for_api(tools)

        if self.reasoning:
            completion_args["reasoning_effort"] = kwargs.get("reasoning_effort", "medium")

        try:
            response = await self._create_chat_completion(**completion_args)
        except AuthenticationError as e:
            # Authentication errors should not be retried
            raise ModelCommunicationError(
                self.model_name,
                Exception(f"Authentication failed: {e}. Check your API key."),
            )
        except APIError as e:
            # All other API errors wrapped in ModelCommunicationError
            raise ModelCommunicationError(self.model_name, e)

        # Validate response structure
        if not response.choices:
            raise ModelResponseError(self.model_name, "No choices in response")

        message = response.choices[0].message
        content = message.content
        tool_calls = []

        if message.tool_calls:
            for tool in message.tool_calls:
                try:
                    args = json.loads(tool.function.arguments)
                except json.JSONDecodeError as e:
                    raise ModelResponseError(
                        self.model_name,
                        f"Invalid JSON in tool arguments for {tool.function.name}: {e}",
                    )

                tool_calls.append(
                    ToolCall(
                        name=tool.function.name,
                        args=args,
                        id=tool.id,
                    ),
                )

        message_dict = message.model_dump()

        return ChatResponse(
            message=message_dict,
            text=content,
            tool_calls=tool_calls,
            thinking=None,
        )

    def format_tools_for_api(self, tools: list[Callable]) -> list[dict[str, object]]:
        formatted_tools = []
        for tool in tools:
            try:
                schema = openai_tool_schema(tool)
                formatted_tools.append(schema)
            except Exception as e:
                # Log error but continue with other tools
                tool_name = getattr(tool, "__name__", "unknown")
                self.logger.log_mcp_warning(
                    "OpenAIModel",
                    f"Failed to generate schema for tool {tool_name}: {e}",
                )
        return formatted_tools

    def format_tool_results(self, tool_results: list[dict[str, object]]) -> list[dict[str, object]]:
        """Format tool results for OpenAI - each result is a separate message."""
        messages = []
        for result in tool_results:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": str(result["content"]),
                },
            )
        return messages
