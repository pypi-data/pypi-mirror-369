"""
Enhanced Load Balancer with Circuit Breaker Integration for SWIM-ZMQ.

Provides intelligent message routing that considers circuit breaker states,
automatic failover, and circuit-aware health monitoring for optimal
system reliability and performance.
"""

import asyncio
import time
import random
import logging
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque

# Import circuit breaker components
from swim.messaging.circuit_breaker import (
    CircuitBreakerManager, CircuitState, CircuitConfig, CircuitBreakerOpenError
)

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Message routing strategies with circuit breaker awareness."""
    ROUND_ROBIN = auto()        # Simple round-robin
    WEIGHTED_ROUND_ROBIN = auto()  # Weighted by capacity
    LEAST_CONNECTIONS = auto()  # Route to node with fewest connections
    LEAST_LATENCY = auto()      # Route to node with lowest latency
    HASH_BASED = auto()         # Consistent hashing for sticky routing
    ADAPTIVE = auto()           # Adaptive based on current conditions
    CIRCUIT_AWARE = auto()      # Circuit breaker state aware routing


class NodeHealth(Enum):
    """Node health states for routing decisions."""
    HEALTHY = auto()      # Node is healthy and available
    DEGRADED = auto()     # Node is experiencing issues but available
    OVERLOADED = auto()   # Node is overloaded, avoid if possible
    UNAVAILABLE = auto()  # Node is unavailable for routing
    CIRCUIT_OPEN = auto() # Node has open circuit breaker


@dataclass
class NodeMetrics:
    """Enhanced metrics for a node with circuit breaker integration."""
    node_id: str
    last_updated: float = field(default_factory=time.time)
    
    # Capacity metrics
    cpu_usage: float = 0.0          # 0.0 to 1.0
    memory_usage: float = 0.0       # 0.0 to 1.0
    queue_depth: int = 0            # Number of pending messages
    max_capacity: int = 1000        # Maximum queue capacity
    
    # Performance metrics
    avg_latency: float = 0.0        # Average response latency (ms)
    success_rate: float = 1.0       # Success rate (0.0 to 1.0)
    throughput: float = 0.0         # Messages per second
    
    # Connection metrics
    active_connections: int = 0
    max_connections: int = 100
    
    # Health indicators
    health: NodeHealth = NodeHealth.HEALTHY
    last_heartbeat: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    
    # Circuit breaker integration
    circuit_state: CircuitState = CircuitState.CLOSED
    circuit_failure_count: int = 0
    circuit_recovery_attempts: int = 0
    last_circuit_state_change: float = field(default_factory=time.time)
    
    def get_capacity_score(self) -> float:
        """Calculate capacity score with circuit breaker penalty."""
        if self.circuit_state == CircuitState.OPEN:
            return 0.0  # No capacity if circuit is open
        
        # Combine multiple capacity indicators
        cpu_score = 1.0 - self.cpu_usage
        memory_score = 1.0 - self.memory_usage
        queue_score = 1.0 - (self.queue_depth / max(self.max_capacity, 1))
        connection_score = 1.0 - (self.active_connections / max(self.max_connections, 1))
        
        # Weighted average
        weights = [0.3, 0.3, 0.3, 0.1]  # cpu, memory, queue, connections
        scores = [cpu_score, memory_score, queue_score, connection_score]
        
        base_score = max(0.0, sum(w * s for w, s in zip(weights, scores)))
        
        # Apply circuit breaker penalty
        circuit_penalty = self._get_circuit_penalty()
        return base_score * circuit_penalty
    
    def get_performance_score(self) -> float:
        """Calculate performance score with circuit breaker considerations."""
        if self.circuit_state == CircuitState.OPEN:
            return 0.0  # No performance if circuit is open
        
        # Normalize latency (assume 1000ms is very poor)
        latency_score = max(0.0, 1.0 - (self.avg_latency / 1000.0))
        
        # Success rate is already normalized
        success_score = self.success_rate
        
        # Combine scores
        base_score = (latency_score + success_score) / 2.0
        
        # Apply circuit breaker penalty
        circuit_penalty = self._get_circuit_penalty()
        return base_score * circuit_penalty
    
    def _get_circuit_penalty(self) -> float:
        """Calculate penalty based on circuit breaker state."""
        if self.circuit_state == CircuitState.OPEN:
            return 0.0
        elif self.circuit_state == CircuitState.HALF_OPEN:
            return 0.5  # Reduced capacity during recovery testing
        else:  # CLOSED
            # Small penalty based on recent failures
            failure_penalty = max(0.0, 1.0 - (self.circuit_failure_count * 0.1))
            return failure_penalty
    
    def get_routing_weight(self) -> float:
        """Calculate overall routing weight with circuit breaker integration."""
        if self.health == NodeHealth.UNAVAILABLE or self.circuit_state == CircuitState.OPEN:
            return 0.0
        
        capacity_score = self.get_capacity_score()
        performance_score = self.get_performance_score()
        
        # Enhanced health penalty including circuit state
        health_multiplier = {
            NodeHealth.HEALTHY: 1.0,
            NodeHealth.DEGRADED: 0.7,
            NodeHealth.OVERLOADED: 0.3,
            NodeHealth.UNAVAILABLE: 0.0,
            NodeHealth.CIRCUIT_OPEN: 0.0
        }[self.health]
        
        # Circuit state multiplier
        circuit_multiplier = {
            CircuitState.CLOSED: 1.0,
            CircuitState.HALF_OPEN: 0.5,  # Reduced weight during recovery
            CircuitState.OPEN: 0.0
        }[self.circuit_state]
        
        # Age penalty (stale metrics are less reliable)
        age_seconds = time.time() - self.last_updated
        age_penalty = max(0.1, 1.0 - (age_seconds / 300.0))  # 5 minute decay
        
        return capacity_score * performance_score * health_multiplier * circuit_multiplier * age_penalty
    
    def is_available(self) -> bool:
        """Check if node is available for routing with circuit breaker consideration."""
        return (
            self.health not in [NodeHealth.UNAVAILABLE, NodeHealth.CIRCUIT_OPEN] and
            self.circuit_state != CircuitState.OPEN and
            time.time() - self.last_heartbeat < 30.0  # 30 second heartbeat timeout
        )
    
    def is_circuit_healthy(self) -> bool:
        """Check if circuit breaker is in healthy state."""
        return self.circuit_state == CircuitState.CLOSED


@dataclass
class RoutingRule:
    """Enhanced routing rule with circuit breaker preferences."""
    message_type: str
    preferred_nodes: Set[str] = field(default_factory=set)
    excluded_nodes: Set[str] = field(default_factory=set)
    min_capacity_threshold: float = 0.2  # Minimum capacity required
    strategy_override: Optional[RoutingStrategy] = None
    sticky_routing: bool = False  # Use consistent hashing
    
    # Circuit breaker specific rules
    allow_half_open_circuits: bool = False  # Allow routing to half-open circuits
    circuit_failure_threshold: int = 3      # Max circuit failures before exclusion
    require_closed_circuit: bool = True     # Require closed circuit for routing


class LoadBalancer:
    """
    Enhanced Load Balancer with Circuit Breaker Integration.
    
    Provides intelligent message routing that considers circuit breaker states,
    automatic failover when circuits open, and circuit-aware health monitoring
    for optimal system reliability and performance.
    """
    
    def __init__(self, node_id: str, strategy: RoutingStrategy = RoutingStrategy.CIRCUIT_AWARE):
        """
        Initialize enhanced load balancer with circuit breaker integration.
        
        Args:
            node_id: Identifier for this node
            strategy: Default routing strategy
        """
        self.node_id = node_id
        self.default_strategy = strategy
        
        # Node tracking with circuit breaker integration
        self.nodes: Dict[str, NodeMetrics] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        
        # Circuit breaker integration
        self.circuit_manager = CircuitBreakerManager(
            node_id=node_id,
            config=CircuitConfig(
                failure_threshold=5,
                recovery_timeout=30.0,
                success_threshold=3,
                probe_interval=10.0,
                max_probe_attempts=3
            )
        )
        
        # Routing state
        self.round_robin_index = 0
        self.sticky_sessions: Dict[str, str] = {}  # workflow_id -> node_id
        
        # Configuration
        self.health_check_interval = 10.0
        self.metrics_update_interval = 5.0
        self.max_nodes = 100
        self.failover_attempts = 5  # Increased for circuit breaker scenarios
        
        # Callbacks
        self.capacity_provider: Optional[Callable] = None
        self.health_checker: Optional[Callable] = None
        self.route_callback: Optional[Callable] = None
        self.circuit_state_callback: Optional[Callable] = None
        
        # Background tasks
        self._running = False
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Enhanced statistics with circuit breaker metrics
        self._stats = {
            "total_routes": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "failover_routes": 0,
            "circuit_blocked_routes": 0,
            "circuit_recovery_routes": 0,
            "routes_by_strategy": defaultdict(int),
            "routes_by_node": defaultdict(int),
            "circuit_state_changes": defaultdict(int)
        }
        
        logger.info(f"ENHANCED_LOAD_BALANCER: Initialized for node {node_id} "
                   f"with strategy {strategy.name} and circuit breaker integration")
    
    def set_capacity_provider(self, provider: Callable[[str], Optional[Dict[str, Any]]]):
        """Set callback to get node capacity metrics."""
        self.capacity_provider = provider
        logger.info("ENHANCED_LOAD_BALANCER: Capacity provider configured")
    
    def set_health_checker(self, checker: Callable[[str], bool]):
        """Set callback to check node health."""
        self.health_checker = checker
        logger.info("ENHANCED_LOAD_BALANCER: Health checker configured")
    
    def set_route_callback(self, callback: Callable[[str, str, str], None]):
        """Set callback for route decisions (for monitoring)."""
        self.route_callback = callback
        logger.info("ENHANCED_LOAD_BALANCER: Route callback configured")
    
    def set_circuit_state_callback(self, callback: Callable[[str, CircuitState, CircuitState], None]):
        """Set callback for circuit breaker state changes."""
        self.circuit_state_callback = callback
        logger.info("ENHANCED_LOAD_BALANCER: Circuit state callback configured")
    
    async def start(self):
        """Start enhanced load balancer with circuit breaker integration."""
        if self._running:
            return
        
        self._running = True
        
        # Start circuit breaker manager
        await self.circuit_manager.start()
        
        # Configure circuit breaker callbacks
        self.circuit_manager.set_probe_callback(self._send_circuit_probe)
        
        # Start health checking
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("ENHANCED_LOAD_BALANCER: Started with circuit breaker integration")
    
    async def stop(self):
        """Stop enhanced load balancer and clean up resources."""
        self._running = False
        
        # Stop circuit breaker manager
        await self.circuit_manager.stop()
        
        # Stop health checking
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("ENHANCED_LOAD_BALANCER: Stopped and cleaned up resources")
    
    def register_node(self, node_id: str, initial_metrics: Optional[Dict[str, Any]] = None):
        """
        Register a node for load balancing with circuit breaker setup.
        
        Args:
            node_id: Node identifier
            initial_metrics: Optional initial metrics
        """
        if len(self.nodes) >= self.max_nodes:
            logger.warning(f"ENHANCED_LOAD_BALANCER: Maximum nodes ({self.max_nodes}) reached, "
                          f"cannot register {node_id}")
            return
        
        metrics = NodeMetrics(node_id=node_id)
        
        if initial_metrics:
            self._update_node_metrics(metrics, initial_metrics)
        
        self.nodes[node_id] = metrics
        logger.info(f"ENHANCED_LOAD_BALANCER: Registered node {node_id} with circuit breaker")
    
    def unregister_node(self, node_id: str):
        """
        Unregister a node from load balancing and clean up circuit breaker.
        
        Args:
            node_id: Node identifier
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            
            # Clean up sticky sessions
            sessions_to_remove = [k for k, v in self.sticky_sessions.items() if v == node_id]
            for session in sessions_to_remove:
                del self.sticky_sessions[session]
            
            logger.info(f"ENHANCED_LOAD_BALANCER: Unregistered node {node_id}")
    
    def update_node_metrics(self, node_id: str, metrics: Dict[str, Any]):
        """
        Update metrics for a node with circuit breaker state sync.
        
        Args:
            node_id: Node identifier
            metrics: Updated metrics
        """
        if node_id not in self.nodes:
            logger.warning(f"ENHANCED_LOAD_BALANCER: Cannot update metrics for unknown node {node_id}")
            return
        
        node_metrics = self.nodes[node_id]
        self._update_node_metrics(node_metrics, metrics)
        
        # Sync circuit breaker state
        circuit_status = self.circuit_manager.get_circuit_status(node_id)
        if circuit_status:
            old_circuit_state = node_metrics.circuit_state
            node_metrics.circuit_state = CircuitState[circuit_status["state"]]
            node_metrics.circuit_failure_count = circuit_status["failure_count"]
            
            # Update health based on circuit state
            if node_metrics.circuit_state == CircuitState.OPEN:
                node_metrics.health = NodeHealth.CIRCUIT_OPEN
            elif node_metrics.health == NodeHealth.CIRCUIT_OPEN and node_metrics.circuit_state == CircuitState.CLOSED:
                node_metrics.health = NodeHealth.HEALTHY
            
            # Track state changes
            if old_circuit_state != node_metrics.circuit_state:
                node_metrics.last_circuit_state_change = time.time()
                self._stats["circuit_state_changes"][node_metrics.circuit_state.name] += 1
                
                # Notify callback
                if self.circuit_state_callback:
                    try:
                        self.circuit_state_callback(node_id, old_circuit_state, node_metrics.circuit_state)
                    except Exception as e:
                        logger.error(f"ENHANCED_LOAD_BALANCER: Error in circuit state callback: {e}")
        
        logger.debug(f"ENHANCED_LOAD_BALANCER: Updated metrics for node {node_id} "
                    f"(weight: {node_metrics.get_routing_weight():.3f}, "
                    f"circuit: {node_metrics.circuit_state.name})")
    
    def _update_node_metrics(self, node_metrics: NodeMetrics, metrics: Dict[str, Any]):
        """Update node metrics from dictionary with circuit breaker fields."""
        node_metrics.last_updated = time.time()
        
        # Update capacity metrics
        if "cpu_usage" in metrics:
            node_metrics.cpu_usage = float(metrics["cpu_usage"])
        if "memory_usage" in metrics:
            node_metrics.memory_usage = float(metrics["memory_usage"])
        if "queue_depth" in metrics:
            node_metrics.queue_depth = int(metrics["queue_depth"])
        if "max_capacity" in metrics:
            node_metrics.max_capacity = int(metrics["max_capacity"])
        
        # Update performance metrics
        if "avg_latency" in metrics:
            node_metrics.avg_latency = float(metrics["avg_latency"])
        if "success_rate" in metrics:
            node_metrics.success_rate = float(metrics["success_rate"])
        if "throughput" in metrics:
            node_metrics.throughput = float(metrics["throughput"])
        
        # Update connection metrics
        if "active_connections" in metrics:
            node_metrics.active_connections = int(metrics["active_connections"])
        if "max_connections" in metrics:
            node_metrics.max_connections = int(metrics["max_connections"])
        
        # Update health
        if "health" in metrics:
            health_str = metrics["health"].upper()
            if hasattr(NodeHealth, health_str):
                node_metrics.health = getattr(NodeHealth, health_str)
        
        # Update circuit breaker specific metrics
        if "circuit_state" in metrics:
            circuit_str = metrics["circuit_state"].upper()
            if hasattr(CircuitState, circuit_str):
                node_metrics.circuit_state = getattr(CircuitState, circuit_str)
        
        if "circuit_failure_count" in metrics:
            node_metrics.circuit_failure_count = int(metrics["circuit_failure_count"])
        
        # Update heartbeat
        node_metrics.last_heartbeat = time.time()
        
        # Reset failure count on successful update
        node_metrics.consecutive_failures = 0
    
    def add_routing_rule(self, rule: RoutingRule):
        """
        Add a routing rule for message type-based routing with circuit breaker support.
        
        Args:
            rule: Enhanced routing rule to add
        """
        self.routing_rules[rule.message_type] = rule
        logger.info(f"ENHANCED_LOAD_BALANCER: Added routing rule for message type {rule.message_type} "
                   f"(circuit_aware: {rule.require_closed_circuit})")
    
    def remove_routing_rule(self, message_type: str):
        """
        Remove a routing rule.
        
        Args:
            message_type: Message type to remove rule for
        """
        if message_type in self.routing_rules:
            del self.routing_rules[message_type]
            logger.info(f"ENHANCED_LOAD_BALANCER: Removed routing rule for message type {message_type}")
    
    async def route_message_with_circuit_protection(self, message_type: str, 
                                                   workflow_id: Optional[str] = None,
                                                   strategy_override: Optional[RoutingStrategy] = None,
                                                   operation: Optional[Callable] = None) -> Optional[str]:
        """
        Route a message with circuit breaker protection and automatic execution.
        
        Args:
            message_type: Type of message being routed
            workflow_id: Optional workflow ID for sticky routing
            strategy_override: Optional strategy override
            operation: Optional operation to execute with circuit breaker protection
            
        Returns:
            Node ID to route to, or None if no nodes available
        """
        # First, get routing decision
        target_node = self.route_message(message_type, workflow_id, strategy_override)
        
        if not target_node:
            return None
        
        # If operation provided, execute with circuit breaker protection
        if operation:
            try:
                await self.circuit_manager.execute_with_circuit_breaker(
                    target_node, operation
                )
                self._stats["circuit_recovery_routes"] += 1
                return target_node
                
            except CircuitBreakerOpenError:
                logger.warning(f"ENHANCED_LOAD_BALANCER: Circuit breaker blocked route to {target_node}")
                self._stats["circuit_blocked_routes"] += 1
                
                # Try failover routing
                exclude_nodes = {target_node}
                return self.route_with_failover(message_type, workflow_id, exclude_nodes)
            
            except Exception as e:
                logger.error(f"ENHANCED_LOAD_BALANCER: Operation failed for {target_node}: {e}")
                return None
        
        return target_node
    
    def route_message(self, message_type: str, workflow_id: Optional[str] = None,
                     strategy_override: Optional[RoutingStrategy] = None) -> Optional[str]:
        """
        Route a message to the best available node with circuit breaker awareness.
        
        Args:
            message_type: Type of message being routed
            workflow_id: Optional workflow ID for sticky routing
            strategy_override: Optional strategy override
            
        Returns:
            Node ID to route to, or None if no nodes available
        """
        self._stats["total_routes"] += 1
        
        # Get available nodes (circuit breaker aware)
        available_nodes = self._get_available_nodes_with_circuit_check(message_type)
        if not available_nodes:
            logger.warning(f"ENHANCED_LOAD_BALANCER: No available nodes for message type {message_type} "
                          f"(considering circuit breaker states)")
            self._stats["failed_routes"] += 1
            return None
        
        # Determine routing strategy
        strategy = self._determine_strategy(message_type, strategy_override)
        self._stats["routes_by_strategy"][strategy.name] += 1
        
        # Check for sticky routing
        if workflow_id and strategy in [RoutingStrategy.HASH_BASED, RoutingStrategy.ADAPTIVE, RoutingStrategy.CIRCUIT_AWARE]:
            rule = self.routing_rules.get(message_type)
            if rule and rule.sticky_routing:
                sticky_node = self._get_sticky_node(workflow_id, available_nodes)
                if sticky_node:
                    return self._finalize_route(sticky_node, message_type, "sticky")
        
        # Route based on strategy
        selected_node = None
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            selected_node = self._route_round_robin(available_nodes)
        elif strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
            selected_node = self._route_weighted_round_robin(available_nodes)
        elif strategy == RoutingStrategy.LEAST_CONNECTIONS:
            selected_node = self._route_least_connections(available_nodes)
        elif strategy == RoutingStrategy.LEAST_LATENCY:
            selected_node = self._route_least_latency(available_nodes)
        elif strategy == RoutingStrategy.HASH_BASED:
            selected_node = self._route_hash_based(workflow_id or message_type, available_nodes)
        elif strategy == RoutingStrategy.ADAPTIVE:
            selected_node = self._route_adaptive(available_nodes)
        elif strategy == RoutingStrategy.CIRCUIT_AWARE:
            selected_node = self._route_circuit_aware(available_nodes)
        
        if selected_node:
            return self._finalize_route(selected_node, message_type, strategy.name)
        else:
            logger.warning(f"ENHANCED_LOAD_BALANCER: Failed to route message type {message_type} "
                          f"using strategy {strategy.name}")
            self._stats["failed_routes"] += 1
            return None
    
    def _get_available_nodes_with_circuit_check(self, message_type: str) -> List[str]:
        """Get list of available nodes considering circuit breaker states."""
        available = []
        rule = self.routing_rules.get(message_type)
        
        for node_id, metrics in self.nodes.items():
            # Check basic availability (includes circuit breaker check)
            if not metrics.is_available():
                continue
            
            # Check circuit breaker specific rules
            if rule:
                # Check if closed circuit is required
                if rule.require_closed_circuit and metrics.circuit_state != CircuitState.CLOSED:
                    continue
                
                # Check if half-open circuits are allowed
                if not rule.allow_half_open_circuits and metrics.circuit_state == CircuitState.HALF_OPEN:
                    continue
                
                # Check circuit failure threshold
                if metrics.circuit_failure_count >= rule.circuit_failure_threshold:
                    continue
                
                # Check excluded nodes
                if node_id in rule.excluded_nodes:
                    continue
                
                # Check preferred nodes (if specified, only use those)
                if rule.preferred_nodes and node_id not in rule.preferred_nodes:
                    continue
                
                # Check minimum capacity threshold
                if metrics.get_capacity_score() < rule.min_capacity_threshold:
                    continue
            else:
                # Default circuit breaker rules when no specific rule exists
                if metrics.circuit_state == CircuitState.OPEN:
                    continue
            
            available.append(node_id)
        
        return available
    
    def _determine_strategy(self, message_type: str, 
                           strategy_override: Optional[RoutingStrategy]) -> RoutingStrategy:
        """Determine which routing strategy to use with circuit breaker preference."""
        if strategy_override:
            return strategy_override
        
        rule = self.routing_rules.get(message_type)
        if rule and rule.strategy_override:
            return rule.strategy_override
        
        return self.default_strategy
    
    def _get_sticky_node(self, workflow_id: str, available_nodes: List[str]) -> Optional[str]:
        """Get sticky node for workflow, ensuring circuit breaker health."""
        if workflow_id in self.sticky_sessions:
            sticky_node = self.sticky_sessions[workflow_id]
            if sticky_node in available_nodes:
                # Additional circuit breaker check for sticky sessions
                if sticky_node in self.nodes:
                    node_metrics = self.nodes[sticky_node]
                    if node_metrics.is_circuit_healthy():
                        return sticky_node
                    else:
                        logger.info(f"ENHANCED_LOAD_BALANCER: Sticky session {workflow_id} -> {sticky_node} "
                                   f"broken due to circuit state: {node_metrics.circuit_state.name}")
                        # Remove unhealthy sticky session
                        del self.sticky_sessions[workflow_id]
        
        return None
    
    def _route_circuit_aware(self, available_nodes: List[str]) -> Optional[str]:
        """Circuit breaker aware routing strategy."""
        if not available_nodes:
            return None
        
        # Prioritize nodes by circuit health and performance
        node_scores = []
        
        for node_id in available_nodes:
            metrics = self.nodes[node_id]
            
            # Base score from routing weight
            base_score = metrics.get_routing_weight()
            
            # Circuit breaker bonus/penalty
            circuit_bonus = {
                CircuitState.CLOSED: 1.0,      # Full bonus for healthy circuits
                CircuitState.HALF_OPEN: 0.3,   # Reduced bonus during recovery
                CircuitState.OPEN: 0.0          # No bonus for open circuits
            }[metrics.circuit_state]
            
            # Recent recovery bonus (encourage using recently recovered nodes)
            time_since_recovery = time.time() - metrics.last_circuit_state_change
            if metrics.circuit_state == CircuitState.CLOSED and time_since_recovery < 300:  # 5 minutes
                recovery_bonus = 0.2 * (1.0 - time_since_recovery / 300.0)
            else:
                recovery_bonus = 0.0
            
            # Failure penalty
            failure_penalty = min(0.3, metrics.circuit_failure_count * 0.05)
            
            total_score = base_score * circuit_bonus + recovery_bonus - failure_penalty
            node_scores.append((node_id, total_score))
        
        # Sort by score and return best node
        node_scores.sort(key=lambda x: x[1], reverse=True)
        return node_scores[0][0] if node_scores else None
    
    def _route_round_robin(self, available_nodes: List[str]) -> str:
        """Simple round-robin routing."""
        if not available_nodes:
            return None
        
        node = available_nodes[self.round_robin_index % len(available_nodes)]
        self.round_robin_index += 1
        return node
    
    def _route_weighted_round_robin(self, available_nodes: List[str]) -> Optional[str]:
        """Weighted round-robin based on node capacity and circuit health."""
        if not available_nodes:
            return None
        
        # Calculate weights (includes circuit breaker penalties)
        weights = []
        for node_id in available_nodes:
            weight = self.nodes[node_id].get_routing_weight()
            weights.append(max(0.1, weight))  # Minimum weight to ensure all nodes get some traffic
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return available_nodes[0]  # Fallback to first node
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return available_nodes[i]
        
        return available_nodes[-1]  # Fallback
    
    def _route_least_connections(self, available_nodes: List[str]) -> Optional[str]:
        """Route to node with least active connections."""
        if not available_nodes:
            return None
        
        min_connections = float('inf')
        best_node = None
        
        for node_id in available_nodes:
            connections = self.nodes[node_id].active_connections
            if connections < min_connections:
                min_connections = connections
                best_node = node_id
        
        return best_node
    
    def _route_least_latency(self, available_nodes: List[str]) -> Optional[str]:
        """Route to node with lowest latency."""
        if not available_nodes:
            return None
        
        min_latency = float('inf')
        best_node = None
        
        for node_id in available_nodes:
            latency = self.nodes[node_id].avg_latency
            if latency < min_latency:
                min_latency = latency
                best_node = node_id
        
        return best_node
    
    def _route_hash_based(self, key: str, available_nodes: List[str]) -> Optional[str]:
        """Consistent hash-based routing for sticky sessions."""
        if not available_nodes:
            return None
        
        # Sort nodes for consistent ordering
        sorted_nodes = sorted(available_nodes)
        
        # Hash the key and select node
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        index = hash_value % len(sorted_nodes)
        
        return sorted_nodes[index]
    
    def _route_adaptive(self, available_nodes: List[str]) -> Optional[str]:
        """Adaptive routing based on current conditions including circuit state."""
        if not available_nodes:
            return None
        
        # Use weighted selection but with adaptive weights
        best_score = -1
        best_node = None
        
        for node_id in available_nodes:
            metrics = self.nodes[node_id]
            
            # Adaptive scoring based on multiple factors
            capacity_score = metrics.get_capacity_score()
            performance_score = metrics.get_performance_score()
            
            # Enhanced health bonus including circuit state
            health_bonus = {
                NodeHealth.HEALTHY: 0.2,
                NodeHealth.DEGRADED: 0.0,
                NodeHealth.OVERLOADED: -0.3,
                NodeHealth.UNAVAILABLE: -1.0,
                NodeHealth.CIRCUIT_OPEN: -1.0
            }[metrics.health]
            
            # Circuit state bonus
            circuit_bonus = {
                CircuitState.CLOSED: 0.1,
                CircuitState.HALF_OPEN: -0.1,
                CircuitState.OPEN: -1.0
            }[metrics.circuit_state]
            
            # Penalty for high queue depth
            queue_penalty = min(0.5, metrics.queue_depth / max(metrics.max_capacity, 1))
            
            # Circuit failure penalty
            circuit_failure_penalty = min(0.2, metrics.circuit_failure_count * 0.02)
            
            total_score = (capacity_score + performance_score + health_bonus + 
                          circuit_bonus - queue_penalty - circuit_failure_penalty)
            
            if total_score > best_score:
                best_score = total_score
                best_node = node_id
        
        return best_node
    
    def _finalize_route(self, node_id: str, message_type: str, strategy: str) -> str:
        """Finalize routing decision and update statistics."""
        self._stats["successful_routes"] += 1
        self._stats["routes_by_node"][node_id] += 1
        
        # Update node connection count
        if node_id in self.nodes:
            self.nodes[node_id].active_connections += 1
        
        # Notify callback
        if self.route_callback:
            try:
                self.route_callback(node_id, message_type, strategy)
            except Exception as e:
                logger.error(f"ENHANCED_LOAD_BALANCER: Error in route callback: {e}")
        
        logger.debug(f"ENHANCED_LOAD_BALANCER: Routed {message_type} to {node_id} using {strategy} "
                    f"(circuit: {self.nodes[node_id].circuit_state.name if node_id in self.nodes else 'UNKNOWN'})")
        return node_id
    
    def route_with_failover(self, message_type: str, workflow_id: Optional[str] = None,
                           exclude_nodes: Optional[Set[str]] = None) -> Optional[str]:
        """
        Route message with automatic failover considering circuit breaker states.
        
        Args:
            message_type: Type of message being routed
            workflow_id: Optional workflow ID for sticky routing
            exclude_nodes: Nodes to exclude from routing
            
        Returns:
            Node ID to route to, or None if all attempts failed
        """
        exclude_nodes = exclude_nodes or set()
        
        for attempt in range(self.failover_attempts):
            # Temporarily exclude failed nodes and nodes with open circuits
            original_health = {}
            original_circuit_state = {}
            
            for node_id in exclude_nodes:
                if node_id in self.nodes:
                    original_health[node_id] = self.nodes[node_id].health
                    original_circuit_state[node_id] = self.nodes[node_id].circuit_state
                    self.nodes[node_id].health = NodeHealth.UNAVAILABLE
                    self.nodes[node_id].circuit_state = CircuitState.OPEN
            
            try:
                # Attempt routing
                selected_node = self.route_message(message_type, workflow_id)
                
                if selected_node and selected_node not in exclude_nodes:
                    if attempt > 0:
                        self._stats["failover_routes"] += 1
                        logger.info(f"ENHANCED_LOAD_BALANCER: Successful failover to {selected_node} "
                                   f"on attempt {attempt + 1}")
                    return selected_node
                else:
                    # Add failed node to exclusion list
                    if selected_node:
                        exclude_nodes.add(selected_node)
                        if selected_node in self.nodes:
                            self.nodes[selected_node].consecutive_failures += 1
            
            finally:
                # Restore original health and circuit states
                for node_id, health in original_health.items():
                    if node_id in self.nodes:
                        self.nodes[node_id].health = health
                
                for node_id, circuit_state in original_circuit_state.items():
                    if node_id in self.nodes:
                        self.nodes[node_id].circuit_state = circuit_state
        
        logger.error(f"ENHANCED_LOAD_BALANCER: All failover attempts failed for message type {message_type}")
        return None
    
    async def _send_circuit_probe(self, target_node: str) -> bool:
        """
        Send probe message to test circuit breaker recovery.
        
        Args:
            target_node: Target node to probe
            
        Returns:
            True if probe successful, False otherwise
        """
        try:
            # Use health checker if available
            if self.health_checker:
                is_healthy = self.health_checker(target_node)
                logger.debug(f"ENHANCED_LOAD_BALANCER: Circuit probe to {target_node}: {'SUCCESS' if is_healthy else 'FAILED'}")
                return is_healthy
            else:
                # Default probe behavior - assume success for now
                logger.debug(f"ENHANCED_LOAD_BALANCER: Circuit probe to {target_node}: SUCCESS (default)")
                return True
                
        except Exception as e:
            logger.error(f"ENHANCED_LOAD_BALANCER: Circuit probe to {target_node} failed: {e}")
            return False
    
    def release_connection(self, node_id: str):
        """
        Release a connection from a node.
        
        Args:
            node_id: Node identifier
        """
        if node_id in self.nodes:
            self.nodes[node_id].active_connections = max(
                0, self.nodes[node_id].active_connections - 1
            )
    
    def create_sticky_session(self, workflow_id: str, node_id: str):
        """
        Create a sticky session for workflow consistency.
        
        Args:
            workflow_id: Workflow identifier
            node_id: Node to stick to
        """
        # Verify node has healthy circuit before creating sticky session
        if node_id in self.nodes and self.nodes[node_id].is_circuit_healthy():
            self.sticky_sessions[workflow_id] = node_id
            logger.debug(f"ENHANCED_LOAD_BALANCER: Created sticky session {workflow_id} -> {node_id}")
        else:
            logger.warning(f"ENHANCED_LOAD_BALANCER: Cannot create sticky session to {node_id} "
                          f"due to unhealthy circuit state")
    
    def remove_sticky_session(self, workflow_id: str):
        """
        Remove a sticky session.
        
        Args:
            workflow_id: Workflow identifier
        """
        if workflow_id in self.sticky_sessions:
            del self.sticky_sessions[workflow_id]
            logger.debug(f"ENHANCED_LOAD_BALANCER: Removed sticky session {workflow_id}")
    
    async def _health_check_loop(self):
        """Background task for health checking nodes with circuit breaker integration."""
        while self._running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"ENHANCED_LOAD_BALANCER: Error in health check loop: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all nodes with circuit breaker state sync."""
        for node_id in list(self.nodes.keys()):
            try:
                # Update metrics from capacity provider
                if self.capacity_provider:
                    metrics = self.capacity_provider(node_id)
                    if metrics:
                        self.update_node_metrics(node_id, metrics)
                
                # Check node health
                if self.health_checker:
                    is_healthy = self.health_checker(node_id)
                    node_metrics = self.nodes[node_id]
                    
                    if is_healthy:
                        node_metrics.consecutive_failures = 0
                        if node_metrics.health == NodeHealth.UNAVAILABLE:
                            node_metrics.health = NodeHealth.HEALTHY
                            logger.info(f"ENHANCED_LOAD_BALANCER: Node {node_id} recovered")
                    else:
                        node_metrics.consecutive_failures += 1
                        if node_metrics.consecutive_failures >= 3:
                            node_metrics.health = NodeHealth.UNAVAILABLE
                            logger.warning(f"ENHANCED_LOAD_BALANCER: Node {node_id} marked unavailable "
                                         f"after {node_metrics.consecutive_failures} failures")
                
            except Exception as e:
                logger.error(f"ENHANCED_LOAD_BALANCER: Error checking health of node {node_id}: {e}")
    
    def get_node_statistics(self) -> Dict[str, Any]:
        """Get statistics for all nodes including circuit breaker states."""
        node_stats = {}
        
        for node_id, metrics in self.nodes.items():
            node_stats[node_id] = {
                "health": metrics.health.name,
                "capacity_score": metrics.get_capacity_score(),
                "performance_score": metrics.get_performance_score(),
                "routing_weight": metrics.get_routing_weight(),
                "active_connections": metrics.active_connections,
                "queue_depth": metrics.queue_depth,
                "avg_latency": metrics.avg_latency,
                "success_rate": metrics.success_rate,
                "consecutive_failures": metrics.consecutive_failures,
                "last_updated": metrics.last_updated,
                
                # Circuit breaker specific stats
                "circuit_state": metrics.circuit_state.name,
                "circuit_failure_count": metrics.circuit_failure_count,
                "circuit_recovery_attempts": metrics.circuit_recovery_attempts,
                "last_circuit_state_change": metrics.last_circuit_state_change,
                "is_circuit_healthy": metrics.is_circuit_healthy()
            }
        
        return node_stats
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics including circuit breaker metrics."""
        total_routes = self._stats["total_routes"]
        success_rate = (self._stats["successful_routes"] / max(total_routes, 1)) * 100
        
        # Circuit breaker specific metrics
        circuit_stats = self.circuit_manager.get_all_circuit_status()
        
        return {
            "node_id": self.node_id,
            "default_strategy": self.default_strategy.name,
            "total_nodes": len(self.nodes),
            "available_nodes": len([n for n in self.nodes.values() if n.is_available()]),
            "healthy_circuits": len([n for n in self.nodes.values() if n.is_circuit_healthy()]),
            "sticky_sessions": len(self.sticky_sessions),
            "routing_rules": len(self.routing_rules),
            "success_rate": success_rate,
            "statistics": self._stats.copy(),
            "node_distribution": dict(self._stats["routes_by_node"]),
            "strategy_distribution": dict(self._stats["routes_by_strategy"]),
            "circuit_breaker_stats": circuit_stats
        }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get recommendations for optimizing load balancing with circuit breaker insights."""
        recommendations = []
        
        # Check for uneven distribution
        if self._stats["routes_by_node"]:
            route_counts = list(self._stats["routes_by_node"].values())
            if route_counts:
                max_routes = max(route_counts)
                min_routes = min(route_counts)
                if max_routes > min_routes * 3:  # 3x imbalance
                    recommendations.append("Uneven load distribution detected - "
                                         "consider adjusting node weights or capacity")
        
        # Check for unhealthy nodes
        unhealthy_nodes = [n for n in self.nodes.values() 
                          if n.health in [NodeHealth.DEGRADED, NodeHealth.OVERLOADED, NodeHealth.CIRCUIT_OPEN]]
        if unhealthy_nodes:
            recommendations.append(f"{len(unhealthy_nodes)} nodes are unhealthy - "
                                 f"investigate capacity or performance issues")
        
        # Check circuit breaker states
        open_circuits = [n for n in self.nodes.values() if n.circuit_state == CircuitState.OPEN]
        if open_circuits:
            recommendations.append(f"{len(open_circuits)} nodes have open circuit breakers - "
                                 f"investigate node connectivity and reliability")
        
        # Check success rate
        total_routes = self._stats["total_routes"]
        if total_routes > 0:
            success_rate = self._stats["successful_routes"] / total_routes
            if success_rate < 0.95:  # Less than 95% success
                recommendations.append(f"Low routing success rate ({success_rate:.1%}) - "
                                     f"check node availability and circuit breaker health")
        
        # Check for excessive circuit breaker blocks
        if self._stats["circuit_blocked_routes"] > total_routes * 0.05:  # More than 5% blocked
            recommendations.append("High circuit breaker block rate detected - "
                                 "investigate node reliability and circuit breaker configuration")
        
        # Check for excessive failovers
        if self._stats["failover_routes"] > total_routes * 0.1:  # More than 10% failovers
            recommendations.append("High failover rate detected - "
                                 "investigate node stability and capacity planning")
        
        if not recommendations:
            recommendations.append("Load balancing with circuit breaker protection operating optimally - "
                                 "no issues detected")
        
        return recommendations
