import binascii
import re
from message import Message
from database import DataBase

class ParseError(Exception):
    pass

class ProtocolError(Exception):
    pass

class Protocol:
    '''Represents the communication protocol'''
    
    _PROTOCOL_VERSION = '1.0'
    _PROTOCOL_COOKIE = 'RIOT'
    _FIELD_SEPARATOR = ';'
    _SUB_FIELD_SEPARATOR = '|'
    
    def CreateGreetingMessage(self, db):
        '''Create the greeting message sent to connecting clients'''
        
        if db == None or not isinstance(db, DataBase):
            raise ValueError
        
        return str.join(self._FIELD_SEPARATOR, \
                        [self._PROTOCOL_COOKIE, self._PROTOCOL_VERSION, db.GetId()]) 

    def ParseGreetingMessage(self, str):
        '''Parse the string to extract the fields'''
        
        if str == None or len(str) == 0:
            raise ValueError
        
        if not re.match(str.join(['^', self._PROTOCOL_COOKIE, self._FIELD_SEPARATOR, '[0-9]+\.[0-9]+']), str):
            raise ParseError
        
        _, ver, dbid_hex = str.split(self._FIELD_SEPARATOR)
        
        # Only exact match for now (should preferably support older versions)
        if Protocol._PROTOCOL_VERSION != ver:
            raise ProtocolError('Incompatible Protocol versions')
        
        dbid_bin = binascii.a2b_hex(dbid_hex)
        if len(dbid_bin) != DataBase.ID_LENGTH_BYTES:
            raise ParseError

        return dbid_bin
        
    
    def CreateMessageIdListRequest(self, time_cookie = None):
        '''Create the message used to request a list of message IDs''' 
        
    def ParseMessageIdListRequest(self, str):
        '''Parse a string requesting a list of message IDs'''
        time_cookie = None
        return time_cookie
        
    def CreateMessageIdList(self, message_ids):
        '''Create the message containing message IDs'''
        
    def ParseMessageIdList(self, str):
        '''Parse the message containing message IDs'''
        message_ids = []
        return message_ids
        
    def CreateMessageListRequest(self, message_ids = None):
        '''Create the message used to request a list of message ids''' 
        
    def ParseMessageListRequest(self, str):
        '''Parse a string requesting a list of message ids'''
        requested_message_ids = None # None means all
        return requested_message_ids
        
    def CreateMessageList(self, messages):
        '''Create the message that transmits the messages'''
        
    def ParseMessageList(self, str):
        '''Parse the message that transmits the messages'''
        messages = []
        return messages