"""
Logging utilities for SWIM P2P.

This module provides functions for setting up and configuring logging
for the SWIM protocol.
"""

import logging
import sys
import os
from typing import Optional
import datetime


def setup_logging(
    name: str = "swim",
    level: Optional[int] = None,
    format_str: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_colors: bool = True,
    json_logging: bool = False  # Added json_logging parameter
) -> logging.Logger:
    """Set up a logger with the specified configuration.
    
    Args:
        name: The name of the logger
        level: The logging level (default: INFO or from env var)
        format_str: Custom format string for log messages
        log_file: Optional file path to write logs to
        enable_colors: Whether to use ANSI colors in log output
        json_logging: Whether to output logs in JSON format
        
    Returns:
        The configured logger
    """
    # Default level is INFO
    if level is None:
        level = logging.INFO
    
    # Default format includes timestamp, level, and logger name
    if format_str is None:
        if json_logging:
            # For JSON logging, we'll handle formatting differently
            format_str = "%(message)s"
        elif enable_colors:
            # With ANSI color codes for log levels
            format_str = "%(asctime)s %(colored_level)s %(name)s: %(message)s"
        else:
            format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    # Create formatter
    if json_logging:
        # Use JSON formatter if JSON logging is enabled
        import json
        
        class JsonFormatter(logging.Formatter):
            """Formatter that outputs JSON strings"""
            
            def format(self, record):
                log_record = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "name": record.name,
                    "message": record.getMessage()
                }
                
                # Add exception info if present
                if record.exc_info:
                    log_record["exception"] = self.formatException(record.exc_info)
                
                # Add any extra attributes
                for key, value in record.__dict__.items():
                    if key not in ["args", "asctime", "created", "exc_info", "exc_text", 
                                  "filename", "funcName", "id", "levelname", "levelno",
                                  "lineno", "module", "msecs", "message", "msg", 
                                  "name", "pathname", "process", "processName", 
                                  "relativeCreated", "stack_info", "thread", "threadName"]:
                        log_record[key] = value
                
                return json.dumps(log_record)
        
        formatter = JsonFormatter()
    else:
        class ColoredFormatter(logging.Formatter):
            """Custom formatter that adds colors to log levels and supports emoji"""
            
            COLORS = {
                'DEBUG': '\033[36m',     # Cyan
                'INFO': '\033[32m',      # Green
                'WARNING': '\033[33m',   # Yellow
                'ERROR': '\033[31m',     # Red
                'CRITICAL': '\033[35m',  # Magenta
                'RESET': '\033[0m'       # Reset
            }
            
            def format(self, record):
                # Add colored level field if using colors
                if enable_colors:
                    levelname = record.levelname
                    if levelname in self.COLORS:
                        record.colored_level = f"[{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}]"
                    else:
                        record.colored_level = f"[{levelname}]"
                
                # Call the original formatter
                return super().format(record)
        
        # Create formatter
        formatter = ColoredFormatter(format_str)
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Create unique log file with timestamp if not provided
        if not os.path.basename(log_file):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"swim_{timestamp}.log")
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    If the logger doesn't exist, it will be created with default settings.
    
    Args:
        name: The name of the logger
        
    Returns:
        The logger
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set up default
    if not logger.handlers:
        return setup_logging(name)
    
    return logger