
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sipapy.SipCore import SipCore
from sipapy.SipWWWAuthenticate import SipWWWAuthenticate
from sipapy.SipAuthorization import SipAuthorization

# Simple user database for authentication
user_db = {
    '100': {'password': 'password123', 'realm': 'sipapy.local'},
    '101': {'password': 'secret456', 'realm': 'sipapy.local'},
    'alice': {'password': 'alicepass', 'realm': 'sipapy.local'},
    'bob': {'password': 'bobpass', 'realm': 'sipapy.local'}
}

# Store active registrations
registrations = {}

# Store authentication challenges (nonce -> user_data)
auth_challenges = {}

def get_user_credentials(username):
    """Get user credentials from the database"""
    return user_db.get(username)

def handle_register_request(req):
    """Handle REGISTER requests with authentication"""
    
    # Extract username from the To header
    to_header = req.getHFBody('to')
    if to_header is None:
        return req.genResponse(400, 'Bad Request - Missing To header', None)
    
    username = to_header.getDisplayName() or to_header.getUser()
    if not username:
        return req.genResponse(400, 'Bad Request - Invalid To header', None)
    
    # Check if this is a new registration or refresh
    contact_header = req.getHFBody('contact')
    expires_header = req.getHFBody('expires')
    
    # Check for Authorization header
    auth_header = req.getHFBody('authorization')
    
    if auth_header is None:
        # No authorization - send 407 Unauthorized with WWW-Authenticate challenge
        www_auth = SipWWWAuthenticate(realm='sipapy.local', algorithm='MD5')
        resp = req.genResponse(407, 'Proxy Authentication Required', None)
        resp.addHeader('WWW-Authenticate', www_auth)
        
        # Store the challenge for this user
        auth_challenges[www_auth.getNonce()] = {
            'username': username,
            'method': req.getMethod(),
            'uri': str(req.getHFBody('request-line')).split(' ')[1]
        }
        
        return resp
    else:
        # Verify the authorization
        user_creds = get_user_credentials(username)
        if user_creds is None:
            return req.genResponse(401, 'Unauthorized - Invalid credentials', None)
        
        # Check if this is a valid authorization for our challenge
        if auth_header.getRealm() != 'sipapy.local':
            return req.genResponse(401, 'Unauthorized - Wrong realm', None)
        
        # Verify the response
        expected_auth = SipWWWAuthenticate(realm='sipapy.local', nonce=auth_header.getNonce())
        expected_auth_response = expected_auth.genAuthHF(
            username=username,
            password=user_creds['password'],
            method=req.getMethod(),
            uri=str(req.getHFBody('request-line')).split(' ')[1]
        )
        
        if auth_header.getResponse() != expected_auth_response.getResponse():
            return req.genResponse(401, 'Unauthorized - Invalid response', None)
        
        # Authentication successful - process registration
        if contact_header:
            contact_uri = str(contact_header.getUrl())
            expires = 3600  # Default expires
            if expires_header:
                try:
                    expires = int(expires_header.getNum())
                except:
                    expires = 3600
            
            # Store or update registration
            registrations[username] = {
                'contact': contact_uri,
                'expires': expires,
                'registered_at': asyncio.get_event_loop().time()
            }
            
            print(f"User {username} registered with contact {contact_uri} (expires in {expires}s)")
            return req.genResponse(200, 'OK', None)
        else:
            return req.genResponse(400, 'Bad Request - Missing Contact header', None)


def recvRequest(req, sip_t):
    # search for exisitng call and forward request if found
    # callid = None
    # cidhf = req.getHFBody('call-id')
    # if cidhf is not None:
    #     callid = str(cidhf).split("@")[0]
    #     call = self.sipCalls.get(callid, None)
    #     if call is not None:
    #         return call.recvRequest(req, sip_t)

    # incoming call
    if req.getMethod() == 'INVITE':
        resp = req.genResponse(180, 'Ringing', None)
        # resp = req.genResponse(200, 'OK', None)
        return (resp, None, None)
    elif req.getMethod() == 'REGISTER':
        return handle_register_request(req), None, None
    elif req.getMethod() == 'PUBLISH':
        print("publish")
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
    sc.start(host='0.0.0.0', port=5061)  # Bind to all interfaces on port 5061

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
