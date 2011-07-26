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
import time
import pybonjour
import select, socket
import random

from dandelion.service import Service

class DiscovererException(Exception):
    '''Exception from operations on the Discoverer'''

class DuplicateNodeException(DiscovererException):
    '''Exception raised when trying to add already exisiting node.'''

class Discoverer(Service):
    REGTYPE = "_dandelion._tcp"
    """The discoverer finds and keeps track of the status of known nodes."""

    def __init__(self, config, server_config):
        self._config = config
        self._server_config = server_config
        self._nodes = []
        self._running = False
        self._stop_requested = True
        self._register_fd = None
        self._thread = None
        self._listen_fds = []

    def add_node(self, ip, port=1337, pin=False, last_sync=None):
        """Explicitly add a new node to the list of known nodes.
        
        A pin:ed node will never be automatically removed by the Discoverer.
        """
        self._validate_node(ip, port)
        with threading.Lock():
            if self._contains_node(ip, port):
                raise DuplicateNodeException()
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


    def _register_callback(self, sdRef, flags, errorCode, name, regtype, domain):
        """Called when the service has been registered."""

    def _register_service(self):

        re_tries = 2
        while True:
            try:
                self._node_name = 'dandelionnode_' + ''.join([str(int(random.random() * 9)) for _ in range(8)])
                self._register_fd = pybonjour.DNSServiceRegister(name=self._node_name,
                                                             regtype=Discoverer.REGTYPE,
                                                             port=self._server_config.port,
                                                             callBack=self._register_callback)
                return

            except pybonjour.BonjourError:
                self._node_name = None
                if re_tries > 0:
                    re_tries -= 1
                    continue
                raise

    def _unregister_service(self):
        if self._register_fd is not None:
            self._register_fd.close()

    def _resolve_callback(self, fd, flags, interfaceIndex, errorCode, fullname,
                         hosttarget, port, txtRecord):

        # Close the handle used for the resolve request
        self._listen_fds.remove(fd)
        fd.close()

        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        def query_record_callback(fd, flags, interfaceIndex, errorCode, fullname,
                                   rrtype, rrclass, rdata, ttl):

            # Close the handle used to make the query
            self._listen_fds.remove(fd)
            fd.close()

            if errorCode != pybonjour.kDNSServiceErr_NoError:
                return

            # We have an A record to a node - add it to the sync pool
            try:
                self.add_node(ip=socket.inet_ntoa(rdata), port=port)
            except DuplicateNodeException:
                pass # Node already in the sync pool

        query_fd = pybonjour.DNSServiceQueryRecord(interfaceIndex=interfaceIndex,
                                                   fullname=hosttarget,
                                                   rrtype=pybonjour.kDNSServiceType_A,
                                                   callBack=query_record_callback)

        self._listen_fds.append(query_fd)


    def _browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName,
                    regtype, replyDomain):

        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            return

        # Did we just find our self?
        if serviceName == self._node_name:
            return

        self._service_registration_completed = True

        resolve_fd = pybonjour.DNSServiceResolve(0,
                                                 interfaceIndex,
                                                 serviceName,
                                                 regtype,
                                                 replyDomain,
                                                 self._resolve_callback)

        self._listen_fds.append(resolve_fd)

    def _work_loop(self):

        self._register_service() # Start advertising self

        # Start browsing for others
        browse_fd = pybonjour.DNSServiceBrowse(regtype=Discoverer.REGTYPE,
                                               callBack=self._browse_callback)

        # Pump zeroconf messages 
        while not self._stop_requested:
            ready = select.select([browse_fd] + self._listen_fds, [], [], 0.1)
            for fd in ready[0]:
                pybonjour.DNSServiceProcessResult(fd)
            time.sleep(0.5) # Throttle traffic slightly

        browse_fd.close()

        self._unregister_service() # Stop advertising self

        if len(self._listen_fds) > 0:
            raise Exception("pybonjour descriptors leaked!")

    def start(self):
        """Start the service. Block until the service is running."""

        if self._running:
            return # Starting twice is a nop

        self._stop_requested = False
        self._thread = threading.Thread(target=self._work_loop)
        self._thread.start()
        self._running = True

    def stop(self):
        """Stop the service. Block until the service is stopped."""

        if not self._running:
            return # Stopping twice is a nop

        self._stop_requested = True
        if self._thread is not None:
            self._thread.join(1)
            if self._thread.is_alive():
                raise Exception # Timeout

        self._running = False

    @property
    def running(self):
        """Returns True if the service is running, False otherwise"""
        return self._running

