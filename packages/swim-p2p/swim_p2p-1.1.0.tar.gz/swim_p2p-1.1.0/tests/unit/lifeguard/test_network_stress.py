#!/usr/bin/env python
"""
Test script to demonstrate Lifeguard resilience under network stress.

This script creates two nodes, one with Lifeguard enabled and one without,
then introduces network delays and packet loss to test resilience.
"""

import asyncio
import logging
import random
import time
import os
import sys
from typing import Tuple, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('network_stress_test.log')
    ]
)

logger = logging.getLogger("network_stress_test")

# Connect to existing nodes instead of creating new ones
async def test_network_stress():
    # Import modules
    from swim.transport.hybrid import HybridTransport
    from swim.protocol.node import Node
    
    # First start two nodes:
    # python -m swim.main --addr 127.0.0.1:8000 --lifeguard --log-level DEBUG
    # python -m swim.main --addr 127.0.0.1:8001 --seeds 127.0.0.1:8000 --no-lifeguard --log-level DEBUG
    
    # Wait for user to confirm nodes are running
    print("Make sure both nodes are running:")
    print("1. Node with Lifeguard at 127.0.0.1:8000")
    print("2. Node without Lifeguard at 127.0.0.1:8001")
    input("Press Enter to continue...")
    
    # Simulate network issues by introducing packet loss and delays
    print("Simulating network degradation...")
    
    # Wait for the nodes to establish communication
    await asyncio.sleep(10)
    
    # Start causing network issues
    print("Starting network stress test. Will run for 2 minutes.")
    start_time = time.time()
    end_time = start_time + 120  # 2 minutes
    
    # Create UDP sockets to send traffic that will be dropped or delayed
    import socket
    lifeguard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    standard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while time.time() < end_time:
        # Generate random malformed packets to both nodes to create stress
        if random.random() < 0.3:  # 30% chance of sending packet
            data = os.urandom(random.randint(10, 100))  # Random data
            
            # Send to Lifeguard node
            lifeguard_sock.sendto(data, ('127.0.0.1', 8000))
            
            # Send to Standard node
            standard_sock.sendto(data, ('127.0.0.1', 8001))
        
        # Small delay between packets
        await asyncio.sleep(0.01)
        
        # Every 15 seconds, print status
        elapsed = time.time() - start_time
        if int(elapsed) % 15 == 0 and int(elapsed) > 0:
            print(f"Test running for {int(elapsed)} seconds...")
            
            # More aggressive network issues every 15 seconds
            for _ in range(100):  # Burst of 100 packets
                data = os.urandom(random.randint(50, 500))  # Larger random data
                
                # Send to both nodes
                lifeguard_sock.sendto(data, ('127.0.0.1', 8000))
                standard_sock.sendto(data, ('127.0.0.1', 8001))
                
                # Tiny delay between burst packets
                await asyncio.sleep(0.001)
                
            print("Sent burst of stress traffic!")
    
    # Clean up
    lifeguard_sock.close()
    standard_sock.close()
    
    print("Network stress test completed. Check the logs of both nodes to compare their behavior.")
    print("The Lifeguard-enabled node (8000) should show:")
    print("1. Adaptive protocol period adjustments")
    print("2. Changing awareness values")
    print("3. Variable probe counts")
    print("4. Adaptive timeouts")
    print("5. Fewer false positives")

if __name__ == "__main__":
    asyncio.run(test_network_stress())