
from itertools import combinations
from rubikscubennnsolver.RubiksCubeNNNEvenEdges import RubiksCubeNNNEvenEdges
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666Misc import (
    lt_LFRB_solve_inner_x_centers_and_oblique_edges_state_targets,
    state_targets_step30,
    state_targets_step31,
)
from rubikscubennnsolver.LookupTable import (
    LookupTable,
    LookupTableCostOnly,
    LookupTableHashCostOnly,
    LookupTableIDA
)
from pprint import pformat
import json
import logging
import math
import sys

log = logging.getLogger(__name__)


moves_666 = (
    "U", "U'", "U2", "Uw", "Uw'", "Uw2", "3Uw", "3Uw'", "3Uw2",
    "L", "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2",
    "F" , "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2",
    "R" , "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2",
    "B" , "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2",
    "D" , "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2"
)
solved_666 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'


set_UD = set(('U', 'D'))
set_LR = set(('L', 'R'))

inner_x_centers_666 = (
    15, 16, 21, 22,
    51, 52, 57, 58,
    87, 88, 93, 94,
    123, 124, 129, 130,
    159, 160, 165, 166,
    195, 196, 201, 202
)

LFRB_inner_x_centers_666 = (
    51, 52, 57, 58,
    87, 88, 93, 94,
    123, 124, 129, 130,
    159, 160, 165, 166,
)

centers_666 = (
    8, 9, 10, 11, 14, 15, 16, 17, 20, 21, 22, 23, 26, 27, 28, 29,
    44, 45, 46, 47, 50, 51, 52, 53, 56, 57, 58, 59, 62, 63, 64, 65,
    80, 81, 82, 83, 86, 87, 88, 89, 92, 93, 94, 95, 98, 99, 100, 101,
    116, 117, 118, 119, 122, 123, 124, 125, 128, 129, 130, 131, 134, 135, 136, 137,
    152, 153, 154, 155, 158, 159, 160, 161, 164, 165, 166, 167, 170, 171, 172, 173,
    188, 189, 190, 191, 194, 195, 196, 197, 200, 201, 202, 203, 206, 207, 208, 209
)

UD_centers_666 = (
    8, 9, 10, 11, 14, 15, 16, 17, 20, 21, 22, 23, 26, 27, 28, 29,
    188, 189, 190, 191, 194, 195, 196, 197, 200, 201, 202, 203, 206, 207, 208, 209
)

FB_centers_666 = (
    80, 81, 82, 83, 86, 87, 88, 89, 92, 93, 94, 95, 98, 99, 100, 101,
    152, 153, 154, 155, 158, 159, 160, 161, 164, 165, 166, 167, 170, 171, 172, 173,
)

UFBD_centers_666 = (
    8, 9, 10, 11, 14, 15, 16, 17, 20, 21, 22, 23, 26, 27, 28, 29,
    80, 81, 82, 83, 86, 87, 88, 89, 92, 93, 94, 95, 98, 99, 100, 101,
    152, 153, 154, 155, 158, 159, 160, 161, 164, 165, 166, 167, 170, 171, 172, 173,
    188, 189, 190, 191, 194, 195, 196, 197, 200, 201, 202, 203, 206, 207, 208, 209
)

step60_centers_666 = (
    # Left
        45, 46,
    50, 51, 52, 53,
    56, 57, 58, 59,
        63, 64,

    # Front
        81, 82,
    86, 87, 88, 89,
    92, 93, 94, 95,
        99, 100,

    # Right
         117, 118,
    122, 123, 124, 125,
    128, 129, 130, 131,
         135, 136,

    # Back
         153, 154,
    158, 159, 160, 161,
    164, 165, 166, 167,
         171, 172,
)

step61_centers_666 = (
    # Left
        45, 46,
    50, 51, 52, 53,
    56, 57, 58, 59,
        63, 64,

    # Right
         117, 118,
    122, 123, 124, 125,
    128, 129, 130, 131,
         135, 136,
)

step62_centers_666 = (
    # Front
        81, 82,
    86, 87, 88, 89,
    92, 93, 94, 95,
        99, 100,

    # Back
         153, 154,
    158, 159, 160, 161,
    164, 165, 166, 167,
         171, 172,
)

UDFB_left_oblique_edges = (9, 17, 28, 20, 189, 197, 208, 200, 81, 89, 100, 92, 153, 161, 172, 164)
UDFB_right_oblique_edges = (10, 23, 27, 14, 190, 203, 207, 194, 82, 95, 99, 86, 154, 167, 171, 158)
UDFB_outer_x_centers = (8, 11, 26, 29, 188, 191, 206, 209, 80, 83, 98, 101, 152, 155, 170, 173)
UDFB_inner_x_centers = (15, 16, 21, 22, 195, 196, 201, 202, 87, 88, 93, 94, 159, 160, 165, 166)

LR_left_oblique_edges = (45, 53, 64, 56, 117, 125, 136, 128)
LR_right_oblique_edges = (46, 59, 63, 50, 118, 131, 135, 122)
LR_outer_x_centers = (44, 47, 62, 65, 116, 119, 134, 137)
LR_inner_x_centers = (51, 52, 57, 58, 123, 124, 129, 130)


outer_x_centers_666 = set((
    8, 11, 26, 29,
    44, 47, 62, 65,
    80, 83, 98, 101,
    116, 119, 134, 137,
    152, 155, 170, 173,
    188, 191, 206, 209
))

oblique_edges_666 = (
    9, 10, 14, 17, 20, 23, 27, 28,
    45, 46, 50, 53, 56, 59, 63, 64,
    81, 82, 86, 89, 92, 95, 99, 100,
    117, 118, 122, 125, 128, 131, 135, 136,
    153, 154, 158, 161, 164, 167, 171, 172,
    189, 190, 194, 197, 200, 203, 207, 208
)

outer_x_center_inner_x_centers_666 = (
    # outer x-centers
    8, 11, 26, 29,
    44, 47, 62, 65,
    80, 83, 98, 101,
    116, 119, 134, 137,
    152, 155, 170, 173,
    188, 191, 206, 209,

    # inner x-centers
    15, 16, 21, 22,
    51, 52, 57, 58,
    87, 88, 93, 94,
    123, 124, 129, 130,
    159, 160, 165, 166,
    195, 196, 201, 202
)

UFBD_inner_x_centers_left_oblique_edges_666 = (
    # inner x-centers
    15, 16, 21, 22,
    87, 88, 93, 94,
    159, 160, 165, 166,
    195, 196, 201, 202,

    # left oblique edges
    9, 17, 20, 28,
    81, 89, 92, 100,
    153, 161, 164, 172,
    189, 197, 200, 208
)

UFBD_inner_x_centers_right_oblique_edges_666 = (
    # inner x-centers
    15, 16, 21, 22,
    87, 88, 93, 94,
    159, 160, 165, 166,
    195, 196, 201, 202,

    # right oblique edges
    10, 14, 23, 27,
    82, 86, 95, 99,
    154, 158, 167, 171,
    190, 194, 203, 207
)

UFBD_oblique_edges_666 = (
    9, 10, 14, 17, 20, 23, 27, 28,
    81, 82, 86, 89, 92, 95, 99, 100,
    153, 154, 158, 161, 164, 167, 171, 172,
    189, 190, 194, 197, 200, 203, 207, 208
)

left_oblique_edges_666 = (
    9, 17, 20, 28,
    45, 53, 56, 64,
    81, 89, 92, 100,
    117, 125, 128, 136,
    153, 161, 164, 172,
    189, 197, 200, 208
)

right_oblique_edges_666 = (
    10, 14, 23, 27,
    46, 50, 59, 63,
    82, 86, 95, 99,
    118, 122, 131, 135,
    154, 158, 167, 171,
    190, 194, 203, 207
)

LFRB_left_oblique_edges_666 = (
    45, 53, 56, 64,
    81, 89, 92, 100,
    117, 125, 128, 136,
    153, 161, 164, 172
)

LFRB_right_oblique_edges_666 = (
    46, 50, 59, 63,
    82, 86, 95, 99,
    118, 122, 131, 135,
    154, 158, 167, 171
)

LFRB_oblique_edges_666 = (
    45, 46, 50, 53, 56, 59, 63, 64,
    81, 82, 86, 89, 92, 95, 99, 100,
    117, 118, 122, 125, 128, 131, 135, 136,
    153, 154, 158, 161, 164, 167, 171, 172
)


LFRB_inner_x_centers_oblique_edges_666 = (
        45, 46,
    50, 51, 52, 53,
    56, 57, 58, 59,
        63, 64,

        81, 82,
    86, 87, 88, 89,
    92, 93, 94, 95,
        99, 100,

         117, 118,
    122, 123, 124, 125,
    128, 129, 130, 131,
         135, 136,

         153, 154,
    158, 159, 160, 161,
    164, 165, 166, 167,
         171, 172,
)

oblique_edge_pairs_666 = (
    (9, 10), (14, 20), (17, 23), (27, 28),
    (45, 46), (50, 56), (53, 59), (63, 64),
    (81, 82), (86, 92), (89, 95), (99, 100),
    (117, 118), (122, 128), (125, 131), (135, 136),
    (153, 154), (158, 164), (161, 167), (171, 172),
    (189, 190), (194, 200), (197, 203), (207, 208)
)

class LookupTable666UDInnerXCentersStage(LookupTable):
    """
    starting-states-6x6x6-step10-UD-inner-x-centers-stage.txt
    =========================================================
    1 steps has 9 entries (0 percent, 0.00x previous step)
    2 steps has 108 entries (0 percent, 12.00x previous step)
    3 steps has 1,434 entries (0 percent, 13.28x previous step)
    4 steps has 15,210 entries (2 percent, 10.61x previous step)
    5 steps has 126,306 entries (17 percent, 8.30x previous step)
    6 steps has 420,312 entries (57 percent, 3.33x previous step)
    7 steps has 171,204 entries (23 percent, 0.41x previous step)
    8 steps has 888 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    Average: 6.02 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step10-UD-inner-x-centers-stage.txt',
            ('f0000f', '0f0f00', '00f0f0'),
            linecount=735471,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in inner_x_centers_666])
        return self.hex_format % int(result, 2)


class LookupTable666UDObliquEdgeStage(LookupTableIDA):
    """
    All we care about is getting the UD oblique edges paired, we do
    not need them to be placed on sides UD at this point.

    lookup-table-6x6x6-step20-UD-oblique-edges-stage.txt
    ====================================================
    1 steps has 4,171,103 entries (7 percent, 0.00x previous step)
    2 steps has 55,048,136 entries (92 percent, 13.20x previous step)

    Total: 59,219,239 entries
    """
    UD_unpaired_obliques_heuristic_666 = {
        (1, 0, 0): 1,
        (1, 1, 0): 1,
        (1, 2, 0): 1,
        (2, 0, 0): 1,
        (2, 1, 0): 1,
        (2, 2, 0): 1,
        (2, 3, 0): 1,
        (2, 3, 1): 2,
        (2, 4, 0): 1,
        (2, 5, 0): 2,
        (2, 5, 1): 1,
        (3, 0, 0): 3,
        (3, 1, 0): 2,
        (3, 2, 0): 2,
        (3, 2, 1): 1,
        (3, 3, 0): 2,
        (3, 3, 1): 2,
        (3, 4, 0): 1,
        (3, 5, 0): 3,
        (4, 0, 0): 3,
        (4, 1, 0): 3,
        (4, 2, 0): 3,
        (4, 2, 1): 1,
        (4, 3, 0): 2,
        (4, 3, 1): 2,
        (4, 4, 0): 1,
        (4, 5, 0): 3,
        (4, 6, 0): 2,
        (5, 0, 0): 5,
        (5, 1, 0): 5,
        (5, 2, 0): 5,
        (5, 2, 1): 2,
        (5, 3, 0): 5,
        (5, 4, 0): 4,
        (5, 5, 0): 4,
        (6, 0, 0): 6,
        (6, 1, 0): 5,
        (6, 2, 0): 5,
        (6, 2, 1): 4,
        (6, 3, 0): 5,
        (6, 4, 0): 4,
        (7, 0, 0): 6,
        (7, 1, 0): 6,
        (7, 2, 0): 6,
        (7, 2, 1): 2,
        (7, 3, 0): 5,
        (7, 4, 0): 4,
        (7, 6, 0): 4,
        (8, 0, 0): 6,
        (8, 1, 0): 6,
        (8, 2, 0): 5,
        (8, 3, 0): 6,
        (8, 4, 0): 4,
        (8, 5, 0): 4
    }

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step20-UD-oblique-edges-stage.txt',
            'TBD',
            moves_666,

            # illegal_moves
            ("3Fw", "3Fw'",
             "3Bw", "3Bw'",
             "3Lw", "3Lw'",
             "3Rw", "3Rw'"),

            # prune tables
            (),
            linecount=4171103,
            max_depth=1)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in oblique_edges_666])

        # Convert to hex
        return self.hex_format % int(result, 2)

    def get_UD_unpaired_obliques_count(self):
        parent_state = self.parent.state
        UD_paired_obliques = 0
        UD = ('U', 'D')

        for (x, y) in oblique_edge_pairs_666:
            if parent_state[x] in UD and parent_state[y] in UD:
                UD_paired_obliques += 1

        UD_unpaired_obliques = 8 - UD_paired_obliques
        return UD_unpaired_obliques

    def get_UD_obliques_four_pair_setup_count(self):
        parent_state = self.parent.state
        result = 0
        UD = ('U', 'D')

        for xy in (
            # Upper
            (9, 27, 189, 207,  82, 100, 153, 171),
            (10, 28, 190, 208,  81, 99, 154, 172),
            (14, 17, 200, 203,  46, 64, 117, 135),
            (20, 23, 194, 197,  45, 63, 118, 136),

            # Left
            (50, 53, 122, 125,  92, 95, 164, 167),
            (56, 59, 128, 131,  86, 89, 158, 161)):

            for index in xy:
                if parent_state[index] not in UD:
                    break
            else:
                #log.info("four count at %s" % pformat(xy))
                result += 1
        return result

    def get_UD_obliques_two_pair_setup_count(self):
        parent_state = self.parent.state
        result = 0
        UD = ('U', 'D')

        for xy in (
            # Upper
            (9, 27,  82, 100), (9, 27, 190, 208), (9, 27, 153, 171),
            (10, 28, 81, 99), (10, 28, 189, 207), (10, 28, 154, 172),
            (14, 17, 46, 64), (14, 17, 117, 135), (14, 17, 194, 197),
            (20, 23, 45, 63), (20, 23, 118, 136), (20, 23, 200, 203),

            # Left
            (45, 63, 194, 197), (45, 63, 117, 135),
            (46, 64, 200, 203), (46, 64, 118, 136),
            (50, 53, 92, 95), (50, 53, 128, 131), (50, 53, 164, 167),
            (56, 59, 86, 89), (56, 59, 122, 125), (56, 59, 158, 161),

            # Front
            (81, 99, 190, 208), (81, 99, 153, 171),
            (82, 100, 189, 207), (82, 100, 154, 172),
            (86, 89, 128, 131), (86, 89, 164, 167),
            (92, 95, 122, 125), (92, 95, 158, 161),

            # Right
            (117, 135, 200, 203),
            (118, 136, 194, 197),
            (122, 125, 164, 167),
            (128, 131, 158, 161),

            # Back
            (153, 171, 189, 207),
            (154, 172, 190, 208),
            ):
            for index in xy:
                if parent_state[index] not in UD:
                    break
            else:
                result += 1
                #log.info("two count at %s" % pformat(xy))

        return result

    def ida_heuristic(self):
        # Used to build UD_unpaired_obliques_heuristic_666
        # return math.ceil(UD_unpaired_obliques/4)

        UD_unpaired_obliques = self.get_UD_unpaired_obliques_count()
        two_count = self.get_UD_obliques_two_pair_setup_count()
        four_count = self.get_UD_obliques_four_pair_setup_count()
        state_tuple = (UD_unpaired_obliques, two_count, four_count)
        result = self.UD_unpaired_obliques_heuristic_666.get(state_tuple)

        if result is not None:
            return result
        else:
            log.warning("UD_unpaired_obliques_heuristic_666 needs entry for %s" % pformat(state_tuple))
            return math.ceil(UD_unpaired_obliques/4)

    def search_complete(self, state, steps_to_here):
        steps = self.steps(state)

        if self.ida_heuristic() == 0 or steps:

            # rotate_xxx() is very fast but it does not append the
            # steps to the solution so put the cube back in original state
            # and execute the steps via a normal rotate() call
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]
            steps_to_go = len(steps_to_here) + len(steps)

            if steps is None:
                steps = []

            for step in steps_to_here + steps:

                # Used to build UD_unpaired_obliques_heuristic_666
                '''
                UD_unpaired_obliques = self.get_UD_unpaired_obliques_count()
                four_count = self.get_UD_obliques_four_pair_setup_count()
                two_count = self.get_UD_obliques_two_pair_setup_count()
                two_count -= four_count * 2 # so as to not double count these
                state_tuple = (UD_unpaired_obliques, two_count, four_count)

                if state_tuple not in self.parent.heuristic_stats:
                    self.parent.heuristic_stats[state_tuple] = []
                self.parent.heuristic_stats[state_tuple].append(steps_to_go)
                '''

                self.parent.rotate(step)
                steps_to_go -= 1

            return True

        return False


#class LookupTable666LRObliqueEdgesStage(LookupTable):
class LookupTable666LRObliqueEdgesStage(LookupTableHashCostOnly):
    """
    lookup-table-6x6x6-step31-LR-oblique-edges-stage.txt
    ====================================================
    1 steps has 70,110 entries (0 percent, 0.00x previous step)
    2 steps has 612,996 entries (0 percent, 8.74x previous step)
    3 steps has 5,513,448 entries (3 percent, 8.99x previous step)
    4 steps has 35,146,680 entries (21 percent, 6.37x previous step)
    5 steps has 93,485,152 entries (56 percent, 2.66x previous step)
    6 steps has 30,737,090 entries (18 percent, 0.33x previous step)
    7 steps has 71,424 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 4.89 moves
    """

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step31-LR-oblique-edges-stage.hash-cost-only.txt',
            state_targets_step31,
            linecount=165636900,
            max_depth=7,
            bucketcount=331273823)

        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step31-LR-oblique-edges-stage.txt',
            state_targets_step31,
            linecount=165636900,
            max_depth=7)
        '''

    def state(self):
        parent_state = self.parent.state
        LR = ('L', 'R')
        result = ''.join(['1' if parent_state[x] in LR else '0' for x in LFRB_oblique_edges_666])
        return self.hex_format % int(result, 2)


class LookupTable666LRInnerXCentersStage(LookupTableCostOnly):
    """
    lookup-table-6x6x6-step32-LR-inner-x-center-stage.txt
    =====================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
    3 steps has 234 entries (1 percent, 8.07x previous step)
    4 steps has 1,246 entries (9 percent, 5.32x previous step)
    5 steps has 4,466 entries (34 percent, 3.58x previous step)
    6 steps has 6,236 entries (48 percent, 1.40x previous step)
    7 steps has 656 entries (5 percent, 0.11x previous step)

    Total: 12,870 entries
    Average: 5.45 moves
    """
    def __init__(self, parent):
        LookupTableCostOnly.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step32-LR-inner-x-center-stage.cost-only.txt',
            'f0f0',
            linecount=12870,
            max_depth=7)

    def state(self):
        parent_state = self.parent.state
        LR = ('L', 'R')
        result = ''.join(['1' if parent_state[x] in LR else '0' for x in LFRB_inner_x_centers_666])
        #return self.hex_format % int(result, 2)
        return int(result, 2)


class LookupTableIDA666LRInnerXCenterAndObliqueEdgesStage(LookupTableIDA):
    """
    lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt
    ====================================================================
    1 steps has 95,346 entries (7 percent, 0.00x previous step)
    2 steps has 1,257,166 entries (92 percent, 13.19x previous step)

    Total: 1,352,512 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt',
            state_targets_step30,
            moves_666,

            # illegal moves
            ("3Fw", "3Fw'",
             "3Bw", "3Bw'",
             "3Lw", "3Lw'",
             "3Rw", "3Rw'",
             "Fw", "Fw'",
             "Bw", "Bw'",
             "Lw", "Lw'",
             "Rw", "Rw'"),

            # prune tables
            (parent.lt_LR_oblique_edges_stage,
             parent.lt_LR_inner_x_centers_stage),

            linecount=1352512,
            max_depth=2),

    def state(self):
        parent_state = self.parent.state
        LR = ('L', 'R')
        result = ''.join(['1' if parent_state[x] in LR else '0' for x in LFRB_inner_x_centers_oblique_edges_666])
        return self.hex_format % int(result, 2)


class LookupTable666UDInnerXCenterAndObliqueEdges(LookupTable):
    """
    This will solve the UD inner x-centers and pair the UD oblique edges.

    lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
    1 steps has 350 entries (0 percent, 0.00x previous step)
    2 steps has 1,358 entries (0 percent, 3.88x previous step)
    3 steps has 5,148 entries (1 percent, 3.79x previous step)
    4 steps has 21,684 entries (6 percent, 4.21x previous step)
    5 steps has 75,104 entries (21 percent, 3.46x previous step)
    6 steps has 134,420 entries (39 percent, 1.79x previous step)
    7 steps has 91,784 entries (26 percent, 0.68x previous step)
    8 steps has 13,152 entries (3 percent, 0.14x previous step)

    Total: 343,000 entries
    Average: 5.93 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt',
            ('xDDxDUUDDUUDxDDxxUUxUDDUUDDUxUUx',
             'xDDxDUUDDUUDxUUxxDDxUDDUUDDUxUUx',
             'xDDxDUUDDUUDxUUxxUUxDDDUDDDUxUUx',
             'xDDxDUUDDUUDxUUxxUUxUDDDUDDDxUUx',
             'xDDxDUUDDUUDxUUxxUUxUDDUUDDUxDDx',
             'xDDxDUUUDUUUxDDxxDDxUDDUUDDUxUUx',
             'xDDxDUUUDUUUxDDxxUUxDDDUDDDUxUUx',
             'xDDxDUUUDUUUxDDxxUUxUDDDUDDDxUUx',
             'xDDxDUUUDUUUxDDxxUUxUDDUUDDUxDDx',
             'xDDxDUUUDUUUxUUxxDDxDDDUDDDUxUUx',
             'xDDxDUUUDUUUxUUxxDDxUDDDUDDDxUUx',
             'xDDxDUUUDUUUxUUxxDDxUDDUUDDUxDDx',
             'xDDxDUUUDUUUxUUxxUUxDDDDDDDDxUUx',
             'xDDxDUUUDUUUxUUxxUUxDDDUDDDUxDDx',
             'xDDxDUUUDUUUxUUxxUUxUDDDUDDDxDDx',
             'xDDxUUUDUUUDxDDxxDDxUDDUUDDUxUUx',
             'xDDxUUUDUUUDxDDxxUUxDDDUDDDUxUUx',
             'xDDxUUUDUUUDxDDxxUUxUDDDUDDDxUUx',
             'xDDxUUUDUUUDxDDxxUUxUDDUUDDUxDDx',
             'xDDxUUUDUUUDxUUxxDDxDDDUDDDUxUUx',
             'xDDxUUUDUUUDxUUxxDDxUDDDUDDDxUUx',
             'xDDxUUUDUUUDxUUxxDDxUDDUUDDUxDDx',
             'xDDxUUUDUUUDxUUxxUUxDDDDDDDDxUUx',
             'xDDxUUUDUUUDxUUxxUUxDDDUDDDUxDDx',
             'xDDxUUUDUUUDxUUxxUUxUDDDUDDDxDDx',
             'xDDxUUUUUUUUxDDxxDDxDDDUDDDUxUUx',
             'xDDxUUUUUUUUxDDxxDDxUDDDUDDDxUUx',
             'xDDxUUUUUUUUxDDxxDDxUDDUUDDUxDDx',
             'xDDxUUUUUUUUxDDxxUUxDDDDDDDDxUUx',
             'xDDxUUUUUUUUxDDxxUUxDDDUDDDUxDDx',
             'xDDxUUUUUUUUxDDxxUUxUDDDUDDDxDDx',
             'xDDxUUUUUUUUxUUxxDDxDDDDDDDDxUUx',
             'xDDxUUUUUUUUxUUxxDDxDDDUDDDUxDDx',
             'xDDxUUUUUUUUxUUxxDDxUDDDUDDDxDDx',
             'xDDxUUUUUUUUxUUxxUUxDDDDDDDDxDDx',
             'xUUxDUUDDUUDxDDxxDDxUDDUUDDUxUUx',
             'xUUxDUUDDUUDxDDxxUUxDDDUDDDUxUUx',
             'xUUxDUUDDUUDxDDxxUUxUDDDUDDDxUUx',
             'xUUxDUUDDUUDxDDxxUUxUDDUUDDUxDDx',
             'xUUxDUUDDUUDxUUxxDDxDDDUDDDUxUUx',
             'xUUxDUUDDUUDxUUxxDDxUDDDUDDDxUUx',
             'xUUxDUUDDUUDxUUxxDDxUDDUUDDUxDDx',
             'xUUxDUUDDUUDxUUxxUUxDDDDDDDDxUUx',
             'xUUxDUUDDUUDxUUxxUUxDDDUDDDUxDDx',
             'xUUxDUUDDUUDxUUxxUUxUDDDUDDDxDDx',
             'xUUxDUUUDUUUxDDxxDDxDDDUDDDUxUUx',
             'xUUxDUUUDUUUxDDxxDDxUDDDUDDDxUUx',
             'xUUxDUUUDUUUxDDxxDDxUDDUUDDUxDDx',
             'xUUxDUUUDUUUxDDxxUUxDDDDDDDDxUUx',
             'xUUxDUUUDUUUxDDxxUUxDDDUDDDUxDDx',
             'xUUxDUUUDUUUxDDxxUUxUDDDUDDDxDDx',
             'xUUxDUUUDUUUxUUxxDDxDDDDDDDDxUUx',
             'xUUxDUUUDUUUxUUxxDDxDDDUDDDUxDDx',
             'xUUxDUUUDUUUxUUxxDDxUDDDUDDDxDDx',
             'xUUxDUUUDUUUxUUxxUUxDDDDDDDDxDDx',
             'xUUxUUUDUUUDxDDxxDDxDDDUDDDUxUUx',
             'xUUxUUUDUUUDxDDxxDDxUDDDUDDDxUUx',
             'xUUxUUUDUUUDxDDxxDDxUDDUUDDUxDDx',
             'xUUxUUUDUUUDxDDxxUUxDDDDDDDDxUUx',
             'xUUxUUUDUUUDxDDxxUUxDDDUDDDUxDDx',
             'xUUxUUUDUUUDxDDxxUUxUDDDUDDDxDDx',
             'xUUxUUUDUUUDxUUxxDDxDDDDDDDDxUUx',
             'xUUxUUUDUUUDxUUxxDDxDDDUDDDUxDDx',
             'xUUxUUUDUUUDxUUxxDDxUDDDUDDDxDDx',
             'xUUxUUUDUUUDxUUxxUUxDDDDDDDDxDDx',
             'xUUxUUUUUUUUxDDxxDDxDDDDDDDDxUUx',
             'xUUxUUUUUUUUxDDxxDDxDDDUDDDUxDDx',
             'xUUxUUUUUUUUxDDxxDDxUDDDUDDDxDDx',
             'xUUxUUUUUUUUxDDxxUUxDDDDDDDDxDDx',
             'xUUxUUUUUUUUxUUxxDDxDDDDDDDDxDDx'),
            linecount=343000,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            'x', parent_state[9], parent_state[10], 'x',
            parent_state[14], parent_state[15], parent_state[16], parent_state[17],
            parent_state[20], parent_state[21], parent_state[22], parent_state[23],
            'x', parent_state[27], parent_state[28], 'x',

            # Down
            'x', parent_state[189], parent_state[190], 'x',
            parent_state[194], parent_state[195], parent_state[196], parent_state[197],
            parent_state[200], parent_state[201], parent_state[202], parent_state[203],
            'x', parent_state[207], parent_state[208], 'x'
        ]

        result = ''.join(result)
        return result


class LookupTable666LRInnerXCenterAndObliqueEdges(LookupTable):
    """
    lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt
    ========================================================================
    1 steps has 140 entries (0 percent, 0.00x previous step)
    2 steps has 476 entries (0 percent, 3.40x previous step)
    3 steps has 2,166 entries (0 percent, 4.55x previous step)
    4 steps has 10,430 entries (3 percent, 4.82x previous step)
    5 steps has 37,224 entries (10 percent, 3.57x previous step)
    6 steps has 89,900 entries (26 percent, 2.42x previous step)
    7 steps has 124,884 entries (36 percent, 1.39x previous step)
    8 steps has 70,084 entries (20 percent, 0.56x previous step)
    9 steps has 7,688 entries (2 percent, 0.11x previous step)
    10 steps has 8 entries (0 percent, 0.00x previous step)

    Total: 343,000 entries
    Average: 6.64 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt',
            ('LLLLLLLLLLLLRRRRRRRRRRRR',
             'LLLLLLLLLLRRLLRRRRRRRRRR',
             'LLLLLLLLLLRRRRLRRRLRRRRR',
             'LLLLLLLLLLRRRRRRRLRRRLRR',
             'LLLLLLLLLLRRRRRRRRRRRRLL',
             'LLLLLRLLLRLLLLRRRRRRRRRR',
             'LLLLLRLLLRLLRRLRRRLRRRRR',
             'LLLLLRLLLRLLRRRRRLRRRLRR',
             'LLLLLRLLLRLLRRRRRRRRRRLL',
             'LLLLLRLLLRRRLLLRRRLRRRRR',
             'LLLLLRLLLRRRLLRRRLRRRLRR',
             'LLLLLRLLLRRRLLRRRRRRRRLL',
             'LLLLLRLLLRRRRRLRRLLRRLRR',
             'LLLLLRLLLRRRRRLRRRLRRRLL',
             'LLLLLRLLLRRRRRRRRLRRRLLL',
             'LLRLLLRLLLLLLLRRRRRRRRRR',
             'LLRLLLRLLLLLRRLRRRLRRRRR',
             'LLRLLLRLLLLLRRRRRLRRRLRR',
             'LLRLLLRLLLLLRRRRRRRRRRLL',
             'LLRLLLRLLLRRLLLRRRLRRRRR',
             'LLRLLLRLLLRRLLRRRLRRRLRR',
             'LLRLLLRLLLRRLLRRRRRRRRLL',
             'LLRLLLRLLLRRRRLRRLLRRLRR',
             'LLRLLLRLLLRRRRLRRRLRRRLL',
             'LLRLLLRLLLRRRRRRRLRRRLLL',
             'LLRLLRRLLRLLLLLRRRLRRRRR',
             'LLRLLRRLLRLLLLRRRLRRRLRR',
             'LLRLLRRLLRLLLLRRRRRRRRLL',
             'LLRLLRRLLRLLRRLRRLLRRLRR',
             'LLRLLRRLLRLLRRLRRRLRRRLL',
             'LLRLLRRLLRLLRRRRRLRRRLLL',
             'LLRLLRRLLRRRLLLRRLLRRLRR',
             'LLRLLRRLLRRRLLLRRRLRRRLL',
             'LLRLLRRLLRRRLLRRRLRRRLLL',
             'LLRLLRRLLRRRRRLRRLLRRLLL',
             'RRLLLLLLLLLLLLRRRRRRRRRR',
             'RRLLLLLLLLLLRRLRRRLRRRRR',
             'RRLLLLLLLLLLRRRRRLRRRLRR',
             'RRLLLLLLLLLLRRRRRRRRRRLL',
             'RRLLLLLLLLRRLLLRRRLRRRRR',
             'RRLLLLLLLLRRLLRRRLRRRLRR',
             'RRLLLLLLLLRRLLRRRRRRRRLL',
             'RRLLLLLLLLRRRRLRRLLRRLRR',
             'RRLLLLLLLLRRRRLRRRLRRRLL',
             'RRLLLLLLLLRRRRRRRLRRRLLL',
             'RRLLLRLLLRLLLLLRRRLRRRRR',
             'RRLLLRLLLRLLLLRRRLRRRLRR',
             'RRLLLRLLLRLLLLRRRRRRRRLL',
             'RRLLLRLLLRLLRRLRRLLRRLRR',
             'RRLLLRLLLRLLRRLRRRLRRRLL',
             'RRLLLRLLLRLLRRRRRLRRRLLL',
             'RRLLLRLLLRRRLLLRRLLRRLRR',
             'RRLLLRLLLRRRLLLRRRLRRRLL',
             'RRLLLRLLLRRRLLRRRLRRRLLL',
             'RRLLLRLLLRRRRRLRRLLRRLLL',
             'RRRLLLRLLLLLLLLRRRLRRRRR',
             'RRRLLLRLLLLLLLRRRLRRRLRR',
             'RRRLLLRLLLLLLLRRRRRRRRLL',
             'RRRLLLRLLLLLRRLRRLLRRLRR',
             'RRRLLLRLLLLLRRLRRRLRRRLL',
             'RRRLLLRLLLLLRRRRRLRRRLLL',
             'RRRLLLRLLLRRLLLRRLLRRLRR',
             'RRRLLLRLLLRRLLLRRRLRRRLL',
             'RRRLLLRLLLRRLLRRRLRRRLLL',
             'RRRLLLRLLLRRRRLRRLLRRLLL',
             'RRRLLRRLLRLLLLLRRLLRRLRR',
             'RRRLLRRLLRLLLLLRRRLRRRLL',
             'RRRLLRRLLRLLLLRRRLRRRLLL',
             'RRRLLRRLLRLLRRLRRLLRRLLL',
             'RRRLLRRLLRRRLLLRRLLRRLLL'),
            linecount=343000,
            max_depth=10,
            filesize=21609000)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in step61_centers_666])
        return result


class LookupTable666FBInnerXCenterAndObliqueEdges(LookupTable666LRInnerXCenterAndObliqueEdges):

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['L' if parent_state[x] == 'F' else 'R' for x in step62_centers_666])
        return result



class LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(LookupTableIDA):
    """
    lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt
    ==========================================================================
    1 steps has 9,800 entries (1 percent, 0.00x previous step)
    2 steps has 74,480 entries (10 percent, 7.60x previous step)
    3 steps has 645,960 entries (88 percent, 8.67x previous step)

    Total: 730,240 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt',
            lt_LFRB_solve_inner_x_centers_and_oblique_edges_state_targets,

            moves_666,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
             "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
             "3Rw2", "3Lw2", "3Fw2", "3Bw2",                                                           # do not mess up solved UD
             "3Lw", "3Lw'", "3Lw2",        # can skip these for 6x6x6 cubes
             "3Dw", "3Dw'", "3Dw2",
             "3Bw", "3Bw'", "3Bw2"),

            # prune tables
            (parent.lt_LR_solve_inner_x_centers_and_oblique_edges,
             parent.lt_FB_solve_inner_x_centers_and_oblique_edges,),

            linecount=730240,
            max_depth=3,
            filesize=46005120)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in step60_centers_666])
        return result


class RubiksCube666(RubiksCubeNNNEvenEdges):
    """
    6x6x6 strategy
    - stage UD centers to sides U or D (use IDA)
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3

    Inheritance model
    -----------------
            RubiksCube
                |
        RubiksCubeNNNEvenEdges
           /            \
    RubiksCubeNNNEven RubiksCube666
    """
    instantiated = False

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCubeNNNEvenEdges.__init__(self, state, order, colormap, debug)

        if RubiksCube666.instantiated:
            #raise Exception("Another 6x6x6 instance is being created")
            log.warning("Another 6x6x6 instance is being created")
        else:
            RubiksCube666.instantiated = True

    def get_fake_444(self):
        if self.fake_444 is None:
            self.fake_444 = RubiksCube444(solved_444, 'URFDLB')
            self.fake_444.lt_init()
        else:
            self.fake_444.re_init()
        return self.fake_444

    def get_fake_555(self):
        if self.fake_555 is None:
            self.fake_555 = RubiksCube555(solved_555, 'URFDLB')
            self.fake_555.lt_init()
        else:
            self.fake_555.re_init()
        return self.fake_555

    def sanity_check(self):
        edge_orbit_0 = (2, 5, 12, 30, 35, 32, 25, 7,
                        38, 41, 48, 66, 71, 68, 61, 43,
                        74, 77, 84, 102, 107, 104, 97, 79,
                        110, 113, 120, 138, 143, 140, 133, 115,
                        146, 149, 156, 174, 179, 176, 169, 151,
                        182, 185, 192, 210, 215, 212, 205, 187)

        edge_orbit_1 = (3, 4, 18, 24, 34, 33, 19, 13,
                        39, 40, 54, 60, 70, 69, 55, 49,
                        75, 76, 90, 96, 106, 105, 91, 85,
                        111, 112, 126, 132, 142, 141, 127, 121,
                        147, 148, 162, 168, 178, 177, 163, 157,
                        183, 184, 198, 204, 214, 213, 199, 193)

        corners = (1, 6, 31, 36,
                   37, 42, 67, 72,
                   73, 78, 103, 108,
                   109, 114, 139, 144,
                   145, 150, 175, 180,
                   181, 186, 211, 216)

        left_oblique_edge = (9, 17, 28, 20,
                             45, 53, 64, 56,
                             81, 89, 100, 92,
                             117, 125, 136, 128,
                             153, 161, 172, 164,
                             189, 197, 208, 200)

        right_oblique_edge = (10, 23, 27, 14,
                              46, 59, 63, 50,
                              82, 95, 99, 86,
                              118, 131, 135, 122,
                              154, 167, 171, 158,
                              190, 203, 207, 194)

        outside_x_centers = (8, 11, 26, 29,
                             44, 47, 62, 65,
                             80, 83, 98, 101,
                             116, 119, 134, 137,
                             152, 155, 170, 173,
                             188, 191, 206, 209)

        inside_x_centers = (15, 16, 21, 22,
                            51, 52, 57, 58,
                            87, 88, 93, 94,
                            123, 124, 129, 130,
                            159, 160, 165, 166,
                            195, 196, 201, 202)

        self._sanity_check('edge-orbit-0', edge_orbit_0, 8)
        self._sanity_check('edge-orbit-1', edge_orbit_1, 8)
        self._sanity_check('corners', corners, 4)
        self._sanity_check('left-oblique', left_oblique_edge, 4)
        self._sanity_check('right-oblique', right_oblique_edge, 4)
        self._sanity_check('outside x-center', outside_x_centers, 4)
        self._sanity_check('inside x-center', inside_x_centers, 4)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_UD_inner_x_centers_stage = LookupTable666UDInnerXCentersStage(self)
        self.lt_UD_oblique_edge_stage = LookupTable666UDObliquEdgeStage(self)
        self.lt_UD_oblique_edge_stage.preload_cache()

        self.lt_LR_oblique_edges_stage = LookupTable666LRObliqueEdgesStage(self)
        self.lt_LR_inner_x_centers_stage = LookupTable666LRInnerXCentersStage(self)
        self.lt_LR_inner_x_centers_and_oblique_edges_stage = LookupTableIDA666LRInnerXCenterAndObliqueEdgesStage(self)
        self.lt_LR_inner_x_centers_and_oblique_edges_stage.preload_cache()
        #self.lt_LR_inner_x_centers_and_oblique_edges_stage.avoid_oll = True

        self.lt_UD_solve_inner_x_centers_and_oblique_edges = LookupTable666UDInnerXCenterAndObliqueEdges(self)

        self.lt_LR_solve_inner_x_centers_and_oblique_edges = LookupTable666LRInnerXCenterAndObliqueEdges(self)
        self.lt_FB_solve_inner_x_centers_and_oblique_edges = LookupTable666FBInnerXCenterAndObliqueEdges(self)
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges = LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(self)
        self.lt_LR_solve_inner_x_centers_and_oblique_edges.preload_cache()
        self.lt_FB_solve_inner_x_centers_and_oblique_edges.preload_cache()
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.preload_cache()
        #self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.avoid_oll = True

    def populate_fake_555_for_ULFRBD_solve(self):
        fake_555 = self.get_fake_555()
        fake_555.nuke_corners()
        fake_555.nuke_edges()
        fake_555.nuke_centers()
        side_names = ('U', 'L', 'F', 'R', 'B', 'D')

        for side_index in range(6):
            offset_555 = side_index * 25
            offset_666 = side_index * 36
            side_name = side_names[side_index]

            # Corners
            fake_555.state[1 + offset_555] = self.state[1 + offset_666]
            fake_555.state[5 + offset_555] = self.state[6 + offset_666]
            fake_555.state[21 + offset_555] = self.state[31 + offset_666]
            fake_555.state[25 + offset_555] = self.state[36 + offset_666]

            # Centers
            fake_555.state[7 + offset_555] = self.state[8 + offset_666]
            fake_555.state[8 + offset_555] = self.state[9 + offset_666]
            fake_555.state[9 + offset_555] = self.state[11 + offset_666]
            fake_555.state[12 + offset_555] = self.state[14 + offset_666]
            fake_555.state[13 + offset_555] = side_name
            fake_555.state[14 + offset_555] = self.state[17 + offset_666]
            fake_555.state[17 + offset_555] = self.state[26 + offset_666]
            fake_555.state[18 + offset_555] = self.state[27 + offset_666]
            fake_555.state[19 + offset_555] = self.state[29 + offset_666]

            # Edges
            fake_555.state[2 + offset_555] = self.state[2 + offset_666]
            fake_555.state[3 + offset_555] = self.state[3 + offset_666]
            fake_555.state[4 + offset_555] = self.state[5 + offset_666]
            fake_555.state[6 + offset_555] = self.state[7 + offset_666]
            fake_555.state[10 + offset_555] = self.state[12 + offset_666]
            fake_555.state[11 + offset_555] = self.state[13 + offset_666]
            fake_555.state[15 + offset_555] = self.state[18 + offset_666]
            fake_555.state[16 + offset_555] = self.state[25 + offset_666]
            fake_555.state[20 + offset_555] = self.state[30 + offset_666]
            fake_555.state[22 + offset_555] = self.state[32 + offset_666]
            fake_555.state[23 + offset_555] = self.state[33 + offset_666]
            fake_555.state[24 + offset_555] = self.state[35 + offset_666]

    def solve_reduced_555_centers_and_edges(self):
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        fake_555.group_centers_guts()
        fake_555.group_edges()

        for step in fake_555.solution:
            self.rotate(step)

    def solve_reduced_555_centers(self):
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        fake_555.group_centers_guts()

        for step in fake_555.solution:
            self.rotate(step)

    def solve_reduced_555_t_centers(self):
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        fake_555.lt_ULFRBD_t_centers_solve.solve()

        for step in fake_555.solution:
            self.rotate(step)

    def stage_UD_oblique_edges(self):
        """
        Used by the 7x7x7 solver...this stages the UD oblique edges to sides U or D
        """
        self.lt_UD_oblique_edge_stage.solve()
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        fake_555.lt_UD_T_centers_stage.solve()

        for step in fake_555.solution:
            self.rotate(step)

    def stage_LR_oblique_edges(self):
        """
        Used by the 7x7x7 solver...this stages the LR oblique edges to sides L or R
        """
        self.lt_LR_inner_x_centers_and_oblique_edges_stage.solve()
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        fake_555.lt_LR_T_centers_stage.solve()

        for step in fake_555.solution:
            self.rotate(step)

    def group_centers_guts(self, oblique_edges_only=False):
        self.lt_init()

        self.lt_UD_inner_x_centers_stage.solve()
        self.rotate_for_best_centers_solving(inner_x_centers_666)
        self.print_cube()
        log.info("%s: UD inner-x-centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.lt_UD_oblique_edge_stage.solve()
        self.print_cube()
        log.info("%s: UD oblique edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Stage UD centers via 555
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()

        if oblique_edges_only:
            fake_555.lt_UD_T_centers_stage.solve()
        else:
            fake_555.group_centers_stage_UD()

        for step in fake_555.solution:
            self.rotate(step)

        self.rotate_for_best_centers_solving(inner_x_centers_666)
        self.print_cube()
        log.info("%s: UD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Test the prune tables
        #self.lt_LR_oblique_edges_stage.solve()
        #self.lt_LR_inner_x_centers_stage.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        # Stage the LR inner x-centers and oblique edges
        self.lt_LR_inner_x_centers_and_oblique_edges_stage.solve()
        self.print_cube()
        log.info("%s: LR oblique edges and inner x-centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Stage LR centers via 555
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()

        if oblique_edges_only:
            fake_555.lt_LR_T_centers_stage.solve()
        else:
            fake_555.group_centers_stage_LR()

        for step in fake_555.solution:
            self.rotate(step)

        self.print_cube()
        log.info("%s: centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Reduce the centers to 5x5x5 centers
        # - solve the UD inner x-centers and pair the UD oblique edges
        # - solve the LR inner x-centers and pair the LR oblique edges
        # - solve the FB inner x-centers and pair the FB oblique edges
        self.lt_UD_solve_inner_x_centers_and_oblique_edges.solve()
        self.print_cube()
        log.info("%s: UD inner x-center solved and oblique edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Test the prune tables
        #self.lt_LR_solve_inner_x_centers_and_oblique_edges.solve()
        #self.lt_FB_solve_inner_x_centers_and_oblique_edges.solve()
        #self.print_cube()
        #sys.exit(0)

        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.solve()
        self.print_cube()
        log.info("%s: LFRB inner x-center and oblique edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("\n\n\n\n\n")

        # We must "solve" the t-centers so that we can use the 4x4x4 solver to pair the inside edges.
        # That solver needs the centers to be solved.
        self.solve_reduced_555_t_centers()
        self.print_cube()
        log.info("%s: Took %d steps to solve oblique edges" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("\n\n\n\n\n")

        if not oblique_edges_only:
            self.prevent_OLL()
            self.pair_inside_edges_via_444()
            log.info("%s: Took %d steps to reduce 5x5x5" % (self, self.get_solution_len_minus_rotates(self.solution)))

            self.solve_reduced_555_centers_and_edges()
            self.print_cube()
            log.info("%s: Took %d steps to reduce to 3x3x3" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def phase(self):
        if self._phase is None:
            self._phase = 'Stage UD centers'
            return self._phase

        if self._phase == 'Stage UD centers':
            if self.UD_centers_staged():
                self._phase = 'Stage LR centers'
            return self._phase

        if self._phase == 'Stage LR centers':
            if self.LR_centers_staged():
                self._phase = 'Solve Centers'

        if self._phase == 'Solve Centers':
            if self.centers_solved():
                self._phase = 'Pair Edges'

        if self._phase == 'Pair Edges':
            if not self.get_non_paired_edges():
                self._phase = 'Solve 3x3x3'

        return self._phase


def rotate_666_U(cube):
    return [cube[0],cube[31],cube[25],cube[19],cube[13],cube[7],cube[1],cube[32],cube[26],cube[20],cube[14],cube[8],cube[2],cube[33],cube[27],cube[21],cube[15],cube[9],cube[3],cube[34],cube[28],cube[22],cube[16],cube[10],cube[4],cube[35],cube[29],cube[23],cube[17],cube[11],cube[5],cube[36],cube[30],cube[24],cube[18],cube[12],cube[6]] + cube[73:79] + cube[43:73] + cube[109:115] + cube[79:109] + cube[145:151] + cube[115:145] + cube[37:43] + cube[151:217]

def rotate_666_U_prime(cube):
    return [cube[0],cube[6],cube[12],cube[18],cube[24],cube[30],cube[36],cube[5],cube[11],cube[17],cube[23],cube[29],cube[35],cube[4],cube[10],cube[16],cube[22],cube[28],cube[34],cube[3],cube[9],cube[15],cube[21],cube[27],cube[33],cube[2],cube[8],cube[14],cube[20],cube[26],cube[32],cube[1],cube[7],cube[13],cube[19],cube[25],cube[31]] + cube[145:151] + cube[43:73] + cube[37:43] + cube[79:109] + cube[73:79] + cube[115:145] + cube[109:115] + cube[151:217]

def rotate_666_U2(cube):
    return [cube[0],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]] + cube[109:115] + cube[43:73] + cube[145:151] + cube[79:109] + cube[37:43] + cube[115:145] + cube[73:79] + cube[151:217]

def rotate_666_Uw(cube):
    return [cube[0],cube[31],cube[25],cube[19],cube[13],cube[7],cube[1],cube[32],cube[26],cube[20],cube[14],cube[8],cube[2],cube[33],cube[27],cube[21],cube[15],cube[9],cube[3],cube[34],cube[28],cube[22],cube[16],cube[10],cube[4],cube[35],cube[29],cube[23],cube[17],cube[11],cube[5],cube[36],cube[30],cube[24],cube[18],cube[12],cube[6]] + cube[73:85] + cube[49:73] + cube[109:121] + cube[85:109] + cube[145:157] + cube[121:145] + cube[37:49] + cube[157:217]

def rotate_666_Uw_prime(cube):
    return [cube[0],cube[6],cube[12],cube[18],cube[24],cube[30],cube[36],cube[5],cube[11],cube[17],cube[23],cube[29],cube[35],cube[4],cube[10],cube[16],cube[22],cube[28],cube[34],cube[3],cube[9],cube[15],cube[21],cube[27],cube[33],cube[2],cube[8],cube[14],cube[20],cube[26],cube[32],cube[1],cube[7],cube[13],cube[19],cube[25],cube[31]] + cube[145:157] + cube[49:73] + cube[37:49] + cube[85:109] + cube[73:85] + cube[121:145] + cube[109:121] + cube[157:217]

def rotate_666_Uw2(cube):
    return [cube[0],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]] + cube[109:121] + cube[49:73] + cube[145:157] + cube[85:109] + cube[37:49] + cube[121:145] + cube[73:85] + cube[157:217]

def rotate_666_3Uw(cube):
    return [cube[0],cube[31],cube[25],cube[19],cube[13],cube[7],cube[1],cube[32],cube[26],cube[20],cube[14],cube[8],cube[2],cube[33],cube[27],cube[21],cube[15],cube[9],cube[3],cube[34],cube[28],cube[22],cube[16],cube[10],cube[4],cube[35],cube[29],cube[23],cube[17],cube[11],cube[5],cube[36],cube[30],cube[24],cube[18],cube[12],cube[6]] + cube[73:91] + cube[55:73] + cube[109:127] + cube[91:109] + cube[145:163] + cube[127:145] + cube[37:55] + cube[163:217]

def rotate_666_3Uw_prime(cube):
    return [cube[0],cube[6],cube[12],cube[18],cube[24],cube[30],cube[36],cube[5],cube[11],cube[17],cube[23],cube[29],cube[35],cube[4],cube[10],cube[16],cube[22],cube[28],cube[34],cube[3],cube[9],cube[15],cube[21],cube[27],cube[33],cube[2],cube[8],cube[14],cube[20],cube[26],cube[32],cube[1],cube[7],cube[13],cube[19],cube[25],cube[31]] + cube[145:163] + cube[55:73] + cube[37:55] + cube[91:109] + cube[73:91] + cube[127:145] + cube[109:127] + cube[163:217]

def rotate_666_3Uw2(cube):
    return [cube[0],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]] + cube[109:127] + cube[55:73] + cube[145:163] + cube[91:109] + cube[37:55] + cube[127:145] + cube[73:91] + cube[163:217]

def rotate_666_L(cube):
    return [cube[0],cube[180]] + cube[2:7] + [cube[174]] + cube[8:13] + [cube[168]] + cube[14:19] + [cube[162]] + cube[20:25] + [cube[156]] + cube[26:31] + [cube[150]] + cube[32:37] + [cube[67],cube[61],cube[55],cube[49],cube[43],cube[37],cube[68],cube[62],cube[56],cube[50],cube[44],cube[38],cube[69],cube[63],cube[57],cube[51],cube[45],cube[39],cube[70],cube[64],cube[58],cube[52],cube[46],cube[40],cube[71],cube[65],cube[59],cube[53],cube[47],cube[41],cube[72],cube[66],cube[60],cube[54],cube[48],cube[42],cube[1]] + cube[74:79] + [cube[7]] + cube[80:85] + [cube[13]] + cube[86:91] + [cube[19]] + cube[92:97] + [cube[25]] + cube[98:103] + [cube[31]] + cube[104:150] + [cube[211]] + cube[151:156] + [cube[205]] + cube[157:162] + [cube[199]] + cube[163:168] + [cube[193]] + cube[169:174] + [cube[187]] + cube[175:180] + [cube[181],cube[73]] + cube[182:187] + [cube[79]] + cube[188:193] + [cube[85]] + cube[194:199] + [cube[91]] + cube[200:205] + [cube[97]] + cube[206:211] + [cube[103]] + cube[212:217]

def rotate_666_L_prime(cube):
    return [cube[0],cube[73]] + cube[2:7] + [cube[79]] + cube[8:13] + [cube[85]] + cube[14:19] + [cube[91]] + cube[20:25] + [cube[97]] + cube[26:31] + [cube[103]] + cube[32:37] + [cube[42],cube[48],cube[54],cube[60],cube[66],cube[72],cube[41],cube[47],cube[53],cube[59],cube[65],cube[71],cube[40],cube[46],cube[52],cube[58],cube[64],cube[70],cube[39],cube[45],cube[51],cube[57],cube[63],cube[69],cube[38],cube[44],cube[50],cube[56],cube[62],cube[68],cube[37],cube[43],cube[49],cube[55],cube[61],cube[67],cube[181]] + cube[74:79] + [cube[187]] + cube[80:85] + [cube[193]] + cube[86:91] + [cube[199]] + cube[92:97] + [cube[205]] + cube[98:103] + [cube[211]] + cube[104:150] + [cube[31]] + cube[151:156] + [cube[25]] + cube[157:162] + [cube[19]] + cube[163:168] + [cube[13]] + cube[169:174] + [cube[7]] + cube[175:180] + [cube[1],cube[180]] + cube[182:187] + [cube[174]] + cube[188:193] + [cube[168]] + cube[194:199] + [cube[162]] + cube[200:205] + [cube[156]] + cube[206:211] + [cube[150]] + cube[212:217]

def rotate_666_L2(cube):
    return [cube[0],cube[181]] + cube[2:7] + [cube[187]] + cube[8:13] + [cube[193]] + cube[14:19] + [cube[199]] + cube[20:25] + [cube[205]] + cube[26:31] + [cube[211]] + cube[32:37] + [cube[72],cube[71],cube[70],cube[69],cube[68],cube[67],cube[66],cube[65],cube[64],cube[63],cube[62],cube[61],cube[60],cube[59],cube[58],cube[57],cube[56],cube[55],cube[54],cube[53],cube[52],cube[51],cube[50],cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[180]] + cube[74:79] + [cube[174]] + cube[80:85] + [cube[168]] + cube[86:91] + [cube[162]] + cube[92:97] + [cube[156]] + cube[98:103] + [cube[150]] + cube[104:150] + [cube[103]] + cube[151:156] + [cube[97]] + cube[157:162] + [cube[91]] + cube[163:168] + [cube[85]] + cube[169:174] + [cube[79]] + cube[175:180] + [cube[73],cube[1]] + cube[182:187] + [cube[7]] + cube[188:193] + [cube[13]] + cube[194:199] + [cube[19]] + cube[200:205] + [cube[25]] + cube[206:211] + [cube[31]] + cube[212:217]

def rotate_666_Lw(cube):
    return [cube[0],cube[180],cube[179]] + cube[3:7] + [cube[174],cube[173]] + cube[9:13] + [cube[168],cube[167]] + cube[15:19] + [cube[162],cube[161]] + cube[21:25] + [cube[156],cube[155]] + cube[27:31] + [cube[150],cube[149]] + cube[33:37] + [cube[67],cube[61],cube[55],cube[49],cube[43],cube[37],cube[68],cube[62],cube[56],cube[50],cube[44],cube[38],cube[69],cube[63],cube[57],cube[51],cube[45],cube[39],cube[70],cube[64],cube[58],cube[52],cube[46],cube[40],cube[71],cube[65],cube[59],cube[53],cube[47],cube[41],cube[72],cube[66],cube[60],cube[54],cube[48],cube[42]] + cube[1:3] + cube[75:79] + cube[7:9] + cube[81:85] + cube[13:15] + cube[87:91] + cube[19:21] + cube[93:97] + cube[25:27] + cube[99:103] + cube[31:33] + cube[105:149] + [cube[212],cube[211]] + cube[151:155] + [cube[206],cube[205]] + cube[157:161] + [cube[200],cube[199]] + cube[163:167] + [cube[194],cube[193]] + cube[169:173] + [cube[188],cube[187]] + cube[175:179] + [cube[182],cube[181]] + cube[73:75] + cube[183:187] + cube[79:81] + cube[189:193] + cube[85:87] + cube[195:199] + cube[91:93] + cube[201:205] + cube[97:99] + cube[207:211] + cube[103:105] + cube[213:217]

def rotate_666_Lw_prime(cube):
    return [cube[0]] + cube[73:75] + cube[3:7] + cube[79:81] + cube[9:13] + cube[85:87] + cube[15:19] + cube[91:93] + cube[21:25] + cube[97:99] + cube[27:31] + cube[103:105] + cube[33:37] + [cube[42],cube[48],cube[54],cube[60],cube[66],cube[72],cube[41],cube[47],cube[53],cube[59],cube[65],cube[71],cube[40],cube[46],cube[52],cube[58],cube[64],cube[70],cube[39],cube[45],cube[51],cube[57],cube[63],cube[69],cube[38],cube[44],cube[50],cube[56],cube[62],cube[68],cube[37],cube[43],cube[49],cube[55],cube[61],cube[67]] + cube[181:183] + cube[75:79] + cube[187:189] + cube[81:85] + cube[193:195] + cube[87:91] + cube[199:201] + cube[93:97] + cube[205:207] + cube[99:103] + cube[211:213] + cube[105:149] + [cube[32],cube[31]] + cube[151:155] + [cube[26],cube[25]] + cube[157:161] + [cube[20],cube[19]] + cube[163:167] + [cube[14],cube[13]] + cube[169:173] + [cube[8],cube[7]] + cube[175:179] + [cube[2],cube[1],cube[180],cube[179]] + cube[183:187] + [cube[174],cube[173]] + cube[189:193] + [cube[168],cube[167]] + cube[195:199] + [cube[162],cube[161]] + cube[201:205] + [cube[156],cube[155]] + cube[207:211] + [cube[150],cube[149]] + cube[213:217]

def rotate_666_Lw2(cube):
    return [cube[0]] + cube[181:183] + cube[3:7] + cube[187:189] + cube[9:13] + cube[193:195] + cube[15:19] + cube[199:201] + cube[21:25] + cube[205:207] + cube[27:31] + cube[211:213] + cube[33:37] + [cube[72],cube[71],cube[70],cube[69],cube[68],cube[67],cube[66],cube[65],cube[64],cube[63],cube[62],cube[61],cube[60],cube[59],cube[58],cube[57],cube[56],cube[55],cube[54],cube[53],cube[52],cube[51],cube[50],cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[180],cube[179]] + cube[75:79] + [cube[174],cube[173]] + cube[81:85] + [cube[168],cube[167]] + cube[87:91] + [cube[162],cube[161]] + cube[93:97] + [cube[156],cube[155]] + cube[99:103] + [cube[150],cube[149]] + cube[105:149] + [cube[104],cube[103]] + cube[151:155] + [cube[98],cube[97]] + cube[157:161] + [cube[92],cube[91]] + cube[163:167] + [cube[86],cube[85]] + cube[169:173] + [cube[80],cube[79]] + cube[175:179] + [cube[74],cube[73]] + cube[1:3] + cube[183:187] + cube[7:9] + cube[189:193] + cube[13:15] + cube[195:199] + cube[19:21] + cube[201:205] + cube[25:27] + cube[207:211] + cube[31:33] + cube[213:217]

def rotate_666_3Lw(cube):
    return [cube[0],cube[180],cube[179],cube[178]] + cube[4:7] + [cube[174],cube[173],cube[172]] + cube[10:13] + [cube[168],cube[167],cube[166]] + cube[16:19] + [cube[162],cube[161],cube[160]] + cube[22:25] + [cube[156],cube[155],cube[154]] + cube[28:31] + [cube[150],cube[149],cube[148]] + cube[34:37] + [cube[67],cube[61],cube[55],cube[49],cube[43],cube[37],cube[68],cube[62],cube[56],cube[50],cube[44],cube[38],cube[69],cube[63],cube[57],cube[51],cube[45],cube[39],cube[70],cube[64],cube[58],cube[52],cube[46],cube[40],cube[71],cube[65],cube[59],cube[53],cube[47],cube[41],cube[72],cube[66],cube[60],cube[54],cube[48],cube[42]] + cube[1:4] + cube[76:79] + cube[7:10] + cube[82:85] + cube[13:16] + cube[88:91] + cube[19:22] + cube[94:97] + cube[25:28] + cube[100:103] + cube[31:34] + cube[106:148] + [cube[213],cube[212],cube[211]] + cube[151:154] + [cube[207],cube[206],cube[205]] + cube[157:160] + [cube[201],cube[200],cube[199]] + cube[163:166] + [cube[195],cube[194],cube[193]] + cube[169:172] + [cube[189],cube[188],cube[187]] + cube[175:178] + [cube[183],cube[182],cube[181]] + cube[73:76] + cube[184:187] + cube[79:82] + cube[190:193] + cube[85:88] + cube[196:199] + cube[91:94] + cube[202:205] + cube[97:100] + cube[208:211] + cube[103:106] + cube[214:217]

def rotate_666_3Lw_prime(cube):
    return [cube[0]] + cube[73:76] + cube[4:7] + cube[79:82] + cube[10:13] + cube[85:88] + cube[16:19] + cube[91:94] + cube[22:25] + cube[97:100] + cube[28:31] + cube[103:106] + cube[34:37] + [cube[42],cube[48],cube[54],cube[60],cube[66],cube[72],cube[41],cube[47],cube[53],cube[59],cube[65],cube[71],cube[40],cube[46],cube[52],cube[58],cube[64],cube[70],cube[39],cube[45],cube[51],cube[57],cube[63],cube[69],cube[38],cube[44],cube[50],cube[56],cube[62],cube[68],cube[37],cube[43],cube[49],cube[55],cube[61],cube[67]] + cube[181:184] + cube[76:79] + cube[187:190] + cube[82:85] + cube[193:196] + cube[88:91] + cube[199:202] + cube[94:97] + cube[205:208] + cube[100:103] + cube[211:214] + cube[106:148] + [cube[33],cube[32],cube[31]] + cube[151:154] + [cube[27],cube[26],cube[25]] + cube[157:160] + [cube[21],cube[20],cube[19]] + cube[163:166] + [cube[15],cube[14],cube[13]] + cube[169:172] + [cube[9],cube[8],cube[7]] + cube[175:178] + [cube[3],cube[2],cube[1],cube[180],cube[179],cube[178]] + cube[184:187] + [cube[174],cube[173],cube[172]] + cube[190:193] + [cube[168],cube[167],cube[166]] + cube[196:199] + [cube[162],cube[161],cube[160]] + cube[202:205] + [cube[156],cube[155],cube[154]] + cube[208:211] + [cube[150],cube[149],cube[148]] + cube[214:217]

def rotate_666_3Lw2(cube):
    return [cube[0]] + cube[181:184] + cube[4:7] + cube[187:190] + cube[10:13] + cube[193:196] + cube[16:19] + cube[199:202] + cube[22:25] + cube[205:208] + cube[28:31] + cube[211:214] + cube[34:37] + [cube[72],cube[71],cube[70],cube[69],cube[68],cube[67],cube[66],cube[65],cube[64],cube[63],cube[62],cube[61],cube[60],cube[59],cube[58],cube[57],cube[56],cube[55],cube[54],cube[53],cube[52],cube[51],cube[50],cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[180],cube[179],cube[178]] + cube[76:79] + [cube[174],cube[173],cube[172]] + cube[82:85] + [cube[168],cube[167],cube[166]] + cube[88:91] + [cube[162],cube[161],cube[160]] + cube[94:97] + [cube[156],cube[155],cube[154]] + cube[100:103] + [cube[150],cube[149],cube[148]] + cube[106:148] + [cube[105],cube[104],cube[103]] + cube[151:154] + [cube[99],cube[98],cube[97]] + cube[157:160] + [cube[93],cube[92],cube[91]] + cube[163:166] + [cube[87],cube[86],cube[85]] + cube[169:172] + [cube[81],cube[80],cube[79]] + cube[175:178] + [cube[75],cube[74],cube[73]] + cube[1:4] + cube[184:187] + cube[7:10] + cube[190:193] + cube[13:16] + cube[196:199] + cube[19:22] + cube[202:205] + cube[25:28] + cube[208:211] + cube[31:34] + cube[214:217]

def rotate_666_F(cube):
    return cube[0:31] + [cube[72],cube[66],cube[60],cube[54],cube[48],cube[42]] + cube[37:42] + [cube[181]] + cube[43:48] + [cube[182]] + cube[49:54] + [cube[183]] + cube[55:60] + [cube[184]] + cube[61:66] + [cube[185]] + cube[67:72] + [cube[186],cube[103],cube[97],cube[91],cube[85],cube[79],cube[73],cube[104],cube[98],cube[92],cube[86],cube[80],cube[74],cube[105],cube[99],cube[93],cube[87],cube[81],cube[75],cube[106],cube[100],cube[94],cube[88],cube[82],cube[76],cube[107],cube[101],cube[95],cube[89],cube[83],cube[77],cube[108],cube[102],cube[96],cube[90],cube[84],cube[78],cube[31]] + cube[110:115] + [cube[32]] + cube[116:121] + [cube[33]] + cube[122:127] + [cube[34]] + cube[128:133] + [cube[35]] + cube[134:139] + [cube[36]] + cube[140:181] + [cube[139],cube[133],cube[127],cube[121],cube[115],cube[109]] + cube[187:217]

def rotate_666_F_prime(cube):
    return cube[0:31] + [cube[109],cube[115],cube[121],cube[127],cube[133],cube[139]] + cube[37:42] + [cube[36]] + cube[43:48] + [cube[35]] + cube[49:54] + [cube[34]] + cube[55:60] + [cube[33]] + cube[61:66] + [cube[32]] + cube[67:72] + [cube[31],cube[78],cube[84],cube[90],cube[96],cube[102],cube[108],cube[77],cube[83],cube[89],cube[95],cube[101],cube[107],cube[76],cube[82],cube[88],cube[94],cube[100],cube[106],cube[75],cube[81],cube[87],cube[93],cube[99],cube[105],cube[74],cube[80],cube[86],cube[92],cube[98],cube[104],cube[73],cube[79],cube[85],cube[91],cube[97],cube[103],cube[186]] + cube[110:115] + [cube[185]] + cube[116:121] + [cube[184]] + cube[122:127] + [cube[183]] + cube[128:133] + [cube[182]] + cube[134:139] + [cube[181]] + cube[140:181] + [cube[42],cube[48],cube[54],cube[60],cube[66],cube[72]] + cube[187:217]

def rotate_666_F2(cube):
    return cube[0:31] + [cube[186],cube[185],cube[184],cube[183],cube[182],cube[181]] + cube[37:42] + [cube[139]] + cube[43:48] + [cube[133]] + cube[49:54] + [cube[127]] + cube[55:60] + [cube[121]] + cube[61:66] + [cube[115]] + cube[67:72] + [cube[109],cube[108],cube[107],cube[106],cube[105],cube[104],cube[103],cube[102],cube[101],cube[100],cube[99],cube[98],cube[97],cube[96],cube[95],cube[94],cube[93],cube[92],cube[91],cube[90],cube[89],cube[88],cube[87],cube[86],cube[85],cube[84],cube[83],cube[82],cube[81],cube[80],cube[79],cube[78],cube[77],cube[76],cube[75],cube[74],cube[73],cube[72]] + cube[110:115] + [cube[66]] + cube[116:121] + [cube[60]] + cube[122:127] + [cube[54]] + cube[128:133] + [cube[48]] + cube[134:139] + [cube[42]] + cube[140:181] + [cube[36],cube[35],cube[34],cube[33],cube[32],cube[31]] + cube[187:217]

def rotate_666_Fw(cube):
    return cube[0:25] + [cube[71],cube[65],cube[59],cube[53],cube[47],cube[41],cube[72],cube[66],cube[60],cube[54],cube[48],cube[42]] + cube[37:41] + [cube[187],cube[181]] + cube[43:47] + [cube[188],cube[182]] + cube[49:53] + [cube[189],cube[183]] + cube[55:59] + [cube[190],cube[184]] + cube[61:65] + [cube[191],cube[185]] + cube[67:71] + [cube[192],cube[186],cube[103],cube[97],cube[91],cube[85],cube[79],cube[73],cube[104],cube[98],cube[92],cube[86],cube[80],cube[74],cube[105],cube[99],cube[93],cube[87],cube[81],cube[75],cube[106],cube[100],cube[94],cube[88],cube[82],cube[76],cube[107],cube[101],cube[95],cube[89],cube[83],cube[77],cube[108],cube[102],cube[96],cube[90],cube[84],cube[78],cube[31],cube[25]] + cube[111:115] + [cube[32],cube[26]] + cube[117:121] + [cube[33],cube[27]] + cube[123:127] + [cube[34],cube[28]] + cube[129:133] + [cube[35],cube[29]] + cube[135:139] + [cube[36],cube[30]] + cube[141:181] + [cube[139],cube[133],cube[127],cube[121],cube[115],cube[109],cube[140],cube[134],cube[128],cube[122],cube[116],cube[110]] + cube[193:217]

def rotate_666_Fw_prime(cube):
    return cube[0:25] + [cube[110],cube[116],cube[122],cube[128],cube[134],cube[140],cube[109],cube[115],cube[121],cube[127],cube[133],cube[139]] + cube[37:41] + [cube[30],cube[36]] + cube[43:47] + [cube[29],cube[35]] + cube[49:53] + [cube[28],cube[34]] + cube[55:59] + [cube[27],cube[33]] + cube[61:65] + [cube[26],cube[32]] + cube[67:71] + [cube[25],cube[31],cube[78],cube[84],cube[90],cube[96],cube[102],cube[108],cube[77],cube[83],cube[89],cube[95],cube[101],cube[107],cube[76],cube[82],cube[88],cube[94],cube[100],cube[106],cube[75],cube[81],cube[87],cube[93],cube[99],cube[105],cube[74],cube[80],cube[86],cube[92],cube[98],cube[104],cube[73],cube[79],cube[85],cube[91],cube[97],cube[103],cube[186],cube[192]] + cube[111:115] + [cube[185],cube[191]] + cube[117:121] + [cube[184],cube[190]] + cube[123:127] + [cube[183],cube[189]] + cube[129:133] + [cube[182],cube[188]] + cube[135:139] + [cube[181],cube[187]] + cube[141:181] + [cube[42],cube[48],cube[54],cube[60],cube[66],cube[72],cube[41],cube[47],cube[53],cube[59],cube[65],cube[71]] + cube[193:217]

def rotate_666_Fw2(cube):
    return cube[0:25] + [cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181]] + cube[37:41] + [cube[140],cube[139]] + cube[43:47] + [cube[134],cube[133]] + cube[49:53] + [cube[128],cube[127]] + cube[55:59] + [cube[122],cube[121]] + cube[61:65] + [cube[116],cube[115]] + cube[67:71] + [cube[110],cube[109],cube[108],cube[107],cube[106],cube[105],cube[104],cube[103],cube[102],cube[101],cube[100],cube[99],cube[98],cube[97],cube[96],cube[95],cube[94],cube[93],cube[92],cube[91],cube[90],cube[89],cube[88],cube[87],cube[86],cube[85],cube[84],cube[83],cube[82],cube[81],cube[80],cube[79],cube[78],cube[77],cube[76],cube[75],cube[74],cube[73],cube[72],cube[71]] + cube[111:115] + [cube[66],cube[65]] + cube[117:121] + [cube[60],cube[59]] + cube[123:127] + [cube[54],cube[53]] + cube[129:133] + [cube[48],cube[47]] + cube[135:139] + [cube[42],cube[41]] + cube[141:181] + [cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25]] + cube[193:217]

def rotate_666_3Fw(cube):
    return cube[0:19] + [cube[70],cube[64],cube[58],cube[52],cube[46],cube[40],cube[71],cube[65],cube[59],cube[53],cube[47],cube[41],cube[72],cube[66],cube[60],cube[54],cube[48],cube[42]] + cube[37:40] + [cube[193],cube[187],cube[181]] + cube[43:46] + [cube[194],cube[188],cube[182]] + cube[49:52] + [cube[195],cube[189],cube[183]] + cube[55:58] + [cube[196],cube[190],cube[184]] + cube[61:64] + [cube[197],cube[191],cube[185]] + cube[67:70] + [cube[198],cube[192],cube[186],cube[103],cube[97],cube[91],cube[85],cube[79],cube[73],cube[104],cube[98],cube[92],cube[86],cube[80],cube[74],cube[105],cube[99],cube[93],cube[87],cube[81],cube[75],cube[106],cube[100],cube[94],cube[88],cube[82],cube[76],cube[107],cube[101],cube[95],cube[89],cube[83],cube[77],cube[108],cube[102],cube[96],cube[90],cube[84],cube[78],cube[31],cube[25],cube[19]] + cube[112:115] + [cube[32],cube[26],cube[20]] + cube[118:121] + [cube[33],cube[27],cube[21]] + cube[124:127] + [cube[34],cube[28],cube[22]] + cube[130:133] + [cube[35],cube[29],cube[23]] + cube[136:139] + [cube[36],cube[30],cube[24]] + cube[142:181] + [cube[139],cube[133],cube[127],cube[121],cube[115],cube[109],cube[140],cube[134],cube[128],cube[122],cube[116],cube[110],cube[141],cube[135],cube[129],cube[123],cube[117],cube[111]] + cube[199:217]

def rotate_666_3Fw_prime(cube):
    return cube[0:19] + [cube[111],cube[117],cube[123],cube[129],cube[135],cube[141],cube[110],cube[116],cube[122],cube[128],cube[134],cube[140],cube[109],cube[115],cube[121],cube[127],cube[133],cube[139]] + cube[37:40] + [cube[24],cube[30],cube[36]] + cube[43:46] + [cube[23],cube[29],cube[35]] + cube[49:52] + [cube[22],cube[28],cube[34]] + cube[55:58] + [cube[21],cube[27],cube[33]] + cube[61:64] + [cube[20],cube[26],cube[32]] + cube[67:70] + [cube[19],cube[25],cube[31],cube[78],cube[84],cube[90],cube[96],cube[102],cube[108],cube[77],cube[83],cube[89],cube[95],cube[101],cube[107],cube[76],cube[82],cube[88],cube[94],cube[100],cube[106],cube[75],cube[81],cube[87],cube[93],cube[99],cube[105],cube[74],cube[80],cube[86],cube[92],cube[98],cube[104],cube[73],cube[79],cube[85],cube[91],cube[97],cube[103],cube[186],cube[192],cube[198]] + cube[112:115] + [cube[185],cube[191],cube[197]] + cube[118:121] + [cube[184],cube[190],cube[196]] + cube[124:127] + [cube[183],cube[189],cube[195]] + cube[130:133] + [cube[182],cube[188],cube[194]] + cube[136:139] + [cube[181],cube[187],cube[193]] + cube[142:181] + [cube[42],cube[48],cube[54],cube[60],cube[66],cube[72],cube[41],cube[47],cube[53],cube[59],cube[65],cube[71],cube[40],cube[46],cube[52],cube[58],cube[64],cube[70]] + cube[199:217]

def rotate_666_3Fw2(cube):
    return cube[0:19] + [cube[198],cube[197],cube[196],cube[195],cube[194],cube[193],cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181]] + cube[37:40] + [cube[141],cube[140],cube[139]] + cube[43:46] + [cube[135],cube[134],cube[133]] + cube[49:52] + [cube[129],cube[128],cube[127]] + cube[55:58] + [cube[123],cube[122],cube[121]] + cube[61:64] + [cube[117],cube[116],cube[115]] + cube[67:70] + [cube[111],cube[110],cube[109],cube[108],cube[107],cube[106],cube[105],cube[104],cube[103],cube[102],cube[101],cube[100],cube[99],cube[98],cube[97],cube[96],cube[95],cube[94],cube[93],cube[92],cube[91],cube[90],cube[89],cube[88],cube[87],cube[86],cube[85],cube[84],cube[83],cube[82],cube[81],cube[80],cube[79],cube[78],cube[77],cube[76],cube[75],cube[74],cube[73],cube[72],cube[71],cube[70]] + cube[112:115] + [cube[66],cube[65],cube[64]] + cube[118:121] + [cube[60],cube[59],cube[58]] + cube[124:127] + [cube[54],cube[53],cube[52]] + cube[130:133] + [cube[48],cube[47],cube[46]] + cube[136:139] + [cube[42],cube[41],cube[40]] + cube[142:181] + [cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19]] + cube[199:217]

def rotate_666_R(cube):
    return cube[0:6] + [cube[78]] + cube[7:12] + [cube[84]] + cube[13:18] + [cube[90]] + cube[19:24] + [cube[96]] + cube[25:30] + [cube[102]] + cube[31:36] + [cube[108]] + cube[37:78] + [cube[186]] + cube[79:84] + [cube[192]] + cube[85:90] + [cube[198]] + cube[91:96] + [cube[204]] + cube[97:102] + [cube[210]] + cube[103:108] + [cube[216],cube[139],cube[133],cube[127],cube[121],cube[115],cube[109],cube[140],cube[134],cube[128],cube[122],cube[116],cube[110],cube[141],cube[135],cube[129],cube[123],cube[117],cube[111],cube[142],cube[136],cube[130],cube[124],cube[118],cube[112],cube[143],cube[137],cube[131],cube[125],cube[119],cube[113],cube[144],cube[138],cube[132],cube[126],cube[120],cube[114],cube[36]] + cube[146:151] + [cube[30]] + cube[152:157] + [cube[24]] + cube[158:163] + [cube[18]] + cube[164:169] + [cube[12]] + cube[170:175] + [cube[6]] + cube[176:186] + [cube[175]] + cube[187:192] + [cube[169]] + cube[193:198] + [cube[163]] + cube[199:204] + [cube[157]] + cube[205:210] + [cube[151]] + cube[211:216] + [cube[145]]

def rotate_666_R_prime(cube):
    return cube[0:6] + [cube[175]] + cube[7:12] + [cube[169]] + cube[13:18] + [cube[163]] + cube[19:24] + [cube[157]] + cube[25:30] + [cube[151]] + cube[31:36] + [cube[145]] + cube[37:78] + [cube[6]] + cube[79:84] + [cube[12]] + cube[85:90] + [cube[18]] + cube[91:96] + [cube[24]] + cube[97:102] + [cube[30]] + cube[103:108] + [cube[36],cube[114],cube[120],cube[126],cube[132],cube[138],cube[144],cube[113],cube[119],cube[125],cube[131],cube[137],cube[143],cube[112],cube[118],cube[124],cube[130],cube[136],cube[142],cube[111],cube[117],cube[123],cube[129],cube[135],cube[141],cube[110],cube[116],cube[122],cube[128],cube[134],cube[140],cube[109],cube[115],cube[121],cube[127],cube[133],cube[139],cube[216]] + cube[146:151] + [cube[210]] + cube[152:157] + [cube[204]] + cube[158:163] + [cube[198]] + cube[164:169] + [cube[192]] + cube[170:175] + [cube[186]] + cube[176:186] + [cube[78]] + cube[187:192] + [cube[84]] + cube[193:198] + [cube[90]] + cube[199:204] + [cube[96]] + cube[205:210] + [cube[102]] + cube[211:216] + [cube[108]]

def rotate_666_R2(cube):
    return cube[0:6] + [cube[186]] + cube[7:12] + [cube[192]] + cube[13:18] + [cube[198]] + cube[19:24] + [cube[204]] + cube[25:30] + [cube[210]] + cube[31:36] + [cube[216]] + cube[37:78] + [cube[175]] + cube[79:84] + [cube[169]] + cube[85:90] + [cube[163]] + cube[91:96] + [cube[157]] + cube[97:102] + [cube[151]] + cube[103:108] + [cube[145],cube[144],cube[143],cube[142],cube[141],cube[140],cube[139],cube[138],cube[137],cube[136],cube[135],cube[134],cube[133],cube[132],cube[131],cube[130],cube[129],cube[128],cube[127],cube[126],cube[125],cube[124],cube[123],cube[122],cube[121],cube[120],cube[119],cube[118],cube[117],cube[116],cube[115],cube[114],cube[113],cube[112],cube[111],cube[110],cube[109],cube[108]] + cube[146:151] + [cube[102]] + cube[152:157] + [cube[96]] + cube[158:163] + [cube[90]] + cube[164:169] + [cube[84]] + cube[170:175] + [cube[78]] + cube[176:186] + [cube[6]] + cube[187:192] + [cube[12]] + cube[193:198] + [cube[18]] + cube[199:204] + [cube[24]] + cube[205:210] + [cube[30]] + cube[211:216] + [cube[36]]

def rotate_666_Rw(cube):
    return cube[0:5] + cube[77:79] + cube[7:11] + cube[83:85] + cube[13:17] + cube[89:91] + cube[19:23] + cube[95:97] + cube[25:29] + cube[101:103] + cube[31:35] + cube[107:109] + cube[37:77] + cube[185:187] + cube[79:83] + cube[191:193] + cube[85:89] + cube[197:199] + cube[91:95] + cube[203:205] + cube[97:101] + cube[209:211] + cube[103:107] + cube[215:217] + [cube[139],cube[133],cube[127],cube[121],cube[115],cube[109],cube[140],cube[134],cube[128],cube[122],cube[116],cube[110],cube[141],cube[135],cube[129],cube[123],cube[117],cube[111],cube[142],cube[136],cube[130],cube[124],cube[118],cube[112],cube[143],cube[137],cube[131],cube[125],cube[119],cube[113],cube[144],cube[138],cube[132],cube[126],cube[120],cube[114],cube[36],cube[35]] + cube[147:151] + [cube[30],cube[29]] + cube[153:157] + [cube[24],cube[23]] + cube[159:163] + [cube[18],cube[17]] + cube[165:169] + [cube[12],cube[11]] + cube[171:175] + [cube[6],cube[5]] + cube[177:185] + [cube[176],cube[175]] + cube[187:191] + [cube[170],cube[169]] + cube[193:197] + [cube[164],cube[163]] + cube[199:203] + [cube[158],cube[157]] + cube[205:209] + [cube[152],cube[151]] + cube[211:215] + [cube[146],cube[145]]

def rotate_666_Rw_prime(cube):
    return cube[0:5] + [cube[176],cube[175]] + cube[7:11] + [cube[170],cube[169]] + cube[13:17] + [cube[164],cube[163]] + cube[19:23] + [cube[158],cube[157]] + cube[25:29] + [cube[152],cube[151]] + cube[31:35] + [cube[146],cube[145]] + cube[37:77] + cube[5:7] + cube[79:83] + cube[11:13] + cube[85:89] + cube[17:19] + cube[91:95] + cube[23:25] + cube[97:101] + cube[29:31] + cube[103:107] + cube[35:37] + [cube[114],cube[120],cube[126],cube[132],cube[138],cube[144],cube[113],cube[119],cube[125],cube[131],cube[137],cube[143],cube[112],cube[118],cube[124],cube[130],cube[136],cube[142],cube[111],cube[117],cube[123],cube[129],cube[135],cube[141],cube[110],cube[116],cube[122],cube[128],cube[134],cube[140],cube[109],cube[115],cube[121],cube[127],cube[133],cube[139],cube[216],cube[215]] + cube[147:151] + [cube[210],cube[209]] + cube[153:157] + [cube[204],cube[203]] + cube[159:163] + [cube[198],cube[197]] + cube[165:169] + [cube[192],cube[191]] + cube[171:175] + [cube[186],cube[185]] + cube[177:185] + cube[77:79] + cube[187:191] + cube[83:85] + cube[193:197] + cube[89:91] + cube[199:203] + cube[95:97] + cube[205:209] + cube[101:103] + cube[211:215] + cube[107:109]

def rotate_666_Rw2(cube):
    return cube[0:5] + cube[185:187] + cube[7:11] + cube[191:193] + cube[13:17] + cube[197:199] + cube[19:23] + cube[203:205] + cube[25:29] + cube[209:211] + cube[31:35] + cube[215:217] + cube[37:77] + [cube[176],cube[175]] + cube[79:83] + [cube[170],cube[169]] + cube[85:89] + [cube[164],cube[163]] + cube[91:95] + [cube[158],cube[157]] + cube[97:101] + [cube[152],cube[151]] + cube[103:107] + [cube[146],cube[145],cube[144],cube[143],cube[142],cube[141],cube[140],cube[139],cube[138],cube[137],cube[136],cube[135],cube[134],cube[133],cube[132],cube[131],cube[130],cube[129],cube[128],cube[127],cube[126],cube[125],cube[124],cube[123],cube[122],cube[121],cube[120],cube[119],cube[118],cube[117],cube[116],cube[115],cube[114],cube[113],cube[112],cube[111],cube[110],cube[109],cube[108],cube[107]] + cube[147:151] + [cube[102],cube[101]] + cube[153:157] + [cube[96],cube[95]] + cube[159:163] + [cube[90],cube[89]] + cube[165:169] + [cube[84],cube[83]] + cube[171:175] + [cube[78],cube[77]] + cube[177:185] + cube[5:7] + cube[187:191] + cube[11:13] + cube[193:197] + cube[17:19] + cube[199:203] + cube[23:25] + cube[205:209] + cube[29:31] + cube[211:215] + cube[35:37]

def rotate_666_3Rw(cube):
    return cube[0:4] + cube[76:79] + cube[7:10] + cube[82:85] + cube[13:16] + cube[88:91] + cube[19:22] + cube[94:97] + cube[25:28] + cube[100:103] + cube[31:34] + cube[106:109] + cube[37:76] + cube[184:187] + cube[79:82] + cube[190:193] + cube[85:88] + cube[196:199] + cube[91:94] + cube[202:205] + cube[97:100] + cube[208:211] + cube[103:106] + cube[214:217] + [cube[139],cube[133],cube[127],cube[121],cube[115],cube[109],cube[140],cube[134],cube[128],cube[122],cube[116],cube[110],cube[141],cube[135],cube[129],cube[123],cube[117],cube[111],cube[142],cube[136],cube[130],cube[124],cube[118],cube[112],cube[143],cube[137],cube[131],cube[125],cube[119],cube[113],cube[144],cube[138],cube[132],cube[126],cube[120],cube[114],cube[36],cube[35],cube[34]] + cube[148:151] + [cube[30],cube[29],cube[28]] + cube[154:157] + [cube[24],cube[23],cube[22]] + cube[160:163] + [cube[18],cube[17],cube[16]] + cube[166:169] + [cube[12],cube[11],cube[10]] + cube[172:175] + [cube[6],cube[5],cube[4]] + cube[178:184] + [cube[177],cube[176],cube[175]] + cube[187:190] + [cube[171],cube[170],cube[169]] + cube[193:196] + [cube[165],cube[164],cube[163]] + cube[199:202] + [cube[159],cube[158],cube[157]] + cube[205:208] + [cube[153],cube[152],cube[151]] + cube[211:214] + [cube[147],cube[146],cube[145]]

def rotate_666_3Rw_prime(cube):
    return cube[0:4] + [cube[177],cube[176],cube[175]] + cube[7:10] + [cube[171],cube[170],cube[169]] + cube[13:16] + [cube[165],cube[164],cube[163]] + cube[19:22] + [cube[159],cube[158],cube[157]] + cube[25:28] + [cube[153],cube[152],cube[151]] + cube[31:34] + [cube[147],cube[146],cube[145]] + cube[37:76] + cube[4:7] + cube[79:82] + cube[10:13] + cube[85:88] + cube[16:19] + cube[91:94] + cube[22:25] + cube[97:100] + cube[28:31] + cube[103:106] + cube[34:37] + [cube[114],cube[120],cube[126],cube[132],cube[138],cube[144],cube[113],cube[119],cube[125],cube[131],cube[137],cube[143],cube[112],cube[118],cube[124],cube[130],cube[136],cube[142],cube[111],cube[117],cube[123],cube[129],cube[135],cube[141],cube[110],cube[116],cube[122],cube[128],cube[134],cube[140],cube[109],cube[115],cube[121],cube[127],cube[133],cube[139],cube[216],cube[215],cube[214]] + cube[148:151] + [cube[210],cube[209],cube[208]] + cube[154:157] + [cube[204],cube[203],cube[202]] + cube[160:163] + [cube[198],cube[197],cube[196]] + cube[166:169] + [cube[192],cube[191],cube[190]] + cube[172:175] + [cube[186],cube[185],cube[184]] + cube[178:184] + cube[76:79] + cube[187:190] + cube[82:85] + cube[193:196] + cube[88:91] + cube[199:202] + cube[94:97] + cube[205:208] + cube[100:103] + cube[211:214] + cube[106:109]

def rotate_666_3Rw2(cube):
    return cube[0:4] + cube[184:187] + cube[7:10] + cube[190:193] + cube[13:16] + cube[196:199] + cube[19:22] + cube[202:205] + cube[25:28] + cube[208:211] + cube[31:34] + cube[214:217] + cube[37:76] + [cube[177],cube[176],cube[175]] + cube[79:82] + [cube[171],cube[170],cube[169]] + cube[85:88] + [cube[165],cube[164],cube[163]] + cube[91:94] + [cube[159],cube[158],cube[157]] + cube[97:100] + [cube[153],cube[152],cube[151]] + cube[103:106] + [cube[147],cube[146],cube[145],cube[144],cube[143],cube[142],cube[141],cube[140],cube[139],cube[138],cube[137],cube[136],cube[135],cube[134],cube[133],cube[132],cube[131],cube[130],cube[129],cube[128],cube[127],cube[126],cube[125],cube[124],cube[123],cube[122],cube[121],cube[120],cube[119],cube[118],cube[117],cube[116],cube[115],cube[114],cube[113],cube[112],cube[111],cube[110],cube[109],cube[108],cube[107],cube[106]] + cube[148:151] + [cube[102],cube[101],cube[100]] + cube[154:157] + [cube[96],cube[95],cube[94]] + cube[160:163] + [cube[90],cube[89],cube[88]] + cube[166:169] + [cube[84],cube[83],cube[82]] + cube[172:175] + [cube[78],cube[77],cube[76]] + cube[178:184] + cube[4:7] + cube[187:190] + cube[10:13] + cube[193:196] + cube[16:19] + cube[199:202] + cube[22:25] + cube[205:208] + cube[28:31] + cube[211:214] + cube[34:37]

def rotate_666_B(cube):
    return [cube[0],cube[114],cube[120],cube[126],cube[132],cube[138],cube[144]] + cube[7:37] + [cube[6]] + cube[38:43] + [cube[5]] + cube[44:49] + [cube[4]] + cube[50:55] + [cube[3]] + cube[56:61] + [cube[2]] + cube[62:67] + [cube[1]] + cube[68:114] + [cube[216]] + cube[115:120] + [cube[215]] + cube[121:126] + [cube[214]] + cube[127:132] + [cube[213]] + cube[133:138] + [cube[212]] + cube[139:144] + [cube[211],cube[175],cube[169],cube[163],cube[157],cube[151],cube[145],cube[176],cube[170],cube[164],cube[158],cube[152],cube[146],cube[177],cube[171],cube[165],cube[159],cube[153],cube[147],cube[178],cube[172],cube[166],cube[160],cube[154],cube[148],cube[179],cube[173],cube[167],cube[161],cube[155],cube[149],cube[180],cube[174],cube[168],cube[162],cube[156],cube[150]] + cube[181:211] + [cube[37],cube[43],cube[49],cube[55],cube[61],cube[67]]

def rotate_666_B_prime(cube):
    return [cube[0],cube[67],cube[61],cube[55],cube[49],cube[43],cube[37]] + cube[7:37] + [cube[211]] + cube[38:43] + [cube[212]] + cube[44:49] + [cube[213]] + cube[50:55] + [cube[214]] + cube[56:61] + [cube[215]] + cube[62:67] + [cube[216]] + cube[68:114] + [cube[1]] + cube[115:120] + [cube[2]] + cube[121:126] + [cube[3]] + cube[127:132] + [cube[4]] + cube[133:138] + [cube[5]] + cube[139:144] + [cube[6],cube[150],cube[156],cube[162],cube[168],cube[174],cube[180],cube[149],cube[155],cube[161],cube[167],cube[173],cube[179],cube[148],cube[154],cube[160],cube[166],cube[172],cube[178],cube[147],cube[153],cube[159],cube[165],cube[171],cube[177],cube[146],cube[152],cube[158],cube[164],cube[170],cube[176],cube[145],cube[151],cube[157],cube[163],cube[169],cube[175]] + cube[181:211] + [cube[144],cube[138],cube[132],cube[126],cube[120],cube[114]]

def rotate_666_B2(cube):
    return [cube[0],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211]] + cube[7:37] + [cube[144]] + cube[38:43] + [cube[138]] + cube[44:49] + [cube[132]] + cube[50:55] + [cube[126]] + cube[56:61] + [cube[120]] + cube[62:67] + [cube[114]] + cube[68:114] + [cube[67]] + cube[115:120] + [cube[61]] + cube[121:126] + [cube[55]] + cube[127:132] + [cube[49]] + cube[133:138] + [cube[43]] + cube[139:144] + [cube[37],cube[180],cube[179],cube[178],cube[177],cube[176],cube[175],cube[174],cube[173],cube[172],cube[171],cube[170],cube[169],cube[168],cube[167],cube[166],cube[165],cube[164],cube[163],cube[162],cube[161],cube[160],cube[159],cube[158],cube[157],cube[156],cube[155],cube[154],cube[153],cube[152],cube[151],cube[150],cube[149],cube[148],cube[147],cube[146],cube[145]] + cube[181:211] + [cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]]

def rotate_666_Bw(cube):
    return [cube[0],cube[114],cube[120],cube[126],cube[132],cube[138],cube[144],cube[113],cube[119],cube[125],cube[131],cube[137],cube[143]] + cube[13:37] + [cube[6],cube[12]] + cube[39:43] + [cube[5],cube[11]] + cube[45:49] + [cube[4],cube[10]] + cube[51:55] + [cube[3],cube[9]] + cube[57:61] + [cube[2],cube[8]] + cube[63:67] + [cube[1],cube[7]] + cube[69:113] + [cube[210],cube[216]] + cube[115:119] + [cube[209],cube[215]] + cube[121:125] + [cube[208],cube[214]] + cube[127:131] + [cube[207],cube[213]] + cube[133:137] + [cube[206],cube[212]] + cube[139:143] + [cube[205],cube[211],cube[175],cube[169],cube[163],cube[157],cube[151],cube[145],cube[176],cube[170],cube[164],cube[158],cube[152],cube[146],cube[177],cube[171],cube[165],cube[159],cube[153],cube[147],cube[178],cube[172],cube[166],cube[160],cube[154],cube[148],cube[179],cube[173],cube[167],cube[161],cube[155],cube[149],cube[180],cube[174],cube[168],cube[162],cube[156],cube[150]] + cube[181:205] + [cube[38],cube[44],cube[50],cube[56],cube[62],cube[68],cube[37],cube[43],cube[49],cube[55],cube[61],cube[67]]

def rotate_666_Bw_prime(cube):
    return [cube[0],cube[67],cube[61],cube[55],cube[49],cube[43],cube[37],cube[68],cube[62],cube[56],cube[50],cube[44],cube[38]] + cube[13:37] + [cube[211],cube[205]] + cube[39:43] + [cube[212],cube[206]] + cube[45:49] + [cube[213],cube[207]] + cube[51:55] + [cube[214],cube[208]] + cube[57:61] + [cube[215],cube[209]] + cube[63:67] + [cube[216],cube[210]] + cube[69:113] + [cube[7],cube[1]] + cube[115:119] + [cube[8],cube[2]] + cube[121:125] + [cube[9],cube[3]] + cube[127:131] + [cube[10],cube[4]] + cube[133:137] + [cube[11],cube[5]] + cube[139:143] + [cube[12],cube[6],cube[150],cube[156],cube[162],cube[168],cube[174],cube[180],cube[149],cube[155],cube[161],cube[167],cube[173],cube[179],cube[148],cube[154],cube[160],cube[166],cube[172],cube[178],cube[147],cube[153],cube[159],cube[165],cube[171],cube[177],cube[146],cube[152],cube[158],cube[164],cube[170],cube[176],cube[145],cube[151],cube[157],cube[163],cube[169],cube[175]] + cube[181:205] + [cube[143],cube[137],cube[131],cube[125],cube[119],cube[113],cube[144],cube[138],cube[132],cube[126],cube[120],cube[114]]

def rotate_666_Bw2(cube):
    return [cube[0],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205]] + cube[13:37] + [cube[144],cube[143]] + cube[39:43] + [cube[138],cube[137]] + cube[45:49] + [cube[132],cube[131]] + cube[51:55] + [cube[126],cube[125]] + cube[57:61] + [cube[120],cube[119]] + cube[63:67] + [cube[114],cube[113]] + cube[69:113] + [cube[68],cube[67]] + cube[115:119] + [cube[62],cube[61]] + cube[121:125] + [cube[56],cube[55]] + cube[127:131] + [cube[50],cube[49]] + cube[133:137] + [cube[44],cube[43]] + cube[139:143] + [cube[38],cube[37],cube[180],cube[179],cube[178],cube[177],cube[176],cube[175],cube[174],cube[173],cube[172],cube[171],cube[170],cube[169],cube[168],cube[167],cube[166],cube[165],cube[164],cube[163],cube[162],cube[161],cube[160],cube[159],cube[158],cube[157],cube[156],cube[155],cube[154],cube[153],cube[152],cube[151],cube[150],cube[149],cube[148],cube[147],cube[146],cube[145]] + cube[181:205] + [cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]]

def rotate_666_3Bw(cube):
    return [cube[0],cube[114],cube[120],cube[126],cube[132],cube[138],cube[144],cube[113],cube[119],cube[125],cube[131],cube[137],cube[143],cube[112],cube[118],cube[124],cube[130],cube[136],cube[142]] + cube[19:37] + [cube[6],cube[12],cube[18]] + cube[40:43] + [cube[5],cube[11],cube[17]] + cube[46:49] + [cube[4],cube[10],cube[16]] + cube[52:55] + [cube[3],cube[9],cube[15]] + cube[58:61] + [cube[2],cube[8],cube[14]] + cube[64:67] + [cube[1],cube[7],cube[13]] + cube[70:112] + [cube[204],cube[210],cube[216]] + cube[115:118] + [cube[203],cube[209],cube[215]] + cube[121:124] + [cube[202],cube[208],cube[214]] + cube[127:130] + [cube[201],cube[207],cube[213]] + cube[133:136] + [cube[200],cube[206],cube[212]] + cube[139:142] + [cube[199],cube[205],cube[211],cube[175],cube[169],cube[163],cube[157],cube[151],cube[145],cube[176],cube[170],cube[164],cube[158],cube[152],cube[146],cube[177],cube[171],cube[165],cube[159],cube[153],cube[147],cube[178],cube[172],cube[166],cube[160],cube[154],cube[148],cube[179],cube[173],cube[167],cube[161],cube[155],cube[149],cube[180],cube[174],cube[168],cube[162],cube[156],cube[150]] + cube[181:199] + [cube[39],cube[45],cube[51],cube[57],cube[63],cube[69],cube[38],cube[44],cube[50],cube[56],cube[62],cube[68],cube[37],cube[43],cube[49],cube[55],cube[61],cube[67]]

def rotate_666_3Bw_prime(cube):
    return [cube[0],cube[67],cube[61],cube[55],cube[49],cube[43],cube[37],cube[68],cube[62],cube[56],cube[50],cube[44],cube[38],cube[69],cube[63],cube[57],cube[51],cube[45],cube[39]] + cube[19:37] + [cube[211],cube[205],cube[199]] + cube[40:43] + [cube[212],cube[206],cube[200]] + cube[46:49] + [cube[213],cube[207],cube[201]] + cube[52:55] + [cube[214],cube[208],cube[202]] + cube[58:61] + [cube[215],cube[209],cube[203]] + cube[64:67] + [cube[216],cube[210],cube[204]] + cube[70:112] + [cube[13],cube[7],cube[1]] + cube[115:118] + [cube[14],cube[8],cube[2]] + cube[121:124] + [cube[15],cube[9],cube[3]] + cube[127:130] + [cube[16],cube[10],cube[4]] + cube[133:136] + [cube[17],cube[11],cube[5]] + cube[139:142] + [cube[18],cube[12],cube[6],cube[150],cube[156],cube[162],cube[168],cube[174],cube[180],cube[149],cube[155],cube[161],cube[167],cube[173],cube[179],cube[148],cube[154],cube[160],cube[166],cube[172],cube[178],cube[147],cube[153],cube[159],cube[165],cube[171],cube[177],cube[146],cube[152],cube[158],cube[164],cube[170],cube[176],cube[145],cube[151],cube[157],cube[163],cube[169],cube[175]] + cube[181:199] + [cube[142],cube[136],cube[130],cube[124],cube[118],cube[112],cube[143],cube[137],cube[131],cube[125],cube[119],cube[113],cube[144],cube[138],cube[132],cube[126],cube[120],cube[114]]

def rotate_666_3Bw2(cube):
    return [cube[0],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199]] + cube[19:37] + [cube[144],cube[143],cube[142]] + cube[40:43] + [cube[138],cube[137],cube[136]] + cube[46:49] + [cube[132],cube[131],cube[130]] + cube[52:55] + [cube[126],cube[125],cube[124]] + cube[58:61] + [cube[120],cube[119],cube[118]] + cube[64:67] + [cube[114],cube[113],cube[112]] + cube[70:112] + [cube[69],cube[68],cube[67]] + cube[115:118] + [cube[63],cube[62],cube[61]] + cube[121:124] + [cube[57],cube[56],cube[55]] + cube[127:130] + [cube[51],cube[50],cube[49]] + cube[133:136] + [cube[45],cube[44],cube[43]] + cube[139:142] + [cube[39],cube[38],cube[37],cube[180],cube[179],cube[178],cube[177],cube[176],cube[175],cube[174],cube[173],cube[172],cube[171],cube[170],cube[169],cube[168],cube[167],cube[166],cube[165],cube[164],cube[163],cube[162],cube[161],cube[160],cube[159],cube[158],cube[157],cube[156],cube[155],cube[154],cube[153],cube[152],cube[151],cube[150],cube[149],cube[148],cube[147],cube[146],cube[145]] + cube[181:199] + [cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]]

def rotate_666_D(cube):
    return cube[0:67] + cube[175:181] + cube[73:103] + cube[67:73] + cube[109:139] + cube[103:109] + cube[145:175] + cube[139:145] + [cube[211],cube[205],cube[199],cube[193],cube[187],cube[181],cube[212],cube[206],cube[200],cube[194],cube[188],cube[182],cube[213],cube[207],cube[201],cube[195],cube[189],cube[183],cube[214],cube[208],cube[202],cube[196],cube[190],cube[184],cube[215],cube[209],cube[203],cube[197],cube[191],cube[185],cube[216],cube[210],cube[204],cube[198],cube[192],cube[186]]

def rotate_666_D_prime(cube):
    return cube[0:67] + cube[103:109] + cube[73:103] + cube[139:145] + cube[109:139] + cube[175:181] + cube[145:175] + cube[67:73] + [cube[186],cube[192],cube[198],cube[204],cube[210],cube[216],cube[185],cube[191],cube[197],cube[203],cube[209],cube[215],cube[184],cube[190],cube[196],cube[202],cube[208],cube[214],cube[183],cube[189],cube[195],cube[201],cube[207],cube[213],cube[182],cube[188],cube[194],cube[200],cube[206],cube[212],cube[181],cube[187],cube[193],cube[199],cube[205],cube[211]]

def rotate_666_D2(cube):
    return cube[0:67] + cube[139:145] + cube[73:103] + cube[175:181] + cube[109:139] + cube[67:73] + cube[145:175] + cube[103:109] + [cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197],cube[196],cube[195],cube[194],cube[193],cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181]]

def rotate_666_Dw(cube):
    return cube[0:61] + cube[169:181] + cube[73:97] + cube[61:73] + cube[109:133] + cube[97:109] + cube[145:169] + cube[133:145] + [cube[211],cube[205],cube[199],cube[193],cube[187],cube[181],cube[212],cube[206],cube[200],cube[194],cube[188],cube[182],cube[213],cube[207],cube[201],cube[195],cube[189],cube[183],cube[214],cube[208],cube[202],cube[196],cube[190],cube[184],cube[215],cube[209],cube[203],cube[197],cube[191],cube[185],cube[216],cube[210],cube[204],cube[198],cube[192],cube[186]]

def rotate_666_Dw_prime(cube):
    return cube[0:61] + cube[97:109] + cube[73:97] + cube[133:145] + cube[109:133] + cube[169:181] + cube[145:169] + cube[61:73] + [cube[186],cube[192],cube[198],cube[204],cube[210],cube[216],cube[185],cube[191],cube[197],cube[203],cube[209],cube[215],cube[184],cube[190],cube[196],cube[202],cube[208],cube[214],cube[183],cube[189],cube[195],cube[201],cube[207],cube[213],cube[182],cube[188],cube[194],cube[200],cube[206],cube[212],cube[181],cube[187],cube[193],cube[199],cube[205],cube[211]]

def rotate_666_Dw2(cube):
    return cube[0:61] + cube[133:145] + cube[73:97] + cube[169:181] + cube[109:133] + cube[61:73] + cube[145:169] + cube[97:109] + [cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197],cube[196],cube[195],cube[194],cube[193],cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181]]

def rotate_666_3Dw(cube):
    return cube[0:55] + cube[163:181] + cube[73:91] + cube[55:73] + cube[109:127] + cube[91:109] + cube[145:163] + cube[127:145] + [cube[211],cube[205],cube[199],cube[193],cube[187],cube[181],cube[212],cube[206],cube[200],cube[194],cube[188],cube[182],cube[213],cube[207],cube[201],cube[195],cube[189],cube[183],cube[214],cube[208],cube[202],cube[196],cube[190],cube[184],cube[215],cube[209],cube[203],cube[197],cube[191],cube[185],cube[216],cube[210],cube[204],cube[198],cube[192],cube[186]]

def rotate_666_3Dw_prime(cube):
    return cube[0:55] + cube[91:109] + cube[73:91] + cube[127:145] + cube[109:127] + cube[163:181] + cube[145:163] + cube[55:73] + [cube[186],cube[192],cube[198],cube[204],cube[210],cube[216],cube[185],cube[191],cube[197],cube[203],cube[209],cube[215],cube[184],cube[190],cube[196],cube[202],cube[208],cube[214],cube[183],cube[189],cube[195],cube[201],cube[207],cube[213],cube[182],cube[188],cube[194],cube[200],cube[206],cube[212],cube[181],cube[187],cube[193],cube[199],cube[205],cube[211]]

def rotate_666_3Dw2(cube):
    return cube[0:55] + cube[127:145] + cube[73:91] + cube[163:181] + cube[109:127] + cube[55:73] + cube[145:163] + cube[91:109] + [cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197],cube[196],cube[195],cube[194],cube[193],cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181]]

def rotate_666_x(cube):
    return [cube[0]] + cube[73:109] + [cube[42],cube[48],cube[54],cube[60],cube[66],cube[72],cube[41],cube[47],cube[53],cube[59],cube[65],cube[71],cube[40],cube[46],cube[52],cube[58],cube[64],cube[70],cube[39],cube[45],cube[51],cube[57],cube[63],cube[69],cube[38],cube[44],cube[50],cube[56],cube[62],cube[68],cube[37],cube[43],cube[49],cube[55],cube[61],cube[67]] + cube[181:217] + [cube[139],cube[133],cube[127],cube[121],cube[115],cube[109],cube[140],cube[134],cube[128],cube[122],cube[116],cube[110],cube[141],cube[135],cube[129],cube[123],cube[117],cube[111],cube[142],cube[136],cube[130],cube[124],cube[118],cube[112],cube[143],cube[137],cube[131],cube[125],cube[119],cube[113],cube[144],cube[138],cube[132],cube[126],cube[120],cube[114],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1],cube[180],cube[179],cube[178],cube[177],cube[176],cube[175],cube[174],cube[173],cube[172],cube[171],cube[170],cube[169],cube[168],cube[167],cube[166],cube[165],cube[164],cube[163],cube[162],cube[161],cube[160],cube[159],cube[158],cube[157],cube[156],cube[155],cube[154],cube[153],cube[152],cube[151],cube[150],cube[149],cube[148],cube[147],cube[146],cube[145]]

def rotate_666_x_prime(cube):
    return [cube[0],cube[180],cube[179],cube[178],cube[177],cube[176],cube[175],cube[174],cube[173],cube[172],cube[171],cube[170],cube[169],cube[168],cube[167],cube[166],cube[165],cube[164],cube[163],cube[162],cube[161],cube[160],cube[159],cube[158],cube[157],cube[156],cube[155],cube[154],cube[153],cube[152],cube[151],cube[150],cube[149],cube[148],cube[147],cube[146],cube[145],cube[67],cube[61],cube[55],cube[49],cube[43],cube[37],cube[68],cube[62],cube[56],cube[50],cube[44],cube[38],cube[69],cube[63],cube[57],cube[51],cube[45],cube[39],cube[70],cube[64],cube[58],cube[52],cube[46],cube[40],cube[71],cube[65],cube[59],cube[53],cube[47],cube[41],cube[72],cube[66],cube[60],cube[54],cube[48],cube[42]] + cube[1:37] + [cube[114],cube[120],cube[126],cube[132],cube[138],cube[144],cube[113],cube[119],cube[125],cube[131],cube[137],cube[143],cube[112],cube[118],cube[124],cube[130],cube[136],cube[142],cube[111],cube[117],cube[123],cube[129],cube[135],cube[141],cube[110],cube[116],cube[122],cube[128],cube[134],cube[140],cube[109],cube[115],cube[121],cube[127],cube[133],cube[139],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197],cube[196],cube[195],cube[194],cube[193],cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181]] + cube[73:109]

def rotate_666_y(cube):
    return [cube[0],cube[31],cube[25],cube[19],cube[13],cube[7],cube[1],cube[32],cube[26],cube[20],cube[14],cube[8],cube[2],cube[33],cube[27],cube[21],cube[15],cube[9],cube[3],cube[34],cube[28],cube[22],cube[16],cube[10],cube[4],cube[35],cube[29],cube[23],cube[17],cube[11],cube[5],cube[36],cube[30],cube[24],cube[18],cube[12],cube[6]] + cube[73:181] + cube[37:73] + [cube[186],cube[192],cube[198],cube[204],cube[210],cube[216],cube[185],cube[191],cube[197],cube[203],cube[209],cube[215],cube[184],cube[190],cube[196],cube[202],cube[208],cube[214],cube[183],cube[189],cube[195],cube[201],cube[207],cube[213],cube[182],cube[188],cube[194],cube[200],cube[206],cube[212],cube[181],cube[187],cube[193],cube[199],cube[205],cube[211]]

def rotate_666_y_prime(cube):
    return [cube[0],cube[6],cube[12],cube[18],cube[24],cube[30],cube[36],cube[5],cube[11],cube[17],cube[23],cube[29],cube[35],cube[4],cube[10],cube[16],cube[22],cube[28],cube[34],cube[3],cube[9],cube[15],cube[21],cube[27],cube[33],cube[2],cube[8],cube[14],cube[20],cube[26],cube[32],cube[1],cube[7],cube[13],cube[19],cube[25],cube[31]] + cube[145:181] + cube[37:145] + [cube[211],cube[205],cube[199],cube[193],cube[187],cube[181],cube[212],cube[206],cube[200],cube[194],cube[188],cube[182],cube[213],cube[207],cube[201],cube[195],cube[189],cube[183],cube[214],cube[208],cube[202],cube[196],cube[190],cube[184],cube[215],cube[209],cube[203],cube[197],cube[191],cube[185],cube[216],cube[210],cube[204],cube[198],cube[192],cube[186]]

def rotate_666_z(cube):
    return [cube[0],cube[67],cube[61],cube[55],cube[49],cube[43],cube[37],cube[68],cube[62],cube[56],cube[50],cube[44],cube[38],cube[69],cube[63],cube[57],cube[51],cube[45],cube[39],cube[70],cube[64],cube[58],cube[52],cube[46],cube[40],cube[71],cube[65],cube[59],cube[53],cube[47],cube[41],cube[72],cube[66],cube[60],cube[54],cube[48],cube[42],cube[211],cube[205],cube[199],cube[193],cube[187],cube[181],cube[212],cube[206],cube[200],cube[194],cube[188],cube[182],cube[213],cube[207],cube[201],cube[195],cube[189],cube[183],cube[214],cube[208],cube[202],cube[196],cube[190],cube[184],cube[215],cube[209],cube[203],cube[197],cube[191],cube[185],cube[216],cube[210],cube[204],cube[198],cube[192],cube[186],cube[103],cube[97],cube[91],cube[85],cube[79],cube[73],cube[104],cube[98],cube[92],cube[86],cube[80],cube[74],cube[105],cube[99],cube[93],cube[87],cube[81],cube[75],cube[106],cube[100],cube[94],cube[88],cube[82],cube[76],cube[107],cube[101],cube[95],cube[89],cube[83],cube[77],cube[108],cube[102],cube[96],cube[90],cube[84],cube[78],cube[31],cube[25],cube[19],cube[13],cube[7],cube[1],cube[32],cube[26],cube[20],cube[14],cube[8],cube[2],cube[33],cube[27],cube[21],cube[15],cube[9],cube[3],cube[34],cube[28],cube[22],cube[16],cube[10],cube[4],cube[35],cube[29],cube[23],cube[17],cube[11],cube[5],cube[36],cube[30],cube[24],cube[18],cube[12],cube[6],cube[150],cube[156],cube[162],cube[168],cube[174],cube[180],cube[149],cube[155],cube[161],cube[167],cube[173],cube[179],cube[148],cube[154],cube[160],cube[166],cube[172],cube[178],cube[147],cube[153],cube[159],cube[165],cube[171],cube[177],cube[146],cube[152],cube[158],cube[164],cube[170],cube[176],cube[145],cube[151],cube[157],cube[163],cube[169],cube[175],cube[139],cube[133],cube[127],cube[121],cube[115],cube[109],cube[140],cube[134],cube[128],cube[122],cube[116],cube[110],cube[141],cube[135],cube[129],cube[123],cube[117],cube[111],cube[142],cube[136],cube[130],cube[124],cube[118],cube[112],cube[143],cube[137],cube[131],cube[125],cube[119],cube[113],cube[144],cube[138],cube[132],cube[126],cube[120],cube[114]]

def rotate_666_z_prime(cube):
    return [cube[0],cube[114],cube[120],cube[126],cube[132],cube[138],cube[144],cube[113],cube[119],cube[125],cube[131],cube[137],cube[143],cube[112],cube[118],cube[124],cube[130],cube[136],cube[142],cube[111],cube[117],cube[123],cube[129],cube[135],cube[141],cube[110],cube[116],cube[122],cube[128],cube[134],cube[140],cube[109],cube[115],cube[121],cube[127],cube[133],cube[139],cube[6],cube[12],cube[18],cube[24],cube[30],cube[36],cube[5],cube[11],cube[17],cube[23],cube[29],cube[35],cube[4],cube[10],cube[16],cube[22],cube[28],cube[34],cube[3],cube[9],cube[15],cube[21],cube[27],cube[33],cube[2],cube[8],cube[14],cube[20],cube[26],cube[32],cube[1],cube[7],cube[13],cube[19],cube[25],cube[31],cube[78],cube[84],cube[90],cube[96],cube[102],cube[108],cube[77],cube[83],cube[89],cube[95],cube[101],cube[107],cube[76],cube[82],cube[88],cube[94],cube[100],cube[106],cube[75],cube[81],cube[87],cube[93],cube[99],cube[105],cube[74],cube[80],cube[86],cube[92],cube[98],cube[104],cube[73],cube[79],cube[85],cube[91],cube[97],cube[103],cube[186],cube[192],cube[198],cube[204],cube[210],cube[216],cube[185],cube[191],cube[197],cube[203],cube[209],cube[215],cube[184],cube[190],cube[196],cube[202],cube[208],cube[214],cube[183],cube[189],cube[195],cube[201],cube[207],cube[213],cube[182],cube[188],cube[194],cube[200],cube[206],cube[212],cube[181],cube[187],cube[193],cube[199],cube[205],cube[211],cube[175],cube[169],cube[163],cube[157],cube[151],cube[145],cube[176],cube[170],cube[164],cube[158],cube[152],cube[146],cube[177],cube[171],cube[165],cube[159],cube[153],cube[147],cube[178],cube[172],cube[166],cube[160],cube[154],cube[148],cube[179],cube[173],cube[167],cube[161],cube[155],cube[149],cube[180],cube[174],cube[168],cube[162],cube[156],cube[150],cube[42],cube[48],cube[54],cube[60],cube[66],cube[72],cube[41],cube[47],cube[53],cube[59],cube[65],cube[71],cube[40],cube[46],cube[52],cube[58],cube[64],cube[70],cube[39],cube[45],cube[51],cube[57],cube[63],cube[69],cube[38],cube[44],cube[50],cube[56],cube[62],cube[68],cube[37],cube[43],cube[49],cube[55],cube[61],cube[67]]

rotate_mapper_666 = {
    "3Bw" : rotate_666_3Bw,
    "3Bw'" : rotate_666_3Bw_prime,
    "3Bw2" : rotate_666_3Bw2,
    "3Dw" : rotate_666_3Dw,
    "3Dw'" : rotate_666_3Dw_prime,
    "3Dw2" : rotate_666_3Dw2,
    "3Fw" : rotate_666_3Fw,
    "3Fw'" : rotate_666_3Fw_prime,
    "3Fw2" : rotate_666_3Fw2,
    "3Lw" : rotate_666_3Lw,
    "3Lw'" : rotate_666_3Lw_prime,
    "3Lw2" : rotate_666_3Lw2,
    "3Rw" : rotate_666_3Rw,
    "3Rw'" : rotate_666_3Rw_prime,
    "3Rw2" : rotate_666_3Rw2,
    "3Uw" : rotate_666_3Uw,
    "3Uw'" : rotate_666_3Uw_prime,
    "3Uw2" : rotate_666_3Uw2,
    "B" : rotate_666_B,
    "B'" : rotate_666_B_prime,
    "B2" : rotate_666_B2,
    "Bw" : rotate_666_Bw,
    "Bw'" : rotate_666_Bw_prime,
    "Bw2" : rotate_666_Bw2,
    "D" : rotate_666_D,
    "D'" : rotate_666_D_prime,
    "D2" : rotate_666_D2,
    "Dw" : rotate_666_Dw,
    "Dw'" : rotate_666_Dw_prime,
    "Dw2" : rotate_666_Dw2,
    "F" : rotate_666_F,
    "F'" : rotate_666_F_prime,
    "F2" : rotate_666_F2,
    "Fw" : rotate_666_Fw,
    "Fw'" : rotate_666_Fw_prime,
    "Fw2" : rotate_666_Fw2,
    "L" : rotate_666_L,
    "L'" : rotate_666_L_prime,
    "L2" : rotate_666_L2,
    "Lw" : rotate_666_Lw,
    "Lw'" : rotate_666_Lw_prime,
    "Lw2" : rotate_666_Lw2,
    "R" : rotate_666_R,
    "R'" : rotate_666_R_prime,
    "R2" : rotate_666_R2,
    "Rw" : rotate_666_Rw,
    "Rw'" : rotate_666_Rw_prime,
    "Rw2" : rotate_666_Rw2,
    "U" : rotate_666_U,
    "U'" : rotate_666_U_prime,
    "U2" : rotate_666_U2,
    "Uw" : rotate_666_Uw,
    "Uw'" : rotate_666_Uw_prime,
    "Uw2" : rotate_666_Uw2,
    "x" : rotate_666_x,
    "x'" : rotate_666_x_prime,
    "y" : rotate_666_y,
    "y'" : rotate_666_y_prime,
    "z" : rotate_666_z,
    "z'" : rotate_666_z_prime,
}

def rotate_666(cube, step):
    return rotate_mapper_666[step](cube)
