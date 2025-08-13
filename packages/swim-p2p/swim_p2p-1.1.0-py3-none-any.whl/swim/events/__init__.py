"""
Event system for the SWIM P2P protocol.

This package provides a lightweight event system that transforms internal SWIM
state changes into standardized event objects for application components to consume.

Key principles:
- SWIM remains the single source of truth for all state
- Events are notifications, not state storage
- Thin wrappers around existing SWIM functionality
- Focus on non-redundant, application-valuable events
"""

from typing import TYPE_CHECKING

# Import core components that don't cause circular imports
from swim.events.dispatcher import EventDispatcher
from swim.events.types import (
    Event,
    EventCategory,
    EventSeverity,
    WorkflowEventType,
    ProtocolEvent,
    PerformanceEvent,
    NetworkEvent,
    ApplicationEvent,
    SystemEvent,
    WorkflowEvent,
    # Protocol-specific events
    PingTimeoutEvent,
    SyncCompletedEvent,
    TransportErrorEvent,
    # Performance events
    LatencyThresholdExceededEvent,
    BandwidthLimitReachedEvent,
    ResourceExhaustionEvent,
    # Network events
    ConnectionEstablishedEvent,
    ConnectionLostEvent,
    NetworkPartitionDetectedEvent,
    # Application events
    MetricsCollectionEvent,
    ConfigurationChangedEvent,
    ShutdownInitiatedEvent,
    # System events
    NodeStartedEvent,
    NodeStoppedEvent,
    ProtocolCycleEvent,
    ProtocolErrorEvent,
    MessageErrorEvent,
    UnknownMessageTypeEvent,
    # Member events (now defined in types.py)
    MemberEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    MemberFailedEvent,
    MemberSuspectedEvent,
    MemberAliveEvent,
    # Agent events
    AgentEvent,
    AgentJoinedEvent,
    AgentLeftEvent,
    AgentFailedEvent,
    # Workflow events
    ProcessWorkflowEvent,
    StepStartedEvent,
    StepCompletedEvent,
    StepFailedEvent,
    WorkflowCompletedEvent,
    # Resource events
    ResourceEvent,
    OutputRequestEvent,
    OutputAvailableEvent,
    OutputReceivedEvent,
    LoadThresholdEvent,
    # Helper functions
    map_member_to_agent_id,
)

from swim.events.handlers import (
    LoggingHandler,
    MetricsHandler,
    PerformanceHandler,
    IntegrationHandler,
    create_default_handlers,
    register_default_handlers,
)

# Only import Member for type checking
if TYPE_CHECKING:
    from swim.protocol.member import Member, MemberState, MemberList

__all__ = [
    # Core components
    "EventDispatcher",
    # Base event types
    "Event",
    "EventCategory",
    "EventSeverity",
    "WorkflowEventType",
    "ProtocolEvent", 
    "PerformanceEvent",
    "NetworkEvent",
    "ApplicationEvent",
    "SystemEvent",
    "WorkflowEvent",
    # Protocol events
    "PingTimeoutEvent",
    "SyncCompletedEvent", 
    "TransportErrorEvent",
    # Performance events
    "LatencyThresholdExceededEvent",
    "BandwidthLimitReachedEvent",
    "ResourceExhaustionEvent",
    # Network events
    "ConnectionEstablishedEvent",
    "ConnectionLostEvent",
    "NetworkPartitionDetectedEvent",
    # Application events
    "MetricsCollectionEvent",
    "ConfigurationChangedEvent",
    "ShutdownInitiatedEvent",
    # System events
    "NodeStartedEvent",
    "NodeStoppedEvent",
    "ProtocolCycleEvent",
    "ProtocolErrorEvent",
    "MessageErrorEvent",
    "UnknownMessageTypeEvent",
    # Member events (from types.py)
    "MemberEvent",
    "MemberJoinedEvent",
    "MemberLeftEvent",
    "MemberFailedEvent",
    "MemberSuspectedEvent",
    "MemberAliveEvent",
    # Agent events
    "AgentEvent",
    "AgentJoinedEvent",
    "AgentLeftEvent",
    "AgentFailedEvent",
    # Workflow events
    "ProcessWorkflowEvent",
    "StepStartedEvent",
    "StepCompletedEvent",
    "StepFailedEvent",
    "WorkflowCompletedEvent",
    # Resource events
    "ResourceEvent",
    "OutputRequestEvent",
    "OutputAvailableEvent",
    "OutputReceivedEvent",
    "LoadThresholdEvent",
    # Helper functions
    "map_member_to_agent_id",
    # Handlers
    "LoggingHandler",
    "MetricsHandler", 
    "PerformanceHandler",
    "IntegrationHandler",
    "create_default_handlers",
    "register_default_handlers",
]

# Version info
__version__ = "1.0.0"
