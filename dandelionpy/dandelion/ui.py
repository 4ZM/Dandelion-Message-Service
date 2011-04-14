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

from dandelion.identity import PrivateIdentity
from dandelion.message import Message
from dandelion.util import encode_b64_bytes
import cmd
import dandelion

class CmdLine(cmd.Cmd):
    """Simple command processor example."""

    prompt = '$ '
    intro = 'Dandelion Messaging Interface v0.1'
    doc_header = 'Commands (type help <command>):'

    def __init__(self, ui):
        super().__init__()
        self._ui = ui

    def emptyline(self):
        pass

    def postcmd(self, stop, line):
        print('')
        return stop

    def do_say(self, args):
        """say message : Create a new message"""
        self._ui.say(args)

    def do_isay(self, args):
        """say message : Create a new signed message"""
        self._ui.say(args, sign=True)

    def do_sayto(self, args):
        """sayto receiver message : Create a new addressed message"""
        self._ui.say(args, receiver_name='RECV')

    def do_isayto(self, args):
        """isayto receiver message : Create a new signed and addressed message"""
        self._ui.say(args, sign=True, receiver_name='RECV')

    def do_msgs(self, args):
        """msgs : Show messages"""
        self._ui.show_messages()

    def do_identities(self, args):
        """identities : Show identities"""
        self._ui.show_identities()

    def do_server(self, args):
        """server [op] : Perform a server operation [start|stop|restart|stat]"""
        args = args.split(' ')
        if args[0] == 'bind' and len(args) == 3:
            try:
                self._ui.listen_to(args[1], int(args[2]))
            except:
                print("Server Bind Config Error")
            return

        try:
            self._ui.server_ctrl(self._parse_service_op(args[0]))
        except:
            print("SYNTAX ERROR")
    
    def do_synchronizer(self, args):
        """synchronizer [op] : Perform a synchronizer operation [start|stop|restart|stat]"""
        args = args.split(' ')
        if args[0] == 'sync' and len(args) == 3:
            try:
                self._ui.singel_sync(args[1], int(args[2]))
            except:
                print("Sync Error")
            return
        
        try:
            self._ui.synchronizer_ctrl(self._parse_service_op(args[0]))
        except:
            print("SYNTAX ERROR")

    def do_exit(self, args):
        """exit : Exit the program"""
        return True

    def _parse_service_op(self, op_str):
        if op_str == 'start':
            return OP_START
        elif op_str == 'stop':
            return OP_STOP
        elif op_str == 'restart':
            return OP_RESTART
        elif op_str == 'status' or op_str == 'stat' or op_str == '':
            return OP_STATUS
        else:
            raise Exception

OP_START, OP_STOP, OP_RESTART, OP_STATUS = range(4)
        
class UI:
    
    def __init__(self, config_manager, db, id, server=None, content_synchronizer=None):
        self._server = server
        self._synchronizer = content_synchronizer
        self._config_manager = config_manager
        self._db = db
        self._identity = id
        #self._id_manager = IdentityManager(self._config_manager.identity_manager_config)

        self._cmd_line = CmdLine(self)


    def run(self):
        self._cmd_line.cmdloop()

    def say(self, msg, sign=None, receiver_name=None):
        
        if receiver_name:
            receiver_ = PrivateIdentity.generate() # Should look up id of receiver
        else:
            receiver_ = None
        
        if sign and receiver_:
            m = dandelion.message.create(msg, sender=self._identity, receiver=receiver_)
            self._db.add_messages([m])
        elif sign:
            m = dandelion.message.create(msg, sender=self._identity)
            self._db.add_messages([m])
        elif receiver_:
            m = dandelion.message.create(msg, receiver=receiver_)
            self._db.add_messages([m])
        else:
            m = dandelion.message.create(msg)
            self._db.add_messages([m])

    def show_messages(self):
        msgs = self._db.get_messages()
        print(' --- MESSAGES BEGIN --- ')
        
        for m in msgs:
            print(' : '.join([encode_b64_bytes(m.id).decode(), 
                              m.text if not m.has_receiver else encode_b64_bytes(m.text).decode(), 
                              'N/A' if not m.has_receiver else encode_b64_bytes(m.receiver).decode(), 
                              'N/A' if not m.has_sender else encode_b64_bytes(m.sender).decode()]))

        print(' --- MESSAGES END --- ')

    def show_identities(self):
        identities = self._db.get_identities()
        print(' --- IDENTITIES BEGIN --- ')
        
        for id in identities:
            print(' : '.join([encode_b64_bytes(id.fingerprint).decode()]))

        print(' --- IDENTITIES END --- ')

    def server_ctrl(self, op=OP_STATUS):
        self._service_ctrl(self._server, op)
    
    def listen_to(self, host, port):
        self._server.ip = host
        self._server.port = port
    
    def singel_sync(self, host, port):
        self._synchronizer.sync(host, port)
    
    def synchronizer_ctrl(self, op=OP_STATUS):
        self._service_ctrl(self._synchronizer, op)
    
    def _service_ctrl(self, service, op):
        if op == OP_START:
            service.start()
        elif op == OP_STOP:
            service.stop()
        elif op == OP_RESTART:
            service.restart()
        elif op == OP_STATUS:
            print(service.status)
        else:
            pass # Error

