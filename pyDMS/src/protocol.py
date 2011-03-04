import binascii
import re
from message import Message
from database import DataBase

class ProtocolParseError(Exception):
    pass

class ProtocolVersionError(Exception):
    pass

class Protocol:
    """This class encapsulates and represents the Dandelion Message Service communication protoco
    
    It handles formating the messages, but not populating them with meaningful data. Like the protocol it is stateless (hence the static functions). 
    
    """
    
    PROTOCOL_VERSION = '1.0'
    
    _PROTOCOL_COOKIE = 'DMS'
    _FIELD_SEPARATOR = ';'
    _SUB_FIELD_SEPARATOR = '|'
    
    def create_greeting_message(self, dbid):
        """Create the server greeting message. 
        
        This message is sent from the server to the client upon connection. 
        The dbid is a binary array representing a data base id. 
        
        [C]                                                    [S]
         |                                                      | 
         |                       connect                        | 
         |----------------------------------------------------->| 
         |                                                      | 
         |     <protocol cookie>;<protocol version>;<db id>     | 
         |<-----------------------------------------------------| 
         |                                                      | 
         |                                                      |
          
        """
        
        if not dbid or not isinstance(dbid, bytearray):
            raise ValueError
        
        print ("dbid, ", dbid)
        return self._FIELD_SEPARATOR.join([self._PROTOCOL_COOKIE, self.PROTOCOL_VERSION, self._serialize_bytearray(dbid)]) 

    def parse_greeting_message(self, str):
        """Parse the greeting message string to extract the message fields.
        
        Returns the data base is and raises a ProtocolParseError if the string can't be parsed. 
        If the message is a valid greeting but announces an unknown protocol cookie or 
        a version that is incompatible with the current protocol version, a ProtocolVersionError is raised. 
        
        """
        
        if str == None or len(str) == 0:
            raise ValueError
        
        if not re.match(str.join(['^', Protocol._PROTOCOL_COOKIE, Protocol._FIELD_SEPARATOR, '[0-9]+\.[0-9]+']), str):
            raise ProtocolParseError
        
        _, ver, dbid_hex = str.split(Protocol._FIELD_SEPARATOR)
        
        # Only exact match for now (should preferably support older versions)
        if Protocol._PROTOCOL_VERSION != ver:
            raise ProtocolVersionError('Incompatible Protocol versions')
        
        # TODO Should perhaps not perform this kind of 'deep' semantic check in this class
        dbid_bin = binascii.a2b_hex(dbid_hex)
        if len(dbid_bin) != DataBase._ID_LENGTH_BYTES:
            raise ProtocolParseError

        return dbid_bin
        
    
    def create_message_id_list_request(self, time_cookie=None):
        """Create the request string used by the client to request a list of message IDs.
        
        The time cookie is an integer represented as hex in the string.
        
        [C]                                                    [S]
         |                                                      | 
         |             GETMESSAGELIST [<time cookie>]           | 
         |----------------------------------------------------->| 
         |                                                      | 
         |       <time cookie>;<msgid>;<msgid>;...;<msgid>      | 
         |<-----------------------------------------------------| 
         |                                                      | 
         |                                                      | 
        
        """ 
        
    def parse_message_id_list_request(self, str):
        """Parse the message id request string.
        
        The time cookie is an integer represented as hex in the string.
        Raises a ProtocolParseError if the string can't be parsed.
        
        """
        
        
        time_cookie = None
        return time_cookie
        
    def create_message_id_list(self, time_cookie, messages=[]):
        """Create the response string for sending message IDs from the server.
        
        [C]                                                    [S]
         |                                                      | 
         |             GETMESSAGELIST [<time cookie>]           | 
         |----------------------------------------------------->| 
         |                                                      | 
         |       <time cookie>;<msgid>;<msgid>;...;<msgid>      | 
         |<-----------------------------------------------------| 
         |                                                      | 
         |                                                      | 
        
        """
        
    def parse_message_id_list(self, str):
        """Parse the message ID response string from the server.
        
        Raises a ProtocolParseError if the string can't be parsed.
        
        """
        
        message_ids = []
        return message_ids
        
    def create_message_list_request(self, message_ids = None):
        """Create the request string used by the client to request a list of messages.
        
        [C]                                                    [S]
         |                                                      | 
         |    GETMESSAGES [[[<msgid>];<msgid>];...;<msgid>]     | 
         |----------------------------------------------------->| 
         |                                                      | 
         |              <msg>;<msg>;...;<msg>;                  | 
         |<-----------------------------------------------------| 
         |                                                      | 
         |                                                      | 
        
        """
        
    def parse_message_list_request(self, str):
        """Parse the message request string from the client
        
        Raises a ProtocolParseError if the string can't be parsed.
        
        """
        
        requested_message_ids = None # None means all
        return requested_message_ids
        
    def create_message_list(self, messages):
        """Create the response string used to transmits the requested messages from the server.
        
        [C]                                                    [S]
         |                                                      | 
         |    GETMESSAGES [[[<msgid>];<msgid>];...;<msgid>]     | 
         |----------------------------------------------------->| 
         |                                                      | 
         |              <msg>;<msg>;...;<msg>;                  | 
         |<-----------------------------------------------------| 
         |                                                      | 
         |                                                      | 

        """
        
    def parse_message_list(self, str):
        """Parse the message response string from the server.
        
        Raises a ProtocolParseError if the string can't be parsed.
        Returns a list of messages. 
        
        """
        messages = []
        return messages
    
    def _serialize_integer(self, integer):
        """Integer to string serialization"""
        return hex(integer)
    
    def _deserialize_integer(self, string):
        """string to integer de-serialization"""
    
    def _serialize_bytearray(self, bytes):
        """bytearray to string serialization"""
        return binascii.b2a_hex(str(bytes))
    
    def _deserialize_bytearray(self, string):
        """string to bytearray de-serialization"""
        return bytearray(binascii.a2b_hex(string))
        