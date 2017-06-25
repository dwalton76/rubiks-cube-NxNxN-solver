#!/usr/bin/env python2

from rubikscubennnsolver import ImplementThis, SolveError, StuckInALoop
from rubikscubennnsolver.LookupTable import NoSteps
from rubikscubennnsolver.RubiksCube777 import RubiksCube777
import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

parser = argparse.ArgumentParser()
parser.add_argument('--print-steps', default=False, action='store_true')
parser.add_argument('--debug', default=False, action='store_true')

# 7x7x7
parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='DBDBDDFBDDLUBDLFRFRBRLLDUFFDUFRBRDFDRUFDFDRDBDBULDBDBDBUFBUFFFULLFLDURRBBRRBRLFUUUDUURBRDUUURFFFLRFLRLDLBUFRLDLDFLLFBDFUFRFFUUUFURDRFULBRFURRBUDDRBDLLRLDLLDLUURFRFBUBURBRUDBDDLRBULBULUBDBBUDRBLFFBLRBURRUFULBRLFDUFDDBULBRLBUFULUDDLLDFRDRDBBFBUBBFLFFRRUFFRLRRDRULLLFRLFULBLLBBBLDFDBRBFDULLULRFDBR',
    default='UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB' # solved
)

'''
UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU
RRRRRRR
RRRRRRR
RRRRRRR
RRRRRRR
RRRRRRR
RRRRRRR
RRRRRRR

FFFFFFF
FFFFFFF
FFFFFFF
FFFFFFF
FFFFFFF
FFFFFFF
FFFFFFF

DDDDDDD
DDDDDDD
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD

LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL

BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB


'''

args = parser.parse_args()
cube = RubiksCube777(args.state, args.debug)

cube.state[61] = 'R'
cube.state[65] = 'L'
cube.state[69] = 'L'
cube.state[79] = 'R'
cube.state[82] = 'L'
cube.state[87] = 'R'
cube.state[89] = 'R'

cube.state[108] = 'B'
cube.state[110] = 'B'
cube.state[114] = 'F'
cube.state[118] = 'F'
cube.state[128] = 'F'
cube.state[132] = 'F'
cube.state[136] = 'B'
cube.state[138] = 'F'

cube.state[157] = 'R'
cube.state[159] = 'R'
cube.state[163] = 'R'
cube.state[167] = 'R'
cube.state[177] = 'L'
cube.state[181] = 'L'
cube.state[185] = 'L'
cube.state[187] = 'L'

cube.state[206] = 'B'
cube.state[208] = 'B'
cube.state[212] = 'F'
cube.state[216] = 'B'
cube.state[226] = 'F'
cube.state[230] = 'F'
cube.state[234] = 'B'
cube.state[236] = 'B'

cube.print_cube()
cube.solve()

print("Final Cube")
cube.print_cube()
cube.print_solution()
