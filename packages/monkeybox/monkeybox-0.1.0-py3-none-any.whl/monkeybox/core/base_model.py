"""Base model class for all LLM providers."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

from .tools import ToolCall


@dataclass
class ChatResponse:
    """Response from a chat completion.

    Attributes:
        message: The full message object to append to history
        text: The text content if any (can be None if only tool calls)
        tool_calls: List of tool calls if any
        thinking: The thinking/reasoning content if any (provider-specific)

    """

    message: dict[str, object]
    text: str | None
    tool_calls: list[ToolCall]
    thinking: str | None = None


class BaseModel(ABC):
    """Abstract base class for all model providers.

    This class defines the interface that all LLM provider implementations must follow.
    Each provider (OpenAI, Anthropic, etc.) should implement these methods according
    to their specific API requirements.
    """

    def __init__(self, model_name: str) -> None:
        """Initialize the base model.

        Args:
            model_name: The name/identifier of the model to use.

        """
        self.model_name = model_name

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, object]],
        tools: list[Callable] | None = None,
        **kwargs,
    ) -> ChatResponse:
        """Send messages to the model and get a response.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            tools: Optional list of callable tools the model can use.
            **kwargs: Additional provider-specific parameters.

        Returns:
            ChatResponse object containing:
                - message: The full message object to append to history
                - text: The text content if any (can be None if only tool calls)
                - tool_calls: List of ToolCall objects if any tools were called
                - thinking: The thinking/reasoning content if any (provider-specific)

        """

    @abstractmethod
    def format_tools_for_api(self, tools: list[Callable]) -> list[dict[str, object]]:
        """Format tool callables into the provider's expected API format.

        Args:
            tools: List of callable functions to format.

        Returns:
            List of tool definitions in the provider's expected format.

        """

    @abstractmethod
    def format_tool_results(
        self,
        tool_results: list[dict[str, object]],
    ) -> dict[str, object] | list[dict[str, object]]:
        """Format tool execution results for the provider's expected format.

        Args:
            tool_results: List of dicts with 'tool_call_id', 'content', and 'name' keys.

        Returns:
            Either a single message dict or list of message dicts, depending on provider.

        """
