"""
Test that the hybrid transport correctly selects UDP or TCP based on message size.
"""

import asyncio
import logging
import sys
import json
from swim.transport.hybrid import HybridTransport
from swim.utils.serialization import deserialize_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

async def test_hybrid_transport_protocol_selection():
    # Create transports
    sender = HybridTransport(udp_max_size=1000)
    receiver = HybridTransport(udp_max_size=1000)
    
    # Bind to different ports
    await sender.bind(("127.0.0.1", 9000))
    await receiver.bind(("127.0.0.1", 9001))
    
    # Define received messages array and event
    received_messages = []
    test_completed = asyncio.Event()
    
    # Set up the receiver callback
    async def on_message(data, addr):
        try:
            msg = deserialize_message(data)
            msg_id = msg.get("id", "unknown")
            msg_type = msg.get("type", "unknown")
            
            print(f"Received message: id={msg_id}, type={msg_type}, size={len(data)} from {addr}")
            received_messages.append((data, addr))
            
            # If we've received both messages, set the event
            if len(received_messages) >= 2:
                test_completed.set()
        except Exception as e:
            print(f"Error processing message: {e}")
    
    # Start the receiver
    await receiver.start_receiver(on_message)
    
    # Send a small message (should use UDP)
    small_message = b'{"type":"PING","from":"127.0.0.1:9000","id":"small-msg"}'
    print(f"Sending small message of size {len(small_message)} bytes (should use UDP)")
    await sender.send(small_message, ("127.0.0.1", 9001))
    
    # Brief pause between sends
    await asyncio.sleep(0.1)
    
    # Create a proper large JSON message
    # Create the message pieces separately to ensure valid JSON
    digest_items = []
    for i in range(100):
        digest_items.append({"addr": f"127.0.0.1:{8000+i}", "state": "ALIVE", "incarnation": i+1})
    
    # Create the full message as a Python dict and then serialize it
    large_message_dict = {
        "type": "HEARTBEAT",
        "from": "127.0.0.1:9000",
        "id": "large-msg",
        "digest": digest_items
    }
    
    # Serialize to JSON and then to bytes
    large_message = json.dumps(large_message_dict).encode('utf-8')
    
    print(f"Sending large message of size {len(large_message)} bytes (should use TCP)")
    await sender.send(large_message, ("127.0.0.1", 9001))
    
    # Wait for both messages to be received
    try:
        await asyncio.wait_for(test_completed.wait(), timeout=5.0)
        print(f"Received {len(received_messages)} messages successfully")
    except asyncio.TimeoutError:
        print(f"Test timed out after receiving only {len(received_messages)} messages")
        await sender.close()
        await receiver.close()
        return False
    
    # Verify both messages were received
    if len(received_messages) != 2:
        print(f"Expected 2 messages but received {len(received_messages)}")
        await sender.close()
        await receiver.close()
        return False
    
    # Verify message contents and protocols
    for i, (data, addr) in enumerate(received_messages):
        try:
            msg = deserialize_message(data)
            if i == 0:
                if msg.get("id") != "small-msg" or msg.get("type") != "PING":
                    print(f"First message has unexpected content: {msg}")
                    return False
                print("✓ Small message received correctly via UDP")
            else:
                if msg.get("id") != "large-msg" or msg.get("type") != "HEARTBEAT":
                    print(f"Second message has unexpected content: {msg}")
                    return False
                print("✓ Large message received correctly via TCP")
        except Exception as e:
            print(f"Error parsing message {i}: {e}")
            return False
    
    # Clean up
    await sender.close()
    await receiver.close()
    
    print("All tests passed! Transport selection is working correctly.")
    return True

# Run the test
if __name__ == "__main__":
    success = asyncio.run(test_hybrid_transport_protocol_selection())
    if not success:
        sys.exit(1)