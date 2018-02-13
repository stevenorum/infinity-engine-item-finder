#!/usr/bin/env python3

import binascii
import json
import os
import sys

from ietools.shared import *

DEFAULT_KEY_FILE = "/Applications/Icewind Dale Enhanced Edition.app/Contents/Resources/game/IcewindDale.app/Contents/Resources/chitin.key"

def parse_key_bif(f, index=-1):
    # I'll deal with this later.
    # f.read(12)
    length = word_to_int(f.read(4))
    name_offset = word_to_int(f.read(4))
    name_length = word_to_int(f.read(2))
    name = clean_string(read_x_bytes(f, name_offset, name_length))
    throwaway = f.read(2)
    bif = {
        "name":name,
        "length":length,
        "index":index
    }
    return bif
    # return bif if name else None

def parse_key_res(f):
    res = {}
    res["name"] = clean_string(f.read(8))
    res["type"] = hexlify(f.read(2))
    res["location"] = f.read(4)
    res["bin_location"] = bin(int(hexlify(res["location"]), base=16))[2:].zfill(32)
    return res

def parse_key(f):
    f.seek(8)
    bif_count = word_to_int(f.read(4))
    res_count = word_to_int(f.read(4))
    bif_offset = word_to_int(f.read(4))
    res_offset = word_to_int(f.read(4))
    biflist = []
    reslist = []
    f.seek(bif_offset)
    for i in range(bif_count):
        bif = parse_key_bif(f, index=i)
        if bif:
            biflist.append(bif)
    f.seek(res_offset)
    for i in range(res_count):
        reslist.append(parse_key_res(f))
    for res in reslist:
        # if "AROW".encode("utf-8") in res["name"]:
        if res["type"] == "ed03" and "arow" in res["name"].lower():
            print(res["name"])
            print(hexlify(res["location"]))
            print(res["bin_location"])
    return biflist, reslist

def parse_chitin(filename=None):
    filename = filename if filename else DEFAULT_KEY_FILE
    return parse_file(filename, _parse_key)



def main():
    biflist, reslist = parse_chitin()
    resmap = {}
    for resource in reslist:
        if resource["type"] == "ed03":
            print("{} : {}".format(resource["name"], word_to_int(resource["location"][0:2])))
            resmap[resource["name"]] = str(word_to_int(resource["location"][0:2]))
    with open('item_codes.json', 'w') as f:
        json.dump(resmap, f, indent=2, sort_keys=True)
    for bif in biflist:
        fname = os.path.join(directory, bif["name"])
        print(bif["index"])
        bif["contents"] = parse_file(fname)


if __name__ == "__main__":
    main()
