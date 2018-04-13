#!/usr/bin/env python3

import logging
import os
import sys

log = logging.getLogger(__name__)


def convert_to_binary(filename):
    filename_new = filename.replace('.txt', '.cost-only.txt')
    prev_state_int = None

    with open(filename, 'r') as fh:
        with open(filename_new, 'w') as fh_new:
            for (line_number, line) in enumerate(fh):
                (state, steps) = line.strip().split(':')
                steps = steps.split()
    
                state_int = int(state, 16)

                # Add 0s for every state from prev_state_int to state_int
                if prev_state_int is None:
                    zeroes_between_prev_and_now = state_int
                else:
                    zeroes_between_prev_and_now = (state_int - prev_state_int - 1)

                if zeroes_between_prev_and_now > 0:
                    zeroes_between_prev_and_now = zeroes_between_prev_and_now * '0'
                    fh_new.write(zeroes_between_prev_and_now)

                # Write the steps_len
                if steps[0].isdigit():
                    steps_len = int(steps[0])
                else:
                    steps_len = len(steps)

                # We save the steps_len as a single hex character so cap it at 15
                if steps_len > 15:
                    log.warning("steps_len %d is > 15...saving as 15" % steps_len)
                    steps_len = 15

                # Convert steps_len to hex and ignore the 0x part of the string
                steps_len = hex(steps_len)[2]
                fh_new.write(steps_len)
                prev_state_int = state_int


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
