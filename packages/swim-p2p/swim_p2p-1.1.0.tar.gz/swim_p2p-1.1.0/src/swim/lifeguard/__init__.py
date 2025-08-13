"""
Lifeguard enhancements for SWIM protocol.

This package implements the HashiCorp Lifeguard enhancements to the SWIM protocol,
which improves reliability and reduces false positives in failure detection.

The enhancements include:
1. Network awareness - Tracks the reliability of each node
2. Dynamic timing - Adjusts protocol timing based on network conditions
3. Adaptive probing - Controls the rate and intensity of probing
"""

from swim.lifeguard.awareness import AwarenessService, get_awareness_service
from swim.lifeguard.timing import TimingService, get_timing_service
from swim.lifeguard.probe_rate import ProbeRateService, get_probe_rate_service

__all__ = [
    'AwarenessService', 
    'get_awareness_service',
    'TimingService', 
    'get_timing_service',
    'ProbeRateService', 
    'get_probe_rate_service'
]

# Initialize and configure services
def initialize_lifeguard(
    metrics_collector=None, 
    latency_tracker=None,
    bandwidth_monitor=None
):
    """
    Initialize and connect all Lifeguard enhancement services.
    
    Args:
        metrics_collector: Optional metrics collector for recording metrics
        latency_tracker: Optional latency tracker for RTT measurements
        bandwidth_monitor: Optional bandwidth monitor for rate control
        
    Returns:
        Tuple of (awareness_service, timing_service, probe_rate_service)
    """
    # Initialize services in dependency order
    awareness_service = get_awareness_service(
        metrics_collector=metrics_collector
    )
    
    timing_service = get_timing_service(
        latency_tracker=latency_tracker,
        awareness_service=awareness_service,
        metrics_collector=metrics_collector
    )
    
    probe_rate_service = get_probe_rate_service(
        latency_tracker=latency_tracker,
        bandwidth_monitor=bandwidth_monitor,
        awareness_service=awareness_service,
        timing_service=timing_service,
        metrics_collector=metrics_collector
    )
    
    return (awareness_service, timing_service, probe_rate_service)

print("Lifeguard enhancement module loaded")