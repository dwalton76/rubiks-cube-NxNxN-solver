# standard libraries
import logging

# rubiks cube libraries
from rubikscubennnsolver.RubiksCube333 import solved_333
from rubikscubennnsolver.RubiksCubeHighLowBuilder import RubiksCubeHighLow333

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)20s %(levelname)8s: %(message)s")
log = logging.getLogger(__name__)


cube = RubiksCubeHighLow333(solved_333, "URFDLB")
cube.build_highlow_edge_values()
