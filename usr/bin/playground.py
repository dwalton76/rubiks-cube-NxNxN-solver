#!/usr/bin/env python3

from pprint import pformat
from rubikscubennnsolver.LookupTable import steps_on_same_face_and_layer
from rubikscubennnsolver.misc import parse_ascii_777
from rubikscubennnsolver.RubiksCube777 import RubiksCube777
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555, get_wings_edges_will_pair
from rubikscubennnsolver.RubiksCube777 import RubiksCube666, moves_666
import logging
import sys

def chop_trailing_outer_layer_steps(steps):
    last_w_index = 0

    for (index, step) in enumerate(steps):
        if "w" in step:
            last_w_index = index

    #log.info("chop_trailing_outer_layer_steps stesp %s, last_w_index %d" % (pformat(steps), last_w_index))
    return steps[0:last_w_index+1]


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

#get_wings_edges_will_pair(
#    "OOOyPXzqRQrPSSSTTTUUUVVVqWwxxWrYYpZZ",
#    "OOO---z-----SSSTTTUUUVVV-Ww---YYYWZZ"
#)
illegal_moves_for_step20 = ("3Fw", "3Fw'", "3Bw", "3Bw'", "3Lw", "3Lw'", "3Rw", "3Rw'")

moves_for_step20 = []
for x in moves_666:
    if x not in illegal_moves_for_step20:
        moves_for_step20.append(x)

#print(" ".join(moves_666))
#print(" ".join(moves_for_step20))

sequences = []

#for step in moves_for_step20:
#    sequences.append((step,))

for step1 in moves_for_step20:
    sequences.append((step1,))

    for step2 in moves_for_step20:

        if not steps_on_same_face_and_layer(step1, step2):
            sequences.append((step1, step2))

            for step3 in moves_for_step20:

                if not steps_on_same_face_and_layer(step2, step3):
                    sequences.append((step1, step2, step3))

                    for step4 in moves_for_step20:

                        if not steps_on_same_face_and_layer(step3, step4):
                            sequences.append((step1, step2, step3, step4))

                            '''
                            for step5 in moves_for_step20:
                                if not steps_on_same_face_and_layer(step4, step5):
                                    sequences.append((step1, step2, step3, step4, step5))
                            '''

# Only keep the ones with a 3w turn
final = []
not_interested = 0
for seq in sequences:
    three_count = 0
    len_seq = len(seq)

    for step in seq:
        if step.startswith("3"):
            three_count += 1

    if three_count >= 1:
        final.append((len_seq, seq))
    else:
        not_interested += 1

final = sorted(final)
#print("\n".join(final))
print("Found {:,}".format(len(final)))
print("Pruned {:,}".format(not_interested))

with open("pre_steps_step20_666.txt", "w") as fh:
    for (_, seq) in final:
        fh.write(" ".join(seq) + "\n")
