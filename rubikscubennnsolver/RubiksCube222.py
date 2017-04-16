
from rubikscubennnsolver import RubiksCube
import logging
import subprocess

log = logging.getLogger(__name__)


moves_2x2x2 = ("U", "U'", "U2",
               "L", "L'", "L2",
               "F" , "F'", "F2",
               "R" , "R'", "R2",
               "B" , "B'", "B2",
               "D" , "D'", "D2")


class RubiksCube222(RubiksCube):

    def solve(self):
        # TODO
        # - rotate the left/front/down (green, red, yellow) corner to be at left/front/down
        # - then use lookup-table-2x2x2-solve.txt
        steps = subprocess.check_output(['rubiks_2x2x2_solver.py', self.get_kociemba_string(True)]).decode('ascii').splitlines()[-1].strip().split()

        for step in steps:
            self.rotate(step)
        self.rotate_U_to_U()
        self.rotate_F_to_F()
