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
import dandelion

class IdentityManager:
    def __init__(self, config):
        self._config = config


class RSAKey:
    """Encryption key for the RSA crypto"""
    
    def __init__(self, n, e, d=None):
        """Create an RSA key. 

        The n,e,d are integers and d is optional.
        """
            
        self._n = n
        self._e = e
        self._d = d # Private key
    
    @property
    def is_private(self):
        """Returns true if the key has a private component"""
        return self._d is not None
    
    @property 
    def n(self):
        """n is used as the modulus for both the public and private keys."""
        return self._n
    
    @property
    def e(self):
        """e is the public key exponent."""
        return self._e
    
    @property
    def d(self):
        """d is the private key exponent."""
        return self._d
    
    
class DSAKey:
    """Signing key for the DSA signature"""
    
    def __init__(self, y, g, p, q, x=None):
        """Create a DSA signature key."""
        
        self._y = y
        self._g = g
        self._p = p
        self._q = q
        self._x = x # Private key

    @property
    def is_private(self):
        """Returns true if the key has a private component"""
        return self._x is not None

    @property 
    def y(self):
        """DSA key parameter y"""
        return self._y
    
    @property 
    def g(self):
        """DSA key parameter g"""
        return self._g
    
    @property 
    def p(self):
        """DSA key parameter p"""
        return self._p
    @property 
    def x(self):
        """The private DSA key parameter x"""
        return self._x


class Identity:
    """A class that represents the public identity of a node in the network"""
    
    _FINGERPRINT_LENGTH_BYTES = 12
    
    def __init__(self, dsa_key, rsa_key):
        """Create a new identity instance from the public or private keys."""
        
        self._dsa_key = dsa_key 
        self._rsa_key = rsa_key
        self._fp = None # Lazy evaluation

    @property 
    def fingerprint(self):
        """The identity fingerprint
        
        A bytes string that is a hash of the public components of the keys.
        """
        if self._fp is None: # Lazy hashing
            h = hashlib.sha256()
            h.update(dandelion.util.encode_int(self._rsa_key.n))
            h.update(dandelion.util.encode_int(self._rsa_key.e))
            h.update(dandelion.util.encode_int(self._dsa_key.y))
            h.update(dandelion.util.encode_int(self._dsa_key.g))
            h.update(dandelion.util.encode_int(self._dsa_key.p))
            self._fp = h.digest()[- Identity._FINGERPRINT_LENGTH_BYTES:] 
        
        return self._fp

    @property 
    def rsa_key(self):
        """The RSA key used for encryption"""
        return self._rsa_key

    @property 
    def dsa_key(self):
        """The DSA key used for signing"""
        return self._dsa_key

    def verify(self, msg, signature):
        """Verify a message signature.
        
        The message and signature are bytes strings.
        
        Return true if the message with the specified signature is signed by this identity.
        """         
        return True # Dummy impl.

    def encrypt(self, plaintext):
        """Encrypt a message to this identity.
        
        The plaintext message is a bytes string and the returned encrypted message is a bytes string.
        """
        return plaintext[::-1] # Dummy impl


class PrivateIdentity(Identity):
    """A class that represents the private identity of a node in the network"""
    
    def __init__(self, dsa_key, rsa_key):
        """Create a new identity instance from the private keys."""
        super().__init__(dsa_key, rsa_key)
        
        """Both keys have to have private components"""
        if not self._dsa_key.is_private or not self._rsa_key.is_private:
            raise ValueError 
        
    def sign(self, msg):
        """Sign a message from this identity.
        
        The message is a bytes string. Return a bytes signature.
        """
        return b'1337' # Dummy impl.

    def decrypt(self, ciphertext):
        """Decrypt a message to this signature.
        
        The ciphertext and the returned plaintext are bytes strings.
        """
        return ciphertext[::-1] # Dummy impl.

    @classmethod
    def generate(cls):
        """Factory class method to create a new private identity"""
        
        return PrivateIdentity(DSAKey(0,0,0,0,0), RSAKey(0,0,0)) # Dummy impl.
