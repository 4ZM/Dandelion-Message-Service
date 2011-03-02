import unittest
import binascii
import re
from message import Message 
from protocol import Protocol
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
        self.assertNotEqual(Protocol._SUB_FIELD_SEPARATOR, Protocol._SUB_FIELD_SEPARATOR)
        
    def test_create_greeting_message(self):
        """Test construction of greeting message"""
        
        p = Protocol()
        db = DataBase()
        
        greeting = p.create_greeting_message(db)
        
        pc, pv, dbid = greeting.split(Protocol.FIELD_SEPARATOR)
        
        self.assertEqual(pc, Protocol._PROTOCOL_COOKIE)
        self.assertEqual(pv, Protocol._PROTOCOL_VERSION)
        self.assertEqual(dbid, binascii.b2a_hex(db))
    
        self.assertRaises(ValueError, p.create_greeting_message, None)
        self.assertRaises(ValueError, p.create_greeting_message, 1337)
    
    def test_parse_greeting_message(self):
        """Test parsing greeting message"""

        p = Protocol()
        db = DataBase()
        
        greeting = p.create_greeting_message(db)

        sample_id = ''.join(['0' for _ in range(DataBase.ID_LENGTH_BYTES*2)])
        sample_greeting = ''.join(';', ['RIOT', '1.0', sample_id])
        print (sample_greeting)
        
        dbid = p.parse_greeting_message(sample_greeting)
        self.assertEqual(dbid, sample_id)
    
        # TEST LOTS OF BAD INPUT HERE
    
    def test_roundtrip_greeting_message(self):
        """Test the greeting message creation / parsing by a round trip"""
        
        p = Protocol()
        db = DataBase()
        
        dbid = p.parse_greeting_message(p.create_greeting_message(db))
        
        self.assertEqual(db.id, dbid)
        
        
    def test_create_message_id_list_request(self):
        """Test message ID list request creation"""
       
        p = Protocol()
        db = DataBase()
        
        str = p.create_message_id_list()
        self.assertEqual(str, Protocol._GETMESSAGELIST)
        
        tc = db.add_message(Message('M'))
        str = p.create_message_id_list(tc)
        
        self.assertEqual(str, Protocol._GETMESSAGELIST.join([binascii.b2a_hex(tc)]))        

    def test_parse_message_id_list_request(self):
        """Test parsing the message ID list request string"""
        
        p = Protocol()
        db = DataBase()
        
        tc = db.add_message(db.add_message(Message('M')))
        p.parse_message_id_list_request(Protocol._GETMESSAGELIST)
        
        tc_back = p.parse_message_id_list_request(Protocol._GETMESSAGELIST.join([' ', binascii.b2a_hex(tc)]))
        self.assertEqual(tc, tc_back)
        
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, 'BAD')
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, 'BAD BAD')
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, Protocol._GETMESSAGELIST.join([' XXX']))
        self.assertRaises(Protocol.ProtocolParseError, p.parse_message_id_list_request, Protocol._GETMESSAGELIST.join([' ', binascii.b2a_hex(tc), ' ', binascii.b2a_hex(tc)]))

    def test_create_message_id_list(self):
        """Test message ID list request creation"""

        p = Protocol()
        db = DataBase()
        
        msg1 = Message('M1')
        msg2 = Message('M2')
        msg3 = Message('M3')
        
        db.add_message(msg1)
        tc1 = db.add_message(msg2)
        tc2 = db.add_message(msg3)
        
        str = p.create_message_id_list()
        tc_str, m1_str, m2_str, m3_str = str.split(';')
        self.assertEqual(len(parts), 4)
        self.assertEqual(tc1, binascii.a2b_hex(tc_str))
        self.assertEqual(msg1.id, binascii.a2b_hex(m1_str))
        self.assertEqual(msg2.id, binascii.a2b_hex(m1_str))
        self.assertEqual(msg3.id, binascii.a2b_hex(m1_str))



    def test_parse_message_id_list(self):
        """Test parsing the message ID list request string"""
        
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