import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from swim.transport.tcp import TCPTransport
from swim.transport.base import Transport

@pytest.fixture
def tcp_transport():
    """Create a TCP transport instance for testing."""
    return TCPTransport()

def test_tcp_transport_implements_transport_interface(tcp_transport):
    """Test that TCPTransport implements the Transport interface."""
    assert isinstance(tcp_transport, Transport)

@pytest.mark.asyncio
async def test_bind():
    """Test that bind initializes the server correctly."""
    # Mock the start_server function
    with patch('asyncio.start_server', new_callable=AsyncMock) as mock_start_server:
        # Set up the mock to return a server object
        mock_server = MagicMock()
        mock_server.close = MagicMock()
        mock_server.wait_closed = AsyncMock()
        mock_start_server.return_value = mock_server
        
        # Create and bind the transport
        transport = TCPTransport()
        address = ("127.0.0.1", 12345)
        await transport.bind(address)
        
        # Check if server was started with correct parameters
        mock_start_server.assert_called_once()
        call_args = mock_start_server.call_args[1]
        assert call_args['port'] == 12345
        assert call_args['host'] == '0.0.0.0'  # Should bind to all interfaces
        
        # Check local address is set
        assert transport.local_address == address
        
        # Close the transport
        await transport.close()
        
        # Check if server was closed
        mock_server.close.assert_called_once()
        mock_server.wait_closed.assert_awaited_once()

@pytest.mark.asyncio
async def test_send_receive():
    """Test sending and receiving data between two transports."""
    # This test requires two real TCP transports to communicate
    sender = TCPTransport()
    receiver = TCPTransport()
    
    # Bind to different ports
    await sender.bind(("127.0.0.1", 12346))
    await receiver.bind(("127.0.0.1", 12347))
    
    # Prepare test data
    test_data = b"Hello, SWIM via TCP!"
    received_data = None
    received_addr = None
    
    # Set up a future to wait for data
    received_future = asyncio.get_event_loop().create_future()
    
    async def on_data(data, addr):
        nonlocal received_data, received_addr
        received_data = data
        received_addr = addr
        received_future.set_result(True)
    
    # Start receiver
    await receiver.start_receiver(on_data)
    
    # Send data - give some time for the receiver to start
    await asyncio.sleep(0.1)  
    await sender.send(test_data, ("127.0.0.1", 12347))
    
    # Wait for data (with timeout)
    await asyncio.wait_for(received_future, timeout=2.0)
    
    # Verify the data
    assert received_data == test_data
    assert received_addr[0] == "127.0.0.1"
    
    # Clean up
    await sender.close()
    await receiver.close()

@pytest.mark.asyncio
async def test_receive_timeout():
    """Test that receive times out correctly."""
    transport = TCPTransport()
    await transport.bind(("127.0.0.1", 12348))
    
    with pytest.raises(asyncio.TimeoutError):
        await transport.receive(timeout=0.1)
    
    await transport.close()

@pytest.mark.asyncio
async def test_close_stops_receiver():
    """Test that close properly stops the receiver task."""
    transport = TCPTransport()
    await transport.bind(("127.0.0.1", 12349))
    
    callback_mock = MagicMock()
    await transport.start_receiver(callback_mock)
    
    assert transport.running is True
    assert transport.receiver_task is not None
    
    await transport.close()
    
    assert transport.running is False
    
    # Check that the receiver task was cancelled
    await asyncio.sleep(0.1)  # Give the cancellation time to propagate
    assert transport.receiver_task.cancelled() or transport.receiver_task.done()

@pytest.mark.asyncio
async def test_handle_client():
    """Test client handling functionality."""
    transport = TCPTransport()
    await transport.bind(("127.0.0.1", 12350))
    
    # Create mock reader and writer
    reader = AsyncMock()
    writer = MagicMock()
    
    # Set up the peername
    writer.get_extra_info.return_value = ("127.0.0.1", 54321)
    
    # Set up reader to return length and message
    message = b'{"type":"PING","from":"127.0.0.1:54321"}'
    length = len(message).to_bytes(4, byteorder='big')
    reader.readexactly.side_effect = [
        length,  # First call returns length
        message,  # Second call returns message
        asyncio.IncompleteReadError(b'', 4)  # Simulate client disconnect
    ]
    
    # Call the client handler directly
    handler_task = asyncio.create_task(transport._handle_client(reader, writer))
    
    # Wait a bit for handler to process the message
    await asyncio.sleep(0.1)
    
    # Try to receive the message
    try:
        data, addr = await transport.receive(timeout=0.1)
        assert data == message
        assert addr == ("127.0.0.1", 54321)
    except asyncio.TimeoutError:
        assert False, "Failed to receive message"
    
    # Cancel the handler task 
    handler_task.cancel()
    await transport.close()

@pytest.mark.asyncio
async def test_connection_pooling():
    """Test connection pooling when sending to the same destination multiple times."""
    with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_open_connection:
        # Set up the mock to return reader, writer
        reader = AsyncMock()
        writer = MagicMock()
        
        # IMPORTANT: Make drain an AsyncMock explicitly
        writer.drain = AsyncMock()
        
        writer.close = MagicMock()
        writer.wait_closed = AsyncMock()
        
        mock_open_connection.return_value = (reader, writer)
        
        # Create transport
        transport = TCPTransport()
        await transport.bind(("127.0.0.1", 12351))
        
        # Send to the same destination twice
        dest = ("127.0.0.1", 12352)
        await transport.send(b"Message 1", dest)
        await transport.send(b"Message 2", dest)
        
        # Should only open connection once
        assert mock_open_connection.call_count == 1
        assert len(transport._connections) == 1
        
        # Verify write was called twice (once for each message)
        assert writer.write.call_count == 2
        
        # Verify drain was called twice
        assert writer.drain.await_count == 2
        
        # Close the transport
        await transport.close()
        
        # All connections should be closed
        writer.close.assert_called_once()
        writer.wait_closed.assert_awaited_once()

@pytest.mark.asyncio
async def test_send_without_bind_raises_error():
    """Test that send raises an error if bind has not been called."""
    transport = TCPTransport()
    
    with pytest.raises(RuntimeError):
        await transport.send(b"test", ("127.0.0.1", 12345))

@pytest.mark.asyncio
async def test_receive_without_bind_raises_error():
    """Test that receive raises an error if bind has not been called."""
    transport = TCPTransport()
    
    with pytest.raises(RuntimeError):
        await transport.receive()