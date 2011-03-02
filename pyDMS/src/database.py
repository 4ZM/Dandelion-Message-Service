import random
import message

class DataBase: 
    """Message data base for the Dandelion Message Service"""
    
    ID_LENGTH_BYTES = 16
    
    def __init__(self):
        """Create a new data base with a random id"""
        
        # Using a naive in-memory db for now
        # TODO Should use some not so naive data structure here to get better access complexity  
        self._messages = []
        self._id = bytearray([int(random.random() * 255) for _ in range(DataBase.ID_LENGTH_BYTES)])
        self._rev = 0
        
        
    @property
    def id(self):
        """The data base id"""
        return self._id
        
    def add_message(self, msg):
        """Add a message or a list of messages to the data base.
        
        Will add all messages, not already in the data base to the data base and return a 
        time cookie that represents the point in time after the messages have been added.
        If no messages were added, it just returns the current time cookie. 
        
        """
        
        if msg is None:
            raise ValueError
        
        # Put it in a list if it isn't already
        # TODO require list
        if not hasattr(msg,'__iter__'):
            msg = [msg]
        
        # Make sure the list only contains messages
        for m in msg:
            if not isinstance(m, message.Message):
                raise ValueError
        
        # Add the messages not already present to the data base
        untagged_messages = [m for (_, m) in self._messages]
        new_msgs = [(self._rev, m) for m in msg if m not in untagged_messages]
        
        if len(new_msgs) > 0:
            self._messages.extend(new_msgs)
            self._rev += 1
            
        return self._rev
        
    def message_count(self):
        """Returns the number of messages currently in the data base"""
        
        return len(self._messages)
        
    def contains_message(self, msg):
        """Returns a True if the message is in the data base or a list of boolean values if the argument is a list of messages"""
        
        if not hasattr(msg,'__iter__'):
            msg = [msg]
            
        untagged_messages = [m for (_, m) in self._messages]
        l = [m in untagged_messages for m in msg]
        
        if len(l) == 1:
            return l[0]
        
        return l 
    
    def remove_message(self, msg=None):
        """Removes messages from the data base.
        
        The specified messages or list of messages will be removed from the data base. 
        If the message parameter is omitted, all messages in the data base will be removed.
        
        """
        
        if msg == None:
            self._messages = []
            return
        
        if not hasattr(msg,'__iter__'):
            msg = [msg]
        
        to_delete = []
        for m in self._messages:
            if m[1] in msg:
                to_delete.append(m)
                
        for m in to_delete:
            self._messages.remove(m)
            

    def messages_since(self, time_cookie=None):
        """Get messages from the data base.
        
        If a time cookie is specified, all messages in the database from (and 
        including) the time specified by the time cookie will be returned.  
        If the time cookie parameter is omitted, all messages currently in the 
        data base will be returned.
        
        """
        
        if time_cookie == None:
            return [m for (_, m) in self._messages]

        msgs = []
        for tc, m in self._messages:
            if tc >= time_cookie:
                msgs.append(m)
        
        return msgs
    