#!/usr/bin/env python3

# standard libraries
import logging
import random
from typing import List

# third party libraries
import click
import numpy as np

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, centers_555, moves_555, solved_555

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


def magic(count: List[int]) -> int:
    """
    count will be a list of integers that represent the cost to solve some phase of a rubiks cube

    Example:

    [
        8,
        10, 10, 10,
        11, 11, 11, 11, 11,
        12, 12, 12, 12, 12, 12, 12, 12,
        13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13,
        14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14,
        15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
        16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16
    ]

    Our job is to return a single int that is the best cost to use:
    - returning the minimum would under estimate the majority of the time but is most likely admissable so the IDA search could still find the shortest solution
    - returning the maximum would over estimate the majority of the time and would cause too many branches to be pruned
    """

    if not count:
        return None

    if len(count) == 1:
        return count[0]

    min_cost = min(count)
    max_cost = max(count)

    data = {}

    for cost in range(min_cost, max_cost + 1):
        under_estimate_count = 0
        perfect_count = 0
        over_estimate_count = 0

        for x in count:
            if cost < x:
                under_estimate_count += 1
            elif cost == x:
                perfect_count += 1
            else:
                over_estimate_count += 1

        data[cost] = (
            float(f"{under_estimate_count / len(count):.2f}"),
            float(f"{perfect_count/ len(count):.2f}"),
            float(f"{over_estimate_count/ len(count):.2f}"),
        )

    for cost, (under_estimate_percentage, perfect_percentage, over_estimate_percentag) in data.items():
        if under_estimate_percentage <= 0.80:
            return cost

    raise Exception("we should not be here")


@cli.command()
@click.argument("filename", type=str)
def parse_csv(filename: str) -> None:
    data = {}
    max_cost = 0

    with open(filename, "r") as fh:
        for line in fh:
            line = list(map(int, line.strip().split(",")))
            cost = line[0]
            pt_cost = tuple(line[1:])

            if pt_cost not in data:
                data[pt_cost] = []

            data[pt_cost].append(cost)

    for pt_cost in data:
        data[pt_cost] = sorted(data[pt_cost])
        max_cost = max(max_cost, *pt_cost)

    shape = [max_cost + 1] * len(pt_cost)
    c_array = np.zeros(shape, dtype=int)

    for pt_cost in sorted(data.keys()):
        count = data[pt_cost]

        i0, i1, i2, i3 = pt_cost
        c_array[i0][i1][i2][i3] = magic(count)

        """
        if pt_cost == (7, 7, 6, 6):
            logger.info(count)
            logger.info(c_array[i0][i1][i2][i3])
        """

    c_array = c_array.tolist()
    # print(c_array[7][7][6][6])
    # standard libraries
    from pprint import pformat

    c_array_str = pformat(c_array)
    c_array_str = c_array_str.replace("[", "{")
    c_array_str = c_array_str.replace("]", "}")
    print(f"unsigned char foobar[9][9][9][9] = {c_array_str};")

    logger.info(f"{len(data)} pt_cost keys")


@cli.command()
@click.option("--cube-count", type=int, default=10, show_default=True, help="number of cubes to scramble")
@click.option("--move-count", type=int, default=16, show_default=True, help="number of moves for scrambling")
@click.option("--batch-size", type=int, default=10000, show_default=True, help="how often to write to disk")
@click.option("--filename", type=str, default="cube.csv", show_default=True, help="ressults filename")
def stage_centers_555(cube_count: int, move_count: int, batch_size: int, filename: str) -> None:
    """
    # To stage 555 centers in single phase is (24!/(8!*8!*8!))^2 entries
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 147 entries (0 percent, 21.00x previous step)
    3 steps has 3,054 entries (0 percent, 20.78x previous step)
    4 steps has 65,520 entries (0 percent, 21.45x previous step)
    5 steps has 1,467,630 entries (4 percent, 22.40x previous step)
    6 steps has 33,349,612 entries (95 percent, 22.72x previous step)

    # extrapolate the rest
    7 steps has 730,356,502 entries (21.90x previous step)
    8 steps has 15,410,522,192 entries (21.10x previous step)
    9 steps has 312,833,600,497 entries (20.30x previous step)
    10 steps has 6,100,255,209,691 entries (19.50x previous step)
    11 steps has 114,074,772,421,221 entries (18.70x previous step)
    12 steps has 2,041,938,426,339,855 entries (17.90x previous step)
    13 steps has 34,917,147,090,411,508 entries (17.10x previous step)
    14 steps has 569,149,497,573,707,328 entries (16.30x previous step)
    15 steps has 8,821,817,212,392,459,264 entries (15.50x previous step)
    16 steps has 80,167,866,768,488,618,872 entries (9.09x previous step)

    Average: 15.887565801237896
    Total  : 89,595,913,068,008,532,900

    # So this will take ~16 moves on average
    """

    # 100k cubes took 5m 51s and the file was 16M
    # 10 million cubes should take 9hr 45m and the file should be 1.6G
    cube = RubiksCube555(solved_555, "URFDLB")
    cube.lt_init()

    prune_tables = [
        cube.lt_LR_t_centers_stage,
        cube.lt_LR_x_centers_stage,
        cube.lt_UD_t_centers_stage,
        cube.lt_UD_x_centers_stage,
    ]

    # put the cube in the goal state for staging 555 centers
    cube.use_nuke_corners = True
    cube.use_nuke_edges = True
    cube.recolor_map = {"D": "U", "R": "L", "B": "F"}
    cube.recolor_positions = centers_555
    cube.recolor()
    cube.state_backup = cube.state[:]
    cube.logger.info_cube()
    random.seed(1234)
    lines = []
    line_count = 0

    with open(filename, "w") as fh_nn:  # noqa: F841
        # scramble CUBE_COUNT cubes up to MOVE_COUNT random moves
        for x in range(cube_count):
            cube.re_init()

            if x % 1000 == 0:
                logger.info(f"{x:,}/{cube_count:,}")

            for y in range(move_count):
                while True:
                    pre_rotate_state = cube.state[:]
                    step = random.choice(moves_555)
                    cube.rotate(step)

                    if cube.state != pre_rotate_state:
                        break

                # logger.info(f"cube {x+1}/{cube_count}, move {y+1}/{move_count}")
                # cube.logger.info_cube()
                heuristics = [y + 1]

                for pt in prune_tables:
                    pt_state = pt.state()
                    heuristics.append(pt.heuristic(pt_state))

                lines.append(",".join(map(str, heuristics)))
                line_count += 1

                if line_count >= batch_size:
                    fh_nn.write("\n".join(lines))
                    fh_nn.write("\n")
                    fh_nn.flush()
                    lines = []
                    line_count = 0

            # logger.info("\n\n\n\n\n\n\n\n")
            # cube.logger.info_cube()

        if lines:
            fh_nn.write("\n".join(lines))
            fh_nn.write("\n")
            fh_nn.flush()


@cli.command()
def lr_centers_555() -> None:
    filename_nn = "cube.csv"
    cube = RubiksCube555(solved_555, "URFDLB")
    cube.lt_init()
    cube.re_init()
    pt_count = len(cube.lt_LR_centers_stage.prune_tables)

    BATCH_SIZE = 10
    to_write = []
    to_write_count = 0
    original_state = cube.state[:]

    with open(filename_nn, "w") as fh_nn:
        fh_nn.write(",".join([f"PT{x}" for x in range(pt_count)]))
        fh_nn.write(",COST\n")

        # solve 10000 random cubes
        for x in range(10000):
            cube.state = original_state[:]
            cube.randomize()
            cube.solution = []

            cube.lt_LR_centers_stage.solve_via_c()
            logger.info(cube.solve_via_c_output)
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
                fh_nn.write("\n".join(to_write) + "\n")
                fh_nn.flush()
                to_write = []
                to_write_count = 0

        if to_write_count:
            fh_nn.write("\n".join(to_write) + "\n")
            fh_nn.flush()
            to_write = []
            to_write_count = 0


if __name__ == "__main__":
    configure_logging()
    cli()
