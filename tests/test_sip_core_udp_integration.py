import asyncio
import unittest
from src.sipapy.SipCore import SipCore
from src.sipapy.SipRequest import SipRequest
from src.sipapy.SipResponse import SipResponse
from src.sipapy.SipCore import TransportType

class TestSipCoreUdpIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_sip_core_udp_enabled(self):
        """Test that SipCore can be initialized with UDP support."""
        
        received_messages = []
        
        async def receive_callback(msg, transaction):
            received_messages.append((msg, transaction))
            # Return a simple 200 OK response
            return msg.genResponse(200, 'OK'), None, None
        
        # Create SipCore with UDP enabled
        sip_core = SipCore(receive_callback, transports=[TransportType.TCP, TransportType.UDP])
        
        # Verify UDP transport was created
        self.assertEqual(len(sip_core.transports), 1)
        self.assertEqual(sip_core.transports[0].get_transport_type(), TransportType.UDP)
        
        # Start the server
        sip_core.start('127.0.0.1', 5065)
        
        # Give it time to start
        await asyncio.sleep(0.1)
        
        # Verify server is running
        self.assertIsNotNone(sip_core.server_task)
        self.assertEqual(len(sip_core.transport_tasks), 1)
        
        # Stop the server
        await sip_core.stop()
        
        # Verify server is stopped
        self.assertEqual(len(sip_core.transport_tasks), 0)

    async def test_sip_core_udp_disabled(self):
        """Test that SipCore works with UDP disabled (default)."""
        
        received_messages = []
        
        async def receive_callback(msg, transaction):
            received_messages.append((msg, transaction))
            return msg.genResponse(200, 'OK'), None, None
        
        # Create SipCore with UDP disabled (default)
        sip_core = SipCore(receive_callback, transports=[TransportType.TCP])
        
        # Verify no additional transports were created
        self.assertEqual(len(sip_core.transports), 0)
        
        # Start the server
        sip_core.start('127.0.0.1', 5066)
        
        # Give it time to start
        await asyncio.sleep(0.1)
        
        # Verify only TCP server is running
        self.assertIsNotNone(sip_core.server_task)
        self.assertEqual(len(sip_core.transport_tasks), 0)
        
        # Stop the server
        await sip_core.stop()

    async def test_sip_core_udp_message_handling(self):
        """Test that SipCore can handle UDP messages correctly."""
        
        received_messages = []
        
        async def receive_callback(msg, transaction):
            received_messages.append((msg, transaction))
            return msg.genResponse(200, 'OK'), None, None
        
        # Create SipCore with UDP enabled
        sip_core = SipCore(receive_callback, transports=[TransportType.TCP, TransportType.UDP])
        
        # Start the server
        sip_core.start('127.0.0.1', 5067)
        await asyncio.sleep(0.1)
        
        # Send a SIP message via UDP
        import socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        sip_invite = "INVITE sip:user@example.com SIP/2.0\r\n" \
                    "Via: SIP/2.0/UDP 127.0.0.1:5067\r\n" \
                    "From: <sip:caller@example.com>\r\n" \
                    "To: <sip:user@example.com>\r\n" \
                    "Call-ID: test-call-udp\r\n" \
                    "CSeq: 1 INVITE\r\n" \
                    "Content-Length: 0\r\n" \
                    "\r\n"
        
        client_socket.sendto(sip_invite.encode(), ("127.0.0.1", 5067))
        
        # Give time for message to be processed
        await asyncio.sleep(0.2)
        
        # Verify message was received
        self.assertEqual(len(received_messages), 1)
        msg, transaction = received_messages[0]
        self.assertEqual(msg.getMethod(), 'INVITE')
        
        # Stop the server
        await sip_core.stop()
        client_socket.close()

    async def test_sip_core_multi_transport(self):
        """Test that SipCore can support multiple transports."""
        
        received_messages = []
        
        async def receive_callback(msg, transaction):
            received_messages.append((msg, transaction))
            return msg.genResponse(200, 'OK'), None, None
        
        # Create SipCore with multiple transports
        sip_core = SipCore(receive_callback, transports=[TransportType.UDP, TransportType.TCP])
        
        # Verify UDP transport was created (TCP is handled separately)
        self.assertEqual(len(sip_core.transports), 1)
        transport_types = [t.get_transport_type() for t in sip_core.transports]
        self.assertIn(TransportType.UDP, transport_types)
        
        # Start the server
        sip_core.start('127.0.0.1', 5068)
        
        # Give it time to start
        await asyncio.sleep(0.1)
        
        # Verify both servers are running
        self.assertIsNotNone(sip_core.server_task)
        self.assertEqual(len(sip_core.transport_tasks), 1)
        
        # Stop the server
        await sip_core.stop()
        
        # Verify both servers are stopped
        self.assertEqual(len(sip_core.transport_tasks), 0)

if __name__ == "__main__":
    unittest.main()
