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


class Service:
    """Abstract Base"""
    
    def start(self):
        """Start the service. Block until the service is running."""
    
    def stop(self):
        """Stop the service. Block until the service is running."""
    
    def restart(self):
        """Stop then start the service. Blocking call"""
        self.stop()
        self.start()
    
    @property
    def status(self):
        """A string with information about the service"""
    
    @property 
    def running(self):
        """Returns True if the service is running, False otherwise"""
        
    