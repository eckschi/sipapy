import asyncio
import uvloop
from .TransportServer import TransportServer
from .TransportType import TransportType

# Set uvloop as the default event loop policy
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class TcpServerconnection(asyncio.Protocol):
    def __init__(self, server, data_received_callback=None):
        self.id = None
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
        # Trigger the external callback if it's provided
        if self.data_received_callback:
            self.data_received_callback(self, data)  
            
    def connection_lost(self, exc):
        print(f"Closing connection from {self.peername}")
        self.server.remove_connection(self.id)  # Remove the connection from the server

    def send_data(self, data):
        """Send data from the outside."""
        if self.transport:
            self.transport.write(data.encode())  # Send data to the connected client

class TcpServer(TransportServer):
    def __init__(self):
        super().__init__()
        self.connections: dict[int, TcpServerconnection] = {}
        self.next_conn_id = 0
        self._transport_type = TransportType.TCP
        self.server = None

    def add_connection(self, connection):
        """Add a connection instance to the connections list."""
        cid = self.next_conn_id
        self.next_conn_id = self.next_conn_id + 1
        self.connections[cid] = connection
        connection.id = cid

    def remove_connection(self, conn_id):
        """Remove a connection instance from the connections list."""
        self.connections.pop(conn_id, None)

    def broadcast(self, message):
        """Send the message to all connected clients."""
        for connection in self.connections:
            connection.send_data(message)
        
    def send_data(self, connection, data, address=None):
        """Send data to a specific connection."""
        if isinstance(connection, int):
            # If connection is an ID, look it up
            conn = self.connections.get(connection)
            if conn:
                conn.send_data(data)
            else:
                print('Connection not found')
        elif hasattr(connection, 'send_data'):
            # If connection is a TcpServerconnection object
            connection.send_data(data)
        else:
            print('Invalid connection type')

    async def start_server(self, host, port, data_received_callback=None):
        self.host = host
        self.port = port
        self.data_received_callback = data_received_callback
        
        loop = asyncio.get_event_loop()
        self.server = await loop.create_server(
            lambda: TcpServerconnection(self, data_received_callback),
            host, port
        )
        addr = self.server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        self.running = True
        try:
            await self.server.serve_forever()
        except asyncio.CancelledError:
            pass  # Handle the cancelation gracefully when server is stopped
        finally:
            self.running = False

    async def stop_server(self):
        """Gracefully stop the server."""
        print("Stopping the server...")
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        
        for connection in self.connections.values():
            connection.transport.close()
        self.connections.clear()
        self.running = False            

