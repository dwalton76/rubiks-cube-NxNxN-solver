#!/usr/bin/env python3

from rubikscubennnsolver.misc import parse_ascii_777
from rubikscubennnsolver.RubiksCube777 import RubiksCube777
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

cube = RubiksCube555(solved_555, 'URFDLB')
cube.nuke_corners()
#cube.nuke_centers()
cube.print_cube()
sys.exit(0)

'''
cube = RubiksCube444(solved_444, 'URFDLB')
original_state = cube.state[:]
cube.print_cube()
cube.bitfield_create()
cube.bitfield_rotate("U2")
cube.bitfield_save()
cube.print_cube()
sys.exit(0)
'''

quarter_turns = ("U", "U'")
half_turns = ("U2",)
cube = RubiksCube444('FLDFDLBDFBLFFRRBDRFRRURBRDUBBDLURUDRRBFFBDLUBLUULUFRRFBLDDUULBDBDFLDBLUBFRFUFBDDUBFLLRFLURDULLRU', 'URFDLB')
cube.print_cube()
cube.bitfield_create()
original_state = cube.state[:]

for step in quarter_turns:
    cube.bitfield_rotate(step)
    cube.bitfield_rotate(step)
    cube.bitfield_rotate(step)
    cube.bitfield_rotate(step)
    cube.bitfield_save()

    if cube.state != original_state:
        cube.print_cube()
        assert False, "%s failed" % step

for step in half_turns:
    cube.bitfield_rotate(step)
    cube.bitfield_rotate(step)
    cube.bitfield_save()

    if cube.state != original_state:
        cube.print_cube()
        assert False, "%s failed" % step
