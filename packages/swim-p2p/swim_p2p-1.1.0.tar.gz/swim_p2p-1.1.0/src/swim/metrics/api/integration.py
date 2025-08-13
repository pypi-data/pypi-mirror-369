"""
Integration module for the SWIM P2P Metrics API.

This module provides functions to integrate the metrics API with the SWIM protocol.
"""

import asyncio
import logging
import threading
import time
from typing import Optional, Dict, Any

from swim.metrics.api.server import set_local_node, start_server_in_thread, broadcast_metrics_update, register_node_api_port
from swim.metrics.api.client import MetricsAPIClient

logger = logging.getLogger(__name__)

class MetricsAPIIntegration:
    """Integration class for the SWIM P2P Metrics API."""
    
    def __init__(self, node, host: str = "0.0.0.0", port: int = 8080):
        """
        Initialize the metrics API integration.
        
        Args:
            node: The SWIM node to integrate with
            host: Host to bind the API server to
            port: Port to bind the API server to
        """
        self.node = node
        self.host = host
        self.port = port
        self.server_thread = None
        self.update_interval = 5.0  # seconds
        self.running = False
        self.update_task = None
        self.discovery_task = None
        
        # Register our own API port
        local_addr = f"{self.node.transport.local_address[0]}:{self.node.transport.local_address[1]}"
        register_node_api_port(local_addr, port)
    
    def start(self):
        """Start the metrics API integration."""
        if self.running:
            return
        
        # Set the local node reference in the server
        set_local_node(self.node)
        
        # Start the API server in a background thread
        self.server_thread = start_server_in_thread(self.host, self.port)
        
        # Start the metrics update task
        self.running = True
        self.update_task = asyncio.create_task(self._update_metrics_loop())
        
        # Start the API discovery task
        self.discovery_task = asyncio.create_task(self._discover_api_ports_loop())
        
        logger.info(f"Metrics API started on http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the metrics API integration."""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel the update task
        if self.update_task:
            self.update_task.cancel()
        
        # Cancel the discovery task
        if self.discovery_task:
            self.discovery_task.cancel()
        
        # The server thread is a daemon thread, so it will be terminated when the main thread exits
        
        logger.info("Metrics API stopped")
    
    async def _update_metrics_loop(self):
        """Periodically update and broadcast metrics."""
        try:
            while self.running:
                try:
                    # Get metrics from the local node
                    from swim.metrics.api.server import _get_local_node_metrics
                    metrics = _get_local_node_metrics()
                    
                    # Broadcast metrics update to WebSocket clients
                    local_addr = f"{self.node.transport.local_address[0]}:{self.node.transport.local_address[1]}"
                    await broadcast_metrics_update(local_addr, metrics)
                    
                except Exception as e:
                    logger.error(f"Error updating metrics: {e}")
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
        
        except asyncio.CancelledError:
            logger.debug("Metrics update task cancelled")
        except Exception as e:
            logger.error(f"Error in metrics update loop: {e}")
    
    async def _discover_api_ports_loop(self):
        """Periodically discover API ports of other nodes."""
        try:
            # Wait a bit before starting discovery to allow the node to join the network
            await asyncio.sleep(5.0)
            
            while self.running:
                try:
                    # Get all members from the local node
                    members = self.node.members.get_all_members()
                    
                    # For each member, try to discover its API port
                    for member in members:
                        member_addr = f"{member.addr[0]}:{member.addr[1]}"
                        
                        # Skip self
                        local_addr = f"{self.node.transport.local_address[0]}:{self.node.transport.local_address[1]}"
                        if member_addr == local_addr:
                            continue
                        
                        # Try to discover the API port
                        await self._discover_api_port(member_addr)
                    
                except Exception as e:
                    logger.error(f"Error discovering API ports: {e}")
                
                # Wait before next discovery
                await asyncio.sleep(30.0)  # Discover every 30 seconds
        
        except asyncio.CancelledError:
            logger.debug("API discovery task cancelled")
        except Exception as e:
            logger.error(f"Error in API discovery loop: {e}")
    
    async def _discover_api_port(self, node_addr: str):
        """
        Discover the API port of a node.
        
        Args:
            node_addr: The address of the node (host:port)
        """
        from swim.metrics.api.server import node_api_ports, _check_api_port
        
        # Skip if we already know the API port
        if node_addr in node_api_ports:
            return
        
        # Parse the address
        host, port_str = node_addr.split(':')
        swim_port = int(port_str)
        
        # Try common API ports: swim_port + 80, swim_port + 100, 8080, 8081, etc.
        potential_ports = [
            swim_port + 80,  # Common offset for API ports
            swim_port + 100,
            8080,
            8081,
            9000,
            9001
        ]
        
        # Try to connect to each potential port
        for port in potential_ports:
            if await _check_api_port(host, port):
                register_node_api_port(node_addr, port)
                logger.info(f"Discovered API port {port} for node {node_addr}")
                
                # Announce our API port to the discovered node
                try:
                    client = MetricsAPIClient(f"http://{host}:{port}")
                    local_addr = f"{self.node.transport.local_address[0]}:{self.node.transport.local_address[1]}"
                    await client.register_api_port(local_addr, self.port)
                    logger.info(f"Announced our API port {self.port} to node {node_addr}")
                except Exception as e:
                    logger.error(f"Error announcing API port to {node_addr}: {e}")
                
                return
        
        logger.debug(f"Could not discover API port for node {node_addr}")

def setup_metrics_api(node, host: str = "0.0.0.0", port: int = 8080) -> MetricsAPIIntegration:
    """
    Set up the metrics API for a node.
    
    Args:
        node: The SWIM node to integrate with
        host: Host to bind the API server to
        port: Port to bind the API server to
        
    Returns:
        The metrics API integration instance
    """
    integration = MetricsAPIIntegration(node, host, port)
    integration.start()
    
    logger.info(f"Set up metrics API for node {node.transport.local_address[0]}:{node.transport.local_address[1]}")
    
    return integration
