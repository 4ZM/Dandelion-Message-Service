import unittest
import binascii
from message import Message
from database import DataBase

class DatabaseTest(unittest.TestCase):
    """Unit test suite for the DataBase class"""
    
    def test_id(self):
        """Test data base id format"""
        
        db = DataBase()
        id = db.id
        self.assertNotEqual(id, None)
        self.assertTrue(len(id) > 0)
        
        # Another data base gets another id
        self.assertNotEqual(id, DataBase().id)
        
    def test_single_message_interface(self):
        """Test functions relating to storing and recovering single messages"""
        
        db = DataBase()
        
        first_msg = Message("A message")

        # Try to add junk
        self.assertRaises(ValueError, db.add_message, None)
        self.assertRaises(ValueError, db.add_message, 23)
        self.assertRaises(ValueError, db.add_message, [None])

        # Add a single message        
        db.add_message(first_msg)
        self.assertNotEqual(db.message_count, None)
        self.assertEqual(db.message_count(), 1)
        self.assertTrue(db.contains_message(first_msg))

        # And for another message? 
        second_msg = Message("A new message")
        self.assertFalse(db.contains_message(second_msg))
        
        # Adding a second message
        db.add_message(second_msg)
        self.assertEqual(db.message_count(), 2)
        self.assertTrue(db.contains_message(first_msg))
        self.assertTrue(db.contains_message(second_msg))

        # Nothing special about the particular instances (it's the id that counts)
        self.assertTrue(db.contains_message(Message("A new message")))

        # Remove a single message
        db.remove_message(first_msg)
        self.assertEqual(db.message_count(), 1)
        self.assertFalse(db.contains_message(first_msg))

        # Remove same single message
        db.remove_message(first_msg)
        self.assertEqual(db.message_count(), 1)
        self.assertFalse(db.contains_message(first_msg))
        
        # Remove all messages
        db.remove_message()
        self.assertEqual(db.message_count(), 0)
        self.assertFalse(db.contains_message(first_msg))
        self.assertFalse(db.contains_message(second_msg))
        
    def test_list_message_interface(self):
        """Test functions relating to storing and recovering single messages"""
        
        db = DataBase()
        
        first_msg_list = [Message('A'), Message('B')]

        # Add a message list        
        db.add_message(first_msg_list)
        self.assertNotEqual(db.message_count, None)
        self.assertEqual(db.message_count(), len(first_msg_list))
        self.assertEqual(db.contains_message(first_msg_list), [True, True])

        # And for another message list? 
        second_msg_list = [Message('C'), Message('A')]
        self.assertEqual(db.contains_message(second_msg_list), [False, True])
        
        # Adding the second message list
        db.add_message(second_msg_list)
        self.assertEqual(db.message_count(), 3)
        self.assertEqual(db.contains_message(first_msg_list), [True, True])
        self.assertEqual(db.contains_message(second_msg_list), [True, True])

        # Remove a list
        db.remove_message(first_msg_list)
        self.assertEqual(db.message_count(), 1)
        self.assertEqual(db.contains_message(first_msg_list), [False, False])
        self.assertEqual(db.contains_message(second_msg_list), [True, False])

        # Remove same message list 
        db.remove_message(first_msg_list)
        self.assertEqual(db.message_count(), 1)
        self.assertEqual(db.contains_message(first_msg_list), [False, False])
        self.assertEqual(db.contains_message(second_msg_list), [True, False])
        
        # Remove all messages
        db.remove_message()
        self.assertEqual(db.message_count(), 0)
        self.assertEqual(db.contains_message(first_msg_list), [False, False])
        self.assertEqual(db.contains_message(second_msg_list), [False, False])

    def test_uid_storage(self):
        """Test function relating to storing and recovering user identities"""
        #TODO 
        
    def test_time_cookies(self):
        """Test the data base time cookies (revision) functionality""" 
        
        db = DataBase()

        # Adding a message        
        first_msg = Message('A Single Message')
        first_cookie = db.add_message(first_msg)
        self.assertNotEqual(first_cookie, None)

        # Same message again
        self.assertEqual(first_cookie, db.add_message(first_msg))

        # New message, new cookie
        second_msg = Message('Another Single Message')
        second_cookie = db.add_message(second_msg)
        self.assertNotEqual(second_cookie, None)
        self.assertNotEqual(second_cookie, first_cookie)

        # Since first should only be second
        some_messages = db.messages_since(first_cookie)
        self.assertNotEqual(some_messages, None)

        self.assertEqual(len(some_messages), 1)
        self.assertEqual(some_messages[0], second_msg)
        
        # Nothing new since last message was added
        last_messages = db.messages_since(second_cookie)
        self.assertNotEqual(last_messages, None)
        self.assertEqual(len(last_messages), 0)
        

if __name__ == '__main__':
    unittest.main()