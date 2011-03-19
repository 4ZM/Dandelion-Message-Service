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
import re
from dandelion.message import Message 
from dandelion.protocol import Protocol, ProtocolParseError, ProtocolVersionError
import dandelion

class ProtocolTest(unittest.TestCase):
    """Unit test suite for the DMS Protocol class"""
     
    def test_constants(self):
        """Checking constant values"""

        self.assertTrue(re.match('^[0-9]+\.[0-9]+$', Protocol.PROTOCOL_VERSION))
        self.assertEqual(Protocol.TERMINATOR, '\n')
        self.assertEqual(Protocol._PROTOCOL_COOKIE, 'DMS')
        self.assertEqual(Protocol._FIELD_SEPARATOR, ';')
        self.assertEqual(Protocol._SUB_FIELD_SEPARATOR, '|')
        self.assertNotEqual(Protocol._FIELD_SEPARATOR, Protocol._SUB_FIELD_SEPARATOR)
        
    def test_create_greeting_message(self):
        """Test construction of greeting message"""
        
        ex_database_id_bin = b'\x01\x03\x03\x07'
        ex_database_id_str = dandelion.util.encode_bytes(ex_database_id_bin).decode()

        greeting = Protocol.create_greeting_message(ex_database_id_bin)
        pc, pv, dbid = greeting[:-1].split(';')
        
        self.assertEqual(pc, "DMS")
        self.assertTrue(re.match('^[0-9]+\.[0-9]+$', pv))
        self.assertEqual(dbid, ex_database_id_str)
    
        self.assertRaises(ValueError, Protocol.create_greeting_message, None)
        self.assertRaises(TypeError, Protocol.create_greeting_message, 1337)
        self.assertRaises(ValueError, Protocol.create_greeting_message, b'')
        self.assertRaises(ValueError, Protocol.create_greeting_message, [])
    
    def test_parse_greeting_message(self):
        """Test parsing greeting message"""

        ex_database_id_bin = b'\x01\x03\x03\x07'
        ex_database_id_str = dandelion.util.encode_bytes(ex_database_id_bin).decode()

        dbid = Protocol.parse_greeting_message('DMS;{0};{1}\n'.format(Protocol.PROTOCOL_VERSION, ex_database_id_str))
        self.assertEqual(dbid, ex_database_id_bin)
        
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, '')
        self.assertRaises(ValueError, Protocol.parse_greeting_message, None)
        self.assertRaises(TypeError, Protocol.parse_greeting_message, 1337)    

        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          'XXX;{0};{1}\n'.format(Protocol.PROTOCOL_VERSION, ex_database_id_str))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          'XXX;XXX;{0};{1}\n'.format(Protocol.PROTOCOL_VERSION, ex_database_id_str))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          'DMS;10;{0}\n'.format(ex_database_id_str))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message, 
                          'DMS;{0};???\n'.format(Protocol.PROTOCOL_VERSION))
        self.assertRaises(ProtocolParseError, Protocol.parse_greeting_message,
                          'DMS;{0};\n'.format(Protocol.PROTOCOL_VERSION)) 
        
        self.assertRaises(ProtocolVersionError, Protocol.parse_greeting_message, 
                          'DMS;2.0;{0}\n'.format(ex_database_id_str))
        
    
    def test_roundtrip_greeting_message(self):
        """Test the greeting message creation / parsing by a round trip"""
        
        ex_database_id_bin = b'\x01\x03\x03\x07'

        self.assertEqual(Protocol.parse_greeting_message(Protocol.create_greeting_message(ex_database_id_bin)), ex_database_id_bin)
        
    def test_create_message_id_list_request(self):
        """Test message ID list request creation"""

        s = Protocol.create_message_id_list_request()
        self.assertTrue('GETMESSAGELIST' in s)
        self.assertTrue(Protocol.is_message_id_list_request(s))
        
        tc = b'\x01\x03\x03\x07'
        s = Protocol.create_message_id_list_request(tc)
        self.assertTrue(' '.join(['GETMESSAGELIST', dandelion.util.encode_bytes(tc).decode()]) in s) 
        self.assertTrue(Protocol.is_message_id_list_request(s))
        
        """Testing bad input"""
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, 0)
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, -1337)
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, [])
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, "1337")
        self.assertRaises(TypeError, Protocol.create_message_id_list_request, "XXX")
                          
    def test_parse_message_id_list_request(self):
        """Test parsing the message ID list request string"""
        
        tc_bin = b'\x01\x03\x03\x07'
        tc_str = dandelion.util.encode_bytes(tc_bin).decode()
        
        self.assertTrue(Protocol.is_message_id_list_request('GETMESSAGELIST {0}\n'.format(tc_str)))
        tc = Protocol.parse_message_id_list_request('GETMESSAGELIST {0}\n'.format(tc_str))
        self.assertEqual(tc, tc_bin)

        self.assertTrue(Protocol.is_message_id_list_request('GETMESSAGELIST\n'))
        tc = Protocol.parse_message_id_list_request('GETMESSAGELIST\n')
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
                          'BAD\n')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'BAD BAD\n')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'GETMESSAGELIST ???\n')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'GETMESSAGELIST 01030307 01030307\n')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list_request, 
                          'GETMESSAGELISTXXX 01030307\n')

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
        tc_str_ok = dandelion.util.encode_bytes(tc).decode()
        
        str_ = Protocol.create_message_id_list(tc, [msg1, msg2, msg3])[:-1]
        tc_str, m1_str, m2_str, m3_str = str_.split(';')
        self.assertEqual(tc_str, tc_str_ok)
        self.assertEqual(msg1.id, dandelion.util.decode_bytes(m1_str.encode()))
        self.assertEqual(msg2.id, dandelion.util.decode_bytes(m2_str.encode()))
        self.assertEqual(msg3.id, dandelion.util.decode_bytes(m3_str.encode()))

        str_ = Protocol.create_message_id_list(tc, None)[:-1]
        self.assertEqual(str_, tc_str)
        
        str_ = Protocol.create_message_id_list(tc, [])[:-1]
        self.assertEqual(str_, tc_str)

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

        tc = b'13\x01\x07'
        tc_str = dandelion.util.encode_bytes(tc).decode()
                
        m1 = b'42'
        m2 = b'\x01\x23\x245'
        m3 = b'\x42\x42\x42'
        m3_str = dandelion.util.encode_bytes(m3).decode()
        m2_str = dandelion.util.encode_bytes(m2).decode()
        m1_str = dandelion.util.encode_bytes(m1).decode()

        parsed_tc, msgidlist = Protocol.parse_message_id_list(''.join([';'.join([tc_str, m1_str, m2_str, m3_str]), '\n']))
        self.assertEqual(parsed_tc, tc)
        self.assertEqual(len(msgidlist), 3)
        self.assertTrue(m1 in msgidlist)
        self.assertTrue(m2 in msgidlist)
        self.assertTrue(m3 in msgidlist)
        
        parsed_tc, msgidlist = Protocol.parse_message_id_list(''.join([tc_str, '\n']))
        self.assertEqual(parsed_tc, tc)
        self.assertEqual(len(msgidlist), 0)
        
        """Testing bad input"""
        self.assertRaises(ValueError, Protocol.parse_message_id_list, None)
        self.assertRaises(TypeError, Protocol.parse_message_id_list, 1337)
        self.assertRaises(TypeError, Protocol.parse_message_id_list, [])
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list, 
                          '')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list, 
                          '\n')

        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list, 
                          '???\n')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list, 
                          'FF FF\n')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list, 
                          '???;???\n')

        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list, 
                          'FF;;FF\n')

        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list, 
                          'FF;FF;\n')

        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_id_list, 
                          ';FF;FF\n')


    def test_roundtrip_message_id_list(self):
        """Test message ID list response creation / parsing by a round trip"""
        
        msg1 = Message('M1')
        msg2 = Message('M2')
        msg3 = Message('M3')
        
        tc, msgids = Protocol.parse_message_id_list(Protocol.create_message_id_list(b'24', [msg1, msg2, msg3]))
        self.assertEqual(tc, b'24')
        self.assertEqual(len(msgids), 3)
        self.assertTrue(msg1.id in msgids)
        self.assertTrue(msg2.id in msgids)
        self.assertTrue(msg3.id in msgids)


    def test_create_message_list_request(self):
        """Test message list request creation"""

        m1 = b'42'
        m2 = b'\x01\x23\x245'
        m3 = b'\x42\x42\x42'
        m3_str = dandelion.util.encode_bytes(m3).decode()
        m2_str = dandelion.util.encode_bytes(m2).decode()
        m1_str = dandelion.util.encode_bytes(m1).decode()
        
        self.assertTrue(Protocol.is_message_list_request('GETMESSAGES\n'))
        self.assertFalse(Protocol.is_message_list_request('GETMES_XXX_SAGES\n'))
        self.assertEqual(Protocol.create_message_list_request(), 'GETMESSAGES\n')
        self.assertEqual(Protocol.create_message_list_request([]), 'GETMESSAGES\n')
        
        str_ = Protocol.create_message_list_request([m1, m2, m3])
        self.assertTrue(Protocol.is_message_list_request(str_))
        self.assertTrue('GETMESSAGES ' in str_)
        self.assertEquals(str_.count(';'), 2)

        self.assertTrue(m1_str in str_)
        self.assertTrue(m2_str in str_)
        self.assertTrue(m3_str in str_)        
        
        """Testing bad input"""
        self.assertRaises(TypeError, Protocol.create_message_list_request, 0)
        self.assertRaises(TypeError, Protocol.create_message_list_request, -1337)
        self.assertRaises(TypeError, Protocol.create_message_list_request, "1337")
        self.assertRaises(TypeError, Protocol.create_message_list_request, "XXX")

    def test_parse_message_list_request(self):
        """Test parsing the message list request string"""
        
        msgs = Protocol.parse_message_list_request('GETMESSAGES\n')
        self.assertEqual(msgs, None)
        
        m1 = b'42'
        m2 = b'\x01\x23\x245'
        m3 = b'\x42\x42\x42'
        m3_str = dandelion.util.encode_bytes(m3).decode()
        m2_str = dandelion.util.encode_bytes(m2).decode()
        m1_str = dandelion.util.encode_bytes(m1).decode()
       
        msgs_ret = Protocol.parse_message_list_request('GETMESSAGES {0}\n'.format(';'.join([m1_str, m2_str, m3_str])))
        self.assertEquals(len(msgs_ret), 3)
        
        self.assertTrue(m1 in msgs_ret)
        self.assertTrue(m2 in msgs_ret)
        self.assertTrue(m3 in msgs_ret)
        
        """Testing bad input"""
        self.assertRaises(ValueError, Protocol.parse_message_list_request, None)
        self.assertRaises(TypeError, Protocol.parse_message_list_request, 1337)
        self.assertRaises(TypeError, Protocol.parse_message_list_request, [])
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list_request, 
                          '')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list_request, 
                          'XXX\n')

        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list_request, 
                          'FF\n')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list_request, 
                          'GETMESSAGESXX\n')
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list_request, 
                          'GETMESSAGES ???;???\n')

        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list_request, 
                          'GETMESSAGES FF;;FF\n')

        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list_request, 
                          'GETMESSAGES FF;FF;\n')

        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list_request, 
                          'GETMESSAGES ;FF;FF\n')

    def test_roundtrip_message_list_request(self):
        """Test message list request creation / parsing by a round trip"""
        msg = Protocol.create_message_list_request()
        res = Protocol.parse_message_list_request(msg)
        self.assertEqual(res, None)
        
        msg = Protocol.create_message_list_request([b'1', b'2'])
        res = Protocol.parse_message_list_request(msg)
        self.assertEqual(res, [b'1', b'2'])

    def test_create_message_list(self):
        """Test message list creation"""
        
        m1 = Message('FUBAR')
        m2 = Message('f00')
        m3 = Message('13;@|37')
        m1_txt_b64 = 'RlVCQVI='
        m2_txt_b64 = 'ZjAw'
        m3_txt_b64 = 'MTM7QHwzNw=='
        
        msg = Protocol.create_message_list([m1, m2, m3])
        
        self.assertTrue(len(msg) > 0)
        self.assertEqual(msg.count(';'), 2)
        self.assertTrue(m1_txt_b64 in msg)
        self.assertTrue(m2_txt_b64 in msg)
        self.assertTrue(m3_txt_b64 in msg)
        
        msg = Protocol.create_message_list([])
        self.assertEqual(msg, Protocol.TERMINATOR)
        
        self.assertRaises(ValueError, Protocol.create_message_list, None)
        self.assertRaises(TypeError, Protocol.create_message_list, 1337)

    def test_parse_message_list(self):
        """Test parsing the message list string"""
        
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list, 
                          ';')
        self.assertRaises(ProtocolParseError, 
                          Protocol.parse_message_list, 
                          '')
        self.assertRaises(ValueError, 
                          Protocol.parse_message_list, 
                          None)

    def test_message_list_roundtrip(self):
        m1 = Message('M1')
        m2 = Message('M2')
        m3 = Message('M3')
        
        msg = Protocol.create_message_list([m1, m2, m3])
        mout = Protocol.parse_message_list(msg)
        self.assertEqual(len(mout), 3)
        self.assertTrue(m1 in mout)
        self.assertTrue(m2 in mout)
        self.assertTrue(m3 in mout)

if __name__ == '__main__':
    unittest.main()
    