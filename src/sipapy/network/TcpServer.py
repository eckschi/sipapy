import asyncio
import uvloop

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

class TcpServer:
    def __init__(self):
        self.connections: dict[int, TcpServerconnection] = {}
        self.next_conn_id = 0

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
        
    def send_to(self, conn_id, message):
        connection = self.connections.get(conn_id)
        if connection:
            connection.send_data(message)
        else:
            print('do hots wos')

    async def start_server(self, host, port, data_received_callback=None):
        loop = asyncio.get_event_loop()
        server = await loop.create_server(
            lambda: TcpServerconnection(self, data_received_callback),
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
        for connection in self.connections:
            connection.transport.close()            

