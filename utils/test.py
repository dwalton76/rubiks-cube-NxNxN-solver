#!/usr/bin/env python2

from rubikscubennnsolver import ImplementThis, SolveError, StuckInALoop
from rubikscubennnsolver.RubiksCube222 import RubiksCube222
from rubikscubennnsolver.RubiksCube333 import RubiksCube333
from rubikscubennnsolver.RubiksCube444 import RubiksCube444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555
import argparse
import json
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

parser = argparse.ArgumentParser()
parser.add_argument('--size', type=str, default='4x4x4')
parser.add_argument('--test-cubes', type=str, default='test_cubes.json')
args = parser.parse_args()

try:

    with open(args.test_cubes, 'r') as fh:
        test_cases = json.load(fh)

    solution_total = 0
    min_solution = None
    max_solution = None

    results = []

    for size in sorted(test_cases.keys()):

        if args.size != 'all' and size != args.size:
            continue

        '''
        # Not ready for these yet
        if size in ('6x6x6', '7x7x7'):
            continue

        # Ignore for now
        if size in ('2x2x2', '3x3x3', '4x4x4'):
            continue
        '''

        kociemba_strings = test_cases[size]
        num_test_cases = len(kociemba_strings)

        for (index, kociemba_string) in enumerate(kociemba_strings):
            log.warning("Test %d/%d %s cube: %s" % (index, num_test_cases, size, kociemba_string))

            # solve the cube
            if size == '2x2x2':
                cube = RubiksCube222(kociemba_string)

            elif size == '3x3x3':
                cube = RubiksCube333(kociemba_string)

            elif size == '4x4x4':
                cube = RubiksCube444(kociemba_string)

            elif size == '5x5x5':
                cube = RubiksCube555(kociemba_string)

            else:
                raise ImplementThis("Add support for %s" % size)

            cube.solve()
            solution = cube.solution

            # Now put the cube back in its initial state and verify the solution solves it
            # uncomment this to test compress_solution()
            #cube = RubiksCube(kociemba_string)
            #for step in solution:
            #    cube.rotate(step)

            if cube.is_solved():
                results.append("\033[92m%s PASS\033[0m: %s" % (size, kociemba_string))
                # cube.print_solution()
            else:
                results.append("\033[91m%s FAIL\033[0m: %s" % (size, kociemba_string))
                cube.print_cube()
                cube.print_solution()
                break
                '''
                for result in results:
                    print(result)

                cube.print_cube()
                assert False, "Cube should be solvd but it isn't"
                '''

            solution_length = len(cube.solution)
            solution_total += solution_length

            if min_solution is None or solution_length < min_solution:
                min_solution = solution_length

            if max_solution is None or solution_length > max_solution:
                max_solution = solution_length

        results.append("%s min solution %s steps" % (size, min_solution))
        results.append("%s max solution %s steps" % (size, max_solution))
        results.append("%s avg solution %s steps" % (size, int(solution_total/len(test_cases[size]))))
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
