"""
Unit tests for the failure detector with adaptive timeouts.
"""

import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch, AsyncMock
from swim.protocol.failure_detector import FailureDetector
from swim.protocol.member import MemberState, MemberList, Member
from swim.utils.serialization import serialize_message


@pytest.fixture
def mock_transport():
    """Create a mock transport for testing."""
    transport = MagicMock()
    transport.send = AsyncMock()
    transport.receive = AsyncMock()
    transport.local_address = ("127.0.0.1", 8000)
    return transport


@pytest.fixture
def member_list():
    """Create a member list with some test members."""
    self_addr = ("127.0.0.1", 8000)
    member_list = MemberList(self_addr)
    
    # Add some members
    member_list.add_member(("127.0.0.1", 8001))
    member_list.add_member(("127.0.0.1", 8002))
    
    return member_list


@pytest.fixture
def failure_detector(mock_transport, member_list):
    """Create a failure detector with mock transport and member list."""
    config = {
        "PING_TIMEOUT_BASE": 0.5,
        "PING_TIMEOUT_MIN": 0.2,
        "PING_TIMEOUT_MAX": 2.0,
        "PING_RETRIES": 2,
        "INDIRECT_PROBE_COUNT": 2,
        "ADAPTIVE_TIMEOUT_FACTOR": 2.0
    }
    return FailureDetector(transport=mock_transport, members=member_list, config=config)


@pytest.mark.asyncio
async def test_ping_success(failure_detector, mock_transport, member_list):
    """Test successful ping with response."""
    target_addr = ("127.0.0.1", 8001)
    
    # Mock successful response
    mock_transport.receive.return_value = (
        serialize_message({
            "type": "PONG", 
            "from": "127.0.0.1:8001",
            "id": "test123",
            "timestamp": time.time()
        }),
        target_addr
    )
    
    # Capture initial heartbeat
    initial_heartbeat = member_list.get_member(target_addr).last_heartbeat
    
    # Execute ping
    result = await failure_detector.ping(target_addr)
    
    # Verify results
    assert result is True
    mock_transport.send.assert_called_once()
    assert member_list.get_member(target_addr).state == MemberState.ALIVE
    assert member_list.get_member(target_addr).last_heartbeat > initial_heartbeat
    
    # Verify RTT was updated
    assert len(member_list.get_member(target_addr).rtt_history) > 0


@pytest.mark.asyncio
async def test_ping_timeout(failure_detector, mock_transport, member_list):
    """Test ping timeout with no response."""
    target_addr = ("127.0.0.1", 8001)
    
    # Mock timeout (no response)
    mock_transport.send.return_value = None
    mock_transport.receive.side_effect = asyncio.TimeoutError("Receive timeout")
    
    # Execute ping
    result = await failure_detector.ping(target_addr)
    
    # Verify results
    assert result is False
    mock_transport.send.assert_called()
    assert member_list.get_member(target_addr).state == MemberState.SUSPECT


@pytest.mark.asyncio
async def test_ping_retries(failure_detector, mock_transport, member_list):
    """Test that ping retries the configured number of times."""
    target_addr = ("127.0.0.1", 8001)
    
    # Mock timeout for all retries
    mock_transport.send.return_value = None
    mock_transport.receive.side_effect = asyncio.TimeoutError("Receive timeout")
    
    # Execute ping
    result = await failure_detector.ping(target_addr)
    
    # Verify results
    assert result is False
    assert mock_transport.send.call_count == failure_detector.config["PING_RETRIES"]
    assert member_list.get_member(target_addr).state == MemberState.SUSPECT


@pytest.mark.asyncio
async def test_adaptive_timeout_calculation(failure_detector, member_list):
    """Test adaptive timeout calculation based on RTT history."""
    target_addr = ("127.0.0.1", 8001)
    member = member_list.get_member(target_addr)
    
    # No RTT history yet, should use base timeout
    timeout = failure_detector._calculate_timeout(target_addr)
    assert timeout == failure_detector.config["PING_TIMEOUT_BASE"]
    
    # Add some RTT samples
    member.add_rtt_sample(0.1)
    member.add_rtt_sample(0.2)
    member.add_rtt_sample(0.3)
    
    # Calculate timeout again
    timeout = failure_detector._calculate_timeout(target_addr)
    
    # Should be based on 95th percentile RTT with safety factor
    expected = 0.3 * failure_detector.config["ADAPTIVE_TIMEOUT_FACTOR"]
    assert timeout == expected
    
    # Add an outlier
    member.add_rtt_sample(1.0)
    
    # Calculate timeout again
    timeout = failure_detector._calculate_timeout(target_addr)
    
    # Should be capped at max timeout
    assert timeout <= failure_detector.config["PING_TIMEOUT_MAX"]


@pytest.mark.asyncio
async def test_indirect_probe_success(failure_detector, mock_transport, member_list):
    """Test successful indirect probe where a helper responds."""
    target_addr = ("127.0.0.1", 8001)
    helper_addr = ("127.0.0.1", 8002)
    
    # Mark target as suspect first
    await member_list.mark_suspect(target_addr)
    
    # Mock helper response (successful probe)
    mock_transport.send.return_value = None
    mock_transport.receive.return_value = (
        serialize_message({
            "type": "PING-REQ-ACK",
            "from": "127.0.0.1:8002",
            "target": "127.0.0.1:8001",
            "status": "alive",
            "id": "test123",
            "rtt": 0.1
        }),
        helper_addr
    )
    
    # Execute indirect probe
    result = await failure_detector.indirect_probe(target_addr)
    
    # Verify results
    assert result is True
    assert mock_transport.send.call_count >= 1  # At least one helper contacted
    assert member_list.get_member(target_addr).state == MemberState.ALIVE


@pytest.mark.asyncio
async def test_indirect_probe_failure(failure_detector, mock_transport, member_list):
    """Test failed indirect probe where no helpers can reach the target."""
    target_addr = ("127.0.0.1", 8001)
    
    # Mark target as suspect first
    await member_list.mark_suspect(target_addr)
    
    # Mock helper responses (all failed probes)
    mock_transport.send.return_value = None
    mock_transport.receive.return_value = (
        serialize_message({
            "type": "PING-REQ-ACK",
            "from": "127.0.0.1:8002",
            "target": "127.0.0.1:8001",
            "status": "unreachable",
            "id": "test123"
        }),
        ("127.0.0.1", 8002)
    )
    
    # Execute indirect probe
    result = await failure_detector.indirect_probe(target_addr)
    
    # Verify results
    assert result is False
    assert mock_transport.send.call_count >= 1  # At least one helper contacted
    assert member_list.get_member(target_addr).state == MemberState.SUSPECT


@pytest.mark.asyncio
async def test_handle_ping(failure_detector, mock_transport):
    """Test handling a PING message."""
    from_addr = ("127.0.0.1", 8001)
    ping_msg = {
        "type": "PING",
        "from": "127.0.0.1:8001",
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Handle the ping
    await failure_detector.handle_ping(from_addr, ping_msg)
    
    # Verify a PONG was sent back
    mock_transport.send.assert_called_once()
    
    # Check the message content
    call_args = mock_transport.send.call_args
    serialized_msg, addr = call_args[0]
    
    # Deserialize and check
    from swim.utils.serialization import deserialize_message
    msg = deserialize_message(serialized_msg)
    
    assert msg["type"] == "PONG"
    assert msg["id"] == "test123"  # Should echo the original ID
    assert "timestamp" in msg
    assert "orig_timestamp" in msg
    assert addr == from_addr


@pytest.mark.asyncio
async def test_handle_ping_req(failure_detector, mock_transport):
    """Test handling a PING-REQ message."""
    from_addr = ("127.0.0.1", 8001)
    target_addr = ("127.0.0.1", 8002)
    ping_req_msg = {
        "type": "PING-REQ",
        "from": "127.0.0.1:8001",
        "target": "127.0.0.1:8002",
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Mock successful ping to target
    mock_transport.receive.return_value = (
        serialize_message({
            "type": "PONG",
            "from": "127.0.0.1:8002",
            "id": "test123"
        }),
        target_addr
    )
    
    # Handle the ping-req
    await failure_detector.handle_ping_req(from_addr, ping_req_msg)
    
    # Verify a PING was sent to the target
    assert mock_transport.send.call_count >= 1
    
    # First call should be to send PING to target
    first_call = mock_transport.send.call_args_list[0]
    serialized_msg, addr = first_call[0]
    
    # Deserialize and check
    from swim.utils.serialization import deserialize_message
    msg = deserialize_message(serialized_msg)
    
    assert msg["type"] == "PING"
    assert addr == target_addr
    
    # Second call should be to send ACK back to requester
    second_call = mock_transport.send.call_args_list[1]
    serialized_msg, addr = second_call[0]
    
    # Deserialize and check
    msg = deserialize_message(serialized_msg)
    
    assert msg["type"] == "PING-REQ-ACK"
    assert msg["status"] == "alive"
    assert addr == from_addr