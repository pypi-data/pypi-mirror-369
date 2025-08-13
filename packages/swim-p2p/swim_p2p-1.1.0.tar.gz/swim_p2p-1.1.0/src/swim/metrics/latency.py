import time
import threading
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class LatencySample:
    """A single latency measurement sample."""
    peer_id: str
    rtt: float  # Round-trip time in seconds
    timestamp: float = field(default_factory=time.time)
    success: bool = True  # Whether the request succeeded


class LatencyTracker:
    """
    Tracks and analyzes network latency between peers.
    
    This class is responsible for collecting round-trip time (RTT) measurements,
    calculating statistics, and providing adaptive timeout values based on
    network conditions.
    """
    
    def __init__(self, metrics_collector=None, window_size: int = 100):
        """
        Initialize the latency tracker.
        
        Args:
            metrics_collector: Optional metrics collector to record latency metrics
            window_size: Maximum number of samples to keep per peer
        """
        self._samples: Dict[str, List[LatencySample]] = {}
        self._lock = threading.RLock()
        self._window_size = window_size
        self._metrics_collector = metrics_collector
        
        # Default timeout parameters
        self._min_timeout = 0.1  # 100ms minimum timeout
        self._max_timeout = 10.0  # 10s maximum timeout
        self._timeout_multiplier = 2.0  # Multiply mean RTT by this factor
        
    def record_rtt(self, peer_id: str, rtt: float, success: bool = True):
        """
        Record a round-trip time measurement.
        
        Args:
            peer_id: Identifier of the peer
            rtt: Round-trip time in seconds
            success: Whether the request succeeded
        """
        with self._lock:
            sample = LatencySample(
                peer_id=peer_id,
                rtt=rtt,
                success=success
            )
            
            if peer_id not in self._samples:
                self._samples[peer_id] = []
            
            self._samples[peer_id].append(sample)
            
            # Trim to window size
            if len(self._samples[peer_id]) > self._window_size:
                self._samples[peer_id] = self._samples[peer_id][-self._window_size:]
            
            # Record to metrics collector if available
            if self._metrics_collector:
                self._metrics_collector.record_histogram(
                    name="peer_rtt",
                    value=rtt,
                    labels={"peer_id": peer_id, "success": str(success)}
                )
    
    def get_rtt_stats(self, peer_id: str, 
                     window: Optional[int] = None,
                     include_failures: bool = False) -> Dict[str, float]:
        """
        Get RTT statistics for a specific peer.
        
        Args:
            peer_id: Identifier of the peer
            window: Optional limit on number of recent samples to consider
            include_failures: Whether to include failed requests in statistics
            
        Returns:
            Dictionary of statistics (min, max, mean, median, etc.)
        """
        with self._lock:
            if peer_id not in self._samples:
                return {}
            
            samples = self._samples[peer_id]
            
            if not include_failures:
                samples = [s for s in samples if s.success]
            
            if not samples:
                return {}
            
            if window is not None and window > 0:
                samples = samples[-window:]
            
            rtts = [s.rtt for s in samples]
            
            result = {
                "count": len(rtts),
                "min": min(rtts),
                "max": max(rtts),
                "mean": statistics.mean(rtts),
                "median": statistics.median(rtts)
            }
            
            # Only compute these if we have enough values
            if len(rtts) > 1:
                result["stdev"] = statistics.stdev(rtts)
                
            if len(rtts) >= 4:  # Need at least 4 values for percentiles
                sorted_rtts = sorted(rtts)
                result["p95"] = sorted_rtts[int(0.95 * len(sorted_rtts))]
                result["p99"] = sorted_rtts[int(0.99 * len(sorted_rtts))]
            
            return result
    
    def get_adaptive_timeout(self, peer_id: str) -> float:
        """
        Calculate an adaptive timeout value based on RTT history.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            Timeout value in seconds
        """
        with self._lock:
            stats = self.get_rtt_stats(peer_id, window=20)
            
            if not stats:
                # No data, use default timeout
                return self._min_timeout * 5
            
            # Base timeout on mean RTT with a multiplier
            timeout = stats["mean"] * self._timeout_multiplier
            
            # Add standard deviation if available to account for variability
            if "stdev" in stats:
                timeout += stats["stdev"]
            
            # Ensure timeout is within bounds
            timeout = max(self._min_timeout, min(self._max_timeout, timeout))
            
            return timeout
    
    def set_timeout_parameters(self, min_timeout: float, max_timeout: float, multiplier: float):
        """
        Set parameters for adaptive timeout calculation.
        
        Args:
            min_timeout: Minimum timeout in seconds
            max_timeout: Maximum timeout in seconds
            multiplier: Multiplier for mean RTT
        """
        with self._lock:
            self._min_timeout = min_timeout
            self._max_timeout = max_timeout
            self._timeout_multiplier = multiplier
    
    def get_peer_latency_trend(self, peer_id: str, 
                              window: int = 20) -> Tuple[str, float]:
        """
        Analyze the trend in latency for a peer.
        
        Args:
            peer_id: Identifier of the peer
            window: Number of recent samples to consider
            
        Returns:
            Tuple of (trend, change_rate) where trend is one of
            "improving", "stable", "degrading" and change_rate is
            the rate of change in RTT
        """
        with self._lock:
            if peer_id not in self._samples:
                return ("unknown", 0.0)
            
            samples = [s for s in self._samples[peer_id] if s.success]
            
            # Fix: Use the available samples even if less than window
            # but ensure we have at least 4 samples for meaningful trend analysis
            if len(samples) < 4:
                return ("unknown", 0.0)
            
            # Take the most recent samples (up to window size)
            recent = samples[-min(window, len(samples)):]
            
            # Split into two halves
            half_size = len(recent) // 2
            first_half = recent[:half_size]
            second_half = recent[half_size:]
            
            # Calculate mean RTT for each half
            first_mean = statistics.mean([s.rtt for s in first_half])
            second_mean = statistics.mean([s.rtt for s in second_half])
            
            # Calculate change rate
            change_rate = (second_mean - first_mean) / first_mean if first_mean > 0 else 0
            
            # Determine trend
            if abs(change_rate) < 0.1:  # Less than 10% change
                trend = "stable"
            elif change_rate < 0:
                trend = "improving"
            else:
                trend = "degrading"
            
            return (trend, change_rate)
    
    def get_network_health(self) -> Dict[str, any]:
        """
        Get an overall assessment of network health.
        
        Returns:
            Dictionary with network health metrics
        """
        with self._lock:
            if not self._samples:
                return {"status": "unknown", "peers": 0}
            
            # Count peers with recent samples (last 60 seconds)
            cutoff = time.time() - 60
            active_peers = 0
            degrading_peers = 0
            
            for peer_id, samples in self._samples.items():
                recent = [s for s in samples if s.timestamp >= cutoff]
                if recent:
                    active_peers += 1
                    trend, _ = self.get_peer_latency_trend(peer_id)
                    if trend == "degrading":
                        degrading_peers += 1
            
            # Calculate failure rate across all peers
            all_recent_samples = []
            for samples in self._samples.values():
                all_recent_samples.extend([s for s in samples if s.timestamp >= cutoff])
            
            failure_rate = 0
            if all_recent_samples:
                failures = sum(1 for s in all_recent_samples if not s.success)
                failure_rate = failures / len(all_recent_samples)
            
            # Determine overall status
            status = "healthy"
            if failure_rate > 0.2:  # More than 20% failures
                status = "unhealthy"
            elif degrading_peers > active_peers * 0.3:  # More than 30% of peers degrading
                status = "degrading"
            
            return {
                "status": status,
                "active_peers": active_peers,
                "degrading_peers": degrading_peers,
                "failure_rate": failure_rate
            }
    
    def clear_samples(self, older_than: Optional[float] = None):
        """
        Clear latency samples from memory.
        
        Args:
            older_than: Optional timestamp, only clear samples older than this
        """
        with self._lock:
            if older_than is None:
                self._samples = {}
                return
            
            for peer_id in self._samples:
                self._samples[peer_id] = [
                    s for s in self._samples[peer_id] 
                    if s.timestamp >= older_than
                ]

print("Latency tracker module loaded")