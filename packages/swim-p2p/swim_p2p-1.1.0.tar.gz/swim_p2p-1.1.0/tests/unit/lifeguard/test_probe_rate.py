"""
Unit tests for the adaptive probing rate control module.
"""
import pytest
import asyncio
import time
from unittest.mock import MagicMock, AsyncMock, patch

from swim.lifeguard.probe_rate import ProbeRateService
from swim.metrics.latency import LatencyTracker
from swim.metrics.bandwidth import BandwidthMonitor, Direction
from swim.lifeguard.awareness import AwarenessService
from swim.lifeguard.timing import TimingService

# Test fixtures
@pytest.fixture
def mock_latency_tracker():
    """Create a mock latency tracker."""
    tracker = MagicMock(spec=LatencyTracker)
    tracker.get_rtt_stats.return_value = {"mean": 0.1, "median": 0.08, "stdev": 0.02}
    return tracker

@pytest.fixture
def mock_bandwidth_monitor():
    """Create a mock bandwidth monitor."""
    monitor = MagicMock(spec=BandwidthMonitor)
    monitor.get_current_rate.return_value = 50000  # 50KB/s
    return monitor

@pytest.fixture
def mock_awareness_service():
    """Create a mock awareness service."""
    service = MagicMock(spec=AwarenessService)
    service.get_awareness.return_value = 4  # Mid-range awareness
    service.get_probe_count.return_value = 3  # Default probe count
    service.get_suspicion_multiplier.return_value = 1.2  # Small multiplier
    return service

@pytest.fixture
def mock_timing_service():
    """Create a mock timing service."""
    service = MagicMock(spec=TimingService)
    service.get_protocol_period.return_value = 1.0  # Default protocol period
    return service

@pytest.fixture
def mock_metrics_collector():
    """Create a mock metrics collector."""
    collector = MagicMock()
    collector.record_gauge = MagicMock()
    collector.record_counter = MagicMock()
    collector.record_event = MagicMock()
    return collector

@pytest.fixture
def probe_rate_service(
    mock_latency_tracker, 
    mock_bandwidth_monitor, 
    mock_awareness_service, 
    mock_timing_service,
    mock_metrics_collector
):
    """Create a probe rate service with mock dependencies."""
    return ProbeRateService(
        latency_tracker=mock_latency_tracker,
        bandwidth_monitor=mock_bandwidth_monitor,
        awareness_service=mock_awareness_service,
        timing_service=mock_timing_service,
        metrics_collector=mock_metrics_collector
    )

# Tests for ProbeRateService
def test_probe_rate_initialization(probe_rate_service):
    """Test that the probe rate service initializes correctly."""
    # Check initial values
    assert probe_rate_service._base_probe_count == 3
    assert probe_rate_service._base_probe_interval == 1.0
    assert probe_rate_service._probe_count_min == 2
    assert probe_rate_service._probe_count_max == 8
    assert probe_rate_service._probe_interval_min == 0.5
    assert probe_rate_service._probe_interval_max == 3.0
    assert probe_rate_service._bandwidth_limit_enabled is False

def test_set_base_parameters(probe_rate_service):
    """Test setting base probing parameters."""
    probe_rate_service.set_base_parameters(probe_count=5, probe_interval=2.0)
    
    assert probe_rate_service._base_probe_count == 5
    assert probe_rate_service._base_probe_interval == 2.0

def test_set_probing_ranges(probe_rate_service):
    """Test setting probing parameter ranges."""
    probe_rate_service.set_probing_ranges(
        probe_count_min=3,
        probe_count_max=10,
        probe_interval_min=0.8,
        probe_interval_max=4.0
    )
    
    assert probe_rate_service._probe_count_min == 3
    assert probe_rate_service._probe_count_max == 10
    assert probe_rate_service._probe_interval_min == 0.8
    assert probe_rate_service._probe_interval_max == 4.0

def test_set_bandwidth_control(probe_rate_service):
    """Test setting bandwidth control parameters."""
    probe_rate_service.set_bandwidth_control(enabled=True, threshold=200000)
    
    assert probe_rate_service._bandwidth_limit_enabled is True
    assert probe_rate_service._bandwidth_threshold == 200000

def test_register_rate_callback(probe_rate_service):
    """Test registering a rate callback."""
    callback = MagicMock()
    probe_rate_service.register_rate_callback(callback)
    
    assert callback in probe_rate_service._rate_callbacks

def test_add_priority_peer(probe_rate_service):
    """Test adding a priority peer."""
    probe_rate_service.add_priority_peer("test-peer")
    
    assert "test-peer" in probe_rate_service._priority_peers

def test_remove_priority_peer(probe_rate_service):
    """Test removing a priority peer."""
    # Add then remove
    probe_rate_service.add_priority_peer("test-peer")
    assert "test-peer" in probe_rate_service._priority_peers
    
    probe_rate_service.remove_priority_peer("test-peer")
    assert "test-peer" not in probe_rate_service._priority_peers

def test_blacklist_peer(probe_rate_service):
    """Test blacklisting a peer."""
    probe_rate_service.blacklist_peer("bad-peer", duration=30.0)
    
    assert "bad-peer" in probe_rate_service._blacklist_peers
    assert "bad-peer" in probe_rate_service._blacklist_timestamps
    
    # Check that metrics were recorded
    probe_rate_service._metrics_collector.record_event.assert_called_once()

def test_is_blacklisted(probe_rate_service):
    """Test checking if a peer is blacklisted."""
    # Not blacklisted
    assert probe_rate_service.is_blacklisted("unknown-peer") is False
    
    # Blacklisted
    probe_rate_service.blacklist_peer("bad-peer")
    assert probe_rate_service.is_blacklisted("bad-peer") is True
    
    # Expired blacklist
    probe_rate_service._blacklist_timestamps["expired-peer"] = time.time() - 100  # 100s ago
    probe_rate_service._blacklist_peers.add("expired-peer")
    assert probe_rate_service.is_blacklisted("expired-peer") is False

def test_record_probe_result(probe_rate_service):
    """Test recording a probe result."""
    # Success
    probe_rate_service.record_probe_result("test-peer", True)
    
    assert "test-peer" in probe_rate_service._probe_history
    assert len(probe_rate_service._probe_history["test-peer"]) == 1
    assert probe_rate_service._probe_history["test-peer"][0][1] is True  # Success
    
    # Check that awareness service was updated
    probe_rate_service._awareness_service.record_success.assert_called_once_with("test-peer")
    
    # Check that metrics were recorded
    probe_rate_service._metrics_collector.record_counter.assert_called_once()
    
    # Failure
    probe_rate_service.record_probe_result("test-peer", False)
    
    assert len(probe_rate_service._probe_history["test-peer"]) == 2
    assert probe_rate_service._probe_history["test-peer"][1][1] is False  # Failure
    
    # Check that awareness service was updated
    probe_rate_service._awareness_service.record_failure.assert_called_once_with("test-peer")

def test_get_probe_count_normal(probe_rate_service):
    """Test getting probe count in normal conditions."""
    count = probe_rate_service.get_probe_count("test-peer")
    
    # Should use the awareness service's recommendation
    assert count == 3
    probe_rate_service._awareness_service.get_probe_count.assert_called_once_with("test-peer")

def test_get_probe_count_blacklisted(probe_rate_service):
    """Test that blacklisted peers get zero probes."""
    probe_rate_service.blacklist_peer("bad-peer")
    count = probe_rate_service.get_probe_count("bad-peer")
    
    assert count == 0

def test_get_probe_count_priority(probe_rate_service):
    """Test that priority peers get more probes."""
    probe_rate_service.add_priority_peer("important-peer")
    count = probe_rate_service.get_probe_count("important-peer")
    
    # Should be higher than normal
    assert count > 3

def test_get_probe_count_bandwidth_limit(probe_rate_service, mock_bandwidth_monitor):
    """Test that probe count is reduced when bandwidth is limited."""
    # Enable bandwidth limit
    probe_rate_service.set_bandwidth_control(enabled=True, threshold=40000)  # 40KB/s
    
    # Set bandwidth above threshold
    mock_bandwidth_monitor.get_current_rate.return_value = 80000  # 80KB/s (2x threshold)
    
    count = probe_rate_service.get_probe_count("test-peer")
    
    # Should be reduced due to bandwidth limit
    assert count < 3

def test_get_probe_count_history(probe_rate_service):
    """Test that probe count is increased for peers with high failure rates."""
    # Add history with high failure rate
    timestamp = time.time()
    probe_rate_service._probe_history["failing-peer"] = [
        (timestamp - 10, False),
        (timestamp - 8, False),
        (timestamp - 6, True),
        (timestamp - 4, False),
        (timestamp - 2, False)
    ]
    
    count = probe_rate_service.get_probe_count("failing-peer")
    
    # Should be higher than normal due to failures
    assert count > 3

def test_get_probe_interval_normal(probe_rate_service):
    """Test getting probe interval in normal conditions."""
    interval = probe_rate_service.get_probe_interval("test-peer")
    
    # Should be adjusted based on awareness
    awareness = probe_rate_service._awareness_service.get_awareness("test-peer")
    expected_interval = probe_rate_service._base_probe_interval * (awareness + 1) / 5
    
    assert abs(interval - expected_interval) < 0.1

def test_get_probe_interval_blacklisted(probe_rate_service):
    """Test that blacklisted peers get infinite interval."""
    probe_rate_service.blacklist_peer("bad-peer")
    interval = probe_rate_service.get_probe_interval("bad-peer")
    
    assert interval == float('inf')

def test_get_probe_interval_priority(probe_rate_service):
    """Test that priority peers get shorter intervals."""
    regular_interval = probe_rate_service.get_probe_interval("regular-peer")
    
    probe_rate_service.add_priority_peer("important-peer")
    priority_interval = probe_rate_service.get_probe_interval("important-peer")
    
    # Priority interval should be shorter
    assert priority_interval < regular_interval

def test_get_probe_interval_rtt(probe_rate_service, mock_latency_tracker):
    """Test that interval is adjusted based on RTT."""
    # Set high RTT
    mock_latency_tracker.get_rtt_stats.return_value = {"mean": 0.5, "median": 0.45, "stdev": 0.1}
    
    interval = probe_rate_service.get_probe_interval("slow-peer")
    
    # Should be higher due to high RTT
    assert interval > probe_rate_service._base_probe_interval

def test_get_probe_interval_bandwidth_limit(probe_rate_service, mock_bandwidth_monitor):
    """Test that interval is increased when bandwidth is limited."""
    # Enable bandwidth limit
    probe_rate_service.set_bandwidth_control(enabled=True, threshold=40000)  # 40KB/s
    
    # Set bandwidth above threshold
    mock_bandwidth_monitor.get_current_rate.return_value = 80000  # 80KB/s (2x threshold)
    
    interval = probe_rate_service.get_probe_interval("test-peer")
    
    # Should be increased due to bandwidth limit
    assert interval > probe_rate_service._base_probe_interval

def test_get_probe_interval_protocol_period(probe_rate_service, mock_timing_service):
    """Test that interval is coordinated with protocol period."""
    # Set extreme interval to test bounds
    max_awareness = 8
    probe_rate_service._awareness_service.get_awareness.return_value = max_awareness
    
    # This would make the interval very long
    interval = probe_rate_service.get_probe_interval("test-peer")
    
    # But it should be capped relative to protocol period
    assert interval <= mock_timing_service.get_protocol_period() * 0.8

def test_get_probe_success_rate(probe_rate_service):
    """Test getting probe success rate."""
    # No history
    assert probe_rate_service.get_probe_success_rate("unknown-peer") is None
    
    # Add mixed history
    timestamp = time.time()
    probe_rate_service._probe_history["mixed-peer"] = [
        (timestamp - 10, True),
        (timestamp - 8, False),
        (timestamp - 6, True),
        (timestamp - 4, False)
    ]
    
    # Success rate should be 2/4 = 0.5
    assert probe_rate_service.get_probe_success_rate("mixed-peer") == 0.5

def test_get_probing_stats(probe_rate_service):
    """Test getting probing statistics."""
    # Add some history
    timestamp = time.time()
    probe_rate_service._probe_history["peer1"] = [
        (timestamp - 10, True),
        (timestamp - 8, False)
    ]
    probe_rate_service._probe_history["peer2"] = [
        (timestamp - 6, True),
        (timestamp - 4, True)
    ]
    
    # Add a priority peer
    probe_rate_service.add_priority_peer("peer1")
    
    stats = probe_rate_service.get_probing_stats()
    
    # Check basic stats
    assert stats["base_probe_count"] == probe_rate_service._base_probe_count
    assert stats["base_probe_interval"] == probe_rate_service._base_probe_interval
    assert stats["priority_peer_count"] == 1
    assert stats["blacklisted_peer_count"] == 0
    
    # Check overall success rate (3/4 = 0.75)
    assert stats["overall_success_rate"] == 0.75
    
    # Check per-peer stats
    assert "peer1" in stats["peer_stats"]
    assert "peer2" in stats["peer_stats"]
    assert stats["peer_stats"]["peer1"]["success_rate"] == 0.5
    assert stats["peer_stats"]["peer2"]["success_rate"] == 1.0

def test_clear_history(probe_rate_service):
    """Test clearing probe history."""
    # Add some history
    timestamp = time.time()
    probe_rate_service._probe_history["peer1"] = [
        (timestamp - 100, True),
        (timestamp - 80, False),
        (timestamp - 10, True)
    ]
    probe_rate_service._probe_history["peer2"] = [
        (timestamp - 90, True),
        (timestamp - 5, True)
    ]
    
    # Clear old entries
    count = probe_rate_service.clear_history(older_than=timestamp - 50)
    
    # Should have cleared 2 entries
    assert count == 2
    
    # Check remaining history
    assert len(probe_rate_service._probe_history["peer1"]) == 1
    assert len(probe_rate_service._probe_history["peer2"]) == 1
    
    # Clear all history
    count = probe_rate_service.clear_history()
    
    # Should have cleared 2 more entries
    assert count == 2
    
    # History should be empty
    assert not probe_rate_service._probe_history

def test_notify_callbacks(probe_rate_service):
    """Test that callbacks are notified when probe rate changes."""
    callback1 = MagicMock()
    callback2 = MagicMock()
    
    probe_rate_service.register_rate_callback(callback1)
    probe_rate_service.register_rate_callback(callback2)
    
    # Get interval, which should trigger callbacks
    interval = probe_rate_service.get_probe_interval("test-peer")
    
    # Both callbacks should be called with peer and rate (1/interval)
    callback1.assert_called_once_with("test-peer", 1.0/interval)
    callback2.assert_called_once_with("test-peer", 1.0/interval)

def test_get_probe_count_bounds(probe_rate_service):
    """Test that probe count stays within bounds."""
    # Override awareness service to return extreme values
    probe_rate_service._awareness_service.get_probe_count.side_effect = [
        1,  # Below min
        20  # Above max
    ]
    
    # Should be capped at min
    count = probe_rate_service.get_probe_count("min-peer")
    assert count == probe_rate_service._probe_count_min
    
    # Should be capped at max
    count = probe_rate_service.get_probe_count("max-peer")
    assert count == probe_rate_service._probe_count_max

def test_get_probe_interval_bounds(probe_rate_service):
    """Test that probe interval stays within bounds."""
    # Test min bound by using very low awareness
    probe_rate_service._awareness_service.get_awareness.return_value = 0
    
    # Additional factors to push interval below min
    probe_rate_service._timing_service.get_protocol_period.return_value = 0.1
    probe_rate_service.add_priority_peer("min-peer")
    
    # Should be capped at min
    interval = probe_rate_service.get_probe_interval("min-peer")
    assert interval == probe_rate_service._probe_interval_min
    
    # Test max bound by using very high awareness and RTT
    probe_rate_service._awareness_service.get_awareness.return_value = 20
    probe_rate_service._latency_tracker.get_rtt_stats.return_value = {"mean": 5.0}
    
    # Additional factors to push interval above max
    probe_rate_service._timing_service.get_protocol_period.return_value = 10.0
    probe_rate_service._bandwidth_monitor.get_current_rate.return_value = 1000000
    probe_rate_service.set_bandwidth_control(enabled=True, threshold=10000)
    
    # Should be capped at max
    interval = probe_rate_service.get_probe_interval("max-peer")
    assert interval == probe_rate_service._probe_interval_max

def test_integration(probe_rate_service):
    """Test the integration of all probe rate features."""
    # Set up test peers with different characteristics
    normal_peer = "normal-peer"
    priority_peer = "priority-peer"
    blacklisted_peer = "blacklisted-peer"
    failing_peer = "failing-peer"
    high_rtt_peer = "high-rtt-peer"
    
    # Configure peers
    probe_rate_service.add_priority_peer(priority_peer)
    probe_rate_service.blacklist_peer(blacklisted_peer)
    
    # Add history
    timestamp = time.time()
    probe_rate_service._probe_history[failing_peer] = [
        (timestamp - 10, False),
        (timestamp - 8, False),
        (timestamp - 6, False)
    ]
    
    # Configure mock dependencies
    def get_rtt_stats_mock(peer_id):
        if peer_id == high_rtt_peer:
            return {"mean": 0.5}
        return {"mean": 0.1}
    
    probe_rate_service._latency_tracker.get_rtt_stats.side_effect = get_rtt_stats_mock
    
    # Get probe counts
    normal_count = probe_rate_service.get_probe_count(normal_peer)
    priority_count = probe_rate_service.get_probe_count(priority_peer)
    blacklisted_count = probe_rate_service.get_probe_count(blacklisted_peer)
    failing_count = probe_rate_service.get_probe_count(failing_peer)
    
    # Get probe intervals
    normal_interval = probe_rate_service.get_probe_interval(normal_peer)
    priority_interval = probe_rate_service.get_probe_interval(priority_peer)
    blacklisted_interval = probe_rate_service.get_probe_interval(blacklisted_peer)
    failing_interval = probe_rate_service.get_probe_interval(failing_peer)
    high_rtt_interval = probe_rate_service.get_probe_interval(high_rtt_peer)
    
    # Verify expected relationships
    assert priority_count > normal_count
    assert blacklisted_count == 0
    assert failing_count > normal_count
    
    assert priority_interval < normal_interval
    assert blacklisted_interval == float('inf')
    assert high_rtt_interval > normal_interval