"""
Used to print the logic that is in rotate_444() and rotate_555() in
https://github.com/dwalton76/rubiks-cube-lookup-tables/blob/master/rotate.c
"""

# standard libraries
import logging
from copy import copy
from pprint import pformat

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube222 import moves_222, solved_222
from rubikscubennnsolver.RubiksCube333 import moves_333, solved_333
from rubikscubennnsolver.RubiksCube444 import moves_444, solved_444
from rubikscubennnsolver.RubiksCube555 import moves_555, solved_555
from rubikscubennnsolver.RubiksCube666 import moves_666, solved_666
from rubikscubennnsolver.RubiksCube777 import moves_777, solved_777

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)12s %(levelname)8s: %(message)s")
log = logging.getLogger(__name__)

build_rotate_xxx_c = False

if build_rotate_xxx_c:
    print(
        """
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "rotate_xxx.h"

"""
    )

for (size, solved_state) in (
    (2, solved_222),
    (3, solved_333),
    (4, solved_444),
    (5, solved_555),
    (6, solved_666),
    (7, solved_777),
):

    cube = RubiksCube(solved_state, "URFDLB")
    max_square_index = size * size * 6

    # Change each value to be equal to its square position
    for x in range(1, max_square_index + 1):
        cube.state[x] = str(x)

    original_state = copy(cube.state)

    if size == 2:
        steps = moves_222

    elif size == 3:
        steps = moves_333

    elif size == 4:
        steps = moves_444

    elif size == 5:
        steps = moves_555

    elif size == 6:
        steps = moves_666

    elif size == 7:
        steps = moves_777

    else:
        raise Exception("Add support for size %s" % size)

    steps = list(steps)
    steps.extend(["x", "x'", "x2", "y", "y'", "y2", "z", "z'", "z2"])

    if size in (4, 5, 6, 7):
        steps.extend(["2U", "2U'", "2U2", "2D", "2D'", "2D2"])
        steps.extend(["2L", "2L'", "2L2", "2R", "2R'", "2R2"])
        steps.extend(["2F", "2F'", "2F2", "2B", "2B'", "2B2"])

    if size in (6, 7):
        steps.extend(["3U", "3U'", "3U2", "3D", "3D'", "3D2"])
        steps.extend(["3L", "3L'", "3L2", "3R", "3R'", "3R2"])
        steps.extend(["3F", "3F'", "3F2", "3B", "3B'", "3B2"])

    # middle layer slices
    if size == 5:
        steps.extend(["3U", "3U'", "3U2"])
        steps.extend(["3L", "3L'", "3L2"])
        steps.extend(["3F", "3F'", "3F2"])

    if build_rotate_xxx_c:
        print("void")
        print("rotate_%d%d%d(char *cube, char *cube_tmp, int array_size, move_type move)" % (size, size, size))
        print("{")
        print("    /* This was contructed using utils/rotate-printer.py */")
        print("    memcpy(cube_tmp, cube, sizeof(char) * array_size);")
        print("")
        first_step = True

        for step in steps:
            cube.rotate(step)
            cube.print_case_statement_C(step, first_step)
            cube.state = copy(original_state)
            first_step = False

        print(
            r"""
    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
"""
        )

    else:
        rotate_mapper = {}

        for step in steps:
            step_pretty = step.replace("'", "_prime")
            function_name = "rotate_%d%d%d_%s" % (size, size, size, step_pretty)
            rotate_mapper[step] = function_name
            cube.rotate(step)

            rotate_mapper[step] = cube.print_case_statement_python(function_name, step)
            cube.state = copy(original_state)

        lines_to_keep = []
        swaps_xxx = "swaps_%d%d%d" % (size, size, size)
        nnn_filename = "rubikscubennnsolver/RubiksCube%d%d%d.py" % (size, size, size)

        with open(nnn_filename, "r") as fh:
            for line in fh:
                if line.startswith(swaps_xxx):
                    break

                lines_to_keep.append(line)

        with open(nnn_filename, "w") as fh:
            fh.write("".join(lines_to_keep))
            fh.write("swaps_%d%d%d = %s\n" % (size, size, size, pformat(rotate_mapper, width=2048)))
            fh.write("\ndef rotate_%d%d%d(cube, step):\n" % (size, size, size))
            fh.write("    return [cube[x] for x in swaps_%d%d%d[step]]\n" % (size, size, size))
            fh.write("")
