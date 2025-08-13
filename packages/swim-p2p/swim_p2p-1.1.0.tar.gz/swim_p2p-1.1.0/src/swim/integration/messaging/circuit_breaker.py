"""
Circuit Breaker implementation for SWIM-ZMQ integration.

Provides fail-fast behavior with automatic recovery testing to prevent
cascading failures in the P2P messaging system.
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass
from enum import Enum, auto

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = auto()      # Normal operation
    OPEN = auto()        # Fail-fast mode
    HALF_OPEN = auto()   # Testing recovery


@dataclass
class CircuitConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: float = 30.0      # Seconds before trying recovery
    success_threshold: int = 3          # Successes needed to close
    probe_interval: float = 5.0         # Seconds between probe messages
    max_probe_attempts: int = 3         # Max probe attempts in half-open


class CircuitBreaker:
    """
    Circuit breaker for node connections with SWIM integration.
    
    Implements the circuit breaker pattern with three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Fail-fast, all requests rejected immediately  
    - HALF_OPEN: Testing recovery with probe messages
    """
    
    def __init__(self, node_id: str, target_node: str, config: Optional[CircuitConfig] = None):
        """
        Initialize circuit breaker for a specific node connection.
        
        Args:
            node_id: Source node identifier
            target_node: Target node identifier
            config: Circuit breaker configuration
        """
        self.node_id = node_id
        self.target_node = target_node
        self.config = config or CircuitConfig()
        
        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.last_probe_time = 0.0
        self.probe_attempts = 0
        
        # Callbacks
        self.probe_callback: Optional[Callable] = None
        self.state_change_callback: Optional[Callable] = None
        
        # Background tasks
        self._running = False
        self._probe_task: Optional[asyncio.Task] = None
        
        logger.info(f"CIRCUIT_BREAKER: Initialized for {node_id} -> {target_node}")
    
    def set_probe_callback(self, callback: Callable[[str], bool]):
        """Set callback for sending probe messages."""
        self.probe_callback = callback
    
    def set_state_change_callback(self, callback: Callable[[str, CircuitState, CircuitState], None]):
        """Set callback for state changes."""
        self.state_change_callback = callback
    
    async def start(self):
        """Start circuit breaker monitoring."""
        if self._running:
            return
        
        self._running = True
        self._probe_task = asyncio.create_task(self._probe_loop())
        logger.info(f"CIRCUIT_BREAKER: Started monitoring {self.target_node}")
    
    async def stop(self):
        """Stop circuit breaker monitoring."""
        self._running = False
        
        if self._probe_task:
            self._probe_task.cancel()
            try:
                await self._probe_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"CIRCUIT_BREAKER: Stopped monitoring {self.target_node}")
    
    async def call(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation through circuit breaker.
        
        Args:
            operation: Function to execute
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Operation result
            
        Raises:
            CircuitBreakerOpenError: When circuit is open
        """
        if self.state == CircuitState.OPEN:
            # Check if we should transition to half-open
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                await self._transition_to_half_open()
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker open for {self.target_node}")
        
        if self.state == CircuitState.HALF_OPEN:
            # In half-open state, only allow limited requests
            if self.probe_attempts >= self.config.max_probe_attempts:
                raise CircuitBreakerOpenError(f"Circuit breaker in half-open, max probes reached")
        
        try:
            # Execute the operation
            result = await operation(*args, **kwargs) if asyncio.iscoroutinefunction(operation) else operation(*args, **kwargs)
            await self._record_success()
            return result
            
        except Exception as e:
            await self._record_failure()
            raise
    
    async def _record_success(self):
        """Record successful operation."""
        self.failure_count = 0  # Reset failure count
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.info(f"CIRCUIT_BREAKER: Success {self.success_count}/{self.config.success_threshold} "
                       f"for {self.target_node}")
            
            if self.success_count >= self.config.success_threshold:
                await self._transition_to_closed()
        
        elif self.state == CircuitState.CLOSED:
            # Already closed, just log success
            logger.debug(f"CIRCUIT_BREAKER: Operation successful for {self.target_node}")
    
    async def _record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        logger.warning(f"CIRCUIT_BREAKER: Failure {self.failure_count}/{self.config.failure_threshold} "
                      f"for {self.target_node}")
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                await self._transition_to_open()
        
        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open goes back to open
            await self._transition_to_open()
    
    async def _transition_to_open(self):
        """Transition to OPEN state."""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.success_count = 0
        self.probe_attempts = 0
        
        logger.warning(f"CIRCUIT_BREAKER: {self.target_node} OPENED "
                      f"(failures: {self.failure_count})")
        
        await self._notify_state_change(old_state, self.state)
    
    async def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.probe_attempts = 0
        
        logger.info(f"CIRCUIT_BREAKER: {self.target_node} HALF_OPEN "
                   f"(testing recovery)")
        
        await self._notify_state_change(old_state, self.state)
    
    async def _transition_to_closed(self):
        """Transition to CLOSED state."""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.probe_attempts = 0
        
        logger.info(f"CIRCUIT_BREAKER: {self.target_node} CLOSED "
                   f"(recovery successful)")
        
        await self._notify_state_change(old_state, self.state)
    
    async def _notify_state_change(self, old_state: CircuitState, new_state: CircuitState):
        """Notify about state changes."""
        if self.state_change_callback:
            try:
                await self.state_change_callback(self.target_node, old_state, new_state)
            except Exception as e:
                logger.error(f"CIRCUIT_BREAKER: Error in state change callback: {e}")
    
    async def _probe_loop(self):
        """Background task for sending probe messages in half-open state."""
        while self._running:
            try:
                await asyncio.sleep(self.config.probe_interval)
                
                if self.state == CircuitState.HALF_OPEN and self.probe_callback:
                    await self._send_probe_message()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"CIRCUIT_BREAKER: Error in probe loop: {e}")
    
    async def _send_probe_message(self):
        """Send probe message to test node recovery."""
        if self.probe_attempts >= self.config.max_probe_attempts:
            return
        
        self.probe_attempts += 1
        self.last_probe_time = time.time()
        
        logger.info(f"CIRCUIT_BREAKER: Sending probe {self.probe_attempts}/{self.config.max_probe_attempts} "
                   f"to {self.target_node}")
        
        try:
            # Send probe message through callback
            success = await self.probe_callback(self.target_node)
            
            if success:
                await self._record_success()
                logger.info(f"CIRCUIT_BREAKER: Probe successful for {self.target_node}")
            else:
                await self._record_failure()
                logger.warning(f"CIRCUIT_BREAKER: Probe failed for {self.target_node}")
                
        except Exception as e:
            await self._record_failure()
            logger.error(f"CIRCUIT_BREAKER: Probe error for {self.target_node}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "target_node": self.target_node,
            "state": self.state.name,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "probe_attempts": self.probe_attempts,
            "last_failure_time": self.last_failure_time,
            "last_probe_time": self.last_probe_time,
            "time_since_last_failure": time.time() - self.last_failure_time,
            "recovery_timeout_remaining": max(0, self.config.recovery_timeout - (time.time() - self.last_failure_time))
        }
    
    def force_open(self):
        """Force circuit breaker to open state (for testing)."""
        self.state = CircuitState.OPEN
        self.failure_count = self.config.failure_threshold
        self.last_failure_time = time.time()
        logger.warning(f"CIRCUIT_BREAKER: Forced {self.target_node} to OPEN state")
    
    def force_close(self):
        """Force circuit breaker to closed state (for recovery)."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"CIRCUIT_BREAKER: Forced {self.target_node} to CLOSED state")
    
    async def handle_node_resurrection(self):
        """
        Handle SWIM node resurrection event.
        Reset circuit breaker state when SWIM detects node is alive again.
        """
        if self.state in [CircuitState.OPEN, CircuitState.HALF_OPEN]:
            old_state = self.state
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.probe_attempts = 0
            
            logger.info(f"CIRCUIT_BREAKER: {self.target_node} RESET due to SWIM resurrection "
                       f"({old_state.name} -> CLOSED)")
            
            await self._notify_state_change(old_state, self.state)


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers for different node connections.
    
    Integrates with SWIM membership to automatically manage circuit breakers
    for all known nodes in the cluster.
    """
    
    def __init__(self, node_id: str, config: Optional[CircuitConfig] = None):
        """
        Initialize circuit breaker manager.
        
        Args:
            node_id: This node's identifier
            config: Default configuration for circuit breakers
        """
        self.node_id = node_id
        self.config = config or CircuitConfig()
        
        # Circuit breaker tracking
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Callbacks
        self.probe_callback: Optional[Callable] = None
        self.swim_membership_callback: Optional[Callable] = None
        
        # Statistics
        self.stats = {
            "total_circuits": 0,
            "open_circuits": 0,
            "half_open_circuits": 0,
            "closed_circuits": 0,
            "total_failures": 0,
            "total_recoveries": 0
        }
        
        logger.info(f"CIRCUIT_MANAGER: Initialized for node {node_id}")
    
    def set_probe_callback(self, callback: Callable[[str], bool]):
        """Set callback for sending probe messages."""
        self.probe_callback = callback
    
    def set_swim_membership_callback(self, callback: Callable[[], List[str]]):
        """Set callback to get current SWIM membership."""
        self.swim_membership_callback = callback
    
    async def handle_swim_member_alive(self, node_address: str):
        """
        Handle SWIM member alive event (resurrection).
        Reset circuit breaker state for the resurrected node.
        
        Args:
            node_address: Address of the resurrected node
        """
        if node_address in self.circuit_breakers:
            await self.circuit_breakers[node_address].handle_node_resurrection()
            logger.info(f"CIRCUIT_MANAGER: Reset circuit breaker for resurrected node {node_address}")
        else:
            logger.debug(f"CIRCUIT_MANAGER: No circuit breaker exists for resurrected node {node_address}")
    
    async def start(self):
        """Start circuit breaker manager."""
        logger.info("CIRCUIT_MANAGER: Started")
    
    async def stop(self):
        """Stop all circuit breakers."""
        for cb in self.circuit_breakers.values():
            await cb.stop()
        
        logger.info("CIRCUIT_MANAGER: Stopped all circuit breakers")
    
    async def get_or_create_circuit_breaker(self, target_node: str) -> CircuitBreaker:
        """
        Get existing or create new circuit breaker for target node.
        
        Args:
            target_node: Target node identifier
            
        Returns:
            Circuit breaker instance
        """
        if target_node not in self.circuit_breakers:
            cb = CircuitBreaker(self.node_id, target_node, self.config)
            
            # Set callbacks
            if self.probe_callback:
                cb.set_probe_callback(self.probe_callback)
            
            cb.set_state_change_callback(self._on_state_change)
            
            # Start the circuit breaker
            await cb.start()
            
            self.circuit_breakers[target_node] = cb
            self.stats["total_circuits"] += 1
            
            logger.info(f"CIRCUIT_MANAGER: Created circuit breaker for {target_node}")
        
        return self.circuit_breakers[target_node]
    
    async def execute_with_circuit_breaker(self, target_node: str, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation with circuit breaker protection.
        
        Args:
            target_node: Target node identifier
            operation: Operation to execute
            *args, **kwargs: Operation arguments
            
        Returns:
            Operation result
        """
        cb = await self.get_or_create_circuit_breaker(target_node)
        return await cb.call(operation, *args, **kwargs)
    
    async def _on_state_change(self, target_node: str, old_state: CircuitState, new_state: CircuitState):
        """Handle circuit breaker state changes."""
        logger.info(f"CIRCUIT_STATE_CHANGE: {target_node} {old_state.name} -> {new_state.name}")
        
        # Update statistics
        if new_state == CircuitState.OPEN:
            self.stats["total_failures"] += 1
        elif old_state == CircuitState.OPEN and new_state == CircuitState.CLOSED:
            self.stats["total_recoveries"] += 1
        
        # Update SWIM membership if callback available
        if self.swim_membership_callback and new_state == CircuitState.OPEN:
            # Notify SWIM that node might be down
            try:
                await self.swim_membership_callback(target_node, "CIRCUIT_OPEN")
            except Exception as e:
                logger.error(f"CIRCUIT_MANAGER: Error notifying SWIM: {e}")
    
    def get_circuit_status(self, target_node: str) -> Optional[Dict[str, Any]]:
        """Get status of circuit breaker for specific node."""
        if target_node in self.circuit_breakers:
            return self.circuit_breakers[target_node].get_status()
        return None
    
    def get_all_circuit_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        status = {}
        
        # Update statistics
        self.stats["open_circuits"] = sum(1 for cb in self.circuit_breakers.values() 
                                         if cb.state == CircuitState.OPEN)
        self.stats["half_open_circuits"] = sum(1 for cb in self.circuit_breakers.values() 
                                              if cb.state == CircuitState.HALF_OPEN)
        self.stats["closed_circuits"] = sum(1 for cb in self.circuit_breakers.values() 
                                           if cb.state == CircuitState.CLOSED)
        
        for target_node, cb in self.circuit_breakers.items():
            status[target_node] = cb.get_status()
        
        return {
            "statistics": self.stats.copy(),
            "circuit_breakers": status
        }
