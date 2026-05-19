"""
Unit tests for the agent implementations.

Tests the base agent class and all concrete agent implementations
including planner, researcher, coder, reviewer, and summarizer.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.base import BaseAgent
from app.agents.coder.agent import CoderAgent
from app.agents.planner.agent import PlannerAgent
from app.agents.researcher.agent import ResearcherAgent
from app.agents.reviewer.agent import ReviewerAgent
from app.agents.summarizer.agent import SummarizerAgent
from app.schemas.agent import AgentConfig, AgentType


# ---------------------------------------------------------------------------
# Tests: Base Agent
# ---------------------------------------------------------------------------


class TestBaseAgent:
    """Tests for the BaseAgent abstract class."""

    def test_base_agent_cannot_be_instantiated(self):
        """Verify that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent()  # type: ignore[abstract]

    @pytest.mark.asyncio
    async def test_execute_with_tracking_success(self):
        """Verify that _execute_with_tracking tracks successful execution."""
        with patch("app.agents.base.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            agent = PlannerAgent()
            agent.execute = AsyncMock(
                return_value=AgentResponse(
                    agent_name="planner",
                    agent_type=AgentType.PLANNER,
                    success=True,
                    content="Test output",
                )
            )

            result = await agent._execute_with_tracking("Test task", {})

            assert result.success is True
            assert result.content == "Test output"
            assert result.execution_time_ms is not None
            assert agent.state.execution_count == 1

    @pytest.mark.asyncio
    async def test_execute_with_tracking_handles_errors(self):
        """Verify that _execute_with_tracking handles exceptions gracefully."""
        with patch("app.agents.base.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            agent = PlannerAgent()
            agent.execute = AsyncMock(side_effect=RuntimeError("Test error"))

            result = await agent._execute_with_tracking("Test task", {})

            assert result.success is False
            assert result.error == "Test error"
            assert result.execution_time_ms is not None


# ---------------------------------------------------------------------------
# Tests: Planner Agent
# ---------------------------------------------------------------------------


class TestPlannerAgent:
    """Tests for the PlannerAgent."""

    @pytest.mark.asyncio
    async def test_planner_properties(self):
        """Verify planner agent properties."""
        with patch("app.agents.planner.agent.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            agent = PlannerAgent()
            assert agent.name == "planner"
            assert agent.agent_type == AgentType.PLANNER
            assert agent.role == "task_planning"
            assert len(agent.description) > 0
            assert len(agent.system_prompt) > 0

    @pytest.mark.asyncio
    async def test_planner_parse_valid_json(self):
        """Verify that the planner can parse valid JSON output."""
        with patch("app.agents.planner.agent.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            agent = PlannerAgent()

            # Test direct JSON
            result = agent._parse_plan_json('{"objective": "test", "steps": []}')
            assert result["objective"] == "test"

            # Test JSON in code block
            result = agent._parse_plan_json('```json\n{"objective": "test2", "steps": []}\n```')
            assert result["objective"] == "test2"

    @pytest.mark.asyncio
    async def test_planner_default_config(self):
        """Verify the planner's default configuration."""
        with patch("app.agents.planner.agent.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            agent = PlannerAgent()
            config = agent._default_config()
            assert config.name == "planner"
            assert config.agent_type == AgentType.PLANNER
            assert config.temperature == 0.3  # Lower for structured output


# ---------------------------------------------------------------------------
# Tests: All Agent Types
# ---------------------------------------------------------------------------


class TestAllAgentTypes:
    """Tests that verify common properties across all agent types."""

    AGENT_CLASSES = [
        ("planner", PlannerAgent, AgentType.PLANNER),
        ("researcher", ResearcherAgent, AgentType.RESEARCHER),
        ("coder", CoderAgent, AgentType.CODER),
        ("reviewer", ReviewerAgent, AgentType.REVIEWER),
        ("summarizer", SummarizerAgent, AgentType.SUMMARIZER),
    ]

    @pytest.mark.parametrize("name,cls,expected_type", AGENT_CLASSES)
    @pytest.mark.asyncio
    async def test_agent_has_correct_type(self, name, cls, expected_type):
        """Verify each agent has the correct AgentType."""
        with patch("app.agents.base.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            agent = cls()
            assert agent.agent_type == expected_type

    @pytest.mark.parametrize("name,cls,expected_type", AGENT_CLASSES)
    @pytest.mark.asyncio
    async def test_agent_has_name(self, name, cls, expected_type):
        """Verify each agent has a non-empty name."""
        with patch("app.agents.base.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            agent = cls()
            assert isinstance(agent.name, str)
            assert len(agent.name) > 0

    @pytest.mark.parametrize("name,cls,expected_type", AGENT_CLASSES)
    @pytest.mark.asyncio
    async def test_agent_has_system_prompt(self, name, cls, expected_type):
        """Verify each agent has a non-empty system prompt."""
        with patch("app.agents.base.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            agent = cls()
            assert isinstance(agent.system_prompt, str)
            assert len(agent.system_prompt) > 50


# ---------------------------------------------------------------------------
# Tests: Reviewer Verdict Extraction
# ---------------------------------------------------------------------------


class TestReviewerVerdict:
    """Tests for the reviewer's verdict extraction logic."""

    @pytest.mark.asyncio
    async def test_extract_approved_verdict(self):
        """Verify APPROVED verdict extraction."""
        with patch("app.agents.reviewer.agent.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            reviewer = ReviewerAgent()
            assert reviewer._extract_verdict("## Review Summary\nAPPROVED") == "APPROVED"

    @pytest.mark.asyncio
    async def test_extract_needs_revision_verdict(self):
        """Verify NEEDS_REVISION verdict extraction."""
        with patch("app.agents.reviewer.agent.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            reviewer = ReviewerAgent()
            assert (
                reviewer._extract_verdict("## Review Summary\nNEEDS_REVISION")
                == "NEEDS_REVISION"
            )

    @pytest.mark.asyncio
    async def test_extract_rejected_verdict(self):
        """Verify REJECTED verdict extraction."""
        with patch("app.agents.reviewer.agent.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            reviewer = ReviewerAgent()
            assert reviewer._extract_verdict("## Review Summary\nREJECTED") == "REJECTED"


# ---------------------------------------------------------------------------
# Tests: Coder Artifact Extraction
# ---------------------------------------------------------------------------


class TestCoderArtifacts:
    """Tests for the coder's code artifact extraction."""

    @pytest.mark.asyncio
    async def test_extract_single_code_block(self):
        """Verify extraction of a single code block."""
        with patch("app.agents.coder.agent.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            coder = CoderAgent()
            text = 'Here is the code:\n```python\ndef hello():\n    print("Hello")\n```'
            artifacts = coder._extract_code_artifacts(text)

            assert len(artifacts) == 1
            assert artifacts[0]["language"] == "python"
            assert 'print("Hello")' in artifacts[0]["content"]

    @pytest.mark.asyncio
    async def test_extract_multiple_code_blocks(self):
        """Verify extraction of multiple code blocks."""
        with patch("app.agents.coder.agent.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                default_llm_provider="openai",
                openai_api_key="sk-test",
                openai_model="gpt-4o",
                openai_temperature=0.7,
                openai_max_tokens=1024,
                anthropic_api_key=None,
                anthropic_model="claude-sonnet-4-20250514",
                anthropic_temperature=0.7,
                anthropic_max_tokens=1024,
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3",
                ollama_temperature=0.7,
                get_openai_settings=MagicMock(
                    return_value=MagicMock(
                        api_key="sk-test",
                        model="gpt-4o",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_anthropic_settings=MagicMock(
                    return_value=MagicMock(
                        api_key=None,
                        model="claude-sonnet-4-20250514",
                        temperature=0.7,
                        max_tokens=1024,
                    )
                ),
                get_ollama_settings=MagicMock(
                    return_value=MagicMock(
                        model="llama3",
                        temperature=0.7,
                        base_url="http://localhost:11434",
                    )
                ),
            )

            coder = CoderAgent()
            text = (
                '**File: main.py**\n```python\nprint("main")\n```\n'
                '**File: utils.py**\n```python\nprint("utils")\n```'
            )
            artifacts = coder._extract_code_artifacts(text)

            assert len(artifacts) == 2
            assert artifacts[0].get("filename") == "main.py"
            assert artifacts[1].get("filename") == "utils.py"
