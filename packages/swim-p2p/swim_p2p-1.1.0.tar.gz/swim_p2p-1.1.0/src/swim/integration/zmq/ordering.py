"""
Message ordering and reassembly for ZMQ messages within workflows.

Provides a reordering buffer to handle out-of-order messages based on
sequence numbers, typically within a specific workflow context.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Deque
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class BufferedMessage:
    """Represents a message stored in the reordering buffer."""
    message_id: str
    sequence_number: int
    payload: Dict[str, Any]
    received_at: float = field(default_factory=time.time)
    trace_context: Optional[Any] = None # Placeholder for messaging.trace.TraceContext

class ReorderingBuffer:
    """
    A buffer that reorders messages based on sequence numbers for a given context (e.g., workflow_id).
    """
    def __init__(self,
                 context_timeout_seconds: float = 300.0, # How long to keep a context alive without activity
                 message_ttl_seconds: float = 60.0,      # How long an individual message can wait
                 on_ready_callback: Optional[callable] = None): # Async callable(context_id, List[BufferedMessage])
        """
        Initialize the reordering buffer.

        Args:
            context_timeout_seconds: Time after which an inactive context is cleared.
            message_ttl_seconds: Time after which a message is dropped if its sequence is still gapped.
            on_ready_callback: Async callback to invoke when messages for a context are ready.
        """
        self._buffers: Dict[str, Deque[BufferedMessage]] = defaultdict(deque)
        self._next_expected_sequence: Dict[str, int] = defaultdict(lambda: 0) # Start with sequence 0
        self._last_activity: Dict[str, float] = defaultdict(time.time)
        self._context_timeout_seconds = context_timeout_seconds
        self._message_ttl_seconds = message_ttl_seconds
        self._on_ready_callback = on_ready_callback
        self._lock = asyncio.Lock()

        logger.info(f"REORDER_BUFFER: Initialized. Context timeout: {context_timeout_seconds}s, Message TTL: {message_ttl_seconds}s")

    async def add_message(self,
                          context_id: str,
                          message_id: str,
                          sequence_number: int,
                          payload: Dict[str, Any],
                          trace_context: Optional[Any] = None) -> None:
        """
        Adds a message to the reordering buffer for a specific context.

        Args:
            context_id: The identifier for the context (e.g., workflow_id).
            message_id: The unique ID of the message.
            sequence_number: The sequence number of the message within the context.
            payload: The message payload.
            trace_context: Optional distributed tracing context.
        """
        async with self._lock:
            buffered_msg = BufferedMessage(
                message_id=message_id,
                sequence_number=sequence_number,
                payload=payload,
                trace_context=trace_context
            )
            self._last_activity[context_id] = time.time()

            # Check for duplicate sequence numbers
            for msg_in_buffer in self._buffers[context_id]:
                if msg_in_buffer.sequence_number == sequence_number:
                    logger.warning(f"REORDER_BUFFER_DUPLICATE: Context {context_id}, Seq {sequence_number}, MsgID {message_id} (existing {msg_in_buffer.message_id}). Ignoring new.")
                    return


            # Insert in sorted order or append and sort
            # A simple append and sort is easier to manage than bisect for deque
            self._buffers[context_id].append(buffered_msg)
            # Sort the deque by sequence number
            self._buffers[context_id] = deque(sorted(self._buffers[context_id], key=lambda m: m.sequence_number))

            logger.info(f"REORDER_BUFFER_ADD: Added MsgID {message_id}, Context {context_id}, Seq {sequence_number}. Buffer size: {len(self._buffers[context_id])}")

            await self._process_context(context_id)

    async def _process_context(self, context_id: str) -> None:
        """Processes a context to release messages that are now in order."""
        ready_messages: List[BufferedMessage] = []
        current_buffer = self._buffers[context_id]
        next_expected = self._next_expected_sequence[context_id]

        while current_buffer:
            if current_buffer[0].sequence_number == next_expected:
                msg = current_buffer.popleft()
                ready_messages.append(msg)
                next_expected += 1
                self._last_activity[context_id] = time.time()
            elif current_buffer[0].sequence_number < next_expected:
                # This implies a past message, possibly due to retry or duplicate after sequence moved on
                # Or, sequence number reset if the system allows it. For now, assume duplicates or late.
                old_msg = current_buffer.popleft()
                logger.warning(f"REORDER_BUFFER_STALE: Context {context_id}, dropping stale/duplicate MsgID {old_msg.message_id} "
                               f"Seq {old_msg.sequence_number} (expected {next_expected-1}).")
            else:
                # Gap detected, next message is not the expected one
                logger.debug(f"REORDER_BUFFER_GAP: Context {context_id}, waiting for Seq {next_expected}. Next available is {current_buffer[0].sequence_number}.")
                break # Stop processing this context for now

        self._next_expected_sequence[context_id] = next_expected

        if ready_messages:
            logger.info(f"REORDER_BUFFER_READY: Context {context_id}, released {len(ready_messages)} messages. Next expected Seq: {next_expected}")
            if self._on_ready_callback:
                try:
                    # Ensure callback is awaitable if it's a coroutine function
                    if asyncio.iscoroutinefunction(self._on_ready_callback):
                        await self._on_ready_callback(context_id, ready_messages)
                    else:
                        self._on_ready_callback(context_id, ready_messages)
                except Exception as e:
                    logger.error(f"REORDER_BUFFER_CALLBACK_ERROR: Context {context_id}, error in on_ready_callback: {e}")
            # Else, user needs to call get_ready_messages manually if no callback


    async def get_ready_messages(self, context_id: str) -> List[BufferedMessage]:
        """
        Retrieves messages from the specified context that are now in sequence.
        This is an alternative to using the on_ready_callback.
        """
        async with self._lock:
            # This logic is essentially what _process_context does, but returns the list
            ready_messages: List[BufferedMessage] = []
            current_buffer = self._buffers[context_id]
            next_expected = self._next_expected_sequence[context_id]

            while current_buffer:
                if current_buffer[0].sequence_number == next_expected:
                    msg = current_buffer.popleft()
                    ready_messages.append(msg)
                    next_expected += 1
                    self._last_activity[context_id] = time.time()
                elif current_buffer[0].sequence_number < next_expected:
                    old_msg = current_buffer.popleft()
                    logger.warning(f"REORDER_BUFFER_GET_STALE: Context {context_id}, dropping stale/duplicate MsgID {old_msg.message_id} "
                                   f"Seq {old_msg.sequence_number} (expected {next_expected-1}).")
                else:
                    break # Gap

            self._next_expected_sequence[context_id] = next_expected
            if ready_messages:
                 logger.info(f"REORDER_BUFFER_GET_READY: Context {context_id}, retrieved {len(ready_messages)} messages. Next expected Seq: {next_expected}")
            return ready_messages


    async def cleanup_expired(self) -> None:
        """
        Periodically cleans up expired contexts and messages.
        Should be called by a background task.
        """
        async with self._lock:
            now = time.time()
            expired_contexts = [
                ctx_id for ctx_id, last_act_time in self._last_activity.items()
                if now - last_act_time > self._context_timeout_seconds
            ]

            for ctx_id in expired_contexts:
                if ctx_id in self._buffers:
                    dropped_count = len(self._buffers[ctx_id])
                    del self._buffers[ctx_id]
                    logger.warning(f"REORDER_BUFFER_CTX_TIMEOUT: Context {ctx_id} timed out. Dropped {dropped_count} buffered messages.")
                if ctx_id in self._next_expected_sequence:
                    del self._next_expected_sequence[ctx_id]
                if ctx_id in self._last_activity:
                    del self._last_activity[ctx_id]

            # Cleanup individual expired messages within active contexts
            for ctx_id, buffer in self._buffers.items():
                original_len = len(buffer)
                # Iterate carefully as we might modify the deque
                new_buffer = deque()
                dropped_this_context = 0
                for msg in list(buffer): # Iterate over a copy
                    if now - msg.received_at > self._message_ttl_seconds:
                        logger.warning(f"REORDER_BUFFER_MSG_TTL: Context {ctx_id}, MsgID {msg.message_id}, Seq {msg.sequence_number} timed out (TTL: {self._message_ttl_seconds}s). Dropping.")
                        # Potentially, we might want to advance next_expected here if this was the blocking message
                        # For simplicity now, just drop. A more advanced system might handle this by forcing the sequence.
                        dropped_this_context +=1
                    else:
                        new_buffer.append(msg)
                if dropped_this_context > 0:
                    self._buffers[ctx_id] = new_buffer
                    logger.info(f"REORDER_BUFFER_MSG_TTL_CLEANUP: Context {ctx_id}, dropped {dropped_this_context} messages due to TTL. New buffer size: {len(new_buffer)}")


    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the reordering buffer."""
        status = {
            "total_contexts": len(self._buffers),
            "total_buffered_messages": sum(len(q) for q in self._buffers.values()),
            "contexts": {}
        }
        for ctx_id, buffer in self._buffers.items():
            status["contexts"][ctx_id] = {
                "buffered_count": len(buffer),
                "next_expected_sequence": self._next_expected_sequence.get(ctx_id, 0),
                "last_activity": self._last_activity.get(ctx_id, 0),
                "oldest_message_age_seconds": (time.time() - buffer[0].received_at) if buffer else 0,
            }
        return status