"""
Enhanced ROUTER socket management with SWIM integration and port validation.
Handles identity management, message dispatching, and reliability coordination.
"""

import asyncio
import logging
import time
import zmq
import zmq.asyncio
from typing import Dict, Optional, Callable, Any, Set
from collections import defaultdict
import json 

logger = logging.getLogger(__name__)


class PortValidationError(Exception):
    """Raised when port validation fails."""
    pass


class RouterManager:
    """
    Enhanced ROUTER socket manager with SWIM integration, reliability features, and port validation.
    """

    def __init__(self, bind_address: str, context: Optional[zmq.asyncio.Context] = None):
        """
        Initialize enhanced ROUTER manager with validation.

        Args:
            bind_address: Address to bind to in format "host:port"
            context: Optional ZMQ context, creates new one if None
        """
        self.bind_address = bind_address
        self.node_id = bind_address 
        self.context = context or zmq.asyncio.Context()
        self.socket: Optional[zmq.asyncio.Socket] = None

        self._message_handlers: Dict[str, Callable] = {}
        self._default_handler: Optional[Callable] = None

        self.swim_membership_callback: Optional[Callable[[str], str]] = None
        self.reliability_manager_callback: Optional[Callable] = None 

        self._active_identities: Dict[bytes, str] = {}  
        self._identity_last_seen: Dict[bytes, float] = {}
        self._identity_swim_state: Dict[bytes, str] = {}  
        self._message_counts: Dict[bytes, int] = defaultdict(int)

        self._pending_acks: Dict[str, float] = {} 
        self._delivery_confirmations: Set[str] = set() 

        self.ack_timeout = 30.0
        self.stale_identity_timeout = 600.0 
        self.port_validation_timeout = 1.0

        self._running = False
        self._receive_task: Optional[asyncio.Task] = None
        self._health_task: Optional[asyncio.Task] = None

        logger.info(f"ROUTER: Initialized for bind address {bind_address}")

    def _validate_bind_address(self) -> None:
        try:
            if ':' not in self.bind_address:
                raise PortValidationError(f"Invalid bind address format: {self.bind_address} (expected host:port)")

            host, port_str = self.bind_address.split(':', 1)

            if not host:
                raise PortValidationError(f"Empty host in bind address: {self.bind_address}")

            try:
                port = int(port_str)
            except ValueError:
                raise PortValidationError(f"Invalid port number in bind address: {self.bind_address}")

            if port < 1 or port > 65535:
                raise PortValidationError(f"Port {port} out of valid range (1-65535)")

            from swim.utils.network import check_port_available

            if not check_port_available(host, port, timeout=self.port_validation_timeout):
                raise PortValidationError(f"Port {port} is not available on {host}")

            logger.debug(f"ROUTER: Port validation successful for {host}:{port}")

        except ImportError:
            logger.warning("ROUTER: Network utilities not available, skipping port availability check")
            try:
                host, port_str = self.bind_address.split(':', 1)
                port = int(port_str)
                if port < 1 or port > 65535:
                    raise PortValidationError(f"Port {port} out of valid range")
            except (ValueError, IndexError):
                raise PortValidationError(f"Invalid bind address format: {self.bind_address}")

    async def start(self):
        if self._running:
            logger.warning("ROUTER: Already running, ignoring start request")
            return

        try:
            logger.info(f"ROUTER: Validating bind address {self.bind_address}")
            self._validate_bind_address()

            self.socket = self.context.socket(zmq.ROUTER)

            self.socket.setsockopt(zmq.LINGER, 1000)
            self.socket.setsockopt(zmq.RCVHWM, 10000)
            self.socket.setsockopt(zmq.SNDHWM, 10000)
            self.socket.setsockopt(zmq.ROUTER_MANDATORY, 1)
            self.socket.setsockopt(zmq.IMMEDIATE, 1) 

            endpoint = f"tcp://{self.bind_address}"
            self.socket.bind(endpoint)

            self._running = True
            self._receive_task = asyncio.create_task(self._receive_loop())
            self._health_task = asyncio.create_task(self._health_check_loop())

            logger.info(f"ROUTER: Enhanced ROUTER listening on {self.bind_address}")
            try:
                bound_address = self.socket.getsockopt_string(zmq.LAST_ENDPOINT)
                logger.info(f"ROUTER: Socket successfully bound to {bound_address}")
            except Exception as e:
                logger.warning(f"ROUTER: Could not verify socket binding: {e}")
            logger.info(f"ROUTER: Configuration - ACK timeout={self.ack_timeout}s, "
                       f"stale timeout={self.stale_identity_timeout}s")

        except PortValidationError:
            raise
        except zmq.ZMQError as e:
            error_msg = str(e).lower()
            if "address already in use" in error_msg:
                raise PortValidationError(f"Port already in use: {self.bind_address}")
            elif "permission denied" in error_msg:
                raise PortValidationError(f"Permission denied for port: {self.bind_address}")
            else:
                raise PortValidationError(f"ZMQ error binding to {self.bind_address}: {e}")
        except Exception as e:
            logger.error(f"ROUTER: Failed to start enhanced ROUTER: {e}")
            await self.stop()
            raise PortValidationError(f"Failed to start ROUTER on {self.bind_address}: {e}")

    async def stop(self):
        if not self._running:
            logger.warning("ROUTER: Already stopped, ignoring stop request")
            return

        logger.info("ROUTER: Stopping enhanced ROUTER...")
        self._running = False

        tasks = [self._receive_task, self._health_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.warning(f"ROUTER: Error closing socket: {e}")
            finally:
                self.socket = None

        self._active_identities.clear()
        self._identity_last_seen.clear()
        self._identity_swim_state.clear()
        self._message_counts.clear()
        self._pending_acks.clear()
        self._delivery_confirmations.clear()

        logger.info("ROUTER: Enhanced ROUTER stopped")

    def set_swim_callback(self, callback: Callable[[str], str]):
        self.swim_membership_callback = callback
        logger.info("ROUTER: SWIM membership callback configured")

    def set_reliability_callback(self, callback: Callable): 
        self.reliability_manager_callback = callback
        logger.info("ROUTER: Reliability manager callback configured")

    async def _receive_loop(self):
        logger.info("ROUTER: Started enhanced receive loop")

        while self._running:
            try:
                if not self.socket: 
                    logger.warning("ROUTER: Socket is not initialized in receive loop.")
                    await asyncio.sleep(0.1)
                    continue

                parts = await self.socket.recv_multipart(zmq.NOBLOCK)

                if len(parts) < 3: 
                    logger.warning(f"ROUTER: Received malformed message (parts: {len(parts)}), expected at least 3. Parts: {parts}")
                    continue

                identity, empty_delimiter, message_data = parts[0], parts[1], parts[2]

                if not identity:
                    logger.warning("ROUTER: Received message with empty identity")
                    continue

                if empty_delimiter != b'':
                    logger.warning(f"ROUTER: Received message with non-empty delimiter from {identity.decode('utf-8', errors='ignore')}. Delimiter: {empty_delimiter!r}")

                if not message_data:
                    logger.warning(f"ROUTER: Received empty message data from {identity.decode('utf-8', errors='ignore')}")
                    continue

                sender_zmq_identity_str = identity.decode('utf-8', errors='ignore')

                await self._track_identity(identity, sender_zmq_identity_str)

                await self._process_reliable_message(sender_zmq_identity_str, message_data, raw_zmq_identity=identity)

            except zmq.Again:
                await asyncio.sleep(0.001)
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"ROUTER: Error in enhanced receive loop: {e}", exc_info=True)
                await asyncio.sleep(0.1) 

        logger.info("ROUTER: Stopped enhanced receive loop")

    async def _track_identity(self, raw_zmq_identity: bytes, sender_zmq_identity_str: str):
        current_time = time.time()

        is_new = raw_zmq_identity not in self._active_identities
        was_dead = False

        if not is_new:
            previous_state = self._identity_swim_state.get(raw_zmq_identity, "UNKNOWN")
            if previous_state == "DEAD":
                was_dead = True
                logger.info(f"RECOVERY: Node (ZMQ ID: {sender_zmq_identity_str}) reconnecting after being marked DEAD")

        if is_new:
            self._active_identities[raw_zmq_identity] = sender_zmq_identity_str
            self._identity_swim_state[raw_zmq_identity] = "UNKNOWN" 
            logger.info(f"ROUTER: New client connected: ZMQ ID {sender_zmq_identity_str}")
        elif was_dead:
            await self._handle_reconnection(raw_zmq_identity, sender_zmq_identity_str)
            return 

        self._identity_last_seen[raw_zmq_identity] = current_time
        self._message_counts[raw_zmq_identity] += 1

        await self._update_swim_state(raw_zmq_identity, sender_zmq_identity_str)

    async def _update_swim_state(self, raw_zmq_identity: bytes, sender_zmq_identity_str: str):
        if not self.swim_membership_callback:
            return

        try:
            # MODIFIED: Parse SWIM ID here before calling the callback
            swim_id_to_check = sender_zmq_identity_str 
            parts = sender_zmq_identity_str.split('-',2)
            if len(parts) >= 2 and parts[0] == 'dealer':
                swim_id_to_check = parts[1] # Use parsed SWIM ID if dealer format

            # The callback now expects the parsed SWIM ID
            swim_state = self.swim_membership_callback(swim_id_to_check)
            old_state = self._identity_swim_state.get(raw_zmq_identity, "UNKNOWN")

            if swim_state != old_state:
                self._identity_swim_state[raw_zmq_identity] = swim_state
                logger.info(f"ROUTER: Node (ZMQ ID: {sender_zmq_identity_str}, Parsed SWIM ID for check: {swim_id_to_check}) SWIM state change: {old_state} -> {swim_state}")

                if swim_state == "DEAD":
                    logger.warning(f"ROUTER: Node (ZMQ ID: {sender_zmq_identity_str}) is DEAD, connection may be stale")
                elif swim_state == "ALIVE" and old_state in ["SUSPECT", "DEAD", "UNKNOWN"]:
                    logger.info(f"ROUTER: Node (ZMQ ID: {sender_zmq_identity_str}) recovered/confirmed ALIVE state")

        except Exception as e:
            logger.error(f"ROUTER: Error updating SWIM state for ZMQ ID {sender_zmq_identity_str}: {e}", exc_info=True)


    async def _handle_reconnection(self, raw_zmq_identity: bytes, sender_zmq_identity_str: str):
        current_time = time.time()

        logger.info(f"RECOVERY: Processing reconnection for ZMQ ID {sender_zmq_identity_str}")

        self._active_identities[raw_zmq_identity] = sender_zmq_identity_str
        self._identity_last_seen[raw_zmq_identity] = current_time
        self._message_counts[raw_zmq_identity] = 0  
        self._identity_swim_state[raw_zmq_identity] = "ALIVE"  

        logger.info(f"RECOVERY: Reconnection processing complete for ZMQ ID {sender_zmq_identity_str}")


    async def _process_reliable_message(self, sender_zmq_identity_str: str, message_data: bytes, raw_zmq_identity: bytes):
        # This part should be outside the try block for the handler
        try:
            from swim.utils.serialization import deserialize_message 
            message = deserialize_message(message_data)
            message_id = message.get('id', 'unknown_msg_id')
        except Exception as e:
            logger.error(f"ROUTER: Failed to deserialize message from {sender_zmq_identity_str}. Error: {e}. Data: {message_data[:100]}")
            # Cannot proceed or send any ACK if we don't have a message_id
            return

        # Now, handle the logic
        try:
            message_type = message.get('type', 'unknown')
            requires_ack = message.get('require_ack', False)
            original_sender_swim_id = message.get('from_node', 'unknown_swim_sender') 

            logger.debug(f"ROUTER: Processing '{message_type}' from ZMQ ID '{sender_zmq_identity_str}' (SWIM sender: '{original_sender_swim_id}'), msg_id='{message_id}', requires_ack={requires_ack}")

            if message_type == 'ACK': 
                # ack_system needs to be available. Assuming it's part of reliability_manager
                if self.reliability_manager_callback and hasattr(self.reliability_manager_callback, 'ack_system'):
                    ack_system_instance = self.reliability_manager_callback.ack_system
                    await ack_system_instance.handle_incoming_ack(message, sender_zmq_identity_str)
                else:
                    logger.warning(f"ROUTER: Cannot handle ACK, AckSystem not available via reliability_manager_callback.")
                return

            # 1. Send Delivery ACK immediately
            if requires_ack:
                await self._send_ack(
                    ack_type_str="delivery",
                    target_zmq_identity=raw_zmq_identity, 
                    acked_message_id=message_id,
                    success=True
                )

            handler = self._message_handlers.get(message_type, self._default_handler)

            # 2. Call the handler and await completion
            if handler:
                try:
                    logger.info(f"ROUTER: Dispatching '{message_type}' from ZMQ ID '{sender_zmq_identity_str}' (SWIM sender: {original_sender_swim_id}) to handler")
                    await self._safe_call_handler(handler, sender_zmq_identity_str, message)
                    
                    # 3.A. If handler succeeds, send SUCCESS Processing ACK
                    logger.info(f"ROUTER: Successfully processed '{message_type}' from ZMQ ID '{sender_zmq_identity_str}'")
                    if requires_ack:
                        await self._send_ack(
                            ack_type_str="processing",
                            target_zmq_identity=raw_zmq_identity,
                            acked_message_id=message_id,
                            success=True
                        )
                except Exception as handler_error:
                    # 3.B. If handler fails, send FAILURE Processing ACK
                    logger.error(f"ROUTER: Handler error for '{message_type}' from ZMQ ID '{sender_zmq_identity_str}': {handler_error}", exc_info=True)
                    if requires_ack:
                        await self._send_ack(
                            ack_type_str="processing",
                            target_zmq_identity=raw_zmq_identity,
                            acked_message_id=message_id,
                            success=False,
                            error_details=str(handler_error)
                        )
            else: # No handler found
                logger.warning(f"ROUTER: No handler for message type: '{message_type}' from ZMQ ID '{sender_zmq_identity_str}'")
                if requires_ack:
                    await self._send_ack(
                        ack_type_str="processing", 
                        target_zmq_identity=raw_zmq_identity,
                        acked_message_id=message_id,
                        success=False,
                        error_details="No handler for message type"
                    )

        except Exception as e:
            logger.error(f"ROUTER: Critical error in _process_reliable_message for ZMQ ID '{sender_zmq_identity_str}': {e}", exc_info=True)
            # Attempt to send a failure ACK if we have the message_id
            if 'message_id' in locals() and 'requires_ack' in locals() and requires_ack:
                await self._send_ack(
                    ack_type_str="processing",
                    target_zmq_identity=raw_zmq_identity,
                    acked_message_id=message_id,
                    success=False,
                    error_details=f"General processing error: {str(e)}"
                )


    async def _send_ack(self, ack_type_str: str, target_zmq_identity: bytes, acked_message_id: str, success: bool = True, error_details: str = None):
        """
        Send ACK with graceful error handling for connection issues.
        
        FIXED: Handle client disconnections gracefully instead of raising exceptions.
        """
        target_zmq_id_str = self._active_identities.get(target_zmq_identity, "unknown")
        
        # FIXED: Check if identity is still valid before attempting to send
        if target_zmq_identity not in self._active_identities:
            logger.debug(f"ROUTER: Cannot send {ack_type_str} ACK to {target_zmq_id_str} - identity no longer active. "
                        f"Client may have disconnected gracefully.")
            return  # Don't treat this as an error - this is normal behavior
        
        ack_payload = {
            "type": "ACK",
            "ack_type": ack_type_str,
            "ack_for": acked_message_id,
            "success": success,
            "node_id": self.node_id,
            "timestamp": time.time()
        }
        
        if error_details:
            ack_payload["error_details"] = error_details
        
        try:
            await self._send_ack_message_payload(target_zmq_identity, ack_payload)
            logger.debug(f"ROUTER: Sent {ack_type_str} ACK (success={success}) for '{acked_message_id}' to ZMQ ID '{target_zmq_id_str}'")
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # FIXED: Handle common connection issues gracefully
            if any(keyword in error_msg for keyword in ["host unreachable", "ehostunreach", "connection refused", "broken pipe", "network unreachable"]):
                logger.debug(f"ROUTER: Client {target_zmq_id_str} disconnected before {ack_type_str} ACK could be sent. "
                            f"Cleaning up stale identity. This is normal behavior during connection cycling.")
                
                # Clean up stale identity to prevent future send attempts
                self._active_identities.pop(target_zmq_identity, None)
                self._identity_last_seen.pop(target_zmq_identity, None)
                self._identity_swim_state.pop(target_zmq_identity, None)
                
                # Don't propagate exception - this is expected when clients disconnect
                return
                
            elif any(keyword in error_msg for keyword in ["again", "eagain", "resource temporarily unavailable", "send buffer full"]):
                logger.warning(f"ROUTER: Send buffer full when sending {ack_type_str} ACK to {target_zmq_id_str}. "
                              f"This may indicate high message volume or network congestion.")
                
                # Mark the identity as potentially degraded but don't remove it yet
                if target_zmq_identity in self._identity_swim_state:
                    current_state = self._identity_swim_state[target_zmq_identity]
                    if current_state == "ALIVE":
                        self._identity_swim_state[target_zmq_identity] = "DEGRADED"
                        logger.debug(f"ROUTER: Marked {target_zmq_id_str} as DEGRADED due to send buffer issues")
                
                # Don't propagate - buffer issues are usually temporary
                return
                
            elif "timeout" in error_msg or "timed out" in error_msg:
                logger.warning(f"ROUTER: Timeout sending {ack_type_str} ACK to {target_zmq_id_str}. "
                              f"Client may be slow or disconnecting.")
                
                # Mark as suspect but don't remove immediately
                if target_zmq_identity in self._identity_swim_state:
                    self._identity_swim_state[target_zmq_identity] = "SUSPECT"
                
                return
                
            else:
                # Unexpected errors should still be logged but not crash the system
                logger.error(f"ROUTER: Unexpected error sending {ack_type_str} ACK to {target_zmq_id_str}: {e}")
                
                # Still clean up the identity to prevent repeated failures
                self._active_identities.pop(target_zmq_identity, None)
                self._identity_last_seen.pop(target_zmq_identity, None)
                self._identity_swim_state.pop(target_zmq_identity, None)
                
                # Don't propagate to avoid crashing the router
                logger.warning(f"ROUTER: Cleaned up identity {target_zmq_id_str} due to unexpected ACK send error")
                return

    async def _send_ack_message_payload(self, target_zmq_identity: bytes, ack_payload: Dict[str, Any]):
        if not self.socket:
            raise Exception("ROUTER socket not available for sending ACK")

        # --- NEW: Check if the identity is still considered active before sending ---
        target_zmq_id_str = target_zmq_identity.decode('utf-8', 'ignore')
        if target_zmq_identity not in self._active_identities:
            logger.warning(f"ROUTER: Cannot send ACK to {target_zmq_id_str}. Identity is no longer active/known. It may have disconnected.")
            # Do not raise an exception here, just log and return.
            # The sender's ReliabilityManager will time out, which is the correct behavior.
            return 
        # --- END NEW ---

        try:
            ack_data = json.dumps(ack_payload).encode('utf-8')
            # Use a short timeout on the send to handle transient network issues
            # Note: ZMQ_SNDTIMEO sockopt might be a better global solution, but this is a targeted fix.
            logger.info(f"ROUTER_SEND_ACK: Sending ACK payload to ZMQ ID '{target_zmq_identity.decode('utf-8', 'ignore')}': {ack_payload}")
            await self.socket.send_multipart([target_zmq_identity, b'', ack_data])
        except zmq.Again:
            # This is less likely with ROUTER but possible if HWM is hit
            logger.error(f"ROUTER_SEND_ACK_ERROR: Failed sending ACK to '{target_zmq_identity.decode('utf-8', 'ignore')}': {e}")
            raise Exception(f"Send buffer full for ZMQ ID {target_zmq_id_str} while sending ACK")
        except zmq.ZMQError as e:
            # --- NEW: More specific handling for Host Unreachable ---
            if e.errno == zmq.EHOSTUNREACH:
                logger.error(f"ROUTER: Host Unreachable for ZMQ ID {target_zmq_id_str}. The client may have disconnected. Marking identity for cleanup.")
                # Proactively clean up the stale identity.
                self._active_identities.pop(target_zmq_identity, None)
                self._identity_last_seen.pop(target_zmq_identity, None)
            # Re-raise the original exception so the calling code knows it failed.
            raise Exception(f"Failed to send ACK payload to ZMQ ID {target_zmq_id_str}: {e}")
        except Exception as e:
            raise Exception(f"Failed to send ACK payload to ZMQ ID {target_zmq_id_str}: {e}")

    async def send_to_node(self, target_zmq_id_str: str, message_data: bytes) -> bool:
        if not self.socket:
            logger.error("ROUTER: Socket not started, cannot send.")
            return False

        if not message_data:
            logger.error(f"ROUTER: Cannot send empty message to ZMQ ID {target_zmq_id_str}")
            return False

        target_identity_bytes: Optional[bytes] = None
        for identity_bytes, zmq_id_str_val in self._active_identities.items():
            if zmq_id_str_val == target_zmq_id_str:
                target_identity_bytes = identity_bytes
                break

        if not target_identity_bytes:
            logger.warning(f"ROUTER: No active ZMQ identity found for target ZMQ ID string '{target_zmq_id_str}'. Cannot send.")
            return False
        
        current_swim_state = self._identity_swim_state.get(target_identity_bytes, "UNKNOWN")
        if self.swim_membership_callback:
            try:
                # MODIFIED: Parse SWIM ID here before calling the callback
                parsed_swim_id = target_zmq_id_str
                parts = target_zmq_id_str.split('-',2)
                if len(parts) >= 2 and parts[0] == 'dealer':
                     parsed_swim_id = parts[1]

                actual_swim_state = self.swim_membership_callback(parsed_swim_id)
                if actual_swim_state != current_swim_state:
                    logger.info(f"ROUTER: SWIM state mismatch for {target_zmq_id_str} (parsed as {parsed_swim_id}). Stored: {current_swim_state}, Actual: {actual_swim_state}. Using actual.")
                    current_swim_state = actual_swim_state
                    self._identity_swim_state[target_identity_bytes] = actual_swim_state

            except Exception as e:
                logger.warning(f"ROUTER: Error checking SWIM state for ZMQ ID {target_zmq_id_str}: {e}")

        if current_swim_state == "DEAD":
            logger.warning(f"ROUTER: Refusing to send to DEAD node (ZMQ ID: {target_zmq_id_str}, SWIM State: {current_swim_state})")
            return False
        elif current_swim_state == "SUSPECT":
            logger.warning(f"ROUTER: Sending to SUSPECT node (ZMQ ID: {target_zmq_id_str}, SWIM State: {current_swim_state}) (may fail)")

        try:
            await self.socket.send_multipart([target_identity_bytes, b'', message_data], zmq.NOBLOCK)
            logger.debug(f"ROUTER: Sent {len(message_data)} bytes to ZMQ ID {target_zmq_id_str}")
            return True

        except zmq.Again:
            logger.warning(f"ROUTER: Send buffer full for ZMQ ID {target_zmq_id_str}")
            return False
        except Exception as e:
            logger.error(f"ROUTER: Failed to send message to ZMQ ID {target_zmq_id_str}: {e}", exc_info=True)
            return False

    async def _process_dealer_message(self, zmq_node_id: str, message: Dict[str, Any]):
        """Process message received from DEALER socket (typically ACKs)."""
        try:
            message_type = message.get('type', 'unknown')
            logger.info(f"ROUTER: Processing DEALER message type '{message_type}' from {zmq_node_id}")
            
            # Route ACK messages to ACK system
            if message_type == 'ACK':
                if hasattr(self, '_message_handlers') and 'ACK' in self._message_handlers:
                    await self._message_handlers['ACK'](message, zmq_node_id)
                else:
                    logger.warning(f"ROUTER: No ACK handler registered for message from {zmq_node_id}")
            else:
                logger.warning(f"ROUTER: Unexpected message type '{message_type}' from DEALER {zmq_node_id}")
                
        except Exception as e:
            logger.error(f"ROUTER: Error processing DEALER message from {zmq_node_id}: {e}")

    async def _safe_call_handler(self, handler: Callable, sender_zmq_identity_str: str, message: Dict[str, Any]):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(sender_zmq_identity_str, message)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, handler, sender_zmq_identity_str, message)
        except Exception as e:
            logger.error(f"ROUTER: Error in message handler for ZMQ ID '{sender_zmq_identity_str}': {e}", exc_info=True)
            raise

    async def _health_check_loop(self):
        logger.info("ROUTER: Started health monitoring loop")

        while self._running:
            try:
                await asyncio.sleep(60) 
                await self._cleanup_stale_identities()
                await self._cleanup_stale_acks() 
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"ROUTER: Error in health check loop: {e}", exc_info=True)

        logger.info("ROUTER: Stopped health monitoring loop")

    async def _cleanup_stale_identities(self):
        current_time = time.time()
        stale_identities_to_remove: list[bytes] = [] 

        for raw_identity_bytes, last_seen_time in list(self._identity_last_seen.items()): 
            zmq_id_str = self._active_identities.get(raw_identity_bytes, "unknown_zmq_id")
            swim_state = self._identity_swim_state.get(raw_identity_bytes, "UNKNOWN")
            age = current_time - last_seen_time

            should_cleanup = False
            reason = ""

            if swim_state == "DEAD" and age > 60:
                should_cleanup = True
                reason = f"SWIM state is DEAD for {age:.1f}s"
            elif age > self.stale_identity_timeout:
                should_cleanup = True
                reason = f"no activity for {age:.1f}s"
            elif swim_state == "UNKNOWN" and age > 300:
                should_cleanup = True
                reason = f"unknown SWIM state for {age:.1f}s"

            if should_cleanup:
                stale_identities_to_remove.append(raw_identity_bytes)
                logger.info(f"ROUTER: Marking stale identity for ZMQ ID {zmq_id_str} for cleanup: {reason}")

        for raw_identity_bytes in stale_identities_to_remove:
            zmq_id_str_removed = self._active_identities.pop(raw_identity_bytes, "unknown_id_at_removal")
            self._identity_last_seen.pop(raw_identity_bytes, None)
            self._identity_swim_state.pop(raw_identity_bytes, None)
            self._message_counts.pop(raw_identity_bytes, None)
            logger.info(f"ROUTER: Cleaned up stale ZMQ identity: {zmq_id_str_removed}")

        if stale_identities_to_remove:
            logger.info(f"ROUTER: Cleaned up {len(stale_identities_to_remove)} stale ZMQ identities")

    async def _cleanup_stale_acks(self):
        current_time = time.time()
        stale_acks_to_remove: list[str] = []

        for message_id, timestamp in list(self._pending_acks.items()): 
            if current_time - timestamp > self.ack_timeout:
                stale_acks_to_remove.append(message_id)

        for message_id in stale_acks_to_remove:
            self._pending_acks.pop(message_id, None) 
            logger.warning(f"ROUTER: Cleaned up stale pending ACK (local router tracking) for {message_id}")

        if stale_acks_to_remove:
            logger.info(f"ROUTER: Cleaned up {len(stale_acks_to_remove)} stale pending ACKs (local router tracking)")


    def register_handler(self, message_type: str, handler: Callable):
        if not callable(handler):
            raise ValueError(f"Handler for {message_type} must be callable")

        self._message_handlers[message_type] = handler
        logger.info(f"ROUTER: Registered handler for {message_type}")

    def set_default_handler(self, handler: Callable):
        if not callable(handler):
            raise ValueError("Default handler must be callable")

        self._default_handler = handler
        logger.info("ROUTER: Set default message handler")

    def get_router_stats(self) -> Dict[str, Any]:
        current_time = time.time()

        swim_state_counts = defaultdict(int)
        for swim_state in self._identity_swim_state.values():
            swim_state_counts[swim_state] += 1

        total_messages = sum(self._message_counts.values())

        client_details_list = []
        for raw_identity, zmq_id_str_val in self._active_identities.items():
            client_details_list.append({
                "zmq_id_str": zmq_id_str_val,
                "swim_state": self._identity_swim_state.get(raw_identity, "UNKNOWN"),
                "last_seen_ago_sec": current_time - self._identity_last_seen.get(raw_identity, 0),
                "message_count": self._message_counts.get(raw_identity, 0)
            })

        return {
            "bind_address": self.bind_address,
            "running": self._running,
            "active_clients": len(self._active_identities),
            "total_messages_received_by_router": total_messages,
            "swim_state_distribution_of_clients": dict(swim_state_counts),
            "pending_acks_router_local": len(self._pending_acks), 
            "delivery_confirmations_router_local": len(self._delivery_confirmations), 
            "registered_handlers": len(self._message_handlers),
            "has_default_handler": self._default_handler is not None,
            "configuration": {
                "ack_timeout": self.ack_timeout,
                "stale_identity_timeout": self.stale_identity_timeout,
                "port_validation_timeout": self.port_validation_timeout
            },
            "clients": client_details_list
        }

    def get_client_details(self, target_zmq_id_str: str) -> Optional[Dict[str, Any]]:
        raw_identity_bytes: Optional[bytes] = None
        for identity_bytes, zmq_id_str_val in self._active_identities.items():
            if zmq_id_str_val == target_zmq_id_str:
                raw_identity_bytes = identity_bytes
                break

        if not raw_identity_bytes:
            return None

        current_time = time.time()
        last_seen = self._identity_last_seen.get(raw_identity_bytes, 0)

        return {
            "zmq_id_str": target_zmq_id_str,
            "swim_state": self._identity_swim_state.get(raw_identity_bytes, "UNKNOWN"),
            "last_seen_timestamp": last_seen,
            "last_seen_ago_sec": current_time - last_seen,
            "message_count": self._message_counts.get(raw_identity_bytes, 0),
            "raw_zmq_identity_bytes_hex": raw_identity_bytes.hex() 
        }