#!/usr/bin/env python3

import logging
import os
import sys


def convert_to_binary(filename):
    filename_new = filename.replace('.txt', '.cost-only.txt')
    max_state_binary_str = None
    foo = {}
    max_state_int = None

    with open(filename, 'r') as fh:
        for (line_number, line) in enumerate(fh):
            (state, steps) = line.strip().split(':')
            steps = steps.split()

            state_int = int(state, 16)

            if steps[0].isdigit():
                steps_len = int(steps[0])
            else:
                steps_len = len(steps)

            foo[state_int] = steps_len
            max_state_int = state_int
            #log.info("state %s is %s, state_rank %d, steps_len %d" % (state, state_binary_str, state_rank, steps_len))

            #if line_number == 1000:
            #    sys.exit(0)

    with open(filename_new, 'w') as fh:
        for index in range(0, max_state_int + 1):
            steps_len = foo.get(index, 0)
            fh.write(str(steps_len))


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("ERROR: To use './convert-to-cost-only.py FILENAME'")
        sys.exit(1)

    filename = sys.argv[1]

    if not os.path.isfile(filename):
        print("ERROR: %s does not exist" % filename)
        sys.exit(1)

    # setup logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    convert_to_binary(filename)
