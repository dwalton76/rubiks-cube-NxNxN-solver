#!/usr/bin/env python3

"""
Print stats to correlate how many unpaired 7x7x7 LR oblique edges there are to a move count.
This was used to build the switch statement in rubikscubennnsolver/ida_search_777.c ida_heuristic_LR_oblique_edges_stage_777()
"""
# standard libraries
import json
import logging
import random

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.misc import print_stats_median
from rubikscubennnsolver.RubiksCube777 import RubiksCube777

logger = logging.getLogger(__name__)
random.seed(1234)

# fmt: off
left_oblique_edges_777 = [
    10, 30, 20, 40,      # Upper
    59, 79, 69, 89,      # Left
    108, 128, 118, 138,  # Front
    157, 177, 167, 187,  # Right
    206, 226, 216, 236,  # Back
    255, 275, 265, 285,  # Down
]

middle_oblique_edges_777 = [
    11, 23, 27, 39,      # Upper
    60, 72, 76, 88,      # Left
    109, 121, 125, 137,  # Front
    158, 170, 174, 186,  # Right
    207, 219, 223, 235,  # Back
    256, 268, 272, 284,  # Down
]

right_oblique_edges_777 = [
    12, 16, 34, 38,      # Upper
    61, 65, 83, 87,      # Left
    110, 114, 132, 136,  # Front
    159, 163, 181, 185,  # Right
    208, 212, 230, 234,  # Back
    257, 261, 279, 283,  # Down
]
# fmt: on


def unpaired_obliques_count_777(cube: RubiksCube777) -> int:
    left_paired_obliques = 0
    left_unpaired_obliques = 8
    right_paired_obliques = 0
    right_unpaired_obliques = 8

    for left_cube_index, middle_cube_index, right_cube_index in zip(
        left_oblique_edges_777, middle_oblique_edges_777, right_oblique_edges_777
    ):
        if cube.state[middle_cube_index] in ("L", "R"):
            if cube.state[left_cube_index] in ("L", "R"):
                left_paired_obliques += 1

            if cube.state[right_cube_index] in ("L", "R"):
                right_paired_obliques += 1

    left_unpaired_obliques -= left_paired_obliques
    right_unpaired_obliques -= right_paired_obliques
    return left_unpaired_obliques + right_unpaired_obliques


def main():
    data = {}

    with open("utils/10k-777-cubes.json", "r") as fh:
        cubes = json.load(fh)

    for index, state in enumerate(cubes["7x7x7"]):
        cube = RubiksCube777(state, "URFDLB")
        cube.lt_init()

        # phase 1
        cube.group_inside_LR_centers()
        phase1_state = cube.state[:]
        phase1_solution = cube.solution[:]
        phase1_solution_len = len(phase1_solution)

        # phase 2 - pair the oblique edges
        cube.lt_LR_oblique_edge_pairing.solve()
        LR_oblique_solution = cube.solution[phase1_solution_len:]
        LR_oblique_solution_len = len(LR_oblique_solution)
        cube.state = phase1_state
        cube.solution = phase1_solution

        total_count = unpaired_obliques_count_777(cube)
        logger.warning(
            f"7x7x7 cube #{index:04d}, LR_oblique_solution_len {LR_oblique_solution_len}, unpaired count {total_count}"
        )

        if total_count not in data:
            data[total_count] = []
        data[total_count].append(LR_oblique_solution_len)

        for step_index, step in enumerate(LR_oblique_solution):
            cube.rotate(step)
            total_count = unpaired_obliques_count_777(cube)

            """
            logger.warning(
                f"{step_index+1}/{LR_oblique_solution_len} post {step} unpaired count {total_count} ({left_count} left, {right_count} right), "
                f"move to go {LR_oblique_solution_len - step_index - 1}"
            )
            """
            if total_count not in data:
                data[total_count] = []
            data[total_count].append(LR_oblique_solution_len - step_index - 1)

        if index and index % 100 == 0:
            logger.warning(f"INDEX {index}")
            print_stats_median(data)
            print("\n\n")

    print_stats_median(data)


if __name__ == "__main__":
    configure_logging(logging.WARNING)
    main()
