"""
Network awareness module for SWIM protocol.

This module implements the network awareness component of HashiCorp's Lifeguard
enhancements to the SWIM protocol, which helps reduce false positives in
failure detection by tracking the reliability of each node in the network.
"""

import time
import threading
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class AwarenessService:
    """
    Implements network awareness tracking for each node.
    
    The awareness value represents the reliability of a node in the network.
    Nodes with lower awareness values are treated with more caution,
    reducing the chance of false positive failure detections.
    """
    
    def __init__(
        self, 
        metrics_collector=None, 
        min_awareness: int = 0,
        max_awareness: int = 8
    ):
        """
        Initialize the awareness service.
        
        Args:
            metrics_collector: Optional metrics collector to record awareness metrics
            min_awareness: Minimum awareness value (default: 0)
            max_awareness: Maximum awareness value (default: 8)
        """
        # Dict to store awareness values for each peer
        self._awareness: Dict[str, int] = {}
        
        # Store timestamps of last awareness change
        self._last_change: Dict[str, float] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configuration
        self._min_awareness = min_awareness
        self._max_awareness = max_awareness
        
        # Optional metrics collector
        self._metrics_collector = metrics_collector
        
        logger.info(f"Awareness service initialized (min={min_awareness}, max={max_awareness})")
    
    def get_awareness(self, peer_id: str) -> int:
        """
        Get the current awareness value for a peer.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            Awareness value (higher means more reliability)
        """
        with self._lock:
            # Default to min_awareness if not yet tracked
            return self._awareness.get(peer_id, self._min_awareness)
    
    def record_success(self, peer_id: str) -> int:
        """
        Record a successful interaction with a peer.
        
        This increases the awareness value for the peer, indicating
        higher reliability.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            New awareness value
        """
        with self._lock:
            # Get current awareness value (default to min if not present)
            current = self._awareness.get(peer_id, self._min_awareness)
            
            # Increase awareness, capped at max_awareness
            new_value = min(current + 1, self._max_awareness)
            
            # Only update if the value changed
            if new_value != current:
                self._awareness[peer_id] = new_value
                self._last_change[peer_id] = time.time()
                
                # Make the awareness change more visible in logs
                logger.info(f"LIFEGUARD: Increased awareness for {peer_id}: {current} -> {new_value}")
                
                # Record metric if collector is available
                if self._metrics_collector:
                    self._metrics_collector.record_gauge(
                        name="peer_awareness",
                        value=new_value,
                        labels={"peer_id": peer_id}
                    )
            
            return new_value

    def record_failure(self, peer_id: str) -> int:
        """
        Record a failed interaction with a peer.
        
        This decreases the awareness value for the peer, indicating
        lower reliability.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            New awareness value
        """
        with self._lock:
            # Get current awareness value (default to min if not present)
            current = self._awareness.get(peer_id, self._min_awareness)
            
            # Decrease awareness, bounded at min_awareness
            new_value = max(current - 1, self._min_awareness)
            
            # Only update if the value changed
            if new_value != current:
                self._awareness[peer_id] = new_value
                self._last_change[peer_id] = time.time()
                
                # Make the awareness change more visible in logs
                logger.info(f"LIFEGUARD: Decreased awareness for {peer_id}: {current} -> {new_value}")
                
                # Record metric if collector is available
                if self._metrics_collector:
                    self._metrics_collector.record_gauge(
                        name="peer_awareness",
                        value=new_value,
                        labels={"peer_id": peer_id}
                    )
            
            return new_value
    
    def get_suspicion_multiplier(self, peer_id: str) -> float:
        """
        Get a multiplier for suspicion timeout based on awareness.
        
        Lower awareness values result in higher multipliers, giving
        less reliable nodes more time before being marked as suspect.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            Multiplier for suspicion timeout (1.0 or higher)
        """
        awareness = self.get_awareness(peer_id)
        
        # Calculate multiplier: lower awareness = higher multiplier
        # Formula: multiplier = (max_awareness + 1) / (awareness + 1)
        multiplier = (self._max_awareness + 1) / (awareness + 1)
        
        logger.debug(f"Suspicion multiplier for {peer_id} (awareness={awareness}): {multiplier:.2f}")
        
        return multiplier
    
    def get_probe_count(self, peer_id: str) -> int:
        """
        Get the number of indirect probes to use based on awareness.
        
        Lower awareness values result in more probes, increasing
        the chance of successful failure detection for less reliable nodes.
        
        Args:
            peer_id: Identifier of the peer
            
        Returns:
            Number of indirect probes to use
        """
        awareness = self.get_awareness(peer_id)
        
        # Base probe count: 3
        # Adjust by awareness: lower awareness = more probes
        # Formula: 3 + (max_awareness - awareness)
        probe_count = 3 + (self._max_awareness - awareness) // 2
        
        logger.debug(f"Probe count for {peer_id} (awareness={awareness}): {probe_count}")
        
        return probe_count
    
    def get_all_awareness(self) -> Dict[str, int]:
        """
        Get awareness values for all tracked peers.
        
        Returns:
            Dictionary mapping peer IDs to awareness values
        """
        with self._lock:
            return self._awareness.copy()
    
    def get_awareness_stats(self) -> Dict[str, any]:
        """
        Get statistics about awareness values.
        
        Returns:
            Dictionary with awareness statistics
        """
        with self._lock:
            if not self._awareness:
                return {
                    "tracked_peers": 0,
                    "avg_awareness": 0
                }
            
            values = list(self._awareness.values())
            
            return {
                "tracked_peers": len(values),
                "min_awareness": min(values),
                "max_awareness": max(values),
                "avg_awareness": sum(values) / len(values),
                "low_awareness_peers": sum(1 for v in values if v < self._max_awareness / 2)
            }
            
    def clear_old_entries(self, older_than: float) -> int:
        """
        Clear awareness entries that haven't changed recently.
        
        Args:
            older_than: Clear entries that haven't changed since this timestamp
            
        Returns:
            Number of entries cleared
        """
        with self._lock:
            to_remove = []
            
            for peer_id, last_change in self._last_change.items():
                if last_change < older_than:
                    to_remove.append(peer_id)
            
            for peer_id in to_remove:
                del self._awareness[peer_id]
                del self._last_change[peer_id]
            
            return len(to_remove)


# Initialize a global instance for easy import
default_awareness_service = None

def get_awareness_service(
    metrics_collector=None, 
    min_awareness: int = 0,
    max_awareness: int = 8
) -> AwarenessService:
    """
    Get or create the default awareness service.
    
    Args:
        metrics_collector: Optional metrics collector
        min_awareness: Minimum awareness value
        max_awareness: Maximum awareness value
        
    Returns:
        The default awareness service instance
    """
    global default_awareness_service
    
    if default_awareness_service is None:
        default_awareness_service = AwarenessService(
            metrics_collector=metrics_collector,
            min_awareness=min_awareness,
            max_awareness=max_awareness
        )
    
    return default_awareness_service