"""
Event handlers for the SWIM protocol.

This module defines handlers for processing events in the system,
including logging, metrics collection, performance monitoring,
and integration with the ZMQ messaging layer.
"""

import logging
import time
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional, Callable, Set, TYPE_CHECKING, Union

# Import only the base types to avoid circular dependency
from swim.events.types import (
    Event, EventCategory, EventSeverity,
    MemberEvent, MemberJoinedEvent, MemberLeftEvent, MemberFailedEvent, MemberSuspectedEvent,
    AgentJoinedEvent, AgentLeftEvent, AgentFailedEvent, map_member_to_agent_id,
    StepStartedEvent, StepCompletedEvent, StepFailedEvent, WorkflowCompletedEvent,
    OutputRequestEvent, OutputAvailableEvent, OutputReceivedEvent, LoadThresholdEvent
)

logger = logging.getLogger(__name__)


class LoggingHandler:
    """
    Handler that logs events to the configured logger.
    
    This handler formats events into human-readable log messages
    with appropriate log levels based on event severity.
    """
    
    def __init__(
        self,
        logger_name: str = "swim.events",
        include_metadata: bool = True,
        max_metadata_length: int = 200
    ):
        """
        Initialize a new logging handler.
        
        Args:
            logger_name: Name of the logger to use
            include_metadata: Whether to include event metadata in logs
            max_metadata_length: Maximum length for metadata in logs
        """
        self.logger = logging.getLogger(logger_name)
        self.include_metadata = include_metadata
        self.max_metadata_length = max_metadata_length
    
    def __call__(self, event: Event) -> None:
        """
        Process an event by logging it.
        
        Args:
            event: The event to log
        """
        # Map event severity to log level
        level_map = {
            EventSeverity.DEBUG: logging.DEBUG,
            EventSeverity.INFO: logging.INFO,
            EventSeverity.WARNING: logging.WARNING,
            EventSeverity.ERROR: logging.ERROR,
            EventSeverity.CRITICAL: logging.CRITICAL
        }
        
        level = level_map.get(event.severity, logging.INFO)
        
        # Format the message based on event type
        event_type = event.__class__.__name__
        
        # Basic message with event type and source
        message = f"{event_type}"
        
        if event.source_node:
            message += f" from {event.source_node}"
        
        # Add event-specific details
        if hasattr(event, 'target_address'):
            message += f", target: {event.target_address}"
        
        if hasattr(event, 'timeout_duration'):
            message += f", timeout: {event.timeout_duration:.1f}s"
        
        if hasattr(event, 'response_time'):
            message += f", response time: {event.response_time:.3f}s"
        
        if hasattr(event, 'member'):
            # Access member attributes safely without importing Member
            member = event.member
            addr = getattr(member, 'addr', None)
            if addr:
                message += f", member: {addr[0]}:{addr[1]}"
        
        # Include metadata if enabled
        if self.include_metadata and event.metadata:
            metadata_str = str(event.metadata)
            if len(metadata_str) > self.max_metadata_length:
                metadata_str = metadata_str[:self.max_metadata_length] + "..."
            message += f", metadata: {metadata_str}"
        
        # Log the message
        self.logger.log(level, message)


class MetricsHandler:
    """
    Handler that collects metrics from events.
    
    This handler maintains counters, gauges, and histograms based on
    events in the system, and can integrate with external metrics collectors.
    """
    
    def __init__(self, metrics_collector=None):
        """
        Initialize a new metrics handler.
        
        Args:
            metrics_collector: Optional external metrics collector to use
        """
        self.metrics_collector = metrics_collector
        
        # Internal metrics storage
        self.counters = defaultdict(int)
        self.gauges = {}
        self.histograms = defaultdict(list)
    
    def __call__(self, event: Event) -> None:
        """
        Process an event by updating metrics.
        
        Args:
            event: The event to process
        """
        try:
            # Update basic counters
            self.counters["events_total"] += 1
            
            # Update category counter
            category_name = event.category.name.lower()
            self.counters[f"events_{category_name}"] += 1
            
            # Update severity counter
            severity_name = event.severity.name.lower()
            self.counters[f"events_{severity_name}"] += 1
            
            # Update event type counter
            event_type = event.__class__.__name__
            self.counters[f"events_{event_type}"] += 1
            
            # Process specific event types
            self._process_specific_event(event)
            
            # Forward to external collector if available
            if self.metrics_collector:
                self._forward_to_collector(event)
                
        except Exception as e:
            logger.error(f"Error processing event in metrics handler: {e}")
    
    def _process_specific_event(self, event: Event) -> None:
        """
        Process specific event types with custom metrics.
        
        Args:
            event: The event to process
        """
        event_type = event.__class__.__name__
        
        # Handle ping timeout events
        if event_type == "PingTimeoutEvent":
            self.counters["ping_timeouts_total"] += 1
            
            if hasattr(event, 'is_indirect') and event.is_indirect:
                self.counters["indirect_ping_timeouts_total"] += 1
            
            if hasattr(event, 'timeout_duration'):
                self.histograms["ping_timeout_duration"].append(event.timeout_duration)
        
        # Handle latency threshold events
        elif event_type == "LatencyThresholdExceededEvent":
            self.counters["latency_threshold_exceeded_total"] += 1
            
            if hasattr(event, 'current_latency_ms'):
                self.histograms["latency_measurements"].append(event.current_latency_ms)
            
            if hasattr(event, 'peer_address') and hasattr(event, 'current_latency_ms'):
                self.gauges[f"latency_current_{event.peer_address}"] = event.current_latency_ms
        
        # Handle resource exhaustion events
        elif event_type == "ResourceExhaustionEvent":
            if hasattr(event, 'resource_type'):
                self.counters[f"resource_exhaustion_{event.resource_type}_total"] += 1
                
                if hasattr(event, 'utilization_percent'):
                    self.gauges[f"resource_usage_{event.resource_type}"] = event.utilization_percent
        
        # Handle member events without importing Member class
        elif event_type.startswith("Member") and hasattr(event, 'member'):
            if event_type == "MemberJoinedEvent":
                self.counters["member_joined_count"] += 1
            elif event_type == "MemberLeftEvent":
                self.counters["member_left_count"] += 1
            elif event_type == "MemberFailedEvent":
                self.counters["member_failed_count"] += 1
            elif event_type == "MemberSuspectedEvent":
                self.counters["member_suspected_count"] += 1
            elif event_type == "MemberAliveEvent":
                self.counters["member_alive_count"] += 1
        
        # Handle agent events
        elif event_type.startswith("Agent"):
            if event_type == "AgentJoinedEvent":
                self.counters["agent_joined_count"] += 1
            elif event_type == "AgentLeftEvent":
                self.counters["agent_left_count"] += 1
            elif event_type == "AgentFailedEvent":
                self.counters["agent_failed_count"] += 1
        
        # Handle workflow events
        elif event_type.startswith("Step") or event_type == "WorkflowCompletedEvent":
            if event_type == "StepStartedEvent":
                self.counters["step_started_count"] += 1
            elif event_type == "StepCompletedEvent":
                self.counters["step_completed_count"] += 1
                if hasattr(event, 'duration_ms'):
                    self.histograms["step_duration_ms"].append(event.duration_ms)
            elif event_type == "StepFailedEvent":
                self.counters["step_failed_count"] += 1
            elif event_type == "WorkflowCompletedEvent":
                self.counters["workflow_completed_count"] += 1
                if hasattr(event, 'total_duration_ms'):
                    self.histograms["workflow_duration_ms"].append(event.total_duration_ms)
    
    def _forward_to_collector(self, event: Event) -> None:
        """
        Forward event metrics to external collector.
        
        Args:
            event: The event to forward
        """
        try:
            # Basic event count
            self.metrics_collector.increment_metric("events_total")
            
            # Category count
            category_name = event.category.name.lower()
            self.metrics_collector.increment_metric(f"events_{category_name}")
            
            # Event type count
            event_type = event.__class__.__name__
            self.metrics_collector.increment_metric(f"events_{event_type}")
            
            # Forward specific metrics based on event type
            if event_type == "PingTimeoutEvent":
                self.metrics_collector.increment_metric("ping_timeouts_total")
                
                if hasattr(event, 'timeout_duration'):
                    self.metrics_collector.record_histogram(
                        "ping_timeout_duration", 
                        event.timeout_duration
                    )
            
            elif event_type == "LatencyThresholdExceededEvent":
                self.metrics_collector.increment_metric("latency_threshold_exceeded_total")
                
                if hasattr(event, 'peer_address') and hasattr(event, 'current_latency_ms'):
                    self.metrics_collector.set_gauge(
                        f"latency_current_{event.peer_address}", 
                        event.current_latency_ms
                    )
            
            elif event_type == "ResourceExhaustionEvent" and hasattr(event, 'resource_type'):
                self.metrics_collector.increment_metric(
                    f"resource_exhaustion_{event.resource_type}_total"
                )
                
                if hasattr(event, 'utilization_percent'):
                    self.metrics_collector.set_gauge(
                        f"resource_usage_{event.resource_type}", 
                        event.utilization_percent
                    )
            
            # Member events
            elif event_type == "MemberJoinedEvent":
                self.metrics_collector.increment_metric("member_joined_count")
            elif event_type == "MemberLeftEvent":
                self.metrics_collector.increment_metric("member_left_count")
            elif event_type == "MemberFailedEvent":
                self.metrics_collector.increment_metric("member_failed_count")
            elif event_type == "MemberSuspectedEvent":
                self.metrics_collector.increment_metric("member_suspected_count")
            elif event_type == "MemberAliveEvent":
                self.metrics_collector.increment_metric("member_alive_count")
                
        except Exception as e:
            logger.error(f"Error forwarding metrics to collector: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary with counters, gauges, and histogram counts
        """
        # Create a copy of the metrics
        metrics = {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histogram_counts": {
                k: len(v) for k, v in self.histograms.items()
            }
        }
        
        return metrics


class PerformanceHandler:
    """
    Handler that monitors performance-related events.
    
    This handler tracks latency and resource usage over time,
    and can trigger alerts when thresholds are exceeded.
    """
    
    def __init__(
        self,
        alert_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        latency_alert_threshold: float = 1000.0,  # ms
        resource_alert_threshold: float = 90.0,   # percent
        cooldown_period: float = 300.0            # seconds
    ):
        """
        Initialize a new performance handler.
        
        Args:
            alert_callback: Function to call when an alert is triggered
            latency_alert_threshold: Threshold for latency alerts in ms
            resource_alert_threshold: Threshold for resource alerts in percent
            cooldown_period: Minimum time between alerts in seconds
        """
        self.alert_callback = alert_callback
        self.latency_alert_threshold = latency_alert_threshold
        self.resource_alert_threshold = resource_alert_threshold
        self.cooldown_period = cooldown_period
        
        # Track history for trend analysis
        self.latency_history: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        self.resource_history: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        
        # Track last alert times
        self.last_alerts: Dict[str, float] = {}
    
    def __call__(self, event: Event) -> None:
        """
        Process an event for performance monitoring.
        
        Args:
            event: The event to process
        """
        # Only process performance-related events
        if event.category != EventCategory.PERFORMANCE and event.category != EventCategory.SYSTEM:
            return
        
        event_type = event.__class__.__name__
        
        # Handle latency events
        if event_type == "LatencyThresholdExceededEvent" and hasattr(event, 'peer_address'):
            self._handle_latency_event(event)
        
        # Handle resource events
        elif event_type == "ResourceExhaustionEvent" and hasattr(event, 'resource_type'):
            self._handle_resource_event(event)
    
    def _handle_latency_event(self, event: Any) -> None:
        """
        Handle a latency-related event.
        
        Args:
            event: The latency event to handle
        """
        peer = event.peer_address
        latency = event.current_latency_ms
        
        # Record in history
        self.latency_history[peer].append((time.time(), latency))
        
        # Trim history to last 100 entries
        if len(self.latency_history[peer]) > 100:
            self.latency_history[peer] = self.latency_history[peer][-100:]
        
        # Check if we should alert
        if latency > self.latency_alert_threshold and self._should_alert(f"latency_{peer}"):
            # Calculate trend
            trend = self._calculate_latency_trend(peer)
            
            # Trigger alert
            if self.alert_callback:
                try:
                    self.alert_callback("high_latency", {
                        "peer": peer,
                        "current_latency": latency,
                        "threshold": self.latency_alert_threshold,
                        "trend": trend
                    })
                except Exception as e:
                    logger.error(f"Error in performance alert callback: {e}")
    
    def _handle_resource_event(self, event: Any) -> None:
        """
        Handle a resource-related event.
        
        Args:
            event: The resource event to handle
        """
        resource = event.resource_type
        usage = event.utilization_percent
        
        # Record in history
        self.resource_history[resource].append((time.time(), usage))
        
        # Trim history to last 100 entries
        if len(self.resource_history[resource]) > 100:
            self.resource_history[resource] = self.resource_history[resource][-100:]
        
        # Check if we should alert
        if usage > self.resource_alert_threshold and self._should_alert(f"resource_{resource}"):
            # Trigger alert
            if self.alert_callback:
                try:
                    self.alert_callback("resource_exhaustion", {
                        "resource": resource,
                        "current_usage": usage,
                        "threshold": self.resource_alert_threshold,
                        "available": event.total_available if hasattr(event, 'total_available') else None
                    })
                except Exception as e:
                    logger.error(f"Error in performance alert callback: {e}")
    
    def _should_alert(self, alert_key: str) -> bool:
        """
        Check if we should trigger an alert based on cooldown period.
        
        Args:
            alert_key: Key identifying the alert type
            
        Returns:
            True if we should alert, False otherwise
        """
        now = time.time()
        last_alert = self.last_alerts.get(alert_key, 0)
        
        if now - last_alert > self.cooldown_period:
            self.last_alerts[alert_key] = now
            return True
        
        return False
    
    def _calculate_latency_trend(self, peer: str) -> str:
        """
        Calculate the trend of latency for a peer.
        
        Args:
            peer: The peer to calculate trend for
            
        Returns:
            Trend description: "increasing", "decreasing", "stable", or "insufficient_data"
        """
        history = self.latency_history.get(peer, [])
        
        if len(history) < 5:
            return "insufficient_data"
        
        # Get recent values (last 5)
        recent = history[-5:]
        
        # Calculate average change
        changes = [recent[i][1] - recent[i-1][1] for i in range(1, len(recent))]
        avg_change = sum(changes) / len(changes)
        
        # Determine trend
        if abs(avg_change) < 5.0:  # Less than 5ms change on average
            return "stable"
        elif avg_change > 0:
            return "increasing"
        else:
            return "decreasing"


class IntegrationHandler:
    """
    Handler that bridges SWIM events to the ZMQ integration layer.
    
    This handler translates SWIM membership events into agent events
    and forwards them to the integration layer for processing.
    """
    
    def __init__(self, integration_layer):
        """
        Initialize the integration handler.
        
        Args:
            integration_layer: The integration layer instance
        """
        self.integration_layer = integration_layer
        
        # Map of event types to handler methods
        self.event_handlers = {
            "MemberJoinedEvent": self._handle_member_joined,
            "MemberLeftEvent": self._handle_member_left,
            "MemberFailedEvent": self._handle_member_failed,
            "MemberSuspectedEvent": self._handle_member_suspected,
            "AgentJoinedEvent": self._handle_agent_joined,
            "AgentLeftEvent": self._handle_agent_left,
            "AgentFailedEvent": self._handle_agent_failed,
            "StepStartedEvent": self._handle_step_started,
            "StepCompletedEvent": self._handle_step_completed,
            "StepFailedEvent": self._handle_step_failed,
            "WorkflowCompletedEvent": self._handle_workflow_completed,
            "OutputRequestEvent": self._handle_output_request,
            "OutputAvailableEvent": self._handle_output_available,
            "OutputReceivedEvent": self._handle_output_received,
            "LoadThresholdEvent": self._handle_load_threshold
        }
    
    def __call__(self, event: Event) -> None:
        """
        Process an event by forwarding it to the integration layer.
        
        Args:
            event: The event to process
        """
        try:
            # Get the event type
            event_type = event.__class__.__name__
            
            # Check if we have a specific handler for this event type
            if event_type in self.event_handlers:
                self.event_handlers[event_type](event)
            else:
                # For unhandled events, log and ignore
                logger.debug(f"No specific handler for event type: {event_type}")
        
        except Exception as e:
            logger.error(f"Error processing event in integration handler: {e}", exc_info=True)
    
    def _handle_member_joined(self, event: MemberJoinedEvent) -> None:
        """Handle a member joined event by creating an agent joined event."""
        try:
            # Extract agent ID from member
            agent_id = map_member_to_agent_id(event.member)
            
            # Create an agent joined event
            agent_event = AgentJoinedEvent(
                agent_id=agent_id,
                agent_type=event.metadata.get('agent_type', 'unknown'),
                capabilities=event.metadata.get('capabilities', []),
                source_node=event.source_node
            )
            
            # Forward to integration layer
            self.integration_layer.handle_agent_joined(agent_event)
            
        except Exception as e:
            logger.error(f"Error handling member joined event: {e}", exc_info=True)
    
    def _handle_member_left(self, event: MemberLeftEvent) -> None:
        """Handle a member left event by creating an agent left event."""
        try:
            # Extract agent ID from member
            agent_id = map_member_to_agent_id(event.member)
            
            # Create an agent left event
            agent_event = AgentLeftEvent(
                agent_id=agent_id,
                reason=event.metadata.get('leave_reason', 'graceful_shutdown'),
                source_node=event.source_node
            )
            
            # Forward to integration layer
            self.integration_layer.handle_agent_left(agent_event)
            
        except Exception as e:
            logger.error(f"Error handling member left event: {e}", exc_info=True)
    
    def _handle_member_failed(self, event: MemberFailedEvent) -> None:
        """Handle a member failed event by creating an agent failed event."""
        try:
            # Extract agent ID from member
            agent_id = map_member_to_agent_id(event.member)
            
            # Create an agent failed event
            agent_event = AgentFailedEvent(
                agent_id=agent_id,
                error=f"Node failure: {event.metadata.get('failure_detection_method', 'unknown')}",
                source_node=event.source_node
            )
            
            # Forward to integration layer
            self.integration_layer.handle_agent_failed(agent_event)
            
        except Exception as e:
            logger.error(f"Error handling member failed event: {e}", exc_info=True)
    
    def _handle_member_suspected(self, event: MemberSuspectedEvent) -> None:
        """Handle a member suspected event."""
        # For suspected members, we might just log or take lighter action
        # since the node might recover
        agent_id = map_member_to_agent_id(event.member)
        logger.info(f"Agent {agent_id} is suspected of failure, monitoring...")
        
        # Optionally notify integration layer to mark as unreliable
        if hasattr(self.integration_layer, 'mark_agent_unreliable'):
            self.integration_layer.mark_agent_unreliable(agent_id)
    
    # Direct agent event handlers
    
    def _handle_agent_joined(self, event: AgentJoinedEvent) -> None:
        """Handle an agent joined event directly."""
        self.integration_layer.handle_agent_joined(event)
    
    def _handle_agent_left(self, event: AgentLeftEvent) -> None:
        """Handle an agent left event directly."""
        self.integration_layer.handle_agent_left(event)
    
    def _handle_agent_failed(self, event: AgentFailedEvent) -> None:
        """Handle an agent failed event directly."""
        self.integration_layer.handle_agent_failed(event)
    
    # Workflow event handlers
    
    def _handle_step_started(self, event: StepStartedEvent) -> None:
        """Handle a step started event."""
        self.integration_layer.handle_step_started(event)
    
    def _handle_step_completed(self, event: StepCompletedEvent) -> None:
        """Handle a step completed event."""
        self.integration_layer.handle_step_completed(event)
    
    def _handle_step_failed(self, event: StepFailedEvent) -> None:
        """Handle a step failed event."""
        self.integration_layer.handle_step_failed(event)
    
    def _handle_workflow_completed(self, event: WorkflowCompletedEvent) -> None:
        """Handle a workflow completed event."""
        self.integration_layer.handle_workflow_completed(event)
    
    # Resource event handlers
    
    def _handle_output_request(self, event: OutputRequestEvent) -> None:
        """Handle an output request event."""
        self.integration_layer.handle_output_request(event)
    
    def _handle_output_available(self, event: OutputAvailableEvent) -> None:
        """Handle an output available event."""
        self.integration_layer.handle_output_available(event)
    
    def _handle_output_received(self, event: OutputReceivedEvent) -> None:
        """Handle an output received event."""
        self.integration_layer.handle_output_received(event)
    
    def _handle_load_threshold(self, event: LoadThresholdEvent) -> None:
        """Handle a load threshold event."""
        self.integration_layer.handle_load_threshold(event)


def create_default_handlers(
    metrics_collector=None,
    enable_performance_alerts: bool = True,
    alert_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    integration_layer=None
) -> List[Callable[[Event], None]]:
    """
    Create a set of default event handlers.
    
    Args:
        metrics_collector: Optional metrics collector to use
        enable_performance_alerts: Whether to enable performance alerts
        alert_callback: Function to call when an alert is triggered
        integration_layer: Optional integration layer for ZMQ messaging
        
    Returns:
        List of event handler functions
    """
    handlers = []
    
    # Always add logging handler
    handlers.append(LoggingHandler())
    
    # Add metrics handler if collector is provided
    if metrics_collector:
        handlers.append(MetricsHandler(metrics_collector))
    
    # Add performance handler if enabled
    if enable_performance_alerts:
        handlers.append(PerformanceHandler(alert_callback))
    
    # Add integration handler if layer is provided
    if integration_layer:
        handlers.append(IntegrationHandler(integration_layer))
    
    return handlers


def register_default_handlers(
    dispatcher,
    metrics_collector=None,
    enable_performance_alerts: bool = True,
    alert_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    integration_layer=None
) -> Dict[str, List[Callable[[Event], None]]]:
    """
    Register default handlers with an event dispatcher.
    
    Args:
        dispatcher: The event dispatcher to register with
        metrics_collector: Optional metrics collector to use
        enable_performance_alerts: Whether to enable performance alerts
        alert_callback: Function to call when an alert is triggered
        integration_layer: Optional integration layer for ZMQ messaging
        
    Returns:
        Dictionary mapping event types to handlers
    """
    handlers = create_default_handlers(
        metrics_collector=metrics_collector,
        enable_performance_alerts=enable_performance_alerts,
        alert_callback=alert_callback,
        integration_layer=integration_layer
    )
    
    # Register all handlers for all events
    for handler in handlers:
        dispatcher.subscribe("*", handler)
    
    return {"*": handlers}