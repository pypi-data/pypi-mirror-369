"""
Unit tests for rate limiter utilities.
"""

import pytest
import time
import threading
from unittest.mock import MagicMock, patch
from swim.utils.rate_limiter import (
    TokenBucket, RateLimiter,
    AdaptiveRateLimiter, PriorityRateLimiter
)


class TestTokenBucket:
    """Tests for the TokenBucket class."""
    
    def test_init(self):
        """Test initializing a token bucket."""
        bucket = TokenBucket(10.0, 100.0)
        assert bucket.rate == 10.0
        assert bucket.capacity == 100.0
        assert bucket.tokens == 100.0  # Should start full
    
    def test_consume(self):
        """Test consuming tokens."""
        bucket = TokenBucket(10.0, 100.0)
        
        # Should be able to consume tokens
        assert bucket.consume(50.0) is True
        assert bucket.tokens == 50.0
        
        # Should be able to consume more tokens
        assert bucket.consume(30.0) is True
        assert bucket.tokens == 20.0
        
        # Should not be able to consume more than available
        assert bucket.consume(30.0) is False
        assert bucket.tokens == 20.0  # Tokens unchanged
    
    def test_refill(self):
        """Test token refill over time."""
        bucket = TokenBucket(10.0, 100.0)
        
        # Consume some tokens
        assert bucket.consume(80.0) is True
        assert bucket.tokens == 20.0
        
        # Wait for refill
        with patch.object(bucket, 'last_refill', time.time() - 1.0):  # Mock 1 second passing
            # This should trigger a refill of 10 tokens (rate * time)
            assert bucket.consume(25.0) is True
            assert bucket.tokens == 5.0  # 20 + 10 - 25
    
    def test_get_wait_time(self):
        """Test getting wait time."""
        bucket = TokenBucket(10.0, 100.0)
        
        # Consume most tokens
        assert bucket.consume(95.0) is True
        assert bucket.tokens == 5.0
        
        # Should need to wait for more tokens
        wait_time = bucket.get_wait_time(10.0)
        assert wait_time > 0.0
        assert wait_time <= 0.5  # Need 5 more tokens at 10 tokens/sec = 0.5 sec
        
        # No wait time if enough tokens
        assert bucket.get_wait_time(5.0) == 0.0
    
    def test_set_rate(self):
        """Test changing the token refill rate."""
        bucket = TokenBucket(10.0, 100.0)
        
        # Consume some tokens
        assert bucket.consume(50.0) is True
        assert bucket.tokens == 50.0
        
        # Change rate
        bucket.set_rate(20.0)
        assert bucket.rate == 20.0
        
        # Wait for refill at new rate
        with patch.object(bucket, 'last_refill', time.time() - 1.0):  # Mock 1 second passing
            # This should trigger a refill of 20 tokens (new_rate * time)
            assert bucket.consume(60.0) is True
            assert bucket.tokens == 10.0  # 50 + 20 - 60


class TestRateLimiter:
    """Tests for the RateLimiter class."""
    
    def test_add_bucket(self):
        """Test adding a rate limiting bucket."""
        limiter = RateLimiter()
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Verify bucket was added
        assert "test" in limiter._buckets
        assert isinstance(limiter._buckets["test"], TokenBucket)
        assert limiter._buckets["test"].rate == 10.0
        assert limiter._buckets["test"].capacity == 100.0
    
    def test_remove_bucket(self):
        """Test removing a rate limiting bucket."""
        limiter = RateLimiter()
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Verify bucket was added
        assert "test" in limiter._buckets
        
        # Remove bucket
        limiter.remove_bucket("test")
        
        # Verify bucket was removed
        assert "test" not in limiter._buckets
    
    def test_check_rate_limit(self):
        """Test checking rate limit."""
        limiter = RateLimiter()
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Should be able to consume tokens
        assert limiter.check_rate_limit("test", 50.0) is True
        
        # Should be able to consume more tokens
        assert limiter.check_rate_limit("test", 30.0) is True
        
        # Should not be able to consume more than available
        assert limiter.check_rate_limit("test", 30.0) is False
        
        # Non-existent bucket should not be rate limited
        assert limiter.check_rate_limit("nonexistent", 1.0) is True
    
    def test_get_wait_time(self):
        """Test getting wait time."""
        limiter = RateLimiter()
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Consume most tokens
        assert limiter.check_rate_limit("test", 95.0) is True
        
        # Should need to wait for more tokens
        wait_time = limiter.get_wait_time("test", 10.0)
        assert wait_time > 0.0
        assert wait_time <= 0.5  # Need 5 more tokens at 10 tokens/sec = 0.5 sec
        
        # No wait time if enough tokens
        assert limiter.get_wait_time("test", 5.0) == 0.0
        
        # Non-existent bucket should have no wait time
        assert limiter.get_wait_time("nonexistent", 1.0) == 0.0
    
    def test_update_rate(self):
        """Test updating rate limit."""
        limiter = RateLimiter()
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Update rate
        limiter.update_rate("test", 20.0)
        
        # Verify rate was updated
        assert limiter.get_current_rate("test") == 20.0
        
        # Non-existent bucket should be ignored
        limiter.update_rate("nonexistent", 30.0)
    
    def test_register_callback(self):
        """Test registering a callback."""
        limiter = RateLimiter()
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Register callback
        callback = MagicMock()
        limiter.register_callback("test", 0.5, callback)
        
        # Verify callback was registered
        assert len(limiter._callbacks["test"]) == 1
        assert limiter._callbacks["test"][0][0] == 0.5
        assert limiter._callbacks["test"][0][1] == callback
        
        # Update rate to trigger callback
        limiter.update_rate("test", 4.0)  # 4.0 / 10.0 = 0.4, which is below threshold of 0.5
        
        # Verify callback was called
        callback.assert_called_once_with("test", 4.0, 10.0)


class TestAdaptiveRateLimiter:
    """Tests for the AdaptiveRateLimiter class."""
    
    def test_add_bucket(self):
        """Test adding a bucket with adaptation parameters."""
        limiter = AdaptiveRateLimiter()
        limiter.add_bucket("test", 10.0, 100.0, min_rate=2.0, max_rate=20.0)
        
        # Verify bucket was added with adaptation parameters
        assert "test" in limiter._buckets
        assert limiter._base_rates["test"] == 10.0
        assert limiter._min_rates["test"] == 2.0
        assert limiter._max_rates["test"] == 20.0
    
    def test_add_bucket_default_limits(self):
        """Test adding a bucket with default adaptation limits."""
        limiter = AdaptiveRateLimiter()
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Verify default limits
        assert limiter._min_rates["test"] == 1.0  # 10.0 * 0.1
        assert limiter._max_rates["test"] == 100.0  # 10.0 * 10.0
    
    def test_adapt_rate_failure(self):
        """Test adapting rate on failure."""
        limiter = AdaptiveRateLimiter(adaptation_factor=0.2)
        limiter.add_bucket("test", 10.0, 100.0, min_rate=1.0, max_rate=20.0)
        
        # Adapt rate on failure
        limiter.adapt_rate("test", False)
        
        # Verify rate was decreased
        new_rate = limiter.get_current_rate("test")
        assert new_rate == 8.0  # 10.0 * (1 - 0.2)
    
    def test_adapt_rate_slow_response(self):
        """Test adapting rate on slow response."""
        limiter = AdaptiveRateLimiter(adaptation_factor=0.2)
        limiter.add_bucket("test", 10.0, 100.0, min_rate=1.0, max_rate=20.0)
        
        # Adapt rate on slow response
        # Expected time per operation is 1.0 / 10.0 = 0.1 seconds
        # Response time is 0.25 seconds, which is > 0.1 * 2
        limiter.adapt_rate("test", True, 0.25)
        
        # Verify rate was decreased
        new_rate = limiter.get_current_rate("test")
        assert new_rate == 9.0  # 10.0 * (1 - 0.2 * 0.5)
    
    def test_adapt_rate_fast_response(self):
        """Test adapting rate on fast response."""
        limiter = AdaptiveRateLimiter(adaptation_factor=0.2)
        limiter.add_bucket("test", 10.0, 100.0, min_rate=1.0, max_rate=20.0)
        
        # Adapt rate on fast response
        # Expected time per operation is 1.0 / 10.0 = 0.1 seconds
        # Response time is 0.04 seconds, which is < 0.1 * 0.5
        limiter.adapt_rate("test", True, 0.04)
        
        # Verify rate was increased
        new_rate = limiter.get_current_rate("test")
        assert new_rate == 10.4  # 10.0 * (1 + 0.2 * 0.2)
    
    def test_reset_to_base_rate(self):
        """Test resetting to base rate."""
        limiter = AdaptiveRateLimiter()
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Change rate
        limiter.update_rate("test", 5.0)
        assert limiter.get_current_rate("test") == 5.0
        
        # Reset to base rate
        limiter.reset_to_base_rate("test")
        assert limiter.get_current_rate("test") == 10.0


class TestPriorityRateLimiter:
    """Tests for the PriorityRateLimiter class."""
    
    def test_add_priority_bucket(self):
        """Test adding a priority bucket."""
        limiter = PriorityRateLimiter(priority_levels=3)
        limiter.add_priority_bucket(
            "test",
            rates=[20.0, 10.0, 5.0],
            capacities=[200.0, 100.0, 50.0]
        )
        
        # Verify priority buckets were added
        assert "test" in limiter._priority_buckets
        assert len(limiter._priority_buckets["test"]) == 3
        
        # Verify bucket parameters
        assert limiter._priority_buckets["test"][0].rate == 20.0
        assert limiter._priority_buckets["test"][1].rate == 10.0
        assert limiter._priority_buckets["test"][2].rate == 5.0
        
        assert limiter._priority_buckets["test"][0].capacity == 200.0
        assert limiter._priority_buckets["test"][1].capacity == 100.0
        assert limiter._priority_buckets["test"][2].capacity == 50.0
    
    def test_add_priority_bucket_invalid(self):
        """Test adding a priority bucket with invalid parameters."""
        limiter = PriorityRateLimiter(priority_levels=3)
        
        # Not enough rates
        with pytest.raises(ValueError):
            limiter.add_priority_bucket(
                "test",
                rates=[20.0, 10.0],  # Only 2, need 3
                capacities=[200.0, 100.0, 50.0]
            )
        
        # Not enough capacities
        with pytest.raises(ValueError):
            limiter.add_priority_bucket(
                "test",
                rates=[20.0, 10.0, 5.0],
                capacities=[200.0, 100.0]  # Only 2, need 3
            )
    
    def test_check_rate_limit_with_priority(self):
        """Test checking rate limit with priority."""
        limiter = PriorityRateLimiter(priority_levels=3)
        
        # Add standard bucket
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Add priority bucket
        limiter.add_priority_bucket(
            "test",
            rates=[20.0, 10.0, 5.0],
            capacities=[200.0, 100.0, 50.0]
        )
        
        # Consume all tokens from standard bucket
        assert limiter.check_rate_limit("test", 100.0) is True
        assert limiter.check_rate_limit("test", 1.0) is False
        
        # Should still be able to use priority bucket for high priority
        assert limiter.check_rate_limit_with_priority("test", 0, 50.0) is True
        
        # Consume all tokens from high priority bucket
        assert limiter.check_rate_limit_with_priority("test", 0, 150.0) is True
        assert limiter.check_rate_limit_with_priority("test", 0, 1.0) is False
        
        # Should still be able to use medium priority bucket
        assert limiter.check_rate_limit_with_priority("test", 1, 50.0) is True
    
    def test_get_wait_time_with_priority(self):
        """Test getting wait time with priority."""
        limiter = PriorityRateLimiter(priority_levels=3)
        
        # Add standard bucket
        limiter.add_bucket("test", 10.0, 100.0)
        
        # Add priority bucket
        limiter.add_priority_bucket(
            "test",
            rates=[20.0, 10.0, 5.0],
            capacities=[200.0, 100.0, 50.0]
        )
        
        # Consume all tokens from standard bucket
        assert limiter.check_rate_limit("test", 100.0) is True
        
        # Standard wait time should be positive
        assert limiter.get_wait_time("test", 10.0) > 0.0
        
        # High priority wait time should be 0
        assert limiter.get_wait_time_with_priority("test", 0, 10.0) == 0.0
        
        # Consume all tokens from high priority bucket
        assert limiter.check_rate_limit_with_priority("test", 0, 200.0) is True
        
        # High priority wait time should now be positive
        assert limiter.get_wait_time_with_priority("test", 0, 10.0) > 0.0
        
        # Medium priority wait time should still be 0
        assert limiter.get_wait_time_with_priority("test", 1, 10.0) == 0.0