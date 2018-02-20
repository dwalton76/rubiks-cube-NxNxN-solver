#!/usr/bin/env python3

import logging
import os
import sys

seek_count = 0


def binary_search(fh, width, state_width, linecount, state_to_find):
    global seek_count
    first = 0
    last = linecount - 1
    b_state_to_find = bytearray(state_to_find, encoding='utf-8')

    while first <= last:
        midpoint = int((first + last)/2)
        fh.seek(midpoint * width)
        seek_count += 1

        # Only read the 'state' part of the line (for speed)
        b_state = fh.read(state_width)

        if b_state_to_find < b_state:
            last = midpoint - 1

        # If this is the line we are looking for, then read the entire line
        elif b_state_to_find == b_state:
            fh.seek(midpoint * width)
            line = fh.read(width)
            (_, value) = line.decode('utf-8').rstrip().split(':')
            return value

        else:
            first = midpoint + 1

    return None


def get_file_vitals(filename):
    """
    Return the width of each line, the width of the state, and the number of lines in the file
    """
    size = os.path.getsize(filename)

    # Find the state_width for the entries in our .txt file
    with open(filename, 'r') as fh:
        first_line = next(fh)
        width = len(first_line)
        (state, steps) = first_line.split(':')
        state_width = len(state)
        linecount = int(size/width)
        return (width, state_width, linecount)


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("ERROR: To use './binary-search-lookup.py FILENAME KEY'" % input_filename)
        sys.exit(1)

    filename = sys.argv[1]
    key = sys.argv[2]

    if not os.path.isfile(filename):
        print("ERROR: %s does not exist" % filename)
        sys.exit(1)

    # setup logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    (width, state_width, linecount) = get_file_vitals(filename)

    with open(filename, 'rb') as fh:
        log.info("search start")
        value = binary_search(fh, width, state_width, linecount, key)
        print("key %s value is %s (took %d seeks)" % (key, value, seek_count))
        log.info("search end")
