#!/usr/bin/env python3
"""
Unified SDP parser tests.

This file consolidates all SDP parsing tests from test_sdp_conversion.py and test_sdp.py
with meaningful test names that describe what each test is actually testing.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sipapy.SdpBody import SdpBody
from sipapy.SdpMediaDescription import SdpMediaDescription, MediaType
from sipapy.SdpCodecInfo import SdpCodecInfo, Codec
from sipapy.SdpOrigin import SdpOrigin
from sipapy.SdpConnection import SdpConnection


class TestSdpParser(unittest.TestCase):
    """Test SDP parsing functionality."""

    # Tests from test_sdp_conversion.py - renamed with meaningful names
    def test_parse_basic_sdp_with_connection_address_ttl(self):
        """Test parsing SDP with connection address including TTL and bandwidth."""
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

    def test_parse_sdp_with_different_origin_and_connection_addresses(self):
        """Test parsing SDP where origin and connection addresses differ."""
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

    def test_parse_sdp_with_long_username(self):
        """Test parsing SDP with a long username in origin field."""
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

    def test_parse_sdp_with_multiple_media_types(self):
        """Test parsing SDP containing both audio and video media descriptions."""
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

    def test_parse_sdp_with_ice_attributes_and_multiple_formats(self):
        """Test parsing SDP with ICE attributes and multiple payload formats."""
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

    # Tests from test_sdp.py - renamed with meaningful names
    def test_parse_simple_sdp_with_multiple_codecs(self):
        """Test parsing a simple SDP with multiple audio codecs."""
        sdp_data = (
            'v=0\r\n'
            'o=- 3966682764 3966682764 IN IP4 10.172.68.90\r\n'
            's=pjmedia\r\n'
            'b=AS:84\r\n'
            't=0 0\r\n'
            'a=X-nat:0\r\n'
            'm=audio 4014 RTP/AVP 8 0 101\r\n'
            'c=IN IP4 10.172.68.90\r\n'
            'b=TIAS:64000\r\n'
            'a=rtcp:4015 IN IP4 10.172.68.90\r\n'
            'a=sendrecv\r\n'
            'a=rtpmap:8 PCMA/8000\r\n'
            'a=rtpmap:0 PCMU/8000\r\n'
            'a=rtpmap:101 telephone-event/8000\r\n'
            'a=fmtp:101 0-16\r\n'
            'a=ssrc:1060656687 cname:5025109619374fa3\r\n')

        sdp = SdpBody.from_string(sdp_data)
        self.assertEqual(sdp.v_header, '0')

        self.assertEqual(len(sdp.media_lines), 1)
        self.assertEqual(sdp.media_lines[0].type, MediaType.AUDIO)
        self.assertEqual(sdp.media_lines[0].port, 4014)
        self.assertEqual(sdp.media_lines[0].c_header.addr, '10.172.68.90')
        self.assertEqual(sdp.media_lines[0].formats, [8, 0, 101])

    def test_parse_rfc4566_compliant_sdp(self):
        """Test parsing SDP compliant with RFC 4566 including optional fields."""
        sdp_data = (
            'v=0\r\n'
            'o=jdoe 2890844526 2890842807 IN IP4 10.47.16.5\r\n'
            's=SDP Seminar\r\n'
            'i=A Seminar on the session description protocol\r\n'
            'u=http://www.example.com/seminars/sdp.pdf\r\n'
            'e=j.doe@example.com (Jane Doe)\r\n'
            'c=IN IP4 224.2.17.12/127\r\n'
            't=2873397496 2873404696\r\n'
            'a=recvonly\r\n'
            'm=audio 49170 RTP/AVP 0\r\n'
            'm=video 51372 RTP/AVP 99\r\n'
            'a=rtpmap:99 h263-1998/90000\r\n')
        sdp = SdpBody.from_string(sdp_data)
        self.assertEqual(sdp.v_header, '0')
        self.assertEqual(sdp.o_header.username, 'jdoe')
        self.assertEqual(sdp.o_header.session_id, '2890844526')
        self.assertEqual(sdp.o_header.version, '2890842807')
        self.assertEqual(sdp.o_header.network_type, 'IN')
        self.assertEqual(sdp.o_header.address_type, 'IP4')
        self.assertEqual(sdp.o_header.address, '10.47.16.5')

        self.assertEqual(sdp.s_header, 'SDP Seminar')
        self.assertEqual(sdp.i_header, 'A Seminar on the session description protocol')
        self.assertEqual(sdp.u_header, 'http://www.example.com/seminars/sdp.pdf')
        self.assertEqual(sdp.e_header, 'j.doe@example.com (Jane Doe)')
        
        # self.assertEqual(sdp.c_header.addr, '224.2.17.12/127')
        self.assertEqual(sdp.t_header,'2873397496 2873404696')
        self.assertEqual(len(sdp.media_lines), 2)
        self.assertEqual(sdp.media_lines[0].port, 49170)
        self.assertEqual(sdp.media_lines[0].c_header.addr, '224.2.17.12/127')
        self.assertEqual(sdp.media_lines[0].type, MediaType.AUDIO)

    def test_parse_sdp_with_multiple_media_and_codec_details(self):
        """Test parsing SDP with multiple media types and detailed codec information."""
        sdp_data = (
            'v=0\r\n'
            'o=jdoe 3724394400 3724394405 IN IP4 198.51.100.1\r\n'
            's=-\r\n'
            'b=AS:1920\r\n'
            'c=IN IP4 198.51.100.1\r\n'
            't=0 0\r\n'
            'm=audio 49170 RTP/AVP 114 101\r\n'
            'a=rtpmap:114 opus/48000/2\r\n'
            'a=fmtp:114 useinbandfec=1;stereo=1\r\n'
            'a=rtpmap:101 telephone-event/8000\r\n'
            'a=fmtp:101 0-15\r\n'
            'm=video 50000 RTP/AVP 97 98\r\n'
            'a=rtpmap:97 VP8/90000\r\n'
            'a=rtpmap:98 H264/90000\r\n')
        sdp = SdpBody.from_string(sdp_data)
        self.assertEqual(sdp.v_header, '0')
        self.assertEqual(len(sdp.media_lines), 2)
        self.assertEqual(sdp.media_lines[0].port, 49170)
        self.assertEqual(sdp.media_lines[0].c_header.addr, '198.51.100.1')
        self.assertEqual(sdp.media_lines[0].type, MediaType.AUDIO)
        self.assertEqual(sdp.media_lines[0].formats, [114, 101])
        self.assertEqual(len(sdp.media_lines[0].codecs), 2)
        self.assertEqual(sdp.media_lines[0].codecs[114].codec, Codec.OPUS)
        self.assertEqual(sdp.media_lines[0].codecs[114].clock_rate, 48000)
        self.assertEqual(sdp.media_lines[0].codecs[114].channels, 2)
        self.assertEqual(sdp.media_lines[0].codecs[114].fmtp, 'useinbandfec=1;stereo=1')

        self.assertEqual(sdp.media_lines[1].port, 50000)
        self.assertEqual(sdp.media_lines[1].c_header.addr, '198.51.100.1')
        self.assertEqual(sdp.media_lines[1].type, MediaType.VIDEO)
        self.assertEqual(sdp.media_lines[1].formats, [97, 98])
        self.assertEqual(len(sdp.media_lines[1].codecs), 2)
        self.assertEqual(sdp.media_lines[1].codecs[97].codec, Codec.VP8)
        self.assertEqual(sdp.media_lines[1].codecs[97].clock_rate, 90000)
        self.assertEqual(sdp.media_lines[1].codecs[98].codec, Codec.H264)
        self.assertEqual(sdp.media_lines[1].codecs[98].clock_rate, 90000)

    def test_sdp_generation(self):
        """Test SDP generation functionality."""
        expected_output = "v=0\r\n"\
            "o=- 1 1000 IN IP4 192.168.56.50\r\n"\
            "s=QC VOIP\r\n"\
            "c=IN IP4 192.168.56.50\r\n"\
            "t=0 0\r\n"\
            "m=audio 46000 RTP/AVP 104 9 102 8 0 96 97\r\n"\
            "a=rtpmap:104 AMR-WB/16000/1\r\n"\
            "a=fmtp:104 mode-change-capability=2; max-red=0\r\n"\
            "a=rtpmap:9 G722/8000\r\n"\
            "a=rtpmap:102 AMR/8000/1\r\n"\
            "a=fmtp:102 mode-change-capability=2; max-red=0\r\n"\
            "a=rtpmap:8 PCMA/8000\r\n"\
            "a=rtpmap:0 PCMU/8000\r\n"\
            "a=rtpmap:96 telephone-event/16000\r\n"\
            "a=fmtp:96 0-15\r\n"\
            "a=rtpmap:97 telephone-event/8000\r\n"\
            "a=fmtp:97 0-15\r\n"\
            "a=sendrecv\r\n"\
            "a=maxptime:40\r\n"\
            "a=ptime:20\r\n"

        sdp = SdpBody.from_values(
            subject="QC VOIP",
            origin=SdpOrigin(address='192.168.56.50'),
            connection=SdpConnection.from_values(
                ntype='IN',
                atype='IP4',
                addr='192.168.56.50')
        )
        sdp.media_lines.append(SdpMediaDescription.from_values(46000, 8, Codec.PCMA, 8000, 1))
        print(sdp)

        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()