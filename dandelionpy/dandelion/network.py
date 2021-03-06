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
import random

import dandelion.protocol
from dandelion.protocol import ProtocolParseError
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
        self._sock.settimeout(10.0)
        #self._sock.setblocking(True)

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
            #print("SOCKTRANSACTION: read chunk: ", data)

            if len(data) == 0:
                break

            if self._terminator in data:
                total_data.extend(data[:data.find(self._terminator) + 1])
                break

            total_data.extend(data)

        #print("SOCKTRANSACTION: read: ", total_data)
        return total_data

    def _write(self, data):
        """Write the data bytes to the socket."""

        #print("SOCKTRANSACTION: write: ", data)
        self._sock.sendall(data)


class ServerTransaction(SocketTransaction):
    """The server communication transaction logic for the dandelion communication protocol."""

    class _AbortTransactionException(Exception):
        """Exception for internal signaling that the transaction should end."""

    class TurnRequest(Exception):
        """Raised when client has requested a turn-around"""

    def __init__(self, sock, db, buff_size=1024):
        super().__init__(sock, dandelion.protocol.TERMINATOR.encode(), buff_size)
        self._db = db

    def process(self):
        """The DMS server transaction logic.
        
        Starts by sending a greeting. Will then service the connected client 
        repeatedly until it disconnects or the server times out."""

        #print("SERVER TRANSACTION: Starting server transaction")

        """Write greeting"""
        self._write(dandelion.protocol.create_greeting_message(self._db.id).encode())

        while True: # Serve client as long as it is active 
            try:
                bdata = self._read()
            except socket.timeout:
                break

            try:
                self._process_data(bdata)
            except ServerTransaction._AbortTransactionException:
                #print("SERVER TRANSACTION: Ending server transaction A")
                return

        #print("SERVER TRANSACTION: Ending server transaction")


    def _process_data(self, bdata):
        """Internal helper function that processes what should be a server request."""

        try:
            data = bdata.decode()

            #print("SERVER Read data: ", data)

            if dandelion.protocol.is_message_id_list_request(data):
                tc = dandelion.protocol.parse_message_id_list_request(data)
                tc, msgs = self._db.get_messages(time_cookie=tc)
                random.shuffle(msgs) # To avoid last piece problem
                response_str = dandelion.protocol.create_message_id_list(tc, msgs)
                self._write(response_str.encode())
            elif dandelion.protocol.is_message_list_request(data):
                msgids = dandelion.protocol.parse_message_list_request(data)
                _, msgs = self._db.get_messages(msgids=msgids)
                response_str = dandelion.protocol.create_message_list(msgs)
                self._write(response_str.encode())
            elif dandelion.protocol.is_identity_id_list_request(data):
                tc = dandelion.protocol.parse_identity_id_list_request(data)
                tc, ids = self._db.get_identities(time_cookie=tc)
                random.shuffle(ids) # To avoid last piece problem
                response_str = dandelion.protocol.create_identity_id_list(tc, ids)
                self._write(response_str.encode())
            elif dandelion.protocol.is_identity_list_request(data):
                identities = dandelion.protocol.parse_identity_list_request(data)
                _, ids = self._db.get_identities(fingerprints=identities)
                response_str = dandelion.protocol.create_identity_list(ids)
                self._write(response_str.encode())
            elif dandelion.protocol.is_turn_request(data):
                response_str = dandelion.protocol.create_turn_reply()
                self._write(response_str.encode())
                raise ServerTransaction.TurnRequest
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
        self._server = None

    def start(self):
        """Start the service. Blocking call."""
#        print('SERVER: Starting')
        self._server = _ServerImpl(self._ip, self._port, self._db)
        self._running = True

    def stop(self):
        """Stop the service. Blocking call."""
#        print('SERVER: Stopping')
        if self._server is not None:
            self._server.shutdown()

        self._server = None
        self._running = False
#        print('SERVER: Stopped')

    @property
    def ip(self):
        """Get the IP the server currently binds to."""
        return self._ip

    @ip.setter
    def ip(self, value):
        """Set the IP the server should bind to. 
        Note: The sever must be stopped before setting the address.
        """

        if self._running:
            raise Exception

        self._ip = value

    @property
    def port(self):
        """Get the port the server currently listens to."""
        return self._port

    @port.setter
    def port(self, value):
        """Set the port the server should listen to. 
        Note: The sever must be stopped before setting the port.
        """

        if self._running:
            raise Exception

        self._port = value

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
        #self.request.setblocking(True)

    def handle(self):

#        print("SERVER: In handler")

        comm_transaction = ServerTransaction(self.request, self.server.db)
        try:
            comm_transaction.process()
        except ServerTransaction.TurnRequest:
            comm_transaction = ClientTransaction(self.request, self.server.db)
            comm_transaction.process()

#        print("SERVER: Out handler")


class ClientTransaction(SocketTransaction):
    """The client communication transaction logic for the dandelion communication protocol."""

    def __init__(self, sock, db, buff_size=1024):
        super().__init__(sock, dandelion.protocol.TERMINATOR.encode(), buff_size)
        self._db = db

    def process(self):
#        print("CLIENT TRANSACTION: starting")

        try:
            """Read greeting from server"""
            dbid = dandelion.protocol.parse_greeting_message(self._read().decode())

            time_cookie = self._db.get_last_time_cookie(dbid)

            """Request and read message id's"""
            self._write(dandelion.protocol.create_message_id_list_request(time_cookie).encode())
            tc, msgids = dandelion.protocol.parse_message_id_list(self._read().decode())

            req_msgids = [mid for mid in msgids if not self._db.contains_message(mid)]

            if len(req_msgids) > 0: # Anything to fetch?
                random.shuffle(req_msgids) # To avoid last piece problem

                """Request and read messages"""
                self._write(dandelion.protocol.create_message_list_request(req_msgids).encode())
                msgs = dandelion.protocol.parse_message_list(self._read().decode())

                """Store the new messages"""
                self._db.add_messages(msgs)

            """Request and read user id's"""
            self._write(dandelion.protocol.create_identity_id_list_request(time_cookie).encode())
            _, identityids = dandelion.protocol.parse_identity_id_list(self._read().decode())

            req_ids = [id for id in identityids if not self._db.contains_identity(id)]

            if len(req_ids) > 0: # Anything to fetch?
                random.shuffle(req_ids) # To avoid last piece problem

                """Request and read identities"""
                self._write(dandelion.protocol.create_identity_list_request(req_ids).encode())
                ids = dandelion.protocol.parse_identity_list(self._read().decode())

                """Store the new identities"""
                self._db.add_identities(ids)

            """Record the synchronization time for the remote db"""
            self._db.update_last_time_cookie(dbid, tc)

        except (socket.timeout, ProtocolParseError, ValueError, TypeError):
            """Do nothing on error, just hang up"""
            #print("CLIENT TRANSACTION: Error processing data from server")

        #print("CLIENT TRANSACTION: hanging up")

    def turn(self):
        self._write(dandelion.protocol.create_turn_request().encode())
        ok = dandelion.protocol.parse_turn_reply(self._read().decode())
        return ok

class Client:
    def __init__(self, host, port, db):
        self._ip = host
        self._port = port
        self._db = db

    def __enter__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(10.0)
        #print("CLIENT: connecting")
        self._sock.connect((self._ip, self._port))
        return self

    def __exit__(self, type, value, traceback):
        #print("CLIENT: disconnecting")
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self._sock.close()

    def execute_transaction(self):
        comm_transaction = ClientTransaction(self._sock, self._db)
        comm_transaction.process()
        if comm_transaction.turn():
            comm_transaction = ServerTransaction(self._sock, self._db)
            comm_transaction.process()
