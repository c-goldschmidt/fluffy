import base64
import hashlib

import binascii
from Crypto.Cipher import AES
from Crypto import Random


def try_encode(raw):
    try:
        raw = raw.encode('UTF-8')
    except AttributeError:
        pass
    return raw


def _unpad(enc):
    _substr = enc[-1:]
    if isinstance(_substr, int):
        return enc[:_substr]
    else:
        return enc[:-ord(_substr)]


class AESCipher(object):
    def __init__(self, key):
        self._key = hashlib.sha256(key.encode('UTF-8')).hexdigest()[:32]
        self._key = binascii.a2b_hex(self._key)
        self.block_size = AES.block_size

    def _pad(self, raw):
        pad_size = self.block_size - len(raw) % self.block_size
        pad_char = chr(pad_size)
        return raw + (pad_size * pad_char)

    def encrypt(self, raw, fixed_iv=False):
        raw = self._pad(raw)

        if fixed_iv:
            assert isinstance(fixed_iv, str)
            hex_iv = hashlib.sha256(fixed_iv.encode('UTF-8')).hexdigest()[:32]
            iv = binascii.a2b_hex(hex_iv)
        else:
            iv = Random.new().read(AES.block_size)

        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        enc = cipher.encrypt(raw)

        return base64.b64encode(iv + enc)

    def decrypt(self, enc):
        enc = base64.b64decode(enc)

        iv = enc[:AES.block_size]
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return _unpad(cipher.decrypt(enc[AES.block_size:]).decode('UTF-8'))
