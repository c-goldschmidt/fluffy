import os
import zlib


def _get_crc(filename):
    prev = 0
    for eachLine in open(filename, 'rb'):
        prev = zlib.crc32(eachLine, prev)
    return '%X' % (prev & 0xFFFFFFFF)


def __fluffy_crc():
    fluffy_crc = _get_crc(__file__)
    fluffy_aes_crc = _get_crc(os.path.join(os.path.dirname(__file__), 'lib', 'aes.py'))

    assert fluffy_crc == '{}', "Don't you mess with fluffy!"
    assert fluffy_aes_crc == '{}', "Don't you mess with fluffy!"
