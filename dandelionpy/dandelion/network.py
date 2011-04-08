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
import socket
import socketserver

from dandelion.protocol import Protocol, ProtocolParseError
from dandelion.database import InMemoryContentDB
from dandelion.service import Service
    
    
class Transaction:
    """Interface for communication transactions.
    
    Represents a synchronous, serial, read and write communications channel 
    and the logic for reading and writing to the channel in some meaningful 
    way.  
    """
    
    def _read(self):
        """Read binary data from the communication channel and return it.""" 
    
    def _write(self, data):
        """Write data to the communication channel. Blocking call."""
    
    def process(self):
        """Perform the communication transaction.
        
        This function should be overridden to implement the logic for reading and 
        writing according to some protocol.
        """

class SocketTransaction(Transaction):
    """A transaction that uses sockets for communication."""
    
    def __init__(self, sock, terminator, buff_size=1024):
        """Setup the SocketTransaction.
        
        The terminator is a single character of type bytes. Read operations will 
        consume data until the terminator is sent. 
        
        Note: The SocketTransaction class is an abstract base class and should 
        not be used stand alone. This function should be called by the sub classes.
        """
        #print("SOCKTRANSACTION: created")
        
        if sock is None:
            raise TypeError
        
        if terminator is None or not isinstance(terminator, bytes):
            raise TypeError
        
        if len(terminator) > 1:
            raise ValueError 
        
        if buff_size is None or not isinstance(buff_size, int):
            raise TypeError
        
        if buff_size <= 0:
            raise ValueError        
        
        self._sock = sock
        self._terminator = terminator
        self._buff_size = buff_size
    
    def _read(self):
        """Read bytes from the socket until a terminator is received.
        
        Implementation of the Transaction._read function.
        
        Returns the bytes read (including the terminator).
        """
        
        total_data = bytearray()

        while True:
            data = self._sock.recv(self._buff_size)
#            print("SOCKTRANSACTION: read chunk: ", data)
            
            if len(data) == 0:
                break
            
            if self._terminator in data:
                total_data.extend(data[:data.find(self._terminator) + 1])
                break
            
            total_data.extend(data)

#        print("SOCKTRANSACTION: read: ", total_data)
        return total_data
    
    def _write(self, data):
        """Write the data bytes to the socket."""
        
        #print("SOCKTRANSACTION: write: ", data)
        self._sock.sendall(data)
    
    
class ServerTransaction(SocketTransaction):
    """The server communication transaction logic for the dandelion communication protocol."""
    
    class _AbortTransactionException(Exception):
        """Exception for internal signaling that the transaction should end.""" 
     
    def __init__(self, sock, db, buff_size=1024):
        super().__init__(sock, Protocol.TERMINATOR.encode(), buff_size)
        self._db = db
     
    def process(self):
        """The DMS server transaction logic.
        
        Starts by sending a greeting. Will then service the connected client 
        repeatedly until it disconnects or the server times out."""
         
#        print("SERVER TRANSACTION: Starting server transaction")
        
        """Write greeting"""
        self._write(Protocol.create_greeting_message(self._db.id).encode())

        while True: # Serve client as long as it is active 
            try:
                bdata = self._read()
            except socket.timeout:
                break

            try:
                self._process_data(bdata)
            except ServerTransaction._AbortTransactionException:
#                print("SERVER TRANSACTION: Ending server transaction A")
                return
            
#        print("SERVER TRANSACTION: Ending server transaction")


    def _process_data(self, bdata):
        """Internal helper function that processes what should be a server request."""
         
        try:
            data = bdata.decode()

            if Protocol.is_message_id_list_request(data):
                
                tc = Protocol.parse_message_id_list_request(data)
                tc, msgs = self._db.get_messages_since(tc)
                response_str = Protocol.create_message_id_list(tc, msgs)
                self._write(response_str.encode()) 

            elif Protocol.is_message_list_request(data):
                msgids = Protocol.parse_message_list_request(data)
                msgs = self._db.get_messages(msgids)
                response_str = Protocol.create_message_list(msgs)
                self._write(response_str.encode())

            else:
                raise ProtocolParseError
        
        except (ProtocolParseError, ValueError, TypeError):
            #print("SERVER TRANSACTION: Error processing data from client")
            raise ServerTransaction._AbortTransactionException

class Server(Service):
    
    def __init__(self, config, db, id):
        self._ip = config.ip
        self._port = config.port
        self._db = db
        self._identity = id
        self._running = False
    
    def start(self):
        """Start the service. Blocking call."""
#        print('SERVER: Starting')
        self._server = _ServerImpl(self._ip, self._port, self._db)
        self._running = True
        
    def stop(self):
        """Stop the service. Blocking call."""
#        print('SERVER: Stopping')
        self._server.shutdown()
        self._running = False
#        print('SERVER: Stopped')
    
    @property
    def status(self):
        """A string with information about the service"""
        print(''.join(['Server status: Running: ', str(self._running), ' (', self._ip, ':', str(self._port), ')']))
    
    @property 
    def running(self):
        """Returns True if the service is running, False otherwise"""
        return self._running
        

class _ServerImpl(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, host, port, db):
        super(socketserver.TCPServer, self).__init__((host, port), _ServerHandler)
        super(socketserver.ThreadingMixIn, self).__init__((host, port), _ServerHandler)
        self.db = db

        # Start server
        self.server_thread = threading.Thread(target=self.serve_forever)
        self.server_thread.start()
#        print('SERVER: Running')
        
    def shutdown(self):
#        print('SERVER: Shutdown')
        super(socketserver.TCPServer, self).shutdown()
        self.server_thread.join(None)
#        print('SERVER: Shutdown completed')

      
        
class _ServerHandler(socketserver.BaseRequestHandler):

    def setup(self):
        self.request.settimeout(5.0)
        #self.request.setblocking(False)
        
    def handle(self):

#        print("SERVER: In handler")

        comm_transaction = ServerTransaction(self.request, self.server.db)
        comm_transaction.process() 
        
#        print("SERVER: Out handler")


class ClientTransaction(SocketTransaction):
    """The client communication transaction logic for the dandelion communication protocol."""

    def __init__(self, sock, db, buff_size=1024):
        super().__init__(sock, Protocol.TERMINATOR.encode(), buff_size)
        self._db = db
     
    def process(self):
#        print("CLIENT TRANSACTION: starting")
        
        try:
            """Read greeting from server"""
            dbid = Protocol.parse_greeting_message(self._read().decode())

            time_cookie = self._db.get_last_time_cookie(dbid)
            
            """Request and read message id's"""
            self._write(Protocol.create_message_id_list_request(time_cookie).encode())
            _, msgids = Protocol.parse_message_id_list(self._read().decode())
            
            req_msgids = [mid for mid in msgids if not self._db.contains_message(mid)]

            if len(req_msgids) == 0: # Nothing to fetch
#                print("CLIENT TRANSACTION: hanging up - 0 sync")
                return 
            
            """Request and read messages"""        
            self._write(Protocol.create_message_list_request(req_msgids).encode())
            msgs = Protocol.parse_message_list(self._read().decode())

            """Store the new messages"""
            self._db.add_messages(msgs)
            
        except (socket.timeout, ProtocolParseError, ValueError, TypeError):
            """Do nothing on error, just hang up"""
            #print("CLIENT TRANSACTION: Error processing data from server")

        # print("CLIENT TRANSACTION: hanging up")


class Client:
    def __init__(self, host, port, db):
        self._ip = host
        self._port = port
        self._db = db
    
    def __enter__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5.0)
        #print("CLIENT: connecting")
        self._sock.connect((self._ip, self._port))
        return self
    
    def __exit__(self, type, value, traceback):
        #print("CLIENT: disconnecting")
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()

    def execute_transaction(self):
        comm_transaction = ClientTransaction(self._sock, self._db)
        comm_transaction.process()


