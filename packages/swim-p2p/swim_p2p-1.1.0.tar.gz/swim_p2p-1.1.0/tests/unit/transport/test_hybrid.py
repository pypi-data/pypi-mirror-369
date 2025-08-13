import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from swim.transport.hybrid import HybridTransport
from swim.transport.base import Transport
from swim.transport.udp import UDPTransport
from swim.transport.tcp import TCPTransport

@pytest.fixture
def hybrid_transport():
    """Create a hybrid transport instance for testing."""
    return HybridTransport()

def test_hybrid_transport_implements_transport_interface(hybrid_transport):
    """Test that HybridTransport implements the Transport interface."""
    assert isinstance(hybrid_transport, Transport)

@pytest.mark.asyncio
async def test_bind():
    """Test that bind initializes both UDP and TCP transports."""
    # Create mocks for both transports
    with patch('swim.transport.udp.UDPTransport.bind', new_callable=AsyncMock) as mock_udp_bind, \
         patch('swim.transport.tcp.TCPTransport.bind', new_callable=AsyncMock) as mock_tcp_bind:
        
        # Create and bind the transport
        transport = HybridTransport()
        address = ("127.0.0.1", 12345)
        await transport.bind(address)
        
        # Check if both transport binds were called with the same address
        mock_udp_bind.assert_awaited_once_with(address)
        mock_tcp_bind.assert_awaited_once_with(address)
        
        # Check local address is set
        assert transport.local_address == address

@pytest.mark.asyncio
async def test_send_small_message_uses_udp():
    """Test that small messages are sent via UDP."""
    with patch('swim.transport.udp.UDPTransport.send', new_callable=AsyncMock) as mock_udp_send, \
         patch('swim.transport.tcp.TCPTransport.send', new_callable=AsyncMock) as mock_tcp_send:
        
        # Create transport
        transport = HybridTransport(udp_max_size=1000)
        transport.local_address = ("127.0.0.1", 12345)  # Set directly to avoid bind
        
        # Send a small message
        small_data = b"A" * 500  # 500 bytes, below threshold
        dest = ("127.0.0.1", 12346)
        await transport.send(small_data, dest)
        
        # Verify UDP was used
        mock_udp_send.assert_awaited_once_with(small_data, dest)
        mock_tcp_send.assert_not_awaited()

@pytest.mark.asyncio
async def test_send_large_message_uses_tcp():
    """Test that large messages are sent via TCP."""
    with patch('swim.transport.udp.UDPTransport.send', new_callable=AsyncMock) as mock_udp_send, \
         patch('swim.transport.tcp.TCPTransport.send', new_callable=AsyncMock) as mock_tcp_send:
        
        # Create transport
        transport = HybridTransport(udp_max_size=1000)
        transport.local_address = ("127.0.0.1", 12345)  # Set directly to avoid bind
        
        # Send a large message
        large_data = b"A" * 1500  # 1500 bytes, above threshold
        dest = ("127.0.0.1", 12346)
        await transport.send(large_data, dest)
        
        # Verify TCP was used
        mock_tcp_send.assert_awaited_once_with(large_data, dest)
        mock_udp_send.assert_not_awaited()

@pytest.mark.asyncio
async def test_send_udp_fallback_to_tcp():
    """Test that failures in UDP send fall back to TCP."""
    with patch('swim.transport.udp.UDPTransport.send', new_callable=AsyncMock) as mock_udp_send, \
         patch('swim.transport.tcp.TCPTransport.send', new_callable=AsyncMock) as mock_tcp_send:
        
        # Set UDP send to fail
        mock_udp_send.side_effect = Exception("UDP send failed")
        
        # Create transport
        transport = HybridTransport(udp_max_size=1000)
        transport.local_address = ("127.0.0.1", 12345)  # Set directly to avoid bind
        
        # Send a small message
        small_data = b"A" * 500  # 500 bytes, below threshold
        dest = ("127.0.0.1", 12346)
        await transport.send(small_data, dest)
        
        # Verify fallback occurred
        mock_udp_send.assert_awaited_once_with(small_data, dest)
        mock_tcp_send.assert_awaited_once_with(small_data, dest)

@pytest.mark.asyncio
async def test_receive_from_udp():
    """Test receiving data from UDP transport."""
    # Create mock data
    test_data = b"UDP test data"
    test_addr = ("127.0.0.1", 54321)
    
    # Create mock awaitable for UDP and TCP receive
    udp_future = asyncio.Future()
    udp_future.set_result((test_data, test_addr))
    
    tcp_future = asyncio.Future()
    # TCP future is not set - it will wait
    
    # Create transport with mocked UDP and TCP receive
    with patch('asyncio.create_task') as mock_create_task:
        mock_create_task.side_effect = [udp_future, tcp_future]
        
        transport = HybridTransport()
        transport.local_address = ("127.0.0.1", 12345)  # Set directly to avoid bind
        
        # Receive data
        result = await transport.receive()
        
        # Check result
        assert result == (test_data, test_addr)
        
        # TCP future should be cancelled
        await asyncio.sleep(0.1)  # Give cancellation time to propagate
        assert tcp_future.cancelled()

@pytest.mark.asyncio
async def test_receive_from_tcp():
    """Test receiving data from TCP transport when UDP has no data."""
    # Create mock data
    test_data = b"TCP test data"
    test_addr = ("127.0.0.1", 54321)
    
    # Create mock awaitable for UDP and TCP receive
    udp_future = asyncio.Future()
    # UDP future is not set - it will wait
    
    tcp_future = asyncio.Future()
    tcp_future.set_result((test_data, test_addr))
    
    # Create transport with mocked UDP and TCP receive
    with patch('asyncio.create_task') as mock_create_task:
        mock_create_task.side_effect = [udp_future, tcp_future]
        
        transport = HybridTransport()
        transport.local_address = ("127.0.0.1", 12345)  # Set directly to avoid bind
        
        # Receive data
        result = await transport.receive()
        
        # Check result
        assert result == (test_data, test_addr)
        
        # UDP future should be cancelled
        await asyncio.sleep(0.1)  # Give cancellation time to propagate
        assert udp_future.cancelled()

@pytest.mark.asyncio
async def test_receive_timeout():
    """Test that receive times out if both UDP and TCP time out."""
    # Create mock awaitable for UDP and TCP receive that never complete
    udp_future = asyncio.Future()
    tcp_future = asyncio.Future()
    
    # Create transport with mocked UDP and TCP receive
    with patch('asyncio.create_task') as mock_create_task, \
         patch('asyncio.wait', new_callable=AsyncMock) as mock_wait:
        
        mock_create_task.side_effect = [udp_future, tcp_future]
        mock_wait.return_value = (set(), {udp_future, tcp_future})  # No tasks done, both pending
        
        transport = HybridTransport()
        transport.local_address = ("127.0.0.1", 12345)  # Set directly to avoid bind
        
        # Receive should time out
        with pytest.raises(asyncio.TimeoutError):
            await transport.receive(timeout=0.1)

@pytest.mark.asyncio
async def test_start_receiver():
    """Test that start_receiver starts receivers on both transports."""
    with patch('swim.transport.udp.UDPTransport.start_receiver', new_callable=AsyncMock) as mock_udp_start, \
         patch('swim.transport.tcp.TCPTransport.start_receiver', new_callable=AsyncMock) as mock_tcp_start:
        
        # Create transport
        transport = HybridTransport()
        transport.local_address = ("127.0.0.1", 12345)  # Set directly to avoid bind
        
        # Create mock callback
        callback = MagicMock()
        
        # Start receiver
        await transport.start_receiver(callback)
        
        # Verify both receivers were started with the same callback
        mock_udp_start.assert_awaited_once_with(callback)
        mock_tcp_start.assert_awaited_once_with(callback)
        
        # Check that running flag is set
        assert transport.running is True
        assert transport.receiver_callback is callback

@pytest.mark.asyncio
async def test_close():
    """Test that close stops both transports."""
    with patch('swim.transport.udp.UDPTransport.close', new_callable=AsyncMock) as mock_udp_close, \
         patch('swim.transport.tcp.TCPTransport.close', new_callable=AsyncMock) as mock_tcp_close:
        
        # Create transport
        transport = HybridTransport()
        transport.local_address = ("127.0.0.1", 12345)  # Set directly to avoid bind
        transport.running = True
        transport.receiver_callback = MagicMock()
        
        # Close the transport
        await transport.close()
        
        # Verify both transports were closed
        mock_udp_close.assert_awaited_once()
        mock_tcp_close.assert_awaited_once()
        
        # Check flags were reset
        assert transport.running is False
        assert transport.receiver_callback is None

@pytest.mark.asyncio
async def test_send_without_bind_raises_error():
    """Test that send raises an error if bind has not been called."""
    transport = HybridTransport()
    
    with pytest.raises(RuntimeError):
        await transport.send(b"test", ("127.0.0.1", 12345))

@pytest.mark.asyncio
async def test_receive_without_bind_raises_error():
    """Test that receive raises an error if bind has not been called."""
    transport = HybridTransport()
    
    with pytest.raises(RuntimeError):
        await transport.receive()