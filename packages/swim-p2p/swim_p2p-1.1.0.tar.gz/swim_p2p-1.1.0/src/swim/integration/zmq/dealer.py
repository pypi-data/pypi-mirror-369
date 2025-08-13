"""
Enhanced DEALER socket management with circuit breaker integration and reliability.
Integrates circuit breaker pattern with SWIM membership events for robust connection management.
"""

import asyncio
import logging
import time
import json
import uuid
import zmq
import zmq.asyncio
from typing import Dict, Optional, Callable, Any, Set
from dataclasses import dataclass
from enum import Enum, auto
from collections import defaultdict

# Import circuit breaker components
from swim.integration.messaging.circuit_breaker import ( 
    CircuitBreakerManager, 
    CircuitBreakerOpenError, 
    CircuitConfig,
    CircuitState 
)

logger = logging.getLogger(__name__)


class ConnectionState(Enum): 
    """Connection states for lifecycle management."""
    CONNECTING = auto()
    ACTIVE = auto()      
    DEGRADED = auto()    
    CLOSING = auto()
    CLOSED = auto()
    FAILED = auto()      


class PortConflictError(Exception):
    """Raised when port conflicts occur during connection establishment."""
    pass


class ConnectionTimeoutError(Exception):
    """Raised when connection establishment times out."""
    pass


@dataclass
class Connection:
    """Enhanced connection information and state with circuit breaker integration."""
    socket: zmq.asyncio.Socket
    state: ConnectionState 
    node_id: str 
    established_at: float
    last_used: float
    failure_count: int = 0 
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy for message sending from DEALER's perspective."""
        return self.state == ConnectionState.ACTIVE
    
    def time_since_use(self) -> float:
        """Get time since last use in seconds."""
        return time.time() - self.last_used


class EnhancedDealerManager:
    """
    Enhanced DEALER manager with circuit breaker integration and reliability.
    
    Provides fail-fast behavior through circuit breakers while maintaining
    connection lifecycle management and SWIM integration.
    """

    def __init__(self, node_id: str, context: Optional[zmq.asyncio.Context] = None):
        """
        Initialize enhanced DEALER manager with circuit breaker support.
        
        Args:
            node_id: This node's identifier (SWIM address format "host:port")
            context: Optional ZMQ context, creates new one if None
        """
        self.node_id = node_id 
        self.context = context or zmq.asyncio.Context.instance() 
        self.connections: Dict[str, Connection] = {} 
        self._lock = asyncio.Lock()

        self._max_connections = 50
        self._connection_timeout = 5.0 
        self._degraded_timeout = 2.0  
        self._idle_timeout = 300.0
        self._max_failure_count = 3
        
        self.circuit_breaker_manager = CircuitBreakerManager(
            node_id=self.node_id, 
            config=CircuitConfig(failure_threshold=3, recovery_timeout=30.0, success_threshold=2, probe_interval=10.0, max_probe_attempts=3)
        )
        
        # Add logging callback for circuit breaker state changes
        def cb_state_change_callback(target_node: str, old_state, new_state):
            logger.info(f"DEALER ({self.node_id}): Circuit breaker for {target_node}: {old_state.name} → {new_state.name}")
        
        # Set the callback after creating the manager
        self.circuit_breaker_manager._state_change_callback = cb_state_change_callback
        
        self.circuit_breaker_manager.set_probe_callback(self._circuit_breaker_probe)
        
        self.on_connection_established: Optional[Callable[[str], None]] = None 
        self.on_connection_failed: Optional[Callable[[str, Exception], None]] = None 
        self.on_connection_degraded: Optional[Callable[[str], None]] = None 
        self.on_connection_restored: Optional[Callable[[str], None]] = None 
        
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
        
        self._stats = defaultdict(int) 

        self.router_manager_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
        logger.info(f"DEALER ({self.node_id}): Initialized with circuit breaker protection")

    async def start(self):
        if self._running:
            logger.warning(f"DEALER ({self.node_id}): Already running.")
            return
        self._running = True
        await self.circuit_breaker_manager.start()
        self._cleanup_task = asyncio.create_task(self._cleanup_connections())
        self._receive_task = asyncio.create_task(self._receive_loop())
        logger.info(f"DEALER ({self.node_id}): Started with circuit breaker protection")

    async def _receive_loop(self):
        """Receive loop for processing incoming messages on DEALER sockets."""
        logger.info(f"DEALER ({self.node_id}): Starting receive loop for ACK processing")
        
        while self._running:
            try:
                # Check all active DEALER connections for incoming messages
                for zmq_node_id, conn in list(self.connections.items()):
                    if conn.state == ConnectionState.ACTIVE and conn.socket:
                        try:
                            # Non-blocking receive check
                            parts = await conn.socket.recv_multipart(zmq.NOBLOCK)
                            logger.info(f"DEALER ({self.node_id}): Received message from {zmq_node_id}: {len(parts)} parts")
                            
                            # Process the received message (ACKs, responses, etc.)
                            await self._process_incoming_message(zmq_node_id, parts)
                            
                        except zmq.Again:
                            # No message available, continue to next socket
                            continue
                        except Exception as e:
                            logger.error(f"DEALER ({self.node_id}): Error receiving from {zmq_node_id}: {e}")
                            conn.failure_count += 1
                            
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"DEALER ({self.node_id}): Critical error in receive loop: {e}")
                await asyncio.sleep(1.0)  # Longer delay on critical errors

    async def _process_incoming_message(self, zmq_node_id: str, parts: list[bytes]):
        """Process incoming message from DEALER socket."""
        try:
            if len(parts) < 2:
                logger.warning(f"DEALER ({self.node_id}): Malformed message from {zmq_node_id}: {len(parts)} parts")
                return
                
            # DEALER receives: [empty_frame, message_data]
            empty_frame, message_data = parts[0], parts[1]
            
            if empty_frame != b'':
                logger.warning(f"DEALER ({self.node_id}): Non-empty delimiter from {zmq_node_id}")
                
            logger.info(f"DEALER ({self.node_id}): Processing {len(message_data)} bytes from {zmq_node_id}")
            
            # Parse message and route to appropriate handler
            try:
                import json
                message = json.loads(message_data.decode('utf-8'))
                message_type = message.get('type', 'unknown')
                
                logger.info(f"DEALER ({self.node_id}): Received {message_type} from {zmq_node_id}")
                
                # Route to router manager for ACK processing
                if self.router_manager_callback:
                    await self.router_manager_callback(zmq_node_id, message)
                else:
                    logger.warning(f"DEALER ({self.node_id}): No router manager callback for {message_type}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"DEALER ({self.node_id}): JSON decode error from {zmq_node_id}: {e}")
            except Exception as e:
                logger.error(f"DEALER ({self.node_id}): Message processing error from {zmq_node_id}: {e}")
                
        except Exception as e:
            logger.error(f"DEALER ({self.node_id}): Critical error processing message from {zmq_node_id}: {e}")

    def set_router_manager_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Set callback to router manager for incoming message processing."""
        self.router_manager_callback = callback
        logger.info(f"DEALER ({self.node_id}): Router manager callback configured")
    
    async def handle_swim_member_alive(self, node_address: str):
        """
        Handle SWIM member alive event - reset circuit breaker for resurrected node.
        This integrates with the SWIM-ZMQ bridge resurrection handling.
        
        Args:
            node_address: SWIM address of the resurrected node (e.g., "127.0.0.1:8001")
        """
        # Convert SWIM address to ZMQ address (add port offset, typically +1000)
        try:
            host, port_str = node_address.split(':')
            swim_port = int(port_str)
            zmq_port = swim_port + 1000  # Standard offset
            zmq_address = f"{host}:{zmq_port}"
            
            await self.circuit_breaker_manager.handle_swim_member_alive(zmq_address)
            logger.info(f"DEALER ({self.node_id}): Handled SWIM resurrection for {node_address} → ZMQ {zmq_address}")
            
        except Exception as e:
            logger.error(f"DEALER ({self.node_id}): Error handling SWIM resurrection for {node_address}: {e}")

    async def stop(self):
        if not self._running:
            logger.warning(f"DEALER ({self.node_id}): Already stopped.")
            return
        logger.info(f"DEALER ({self.node_id}): Stopping...")
        self._running = False
        
        # Stop receive loop
        if hasattr(self, '_receive_task') and self._receive_task:
            self._receive_task.cancel()
            try: 
                await self._receive_task
            except asyncio.CancelledError: 
                pass
        
        await self.circuit_breaker_manager.stop()
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try: await self._cleanup_task
            except asyncio.CancelledError: pass
        await self._close_all_connections()
        logger.info(f"DEALER ({self.node_id}): Stopped.")

    def _validate_node_address(self, zmq_node_id: str) -> None: 
        if ':' not in zmq_node_id: raise ValueError(f"Invalid ZMQ address format: {zmq_node_id}")
        try:
            host, port_str = zmq_node_id.split(':', 1)
            port = int(port_str)
            if not host or port < 1 or port > 65535: raise ValueError("Invalid host or port")
        except ValueError as e: raise ValueError(f"Invalid ZMQ address {zmq_node_id}: {e}")

    async def get_connection(self, zmq_node_id: str) -> Optional[zmq.asyncio.Socket]: 
        try: self._validate_node_address(zmq_node_id)
        except ValueError as e:
            logger.error(f"DEALER ({self.node_id}): Invalid target ZMQ address {zmq_node_id}: {e}")
            return None
        
        cb = await self.circuit_breaker_manager.get_or_create_circuit_breaker(zmq_node_id)
        if cb.state == CircuitState.OPEN:
            logger.debug(f"DEALER ({self.node_id}): Circuit breaker OPEN for ZMQ {zmq_node_id}, blocking connection attempt.")
            self._stats["messages_blocked_by_circuit"] += 1
            return None 
        
        async with self._lock:
            if zmq_node_id in self.connections:
                conn = self.connections[zmq_node_id]
                if conn.state == ConnectionState.ACTIVE:
                    conn.last_used = time.time()
                    logger.debug(f"DEALER ({self.node_id}): Using existing ACTIVE connection to ZMQ {zmq_node_id}")
                    return conn.socket
                elif conn.state in [ConnectionState.CONNECTING, ConnectionState.DEGRADED]:
                    logger.debug(f"DEALER ({self.node_id}): Connection to ZMQ {zmq_node_id} in state {conn.state.name}. Allowing send attempt.")
                    return conn.socket 
                else: 
                    logger.info(f"DEALER ({self.node_id}): Connection to ZMQ {zmq_node_id} is {conn.state.name}. Attempting to recreate.")
                    await self._cleanup_connection_nolock(zmq_node_id) 
            
            return await self._create_connection_with_circuit_breaker(zmq_node_id)
    
    async def _create_connection_with_circuit_breaker(self, zmq_node_id: str) -> Optional[zmq.asyncio.Socket]: 
        try:
            socket = await self.circuit_breaker_manager.execute_with_circuit_breaker(
                target_node=zmq_node_id, 
                operation=self._create_connection_internal,
                zmq_target_node_id=zmq_node_id 
            )
            if socket:
                self._stats["total_connections_created"] += 1
            return socket
        except CircuitBreakerOpenError:
            logger.warning(f"DEALER ({self.node_id}): Circuit breaker blocked connection attempt to ZMQ {zmq_node_id}")
            self._stats["messages_blocked_by_circuit"] += 1
            if zmq_node_id in self.connections: self.connections[zmq_node_id].state = ConnectionState.FAILED 
            return None
        except Exception as e: 
            logger.error(f"DEALER ({self.node_id}): Failed to create connection to ZMQ {zmq_node_id} via CB: {e}")
            if zmq_node_id in self.connections: self.connections[zmq_node_id].state = ConnectionState.FAILED
            if self.on_connection_failed: self.on_connection_failed(zmq_node_id, e)
            return None

    async def _create_connection_internal(self, zmq_target_node_id: str) -> Optional[zmq.asyncio.Socket]: 
        socket = None
        try:
            if len(self.connections) >= self._max_connections:
                await self._evict_idle_connection_nolock()

            socket = self.context.socket(zmq.DEALER)
            identity = f"dealer-{self.node_id}-to-{zmq_target_node_id}-{uuid.uuid4().hex[:8]}".encode()
            socket.setsockopt(zmq.IDENTITY, identity)
            socket.setsockopt(zmq.LINGER, 0) 
            socket.setsockopt(zmq.SNDTIMEO, int(self._connection_timeout * 1000)) 
            
            endpoint = f"tcp://{zmq_target_node_id}"
            logger.info(f"DEALER ({self.node_id}): Attempting ZMQ connect to {endpoint} with identity {identity.decode()}")
            socket.connect(endpoint)

            current_time = time.time()
            connection = Connection(
                socket=socket, state=ConnectionState.ACTIVE, 
                node_id=zmq_target_node_id, established_at=current_time, last_used=current_time
            )
            self.connections[zmq_target_node_id] = connection
            logger.info(f"DEALER ({self.node_id}): ZMQ DEALER socket created and connect initiated to {zmq_target_node_id}. State: ACTIVE.")
            if self.on_connection_established: self.on_connection_established(zmq_target_node_id)
            return socket
            
        except zmq.ZMQError as e:
            logger.error(f"DEALER ({self.node_id}): ZMQError during ZMQ connect to {zmq_target_node_id}: {e}")
            if socket: socket.close()
            if zmq_target_node_id in self.connections: self.connections[zmq_target_node_id].state = ConnectionState.FAILED
            raise 
        except Exception as e:
            logger.error(f"DEALER ({self.node_id}): Unexpected error during ZMQ connect to {zmq_target_node_id}: {e}", exc_info=True)
            if socket: socket.close()
            if zmq_target_node_id in self.connections: self.connections[zmq_target_node_id].state = ConnectionState.FAILED
            raise 

    async def send_message(self, zmq_node_id: str, message: bytes) -> bool: 
        if not message: return False
        
        logger.info(f"DEALER ({self.node_id}): Attempting to send {len(message)} bytes to {zmq_node_id}")
        
        socket = await self.get_connection(zmq_node_id) 
        if not socket:
            logger.error(f"DEALER ({self.node_id}): No ZMQ connection available or circuit open for {zmq_node_id}")
            cb = await self.circuit_breaker_manager.get_or_create_circuit_breaker(zmq_node_id) 
            logger.error(f"DEALER ({self.node_id}): Circuit breaker state for {zmq_node_id}: {cb.state.name}")
            # Only record failure if the circuit wasn't already open, to avoid double counting
            # by get_connection and then here. get_connection logs if CB is open.
            if cb.state != CircuitState.OPEN:
                 await cb._record_failure()
            return False

        try:
            await self.circuit_breaker_manager.execute_with_circuit_breaker(
                target_node=zmq_node_id,
                operation=self._send_message_internal, 
                socket=socket, 
                message=message,
                zmq_target_node_id=zmq_node_id 
            )
            logger.info(f"DEALER ({self.node_id}): ✅ Successfully sent {len(message)} bytes to {zmq_node_id}")
            return True
        except CircuitBreakerOpenError:
            logger.warning(f"DEALER ({self.node_id}): ❌ Circuit breaker blocked message to ZMQ {zmq_node_id} during send.")
            self._stats["messages_blocked_by_circuit"] += 1
            return False
        except Exception as e: 
            logger.error(f"DEALER ({self.node_id}): ❌ Send failed to ZMQ {zmq_node_id}: {e}")
            if zmq_node_id in self.connections:
                 self.connections[zmq_node_id].failure_count += 1
                 if self.connections[zmq_node_id].failure_count >= self._max_failure_count:
                     self.connections[zmq_node_id].state = ConnectionState.FAILED
                 else:
                     self.connections[zmq_node_id].state = ConnectionState.DEGRADED
            return False

    async def _send_message_internal(self, socket: zmq.asyncio.Socket, message: bytes, zmq_target_node_id: str): 
        try:
            # DEALER to ROUTER communication requires an empty delimiter frame
            # The ZMQ DEALER socket automatically adds its own identity as the first frame when sending.
            # Then we add an empty frame (delimiter for ROUTER).
            # Then the actual message payload.
            # So, ROUTER receives: [dealer_identity, empty_frame, message_payload]
            await socket.send_multipart([b'', message], flags=zmq.NOBLOCK) 

            if zmq_target_node_id in self.connections:
                self.connections[zmq_target_node_id].last_used = time.time()
                self.connections[zmq_target_node_id].failure_count = 0 
                if self.connections[zmq_target_node_id].state != ConnectionState.ACTIVE:
                    self.connections[zmq_target_node_id].state = ConnectionState.ACTIVE
                    if self.on_connection_restored: self.on_connection_restored(zmq_target_node_id)

            logger.debug(f"DEALER ({self.node_id}): Sent multipart (empty + {len(message)} bytes payload) to ZMQ {zmq_target_node_id}")
        except zmq.Again: 
            logger.warning(f"DEALER ({self.node_id}): Send buffer full for ZMQ {zmq_target_node_id}. Marking as DEGRADED.")
            if zmq_target_node_id in self.connections:
                 self.connections[zmq_target_node_id].state = ConnectionState.DEGRADED
                 if self.on_connection_degraded: self.on_connection_degraded(zmq_target_node_id)
            raise 
        except Exception as e:
            logger.error(f"DEALER ({self.node_id}): Send error to ZMQ {zmq_target_node_id}: {e}")
            if zmq_target_node_id in self.connections:
                 self.connections[zmq_target_node_id].state = ConnectionState.FAILED
            raise 

    async def _circuit_breaker_probe(self, zmq_target_node_id: str) -> bool: 
        self._stats["probe_messages_sent"] += 1
        socket = None
        try:
            # Probe message now includes its own unique ID for ACK correlation
            probe_id = str(uuid.uuid4())
            probe_data = json.dumps({
                "type": "CIRCUIT_BREAKER_PROBE", 
                "id": probe_id, 
                "source_swim_id": self.node_id, # Sending node's SWIM ID
                "target_zmq_id": zmq_target_node_id, # Target ZMQ ID
                "timestamp": time.time()
            }).encode('utf-8')

            socket = self.context.socket(zmq.DEALER)
            identity = f"probe-{self.node_id}-to-{zmq_target_node_id}-{probe_id[:8]}".encode() # Include probe ID in identity
            socket.setsockopt(zmq.IDENTITY, identity)
            socket.setsockopt(zmq.LINGER, 0)
            socket.setsockopt(zmq.SNDTIMEO, 1000) 
            
            endpoint = f"tcp://{zmq_target_node_id}"
            socket.connect(endpoint)
            
            # Send as multipart: [empty_delimiter, probe_payload]
            await socket.send_multipart([b'', probe_data], flags=zmq.NOBLOCK)
            
            # For a probe to be truly successful, we need a response (e.g., a PROBE_ACK).
            # This simplified version just checks if the send itself worked.
            # A more robust probe would involve ZMQ_RCVTIMEO on the probe socket
            # and waiting for a specific PROBE_ACK message.
            # The target RouterManager needs a handler for CIRCUIT_BREAKER_PROBE to send this ACK.
            logger.info(f"DEALER ({self.node_id}): Circuit breaker probe (ID: {probe_id}) to ZMQ {zmq_target_node_id} sent.")
            
            # Simulate waiting for an ACK by checking if the circuit breaker state changes to CLOSED
            # This is a bit indirect; direct ACK is better.
            # For now, we assume if the send didn't throw an error, it's a positive sign.
            # The actual success will be determined by the CircuitBreaker if it receives positive feedback
            # (e.g., via a _handle_circuit_probe_ack method called by the main message loop).
            return True # Optimistically true, real success depends on ACK or subsequent successful sends.
        except Exception as e:
            logger.warning(f"DEALER ({self.node_id}): Circuit breaker probe to ZMQ {zmq_target_node_id} failed during send: {e}")
            return False
        finally:
            if socket: socket.close()

    async def mark_failed(self, zmq_node_id: str): 
        async with self._lock:
            if zmq_node_id in self.connections:
                conn = self.connections[zmq_node_id]
                conn.state = ConnectionState.FAILED 
                conn.failure_count = self._max_failure_count 
                logger.warning(f"DEALER ({self.node_id}): Connection to ZMQ {zmq_node_id} marked FAILED externally.")
                cb = await self.circuit_breaker_manager.get_or_create_circuit_breaker(zmq_node_id)
                for _ in range(self.circuit_breaker_manager.config.failure_threshold):
                    await cb._record_failure() # This internally checks if it should open.

    async def _evict_idle_connection_nolock(self):
        if not self.connections: return
        oldest_node = min(self.connections.keys(), key=lambda nid: self.connections[nid].last_used)
        await self._cleanup_connection_nolock(oldest_node)
        logger.info(f"DEALER ({self.node_id}): Evicted idle ZMQ connection to {oldest_node}")

    async def _cleanup_connection_nolock(self, zmq_node_id: str): 
        if zmq_node_id in self.connections:
            conn = self.connections.pop(zmq_node_id)
            try: conn.socket.close()
            except Exception as e: logger.warning(f"DEALER ({self.node_id}): Error closing ZMQ socket for {zmq_node_id}: {e}")
            logger.debug(f"DEALER ({self.node_id}): Cleaned up ZMQ connection to {zmq_node_id}")

    async def _close_all_connections(self):
        async with self._lock:
            node_ids = list(self.connections.keys())
            for zmq_node_id in node_ids: await self._cleanup_connection_nolock(zmq_node_id)
            logger.info(f"DEALER ({self.node_id}): Closed {len(node_ids)} ZMQ connections")

    async def _cleanup_connections(self):
        logger.info(f"DEALER ({self.node_id}): Started ZMQ connection cleanup task")
        while self._running:
            try:
                await asyncio.sleep(60) 
                to_close = []
                async with self._lock: 
                    for zmq_node_id, conn in list(self.connections.items()): 
                        if conn.state in [ConnectionState.CLOSED, ConnectionState.FAILED] or \
                           conn.time_since_use() > self._idle_timeout:
                            to_close.append(zmq_node_id)
                
                for zmq_node_id in to_close:
                    async with self._lock: 
                         await self._cleanup_connection_nolock(zmq_node_id)
                    logger.info(f"DEALER ({self.node_id}): Cleaned up idle/failed ZMQ connection to {zmq_node_id}")
            except asyncio.CancelledError: break
            except Exception as e: logger.error(f"DEALER ({self.node_id}): Error in ZMQ cleanup loop: {e}", exc_info=True)
        logger.info(f"DEALER ({self.node_id}): Stopped ZMQ connection cleanup task")

    def get_connection_stats(self) -> Dict[str, Any]:
        state_counts = defaultdict(int)
        for conn in self.connections.values(): state_counts[conn.state.name] += 1
        
        cb_summary = self.circuit_breaker_manager.get_all_circuit_status()
        num_open_circuits = cb_summary.get("statistics", {}).get("open_circuits", 0)

        return {
            "dealer_node_id": self.node_id,
            "total_managed_zmq_connections": len(self.connections),
            "zmq_connection_states": dict(state_counts),
            "open_circuits_managed_by_dealer_cb": num_open_circuits,
            "dealer_internal_stats": dict(self._stats)
        }