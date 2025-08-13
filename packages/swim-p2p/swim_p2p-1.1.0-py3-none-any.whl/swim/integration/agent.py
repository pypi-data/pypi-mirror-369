"""
Agent integration interface for the ZMQ integration layer.

This module provides the main orchestrator that combines all ZMQ components
and demonstrates their integration with comprehensive logging.
"""

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, Any, Optional

from swim.events.types import Event # Keep for potential future use
from swim.events.dispatcher import EventDispatcher

# Import ZMQ components
from swim.integration.zmq.dealer import EnhancedDealerManager
from swim.integration.zmq.router import RouterManager
from swim.integration.zmq.connection_manager import ConnectionManager
from swim.integration.zmq.capacity_tracker import CapacityTracker
from swim.integration.zmq.flow_control import FlowControlManager

# Import messaging components
from swim.integration.messaging.reliability import ReliabilityManager
from swim.integration.messaging.ack_system import AckSystem
from swim.integration.messaging.circuit_breaker import CircuitBreakerManager
from swim.integration.messaging.buffer_monitor import BufferMonitor
from swim.integration.messaging.workflow import WorkflowManager
from swim.integration.messaging.trace import start_trace, inject_context, log_trace_event, extract_context, TraceContext

logger = logging.getLogger(__name__)

class ZMQAgentIntegration:
    """
    Main orchestrator for ZMQ messaging integration with SWIM protocol.

    Combines all ZMQ components and demonstrates reliable messaging
    with comprehensive observability and logging.
    """

    def __init__(self, node_id: str, bind_address: str, event_dispatcher: EventDispatcher, config: Dict[str, Any]):
        """
        Initialize ZMQ Agent Integration.

        Args:
            node_id: This node's identifier (SWIM address format, e.g., "127.0.0.1:5555")
            bind_address: Address to bind ROUTER socket (e.g., "127.0.0.1:6000")
            event_dispatcher: SWIM event dispatcher
            config: Main application configuration dictionary
        """
        self.node_id = node_id 
        self.bind_address = bind_address 
        self.event_dispatcher = event_dispatcher
        self.config = config
        self.node_name = config.get("NODE_NAME") # Get from config
        if not self.node_name: # Generate a default if not provided
            try:
                _, port_str = node_id.split(":")
                self.node_name = f"Node@{port_str}"
            except ValueError:
                self.node_name = f"Node@{uuid.uuid4().hex[:6]}" # Fallback if node_id format is unexpected
        
        logger.info(f"ZMQ_AGENT_INIT: Initializing ZMQ messaging for node '{self.node_name}' (SWIM ID: {node_id})")
        logger.info(f"ZMQ_AGENT_INIT: ROUTER binding to {bind_address}")

        self._initialize_components()
        self._wire_components()

        self.message_count = 0
        self.successful_messages = 0
        self.failed_messages = 0

        self._running = False

        logger.info(f"ZMQ_AGENT_INIT: All components initialized and wired for node '{self.node_name}'")

    def _initialize_components(self):
        logger.info(f"ZMQ_COMPONENTS ({self.node_name}): Initializing ZMQ components")

        self.dealer_manager = EnhancedDealerManager(self.node_id)
        self.router_manager = RouterManager(self.bind_address)

        port_manager_instance = None
        self.connection_manager = ConnectionManager(self.node_id, port_manager=port_manager_instance)

        self.reliability_manager = ReliabilityManager(self.node_id)
        self.ack_system = AckSystem(self.node_id) 

        self.circuit_breaker_manager = CircuitBreakerManager(self.node_id)
        self.capacity_tracker = CapacityTracker(self.node_id)
        self.flow_control = FlowControlManager(self.node_id)
        self.buffer_monitor = BufferMonitor(self.node_id)
        self.workflow_manager = WorkflowManager(self.node_id)
        logger.info(f"ZMQ_COMPONENTS ({self.node_name}): All managers created")


    def _wire_components(self):

        logger.info(f"ZMQ_WIRING ({self.node_name}): Connecting components")
        self.connection_manager.set_dealer_callbacks(
            connect_callback=self.dealer_manager.get_connection,
            disconnect_callback=self.dealer_manager.mark_failed
        )
        self.reliability_manager.set_transport_callback(self._transport_send_via_dealer)
        self.reliability_manager.set_swim_membership_callback(self._check_swim_alive_for_reliability)
        self.reliability_manager.set_circuit_breaker_callback(self._check_circuit_closed_for_reliability)
        self.reliability_manager.set_connection_manager_callback(self.connection_manager)
        self.reliability_manager.set_ack_system_callback(self.ack_system)
        self.ack_system.set_reliability_callback(self._forward_ack_to_reliability_manager)
        self.ack_system.set_transport_callback(self._transport_send_ack_via_router)
        self.router_manager.set_swim_callback(self._get_swim_state_for_router_identity)
        self.router_manager.set_reliability_callback(self.reliability_manager)
        self.dealer_manager.set_router_manager_callback(self.router_manager._process_dealer_message)

        # Register handlers for specific message types
        self.router_manager.register_handler("AUTOMATED_CHECK_IN", self._handle_automated_check_in)
        self.router_manager.register_handler("CHECK_IN_RESPONSE", self._handle_check_in_response) # For potential responses

        # Keep other handlers if they are still relevant or for general use
        self.router_manager.register_handler("HELLO_MESSAGE", self._handle_hello_message) 
        self.router_manager.register_handler("CUSTOM_MESSAGE", self._handle_custom_message)
        self.router_manager.register_handler("CONNECTION_TEST", self._handle_connection_test)
        self.router_manager.register_handler("CIRCUIT_BREAKER_PROBE", self._handle_circuit_probe)
        self.router_manager.register_handler("CIRCUIT_BREAKER_PROBE_ACK", self._handle_circuit_probe_ack)
        self.router_manager.register_handler("ACK", self.ack_system.handle_incoming_ack)

        self.capacity_tracker.set_capacity_change_callback(self._on_capacity_change)
        self.flow_control.set_capacity_provider(self._get_node_capacity)
        self.buffer_monitor.set_buffer_overflow_callback(self._on_buffer_overflow)
        logger.info(f"ZMQ_WIRING ({self.node_name}): All components wired successfully")



    async def start(self):
        if self._running:
            logger.warning(f"ZMQ_AGENT_STARTUP ({self.node_name}): Agent already running.")
            return

        logger.info(f"ZMQ_AGENT_STARTUP ({self.node_name}): Starting ZMQ Agent Integration")
        try:
            await self.router_manager.start()
            logger.info(f"ZMQ_ROUTER_READY ({self.node_name}): Bound to {self.bind_address}")
            await self.dealer_manager.start()
            logger.info(f"ZMQ_DEALER_READY ({self.node_name}): Connection pool initialized")
            await self.reliability_manager.start() 
            await self.ack_system.start()
            logger.info(f"ZMQ_RELIABILITY_READY ({self.node_name}): Message tracking active")
            await self.capacity_tracker.start()
            await self.flow_control.start()
            await self.buffer_monitor.start()
            await self.workflow_manager.start()
            await self.connection_manager.start()
            self._running = True
            logger.info(f"ZMQ_MONITORING_READY ({self.node_name}): All monitoring systems active")
            logger.info(f"ZMQ_READY ({self.node_name}): Node ready for reliable messaging")
        except Exception as e:
            logger.error(f"ZMQ_STARTUP_FAILED for {self.node_name}: {e}", exc_info=True)
            await self.stop()
            raise

    async def stop(self):
        if not self._running:
            logger.warning(f"ZMQ_AGENT_SHUTDOWN ({self.node_name}): Agent already stopped or not started.")
            return

        logger.info(f"ZMQ_AGENT_SHUTDOWN ({self.node_name}): Gracefully stopping all components")
        self._running = False
        components_to_stop = [
            ("connection_manager", self.connection_manager),
            ("workflow_manager", self.workflow_manager),
            ("buffer_monitor", self.buffer_monitor),
            ("flow_control", self.flow_control),
            ("capacity_tracker", self.capacity_tracker),
            ("ack_system", self.ack_system),
            ("reliability_manager", self.reliability_manager),
            ("dealer_manager", self.dealer_manager),
            ("router_manager", self.router_manager),
        ]
        for name, component in components_to_stop:
            try:
                if hasattr(component, 'stop') and asyncio.iscoroutinefunction(component.stop):
                    await component.stop()
                elif hasattr(component, 'stop'):
                    component.stop() # type: ignore
                logger.info(f"ZMQ_SHUTDOWN ({self.node_name}): {name} stopped")
            except Exception as e:
                logger.error(f"ZMQ_SHUTDOWN_ERROR ({self.node_name}): Failed to stop {name}: {e}", exc_info=True)
        logger.info(f"ZMQ_SHUTDOWN ({self.node_name}): Complete")

    async def handle_swim_member_joined(self, swim_node_id_str: str):
        """
        Handle SWIM member join or resurrection.
        This method handles both new members joining and previously failed members being resurrected.
        """
        logger.info(f"ZMQ_API ({self.node_name}): Member {swim_node_id_str} joined/resurrected, setting up ZMQ connections")
        self.capacity_tracker.register_node(swim_node_id_str)
        self.flow_control.register_node(swim_node_id_str)
        try:
            host, port_str = swim_node_id_str.split(':')
            swim_port = int(port_str)
            zmq_port_offset = self.config.get("ZMQ_PORT_OFFSET", 1000)
            zmq_port = swim_port + zmq_port_offset
            self.connection_manager.register_port_mapping( swim_port=swim_port, zmq_port=zmq_port, host=host, node_id=swim_node_id_str )
            logger.info(f"ZMQ_API ({self.node_name}): Port mapping registered for {swim_node_id_str}: SWIM Port {swim_port} -> ZMQ Port {zmq_port} on host {host}")
        except Exception as e:
            logger.error(f"ZMQ_API ({self.node_name}): Port mapping failed for {swim_node_id_str}: {e}", exc_info=True)
        await self.connection_manager.handle_swim_membership_change(swim_node_id_str, "ALIVE")
        logger.info(f"ZMQ_API ({self.node_name}): Ready for messaging with {swim_node_id_str}")

    async def handle_swim_member_left(self, swim_node_id_str: str):
        logger.info(f"ZMQ_API ({self.node_name}): Member {swim_node_id_str} left, cleaning up ZMQ resources")
        await self.connection_manager.handle_swim_membership_change(swim_node_id_str, "DEAD")
        self.capacity_tracker.unregister_node(swim_node_id_str)
        self.flow_control.unregister_node(swim_node_id_str)
        logger.info(f"ZMQ_API ({self.node_name}): Cleanup complete for {swim_node_id_str}")

    async def handle_swim_member_suspected(self, swim_node_id_str: str):
        logger.warning(f"ZMQ_API ({self.node_name}): Member {swim_node_id_str} suspected, degrading ZMQ connections")
        await self.connection_manager.handle_swim_membership_change(swim_node_id_str, "SUSPECT")
        logger.warning(f"ZMQ_API ({self.node_name}): Connections to {swim_node_id_str} degraded")

    async def handle_swim_member_failed(self, swim_node_id_str: str):
        logger.error(f"ZMQ_API ({self.node_name}): Member {swim_node_id_str} failed, closing ZMQ connections")
        await self.connection_manager.handle_swim_membership_change(swim_node_id_str, "DEAD")
        logger.error(f"ZMQ_API ({self.node_name}): Connections to {swim_node_id_str} closed")

    async def send_message_base(self, target_swim_node_id_str: str, message_type: str,
                                message_content_key: str, message_content_value: str,
                                operation_name: str) -> bool:
        self.message_count += 1
        message_id_for_payload_and_rm = str(uuid.uuid4())
        trace_context_obj = start_trace(f"ZMQ_{operation_name}_{self.node_name}", f"send_{operation_name.lower()}")
        logger.info(f"ZMQ_SEND ({self.node_name}): Sending {operation_name} to SWIM node {target_swim_node_id_str} (MsgID: {message_id_for_payload_and_rm})")
        target_zmq_address: Optional[str] = self.connection_manager.get_zmq_address_for_swim(target_swim_node_id_str)

        if not target_zmq_address:
            logger.error(f"ZMQ_SEND ({self.node_name}): Could not map SWIM ID {target_swim_node_id_str} to ZMQ address. Message {message_id_for_payload_and_rm} not sent.")
            if trace_context_obj: log_trace_event(trace_context_obj, f"ZMQ_{operation_name}_{self.node_name}", "address_mapping_failed", {"swim_target": target_swim_node_id_str})
            self.failed_messages += 1
            return False

        message_payload = {
            "type": message_type, "id": message_id_for_payload_and_rm, "from_node": self.node_id, # SWIM ID of sender
            "from_node_name": self.node_name, # Friendly name of sender
            message_content_key: message_content_value,
            "timestamp": time.time(), "sequence": self.message_count, "require_ack": True
        }
        message_payload = inject_context(message_payload, trace_context_obj)
        message_data = json.dumps(message_payload).encode('utf-8')
        log_trace_event(trace_context_obj, f"ZMQ_{operation_name}_{self.node_name}", "payload_created", {"size_bytes": len(message_data), "target_swim": target_swim_node_id_str, "target_zmq": target_zmq_address})

        try:
            logger.info(f"ZMQ_SEND ({self.node_name}): Initiating reliable send for MsgID {message_id_for_payload_and_rm} to ZMQ node {target_zmq_address} (for SWIM: {target_swim_node_id_str})")
            success = await self.reliability_manager.send_reliable(
                target_node=target_zmq_address,
                message_data=message_data,
                message_id_override=message_id_for_payload_and_rm,
                trace_id=trace_context_obj.trace_id if trace_context_obj else None,
                timeout=30.0
            )
            if success:
                self.successful_messages += 1
                if trace_context_obj: log_trace_event(trace_context_obj, f"ZMQ_{operation_name}_{self.node_name}", "delivery_successful", {})
            else:
                self.failed_messages += 1
                failure_reason_for_cm = "send_reliable_returned_false"
                if not self.connection_manager.can_send_to_node(target_zmq_address):
                    failure_reason_for_cm = "CONNECTION_READINESS_CHECK_FAILED_AT_SEND_TIME"
                if trace_context_obj: log_trace_event(trace_context_obj, f"ZMQ_{operation_name}_{self.node_name}", "delivery_failed", {"reason": failure_reason_for_cm})
            logger.info(f"ZMQ_SEND_OUTCOME ({self.node_name}): Message {message_id_for_payload_and_rm} to {target_swim_node_id_str} (via ZMQ {target_zmq_address}): {'SUCCESS' if success else 'FAILED'}")
            return success
        except Exception as e:
            self.failed_messages += 1
            logger.error(f"ZMQ_SEND_EXCEPTION ({self.node_name}): sending MsgID {message_id_for_payload_and_rm} to {target_swim_node_id_str} (via ZMQ {target_zmq_address}): {e}", exc_info=True)
            if trace_context_obj: log_trace_event(trace_context_obj, f"ZMQ_{operation_name}_{self.node_name}", "exception", {"error": str(e)})
            return False

    async def send_automated_check_in(self, target_swim_node_id_str: str) -> bool:
        """Sends an automated 'checking in' message to a target node."""
        message_text = f"Hello, this is {self.node_name} checking in."
        logger.info(f"ZMQ_AGENT ({self.node_name}): Preparing automated check-in to {target_swim_node_id_str}")
        return await self.send_message_base(
            target_swim_node_id_str,
            "AUTOMATED_CHECK_IN",
            "check_in_message", # Key for the message content
            message_text,
            "AutomatedCheckIn" # Operation name for tracing
        )

    # Kept for general use or other demos if needed
    async def send_hello_message(self, target_swim_node_id_str: str) -> bool:
        hello_content = f"Generic Hello from {self.node_name} (SWIM ID: {self.node_id}), this is message attempt #{self.message_count}"
        return await self.send_message_base(
            target_swim_node_id_str, "HELLO_MESSAGE", "message", hello_content, "HelloDemo"
        )

    async def send_custom_message(self, target_swim_node_id_str: str, custom_message_text: str) -> bool:
        return await self.send_message_base(
            target_swim_node_id_str, "CUSTOM_MESSAGE", "custom_message", custom_message_text, "CustomMessage"
        )

    async def _transport_send_via_dealer(self, target_zmq_node_id_str: str, message_data: bytes) -> bool:
        logger.debug(f"ZMQ_TRANSPORT_SEND_CB ({self.node_name}): Sending {len(message_data)} bytes to ZMQ node {target_zmq_node_id_str} via Dealer")
        return await self.dealer_manager.send_message(target_zmq_node_id_str, message_data)

    async def _transport_send_ack_via_router(self, target_zmq_node_id_str: str, ack_data: bytes) -> bool:
        logger.debug(f"ZMQ_ACK_TRANSPORT_SEND_CB ({self.node_name}): Sending ACK to ZMQ node {target_zmq_node_id_str} via Router")
        return await self.router_manager.send_to_node(target_zmq_node_id_str, ack_data)

    def _check_swim_alive_for_reliability(self, target_zmq_node_id_str: str) -> bool:
        swim_node_id_str = self.connection_manager.get_swim_address_for_zmq(target_zmq_node_id_str)
        if not swim_node_id_str:
            logger.warning(f"SWIM_ALIVE_CHECK_CB ({self.node_name}): Could not map ZMQ address {target_zmq_node_id_str} back to SWIM ID. Assuming not alive.")
            return False
        conn_info = self.connection_manager.get_connection_info(swim_node_id_str)
        is_alive = conn_info is not None and conn_info.get("swim_protocol_state") == "ALIVE"
        logger.debug(f"SWIM_ALIVE_CHECK_CB ({self.node_name}): Target ZMQ {target_zmq_node_id_str} (SWIM: {swim_node_id_str}) is_alive: {is_alive} (SWIM state: {conn_info.get('swim_protocol_state') if conn_info else 'N/A'})")
        return is_alive

    def _check_circuit_closed_for_reliability(self, target_zmq_node_id_str: str) -> bool:
        status = self.circuit_breaker_manager.get_circuit_status(target_zmq_node_id_str)
        is_closed = status is None or status.get("state") == "CLOSED"
        logger.debug(f"CIRCUIT_CLOSED_CHECK_CB ({self.node_name}): Circuit for ZMQ node {target_zmq_node_id_str} is_closed: {is_closed}")
        return is_closed

    def _get_swim_state_for_router_identity(self, swim_id_str: str) -> str:
        sender_swim_id = swim_id_str
        conn_info = self.connection_manager.get_connection_info(sender_swim_id)
        if conn_info and conn_info.get("swim_protocol_state"):
            state = conn_info["swim_protocol_state"]
            logger.debug(f"SWIM_STATE_GET_CB_FOR_ROUTER ({self.node_name}): SWIM state for {sender_swim_id} is {state}")
            return state
        logger.warning(f"SWIM_STATE_GET_CB_FOR_ROUTER ({self.node_name}): Could not get SWIM state for {sender_swim_id}. Returning UNKNOWN.")
        return "UNKNOWN"

    async def _forward_ack_to_reliability_manager(self, message_id: str, ack_type_str: str, success: bool):
        logger.debug(f"ACK_FORWARD_CB ({self.node_name}): {ack_type_str.upper()} ACK for {message_id}, success={success} -> to ReliabilityManager")
        if ack_type_str.lower() == "delivery":
            await self.reliability_manager.handle_delivery_ack(message_id, success)
        elif ack_type_str.lower() == "processing":
            await self.reliability_manager.handle_processing_ack(message_id, success)
        else:
            logger.warning(f"ACK_FORWARD_CB ({self.node_name}): Unknown ACK type '{ack_type_str}' for message {message_id}.")

    def _get_node_capacity(self, swim_node_id_str: str) -> Optional[Dict[str, Any]]:
        node_cap = self.capacity_tracker.get_node_capacity(swim_node_id_str)
        return node_cap.get_capacity_summary() if node_cap else None

    async def _on_capacity_change(self, swim_node_id_str: str, old_state, new_state):
        logger.info(f"ZMQ_CAPACITY_CHANGE_CB ({self.node_name}): Node {swim_node_id_str} capacity {old_state.name} -> {new_state.name}")

    async def _on_buffer_overflow(self, buffer_id: str, metrics):
        logger.error(f"ZMQ_BUFFER_OVERFLOW_CB ({self.node_name}): {buffer_id} at {metrics.current_size}/{metrics.max_size}")

    async def _handle_automated_check_in(self, sender_zmq_identity_str: str, message: Dict[str, Any]):
        original_sender_swim_id = message.get('from_node', 'unknown_sender')
        original_sender_node_name = message.get('from_node_name', original_sender_swim_id)
        check_in_message_text = message.get('check_in_message', '')
        
        logger.info(f"ZMQ_HANDLER ({self.node_name}): *** RECEIVED AUTOMATED CHECK-IN from {original_sender_node_name} (ZMQ ID: {sender_zmq_identity_str}, SWIM ID: {original_sender_swim_id}) ***")
        logger.info(f"ZMQ_HANDLER ({self.node_name}): Check-in content: '{check_in_message_text}' (MsgID: {message.get('id')})")

        trace_context = extract_context(message)
        if trace_context: log_trace_event(trace_context, f"ZMQ_CheckInHandler_{self.node_name}", "check_in_received", {"sender_zmq_id": sender_zmq_identity_str, "sender_node_name": original_sender_node_name, "message_content": check_in_message_text})
        
        # Optionally, send a response
        response_text = f"Hello {original_sender_node_name}, this is {self.node_name}. Received your check-in."
        logger.info(f"ZMQ_HANDLER ({self.node_name}): Sending CHECK_IN_RESPONSE to {original_sender_node_name} (SWIM ID: {original_sender_swim_id})")

        asyncio.create_task(
        self.send_message_base(
            original_sender_swim_id,
            "CHECK_IN_RESPONSE",
            "response_message",
            response_text,
            "CheckInResponse"
        )
    )

    async def _handle_check_in_response(self, sender_zmq_identity_str: str, message: Dict[str, Any]):
        original_sender_swim_id = message.get('from_node', 'unknown_sender')
        original_sender_node_name = message.get('from_node_name', original_sender_swim_id)
        response_message_text = message.get('response_message', '')

        logger.info(f"ZMQ_HANDLER ({self.node_name}): *** RECEIVED CHECK_IN_RESPONSE from {original_sender_node_name} (ZMQ ID: {sender_zmq_identity_str}, SWIM ID: {original_sender_swim_id}) ***")
        logger.info(f"ZMQ_HANDLER ({self.node_name}): Response content: '{response_message_text}' (MsgID: {message.get('id')})")

        trace_context = extract_context(message)
        if trace_context: log_trace_event(trace_context, f"ZMQ_CheckInResponseHandler_{self.node_name}", "response_received", {"sender_zmq_id": sender_zmq_identity_str, "sender_node_name": original_sender_node_name, "message_content": response_message_text})


    async def _handle_hello_message(self, sender_zmq_identity_str: str, message: Dict[str, Any]):
        original_sender_swim_id = message.get('from_node', 'unknown_sender')
        original_sender_node_name = message.get('from_node_name', original_sender_swim_id) # Get friendly name
        logger.info(f"ZMQ_HANDLER ({self.node_name}): *** RECEIVED HELLO MESSAGE from {original_sender_node_name} (ZMQ ID: {sender_zmq_identity_str}, SWIM ID: {original_sender_swim_id}) ***")
        logger.info(f"ZMQ_HANDLER ({self.node_name}): Message content: {message.get('message', 'No message content')} (MsgID: {message.get('id')})")
        trace_context = extract_context(message)
        if trace_context: log_trace_event(trace_context, f"ZMQ_HelloHandler_{self.node_name}", "message_received", {"sender_zmq_id": sender_zmq_identity_str, "sender_node_name": original_sender_node_name, "sequence": message.get("sequence",0)})
        try:
            response_text = f"Hello back from {self.node_name}! Got your hello: '{message.get('message', '')}'"
            logger.info(f"ZMQ_HANDLER ({self.node_name}): Sending HELLO response to {original_sender_node_name} (SWIM ID: {original_sender_swim_id})")
            # Use send_custom_message for generic replies if HELLO_MESSAGE is just for initial contact.
            await self.send_custom_message(original_sender_swim_id, response_text) 
        except Exception as e:
            logger.error(f"ZMQ_HANDLER ({self.node_name}): Failed to send HELLO response to {original_sender_node_name}: {e}", exc_info=True)

    async def _handle_custom_message(self, sender_zmq_identity_str: str, message: Dict[str, Any]):
        original_sender_swim_id = message.get('from_node', 'unknown_sender')
        original_sender_node_name = message.get('from_node_name', original_sender_swim_id)
        custom_msg_text = message.get('custom_message', '')
        logger.info(f"ZMQ_HANDLER ({self.node_name}): *** RECEIVED CUSTOM MESSAGE from {original_sender_node_name} (ZMQ ID: {sender_zmq_identity_str}, SWIM ID: {original_sender_swim_id}) ***")
        logger.info(f"ZMQ_HANDLER ({self.node_name}): Custom message content: '{custom_msg_text}' (MsgID: {message.get('id')})")
        trace_context = extract_context(message)
        if trace_context: log_trace_event(trace_context, f"ZMQ_CustomHandler_{self.node_name}", "message_received", {"sender_zmq_id": sender_zmq_identity_str, "sender_node_name": original_sender_node_name, "custom_message": custom_msg_text})
        try:
            response_text = f"Acknowledged custom message from {original_sender_node_name}: '{custom_msg_text}' (I am {self.node_name})"
            logger.info(f"ZMQ_HANDLER ({self.node_name}): Sending CUSTOM response to {original_sender_node_name} (SWIM ID: {original_sender_swim_id})")
            await self.send_custom_message(original_sender_swim_id, response_text)
        except Exception as e:
            logger.error(f"ZMQ_HANDLER ({self.node_name}): Failed to send CUSTOM response to {original_sender_node_name}: {e}", exc_info=True)

    async def _handle_connection_test(self, sender_zmq_identity_str: str, message: Dict[str, Any]):
        original_sender_swim_id = message.get('source', 'unknown_sender') # Assuming 'source' is SWIM ID
        original_sender_node_name = message.get('from_node_name', original_sender_swim_id)
        logger.info(f"ZMQ_HANDLER ({self.node_name}): Connection test received from {original_sender_node_name} (ZMQ ID: {sender_zmq_identity_str}, SWIM ID: {original_sender_swim_id})")
        pong_message = { "type": "CONNECTION_TEST_PONG", "id": str(uuid.uuid4()), "ack_for": message.get("id"), "from_node": self.node_id, "from_node_name": self.node_name, "timestamp": time.time() }
        pong_data = json.dumps(pong_message).encode('utf-8')
        if self.router_manager and self.router_manager.socket:
            try:
                active_raw_identity = None
                for raw_id, id_str in self.router_manager._active_identities.items():
                    if id_str == sender_zmq_identity_str: active_raw_identity = raw_id; break
                if active_raw_identity:
                    await self.router_manager.socket.send_multipart([active_raw_identity, b'', pong_data])
                    logger.info(f"ZMQ_HANDLER ({self.node_name}): Sent CONNECTION_TEST_PONG to {original_sender_node_name} (ZMQ ID: {sender_zmq_identity_str})")
                else: logger.warning(f"ZMQ_HANDLER ({self.node_name}): Could not find active raw ZMQ identity for {sender_zmq_identity_str} to send PONG.")
            except Exception as e: logger.error(f"ZMQ_HANDLER ({self.node_name}): Failed to send PONG for connection test to {sender_zmq_identity_str}: {e}", exc_info=True)

    async def _handle_circuit_probe(self, sender_zmq_identity_str: str, message: Dict[str, Any]):
        original_sender_swim_id = message.get('source_swim_id', 'unknown_sender')
        original_sender_node_name = message.get('from_node_name', original_sender_swim_id) # Assuming probe might also send this
        logger.info(f"ZMQ_HANDLER ({self.node_name}): Circuit breaker probe received from {original_sender_node_name} (ZMQ ID: {sender_zmq_identity_str}, SWIM ID: {original_sender_swim_id})")
        probe_ack_message = { "type": "CIRCUIT_BREAKER_PROBE_ACK", "id": str(uuid.uuid4()), "ack_for": message.get("id"), "from_node": self.node_id, "from_node_name": self.node_name, "status": "HEALTHY", "timestamp": time.time() }
        probe_ack_data = json.dumps(probe_ack_message).encode('utf-8')
        if self.router_manager and self.router_manager.socket:
            try:
                target_identity_bytes = None
                for raw_id, id_str in self.router_manager._active_identities.items():
                    if id_str == sender_zmq_identity_str: target_identity_bytes = raw_id; break
                if target_identity_bytes:
                    await self.router_manager.socket.send_multipart([target_identity_bytes, b'', probe_ack_data])
                    logger.info(f"ZMQ_HANDLER ({self.node_name}): Sent CIRCUIT_BREAKER_PROBE_ACK to {original_sender_node_name} (ZMQ ID: {sender_zmq_identity_str})")
                else: logger.warning(f"ZMQ_HANDLER ({self.node_name}): Could not find active raw ZMQ identity for {sender_zmq_identity_str} to send PROBE_ACK.")
            except Exception as e: logger.error(f"ZMQ_HANDLER ({self.node_name}): Failed to send PROBE_ACK to {sender_zmq_identity_str}: {e}", exc_info=True)

    async def _handle_circuit_probe_ack(self, sender_zmq_identity_str: str, message: Dict[str, Any]):
        ack_sender_swim_id = message.get('from_node', 'unknown_ack_sender')
        ack_sender_node_name = message.get('from_node_name', ack_sender_swim_id)
        acked_probe_id = message.get('ack_for')
        status = message.get('status', 'UNKNOWN')
        logger.info(f"ZMQ_HANDLER ({self.node_name}): Received CIRCUIT_BREAKER_PROBE_ACK from {ack_sender_node_name} (ZMQ ID: {sender_zmq_identity_str}, SWIM ID: {ack_sender_swim_id}) for probe {acked_probe_id}, status: {status}")
        target_zmq_address_for_cb = self.connection_manager.get_zmq_address_for_swim(ack_sender_swim_id)
        if target_zmq_address_for_cb:
            cb = await self.circuit_breaker_manager.get_or_create_circuit_breaker(target_zmq_address_for_cb)
            if status == "HEALTHY": await cb._record_success(); logger.info(f"ZMQ_HANDLER ({self.node_name}): Probe ACK indicates {ack_sender_node_name} (ZMQ {target_zmq_address_for_cb}) is healthy. Recorded success for its circuit breaker.")
            else: await cb._record_failure(); logger.warning(f"ZMQ_HANDLER ({self.node_name}): Probe ACK indicates {ack_sender_node_name} (ZMQ {target_zmq_address_for_cb}) is NOT healthy ({status}). Recorded failure for its circuit breaker.")
        else: logger.warning(f"ZMQ_HANDLER ({self.node_name}): Could not map SWIM ID {ack_sender_swim_id} (from probe ACK sender) to ZMQ address for circuit breaker update.")

    def get_integration_status(self) -> Dict[str, Any]:
        dealer_stats = self.dealer_manager.get_connection_stats() if self.dealer_manager else {}
        router_stats = self.router_manager.get_router_stats() if self.router_manager else {}
        reliability_stats = self.reliability_manager.get_statistics() if self.reliability_manager else {}
        capacity_stats = self.capacity_tracker.get_statistics() if self.capacity_tracker else {}
        circuit_stats = self.circuit_breaker_manager.get_all_circuit_status() if self.circuit_breaker_manager else {}
        buffer_stats = self.buffer_monitor.get_all_buffer_status() if self.buffer_monitor else {}
        conn_mgr_stats = self.connection_manager.get_connection_statistics() if self.connection_manager else {}
        return {
            "node_id": self.node_id, "node_name": self.node_name, "bind_address": self.bind_address, "running": self._running,
            "message_stats": { "total_sent_attempts_by_agent": self.message_count, "successful_reliable_sends_by_agent": self.successful_messages, "failed_reliable_sends_by_agent": self.failed_messages, "success_rate_agent": f"{self.successful_messages / max(self.message_count, 1) * 100:.1f}%" },
            "component_status": { "dealer": dealer_stats, "router": router_stats, "reliability": reliability_stats, "capacity": capacity_stats, "circuits": circuit_stats, "buffers": buffer_stats, "connection_manager": conn_mgr_stats }
        }


async def demo_zmq_messaging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    logger.info("ZMQ_DEMO: Starting ZMQ messaging demonstration")
    class DummyEventDispatcher:
        def subscribe(self, event_type, handler): pass
        def emit(self, event): pass
    event_dispatcher = DummyEventDispatcher() # type: ignore

    node1_swim_addr_str = "127.0.0.1:8000"
    node1_zmq_router_bind_addr_str = "127.0.0.1:9000"
    # Changed ZMQ_CUSTOM_MESSAGE to NODE_NAME, SEND_ON_JOIN will trigger automated check-in
    config1 = {"ZMQ_PORT_OFFSET": 1000, "NODE_NAME": "NodeA", "SEND_ON_JOIN": True, "ZMQ_ENABLED": True}

    node2_swim_addr_str = "127.0.0.1:8001"
    node2_zmq_router_bind_addr_str = "127.0.0.1:9001"
    config2 = {"ZMQ_PORT_OFFSET": 1000, "NODE_NAME": "NodeB", "SEND_ON_JOIN": True, "ZMQ_ENABLED": True}

    node1_agent = ZMQAgentIntegration(node1_swim_addr_str, node1_zmq_router_bind_addr_str, event_dispatcher, config1)
    node2_agent = ZMQAgentIntegration(node2_swim_addr_str, node2_zmq_router_bind_addr_str, event_dispatcher, config2)

    try:
        logger.info("ZMQ_DEMO: Starting nodes")
        await node1_agent.start()
        await node2_agent.start()
        await asyncio.sleep(1.0)

        logger.info("ZMQ_DEMO: Simulating SWIM membership events (manual ZMQ setup)")
        # Simulate Node B joining Node A's perspective
        await node1_agent.handle_swim_member_joined(node2_swim_addr_str) 
        # Simulate Node A joining Node B's perspective
        await node2_agent.handle_swim_member_joined(node1_swim_addr_str) 

        # The SWIMZMQBridge's _monitor_stability_and_trigger_messaging loop will handle sending
        # the automated check-in messages after its stability_timeout.
        # Let's wait for more than the default stability timeout (e.g., 3s) + some buffer
        logger.info("ZMQ_DEMO: Waiting for stability and automated check-in messages (e.g., 5-7 seconds)...")
        await asyncio.sleep(7.0) 
        
        logger.info("ZMQ_DEMO: Automated check-in messages should have been attempted.")

        # Optionally, send another explicit message if needed for further testing
        # logger.info("ZMQ_DEMO: Node A sending an explicit hello to Node B")
        # await node1_agent.send_hello_message(node2_swim_addr_str)
        # await asyncio.sleep(2.0)

        logger.info("ZMQ_DEMO: Waiting a bit longer for any final ACKs or processing...")
        await asyncio.sleep(5.0) 

        logger.info("ZMQ_DEMO: Final Results Check:")
        stats1 = node1_agent.get_integration_status()
        stats2 = node2_agent.get_integration_status()

        logger.info(f"ZMQ_DEMO: Node A ({node1_agent.node_name}) final stats: {stats1['message_stats']}")
        logger.info(f"ZMQ_DEMO: Node B ({node2_agent.node_name}) final stats: {stats2['message_stats']}")

        node1_rm_stats = stats1.get('component_status', {}).get('reliability', {})
        node2_rm_stats = stats2.get('component_status', {}).get('reliability', {})
        logger.info(f"ZMQ_DEMO: Node A ReliabilityManager pending messages: {node1_rm_stats.get('pending_messages_rm', 'N/A')}")
        logger.info(f"ZMQ_DEMO: Node B ReliabilityManager pending messages: {node2_rm_stats.get('pending_messages_rm', 'N/A')}")

    finally:
        logger.info("ZMQ_DEMO: Cleaning up")
        await node1_agent.stop()
        await node2_agent.stop()
        logger.info("ZMQ_DEMO: Demo complete")

if __name__ == "__main__":
    asyncio.run(demo_zmq_messaging())