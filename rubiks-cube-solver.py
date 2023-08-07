#!/usr/bin/env python3

"""
Solve any size rubiks cube:
- For 2x2x2 and 3x3x3 just solve it
- For 4x4x4 and larger, reduce to 3x3x3 and then solve
"""

# standard libraries
import argparse
import datetime as dt
import logging
import resource
import sys
from math import sqrt

# rubiks cube libraries
from rubikscubennnsolver import SolveError, configure_logging, reverse_steps

if sys.version_info < (3, 6):
    raise SystemError("Must be using Python 3.6 or higher")

configure_logging()
logger = logging.getLogger(__name__)

logger.info("rubiks-cube-solver.py begin")

start_time = dt.datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("--print-steps", default=False, action="store_true", help="Display animated step-by-step solution")
parser.add_argument("--debug", default=False, action="store_true", help="set loglevel to DEBUG")
parser.add_argument("--no-comments", default=False, action="store_true", help="No comments in alg.cubing.net url")

# CPU mode
parser.add_argument(
    "--min-memory",
    default=False,
    action="store_true",
    help="Load smaller tables to use less memory...takes longer to run",
)

action = parser.add_mutually_exclusive_group(required=False)
parser.add_argument("--openwith", default=None, type=str, help="Colors for sides U, L, etc")
parser.add_argument("--colormap", default=None, type=str, help="Colors for sides U, L, etc")
parser.add_argument("--order", type=str, default="URFDLB", help="order of sides in --state, default kociemba URFDLB")
parser.add_argument("--solution333", type=str, default=None, help="cube explorer optimal steps for solving 3x3x3")
parser.add_argument(
    "--state",
    type=str,
    help="Cube state",
    default="LBBUUURBDDBBDFLFLUDFBFDDFLLLLRLRFRDUDBULBLFLDLFBLBUDFURURDUUBFFBBRBRLBRFLLDRRDDFRRUURRFDUFBFURUD",
)

args = parser.parse_args()

if "G" in args.state:
    args.state = args.state.replace("G", "F")
    args.state = args.state.replace("Y", "D")
    args.state = args.state.replace("O", "L")
    args.state = args.state.replace("W", "U")

if args.debug:
    logger.setLevel(logging.DEBUG)

size = int(sqrt((len(args.state) / 6)))

if size == 2:
    # rubiks cube libraries
    from rubikscubennnsolver.RubiksCube222 import RubiksCube222

    cube = RubiksCube222(args.state, args.order, args.colormap)
elif size == 3:
    # rubiks cube libraries
    from rubikscubennnsolver.RubiksCube333 import RubiksCube333

    cube = RubiksCube333(args.state, args.order, args.colormap)
elif size == 4:
    # rubiks cube libraries
    from rubikscubennnsolver.RubiksCube444 import RubiksCube444

    cube = RubiksCube444(args.state, args.order, args.colormap)
elif size == 5:
    # rubiks cube libraries
    from rubikscubennnsolver.RubiksCube555 import RubiksCube555

    cube = RubiksCube555(args.state, args.order, args.colormap)
elif size == 6:
    # rubiks cube libraries
    from rubikscubennnsolver.RubiksCube666 import RubiksCube666

    cube = RubiksCube666(args.state, args.order, args.colormap)
elif size == 7:
    # rubiks cube libraries
    from rubikscubennnsolver.RubiksCube777 import RubiksCube777

    cube = RubiksCube777(args.state, args.order, args.colormap)
elif size % 2 == 0:
    # rubiks cube libraries
    from rubikscubennnsolver.RubiksCubeNNNEven import RubiksCubeNNNEven

    cube = RubiksCubeNNNEven(args.state, args.order, args.colormap)
else:
    # rubiks cube libraries
    from rubikscubennnsolver.RubiksCubeNNNOdd import RubiksCubeNNNOdd

    cube = RubiksCubeNNNOdd(args.state, args.order, args.colormap)

cube.sanity_check()
cube.print_cube("Initial Cube")
cube.www_header()
cube.www_write_cube("Initial Cube")

if args.openwith:
    for step in args.openwith.split():
        cube.rotate(step)
    cube.print_cube("post --openwith")

if args.solution333:
    solution333 = reverse_steps(args.solution333.split())
else:
    solution333 = []

cube.solve(solution333)
end_time = dt.datetime.now()
cube.print_cube("Final Cube")
cube.print_solution(not args.no_comments)

logger.info("*********************************************************************************")
logger.info("See /tmp/rubiks-cube-NxNxN-solver/index.html for more detailed solve instructions")
logger.info("*********************************************************************************\n")

# Now put the cube back in its initial state and verify the solution solves it
solution = cube.solution
cube.re_init()
len_steps = len(solution)

for i, step in enumerate(solution):
    if args.print_steps:
        print(("Move %d/%d: %s" % (i + 1, len_steps, step)))

    cube.rotate(step)

    www_desc = "Cube After Move %d/%d: %s<br>\n" % (i + 1, len_steps, step)
    cube.www_write_cube(www_desc)

    if args.print_steps:
        cube.print_cube(f"--print-steps {step}")
        print("\n\n\n\n")

cube.www_footer()

if args.print_steps:
    cube.print_cube("--print-steps DONE")

if args.min_memory:
    print("\n\n****************************************")
    print("--min-memory has been replaced by --fast")
    print("****************************************\n\n")

logger.info("rubiks-cube-solver.py end")
logger.info(f"Memory : {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss:,} bytes")
logger.info(f"Time   : {end_time - start_time}")
logger.info("")

if not cube.solved():
    raise SolveError("cube should be solved but is not")
