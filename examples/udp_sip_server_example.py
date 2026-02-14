#!/usr/bin/env python3
"""
Example of a SIP UDP server using the improved UdpServer class.
This demonstrates how to integrate the UDP server with the existing SIP message handling.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sipapy.network.UdpServer import UdpServer
from sipapy.SipRequest import SipRequest
from sipapy.SipResponse import SipResponse
from loguru import logger

class SimpleSipUdpServer:
    def __init__(self):
        self.udp_server = UdpServer()
        
    async def handle_sip_message(self, connection, data):
        """Handle incoming SIP messages."""
        try:
            message = data.decode('utf-8', 'backslashreplace')
            logger.info(f"Received SIP message from {connection.peername[0]}:{connection.peername[1]}:")
            logger.info(message)
            
            if message.startswith('SIP/2.0 '):
                # This is a response
                resp = SipResponse(message)
                logger.info(f"Received SIP response: {resp.getSCode()} {resp.getReason()}")
                
            elif message.strip():
                # This is a request
                req = SipRequest(message)
                logger.info(f"Received SIP request: {req.method}")
                
                # Send a simple response
                if req.method == 'INVITE':
                    response = "SIP/2.0 200 OK\r\n" \
                              "Via: SIP/2.0/UDP 127.0.0.1:5060\r\n" \
                              "From: <sip:caller@example.com>\r\n" \
                              "To: <sip:user@example.com>\r\n" \
                              "Call-ID: test-call-123\r\n" \
                              "CSeq: 1 INVITE\r\n" \
                              "Content-Length: 0\r\n" \
                              "\r\n"
                    self.udp_server.send_to(connection.peername, response)
                    logger.info("Sent 200 OK response")
                    
                elif req.method == 'REGISTER':
                    response = "SIP/2.0 200 OK\r\n" \
                              "Via: SIP/2.0/UDP 127.0.0.1:5060\r\n" \
                              "From: <sip:user@example.com>\r\n" \
                              "To: <sip:user@example.com>\r\n" \
                              "Call-ID: test-register-123\r\n" \
                              "CSeq: 1 REGISTER\r\n" \
                              "Contact: <sip:user@127.0.0.1:5060>\r\n" \
                              "Expires: 3600\r\n" \
                              "Content-Length: 0\r\n" \
                              "\r\n"
                    self.udp_server.send_to(connection.peername, response)
                    logger.info("Sent 200 OK response to REGISTER")
                    
                elif req.method == 'OPTIONS':
                    response = "SIP/2.0 200 OK\r\n" \
                              "Via: SIP/2.0/UDP 127.0.0.1:5060\r\n" \
                              "From: <sip:caller@example.com>\r\n" \
                              "To: <sip:user@example.com>\r\n" \
                              "Call-ID: test-options-123\r\n" \
                              "CSeq: 1 OPTIONS\r\n" \
                              "Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REGISTER\r\n" \
                              "Content-Length: 0\r\n" \
                              "\r\n"
                    self.udp_server.send_to(connection.peername, response)
                    logger.info("Sent 200 OK response to OPTIONS")
                    
        except Exception as e:
            logger.error(f"Error handling SIP message: {e}")
            # Send error response
            error_response = "SIP/2.0 500 Internal Server Error\r\n" \
                           "Via: SIP/2.0/UDP 127.0.0.1:5060\r\n" \
                           "Content-Length: 0\r\n" \
                           "\r\n"
            self.udp_server.send_to(connection.peername, error_response)
            
    async def start(self, host='127.0.0.1', port=5060):
        """Start the SIP UDP server."""
        logger.info(f"Starting SIP UDP server on {host}:{port}")
        await self.udp_server.start_server(host, port, self.handle_sip_message)

    async def stop(self):
        """Stop the SIP UDP server."""
        logger.info("Stopping SIP UDP server")
        await self.udp_server.stop_server()

async def main():
    """Main function to run the example server."""
    server = SimpleSipUdpServer()
    
    try:
        await server.start()
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
