import hashlib
import binascii

class Message:
    '''A Message'''
    
    ID_LENGTH_BYTES = 16
    MAX_TEXT_LENGTH = 160 
    
    def __init__(self, text, signer=None, encrypter=None):
        '''Create a message without sender and recipient'''
        
        if text == None or len(text) > Message.MAX_TEXT_LENGTH:
            raise ValueError
         
        self._text = text
        self._sender = None
        self._receiver = None
        
        h = hashlib.sha256()
        h.update(text)
        self._id = h.digest()[-Message.ID_LENGTH_BYTES:]
                
    def GetId(self):
        '''Returns the message Id'''
        return self._id
        
    def GetText(self):
        '''Get the text message string'''
        return self._text
        
    def HasSender(self):
        '''Returns true if the message has a sender'''
        return self._sender != None
        
    def HasReceiver(self):
        '''Returns true if the message has a receiver'''
        return self._receiver != None
        
    def GetSender(self):
        '''Returns the sender field of the message (i.e. the UserId fingerprint for the sender)'''
        return self._sender    

    def GetReceiver(self):
        '''Returns the receiver field of the message (i.e. the UserId fingerprint for the receiver)'''
        return self._receiver
         
    def __str__(self):
        '''String conversion ID-hex'''
        return binascii.b2a_hex(self._id)
         
    def __eq__(self, other):
        return isinstance(other, Message) and self._id == other._id
    
    def __ne__(self, other):
        return not self.__eq__(other)