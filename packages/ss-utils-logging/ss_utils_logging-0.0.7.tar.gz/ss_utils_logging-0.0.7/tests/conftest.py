"""
Pytest fixtures for utils_logging tests.
"""

import logging

import pytest


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration after each test."""
    yield
    # Clear all handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    # Reset root logger level
    root_logger.setLevel(logging.WARNING)

    # Clear handlers from any test loggers
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("test"):
            logger = logging.getLogger(name)
            logger.handlers.clear()
            logger.setLevel(logging.NOTSET)
