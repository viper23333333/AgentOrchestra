"""
Base agent class for the AgentOrchestra system.

Defines the common interface and shared functionality that all
concrete agents must implement. Provides lifecycle management,
error handling, and metrics tracking.
"""

from __future__ import annotations

import abc
import logging
import time
from typing import Any

from app.schemas.agent import AgentConfig, AgentResponse, AgentState, AgentType
from app.services.llm.provider import LLMServiceProvider

logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """Abstract base class for all agents in the AgentOrchestra system.

    Each agent has a specific role (planning, research, coding, etc.)
    and implements the execute() method to perform its task. Agents
    use the LLM service provider to interact with language models.

    Attributes:
        config: Agent configuration including name, type, and parameters.
        state: Runtime state tracking for the agent.
        llm: LLM service provider for model interactions.

    Example:
        >>> class MyAgent(BaseAgent):
        ...     @property
        ...     def name(self) -> str:
        ...         return "my_agent"
        ...     async def execute(self, task: str, context: dict) -> AgentResponse:
        ...         response = await self.llm.chat(task, system_prompt=self.system_prompt)
        ...         return AgentResponse(agent_name=self.name, content=response)
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        provider: str | None = None,
    ) -> None:
        """Initialize the agent.

        Args:
            config: Agent configuration. If None, uses default from subclass.
            provider: LLM provider override for this agent.
        """
        self._config = config or self._default_config()
        self._state = AgentState(
            agent_name=self._config.name,
            agent_type=self._config.agent_type,
        )
        self._llm: LLMServiceProvider | None = None
        self._provider_override = provider

        logger.info("Agent '%s' initialized (type=%s)", self.name, self.agent_type.value)

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the agent's unique name.

        Returns:
            str: Agent name.
        """
        ...

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Return a human-readable description of the agent's capabilities.

        Returns:
            str: Agent description.
        """
        ...

    @property
    @abc.abstractmethod
    def role(self) -> str:
        """Return the agent's role in the orchestration workflow.

        Returns:
            str: Agent role description.
        """
        ...

    @property
    @abc.abstractmethod
    def agent_type(self) -> AgentType:
        """Return the agent's type classification.

        Returns:
            AgentType: The agent type enum value.
        """
        ...

    @property
    @abc.abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent.

        The system prompt defines the agent's behavior, constraints,
        and output format expectations.

        Returns:
            str: System prompt template.
        """
        ...

    @abc.abstractmethod
    async def execute(self, task: str, context: dict[str, Any]) -> AgentResponse:
        """Execute the agent's primary task.

        This is the main entry point for agent execution. Each agent
        subclass implements its specific logic here.

        Args:
            task: The task description or input for the agent.
            context: Additional context from previous agents or the orchestrator.

        Returns:
            AgentResponse: The agent's execution result.
        """
        ...

    @abc.abstractmethod
    def _default_config(self) -> AgentConfig:
        """Return the default configuration for this agent.

        Returns:
            AgentConfig: Default configuration.
        """
        ...

    @property
    def config(self) -> AgentConfig:
        """Return the agent's current configuration.

        Returns:
            AgentConfig: Agent configuration.
        """
        return self._config

    @property
    def state(self) -> AgentState:
        """Return the agent's current runtime state.

        Returns:
            AgentState: Current agent state.
        """
        return self._state

    @property
    def llm(self) -> LLMServiceProvider:
        """Get or create the LLM service provider.

        Lazily initializes the provider on first access.

        Returns:
            LLMServiceProvider: The LLM service provider.
        """
        if self._llm is None:
            self._llm = LLMServiceProvider(provider=self._provider_override)
        return self._llm

    def update_config(self, config_update: dict[str, Any]) -> None:
        """Update the agent's configuration at runtime.

        Args:
            config_update: Dictionary of configuration fields to update.
        """
        current = self._config.model_dump()
        current.update({k: v for k, v in config_update.items() if v is not None})
        self._config = AgentConfig(**current)
        logger.info("Agent '%s' configuration updated", self.name)

    async def _execute_with_tracking(
        self,
        task: str,
        context: dict[str, Any],
    ) -> AgentResponse:
        """Execute the agent with state tracking and error handling.

        Wraps the execute() method with timing, state management,
        and error capture.

        Args:
            task: The task description.
            context: Additional context.

        Returns:
            AgentResponse: The execution result with timing metadata.
        """
        from app.schemas.agent import AgentStatus

        self._state.status = AgentStatus.RUNNING
        self._state.current_task = task
        self._state.input_data = context
        self._state.error_message = None

        start_time = time.perf_counter()
        try:
            response = await self.execute(task, context)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            response.execution_time_ms = elapsed_ms
            self._state.status = AgentStatus.COMPLETED if response.success else AgentStatus.ERROR
            self._state.output_data = {"content": response.content}
            self._state.execution_count += 1
            self._state.total_execution_time_ms += elapsed_ms

            logger.info(
                "Agent '%s' completed in %.1fms (success=%s)",
                self.name,
                elapsed_ms,
                response.success,
            )
            return response

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._state.status = AgentStatus.ERROR
            self._state.error_message = str(e)
            self._state.last_updated = __import__("datetime").datetime.utcnow()

            logger.error(
                "Agent '%s' failed after %.1fms: %s",
                self.name,
                elapsed_ms,
                str(e),
                exc_info=True,
            )

            return AgentResponse(
                agent_name=self.name,
                agent_type=self.agent_type,
                success=False,
                content="",
                error=str(e),
                execution_time_ms=elapsed_ms,
            )
