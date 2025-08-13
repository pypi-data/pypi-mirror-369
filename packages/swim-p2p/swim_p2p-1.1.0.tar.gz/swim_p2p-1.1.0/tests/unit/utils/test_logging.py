"""
Unit tests for logging utilities.
"""

import pytest
import logging
import io
from swim.utils.logging import setup_logging, get_logger


def test_setup_logging():
    """Test that logging setup configures the logger correctly."""
    # Capture log output
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    
    # Setup logging with our handler
    logger = setup_logging("test_logger", level=logging.DEBUG)
    
    # Replace the handler to capture output
    logger.handlers.clear()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    
    # Test logging at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Get the captured output
    log_output = log_capture.getvalue()
    
    # Verify log messages
    assert "DEBUG: Debug message" in log_output
    assert "INFO: Info message" in log_output
    assert "WARNING: Warning message" in log_output
    assert "ERROR: Error message" in log_output


def test_log_levels():
    """Test that log levels are respected."""
    # Capture log output
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    
    # Setup logging with WARNING level
    logger = setup_logging("test_logger", level=logging.WARNING)
    
    # Replace the handler to capture output
    logger.handlers.clear()
    logger.addHandler(handler)
    
    # Test logging at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Get the captured output
    log_output = log_capture.getvalue()
    
    # Verify only WARNING and above are logged
    assert "DEBUG: Debug message" not in log_output
    assert "INFO: Info message" not in log_output
    assert "WARNING: Warning message" in log_output
    assert "ERROR: Error message" in log_output


def test_get_logger():
    """Test getting a logger."""
    # Get a logger
    logger1 = get_logger("test_logger")
    
    # Get the same logger again
    logger2 = get_logger("test_logger")
    
    # Verify it's the same logger
    assert logger1 is logger2
    
    # Verify it has a handler
    assert len(logger1.handlers) > 0