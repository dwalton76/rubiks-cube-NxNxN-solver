#!/usr/bin/env python3

# standard libraries
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)20s %(levelname)8s: %(message)s")
log = logging.getLogger(__name__)

pt_state_filename = sys.argv[1]
perfect_hash_filename = pt_state_filename.replace("pt_state", "pt-state-perfect-hash")
pt0_max = int(sys.argv[2])
pt1_max = int(sys.argv[3])

result = ["0"] * pt0_max * pt1_max
log.info(f"pt0_max {pt0_max:,}, pt1_max {pt1_max:,}, result {len(result):,} entries")

with open(pt_state_filename, "r") as fh_read:
    for (line_number, line) in enumerate(fh_read):
        (pt_state, cost) = line.rstrip().split(":")
        (pt0_state, pt1_state) = pt_state.split("-")
        pt0_state = int(pt0_state)
        pt1_state = int(pt1_state)

        index = (pt0_state * pt1_max) + pt1_state

        if int(cost) <= 9:
            pass
        elif cost == "10":
            cost = "a"
        elif cost == "11":
            cost = "b"
        elif cost == "12":
            cost = "c"
        elif cost == "13":
            cost = "d"
        elif cost == "14":
            cost = "e"
        elif cost == "15":
            cost = "f"
        else:
            raise Exception(f"cost {cost} too high")

        try:
            result[index] = cost
        except IndexError:
            log.info(f"pt0_state {pt0_state:,}, pt1_state {pt1_state:,}, index {index:,}, cost {cost}")
            raise

        if line_number % 1000000 == 0:
            log.info(f"{line_number:,}")

with open(perfect_hash_filename, "w") as fh:
    fh.write("".join(result))
