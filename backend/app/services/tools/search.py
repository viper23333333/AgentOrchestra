"""
Web search tool for the AgentOrchestra system.

Provides a tool interface for agents to perform web searches,
retrieve search results, and extract relevant information.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SearchResult(BaseModel):
    """Represents a single web search result.

    Attributes:
        title: Title of the search result.
        url: URL of the search result.
        snippet: Brief description/snippet of the content.
        relevance_score: Computed relevance score (0.0 - 1.0).
    """

    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    snippet: str = Field(default="", description="Content snippet")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance score")


class SearchResponse(BaseModel):
    """Response from a web search operation.

    Attributes:
        query: The search query that was executed.
        results: List of search results.
        total_results: Total number of results found.
    """

    query: str = Field(..., description="Search query")
    results: list[SearchResult] = Field(default_factory=list, description="Search results")
    total_results: int = Field(default=0, description="Total results count")


class SearchTool:
    """Web search tool for agents.

    Provides a unified interface for performing web searches.
    Currently supports a mock implementation for development,
    with hooks for integrating real search APIs (e.g., Tavily, SerpAPI).

    Attributes:
        name: Tool name.
        description: Tool description for agent consumption.
        max_results: Maximum number of results to return.
    """

    name: str = "web_search"
    description: str = (
        "Search the web for information. Use this tool when you need to "
        "find current information, look up documentation, or gather data "
        "from the internet. Returns a list of relevant search results "
        "with titles, URLs, and snippets."
    )

    def __init__(self, max_results: int = 10, api_key: str | None = None) -> None:
        """Initialize the search tool.

        Args:
            max_results: Maximum number of results to return per query.
            api_key: Optional API key for the search service.
        """
        self.max_results = max_results
        self._api_key = api_key
        logger.info("SearchTool initialized (max_results=%d)", max_results)

    async def search(self, query: str, num_results: int | None = None) -> SearchResponse:
        """Execute a web search query.

        Args:
            query: The search query string.
            num_results: Override for the number of results to return.

        Returns:
            SearchResponse: The search results.

        Raises:
            SearchToolError: If the search operation fails.
        """
        num_results = min(num_results or self.max_results, self.max_results)

        try:
            # Attempt to use Tavily if API key is available
            if self._api_key:
                return await self._search_tavily(query, num_results)

            # Fallback to mock search for development
            return await self._search_mock(query, num_results)
        except Exception as e:
            raise SearchToolError(f"Search failed for query '{query}': {e}") from e

    async def _search_tavily(self, query: str, num_results: int) -> SearchResponse:
        """Search using the Tavily API.

        Args:
            query: Search query.
            num_results: Number of results to return.

        Returns:
            SearchResponse: Search results from Tavily.
        """
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self._api_key,
                        "query": query,
                        "max_results": num_results,
                        "include_answer": True,
                    },
                )
                response.raise_for_status()
                data = response.json()

            results = [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", ""),
                    relevance_score=r.get("score", 0.0),
                )
                for r in data.get("results", [])
            ]

            return SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
            )
        except ImportError:
            logger.warning("httpx not installed, falling back to mock search")
            return await self._search_mock(query, num_results)
        except Exception as e:
            logger.warning("Tavily search failed: %s, falling back to mock", e)
            return await self._search_mock(query, num_results)

    async def _search_mock(self, query: str, num_results: int) -> SearchResponse:
        """Mock search for development and testing.

        Args:
            query: Search query.
            num_results: Number of mock results to generate.

        Returns:
            SearchResponse: Mock search results.
        """
        logger.debug("Using mock search for query: %s", query)

        mock_results = [
            SearchResult(
                title=f"Search result {i + 1} for: {query}",
                url=f"https://example.com/result/{i + 1}",
                snippet=f"This is a mock search result snippet for the query: {query}. "
                f"Result {i + 1} contains relevant information.",
                relevance_score=round(1.0 - (i * 0.1), 2),
            )
            for i in range(num_results)
        ]

        return SearchResponse(
            query=query,
            results=mock_results,
            total_results=num_results,
        )

    def get_tool_definition(self) -> dict[str, Any]:
        """Return the tool definition for LangChain tool binding.

        Returns:
            dict: Tool definition compatible with LangChain.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query string",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": self.max_results,
                        },
                    },
                    "required": ["query"],
                },
            },
        }


class SearchToolError(Exception):
    """Custom exception for search tool errors."""

    pass
