"""
Reviewer Agent - Reviews code quality and suggests improvements.

The reviewer agent examines code produced by the coder agent,
identifies issues, checks for best practices, and provides
actionable feedback for improvements.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.agent import AgentConfig, AgentResponse, AgentType

logger = logging.getLogger(__name__)

REVIEWER_SYSTEM_PROMPT = """You are a senior code reviewer in a multi-agent AI system called AgentOrchestra.

Your role is to:
1. Review code for correctness, efficiency, and readability
2. Identify bugs, security vulnerabilities, and edge cases
3. Check adherence to coding standards and best practices
4. Evaluate error handling and documentation quality
5. Provide actionable, specific improvement suggestions

Review Criteria:
- **Correctness**: Does the code do what it's supposed to do?
- **Code Quality**: Is it clean, readable, and well-structured?
- **Error Handling**: Are errors properly caught and handled?
- **Performance**: Are there obvious performance issues?
- **Security**: Are there security vulnerabilities?
- **Documentation**: Are functions and classes properly documented?
- **Testing**: Are there appropriate tests?
- **Best Practices**: Does it follow language-specific best practices?

Output Format:
Provide your review in this structure:
## Review Summary
[Overall assessment: APPROVED / NEEDS_REVISION / REJECTED]

## Issues Found
[List each issue with severity: CRITICAL / MAJOR / MINOR / SUGGESTION]

## Suggestions
[Specific, actionable improvement suggestions]

## Revised Code (if NEEDS_REVISION)
[Provide corrected code if there are critical or major issues]

Important:
- Be thorough but fair
- Focus on actionable feedback
- Prioritize critical and major issues
- If the code is good, say so and approve it"""


class ReviewerAgent(BaseAgent):
    """Reviewer agent that examines code quality and provides feedback.

    This agent reviews code produced by the coder agent, identifies
    issues, and determines whether the code needs revision. It can
    trigger the coder agent to make corrections if needed.

    Attributes:
        name: Agent identifier ("reviewer").
        description: Human-readable description.
        role: Agent's role in the workflow.
    """

    @property
    def name(self) -> str:
        """Return the agent's name.

        Returns:
            str: "reviewer"
        """
        return "reviewer"

    @property
    def description(self) -> str:
        """Return the agent's description.

        Returns:
            str: Description of the reviewer's capabilities.
        """
        return (
            "Reviews code quality, identifies bugs and issues, "
            "checks best practices compliance, and provides "
            "actionable improvement suggestions."
        )

    @property
    def role(self) -> str:
        """Return the agent's role.

        Returns:
            str: "code_review"
        """
        return "code_review"

    @property
    def agent_type(self) -> AgentType:
        """Return the agent's type.

        Returns:
            AgentType: AgentType.REVIEWER
        """
        return AgentType.REVIEWER

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for the reviewer.

        Returns:
            str: The reviewer's system prompt.
        """
        return self._config.system_prompt or REVIEWER_SYSTEM_PROMPT

    def _default_config(self) -> AgentConfig:
        """Return default configuration for the reviewer agent.

        Returns:
            AgentConfig: Default configuration.
        """
        return AgentConfig(
            name="reviewer",
            agent_type=AgentType.REVIEWER,
            description=self.description,
            temperature=0.2,  # Low temperature for consistent reviews
            max_tokens=4096,
        )

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResponse:
        """Review code and provide feedback.

        Args:
            task: The review task (typically "review the following code").
            context: Context containing the code to review and the original task.

        Returns:
            AgentResponse: Response containing the review result and verdict.
        """
        # Extract code from context
        code_to_review = context.get("code", "")
        original_task = context.get("original_task", task)

        if not code_to_review:
            return AgentResponse(
                agent_name=self.name,
                agent_type=self.agent_type,
                success=False,
                content="No code provided for review.",
                error="Missing code in context",
            )

        # Build the review prompt
        prompt = (
            f"## Original Task\n{original_task}\n\n"
            f"## Code to Review\n```\n{code_to_review}\n```\n\n"
            f"Please review this code thoroughly following the criteria "
            f"in your instructions. Provide your verdict and any "
            f"improvement suggestions."
        )

        response_text = await self.llm.chat(prompt, system_prompt=self.system_prompt)

        # Determine the review verdict
        verdict = self._extract_verdict(response_text)

        return AgentResponse(
            agent_name=self.name,
            agent_type=self.agent_type,
            success=True,
            content=response_text,
            metadata={
                "verdict": verdict,
                "needs_revision": verdict == "NEEDS_REVISION",
                "rejected": verdict == "REJECTED",
            },
        )

    def _extract_verdict(self, review_text: str) -> str:
        """Extract the review verdict from the response.

        Looks for APPROVED, NEEDS_REVISION, or REJECTED keywords
        in the review text.

        Args:
            review_text: The full review response text.

        Returns:
            str: The verdict ("APPROVED", "NEEDS_REVISION", or "REJECTED").
        """
        text_upper = review_text.upper()

        if "REJECTED" in text_upper:
            return "REJECTED"
        elif "NEEDS_REVISION" in text_upper or "NEEDS REVISION" in text_upper:
            return "NEEDS_REVISION"
        else:
            return "APPROVED"
