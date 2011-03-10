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

    
import threading
import socketserver
from dandelion.protocol import Protocol, ProtocolParseError
from dandelion.database import ContentDB
import socket
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
    """A transaction that uses sockets for communication"""
    
    def __init__(self, sock):
        print("SOCKTRANSACTION: created")
        self._sock = sock
    
    def _read(self):
        
        try:
            s = self._sock.recv(Protocol.MESSAGE_LENGTH_BYTES*2).decode()
            d = Protocol.parse_size_str(s)
            data = self._sock.recv(d).decode()
            print("SOCKTRANSACTION: read: ", ''.join([s, data]))
            return ''.join([s, data])
    
        except Exception as e:
            print("SOCKTRANSACTION: reading Exception: ", e)
            return None
    
    def _write(self, data):
        print("SOCKTRANSACTION: write: ", data)
        self._sock.sendall(data)
    
    
class DandelionServerTransaction(SocketTransaction):
    """The server communication transaction logic for the dandelion communication protocol."""
     
    def __init__(self, sock, db):
        super().__init__(sock)
        self._db = db
     
    def process(self):
        
            print("SERVER TRANSACTION: Starting server transaction")

            data = self._read()
            
            if data is None:
                return
            
            print("S: Raw recv: ", data)
            
            try:
                
                if Protocol.is_message_id_list_request(data):
                    
                    tc = Protocol.parse_message_id_list_request(data)
                    print("S: Got message id list request, tc: ", tc)
                    
                    tc, msgs = self._db.messages_since(tc)

                    response_str = Protocol.create_message_id_list(tc, msgs)
                    
                    print("S: sending id list: ", response_str)
                    self._write(response_str.encode()) 
                    
                elif Protocol.is_message_list_request(data):
                    
                    msgids = Protocol.parse_message_list_request(data)
                    
                    print("S: Got message list request, mids: ", msgids)
                    
                    msgs = self._db.get_messages(msgids)
                    response_str = Protocol.create_message_list(msgs)
        
                    print("S: sending msg list: ", response_str)
                    self._write(response_str)
        
            except ProtocolParseError:
                print("S: ProtocolParseError")
                return
            
            except ValueError:
                print("S: ValueError")
                return
                
            except TypeError:
                print("S: TypeError")
                return
        

class DandelionServer(Service):
    
    def __init__(self, host, port, db):
        self._host = host
        self._port = port
        self._db = db
        self._running = False
    
    def start(self):
        """Start the service. Blocking call."""
        print('SERVER: Starting')
        self._server = _DandelionServerImpl(self._host, self._port, self._db)
        self._running = True
        
    def stop(self):
        """Stop the service. Blocking call."""
        print('SERVER: Stopping')
        self._server.shutdown()
        self._running = False
    
    @property
    def status(self):
        """A string with information about the service"""
        print(''.join(['Server status: Running: ', str(self._running), ' (', self._host, ':', str(self._port), ')']))
    
    @property 
    def running(self):
        """Returns True if the service is running, False otherwise"""
        return self._running
        

class _DandelionServerImpl(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, host, port, db):
        super(socketserver.TCPServer, self).__init__((host,port), _DandelionServerHandler)
        super(socketserver.ThreadingMixIn, self).__init__((host,port), _DandelionServerHandler)
        self.db = db

        # Start server
        self.server_thread = threading.Thread(target=self.serve_forever)
        self.server_thread.start()
        print('SERVER: Running')
        
    def shutdown(self):
        super(socketserver.TCPServer, self).shutdown()
        self.server_thread.join(None)

      
        
class _DandelionServerHandler(socketserver.BaseRequestHandler):

    def setup(self):
        self.request.settimeout(10.0)
        #self.request.setblocking(False)
        
    def handle(self):

        print("SERVER: In handler")

        self.request.send(Protocol.create_greeting_message(self.server.db.id).encode())

        comm_transaction = DandelionServerTransaction(self.request, self.server.db)
        comm_transaction.process() 


class DandelionClientTransaction(SocketTransaction):
    """The client communication transaction logic for the dandelion communication protocol."""
     
    def __init__(self, sock, db):
        super().__init__(sock)
        self._db = db
     
    def process(self):
        print("CLIENT TRANSACTION: starting")
        
        dbid = Protocol.parse_greeting_message(self._read())
        
        print("CLIENT TRANSACTION: greeting db: ", dbid)
        
        print("CLIENT TRANSACTION: sending id list req")

        self._write(Protocol.create_message_id_list_request().encode())
        
        s = self._read()

        print("CLIENT TRANSACTION: msg id response: ", s)


class DandelionClient:
    def __init__(self, host, port, db):
        self._host = host
        self._port = port
        self._db = db
    
    def __enter__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(10.0)
        print("CLIENT: connecting")
        self._sock.connect((self._host, self._port))
        return self
    
    def __exit__(self, type, value, traceback):
        print("CLIENT: disconnecting")
        self._sock.close()

    def execute_transaction(self):
        comm_transaction = DandelionClientTransaction(self._sock, self._db)
        comm_transaction.process()


