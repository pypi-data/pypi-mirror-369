"""
Rate limiting utilities for SWIM P2P.

This module provides classes for rate limiting operations,
with support for token bucket algorithm, adaptive rate limiting,
and priority-based rate limiting.
"""

import time
import threading
import logging
from typing import Dict, Callable, Optional, List, Tuple, Any

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket rate limiter implementation.
    
    This class implements the token bucket algorithm for rate limiting.
    It allows for bursts of operations up to a maximum capacity,
    while maintaining a long-term rate limit.
    """
    
    def __init__(self, rate: float, capacity: float):
        """Initialize the token bucket.
        
        Args:
            rate: Token refill rate per second
            capacity: Maximum number of tokens the bucket can hold
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.RLock()
    
    def _refill(self) -> None:
        """Refill the token bucket based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Calculate new tokens based on elapsed time and rate
        new_tokens = elapsed * self.rate
        
        # Update tokens and timestamp
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
    
    def consume(self, tokens: float = 1.0) -> bool:
        """Consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_wait_time(self, tokens: float = 1.0) -> float:
        """Calculate the wait time until enough tokens are available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Wait time in seconds, or 0 if enough tokens are available
        """
        with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                return 0.0
            
            # Calculate time needed to refill the required tokens
            needed_tokens = tokens - self.tokens
            return needed_tokens / self.rate
    
    def set_rate(self, rate: float) -> None:
        """Update the token refill rate.
        
        Args:
            rate: New token refill rate per second
        """
        with self._lock:
            self._refill()  # Refill with old rate before changing
            self.rate = rate


class RateLimiter:
    """Rate limiter with support for multiple buckets and priorities.
    
    This class provides a flexible rate limiting system with support for
    different operation types, priorities, and adaptive rate limiting.
    """
    
    def __init__(self):
        """Initialize the rate limiter."""
        self._buckets: Dict[str, TokenBucket] = {}
        self._callbacks: Dict[str, List[Tuple[float, Callable]]] = {}
        self._lock = threading.RLock()
    
    def add_bucket(self, name: str, rate: float, capacity: float) -> None:
        """Add a new rate limiting bucket.
        
        Args:
            name: Bucket name/identifier
            rate: Token refill rate per second
            capacity: Maximum number of tokens the bucket can hold
        """
        with self._lock:
            self._buckets[name] = TokenBucket(rate, capacity)
            self._callbacks[name] = []
    
    def remove_bucket(self, name: str) -> None:
        """Remove a rate limiting bucket.
        
        Args:
            name: Bucket name/identifier
        """
        with self._lock:
            if name in self._buckets:
                del self._buckets[name]
            
            if name in self._callbacks:
                del self._callbacks[name]
    
    def register_callback(self, bucket_name: str, threshold: float, callback: Callable[[str, float, float], None]) -> None:
        """Register a callback for when rate limit is exceeded.
        
        Args:
            bucket_name: Bucket name/identifier
            threshold: Threshold ratio (0.0-1.0) of rate at which to trigger callback
            callback: Function to call with (bucket_name, current_rate, limit)
        """
        with self._lock:
            if bucket_name in self._callbacks:
                self._callbacks[bucket_name].append((threshold, callback))
    
    def check_rate_limit(self, bucket_name: str, tokens: float = 1.0) -> bool:
        """Check if an operation would exceed the rate limit.
        
        Args:
            bucket_name: Bucket name/identifier
            tokens: Number of tokens the operation would consume
            
        Returns:
            True if the operation is allowed, False if it would exceed the limit
        """
        with self._lock:
            if bucket_name not in self._buckets:
                # No rate limit defined for this bucket
                return True
            
            bucket = self._buckets[bucket_name]
            return bucket.consume(tokens)
    
    def get_wait_time(self, bucket_name: str, tokens: float = 1.0) -> float:
        """Get the wait time until an operation would be allowed.
        
        Args:
            bucket_name: Bucket name/identifier
            tokens: Number of tokens the operation would consume
            
        Returns:
            Wait time in seconds, or 0 if the operation is allowed now
        """
        with self._lock:
            if bucket_name not in self._buckets:
                # No rate limit defined for this bucket
                return 0.0
            
            bucket = self._buckets[bucket_name]
            return bucket.get_wait_time(tokens)
    
    def update_rate(self, bucket_name: str, rate: float) -> None:
        """Update the rate limit for a bucket.
        
        Args:
            bucket_name: Bucket name/identifier
            rate: New token refill rate per second
        """
        with self._lock:
            if bucket_name in self._buckets:
                old_rate = self._buckets[bucket_name].rate
                self._buckets[bucket_name].set_rate(rate)
                
                # Trigger callbacks if rate decreased significantly
                if rate < old_rate:
                    ratio = rate / old_rate
                    for threshold, callback in self._callbacks.get(bucket_name, []):
                        if ratio <= threshold:
                            try:
                                callback(bucket_name, rate, old_rate)
                            except Exception as e:
                                logger.error(f"Error in rate limit callback: {e}")
    
    def get_current_rate(self, bucket_name: str) -> Optional[float]:
        """Get the current rate limit for a bucket.
        
        Args:
            bucket_name: Bucket name/identifier
            
        Returns:
            Current token refill rate per second, or None if bucket doesn't exist
        """
        with self._lock:
            if bucket_name in self._buckets:
                return self._buckets[bucket_name].rate
            return None


class AdaptiveRateLimiter(RateLimiter):
    """Rate limiter that adapts based on network conditions.
    
    This class extends RateLimiter to automatically adjust rates
    based on network conditions and feedback.
    """
    
    def __init__(self, adaptation_factor: float = 0.2):
        """Initialize the adaptive rate limiter.
        
        Args:
            adaptation_factor: Factor by which to adjust rates (0.0-1.0)
        """
        super().__init__()
        self.adaptation_factor = adaptation_factor
        self._base_rates: Dict[str, float] = {}
        self._min_rates: Dict[str, float] = {}
        self._max_rates: Dict[str, float] = {}
    
    def add_bucket(self, name: str, rate: float, capacity: float, 
                  min_rate: Optional[float] = None, max_rate: Optional[float] = None) -> None:
        """Add a new rate limiting bucket with adaptation parameters.
        
        Args:
            name: Bucket name/identifier
            rate: Initial token refill rate per second
            capacity: Maximum number of tokens the bucket can hold
            min_rate: Minimum allowed rate (default: rate * 0.1)
            max_rate: Maximum allowed rate (default: rate * 10.0)
        """
        super().add_bucket(name, rate, capacity)
        
        with self._lock:
            self._base_rates[name] = rate
            self._min_rates[name] = min_rate if min_rate is not None else rate * 0.1
            self._max_rates[name] = max_rate if max_rate is not None else rate * 10.0
    
    def adapt_rate(self, bucket_name: str, success: bool, response_time: Optional[float] = None) -> None:
        """Adapt the rate based on operation success and response time.
        
        Args:
            bucket_name: Bucket name/identifier
            success: Whether the operation succeeded
            response_time: Optional response time in seconds
        """
        with self._lock:
            if bucket_name not in self._buckets:
                return
            
            current_rate = self._buckets[bucket_name].rate
            base_rate = self._base_rates[bucket_name]
            min_rate = self._min_rates[bucket_name]
            max_rate = self._max_rates[bucket_name]
            
            if not success:
                # Decrease rate on failure
                new_rate = max(min_rate, current_rate * (1 - self.adaptation_factor))
                self.update_rate(bucket_name, new_rate)
            elif response_time is not None:
                # Adjust based on response time
                expected_time = 1.0 / base_rate  # Expected time per operation
                
                if response_time > expected_time * 2:
                    # Response time too high, decrease rate
                    new_rate = max(min_rate, current_rate * (1 - self.adaptation_factor * 0.5))
                    self.update_rate(bucket_name, new_rate)
                elif response_time < expected_time * 0.5:
                    # Response time good, increase rate
                    new_rate = min(max_rate, current_rate * (1 + self.adaptation_factor * 0.2))
                    self.update_rate(bucket_name, new_rate)
    
    def reset_to_base_rate(self, bucket_name: str) -> None:
        """Reset a bucket's rate to its base rate.
        
        Args:
            bucket_name: Bucket name/identifier
        """
        with self._lock:
            if bucket_name in self._buckets and bucket_name in self._base_rates:
                self.update_rate(bucket_name, self._base_rates[bucket_name])


class PriorityRateLimiter(RateLimiter):
    """Rate limiter with support for operation priorities.
    
    This class extends RateLimiter to support different priorities
    for different operations, allowing high-priority operations
    to proceed even when low-priority operations are rate-limited.
    """
    
    def __init__(self, priority_levels: int = 3):
        """Initialize the priority rate limiter.
        
        Args:
            priority_levels: Number of priority levels (default: 3)
        """
        super().__init__()
        self.priority_levels = priority_levels
        self._priority_buckets: Dict[str, Dict[int, TokenBucket]] = {}
    
    def add_priority_bucket(self, name: str, rates: List[float], capacities: List[float]) -> None:
        """Add a new priority-based rate limiting bucket.
        
        Args:
            name: Bucket name/identifier
            rates: List of rates for each priority level (highest first)
            capacities: List of capacities for each priority level
            
        Raises:
            ValueError: If rates and capacities don't match priority levels
        """
        if len(rates) != self.priority_levels or len(capacities) != self.priority_levels:
            raise ValueError(f"Must provide {self.priority_levels} rates and capacities")
        
        with self._lock:
            self._priority_buckets[name] = {}
            for priority in range(self.priority_levels):
                self._priority_buckets[name][priority] = TokenBucket(rates[priority], capacities[priority])
    
    def check_rate_limit_with_priority(self, bucket_name: str, priority: int, tokens: float = 1.0) -> bool:
        """Check if an operation would exceed the rate limit for its priority.
        
        Args:
            bucket_name: Bucket name/identifier
            priority: Operation priority (0 = highest)
            tokens: Number of tokens the operation would consume
            
        Returns:
            True if the operation is allowed, False if it would exceed the limit
        """
        with self._lock:
            # First try standard buckets
            if super().check_rate_limit(bucket_name, tokens):
                return True
            
            # Then try priority buckets
            if bucket_name in self._priority_buckets and priority < self.priority_levels:
                if priority in self._priority_buckets[bucket_name]:
                    return self._priority_buckets[bucket_name][priority].consume(tokens)
            
            return False
    
    def get_wait_time_with_priority(self, bucket_name: str, priority: int, tokens: float = 1.0) -> float:
        """Get the wait time for a priority operation.
        
        Args:
            bucket_name: Bucket name/identifier
            priority: Operation priority (0 = highest)
            tokens: Number of tokens the operation would consume
            
        Returns:
            Wait time in seconds, or 0 if the operation is allowed now
        """
        with self._lock:
            # Check standard wait time
            standard_wait = super().get_wait_time(bucket_name, tokens)
            if standard_wait == 0.0:
                return 0.0
            
            # Check priority wait time
            if bucket_name in self._priority_buckets and priority < self.priority_levels:
                if priority in self._priority_buckets[bucket_name]:
                    return self._priority_buckets[bucket_name][priority].get_wait_time(tokens)
            
            return standard_wait