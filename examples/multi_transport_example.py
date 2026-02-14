#!/usr/bin/env python3
"""
Example showing how to use the new multi-transport system in SipCore.

This example demonstrates how to create a SIP server that supports both TCP and UDP transports.
"""

import asyncio
from sipapy.SipCore import SipCore, TransportType
from sipapy.SipResponse import SipResponse

async def main():
    # Define a simple callback that handles incoming SIP requests
    async def handle_request(msg, transaction):
        print(f"Received {msg.getMethod()} request from {msg.getSource()}")
        
        # Generate a simple 200 OK response
        response = msg.genResponse(200, "OK")
        return response
    
    # Create SipCore with both TCP and UDP transport support
    # Default is TCP-only, so we need to explicitly add UDP
    sip_core = SipCore(handle_request, transports=[TransportType.TCP, TransportType.UDP])
    
    print("Starting SIP server with TCP and UDP support...")
    print(f"Available transports: {[t.get_transport_type() for t in sip_core.transports]}")
    
    # Start the server on port 5060
    sip_core.start('0.0.0.0', 5060)
    
    print("SIP server running. Press Ctrl+C to stop.")
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping SIP server...")
        await sip_core.stop()
        print("SIP server stopped.")

if __name__ == "__main__":
    asyncio.run(main())