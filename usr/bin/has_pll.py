#!/usr/bin/env python3

"""
Called by ida_search.c to determine if a 444 has PLL or not
"""

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
