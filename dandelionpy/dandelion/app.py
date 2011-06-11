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

from dandelion.config import ConfigManager 
from dandelion.network import Server
from dandelion.synchronizer import Synchronizer
from dandelion.discoverer import Discoverer
from dandelion.ui import UI
from dandelion.gui.gui import GUI

class DandelionApp:

    def __init__(self, config_file=None):
        self._config_manager = ConfigManager(config_file)
    
        self._server = Server(self._config_manager.server_config, 
                              self._config_manager.content_db,
                              self._config_manager.identity) 
        
        self._discoverer = Discoverer(self._config_manager.discoverer_config)
        
        self._synchronizer = Synchronizer(self._discoverer,
                                          self._config_manager.synchronizer_config,
                                          self._config_manager.content_db)

    def run_ui(self): 
        
        self._ui = UI(self._config_manager.ui_config, 
                      self._config_manager.content_db,
                      self._config_manager.identity,
                      self._server, 
                      self._discoverer,
                      self._synchronizer)
        
        self._ui.run()
    
    def run_gui(self):

        self._gui = GUI(self._config_manager.ui_config, 
                        self._config_manager.content_db,
                        self._config_manager.identity,
                        self._server, 
                        self._synchronizer)
        
    def exit(self):
        self._synchronizer.stop()
        self._discoverer.stop()
        self._server.stop()
        self._config_manager.write_file()

def run():
    app = DandelionApp('dandelion.conf')

    app._server.start()
    app._discoverer.start()
    app._synchronizer.start()
    app.run_gui()

    app.exit()

if __name__ == '__main__':
    run()
