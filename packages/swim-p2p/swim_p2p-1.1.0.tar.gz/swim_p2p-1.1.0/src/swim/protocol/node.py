"""
Node implementation for SWIM P2P with Lifeguard enhancements.

This module provides the main Node class that coordinates the SWIM protocol
components and manages the node lifecycle, with enhanced reliability features
from Hashicorp's Lifeguard and production-ready port validation.
"""

import asyncio
import logging
import time
import uuid
import random
import socket
from typing import Dict, List, Optional, Tuple, Any, Set, TYPE_CHECKING

from swim.transport.base import Transport
from swim.transport.hybrid import HybridTransport
from swim.protocol.member import MemberList, MemberState
from swim.protocol.failure_detector import FailureDetector
from swim.protocol.disseminator import GossipService
from swim.protocol.sync import SyncService
from swim.utils.serialization import deserialize_message

# Import network utilities for port validation
from swim.utils.network import check_port_available, PortConfig, PortManager

# Import metrics components
from swim.metrics.collector import MetricsCollector
from swim.metrics.latency import LatencyTracker
from swim.metrics.bandwidth import BandwidthMonitor, Direction

# Import Lifeguard components
from swim.lifeguard.awareness import AwarenessService, get_awareness_service
from swim.lifeguard.timing import TimingService, get_timing_service
from swim.lifeguard.probe_rate import ProbeRateService, get_probe_rate_service

# Import event system components using TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from swim.events.dispatcher import EventDispatcher
    from swim.events.types import Event

logger = logging.getLogger(__name__)


class PortValidationError(Exception):
    """Raised when port validation fails during node creation."""
    pass


class NodeConfigError(Exception):
    """Raised when node configuration is invalid."""
    pass


class Node:
    """
    Main SWIM protocol node with enhanced reliability features from Lifeguard.
    
    This class coordinates the SWIM protocol components and manages
    the node lifecycle including heartbeating and message handling,
    with support for push-pull synchronization, adaptive timing, and
    production-ready port validation.
    """
    
    def __init__(
        self,
        transport: Transport,
        members: MemberList,
        failure_detector: FailureDetector,
        gossip: GossipService,
        sync_service: Optional['SyncService'] = None,
        config: Optional[Dict[str, Any]] = None,
        event_dispatcher: Optional['EventDispatcher'] = None,
        port_manager: Optional[PortManager] = None
    ):
        """
        Initialize a new SWIM node with Lifeguard enhancements.
        
        Args:
            transport: The transport to use for communication.
            members: The member list to maintain.
            failure_detector: The failure detector to use.
            gossip: The gossip service to use.
            sync_service: Optional sync service for push-pull synchronization.
            config: Optional configuration parameters.
            event_dispatcher: Optional event dispatcher for emitting events.
            port_manager: Optional port manager for production deployments.
        """
        self.transport = transport
        self.members = members
        self.failure_detector = failure_detector
        self.gossip = gossip
        self.sync_service = sync_service
        self.config = config or {}
        self.event_dispatcher = event_dispatcher
        self.port_manager = port_manager
        
        # Connect event dispatcher to member list if provided
        if self.event_dispatcher and self.members:
            self.members.event_dispatcher = self.event_dispatcher
        
        # Default configuration
        self.config.setdefault("HEARTBEAT_INTERVAL", 1.0)
        self.config.setdefault("PROTOCOL_PERIOD", 1.0)
        self.config.setdefault("SUSPECT_TIMEOUT", 5.0)
        self.config.setdefault("ADAPTIVE_TIMING_ENABLED", True)
        self.config.setdefault("PROTOCOL_PERIOD_MIN", 0.5)
        self.config.setdefault("PROTOCOL_PERIOD_MAX", 2.0)
        self.config.setdefault("PROTOCOL_PERIOD_ADJUSTMENT_FACTOR", 0.1)
        self.config.setdefault("METRICS_ENABLED", True)
        self.config.setdefault("LIFEGUARD_ENABLED", True)  # Enable Lifeguard by default
        self.config.setdefault("PORT_VALIDATION_ENABLED", True)  # Enable port validation by default
        self.config.setdefault("PORT_VALIDATION_TIMEOUT", 1.0)  # Port check timeout
        
        # Node state
        self.running = False
        self.tasks: Set[asyncio.Task] = set()
        
        # Operation statistics
        self._protocol_cycles = 0
        self._ping_operations = 0
        self._probe_operations = 0
        self._last_protocol_cycle_time = 0
        self._protocol_cycle_times: List[float] = []
        
        # Check if we have a hybrid transport
        self.hybrid_transport = None
        if isinstance(transport, HybridTransport):
            self.hybrid_transport = transport
        
        # Initialize metrics components if enabled
        self.metrics_collector = None
        self.latency_tracker = None
        self.bandwidth_monitor = None
        
        if self.config.get("METRICS_ENABLED", True):
            node_id = f"{self.transport.local_address[0]}:{self.transport.local_address[1]}"
            self.metrics_collector = MetricsCollector(node_id)
            self.latency_tracker = LatencyTracker(self.metrics_collector)
            self.bandwidth_monitor = BandwidthMonitor(self.metrics_collector)
            
            # Start metrics collection
            self.metrics_collector.start()
            
            logger.info(f"Metrics collection enabled for node {node_id}")
        
        # Initialize Lifeguard components if enabled
        self.awareness_service = None
        self.timing_service = None
        self.probe_rate_service = None
        
        if self.config.get("LIFEGUARD_ENABLED", True):
            self._initialize_lifeguard()
            logger.info("Lifeguard enhancements enabled")
        
        logger.info(f"Node initialized at {self.transport.local_address[0]}:{self.transport.local_address[1]} with enhanced reliability features")
    
    @staticmethod
    def validate_port_availability(host: str, port: int, timeout: float = 1.0) -> bool:
        """
        Validate that a port is available for binding.
        
        Args:
            host: Host to check port on
            port: Port number to validate
            timeout: Timeout for the validation check
            
        Returns:
            True if port is available, False otherwise
        """
        return check_port_available(host, port, timeout)
    
    @staticmethod
    def validate_bind_address(bind_addr: Tuple[str, int], timeout: float = 1.0) -> None:
        """
        Validate that a bind address is available.
        
        Args:
            bind_addr: Address tuple (host, port) to validate
            timeout: Timeout for the validation check
            
        Raises:
            PortValidationError: If the port is not available
            NodeConfigError: If the address format is invalid
        """
        if not bind_addr or len(bind_addr) != 2:
            raise NodeConfigError(f"Invalid bind address format: {bind_addr}")
        
        host, port = bind_addr
        
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise NodeConfigError(f"Invalid port number: {port}")
        
        if not isinstance(host, str) or not host:
            raise NodeConfigError(f"Invalid host: {host}")
        
        # Check if port is available
        if not check_port_available(host, port, timeout):
            raise PortValidationError(f"Port {port} is not available on {host}")
        
        logger.debug(f"Port validation successful for {host}:{port}")
    
    @staticmethod
    def validate_seed_addresses(seed_addrs: List[Tuple[str, int]]) -> None:
        """
        Validate seed addresses format.
        
        Args:
            seed_addrs: List of seed addresses to validate
            
        Raises:
            NodeConfigError: If any seed address is invalid
        """
        if not seed_addrs:
            return
        
        for i, addr in enumerate(seed_addrs):
            if not addr or len(addr) != 2:
                raise NodeConfigError(f"Invalid seed address format at index {i}: {addr}")
            
            host, port = addr
            
            if not isinstance(port, int) or port < 1 or port > 65535:
                raise NodeConfigError(f"Invalid port in seed address {i}: {port}")
            
            if not isinstance(host, str) or not host:
                raise NodeConfigError(f"Invalid host in seed address {i}: {host}")
        
        logger.debug(f"Seed address validation successful for {len(seed_addrs)} addresses")
    
    def _initialize_lifeguard(self) -> None:
        """Initialize Lifeguard enhancement services."""
        # Create awareness service
        self.awareness_service = get_awareness_service(
            metrics_collector=self.metrics_collector
        )
        
        # Create timing service
        self.timing_service = get_timing_service(
            latency_tracker=self.latency_tracker,
            awareness_service=self.awareness_service,
            metrics_collector=self.metrics_collector
        )
        
        # Create probe rate service
        self.probe_rate_service = get_probe_rate_service(
            latency_tracker=self.latency_tracker,
            bandwidth_monitor=self.bandwidth_monitor,
            awareness_service=self.awareness_service,
            timing_service=self.timing_service,
            metrics_collector=self.metrics_collector
        )
        
        # Connect services to their respective components
        if self.failure_detector:
            # Update failure detector with services
            self.failure_detector.awareness_service = self.awareness_service
            self.failure_detector.timing_service = self.timing_service
            self.failure_detector.probe_rate_service = self.probe_rate_service
    
    @classmethod
    async def create(
        cls,
        bind_addr: Tuple[str, int],
        transport: Transport,
        seed_addrs: Optional[List[Tuple[str, int]]] = None,
        config: Optional[Dict[str, Any]] = None,
        event_dispatcher: Optional['EventDispatcher'] = None,
        port_manager: Optional[PortManager] = None,
        validate_ports: bool = True
    ) -> "Node":
        """
        Create and initialize a new SWIM node with enhanced port validation.
        
        This factory method creates and wires up all the required components
        with comprehensive validation for production deployments.
        
        Args:
            bind_addr: The address to bind the transport to.
            transport: The transport to use.
            seed_addrs: Optional list of seed node addresses to join.
            config: Optional configuration parameters.
            event_dispatcher: Optional event dispatcher for emitting events.
            port_manager: Optional port manager for production deployments.
            validate_ports: Whether to validate port availability (default: True).
            
        Returns:
            A new initialized Node instance.
            
        Raises:
            PortValidationError: If port validation fails
            NodeConfigError: If configuration is invalid
            RuntimeError: If node creation fails
        """
        config = config or {}
        
        try:
            # Validate configuration
            if not bind_addr:
                raise NodeConfigError("bind_addr is required")
            
            if not transport:
                raise NodeConfigError("transport is required")
            
            # Validate port availability if enabled
            if validate_ports and config.get("PORT_VALIDATION_ENABLED", True):
                timeout = config.get("PORT_VALIDATION_TIMEOUT", 1.0)
                
                logger.info(f"Validating port availability for {bind_addr[0]}:{bind_addr[1]}")
                cls.validate_bind_address(bind_addr, timeout)
                
                # Validate seed addresses format
                if seed_addrs:
                    cls.validate_seed_addresses(seed_addrs)
                
                logger.info("Port validation completed successfully")
            
            # Register port with port manager if provided
            if port_manager:
                node_id = f"{bind_addr[0]}:{bind_addr[1]}"
                # Note: In production, you might want to register the port pair
                # but for SWIM nodes, we typically only need to track the SWIM port
                logger.info(f"Registering node {node_id} with port manager")
            
            # Bind the transport with error handling
            try:
                await transport.bind(bind_addr)
                logger.info(f"Transport successfully bound to {bind_addr[0]}:{bind_addr[1]}")
            except OSError as e:
                if "Address already in use" in str(e):
                    raise PortValidationError(f"Port {bind_addr[1]} is already in use on {bind_addr[0]}")
                elif "Permission denied" in str(e):
                    raise PortValidationError(f"Permission denied for port {bind_addr[1]} on {bind_addr[0]}")
                else:
                    raise RuntimeError(f"Failed to bind transport to {bind_addr[0]}:{bind_addr[1]}: {e}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error binding transport: {e}")
            
            # Create member list with event dispatcher
            members = MemberList(bind_addr, event_dispatcher=event_dispatcher)
            
            # Add seed nodes with validation
            if seed_addrs:
                added_seeds = 0
                for addr in seed_addrs:
                    if addr != bind_addr:  # Don't add self as seed
                        try:
                            members.add_member(addr)
                            added_seeds += 1
                            logger.debug(f"Added seed node: {addr[0]}:{addr[1]}")
                        except Exception as e:
                            logger.warning(f"Failed to add seed node {addr[0]}:{addr[1]}: {e}")
                
                logger.info(f"Added {added_seeds} seed nodes to member list")
            
            # Create failure detector
            failure_detector = FailureDetector(
                transport=transport,
                members=members,
                config=config
            )
            
            # Create gossip service
            gossip = GossipService(
                transport=transport,
                members=members,
                config=config
            )
            
            # Create sync service if enabled
            sync_service = None
            if config.get("PUSH_PULL_SYNC_ENABLED", True):
                sync_service = SyncService(
                    transport=transport,
                    members=members,
                    config=config
                )
                logger.info("Push-pull sync service enabled")
            
            # Create and return node
            node = cls(
                transport=transport,
                members=members,
                failure_detector=failure_detector,
                gossip=gossip,
                sync_service=sync_service,
                config=config,
                event_dispatcher=event_dispatcher,
                port_manager=port_manager
            )
            
            logger.info(f"Node created successfully at {bind_addr[0]}:{bind_addr[1]}")
            return node
            
        except (PortValidationError, NodeConfigError) as e:
            logger.error(f"Node creation failed due to validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during node creation: {e}")
            raise RuntimeError(f"Failed to create node: {e}")
    
    @classmethod
    async def create_with_port_manager(
        cls,
        node_id: str,
        port_manager: PortManager,
        transport: Transport,
        seed_addrs: Optional[List[Tuple[str, int]]] = None,
        config: Optional[Dict[str, Any]] = None,
        event_dispatcher: Optional['EventDispatcher'] = None,
        host: str = "127.0.0.1"
    ) -> "Node":
        """
        Create a node using the port manager for automatic port allocation.
        
        Args:
            node_id: Unique identifier for the node
            port_manager: Port manager for allocation
            transport: Transport to use
            seed_addrs: Optional seed addresses
            config: Optional configuration
            event_dispatcher: Optional event dispatcher
            host: Host to bind to (default: 127.0.0.1)
            
        Returns:
            New Node instance with allocated ports
            
        Raises:
            PortValidationError: If port allocation fails
        """
        try:
            # Allocate port pair (SWIM port only for pure SWIM nodes)
            # Note: For SWIM-ZMQ integration, you'd allocate both ports
            swim_port, _ = port_manager.allocate_port_pair(node_id, host)
            bind_addr = (host, swim_port)
            
            logger.info(f"Allocated SWIM port {swim_port} for node {node_id}")
            
            # Create node with allocated address
            return await cls.create(
                bind_addr=bind_addr,
                transport=transport,
                seed_addrs=seed_addrs,
                config=config,
                event_dispatcher=event_dispatcher,
                port_manager=port_manager,
                validate_ports=False  # Skip validation since port manager handles it
            )
            
        except Exception as e:
            # Clean up allocated ports on failure
            try:
                port_manager.release_ports(node_id)
            except:
                pass
            raise PortValidationError(f"Failed to create node with port manager: {e}")
    
    async def start(self) -> None:
        """
        Start the SWIM node.
        
        This method starts the protocol tasks and message handler.
        """
        if self.running:
            return
        
        self.running = True
        
        # Validate that transport is still bound
        if not hasattr(self.transport, 'local_address') or not self.transport.local_address:
            raise RuntimeError("Transport is not properly bound")
        
        # Start protocol task
        protocol_task = asyncio.create_task(self._protocol_loop())
        self.tasks.add(protocol_task)
        protocol_task.add_done_callback(self.tasks.discard)
        
        # Start sync service if available
        if self.sync_service:
            sync_task = asyncio.create_task(self.sync_service.start())
            self.tasks.add(sync_task)
            sync_task.add_done_callback(self.tasks.discard)
        
        # Start message handler
        await self.transport.start_receiver(self._handle_message)
        
        # Record node start event in metrics
        if self.metrics_collector:
            self.metrics_collector.record_event(
                name="node_event",
                value="start",
                labels={"addr": f"{self.transport.local_address[0]}:{self.transport.local_address[1]}"}
            )
        
        # Emit node start event if event dispatcher is available
        if self.event_dispatcher:
            # Import here to avoid circular imports
            from swim.events.types import NodeStartedEvent
            
            event = NodeStartedEvent(
                source_node=f"{self.transport.local_address[0]}:{self.transport.local_address[1]}",
                metadata={
                    "transport_type": self.transport.__class__.__name__,
                    "seed_count": len(self.members.get_all_members()) - 1,  # Exclude self
                    "lifeguard_enabled": self.config.get("LIFEGUARD_ENABLED", True),
                    "port_validation_enabled": self.config.get("PORT_VALIDATION_ENABLED", True)
                }
            )
            self.event_dispatcher.emit(event)
        
        logger.info(f"Node started at {self.transport.local_address[0]}:{self.transport.local_address[1]}")
    
    async def stop(self) -> None:
        """
        Stop the SWIM node and clean up resources.
        
        This method stops all tasks, closes the transport, and releases ports.
        """
        if not self.running:
            return
        
        self.running = False
        
        # Emit node stop event if event dispatcher is available
        if self.event_dispatcher:
            # Import here to avoid circular imports
            from swim.events.types import NodeStoppedEvent
            
            event = NodeStoppedEvent(
                source_node=f"{self.transport.local_address[0]}:{self.transport.local_address[1]}",
                metadata={
                    "uptime": time.time() - self._start_time if hasattr(self, '_start_time') else None,
                    "protocol_cycles": self._protocol_cycles,
                    "ping_operations": self._ping_operations
                }
            )
            self.event_dispatcher.emit(event)
        
        # FIXED: Stop sync service BEFORE cancelling tasks and closing transport
        if self.sync_service:
            try:
                await self.sync_service.stop()
                logger.debug("Sync service stopped")
            except Exception as e:
                logger.warning(f"Error stopping sync service: {e}")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks.clear()
        
        # FIXED: Add small delay to let any remaining operations complete
        await asyncio.sleep(0.1)
        
        # Close transport
        try:
            await self.transport.close()
        except Exception as e:
            logger.warning(f"Error closing transport: {e}")
        
        # Release ports if using port manager
        if self.port_manager and hasattr(self.transport, 'local_address'):
            node_id = f"{self.transport.local_address[0]}:{self.transport.local_address[1]}"
            try:
                self.port_manager.release_ports(node_id)
                logger.info(f"Released ports for node {node_id}")
            except Exception as e:
                logger.warning(f"Error releasing ports for node {node_id}: {e}")
        
        # Record node stop event in metrics
        if self.metrics_collector:
            self.metrics_collector.record_event(
                name="node_event",
                value="stop",
                labels={"addr": f"{self.transport.local_address[0]}:{self.transport.local_address[1]}"}
            )
            
            # Stop metrics collection
            self.metrics_collector.stop()
        
        logger.info(f"Node stopped at {self.transport.local_address[0]}:{self.transport.local_address[1]}")
    
    def _adjust_protocol_period(self) -> float:
        """
        Adjust the protocol period based on network conditions.
        
        Returns:
            The adjusted protocol period in seconds.
        """
        # Use Lifeguard timing service if available
        if self.timing_service and self.config.get("LIFEGUARD_ENABLED", True):
            # Get network conditions based on recent protocol cycle times
            network_conditions = None
            if len(self._protocol_cycle_times) >= 5:
                avg_cycle_time = sum(self._protocol_cycle_times) / len(self._protocol_cycle_times)
                network_conditions = {
                    "avg_cycle_time": avg_cycle_time,
                    "congested": avg_cycle_time > self.config["PROTOCOL_PERIOD"] * 0.8
                }
            
            period = self.timing_service.get_protocol_period(network_conditions)
            
            # Record protocol period in metrics if enabled
            if self.metrics_collector:
                self.metrics_collector.record_gauge(
                    name="protocol_period",
                    value=period
                )
            
            return period
        
        # Fallback to original implementation if Lifeguard is disabled
        period = self.config["PROTOCOL_PERIOD"]
        
        # Only adjust the period if adaptive timing is enabled
        if self.config["ADAPTIVE_TIMING_ENABLED"]:
            # If we have enough data, adjust the period based on network conditions
            if len(self._protocol_cycle_times) >= 5:
                # Calculate average of recent cycle times
                avg_cycle_time = sum(self._protocol_cycle_times) / len(self._protocol_cycle_times)
                
                # Adjust period based on average cycle time
                if avg_cycle_time > period * 0.8:
                    # Network is slow, increase period
                    period = min(
                        period * (1 + self.config["PROTOCOL_PERIOD_ADJUSTMENT_FACTOR"]),
                        self.config["PROTOCOL_PERIOD_MAX"]
                    )
                    logger.debug(f"Increasing protocol period to {period:.2f}s due to slow network")
                elif avg_cycle_time < period * 0.3:
                    # Network is fast, decrease period
                    period = max(
                        period * (1 - self.config["PROTOCOL_PERIOD_ADJUSTMENT_FACTOR"]),
                        self.config["PROTOCOL_PERIOD_MIN"]
                    )
                    logger.debug(f"Decreasing protocol period to {period:.2f}s due to fast network")
        
        # Always record protocol period in metrics if metrics are enabled
        if self.metrics_collector:
            self.metrics_collector.record_gauge(
                name="protocol_period",
                value=period
            )
        
        return period
    
    async def _protocol_loop(self) -> None:
        """
        Main protocol loop with adaptive timing.
        
        This method runs the SWIM protocol periodically, including:
        1. Sending heartbeats
        2. Checking suspect members
        3. Probing random members
        """
        try:
            # Store start time for uptime tracking
            self._start_time = time.time()
            
            while self.running:
                try:
                    # Generate a cycle ID for tracking
                    cycle_id = str(uuid.uuid4())[:8]
                    self._protocol_cycles += 1
                    
                    start_time = time.time()
                    logger.debug(f"[{cycle_id}] Starting protocol cycle #{self._protocol_cycles}")
                    
                    # Send heartbeat
                    await self.gossip.send_heartbeat()
                    
                    # Check suspect members
                    logger.debug(f"[{cycle_id}] Checking suspect members")
                    await self._check_suspects()
                    
                    # Probe a random member
                    logger.debug(f"[{cycle_id}] Probing random member")
                    await self._probe_random_member()
                    
                    # Summary of cluster state
                    alive_count = len(self.members.get_alive_members())
                    suspect_count = len(self.members.get_suspect_members())
                    dead_count = len([m for m in self.members.get_all_members() 
                                    if m.state == MemberState.DEAD])
                    total_count = len(self.members.get_all_members())
                    
                    # More detailed log about cluster stability
                    lifeguard_status = ""
                    if self.config.get("LIFEGUARD_ENABLED", False):
                        lifeguard_status = "LIFEGUARD: "
                        
                        # Report awareness values if available
                        if hasattr(self, 'awareness_service') and self.awareness_service:
                            awareness_values = self.awareness_service.get_all_awareness()
                            if awareness_values:
                                awareness_str = ", ".join([f"{addr}: {val}" for addr, val 
                                                        in awareness_values.items()])
                                lifeguard_status += f"Awareness values [{awareness_str}] "
                                
                        # Report adaptive timing if available
                        if hasattr(self, 'timing_service') and self.timing_service:
                            period = self._current_protocol_period if hasattr(self, '_current_protocol_period') else 1.0
                            lifeguard_status += f"Protocol period: {period:.2f}s "
                            
                        # Report any suspect/dead transitions
                        transitions = self._suspect_transitions if hasattr(self, '_suspect_transitions') else 0
                        false_positives = self._false_positives if hasattr(self, '_false_positives') else 0
                        lifeguard_status += f"Transitions: {transitions} False positives: {false_positives}"
                    
                    logger.info(f"[{cycle_id}] Cluster state: {alive_count} alive, {suspect_count} suspect, "
                            f"{dead_count} dead (total: {total_count}) {lifeguard_status}")
                    
                    # Record member counts in metrics
                    if self.metrics_collector:
                        self.metrics_collector.record_gauge(
                            name="member_count",
                            value=alive_count,
                            labels={"state": "alive"}
                        )
                        self.metrics_collector.record_gauge(
                            name="member_count",
                            value=suspect_count,
                            labels={"state": "suspect"}
                        )
                        self.metrics_collector.record_gauge(
                            name="member_count",
                            value=dead_count,
                            labels={"state": "dead"}
                        )
                        self.metrics_collector.record_gauge(
                            name="member_count",
                            value=total_count,
                            labels={"state": "total"}
                        )
                    
                    # Emit protocol cycle event if event dispatcher is available
                    if self.event_dispatcher and self._protocol_cycles % 10 == 0:  # Every 10 cycles
                        # Import here to avoid circular imports
                        from swim.events.types import ProtocolCycleEvent
                        
                        event = ProtocolCycleEvent(
                            source_node=f"{self.transport.local_address[0]}:{self.transport.local_address[1]}",
                            metadata={
                                "cycle_number": self._protocol_cycles,
                                "alive_count": alive_count,
                                "suspect_count": suspect_count,
                                "dead_count": dead_count,
                                "total_count": total_count
                            }
                        )
                        self.event_dispatcher.emit(event)
                    
                    # Track cycle time for adaptive timing
                    end_time = time.time()
                    cycle_time = end_time - start_time
                    self._last_protocol_cycle_time = cycle_time
                    
                    # Keep a rolling window of cycle times
                    self._protocol_cycle_times.append(cycle_time)
                    if len(self._protocol_cycle_times) > 10:
                        self._protocol_cycle_times.pop(0)
                    
                    # Record protocol cycle duration in metrics
                    if self.metrics_collector:
                        self.metrics_collector.record_histogram(
                            name="protocol_cycle_duration",
                            value=cycle_time
                        )
                    
                    # Calculate next protocol period
                    next_period = self._adjust_protocol_period()
                    self._current_protocol_period = next_period
                    
                    # Log the adaptive protocol period clearly for Lifeguard
                    if self.config.get("LIFEGUARD_ENABLED", False) and abs(next_period - self.config["PROTOCOL_PERIOD"]) > 0.05:
                        logger.info(f"LIFEGUARD: Adaptive protocol period: {next_period:.2f}s (base: {self.config['PROTOCOL_PERIOD']:.2f}s)")
                    
                    # Sleep until next protocol period
                    await asyncio.sleep(next_period)
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"Error in protocol loop: {e}")
                    
                    # Record error in metrics
                    if self.metrics_collector:
                        self.metrics_collector.record_event(
                            name="protocol_error",
                            value=str(e)
                        )
                    
                    # Emit error event if event dispatcher is available
                    if self.event_dispatcher:
                        # Import here to avoid circular imports
                        from swim.events.types import ProtocolErrorEvent
                        
                        event = ProtocolErrorEvent(
                            source_node=f"{self.transport.local_address[0]}:{self.transport.local_address[1]}",
                            metadata={
                                "error": str(e),
                                "cycle_number": self._protocol_cycles
                            }
                        )
                        self.event_dispatcher.emit(event)
                    
                    await asyncio.sleep(1.0)  # Avoid tight loop on errors
            
        except asyncio.CancelledError:
            logger.debug("Protocol loop cancelled")
    
    async def _check_suspects(self) -> None:
        """
        Check suspect members with indirect probing.
        
        This method is called periodically to check if suspect members
        are reachable through indirect probing.
        """
        suspect_members = self.members.get_suspect_members()
        
        if suspect_members:
            logger.info(f"Checking {len(suspect_members)} suspect members")
        
        for member in suspect_members:
            # Skip self
            if member.addr == self.transport.local_address:
                continue
            
            # Get suspect timeout from Lifeguard if available
            suspect_timeout = self.config["SUSPECT_TIMEOUT"]
            if self.timing_service and self.config.get("LIFEGUARD_ENABLED", True):
                peer_id = f"{member.addr[0]}:{member.addr[1]}"
                suspect_timeout = self.timing_service.get_suspect_timeout(peer_id)
                logger.info(f"LIFEGUARD: Using adaptive suspect timeout for {peer_id}: {suspect_timeout:.2f}s (base: {self.config['SUSPECT_TIMEOUT']:.2f}s)")
            
            # Check if suspect timeout has expired
            suspect_time = time.time() - member.last_state_change
            if suspect_time > suspect_timeout:
                logger.warning(f"Suspect timeout expired for {member.addr[0]}:{member.addr[1]}, marking as DEAD")
                
                # Record suspect timeout in metrics
                if self.metrics_collector:
                    self.metrics_collector.record_event(
                        name="suspect_timeout",
                        value=f"{member.addr[0]}:{member.addr[1]}",
                        labels={"suspect_time": f"{suspect_time:.2f}s"}
                    )
                
                # Track transitions for Lifeguard stats
                if hasattr(self, '_suspect_transitions'):
                    self._suspect_transitions += 1
                else:
                    self._suspect_transitions = 1
                    
                # Check if this might be a false positive (for stats only)
                if member.last_heartbeat > time.time() - 30:  # If heard from in last 30s
                    if hasattr(self, '_false_positives'):
                        self._false_positives += 1
                    else:
                        self._false_positives = 1
                    logger.warning(f"LIFEGUARD: Potential false positive detected for {member.addr[0]}:{member.addr[1]} (heard from {time.time() - member.last_heartbeat:.1f}s ago)")
                
                await self.members.mark_dead(member.addr)
                continue
            
            # Try indirect probing
            probe_id = str(uuid.uuid4())[:8]
            logger.info(f"[{probe_id}] Checking suspect member {member.addr[0]}:{member.addr[1]} with indirect probe "
                    f"(suspect for {suspect_time:.2f}s)")
            
            start_time = time.time()
            result = await self.failure_detector.indirect_probe(member.addr)
            probe_time = time.time() - start_time
            
            # Record indirect probe in metrics
            if self.metrics_collector:
                self.metrics_collector.record_event(
                    name="indirect_probe",
                    value="success" if result else "failure",
                    labels={
                        "target": f"{member.addr[0]}:{member.addr[1]}",
                        "probe_time": f"{probe_time:.3f}s"
                    }
                )
                    
            # Update probe result in awareness service if available
            if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True):
                peer_id = f"{member.addr[0]}:{member.addr[1]}"
                if result:
                    self.awareness_service.record_success(peer_id)
                else:
                    self.awareness_service.record_failure(peer_id)
                        
            # Update probe result in probe rate service if available
            if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True):
                peer_id = f"{member.addr[0]}:{member.addr[1]}"
                self.probe_rate_service.record_probe_result(peer_id, result)
            
            if result:
                logger.info(f"[{probe_id}] Indirect probe SUCCESSFUL for {member.addr[0]}:{member.addr[1]}")
            else:
                logger.info(f"[{probe_id}] Indirect probe FAILED for {member.addr[0]}:{member.addr[1]}")
    
    async def _probe_random_member(self) -> None:
        """
        Probe a random member to check its status.
        
        This implements the SWIM failure detection by randomly selecting
        a member to ping in each protocol period. Enhanced with resurrection
        detection for DEAD members.
        """
        # Get a random member to probe - include DEAD members occasionally for resurrection
        targets = self.members.get_random_members(1, include_dead=True)
        if not targets:
            return
        
        target = targets[0]
        
        # Enhanced resurrection-aware probing strategy
        if target.state == MemberState.DEAD:
            # Conservative resurrection probing: only probe DEAD members occasionally
            # This prevents overwhelming DEAD nodes while enabling resurrection detection
            
            # Calculate time since member was marked DEAD
            time_since_death = time.time() - target.last_state_change
            
            # Resurrection probing criteria:
            # 1. At least 30 seconds since marked DEAD (avoid immediate retries)
            # 2. Exponential backoff with some randomness to prevent coordinated probing
            # 3. Maximum interval of 5 minutes between resurrection attempts
            
            min_resurrection_interval = 30.0  # Minimum 30 seconds
            max_resurrection_interval = 300.0  # Maximum 5 minutes
            
            # Exponential backoff based on time since death, with randomness
            import random
            backoff_factor = min(time_since_death / 60.0, 5.0)  # Scale to 0-5 based on minutes
            resurrection_interval = min_resurrection_interval * (2 ** backoff_factor)
            resurrection_interval = min(resurrection_interval, max_resurrection_interval)
            
            # Add randomness (±25%) to prevent coordinated probing
            jitter = random.uniform(0.75, 1.25)
            resurrection_interval *= jitter
            
            # Calculate time since last potential resurrection probe
            # Use a simple deterministic approach based on protocol cycles
            should_probe_dead = (self._protocol_cycles % int(resurrection_interval)) == 0
            
            if not should_probe_dead:
                logger.debug(f"Skipping DEAD member {target.addr[0]}:{target.addr[1]} for resurrection probe "
                           f"(will retry in ~{resurrection_interval:.1f}s)")
                return
            
            logger.info(f"RESURRECTION_PROBE: Attempting resurrection probe for DEAD member "
                       f"{target.addr[0]}:{target.addr[1]} (dead for {time_since_death:.1f}s)")
        
        # Skip blacklisted peers if using Lifeguard probe rate service
        if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True):
            peer_id = f"{target.addr[0]}:{target.addr[1]}"
            if self.probe_rate_service.is_blacklisted(peer_id):
                logger.debug(f"Skipping blacklisted peer: {peer_id}")
                return
        
        # Ping the target
        self._ping_operations += 1
        probe_type = "RESURRECTION" if target.state == MemberState.DEAD else "NORMAL"
        logger.debug(f"Probing {probe_type.lower()} member {target.addr[0]}:{target.addr[1]} "
                    f"(ping #{self._ping_operations})")
        
        start_time = time.time()
        result = await self.failure_detector.ping(target.addr)
        ping_time = time.time() - start_time
        
        # Record ping result in metrics
        if self.metrics_collector and self.latency_tracker:
            # Record ping event
            self.metrics_collector.record_event(
                name="ping",
                value="success" if result else "failure",
                labels={
                    "target": f"{target.addr[0]}:{target.addr[1]}",
                    "probe_type": probe_type.lower()
                }
            )
            
            # Record RTT in latency tracker
            peer_id = f"{target.addr[0]}:{target.addr[1]}"
            self.latency_tracker.record_rtt(peer_id, ping_time, result)
            
            # Update awareness service if available
            if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True):
                if result:
                    self.awareness_service.record_success(peer_id)
                else:
                    self.awareness_service.record_failure(peer_id)
                    
            # Update probe rate service if available
            if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True):
                self.probe_rate_service.record_probe_result(peer_id, result)
            
            # If we have enough RTT data, use it to adjust timeout
            if self.failure_detector and hasattr(self.failure_detector, 'ping_timeout'):
                old_timeout = self.failure_detector.ping_timeout
                
                # Use Lifeguard timing service if available
                if self.timing_service and self.config.get("LIFEGUARD_ENABLED", True):
                    new_timeout = self.timing_service.get_ping_timeout(peer_id)
                else:
                    new_timeout = self.latency_tracker.get_adaptive_timeout(peer_id)
                
                # Only update if significant change
                if abs(old_timeout - new_timeout) > 0.05:
                    self.failure_detector.ping_timeout = new_timeout
                    
                    # Record timeout adjustment
                    self.metrics_collector.record_event(
                        name="timeout_adjustment",
                        value=f"{old_timeout:.3f}->{new_timeout:.3f}",
                        labels={"peer_id": peer_id}
                    )
        
        if result:
            if target.state == MemberState.DEAD:
                logger.info(f"RESURRECTION_SUCCESS: DEAD member {target.addr[0]}:{target.addr[1]} "
                           f"responded to resurrection probe!")
            logger.debug(f"Random probe SUCCESSFUL for {target.addr[0]}:{target.addr[1]}")
        else:
            if target.state == MemberState.DEAD:
                logger.debug(f"RESURRECTION_FAILED: DEAD member {target.addr[0]}:{target.addr[1]} "
                            f"did not respond to resurrection probe")
            logger.debug(f"Random probe FAILED for {target.addr[0]}:{target.addr[1]}")
    
    async def _handle_message(self, data: bytes, from_addr: Tuple[str, int]) -> None:
        """
        Handle a received message.
        
        This callback is called by the transport when a message is received.
        
        Args:
            data: The raw message data.
            from_addr: The address that sent the message.
        """
        # Record message received in bandwidth monitor
        if self.bandwidth_monitor:
            self.bandwidth_monitor.record_bandwidth(
                direction=Direction.INBOUND,
                bytes=len(data),
                peer_id=f"{from_addr[0]}:{from_addr[1]}",
                message_type="unknown"  # Will be updated after deserialization
            )
        
        try:
            msg = deserialize_message(data)
        except Exception as e:
            logger.warning(f"Error deserializing message from {from_addr[0]}:{from_addr[1]}: {e}")
            
            # Record deserialization error in metrics
            if self.metrics_collector:
                self.metrics_collector.record_event(
                    name="message_error",
                    value="deserialization_error",
                    labels={"from": f"{from_addr[0]}:{from_addr[1]}"}
                )
            
            # Emit message error event if event dispatcher is available
            if self.event_dispatcher:
                # Import here to avoid circular imports
                from swim.events.types import MessageErrorEvent
                
                event = MessageErrorEvent(
                    source_node=f"{self.transport.local_address[0]}:{self.transport.local_address[1]}",
                    metadata={
                        "error": str(e),
                        "from": f"{from_addr[0]}:{from_addr[1]}",
                        "data_size": len(data)
                    }
                )
                self.event_dispatcher.emit(event)
            
            return
        
        msg_type = msg.get("type")
        msg_id = msg.get("id", "unknown")
        
        # Update message type in bandwidth monitor
        if self.bandwidth_monitor and msg_type:
            self.bandwidth_monitor.record_bandwidth(
                direction=Direction.INBOUND,
                bytes=len(data),
                peer_id=f"{from_addr[0]}:{from_addr[1]}",
                message_type=msg_type
            )
        
        # Record message received in metrics
        if self.metrics_collector:
            self.metrics_collector.record_counter(
                name="message_received",
                value=1,
                labels={
                    "type": msg_type,
                    "from": f"{from_addr[0]}:{from_addr[1]}"
                }
            )
        
        logger.debug(f"[{msg_id}] Handling message of type {msg_type} from {from_addr[0]}:{from_addr[1]}")
        
        # Update awareness service on successful message receipt
        if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True):
            peer_id = f"{from_addr[0]}:{from_addr[1]}"
            self.awareness_service.record_success(peer_id)
        
        if msg_type == "PING":
            await self.failure_detector.handle_ping(from_addr, msg)
        elif msg_type == "PING-REQ":
            await self.failure_detector.handle_ping_req(from_addr, msg)
        elif msg_type == "HEARTBEAT":
            await self.gossip.handle_message(from_addr, data)
        elif msg_type in ["SYNC-REQ", "SYNC-RESP"]:
            if self.sync_service:
                await self.sync_service.handle_message(from_addr, data)
            else:
                await self.gossip.handle_message(from_addr, data)
        else:
            logger.debug(f"[{msg_id}] Received unknown message type: {msg_type}")
            
            # Record unknown message type in metrics
            if self.metrics_collector:
                self.metrics_collector.record_event(
                    name="unknown_message_type",
                    value=msg_type,
                    labels={"from": f"{from_addr[0]}:{from_addr[1]}"}
                )
            
            # Emit unknown message type event if event dispatcher is available
            if self.event_dispatcher:
                # Import here to avoid circular imports
                from swim.events.types import UnknownMessageTypeEvent
                
                event = UnknownMessageTypeEvent(
                    source_node=f"{self.transport.local_address[0]}:{self.transport.local_address[1]}",
                    metadata={
                        "message_type": msg_type,
                        "from": f"{from_addr[0]}:{from_addr[1]}",
                        "message_id": msg_id
                    }
                )
                self.event_dispatcher.emit(event)
    
    def get_metrics_report(self) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive metrics report.
        
        Returns:
            A dictionary containing all metrics and their statistics,
            or None if metrics are not enabled.
        """
        if not self.metrics_collector:
            return None
        
        report = {
            "timestamp": time.time(),
            "node_id": self.metrics_collector.node_id,
            "metrics": self.metrics_collector.report_metrics()
        }
        
        # Add network health if latency tracker is available
        if self.latency_tracker:
            report["network_health"] = self.latency_tracker.get_network_health()
        
        # Add bandwidth information if bandwidth monitor is available
        if self.bandwidth_monitor:
            report["bandwidth"] = {
                "current_rates": {
                    "inbound": self.bandwidth_monitor.get_current_rate(Direction.INBOUND),
                    "outbound": self.bandwidth_monitor.get_current_rate(Direction.OUTBOUND)
                },
                "recommendations": self.bandwidth_monitor.get_optimization_recommendations()
            }
        
        # Add Lifeguard information if enabled
        if self.config.get("LIFEGUARD_ENABLED", True):
            report["lifeguard"] = {}
            
            if self.awareness_service:
                report["lifeguard"]["awareness"] = self.awareness_service.get_awareness_stats()
            
            if self.timing_service:
                report["lifeguard"]["timing"] = self.timing_service.get_timing_stats()
            
            if self.probe_rate_service:
                report["lifeguard"]["probe_rate"] = self.probe_rate_service.get_probing_stats()
        
        return report
    
    def get_peer_metrics(self, peer_addr: Tuple[str, int]) -> Optional[Dict[str, Any]]:
        """
        Get metrics specific to a peer.
        
        Args:
            peer_addr: The address of the peer.
            
        Returns:
            A dictionary containing peer-specific metrics,
            or None if metrics are not enabled.
        """
        if not self.metrics_collector or not self.latency_tracker or not self.bandwidth_monitor:
            return None
        
        peer_id = f"{peer_addr[0]}:{peer_addr[1]}"
        
        result = {
            "latency": self.latency_tracker.get_rtt_stats(peer_id),
            "latency_trend": self.latency_tracker.get_peer_latency_trend(peer_id),
            "bandwidth": {
                "inbound": self.bandwidth_monitor.get_bandwidth_stats(
                    direction=Direction.INBOUND,
                    peer_id=peer_id,
                    time_window=300  # Last 5 minutes
                ),
                "outbound": self.bandwidth_monitor.get_bandwidth_stats(
                    direction=Direction.OUTBOUND,
                    peer_id=peer_id,
                    time_window=300  # Last 5 minutes
                )
            }
        }
        
        # Add adaptive timeout
        result["adaptive_timeout"] = self.latency_tracker.get_adaptive_timeout(peer_id)
        
        # Add Lifeguard information if enabled
        if self.config.get("LIFEGUARD_ENABLED", True):
            result["lifeguard"] = {}
            
            if self.awareness_service:
                result["lifeguard"]["awareness"] = self.awareness_service.get_awareness(peer_id)
            
            if self.timing_service:
                result["lifeguard"]["ping_timeout"] = self.timing_service.get_ping_timeout(peer_id)
                result["lifeguard"]["suspect_timeout"] = self.timing_service.get_suspect_timeout(peer_id)
            
            if self.probe_rate_service:
                result["lifeguard"]["probe_count"] = self.probe_rate_service.get_probe_count(peer_id)
                result["lifeguard"]["probe_interval"] = self.probe_rate_service.get_probe_interval(peer_id)
                result["lifeguard"]["probe_success_rate"] = self.probe_rate_service.get_probe_success_rate(peer_id)
        
        return result
