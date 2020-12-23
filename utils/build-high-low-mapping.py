"""
Ran once for 333, 444, 555 and 666 cubes to generate
"""
# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.RubiksCube333 import solved_333
from rubikscubennnsolver.RubiksCubeHighLowBuilder import RubiksCubeHighLow333

configure_logging()
cube = RubiksCubeHighLow333(solved_333, "URFDLB")
cube.build_highlow_edge_values()
