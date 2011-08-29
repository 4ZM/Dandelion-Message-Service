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
from dandelion.encryption import _append_padding,_strip_padding,symetric_decrypt,symetric_encrypt
from oaep_encoder import OAEPEncoder, DecoderError

class UtilTest(unittest.TestCase):

    def test_sym_crypto(self):
        plaintext = b"Secret message..."
        key = b'Equally secret key'
        
        # Round trip 
        ciphertext = symetric_encrypt(key, plaintext)
        self.assertEqual(plaintext, symetric_decrypt(key, ciphertext))

        # Strange, but ok
        ciphertext = symetric_encrypt(key, b'')
        self.assertEqual(b'', symetric_decrypt(key, ciphertext))
        
        self.assertRaises(TypeError, symetric_encrypt, None, b'AAA')
        self.assertRaises(TypeError, symetric_encrypt, b'AAA', None)
        self.assertRaises(TypeError, symetric_encrypt, None, None)
        self.assertRaises(TypeError, symetric_encrypt, 1234, b'AAA')
        self.assertRaises(TypeError, symetric_encrypt, b'AAA', 1243)
        self.assertRaises(TypeError, symetric_encrypt, 1234, 1243)
        self.assertRaises(ValueError, symetric_encrypt, b'', b'AAA') # Empty key

        self.assertRaises(TypeError, symetric_decrypt, None, b'AAA')
        self.assertRaises(TypeError, symetric_decrypt, b'AAAA', None)
        self.assertRaises(TypeError, symetric_decrypt, None, None)
        self.assertRaises(TypeError, symetric_decrypt, 1234, b'AAA')
        self.assertRaises(TypeError, symetric_decrypt, b'AAA', 1243)
        self.assertRaises(TypeError, symetric_decrypt, 1234, 1243)
        self.assertRaises(ValueError, symetric_decrypt, b'', b'AAA') # Empty key

    def test_padding(self):
        bstr = _append_padding(b'', 16)
        self.assertEqual(len(bstr), 16)
        self.assertEqual(bstr[len(bstr)-1], 15)
        
        # Adding random padding 
        msg = b'1234567890'
        bstr = _append_padding(msg, 16)
        self.assertEqual(len(bstr), 16)
        self.assertEqual(bstr[len(bstr)-1], 16 - len(msg) - 1)

        msg = b'12345678901234'
        bstr = _append_padding(msg, 16)
        self.assertEqual(len(bstr), 16)
        self.assertEqual(bstr[len(bstr)-1], 16 - len(msg) - 1)

        msg = b'123456789012345'
        bstr = _append_padding(msg, 16)
        self.assertEqual(len(bstr), 32)
        self.assertEqual(bstr[len(bstr)-1], 32 - len(msg) - 1)

        msg = b'12345678901234567890'
        bstr = _append_padding(msg, 16)
        self.assertEqual(len(bstr), 32)
        self.assertEqual(bstr[len(bstr)-1], 32 - len(msg) - 1)
        
        # Random padding, so not repeatable
        bstr = _append_padding(msg, 16)
        bstr2 = _append_padding(msg, 16)
        self.assertNotEqual(bstr, bstr2)
        
        # Round trip
        self.assertEqual(b'', _strip_padding(_append_padding(b'', 16)))
        self.assertEqual(b'AAA', _strip_padding(_append_padding(b'AAA', 16)))
        self.assertEqual(b'12345678901234567890', _strip_padding(_append_padding(b'12345678901234567890', 16)))
        
        # Deterministic padding, so repeatable
        bstr = _append_padding(msg, 16, 0)
        bstr2 = _append_padding(msg, 16, 0)
        self.assertEqual(bstr, bstr2)
        
        # Test bad input
        self.assertRaises(TypeError, _append_padding, None, 16)
        self.assertRaises(TypeError, _append_padding, 1234, 16)
        self.assertRaises(TypeError, _append_padding, "1234", 16)
        self.assertRaises(ValueError, _append_padding, b'1234', 0)
        self.assertRaises(ValueError, _append_padding, b'1234', -1)
        self.assertRaises(ValueError, _append_padding, b'1234', 256)
        self.assertRaises(TypeError, _append_padding, b'1234', b'16')
        self.assertRaises(ValueError, _append_padding, b'1234', 16, -1)
        self.assertRaises(ValueError, _append_padding, b'1234', 16, 257)
        self.assertRaises(TypeError, _append_padding, b'1234', 16, b'0')
        
        self.assertRaises(TypeError, _strip_padding, None)
        self.assertRaises(TypeError, _strip_padding, 1)
        self.assertRaises(ValueError, _strip_padding, b'')

    def test_oaep(self):
        encoder = OAEPEncoder()
        data_str = b'some random string'

        self.assertNotEqual(data_str, encoder.encode(data_str, salt=b'', keybits=2048))

        enc1 = encoder.encode(data_str)
        enc2 = encoder.encode(data_str)
        dec1 = encoder.decode(enc1)
        dec2 = encoder.decode(enc2)

        self.assertEqual(data_str, dec1)
        self.assertEqual(data_str, dec2)
        self.assertNotEqual(enc1, enc2)

        self.assertRaises(DecoderError, encoder.decode, data_str)
        self.assertRaises(TypeError, encoder.decode, None)
        self.assertRaises(TypeError, encoder.decode, 1337)
        self.assertRaises(DecoderError, encoder.decode, "1337")

        self.assertRaises(TypeError, encoder.encode, None)
        self.assertRaises(TypeError, encoder.encode, "1337")
        self.assertRaises(TypeError, encoder.encode, 1337)

if __name__ == '__main__':
    unittest.main()
