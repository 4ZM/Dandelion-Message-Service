"""
Copyright (c) 2011 Anders Sundman <anders@4zm.org>

This file is part of pydms

pydms is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pydms is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pydms.  If not, see <http://www.gnu.org/licenses/>.
"""

import binascii
import re
from dandelion.message import Message

class ProtocolParseError(Exception):
    pass

class ProtocolVersionError(Exception):
    pass

class Protocol:
    """The DMS protocol.
    
    This class encapsulates and represents the Dandelion Message Service 
    communication protocol. 
    
    It handles formating the messages, but not populating them with 
    meaningful data. Like the protocol it is state-less (hence the 
    classmethods). 
    
    """
    
    PROTOCOL_VERSION = '1.0'
    
    _PROTOCOL_COOKIE = 'DMS'
    _FIELD_SEPARATOR = ';'
    _SUB_FIELD_SEPARATOR = '|'
    
    _GETMESSAGELIST = 'GETMESSAGELIST'
    
    @classmethod
    def create_greeting_message(cls, dbid):
        """Create the server greeting message string.
        
        This message is sent from the server to the client upon connection. 
        The dbid (bytes) represents a data base id. 
        
        [C]                                                    [S]
         |                                                      | 
         |     <protocol cookie>;<protocol version>;<db id>     | 
         |<-----------------------------------------------------| 
         |                                                      | 
          
        """
        
        if not dbid:
            raise ValueError
        
        if not isinstance(dbid, bytes):
            raise TypeError
        
        return cls._FIELD_SEPARATOR.join([cls._PROTOCOL_COOKIE, 
                                          cls.PROTOCOL_VERSION, 
                                          cls._serialize_bytearray(dbid)]) 

    @classmethod
    def parse_greeting_message(cls, msgstr):
        """Parse the greeting message string.
        
        Returns the data base id (bytes) or raises a ProtocolParseError if 
        the string can't be parsed.  If the message is a valid greeting but 
        announces a version that is incompatible with the current protocol 
        version, a ProtocolVersionError is raised. 
        
        """

        if msgstr == None:
            raise ValueError
        
        if not isinstance(msgstr, str):
            raise TypeError
        
        match = re.search(
          ''.join([r'^', 
                   Protocol._PROTOCOL_COOKIE, 
                   Protocol._FIELD_SEPARATOR, 
                   r'([0-9]+\.[0-9]+)',
                   Protocol._FIELD_SEPARATOR,
                   r'([a-fA-F0-9]+)$']), msgstr)
        
        if not match:
            raise ProtocolParseError
        
        ver, dbid_hex = match.groups()
        
        """Only exact match for now (should preferably support older versions)"""
        if Protocol.PROTOCOL_VERSION != ver:
            raise ProtocolVersionError('Incompatible Protocol versions')
        
        try:
            dbid = cls._deserialize_bytearray(dbid_hex)
        except ValueError:
            raise ProtocolParseError
        
        return dbid 
        
    @classmethod
    def create_message_id_list_request(cls, time_cookie=None):
        """Create the message id request string.
        
        The time cookie (bytes) is optional and will be serialized to some 
        readable format.
        
        [C]                                                    [S]
         |                                                      | 
         |             GETMESSAGELIST [<time cookie>]           | 
         |----------------------------------------------------->| 
         |                                                      | 

        """ 
        
        if time_cookie is None:
            return cls._GETMESSAGELIST
    
        if not isinstance(time_cookie, bytes):
            raise TypeError
        
        return ' '.join([cls._GETMESSAGELIST, cls._serialize_bytearray(time_cookie)])
        
        
    @classmethod
    def parse_message_id_list_request(cls, msgstr):
        """Parse the message id request string.
        
        If  a time cookie is present in the string it will be returned 
        as a bytes type. If not, None will be returned.
        
        Raises a ProtocolParseError if the string can't be parsed.
        
        """
        
        if msgstr is None:
            raise ValueError
        
        if not isinstance(msgstr, str):
            raise TypeError
        
        match = re.search(''.join([r'^', 
                                   Protocol._GETMESSAGELIST, 
                                   r'( ([a-fA-F0-9]+))?$']), msgstr)
        
        if not match:
            raise ProtocolParseError
        
        if match.groups()[0] is None:
            return None
        
        return cls._deserialize_bytearray(match.groups()[1])
        
    @classmethod    
    def create_message_id_list(cls, time_cookie, messages=None):
        """Create the response string for sending message IDs from the server.
        
        The time_cookie (bytes) is required, but the list of Message's is
        optional.
        
        [C]                                                    [S]
         |                                                      | 
         |       <time cookie>;<msgid>;<msgid>;...;<msgid>      | 
         |<-----------------------------------------------------| 
         |                                                      | 
        
        """
        
        if time_cookie is None:
            raise ValueError
    
        if not isinstance(time_cookie, bytes):
            raise TypeError

        if messages is None: # Don't set default=[] (would make default mutable)
            messages = []

        if not hasattr(messages, '__iter__'):
            raise TypeError
        
        tc_str = cls._serialize_bytearray(time_cookie)
        
        """TOOO How to do this in a pythonic way?"""
        msgparts = [tc_str]
        msgparts.extend([cls._serialize_bytearray(msg.id) for msg in messages])
        return Protocol._FIELD_SEPARATOR.join(msgparts)

        
    @classmethod
    def parse_message_id_list(cls, msgstr):
        """Parse the message ID response string from the server.
        
        Raises a ProtocolParseError if the string can't be parsed.
        
        """
        
        if msgstr is None:
            raise ValueError
        
        if not isinstance(msgstr, str):
            raise TypeError
        
        match = re.search(''.join([r'^', 
                                   r'([a-fA-F0-9]+)', 
                                   r'(;[a-fA-F0-9]+)*$']), msgstr)
        
        if not match:
            raise ProtocolParseError
        
        tc = match.groups()[0]
        if tc is None:
            raise ProtocolParseError
        
        return (cls._deserialize_bytearray(tc), 
                [cls._deserialize_bytearray(m) for m in msgstr.split(';')[1:]])

        
    @classmethod
    def create_message_list_request(cls, message_ids=None):
        """Create the request string used by the client to request a list of messages.
        
        [C]                                                    [S]
         |                                                      | 
         |    GETMESSAGES [[[<msgid>];<msgid>];...;<msgid>]     | 
         |----------------------------------------------------->| 
         |                                                      |  
        
        """
        
    @classmethod
    def parse_message_list_request(cls, str):
        """Parse the message request string from the client
        
        Raises a ProtocolParseError if the string can't be parsed.
        
        """
        
        requested_message_ids = None # None means all
        return requested_message_ids
    
    @classmethod
    def create_message_list(cls, messages):
        """Create the response string used to transmits the requested messages from the server.
        
        [C]                                                    [S]
         |                                                      | 
         |              <msg>;<msg>;...;<msg>;                  | 
         |<-----------------------------------------------------| 
         |                                                      | 

        """
    
    @classmethod
    def parse_message_list(cls, str):
        """Parse the message response string from the server.
        
        Raises a ProtocolParseError if the string can't be parsed.
        Returns a list of messages. 
        
        """
        messages = []
        return messages
    
    
    @staticmethod
    def _serialize_bytearray(b):
        """bytes to string serialization"""
        try:
            s = binascii.b2a_hex(b).decode()
        except binascii.Error:
            raise ValueError()
        
        return s 
    
    @staticmethod
    def _deserialize_bytearray(s):
        """string to bytes de-serialization"""
        try:
            b = bytes(binascii.a2b_hex(s))
        except binascii.Error:
            raise ValueError()
        
        return b 
        