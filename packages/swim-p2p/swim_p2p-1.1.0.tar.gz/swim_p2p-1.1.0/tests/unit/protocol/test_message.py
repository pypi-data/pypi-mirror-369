"""
Unit tests for the standardized message formats.
"""

import pytest
import time
from swim.protocol.message import (
    Message, MessageType, PingMessage, PongMessage, PingReqMessage,
    PingReqAckMessage, HeartbeatMessage, SyncReqMessage, SyncRespMessage,
    FullStateMessage
)


def test_message_types():
    """Test that all expected message types are defined."""
    assert hasattr(MessageType, "PING")
    assert hasattr(MessageType, "PONG")
    assert hasattr(MessageType, "PING_REQ")
    assert hasattr(MessageType, "PING_REQ_ACK")
    assert hasattr(MessageType, "HEARTBEAT")
    assert hasattr(MessageType, "SYNC_REQ")
    assert hasattr(MessageType, "SYNC_RESP")
    assert hasattr(MessageType, "FULL_STATE")


def test_base_message_creation():
    """Test creating a base Message."""
    from_addr = ("127.0.0.1", 8000)
    msg = Message(MessageType.PING, from_addr)
    
    assert msg.type == MessageType.PING
    assert msg.from_addr == from_addr
    assert msg.id is not None
    assert msg.timestamp > 0
    
    # Test with explicit values
    msg_id = "test123"
    timestamp = time.time()
    msg = Message(MessageType.PONG, from_addr, msg_id, timestamp)
    
    assert msg.id == msg_id
    assert msg.timestamp == timestamp


def test_message_serialization():
    """Test serializing a message to a dictionary."""
    from_addr = ("127.0.0.1", 8000)
    msg_id = "test123"
    timestamp = time.time()
    msg = Message(MessageType.PING, from_addr, msg_id, timestamp)
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "PING"
    assert data["from"] == "127.0.0.1:8000"
    assert data["id"] == msg_id
    assert data["timestamp"] == timestamp


def test_message_deserialization():
    """Test deserializing a message from a dictionary."""
    data = {
        "type": "PING",
        "from": "127.0.0.1:8000",
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Deserialize from dict
    msg = Message.from_dict(data)
    
    assert msg.type == MessageType.PING
    assert msg.from_addr == ("127.0.0.1", 8000)
    assert msg.id == "test123"
    assert msg.timestamp == data["timestamp"]


def test_ping_message():
    """Test PingMessage creation and serialization."""
    from_addr = ("127.0.0.1", 8000)
    target_addr = ("127.0.0.1", 8001)
    msg = PingMessage(from_addr, "test123", time.time(), target_addr)
    
    assert msg.type == MessageType.PING
    assert msg.target_addr == target_addr
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "PING"
    assert data["target"] == "127.0.0.1:8001"


def test_pong_message():
    """Test PongMessage creation and serialization."""
    from_addr = ("127.0.0.1", 8000)
    orig_timestamp = time.time() - 0.1
    msg = PongMessage(from_addr, "test123", time.time(), "PING", orig_timestamp)
    
    assert msg.type == MessageType.PONG
    assert msg.in_response_to == "PING"
    assert msg.orig_timestamp == orig_timestamp
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "PONG"
    assert data["in_response_to"] == "PING"
    assert data["orig_timestamp"] == orig_timestamp


def test_ping_req_message():
    """Test PingReqMessage creation and serialization."""
    from_addr = ("127.0.0.1", 8000)
    target_addr = ("127.0.0.1", 8001)
    msg = PingReqMessage(from_addr, "test123", time.time(), target_addr)
    
    assert msg.type == MessageType.PING_REQ
    assert msg.target_addr == target_addr
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "PING_REQ"
    assert data["target"] == "127.0.0.1:8001"


def test_ping_req_ack_message():
    """Test PingReqAckMessage creation and serialization."""
    from_addr = ("127.0.0.1", 8000)
    target_addr = ("127.0.0.1", 8001)
    msg = PingReqAckMessage(from_addr, "test123", time.time(), target_addr, "alive", 0.1)
    
    assert msg.type == MessageType.PING_REQ_ACK
    assert msg.target_addr == target_addr
    assert msg.status == "alive"
    assert msg.rtt == 0.1
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "PING_REQ_ACK"
    assert data["target"] == "127.0.0.1:8001"
    assert data["status"] == "alive"
    assert data["rtt"] == 0.1


def test_heartbeat_message():
    """Test HeartbeatMessage creation and serialization."""
    from_addr = ("127.0.0.1", 8000)
    digest = {
        "version": 1,
        "entries": [
            {"addr": "127.0.0.1:8000", "state": "ALIVE", "incarnation": 1}
        ],
        "is_full": True
    }
    msg = HeartbeatMessage(from_addr, "test123", time.time(), digest)
    
    assert msg.type == MessageType.HEARTBEAT
    assert msg.digest == digest
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "HEARTBEAT"
    assert data["digest"] == digest


def test_sync_req_message():
    """Test SyncReqMessage creation and serialization."""
    from_addr = ("127.0.0.1", 8000)
    msg = SyncReqMessage(from_addr, "test123", time.time(), 5)
    
    assert msg.type == MessageType.SYNC_REQ
    assert msg.known_version == 5
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "SYNC_REQ"
    assert data["known_version"] == 5


def test_sync_resp_message():
    """Test SyncRespMessage creation and serialization."""
    from_addr = ("127.0.0.1", 8000)
    digest = {
        "version": 10,
        "entries": [
            {"addr": "127.0.0.1:8000", "state": "ALIVE", "incarnation": 1}
        ],
        "is_full": False
    }
    msg = SyncRespMessage(from_addr, "test123", time.time(), digest)
    
    assert msg.type == MessageType.SYNC_RESP
    assert msg.digest == digest
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "SYNC_RESP"
    assert data["digest"] == digest


def test_full_state_message():
    """Test FullStateMessage creation and serialization."""
    from_addr = ("127.0.0.1", 8000)
    state = {
        "members": [
            {"addr": "127.0.0.1:8000", "state": "ALIVE", "incarnation": 1}
        ],
        "version": 15
    }
    msg = FullStateMessage(from_addr, "test123", time.time(), state)
    
    assert msg.type == MessageType.FULL_STATE
    assert msg.state == state
    
    # Serialize to dict
    data = msg.to_dict()
    
    assert data["type"] == "FULL_STATE"
    assert data["state"] == state


def test_message_bytes_conversion():
    """Test converting a message to and from bytes."""
    from_addr = ("127.0.0.1", 8000)
    msg = PingMessage(from_addr, "test123", time.time())
    
    # Convert to bytes
    msg_bytes = msg.to_bytes()
    
    # Convert back from bytes
    msg2 = Message.from_bytes(msg_bytes)
    
    assert msg2.type == msg.type
    assert msg2.from_addr == msg.from_addr
    assert msg2.id == msg.id
    assert msg2.timestamp == msg.timestamp


def test_message_from_dict_factory():
    """Test the factory method for creating specific message types."""
    # Test creating different message types from dictionaries
    
    # PING
    ping_data = {
        "type": "PING",
        "from": "127.0.0.1:8000",
        "id": "test123",
        "timestamp": time.time(),
        "target": "127.0.0.1:8001"
    }
    ping_msg = Message.from_dict(ping_data)
    assert isinstance(ping_msg, PingMessage)
    assert ping_msg.target_addr == ("127.0.0.1", 8001)
    
    # PONG
    pong_data = {
        "type": "PONG",
        "from": "127.0.0.1:8000",
        "id": "test123",
        "timestamp": time.time(),
        "in_response_to": "PING",
        "orig_timestamp": time.time() - 0.1
    }
    pong_msg = Message.from_dict(pong_data)
    assert isinstance(pong_msg, PongMessage)
    assert pong_msg.in_response_to == "PING"
    
    # HEARTBEAT
    heartbeat_data = {
        "type": "HEARTBEAT",
        "from": "127.0.0.1:8000",
        "id": "test123",
        "timestamp": time.time(),
        "digest": {
            "version": 1,
            "entries": [],
            "is_full": True
        }
    }
    heartbeat_msg = Message.from_dict(heartbeat_data)
    assert isinstance(heartbeat_msg, HeartbeatMessage)
    assert "version" in heartbeat_msg.digest