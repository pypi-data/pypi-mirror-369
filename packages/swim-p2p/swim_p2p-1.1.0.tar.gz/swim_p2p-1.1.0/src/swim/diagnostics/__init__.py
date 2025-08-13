"""
Diagnostics Package for SWIM P2P Integration.

This package provides tools for comprehensive diagnostics, including:
- Message path tracing and visualization.
- End-to-end health monitoring.
- Performance bottleneck detection.
"""

from .message_tracer import MessageTracer, TraceContext, MessageTraceRecord
from .health_checker import HealthChecker
from .performance_analyzer import PerformanceAnalyzer

__all__ = [
    "MessageTracer",
    "TraceContext",
    "MessageTraceRecord",
    "HealthChecker",
    "PerformanceAnalyzer",
]

logger = logging.getLogger(__name__)
logger.info("DIAGNOSTICS: Package initialized.")