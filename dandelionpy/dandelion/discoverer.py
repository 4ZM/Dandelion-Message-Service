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


import socket
import threading
from zeroconf import mdns

class Discoverer:
    def __init__(self, type=None):
        print("DISCOVERER INITIATED")
        self._type = type
        self._mdns = mdns
        
        
    def start(self):
        print("ServiceListener starts to listen ... ")
        self._listener = ServiceListener(self._mdns.Zeroconf())
        self._browser = ServiceBrowser(self._mdns.Zeroconf(), self._type, self._listener)
        
    def stop(self):
        print("ServiceListener stops to listen ...")
        self._mdns.Zeroconf().close()

    @property
    def available_services(self):
        return self.get_results()
    
    def get_results(self):
        return self._listener.available_services
        



class ServiceBrowser(threading.Thread):
    """ wrapper class for the mdns.ServiceBrowser threaded class """
    def __init__(self, zeroconf, type, listener):
        threading.Thread.__init__(self)
        print("Starting ServiceBrowser")
        self._zeroconf = zeroconf   #the whole shobang, this can be tidied up inside the zeroconf package
        self._type = type
        self._listener = listener
        mdns.ServiceBrowser(self._zeroconf, self._type, self._listener)
      
class ServiceListener(object):
        
    def __init__(self, zeroconf):
        self._zeroconf = zeroconf
        self._available_services = []
    
    def removeService(self, zeroconf, type, name):
        print("Service", name, "removed")
        self._available_services.pop()
        
    def addService(self, zeroconf, type, name):
        """ Called if a service is added to the network"""
        print("DISCOVERER SERVICE", name, " - Added")
        print("DISCOVERER SERVICE TYPE: ", type)
        _info = self._zeroconf.getServiceInfo(type, name)
        info_dict = {
                     'address' : _info.getAddress(),
                     'address_verbose' : str(socket.inet_ntoa(_info.getAddress())),
                     'port' : _info.getPort(),
                     'server' : _info.getServer(),
                     'text'  : _info.getText(),
                     'properties' : _info.getProperties()
                     }

           
        self._available_services.append(info_dict)
        
    @property
    def available_services(self):
        return self._available_services
            
        