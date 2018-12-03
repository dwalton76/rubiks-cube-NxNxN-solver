#!/usr/bin/env python3

"""
This
- parses all of the edge patterns in lookup-table-4x4x4-step141.txt
- puts the centers back to solved
- runs step140 IDA to find the solution for each edge pattern when the centers are solved

This is used by --fast solves so they do not have to run IDA for step300
"""

from rubikscubennnsolver import reverse_steps, wing_str_map
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444, edges_partner_444
import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

cube = RubiksCube444(solved_444, "URFDLB")
cube.cpu_mode = "fast"
cube.lt_init()

only_colors = ("LB", "LF", "RB", "RF")

with open("results.txt", "w") as fh_results:
    with open("lookup-table-4x4x4-step141.txt", "r") as fh:
        for (line_number, line) in enumerate(fh):
            cube.re_init()
            (state, steps_to_solve) = line.strip().split(":")
            steps_to_solve = steps_to_solve.split()
            steps_to_scramble = reverse_steps(steps_to_solve)

            for step in steps_to_scramble:
                cube.rotate(step)

            # put the centers back to solved
            for side in cube.sides.values():
                for square_index in side.center_pos:
                    cube.state[square_index] = side.name

            #cube.print_cube()
            scramble_len = len(cube.solution)

            #cube.lt_pair_first_four_edges.only_colors = only_colors
            cube.lt_pair_first_four_edges_edges_only.only_colors = only_colors
            cube.lt_pair_first_four_edges.solve()

            fh_results.write("%s:%s\n" % (state, " ".join(cube.solution[scramble_len:])))
            #cube.print_cube()

            if line_number and line_number % 1000 == 0:
                log.warning(line_number)
                fh_results.flush()
                break
