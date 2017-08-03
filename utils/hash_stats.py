#!/usr/bin/env python

import sys
buckets = 0.0
empty_buckets = 0
max_collisions = 0
total_entries = 0

with open(sys.argv[1], 'r') as fh:
    for line in fh:
        line = line.strip()

        if line:
            entries = len(line.split(','))
            if entries > max_collisions:
                max_collisions = entries
            total_entries += entries
            buckets += 1
        else:
            empty_buckets += 1

print("%d buckets" % buckets)
print("%d empty buckets" % empty_buckets)
print("%d max in bucket" % max_collisions)
print("%d entries" % total_entries)
print("%s avg per bucket" % (total_entries/buckets))

