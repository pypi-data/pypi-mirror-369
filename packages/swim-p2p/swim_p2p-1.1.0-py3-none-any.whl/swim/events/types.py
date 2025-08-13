"""
Event type definitions for the SWIM P2P protocol.

This module defines event types that provide value without duplicating SWIM's
core membership functionality. Events are categorized by their purpose:

1. ProtocolEvent: Low-level protocol operations (timeouts, errors)
2. PerformanceEvent: Performance thresholds and resource issues  
3. NetworkEvent: Network-level connectivity changes
4. ApplicationEvent: Application lifecycle and configuration
5. SystemEvent: System lifecycle events (node start/stop, protocol cycles)
6. MemberEvent: Member-related events (join/leave/suspect/alive/failed)
7. WorkflowEvent: Multi-agent workflow events (agent, workflow, resource)

IMPORTANT: All event instances must be created with keyword arguments due to the
use of kw_only=True in the dataclass decorators. For example:
    event = PingTimeoutEvent(
        target_address="127.0.0.1:8000",
        timeout_duration=1.5,
        attempt_number=1
    )
"""

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from datetime import datetime

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from swim.protocol.member import Member


class EventSeverity(Enum):
    """Severity levels for events."""
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventCategory(Enum):
    """Categories of events in the system."""
    PROTOCOL = "protocol"
    PERFORMANCE = "performance"
    NETWORK = "network"
    APPLICATION = "application"
    SYSTEM = "system"
    WORKFLOW = "workflow"  # New category for workflow events


class WorkflowEventType(Enum):
    """Sub-categories for workflow-specific events."""
    AGENT = "agent"
    WORKFLOW = "workflow"
    RESOURCE = "resource"


def _generate_event_id() -> str:
    """Generate a unique event ID using UUID4."""
    return f"evt_{uuid.uuid4().hex[:12]}"


@dataclass(kw_only=True)
class Event(ABC):
    """
    Base event class for all events in the SWIM system.
    
    This provides common functionality while keeping events lightweight.
    Events are immutable snapshots of what happened, not state containers.
    """
    source_node: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=_generate_event_id)
    severity: EventSeverity = EventSeverity.INFO
    category: EventCategory = field(default=None, init=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate event after creation."""
        if not hasattr(self, 'category'):
            raise ValueError(f"Event {self.__class__.__name__} must set category")
    
    @property
    def age_seconds(self) -> float:
        """Get the age of this event in seconds."""
        return time.time() - self.timestamp
    
    @property
    def datetime(self) -> datetime:
        """Get the event timestamp as a datetime object."""
        return datetime.fromtimestamp(self.timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.__class__.__name__,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "source_node": self.source_node,
            "severity": self.severity.value,
            "category": self.category.value,
            "metadata": self.metadata,
            **self._event_specific_data()
        }
    
    @abstractmethod
    def _event_specific_data(self) -> Dict[str, Any]:
        """Return event-specific data for serialization."""
        pass
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.__class__.__name__}(id={self.event_id}, severity={self.severity.value})"


# =============================================================================
# SYSTEM EVENTS - Node lifecycle and system operations
# =============================================================================

@dataclass(kw_only=True)
class SystemEvent(Event):
    """Base class for system-level events."""
    category: EventCategory = field(default=EventCategory.SYSTEM, init=False)


@dataclass(kw_only=True)
class NodeStartedEvent(SystemEvent):
    """Event emitted when a node starts."""
    severity: EventSeverity = field(default=EventSeverity.INFO, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "node_address": self.source_node,
            "transport_type": self.metadata.get("transport_type"),
            "seed_count": self.metadata.get("seed_count"),
            "lifeguard_enabled": self.metadata.get("lifeguard_enabled", False)
        }


@dataclass(kw_only=True)
class NodeStoppedEvent(SystemEvent):
    """Event emitted when a node stops."""
    severity: EventSeverity = field(default=EventSeverity.INFO, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "node_address": self.source_node,
            "uptime": self.metadata.get("uptime"),
            "protocol_cycles": self.metadata.get("protocol_cycles"),
            "ping_operations": self.metadata.get("ping_operations")
        }


@dataclass(kw_only=True)
class ProtocolCycleEvent(SystemEvent):
    """Event emitted periodically during protocol cycles."""
    severity: EventSeverity = field(default=EventSeverity.DEBUG, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "cycle_number": self.metadata.get("cycle_number"),
            "alive_count": self.metadata.get("alive_count"),
            "suspect_count": self.metadata.get("suspect_count"),
            "dead_count": self.metadata.get("dead_count"),
            "total_count": self.metadata.get("total_count")
        }


@dataclass(kw_only=True)
class ProtocolErrorEvent(SystemEvent):
    """Event emitted when an error occurs in the protocol loop."""
    severity: EventSeverity = field(default=EventSeverity.ERROR, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "error": self.metadata.get("error"),
            "cycle_number": self.metadata.get("cycle_number")
        }


@dataclass(kw_only=True)
class MessageErrorEvent(SystemEvent):
    """Event emitted when a message cannot be processed."""
    severity: EventSeverity = field(default=EventSeverity.WARNING, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "error": self.metadata.get("error"),
            "from": self.metadata.get("from"),
            "data_size": self.metadata.get("data_size")
        }


@dataclass(kw_only=True)
class UnknownMessageTypeEvent(SystemEvent):
    """Event emitted when an unknown message type is received."""
    severity: EventSeverity = field(default=EventSeverity.WARNING, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "message_type": self.metadata.get("message_type"),
            "from": self.metadata.get("from"),
            "message_id": self.metadata.get("message_id")
        }


# =============================================================================
# PROTOCOL EVENTS - Low-level protocol operations
# =============================================================================

@dataclass(kw_only=True)
class ProtocolEvent(Event):
    """Base class for protocol-level events."""
    category: EventCategory = field(default=EventCategory.PROTOCOL, init=False)


@dataclass(kw_only=True)
class PingTimeoutEvent(ProtocolEvent):
    """
    Emitted when a ping operation times out.
    
    This is different from membership changes - it's about the protocol
    operation itself, useful for debugging and performance analysis.
    """
    target_address: str
    timeout_duration: float
    attempt_number: int
    is_indirect: bool = False
    severity: EventSeverity = field(default=EventSeverity.WARNING, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "target_address": self.target_address,
            "timeout_duration": self.timeout_duration,
            "attempt_number": self.attempt_number,
            "is_indirect": self.is_indirect
        }


@dataclass(kw_only=True)
class SyncCompletedEvent(ProtocolEvent):
    """
    Emitted when a push-pull sync operation completes.
    
    Useful for monitoring sync performance and frequency.
    """
    peer_address: str
    duration_ms: float
    members_exchanged: int
    bytes_transferred: int
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "peer_address": self.peer_address,
            "duration_ms": self.duration_ms,
            "members_exchanged": self.members_exchanged,
            "bytes_transferred": self.bytes_transferred
        }


@dataclass(kw_only=True)
class TransportErrorEvent(ProtocolEvent):
    """
    Emitted when transport-level errors occur.
    
    Helps distinguish between network issues and protocol issues.
    """
    error_type: str
    error_message: str
    target_address: Optional[str] = None
    operation: Optional[str] = None
    severity: EventSeverity = field(default=EventSeverity.ERROR, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "target_address": self.target_address,
            "operation": self.operation
        }


# =============================================================================
# PERFORMANCE EVENTS - Resource and performance monitoring
# =============================================================================

@dataclass(kw_only=True)
class PerformanceEvent(Event):
    """Base class for performance-related events."""
    category: EventCategory = field(default=EventCategory.PERFORMANCE, init=False)


@dataclass(kw_only=True)
class LatencyThresholdExceededEvent(PerformanceEvent):
    """
    Emitted when network latency exceeds configured thresholds.
    
    Helps applications adapt to network conditions.
    """
    peer_address: str
    current_latency_ms: float
    threshold_ms: float
    measurement_window: str
    severity: EventSeverity = field(default=EventSeverity.WARNING, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "peer_address": self.peer_address,
            "current_latency_ms": self.current_latency_ms,
            "threshold_ms": self.threshold_ms,
            "measurement_window": self.measurement_window
        }


@dataclass(kw_only=True)
class BandwidthLimitReachedEvent(PerformanceEvent):
    """
    Emitted when bandwidth usage approaches configured limits.
    
    Allows applications to throttle or prioritize traffic.
    """
    current_bandwidth_bps: float
    limit_bandwidth_bps: float
    direction: str  # "inbound" or "outbound"
    utilization_percent: float
    severity: EventSeverity = field(default=EventSeverity.WARNING, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "current_bandwidth_bps": self.current_bandwidth_bps,
            "limit_bandwidth_bps": self.limit_bandwidth_bps,
            "direction": self.direction,
            "utilization_percent": self.utilization_percent
        }


@dataclass(kw_only=True)
class ResourceExhaustionEvent(PerformanceEvent):
    """
    Emitted when system resources are running low.
    
    Helps applications take corrective action before failures.
    """
    resource_type: str  # "memory", "cpu", "file_descriptors", etc.
    current_usage: float
    total_available: float
    utilization_percent: float
    severity: EventSeverity = field(default=EventSeverity.ERROR, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "resource_type": self.resource_type,
            "current_usage": self.current_usage,
            "total_available": self.total_available,
            "utilization_percent": self.utilization_percent
        }


# =============================================================================
# NETWORK EVENTS - Connectivity and topology changes
# =============================================================================

@dataclass(kw_only=True)
class NetworkEvent(Event):
    """Base class for network-level events."""
    category: EventCategory = field(default=EventCategory.NETWORK, init=False)


@dataclass(kw_only=True)
class ConnectionEstablishedEvent(NetworkEvent):
    """
    Emitted when a new network connection is established.
    
    Different from membership - this is about transport connections.
    """
    peer_address: str
    connection_type: str  # "tcp", "udp", "hybrid"
    connection_id: str
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "peer_address": self.peer_address,
            "connection_type": self.connection_type,
            "connection_id": self.connection_id
        }


@dataclass(kw_only=True)
class ConnectionLostEvent(NetworkEvent):
    """
    Emitted when a network connection is lost.
    
    Helps distinguish between connection issues and node failures.
    """
    peer_address: str
    connection_type: str
    connection_id: str
    reason: str
    duration_seconds: float
    severity: EventSeverity = field(default=EventSeverity.WARNING, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "peer_address": self.peer_address,
            "connection_type": self.connection_type,
            "connection_id": self.connection_id,
            "reason": self.reason,
            "duration_seconds": self.duration_seconds
        }


@dataclass(kw_only=True)
class NetworkPartitionDetectedEvent(NetworkEvent):
    """
    Emitted when a potential network partition is detected.
    
    Based on patterns in connectivity, not individual node failures.
    """
    affected_nodes: List[str]
    partition_confidence: float  # 0.0 to 1.0
    detection_method: str
    severity: EventSeverity = field(default=EventSeverity.CRITICAL, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "affected_nodes": self.affected_nodes,
            "partition_confidence": self.partition_confidence,
            "detection_method": self.detection_method
        }


# =============================================================================
# APPLICATION EVENTS - Lifecycle and configuration
# =============================================================================

@dataclass(kw_only=True)
class ApplicationEvent(Event):
    """Base class for application-level events."""
    category: EventCategory = field(default=EventCategory.APPLICATION, init=False)


@dataclass(kw_only=True)
class MetricsCollectionEvent(ApplicationEvent):
    """
    Emitted when metrics collection completes.
    
    Allows other components to react to fresh metrics data.
    """
    collection_duration_ms: float
    metrics_count: int
    collection_type: str  # "periodic", "on_demand", "triggered"
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "collection_duration_ms": self.collection_duration_ms,
            "metrics_count": self.metrics_count,
            "collection_type": self.collection_type
        }


@dataclass(kw_only=True)
class ConfigurationChangedEvent(ApplicationEvent):
    """
    Emitted when node configuration changes.
    
    Allows components to adapt to new settings.
    """
    changed_keys: List[str]
    change_source: str  # "api", "file", "environment", etc.
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "changed_keys": self.changed_keys,
            "change_source": self.change_source
        }


@dataclass(kw_only=True)
class ShutdownInitiatedEvent(ApplicationEvent):
    """
    Emitted when node shutdown begins.
    
    Allows components to perform cleanup.
    """
    shutdown_reason: str
    graceful: bool
    estimated_shutdown_time_seconds: float
    severity: EventSeverity = field(default=EventSeverity.INFO, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "shutdown_reason": self.shutdown_reason,
            "graceful": self.graceful,
            "estimated_shutdown_time_seconds": self.estimated_shutdown_time_seconds
        }


# =============================================================================
# MEMBER EVENTS - Events related to membership changes
# =============================================================================

@dataclass(kw_only=True)
class MemberEvent(Event):
    """Base event class for member-related events."""
    member: 'Member'
    category: EventCategory = field(default=EventCategory.APPLICATION, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        """Return member-specific data for serialization."""
        return {
            "member": self.member.to_dict() if hasattr(self.member, 'to_dict') else str(self.member)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemberEvent":
        """Create a member event from a dictionary."""
        # Import here to avoid circular imports
        from swim.protocol.member import Member
        
        member_data = data.pop("member", {})
        member = Member.from_dict(member_data) if hasattr(Member, 'from_dict') else None
        return cls(
            member=member,
            timestamp=data.get("timestamp", time.time()),
            source_node=data.get("source_node"),
            metadata=data.get("metadata", {})
        )


@dataclass(kw_only=True)
class MemberJoinedEvent(MemberEvent):
    """Event emitted when a new member joins the cluster."""
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "join_method": self.metadata.get("join_method", "unknown"),
            "seed_node": self.metadata.get("seed_node"),
            "cluster_size": self.metadata.get("cluster_size")
        })
        return data


@dataclass(kw_only=True)
class MemberLeftEvent(MemberEvent):
    """Event emitted when a member leaves the cluster gracefully."""
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "leave_reason": self.metadata.get("leave_reason", "graceful_shutdown"),
            "was_alive": self.metadata.get("was_alive", True),
            "uptime": self.metadata.get("uptime")
        })
        return data


@dataclass(kw_only=True)
class MemberFailedEvent(MemberEvent):
    """Event emitted when a member is detected as failed."""
    severity: EventSeverity = field(default=EventSeverity.WARNING, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "failure_detection_method": self.metadata.get("failure_detection_method", "timeout"),
            "last_seen": self.metadata.get("last_seen"),
            "failure_duration": self.metadata.get("failure_duration"),
            "consecutive_failures": self.metadata.get("consecutive_failures")
        })
        return data


@dataclass(kw_only=True)
class MemberSuspectedEvent(MemberEvent):
    """Event emitted when a member is suspected of being failed."""
    severity: EventSeverity = field(default=EventSeverity.INFO, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "suspicion_reason": self.metadata.get("suspicion_reason", "ping_timeout"),
            "timeout_duration": self.metadata.get("timeout_duration"),
            "attempt_number": self.metadata.get("attempt_number"),
            "indirect_ping_attempted": self.metadata.get("indirect_ping_attempted", False)
        })
        return data


@dataclass(kw_only=True)
class MemberAliveEvent(MemberEvent):
    """Event emitted when a previously suspected member is detected as alive."""
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "recovery_method": self.metadata.get("recovery_method", "ping_response"),
            "was_suspected_duration": self.metadata.get("was_suspected_duration"),
            "incarnation_changed": self.metadata.get("incarnation_changed", False),
            "false_positive": self.metadata.get("false_positive", False)
        })
        return data


# =============================================================================
# WORKFLOW EVENTS - Events related to multi-agent workflows
# =============================================================================

@dataclass(kw_only=True)
class WorkflowEvent(Event):
    """Base class for workflow-related events."""
    category: EventCategory = field(default=EventCategory.WORKFLOW, init=False)
    workflow_type: WorkflowEventType = field(default=None, init=False)


# ============================================================================
# Agent Events - Related to agent lifecycle
# ============================================================================

@dataclass(kw_only=True)
class AgentEvent(WorkflowEvent):
    """Base class for agent-related events."""
    agent_id: str
    workflow_type: WorkflowEventType = field(default=WorkflowEventType.AGENT, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "workflow_type": self.workflow_type.value
        }


@dataclass(kw_only=True)
class AgentJoinedEvent(AgentEvent):
    """Event emitted when a new agent joins the system."""
    agent_type: str
    capabilities: List[str]
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "agent_type": self.agent_type,
            "capabilities": self.capabilities
        })
        return data


@dataclass(kw_only=True)
class AgentLeftEvent(AgentEvent):
    """Event emitted when an agent gracefully leaves the system."""
    reason: str = "shutdown"
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "reason": self.reason
        })
        return data


@dataclass(kw_only=True)
class AgentFailedEvent(AgentEvent):
    """Event emitted when an agent fails unexpectedly."""
    error: str
    severity: EventSeverity = field(default=EventSeverity.ERROR, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "error": self.error
        })
        return data


# ============================================================================
# Process Workflow Events - Related to workflow execution
# ============================================================================

@dataclass(kw_only=True)
class ProcessWorkflowEvent(WorkflowEvent):
    """Base class for process workflow-related events."""
    workflow_id: str
    workflow_type: WorkflowEventType = field(default=WorkflowEventType.WORKFLOW, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type.value
        }


@dataclass(kw_only=True)
class StepStartedEvent(ProcessWorkflowEvent):
    """Event emitted when a workflow step begins."""
    step_id: str
    agent_id: str
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "step_id": self.step_id,
            "agent_id": self.agent_id
        })
        return data


@dataclass(kw_only=True)
class StepCompletedEvent(ProcessWorkflowEvent):
    """Event emitted when a workflow step completes successfully."""
    step_id: str
    agent_id: str
    duration_ms: float
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "step_id": self.step_id,
            "agent_id": self.agent_id,
            "duration_ms": self.duration_ms
        })
        return data


@dataclass(kw_only=True)
class StepFailedEvent(ProcessWorkflowEvent):
    """Event emitted when a workflow step fails."""
    step_id: str
    agent_id: str
    error: str
    severity: EventSeverity = field(default=EventSeverity.ERROR, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "step_id": self.step_id,
            "agent_id": self.agent_id,
            "error": self.error
        })
        return data


@dataclass(kw_only=True)
class WorkflowCompletedEvent(ProcessWorkflowEvent):
    """Event emitted when an entire workflow finishes."""
    total_duration_ms: float
    step_count: int
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "total_duration_ms": self.total_duration_ms,
            "step_count": self.step_count
        })
        return data


# ============================================================================
# Resource Events - Related to resources and outputs
# ============================================================================

@dataclass(kw_only=True)
class ResourceEvent(WorkflowEvent):
    """Base class for resource-related events."""
    resource_id: str
    workflow_type: WorkflowEventType = field(default=WorkflowEventType.RESOURCE, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "workflow_type": self.workflow_type.value
        }


@dataclass(kw_only=True)
class OutputRequestEvent(ResourceEvent):
    """Event emitted when an agent needs a resource."""
    agent_id: str
    resource_type: str
    priority: int = 0
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "agent_id": self.agent_id,
            "resource_type": self.resource_type,
            "priority": self.priority
        })
        return data


@dataclass(kw_only=True)
class OutputAvailableEvent(ResourceEvent):
    """Event emitted when a resource becomes available."""
    resource_type: str
    size_bytes: Optional[int] = None
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "resource_type": self.resource_type,
            "size_bytes": self.size_bytes
        })
        return data


@dataclass(kw_only=True)
class OutputReceivedEvent(ResourceEvent):
    """Event emitted when an agent has received a resource."""
    agent_id: str
    resource_type: str
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "agent_id": self.agent_id,
            "resource_type": self.resource_type
        })
        return data


@dataclass(kw_only=True)
class LoadThresholdEvent(ResourceEvent):
    """Event emitted when an agent's load crosses a threshold."""
    agent_id: str
    current_load: float  # 0.0 to 1.0
    threshold: float
    is_overloaded: bool
    severity: EventSeverity = field(default=EventSeverity.WARNING, init=False)
    
    def _event_specific_data(self) -> Dict[str, Any]:
        data = super()._event_specific_data()
        data.update({
            "agent_id": self.agent_id,
            "current_load": self.current_load,
            "threshold": self.threshold,
            "is_overloaded": self.is_overloaded
        })
        return data


# Helper function to map SWIM members to agent IDs
def map_member_to_agent_id(member) -> str:
    """Extract agent ID from a SWIM member."""
    # This assumes your Member objects have metadata with agent_id
    # Adjust based on your actual Member implementation
    if hasattr(member, 'metadata') and 'agent_id' in member.metadata:
        return member.metadata['agent_id']
    
    # Fallback: use address as ID
    if hasattr(member, 'addr'):
        return f"{member.addr[0]}:{member.addr[1]}"
    
    return str(member)