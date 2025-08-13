"""
Serialization utilities for SWIM P2P.

This module provides functions for serializing and deserializing
messages used in the SWIM protocol, with support for compression
and different message types.
"""

import json
import zlib
import base64
from typing import Dict, Any, Union, Optional, Tuple


def serialize_message(msg: Dict[str, Any], compress: bool = False) -> bytes:
    """Serialize a message to JSON bytes.
    
    Args:
        msg: The message dictionary to serialize
        compress: Whether to compress the message (for large messages)
        
    Returns:
        The serialized message as bytes
        
    Raises:
        TypeError: If the message contains types that cannot be serialized to JSON
    """
    serialized = json.dumps(msg).encode("utf-8")
    
    if compress and len(serialized) > 1024:  # Only compress messages larger than 1KB
        compressed = zlib.compress(serialized)
        # Add a marker to indicate this is compressed
        return b'C' + compressed
    
    return b'U' + serialized


def deserialize_message(data: Union[bytes, bytearray]) -> Dict[str, Any]:
    """Deserialize a message from JSON bytes.
    
    Args:
        data: The serialized message bytes
        
    Returns:
        The deserialized message as a dictionary
        
    Raises:
        json.JSONDecodeError: If the data is not valid JSON
        zlib.error: If the compressed data is corrupted
    """
    if not data:
        raise ValueError("Empty data received")
    
    # Check if the message is compressed
    if data[0] == ord('C'):
        # Decompress the message
        decompressed = zlib.decompress(data[1:])
        return json.loads(decompressed.decode("utf-8"))
    elif data[0] == ord('U'):
        # Uncompressed message
        return json.loads(data[1:].decode("utf-8"))
    else:
        # Legacy format (no marker)
        return json.loads(data.decode("utf-8"))


def serialize_partial(msg: Dict[str, Any], fields: list) -> bytes:
    """Serialize only specific fields of a message.
    
    This is useful for sending partial updates.
    
    Args:
        msg: The message dictionary to serialize
        fields: List of field names to include
        
    Returns:
        The serialized partial message as bytes
    """
    partial = {k: msg[k] for k in fields if k in msg}
    return serialize_message(partial)


def serialize_binary_data(data: bytes) -> str:
    """Serialize binary data to a string representation.
    
    Args:
        data: Binary data to serialize
        
    Returns:
        Base64 encoded string representation
    """
    return base64.b64encode(data).decode('ascii')


def deserialize_binary_data(encoded: str) -> bytes:
    """Deserialize binary data from a string representation.
    
    Args:
        encoded: Base64 encoded string
        
    Returns:
        Original binary data
    """
    return base64.b64decode(encoded)