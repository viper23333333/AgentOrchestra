"""
Coder Agent - Writes code based on plans and research.

The coder agent is responsible for implementing solutions, writing
code, and creating scripts based on the execution plan and research
findings provided by other agents.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.agent import AgentConfig, AgentResponse, AgentType

logger = logging.getLogger(__name__)

CODER_SYSTEM_PROMPT = """You are an expert software engineer in a multi-agent AI system called AgentOrchestra.

Your role is to:
1. Read and understand the execution plan and research findings
2. Write clean, well-structured, and efficient code
3. Follow best practices and coding standards
4. Include appropriate error handling and documentation
5. Write tests when applicable

Coding Standards:
- Use Python 3.11+ features (type hints, match statements, etc.)
- Follow PEP 8 style guidelines
- Include docstrings (Google style) for all functions and classes
- Handle errors gracefully with descriptive messages
- Use meaningful variable and function names
- Keep functions focused and concise (single responsibility)
- Add inline comments for complex logic

Output Format:
When writing code, use markdown code blocks with the appropriate language tag.
For example:
```python
def example_function(param: str) -> str:
    \"\"\"Example function with docstring.\"\"\"
    return param.upper()
```

If multiple files are needed, clearly label each file:
**File: filename.py**
```python
# code here
```"""


class CoderAgent(BaseAgent):
    """Coder agent that writes and implements code solutions.

    This agent takes the execution plan and research data, then
    produces working code implementations. It focuses on writing
    clean, well-documented, and production-ready code.

    Attributes:
        name: Agent identifier ("coder").
        description: Human-readable description.
        role: Agent's role in the workflow.
    """

    @property
    def name(self) -> str:
        """Return the agent's name.

        Returns:
            str: "coder"
        """
        return "coder"

    @property
    def description(self) -> str:
        """Return the agent's description.

        Returns:
            str: Description of the coder's capabilities.
        """
        return (
            "Writes clean, well-structured code based on execution plans "
            "and research findings. Follows best practices and coding standards."
        )

    @property
    def role(self) -> str:
        """Return the agent's role.

        Returns:
            str: "code_implementation"
        """
        return "code_implementation"

    @property
    def agent_type(self) -> AgentType:
        """Return the agent's type.

        Returns:
            AgentType: AgentType.CODER
        """
        return AgentType.CODER

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for the coder.

        Returns:
            str: The coder's system prompt.
        """
        return self._config.system_prompt or CODER_SYSTEM_PROMPT

    def _default_config(self) -> AgentConfig:
        """Return default configuration for the coder agent.

        Returns:
            AgentConfig: Default configuration.
        """
        return AgentConfig(
            name="coder",
            agent_type=AgentType.CODER,
            description=self.description,
            tools=["code_executor"],
            temperature=0.2,  # Low temperature for precise code generation
            max_tokens=8192,  # Higher token limit for code output
        )

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResponse:
        """Write code based on the task plan and research context.

        Args:
            task: The coding task description.
            context: Additional context including plan and research findings.

        Returns:
            AgentResponse: Response containing the generated code.
        """
        # Build a comprehensive prompt with all available context
        prompt_parts = [f"## Coding Task\n{task}"]

        # Add plan context if available
        plan = context.get("plan")
        if plan:
            plan_text = plan.get("objective", str(plan)) if isinstance(plan, dict) else str(plan)
            prompt_parts.append(f"## Execution Plan\n{plan_text}")

        # Add research context if available
        research = context.get("research")
        if research:
            prompt_parts.append(f"## Research Findings\n{research}")

        # Add review feedback if this is a revision
        review_feedback = context.get("review_feedback")
        if review_feedback:
            prompt_parts.append(
                f"## Review Feedback (Please address these issues)\n{review_feedback}"
            )

        prompt = "\n\n".join(prompt_parts)
        prompt += (
            "\n\nPlease implement the solution following the coding standards "
            "outlined in your instructions. Provide complete, runnable code."
        )

        response_text = await self.llm.chat(prompt, system_prompt=self.system_prompt)

        # Extract code artifacts from the response
        artifacts = self._extract_code_artifacts(response_text)

        return AgentResponse(
            agent_name=self.name,
            agent_type=self.agent_type,
            success=True,
            content=response_text,
            artifacts=artifacts,
            metadata={
                "artifact_count": len(artifacts),
                "is_revision": bool(review_feedback),
            },
        )

    def _extract_code_artifacts(self, text: str) -> list[dict[str, Any]]:
        """Extract code blocks from the response text.

        Parses markdown code blocks and returns them as artifacts.

        Args:
            text: The response text containing code blocks.

        Returns:
            list[dict]: List of code artifacts with language and content.
        """
        artifacts: list[dict[str, Any]] = []
        in_code_block = False
        current_language = ""
        current_code: list[str] = []
        current_filename = ""

        for line in text.split("\n"):
            if line.strip().startswith("**File:") and ":" in line:
                # Extract filename
                current_filename = line.strip().replace("**File:", "").replace("**", "").strip()
                continue

            if line.strip().startswith("```"):
                if not in_code_block:
                    # Start of code block
                    in_code_block = True
                    lang = line.strip()[3:].strip()
                    current_language = lang if lang else "text"
                    current_code = []
                else:
                    # End of code block
                    in_code_block = False
                    code_content = "\n".join(current_code)
                    if code_content.strip():
                        artifact: dict[str, Any] = {
                            "type": "code",
                            "language": current_language,
                            "content": code_content,
                        }
                        if current_filename:
                            artifact["filename"] = current_filename
                        artifacts.append(artifact)
                    current_language = ""
                    current_code = []
                    current_filename = ""
            elif in_code_block:
                current_code.append(line)

        return artifacts
