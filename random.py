#!/usr/bin/env python3

import json
import sys

class ByteBlob(object):
    def __init__(self, bstream, size):
        self._bytes = bstream.read(size)
        pass
    pass

class CharArray(ByteBlob):
    def __init__(self, bstream, size):
        super().__init__(bstream, size)
        self._text = self._bytes.decode("utf-8")
        pass
    pass

class ResRef(ByteBlob):
    def __init__(self, bstream):
        super().__init__(bstream, 8)
        pass
    pass

class Word(ByteBlob):
    def __init__(self, bstream):
        super().__init__(bstream, 2)
        self._bytes = reversed(self._bytes)
        pass
    pass

class DWord(ByteBlob):
    def __init__(self, bstream):
        super().__init__(bstream, 4)
        self._bytes = reversed(self._bytes)
        pass
    pass

def parse_header(f):
    signature = f.read(4)
    version = f.read(4)

with open(sys.argv[1], "rb") as f:
    header = parse_header(f)
    content = 
