#!/usr/bin/env python3

import binascii
import json
import os
import sys

from ietools.shared import *

DEFAULT_TLK_FILE = "/Applications/Icewind Dale Enhanced Edition.app/Contents/Resources/game/IcewindDale.app/Contents/Resources/lang/en_US/dialog.tlk"

def _parse_tlk_string(f, str_offset):
    desc = f.read(2)
    resname = f.read(8)
    volumevar = f.read(4)
    pitchvar = f.read(4)
    offset = word_to_int(f.read(4))
    length = word_to_int(f.read(4))
    contents = clean_string(read_x_bytes(f, offset + str_offset, length))
    d = {
        "desc":desc,
        "resname":resname,
        "volumevar":volumevar,
        "pitchvar":pitchvar,
        "offset":offset,
        "length":length,
        "contents":contents,
    }
    return d

def _parse_tlk(f, **kwargs):
    header = f.read(8)
    language_id = f.read(2)
    strref_count = word_to_int(f.read(4))
    str_offset = word_to_int(f.read(4))
    strings = []
    for i in range(strref_count):
        s = _parse_tlk_string(f, str_offset)
        strings.append(s)
    return strings

def parse_tlk(filename=None):
    filename = filename if filename else DEFAULT_TLK_FILE
    return parse_file(filename, _parse_tlk)

def main():
    strs = parse_tlk()
    print(strs[6913])

    print(strs[6899])
    print(strs[6901])
    print(strs[6904])
    print(strs[6906])
    print(strs[6908])
    print(strs[6909])
    print(strs[6910])
    print(strs[6911])
    d = {i:strs[i]['contents'] for i in range(len(strs))}
    with open('tlk.json','w') as f:
        json.dump(d, f, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()
