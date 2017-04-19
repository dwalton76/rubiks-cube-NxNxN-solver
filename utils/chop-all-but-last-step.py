#!/usr/bin/env python3

import sys

with open(sys.argv[1], 'r') as fh_read:
    with open('small.txt', 'w') as fh:
        for line in fh_read:
            (state, steps) = line.strip().split(':')
            steps = steps.split()

            if steps:
                fh.write("%s:%s\n" % (state, steps[0]))
            else:
                fh.write("%s:\n" % state)
