#!/usr/bin/env python2

"""
Used to print the logic that is in rotate_444() and rotate_555() in
https://github.com/dwalton76/rubiks-cube-lookup-tables/blob/master/rotate.c
"""

from copy import copy
from rubikscubennnsolver import RubiksCube
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

solved_222 = 'UUUURRRRFFFFDDDDLLLLBBBB'
solved_333 = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
solved_444 = 'UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB'
solved_555 = 'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB'
solved_666 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
solved_777 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

for (size, solved_state) in (
    (2, solved_222),
    (3, solved_333),
    (4, solved_444),
    (5, solved_555),
    (6, solved_666),
    (7, solved_777)
    ):

    cube = RubiksCube(solved_state)
    max_square_index = size * size * 6

    # Change each value to be equal to its square position
    for x in xrange(1, max_square_index+1):
        cube.state[x] = str(x)

    original_state = copy(cube.state)

    if size == 2 or size == 3:
        steps = ("U", "U'", "U2",
                 "L", "L'", "L2",
                 "F", "F'", "F2",
                 "R", "R'", "R2",
                 "B", "B'", "B2",
                 "D", "D'", "D2")

    elif size == 4 or size == 5:
        steps = ("U", "U'", "U2", "Uw", "Uw'", "Uw2",
                 "L", "L'", "L2", "Lw", "Lw'", "Lw2",
                 "F", "F'", "F2", "Fw", "Fw'", "Fw2",
                 "R", "R'", "R2", "Rw", "Rw'", "Rw2",
                 "B", "B'", "B2", "Bw", "Bw'", "Bw2",
                 "D", "D'", "D2", "Dw", "Dw'", "Dw2")

    elif size == 6 or size == 7:
        steps = ("U", "U'", "U2", "Uw", "Uw'", "Uw2", "3Uw", "3Uw'", "3Uw2",
                 "L", "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2",
                 "F", "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2",
                 "R", "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2",
                 "B", "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2",
                 "D", "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2")

    if False:
        print("void")
        print("rotate_%d%d%d(int *cube, int *cube_tmp, int array_size, char *step)" % (size, size, size))
        print("{")
        print("    /* This was contructed using 'solver.py --rotate-printer' */")
        print("    memcpy(cube_tmp, cube, sizeof(int) * array_size);")
        print("")
        for step in steps:
            cube.rotate(step)
            cube.print_case_statement_C(step)
            cube.state = copy(original_state)
        print("}\n\n")

    else:
        rotate_mapper = {}

        for step in steps:
            step_pretty = step.replace("'", "_prime")

            function_name = "rotate_%d%d%d_%s" % (size, size, size, step_pretty)
            print("")
            print("def %s(cube):" % function_name)
            rotate_mapper[step] = function_name

            cube.rotate(step)
            cube.print_case_statement_python(step)
            cube.state = copy(original_state)
            #print("\n\n")

        print("")
        print("rotate_mapper_%d%d%d = {" % (size, size, size))
        for step in sorted(rotate_mapper.keys()):
            print("    \"%s\" : %s," % (step, rotate_mapper[step]))
        print("}")

        print("")
        print("def rotate_%d%d%d(cube, step):" % (size, size, size))
        print("    return rotate_mapper_%d%d%d[step](cube)" % (size, size, size))
        print("")
