"""
Unit tests for network utilities.
"""

import pytest
import socket
import ipaddress
from unittest.mock import patch, MagicMock
from swim.utils.network import (
    get_local_ip, get_available_port, get_network_interfaces,
    get_mac_address, is_interface_up, ping, detect_network_type,
    is_private_ip, format_addr, parse_addr
)


def test_get_local_ip():
    """Test getting local IP address."""
    # Mock socket to return a specific IP
    with patch('socket.socket') as mock_socket:
        mock_instance = MagicMock()
        mock_socket.return_value = mock_instance
        mock_instance.getsockname.return_value = ('192.168.1.100', 12345)
        
        ip = get_local_ip()
        assert ip == '192.168.1.100'
        
        # Verify socket was created and connected
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_instance.connect.assert_called_once_with(('8.8.8.8', 80))


def test_get_local_ip_fallback():
    """Test getting local IP address with fallback."""
    # Mock socket to raise an exception
    with patch('socket.socket') as mock_socket:
        mock_instance = MagicMock()
        mock_socket.return_value = mock_instance
        mock_instance.connect.side_effect = Exception("Connection failed")
        
        ip = get_local_ip()
        assert ip == '127.0.0.1'  # Should fall back to localhost


def test_get_available_port():
    """Test finding an available port."""
    # Mock socket.connect_ex to simulate ports 8000-8002 as in use, 8003 as available
    with patch('socket.socket') as mock_socket:
        mock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_instance
        
        # Simulate ports 8000-8002 as in use (return 0), 8003 as available (return non-zero)
        mock_instance.connect_ex.side_effect = [0, 0, 0, 1]
        
        port = get_available_port(8000, 8010)
        assert port == 8003
        
        # Verify connect_ex was called with the right addresses
        assert mock_instance.connect_ex.call_count == 4
        mock_instance.connect_ex.assert_any_call(('localhost', 8000))
        mock_instance.connect_ex.assert_any_call(('localhost', 8001))
        mock_instance.connect_ex.assert_any_call(('localhost', 8002))
        mock_instance.connect_ex.assert_any_call(('localhost', 8003))


def test_get_available_port_none_available():
    """Test finding an available port when none are available."""
    # Mock socket.connect_ex to simulate all ports as in use
    with patch('socket.socket') as mock_socket:
        mock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_instance
        
        # Simulate all ports as in use (return 0)
        mock_instance.connect_ex.return_value = 0
        
        with pytest.raises(RuntimeError, match="No available ports in range"):
            get_available_port(8000, 8005)
        
        # Verify connect_ex was called for each port
        assert mock_instance.connect_ex.call_count == 6  # 8000-8005 inclusive


def test_is_private_ip():
    """Test checking if an IP is private."""
    # Private IPs
    assert is_private_ip('192.168.1.1') is True
    assert is_private_ip('10.0.0.1') is True
    assert is_private_ip('172.16.0.1') is True
    
    # Public IPs
    assert is_private_ip('8.8.8.8') is False
    assert is_private_ip('203.0.113.1') is False
    
    # Invalid IP
    assert is_private_ip('not-an-ip') is False


def test_format_addr():
    """Test formatting an address tuple."""
    addr = ('192.168.1.1', 8000)
    formatted = format_addr(addr)
    assert formatted == '192.168.1.1:8000'


def test_parse_addr():
    """Test parsing an address string."""
    addr_str = '192.168.1.1:8000'
    addr = parse_addr(addr_str)
    assert addr == ('192.168.1.1', 8000)


def test_parse_addr_invalid_format():
    """Test parsing an invalid address string."""
    with pytest.raises(ValueError, match="Invalid address format"):
        parse_addr('192.168.1.1')


def test_parse_addr_invalid_port():
    """Test parsing an address with invalid port."""
    with pytest.raises(ValueError, match="Invalid port in address"):
        parse_addr('192.168.1.1:port')


@patch('subprocess.check_output')
def test_ping(mock_check_output):
    """Test pinging a host."""
    # Mock subprocess to return a successful ping result
    mock_check_output.return_value = b"64 bytes from 8.8.8.8: icmp_seq=1 ttl=56 time=15.6 ms"
    
    rtt = ping('8.8.8.8')
    assert rtt is not None
    assert isinstance(rtt, float)
    assert rtt == 0.0156  # 15.6 ms converted to seconds


@patch('subprocess.check_output')
def test_ping_failure(mock_check_output):
    """Test pinging a host that fails."""
    # Mock subprocess to raise an exception
    mock_check_output.side_effect = Exception("Ping failed")
    
    rtt = ping('8.8.8.8')
    assert rtt is None


@patch('swim.utils.network.ping')
def test_detect_network_type(mock_ping):
    """Test detecting network type."""
    # Mock ping to return fast RTTs
    mock_ping.return_value = 0.01  # 10ms
    
    network_type = detect_network_type()
    assert network_type == "good"
    
    # Mock ping to return slow RTTs
    mock_ping.return_value = 0.2  # 200ms
    
    network_type = detect_network_type()
    assert network_type == "high_latency"
    
    # Mock ping to return None (failure)
    mock_ping.return_value = None
    
    network_type = detect_network_type()
    assert network_type == "unknown"


@patch('socket.if_nameindex')
@patch('socket.gethostbyname')
@patch('socket.gethostname')
@patch('swim.utils.network.get_mac_address')
@patch('swim.utils.network.is_interface_up')
def test_get_network_interfaces(mock_is_up, mock_get_mac, mock_hostname, mock_gethostbyname, mock_if_nameindex):
    """Test getting network interfaces."""
    # Mock interface data
    mock_if_nameindex.return_value = [(1, 'eth0'), (2, 'wlan0')]
    mock_hostname.return_value = 'testhost'
    mock_gethostbyname.return_value = '192.168.1.100'
    mock_get_mac.return_value = '00:11:22:33:44:55'
    mock_is_up.return_value = True
    
    interfaces = get_network_interfaces()
    
    assert len(interfaces) == 2
    assert 'eth0' in interfaces
    assert 'wlan0' in interfaces
    
    assert interfaces['eth0']['ip'] == '192.168.1.100'
    assert interfaces['eth0']['mac'] == '00:11:22:33:44:55'
    assert interfaces['eth0']['is_up'] is True


@patch('platform.system')
@patch('subprocess.check_output')
def test_get_mac_address_linux(mock_check_output, mock_system):
    """Test getting MAC address on Linux."""
    # Mock platform to return Linux
    mock_system.return_value = "Linux"
    
    # Mock ifconfig output
    mock_check_output.return_value = b"""
    eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
            inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255
            inet6 fe80::1234:5678:9abc:def0  prefixlen 64  scopeid 0x20<link>
            ether 00:11:22:33:44:55  txqueuelen 1000  (Ethernet)
    """
    
    mac = get_mac_address('eth0')
    assert mac == '00:11:22:33:44:55'


@patch('platform.system')
@patch('subprocess.check_output')
def test_get_mac_address_windows(mock_check_output, mock_system):
    """Test getting MAC address on Windows."""
    # Mock platform to return Windows
    mock_system.return_value = "Windows"
    
    # Mock ipconfig output
    mock_check_output.return_value = b"""
    Ethernet adapter eth0:
       Connection-specific DNS Suffix  . : example.com
       Physical Address. . . . . . . . . : 00-11-22-33-44-55
       DHCP Enabled. . . . . . . . . . . : Yes
    """
    
    mac = get_mac_address('eth0')
    assert mac == '00-11-22-33-44-55'


@patch('platform.system')
@patch('subprocess.check_output')
def test_is_interface_up_linux(mock_check_output, mock_system):
    """Test checking if interface is up on Linux."""
    # Mock platform to return Linux
    mock_system.return_value = "Linux"
    
    # Mock ifconfig output for UP interface
    mock_check_output.return_value = b"""
    eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
    """
    
    assert is_interface_up('eth0') is True
    
    # Mock ifconfig output for DOWN interface
    mock_check_output.return_value = b"""
    eth0: flags=4099<BROADCAST,MULTICAST>  mtu 1500
    """
    
    assert is_interface_up('eth0') is False