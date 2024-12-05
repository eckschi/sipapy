import unittest
import context
import sys

from sipapy.SipReason import SipReason

class TestReason(unittest.TestCase):
    def test_reason(self):
        ours = 'Reason: Q.850; cause=31; text="db4e8de3-ef1e-4427-b6b8-afc339de9f0d;Callee only had Trouter endpoints registered and PNH got delivery errors from all of them."'
        tset = (ours, 'Reason: Q.850;cause=31;text="db4e8de3-ef1e-4427-b6b8-afc339de9f0d;Callee only had Trouter endpoints registered and PNH got delivery errors from all of them."',
            'Reason: Q.850 ; cause= 31;   text=  "db4e8de3-ef1e-4427-b6b8-afc339de9f0d;Callee only had Trouter endpoints registered and PNH got delivery errors from all of them."     ',
            'Reason: Q.850 ;    text=  "db4e8de3-ef1e-4427-b6b8-afc339de9f0d;Callee only had Trouter endpoints registered and PNH got delivery errors from all of them."   ; cause= 31  ')
        for r in tset:
            s = SipReason(r)
            s.parse()
            self.assertEqual(str(s), ours)

