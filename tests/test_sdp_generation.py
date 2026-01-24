import unittest
import context
from sipapy.SdpBody import SdpBody
from sipapy.SdpOrigin import SdpOrigin
from sipapy.SdpMediaDescription import SdpMediaDescription

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

    def test_roundtrip_example_1(self):
        sdp_body = """v=0\r
o=Evil 3559 3228 IN IP4 192.168.2.122\r
s=SIP Call\r
t=0 0\r
m=audio 17124 RTP/AVP 18\r
c=IN IP4 192.168.2.122/127/2000000000\r
a=rtpmap:18 G729/8000\r
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
a=rtpmap:0 PCMU/8000\r
"""
        sdp = SdpBody.from_string(sdp_body)
        self.assertEqual(str(sdp).strip(), sdp_body.strip())

if __name__ == "__main__":
    unittest.main()