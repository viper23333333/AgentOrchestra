"""
Chat API endpoints for the AgentOrchestra system.

Provides REST endpoints for sending chat messages, receiving streaming
responses via SSE, and retrieving conversation history.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.schemas.message import (
    AgentMessage,
    ChatRequest,
    ChatResponse,
    MessageType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# In-memory task store (replace with database in production)
_task_store: dict[str, dict[str, Any]] = {}


@router.post(
    "",
    response_model=ChatResponse,
    summary="Send a chat message",
    description="Send a message and receive a response from the multi-agent system.",
)
async def send_message(request: ChatRequest) -> ChatResponse:
    """Process a chat message through the orchestration pipeline.

    Creates or continues a conversation, runs the multi-agent workflow,
    and returns the final response with all agent outputs.

    Args:
        request: The chat request containing the message and options.

    Returns:
        ChatResponse: The response with the assistant's message and agent outputs.

    Raises:
        HTTPException: If the orchestration fails.
    """
    try:
        from app.core.orchestrator import Orchestrator

        conversation_id = request.conversation_id or uuid.uuid4().hex

        logger.info(
            "Processing chat message (conversation_id=%s, stream=%s)",
            conversation_id,
            request.stream,
        )

        # Initialize orchestrator and execute
        orchestrator = Orchestrator(provider=request.model_override)
        task_result = await orchestrator.execute(request.message)

        # Build agent messages from the task result
        agent_messages = [
            AgentMessage(
                agent_name=agent_name,
                agent_role=agent_name,
                content=content,
                message_type=MessageType.TEXT,
            )
            for agent_name, content in task_result.outputs.items()
        ]

        response = ChatResponse(
            message=task_result.summary or "Task completed successfully.",
            conversation_id=conversation_id,
            agent_messages=agent_messages,
            task_result=task_result,
        )

        # Store for history retrieval
        _task_store[conversation_id] = {
            "request": request.model_dump(),
            "response": response.model_dump(),
        }

        return response

    except Exception as e:
        logger.error("Chat processing failed: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}") from e


@router.get(
    "/stream",
    summary="Stream chat response via SSE",
    description="Send a message and receive a streaming response using Server-Sent Events.",
)
async def stream_message(
    message: str,
    conversation_id: str | None = None,
    model_override: str | None = None,
) -> EventSourceResponse:
    """Stream a chat response via Server-Sent Events (SSE).

    Each agent's output is sent as a separate SSE event, allowing
    the client to display progress in real-time.

    Args:
        message: The user's message.
        conversation_id: Optional conversation ID for continuing a conversation.
        model_override: Optional model override.

    Returns:
        EventSourceResponse: SSE stream of agent events.

    Raises:
        HTTPException: If streaming fails to initialize.
    """
    try:
        from app.core.orchestrator import Orchestrator

        conversation_id = conversation_id or uuid.uuid4().hex
        orchestrator = Orchestrator(provider=model_override)

        async def event_generator():
            """Generate SSE events from the orchestration workflow."""
            try:
                async for event in orchestrator.execute_stream(message):
                    yield {
                        "event": event.get("event", "message"),
                        "data": json.dumps(event, default=str),
                    }
            except Exception as e:
                logger.error("SSE stream error: %s", str(e), exc_info=True)
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)}),
                }

        return EventSourceResponse(event_generator())

    except Exception as e:
        logger.error("Failed to initialize stream: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stream init failed: {str(e)}") from e


@router.get(
    "/history",
    summary="Get conversation history",
    description="Retrieve the history of conversations.",
)
async def get_history(
    conversation_id: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Retrieve conversation history.

    Args:
        conversation_id: Specific conversation ID. If None, returns all conversations.
        limit: Maximum number of conversations to return.

    Returns:
        dict: Conversation history data.
    """
    if conversation_id:
        # Return specific conversation
        conversation = _task_store.get(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=404, detail=f"Conversation '{conversation_id}' not found"
            )
        return {"conversation_id": conversation_id, "data": conversation}

    # Return all conversations (limited)
    all_conversations = list(_task_store.items())[:limit]
    return {
        "conversations": [
            {"conversation_id": cid, "data": data} for cid, data in all_conversations
        ],
        "total": len(_task_store),
    }
