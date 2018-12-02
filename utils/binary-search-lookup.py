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


def binary_search_list(states, b_state_to_find):
    first = 0
    linecount = len(states)
    last = linecount - 1
    #b_state_to_find = bytearray(state_to_find, encoding='utf-8')

    while first <= last:
        midpoint = int((first + last)/2)
        b_state = bytearray(states[midpoint], encoding='utf-8')

        if b_state_to_find < b_state:
            last = midpoint - 1

        # If this is the line we are looking for, then read the entire line
        elif b_state_to_find == b_state:
            return (True, midpoint)

        else:
            first = midpoint + 1

    return (False, first)


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
    index = 0
    skip_count = 0
    looked_for_count = 0

    fh.seek(0)
    b_state_first = fh.read(state_width)

    fh.seek((linecount - 1) * width)
    b_state_last = fh.read(state_width)

    (_, starting_index) = binary_search_list(states_to_find, b_state_first)
    log.info("start at index %d" % starting_index)

    for state_to_find in states_to_find[starting_index:]:
        b_state_to_find = bytearray(state_to_find, encoding='utf-8')

        if b_state_to_find < b_state_first:
            #log.info("SKIP %s < %s" % (b_state_to_find, b_state_first))
            skip_count += 1
            index += 1
            continue
        elif b_state_to_find > b_state_last:
            log.info("DONE %s > %s" % (b_state_to_find, b_state_last))
            break

        if cache:
            (cache, first, last) = find_first_last(linecount, cache, b_state_to_find)
        else:
            first = 0
            last = linecount - 1

        looked_for_count += 1
        index += 1

        #log.info("state_to_find %s, first %s, last %s, cache %d entries" % (state_to_find, first, last, len(cache)))
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

    log.info("%d keys were less than 1st entry" % skip_count)
    log.info("%d keys were between 1st and last entry" % looked_for_count)
    log.info("%d keys were after last entry" % (len(states_to_find) - index))
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

    if os.path.isfile(key):
        keys = []
        with open(key, 'r') as fh:
            for line in fh:
                line = line.strip()
                keys.append(line)
    elif ',' in key:
        keys = key.split(',')
        key = None
    else:
        keys = None
        
    # setup logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    (width, state_width, linecount) = get_file_vitals(filename)

    with open(filename, 'rb') as fh:
        log.info("search start")

        if keys:
            log.info("finding {:,} keys".format(len(keys)))
            #for x in key.split(','):
            #    seek_count = 0
            #    value = binary_search(fh, width, state_width, linecount, x)
            #    print("key %s value is %s (took %d seeks)" % (x, value, seek_count))

            values = binary_search_multiple(fh, width, state_width, linecount, keys)
            #log.info("keys: %s" % pformat(keys))
            #log.info("values: %s" % pformat(values))

            for (key, value) in zip(keys, values):
                #if value is not None:
                #    print("key %s value is %s" % (key, value))
                print("key %s value is %s" % (key, value))
            print("Took %d seeks" % seek_count)

        else:
            value = binary_search(fh, width, state_width, linecount, key)
            print("key %s value is %s (took %d seeks)" % (key, value, seek_count))

        log.info("search end")
