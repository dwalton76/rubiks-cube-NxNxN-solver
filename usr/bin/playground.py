# standard libraries
import logging

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)20s %(levelname)8s: %(message)s")
log = logging.getLogger(__name__)

cube = RubiksCube555(solved_555, "URFDLB")
cube.cpu_mode = "normal"
cube.lt_init()
cube.lt_foo_UD_x_centers_stage.build_ida_graph()
