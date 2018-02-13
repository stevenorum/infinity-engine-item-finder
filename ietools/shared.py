#!/usr/bin/env python3

import binascii
import json
import os
import sys

def hexlify(bs):
    try:
        return binascii.hexlify(bs).decode("utf-8")
    except:
        return bs

def binlify(bs):
    try:
        return bin(int(hexlify(bs), base=16))[2:].zfill(32)
    except:
        return bs

def word_to_int(bs):
    val = 0
    multiplier = 1
    for b in bs:
        val += multiplier * b
        multiplier *= 256
    return val

def read_x_bytes(f, offset, x):
    here = f.tell()
    f.seek(offset)
    bs = f.read(x)
    f.seek(here)
    return bs

def clean_string(s):
    st = bytearray()
    for c in s:
        if c == 0x00:
            break
        st += bytearray([c])
    return st.decode("utf-8")

def parse_file(filename, parse = lambda x:x):
    print("Parsing file '{}'...".format(filename))
    fsize = os.path.getsize(filename)
    with open(filename, "rb") as f:
        return parse(f, size=fsize)

def jsonifier(obj):
    """https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable"""
    if isinstance(obj, (bytes,bytearray)):
        return "(bytes) 0x{}".format(hexlify(obj))
    else:
        return json.dumps(obj, default=jsonifier)

def unpack_json_bytes(obj):
    if obj == None:
        return obj
    if isinstance(obj, (int, float, bool)):
        return obj
    if isinstance(obj, list):
        return [unpack_json_bytes(e) for e in obj]
    if isinstance(obj, dict):
        return {k:unpack_json_bytes(obj[k]) for k in obj}
    if isinstance(obj, str):
        if obj.startswith("(bytes) 0x"):
            return bytearray.fromhex(obj[10:])
        return obj
    return obj

def loadf(fname):
    with open(fname, 'r') as f:
        return unpack_json_bytes(json.load(f))

def dumpf(obj, fname):
    with open(fname, 'w') as f:
        return json.dump(obj, f, default=jsonifier, indent=2, sort_keys=True)

def dumps(obj):
    return json.dumps(obj, default=jsonifier, indent=2, sort_keys=True)
