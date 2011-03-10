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

import cmd
from message import Message

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
        self._ui.say(args, sender=True)

    def do_sayto(self, args):
        """sayto receiver message : Create a new addressed message"""
        self._ui.say(args, receiver='RECV')

    def do_isayto(self, args):
        """isayto receiver message : Create a new signed and addressed message"""
        self._ui.say(args, sender=True, receiver='RECV')
        

    def do_stat(self, args):
        """stat : Show current status of this client"""

    def do_msgs(self, args):
        """msgs : Show messages"""
        self._ui.show_messages()

    def do_server(self, args):
        """server [op] : Perform a server operation [start|stop|restart|stat]"""
        self._ui.server_ctrl(self._parse_service_op(args))
    
    def do_synchronizer(self, args):
        """synchronizer [op] : Perform a synchronizer operation [start|stop|restart|stat]"""
        self._ui.synchronizer_ctrl(self._parse_service_op(args))

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
        elif op_str == 'status':
            return OP_STATUS
        else:
            raise Exception

OP_START, OP_STOP, OP_RESTART, OP_STATUS = range(4)
        
class UI:
    
    def __init__(self, config_manager, server=None, content_synchronizer=None):
        self._server = server
        self._synchronizer = content_synchronizer
        self._config_manager = config_manager
        self._db = config_manager.content_db
        #self._id_manager = IdentityManager(self._config_manager.identity_manager_config)

        self._cmd_line = CmdLine(self)


    def run(self):
        print('UI: Starting cmd line')
        self._cmd_line.cmdloop()
        print('UI: Exiting cmd line')

    def say(self, msg, sender=None, receiver=None):
        
        if sender and receiver:
            print(''.join(['SAY: ', msg, ' (Sign: YES) (Receiver: ', receiver, ')']))
        elif sender:
            print(''.join(['SAY: ', msg, ' (Sign: YES) (Receiver: N/A)']))
        elif receiver:
            print(''.join(['SAY: ', msg, ' (Sign: N/A) (Receiver: ', receiver, ')']))
        else:
            print(''.join(['SAY: ', msg, ' (Sign: N/A) (Receiver: N/A)']))
            m = Message(msg)
            self._db.add_messages([m])

    def show_messages(self):
        msgs = self._db.get_messages()
        print(' --- MESSAGES BEGIN --- ')
        
        for m in msgs:
            print(' : '.join([m.text, str(m.id)]))

        print(' --- MESSAGES END --- ')

    def server_ctrl(self, op=OP_STATUS):
        self._service_ctrl(self._server, op)
    
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
    

if __name__ == '__main__':
    
    UI(None).run()
    


