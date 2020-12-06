# standard libraries
import logging

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(filename)30s %(levelname)8s: %(message)s")
log = logging.getLogger(__name__)

filename_nn = "cube.csv"
cube = RubiksCube555(solved_555, "URFDLB")
cube.cpu_mode = "normal"
cube.lt_init()
cube.re_init()
pt_count = len(cube.lt_LR_centers_stage.prune_tables)

# BATCH_SIZE = 10000
BATCH_SIZE = 10
to_write = []
to_write_count = 0
original_state = cube.state[:]
count = 0

with open(filename_nn, "w") as fh_nn:
    fh_nn.write(",".join([f"PT{x}" for x in range(pt_count)]))
    fh_nn.write(",COST\n")

    # solve 10000 random cubes
    for x in range(10000):

        if x and x % 100 == 0:
            log.warning(f"{x:,}")

        cube.state = original_state[:]
        cube.randomize()
        cube.solution = []

        cube.lt_LR_centers_stage.solve_via_c()
        in_table = False

        for line in cube.solve_via_c_output.splitlines():
            if line.startswith("       ===  ===  ===  ===  ==="):
                in_table = True

            elif in_table:
                if line:
                    line = line.strip().split()
                    cost_to_goal = line[-2]

                    if cost_to_goal != "0":
                        nn_line = line[1 : pt_count + 1]
                        nn_line.append(cost_to_goal)
                        to_write.append(",".join(nn_line))
                        to_write_count += 1

                else:
                    in_table = False
                    break

        if to_write_count >= BATCH_SIZE:
            log.info("*" * 50)
            fh_nn.write("\n".join(to_write) + "\n")
            fh_nn.flush()
            to_write = []
            to_write_count = 0

    if to_write_count:
        fh_nn.write("\n".join(to_write) + "\n")
        fh_nn.flush()
        to_write = []
        to_write_count = 0
