#!/usr/bin/env python3

from collections import Counter
import argparse
import logging
import os
import sys

log = logging.getLogger(__name__)

def permutation_rank(word):
    """
    Based on
    https://github.com/thedavidwells/Lexicographical-Word-Rank/blob/master/word_rank.py

    >>> permutation_rank("BBGGGG")
    0

    >>> permutation_rank("GBGGBG")
    7

    >>> permutation_rank("GGGGBB")
    14

    >>> permutation_rank("GGBGBBGBBBGBBBBGGGGGBBBBBGGGGBGGGBGGBGBB")
    114581417273
    """
    rank = 0
    permutations = 1

    word_length = len(word)
    myCounter = Counter()

    for i in range(word_length):
        permutationContainer = word[((word_length - 1) - i)]
        myCounter[permutationContainer] += 1

        for j in myCounter:

            if (j < permutationContainer):
                rank += (permutations * myCounter[j] // myCounter[permutationContainer])

        permutations = ((permutations * (i + 1)) // myCounter[permutationContainer])

    return rank


def convert_to_cost_only(filename, use_permutation_rank):
    filename_new = filename.replace('.txt', '.cost-only.txt')
    prev_state_int = None
    first_permutation_rank = None

    with open(filename, 'r') as fh:
        with open(filename_new, 'w') as fh_new:
            for (line_number, line) in enumerate(fh):
                (state, steps) = line.strip().split(':')
                steps = steps.split()

                if use_permutation_rank:
                    state_int = permutation_rank(state)
                else:
                    state_int = int(state, 16)

                if first_permutation_rank is None:
                    first_permutation_rank = state_int

                #state_int -= first_permutation_rank
                #log.info("%s: permutation rank %d" % (state, state_int))

                # Add 0s for every state from prev_state_int to state_int
                if prev_state_int is None:
                    zeroes_between_prev_and_now = state_int
                else:
                    zeroes_between_prev_and_now = (state_int - prev_state_int - 1)

                if zeroes_between_prev_and_now > 0:
                    #log.info("zeroes_between_prev_and_now %s" % zeroes_between_prev_and_now)
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

    # setup logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='lookup-table filename')
    parser.add_argument('--use-permutation-rank', default=False, action='store_true', help='calculate permutation_rank()')
    args = parser.parse_args()

    convert_to_cost_only(args.filename, args.use_permutation_rank)
