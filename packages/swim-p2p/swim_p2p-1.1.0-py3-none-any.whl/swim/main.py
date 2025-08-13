"""
Main entry point for SWIM P2P with ZMQ messaging integration.

This module provides a command-line interface for running a SWIM node
with reliable ZMQ messaging capabilities.
"""

import asyncio
import argparse
import logging
import signal
import sys
import os
import json
import time
from typing import List, Tuple, Optional, Dict, Any, Set, TYPE_CHECKING

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, using environment variables as is

from swim.transport.udp import UDPTransport
from swim.transport.tcp import TCPTransport
from swim.transport.hybrid import HybridTransport
from swim.protocol.node import Node
from swim.config import get_config, save_config, validate_config
from swim.utils.logging import setup_logging
from swim.utils.network import get_local_ip, get_available_port, PortValidationError

# Import event system components
from swim.events.dispatcher import EventDispatcher
from swim.events.handlers import create_default_handlers, register_default_handlers
# Import specific MemberEvent types for type hinting and subscription
from swim.events.types import (
    MemberJoinedEvent, MemberLeftEvent, MemberFailedEvent, MemberSuspectedEvent, MemberAliveEvent,
    Event as SwimEvent, EventCategory, EventSeverity # Base Event for custom events if needed
)


# Import ZMQ Agent Integration
from swim.integration.agent import ZMQAgentIntegration # Corrected import path

logger = logging.getLogger(__name__)

def parse_address(addr_str: str) -> Tuple[str, int]:
    """
    Parse an address string in the format "host:port".
    
    Args:
        addr_str: The address string to parse.
    
    Returns:
        A tuple of (host, port).
    
    Raises:
        ValueError: If the address is invalid.
    """
    try:
        if ":" not in addr_str:
            # Try to parse as just a port number
            try:
                port = int(addr_str)
                return (get_local_ip(), port)
            except ValueError:
                raise ValueError(f"Invalid port: {addr_str}")
        
        host, port_str = addr_str.split(":")
        if not host:
            host = get_local_ip()
        
        port = int(port_str)
        return (host, port)
    except ValueError as e:
        if "invalid literal for int" in str(e):
            raise ValueError(f"Invalid port in address: {addr_str}. Expected 'host:port' or 'port'")
        raise ValueError(f"Invalid address format: {addr_str}. Expected 'host:port' or 'port'")


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Optional list of arguments to parse.
    
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="SWIM P2P Node with ZMQ Messaging",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Get default bind address from environment variable
    default_addr = os.environ.get("SWIM_BIND_ADDRESS")
    
    parser.add_argument(
        "--addr",
        default=default_addr,
        help="Address to bind to in the format 'host:port' or just 'port' (default: from SWIM_BIND_ADDRESS env var)"
    )
    
    # Get default seed nodes from environment variable
    default_seeds = os.environ.get("SWIM_SEED_NODES", "").split() if os.environ.get("SWIM_SEED_NODES") else []
    
    parser.add_argument(
        "--seeds",
        nargs="*",
        default=default_seeds,
        help="Seed nodes to join in the format 'host:port' (default: from SWIM_SEED_NODES env var)"
    )
    
    # ZMQ Integration options
    zmq_group = parser.add_argument_group("ZMQ Messaging Options")
    zmq_group.add_argument(
        "--zmq-enabled",
        action="store_true",
        default=True, 
        help="Enable ZMQ messaging integration (default: enabled)"
    )
    
    zmq_group.add_argument(
        "--no-zmq",
        action="store_false",
        dest="zmq_enabled",
        help="Disable ZMQ messaging integration"
    )
    
    zmq_group.add_argument(
        "--zmq-port-offset",
        type=int,
        default=1000,
        help="Port offset for ZMQ ROUTER (SWIM port + offset)"
    )
    
    zmq_group.add_argument(
        "--node-name",
        type=str,
        default="", # Default to empty, ZMQAgent will generate one if not set
        help="Friendly name for this node, used in automated ZMQ messages (e.g., 'NodeA')"
    )
        
    zmq_group.add_argument(
        "--send-on-join", # This flag now controls the automated check-in message
        action="store_true",
        default=True, 
        help="Send automated 'checking in' message after a new member becomes stable"
    )
    
    # Logging options
    log_group = parser.add_argument_group("Logging Options")
    log_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Set the logging level (default: from SWIM_LOG_LEVEL env var or INFO)"
    )
    
    log_group.add_argument(
        "--log-file",
        default=None,
        help="Log file path (default: from SWIM_LOG_FILE env var)"
    )
    
    log_group.add_argument(
        "--json-logging",
        action="store_true",
        default=None, 
        help="Enable JSON formatted logging (default: from SWIM_JSON_LOGGING env var)"
    )
    
    # Transport options
    transport_group = parser.add_argument_group("Transport Options")
    transport_group.add_argument(
        "--transport",
        choices=["udp", "tcp", "hybrid"],
        default="hybrid", 
        help="Transport type to use"
    )
    
    transport_group.add_argument(
        "--udp-max-size",
        type=int,
        default=None,
        help="Maximum size for UDP messages before switching to TCP (default: from SWIM_UDP_MAX_SIZE env var)"
    )
    
    transport_group.add_argument(
        "--tcp-buffer-size",
        type=int,
        default=None,
        help="TCP buffer size in bytes (default: from SWIM_TCP_BUFFER_SIZE env var)"
    )
    
    transport_group.add_argument(
        "--tcp-max-connections",
        type=int,
        default=None,
        help="Maximum number of TCP connections (default: from SWIM_TCP_MAX_CONNECTIONS env var)"
    )
    
    # Protocol options
    protocol_group = parser.add_argument_group("Protocol Options")
    protocol_group.add_argument(
        "--push-pull-sync",
        action="store_true",
        dest="push_pull_sync",
        default=None, 
        help="Enable push-pull synchronization (default: from SWIM_PUSH_PULL_SYNC env var)"
    )
    
    protocol_group.add_argument(
        "--no-push-pull-sync",
        action="store_false",
        dest="push_pull_sync",
        help="Disable push-pull synchronization"
    )
    
    protocol_group.add_argument(
        "--sync-interval",
        type=float,
        default=None,
        help="Interval between sync requests in seconds (default: from SWIM_SYNC_INTERVAL env var)"
    )
    
    protocol_group.add_argument(
        "--adaptive-timing",
        action="store_true",
        dest="adaptive_timing",
        default=None, 
        help="Enable adaptive protocol timing (default: from SWIM_ADAPTIVE_TIMING env var)"
    )
    
    protocol_group.add_argument(
        "--no-adaptive-timing",
        action="store_false",
        dest="adaptive_timing",
        help="Disable adaptive protocol timing"
    )
    
    protocol_group.add_argument(
        "--protocol-period",
        type=float,
        default=None,
        help="Base protocol period in seconds (default: from SWIM_PROTOCOL_PERIOD env var)"
    )
    
    protocol_group.add_argument(
        "--suspect-timeout",
        type=float,
        default=None,
        help="Timeout for suspect members in seconds (default: from SWIM_SUSPECT_TIMEOUT env var)"
    )
    
    # Bandwidth and rate limiting options
    bandwidth_group = parser.add_argument_group("Bandwidth and Rate Limiting Options")
    bandwidth_group.add_argument(
        "--rate-limiting",
        action="store_true",
        dest="rate_limiting",
        default=None, 
        help="Enable rate limiting (default: from SWIM_RATE_LIMITING env var)"
    )
    
    bandwidth_group.add_argument(
        "--no-rate-limiting",
        action="store_false",
        dest="rate_limiting",
        help="Disable rate limiting"
    )
    
    bandwidth_group.add_argument(
        "--max-outbound-rate",
        type=int,
        default=None,
        help="Maximum outbound bandwidth in bytes per second, 0 for no limit (default: from SWIM_MAX_OUTBOUND_RATE env var)"
    )
    
    bandwidth_group.add_argument(
        "--max-inbound-rate",
        type=int,
        default=None,
        help="Maximum inbound bandwidth in bytes per second, 0 for no limit (default: from SWIM_MAX_INBOUND_RATE env var)"
    )
    
    # Metrics options
    metrics_group = parser.add_argument_group("Metrics Options")
    metrics_group.add_argument(
        "--metrics",
        action="store_true",
        dest="metrics_enabled",
        default=None, 
        help="Enable metrics collection (default: from SWIM_METRICS_ENABLED env var)"
    )
    
    metrics_group.add_argument(
        "--no-metrics",
        action="store_false",
        dest="metrics_enabled",
        help="Disable metrics collection"
    )
    
    metrics_group.add_argument(
        "--metrics-report-interval",
        type=float,
        default=None,
        help="Interval between metrics reports in seconds (default: from SWIM_METRICS_REPORT_INTERVAL env var)"
    )
    
    # Metrics API options
    metrics_group.add_argument(
        "--metrics-api",
        action="store_true",
        dest="metrics_api_enabled",
        default=None, 
        help="Enable metrics API (default: from SWIM_METRICS_API_ENABLED env var)"
    )
    
    metrics_group.add_argument(
        "--no-metrics-api",
        action="store_false",
        dest="metrics_api_enabled",
        help="Disable metrics API"
    )
    
    metrics_group.add_argument(
        "--metrics-api-port",
        type=int,
        default=None,
        help="Port for metrics API server (default: node port + 80)"
    )
    
    metrics_group.add_argument(
        "--metrics-api-host",
        default=None,
        help="Host for metrics API server (default: same as node host)"
    )
    
    # Configuration file options
    config_group = parser.add_argument_group("Configuration Options")
    config_group.add_argument(
        "--config-file",
        default=os.environ.get("SWIM_CONFIG_FILE", ""),
        help="Path to configuration file (default: from SWIM_CONFIG_FILE env var)"
    )
    
    config_group.add_argument(
        "--save-config",
        default="",
        help="Save current configuration to file"
    )
    
    # Add auto-discovery option
    parser.add_argument(
        "--auto-discover",
        action="store_true",
        help="Automatically discover local address and available port"
    )
    
    # Add version option
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit"
    )

    # Lifeguard options
    lifeguard_group = parser.add_argument_group("Lifeguard Enhancement Options")
    lifeguard_group.add_argument(
        "--lifeguard",
        action="store_true",
        dest="lifeguard_enabled",
        default=None, 
        help="Enable Lifeguard enhancements (default: from SWIM_LIFEGUARD_ENABLED env var)"
    )
    
    lifeguard_group.add_argument(
        "--no-lifeguard",
        action="store_false",
        dest="lifeguard_enabled",
        help="Disable Lifeguard enhancements"
    )
    
    lifeguard_group.add_argument(
        "--max-awareness",
        type=int,
        default=None,
        help="Maximum awareness level for Lifeguard (default: from SWIM_MAX_AWARENESS env var)"
    )
    
    # Event system options
    events_group = parser.add_argument_group("Event System Options")
    events_group.add_argument(
        "--events",
        action="store_true",
        dest="events_enabled",
        default=None, 
        help="Enable event system (default: from SWIM_EVENTS_ENABLED env var)"
    )
    
    events_group.add_argument(
        "--no-events",
        action="store_false",
        dest="events_enabled",
        help="Disable event system"
    )
    
    events_group.add_argument(
        "--event-history",
        type=int,
        default=None,
        help="Maximum number of events to keep in history (default: from SWIM_EVENT_HISTORY env var)"
    )
    
    events_group.add_argument(
        "--event-handlers",
        choices=["logging", "metrics", "performance", "all", "none"],
        default="all", 
        help="Event handlers to enable (default: all)"
    )
    
    parsed_args = parser.parse_args(args)
    
    # Handle version request
    if parsed_args.version:
        from swim import __version__
        print(f"SWIM P2P Protocol with ZMQ Messaging version {__version__}")
        sys.exit(0)
    
    # Handle auto-discovery
    if parsed_args.auto_discover:
        local_ip = get_local_ip()
        available_port = get_available_port()
        parsed_args.addr = f"{local_ip}:{available_port}"
        print(f"Auto-discovered local address: {parsed_args.addr}")
    
    # Validate that addr is provided
    if not parsed_args.addr:
        parser.error("Address must be provided either via --addr, SWIM_BIND_ADDRESS environment variable, or --auto-discover")
    
    return parsed_args


def apply_args_to_config(args: argparse.Namespace, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply command-line arguments to configuration.
    
    Args:
        args: Parsed command-line arguments
        config: Base configuration dictionary
        
    Returns:
        Updated configuration dictionary
    """
    updated_config = config.copy()
    
    # Apply ZMQ options
    updated_config["ZMQ_ENABLED"] = args.zmq_enabled
    updated_config["ZMQ_PORT_OFFSET"] = args.zmq_port_offset
    updated_config["NODE_NAME"] = args.node_name # New config for node name
    updated_config["SEND_ON_JOIN"] = args.send_on_join # This flag controls the new automated check-in

    # Remove obsolete ZMQ config options
    if "ZMQ_CUSTOM_MESSAGE" in updated_config:
        del updated_config["ZMQ_CUSTOM_MESSAGE"]
    if "AUTO_MESSAGING" in updated_config:
        del updated_config["AUTO_MESSAGING"]
    if "MESSAGE_INTERVAL" in updated_config: # This interval is not used by the new logic
        del updated_config["MESSAGE_INTERVAL"]

    # Apply transport options
    if args.udp_max_size is not None:
        updated_config["UDP_MAX_SIZE"] = args.udp_max_size
    if args.tcp_buffer_size is not None:
        updated_config["TCP_BUFFER_SIZE"] = args.tcp_buffer_size
    if args.tcp_max_connections is not None:
        updated_config["TCP_MAX_CONNECTIONS"] = args.tcp_max_connections
    
    # Apply protocol options
    if args.push_pull_sync is not None:
        updated_config["PUSH_PULL_SYNC_ENABLED"] = args.push_pull_sync
    if args.sync_interval is not None:
        updated_config["SYNC_INTERVAL"] = args.sync_interval
    if args.adaptive_timing is not None:
        updated_config["ADAPTIVE_TIMING_ENABLED"] = args.adaptive_timing
    if args.protocol_period is not None:
        updated_config["PROTOCOL_PERIOD"] = args.protocol_period
    if args.suspect_timeout is not None:
        updated_config["SUSPECT_TIMEOUT"] = args.suspect_timeout
    
    # Apply bandwidth and rate limiting options
    if args.rate_limiting is not None:
        updated_config["RATE_LIMITING_ENABLED"] = args.rate_limiting
    if args.max_outbound_rate is not None:
        updated_config["MAX_OUTBOUND_RATE"] = args.max_outbound_rate
    if args.max_inbound_rate is not None:
        updated_config["MAX_INBOUND_RATE"] = args.max_inbound_rate
    
    # Apply metrics options
    if args.metrics_enabled is not None:
        updated_config["METRICS_ENABLED"] = args.metrics_enabled
    if args.metrics_report_interval is not None:
        updated_config["METRICS_REPORT_INTERVAL"] = args.metrics_report_interval
    
    # Apply metrics API options
    if args.metrics_api_enabled is not None:
        updated_config["METRICS_API_ENABLED"] = args.metrics_api_enabled
    if args.metrics_api_port is not None:
        updated_config["METRICS_API_PORT"] = args.metrics_api_port
    if args.metrics_api_host is not None:
        updated_config["METRICS_API_HOST"] = args.metrics_api_host
    
    # Apply logging options
    if args.log_level is not None:
        updated_config["LOG_LEVEL"] = args.log_level
    if args.log_file is not None:
        updated_config["LOG_FILE"] = args.log_file
    if args.json_logging is not None:
        updated_config["JSON_LOGGING"] = args.json_logging
    
    # Apply Lifeguard options
    if args.lifeguard_enabled is not None:
        updated_config["LIFEGUARD_ENABLED"] = args.lifeguard_enabled
    if args.max_awareness is not None:
        updated_config["MAX_AWARENESS"] = args.max_awareness
    
    # Apply event system options
    if args.events_enabled is not None:
        updated_config["EVENTS_ENABLED"] = args.events_enabled
    if args.event_history is not None:
        updated_config["EVENT_HISTORY"] = args.event_history
    if args.event_handlers:
        updated_config["EVENT_HANDLERS"] = args.event_handlers
    
    return updated_config


async def create_transport(transport_type: str, config: Dict[str, Any]) -> Any:
    """
    Create a transport instance based on type and configuration.
    
    Args:
        transport_type: Type of transport to create
        config: Configuration dictionary
        
    Returns:
        Transport instance
    """
    if transport_type == "udp":
        from swim.transport.udp import UDPTransport
        return UDPTransport()
    
    elif transport_type == "tcp":
        from swim.transport.tcp import TCPTransport
        return TCPTransport(
            buffer_size=config.get("TCP_BUFFER_SIZE", 65536), 
            max_connections=config.get("TCP_MAX_CONNECTIONS", 128) 
        )
    
    else:  # hybrid is default
        from swim.transport.hybrid import HybridTransport
        return HybridTransport(
            udp_max_size=config.get("UDP_MAX_SIZE", 1400), 
            tcp_buffer_size=config.get("TCP_BUFFER_SIZE", 65536), 
            tcp_max_connections=config.get("TCP_MAX_CONNECTIONS", 128) 
        )


async def setup_event_system(config: Dict[str, Any], metrics_collector=None) -> Optional[EventDispatcher]:
    """
    Set up the event system based on configuration.
    
    Args:
        config: Configuration dictionary
        metrics_collector: Optional metrics collector for metrics handler
        
    Returns:
        Event dispatcher instance or None if events are disabled
    """
    if not config.get("EVENTS_ENABLED", True):
        return None
    
    max_history = config.get("EVENT_HISTORY", 1000)
    dispatcher = EventDispatcher(max_history_size=max_history, enable_history=True)
    
    handlers_config = config.get("EVENT_HANDLERS", "all")
    if handlers_config == "none":
        return dispatcher
    
    enable_metrics = handlers_config in ["metrics", "all"] and metrics_collector is not None
    enable_performance = handlers_config in ["performance", "all"]
    
    def alert_callback(alert_type, data):
        if alert_type == "high_latency":
            logger.warning(f"High latency detected for {data['peer']}: {data['current_latency']:.2f}ms")
        elif alert_type == "resource_exhaustion":
            logger.warning(f"Resource exhaustion detected: {data['resource']} at {data['current_usage']:.1f}%")
    
    register_default_handlers(
        dispatcher,
        metrics_collector=metrics_collector if enable_metrics else None,
        enable_performance_alerts=enable_performance,
        alert_callback=alert_callback if enable_performance else None
    )
    
    logger.info(f"Event system initialized with {handlers_config} handlers and {max_history} event history")
    return dispatcher


async def setup_zmq_integration(
    bind_addr: Tuple[str, int], 
    config: Dict[str, Any], 
    event_dispatcher: Optional[EventDispatcher]
) -> Optional[ZMQAgentIntegration]:
    """
    Set up ZMQ messaging integration.
    
    Args:
        bind_addr: SWIM node bind address
        config: Configuration dictionary
        event_dispatcher: Event dispatcher instance
        
    Returns:
        ZMQ agent integration instance or None if disabled
    """
    if not config.get("ZMQ_ENABLED", True):
        logger.info("ZMQ_INTEGRATION: ZMQ messaging is disabled")
        return None
    
    if not event_dispatcher:
        logger.error("ZMQ_INTEGRATION: Cannot enable ZMQ messaging without an active event system.")
        return None

    try:
        host, port = bind_addr
        zmq_port_offset = config.get("ZMQ_PORT_OFFSET", 1000)
        zmq_port = port + zmq_port_offset
        zmq_bind_address = f"{host}:{zmq_port}"
        
        node_id = f"{host}:{port}" # SWIM node ID
        
        logger.info(f"ZMQ_INTEGRATION: Initializing ZMQ integration for SWIM node {node_id}")
        logger.info(f"ZMQ_INTEGRATION: ZMQ ROUTER will bind to {zmq_bind_address}")
        
        zmq_agent = ZMQAgentIntegration(
            node_id=node_id,
            bind_address=zmq_bind_address,
            event_dispatcher=event_dispatcher,
            config=config
        )
        
        await zmq_agent.start()
        logger.info(f"ZMQ_INTEGRATION: ZMQ messaging integration ready")
        logger.info(f"ZMQ_INTEGRATION: SWIM {node_id} \u2194 ZMQ {zmq_bind_address}")
        return zmq_agent
        
    except Exception as e:
        logger.error(f"ZMQ_INTEGRATION: Failed to initialize ZMQ integration: {e}", exc_info=True)
        return None


class SWIMZMQBridge:
    """
    Bridge between SWIM membership and ZMQ messaging.
    Handles logic for sending automated check-in messages upon stable member joins.
    """
    
    def __init__(self, swim_node: Node, zmq_agent: ZMQAgentIntegration, config: Dict[str, Any]):
        self.swim_node = swim_node
        self.zmq_agent = zmq_agent
        self.config = config
        self.node_name = config.get("NODE_NAME", f"Node@{swim_node.transport.local_address[1]}" if swim_node.transport.local_address else "UnknownNode")
        
        self.stable_members: Set[str] = set()
        self._sent_check_in_to: Set[str] = set()
        self.last_membership_change = time.time()
        self.stability_timeout = config.get("STABILITY_TIMEOUT_SECONDS", 3.0) # Configurable stability
        
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        logger.info(f"SWIM_ZMQ_BRIDGE: Bridge initialized for node '{self.node_name}' (SWIM ID: {self.zmq_agent.node_id})")
        logger.info(f"SWIM_ZMQ_BRIDGE: Automated check-in on stable join: {self.config.get('SEND_ON_JOIN', True)}")
        logger.info(f"SWIM_ZMQ_BRIDGE: Stability timeout: {self.stability_timeout}s")

    async def start(self):
        """Start the SWIM-ZMQ bridge."""
        if self._running: return
        self._running = True
        logger.info("SWIM_ZMQ_BRIDGE: Starting membership monitoring")
        
        if self.swim_node.event_dispatcher:
            self.swim_node.event_dispatcher.subscribe(MemberJoinedEvent, self._on_member_joined)
            self.swim_node.event_dispatcher.subscribe(MemberLeftEvent, self._on_member_left)
            self.swim_node.event_dispatcher.subscribe(MemberFailedEvent, self._on_member_failed)
            self.swim_node.event_dispatcher.subscribe(MemberSuspectedEvent, self._on_member_suspected)
            self.swim_node.event_dispatcher.subscribe(MemberAliveEvent, self._on_member_alive)
            logger.info("SWIM_ZMQ_BRIDGE: Subscribed to SWIM membership events")
        else:
            logger.error("SWIM_ZMQ_BRIDGE: Event dispatcher not available - SWIM integration will not work effectively.")
            self._running = False
            return
        
        self._monitor_task = asyncio.create_task(self._monitor_stability_and_trigger_messaging())
    
    async def stop(self):
        """Stop the SWIM-ZMQ bridge."""
        if not self._running: return
        self._running = False
        logger.info("SWIM_ZMQ_BRIDGE: Stopping bridge")
        
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try: await self._monitor_task
            except asyncio.CancelledError: pass
            self._monitor_task = None

    async def _on_member_joined(self, event: MemberJoinedEvent):
        joined_member_address_str = event.member.address 
        logger.info(f"SWIM_ZMQ_BRIDGE: *** MEMBER {joined_member_address_str} JOINED SWIM CLUSTER *** (Event Source: {event.source_node})")
        
        try:
            await self.zmq_agent.handle_swim_member_joined(joined_member_address_str)
            logger.info(f"SWIM_ZMQ_BRIDGE: ZMQ agent updated for joined member {joined_member_address_str}")
        except Exception as e:
            logger.error(f"SWIM_ZMQ_BRIDGE: Error updating ZMQ agent for joined member {joined_member_address_str}: {e}", exc_info=True)
        
        self.stable_members.add(joined_member_address_str)
        self.last_membership_change = time.time()
        logger.info(f"SWIM_ZMQ_BRIDGE: Membership change detected ({joined_member_address_str} joined), resetting stability timer. Current stable members view: {self.stable_members}")

    async def _on_member_left(self, event: MemberLeftEvent):
        left_member_address_str = event.member.address
        logger.info(f"SWIM_ZMQ_BRIDGE: *** MEMBER {left_member_address_str} LEFT SWIM CLUSTER *** (Event Source: {event.source_node})")
        
        try:
            await self.zmq_agent.handle_swim_member_left(left_member_address_str)
            logger.info(f"SWIM_ZMQ_BRIDGE: ZMQ agent updated for left member {left_member_address_str}")
        except Exception as e:
            logger.error(f"SWIM_ZMQ_BRIDGE: Error updating ZMQ agent for left member {left_member_address_str}: {e}", exc_info=True)
        
        self.stable_members.discard(left_member_address_str)
        self._sent_check_in_to.discard(left_member_address_str) # Clear check-in status
        self.last_membership_change = time.time()
        logger.info(f"SWIM_ZMQ_BRIDGE: Membership change detected ({left_member_address_str} left). Current stable members view: {self.stable_members}")

    async def _on_member_suspected(self, event: MemberSuspectedEvent):
        suspected_member_address_str = event.member.address
        logger.warning(f"SWIM_ZMQ_BRIDGE: *** MEMBER {suspected_member_address_str} SUSPECTED *** (Event Source: {event.source_node})")
        
        try:
            await self.zmq_agent.handle_swim_member_suspected(suspected_member_address_str)
            logger.warning(f"SWIM_ZMQ_BRIDGE: ZMQ agent updated for suspected member {suspected_member_address_str}")
        except Exception as e:
            logger.error(f"SWIM_ZMQ_BRIDGE: Error updating ZMQ agent for suspected member {suspected_member_address_str}: {e}", exc_info=True)
        
        self.stable_members.discard(suspected_member_address_str)
        # Do not clear _sent_check_in_to for suspected, only for left/failed.

    async def _on_member_failed(self, event: MemberFailedEvent):
        failed_member_address_str = event.member.address
        logger.error(f"SWIM_ZMQ_BRIDGE: *** MEMBER {failed_member_address_str} FAILED *** (Event Source: {event.source_node})")
        
        try:
            await self.zmq_agent.handle_swim_member_failed(failed_member_address_str)
            logger.error(f"SWIM_ZMQ_BRIDGE: ZMQ agent updated for failed member {failed_member_address_str}")
        except Exception as e:
            logger.error(f"SWIM_ZMQ_BRIDGE: Error updating ZMQ agent for failed member {failed_member_address_str}: {e}", exc_info=True)
        
        self.stable_members.discard(failed_member_address_str)
        self._sent_check_in_to.discard(failed_member_address_str) # Clear check-in status
        self.last_membership_change = time.time()
        logger.info(f"SWIM_ZMQ_BRIDGE: Membership change detected ({failed_member_address_str} failed). Current stable members view: {self.stable_members}")

    async def _on_member_alive(self, event: MemberAliveEvent):
        """
        Handle member resurrection - when a previously failed/dead member comes back alive.
        This is different from _on_member_joined which handles new members joining for the first time.
        """
        resurrected_member_address_str = event.member.address
        logger.info(f"SWIM_ZMQ_BRIDGE: *** MEMBER {resurrected_member_address_str} RESURRECTED *** (Event Source: {event.source_node})")
        
        try:
            # Re-establish ZMQ connections for the resurrected member
            await self.zmq_agent.handle_swim_member_joined(resurrected_member_address_str)
            logger.info(f"SWIM_ZMQ_BRIDGE: ZMQ agent updated for resurrected member {resurrected_member_address_str}")
            
            # Reset circuit breaker state for the resurrected member
            if hasattr(self.zmq_agent, 'circuit_breaker_manager') and self.zmq_agent.circuit_breaker_manager:
                await self.zmq_agent.circuit_breaker_manager.handle_swim_member_alive(resurrected_member_address_str)
                logger.info(f"SWIM_ZMQ_BRIDGE: Circuit breaker reset for resurrected member {resurrected_member_address_str}")
            
        except Exception as e:
            logger.error(f"SWIM_ZMQ_BRIDGE: Error updating ZMQ agent for resurrected member {resurrected_member_address_str}: {e}", exc_info=True)
        
        # Add back to stable members and clear any previous check-in status for fresh start
        self.stable_members.add(resurrected_member_address_str)
        self._sent_check_in_to.discard(resurrected_member_address_str)  # Fresh start for check-ins
        self.last_membership_change = time.time()
        logger.info(f"SWIM_ZMQ_BRIDGE: Membership change detected ({resurrected_member_address_str} resurrected), resetting stability timer. Current stable members view: {self.stable_members}")

    async def _monitor_stability_and_trigger_messaging(self):
        logger.info("SWIM_ZMQ_BRIDGE: Starting stability monitoring and check-in messaging trigger")
        stability_check_count = 0
        
        while self._running:
            try:
                await asyncio.sleep(2.0) # Check interval
                stability_check_count += 1
                
                # Reconcile stable_members with actual SWIM state first
                if self.swim_node and self.swim_node.members:
                    current_swim_alive_members = {m.address for m in self.swim_node.members.get_alive_members(exclude_self=True)}
                    if current_swim_alive_members != self.stable_members:
                        logger.info(f"SWIM_ZMQ_BRIDGE: Reconciling stable members. Bridge had: {self.stable_members}, SWIM has: {current_swim_alive_members}")
                        
                        newly_added_to_bridge = current_swim_alive_members - self.stable_members
                        newly_removed_from_bridge = self.stable_members - current_swim_alive_members

                        for m_add in newly_added_to_bridge:
                            if hasattr(self.zmq_agent, 'handle_swim_member_joined'):
                                await self.zmq_agent.handle_swim_member_joined(m_add)
                            self.stable_members.add(m_add)

                        for m_rem in newly_removed_from_bridge:
                            if hasattr(self.zmq_agent, 'handle_swim_member_left'):
                                await self.zmq_agent.handle_swim_member_left(m_rem)
                            self.stable_members.discard(m_rem)
                            self._sent_check_in_to.discard(m_rem)
                        
                        self.last_membership_change = time.time() # Membership changed due to reconciliation
                        logger.info(f"SWIM_ZMQ_BRIDGE: Stable members reconciled. New stable set: {self.stable_members}. Resetting stability timer.")
                        continue # Re-evaluate stability in next cycle

                time_since_change = time.time() - self.last_membership_change
                logger.debug(f"SWIM_ZMQ_BRIDGE: Stability check #{stability_check_count}, current stable members view: {len(self.stable_members)}, time since last change: {time_since_change:.1f}s")

                if time_since_change >= self.stability_timeout:
                    if self.config.get("SEND_ON_JOIN", True): # SEND_ON_JOIN enables this feature
                        members_to_check_in_with = list(self.stable_members - self._sent_check_in_to)
                        
                        if members_to_check_in_with:
                            logger.info(f"SWIM_ZMQ_BRIDGE: Cluster stable. Sending automated check-in messages to: {members_to_check_in_with}")
                            
                            successful_sends = 0
                            failed_sends = 0
                            
                            for target_swim_address_str in members_to_check_in_with:
                                if target_swim_address_str == self.zmq_agent.node_id:
                                    continue
                                
                                try:
                                    logger.info(f"SWIM_ZMQ_BRIDGE: *** SENDING AUTOMATED CHECK-IN TO {target_swim_address_str} from {self.node_name} ***")
                                    success = await self.zmq_agent.send_automated_check_in(target_swim_address_str)
                                    
                                    if success:
                                        successful_sends += 1
                                        self._sent_check_in_to.add(target_swim_address_str)
                                    else:
                                        failed_sends += 1
                                    
                                    log_symbol = "\u2713" if success else "\u2717"
                                    logger.info(f"SWIM_ZMQ_BRIDGE: {log_symbol} Automated check-in from {self.node_name} to {target_swim_address_str} {'SUCCESS' if success else 'FAILED'}")
                                
                                except Exception as e:
                                    failed_sends += 1
                                    logger.error(f"SWIM_ZMQ_BRIDGE: \u2717 Exception sending automated check-in from {self.node_name} to {target_swim_address_str}: {e}", exc_info=True)
                            
                            total_attempted = successful_sends + failed_sends
                            if total_attempted > 0:
                                success_rate = successful_sends / total_attempted * 100
                                logger.info(f"SWIM_ZMQ_BRIDGE: *** AUTOMATED CHECK-IN ROUND COMPLETE *** Success: {successful_sends}/{total_attempted} ({success_rate:.1f}%)")
            
            except asyncio.CancelledError:
                logger.info("SWIM_ZMQ_BRIDGE: Stability monitoring and check-in messaging trigger cancelled")
                break
            except Exception as e:
                logger.error(f"SWIM_ZMQ_BRIDGE: Error in stability monitoring/check-in trigger: {e}", exc_info=True)


async def setup_bandwidth_limits(node: Node, config: Dict[str, Any]) -> None:
    if not config.get("RATE_LIMITING_ENABLED", False): return
    if not node.bandwidth_monitor:
        logger.warning("SWIM_BANDWIDTH: Rate limiting enabled but bandwidth monitor not available on node.")
        return
    from swim.metrics.bandwidth import Direction
    inbound_limit = config.get("MAX_INBOUND_RATE", 0)
    outbound_limit = config.get("MAX_OUTBOUND_RATE", 0)
    if inbound_limit > 0:
        node.bandwidth_monitor.set_rate_limit(Direction.INBOUND, inbound_limit)
        logger.info(f"Set inbound bandwidth limit to {inbound_limit} bytes/sec")
    if outbound_limit > 0:
        node.bandwidth_monitor.set_rate_limit(Direction.OUTBOUND, outbound_limit)
        logger.info(f"Set outbound bandwidth limit to {outbound_limit} bytes/sec")


async def setup_metrics_reporting(node: Node, config: Dict[str, Any]) -> Optional[asyncio.Task]:
    if not config.get("METRICS_ENABLED", True) or not node.metrics_collector: return None
    interval = config.get("METRICS_REPORT_INTERVAL", 60.0)
    class MetricsReportGeneratedEvent(SwimEvent):
        category = EventCategory.APPLICATION
        severity = EventSeverity.INFO
        def _event_specific_data(self) -> Dict[str, Any]: return self.metadata
    async def report_metrics():
        while True:
            try:
                report = node.get_metrics_report()
                if report:
                    metrics_data = report.get("metrics", {})
                    alive_count = metrics_data.get("gauge", {}).get("member_count", {}).get("alive", {}).get("value",0)
                    suspect_count = metrics_data.get("gauge", {}).get("member_count", {}).get("suspect", {}).get("value",0)
                    total_count = metrics_data.get("gauge", {}).get("member_count", {}).get("total", {}).get("value",0)
                    bandwidth_report = report.get("bandwidth", {})
                    inbound_rate = bandwidth_report.get("current_rates", {}).get("inbound", 0)
                    outbound_rate = bandwidth_report.get("current_rates", {}).get("outbound", 0)
                    logger.info(
                        f"SWIM_METRICS: {alive_count} alive, {suspect_count} suspect, {total_count} total. "
                        f"BW: {inbound_rate:.2f} B/s IN, {outbound_rate:.2f} B/s OUT."
                    )
                    recommendations = bandwidth_report.get("recommendations", [])
                    for rec in recommendations:
                        if rec.get("type") == "warning":
                            logger.warning(f"SWIM_BANDWIDTH_REC: {rec.get('message')} - {rec.get('suggestion')}")
                    if node.event_dispatcher:
                        event = MetricsReportGeneratedEvent(
                            source_node=f"{node.transport.local_address[0]}:{node.transport.local_address[1]}",
                            metadata={ "alive_count": alive_count, "suspect_count": suspect_count, "total_count": total_count, "inbound_rate": inbound_rate, "outbound_rate": outbound_rate, "recommendations": [rec.get("message") for rec in recommendations if rec.get("type") == "warning"] }
                        )
                        node.event_dispatcher.emit(event)
            except Exception as e: logger.error(f"SWIM_METRICS: Error in metrics reporting: {e}", exc_info=True)
            await asyncio.sleep(interval)
    task = asyncio.create_task(report_metrics())
    return task


async def setup_metrics_api(node: Node, config: Dict[str, Any]) -> Optional[Any]:
    if not config.get("METRICS_API_ENABLED", False) or not config.get("METRICS_ENABLED", True): return None
    try:
        from swim.metrics.api.integration import setup_metrics_api as setup_api_server
        node_addr = node.transport.local_address
        api_host = config.get("METRICS_API_HOST", node_addr[0])
        api_port = config.get("METRICS_API_PORT", node_addr[1] + 80)
        integration = setup_api_server(node, api_host, api_port)
        logger.info(f"SWIM_METRICS_API: Started on http://{api_host}:{api_port}")
        if node.event_dispatcher:
            class MetricsAPIStartedEvent(SwimEvent):
                category = EventCategory.APPLICATION
                severity = EventSeverity.INFO
                def _event_specific_data(self) -> Dict[str, Any]: return self.metadata
            event = MetricsAPIStartedEvent( source_node=f"{node.transport.local_address[0]}:{node.transport.local_address[1]}", metadata={"api_host": api_host, "api_port": api_port, "url": f"http://{api_host}:{api_port}"} )
            node.event_dispatcher.emit(event)
        return integration
    except ImportError: logger.error("SWIM_METRICS_API: Failed to import metrics API modules (fastapi/uvicorn likely missing).")
    except Exception as e: logger.error(f"SWIM_METRICS_API: Failed to set up metrics API: {e}", exc_info=True)
    return None


async def main_async(args: Optional[List[str]] = None) -> None:
    parsed_args = parse_args(args)
    config = get_config()
    config = apply_args_to_config(parsed_args, config)
    
    errors = validate_config(config)
    if errors:
        print("Configuration errors:")
        for key, error_msg in errors.items(): print(f"  {key}: {error_msg}")
        sys.exit(1)
    
    if parsed_args.save_config:
        if save_config(config, parsed_args.save_config): print(f"Configuration saved to {parsed_args.save_config}")
        else: print(f"Failed to save configuration to {parsed_args.save_config}"); sys.exit(1)
    
    global logger
    logger = setup_logging( "swim", level=getattr(logging, config.get("LOG_LEVEL", "INFO")), log_file=config.get("LOG_FILE") if config.get("LOG_FILE") else None, json_logging=config.get("JSON_LOGGING", False) )
    
    swim_node = None
    zmq_agent = None
    swim_zmq_bridge = None
    metrics_api_integration = None 
    
    try:
        bind_addr = parse_address(parsed_args.addr)
        seed_addrs = [parse_address(seed) for seed in parsed_args.seeds]
        
        logger.info(f"MAIN: Starting SWIM P2P node with ZMQ messaging integration")
        logger.info(f"MAIN: SWIM node binding to {bind_addr[0]}:{bind_addr[1]}")
        
        transport_type = parsed_args.transport
        transport = await create_transport(transport_type, config)
        logger.info(f"SWIM_TRANSPORT: Using {transport_type.upper()} transport")
        
        metrics_collector_instance = None
        if config.get("METRICS_ENABLED", True):
            from swim.metrics.collector import MetricsCollector
            node_id_for_metrics = f"{bind_addr[0]}:{bind_addr[1]}"
            metrics_collector_instance = MetricsCollector(node_id_for_metrics)
            logger.info(f"SWIM_METRICS: Metrics collector initialized for {node_id_for_metrics}")
        
        event_dispatcher_instance = await setup_event_system(config, metrics_collector_instance)
        if event_dispatcher_instance: logger.info("SWIM_EVENTS: Event system initialized")
        else: logger.info("SWIM_EVENTS: Event system disabled by configuration.")
        
        logger.info("SWIM_NODE: Creating SWIM node")
        swim_node = await Node.create( bind_addr=bind_addr, transport=transport, seed_addrs=seed_addrs, config=config, event_dispatcher=event_dispatcher_instance )

        if config.get("LIFEGUARD_ENABLED", True) and swim_node: 
            logger.info("SWIM_LIFEGUARD: Initializing Lifeguard enhancements")
            if hasattr(swim_node, '_initialize_lifeguard'): swim_node._initialize_lifeguard() 
        
        if swim_node: 
            await setup_bandwidth_limits(swim_node, config)
            metrics_reporting_task = await setup_metrics_reporting(swim_node, config)
            if metrics_reporting_task:
                swim_node.tasks.add(metrics_reporting_task)
                metrics_reporting_task.add_done_callback(swim_node.tasks.discard)
            metrics_api_integration = await setup_metrics_api(swim_node, config)
        
        logger.info("ZMQ_INTEGRATION: Setting up ZMQ messaging integration")
        zmq_agent = await setup_zmq_integration(bind_addr, config, event_dispatcher_instance)
        
        if zmq_agent and swim_node: 
            logger.info("SWIM_ZMQ_BRIDGE: Setting up SWIM-ZMQ bridge")
            swim_zmq_bridge = SWIMZMQBridge(swim_node, zmq_agent, config)
            await swim_zmq_bridge.start()
            logger.info("SWIM_ZMQ_BRIDGE: SWIM-ZMQ bridge active")
        elif config.get("ZMQ_ENABLED", True): logger.error("ZMQ_INTEGRATION: ZMQ enabled but ZMQ agent or SWIM node failed to initialize. Bridge not started.")
        else: logger.info("ZMQ_INTEGRATION: ZMQ messaging integration disabled")
        
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler( sig, lambda s=sig: asyncio.create_task(shutdown(swim_node, zmq_agent, swim_zmq_bridge, metrics_api_integration, s)) )
        
        logger.info(f"SWIM_READY: SWIM node started at {bind_addr[0]}:{bind_addr[1]} with {transport_type} transport")
        
        features = [ "push-pull synchronization" if config.get("PUSH_PULL_SYNC_ENABLED", True) else None, "adaptive timing" if config.get("ADAPTIVE_TIMING_ENABLED", True) else None, "metrics collection" if config.get("METRICS_ENABLED", True) else None, "rate limiting" if config.get("RATE_LIMITING_ENABLED", False) else None, "metrics API" if config.get("METRICS_API_ENABLED", False) else None, "event system" if config.get("EVENTS_ENABLED", True) else None, "Lifeguard enhancements" if config.get("LIFEGUARD_ENABLED", True) else None, "ZMQ messaging" if config.get("ZMQ_ENABLED", True) and zmq_agent else None, ]
        enabled_features = [f for f in features if f]
        if enabled_features: logger.info(f"ENABLED_FEATURES: {', '.join(enabled_features)}")
        if seed_addrs: logger.info(f"SWIM_SEEDS: Joining cluster via: {', '.join(f'{a[0]}:{a[1]}' for a in seed_addrs)}")
        
        if swim_node:
            logger.info("SWIM_START: Starting SWIM protocol")
            await swim_node.start()
            logger.info("SWIM_READY: SWIM protocol active")
        else:
            logger.error("SWIM_NODE: SWIM node failed to initialize. Cannot start protocol.")
            return 

        if zmq_agent: logger.info(f"ZMQ_READY: ZMQ messaging ready for node '{config.get('NODE_NAME', 'Unnamed')}'")
        if config.get("SEND_ON_JOIN", True): logger.info(f"AUTOMATED_CHECK_IN: Enabled for node '{config.get('NODE_NAME', 'Unnamed')}'")
        
        logger.info("MAIN: System ready. Use Ctrl+C to shutdown gracefully.")
        
        while True: 
            if swim_node and not swim_node.running: logger.error("MAIN_LOOP: SWIM node is no longer running. Shutting down."); break
            if zmq_agent and hasattr(zmq_agent, '_running') and not zmq_agent._running: logger.error("MAIN_LOOP: ZMQ Agent is no longer running. Shutting down."); break
            await asyncio.sleep(5) 
            
    except PortValidationError as e: logger.error(f"PORT_VALIDATION_ERROR: {e}"); sys.exit(1)
    except ValueError as e: logger.error(f"MAIN_ERROR: Configuration or address parsing error: {e}"); sys.exit(1)
    except KeyboardInterrupt: logger.info("MAIN: Keyboard interrupt received, initiating shutdown...")
    except Exception as e: logger.exception(f"MAIN_ERROR: Unexpected error: {e}"); sys.exit(1)
    finally: 
        logger.info("MAIN: Reached finally block, ensuring shutdown sequence is called.")
        current_loop = asyncio.get_event_loop()
        if not current_loop.is_closed():
            if not current_loop.is_running():
                 async def final_cleanup(): await shutdown(swim_node, zmq_agent, swim_zmq_bridge, metrics_api_integration, "FINALLY_BLOCK_STOPPED_LOOP")
                 current_loop.run_until_complete(final_cleanup())
            else:
                 logger.info("MAIN_FINALLY: Event loop is running, scheduling final shutdown.")
                 asyncio.create_task(shutdown(swim_node, zmq_agent, swim_zmq_bridge, metrics_api_integration, "FINALLY_BLOCK_RUNNING_LOOP"))


async def shutdown(swim_node: Optional[Node], 
                  zmq_agent: Optional[ZMQAgentIntegration] = None, 
                  swim_zmq_bridge: Optional[SWIMZMQBridge] = None, 
                  metrics_api_integration: Optional[Any] = None, 
                  signal_name: Optional[str] = None) -> None:
    
    if hasattr(shutdown, 'shutting_down') and shutdown.shutting_down:
        logger.info("SHUTDOWN: Already in progress, skipping redundant call.")
        return
    shutdown.shutting_down = True

    if signal_name: logger.info(f"SHUTDOWN: Received signal {signal_name}, gracefully stopping all components")
    else: logger.info("SHUTDOWN: Gracefully stopping all components")
    
    if swim_node and swim_node.event_dispatcher:
        class NodeShutdownInitiatedEvent(SwimEvent):
            category = EventCategory.SYSTEM
            severity = EventSeverity.INFO
            def _event_specific_data(self) -> Dict[str, Any]: return self.metadata
        event = NodeShutdownInitiatedEvent( source_node=f"{swim_node.transport.local_address[0]}:{swim_node.transport.local_address[1]}" if swim_node.transport.local_address else "unknown", metadata={ "uptime": time.time() - swim_node._start_time if hasattr(swim_node, '_start_time') else None, "protocol_cycles": swim_node._protocol_cycles if hasattr(swim_node, '_protocol_cycles') else 0, "reason": signal_name or "application_exit" } )
        swim_node.event_dispatcher.emit(event)
    
    if swim_zmq_bridge:
        try: logger.info("SHUTDOWN: Stopping SWIM-ZMQ bridge"); await swim_zmq_bridge.stop(); logger.info("SHUTDOWN: SWIM-ZMQ bridge stopped")
        except Exception as e: logger.error(f"SHUTDOWN: Error stopping SWIM-ZMQ bridge: {e}", exc_info=True)
    if zmq_agent:
        try: logger.info("SHUTDOWN: Stopping ZMQ agent integration"); await zmq_agent.stop(); logger.info("SHUTDOWN: ZMQ agent integration stopped")
        except Exception as e: logger.error(f"SHUTDOWN: Error stopping ZMQ agent: {e}", exc_info=True)
    if metrics_api_integration and hasattr(metrics_api_integration, 'stop'): 
        try: logger.info("SHUTDOWN: Stopping metrics API"); await metrics_api_integration.stop() if asyncio.iscoroutinefunction(metrics_api_integration.stop) else metrics_api_integration.stop(); logger.info("SHUTDOWN: Metrics API stopped") # type: ignore
        except Exception as e: logger.error(f"SHUTDOWN: Error stopping metrics API: {e}", exc_info=True)
    if swim_node:
        try: logger.info("SHUTDOWN: Stopping SWIM node"); await swim_node.stop(); logger.info("SHUTDOWN: SWIM node stopped")
        except Exception as e: logger.error(f"SHUTDOWN: Error stopping SWIM node: {e}", exc_info=True)
    
    current_task = asyncio.current_task()
    tasks = [t for t in asyncio.all_tasks() if t is not current_task]
    if tasks:
        logger.info(f"SHUTDOWN: Cancelling {len(tasks)} remaining tasks")
        for task in tasks:
            if not task.done(): task.cancel()
        await asyncio.sleep(0.1) 

    logger.info("SHUTDOWN: All components stopped gracefully")
    loop = asyncio.get_event_loop()
    if loop.is_running(): logger.info("SHUTDOWN: Stopping event loop."); loop.stop()
    delattr(shutdown, 'shutting_down')


def main(args: Optional[List[str]] = None) -> None:
    """ Main entry point for the SWIM node with ZMQ integration. """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(main_async(args))
    except KeyboardInterrupt: logger.info("MAIN_SYNC: Keyboard interrupt caught. Shutdown should be handled by signal handler.")
    except Exception as e: logger.critical(f"MAIN_SYNC: Unhandled exception in main_async: {e}", exc_info=True)
    finally:
        logger.info("MAIN_SYNC: Ensuring event loop is closed.")
        if not loop.is_closed():
            remaining_tasks = asyncio.all_tasks(loop=loop)
            if remaining_tasks:
                logger.info(f"MAIN_SYNC_FINALLY: {len(remaining_tasks)} tasks still pending. Cancelling...")
                for task in remaining_tasks:
                    if not task.done(): task.cancel()
                loop.run_until_complete(asyncio.gather(*remaining_tasks, return_exceptions=True))
            if loop.is_running(): logger.warning("MAIN_SYNC_FINALLY: Loop still running unexpectedly, forcing stop."); loop.stop()
            logger.info("MAIN_SYNC_FINALLY: Closing event loop.")
            loop.close()

if __name__ == "__main__":
    main()