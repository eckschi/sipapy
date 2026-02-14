import socket
import asyncio
import unittest
from src.sipapy.network.UdpServer import UdpServer
from src.sipapy.SipRequest import SipRequest
from src.sipapy.SipResponse import SipResponse

class TestUdpServer(unittest.IsolatedAsyncioTestCase):
    async def test_udp_server_basic(self):
        """Test basic UDP server functionality."""
        server = UdpServer()
        
        # Track received messages
        received_messages = []
        
        async def data_received_callback(connection, data):
            print(f"Server received from {connection.peername}: {data}")
            received_messages.append((connection.peername, data))
            # Echo back for basic test
            print(f"Server sending back to {connection.peername}")
            server.send_to(connection.peername, data)
        
        # Start server in background
        server_task = asyncio.create_task(
            server.start_server("127.0.0.1", 5061, data_received_callback)
        )
        
        # Give server time to start
        await asyncio.sleep(0.1)

        # Send test message
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_message = b"hello"
        client_socket.sendto(test_message, ("127.0.0.1", 5061))
        
        # Give time for server to process
        await asyncio.sleep(0.2)
        
        # Verify that server received the message
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0][1], test_message)
        
        # Cleanup
        await server.stop_server()
        await server_task
        client_socket.close()

    async def test_udp_server_sip_message(self):
        """Test UDP server with SIP message parsing."""
        server = UdpServer()
        
        received_sip_messages = []
        
        async def data_received_callback(connection, data):
            try:
                message = data.decode('utf-8', 'backslashreplace')
                if message.startswith('SIP/2.0 '):
                    # This is a response
                    resp = SipResponse(message)
                    received_sip_messages.append(('response', resp))
                else:
                    # This is a request
                    req = SipRequest(message)
                    received_sip_messages.append(('request', req))
                    
                # Send a simple response
                if message.startswith('INVITE'):
                    response = "SIP/2.0 200 OK\r\n\r\n"
                    server.send_to(connection.peername, response)
                    
            except Exception as e:
                print(f"Error parsing SIP message: {e}")
        
        # Start server
        server_task = asyncio.create_task(
            server.start_server("127.0.0.1", 5062, data_received_callback)
        )
        
        await asyncio.sleep(0.1)

        # Send SIP INVITE
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sip_invite = "INVITE sip:user@example.com SIP/2.0\r\n" \
                    "Via: SIP/2.0/UDP 127.0.0.1:5062\r\n" \
                    "From: <sip:caller@example.com>\r\n" \
                    "To: <sip:user@example.com>\r\n" \
                    "Call-ID: test-call-123\r\n" \
                    "CSeq: 1 INVITE\r\n" \
                    "Content-Length: 0\r\n" \
                    "\r\n"
        
        client_socket.sendto(sip_invite.encode(), ("127.0.0.1", 5062))
        
        # Give time for server to process
        await asyncio.sleep(0.2)
        
        # Verify
        self.assertEqual(len(received_sip_messages), 1)
        self.assertEqual(received_sip_messages[0][0], 'request')
        
        # Cleanup
        await server.stop_server()
        await server_task
        client_socket.close()

    async def test_udp_server_stop(self):
        """Test UDP server stop functionality."""
        server = UdpServer()
        
        async def dummy_callback(connection, data):
            pass
        
        # Start and immediately stop
        server_task = asyncio.create_task(
            server.start_server("127.0.0.1", 5063, dummy_callback)
        )
        
        await asyncio.sleep(0.1)
        await server.stop_server()
        await server_task
        
        # Verify server is stopped
        self.assertFalse(server.running)
        self.assertIsNone(server.transport)

if __name__ == "__main__":
    unittest.main()
