#!/usr/bin/env python3

# standard libraries
import argparse
import json
import logging
import sys

# rubiks cube libraries
from rubikscubennnsolver import SolveError, StuckInALoop, configure_logging
from rubikscubennnsolver.RubiksCube222 import RubiksCube222, solved_222
from rubikscubennnsolver.RubiksCube333 import RubiksCube333, solved_333
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_666
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, solved_777
from rubikscubennnsolver.RubiksCubeNNNEven import (
    RubiksCubeNNNEven,
    solved_888,
    solved_101010,
    solved_121212,
    solved_141414,
)
from rubikscubennnsolver.RubiksCubeNNNOdd import (
    RubiksCubeNNNOdd,
    solved_999,
    solved_111111,
    solved_131313,
    solved_151515,
)

configure_logging()
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--size", type=str, default="4x4x4")
parser.add_argument("--test-cubes", type=str, default="./utils/test-cubes.json")
parser.add_argument("--start", type=int, default=0)

args = parser.parse_args()

try:
    with open(args.test_cubes, "r") as fh:
        test_cases = json.load(fh)

    solution_total = 0
    min_solution = None
    max_solution = None
    min_solution_kociemba_string = None
    max_solution_kociemba_string = None

    results = []
    order = "URFDLB"

    for size in sorted(test_cases.keys()):
        if args.size != "all" and size != args.size:
            continue

        # solve the cube
        if size == "2x2x2":
            cube = RubiksCube222(solved_222, order)

        elif size == "3x3x3":
            cube = RubiksCube333(solved_333, order)

        elif size == "4x4x4":
            cube = RubiksCube444(solved_444, order)

        elif size == "5x5x5":
            cube = RubiksCube555(solved_555, order)

        elif size == "6x6x6":
            cube = RubiksCube666(solved_666, order)

        elif size == "7x7x7":
            cube = RubiksCube777(solved_777, order)

        elif size == "8x8x8":
            cube = RubiksCubeNNNEven(solved_888, order)

        elif size == "9x9x9":
            cube = RubiksCubeNNNOdd(solved_999, order)

        elif size == "10x10x10":
            cube = RubiksCubeNNNEven(solved_101010, order)

        elif size == "11x11x11":
            cube = RubiksCubeNNNOdd(solved_111111, order)

        elif size == "12x12x12":
            continue  # no need to test above 10x10x10
            cube = RubiksCubeNNNEven(solved_121212, order)

        elif size == "13x13x13":
            continue  # no need to test above 11x11x11
            cube = RubiksCubeNNNOdd(solved_131313, order)

        elif size == "14x14x14":
            continue  # no need to test above 10x10x10
            cube = RubiksCubeNNNEven(solved_141414, order)

        elif size == "15x15x15":
            continue  # no need to test above 11x11x11
            cube = RubiksCubeNNNOdd(solved_151515, order)

        else:
            print(f"ERROR: Add support for {size}")
            sys.exit(1)

        kociemba_strings = test_cases[size]
        num_test_cases = len(kociemba_strings)
        num_test_cases_executed = 0

        for index, kociemba_string in enumerate(kociemba_strings):
            if index < args.start:
                continue

            # Only test one of each for 'all'
            if args.size == "all" and index > 0:
                continue

            logger.warning("Test %d/%d %s cube: %s" % (index, num_test_cases, size, kociemba_string))
            num_test_cases_executed += 1
            kociemba_string = str(kociemba_string)
            cube.solution = []
            cube.load_state(kociemba_string, order)

            try:
                cube.solve()
                solution = cube.solution
            except Exception as e:
                results.append(f"[91m{size} FAIL (exception) [0m: {kociemba_string}\n{str(e)}\n")
                continue

            # Now put the cube back in its initial state and verify the solution solves it
            # uncomment this to test compress_solution()
            # cube = RubiksCube(kociemba_string)
            # for step in solution:
            #    cube.rotate(step)

            if cube.solved():
                results.append(f"[92m{size} PASS[0m: {kociemba_string}")
            else:
                results.append(f"[91m{size} FAIL (not solved)[0m: {kociemba_string}")
                cube.print_cube("failed to solve")
                cube.print_solution()

            solution_length = cube.get_solution_len_minus_rotates(cube.solution)
            solution_total += solution_length

            if min_solution is None or solution_length < min_solution:
                min_solution = solution_length
                min_solution_kociemba_string = kociemba_string

            if max_solution is None or solution_length > max_solution:
                max_solution = solution_length
                max_solution_kociemba_string = kociemba_string

        results.append(f"{size} avg solution {float(solution_total / num_test_cases_executed)} steps")
        results.append(f"{size} min solution {min_solution} steps ({min_solution_kociemba_string})")
        results.append(f"{size} max solution {max_solution} steps ({max_solution_kociemba_string})")
        results.append("")

    for result in results:
        print(result)

except (NotImplementedError, SolveError, StuckInALoop) as e:
    cube.print_cube_layout()
    cube.print_cube(str(e))
    raise e
