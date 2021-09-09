#!/usr/bin/env python3

"""
Print stats to correlate 444 phase3 stage move count based centers cost and edges cost
"""
# standard libraries
import json
import logging
import random
import subprocess

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.misc import print_stats_median
from rubikscubennnsolver.RubiksCube444 import RubiksCube444

logger = logging.getLogger(__name__)
random.seed(1234)


def main():
    data = {}

    with open("utils/10k-444-cubes.json", "r") as fh:
        cubes = json.load(fh)

    for index, state in enumerate(cubes["4x4x4"]):
        cube = RubiksCube444(state, "URFDLB")
        cube.lt_init()
        cube.lt_ULFRBD_centers_stage.solve_via_c()
        cube.rotate_for_best_centers_staging()
        cube.tsai_phase2()

        try:
            cube.lt_reduce333.avoid_pll = False
            cube.lt_reduce333.solve()
        except subprocess.CalledProcessError as e:
            logger.exception(e)
            continue

        """
               CENTERS  EDGES  CTG  TRU  IDX
               =======  =====  ===  ===  ===
         INIT        0     11   11   15    0
          Uw2        1     11   11   14    1
           B'        2     12   12   13    2
           D'        2     11   11   12    3
          Lw2        3     10   10   11    4
            B        4     10   10   10    5
          Lw2        3      9    9    9    6
          Fw2        6      8    8    8    7
           U'        5      7    7    7    8
            B        4      6    6    6    9
            D        4      5    5    5   10
          Fw2        4      4    4    4   11
          Lw2        3      3    3    3   12
           B'        2      2    2    2   13
           R2        1      1    1    1   14
          Uw2        0      0    0    0   15
        """
        found_init = False
        for line in cube.solve_via_c_output.splitlines():
            line = line.strip()

            if not found_init and line.startswith("INIT"):
                found_init = True

            if found_init:
                if line:
                    step, centers_cost, edges_cost, ctg, true_cost, _index = line.split()
                    centers_cost = int(centers_cost)
                    edges_cost = int(edges_cost)

                    if (centers_cost, edges_cost) not in data:
                        data[(centers_cost, edges_cost)] = []
                    data[(centers_cost, edges_cost)].append(int(true_cost))
                else:
                    found_init = False
                    break

        if index and index % 10 == 0:
            logger.warning(f"INDEX {index}")
            print_stats_median(data)
            print("\n\n")

    print_stats_median(data)


if __name__ == "__main__":
    configure_logging(logging.WARNING)
    main()
