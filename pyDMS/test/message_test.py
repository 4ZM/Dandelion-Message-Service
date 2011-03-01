import unittest
import binascii
import message

class MessageTest(unittest.TestCase):
    sample_message = 'A test message'
    sample_message_sha256 = '5f5cb37d292599ecdca99a5590b347ceb1d908a7f1491c3778e1b29e4863ca3a'
    
    def test_globals(self):
        self.assertTrue(message.Message.ID_LENGTH_BYTES > 0)
    
    def test_basic_construction(self):
        '''Testing construction interface'''
        msg = message.Message(self.sample_message)
        msgText = msg.GetText()
        self.assertEqual(self.sample_message, msgText)

        self.assertNotEqual(msg.GetId(), None)

        self.assertFalse(msg.HasSender())
        self.assertEqual(msg.GetSender(), None)
        
        self.assertFalse(msg.HasReceiver())
        self.assertEqual(msg.GetReceiver(), None)

    def test_id_generation(self):
        '''Testing the correctness of message id generation'''
        msg = message.Message(self.sample_message)
        id = msg.GetId()
        
        # Check  id length
        self.assertEqual(len(id), message.Message.ID_LENGTH_BYTES)

        # LSB SHA256         
        self.assertEqual(id, binascii.a2b_hex(self.sample_message_sha256)[-message.Message.ID_LENGTH_BYTES:])

        # Deterministic Id generation        
        self.assertEqual(message.Message("Some String or other").GetId(), message.Message("Some String or other").GetId()) 
        
        # Just a sanity check
        self.assertNotEqual(message.Message("Some String").GetId(), message.Message("Some other String").GetId())

    def test_message_comparisson(self):
        msg1 = message.Message('A')
        msg2 = message.Message('A')
        msg3 = message.Message('B')
        self.assertEqual(msg1.GetId(), msg2.GetId())
        self.assertEqual(msg1, msg2)
        self.assertNotEqual(msg1, msg3)
        self.assertTrue(msg1 == msg2)
        self.assertTrue(msg1 != msg3)
        
    def test_bad_input_construction(self):
        '''Testing message creation with bad input'''
        self.assertRaises(ValueError, message.Message, None)
        
        corner_case_str = ''.join(['x' for c in xrange(message.Message.MAX_TEXT_LENGTH)])
        self.assertTrue(len(corner_case_str) == message.Message.MAX_TEXT_LENGTH)
        message.Message(corner_case_str)
        
        corner_case_str = ''.join(['x' for c in xrange(message.Message.MAX_TEXT_LENGTH + 1)])
        self.assertTrue(len(corner_case_str) > message.Message.MAX_TEXT_LENGTH)
        self.assertRaises(ValueError, message.Message, corner_case_str)
        
    def test_string_rep(self):
        '''Testing the implicit string conversion'''
        msg = message.Message(self.sample_message)
        self.assertEqual(str(msg), binascii.b2a_hex(msg.GetId()));         

if __name__ == '__main__':
    unittest.main()