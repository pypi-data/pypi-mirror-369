"""
Credit-based flow control system for SWIM-ZMQ integration.

Implements a credit-based flow control mechanism to prevent overwhelming
nodes and ensure fair resource allocation across the P2P network.
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Callable, Any, Set, List
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque
import uuid

logger = logging.getLogger(__name__)


class FlowState(Enum):
    """Flow control states."""
    NORMAL = auto()         # Normal flow, credits available
    THROTTLED = auto()      # Throttled due to low credits
    BLOCKED = auto()        # Blocked due to no credits
    SUSPENDED = auto()      # Suspended due to node issues


class CreditType(Enum):
    """Types of credits for different message categories."""
    HIGH_PRIORITY = auto()      # Critical system messages
    NORMAL_PRIORITY = auto()    # Regular application messages
    LOW_PRIORITY = auto()       # Background/maintenance messages
    BULK_TRANSFER = auto()      # Large data transfers


@dataclass
class CreditPool:
    """Credit pool for a specific message type."""
    credit_type: CreditType
    max_credits: int = 100
    current_credits: int = 100
    reserved_credits: int = 0
    credit_rate: float = 10.0  # Credits per second
    last_refill: float = field(default_factory=time.time)
    
    # Statistics
    total_granted: int = 0
    total_returned: int = 0
    total_expired: int = 0
    
    def can_grant(self, amount: int) -> bool:
        """Check if credits can be granted."""
        return self.current_credits >= amount
    
    def grant_credits(self, amount: int) -> bool:
        """Grant credits if available."""
        if self.can_grant(amount):
            self.current_credits -= amount
            self.reserved_credits += amount
            self.total_granted += amount
            return True
        return False
    
    def return_credits(self, amount: int):
        """Return unused credits."""
        returned = min(amount, self.reserved_credits)
        self.current_credits += returned
        self.reserved_credits -= returned
        self.total_returned += returned
    
    def consume_credits(self, amount: int):
        """Consume credits (message sent successfully)."""
        consumed = min(amount, self.reserved_credits)
        self.reserved_credits -= consumed
        # Credits are consumed, not returned to pool
    
    def refill_credits(self):
        """Refill credits based on rate."""
        current_time = time.time()
        time_elapsed = current_time - self.last_refill
        
        if time_elapsed > 0:
            credits_to_add = int(self.credit_rate * time_elapsed)
            if credits_to_add > 0:
                self.current_credits = min(
                    self.max_credits,
                    self.current_credits + credits_to_add
                )
                self.last_refill = current_time
    
    def get_utilization(self) -> float:
        """Get credit utilization (0.0 = empty, 1.0 = full)."""
        return self.current_credits / max(self.max_credits, 1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get credit pool status."""
        return {
            "credit_type": self.credit_type.name,
            "max_credits": self.max_credits,
            "current_credits": self.current_credits,
            "reserved_credits": self.reserved_credits,
            "utilization": self.get_utilization(),
            "credit_rate": self.credit_rate,
            "statistics": {
                "total_granted": self.total_granted,
                "total_returned": self.total_returned,
                "total_expired": self.total_expired
            }
        }


@dataclass
class FlowControlTicket:
    """Ticket representing granted flow control credits."""
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str = ""
    credit_type: CreditType = CreditType.NORMAL_PRIORITY
    credits_granted: int = 0
    granted_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 30.0)
    consumed: bool = False
    
    def is_expired(self) -> bool:
        """Check if ticket has expired."""
        return time.time() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if ticket is valid for use."""
        return not self.consumed and not self.is_expired()


class NodeFlowControl:
    """Flow control state for a specific node."""
    
    def __init__(self, node_id: str):
        """
        Initialize node flow control.
        
        Args:
            node_id: Node identifier
        """
        self.node_id = node_id
        self.state = FlowState.NORMAL
        
        # Credit pools for different message types
        self.credit_pools: Dict[CreditType, CreditPool] = {
            CreditType.HIGH_PRIORITY: CreditPool(CreditType.HIGH_PRIORITY, 50, 50, 0, 20.0),
            CreditType.NORMAL_PRIORITY: CreditPool(CreditType.NORMAL_PRIORITY, 100, 100, 0, 10.0),
            CreditType.LOW_PRIORITY: CreditPool(CreditType.LOW_PRIORITY, 200, 200, 0, 5.0),
            CreditType.BULK_TRANSFER: CreditPool(CreditType.BULK_TRANSFER, 20, 20, 0, 2.0)
        }
        
        # Active tickets
        self.active_tickets: Dict[str, FlowControlTicket] = {}
        
        # Flow control metrics
        self.last_updated = time.time()
        self.total_requests = 0
        self.granted_requests = 0
        self.blocked_requests = 0
        self.throttled_requests = 0
        
        # Adaptive parameters
        self.congestion_factor = 1.0  # 1.0 = normal, >1.0 = congested
        self.node_health_factor = 1.0  # 1.0 = healthy, <1.0 = degraded
    
    def request_credits(self, credit_type: CreditType, amount: int = 1) -> Optional[FlowControlTicket]:
        """
        Request credits for message sending.
        
        Args:
            credit_type: Type of credits requested
            amount: Number of credits requested
            
        Returns:
            FlowControlTicket if granted, None if denied
        """
        self.total_requests += 1
        
        # Check flow state
        if self.state == FlowState.BLOCKED:
            self.blocked_requests += 1
            return None
        
        # Refill credits first
        self.credit_pools[credit_type].refill_credits()
        
        # Apply adaptive factors
        effective_amount = int(amount * self.congestion_factor / self.node_health_factor)
        
        # Check if credits are available
        if not self.credit_pools[credit_type].can_grant(effective_amount):
            if self.state == FlowState.NORMAL:
                self.state = FlowState.THROTTLED
                logger.info(f"FLOW_CONTROL: Node {self.node_id} throttled for {credit_type.name}")
            
            self.throttled_requests += 1
            return None
        
        # Grant credits
        if self.credit_pools[credit_type].grant_credits(effective_amount):
            ticket = FlowControlTicket(
                node_id=self.node_id,
                credit_type=credit_type,
                credits_granted=effective_amount
            )
            
            self.active_tickets[ticket.ticket_id] = ticket
            self.granted_requests += 1
            
            # Update state
            if self.state == FlowState.THROTTLED:
                self.state = FlowState.NORMAL
                logger.info(f"FLOW_CONTROL: Node {self.node_id} flow restored")
            
            self.last_updated = time.time()
            return ticket
        
        return None
    
    def consume_ticket(self, ticket_id: str) -> bool:
        """
        Consume a ticket (message sent successfully).
        
        Args:
            ticket_id: Ticket identifier
            
        Returns:
            True if ticket was consumed, False otherwise
        """
        if ticket_id not in self.active_tickets:
            return False
        
        ticket = self.active_tickets[ticket_id]
        
        if not ticket.is_valid():
            self._cleanup_ticket(ticket_id)
            return False
        
        # Consume credits
        self.credit_pools[ticket.credit_type].consume_credits(ticket.credits_granted)
        ticket.consumed = True
        
        # Remove ticket
        del self.active_tickets[ticket_id]
        
        logger.debug(f"FLOW_CONTROL: Consumed ticket {ticket_id} for {self.node_id}")
        return True
    
    def return_ticket(self, ticket_id: str) -> bool:
        """
        Return an unused ticket.
        
        Args:
            ticket_id: Ticket identifier
            
        Returns:
            True if ticket was returned, False otherwise
        """
        if ticket_id not in self.active_tickets:
            return False
        
        ticket = self.active_tickets[ticket_id]
        
        # Return credits to pool
        self.credit_pools[ticket.credit_type].return_credits(ticket.credits_granted)
        
        # Remove ticket
        del self.active_tickets[ticket_id]
        
        logger.debug(f"FLOW_CONTROL: Returned ticket {ticket_id} for {self.node_id}")
        return True
    
    def update_congestion_factor(self, factor: float):
        """Update congestion factor (affects credit requirements)."""
        self.congestion_factor = max(0.1, min(10.0, factor))
        logger.debug(f"FLOW_CONTROL: Updated congestion factor for {self.node_id}: {factor:.2f}")
    
    def update_health_factor(self, factor: float):
        """Update node health factor (affects credit availability)."""
        self.node_health_factor = max(0.1, min(2.0, factor))
        logger.debug(f"FLOW_CONTROL: Updated health factor for {self.node_id}: {factor:.2f}")
    
    def _cleanup_ticket(self, ticket_id: str):
        """Clean up expired or invalid ticket."""
        if ticket_id in self.active_tickets:
            ticket = self.active_tickets[ticket_id]
            
            # Return credits if not consumed
            if not ticket.consumed:
                self.credit_pools[ticket.credit_type].return_credits(ticket.credits_granted)
            
            del self.active_tickets[ticket_id]
    
    def cleanup_expired_tickets(self):
        """Clean up all expired tickets."""
        expired_tickets = [
            ticket_id for ticket_id, ticket in self.active_tickets.items()
            if ticket.is_expired()
        ]
        
        for ticket_id in expired_tickets:
            self._cleanup_ticket(ticket_id)
            self.credit_pools[self.active_tickets[ticket_id].credit_type].total_expired += 1
        
        if expired_tickets:
            logger.debug(f"FLOW_CONTROL: Cleaned up {len(expired_tickets)} expired tickets for {self.node_id}")
    
    def get_flow_status(self) -> Dict[str, Any]:
        """Get comprehensive flow control status."""
        return {
            "node_id": self.node_id,
            "state": self.state.name,
            "congestion_factor": self.congestion_factor,
            "health_factor": self.node_health_factor,
            "active_tickets": len(self.active_tickets),
            "last_updated": self.last_updated,
            "credit_pools": {
                credit_type.name: pool.get_status()
                for credit_type, pool in self.credit_pools.items()
            },
            "statistics": {
                "total_requests": self.total_requests,
                "granted_requests": self.granted_requests,
                "blocked_requests": self.blocked_requests,
                "throttled_requests": self.throttled_requests,
                "success_rate": self.granted_requests / max(self.total_requests, 1)
            }
        }


class FlowControlManager:
    """
    Credit-based flow control system for SWIM-ZMQ integration.
    
    Manages flow control across multiple nodes, preventing overwhelming
    and ensuring fair resource allocation.
    """
    
    def __init__(self, node_id: str):
        """
        Initialize flow control manager.
        
        Args:
            node_id: Identifier for this node
        """
        self.node_id = node_id
        self.node_flows: Dict[str, NodeFlowControl] = {}
        
        # Configuration
        self.cleanup_interval = 30.0  # seconds
        self.monitoring_interval = 10.0  # seconds
        self.default_ticket_timeout = 30.0  # seconds
        
        # Global flow control
        self.global_flow_enabled = True
        self.emergency_brake = False  # Emergency stop all flow
        
        # Callbacks
        self.flow_state_callback: Optional[Callable] = None
        self.congestion_callback: Optional[Callable] = None
        self.capacity_provider: Optional[Callable] = None
        
        # Background tasks
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.global_stats = {
            "total_nodes": 0,
            "total_requests": 0,
            "total_granted": 0,
            "total_blocked": 0,
            "emergency_brakes": 0
        }
        
        logger.info(f"FLOW_CONTROL_MANAGER: Initialized for node {node_id}")
    
    def set_flow_state_callback(self, callback: Callable[[str, FlowState, FlowState], None]):
        """Set callback for flow state changes."""
        self.flow_state_callback = callback
    
    def set_congestion_callback(self, callback: Callable[[str, float], None]):
        """Set callback for congestion updates."""
        self.congestion_callback = callback
    
    def set_capacity_provider(self, provider: Callable[[str], Optional[Dict[str, Any]]]):
        """Set callback to get node capacity information."""
        self.capacity_provider = provider
    
    async def start(self):
        """Start flow control manager."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("FLOW_CONTROL_MANAGER: Started")
    
    async def stop(self):
        """Stop flow control manager."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("FLOW_CONTROL_MANAGER: Stopped")
    
    def register_node(self, node_id: str):
        """
        Register a node for flow control.
        
        Args:
            node_id: Node identifier
        """
        if node_id not in self.node_flows:
            self.node_flows[node_id] = NodeFlowControl(node_id)
            self.global_stats["total_nodes"] += 1
            logger.info(f"FLOW_CONTROL: Registered node {node_id}")
    
    def unregister_node(self, node_id: str):
        """
        Unregister a node from flow control.
        
        Args:
            node_id: Node identifier
        """
        if node_id in self.node_flows:
            # Clean up any active tickets
            node_flow = self.node_flows[node_id]
            for ticket_id in list(node_flow.active_tickets.keys()):
                node_flow.return_ticket(ticket_id)
            
            del self.node_flows[node_id]
            self.global_stats["total_nodes"] -= 1
            logger.info(f"FLOW_CONTROL: Unregistered node {node_id}")
    
    async def request_flow_control(self, target_node: str, message_type: str = "normal",
                                 priority: str = "normal") -> Optional[FlowControlTicket]:
        """
        Request flow control permission to send message.
        
        Args:
            target_node: Target node identifier
            message_type: Type of message
            priority: Message priority (high, normal, low, bulk)
            
        Returns:
            FlowControlTicket if granted, None if denied
        """
        # Check emergency brake
        if self.emergency_brake:
            self.global_stats["total_blocked"] += 1
            return None
        
        # Check global flow control
        if not self.global_flow_enabled:
            self.global_stats["total_blocked"] += 1
            return None
        
        # Register node if not exists
        if target_node not in self.node_flows:
            self.register_node(target_node)
        
        # Map priority to credit type
        credit_type_map = {
            "high": CreditType.HIGH_PRIORITY,
            "normal": CreditType.NORMAL_PRIORITY,
            "low": CreditType.LOW_PRIORITY,
            "bulk": CreditType.BULK_TRANSFER
        }
        credit_type = credit_type_map.get(priority, CreditType.NORMAL_PRIORITY)
        
        # Request credits
        node_flow = self.node_flows[target_node]
        old_state = node_flow.state
        
        self.global_stats["total_requests"] += 1
        ticket = node_flow.request_credits(credit_type)
        
        if ticket:
            self.global_stats["total_granted"] += 1
            logger.debug(f"FLOW_CONTROL: Granted ticket {ticket.ticket_id} for {target_node}")
        else:
            self.global_stats["total_blocked"] += 1
            logger.debug(f"FLOW_CONTROL: Blocked request for {target_node} ({priority})")
        
        # Check for state changes
        new_state = node_flow.state
        if old_state != new_state and self.flow_state_callback:
            try:
                self.flow_state_callback(target_node, old_state, new_state)
            except Exception as e:
                logger.error(f"FLOW_CONTROL: Error in flow state callback: {e}")
        
        return ticket
    
    async def consume_flow_ticket(self, ticket: FlowControlTicket) -> bool:
        """
        Consume a flow control ticket (message sent successfully).
        
        Args:
            ticket: Flow control ticket
            
        Returns:
            True if consumed successfully, False otherwise
        """
        if ticket.node_id not in self.node_flows:
            return False
        
        return self.node_flows[ticket.node_id].consume_ticket(ticket.ticket_id)
    
    async def return_flow_ticket(self, ticket: FlowControlTicket) -> bool:
        """
        Return an unused flow control ticket.
        
        Args:
            ticket: Flow control ticket
            
        Returns:
            True if returned successfully, False otherwise
        """
        if ticket.node_id not in self.node_flows:
            return False
        
        return self.node_flows[ticket.node_id].return_ticket(ticket.ticket_id)
    
    def update_node_congestion(self, node_id: str, congestion_level: float):
        """
        Update congestion level for a node.
        
        Args:
            node_id: Node identifier
            congestion_level: Congestion level (1.0 = normal, >1.0 = congested)
        """
        if node_id in self.node_flows:
            self.node_flows[node_id].update_congestion_factor(congestion_level)
            
            if self.congestion_callback:
                try:
                    self.congestion_callback(node_id, congestion_level)
                except Exception as e:
                    logger.error(f"FLOW_CONTROL: Error in congestion callback: {e}")
    
    def update_node_health(self, node_id: str, health_factor: float):
        """
        Update health factor for a node.
        
        Args:
            node_id: Node identifier
            health_factor: Health factor (1.0 = healthy, <1.0 = degraded)
        """
        if node_id in self.node_flows:
            self.node_flows[node_id].update_health_factor(health_factor)
    
    def set_emergency_brake(self, enabled: bool):
        """
        Set emergency brake to stop all flow.
        
        Args:
            enabled: Whether to enable emergency brake
        """
        if enabled != self.emergency_brake:
            self.emergency_brake = enabled
            if enabled:
                self.global_stats["emergency_brakes"] += 1
                logger.warning("FLOW_CONTROL: Emergency brake ENABLED - all flow stopped")
            else:
                logger.info("FLOW_CONTROL: Emergency brake DISABLED - flow resumed")
    
    def get_node_flow_status(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get flow control status for a specific node.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Flow status dictionary or None if node not found
        """
        if node_id in self.node_flows:
            return self.node_flows[node_id].get_flow_status()
        return None
    
    def get_all_flow_status(self) -> Dict[str, Any]:
        """Get comprehensive flow control status for all nodes."""
        node_status = {}
        for node_id, node_flow in self.node_flows.items():
            node_status[node_id] = node_flow.get_flow_status()
        
        # Calculate aggregate statistics
        total_active_tickets = sum(len(nf.active_tickets) for nf in self.node_flows.values())
        blocked_nodes = sum(1 for nf in self.node_flows.values() if nf.state == FlowState.BLOCKED)
        throttled_nodes = sum(1 for nf in self.node_flows.values() if nf.state == FlowState.THROTTLED)
        
        return {
            "manager_node_id": self.node_id,
            "global_flow_enabled": self.global_flow_enabled,
            "emergency_brake": self.emergency_brake,
            "total_nodes": len(self.node_flows),
            "total_active_tickets": total_active_tickets,
            "blocked_nodes": blocked_nodes,
            "throttled_nodes": throttled_nodes,
            "global_statistics": self.global_stats.copy(),
            "node_flows": node_status
        }
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"FLOW_CONTROL: Error in cleanup loop: {e}")
    
    async def _perform_cleanup(self):
        """Perform cleanup of expired tickets."""
        cleanup_count = 0
        
        for node_flow in self.node_flows.values():
            before_count = len(node_flow.active_tickets)
            node_flow.cleanup_expired_tickets()
            after_count = len(node_flow.active_tickets)
            cleanup_count += (before_count - after_count)
        
        if cleanup_count > 0:
            logger.debug(f"FLOW_CONTROL: Cleaned up {cleanup_count} expired tickets")
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(self.monitoring_interval)
                await self._perform_monitoring()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"FLOW_CONTROL: Error in monitoring loop: {e}")
    
    async def _perform_monitoring(self):
        """Perform monitoring and adaptive adjustments."""
        if not self.capacity_provider:
            return
        
        # Update node health and congestion based on capacity
        for node_id in self.node_flows.keys():
            try:
                capacity_info = self.capacity_provider(node_id)
                if capacity_info:
                    # Update congestion based on queue depth
                    queue_depth = capacity_info.get("queue_depth", 0)
                    max_capacity = capacity_info.get("max_capacity", 100)
                    congestion_level = 1.0 + (queue_depth / max(max_capacity, 1))
                    
                    # Update health based on success rate
                    success_rate = capacity_info.get("success_rate", 1.0)
                    health_factor = success_rate
                    
                    self.update_node_congestion(node_id, congestion_level)
                    self.update_node_health(node_id, health_factor)
                    
            except Exception as e:
                logger.error(f"FLOW_CONTROL: Error updating node {node_id}: {e}")
    
    def get_flow_recommendations(self) -> List[str]:
        """Get recommendations for optimizing flow control."""
        recommendations = []
        
        if not self.node_flows:
            return ["No nodes registered for flow control"]
        
        # Check for blocked nodes
        blocked_nodes = [nid for nid, nf in self.node_flows.items() if nf.state == FlowState.BLOCKED]
        if blocked_nodes:
            recommendations.append(f"{len(blocked_nodes)} nodes are blocked - "
                                 f"investigate capacity or increase credit limits")
        
        # Check for high throttling
        total_requests = sum(nf.total_requests for nf in self.node_flows.values())
        total_throttled = sum(nf.throttled_requests for nf in self.node_flows.values())
        
        if total_requests > 0:
            throttle_rate = total_throttled / total_requests
            if throttle_rate > 0.2:  # More than 20% throttled
                recommendations.append(f"High throttling rate ({throttle_rate:.1%}) - "
                                     f"consider increasing credit rates or capacity")
        
        # Check for emergency brake usage
        if self.global_stats["emergency_brakes"] > 0:
            recommendations.append("Emergency brake has been used - "
                                 "investigate system stability and capacity planning")
        
        # Check success rate
        if total_requests > 0:
            success_rate = self.global_stats["total_granted"] / total_requests
            if success_rate < 0.8:  # Less than 80% success
                recommendations.append(f"Low flow control success rate ({success_rate:.1%}) - "
                                     f"review credit allocation and node capacity")
        
        if not recommendations:
            recommendations.append("Flow control operating optimally - no issues detected")
        
        return recommendations
