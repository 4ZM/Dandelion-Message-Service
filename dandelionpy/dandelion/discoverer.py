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
        super().__init__(self._do_discovery, 1) # TODO: Get time from cfg-file 
        self._config = config
        self._nodes = []        
        
    def add_node(self, ip, port=1337, pin=False, last_sync=None):
        """Explicitly add a new node to the list of known nodes.
        
        A pin:ed node will never be automatically removed by the Discoverer.
        """
        self._validate_node(ip, port)
        with threading.Lock():
            if self._contains_node(ip, port): 
                raise DiscovererException()
            self._nodes.append({ 'ip' : ip, 'port' : port, 'pin' : pin, 'last_sync' : last_sync, 'processing' : False })

    def remove_node(self, ip, port=1337):
        """Explicitly remove a new node to the list of known nodes.
        
        This will remove a node even if it is pinned.  
        """
        self._validate_node(ip, port)
        with threading.Lock(): 
            if not self._contains_node(ip, port):
                raise DiscovererException()
            self._remove_node(ip, port)

    def contains_node(self, ip, port=1337):
        """Check if the Discoverer knows of a specific node."""
        self._validate_node(ip, port)
        with threading.Lock():
            return self._contains_node(ip, port)


    def acquire_node(self):
        """Request an available node and raise an exception if there are none.""" 
        
        with threading.Lock():
            resting_nodes = [n for n in self._nodes if not n['processing']]

            if len(resting_nodes) == 0: # Do we have any nodes to sync with? 
                raise DiscovererException()
            
            # Sync with the oldest one first
            resting_nodes.sort(key=lambda x: x['last_sync'] if x['last_sync'] is not None else datetime.datetime.min)
            next_node = resting_nodes[0]
            next_node['processing'] = True
        
            return (next_node['ip'], next_node['port']) 
        
    def release_node(self, ip, port, successful_sync):
        """Return a node to the discoverer that was previously acquired."""
        self._validate_node(ip, port)
        
        if not isinstance(successful_sync, bool):
            raise TypeError()
        
        with threading.Lock():
            if not self._contains_node(ip, port): 
                raise DiscovererException()
            
            node = [node for node in self._nodes if node['ip'] == ip and node['port'] == port][0]
            
            if not node['processing']: # Returned node that wasn't processed!
                raise DiscovererException()
            
            if successful_sync:
                node['last_sync'] = datetime.datetime.now()
            elif not node['pin']: # No success and not pinned; drop it.
                self._remove_node(node['ip'], node['port'])
            else: # No success and pinned; do nothing
                pass
              
            node['processing'] = False
            
    def _validate_node(self, ip, port):
        """Raise the appropriate exception if the ip or port is invalid. Otherwise do nothing."""
        if not isinstance(ip, str) or not isinstance(port, int):
            raise TypeError

        if not 0 < port <= 65535:
            raise ValueError

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
        