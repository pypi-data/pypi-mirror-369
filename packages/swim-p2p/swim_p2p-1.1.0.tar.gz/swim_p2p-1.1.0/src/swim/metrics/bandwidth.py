import time
import threading
import statistics
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum


class Direction(Enum):
    """Direction of data transfer."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


@dataclass
class BandwidthSample:
    """A single bandwidth usage sample."""
    direction: Direction
    bytes: int
    peer_id: Optional[str]
    message_type: Optional[str]
    timestamp: float = field(default_factory=time.time)


class BandwidthMonitor:
    """
    Monitors and optimizes bandwidth usage.
    
    This class is responsible for tracking inbound and outbound bandwidth,
    implementing rate limiting, and providing optimization recommendations.
    """
    
    def __init__(self, metrics_collector=None, window_size: int = 3600):
        """
        Initialize the bandwidth monitor.
        
        Args:
            metrics_collector: Optional metrics collector to record bandwidth metrics
            window_size: Maximum number of samples to keep (default: 1 hour worth)
        """
        self._samples: List[BandwidthSample] = []
        self._lock = threading.RLock()
        self._window_size = window_size
        self._metrics_collector = metrics_collector
        
        # Rate limiting
        self._rate_limits: Dict[Direction, int] = {
            Direction.INBOUND: 0,  # 0 means no limit
            Direction.OUTBOUND: 0  # 0 means no limit
        }
        self._current_rates: Dict[Direction, float] = {
            Direction.INBOUND: 0.0,
            Direction.OUTBOUND: 0.0
        }
        self._rate_callbacks: Dict[Direction, List[Callable]] = {
            Direction.INBOUND: [],
            Direction.OUTBOUND: []
        }
        
        # Start background thread for rate calculation
        self._running = True
        self._rate_thread = threading.Thread(
            target=self._calculate_rates_loop,
            daemon=True
        )
        self._rate_thread.start()
    
    def __del__(self):
        """Clean up resources."""
        self._running = False
        if hasattr(self, '_rate_thread') and self._rate_thread.is_alive():
            self._rate_thread.join(timeout=1.0)
    
    def record_bandwidth(self, direction: Direction, bytes: int, 
                        peer_id: Optional[str] = None,
                        message_type: Optional[str] = None):
        """
        Record bandwidth usage.
        
        Args:
            direction: Direction of data transfer
            bytes: Number of bytes transferred
            peer_id: Optional identifier of the peer
            message_type: Optional type of message
        """
        with self._lock:
            sample = BandwidthSample(
                direction=direction,
                bytes=bytes,
                peer_id=peer_id,
                message_type=message_type
            )
            
            self._samples.append(sample)
            
            # Trim to window size
            if len(self._samples) > self._window_size:
                self._samples = self._samples[-self._window_size:]
            
            # Record to metrics collector if available
            if self._metrics_collector:
                labels = {"direction": direction.value}
                if peer_id:
                    labels["peer_id"] = peer_id
                if message_type:
                    labels["message_type"] = message_type
                
                self._metrics_collector.record_counter(
                    name="bandwidth_bytes",
                    value=bytes,
                    labels=labels
                )
    
    def _calculate_rates_loop(self):
        """Background thread for calculating current bandwidth rates."""
        while self._running:
            try:
                self._update_current_rates()
                time.sleep(1.0)  # Update rates every second
            except Exception as e:
                print(f"Error in bandwidth rate calculation: {e}")
    
    def _update_current_rates(self):
        """Calculate current bandwidth rates based on recent samples."""
        with self._lock:
            now = time.time()
            window_start = now - 5.0  # Calculate rate over last 5 seconds
            
            # Filter samples in the time window
            recent_samples = [s for s in self._samples if s.timestamp >= window_start]
            
            # Calculate rates for each direction
            for direction in Direction:
                dir_samples = [s for s in recent_samples if s.direction == direction]
                
                if not dir_samples:
                    self._current_rates[direction] = 0.0
                    continue
                
                total_bytes = sum(s.bytes for s in dir_samples)
                time_span = now - min(s.timestamp for s in dir_samples)
                
                # Avoid division by zero
                if time_span > 0:
                    rate = total_bytes / time_span  # bytes per second
                else:
                    rate = 0.0
                
                old_rate = self._current_rates[direction]
                self._current_rates[direction] = rate
                
                # Check if we're exceeding rate limits
                if self._rate_limits[direction] > 0 and rate > self._rate_limits[direction]:
                    # Notify callbacks about rate limit exceeded
                    for callback in self._rate_callbacks[direction]:
                        try:
                            callback(direction, rate, self._rate_limits[direction])
                        except Exception as e:
                            print(f"Error in bandwidth callback: {e}")
                
                # Record current rate to metrics collector
                if self._metrics_collector:
                    self._metrics_collector.record_gauge(
                        name="bandwidth_rate",
                        value=rate,
                        labels={"direction": direction.value}
                    )
    
    def get_current_rate(self, direction: Direction) -> float:
        """
        Get the current bandwidth rate.
        
        Args:
            direction: Direction of data transfer
            
        Returns:
            Current rate in bytes per second
        """
        with self._lock:
            return self._current_rates[direction]
    
    def set_rate_limit(self, direction: Direction, bytes_per_second: int):
        """
        Set a rate limit for bandwidth usage.
        
        Args:
            direction: Direction of data transfer
            bytes_per_second: Maximum bytes per second (0 for no limit)
        """
        with self._lock:
            self._rate_limits[direction] = bytes_per_second
    
    def register_rate_callback(self, direction: Direction, 
                              callback: Callable[[Direction, float, int], None]):
        """
        Register a callback to be called when a rate limit is exceeded.
        
        Args:
            direction: Direction of data transfer
            callback: Function to call with (direction, current_rate, limit)
        """
        with self._lock:
            self._rate_callbacks[direction].append(callback)
    
    def get_bandwidth_stats(self, direction: Optional[Direction] = None,
                           peer_id: Optional[str] = None,
                           message_type: Optional[str] = None,
                           time_window: Optional[float] = None) -> Dict[str, any]:
        """
        Get bandwidth usage statistics.
        
        Args:
            direction: Optional filter by direction
            peer_id: Optional filter by peer
            message_type: Optional filter by message type
            time_window: Optional time window in seconds
            
        Returns:
            Dictionary of bandwidth statistics
        """
        with self._lock:
            # Apply filters
            samples = self._samples
            
            if direction is not None:
                samples = [s for s in samples if s.direction == direction]
            
            if peer_id is not None:
                samples = [s for s in samples if s.peer_id == peer_id]
            
            if message_type is not None:
                samples = [s for s in samples if s.message_type == message_type]
            
            if time_window is not None:
                cutoff = time.time() - time_window
                samples = [s for s in samples if s.timestamp >= cutoff]
            
            if not samples:
                return {"total_bytes": 0, "sample_count": 0}
            
            # Calculate statistics
            total_bytes = sum(s.bytes for s in samples)
            time_span = max(s.timestamp for s in samples) - min(s.timestamp for s in samples)
            
            result = {
                "total_bytes": total_bytes,
                "sample_count": len(samples),
                "start_time": min(s.timestamp for s in samples),
                "end_time": max(s.timestamp for s in samples)
            }
            
            # Calculate average rate if we have a meaningful time span
            if time_span > 0:
                result["average_rate"] = total_bytes / time_span
            
            # Break down by message type if not already filtered
            if message_type is None:
                by_message = {}
                for s in samples:
                    msg_type = s.message_type or "unknown"
                    if msg_type not in by_message:
                        by_message[msg_type] = 0
                    by_message[msg_type] += s.bytes
                
                result["by_message_type"] = by_message
            
            # Break down by peer if not already filtered
            if peer_id is None:
                by_peer = {}
                for s in samples:
                    pid = s.peer_id or "unknown"
                    if pid not in by_peer:
                        by_peer[pid] = 0
                    by_peer[pid] += s.bytes
                
                result["by_peer"] = by_peer
            
            return result
    
    def get_optimization_recommendations(self) -> List[Dict[str, any]]:
        """
        Get recommendations for bandwidth optimization.
        
        Returns:
            List of recommendation dictionaries
        """
        with self._lock:
            recommendations = []
            
            # Get recent bandwidth stats
            inbound_stats = self.get_bandwidth_stats(
                direction=Direction.INBOUND,
                time_window=300  # Last 5 minutes
            )
            
            outbound_stats = self.get_bandwidth_stats(
                direction=Direction.OUTBOUND,
                time_window=300  # Last 5 minutes
            )
            
            # Check if we have enough data
            if inbound_stats.get("sample_count", 0) < 10 or outbound_stats.get("sample_count", 0) < 10:
                recommendations.append({
                    "type": "info",
                    "message": "Not enough bandwidth data for optimization recommendations"
                })
                return recommendations
            
            # Check for high bandwidth usage by message type
            if "by_message_type" in outbound_stats:
                total_outbound = outbound_stats["total_bytes"]
                for msg_type, bytes_used in outbound_stats["by_message_type"].items():
                    percentage = (bytes_used / total_outbound) * 100 if total_outbound > 0 else 0
                    
                    if percentage > 50 and bytes_used > 1000000:  # More than 50% and 1MB
                        recommendations.append({
                            "type": "warning",
                            "message": f"High bandwidth usage from {msg_type} messages",
                            "details": f"{bytes_used} bytes ({percentage:.1f}% of outbound traffic)",
                            "suggestion": "Consider reducing message frequency or size"
                        })
            
            # Check for imbalanced peer communication
            if "by_peer" in outbound_stats:
                peer_counts = len(outbound_stats["by_peer"])
                if peer_counts > 5:  # Only meaningful with multiple peers
                    # Calculate standard deviation of peer bandwidth
                    peer_bytes = list(outbound_stats["by_peer"].values())
                    if len(peer_bytes) > 1:
                        stdev = statistics.stdev(peer_bytes)
                        mean = statistics.mean(peer_bytes)
                        
                        if stdev > mean * 2:  # High variance
                            recommendations.append({
                                "type": "warning",
                                "message": "Imbalanced communication with peers",
                                "details": f"Standard deviation: {stdev:.1f} bytes, Mean: {mean:.1f} bytes",
                                "suggestion": "Review peer selection algorithm for better distribution"
                            })
            
            # Check inbound/outbound ratio
            inbound_total = inbound_stats.get("total_bytes", 0)
            outbound_total = outbound_stats.get("total_bytes", 0)
            
            if inbound_total > 0 and outbound_total > 0:
                ratio = outbound_total / inbound_total
                
                if ratio > 5:  # Sending 5x more than receiving
                    recommendations.append({
                        "type": "warning",
                        "message": "High outbound to inbound ratio",
                        "details": f"Sending {ratio:.1f}x more data than receiving",
                        "suggestion": "Consider reducing gossip rate or message size"
                    })
                elif ratio < 0.2:  # Receiving 5x more than sending
                    recommendations.append({
                        "type": "warning",
                        "message": "High inbound to outbound ratio",
                        "details": f"Receiving {1/ratio:.1f}x more data than sending",
                        "suggestion": "Consider implementing better filtering of incoming messages"
                    })
            
            # Add general recommendations if none specific
            if not recommendations:
                recommendations.append({
                    "type": "info",
                    "message": "Bandwidth usage appears balanced",
                    "suggestion": "Continue monitoring for changes"
                })
            
            return recommendations
    
    def clear_samples(self, older_than: Optional[float] = None):
        """
        Clear bandwidth samples from memory.
        
        Args:
            older_than: Optional timestamp, only clear samples older than this
        """
        with self._lock:
            if older_than is None:
                self._samples = []
                return
            
            self._samples = [s for s in self._samples if s.timestamp >= older_than]

print("Bandwidth monitor module loaded")