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
import time
import os

import dandelion.service
import dandelion.synchronizer
import dandelion.discoverer
import dandelion.config

def _wait_for_cnt(lst, limit=1, time_out=0.5):
    """Helper function for synchronization. Will return when the lists length 
    is limit or longer or when the time_out has transpired."""
    t1 = t2 = time.time()
    
    while t2 - t1 < time_out:
        if len(lst) >= limit:
            return True
        time.sleep(0.01) # Don't busy wait
        t2 = time.time()
        
    return False

class RepetitiveWorkerTest(unittest.TestCase):
    """Unit test suite for the RepetitiveWorker helper class."""

    def test_construction(self):
        def _test_func():
            pass

        # Vanilla construction        
        rw = dandelion.service.RepetitiveWorker(_test_func, min_wait_time_sec=1)
        self.assertFalse(rw.running)
        rw = dandelion.service.RepetitiveWorker(_test_func)
        self.assertFalse(rw.running)

        # Don't wait construction        
        rw = dandelion.service.RepetitiveWorker(_test_func, min_wait_time_sec=0)
        self.assertFalse(rw.running)

        # Ok, to use same func twice
        rw = dandelion.service.RepetitiveWorker(_test_func, min_wait_time_sec=0)
        self.assertFalse(rw.running)

        # Illegal construction
        self.assertRaises(TypeError, dandelion.service.RepetitiveWorker, None)
        self.assertRaises(TypeError, dandelion.service.RepetitiveWorker, "fu")
        self.assertRaises(TypeError, dandelion.service.RepetitiveWorker, _test_func, None)
        self.assertRaises(ValueError, dandelion.service.RepetitiveWorker, _test_func, "fu")
        self.assertRaises(ValueError, dandelion.service.RepetitiveWorker, _test_func, -1)

    def test_start_stop(self):
        lst = []
        def _test_func():
            lst.append(1337)

        rw = dandelion.service.RepetitiveWorker(_test_func, min_wait_time_sec=0)
        
        # Constructions shouldn't call the work function
        self.assertFalse(rw.running)
        self.assertEqual(len(lst), 0)
        
        # Start, check that it's running and then stop
        rw.start()
        self.assertTrue(_wait_for_cnt(lst)) # Check that the function did run
        self.assertTrue(rw.running)
        rw.stop()
        self.assertFalse(rw.running)
        
        # Re-start and test again
        rw.start()
        self.assertTrue(_wait_for_cnt(lst, limit=len(lst))) # Check that the function did run
        self.assertTrue(rw.running)
        rw.stop()
        self.assertFalse(rw.running)

        # Test "twice" operations
        rw.start()
        self.assertTrue(rw.running)
        rw.start()
        self.assertTrue(rw.running)
        rw.stop()
        self.assertFalse(rw.running)
        rw.stop()
        self.assertFalse(rw.running)
       
        # Test restart
        self.assertFalse(rw.running)
        rw.restart()
        self.assertTrue(rw.running)
        rw.restart()
        self.assertTrue(rw.running)
        
class DiscovererTest(unittest.TestCase):
    """Unit test suite for the Discoverer class."""

    TEST_FILE = os.path.join(os.path.split(os.path.abspath(__file__))[0], 
                             'config_test_data.conf')

    def test_start_stop(self): 
        d = dandelion.discoverer.Discoverer(dandelion.config.ConfigManager(self.TEST_FILE))
        self.assertFalse(d.running)
        d.start()
        self.assertTrue(d.running)
        d.stop()
        self.assertFalse(d.running)    

    def test_add_remove(self): 
        d = dandelion.discoverer.Discoverer(dandelion.config.ConfigManager(self.TEST_FILE))

        # Initially empty
        self.assertFalse(d.contains_node("127.0.0.1", 1234))
        
        # Add the node
        d.add_node("127.0.0.1", 1234)
        self.assertTrue(d.contains_node("127.0.0.1", 1234))

        # Adding same node is error
        self.assertRaises(dandelion.discoverer.DiscovererException, d.add_node, "127.0.0.1", 1234) 

        # Remove the node
        d.remove_node("127.0.0.1", 1234)
        self.assertFalse(d.contains_node("127.0.0.1", 1234))

        # Removing same node is error
        self.assertRaises(dandelion.discoverer.DiscovererException, d.remove_node, "127.0.0.1", 1234) 
        
        # Illegal arguments
        self.assertRaises(TypeError, d.add_node, None, 1234)
        self.assertRaises(TypeError, d.add_node, 1234, 1234)
        
        self.assertRaises(TypeError, d.add_node, "127.0.0.1", None)
        self.assertRaises(TypeError, d.add_node, "127.0.0.1", "1234")
        self.assertRaises(ValueError, d.add_node, "127.0.0.1", -1234)
        self.assertRaises(ValueError, d.add_node, "127.0.0.1", 65536)

    def test_requst_release(self):
        d = dandelion.discoverer.Discoverer(dandelion.config.ConfigManager(self.TEST_FILE))
        
        # No nodes to acquire yet...
        self.assertRaises(dandelion.discoverer.DiscovererException, d.acquire_node)
        
        d.add_node("127.0.0.1", 1234) 

        # We should get the only available node
        ip, port = d.acquire_node()
        self.assertEqual(ip, "127.0.0.1")
        self.assertEqual(port, 1234)
        
        # No nodes left to request, so fail
        self.assertRaises(dandelion.discoverer.DiscovererException, d.acquire_node)
        
        # Hand the node back to the discoverer
        d.release_node(ip, port, True)
        
        # Can't release the node twice
        self.assertRaises(dandelion.discoverer.DiscovererException, d.release_node, ip, port, True)

        # Now we can acquire it again and hand it back again
        ip, port = d.acquire_node()
        self.assertEqual(ip, "127.0.0.1")
        self.assertEqual(port, 1234)
        d.release_node(ip, port, True)
        
        # Can't acquire deleted nodes...
        d.remove_node("127.0.0.1", 1234)
        self.assertRaises(dandelion.discoverer.DiscovererException, d.acquire_node)
        
        # The out-of-sync case
        d.add_node("127.0.0.1", 1234)
        ip, port = d.acquire_node()
        d.remove_node("127.0.0.1", 1234) 
        self.assertRaises(dandelion.discoverer.DiscovererException, d.release_node, ip, port, True)
        
        # Release with illegal arguments
        self.assertRaises(TypeError, d.release_node, None, 1234, True)
        self.assertRaises(TypeError, d.release_node, 1234, 1234, True)
        
        self.assertRaises(TypeError, d.release_node, "127.0.0.1", None, True)
        self.assertRaises(TypeError, d.release_node, "127.0.0.1", "1234", True)
        self.assertRaises(ValueError, d.release_node, "127.0.0.1", -1234, True)
        self.assertRaises(ValueError, d.release_node, "127.0.0.1", 65536, True)

        self.assertRaises(TypeError, d.release_node, "127.0.0.1", 1234, None)
        self.assertRaises(TypeError, d.release_node, "127.0.0.1", 1234, 1234)
        
    def test_pining(self):
        d = dandelion.discoverer.Discoverer(dandelion.config.ConfigManager(self.TEST_FILE))

        # Not pinned (default)
        d.add_node("127.0.0.1", 1234) 
        ip, port = d.acquire_node()
        self.assertEqual(ip, "127.0.0.1")
        self.assertEqual(port, 1234)
        d.release_node(ip, port, False) # Simulate failed sync (automatically removed)
        self.assertRaises(dandelion.discoverer.DiscovererException, d.acquire_node)

        # Pinned node
        d.add_node("127.0.0.1", 1234, pin=True) 
        ip, port = d.acquire_node()
        d.release_node(ip, port, False) # Simulate failed sync (not automatically removed)
        ip, port = d.acquire_node()
        self.assertEqual(ip, "127.0.0.1")
        self.assertEqual(port, 1234)

    def test_acquire_order(self):
        d = dandelion.discoverer.Discoverer(dandelion.config.ConfigManager(self.TEST_FILE))

        d.add_node("127.0.0.1", 1)
        d.add_node("127.0.0.1", 2)
        d.add_node("127.0.0.1", 3)
        
        ip1, port1 = d.acquire_node()
        ip2, port2 = d.acquire_node()
        ip3, port3 = d.acquire_node()
        
        # Release as 2,3,1
        d.release_node(ip2, port2, True)
        time.sleep(1)
        d.release_node(ip3, port3, True)
        time.sleep(1)
        d.release_node(ip1, port1, True)

        # Should get them in order 2,3,1 (oldest first)        
        ip, port = d.acquire_node()
        self.assertEqual(ip, "127.0.0.1")
        self.assertEqual(port, 2)
        ip, port = d.acquire_node()
        self.assertEqual(ip, "127.0.0.1")
        self.assertEqual(port, 3)
        ip, port = d.acquire_node()
        self.assertEqual(ip, "127.0.0.1")
        self.assertEqual(port, 1)

class SynchronizerTest(unittest.TestCase):
    """Unit test suite for the Synchronizer class."""
     
    def test_xxx(self):
        pass

if __name__ == '__main__':
    unittest.main()
