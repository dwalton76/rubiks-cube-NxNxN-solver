#!/usr/bin/env python3

# standard libraries
import sys

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube444 import RubiksCube444

# This is only called by ida_search.c, it uses ULFRBD order
cube = RubiksCube444(sys.argv[1], "ULFRBD")
if cube.edge_solution_leads_to_pll_parity():
    print(True)
else:
    print(False)
