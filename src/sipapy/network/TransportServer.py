import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
from loguru import logger

class TransportServer(ABC):
    """Abstract base class for transport servers."""
    
    def __init__(self):
        self.host = None
        self.port = None
        self.data_received_callback = None
        self.running = False
        self.server_task = None
    
    @abstractmethod
    async def start_server(self, host: str, port: int, data_received_callback: Optional[Callable] = None):
        """Start the transport server."""
        pass
    
    @abstractmethod
    async def stop_server(self):
        """Stop the transport server."""
        pass
    
    @abstractmethod
    def send_data(self, connection: Any, data: str, address: tuple = None):
        """Send data to a specific connection/address."""
        pass
    
    def get_transport_type(self) -> 'TransportType':
        """Get the transport type of this server."""
        from .TransportType import TransportType
        return self._transport_type
    
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self.running