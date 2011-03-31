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
import dandelion.util
import hashlib


class IdentityManager:
    def __init__(self, config):
        self._config = config

class RSAKey:
    def __init__(self, n, e, d=None):
        self._n = n
        self._e = e
        self._d = d # Private key
    
    @property
    def is_private(self):
        return self._d is not None
    
    def encode(self):
        return [dandelion.util.encode_int(self._n), 
                dandelion.util.encode_int(self._e)]
    
class DSAKey:
    def __init__(self, y, g, p, q, x=None):
        self._y = y
        self._g = g
        self._p = p
        self._q = q
        self._x = x # Private key

    @property
    def is_private(self):
        return self._x is not None

    def encode(self):
        return [dandelion.util.encode_int(self._y),
                dandelion.util.encode_int(self._g),
                dandelion.util.encode_int(self._p), 
                dandelion.util.encode_int(self._q)]

    

class Identity:
    
    _FP_LENGTH_BYTES = 18
    
    def __init__(self, key_pair):
        self._dsa_key, self._rsa_key = key_pair
        
        h = hashlib.sha256()
        map(h.update, self._dsa_key.encode())
        map(h.update, self._rsa_key.encode())
        self._fp = h.digest()[- Identity._FP_LENGTH_BYTES:] 

    @property 
    def fingerprint(self):
        return self._fp

    def verify(self, msg, signature):
        return True

    def encrypt(self, plaintext):
        return plaintext

    def export_id(self):
        return (self._dsa_key, self._rsa_key)
    
    @classmethod
    def import_id(cls, key_pair):
        dsa_key, rsa_key = key_pair
        
        if dsa_key.is_private and rsa_key.is_private:
            return PrivateIdentity(key_pair)
        elif not dsa_key.is_private and not rsa_key.is_private:
            return Identity(key_pair)
        else:
            raise ValueError # Can't mix public and private key parts

class PrivateIdentity(Identity):
    
    def __init__(self, key_pair):
        super().__init__(key_pair)
        
        """Both keys have to have private components"""
        if not self._dsa_key.is_private or not self._rsa_key.is_private:
            raise ValueError 
        
    def sign(self, msg):
        return b'1337'

    def decrypt(self, ciphertext):
        return ciphertext

    @classmethod
    def generate(cls):
        return PrivateIdentity((DSAKey(0,0,0,0,0), RSAKey(0,0,0)))
