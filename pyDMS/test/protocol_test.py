import unittest
import binascii
import re
from message import Message 
from protocol import Protocol, ProtocolParseError, ProtocolVersionError
from database import DataBase

class ProtocolTest(unittest.TestCase):
    """Unit test suite for the DMS Protocol class"""
     
    def test_constants(self):
        """Checking constant values"""
        
        p = Protocol()

        self.assertTrue(re.match('^[0-9]+\.[0-9]+$', Protocol.PROTOCOL_VERSION))
        self.assertEqual(Protocol._PROTOCOL_COOKIE, 'DMS')
        self.assertEqual(len(Protocol._FIELD_SEPARATOR), 1)
        self.assertEqual(len(Protocol._SUB_FIELD_SEPARATOR), 1)
        self.assertNotEqual(Protocol._FIELD_SEPARATOR, Protocol._SUB_FIELD_SEPARATOR)
        
    def test_create_greeting_message(self):
        """Test construction of greeting message"""
        
        p = Protocol()
        ex_database_id_bin = b'\1\3\3\7'
        ex_database_id_hex = '01030307'

        greeting = p.create_greeting_message(ex_database_id_bin)
        
        pc, pv, dbid = greeting.split(';')
        
        self.assertEqual(pc, "DMS")
        self.assertTrue(re.match('^[0-9]+\.[0-9]+$', pv))
        self.assertEqual(dbid, ex_database_id_hex)
    
        self.assertRaises(ValueError, p.create_greeting_message, None)
        self.assertRaises(ValueError, p.create_greeting_message, 1337)
        self.assertRaises(ValueError, p.create_greeting_message, b'\0')
        self.assertRaises(ValueError, p.create_greeting_message, b'')
        self.assertRaises(ValueError, p.create_greeting_message, [])
    
    def test_parse_greeting_message(self):
        """Test parsing greeting message"""

        p = Protocol()
        ex_database_id_bin = binarray(b'\1\3\3\7')
        ex_database_id_hex = '01030307'

        dbid = p.parse_greeting_message('DMS'.join([';', '1.0', ';', ex_database_id_hex]))
        self.assertEqual(dbid, ex_database_id)
        
        self.assertRaises(ProtocolParseError, p.parse_greeting_message, '')
        self.assertRaises(ProtocolParseError, p.parse_greeting_message, 'XXX'.join([';', '1.0', ';', ex_database_id_hex]))
        self.assertRaises(ProtocolParseError, p.parse_greeting_message, 'XXX;XXX'.join([';', '1.0', ';', ex_database_id_hex]))
        self.assertRaises(ProtocolParseError, p.parse_greeting_message, 'DMS'.join([';', '10', ';', ex_database_id_hex]))
        self.assertRaises(ProtocolParseError, p.parse_greeting_message, 'DMS'.join([';', '1.0', ';', 'XXX']))
        self.assertRaises(ProtocolParseError, p.parse_greeting_message, 'DMS'.join([';', '1.0', ';']))
        
        self.assertRaises(ProtocolVersionError, p.parse_greeting_message, 'DMS'.join([';', '2.0', ';', ex_database_id_hex]))
        
        self.assertRaises(ValueError, p.parse_greeting_message, None)
        self.assertRaises(ValueError, p.parse_greeting_message, 1337)    
    
    def test_roundtrip_greeting_message(self):
        """Test the greeting message creation / parsing by a round trip"""
        
        p = Protocol()
        ex_database_id_bin = binarray(b'\1\3\3\7')
        ex_database_id_hex = '01030307'

        self.assertEqual(p.parse_greeting_message(p.create_greeting_message(ex_database_id_bin)), ex_database_id_bin)
        
    def test_create_message_id_list_request(self):
        """Test message ID list request creation"""
       
        p = Protocol()
        
        str = p.create_message_id_list()
        self.assertEqual(str, 'GETMESSAGELIST')
        
        str = p.create_message_id_list(1337)
        self.assertEqual(str, 'GETMESSAGELIST 0539') # 1337 = 0x0539
        
        """Testing bad input"""
        self.assertRaises(ValueError, p.create_message_id_list, 0)
        self.assertRaises(ValueError, p.create_message_id_list, -1337)
        self.assertRaises(ValueError, p.create_message_id_list, [])
        self.assertRaises(ValueError, p.create_message_id_list, "0539")
        self.assertRaises(ValueError, p.create_message_id_list, "XXX")
                          
    def test_parse_message_id_list_request(self):
        """Test parsing the message ID list request string"""
        
        p = Protocol()
        tc = p.parse_message_id_list_request('GETMESSAGELIST 0539')
        self.assertEqual(tc, 1337)

        """Testing bad input"""
        self.assertRaises(ValueError, p.parse_message_id_list_request, None)
        self.assertRaises(ValueError, p.parse_message_id_list_request, 1337)
        self.assertRaises(ValueError, p.parse_message_id_list_request, [])
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, '')
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, 'BAD')
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, 'BAD BAD')
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, 'GETMESSAGELIST XXXX')
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, 'GETMESSAGELIST 0539 0539')
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, 'GETMESSAGELISTXXX 0539')

    def test_roundtrip_create_message_id_list_request(self):
        """Test message ID list request creation / parsing by a round trip"""
        
        p = Protocol()
        
        tc = p.parse_message_id_list_request(p.create_message_id_list())
        self.assertTrue(tc > 0)
        
        tc = p.parse_message_id_list_request(p.create_message_id_list(1337))
        self.assertEqual(tc, 1337)

    def test_create_message_id_list(self):
        """Test message ID list request creation"""

        p = Protocol()
        db = DataBase()
        
        msg1 = Message('M1')
        msg2 = Message('M2')
        msg3 = Message('M3')
        
        tc = b'\1\3\3\7'
        tc_hex = '0103037'
        
        str_ = p.create_message_id_list(tc, [msg1, msg2, msg3])
        tc_str, m1_str, m2_str, m3_str = str_.split(';')
        self.assertEqual(tc_hex, tc_str)
        self.assertEqual(msg1.id, hex2int(m1_str))
        self.assertEqual(msg2.id, hex2int(m2_str))
        self.assertEqual(msg3.id, hex2int(m3_str))

        str_ = p.create_message_id_list(1337, [])
        self.assertEqual(1337, hex2int(str_))

        """Testing bad input"""
        self.assertRaises(ValueError, p.create_message_id_list, 1337, None)
        self.assertRaises(ValueError, p.create_message_id_list, 1337, msg1)
        self.assertRaises(ValueError, p.create_message_id_list, [msg1], 1337)
        self.assertRaises(ValueError, p.create_message_id_list, 1337, 1337)
        self.assertRaises(ValueError, p.create_message_id_list, None, [])
        self.assertRaises(ValueError, p.create_message_id_list, 0, [])
        self.assertRaises(ValueError, p.create_message_id_list, -1337, [])


    def test_parse_message_id_list(self):
        """Test parsing the message ID list request string"""
        # TBD
        p = Protocol()
        db = DataBase()
        
        msg1 = Message('M1')
        msg2 = Message('M2')
        msg3 = Message('M3')
        
        db.add_message(msg1)
        tc = db.add_message(msg2)
        db.add_message(msg3)
        
        msglist = p.parse_message_id_list_request(Protocol._GETMESSAGELIST)
        self.assertEqual(len(msgid), 3)
        self.assertEqual(msg1.id, msgids[0])
        self.assertEqual(msg2.id, msgids[1])
        self.assertEqual(msg3.id, msgids[2])
        
        msglist = p.parse_message_id_list_request(Protocol._GETMESSAGELIST.join([' ', binascii.b2a_hex(tc)]))
        self.assertEqual(len(msgid), 1)
        self.assertEqual(msg3.id, msgid[0])
        
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