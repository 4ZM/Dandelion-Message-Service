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

import base64
import binascii

def encode_b64_bytes(bstr):
    """bytes to Base64 encoding"""
    if not isinstance(bstr, bytes) and not isinstance(bstr, bytearray):
        raise TypeError    
    
    return base64.b64encode(bstr)
    
def decode_b64_bytes(bstr):
    """Base64 to bytes decoding"""
    if not isinstance(bstr, bytes) and not isinstance(bstr, bytearray):
        raise TypeError    

    return base64.b64decode(bstr)

def encode_b64_int(x):
    """int to Base64 encoding"""
    return encode_b64_bytes(encode_int(x))

def decode_b64_int(bstr):
    """Base64 str to int decoding""" 
    return decode_int(decode_b64_bytes(bstr))

def encode_int(x):
    """int to bytes conversion"""
    if not isinstance(x, int):
        raise TypeError
    
    if x < 0:
        raise ValueError
    
    hstr = '{0:X}'.format(x)
    
    if len(hstr) % 2 != 0:
        hstr = ''.join(['0', hstr])

    return binascii.a2b_hex(hstr.encode())

def decode_int(bstr):
    """bytes to int conversion"""
    if not isinstance(bstr, bytes) and not isinstance(bstr, bytearray):
        raise TypeError    

    return int(binascii.b2a_hex(bstr), 16)
