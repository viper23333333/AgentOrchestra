"""
FastAPI application entry point for AgentOrchestra.

Configures the FastAPI application with CORS, routing, middleware,
exception handling, and lifecycle management.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.utils.logger import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler.

    Manages startup and shutdown events for the FastAPI application.
    Initializes services on startup and cleans up on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control to the application.
    """
    # --- Startup ---
    settings = get_settings()
    setup_logging(
        level=settings.log_level,
        json_logs=not settings.debug,
    )

    logger.info("=" * 60)
    logger.info("  AgentOrchestra v%s starting...", settings.app_version)
    logger.info("  Environment: %s", "development" if settings.debug else "production")
    logger.info("  Default LLM: %s", settings.default_llm_provider)
    logger.info("=" * 60)

    # Register agents
    try:
        from app.api.v1.endpoints.agents import register_agents
        from app.core.orchestrator import Orchestrator

        orchestrator = Orchestrator()
        register_agents(orchestrator.get_agent_info())
        logger.info("Agent registration complete")
    except Exception as e:
        logger.warning("Agent registration failed (non-fatal): %s", e)

    yield

    # --- Shutdown ---
    logger.info("AgentOrchestra shutting down...")

    # Close Redis connections if open
    try:
        from app.services.memory.conversation import RedisConversationMemory

        # Note: In a real app, you'd keep a reference to close properly
        logger.info("Cleanup complete")
    except Exception:
        pass

    logger.info("AgentOrchestra stopped.")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application.

    Sets up CORS, middleware, routers, and exception handlers.

    Returns:
        FastAPI: The configured application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "A multi-agent orchestration system powered by FastAPI and LangGraph. "
            "Supports multiple LLM providers (OpenAI, Anthropic, Ollama) and "
            "coordinates specialized agents for planning, research, coding, "
            "review, and summarization."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- CORS Configuration ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request Timing Middleware ---
    @app.middleware("http")
    async def add_request_timing(request: Request, call_next):
        """Add response timing header to all requests."""
        start_time = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"
        return response

    # --- Exception Handlers ---
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions."""
        logger.warning("ValueError: %s", str(exc))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions."""
        logger.error(
            "Unhandled exception: %s",
            str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Please try again."},
        )

    # --- Routers ---
    from app.api.v1.endpoints import agents, chat, tasks

    api_v1_prefix = "/api/v1"

    app.include_router(chat.router, prefix=api_v1_prefix)
    app.include_router(agents.router, prefix=api_v1_prefix)
    app.include_router(tasks.router, prefix=api_v1_prefix)

    # --- Health Check ---
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
    )
