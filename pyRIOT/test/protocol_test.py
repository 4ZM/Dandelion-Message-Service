import unittest
import binascii
import re
from message import Message 
from protocol import Protocol
from database import DataBase

class ProtocolTest(unittest.TestCase):
    '''Unit test suite for the Protocol class'''
     
    def test_constants(self):
        '''Checking constant values'''
        
        p = Protocol()

        self.assertTrue(re.match('^[0-9]+\.[0-9]+$', Protocol._PROTOCOL_VERSION))
        self.assertEqual(Protocol._PROTOCOL_COOKIE, 'RIOT')
        self.assertEqual(Protocol._FIELD_SEPARATOR, ';')
        self.assertEqual(Protocol._SUB_FIELD_SEPARATOR, '|')
        
    def test_CreateGreetingMessage(self):
        '''Test construction of greeting message'''
        
        p = Protocol()
        db = DataBase()
        
        greeting = p.CreateGreetingMessage(db)
        
        pc, pv, dbid = greeting.split(Protocol.FIELD_SEPARATOR)
        
        self.assertEqual(pc, Protocol.PROTOCOL_COOKIE)
        self.assertEqual(pv, Protocol.PROTOCOL_VERSION)
        self.assertEqual(dbid, binascii.b2a_hex(db))
    
        self.assertRaises(ValueError, p.CreateGreetingMessage, None)
        self.assertRaises(ValueError, p.CreateGreetingMessage, 1337)
    
    def test_ParseGreetingMessage(self):
        p = Protocol()
        db = DataBase()
        
        greeting = p.CreateGreetingMessage(db)

        sample_id = ''.join(['0' for _ in xrange(DataBase.ID_LENGTH_BYTES*2)])
        sample_greeting = ''.join(';', ['RIOT', '1.0', sample_id])
        print (sample_greeting)
        
        dbid = p.ParseGreetingMessage(sample_greeting)
        self.assertEqual(dbid, sample_id)
    
        # TEST LOTS OF BAD INPUT HERE
    
    def test_roundtrip_GreetingMessage(self):
        '''Test the greeting message round trip'''
        
        p = Protocol()
        db = DataBase()
        
        dbid = p.ParseGreetingMessage(p.CreateGreetingMessage(db))
        
        self.assertEqual(db.GetId(), dbid)
        
        
    def test_CreateMessageIdListRequest(self):
        ''''''

    def test_ParseMessageIdListRequest(self):
        ''''''

    def test_CreateMessageIdList(self):
        ''''''

    def test_ParseMessageIdList(self):
        ''''''
        
    def test_CreateMessageListRequest(self):
        ''''''

    def test_ParseMessageListRequest(self):
        ''''''

    def test_CreateMessageList(self):
        ''''''

    def test_ParseMessageList(self):
        ''''''

if __name__ == '__main__':
    unittest.main()