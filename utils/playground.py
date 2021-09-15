#!/usr/bin/env python3

"""
Used for doing misc testing
"""

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube, configure_logging
from rubikscubennnsolver.RubiksCubeNNNOdd import solved_171717

configure_logging()
cube = RubiksCube(solved_171717, "URFDLB")
cube.randomize(count=2000)
cube.print_cube("playground")
print((cube.get_kociemba_string(True)))
