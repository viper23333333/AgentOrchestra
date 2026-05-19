"""
LLM service provider module.

Encapsulates LLM model invocation with support for both streaming and
non-streaming modes. Provides a high-level interface for agents to
interact with LLM models without worrying about provider specifics.
"""

from __future__ import annotations

import logging
import time
from typing import Any, AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.models.llm_models import BaseModelAdapter, LLMAdapterError, LLMFactory

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Custom exception for LLM service errors."""

    def __init__(self, message: str, provider: str = "unknown") -> None:
        self.provider = provider
        super().__init__(f"[LLMService:{provider}] {message}")


class LLMServiceProvider:
    """High-level LLM service that wraps the adapter layer.

    Provides a clean interface for agents to call LLM models with
    automatic prompt construction, error handling, and metrics tracking.

    Attributes:
        adapter: The underlying LLM adapter.
        provider_name: Name of the active LLM provider.

    Example:
        >>> provider = LLMServiceProvider("openai")
        >>> response = await provider.chat("Hello, world!")
        >>> async for token in provider.chat_stream("Tell me a story"):
        ...     print(token, end="")
    """

    def __init__(self, provider: str | None = None) -> None:
        """Initialize the LLM service provider.

        Args:
            provider: LLM provider name. Defaults to the configured default.

        Raises:
            LLMServiceError: If the adapter cannot be created.
        """
        self._factory = LLMFactory()
        try:
            self.adapter: BaseModelAdapter = self._factory.create_adapter(provider)
        except (ValueError, LLMAdapterError) as e:
            raise LLMServiceError(str(e), provider or "unknown") from e

        self.provider_name: str = self.adapter.provider_name
        logger.info("LLMServiceProvider initialized with %s", self.provider_name)

    async def chat(
        self,
        message: str,
        system_prompt: str | None = None,
        history: list[BaseMessage] | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> str:
        """Send a chat message and get a complete response.

        Constructs the message list from the system prompt, conversation
        history, and the current user message, then invokes the LLM.

        Args:
            message: The user's message content.
            system_prompt: Optional system prompt to set context.
            history: Optional conversation history (previous messages).
            temperature: Optional temperature override for this call.
            **kwargs: Additional provider-specific parameters.

        Returns:
            str: The LLM's response text.

        Raises:
            LLMServiceError: If the LLM invocation fails.
        """
        messages = self._build_messages(message, system_prompt, history)

        if temperature is not None:
            kwargs["temperature"] = temperature

        start_time = time.perf_counter()
        try:
            response: AIMessage = await self.adapter.invoke(messages, **kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.debug(
                "LLM response received in %.1fms (provider=%s, tokens=%s)",
                elapsed_ms,
                self.provider_name,
                getattr(response, "response_metadata", {}).get("token_usage", "N/A"),
            )
            return str(response.content)
        except LLMAdapterError as e:
            raise LLMServiceError(str(e), self.provider_name) from e
        except Exception as e:
            raise LLMServiceError(
                f"Unexpected error: {e}", self.provider_name
            ) from e

    async def chat_stream(
        self,
        message: str,
        system_prompt: str | None = None,
        history: list[BaseMessage] | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a chat response token by token.

        Constructs the message list and streams the LLM's response.

        Args:
            message: The user's message content.
            system_prompt: Optional system prompt to set context.
            history: Optional conversation history.
            temperature: Optional temperature override for this call.
            **kwargs: Additional provider-specific parameters.

        Yields:
            str: Individual token chunks from the LLM response.

        Raises:
            LLMServiceError: If streaming fails.
        """
        messages = self._build_messages(message, system_prompt, history)

        if temperature is not None:
            kwargs["temperature"] = temperature

        start_time = time.perf_counter()
        token_count = 0
        try:
            async for token in self.adapter.stream(messages, **kwargs):
                token_count += 1
                yield token
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.debug(
                "LLM stream completed in %.1fms (provider=%s, tokens=%d)",
                elapsed_ms,
                self.provider_name,
                token_count,
            )
        except LLMAdapterError as e:
            raise LLMServiceError(str(e), self.provider_name) from e
        except Exception as e:
            raise LLMServiceError(
                f"Unexpected error during streaming: {e}", self.provider_name
            ) from e

    def _build_messages(
        self,
        message: str,
        system_prompt: str | None,
        history: list[BaseMessage] | None,
    ) -> list[BaseMessage]:
        """Build the complete message list for the LLM call.

        Args:
            message: The current user message.
            system_prompt: Optional system prompt.
            history: Optional conversation history.

        Returns:
            list[BaseMessage]: Ordered list of messages.
        """
        messages: list[BaseMessage] = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        if history:
            messages.extend(history)

        messages.append(HumanMessage(content=message))
        return messages

    def switch_provider(self, provider: str) -> None:
        """Switch to a different LLM provider at runtime.

        Args:
            provider: The new provider name ("openai", "anthropic", "ollama").

        Raises:
            LLMServiceError: If the new adapter cannot be created.
        """
        try:
            self.adapter = self._factory.create_adapter(provider)
            self.provider_name = self.adapter.provider_name
            logger.info("Switched LLM provider to %s", self.provider_name)
        except (ValueError, LLMAdapterError) as e:
            raise LLMServiceError(str(e), provider) from e
