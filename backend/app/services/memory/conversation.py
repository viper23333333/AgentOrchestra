"""
Conversation memory management module.

Provides both Redis-backed and in-memory conversation storage for
persisting chat history across requests. Supports configurable TTL,
conversation limits, and message pruning.
"""

from __future__ import annotations

import json
import logging
import time
from collections import OrderedDict
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class ConversationMemoryError(Exception):
    """Custom exception for conversation memory errors."""

    def __init__(self, message: str, backend: str = "unknown") -> None:
        self.backend = backend
        super().__init__(f"[Memory:{backend}] {message}")


class BaseConversationMemory:
    """Abstract base class for conversation memory backends.

    Defines the common interface for storing and retrieving
    conversation history.
    """

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Save a message to the conversation history.

        Args:
            conversation_id: Unique conversation identifier.
            role: Message role (user, assistant, system).
            content: Message content.
            metadata: Optional metadata to attach to the message.
        """
        raise NotImplementedError

    async def get_history(
        self,
        conversation_id: str,
        limit: int | None = None,
    ) -> list[BaseMessage]:
        """Retrieve conversation history as LangChain messages.

        Args:
            conversation_id: Unique conversation identifier.
            limit: Maximum number of messages to return (most recent first).

        Returns:
            list[BaseMessage]: List of LangChain message objects.
        """
        raise NotImplementedError

    async def clear(self, conversation_id: str) -> None:
        """Clear all messages for a conversation.

        Args:
            conversation_id: Unique conversation identifier.
        """
        raise NotImplementedError

    async def get_conversation_ids(self) -> list[str]:
        """List all known conversation IDs.

        Returns:
            list[str]: List of conversation IDs.
        """
        raise NotImplementedError


class InMemoryConversationMemory(BaseConversationMemory):
    """In-memory conversation storage.

    Stores conversations in an OrderedDict with automatic size limiting.
    Suitable for development and testing. Not persistent across restarts.

    Attributes:
        max_conversations: Maximum number of conversations to keep.
        max_messages_per_conversation: Max messages per conversation.
    """

    def __init__(
        self,
        max_conversations: int = 1000,
        max_messages_per_conversation: int = 100,
    ) -> None:
        """Initialize the in-memory store.

        Args:
            max_conversations: Maximum conversations to keep in memory.
            max_messages_per_conversation: Max messages per conversation.
        """
        self._store: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
        self.max_conversations = max_conversations
        self.max_messages_per_conversation = max_messages_per_conversation

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Save a message to the in-memory store.

        Args:
            conversation_id: Unique conversation identifier.
            role: Message role.
            content: Message content.
            metadata: Optional metadata.
        """
        if conversation_id not in self._store:
            self._store[conversation_id] = []
            # Evict oldest conversation if limit reached
            if len(self._store) > self.max_conversations:
                self._store.popitem(last=False)
                logger.debug("Evicted oldest conversation from memory store")

        message_data: dict[str, Any] = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        self._store[conversation_id].append(message_data)

        # Trim old messages if limit reached
        if len(self._store[conversation_id]) > self.max_messages_per_conversation:
            self._store[conversation_id] = self._store[conversation_id][
                -self.max_messages_per_conversation :
            ]

    async def get_history(
        self,
        conversation_id: str,
        limit: int | None = None,
    ) -> list[BaseMessage]:
        """Retrieve conversation history from the in-memory store.

        Args:
            conversation_id: Unique conversation identifier.
            limit: Maximum number of messages to return.

        Returns:
            list[BaseMessage]: List of LangChain message objects.
        """
        messages_data = self._store.get(conversation_id, [])
        if limit is not None:
            messages_data = messages_data[-limit:]

        return self._to_langchain_messages(messages_data)

    async def clear(self, conversation_id: str) -> None:
        """Clear a conversation from the in-memory store.

        Args:
            conversation_id: Unique conversation identifier.
        """
        self._store.pop(conversation_id, None)
        logger.debug("Cleared conversation %s from memory", conversation_id)

    async def get_conversation_ids(self) -> list[str]:
        """List all conversation IDs in the store.

        Returns:
            list[str]: List of conversation IDs.
        """
        return list(self._store.keys())

    @staticmethod
    def _to_langchain_messages(messages_data: list[dict[str, Any]]) -> list[BaseMessage]:
        """Convert raw message dicts to LangChain message objects.

        Args:
            messages_data: List of message dictionaries.

        Returns:
            list[BaseMessage]: List of LangChain message objects.
        """
        role_to_class: dict[str, type[BaseMessage]] = {
            "user": HumanMessage,
            "assistant": AIMessage,
            "system": SystemMessage,
        }
        messages: list[BaseMessage] = []
        for msg in messages_data:
            cls = role_to_class.get(msg["role"], HumanMessage)
            messages.append(cls(content=msg["content"]))
        return messages


class RedisConversationMemory(BaseConversationMemory):
    """Redis-backed conversation storage.

    Persists conversation history in Redis with configurable TTL.
    Suitable for production use with multiple server instances.

    Attributes:
        redis_url: Redis connection URL.
        ttl: Time-to-live for conversation data in seconds.
        key_prefix: Redis key prefix for namespacing.
    """

    def __init__(
        self,
        redis_url: str | None = None,
        ttl: int = 3600,
        key_prefix: str = "agent_orchestra:conv:",
    ) -> None:
        """Initialize the Redis-backed store.

        Args:
            redis_url: Redis connection URL. Defaults to settings.
            ttl: TTL in seconds for conversation keys.
            key_prefix: Redis key prefix.
        """
        settings = get_settings()
        self.redis_url = redis_url or settings.redis_url
        self.ttl = ttl
        self.key_prefix = key_prefix
        self._redis = None

    async def _get_redis(self):
        """Get or create the Redis connection.

        Returns:
            Redis connection instance.

        Raises:
            ConversationMemoryError: If Redis connection fails.
        """
        if self._redis is None:
            try:
                import redis.asyncio as aioredis

                self._redis = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    max_connections=10,
                )
                # Test connection
                await self._redis.ping()
                logger.info("Connected to Redis at %s", self.redis_url)
            except Exception as e:
                raise ConversationMemoryError(
                    f"Failed to connect to Redis: {e}", backend="redis"
                ) from e
        return self._redis

    def _conversation_key(self, conversation_id: str) -> str:
        """Build the Redis key for a conversation.

        Args:
            conversation_id: Conversation identifier.

        Returns:
            str: Full Redis key.
        """
        return f"{self.key_prefix}{conversation_id}"

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Save a message to Redis.

        Args:
            conversation_id: Unique conversation identifier.
            role: Message role.
            content: Message content.
            metadata: Optional metadata.
        """
        redis = await self._get_redis()
        key = self._conversation_key(conversation_id)

        message_data = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }

        try:
            await redis.rpush(key, json.dumps(message_data))
            await redis.expire(key, self.ttl)
        except Exception as e:
            raise ConversationMemoryError(f"Failed to save message: {e}", backend="redis") from e

    async def get_history(
        self,
        conversation_id: str,
        limit: int | None = None,
    ) -> list[BaseMessage]:
        """Retrieve conversation history from Redis.

        Args:
            conversation_id: Unique conversation identifier.
            limit: Maximum number of messages to return.

        Returns:
            list[BaseMessage]: List of LangChain message objects.
        """
        redis = await self._get_redis()
        key = self._conversation_key(conversation_id)

        try:
            raw_messages = await redis.lrange(key, -limit if limit else 0, -1)
        except Exception as e:
            raise ConversationMemoryError(
                f"Failed to retrieve history: {e}", backend="redis"
            ) from e

        messages_data: list[dict[str, Any]] = []
        for raw in raw_messages:
            try:
                messages_data.append(json.loads(raw))
            except json.JSONDecodeError:
                logger.warning("Skipping malformed message in Redis for %s", conversation_id)

        return InMemoryConversationMemory._to_langchain_messages(messages_data)

    async def clear(self, conversation_id: str) -> None:
        """Clear a conversation from Redis.

        Args:
            conversation_id: Unique conversation identifier.
        """
        redis = await self._get_redis()
        key = self._conversation_key(conversation_id)

        try:
            await redis.delete(key)
            logger.debug("Cleared conversation %s from Redis", conversation_id)
        except Exception as e:
            raise ConversationMemoryError(
                f"Failed to clear conversation: {e}", backend="redis"
            ) from e

    async def get_conversation_ids(self) -> list[str]:
        """List all conversation IDs in Redis.

        Returns:
            list[str]: List of conversation IDs.
        """
        redis = await self._get_redis()
        try:
            keys = await redis.keys(f"{self.key_prefix}*")
            # Strip the prefix to get just the IDs
            prefix_len = len(self.key_prefix)
            return [key[prefix_len:] for key in keys]
        except Exception as e:
            raise ConversationMemoryError(
                f"Failed to list conversations: {e}", backend="redis"
            ) from e

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None
            logger.info("Closed Redis connection")


class ConversationMemoryFactory:
    """Factory for creating the appropriate conversation memory backend.

    Selects between Redis and in-memory backends based on configuration
    and availability.

    Example:
        >>> memory = ConversationMemoryFactory.create()
        >>> await memory.save_message("conv-1", "user", "Hello")
    """

    @staticmethod
    def create(
        backend: str | None = None,
        **kwargs: Any,
    ) -> BaseConversationMemory:
        """Create a conversation memory instance.

        Args:
            backend: Memory backend type ("redis" or "memory").
                     Defaults to "redis" if REDIS_URL is configured, else "memory".
            **kwargs: Additional arguments passed to the backend constructor.

        Returns:
            BaseConversationMemory: The conversation memory instance.
        """
        settings = get_settings()
        backend = backend or ("redis" if settings.redis_url else "memory")

        if backend == "redis":
            logger.info("Using Redis conversation memory backend")
            return RedisConversationMemory(**kwargs)
        else:
            logger.info("Using in-memory conversation memory backend")
            return InMemoryConversationMemory(**kwargs)
