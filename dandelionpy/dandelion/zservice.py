
import socket
import logging
import os, sys
from zeroconf import mdns

class ZeroconfService():
    
    def __init__(self, info_dict=None):
        
        self._info_dict = info_dict
        self._ttl = None
        self._mdns = mdns
        self._zeroconf = mdns.Zeroconf('')
        
        host_ip = socket.gethostbyname( socket.gethostname() )
        
        self._info = self._mdns.ServiceInfo(
            self._info_dict['type'], 
            self._info_dict['service_name'],
            socket.inet_aton(host_ip), 
            1234,
            0, 
            0, 
            self._info_dict['description']
        )

    def register(self):
        # joins multicast group and registers service
        #self._zeroconf.registerService(self._info, self._ttl)
        print("RegisterZeroconf")
        
    
    def unregister(self):
        # unregisters service and leaves multicast group
        #self._zeroconf.unregisterService(self._info)
        #self.close()
        print("UnRegisterZeroconf")
        
    
    def unregister_all(self):
        #self._zeroconf.unregisterAllServices()
        self.close()

        
    def close(self):
        self._zeroconf.close()    
        
        