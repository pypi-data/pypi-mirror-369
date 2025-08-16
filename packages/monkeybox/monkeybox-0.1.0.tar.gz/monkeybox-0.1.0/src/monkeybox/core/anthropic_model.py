"""Anthropic model implementation."""

from collections.abc import Callable

from anthropic import APIError, APITimeoutError, AsyncAnthropic, AuthenticationError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .base_model import BaseModel, ChatResponse
from .exceptions import ModelCommunicationError, ModelResponseError
from .logger import MonkeyboxLogger
from .tools import ToolCall, anthropic_tool_schema


class AnthropicModel(BaseModel):
    """Anthropic model implementation using native SDK."""

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        reasoning: bool = False,
        timeout: float | None = None,
    ):
        super().__init__(model_name)
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout)
        self.reasoning = reasoning
        self.logger = MonkeyboxLogger("anthropic")

    @retry(
        retry=retry_if_exception_type((RateLimitError, APITimeoutError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(3),
    )
    async def _create_message(self, **kwargs):
        """Create message with retry logic for rate limits and timeouts."""
        return await self.client.messages.create(**kwargs)

    async def chat(
        self,
        messages: list[dict[str, object]],
        tools: list[Callable] | None = None,
        **kwargs,
    ) -> ChatResponse:
        """Send messages to the model and get a response."""
        # Safely extract system message
        system_message = None
        if messages and messages[0].get("role") == "system":
            system_message = messages[0]["content"]
            messages = messages[1:]
        elif not messages:
            raise ModelResponseError(self.model_name, "No messages provided to chat")

        max_tokens = kwargs.get("max_tokens", 4096)
        completion_args = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            **kwargs,
        }

        if system_message:
            completion_args["system"] = system_message

        if tools:
            completion_args["tools"] = self.format_tools_for_api(tools)

        if self.reasoning:
            budget_tokens = kwargs.get("budget_tokens", int(max_tokens * 0.85))
            if budget_tokens > max_tokens:
                budget_tokens = int(max_tokens * 0.85)
            completion_args["thinking"] = {
                "type": "enabled",
                "budget_tokens": budget_tokens,
            }

        try:
            response = await self._create_message(**completion_args)
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
        if not response.content:
            raise ModelResponseError(self.model_name, "Empty response content")

        text = None
        tool_calls = []
        thinking = None

        for block in response.content:
            if hasattr(block, "type"):
                if block.type == "text":
                    text = getattr(block, "text", None)
                elif block.type == "tool_use":
                    if hasattr(block, "name") and hasattr(block, "input") and hasattr(block, "id"):
                        tool_calls.append(
                            ToolCall(
                                name=block.name,
                                args=block.input,
                                id=block.id,
                            ),
                        )
                elif block.type == "thinking":
                    thinking = getattr(block, "thinking", None)
            else:
                # Log unknown block type but continue
                self.logger.log_mcp_warning(
                    "AnthropicModel",
                    f"Unknown content block type in response: {type(block)}",
                )

        return ChatResponse(
            message={"role": "assistant", "content": response.content},
            text=text,
            tool_calls=tool_calls,
            thinking=thinking,
        )

    def format_tools_for_api(self, tools: list[Callable]) -> list[dict[str, object]]:
        formatted_tools = []
        for tool in tools:
            try:
                schema = anthropic_tool_schema(tool)
                formatted_tools.append(schema)
            except Exception as e:
                # Log error but continue with other tools
                tool_name = getattr(tool, "__name__", "unknown")
                self.logger.log_mcp_warning(
                    "AnthropicModel",
                    f"Failed to generate schema for tool {tool_name}: {e}",
                )
        return formatted_tools

    def format_tool_results(self, tool_results: list[dict[str, object]]) -> dict[str, object]:
        """Format tool results for Anthropic - all results in one user message."""
        formatted_results = []
        for result in tool_results:
            formatted_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": result["tool_call_id"],
                    "content": str(result["content"]),
                },
            )
        return {"role": "user", "content": formatted_results}
