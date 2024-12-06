import asyncio
import uvloop

# Set uvloop as the default event loop policy
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class TcpServerProtocol(asyncio.Protocol):
    def __init__(self, server, data_received_callback=None):
        self.server = server
        self.transport = None
        self.peername = None
        self.data_received_callback = data_received_callback

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        print(f"Connection from {self.peername}")
        self.server.add_connection(self)  # Register this connection

    def data_received(self, data):
        message = data.decode()
        print(f"Received data: {message}")
        
        # Trigger the external callback if it's provided
        if self.data_received_callback:
            self.data_received_callback(self, message)  # Call the user's callback
            
        # Echo back the received data
        self.transport.write(data)
        print(f"Sent data: {message}")

    def connection_lost(self, exc):
        print(f"Closing connection from {self.peername}")
        self.server.remove_connection(self)  # Remove the connection from the server

    def send_data(self, data):
        """Send data from the outside."""
        if self.transport:
            self.transport.write(data.encode())  # Send data to the connected client

class TcpServer:
    def __init__(self):
        self.connections = []

    def add_connection(self, protocol):
        """Add a protocol instance to the connections list."""
        self.connections.append(protocol)

    def remove_connection(self, protocol):
        """Remove a protocol instance from the connections list."""
        self.connections.remove(protocol)

    def broadcast(self, message):
        """Send the message to all connected clients."""
        for protocol in self.connections:
            protocol.send_data(message)

    async def start_server(self, host='127.0.0.1', port=8888, data_received_callback=None):
        loop = asyncio.get_event_loop()
        server = await loop.create_server(
            lambda: TcpServerProtocol(self, data_received_callback),
            host, port
        )
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            pass  # Handle the cancelation gracefully when server is stopped

    def stop_server(self):
        """Gracefully stop the server."""
        print("Stopping the server...")
        for protocol in self.connections:
            protocol.transport.close()            

