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

from dandelion.identity import Identity, RSA_key, DSA_key
from dandelion.message import Message
from dandelion.util import encode_b64_bytes, decode_b64_bytes, encode_b64_int, \
    decode_b64_int
import re

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
    TERMINATOR = '\n'
    
    _PROTOCOL_COOKIE = 'DMS'
    _FIELD_SEPARATOR = ';'
    _SUB_FIELD_SEPARATOR = '|'
    
    _GETMESSAGELIST = 'GETMESSAGELIST'
    _GETMESSAGES = 'GETMESSAGES'
 
    _GETIDENTITYLIST = 'GETIDENTITYLIST'
    _GETIDENTITIES = 'GETIDENTITIES'
    
    
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
        
        return '{0}{3}{1}{3}{2}{4}'.format(cls._PROTOCOL_COOKIE, 
                                           Protocol.PROTOCOL_VERSION, 
                                           encode_b64_bytes(dbid).decode(),
                                           cls._FIELD_SEPARATOR,
                                           Protocol.TERMINATOR)

    @classmethod
    def parse_greeting_message(cls, msgstr):
        """Parse the greeting message string.
        
        Returns the data base id (bytes) or raises a ProtocolParseError if 
        the string can't be parsed.  If the message is a valid greeting but 
        announces a version that is incompatible with the current protocol 
        version, a ProtocolVersionError is raised.         
        """

        cls._assert_type(msgstr, str)
        
        match = re.search(
          ''.join([r'^', 
                   cls._PROTOCOL_COOKIE, 
                   cls._FIELD_SEPARATOR, 
                   r'([0-9]+\.[0-9]+)',
                   cls._FIELD_SEPARATOR,
                   r'([a-zA-Z0-9+/=]+)',
                   Protocol.TERMINATOR,
                   r'$']), msgstr)
        
        if not match:
            raise ProtocolParseError
        
        ver, dbid_str = match.groups()
        
        """Only exact match for now (should preferably support older versions)"""
        if Protocol.PROTOCOL_VERSION != ver:
            raise ProtocolVersionError('Incompatible Protocol versions')
        
        try:
            dbid = decode_b64_bytes(dbid_str.encode())
        except ValueError:
            raise ProtocolParseError
        
        return dbid 
        
    @classmethod
    def is_message_id_list_request(cls, msgstr):
        """Check if the string is a message id request."""
        
        cls._assert_type(msgstr, str)
        
        return msgstr.startswith(cls._GETMESSAGELIST)

    @classmethod
    def is_identity_id_list_request(cls, msgstr):
        """Check if the string is a identity id request."""

        cls._assert_type(msgstr, str)
                
        return msgstr.startswith(cls._GETIDENTITYLIST)    
        
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
            return ''.join([cls._GETMESSAGELIST, Protocol.TERMINATOR])
    
        if not isinstance(time_cookie, bytes):
            raise TypeError
        
        return '{0} {1}{2}'.format(cls._GETMESSAGELIST, 
                                   encode_b64_bytes(time_cookie).decode(), 
                                   Protocol.TERMINATOR)
            
    @classmethod
    def create_identity_id_list_request(cls, time_cookie=None):
        """Create the identity id request string.
        
        The time cookie (bytes) is optional and will be serialized to some 
        readable format.
        
        [C]                                                    [S]
         |                                                      | 
         |              GETUSERLIST [<time cookie> ]            | 
         |----------------------------------------------------->| 
         |                                                      | 
        """         

        if time_cookie is None:
            return ''.join([cls._GETIDENTITYLIST, Protocol.TERMINATOR])
    
        if not isinstance(time_cookie, bytes):
            raise TypeError
        
        return '{0} {1}{2}'.format(cls._GETIDENTITYLIST, 
                                   encode_b64_bytes(time_cookie).decode(), 
                                   Protocol.TERMINATOR)

        
    @classmethod
    def parse_message_id_list_request(cls, msgstr):
        """Parse the message id request string.
        
        If  a time cookie is present in the string it will be returned 
        as a bytes type. If not, None will be returned.
        
        Raises a ProtocolParseError if the string can't be parsed.
        """
        
        cls._assert_type(msgstr, str)
                
        if not cls.is_message_id_list_request(msgstr):
            raise ProtocolParseError
                
        match = re.search(''.join([r'^', 
                                   cls._GETMESSAGELIST, 
                                   r'( ([a-zA-Z0-9+/=]+))?',
                                   Protocol.TERMINATOR,
                                   r'$']), msgstr)
        
        if not match:
            raise ProtocolParseError
        
        if match.groups()[0] is None:
            return None
        
        return decode_b64_bytes(match.groups()[1].encode())
        
    @classmethod
    def parse_identity_id_list_request(cls, identitystr):
        """Parse the identity id request string.
        
        If  a time cookie is present in the string it will be returned 
        as a bytes type. If not, None will be returned.
        
        Raises a ProtocolParseError if the string can't be parsed.
        """
        
        cls._assert_type(identitystr, str)
                
        if not cls.is_identity_id_list_request(identitystr):
            raise ProtocolParseError
                
        match = re.search(''.join([r'^', 
                                   cls._GETIDENTITYLIST, 
                                   r'( ([a-zA-Z0-9+/=]+))?',
                                   Protocol.TERMINATOR,
                                   r'$']), identitystr)
        
        if not match:
            raise ProtocolParseError
        
        if match.groups()[0] is None:
            return None
        
        return decode_b64_bytes(match.groups()[1].encode())
    
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
        
        cls._assert_type(time_cookie, bytes)

        if messages is None: # Don't use mutable default (e.g. [])
            messages = []

        if not hasattr(messages, '__iter__'):
            raise TypeError
        
        tc_str = encode_b64_bytes(time_cookie).decode()
        
        msgparts = [tc_str]
        msgparts.extend([encode_b64_bytes(msg.id).decode() for msg in messages])
        return ''.join([cls._FIELD_SEPARATOR.join(msgparts),
                        Protocol.TERMINATOR])

    @classmethod    
    def create_identity_id_list(cls, time_cookie, identities=None):
        """Create the response string for sending identity IDs from the server.
        
        The time_cookie (bytes) is required, but the list of IDs is
        optional.
        
        [C]                                                    [S]
         |                                                      | 
         |         <time cookie>;<uid>;<uid>;...;<uid>          | 
         |<-----------------------------------------------------| 
         |                                                      | 
        """
        
        cls._assert_type(time_cookie, bytes)

        if identities is None: # Don't use mutable default (e.g. [])
            identities = []

        if not hasattr(identities, '__iter__'):
            raise TypeError
        
        tc_str = encode_b64_bytes(time_cookie).decode()
        
        identityparts = [tc_str]
        identityparts.extend([encode_b64_bytes(identity.fingerprint).decode() for identity in identities])
        return ''.join([cls._FIELD_SEPARATOR.join(identityparts),
                        Protocol.TERMINATOR])

                
    @classmethod
    def parse_message_id_list(cls, msgstr):
        """Parse the message ID response string from the server.
        
        Returns a (tc, [msgid]) tuple.
        
        Raises a ProtocolParseError if the string can't be parsed.
        """
        
        cls._assert_type(msgstr, str)

        match = re.search(''.join([r'^', 
                                   r'([a-zA-Z0-9+/=]+)', 
                                   r'(;[a-zA-Z0-9+/=]+)*',
                                   Protocol.TERMINATOR,
                                   r'$']), msgstr)
        
        if not match:
            raise ProtocolParseError
        
        tc = match.groups()[0]
        if tc is None:
            raise ProtocolParseError
        
        return (decode_b64_bytes(tc.encode()), 
                [decode_b64_bytes(m.encode()) for m in msgstr[:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)[1:]])

    @classmethod
    def parse_identity_id_list(cls, identitystr):
        """Parse the identity ID response string from the server.
        
        Returns a (tc, [identityid]) tuple.
        
        Raises a ProtocolParseError if the string can't be parsed.
        """
        
        cls._assert_type(identitystr, str)

        match = re.search(''.join([r'^', 
                                   r'([a-zA-Z0-9+/=]+)', 
                                   r'(;[a-zA-Z0-9+/=]+)*',
                                   Protocol.TERMINATOR,
                                   r'$']), identitystr)
        
        if not match:
            raise ProtocolParseError
        
        tc = match.groups()[0]
        if tc is None:
            raise ProtocolParseError
        
        return (decode_b64_bytes(tc.encode()), 
                [decode_b64_bytes(identityid.encode()) for identityid in identitystr[:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)[1:]])



    @classmethod
    def is_message_list_request(cls, msgstr):
        """Check if the string is a message list request"""
        cls._assert_type(msgstr, str)
                
        return msgstr.startswith(cls._GETMESSAGES)
    
    @classmethod
    def is_identity_list_request(cls, identitystr):
        """Check if the string is a identity list request"""
        cls._assert_type(identitystr, str)
                
        return identitystr.startswith(cls._GETIDENTITIES)


    @classmethod
    def create_message_list_request(cls, msg_ids=None):
        """Create the request string used by the client to request a list of messages.
        
        [C]                                                    [S]
         |                                                      | 
         |    GETMESSAGES [[[<msgid>];<msgid>];...;<msgid>]     | 
         |----------------------------------------------------->| 
         |                                                      |  
        """
        
        if msg_ids is None: # Don't use mutable default (e.g. [])
            msg_ids = []

        if not hasattr(msg_ids, '__iter__'):
            raise TypeError

        if len(msg_ids) == 0:
            return ''.join([cls._GETMESSAGES, Protocol.TERMINATOR])
        
        msgid_str = cls._FIELD_SEPARATOR.join([encode_b64_bytes(mid).decode() for mid in msg_ids])
        
        return '{0} {1}{2}'.format(cls._GETMESSAGES, msgid_str, Protocol.TERMINATOR)
        
    @classmethod
    def create_identity_list_request(cls, identity_ids=None):
        """Create the request string used by the client to request a list of identities.
        
        [C]                                                    [S]
         |                                                      | 
         |    GETIDENTITIES [[[<identityid>];<identityid>];...;<identityid>]     | 
         |----------------------------------------------------->| 
         |                                                      |  
        """

        if identity_ids is None: # Don't use mutable default (e.g. [])
            identity_ids = []

        if not hasattr(identity_ids, '__iter__'):
            raise TypeError

        if len(identity_ids) == 0:
            return ''.join([cls._GETIDENTITIES, Protocol.TERMINATOR])
        identityid_str = cls._FIELD_SEPARATOR.join([encode_b64_bytes(uid).decode() for uid in identity_ids])
        
        return '{0} {1}{2}'.format(cls._GETIDENTITIES, identityid_str, Protocol.TERMINATOR)
    

    @classmethod
    def parse_message_list_request(cls, msgstr):
        """Parse the message request string from the client
        
        Raises a ProtocolParseError if the string can't be parsed.
        """

        if not cls.is_message_list_request(msgstr):
            raise ProtocolParseError

        match = re.search(r''.join([r'^',
                                    cls._GETMESSAGES, 
                                    r'( [a-zA-Z0-9+/=]+)?', 
                                    r'(;[a-zA-Z0-9+/=]+)*',
                                    Protocol.TERMINATOR,
                                    r'$']), msgstr)
        if not match:
            raise ProtocolParseError

        if not match.groups()[0]:
            return None
        
        id_strings = msgstr[len(cls._GETMESSAGES) + 1:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)
        return [decode_b64_bytes(id.encode()) for id in id_strings]
    
    @classmethod
    def parse_identity_list_request(cls, identitystr):
        """Parse the identity request string from the client
        
        Raises a ProtocolParseError if the string can't be parsed.
        """
        
        if not cls.is_identity_list_request(identitystr):
            raise ProtocolParseError

        match = re.search(r''.join([r'^',
                                    cls._GETIDENTITIES, 
                                    r'( [a-zA-Z0-9+/=]+)?', 
                                    r'(;[a-zA-Z0-9+/=]+)*',
                                    Protocol.TERMINATOR,
                                    r'$']), identitystr)
        if not match:
            raise ProtocolParseError

        if not match.groups()[0]:
            return None
        
        id_strings = identitystr[len(cls._GETIDENTITIES) + 1:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)
        return [decode_b64_bytes(id.encode()) for id in id_strings]

    
    @classmethod
    def create_message_list(cls, messages):
        """Create the message transmission string.
        
        Create the response string used to transmits the requested
        messages from the server.
        
        [C]                                                    [S]
         |                                                      | 
         |              <msg>;<msg>;...;<msg>                   | 
         |<-----------------------------------------------------| 
         |                                                      | 
        """

        if messages is None:
            raise ValueError
    
        if not hasattr(messages, '__iter__'):
            raise TypeError
        
        msgstrings = []
        for msg in messages:
            msgstrings.extend([cls._message2string(msg)])
        
        msg = cls._FIELD_SEPARATOR.join(msgstrings)
        
        return ''.join([msg, Protocol.TERMINATOR])
    
    @classmethod
    def create_identity_list(cls, identities):
        """Create the identity transmission string.
        
        Create the response string used to transmits the requested
        identities from the server.
        
        [C]                                                    [S]
         |                                                      | 
         |             <identity>;<identity>;...;<identity>                 | 
         |<-----------------------------------------------------| 
         |                                                      | 
        """
        
        if identities is None:
            raise ValueError
    
        if not hasattr(identities, '__iter__'):
            raise TypeError
        
        identitystrings = []
        for identity in identities:
            identitystrings.extend([cls._identity2string(identity)])
        
        identity = cls._FIELD_SEPARATOR.join(identitystrings)
        
        return ''.join([identity, Protocol.TERMINATOR])

    @classmethod
    def parse_message_list(cls, msgstr):
        """Parse the message transmission string from the server.
        
        Raises a ProtocolParseError if the string can't be parsed.
        Returns a list of messages. 
        """
        
        cls._assert_type(msgstr, str)

        match = re.search(''.join([r'^(.+)(', 
                                   cls._FIELD_SEPARATOR, 
                                   r'.+)*', 
                                   Protocol.TERMINATOR, 
                                   r'$']), msgstr)

        if not match:
            raise ProtocolParseError

        parts = msgstr[:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)
        
        return [cls._string2message(m) for m in parts]
     
    @classmethod
    def parse_identity_list(cls, identitystr):
        """Parse the identity transmission string from the server.
        
        Raises a ProtocolParseError if the string can't be parsed.
        Returns a list of identities. 
        """
        
        cls._assert_type(identitystr, str)

        match = re.search(''.join([r'^(.+)(', 
                                   cls._FIELD_SEPARATOR, 
                                   r'.+)*', 
                                   Protocol.TERMINATOR, 
                                   r'$']), identitystr)

        if not match:
            raise ProtocolParseError

        parts = identitystr[:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)
        
        return [cls._string2identity(identity) for identity in parts]

    @classmethod
    def _assert_type(cls, x, type):
        """If x is a string this function does nothing. If it is None it raises a 
        ValueError and if it's not a string it raises a TypeError.
        """
        if x is None:
            raise ValueError
        
        if not isinstance(x, type):
            raise TypeError

     
    @classmethod
    def _message2string(cls, msg):
        """Serialize a message to a DMS string"""
        
        text = msg.text.encode() if isinstance(msg.text, str) else msg.text # Convert to bytes string
        receiver = b'' if msg.receiver is None else msg.receiver
        sender, signature = (b'',b'') if msg.sender is None else (msg.sender, msg.signature)

        return cls._SUB_FIELD_SEPARATOR.join([
                  encode_b64_bytes(text).decode(),
                  encode_b64_bytes(receiver).decode(),
                  encode_b64_bytes(sender).decode(),
                  encode_b64_bytes(signature).decode()])
        
    @classmethod
    def _string2message(cls, mstr):
        """Parse the string and create a message"""

        TEXT_INDEX, RECEIVER_INDEX, SENDER_INDEX, SIGNATURE_INDEX = (0,1,2,3)

        mparts = mstr.split(cls._SUB_FIELD_SEPARATOR)
        
        if len(mparts) != 4:
            raise ProtocolParseError
        
        if (mparts[SENDER_INDEX] != b'' and mparts[SIGNATURE_INDEX] == b'') or (mparts[SENDER_INDEX] == b'' and mparts[SIGNATURE_INDEX] != b''):
            raise  ProtocolParseError

        receiver = None if mparts[RECEIVER_INDEX] == b'' else decode_b64_bytes(mparts[RECEIVER_INDEX].encode()) 
        text = decode_b64_bytes(mparts[TEXT_INDEX].encode())
        text = text.decode() if receiver is None else text # Decode unless encrypted 
        sender = None if mparts[SENDER_INDEX] == b'' else decode_b64_bytes(mparts[SENDER_INDEX].encode())
        signature = None if mparts[SIGNATURE_INDEX] == b'' else decode_b64_bytes(mparts[SIGNATURE_INDEX].encode())

        return Message(text, receiver, sender, signature)
    
    @classmethod
    def _identity2string(cls, identity):
        """Serialize a identity to a DMS string"""

        return cls._SUB_FIELD_SEPARATOR.join([
                  encode_b64_int(identity.rsa_key.n).decode(),
                  encode_b64_int(identity.rsa_key.e).decode(),
                  encode_b64_int(identity.dsa_key.y).decode(),
                  encode_b64_int(identity.dsa_key.g).decode(),
                  encode_b64_int(identity.dsa_key.p).decode(),
                  encode_b64_int(identity.dsa_key.q).decode()])


    @classmethod
    def _string2identity(cls, identitystr):
        """Parse the string and create a identity"""

        RSA_N_INDEX, RSA_E_INDEX, DSA_Y_INDEX, DSA_G_INDEX, DSA_P_INDEX, DSA_Q_INDEX = (0,1,2,3,4,5)

        idparts = identitystr.split(cls._SUB_FIELD_SEPARATOR)
        
        if len(idparts) != 6:
            raise ProtocolParseError

        rsa_key = RSA_key(decode_b64_int(idparts[RSA_N_INDEX].encode()), 
                         decode_b64_int(idparts[RSA_E_INDEX].encode()))
                
        dsa_key = DSA_key(decode_b64_int(idparts[DSA_Y_INDEX].encode()), 
                         decode_b64_int(idparts[DSA_G_INDEX].encode()),
                         decode_b64_int(idparts[DSA_P_INDEX].encode()),
                         decode_b64_int(idparts[DSA_Q_INDEX].encode()))
        
        return Identity(dsa_key, rsa_key)

