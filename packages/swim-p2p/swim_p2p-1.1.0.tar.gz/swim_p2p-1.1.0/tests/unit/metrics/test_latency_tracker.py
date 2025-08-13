import unittest
import time
from swim.metrics.latency import LatencyTracker


class TestLatencyTracker(unittest.TestCase):
    
    def setUp(self):
        self.tracker = LatencyTracker()
    
    def test_record_rtt(self):
        self.tracker.record_rtt("peer1", 0.1)
        stats = self.tracker.get_rtt_stats("peer1")
        
        self.assertEqual(stats["count"], 1)
        self.assertEqual(stats["min"], 0.1)
        self.assertEqual(stats["max"], 0.1)
        self.assertEqual(stats["mean"], 0.1)
        self.assertEqual(stats["median"], 0.1)
    
    def test_get_rtt_stats_multiple_samples(self):
        # Add multiple RTT samples
        for rtt in [0.1, 0.2, 0.3, 0.4, 0.5]:
            self.tracker.record_rtt("peer1", rtt)
        
        stats = self.tracker.get_rtt_stats("peer1")
        
        self.assertEqual(stats["count"], 5)
        self.assertEqual(stats["min"], 0.1)
        self.assertEqual(stats["max"], 0.5)
        self.assertEqual(stats["mean"], 0.3)
        self.assertEqual(stats["median"], 0.3)
        self.assertIn("stdev", stats)
        self.assertIn("p95", stats)
        self.assertIn("p99", stats)
    
    def test_get_rtt_stats_with_window(self):
        # Add multiple RTT samples
        for rtt in [0.1, 0.2, 0.3, 0.4, 0.5]:
            self.tracker.record_rtt("peer1", rtt)
        
        # Get stats with window of 2 (should only use the last 2 samples)
        stats = self.tracker.get_rtt_stats("peer1", window=2)
        
        self.assertEqual(stats["count"], 2)
        self.assertEqual(stats["min"], 0.4)
        self.assertEqual(stats["max"], 0.5)
        self.assertEqual(stats["mean"], 0.45)
        self.assertEqual(stats["median"], 0.45)
    
    def test_get_rtt_stats_with_failures(self):
        # Add successful and failed RTT samples
        self.tracker.record_rtt("peer1", 0.1, success=True)
        self.tracker.record_rtt("peer1", 0.2, success=False)
        self.tracker.record_rtt("peer1", 0.3, success=True)
        
        # By default, failures are excluded
        stats = self.tracker.get_rtt_stats("peer1")
        self.assertEqual(stats["count"], 2)
        self.assertEqual(stats["min"], 0.1)
        self.assertEqual(stats["max"], 0.3)
        
        # Include failures
        stats = self.tracker.get_rtt_stats("peer1", include_failures=True)
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["min"], 0.1)
        self.assertEqual(stats["max"], 0.3)
    
    def test_get_adaptive_timeout(self):
        # Add RTT samples
        for rtt in [0.1, 0.15, 0.2]:
            self.tracker.record_rtt("peer1", rtt)
        
        # Set timeout parameters
        self.tracker.set_timeout_parameters(min_timeout=0.05, max_timeout=1.0, multiplier=2.0)
        
        # Get adaptive timeout
        timeout = self.tracker.get_adaptive_timeout("peer1")
        
        # Expected timeout: mean(0.1, 0.15, 0.2) * 2.0 + stdev
        # mean = 0.15, stdev ≈ 0.05, so timeout ≈ 0.35
        self.assertGreater(timeout, 0.3)
        self.assertLess(timeout, 0.4)
    
    def test_get_peer_latency_trend(self):
        # Add RTT samples with increasing latency
        for i in range(10):
            self.tracker.record_rtt("peer1", 0.1 + i * 0.01)
        
        # Add RTT samples with decreasing latency
        for i in range(10):
            self.tracker.record_rtt("peer2", 0.2 - i * 0.01)
        
        # Add RTT samples with stable latency
        for i in range(10):
            self.tracker.record_rtt("peer3", 0.15 + (i % 3 - 1) * 0.01)
        
        # Check trends
        trend1, rate1 = self.tracker.get_peer_latency_trend("peer1")
        trend2, rate2 = self.tracker.get_peer_latency_trend("peer2")
        trend3, rate3 = self.tracker.get_peer_latency_trend("peer3")
        
        self.assertEqual(trend1, "degrading")
        self.assertGreater(rate1, 0)
        
        self.assertEqual(trend2, "improving")
        self.assertLess(rate2, 0)
        
        self.assertEqual(trend3, "stable")
        self.assertAlmostEqual(abs(rate3), 0, delta=0.1)
    
    def test_get_network_health(self):
        # Add RTT samples for multiple peers
        for peer in ["peer1", "peer2", "peer3"]:
            for i in range(5):
                self.tracker.record_rtt(peer, 0.1 + i * 0.01)
        
        # Add some failures
        self.tracker.record_rtt("peer1", 0.5, success=False)
        
        # Get network health
        health = self.tracker.get_network_health()
        
        self.assertIn("status", health)
        self.assertIn("active_peers", health)
        self.assertEqual(health["active_peers"], 3)
    
    def test_clear_samples(self):
        # Add some samples
        self.tracker.record_rtt("peer1", 0.1)
        self.tracker.record_rtt("peer2", 0.2)
        
        # Verify they exist
        self.assertTrue(self.tracker.get_rtt_stats("peer1"))
        self.assertTrue(self.tracker.get_rtt_stats("peer2"))
        
        # Clear all samples
        self.tracker.clear_samples()
        
        # Verify they're gone
        self.assertFalse(self.tracker.get_rtt_stats("peer1"))
        self.assertFalse(self.tracker.get_rtt_stats("peer2"))
    
    def test_clear_samples_with_timestamp(self):
        # Add samples at different times
        self.tracker.record_rtt("peer1", 0.1)
        time.sleep(0.1)
        cutoff = time.time()
        time.sleep(0.1)
        self.tracker.record_rtt("peer1", 0.2)
        
        # Clear samples older than cutoff
        self.tracker.clear_samples(older_than=cutoff)
        
        # Verify only newer samples remain
        stats = self.tracker.get_rtt_stats("peer1")
        self.assertEqual(stats["count"], 1)
        self.assertEqual(stats["min"], 0.2)
        self.assertEqual(stats["max"], 0.2)


if __name__ == '__main__':
    unittest.main()