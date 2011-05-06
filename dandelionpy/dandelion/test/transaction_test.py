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

from dandelion.database import ContentDB
from dandelion.message import Message
from dandelion.network import SocketTransaction, ServerTransaction, \
    ClientTransaction
import dandelion.protocol
import socket
import tempfile
import threading
import unittest
from dandelion.identity import PrivateIdentity


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
        self._sock.shutdown(socket.SHUT_RDWR)
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
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()
        
    def _wait_for_connection(self):
        self._client_sock, _ = self._sock.accept()
        self._client_sock.settimeout(TIMEOUT)
        
        
def recv_n(sock, nbytes):
    return b''.join([sock.recv(1) for _ in range(nbytes)])


class TransactionTest(unittest.TestCase):
    """Unit test suite for the DMS network transactions"""
     
    def test_helper_classes(self):
        """This test case tests the helper server and client classes used in the other test cases.""" 
    
        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:

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
    
        with TestServerHelper() as server_helper, TestClientHelper() as _:
            
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
    
        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
                
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
    
        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
                
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

    def test_basic_server_transaction(self):
        """Tests the server transaction protocol and logic""" 
    
        db = ContentDB(tempfile.NamedTemporaryFile().name)
        db.add_identities([dandelion.identity.generate(), dandelion.identity.generate()])
        tc = db.add_messages([Message('fubar'), Message('foo'), Message('bar')])
    
        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
            srv_transaction = ServerTransaction(server_helper.sock, db)
            test_client = SocketTransaction(client_helper.sock, b'\n')
            
            """Run the server transaction in a separate thread to allow client access"""
            thread = threading.Thread(target=srv_transaction.process)
            thread.start()

            """Check greeting from server"""
            rcv = test_client._read()
            self.assertEqual(rcv, dandelion.protocol.create_greeting_message(db.id).encode())
            
            """Check response to mdgid list req"""
            test_client._write(dandelion.protocol.create_message_id_list_request(tc).encode())
            rcv = test_client._read()
            self.assertEqual(rcv, dandelion.protocol.create_message_id_list(tc, None).encode())

            """Check response to identityid list req"""
            test_client._write(dandelion.protocol.create_identity_id_list_request(tc).encode())
            rcv = test_client._read()
            self.assertEqual(rcv, dandelion.protocol.create_identity_id_list(tc, None).encode())

            """Check response to mdg req"""
            test_client._write(dandelion.protocol.create_message_list_request([msg.id for msg in db.get_messages()[1]]).encode())
            rcv = test_client._read()
            self.assertEqual(rcv, dandelion.protocol.create_message_list(db.get_messages()[1]).encode())

            """Check response to identity req"""
            test_client._write(dandelion.protocol.create_identity_list_request([id.fingerprint for id in db.get_identities()[1]]).encode())
            rcv = test_client._read()
            self.assertEqual(rcv, dandelion.protocol.create_identity_list(db.get_identities()[1]).encode())

            """Wait for server (will time out if no requests)"""
            thread.join(2*TIMEOUT)

    def test_basic_client_transaction(self):
        """Tests the client transaction protocol and logic""" 

        client_db = ContentDB(tempfile.NamedTemporaryFile().name)
        srv_db = ContentDB(tempfile.NamedTemporaryFile().name)

        self.assertEqual(client_db.message_count, 0)
        srv_db.add_identities([dandelion.identity.generate(), dandelion.identity.generate()])
        tc = srv_db.add_messages([Message('fubar'), Message('foo'), Message('bar')])

        self.assertEqual(client_db.message_count, 0)
        self.assertEqual(client_db.identity_count, 0)
        self.assertEqual(srv_db.message_count, 3)
        self.assertEqual(srv_db.identity_count, 2)
    
        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
            
            client_transaction = ClientTransaction(client_helper.sock, client_db)
            srv_sock = SocketTransaction(server_helper.sock, b'\n')
            
            """Run the client transaction in a separate thread"""
            thread = threading.Thread(target=client_transaction.process)
            thread.start()
            
            """Send a greeting (should be req. by client)"""
            srv_sock._write(dandelion.protocol.create_greeting_message(srv_db.id).encode())
            
            """Reading msg id list request"""
            rcv = srv_sock._read()
            self.assertEqual(rcv, dandelion.protocol.create_message_id_list_request().encode())

            """Sending the msg id list"""
            srv_sock._write(dandelion.protocol.create_message_id_list(tc, srv_db.get_messages()[1]).encode())

            """Reading msg list request"""
            rcv = srv_sock._read()
            self.assertEqual(rcv, dandelion.protocol.create_message_list_request([msg.id for msg in srv_db.get_messages()[1]]).encode())

            """Sending the msg id list"""
            srv_sock._write(dandelion.protocol.create_message_list(srv_db.get_messages()[1]).encode())


            """Reading identity id list request"""
            rcv = srv_sock._read()
            self.assertEqual(rcv, dandelion.protocol.create_identity_id_list_request().encode())

            """Sending the identity id list"""
            srv_sock._write(dandelion.protocol.create_identity_id_list(tc, srv_db.get_identities()[1]).encode())

            """Reading identity list request"""
            rcv = srv_sock._read()
            self.assertEqual(rcv, dandelion.protocol.create_identity_list_request([id.fingerprint for id in srv_db.get_identities()[1]]).encode())

            """Sending the msg id list"""
            srv_sock._write(dandelion.protocol.create_identity_list(srv_db.get_identities()[1]).encode())
            
            """Wait for client to hang up"""
            thread.join(2*TIMEOUT)
                
        """Make sure the client has updated the db"""
        self.assertEqual(client_db.message_count, 3)
        self.assertEqual(srv_db.message_count, 3)
        self.assertEqual(len([srvmsg for srvmsg in srv_db.get_messages()[1] if srvmsg not in client_db.get_messages()[1]]), 0) 

    def test_server_transaction_protocol_violation(self):
        """Tests the servers response to an invalid request""" 
    
        db = ContentDB(tempfile.NamedTemporaryFile().name)

        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
            srv_transaction = ServerTransaction(server_helper.sock, db)
            test_client = SocketTransaction(client_helper.sock, b'\n')
            
            """Run the server transaction in a separate thread to allow client access"""
            thread = threading.Thread(target=srv_transaction.process)
            thread.start()

            """Check greeting from server"""
            rcv = test_client._read()
            self.assertEqual(rcv, dandelion.protocol.create_greeting_message(db.id).encode())
            
            """Check response to mdgid list req"""
            test_client._write(b'NON PROTOCOL MESSAGE\n')
            self.assertRaises(socket.timeout, test_client._read)

            """Wait for server (will time out if no requests)"""
            thread.join(2*TIMEOUT)
            server_helper, client_helper = None, None

        
    def test_client_transaction_protocol_violation(self):
        """Tests the client transaction protocol and logic""" 
        
        client_db = ContentDB(tempfile.NamedTemporaryFile().name)
   
        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
            
            client_transaction = ClientTransaction(client_helper.sock, client_db)
            srv_sock = SocketTransaction(server_helper.sock, b'\n')
            
            """Run the client transaction in a separate thread"""
            thread = threading.Thread(target=client_transaction.process)
            thread.start()
            
            """Send a greeting (should be req. by client)"""
            srv_sock._write(b'NON PROTOCOL MESSAGE\n')
            self.assertRaises(socket.timeout, srv_sock._read)

            """Wait for client to hang up"""
            thread.join(2*TIMEOUT)

    def test_client_server_transaction(self):
        """Tests the whole, client driven transaction protocol and logic""" 
        
        client_db = ContentDB(tempfile.NamedTemporaryFile().name)
        server_db = ContentDB(tempfile.NamedTemporaryFile().name)
        
        id1 = dandelion.identity.generate()
        id2 = dandelion.identity.generate()
        server_db.add_identities([id1, id2])
        server_db.add_messages([Message('fubar'), dandelion.message.create('foo', id1, id2), Message('bar')])
    
        self.assertEqual(client_db.message_count, 0)
        self.assertEqual(client_db.identity_count, 0)
        self.assertEqual(server_db.message_count, 3)
        self.assertEqual(server_db.identity_count, 2)

        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
                
            client_transaction = ClientTransaction(client_helper.sock, client_db)
            server_transaction = ServerTransaction(server_helper.sock, server_db)
            
            """Run the client transactions asynchronously"""
            server_thread = threading.Thread(target=server_transaction.process)
            client_thread = threading.Thread(target=client_transaction.process)
            server_thread.start()
            client_thread.start()
            
            """Wait for client to hang up"""
            client_thread.join(1) # One sec should be plenty
            server_thread.join(2*TIMEOUT)
            
        """Make sure the client has updated the db"""
        self.assertEqual(client_db.message_count, 3)
        self.assertEqual(server_db.message_count, 3)
        self.assertEqual(client_db.identity_count, 2)
        self.assertEqual(server_db.identity_count, 2)

        self.assertEqual(len([srvmsg for srvmsg in server_db.get_messages()[1] if srvmsg not in client_db.get_messages()[1]]), 0) 
        self.assertEqual(len([srvid for srvid in server_db.get_identities()[1] if srvid not in client_db.get_identities()[1]]), 0)

    def test_client_server_transaction_empty_db(self):
        """Tests the whole, client driven transaction protocol and logic with an empty db""" 
        
        client_db = ContentDB(tempfile.NamedTemporaryFile().name)
        server_db = ContentDB(tempfile.NamedTemporaryFile().name)
    
        self.assertEqual(client_db.message_count, 0)
        self.assertEqual(server_db.message_count, 0)
        self.assertEqual(client_db.identity_count, 0)
        self.assertEqual(server_db.identity_count, 0)
    
        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
                
            client_transaction = ClientTransaction(client_helper.sock, client_db)
            server_transaction = ServerTransaction(server_helper.sock, server_db)
            
            """Run the client transactions asynchronously"""
            server_thread = threading.Thread(target=server_transaction.process)
            client_thread = threading.Thread(target=client_transaction.process)
            server_thread.start()
            client_thread.start()
            
            """Wait for client to hang up"""
            client_thread.join(1) # One sec should be plenty
            server_thread.join(2*TIMEOUT)
            
        """Make sure the db hasn't changed"""
        self.assertEqual(client_db.message_count, 0)
        self.assertEqual(server_db.message_count, 0)
        self.assertEqual(client_db.identity_count, 0)
        self.assertEqual(server_db.identity_count, 0)
        
    def test_client_server_transaction_partial_sync(self):
        """Tests the whole, client driven transaction protocol and logic""" 
        
        client_db = ContentDB(tempfile.NamedTemporaryFile().name)
        server_db = ContentDB(tempfile.NamedTemporaryFile().name)
        
        id1 = dandelion.identity.generate()
        id2 = dandelion.identity.generate()
        
        client_db.add_identities([id1])
        server_db.add_identities([id1, id2])
        client_db.add_messages([Message('fubar')])
        server_db.add_messages([Message('fubar'), Message('foo'), Message('bar')])
    
        self.assertEqual(client_db.identity_count, 1)
        self.assertEqual(server_db.identity_count, 2)
        self.assertEqual(client_db.message_count, 1)
        self.assertEqual(server_db.message_count, 3)
    
        with TestServerHelper() as server_helper, TestClientHelper() as client_helper:
                
            client_transaction = ClientTransaction(client_helper.sock, client_db)
            server_transaction = ServerTransaction(server_helper.sock, server_db)
            
            """Run the client transactions asynchronously"""
            server_thread = threading.Thread(target=server_transaction.process)
            client_thread = threading.Thread(target=client_transaction.process)
            server_thread.start()
            client_thread.start()
            
            """Wait for client to hang up"""
            client_thread.join(1) # One sec should be plenty
            server_thread.join(2*TIMEOUT)
            
        """Make sure the client has updated the db"""
        self.assertEqual(client_db.identity_count, 2)
        self.assertEqual(server_db.identity_count, 2)
        self.assertEqual(client_db.message_count, 3)
        self.assertEqual(server_db.message_count, 3)
        self.assertEqual(len([srvmsg for srvmsg in server_db.get_messages()[1] if srvmsg not in client_db.get_messages()[1]]), 0) 
        self.assertEqual(len([srvids for srvids in server_db.get_identities()[1] if srvids not in client_db.get_identities()[1]]), 0)


if __name__ == '__main__':
    unittest.main()
