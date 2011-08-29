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

import Crypto.Hash
import Crypto.PublicKey.DSA
import Crypto.PublicKey.RSA
import Crypto.Random
import Crypto.Util


from dandelion.util import encode_int, encode_b64_bytes
import hashlib
from oaep_encoder import OAEPEncoder

class IdentityManager:
    def __init__(self, config):
        self._config = config

DSA_KEY_SIZE = 1024
RSA_KEY_SIZE = 2048


class RSA_key:
    """Encryption key for the RSA crypto"""

    def __init__(self, n, e, d=None):
        """Create an RSA key. 

        The n,e,d are integers and d is optional.
        """

        if not isinstance(n, int) or not isinstance(e, int) or (d is not None and not isinstance(d, int)):
            raise TypeError

        self._n = n
        self._e = e
        self._d = d # Private key

    @property
    def is_private(self):
        """Returns true if the key has a private component"""
        return self._d is not None

    def public_key(self):
        """Make a copy of the key without private data"""
        return RSA_key(self.n, self.e)

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


class DSA_key:
    """Signing key for the DSA signature"""

    def __init__(self, y, g, p, q, x=None):
        """Create a DSA signature key."""

        if not isinstance(y, int) or not isinstance(g, int) or not isinstance(p, int) or not isinstance(q, int) or (x is not None and not isinstance(g, int)):
            raise TypeError


        self._y = y
        self._g = g
        self._p = p
        self._q = q
        self._x = x # Private key

    @property
    def is_private(self):
        """Returns true if the key has a private component"""
        return self._x is not None

    def public_key(self):
        """Make a copy of the key without private data"""
        return DSA_key(self.y, self.g, self.p, self.q)

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
    def q(self):
        """DSA key parameter q"""
        return self._q

    @property
    def x(self):
        """The private DSA key parameter x"""
        return self._x


class Identity:
    """A class that represents the public identity of a node in the network"""

    _FINGERPRINT_LENGTH_BYTES = 12

    def __init__(self, dsa_key, rsa_key):
        """Create a new identity instance from the public or private keys."""

        self._dsa_key = Crypto.PublicKey.DSA.construct((dsa_key.y, dsa_key.g, 
                                                        dsa_key.p, dsa_key.q, 
                                                        dsa_key.x))
 
        self._rsa_key = Crypto.PublicKey.RSA.construct((rsa_key.n, rsa_key.e, rsa_key.d))

        self._oaep_encoder = OAEPEncoder()

        self._fp = None # Lazy evaluation

    @property
    def fingerprint(self):
        """The identity fingerprint
        
        A bytes string that is a hash of the public components of the keys.
        """
        if self._fp is None: # Lazy hashing
            h = hashlib.sha256()
            h.update(encode_int(self._rsa_key.n))
            h.update(encode_int(self._rsa_key.e))
            h.update(encode_int(self._dsa_key.y))
            h.update(encode_int(self._dsa_key.g))
            h.update(encode_int(self._dsa_key.p))
            self._fp = h.digest()[-Identity._FINGERPRINT_LENGTH_BYTES:]

        return self._fp

    @property
    def rsa_key(self):
        """The RSA key used for encryption"""
        return RSA_key(self._rsa_key.n, self._rsa_key.e, self._rsa_key.d if self._rsa_key.has_private() else None)

    @property
    def dsa_key(self):
        """The DSA key used for signing"""
        return DSA_key(self._dsa_key.y,  self._dsa_key.g,  self._dsa_key.p,  self._dsa_key.q,  self._dsa_key.x if self._dsa_key.has_private() else None)

    def public_identity(self):
        """Return a copy of this identity without private parts"""
        return Identity(self.dsa_key.public_key(), self.rsa_key.public_key())

    def verify(self, msg, signature):
        """Verify a message signature.
        
        The message is a bytes strings. The signature is a pair of ints.
        
        Return true if the message with the specified signature is signed by this identity.
        """
        return self._dsa_key.verify(self._hash(msg), signature)

    def _hash(self, msg):

        return Crypto.Hash.SHA256.new(msg).digest()

    def encrypt(self, plaintext):
        """Encrypt a message to this identity.
        
        The plaintext message is a bytes string and the returned encrypted message is a bytes string.
        """
        encoded = self._oaep_encoder.encode(plaintext, keybits=RSA_KEY_SIZE)
        return self._rsa_key.encrypt(encoded, b'n/a')[0] # no k value for RSA

    def __str__(self):
        """String conversion is user Base64 encoded fingerprint"""
        return encode_b64_bytes(self.fingerprint).decode()

    def __eq__(self, other):
        return isinstance(other, Identity) and self.fingerprint == other.fingerprint

    def __ne__(self, other):
        return not self.__eq__(other)


class PrivateIdentity(Identity):
    """A class that represents the private identity of a node in the network"""

    def __init__(self, dsa_key, rsa_key):
        """Create a new identity instance from the private keys."""
        super().__init__(dsa_key, rsa_key)

        """Both keys have to have private components"""
        if not self.dsa_key.is_private or not self.rsa_key.is_private:
            raise ValueError

    def sign(self, msg):
        """Sign a message from this identity.
        
        The message is a bytes string. Return a pair of ints (DSA signature).
        """
        k = Crypto.Util.number.getPrime(128, _rnd)
        signature = self._dsa_key.sign(self._hash(msg), k)

        return signature

    def decrypt(self, ciphertext):
        """Decrypt a message to this identity.
        
        The ciphertext and the returned plaintext are bytes strings.
        """

        encoded_msg = self._rsa_key.decrypt(ciphertext)
        return self._oaep_encoder.decode(encoded_msg)

class IdentityInfo:
    """A class that provides additional, local information about an 
       identity, e.g. nickname."""

    def __init__(self, db, id):
        """Create a new identity object with information about id 
           from the specified data base."""
        # TODO Check params...

        self._db = db
        self._id = id

    @property
    def db(self):
        return self._db

    @property
    def id(self):
        return self._id

    def is_private(self):
        """Return true if the identity has private components"""
        return self._id.dsa_key.is_private and self._id.rsa_key.is_private

    @property
    def nick(self):
        """Get the nick of the identity or None if no nick has been set"""
        return self._db.get_nick(self._id.fingerprint)

    @nick.setter
    def nick(self, value):
        """Set the nick of the identity or None to clear the nick"""
        self._db.set_nick(self._id.fingerprint, value)

_rnd = Crypto.Random.new().read

def generate():
    """Factory method to create a new private identity"""

    raw_dsa_key = Crypto.PublicKey.DSA.generate(DSA_KEY_SIZE, _rnd)   # This will take a while...
    dsa_key = DSA_key(raw_dsa_key.y, raw_dsa_key.g, raw_dsa_key.p, raw_dsa_key.q, raw_dsa_key.x)
    
    raw_rsa_key = Crypto.PublicKey.RSA.generate(RSA_KEY_SIZE, _rnd)
    rsa_key = RSA_key(raw_rsa_key.n, raw_rsa_key.e, raw_rsa_key.d)

    return PrivateIdentity(dsa_key, rsa_key)
