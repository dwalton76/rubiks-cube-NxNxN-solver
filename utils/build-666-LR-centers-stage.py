#!/usr/bin/env python3

"""
Print stats to correlate 666 LR centers stage move count based on inner x-center and oblique edges tuple
"""
# standard libraries
import json
import logging
import random

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.misc import print_stats_median
from rubikscubennnsolver.RubiksCube666 import RubiksCube666

logger = logging.getLogger(__name__)
random.seed(1234)


def main():
    data = {}

    with open("utils/10k-666-cubes.json", "r") as fh:
        cubes = json.load(fh)

    for index, state in enumerate(cubes["6x6x6"]):
        cube = RubiksCube666(state, "URFDLB")
        cube.lt_init()
        cube.lt_LR_oblique_edge_stage.solve_via_c(use_kociemba_string=True)

        """
       UNPAIRED  EST  PT0  CTG  TRU  IDX
       ========  ===  ===  ===  ===  ===
 INIT         4    4    6    0    9    0
  Fw2         4    4    6    6    8    1
   Rw         4    4    5    5    7    2
   U'         4    4    4    4    6    3
  Bw2         4    4    5    5    5    4
  3Bw         1    1    4    4    4    5
   R'         1    1    3    3    3    6
  3Dw         1    1    2    2    2    7
   Bw         1    1    1    1    1    8
  3Dw         0    0    0    0    0    9
        """
        found_init = False

        for line in cube.solve_via_c_output.splitlines():
            line = line.strip()

            if not found_init and line.startswith("INIT"):
                found_init = True

            if found_init and line:
                step, unpaired_count, estimate, pt0_cost, ctg, true_cost, _index = line.split()
                unpaired_count = int(unpaired_count)
                pt0_cost = int(pt0_cost)

                if (unpaired_count, pt0_cost) not in data:
                    data[(unpaired_count, pt0_cost)] = []
                data[(unpaired_count, pt0_cost)].append(int(true_cost))

        if index and index % 10 == 0:
            logger.warning(f"INDEX {index}")
            print_stats_median(data)
            print("\n\n")

    print_stats_median(data)


if __name__ == "__main__":
    configure_logging(logging.WARNING)
    main()
