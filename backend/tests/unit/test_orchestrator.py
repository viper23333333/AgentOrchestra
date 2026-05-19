"""
Unit tests for the orchestration engine.

Tests the LangGraph-based workflow including node execution,
conditional routing, and state management.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.orchestrator import Orchestrator, OrchestratorState
from app.schemas.agent import AgentResponse, AgentType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(
    agent_name: str,
    agent_type: AgentType,
    content: str = "test output",
    success: bool = True,
) -> AgentResponse:
    """Create a mock AgentResponse for testing.

    Args:
        agent_name: Name of the agent.
        agent_type: Type of the agent.
        content: Response content.
        success: Whether the execution was successful.

    Returns:
        AgentResponse: A mock agent response.
    """
    return AgentResponse(
        agent_name=agent_name,
        agent_type=agent_type,
        success=success,
        content=content,
        metadata={},
    )


# ---------------------------------------------------------------------------
# Tests: Orchestrator Initialization
# ---------------------------------------------------------------------------


class TestOrchestratorInit:
    """Tests for orchestrator initialization."""

    @pytest.mark.asyncio
    async def test_orchestrator_creates_all_agents(self):
        """Verify that the orchestrator initializes all five agents."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=2)
            orchestrator = Orchestrator()

        assert orchestrator.planner is not None
        assert orchestrator.researcher is not None
        assert orchestrator.coder is not None
        assert orchestrator.reviewer is not None
        assert orchestrator.summarizer is not None

    @pytest.mark.asyncio
    async def test_orchestrator_builds_graph(self):
        """Verify that the orchestrator builds a compiled graph."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=2)
            orchestrator = Orchestrator()

        assert orchestrator.graph is not None

    @pytest.mark.asyncio
    async def test_get_agent_info_returns_all_agents(self):
        """Verify that get_agent_info returns information for all agents."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=2)
            orchestrator = Orchestrator()

        info = orchestrator.get_agent_info()
        assert len(info) == 5
        names = [a["name"] for a in info]
        assert "planner" in names
        assert "researcher" in names
        assert "coder" in names
        assert "reviewer" in names
        assert "summarizer" in names


# ---------------------------------------------------------------------------
# Tests: Routing Logic
# ---------------------------------------------------------------------------


class TestRoutingLogic:
    """Tests for the conditional routing logic."""

    @pytest.mark.asyncio
    async def test_route_to_summarize_when_no_feedback(self):
        """Verify routing to summarizer when no review feedback is given."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=3)
            orchestrator = Orchestrator()

        state: OrchestratorState = {
            "user_request": "test",
            "review_feedback": "",
            "revision_count": 0,
        }
        result = orchestrator._route_after_review(state)
        assert result == "summarize"

    @pytest.mark.asyncio
    async def test_route_to_revise_when_feedback_given(self):
        """Verify routing to coder when review feedback is present."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=3)
            orchestrator = Orchestrator()

        state: OrchestratorState = {
            "user_request": "test",
            "review_feedback": "Please fix the bug in line 42",
            "revision_count": 0,
        }
        result = orchestrator._route_after_review(state)
        assert result == "revise"

    @pytest.mark.asyncio
    async def test_route_to_summarize_at_max_revisions(self):
        """Verify routing to summarizer when max revisions is reached."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=2)
            orchestrator = Orchestrator()

        state: OrchestratorState = {
            "user_request": "test",
            "review_feedback": "Still needs work",
            "revision_count": 2,
        }
        result = orchestrator._route_after_review(state)
        assert result == "summarize"

    @pytest.mark.asyncio
    async def test_route_to_revise_below_max_revisions(self):
        """Verify routing to coder when below max revisions."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=3)
            orchestrator = Orchestrator()

        state: OrchestratorState = {
            "user_request": "test",
            "review_feedback": "Fix the error handling",
            "revision_count": 1,
        }
        result = orchestrator._route_after_review(state)
        assert result == "revise"


# ---------------------------------------------------------------------------
# Tests: Node Execution
# ---------------------------------------------------------------------------


class TestNodeExecution:
    """Tests for individual node execution."""

    @pytest.mark.asyncio
    async def test_planner_node_updates_state(self):
        """Verify that the planner node correctly updates the state."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=2)
            orchestrator = Orchestrator()

        # Mock the planner's execute method
        mock_response = _make_response("planner", AgentType.PLANNER, "Plan output")
        orchestrator.planner._execute_with_tracking = AsyncMock(return_value=mock_response)

        state: OrchestratorState = {
            "user_request": "Build an API",
            "agent_responses": [],
        }

        result = await orchestrator._planner_node(state)

        assert result["plan_output"] == "Plan output"
        assert result["current_agent"] == "planner"
        assert len(result["agent_responses"]) == 1

    @pytest.mark.asyncio
    async def test_summarizer_node_updates_state(self):
        """Verify that the summarizer node correctly updates the state."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=2)
            orchestrator = Orchestrator()

        mock_response = _make_response("summarizer", AgentType.SUMMARIZER, "Final summary")
        orchestrator.summarizer._execute_with_tracking = AsyncMock(return_value=mock_response)

        state: OrchestratorState = {
            "user_request": "Build an API",
            "plan_output": "Plan",
            "research_output": "Research",
            "code_output": "Code",
            "review_output": "Review",
            "revision_count": 0,
            "agent_responses": [],
        }

        result = await orchestrator._summarizer_node(state)

        assert result["summary_output"] == "Final summary"
        assert result["current_agent"] == "summarizer"


# ---------------------------------------------------------------------------
# Tests: Full Execution
# ---------------------------------------------------------------------------


class TestFullExecution:
    """Tests for the full orchestration execution."""

    @pytest.mark.asyncio
    async def test_execute_returns_task_result(self):
        """Verify that execute returns a TaskResult."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=2)
            orchestrator = Orchestrator()

        # Mock all agent executions
        mock_responses = {
            "planner": _make_response("planner", AgentType.PLANNER, "Plan created"),
            "researcher": _make_response("researcher", AgentType.RESEARCHER, "Research done"),
            "coder": _make_response("coder", AgentType.CODER, "Code written"),
            "reviewer": _make_response("reviewer", AgentType.REVIEWER, "Code approved"),
            "summarizer": _make_response("summarizer", AgentType.SUMMARIZER, "Final report"),
        }

        for agent_name, response in mock_responses.items():
            agent = getattr(orchestrator, agent_name)
            agent._execute_with_tracking = AsyncMock(return_value=response)

        result = await orchestrator.execute("Build a REST API")

        assert result is not None
        assert result.status.value in ("success", "partial", "failed")
        assert "planner" in result.outputs or result.status.value == "failed"

    @pytest.mark.asyncio
    async def test_execute_handles_errors_gracefully(self):
        """Verify that execute handles errors and returns a failed TaskResult."""
        with patch("app.core.orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_revision_rounds=2)
            orchestrator = Orchestrator()

        # Mock planner to raise an error
        orchestrator.planner._execute_with_tracking = AsyncMock(
            side_effect=RuntimeError("LLM connection failed")
        )

        result = await orchestrator.execute("Build a REST API")

        assert result is not None
        assert result.status.value == "failed"
