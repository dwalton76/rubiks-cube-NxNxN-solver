#!/usr/bin/env python2

from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_6x6x6
from pprint import pformat
import logging
import sys


def reverse_steps(steps):
    results = []
    for step in reversed(steps):
        if step.endswith("2"):
            pass
        elif step.endswith("'"):
            step = step[0:-1]
        else:
            step += "'"
        results.append(step)
    return results


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    filename = sys.argv[1]


    # This is all a bit hardcoded for now
    #if 'foo.txt' in filename:
    if 'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt' in filename:
        max_depth = 9
        data = {}
        cube = RubiksCube666(solved_6x6x6, 'URFDLB')
        cube.lt_init()
        original_state = cube.state[:]
        original_solution = cube.solution[:]

        for x in range(1, max_depth+1):
            log.info("x %d" % x)
            with open(filename, 'r') as fh:
                for line in fh:
                    (state, steps) = line.rstrip().split(':')
                    steps = steps.split()

                    if len(steps) == x:
                        cube.state = original_state[:]
                        cube.solution = original_solution[:]

                        # create a solved cube
                        # reverse the steps and apply them
                        # get the cost of cube in each prune table
                        actual_cost_to_goal = 0

                        for step in steps:
                            result = cube.lt_LFRB_solve_inner_x_centers_and_oblique_edges.ida_heuristic_all_costs()
                            LR_cost = result['lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt']
                            FB_cost = result['lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt']

                            if (LR_cost, FB_cost) not in data:
                                data[(LR_cost, FB_cost)] = actual_cost_to_goal
                            cube.rotate(step)
                            actual_cost_to_goal += 1

                        #log.info("STATS:\n%s\n" % pformat(stats))
        log.info("DATA:\n%s\n" % pformat(data))
    else:
        raise Exception("Add support for %s" % filename)
