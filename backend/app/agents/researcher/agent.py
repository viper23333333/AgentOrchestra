"""
Researcher Agent - Searches for information and collects data.

The researcher agent gathers information from web searches and other
sources to support the task execution. It analyzes findings and
provides structured research summaries.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.agent import AgentConfig, AgentResponse, AgentType
from app.services.tools.search import SearchTool, SearchToolError

logger = logging.getLogger(__name__)

RESEARCHER_SYSTEM_PROMPT = """You are an expert research agent in a multi-agent AI system called AgentOrchestra.

Your role is to:
1. Understand what information is needed for the task
2. Formulate effective search queries
3. Analyze search results and extract relevant information
4. Synthesize findings into a structured research summary
5. Identify gaps in the research and suggest follow-up queries

Guidelines:
- Focus on factual, up-to-date information
- Cite sources when possible (URLs, titles)
- Organize findings logically
- Highlight key insights and actionable data
- Be thorough but concise
- If search results are insufficient, clearly state what additional information is needed

Output format:
Provide a structured research summary with:
1. Key Findings: Main discoveries
2. Details: Supporting information organized by topic
3. Sources: List of sources consulted
4. Gaps: What information is still missing (if any)"""


class ResearcherAgent(BaseAgent):
    """Researcher agent that searches for and analyzes information.

    This agent uses web search tools to gather information relevant
    to the task, analyzes the results, and produces structured
    research summaries for other agents to use.

    Attributes:
        name: Agent identifier ("researcher").
        description: Human-readable description.
        role: Agent's role in the workflow.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        provider: str | None = None,
    ) -> None:
        """Initialize the researcher agent.

        Args:
            config: Agent configuration.
            provider: LLM provider override.
        """
        super().__init__(config=config, provider=provider)
        self._search_tool = SearchTool()

    @property
    def name(self) -> str:
        """Return the agent's name.

        Returns:
            str: "researcher"
        """
        return "researcher"

    @property
    def description(self) -> str:
        """Return the agent's description.

        Returns:
            str: Description of the researcher's capabilities.
        """
        return (
            "Searches the web for information, collects relevant data, "
            "analyzes findings, and produces structured research summaries."
        )

    @property
    def role(self) -> str:
        """Return the agent's role.

        Returns:
            str: "information_research"
        """
        return "information_research"

    @property
    def agent_type(self) -> AgentType:
        """Return the agent's type.

        Returns:
            AgentType: AgentType.RESEARCHER
        """
        return AgentType.RESEARCHER

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for the researcher.

        Returns:
            str: The researcher's system prompt.
        """
        return self._config.system_prompt or RESEARCHER_SYSTEM_PROMPT

    def _default_config(self) -> AgentConfig:
        """Return default configuration for the researcher agent.

        Returns:
            AgentConfig: Default configuration.
        """
        return AgentConfig(
            name="researcher",
            agent_type=AgentType.RESEARCHER,
            description=self.description,
            tools=["web_search"],
            temperature=0.3,
            max_tokens=4096,
        )

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResponse:
        """Research the given topic and produce a structured summary.

        Args:
            task: The research topic or question.
            context: Additional context including the task plan.

        Returns:
            AgentResponse: Response containing the research summary.
        """
        # Extract search queries from the task or generate them
        search_queries = self._extract_search_queries(task, context)

        # Execute searches
        all_results: list[str] = []
        for query in search_queries:
            try:
                search_response = await self._search_tool.search(query, num_results=5)
                results_text = "\n".join(
                    f"- [{r.title}]({r.url}): {r.snippet}"
                    for r in search_response.results
                )
                all_results.append(f"Query: {query}\nResults:\n{results_text}")
                logger.info(
                    "Research search completed: query='%s', results=%d",
                    query,
                    len(search_response.results),
                )
            except SearchToolError as e:
                logger.warning("Search failed for query '%s': %s", query, e)
                all_results.append(f"Query: {query}\nError: {e}")

        # Use LLM to analyze and synthesize the research
        research_data = "\n\n".join(all_results)
        prompt = (
            f"Research Task: {task}\n\n"
            f"Search Results:\n{research_data}\n\n"
            f"Please analyze these search results and provide a structured "
            f"research summary following the output format in your instructions."
        )

        response_text = await self.llm.chat(prompt, system_prompt=self.system_prompt)

        return AgentResponse(
            agent_name=self.name,
            agent_type=self.agent_type,
            success=True,
            content=response_text,
            metadata={
                "queries_executed": search_queries,
                "results_count": len(all_results),
            },
        )

    def _extract_search_queries(self, task: str, context: dict[str, Any]) -> list[str]:
        """Extract or generate search queries from the task.

        If the context contains a plan with research steps, extracts
        queries from those steps. Otherwise, generates queries from
        the task description.

        Args:
            task: The research task.
            context: Additional context.

        Returns:
            list[str]: List of search queries.
        """
        # Check if context has specific research queries
        if context.get("search_queries"):
            return context["search_queries"]

        # If there's a plan, look for research steps
        plan = context.get("plan")
        if plan and isinstance(plan, dict):
            steps = plan.get("steps", [])
            queries = [
                step.get("description", "")
                for step in steps
                if step.get("assigned_agent") == "researcher"
            ]
            if queries:
                return queries[:3]  # Limit to 3 queries

        # Generate queries from the task itself
        return [task]
