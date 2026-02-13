import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sipapy.SdpBody import SdpBody
from sipapy.SdpOrigin import SdpOrigin
from sipapy.SdpMediaDescription import SdpMediaDescription, MediaType
from sipapy.SdpConnection import SdpConnection
from sipapy.SdpGeneric import SdpGeneric

class TestSdpGeneration(unittest.TestCase):
    def test_generation_1(self):
        origin = SdpOrigin(address="192.168.2.220")
        sdp = SdpBody.from_values(subject="Test Session", origin=origin)
        media = SdpMediaDescription.from_values(port=5061, rtpmap=0, codec="PCMU", clock_rate=8000)
        sdp.media_lines.append(media)

        expected_sdp = """v=0\r
o=- %s %s IN IP4 192.168.2.220\r
s=Test Session\r
t=0 0\r
m=audio 5061 RTP/AVP 0\r
a=rtpmap:0 PCMU/8000/1\r
""" % (origin.session_id, origin.version)

        self.assertEqual(str(sdp).strip(), expected_sdp.strip())

    def test_full_sdp_generation_with_session_attributes(self):
        origin = SdpOrigin(address="192.168.1.100")
        origin.username = "testuser"
        connection = SdpConnection.from_values("IN", "IP4", "192.168.1.100")
        sdp = SdpBody.from_values(subject="Complex Session", origin=origin, connection=connection)
        
        sdp.i_header = SdpGeneric("A longer session description")
        sdp.b_header = SdpGeneric("AS:1000")
        sdp.a_headers.append(SdpGeneric("x-custom-attribute:somevalue"))

        # Add an audio media description
        audio_media = SdpMediaDescription.from_values(port=5000, rtpmap=0, codec="PCMU", clock_rate=8000)
        audio_media.addHeader('a', 'ptime:20')
        audio_media.addHeader('a', 'sendrecv')
        sdp.media_lines.append(audio_media)

        # Add a video media description
        video_media = SdpMediaDescription.from_values(port=5002, rtpmap=100, codec="VP8", clock_rate=90000, type=MediaType.VIDEO)
        video_media.addHeader('a', 'fmtp:100 profile-level-id=42e01f;packetization-mode=1')
        video_media.addHeader('a', 'recvonly')
        sdp.media_lines.append(video_media)

        expected_sdp_template = """v=0\r
o=testuser %s %s IN IP4 192.168.1.100\r
s=Complex Session\r
i=A longer session description\r
c=IN IP4 192.168.1.100\r
b=AS:1000\r
t=0 0\r
a=x-custom-attribute:somevalue\r
m=audio 5000 RTP/AVP 0\r
a=rtpmap:0 PCMU/8000/1\r
a=ptime:20\r
a=sendrecv\r
m=video 5002 RTP/AVP 100\r
a=rtpmap:100 VP8/90000/1\r
a=fmtp:100 profile-level-id=42e01f;packetization-mode=1\r
a=recvonly"""

        # We need to get the dynamic session_id and version from the created SdpOrigin object
        expected_sdp = expected_sdp_template % (origin.session_id, origin.version)
        
        generated_sdp = str(sdp).strip()
        self.assertEqual(generated_sdp, expected_sdp.strip())

        # Round-trip test
        parsed_sdp = SdpBody.from_string(expected_sdp)
        self.assertEqual(str(parsed_sdp).strip(), expected_sdp.strip())

    def test_roundtrip_example_1(self):
        sdp_body = """v=0\r
o=Evil 3559 3228 IN IP4 192.168.2.122\r
s=SIP Call\r
t=0 0\r
m=audio 17124 RTP/AVP 18\r
c=IN IP4 192.168.2.122/127/2000000000\r
a=rtpmap:18 G729/8000/1\r
"""
        sdp = SdpBody.from_string(sdp_body)
        self.assertEqual(str(sdp).strip(), sdp_body.strip())

    def test_roundtrip_example_2(self):
        sdp_body = """v=0\r
o=UserA 2890844526 2890844527 IN IP4 here.com\r
s=Session SDP\r
c=IN IP4 pc33.atlanta.com\r
t=5 17\r
m=audio 49172 RTP/AVP 0\r
a=rtpmap:0 PCMU/8000/1""" # No trailing \r\n, as it's stripped by .strip()
        sdp = SdpBody.from_string(sdp_body)
        self.assertEqual(str(sdp).strip(), sdp_body.strip())

    def test_ipv6_and_attributes(self):
        origin = SdpOrigin(address="2001:db8::1")
        origin.address_type = 'IP6'
        connection = SdpConnection.from_values("IN", "IP6", "2001:db8::2")
        sdp = SdpBody.from_values(subject="IPv6 Session", origin=origin, connection=connection)

        sdp.k_header = SdpGeneric("clear:password")

        # Audio stream - sendonly
        audio_media = SdpMediaDescription.from_values(port=5004, rtpmap=8, codec="PCMA", clock_rate=8000)
        audio_media.addHeader('a', 'sendonly')
        sdp.media_lines.append(audio_media)

        # Video stream - inactive
        video_media = SdpMediaDescription.from_values(port=5006, rtpmap=101, codec="H264", clock_rate=90000, type=MediaType.VIDEO)
        video_media.addHeader('a', 'inactive')
        sdp.media_lines.append(video_media)

        expected_sdp_template = """v=0\r
o=- %s %s IN IP6 2001:db8::1\r
s=IPv6 Session\r
c=IN IP6 2001:db8::2\r
t=0 0\r
k=clear:password\r
m=audio 5004 RTP/AVP 8\r
a=rtpmap:8 PCMA/8000/1\r
a=sendonly\r
m=video 5006 RTP/AVP 101\r
a=rtpmap:101 H264/90000/1\r
a=inactive"""

        expected_sdp = expected_sdp_template % (origin.session_id, origin.version)
        generated_sdp = str(sdp).strip()
        self.assertEqual(generated_sdp, expected_sdp.strip())

        # Round-trip test
        parsed_sdp = SdpBody.from_string(expected_sdp)
        self.assertEqual(str(parsed_sdp).strip(), expected_sdp.strip())

if __name__ == "__main__":
    unittest.main()