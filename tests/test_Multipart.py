import unittest
import context

from sipapy.MsgBody import MsgBody
from sipapy.MultipartMixBody import MultipartMixBody
from sipapy.SipContentType import SipContentType

# body from RFC 8147 https://datatracker.ietf.org/doc/html/rfc8147
ECALL_BODY1 = (
    "--boundaryZZZ\r\n"
    "Content-Disposition: by-reference\r\n"
    "Content-Type: application/EmergencyCallData.Control+xml\r\n"
    "Content-ID: <3456789012@atlanta.example.com>\r\n"
    "\r\n"
    '<?xml version="1.0" encoding="UTF-8"?>\r\n'
    '<EmergencyCallData.Control xmlns="urn:ietf:params:xml:ns:EmergencyCallData:control">\r\n'
    '<request action="send-data" datatype="eCall.MSD"/>\r\n'
    "</EmergencyCallData.Control>\r\n"
    "--boundaryZZZ--\r\n"
)


class TestMultipart(unittest.TestCase):
    def test_run(self):
        ct = SipContentType("multipart/mixed;boundary=boundaryZZZ")
        ct.parse()
        got = MsgBody(ECALL_BODY1, mtype=ct)
        got.parse()
        mp = got.content
        self.assertEqual(MultipartMixBody, type(mp))
        self.assertEqual(1, len(mp.parts))
        p0 = mp.parts[0]
        self.assertEqual(MsgBody, type(p0))
        print(p0.mtype)
        self.assertEqual("application/EmergencyCallData.Control+xml", p0.mtype.localStr())
        h0 = mp.part_headers[0]
        self.assertEqual("content-disposition", h0[0].name)
        self.assertEqual("content-id", h0[1].name)
