import time
import threading
import statistics
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"  # Monotonically increasing value
    GAUGE = "gauge"      # Value that can go up and down
    HISTOGRAM = "histogram"  # Distribution of values
    EVENT = "event"      # Discrete events


@dataclass
class MetricValue:
    """Container for a metric value with metadata."""
    name: str
    type: MetricType
    value: Any
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Central metrics collection and aggregation service.
    
    This class is responsible for collecting metrics from various components
    of the SWIM protocol, aggregating them, and providing interfaces for
    reporting and analysis.
    """
    
    def __init__(self, node_id: str):
        """
        Initialize the metrics collector.
        
        Args:
            node_id: Unique identifier for this node
        """
        self.node_id = node_id
        self._metrics: Dict[str, List[MetricValue]] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()
        self._reporting_interval = 60  # seconds
        self._reporting_thread: Optional[threading.Thread] = None
        self._running = False
        
    def start(self):
        """Start the metrics collection and reporting."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._reporting_thread = threading.Thread(
                target=self._reporting_loop,
                daemon=True
            )
            self._reporting_thread.start()
    
    def stop(self):
        """Stop the metrics collection and reporting."""
        with self._lock:
            self._running = False
            if self._reporting_thread:
                self._reporting_thread.join(timeout=1.0)
                self._reporting_thread = None
    
    def _reporting_loop(self):
        """Background thread for periodic metrics reporting."""
        while self._running:
            time.sleep(self._reporting_interval)
            self.report_metrics()
    
    def set_reporting_interval(self, interval: float):
        """
        Set the interval for periodic metrics reporting.
        
        Args:
            interval: Reporting interval in seconds
        """
        with self._lock:
            self._reporting_interval = interval
    
    def record_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """
        Record a counter metric.
        
        Args:
            name: Name of the metric
            value: Value to increment the counter by
            labels: Optional key-value pairs for additional context
        """
        with self._lock:
            if labels is None:
                labels = {}
            
            # Add node_id as a default label
            labels["node_id"] = self.node_id
            
            metric = MetricValue(
                name=name,
                type=MetricType.COUNTER,
                value=value,
                labels=labels
            )
            
            if name not in self._metrics:
                self._metrics[name] = []
            
            self._metrics[name].append(metric)
            self._trigger_callbacks(name, metric)
    
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a gauge metric.
        
        Args:
            name: Name of the metric
            value: Current value of the gauge
            labels: Optional key-value pairs for additional context
        """
        with self._lock:
            if labels is None:
                labels = {}
            
            # Add node_id as a default label
            labels["node_id"] = self.node_id
            
            metric = MetricValue(
                name=name,
                type=MetricType.GAUGE,
                value=value,
                labels=labels
            )
            
            if name not in self._metrics:
                self._metrics[name] = []
            
            self._metrics[name].append(metric)
            self._trigger_callbacks(name, metric)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a value for a histogram metric.
        
        Args:
            name: Name of the metric
            value: Value to add to the histogram
            labels: Optional key-value pairs for additional context
        """
        with self._lock:
            if labels is None:
                labels = {}
            
            # Add node_id as a default label
            labels["node_id"] = self.node_id
            
            metric = MetricValue(
                name=name,
                type=MetricType.HISTOGRAM,
                value=value,
                labels=labels
            )
            
            if name not in self._metrics:
                self._metrics[name] = []
            
            self._metrics[name].append(metric)
            self._trigger_callbacks(name, metric)
    
    def record_event(self, name: str, value: Any, labels: Optional[Dict[str, str]] = None):
        """
        Record an event metric.
        
        Args:
            name: Name of the metric
            value: Value associated with the event
            labels: Optional key-value pairs for additional context
        """
        with self._lock:
            if labels is None:
                labels = {}
            
            # Add node_id as a default label
            labels["node_id"] = self.node_id
            
            metric = MetricValue(
                name=name,
                type=MetricType.EVENT,
                value=value,
                labels=labels
            )
            
            if name not in self._metrics:
                self._metrics[name] = []
            
            self._metrics[name].append(metric)
            self._trigger_callbacks(name, metric)
    
    def register_callback(self, metric_name: str, callback: Callable[[MetricValue], None]):
        """
        Register a callback to be called when a specific metric is recorded.
        
        Args:
            metric_name: Name of the metric to watch
            callback: Function to call when the metric is recorded
        """
        with self._lock:
            if metric_name not in self._callbacks:
                self._callbacks[metric_name] = []
            
            self._callbacks[metric_name].append(callback)
    
    def _trigger_callbacks(self, metric_name: str, metric: MetricValue):
        """
        Trigger all callbacks registered for a specific metric.
        
        Args:
            metric_name: Name of the metric
            metric: The metric value that was recorded
        """
        if metric_name in self._callbacks:
            for callback in self._callbacks[metric_name]:
                try:
                    callback(metric)
                except Exception as e:
                    print(f"Error in metric callback: {e}")
    
    def get_metrics(self, name: Optional[str] = None, 
                   since: Optional[float] = None,
                   metric_type: Optional[MetricType] = None,
                   labels: Optional[Dict[str, str]] = None) -> Dict[str, List[MetricValue]]:
        """
        Get metrics matching the specified criteria.
        
        Args:
            name: Optional name filter
            since: Optional timestamp filter (only metrics after this time)
            metric_type: Optional type filter
            labels: Optional labels filter (all specified labels must match)
            
        Returns:
            Dictionary of metric name to list of matching metric values
        """
        with self._lock:
            result = {}
            
            # If name is specified, only look at that metric
            metrics_to_check = {name: self._metrics[name]} if name and name in self._metrics else self._metrics
            
            for metric_name, values in metrics_to_check.items():
                matching_values = []
                
                for metric in values:
                    # Apply filters
                    if since is not None and metric.timestamp < since:
                        continue
                    
                    if metric_type is not None and metric.type != metric_type:
                        continue
                    
                    if labels is not None:
                        # Check if all specified labels match
                        if not all(k in metric.labels and metric.labels[k] == v for k, v in labels.items()):
                            continue
                    
                    matching_values.append(metric)
                
                if matching_values:
                    result[metric_name] = matching_values
            
            return result
    
    def compute_statistics(self, name: str, 
                          since: Optional[float] = None,
                          labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Compute statistics for a histogram metric.
        
        Args:
            name: Name of the metric
            since: Optional timestamp filter (only metrics after this time)
            labels: Optional labels filter
            
        Returns:
            Dictionary of statistic name to value
        """
        metrics = self.get_metrics(name, since, MetricType.HISTOGRAM, labels)
        
        if not metrics or name not in metrics:
            return {}
        
        values = [m.value for m in metrics[name]]
        
        if not values:
            return {}
        
        result = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values)
        }
        
        # Only compute these if we have enough values
        if len(values) > 1:
            result["stdev"] = statistics.stdev(values)
            
        if len(values) >= 4:  # Need at least 4 values for percentiles
            sorted_values = sorted(values)
            result["p95"] = sorted_values[int(0.95 * len(sorted_values))]
            result["p99"] = sorted_values[int(0.99 * len(sorted_values))]
        
        return result
    
    def report_metrics(self):
        """
        Generate a comprehensive metrics report.
        
        Returns:
            Dictionary containing all metrics and their statistics
        """
        with self._lock:
            report = {
                "timestamp": time.time(),
                "node_id": self.node_id,
                "metrics": {}
            }
            
            # Process each metric type differently
            for name, values in self._metrics.items():
                if not values:
                    continue
                
                # Group by metric type
                by_type = {}
                for metric in values:
                    if metric.type not in by_type:
                        by_type[metric.type] = []
                    by_type[metric.type].append(metric)
                
                report["metrics"][name] = {}
                
                # Process each type
                for metric_type, metrics in by_type.items():
                    if metric_type == MetricType.COUNTER:
                        # Sum all counter values
                        total = sum(m.value for m in metrics)
                        report["metrics"][name]["counter"] = total
                        
                    elif metric_type == MetricType.GAUGE:
                        # Take the most recent gauge value
                        latest = max(metrics, key=lambda m: m.timestamp)
                        report["metrics"][name]["gauge"] = latest.value
                        
                    elif metric_type == MetricType.HISTOGRAM:
                        # Compute statistics
                        values = [m.value for m in metrics]
                        stats = {
                            "count": len(values),
                            "min": min(values),
                            "max": max(values),
                            "mean": statistics.mean(values)
                        }
                        
                        if len(values) > 1:
                            stats["stdev"] = statistics.stdev(values)
                            
                        if len(values) >= 4:  # Need at least 4 values for percentiles
                            sorted_values = sorted(values)
                            stats["p95"] = sorted_values[int(0.95 * len(sorted_values))]
                            stats["p99"] = sorted_values[int(0.99 * len(sorted_values))]
                            
                        report["metrics"][name]["histogram"] = stats
                        
                    elif metric_type == MetricType.EVENT:
                        # Count events by value
                        event_counts = {}
                        for metric in metrics:
                            value = str(metric.value)
                            if value not in event_counts:
                                event_counts[value] = 0
                            event_counts[value] += 1
                            
                        report["metrics"][name]["events"] = event_counts
            
            print(f"Metrics Report: {report}")
            return report
    
    def clear_metrics(self, older_than: Optional[float] = None):
        """
        Clear metrics from memory.
        
        Args:
            older_than: Optional timestamp, only clear metrics older than this
        """
        with self._lock:
            if older_than is None:
                self._metrics = {}
                return
            
            for name, values in self._metrics.items():
                self._metrics[name] = [m for m in values if m.timestamp >= older_than]

print("Metrics collector module loaded")