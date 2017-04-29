
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube222 import moves_2x2x2
import logging

log = logging.getLogger(__name__)

moves_3x3x3 = moves_2x2x2
solved_3x3x3 = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

class RubiksCube333(RubiksCube):

    def __init__(self, kociemba_string, debug=False):
        RubiksCube.__init__(self, kociemba_string, debug)

        if debug:
            log.setLevel(logging.DEBUG)

    def phase(self):
        return 'Solve 3x3x3'

    def solve(self):
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if self.get_state_all() != 'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD':
            self.solve_333()
            self.compress_solution()
