import unittest
import context
import sys

from sipapy.SipURL import SipURL

class TestURL(unittest.TestCase):
    def test_url(self):
        test_set = (('sip:user;par=u%40example.net@example.com', ()),
                #('sip:user@example.com?Route=%3Csip:example.com%3E', ()),
                ('sip:[2001:db8::10]', ()),
                ('sip:[2001:db8::10]:5070', ()),
                ('sip:user@example.net;tag=9817--94', ('tag=9817--94',)),
                ('sip:alice@atlanta.com;ttl=15;maddr=239.255.255.1',
                 ('ttl=15', 'maddr=239.255.255.1')),
                ('sip:alice:secretword@atlanta.com;transport=tcp', ('transport=tcp',)),
                ('sip:alice@atlanta.com?subject=project%20x&priority=urgent', ()),
                ('sip:+1-212-555-1212:1234@gateway.com;user=phone', ('user=phone',)),
                ('sip:atlanta.com;method=REGISTER?to=alice%40atlanta.com',
                 ('method=REGISTER',)),
                ('sip:alice;day=tuesday@atlanta.com', ()),
                ('sip:+611234567890@ims.mnc000.mcc000.3gppnetwork.org;user=phone;npdi',
                 ('user=phone', 'npdi')),
                ('sip:1234#567890@example.com', ()),
                #('sip:foo@1.2.3.4:', ()),
                #('sip:foo@1.2.3.4:5060:5060', ())
                )
        for u, mp in test_set:
            su = SipURL(u)
            sp = su.getParams()
            print((tuple(sp), mp, su.getHost(), su.getPort()))
            self.assertEqual(str(su), u)
