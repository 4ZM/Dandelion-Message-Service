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

import unittest
from dandelion.network import SocketTransaction, ServerTransaction
import socket
import threading
from dandelion.database import ContentDB
from dandelion.message import Message
from dandelion.protocol import Protocol

HOST = '127.0.0.1'
PORT = 1337
TIMEOUT = 0.1

class TestClientHelper:
    """A helper to create a socket (client side) for testing communication"""

    @property
    def sock(self):
        return self._sock
    
    def __enter__(self):    
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(TIMEOUT)
        self._sock.connect((HOST, PORT))
        return self
        
    def __exit__(self, type, value, traceback):
        self._sock.close()
        

class TestServerHelper:
    """A helper to create a socket (server side) for testing communication"""
    
    @property
    def sock(self):
        while self._client_sock is None: # Block until there is a connection 
            pass
        return self._client_sock
    
    def __enter__(self):    
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind((HOST, PORT))
        self._sock.listen(1)
        self._sock.settimeout(TIMEOUT)
        self._client_sock = None
        self._thread = threading.Thread(target=self._wait_for_connection)
        self._thread.start()
        return self
    
    def __exit__(self, type, value, traceback):
        self._thread.join()
        self._sock.close()
        
    def _wait_for_connection(self):
        self._client_sock, _ = self._sock.accept()
        self._client_sock.settimeout(TIMEOUT)
        
        
def recv_n(sock, nbytes):
    return b''.join([sock.recv(1) for _ in range(nbytes)])


class MessageTest(unittest.TestCase):
    """Unit test suite for the DMS network transactions"""
     
    def test_helper_classes(self):
        """This test case tests the helper server and client classes used in the other test cases.""" 
    
        with TestServerHelper() as server_helper:
            with TestClientHelper() as client_helper:

                self.assertNotEqual(server_helper, None)
                self.assertNotEqual(client_helper, None)
                
                self.assertRaises(socket.timeout, recv_n, client_helper.sock, 1)
                self.assertRaises(socket.timeout, recv_n, client_helper.sock, 10000)
                
                msg = b'123'
                
                server_helper.sock.sendall(msg)
                ret = recv_n(client_helper.sock, len(msg))
                self.assertTrue(isinstance(ret, bytes))
                self.assertEqual(msg, ret)

                server_helper.sock.sendall(msg)
                server_helper.sock.sendall(msg)
                ret = recv_n(client_helper.sock, len(msg) * 2)
                self.assertEqual(b''.join([msg, msg]), ret)

                server_helper.sock.sendall(msg)
                self.assertRaises(socket.timeout, recv_n, client_helper.sock, len(msg) * 2)
                self.assertRaises(socket.timeout, recv_n, client_helper.sock, 1)

                server_helper.sock.sendall(b'')
                ret = recv_n(client_helper.sock, 0)
                self.assertEqual(ret, b'')
                ret = recv_n(client_helper.sock, 0)
                self.assertEqual(ret, b'')
                self.assertRaises(socket.timeout, recv_n, client_helper.sock, 1)


    def test_socket_transaction_ctor(self):
        """Tests the SocketTransaction base class constructor""" 
    
        with TestServerHelper() as server_helper:
            with TestClientHelper() as _:
                
                SocketTransaction(server_helper.sock, b'\n')
                SocketTransaction(server_helper.sock, b'\n', 2048)
                
                self.assertRaises(TypeError, SocketTransaction, server_helper.sock, None)
                self.assertRaises(TypeError, SocketTransaction, server_helper.sock, '\n')
                self.assertRaises(ValueError, SocketTransaction, server_helper.sock, b'12')
                
                self.assertRaises(TypeError, SocketTransaction, server_helper.sock, b'\n', None)
                self.assertRaises(TypeError, SocketTransaction, server_helper.sock, b'\n', 'str')
                self.assertRaises(ValueError, SocketTransaction, server_helper.sock, b'\n', 0)
                self.assertRaises(ValueError, SocketTransaction, server_helper.sock, b'\n', -10)


    def test_socket_transaction_write(self):
        """Tests the SocketTransaction base class _write function (protected)""" 
    
        with TestServerHelper() as server_helper:
            with TestClientHelper() as client_helper:
                
                msg = b'123'
                
                """Using the server socket"""
                st_a = SocketTransaction(server_helper.sock, b'\n')

                st_a._write(msg)
                ret = recv_n(client_helper.sock, len(msg))
                self.assertEqual(msg, ret)

                st_a._write(b'')
                ret = recv_n(client_helper.sock, 0)
                self.assertEqual(ret, b'')

                self.assertRaises(TypeError, st_a._write, 1)
                self.assertRaises(TypeError, st_a._write, None)
                self.assertRaises(TypeError, st_a._write, 'str')
                
                """Using the client socket"""
                st_b = SocketTransaction(client_helper.sock, b'\n')

                st_b._write(msg)
                ret = recv_n(server_helper.sock, len(msg))
                self.assertEqual(msg, ret)

                st_b._write(b'')
                ret = recv_n(server_helper.sock, 0)
                self.assertEqual(ret, b'')

                self.assertRaises(TypeError, st_b._write, 1)
                self.assertRaises(TypeError, st_b._write, None)
                self.assertRaises(TypeError, st_b._write, 'str')
                
                
    def test_socket_transaction_read(self):
        """Tests the SocketTransaction base class _read function (protected)""" 
    
        with TestServerHelper() as server_helper:
            with TestClientHelper() as client_helper:
                
                msg = b'123\n'
                
                """Using the server socket"""
                client_helper.sock.sendall(msg)
                ret = SocketTransaction(server_helper.sock, b'\n')._read()
                self.assertEqual(msg, ret)

                """Using the client socket"""
                server_helper.sock.sendall(msg)
                ret = SocketTransaction(client_helper.sock, b'\n')._read()
                self.assertEqual(msg, ret)

                """Reading with different buffer lengths"""
                server_helper.sock.sendall(msg)
                ret = SocketTransaction(client_helper.sock, b'\n', 1)._read()
                self.assertEqual(msg, ret)

                server_helper.sock.sendall(msg)
                ret = SocketTransaction(client_helper.sock, b'\n', 2)._read()
                self.assertEqual(msg, ret)

                server_helper.sock.sendall(msg)
                ret = SocketTransaction(client_helper.sock, b'\n', 3)._read()
                self.assertEqual(msg, ret)

                server_helper.sock.sendall(msg)
                ret = SocketTransaction(client_helper.sock, b'\n', 4)._read()
                self.assertEqual(msg, ret)

    def test_server_transaction(self):
        """Tests the server transaction protocol and logic""" 
    
        db = ContentDB()
        tc = db.add_messages([Message('fubar'), Message('foo'), Message('bar')])
    
        with TestServerHelper() as server_helper:
            with TestClientHelper() as client_helper:

                srv_transaction = ServerTransaction(server_helper.sock, db)
                test_client = SocketTransaction(client_helper.sock, b'\n')
                
                """Run the server transaction in a separate thread to allow client access"""
                thread = threading.Thread(target=srv_transaction.process)
                thread.start()

                """Check greeting from server"""
                rcv = test_client._read()
                self.assertEqual(rcv, Protocol.create_greeting_message(db.id).encode())
                
                """Check response to mdgid list req"""
                test_client._write(Protocol.create_message_id_list_request(tc).encode())
                rcv = test_client._read()
                self.assertEqual(rcv, Protocol.create_message_id_list(tc, None).encode())

                """Check response to mdg req"""
                test_client._write(Protocol.create_message_list_request([msg.id for msg in db.get_messages()]).encode())
                rcv = test_client._read()
                self.assertEqual(rcv, Protocol.create_message_list(db.get_messages()).encode())

                """Wait for server (will time out if no requests)"""
                thread.join(2*TIMEOUT)
                

if __name__ == '__main__':
    unittest.main()
