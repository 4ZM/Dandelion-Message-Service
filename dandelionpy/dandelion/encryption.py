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

import dandelion.util
import Crypto.Random

from Crypto.Cipher import AES

def symetric_encrypt(key, plaintext):
    """
    """

    if len(key) == 0:
        raise ValueError
     
    padded_plaintext = _append_padding(plaintext, 16)
    encobj = AES.new(_append_padding(key, 16, 0), AES.MODE_ECB)
    ciphertext = encobj.encrypt(padded_plaintext)
    
    return ciphertext
    
def symetric_decrypt(key, ciphertext):
    """"""
    
    encobj = AES.new(_append_padding(key, 16, 0), AES.MODE_ECB)
    padded_plaintext = encobj.decrypt(ciphertext)
    plaintext = _strip_padding(padded_plaintext)

    return plaintext

def _append_padding(bstr, blocksize, pad_value=None):
    """Add padding to the back of a message. If pad_value is specified (1 byte) 
    this value is used as padding, otherwise random data will be used.
    
    This will make its length divisible by the blocksize. Max blocksize is 255.
    
    Padding format: bstr | pad_value or random data | 1byte padding length.
    """

    if not isinstance(bstr, bytes) and not isinstance(bstr, bytearray):
        raise TypeError
    
    if not 1 < blocksize < 256:
        raise ValueError

    if pad_value is not None and not 0 <= pad_value < 256:
        raise ValueError

    data_length = len(bstr) + 1 # Add one for padding length field 
    padding_length = blocksize - (data_length % blocksize)

    if pad_value is None:
        padding = Crypto.Random.get_random_bytes(padding_length)
    else:
        padding = bytes([pad_value for _ in range(padding_length)])

    return b''.join([bstr, padding, bytes([padding_length])])
        
def _strip_padding(padded_bstr):
    """Remove the padding added with the _append_padding function"""
    
    if not isinstance(padded_bstr, bytes) and not isinstance(padded_bstr, bytearray):
        raise TypeError
    
    if len(padded_bstr) < 1:
        raise ValueError 

    padding_bytes = padded_bstr[len(padded_bstr)-1]
    return padded_bstr[: - (padding_bytes + 1)]
