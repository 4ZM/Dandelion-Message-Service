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

from dandelion.service import RepetitiveWorker
from dandelion.network import Client

class Synchronizer(RepetitiveWorker):
    """The synchronizer dispatches requests to nodes found by the discoverer."""
    
    def __init__(self, discoverer, config, db):
        super().__init__(self._do_sync, 1) # TODO: get time from cfg-file
        self._config = config
        self._db = db
        self._discoverer = discoverer

    def sync(self, host, port):
        """Perform a synchronization with a specific node"""
        with Client(host, port, self._db) as client:
            client.execute_transaction()

    def _do_sync(self):
        """Use the discoverer to get a node (or several) to synchronize with 
        and then perform the synchronization.
        """    

        try: 
            host, port = self._discoverer.acquire_node()
        except:
            return
        
        try: 
            self.sync(host, port)
        except:
            self._discoverer.release_node(host, port, False) # Ack failure
        else:
            self._discoverer.release_node(host, port, True) # Ack success 

