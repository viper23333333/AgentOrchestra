"""
Core orchestration engine using LangGraph.

Implements a multi-agent workflow using LangGraph's StateGraph with
conditional routing. The workflow follows: planner -> researcher -> coder
-> reviewer -> summarizer, with the reviewer able to send work back to
the coder for revisions.
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.coder.agent import CoderAgent
from app.agents.planner.agent import PlannerAgent
from app.agents.researcher.agent import ResearcherAgent
from app.agents.reviewer.agent import ReviewerAgent
from app.agents.summarizer.agent import SummarizerAgent
from app.config.settings import get_settings
from app.schemas.message import TaskResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State Definition
# ---------------------------------------------------------------------------


class OrchestratorState(TypedDict, total=False):
    """State definition for the orchestration workflow.

    This TypedDict defines the shared state that flows through all
    nodes in the LangGraph workflow. Each agent node reads from and
    writes to this state.

    Attributes:
        user_request: The original user request.
        plan_output: Output from the planner agent.
        research_output: Output from the researcher agent.
        code_output: Output from the coder agent.
        review_output: Output from the reviewer agent.
        summary_output: Output from the summarizer agent.
        review_feedback: Feedback from the reviewer for code revision.
        revision_count: Number of code revision iterations.
        max_revisions: Maximum allowed revision rounds.
        agent_responses: List of all agent responses for tracking.
        error: Error message if the workflow failed.
        current_agent: Name of the currently executing agent.
    """

    user_request: str
    plan_output: str
    research_output: str
    code_output: str
    review_output: str
    summary_output: str
    review_feedback: str
    revision_count: int
    max_revisions: int
    agent_responses: list[dict[str, Any]]
    error: str | None
    current_agent: str


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class Orchestrator:
    """Multi-agent orchestration engine powered by LangGraph.

    Coordinates the execution of multiple agents in a structured workflow.
    The default workflow is: planner -> researcher -> coder -> reviewer
    -> (conditional: coder or summarizer) -> summarizer.

    The reviewer can route back to the coder if the code needs revision,
    up to a configurable maximum number of rounds.

    Attributes:
        planner: The planner agent instance.
        researcher: The researcher agent instance.
        coder: The coder agent instance.
        reviewer: The reviewer agent instance.
        summarizer: The summarizer agent instance.
        graph: The compiled LangGraph StateGraph.

    Example:
        >>> orchestrator = Orchestrator()
        >>> result = await orchestrator.execute("Build a REST API")
        >>> print(result.summary)
    """

    def __init__(self, provider: str | None = None) -> None:
        """Initialize the orchestrator with all agents.

        Args:
            provider: LLM provider override for all agents.
        """
        settings = get_settings()

        # Initialize all agents
        self.planner = PlannerAgent(provider=provider)
        self.researcher = ResearcherAgent(provider=provider)
        self.coder = CoderAgent(provider=provider)
        self.reviewer = ReviewerAgent(provider=provider)
        self.summarizer = SummarizerAgent(provider=provider)

        self.max_revisions = settings.max_revision_rounds

        # Build the workflow graph
        self.graph = self._build_graph()
        logger.info("Orchestrator initialized (max_revisions=%d)", self.max_revisions)

    def _build_graph(self) -> StateGraph:
        """Build and compile the LangGraph workflow.

        Constructs the state graph with nodes for each agent and
        conditional edges for the review routing logic.

        Returns:
            StateGraph: The compiled workflow graph.
        """
        workflow = StateGraph(OrchestratorState)

        # Add nodes (one per agent)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("coder", self._coder_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("summarizer", self._summarizer_node)

        # Set entry point
        workflow.set_entry_point("planner")

        # Define edges
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "coder")
        workflow.add_edge("coder", "reviewer")

        # Conditional edge: reviewer -> coder (if needs revision) or summarizer
        workflow.add_conditional_edges(
            "reviewer",
            self._route_after_review,
            {
                "revise": "coder",
                "summarize": "summarizer",
            },
        )

        workflow.add_edge("summarizer", END)

        return workflow.compile()

    # -----------------------------------------------------------------------
    # Node Functions
    # -----------------------------------------------------------------------

    async def _planner_node(self, state: OrchestratorState) -> dict[str, Any]:
        """Execute the planner agent.

        Args:
            state: Current workflow state.

        Returns:
            dict: Updated state fields from the planner.
        """
        logger.info("Executing planner node")
        response = await self.planner._execute_with_tracking(
            task=state["user_request"],
            context={},
        )

        return {
            "plan_output": response.content,
            "current_agent": "planner",
            "agent_responses": state.get("agent_responses", []) + [response.model_dump()],
        }

    async def _researcher_node(self, state: OrchestratorState) -> dict[str, Any]:
        """Execute the researcher agent.

        Args:
            state: Current workflow state.

        Returns:
            dict: Updated state fields from the researcher.
        """
        logger.info("Executing researcher node")
        response = await self.researcher._execute_with_tracking(
            task=state["user_request"],
            context={"plan": state.get("plan_output", "")},
        )

        return {
            "research_output": response.content,
            "current_agent": "researcher",
            "agent_responses": state.get("agent_responses", []) + [response.model_dump()],
        }

    async def _coder_node(self, state: OrchestratorState) -> dict[str, Any]:
        """Execute the coder agent.

        Args:
            state: Current workflow state.

        Returns:
            dict: Updated state fields from the coder.
        """
        logger.info("Executing coder node (revision #%d)", state.get("revision_count", 0))
        response = await self.coder._execute_with_tracking(
            task=state["user_request"],
            context={
                "plan": state.get("plan_output", ""),
                "research": state.get("research_output", ""),
                "review_feedback": state.get("review_feedback", ""),
            },
        )

        return {
            "code_output": response.content,
            "current_agent": "coder",
            "agent_responses": state.get("agent_responses", []) + [response.model_dump()],
        }

    async def _reviewer_node(self, state: OrchestratorState) -> dict[str, Any]:
        """Execute the reviewer agent.

        Args:
            state: Current workflow state.

        Returns:
            dict: Updated state fields from the reviewer.
        """
        logger.info("Executing reviewer node")
        response = await self.reviewer._execute_with_tracking(
            task="Review the code",
            context={
                "code": state.get("code_output", ""),
                "original_task": state["user_request"],
            },
        )

        return {
            "review_output": response.content,
            "review_feedback": response.content if response.metadata.get("needs_revision") else "",
            "current_agent": "reviewer",
            "agent_responses": state.get("agent_responses", []) + [response.model_dump()],
        }

    async def _summarizer_node(self, state: OrchestratorState) -> dict[str, Any]:
        """Execute the summarizer agent.

        Args:
            state: Current workflow state.

        Returns:
            dict: Updated state fields from the summarizer.
        """
        logger.info("Executing summarizer node")
        response = await self.summarizer._execute_with_tracking(
            task=state["user_request"],
            context={
                "plan_output": state.get("plan_output", ""),
                "research_output": state.get("research_output", ""),
                "code_output": state.get("code_output", ""),
                "review_output": state.get("review_output", ""),
                "revision_count": state.get("revision_count", 0),
            },
        )

        return {
            "summary_output": response.content,
            "current_agent": "summarizer",
            "agent_responses": state.get("agent_responses", []) + [response.model_dump()],
        }

    # -----------------------------------------------------------------------
    # Routing Functions
    # -----------------------------------------------------------------------

    def _route_after_review(self, state: OrchestratorState) -> str:
        """Determine the next step after code review.

        Routes back to the coder if the review indicates revision is needed
        and the maximum revision count has not been reached.

        Args:
            state: Current workflow state.

        Returns:
            str: "revise" if code needs revision, "summarize" otherwise.
        """
        review_feedback = state.get("review_feedback", "")
        revision_count = state.get("revision_count", 0)
        max_revisions = state.get("max_revisions", self.max_revisions)

        if review_feedback and revision_count < max_revisions:
            logger.info(
                "Code needs revision (round %d/%d)",
                revision_count + 1,
                max_revisions,
            )
            return "revise"

        if review_feedback and revision_count >= max_revisions:
            logger.warning(
                "Max revisions (%d) reached, proceeding to summarizer",
                max_revisions,
            )

        return "summarize"

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    async def execute(self, user_request: str) -> TaskResult:
        """Execute the full orchestration workflow.

        Runs the complete agent pipeline: plan -> research -> code ->
        review -> (optional revision loop) -> summarize.

        Args:
            user_request: The user's task or request.

        Returns:
            TaskResult: The final task result with all agent outputs.
        """
        start_time = time.perf_counter()

        initial_state: OrchestratorState = {
            "user_request": user_request,
            "plan_output": "",
            "research_output": "",
            "code_output": "",
            "review_output": "",
            "summary_output": "",
            "review_feedback": "",
            "revision_count": 0,
            "max_revisions": self.max_revisions,
            "agent_responses": [],
            "error": None,
            "current_agent": "",
        }

        try:
            # Execute the graph
            final_state = await self.graph.ainvoke(initial_state)

            # Handle revision count in the state updates
            # (The graph nodes don't directly increment revision_count,
            #  so we handle it via the routing logic)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Build the task result
            agent_responses = final_state.get("agent_responses", [])
            outputs: dict[str, str] = {}
            code_artifacts: list[dict[str, Any]] = []

            for resp_data in agent_responses:
                agent_name = resp_data.get("agent_name", "unknown")
                outputs[agent_name] = resp_data.get("content", "")

                # Collect code artifacts from the coder
                if agent_name == "coder":
                    code_artifacts.extend(resp_data.get("artifacts", []))

            result = TaskResult(
                task_id=hash(user_request) % (10**12),  # Deterministic but simple ID
                summary=final_state.get("summary_output", ""),
                outputs=outputs,
                code_artifacts=code_artifacts,
                status=TaskResult.Status.SUCCESS,
                total_execution_time_ms=elapsed_ms,
            )

            logger.info(
                "Orchestration completed in %.1fms (agents=%d)",
                elapsed_ms,
                len(agent_responses),
            )
            return result

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error("Orchestration failed: %s", str(e), exc_info=True)

            return TaskResult(
                task_id=hash(user_request) % (10**12),
                summary="",
                status=TaskResult.Status.FAILED,
                total_execution_time_ms=elapsed_ms,
            )

    async def execute_stream(self, user_request: str) -> AsyncIterator[dict[str, Any]]:
        """Execute the workflow with streaming output.

        Yields intermediate results from each agent as they complete,
        allowing the client to see progress in real-time.

        Args:
            user_request: The user's task or request.

        Yields:
            dict: Event data with agent name, content, and event type.
        """
        start_time = time.perf_counter()

        initial_state: OrchestratorState = {
            "user_request": user_request,
            "plan_output": "",
            "research_output": "",
            "code_output": "",
            "review_output": "",
            "summary_output": "",
            "review_feedback": "",
            "revision_count": 0,
            "max_revisions": self.max_revisions,
            "agent_responses": [],
            "error": None,
            "current_agent": "",
        }

        try:
            # Stream events from the graph
            async for event in self.graph.astream_events(initial_state, version="v1"):
                event_type = event.get("event", "")
                event_data = event.get("data", {})

                if event_type == "on_chain_end":
                    # A node has completed
                    name = event.get("name", "")
                    if name in ("planner", "researcher", "coder", "reviewer", "summarizer"):
                        output = event_data.get("output", {})
                        yield {
                            "event": "agent_complete",
                            "agent": name,
                            "content": output.get(name, "") if isinstance(output, dict) else "",
                            "timestamp": time.time(),
                        }

            yield {
                "event": "workflow_complete",
                "execution_time_ms": (time.perf_counter() - start_time) * 1000,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error("Streaming orchestration failed: %s", str(e), exc_info=True)
            yield {
                "event": "error",
                "error": str(e),
                "timestamp": time.time(),
            }

    def get_agent_info(self) -> list[dict[str, Any]]:
        """Get information about all registered agents.

        Returns:
            list[dict]: List of agent information dictionaries.
        """
        agents = [self.planner, self.researcher, self.coder, self.reviewer, self.summarizer]
        return [
            {
                "name": agent.name,
                "type": agent.agent_type.value,
                "description": agent.description,
                "role": agent.role,
            }
            for agent in agents
        ]
