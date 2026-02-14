import asyncio
import uvloop
from loguru import logger
from .TransportServer import TransportServer
from .TransportType import TransportType

# Set uvloop as the default event loop policy
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class UdpServer(TransportServer):
    def __init__(self):
        super().__init__()
        self.transport = None
        self.protocol = None
        self._transport_type = TransportType.UDP

    async def start_server(self, host, port, data_received_callback=None):
        """Start the UDP server."""
        self.host = host
        self.port = port
        self.data_received_callback = data_received_callback
        
        class UdpProtocol(asyncio.DatagramProtocol):
            def __init__(self, server):
                self.server = server
                
            def connection_made(self, transport):
                self.transport = transport
                logger.info(f"UDP server listening on {host}:{port}")
                
            def datagram_received(self, data, addr):
                if self.server.data_received_callback:
                    # Create a simple connection-like object for compatibility
                    class UdpConnection:
                        def __init__(self, addr):
                            self.peername = addr
                            self.transport = None
                            
                    connection = UdpConnection(addr)
                    # Call the callback - always create a task to handle async callbacks
                    asyncio.create_task(self.server.data_received_callback(connection, data))
                            
            def error_received(self, exc):
                logger.error(f"UDP server error: {exc}")
                
            def connection_lost(self, exc):
                logger.info("UDP server connection lost")
                self.server.running = False
        
        self.protocol = UdpProtocol(self)
        self.transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: self.protocol,
            local_addr=(host, port)
        )
        self.running = True

    async def stop_server(self):
        """Stop the UDP server."""
        logger.info("Stopping UDP server...")
        self.running = False
        if self.transport:
            self.transport.close()
            self.transport = None
        self.protocol = None

    def send_data(self, data, address=None):
        """Send data to a specific address."""
        if self.transport and address:
            try:
                if isinstance(data, str):
                    data = data.encode('utf-8')
                self.transport.sendto(data, address)
                logger.debug(f"Sent UDP data to {address[0]}:{address[1]}")
            except Exception as e:
                logger.error(f"Failed to send UDP data to {address}: {e}")
