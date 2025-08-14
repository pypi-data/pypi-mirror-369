"""
Logging configuration with orjson serialization.
"""

import logging
from collections.abc import Mapping
from logging.config import dictConfig
from pathlib import Path

import yaml


class MergingLoggerAdapter(logging.LoggerAdapter):
    """LoggerAdapter that properly merges extra fields from both adapter and log calls.

    NOTE: This is a fix for python before 3.13. See: https://github.com/python/cpython/issues/76913
    """

    def process(self, msg, kwargs):
        """
        Merge extra fields from adapter and individual log calls.

        Individual log call extra fields take precedence over adapter extra fields.
        """
        if "extra" in kwargs:
            # Merge adapter extra with log call extra, with log call taking precedence
            merged_extra = {**self.extra, **kwargs["extra"]}
            kwargs["extra"] = merged_extra
        else:
            kwargs["extra"] = self.extra
        return msg, kwargs


def configure_logging(
    pth_config: Path | str,
    suppress_loggers: list[str] | None = None,
) -> None:
    """
    Configure Python logging with YAML configuration files.

    Args:
        pth_config: Path to the logging configuration YAML file
        suppress_loggers: Additional logger names to suppress (set to WARNING level)

    Example:
        configure_logging(Path("config/logging.yaml"))
        configure_logging("config/logging.prod.yaml", suppress_loggers=["custom.noisy.logger"])
    """
    pth_config = Path(pth_config)

    if not pth_config.exists():
        raise FileNotFoundError(f"Logging configuration file not found: {pth_config}")

    with open(pth_config) as f:
        config = yaml.safe_load(f)

    # Ensure logs directory exists if file handler is configured
    _ensure_log_directory(config)

    # Apply logging configuration
    dictConfig(config)

    # Apply additional logger suppression if specified
    if suppress_loggers:
        for logger_name in suppress_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(
    name: str | None = None,
    extra: Mapping[str, object] | None = None,
) -> logging.Logger:
    """
    Get a logger instance with optional extra context.

    Args:
        name: Logger name (defaults to calling module name)
        extra: Additional context to include in log messages

    Returns:
        Logger instance

    Example:
        logger = get_logger(__name__, service="my-service", version="1.0.0")
        logger.info("Processing request", user_id=123, action="login")
    """
    logger = logging.getLogger(name)

    # If extra context is provided, create a MergingLoggerAdapter
    if extra:
        return MergingLoggerAdapter(logger, extra=extra)

    return logger


def _ensure_log_directory(config: dict) -> None:
    """Ensure log directories exist for file handlers."""
    handlers = config.get("handlers", {})

    for handler_config in handlers.values():
        if "filename" in handler_config:
            log_file = Path(handler_config["filename"])
            log_file.parent.mkdir(parents=True, exist_ok=True)


def generate_config_files(config_dir: Path | str, overwrite: bool = False) -> None:
    """
    Generate example logging configuration files by copying from example_config.

    Args:
        config_dir: Directory where config files should be generated
        overwrite: Whether to overwrite existing files
    Raises:
        FileExistsError: If any config file already exists in the target directory

    Example:
        generate_config_files("config")
        generate_config_files(Path.cwd() / "my_config")
    """
    import shutil

    config_dir = Path(config_dir)
    example_dir = Path(__file__).parent / "example_config"

    config_dir.mkdir(parents=True, exist_ok=True)

    # Check for existing files before copying
    if not overwrite:
        for src_file in example_dir.glob("*.yaml"):
            dest_file = config_dir / src_file.name
            if dest_file.exists():
                raise FileExistsError(
                    f"Configuration file already exists: {dest_file}. "
                    "Remove existing files or choose a different directory."
                )

    # Copy all yaml files from example_config
    for src_file in example_dir.glob("*.yaml"):
        dest_file = config_dir / src_file.name
        shutil.copy2(src_file, dest_file)
