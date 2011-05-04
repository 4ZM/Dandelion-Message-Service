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
import dandelion.message
import dandelion.identity
from dandelion.message import Message
from dandelion.database import ContentDB, ContentDBException

class DatabaseTest(unittest.TestCase):
    """Unit test suite for the InMemoryContentDB class"""
    
    def test_sqlite(self):
        """Perform some SQLite specific tests."""
        tmp = tempfile.NamedTemporaryFile()
        sqlitedb = ContentDB(tmp.name)
        
        self.assertTrue(len(sqlitedb.id), ContentDB._DBID_LENGTH_BYTES)
        self.assertTrue(ContentDB._TCID_LENGTH_BYTES > 1)
        self.assertTrue(isinstance(sqlitedb.id, bytes))
        self.assertEqual(sqlitedb.message_count, 0)

        m1 = Message('a')
        tc1 = sqlitedb.add_messages([m1, Message('b')])
        self.assertEqual(sqlitedb.message_count, 2)

        sqlitedb2 = ContentDB(tmp.name, sqlitedb.id) # New db is the same as old
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
        
        db = ContentDB(":memory:")
        ContentDB.register(db)
        self.assertRaises(ContentDBException, ContentDB.register, db)
        self.assertRaises(ContentDBException, ContentDB.register, ContentDB(":memory:"))
        
        db_back = ContentDB.db
        self.assertNotEqual(db_back, None)
        self.assertEqual(db_back, db)
        
        ContentDB.unregister()
        self.assertEqual(ContentDB.db, None)

    def test_id(self):
        """Test data base id format"""
        db = ContentDB(tempfile.NamedTemporaryFile().name)
        
        id = db.id
        self.assertNotEqual(id, None)
        self.assertTrue(len(id) > 0)
        self.assertTrue(isinstance(db.id, bytes))
        
        # Another data base gets another id
        self.assertNotEqual(id, ContentDB(":memory:").id)

    def test_time_cookies(self):
        """Test the data base time cookies (revision) functionality.""" 
        
        db = ContentDB(tempfile.NamedTemporaryFile().name)

        # Adding a message        
        first_msg = Message('A Single Message')
        first_cookie = db.add_messages([first_msg])
        self.assertNotEqual(first_cookie, None)
        self.assertTrue(isinstance(first_cookie, bytes))
        self.assertTrue((db.get_last_time_cookie(None) is None) or (db.get_last_time_cookie(None) == first_cookie))

        # Same message again
        self.assertEqual(first_cookie, db.add_messages([first_msg]))

        # New message, new cookie
        id1 = dandelion.identity.generate()
        id2 = dandelion.identity.generate()
        second_msg = dandelion.message.create('Another Single Message', id1, id2)
        second_cookie = db.add_messages([second_msg])
        self.assertNotEqual(second_cookie, None)
        self.assertNotEqual(second_cookie, first_cookie)
        self.assertTrue((db.get_last_time_cookie(None) is None) or (db.get_last_time_cookie(None) == second_cookie))

        # Since first should only be second
        tc, some_messages = db.get_messages(time_cookie=first_cookie)
        self.assertNotEqual(some_messages, None)
        self.assertEqual(tc, second_cookie)

        self.assertEqual(len(some_messages), 1)
        self.assertEqual(some_messages[0], second_msg)
        
        # Nothing new since last message was added
        tc, last_messages = db.get_messages(time_cookie=second_cookie)
        self.assertNotEqual(last_messages, None)
        self.assertEqual(len(last_messages), 0)
        self.assertEqual(tc, second_cookie)
        
        # Same id gives same tc
        self.assertEqual(second_cookie, db.add_messages([first_msg]))
       
        # New identity, new cookie
        identity = dandelion.identity.generate()
        third_cookie = db.add_identities([identity])
        self.assertNotEqual(third_cookie, None)
        self.assertNotEqual(third_cookie, second_cookie)
        self.assertTrue(db.get_last_time_cookie() == third_cookie)
        
        # Trying some bad input
        self.assertRaises(TypeError, db.get_messages, [], 0)
        self.assertRaises(TypeError, db.get_messages, [], '')
        self.assertRaises(TypeError, db.get_messages, [], 'fubar')
        self.assertRaises(ValueError, db.get_messages, [], b'')
        self.assertRaises(ValueError, db.get_messages, [], b'1337')
        
    def test_message_interface(self):
        """Test functions relating to storing and recovering messages."""
        
        db = ContentDB(tempfile.NamedTemporaryFile().name)
        
        id1 = dandelion.identity.generate()
        id2 = dandelion.identity.generate()
        first_msg_list = [Message('A'), Message('B'), 
                          dandelion.message.create("W Sender", sender=id1), 
                          dandelion.message.create("W Receiver", receiver=id2), 
                          dandelion.message.create("W Sender And Receiver", sender=id1, receiver=id2)]

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
        
    def test_get_messages(self):
        """Test message retrieval."""
        
        db = ContentDB(tempfile.NamedTemporaryFile().name)

        _, mlist = db.get_messages()
        self.assertEqual(mlist, [])

        id1 = dandelion.identity.generate()
        id2 = dandelion.identity.generate()
        m1 = Message('M1')
        m2 = Message('M2')
        m3 = dandelion.message.create('M3', id1, id2)
        
        db.add_identities([id1])
        db.add_messages([m1, m2, m3])
        
        _, mlist = db.get_messages()
        self.assertTrue(m1 in mlist)
        self.assertTrue(m2 in mlist)
        self.assertTrue(m3 in mlist)
        
        _, mlist = db.get_messages([m1.id, m3.id])
        self.assertTrue(m1 in mlist)
        self.assertFalse(m2 in mlist)
        self.assertTrue(m3 in mlist)
        
    def test_identity_interface(self):
        """Test functions relating to storing and recovering identities."""
        
        db = ContentDB(tempfile.NamedTemporaryFile().name)
        
        _, idlist = db.get_identities()
        self.assertEqual(idlist, [])

        
        id_a = dandelion.identity.generate()
        id_b = dandelion.identity.generate()
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
        second_id_list = [dandelion.identity.generate(), id_a]
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

    def test_get_identities(self):
        """Test identity retrieval."""
        
        db = ContentDB(tempfile.NamedTemporaryFile().name)

        id1 = dandelion.identity.generate()
        id2 = dandelion.identity.generate().public_identity()
        id3 = dandelion.identity.generate()
        
        db.add_identities([id1, id2, id3])
        db.add_messages([Message("fu")])
        
        _, idlist = db.get_identities()
        self.assertTrue(id1 in idlist)
        self.assertTrue(id2 in idlist)
        self.assertTrue(id3 in idlist)
        for id in idlist:
            self.assertFalse(id.rsa_key.is_private)
            self.assertFalse(id.dsa_key.is_private)
        
        _, idlist = db.get_identities(fingerprints=[id1.fingerprint, id2.fingerprint])
        self.assertTrue(id1 in idlist)
        self.assertTrue(id2 in idlist)
        self.assertFalse(id3 in idlist)
        for id in idlist:
            self.assertFalse(id.rsa_key.is_private)
            self.assertFalse(id.dsa_key.is_private)
        
#        self.assertRaises(ValueError, db.add_private_identity, id2)
#        self.assertIsNone(db.get_private_identitity(id2.fingerprint))
#        
#        db.add_private_identity(id1)
#        id = db.get_private_identitity(id1.fingerprint)
#        self.assertEqual(id1.fingerprint, id.fingerprint)
#        self.assertTrue(id.is_private)
#        self.assertTrue(id1.is_private)
        
if __name__ == '__main__':
    unittest.main()