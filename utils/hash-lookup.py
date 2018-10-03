#!/usr/bin/env python3

from pyhashxx import hashxx
import os
import sys

if len(sys.argv) != 4:
    print("ERROR: To use './hash-lookup.py FILENAME KEY BUCKETCOUNT'")
    sys.exit(1)

filename = sys.argv[1]
key = sys.argv[2]
bucketcount = int(sys.argv[3])

if not os.path.isfile(filename):
    print("ERROR: %s does not exist" % filename)
    sys.exit(1)

hash_raw = hashxx(key.encode('utf-8'))
hash_index = int(hash_raw % bucketcount)

with open(filename, 'rb') as fh:
    content = fh.read()
    cost = int(chr(content[hash_index]), 16)

    print("hash_raw: %s" % hash_raw)
    print("hash_index: %s" % hash_index)
    print("cost: %s" % cost)
