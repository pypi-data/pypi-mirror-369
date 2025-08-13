from abc import ABC, abstractmethod
from typing import Callable, Tuple, Any, Dict, Optional, Union
from enum import Enum, auto

class TransportType(Enum):
    """Enum for transport types."""
    UDP = auto()
    TCP = auto()
    HYBRID = auto()

class Transport(ABC):
    """Enhanced abstract base class for all transport implementations."""
    
    @abstractmethod
    async def bind(self, address: Tuple[str, int]) -> None:
        """Bind the transport to a local address asynchronously.
        
        Args:
            address: A tuple of (host, port) to bind to
        """
        pass
    
    @abstractmethod
    async def send(self, data: bytes, dest: Tuple[str, int]) -> None:
        """Send data to a specific destination asynchronously.
        
        Args:
            data: The bytes to send
            dest: A tuple of (host, port) for the destination
        """
        pass
    
    @abstractmethod
    async def receive(self, timeout: Optional[float] = None, msg_type: Optional[str] = None) -> Tuple[bytes, Tuple[str, int]]:
        """Receive data from the transport asynchronously.
        
        Args:
            timeout: Maximum time to wait for data (None = wait forever)
            msg_type: Optional specific message type to receive
            
        Returns:
            A tuple of (data, sender_address)
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the transport and release resources asynchronously."""
        pass
    
    @abstractmethod
    async def start_receiver(self, callback: Callable[[bytes, Tuple[str, int]], Any]) -> None:
        """Start a background task to continuously receive messages.
        
        Args:
            callback: Function to call with (data, sender_address) when data is received
        """
        pass
    
    @classmethod
    def select_transport_for_message(cls, message_size: int, threshold: int = 1400) -> TransportType:
        """Select the appropriate transport type based on message size.
        
        Args:
            message_size: Size of the message in bytes
            threshold: Size threshold above which to use TCP
            
        Returns:
            TransportType enum value (UDP or TCP)
        """
        if message_size <= threshold:
            return TransportType.UDP
        else:
            return TransportType.TCP