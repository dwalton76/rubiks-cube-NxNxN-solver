#!/usr/bin/env python3

from pprint import pformat, pprint
from rubikscubennnsolver import wing_strs_all
from rubikscubennnsolver.LookupTable import steps_on_same_face_and_layer
from rubikscubennnsolver.misc import parse_ascii_777
from rubikscubennnsolver.RubiksCube777 import RubiksCube777
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555, edges_partner_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, moves_666, solved_666, rotate_666
import itertools
import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

# Build wing_str_combos_two and wing_str_combos_four
pprint(tuple(itertools.combinations(wing_strs_all, 2)))
#pprint(tuple(itertools.combinations(wing_strs_all, 4)))


#cube = RubiksCube666(solved_666, "URFDLB")
#cube.rotate("3U")
#cube.print_cube()

'''
edges_partner_555 = {}
for side in cube.sides.values():
    for square_index in side.edge_pos:
        partner_index = side.get_wing_partner(square_index)
        edges_partner_555[square_index] = partner_index
pprint(edges_partner_555)


foo = []
for side in cube.sides.values():
    for square_index in side.edge_pos:
        partner_index = edges_partner_555[square_index]
        foo.append((square_index, partner_index))
pprint(foo)
cube.build_highlow_edge_values()
'''
