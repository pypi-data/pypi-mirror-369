"""
Metrics API for SWIM P2P protocol.

This package provides an API for querying metrics from SWIM P2P protocol nodes.
"""

from swim.metrics.api.server import app, set_local_node, start_server, start_server_in_thread
from swim.metrics.api.client import MetricsAPIClient
from swim.metrics.api.integration import MetricsAPIIntegration, setup_metrics_api

__all__ = [
    "app",
    "set_local_node",
    "start_server",
    "start_server_in_thread",
    "MetricsAPIClient",
    "MetricsAPIIntegration",
    "setup_metrics_api"
]
