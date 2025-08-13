"""
Unit tests for the gossip disseminator with push-pull sync.
"""

import pytest
import asyncio
import json
import time
from unittest.mock import MagicMock, AsyncMock
from swim.protocol.disseminator import GossipService
from swim.protocol.member import MemberList, MemberState
from swim.utils.serialization import serialize_message, deserialize_message


@pytest.fixture
def mock_transport():
    """Create a mock transport for testing."""
    transport = MagicMock()
    transport.send = AsyncMock()
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
def gossip_service(mock_transport, member_list):
    """Create a gossip service with mock transport and member list."""
    config = {
        "GOSSIP_FANOUT": 2,
        "FULL_SYNC_INTERVAL": 30.0,
        "PUSH_PULL_SYNC_ENABLED": True,
        "PUSH_PULL_SYNC_PROBABILITY": 1.0  # Always initiate for testing
    }
    return GossipService(transport=mock_transport, members=member_list, config=config)


@pytest.mark.asyncio
async def test_send_heartbeat(gossip_service, mock_transport, member_list):
    """Test sending heartbeat with piggybacked membership digest."""
    # Execute send heartbeat
    await gossip_service.send_heartbeat()
    
    # Verify transport was called to send messages
    assert mock_transport.send.call_count >= gossip_service.config["GOSSIP_FANOUT"]
    
    # Verify message content
    call_args = mock_transport.send.call_args_list[0]
    msg, addr = call_args[0]
    
    # Parse the message
    msg_data = deserialize_message(msg)
    
    # Check message structure
    assert "type" in msg_data
    assert msg_data["type"] == "HEARTBEAT"
    assert "from" in msg_data
    assert msg_data["from"] == "127.0.0.1:8000"  # Self address
    assert "digest" in msg_data
    assert isinstance(msg_data["digest"], dict)
    assert "entries" in msg_data["digest"]
    assert "version" in msg_data["digest"]
    
    # Check digest contains all members
    assert len(msg_data["digest"]["entries"]) == 3  # Self + 2 members


@pytest.mark.asyncio
async def test_handle_heartbeat(gossip_service, member_list):
    """Test handling a heartbeat message with membership digest."""
    # Create a heartbeat message from a new node with its own view
    peer_addr = ("127.0.0.1", 8003)
    
    # This peer knows about a node that our member_list doesn't
    heartbeat_msg = {
        "type": "HEARTBEAT",
        "from": "127.0.0.1:8003",
        "digest": {
            "version": 3,
            "entries": [
                {"addr": "127.0.0.1:8003", "state": "ALIVE", "incarnation": 1},
                {"addr": "127.0.0.1:8004", "state": "ALIVE", "incarnation": 1},
                {"addr": "127.0.0.1:8001", "state": "SUSPECT", "incarnation": 2}  # Conflict with our view
            ],
            "is_full": True
        },
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Encode the message
    encoded_msg = serialize_message(heartbeat_msg)
    
    # Handle the message
    await gossip_service.handle_message(peer_addr, encoded_msg)
    
    # Verify the peer was added to our member list
    assert member_list.get_member(peer_addr) is not None
    
    # Verify the new node was added
    new_node_addr = ("127.0.0.1", 8004)
    assert member_list.get_member(new_node_addr) is not None
    
    # Verify the conflict was resolved (higher incarnation wins)
    conflict_addr = ("127.0.0.1", 8001)
    assert member_list.get_member(conflict_addr).state == MemberState.SUSPECT
    
    # Verify the known version was updated
    assert gossip_service._known_versions.get(peer_addr) == 3


@pytest.mark.asyncio
async def test_push_pull_sync(gossip_service, mock_transport, member_list):
    """Test push-pull synchronization."""
    # Force a full sync
    gossip_service._last_full_sync = 0
    
    # Execute send heartbeat which should trigger push-pull
    await gossip_service.send_heartbeat()
    
    # Verify sync request was sent
    sync_req_sent = False
    for call in mock_transport.send.call_args_list:
        msg, _ = call[0]
        msg_data = deserialize_message(msg)
        if msg_data.get("type") == "SYNC-REQ":
            sync_req_sent = True
            break
    
    assert sync_req_sent, "No SYNC-REQ message was sent"


@pytest.mark.asyncio
async def test_handle_sync_req(gossip_service, mock_transport):
    """Test handling a sync request."""
    from_addr = ("127.0.0.1", 8001)
    sync_req_msg = {
        "type": "SYNC-REQ",
        "from": "127.0.0.1:8001",
        "id": "test123",
        "known_version": 0,  # Request full sync
        "timestamp": time.time()
    }
    
    # Handle the sync request
    await gossip_service._handle_sync_req(from_addr, sync_req_msg)
    
    # Verify a sync response was sent
    mock_transport.send.assert_called_once()
    
    # Check the message content
    call_args = mock_transport.send.call_args
    serialized_msg, addr = call_args[0]
    
    # Deserialize and check
    msg = deserialize_message(serialized_msg)
    
    assert msg["type"] == "SYNC-RESP"
    assert "digest" in msg
    assert addr == from_addr


@pytest.mark.asyncio
async def test_handle_sync_resp(gossip_service, member_list):
    """Test handling a sync response."""
    from_addr = ("127.0.0.1", 8003)
    
    # Create a sync response with a new member
    sync_resp_msg = {
        "type": "SYNC-RESP",
        "from": "127.0.0.1:8003",
        "id": "test123",
        "digest": {
            "version": 5,
            "entries": [
                {"addr": "127.0.0.1:8003", "state": "ALIVE", "incarnation": 1},
                {"addr": "127.0.0.1:8005", "state": "ALIVE", "incarnation": 1}  # New member
            ],
            "is_full": True
        },
        "timestamp": time.time()
    }
    
    # Handle the sync response
    await gossip_service._handle_sync_resp(from_addr, sync_resp_msg)
    
    # Verify the new member was added
    new_member_addr = ("127.0.0.1", 8005)
    assert member_list.get_member(new_member_addr) is not None
    
    # Verify the known version was updated
    assert gossip_service._known_versions.get(from_addr) == 5


@pytest.mark.asyncio
async def test_calculate_fanout(gossip_service, member_list):
    """Test adaptive fanout calculation based on cluster size."""
    # Default fanout for small cluster
    fanout = gossip_service._calculate_fanout()
    assert fanout == gossip_service.config["GOSSIP_FANOUT"]
    
    # Add more members to simulate a larger cluster
    for port in range(8003, 8020):
        member_list.add_member(("127.0.0.1", port))
    
    # Recalculate fanout
    fanout = gossip_service._calculate_fanout()
    
    # Should be larger than the default for a larger cluster
    assert fanout >= gossip_service.config["GOSSIP_FANOUT"]