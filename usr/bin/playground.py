#!/usr/bin/env python3

from pprint import pformat
from rubikscubennnsolver.LookupTable import steps_on_same_face_and_layer
from rubikscubennnsolver.misc import parse_ascii_777
from rubikscubennnsolver.RubiksCube777 import RubiksCube777
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555, get_wings_edges_will_pair
from rubikscubennnsolver.RubiksCube777 import RubiksCube666, moves_666
import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

#get_wings_edges_will_pair(
#    "OOOyPXzqRQrPSSSTTTUUUVVVqWwxxWrYYpZZ",
#    "OOO---z-----SSSTTTUUUVVV-Ww---YYYWZZ"
#)

cube = RubiksCube555(solved_555, "URFDLB")
cube.rotate("Uw")
cube.rotate("U'")
cube.print_cube()
cube.re_init()

cube.rotate("Uw'")
cube.rotate("U")
cube.print_cube()
