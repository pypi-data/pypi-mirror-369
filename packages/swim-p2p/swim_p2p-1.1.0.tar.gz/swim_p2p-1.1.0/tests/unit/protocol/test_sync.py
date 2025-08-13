"""
Unit tests for the push-pull synchronization service.
"""

import pytest
import asyncio
import time
import uuid
from unittest.mock import MagicMock, AsyncMock, patch
from swim.protocol.sync import SyncService
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
def sync_service(mock_transport, member_list):
    """Create a sync service with mock transport and member list."""
    config = {
        "FULL_SYNC_INTERVAL": 0.5,  # Short interval for testing
        "SYNC_FANOUT": 2,
        "SYNC_TIMEOUT": 0.5
    }
    return SyncService(transport=mock_transport, members=member_list, config=config)


@pytest.mark.asyncio
async def test_sync_service_start_stop(sync_service):
    """Test starting and stopping the sync service."""
    # Start the service
    await sync_service.start()
    
    # Verify the service is running
    assert sync_service._running is True
    assert sync_service._sync_task is not None
    
    # Stop the service
    await sync_service.stop()
    
    # Verify the service is stopped
    assert sync_service._running is False
    assert sync_service._sync_task is None


@pytest.mark.asyncio
async def test_perform_full_sync(sync_service, mock_transport, member_list):
    """Test performing a full sync."""
    # Mock uuid.uuid4 to return a predictable value
    mock_uuid = "12345678-1234-5678-1234-567812345678"
    with patch('uuid.uuid4', return_value=uuid.UUID(mock_uuid)):
        # Execute full sync
        await sync_service._perform_full_sync()
        
        # Verify sync requests were sent
        assert mock_transport.send.call_count == sync_service.config["SYNC_FANOUT"]
        
        # Check message content
        call_args = mock_transport.send.call_args_list[0]
        serialized_msg, addr = call_args[0]
        
        # Deserialize and check
        msg = deserialize_message(serialized_msg)
        
        assert msg["type"] == "SYNC-REQ"
        assert msg["known_version"] == 0  # 0 indicates full sync
        assert msg["id"] == mock_uuid[:8]  # First 8 chars of UUID
        assert addr in [("127.0.0.1", 8001), ("127.0.0.1", 8002)]


@pytest.mark.asyncio
async def test_perform_incremental_sync(sync_service, mock_transport):
    """Test performing an incremental sync."""
    # Set a known version for a target
    target_addr = ("127.0.0.1", 8001)
    sync_service._known_versions[target_addr] = 5
    
    # Add the target to the member list to ensure it's selected
    member = sync_service.members.get_member(target_addr)
    if not member:
        sync_service.members.add_member(target_addr)
    
    # Mock get_random_members to ensure our target is selected
    with patch.object(sync_service.members, 'get_random_members') as mock_get_random:
        # Make sure our target is returned
        mock_get_random.return_value = [sync_service.members.get_member(target_addr)]
        
        # Mock uuid.uuid4 to return a predictable value
        mock_uuid = "12345678-1234-5678-1234-567812345678"
        with patch('uuid.uuid4', return_value=uuid.UUID(mock_uuid)):
            # Reset the transport mock to ensure we're only capturing calls from this test
            mock_transport.reset_mock()
            
            # Execute incremental sync
            await sync_service._perform_incremental_sync()
            
            # Verify a sync request was sent
            mock_transport.send.assert_called_once()
            
            # Check message content
            serialized_msg, addr = mock_transport.send.call_args[0]
            
            # Deserialize and check
            msg = deserialize_message(serialized_msg)
            
            assert msg["type"] == "SYNC-REQ"
            assert msg["known_version"] == 5  # Should use the known version we set
            assert msg["id"] == mock_uuid[:8]  # First 8 chars of UUID
            assert addr == target_addr


@pytest.mark.asyncio
async def test_handle_sync_req_full_sync(sync_service, mock_transport, member_list):
    """Test handling a full sync request."""
    from_addr = ("127.0.0.1", 8001)
    
    # Create a mock digest for the member list
    mock_digest = {
        "version": 10,
        "entries": [
            {"addr": "127.0.0.1:8000", "state": "ALIVE", "incarnation": 1}
        ],
        "is_full": True
    }
    
    # Mock the serialize_digest method
    with patch.object(member_list, 'serialize_digest', return_value=mock_digest):
        # Test full sync request
        full_sync_req = {
            "type": "SYNC-REQ",
            "from": "127.0.0.1:8001",
            "id": "test123",
            "known_version": 0,  # 0 indicates full sync
            "timestamp": time.time()
        }
        
        # Handle the request
        await sync_service._handle_sync_req(from_addr, full_sync_req)
        
        # Verify a response was sent
        mock_transport.send.assert_called_once()
        
        # Check message content
        serialized_msg, addr = mock_transport.send.call_args[0]
        
        # Deserialize and check
        msg = deserialize_message(serialized_msg)
        
        assert msg["type"] == "SYNC-RESP"
        assert msg["id"] == "test123"
        assert msg["digest"] == mock_digest
        assert addr == from_addr


@pytest.mark.asyncio
async def test_handle_sync_req_incremental_sync(sync_service, mock_transport, member_list):
    """Test handling an incremental sync request."""
    from_addr = ("127.0.0.1", 8001)
    
    # Create a mock digest for the member list
    mock_digest = {
        "version": 10,
        "entries": [
            {"addr": "127.0.0.1:8000", "state": "ALIVE", "incarnation": 1}
        ],
        "is_full": False
    }
    
    # Mock the serialize_digest method
    with patch.object(member_list, 'serialize_digest', return_value=mock_digest):
        # Test incremental sync request
        incremental_sync_req = {
            "type": "SYNC-REQ",
            "from": "127.0.0.1:8001",
            "id": "test456",
            "known_version": 5,  # Non-zero indicates incremental sync
            "timestamp": time.time()
        }
        
        # Handle the request
        await sync_service._handle_sync_req(from_addr, incremental_sync_req)
        
        # Verify a response was sent
        mock_transport.send.assert_called_once()
        
        # Check message content
        serialized_msg, addr = mock_transport.send.call_args[0]
        
        # Deserialize and check
        msg = deserialize_message(serialized_msg)
        
        assert msg["type"] == "SYNC-RESP"
        assert msg["id"] == "test456"
        assert msg["digest"] == mock_digest
        assert addr == from_addr
        
        # Verify serialize_digest was called with the correct parameters
        member_list.serialize_digest.assert_called_once_with(full=False, since_version=5)


@pytest.mark.asyncio
async def test_handle_sync_resp(sync_service, member_list):
    """Test handling a sync response."""
    from_addr = ("127.0.0.1", 8003)
    
    # Mock the merge_digest method
    with patch.object(member_list, 'merge_digest', AsyncMock()) as mock_merge_digest:
        # Create a sync response with a new member
        sync_resp = {
            "type": "SYNC-RESP",
            "from": "127.0.0.1:8003",
            "id": "test123",
            "digest": {
                "version": 10,
                "entries": [
                    {"addr": "127.0.0.1:8003", "state": "ALIVE", "incarnation": 1},
                    {"addr": "127.0.0.1:8004", "state": "ALIVE", "incarnation": 1}  # New member
                ],
                "is_full": True
            },
            "timestamp": time.time()
        }
        
        # Handle the response
        await sync_service._handle_sync_resp(from_addr, sync_resp)
        
        # Verify merge_digest was called with the correct digest
        mock_merge_digest.assert_called_once_with(sync_resp["digest"])
        
        # Verify the known version was updated
        assert sync_service._known_versions[from_addr] == 10
        
        # Verify statistics were updated
        assert sync_service._sync_successes == 1


@pytest.mark.asyncio
async def test_handle_sync_resp_without_digest(sync_service):
    """Test handling a sync response without a digest."""
    from_addr = ("127.0.0.1", 8003)
    
    # Create a sync response without a digest
    sync_resp = {
        "type": "SYNC-RESP",
        "from": "127.0.0.1:8003",
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Handle the response
    await sync_service._handle_sync_resp(from_addr, sync_resp)
    
    # Verify statistics were updated
    assert sync_service._sync_failures == 1
    assert sync_service._sync_successes == 0


@pytest.mark.asyncio
async def test_handle_message_sync_req(sync_service):
    """Test handling a SYNC-REQ message."""
    # Patch the _handle_sync_req method
    with patch.object(sync_service, '_handle_sync_req', AsyncMock()) as mock_handle_req:
        # Create a SYNC-REQ message
        from_addr = ("127.0.0.1", 8001)
        sync_req_msg = {
            "type": "SYNC-REQ",
            "from": "127.0.0.1:8001",
            "id": "test123",
            "known_version": 0
        }
        
        # Serialize the message
        serialized_msg = serialize_message(sync_req_msg)
        
        # Handle the message
        await sync_service.handle_message(from_addr, serialized_msg)
        
        # Verify the correct handler was called
        mock_handle_req.assert_called_once()
        call_args = mock_handle_req.call_args[0]
        assert call_args[0] == from_addr
        assert call_args[1]["type"] == sync_req_msg["type"]
        assert call_args[1]["id"] == sync_req_msg["id"]


@pytest.mark.asyncio
async def test_handle_message_sync_resp(sync_service):
    """Test handling a SYNC-RESP message."""
    # Patch the _handle_sync_resp method
    with patch.object(sync_service, '_handle_sync_resp', AsyncMock()) as mock_handle_resp:
        # Create a SYNC-RESP message
        from_addr = ("127.0.0.1", 8001)
        sync_resp_msg = {
            "type": "SYNC-RESP",
            "from": "127.0.0.1:8001",
            "id": "test123",
            "digest": {"version": 1, "entries": [], "is_full": True}
        }
        
        # Serialize the message
        serialized_msg = serialize_message(sync_resp_msg)
        
        # Handle the message
        await sync_service.handle_message(from_addr, serialized_msg)
        
        # Verify the correct handler was called
        mock_handle_resp.assert_called_once()
        call_args = mock_handle_resp.call_args[0]
        assert call_args[0] == from_addr
        assert call_args[1]["type"] == sync_resp_msg["type"]
        assert call_args[1]["id"] == sync_resp_msg["id"]


@pytest.mark.asyncio
async def test_handle_message_unknown_type(sync_service):
    """Test handling a message with an unknown type."""
    # Patch the handlers to ensure they're not called
    with patch.object(sync_service, '_handle_sync_req', AsyncMock()) as mock_handle_req, \
         patch.object(sync_service, '_handle_sync_resp', AsyncMock()) as mock_handle_resp:
        
        # Create a message with an unknown type
        from_addr = ("127.0.0.1", 8001)
        unknown_msg = {
            "type": "UNKNOWN",
            "from": "127.0.0.1:8001",
            "id": "test123"
        }
        
        # Serialize the message
        serialized_msg = serialize_message(unknown_msg)
        
        # Handle the message
        await sync_service.handle_message(from_addr, serialized_msg)
        
        # Verify no handlers were called
        mock_handle_req.assert_not_called()
        mock_handle_resp.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_deserialization_error(sync_service):
    """Test handling a message that can't be deserialized."""
    # Patch the handlers to ensure they're not called
    with patch.object(sync_service, '_handle_sync_req', AsyncMock()) as mock_handle_req, \
         patch.object(sync_service, '_handle_sync_resp', AsyncMock()) as mock_handle_resp:
        
        # Create invalid message bytes
        from_addr = ("127.0.0.1", 8001)
        invalid_msg = b'not valid json'
        
        # Handle the message
        await sync_service.handle_message(from_addr, invalid_msg)
        
        # Verify no handlers were called
        mock_handle_req.assert_not_called()
        mock_handle_resp.assert_not_called()


def test_sync_decision_logic(sync_service):
    """Test the decision logic for full vs incremental sync."""
    # Test case 1: Initial state, should do full sync
    sync_service._last_full_sync = 0
    current_time = 10  # 10 seconds later
    
    with patch('time.time', return_value=current_time):
        # Check if we should do a full sync
        do_full_sync = (current_time - sync_service._last_full_sync) > sync_service.config["FULL_SYNC_INTERVAL"]
        assert do_full_sync is True, "Should do full sync when interval has passed"
    
    # Test case 2: Just did a full sync, should do incremental
    sync_service._last_full_sync = current_time
    
    with patch('time.time', return_value=current_time + 0.1):  # 0.1 seconds later
        # Check if we should do a full sync
        do_full_sync = (time.time() - sync_service._last_full_sync) > sync_service.config["FULL_SYNC_INTERVAL"]
        assert do_full_sync is False, "Should do incremental sync when interval has not passed"
    
    # Test case 3: Interval has passed again, should do full sync
    with patch('time.time', return_value=current_time + sync_service.config["FULL_SYNC_INTERVAL"] + 0.1):
        # Check if we should do a full sync
        do_full_sync = (time.time() - sync_service._last_full_sync) > sync_service.config["FULL_SYNC_INTERVAL"]
        assert do_full_sync is True, "Should do full sync when interval has passed again"