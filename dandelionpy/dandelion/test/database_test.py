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
from dandelion.message import Message
from dandelion.database import ContentDB

class DatabaseTest(unittest.TestCase):
    """Unit test suite for the ContentDB class"""
    
    def test_id(self):
        """Test data base id format"""
        
        db = ContentDB()
        id = db.id
        self.assertNotEqual(id, None)
        self.assertTrue(len(id) > 0)
        self.assertTrue(isinstance(db.id, bytes))
        
        # Another data base gets another id
        self.assertNotEqual(id, ContentDB().id)
        
    def test_single_message_interface(self):
        """Test functions relating to storing and recovering single messages"""
        
        db = ContentDB()
        
        first_msg = Message("A message")

        # Try to add junk
        self.assertRaises(ValueError, db.add_messages, None)
        self.assertRaises(TypeError, db.add_messages, 23)
        self.assertRaises(TypeError, db.add_messages, [None])

        # Add a single message        
        db.add_messages([first_msg])
        self.assertEqual(db.message_count, 1)
        self.assertEqual(db.contains_messages([first_msg]), [True])
        
    def test_list_message_interface(self):
        """Test functions relating to storing and recovering single messages"""
        
        db = ContentDB()
        
        first_msg_list = [Message('A'), Message('B')]

        # Add a message list        
        db.add_messages(first_msg_list)
        self.assertNotEqual(db.message_count, None)
        self.assertEqual(db.message_count, len(first_msg_list))
        self.assertEqual(db.contains_messages(first_msg_list), [True, True])

        # And for another message list? 
        second_msg_list = [Message('C'), Message('A')]
        self.assertEqual(db.contains_messages(second_msg_list), [False, True])
        
        # Adding the second message list
        db.add_messages(second_msg_list)
        self.assertEqual(db.message_count, 3)
        self.assertEqual(db.contains_messages(first_msg_list), [True, True])
        self.assertEqual(db.contains_messages(second_msg_list), [True, True])

        # Remove a list
        db.remove_messages(first_msg_list)
        self.assertEqual(db.message_count, 1)
        self.assertEqual(db.contains_messages(first_msg_list), [False, False])
        self.assertEqual(db.contains_messages(second_msg_list), [True, False])

        # Remove same message list 
        db.remove_messages(first_msg_list)
        self.assertEqual(db.message_count, 1)
        self.assertEqual(db.contains_messages(first_msg_list), [False, False])
        self.assertEqual(db.contains_messages(second_msg_list), [True, False])
        
        # Remove all messages
        db.remove_messages()
        self.assertEqual(db.message_count, 0)
        self.assertEqual(db.contains_messages(first_msg_list), [False, False])
        self.assertEqual(db.contains_messages(second_msg_list), [False, False])

    def test_uid_storage(self):
        """Test function relating to storing and recovering user identities"""
        #TODO 
        
    def test_time_cookies(self):
        """Test the data base time cookies (revision) functionality""" 
        
        db = ContentDB()

        # Adding a message        
        first_msg = Message('A Single Message')
        first_cookie = db.add_messages([first_msg])
        self.assertNotEqual(first_cookie, None)

        # Same message again
        self.assertEqual(first_cookie, db.add_messages([first_msg]))

        # New message, new cookie
        second_msg = Message('Another Single Message')
        second_cookie = db.add_messages([second_msg])
        self.assertNotEqual(second_cookie, None)
        self.assertNotEqual(second_cookie, first_cookie)

        # Since first should only be second
        tc, some_messages = db.messages_since(first_cookie)
        self.assertNotEqual(some_messages, None)
        self.assertEqual(tc, second_cookie)

        self.assertEqual(len(some_messages), 1)
        self.assertEqual(some_messages[0], second_msg)
        
        # Nothing new since last message was added
        tc, last_messages = db.messages_since(second_cookie)
        self.assertNotEqual(last_messages, None)
        self.assertEqual(len(last_messages), 0)
        self.assertEqual(tc, second_cookie)
        
        # Trying some bad input
        self.assertRaises(TypeError, db.messages_since, 0)
        self.assertRaises(TypeError, db.messages_since, '')
        self.assertRaises(TypeError, db.messages_since, 'fubar')
        self.assertRaises(ValueError, db.messages_since, b'')
        self.assertRaises(ValueError, db.messages_since, b'1337')
        
    def test_get_messages(self):
        """Test the message retrieval from msg id list"""
        
        db = ContentDB()

        m1 = Message('M1')
        m2 = Message('M2')
        m3 = Message('M3')
        
        db.add_messages([m1, m2, m3])
        
        mlist = db.get_messages()
        self.assertTrue(m1 in mlist)
        self.assertTrue(m2 in mlist)
        self.assertTrue(m3 in mlist)
        
        mlist = db.get_messages([m1.id, m3.id])
        self.assertTrue(m1 in mlist)
        self.assertFalse(m2 in mlist)
        self.assertTrue(m3 in mlist)
        
        
if __name__ == '__main__':
    unittest.main()