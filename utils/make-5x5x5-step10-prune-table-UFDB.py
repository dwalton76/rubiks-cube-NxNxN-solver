#!/usr/bin/env python

import os
import shutil
import subprocess
from pprint import pprint

UFDB_states = []

line_number = 0
ufdb_filename = 'UFDB_foo.txt'
with open(ufdb_filename, 'w') as fh_ufdb:
    with open('/home/dwalton/lego/rubiks-cube-NxNxN-solver/lookup-table-5x5x5-step10-UD-centers-stage.txt.6-deep', 'r') as fh:
        hex_width = len('020000002b9ff7')
        num_of_bits = 54
        UFDB_hex_width = 9

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

            UFDB_state = state[0:9] + state[18:27] + state[45:54] + state[36:45]
            UFDB_hex_state = str(hex(int(UFDB_state, 2)))[2:]
            #print("UFDB hex: %s" % UFDB_hex_state)

            if UFDB_hex_state.endswith('L'):
                UFDB_hex_state = UFDB_hex_state[:-1]

            UFDB_hex_state = UFDB_hex_state.zfill(UFDB_hex_width)
            #print("UFDB hex: %s" % UFDB_hex_state)
            #print("")

            fh_ufdb.write("%s:%d\n" % (UFDB_hex_state, len(steps.split())))

            if line_number % 1000000 == 0:
                print("%d: read %s" % (line_number, ufdb_filename))
            line_number += 1

            #if line_number == 10:
            #    break

# Sort the file
subprocess.check_output("sort  --temporary-directory=./tmp/ --output=%s %s" % (ufdb_filename, ufdb_filename), shell=True)

# Now parse the file and keep the shortest solution for each state
ufdb_filename_final = ufdb_filename + '.final'
prev_state = None
steps_for_prev_state = []
line_number = 0

with open(ufdb_filename_final, 'w') as fh_final:
    with open(ufdb_filename, 'r') as fh:
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
                print("%d: write %s" % (line_number, ufdb_filename_final))

    # write shortest solution for prev_state
    if steps_for_prev_state:
        len_steps_for_prev_state = min(steps_for_prev_state)
        fh_final.write("%s:%d\n" % (prev_state, len_steps_for_prev_state))

os.unlink(ufdb_filename)
#subprocess.check_output("./utils/pad_lines.py %s" % ufdb_filename_final, shell=True)
shutil.move(ufdb_filename_final, 'lookup-table-5x5x5-step13-UD-centers-stage-UFDB-only.txt')
