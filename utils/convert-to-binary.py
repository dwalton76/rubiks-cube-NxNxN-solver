#!/usr/bin/env python3

import argparse
import logging


def convert_text_to_binary_555(filename):
    line_number = 0
    num_of_bits = 54

    with open(filename, 'r') as fh:
        for line in fh:
            (state, steps) = line.rstrip().split(':')
            state_hex = int(state, 16)

            if state_hex.endswith('L'):
                state_hex = state_hex[:-1]


            state_bin = bin(int(state, 16))[2:].zfill(num_of_bits)

            line_number += 1

            if line_number == 10:
                break


if __nmae__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, default=None)
    args = parser.parse_args()


    convert_text_to_binary_555(args.filename)
