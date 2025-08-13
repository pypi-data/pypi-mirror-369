"""
Enhanced CLI for the SWIM P2P Metrics API.

This module provides an enhanced CLI for viewing metrics from all nodes in the network.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional, Set, Any

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Import the client
from swim.metrics.api.client import MetricsAPIClient

console = Console()

class MetricsAPICLI:
    """CLI for interacting with the SWIM P2P Metrics API."""
    
    def __init__(self, base_url: str):
        """
        Initialize the metrics API CLI.
        
        Args:
            base_url: Base URL of the metrics API server
        """
        self.client = MetricsAPIClient(base_url)
        self.layout = Layout()
        self.setup_layout()
        self.nodes = []
        self.selected_node = None
        self.network_metrics = None
        self.node_metrics = {}
        self.update_interval = 2.0  # seconds
        self.running = False
    
    def setup_layout(self):
        """Set up the layout for the CLI."""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        
        self.layout["main"].split_row(
            Layout(name="nodes", ratio=1),
            Layout(name="metrics", ratio=3)
        )
        
        self.layout["metrics"].split(
            Layout(name="node_info", size=5),
            Layout(name="bandwidth", size=8),
            Layout(name="protocol", size=8),
            Layout(name="latency", size=8)
        )
    
    async def update_nodes(self):
        """Update the list of connected nodes."""
        try:
            self.nodes = await self.client.get_nodes()
            if self.nodes and not self.selected_node:
                self.selected_node = self.nodes[0]
        except Exception as e:
            console.print(f"[bold red]Error updating nodes:[/bold red] {e}")
    
    async def update_metrics(self):
        """Update metrics for the selected node and network."""
        try:
            # Update network metrics
            self.network_metrics = await self.client.get_network_metrics()
            
            # Update selected node metrics
            if self.selected_node:
                self.node_metrics[self.selected_node] = await self.client.get_node_metrics(self.selected_node)
        except Exception as e:
            console.print(f"[bold red]Error updating metrics:[/bold red] {e}")
    
    def render_nodes_panel(self):
        """Render the nodes panel."""
        table = Table(show_header=True, header_style="bold")
        table.add_column("Address")
        table.add_column("State")
        
        for node in self.nodes:
            state = "Unknown"
            style = ""
            
            if node in self.node_metrics:
                state = self.node_metrics[node]["node_info"]["state"]
                if state == "alive":
                    style = "green"
                elif state == "suspect":
                    style = "yellow"
                elif state == "dead":
                    style = "red"
            
            if node == self.selected_node:
                table.add_row(f"[bold]{node}[/bold]", f"[bold {style}]{state}[/bold {style}]")
            else:
                table.add_row(node, f"[{style}]{state}[/{style}]")
        
        return Panel(table, title="Nodes", border_style="blue")
    
    def render_node_info_panel(self):
        """Render the node info panel."""
        if not self.selected_node or self.selected_node not in self.node_metrics:
            return Panel(Text("No node selected"), title="Node Info", border_style="blue")
        
        metrics = self.node_metrics[self.selected_node]
        node_info = metrics["node_info"]
        
        table = Table(show_header=False)
        table.add_column("Property")
        table.add_column("Value")
        
        table.add_row("Address", node_info["address"])
        table.add_row("State", node_info["state"])
        table.add_row("Incarnation", str(node_info["incarnation"]))
        table.add_row("Last State Change", str(datetime.fromtimestamp(node_info["last_state_change"])))
        table.add_row("Uptime", f"{metrics['uptime_seconds']:.2f} seconds")
        
        return Panel(table, title=f"Node Info: {self.selected_node}", border_style="blue")
    
    def render_bandwidth_panel(self):
        """Render the bandwidth panel."""
        if not self.selected_node or self.selected_node not in self.node_metrics:
            return Panel(Text("No node selected"), title="Bandwidth", border_style="blue")
        
        metrics = self.node_metrics[self.selected_node]
        bandwidth = metrics["bandwidth"]
        
        table = Table(show_header=False)
        table.add_column("Metric")
        table.add_column("Value")
        
        table.add_row("Inbound Bytes", f"{bandwidth['inbound_bytes']:,}")
        table.add_row("Outbound Bytes", f"{bandwidth['outbound_bytes']:,}")
        table.add_row("Inbound Rate", f"{bandwidth['inbound_rate']:.2f} bytes/sec")
        table.add_row("Outbound Rate", f"{bandwidth['outbound_rate']:.2f} bytes/sec")
        table.add_row("Messages Sent", f"{bandwidth['total_messages_sent']:,}")
        table.add_row("Messages Received", f"{bandwidth['total_messages_received']:,}")
        
        return Panel(table, title="Bandwidth", border_style="blue")
    
    def render_protocol_panel(self):
        """Render the protocol panel."""
        if not self.selected_node or self.selected_node not in self.node_metrics:
            return Panel(Text("No node selected"), title="Protocol", border_style="blue")
        
        metrics = self.node_metrics[self.selected_node]
        protocol = metrics["protocol"]
        
        table = Table(show_header=False)
        table.add_column("Metric")
        table.add_column("Value")
        
        table.add_row("Ping Count", f"{protocol['ping_count']:,}")
        table.add_row("Ack Count", f"{protocol['ack_count']:,}")
        table.add_row("Indirect Ping Count", f"{protocol['indirect_ping_count']:,}")
        table.add_row("Alive Count", f"{protocol['alive_count']:,}")
        table.add_row("Suspect Count", f"{protocol['suspect_count']:,}")
        table.add_row("Dead Count", f"{protocol['dead_count']:,}")
        table.add_row("Push-Pull Sync Count", f"{protocol['push_pull_sync_count']:,}")
        
        return Panel(table, title="Protocol", border_style="blue")
    
    def render_latency_panel(self):
        """Render the latency panel."""
        if not self.selected_node or self.selected_node not in self.node_metrics:
            return Panel(Text("No node selected"), title="Latency", border_style="blue")
        
        metrics = self.node_metrics[self.selected_node]
        latency = metrics["latency"]
        
        table = Table(show_header=False)
        table.add_column("Metric")
        table.add_column("Value")
        
        table.add_row("Average Latency", f"{latency['avg_latency_ms']:.2f} ms")
        table.add_row("Minimum Latency", f"{latency['min_latency_ms']:.2f} ms")
        table.add_row("Maximum Latency", f"{latency['max_latency_ms']:.2f} ms")
        
        if latency.get("p95_latency_ms") is not None:
            table.add_row("95th Percentile", f"{latency['p95_latency_ms']:.2f} ms")
        
        if latency.get("p99_latency_ms") is not None:
            table.add_row("99th Percentile", f"{latency['p99_latency_ms']:.2f} ms")
        
        return Panel(table, title="Latency", border_style="blue")
    
    def render_header(self):
        """Render the header panel."""
        if not self.network_metrics:
            return Panel(Text("SWIM P2P Metrics Dashboard", justify="center"), border_style="blue")
        
        network = self.network_metrics
        text = Text()
        text.append("SWIM P2P Metrics Dashboard", style="bold")
        text.append(" | ")
        text.append(f"Nodes: {network['total_nodes']}", style="bold")
        text.append(" | ")
        text.append(f"Alive: {network['alive_nodes']}", style="bold green")
        text.append(" | ")
        text.append(f"Suspect: {network['suspect_nodes']}", style="bold yellow")
        text.append(" | ")
        text.append(f"Dead: {network['dead_nodes']}", style="bold red")
        
        return Panel(text, border_style="blue")
    
    def render(self):
        """Render the CLI."""
        self.layout["header"].update(self.render_header())
        self.layout["nodes"].update(self.render_nodes_panel())
        self.layout["node_info"].update(self.render_node_info_panel())
        self.layout["bandwidth"].update(self.render_bandwidth_panel())
        self.layout["protocol"].update(self.render_protocol_panel())
        self.layout["latency"].update(self.render_latency_panel())
        
        return self.layout
    
    async def handle_input(self):
        """Handle user input."""
        while self.running:
            # This is a simple implementation - in a real CLI you'd use a library like prompt_toolkit
            # for better input handling
            await asyncio.sleep(0.1)
    
    async def handle_websocket_message(self, data):
        """Handle WebSocket messages."""
        if data["type"] == "metrics_update":
            # Request updated metrics for the node
            node_addr = data["node"]
            if node_addr == self.selected_node or node_addr not in self.node_metrics:
                await self.client.request_node_metrics(node_addr)
        elif data["type"] == "node_metrics":
            # Update node metrics
            node_addr = data["address"]
            self.node_metrics[node_addr] = data["metrics"]
            if hasattr(self, 'live'):
                self.live.update(self.render())
    
    async def run(self):
        """Run the CLI."""
        self.running = True
        
        # Start the WebSocket connection
        await self.client.start_websocket()
        
        # Register WebSocket callback
        self.client.add_websocket_callback(self.handle_websocket_message)
        
        # Create tasks for updating data and handling input
        update_task = asyncio.create_task(self.update_loop())
        input_task = asyncio.create_task(self.handle_input())
        
        try:
            with Live(self.render(), refresh_per_second=4) as live:
                self.live = live
                # Wait for tasks to complete
                await asyncio.gather(update_task, input_task)
        except KeyboardInterrupt:
            pass
        finally:
            # Clean up
            self.running = False
            update_task.cancel()
            input_task.cancel()
            await self.client.stop_websocket()
    
    async def update_loop(self):
        """Loop to update data periodically."""
        while self.running:
            await self.update_nodes()
            await self.update_metrics()
            if hasattr(self, 'live'):
                self.live.update(self.render())
            await asyncio.sleep(self.update_interval)

async def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="SWIM P2P Metrics API CLI")
    parser.add_argument("--url", default="http://localhost:8080", help="Base URL of the metrics API server")
    parser.add_argument("--interval", type=float, default=2.0, help="Update interval in seconds")
    
    args = parser.parse_args()
    
    cli = MetricsAPICLI(args.url)
    cli.update_interval = args.interval
    
    await cli.run()

if __name__ == "__main__":
    asyncio.run(main())
