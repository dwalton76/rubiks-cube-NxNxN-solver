#!/usr/bin/env python3

"""
Print stats to correlate how many unpaired 7x7x7 UD oblique edges there are to a move count.
This was used to build the switch statement in rubikscubennnsolver/ida_search_777.c ida_heuristic_UD_oblique_edges_stage_777()
"""
# standard libraries
import json
import logging

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.misc import print_stats_median
from rubikscubennnsolver.RubiksCube777 import RubiksCube777

logger = logging.getLogger(__name__)


def main():
    data = {}

    with open("utils/10k-777-cubes.json", "r") as fh:
        cubes = json.load(fh)

    for index, state in enumerate(cubes["7x7x7"]):
        cube = RubiksCube777(state, "URFDLB")
        cube.lt_init()
        cube.stage_LR_centers()

        # stage inner x-centers and pair oblique edges in one phase
        cube.lt_UD_inner_centers.solve_via_c(use_kociemba_string=True)

        """
       UNPAIRED  EST  PT0  PT1  PER01  CTG  TRU  IDX
       ========  ===  ===  ===  =====  ===  ===  ===
 INIT         9   10    6    5      9   11   15    0
  Uw2         9   10    6    5      9   11   14    1
 3Dw2         8   10    7    4      9   11   13    2
  3Rw         6    7    7    3      9   10   12    3
  Fw2         6    7    7    3      9   10   11    4
   Rw         6    7    7    3      9   10   10    5
  Bw2         6    7    7    2      8    9    9    6
   D'         6    7    7    1      7    7    8    7
 3Lw2         5    6    6    1      6    6    7    8
 3Rw'         3    3    5    2      5    5    6    9
 3Uw2         2    2    4    2      4    4    5   10
   F'         2    2    3    2      3    3    4   11
  Rw2         2    2    3    2      3    3    3   12
    U         2    2    2    2      2    2    2   13
  3Lw         1    1    1    1      1    1    1   14
  3Rw         0    0    0    0      0    0    0   15
        """
        found_init = False

        for line in cube.solve_via_c_output.splitlines():
            logger.info(line)
            line = line.strip()

            if not found_init and line.startswith("INIT"):
                found_init = True

            if found_init and line:
                step, unpaired_count, estimate, pt0_cost, pt1_cost, per01_cost, ctg, true_cost, _index = line.split()
                unpaired_count = int(unpaired_count)
                per01_cost = int(per01_cost)

                if (unpaired_count, per01_cost) not in data:
                    data[(unpaired_count, per01_cost)] = []
                data[(unpaired_count, per01_cost)].append(int(true_cost))

        # if index and index % 10 == 0:
        if True:
            logger.warning(f"INDEX {index}")
            print_stats_median(data)
            print("\n\n")

    print_stats_median(data)


if __name__ == "__main__":
    configure_logging(logging.WARNING)
    main()
