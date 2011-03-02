import hashlib
import binascii

class Message:
    """A DMS Message"""
    
    ID_LENGTH_BYTES = 16
    MAX_TEXT_LENGTH = 160 
    
    def __init__(self, text, signer=None, encrypter=None):
        """Create a message without sender and recipient"""
        
        if text is None or len(text) > Message.MAX_TEXT_LENGTH:
            raise ValueError
         
        self._text = text
        self._sender = None
        self._receiver = None
        
        h = hashlib.sha256()
        h.update(text)
        self._id = h.digest()[- Message.ID_LENGTH_BYTES:] # Least significant bytes
                
    @property
    def id(self):
        """Message Id"""
        return self._id
    
    @property    
    def text(self):
        """Message text string"""
        return self._text

    @property
    def sender(self):
        """The sender of the message
        
        I.e. the UserId finger print for the sender
        
        """
        
        return self._sender    

    @property
    def receiver(self):
        """The receiver of the message
        
        I.e. the UserId finger print for the receiver
        
        """
        
        return self._receiver
    
        
    def has_sender(self):
        """Returns true if the message has a sender"""
        return self._sender is not None
        
    def has_receiver(self):
        """Returns true if the message has a receiver"""
        return self._receiver is not None
        
     
    def __str__(self):
        """String conversion is message ID as hex"""
        return binascii.b2a_hex(self._id)
         
    def __eq__(self, other):
        return isinstance(other, Message) and self._id == other._id
    
    def __ne__(self, other):
        return not self.__eq__(other)