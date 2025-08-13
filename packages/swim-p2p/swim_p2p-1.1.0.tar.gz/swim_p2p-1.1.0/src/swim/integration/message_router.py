"""
Message routing with failure awareness for SWIM P2P.

This module provides intelligent message routing that adapts to network
conditions, member failures, and load balancing requirements.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import random

from swim.protocol.member import Member, MemberState
from swim.events.dispatcher import EventDispatcher
from swim.events.types import EventType, MembershipEvent
from swim.integration.messaging.circuit_breaker import CircuitBreaker
from swim.integration.load_balancer import LoadBalancer


class RoutingStrategy(Enum):
    """Message routing strategies."""
    DIRECT = "direct"
    LOAD_BALANCED = "load_balanced"
    REDUNDANT = "redundant"
    ADAPTIVE = "adaptive"
    CIRCUIT_AWARE = "circuit_aware"  # NEW: Circuit breaker aware routing


@dataclass
class RouteMetrics:
    """Metrics for a specific route."""
    success_count: int = 0
    failure_count: int = 0
    average_latency: float = 0.0
    last_success: float = 0.0
    last_failure: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 1.0
    
    @property
    def is_healthy(self) -> bool:
        """Check if route is healthy."""
        return self.success_rate > 0.8 and (time.time() - self.last_failure) > 30.0


@dataclass
class NodeInfo:
    """Information about a network node."""
    node_id: str
    address: Tuple[str, int]
    state: MemberState
    capabilities: Set[str]
    load_factor: float = 0.0
    last_seen: float = 0.0


class MessageRouter:
    """
    Intelligent message router with failure awareness and hello message support.
    
    This router adapts to network conditions, handles member failures,
    and provides load balancing and redundancy features. It works at a higher
    level than the ZMQ RouterManager, making routing decisions based on
    application-level concerns.
    """
    
    def __init__(
        self,
        local_node_id: str,
        event_dispatcher: EventDispatcher,
        load_balancer: LoadBalancer,
        circuit_breaker: CircuitBreaker,
        default_strategy: RoutingStrategy = RoutingStrategy.ADAPTIVE
    ):
        self.local_node_id = local_node_id
        self.event_dispatcher = event_dispatcher
        self.load_balancer = load_balancer
        self.circuit_breaker = circuit_breaker
        self.default_strategy = default_strategy
        
        self._nodes: Dict[str, NodeInfo] = {}
        self._route_metrics: Dict[str, RouteMetrics] = {}
        self._failed_nodes: Set[str] = set()
        self._logger = logging.getLogger("swim.message_router")
        
        # Routing configuration
        self.max_retries = 3
        self.retry_delay = 1.0
        self.health_check_interval = 30.0
        self.route_timeout = 10.0
        
        # Hello message routing configuration
        self.hello_message_timeout = 5.0
        self.hello_broadcast_strategy = RoutingStrategy.CIRCUIT_AWARE
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Start background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        
        self._logger.info(f"MESSAGE_ROUTER: Initialized for node {local_node_id}")
    
    def _setup_event_handlers(self) -> None:
        """Set up event handlers for membership changes."""
        self.event_dispatcher.subscribe(
            EventType.MEMBER_JOIN,
            self._handle_member_join
        )
        self.event_dispatcher.subscribe(
            EventType.MEMBER_LEAVE,
            self._handle_member_leave
        )
        self.event_dispatcher.subscribe(
            EventType.MEMBER_FAILED,
            self._handle_member_failed
        )
        self.event_dispatcher.subscribe(
            EventType.MEMBER_UPDATE,
            self._handle_member_update
        )
    
    async def start(self) -> None:
        """Start the message router."""
        self._logger.info("MESSAGE_ROUTER: Starting message router")
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def stop(self) -> None:
        """Stop the message router."""
        self._logger.info("MESSAGE_ROUTER: Stopping message router")
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
    
    async def add_node(self, node_id: str, address: Tuple[str, int], capabilities: Optional[Set[str]] = None) -> None:
        """Add a node to the routing table."""
        self._nodes[node_id] = NodeInfo(
            node_id=node_id,
            address=address,
            state=MemberState.ALIVE,
            capabilities=capabilities or set(),
            last_seen=time.time()
        )
        
        if node_id not in self._route_metrics:
            self._route_metrics[node_id] = RouteMetrics()
        
        self._failed_nodes.discard(node_id)
        self._logger.debug(f"MESSAGE_ROUTER: Added node to routing table: {node_id}")
    
    async def remove_node(self, node_id: str) -> None:
        """Remove a node from the routing table."""
        self._nodes.pop(node_id, None)
        self._failed_nodes.discard(node_id)
        self._logger.debug(f"MESSAGE_ROUTER: Removed node from routing table: {node_id}")
    
    async def mark_node_failed(self, node_id: str) -> None:
        """Mark a node as failed."""
        if node_id in self._nodes:
            self._nodes[node_id].state = MemberState.FAILED
        
        self._failed_nodes.add(node_id)
        
        # Update route metrics
        if node_id in self._route_metrics:
            self._route_metrics[node_id].last_failure = time.time()
        
        self._logger.warning(f"MESSAGE_ROUTER: Marked node as failed: {node_id}")
    
    async def route_hello_message(
        self,
        target_node: Optional[str] = None,
        message_content: str = "Hello from message router",
        strategy: Optional[RoutingStrategy] = None
    ) -> Any:
        """
        Route a hello message with specialized hello message handling.
        
        Args:
            target_node: Specific target node (None for broadcast)
            message_content: Hello message content
            strategy: Routing strategy to use
            
        Returns:
            Response from the target node or dict of responses for broadcast
        """
        strategy = strategy or self.hello_broadcast_strategy
        
        hello_payload = {
            "type": "HELLO",
            "content": message_content,
            "timestamp": time.time(),
            "from": self.local_node_id
        }
        
        # Use specialized hello message capabilities
        required_capabilities = {"hello_messages"}
        
        if target_node:
            # Direct hello message
            return await self._route_to_specific_node(
                target_node, 
                "HELLO", 
                hello_payload,
                timeout=self.hello_message_timeout
            )
        else:
            # Broadcast hello message
            return await self._broadcast_hello_message(hello_payload, strategy)
    
    async def _broadcast_hello_message(
        self,
        hello_payload: Dict[str, Any],
        strategy: RoutingStrategy
    ) -> Dict[str, Any]:
        """
        Broadcast hello message to multiple nodes.
        
        Args:
            hello_payload: Hello message payload
            strategy: Routing strategy for broadcast
            
        Returns:
            Dictionary mapping node IDs to their responses
        """
        # Select candidates for hello message broadcast
        candidates = await self._select_candidates({"hello_messages"})
        
        if not candidates:
            self._logger.warning("MESSAGE_ROUTER: No nodes available for hello broadcast")
            return {}
        
        self._logger.info(f"MESSAGE_ROUTER: Broadcasting hello to {len(candidates)} nodes")
        
        if strategy == RoutingStrategy.CIRCUIT_AWARE:
            # Filter out nodes with open circuit breakers
            healthy_candidates = []
            for node_id in candidates:
                if await self.circuit_breaker.can_execute(node_id):
                    healthy_candidates.append(node_id)
            candidates = healthy_candidates
        
        # Send hello messages concurrently
        tasks = []
        for node_id in candidates:
            task = asyncio.create_task(
                self._route_to_specific_node(
                    node_id, 
                    "HELLO", 
                    hello_payload,
                    timeout=self.hello_message_timeout
                )
            )
            tasks.append((node_id, task))
        
        # Collect responses
        responses = {}
        for node_id, task in tasks:
            try:
                response = await task
                responses[node_id] = response
            except Exception as e:
                self._logger.warning(f"MESSAGE_ROUTER: Failed to send hello to {node_id}: {e}")
                responses[node_id] = None
        
        success_count = sum(1 for response in responses.values() if response is not None)
        self._logger.info(f"MESSAGE_ROUTER: Hello broadcast completed: {success_count}/{len(responses)} successful")
        
        return responses
    
    async def route_message(
        self,
        target_node: Optional[str],
        message_type: str,
        payload: Dict[str, Any],
        strategy: Optional[RoutingStrategy] = None,
        required_capabilities: Optional[Set[str]] = None,
        timeout: Optional[float] = None
    ) -> Any:
        """
        Route a message to the appropriate node(s).
        
        Args:
            target_node: Specific target node (None for automatic selection)
            message_type: Type of message
            payload: Message payload
            strategy: Routing strategy to use
            required_capabilities: Required node capabilities
            timeout: Optional timeout for the operation
            
        Returns:
            Response from the target node
        """
        strategy = strategy or self.default_strategy
        timeout = timeout or self.route_timeout
        
        # Special handling for hello messages
        if message_type == "HELLO":
            return await self.route_hello_message(
                target_node, 
                payload.get("content", "Hello"), 
                strategy
            )
        
        # If specific target is provided, route directly
        if target_node:
            return await self._route_to_specific_node(target_node, message_type, payload, timeout)
        
        # Select target based on strategy
        candidates = await self._select_candidates(required_capabilities)
        if not candidates:
            raise RuntimeError("No available nodes for routing")
        
        if strategy == RoutingStrategy.DIRECT:
            target = candidates[0]
            return await self._route_to_specific_node(target, message_type, payload, timeout)
        
        elif strategy == RoutingStrategy.LOAD_BALANCED:
            target = await self._select_load_balanced_node(candidates)
            return await self._route_to_specific_node(target, message_type, payload, timeout)
        
        elif strategy == RoutingStrategy.REDUNDANT:
            return await self._route_redundant(candidates[:3], message_type, payload, timeout)
        
        elif strategy == RoutingStrategy.ADAPTIVE:
            return await self._route_adaptive(candidates, message_type, payload, timeout)
        
        elif strategy == RoutingStrategy.CIRCUIT_AWARE:
            return await self._route_circuit_aware(candidates, message_type, payload, timeout)
        
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")
    
    async def _route_circuit_aware(
        self,
        candidates: List[str],
        message_type: str,
        payload: Dict[str, Any],
        timeout: float
    ) -> Any:
        """Route message with circuit breaker awareness."""
        # Filter candidates by circuit breaker state
        healthy_candidates = []
        for node_id in candidates:
            if await self.circuit_breaker.can_execute(node_id):
                healthy_candidates.append(node_id)
        
        if not healthy_candidates:
            raise RuntimeError("No healthy nodes available (all circuit breakers open)")
        
        # Use load balancing among healthy nodes
        target = await self._select_load_balanced_node(healthy_candidates)
        return await self._route_to_specific_node(target, message_type, payload, timeout)
    
    async def _route_to_specific_node(
        self,
        node_id: str,
        message_type: str,
        payload: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Any:
        """Route message to a specific node with retries."""
        if node_id in self._failed_nodes:
            raise RuntimeError(f"Node {node_id} is marked as failed")
        
        if node_id not in self._nodes:
            raise RuntimeError(f"Node {node_id} not found in routing table")
        
        # Check circuit breaker
        if not await self.circuit_breaker.can_execute(node_id):
            raise RuntimeError(f"Circuit breaker open for node {node_id}")
        
        timeout = timeout or self.route_timeout
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Simulate message sending (replace with actual transport)
                response = await self._send_message(node_id, message_type, payload, timeout)
                
                # Update metrics on success
                latency = time.time() - start_time
                await self._update_route_metrics(node_id, success=True, latency=latency)
                await self.circuit_breaker.record_success(node_id)
                
                return response
                
            except Exception as e:
                # Update metrics on failure
                await self._update_route_metrics(node_id, success=False)
                await self.circuit_breaker.record_failure(node_id)
                
                if attempt == self.max_retries - 1:
                    self._logger.error(f"MESSAGE_ROUTER: Failed to route to {node_id} after {self.max_retries} attempts: {e}")
                    raise
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        raise RuntimeError(f"Failed to route message to {node_id}")
    
    async def _send_message(self, node_id: str, message_type: str, payload: Dict[str, Any], timeout: float) -> Any:
        """Send message to a node (placeholder for actual transport)."""
        # This would be replaced with actual ZMQ transport or agent interface
        await asyncio.sleep(0.01)  # Simulate network delay
        
        # Simulate occasional failures for testing
        if random.random() < 0.05:  # 5% failure rate
            raise RuntimeError("Simulated network error")
        
        # Special response for hello messages
        if message_type == "HELLO":
            return {
                "type": "HELLO_RESPONSE",
                "content": f"Hello response from {node_id}",
                "original_content": payload.get("content", ""),
                "node_id": node_id,
                "timestamp": time.time()
            }
        
        return {"status": "success", "node_id": node_id, "echo": payload}
    
    async def _select_candidates(self, required_capabilities: Optional[Set[str]] = None) -> List[str]:
        """Select candidate nodes for routing."""
        candidates = []
        
        for node_id, node_info in self._nodes.items():
            # Skip failed nodes
            if node_id in self._failed_nodes:
                continue
            
            # Skip nodes that don't meet capability requirements
            if required_capabilities and not required_capabilities.issubset(node_info.capabilities):
                continue
            
            # Skip nodes with open circuit breakers for non-hello messages
            if not await self.circuit_breaker.can_execute(node_id):
                continue
            
            candidates.append(node_id)
        
        # Sort by health and performance
        candidates.sort(key=lambda node_id: (
            -self._route_metrics.get(node_id, RouteMetrics()).success_rate,
            self._route_metrics.get(node_id, RouteMetrics()).average_latency
        ))
        
        return candidates
    
    async def _select_load_balanced_node(self, candidates: List[str]) -> str:
        """Select node using load balancing."""
        if not candidates:
            raise RuntimeError("No candidates available")
        
        # Use load balancer to select best node
        node_loads = {}
        for node_id in candidates:
            node_info = self._nodes[node_id]
            node_loads[node_id] = node_info.load_factor
        
        selected = await self.load_balancer.select_node(node_loads)
        return selected
    
    async def _route_redundant(
        self,
        candidates: List[str],
        message_type: str,
        payload: Dict[str, Any],
        timeout: float
    ) -> Any:
        """Route message to multiple nodes for redundancy."""
        if not candidates:
            raise RuntimeError("No candidates available")
        
        # Send to multiple nodes concurrently
        tasks = []
        for node_id in candidates:
            task = asyncio.create_task(
                self._route_to_specific_node(node_id, message_type, payload, timeout)
            )
            tasks.append(task)
        
        # Wait for first successful response
        try:
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
                timeout=timeout
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            
            # Return first successful result
            for task in done:
                try:
                    return await task
                except Exception:
                    continue
            
            raise RuntimeError("All redundant routes failed")
            
        except asyncio.TimeoutError:
            # Cancel all tasks
            for task in tasks:
                task.cancel()
            raise RuntimeError("Redundant routing timed out")
    
    async def _route_adaptive(
        self,
        candidates: List[str],
        message_type: str,
        payload: Dict[str, Any],
        timeout: float
    ) -> Any:
        """Adaptive routing based on current conditions."""
        if not candidates:
            raise RuntimeError("No candidates available")
        
        # Choose strategy based on network conditions
        healthy_nodes = [
            node_id for node_id in candidates
            if self._route_metrics.get(node_id, RouteMetrics()).is_healthy
        ]
        
        if len(healthy_nodes) >= 3:
            # Network is healthy, use load balancing
            target = await self._select_load_balanced_node(healthy_nodes)
            return await self._route_to_specific_node(target, message_type, payload, timeout)
        
        elif len(healthy_nodes) >= 1:
            # Some healthy nodes, use redundancy
            return await self._route_redundant(healthy_nodes[:2], message_type, payload, timeout)
        
        else:
            # Network is degraded, try best available
            target = candidates[0]
            return await self._route_to_specific_node(target, message_type, payload, timeout)
    
    async def _update_route_metrics(
        self,
        node_id: str,
        success: bool,
        latency: Optional[float] = None
    ) -> None:
        """Update routing metrics for a node."""
        if node_id not in self._route_metrics:
            self._route_metrics[node_id] = RouteMetrics()
        
        metrics = self._route_metrics[node_id]
        
        if success:
            metrics.success_count += 1
            metrics.last_success = time.time()
            
            if latency is not None:
                # Update average latency
                total_ops = metrics.success_count + metrics.failure_count
                metrics.average_latency = (
                    (metrics.average_latency * (total_ops - 1) + latency) / total_ops
                )
        else:
            metrics.failure_count += 1
            metrics.last_failure = time.time()
    
    async def _health_check_loop(self) -> None:
        """Background task for health checking."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"MESSAGE_ROUTER: Error in health check loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all nodes."""
        current_time = time.time()
        
        for node_id, node_info in list(self._nodes.items()):
            # Check if node has been seen recently
            if current_time - node_info.last_seen > 60.0:  # 1 minute timeout
                self._logger.warning(f"MESSAGE_ROUTER: Node {node_id} not seen recently, marking as suspect")
                node_info.state = MemberState.SUSPECT
            
            # Update load factors (placeholder)
            node_info.load_factor = random.uniform(0.1, 0.9)
    
    async def get_available_nodes(self) -> List[str]:
        """Get list of available nodes."""
        return [
            node_id for node_id, node_info in self._nodes.items()
            if node_id not in self._failed_nodes and node_info.state == MemberState.ALIVE
        ]
    
    async def get_hello_capable_nodes(self) -> List[str]:
        """Get list of nodes that support hello messages."""
        return [
            node_id for node_id, node_info in self._nodes.items()
            if (node_id not in self._failed_nodes and 
                node_info.state == MemberState.ALIVE and
                "hello_messages" in node_info.capabilities)
        ]
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        total_nodes = len(self._nodes)
        healthy_nodes = len([
            node_id for node_id in self._nodes
            if self._route_metrics.get(node_id, RouteMetrics()).is_healthy
        ])
        failed_nodes = len(self._failed_nodes)
        hello_capable_nodes = len([
            node_id for node_id, node_info in self._nodes.items()
            if "hello_messages" in node_info.capabilities
        ])
        
        return {
            "total_nodes": total_nodes,
            "healthy_nodes": healthy_nodes,
            "failed_nodes": failed_nodes,
            "hello_capable_nodes": hello_capable_nodes,
            "default_strategy": self.default_strategy.value,
            "hello_broadcast_strategy": self.hello_broadcast_strategy.value,
            "route_metrics": {
                node_id: {
                    "success_rate": metrics.success_rate,
                    "average_latency": metrics.average_latency,
                    "is_healthy": metrics.is_healthy
                }
                for node_id, metrics in self._route_metrics.items()
            }
        }
    
    # Event handlers
    async def _handle_member_join(self, event: MembershipEvent) -> None:
        """Handle member join events."""
        capabilities = getattr(event.member, 'capabilities', set())
        await self.add_node(event.member.node_id, event.member.address, capabilities)
    
    async def _handle_member_leave(self, event: MembershipEvent) -> None:
        """Handle member leave events."""
        await self.remove_node(event.member.node_id)
    
    async def _handle_member_failed(self, event: MembershipEvent) -> None:
        """Handle member failure events."""
        await self.mark_node_failed(event.member.node_id)
    
    async def _handle_member_update(self, event: MembershipEvent) -> None:
        """Handle member update events."""
        if event.member.node_id in self._nodes:
            self._nodes[event.member.node_id].last_seen = time.time()
            self._nodes[event.member.node_id].state = event.member.state
