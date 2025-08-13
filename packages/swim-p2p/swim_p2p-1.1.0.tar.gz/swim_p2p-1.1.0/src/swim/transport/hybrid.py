import logging
from typing import Tuple, Optional, Callable, Any, Dict, Union

from .base import Transport
from .udp import UDPTransport
from .tcp import TCPTransport

logger = logging.getLogger(__name__)

class HybridTransport(Transport):
    """
    Hybrid transport that dynamically selects between UDP and TCP based on message size.
    
    This implementation automatically chooses the appropriate transport protocol
    based on the size of the message being sent. Small messages use UDP for lower
    latency, while large messages use TCP for reliable delivery.
    """
    
    def __init__(
        self,
        udp_max_size: int = 1400,  # Conservative MTU to avoid fragmentation
        udp_buffer_size: int = 65536,
        tcp_buffer_size: int = 65536,
        tcp_max_connections: int = 100
    ):
        """Initialize a new hybrid transport.
        
        Args:
            udp_max_size: Maximum size for UDP messages before switching to TCP
            udp_buffer_size: Buffer size for UDP transport
            tcp_buffer_size: Buffer size for TCP transport
            tcp_max_connections: Maximum TCP connections
        """
        self.udp_max_size = udp_max_size
        self.udp_transport = UDPTransport(buffer_size=udp_buffer_size)
        self.tcp_transport = TCPTransport(
            buffer_size=tcp_buffer_size,
            max_connections=tcp_max_connections
        )
        
        # Common state
        self.local_address = None
        self.running = False
        self.receiver_callback = None
    
    async def bind(self, address: Tuple[str, int]) -> None:
        """Bind both transports to the same address.
        
        Args:
            address: (host, port) tuple to bind to
        """
        # Bind both transports
        await self.udp_transport.bind(address)
        await self.tcp_transport.bind(address)
        
        self.local_address = address
        logger.info(f"Hybrid transport bound to {address[0]}:{address[1]}")
    
    async def send(self, data: bytes, dest: Tuple[str, int]) -> None:
        if not self.local_address:
            raise RuntimeError("Transport not initialized. Call bind() first.")
        
        # Try to parse the message for better logging
        try:
            from swim.utils.serialization import deserialize_message
            msg = deserialize_message(data)
            msg_type = msg.get("type", "UNKNOWN")
            msg_id = msg.get("id", "unknown")
            
            # Log transport selection
            if len(data) <= self.udp_max_size:
                logger.info(f"[{msg_id}] HYBRID: Using UDP for {len(data)} byte {msg_type} message to {dest[0]}:{dest[1]}")
                try:
                    await self.udp_transport.send(data, dest)
                except Exception as e:
                    logger.warning(f"[{msg_id}] HYBRID: UDP send failed, falling back to TCP: {e}")
                    await self.tcp_transport.send(data, dest)
            else:
                logger.info(f"[{msg_id}] HYBRID: Using TCP for {len(data)} byte {msg_type} message to {dest[0]}:{dest[1]}")
                await self.tcp_transport.send(data, dest)
        except Exception as e:
            # If parsing fails, fall back to the original logic
            if len(data) <= self.udp_max_size:
                logger.debug(f"Using UDP to send {len(data)} bytes to {dest[0]}:{dest[1]}")
                try:
                    await self.udp_transport.send(data, dest)
                except Exception as e:
                    logger.warning(f"UDP send failed, falling back to TCP: {e}")
                    await self.tcp_transport.send(data, dest)
            else:
                logger.debug(f"Using TCP to send {len(data)} bytes to {dest[0]}:{dest[1]}")
                await self.tcp_transport.send(data, dest)
    
    async def receive(self, timeout: Optional[float] = None, msg_type: Optional[str] = None) -> Tuple[bytes, Tuple[str, int]]:
        """Receive data from either transport, whichever has data available first.
        
        Args:
            timeout: Max seconds to wait (None = wait forever)
            msg_type: Optional message type to listen for specifically
            
        Returns:
            Tuple of (data_bytes, sender_address)
            
        Raises:
            asyncio.TimeoutError: If the operation times out
        """
        if not self.local_address:
            raise RuntimeError("Transport not initialized. Call bind() first.")
        
        # Create tasks for both transports
        import asyncio
        udp_task = asyncio.create_task(self.udp_transport.receive(timeout, msg_type))
        tcp_task = asyncio.create_task(self.tcp_transport.receive(timeout, msg_type))
        
        # Wait for the first one to complete or both to fail
        done, pending = await asyncio.wait(
            [udp_task, tcp_task],
            return_when=asyncio.FIRST_COMPLETED,
            timeout=timeout
        )
        
        # Cancel the pending task
        for task in pending:
            task.cancel()
        
        # Check for timeout
        if not done:
            logger.debug("Receive timed out on both transports")
            raise asyncio.TimeoutError("Receive timed out")
        
        # Get result from completed task
        for task in done:
            try:
                result = task.result()
                protocol = "UDP" if task == udp_task else "TCP"
                logger.debug(f"Received data via {protocol} from {result[1][0]}:{result[1][1]}")
                return result
            except Exception as e:
                logger.debug(f"Task failed with: {e}")
        
        # If we get here, both tasks failed
        raise RuntimeError("Both UDP and TCP receive operations failed")
    
    async def start_receiver(self, callback: Callable[[bytes, Tuple[str, int]], Any]) -> None:
        """Start receiver on both transports.
        
        Args:
            callback: Function to call with (data, sender_address) on receipt
        """
        if self.running:
            return
        
        self.running = True
        self.receiver_callback = callback
        
        # Start receivers on both transports
        await self.udp_transport.start_receiver(callback)
        await self.tcp_transport.start_receiver(callback)
        
        logger.info("Hybrid transport receiver started on both UDP and TCP")
    
    async def close(self) -> None:
        """Close both transports."""
        self.running = False
        
        # Close both transports
        await self.udp_transport.close()
        await self.tcp_transport.close()
        
        self.receiver_callback = None
        logger.info("Hybrid transport closed")