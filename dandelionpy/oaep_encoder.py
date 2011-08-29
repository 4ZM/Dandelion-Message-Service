"""
OAEP Encoder from: 
http://japrogbits.blogspot.com/2011/02/using-encrypted-data-between-python-and.html

Modified for Python 3k compatibility by Anders Sundman, 2011
"""

import Crypto.Random
import hashlib
import struct

class PKCS1Error(RuntimeError):
    '''
    Base class for PKCS1 encoding/decoding errors.
    Error of this or derived classes should be caught
    by the calling code and then a generic error message
    should be returned to the caller.
    '''
    pass

class DecoderError(PKCS1Error):
    '''
    Raised when a decoding error has been detected.
    '''
    pass

class EncoderError(PKCS1Error):
    '''
    Raise when an encoding error has been detected.
    '''
    pass


class PKCSAuxiliary(object):
    '''
    Auxiliary functions used in RFC 2437
    '''

    def __init__(self):
        self._hash_length = None

    @property
    def hash_length(self):
        if not self._hash_length:
            hasher = self.create_hasher()
            self._hash_length = hasher.digest_size

        return self._hash_length

    @staticmethod
    def create_hasher():
        return hashlib.sha1()

    @staticmethod
    def compute_hash(data, hex_digest=False):
        hasher = PKCSAuxiliary.create_hasher()
        hasher.update(data)
        if hex_digest:
            return hasher.hex_digest()
        else:
            return hasher.digest()

    def mgf(self, seed, length):
        '''
        RFC 2437 page 28 MFG1
        '''
        counter = 0
        raw_mask = bytearray()
        limit = length / self.hash_length

        while counter <= limit:
            C = self.i2osp(counter)
            raw_mask.extend(self.compute_hash(seed + C))
            counter += 1

        if len(raw_mask) < length:
            raise PKCS1Error("MGF: mask too long")

        mask = raw_mask[:length]
        return mask

    def i2osp(self, x):
        '''
        RFC 2437 page 6 I2OSP
        Special case where length = 4
        '''
        if x > 256 ** 4:
            raise PKCS1Error("I2OSP: integer too large")

        sp = (
            int((x >> 24) & 0xff),
            int((x >> 16) & 0xff),
            int((x >> 8) & 0xff),
            int((x >> 0) & 0xff)
        )

        return struct.pack('BBBB', *sp)

    @staticmethod
    def xor(a, b):
        '''
        RFC 2437  bitwise exclusive-or of two octet strings.
        page 23
        '''
        if len(a) != len(b):
            raise PKCS1Error("XOR: invalid input lengths")

        output = bytearray(len(a))
        for i in range(len(a)):
            output[i] = a[i] ^ b[i]

        return output


class OAEPEncoder(PKCSAuxiliary):
    '''
    RFC 2437 9.1.1 EME-OAEP PKCS1-v2.0
    9.1.1.1 EME-OAEP-ENCODE
    9.1.1.2 EME-OAEP-DECODE
    '''

    def __init__(self):
        super(OAEPEncoder, self).__init__()


    def encode(self, msg, salt=b'', keybits=1024):
        k = keybits // 8
        if len(msg) > (k - 2 - 2 * self.hash_length):
            raise EncoderError("EME-OAEP: message too long")

        emLen = k - 1
        if (emLen < (2 * self.hash_length + 1) or
            len(msg) > (emLen - 1 - 2 * self.hash_length)):
            raise EncoderError("EME-OAEP: message too long")

        pslen = emLen - len(msg) - 2 * self.hash_length - 1

        zfill = bytes([0 for _ in range(pslen)])

        shash = self.compute_hash(salt)
        dbout = b''.join([shash, zfill, b'\x01', msg])

        seed = Crypto.Random.get_random_bytes(self.hash_length)
        assert len(seed) == self.hash_length

        dbMask = self.mgf(seed, emLen - self.hash_length)
        maskedDB = self.xor(dbout, dbMask)
        seedMask = self.mgf(maskedDB, self.hash_length)
        maskedSeed = self.xor(seed, seedMask)
        
        emout = b''.join([maskedSeed, maskedDB])

        return emout


    def decode(self, emsg, salt=b''):
        if len(emsg) < (2 * self.hash_length + 1):
            raise DecoderError("EME-OAEP: decoding error")

        maskedSeed = emsg[:self.hash_length]
        maskedDB = emsg[self.hash_length:]
        seedMask = self.mgf(maskedDB, self.hash_length)
        seed = self.xor(maskedSeed, seedMask)
        dbMask = self.mgf(seed, len(emsg) - self.hash_length)
        db = self.xor(maskedDB, dbMask)
        shash = self.compute_hash(salt)

        db_shash = db[:self.hash_length]
        if db_shash != shash:
            raise DecoderError("EME-OAEP: decoding error")

        index = db.find(b'\x01', self.hash_length)
        if - 1 == index:
            raise DecoderError("EME-OAEP: decoding error")

        return db[index + 1:]
    
