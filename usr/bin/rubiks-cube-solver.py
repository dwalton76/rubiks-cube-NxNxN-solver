#!/usr/bin/env python2

"""
Solve any size rubiks cube:
- For 2x2x2 and 3x3x3 just solve it
- For 4x4x4 and larger, reduce to 3x3x3 and then solve

This is a work in progress
"""

from rubikscubennnsolver import ImplementThis, SolveError, StuckInALoop
from rubikscubennnsolver.LookupTable import NoSteps
from rubikscubennnsolver.RubiksCube222 import RubiksCube222
from rubikscubennnsolver.RubiksCube333 import RubiksCube333
from rubikscubennnsolver.RubiksCube444 import RubiksCube444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666
from rubikscubennnsolver.RubiksCube777 import RubiksCube777
from time import sleep
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

# 2x2x2
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='DLRRFULLDUBFDURDBFBRBLFU')
#    default='UUUURRRRFFFFDDDDLLLLBBBB')

# 3x3x3
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='RRBBUFBFBRLRRRFRDDURUBFBBRFLUDUDFLLFFLLLLDFBDDDUUBDLUU')
#    default='UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB') # solved

# 4x4x4
parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
    default='FUULURFFRLRBDDDULUDFLFBBFUURRRUBLBLBDLUBDBULDDRDFLFBBRDBFDBLRBLDULUFFRLRDLDBBRLRUFFRUBFDUDFRLFRU')
#    default='RRRRRRRLRRRLRRRFLBBFBBBBBBBBRBBBUUUUUDDDUDDDDDDULLLFLLLRLLLRLFFLBFFBLFFFLFFFBFFFDDDDUUUUUUUUUDDD')
#    default='DUFFRDLRDLBUDLBULLBLFFUBURFFURFURDUBUDLLFDLRFDLRRRDBBBDDUFULLBFFBBBBLBBRFFUDFFUDDDLLDRRBRRUURRLU') # edges take 46 steps
#    default='LFBDUFLDBUBBFDFBLDLFRDFRRURFDFDLULUDLBLUUDRDUDUBBFFRBDFRRRRRRRLFBLLRDLDFBUBLFBLRLURUUBLBDUFUUFBD')
#    default='DFBRULBFFUDFDRULURDUUFLLRFLFDLRRFBRFUDUFLRBDBDULRBLBBBFDUFUBUFBDLLLRURDBDBDDBBLUFDRFFULRURRRBLDL') # takes a lot of moves
#    default='UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB') # solved

# 5x5x5
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='RFFFUDUDURBFULULFDBLRLDUFDBLUBBBDDURLRDRFRUDDBFUFLFURRLDFRRRUBFUUDUFLLBLBBULDDRRUFUUUBUDFFDRFLRBBLRFDLLUUBBRFRFRLLBFRLBRRFRBDLLDDFBLRDLFBBBLBLBDUUFDDD')
#    https://www.speedsolving.com/forum/threads/arnauds-5x5x5-edge-pairing-method-examples.1447/
#    default='LDFRDDUUUUFUUUBLUUUFLDFDRFDDFBBRRRULRRRBFRRRURFRFDUBDRUBFFFUBFFFUUFFFRLDLRFDLBDDLDDDRDDDDUDDDDUULDLFBFLFFULLLRFLLLRLLLLRRBLBBRBULULBBBRUBBBRBBBBULBRFB')
#    default='UDLFDLDDLUFDUBRLBDLFLRBFRBLBBFUDURDULRRBRLFUURBUFLUBDUDRURRRBUFUFFFRUFFLDUURURFFULFFRLFDBRRFRDDBRFBBLBRDFBBBBUDDLLLDBUULUDULDLDDLBRRLRLUBBFFBDLFBDDLFR')
#    default='UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB') # solved
#    default='DFFURRULDLDLURLBDDRRBFRURFBFBFRBDLBBFRBLRFBRBBFLULDLBLULLFRUBUFLDFFLDULDDLUURRDRFBRLULUDRBDUUUBBRFFDBDFURDBBDDRULBUDRDLLLBDRFDLRDLLFDBBUFBRURFFUFFUUFU') # step10 takes 9s
#    default='URUBFUUFRDFFUUFLRDBLLBDDDLUULRDLDUBDLRBBLFLBRBFUUBBRBFFUDLFLLBFUFUDRLBFUBBURRLLRUFRDUFFDFRFUBRBBDRFRFLLFURLLFBRBLUDRDDRRDRRFDUDLFLDLUUDUDBRBBBRBDDLDFL') # step10 takes 45s, step30 takes 14s
#    default='RFUBLFUBRULLUDDRLRLLFFFLUBDBLBFFUFLFURBFFLDDLFFBBRLUUDRRDLLLRDFFLBBLFURUBULBRLBDRUURDRRDFURDBUUBBFBUDRUBURBRBDLFLBDFBDULLDBBDDDRRFURLDUDUBRDFRFFDFDRLU') # step10 takes 50s

# 6x6x6
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='FBDDDFFUDRFBBLFLLURLDLLUFBLRFDUFLBLLFBFLRRBBFDRRDUBUFRBUBRDLUBFDRLBBRLRUFLBRBDUDFFFDBLUDBBLRDFUUDLBBBRRDRUDLBLDFRUDLLFFUUBFBUUFDLRUDUDBRRBBUFFDRRRDBULRRURULFDBRRULDDRUUULBLLFDFRRFDURFFLDUUBRUFDRFUBLDFULFBFDDUDLBLLRBL')
#    default='DDDDDLDUUUULUUUUUFFUUUUUUUUUUBLFFUFFRULUUBLRRRRFRRRRLBDRRLLLBLLRLFBFBDDRFURRDURBBBBFDBBBBBFBBBBRLBBBBUURUDDRLFBBLDRDDDDLFDDDDRLDDDDFRDDDDFUDDLRFLBRDLURLLLLDFLLLLBULLRRRBRRRRBRBBLUBDRLLBFUFFFFBUFFFFUFFFFFLRFFFFLDUBRLB') # has crazy 4x4x4 reduction issues
#    default='UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB') # solved

# 7x7x7
#parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='DBDBDDFBDDLUBDLFRFRBRLLDUFFDUFRBRDFDRUFDFDRDBDBULDBDBDBUFBUFFFULLFLDURRBBRRBRLFUUUDUURBRDUUURFFFLRFLRLDLBUFRLDLDFLLFBDFUFRFFUUUFURDRFULBRFURRBUDDRBDLLRLDLLDLUURFRFBUBURBRUDBDDLRBULBULUBDBBUDRBLFFBLRBURRUFULBRLFDUFDDBULBRLBUFULUDDLLDFRDRDBBFBUBBFLFFRRUFFRLRRDRULLLFRLFULBLLBBBLDFDBRBFDULLULRFDBR')

args = parser.parse_args()

if args.debug:
    log.setLevel(logging.DEBUG)

try:
    if len(args.state) == 24:
        cube = RubiksCube222(args.state, args.debug)

    elif len(args.state) == 54:
        cube = RubiksCube333(args.state, args.debug)

    elif len(args.state) == 96:
        cube = RubiksCube444(args.state, args.debug)

    elif len(args.state) == 150:
        cube = RubiksCube555(args.state, args.debug)

    elif len(args.state) == 216:
        cube = RubiksCube666(args.state, args.debug)

    elif len(args.state) == 294:
        cube = RubiksCube777(args.state, args.debug)
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

    elif len(args.state) == 294:
        cube = RubiksCube777(args.state)

    else:
        raise Exception("Implement cube with %d facelets" % len(args.state))

    # Uncomment to print the solution step by step
    len_steps = len(solution)

    for (i, step) in enumerate(solution):

        if args.print_steps:
            print("Phase     : %s" % cube.phase())
            print("Move %d/%d: %s" % (i+1, len_steps, step))

        cube.rotate(step)

        if args.print_steps:
            cube.print_cube()
            print("\n\n\n\n")
            sleep(1)
            os.system('clear')

    if args.print_steps:
        cube.print_cube()

    if not cube.solved():
        kociemba_string = cube.get_kociemba_string(False)
        edge_swap_count = cube.get_edge_swap_count(edges_paired=True, orbit=None, debug=True)
        corner_swap_count = cube.get_corner_swap_count(debug=True)

        raise SolveError("cube should be solved but is not, edge parity %d, corner parity %d, kociemba %s" %
            (edge_swap_count, corner_swap_count, kociemba_string))

except (ImplementThis, SolveError, StuckInALoop, NoSteps, KeyError):
    cube.print_cube_layout()
    cube.print_cube()
    cube.print_solution()
    print(cube.get_kociemba_string(True))
    raise
