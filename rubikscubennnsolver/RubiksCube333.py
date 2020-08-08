# standard libraries
import logging

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.LookupTable import LookupTable
from rubikscubennnsolver.RubiksCube222 import moves_222
from rubikscubennnsolver.swaps import swaps_333

log = logging.getLogger(__name__)

moves_333 = moves_222
solved_333 = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
centers_333 = (5, 14, 23, 32, 41, 50)

edges_333 = (2, 4, 6, 8, 11, 13, 15, 17, 20, 22, 24, 26, 29, 31, 33, 35, 38, 40, 42, 44, 47, 49, 51, 53)

corners_333 = (1, 3, 7, 9, 10, 12, 16, 18, 19, 21, 25, 27, 28, 30, 34, 36, 37, 39, 43, 45, 46, 48, 52, 54)


class LookupTable333Phase2Edges(LookupTable):
    """
    lookup-table-3x3x3-step11-edges.txt
    ===================================
    1 steps has 10 entries (0 percent, 0.00x previous step)
    2 steps has 68 entries (0 percent, 6.80x previous step)
    3 steps has 456 entries (0 percent, 6.71x previous step)
    4 steps has 3063 entries (0 percent, 6.72x previous step)
    5 steps has 18202 entries (1 percent, 5.94x previous step)
    6 steps has 86691 entries (8 percent, 4.76x previous step)
    7 steps has 290812 entries (30 percent, 3.35x previous step)
    8 steps has 434814 entries (44 percent, 1.50x previous step)
    9 steps has 120488 entries (12 percent, 0.28x previous step)
    10 steps has 11818 entries (1 percent, 0.10x previous step)
    11 steps has 1114 entries (0 percent, 0.09x previous step)
    12 steps has 144 entries (0 percent, 0.13x previous step)

    Total: 967680 entries
    Average: 7.601348 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-3x3x3-step11-edges.txt",
            "UUUULLLLFFFFRRRRBBBBDDDD",
            linecount=967680,
            max_depth=12,
        )

    def state(self):
        parent_state = self.parent.state
        result = "".join([parent_state[x] for x in edges_333])
        return result


class LookupTable333Phase2Corners(LookupTable):
    """
    lookup-table-3x3x3-step12-corners.txt
    =====================================
    1 steps has 10 entries (0 percent, 0.00x previous step)
    2 steps has 68 entries (0 percent, 6.80x previous step)
    3 steps has 330 entries (0 percent, 4.85x previous step)
    4 steps has 752 entries (1 percent, 2.28x previous step)
    5 steps has 1400 entries (3 percent, 1.86x previous step)
    6 steps has 2752 entries (6 percent, 1.97x previous step)
    7 steps has 4384 entries (10 percent, 1.59x previous step)
    8 steps has 6208 entries (15 percent, 1.42x previous step)
    9 steps has 7136 entries (17 percent, 1.15x previous step)
    10 steps has 8064 entries (20 percent, 1.13x previous step)
    11 steps has 6528 entries (16 percent, 0.81x previous step)
    12 steps has 2432 entries (6 percent, 0.37x previous step)
    13 steps has 256 entries (0 percent, 0.11x previous step)

    Total: 40320 entries
    Average: 8.858929 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-3x3x3-step12-corners.txt",
            "UUUULLLLFFFFRRRRBBBBDDDD",
            linecount=40320,
            max_depth=13,
        )

    def state(self):
        parent_state = self.parent.state
        result = "".join([parent_state[x] for x in corners_333])
        return result


class RubiksCube333(RubiksCube):

    reduce333_orient_edges_tuples = (
        (2, 38),
        (4, 11),
        (6, 29),
        (8, 20),
        (13, 42),
        (15, 22),
        (24, 31),
        (33, 40),
        (47, 26),
        (49, 17),
        (51, 35),
        (53, 44),
    )

    def phase(self):
        return "Solve 3x3x3"

    def solve(self, solution333=None):
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if self.get_state_all() != "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD":
            self.solve_333()
            self.compress_solution()

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_phase2_edges = LookupTable333Phase2Edges(self)
        self.lt_phase2_corners = LookupTable333Phase2Corners(self)


def rotate_333(cube, step):
    return [cube[x] for x in swaps_333[step]]
