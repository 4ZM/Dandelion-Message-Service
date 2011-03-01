import random
import message

class DataBase: 
    '''Message Data Base'''
    
    ID_LENGTH_BYTES = 16
    
    def __init__(self):
        '''Create a new DataBase instance'''
        
        # Using a naive in-memory db for now
        # TODO Should use some not so naive data structure here to get better access complexity  
        self._messages = []
        self._id = bytearray([int(random.random() * 255) for _ in xrange(DataBase.ID_LENGTH_BYTES)])
        self._rev = 0
        
    def GetId(self):
        '''Returns the data base id'''
        return self._id
        
    def AddMessage(self, msg):
        '''
        Add a message or a list of messages to the data base.
        returns a TimeCookie
        '''
        if msg == None:
            raise ValueError
        
        # Put it in a list if it isn't already
        if not hasattr(msg,'__iter__'):
            msg = [msg]
        
        for m in msg:
            if not isinstance(m, message.Message):
                raise ValueError
        
        # Add the messages not already present
        new_msgs = [(self._rev, m) for m in msg if m not in self._messages]
        self._messages.extend(new_msgs)
        
        self._rev += 1
        return self._rev
        
    def MessageCount(self):
        '''Returns the number of messages in the data base'''
        return len(self._messages)
        
    def ContainsMessage(self, msg):
        '''Returns a True if the message is in the data base or a list of boolean values if the argument is a list of messages'''
        
        if not hasattr(msg,'__iter__'):
            msg = [msg]
            
        untagged_messages = [m for (_, m) in self._messages]
        l = [m in untagged_messages for m in msg]

        #l = [(_, m) in self._messages for m in msg]
        #l = [m in self._messages for m in msg]
        
        if len(l) == 1:
            return l[0]
        
        return l 
    
    def RemoveMessage(self, msg = None):
        '''Remove the specified messages from the data base. If no messages are specified, all messages in the data base will be removed'''
        
        if msg == None:
            self._messages = []
            return
        
        if not hasattr(msg,'__iter__'):
            msg = [msg]
        
        untagged_messages = [m for (_, m) in self._messages]
        print ("untagged: ", untagged_messages)
        for m in [m for m in msg if m in untagged_messages]:
            self._messages.remove(m)
