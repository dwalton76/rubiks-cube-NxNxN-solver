"""
Used for doing misc testing
"""

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555

configure_logging()
cube = RubiksCube555(solved_555, "URFDLB")
cube.cpu_mode = "normal"
cube.lt_init()
cube.lt_foo_UD_x_centers_stage.build_ida_graph()
