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

import socket
import configparser
from dandelion.database import ContentDB

class ConfigException(Exception):
    pass

class Config:
    def load(self, confparser):
        pass
    def store(self, confparser):
        pass

class ServerConfig(Config):
    
    _SECTION_NAME = 'server'
    
    _PORT_NAME = 'port'
    _PORT_DEFAULT = 1337
    
    _IP_NAME = 'ip'
    #_IP_DEFAULT = '127.0.0.1'
    _IP_DEFAULT = socket.gethostbyname( socket.gethostname() )
    
    _TYPE_DEFAULT = '_http._tcp.local.'
    
    def __init__(self):
        self._port = ServerConfig._PORT_DEFAULT
        self._ip = ServerConfig._IP_DEFAULT
        self._type = ServerConfig._TYPE_DEFAULT
    
    @property 
    def type(self):
        return self._type
    
    @property
    def port(self):
        return self._port
        
    @property
    def ip(self):
        return self._ip
        
    def load(self, confparser):
        if not confparser.has_section(ServerConfig._SECTION_NAME):
            confparser.add_section(ServerConfig._SECTION_NAME)
        
        # TODO for python 3.2; replace with fallback arg.
        if confparser.has_option(ServerConfig._SECTION_NAME, ServerConfig._PORT_NAME):
            self._port = confparser.getint(ServerConfig._SECTION_NAME, ServerConfig._PORT_NAME)
        else:
            self._port = ServerConfig._PORT_DEFAULT
        
        if confparser.has_option(ServerConfig._SECTION_NAME, ServerConfig._IP_NAME):
            self._ip = confparser.get(ServerConfig._SECTION_NAME, ServerConfig._IP_NAME)
        else: 
            self._ip = ServerConfig._IP_DEFAULT

    def store(self, confparser):
        confparser.add_section(ServerConfig._SECTION_NAME)
        confparser.set(ServerConfig._SECTION_NAME, ServerConfig._PORT_NAME, self._port)
        confparser.set(ServerConfig._SECTION_NAME, ServerConfig._IP_NAME, self._ip)


class SynchronizerConfig(Config):
    
    _SECTION_NAME = 'synchronizer'
        
    def __init__(self):
        pass
        
    def load(self, confparser):
        if not confparser.has_section(ServerConfig._SECTION_NAME):
            raise ConfigException
        

    def store(self, confparser):
        confparser.add_section(ServerConfig._SECTION_NAME)


class UiConfig(Config):
    
    _SECTION_NAME = 'ui'
        
    def __init__(self):
        pass
        
    def load(self, confparser):
        if not confparser.has_section(ServerConfig._SECTION_NAME):
            raise ConfigException
        

    def store(self, confparser):
        confparser.add_section(ServerConfig._SECTION_NAME)

class IdentityConfig(Config):
    
    _SECTION_NAME = 'synchronizer'
        
    def __init__(self):
        pass
        
    def load(self, confparser):
        if not confparser.has_section(ServerConfig._SECTION_NAME):
            raise ConfigException
        

    def store(self, confparser):
        confparser.add_section(ServerConfig._SECTION_NAME)


class ConfigManager:

    def __init__(self, config_file=None):

        if config_file is None:
            self._cfg_file_name = 'dandelion.conf'
        else:
            self._cfg_file_name = config_file
        
        self._server_config = ServerConfig()
        self._synchronizer_config = SynchronizerConfig()
        self._id_manager_config = IdentityConfig()
        self._ui_config = UiConfig()
        
        self.read_file()
        
        self._content_db = ContentDB()

    @property
    def config_file(self):
        return self._cfg_file_name

    @property
    def server_config(self):
        return self._server_config
    
    @property
    def synchronizer_config(self):
        return self._synchronizer_config
    
    @property
    def identity_manager_config(self):
        return self._id_manager_config
    
    @property
    def ui_config(self):
        return self._ui_config
    
    @property 
    def content_db(self):
        return self._content_db
    
    def write_file(self):

        confparser = configparser.ConfigParser()
        
        self._server_config.store(confparser)
        
        with open(self._cfg_file_name, 'w') as configfile:
            confparser.write(configfile)
    
    def read_file(self):
        
        confparser = configparser.ConfigParser()
        confparser.read(self._cfg_file_name)
        
        self._server_config.load(confparser)
