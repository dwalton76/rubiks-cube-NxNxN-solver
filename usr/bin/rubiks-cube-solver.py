#!/usr/bin/env python2

"""
Solve any size rubiks cube:
- For 2x2x2 and 3x3x3 just solve it
- For 4x4x4 and larger, reduce to 3x3x3 and then solve

This is a work in progress
"""

from rubikscubennnsolver import ImplementThis, SolveError, StuckInALoop
from rubikscubennnsolver.RubiksCube222 import RubiksCube222
from rubikscubennnsolver.RubiksCube333 import RubiksCube333
from rubikscubennnsolver.RubiksCube444 import RubiksCube444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666
from time import sleep
import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

parser = argparse.ArgumentParser()

# 2x2x2
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='DLRRFULLDUBFDURDBFBRBLFU')
    #default='UUUURRRRFFFFDDDDLLLLBBBB')

# 3x3x3
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='RRBBUFBFBRLRRRFRDDURUBFBBRFLUDUDFLLFFLLLLDFBDDDUUBDLUU')
    #default='UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB') # solved

# 4x4x4
parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
    default='FUULURFFRLRBDDDULUDFLFBBFUURRRUBLBLBDLUBDBULDDRDFLFBBRDBFDBLRBLDULUFFRLRDLDBBRLRUFFRUBFDUDFRLFRU')
    #default='LFBDUFLDBUBBFDFBLDLFRDFRRURFDFDLULUDLBLUUDRDUDUBBFFRBDFRRRRRRRLFBLLRDLDFBUBLFBLRLURUUBLBDUFUUFBD')
    #default='UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB') # solved

# 5x5x5
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='RFFFUDUDURBFULULFDBLRLDUFDBLUBBBDDURLRDRFRUDDBFUFLFURRLDFRRRUBFUUDUFLLBLBBULDDRRUFUUUBUDFFDRFLRBBLRFDLLUUBBRFRFRLLBFRLBRRFRBDLLDDFBLRDLFBBBLBLBDUUFDDD')
    #default='UDLFDLDDLUFDUBRLBDLFLRBFRBLBBFUDURDULRRBRLFUURBUFLUBDUDRURRRBUFUFFFRUFFLDUURURFFULFFRLFDBRRFRDDBRFBBLBRDFBBBBUDDLLLDBUULUDULDLDDLBRRLRLUBBFFBDLFBDDLFR')
    #default='DFFURRULDLDLURLBDDRRBFRURFBFBFRBDLBBFRBLRFBRBBFLULDLBLULLFRUBUFLDFFLDULDDLUURRDRFBRLULUDRBDUUUBBRFFDBDFURDBBDDRULBUDRDLLLBDRFDLRDLLFDBBUFBRURFFUFFUUFU') # ida_UD_centers_stage on this one takes forever
    #default='UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB') # solved

# 6x6x6
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='FBDDDFFUDRFBBLFLLURLDLLUFBLRFDUFLBLLFBFLRRBBFDRRDUBUFRBUBRDLUBFDRLBBRLRUFLBRBDUDFFFDBLUDBBLRDFUUDLBBBRRDRUDLBLDFRUDLLFFUUBFBUUFDLRUDUDBRRBBUFFDRRRDBULRRURULFDBRRULDDRUUULBLLFDFRRFDURFFLDUUBRUFDRFUBLDFULFBFDDUDLBLLRBL')
    #default='UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB') # solved

args = parser.parse_args()

try:
    if len(args.state) == 24:
        cube = RubiksCube222(args.state)

    elif len(args.state) == 54:
        cube = RubiksCube333(args.state)

    elif len(args.state) == 96:
        cube = RubiksCube444(args.state)

    elif len(args.state) == 150:
        cube = RubiksCube555(args.state)

    elif len(args.state) == 216:
        cube = RubiksCube666(args.state)

    else:
        print("ERROR: add support for cubes with %d facelets" % len(args.state))
        sys.exit(1)

    cube.print_cube()
    cube.solve()

    print("Final Cube")
    cube.print_cube()

    '''
    print("\nOriginal solution")
    cube.print_solution()
    print("%d steps" % len(cube.solution))
    '''

    print("\nSolution")
    cube.print_solution()

    # Now put the cube back in its initial state and verify the solution solves it
    solution = cube.solution

    if len(args.state) == 24:
        cube = RubiksCube222(args.state)

    elif len(args.state) == 54:
        cube = RubiksCube333(args.state)

    elif len(args.state) == 96:
        cube = RubiksCube444(args.state)

    elif len(args.state) == 150:
        cube = RubiksCube555(args.state)

    elif len(args.state) == 216:
        cube = RubiksCube666(args.state)

    else:
        raise Exception("Implement cube with %d facelets" % len(args.state))

    # Uncomment to print the solution step by step
    len_steps = len(solution)
    print_steps = False

    for (i, step) in enumerate(solution):

        if print_steps:
            print("Phase: %s" % cube.phase())
            print("Move %d/%d: %s" % (i+1, len_steps, step))

        cube.rotate(step)

        if print_steps:
            cube.print_cube()
            print("\n\n\n\n")
            sleep(1)
            os.system('clear')

    if print_steps:
        cube.print_cube()

    if not cube.solved():
        kociemba_string = cube.get_kociemba_string(False)
        edge_swap_count = cube.get_edge_swap_count(edges_paired=True, debug=True)
        corner_swap_count = cube.get_corner_swap_count(debug=True)

        raise SolveError("cube should be solved but is not, edge parity %d, corner parity %d, kociemba %s" %
            (edge_swap_count, corner_swap_count, kociemba_string))

except ImplementThis:
    cube.print_cube_layout()
    cube.print_cube()
    raise

except SolveError:
    cube.print_cube_layout()
    cube.print_cube()
    raise

except StuckInALoop:
    cube.print_cube_layout()
    cube.print_cube()
    raise
