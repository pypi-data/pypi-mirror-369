"""
Unified reliability manager for ZMQ messaging with SWIM integration.

This is the core coordinator that orchestrates all reliability mechanisms
including message tracking, ACK handling, and integration with SWIM membership.
"""

import asyncio
import time
import uuid
import logging
import random
import threading
import json # Added for _test_connection    
from typing import Dict, Optional, Callable, Any, Set, Tuple, List
from dataclasses import dataclass
from enum import Enum, auto

# Import AckSystem for type hinting
from swim.integration.messaging.ack_system import AckSystem, AckType

logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """Message delivery status through the three-tier ACK system."""
    PENDING = auto()           # Message created, not yet sent
    TRANSPORT_CONFIRMED = auto()  # ZMQ confirms message left sender buffer
    DELIVERED = auto()         # Receiver confirms message arrived
    PROCESSED = auto()         # Receiver confirms message was processed
    FAILED = auto()           # Message delivery failed
    EXPIRED = auto()          # Message timed out


@dataclass
class PendingMessage:
    """Tracks a message through its complete lifecycle."""
    message_id: str
    target_node: str # This is the ZMQ address of the target
    message_data: bytes
    created_at: float
    last_attempt_at: float
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    trace_id: Optional[str] = None
    requires_ordering: bool = False
    workflow_id: Optional[str] = None

    def is_expired(self, timeout_seconds: float = 30.0) -> bool:
        """Check if message has exceeded its lifetime."""
        return time.time() - self.created_at > timeout_seconds

    def should_retry(self) -> bool:
        """Check if message should be retried."""
        return (self.retry_count < self.max_retries and
                self.status in [MessageStatus.PENDING, MessageStatus.TRANSPORT_CONFIRMED, MessageStatus.FAILED] and # Allow retry even if transport confirmed but no delivery
                not self.is_expired())

    def calculate_retry_delay(self) -> float:
        """Calculate exponential backoff with jitter for retry delay."""
        base_delay = 0.1  # 100ms base
        max_delay = 5.0   # 5 second cap

        # Exponential backoff: 100ms, 200ms, 400ms, 800ms, etc.
        backoff_delay = base_delay * (2 ** self.retry_count)

        # Add jitter (±25%) to prevent thundering herd
        jitter = random.uniform(0.75, 1.25)

        # Apply jitter and cap at max_delay
        return min(backoff_delay * jitter, max_delay)


class ReliabilityManager:
    """
    Core coordinator for reliable message delivery.

    Manages message lifecycle from creation to completion, coordinates
    with SWIM membership for connection health, and provides retry logic.
    """

    def __init__(self, node_id: str): # node_id is this node's SWIM ID
        """
        Initialize the reliability manager.

        Args:
            node_id: Identifier for this node (SWIM address format)
        """
        self.node_id = node_id
        self._pending_messages: Dict[str, PendingMessage] = {}
        self._ack_waiters: Dict[str, asyncio.Event] = {}
        self._lock = asyncio.Lock()
        self._thread_safe_lock = threading.Lock() 


        # Callbacks for integration with other components
        self.transport_send_callback: Optional[Callable[[str, bytes], Any]] = None # Expects ZMQ address, message_data
        self.swim_membership_callback: Optional[Callable[[str], bool]] = None # Expects ZMQ address, returns if alive
        self.circuit_breaker_callback: Optional[Callable[[str], bool]] = None # Expects ZMQ address, returns if closed
        self.connection_manager_callback: Optional[Any] = None # ConnectionManager instance
        self.ack_system_callback: Optional[AckSystem] = None # MODIFIED: Added AckSystem callback

        # Configuration
        self.default_timeout = 30.0
        self.cleanup_interval = 60.0
        self.max_pending_messages = 10000

        # Background tasks
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
        self._retry_task: Optional[asyncio.Task] = None

        logger.info(f"RELIABILITY: Initialized ReliabilityManager for node {node_id}")
        logger.info(f"REGISTRY: Central message registry initialized with capacity {self.max_pending_messages}")

    async def start(self):
        """Start the reliability manager background tasks."""
        if self._running:
            logger.warning("RELIABILITY: Already running, ignoring start request")
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._retry_task = asyncio.create_task(self._retry_loop())

        logger.info("RELIABILITY: Started background tasks")
        logger.info("TIMEOUT_POLICY: Cleanup interval set to {:.1f}s, default message timeout {:.1f}s".format(
            self.cleanup_interval, self.default_timeout))

    async def stop(self):
        """Stop the reliability manager and cleanup resources."""
        logger.info("RELIABILITY: Stopping reliability manager")
        self._running = False

        # Cancel background tasks
        for task in [self._cleanup_task, self._retry_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Fail all pending messages
        async with self._lock:
            pending_count = len(self._pending_messages)
            for msg_id, message in list(self._pending_messages.items()): # Iterate over copy
                logger.warning(f"REGISTRY: Failing pending message {msg_id} to {message.target_node} due to shutdown")
                if msg_id in self._ack_waiters:
                    self._ack_waiters[msg_id].set()
                # MODIFIED: Notify AckSystem if message was registered
                if self.ack_system_callback and msg_id in self.ack_system_callback._pending_acks:
                    logger.info(f"TIMEOUT_POLICY: Notifying AckSystem & cleaning its tracking for expired message {msg_id}")
                    # Simulate a processing failure due to timeout for AckSystem's perspective
                    await self.ack_system_callback._notify_reliability_manager(msg_id, AckType.PROCESSING, False)
                    self.ack_system_callback._cleanup_message_tracking(msg_id)

            self._pending_messages.clear()
            self._ack_waiters.clear()

        logger.info(f"RELIABILITY: Stopped, failed {pending_count} pending messages")

    def set_transport_callback(self, callback: Callable[[str, bytes], Any]):
        """Set the callback for sending messages via transport."""
        self.transport_send_callback = callback
        logger.info("INTEGRATION: ZMQ transport callback configured")

    def set_swim_membership_callback(self, callback: Callable[[str], bool]):
        """Set callback to check if a node is alive via SWIM."""
        self.swim_membership_callback = callback
        logger.info("SWIM_INTEGRATION: SWIM membership callback configured")

    def set_circuit_breaker_callback(self, callback: Callable[[str], bool]):
        """Set callback to check circuit breaker status."""
        self.circuit_breaker_callback = callback
        logger.info("CIRCUIT_BREAKER: Circuit breaker integration configured")

    def set_connection_manager_callback(self, callback: Any):  # ConnectionManager instance
        """Set callback to connection manager for readiness checks."""
        self.connection_manager_callback = callback
        logger.info("CONNECTION_MANAGER: Connection manager integration configured")

    def set_ack_system_callback(self, callback: AckSystem):
        """Set the callback for interacting with the AckSystem."""
        self.ack_system_callback = callback
        logger.info("INTEGRATION: AckSystem callback configured for ReliabilityManager")

    async def send_reliable(self, target_node: str, message_data: bytes, # target_node is ZMQ address
                        trace_id: Optional[str] = None,
                        workflow_id: Optional[str] = None,
                        requires_ordering: bool = False,
                        timeout: float = 30.0,
                        message_id_override: Optional[str] = None) -> bool: # MODIFIED: Added message_id_override
        """
        Send a message with reliability guarantees and improved recovery handling.

        Args:
            target_node: Target ZMQ node identifier ("host:port")
            message_data: Message payload
            trace_id: Optional trace ID for correlation
            workflow_id: Optional workflow context
            requires_ordering: Whether message requires ordering
            timeout: Timeout in seconds
            message_id_override: Optional message ID to use for tracking (ensures consistency with payload ID)

        Returns:
            True if message was processed successfully, False otherwise
        """
        logger.info(f"API: Sending reliable message to ZMQ node {target_node}, size={len(message_data)} bytes, "
                f"trace_id={trace_id}, workflow_id={workflow_id}, ordering={requires_ordering}")

        if not self.transport_send_callback:
            logger.error("API: No transport callback configured, message send failed")
            return False

        # Check connection readiness via ConnectionManager (expects ZMQ address)
        proceed_with_send_attempt = True
        if self.connection_manager_callback:
            if not self.connection_manager_callback.can_send_to_node(target_node):
                # MODIFIED: If CM says not ready, but SWIM says alive, let retry loop handle it after queuing.
                # Only fail immediately if SWIM also says not alive or CM has no info AND SWIM is not available.
                is_swim_alive = self.swim_membership_callback(target_node) if self.swim_membership_callback else False
                if not is_swim_alive: # If not ready AND not SWIM alive, then fail fast.
                    logger.warning(f"CONNECTION_READINESS: Connection to ZMQ node {target_node} not ready AND SWIM reports not alive. Failing message.")
                    proceed_with_send_attempt = False # Fail fast
                else:
                    logger.warning(f"CONNECTION_READINESS: Connection to ZMQ node {target_node} not ready, but SWIM reports ALIVE. Will queue and retry.")
                    # proceed_with_send_attempt remains True, message will be queued and retried.
            else:
                logger.debug(f"CONNECTION_READINESS: Connection to ZMQ node {target_node} verified ready")
        
        if not proceed_with_send_attempt: # Only if explicitly decided to fail fast
            return False

        # Check if target node is alive via SWIM (expects ZMQ address, maps internally)
        if self.swim_membership_callback:
            if not self.swim_membership_callback(target_node):
                logger.warning(f"SWIM_INTEGRATION: Target ZMQ node {target_node} is not alive according to SWIM, rejecting message")
                return False # Fail fast if SWIM says it's dead. Retries won't help.
            else:
                logger.debug(f"SWIM_INTEGRATION: Target ZMQ node {target_node} confirmed alive by SWIM")

        # Check circuit breaker status (expects ZMQ address)
        if self.circuit_breaker_callback:
            if not self.circuit_breaker_callback(target_node):
                logger.warning(f"CIRCUIT_BREAKER: Circuit open for ZMQ node {target_node}, failing message immediately")
                return False # Fail fast if circuit is open.
            else:
                logger.debug(f"CIRCUIT_BREAKER: Circuit closed for ZMQ node {target_node}, proceeding with send")

        message_id = message_id_override if message_id_override else str(uuid.uuid4()) # MODIFIED use override
        message = PendingMessage(
            message_id=message_id,
            target_node=target_node, # ZMQ address
            message_data=message_data,
            created_at=time.time(),
            last_attempt_at=time.time(), # Will be updated before actual send
            trace_id=trace_id,
            workflow_id=workflow_id,
            requires_ordering=requires_ordering
        )

        async with self._lock:
            if len(self._pending_messages) >= self.max_pending_messages:
                logger.error(f"REGISTRY: Maximum pending messages limit ({self.max_pending_messages}) reached, rejecting message")
                return False

            self._pending_messages[message_id] = message
            self._ack_waiters[message_id] = asyncio.Event()
            logger.info(f"REGISTRY: Registered message {message_id} to ZMQ {target_node}, pending count: {len(self._pending_messages)}")

            if self.ack_system_callback:
                self.ack_system_callback.register_outgoing_message(message_id)

        try:
            await self._send_message(message) # This will update last_attempt_at

            logger.debug(f"ACK_BRIDGE: Waiting for processing ACK for message {message_id} to ZMQ {target_node}, timeout={timeout}s")
            try:
                await asyncio.wait_for(
                    self._ack_waiters[message_id].wait(),
                    timeout=timeout
                )

                final_message = self._pending_messages.get(message_id)
                success = final_message and final_message.status == MessageStatus.PROCESSED

                if success:
                    logger.info(f"API: Message {message_id} to ZMQ {target_node} processed successfully")
                else:
                    final_status_name = final_message.status.name if final_message else 'UNKNOWN_OR_CLEANED_UP'
                    logger.warning(f"API: Message {message_id} to ZMQ {target_node} did not complete successfully. Final Status: {final_status_name}")
                    if final_message: self._log_ack_failure_stage(final_message)

                return success

            except asyncio.TimeoutError:
                logger.warning(f"TIMEOUT_POLICY: Message {message_id} to ZMQ {target_node} timed out after {timeout}s waiting for processing ACK.")
                await self._update_message_status(message_id, MessageStatus.EXPIRED) 
                if self.ack_system_callback and message_id in self.ack_system_callback._pending_acks: 
                    await self.ack_system_callback._notify_reliability_manager(message_id, AckType.PROCESSING, False) 
                    self.ack_system_callback._cleanup_message_tracking(message_id)
                return False

        finally:
            async with self._lock:
                self._pending_messages.pop(message_id, None)
                self._ack_waiters.pop(message_id, None)
                logger.debug(f"REGISTRY: Cleaned up reliability tracking for message {message_id}, pending count: {len(self._pending_messages)}")

    async def _test_connection(self, target_node: str) -> bool:
        """ Not currently used in send_reliable, kept for completeness """
        logger.info(f"CONNECTION_TEST: Testing connection to recently recovered node {target_node}")
        test_message_id = str(uuid.uuid4())
        test_message_data = json.dumps({
            "type": "CONNECTION_TEST", "id": test_message_id, "timestamp": time.time()
        }).encode('utf-8')
        try:
            if not self.transport_send_callback: return False
            await self.transport_send_callback(target_node, test_message_data)
            await asyncio.sleep(2.0) # Simplified wait
            logger.info(f"CONNECTION_TEST: Connection test succeeded for {target_node}")
            return True
        except Exception as e:
            logger.error(f"CONNECTION_TEST: Connection test failed for {target_node}: {e}")
            return False

    def _log_ack_failure_stage(self, message: PendingMessage):
        """Log detailed information about which ACK stage failed."""
        if message.status == MessageStatus.TRANSPORT_CONFIRMED:
            logger.error(f"ACK_FAILURE_RM: Message {message.message_id} to {message.target_node} succeeded TRANSPORT_CONFIRMED, but failed before/at DELIVERY ACK.")
        elif message.status == MessageStatus.DELIVERED:
            logger.error(f"ACK_FAILURE_RM: Message {message.message_id} to {message.target_node} was DELIVERED, but failed before/at PROCESSING ACK.")
        elif message.status == MessageStatus.PENDING: 
            logger.error(f"ACK_FAILURE_RM: Message {message.message_id} to {message.target_node} failed before TRANSPORT_CONFIRMED.")
        elif message.status == MessageStatus.FAILED:
             logger.error(f"ACK_FAILURE_RM: Message {message.message_id} to {message.target_node} explicitly FAILED. Check previous logs for reason.")
        elif message.status == MessageStatus.EXPIRED:
             logger.error(f"ACK_FAILURE_RM: Message {message.message_id} to {message.target_node} EXPIRED. Likely due to ACK timeout.")
        else:
            logger.error(f"ACK_FAILURE_RM: Message {message.message_id} to {message.target_node} in unexpected state {message.status.name} at failure point.")

    async def _send_message(self, message: PendingMessage):
        """Send a message via the transport layer and notify AckSystem."""
        try:
            message.last_attempt_at = time.time()
            if message.retry_count == 0 : message.retry_count = 1 # First attempt is attempt 1
            else: message.retry_count +=1

            logger.info(f"TRANSPORT: Attempting send for message {message.message_id} to ZMQ {message.target_node} "
                       f"(attempt {message.retry_count}/{message.max_retries})")

            if not self.transport_send_callback:
                raise Exception("Transport send callback not configured")

            await self.transport_send_callback(message.target_node, message.message_data)

            await self._update_message_status(message.message_id, MessageStatus.TRANSPORT_CONFIRMED)
            logger.info(f"TRANSPORT: Message {message.message_id} sent via ZMQ transport (RM status: TRANSPORT_CONFIRMED)")

            if self.ack_system_callback:
                self.ack_system_callback.confirm_transport_sent(message.message_id, True)

        except Exception as e:
            logger.error(f"TRANSPORT: Failed to send message {message.message_id} to ZMQ {message.target_node}: {e}", exc_info=True)
            await self._update_message_status(message.message_id, MessageStatus.FAILED)
            if self.ack_system_callback:
                self.ack_system_callback.confirm_transport_sent(message.message_id, False)
            raise 

    async def handle_delivery_ack(self, message_id: str, success: bool):
        logger.info(f"RELIABILITY_MGR: Processing DELIVERY ACK for {message_id}, success={success}")
        if success:
            await self._update_message_status(message_id, MessageStatus.DELIVERED)
        else:
            await self._update_message_status(message_id, MessageStatus.FAILED)
            if message_id in self._ack_waiters:
                logger.warning(f"RELIABILITY_MGR: Negative delivery ACK for {message_id}, signaling send_reliable to fail.")
                self._ack_waiters[message_id].set() 

    async def handle_processing_ack(self, message_id: str, success: bool):
        logger.info(f"RELIABILITY_MGR: Processing PROCESSING ACK for {message_id}, success={success}")
        if success:
            await self._update_message_status(message_id, MessageStatus.PROCESSED)
        else:
            await self._update_message_status(message_id, MessageStatus.FAILED)

        if message_id in self._ack_waiters:
            self._ack_waiters[message_id].set()
            logger.debug(f"RELIABILITY_MGR: Signaled completion/failure for message {message_id} to send_reliable.")

    async def _update_message_status(self, message_id: str, status: MessageStatus):
        """Update the status of a pending message with thread-safe fallback."""
        try:
            # Try async lock first (main event loop context)
            async with self._lock:
                if message_id in self._pending_messages:
                    old_status = self._pending_messages[message_id].status
                    if old_status == MessageStatus.PROCESSED and status != MessageStatus.PROCESSED:
                        logger.warning(f"REGISTRY: Attempt to change status of already PROCESSED message {message_id} from {old_status.name} to {status.name}. Ignoring.")
                        return
                    if old_status == MessageStatus.EXPIRED and status != MessageStatus.EXPIRED:
                        logger.warning(f"REGISTRY: Attempt to change status of already EXPIRED message {message_id} from {old_status.name} to {status.name}. Ignoring.")
                        return
                    self._pending_messages[message_id].status = status
                    target_node = self._pending_messages[message_id].target_node
                    logger.info(f"REGISTRY: Message {message_id} to ZMQ {target_node} status: {old_status.name} -> {status.name}")
        except RuntimeError as e:
            if "different event loop" in str(e) or "bound to a different event loop" in str(e):
                # Fallback to thread-safe lock for timeout callbacks
                logger.debug(f"REGISTRY: Using thread-safe fallback for message {message_id} status update")
                self._update_message_status_thread_safe(message_id, status)
            else:
                raise

    def _update_message_status_thread_safe(self, message_id: str, status: MessageStatus):
        """Thread-safe version for timeout callbacks from different event loops."""
        with self._thread_safe_lock:
            if message_id in self._pending_messages:
                old_status = self._pending_messages[message_id].status
                if old_status == MessageStatus.PROCESSED and status != MessageStatus.PROCESSED:
                    logger.warning(f"REGISTRY: Attempt to change status of already PROCESSED message {message_id} from {old_status.name} to {status.name}. Ignoring. (thread-safe)")
                    return
                if old_status == MessageStatus.EXPIRED and status != MessageStatus.EXPIRED:
                    logger.warning(f"REGISTRY: Attempt to change status of already EXPIRED message {message_id} from {old_status.name} to {status.name}. Ignoring. (thread-safe)")
                    return
                self._pending_messages[message_id].status = status
                target_node = self._pending_messages[message_id].target_node
                logger.info(f"REGISTRY: Message {message_id} to ZMQ {target_node} status: {old_status.name} -> {status.name} (thread-safe)")
            
            # Clean up ACK waiter if present
            if message_id in self._ack_waiters:
                try:
                    self._ack_waiters[message_id].set()
                except Exception as e:
                    logger.debug(f"REGISTRY: Error setting ACK waiter event: {e}")

    async def _retry_loop(self):
        logger.info("RETRY_LOGIC: Started retry background task")

        while self._running:
            try:
                await asyncio.sleep(1.0)

                messages_to_retry_snapshot: List[PendingMessage] = []
                async with self._lock:
                    for message_id in list(self._pending_messages.keys()):
                        message = self._pending_messages.get(message_id)
                        if message and message.should_retry():
                            retry_delay = message.calculate_retry_delay()
                            time_since_attempt = time.time() - message.last_attempt_at

                            if time_since_attempt >= retry_delay:
                                messages_to_retry_snapshot.append(message)

                for message in messages_to_retry_snapshot:
                    async with self._lock: 
                        current_message_state = self._pending_messages.get(message.message_id)
                        if not current_message_state or not current_message_state.should_retry():
                            continue 

                        if self.swim_membership_callback and not self.swim_membership_callback(message.target_node):
                            logger.warning(f"RETRY_LOGIC: Skipping retry for {message.message_id} to ZMQ {message.target_node} - target not alive per SWIM.")
                            await self._update_message_status(message.message_id, MessageStatus.FAILED)
                            if message.message_id in self._ack_waiters: self._ack_waiters[message.message_id].set()
                            continue

                        if self.circuit_breaker_callback and not self.circuit_breaker_callback(message.target_node):
                            logger.warning(f"RETRY_LOGIC: Skipping retry for {message.message_id} to ZMQ {message.target_node} - circuit open.")
                            await self._update_message_status(message.message_id, MessageStatus.FAILED)
                            if message.message_id in self._ack_waiters: self._ack_waiters[message.message_id].set()
                            continue

                    retry_delay_val = message.calculate_retry_delay() 
                    logger.info(f"RETRY_LOGIC: Retrying message {message.message_id} to ZMQ {message.target_node} "
                               f"(next attempt: {message.retry_count + 1}/{message.max_retries}) " 
                               f"after {retry_delay_val:.2f}s backoff. Current status: {message.status.name}")

                    try:
                        await self._send_message(message) 
                    except Exception as e:
                        logger.error(f"RETRY_LOGIC: Retry attempt failed for message {message.message_id}: {e}")
                        async with self._lock: 
                            final_check_message = self._pending_messages.get(message.message_id)
                            if final_check_message and not final_check_message.should_retry():
                                logger.warning(f"RETRY_LOGIC: Exhausted retries or message expired for {message.message_id}, marking as FAILED.")
                                await self._update_message_status(message.message_id, MessageStatus.FAILED)
                                if message.message_id in self._ack_waiters: self._ack_waiters[message.message_id].set()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"RETRY_LOGIC: Error in retry loop: {e}", exc_info=True)

        logger.info("RETRY_LOGIC: Stopped retry background task")

    async def _cleanup_loop(self):
        logger.info(f"TIMEOUT_POLICY: Started cleanup background task, interval={self.cleanup_interval}s")

        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_messages()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"TIMEOUT_POLICY: Error in cleanup loop: {e}", exc_info=True)

        logger.info("TIMEOUT_POLICY: Stopped cleanup background task")

    async def _cleanup_expired_messages(self):
        expired_message_ids: List[Tuple[str, str, float]] = []

        async with self._lock:
            for msg_id, message in list(self._pending_messages.items()): 
                if message.is_expired(self.default_timeout): 
                    expired_message_ids.append((msg_id, message.target_node, time.time() - message.created_at))

        for msg_id, target_node, age in expired_message_ids:
            logger.warning(f"TIMEOUT_POLICY: Expiring message {msg_id} to ZMQ {target_node} "
                          f"after {age:.1f}s (RM timeout={self.default_timeout}s)")
            await self._update_message_status(msg_id, MessageStatus.EXPIRED)

            if msg_id in self._ack_waiters:
                self._ack_waiters[msg_id].set() 

            if self.ack_system_callback and msg_id in self.ack_system_callback._pending_acks:
                logger.info(f"TIMEOUT_POLICY: Notifying AckSystem & cleaning its tracking for expired message {msg_id}")
                await self.ack_system_callback._notify_reliability_manager(msg_id, AckType.PROCESSING, False)
                self.ack_system_callback._cleanup_message_tracking(msg_id)

            async with self._lock: 
                self._pending_messages.pop(msg_id, None)
                self._ack_waiters.pop(msg_id, None)

        if expired_message_ids:
            async with self._lock: 
                current_pending_count = len(self._pending_messages)
            logger.info(f"REGISTRY: Cleaned up {len(expired_message_ids)} expired messages from ReliabilityManager, "
                       f"pending count: {current_pending_count}")

    def get_statistics(self) -> Dict[str, Any]:
        pending_count = len(self._pending_messages)
        stats = {
            "pending_messages_rm": pending_count,
            "running": self._running,
            "node_id": self.node_id,
            "max_pending_rm": self.max_pending_messages,
            "default_timeout_rm": self.default_timeout
        }
        logger.debug(f"REGISTRY: ReliabilityManager statistics - pending: {stats['pending_messages_rm']}, "
                    f"max: {stats['max_pending_rm']}, running: {stats['running']}")
        return stats