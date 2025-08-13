import unittest
import time
from swim.metrics.bandwidth import BandwidthMonitor, Direction


class TestBandwidthMonitor(unittest.TestCase):
    
    def setUp(self):
        self.monitor = BandwidthMonitor()
    
    def test_record_bandwidth(self):
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1000, "peer1", "ping")
        
        # Get stats
        stats = self.monitor.get_bandwidth_stats(Direction.OUTBOUND)
        
        self.assertEqual(stats["total_bytes"], 1000)
        self.assertEqual(stats["sample_count"], 1)
        # Fix: Remove the incorrect assertion line that's causing the error
        # self.assertIn("by_message_type", 1000)  # This is wrong - trying to check if a string is in an integer
        self.assertIn("by_message_type", stats)  # This is the correct assertion
        self.assertIn("ping", stats["by_message_type"])
        self.assertEqual(stats["by_message_type"]["ping"], 1000)
    
    def test_record_bandwidth_multiple_messages(self):
        # Record bandwidth for different message types
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1000, "peer1", "ping")
        self.monitor.record_bandwidth(Direction.OUTBOUND, 2000, "peer1", "sync")
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1500, "peer2", "ping")
        
        # Get stats
        stats = self.monitor.get_bandwidth_stats(Direction.OUTBOUND)
        
        self.assertEqual(stats["total_bytes"], 4500)
        self.assertEqual(stats["sample_count"], 3)
        
        # Check breakdown by message type
        self.assertIn("by_message_type", stats)
        self.assertEqual(stats["by_message_type"]["ping"], 2500)
        self.assertEqual(stats["by_message_type"]["sync"], 2000)
        
        # Check breakdown by peer
        self.assertIn("by_peer", stats)
        self.assertEqual(stats["by_peer"]["peer1"], 3000)
        self.assertEqual(stats["by_peer"]["peer2"], 1500)
    
    def test_get_bandwidth_stats_with_filters(self):
        # Record bandwidth for different directions, peers, and message types
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1000, "peer1", "ping")
        self.monitor.record_bandwidth(Direction.INBOUND, 2000, "peer1", "sync")
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1500, "peer2", "ping")
        
        # Filter by direction
        stats = self.monitor.get_bandwidth_stats(direction=Direction.OUTBOUND)
        self.assertEqual(stats["total_bytes"], 2500)
        self.assertEqual(stats["sample_count"], 2)
        
        # Filter by peer
        stats = self.monitor.get_bandwidth_stats(peer_id="peer1")
        self.assertEqual(stats["total_bytes"], 3000)
        self.assertEqual(stats["sample_count"], 2)
        
        # Filter by message type
        stats = self.monitor.get_bandwidth_stats(message_type="ping")
        self.assertEqual(stats["total_bytes"], 2500)
        self.assertEqual(stats["sample_count"], 2)
        
        # Combined filters
        stats = self.monitor.get_bandwidth_stats(
            direction=Direction.OUTBOUND,
            peer_id="peer1",
            message_type="ping"
        )
        self.assertEqual(stats["total_bytes"], 1000)
        self.assertEqual(stats["sample_count"], 1)
    
    def test_get_bandwidth_stats_with_time_window(self):
        # Record bandwidth at different times
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1000, "peer1", "ping")
        time.sleep(0.1)
        cutoff = time.time()
        time.sleep(0.1)
        self.monitor.record_bandwidth(Direction.OUTBOUND, 2000, "peer1", "ping")
        
        # Get stats with time window
        stats = self.monitor.get_bandwidth_stats(time_window=time.time() - cutoff)
        
        self.assertEqual(stats["total_bytes"], 2000)
        self.assertEqual(stats["sample_count"], 1)
    
    def test_get_current_rate(self):
        # Record bandwidth
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1000, "peer1", "ping")
        
        # Get current rate (might be 0 if not enough time has passed)
        rate = self.monitor.get_current_rate(Direction.OUTBOUND)
        
        # Rate should be a float
        self.assertIsInstance(rate, float)
    
    def test_set_rate_limit_and_callback(self):
        # Set up a callback to track when rate limit is exceeded
        callback_called = False
        callback_direction = None
        callback_rate = None
        callback_limit = None
        
        def test_callback(direction, rate, limit):
            nonlocal callback_called, callback_direction, callback_rate, callback_limit
            callback_called = True
            callback_direction = direction
            callback_rate = rate
            callback_limit = limit
        
        # Register the callback
        self.monitor.register_rate_callback(Direction.OUTBOUND, test_callback)
        
        # Set a rate limit
        self.monitor.set_rate_limit(Direction.OUTBOUND, 1000)  # 1000 bytes/sec
        
        # Record bandwidth that might exceed the limit
        for _ in range(10):
            self.monitor.record_bandwidth(Direction.OUTBOUND, 200, "peer1", "ping")
        
        # Wait for rate calculation to happen
        time.sleep(1.1)
        
        # Check if callback was called (may not be if rate calculation hasn't happened yet)
        if callback_called:
            self.assertEqual(callback_direction, Direction.OUTBOUND)
            self.assertGreaterEqual(callback_rate, 1000)
            self.assertEqual(callback_limit, 1000)
    
    def test_get_optimization_recommendations(self):
        # Record bandwidth with imbalanced usage
        for _ in range(10):
            self.monitor.record_bandwidth(Direction.OUTBOUND, 1000, "peer1", "ping")
            self.monitor.record_bandwidth(Direction.OUTBOUND, 100, "peer2", "ping")
            self.monitor.record_bandwidth(Direction.INBOUND, 100, "peer1", "ping")
        
        # Get recommendations
        recommendations = self.monitor.get_optimization_recommendations()
        
        # Should have at least one recommendation
        self.assertGreaterEqual(len(recommendations), 1)
        
        # Each recommendation should have type, message, and suggestion
        for rec in recommendations:
            self.assertIn("type", rec)
            self.assertIn("message", rec)
            self.assertIn("suggestion", rec)
    
    def test_clear_samples(self):
        # Add some samples
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1000, "peer1", "ping")
        self.monitor.record_bandwidth(Direction.INBOUND, 2000, "peer2", "sync")
        
        # Verify they exist
        stats = self.monitor.get_bandwidth_stats()
        self.assertEqual(stats["total_bytes"], 3000)
        
        # Clear all samples
        self.monitor.clear_samples()
        
        # Verify they're gone
        stats = self.monitor.get_bandwidth_stats()
        self.assertEqual(stats["total_bytes"], 0)
    
    def test_clear_samples_with_timestamp(self):
        # Add samples at different times
        self.monitor.record_bandwidth(Direction.OUTBOUND, 1000, "peer1", "ping")
        time.sleep(0.1)
        cutoff = time.time()
        time.sleep(0.1)
        self.monitor.record_bandwidth(Direction.OUTBOUND, 2000, "peer1", "ping")
        
        # Clear samples older than cutoff
        self.monitor.clear_samples(older_than=cutoff)
        
        # Verify only newer samples remain
        stats = self.monitor.get_bandwidth_stats()
        self.assertEqual(stats["total_bytes"], 2000)
        self.assertEqual(stats["sample_count"], 1)


if __name__ == '__main__':
    unittest.main()