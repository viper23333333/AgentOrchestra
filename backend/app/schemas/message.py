"""
Message data models for the AgentOrchestra system.

Defines Pydantic models for chat messages, agent messages, task plans,
task results, and other communication structures used across the system.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    """Enumeration of possible message roles in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"


class MessageType(StrEnum):
    """Enumeration of message types for classification."""

    TEXT = "text"
    CODE = "code"
    PLAN = "plan"
    REVIEW = "review"
    SUMMARY = "summary"
    ERROR = "error"


class ChatMessage(BaseModel):
    """Represents a single chat message in a conversation.

    Attributes:
        id: Unique message identifier (auto-generated UUID).
        role: The role of the message sender.
        content: The text content of the message.
        message_type: Classification of the message type.
        timestamp: When the message was created.
        metadata: Optional additional metadata (e.g., token count, model used).
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique message ID")
    role: MessageRole = Field(default=MessageRole.USER, description="Sender role")
    content: str = Field(..., min_length=1, description="Message content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "content": "Help me build a REST API with FastAPI",
                    "message_type": "text",
                }
            ]
        }
    }


class AgentMessage(BaseModel):
    """Represents a message produced by a specific agent.

    Extends ChatMessage with agent-specific metadata such as agent name,
    execution time, and tool usage information.

    Attributes:
        agent_name: Name of the agent that produced this message.
        agent_role: The role/function of the agent.
        execution_time_ms: Time taken to generate this response (milliseconds).
        tools_used: List of tool names used during generation.
        confidence: Confidence score (0.0 - 1.0) of the agent's response.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique message ID")
    agent_name: str = Field(..., description="Name of the producing agent")
    agent_role: str = Field(..., description="Role of the producing agent")
    content: str = Field(..., min_length=1, description="Agent response content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    execution_time_ms: float | None = Field(default=None, description="Execution time in ms")
    tools_used: list[str] = Field(default_factory=list, description="Tools used")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0, description="Confidence score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskStep(BaseModel):
    """Represents a single step within a task plan.

    Attributes:
        step_number: Sequential step number (1-based).
        description: Human-readable description of the step.
        assigned_agent: Name of the agent responsible for this step.
        dependencies: List of step numbers this step depends on.
        status: Current status of the step.
        output: The output/result of executing this step.
    """

    class Status(StrEnum):
        """Status of a task step."""

        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"
        SKIPPED = "skipped"

    step_number: int = Field(..., ge=1, description="Step number (1-based)")
    description: str = Field(..., min_length=1, description="Step description")
    assigned_agent: str = Field(..., description="Agent assigned to this step")
    dependencies: list[int] = Field(default_factory=list, description="Dependent step numbers")
    status: Status = Field(default=Status.PENDING, description="Step status")
    output: str | None = Field(default=None, description="Step output/result")


class TaskPlan(BaseModel):
    """Represents a structured execution plan created by the planner agent.

    Attributes:
        id: Unique plan identifier.
        user_request: The original user request that triggered this plan.
        objective: High-level objective of the plan.
        steps: Ordered list of execution steps.
        estimated_complexity: Estimated complexity (1-10).
        created_at: Timestamp when the plan was created.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique plan ID")
    user_request: str = Field(..., description="Original user request")
    objective: str = Field(..., description="Plan objective")
    steps: list[TaskStep] = Field(default_factory=list, description="Execution steps")
    estimated_complexity: int = Field(default=5, ge=1, le=10, description="Complexity estimate")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class TaskResult(BaseModel):
    """Represents the final result of a completed task.

    Aggregates outputs from all agents involved in the task execution.

    Attributes:
        id: Unique result identifier.
        task_id: Reference to the associated task/plan ID.
        summary: High-level summary of the task outcome.
        outputs: Map of agent name to their output content.
        code_artifacts: List of generated code artifacts.
        status: Final task status.
        total_execution_time_ms: Total time for the entire task.
        created_at: Timestamp when the result was produced.
    """

    class Status(StrEnum):
        """Final task status."""

        SUCCESS = "success"
        PARTIAL = "partial"
        FAILED = "failed"

    id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique result ID")
    task_id: str = Field(..., description="Associated task ID")
    summary: str = Field(default="", description="Task outcome summary")
    outputs: dict[str, str] = Field(default_factory=dict, description="Agent outputs")
    code_artifacts: list[dict[str, Any]] = Field(
        default_factory=list, description="Generated code artifacts"
    )
    status: Status = Field(default=Status.SUCCESS, description="Final status")
    total_execution_time_ms: float | None = Field(default=None, description="Total execution time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class ChatRequest(BaseModel):
    """Incoming chat request from the client.

    Attributes:
        message: The user's message content.
        conversation_id: Optional conversation ID for continuing a conversation.
        stream: Whether to stream the response via SSE.
        model_override: Optional model override for this specific request.
        agent_override: Optional specific agent to route to directly.
    """

    message: str = Field(..., min_length=1, description="User message")
    conversation_id: str | None = Field(default=None, description="Conversation ID")
    stream: bool = Field(default=False, description="Enable SSE streaming")
    model_override: str | None = Field(default=None, description="Override default model")
    agent_override: str | None = Field(default=None, description="Override agent routing")


class ChatResponse(BaseModel):
    """Outgoing chat response to the client.

    Attributes:
        message: The assistant's response content.
        conversation_id: The conversation ID.
        agent_messages: List of individual agent messages.
        task_result: Optional task result if a multi-agent workflow was executed.
    """

    message: str = Field(..., description="Response message")
    conversation_id: str = Field(..., description="Conversation ID")
    agent_messages: list[AgentMessage] = Field(
        default_factory=list, description="Individual agent messages"
    )
    task_result: TaskResult | None = Field(default=None, description="Task result if applicable")
