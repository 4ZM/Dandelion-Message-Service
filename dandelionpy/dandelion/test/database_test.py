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
import tempfile
from dandelion.message import Message
from dandelion.database import ContentDB, InMemoryContentDB, SQLiteContentDB, ContentDBException

class DatabaseTest(unittest.TestCase):
    """Unit test suite for the InMemoryContentDB class"""
    
    def test_sqlite(self):
        tmp = tempfile.NamedTemporaryFile()
        sqlitedb = SQLiteContentDB(tmp.name)
        
        self.assertTrue(len(sqlitedb.id), ContentDB._DBID_LENGTH_BYTES)
        self.assertTrue(ContentDB._TCID_LENGTH_BYTES > 1)
        self.assertTrue(isinstance(sqlitedb.id, bytes))
        self.assertEqual(sqlitedb.message_count, 0)

        m1 = Message('a')
        tc1 = sqlitedb.add_messages([m1, Message('b')])
        self.assertEqual(sqlitedb.message_count, 2)
        tc2 = sqlitedb.add_messages([Message('c')])
        self.assertEqual(sqlitedb.message_count, 3)
        self.assertNotEqual(tc1, tc2)

        sqlitedb.get_messages([m1.id])
    
    def test_singleton(self):
        
        self.assertEqual(ContentDB.db, None)
        self.assertRaises(ContentDBException, ContentDB.register, None)
        self.assertRaises(ContentDBException, ContentDB.register, 23)
        self.assertRaises(ContentDBException, ContentDB.unregister)
        
        db = InMemoryContentDB()
        ContentDB.register(db)
        self.assertRaises(ContentDBException, ContentDB.register, db)
        self.assertRaises(ContentDBException, ContentDB.register, InMemoryContentDB())
        
        db_back = ContentDB.db
        self.assertNotEqual(db_back, None)
        self.assertEqual(db_back, db)
        
        ContentDB.unregister()
        self.assertEqual(ContentDB.db, None)


    def test_sqlitedb_id(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_id(ContentDB.db)
        ContentDB.unregister()

    def test_sqlitedb_single_message_interface(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_single_message_interface()
        ContentDB.unregister()
        
    def test_sqlitedb_list_message_interface(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_list_message_interface()
        ContentDB.unregister()
        
    def test_sqlitedb_test_time_cookies(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_time_cookies()
        ContentDB.unregister()

    def test_sqlitedb_get_messages(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_get_messages()
        ContentDB.unregister()


    def test_imcdb_id(self):
        ContentDB.register(InMemoryContentDB())
        self._test_id(ContentDB.db)
        ContentDB.unregister()

    def test_imcdb_single_message_interface(self):
        ContentDB.register(InMemoryContentDB())
        self._test_single_message_interface()
        ContentDB.unregister()
        
    def test_imcdb_list_message_interface(self):
        ContentDB.register(InMemoryContentDB())
        self._test_list_message_interface()
        ContentDB.unregister()
        
    def test_imcdb_test_time_cookies(self):
        ContentDB.register(InMemoryContentDB())
        self._test_time_cookies()
        ContentDB.unregister()

    def test_imcdb_get_messages(self):
        ContentDB.register(InMemoryContentDB())
        self._test_get_messages()
        ContentDB.unregister()


    def _test_id(self, db):
        """Test data base id format"""
        db = ContentDB.db
        
        id = db.id
        self.assertNotEqual(id, None)
        self.assertTrue(len(id) > 0)
        self.assertTrue(isinstance(db.id, bytes))
        
        # Another data base gets another id
        self.assertNotEqual(id, InMemoryContentDB().id)

    def _test_single_message_interface(self):
        """Test functions relating to storing and recovering single messages"""
        
        db = ContentDB.db
        
        first_msg = Message("A message")

        # Try to add junk
        self.assertRaises(ValueError, db.add_messages, None)
        self.assertRaises(TypeError, db.add_messages, 23)
        self.assertRaises(TypeError, db.add_messages, [None])

        # Add a single message        
        db.add_messages([first_msg])
        self.assertEqual(db.message_count, 1)
        self.assertEqual(db.contains_message(first_msg.id), True)
        
    def _test_list_message_interface(self):
        """Test functions relating to storing and recovering single messages"""
        
        db = ContentDB.db
        
        first_msg_list = [Message('A'), Message('B')]

        # Add a message list        
        db.add_messages(first_msg_list)
        self.assertNotEqual(db.message_count, None)
        self.assertEqual(db.message_count, len(first_msg_list))
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [True, True])

        # And for another message list? 
        second_msg_list = [Message('C'), Message('A')]
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [False, True])
        
        # Adding the second message list
        db.add_messages(second_msg_list)
        self.assertEqual(db.message_count, 3)
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [True, True])
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [True, True])

        # Remove a list
        db.remove_messages(first_msg_list)
        self.assertEqual(db.message_count, 1)
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [False, False])
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [True, False])

        # Remove same message list 
        db.remove_messages(first_msg_list)
        self.assertEqual(db.message_count, 1)
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [False, False])
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [True, False])
        
        # Remove all messages
        db.remove_messages()
        self.assertEqual(db.message_count, 0)
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [False, False])
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [False, False])

    def _test_time_cookies(self):
        """Test the data base time cookies (revision) functionality""" 
        
        db = ContentDB.db

        # Adding a message        
        first_msg = Message('A Single Message')
        first_cookie = db.add_messages([first_msg])
        self.assertNotEqual(first_cookie, None)
        self.assertTrue(isinstance(first_cookie, bytes))

        # Same message again
        self.assertEqual(first_cookie, db.add_messages([first_msg]))

        # New message, new cookie
        second_msg = Message('Another Single Message')
        second_cookie = db.add_messages([second_msg])
        self.assertNotEqual(second_cookie, None)
        self.assertNotEqual(second_cookie, first_cookie)

        # Since first should only be second
        tc, some_messages = db.get_messages_since(first_cookie)
        self.assertNotEqual(some_messages, None)
        self.assertEqual(tc, second_cookie)

        self.assertEqual(len(some_messages), 1)
        self.assertEqual(some_messages[0], second_msg)
        
        # Nothing new since last message was added
        tc, last_messages = db.get_messages_since(second_cookie)
        self.assertNotEqual(last_messages, None)
        self.assertEqual(len(last_messages), 0)
        self.assertEqual(tc, second_cookie)
        
        # Trying some bad input
        self.assertRaises(TypeError, db.get_messages_since, 0)
        self.assertRaises(TypeError, db.get_messages_since, '')
        self.assertRaises(TypeError, db.get_messages_since, 'fubar')
        self.assertRaises(ValueError, db.get_messages_since, b'')
        self.assertRaises(ValueError, db.get_messages_since, b'1337')

    def _test_get_messages(self):
        """Test the message retrieval from msg id list"""
        
        db = ContentDB.db

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