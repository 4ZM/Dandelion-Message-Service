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

from config import ConfigManager 
from configuration import ConfigurationManager
from network import Server
from synchronizer import Synchronizer
from ui import UI

class DandelionApp:

    def __init__(self, config_file=None):
        self._config_manager = ConfigurationManager(config_file)
    
    def start_server(self): 
        self._server = Server(self._config_manager.local_address, 
                              self._config_manager.local_port, 
                              self._config_manager.content_db) 
        self._server.start()
    
    def start_content_synchronizer(self): 
        self._synchronizer = Synchronizer(self._config_manager.local_address,
                                          self._config_manager.local_port,
                                          self._config_manager.type,
                                          self._config_manager.content_db)
        self._synchronizer.start()
    
    def run_ui(self): 
        
        self._ui = UI(self._config_manager.ui,  #dict 
                      self._config_manager.content_db,
                      self._server, 
                      self._synchronizer)
        self._ui.run()
    
    def exit(self):
        self._synchronizer.stop()
        self._server.stop()


if __name__ == '__main__':
    
    app = DandelionApp('dandelion.conf')
    print('APP: Starting Server')
    app.start_server()
    print('APP: Starting Synchronizer')
    app.start_content_synchronizer()
    print('APP: Starting UI')
    app.run_ui()
    print('APP: Exiting')
    app.exit()