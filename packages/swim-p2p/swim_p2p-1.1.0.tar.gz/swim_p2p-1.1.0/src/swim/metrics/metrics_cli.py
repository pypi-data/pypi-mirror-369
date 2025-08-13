"""
Enhanced Metrics CLI for SWIM P2P Protocol - API Endpoint Fix Version.

This version uses the correct API endpoints to fetch metrics.
"""

import argparse
import asyncio
import json
import time
import os
import sys
from datetime import datetime
import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import aiohttp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("metrics_cli.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("metrics_cli")

# Add parent directory to path so we can import the necessary modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Default API port
DEFAULT_API_PORT = 8089

try:
    from swim.metrics.collector import MetricsCollector
    from swim.metrics.latency import LatencyTracker
    from swim.metrics.bandwidth import BandwidthMonitor, Direction
    from swim.config import get_config
    from swim.utils.network import get_local_ip, get_available_port
    from swim.metrics.api.client import MetricsAPIClient
except ImportError as e:
    logger.warning(f"Could not import SWIM modules: {e}. Some functionality may be limited.")


class MetricsFileHandler:
    """
    Handles saving metrics data to files with proper API format support.
    """

    def __init__(self, metrics_dir: str):
        """
        Initialize the metrics file handler.
        
        Args:
            metrics_dir: Directory to save metrics data
        """
        self.metrics_dir = metrics_dir
        self.files_written = 0
        
        # Create metrics directory and subdirectories
        self._ensure_directories_exist()

    def _ensure_directories_exist(self) -> None:
        """Create metrics directory and subdirectories if they don't exist."""
        os.makedirs(self.metrics_dir, exist_ok=True)
        os.makedirs(os.path.join(self.metrics_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(self.metrics_dir, "bandwidth"), exist_ok=True)
        os.makedirs(os.path.join(self.metrics_dir, "members"), exist_ok=True)
        os.makedirs(os.path.join(self.metrics_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.metrics_dir, "errors"), exist_ok=True)
        
        logger.info(f"Metrics will be saved to {os.path.abspath(self.metrics_dir)}")

    def save_metrics(self, node_id: str, metrics_data: Dict[str, Any]) -> None:
        """
        Save metrics data to files with support for API format.
        
        Args:
            node_id: Identifier for the node
            metrics_data: Metrics data to save
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        try:
            logger.info(f"💾 SAVING METRICS FOR {node_id}")
            
            # Save raw metrics data - always do this regardless of format
            raw_file = os.path.join(self.metrics_dir, "raw", f"{node_id.replace(':', '_')}-{timestamp}.json")
            os.makedirs(os.path.dirname(raw_file), exist_ok=True)
            with open(raw_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            logger.info(f"✅ Saved raw metrics to {raw_file}")
            self.files_written += 1
            
            # Handle API format metrics (nested under 'metrics' key)
            if "metrics" in metrics_data and isinstance(metrics_data["metrics"], dict):
                api_metrics = metrics_data["metrics"]
                
                # Extract bandwidth metrics from API format
                self._save_api_bandwidth_metrics(node_id, api_metrics, timestamp)
                
                # Extract member/protocol metrics from API format
                self._save_api_member_metrics(node_id, api_metrics, timestamp)
                
                # Save protocol statistics
                self._save_api_protocol_metrics(node_id, api_metrics, timestamp)
            
            # Also save a comprehensive report file
            report_dir = os.path.join(self.metrics_dir, "reports")
            os.makedirs(report_dir, exist_ok=True)
            report_file = os.path.join(report_dir, f"{node_id.replace(':', '_')}-{timestamp}.json")
            
            with open(report_file, 'w') as f:
                json.dump({
                    "timestamp": timestamp,
                    "node_id": node_id,
                    "raw_metrics": metrics_data,
                    "processed_at": datetime.now().isoformat()
                }, f, indent=2)
            
            logger.info(f"✅ Saved comprehensive report to {report_file}")
            self.files_written += 1
            
            logger.info(f"📊 METRICS SAVE COMPLETE - Total files written: {self.files_written}")
            
        except Exception as e:
            logger.error(f"❌ Error saving metrics data for {node_id}: {e}", exc_info=True)
            self._save_error_info(node_id, metrics_data, timestamp, str(e))

    def _save_api_bandwidth_metrics(self, node_id: str, api_metrics: Dict[str, Any], timestamp: str) -> None:
        """Save bandwidth metrics from API format."""
        try:
            bandwidth_file = os.path.join(self.metrics_dir, "bandwidth", f"{node_id.replace(':', '_')}-{timestamp}.csv")
            os.makedirs(os.path.dirname(bandwidth_file), exist_ok=True)
            
            with open(bandwidth_file, 'w', newline='') as f:
                f.write("Metric,Value,Unit\n")
                
                # Extract bandwidth-related metrics
                if "bandwidth_bytes" in api_metrics:
                    bandwidth_bytes = api_metrics["bandwidth_bytes"]
                    if isinstance(bandwidth_bytes, dict) and "counter" in bandwidth_bytes:
                        f.write(f"total_bytes,{bandwidth_bytes['counter']},bytes\n")
                
                if "bandwidth_rate" in api_metrics:
                    bandwidth_rate = api_metrics["bandwidth_rate"]
                    if isinstance(bandwidth_rate, dict) and "gauge" in bandwidth_rate:
                        f.write(f"current_rate,{bandwidth_rate['gauge']},bytes_per_sec\n")
                
                # Extract message counts
                if "message_received" in api_metrics:
                    msg_received = api_metrics["message_received"]
                    if isinstance(msg_received, dict) and "counter" in msg_received:
                        f.write(f"messages_received,{msg_received['counter']},count\n")
                
                # Extract RTT statistics
                if "peer_rtt" in api_metrics:
                    rtt_data = api_metrics["peer_rtt"]
                    if isinstance(rtt_data, dict) and "histogram" in rtt_data:
                        histogram = rtt_data["histogram"]
                        for key, value in histogram.items():
                            f.write(f"rtt_{key},{value},ms\n")
            
            logger.info(f"✅ Saved API bandwidth metrics to {bandwidth_file}")
            self.files_written += 1
            
        except Exception as e:
            logger.error(f"Error saving API bandwidth metrics: {e}")

    def _save_api_member_metrics(self, node_id: str, api_metrics: Dict[str, Any], timestamp: str) -> None:
        """Save member/protocol metrics from API format."""
        try:
            members_file = os.path.join(self.metrics_dir, "members", f"{node_id.replace(':', '_')}-{timestamp}.csv")
            os.makedirs(os.path.dirname(members_file), exist_ok=True)
            
            with open(members_file, 'w', newline='') as f:
                f.write("Metric,Value,Type\n")
                
                # Extract member count
                if "member_count" in api_metrics:
                    member_count = api_metrics["member_count"]
                    if isinstance(member_count, dict) and "gauge" in member_count:
                        f.write(f"total_members,{member_count['gauge']},count\n")
                
                # Extract awareness metrics
                if "peer_awareness" in api_metrics:
                    awareness = api_metrics["peer_awareness"]
                    if isinstance(awareness, dict) and "gauge" in awareness:
                        f.write(f"peer_awareness,{awareness['gauge']},level\n")
                
                # Extract probe metrics
                if "probe_count" in api_metrics:
                    probe_count = api_metrics["probe_count"]
                    if isinstance(probe_count, dict) and "gauge" in probe_count:
                        f.write(f"probe_count,{probe_count['gauge']},count\n")
                
                if "probe_result" in api_metrics:
                    probe_result = api_metrics["probe_result"]
                    if isinstance(probe_result, dict) and "counter" in probe_result:
                        f.write(f"total_probes,{probe_result['counter']},count\n")
            
            logger.info(f"✅ Saved API member metrics to {members_file}")
            self.files_written += 1
            
        except Exception as e:
            logger.error(f"Error saving API member metrics: {e}")

    def _save_api_protocol_metrics(self, node_id: str, api_metrics: Dict[str, Any], timestamp: str) -> None:
        """Save protocol-specific metrics from API format."""
        try:
            protocol_file = os.path.join(self.metrics_dir, "reports", f"{node_id.replace(':', '_')}-protocol-{timestamp}.csv")
            os.makedirs(os.path.dirname(protocol_file), exist_ok=True)
            
            with open(protocol_file, 'w', newline='') as f:
                f.write("Metric,Value,Unit\n")
                
                # Extract protocol timing
                if "protocol_period" in api_metrics:
                    period = api_metrics["protocol_period"]
                    if isinstance(period, dict) and "gauge" in period:
                        f.write(f"protocol_period,{period['gauge']},seconds\n")
                
                if "ping_timeout" in api_metrics:
                    timeout = api_metrics["ping_timeout"]
                    if isinstance(timeout, dict) and "gauge" in timeout:
                        f.write(f"ping_timeout,{timeout['gauge']},seconds\n")
                
                # Extract event counts
                if "ping" in api_metrics and "events" in api_metrics["ping"]:
                    ping_events = api_metrics["ping"]["events"]
                    for event, count in ping_events.items():
                        f.write(f"ping_{event},{count},count\n")
                
                if "node_event" in api_metrics and "events" in api_metrics["node_event"]:
                    node_events = api_metrics["node_event"]["events"]
                    for event, count in node_events.items():
                        f.write(f"node_{event},{count},count\n")
            
            logger.info(f"✅ Saved API protocol metrics to {protocol_file}")
            self.files_written += 1
            
        except Exception as e:
            logger.error(f"Error saving API protocol metrics: {e}")

    def _save_error_info(self, node_id: str, metrics_data: Dict[str, Any], timestamp: str, error_msg: str) -> None:
        """Save error information for debugging."""
        try:
            error_dir = os.path.join(self.metrics_dir, "errors")
            os.makedirs(error_dir, exist_ok=True)
            error_file = os.path.join(error_dir, f"{node_id.replace(':', '_')}-{timestamp}-error.txt")
            with open(error_file, 'w') as f:
                f.write(f"Error saving metrics: {error_msg}\n\n")
                f.write(f"Metrics data: {json.dumps(metrics_data, indent=2)}")
            logger.info(f"Saved error information to {error_file}")
        except Exception as inner_e:
            logger.error(f"Failed to save error information: {inner_e}")


class APIMetricsCLI:
    """
    CLI for interacting with the SWIM P2P Metrics API with correct endpoints.
    
    This version uses the correct API endpoints to fetch metrics.
    """

    def __init__(self, api_url: str, metrics_dir: Optional[str] = None):
        """
        Initialize the metrics API CLI.
        
        Args:
            api_url: URL of the metrics API server
            metrics_dir: Optional directory to save metrics data
        """
        self.api_url = api_url
        self.metrics_dir = metrics_dir
        self.update_interval = 2.0  # seconds
        self.running = False
        self.session = None
        
        # Create metrics file handler if metrics_dir is provided
        self.file_handler = MetricsFileHandler(metrics_dir) if metrics_dir else None

    async def run(self) -> None:
        """Run the CLI with direct HTTP polling."""
        self.running = True
        
        try:
            self.session = aiohttp.ClientSession()
            
            # Test HTTP connection first
            await self._test_http_connection()
            
            # Start polling loop
            poll_task = asyncio.create_task(self._polling_loop())
            
            try:
                # Run until interrupted
                while self.running:
                    await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
            finally:
                # Clean up
                self.running = False
                poll_task.cancel()
                try:
                    await poll_task
                except asyncio.CancelledError:
                    pass
                
                if self.session:
                    await self.session.close()
                    
        except Exception as e:
            logger.error(f"Error in API CLI: {e}", exc_info=True)

    async def _test_http_connection(self) -> None:
        """Test HTTP connection to the API."""
        try:
            async with self.session.get(f"{self.api_url}/api/nodes") as response:
                if response.status == 200:
                    nodes = await response.json()
                    logger.info(f"✅ HTTP API connection successful. Found {len(nodes)} nodes.")
                else:
                    logger.error(f"❌ HTTP API returned status {response.status}")
                    raise Exception(f"HTTP API failed with status {response.status}")
        except Exception as e:
            logger.error(f"❌ HTTP connection test failed: {e}")
            raise

    async def _polling_loop(self) -> None:
        """Periodically poll for metrics via HTTP."""
        try:
            while self.running:
                try:
                    # Get all nodes
                    async with self.session.get(f"{self.api_url}/api/nodes") as response:
                        if response.status == 200:
                            nodes = await response.json()
                            
                            # Get metrics for the local node
                            # The API doesn't support per-node metrics endpoints, so we use the main metrics endpoint
                            try:
                                async with self.session.get(f"{self.api_url}/api/metrics") as metrics_response:
                                    if metrics_response.status == 200:
                                        metrics_data = await metrics_response.json()
                                        
                                        # Process and save the metrics for the local node
                                        # We'll use the first node in the list as the local node ID
                                        if nodes:
                                            local_node = nodes[0]
                                            await self._handle_node_metrics(local_node, metrics_data)
                                    else:
                                        logger.warning(f"Failed to get metrics: {metrics_response.status}")
                            except Exception as metrics_error:
                                logger.error(f"Error getting metrics: {metrics_error}")
                    
                    # Wait for next update
                    await asyncio.sleep(self.update_interval)
                    
                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    await asyncio.sleep(self.update_interval)
                    
        except asyncio.CancelledError:
            logger.debug("Polling loop cancelled")

    async def _handle_node_metrics(self, node_addr: str, metrics: Dict[str, Any]) -> None:
        """Handle node metrics and save them."""
        try:
            logger.info(f"📊 Received metrics for {node_addr}")
            
            # Display metrics
            self._display_node_metrics(node_addr, metrics)
            
            # Save metrics if file handler is available
            if self.file_handler:
                # Create a properly formatted metrics structure
                formatted_metrics = {
                    "timestamp": time.time(),
                    "node_id": node_addr,
                    "metrics": metrics
                }
                self.file_handler.save_metrics(node_addr, formatted_metrics)
            
        except Exception as e:
            logger.error(f"Error handling node metrics: {e}", exc_info=True)

    def _display_node_metrics(self, node_addr: str, metrics: Dict[str, Any]) -> None:
        """Display metrics for a node."""
        print(f"\n=== 📊 Node Metrics: {node_addr} ===")
        
        # Display bandwidth metrics
        if "bandwidth_rate" in metrics:
            rate_data = metrics["bandwidth_rate"]
            if isinstance(rate_data, dict) and "gauge" in rate_data:
                print(f"📈 Bandwidth Rate: {rate_data['gauge']:.2f} bytes/s")
        
        if "bandwidth_bytes" in metrics:
            bytes_data = metrics["bandwidth_bytes"]
            if isinstance(bytes_data, dict) and "counter" in bytes_data:
                print(f"📊 Total Bandwidth: {bytes_data['counter']} bytes")
        
        # Display member information
        if "member_count" in metrics:
            member_data = metrics["member_count"]
            if isinstance(member_data, dict) and "gauge" in member_data:
                print(f"👥 Member Count: {member_data['gauge']}")
        
        # Display protocol metrics
        if "protocol_period" in metrics:
            period_data = metrics["protocol_period"]
            if isinstance(period_data, dict) and "gauge" in period_data:
                print(f"⏱️ Protocol Period: {period_data['gauge']:.3f}s")


async def run_api_cli(api_url: str, refresh_interval: float, metrics_dir: Optional[str] = None) -> None:
    """Run the metrics CLI using the metrics API."""
    try:
        cli = APIMetricsCLI(api_url, metrics_dir)
        cli.update_interval = refresh_interval
        
        await cli.run()
    except Exception as e:
        logger.error(f"Error in API CLI: {e}", exc_info=True)
        print(f"Error in API CLI: {e}")


async def run_cli_with_node(addr_str: str, refresh_interval: float, metrics_dir: Optional[str] = None, use_api: bool = False, api_port: int = DEFAULT_API_PORT) -> None:
    """Run the metrics CLI with a connected node."""
    try:
        # Import the connect_to_node function
        from swim.main import connect_to_node
        
        # Connect to the node
        logger.info(f"Connecting to node at {addr_str}...")
        node = await connect_to_node(addr_str)
        logger.info(f"Connected to node at {addr_str}")
        
        if use_api:
            try:
                from swim.metrics.api.integration import setup_metrics_api
                
                # Extract host and port from addr_str
                host, port_str = addr_str.split(':')
                api_host = host
                
                # Set up the metrics API
                logger.info(f"Setting up metrics API on {api_host}:{api_port}...")
                integration = setup_metrics_api(node, api_host, api_port)
                logger.info(f"Metrics API set up on {api_host}:{api_port}")
                
                # Display metrics directory if specified
                if metrics_dir:
                    print(f"📁 Metrics will be saved to {os.path.abspath(metrics_dir)}")
                
                # Wait a moment for the server to fully start
                await asyncio.sleep(2)
                
                # Run the API CLI
                api_url = f"http://{api_host}:{api_port}"
                await run_api_cli(api_url, refresh_interval, metrics_dir)
                
                # Clean up
                integration.stop()
            except ImportError as e:
                logger.error(f"Could not import metrics API integration: {e}")
                print(f"Error: Could not import metrics API integration: {e}")
        
        await node.stop()
    except Exception as e:
        logger.error(f"Error connecting to node: {e}", exc_info=True)
        print(f"Error connecting to node: {e}")


def main() -> None:
    """Main entry point for the metrics CLI."""
    parser = argparse.ArgumentParser(description="SWIM Protocol Metrics CLI - API Endpoint Fix Version")
    parser.add_argument("--connect", help="Connect to a running node at the specified address (e.g., 127.0.0.1:8000)")
    parser.add_argument("--metrics-dir", default="./metrics_data", help="Directory to save metrics data")
    parser.add_argument("--no-save", action="store_true", help="Don't save metrics data to files")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--use-api", action="store_true", help="Use the metrics API")
    parser.add_argument("--api-port", type=int, default=DEFAULT_API_PORT, help=f"Port for the metrics API server (default: {DEFAULT_API_PORT})")
    parser.add_argument("--refresh", type=float, default=2.0, help="Refresh interval in seconds")

    args = parser.parse_args()

    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # Determine metrics directory
    metrics_dir = None if args.no_save else args.metrics_dir

    if args.connect:
        # Connect to a running node
        try:
            asyncio.run(run_cli_with_node(args.connect, args.refresh, metrics_dir, args.use_api, args.api_port))
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            print(f"Unhandled exception: {e}")
    else:
        print("Please specify --connect with a node address")


if __name__ == "__main__":
    main()