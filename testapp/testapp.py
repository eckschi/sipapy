
import context
import asyncio
from sipapy.SipCore import SipCore


def recvRequest(self, req, sip_t):
    # search for exisitng call and forward request if found
    callid = None
    cidhf = req.getHFBody('call-id')
    if cidhf is not None:
        callid = str(cidhf).split("@")[0]
        call = self.sipCalls.get(callid, None)
        if call is not None:
            return call.recvRequest(req, sip_t)

    # incoming call
    if req.getMethod() == 'INVITE':
        resp = req.genResponse(200, 'OK', None)
        return (resp, None, None)


def _recvResponse(self, resp, tr):
    cidhf = resp.getHFBody('call-id')
    if cidhf is not None:
        callid = str(cidhf).split("@")[0]
        call = self.sipCalls.get(callid, None)
        if call is not None:
            return call.recvResponse(resp, tr)

    # old code and global sip requests
    if resp.reason == "OK":
        pass
    # missing ack for invite ...


async def main():
    sc = SipCore(recvRequest)
    sc.start()

    try:
        await asyncio.gather(sc.server_task)
    except asyncio.CancelledError:
        print("Received KeyboardInterrupt, shutting down...")
        # Stop the server and clean up resources
        sc.stop()
        await sc.server_task  # Wait for server task to close gracefully
        print("Server shut down gracefully.")

if __name__ == '__main__':

    asyncio.run(main())
