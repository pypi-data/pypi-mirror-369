"""
Integration test for transport fallback in hybrid transport.
"""

import pytest
import asyncio
import os
import time
import logging
from typing import Tuple, List

from swim.transport.udp import UDPTransport
from swim.transport.tcp import TCPTransport
from swim.transport.hybrid import HybridTransport

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_transport_fallback_large_message():
    """Test that large messages use TCP even when hybrid transport is used."""
    # Create a hybrid transport for sender
    sender = HybridTransport(udp_max_size=1000)  # Messages > 1000 bytes should use TCP
    
    # Create separate UDP and TCP receivers to verify which one receives the message
    udp_receiver = UDPTransport()
    tcp_receiver = TCPTransport()
    
    # Bind to different ports
    sender_addr = ("127.0.0.1", 12360)
    udp_receiver_addr = ("127.0.0.1", 12361)
    tcp_receiver_addr = ("127.0.0.1", 12361)  # Same port but different protocol
    
    await sender.bind(sender_addr)
    await udp_receiver.bind(udp_receiver_addr)
    await tcp_receiver.bind(tcp_receiver_addr)
    
    # Define futures to track reception
    udp_received = asyncio.Future()
    tcp_received = asyncio.Future()
    
    # Set up callbacks
    async def on_udp_data(data, addr):
        logger.info(f"UDP received {len(data)} bytes from {addr[0]}:{addr[1]}")
        udp_received.set_result((data, addr))
    
    async def on_tcp_data(data, addr):
        logger.info(f"TCP received {len(data)} bytes from {addr[0]}:{addr[1]}")
        tcp_received.set_result((data, addr))
    
    # Start receivers
    await udp_receiver.start_receiver(on_udp_data)
    await tcp_receiver.start_receiver(on_tcp_data)
    
    # Wait a bit for the receivers to be ready
    await asyncio.sleep(0.1)
    
    # Send a large message (should use TCP)
    large_data = b"X" * 2000  # 2000 bytes, above the threshold
    dest_addr = ("127.0.0.1", 12361)
    await sender.send(large_data, dest_addr)
    
    # Wait for reception (with timeout)
    try:
        # We expect TCP to receive the data, not UDP
        await asyncio.wait_for(tcp_received, timeout=2.0)
        
        # UDP should not receive the large message
        udp_done = False
        try:
            await asyncio.wait_for(asyncio.shield(udp_received), timeout=0.5)
            udp_done = True
        except asyncio.TimeoutError:
            # This is expected
            pass
        
        assert not udp_done, "UDP should not have received the large message"
        
        # Verify the received data via TCP
        data, addr = tcp_received.result()
        assert data == large_data
        assert addr[0] == sender_addr[0]
        
    except asyncio.TimeoutError:
        assert False, "Failed to receive message on either transport"
    finally:
        # Clean up
        await sender.close()
        await udp_receiver.close()
        await tcp_receiver.close()

@pytest.mark.asyncio
async def test_transport_fallback_small_message():
    """Test that small messages use UDP when hybrid transport is used."""
    # Create a hybrid transport for sender
    sender = HybridTransport(udp_max_size=1000)  # Messages <= 1000 bytes should use UDP
    
    # Create separate UDP and TCP receivers to verify which one receives the message
    udp_receiver = UDPTransport()
    tcp_receiver = TCPTransport()
    
    # Bind to different ports
    sender_addr = ("127.0.0.1", 12370)
    udp_receiver_addr = ("127.0.0.1", 12371)
    tcp_receiver_addr = ("127.0.0.1", 12371)  # Same port but different protocol
    
    await sender.bind(sender_addr)
    await udp_receiver.bind(udp_receiver_addr)
    await tcp_receiver.bind(tcp_receiver_addr)
    
    # Define futures to track reception
    udp_received = asyncio.Future()
    tcp_received = asyncio.Future()
    
    # Set up callbacks
    async def on_udp_data(data, addr):
        logger.info(f"UDP received {len(data)} bytes from {addr[0]}:{addr[1]}")
        udp_received.set_result((data, addr))
    
    async def on_tcp_data(data, addr):
        logger.info(f"TCP received {len(data)} bytes from {addr[0]}:{addr[1]}")
        tcp_received.set_result((data, addr))
    
    # Start receivers
    await udp_receiver.start_receiver(on_udp_data)
    await tcp_receiver.start_receiver(on_tcp_data)
    
    # Wait a bit for the receivers to be ready
    await asyncio.sleep(0.1)
    
    # Send a small message (should use UDP)
    small_data = b"X" * 500  # 500 bytes, below the threshold
    dest_addr = ("127.0.0.1", 12371)
    await sender.send(small_data, dest_addr)
    
    # Wait for reception (with timeout)
    try:
        # We expect UDP to receive the data, not TCP
        await asyncio.wait_for(udp_received, timeout=2.0)
        
        # TCP should not receive the small message
        tcp_done = False
        try:
            await asyncio.wait_for(asyncio.shield(tcp_received), timeout=0.5)
            tcp_done = True
        except asyncio.TimeoutError:
            # This is expected
            pass
        
        assert not tcp_done, "TCP should not have received the small message"
        
        # Verify the received data via UDP
        data, addr = udp_received.result()
        assert data == small_data
        assert addr[0] == sender_addr[0]
        
    except asyncio.TimeoutError:
        assert False, "Failed to receive message on either transport"
    finally:
        # Clean up
        await sender.close()
        await udp_receiver.close()
        await tcp_receiver.close()

@pytest.mark.asyncio
async def test_transport_dynamic_switch():
    """Test that hybrid transport can dynamically switch between UDP and TCP based on message size."""
    # Create a hybrid transport for sender and receiver
    sender = HybridTransport(udp_max_size=1000)
    receiver = HybridTransport(udp_max_size=1000)
    
    # Bind to different ports
    sender_addr = ("127.0.0.1", 12380)
    receiver_addr = ("127.0.0.1", 12381)
    
    await sender.bind(sender_addr)
    await receiver.bind(receiver_addr)
    
    # Define variables to track reception
    received_messages = []
    test_done = asyncio.Event()
    
    # Set up callback
    async def on_data(data, addr):
        logger.info(f"Received {len(data)} bytes from {addr[0]}:{addr[1]}")
        received_messages.append(data)
        if len(received_messages) >= 4:  # We'll send 4 messages
            test_done.set()
    
    # Start receiver
    await receiver.start_receiver(on_data)
    
    # Wait a bit for the receiver to be ready
    await asyncio.sleep(0.1)
    
    # Send messages of varying sizes
    messages = [
        b"X" * 500,    # Small - should use UDP
        b"Y" * 1500,   # Large - should use TCP
        b"Z" * 750,    # Small - should use UDP
        b"W" * 2000    # Large - should use TCP
    ]
    
    for msg in messages:
        await sender.send(msg, receiver_addr)
        await asyncio.sleep(0.1)  # Brief pause between sends
    
    # Wait for all messages to be received
    try:
        await asyncio.wait_for(test_done.wait(), timeout=5.0)
        
        # Verify all messages were received
        assert len(received_messages) == 4
        
        # Verify the content of each message
        for i, expected in enumerate(messages):
            assert received_messages[i] == expected
        
    except asyncio.TimeoutError:
        assert False, f"Failed to receive all messages. Received: {len(received_messages)} of 4"
    finally:
        # Clean up
        await sender.close()
        await receiver.close()

@pytest.mark.asyncio
async def test_transport_udp_failure_fallback():
    """Test that hybrid transport falls back to TCP when UDP fails."""
    # Create a hybrid transport with a mocked UDP transport that fails
    sender = HybridTransport(udp_max_size=1000)
    receiver = TCPTransport()  # Only use TCP receiver
    
    # Sabotage the UDP transport to always fail
    original_send = sender.udp_transport.send
    
    async def mock_udp_send(data, dest):
        logger.info("Simulating UDP send failure")
        raise ConnectionRefusedError("Simulated UDP failure")
    
    sender.udp_transport.send = mock_udp_send
    
    # Bind to different ports
    sender_addr = ("127.0.0.1", 12390)
    receiver_addr = ("127.0.0.1", 12391)
    
    await sender.bind(sender_addr)
    await receiver.bind(receiver_addr)
    
    # Define future to track reception
    received = asyncio.Future()
    
    # Set up callback
    async def on_data(data, addr):
        logger.info(f"Received {len(data)} bytes from {addr[0]}:{addr[1]}")
        received.set_result((data, addr))
    
    # Start receiver
    await receiver.start_receiver(on_data)
    
    # Wait a bit for the receiver to be ready
    await asyncio.sleep(0.1)
    
    # Send a small message (would normally use UDP but will fail over to TCP)
    small_data = b"X" * 500
    await sender.send(small_data, receiver_addr)
    
    # Wait for reception (with timeout)
    try:
        await asyncio.wait_for(received, timeout=2.0)
        
        # Verify the received data via TCP
        data, addr = received.result()
        assert data == small_data
        assert addr[0] == sender_addr[0]
        
    except asyncio.TimeoutError:
        assert False, "Failed to receive message after UDP fallback to TCP"
    finally:
        # Restore the original method
        sender.udp_transport.send = original_send
        
        # Clean up
        await sender.close()
        await receiver.close()