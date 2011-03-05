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

import hashlib
import binascii

class Message:
    """A DMS Message"""
    
    _ID_LENGTH_BYTES = 16
    MAX_TEXT_LENGTH = 160 
    
    def __init__(self, text, signer=None, encrypter=None):
        """Create a message without sender and recipient"""
        
        if text is None or len(text) > Message.MAX_TEXT_LENGTH:
            raise ValueError
         
        self._text = text
        self._sender = None
        self._receiver = None
        
        h = hashlib.sha256()
        h.update(text.encode())
        self._id = h.digest()[- Message._ID_LENGTH_BYTES:] # Least significant bytes
                
    @property
    def id(self):
        """Message Id (bytes)"""
        return self._id
    
    @property    
    def text(self):
        """Message text string (UTF-8 string)"""
        return self._text

    @property
    def sender(self):
        """The sender of the message (bytes)
        
        I.e. the UserId finger print for the sender
        
        """
        
        return self._sender    

    @property
    def receiver(self):
        """The receiver of the message (bytes)
        
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
        return binascii.b2a_hex(self._id).decode()
         
    def __eq__(self, other):
        return isinstance(other, Message) and self._id == other._id
    
    def __ne__(self, other):
        return not self.__eq__(other)