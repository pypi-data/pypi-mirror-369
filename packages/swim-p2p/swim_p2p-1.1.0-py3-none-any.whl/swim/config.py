"""
Configuration for SWIM P2P.

This module provides configuration management for the SWIM protocol,
including default values and environment variable overrides.
"""

import os
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def get_config() -> Dict[str, Any]:
    """
    Get the configuration for the SWIM protocol.
    
    This function returns a dictionary with configuration values,
    using environment variables if available, or defaults otherwise.
    
    Returns:
        A dictionary with configuration values.
    """
    config = {
        # Failure detection
        "PING_TIMEOUT": float(os.environ.get("SWIM_PING_TIMEOUT", "1.0")),
        "PING_RETRIES": int(os.environ.get("SWIM_PING_RETRIES", "2")),
        "INDIRECT_PROBE_COUNT": int(os.environ.get("SWIM_INDIRECT_PROBE_COUNT", "3")),
        
        # Gossip
        "PROTOCOL_PERIOD": float(os.environ.get("SWIM_PROTOCOL_PERIOD", "1.0")),
        "GOSSIP_FANOUT": int(os.environ.get("SWIM_GOSSIP_FANOUT", "3")),
        "HEARTBEAT_INTERVAL": float(os.environ.get("SWIM_HEARTBEAT_INTERVAL", "1.0")),
        
        # Timeouts
        "SUSPECT_TIMEOUT": float(os.environ.get("SWIM_SUSPECT_TIMEOUT", "5.0")),
        
        # Adaptive timing
        "ADAPTIVE_TIMING_ENABLED": os.environ.get("SWIM_ADAPTIVE_TIMING", "true").lower() in ("true", "1", "yes"),
        "PROTOCOL_PERIOD_MIN": float(os.environ.get("SWIM_PROTOCOL_PERIOD_MIN", "0.5")),
        "PROTOCOL_PERIOD_MAX": float(os.environ.get("SWIM_PROTOCOL_PERIOD_MAX", "2.0")),
        "PROTOCOL_PERIOD_ADJUSTMENT_FACTOR": float(os.environ.get("SWIM_PROTOCOL_PERIOD_ADJUSTMENT_FACTOR", "0.1")),
        
        # Push-pull synchronization
        "PUSH_PULL_SYNC_ENABLED": os.environ.get("SWIM_PUSH_PULL_SYNC", "true").lower() in ("true", "1", "yes"),
        "SYNC_INTERVAL": float(os.environ.get("SWIM_SYNC_INTERVAL", "30.0")),
        "SYNC_REQUEST_TIMEOUT": float(os.environ.get("SWIM_SYNC_REQUEST_TIMEOUT", "5.0")),
        
        # Transport settings
        "UDP_MAX_SIZE": int(os.environ.get("SWIM_UDP_MAX_SIZE", "1400")),
        "TCP_BUFFER_SIZE": int(os.environ.get("SWIM_TCP_BUFFER_SIZE", "65536")),
        "TCP_MAX_CONNECTIONS": int(os.environ.get("SWIM_TCP_MAX_CONNECTIONS", "100")),
        "TCP_CONNECTION_TIMEOUT": float(os.environ.get("SWIM_TCP_CONNECTION_TIMEOUT", "5.0")),
        
        # Rate control and bandwidth management
        "RATE_LIMITING_ENABLED": os.environ.get("SWIM_RATE_LIMITING", "false").lower() in ("true", "1", "yes"),
        "MAX_OUTBOUND_RATE": int(os.environ.get("SWIM_MAX_OUTBOUND_RATE", "0")),  # 0 means no limit
        "MAX_INBOUND_RATE": int(os.environ.get("SWIM_MAX_INBOUND_RATE", "0")),    # 0 means no limit
        "BANDWIDTH_WINDOW_SIZE": int(os.environ.get("SWIM_BANDWIDTH_WINDOW_SIZE", "3600")),
        
        # Metrics
        "METRICS_ENABLED": os.environ.get("SWIM_METRICS_ENABLED", "true").lower() in ("true", "1", "yes"),
        "METRICS_REPORT_INTERVAL": float(os.environ.get("SWIM_METRICS_REPORT_INTERVAL", "60.0")),
        
        # Logging
        "LOG_LEVEL": os.environ.get("SWIM_LOG_LEVEL", "INFO"),
        "LOG_FILE": os.environ.get("SWIM_LOG_FILE", ""),
        "JSON_LOGGING": os.environ.get("SWIM_JSON_LOGGING", "false").lower() in ("true", "1", "yes"),

        # Lifeguard enhancements
        "LIFEGUARD_ENABLED": os.environ.get("SWIM_LIFEGUARD_ENABLED", "true").lower() in ("true", "1", "yes"),
        "MIN_AWARENESS": int(os.environ.get("SWIM_MIN_AWARENESS", "0")),
        "MAX_AWARENESS": int(os.environ.get("SWIM_MAX_AWARENESS", "8")),
        "PROBE_RATE_MIN": float(os.environ.get("SWIM_PROBE_RATE_MIN", "0.2")),
        "PROBE_RATE_MAX": float(os.environ.get("SWIM_PROBE_RATE_MAX", "2.0")),
    }
    
    # Try to load config from file if specified
    config_file = os.environ.get("SWIM_CONFIG_FILE", "")
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                # Update config with file values
                config.update(file_config)
                logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_file}: {e}")
    
    # Log the configuration
    logger.debug(f"SWIM configuration: {config}")
    
    return config


def save_config(config: Dict[str, Any], file_path: str) -> bool:
    """
    Save configuration to a file.
    
    Args:
        config: Configuration dictionary
        file_path: Path to save the configuration
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuration saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration to {file_path}: {e}")
        return False


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key: Configuration key
        default: Default value if key is not found
        
    Returns:
        Configuration value or default
    """
    config = get_config()
    return config.get(key, default)


def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate configuration values.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of validation errors (empty if valid)
    """
    errors = {}
    
    # Validate numeric ranges
    numeric_ranges = {
        "PING_TIMEOUT": (0.1, 10.0),
        "PING_RETRIES": (0, 10),
        "INDIRECT_PROBE_COUNT": (1, 10),
        "PROTOCOL_PERIOD": (0.1, 10.0),
        "GOSSIP_FANOUT": (1, 10),
        "SUSPECT_TIMEOUT": (1.0, 60.0),
        "PROTOCOL_PERIOD_MIN": (0.1, 1.0),
        "PROTOCOL_PERIOD_MAX": (1.0, 10.0),
        "PROTOCOL_PERIOD_ADJUSTMENT_FACTOR": (0.01, 0.5),
        "SYNC_INTERVAL": (5.0, 300.0),
        "UDP_MAX_SIZE": (512, 65507),
        "TCP_BUFFER_SIZE": (1024, 1048576),
        "TCP_MAX_CONNECTIONS": (10, 1000),
    }
    
    for key, (min_val, max_val) in numeric_ranges.items():
        if key in config:
            value = config[key]
            if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                errors[key] = f"Must be between {min_val} and {max_val}"
    
    # Validate boolean values
    boolean_keys = [
        "ADAPTIVE_TIMING_ENABLED",
        "PUSH_PULL_SYNC_ENABLED",
        "RATE_LIMITING_ENABLED",
        "METRICS_ENABLED",
        "JSON_LOGGING"
    ]
    
    for key in boolean_keys:
        if key in config and not isinstance(config[key], bool):
            errors[key] = "Must be a boolean value"
    
    # Validate log level
    if "LOG_LEVEL" in config:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config["LOG_LEVEL"] not in valid_levels:
            errors["LOG_LEVEL"] = f"Must be one of: {', '.join(valid_levels)}"
    
    return errors