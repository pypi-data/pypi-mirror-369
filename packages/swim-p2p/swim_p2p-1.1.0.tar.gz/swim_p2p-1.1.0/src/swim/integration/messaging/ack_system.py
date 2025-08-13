"""
Three-tier acknowledgment system for reliable ZMQ messaging.

Implements Transport ACK, Delivery ACK, and Processing ACK to ensure
end-to-end message delivery confirmation with the reliability manager.
"""

import asyncio
import time
import json
import logging
from typing import Dict, Optional, Callable, Any, Awaitable
from dataclasses import dataclass
from enum import Enum, auto


logger = logging.getLogger(__name__)


class AckType(Enum):
    """Types of acknowledgments in the three-tier system."""
    TRANSPORT = "transport"     # Message left sender ZMQ buffer
    DELIVERY = "delivery"       # Message arrived at receiver and queued
    PROCESSING = "processing"   # Message processed by application


@dataclass
class AckMessage:
    """Standardized ACK message format."""
    message_id: str
    ack_type: AckType
    success: bool
    timestamp: float
    node_id: str # ID of the node SENDING this ACK
    error_details: Optional[str] = None
    
    def to_bytes(self) -> bytes:
        """Serialize ACK message for transmission."""
        data = {
            "type": "ACK", # This is the outer message type for routing
            "message_id": self.message_id, # ID of the message being ACKed
            "ack_type": self.ack_type.value, # 'transport', 'delivery', or 'processing'
            "success": self.success,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
            "error_details": self.error_details
        }
        return json.dumps(data).encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'AckMessage':
        """Deserialize ACK message from transmission."""
        parsed = json.loads(data.decode('utf-8'))
        if parsed.get("type") != "ACK":
            raise ValueError(f"Message is not of type ACK: {parsed.get('type')}")
        return cls(
            message_id=parsed["message_id"],
            ack_type=AckType(parsed["ack_type"]),
            success=parsed["success"],
            timestamp=parsed["timestamp"],
            node_id=parsed["node_id"],
            error_details=parsed.get("error_details")
        )


class AckSystem:
    """
    Three-tier acknowledgment system coordinator.
    
    Manages the complete ACK lifecycle from transport confirmation
    through delivery and processing acknowledgments.
    """
    
    def __init__(self, node_id: str): # node_id is this AckSystem's owner node ID
        """
        Initialize the ACK system.
        
        Args:
            node_id: This node's identifier
        """
        self.node_id = node_id
        self._pending_acks: Dict[str, Dict[AckType, bool]] = {}
        self._ack_timeouts: Dict[str, float] = {} # Tracks when a message was registered for ACK tracking
        self._reliability_manager_notify_callback: Optional[Callable[[str, str, bool], Awaitable[None]]] = None # For notifying RM
        self._transport_send_ack_callback: Optional[Callable[[str, bytes], Awaitable[bool]]] = None # For sending ACKs
        
        # Configuration
        self.transport_ack_timeout = 5.0    # How long RM waits for AckSystem to confirm transport
        self.delivery_ack_timeout = 10.0    # How long RM waits for delivery ACK after transport confirmed
        self.processing_ack_timeout = 30.0  # How long RM waits for processing ACK after delivery confirmed
        
        self._running = False
        self._timeout_task: Optional[asyncio.Task] = None
        self.cleanup_interval = 30.0
        
        logger.info(f"ACK_SYSTEM: Initialized for node {node_id}")
        logger.info(f"ACK_TIMEOUTS: Transport={self.transport_ack_timeout}s, "
                   f"Delivery={self.delivery_ack_timeout}s, Processing={self.processing_ack_timeout}s")
    
    async def start(self):
        """Starts the background task for checking ACK timeouts."""
        if self._running:
            return
        self._running = True
        self._timeout_task = asyncio.create_task(self._ack_timeout_loop())
        logger.info(f"ACK_SYSTEM ({self.node_id}): Started background ACK timeout checker.")

    async def stop(self):
        """Stops the background ACK timeout checker task."""
        if not self._running:
            return
        self._running = False
        if self._timeout_task:
            if not self._timeout_task.done():
                self._timeout_task.cancel()
            try:
                await self._timeout_task
            except asyncio.CancelledError:
                pass # Expected
            self._timeout_task = None
        logger.info(f"ACK_SYSTEM ({self.node_id}): Stopped background ACK timeout checker.")

    async def _ack_timeout_loop(self):
        """Background loop to periodically check for ACK timeouts."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.check_ack_timeouts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"ACK_SYSTEM ({self.node_id}): Error in ACK timeout loop: {e}", exc_info=True)

    def set_reliability_callback(self, callback: Callable[[str, str, bool], Awaitable[None]]): # Callback to ReliabilityManager
        """Set callback to notify reliability manager of ACK events."""
        self._reliability_manager_notify_callback = callback
        logger.info("ACK_SYSTEM: Reliability manager notify callback configured")
    
    def set_transport_callback(self, callback: Callable[[str, bytes], Awaitable[bool]]): # Callback to send ACKs via Router
        """Set callback for sending ACK messages via transport."""
        self._transport_send_ack_callback = callback
        logger.info("ACK_SYSTEM: Transport send ACK callback configured")
    
    def register_outgoing_message(self, message_id: str):
        """Register a new outgoing message for ACK tracking by this AckSystem instance."""
        if message_id in self._pending_acks:
            logger.warning(f"ACK_SYSTEM: Message {message_id} already registered for ACK tracking. Overwriting.")
        self._pending_acks[message_id] = {
            AckType.TRANSPORT: False,
            AckType.DELIVERY: False,
            AckType.PROCESSING: False
        }
        self._ack_timeouts[message_id] = time.time() # Record when we started tracking this message
        
        logger.info(f"ACK_SYSTEM: Registered message {message_id} for three-tier ACK tracking")
    
    def confirm_transport_sent(self, message_id: str, success: bool):
        """
        Confirm that ZMQ transport has sent the message (called by ReliabilityManager).
        
        This is the first ACK stage *from the perspective of this AckSystem*.
        """
        if message_id not in self._pending_acks:
            logger.warning(f"ACK_SYSTEM: Unknown message {message_id} for transport confirmation. Was it registered?")
            return # Or register it here if desired, but RM should register first
        
        self._pending_acks[message_id][AckType.TRANSPORT] = success
        
        if success:
            logger.info(f"TRANSPORT_ACK: Message {message_id} confirmed sent via ZMQ transport (AckSystem notified)")
        else:
            logger.error(f"TRANSPORT_ACK: Message {message_id} failed to send via ZMQ transport (AckSystem notified)")
            # If transport fails, the message effectively fails entirely from ACK perspective.
            # Notify RM that processing ultimately failed.
            asyncio.create_task(self._notify_reliability_manager(message_id, AckType.PROCESSING, False)) # Cascade failure to final ACK
            self._cleanup_message_tracking(message_id) # No further ACKs expected
    
    async def handle_incoming_ack(self, message: Dict[str, Any], sender_node_zmq_id: str):
        """
        Handle incoming ACK message from a peer (called by RouterManager).
        
        Args:
            message: Deserialized ACK message dictionary
            sender_node_zmq_id: ZMQ identity of the node that sent the ACK
        """
        try:
            
            message_id = message.get('ack_for')  
            ack_type_str = message.get('ack_type')
            success = message.get('success', True)
            node_id = message.get('node_id', 'unknown')
            error_details = message.get('error_details')
            
            if not message_id or not ack_type_str:
                logger.error(f"ACK_SYSTEM: Invalid ACK message format from {sender_node_zmq_id}: missing ack_for or ack_type")
                return
                
            try:
                ack_type = AckType(ack_type_str)
            except ValueError:
                logger.error(f"ACK_SYSTEM: Invalid ack_type '{ack_type_str}' in ACK from {sender_node_zmq_id}")
                return
            
            logger.info(f"{ack_type.name}_ACK: Received {ack_type.name} ACK "
                    f"for message '{message_id}' from ZMQ ID '{sender_node_zmq_id}' (originated from SWIM ID '{node_id}'), success={success}")
            
            if message_id not in self._pending_acks:
                logger.warning(f"{ack_type.name}_ACK: Unknown message ID '{message_id}' in ACK tracking. Ignoring ACK from {sender_node_zmq_id}.")
                return
            
            # Update ACK status for the specific type
            if ack_type == AckType.DELIVERY:
                self._pending_acks[message_id][AckType.DELIVERY] = success
            elif ack_type == AckType.PROCESSING:
                self._pending_acks[message_id][AckType.PROCESSING] = success
            else:
                logger.warning(f"ACK_SYSTEM: Received ACK with unexpected ack_type '{ack_type.name}' for {message_id}")
                return

            if not success and error_details:
                logger.error(f"{ack_type.name}_ACK: Negative ACK for message '{message_id}', error: {error_details}")
            
            # Notify reliability manager about this specific ACK type
            await self._notify_reliability_manager(message_id, ack_type, success)
            
            # If this was the final processing ACK (successful or not), clean up.
            if ack_type == AckType.PROCESSING:
                self._cleanup_message_tracking(message_id)
        
        except Exception as e:
            logger.error(f"ACK_SYSTEM: Error handling incoming ACK from {sender_node_zmq_id}: {e}", exc_info=True)
    
    # Methods for THIS node (acting as a receiver) to SEND ACKs back
    # These are called by RouterManager after it receives an application message.
    
    async def send_ack_from_receiver(self, acked_message_id: str, target_sender_zmq_id: str, ack_to_send: AckType, success: bool, 
                               error_details: Optional[str] = None):
        """
        Helper for a receiver to send an ACK message (Delivery or Processing) back to the original sender.
        
        Args:
            acked_message_id: ID of the message being acknowledged.
            target_sender_zmq_id: The ZMQ identity of the original sender (to send the ACK to).
            ack_to_send: The type of ACK to send (DELIVERY or PROCESSING).
            success: Whether the operation being ACKed was successful.
            error_details: Optional error information if not successful.
        """
        if ack_to_send == AckType.TRANSPORT:
            logger.error("ACK_SYSTEM: send_ack_from_receiver should not be called for TRANSPORT ACKs. These are local confirmations.")
            return

        ack = AckMessage(
            message_id=acked_message_id,
            ack_type=ack_to_send,
            success=success,
            timestamp=time.time(),
            node_id=self.node_id, # This node (the receiver of original message) is sending the ACK
            error_details=error_details
        )
        
        await self._send_ack_payload(ack, target_sender_zmq_id)
        
        status_str = "SUCCESS" if success else f"FAILURE ({error_details or 'No details'})"
        logger.info(f"ACK_SYSTEM: Sent {ack_to_send.name} ACK ({status_str}) for message '{acked_message_id}' to ZMQ ID '{target_sender_zmq_id}'")

    async def _send_ack_payload(self, ack_message_obj: AckMessage, target_sender_zmq_id: str):
        """Internal helper to send a constructed AckMessage object."""
        if not self._transport_send_ack_callback:
            logger.error(f"ACK_SYSTEM: No transport_send_ack_callback configured. Cannot send {ack_message_obj.ack_type.name} ACK for {ack_message_obj.message_id}.")
            return
        
        try:
            ack_bytes = ack_message_obj.to_bytes() # This creates the {"type": "ACK", ...} payload
            # The _transport_send_ack_callback is self.router_manager.send_to_node,
            # which expects the ZMQ identity of the target DEALER.
            sent_ok = await self._transport_send_ack_callback(target_sender_zmq_id, ack_bytes)
            if sent_ok:
                logger.debug(f"ACK_SYSTEM: Successfully dispatched {ack_message_obj.ack_type.name} ACK for message {ack_message_obj.message_id} to ZMQ ID {target_sender_zmq_id}")
            else:
                logger.error(f"ACK_SYSTEM: Transport send ACK callback returned False for {ack_message_obj.ack_type.name} ACK to ZMQ ID {target_sender_zmq_id}")

        except Exception as e:
            logger.error(f"ACK_SYSTEM: Failed to send {ack_message_obj.ack_type.name} ACK to ZMQ ID {target_sender_zmq_id}: {e}", exc_info=True)
    
    async def _notify_reliability_manager(self, message_id: str, ack_type: AckType, success: bool):
        """Notify reliability manager of ACK status change."""
        if not self._reliability_manager_notify_callback:
            logger.warning(f"ACK_SYSTEM: No reliability manager notify callback configured (for msg {message_id}, ack {ack_type.name})")
            return
        
        try:
            # MODIFIED: Ensure the callback is awaited
            await self._reliability_manager_notify_callback(message_id, ack_type.value, success)
            logger.debug(f"ACK_BRIDGE: Notified ReliabilityManager of {ack_type.name} ACK "
                        f"for message '{message_id}', success={success}")
        except Exception as e:
            logger.error(f"ACK_BRIDGE: Error notifying ReliabilityManager for msg '{message_id}', ack {ack_type.name}: {e}", exc_info=True)
    
    def _cleanup_message_tracking(self, message_id: str):
        """Remove message from ACK tracking."""
        removed_ack = self._pending_acks.pop(message_id, None)
        removed_timeout = self._ack_timeouts.pop(message_id, None)
        if removed_ack or removed_timeout:
            logger.debug(f"ACK_SYSTEM: Cleaned up ACK tracking for message {message_id}")
    
    async def check_ack_timeouts(self) -> list:
        """
        Check for ACK timeouts based on when the message was registered with AckSystem.
        This is about this AckSystem instance *waiting for ACKs from peers*.
        
        Returns:
            List of (message_id, ack_type_expected_but_timed_out) tuples.
        """
        current_time = time.time()
        timed_out_messages_for_rm = []
        
        # Iterate over a copy of keys if modification within loop is possible
        for message_id, registration_time in list(self._ack_timeouts.items()):
            if message_id not in self._pending_acks:
                continue
            
            acks_status = self._pending_acks[message_id]
            
            # Stage 2: Waiting for Delivery ACK
            if acks_status.get(AckType.TRANSPORT) and not acks_status.get(AckType.DELIVERY):
                if (current_time - registration_time) > self.delivery_ack_timeout:
                    logger.warning(f"ACK_SYSTEM_TIMEOUT: Delivery ACK timeout for message {message_id} ...")
                    timed_out_messages_for_rm.append((message_id, AckType.DELIVERY))
                    await self._notify_reliability_manager(message_id, AckType.DELIVERY, False)
                    self._cleanup_message_tracking(message_id)
                    continue

            # Stage 3: Waiting for Processing ACK
            if acks_status.get(AckType.DELIVERY) and not acks_status.get(AckType.PROCESSING):
                if (current_time - registration_time) > self.processing_ack_timeout:
                    logger.warning(f"ACK_SYSTEM_TIMEOUT: Processing ACK timeout for message {message_id} ...")
                    timed_out_messages_for_rm.append((message_id, AckType.PROCESSING))
                    await self._notify_reliability_manager(message_id, AckType.PROCESSING, False)
                    self._cleanup_message_tracking(message_id)
                    continue
        
        return timed_out_messages_for_rm
    
    def get_ack_status(self, message_id: str) -> Optional[Dict[str, bool]]:
        """Get current ACK status for a message this AckSystem is tracking."""
        if message_id not in self._pending_acks:
            return None
        
        return {ack_type.name: status for ack_type, status in self._pending_acks[message_id].items()}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ACK system statistics."""
        return {
            "node_id": self.node_id,
            "running": self._running,
            "pending_acks": len(self._pending_acks),
            "tracked_messages": list(self._pending_acks.keys()),
            "configuration": {
                "transport_timeout": self.transport_ack_timeout,
                "delivery_timeout": self.delivery_ack_timeout,
                "processing_timeout": self.processing_ack_timeout,
                "cleanup_interval": self.cleanup_interval
            }
        }