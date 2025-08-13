"""
Unit tests for timing service.
"""

import pytest
import time
from unittest.mock import MagicMock, AsyncMock, patch

from swim.lifeguard.timing import TimingService, get_timing_service
from swim.metrics.latency import LatencyTracker
from swim.lifeguard.awareness import AwarenessService

class TestTimingService:
    """Test cases for the TimingService class."""
    
    def test_initialization(self):
        """Test that TimingService initializes with correct default values."""
        service = TimingService()
        
        # Check initial timing parameters
        assert service._base_protocol_period == 1.0
        assert service._base_ping_timeout == 1.0
        assert service._base_suspect_timeout == 5.0
        
        # Check timing ranges
        assert service._protocol_period_min == 0.5
        assert service._protocol_period_max == 2.0
        assert service._ping_timeout_min == 0.2
        assert service._ping_timeout_max == 3.0
        assert service._suspect_timeout_min == 2.0
        assert service._suspect_timeout_max == 15.0
        
        # Check initial current values
        assert service._current_protocol_period == 1.0
    
    def test_set_base_timing(self):
        """Test that set_base_timing updates base timing parameters correctly."""
        service = TimingService()
        
        # Set new timing parameters
        service.set_base_timing(
            protocol_period=2.0,
            ping_timeout=1.5,
            suspect_timeout=10.0
        )
        
        # Check that parameters were updated
        assert service._base_protocol_period == 2.0
        assert service._current_protocol_period == 2.0  # Current value also updated
        assert service._base_ping_timeout == 1.5
        assert service._base_suspect_timeout == 10.0
        
        # Check partial update
        service.set_base_timing(protocol_period=1.5)
        assert service._base_protocol_period == 1.5
        assert service._current_protocol_period == 1.5
        assert service._base_ping_timeout == 1.5  # Unchanged
        assert service._base_suspect_timeout == 10.0  # Unchanged
    
    def test_set_timing_ranges(self):
        """Test that set_timing_ranges updates timing ranges correctly."""
        service = TimingService()
        
        # Set new timing ranges
        service.set_timing_ranges(
            protocol_period_min=0.8,
            protocol_period_max=3.0,
            ping_timeout_min=0.3,
            ping_timeout_max=5.0,
            suspect_timeout_min=3.0,
            suspect_timeout_max=20.0
        )
        
        # Check that ranges were updated
        assert service._protocol_period_min == 0.8
        assert service._protocol_period_max == 3.0
        assert service._ping_timeout_min == 0.3
        assert service._ping_timeout_max == 5.0
        assert service._suspect_timeout_min == 3.0
        assert service._suspect_timeout_max == 20.0
        
        # Check partial update
        service.set_timing_ranges(protocol_period_min=1.0, ping_timeout_max=4.0)
        assert service._protocol_period_min == 1.0  # Updated
        assert service._protocol_period_max == 3.0  # Unchanged
        assert service._ping_timeout_min == 0.3  # Unchanged
        assert service._ping_timeout_max == 4.0  # Updated
        assert service._suspect_timeout_min == 3.0  # Unchanged
        assert service._suspect_timeout_max == 20.0  # Unchanged
    
    def test_register_callback(self):
        """Test that register_callback adds callbacks correctly."""
        service = TimingService()
        
        # Define test callbacks
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        # Register callbacks
        service.register_callback("protocol_period", callback1)
        service.register_callback("ping_timeout", callback2)
        
        # Check that callbacks were registered
        assert callback1 in service._callbacks["protocol_period"]
        assert callback2 in service._callbacks["ping_timeout"]
    
    def test_notify_callbacks(self):
        """Test that _notify_callbacks calls registered callbacks correctly."""
        service = TimingService()
        
        # Define test callbacks
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        # Register callbacks
        service.register_callback("protocol_period", callback1)
        service.register_callback("protocol_period", callback2)
        
        # Notify callbacks
        service._notify_callbacks("protocol_period", 1.5)
        
        # Check that callbacks were called
        callback1.assert_called_once_with("protocol_period", 1.5)
        callback2.assert_called_once_with("protocol_period", 1.5)
        
        # Check that callbacks for other parameters weren't called
        service._notify_callbacks("ping_timeout", 2.0)
        assert callback1.call_count == 1
        assert callback2.call_count == 1
    
    def test_get_protocol_period_no_adjustments(self):
        """Test that get_protocol_period returns current period when no adjustments needed."""
        service = TimingService()
        service._current_protocol_period = 1.5
        
        # Without a latency tracker or network conditions, should return current value
        period = service.get_protocol_period()
        assert period == 1.5
    
    def test_get_protocol_period_with_network_conditions(self):
        """Test that get_protocol_period adjusts based on network conditions."""
        service = TimingService()
        service._current_protocol_period = 1.0
        service._protocol_adjustment_factor = 0.1
        
        # Congested network
        period = service.get_protocol_period(network_conditions={"congested": True})
        assert period > 1.0  # Should increase
        
        # Reset
        service._current_protocol_period = 1.0
        
        # High failure rate
        period = service.get_protocol_period(network_conditions={"failure_rate": 0.2})
        assert period > 1.0  # Should increase
    
    def test_get_protocol_period_with_latency_tracker(self):
        """Test that get_protocol_period adjusts based on latency tracker."""
        # Create a mock latency tracker
        mock_tracker = MagicMock()
        
        # Create timing service with mock tracker
        service = TimingService(latency_tracker=mock_tracker)
        service._current_protocol_period = 1.0
        service._protocol_adjustment_factor = 0.1
        
        # Test degrading network
        mock_tracker.get_network_health.return_value = {"status": "degrading"}
        period = service.get_protocol_period()
        assert period > 1.0  # Should increase
        
        # Reset
        service._current_protocol_period = 1.0
        
        # Test healthy network
        mock_tracker.get_network_health.return_value = {"status": "healthy", "active_peers": 5}
        period = service.get_protocol_period()
        assert period < 1.0  # Should decrease
    
    def test_get_protocol_period_bounds(self):
        """Test that get_protocol_period respects min/max bounds."""
        service = TimingService()
        service._protocol_period_min = 0.5
        service._protocol_period_max = 2.0
        
        # Test lower bound
        service._current_protocol_period = 0.4  # Below min
        period = service.get_protocol_period()
        assert period == 0.5  # Should be capped at min
        
        # Test upper bound
        service._current_protocol_period = 2.5  # Above max
        period = service.get_protocol_period()
        assert period == 2.0  # Should be capped at max
    
    def test_get_ping_timeout_no_latency_tracker(self):
        """Test that get_ping_timeout returns base timeout without a latency tracker."""
        service = TimingService()
        service._base_ping_timeout = 1.5
        
        # Without a latency tracker, should return base value
        timeout = service.get_ping_timeout("test_peer")
        assert timeout == 1.5
    
    def test_get_ping_timeout_with_latency_tracker(self):
        """Test that get_ping_timeout uses the latency tracker's adaptive timeout."""
        # Create a mock latency tracker
        mock_tracker = MagicMock()
        mock_tracker.get_adaptive_timeout.return_value = 2.0
        
        # Create timing service with mock tracker
        service = TimingService(latency_tracker=mock_tracker)
        
        # Get timeout for a peer
        timeout = service.get_ping_timeout("test_peer")
        
        # Check that adaptive timeout was used
        assert timeout == 2.0
        mock_tracker.get_adaptive_timeout.assert_called_once_with("test_peer")
    
    def test_get_ping_timeout_bounds(self):
        """Test that get_ping_timeout respects min/max bounds."""
        # Create a mock latency tracker
        mock_tracker = MagicMock()
        
        # Create timing service with mock tracker
        service = TimingService(latency_tracker=mock_tracker)
        service._ping_timeout_min = 0.5
        service._ping_timeout_max = 2.0
        
        # Test lower bound
        mock_tracker.get_adaptive_timeout.return_value = 0.3  # Below min
        timeout = service.get_ping_timeout("test_peer")
        assert timeout == 0.5  # Should be capped at min
        
        # Test upper bound
        mock_tracker.get_adaptive_timeout.return_value = 2.5  # Above max
        timeout = service.get_ping_timeout("test_peer")
        assert timeout == 2.0  # Should be capped at max
    
    def test_get_suspect_timeout_no_awareness(self):
        """Test that get_suspect_timeout returns base timeout without awareness service."""
        # Create timing service without awareness service
        service = TimingService(awareness_service=None)
        service._base_suspect_timeout = 5.0
        
        # Get timeout for a peer
        timeout = service.get_suspect_timeout("test_peer")
        
        # Check that base timeout was used
        assert timeout == 5.0
    
    def test_get_suspect_timeout_with_awareness(self):
        """Test that get_suspect_timeout adjusts based on awareness."""
        # Create a mock awareness service
        mock_awareness = MagicMock()
        mock_awareness.get_suspicion_multiplier.return_value = 2.0
        
        # Create timing service with mock awareness
        service = TimingService(awareness_service=mock_awareness)
        service._base_suspect_timeout = 5.0
        
        # Get timeout for a peer
        timeout = service.get_suspect_timeout("test_peer")
        
        # Check that multiplier was applied
        assert timeout == 10.0  # 5.0 * 2.0 = 10.0
        mock_awareness.get_suspicion_multiplier.assert_called_once_with("test_peer")
    
    def test_get_suspect_timeout_bounds(self):
        """Test that get_suspect_timeout respects min/max bounds."""
        # Create a mock awareness service
        mock_awareness = MagicMock()
        
        # Create timing service with mock awareness
        service = TimingService(awareness_service=mock_awareness)
        service._base_suspect_timeout = 5.0
        service._suspect_timeout_min = 3.0
        service._suspect_timeout_max = 10.0
        
        # Test lower bound
        mock_awareness.get_suspicion_multiplier.return_value = 0.5  # Makes timeout 2.5, below min
        timeout = service.get_suspect_timeout("test_peer")
        assert timeout == 3.0  # Should be capped at min
        
        # Test upper bound
        mock_awareness.get_suspicion_multiplier.return_value = 3.0  # Makes timeout 15.0, above max
        timeout = service.get_suspect_timeout("test_peer")
        assert timeout == 10.0  # Should be capped at max
    
    def test_get_timing_stats(self):
        """Test that get_timing_stats returns correct statistics."""
        service = TimingService()
        
        # Set some current values
        service._current_protocol_period = 1.2
        service._base_protocol_period = 1.0
        service._base_ping_timeout = 1.0
        service._base_suspect_timeout = 5.0
        
        # Add some history
        service._timing_history["protocol_period"] = [(time.time(), 0.8), (time.time(), 1.0), (time.time(), 1.2)]
        service._timing_history["ping_timeout"] = [(time.time(), 0.5), (time.time(), 1.0), (time.time(), 1.5)]
        
        # Get stats
        stats = service.get_timing_stats()
        
        # Check basic stats
        assert stats["current_protocol_period"] == 1.2
        assert stats["base_protocol_period"] == 1.0
        assert stats["base_ping_timeout"] == 1.0
        assert stats["base_suspect_timeout"] == 5.0
        
        # Check protocol period stats
        assert stats["protocol_period"]["count"] == 3
        assert stats["protocol_period"]["min"] == 0.8
        assert stats["protocol_period"]["max"] == 1.2
        assert stats["protocol_period"]["mean"] == 1.0
        
        # Check ping timeout stats
        assert stats["ping_timeout"]["count"] == 3
        assert stats["ping_timeout"]["min"] == 0.5
        assert stats["ping_timeout"]["max"] == 1.5
        assert stats["ping_timeout"]["mean"] == 1.0
    
    def test_metrics_collection(self):
        """Test that metrics are recorded correctly."""
        # Create a mock metrics collector
        mock_collector = MagicMock()
        
        # Create timing service with mock collector
        service = TimingService(metrics_collector=mock_collector)
        
        # Trigger a protocol period adjustment
        service._current_protocol_period = 1.0
        service._protocol_adjustment_factor = 0.1
        # Make a significant change to trigger update
        period = service.get_protocol_period(network_conditions={"congested": True})
        
        # Check that metrics were recorded
        mock_collector.record_gauge.assert_called_once()
        
        # Verify call
        call = mock_collector.record_gauge.call_args
        assert call[1]["name"] == "protocol_period"
    
    def test_get_timing_service_singleton(self):
        """Test that get_timing_service returns a singleton instance."""
        # Get the default service
        service1 = get_timing_service()
        
        # Get it again
        service2 = get_timing_service()
        
        # Should be the same instance
        assert service1 is service2
        
        # Reset for other tests
        import swim.lifeguard.timing
        swim.lifeguard.timing.default_timing_service = None