#!/usr/bin/env python3

from collections import Counter
import argparse
import logging
import os
import sys

log = logging.getLogger(__name__)

def keep_up_to_max_depth(filename, max_depth):
    filename_new = filename.replace('.txt', '.max-depth')

    with open(filename, 'r') as fh, open(filename_new, 'w') as fh_new:

        for (line_number, line) in enumerate(fh):
            (state, steps) = line.strip().split(':')
            steps = steps.split()

            if len(steps) <= max_depth:
                fh_new.write(line)


if __name__ == '__main__':

    # setup logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='lookup-table filename')
    parser.add_argument('maxdepth', type=int, help='max steps to keep')
    args = parser.parse_args()

    keep_up_to_max_depth(args.filename, args.maxdepth)
