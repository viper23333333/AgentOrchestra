"""
Planner Agent - Analyzes user requirements and creates execution plans.

The planner agent is the first agent in the orchestration workflow.
It analyzes the user's request, breaks it down into subtasks,
and creates a structured execution plan for other agents to follow.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.agent import AgentConfig, AgentResponse, AgentType
from app.schemas.message import TaskPlan, TaskStep

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are an expert task planner in a multi-agent AI system called AgentOrchestra.

Your role is to:
1. Analyze the user's request thoroughly
2. Break down complex tasks into clear, actionable subtasks
3. Assign each subtask to the most appropriate agent (researcher, coder, reviewer)
4. Define dependencies between subtasks
5. Estimate the complexity of the overall task

Available agents:
- researcher: Searches for information, collects data, analyzes findings
- coder: Writes code, implements solutions, creates scripts
- reviewer: Reviews code quality, identifies issues, suggests improvements
- summarizer: Combines outputs, generates final reports

Output your plan as a JSON object with this exact structure:
{
    "objective": "High-level objective of the plan",
    "steps": [
        {
            "step_number": 1,
            "description": "Clear description of what needs to be done",
            "assigned_agent": "agent_name",
            "dependencies": [],
            "status": "pending"
        }
    ],
    "estimated_complexity": 5
}

Rules:
- Steps should be ordered logically (dependencies first)
- Each step should be specific and actionable
- Assign the right agent for each step
- Keep the plan concise but comprehensive
- Always output valid JSON"""


class PlannerAgent(BaseAgent):
    """Planner agent that analyzes requirements and creates execution plans.

    This agent is responsible for understanding the user's intent,
    decomposing complex requests into manageable subtasks, and
    creating a structured plan that guides the entire workflow.

    Attributes:
        name: Agent identifier ("planner").
        description: Human-readable description.
        role: Agent's role in the workflow.
    """

    @property
    def name(self) -> str:
        """Return the agent's name.

        Returns:
            str: "planner"
        """
        return "planner"

    @property
    def description(self) -> str:
        """Return the agent's description.

        Returns:
            str: Description of the planner's capabilities.
        """
        return (
            "Analyzes user requirements, decomposes tasks into subtasks, "
            "and creates structured execution plans for the multi-agent team."
        )

    @property
    def role(self) -> str:
        """Return the agent's role.

        Returns:
            str: "task_planning"
        """
        return "task_planning"

    @property
    def agent_type(self) -> AgentType:
        """Return the agent's type.

        Returns:
            AgentType: AgentType.PLANNER
        """
        return AgentType.PLANNER

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for the planner.

        Returns:
            str: The planner's system prompt.
        """
        return self._config.system_prompt or PLANNER_SYSTEM_PROMPT

    def _default_config(self) -> AgentConfig:
        """Return default configuration for the planner agent.

        Returns:
            AgentConfig: Default configuration.
        """
        return AgentConfig(
            name="planner",
            agent_type=AgentType.PLANNER,
            description=self.description,
            temperature=0.3,  # Lower temperature for more structured output
            max_tokens=4096,
        )

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResponse:
        """Analyze the task and create an execution plan.

        Args:
            task: The user's request or task description.
            context: Additional context (e.g., conversation history).

        Returns:
            AgentResponse: Response containing the structured task plan.
        """
        # Build the prompt with context
        context_info = ""
        if context.get("conversation_history"):
            context_info = f"\n\nPrevious conversation context:\n{context['conversation_history']}"

        prompt = (
            f"Analyze the following user request and create a detailed execution plan:\n\n"
            f"User Request: {task}{context_info}\n\n"
            f"Respond with ONLY the JSON plan, no additional text."
        )

        response_text = await self.llm.chat(prompt, system_prompt=self.system_prompt)

        # Parse the JSON response
        try:
            plan_data = self._parse_plan_json(response_text)
            plan = TaskPlan(
                user_request=task,
                objective=plan_data.get("objective", ""),
                steps=[
                    TaskStep(
                        step_number=step.get("step_number", i + 1),
                        description=step.get("description", ""),
                        assigned_agent=step.get("assigned_agent", "coder"),
                        dependencies=step.get("dependencies", []),
                        status=TaskStep.Status.PENDING,
                    )
                    for i, step in enumerate(plan_data.get("steps", []))
                ],
                estimated_complexity=plan_data.get("estimated_complexity", 5),
            )

            return AgentResponse(
                agent_name=self.name,
                agent_type=self.agent_type,
                success=True,
                content=response_text,
                artifacts=[plan.model_dump()],
                metadata={"plan_id": plan.id, "step_count": len(plan.steps)},
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse plan JSON: %s. Returning raw text.", e)
            return AgentResponse(
                agent_name=self.name,
                agent_type=self.agent_type,
                success=True,
                content=response_text,
                metadata={"parse_error": str(e)},
            )

    def _parse_plan_json(self, text: str) -> dict[str, Any]:
        """Extract and parse JSON from the LLM response.

        Handles cases where the LLM wraps JSON in markdown code blocks.

        Args:
            text: Raw LLM response text.

        Returns:
            dict: Parsed JSON object.

        Raises:
            json.JSONDecodeError: If the text cannot be parsed as JSON.
        """
        # Try direct JSON parse first
        text = text.strip()
        if text.startswith("{"):
            return json.loads(text)

        # Try extracting from markdown code blocks
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            return json.loads(text[start:end].strip())

        if "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            return json.loads(text[start:end].strip())

        # Last resort: find the first { and last }
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
