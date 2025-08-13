"""
Message path tracing and visualization for SWIM-ZMQ integration.

Collects trace events for messages to reconstruct their path and interactions
across different services and components.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field
import asyncio # For RLock if used in async context

logger = logging.getLogger(__name__)

@dataclass
class TraceContext: # Duplicating here for standalone use if messaging.trace is not ready
    """Represents the context for a distributed trace."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    sampled: bool = True
    baggage: Dict[str, str] = field(default_factory=dict)

    def __str__(self):
        return f"Trace(tid={self.trace_id}, sid={self.span_id}, psid={self.parent_span_id})"

@dataclass
class MessageTraceEvent:
    """Represents a single event in a message's trace."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    service_name: str  # e.g., "ReliabilityManager", "WorkflowEngine", "ZMQ_Receiver"
    event_name: str    # e.g., "message_sent", "ack_received", "processing_started"
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    attributes: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None # Optional duration for timed events

class MessageTracer:
    """
    Collects and stores trace events for messages.
    """
    def __init__(self, max_traces: int = 1000, max_events_per_trace: int = 100):
        """
        Initialize the MessageTracer.

        Args:
            max_traces: Maximum number of recent traces to keep in memory.
            max_events_per_trace: Maximum number of events to store for a single trace.
        """
        self._traces: Dict[str, List[MessageTraceEvent]] = {} # trace_id -> list of events
        self._trace_timestamps: Dict[str, float] = {} # trace_id -> last_event_timestamp
        self._max_traces = max_traces
        self._max_events_per_trace = max_events_per_trace
        self._lock = asyncio.Lock() # Use asyncio.Lock if called from async code

        # For removing oldest traces when max_traces is hit
        self._trace_lru_order: List[str] = []

        logger.info(f"MSG_TRACER: Initialized. Max traces: {max_traces}, Max events/trace: {max_events_per_trace}")

    async def record_event(self,
                           trace_context: TraceContext,
                           service_name: str,
                           event_name: str,
                           attributes: Optional[Dict[str, Any]] = None,
                           duration_ms: Optional[float] = None) -> None:
        """
        Records a new event for a given trace context.

        Args:
            trace_context: The TraceContext of the message/operation.
            service_name: The name of the service or component emitting the event.
            event_name: A descriptive name for the event.
            attributes: Optional key-value attributes associated with the event.
            duration_ms: Optional duration if this event marks the end of a timed operation.
        """
        if not trace_context.sampled:
            # logger.debug(f"MSG_TRACER_SKIP_UNSAMPLED: Trace {trace_context.trace_id} not sampled. Event: {service_name}/{event_name}")
            return

        async with self._lock:
            trace_id = trace_context.trace_id
            now = time.time()

            event = MessageTraceEvent(
                trace_id=trace_id,
                span_id=trace_context.span_id,
                parent_span_id=trace_context.parent_span_id,
                service_name=service_name,
                event_name=event_name,
                attributes=attributes or {},
                duration_ms=duration_ms
            )

            if trace_id not in self._traces:
                if len(self._traces) >= self._max_traces:
                    # Remove the oldest trace (Least Recently Updated might be better than LRU added)
                    if self._trace_lru_order:
                        oldest_trace_id = self._trace_lru_order.pop(0)
                        if oldest_trace_id in self._traces:
                            del self._traces[oldest_trace_id]
                        if oldest_trace_id in self._trace_timestamps:
                            del self._trace_timestamps[oldest_trace_id]
                        logger.info(f"MSG_TRACER_EVICT_OLD: Evicted trace {oldest_trace_id} due to max_traces limit.")

                self._traces[trace_id] = []
                self._trace_lru_order.append(trace_id)

            if len(self._traces[trace_id]) < self._max_events_per_trace:
                self._traces[trace_id].append(event)
                self._trace_timestamps[trace_id] = now # Update last activity time
                # If trace was removed from LRU and re-added, ensure it's at the end
                if trace_id in self._trace_lru_order:
                    self._trace_lru_order.remove(trace_id)
                self._trace_lru_order.append(trace_id)

                logger.debug(f"MSG_TRACER_EVENT: Recorded event for trace {trace_id}, span {event.span_id}. "
                            f"Service: {service_name}, Event: {event_name}. Total events for trace: {len(self._traces[trace_id])}")
            else:
                logger.warning(f"MSG_TRACER_MAX_EVENTS: Trace {trace_id} reached max events ({self._max_events_per_trace}). "
                               f"Event '{event_name}' for service '{service_name}' not recorded.")

    async def get_trace(self, trace_id: str) -> Optional[List[MessageTraceEvent]]:
        """
        Retrieves all recorded events for a specific trace ID.

        Args:
            trace_id: The ID of the trace to retrieve.

        Returns:
            A list of MessageTraceEvent objects, or None if the trace is not found.
            The events are typically in the order they were recorded.
        """
        async with self._lock:
            trace_events = self._traces.get(trace_id)
            if trace_events:
                logger.info(f"MSG_TRACER_GET: Retrieved {len(trace_events)} events for trace {trace_id}.")
                # Return a copy to prevent modification
                return list(trace_events)
            else:
                logger.info(f"MSG_TRACER_GET_NOT_FOUND: Trace {trace_id} not found.")
                return None

    async def get_all_trace_ids(self) -> List[str]:
        """Returns a list of all currently stored trace IDs."""
        async with self._lock:
            return list(self._traces.keys())

    async def cleanup_old_traces(self, max_age_seconds: int = 3600) -> int:
        """
        Removes traces older than a specified age.

        Args:
            max_age_seconds: Maximum age of a trace (based on last event) in seconds.

        Returns:
            The number of traces cleaned up.
        """
        async with self._lock:
            now = time.time()
            cleaned_count = 0
            traces_to_remove = [
                tid for tid, ts in self._trace_timestamps.items()
                if (now - ts) > max_age_seconds
            ]

            for tid in traces_to_remove:
                if tid in self._traces:
                    del self._traces[tid]
                if tid in self._trace_timestamps:
                    del self._trace_timestamps[tid]
                if tid in self._trace_lru_order:
                    self._trace_lru_order.remove(tid)
                cleaned_count += 1
            if cleaned_count > 0:
                logger.info(f"MSG_TRACER_CLEANUP: Cleaned up {cleaned_count} old traces (older than {max_age_seconds}s).")
            return cleaned_count

    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the MessageTracer."""
        return {
            "total_traces_stored": len(self._traces),
            "max_traces_limit": self._max_traces,
            "max_events_per_trace_limit": self._max_events_per_trace,
            "total_events_stored": sum(len(events) for events in self._traces.values())
        }