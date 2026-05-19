"""
Structured logging configuration for the AgentOrchestra system.

Provides a centralized logging setup with structured JSON output,
log level configuration, and request/response logging middleware support.
"""

from __future__ import annotations

import logging
import sys
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON-structured log formatter.

    Formats log records as JSON objects for better parsing and
    integration with log aggregation systems (ELK, CloudWatch, etc.).

    Attributes:
        fmt_keys: Mapping of log record attributes to JSON field names.
    """

    def __init__(
        self,
        fmt_keys: dict[str, str] | None = None,
        prefix: str = "",
    ) -> None:
        """Initialize the JSON formatter.

        Args:
            fmt_keys: Custom mapping of log attributes to JSON keys.
            prefix: Optional prefix for all log messages.
        """
        super().__init__()
        self.fmt_keys = fmt_keys or {
            "level": "levelname",
            "message": "message",
            "timestamp": "asctime",
            "logger": "name",
            "module": "module",
            "function": "funcName",
            "line": "lineno",
        }
        self.prefix = prefix

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            str: JSON-formatted log string.
        """
        import json

        message = record.getMessage()
        if self.prefix:
            message = f"{self.prefix} {message}"

        log_entry: dict[str, Any] = {
            "message": message,
            "level": record.levelname.lower(),
            "timestamp": self.formatTime(record, self.datefmt),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "message": str(record.exc_info[1]),
            }

        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "created",
                "relativeCreated",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "pathname",
                "filename",
                "module",
                "thread",
                "threadName",
                "process",
                "processName",
                "levelname",
                "levelno",
                "message",
                "msecs",
                "taskName",
            }:
                log_entry[key] = value

        try:
            return json.dumps(log_entry, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(log_entry)


class ColoredFormatter(logging.Formatter):
    """Colored console log formatter for development.

    Provides color-coded log output for better readability in
    terminal environments.
    """

    # ANSI color codes
    COLORS: dict[str, str] = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[1;31m",  # Bold Red
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with color codes.

        Args:
            record: The log record to format.

        Returns:
            str: Color-formatted log string.
        """
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname:<8}{self.RESET}"

        # Format the message
        formatted = super().format(record)
        return formatted


def setup_logging(
    level: str = "INFO",
    json_logs: bool = False,
    log_file: str | None = None,
) -> None:
    """Configure application-wide logging.

    Sets up root logger with appropriate handlers and formatters.
    Supports both JSON and colored console output.

    Args:
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_logs: If True, use JSON formatting (for production).
                   If False, use colored console output (for development).
        log_file: Optional file path to write logs to.

    Example:
        >>> setup_logging(level="DEBUG", json_logs=True)
        >>> logger = logging.getLogger("app")
        >>> logger.info("Application started")
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

    if json_logs:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            ColoredFormatter(
                fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.INFO)
    logging.getLogger("langgraph").setLevel(logging.INFO)

    # Log startup message
    root_logger.info(
        "Logging configured (level=%s, json=%s, file=%s)",
        level,
        json_logs,
        log_file or "none",
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module).

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
