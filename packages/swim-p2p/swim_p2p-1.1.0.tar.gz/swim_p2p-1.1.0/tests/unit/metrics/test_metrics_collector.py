import unittest
import time
from swim.metrics.collector import MetricsCollector, MetricType


class TestMetricsCollector(unittest.TestCase):
    
    def setUp(self):
        self.collector = MetricsCollector("test-node")
    
    def test_record_counter(self):
        self.collector.record_counter("test_counter", 5)
        metrics = self.collector.get_metrics("test_counter")
        
        self.assertIn("test_counter", metrics)
        self.assertEqual(len(metrics["test_counter"]), 1)
        self.assertEqual(metrics["test_counter"][0].type, MetricType.COUNTER)
        self.assertEqual(metrics["test_counter"][0].value, 5)
    
    def test_record_gauge(self):
        self.collector.record_gauge("test_gauge", 10.5)
        metrics = self.collector.get_metrics("test_gauge")
        
        self.assertIn("test_gauge", metrics)
        self.assertEqual(len(metrics["test_gauge"]), 1)
        self.assertEqual(metrics["test_gauge"][0].type, MetricType.GAUGE)
        self.assertEqual(metrics["test_gauge"][0].value, 10.5)
    
    def test_record_histogram(self):
        self.collector.record_histogram("test_histogram", 15.5)
        metrics = self.collector.get_metrics("test_histogram")
        
        self.assertIn("test_histogram", metrics)
        self.assertEqual(len(metrics["test_histogram"]), 1)
        self.assertEqual(metrics["test_histogram"][0].type, MetricType.HISTOGRAM)
        self.assertEqual(metrics["test_histogram"][0].value, 15.5)
    
    def test_record_event(self):
        self.collector.record_event("test_event", "something happened")
        metrics = self.collector.get_metrics("test_event")
        
        self.assertIn("test_event", metrics)
        self.assertEqual(len(metrics["test_event"]), 1)
        self.assertEqual(metrics["test_event"][0].type, MetricType.EVENT)
        self.assertEqual(metrics["test_event"][0].value, "something happened")
    
    def test_get_metrics_with_filters(self):
        # Add some metrics with different labels
        self.collector.record_counter("test_counter", 1, {"region": "us-east"})
        self.collector.record_counter("test_counter", 2, {"region": "us-west"})
        self.collector.record_counter("test_counter", 3, {"region": "eu-west"})
        
        # Filter by label
        metrics = self.collector.get_metrics("test_counter", labels={"region": "us-east"})
        self.assertEqual(len(metrics["test_counter"]), 1)
        self.assertEqual(metrics["test_counter"][0].value, 1)
        
        # Filter by type
        self.collector.record_gauge("test_counter", 4.0)  # Add a gauge with the same name
        metrics = self.collector.get_metrics("test_counter", metric_type=MetricType.COUNTER)
        self.assertEqual(len(metrics["test_counter"]), 3)  # Should only get the counters
    
    def test_compute_statistics(self):
        # Add some histogram values
        for value in [10, 20, 30, 40, 50]:
            self.collector.record_histogram("test_histogram", value)
        
        stats = self.collector.compute_statistics("test_histogram")
        
        self.assertEqual(stats["count"], 5)
        self.assertEqual(stats["min"], 10)
        self.assertEqual(stats["max"], 50)
        self.assertEqual(stats["mean"], 30)
        self.assertEqual(stats["median"], 30)
        self.assertIn("stdev", stats)
        self.assertIn("p95", stats)
        self.assertIn("p99", stats)
    
    def test_report_metrics(self):
        # Add various metrics
        self.collector.record_counter("requests", 10)
        self.collector.record_gauge("cpu_usage", 45.5)
        for value in [0.1, 0.2, 0.3]:
            self.collector.record_histogram("response_time", value)
        self.collector.record_event("system_event", "startup")
        
        report = self.collector.report_metrics()
        
        self.assertEqual(report["node_id"], "test-node")
        self.assertIn("metrics", report)
        self.assertIn("requests", report["metrics"])
        self.assertIn("cpu_usage", report["metrics"])
        self.assertIn("response_time", report["metrics"])
        self.assertIn("system_event", report["metrics"])
    
    def test_clear_metrics(self):
        # Add some metrics
        self.collector.record_counter("test_counter", 1)
        self.collector.record_gauge("test_gauge", 2.0)
        
        # Verify they exist
        self.assertTrue(self.collector.get_metrics("test_counter"))
        self.assertTrue(self.collector.get_metrics("test_gauge"))
        
        # Clear all metrics
        self.collector.clear_metrics()
        
        # Verify they're gone
        self.assertFalse(self.collector.get_metrics("test_counter"))
        self.assertFalse(self.collector.get_metrics("test_gauge"))
    
    def test_clear_metrics_with_timestamp(self):
        # Add some metrics at different times
        self.collector.record_counter("test_counter", 1)
        time.sleep(0.1)
        cutoff = time.time()
        time.sleep(0.1)
        self.collector.record_counter("test_counter", 2)
        
        # Clear metrics older than cutoff
        self.collector.clear_metrics(older_than=cutoff)
        
        # Verify only newer metrics remain
        metrics = self.collector.get_metrics("test_counter")
        self.assertEqual(len(metrics["test_counter"]), 1)
        self.assertEqual(metrics["test_counter"][0].value, 2)
    
    def test_callbacks(self):
        # Create a callback function
        callback_called = False
        callback_value = None
        
        def test_callback(metric):
            nonlocal callback_called, callback_value
            callback_called = True
            callback_value = metric.value
        
        # Register the callback
        self.collector.register_callback("test_counter", test_callback)
        
        # Record a metric that should trigger the callback
        self.collector.record_counter("test_counter", 42)
        
        # Verify callback was called with correct value
        self.assertTrue(callback_called)
        self.assertEqual(callback_value, 42)


if __name__ == '__main__':
    unittest.main()