#!/usr/bin/env python3
"""
SWIM-ZMQ Integration Test - Port Conflict Fix

This version fixes the critical port conflict between SWIM and ZMQ layers.

Key fixes:
1. Separated SWIM and ZMQ port ranges completely
2. Added network connectivity validation
3. Enhanced error handling for transport failures
4. Improved startup sequencing with connectivity checks
"""

import os
import sys
import time
import asyncio
import logging
import uuid
import json
import socket
from typing import Dict, List, Optional, Tuple, Set, Any

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from swim.transport.hybrid import HybridTransport
from swim.protocol.node import Node
from swim.events.dispatcher import EventDispatcher
from swim.events.handlers import LoggingHandler

# Import reliability components
from swim.integration.messaging.reliability import ReliabilityManager
from swim.integration.messaging.ack_system import AckSystem
from swim.integration.messaging.message_registry import MessageRegistry
from swim.integration.zmq.connection_manager import ConnectionManager
from swim.integration.zmq.dealer import EnhancedDealerManager
from swim.integration.zmq.router import RouterManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("swim_zmq_test")

# Enable debug for troubleshooting
DEBUG = True
if DEBUG:
    logging.getLogger("swim").setLevel(logging.DEBUG)


def check_port_available(host: str, port: int) -> bool:
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False


def find_available_ports(host: str, start_port: int, count: int) -> List[int]:
    """Find a range of available ports."""
    available = []
    port = start_port
    while len(available) < count:
        if check_port_available(host, port):
            available.append(port)
        port += 1
        if port > start_port + 1000:  # Safety limit
            raise RuntimeError(f"Could not find {count} available ports starting from {start_port}")
    return available


class MessageSerializer:
    """Handles proper message serialization for ZMQ transport."""
    
    @staticmethod
    def serialize(message: Dict[str, Any]) -> bytes:
        """Serialize message to bytes for ZMQ transport."""
        try:
            return json.dumps(message, default=str).encode('utf-8')
        except Exception as e:
            logger.error(f"Failed to serialize message: {e}")
            raise
    
    @staticmethod
    def deserialize(data: bytes) -> Dict[str, Any]:
        """Deserialize message from bytes."""
        try:
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to deserialize message: {e}")
            raise


class SwimZmqBridge:
    """Enhanced bridge between SWIM membership and ZMQ messaging."""
    
    def __init__(self, connection_manager: ConnectionManager, reliability_manager: ReliabilityManager):
        self.connection_manager = connection_manager
        self.reliability_manager = reliability_manager
        self.known_members = set()
        
    def swim_to_zmq_address(self, swim_addr: Tuple[str, int], zmq_port: int) -> str:
        """Convert SWIM address to ZMQ address using explicit ZMQ port."""
        return f"{swim_addr[0]}:{zmq_port}"
    
    async def sync_with_swim_state(self, swim_node, zmq_port_map: Dict[int, int]):
        """Synchronize ZMQ connections with current SWIM state."""
        if not swim_node.members:
            return
            
        current_alive = set()
        
        # Get all alive members from SWIM
        for member in swim_node.members.get_alive_members():
            swim_port = member.addr[1]
            if swim_port in zmq_port_map:
                zmq_port = zmq_port_map[swim_port]
                zmq_addr = f"{member.addr[0]}:{zmq_port}"
                current_alive.add(zmq_addr)
                
                # Register new alive members
                if zmq_addr not in self.known_members:
                    logger.info(f"BRIDGE: Registering new alive member {zmq_addr} (SWIM: {member.addr[0]}:{swim_port})")
                    await self.connection_manager.handle_swim_membership_change(zmq_addr, "ALIVE")
                    self.known_members.add(zmq_addr)
        
        # Remove members that are no longer alive
        to_remove = self.known_members - current_alive
        for zmq_addr in to_remove:
            logger.info(f"BRIDGE: Removing dead member {zmq_addr}")
            await self.connection_manager.handle_swim_membership_change(zmq_addr, "DEAD")
            self.known_members.discard(zmq_addr)
        
        logger.info(f"BRIDGE: Synchronized {len(current_alive)} alive members")


class TestNode:
    """Enhanced test node with port conflict resolution."""
    
    def __init__(self, node_id: str, swim_port: int, zmq_port: int):
        self.node_id = node_id
        self.host = "127.0.0.1"
        self.swim_addr = (self.host, swim_port)
        self.zmq_addr = (self.host, zmq_port)
        self.zmq_addr_str = f"{self.host}:{zmq_port}"
        
        # Core components
        self.node = None
        self.event_dispatcher = None
        self.message_registry = None
        self.ack_system = None
        self.reliability_manager = None
        self.connection_manager = None
        self.dealer_manager = None
        self.router_manager = None
        self.swim_zmq_bridge = None
        
        # Message tracking
        self.sent_messages = {}
        self.received_messages = {}
        
        # State tracking
        self.is_running = False
        self.startup_complete = False
        
    async def start(self, seed_addrs: Optional[List[Tuple[str, int]]] = None, zmq_port_map: Optional[Dict[int, int]] = None):
        """Start the test node with proper initialization sequence."""
        logger.info(f"Starting {self.node_id} - SWIM: {self.swim_addr[0]}:{self.swim_addr[1]}, ZMQ: {self.zmq_addr_str}")
        
        try:
            # Phase 1: Validate ports
            if not check_port_available(self.host, self.swim_addr[1]):
                raise RuntimeError(f"SWIM port {self.swim_addr[1]} is not available")
            if not check_port_available(self.host, self.zmq_addr[1]):
                raise RuntimeError(f"ZMQ port {self.zmq_addr[1]} is not available")
            
            # Phase 2: Initialize event system
            self.event_dispatcher = EventDispatcher()
            self.event_dispatcher.subscribe("*", LoggingHandler())
            
            # Phase 3: Initialize ZMQ components
            await self._initialize_zmq_components()
            
            # Phase 4: Initialize SWIM node
            await self._initialize_swim_node(seed_addrs)
            
            # Phase 5: Initialize reliability layer
            await self._initialize_reliability_layer()
            
            # Phase 6: Create SWIM-ZMQ bridge
            self.swim_zmq_bridge = SwimZmqBridge(self.connection_manager, self.reliability_manager)
            
            # Phase 7: Connect all components
            await self._connect_components()
            
            # Phase 8: Start SWIM protocol
            await self.node.start()
            
            self.is_running = True
            logger.info(f"{self.node_id} fully started")
            
            # Phase 9: Post-startup initialization
            await self._post_startup_initialization(zmq_port_map or {})
            
            self.startup_complete = True
            
        except Exception as e:
            logger.error(f"Failed to start {self.node_id}: {e}")
            await self.stop()
            raise
    
    async def _initialize_zmq_components(self):
        """Initialize ZMQ components."""
        # Router for receiving messages
        self.router_manager = RouterManager(
            bind_address=self.zmq_addr_str
        )
        await self.router_manager.start()
        
        # Dealer for sending messages
        self.dealer_manager = EnhancedDealerManager(node_id=self.zmq_addr_str)
        await self.dealer_manager.start()
        
        # Connection manager
        self.connection_manager = ConnectionManager(node_id=self.zmq_addr_str)
        self.connection_manager.set_dealer_callbacks(
            connect_callback=self.dealer_manager.get_connection,
            disconnect_callback=self.dealer_manager.mark_failed
        )
        await self.connection_manager.start()
        
        # Set up message handler
        self.router_manager.set_default_handler(self._handle_message)
        
    async def _initialize_swim_node(self, seed_addrs):
        """Initialize SWIM node."""
        transport = HybridTransport()
        self.node = await Node.create(
            bind_addr=self.swim_addr,
            transport=transport,
            seed_addrs=seed_addrs,
            event_dispatcher=self.event_dispatcher
        )
        
    async def _initialize_reliability_layer(self):
        """Initialize reliability and messaging components."""
        # Message registry
        self.message_registry = MessageRegistry(node_id=self.zmq_addr_str)
        
        # ACK system
        self.ack_system = AckSystem(node_id=self.zmq_addr_str)
        
        # Reliability manager
        self.reliability_manager = ReliabilityManager(node_id=self.zmq_addr_str)
        self.reliability_manager.set_transport_callback(self._send_via_dealer)
        
    async def _connect_components(self):
        """Connect all components together."""
        # Connect ACK system to reliability manager
        self.ack_system.set_reliability_callback(self.reliability_manager.handle_delivery_ack)
        self.ack_system.set_transport_callback(self._send_via_dealer)
        
    async def _send_via_dealer(self, target_node: str, message_data: bytes) -> bool:
        """Send message via dealer with proper serialization."""
        try:
            # Ensure message is properly formatted
            if isinstance(message_data, dict):
                message_data = MessageSerializer.serialize(message_data)
            elif isinstance(message_data, str):
                message_data = message_data.encode('utf-8')
            
            return await self.dealer_manager.send_message(target_node, message_data)
        except Exception as e:
            logger.error(f"Failed to send via dealer: {e}")
            return False
    
    async def _post_startup_initialization(self, zmq_port_map: Dict[int, int]):
        """Perform post-startup initialization with enhanced synchronization."""
        # Wait for SWIM to stabilize
        await asyncio.sleep(3)
        
        # Synchronize ZMQ with SWIM state
        await self.swim_zmq_bridge.sync_with_swim_state(self.node, zmq_port_map)
        
        # Additional stabilization
        await asyncio.sleep(2)
    
    async def sync_swim_zmq_state(self, zmq_port_map: Dict[int, int]):
        """Manually synchronize SWIM and ZMQ state."""
        if self.swim_zmq_bridge:
            await self.swim_zmq_bridge.sync_with_swim_state(self.node, zmq_port_map)
    
    async def stop(self):
        """Stop all components gracefully."""
        logger.info(f"Stopping {self.node_id}")
        
        self.is_running = False
        
        # Stop components in reverse order
        components = [
            ('SWIM node', self.node),
            ('Reliability manager', self.reliability_manager),
            ('Connection manager', self.connection_manager),
            ('Dealer manager', self.dealer_manager),
            ('Router manager', self.router_manager)
        ]
        
        for name, component in components:
            if component:
                try:
                    await component.stop()
                    logger.debug(f"{self.node_id} {name} stopped")
                except Exception as e:
                    logger.error(f"Error stopping {self.node_id} {name}: {e}")
        
        logger.info(f"{self.node_id} stopped")
    
    async def _handle_message(self, sender: str, message_data: bytes):
        """Handle received messages with proper deserialization."""
        try:
            # Deserialize message
            if isinstance(message_data, bytes):
                message = MessageSerializer.deserialize(message_data)
            else:
                message = message_data
            
            message_id = message.get("id", "unknown")
            message_type = message.get("type", "unknown")
            
            logger.info(f"{self.node_id} received {message_type} message {message_id} from {sender}")
            
            # Store message for verification
            self.received_messages[message_id] = {
                "sender": sender,
                "message": message,
                "timestamp": time.time()
            }
            
            # Send processing ACK if required
            if message.get("require_ack", False):
                await self.ack_system.send_processing_ack(
                    message_id=message_id,
                    target_node=sender,
                    success=True
                )
            
            # Handle specific message types
            await self._process_message_by_type(sender, message)
            
        except Exception as e:
            logger.error(f"Error handling message in {self.node_id} from {sender}: {e}")
    
    async def _process_message_by_type(self, sender: str, message: Dict):
        """Process message based on its type."""
        message_type = message.get("type", "unknown")
        
        if message_type == "TEST_MESSAGE" and message.get("echo", False):
            # Send echo response
            response = {
                "type": "ECHO_RESPONSE",
                "id": str(uuid.uuid4()),
                "original_id": message.get("id"),
                "content": f"Echo: {message.get('content', '')}",
                "timestamp": time.time(),
                "require_ack": True
            }
            await self.send_message(sender, response)
        
        elif message_type == "WARMUP":
            # Respond to warmup messages
            logger.info(f"{self.node_id} received warmup message from {sender}")
    
    async def send_message(self, target_node: str, message: Dict, zmq_port_map: Optional[Dict[int, int]] = None) -> bool:
        """Send a message with enhanced error handling and state checking."""
        if not self.is_running:
            logger.warning(f"{self.node_id} cannot send message - node is not running")
            return False
        
        # Ensure SWIM-ZMQ state is synchronized before sending
        if zmq_port_map:
            await self.sync_swim_zmq_state(zmq_port_map)
        
        message_id = message.get("id", str(uuid.uuid4()))
        message["id"] = message_id
        
        logger.info(f"{self.node_id} sending {message.get('type', 'unknown')} message {message_id} to {target_node}")
        
        # Track sent message
        self.sent_messages[message_id] = {
            "target": target_node,
            "message": message,
            "timestamp": time.time()
        }
        
        try:
            # Serialize message
            message_data = MessageSerializer.serialize(message)
            
            # Send via reliability manager
            success = await self.reliability_manager.send_reliable(
                target_node=target_node,
                message_data=message_data,
                trace_id=message.get("trace_id"),
                workflow_id=message.get("workflow_id"),
                timeout=10.0
            )
            
            if success:
                logger.info(f"{self.node_id} message {message_id} sent successfully to {target_node}")
            else:
                logger.warning(f"{self.node_id} failed to send message {message_id} to {target_node}")
            
            return success
            
        except Exception as e:
            logger.error(f"{self.node_id} error sending message {message_id} to {target_node}: {e}")
            return False
    
    async def send_test_message(self, target_node: str, content: str, echo: bool = False, zmq_port_map: Optional[Dict[int, int]] = None) -> Optional[str]:
        """Send a test message and return message ID or None if failed."""
        message_id = str(uuid.uuid4())
        message = {
            "type": "TEST_MESSAGE",
            "id": message_id,
            "content": content,
            "echo": echo,
            "timestamp": time.time(),
            "require_ack": True
        }
        
        success = await self.send_message(target_node, message, zmq_port_map)
        return message_id if success else None
    
    async def wait_for_swim_discovery(self, expected_alive_count: int, timeout: float = 30.0) -> bool:
        """Wait for SWIM to discover expected number of alive members."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.node and self.node.members:
                alive_members = self.node.members.get_alive_members()
                if len(alive_members) >= expected_alive_count:
                    logger.info(f"{self.node_id} SWIM discovered {len(alive_members)} alive members")
                    return True
            
            await asyncio.sleep(1)
        
        alive_count = len(self.node.members.get_alive_members()) if self.node and self.node.members else 0
        logger.warning(f"{self.node_id} SWIM discovery timeout - only found {alive_count} alive members")
        return False


async def run_port_fixed_test():
    """Run the integration test with proper port separation."""
    nodes = []
    test_success = True
    
    try:
        logger.info("=== SWIM-ZMQ Integration Test - Port Conflict Fix ===")
        
        # Find available ports with proper separation
        logger.info("Finding available ports...")
        swim_ports = find_available_ports("127.0.0.1", 8000, 3)
        zmq_ports = find_available_ports("127.0.0.1", 9000, 3)
        
        # Create port mapping
        zmq_port_map = {swim_ports[i]: zmq_ports[i] for i in range(3)}
        
        logger.info(f"SWIM ports: {swim_ports}")
        logger.info(f"ZMQ ports: {zmq_ports}")
        logger.info(f"Port mapping: {zmq_port_map}")
        
        # Create test nodes
        node1 = TestNode("Node1", swim_ports[0], zmq_ports[0])
        node2 = TestNode("Node2", swim_ports[1], zmq_ports[1])
        node3 = TestNode("Node3", swim_ports[2], zmq_ports[2])
        nodes = [node1, node2, node3]
        
        # Phase 1: Start nodes with proper sequencing
        logger.info("=== PHASE 1: Node Startup ===")
        
        # Start seed node first
        logger.info("Starting seed node (Node1)...")
        await node1.start(zmq_port_map=zmq_port_map)
        await asyncio.sleep(3)
        
        # Start second node
        logger.info("Starting Node2...")
        await node2.start(seed_addrs=[(node1.swim_addr[0], node1.swim_addr[1])], zmq_port_map=zmq_port_map)
        await asyncio.sleep(3)
        
        # Start third node
        logger.info("Starting Node3...")
        await node3.start(seed_addrs=[(node1.swim_addr[0], node1.swim_addr[1])], zmq_port_map=zmq_port_map)
        await asyncio.sleep(5)
        
        # Wait for SWIM discovery
        logger.info("Waiting for SWIM membership discovery...")
        discovery_success = True
        for node in nodes:
            success = await node.wait_for_swim_discovery(expected_alive_count=2, timeout=20.0)
            if not success:
                logger.error(f"{node.node_id} failed to discover other nodes")
                discovery_success = False
            else:
                alive_count = len(node.node.members.get_alive_members())
                logger.info(f"{node.node_id} discovered {alive_count} alive members")
        
        if not discovery_success:
            logger.error("SWIM discovery failed - aborting test")
            return False
        
        # Phase 2: Basic messaging test
        logger.info("=== PHASE 2: Basic Messaging Test ===")
        
        # Synchronize all nodes before testing
        for node in nodes:
            await node.sync_swim_zmq_state(zmq_port_map)
        
        await asyncio.sleep(2)  # Let synchronization complete
        
        test_messages = []
        
        # Send test messages
        msg1_id = await node1.send_test_message(node3.zmq_addr_str, "Hello from Node1 to Node3", echo=True, zmq_port_map=zmq_port_map)
        if msg1_id:
            test_messages.append((msg1_id, node3, "Node1->Node3"))
        
        msg2_id = await node2.send_test_message(node1.zmq_addr_str, "Hello from Node2 to Node1", echo=True, zmq_port_map=zmq_port_map)
        if msg2_id:
            test_messages.append((msg2_id, node1, "Node2->Node1"))
        
        msg3_id = await node3.send_test_message(node2.zmq_addr_str, "Hello from Node3 to Node2", echo=True, zmq_port_map=zmq_port_map)
        if msg3_id:
            test_messages.append((msg3_id, node2, "Node3->Node2"))
        
        # Wait for message processing
        await asyncio.sleep(5)
        
        # Verify message delivery
        logger.info("Verifying message delivery...")
        for msg_id, target_node, description in test_messages:
            if msg_id and msg_id in target_node.received_messages:
                logger.info(f"✓ {description} message {msg_id} delivered successfully")
            else:
                logger.error(f"✗ {description} message {msg_id} failed to deliver")
                test_success = False
        
        # Final summary
        logger.info("=== TEST SUMMARY ===")
        if test_success:
            logger.info("✅ All tests PASSED!")
        else:
            logger.error("❌ Some tests FAILED!")
        
        return test_success
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        return False
        
    finally:
        # Cleanup
        logger.info("Cleaning up test nodes...")
        for node in nodes:
            if node and hasattr(node, 'stop'):
                try:
                    await node.stop()
                    logger.info(f"{node.node_id} stopped successfully")
                except Exception as e:
                    logger.error(f"Error stopping {node.node_id}: {e}")


if __name__ == "__main__":
    try:
        success = asyncio.run(run_port_fixed_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        sys.exit(1)
