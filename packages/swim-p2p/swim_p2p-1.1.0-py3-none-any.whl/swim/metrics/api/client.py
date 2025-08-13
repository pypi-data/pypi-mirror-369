"""
Client for the SWIM P2P Metrics API.

This module provides a Python client for interacting with the metrics API.
"""

import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class MetricsAPIClient:
    """Client for interacting with the SWIM P2P Metrics API."""
    
    def __init__(self, base_url: str):
        """
        Initialize the metrics API client.
        
        Args:
            base_url: Base URL of the metrics API server (e.g., http://localhost:8080)
        """
        self.base_url = base_url.rstrip('/')
        self.websocket = None
        self.ws_task = None
        self.ws_callbacks = []
    
    async def get_nodes(self) -> List[str]:
        """Get a list of all known node addresses."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/nodes") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get nodes: {response.status} - {error_text}")
    
    async def get_node_metrics(self, address: str) -> Dict[str, Any]:
        """Get metrics for a specific node."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/metrics/node/{address}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get node metrics: {response.status} - {error_text}")
    
    async def get_network_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics for the entire network."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/metrics/network") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get network metrics: {response.status} - {error_text}")
    
    async def get_node_api_ports(self) -> Dict[str, int]:
        """Get the API ports for all known nodes."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/node-api-ports") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get node API ports: {response.status} - {error_text}")
    
    async def register_api_port(self, node_addr: str, port: int) -> Dict[str, Any]:
        """Register the API port for a node."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/register-api-port/{node_addr}",
                params={"port": port}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to register API port: {response.status} - {error_text}")
    
    async def _websocket_listener(self):
        """Background task to listen for WebSocket messages."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(f"{self.base_url}/ws/metrics") as ws:
                    self.websocket = ws
                    
                    # Handle incoming messages
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            # Call all registered callbacks with the data
                            for callback in self.ws_callbacks:
                                try:
                                    await callback(data)
                                except Exception as e:
                                    print(f"Error in WebSocket callback: {e}")
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print(f"WebSocket connection closed with exception {ws.exception()}")
                            break
        except Exception as e:
            print(f"WebSocket connection error: {e}")
        finally:
            self.websocket = None
    
    async def start_websocket(self):
        """Start the WebSocket connection for real-time updates."""
        if self.ws_task is None or self.ws_task.done():
            self.ws_task = asyncio.create_task(self._websocket_listener())
    
    async def stop_websocket(self):
        """Stop the WebSocket connection."""
        if self.ws_task and not self.ws_task.done():
            self.ws_task.cancel()
            try:
                await self.ws_task
            except asyncio.CancelledError:
                pass
            self.ws_task = None
    
    def add_websocket_callback(self, callback):
        """
        Add a callback function to be called when WebSocket messages are received.
        
        The callback should be a coroutine function that takes a single argument (the message data).
        """
        self.ws_callbacks.append(callback)
    
    def remove_websocket_callback(self, callback):
        """Remove a previously added WebSocket callback."""
        if callback in self.ws_callbacks:
            self.ws_callbacks.remove(callback)
    
    async def request_node_metrics(self, address: str):
        """Request metrics for a specific node via WebSocket."""
        if self.websocket:
            await self.websocket.send_str(json.dumps({
                "type": "get_node_metrics",
                "address": address,
                "timestamp": datetime.now().isoformat()
            }))
    
    async def request_network_metrics(self):
        """Request network metrics via WebSocket."""
        if self.websocket:
            await self.websocket.send_str(json.dumps({
                "type": "get_network_metrics",
                "timestamp": datetime.now().isoformat()
            }))
    
    async def register_api_port_ws(self, node_addr: str, port: int):
        """Register the API port for a node via WebSocket."""
        if self.websocket:
            await self.websocket.send_str(json.dumps({
                "type": "register_api_port",
                "node_addr": node_addr,
                "port": port,
                "timestamp": datetime.now().isoformat()
            }))
