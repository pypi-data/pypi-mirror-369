"""
Tests for logging configuration functionality.
"""

from pathlib import Path

import orjson
import pytest
import yaml

from ss_utils_logging import configure_logging, generate_config_files, get_logger


def modify_config_for_tmp_dir(config_path: Path, tmp_path: Path) -> None:
    """Modify logging config to use tmp directory for log files."""
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Update file handler to use tmp directory
    if "handlers" in config and "file" in config["handlers"]:
        log_file = tmp_path / "logs" / "app.json"
        config["handlers"]["file"]["filename"] = str(log_file)

    # Write modified config back
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def test_logging_dev_config(tmp_path, capsys):
    """Test logging with development configuration."""
    # Setup paths
    pth_log_config = tmp_path / "config/logging.yaml"

    # Generate config files
    generate_config_files(pth_log_config.parent)

    # Modify config to use tmp directory for log files
    modify_config_for_tmp_dir(pth_log_config, tmp_path)

    # Configure logging with dev config
    configure_logging(pth_log_config)

    # Create logger and test
    logger = get_logger("test-utils-logging")
    logger.warning("hello")
    logger.info("info message", extra={"user_id": 123})
    logger.debug("debug message")  # Won't show - root logger is INFO level

    # Check console output
    captured = capsys.readouterr()
    assert "hello" in captured.out
    assert "WARNING" in captured.out
    assert "info message" in captured.out
    # DEBUG won't appear because root logger is set to INFO in the config

    # Check JSON log file was created in tmp directory
    log_file = tmp_path / "logs" / "app.json"
    assert log_file.exists()

    # Validate JSON content
    with open(log_file) as f:
        lines = f.readlines()

    # Parse last line (should be the info message since debug won't be logged)
    last_log = orjson.loads(lines[-1])
    assert last_log["message"] == "info message"
    assert last_log["severity"] == "INFO"
    assert last_log["logger"] == "test-utils-logging"
    assert last_log["user_id"] == 123


def test_logging_prod_config(tmp_path, capsys):
    """Test logging with production configuration."""
    # Setup paths
    pth_log_config = tmp_path / "config/logging.yaml"
    pth_log_config_prod = tmp_path / "config/logging.prod.yaml"

    # Generate config files
    generate_config_files(pth_log_config.parent)

    # Configure logging with prod config
    configure_logging(pth_log_config_prod)

    # Create logger and test
    logger = get_logger("test-utils-logging")
    logger.warning("hello prod")
    logger.info("info prod message", extra={"env": "production"})
    logger.debug("debug message - should not appear")

    # Check console output is JSON format
    captured = capsys.readouterr()
    assert "debug message" not in captured.out  # DEBUG not logged in prod

    # Parse JSON lines from console
    lines = [line for line in captured.out.strip().split("\n") if line]
    assert len(lines) == 2  # Only WARNING and INFO

    # Validate JSON structure
    warning_log = orjson.loads(lines[0])
    assert warning_log["message"] == "hello prod"
    assert warning_log["severity"] == "WARNING"

    info_log = orjson.loads(lines[1])
    assert info_log["message"] == "info prod message"
    assert info_log["env"] == "production"


def test_generate_config_files_overwrite(tmp_path):
    """Test generate_config_files with overwrite behavior."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create existing file
    (config_dir / "logging.yaml").write_text("old content")

    # Should raise error without overwrite
    with pytest.raises(FileExistsError, match="Configuration file already exists"):
        generate_config_files(config_dir)

    # Should succeed with overwrite=True
    generate_config_files(config_dir, overwrite=True)

    # Verify content was replaced
    content = (config_dir / "logging.yaml").read_text()
    assert "old content" not in content
    assert "version: 1" in content


def test_exception_logging(tmp_path):
    """Test exception information is logged correctly."""
    # Setup and configure
    pth_log_config = tmp_path / "config/logging.yaml"
    generate_config_files(pth_log_config.parent)
    modify_config_for_tmp_dir(pth_log_config, tmp_path)
    configure_logging(pth_log_config)

    logger = get_logger("test-exception")

    # Log an exception
    try:
        1 / 0  # noqa: B018
    except ZeroDivisionError:
        logger.error("Division error occurred", exc_info=True)

    # Check JSON log file
    log_file = tmp_path / "logs" / "app.json"
    with open(log_file) as f:
        last_line = f.readlines()[-1]

    log_entry = orjson.loads(last_line)
    assert log_entry["message"] == "Division error occurred"
    assert log_entry["severity"] == "ERROR"
    assert "exception" in log_entry
    assert log_entry["exception"]["type"] == "ZeroDivisionError"
    assert "traceback" in log_entry["exception"]


def test_extra_fields_logging(tmp_path):
    """Test extra fields are included in logs."""
    # Setup
    pth_log_config = tmp_path / "config/logging.yaml"
    generate_config_files(pth_log_config.parent)
    modify_config_for_tmp_dir(pth_log_config, tmp_path)
    configure_logging(pth_log_config)

    # Test 1: Logger with extra context at creation
    logger_with_extra = get_logger("test-service", extra={"service": "api", "version": "1.0"})
    logger_with_extra.info("Service started")

    # Test 2: Regular logger with extra fields in log call
    logger = get_logger("test-regular", extra={"request_id": "def456", "service": "api"})
    logger.info("User idle")
    logger.info("User action", extra={"request_id": "abc123", "user_id": 456})

    # Check JSON log
    log_file = tmp_path / "logs" / "app.json"
    with open(log_file) as f:
        lines = f.readlines()

    # Parse the service log entry (first)
    service_log = orjson.loads(lines[-3])
    assert service_log["service"] == "api"
    assert service_log["version"] == "1.0"
    assert service_log["message"] == "Service started"

    # Parse the user idle log entry (second to last)
    idle_log = orjson.loads(lines[-2])
    assert idle_log["request_id"] == "def456"  # From get_logger extra
    assert idle_log["service"] == "api"  # From get_logger extra
    assert idle_log["message"] == "User idle"

    # Parse the user action log entry (last) - tests proper merging behavior
    user_log = orjson.loads(lines[-1])
    assert user_log["request_id"] == "abc123"  # Call-level extra overrides adapter extra
    assert user_log["user_id"] == 456  # Call-level extra fields are now included
    assert user_log["service"] == "api"  # Adapter extra fields are preserved
    assert user_log["message"] == "User action"


def test_suppress_loggers(tmp_path, capsys):
    """Test logger suppression functionality."""
    # Setup
    pth_log_config = tmp_path / "config/logging.yaml"
    generate_config_files(pth_log_config.parent)
    modify_config_for_tmp_dir(pth_log_config, tmp_path)
    configure_logging(pth_log_config, suppress_loggers=["noisy.module"])

    # Test suppressed logger
    noisy_logger = get_logger("noisy.module")
    noisy_logger.info("This should not appear")
    noisy_logger.warning("This warning should appear")

    captured = capsys.readouterr()
    assert "This should not appear" not in captured.out
    assert "This warning should appear" in captured.out


def test_missing_config_file():
    """Test error when config file doesn't exist."""
    with pytest.raises(FileNotFoundError, match="Logging configuration file not found"):
        configure_logging(Path("/non/existent/path.yaml"))


def test_log_directory_auto_creation(tmp_path):
    """Test that log directory is created automatically."""
    # Ensure logs directory doesn't exist initially
    logs_dir = tmp_path / "logs"
    assert not logs_dir.exists()

    # Setup and configure
    pth_log_config = tmp_path / "config/logging.yaml"
    generate_config_files(pth_log_config.parent)
    modify_config_for_tmp_dir(pth_log_config, tmp_path)
    configure_logging(pth_log_config)

    # Log something
    logger = get_logger("test")
    logger.info("Creating log directory")

    # Verify directory was created in tmp directory
    assert logs_dir.exists()
    assert (logs_dir / "app.json").exists()
