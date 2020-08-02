# standard libraries
import argparse
import json
import logging
import sys
from pprint import pformat
from statistics import median

# rubiks cube libraries
from rubikscubennnsolver import ImplementThis, NotSolving, SolveError, StuckInALoop
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)12s %(levelname)8s: %(message)s")
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--size", type=str, default="4x4x4")
parser.add_argument("--test-cubes", type=str, default="./utils/test-cubes.json")
parser.add_argument("--start", type=int, default=0)

# cpu_mode
parser.add_argument("--fast", default=True, action="store_true", help="Find a solution quickly")
parser.add_argument("--normal", default=False, action="store_true", help="Find a shorter solution but takes longer")
parser.add_argument("--slow", default=False, action="store_true", help="Find shortest solution we can, takes a while")
args = parser.parse_args()

if args.slow:
    cpu_mode = "slow"
elif args.normal:
    cpu_mode = "normal"
elif args.fast:
    cpu_mode = "fast"
else:
    raise Exception("What CPU mode to use?")

try:

    with open(args.test_cubes, "r") as fh:
        test_cases = json.load(fh)

    solution_total = 0
    centers_solution_total = 0
    edges_solution_total = 0
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
            print("ERROR: Add support for %s" % size)
            sys.exit(1)

        kociemba_strings = test_cases[size]
        num_test_cases = len(kociemba_strings)
        num_test_cases_executed = 0

        for (index, kociemba_string) in enumerate(kociemba_strings):

            if index < args.start:
                continue

            # Only test one of each for 'all'
            if args.size == "all" and index > 0:
                continue

            # os.system('clear')
            log.warning("Test %d/%d %s cube: %s" % (index, num_test_cases, size, kociemba_string))
            num_test_cases_executed += 1
            kociemba_string = str(kociemba_string)
            cube.solution = []
            cube.load_state(kociemba_string, order)
            cube.cpu_mode = cpu_mode

            try:
                cube.solve()
                solution = cube.solution
            except NotSolving:

                if num_test_cases_executed % 100 == 0:
                    # log.info("%s: heuristic_stats raw\n%s\n\n" % (size, pformat(cube.heuristic_stats)))
                    tmp_heuristic_stats = {}

                    for (key, value) in cube.heuristic_stats.items():
                        tmp_heuristic_stats[key] = int(median(value))

                    log.info("%s: heuristic_stats median\n%s\n\n" % (size, pformat(tmp_heuristic_stats)))

                continue

            except Exception as e:
                results.append("\033[91m%s FAIL (exception) \033[0m: %s\n%s\n" % (size, kociemba_string, str(e)))
                continue

            # Now put the cube back in its initial state and verify the solution solves it
            # uncomment this to test compress_solution()
            # cube = RubiksCube(kociemba_string)
            # for step in solution:
            #    cube.rotate(step)

            if cube.solved():
                results.append("\033[92m%s PASS\033[0m: %s" % (size, kociemba_string))
                # cube.print_solution()
            else:
                results.append("\033[91m%s FAIL (not solved)\033[0m: %s" % (size, kociemba_string))
                cube.print_cube()
                cube.print_solution()
                """
                for result in results:
                    print(result)

                cube.print_cube()
                assert False, "Cube should be solvd but it isn't"
                """

            solution_length = cube.get_solution_len_minus_rotates(cube.solution)
            solution_total += solution_length
            centers_solution_total += cube.steps_to_solve_centers
            edges_solution_total += cube.steps_to_group_edges

            if min_solution is None or solution_length < min_solution:
                min_solution = solution_length
                min_solution_kociemba_string = kociemba_string

            if max_solution is None or solution_length > max_solution:
                max_solution = solution_length
                max_solution_kociemba_string = kociemba_string

        if cube.heuristic_stats:
            results.append("%s: FINAL heuristic_stats raw\n%s\n\n" % (size, pformat(cube.heuristic_stats)))

            for (key, value) in cube.heuristic_stats.items():
                cube.heuristic_stats[key] = int(median(value))

            results.append("%s: FINAL heuristic_stats median\n%s\n\n" % (size, pformat(cube.heuristic_stats)))

        results.append(
            "%s avg centers solution %s steps" % (size, float(centers_solution_total / num_test_cases_executed))
        )
        results.append("%s avg edges solution %s steps" % (size, float(edges_solution_total / num_test_cases_executed)))
        results.append("%s avg solution %s steps" % (size, float(solution_total / num_test_cases_executed)))
        results.append("%s min solution %s steps (%s)" % (size, min_solution, min_solution_kociemba_string))
        results.append("%s max solution %s steps (%s)" % (size, max_solution, max_solution_kociemba_string))
        results.append("")

    for result in results:
        print(result)

except ImplementThis:
    cube.print_cube_layout()
    raise

except SolveError:
    cube.print_cube_layout()
    cube.print_cube()
    raise

except StuckInALoop:
    cube.print_cube_layout()
    cube.print_cube()
    raise
