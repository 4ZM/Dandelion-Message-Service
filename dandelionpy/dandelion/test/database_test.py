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
from dandelion.identity import IdentityInfo

_id1 = dandelion.identity.generate()
_id2 = dandelion.identity.generate()
_id3 = dandelion.identity.generate()

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

    def test_remote_cookies(self):
        """Test the remote time cookie interface"""
        db = ContentDB(tempfile.NamedTemporaryFile().name)

        remotefp_1 = b"1337"
        remotefp_2 = b"2342"
        remotetc_1 = b"1"
        remotetc_2 = b"2"

        # No time cookie for the db yet       
        self.assertIsNone(db.get_last_time_cookie(remotefp_1))

        # Initial tc
        db.update_last_time_cookie(remotefp_1, remotetc_1)
        self.assertEqual(db.get_last_time_cookie(remotefp_1), remotetc_1)

        # Same tc again
        db.update_last_time_cookie(remotefp_1, remotetc_1)
        self.assertEqual(db.get_last_time_cookie(remotefp_1), remotetc_1)

        # Second tc
        db.update_last_time_cookie(remotefp_1, remotetc_2)
        self.assertEqual(db.get_last_time_cookie(remotefp_1), remotetc_2)

        # Second db
        db.update_last_time_cookie(remotefp_2, remotetc_1)
        self.assertEqual(db.get_last_time_cookie(remotefp_1), remotetc_2)
        self.assertEqual(db.get_last_time_cookie(remotefp_2), remotetc_1)


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
        second_msg = dandelion.message.create('Another Single Message', _id1, _id2)
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
        _id3 = dandelion.identity.generate()
        third_cookie = db.add_identities([_id3])
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

        first_msg_list = [Message('A'), Message('B'),
                          dandelion.message.create("W Sender", sender=_id1),
                          dandelion.message.create("W Receiver", receiver=_id2),
                          dandelion.message.create("W Sender And Receiver", sender=_id1, receiver=_id2)]

        # Try to add junk
        self.assertRaises(TypeError, db.add_messages, None)
        self.assertRaises(TypeError, db.add_messages, 23)
        self.assertRaises(AttributeError, db.add_messages, [None])

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

        m1 = Message('M1')
        m2 = Message('M2')
        m3 = dandelion.message.create('M3', _id1, _id2)

        db.add_identities([_id1])
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

        first_id_list = [_id1, _id2]

        # Try to add junk
        self.assertRaises(TypeError, db.add_identities, None)
        self.assertRaises(TypeError, db.add_identities, 23)
        self.assertRaises(AttributeError, db.add_identities, [None])

        # Add a message list
        self.assertEqual(db.identity_count, 0)
        db.add_identities(first_id_list)
        self.assertNotEqual(db.identity_count, None)
        self.assertEqual(db.identity_count, len(first_id_list))
        self.assertEqual([db.contains_identity(id.fingerprint) for id in first_id_list], [True, True])

        # And for another message list? 
        second_id_list = [dandelion.identity.generate(), _id1]
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

        db.add_identities([_id1, _id2, _id3])
        db.add_messages([Message("fu")])

        _, idlist = db.get_identities()
        self.assertTrue(_id1 in idlist)
        self.assertTrue(_id2 in idlist)
        self.assertTrue(_id3 in idlist)
        for id in idlist:
            self.assertFalse(id.rsa_key.is_private)
            self.assertFalse(id.dsa_key.is_private)

        _, idlist = db.get_identities(fingerprints=[_id1.fingerprint, _id2.fingerprint])
        self.assertTrue(_id1 in idlist)
        self.assertTrue(_id2 in idlist)
        self.assertFalse(_id3 in idlist)
        for id in idlist:
            self.assertFalse(id.rsa_key.is_private)
            self.assertFalse(id.dsa_key.is_private)

#        self.assertRaises(ValueError, db.add_private_identity, _id2)
#        self.assertIsNone(db.get_private_identitity(_id2.fingerprint))
#        
#        db.add_private_identity(_id1)
#        id = db.get_private_identitity(_id1.fingerprint)
#        self.assertEqual(_id1.fingerprint, id.fingerprint)
#        self.assertTrue(id.is_private)
#        self.assertTrue(_id1.is_private)

    def test_private_identities(self):
        """Test private id interface"""

        db = ContentDB(tempfile.NamedTemporaryFile().name)
        id_priv = dandelion.identity.generate()
        id_pub = dandelion.identity.generate().public_identity()

        # Add junk
        self.assertRaises(TypeError, db.add_private_identity, None)
        self.assertRaises(ValueError, db.add_private_identity, id_pub)

        # Add, get, remove
        db.add_private_identity(id_priv)
        id = db.get_private_identity(id_priv.fingerprint)

        self.assertEqual(id_priv.fingerprint, id.fingerprint)
        self.assertEqual(id_priv, id)
        self.assertTrue(IdentityInfo(db, id).is_private())

        db.remove_private_identity(id_priv, keep_public_identity=False)
        self.assertFalse(db.contains_identity(id_priv.fingerprint))

        # Add and remove private, but keep public
        db.add_private_identity(id_priv)
        db.remove_private_identity(id_priv, keep_public_identity=True)
        self.assertTrue(db.contains_identity(id_priv.fingerprint))
        self.assertFalse(IdentityInfo(db, db.get_identities([id_priv.fingerprint])[1][0]).is_private())
        self.assertRaises(ValueError, db.get_private_identity, id_priv.fingerprint)


    def test_identity_info_nick(self):
        """"Test getting and setting nickname"""

        db = ContentDB(tempfile.NamedTemporaryFile().name)
        _id1 = dandelion.identity.generate()
        db.add_identities([_id1])

        # Check for empty nicks
        self.assertIsNone(db.get_nick(b'1337'))
        self.assertIsNone(db.get_nick(_id1.fingerprint))

        # Test setting a nick
        db.set_nick(_id1.fingerprint, "me")
        self.assertEqual(db.get_nick(_id1.fingerprint), "me")
        db.set_nick(_id1.fingerprint, "you")
        self.assertEqual(db.get_nick(_id1.fingerprint), "you")
        db.set_nick(_id1.fingerprint, None)
        self.assertIsNone(db.get_nick(_id1.fingerprint))

        # Trying some bad input
        self.assertRaises(TypeError, db.get_nick, 0)
        self.assertRaises(TypeError, db.get_nick, '')
        self.assertRaises(TypeError, db.get_nick, None)
        self.assertRaises(ValueError, db.get_nick, b'')

        self.assertRaises(TypeError, db.set_nick, _id1.fingerprint, 0)
        self.assertRaises(TypeError, db.set_nick, _id1.fingerprint, b'')
        self.assertRaises(TypeError, db.set_nick, None, "qwerty")
        self.assertRaises(TypeError, db.set_nick, 0, "qwerty")
        self.assertRaises(TypeError, db.set_nick, '', "qwerty")
        self.assertRaises(ValueError, db.set_nick, b'', "qwerty")

if __name__ == '__main__':
    unittest.main()

