#!/usr/bin/env python3

from bloomfilter import BloomFilter, BloomFilterFromFile
import logging
import os
import sys


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))


filename = sys.argv[1]
filename_bf = filename + '.bf'
target = sys.argv[2]

if not os.path.exists(filename):
    print("ERROR: %s does not exist" % filename)
    sys.exit(1)

if not os.path.exists(filename_bf):
    print("ERROR: %s does not exist" % filename_bf)
    sys.exit(1)

'''
line_count = 0
log.info("find line_count")
with open(filename, 'r') as fh:
    for line in fh:
        line_count += 1
log.info("line_count is %d" % line_count)

n = line_count # no of items to add
p = 0.10 # false positive probability

bf = BloomFilter(n, p, filename)
bf.load_bit_array()
'''

bf = BloomFilterFromFile(735471, filename)

'''
with open(filename, 'r') as fh:
    for line in fh:
        (state, steps) = line.split(':')
        bf.add(state)

bf.save_bit_array()
'''

if bf.check(target):
    print("%s may be in the file" % target)
else:
    print("%s is not in the file" % target)
