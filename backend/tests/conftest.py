"""
Pytest configuration and shared fixtures for the AgentOrchestra test suite.

Provides common test fixtures including FastAPI test client,
mock LLM adapters, and sample data generators.
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Settings Override
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _override_settings():
    """Override application settings for testing.

    Ensures tests don't require real API keys or external services.
    """
    mock_settings = MagicMock()
    mock_settings.app_name = "AgentOrchestra (Test)"
    mock_settings.app_version = "0.1.0-test"
    mock_settings.debug = True
    mock_settings.log_level = "DEBUG"
    mock_settings.secret_key = "test-secret-key"
    mock_settings.default_llm_provider = "openai"
    mock_settings.openai_api_key = "sk-test-key"
    mock_settings.openai_model = "gpt-4o"
    mock_settings.openai_temperature = 0.7
    mock_settings.openai_max_tokens = 1024
    mock_settings.anthropic_api_key = None
    mock_settings.anthropic_model = "claude-sonnet-4-20250514"
    mock_settings.anthropic_temperature = 0.7
    mock_settings.anthropic_max_tokens = 1024
    mock_settings.ollama_base_url = "http://localhost:11434"
    mock_settings.ollama_model = "llama3"
    mock_settings.ollama_temperature = 0.7
    mock_settings.redis_url = ""
    mock_settings.redis_max_connections = 5
    mock_settings.database_url = "sqlite+aiosqlite:///test.db"
    mock_settings.cors_origins = ["http://localhost:3000"]
    mock_settings.cors_allow_credentials = True
    mock_settings.host = "127.0.0.1"
    mock_settings.port = 8000
    mock_settings.workers = 1
    mock_settings.max_revision_rounds = 2

    # Method stubs
    mock_settings.get_openai_settings.return_value = MagicMock(
        api_key="sk-test-key",
        model="gpt-4o",
        temperature=0.7,
        max_tokens=1024,
    )
    mock_settings.get_anthropic_settings.return_value = MagicMock(
        api_key=None,
        model="claude-sonnet-4-20250514",
        temperature=0.7,
        max_tokens=1024,
    )
    mock_settings.get_ollama_settings.return_value = MagicMock(
        model="llama3",
        temperature=0.7,
        base_url="http://localhost:11434",
    )

    with patch("app.config.settings.get_settings", return_value=mock_settings):
        with patch("app.models.llm_models.get_settings", return_value=mock_settings):
            with patch("app.services.llm.provider.get_settings", return_value=mock_settings):
                with patch("app.services.memory.conversation.get_settings", return_value=mock_settings):
                    yield mock_settings


# ---------------------------------------------------------------------------
# Mock LLM Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_llm_response() -> str:
    """Return a mock LLM response string.

    Returns:
        str: A sample LLM response.
    """
    return "This is a mock LLM response for testing."


@pytest.fixture
def mock_llm_adapter(mock_llm_response: str) -> MagicMock:
    """Return a mock LLM adapter that returns canned responses.

    Args:
        mock_llm_response: The canned response text.

    Returns:
        MagicMock: Mock adapter with invoke and stream methods.
    """
    from langchain_core.messages import AIMessage

    adapter = MagicMock()
    adapter.provider_name = "mock"
    adapter.model_name = "mock-model"

    # Mock invoke
    async def mock_invoke(messages, **kwargs):
        return AIMessage(content=mock_llm_response)

    adapter.invoke = AsyncMock(side_effect=mock_invoke)

    # Mock stream
    async def mock_stream(messages, **kwargs):
        for word in mock_llm_response.split():
            yield word + " "

    adapter.stream = mock_stream
    adapter.validate_api_key.return_value = True

    return adapter


# ---------------------------------------------------------------------------
# FastAPI Test Client
# ---------------------------------------------------------------------------


@pytest.fixture
async def test_client() -> AsyncIterator[AsyncClient]:
    """Provide an async test client for the FastAPI application.

    Yields:
        AsyncClient: Configured test client.
    """
    from app.main import create_application

    app = create_application()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# ---------------------------------------------------------------------------
# Sample Data Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_user_request() -> str:
    """Return a sample user request for testing.

    Returns:
        str: A sample task description.
    """
    return "Build a simple REST API with FastAPI that manages a todo list."


@pytest.fixture
def sample_chat_request() -> dict[str, Any]:
    """Return a sample chat request payload.

    Returns:
        dict: Chat request data.
    """
    return {
        "message": "Help me write a Python function to sort a list",
        "stream": False,
    }


@pytest.fixture
def sample_task_plan() -> dict[str, Any]:
    """Return a sample task plan.

    Returns:
        dict: Task plan data.
    """
    return {
        "objective": "Build a REST API for todo management",
        "steps": [
            {
                "step_number": 1,
                "description": "Research best practices for REST API design",
                "assigned_agent": "researcher",
                "dependencies": [],
                "status": "pending",
            },
            {
                "step_number": 2,
                "description": "Implement the API endpoints",
                "assigned_agent": "coder",
                "dependencies": [1],
                "status": "pending",
            },
            {
                "step_number": 3,
                "description": "Review the code for quality",
                "assigned_agent": "reviewer",
                "dependencies": [2],
                "status": "pending",
            },
        ],
        "estimated_complexity": 5,
    }
