"""
Adaptive probing rate control for SWIM protocol.

This module implements the adaptive probing component of HashiCorp's Lifeguard
enhancements, which adjusts the frequency and intensity of probing based on
node awareness and network conditions.
"""

import time
import threading
import logging
import random
from typing import Dict, List, Optional, Set, Tuple, Callable

from swim.metrics.latency import LatencyTracker
from swim.metrics.bandwidth import BandwidthMonitor, Direction
from swim.lifeguard.awareness import AwarenessService, get_awareness_service
from swim.lifeguard.timing import TimingService, get_timing_service

logger = logging.getLogger(__name__)

class ProbeRateService:
    """
    Implements adaptive probing rate control for the SWIM protocol.
    
    This service adjusts the rate and intensity of probing based on
    network conditions and node awareness to improve reliability
    while controlling bandwidth usage.
    """
    
    def __init__(
        self,
        latency_tracker: Optional[LatencyTracker] = None,
        bandwidth_monitor: Optional[BandwidthMonitor] = None,
        awareness_service: Optional[AwarenessService] = None,
        timing_service: Optional[TimingService] = None,
        metrics_collector = None
    ):
        """
        Initialize the probe rate service.
        
        Args:
            latency_tracker: Optional latency tracker for network condition monitoring
            bandwidth_monitor: Optional bandwidth monitor for rate control
            awareness_service: Optional awareness service for reliability-based adjustments
            timing_service: Optional timing service for coordination
            metrics_collector: Optional metrics collector to record probing metrics
        """
        # Components
        self._latency_tracker = latency_tracker
        self._bandwidth_monitor = bandwidth_monitor
        self._awareness_service = awareness_service or get_awareness_service()
        self._timing_service = timing_service or get_timing_service()
        self._metrics_collector = metrics_collector
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Base probing parameters
        self._base_probe_count = 3  # Default indirect probe count
        self._base_probe_interval = 1.0  # seconds between probes
        
        # Adaptive ranges
        self._probe_count_min = 2
        self._probe_count_max = 8
        self._probe_interval_min = 0.5  # seconds
        self._probe_interval_max = 3.0  # seconds
        
        # Bandwidth control
        self._bandwidth_limit_enabled = False
        self._bandwidth_threshold = 100000  # bytes per second (100KB/s)
        
        # Prioritization
        self._priority_peers: Set[str] = set()  # High-priority peers to probe more frequently
        self._blacklist_peers: Set[str] = set()  # Temporary blacklist for problematic peers
        self._blacklist_timeout = 60.0  # seconds to keep peers on blacklist
        self._blacklist_timestamps: Dict[str, float] = {}  # When peers were blacklisted
        
        # Probing history for learning
        self._probe_history: Dict[str, List[Tuple[float, bool]]] = {}  # peer_id -> [(timestamp, success)]
        
        # Callbacks for probe rate changes
        self._rate_callbacks: List[Callable[[str, float], None]] = []
        
        logger.info("Probe rate service initialized with adaptive control")
    
    def set_base_parameters(
        self,
        probe_count: Optional[int] = None,
        probe_interval: Optional[float] = None,
    ) -> None:
        """
        Set the base probing parameters.
        
        Args:
            probe_count: Base number of indirect probes
            probe_interval: Base interval between probes in seconds
        """
        with self._lock:
            if probe_count is not None:
                self._base_probe_count = probe_count
            
            if probe_interval is not None:
                self._base_probe_interval = probe_interval
            
            logger.info(f"Base probing parameters updated: count={self._base_probe_count}, "
                      f"interval={self._base_probe_interval}s")
    
    def set_probing_ranges(
        self,
        probe_count_min: Optional[int] = None,
        probe_count_max: Optional[int] = None,
        probe_interval_min: Optional[float] = None,
        probe_interval_max: Optional[float] = None
    ) -> None:
        """
        Set the allowed ranges for adaptive probing parameters.
        
        Args:
            probe_count_min: Minimum number of indirect probes
            probe_count_max: Maximum number of indirect probes
            probe_interval_min: Minimum interval between probes in seconds
            probe_interval_max: Maximum interval between probes in seconds
        """
        with self._lock:
            if probe_count_min is not None:
                self._probe_count_min = probe_count_min
            
            if probe_count_max is not None:
                self._probe_count_max = probe_count_max
            
            if probe_interval_min is not None:
                self._probe_interval_min = probe_interval_min
            
            if probe_interval_max is not None:
                self._probe_interval_max = probe_interval_max
            
            logger.info(f"Probing ranges updated: count=({self._probe_count_min}-{self._probe_count_max}), "
                      f"interval=({self._probe_interval_min}s-{self._probe_interval_max}s)")
    
    def set_bandwidth_control(self, enabled: bool, threshold: Optional[int] = None) -> None:
        """
        Configure bandwidth control for probing.
        
        Args:
            enabled: Whether to enable bandwidth-based rate control
            threshold: Bandwidth threshold in bytes per second
        """
        with self._lock:
            self._bandwidth_limit_enabled = enabled
            
            if threshold is not None:
                self._bandwidth_threshold = threshold
            
            logger.info(f"Bandwidth control: enabled={enabled}, threshold={self._bandwidth_threshold} B/s")
    
    def register_rate_callback(self, callback: Callable[[str, float], None]) -> None:
        """
        Register a callback to be notified when the probe rate changes.
        
        Args:
            callback: Function to call with (peer_id, new_rate)
        """
        with self._lock:
            self._rate_callbacks.append(callback)
    
    def _notify_rate_callbacks(self, peer_id: str, rate: float) -> None:
        """
        Notify callbacks about a rate change.
        
        Args:
            peer_id: Identifier of the peer
            rate: New probe rate (probes per second)
        """
        for callback in self._rate_callbacks:
            try:
                callback(peer_id, rate)
            except Exception as e:
                logger.error(f"Error in probe rate callback: {e}")
    
    def add_priority_peer(self, peer_id: str) -> None:
        """
        Add a peer to the high-priority list.
        
        High-priority peers are probed more frequently and with more helpers.
        
        Args:
            peer_id: Identifier of the peer
        """
        with self._lock:
            self._priority_peers.add(peer_id)
            logger.debug(f"Added {peer_id} to priority peers list")
    
    def remove_priority_peer(self, peer_id: str) -> None:
        """
        Remove a peer from the high-priority list.
        
        Args:
            peer_id: Identifier of the peer
        """
        with self._lock:
            self._priority_peers.discard(peer_id)
            logger.debug(f"Removed {peer_id} from priority peers list")
    
    def blacklist_peer(self, peer_id: str, duration: Optional[float] = None) -> None:
        """
        Temporarily blacklist a peer from being probed.
        
        Args:
            peer_id: Identifier of the peer
            duration: Optional custom blacklist duration in seconds
        """
        with self._lock:
            self._blacklist_peers.add(peer_id)
            self._blacklist_timestamps[peer_id] = time.time()
            
            timeout = duration if duration is not None else self._blacklist_timeout
            logger.info(f"Blacklisted {peer_id} for {timeout}s")
            
            # Record metric if available
            if self._metrics_collector:
                self._metrics_collector.record_event(
                    name="peer_blacklisted",
                    value=timeout,
                    labels={"peer_id": peer_id}
                )
    
    def is_blacklisted(self, peer_id: str) -> bool:
        """
        Check if a peer is currently blacklisted.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            True if the peer is blacklisted, False otherwise
        """
        with self._lock:
            if peer_id not in self._blacklist_peers:
                return False
            
            # Check if blacklist has expired
            timestamp = self._blacklist_timestamps.get(peer_id, 0)
            if time.time() - timestamp > self._blacklist_timeout:
                # Remove from blacklist
                self._blacklist_peers.discard(peer_id)
                self._blacklist_timestamps.pop(peer_id, None)
                return False
            
            return True
    
    def record_probe_result(self, peer_id: str, success: bool) -> None:
        """
        Record the result of a probe operation.
        
        This is used to learn about the reliability of different peers
        and adjust probing parameters accordingly.
        
        Args:
            peer_id: Identifier of the peer
            success: Whether the probe was successful
        """
        with self._lock:
            if peer_id not in self._probe_history:
                self._probe_history[peer_id] = []
            
            self._probe_history[peer_id].append((time.time(), success))
            
            # Trim history to last 50 entries
            if len(self._probe_history[peer_id]) > 50:
                self._probe_history[peer_id] = self._probe_history[peer_id][-50:]
            
            # Update awareness based on probe result
            if self._awareness_service:
                if success:
                    self._awareness_service.record_success(peer_id)
                else:
                    self._awareness_service.record_failure(peer_id)
            
            # Record metric if available
            if self._metrics_collector:
                self._metrics_collector.record_counter(
                    name="probe_result",
                    value=1,
                    labels={"peer_id": peer_id, "success": str(success)}
                )
    
    def get_probe_count(self, peer_id: str) -> int:
        """
        Get the number of indirect probes to use for a specific peer.
        
        The number of probes is adjusted based on:
        - Awareness value of the peer (lower awareness = more probes)
        - Priority status (high priority = more probes)
        - Bandwidth availability
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            Number of indirect probes to use
        """
        with self._lock:
            # Start with base probe count
            count = self._base_probe_count
            
            # Don't probe blacklisted peers
            if self.is_blacklisted(peer_id):
                return 0
            
            # Adjust based on awareness
            if self._awareness_service:
                # Delegate to awareness service which has the logic for this
                awareness = self._awareness_service.get_awareness(peer_id)
                count = self._awareness_service.get_probe_count(peer_id)
                logger.info(f"LIFEGUARD: Probe count for {peer_id} (awareness={awareness}): {count}")
            
            # Increase count for priority peers
            if peer_id in self._priority_peers:
                old_count = count
                count += 1
                logger.info(f"LIFEGUARD: Increased probe count for priority peer {peer_id}: {old_count} -> {count}")
            
            # Check probe history for recent failures
            if peer_id in self._probe_history:
                recent = [success for ts, success in self._probe_history[peer_id]
                        if time.time() - ts < 60]  # Last minute
                
                if recent:
                    failure_rate = sum(1 for s in recent if not s) / len(recent)
                    
                    # Increase count if high failure rate
                    if failure_rate > 0.5:  # More than 50% failures
                        old_count = count
                        count += 1
                        logger.info(f"LIFEGUARD: Increased probe count due to high failure rate ({failure_rate:.1%}) for {peer_id}: {old_count} -> {count}")
            
            # Reduce count if bandwidth is limited
            if self._bandwidth_limit_enabled and self._bandwidth_monitor:
                current_rate = self._bandwidth_monitor.get_current_rate(Direction.OUTBOUND)
                
                if current_rate > self._bandwidth_threshold:
                    # Scale down proportionally to how much we're over the threshold
                    reduction = int(min(count - self._probe_count_min,
                                    (current_rate / self._bandwidth_threshold - 1) * count))
                    
                    if reduction > 0:
                        old_count = count
                        count -= reduction
                        logger.info(f"LIFEGUARD: Reducing probe count due to bandwidth limit for {peer_id}: {old_count} -> {count}")
            
            # Ensure count is within bounds
            count = max(self._probe_count_min, min(self._probe_count_max, count))
            
            # Record metric if available
            if self._metrics_collector:
                self._metrics_collector.record_gauge(
                    name="probe_count",
                    value=count,
                    labels={"peer_id": peer_id}
                )
            
            return count
    
    def get_probe_interval(self, peer_id: str) -> float:
        """
        Get the interval between probes for a specific peer.
        
        The interval is adjusted based on:
        - Awareness value of the peer (higher awareness = longer interval)
        - Priority status (high priority = shorter interval)
        - Bandwidth availability
        - Network conditions
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            Interval between probes in seconds
        """
        with self._lock:
            # Start with base interval
            interval = self._base_probe_interval
            
            # Don't probe blacklisted peers
            if self.is_blacklisted(peer_id):
                return float('inf')  # Infinite interval = don't probe
            
            # Adjust based on awareness
            if self._awareness_service:
                awareness = self._awareness_service.get_awareness(peer_id)
                
                # Higher awareness = longer interval (less frequent probing)
                # Formula: interval *= (awareness + 1) / (max_awareness / 2 + 1)
                max_awareness = 8  # Default max awareness
                interval *= (awareness + 1) / (max_awareness / 2 + 1)
            
            # Shorter interval for priority peers
            if peer_id in self._priority_peers:
                interval *= 0.8  # 20% shorter interval
            
            # Adjust based on RTT if available
            if self._latency_tracker:
                stats = self._latency_tracker.get_rtt_stats(peer_id)
                
                if stats:
                    # Higher RTT = longer interval to avoid overloading
                    rtt = stats.get("mean", 0)
                    if rtt > 0:
                        # Scale interval by RTT, but don't extend too much
                        # Formula: interval = max(interval, min(rtt * 2, interval * 1.5))
                        interval = max(interval, min(rtt * 2, interval * 1.5))
            
            # Increase interval if bandwidth is limited
            if self._bandwidth_limit_enabled and self._bandwidth_monitor:
                current_rate = self._bandwidth_monitor.get_current_rate(Direction.OUTBOUND)
                
                if current_rate > self._bandwidth_threshold:
                    # Scale up proportionally to how much we're over the threshold
                    ratio = current_rate / self._bandwidth_threshold
                    interval *= min(2.0, ratio)  # At most double the interval
                    logger.debug(f"Increasing probe interval due to bandwidth limit: {interval:.2f}s")
            
            # Use protocol period as a reference
            if self._timing_service:
                protocol_period = self._timing_service.get_protocol_period()
                
                # Interval should generally be a fraction of the protocol period
                # to ensure regular probing
                if interval < protocol_period * 0.2:
                    interval = protocol_period * 0.2  # At least 20% of protocol period
                
                if interval > protocol_period * 0.8:
                    interval = protocol_period * 0.8  # At most 80% of protocol period
            
            # Ensure interval is within bounds
            interval = max(self._probe_interval_min, min(self._probe_interval_max, interval))
            
            # Record metric if available
            if self._metrics_collector:
                self._metrics_collector.record_gauge(
                    name="probe_interval",
                    value=interval,
                    labels={"peer_id": peer_id}
                )
            
            # Notify callbacks about the rate (probes per second)
            rate = 1.0 / interval if interval > 0 else 0
            self._notify_rate_callbacks(peer_id, rate)
            
            return interval
    
    def get_probe_success_rate(self, peer_id: str) -> Optional[float]:
        """
        Get the success rate of probes for a specific peer.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            Success rate (0.0-1.0) or None if no history
        """
        with self._lock:
            if peer_id not in self._probe_history or not self._probe_history[peer_id]:
                return None
            
            # Calculate success rate over all history
            history = self._probe_history[peer_id]
            successes = sum(1 for _, success in history if success)
            
            return successes / len(history)
    
    def adapt_rate(self, peer_id: str, success: bool, response_time: Optional[float] = None) -> None:
        """
        Adapt the probe rate based on operation success and response time.
        
        This method adjusts how frequently we probe a peer based on
        the success of operations and their response times.
        
        Args:
            peer_id: Identifier of the peer
            success: Whether the operation succeeded
            response_time: Optional response time in seconds
        """
        with self._lock:
            # Get current interval
            current_interval = self.get_probe_interval(peer_id)
            
            if not success:
                # For failures, increase the interval (probe less frequently)
                new_interval = min(
                    self._probe_interval_max, 
                    current_interval * 1.2  # 20% increase
                )
                
                if new_interval != current_interval:
                    logger.info(f"LIFEGUARD: Increasing probe interval for {peer_id} due to failure: {current_interval:.2f}s -> {new_interval:.2f}s")
                    
                    # Store the new interval
                    if not hasattr(self, '_custom_intervals'):
                        self._custom_intervals = {}
                    self._custom_intervals[peer_id] = new_interval
            
            elif response_time is not None:
                # For successful operations with response time info
                if response_time > current_interval * 0.8:
                    # Response time is high, increase interval
                    new_interval = min(
                        self._probe_interval_max,
                        current_interval * 1.1  # 10% increase
                    )
                    
                    if new_interval != current_interval:
                        logger.info(f"LIFEGUARD: Increasing probe interval for {peer_id} due to high latency: {current_interval:.2f}s -> {new_interval:.2f}s")
                        
                        # Store the new interval
                        if not hasattr(self, '_custom_intervals'):
                            self._custom_intervals = {}
                        self._custom_intervals[peer_id] = new_interval
                        
                elif response_time < current_interval * 0.2:
                    # Response time is low, decrease interval
                    new_interval = max(
                        self._probe_interval_min,
                        current_interval * 0.9  # 10% decrease
                    )
                    
                    if new_interval != current_interval:
                        logger.info(f"LIFEGUARD: Decreasing probe interval for {peer_id} due to low latency: {current_interval:.2f}s -> {new_interval:.2f}s")
                        
                        # Store the new interval
                        if not hasattr(self, '_custom_intervals'):
                            self._custom_intervals = {}
                        self._custom_intervals[peer_id] = new_interval

    def get_probe_interval(self, peer_id: str) -> float:
        """
        Get the interval between probes for a specific peer.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            Interval between probes in seconds
        """
        with self._lock:
            # Use custom interval if set
            if hasattr(self, '_custom_intervals') and peer_id in self._custom_intervals:
                return self._custom_intervals[peer_id]
                
            # Default interval
            interval = 1.0 / self._base_probe_count  # Default to 1/probe_count
            
            # Adjust based on awareness if available
            if self._awareness_service:
                awareness = self._awareness_service.get_awareness(peer_id)
                
                # Higher awareness = longer interval (less frequent probing)
                if awareness > 0:  # Only adjust if awareness is positive
                    # Scale interval by awareness - higher awareness means longer interval
                    interval *= (1.0 + awareness * 0.2)  # +20% per awareness level
            
            # Adjust for priority peers
            if peer_id in self._priority_peers:
                interval *= 0.5  # Half interval for priority peers
            
            # Apply bandwidth-based adjustments
            if self._bandwidth_limit_enabled and self._bandwidth_monitor:
                current_rate = self._bandwidth_monitor.get_current_rate(Direction.OUTBOUND)
                
                if current_rate > self._bandwidth_threshold:
                    # Network is congested, increase interval
                    ratio = current_rate / self._bandwidth_threshold
                    interval *= min(2.0, ratio)  # At most double the interval
            
            # Clamp to limits
            interval = max(self._probe_interval_min, min(self._probe_interval_max, interval))
            
            return interval

    def get_probing_stats(self) -> Dict[str, any]:
        """
        Get statistics about probing operations.
        
        Returns:
            Dictionary with probing statistics
        """
        with self._lock:
            stats = {
                "base_probe_count": self._base_probe_count,
                "base_probe_interval": self._base_probe_interval,
                "priority_peer_count": len(self._priority_peers),
                "blacklisted_peer_count": len(self._blacklist_peers),
                "bandwidth_limit_enabled": self._bandwidth_limit_enabled,
                "bandwidth_threshold": self._bandwidth_threshold
            }
            
            # Calculate overall success rate
            total_probes = 0
            total_successes = 0
            
            for peer_id, history in self._probe_history.items():
                successes = sum(1 for _, success in history if success)
                total_successes += successes
                total_probes += len(history)
            
            if total_probes > 0:
                stats["overall_success_rate"] = total_successes / total_probes
            
            # Per-peer statistics
            peer_stats = {}
            
            for peer_id, history in self._probe_history.items():
                if not history:
                    continue
                
                successes = sum(1 for _, success in history if success)
                
                peer_stats[peer_id] = {
                    "probe_count": len(history),
                    "success_rate": successes / len(history),
                    "last_probe_time": max(ts for ts, _ in history),
                    "probe_count_setting": self.get_probe_count(peer_id),
                    "probe_interval_setting": self.get_probe_interval(peer_id)
                }
            
            stats["peer_stats"] = peer_stats
            
            return stats
    
    def clear_history(self, older_than: Optional[float] = None) -> int:
        """
        Clear probe history from memory.
        
        Args:
            older_than: Optional timestamp, only clear history older than this
            
        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = 0
            
            if older_than is None:
                # Clear all history
                count = sum(len(history) for history in self._probe_history.values())
                self._probe_history = {}
            else:
                # Clear only older entries
                for peer_id in list(self._probe_history.keys()):
                    history = self._probe_history[peer_id]
                    new_history = [(ts, success) for ts, success in history if ts >= older_than]
                    
                    count += len(history) - len(new_history)
                    
                    if new_history:
                        self._probe_history[peer_id] = new_history
                    else:
                        del self._probe_history[peer_id]
            
            return count


# Initialize a global instance for easy import
default_probe_rate_service = None

def get_probe_rate_service(
    latency_tracker: Optional[LatencyTracker] = None,
    bandwidth_monitor: Optional[BandwidthMonitor] = None,
    awareness_service: Optional[AwarenessService] = None,
    timing_service: Optional[TimingService] = None,
    metrics_collector = None
) -> ProbeRateService:
    """
    Get or create the default probe rate service.
    
    Args:
        latency_tracker: Optional latency tracker
        bandwidth_monitor: Optional bandwidth monitor
        awareness_service: Optional awareness service
        timing_service: Optional timing service
        metrics_collector: Optional metrics collector
        
    Returns:
        The default probe rate service instance
    """
    global default_probe_rate_service
    
    if default_probe_rate_service is None:
        default_probe_rate_service = ProbeRateService(
            latency_tracker=latency_tracker,
            bandwidth_monitor=bandwidth_monitor,
            awareness_service=awareness_service,
            timing_service=timing_service,
            metrics_collector=metrics_collector
        )
    
    return default_probe_rate_service