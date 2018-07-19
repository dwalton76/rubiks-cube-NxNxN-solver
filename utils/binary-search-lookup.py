#!/usr/bin/env python3

from pprint import pformat
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


def find_first_last(linecount, cache, b_state_to_find):
    cache.sort()
    first = 0
    last = linecount - 1
    to_delete = 0
    #log.info("find_first_last for %s with cache\n%s" % (b_state_to_find, pformat(cache)))

    for (offset, state) in cache:

        if state < b_state_to_find:
            to_delete += 1
            first = offset
            #log.info("state %s < b_state_to_find %s, to_delete %d, first %s" % (state, b_state_to_find, to_delete, first))

        elif state == b_state_to_find:
            first = offset
            last = offset
            #log.info("state %s == b_state_to_find %s, to_delete %d, first %s, last %s" % (state, b_state_to_find, first, last))
            break

        else:
            last = offset
            #log.info("state %s > b_state_to_find %s, last %s" % (state, b_state_to_find, last))
            break

    to_delete -= 1

    if to_delete > 0:
        cache = cache[to_delete:]

    #log.info("find_first_last for %s, deleted %s, first %s, last %s, cache\n%s" % (b_state_to_find, to_delete, first, last, pformat(cache)))
    return (cache, first, last)


def binary_search_multiple(fh, width, state_width, linecount, states_to_find):
    global seek_count
    states_to_find.sort()
    cache = []
    results = []
    #log.info("\n\n\n\n\n\n")
    #log.info("binary_search_multiple called for %s" % pformat(states_to_find))

    for state_to_find in states_to_find:
        b_state_to_find = bytearray(state_to_find, encoding='utf-8')

        if cache:
            (cache, first, last) = find_first_last(linecount, cache, b_state_to_find)
        else:
            first = 0
            last = linecount - 1

        #log.info("state_to_find %s, first %s, last %s, cache\n%s" % (state_to_find, first, last, pformat(cache)))
        while first <= last:
            midpoint = int((first + last)/2)
            fh.seek(midpoint * width)
            seek_count += 1

            # Only read the 'state' part of the line (for speed)
            b_state = fh.read(state_width)

            # We did a read...reads are expensive...cache the read
            cache.append((midpoint, b_state))

            if b_state_to_find < b_state:
                last = midpoint - 1

            # If this is the line we are looking for, then read the entire line
            elif b_state_to_find == b_state:
                fh.seek(midpoint * width)
                line = fh.read(width)
                (_, value) = line.decode('utf-8').rstrip().split(':')
                results.append(value)
                break

            else:
                first = midpoint + 1
        else:
            results.append(None)

    return results


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

        if ',' in key:
            #for x in key.split(','):
            #    seek_count = 0
            #    value = binary_search(fh, width, state_width, linecount, x)
            #    print("key %s value is %s (took %d seeks)" % (x, value, seek_count))

            keys = key.split(',')
            values = binary_search_multiple(fh, width, state_width, linecount, keys)
            #log.info("keys: %s" % pformat(keys))
            #log.info("values: %s" % pformat(values))

            for (key, value) in zip(keys, values):
                print("key %s value is %s" % (key, value))
            print("Took %d seeks" % seek_count)

        else:
            value = binary_search(fh, width, state_width, linecount, key)
            print("key %s value is %s (took %d seeks)" % (key, value, seek_count))

        log.info("search end")
