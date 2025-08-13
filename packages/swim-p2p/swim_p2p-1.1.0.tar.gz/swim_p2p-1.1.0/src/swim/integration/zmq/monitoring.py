"""
ZMQ socket monitoring for enhanced observability.

Integrates with ZMQ's built-in monitoring API to track socket events,
connection states, and potentially buffer utilization.
"""
import asyncio
import zmq
import zmq.asyncio
import logging
from typing import Optional, Callable, Any, Dict

logger = logging.getLogger(__name__)

# Mapping ZMQ event codes to human-readable names
ZMQ_EVENT_MAP = {
    zmq.EVENT_CONNECTED: "EVENT_CONNECTED",
    zmq.EVENT_CONNECT_DELAYED: "EVENT_CONNECT_DELAYED",
    zmq.EVENT_CONNECT_RETRIED: "EVENT_CONNECT_RETRIED",
    zmq.EVENT_LISTENING: "EVENT_LISTENING",
    zmq.EVENT_BIND_FAILED: "EVENT_BIND_FAILED",
    zmq.EVENT_ACCEPTED: "EVENT_ACCEPTED",
    zmq.EVENT_ACCEPT_FAILED: "EVENT_ACCEPT_FAILED",
    zmq.EVENT_CLOSED: "EVENT_CLOSED",
    zmq.EVENT_CLOSE_FAILED: "EVENT_CLOSE_FAILED",
    zmq.EVENT_DISCONNECTED: "EVENT_DISCONNECTED",
    zmq.EVENT_MONITOR_STOPPED: "EVENT_MONITOR_STOPPED",
    zmq.EVENT_HANDSHAKE_FAILED_NO_DETAIL: "EVENT_HANDSHAKE_FAILED_NO_DETAIL",
    zmq.EVENT_HANDSHAKE_SUCCEEDED: "EVENT_HANDSHAKE_SUCCEEDED",
    zmq.EVENT_HANDSHAKE_FAILED_PROTOCOL: "EVENT_HANDSHAKE_FAILED_PROTOCOL",
    zmq.EVENT_HANDSHAKE_FAILED_AUTH: "EVENT_HANDSHAKE_FAILED_AUTH",
    # Note: ZMQ_EVENT_SENT is not directly available on all socket types via monitor.
    # It's typically used with zmq_socket_monitor_versioned.
    # For simplicity here, we'll focus on connection events.
    # ZMQ_EVENT_SENT could be simulated or handled by the sending logic itself.
}
if hasattr(zmq, 'EVENT_ALL'): # zmq.EVENT_ALL might not be in all pyzmq versions
    ZMQ_EVENT_MAP[zmq.EVENT_ALL] = "EVENT_ALL"


class ZMQMonitor:
    """
    Monitors a ZMQ socket for events.
    """
    def __init__(self,
                 monitored_socket_name: str,
                 on_event_callback: Optional[Callable[[str, int, str, str], None]] = None,
                 metrics_collector: Optional[Any] = None): # Type hint for MetricsCollector
        """
        Initialize the ZMQMonitor.

        Args:
            monitored_socket_name: A descriptive name for the socket being monitored (e.g., "DealerSocket-PeerX").
            on_event_callback: Optional callback for all ZMQ events.
                               Args: (socket_name, event_code, event_name, event_address)
            metrics_collector: Optional MetricsCollector instance.
        """
        self.monitored_socket_name = monitored_socket_name
        self._monitor_socket: Optional[zmq.asyncio.Socket] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._running = False
        self.on_event_callback = on_event_callback
        self.metrics_collector = metrics_collector

        self._event_handlers: Dict[int, Callable[[str, str], None]] = {
            zmq.EVENT_CONNECTED: self._on_connected,
            zmq.EVENT_DISCONNECTED: self._on_disconnected,
            zmq.EVENT_ACCEPTED: self._on_accepted,
            zmq.EVENT_CLOSED: self._on_closed,
            zmq.EVENT_BIND_FAILED: self._on_bind_failed,
            # Add more specific handlers as needed
        }
        logger.info(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Initialized.")

    async def attach(self, socket_to_monitor: zmq.asyncio.Socket) -> None:
        """
        Attaches the monitor to a ZMQ socket.

        Args:
            socket_to_monitor: The ZMQ socket (zmq.asyncio.Socket) to monitor.
        """
        if self._running:
            logger.warning(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Already attached and running.")
            return

        try:
            # The monitor endpoint must be inproc
            monitor_endpoint = f"inproc://monitor.{self.monitored_socket_name}-{id(socket_to_monitor)}"
            socket_to_monitor.monitor(monitor_endpoint, zmq.EVENT_ALL) # type: ignore

            self._monitor_socket = zmq.asyncio.Context.instance().socket(zmq.PAIR)
            self._monitor_socket.connect(monitor_endpoint) # type: ignore
            self._running = True
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Attached to socket. Monitoring endpoint: {monitor_endpoint}")
        except zmq.ZMQError as e:
            logger.error(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Failed to attach monitor: {e}")
            self._running = False
            if self._monitor_socket:
                self._monitor_socket.close()
                self._monitor_socket = None

    async def _monitor_loop(self) -> None:
        """Continuously receives and processes monitor events."""
        logger.info(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Starting monitor loop.")
        while self._running and self._monitor_socket:
            try:
                event_data = await self._monitor_socket.recv_multipart()
                # ZMQ monitor events are versioned; version 2 is {event: int, value: int, endpoint: str}
                # For simplicity, assuming event_data is typically [event_struct, endpoint_bytes]
                # or using recv_event for newer pyzmq
                if hasattr(self._monitor_socket, 'recv_event'):
                     # Modern pyzmq
                    event = await self._monitor_socket.recv_event(flags=zmq.NOBLOCK) # type: ignore
                    event_code = event.event
                    event_address = event.addr
                    # event_value = event.value (e.g. fd for connect/accept, errno for bind_failed)
                else:
                    # Older pyzmq, manual parsing (might be less reliable)
                    # This part is tricky as event structure can vary.
                    # A common structure for connection events is [event_code_bytes (2), value_bytes (4), address_bytes]
                    # For now, we'll just log the raw event.
                    # A more robust solution would use zmq_socket_monitor_versioned and parse correctly.
                    # Focusing on just logging the event name and address if possible.
                    # Typically, the first frame might describe the event, and the second the address.
                    # This is a simplification. Real parsing needs to check zmq_socket_monitor() docs.
                    if len(event_data) >= 1:
                        # This is a placeholder. Actual event parsing is complex.
                        # For now, we'll assume the event_code is somehow derivable or we log raw.
                        # Let's assume event is in the first part of the first frame.
                        # This requires more specific knowledge of the ZMQ event structure.
                        # For now, let's just get a generic code.
                        try:
                            # A common format is a struct in the first frame
                            # Example: struct.unpack_from('<Hi', event_data[0]) for event and value
                            # We'll use a simpler interpretation for this example.
                            event_code = int.from_bytes(event_data[0][:2], 'little') if len(event_data[0]) >=2 else -1
                            event_address = event_data[1].decode('utf-8') if len(event_data) > 1 else "N/A"
                        except Exception:
                            event_code = -1 # Unknown
                            event_address = "ParseError"


                event_name = ZMQ_EVENT_MAP.get(event_code, f"UNKNOWN_EVENT_{event_code}")

                logger.info(f"ZMQ_MONITOR_EVENT [{self.monitored_socket_name}]: Code: {event_code}, Name: {event_name}, Address: {event_address}")

                if self.metrics_collector:
                    self.metrics_collector.record_event(
                        "zmq_monitor_event",
                        value=event_name,
                        labels={"socket_name": self.monitored_socket_name, "address": event_address}
                    )

                if self.on_event_callback:
                    self.on_event_callback(self.monitored_socket_name, event_code, event_name, event_address)

                if event_code in self._event_handlers:
                    self._event_handlers[event_code](event_name, event_address)

                if event_code == zmq.EVENT_MONITOR_STOPPED:
                    logger.info(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Monitor loop stopped by ZMQ_EVENT_MONITOR_STOPPED.")
                    self._running = False
                    break
            except zmq.Again: # Expected if using NOBLOCK and no event
                await asyncio.sleep(0.01) # Don't busy-loop
            except asyncio.CancelledError:
                logger.info(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Monitor loop cancelled.")
                self._running = False
                break
            except Exception as e:
                logger.error(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Error in monitor loop: {e}")
                # Potentially stop if errors persist, or add a backoff
                await asyncio.sleep(1) # Avoid tight loop on error

        logger.info(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Monitor loop exited.")
        if self._monitor_socket:
            self._monitor_socket.close()
            self._monitor_socket = None

    async def detach(self) -> None:
        """Detaches the monitor and stops monitoring."""
        logger.info(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Detaching monitor...")
        self._running = False
        if self._monitor_task:
            if not self._monitor_task.done():
                self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass # Expected
            self._monitor_task = None
        # Note: The monitored socket itself should call unmonitor() if desired.
        # This class only closes its own PAIR socket for receiving monitor events.
        if self._monitor_socket:
             self._monitor_socket.close(linger=0) # Close immediately
             self._monitor_socket = None
        logger.info(f"ZMQ_MONITOR [{self.monitored_socket_name}]: Monitor detached.")

    # --- Specific Event Handlers (can be expanded) ---
    def _on_connected(self, event_name: str, address: str):
        logger.info(f"ZMQ_CONNECTED [{self.monitored_socket_name}]: Connected to {address}.")
        # Potentially update CircuitBreaker or ReliabilityManager

    def _on_disconnected(self, event_name: str, address: str):
        logger.warning(f"ZMQ_DISCONNECTED [{self.monitored_socket_name}]: Disconnected from {address}.")
        # Potentially update CircuitBreaker or ReliabilityManager

    def _on_accepted(self, event_name: str, address: str):
        logger.info(f"ZMQ_ACCEPTED [{self.monitored_socket_name}]: Accepted connection from {address}.")

    def _on_closed(self, event_name: str, address: str):
        logger.info(f"ZMQ_CLOSED [{self.monitored_socket_name}]: Connection closed for {address}.")

    def _on_bind_failed(self, event_name: str, address: str):
        logger.error(f"ZMQ_BIND_FAILED [{self.monitored_socket_name}]: Bind failed for {address}.")


# Example usage (conceptual, would be integrated into ZMQ node setup)
async def example_zmq_monitoring():
    ctx = zmq.asyncio.Context()
    socket_to_monitor = ctx.socket(zmq.DEALER) # Example socket
    socket_name = "MyDealerSocket"

    # Create a monitor instance
    monitor = ZMQMonitor(socket_name)
    await monitor.attach(socket_to_monitor)

    # ... socket operations ...
    try:
        socket_to_monitor.connect("tcp://localhost:5555") # Trigger some events
        await asyncio.sleep(2)
        socket_to_monitor.disconnect("tcp://localhost:5555")
        await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Example error: {e}")
    finally:
        await monitor.detach()
        socket_to_monitor.close()
        # ctx.term() # If this is the end of ZMQ usage