"""
Task management API endpoints.

Provides REST endpoints for creating, listing, and retrieving tasks.
Tasks represent multi-agent workflow executions.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------


class TaskCreateRequest(BaseModel):
    """Request model for creating a new task.

    Attributes:
        message: The user's task description.
        model_override: Optional LLM model override.
        priority: Task priority (low, medium, high).
    """

    message: str = Field(..., min_length=1, description="Task description")
    model_override: str | None = Field(default=None, description="LLM model override")
    priority: str = Field(default="medium", description="Task priority")


class TaskInfo(BaseModel):
    """Information about a task.

    Attributes:
        id: Unique task identifier.
        message: The original task description.
        status: Current task status.
        priority: Task priority.
        result: Task result if completed.
        created_at: Creation timestamp.
        completed_at: Completion timestamp.
    """

    id: str = Field(..., description="Task ID")
    message: str = Field(..., description="Task description")
    status: str = Field(default="pending", description="Task status")
    priority: str = Field(default="medium", description="Task priority")
    result: dict[str, Any] | None = Field(default=None, description="Task result")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created at")
    completed_at: datetime | None = Field(default=None, description="Completed at")


# ---------------------------------------------------------------------------
# In-memory Task Store
# ---------------------------------------------------------------------------

_tasks: dict[str, TaskInfo] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=TaskInfo,
    summary="Create a new task",
    description="Create and execute a new multi-agent task.",
    status_code=201,
)
async def create_task(request: TaskCreateRequest) -> TaskInfo:
    """Create a new task and execute it through the orchestration pipeline.

    Args:
        request: The task creation request.

    Returns:
        TaskInfo: The created task with its result.

    Raises:
        HTTPException: If task creation or execution fails.
    """
    task_id = uuid.uuid4().hex
    task = TaskInfo(
        id=task_id,
        message=request.message,
        status="processing",
        priority=request.priority,
    )
    _tasks[task_id] = task

    try:
        from app.core.orchestrator import Orchestrator

        logger.info("Creating task %s: %s", task_id, request.message[:100])

        orchestrator = Orchestrator(provider=request.model_override)
        task_result = await orchestrator.execute(request.message)

        # Update task with result
        task.status = "completed"
        task.result = task_result.model_dump()
        task.completed_at = datetime.utcnow()

        logger.info(
            "Task %s completed in %.1fms", task_id, task_result.total_execution_time_ms or 0
        )

        return task

    except Exception as e:
        task.status = "failed"
        logger.error("Task %s failed: %s", task_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}") from e


@router.get(
    "",
    response_model=list[TaskInfo],
    summary="List all tasks",
    description="Get a list of all tasks with optional filtering.",
)
async def list_tasks(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[TaskInfo]:
    """List all tasks with optional filtering.

    Args:
        status: Filter by status (pending, processing, completed, failed).
        limit: Maximum number of tasks to return.
        offset: Number of tasks to skip.

    Returns:
        list[TaskInfo]: List of task information objects.
    """
    all_tasks = list(_tasks.values())

    # Filter by status
    if status:
        all_tasks = [t for t in all_tasks if t.status == status]

    # Sort by creation time (newest first)
    all_tasks.sort(key=lambda t: t.created_at, reverse=True)

    # Apply pagination
    paginated = all_tasks[offset : offset + limit]

    return paginated


@router.get(
    "/{task_id}",
    response_model=TaskInfo,
    summary="Get task details",
    description="Get detailed information about a specific task.",
)
async def get_task(task_id: str) -> TaskInfo:
    """Get detailed information about a specific task.

    Args:
        task_id: The unique task identifier.

    Returns:
        TaskInfo: Detailed task information.

    Raises:
        HTTPException: If the task is not found.
    """
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task
