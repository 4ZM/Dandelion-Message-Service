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

import configparser
from database import ContentDB

class ConfigException(Exception):
    pass

class ConfigManager:
    
    _SERVER_CONFIG_DEFAULTS = { 'local_address': '127.0.0.1', 'listen_port': '1337', 'max_connections': '5' }
    _SYNCHRONIZER_CONFIG_DEFAULTS = { 'max_connections': '10' }
    _UI_CONFIG_DEFAULTS = { }
    _ID_MANAGER_CONFIG_DEFAULTS = { }
    
    def __init__(self, config_file=None):
        
        self._server_config = self._SERVER_CONFIG_DEFAULTS.copy()
        self._synchronizer_config = self._SYNCHRONIZER_CONFIG_DEFAULTS.copy() 
        self._ui_config = self._UI_CONFIG_DEFAULTS.copy()
        self._id_manager_config = self._ID_MANAGER_CONFIG_DEFAULTS.copy()
        
        self._content_db = ContentDB()

        if config_file is None:
            self._cfg_file_name = 'data.conf'
        else:
            self._cfg_file_name = config_file
        
        self.read_cfg_file()
    
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
    
    def write_cfg_file(self):

        cfg_file_mgr = configparser.ConfigParser()

        self._store_config(cfg_file_mgr, 'server', self._server_config)
        self._store_config(cfg_file_mgr, 'synchronizer', self._synchronizer_config)
        self._store_config(cfg_file_mgr, 'ui', self._ui_config)
        self._store_config(cfg_file_mgr, 'identity_mgr', self._id_manager_config)        

        with open(self._cfg_file_name, 'w') as configfile:
            cfg_file_mgr.write(configfile)

    def _store_config(self, cfg_file_mgr, config_name, config_db):
        cfg_file_mgr.add_section(config_name)
        
        for k,v in config_db.items():
            cfg_file_mgr.set(config_name, k, v)

    
    def read_cfg_file(self):
        
        cfg_file_mgr = configparser.ConfigParser()
        cfg_file_mgr.read(self._cfg_file_name)
        
        self._load_config(cfg_file_mgr, 'server', self._server_config, ConfigManager._SERVER_CONFIG_DEFAULTS)
        self._load_config(cfg_file_mgr, 'synchronizer', self._synchronizer_config, ConfigManager._SYNCHRONIZER_CONFIG_DEFAULTS)
        self._load_config(cfg_file_mgr, 'ui', self._ui_config, ConfigManager._UI_CONFIG_DEFAULTS)
        self._load_config(cfg_file_mgr, 'identity_mgr', self._id_manager_config, ConfigManager._ID_MANAGER_CONFIG_DEFAULTS)

    def _load_config(self, cfg_file_mgr, config_name, config_db, defaults):
        
        if not cfg_file_mgr.has_section(config_name):
            return
        
        for key in cfg_file_mgr.options(config_name):
            if key not in defaults: # Can't have key that the program isn't expecting
                raise ConfigException
    
            config_db[key] = cfg_file_mgr.get(config_name, key)


        

if __name__ == '__main__':

    cm = ConfigManager()
    print(''.join(['SERVER: ', str(cm.server_config)]))
    print(''.join(['SYNCHRONIZER: ', str(cm.synchronizer_config)]))
    print(''.join(['UI: ', str(cm.ui_config)]))
    print(''.join(['ID: ', str(cm.identity_manager_config)]))
    #cm.write_cfg_file()
    