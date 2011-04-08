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

import hashlib
import dandelion.util

class Message:
    """A DMS Message"""
    
    _ID_LENGTH_BYTES = 12
    MAX_TEXT_LENGTH = 140 
    
    def __init__(self, text, receiver_fp=None, sender_fp=None, signature=None):
        """Create a message. Sender and receiver are optional.
        
        Typically, the factory method create will be used.
        """
        
        if text is None: # Must have content
            raise ValueError
        
        if receiver_fp is None and len(text) > Message.MAX_TEXT_LENGTH: # Limit only applies to plaintext data
            raise ValueError

        # Must have both sender and signature if it has one
        if (sender_fp is None and signature is not None) or (sender_fp is not None and signature is None):
            raise ValueError             
        
        self._id = None # Lazy evalutation
        self._text = text
        self._receiver_fp = receiver_fp
        self._sender_fp = sender_fp
        self._signature = signature
                
    @property
    def id(self):
        """Message Id (bytes)"""

        if self._id is None: # Lazy hashing
            h = hashlib.sha256()
            h.update(self._text.encode())
            
            if self._receiver_fp is not None:
                h.update(self._receiver_fp)
            
            if self._sender_fp is not None:
                h.update(self._sender_fp)
                h.update(self._signature)
            
            self._id = h.digest()[- Message._ID_LENGTH_BYTES:] # Least significant bytes

        return self._id
    
    @property    
    def text(self):
        """Message text string UTF-8 string or bytes if the message is encrypted"""
        return self._text

    @property
    def receiver(self):
        """The receiver of the message (bytes)
        
        I.e. the UserId finger print for the receiver
        """
        return self._receiver_fp

    @property
    def sender(self):
        """The sender of the message (bytes)
        
        I.e. the UserId finger print for the sender
        """
        return self._sender_fp

    @property 
    def signature(self):
        """Message signature"""
        return self._signature 
        
    @property
    def has_sender(self):
        """Returns true if the message has a sender"""
        return self._sender_fp is not None
        
    @property
    def has_receiver(self):
        """Returns true if the message has a receiver"""
        return self._receiver_fp is not None

    @classmethod         
    def create(cls, text, sender=None, receiver=None):
        """Factory method for Messages"""
        
        if sender is None and receiver is None:
            return Message(text)
        elif sender is None and receiver is not None:
            return Message(receiver.encrypt(text), receiver_fp=receiver.fingerprint)
        elif sender is not None and receiver is None:
            sig = sender.sign(text.encode())
            return Message(text, sender_fp=sender.fingerprint, signature=sig)
        else: # sender and receiver
            text = receiver.encrypt(text)
            sig = sender.sign(text.encode())
            return Message(text, receiver_fp=receiver.fingerprint, sender_fp=sender.fingerprint, signature=sig)
            
    def __str__(self):
        """String conversion is message ID as hex"""
        return dandelion.util.encode_b64_bytes(self.id).decode()
         
    def __eq__(self, other):
        return isinstance(other, Message) and self.id == other.id
    
    def __ne__(self, other):
        return not self.__eq__(other)