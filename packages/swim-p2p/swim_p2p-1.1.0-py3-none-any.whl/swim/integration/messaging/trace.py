"""
Distributed tracing utilities for SWIM-ZMQ integration.

Provides mechanisms to generate, propagate, and log trace context
across services and message hops.
"""

import uuid
import time
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field

# Attempt to import MessageTracer from diagnostics, will be None if not available yet
try:
    from swim.diagnostics.message_tracer import MessageTracer, TraceContext as DiagnosticTraceContext
except ImportError:
    MessageTracer = None
    DiagnosticTraceContext = None # type: ignore

logger = logging.getLogger(__name__)

# If DiagnosticTraceContext is not available, define a local one
if DiagnosticTraceContext is None:
    @dataclass
    class TraceContext:
        """Represents the context for a distributed trace."""
        trace_id: str
        span_id: str
        parent_span_id: Optional[str] = None
        sampled: bool = True # Add sampling decision
        baggage: Dict[str, str] = field(default_factory=dict) # For additional context

        def __str__(self):
            return f"Trace(tid={self.trace_id}, sid={self.span_id}, psid={self.parent_span_id})"
else:
    TraceContext = DiagnosticTraceContext # type: ignore


_message_tracer_instance: Optional[MessageTracer] = None

def set_message_tracer(tracer: MessageTracer):
    """Sets the global message tracer instance."""
    global _message_tracer_instance
    _message_tracer_instance = tracer
    logger.info("TRACE: Global MessageTracer instance configured.")

def _generate_id() -> str:
    """Generates a unique ID for trace or span."""
    return uuid.uuid4().hex[:16] # Shorter ID for readability

def start_trace(service_name: str, operation_name: str) -> TraceContext:
    """
    Starts a new distributed trace.

    Args:
        service_name: Name of the service initiating the trace.
        operation_name: Name of the initial operation.

    Returns:
        A new TraceContext.
    """
    trace_id = _generate_id()
    span_id = _generate_id()
    context = TraceContext(trace_id=trace_id, span_id=span_id)
    logger.info(f"TRACE_START: New trace started. Context: {context}, Service: {service_name}, Operation: {operation_name}")
    if _message_tracer_instance:
        _message_tracer_instance.record_event(context, service_name, operation_name, {"event": "trace_start"})
    return context

def start_span(existing_context: TraceContext, service_name: str, operation_name: str) -> TraceContext:
    """
    Starts a new span within an existing trace.

    Args:
        existing_context: The current TraceContext (from which to derive parent).
        service_name: Name of the service for this span.
        operation_name: Name of the operation for this span.

    Returns:
        A new TraceContext for the child span.
    """
    if not existing_context.sampled: # Do not create child spans for non-sampled traces
        return existing_context

    new_span_id = _generate_id()
    child_context = TraceContext(
        trace_id=existing_context.trace_id,
        span_id=new_span_id,
        parent_span_id=existing_context.span_id,
        sampled=existing_context.sampled,
        baggage=existing_context.baggage.copy() # Propagate baggage
    )
    logger.info(f"TRACE_SPAN_START: New span started. Context: {child_context}, Parent: {existing_context.span_id}, Service: {service_name}, Operation: {operation_name}")
    if _message_tracer_instance:
        _message_tracer_instance.record_event(child_context, service_name, operation_name, {"event": "span_start"})
    return child_context

def inject_context(message_payload: Dict[str, Any], trace_context: Optional[TraceContext]) -> Dict[str, Any]:
    """
    Injects trace context into a message payload.

    Args:
        message_payload: The original message payload dictionary.
        trace_context: The TraceContext to inject.

    Returns:
        The message payload dictionary with trace context added.
    """
    if trace_context and trace_context.sampled:
        if 'headers' not in message_payload:
            message_payload['headers'] = {}
        message_payload['headers']['X-Trace-ID'] = trace_context.trace_id
        message_payload['headers']['X-Span-ID'] = trace_context.span_id
        if trace_context.parent_span_id:
            message_payload['headers']['X-Parent-Span-ID'] = trace_context.parent_span_id
        if trace_context.baggage:
            message_payload['headers']['X-Trace-Baggage'] = trace_context.baggage
        logger.debug(f"TRACE_INJECT: Injected trace context {trace_context} into message.")
    return message_payload

def extract_context(message_payload: Dict[str, Any]) -> Optional[TraceContext]:
    """
    Extracts trace context from a message payload.

    Args:
        message_payload: The message payload dictionary.

    Returns:
        A TraceContext if found, otherwise None.
    """
    headers = message_payload.get('headers', {})
    trace_id = headers.get('X-Trace-ID')
    span_id = headers.get('X-Span-ID')

    if trace_id and span_id:
        context = TraceContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=headers.get('X-Parent-Span-ID'),
            sampled=True, # Assume sampled if headers are present
            baggage=headers.get('X-Trace-Baggage', {})
        )
        logger.debug(f"TRACE_EXTRACT: Extracted trace context {context} from message.")
        return context
    logger.debug("TRACE_EXTRACT: No trace context found in message.")
    return None

def log_trace_event(trace_context: Optional[TraceContext], service_name: str, event_name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    Logs a specific event within a trace.

    Args:
        trace_context: The current TraceContext.
        service_name: Name of the service logging the event.
        event_name: A descriptive name for the event (e.g., "message_sent", "db_query_start").
        attributes: Optional dictionary of key-value attributes for the event.
    """
    if trace_context and trace_context.sampled:
        full_attributes = attributes or {}
        full_attributes["event_time_ms"] = int(time.time() * 1000)
        logger.info(f"TRACE_EVENT: Context: {trace_context}, Service: {service_name}, Event: {event_name}, Attrs: {full_attributes}")
        if _message_tracer_instance:
            _message_tracer_instance.record_event(trace_context, service_name, event_name, full_attributes)
    elif not trace_context:
        logger.debug(f"TRACE_EVENT_SKIP: No trace context. Service: {service_name}, Event: {event_name}")
    # else: (trace_context exists but not sampled)
    #   logger.debug(f"TRACE_EVENT_SKIP: Trace not sampled. Context: {trace_context}, Service: {service_name}, Event: {event_name}")

def end_span(trace_context: Optional[TraceContext], service_name: str, operation_name: str, error: Optional[Exception] = None):
    """
    Ends a span, typically called after an operation completes.

    Args:
        trace_context: The TraceContext of the span to end.
        service_name: Name of the service where the span ends.
        operation_name: Name of the operation that the span covered.
        error: Optional exception if the operation failed.
    """
    if trace_context and trace_context.sampled:
        attributes = {"event": "span_end"}
        if error:
            attributes["error"] = True
            attributes["error.message"] = str(error)
            attributes["error.type"] = type(error).__name__
        logger.info(f"TRACE_SPAN_END: Context: {trace_context}, Service: {service_name}, Operation: {operation_name}, Error: {error is not None}")
        if _message_tracer_instance:
            _message_tracer_instance.record_event(trace_context, service_name, operation_name, attributes)