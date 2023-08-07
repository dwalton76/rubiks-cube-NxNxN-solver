#!/usr/bin/env python3

"""
Print stats to correlate 555 LR centers stage move count based on x-center, t-center move count tuple.
"""
# standard libraries
import json
import logging
import random

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.misc import print_stats_median
from rubikscubennnsolver.RubiksCube555 import RubiksCube555

logger = logging.getLogger(__name__)
random.seed(1234)


def main():
    data = {}

    with open("utils/10k-555-cubes.json", "r") as fh:
        cubes = json.load(fh)

    for index, state in enumerate(cubes["5x5x5"]):
        cube = RubiksCube555(state, "URFDLB")
        cube.lt_init()

        # phase 1
        cube.group_centers_stage_LR()

        """
       PT0  PT1  PT2  PT3  PT4  PER01  PER02  CTG  TRU  IDX
       ===  ===  ===  ===  ===  =====  =====  ===  ===  ===
  INIT   7    6    0    0    0      0      0    0   11    0
    D    7    6    0    0    0      0      0    8   10    1
  Fw'    6    6    0    0    0      0      0    7    9    2
    U    5    6    0    0    0      0      0    7    8    3
  Bw'    5    5    0    0    0      0      0    5    7    4
  Rw2    5    5    0    0    0      0      0    5    6    5
   Lw    4    4    0    0    0      0      0    4    5    6
  Dw'    3    3    0    0    0      0      0    3    4    7
   Rw    2    3    0    0    0      0      0    3    3    8
  Lw2    2    2    0    0    0      0      0    2    2    9
    L    1    1    0    0    0      0      0    1    1   10
  Bw'    0    0    0    0    0      0      0    0    0   11
        """
        found_init = False
        for line in cube.solve_via_c_output.splitlines():
            line = line.strip()

            if not found_init and line.startswith("INIT"):
                found_init = True

            if found_init and line:
                (
                    step,
                    pt0_cost,
                    pt1_cost,
                    pt2_cost,
                    pt3_cost,
                    pt4_cost,
                    per01_cost,
                    per02_cost,
                    ctg,
                    true_cost,
                    _index,
                ) = line.split()
                pt0_cost = int(pt0_cost)
                pt1_cost = int(pt1_cost)
                pt2_cost = int(pt2_cost)
                pt3_cost = int(pt3_cost)
                pt4_cost = int(pt4_cost)

                if (pt0_cost, pt1_cost) not in data:
                    data[(pt0_cost, pt1_cost)] = []
                data[(pt0_cost, pt1_cost)].append(int(true_cost))

        if index and index % 100 == 0:
            logger.warning(f"INDEX {index}")
            print_stats_median(data)
            print("\n\n")

    print_stats_median(data)


if __name__ == "__main__":
    configure_logging(logging.WARNING)
    main()
