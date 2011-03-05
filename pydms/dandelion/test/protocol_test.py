"""
Copyright (c) 2011 Anders Sundman <anders@4zm.org>

This file is part of pydms

pydms is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pydms is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pydms.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import binascii
import re
from dandelion.message import Message 
from dandelion.protocol import Protocol, ProtocolParseError, ProtocolVersionError
from dandelion.database import DataBase

class ProtocolTest(unittest.TestCase):
    """Unit test suite for the DMS Protocol class"""
     
    def test_constants(self):
        """Checking constant values"""

        self.assertTrue(re.match('^[0-9]+\.[0-9]+$', Protocol.PROTOCOL_VERSION))
        self.assertEqual(Protocol._PROTOCOL_COOKIE, 'DMS')
        self.assertEqual(len(Protocol._FIELD_SEPARATOR), 1)
        self.assertEqual(len(Protocol._SUB_FIELD_SEPARATOR), 1)
        self.assertNotEqual(Protocol._FIELD_SEPARATOR, Protocol._SUB_FIELD_SEPARATOR)
        
    def test_create_greeting_message(self):
        """Test construction of greeting message"""
        
        ex_database_id_bin = b'\x01\x03\x03\x07'
        ex_database_id_hex = '01030307'

        greeting = Protocol.create_greeting_message(ex_database_id_bin)
        pc, pv, dbid = greeting.split(';')
        
        self.assertEqual(pc, "DMS")
        self.assertTrue(re.match('^[0-9]+\.[0-9]+$', pv))
        self.assertEqual(dbid, ex_database_id_hex)
    
        self.assertRaises(ValueError, Protocol.create_greeting_message, None)
        self.assertRaises(TypeError, Protocol.create_greeting_message, 1337)
        self.assertRaises(ValueError, Protocol.create_greeting_message, b'')
        self.assertRaises(ValueError, Protocol.create_greeting_message, [])
    
    def test_parse_greeting_message(self):
        """Test parsing greeting message"""

        ex_database_id_bin = b'\x01\x03\x03\x07'
        ex_database_id_hex = '01030307'

        dbid = Protocol.parse_greeting_message(';'.join(['DMS', Protocol.PROTOCOL_VERSION, ex_database_id_hex]))
        self.assertEqual(dbid, ex_database_id_bin)
        
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, '')
        self.assertRaises(ValueError, Protocol.parse_greeting_message, None)
        self.assertRaises(TypeError, Protocol.parse_greeting_message, 1337)    

        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          ';'.join(['XXX', '1.0', ex_database_id_hex]))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          ';'.join(['XXX', 'XXX', '1.0', ';', ex_database_id_hex]))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          ';'.join(['DMS', '10', ex_database_id_hex]))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          ';'.join(['DMS', '1.0', 'XXX']))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          ';'.join(['DMS', '1.0', 'XXXX']))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          ''.join(['DMS', ';', '1.0', ';']))
        
        self.assertRaises(ProtocolVersionError, Protocol.parse_greeting_message, 
                          ';'.join(['DMS', '2.0', ex_database_id_hex]))
        
    
    def test_roundtrip_greeting_message(self):
        """Test the greeting message creation / parsing by a round trip"""
        
        ex_database_id_bin = b'\x01\x03\x03\x07'

        self.assertEqual(Protocol.parse_greeting_message(Protocol.create_greeting_message(ex_database_id_bin)), ex_database_id_bin)
        
    def test_create_message_id_list_request(self):
        """Test message ID list request creation"""

        s = Protocol.create_message_id_list_request()
        self.assertEqual(s, 'GETMESSAGELIST')
        
        s = Protocol.create_message_id_list_request(b'\x01\x03\x03\x07')
        self.assertEqual(s, 'GETMESSAGELIST 01030307') # 1337 = 0x0539
        
        """Testing bad input"""
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, 0)
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, -1337)
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, [])
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, "1337")
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, "XXX")
                          
    def test_parse_message_id_list_request(self):
        """Test parsing the message ID list request string"""
        
        tc = Protocol.parse_message_id_list_request('GETMESSAGELIST 01030307')
        self.assertEqual(tc, b'\x01\x03\x03\x07')

        tc = Protocol.parse_message_id_list_request('GETMESSAGELIST')
        self.assertEqual(tc, None)

        """Testing bad input"""
        self.assertRaises(ValueError, Protocol.parse_message_id_list_request, None)
        self.assertRaises(TypeError, Protocol.parse_message_id_list_request, 1337)
        self.assertRaises(TypeError, Protocol.parse_message_id_list_request, [])
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          '')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'BAD')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'BAD BAD')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'GETMESSAGELIST XXXX')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'GETMESSAGELIST 01030307 01030307')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'GETMESSAGELISTXXX 01030307')

    def test_roundtrip_create_message_id_list_request(self):
        """Test message ID list request creation / parsing by a round trip"""
        
        tc = Protocol.parse_message_id_list_request(Protocol.create_message_id_list_request())
        self.assertEqual(tc, None)
        
        ex_database_id_bin = b'\x01\x03\x03\x07'
        tc = Protocol.parse_message_id_list_request(Protocol.create_message_id_list_request(ex_database_id_bin))
        self.assertEqual(tc, ex_database_id_bin)

    def test_create_message_id_list(self):
        """Test message ID list request creation"""

        msg1 = Message('M1')
        msg2 = Message('M2')
        msg3 = Message('M3')
        
        tc = b'\x01\x03\x03\x07'
        tc_hex = '01030307'
        
        str_ = Protocol.create_message_id_list(tc, [msg1, msg2, msg3])
        tc_str, m1_str, m2_str, m3_str = str_.split(';')
        self.assertEqual(tc_hex, tc_str)
        self.assertEqual(msg1.id, binascii.a2b_hex(m1_str))
        self.assertEqual(msg2.id, binascii.a2b_hex(m2_str))
        self.assertEqual(msg3.id, binascii.a2b_hex(m3_str))

        str_ = Protocol.create_message_id_list(tc, None)
        self.assertEqual(str_, tc_hex)
        
        str_ = Protocol.create_message_id_list(tc, [])
        self.assertEqual(str_, tc_hex)

        """Testing bad input"""
        self.assertRaises(TypeError, Protocol.create_message_id_list, 1337, None)
        self.assertRaises(TypeError, Protocol.create_message_id_list, tc, msg1)
        self.assertRaises(TypeError, Protocol.create_message_id_list, [msg1], tc)
        self.assertRaises(AttributeError, Protocol.create_message_id_list, tc, tc)
        self.assertRaises(ValueError, Protocol.create_message_id_list, None, [])
        self.assertRaises(TypeError, Protocol.create_message_id_list, 0, None)
        self.assertRaises(AttributeError, Protocol.create_message_id_list, tc, ['fo'])


    def test_parse_message_id_list(self):
        """Test parsing the message ID list request string"""

        tc_hex = '01030307'
        tc = binascii.a2b_hex(tc_hex)
        
        m1_hex = '0402'
        m1 = binascii.a2b_hex(m1_hex)
        
        m2_hex = '2503FF07'
        m2 = binascii.a2b_hex(m2_hex)

        m3_hex = '01AE03C7'
        m3 = binascii.a2b_hex(m3_hex)

        parsed_tc, msgidlist = Protocol.parse_message_id_list(';'.join([tc_hex, m1_hex, m2_hex, m3_hex]))
        self.assertEqual(parsed_tc, tc)
        self.assertEqual(len(msgidlist), 3)
        self.assertTrue(m1 in msgidlist)
        self.assertTrue(m2 in msgidlist)
        self.assertTrue(m3 in msgidlist)
        
        parsed_tc, msgidlist = Protocol.parse_message_id_list(tc_hex)
        self.assertEqual(parsed_tc, tc)
        self.assertEqual(len(msgidlist), 0)
                
    def test_create_message_list_request(self):
        """Test message list request creation"""

    def test_parse_message_list_request(self):
        """Test parsing the message list request string"""

    def test_create_message_list(self):
        """Test message list creation"""

    def test_parse_message_list(self):
        """Test parsing the message list string"""


if __name__ == '__main__':
    unittest.main()