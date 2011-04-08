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

import re
from dandelion.message import Message
import dandelion.util
from dandelion.identity import Identity, RSAKey, DSAKey

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
 
    _GETUSERLIST = 'GETUSERLIST'
    _GETUSERS = 'GETUSERS'
    
    
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
                                           dandelion.util.encode_b64_bytes(dbid).decode(),
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
            dbid = dandelion.util.decode_b64_bytes(dbid_str.encode())
        except ValueError:
            raise ProtocolParseError
        
        return dbid 
        
    @classmethod
    def is_message_id_list_request(cls, msgstr):
        """Check if the string is a message id request."""
        
        cls._assert_type(msgstr, str)
        
        return msgstr.startswith(cls._GETMESSAGELIST)

    @classmethod
    def is_user_id_list_request(cls, msgstr):
        """Check if the string is a user id request."""

        cls._assert_type(msgstr, str)
                
        return msgstr.startswith(cls._GETUSERLIST)    
        
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
                                   dandelion.util.encode_b64_bytes(time_cookie).decode(), 
                                   Protocol.TERMINATOR)
            
    @classmethod
    def create_user_id_list_request(cls, time_cookie=None):
        """Create the user id request string.
        
        The time cookie (bytes) is optional and will be serialized to some 
        readable format.
        
        [C]                                                    [S]
         |                                                      | 
         |              GETUSERLIST [<time cookie> ]            | 
         |----------------------------------------------------->| 
         |                                                      | 
        """         

        if time_cookie is None:
            return ''.join([cls._GETUSERLIST, Protocol.TERMINATOR])
    
        if not isinstance(time_cookie, bytes):
            raise TypeError
        
        return '{0} {1}{2}'.format(cls._GETUSERLIST, 
                                   dandelion.util.encode_b64_bytes(time_cookie).decode(), 
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
        
        return dandelion.util.decode_b64_bytes(match.groups()[1].encode())
        
    @classmethod
    def parse_user_id_list_request(cls, userstr):
        """Parse the user id request string.
        
        If  a time cookie is present in the string it will be returned 
        as a bytes type. If not, None will be returned.
        
        Raises a ProtocolParseError if the string can't be parsed.
        """
        
        cls._assert_type(userstr, str)
                
        if not cls.is_user_id_list_request(userstr):
            raise ProtocolParseError
                
        match = re.search(''.join([r'^', 
                                   cls._GETUSERLIST, 
                                   r'( ([a-zA-Z0-9+/=]+))?',
                                   Protocol.TERMINATOR,
                                   r'$']), userstr)
        
        if not match:
            raise ProtocolParseError
        
        if match.groups()[0] is None:
            return None
        
        return dandelion.util.decode_b64_bytes(match.groups()[1].encode())
    
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
        
        tc_str = dandelion.util.encode_b64_bytes(time_cookie).decode()
        
        msgparts = [tc_str]
        msgparts.extend([dandelion.util.encode_b64_bytes(msg.id).decode() for msg in messages])
        return ''.join([cls._FIELD_SEPARATOR.join(msgparts),
                        Protocol.TERMINATOR])

    @classmethod    
    def create_user_id_list(cls, time_cookie, users=None):
        """Create the response string for sending user IDs from the server.
        
        The time_cookie (bytes) is required, but the list of IDs is
        optional.
        
        [C]                                                    [S]
         |                                                      | 
         |     <time cookie>;<userid>;<userid>;...;<userid>     | 
         |<-----------------------------------------------------| 
         |                                                      | 
        """
        
        cls._assert_type(time_cookie, bytes)

        if users is None: # Don't use mutable default (e.g. [])
            users = []

        if not hasattr(users, '__iter__'):
            raise TypeError
        
        tc_str = dandelion.util.encode_b64_bytes(time_cookie).decode()
        
        userparts = [tc_str]
        userparts.extend([dandelion.util.encode_b64_bytes(user.fingerprint).decode() for user in users])
        return ''.join([cls._FIELD_SEPARATOR.join(userparts),
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
        
        return (dandelion.util.decode_b64_bytes(tc.encode()), 
                [dandelion.util.decode_b64_bytes(m.encode()) for m in msgstr[:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)[1:]])

    @classmethod
    def parse_user_id_list(cls, userstr):
        """Parse the user ID response string from the server.
        
        Returns a (tc, [userid]) tuple.
        
        Raises a ProtocolParseError if the string can't be parsed.
        """
        
        cls._assert_type(userstr, str)

        match = re.search(''.join([r'^', 
                                   r'([a-zA-Z0-9+/=]+)', 
                                   r'(;[a-zA-Z0-9+/=]+)*',
                                   Protocol.TERMINATOR,
                                   r'$']), userstr)
        
        if not match:
            raise ProtocolParseError
        
        tc = match.groups()[0]
        if tc is None:
            raise ProtocolParseError
        
        return (dandelion.util.decode_b64_bytes(tc.encode()), 
                [dandelion.util.decode_b64_bytes(userid.encode()) for userid in userstr[:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)[1:]])



    @classmethod
    def is_message_list_request(cls, msgstr):
        """Check if the string is a message list request"""
        cls._assert_type(msgstr, str)
                
        return msgstr.startswith(cls._GETMESSAGES)
    
    @classmethod
    def is_user_list_request(cls, userstr):
        """Check if the string is a user list request"""
        cls._assert_type(userstr, str)
                
        return userstr.startswith(cls._GETUSERS)


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
        
        msgid_str = cls._FIELD_SEPARATOR.join([dandelion.util.encode_b64_bytes(mid).decode() for mid in msg_ids])
        
        return '{0} {1}{2}'.format(cls._GETMESSAGES, msgid_str, Protocol.TERMINATOR)
        
    @classmethod
    def create_user_list_request(cls, user_ids=None):
        """Create the request string used by the client to request a list of users.
        
        [C]                                                    [S]
         |                                                      | 
         |    GETUSERS [[[<userid>];<userid>];...;<userid>]     | 
         |----------------------------------------------------->| 
         |                                                      |  
        """

        if user_ids is None: # Don't use mutable default (e.g. [])
            user_ids = []

        if not hasattr(user_ids, '__iter__'):
            raise TypeError

        if len(user_ids) == 0:
            return ''.join([cls._GETUSERS, Protocol.TERMINATOR])
        
        userid_str = cls._FIELD_SEPARATOR.join([dandelion.util.encode_b64_bytes(uid).decode() for uid in user_ids])
        
        return '{0} {1}{2}'.format(cls._GETUSERS, userid_str, Protocol.TERMINATOR)
    

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
        return [dandelion.util.decode_b64_bytes(id.encode()) for id in id_strings]
    
    @classmethod
    def parse_user_list_request(cls, userstr):
        """Parse the user request string from the client
        
        Raises a ProtocolParseError if the string can't be parsed.
        """
        
        if not cls.is_user_list_request(userstr):
            raise ProtocolParseError

        match = re.search(r''.join([r'^',
                                    cls._GETUSERS, 
                                    r'( [a-zA-Z0-9+/=]+)?', 
                                    r'(;[a-zA-Z0-9+/=]+)*',
                                    Protocol.TERMINATOR,
                                    r'$']), userstr)
        if not match:
            raise ProtocolParseError

        if not match.groups()[0]:
            return None
        
        id_strings = userstr[len(cls._GETUSERS) + 1:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)
        return [dandelion.util.decode_b64_bytes(id.encode()) for id in id_strings]

    
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
    def create_user_list(cls, users):
        """Create the user transmission string.
        
        Create the response string used to transmits the requested
        users from the server.
        
        [C]                                                    [S]
         |                                                      | 
         |             <user>;<user>;...;<user>                 | 
         |<-----------------------------------------------------| 
         |                                                      | 
        """
        
        if users is None:
            raise ValueError
    
        if not hasattr(users, '__iter__'):
            raise TypeError
        
        userstrings = []
        for user in users:
            userstrings.extend([cls._user2string(user)])
        
        user = cls._FIELD_SEPARATOR.join(userstrings)
        
        return ''.join([user, Protocol.TERMINATOR])

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
    def parse_user_list(cls, userstr):
        """Parse the user transmission string from the server.
        
        Raises a ProtocolParseError if the string can't be parsed.
        Returns a list of users. 
        """
        
        cls._assert_type(userstr, str)

        match = re.search(''.join([r'^(.+)(', 
                                   cls._FIELD_SEPARATOR, 
                                   r'.+)*', 
                                   Protocol.TERMINATOR, 
                                   r'$']), userstr)

        if not match:
            raise ProtocolParseError

        parts = userstr[:-len(Protocol.TERMINATOR)].split(cls._FIELD_SEPARATOR)
        
        return [cls._string2user(user) for user in parts]

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
        receiver = b'' if msg.receiver is None else msg.receiver.encode()
        sender, signature = (b'',b'') if msg.sender is None else (msg.sender.encode(), msg.signature.encode())

        return cls._SUB_FIELD_SEPARATOR.join([
                  dandelion.util.encode_b64_bytes(text).decode(),
                  dandelion.util.encode_b64_bytes(receiver).decode(),
                  dandelion.util.encode_b64_bytes(sender).decode(),
                  dandelion.util.encode_b64_bytes(signature).decode()])
        
    @classmethod
    def _string2message(cls, mstr):
        """Parse the string and create a message"""
        
        TEXT_INDEX, RECEIVER_INDEX, SENDER_INDEX, SIGNATURE_INDEX = (0,1,2,3)

        mparts = mstr.split(cls._SUB_FIELD_SEPARATOR)
        
        if len(mparts) != 4:
            raise ProtocolParseError
        
        if (mparts[SENDER_INDEX] != b'' and mparts[SIGNATURE_INDEX] == b'') or (mparts[SENDER_INDEX] == b'' and mparts[SIGNATURE_INDEX] != b''):
            raise  ProtocolParseError
        
        receiver = dandelion.util.decode_b64_bytes(mparts[RECEIVER_INDEX].encode()).decode() if mparts[RECEIVER_INDEX] == b'' else None 
        text = dandelion.util.decode_b64_bytes(mparts[TEXT_INDEX].encode())
        text = text.decode() if receiver is None else text # Decode unless encrypted 
        sender = dandelion.util.decode_b64_bytes(mparts[SENDER_INDEX].encode()).decode() if mparts[SENDER_INDEX] == b'' else None
        signature = dandelion.util.decode_b64_bytes(mparts[SIGNATURE_INDEX].encode()).decode() if mparts[SIGNATURE_INDEX] == b'' else None

        return Message(text, receiver, sender, signature)
    
    @classmethod
    def _user2string(cls, user):
        """Serialize a user to a DMS string"""

        return cls._SUB_FIELD_SEPARATOR.join([
                  dandelion.util.encode_b64_int(user.rsa_key.n).decode(),
                  dandelion.util.encode_b64_int(user.rsa_key.e).decode(),
                  dandelion.util.encode_b64_int(user.dsa_key.y).decode(),
                  dandelion.util.encode_b64_int(user.dsa_key.g).decode(),
                  dandelion.util.encode_b64_int(user.dsa_key.p).decode(),
                  dandelion.util.encode_b64_int(user.dsa_key.q).decode()])


    @classmethod
    def _string2user(cls, userstr):
        """Parse the string and create a user"""

        RSA_N_INDEX, RSA_E_INDEX, DSA_Y_INDEX, DSA_G_INDEX, DSA_P_INDEX, DSA_Q_INDEX = (0,1,2,3,4,5)

        uparts = userstr.split(cls._SUB_FIELD_SEPARATOR)
        
        if len(uparts) != 6:
            raise ProtocolParseError

        rsa_key = RSAKey(dandelion.util.decode_b64_int(uparts[RSA_N_INDEX].encode()), 
                         dandelion.util.decode_b64_int(uparts[RSA_E_INDEX].encode()))
                
        dsa_key = DSAKey(dandelion.util.decode_b64_int(uparts[DSA_Y_INDEX].encode()), 
                         dandelion.util.decode_b64_int(uparts[DSA_G_INDEX].encode()),
                         dandelion.util.decode_b64_int(uparts[DSA_P_INDEX].encode()),
                         dandelion.util.decode_b64_int(uparts[DSA_Q_INDEX].encode()))
        
        return Identity(dsa_key, rsa_key)

