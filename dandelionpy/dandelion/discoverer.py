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

import threading
import datetime

from dandelion.service import RepetitiveWorker

class DiscovererException(Exception):
    '''Exception from operations on the Discoverer'''


class Discoverer(RepetitiveWorker):
    """The discoverer finds and keeps track of the status of known nodes."""
    
    def __init__(self, config):
        super().__init__(self._do_discovery, 5) # TODO: Get time from cfg-file 
        self._config = config
        self._nodes = []        
        
    def add_node(self, ip, port=1337, pin=False, last_sync=None):
        """Explicitly add a new node to the list of known nodes.
        
        A pin:ed node will never be removed by the Discoverer.
        """
        with threading.Lock():
            
            if self._contains_node(ip, port): 
                raise DiscovererException()
            
            self._nodes.append({ 'ip' : ip, 'port' : port, 'pin' : pin, 'last_sync' : last_sync, 'processing' : False })

    def remove_node(self, ip, port=1337):
        """Explicitly remove a new node to the list of known nodes.
        
        This will remove a node even if it is pinned.  
        """
        with threading.Lock(): 
            if not self._contains_node(ip, port):
                raise DiscovererException()
            self._remove_node(ip, port)

    def acquire_node(self):
        """Request an available node and raise an exception if there are none.""" 
        
        with threading.Lock():
            resting_nodes = [n for n in self._nodes if not n['processing']]
            
            if len(resting_nodes) == 0: # Do we have any nodes to sync with? 
                raise DiscovererException()
            
            # Sync with the oldest one first
            next_node = sorted(resting_nodes, cmp=lambda x,y: x['last_sync'] < y['last_sync'])[0] 
            next_node['processing'] = True
        
            return (next_node['ip'], next_node['port']) 
        
    def release_node(self, ip, port, successful_sync):
        """Return a node to the discoverer that was previously acquired."""
        
        with threading.Lock():
            if not self._contains_node(ip, port): 
                raise DiscovererException()
            
            node = [node for node in self._nodes if node['ip'] == ip and node['port'] == port][0]
            
            if successful_sync:
                node['last_sync'] = datetime().now()
            elif not node['pin']: # No success and not pinned; drop it.
                self._remove_node(node['ip'], node['port'])
            else: # No success and pinned; do nothing
                pass
              
            node['processing'] = False
            
    def _remove_node(self, ip, port=1337):
        """ 
        Should only be executed inside a lock.
        """
        
        # Copy all but the one to remove
        self._nodes = [node for node in self._nodes if not (node['ip'] == ip and node['port'] == port)]

    def _contains_node(self, ip, port):
        """Check if the Discoverer has the ip/port in it's node list.
        
        Should only be executed inside a lock.
        """
        return len([node for node in self._nodes if node['ip'] == ip and node['port'] == port]) > 0
        
    def _do_discovery(self):
        """Find and add new nodes to node list here."""
        
        # TODO: Implement!
        