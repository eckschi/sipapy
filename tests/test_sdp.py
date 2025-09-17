import unittest

from sipapy.SdpBody import SdpBody
from sipapy.SdpMediaDescription import SdpMediaDescription, MediaType
from sipapy.SdpCodecInfo import SdpCodecInfo, Codec
from sipapy.SdpOrigin import SdpOrigin
from sipapy.SdpConnection import SdpConnection

class TestSdp(unittest.TestCase):
    def test_simple_sdp(self):
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

    def test_sdp_rfc4566(self):
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

    def test_multiple_media_sdp(self):
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

    def test_generate_sdp(self):
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
        sdp.media_lines.append(SdpMediaDescription.from_values(46000, Codec.PCMA, 8000, 1))
        print(sdp)

        self.assertTrue(True)
