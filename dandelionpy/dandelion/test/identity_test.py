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
import dandelion.identity

from dandelion.identity import IdentityInfo
from dandelion.database import ContentDB

class IdentityTest(unittest.TestCase):

    def test_creation(self):
        id = dandelion.identity.generate()
        self.assertIsNotNone(id.fingerprint)

    def test_identity_info(self):
        """Test the IdentityInfo class"""

        db = ContentDB(tempfile.NamedTemporaryFile().name)
        id_a = dandelion.identity.generate()
        db.add_identities([id_a])

        # Test creation
        id_info_a = IdentityInfo(db, id_a)
        self.assertEqual(id_info_a.db, db)
        self.assertEqual(id_info_a.id.fingerprint, id_a.fingerprint)
        self.assertIsNone(id_info_a.nick)

        # Test nick set/get
        id_info_a.nick = "me"
        self.assertEqual(id_info_a.nick, "me")
        id_info_a.nick = "you"
        self.assertEqual(id_info_a.nick, "you")
        id_info_a.nick = None
        self.assertIsNone(id_info_a.nick)

        # Test bad input
        self.assertRaises(TypeError, id_info_a.nick, 0)
        self.assertRaises(TypeError, id_info_a.nick, b'')

if __name__ == '__main__':
    unittest.main()

