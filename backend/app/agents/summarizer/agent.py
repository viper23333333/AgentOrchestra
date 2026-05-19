"""
Summarizer Agent - Combines outputs and generates final reports.

The summarizer agent is the final agent in the orchestration workflow.
It aggregates outputs from all other agents, synthesizes the information,
and produces a comprehensive final report for the user.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.agent import AgentConfig, AgentResponse, AgentType

logger = logging.getLogger(__name__)

SUMMARIZER_SYSTEM_PROMPT = """You are an expert technical summarizer in a multi-agent AI system called AgentOrchestra.

Your role is to:
1. Aggregate and synthesize outputs from all agents in the workflow
2. Create a clear, well-structured final report
3. Highlight key findings, decisions, and outcomes
4. Present code solutions with explanations
5. Note any limitations or areas for further work

Report Structure:
## Summary
[Concise overview of what was accomplished]

## Approach
[Brief description of the approach taken]

## Key Findings
[Main discoveries and insights from research]

## Solution
[The implemented solution with code and explanations]

## Code Artifacts
[List of all code files produced with brief descriptions]

## Review Notes
[Summary of code review findings and quality assessment]

## Next Steps
[Suggested follow-up actions or improvements]

Guidelines:
- Be clear and concise
- Use markdown formatting for readability
- Include all relevant code artifacts
- Make the report actionable for the user
- If there were issues or limitations, be transparent about them"""


class SummarizerAgent(BaseAgent):
    """Summarizer agent that produces final reports.

    This agent takes all the outputs from the orchestration workflow
    (plan, research, code, review) and synthesizes them into a
    comprehensive, user-friendly final report.

    Attributes:
        name: Agent identifier ("summarizer").
        description: Human-readable description.
        role: Agent's role in the workflow.
    """

    @property
    def name(self) -> str:
        """Return the agent's name.

        Returns:
            str: "summarizer"
        """
        return "summarizer"

    @property
    def description(self) -> str:
        """Return the agent's description.

        Returns:
            str: Description of the summarizer's capabilities.
        """
        return (
            "Aggregates outputs from all agents, synthesizes information, "
            "and produces comprehensive final reports for the user."
        )

    @property
    def role(self) -> str:
        """Return the agent's role.

        Returns:
            str: "report_generation"
        """
        return "report_generation"

    @property
    def agent_type(self) -> AgentType:
        """Return the agent's type.

        Returns:
            AgentType: AgentType.SUMMARIZER
        """
        return AgentType.SUMMARIZER

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for the summarizer.

        Returns:
            str: The summarizer's system prompt.
        """
        return self._config.system_prompt or SUMMARIZER_SYSTEM_PROMPT

    def _default_config(self) -> AgentConfig:
        """Return default configuration for the summarizer agent.

        Returns:
            AgentConfig: Default configuration.
        """
        return AgentConfig(
            name="summarizer",
            agent_type=AgentType.SUMMARIZER,
            description=self.description,
            temperature=0.4,  # Moderate temperature for creative but structured output
            max_tokens=4096,
        )

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResponse:
        """Generate a final summary report from all agent outputs.

        Args:
            task: The original user request.
            context: Context containing outputs from all agents.

        Returns:
            AgentResponse: Response containing the final report.
        """
        # Build comprehensive prompt from all agent outputs
        prompt_parts = [
            f"## Original User Request\n{task}",
        ]

        # Add plan output
        plan_output = context.get("plan_output")
        if plan_output:
            prompt_parts.append(f"## Execution Plan\n{plan_output}")

        # Add research output
        research_output = context.get("research_output")
        if research_output:
            prompt_parts.append(f"## Research Findings\n{research_output}")

        # Add code output
        code_output = context.get("code_output")
        if code_output:
            prompt_parts.append(f"## Code Solution\n{code_output}")

        # Add review output
        review_output = context.get("review_output")
        if review_output:
            prompt_parts.append(f"## Code Review\n{review_output}")

        # Add revision history if any
        revision_count = context.get("revision_count", 0)
        if revision_count > 0:
            prompt_parts.append(
                f"## Note\nThis solution went through {revision_count} revision(s) "
                f"based on code review feedback."
            )

        prompt = "\n\n".join(prompt_parts)
        prompt += (
            "\n\nPlease create a comprehensive final report following "
            "the structure in your instructions."
        )

        response_text = await self.llm.chat(prompt, system_prompt=self.system_prompt)

        return AgentResponse(
            agent_name=self.name,
            agent_type=self.agent_type,
            success=True,
            content=response_text,
            metadata={
                "revision_count": revision_count,
                "has_plan": bool(plan_output),
                "has_research": bool(research_output),
                "has_code": bool(code_output),
                "has_review": bool(review_output),
            },
        )
