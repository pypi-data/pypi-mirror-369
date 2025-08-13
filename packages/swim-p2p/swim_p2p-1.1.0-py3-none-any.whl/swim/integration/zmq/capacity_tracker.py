"""
Advanced capacity tracking and monitoring for SWIM-ZMQ integration.

Provides real-time capacity monitoring, predictive analytics, and adaptive
thresholds to optimize system performance and prevent overload conditions.
"""

import asyncio
import time
import logging
import statistics
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque, defaultdict
import json

logger = logging.getLogger(__name__)


class CapacityState(Enum):
    """Capacity states for nodes."""
    OPTIMAL = auto()        # Operating within optimal range
    MODERATE = auto()       # Approaching capacity limits
    HIGH = auto()          # High utilization, monitor closely
    CRITICAL = auto()      # Critical capacity, throttle incoming
    OVERLOADED = auto()    # Overloaded, reject new requests


class MetricType(Enum):
    """Types of capacity metrics."""
    CPU_USAGE = auto()
    MEMORY_USAGE = auto()
    QUEUE_DEPTH = auto()
    CONNECTION_COUNT = auto()
    THROUGHPUT = auto()
    LATENCY = auto()
    ERROR_RATE = auto()


@dataclass
class CapacityThresholds:
    """Configurable thresholds for capacity states."""
    optimal_max: float = 0.6      # 60% - optimal operation
    moderate_max: float = 0.75    # 75% - moderate load
    high_max: float = 0.85        # 85% - high load
    critical_max: float = 0.95    # 95% - critical load
    # Above critical_max = overloaded
    
    def get_state(self, utilization: float) -> CapacityState:
        """Get capacity state based on utilization."""
        if utilization <= self.optimal_max:
            return CapacityState.OPTIMAL
        elif utilization <= self.moderate_max:
            return CapacityState.MODERATE
        elif utilization <= self.high_max:
            return CapacityState.HIGH
        elif utilization <= self.critical_max:
            return CapacityState.CRITICAL
        else:
            return CapacityState.OVERLOADED


@dataclass
class CapacityMetric:
    """Individual capacity metric with history."""
    metric_type: MetricType
    current_value: float = 0.0
    max_value: float = 100.0
    history: deque = field(default_factory=lambda: deque(maxlen=100))
    last_updated: float = field(default_factory=time.time)
    
    def update(self, value: float, max_val: Optional[float] = None):
        """Update metric value and history."""
        self.current_value = value
        if max_val is not None:
            self.max_value = max_val
        self.last_updated = time.time()
        self.history.append((time.time(), value))
    
    def get_utilization(self) -> float:
        """Get utilization as percentage (0.0 to 1.0)."""
        if self.max_value <= 0:
            return 0.0
        return min(1.0, self.current_value / self.max_value)
    
    def get_trend(self, window_seconds: float = 60.0) -> str:
        """Get trend direction over time window."""
        if len(self.history) < 2:
            return "STABLE"
        
        cutoff_time = time.time() - window_seconds
        recent_values = [val for ts, val in self.history if ts >= cutoff_time]
        
        if len(recent_values) < 2:
            return "STABLE"
        
        # Simple linear trend
        first_half = recent_values[:len(recent_values)//2]
        second_half = recent_values[len(recent_values)//2:]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        change_percent = (avg_second - avg_first) / max(avg_first, 0.01)
        
        if change_percent > 0.1:  # 10% increase
            return "INCREASING"
        elif change_percent < -0.1:  # 10% decrease
            return "DECREASING"
        else:
            return "STABLE"
    
    def get_statistics(self, window_seconds: float = 300.0) -> Dict[str, float]:
        """Get statistical summary over time window."""
        cutoff_time = time.time() - window_seconds
        recent_values = [val for ts, val in self.history if ts >= cutoff_time]
        
        if not recent_values:
            return {"count": 0}
        
        return {
            "count": len(recent_values),
            "current": self.current_value,
            "mean": statistics.mean(recent_values),
            "median": statistics.median(recent_values),
            "min": min(recent_values),
            "max": max(recent_values),
            "std_dev": statistics.stdev(recent_values) if len(recent_values) > 1 else 0.0,
            "utilization": self.get_utilization(),
            "trend": self.get_trend(window_seconds)
        }


@dataclass
class NodeCapacity:
    """Comprehensive capacity information for a node."""
    node_id: str
    metrics: Dict[MetricType, CapacityMetric] = field(default_factory=dict)
    thresholds: CapacityThresholds = field(default_factory=CapacityThresholds)
    last_updated: float = field(default_factory=time.time)
    
    # Predictive analytics
    predicted_overload_time: Optional[float] = None
    capacity_score: float = 1.0  # 0.0 = no capacity, 1.0 = full capacity
    
    def __post_init__(self):
        """Initialize default metrics."""
        for metric_type in MetricType:
            if metric_type not in self.metrics:
                self.metrics[metric_type] = CapacityMetric(metric_type)
    
    def update_metric(self, metric_type: MetricType, value: float, max_value: Optional[float] = None):
        """Update a specific metric."""
        if metric_type not in self.metrics:
            self.metrics[metric_type] = CapacityMetric(metric_type)
        
        self.metrics[metric_type].update(value, max_value)
        self.last_updated = time.time()
        self._recalculate_capacity_score()
    
    def get_overall_state(self) -> CapacityState:
        """Get overall capacity state based on all metrics."""
        worst_state = CapacityState.OPTIMAL
        
        for metric in self.metrics.values():
            utilization = metric.get_utilization()
            state = self.thresholds.get_state(utilization)
            
            # Take the worst state
            if state.value > worst_state.value:
                worst_state = state
        
        return worst_state
    
    def _recalculate_capacity_score(self):
        """Recalculate overall capacity score."""
        if not self.metrics:
            self.capacity_score = 1.0
            return
        
        # Weighted average of metric utilizations
        weights = {
            MetricType.CPU_USAGE: 0.25,
            MetricType.MEMORY_USAGE: 0.25,
            MetricType.QUEUE_DEPTH: 0.20,
            MetricType.CONNECTION_COUNT: 0.10,
            MetricType.THROUGHPUT: 0.10,
            MetricType.LATENCY: 0.05,
            MetricType.ERROR_RATE: 0.05
        }
        
        total_weight = 0.0
        weighted_utilization = 0.0
        
        for metric_type, metric in self.metrics.items():
            weight = weights.get(metric_type, 0.1)
            utilization = metric.get_utilization()
            
            # For latency and error rate, higher is worse
            if metric_type in [MetricType.LATENCY, MetricType.ERROR_RATE]:
                utilization = min(1.0, utilization)  # Cap at 100%
            
            weighted_utilization += weight * utilization
            total_weight += weight
        
        if total_weight > 0:
            avg_utilization = weighted_utilization / total_weight
            self.capacity_score = max(0.0, 1.0 - avg_utilization)
        else:
            self.capacity_score = 1.0
    
    def predict_overload(self, prediction_window: float = 300.0) -> Optional[float]:
        """Predict when node might become overloaded."""
        # Simple linear extrapolation based on trends
        critical_metrics = []
        
        for metric_type in [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE, MetricType.QUEUE_DEPTH]:
            if metric_type in self.metrics:
                metric = self.metrics[metric_type]
                if len(metric.history) >= 5:  # Need enough data points
                    trend = metric.get_trend(60.0)  # 1-minute trend
                    if trend == "INCREASING":
                        current_util = metric.get_utilization()
                        if current_util > 0.7:  # Already at 70%
                            critical_metrics.append(metric_type)
        
        if critical_metrics:
            # Estimate time to overload (simplified)
            self.predicted_overload_time = time.time() + prediction_window
            return self.predicted_overload_time
        else:
            self.predicted_overload_time = None
            return None
    
    def get_capacity_summary(self) -> Dict[str, Any]:
        """Get comprehensive capacity summary."""
        return {
            "node_id": self.node_id,
            "overall_state": self.get_overall_state().name,
            "capacity_score": self.capacity_score,
            "predicted_overload_time": self.predicted_overload_time,
            "last_updated": self.last_updated,
            "metrics": {
                metric_type.name: metric.get_statistics()
                for metric_type, metric in self.metrics.items()
            }
        }


class CapacityTracker:
    """
    Advanced capacity tracking and monitoring system.
    
    Provides real-time capacity monitoring, predictive analytics, and adaptive
    thresholds to optimize system performance and prevent overload conditions.
    """
    
    def __init__(self, node_id: str):
        """
        Initialize capacity tracker.
        
        Args:
            node_id: Identifier for this node
        """
        self.node_id = node_id
        self.nodes: Dict[str, NodeCapacity] = {}
        
        # Configuration
        self.monitoring_interval = 5.0  # seconds
        self.cleanup_interval = 300.0   # 5 minutes
        self.node_timeout = 600.0       # 10 minutes
        self.prediction_enabled = True
        
        # Callbacks
        self.capacity_change_callback: Optional[Callable] = None
        self.overload_prediction_callback: Optional[Callable] = None
        self.threshold_breach_callback: Optional[Callable] = None
        
        # Background tasks
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "nodes_tracked": 0,
            "capacity_updates": 0,
            "overload_predictions": 0,
            "threshold_breaches": 0,
            "cleanup_operations": 0
        }
        
        logger.info(f"CAPACITY_TRACKER: Initialized for node {node_id}")
    
    def set_capacity_change_callback(self, callback: Callable[[str, CapacityState, CapacityState], None]):
        """Set callback for capacity state changes."""
        self.capacity_change_callback = callback
    
    def set_overload_prediction_callback(self, callback: Callable[[str, float], None]):
        """Set callback for overload predictions."""
        self.overload_prediction_callback = callback
    
    def set_threshold_breach_callback(self, callback: Callable[[str, MetricType, float], None]):
        """Set callback for threshold breaches."""
        self.threshold_breach_callback = callback
    
    async def start(self):
        """Start capacity tracking."""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("CAPACITY_TRACKER: Started monitoring")
    
    async def stop(self):
        """Stop capacity tracking."""
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("CAPACITY_TRACKER: Stopped monitoring")
    
    def register_node(self, node_id: str, thresholds: Optional[CapacityThresholds] = None):
        """
        Register a node for capacity tracking.
        
        Args:
            node_id: Node identifier
            thresholds: Optional custom thresholds
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = NodeCapacity(
                node_id=node_id,
                thresholds=thresholds or CapacityThresholds()
            )
            self.stats["nodes_tracked"] += 1
            logger.info(f"CAPACITY_TRACKER: Registered node {node_id}")
    
    def unregister_node(self, node_id: str):
        """
        Unregister a node from capacity tracking.
        
        Args:
            node_id: Node identifier
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.stats["nodes_tracked"] -= 1
            logger.info(f"CAPACITY_TRACKER: Unregistered node {node_id}")
    
    def update_node_capacity(self, node_id: str, metric_type: MetricType, 
                           value: float, max_value: Optional[float] = None):
        """
        Update capacity metric for a node.
        
        Args:
            node_id: Node identifier
            metric_type: Type of metric being updated
            value: Current metric value
            max_value: Optional maximum value for the metric
        """
        if node_id not in self.nodes:
            self.register_node(node_id)
        
        node = self.nodes[node_id]
        old_state = node.get_overall_state()
        
        # Update the metric
        node.update_metric(metric_type, value, max_value)
        self.stats["capacity_updates"] += 1
        
        # Check for state changes
        new_state = node.get_overall_state()
        if old_state != new_state:
            logger.info(f"CAPACITY_CHANGE: {node_id} {old_state.name} -> {new_state.name}")
            
            if self.capacity_change_callback:
                try:
                    self.capacity_change_callback(node_id, old_state, new_state)
                except Exception as e:
                    logger.error(f"CAPACITY_TRACKER: Error in capacity change callback: {e}")
        
        # Check for threshold breaches
        utilization = node.metrics[metric_type].get_utilization()
        if utilization > node.thresholds.critical_max:
            self.stats["threshold_breaches"] += 1
            
            if self.threshold_breach_callback:
                try:
                    self.threshold_breach_callback(node_id, metric_type, utilization)
                except Exception as e:
                    logger.error(f"CAPACITY_TRACKER: Error in threshold breach callback: {e}")
        
        # Predictive analysis
        if self.prediction_enabled:
            overload_time = node.predict_overload()
            if overload_time and self.overload_prediction_callback:
                self.stats["overload_predictions"] += 1
                try:
                    self.overload_prediction_callback(node_id, overload_time)
                except Exception as e:
                    logger.error(f"CAPACITY_TRACKER: Error in overload prediction callback: {e}")
        
        logger.debug(f"CAPACITY_UPDATE: {node_id} {metric_type.name}={value} "
                    f"(util: {utilization:.1%}, state: {new_state.name})")
    
    def update_multiple_metrics(self, node_id: str, metrics: Dict[str, Tuple[float, Optional[float]]]):
        """
        Update multiple metrics for a node at once.
        
        Args:
            node_id: Node identifier
            metrics: Dictionary of metric_name -> (value, max_value)
        """
        metric_type_map = {
            "cpu_usage": MetricType.CPU_USAGE,
            "memory_usage": MetricType.MEMORY_USAGE,
            "queue_depth": MetricType.QUEUE_DEPTH,
            "connection_count": MetricType.CONNECTION_COUNT,
            "throughput": MetricType.THROUGHPUT,
            "latency": MetricType.LATENCY,
            "error_rate": MetricType.ERROR_RATE
        }
        
        for metric_name, (value, max_value) in metrics.items():
            if metric_name in metric_type_map:
                self.update_node_capacity(node_id, metric_type_map[metric_name], value, max_value)
    
    def get_node_capacity(self, node_id: str) -> Optional[NodeCapacity]:
        """
        Get capacity information for a node.
        
        Args:
            node_id: Node identifier
            
        Returns:
            NodeCapacity object or None if not found
        """
        return self.nodes.get(node_id)
    
    def get_available_capacity_nodes(self, min_capacity_score: float = 0.3) -> List[str]:
        """
        Get list of nodes with available capacity.
        
        Args:
            min_capacity_score: Minimum capacity score required
            
        Returns:
            List of node IDs with sufficient capacity
        """
        available_nodes = []
        
        for node_id, node in self.nodes.items():
            if (node.capacity_score >= min_capacity_score and 
                node.get_overall_state() not in [CapacityState.CRITICAL, CapacityState.OVERLOADED]):
                available_nodes.append(node_id)
        
        # Sort by capacity score (highest first)
        available_nodes.sort(key=lambda nid: self.nodes[nid].capacity_score, reverse=True)
        return available_nodes
    
    def get_overloaded_nodes(self) -> List[str]:
        """Get list of overloaded nodes."""
        return [
            node_id for node_id, node in self.nodes.items()
            if node.get_overall_state() == CapacityState.OVERLOADED
        ]
    
    def get_capacity_distribution(self) -> Dict[str, int]:
        """Get distribution of nodes by capacity state."""
        distribution = defaultdict(int)
        
        for node in self.nodes.values():
            state = node.get_overall_state()
            distribution[state.name] += 1
        
        return dict(distribution)
    
    def get_cluster_capacity_summary(self) -> Dict[str, Any]:
        """Get overall cluster capacity summary."""
        if not self.nodes:
            return {"total_nodes": 0, "average_capacity_score": 0.0}
        
        total_capacity = sum(node.capacity_score for node in self.nodes.values())
        avg_capacity = total_capacity / len(self.nodes)
        
        distribution = self.get_capacity_distribution()
        overloaded_nodes = self.get_overloaded_nodes()
        
        return {
            "total_nodes": len(self.nodes),
            "average_capacity_score": avg_capacity,
            "capacity_distribution": distribution,
            "overloaded_nodes": len(overloaded_nodes),
            "available_nodes": len(self.get_available_capacity_nodes()),
            "cluster_health": "HEALTHY" if len(overloaded_nodes) == 0 else "DEGRADED"
        }
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(self.monitoring_interval)
                await self._perform_monitoring_cycle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"CAPACITY_TRACKER: Error in monitoring loop: {e}")
    
    async def _perform_monitoring_cycle(self):
        """Perform one monitoring cycle."""
        current_time = time.time()
        
        # Check for stale nodes
        stale_nodes = []
        for node_id, node in self.nodes.items():
            if current_time - node.last_updated > self.node_timeout:
                stale_nodes.append(node_id)
        
        # Log stale nodes
        for node_id in stale_nodes:
            logger.warning(f"CAPACITY_TRACKER: Node {node_id} has stale capacity data "
                          f"({current_time - self.nodes[node_id].last_updated:.1f}s old)")
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"CAPACITY_TRACKER: Error in cleanup loop: {e}")
    
    async def _perform_cleanup(self):
        """Perform cleanup of old data."""
        current_time = time.time()
        cleanup_count = 0
        
        # Clean up very old nodes
        nodes_to_remove = []
        for node_id, node in self.nodes.items():
            if current_time - node.last_updated > (self.node_timeout * 2):
                nodes_to_remove.append(node_id)
        
        for node_id in nodes_to_remove:
            self.unregister_node(node_id)
            cleanup_count += 1
        
        if cleanup_count > 0:
            self.stats["cleanup_operations"] += cleanup_count
            logger.info(f"CAPACITY_TRACKER: Cleaned up {cleanup_count} stale nodes")
    
    def export_capacity_data(self, include_history: bool = False) -> Dict[str, Any]:
        """
        Export capacity data for analysis or backup.
        
        Args:
            include_history: Whether to include metric history
            
        Returns:
            Dictionary containing all capacity data
        """
        export_data = {
            "timestamp": time.time(),
            "tracker_node_id": self.node_id,
            "statistics": self.stats.copy(),
            "cluster_summary": self.get_cluster_capacity_summary(),
            "nodes": {}
        }
        
        for node_id, node in self.nodes.items():
            node_data = node.get_capacity_summary()
            
            if include_history:
                node_data["metric_history"] = {}
                for metric_type, metric in node.metrics.items():
                    node_data["metric_history"][metric_type.name] = list(metric.history)
            
            export_data["nodes"][node_id] = node_data
        
        return export_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get capacity tracker statistics."""
        return {
            "tracker_node_id": self.node_id,
            "running": self._running,
            "configuration": {
                "monitoring_interval": self.monitoring_interval,
                "cleanup_interval": self.cleanup_interval,
                "node_timeout": self.node_timeout,
                "prediction_enabled": self.prediction_enabled
            },
            "statistics": self.stats.copy(),
            "cluster_summary": self.get_cluster_capacity_summary()
        }
