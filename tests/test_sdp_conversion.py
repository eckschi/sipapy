import unittest
import context
from sipapy.SdpBody import SdpBody

class TestSdpConversion(unittest.TestCase):
    def test_example_1(self):
        sdp_body = """v=0
o=Evil 3559 3228 IN IP4 192.168.2.122
s=SIP Call
t=0 0
m=audio 17124 RTP/AVP 18
c=IN IP4 192.168.2.122/127/2000000000
a=rtpmap:18 G729/8000
"""
        sdp = SdpBody.from_string(sdp_body)
        self.assertEqual(sdp.v_header, '0')
        self.assertEqual(sdp.o_header.username, "Evil")
        self.assertEqual(sdp.o_header.session_id, "3559")
        self.assertEqual(sdp.o_header.version, "3228")
        self.assertEqual(sdp.o_header.network_type, "IN")
        self.assertEqual(sdp.o_header.address_type, "IP4")
        self.assertEqual(sdp.o_header.address, "192.168.2.122")
        self.assertEqual(sdp.s_header, "SIP Call")
        self.assertEqual(sdp.t_header, "0 0")
        self.assertEqual(len(sdp.media_lines), 1)
        media = sdp.media_lines[0]
        self.assertEqual(media.stype, "audio")
        self.assertEqual(media.port, 17124)
        self.assertEqual(media.transport, "RTP/AVP")
        self.assertEqual(media.formats, [18])
        self.assertEqual(media.c_header.ntype, "IN")
        self.assertEqual(media.c_header.atype, "IP4")
        self.assertEqual(media.c_header.addr, "192.168.2.122/127/2000000000")
        self.assertEqual(len(media.other_attributes), 1)
        self.assertEqual(media.other_attributes[0].name, "rtpmap")
        self.assertEqual(media.other_attributes[0].value, "18 G729/8000")
    def test_example_2(self):
        sdp_body = """v=0
o=UserA 2890844526 2890844527 IN IP4 here.com
s=Session SDP
c=IN IP4 pc33.atlanta.com
t=5 17
m=audio 49172 RTP/AVP 0
a=rtpmap:0 PCMU/8000
"""
        sdp = SdpBody.from_string(sdp_body)
        self.assertEqual(sdp.v_header, '0')
        self.assertEqual(sdp.o_header.username, "UserA")
        self.assertEqual(sdp.o_header.session_id, "2890844526")
        self.assertEqual(sdp.o_header.version, "2890844527")
        self.assertEqual(sdp.o_header.network_type, "IN")
        self.assertEqual(sdp.o_header.address_type, "IP4")
        self.assertEqual(sdp.o_header.address, "here.com")
        self.assertEqual(sdp.s_header, "Session SDP")
        self.assertEqual(sdp.t_header, "5 17")
        self.assertEqual(len(sdp.media_lines), 1)
        media = sdp.media_lines[0]
        self.assertEqual(media.stype, "audio")
        self.assertEqual(media.port, 49172)
        self.assertEqual(media.transport, "RTP/AVP")
        self.assertEqual(media.formats, [0])
        self.assertEqual(media.c_header.ntype, "IN")
        self.assertEqual(media.c_header.atype, "IP4")
        self.assertEqual(media.c_header.addr, "pc33.atlanta.com")
        self.assertEqual(len(media.other_attributes), 1)
        self.assertEqual(media.other_attributes[0].name, "rtpmap")
        self.assertEqual(media.other_attributes[0].value, "0 PCMU/8000")
    def test_example_3(self):
        sdp_body = """v=0
o=CiscoSystemsSIP-GW-UserAgent 3559 3228 IN IP4 192.168.2.122
s=SIP Call
c=IN IP4 192.168.2.122
t=0 0
m=audio 17124 RTP/AVP 18
a=rtpmap:18 G729/8000
"""
        sdp = SdpBody.from_string(sdp_body)
        self.assertEqual(sdp.v_header, '0')
        self.assertEqual(sdp.o_header.username, "CiscoSystemsSIP-GW-UserAgent")
        self.assertEqual(sdp.o_header.session_id, "3559")
        self.assertEqual(sdp.o_header.version, "3228")
        self.assertEqual(sdp.o_header.network_type, "IN")
        self.assertEqual(sdp.o_header.address_type, "IP4")
        self.assertEqual(sdp.o_header.address, "192.168.2.122")
        self.assertEqual(sdp.s_header, "SIP Call")
        self.assertEqual(sdp.t_header, "0 0")
        self.assertEqual(len(sdp.media_lines), 1)
        media = sdp.media_lines[0]
        self.assertEqual(media.stype, "audio")
        self.assertEqual(media.port, 17124)
        self.assertEqual(media.transport, "RTP/AVP")
        self.assertEqual(media.formats, [18])
        self.assertEqual(media.c_header.ntype, "IN")
        self.assertEqual(media.c_header.atype, "IP4")
        self.assertEqual(media.c_header.addr, "192.168.2.122")
        self.assertEqual(len(media.other_attributes), 1)
        self.assertEqual(media.other_attributes[0].name, "rtpmap")
        self.assertEqual(media.other_attributes[0].value, "18 G729/8000")
    def test_example_4(self):
        sdp_body = """v=0
o=UserA 2890844526 2890844527 IN IP4 here.com
s=Session SDP
c=IN IP4 pc33.atlanta.com
t=0 0
m=audio 49172 RTP/AVP 0
a=rtpmap:0 PCMU/8000
m=video 51372 RTP/AVP 31
a=rtpmap:31 H261/90000
"""
        sdp = SdpBody.from_string(sdp_body)
        self.assertEqual(sdp.v_header, '0')
        self.assertEqual(sdp.o_header.username, "UserA")
        self.assertEqual(sdp.o_header.session_id, "2890844526")
        self.assertEqual(sdp.o_header.version, "2890844527")
        self.assertEqual(sdp.o_header.network_type, "IN")
        self.assertEqual(sdp.o_header.address_type, "IP4")
        self.assertEqual(sdp.o_header.address, "here.com")
        self.assertEqual(sdp.s_header, "Session SDP")
        self.assertEqual(sdp.t_header, "0 0")
        self.assertEqual(len(sdp.media_lines), 2)
        
        # Test audio media
        media_audio = sdp.media_lines[0]
        self.assertEqual(media_audio.stype, "audio")
        self.assertEqual(media_audio.port, 49172)
        self.assertEqual(media_audio.transport, "RTP/AVP")
        self.assertEqual(media_audio.formats, [0])
        self.assertEqual(media_audio.c_header.ntype, "IN")
        self.assertEqual(media_audio.c_header.atype, "IP4")
        self.assertEqual(media_audio.c_header.addr, "pc33.atlanta.com")
        self.assertEqual(len(media_audio.other_attributes), 1)
        self.assertEqual(media_audio.other_attributes[0].name, "rtpmap")
        self.assertEqual(media_audio.other_attributes[0].value, "0 PCMU/8000")

        # Test video media
        media_video = sdp.media_lines[1]
        self.assertEqual(media_video.stype, "video")
        self.assertEqual(media_video.port, 51372)
        self.assertEqual(media_video.transport, "RTP/AVP")
        self.assertEqual(media_video.formats, [31])
        self.assertEqual(media_video.c_header.ntype, "IN")
        self.assertEqual(media_video.c_header.atype, "IP4")
        self.assertEqual(media_video.c_header.addr, "pc33.atlanta.com")
        self.assertEqual(len(media_video.other_attributes), 1)
        self.assertEqual(media_video.other_attributes[0].name, "rtpmap")
        self.assertEqual(media_video.other_attributes[0].value, "31 H261/90000")
    def test_example_5(self):
        sdp_body = """v=0
o=- 3603282031 3603282031 IN IP4 192.168.2.181
s=talk
t=0 0
a=ice-ufrag:8e68e7343c0a48a6a612c6f39d745863
a=ice-pwd:3b63a436971b4021a814a0a430198084
m=audio 5062 RTP/AVP 0 101
c=IN IP4 192.168.2.181
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=sendrecv
"""
        sdp = SdpBody.from_string(sdp_body)
        self.assertEqual(sdp.v_header, '0')
        self.assertEqual(sdp.o_header.username, "-")
        self.assertEqual(sdp.o_header.session_id, "3603282031")
        self.assertEqual(sdp.o_header.version, "3603282031")
        self.assertEqual(sdp.o_header.network_type, "IN")
        self.assertEqual(sdp.o_header.address_type, "IP4")
        self.assertEqual(sdp.o_header.address, "192.168.2.181")
        self.assertEqual(sdp.s_header, "talk")
        self.assertEqual(sdp.t_header, "0 0")
        
        # Test session-level attributes
        self.assertEqual(len(sdp.a_headers), 2)
        self.assertEqual(sdp.a_headers[0].name, "ice-ufrag")
        self.assertEqual(sdp.a_headers[0].value, "8e68e7343c0a48a6a612c6f39d745863")
        self.assertEqual(sdp.a_headers[1].name, "ice-pwd")
        self.assertEqual(sdp.a_headers[1].value, "3b63a436971b4021a814a0a430198084")

        # Test media descriptions
        self.assertEqual(len(sdp.media_lines), 1)
        media = sdp.media_lines[0]
        self.assertEqual(media.stype, "audio")
        self.assertEqual(media.port, 5062)
        self.assertEqual(media.transport, "RTP/AVP")
        self.assertEqual(media.formats, [0, 101])
        self.assertEqual(media.c_header.ntype, "IN")
        self.assertEqual(media.c_header.atype, "IP4")
        self.assertEqual(media.c_header.addr, "192.168.2.181")
        
        # Test media-level attributes
        self.assertEqual(len(media.other_attributes), 4)
        self.assertEqual(media.other_attributes[0].name, "rtpmap")
        self.assertEqual(media.other_attributes[0].value, "0 PCMU/8000")
        self.assertEqual(media.other_attributes[1].name, "rtpmap")
        self.assertEqual(media.other_attributes[1].value, "101 telephone-event/8000")
        self.assertEqual(media.other_attributes[2].name, "fmtp")
        self.assertEqual(media.other_attributes[2].value, "101 0-15")
        self.assertEqual(media.other_attributes[3].name, "sendrecv")
        self.assertIsNone(media.other_attributes[3].value)

    if __name__ == "__main__":

        unittest.main()

    