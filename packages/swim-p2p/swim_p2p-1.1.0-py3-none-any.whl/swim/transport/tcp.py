import socket
import asyncio
import logging
from typing import Tuple, Optional, Callable, Any, Dict, Set

from .base import Transport

logger = logging.getLogger(__name__)

class TCPTransport(Transport):
    """TCP implementation of the Transport interface using asyncio."""
    
    def __init__(self, buffer_size: int = 65536, max_connections: int = 100):
        """Initialize a new TCP transport.
        
        Args:
            buffer_size: Maximum size of TCP receive buffer
            max_connections: Maximum number of concurrent connections
        """
        self.buffer_size = buffer_size
        self.max_connections = max_connections
        self.server = None
        self.local_address = None
        self.receive_queue = asyncio.Queue()
        self.running = False
        self.receiver_task = None
        
        # Keep track of active connections
        self._connections: Dict[Tuple[str, int], asyncio.StreamWriter] = {}
        self._connection_lock = asyncio.Lock()
        
        # Create separate response queues for different message types
        self._response_queues: Dict[str, asyncio.Queue] = {}
    
    async def bind(self, address: Tuple[str, int]) -> None:
        """Bind to a local address asynchronously.
        
        Args:
            address: (host, port) tuple to bind to
        """
        self.local_address = address
        
        # Start server
        self.server = await asyncio.start_server(
            self._handle_client,
            host='0.0.0.0',  # Listen on all interfaces
            port=address[1],
            limit=self.buffer_size,
            backlog=self.max_connections,
        )
        
        logger.info(f"TCP transport bound to all interfaces (0.0.0.0:{address[1]}), "
                   f"identifying as {address[0]}:{address[1]}")
        
        # Create specific response queues for different message types
        for msg_type in ["PONG", "PING-REQ-ACK", "HEARTBEAT"]:
            self._response_queues[msg_type] = asyncio.Queue()
            logger.debug(f"Created message queue for {msg_type} messages")
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle a client connection.
        
        Args:
            reader: StreamReader for receiving data
            writer: StreamWriter for sending data
        """
        peer_addr = writer.get_extra_info('peername')
        
        logger.debug(f"New TCP connection from {peer_addr[0]}:{peer_addr[1]}")
        
        try:
            while True:
                # Read the message length (4 bytes, big-endian)
                length_bytes = await reader.readexactly(4)
                message_length = int.from_bytes(length_bytes, byteorder='big')
                
                # Read the message data
                data = await reader.readexactly(message_length)
                
                try:
                    # Try to parse the message to determine its type
                    from swim.utils.serialization import deserialize_message
                    msg = deserialize_message(data)
                    
                    # Check if it's a response to a specific message type
                    msg_type = msg.get("type", "UNKNOWN")
                    msg_id = msg.get("id", "unknown")
                    
                    # Log message details
                    addr_str = f"{peer_addr[0]}:{peer_addr[1]}"
                    logger.debug(f"[{msg_id}] RECEIVED {len(data)} bytes from {addr_str}, type={msg_type}")
                    
                    # Put the message in the general queue
                    self.receive_queue.put_nowait((data, peer_addr))
                    
                    # If it's a specific type we're interested in, also put it in the 
                    # type-specific queue to avoid mixing messages
                    if msg_type in self._response_queues:
                        self._response_queues[msg_type].put_nowait((data, peer_addr))
                        logger.debug(f"[{msg_id}] Added {msg_type} to type-specific queue")
                        
                except Exception as e:
                    # If we can't parse, just put it in the general queue
                    logger.debug(f"Error parsing message: {e}, adding to general queue")
                    self.receive_queue.put_nowait((data, peer_addr))
                
        except asyncio.IncompleteReadError:
            # Client disconnected
            logger.debug(f"TCP connection closed by {peer_addr[0]}:{peer_addr[1]}")
        except Exception as e:
            logger.error(f"Error handling TCP client {peer_addr[0]}:{peer_addr[1]}: {e}")
        finally:
            # Remove from connections if present
            async with self._connection_lock:
                if peer_addr in self._connections:
                    del self._connections[peer_addr]
            
            # Close the connection
            writer.close()
            await writer.wait_closed()
    
    async def send(self, data: bytes, dest: Tuple[str, int]) -> None:
        """Send data to a destination asynchronously.
        
        Args:
            data: Bytes to send
            dest: (host, port) destination
        """
        if not self.local_address:
            raise RuntimeError("Transport not initialized. Call bind() first.")
        
        try:
            # Check if we already have a connection to this destination
            writer = await self._get_connection(dest)
            
            # Add length prefix to the message (4 bytes, big-endian)
            length_prefix = len(data).to_bytes(4, byteorder='big')
            
            # Send the length-prefixed message
            writer.write(length_prefix + data)
            await writer.drain()
            
            # Try to extract message ID and type for better logging
            try:
                from swim.utils.serialization import deserialize_message
                msg = deserialize_message(data)
                msg_type = msg.get("type", "UNKNOWN")
                msg_id = msg.get("id", "unknown")
                logger.debug(f"[{msg_id}] SENT {len(data)} bytes to {dest[0]}:{dest[1]}, type={msg_type}")
            except:
                logger.debug(f"SENT {len(data)} bytes to {dest[0]}:{dest[1]}")
                
        except ConnectionRefusedError:
            logger.error(f"Connection refused to {dest[0]}:{dest[1]}")
            # Remove failed connection
            async with self._connection_lock:
                if dest in self._connections:
                    self._connections[dest].close()
                    del self._connections[dest]
            raise
        except Exception as e:
            logger.error(f"Failed to send data to {dest}: {e}")
            raise
    
    async def _get_connection(self, dest: Tuple[str, int]) -> asyncio.StreamWriter:
        """Get or create a connection to the destination.
        
        Args:
            dest: (host, port) destination
            
        Returns:
            StreamWriter for the connection
        """
        async with self._connection_lock:
            if dest in self._connections:
                # Use existing connection
                return self._connections[dest]
            
            # Create new connection
            try:
                reader, writer = await asyncio.open_connection(dest[0], dest[1])
                self._connections[dest] = writer
                return writer
            except Exception as e:
                logger.error(f"Failed to establish connection to {dest[0]}:{dest[1]}: {e}")
                raise
    
    async def receive(self, timeout: Optional[float] = None, msg_type: Optional[str] = None) -> Tuple[bytes, Tuple[str, int]]:
        """Receive data from the socket asynchronously.
        
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
        
        try:
            # Use the type-specific queue if requested and available
            queue = self._response_queues.get(msg_type, self.receive_queue) if msg_type else self.receive_queue
            
            if msg_type:
                logger.debug(f"Waiting for specific message type: {msg_type} with timeout {timeout}s")
            
            if timeout is not None:
                # Use asyncio timeout
                start_time = asyncio.get_event_loop().time()
                result = await asyncio.wait_for(queue.get(), timeout)
                elapsed = asyncio.get_event_loop().time() - start_time
                
                # Try to extract message details for better logging
                try:
                    from swim.utils.serialization import deserialize_message
                    data, addr = result
                    msg = deserialize_message(data)
                    msg_id = msg.get("id", "unknown")
                    logger.debug(f"[{msg_id}] Received response after {elapsed:.4f}s "
                               f"from {addr[0]}:{addr[1]}, type={msg.get('type', 'UNKNOWN')}")
                except:
                    pass
                
                return result
            else:
                # Wait indefinitely
                return await queue.get()
        except asyncio.TimeoutError:
            logger.debug(f"Socket receive timed out{f' for {msg_type}' if msg_type else ''}")
            raise
    
    async def start_receiver(self, callback: Callable[[bytes, Tuple[str, int]], Any]) -> None:
        """Start an async task to process received messages.
        
        Args:
            callback: Function to call with (data, sender_address) on receipt
        """
        if self.running:
            return
        
        self.running = True
        
        async def receiver_loop():
            while self.running:
                try:
                    data, addr = await self.receive()
                    # Execute callback - if it's a coroutine, await it
                    result = callback(data, addr)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    if self.running:  # Only log if we're supposed to be running
                        logger.error(f"Error in receiver loop: {e}")
        
        self.receiver_task = asyncio.create_task(receiver_loop())
        logger.info("TCP receiver task started")
    
    async def close(self) -> None:
        """Close the transport and stop the receiver task."""
        self.running = False
        
        if self.receiver_task:
            try:
                self.receiver_task.cancel()
                await asyncio.gather(self.receiver_task, return_exceptions=True)
            except:
                pass
        
        # Close all connections
        async with self._connection_lock:
            for writer in self._connections.values():
                writer.close()
                try:
                    await writer.wait_closed()
                except:
                    pass
            self._connections.clear()
        
        # Close server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        
        logger.info("TCP transport closed")