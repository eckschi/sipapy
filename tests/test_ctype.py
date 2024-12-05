import unittest
import context

from sipapy.SipContentType import SipContentType

class TestContentType(unittest.TestCase):
    def test_normal_ctype(self):
        t = 'multipart/mixed;boundary=OSS-unique-boundary-42'
        ct1 = SipContentType(t)
        ct1.parse()
        self.assertEqual(f'{ct1}', t)
        self.assertEqual(ct1.name, 'multipart/mixed')
        self.assertEqual(ct1.params['boundary'], 'OSS-unique-boundary-42')
        ct2 = ct1.getCopy()
        self.assertEqual(f'{ct2}', t)
        ct1.params['some'] = 'value'
        self.assertEqual(f'{ct1}' , t + ';some=value')
        self.assertEqual(f'{ct2}',  t)
