"""
Metrics API server for SWIM P2P protocol - Fixed Version.

This module provides a FastAPI-based server for exposing metrics
from SWIM P2P nodes to external clients.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

import aiohttp
from fastapi import FastAPI, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import from the existing SWIM implementation
from swim.metrics.collector import MetricsCollector
from swim.metrics.latency import LatencyTracker
from swim.metrics.bandwidth import BandwidthMonitor, Direction

logger = logging.getLogger(__name__)

# Models for API responses
class NodeInfo(BaseModel):
    """Information about a node."""
    address: str
    state: str
    incarnation: int
    last_state_change: float

class BandwidthStats(BaseModel):
    """Bandwidth statistics."""
    inbound_bytes: int
    outbound_bytes: int
    inbound_rate: float  # bytes/sec
    outbound_rate: float  # bytes/sec
    total_messages_sent: int
    total_messages_received: int

class LatencyStats(BaseModel):
    """Latency statistics."""
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p95_latency_ms: Optional[float] = None
    p99_latency_ms: Optional[float] = None

class ProtocolStats(BaseModel):
    """Protocol statistics."""
    ping_count: int
    ack_count: int
    indirect_ping_count: int
    alive_count: int
    suspect_count: int
    dead_count: int
    push_pull_sync_count: int

class NodeMetrics(BaseModel):
    """Comprehensive metrics for a node."""
    node_info: NodeInfo
    bandwidth: BandwidthStats
    latency: LatencyStats
    protocol: ProtocolStats
    uptime_seconds: float
    last_updated: datetime

class NetworkMetrics(BaseModel):
    """Network-wide metrics."""
    nodes: List[NodeMetrics]
    total_nodes: int
    alive_nodes: int
    suspect_nodes: int
    dead_count: int
    network_bandwidth: BandwidthStats

# Create FastAPI app
app = FastAPI(
    title="SWIM P2P Metrics API",
    description="API for querying metrics from SWIM P2P protocol nodes",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for node metrics
node_metrics: Dict[str, NodeMetrics] = {}
node_api_ports: Dict[str, int] = {}  # Map of node address to API port
websocket_clients: List[WebSocket] = []

# Reference to the local node
local_node = None

def set_local_node(node):
    """Set the local node reference."""
    global local_node
    local_node = node

def register_node_api_port(node_addr: str, port: int):
    """Register the API port for a node."""
    node_api_ports[node_addr] = port
    logger.info(f"Registered API port {port} for node {node_addr}")

@app.get("/api/nodes", response_model=List[str])
async def get_nodes():
    """Get a list of all known node addresses."""
    global local_node
    
    if not local_node:
        return list(node_metrics.keys())
    
    # Get all members from the local node
    members = local_node.members.get_all_members()
    addresses = [f"{member.addr[0]}:{member.addr[1]}" for member in members]
    
    # Add local node if not in the list
    local_addr = f"{local_node.transport.local_address[0]}:{local_node.transport.local_address[1]}"
    if local_addr not in addresses:
        addresses.append(local_addr)
    
    return addresses

# NEW ENDPOINT: Add a simple /api/metrics endpoint that returns the local node's metrics
@app.get("/api/metrics")
async def get_metrics():
    """Get metrics for the local node."""
    global local_node
    
    if not local_node:
        raise HTTPException(status_code=404, detail="Local node not available")
    
    # Get metrics report from the node
    report = local_node.get_metrics_report()
    if not report:
        raise HTTPException(status_code=404, detail="No metrics available for local node")
    
    # Return the raw metrics data
    return report.get("metrics", {})

@app.get("/api/metrics/node/{address}", response_model=NodeMetrics)
async def get_node_metrics(address: str):
    """Get metrics for a specific node."""
    global local_node
    
    # Check if this is the local node
    if local_node and f"{local_node.transport.local_address[0]}:{local_node.transport.local_address[1]}" == address:
        return _get_local_node_metrics()
    
    # Check if we have cached metrics for this node
    if address in node_metrics:
        # Check if the metrics are fresh (less than 10 seconds old)
        if (datetime.now() - node_metrics[address].last_updated).total_seconds() < 10:
            return node_metrics[address]
    
    # Try to fetch metrics from the node
    try:
        metrics = await _fetch_node_metrics(address)
        if metrics:
            node_metrics[address] = metrics
            return metrics
    except Exception as e:
        logger.error(f"Failed to fetch metrics from {address}: {e}")
        # If we have stale metrics, return them rather than failing
        if address in node_metrics:
            logger.warning(f"Returning stale metrics for {address}")
            return node_metrics[address]
    
    raise HTTPException(status_code=404, detail=f"No metrics available for node {address}")

@app.get("/api/metrics/network", response_model=NetworkMetrics)
async def get_network_metrics():
    """Get aggregated metrics for the entire network."""
    global local_node
    
    # Get all known nodes
    nodes = await get_nodes()
    
    # Collect metrics for each node
    node_metrics_list = []
    alive_count = 0
    suspect_count = 0
    dead_count = 0
    
    total_inbound_bytes = 0
    total_outbound_bytes = 0
    total_inbound_rate = 0.0
    total_outbound_rate = 0.0
    total_messages_sent = 0
    total_messages_received = 0
    
    # Create tasks to fetch metrics from all nodes in parallel
    tasks = []
    for addr in nodes:
        tasks.append(get_node_metrics_safe(addr))
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Process results
    for metrics in results:
        if metrics:
            node_metrics_list.append(metrics)
            
            # Count node states
            if metrics.node_info.state == "alive":
                alive_count += 1
            elif metrics.node_info.state == "suspect":
                suspect_count += 1
            elif metrics.node_info.state == "dead":
                dead_count += 1
            
            # Aggregate bandwidth stats
            total_inbound_bytes += metrics.bandwidth.inbound_bytes
            total_outbound_bytes += metrics.bandwidth.outbound_bytes
            total_inbound_rate += metrics.bandwidth.inbound_rate
            total_outbound_rate += metrics.bandwidth.outbound_rate
            total_messages_sent += metrics.bandwidth.total_messages_sent
            total_messages_received += metrics.bandwidth.total_messages_received
    
    # Create network bandwidth stats
    network_bandwidth = BandwidthStats(
        inbound_bytes=total_inbound_bytes,
        outbound_bytes=total_outbound_bytes,
        inbound_rate=total_inbound_rate,
        outbound_rate=total_outbound_rate,
        total_messages_sent=total_messages_sent,
        total_messages_received=total_messages_received
    )
    
    return NetworkMetrics(
        nodes=node_metrics_list,
        total_nodes=len(nodes),
        alive_nodes=alive_count,
        suspect_nodes=suspect_count,
        dead_count=dead_count,
        network_bandwidth=network_bandwidth
    )

async def get_node_metrics_safe(address: str) -> Optional[NodeMetrics]:
    """
    Safely get metrics for a node, catching any exceptions.
    
    This is a helper function for get_network_metrics to avoid failing
    if one node's metrics can't be fetched.
    """
    try:
        return await get_node_metrics(address)
    except Exception as e:
        logger.error(f"Error getting metrics for {address}: {e}")
        return None

@app.get("/api/node-api-ports", response_model=Dict[str, int])
async def get_node_api_ports():
    """Get the API ports for all known nodes."""
    return node_api_ports

@app.post("/api/register-api-port/{node_addr}")
async def register_api_port(node_addr: str, port: int):
    """Register the API port for a node."""
    register_node_api_port(node_addr, port)
    return {"status": "success", "node_addr": node_addr, "port": port}

# NEW ENDPOINT: Add a simple /api/nodes/{node}/metrics endpoint that redirects to the correct endpoint
@app.get("/api/nodes/{node}/metrics")
async def get_node_metrics_redirect(node: str):
    """Get metrics for a specific node (redirect to the correct endpoint)."""
    # This is a compatibility endpoint for clients that expect this URL pattern
    try:
        # Get the metrics from the local node
        if local_node:
            report = local_node.get_metrics_report()
            if report:
                return report.get("metrics", {})
        
        # If we don't have a local node or metrics, return an empty object
        return {}
    except Exception as e:
        logger.error(f"Error getting metrics for node {node}: {e}")
        return {}

@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics updates."""
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        # Send initial data
        nodes = await get_nodes()
        initial_data = {
            "type": "initial_data",
            "nodes": nodes,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(initial_data))
        
        # Keep the connection open and handle messages
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            # Handle different request types
            if request["type"] == "get_node_metrics":
                addr = request.get("address")
                try:
                    metrics = await get_node_metrics(addr)
                    response = {
                        "type": "node_metrics",
                        "address": addr,
                        "metrics": metrics.dict(),
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(response))
                except Exception as e:
                    error_response = {
                        "type": "error",
                        "address": addr,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(error_response))
            
            elif request["type"] == "get_network_metrics":
                try:
                    metrics = await get_network_metrics()
                    response = {
                        "type": "network_metrics",
                        "metrics": metrics.dict(),
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(response))
                except Exception as e:
                    error_response = {
                        "type": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(error_response))
            
            elif request["type"] == "register_api_port":
                try:
                    node_addr = request.get("node_addr")
                    port = request.get("port")
                    if node_addr and port:
                        register_node_api_port(node_addr, port)
                        response = {
                            "type": "register_api_port_response",
                            "status": "success",
                            "node_addr": node_addr,
                            "port": port,
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(response))
                except Exception as e:
                    error_response = {
                        "type": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(error_response))
    
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in websocket_clients:
            websocket_clients.remove(websocket)

def _get_local_node_metrics() -> NodeMetrics:
    """Get metrics from the local node."""
    global local_node
    
    if not local_node:
        raise HTTPException(status_code=404, detail="Local node not available")
    
    # Get metrics report from the node
    report = local_node.get_metrics_report()
    if not report:
        raise HTTPException(status_code=404, detail="No metrics available for local node")
    
    # Extract node info
    local_addr = f"{local_node.transport.local_address[0]}:{local_node.transport.local_address[1]}"
    
    # Get member state
    state = "unknown"
    incarnation = 0
    last_state_change = 0.0
    
    # Try to find self in member list
    for member in local_node.members.get_all_members():
        if member.addr == local_node.transport.local_address:
            state = member.state.name.lower()
            incarnation = member.incarnation
            last_state_change = member.last_state_change
            break
    
    # If not found, assume alive
    if state == "unknown":
        state = "alive"
    
    node_info = NodeInfo(
        address=local_addr,
        state=state,
        incarnation=incarnation,
        last_state_change=last_state_change
    )
    
    # Extract bandwidth stats
    bandwidth_data = report.get("bandwidth", {})
    current_rates = bandwidth_data.get("current_rates", {})
    
    bandwidth = BandwidthStats(
        inbound_bytes=0,  # Need to extract from metrics
        outbound_bytes=0,  # Need to extract from metrics
        inbound_rate=current_rates.get("inbound", 0.0),
        outbound_rate=current_rates.get("outbound", 0.0),
        total_messages_sent=0,  # Need to extract from metrics
        total_messages_received=0  # Need to extract from metrics
    )
    
    # Try to extract message counts from metrics
    metrics_data = report.get("metrics", {})
    if "message_sent" in metrics_data:
        bandwidth.total_messages_sent = metrics_data["message_sent"].get("counter", 0)
    if "message_received" in metrics_data:
        bandwidth.total_messages_received = metrics_data["message_received"].get("counter", 0)
    
    # Extract latency stats
    latency = LatencyStats(
        avg_latency_ms=0.0,
        min_latency_ms=0.0,
        max_latency_ms=0.0
    )
    
    # Try to extract from peer_rtt histogram
    if "peer_rtt" in metrics_data and "histogram" in metrics_data["peer_rtt"]:
        rtt_stats = metrics_data["peer_rtt"]["histogram"]
        latency.avg_latency_ms = rtt_stats.get("mean", 0.0) * 1000
        latency.min_latency_ms = rtt_stats.get("min", 0.0) * 1000
        latency.max_latency_ms = rtt_stats.get("max", 0.0) * 1000
        if "p95" in rtt_stats:
            latency.p95_latency_ms = rtt_stats["p95"] * 1000
        if "p99" in rtt_stats:
            latency.p99_latency_ms = rtt_stats["p99"] * 1000
    
    # Extract protocol stats
    protocol = ProtocolStats(
        ping_count=metrics_data.get("ping", {}).get("counter", 0),
        ack_count=metrics_data.get("ack", {}).get("counter", 0),
        indirect_ping_count=metrics_data.get("indirect_ping", {}).get("counter", 0),
        alive_count=0,  # Will be set below
        suspect_count=0,  # Will be set below
        dead_count=0,  # Will be set below
        push_pull_sync_count=metrics_data.get("sync", {}).get("counter", 0)
    )
    
    # Extract member counts
    if "member_count" in metrics_data and "gauge" in metrics_data["member_count"]:
        member_counts = metrics_data["member_count"]["gauge"]
        protocol.alive_count = member_counts.get("alive", 0)
        protocol.suspect_count = member_counts.get("suspect", 0)
        protocol.dead_count = member_counts.get("dead", 0)
    
    # Calculate uptime
    uptime = time.time() - report.get("start_time", time.time())
    
    return NodeMetrics(
        node_info=node_info,
        bandwidth=bandwidth,
        latency=latency,
        protocol=protocol,
        uptime_seconds=uptime,
        last_updated=datetime.now()
    )

async def _fetch_node_metrics(address: str) -> Optional[NodeMetrics]:
    """
    Fetch metrics from a remote node.
    
    This function makes an HTTP request to the node's metrics API
    to fetch its metrics.
    
    Args:
        address: The address of the node (host:port)
        
    Returns:
        The node's metrics, or None if the metrics couldn't be fetched
    """
    # Parse the address
    host, port_str = address.split(':')
    swim_port = int(port_str)
    
    # Determine the API port
    api_port = None
    if address in node_api_ports:
        api_port = node_api_ports[address]
    else:
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
                api_port = port
                register_node_api_port(address, port)
                break
    
    if not api_port:
        logger.warning(f"Could not determine API port for node {address}")
        return None
    
    # Make the request to the node's API
    url = f"http://{host}:{api_port}/api/metrics/node/{address}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Convert the JSON data to a NodeMetrics object
                    node_info = NodeInfo(**data["node_info"])
                    bandwidth = BandwidthStats(**data["bandwidth"])
                    latency = LatencyStats(**data["latency"])
                    protocol = ProtocolStats(**data["protocol"])
                    
                    # Parse the last_updated timestamp
                    last_updated = datetime.fromisoformat(data["last_updated"])
                    
                    return NodeMetrics(
                        node_info=node_info,
                        bandwidth=bandwidth,
                        latency=latency,
                        protocol=protocol,
                        uptime_seconds=data["uptime_seconds"],
                        last_updated=last_updated
                    )
                else:
                    logger.warning(f"Failed to fetch metrics from {url}: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        logger.warning(f"Error connecting to {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Error fetching metrics from {url}: {e}")
        return None

async def _check_api_port(host: str, port: int) -> bool:
    """
    Check if a node has a metrics API running on the specified port.
    
    Args:
        host: The host to check
        port: The port to check
        
    Returns:
        True if the port has a metrics API, False otherwise
    """
    url = f"http://{host}:{port}/api/nodes"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2) as response:
                return response.status == 200
    except:
        return False

async def broadcast_metrics_update(node_addr: str, metrics: NodeMetrics):
    """Broadcast a metrics update to all connected WebSocket clients."""
    if not websocket_clients:
        return
    
    update_msg = {
        "type": "metrics_update",
        "node": node_addr,
        "metrics": metrics.dict(),
        "timestamp": datetime.now().isoformat()
    }
    
    for client in websocket_clients:
        try:
            await client.send_text(json.dumps(update_msg))
        except Exception as e:
            logger.error(f"Error sending update to WebSocket client: {e}")

def start_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the metrics API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)

def start_server_in_thread(host: str = "0.0.0.0", port: int = 8080):
    """Start the metrics API server in a background thread."""
    import threading
    thread = threading.Thread(
        target=start_server,
        args=(host, port),
        daemon=True
    )
    thread.start()
    return thread