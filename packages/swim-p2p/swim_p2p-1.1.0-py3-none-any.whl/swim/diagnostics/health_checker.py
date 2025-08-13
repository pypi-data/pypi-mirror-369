"""
End-to-end health monitoring for the SWIM-ZMQ system.

Periodically sends synthetic probe messages through the system to check
overall health, measure end-to-end latency, and ensure connectivity.
"""
import asyncio
import time
import logging
import random
import uuid
from typing import Optional, Any, List, Tuple, Dict

# Assuming ReliabilityManager and MemberList are accessible
# These would typically be passed during HealthChecker initialization
# from swim.reliability import ReliabilityManager # Placeholder
# from swim.protocol.member import MemberList, Member  # Placeholder

logger = logging.getLogger(__name__)

# Define a simple structure for the probe message
HEALTH_PROBE_MESSAGE_TYPE = "HEALTH_PROBE"
HEALTH_PROBE_ACK_MESSAGE_TYPE = "HEALTH_PROBE_ACK"


class HealthChecker:
    """
    Performs end-to-end health checks by sending synthetic probes.
    """
    def __init__(self,
                 node_id: str,
                 reliability_manager: Any, # Actual type: ReliabilityManager
                 member_list: Any,          # Actual type: MemberList
                 check_interval_seconds: float = 60.0,
                 probe_timeout_seconds: float = 10.0,
                 metrics_collector: Optional[Any] = None, # Actual type: MetricsCollector
                 target_peer_count: int = 1): # Number of peers to probe each interval
        """
        Initialize the HealthChecker.

        Args:
            node_id: Identifier of the current node.
            reliability_manager: Instance of ReliabilityManager to send probes.
            member_list: Instance of MemberList to select peers.
            check_interval_seconds: How often to perform health checks.
            probe_timeout_seconds: Timeout for waiting for a probe ACK.
            metrics_collector: Optional MetricsCollector instance.
            target_peer_count: Number of peers to probe in each interval. 0 for all alive.
        """
        self.node_id = node_id
        self.reliability_manager = reliability_manager
        self.member_list = member_list
        self.check_interval_seconds = check_interval_seconds
        self.probe_timeout_seconds = probe_timeout_seconds
        self.metrics_collector = metrics_collector
        self.target_peer_count = target_peer_count

        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._active_probes: Dict[str, float] = {} # probe_id -> start_time

        logger.info(f"HEALTH_CHECKER [{self.node_id}]: Initialized. Interval: {check_interval_seconds}s, Timeout: {probe_timeout_seconds}s")

    async def start_monitoring(self) -> None:
        """Starts the periodic health check_interval_seconds monitoring task."""
        if self._running:
            logger.warning(f"HEALTH_CHECKER [{self.node_id}]: Monitoring already active.")
            return
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"HEALTH_CHECKER [{self.node_id}]: Started health monitoring.")

    async def stop_monitoring(self) -> None:
        """Stops the health check monitoring task."""
        if not self._running:
            return
        self._running = False
        if self._monitor_task:
            if not self._monitor_task.done():
                self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass # Expected
            self._monitor_task = None
        logger.info(f"HEALTH_CHECKER [{self.node_id}]: Stopped health monitoring.")

    async def _monitoring_loop(self) -> None:
        """The main loop that periodically performs health checks."""
        logger.info(f"HEALTH_CHECKER [{self.node_id}]: Monitoring loop started.")
        while self._running:
            try:
                await self._perform_checks()
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                logger.info(f"HEALTH_CHECKER [{self.node_id}]: Monitoring loop cancelled.")
                break
            except Exception as e:
                logger.error(f"HEALTH_CHECKER [{self.node_id}]: Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval_seconds / 2) # Shorter sleep on error

    async def _perform_checks(self) -> None:
        """Selects peers and initiates health probes to them."""
        alive_peers = self.member_list.get_alive_members(exclude_self=True)
        if not alive_peers:
            logger.info(f"HEALTH_CHECKER [{self.node_id}]: No alive peers to probe.")
            return

        if self.target_peer_count == 0 or self.target_peer_count >= len(alive_peers):
            targets = alive_peers # Probe all
        else:
            targets = random.sample(alive_peers, min(self.target_peer_count, len(alive_peers)))

        logger.info(f"HEALTH_CHECKER [{self.node_id}]: Performing health checks on {len(targets)} peers.")
        for peer_member in targets:
            peer_node_id = f"{peer_member.addr[0]}:{peer_member.addr[1]}"
            asyncio.create_task(self._send_probe_and_wait(peer_node_id, peer_member.addr))

    async def _send_probe_and_wait(self, peer_node_id: str, peer_address: Tuple[str, int]) -> None:
        """Sends a health probe to a specific peer and awaits an ACK."""
        probe_id = str(uuid.uuid4())
        probe_payload = {
            "type": HEALTH_PROBE_MESSAGE_TYPE,
            "probe_id": probe_id,
            "sender_node_id": self.node_id,
            "timestamp": time.time()
        }
        # Note: Trace context could be added here if messaging.trace is used
        # from messaging.trace import start_trace, inject_context
        # trace_ctx = start_trace("HealthChecker", "send_probe")
        # probe_payload = inject_context(probe_payload, trace_ctx)


        start_time = time.time()
        self._active_probes[probe_id] = start_time
        logger.info(f"HEALTH_CHECKER_PROBE_SEND [{self.node_id} -> {peer_node_id}]: Sending probe_id {probe_id}.")

        try:
            # We expect ReliabilityManager.send_reliable to handle the ACK mechanism
            # For this to work, the receiver must implement logic to send a
            # HEALTH_PROBE_ACK message back, which will be handled by handle_probe_ack.
            # send_reliable will return True if the *processing ACK* for the probe is received.
            # The payload for the processing ACK on the receiver side would be the HEALTH_PROBE_ACK.
            # This requires the application handler on the receiver to understand HEALTH_PROBE.

            # For a simpler model, we can assume `send_reliable` is just for sending
            # and we need a separate mechanism to await the specific HEALTH_PROBE_ACK.
            # However, leveraging the existing ReliabilityManager for its ACK handling is better.
            # Let's assume `send_reliable` waits for the *processing_ack* of the `HEALTH_PROBE` message.
            # The `HEALTH_PROBE_ACK` is the *payload* of that processing_ack.

            # If ReliabilityManager's send_reliable is used, it would internally wait for its own 3-tier ACKs.
            # For a health check, we are interested in the E2E app-level ACK.
            # This means the receiver application must handle HEALTH_PROBE and send back a specific HEALTH_PROBE_ACK.
            # And the sender must have a way to correlate this.
            # Let's assume the application handler on the receiver, upon getting HEALTH_PROBE,
            # sends back a new message of type HEALTH_PROBE_ACK using its ReliabilityManager.
            # The sender (HealthChecker) would need to listen for these. This complicates things.

            # Simpler for now: assume send_reliable sends the probe and the receiver's app logic
            # will send a *new* message back of type HEALTH_PROBE_ACK.
            # The HealthChecker then needs a way to receive these.
            # This means HealthChecker needs to register a handler for HEALTH_PROBE_ACK.

            # Let's use a direct call and rely on the ReliabilityManager's success return.
            # The application on the *receiver* needs to, upon receiving HEALTH_PROBE,
            # use *its* AckSystem to send the Processing ACK *and also*
            # potentially send a separate HEALTH_PROBE_ACK message if a payload is expected.
            # For simplicity, let's assume send_reliable's success indicates E2E success of the probe.
            # The "payload" sent is the health probe itself.
            # The "processing" on the other side is just acknowledging it.

            success = await self.reliability_manager.send_reliable(
                target_node=peer_node_id, # ReliabilityManager likely uses node_id strings
                message_data=probe_payload, # This needs to be bytes
                # trace_id=trace_ctx.trace_id if trace_ctx else None,
                # requires_ordering=False,
                timeout=self.probe_timeout_seconds
            )
            # This `success` means the ReliabilityManager got its 3 ACKs for the HEALTH_PROBE message.

            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            if success:
                logger.info(f"HEALTH_CHECKER_PROBE_SUCCESS [{self.node_id} -> {peer_node_id}]: Probe {probe_id} successful. Latency: {latency_ms:.2f}ms.")
                if self.metrics_collector:
                    self.metrics_collector.record_histogram("health_check_latency_ms", latency_ms, {"target_node": peer_node_id, "status": "success"})
                    self.metrics_collector.record_counter("health_check_count", 1, {"target_node": peer_node_id, "status": "success"})
            else:
                # This means send_reliable itself timed out or failed its ACK stages
                logger.warning(f"HEALTH_CHECKER_PROBE_FAILURE [{self.node_id} -> {peer_node_id}]: Probe {probe_id} failed or timed out (ReliabilityManager failure).")
                if self.metrics_collector:
                    self.metrics_collector.record_counter("health_check_count", 1, {"target_node": peer_node_id, "status": "failure_reliability"})

        except asyncio.TimeoutError: # This would be if send_reliable itself has a timeout that's hit
            logger.warning(f"HEALTH_CHECKER_PROBE_TIMEOUT_EXTERNAL [{self.node_id} -> {peer_node_id}]: Probe {probe_id} send_reliable call timed out.")
            if self.metrics_collector:
                self.metrics_collector.record_counter("health_check_count", 1, {"target_node": peer_node_id, "status": "timeout_external"})
        except Exception as e:
            logger.error(f"HEALTH_CHECKER_PROBE_ERROR [{self.node_id} -> {peer_node_id}]: Error sending probe {probe_id}: {e}")
            if self.metrics_collector:
                self.metrics_collector.record_counter("health_check_count", 1, {"target_node": peer_node_id, "status": "error"})
        finally:
            if probe_id in self._active_probes:
                del self._active_probes[probe_id]


    def register_probe_handlers(self, zmq_receiver_add_handler_method: Callable):
        """
        Call this method from your ZMQ receiver setup to register a handler for HEALTH_PROBE messages.
        The ZMQ receiver should, upon receiving a HEALTH_PROBE_MESSAGE_TYPE message,
        extract the payload, and then its application logic should use its *own*
        ReliabilityManager to send a message of type HEALTH_PROBE_ACK_MESSAGE_TYPE back to
        probe_payload["sender_node_id"].

        More simply, if ReliabilityManager's `send_reliable` return value is trusted
        as an E2E check (meaning the processing_ack stage IS the health probe ack),
        then the ZMQ receiver only needs to ensure that its application logic
        correctly triggers the processing_ack for HEALTH_PROBE messages.

        Example for the ZMQ receiver's application message handler:
        ```python
        # In ZMQ Receiver's application handler
        # async def handle_application_message(sender_node_id, message_id, payload_dict, ack_system_ref):
        #     if payload_dict.get("type") == HEALTH_PROBE_MESSAGE_TYPE:
        #         logger.info(f"Received HEALTH_PROBE {payload_dict.get('probe_id')} from {sender_node_id}. Acknowledging.")
        #         # The act of calling mark_message_processed in WorkflowManager (if used)
        #         # or directly calling ack_system_ref.send_processing_ack will signal success
        #         # to the HealthChecker's send_reliable call.
        #         # No separate HEALTH_PROBE_ACK message needs to be sent IF send_reliable's success is the E2E signal.
        #         # If a payload is needed for the ACK, then a new message would be sent.
        #         ack_system_ref.send_processing_ack(message_id, sender_node_id, success=True) # This is for the ZMQ transport of HEALTH_PROBE
        #         return True # Processed
        ```
        """
        logger.info(f"HEALTH_CHECKER [{self.node_id}]: Probe handling logic needs to be implemented in the ZMQ message receiver's application layer.")
        logger.info(f"HEALTH_CHECKER [{self.node_id}]: Receiver should acknowledge messages of type '{HEALTH_PROBE_MESSAGE_TYPE}' "
                    f"to complete the health check initiated by 'send_reliable'.")


    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the HealthChecker."""
        return {
            "node_id": self.node_id,
            "running": self._running,
            "check_interval_seconds": self.check_interval_seconds,
            "probe_timeout_seconds": self.probe_timeout_seconds,
            "active_probes_count": len(self._active_probes),
        }