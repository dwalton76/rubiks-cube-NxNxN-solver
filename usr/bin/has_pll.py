#!/usr/bin/env python3

from pprint import pformat, pprint
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
import sys

# This is only called by ida_search.c, it uses ULFRBD order
cube = RubiksCube444(sys.argv[1], "ULFRBD")
if cube.edge_solution_leads_to_pll_parity():
    print(True)
else:
    print(False)
