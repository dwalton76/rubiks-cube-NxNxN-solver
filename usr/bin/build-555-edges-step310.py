#!/usr/bin/env python3

"""
This
- parses all of the edge patterns in lookup-table-5x5x5-step301-edges-x-plane-edges-only.txt
- puts the centers back to solved
- runs step300 IDA to find the solution for each edge pattern when the centers are solved

This is used by --fast solves so they do not have to run IDA for step300
"""

from rubikscubennnsolver import reverse_steps, wing_str_map
from rubikscubennnsolver.RubiksCube555 import solved_555, edges_partner_555
from rubikscubennnsolver.RubiksCube555ForNNN import RubiksCube555ForNNN
import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

cube = RubiksCube555ForNNN(solved_555, "URFDLB")
cube.lt_init()

with open("results.txt", "w") as fh_results:
    with open("lookup-table-5x5x5-step301-edges-x-plane-edges-only.txt", "r") as fh:
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

            scramble_len = len(cube.solution)

            # The 4 paired edges are in the x-plane
            only_colors = []
            for square_index in (36, 40, 86, 90):
                partner_index = edges_partner_555[square_index]
                square_value = cube.state[square_index]
                partner_value = cube.state[partner_index]
                wing_str = wing_str_map[square_value + partner_value]
                only_colors.append(wing_str)

            cube.lt_edges_x_plane_edges_only.only_colors = only_colors
            cube.lt_edges_x_plane.only_colors = only_colors
            cube.lt_edges_x_plane.solve()

            fh_results.write("%s:%s\n" % (state, " ".join(cube.solution[scramble_len:])))

            if line_number % 100 == 0:
                log.warning(line_number)
                fh_results.flush()
