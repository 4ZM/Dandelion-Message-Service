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

import random
import pickle

from message import Message

class ContentDB: 
    """Message data base for the Dandelion Message Service"""
    
    _ID_LENGTH_BYTES = 16
    
    def __init__(self):
        """Create a new data base with a random id"""
        
        # Using a naive in-memory db for now
        # TODO Should use some not so naive data structure here to get better access complexity  
        self._messages = []
        self._id = bytes([int(random.random() * 255) for _ in range(ContentDB._ID_LENGTH_BYTES)])
        self._rev = 0
        
        
    @property
    def id(self):
        """The data base id (bytes)"""
        return self._id
    
    # TODO TimeCookie should be long number?
    def add_messages(self, msgs):
        """Add a a list of messages to the data base.
        
        Will add all messages, not already in the data base to the data base and return a 
        time cookie (bytes) that represents the point in time after the messages have been added.
        If no messages were added, it just returns the current time cookie. 
        
        """
        
        if msgs is None:
            raise ValueError
        
        if not hasattr(msgs,'__iter__'):
            raise TypeError
        
        # Make sure the list only contains messages
        for m in msgs:
            if not isinstance(m, Message):
                raise TypeError
        
        # Add the messages not already present to the data base
        untagged_messages = [m for (_, m) in self._messages]
        new_msgs = [(self._rev, m) for m in msgs if m not in untagged_messages]
        
        if len(new_msgs) > 0:
            self._messages.extend(new_msgs)
            self._rev += 1
            
        #pickle.loads(binascii.a2b_hex(binascii.b2a_hex(pickle.dumps(123))))
            
        return pickle.dumps(self._rev)
        
    @property
    def message_count(self):
        """Returns the number of messages currently in the data base (int)"""
        
        return len(self._messages)
        
    def contains_messages(self, msgs):
        """Returns a list of boolean values where True indicates that the argument at 
        that position in the argument message list is in the data base.
        
        """
        
        if not hasattr(msgs,'__iter__'):
            raise TypeError
            
        untagged_messages = [m for (_, m) in self._messages]
        l = [m in untagged_messages for m in msgs]
        
        return l 
    
    def remove_messages(self, msgs=None):
        """Removes messages from the data base.
        
        The specified list of messages will be removed from the data base. 
        If the message parameter is omitted, all messages in the data base will be removed.
        
        """
        
        if msgs is None:
            self._messages = []
            return
        
        if not hasattr(msgs,'__iter__'):
            raise TypeError
        
        to_delete = [(tc,m) for tc, m in self._messages if m in msgs]
                        
        for m in to_delete:
            self._messages.remove(m)

    def get_messages(self, msgids=None):
        """Get a list of all messages with specified message id"""
        
        if msgids is None:
            return [m for _, m in self._messages]
        
        if not hasattr(msgids,'__iter__'):
            raise TypeError
               
        return [m for _, m in self._messages if m.id in msgids]

    def messages_since(self, time_cookie=None):
        """Get messages from the data base.
        
        If a time cookie is specified, all messages in the database from (and 
        including) the time specified by the time cookie will be returned.  
        If the time cookie parameter is omitted, all messages currently in the 
        data base will be returned.
        
        """
        
        if time_cookie is None:
            return (pickle.dumps(self._rev), [m for (_, m) in self._messages])
        
        if not isinstance(time_cookie, bytes):
            raise TypeError 
        
        tc_num = pickle.loads(time_cookie)
        msgs = []
        for tc, m in self._messages:
            if tc >= tc_num:
                msgs.append(m)
        
        return (pickle.dumps(self._rev), msgs)
    