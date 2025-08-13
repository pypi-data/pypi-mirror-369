"""
SWIM-ZMQ connection manager that bridges membership state with ZMQ connections.

Manages connection lifecycle based on SWIM membership events and provides
connection health monitoring with automatic recovery. Enhanced with production-ready
port mapping and address conversion capabilities.
"""

import asyncio
import time
import logging
from typing import Dict, Set, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto

# Import network utilities for port management
from swim.utils.network import PortManager, PortConfig # Assuming this exists in your project

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection states based on SWIM membership."""
    CONNECTING = auto()    # Initial connection establishment
    CONNECTED = auto()     # TCP connected, ZMQ handshake potentially in progress
    ACTIVE = auto()       # Node is ALIVE, connection healthy and ready for ZMQ messages
    DEGRADED = auto()     # Node is SUSPECT, connection degraded
    CLOSING = auto()      # Node is DEAD, connection being closed
    FAILED = auto()       # Connection failed, needs recovery


class AddressConversionError(Exception):
    """Raised when address conversion between SWIM and ZMQ fails."""
    pass


class PortMappingError(Exception):
    """Raised when port mapping operations fail."""
    pass


@dataclass
class ConnectionInfo:
    """Track connection state and health metrics."""
    node_id: str # ZMQ address string "host:port"
    state: ConnectionState
    established_at: float
    last_used: float
    failure_count: int = 0
    swim_state: str = "UNKNOWN"
    swim_address: Optional[Tuple[str, int]] = None # Original SWIM address
    zmq_address: Optional[str] = None # Same as node_id for consistency
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy for message sending."""
        return self.state in [ConnectionState.ACTIVE] # Only ACTIVE is truly healthy for ZMQ
    
    def time_since_use(self) -> float:
        """Get time since last use in seconds."""
        return time.time() - self.last_used


@dataclass
class PortMapping:
    """Represents a SWIM to ZMQ port mapping."""
    swim_port: int
    zmq_port: int
    host: str
    registered_at: float
    node_id: str # SWIM node_id "host:swim_port"
    
    @property
    def swim_address(self) -> Tuple[str, int]:
        """Get SWIM address tuple."""
        return (self.host, self.swim_port)
    
    @property
    def zmq_address_str(self) -> str: # Renamed to avoid conflict
        """Get ZMQ address string."""
        return f"{self.host}:{self.zmq_port}"


class ConnectionManager:
    """
    Manages ZMQ connections based on SWIM membership state with port mapping.
    
    Bridges SWIM protocol events with ZMQ connection lifecycle,
    providing automatic connection management, health monitoring,
    and seamless address conversion between SWIM and ZMQ layers.
    """
    
    def __init__(self, node_id: str, port_manager: Optional[PortManager] = None):
        """
        Initialize the connection manager with port mapping capabilities.
        
        Args:
            node_id: This node's identifier (SWIM address format "host:port")
            port_manager: Optional port manager for production deployments
        """
        self.node_id = node_id # This node's SWIM address
        self.port_manager = port_manager
        
        self._connections: Dict[str, ConnectionInfo] = {} # Keyed by ZMQ address string
        self._swim_members: Dict[str, str] = {}  # Keyed by SWIM address string -> SWIM state
        self._lock = asyncio.Lock()
        
        self._port_mappings_by_swim_addr: Dict[str, PortMapping] = {} # SWIM "host:swim_port" -> PortMapping
        self._port_mappings_by_zmq_addr: Dict[str, PortMapping] = {} # ZMQ "host:zmq_port" -> PortMapping
        
        self._dealer_connect_callback: Optional[Callable[[str], Any]] = None # Expects ZMQ address
        self._dealer_disconnect_callback: Optional[Callable[[str], Any]] = None # Expects ZMQ address
        self._message_redistribute_callback: Optional[Callable] = None # Expects ZMQ address
        
        self.connection_timeout = 5.0
        self.health_check_interval = 30.0
        self.idle_timeout = 300.0  
        self.max_failure_count = 3
        self.default_port_offset = 1000  
        
        self._running = False
        self._health_check_task: Optional[asyncio.Task] = None
        
        logger.info(f"CONNECTION_MANAGER ({self.node_id}): Initialized")
    
    def register_port_mapping(self, swim_port: int, zmq_port: int, host: str = "127.0.0.1", 
                             node_id: Optional[str] = None) -> None: # node_id is SWIM ID
        """
        Register a SWIM to ZMQ port mapping.
        
        Args:
            swim_port: SWIM protocol port
            zmq_port: ZMQ messaging port
            host: Host address (default: 127.0.0.1)
            node_id: Optional node identifier for this mapping (SWIM address string)
            
        Raises:
            PortMappingError: If mapping conflicts with existing mappings
        """
        if swim_port < 1 or swim_port > 65535: raise PortMappingError(f"Invalid SWIM port: {swim_port}")
        if zmq_port < 1 or zmq_port > 65535: raise PortMappingError(f"Invalid ZMQ port: {zmq_port}")
        
        swim_addr_str = f"{host}:{swim_port}"
        zmq_addr_str = f"{host}:{zmq_port}"
        key_node_id = node_id or swim_addr_str # Key for the mapping, usually the SWIM address string

        if swim_addr_str in self._port_mappings_by_swim_addr:
            existing = self._port_mappings_by_swim_addr[swim_addr_str]
            if existing.zmq_port != zmq_port or existing.host != host:
                raise PortMappingError(f"SWIM address {swim_addr_str} already mapped to ZMQ {existing.host}:{existing.zmq_port}")
        
        if zmq_addr_str in self._port_mappings_by_zmq_addr:
            existing_swim_mapping = self._port_mappings_by_zmq_addr[zmq_addr_str]
            if existing_swim_mapping.swim_address != (host, swim_port):
                raise PortMappingError(f"ZMQ address {zmq_addr_str} already mapped to SWIM {existing_swim_mapping.swim_address[0]}:{existing_swim_mapping.swim_address[1]}")
        
        mapping = PortMapping(
            swim_port=swim_port, zmq_port=zmq_port, host=host,
            registered_at=time.time(), node_id=key_node_id
        )
        
        self._port_mappings_by_swim_addr[swim_addr_str] = mapping
        self._port_mappings_by_zmq_addr[zmq_addr_str] = mapping
        
        logger.info(f"PORT_MAPPING ({self.node_id}): Registered SWIM {swim_addr_str} -> ZMQ {zmq_addr_str} for node {key_node_id}")
    
    def register_port_mappings_bulk(self, mappings: Dict[int, int], host: str = "127.0.0.1") -> None:
        for swim_port, zmq_port in mappings.items():
            try: self.register_port_mapping(swim_port, zmq_port, host)
            except PortMappingError as e: logger.warning(f"PORT_MAPPING ({self.node_id}): Failed to register {swim_port}->{zmq_port}: {e}")
        logger.info(f"PORT_MAPPING ({self.node_id}): Bulk registered {len(mappings)} port mappings")
    
    def get_zmq_address_for_swim(self, swim_addr_str: str) -> Optional[str]:
        """
        Convert SWIM address string to ZMQ address string using registered mappings.
        
        Args:
            swim_addr_str: SWIM address string "host:port"
            
        Returns:
            ZMQ address string "host:port" or None if mapping not found or fallback fails.
        """
        mapping = self._port_mappings_by_swim_addr.get(swim_addr_str)
        if mapping: return mapping.zmq_address_str
        
        try:
            host, port_str = swim_addr_str.split(':')
            swim_port = int(port_str)
            zmq_port = swim_port + self.default_port_offset
            fallback_addr = f"{host}:{zmq_port}"
            logger.debug(f"PORT_MAPPING ({self.node_id}): No explicit mapping for SWIM {swim_addr_str}, using fallback ZMQ {fallback_addr}")
            return fallback_addr
        except ValueError:
            logger.error(f"PORT_MAPPING ({self.node_id}): Invalid SWIM address format for fallback: {swim_addr_str}")
            return None

    def get_swim_address_for_zmq(self, zmq_addr_str: str) -> Optional[str]:
        """
        Convert ZMQ address string to SWIM address string using registered mappings.
        
        Args:
            zmq_addr_str: ZMQ address string "host:port"
            
        Returns:
            SWIM address string "host:port" or None if mapping not found or fallback fails.
        """
        mapping = self._port_mappings_by_zmq_addr.get(zmq_addr_str)
        if mapping: return mapping.node_id # node_id in PortMapping is the SWIM address string
        
        try:
            host, port_str = zmq_addr_str.split(':')
            zmq_port = int(port_str)
            swim_port = zmq_port - self.default_port_offset
            if swim_port > 0:
                fallback_addr_str = f"{host}:{swim_port}"
                logger.debug(f"PORT_MAPPING ({self.node_id}): No explicit mapping for ZMQ {zmq_addr_str}, using fallback SWIM {fallback_addr_str}")
                return fallback_addr_str
        except ValueError:
            logger.error(f"PORT_MAPPING ({self.node_id}): Invalid ZMQ address format for fallback: {zmq_addr_str}")
        return None

    async def _verify_connection_ready(self, zmq_node_id: str) -> bool: # zmq_node_id is ZMQ "host:port"
        """
        Verify that a connection is actually ready for messaging.
        This now relies more on the DealerManager's own checks.
        Args:
            zmq_node_id: ZMQ Node to verify connection for ("host:port")
        Returns:
            True if connection is ready, False otherwise
        """
        if not self._dealer_connect_callback: # This is actually dealer_manager.get_connection
            logger.warning(f"CONNECTION_VERIFICATION ({self.node_id}): No dealer callback to get socket for verification of {zmq_node_id}")
            return False
            
        try:
            # Ask DealerManager if it considers its connection to zmq_node_id ready
            # This requires DealerManager to have a method for this.
            # Let's assume DealerManager.get_connection() returning a socket implies some readiness.
            # A more explicit check might be needed in DealerManager.
            # For now, we'll assume if we get a socket back from dealer, it's "verifiable"
            # The actual send attempts will confirm.
            socket = await self._dealer_connect_callback(zmq_node_id) # Attempt to get/create connection
            if socket:
                # More robust check: see if dealer manager's own internal connection state is healthy
                if hasattr(self._dealer_connect_callback, '__self__'): # Access the DealerManager instance
                    dealer_manager = self._dealer_connect_callback.__self__
                    if hasattr(dealer_manager, 'is_connection_healthy_for_dealer'): # A hypothetical method
                        is_ready = dealer_manager.is_connection_healthy_for_dealer(zmq_node_id)
                        logger.info(f"CONNECTION_VERIFICATION ({self.node_id}): Dealer reports {zmq_node_id} readiness: {is_ready}")
                        return is_ready
                
                # Fallback: if we got a socket, assume it's at least trying to be ready
                logger.info(f"CONNECTION_VERIFICATION ({self.node_id}): Connection to {zmq_node_id} seems ready (socket obtained).")
                return True
            else:
                logger.warning(f"CONNECTION_VERIFICATION ({self.node_id}): Could not obtain socket for {zmq_node_id} from dealer.")
                return False
                
        except Exception as e:
            logger.error(f"CONNECTION_VERIFICATION ({self.node_id}): Error verifying {zmq_node_id}: {e}", exc_info=True)
            return False

    async def start(self):
        if self._running: return
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info(f"CONNECTION_MANAGER ({self.node_id}): Started background health monitoring")
    
    async def stop(self):
        if not self._running: return
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try: await self._health_check_task
            except asyncio.CancelledError: pass
        await self._close_all_connections()
        logger.info(f"CONNECTION_MANAGER ({self.node_id}): Stopped and closed all connections")
    
    def set_dealer_callbacks(self, connect_callback: Callable[[str], Any], 
                            disconnect_callback: Callable[[str], Any]):
        self._dealer_connect_callback = connect_callback # Expects ZMQ address
        self._dealer_disconnect_callback = disconnect_callback # Expects ZMQ address
        logger.info(f"CONNECTION_POOL ({self.node_id}): ZMQ DEALER callbacks configured")
    
    def set_message_redistribute_callback(self, callback: Callable[[str], Any]): # Expects ZMQ address
        self._message_redistribute_callback = callback
        logger.info(f"CONNECTION_POOL ({self.node_id}): Message redistribution callback configured")
    
    async def handle_swim_membership_change(self, swim_node_id_str: str, new_swim_state: str):
        """
        Handle SWIM membership state changes.
        Args:
            swim_node_id_str: SWIM Node that changed state ("host:port")
            new_swim_state: New SWIM state (ALIVE, SUSPECT, DEAD)
        """
        if swim_node_id_str == self.node_id: return # Don't manage connection to self

        # Get ZMQ address for this SWIM node
        target_zmq_address = self.get_zmq_address_for_swim(swim_node_id_str)
        if not target_zmq_address:
            logger.error(f"SWIM_INTEGRATION ({self.node_id}): No ZMQ mapping for SWIM node {swim_node_id_str}. Cannot manage connection.")
            return

        async with self._lock:
            old_swim_state = self._swim_members.get(swim_node_id_str, "UNKNOWN")
            self._swim_members[swim_node_id_str] = new_swim_state
            
            logger.info(f"SWIM_INTEGRATION ({self.node_id}): SWIM Node {swim_node_id_str} (ZMQ: {target_zmq_address}) state change: {old_swim_state} -> {new_swim_state}")
            
            conn_info = self._connections.get(target_zmq_address)

            if new_swim_state == "ALIVE":
                if conn_info and conn_info.state == ConnectionState.FAILED:
                    logger.info(f"SWIM_INTEGRATION ({self.node_id}): Node {swim_node_id_str} (ZMQ: {target_zmq_address}) recovered to ALIVE, was FAILED. Re-establishing.")
                    await self._establish_connection(target_zmq_address, swim_addr_tuple=self._parse_swim_addr_str(swim_node_id_str))
                elif not conn_info or conn_info.state == ConnectionState.CLOSING: # New or was closing
                    logger.info(f"SWIM_INTEGRATION ({self.node_id}): Node {swim_node_id_str} (ZMQ: {target_zmq_address}) is ALIVE. Establishing/Re-establishing connection.")
                    await self._establish_connection(target_zmq_address, swim_addr_tuple=self._parse_swim_addr_str(swim_node_id_str))
                elif conn_info: # Already exists, update its SWIM state
                    conn_info.swim_state = "ALIVE"
                    if conn_info.state == ConnectionState.DEGRADED: # Was suspect, now alive
                        conn_info.state = ConnectionState.ACTIVE
                        conn_info.failure_count = 0
                        logger.info(f"CONNECTION_RECOVERY ({self.node_id}): Restored connection to ZMQ {target_zmq_address} from DEGRADED.")
            elif new_swim_state == "SUSPECT":
                if conn_info and conn_info.state == ConnectionState.ACTIVE:
                    conn_info.state = ConnectionState.DEGRADED
                    conn_info.swim_state = "SUSPECT"
                    logger.warning(f"CONNECTION_DEGRADATION ({self.node_id}): Degraded connection to ZMQ {target_zmq_address} due to SUSPECT state.")
            elif new_swim_state == "DEAD":
                if conn_info:
                    conn_info.swim_state = "DEAD" # Mark it first
                    await self._handle_node_dead(target_zmq_address) # Then process closure

    def _parse_swim_addr_str(self, swim_addr_str: str) -> Optional[Tuple[str, int]]:
        try:
            host, port_str = swim_addr_str.split(':')
            return host, int(port_str)
        except ValueError:
            logger.error(f"HELPER ({self.node_id}): Could not parse SWIM address string: {swim_addr_str}")
            return None

    async def _handle_node_dead(self, zmq_node_id: str): # zmq_node_id is ZMQ "host:port"
        if zmq_node_id in self._connections:
            conn = self._connections[zmq_node_id]
            conn.state = ConnectionState.CLOSING # Mark for closure
            # conn.swim_state is already DEAD from caller
            
            logger.warning(f"CONNECTION_CLOSURE ({self.node_id}): Closing connection to ZMQ {zmq_node_id} due to DEAD state")
            
            if self._message_redistribute_callback:
                try:
                    # Assuming redistribute callback expects ZMQ address
                    await self._message_redistribute_callback(zmq_node_id) 
                    logger.info(f"MESSAGE_REDISTRIBUTION ({self.node_id}): Redistributed messages for dead ZMQ node {zmq_node_id}")
                except Exception as e:
                    logger.error(f"MESSAGE_REDISTRIBUTION ({self.node_id}): Error redistributing messages for ZMQ {zmq_node_id}: {e}")
            
            await self._close_connection(zmq_node_id)
    
    async def _establish_connection(self, zmq_node_id: str, swim_addr_tuple: Optional[Tuple[str, int]]): # zmq_node_id is ZMQ "host:port"
        try:
            logger.info(f"CONNECTION_ESTABLISHMENT ({self.node_id}): Attempting to establish connection to ZMQ {zmq_node_id}")
            
            # Clean up if there's an old failed/closed connection record
            if zmq_node_id in self._connections and self._connections[zmq_node_id].state in [ConnectionState.FAILED, ConnectionState.CLOSING]:
                logger.info(f"CONNECTION_ESTABLISHMENT ({self.node_id}): Cleaning up prior failed/closed record for ZMQ {zmq_node_id}")
                await self._close_connection(zmq_node_id) # Ensures socket is closed by dealer if it exists

            current_time = time.time()
            conn = ConnectionInfo(
                node_id=zmq_node_id, # Storing ZMQ address as the key ID
                state=ConnectionState.CONNECTING,
                established_at=current_time,
                last_used=current_time,
                swim_state=self._swim_members.get(f"{swim_addr_tuple[0]}:{swim_addr_tuple[1]}" if swim_addr_tuple else "UNKNOWN", "ALIVE"), # Default to ALIVE if establishing
                swim_address=swim_addr_tuple,
                zmq_address=zmq_node_id
            )
            self._connections[zmq_node_id] = conn
            
            if self._dealer_connect_callback:
                # Dealer callback should establish the ZMQ DEALER socket connection
                # It returns the socket, but ConnectionManager primarily cares about success/failure
                # The DealerManager itself will store and manage the socket.
                zmq_socket = await self._dealer_connect_callback(zmq_node_id) # This is dealer_manager.get_connection
                
                if zmq_socket: # Implies successful ZMQ DEALER socket creation/connection by DealerManager
                    conn.state = ConnectionState.ACTIVE # Directly to ACTIVE if dealer_connect was successful
                    conn.established_at = time.time() # Update timestamp to actual ZMQ connection time
                    logger.info(f"CONNECTION_ESTABLISHMENT ({self.node_id}): Successfully established ZMQ connection to {zmq_node_id}")
                else: # DealerManager failed to provide a socket
                    conn.state = ConnectionState.FAILED
                    conn.failure_count += 1
                    logger.error(f"CONNECTION_ESTABLISHMENT ({self.node_id}): DealerManager failed to create/provide socket for ZMQ {zmq_node_id}")
            else:
                logger.error(f"CONNECTION_ESTABLISHMENT ({self.node_id}): No DEALER connect callback configured for ZMQ {zmq_node_id}")
                conn.state = ConnectionState.FAILED
                conn.failure_count += 1
                
        except Exception as e:
            logger.error(f"CONNECTION_ESTABLISHMENT ({self.node_id}): Failed to establish connection to ZMQ {zmq_node_id}: {e}", exc_info=True)
            if zmq_node_id in self._connections:
                self._connections[zmq_node_id].state = ConnectionState.FAILED
                self._connections[zmq_node_id].failure_count += 1
    
    async def _close_connection(self, zmq_node_id: str): # zmq_node_id is ZMQ "host:port"
        if zmq_node_id not in self._connections: return
        
        try:
            logger.info(f"CONNECTION_CLOSURE ({self.node_id}): Closing connection to ZMQ {zmq_node_id}")
            if self._dealer_disconnect_callback:
                # Dealer disconnect callback should handle closing the ZMQ DEALER socket
                await self._dealer_disconnect_callback(zmq_node_id) # This is dealer_manager.mark_failed / or a more direct close
            
            del self._connections[zmq_node_id]
            logger.info(f"CONNECTION_POOL ({self.node_id}): Removed connection to ZMQ {zmq_node_id} from pool")
        
        except Exception as e:
            logger.error(f"CONNECTION_CLOSURE ({self.node_id}): Error closing connection to ZMQ {zmq_node_id}: {e}", exc_info=True)
    
    async def _close_all_connections(self):
        node_ids = list(self._connections.keys())
        for zmq_node_id in node_ids: await self._close_connection(zmq_node_id)
        logger.info(f"CONNECTION_POOL ({self.node_id}): Closed {len(node_ids)} connections")
    
    def mark_connection_used(self, zmq_node_id: str): # zmq_node_id is ZMQ "host:port"
        if zmq_node_id in self._connections:
            self._connections[zmq_node_id].last_used = time.time()
            logger.debug(f"CONNECTION_HEALTH ({self.node_id}): Marked connection to ZMQ {zmq_node_id} as used")
    
    def mark_connection_failed(self, zmq_node_id: str, reason: str = "unspecified"): # zmq_node_id is ZMQ "host:port"
        if zmq_node_id in self._connections:
            conn = self._connections[zmq_node_id]
            conn.failure_count += 1
            
            logger.warning(f"CONNECTION_HEALTH ({self.node_id}): Recorded failure for ZMQ {zmq_node_id}. Reason: {reason}. Count: {conn.failure_count}/{self.max_failure_count}. Current state: {conn.state.name}")

            # Only transition to FAILED if it wasn't just a transient "not ready" and max failures are hit.
            # If the reason was "CONNECTION_READINESS_CHECK_FAILED", it might be a race condition.
            # Give it a chance to become active without immediately marking FAILED unless max_failure_count is hit.
            if conn.failure_count >= self.max_failure_count:
                if conn.state != ConnectionState.FAILED:
                    logger.error(f"CONNECTION_HEALTH ({self.node_id}): Connection to ZMQ {zmq_node_id} marked as FAILED "
                               f"after {conn.failure_count} failures. Reason for last failure: {reason}")
                    conn.state = ConnectionState.FAILED
                    # Potentially notify DealerManager to update circuit breaker more directly here if needed
                    # For now, circuit breaker is updated by DealerManager when its own send attempts fail.
            elif conn.state == ConnectionState.ACTIVE: # If it was active and a failure occurred
                logger.warning(f"CONNECTION_HEALTH ({self.node_id}): Connection to ZMQ {zmq_node_id} was ACTIVE, now marking DEGRADED due to failure. Reason: {reason}")
                conn.state = ConnectionState.DEGRADED # Or some other transient failure state
            # else:
                # logger.debug(f"CONNECTION_HEALTH ({self.node_id}): Connection to ZMQ {zmq_node_id} not ACTIVE, failure count incremented. Current state: {conn.state.name}")
    
    def get_healthy_connections(self) -> Set[str]: # Returns set of ZMQ "host:port"
        healthy = { zid for zid, conn_info in self._connections.items() if conn_info.state == ConnectionState.ACTIVE }
        logger.debug(f"CONNECTION_POOL ({self.node_id}): {len(healthy)} healthy (ACTIVE) ZMQ connections available")
        return healthy
    
    def can_send_to_node(self, zmq_node_id: str) -> bool: # zmq_node_id is ZMQ "host:port"
        conn_info = self._connections.get(zmq_node_id)
        if not conn_info:
            logger.debug(f"CONNECTION_HEALTH ({self.node_id}): No connection record for ZMQ {zmq_node_id}, cannot send.")
            return False
        
        # Only allow sending if ZMQ connection state is ACTIVE
        can_send = conn_info.state == ConnectionState.ACTIVE
        
        if not can_send:
            logger.warning(f"CONNECTION_HEALTH ({self.node_id}): Cannot send to ZMQ {zmq_node_id}, state: {conn_info.state.name}")
        else:
            logger.debug(f"CONNECTION_HEALTH ({self.node_id}): Can send to ZMQ {zmq_node_id}, connection state is ACTIVE.")
        return can_send
    
    async def _health_check_loop(self):
        logger.info(f"CONNECTION_HEALTH ({self.node_id}): Started health monitoring loop")
        while self._running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError: break
            except Exception as e: logger.error(f"CONNECTION_HEALTH ({self.node_id}): Error in health check loop: {e}", exc_info=True)
        logger.info(f"CONNECTION_HEALTH ({self.node_id}): Stopped health monitoring loop")
    
    async def _perform_health_checks(self):
        current_time = time.time()
        unhealthy_to_retry = []
        idle_to_close = []
        
        async with self._lock:
            for zmq_node_id, conn in list(self._connections.items()):
                # Check for idle connections
                if conn.time_since_use() > self.idle_timeout:
                    idle_to_close.append(zmq_node_id)
                
                # Check for failed connections that need recovery if SWIM says ALIVE
                swim_id_str = f"{conn.swim_address[0]}:{conn.swim_address[1]}" if conn.swim_address else None
                if conn.state == ConnectionState.FAILED and swim_id_str and self._swim_members.get(swim_id_str) == "ALIVE":
                    unhealthy_to_retry.append((zmq_node_id, conn.swim_address))
        
        for zmq_node_id in idle_to_close:
            logger.info(f"CONNECTION_HEALTH ({self.node_id}): Closing idle connection to ZMQ {zmq_node_id}")
            await self._close_connection(zmq_node_id)
        
        for zmq_node_id, swim_addr_tuple in unhealthy_to_retry:
            logger.info(f"CONNECTION_RECOVERY ({self.node_id}): Attempting recovery for failed connection to ZMQ {zmq_node_id} (SWIM: {swim_addr_tuple})")
            await self._establish_connection(zmq_node_id, swim_addr_tuple)
        
        if idle_to_close or unhealthy_to_retry:
            logger.info(f"CONNECTION_HEALTH ({self.node_id}): Closed {len(idle_to_close)} idle connections, "
                       f"attempted recovery for {len(unhealthy_to_retry)} failed connections")
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        stats_by_state = {state.name.lower(): 0 for state in ConnectionState}
        for conn in self._connections.values(): stats_by_state[conn.state.name.lower()] += 1
        
        return {
            "manager_node_id": self.node_id,
            "total_zmq_connections": len(self._connections),
            "healthy_zmq_connections": sum(1 for c in self._connections.values() if c.state == ConnectionState.ACTIVE),
            "swim_members_tracked": len(self._swim_members),
            "zmq_connection_states": stats_by_state,
            "port_mappings_by_swim": len(self._port_mappings_by_swim_addr),
            "port_mappings_by_zmq": len(self._port_mappings_by_zmq_addr),
            "running": self._running
        }
    
    def get_connection_info(self, swim_node_id_str: str) -> Optional[Dict[str, Any]]: # Expects SWIM "host:port"
        zmq_address = self.get_zmq_address_for_swim(swim_node_id_str)
        if not zmq_address or zmq_address not in self._connections:
            return None
        
        conn = self._connections[zmq_address]
        return {
            "swim_node_id": swim_node_id_str, # The input ID
            "zmq_node_id": conn.node_id, # ZMQ address this connection is for
            "connection_state": conn.state.name,
            "swim_protocol_state": conn.swim_state,
            "established_at": conn.established_at,
            "last_used_at": conn.last_used,
            "time_since_use_sec": conn.time_since_use(),
            "failure_count": conn.failure_count,
            "is_healthy_for_messaging": conn.is_healthy()
        }