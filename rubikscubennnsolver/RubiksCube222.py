
from rubikscubennnsolver import RubiksCube, SolveError, LookupTable
import logging

log = logging.getLogger(__name__)


moves_2x2x2 = ("U", "U'", "U2",
               "L", "L'", "L2",
               "F" , "F'", "F2",
               "R" , "R'", "R2",
               "B" , "B'", "B2",
               "D" , "D'", "D2")


class RubiksCube222(RubiksCube):

    def __init__(self, kociemba_string):
        RubiksCube.__init__(self, kociemba_string)
        self.lt = LookupTable(self, 'lookup-table-2x2x2-solve.txt', 'all', 'UUUULLLLFFFFRRRRBBBBDDDD')

    def solve(self):
        """
        lookup-table-2x2x2-solve.txt was constructed using only:
            U, U', U2, B, B', B2, R, R' and R2

        so we must rotate the LFD corner to be at LFD. Rotating doesn't add
        to our move count as they are compressed out in compress_solution().
        """
        if self.state[16] == 'L' and self.state[19] == 'F' and self.state[24] == 'D':
            self.rotate_y()
            self.rotate_y()
        elif self.state[24] == 'L' and self.state[16] == 'F' and self.state[19] == 'D':
            self.rotate_x()
            self.rotate_y()
        elif self.state[23] == 'L' and self.state[20] == 'F' and self.state[7] == 'D':
            self.rotate_x()
            self.rotate_z_reverse()
            self.rotate_y()
        elif self.state[1] == 'L' and self.state[5] == 'F' and self.state[18] == 'D':
            self.rotate_x()
            self.rotate_y_reverse()
        elif self.state[15] == 'L' and self.state[22] == 'F' and self.state[12] == 'D':
            self.rotate_y()
            self.rotate_x()
            self.rotate_z_reverse()
        elif self.state[6] == 'L' and self.state[3] == 'F' and self.state[9] == 'D':
            self.rotate_x_reverse()
        elif self.state[11] == 'L' and self.state[21] == 'F' and self.state[8] == 'D':
            self.rotate_x()
            self.rotate_z_reverse()
        elif self.state[17] == 'L' and self.state[14] == 'F' and self.state[2] == 'D':
            self.rotate_x()
            self.rotate_x()
            self.rotate_y()
        elif self.state[5] == 'L' and self.state[18] == 'F' and self.state[1] == 'D':
            self.rotate_x()
            self.rotate_x()
        elif self.state[10] == 'L' and self.state[4] == 'F' and self.state[13] == 'D':
            self.rotate_z()
            self.rotate_y()
        elif self.state[4] == 'L' and self.state[13] == 'F' and self.state[10] == 'D':
            self.rotate_x_reverse()
            self.rotate_y()
        elif self.state[14] == 'L' and self.state[2] == 'F' and self.state[17] == 'D':
            self.rotate_x()
            self.rotate_y()
            self.rotate_y()
        elif self.state[22] == 'L' and self.state[12] == 'F' and self.state[15] == 'D':
            self.rotate_z()
        elif self.state[8] == 'L' and self.state[11] == 'F' and self.state[21] == 'D':
            pass
        elif self.state[3] == 'L' and self.state[9] == 'F' and self.state[6] == 'D':
            self.rotate_z_reverse()
        elif self.state[12] == 'L' and self.state[15] == 'F' and self.state[22] == 'D':
            self.rotate_y()
        elif self.state[2] == 'L' and self.state[17] == 'F' and self.state[14] == 'D':
            self.rotate_z()
            self.rotate_y()
            self.rotate_y()
        elif self.state[13] == 'L' and self.state[10] == 'F' and self.state[4] == 'D':
            self.rotate_z()
            self.rotate_z()
        elif self.state[9] == 'L' and self.state[6] == 'F' and self.state[3] == 'D':
            self.rotate_z()
            self.rotate_z()
            self.rotate_y()
        elif self.state[21] == 'L' and self.state[8] == 'F' and self.state[11] == 'D':
            self.rotate_x_reverse()
            self.rotate_y_reverse()
        elif self.state[19] == 'L' and self.state[24] == 'F' and self.state[16] == 'D':
            self.rotate_x()
            self.rotate_z()
        elif self.state[18] == 'L' and self.state[1] == 'F' and self.state[5] == 'D':
            self.rotate_y_reverse()
            self.rotate_x_reverse()
        elif self.state[20] == 'L' and self.state[7] == 'F' and self.state[23] == 'D':
            self.rotate_y_reverse()
        elif self.state[7] == 'L' and self.state[23] == 'F' and self.state[20] == 'D':
            self.rotate_x()
        else:
            raise SolveError("Implement this")

        # lt is a LookupTable object for lookup-table-2x2x2-solve.txt
        self.lt.solve()
        self.compress_solution()
