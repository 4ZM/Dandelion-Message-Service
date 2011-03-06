"""
Copyright (c) 2011 Anders Sundman <anders@4zm.org>

This file is part of dandelionpy

dandelionpy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

dandelionpy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with dandelionpy.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import binascii
from dandelion.message import Message 

class MessageTest(unittest.TestCase):
    """Unit test suite for the DMS Message class"""
     
    _sample_message = "A test message"
    _sample_message_sha256 = "5f5cb37d292599ecdca99a5590b347ceb1d908a7f1491c3778e1b29e4863ca3a"
    
    def test_globals(self):
        """Testing for sane message constants"""
        
        self.assertTrue(Message.MAX_TEXT_LENGTH > 0)
    
    def test_basic_construction(self):
        """Testing construction interface"""
        
        msg = Message(self._sample_message)
        msg_text = msg.text
        self.assertEqual(self._sample_message, msg_text)

        self.assertNotEqual(msg.id, None)
        self.assertTrue(len(msg.id) > 0)

        self.assertFalse(msg.has_sender())
        self.assertEqual(msg.sender, None)
        
        self.assertFalse(msg.has_receiver())
        self.assertEqual(msg.receiver, None)

    def test_construction_with_sender(self):
        """Testing message construction when specifying a sender"""
        # TODO

    def test_construction_with_receiver(self):
        """Testing message construction when specifying a receiver"""
        # TODO
    
    def test_construction_with_sender_and_receiver(self):
        """Testing message construction when specifying a sender and a receiver"""
        # TODO
        
    def test_id_generation(self):
        """Testing the correctness of message id generation"""
        
        msg = Message(self._sample_message)
        id = msg.id
        
        # Check  id length
        self.assertEqual(len(id), Message._ID_LENGTH_BYTES)

        # LSB SHA256         
        self.assertEqual(id, binascii.a2b_hex(self._sample_message_sha256)[- Message._ID_LENGTH_BYTES:])

        # Deterministic Id generation        
        self.assertEqual(Message("Some String or other").id, Message("Some String or other").id) 
        
        # Unique Id generation
        self.assertNotEqual(Message("Some String").id, Message("Some other String").id)

    def test_message_comparisson(self):
        """Testing message equality comparison"""
        
        msg1 = Message('A')
        msg2 = Message('A')
        msg3 = Message('B')
        self.assertEqual(msg1.id, msg2.id)
        self.assertEqual(msg1, msg2)
        self.assertNotEqual(msg1, msg3)
        self.assertTrue(msg1 == msg2)
        self.assertTrue(msg1 != msg3)
        
    def test_bad_input_construction(self):
        """Testing message creation with bad input"""
        
        self.assertRaises(ValueError, Message, None)
        
        corner_case_str = ''.join(['x' for _ in range(Message.MAX_TEXT_LENGTH)])
        self.assertTrue(len(corner_case_str) == Message.MAX_TEXT_LENGTH)
        Message(corner_case_str)
        
        corner_case_str = ''.join(['x' for _ in range(Message.MAX_TEXT_LENGTH + 1)])
        self.assertTrue(len(corner_case_str) > Message.MAX_TEXT_LENGTH)
        self.assertRaises(ValueError, Message, corner_case_str)
        
    def test_string_rep(self):
        """Testing the message to string conversion"""
        
        msg = Message(self._sample_message)
        self.assertEqual(str(msg), self._sample_message_sha256[- 2*Message._ID_LENGTH_BYTES:])         


if __name__ == '__main__':
    unittest.main()
