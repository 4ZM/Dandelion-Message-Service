"""
Copyright (c) 2011 Anders Sundman <anders@4zm.org>

This file is part of Dandelion Messaging System.

Dandelion is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Dandelion is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Dandelion.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
from dandelion.util import encode_b64_bytes, encode_b64_int, decode_b64_bytes, decode_b64_int

class UtilTest(unittest.TestCase):
    
    def test_encode_bytes(self):
        
        self.assertEqual(encode_b64_bytes(b''), b'')
        self.assertEqual(encode_b64_bytes(b'\x00\x00\x00'), b'AAAA')
        self.assertEqual(encode_b64_bytes(b'\xFF\xFF\xFF'), b'////')
        self.assertEqual(encode_b64_bytes(b'123'), b'MTIz')
        self.assertEqual(encode_b64_bytes(bytearray(b'123')), b'MTIz')
        self.assertEqual(encode_b64_bytes(b'1337'), b'MTMzNw==')
        
        self.assertRaises(TypeError, encode_b64_bytes, None)
        self.assertRaises(TypeError, encode_b64_bytes, '1337')
        self.assertRaises(TypeError, encode_b64_bytes, 1337)
        
    def test_decode_bytes(self):
        
        self.assertEqual(decode_b64_bytes(b''), b'')
        self.assertEqual(decode_b64_bytes(b'AAAA'), b'\x00\x00\x00')
        self.assertEqual(decode_b64_bytes(b'////'), b'\xFF\xFF\xFF')
        self.assertEqual(decode_b64_bytes(b'MTIz'), b'123')
        self.assertEqual(decode_b64_bytes(bytearray(b'MTIz')), b'123')
        self.assertEqual(decode_b64_bytes(b'MTMzNw=='), b'1337')
        
        self.assertRaises(TypeError, decode_b64_bytes, None)
        self.assertRaises(TypeError, decode_b64_bytes, '1337')
        self.assertRaises(TypeError, decode_b64_bytes, 1337)
        
    def test_encode_b64_int(self):
        
        self.assertEqual(encode_b64_int(0), b'AA==')
        self.assertEqual(encode_b64_int(2**24-1), b'////')

        self.assertRaises(ValueError, encode_b64_int, -1)
        self.assertRaises(TypeError, encode_b64_int, '')
        self.assertRaises(TypeError, encode_b64_int, None)

    def test_decode_b64_int(self):
        
        self.assertEqual(decode_b64_int(b'AA=='), 0)
        self.assertEqual(decode_b64_int(b'////'), 2**24-1)

        self.assertRaises(TypeError, decode_b64_int, '')
        self.assertRaises(TypeError, decode_b64_int, None)
        self.assertRaises(TypeError, decode_b64_int, 123)
        self.assertRaises(ValueError, decode_b64_int, b'\x01')
        
if __name__ == '__main__':
    unittest.main()