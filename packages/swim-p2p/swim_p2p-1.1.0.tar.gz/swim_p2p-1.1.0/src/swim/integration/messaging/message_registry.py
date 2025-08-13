"""
Message registry for persistent tracking of message lifecycle.

Stores message metadata and tracks the complete lifecycle from creation
to completion, integrating with the ACK system and reliability manager.
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict

logger = logging.getLogger(__name__)


class MessageState(Enum):
    """Complete message lifecycle states."""
    CREATED = "created"
    TRANSPORT_SENT = "transport_sent"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    FAILED = "failed"
    EXPIRED = "expired"
    COMPLETED = "completed"


@dataclass
class MessageRecord:
    """Complete message metadata record."""
    message_id: str
    sender_node: str
    receiver_node: str
    created_at: float
    message_size: int
    state: MessageState = MessageState.CREATED
    retry_count: int = 0
    max_retries: int = 3
    trace_id: Optional[str] = None
    workflow_id: Optional[str] = None
    
    # ACK tracking
    transport_ack_received: bool = False
    delivery_ack_received: bool = False
    processing_ack_received: bool = False
    transport_ack_timestamp: Optional[float] = None
    delivery_ack_timestamp: Optional[float] = None
    processing_ack_timestamp: Optional[float] = None
    
    # Timing metadata
    last_retry_at: Optional[float] = None
    completed_at: Optional[float] = None
    total_duration: Optional[float] = None
    
    # Error tracking
    last_error: Optional[str] = None
    error_count: int = 0
    
    def update_state(self, new_state: MessageState, error: Optional[str] = None):
        """Update message state with timestamp and error tracking."""
        old_state = self.state
        self.state = new_state
        
        if new_state in [MessageState.FAILED, MessageState.EXPIRED]:
            self.error_count += 1
            if error:
                self.last_error = error
        
        if new_state in [MessageState.PROCESSED, MessageState.COMPLETED, MessageState.FAILED, MessageState.EXPIRED]:
            self.completed_at = time.time()
            self.total_duration = self.completed_at - self.created_at
        
        logger.info(f"REGISTRY: Message {self.message_id} state change: {old_state.value} -> {new_state.value}")
        if error:
            logger.error(f"REGISTRY: Message {self.message_id} error: {error}")
    
    def record_ack(self, ack_type: str, success: bool):
        """Record ACK receipt with timestamp."""
        current_time = time.time()
        
        if ack_type == "transport":
            self.transport_ack_received = success
            self.transport_ack_timestamp = current_time
            if success:
                self.update_state(MessageState.TRANSPORT_SENT)
        elif ack_type == "delivery":
            self.delivery_ack_received = success
            self.delivery_ack_timestamp = current_time
            if success:
                self.update_state(MessageState.DELIVERED)
        elif ack_type == "processing":
            self.processing_ack_received = success
            self.processing_ack_timestamp = current_time
            if success:
                self.update_state(MessageState.PROCESSED)
        
        logger.info(f"REGISTRY: Message {self.message_id} {ack_type} ACK recorded: {success}")
    
    def is_expired(self, max_age: float) -> bool:
        """Check if message has expired based on age."""
        return time.time() - self.created_at > max_age
    
    def is_completed(self) -> bool:
        """Check if message is in a final state."""
        return self.state in [MessageState.PROCESSED, MessageState.COMPLETED, MessageState.FAILED, MessageState.EXPIRED]
    
    def get_ack_status(self) -> Dict[str, bool]:
        """Get current ACK status summary."""
        return {
            "transport": self.transport_ack_received,
            "delivery": self.delivery_ack_received,
            "processing": self.processing_ack_received
        }


class MessageRegistry:
    """
    Central registry for tracking message lifecycle and metadata.
    
    Provides persistent storage of message records with cleanup policies
    and query interfaces for debugging and monitoring.
    """
    
    def __init__(self, node_id: str, max_records: int = 10000):
        """
        Initialize message registry.
        
        Args:
            node_id: This node's identifier
            max_records: Maximum number of records to keep in memory
        """
        self.node_id = node_id
        self.max_records = max_records
        self._records: Dict[str, MessageRecord] = {}
        self._lock = asyncio.Lock()
        
        # Cleanup configuration
        self.completed_message_ttl = 300.0  # Keep completed messages for 5 minutes
        self.failed_message_ttl = 1800.0    # Keep failed messages for 30 minutes
        self.max_message_age = 3600.0       # Expire messages after 1 hour
        
        # Statistics
        self._stats = defaultdict(int)
        
        logger.info(f"REGISTRY: Initialized message registry for node {node_id}")
        logger.info(f"REGISTRY: Memory limit: {max_records} records, TTL policies: "
                   f"completed={self.completed_message_ttl}s, failed={self.failed_message_ttl}s")
    
    async def register_message(self, message_id: str, sender_node: str, receiver_node: str,
                              message_size: int, trace_id: Optional[str] = None,
                              workflow_id: Optional[str] = None, max_retries: int = 3) -> MessageRecord:
        """
        Register a new message in the registry.
        
        Args:
            message_id: Unique message identifier
            sender_node: Sending node identifier
            receiver_node: Receiving node identifier
            message_size: Size of message in bytes
            trace_id: Optional trace identifier
            workflow_id: Optional workflow identifier
            max_retries: Maximum retry attempts
            
        Returns:
            Created message record
        """
        async with self._lock:
            # Check memory limits
            if len(self._records) >= self.max_records:
                await self._emergency_cleanup()
            
            record = MessageRecord(
                message_id=message_id,
                sender_node=sender_node,
                receiver_node=receiver_node,
                created_at=time.time(),
                message_size=message_size,
                trace_id=trace_id,
                workflow_id=workflow_id,
                max_retries=max_retries
            )
            
            self._records[message_id] = record
            self._stats["messages_registered"] += 1
            
            logger.info(f"REGISTRY: Registered message {message_id} from {sender_node} to {receiver_node}, "
                       f"size={message_size} bytes, registry size: {len(self._records)}")
            
            if trace_id:
                logger.debug(f"REGISTRY: Message {message_id} trace_id: {trace_id}")
            if workflow_id:
                logger.debug(f"REGISTRY: Message {message_id} workflow_id: {workflow_id}")
            
            return record
    
    async def update_message_state(self, message_id: str, new_state: MessageState, 
                                  error: Optional[str] = None):
        """Update message state in registry."""
        async with self._lock:
            if message_id not in self._records:
                logger.warning(f"REGISTRY: Unknown message {message_id} for state update")
                return
            
            self._records[message_id].update_state(new_state, error)
            self._stats[f"state_{new_state.value}"] += 1
            
            if error:
                self._stats["errors_recorded"] += 1
    
    async def record_ack(self, message_id: str, ack_type: str, success: bool):
        """Record ACK receipt for a message."""
        async with self._lock:
            if message_id not in self._records:
                logger.warning(f"REGISTRY: Unknown message {message_id} for ACK {ack_type}")
                return
            
            self._records[message_id].record_ack(ack_type, success)
            self._stats[f"ack_{ack_type}_received"] += 1
            
            if not success:
                self._stats[f"ack_{ack_type}_failed"] += 1
    
    async def record_retry(self, message_id: str):
        """Record a retry attempt for a message."""
        async with self._lock:
            if message_id not in self._records:
                logger.warning(f"REGISTRY: Unknown message {message_id} for retry recording")
                return
            
            record = self._records[message_id]
            record.retry_count += 1
            record.last_retry_at = time.time()
            self._stats["retries_recorded"] += 1
            
            logger.info(f"REGISTRY: Recorded retry {record.retry_count}/{record.max_retries} "
                       f"for message {message_id}")
    
    async def get_message(self, message_id: str) -> Optional[MessageRecord]:
        """Get a specific message record."""
        async with self._lock:
            record = self._records.get(message_id)
            if record:
                logger.debug(f"REGISTRY: Retrieved message {message_id}, state: {record.state.value}")
            else:
                logger.debug(f"REGISTRY: Message {message_id} not found in registry")
            return record
    
    async def query_messages(self, sender_node: Optional[str] = None,
                           receiver_node: Optional[str] = None,
                           state: Optional[MessageState] = None,
                           workflow_id: Optional[str] = None,
                           since: Optional[float] = None,
                           limit: int = 100) -> List[MessageRecord]:
        """
        Query messages with filters for debugging and monitoring.
        
        Args:
            sender_node: Filter by sender
            receiver_node: Filter by receiver
            state: Filter by message state
            workflow_id: Filter by workflow
            since: Filter by creation time (timestamp)
            limit: Maximum number of results
            
        Returns:
            List of matching message records
        """
        async with self._lock:
            results = []
            
            for record in self._records.values():
                # Apply filters
                if sender_node and record.sender_node != sender_node:
                    continue
                if receiver_node and record.receiver_node != receiver_node:
                    continue
                if state and record.state != state:
                    continue
                if workflow_id and record.workflow_id != workflow_id:
                    continue
                if since and record.created_at < since:
                    continue
                
                results.append(record)
                
                if len(results) >= limit:
                    break
            
            logger.debug(f"REGISTRY: Query returned {len(results)} messages "
                        f"(filters: sender={sender_node}, receiver={receiver_node}, "
                        f"state={state}, workflow={workflow_id})")
            
            return results
    
    async def cleanup_expired_messages(self) -> int:
        """
        Clean up expired and old completed messages.
        
        Returns:
            Number of messages cleaned up
        """
        async with self._lock:
            current_time = time.time()
            to_remove = []
            
            for message_id, record in self._records.items():
                should_remove = False
                reason = ""
                
                # Check age-based expiry
                if record.is_expired(self.max_message_age):
                    should_remove = True
                    reason = f"expired (age: {current_time - record.created_at:.1f}s)"
                
                # Check TTL for completed messages
                elif record.state == MessageState.PROCESSED and record.completed_at:
                    if current_time - record.completed_at > self.completed_message_ttl:
                        should_remove = True
                        reason = f"completed TTL exceeded ({current_time - record.completed_at:.1f}s)"
                
                # Check TTL for failed messages
                elif record.state in [MessageState.FAILED, MessageState.EXPIRED] and record.completed_at:
                    if current_time - record.completed_at > self.failed_message_ttl:
                        should_remove = True
                        reason = f"failed TTL exceeded ({current_time - record.completed_at:.1f}s)"
                
                if should_remove:
                    to_remove.append((message_id, reason))
            
            # Remove expired messages
            for message_id, reason in to_remove:
                del self._records[message_id]
                self._stats["messages_cleaned"] += 1
                logger.debug(f"REGISTRY: Cleaned up message {message_id}: {reason}")
            
            if to_remove:
                logger.info(f"REGISTRY: Cleaned up {len(to_remove)} expired messages, "
                           f"registry size: {len(self._records)}")
            
            return len(to_remove)
    
    async def _emergency_cleanup(self):
        """Emergency cleanup when registry is full."""
        logger.warning(f"REGISTRY: Emergency cleanup triggered, registry at {len(self._records)}/{self.max_records}")
        
        # First, clean up expired messages
        cleaned = await self.cleanup_expired_messages()
        
        # If still over limit, remove oldest completed messages
        if len(self._records) >= self.max_records * 0.9:  # 90% threshold
            completed_messages = [
                (msg_id, record) for msg_id, record in self._records.items()
                if record.is_completed()
            ]
            
            # Sort by completion time (oldest first)
            completed_messages.sort(key=lambda x: x[1].completed_at or 0)
            
            # Remove oldest 25%
            to_remove = int(len(completed_messages) * 0.25)
            for i in range(min(to_remove, len(completed_messages))):
                msg_id, _ = completed_messages[i]
                del self._records[msg_id]
                cleaned += 1
        
        self._stats["emergency_cleanups"] += 1
        logger.warning(f"REGISTRY: Emergency cleanup completed, removed {cleaned} messages, "
                      f"registry size: {len(self._records)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics."""
        # Count messages by state
        state_counts = defaultdict(int)
        for record in self._records.values():
            state_counts[record.state.value] += 1
        
        # Calculate age distribution
        current_time = time.time()
        age_buckets = {"0-60s": 0, "1-5min": 0, "5-30min": 0, "30min+": 0}
        
        for record in self._records.values():
            age = current_time - record.created_at
            if age < 60:
                age_buckets["0-60s"] += 1
            elif age < 300:
                age_buckets["1-5min"] += 1
            elif age < 1800:
                age_buckets["5-30min"] += 1
            else:
                age_buckets["30min+"] += 1
        
        stats = {
            "registry_size": len(self._records),
            "max_records": self.max_records,
            "memory_utilization": f"{len(self._records) / self.max_records * 100:.1f}%",
            "state_distribution": dict(state_counts),
            "age_distribution": dict(age_buckets),
            "lifetime_stats": dict(self._stats),
            "node_id": self.node_id
        }
        
        logger.debug(f"REGISTRY: Statistics - Size: {len(self._records)}/{self.max_records} "
                    f"({stats['memory_utilization']}), States: {dict(state_counts)}")
        
        return stats
    
    async def get_pending_messages(self) -> List[MessageRecord]:
        """Get all messages that are not in a final state."""
        return await self.query_messages(
            state=None,  # Will filter below
            limit=self.max_records
        )
        
        # Filter for non-final states
        async with self._lock:
            pending = [
                record for record in self._records.values()
                if not record.is_completed()
            ]
            
            logger.debug(f"REGISTRY: Found {len(pending)} pending messages")
            return pending