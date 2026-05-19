"""
Application configuration management module.

Uses pydantic-settings to load configuration from environment variables
and .env files. Provides a centralized Settings singleton for access
throughout the application.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderSettings(BaseSettings):
    """Configuration for a single LLM provider."""

    api_key: str | None = Field(default=None, description="API key for the provider")
    model: str = Field(default="gpt-4o", description="Default model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=4096, ge=1, le=128000, description="Maximum tokens per request")
    base_url: str | None = Field(default=None, description="Custom base URL (e.g., for Ollama)")


class RedisSettings(BaseSettings):
    """Redis connection configuration."""

    url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    max_connections: int = Field(default=10, ge=1, le=100, description="Max connection pool size")
    ttl: int = Field(default=3600, ge=60, description="Default TTL for cached items (seconds)")


class DatabaseSettings(BaseSettings):
    """Database connection configuration."""

    url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/agent_orchestra",
        description="Database connection URL",
    )
    pool_size: int = Field(default=5, ge=1, le=50, description="Connection pool size")
    max_overflow: int = Field(default=10, ge=0, le=50, description="Max overflow connections")


class CORSSettings(BaseSettings):
    """CORS (Cross-Origin Resource Sharing) configuration."""

    origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed origins",
    )
    allow_credentials: bool = Field(default=True, description="Allow credentials")
    allow_methods: list[str] = Field(
        default=["*"],
        description="Allowed HTTP methods",
    )
    allow_headers: list[str] = Field(
        default=["*"],
        description="Allowed HTTP headers",
    )


class Settings(BaseSettings):
    """Main application settings.

    Loads configuration from environment variables and .env files.
    All settings have sensible defaults for local development.

    Attributes:
        app_name: Application name displayed in docs and logs.
        app_version: Semantic version string.
        debug: Enable debug mode (verbose logging, auto-reload).
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        secret_key: Secret key for signing tokens and encrypting data.
        default_llm_provider: Which LLM provider to use by default.
        cors: CORS configuration.
        redis: Redis configuration.
        database: Database configuration.
        host: Server bind address.
        port: Server bind port.
        workers: Number of uvicorn worker processes.
        max_revision_rounds: Maximum code review iterations before forced acceptance.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = Field(default="AgentOrchestra", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Log level"
    )
    secret_key: str = Field(
        default="change-this-in-production",
        description="Secret key for cryptographic operations",
    )

    # --- Default LLM Provider ---
    default_llm_provider: Literal["openai", "anthropic", "ollama"] = Field(
        default="openai", description="Default LLM provider"
    )

    # --- OpenAI ---
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=4096, alias="OPENAI_MAX_TOKENS")

    # --- Anthropic ---
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", alias="ANTHROPIC_MODEL")
    anthropic_temperature: float = Field(default=0.7, alias="ANTHROPIC_TEMPERATURE")
    anthropic_max_tokens: int = Field(default=4096, alias="ANTHROPIC_MAX_TOKENS")

    # --- Ollama ---
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")
    ollama_temperature: float = Field(default=0.7, alias="OLLAMA_TEMPERATURE")

    # --- Redis ---
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")

    # --- Database ---
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/agent_orchestra",
        alias="DATABASE_URL",
    )

    # --- CORS ---
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="CORS_ORIGINS",
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")

    # --- Server ---
    host: str = Field(default="0.0.0.0", description="Server bind host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server bind port")
    workers: int = Field(default=1, ge=1, le=16, description="Number of workers")

    # --- Orchestration ---
    max_revision_rounds: int = Field(
        default=3, ge=1, le=10, description="Max code review iterations"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # --- Computed Properties ---

    @property
    def cors_settings(self) -> CORSSettings:
        """Return CORS settings as a structured object."""
        return CORSSettings(
            origins=self.cors_origins,
            allow_credentials=self.cors_allow_credentials,
        )

    @property
    def redis_settings(self) -> RedisSettings:
        """Return Redis settings as a structured object."""
        return RedisSettings(
            url=self.redis_url,
            max_connections=self.redis_max_connections,
        )

    @property
    def database_settings(self) -> DatabaseSettings:
        """Return database settings as a structured object."""
        return DatabaseSettings(url=self.database_url)

    def get_openai_settings(self) -> LLMProviderSettings:
        """Return OpenAI provider settings."""
        return LLMProviderSettings(
            api_key=self.openai_api_key,
            model=self.openai_model,
            temperature=self.openai_temperature,
            max_tokens=self.openai_max_tokens,
        )

    def get_anthropic_settings(self) -> LLMProviderSettings:
        """Return Anthropic provider settings."""
        return LLMProviderSettings(
            api_key=self.anthropic_api_key,
            model=self.anthropic_model,
            temperature=self.anthropic_temperature,
            max_tokens=self.anthropic_max_tokens,
        )

    def get_ollama_settings(self) -> LLMProviderSettings:
        """Return Ollama provider settings."""
        return LLMProviderSettings(
            model=self.ollama_model,
            temperature=self.ollama_temperature,
            base_url=self.ollama_base_url,
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached Settings singleton.

    Uses lru_cache to ensure settings are loaded only once per process.
    Call ``get_settings.cache_clear()`` to force a reload (useful in tests).

    Returns:
        Settings: The application settings instance.
    """
    return Settings()
