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
from dandelion.database import ContentDB, SQLiteContentDB, ContentDBException
from dandelion.identity import PrivateIdentity

class DatabaseTest(unittest.TestCase):
    """Unit test suite for the InMemoryContentDB class"""
    
    def test_sqlite(self):
        """Perform some SQLite specific tests."""
        tmp = tempfile.NamedTemporaryFile()
        sqlitedb = SQLiteContentDB(tmp.name)
        
        self.assertTrue(len(sqlitedb.id), ContentDB._DBID_LENGTH_BYTES)
        self.assertTrue(ContentDB._TCID_LENGTH_BYTES > 1)
        self.assertTrue(isinstance(sqlitedb.id, bytes))
        self.assertEqual(sqlitedb.message_count, 0)

        m1 = Message('a')
        tc1 = sqlitedb.add_messages([m1, Message('b')])
        self.assertEqual(sqlitedb.message_count, 2)

        sqlitedb2 = SQLiteContentDB(tmp.name, sqlitedb.id) # New db is the same as old
        self.assertEqual(sqlitedb.id, sqlitedb2.id)
        self.assertEqual(sqlitedb.message_count, 2)

        tc2 = sqlitedb2.add_messages([Message('c')])
        self.assertEqual(sqlitedb.message_count, 3)
        self.assertEqual(sqlitedb2.message_count, 3)
        self.assertNotEqual(tc1, tc2)
    
    def test_singleton(self):
        """Test the singleton register / unregister function."""
        self.assertEqual(ContentDB.db, None)
        self.assertRaises(ContentDBException, ContentDB.register, None)
        self.assertRaises(ContentDBException, ContentDB.register, 23)
        self.assertRaises(ContentDBException, ContentDB.unregister)
        
        db = SQLiteContentDB(":memory:")
        ContentDB.register(db)
        self.assertRaises(ContentDBException, ContentDB.register, db)
        self.assertRaises(ContentDBException, ContentDB.register, SQLiteContentDB(":memory:"))
        
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

    def test_sqlitedb_test_time_cookies(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_time_cookies()
        ContentDB.unregister()

    def test_sqlitedb_message_interface(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_message_interface()
        ContentDB.unregister()
        
    def test_sqlitedb_get_messages(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_get_messages()
        ContentDB.unregister()

    def test_sqlitedb_identity_interface(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_identity_interface()
        ContentDB.unregister()
        
    def test_sqlitedb_get_identities(self):
        tmp = tempfile.NamedTemporaryFile()
        ContentDB.register(SQLiteContentDB(tmp.name))
        self._test_get_identities()
        ContentDB.unregister()

    def _test_id(self, db):
        """Test data base id format"""
        db = ContentDB.db
        
        id = db.id
        self.assertNotEqual(id, None)
        self.assertTrue(len(id) > 0)
        self.assertTrue(isinstance(db.id, bytes))
        
        # Another data base gets another id
        self.assertNotEqual(id, SQLiteContentDB(":memory:").id)

    def _test_time_cookies(self):
        """Test the data base time cookies (revision) functionality.""" 
        
        db = ContentDB.db

        # Adding a message        
        first_msg = Message('A Single Message')
        first_cookie = db.add_messages([first_msg])
        self.assertNotEqual(first_cookie, None)
        self.assertTrue(isinstance(first_cookie, bytes))
        self.assertTrue((db.get_last_time_cookie(None) is None) or (db.get_last_time_cookie(None) == first_cookie))

        # Same message again
        self.assertEqual(first_cookie, db.add_messages([first_msg]))

        # New message, new cookie
        id1 = PrivateIdentity.generate()
        id2 = PrivateIdentity.generate()
        second_msg = Message.create('Another Single Message', id1, id2)
        second_cookie = db.add_messages([second_msg])
        self.assertNotEqual(second_cookie, None)
        self.assertNotEqual(second_cookie, first_cookie)
        self.assertTrue((db.get_last_time_cookie(None) is None) or (db.get_last_time_cookie(None) == second_cookie))

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
        
        # Same id gives same tc
        self.assertEqual(second_cookie, db.add_messages([first_msg]))
       
        # New identity, new cookie
        identity = PrivateIdentity.generate()
        third_cookie = db.add_identities([identity])
        self.assertNotEqual(third_cookie, None)
        self.assertNotEqual(third_cookie, second_cookie)
        self.assertTrue(db.get_last_time_cookie() == third_cookie)
        
        # Trying some bad input
        self.assertRaises(TypeError, db.get_messages_since, 0)
        self.assertRaises(TypeError, db.get_messages_since, '')
        self.assertRaises(TypeError, db.get_messages_since, 'fubar')
        self.assertRaises(ValueError, db.get_messages_since, b'')
        self.assertRaises(ValueError, db.get_messages_since, b'1337')
        
    def _test_message_interface(self):
        """Test functions relating to storing and recovering messages."""
        
        db = ContentDB.db
        
        id1 = PrivateIdentity.generate()
        id2 = PrivateIdentity.generate()
        first_msg_list = [Message('A'), Message('B'), 
                          Message.create("W Sender", sender=id1), 
                          Message.create("W Receiver", receiver=id2), 
                          Message.create("W Sender And Receiver", sender=id1, receiver=id2)]

        # Try to add junk
        self.assertRaises(ValueError, db.add_messages, None)
        self.assertRaises(TypeError, db.add_messages, 23)
        self.assertRaises(TypeError, db.add_messages, [None])
        
        # Add a message list        
        self.assertEqual(db.message_count, 0)
        db.add_messages(first_msg_list)
        self.assertNotEqual(db.message_count, None)
        self.assertEqual(db.message_count, len(first_msg_list))
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [True, True, True, True, True])

        # And for another message list? 
        second_msg_list = [Message('C'), Message('A')]
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [False, True])
        
        # Adding the second message list
        db.add_messages(second_msg_list)
        self.assertEqual(db.message_count, 6)
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [True, True, True, True, True])
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [True, True])

        # Remove a list
        db.remove_messages(first_msg_list)
        self.assertEqual(db.message_count, 1)
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [False, False, False, False, False])
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [True, False])

        # Remove same message list 
        db.remove_messages(first_msg_list)
        self.assertEqual(db.message_count, 1)
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [False, False, False, False, False])
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [True, False])
        
        # Remove all messages
        db.remove_messages()
        self.assertEqual(db.message_count, 0)
        self.assertEqual([db.contains_message(m.id) for m in first_msg_list], [False, False, False, False, False])
        self.assertEqual([db.contains_message(m.id) for m in second_msg_list], [False, False])
        
    def _test_get_messages(self):
        """Test message retrieval."""
        
        db = ContentDB.db

        mlist = db.get_messages()
        self.assertEqual(mlist, [])
        _, mlist = db.get_messages_since()
        self.assertEqual(mlist, [])

        id1 = PrivateIdentity.generate()
        id2 = PrivateIdentity.generate()
        m1 = Message('M1')
        m2 = Message('M2')
        m3 = Message.create('M3', id1, id2)
        
        db.add_identities([id1])
        db.add_messages([m1, m2, m3])
        
        _, mlist = db.get_messages_since()
        self.assertTrue(m1 in mlist)
        self.assertTrue(m2 in mlist)
        self.assertTrue(m3 in mlist)
        
        mlist = db.get_messages()
        self.assertTrue(m1 in mlist)
        self.assertTrue(m2 in mlist)
        self.assertTrue(m3 in mlist)
        
        mlist = db.get_messages([m1.id, m3.id])
        self.assertTrue(m1 in mlist)
        self.assertFalse(m2 in mlist)
        self.assertTrue(m3 in mlist)
        
    def _test_identity_interface(self):
        """Test functions relating to storing and recovering identities."""
        
        db = ContentDB.db
        
        idlist = db.get_identities()
        self.assertEqual(idlist, [])
        _, idlist = db.get_identities_since()
        self.assertEqual(idlist, [])

        
        id_a = PrivateIdentity.generate()
        id_b = PrivateIdentity.generate()
        first_id_list = [id_a, id_b]

        # Try to add junk
        self.assertRaises(ValueError, db.add_identities, None)
        self.assertRaises(TypeError, db.add_identities, 23)
        self.assertRaises(TypeError, db.add_identities, [None])
        
        # Add a message list
        self.assertEqual(db.identity_count, 0)        
        db.add_identities(first_id_list)
        self.assertNotEqual(db.identity_count, None)
        self.assertEqual(db.identity_count, len(first_id_list))
        self.assertEqual([db.contains_identity(id.fingerprint) for id in first_id_list], [True, True])

        # And for another message list? 
        second_id_list = [PrivateIdentity.generate(), id_a]
        self.assertEqual([db.contains_identity(id.fingerprint) for id in second_id_list], [False, True])
        
        # Adding the second message list
        db.add_identities(second_id_list)
        self.assertEqual(db.identity_count, 3)
        self.assertEqual([db.contains_identity(id.fingerprint) for id in first_id_list], [True, True])
        self.assertEqual([db.contains_identity(id.fingerprint) for id in second_id_list], [True, True])

        # Remove a list
        db.remove_identities(first_id_list)
        self.assertEqual(db.identity_count, 1)
        self.assertEqual([db.contains_identity(id.fingerprint) for id in first_id_list], [False, False])
        self.assertEqual([db.contains_identity(id.fingerprint) for id in second_id_list], [True, False])

        # Remove same message list 
        db.remove_identities(first_id_list)
        self.assertEqual(db.identity_count, 1)
        self.assertEqual([db.contains_identity(id.fingerprint) for id in first_id_list], [False, False])
        self.assertEqual([db.contains_identity(id.fingerprint) for id in second_id_list], [True, False])
        
        # Remove all messages
        db.remove_identities()
        self.assertEqual(db.identity_count, 0)
        self.assertEqual([db.contains_identity(id.fingerprint) for id in first_id_list], [False, False])
        self.assertEqual([db.contains_identity(id.fingerprint) for id in second_id_list], [False, False])

    def _test_get_identities(self):
        """Test identity retrieval."""
        
        db = ContentDB.db

        id1 = PrivateIdentity.generate()
        id2 = PrivateIdentity.generate()
        id3 = PrivateIdentity.generate()
        
        db.add_identities([id1, id2, id3])
        db.add_messages([Message("fu")])
        
        _, idlist = db.get_identities_since()
        
        self.assertTrue(id1 in idlist)
        self.assertTrue(id2 in idlist)
        self.assertTrue(id3 in idlist)
        
        idlist = db.get_identities()
        self.assertTrue(id1 in idlist)
        self.assertTrue(id2 in idlist)
        self.assertTrue(id3 in idlist)
        
        idlist = db.get_identities([id1.fingerprint, id2.fingerprint])
        self.assertTrue(id1 in idlist)
        self.assertTrue(id2 in idlist)
        self.assertFalse(id3 in idlist)
        
if __name__ == '__main__':
    unittest.main()