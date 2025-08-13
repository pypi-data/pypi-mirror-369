import asyncio
import pytest
import socket
from unittest.mock import patch, MagicMock

from swim.transport.udp import UDPTransport
from swim.transport.base import Transport

@pytest.fixture
def udp_transport():
    """Create a UDP transport instance for testing."""
    return UDPTransport()

# checks if UDPTransport is an instance of the Transport abstract base class
def test_udp_transport_implements_transport_interface(udp_transport):
    """Test that UDPTransport implements the Transport interface."""
    assert isinstance(udp_transport, Transport)


@pytest.mark.asyncio
async def test_bind():
    """Test that bind initializes the transport correctly."""
    transport = UDPTransport()
    
    address = ("127.0.0.1", 12345)
    await transport.bind(address)
    
    assert transport.local_address == address
    assert transport.transport is not None
    assert transport.protocol is not None
    
    await transport.close()

# Try sending data between two transports
@pytest.mark.asyncio
async def test_send_receive():
    """Test sending and receiving data between two transports."""
    sender = UDPTransport()
    receiver = UDPTransport()
    
    # Bind to different ports
    await sender.bind(("127.0.0.1", 12345))
    await receiver.bind(("127.0.0.1", 12346))
    
    # Prepare test data
    test_data = b"Hello, SWIM!"
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
    
    # Send data
    await sender.send(test_data, ("127.0.0.1", 12346))
    
    # Wait for data (with timeout)
    await asyncio.wait_for(received_future, timeout=1.0)
    
    # Verify the data
    assert received_data == test_data
    assert received_addr[0] == "127.0.0.1"
    assert received_addr[1] == 12345
    
    # Clean up
    await sender.close()
    await receiver.close()

# Tests timeout after a certain period
@pytest.mark.asyncio
async def test_receive_timeout():
    """Test that receive times out correctly."""
    transport = UDPTransport()
    await transport.bind(("127.0.0.1", 12347))
    
    with pytest.raises(asyncio.TimeoutError):
        await transport.receive(timeout=0.1)
    
    await transport.close()

@pytest.mark.asyncio
async def test_close_stops_receiver():
    """Test that close properly stops the receiver task."""
    transport = UDPTransport()
    await transport.bind(("127.0.0.1", 12348))
    
    callback_mock = MagicMock()
    await transport.start_receiver(callback_mock)
    
    assert transport.running is True
    assert transport.receiver_task is not None
    
    await transport.close()
    
    assert transport.running is False
    assert transport.transport is None
    
    # Verify the task was cancelled
    with pytest.raises(asyncio.CancelledError):
        if transport.receiver_task and transport.receiver_task.cancelled():
            await transport.receiver_task

# Trying to send without binding a port raises an error
@pytest.mark.asyncio
async def test_send_without_bind_raises_error():
    """Test that send raises an error if bind has not been called."""
    transport = UDPTransport()
    
    with pytest.raises(RuntimeError):
        await transport.send(b"test", ("127.0.0.1", 12345))

# Recieving without binding a port raises an error
@pytest.mark.asyncio
async def test_receive_without_bind_raises_error():
    """Test that receive raises an error if bind has not been called."""
    transport = UDPTransport()
    
    with pytest.raises(RuntimeError):
        await transport.receive()