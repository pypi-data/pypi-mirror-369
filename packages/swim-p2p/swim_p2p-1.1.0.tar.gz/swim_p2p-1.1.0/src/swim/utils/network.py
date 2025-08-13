"""
Network utilities for SWIM P2P.

This module provides functions for network interface discovery,
IP address and port utilities, and network condition detection.
Enhanced with production-ready port management for SWIM-ZMQ integration.
"""

import socket
import ipaddress
import platform
import subprocess
import re
import time
import logging
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass, field
from contextlib import contextmanager

logger = logging.getLogger(__name__)

def get_local_ip() -> str:
    """Get the local IP address.
    
    Returns:
        The local IP address as a string
    """
    # Create a socket to connect to an external server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't actually establish a connection
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"  # Fallback to localhost
    finally:
        s.close()
    return ip


def get_available_port(start_port: int = 8000, end_port: int = 9000) -> int:
    """Find an available port in the given range.
    
    Args:
        start_port: The start of the port range to check
        end_port: The end of the port range to check
        
    Returns:
        An available port number
        
    Raises:
        RuntimeError: If no available port is found in the range
    """
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            if result != 0:  # Port is available
                return port
    
    raise RuntimeError(f"No available ports in range {start_port}-{end_port}")


def get_network_interfaces() -> Dict[str, Dict[str, str]]:
    """Get information about all network interfaces.
    
    Returns:
        Dictionary mapping interface names to their properties
    """
    interfaces = {}
    
    # Get all network interfaces
    for interface_name in socket.if_nameindex():
        name = interface_name[1]
        try:
            # Get the IP address
            ip = socket.gethostbyname(socket.gethostname())
            interfaces[name] = {
                "ip": ip,
                "mac": get_mac_address(name),
                "is_up": is_interface_up(name)
            }
        except Exception:
            pass
    
    return interfaces


def get_mac_address(interface_name: str) -> str:
    """Get the MAC address of a network interface.
    
    Args:
        interface_name: Name of the network interface
        
    Returns:
        MAC address as a string
    """
    if platform.system() == "Windows":
        # Windows implementation
        output = subprocess.check_output("ipconfig /all").decode("utf-8")
        pattern = re.compile(f"{interface_name}.*?Physical Address.*?([0-9A-F]{{2}}(-[0-9A-F]{{2}}){{5}})", 
                            re.DOTALL | re.IGNORECASE)
        match = pattern.search(output)
        if match:
            return match.group(1)
        return "00-00-00-00-00-00"
    else:
        # Linux/Mac implementation
        try:
            output = subprocess.check_output(["ifconfig", interface_name]).decode("utf-8")
            pattern = re.compile(r"ether\s+([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})")
            match = pattern.search(output)
            if match:
                return match.group(1)
        except Exception:
            pass
        return "00:00:00:00:00:00"


def is_interface_up(interface_name: str) -> bool:
    """Check if a network interface is up.
    
    Args:
        interface_name: Name of the network interface
        
    Returns:
        True if the interface is up, False otherwise
    """
    if platform.system() == "Windows":
        # Windows implementation
        output = subprocess.check_output("ipconfig /all").decode("utf-8")
        return interface_name in output
    else:
        # Linux/Mac implementation
        try:
            output = subprocess.check_output(["ifconfig", interface_name]).decode("utf-8")
            return "UP" in output
        except Exception:
            return False


def ping(host: str, timeout: float = 1.0) -> Optional[float]:
    """Ping a host and return the round-trip time.
    
    Args:
        host: The host to ping
        timeout: Timeout in seconds
        
    Returns:
        Round-trip time in seconds, or None if the ping failed
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", "-W", str(int(timeout * 1000)), host]
    
    try:
        output = subprocess.check_output(command).decode("utf-8")
        pattern = re.compile(r"time=(\d+\.?\d*)\s*ms")
        match = pattern.search(output)
        if match:
            return float(match.group(1)) / 1000.0  # Convert ms to seconds
        return None
    except Exception:
        return None


def detect_network_type() -> str:
    """Detect the type of network connection.
    
    Returns:
        Network type as a string: "high_latency", "low_bandwidth", or "good"
    """
    # Ping a few well-known hosts
    hosts = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
    rtts = []
    
    for host in hosts:
        rtt = ping(host)
        if rtt is not None:
            rtts.append(rtt)
    
    if not rtts:
        return "unknown"
    
    avg_rtt = sum(rtts) / len(rtts)
    
    if avg_rtt > 0.1:  # 100ms
        return "high_latency"
    
    # TODO: Add bandwidth detection
    
    return "good"


def is_private_ip(ip: str) -> bool:
    """Check if an IP address is private.
    
    Args:
        ip: IP address to check
        
    Returns:
        True if the IP is private, False otherwise
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        
        # Handle special cases that ipaddress.is_private considers private
        # but are actually reserved for documentation/testing
        
        # TEST-NET ranges (RFC 5737)
        if ip.startswith('192.0.2.') or ip.startswith('198.51.100.') or ip.startswith('203.0.113.'):
            return False
        
        # Documentation range (RFC 6890)
        if ip.startswith('2001:db8:'):
            return False
            
        return ip_obj.is_private
    except ValueError:
        return False


def format_addr(addr: Tuple[str, int]) -> str:
    """Format an address tuple as a string.
    
    Args:
        addr: Address tuple (host, port)
        
    Returns:
        Formatted address string
    """
    return f"{addr[0]}:{addr[1]}"


def parse_addr(addr_str: str) -> Tuple[str, int]:
    """Parse an address string into a tuple.
    
    Args:
        addr_str: Address string in format "host:port"
        
    Returns:
        Address tuple (host, port)
        
    Raises:
        ValueError: If the address string is invalid
    """
    parts = addr_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid address format: {addr_str}")
    
    try:
        port = int(parts[1])
    except ValueError:
        raise ValueError(f"Invalid port in address: {addr_str}")
    
    return (parts[0], port)


# ============================================================================
# NEW PRODUCTION-READY PORT MANAGEMENT FEATURES
# ============================================================================

class PortValidationError(Exception):
    """Base class for port-related validation errors."""
    pass


class PortConflictError(PortValidationError):
    """Raised when port allocation fails due to conflicts."""
    pass


class PortExhaustionError(PortValidationError):
    """Raised when no ports are available in the specified range."""
    pass


@dataclass
class PortRange:
    """Defines a range of ports for allocation."""
    start: int
    end: int
    name: str
    
    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError(f"Invalid port range: {self.start}-{self.end}")
        if self.start < 1024:
            logger.warning(f"Port range {self.name} includes privileged ports (<1024)")
    
    def __contains__(self, port: int) -> bool:
        return self.start <= port <= self.end
    
    def size(self) -> int:
        return self.end - self.start + 1


@dataclass
class PortConfig:
    """Configuration for port allocation."""
    # Use field(default_factory=...) for mutable defaults
    swim_port_range: PortRange = field(default_factory=lambda: PortRange(8000, 8999, "SWIM"))
    zmq_port_range: PortRange = field(default_factory=lambda: PortRange(9000, 9999, "ZMQ"))
    bind_interface: str = "127.0.0.1"
    max_allocation_attempts: int = 100
    port_check_timeout: float = 1.0
    
    def get_default_zmq_port(self, swim_port: int) -> int:
        """Get default ZMQ port for given SWIM port using offset."""
        offset = self.zmq_port_range.start - self.swim_port_range.start
        return swim_port + offset


def check_port_available(host: str, port: int, timeout: float = 1.0) -> bool:
    """Enhanced port availability check with timeout.
    
    Args:
        host: Host to check port on
        port: Port number to check
        timeout: Timeout for the check
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.bind((host, port))
            return True
    except (OSError, socket.error) as e:
        logger.debug(f"Port {host}:{port} not available: {e}")
        return False


def find_available_ports(host: str, port_range: PortRange, count: int, 
                        max_attempts: int = 1000) -> List[int]:
    """Find multiple available ports in the specified range.
    
    Args:
        host: Host to check ports on
        port_range: Range of ports to search
        count: Number of ports needed
        max_attempts: Maximum attempts before giving up
        
    Returns:
        List of available port numbers
        
    Raises:
        PortExhaustionError: If not enough ports are available
    """
    available = []
    attempts = 0
    port = port_range.start
    
    while len(available) < count and attempts < max_attempts:
        if port > port_range.end:
            break
            
        if check_port_available(host, port):
            available.append(port)
        
        port += 1
        attempts += 1
    
    if len(available) < count:
        raise PortExhaustionError(
            f"Could not find {count} available ports in range "
            f"{port_range.start}-{port_range.end} after {attempts} attempts"
        )
    
    return available


class PortManager:
    """Production-ready port allocation manager for SWIM-ZMQ integration."""
    
    def __init__(self, config: Optional[PortConfig] = None):
        self.config = config or PortConfig()
        self.allocated_ports: Dict[str, Tuple[int, int]] = {}  # node_id -> (swim_port, zmq_port)
        self.port_mapping: Dict[int, int] = {}  # swim_port -> zmq_port
        
    def allocate_port_pair(self, node_id: str, host: Optional[str] = None) -> Tuple[int, int]:
        """Allocate a SWIM+ZMQ port pair for a node.
        
        Args:
            node_id: Unique identifier for the node
            host: Host to allocate ports on (defaults to config bind_interface)
            
        Returns:
            Tuple of (swim_port, zmq_port)
            
        Raises:
            PortConflictError: If ports are already allocated for this node
            PortExhaustionError: If no ports are available
        """
        if node_id in self.allocated_ports:
            raise PortConflictError(f"Ports already allocated for node {node_id}")
        
        host = host or self.config.bind_interface
        
        try:
            # Find available SWIM port
            swim_ports = find_available_ports(
                host, 
                self.config.swim_port_range, 
                1,
                self.config.max_allocation_attempts
            )
            swim_port = swim_ports[0]
            
            # Try default ZMQ port first
            zmq_port = self.config.get_default_zmq_port(swim_port)
            if not check_port_available(host, zmq_port, self.config.port_check_timeout):
                # Find alternative ZMQ port
                zmq_ports = find_available_ports(
                    host,
                    self.config.zmq_port_range,
                    1,
                    self.config.max_allocation_attempts
                )
                zmq_port = zmq_ports[0]
            
            # Reserve the ports
            self.allocated_ports[node_id] = (swim_port, zmq_port)
            self.port_mapping[swim_port] = zmq_port
            
            logger.info(f"PORT_MANAGER: Allocated ports for {node_id}: SWIM={swim_port}, ZMQ={zmq_port}")
            return swim_port, zmq_port
            
        except (PortExhaustionError, PortConflictError) as e:
            logger.error(f"PORT_MANAGER: Failed to allocate ports for {node_id}: {e}")
            raise
    
    def allocate_port_pairs(self, node_ids: List[str], host: Optional[str] = None) -> Dict[str, Tuple[int, int]]:
        """Allocate port pairs for multiple nodes efficiently.
        
        Args:
            node_ids: List of node identifiers
            host: Host to allocate ports on
            
        Returns:
            Dictionary mapping node_id to (swim_port, zmq_port)
        """
        host = host or self.config.bind_interface
        allocations = {}
        
        try:
            # Find all required ports at once to avoid conflicts
            swim_ports = find_available_ports(
                host,
                self.config.swim_port_range,
                len(node_ids),
                self.config.max_allocation_attempts
            )
            
            zmq_ports = find_available_ports(
                host,
                self.config.zmq_port_range,
                len(node_ids),
                self.config.max_allocation_attempts
            )
            
            # Allocate pairs
            for i, node_id in enumerate(node_ids):
                if node_id in self.allocated_ports:
                    raise PortConflictError(f"Ports already allocated for node {node_id}")
                
                swim_port = swim_ports[i]
                zmq_port = zmq_ports[i]
                
                self.allocated_ports[node_id] = (swim_port, zmq_port)
                self.port_mapping[swim_port] = zmq_port
                allocations[node_id] = (swim_port, zmq_port)
            
            logger.info(f"PORT_MANAGER: Allocated {len(allocations)} port pairs")
            return allocations
            
        except (PortExhaustionError, PortConflictError) as e:
            # Rollback any partial allocations
            for node_id in allocations:
                self.release_ports(node_id)
            logger.error(f"PORT_MANAGER: Failed to allocate port pairs: {e}")
            raise
    
    def release_ports(self, node_id: str):
        """Release allocated ports for a node.
        
        Args:
            node_id: Node identifier to release ports for
        """
        if node_id in self.allocated_ports:
            swim_port, zmq_port = self.allocated_ports[node_id]
            del self.allocated_ports[node_id]
            self.port_mapping.pop(swim_port, None)
            logger.info(f"PORT_MANAGER: Released ports for {node_id}: SWIM={swim_port}, ZMQ={zmq_port}")
    
    def get_zmq_port_for_swim(self, swim_port: int) -> Optional[int]:
        """Get ZMQ port for given SWIM port.
        
        Args:
            swim_port: SWIM port number
            
        Returns:
            Corresponding ZMQ port or None if not found
        """
        return self.port_mapping.get(swim_port)
    
    def swim_to_zmq_address(self, swim_addr: Tuple[str, int]) -> Optional[str]:
        """Convert SWIM address to ZMQ address using port mapping.
        
        Args:
            swim_addr: SWIM address tuple (host, port)
            
        Returns:
            ZMQ address string or None if mapping not found
        """
        zmq_port = self.get_zmq_port_for_swim(swim_addr[1])
        if zmq_port:
            return f"{swim_addr[0]}:{zmq_port}"
        return None
    
    def get_port_usage(self) -> Dict[str, Dict[str, int]]:
        """Get current port usage statistics.
        
        Returns:
            Dictionary with usage statistics for SWIM and ZMQ ports
        """
        return {
            "swim": {
                "allocated": len(self.allocated_ports),
                "available": self.config.swim_port_range.size() - len(self.allocated_ports),
                "range": f"{self.config.swim_port_range.start}-{self.config.swim_port_range.end}"
            },
            "zmq": {
                "allocated": len(self.allocated_ports),
                "available": self.config.zmq_port_range.size() - len(self.allocated_ports),
                "range": f"{self.config.zmq_port_range.start}-{self.config.zmq_port_range.end}"
            }
        }
    
    @contextmanager
    def port_reservation(self, node_id: str, host: Optional[str] = None):
        """Context manager for temporary port reservation.
        
        Args:
            node_id: Node identifier
            host: Host to allocate ports on
            
        Yields:
            Tuple of (swim_port, zmq_port)
        """
        swim_port, zmq_port = None, None
        try:
            swim_port, zmq_port = self.allocate_port_pair(node_id, host)
            yield swim_port, zmq_port
        finally:
            if swim_port and zmq_port:
                self.release_ports(node_id)


# Global port manager instance
_global_port_manager: Optional[PortManager] = None


def get_port_manager(config: Optional[PortConfig] = None) -> PortManager:
    """Get the global port manager instance.
    
    Args:
        config: Optional port configuration
        
    Returns:
        Global PortManager instance
    """
    global _global_port_manager
    if _global_port_manager is None:
        _global_port_manager = PortManager(config)
    return _global_port_manager


def set_port_manager(manager: PortManager):
    """Set a custom port manager instance.
    
    Args:
        manager: PortManager instance to use globally
    """
    global _global_port_manager
    _global_port_manager = manager
