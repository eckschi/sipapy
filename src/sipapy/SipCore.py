import asyncio
import uvloop

from sipapy.network.TcpServer import TcpServer

# Set uvloop as the default event loop policy
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class SipCore:
    def __init__(self):
        self.server = TcpServer()

    def start(self):
        # Start the server in the background
        self.server_task = asyncio.create_task(
            self.server.start_server(data_received_callback=self.data_received))

    def stop(self):
        # Stop the server
        self.server.stop_server()

    # User code that interacts with the server and provides a data-received callback
    def data_received(self, protocol, data):
        """A user-defined callback for handling received data."""
        print(
            f"User callback - Data received from {protocol.peername}: {data}")
        # For example, you can respond to the client, log data, etc.
        protocol.send_data(f"User processed: {data}")
