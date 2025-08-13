"""
Integration test for the SWIM protocol with Hybrid Transport.

This test creates multiple SWIM nodes using hybrid transport and verifies
they can discover each other and maintain cluster membership.
"""

import asyncio
import logging
import time
import random
from typing import List, Dict, Set, Tuple

from swim.transport.hybrid import HybridTransport
from swim.protocol.node import Node
from swim.protocol.member import MemberState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("swim.integration.test")

# Disable some verbose logging
logging.getLogger("swim.transport.udp").setLevel(logging.WARNING)
logging.getLogger("swim.transport.tcp").setLevel(logging.WARNING)

async def run_swim_cluster_test(node_count: int = 3, test_duration: int = 20) -> bool:
    """
    Create a cluster of SWIM nodes and verify they discover each other.
    
    Args:
        node_count: Number of nodes to create
        test_duration: How long to run the test in seconds
        
    Returns:
        True if test passes, False otherwise
    """
    # Create nodes
    nodes: List[Node] = []
    addresses: List[Tuple[str, int]] = []
    
    logger.info(f"Starting SWIM cluster test with {node_count} nodes")
    
    # Create the first node (bootstrap node)
    base_port = 10000
    bootstrap_addr = ("127.0.0.1", base_port)
    
    logger.info(f"Creating bootstrap node at {bootstrap_addr[0]}:{bootstrap_addr[1]}")
    bootstrap_transport = HybridTransport(udp_max_size=1000)  # Use smaller threshold to force more TCP usage
    
    bootstrap_node = await Node.create(
        bind_addr=bootstrap_addr,
        transport=bootstrap_transport,
        seed_addrs=None,
        config={
            "PROTOCOL_PERIOD": 0.5,  # Faster protocol cycle for testing
            "SUSPECT_TIMEOUT": 2.0,  # Shorter suspect timeout
            "PUSH_PULL_SYNC_ENABLED": True,  # Enable push-pull sync
            "ADAPTIVE_TIMING_ENABLED": True,  # Enable adaptive timing
        }
    )
    
    await bootstrap_node.start()
    nodes.append(bootstrap_node)
    addresses.append(bootstrap_addr)
    
    # Create additional nodes that join the cluster
    for i in range(1, node_count):
        node_addr = ("127.0.0.1", base_port + i)
        logger.info(f"Creating node {i} at {node_addr[0]}:{node_addr[1]}")
        
        # Create hybrid transport with random UDP max size to test different behaviors
        udp_max = random.choice([500, 1000, 2000])
        transport = HybridTransport(udp_max_size=udp_max)
        
        node = await Node.create(
            bind_addr=node_addr,
            transport=transport,
            seed_addrs=[bootstrap_addr],  # Join via bootstrap node
            config={
                "PROTOCOL_PERIOD": 0.5,
                "SUSPECT_TIMEOUT": 2.0,
                "PUSH_PULL_SYNC_ENABLED": True,
                "ADAPTIVE_TIMING_ENABLED": True,
            }
        )
        
        await node.start()
        nodes.append(node)
        addresses.append(node_addr)
        
        # Brief pause between node starts
        await asyncio.sleep(0.5)
    
    # Run the test for the specified duration
    logger.info(f"All nodes started. Running test for {test_duration} seconds...")
    
    start_time = time.time()
    last_status = 0
    
    try:
        while time.time() - start_time < test_duration:
            # Every 5 seconds, check that all nodes have discovered each other
            elapsed = time.time() - start_time
            if elapsed - last_status >= 5:
                last_status = elapsed
                logger.info(f"Test running for {elapsed:.1f} seconds...")
                
                all_discovered = True
                
                # Check each node's member list
                for i, node in enumerate(nodes):
                    members = node.members.get_all_members()
                    alive_count = len([m for m in members if m.state == MemberState.ALIVE])
                    
                    logger.info(f"Node {i} at {addresses[i][0]}:{addresses[i][1]} sees {alive_count} alive members")
                    
                    # Each node should see all other nodes as alive
                    if alive_count < node_count:
                        logger.warning(f"Node {i} only sees {alive_count}/{node_count} nodes as alive")
                        all_discovered = False
                
                if all_discovered:
                    logger.info("All nodes have discovered each other!")
                    
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error during test: {e}")
        
    finally:
        # Clean up
        logger.info("Stopping all nodes...")
        for node in nodes:
            await node.stop()
    
    # Final verification - check that all nodes discovered each other
    success = True
    for i, node in enumerate(nodes):
        members = node.members.get_all_members()
        alive_count = len([m for m in members if m.state == MemberState.ALIVE])
        
        if alive_count < node_count:
            logger.error(f"Node {i} only saw {alive_count}/{node_count} nodes as alive")
            success = False
    
    if success:
        logger.info("SWIM cluster test PASSED! All nodes discovered each other.")
    else:
        logger.error("SWIM cluster test FAILED! Not all nodes discovered each other.")
    
    return success

# Run the test
if __name__ == "__main__":
    success = asyncio.run(run_swim_cluster_test(node_count=5, test_duration=30))
    if not success:
        import sys
        sys.exit(1)