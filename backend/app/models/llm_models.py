"""
LLM model management with unified adapter interface.

Provides an abstraction layer over multiple LLM providers (OpenAI, Anthropic, Ollama)
using the Adapter pattern. Each provider has a concrete adapter that implements a
common interface, and a factory class creates the appropriate adapter based on config.
"""

from __future__ import annotations

import abc
import logging
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage

from app.config.settings import LLMProviderSettings, Settings, get_settings

logger = logging.getLogger(__name__)


class BaseModelAdapter(abc.ABC):
    """Abstract base class for LLM model adapters.

    Defines the common interface that all LLM provider adapters must implement.
    Each adapter wraps a LangChain chat model and provides a unified API for
    both streaming and non-streaming inference.

    Attributes:
        provider_name: Human-readable name of the LLM provider.
        model_name: The specific model being used.
        settings: Provider-specific settings.
    """

    def __init__(self, settings: LLMProviderSettings) -> None:
        """Initialize the adapter with provider settings.

        Args:
            settings: Provider-specific configuration including API keys and model params.
        """
        self.settings = settings
        self.provider_name: str = "unknown"
        self.model_name: str = settings.model
        self._model: BaseChatModel | None = None

    @property
    @abc.abstractmethod
    def model(self) -> BaseChatModel:
        """Return the underlying LangChain chat model instance.

        Lazily initializes the model on first access.

        Returns:
            BaseChatModel: The LangChain chat model.
        """
        ...

    @abc.abstractmethod
    async def invoke(self, messages: list[BaseMessage], **kwargs: Any) -> AIMessage:
        """Send messages to the LLM and return the response.

        Args:
            messages: List of LangChain message objects.
            **kwargs: Additional provider-specific parameters.

        Returns:
            AIMessage: The model's response message.

        Raises:
            LLMAdapterError: If the invocation fails.
        """
        ...

    @abc.abstractmethod
    async def stream(self, messages: list[BaseMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream responses from the LLM token by token.

        Args:
            messages: List of LangChain message objects.
            **kwargs: Additional provider-specific parameters.

        Yields:
            str: Individual tokens/chunks of the response.

        Raises:
            LLMAdapterError: If streaming fails.
        """
        ...

    def validate_api_key(self) -> bool:
        """Check whether the required API key is configured.

        Returns:
            bool: True if the API key is present and non-empty.
        """
        return bool(self.settings.api_key)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider_name}, model={self.model_name})"


class LLMAdapterError(Exception):
    """Custom exception for LLM adapter errors.

    Wraps provider-specific errors with additional context about
    which adapter and operation failed.
    """

    def __init__(self, adapter: str, operation: str, detail: str) -> None:
        self.adapter = adapter
        self.operation = operation
        self.detail = detail
        super().__init__(f"[{adapter}] {operation} failed: {detail}")


class OpenAIAdapter(BaseModelAdapter):
    """Adapter for OpenAI models (GPT-4o, GPT-4, GPT-3.5-turbo, etc.).

    Uses langchain-openai's ChatOpenAI as the underlying model.
    Supports both streaming and non-streaming inference.
    """

    def __init__(self, settings: LLMProviderSettings) -> None:
        """Initialize the OpenAI adapter.

        Args:
            settings: Provider settings including API key and model parameters.
        """
        super().__init__(settings)
        self.provider_name = "openai"

    @property
    def model(self) -> BaseChatModel:
        """Create and return the ChatOpenAI model instance.

        Returns:
            BaseChatModel: Configured ChatOpenAI instance.

        Raises:
            LLMAdapterError: If the API key is not configured.
        """
        if self._model is not None:
            return self._model

        if not self.validate_api_key():
            raise LLMAdapterError(
                adapter=self.provider_name,
                operation="init",
                detail="OPENAI_API_KEY is not configured",
            )

        from langchain_openai import ChatOpenAI

        self._model = ChatOpenAI(
            api_key=self.settings.api_key,
            model=self.settings.model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            streaming=True,
        )
        logger.info("Initialized OpenAI adapter with model: %s", self.settings.model)
        return self._model

    async def invoke(self, messages: list[BaseMessage], **kwargs: Any) -> AIMessage:
        """Invoke the OpenAI model with the given messages.

        Args:
            messages: List of LangChain message objects.
            **kwargs: Additional parameters (e.g., temperature override).

        Returns:
            AIMessage: The model's response.

        Raises:
            LLMAdapterError: On API call failure.
        """
        try:
            response = await self.model.ainvoke(messages, **kwargs)
            return response
        except Exception as e:
            raise LLMAdapterError(
                adapter=self.provider_name, operation="invoke", detail=str(e)
            ) from e

    async def stream(self, messages: list[BaseMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream responses from the OpenAI model.

        Args:
            messages: List of LangChain message objects.
            **kwargs: Additional parameters.

        Yields:
            str: Token chunks from the model response.

        Raises:
            LLMAdapterError: On streaming failure.
        """
        try:
            async for chunk in self.model.astream(messages, **kwargs):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as e:
            raise LLMAdapterError(
                adapter=self.provider_name, operation="stream", detail=str(e)
            ) from e


class AnthropicAdapter(BaseModelAdapter):
    """Adapter for Anthropic models (Claude Sonnet, Claude Opus, etc.).

    Uses langchain-anthropic's ChatAnthropic as the underlying model.
    Supports both streaming and non-streaming inference.
    """

    def __init__(self, settings: LLMProviderSettings) -> None:
        """Initialize the Anthropic adapter.

        Args:
            settings: Provider settings including API key and model parameters.
        """
        super().__init__(settings)
        self.provider_name = "anthropic"

    @property
    def model(self) -> BaseChatModel:
        """Create and return the ChatAnthropic model instance.

        Returns:
            BaseChatModel: Configured ChatAnthropic instance.

        Raises:
            LLMAdapterError: If the API key is not configured.
        """
        if self._model is not None:
            return self._model

        if not self.validate_api_key():
            raise LLMAdapterError(
                adapter=self.provider_name,
                operation="init",
                detail="ANTHROPIC_API_KEY is not configured",
            )

        from langchain_anthropic import ChatAnthropic

        self._model = ChatAnthropic(
            api_key=self.settings.api_key,
            model=self.settings.model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            streaming=True,
        )
        logger.info("Initialized Anthropic adapter with model: %s", self.settings.model)
        return self._model

    async def invoke(self, messages: list[BaseMessage], **kwargs: Any) -> AIMessage:
        """Invoke the Anthropic model with the given messages.

        Args:
            messages: List of LangChain message objects.
            **kwargs: Additional parameters.

        Returns:
            AIMessage: The model's response.

        Raises:
            LLMAdapterError: On API call failure.
        """
        try:
            response = await self.model.ainvoke(messages, **kwargs)
            return response
        except Exception as e:
            raise LLMAdapterError(
                adapter=self.provider_name, operation="invoke", detail=str(e)
            ) from e

    async def stream(self, messages: list[BaseMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream responses from the Anthropic model.

        Args:
            messages: List of LangChain message objects.
            **kwargs: Additional parameters.

        Yields:
            str: Token chunks from the model response.

        Raises:
            LLMAdapterError: On streaming failure.
        """
        try:
            async for chunk in self.model.astream(messages, **kwargs):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as e:
            raise LLMAdapterError(
                adapter=self.provider_name, operation="stream", detail=str(e)
            ) from e


class OllamaAdapter(BaseModelAdapter):
    """Adapter for Ollama local models.

    Uses langchain-community's ChatOllama as the underlying model.
    Supports both streaming and non-streaming inference with local LLMs.
    """

    def __init__(self, settings: LLMProviderSettings) -> None:
        """Initialize the Ollama adapter.

        Args:
            settings: Provider settings including base URL and model parameters.
        """
        super().__init__(settings)
        self.provider_name = "ollama"

    @property
    def model(self) -> BaseChatModel:
        """Create and return the ChatOllama model instance.

        Returns:
            BaseChatModel: Configured ChatOllama instance.
        """
        if self._model is not None:
            return self._model

        from langchain_community.chat_models import ChatOllama

        self._model = ChatOllama(
            base_url=self.settings.base_url or "http://localhost:11434",
            model=self.settings.model,
            temperature=self.settings.temperature,
            streaming=True,
        )
        logger.info("Initialized Ollama adapter with model: %s", self.settings.model)
        return self._model

    def validate_api_key(self) -> bool:
        """Ollama does not require an API key.

        Returns:
            bool: Always True for Ollama.
        """
        return True

    async def invoke(self, messages: list[BaseMessage], **kwargs: Any) -> AIMessage:
        """Invoke the Ollama model with the given messages.

        Args:
            messages: List of LangChain message objects.
            **kwargs: Additional parameters.

        Returns:
            AIMessage: The model's response.

        Raises:
            LLMAdapterError: On invocation failure.
        """
        try:
            response = await self.model.ainvoke(messages, **kwargs)
            return response
        except Exception as e:
            raise LLMAdapterError(
                adapter=self.provider_name, operation="invoke", detail=str(e)
            ) from e

    async def stream(self, messages: list[BaseMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream responses from the Ollama model.

        Args:
            messages: List of LangChain message objects.
            **kwargs: Additional parameters.

        Yields:
            str: Token chunks from the model response.

        Raises:
            LLMAdapterError: On streaming failure.
        """
        try:
            async for chunk in self.model.astream(messages, **kwargs):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as e:
            raise LLMAdapterError(
                adapter=self.provider_name, operation="stream", detail=str(e)
            ) from e


class LLMFactory:
    """Factory class for creating LLM adapters based on configuration.

    Provides a centralized point for creating and caching LLM adapters.
    Supports dynamic provider switching and adapter reuse.

    Example:
        >>> factory = LLMFactory()
        >>> adapter = factory.create_adapter("openai")
        >>> response = await adapter.invoke([HumanMessage(content="Hello")])
    """

    _adapters: dict[str, BaseModelAdapter] = {}

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the factory with application settings.

        Args:
            settings: Application settings. Uses get_settings() if not provided.
        """
        self._settings = settings or get_settings()

    def create_adapter(self, provider: str | None = None) -> BaseModelAdapter:
        """Create or return a cached LLM adapter for the specified provider.

        Args:
            provider: Provider name ("openai", "anthropic", "ollama").
                     Defaults to the configured default provider.

        Returns:
            BaseModelAdapter: The LLM adapter instance.

        Raises:
            ValueError: If the provider name is not recognized.
        """
        provider = provider or self._settings.default_llm_provider

        # Return cached adapter if available
        if provider in LLMFactory._adapters:
            return LLMFactory._adapters[provider]

        # Create new adapter based on provider
        adapter_map: dict[str, type[BaseModelAdapter]] = {
            "openai": OpenAIAdapter,
            "anthropic": AnthropicAdapter,
            "ollama": OllamaAdapter,
        }

        adapter_cls = adapter_map.get(provider)
        if adapter_cls is None:
            raise ValueError(
                f"Unknown LLM provider: '{provider}'. "
                f"Supported providers: {list(adapter_map.keys())}"
            )

        # Get provider-specific settings
        settings_getters = {
            "openai": self._settings.get_openai_settings,
            "anthropic": self._settings.get_anthropic_settings,
            "ollama": self._settings.get_ollama_settings,
        }
        provider_settings = settings_getters[provider]()
        adapter = adapter_cls(provider_settings)

        # Cache the adapter
        LLMFactory._adapters[provider] = adapter
        logger.info("Created and cached %s adapter", provider)
        return adapter

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached adapters.

        Useful for testing or when configuration changes at runtime.
        """
        cls._adapters.clear()
        logger.info("Cleared LLM adapter cache")
