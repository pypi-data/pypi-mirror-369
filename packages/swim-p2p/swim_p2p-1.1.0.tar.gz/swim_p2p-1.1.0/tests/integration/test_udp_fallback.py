
"""
Test that the hybrid transport correctly falls back to TCP when UDP fails.
"""

import asyncio
import logging
import sys
import socket
from swim.transport.hybrid import HybridTransport
from swim.utils.serialization import deserialize_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

async def test_udp_fallback():
    # Create transports
    sender = HybridTransport(udp_max_size=2000)  # Higher UDP size threshold
    receiver = HybridTransport(udp_max_size=2000)
    
    # Bind to different ports
    await sender.bind(("127.0.0.1", 9010))
    await receiver.bind(("127.0.0.1", 9011))
    
    # Define received message event
    message_received = asyncio.Event()
    received_data = None
    
    # Set up the receiver callback
    async def on_message(data, addr):
        nonlocal received_data
        msg = deserialize_message(data)
        msg_id = msg.get("id", "unknown")
        msg_type = msg.get("type", "unknown")
        
        print(f"Received message: id={msg_id}, type={msg_type}, size={len(data)} from {addr}")
        received_data = data
        message_received.set()
    
    # Start the receiver
    await receiver.start_receiver(on_message)
    
    # Create a normal message that would use UDP
    test_message = b'{"type":"PING","from":"127.0.0.1:9010","id":"fallback-test"}'
    
    # First, save the original UDP send method
    original_send = sender.udp_transport.send
    
    # Then, override it to always fail (simulating UDP failure)
    async def mock_udp_send(data, dest):
        print(f"UDP send to {dest} failed (simulated)")
        raise ConnectionError("Simulated UDP failure")
    
    try:
        # Replace the send method with our mock that always fails
        sender.udp_transport.send = mock_udp_send
        
        # Send message that would normally use UDP but should fall back to TCP
        print(f"Sending message of size {len(test_message)} bytes with UDP forced to fail")
        await sender.send(test_message, ("127.0.0.1", 9011))
        
        # Wait for the message to be received
        try:
            await asyncio.wait_for(message_received.wait(), timeout=5.0)
            print("Message successfully received via TCP fallback!")
            
            # Verify the message content
            msg = deserialize_message(received_data)
            if msg.get("id") != "fallback-test" or msg.get("type") != "PING":
                print(f"Received message has unexpected content: {msg}")
                return False
            
            print("UDP fallback to TCP is working correctly!")
            return True
            
        except asyncio.TimeoutError:
            print("Test failed: Message not received within timeout")
            return False
            
    except Exception as e:
        print(f"Unexpected error during test: {e}")
        return False
        
    finally:
        # Restore the original UDP send method
        sender.udp_transport.send = original_send
        
        # Clean up
        await sender.close()
        await receiver.close()

# Run the test
if __name__ == "__main__":
    success = asyncio.run(test_udp_fallback())
    if not success:
        sys.exit(1)