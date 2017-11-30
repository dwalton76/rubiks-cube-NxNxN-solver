#!/usr/bin/env python3

"""
Used to print the logic that is in rotate_444() and rotate_555() in
https://github.com/dwalton76/rubiks-cube-lookup-tables/blob/master/rotate.c
"""

from copy import copy
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube222 import solved_2x2x2, moves_2x2x2
from rubikscubennnsolver.RubiksCube333 import solved_3x3x3, moves_3x3x3
from rubikscubennnsolver.RubiksCube444 import solved_4x4x4, moves_4x4x4
from rubikscubennnsolver.RubiksCube555 import solved_5x5x5, moves_5x5x5
from rubikscubennnsolver.RubiksCube666 import solved_6x6x6, moves_6x6x6
from rubikscubennnsolver.RubiksCube777 import solved_7x7x7, moves_7x7x7
from rubikscubennnsolver.RubiksCubeNNNEven import solved_8x8x8, moves_8x8x8
from rubikscubennnsolver.RubiksCubeNNNOdd import solved_9x9x9
from rubikscubennnsolver.RubiksCubeNNNEven import moves_8x8x8 as moves_9x9x9
from rubikscubennnsolver.RubiksCubeNNNEven import solved_10x10x10, moves_10x10x10
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

build_rotate_xxx_c = False


if build_rotate_xxx_c:
    print("""
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "rotate_xxx.h"

int
strmatch (char *str1, char *str2)
{
    if (strcmp(str1, str2) == 0) {
        return 1;
    }
    return 0;
}
""")

for (size, solved_state) in (
    (2, solved_2x2x2),
    (3, solved_3x3x3),
    (4, solved_4x4x4),
    (5, solved_5x5x5),
    (6, solved_6x6x6),
    (7, solved_7x7x7),
    (8, solved_8x8x8),
    (9, solved_9x9x9),
    (10, solved_10x10x10),
    ):

    cube = RubiksCube(solved_state, 'URFDLB')
    max_square_index = size * size * 6

    # Change each value to be equal to its square position
    for x in range(1, max_square_index+1):
        cube.state[x] = str(x)

    original_state = copy(cube.state)

    if size == 2:
        steps = moves_2x2x2

    elif size == 3:
        steps = moves_3x3x3

    elif size == 4:
        steps = moves_4x4x4

    elif size == 5:
        steps = moves_5x5x5

    elif size == 6:
        steps = moves_6x6x6

    elif size == 7:
        steps = moves_7x7x7

    elif size == 8:
        steps = moves_8x8x8

    elif size == 9:
        steps = moves_9x9x9

    elif size == 10:
        steps = moves_10x10x10

    else:
        raise Exception("Add support for size %s" % size)

    steps = list(steps)
    steps.extend(["x", "x'", "y", "y'", "z", "z'"])

    if build_rotate_xxx_c:
        print("void")
        print("rotate_%d%d%d(int *cube, int *cube_tmp, int array_size, char *step)" % (size, size, size))
        print("{")
        print("    /* This was contructed using 'solver.py --rotate-printer' */")
        print("    memcpy(cube_tmp, cube, sizeof(int) * array_size);")
        print("")
        first_step = True

        for step in steps:
            cube.rotate(step)
            cube.print_case_statement_C(step, first_step)
            cube.state = copy(original_state)
            first_step = False

        print("""    } else if (strcmp(step, "noturn") == 0) {
    } else {
        printf("ERROR: invalid step %s\\n", step);
        // exit(1);
    }
}
""")

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
