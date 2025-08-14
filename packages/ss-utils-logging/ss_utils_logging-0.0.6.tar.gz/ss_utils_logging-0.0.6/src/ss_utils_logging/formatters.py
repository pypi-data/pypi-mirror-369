"""
Custom logging formatters with orjson for high performance.
"""

import logging
import traceback
from datetime import UTC, datetime
from typing import Any

import orjson


class ORJSONFormatter(logging.Formatter):
    """High-performance JSON formatter using orjson."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string using orjson."""
        log_entry: dict[str, Any] = {
            "time": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add any extra fields from log call
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "message",
                }:
                    log_entry[key] = value

        # Use orjson for fast serialization
        return orjson.dumps(log_entry).decode("utf-8")


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter for development."""

    # Color codes for different log levels
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console output with colors."""
        # Get color for log level
        color = self.COLORS.get(record.levelname, "")

        # Format basic message
        formatted = super().format(record)

        # Add color if available
        if color:
            # Color the level name only
            formatted = formatted.replace(f"[{record.levelname:>8}]", f"[{color}{record.levelname:>8}{self.RESET}]")

        # Add extra fields if present
        extra_fields = []
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "message",
                    "asctime",
                }:
                    extra_fields.append(f"{key}={value}")

        if extra_fields:
            formatted += f" [{', '.join(extra_fields)}]"

        return formatted
