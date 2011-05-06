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
import os

from dandelion.config import *
from dandelion.database import ContentDB

class ConfigTest(unittest.TestCase):
    """Unit test suite for the DMS configuration classes"""

    TEST_FILE = os.path.join(os.path.split(os.path.abspath(__file__))[0], 
                             'config_test_data.conf')
    
    def test_construction(self):
        cm = ConfigManager(ConfigTest.TEST_FILE)
        self.assertEqual(ConfigTest.TEST_FILE, cm.config_file)
        self.assertTrue(isinstance(cm.server_config, ServerConfig))
        self.assertTrue(isinstance(cm.synchronizer_config, SynchronizerConfig))
        self.assertTrue(isinstance(cm.identity_manager_config, IdentityConfig))
        self.assertTrue(isinstance(cm.ui_config, UiConfig))
        self.assertTrue(isinstance(cm.content_db, ContentDB))
        
    def test_default_file(self):
        cm = ConfigManager()
        self.assertEqual('dandelion.conf', cm.config_file)

    def test_server_config(self):
        sc = ConfigManager(ConfigTest.TEST_FILE).server_config
        self.assertEqual(sc.ip, '169.255.1.2')
        self.assertEqual(sc.port, 1234)
        
if __name__ == '__main__':
    unittest.main()
    