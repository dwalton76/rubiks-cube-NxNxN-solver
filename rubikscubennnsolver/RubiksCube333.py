
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube222 import moves_2x2x2
import logging

log = logging.getLogger(__name__)

moves_3x3x3 = moves_2x2x2

class RubiksCube333(RubiksCube):

    def solve(self):
        self.rotate_U_to_U()
        self.rotate_F_to_F()
        self.solve_333()
        self.compress_solution()
