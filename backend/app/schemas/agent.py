"""
Agent-related data models for the AgentOrchestra system.

Defines Pydantic models for agent configuration, state, responses,
and other agent-specific data structures.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AgentType(StrEnum):
    """Enumeration of available agent types."""

    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    SUMMARIZER = "summarizer"


class AgentStatus(StrEnum):
    """Enumeration of agent runtime statuses."""

    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


class AgentConfig(BaseModel):
    """Configuration for an individual agent.

    Attributes:
        name: Human-readable agent name.
        agent_type: The type/category of the agent.
        description: Detailed description of the agent's capabilities.
        model: LLM model to use (overrides global default).
        temperature: Sampling temperature for this agent.
        max_tokens: Maximum tokens for this agent's responses.
        system_prompt: Custom system prompt template.
        tools: List of tool names this agent has access to.
        max_retries: Maximum retry attempts on failure.
        timeout_seconds: Execution timeout in seconds.
    """

    name: str = Field(..., min_length=1, description="Agent name")
    agent_type: AgentType = Field(..., description="Agent type")
    description: str = Field(..., min_length=1, description="Agent description")
    model: str | None = Field(default=None, description="LLM model override")
    temperature: float | None = Field(
        default=None, ge=0.0, le=2.0, description="Temperature override"
    )
    max_tokens: int | None = Field(default=None, ge=1, le=128000, description="Max tokens override")
    system_prompt: str | None = Field(default=None, description="Custom system prompt")
    tools: list[str] = Field(default_factory=list, description="Available tools")
    max_retries: int = Field(default=3, ge=0, le=10, description="Max retries")
    timeout_seconds: int = Field(default=120, ge=10, le=600, description="Timeout in seconds")


class AgentState(BaseModel):
    """Runtime state of an agent.

    Tracks the current execution state, metrics, and history of an agent.

    Attributes:
        agent_name: Name of the agent.
        agent_type: Type of the agent.
        status: Current runtime status.
        current_task: Description of the task currently being processed.
        input_data: Input data for the current task.
        output_data: Output data from the current task.
        error_message: Error message if the agent encountered an error.
        execution_count: Number of tasks executed by this agent.
        total_execution_time_ms: Cumulative execution time in milliseconds.
        last_updated: Timestamp of the last state update.
    """

    agent_name: str = Field(..., description="Agent name")
    agent_type: AgentType = Field(..., description="Agent type")
    status: AgentStatus = Field(default=AgentStatus.IDLE, description="Current status")
    current_task: str | None = Field(default=None, description="Current task description")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Input data")
    output_data: dict[str, Any] = Field(default_factory=dict, description="Output data")
    error_message: str | None = Field(default=None, description="Error message")
    execution_count: int = Field(default=0, ge=0, description="Tasks executed")
    total_execution_time_ms: float = Field(default=0.0, ge=0.0, description="Total execution time")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")


class AgentResponse(BaseModel):
    """Response produced by an agent after execution.

    Attributes:
        agent_name: Name of the agent that produced the response.
        agent_type: Type of the agent.
        success: Whether the execution was successful.
        content: The primary output content.
        artifacts: Additional output artifacts (code, files, etc.).
        metadata: Additional metadata about the execution.
        execution_time_ms: Time taken for this execution.
        error: Error message if execution failed.
    """

    agent_name: str = Field(..., description="Agent name")
    agent_type: AgentType = Field(..., description="Agent type")
    success: bool = Field(default=True, description="Execution success flag")
    content: str = Field(default="", description="Primary output content")
    artifacts: list[dict[str, Any]] = Field(default_factory=list, description="Output artifacts")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    execution_time_ms: float | None = Field(default=None, description="Execution time")
    error: str | None = Field(default=None, description="Error message if failed")


class AgentInfo(BaseModel):
    """Public information about an agent (returned by API).

    Attributes:
        name: Agent name.
        agent_type: Agent type.
        description: Agent description.
        status: Current runtime status.
        tools: List of available tools.
        execution_count: Number of tasks executed.
    """

    name: str = Field(..., description="Agent name")
    agent_type: AgentType = Field(..., description="Agent type")
    description: str = Field(..., description="Agent description")
    status: AgentStatus = Field(default=AgentStatus.IDLE, description="Current status")
    tools: list[str] = Field(default_factory=list, description="Available tools")
    execution_count: int = Field(default=0, description="Tasks executed")


class AgentConfigUpdate(BaseModel):
    """Model for updating agent configuration via API.

    Only non-None fields will be updated.

    Attributes:
        model: New LLM model.
        temperature: New temperature.
        max_tokens: New max tokens.
        system_prompt: New system prompt.
        tools: New list of tools.
        max_retries: New max retries.
        timeout_seconds: New timeout.
    """

    model: str | None = Field(default=None, description="New LLM model")
    temperature: float | None = Field(default=None, ge=0.0, le=2.0, description="New temperature")
    max_tokens: int | None = Field(default=None, ge=1, le=128000, description="New max tokens")
    system_prompt: str | None = Field(default=None, description="New system prompt")
    tools: list[str] | None = Field(default=None, description="New tools list")
    max_retries: int | None = Field(default=None, ge=0, le=10, description="New max retries")
    timeout_seconds: int | None = Field(default=None, ge=10, le=600, description="New timeout")
