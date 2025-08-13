"""
Message definitions for SWIM P2P.
This module defines the standardized message formats used in the SWIM protocol.
"""

import time
import uuid
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Tuple, Union


class MessageType(Enum):
    """Types of messages in the SWIM protocol."""
    PING = auto()
    PONG = auto()
    PING_REQ = auto()
    PING_REQ_ACK = auto()
    HEARTBEAT = auto()
    SYNC_REQ = auto()
    SYNC_RESP = auto()
    FULL_STATE = auto()


class Message:
    """
    Base class for SWIM protocol messages.
    
    This class provides common functionality for all message types,
    including serialization and deserialization.
    """
    
    def __init__(
        self,
        msg_type: MessageType,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        """
        Initialize a new message.
        
        Args:
            msg_type: The type of message.
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
        """
        self.type = msg_type
        self.from_addr = from_addr
        self.id = msg_id or str(uuid.uuid4())[:8]
        self.timestamp = timestamp or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        return {
            "type": self.type.name,
            "from": f"{self.from_addr[0]}:{self.from_addr[1]}",
            "id": self.id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a message from a dictionary.
        
        Args:
            data: The dictionary representation of the message.
            
        Returns:
            A new Message instance.
        """
        # Parse from address
        from_str = data.get("from", "0.0.0.0:0")
        host, port_str = from_str.split(":")
        from_addr = (host, int(port_str))
        
        # Parse message type
        msg_type = MessageType[data.get("type", "PING")]
        
        # Create appropriate message subclass based on type
        if msg_type == MessageType.PING:
            return PingMessage(
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp"),
                target_addr=_parse_addr(data.get("target"))
            )
        elif msg_type == MessageType.PONG:
            return PongMessage(
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp"),
                in_response_to=data.get("in_response_to"),
                orig_timestamp=data.get("orig_timestamp")
            )
        elif msg_type == MessageType.PING_REQ:
            return PingReqMessage(
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp"),
                target_addr=_parse_addr(data.get("target"))
            )
        elif msg_type == MessageType.PING_REQ_ACK:
            return PingReqAckMessage(
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp"),
                target_addr=_parse_addr(data.get("target")),
                status=data.get("status"),
                rtt=data.get("rtt")
            )
        elif msg_type == MessageType.HEARTBEAT:
            return HeartbeatMessage(
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp"),
                digest=data.get("digest")
            )
        elif msg_type == MessageType.SYNC_REQ:
            return SyncReqMessage(
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp"),
                known_version=data.get("known_version", 0)
            )
        elif msg_type == MessageType.SYNC_RESP:
            return SyncRespMessage(
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp"),
                digest=data.get("digest")
            )
        elif msg_type == MessageType.FULL_STATE:
            return FullStateMessage(
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp"),
                state=data.get("state")
            )
        else:
            # Default to base Message class
            return cls(
                msg_type=msg_type,
                from_addr=from_addr,
                msg_id=data.get("id"),
                timestamp=data.get("timestamp")
            )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        """
        Create a message from serialized bytes.
        
        Args:
            data: The serialized message bytes.
            
        Returns:
            A new Message instance.
        """
        from swim.utils.serialization import deserialize_message
        return cls.from_dict(deserialize_message(data))
    
    def to_bytes(self) -> bytes:
        """
        Convert the message to serialized bytes.
        
        Returns:
            The serialized message bytes.
        """
        from swim.utils.serialization import serialize_message
        return serialize_message(self.to_dict())


class PingMessage(Message):
    """
    PING message for direct failure detection.
    """
    
    def __init__(
        self,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        target_addr: Optional[Tuple[str, int]] = None
    ):
        """
        Initialize a new PING message.
        
        Args:
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
            target_addr: Optional target address for indirect pings.
        """
        super().__init__(MessageType.PING, from_addr, msg_id, timestamp)
        self.target_addr = target_addr
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        data = super().to_dict()
        if self.target_addr:
            data["target"] = f"{self.target_addr[0]}:{self.target_addr[1]}"
        return data


class PongMessage(Message):
    """
    PONG message in response to a PING.
    """
    
    def __init__(
        self,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        in_response_to: Optional[str] = None,
        orig_timestamp: Optional[float] = None
    ):
        """
        Initialize a new PONG message.
        
        Args:
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
            in_response_to: The type of message this is responding to.
            orig_timestamp: The timestamp of the original message.
        """
        super().__init__(MessageType.PONG, from_addr, msg_id, timestamp)
        self.in_response_to = in_response_to or "PING"
        self.orig_timestamp = orig_timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        data = super().to_dict()
        data["in_response_to"] = self.in_response_to
        if self.orig_timestamp:
            data["orig_timestamp"] = self.orig_timestamp
        return data


class PingReqMessage(Message):
    """
    PING-REQ message for indirect failure detection.
    """
    
    def __init__(
        self,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        target_addr: Optional[Tuple[str, int]] = None
    ):
        """
        Initialize a new PING-REQ message.
        
        Args:
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
            target_addr: The target address to ping indirectly.
        """
        super().__init__(MessageType.PING_REQ, from_addr, msg_id, timestamp)
        self.target_addr = target_addr
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        data = super().to_dict()
        if self.target_addr:
            data["target"] = f"{self.target_addr[0]}:{self.target_addr[1]}"
        return data


class PingReqAckMessage(Message):
    """
    PING-REQ-ACK message in response to a PING-REQ.
    """
    
    def __init__(
        self,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        target_addr: Optional[Tuple[str, int]] = None,
        status: Optional[str] = None,
        rtt: Optional[float] = None
    ):
        """
        Initialize a new PING-REQ-ACK message.
        
        Args:
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
            target_addr: The target address that was pinged.
            status: The status of the indirect ping (alive, unreachable).
            rtt: The round-trip time of the indirect ping.
        """
        super().__init__(MessageType.PING_REQ_ACK, from_addr, msg_id, timestamp)
        self.target_addr = target_addr
        self.status = status or "unreachable"
        self.rtt = rtt
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        data = super().to_dict()
        if self.target_addr:
            data["target"] = f"{self.target_addr[0]}:{self.target_addr[1]}"
        data["status"] = self.status
        if self.rtt is not None:
            data["rtt"] = self.rtt
        return data


class HeartbeatMessage(Message):
    """
    HEARTBEAT message for gossip dissemination.
    """
    
    def __init__(
        self,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        digest: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new HEARTBEAT message.
        
        Args:
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
            digest: The membership digest to disseminate.
        """
        super().__init__(MessageType.HEARTBEAT, from_addr, msg_id, timestamp)
        self.digest = digest or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        data = super().to_dict()
        data["digest"] = self.digest
        return data


class SyncReqMessage(Message):
    """
    SYNC-REQ message for push-pull synchronization.
    """
    
    def __init__(
        self,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        known_version: int = 0
    ):
        """
        Initialize a new SYNC-REQ message.
        
        Args:
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
            known_version: The version known to the requester.
        """
        super().__init__(MessageType.SYNC_REQ, from_addr, msg_id, timestamp)
        self.known_version = known_version
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        data = super().to_dict()
        data["known_version"] = self.known_version
        return data


class SyncRespMessage(Message):
    """
    SYNC-RESP message in response to a SYNC-REQ.
    """
    
    def __init__(
        self,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        digest: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new SYNC-RESP message.
        
        Args:
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
            digest: The membership digest to synchronize.
        """
        super().__init__(MessageType.SYNC_RESP, from_addr, msg_id, timestamp)
        self.digest = digest or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        data = super().to_dict()
        data["digest"] = self.digest
        return data


class FullStateMessage(Message):
    """
    FULL-STATE message for complete state transfer.
    """
    
    def __init__(
        self,
        from_addr: Tuple[str, int],
        msg_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        state: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new FULL-STATE message.
        
        Args:
            from_addr: The address that sent the message.
            msg_id: Optional unique ID for the message.
            timestamp: Optional timestamp for the message.
            state: The complete membership state.
        """
        super().__init__(MessageType.FULL_STATE, from_addr, msg_id, timestamp)
        self.state = state or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the message.
        """
        data = super().to_dict()
        data["state"] = self.state
        return data


def _parse_addr(addr_str: Optional[str]) -> Optional[Tuple[str, int]]:
    """
    Parse an address string into a tuple.
    
    Args:
        addr_str: The address string in the format "host:port".
        
    Returns:
        A tuple of (host, port), or None if the input is invalid.
    """
    if not addr_str:
        return None
    
    try:
        host, port_str = addr_str.split(":")
        return (host, int(port_str))
    except (ValueError, TypeError):
        return None