#!/usr/bin/env python

import os
import shutil
import subprocess
from pprint import pprint

LFRB_states = []

line_number = 0
lfrb_filename = 'LFRB_foo.txt'
with open(lfrb_filename, 'w') as fh_ufdb:
    with open('/home/dwalton/lego/rubiks-cube-NxNxN-solver/lookup-table-5x5x5-step10-UD-centers-stage.txt.6-deep', 'r') as fh:
        hex_width = len('020000002b9ff7')
        num_of_bits = 54
        LFRB_hex_width = 9

        for line in fh:
            line = line.rstrip()
            (state, steps) = line.split(':')

            # state is 54 bits once you convert from hex to binary
            # 100011000000000000100100011010100000101001010001110101
            #
            # 100011000  U 0:9
            # 000000000  L 9:18
            # 100100011  F 18:27
            # 010100000  R 27:36
            # 101001010  B 36:45
            # 001110101  D 45:54

            #print("state hex: %s" % state)
            state_dec = int(state, 16)
            #print("state dec: %s" % state_dec)

            # convert to binary and remove the leading 0b via [2:] then pad leading zeroes to num_of_bits
            state = str(bin(state_dec)[2:].zfill(num_of_bits))
            #print("state bin: %s" % state)

            LFRB_state = state[9:45]
            LFRB_hex_state = str(hex(int(LFRB_state, 2)))[2:]
            #print("LFRB hex: %s" % LFRB_hex_state)

            if LFRB_hex_state.endswith('L'):
                LFRB_hex_state = LFRB_hex_state[:-1]

            LFRB_hex_state = LFRB_hex_state.zfill(LFRB_hex_width)
            #print("LFRB hex: %s" % LFRB_hex_state)
            #print("")

            fh_ufdb.write("%s:%d\n" % (LFRB_hex_state, len(steps.split())))

            if line_number % 1000000 == 0:
                print("%d: read %s" % (line_number, lfrb_filename))
            line_number += 1

            #if line_number == 10:
            #    break

# Sort the file
subprocess.check_output("sort  --temporary-directory=./tmp/ --output=%s %s" % (lfrb_filename, lfrb_filename), shell=True)

# Now parse the file and keep the shortest solution for each state
lfrb_filename_final = lfrb_filename + '.final'
prev_state = None
steps_for_prev_state = []
line_number = 0

with open(lfrb_filename_final, 'w') as fh_final:
    with open(lfrb_filename, 'r') as fh:
        for line in fh:
            line = line.rstrip()
            (state, len_steps) = line.split(':')
            len_steps = int(len_steps)

            if prev_state is None:
                steps_for_prev_state.append(len_steps)
            else:
                if state == prev_state:
                    steps_for_prev_state.append(len_steps)
                else:
                    # write shortest solution for prev_state
                    len_steps_for_prev_state = min(steps_for_prev_state)

                    fh_final.write("%s:%d\n" % (prev_state, len_steps_for_prev_state))

                    # Reset steps_for_prev_state
                    steps_for_prev_state = []
                    steps_for_prev_state.append(len_steps)

            prev_state = state

            line_number += 1

            if line_number % 1000000 == 0:
                print("%d: write %s" % (line_number, lfrb_filename_final))

    # write shortest solution for prev_state
    if steps_for_prev_state:
        len_steps_for_prev_state = min(steps_for_prev_state)
        fh_final.write("%s:%d\n" % (prev_state, len_steps_for_prev_state))

os.unlink(lfrb_filename)
#subprocess.check_output("./utils/pad_lines.py %s" % lfrb_filename_final, shell=True)
shutil.move(lfrb_filename_final, 'lookup-table-5x5x5-step14-UD-centers-stage-LFRB-only.txt')
