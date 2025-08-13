"""
Unit tests for serialization utilities.
"""

import pytest
import json
import base64
import zlib
from swim.utils.serialization import (
    serialize_message, deserialize_message,
    serialize_partial, serialize_binary_data, deserialize_binary_data
)


def test_serialize_message():
    """Test serializing a message to bytes."""
    message = {
        "type": "PING",
        "from": "127.0.0.1:8000",
        "data": {
            "key": "value",
            "number": 42
        }
    }
    
    serialized = serialize_message(message)
    
    # Verify it's bytes
    assert isinstance(serialized, bytes)
    
    # Verify it starts with the uncompressed marker
    assert serialized[0] == ord('U')
    
    # Verify it can be deserialized back
    deserialized = deserialize_message(serialized)
    assert deserialized == message


def test_serialize_message_with_compression():
    """Test serializing a message with compression."""
    # Create a large message that will trigger compression
    large_data = "x" * 2000  # More than 1KB to trigger compression
    message = {
        "type": "LARGE_MESSAGE",
        "from": "127.0.0.1:8000",
        "data": large_data
    }
    
    # Serialize with compression
    serialized = serialize_message(message, compress=True)
    
    # Verify it's bytes
    assert isinstance(serialized, bytes)
    
    # Verify it starts with the compressed marker
    assert serialized[0] == ord('C')
    
    # Verify compressed size is smaller than original
    original_size = len(json.dumps(message).encode('utf-8'))
    assert len(serialized) < original_size
    
    # Verify it can be deserialized back
    deserialized = deserialize_message(serialized)
    assert deserialized == message


def test_deserialize_message():
    """Test deserializing a message from bytes."""
    original = {
        "type": "HEARTBEAT",
        "from": "127.0.0.1:8000",
        "digest": [
            {"addr": "127.0.0.1:8000", "state": "ALIVE", "incarnation": 1},
            {"addr": "127.0.0.1:8001", "state": "SUSPECT", "incarnation": 2}
        ]
    }
    
    # Serialize to bytes with uncompressed marker
    serialized = b'U' + json.dumps(original).encode()
    
    # Deserialize
    deserialized = deserialize_message(serialized)
    
    # Verify it matches the original
    assert deserialized == original


def test_deserialize_legacy_format():
    """Test deserializing a message in legacy format (no marker)."""
    original = {
        "type": "PING",
        "from": "127.0.0.1:8000"
    }
    
    # Serialize to bytes without marker (legacy format)
    serialized = json.dumps(original).encode()
    
    # Deserialize
    deserialized = deserialize_message(serialized)
    
    # Verify it matches the original
    assert deserialized == original


def test_deserialize_compressed_message():
    """Test deserializing a compressed message."""
    original = {
        "type": "LARGE_MESSAGE",
        "data": "x" * 2000
    }
    
    # Manually compress the message
    json_data = json.dumps(original).encode('utf-8')
    compressed = zlib.compress(json_data)
    serialized = b'C' + compressed
    
    # Deserialize
    deserialized = deserialize_message(serialized)
    
    # Verify it matches the original
    assert deserialized == original


def test_deserialize_invalid_json():
    """Test deserializing invalid JSON."""
    invalid_data = b'U' + b"This is not valid JSON"
    
    with pytest.raises(json.JSONDecodeError):
        deserialize_message(invalid_data)


def test_deserialize_empty_data():
    """Test deserializing empty data."""
    with pytest.raises(ValueError, match="Empty data received"):
        deserialize_message(b"")


def test_serialize_complex_types():
    """Test serializing message with complex types."""
    from enum import Enum
    
    class TestEnum(Enum):
        VALUE1 = 1
        VALUE2 = 2
    
    # This should raise a TypeError because Enum is not JSON serializable
    with pytest.raises(TypeError):
        serialize_message({"enum": TestEnum.VALUE1})


def test_serialize_partial():
    """Test serializing partial message."""
    message = {
        "type": "PING",
        "from": "127.0.0.1:8000",
        "id": "123",
        "timestamp": 1234567890,
        "data": {
            "key": "value"
        }
    }
    
    # Serialize only specific fields
    fields = ["type", "from", "id"]
    serialized = serialize_partial(message, fields)
    
    # Deserialize and verify only specified fields are included
    deserialized = deserialize_message(serialized)
    assert "type" in deserialized
    assert "from" in deserialized
    assert "id" in deserialized
    assert "timestamp" not in deserialized
    assert "data" not in deserialized
    
    assert deserialized["type"] == message["type"]
    assert deserialized["from"] == message["from"]
    assert deserialized["id"] == message["id"]


def test_serialize_partial_nonexistent_fields():
    """Test serializing partial message with nonexistent fields."""
    message = {"type": "PING", "from": "127.0.0.1:8000"}
    
    # Include a field that doesn't exist
    fields = ["type", "nonexistent"]
    serialized = serialize_partial(message, fields)
    
    # Deserialize and verify
    deserialized = deserialize_message(serialized)
    assert "type" in deserialized
    assert "nonexistent" not in deserialized
    assert deserialized["type"] == message["type"]


def test_binary_data_serialization():
    """Test serializing and deserializing binary data."""
    # Create some binary data
    binary_data = b'\x00\x01\x02\x03\x04\xFF\xFE\xFD'
    
    # Serialize to string
    serialized = serialize_binary_data(binary_data)
    
    # Verify it's a string
    assert isinstance(serialized, str)
    
    # Verify it's valid base64
    try:
        base64.b64decode(serialized)
    except Exception:
        pytest.fail("Not valid base64")
    
    # Deserialize back to binary
    deserialized = deserialize_binary_data(serialized)
    
    # Verify it matches the original
    assert deserialized == binary_data


def test_binary_data_in_message():
    """Test using binary data in a message."""
    # Create a message with binary data
    binary_data = b'\x00\x01\x02\x03\x04\xFF\xFE\xFD'
    encoded = serialize_binary_data(binary_data)
    
    message = {
        "type": "BINARY",
        "data": encoded
    }
    
    # Serialize the message
    serialized = serialize_message(message)
    
    # Deserialize
    deserialized = deserialize_message(serialized)
    
    # Extract and decode the binary data
    decoded = deserialize_binary_data(deserialized["data"])
    
    # Verify it matches the original
    assert decoded == binary_data