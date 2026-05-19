"""
Agent management API endpoints.

Provides REST endpoints for listing agents, getting agent details,
and updating agent configurations at runtime.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentConfigUpdate, AgentInfo, AgentStatus, AgentType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])

# Global agent registry (populated by the orchestrator)
_agent_registry: dict[str, dict[str, Any]] = {}


def register_agents(agents_info: list[dict[str, Any]]) -> None:
    """Register agents from the orchestrator.

    Called during application startup to populate the agent registry.

    Args:
        agents_info: List of agent information dictionaries from the orchestrator.
    """
    for info in agents_info:
        _agent_registry[info["name"]] = {
            "info": info,
            "config": {},
        }
    logger.info("Registered %d agents", len(_agent_registry))


@router.get(
    "",
    response_model=list[AgentInfo],
    summary="List all agents",
    description="Get information about all registered agents in the system.",
)
async def list_agents() -> list[AgentInfo]:
    """List all registered agents.

    Returns information about each agent including name, type,
    description, and current status.

    Returns:
        list[AgentInfo]: List of agent information objects.
    """
    agents = []
    for name, data in _agent_registry.items():
        info = data["info"]
        agents.append(
            AgentInfo(
                name=info.get("name", name),
                agent_type=AgentType(info.get("type", "planner")),
                description=info.get("description", ""),
                status=AgentStatus.IDLE,
                tools=info.get("tools", []),
            )
        )
    return agents


@router.get(
    "/{agent_id}",
    response_model=AgentInfo,
    summary="Get agent details",
    description="Get detailed information about a specific agent.",
)
async def get_agent(agent_id: str) -> AgentInfo:
    """Get detailed information about a specific agent.

    Args:
        agent_id: The agent's name/identifier.

    Returns:
        AgentInfo: Detailed agent information.

    Raises:
        HTTPException: If the agent is not found.
    """
    agent_data = _agent_registry.get(agent_id)
    if not agent_data:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    info = agent_data["info"]
    return AgentInfo(
        name=info.get("name", agent_id),
        agent_type=AgentType(info.get("type", "planner")),
        description=info.get("description", ""),
        status=AgentStatus.IDLE,
        tools=info.get("tools", []),
    )


@router.post(
    "/{agent_id}/config",
    response_model=dict[str, Any],
    summary="Update agent configuration",
    description="Update the runtime configuration of a specific agent.",
)
async def update_agent_config(
    agent_id: str,
    config_update: AgentConfigUpdate,
) -> dict[str, Any]:
    """Update an agent's configuration at runtime.

    Args:
        agent_id: The agent's name/identifier.
        config_update: Configuration fields to update.

    Returns:
        dict: Updated configuration.

    Raises:
        HTTPException: If the agent is not found or update fails.
    """
    agent_data = _agent_registry.get(agent_id)
    if not agent_data:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    try:
        # Update only non-None fields
        update_data = config_update.model_dump(exclude_none=True)
        agent_data["config"].update(update_data)

        logger.info("Updated configuration for agent '%s': %s", agent_id, update_data)

        return {
            "agent_id": agent_id,
            "updated_fields": list(update_data.keys()),
            "config": agent_data["config"],
        }
    except Exception as e:
        logger.error("Failed to update agent config: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Configuration update failed: {str(e)}") from e
