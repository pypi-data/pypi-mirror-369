"""
Dynamic timing adjustments for SWIM protocol.

This module implements the adaptive timing component of HashiCorp's Lifeguard
enhancements, which adjusts protocol timing parameters based on network conditions
to improve reliability and reduce false positives.
"""

import time
import threading
import logging
import statistics
from typing import Dict, List, Optional, Tuple, Callable

from swim.metrics.latency import LatencyTracker
from swim.lifeguard.awareness import AwarenessService, get_awareness_service

logger = logging.getLogger(__name__)

class TimingService:
    """
    Implements dynamic timing adjustments for the SWIM protocol.
    
    This service adjusts various timing parameters based on network conditions
    and node awareness to improve reliability and reduce false positives.
    """
    
    def __init__(
        self,
        latency_tracker: Optional[LatencyTracker] = None,
        awareness_service: Optional[AwarenessService] = None,
        metrics_collector = None
    ):
        """
        Initialize the timing service.
        
        Args:
            latency_tracker: Optional latency tracker to use for RTT-based adjustments
            awareness_service: Optional awareness service to use for reliability-based adjustments
            metrics_collector: Optional metrics collector to record timing metrics
        """
        # Components
        self._latency_tracker = latency_tracker
        self._awareness_service = awareness_service or get_awareness_service()
        self._metrics_collector = metrics_collector
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Base timing parameters
        self._base_protocol_period = 1.0  # seconds
        self._base_ping_timeout = 1.0  # seconds
        self._base_suspect_timeout = 5.0  # seconds
        
        # Adaptive timing ranges
        self._protocol_period_min = 0.5  # seconds
        self._protocol_period_max = 2.0  # seconds
        self._ping_timeout_min = 0.2  # seconds
        self._ping_timeout_max = 3.0  # seconds
        self._suspect_timeout_min = 2.0  # seconds
        self._suspect_timeout_max = 15.0  # seconds
        
        # Adjustment factors
        self._protocol_adjustment_factor = 0.1  # How quickly to adjust protocol period
        
        # History of timing values for learning
        self._timing_history: Dict[str, List[Tuple[float, float]]] = {
            "protocol_period": [],
            "ping_timeout": [],
            "suspect_timeout": []
        }
        
        # Current values
        self._current_protocol_period = self._base_protocol_period
        
        # Callbacks for timing changes
        self._callbacks: Dict[str, List[Callable]] = {
            "protocol_period": [],
            "ping_timeout": [],
            "suspect_timeout": []
        }
        
        logger.info("Timing service initialized with adaptive adjustments")
    
    def set_base_timing(
        self,
        protocol_period: Optional[float] = None,
        ping_timeout: Optional[float] = None,
        suspect_timeout: Optional[float] = None
    ) -> None:
        """
        Set the base timing parameters.
        
        Args:
            protocol_period: Base protocol period in seconds
            ping_timeout: Base ping timeout in seconds
            suspect_timeout: Base suspect timeout in seconds
        """
        with self._lock:
            if protocol_period is not None:
                self._base_protocol_period = protocol_period
                self._current_protocol_period = protocol_period
            
            if ping_timeout is not None:
                self._base_ping_timeout = ping_timeout
            
            if suspect_timeout is not None:
                self._base_suspect_timeout = suspect_timeout
            
            logger.info(f"Base timing updated: protocol={self._base_protocol_period}s, "
                      f"ping={self._base_ping_timeout}s, suspect={self._base_suspect_timeout}s")
    
    def set_timing_ranges(
        self,
        protocol_period_min: Optional[float] = None,
        protocol_period_max: Optional[float] = None,
        ping_timeout_min: Optional[float] = None,
        ping_timeout_max: Optional[float] = None,
        suspect_timeout_min: Optional[float] = None,
        suspect_timeout_max: Optional[float] = None
    ) -> None:
        """
        Set the allowed ranges for adaptive timing parameters.
        
        Args:
            protocol_period_min: Minimum protocol period in seconds
            protocol_period_max: Maximum protocol period in seconds
            ping_timeout_min: Minimum ping timeout in seconds
            ping_timeout_max: Maximum ping timeout in seconds
            suspect_timeout_min: Minimum suspect timeout in seconds
            suspect_timeout_max: Maximum suspect timeout in seconds
        """
        with self._lock:
            if protocol_period_min is not None:
                self._protocol_period_min = protocol_period_min
            
            if protocol_period_max is not None:
                self._protocol_period_max = protocol_period_max
            
            if ping_timeout_min is not None:
                self._ping_timeout_min = ping_timeout_min
            
            if ping_timeout_max is not None:
                self._ping_timeout_max = ping_timeout_max
            
            if suspect_timeout_min is not None:
                self._suspect_timeout_min = suspect_timeout_min
            
            if suspect_timeout_max is not None:
                self._suspect_timeout_max = suspect_timeout_max
            
            logger.info(f"Timing ranges updated: protocol=({self._protocol_period_min}s-{self._protocol_period_max}s), "
                      f"ping=({self._ping_timeout_min}s-{self._ping_timeout_max}s), "
                      f"suspect=({self._suspect_timeout_min}s-{self._suspect_timeout_max}s)")
    
    def register_callback(self, parameter: str, callback: Callable[[str, float], None]) -> None:
        """
        Register a callback to be notified when a timing parameter changes.
        
        Args:
            parameter: The parameter to watch ("protocol_period", "ping_timeout", "suspect_timeout")
            callback: Function to call with (parameter_name, new_value)
        """
        with self._lock:
            if parameter in self._callbacks:
                self._callbacks[parameter].append(callback)
    
    def _notify_callbacks(self, parameter: str, value: float) -> None:
        """
        Notify callbacks about a parameter change.
        
        Args:
            parameter: The parameter that changed
            value: The new value
        """
        if parameter in self._callbacks:
            for callback in self._callbacks[parameter]:
                try:
                    callback(parameter, value)
                except Exception as e:
                    logger.error(f"Error in timing callback: {e}")
    
    def get_protocol_period(self, network_conditions: Optional[Dict[str, any]] = None) -> float:
        """
        Get the current protocol period, adjusted for network conditions.
        
        The protocol period is the time between protocol cycles (heartbeats, probes).
        It is adjusted based on overall network conditions:
        - Slower networks -> longer period to reduce overhead
        - Faster networks -> shorter period for quicker failure detection
        
        Args:
            network_conditions: Optional network condition info to use for adjustment
            
        Returns:
            Adjusted protocol period in seconds
        """
        with self._lock:
            # Use current value if we don't have a latency tracker or network conditions
            if self._latency_tracker is None and network_conditions is None:
                return self._current_protocol_period
            
            # Start with current protocol period
            period = self._current_protocol_period
            
            # Get network health if available
            if self._latency_tracker is not None:
                health = self._latency_tracker.get_network_health()
                
                # Adjust based on network health
                if health.get("status") == "degrading":
                    # Network is degrading, increase period to reduce overhead
                    old_period = period
                    period = period * (1 + self._protocol_adjustment_factor)
                    logger.info(f"LIFEGUARD: Increasing protocol period due to degrading network: {old_period:.2f}s -> {period:.2f}s")
                elif health.get("status") == "healthy" and health.get("active_peers", 0) > 0:
                    # Network is healthy, decrease period for faster failure detection
                    old_period = period
                    period = period * (1 - self._protocol_adjustment_factor * 0.5)
                    logger.info(f"LIFEGUARD: Decreasing protocol period due to healthy network: {old_period:.2f}s -> {period:.2f}s")
            
            # Apply manual network conditions if provided
            if network_conditions is not None:
                if network_conditions.get("congested", False):
                    # Network is congested, increase period
                    old_period = period
                    period = period * (1 + self._protocol_adjustment_factor)
                    logger.info(f"LIFEGUARD: Increasing protocol period due to congestion: {old_period:.2f}s -> {period:.2f}s")
                
                if network_conditions.get("failure_rate", 0) > 0.1:
                    # High failure rate, increase period
                    old_period = period
                    period = period * (1 + self._protocol_adjustment_factor)
                    logger.info(f"LIFEGUARD: Increasing protocol period due to high failure rate: {old_period:.2f}s -> {period:.2f}s")
            
            # Ensure period is within bounds
            period = max(self._protocol_period_min, min(self._protocol_period_max, period))
            
            # Only update if different enough
            if abs(period - self._current_protocol_period) > 0.05:
                old_period = self._current_protocol_period
                self._current_protocol_period = period
                
                # Add to history
                self._timing_history["protocol_period"].append((time.time(), period))
                if len(self._timing_history["protocol_period"]) > 100:
                    self._timing_history["protocol_period"] = self._timing_history["protocol_period"][-100:]
                
                # Notify callbacks
                self._notify_callbacks("protocol_period", period)
                
                # Record metric if available
                if self._metrics_collector:
                    self._metrics_collector.record_gauge(
                        name="protocol_period",
                        value=period
                    )
                
                logger.info(f"LIFEGUARD: Protocol period adjusted: {old_period:.2f}s -> {period:.2f}s")
            
            return period
    
    def get_ping_timeout(self, peer_id: Optional[str] = None) -> float:
        """
        Get the ping timeout for a specific peer, adjusted for network conditions.
        
        The ping timeout is adjusted based on:
        - Historical RTT to the peer (if available)
        - Awareness value of the peer (less reliable peers get longer timeouts)
        
        Args:
            peer_id: Optional identifier of the peer
            
        Returns:
            Adjusted ping timeout in seconds
        """
        with self._lock:
            # Start with base timeout
            timeout = self._base_ping_timeout
            
            # Adjust based on latency if we have a tracker and peer_id
            if self._latency_tracker is not None and peer_id is not None:
                timeout = self._latency_tracker.get_adaptive_timeout(peer_id)
                
                # Record the derived timeout
                self._timing_history["ping_timeout"].append((time.time(), timeout))
                if len(self._timing_history["ping_timeout"]) > 100:
                    self._timing_history["ping_timeout"] = self._timing_history["ping_timeout"][-100:]
            
            # Ensure timeout is within bounds
            timeout = max(self._ping_timeout_min, min(self._ping_timeout_max, timeout))
            
            # Record metric if available
            if self._metrics_collector and peer_id is not None:
                self._metrics_collector.record_gauge(
                    name="ping_timeout",
                    value=timeout,
                    labels={"peer_id": peer_id}
                )
            
            return timeout
    
    def get_suspect_timeout(self, peer_id: Optional[str] = None) -> float:
        """
        Get the suspect timeout for a specific peer, adjusted for reliability.
        
        The suspect timeout is adjusted based on:
        - Awareness value of the peer (less reliable peers get longer timeouts)
        - Overall network health
        
        Args:
            peer_id: Optional identifier of the peer
            
        Returns:
            Adjusted suspect timeout in seconds
        """
        with self._lock:
            # Start with base timeout
            timeout = self._base_suspect_timeout
            
            # Adjust based on awareness if we have a peer_id
            if peer_id is not None and self._awareness_service is not None:
                # Get multiplier based on awareness (lower awareness = higher multiplier)
                multiplier = self._awareness_service.get_suspicion_multiplier(peer_id)
                timeout = timeout * multiplier
            
            # Ensure timeout is within bounds
            timeout = max(self._suspect_timeout_min, min(self._suspect_timeout_max, timeout))
            
            # Record the derived timeout
            self._timing_history["suspect_timeout"].append((time.time(), timeout))
            if len(self._timing_history["suspect_timeout"]) > 100:
                self._timing_history["suspect_timeout"] = self._timing_history["suspect_timeout"][-100:]
            
            # Record metric if available
            if self._metrics_collector and peer_id is not None:
                self._metrics_collector.record_gauge(
                    name="suspect_timeout",
                    value=timeout,
                    labels={"peer_id": peer_id}
                )
            
            return timeout
    
    def get_timing_stats(self) -> Dict[str, any]:
        """
        Get statistics about timing adjustments.
        
        Returns:
            Dictionary with timing statistics
        """
        with self._lock:
            stats = {
                "current_protocol_period": self._current_protocol_period,
                "base_protocol_period": self._base_protocol_period,
                "base_ping_timeout": self._base_ping_timeout,
                "base_suspect_timeout": self._base_suspect_timeout
            }
            
            # Calculate statistics for each parameter
            for param, history in self._timing_history.items():
                if not history:
                    continue
                
                values = [value for _, value in history]
                
                param_stats = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values) if values else 0,
                    "current": values[-1] if values else 0
                }
                
                if len(values) > 1:
                    param_stats["stdev"] = statistics.stdev(values)
                
                stats[param] = param_stats
            
            return stats


# Initialize a global instance for easy import
default_timing_service = None

def get_timing_service(
    latency_tracker: Optional[LatencyTracker] = None,
    awareness_service: Optional[AwarenessService] = None,
    metrics_collector = None
) -> TimingService:
    """
    Get or create the default timing service.
    
    Args:
        latency_tracker: Optional latency tracker
        awareness_service: Optional awareness service
        metrics_collector: Optional metrics collector
        
    Returns:
        The default timing service instance
    """
    global default_timing_service
    
    if default_timing_service is None:
        default_timing_service = TimingService(
            latency_tracker=latency_tracker,
            awareness_service=awareness_service,
            metrics_collector=metrics_collector
        )
    
    return default_timing_service