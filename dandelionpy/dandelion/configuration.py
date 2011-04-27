"""
Copyright (c) 2011 Mathias Tervo <mathias.tervo@gmail.com>

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

import io
import configparser
from dandelion.database import ContentDB
import dandelion

class ConfigurationManager():
   
    CONFIG_DEFAULTS = {
                       'server' : {'local_address' : '127.0.0.1', 
                                   'local_port' : 1337,
                                   'mdns_group' : '239.255.255.250',
                                   'type' : '_http._tcp.local.',
                                   'service_name' : 'dandelion_service',
                                   'max_connections' : 5,
                                   'description' : 'DandelionMessagingSystem'
                                   },
                        
                       'synchronization' : {'server_time' : 0},
                       
                       'ui' : {},
                       }
    
    DEFAULT_CONFIG_FILE = '../dandelion.cfg'
    
    def __init__(self, config_file=None):
        
        self._cfg = self.CONFIG_DEFAULTS.copy()
        
        if not config_file:
            self._config_file = self.DEFAULT_CONFIG_FILE
        else:
            self._config_file = config_file
        
        if not self._config_file_exists():
            self.write_defaults_to_config_file()
            
        self.load_config() 
        
        self._content_db = dandelion.database.SQLiteContentDB("msgs.db")
        
        self._identity = dandelion.identity.generate()
        
        # store all dict values as attributes so we can access the like this
        # self.server_time (the same as self_cfg['synchronization']['server_time']
        # one downfall is that we cant have settings with the same name even though they are
        # in different sections. 
        for key in self._cfg:
            setattr(self, key, self._cfg[key])
            for k, v in self._cfg[key].items():
                setattr(self.__class__, k, v)

        

    def _config_file_exists(self):
        try:
            open(self._config_file, "r")
            print("File exists")
            return True
        except IOError:
            return False
    
    
    def write_defaults_to_config_file(self):

        config = configparser.ConfigParser()
        
        for section_name, optdict in self.CONFIG_DEFAULTS.items():
            config.add_section(section_name)
            for option, value in optdict.items():
                config.set(section_name, str(option), str(value))
                
            with open(self._config_file, 'w') as configfile:
                config.write(configfile)


    def load_config(self):
        """ This allows us to access the config like:
                    self._cfg['server']['local_address']
        """
        config = configparser.ConfigParser()
        config.read(io.StringIO(self._config_file))
        
        for section_name, optdict in self.CONFIG_DEFAULTS.items():
            if config.has_section(section_name):
                for option, default_value in optdict.items():

                    conf_value = config.get(section_name, option)
                    if conf_value != default_value:
                
                        self._cfg[section_name][option] = conf_value

    @property
    def content_db(self):
        return self._content_db
    

    @property 
    def identity(self):
        return self._identity
    
    
"""
    entry point

"""

class MydelionApp():
    def __init__(self, config_file=None):
        cm = ConfigurationManager(config_file)
        #print("server info", cm.server_info.mdns_group)
        print("cm.server", cm.server)
        print("sync info", cm.server_time)
        cm.server_time = 2
        
        
if __name__ == "__main__":
    
    print("Starting application")
    app = MydelionApp()