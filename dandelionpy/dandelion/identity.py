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


class IdentityManager:
    def __init__(self, config):
        self._config = config

class RSAKey:
    def __init__(self, n, e, d=None):
        self.n = n
        self.e = e
        self.d = d # Private key
    
class DSAKey:
    def __init__(self, y, g, p, q, x=None):
        self.y = y
        self.g = g
        self.p = p
        self.q = q
        self.x = x # Private key



class Identity:
    
    def __init__(self, DSAKey, RSAKey):
        pass
    
    @property 
    def fingerprint(self):
        return 0
    
    
    
    def sign(self, message):
        return ''
    
    def verify(self, message, signature):
        return True
    
    
    def encrypt(self, plaintext):
        return plaintext

    def decrypt(self, ciphertext):
        return ciphertext

    @classmethod
    def generate(cls):
        return Identity(DSAKey(0,0,0,0), RSAKey(0,0))
        
    @classmethod
    def export_id(cls):
        pass
    
    @classmethod
    def import_id(cls):
        pass
