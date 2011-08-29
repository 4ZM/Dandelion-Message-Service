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
import configparser
import dandelion.identity
from dandelion.util import decode_b64_bytes, encode_b64_bytes

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
    _IP_DEFAULT = '0.0.0.0' # Bind to anything

    _DB_FILE_NAME = "db_file"
    _DB_FILE_DEFAULT = "dandelion.sqlite"

    def __init__(self):
        self._port = ServerConfig._PORT_DEFAULT
        self._ip = ServerConfig._IP_DEFAULT
        self._db_file = ServerConfig._DB_FILE_DEFAULT

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value

    @property
    def db_file(self):
        return self._db_file

    def load(self, confparser):
        if not confparser.has_section(ServerConfig._SECTION_NAME):
            confparser.add_section(ServerConfig._SECTION_NAME)

        # TODO for python 3.2; replace with fallback arg.
        if confparser.has_option(ServerConfig._SECTION_NAME, ServerConfig._PORT_NAME):
            self._port = confparser.getint(ServerConfig._SECTION_NAME, ServerConfig._PORT_NAME)

        if confparser.has_option(ServerConfig._SECTION_NAME, ServerConfig._IP_NAME):
            self._ip = confparser.get(ServerConfig._SECTION_NAME, ServerConfig._IP_NAME)

        if confparser.has_option(ServerConfig._SECTION_NAME, ServerConfig._DB_FILE_NAME):
            self._db_file = confparser.get(ServerConfig._SECTION_NAME, ServerConfig._DB_FILE_NAME)

    def store(self, confparser):
        confparser.add_section(ServerConfig._SECTION_NAME)
        confparser.set(ServerConfig._SECTION_NAME, ServerConfig._PORT_NAME, str(self._port))
        confparser.set(ServerConfig._SECTION_NAME, ServerConfig._IP_NAME, self._ip)
        confparser.set(ServerConfig._SECTION_NAME, ServerConfig._DB_FILE_NAME, self._db_file)


class SynchronizerConfig(Config):

    _SECTION_NAME = 'synchronizer'

    def __init__(self):
        pass

    def load(self, confparser):
        if not confparser.has_section(SynchronizerConfig._SECTION_NAME):
            raise ConfigException


    def store(self, confparser):
        confparser.add_section(SynchronizerConfig._SECTION_NAME)

class DiscovererConfig(Config):

    _SECTION_NAME = 'discoverer'

    def __init__(self):
        pass

    def load(self, confparser):
        if not confparser.has_section(DiscovererConfig._SECTION_NAME):
            raise ConfigException


    def store(self, confparser):
        confparser.add_section(DiscovererConfig._SECTION_NAME)

class UiConfig(Config):

    _SECTION_NAME = 'ui'

    # TODO button sizes etc.

    # master

    _BG_MASTER_NAME = 'bg_master'
    _BG_MASTER_DEFAULT = 'black'

    # frames

    _BG_FRAME_NAME = 'bg_frame'
    _BG_FRAME_DEFAULT = 'black'

    _BORDER_NAME = 'border'
    _BORDER_DEFAULT = '1'

    # welcome screen

    _WELCOME_SCREEN_NAME = 'welcome_screen'
    _WELCOME_SCREEN_DEFAULT = """  
  Welcome to the Dandelion Message System  
  --------------------------------------------------  
  Dandelion is robust, distributed message passing   
  designed to leverage the power of self organizing 
  networks. The message passing protocol can be     
  implemented on any transport layer but we will     
  start by implementing it utilizing Zeroconf       
  service discovery and ad hoc wifi networks with    
  link local addresses. Dandelion does not rely on   
  any existing infrastructure like the Internet or   
  mobile phone services - it is truly peer to peer. 
        """

    # button

    _BG_BUTTON_NAME = 'bg_button'
    _BG_BUTTON_DEFAULT = 'black'

    _FG_BUTTON_NAME = 'fg_button'
    _FG_BUTTON_DEFAULT = 'green'

    _ABG_BUTTON_NAME = 'abg_button'
    _ABG_BUTTON_DEFAULT = 'yellow'

    _HBG_BUTTON_NAME = 'hbg_button'
    _HBG_BUTTON_DEFAULT = 'yellow'

    # windows widgets

    _BG_WINDOW_NAME = 'bg_window'
    _BG_WINDOW_DEFAULT = 'black'

    _FG_WINDOW_NAME = 'fg_window'
    _FG_WINDOW_DEFAULT = 'green'

    # button alert 
    #fg_button_a = "red" # foreground color

    _FG_BUTTON_A_NAME = 'fg_button_a'
    _FG_BUTTON_A_DEFAULT = 'red'

    # Labels for buttons

    _LABEL_SEARCH_M_NAME = 'label_search_m'
    _LABEL_SEARCH_M_DEFAULT = 'Search'

    _LABEL_SHOW_M_NAME = 'label_show_m'
    _LABEL_SHOW_M_DEFAULT = 'Get messages'

    _LABEL_QUIT_NAME = 'label_quit'
    _LABEL_QUIT_DEFAULT = 'x'

    _LABEL_GET_ID_NAME = 'label_get_id'
    _LABEL_GET_ID_DEFAULT = 'Get ids'

    _LABEL_STOP_NAME = 'label_stop'
    _LABEL_STOP_DEFAULT = 'Stop'

    _LABEL_START_NAME = 'label_start'
    _LABEL_START_DEFAULT = 'Start'

    _LABEL_SEND_NAME = 'label_send'
    _LABEL_SEND_DEFAULT = 'Send'

    _LABEL_HELP_NAME = 'label_help'
    _LABEL_HELP_DEFAULT = '?'

    # Labels misc      

    _YOUR_M_TITLE_NAME = 'your_m_title'
    _YOUR_M_TITLE_DEFAULT = 'What on your mind?'

    _SIGN_NAME = 'sign'
    _SIGN_DEFAULT = 'Sign'

    _LABEL_NICKBOX_NAME = 'label_nickbox'
    _LABEL_NICKBOX_DEFAULT = 'Rename nick'

    _LABEL_SET_NEW_NICK_NAME = 'label_set_new_nick'
    _LABEL_SET_NEW_NICK_DEFAULT = 'Set new nick'

    _LABEL_SEARCHBOX_NAME = 'label_searchbox'
    _LABEL_SEARCHBOX_DEFAULT = 'Search'

    def __init__(self):
        self.uidict = {
            UiConfig._BG_MASTER_NAME : UiConfig._BG_MASTER_DEFAULT,
            UiConfig._BG_FRAME_NAME : UiConfig._BG_FRAME_DEFAULT,
            UiConfig._BORDER_NAME : UiConfig._BORDER_DEFAULT,
            UiConfig._WELCOME_SCREEN_NAME : UiConfig._WELCOME_SCREEN_DEFAULT,
            UiConfig._BG_BUTTON_NAME : UiConfig._BG_BUTTON_DEFAULT,
            UiConfig._FG_BUTTON_NAME : UiConfig._FG_BUTTON_DEFAULT,
            UiConfig._ABG_BUTTON_NAME : UiConfig._ABG_BUTTON_DEFAULT,
            UiConfig._HBG_BUTTON_NAME : UiConfig._HBG_BUTTON_DEFAULT,
            UiConfig._BG_WINDOW_NAME : UiConfig._BG_WINDOW_DEFAULT,
            UiConfig._FG_WINDOW_NAME : UiConfig._FG_WINDOW_DEFAULT,
            UiConfig._FG_BUTTON_A_NAME : UiConfig._FG_BUTTON_A_DEFAULT,
            UiConfig._LABEL_SEARCH_M_NAME : UiConfig._LABEL_SEARCH_M_DEFAULT,
            UiConfig._LABEL_SHOW_M_NAME : UiConfig._LABEL_SHOW_M_DEFAULT,
            UiConfig._LABEL_QUIT_NAME : UiConfig._LABEL_QUIT_DEFAULT,
            UiConfig._LABEL_GET_ID_NAME : UiConfig._LABEL_GET_ID_DEFAULT,
            UiConfig._LABEL_STOP_NAME : UiConfig._LABEL_STOP_DEFAULT,
            UiConfig._LABEL_START_NAME : UiConfig._LABEL_START_DEFAULT,
            UiConfig._LABEL_SEND_NAME : UiConfig._LABEL_SEND_DEFAULT,
            UiConfig._LABEL_HELP_NAME : UiConfig._LABEL_HELP_DEFAULT,
            UiConfig._YOUR_M_TITLE_NAME : UiConfig._YOUR_M_TITLE_DEFAULT,
            UiConfig._SIGN_NAME : UiConfig._SIGN_DEFAULT,
            UiConfig._LABEL_NICKBOX_NAME : UiConfig._LABEL_NICKBOX_DEFAULT,
            UiConfig._LABEL_SET_NEW_NICK_NAME : UiConfig._LABEL_SET_NEW_NICK_DEFAULT,
            UiConfig._LABEL_SEARCHBOX_NAME : UiConfig._LABEL_SEARCHBOX_DEFAULT}

    def __getitem__(self, key):
        return self.uidict[key]

    def __setitem__(self, key, value):
        self.uidict[key] = value

    def load(self, confparser):
        if not confparser.has_section(UiConfig._SECTION_NAME):
            #raise ConfigException
            confparser.add_section(UiConfig._SECTION_NAME)

        for key in confparser[UiConfig._SECTION_NAME]:
            if key in self.uidict:
                self.uidict[key] = confparser[UiConfig._SECTION_NAME][key]
            else:
                pass # TODO complain in a user friendly way

    def store(self, confparser):
        confparser.add_section(UiConfig._SECTION_NAME)

        for key in self.uidict:
            confparser.set(UiConfig._SECTION_NAME, key, self.uidict[key])

class IdentityConfig(Config):

    _SECTION_NAME = 'identity'

    _MY_ID_NAME = 'myid'
    _MY_ID_DEFAULT = None

    def __init__(self):
        self._my_id = IdentityConfig._MY_ID_DEFAULT

    @property
    def my_id(self):
        return self._my_id

    @my_id.setter
    def my_id(self, value):
        self._my_id = value

    def load(self, confparser):
        if not confparser.has_section(IdentityConfig._SECTION_NAME):
            confparser.add_section(IdentityConfig._SECTION_NAME)

        if confparser.has_option(IdentityConfig._SECTION_NAME, IdentityConfig._MY_ID_NAME):
            self._my_id = confparser.get(IdentityConfig._SECTION_NAME, IdentityConfig._MY_ID_NAME)

    def store(self, confparser):
        confparser.add_section(IdentityConfig._SECTION_NAME)
        confparser.set(IdentityConfig._SECTION_NAME, IdentityConfig._MY_ID_NAME, self._my_id)

class ConfigManager:

    def __init__(self, config_file='dandelion.conf'):
        self._cfg_file_name = config_file
        self._server_config = ServerConfig()
        self._synchronizer_config = SynchronizerConfig()
        self._discoverer_config = DiscovererConfig()
        self._id_manager_config = IdentityConfig()
        self._ui_config = UiConfig()

        self.read_file()

        self._content_db = ContentDB(self._server_config.db_file)
        key = b'a secret key'

        if self._id_manager_config.my_id is not None and not self._content_db.contains_identity(decode_b64_bytes(self._id_manager_config.my_id.encode())) :
            print("WARNING! Bad or non existing ID requested in config. Requested:", self._id_manager_config.my_id)
            self._id_manager_config.my_id = None

        if self._id_manager_config.my_id is not None:
            fp = decode_b64_bytes(self._id_manager_config.my_id.encode())
            try:
                self._identity = self._content_db.get_private_identity(fp, key)
                print("My claimed ID:", self._id_manager_config.my_id)
                return
            except ValueError:
                pass
            
        self._identity = dandelion.identity.generate()
        self._content_db.add_private_identity(self._identity, key)
        id_str = encode_b64_bytes(self._identity.fingerprint).decode()
        self._id_manager_config.my_id = id_str

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
    def discoverer_config(self):
        return self._discoverer_config

    @property
    def identity_manager_config(self):
        return self._id_manager_config

    @property
    def ui_config(self):
        return self._ui_config

    @property
    def content_db(self):
        return self._content_db

    @property
    def identity(self):
        return self._identity

    def write_file(self):

        confparser = configparser.ConfigParser()

        self._server_config.store(confparser)
        self._ui_config.store(confparser)
        self._id_manager_config.store(confparser)

        with open(self._cfg_file_name, 'w') as configfile:
            confparser.write(configfile)

    def read_file(self):

        confparser = configparser.ConfigParser()
        confparser.read(self._cfg_file_name)

        self._server_config.load(confparser)
        self._ui_config.load(confparser)
        self._id_manager_config.load(confparser)

