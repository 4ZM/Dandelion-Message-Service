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
from dandelion.config import *

class MessageTest(unittest.TestCase):
    """Unit test suite for the DMS configuration classes"""
     
    TEST_FILE = 'config_test_data.conf'
    
    def test_construction(self):
        cm = ConfigManager(MessageTest.TEST_FILE)
        self.assertEqual(MessageTest.TEST_FILE, cm.config_file)
        self.assertTrue(isinstance(cm.server_config, ServerConfig))
        self.assertTrue(isinstance(cm.synchronizer_config, SynchronizerConfig))
        self.assertTrue(isinstance(cm.identity_manager_config, IdentityConfig))
        self.assertTrue(isinstance(cm.ui_config, UiConfig))
        self.assertTrue(isinstance(cm.content_db, ContentDB))
        
    def test_default_file(self):
        cm = ConfigManager()
        self.assertEqual('dandelion.conf', cm.config_file)

    def test_server_config(self):
        sc = ConfigManager(MessageTest.TEST_FILE).server_config
        self.assertEqual(sc.ip, '169.255.1.2')
        self.assertEqual(sc.port, 1234)
        
if __name__ == '__main__':
    unittest.main()
    