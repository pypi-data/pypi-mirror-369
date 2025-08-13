"""
Unit tests for awareness service.
"""

import pytest
import time
from unittest.mock import MagicMock, AsyncMock, patch

from swim.lifeguard.awareness import AwarenessService, get_awareness_service

class TestAwarenessService:
    """Test cases for the AwarenessService class."""
    
    def test_initialization(self):
        """Test that AwarenessService initializes with correct default values."""
        min_awareness = 1
        max_awareness = 10
        service = AwarenessService(min_awareness=min_awareness, max_awareness=max_awareness)
        
        # Check that initial state is correct
        assert service._min_awareness == min_awareness
        assert service._max_awareness == max_awareness
        assert service._awareness == {}
        assert service._last_change == {}
    
    def test_get_awareness_default(self):
        """Test that get_awareness returns min_awareness for unknown peers."""
        service = AwarenessService(min_awareness=2, max_awareness=8)
        
        # Unknown peer should get min_awareness
        assert service.get_awareness("unknown_peer") == 2
    
    def test_record_success(self):
        """Test that record_success increases awareness correctly."""
        service = AwarenessService(min_awareness=0, max_awareness=5)
        
        # First success should set awareness to min + 1
        result = service.record_success("test_peer")
        assert result == 1
        assert service.get_awareness("test_peer") == 1
        
        # Second success should increase by 1
        result = service.record_success("test_peer")
        assert result == 2
        assert service.get_awareness("test_peer") == 2
        
        # Increase to max
        result = service.record_success("test_peer")
        result = service.record_success("test_peer")
        result = service.record_success("test_peer")
        # Should be capped at max
        assert result == 5
        assert service.get_awareness("test_peer") == 5
        
        # Further increases should be capped
        result = service.record_success("test_peer")
        assert result == 5
        assert service.get_awareness("test_peer") == 5
    
    def test_record_failure(self):
        """Test that record_failure decreases awareness correctly."""
        service = AwarenessService(min_awareness=0, max_awareness=5)
        
        # Set initial awareness to max
        service._awareness["test_peer"] = 5
        
        # First failure should reduce by 1
        result = service.record_failure("test_peer")
        assert result == 4
        assert service.get_awareness("test_peer") == 4
        
        # Multiple failures
        result = service.record_failure("test_peer")
        result = service.record_failure("test_peer")
        result = service.record_failure("test_peer")
        result = service.record_failure("test_peer")
        # Should be capped at min
        assert result == 0
        assert service.get_awareness("test_peer") == 0
        
        # Further decreases should be capped
        result = service.record_failure("test_peer")
        assert result == 0
        assert service.get_awareness("test_peer") == 0
    
    def test_get_suspicion_multiplier(self):
        """Test that get_suspicion_multiplier returns correct values."""
        service = AwarenessService(min_awareness=0, max_awareness=8)
        
        # Set up different awareness levels
        service._awareness["high"] = 8  # Max awareness
        service._awareness["medium"] = 4  # Mid awareness
        service._awareness["low"] = 0  # Min awareness
        
        # Check multipliers
        # Formula: multiplier = (max_awareness + 1) / (awareness + 1)
        
        # High awareness should have low multiplier (1.0)
        high_multiplier = service.get_suspicion_multiplier("high")
        assert high_multiplier == (8 + 1) / (8 + 1)  # 9/9 = 1.0
        
        # Medium awareness should have medium multiplier
        medium_multiplier = service.get_suspicion_multiplier("medium")
        assert medium_multiplier == (8 + 1) / (4 + 1)  # 9/5 = 1.8
        
        # Low awareness should have high multiplier
        low_multiplier = service.get_suspicion_multiplier("low")
        assert low_multiplier == (8 + 1) / (0 + 1)  # 9/1 = 9.0
    
    def test_get_probe_count(self):
        """Test that get_probe_count returns correct values."""
        service = AwarenessService(min_awareness=0, max_awareness=8)
        
        # Set up different awareness levels
        service._awareness["high"] = 8  # Max awareness
        service._awareness["medium"] = 4  # Mid awareness
        service._awareness["low"] = 0  # Min awareness
        
        # Check probe counts
        # Formula: 3 + (max_awareness - awareness) // 2
        
        # High awareness should have low probe count (3)
        high_count = service.get_probe_count("high")
        assert high_count == 3 + (8 - 8) // 2  # 3 + 0 = 3
        
        # Medium awareness should have medium probe count
        medium_count = service.get_probe_count("medium")
        assert medium_count == 3 + (8 - 4) // 2  # 3 + 2 = 5
        
        # Low awareness should have high probe count
        low_count = service.get_probe_count("low")
        assert low_count == 3 + (8 - 0) // 2  # 3 + 4 = 7
    
    def test_get_all_awareness(self):
        """Test that get_all_awareness returns a copy of the awareness dict."""
        service = AwarenessService()
        
        # Set up some awareness values
        service._awareness["peer1"] = 1
        service._awareness["peer2"] = 2
        
        # Get all awareness
        all_awareness = service.get_all_awareness()
        
        # Check it's a copy, not the original
        assert all_awareness is not service._awareness
        assert all_awareness == service._awareness
        
        # Modifying the copy should not affect the original
        all_awareness["peer3"] = 3
        assert "peer3" not in service._awareness
    
    def test_get_awareness_stats(self):
        """Test that get_awareness_stats returns correct statistics."""
        service = AwarenessService(min_awareness=0, max_awareness=10)
        
        # Test empty stats
        empty_stats = service.get_awareness_stats()
        assert empty_stats["tracked_peers"] == 0
        assert empty_stats["avg_awareness"] == 0
        
        # Set up some awareness values
        service._awareness["peer1"] = 2
        service._awareness["peer2"] = 4
        service._awareness["peer3"] = 6
        service._awareness["peer4"] = 8
        
        # Get stats
        stats = service.get_awareness_stats()
        
        # Check stats
        assert stats["tracked_peers"] == 4
        assert stats["min_awareness"] == 2
        assert stats["max_awareness"] == 8
        assert stats["avg_awareness"] == 5.0  # (2+4+6+8)/4 = 5.0
        assert stats["low_awareness_peers"] == 2  # peers with awareness < max/2 (< 5)
    
    def test_clear_old_entries(self):
        """Test that clear_old_entries removes old entries correctly."""
        service = AwarenessService()
        
        # Set up some awareness values with different timestamps
        service._awareness["old1"] = 1
        service._awareness["old2"] = 2
        service._awareness["new1"] = 3
        service._awareness["new2"] = 4
        
        # Set timestamps
        now = time.time()
        service._last_change["old1"] = now - 100
        service._last_change["old2"] = now - 200
        service._last_change["new1"] = now - 10
        service._last_change["new2"] = now - 20
        
        # Clear entries older than 50 seconds
        cleared = service.clear_old_entries(now - 50)
        
        # Check that only old entries were cleared
        assert cleared == 2
        assert "old1" not in service._awareness
        assert "old2" not in service._awareness
        assert "new1" in service._awareness
        assert "new2" in service._awareness
        
        # Check timestamps were also cleared
        assert "old1" not in service._last_change
        assert "old2" not in service._last_change
    
    def test_metrics_collection(self):
        """Test that metrics are recorded correctly."""
        # Create a mock metrics collector
        mock_collector = MagicMock()
        
        # Create awareness service with mock collector
        service = AwarenessService(metrics_collector=mock_collector)
        
        # Record success and failure
        service.record_success("test_peer")
        service.record_failure("test_peer")
        
        # Check that metrics were recorded
        assert mock_collector.record_gauge.call_count == 2
        
        # Verify first call (success)
        first_call = mock_collector.record_gauge.call_args_list[0]
        assert first_call[1]["name"] == "peer_awareness"
        assert first_call[1]["value"] == 1
        assert first_call[1]["labels"]["peer_id"] == "test_peer"
        
        # Verify second call (failure)
        second_call = mock_collector.record_gauge.call_args_list[1]
        assert second_call[1]["name"] == "peer_awareness"
        assert second_call[1]["value"] == 0
        assert second_call[1]["labels"]["peer_id"] == "test_peer"
    
    def test_get_awareness_service_singleton(self):
        """Test that get_awareness_service returns a singleton instance."""
        # Get the default service
        service1 = get_awareness_service()
        
        # Get it again
        service2 = get_awareness_service()
        
        # Should be the same instance
        assert service1 is service2
        
        # Reset for other tests
        import swim.lifeguard.awareness
        swim.lifeguard.awareness.default_awareness_service = None