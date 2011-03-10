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

from service import Service
from discoverer import Discoverer
from threading import Thread

class Synchronizer(Service):
    
    def __init__(self, config, db):
        self._config = config
        self._db = db
        self._discoverer = Discoverer()
        
    def start(self):
        """Start the service. Block until the service is running."""
        print('SYNCHRONIZER: Starting')
        self._stop_requested = False
        self._thread = Thread(target=self._sync_loop)
        self._thread.start()
        self._running = True
    
    def stop(self):
        """Stop the service. Block until the service is running."""
        
        self._stop_requested = True
        print('SYNCHRONIZER: Stopping')
        self._thread.join(0.1)
        if self._thread.is_alive():
            raise Exception # Timeout
            
        self._running = False
        
    
    def restart(self):
        """Stop then start the service. Blocking call"""
        self.stop()
        self.start()
    
    @property
    def status(self):
        """A string with information about the service"""
        print(''.join(['Synchronizer status: Running: ', str(self._running)]))
        
    
    @property 
    def running(self):
        """Returns True if the service is running, False otherwise"""
        return self._running
        
    def _sync_loop(self):
        print('SYNCHRONIZER: Running')

        while not self._stop_requested:
            pass
    