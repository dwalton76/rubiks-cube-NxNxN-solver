#!/usr/bin/env python3

from pprint import pformat, pprint
from rubikscubennnsolver import wing_strs_all, reverse_steps
from rubikscubennnsolver.LookupTable import steps_on_same_face_and_layer
from rubikscubennnsolver.misc import parse_ascii_777
from rubikscubennnsolver.RubiksCube777 import RubiksCube777
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555, edges_partner_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, moves_666, solved_666, rotate_666
import itertools
import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

# Build wing_str_combos_two and wing_str_combos_four
#pprint(tuple(itertools.combinations(wing_strs_all, 2)))
#pprint(tuple(itertools.combinations(wing_strs_all, 4)))

cube = RubiksCube555(solved_555, "URFDLB")

for step in reverse_steps("F Dw2 U R2 B R' Dw' Rw' Fw' B Uw' F L Uw Lw2 Dw' L Dw F' Rw' B' Rw' Lw' F U Lw F Rw2 U2 Lw2 D' Rw2 D2 Lw' D' Rw' Lw2 B' Lw' F' Dw L F' L' U' F Dw'  B' Uw' B' D' U2 B Uw  D' L' Bw U' F2 B U Bw' F B Uw' B2 R' B2 R Uw D2 B U B' D' F B' R' L' F2 D' F L B D' B' ".split()):
    cube.rotate(step)

cube.print_cube()

for step in "F Dw2 U R2 B R' Dw' Rw' Fw' B Uw' F L Uw Lw2 Dw' L Dw  F' Rw' B' Rw' Lw' F U Lw F Rw2 U2 Lw2 D' Rw2 D2 Lw' D' Rw' Lw2 B' Lw' ".split():
    cube.rotate(step)

cube.print_cube()
print(cube.get_kociemba_string(True))
