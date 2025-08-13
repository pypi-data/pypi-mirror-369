"""
Congestion detection and adaptive throttling for SWIM-ZMQ integration.

This module monitors network conditions and implements adaptive throttling
to prevent congestion collapse and maintain system stability under load.
Provides early warning systems and graceful degradation capabilities.
"""

import asyncio
import time
import logging
import statistics
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class CongestionLevel(Enum):
    """Network congestion levels."""
    NORMAL = auto()      # Normal operation
    LIGHT = auto()       # Light congestion detected
    MODERATE = auto()    # Moderate congestion, throttling recommended
    HEAVY = auto()       # Heavy congestion, aggressive throttling
    SEVERE = auto()      # Severe congestion, emergency measures


class ThrottleAction(Enum):
    """Throttling actions that can be taken."""
    NONE = auto()           # No action needed
    REDUCE_RATE = auto()    # Reduce message sending rate
    DELAY_MESSAGES = auto() # Add delays between messages
    DROP_LOW_PRIORITY = auto()  # Drop low priority messages
    CIRCUIT_BREAK = auto()  # Open circuit breaker


@dataclass
class CongestionMetrics:
    """Metrics for congestion detection."""
    timestamp: float = field(default_factory=time.time)
    
    # Latency metrics
    avg_latency: float = 0.0
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    latency_trend: float = 0.0  # Positive = increasing
    
    # Queue metrics
    queue_depth: int = 0
    queue_growth_rate: float = 0.0
    
    # Throughput metrics
    messages_per_second: float = 0.0
    throughput_trend: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    
    # Resource metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    def get_congestion_score(self) -> float:
        """Calculate overall congestion score (0.0 = no congestion, 1.0 = severe)."""
        # Weighted combination of metrics
        latency_score = min(self.avg_latency / 1000.0, 1.0)  # Normalize to 1s max
        queue_score = min(self.queue_depth / 1000.0, 1.0)    # Normalize to 1000 msgs max
        error_score = min(self.error_rate, 1.0)
        resource_score = max(self.cpu_usage, self.memory_usage)
        
        # Weighted average
        weights = [0.3, 0.3, 0.2, 0.2]  # latency, queue, errors, resources
        scores = [latency_score, queue_score, error_score, resource_score]
        
        return sum(w * s for w, s in zip(weights, scores))


@dataclass
class ThrottleConfig:
    """Configuration for throttling behavior."""
    # Rate limiting
    base_rate_limit: float = 100.0  # Messages per second
    min_rate_limit: float = 10.0    # Minimum rate during throttling
    rate_adjustment_factor: float = 0.8  # Factor to reduce rate by
    
    # Delay configuration
    base_delay: float = 0.01        # Base delay between messages (10ms)
    max_delay: float = 1.0          # Maximum delay (1s)
    delay_multiplier: float = 2.0   # Delay increase factor
    
    # Thresholds
    light_congestion_threshold: float = 0.3
    moderate_congestion_threshold: float = 0.5
    heavy_congestion_threshold: float = 0.7
    severe_congestion_threshold: float = 0.9
    
    # Recovery
    recovery_factor: float = 1.1    # Factor to increase rate during recovery
    recovery_delay: float = 5.0     # Time to wait before attempting recovery


class CongestionDetector:
    """
    Detects and responds to network congestion.
    
    Monitors end-to-end latency, queue depths, and error rates to detect
    congestion and coordinate adaptive throttling responses.
    """
    
    def __init__(self, node_id: str, config: Optional[ThrottleConfig] = None):
        """
        Initialize congestion detector.
        
        Args:
            node_id: Identifier for this node
            config: Throttling configuration
        """
        self.node_id = node_id
        self.config = config or ThrottleConfig()
        
        # Metrics tracking
        self.latency_samples: deque = deque(maxlen=100)
        self.queue_depth_samples: deque = deque(maxlen=50)
        self.throughput_samples: deque = deque(maxlen=50)
        self.error_samples: deque = deque(maxlen=50)
        
        # Current state
        self.current_level = CongestionLevel.NORMAL
        self.current_rate_limit = self.config.base_rate_limit
        self.current_delay = self.config.base_delay
        self.last_adjustment = time.time()
        
        # Callbacks
        self.congestion_callback: Optional[Callable] = None
        self.throttle_callback: Optional[Callable] = None
        
        # Background monitoring
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self.monitor_interval = 1.0  # Monitor every second
        
        # Statistics
        self._stats = {
            "congestion_events": 0,
            "throttle_actions": 0,
            "messages_dropped": 0,
            "total_delay_added": 0.0
        }
        
        logger.info(f"CONGESTION_DETECTOR: Initialized for node {node_id}")
    
    def set_congestion_callback(self, callback: Callable[[CongestionLevel, CongestionMetrics], None]):
        """Set callback for congestion level changes."""
        self.congestion_callback = callback
        logger.info("CONGESTION_DETECTOR: Congestion callback configured")
    
    def set_throttle_callback(self, callback: Callable[[ThrottleAction, Dict[str, Any]], None]):
        """Set callback for throttle actions."""
        self.throttle_callback = callback
        logger.info("CONGESTION_DETECTOR: Throttle callback configured")
    
    async def start(self):
        """Start congestion monitoring."""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("CONGESTION_DETECTOR: Started monitoring")
    
    async def stop(self):
        """Stop congestion monitoring."""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("CONGESTION_DETECTOR: Stopped monitoring")
    
    def record_latency(self, latency_ms: float):
        """Record a latency measurement."""
        self.latency_samples.append((time.time(), latency_ms))
    
    def record_queue_depth(self, depth: int):
        """Record queue depth measurement."""
        self.queue_depth_samples.append((time.time(), depth))
    
    def record_throughput(self, messages_per_second: float):
        """Record throughput measurement."""
        self.throughput_samples.append((time.time(), messages_per_second))
    
    def record_error(self, error_type: str):
        """Record an error occurrence."""
        self.error_samples.append((time.time(), error_type))
    
    async def _monitor_loop(self):
        """Background monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(self.monitor_interval)
                await self._check_congestion()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"CONGESTION_MONITOR: Error in monitoring loop: {e}")
    
    async def _check_congestion(self):
        """Check for congestion and take appropriate action."""
        metrics = self._calculate_metrics()
        congestion_score = metrics.get_congestion_score()
        
        # Determine congestion level
        new_level = self._determine_congestion_level(congestion_score)
        
        # Check if level changed
        if new_level != self.current_level:
            logger.info(f"CONGESTION_LEVEL: Changed from {self.current_level.name} "
                       f"to {new_level.name} (score: {congestion_score:.3f})")
            
            old_level = self.current_level
            self.current_level = new_level
            self._stats["congestion_events"] += 1
            
            # Notify callback
            if self.congestion_callback:
                try:
                    self.congestion_callback(new_level, metrics)
                except Exception as e:
                    logger.error(f"CONGESTION_CALLBACK: Error in congestion callback: {e}")
            
            # Take throttling action
            await self._apply_throttling(new_level, old_level, metrics)
    
    def _calculate_metrics(self) -> CongestionMetrics:
        """Calculate current congestion metrics."""
        now = time.time()
        metrics = CongestionMetrics()
        
        # Calculate latency metrics
        if self.latency_samples:
            recent_latencies = [lat for ts, lat in self.latency_samples if now - ts < 30]
            if recent_latencies:
                metrics.avg_latency = statistics.mean(recent_latencies)
                metrics.p95_latency = statistics.quantiles(recent_latencies, n=20)[18]  # 95th percentile
                metrics.p99_latency = statistics.quantiles(recent_latencies, n=100)[98]  # 99th percentile
                
                # Calculate trend (positive = increasing latency)
                if len(recent_latencies) >= 10:
                    mid = len(recent_latencies) // 2
                    first_half = statistics.mean(recent_latencies[:mid])
                    second_half = statistics.mean(recent_latencies[mid:])
                    metrics.latency_trend = (second_half - first_half) / first_half
        
        # Calculate queue metrics
        if self.queue_depth_samples:
            recent_depths = [(ts, depth) for ts, depth in self.queue_depth_samples if now - ts < 30]
            if recent_depths:
                depths = [depth for _, depth in recent_depths]
                metrics.queue_depth = int(statistics.mean(depths))
                
                # Calculate growth rate
                if len(recent_depths) >= 5:
                    timestamps = [ts for ts, _ in recent_depths]
                    time_span = timestamps[-1] - timestamps[0]
                    if time_span > 0:
                        depth_change = depths[-1] - depths[0]
                        metrics.queue_growth_rate = depth_change / time_span
        
        # Calculate throughput metrics
        if self.throughput_samples:
            recent_throughput = [tps for ts, tps in self.throughput_samples if now - ts < 30]
            if recent_throughput:
                metrics.messages_per_second = statistics.mean(recent_throughput)
                
                # Calculate trend
                if len(recent_throughput) >= 5:
                    mid = len(recent_throughput) // 2
                    first_half = statistics.mean(recent_throughput[:mid])
                    second_half = statistics.mean(recent_throughput[mid:])
                    if first_half > 0:
                        metrics.throughput_trend = (second_half - first_half) / first_half
        
        # Calculate error metrics
        if self.error_samples:
            recent_errors = [err for ts, err in self.error_samples if now - ts < 60]
            total_samples = len([s for s in self.throughput_samples if now - s[0] < 60])
            if total_samples > 0:
                metrics.error_rate = len(recent_errors) / total_samples
                
                timeout_errors = [err for err in recent_errors if 'timeout' in err.lower()]
                metrics.timeout_rate = len(timeout_errors) / total_samples
        
        return metrics
    
    def _determine_congestion_level(self, score: float) -> CongestionLevel:
        """Determine congestion level based on score."""
        if score >= self.config.severe_congestion_threshold:
            return CongestionLevel.SEVERE
        elif score >= self.config.heavy_congestion_threshold:
            return CongestionLevel.HEAVY
        elif score >= self.config.moderate_congestion_threshold:
            return CongestionLevel.MODERATE
        elif score >= self.config.light_congestion_threshold:
            return CongestionLevel.LIGHT
        else:
            return CongestionLevel.NORMAL
    
    async def _apply_throttling(self, new_level: CongestionLevel, old_level: CongestionLevel, 
                               metrics: CongestionMetrics):
        """Apply appropriate throttling based on congestion level."""
        action = ThrottleAction.NONE
        action_params = {}
        
        if new_level == CongestionLevel.NORMAL:
            # Recovery mode
            if old_level != CongestionLevel.NORMAL:
                action = ThrottleAction.REDUCE_RATE
                self.current_rate_limit = min(
                    self.current_rate_limit * self.config.recovery_factor,
                    self.config.base_rate_limit
                )
                self.current_delay = max(
                    self.current_delay / self.config.delay_multiplier,
                    self.config.base_delay
                )
                action_params = {
                    "new_rate_limit": self.current_rate_limit,
                    "new_delay": self.current_delay
                }
                logger.info(f"CONGESTION_RECOVERY: Recovering from congestion "
                           f"(rate: {self.current_rate_limit:.1f}/s, delay: {self.current_delay:.3f}s)")
        
        elif new_level == CongestionLevel.LIGHT:
            action = ThrottleAction.REDUCE_RATE
            self.current_rate_limit *= self.config.rate_adjustment_factor
            action_params = {"new_rate_limit": self.current_rate_limit}
            logger.info(f"CONGESTION_LIGHT: Reducing rate to {self.current_rate_limit:.1f}/s")
        
        elif new_level == CongestionLevel.MODERATE:
            action = ThrottleAction.DELAY_MESSAGES
            self.current_delay = min(
                self.current_delay * self.config.delay_multiplier,
                self.config.max_delay
            )
            action_params = {"new_delay": self.current_delay}
            logger.info(f"CONGESTION_MODERATE: Adding delay of {self.current_delay:.3f}s")
        
        elif new_level == CongestionLevel.HEAVY:
            action = ThrottleAction.DROP_LOW_PRIORITY
            self.current_rate_limit = max(
                self.current_rate_limit * 0.5,
                self.config.min_rate_limit
            )
            action_params = {
                "new_rate_limit": self.current_rate_limit,
                "drop_low_priority": True
            }
            logger.warning(f"CONGESTION_HEAVY: Aggressive throttling "
                          f"(rate: {self.current_rate_limit:.1f}/s, dropping low priority)")
        
        elif new_level == CongestionLevel.SEVERE:
            action = ThrottleAction.CIRCUIT_BREAK
            action_params = {"circuit_break": True}
            logger.error(f"CONGESTION_SEVERE: Emergency measures - circuit breaking")
        
        # Record action
        if action != ThrottleAction.NONE:
            self._stats["throttle_actions"] += 1
            self.last_adjustment = time.time()
            
            # Notify callback
            if self.throttle_callback:
                try:
                    self.throttle_callback(action, action_params)
                except Exception as e:
                    logger.error(f"CONGESTION_THROTTLE: Error in throttle callback: {e}")
    
    def should_throttle_message(self, priority: str = "normal") -> Tuple[bool, float]:
        """
        Check if a message should be throttled.
        
        Args:
            priority: Message priority ("low", "normal", "high")
            
        Returns:
            Tuple of (should_delay, delay_seconds)
        """
        # Check if we should drop low priority messages
        if (self.current_level in [CongestionLevel.HEAVY, CongestionLevel.SEVERE] and 
            priority == "low"):
            self._stats["messages_dropped"] += 1
            return True, float('inf')  # Infinite delay = drop
        
        # Check if circuit breaker is open
        if self.current_level == CongestionLevel.SEVERE:
            return True, float('inf')  # Drop all messages
        
        # Apply delay based on current congestion level
        delay = 0.0
        if self.current_level != CongestionLevel.NORMAL:
            delay = self.current_delay
            self._stats["total_delay_added"] += delay
        
        return delay > 0, delay
    
    def get_current_rate_limit(self) -> float:
        """Get current rate limit in messages per second."""
        return self.current_rate_limit
    
    def get_congestion_status(self) -> Dict[str, Any]:
        """Get current congestion status."""
        metrics = self._calculate_metrics()
        
        return {
            "node_id": self.node_id,
            "congestion_level": self.current_level.name,
            "congestion_score": metrics.get_congestion_score(),
            "current_rate_limit": self.current_rate_limit,
            "current_delay": self.current_delay,
            "metrics": {
                "avg_latency": metrics.avg_latency,
                "queue_depth": metrics.queue_depth,
                "error_rate": metrics.error_rate,
                "throughput": metrics.messages_per_second
            },
            "last_adjustment": self.last_adjustment,
            "statistics": self._stats.copy()
        }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get recommendations for optimizing performance."""
        recommendations = []
        metrics = self._calculate_metrics()
        
        if metrics.avg_latency > 500:  # 500ms
            recommendations.append("High latency detected - consider reducing message size or frequency")
        
        if metrics.queue_depth > 100:
            recommendations.append("High queue depth - consider increasing processing capacity")
        
        if metrics.error_rate > 0.05:  # 5%
            recommendations.append("High error rate - check network connectivity and node health")
        
        if self.current_level != CongestionLevel.NORMAL:
            recommendations.append(f"System under {self.current_level.name.lower()} congestion - "
                                 f"consider scaling or load balancing")
        
        if not recommendations:
            recommendations.append("System operating normally - no optimizations needed")
        
        return recommendations
