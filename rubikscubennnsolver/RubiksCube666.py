
from rubikscubennnsolver import NotSolving
from rubikscubennnsolver.RubiksCubeNNNEvenEdges import RubiksCubeNNNEvenEdges
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666Misc import (
    state_targets_step30,
    state_targets_step31,
    state_targets_step60,
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
import resource
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


inner_x_centers_666 = (
    15, 16, 21, 22,
    51, 52, 57, 58,
    87, 88, 93, 94,
    123, 124, 129, 130,
    159, 160, 165, 166,
    195, 196, 201, 202
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


class LookupTable666UDInnerXCentersStage(LookupTable):
    """
    lookup-table-6x6x6-step10-UD-inner-x-centers-stage.txt
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

    def ida_heuristic(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in inner_x_centers_666])
        return (self.hex_format % int(result, 2), 0)


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
    oblique_edges_666 = (
        9, 10, 14, 17, 20, 23, 27, 28,
        45, 46, 50, 53, 56, 59, 63, 64,
        81, 82, 86, 89, 92, 95, 99, 100,
        117, 118, 122, 125, 128, 131, 135, 136,
        153, 154, 158, 161, 164, 167, 171, 172,
        189, 190, 194, 197, 200, 203, 207, 208
    )

    oblique_edge_pairs_666 = (
        (9, 10), (14, 20), (17, 23), (27, 28),
        (45, 46), (50, 56), (53, 59), (63, 64),
        (81, 82), (86, 92), (89, 95), (99, 100),
        (117, 118), (122, 128), (125, 131), (135, 136),
        (153, 154), (158, 164), (161, 167), (171, 172),
        (189, 190), (194, 200), (197, 203), (207, 208)
    )

    oblique_edge_four_pairs_666 = (
        # Upper
        (9, 27, 189, 207,  82, 100, 153, 171),
        (10, 28, 190, 208,  81, 99, 154, 172),
        (14, 17, 200, 203,  46, 64, 117, 135),
        (20, 23, 194, 197,  45, 63, 118, 136),

        # Left
        (50, 53, 122, 125,  92, 95, 164, 167),
        (56, 59, 128, 131,  86, 89, 158, 161)
    )

    oblique_edge_two_pairs_666 = (
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
    )

    heuristic_stats = {
        (1, 0, 0): 1,
        (1, 1, 0): 1,
        (1, 2, 0): 1,
        (1, 3, 0): 1,
        (2, 0, 0): 1,
        (2, 1, 0): 1,
        (2, 2, 0): 1,
        (2, 2, 1): 1,
        (2, 3, 0): 1,
        (2, 3, 1): 2,
        (2, 4, 0): 1,
        (2, 5, 0): 2,
        (2, 5, 1): 1,
        (2, 6, 0): 2,
        (2, 7, 0): 1,
        (3, 0, 0): 3,
        (3, 1, 0): 2,
        (3, 2, 0): 2,
        (3, 2, 1): 1,
        (3, 3, 0): 2,
        (3, 3, 1): 2,
        (3, 4, 0): 1,
        (3, 5, 0): 2,
        (4, 0, 0): 4,
        (4, 1, 0): 3,
        (4, 2, 0): 3,
        (4, 2, 1): 1,
        (4, 3, 0): 2,
        (4, 3, 1): 2,
        (4, 4, 0): 1,
        (4, 5, 0): 2,
        (4, 5, 1): 3,
        (4, 6, 0): 2,
        (5, 0, 0): 6,
        (5, 1, 0): 5,
        (5, 2, 0): 5,
        (5, 2, 1): 4,
        (5, 3, 0): 4,
        (5, 3, 1): 2,
        (5, 4, 0): 2,
        (5, 5, 0): 4,
        (6, 0, 0): 6,
        (6, 1, 0): 6,
        (6, 2, 0): 6,
        (6, 2, 1): 3,
        (6, 3, 0): 5,
        (6, 3, 1): 2,
        (6, 4, 0): 5,
        (6, 5, 0): 5,
        (7, 0, 0): 6,
        (7, 1, 0): 6,
        (7, 2, 0): 6,
        (7, 2, 1): 2,
        (7, 3, 0): 6,
        (7, 4, 0): 5,
        (7, 5, 0): 5,
        (7, 6, 0): 4,
        (8, 0, 0): 6,
        (8, 1, 0): 6,
        (8, 2, 0): 5,
        (8, 2, 1): 3,
        (8, 3, 0): 5,
        (8, 4, 0): 5,
        (8, 5, 0): 5,
    }
    # uncomment to test step20 without heuristic_stats
    #heuristic_stats = {}

    def __init__(self, parent):
        if parent.min_memory:
            filename = 'lookup-table-6x6x6-step20-UD-oblique-edges-stage.txt.1-deep'
            linecount = 4171103
            max_depth = 1
            filesize = 75079854
            exit_asap = True
        else:
            filename = 'lookup-table-6x6x6-step20-UD-oblique-edges-stage.txt'
            linecount = 59219239
            max_depth = 2
            filesize = 1065946302
            #exit_asap = False
            exit_asap = True

        LookupTableIDA.__init__(
            self,
            parent,
            filename,
            'TBD',
            moves_666,

            # illegal_moves
            ("3Fw", "3Fw'",
             "3Bw", "3Bw'",
             "3Lw", "3Lw'",
             "3Rw", "3Rw'"),

            # prune tables
            (),
            linecount=linecount,
            max_depth=max_depth,
            filesize=filesize,
            exit_asap=exit_asap,
        )

    def recolor(self):
        log.info("%s: recolor (custom)" % self)
        #self.parent.print_cube()
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_666:
            if x in self.oblique_edges_666:
                if self.parent.state[x] == 'U' or self.parent.state[x] == 'D':
                    self.parent.state[x] = 'U'
                else:
                    self.parent.state[x] = 'x'
            else:
                self.parent.state[x] = '.'

        #self.parent.print_cube()

    def get_UD_unpaired_obliques_count(self):
        parent_state = self.parent.state
        UD_paired_obliques = 0

        for (x, y) in self.oblique_edge_pairs_666:
            if parent_state[x] == 'U' and parent_state[y] == 'U':
                UD_paired_obliques += 1

        UD_unpaired_obliques = 8 - UD_paired_obliques
        return UD_unpaired_obliques

    def get_UD_obliques_four_pair_setup_count(self):
        parent_state = self.parent.state
        result = 0

        for xy in self.oblique_edge_four_pairs_666:
            for index in xy:
                if parent_state[index] != 'U':
                    break
            else:
                #log.info("four count at %s" % pformat(xy))
                result += 1
        return result

    def get_UD_obliques_two_pair_setup_count(self):
        parent_state = self.parent.state
        result = 0

        for xy in self.oblique_edge_two_pairs_666:
            for index in xy:
                if parent_state[index] != 'U':
                    break
            else:
                result += 1
                #log.info("two count at %s" % pformat(xy))

        return result

    def ida_heuristic(self):
        parent_state = self.parent.state
        lt_state = 0

        for x in self.oblique_edges_666:
            if parent_state[x] == 'U':
                lt_state = lt_state | 0x1
            lt_state = lt_state << 1
        lt_state = lt_state >> 1
        lt_state = self.hex_format % lt_state

        UD_unpaired_obliques = self.get_UD_unpaired_obliques_count()

        if not UD_unpaired_obliques:
            # 0 is the cost_to_goal
            return (lt_state, 0)

        # Used to build UD_unpaired_obliques_heuristic_666
        #return (lt_state, math.ceil(UD_unpaired_obliques/4))

        two_count = self.get_UD_obliques_two_pair_setup_count()
        four_count = self.get_UD_obliques_four_pair_setup_count()
        state_tuple = (UD_unpaired_obliques, two_count, four_count)
        cost_to_goal = self.heuristic_stats.get(state_tuple)

        if cost_to_goal is None:
            #log.warning("UD_unpaired_obliques_heuristic_666 needs entry for %s" % pformat(state_tuple))
            cost_to_goal = math.ceil(UD_unpaired_obliques/4)

        return (lt_state, cost_to_goal)

    def search_complete(self, state, steps_to_here):
        """
        Used to build UD_unpaired_obliques_heuristic_666
        """
        (lt_state, cost_to_goal) = self.ida_heuristic()

        if cost_to_goal == 0:
            steps = None
        else:
            steps = self.steps(lt_state)

        if cost_to_goal == 0 or steps:

            if steps is None:
                steps = []

            # rotate_xxx() is very fast but it does not append the
            # steps to the solution so put the cube back in original state
            # and execute the steps via a normal rotate() call
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]
            steps_to_go = len(steps_to_here) + len(steps)

            for step in steps_to_here + steps:

                #UD_unpaired_obliques = self.get_UD_unpaired_obliques_count()
                #four_count = self.get_UD_obliques_four_pair_setup_count()
                #two_count = self.get_UD_obliques_two_pair_setup_count()
                #two_count -= four_count * 2 # so as to not double count these
                #state_tuple = (UD_unpaired_obliques, two_count, four_count)

                #if state_tuple not in self.parent.heuristic_stats:
                #    self.parent.heuristic_stats[state_tuple] = []
                #self.parent.heuristic_stats[state_tuple].append(steps_to_go)

                self.parent.rotate(step)
                steps_to_go -= 1

            (lt_state, cost_to_goal) = self.ida_heuristic()
            while cost_to_goal > 0:
                steps = self.steps(lt_state)

                if steps:
                    for step in steps:
                        self.parent.rotate(step)

                (lt_state, cost_to_goal) = self.ida_heuristic()

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
            bucketcount=165636907,
            filesize=165636908)

        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step31-LR-oblique-edges-stage.txt',
            state_targets_step31,
            linecount=165636900,
            max_depth=7)
        '''


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


class LookupTableIDA666LRInnerXCenterAndObliqueEdgesStage(LookupTableIDA):
    """
    lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt
    ====================================================================
    1 steps has 140,504 entries (0 percent, 0.00x previous step)
    2 steps has 1,525,128 entries (7 percent, 10.85x previous step)
    3 steps has 18,193,324 entries (91 percent, 11.93x previous step)

    Total: 19,858,956 entries
    """
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

    LFRB_inner_x_centers_666 = (
        51, 52, 57, 58,
        87, 88, 93, 94,
        123, 124, 129, 130,
        159, 160, 165, 166,
    )

    set_LFRB_inner_x_centers_666 = set(LFRB_inner_x_centers_666)

    def __init__(self, parent):

        if parent.min_memory:
            filename = 'lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt.2-deep'
            linecount = 1665632
            max_depth = 2
            filesize = 29981376
        else:
            filename = 'lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt'
            linecount = 19858956
            max_depth = 3
            filesize = 357461208

        LookupTableIDA.__init__(
            self,
            parent,
            filename,
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

            linecount=linecount,
            max_depth=max_depth,
            filesize=filesize),

    def recolor(self):
        log.info("%s: recolor (custom)" % self)
        #self.parent.print_cube()
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_666:
            if x in self.LFRB_inner_x_centers_oblique_edges_666:
                if self.parent.state[x] == 'L' or self.parent.state[x] == 'R':
                    self.parent.state[x] = 'L'
                else:
                    self.parent.state[x] = 'x'
            else:
                self.parent.state[x] = '.'

        #self.parent.print_cube()

    def ida_heuristic(self):
        parent_state = self.parent.state
        centers_state = 0
        edges_state = 0
        lt_state = 0

        set_LFRB_inner_x_centers_666 = self.set_LFRB_inner_x_centers_666

        for x in self.LFRB_inner_x_centers_oblique_edges_666:
            x_state = parent_state[x]

            if x in set_LFRB_inner_x_centers_666:
                if x_state == 'L':
                    centers_state = centers_state | 0x1
                    lt_state = lt_state | 0x1
                centers_state = centers_state << 1
            else:
                if x_state == 'L':
                    edges_state = edges_state | 0x1
                    lt_state = lt_state | 0x1
                edges_state = edges_state << 1

            lt_state = lt_state << 1

        centers_state = centers_state >> 1
        edges_state = edges_state >> 1
        lt_state = lt_state >> 1

        edges_state = self.parent.lt_LR_oblique_edges_stage.hex_format % edges_state

        cost_to_goal = max(
            self.parent.lt_LR_oblique_edges_stage.heuristic(edges_state),
            self.parent.lt_LR_inner_x_centers_stage.heuristic(centers_state),
        )

        lt_state = self.hex_format % lt_state
        #log.info("%s: lt_state %s, centers_state %s, edges_state %s, cost_to_goal %s" % (self, lt_state, centers_state, edges_state, cost_to_goal))
        return (lt_state, cost_to_goal)


class LookupTable666UDInnerXCenterAndObliqueEdges(LookupTable):
    """
    This will solve the UD inner x-centers and pair the UD oblique edges.

    lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
    1 steps has 210 entries (0 percent, 0.00x previous step)
    2 steps has 924 entries (0 percent, 4.40x previous step)
    3 steps has 4,148 entries (1 percent, 4.49x previous step)
    4 steps has 19,330 entries (5 percent, 4.66x previous step)
    5 steps has 70,702 entries (20 percent, 3.66x previous step)
    6 steps has 134,068 entries (39 percent, 1.90x previous step)
    7 steps has 98,376 entries (28 percent, 0.73x previous step)
    8 steps has 15,218 entries (4 percent, 0.15x previous step)
    9 steps has 24 entries (0 percent, 0.00x previous step)

    Total: 343,000 entries
    Average: 6.01 moves

    We could chop all but the first step on this table but this is one that
    we do not load into memory and it is only 15M so we will keep all of the
    steps.
    """

    UD_inner_x_centers_and_oblique_edges = (
        # Upper
             9, 10,
        14, 15, 16, 17,
        20, 21, 22, 23,
            27, 28,

        # Down
             189, 190,
        194, 195, 196, 197,
        200, 201, 202, 203,
             207, 208,
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt',
            ('198e67', '19b267', '19bc47', '19be23', '19be64', '1dc267', '1dcc47', '1dce23',
             '1dce64', '1df047', '1df223', '1df264', '1dfc03', '1dfc44', '1dfe20', '3b8267',
             '3b8c47', '3b8e23', '3b8e64', '3bb047', '3bb223', '3bb264', '3bbc03', '3bbc44',
             '3bbe20', '3fc047', '3fc223', '3fc264', '3fcc03', '3fcc44', '3fce20', '3ff003',
             '3ff044', '3ff220', '3ffc00', 'd98267', 'd98c47', 'd98e23', 'd98e64', 'd9b047',
             'd9b223', 'd9b264', 'd9bc03', 'd9bc44', 'd9be20', 'ddc047', 'ddc223', 'ddc264',
             'ddcc03', 'ddcc44', 'ddce20', 'ddf003', 'ddf044', 'ddf220', 'ddfc00', 'fb8047',
             'fb8223', 'fb8264', 'fb8c03', 'fb8c44', 'fb8e20', 'fbb003', 'fbb044', 'fbb220',
             'fbbc00', 'ffc003', 'ffc044', 'ffc220', 'ffcc00', 'fff000'),
            linecount=343000,
            max_depth=9,
            filesize=15435000,
        )

    def ida_heuristic(self):
        parent_state = self.parent.state
        lt_state = 0

        for x in self.UD_inner_x_centers_and_oblique_edges:
            if parent_state[x] == 'U':
                lt_state = lt_state | 0x1
            lt_state = lt_state << 1

        lt_state = lt_state >> 1
        lt_state = self.hex_format % lt_state
        return (lt_state, 0)


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
            ('198e67', '19b267', '19bc47', '19be23', '19be64', '1dc267', '1dcc47', '1dce23',
             '1dce64', '1df047', '1df223', '1df264', '1dfc03', '1dfc44', '1dfe20', '3b8267',
             '3b8c47', '3b8e23', '3b8e64', '3bb047', '3bb223', '3bb264', '3bbc03', '3bbc44',
             '3bbe20', '3fc047', '3fc223', '3fc264', '3fcc03', '3fcc44', '3fce20', '3ff003',
             '3ff044', '3ff220', '3ffc00', 'd98267', 'd98c47', 'd98e23', 'd98e64', 'd9b047',
             'd9b223', 'd9b264', 'd9bc03', 'd9bc44', 'd9be20', 'ddc047', 'ddc223', 'ddc264',
             'ddcc03', 'ddcc44', 'ddce20', 'ddf003', 'ddf044', 'ddf220', 'ddfc00', 'fb8047',
             'fb8223', 'fb8264', 'fb8c03', 'fb8c44', 'fb8e20', 'fbb003', 'fbb044', 'fbb220',
             'fbbc00', 'ffc003', 'ffc044', 'ffc220', 'ffcc00', 'fff000'),
            linecount=343000,
            max_depth=10,
            filesize=3430000)


class LookupTable666FBInnerXCenterAndObliqueEdges(LookupTable666LRInnerXCenterAndObliqueEdges):
    """
    lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
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
            'lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt',
            ('198e67', '19b267', '19bc47', '19be23', '19be64', '1dc267', '1dcc47', '1dce23',
             '1dce64', '1df047', '1df223', '1df264', '1dfc03', '1dfc44', '1dfe20', '3b8267',
             '3b8c47', '3b8e23', '3b8e64', '3bb047', '3bb223', '3bb264', '3bbc03', '3bbc44',
             '3bbe20', '3fc047', '3fc223', '3fc264', '3fcc03', '3fcc44', '3fce20', '3ff003',
             '3ff044', '3ff220', '3ffc00', 'd98267', 'd98c47', 'd98e23', 'd98e64', 'd9b047',
             'd9b223', 'd9b264', 'd9bc03', 'd9bc44', 'd9be20', 'ddc047', 'ddc223', 'ddc264',
             'ddcc03', 'ddcc44', 'ddce20', 'ddf003', 'ddf044', 'ddf220', 'ddfc00', 'fb8047',
             'fb8223', 'fb8264', 'fb8c03', 'fb8c44', 'fb8e20', 'fbb003', 'fbb044', 'fbb220',
             'fbbc00', 'ffc003', 'ffc044', 'ffc220', 'ffcc00', 'fff000'),
            linecount=343000,
            max_depth=10,
            filesize=3430000)


class LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(LookupTableIDA):
    """
    lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt
    ==========================================================================
    1 steps has 9,800 entries (0 percent, 0.00x previous step)
    2 steps has 74,480 entries (1 percent, 7.60x previous step)
    3 steps has 645,960 entries (12 percent, 8.67x previous step)
    4 steps has 4,589,992 entries (86 percent, 7.11x previous step)

    Total: 5,320,232 entries
    """
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

    set_step61_centers_666 = set(step61_centers_666)
    set_step62_centers_666 = set(step62_centers_666)

    def __init__(self, parent):
        # LBBFDRLUDDDRUUUUDFFUUUDBRDDDUDDBDLULFFURBUFLLRLRDLRRLDURLRRFDRRLRRDFBBUBRLBUBDUFFBFDLBFFFRUBBBFLLBFBFLLRBDDRUBLFBFRUUUUUDUDDUDRUDDULBDDDDRULURLLDURDUBDLLRLFLLLLRFFRLRLRBRLRRURDFLDFFRURLBFFFFBLRBFBFDLBBFBUFBFBBUUFBBFB
        if parent.min_memory:
            # 3-deep
            filename = 'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.3-deep'
            linecount = 730240
            max_depth = 3
            filesize = 13144320

        else:
            # 4-deep
            filename = 'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt'
            linecount = 5320232
            max_depth = 4
            filesize = 95764176

        LookupTableIDA.__init__(
            self,
            parent,
            filename,
            state_targets_step60,

            moves_666,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
             "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
             "3Rw2", "3Lw2", "3Fw2", "3Bw2",                                                           # do not mess up solved UD
             "3Lw", "3Lw'", "3Lw2",        # can skip these for 6x6x6 cubes
             "3Dw", "3Dw'", "3Dw2",
             "3Bw", "3Bw'", "3Bw2"),

            # prune tables
            (parent.lt_LR_solve_inner_x_centers_and_oblique_edges,
             parent.lt_FB_solve_inner_x_centers_and_oblique_edges,
            ),

            linecount=linecount,
            max_depth=max_depth,
            filesize=filesize,
        )

    def recolor(self):
        log.info("%s: recolor (custom)" % self)
        #self.parent.print_cube()
        self.parent.nuke_corners()
        self.parent.nuke_edges()

        for x in centers_666:
            if x in self.set_step61_centers_666:
                if self.parent.state[x] == 'R':
                    self.parent.state[x] = 'x'

            elif x in self.set_step62_centers_666:
                if self.parent.state[x] == 'B':
                    self.parent.state[x] = 'x'
            else:
                self.parent.state[x] = '.'

        #self.parent.print_cube()

    def ida_heuristic(self):
        parent = self.parent
        parent_state = self.parent.state
        set_step61_centers_666 = self.set_step61_centers_666
        set_step62_centers_666 = self.set_step62_centers_666

        lt_state = 0
        step61_state = 0
        step62_state = 0

        for x in self.step60_centers_666:
            x_state = parent_state[x]

            if x in set_step61_centers_666:

                if x_state == 'L':
                    step61_state = step61_state | 0x1
                    lt_state = lt_state | 0x1

                step61_state = step61_state << 1

            elif x in set_step62_centers_666:

                if x_state == 'F':
                    step62_state = step62_state | 0x1
                    lt_state = lt_state | 0x1

                step62_state = step62_state << 1

            lt_state = lt_state << 1

        lt_state = lt_state >> 1
        step61_state = step61_state >> 1
        step62_state = step62_state >> 1

        step61_state = parent.lt_LR_solve_inner_x_centers_and_oblique_edges.hex_format % step61_state
        step62_state = parent.lt_FB_solve_inner_x_centers_and_oblique_edges.hex_format % step62_state
        lt_state = self.hex_format % lt_state

        cost_to_goal = max(
            parent.lt_LR_solve_inner_x_centers_and_oblique_edges.heuristic(step61_state),
            parent.lt_FB_solve_inner_x_centers_and_oblique_edges.heuristic(step62_state),
        )

        return (lt_state, cost_to_goal)


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
            self.fake_444.enable_print_cube = False
        else:
            self.fake_444.re_init()
        return self.fake_444

    def get_fake_555(self):
        if self.fake_555 is None:
            self.fake_555 = RubiksCube555(solved_555, 'URFDLB')
            self.fake_555.lt_init()
            self.fake_555.enable_print_cube = False
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
        self.lt_UD_oblique_edge_stage.preload_cache_string()

        self.lt_LR_oblique_edges_stage = LookupTable666LRObliqueEdgesStage(self)
        self.lt_LR_inner_x_centers_stage = LookupTable666LRInnerXCentersStage(self)
        self.lt_LR_inner_x_centers_and_oblique_edges_stage = LookupTableIDA666LRInnerXCenterAndObliqueEdgesStage(self)
        self.lt_LR_inner_x_centers_and_oblique_edges_stage.preload_cache_string()

        self.lt_UD_solve_inner_x_centers_and_oblique_edges = LookupTable666UDInnerXCenterAndObliqueEdges(self)

        self.lt_LR_solve_inner_x_centers_and_oblique_edges = LookupTable666LRInnerXCenterAndObliqueEdges(self)
        self.lt_FB_solve_inner_x_centers_and_oblique_edges = LookupTable666FBInnerXCenterAndObliqueEdges(self)
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges = LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(self)
        self.lt_LR_solve_inner_x_centers_and_oblique_edges.preload_cache_dict()
        self.lt_FB_solve_inner_x_centers_and_oblique_edges.preload_cache_dict()
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.preload_cache_string()
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

    def group_centers_guts(self, oblique_edges_only=False):
        self.lt_init()
        self.lt_UD_inner_x_centers_stage.solve()
        self.rotate_for_best_centers_staging(inner_x_centers_666)
        self.print_cube()
        log.info("%s: UD inner-x-centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.lt_UD_oblique_edge_stage.solve()
        self.print_cube()
        log.info("%s: UD oblique edges paired (not staged), %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        #self.print_cube()
        #log.info("%s: UD oblique edges paired (not staged), %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #raise NotSolving("Building UD_unpaired_obliques_heuristic_666")

        # Stage UD centers via 555
        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()

        if oblique_edges_only:
            fake_555.lt_UD_T_centers_stage.solve()
        else:
            fake_555.group_centers_stage_UD()

        for step in fake_555.solution:
            self.rotate(step)

        self.rotate_for_best_centers_staging(inner_x_centers_666)
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
        self.rotate_for_best_centers_staging(inner_x_centers_666)
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
        log.info("kociemba: %s" % self.get_kociemba_string(True))
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

        if oblique_edges_only:
            self.solve_reduced_555_t_centers()
            self.print_cube()
            log.info("%s: solved T-centers, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("\n\n\n\n\n")
        else:
            self.solve_reduced_555_centers()
            self.print_cube()
            log.info("%s: centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("\n\n\n\n\n")


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

swaps_666 = {'3Bw': (0, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 6, 12, 18, 40, 41, 42, 5, 11, 17, 46, 47, 48, 4, 10, 16, 52, 53, 54, 3, 9, 15, 58, 59, 60, 2, 8, 14, 64, 65, 66, 1, 7, 13, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 204, 210, 216, 115, 116, 117, 203, 209, 215, 121, 122, 123, 202, 208, 214, 127, 128, 129, 201, 207, 213, 133, 134, 135, 200, 206, 212, 139, 140, 141, 199, 205, 211, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67),
 "3Bw'": (0, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 211, 205, 199, 40, 41, 42, 212, 206, 200, 46, 47, 48, 213, 207, 201, 52, 53, 54, 214, 208, 202, 58, 59, 60, 215, 209, 203, 64, 65, 66, 216, 210, 204, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 13, 7, 1, 115, 116, 117, 14, 8, 2, 121, 122, 123, 15, 9, 3, 127, 128, 129, 16, 10, 4, 133, 134, 135, 17, 11, 5, 139, 140, 141, 18, 12, 6, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114),
 '3Bw2': (0, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 144, 143, 142, 40, 41, 42, 138, 137, 136, 46, 47, 48, 132, 131, 130, 52, 53, 54, 126, 125, 124, 58, 59, 60, 120, 119, 118, 64, 65, 66, 114, 113, 112, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 69, 68, 67, 115, 116, 117, 63, 62, 61, 121, 122, 123, 57, 56, 55, 127, 128, 129, 51, 50, 49, 133, 134, 135, 45, 44, 43, 139, 140, 141, 39, 38, 37, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1),
 '3Dw': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186),
 "3Dw'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211),
 '3Dw2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181),
 '3Fw': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 37, 38, 39, 193, 187, 181, 43, 44, 45, 194, 188, 182, 49, 50, 51, 195, 189, 183, 55, 56, 57, 196, 190, 184, 61, 62, 63, 197, 191, 185, 67, 68, 69, 198, 192, 186, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78, 31, 25, 19, 112, 113, 114, 32, 26, 20, 118, 119, 120, 33, 27, 21, 124, 125, 126, 34, 28, 22, 130, 131, 132, 35, 29, 23, 136, 137, 138, 36, 30, 24, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 "3Fw'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 37, 38, 39, 24, 30, 36, 43, 44, 45, 23, 29, 35, 49, 50, 51, 22, 28, 34, 55, 56, 57, 21, 27, 33, 61, 62, 63, 20, 26, 32, 67, 68, 69, 19, 25, 31, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103, 186, 192, 198, 112, 113, 114, 185, 191, 197, 118, 119, 120, 184, 190, 196, 124, 125, 126, 183, 189, 195, 130, 131, 132, 182, 188, 194, 136, 137, 138, 181, 187, 193, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 '3Fw2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 37, 38, 39, 141, 140, 139, 43, 44, 45, 135, 134, 133, 49, 50, 51, 129, 128, 127, 55, 56, 57, 123, 122, 121, 61, 62, 63, 117, 116, 115, 67, 68, 69, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 112, 113, 114, 66, 65, 64, 118, 119, 120, 60, 59, 58, 124, 125, 126, 54, 53, 52, 130, 131, 132, 48, 47, 46, 136, 137, 138, 42, 41, 40, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 '3Lw': (0, 180, 179, 178, 4, 5, 6, 174, 173, 172, 10, 11, 12, 168, 167, 166, 16, 17, 18, 162, 161, 160, 22, 23, 24, 156, 155, 154, 28, 29, 30, 150, 149, 148, 34, 35, 36, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 1, 2, 3, 76, 77, 78, 7, 8, 9, 82, 83, 84, 13, 14, 15, 88, 89, 90, 19, 20, 21, 94, 95, 96, 25, 26, 27, 100, 101, 102, 31, 32, 33, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 213, 212, 211, 151, 152, 153, 207, 206, 205, 157, 158, 159, 201, 200, 199, 163, 164, 165, 195, 194, 193, 169, 170, 171, 189, 188, 187, 175, 176, 177, 183, 182, 181, 73, 74, 75, 184, 185, 186, 79, 80, 81, 190, 191, 192, 85, 86, 87, 196, 197, 198, 91, 92, 93, 202, 203, 204, 97, 98, 99, 208, 209, 210, 103, 104, 105, 214, 215, 216),
 "3Lw'": (0, 73, 74, 75, 4, 5, 6, 79, 80, 81, 10, 11, 12, 85, 86, 87, 16, 17, 18, 91, 92, 93, 22, 23, 24, 97, 98, 99, 28, 29, 30, 103, 104, 105, 34, 35, 36, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67, 181, 182, 183, 76, 77, 78, 187, 188, 189, 82, 83, 84, 193, 194, 195, 88, 89, 90, 199, 200, 201, 94, 95, 96, 205, 206, 207, 100, 101, 102, 211, 212, 213, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 33, 32, 31, 151, 152, 153, 27, 26, 25, 157, 158, 159, 21, 20, 19, 163, 164, 165, 15, 14, 13, 169, 170, 171, 9, 8, 7, 175, 176, 177, 3, 2, 1, 180, 179, 178, 184, 185, 186, 174, 173, 172, 190, 191, 192, 168, 167, 166, 196, 197, 198, 162, 161, 160, 202, 203, 204, 156, 155, 154, 208, 209, 210, 150, 149, 148, 214, 215, 216),
 '3Lw2': (0, 181, 182, 183, 4, 5, 6, 187, 188, 189, 10, 11, 12, 193, 194, 195, 16, 17, 18, 199, 200, 201, 22, 23, 24, 205, 206, 207, 28, 29, 30, 211, 212, 213, 34, 35, 36, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 180, 179, 178, 76, 77, 78, 174, 173, 172, 82, 83, 84, 168, 167, 166, 88, 89, 90, 162, 161, 160, 94, 95, 96, 156, 155, 154, 100, 101, 102, 150, 149, 148, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 105, 104, 103, 151, 152, 153, 99, 98, 97, 157, 158, 159, 93, 92, 91, 163, 164, 165, 87, 86, 85, 169, 170, 171, 81, 80, 79, 175, 176, 177, 75, 74, 73, 1, 2, 3, 184, 185, 186, 7, 8, 9, 190, 191, 192, 13, 14, 15, 196, 197, 198, 19, 20, 21, 202, 203, 204, 25, 26, 27, 208, 209, 210, 31, 32, 33, 214, 215, 216),
 '3Rw': (0, 1, 2, 3, 76, 77, 78, 7, 8, 9, 82, 83, 84, 13, 14, 15, 88, 89, 90, 19, 20, 21, 94, 95, 96, 25, 26, 27, 100, 101, 102, 31, 32, 33, 106, 107, 108, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 184, 185, 186, 79, 80, 81, 190, 191, 192, 85, 86, 87, 196, 197, 198, 91, 92, 93, 202, 203, 204, 97, 98, 99, 208, 209, 210, 103, 104, 105, 214, 215, 216, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114, 36, 35, 34, 148, 149, 150, 30, 29, 28, 154, 155, 156, 24, 23, 22, 160, 161, 162, 18, 17, 16, 166, 167, 168, 12, 11, 10, 172, 173, 174, 6, 5, 4, 178, 179, 180, 181, 182, 183, 177, 176, 175, 187, 188, 189, 171, 170, 169, 193, 194, 195, 165, 164, 163, 199, 200, 201, 159, 158, 157, 205, 206, 207, 153, 152, 151, 211, 212, 213, 147, 146, 145),
 "3Rw'": (0, 1, 2, 3, 177, 176, 175, 7, 8, 9, 171, 170, 169, 13, 14, 15, 165, 164, 163, 19, 20, 21, 159, 158, 157, 25, 26, 27, 153, 152, 151, 31, 32, 33, 147, 146, 145, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 4, 5, 6, 79, 80, 81, 10, 11, 12, 85, 86, 87, 16, 17, 18, 91, 92, 93, 22, 23, 24, 97, 98, 99, 28, 29, 30, 103, 104, 105, 34, 35, 36, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 216, 215, 214, 148, 149, 150, 210, 209, 208, 154, 155, 156, 204, 203, 202, 160, 161, 162, 198, 197, 196, 166, 167, 168, 192, 191, 190, 172, 173, 174, 186, 185, 184, 178, 179, 180, 181, 182, 183, 76, 77, 78, 187, 188, 189, 82, 83, 84, 193, 194, 195, 88, 89, 90, 199, 200, 201, 94, 95, 96, 205, 206, 207, 100, 101, 102, 211, 212, 213, 106, 107, 108),
 '3Rw2': (0, 1, 2, 3, 184, 185, 186, 7, 8, 9, 190, 191, 192, 13, 14, 15, 196, 197, 198, 19, 20, 21, 202, 203, 204, 25, 26, 27, 208, 209, 210, 31, 32, 33, 214, 215, 216, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 177, 176, 175, 79, 80, 81, 171, 170, 169, 85, 86, 87, 165, 164, 163, 91, 92, 93, 159, 158, 157, 97, 98, 99, 153, 152, 151, 103, 104, 105, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 148, 149, 150, 102, 101, 100, 154, 155, 156, 96, 95, 94, 160, 161, 162, 90, 89, 88, 166, 167, 168, 84, 83, 82, 172, 173, 174, 78, 77, 76, 178, 179, 180, 181, 182, 183, 4, 5, 6, 187, 188, 189, 10, 11, 12, 193, 194, 195, 16, 17, 18, 199, 200, 201, 22, 23, 24, 205, 206, 207, 28, 29, 30, 211, 212, 213, 34, 35, 36),
 '3Uw': (0, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 "3Uw'": (0, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 '3Uw2': (0, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'B': (0, 114, 120, 126, 132, 138, 144, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 6, 38, 39, 40, 41, 42, 5, 44, 45, 46, 47, 48, 4, 50, 51, 52, 53, 54, 3, 56, 57, 58, 59, 60, 2, 62, 63, 64, 65, 66, 1, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 216, 115, 116, 117, 118, 119, 215, 121, 122, 123, 124, 125, 214, 127, 128, 129, 130, 131, 213, 133, 134, 135, 136, 137, 212, 139, 140, 141, 142, 143, 211, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 37, 43, 49, 55, 61, 67),
 "B'": (0, 67, 61, 55, 49, 43, 37, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 211, 38, 39, 40, 41, 42, 212, 44, 45, 46, 47, 48, 213, 50, 51, 52, 53, 54, 214, 56, 57, 58, 59, 60, 215, 62, 63, 64, 65, 66, 216, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 1, 115, 116, 117, 118, 119, 2, 121, 122, 123, 124, 125, 3, 127, 128, 129, 130, 131, 4, 133, 134, 135, 136, 137, 5, 139, 140, 141, 142, 143, 6, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 144, 138, 132, 126, 120, 114),
 'B2': (0, 216, 215, 214, 213, 212, 211, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 144, 38, 39, 40, 41, 42, 138, 44, 45, 46, 47, 48, 132, 50, 51, 52, 53, 54, 126, 56, 57, 58, 59, 60, 120, 62, 63, 64, 65, 66, 114, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 67, 115, 116, 117, 118, 119, 61, 121, 122, 123, 124, 125, 55, 127, 128, 129, 130, 131, 49, 133, 134, 135, 136, 137, 43, 139, 140, 141, 142, 143, 37, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 6, 5, 4, 3, 2, 1),
 'Bw': (0, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 6, 12, 39, 40, 41, 42, 5, 11, 45, 46, 47, 48, 4, 10, 51, 52, 53, 54, 3, 9, 57, 58, 59, 60, 2, 8, 63, 64, 65, 66, 1, 7, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 210, 216, 115, 116, 117, 118, 209, 215, 121, 122, 123, 124, 208, 214, 127, 128, 129, 130, 207, 213, 133, 134, 135, 136, 206, 212, 139, 140, 141, 142, 205, 211, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67),
 "Bw'": (0, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 211, 205, 39, 40, 41, 42, 212, 206, 45, 46, 47, 48, 213, 207, 51, 52, 53, 54, 214, 208, 57, 58, 59, 60, 215, 209, 63, 64, 65, 66, 216, 210, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 7, 1, 115, 116, 117, 118, 8, 2, 121, 122, 123, 124, 9, 3, 127, 128, 129, 130, 10, 4, 133, 134, 135, 136, 11, 5, 139, 140, 141, 142, 12, 6, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114),
 'Bw2': (0, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 144, 143, 39, 40, 41, 42, 138, 137, 45, 46, 47, 48, 132, 131, 51, 52, 53, 54, 126, 125, 57, 58, 59, 60, 120, 119, 63, 64, 65, 66, 114, 113, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 68, 67, 115, 116, 117, 118, 62, 61, 121, 122, 123, 124, 56, 55, 127, 128, 129, 130, 50, 49, 133, 134, 135, 136, 44, 43, 139, 140, 141, 142, 38, 37, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1),
 'D': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 175, 176, 177, 178, 179, 180, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 67, 68, 69, 70, 71, 72, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 103, 104, 105, 106, 107, 108, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 139, 140, 141, 142, 143, 144, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186),
 "D'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 103, 104, 105, 106, 107, 108, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 139, 140, 141, 142, 143, 144, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 175, 176, 177, 178, 179, 180, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 67, 68, 69, 70, 71, 72, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211),
 'D2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 139, 140, 141, 142, 143, 144, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 175, 176, 177, 178, 179, 180, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 67, 68, 69, 70, 71, 72, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 103, 104, 105, 106, 107, 108, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181),
 'Dw': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186),
 "Dw'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211),
 'Dw2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181),
 'F': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 72, 66, 60, 54, 48, 42, 37, 38, 39, 40, 41, 181, 43, 44, 45, 46, 47, 182, 49, 50, 51, 52, 53, 183, 55, 56, 57, 58, 59, 184, 61, 62, 63, 64, 65, 185, 67, 68, 69, 70, 71, 186, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78, 31, 110, 111, 112, 113, 114, 32, 116, 117, 118, 119, 120, 33, 122, 123, 124, 125, 126, 34, 128, 129, 130, 131, 132, 35, 134, 135, 136, 137, 138, 36, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 139, 133, 127, 121, 115, 109, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 "F'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 109, 115, 121, 127, 133, 139, 37, 38, 39, 40, 41, 36, 43, 44, 45, 46, 47, 35, 49, 50, 51, 52, 53, 34, 55, 56, 57, 58, 59, 33, 61, 62, 63, 64, 65, 32, 67, 68, 69, 70, 71, 31, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103, 186, 110, 111, 112, 113, 114, 185, 116, 117, 118, 119, 120, 184, 122, 123, 124, 125, 126, 183, 128, 129, 130, 131, 132, 182, 134, 135, 136, 137, 138, 181, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 42, 48, 54, 60, 66, 72, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'F2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 186, 185, 184, 183, 182, 181, 37, 38, 39, 40, 41, 139, 43, 44, 45, 46, 47, 133, 49, 50, 51, 52, 53, 127, 55, 56, 57, 58, 59, 121, 61, 62, 63, 64, 65, 115, 67, 68, 69, 70, 71, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 110, 111, 112, 113, 114, 66, 116, 117, 118, 119, 120, 60, 122, 123, 124, 125, 126, 54, 128, 129, 130, 131, 132, 48, 134, 135, 136, 137, 138, 42, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 36, 35, 34, 33, 32, 31, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'Fw': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 37, 38, 39, 40, 187, 181, 43, 44, 45, 46, 188, 182, 49, 50, 51, 52, 189, 183, 55, 56, 57, 58, 190, 184, 61, 62, 63, 64, 191, 185, 67, 68, 69, 70, 192, 186, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78, 31, 25, 111, 112, 113, 114, 32, 26, 117, 118, 119, 120, 33, 27, 123, 124, 125, 126, 34, 28, 129, 130, 131, 132, 35, 29, 135, 136, 137, 138, 36, 30, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 "Fw'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 37, 38, 39, 40, 30, 36, 43, 44, 45, 46, 29, 35, 49, 50, 51, 52, 28, 34, 55, 56, 57, 58, 27, 33, 61, 62, 63, 64, 26, 32, 67, 68, 69, 70, 25, 31, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103, 186, 192, 111, 112, 113, 114, 185, 191, 117, 118, 119, 120, 184, 190, 123, 124, 125, 126, 183, 189, 129, 130, 131, 132, 182, 188, 135, 136, 137, 138, 181, 187, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'Fw2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 37, 38, 39, 40, 140, 139, 43, 44, 45, 46, 134, 133, 49, 50, 51, 52, 128, 127, 55, 56, 57, 58, 122, 121, 61, 62, 63, 64, 116, 115, 67, 68, 69, 70, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 111, 112, 113, 114, 66, 65, 117, 118, 119, 120, 60, 59, 123, 124, 125, 126, 54, 53, 129, 130, 131, 132, 48, 47, 135, 136, 137, 138, 42, 41, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'L': (0, 180, 2, 3, 4, 5, 6, 174, 8, 9, 10, 11, 12, 168, 14, 15, 16, 17, 18, 162, 20, 21, 22, 23, 24, 156, 26, 27, 28, 29, 30, 150, 32, 33, 34, 35, 36, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 1, 74, 75, 76, 77, 78, 7, 80, 81, 82, 83, 84, 13, 86, 87, 88, 89, 90, 19, 92, 93, 94, 95, 96, 25, 98, 99, 100, 101, 102, 31, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 211, 151, 152, 153, 154, 155, 205, 157, 158, 159, 160, 161, 199, 163, 164, 165, 166, 167, 193, 169, 170, 171, 172, 173, 187, 175, 176, 177, 178, 179, 181, 73, 182, 183, 184, 185, 186, 79, 188, 189, 190, 191, 192, 85, 194, 195, 196, 197, 198, 91, 200, 201, 202, 203, 204, 97, 206, 207, 208, 209, 210, 103, 212, 213, 214, 215, 216),
 "L'": (0, 73, 2, 3, 4, 5, 6, 79, 8, 9, 10, 11, 12, 85, 14, 15, 16, 17, 18, 91, 20, 21, 22, 23, 24, 97, 26, 27, 28, 29, 30, 103, 32, 33, 34, 35, 36, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67, 181, 74, 75, 76, 77, 78, 187, 80, 81, 82, 83, 84, 193, 86, 87, 88, 89, 90, 199, 92, 93, 94, 95, 96, 205, 98, 99, 100, 101, 102, 211, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 31, 151, 152, 153, 154, 155, 25, 157, 158, 159, 160, 161, 19, 163, 164, 165, 166, 167, 13, 169, 170, 171, 172, 173, 7, 175, 176, 177, 178, 179, 1, 180, 182, 183, 184, 185, 186, 174, 188, 189, 190, 191, 192, 168, 194, 195, 196, 197, 198, 162, 200, 201, 202, 203, 204, 156, 206, 207, 208, 209, 210, 150, 212, 213, 214, 215, 216),
 'L2': (0, 181, 2, 3, 4, 5, 6, 187, 8, 9, 10, 11, 12, 193, 14, 15, 16, 17, 18, 199, 20, 21, 22, 23, 24, 205, 26, 27, 28, 29, 30, 211, 32, 33, 34, 35, 36, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 180, 74, 75, 76, 77, 78, 174, 80, 81, 82, 83, 84, 168, 86, 87, 88, 89, 90, 162, 92, 93, 94, 95, 96, 156, 98, 99, 100, 101, 102, 150, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 103, 151, 152, 153, 154, 155, 97, 157, 158, 159, 160, 161, 91, 163, 164, 165, 166, 167, 85, 169, 170, 171, 172, 173, 79, 175, 176, 177, 178, 179, 73, 1, 182, 183, 184, 185, 186, 7, 188, 189, 190, 191, 192, 13, 194, 195, 196, 197, 198, 19, 200, 201, 202, 203, 204, 25, 206, 207, 208, 209, 210, 31, 212, 213, 214, 215, 216),
 'Lw': (0, 180, 179, 3, 4, 5, 6, 174, 173, 9, 10, 11, 12, 168, 167, 15, 16, 17, 18, 162, 161, 21, 22, 23, 24, 156, 155, 27, 28, 29, 30, 150, 149, 33, 34, 35, 36, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 1, 2, 75, 76, 77, 78, 7, 8, 81, 82, 83, 84, 13, 14, 87, 88, 89, 90, 19, 20, 93, 94, 95, 96, 25, 26, 99, 100, 101, 102, 31, 32, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 212, 211, 151, 152, 153, 154, 206, 205, 157, 158, 159, 160, 200, 199, 163, 164, 165, 166, 194, 193, 169, 170, 171, 172, 188, 187, 175, 176, 177, 178, 182, 181, 73, 74, 183, 184, 185, 186, 79, 80, 189, 190, 191, 192, 85, 86, 195, 196, 197, 198, 91, 92, 201, 202, 203, 204, 97, 98, 207, 208, 209, 210, 103, 104, 213, 214, 215, 216),
 "Lw'": (0, 73, 74, 3, 4, 5, 6, 79, 80, 9, 10, 11, 12, 85, 86, 15, 16, 17, 18, 91, 92, 21, 22, 23, 24, 97, 98, 27, 28, 29, 30, 103, 104, 33, 34, 35, 36, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67, 181, 182, 75, 76, 77, 78, 187, 188, 81, 82, 83, 84, 193, 194, 87, 88, 89, 90, 199, 200, 93, 94, 95, 96, 205, 206, 99, 100, 101, 102, 211, 212, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 32, 31, 151, 152, 153, 154, 26, 25, 157, 158, 159, 160, 20, 19, 163, 164, 165, 166, 14, 13, 169, 170, 171, 172, 8, 7, 175, 176, 177, 178, 2, 1, 180, 179, 183, 184, 185, 186, 174, 173, 189, 190, 191, 192, 168, 167, 195, 196, 197, 198, 162, 161, 201, 202, 203, 204, 156, 155, 207, 208, 209, 210, 150, 149, 213, 214, 215, 216),
 'Lw2': (0, 181, 182, 3, 4, 5, 6, 187, 188, 9, 10, 11, 12, 193, 194, 15, 16, 17, 18, 199, 200, 21, 22, 23, 24, 205, 206, 27, 28, 29, 30, 211, 212, 33, 34, 35, 36, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 180, 179, 75, 76, 77, 78, 174, 173, 81, 82, 83, 84, 168, 167, 87, 88, 89, 90, 162, 161, 93, 94, 95, 96, 156, 155, 99, 100, 101, 102, 150, 149, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 104, 103, 151, 152, 153, 154, 98, 97, 157, 158, 159, 160, 92, 91, 163, 164, 165, 166, 86, 85, 169, 170, 171, 172, 80, 79, 175, 176, 177, 178, 74, 73, 1, 2, 183, 184, 185, 186, 7, 8, 189, 190, 191, 192, 13, 14, 195, 196, 197, 198, 19, 20, 201, 202, 203, 204, 25, 26, 207, 208, 209, 210, 31, 32, 213, 214, 215, 216),
 'R': (0, 1, 2, 3, 4, 5, 78, 7, 8, 9, 10, 11, 84, 13, 14, 15, 16, 17, 90, 19, 20, 21, 22, 23, 96, 25, 26, 27, 28, 29, 102, 31, 32, 33, 34, 35, 108, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 186, 79, 80, 81, 82, 83, 192, 85, 86, 87, 88, 89, 198, 91, 92, 93, 94, 95, 204, 97, 98, 99, 100, 101, 210, 103, 104, 105, 106, 107, 216, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114, 36, 146, 147, 148, 149, 150, 30, 152, 153, 154, 155, 156, 24, 158, 159, 160, 161, 162, 18, 164, 165, 166, 167, 168, 12, 170, 171, 172, 173, 174, 6, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 175, 187, 188, 189, 190, 191, 169, 193, 194, 195, 196, 197, 163, 199, 200, 201, 202, 203, 157, 205, 206, 207, 208, 209, 151, 211, 212, 213, 214, 215, 145),
 "R'": (0, 1, 2, 3, 4, 5, 175, 7, 8, 9, 10, 11, 169, 13, 14, 15, 16, 17, 163, 19, 20, 21, 22, 23, 157, 25, 26, 27, 28, 29, 151, 31, 32, 33, 34, 35, 145, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 6, 79, 80, 81, 82, 83, 12, 85, 86, 87, 88, 89, 18, 91, 92, 93, 94, 95, 24, 97, 98, 99, 100, 101, 30, 103, 104, 105, 106, 107, 36, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 216, 146, 147, 148, 149, 150, 210, 152, 153, 154, 155, 156, 204, 158, 159, 160, 161, 162, 198, 164, 165, 166, 167, 168, 192, 170, 171, 172, 173, 174, 186, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 78, 187, 188, 189, 190, 191, 84, 193, 194, 195, 196, 197, 90, 199, 200, 201, 202, 203, 96, 205, 206, 207, 208, 209, 102, 211, 212, 213, 214, 215, 108),
 'R2': (0, 1, 2, 3, 4, 5, 186, 7, 8, 9, 10, 11, 192, 13, 14, 15, 16, 17, 198, 19, 20, 21, 22, 23, 204, 25, 26, 27, 28, 29, 210, 31, 32, 33, 34, 35, 216, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 175, 79, 80, 81, 82, 83, 169, 85, 86, 87, 88, 89, 163, 91, 92, 93, 94, 95, 157, 97, 98, 99, 100, 101, 151, 103, 104, 105, 106, 107, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 146, 147, 148, 149, 150, 102, 152, 153, 154, 155, 156, 96, 158, 159, 160, 161, 162, 90, 164, 165, 166, 167, 168, 84, 170, 171, 172, 173, 174, 78, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 6, 187, 188, 189, 190, 191, 12, 193, 194, 195, 196, 197, 18, 199, 200, 201, 202, 203, 24, 205, 206, 207, 208, 209, 30, 211, 212, 213, 214, 215, 36),
 'Rw': (0, 1, 2, 3, 4, 77, 78, 7, 8, 9, 10, 83, 84, 13, 14, 15, 16, 89, 90, 19, 20, 21, 22, 95, 96, 25, 26, 27, 28, 101, 102, 31, 32, 33, 34, 107, 108, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 185, 186, 79, 80, 81, 82, 191, 192, 85, 86, 87, 88, 197, 198, 91, 92, 93, 94, 203, 204, 97, 98, 99, 100, 209, 210, 103, 104, 105, 106, 215, 216, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114, 36, 35, 147, 148, 149, 150, 30, 29, 153, 154, 155, 156, 24, 23, 159, 160, 161, 162, 18, 17, 165, 166, 167, 168, 12, 11, 171, 172, 173, 174, 6, 5, 177, 178, 179, 180, 181, 182, 183, 184, 176, 175, 187, 188, 189, 190, 170, 169, 193, 194, 195, 196, 164, 163, 199, 200, 201, 202, 158, 157, 205, 206, 207, 208, 152, 151, 211, 212, 213, 214, 146, 145),
 "Rw'": (0, 1, 2, 3, 4, 176, 175, 7, 8, 9, 10, 170, 169, 13, 14, 15, 16, 164, 163, 19, 20, 21, 22, 158, 157, 25, 26, 27, 28, 152, 151, 31, 32, 33, 34, 146, 145, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 5, 6, 79, 80, 81, 82, 11, 12, 85, 86, 87, 88, 17, 18, 91, 92, 93, 94, 23, 24, 97, 98, 99, 100, 29, 30, 103, 104, 105, 106, 35, 36, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 216, 215, 147, 148, 149, 150, 210, 209, 153, 154, 155, 156, 204, 203, 159, 160, 161, 162, 198, 197, 165, 166, 167, 168, 192, 191, 171, 172, 173, 174, 186, 185, 177, 178, 179, 180, 181, 182, 183, 184, 77, 78, 187, 188, 189, 190, 83, 84, 193, 194, 195, 196, 89, 90, 199, 200, 201, 202, 95, 96, 205, 206, 207, 208, 101, 102, 211, 212, 213, 214, 107, 108),
 'Rw2': (0, 1, 2, 3, 4, 185, 186, 7, 8, 9, 10, 191, 192, 13, 14, 15, 16, 197, 198, 19, 20, 21, 22, 203, 204, 25, 26, 27, 28, 209, 210, 31, 32, 33, 34, 215, 216, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 176, 175, 79, 80, 81, 82, 170, 169, 85, 86, 87, 88, 164, 163, 91, 92, 93, 94, 158, 157, 97, 98, 99, 100, 152, 151, 103, 104, 105, 106, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 147, 148, 149, 150, 102, 101, 153, 154, 155, 156, 96, 95, 159, 160, 161, 162, 90, 89, 165, 166, 167, 168, 84, 83, 171, 172, 173, 174, 78, 77, 177, 178, 179, 180, 181, 182, 183, 184, 5, 6, 187, 188, 189, 190, 11, 12, 193, 194, 195, 196, 17, 18, 199, 200, 201, 202, 23, 24, 205, 206, 207, 208, 29, 30, 211, 212, 213, 214, 35, 36),
 'U': (0, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6, 73, 74, 75, 76, 77, 78, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 109, 110, 111, 112, 113, 114, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 145, 146, 147, 148, 149, 150, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 37, 38, 39, 40, 41, 42, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 "U'": (0, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31, 145, 146, 147, 148, 149, 150, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 37, 38, 39, 40, 41, 42, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 73, 74, 75, 76, 77, 78, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 109, 110, 111, 112, 113, 114, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'U2': (0, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 109, 110, 111, 112, 113, 114, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 145, 146, 147, 148, 149, 150, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 37, 38, 39, 40, 41, 42, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 73, 74, 75, 76, 77, 78, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'Uw': (0, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 "Uw'": (0, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'Uw2': (0, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216),
 'x': (0, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145),
 "x'": (0, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108),
 'y': (0, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211),
 "y'": (0, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186),
 'z': (0, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114),
 "z'": (0, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67),
    "x x" : (0, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36),
    "y y" : (0, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181),
    "z z" : (0, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1),
    "x y" : (0, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150),
    "x y'" : (0, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175),
    "x z" : (0, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109),
    "x z'" : (0, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37),
    "x y y" : (0, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180),
    "x z z" : (0, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73),
    "x' y" : (0, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103),
    "x' y'" : (0, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78),
    "x' z" : (0, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144),
    "x' z'" : (0, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72),
    "y x x" : (0, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6),
    "y z z" : (0, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186, 180, 179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31),
    "z x x" : (0, 139, 133, 127, 121, 115, 109, 140, 134, 128, 122, 116, 110, 141, 135, 129, 123, 117, 111, 142, 136, 130, 124, 118, 112, 143, 137, 131, 125, 119, 113, 144, 138, 132, 126, 120, 114, 186, 192, 198, 204, 210, 216, 185, 191, 197, 203, 209, 215, 184, 190, 196, 202, 208, 214, 183, 189, 195, 201, 207, 213, 182, 188, 194, 200, 206, 212, 181, 187, 193, 199, 205, 211, 175, 169, 163, 157, 151, 145, 176, 170, 164, 158, 152, 146, 177, 171, 165, 159, 153, 147, 178, 172, 166, 160, 154, 148, 179, 173, 167, 161, 155, 149, 180, 174, 168, 162, 156, 150, 6, 12, 18, 24, 30, 36, 5, 11, 17, 23, 29, 35, 4, 10, 16, 22, 28, 34, 3, 9, 15, 21, 27, 33, 2, 8, 14, 20, 26, 32, 1, 7, 13, 19, 25, 31, 78, 84, 90, 96, 102, 108, 77, 83, 89, 95, 101, 107, 76, 82, 88, 94, 100, 106, 75, 81, 87, 93, 99, 105, 74, 80, 86, 92, 98, 104, 73, 79, 85, 91, 97, 103, 67, 61, 55, 49, 43, 37, 68, 62, 56, 50, 44, 38, 69, 63, 57, 51, 45, 39, 70, 64, 58, 52, 46, 40, 71, 65, 59, 53, 47, 41, 72, 66, 60, 54, 48, 42),
    "z y y" : (0, 42, 48, 54, 60, 66, 72, 41, 47, 53, 59, 65, 71, 40, 46, 52, 58, 64, 70, 39, 45, 51, 57, 63, 69, 38, 44, 50, 56, 62, 68, 37, 43, 49, 55, 61, 67, 31, 25, 19, 13, 7, 1, 32, 26, 20, 14, 8, 2, 33, 27, 21, 15, 9, 3, 34, 28, 22, 16, 10, 4, 35, 29, 23, 17, 11, 5, 36, 30, 24, 18, 12, 6, 150, 156, 162, 168, 174, 180, 149, 155, 161, 167, 173, 179, 148, 154, 160, 166, 172, 178, 147, 153, 159, 165, 171, 177, 146, 152, 158, 164, 170, 176, 145, 151, 157, 163, 169, 175, 211, 205, 199, 193, 187, 181, 212, 206, 200, 194, 188, 182, 213, 207, 201, 195, 189, 183, 214, 208, 202, 196, 190, 184, 215, 209, 203, 197, 191, 185, 216, 210, 204, 198, 192, 186, 103, 97, 91, 85, 79, 73, 104, 98, 92, 86, 80, 74, 105, 99, 93, 87, 81, 75, 106, 100, 94, 88, 82, 76, 107, 101, 95, 89, 83, 77, 108, 102, 96, 90, 84, 78, 114, 120, 126, 132, 138, 144, 113, 119, 125, 131, 137, 143, 112, 118, 124, 130, 136, 142, 111, 117, 123, 129, 135, 141, 110, 116, 122, 128, 134, 140, 109, 115, 121, 127, 133, 139),
    "reflect-x" : (0, 211, 212, 213, 214, 215, 216, 205, 206, 207, 208, 209, 210, 199, 200, 201, 202, 203, 204, 193, 194, 195, 196, 197, 198, 187, 188, 189, 190, 191, 192, 181, 182, 183, 184, 185, 186, 67, 68, 69, 70, 71, 72, 61, 62, 63, 64, 65, 66, 55, 56, 57, 58, 59, 60, 49, 50, 51, 52, 53, 54, 43, 44, 45, 46, 47, 48, 37, 38, 39, 40, 41, 42, 103, 104, 105, 106, 107, 108, 97, 98, 99, 100, 101, 102, 91, 92, 93, 94, 95, 96, 85, 86, 87, 88, 89, 90, 79, 80, 81, 82, 83, 84, 73, 74, 75, 76, 77, 78, 139, 140, 141, 142, 143, 144, 133, 134, 135, 136, 137, 138, 127, 128, 129, 130, 131, 132, 121, 122, 123, 124, 125, 126, 115, 116, 117, 118, 119, 120, 109, 110, 111, 112, 113, 114, 175, 176, 177, 178, 179, 180, 169, 170, 171, 172, 173, 174, 163, 164, 165, 166, 167, 168, 157, 158, 159, 160, 161, 162, 151, 152, 153, 154, 155, 156, 145, 146, 147, 148, 149, 150, 31, 32, 33, 34, 35, 36, 25, 26, 27, 28, 29, 30, 19, 20, 21, 22, 23, 24, 13, 14, 15, 16, 17, 18, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6),
    "reflect-x x" : (0, 103, 104, 105, 106, 107, 108, 97, 98, 99, 100, 101, 102, 91, 92, 93, 94, 95, 96, 85, 86, 87, 88, 89, 90, 79, 80, 81, 82, 83, 84, 73, 74, 75, 76, 77, 78, 72, 66, 60, 54, 48, 42, 71, 65, 59, 53, 47, 41, 70, 64, 58, 52, 46, 40, 69, 63, 57, 51, 45, 39, 68, 62, 56, 50, 44, 38, 67, 61, 55, 49, 43, 37, 31, 32, 33, 34, 35, 36, 25, 26, 27, 28, 29, 30, 19, 20, 21, 22, 23, 24, 13, 14, 15, 16, 17, 18, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 109, 115, 121, 127, 133, 139, 110, 116, 122, 128, 134, 140, 111, 117, 123, 129, 135, 141, 112, 118, 124, 130, 136, 142, 113, 119, 125, 131, 137, 143, 114, 120, 126, 132, 138, 144, 186, 185, 184, 183, 182, 181, 192, 191, 190, 189, 188, 187, 198, 197, 196, 195, 194, 193, 204, 203, 202, 201, 200, 199, 210, 209, 208, 207, 206, 205, 216, 215, 214, 213, 212, 211, 150, 149, 148, 147, 146, 145, 156, 155, 154, 153, 152, 151, 162, 161, 160, 159, 158, 157, 168, 167, 166, 165, 164, 163, 174, 173, 172, 171, 170, 169, 180, 179, 178, 177, 176, 175),
    "reflect-x x'" : (0, 150, 149, 148, 147, 146, 145, 156, 155, 154, 153, 152, 151, 162, 161, 160, 159, 158, 157, 168, 167, 166, 165, 164, 163, 174, 173, 172, 171, 170, 169, 180, 179, 178, 177, 176, 175, 37, 43, 49, 55, 61, 67, 38, 44, 50, 56, 62, 68, 39, 45, 51, 57, 63, 69, 40, 46, 52, 58, 64, 70, 41, 47, 53, 59, 65, 71, 42, 48, 54, 60, 66, 72, 211, 212, 213, 214, 215, 216, 205, 206, 207, 208, 209, 210, 199, 200, 201, 202, 203, 204, 193, 194, 195, 196, 197, 198, 187, 188, 189, 190, 191, 192, 181, 182, 183, 184, 185, 186, 144, 138, 132, 126, 120, 114, 143, 137, 131, 125, 119, 113, 142, 136, 130, 124, 118, 112, 141, 135, 129, 123, 117, 111, 140, 134, 128, 122, 116, 110, 139, 133, 127, 121, 115, 109, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 18, 17, 16, 15, 14, 13, 24, 23, 22, 21, 20, 19, 30, 29, 28, 27, 26, 25, 36, 35, 34, 33, 32, 31, 103, 104, 105, 106, 107, 108, 97, 98, 99, 100, 101, 102, 91, 92, 93, 94, 95, 96, 85, 86, 87, 88, 89, 90, 79, 80, 81, 82, 83, 84, 73, 74, 75, 76, 77, 78),
    "reflect-x y" : (0, 181, 187, 193, 199, 205, 211, 182, 188, 194, 200, 206, 212, 183, 189, 195, 201, 207, 213, 184, 190, 196, 202, 208, 214, 185, 191, 197, 203, 209, 215, 186, 192, 198, 204, 210, 216, 103, 104, 105, 106, 107, 108, 97, 98, 99, 100, 101, 102, 91, 92, 93, 94, 95, 96, 85, 86, 87, 88, 89, 90, 79, 80, 81, 82, 83, 84, 73, 74, 75, 76, 77, 78, 139, 140, 141, 142, 143, 144, 133, 134, 135, 136, 137, 138, 127, 128, 129, 130, 131, 132, 121, 122, 123, 124, 125, 126, 115, 116, 117, 118, 119, 120, 109, 110, 111, 112, 113, 114, 175, 176, 177, 178, 179, 180, 169, 170, 171, 172, 173, 174, 163, 164, 165, 166, 167, 168, 157, 158, 159, 160, 161, 162, 151, 152, 153, 154, 155, 156, 145, 146, 147, 148, 149, 150, 67, 68, 69, 70, 71, 72, 61, 62, 63, 64, 65, 66, 55, 56, 57, 58, 59, 60, 49, 50, 51, 52, 53, 54, 43, 44, 45, 46, 47, 48, 37, 38, 39, 40, 41, 42, 36, 30, 24, 18, 12, 6, 35, 29, 23, 17, 11, 5, 34, 28, 22, 16, 10, 4, 33, 27, 21, 15, 9, 3, 32, 26, 20, 14, 8, 2, 31, 25, 19, 13, 7, 1),
    "reflect-x y'" : (0, 216, 210, 204, 198, 192, 186, 215, 209, 203, 197, 191, 185, 214, 208, 202, 196, 190, 184, 213, 207, 201, 195, 189, 183, 212, 206, 200, 194, 188, 182, 211, 205, 199, 193, 187, 181, 175, 176, 177, 178, 179, 180, 169, 170, 171, 172, 173, 174, 163, 164, 165, 166, 167, 168, 157, 158, 159, 160, 161, 162, 151, 152, 153, 154, 155, 156, 145, 146, 147, 148, 149, 150, 67, 68, 69, 70, 71, 72, 61, 62, 63, 64, 65, 66, 55, 56, 57, 58, 59, 60, 49, 50, 51, 52, 53, 54, 43, 44, 45, 46, 47, 48, 37, 38, 39, 40, 41, 42, 103, 104, 105, 106, 107, 108, 97, 98, 99, 100, 101, 102, 91, 92, 93, 94, 95, 96, 85, 86, 87, 88, 89, 90, 79, 80, 81, 82, 83, 84, 73, 74, 75, 76, 77, 78, 139, 140, 141, 142, 143, 144, 133, 134, 135, 136, 137, 138, 127, 128, 129, 130, 131, 132, 121, 122, 123, 124, 125, 126, 115, 116, 117, 118, 119, 120, 109, 110, 111, 112, 113, 114, 1, 7, 13, 19, 25, 31, 2, 8, 14, 20, 26, 32, 3, 9, 15, 21, 27, 33, 4, 10, 16, 22, 28, 34, 5, 11, 17, 23, 29, 35, 6, 12, 18, 24, 30, 36),
    "reflect-x z" : (0, 37, 43, 49, 55, 61, 67, 38, 44, 50, 56, 62, 68, 39, 45, 51, 57, 63, 69, 40, 46, 52, 58, 64, 70, 41, 47, 53, 59, 65, 71, 42, 48, 54, 60, 66, 72, 1, 7, 13, 19, 25, 31, 2, 8, 14, 20, 26, 32, 3, 9, 15, 21, 27, 33, 4, 10, 16, 22, 28, 34, 5, 11, 17, 23, 29, 35, 6, 12, 18, 24, 30, 36, 73, 79, 85, 91, 97, 103, 74, 80, 86, 92, 98, 104, 75, 81, 87, 93, 99, 105, 76, 82, 88, 94, 100, 106, 77, 83, 89, 95, 101, 107, 78, 84, 90, 96, 102, 108, 181, 187, 193, 199, 205, 211, 182, 188, 194, 200, 206, 212, 183, 189, 195, 201, 207, 213, 184, 190, 196, 202, 208, 214, 185, 191, 197, 203, 209, 215, 186, 192, 198, 204, 210, 216, 180, 174, 168, 162, 156, 150, 179, 173, 167, 161, 155, 149, 178, 172, 166, 160, 154, 148, 177, 171, 165, 159, 153, 147, 176, 170, 164, 158, 152, 146, 175, 169, 163, 157, 151, 145, 109, 115, 121, 127, 133, 139, 110, 116, 122, 128, 134, 140, 111, 117, 123, 129, 135, 141, 112, 118, 124, 130, 136, 142, 113, 119, 125, 131, 137, 143, 114, 120, 126, 132, 138, 144),
    "reflect-x z'" : (0, 144, 138, 132, 126, 120, 114, 143, 137, 131, 125, 119, 113, 142, 136, 130, 124, 118, 112, 141, 135, 129, 123, 117, 111, 140, 134, 128, 122, 116, 110, 139, 133, 127, 121, 115, 109, 216, 210, 204, 198, 192, 186, 215, 209, 203, 197, 191, 185, 214, 208, 202, 196, 190, 184, 213, 207, 201, 195, 189, 183, 212, 206, 200, 194, 188, 182, 211, 205, 199, 193, 187, 181, 108, 102, 96, 90, 84, 78, 107, 101, 95, 89, 83, 77, 106, 100, 94, 88, 82, 76, 105, 99, 93, 87, 81, 75, 104, 98, 92, 86, 80, 74, 103, 97, 91, 85, 79, 73, 36, 30, 24, 18, 12, 6, 35, 29, 23, 17, 11, 5, 34, 28, 22, 16, 10, 4, 33, 27, 21, 15, 9, 3, 32, 26, 20, 14, 8, 2, 31, 25, 19, 13, 7, 1, 145, 151, 157, 163, 169, 175, 146, 152, 158, 164, 170, 176, 147, 153, 159, 165, 171, 177, 148, 154, 160, 166, 172, 178, 149, 155, 161, 167, 173, 179, 150, 156, 162, 168, 174, 180, 72, 66, 60, 54, 48, 42, 71, 65, 59, 53, 47, 41, 70, 64, 58, 52, 46, 40, 69, 63, 57, 51, 45, 39, 68, 62, 56, 50, 44, 38, 67, 61, 55, 49, 43, 37),
    "reflect-x x x" : (0, 31, 32, 33, 34, 35, 36, 25, 26, 27, 28, 29, 30, 19, 20, 21, 22, 23, 24, 13, 14, 15, 16, 17, 18, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 42, 41, 40, 39, 38, 37, 48, 47, 46, 45, 44, 43, 54, 53, 52, 51, 50, 49, 60, 59, 58, 57, 56, 55, 66, 65, 64, 63, 62, 61, 72, 71, 70, 69, 68, 67, 150, 149, 148, 147, 146, 145, 156, 155, 154, 153, 152, 151, 162, 161, 160, 159, 158, 157, 168, 167, 166, 165, 164, 163, 174, 173, 172, 171, 170, 169, 180, 179, 178, 177, 176, 175, 114, 113, 112, 111, 110, 109, 120, 119, 118, 117, 116, 115, 126, 125, 124, 123, 122, 121, 132, 131, 130, 129, 128, 127, 138, 137, 136, 135, 134, 133, 144, 143, 142, 141, 140, 139, 78, 77, 76, 75, 74, 73, 84, 83, 82, 81, 80, 79, 90, 89, 88, 87, 86, 85, 96, 95, 94, 93, 92, 91, 102, 101, 100, 99, 98, 97, 108, 107, 106, 105, 104, 103, 211, 212, 213, 214, 215, 216, 205, 206, 207, 208, 209, 210, 199, 200, 201, 202, 203, 204, 193, 194, 195, 196, 197, 198, 187, 188, 189, 190, 191, 192, 181, 182, 183, 184, 185, 186),
    "reflect-x y y" : (0, 186, 185, 184, 183, 182, 181, 192, 191, 190, 189, 188, 187, 198, 197, 196, 195, 194, 193, 204, 203, 202, 201, 200, 199, 210, 209, 208, 207, 206, 205, 216, 215, 214, 213, 212, 211, 139, 140, 141, 142, 143, 144, 133, 134, 135, 136, 137, 138, 127, 128, 129, 130, 131, 132, 121, 122, 123, 124, 125, 126, 115, 116, 117, 118, 119, 120, 109, 110, 111, 112, 113, 114, 175, 176, 177, 178, 179, 180, 169, 170, 171, 172, 173, 174, 163, 164, 165, 166, 167, 168, 157, 158, 159, 160, 161, 162, 151, 152, 153, 154, 155, 156, 145, 146, 147, 148, 149, 150, 67, 68, 69, 70, 71, 72, 61, 62, 63, 64, 65, 66, 55, 56, 57, 58, 59, 60, 49, 50, 51, 52, 53, 54, 43, 44, 45, 46, 47, 48, 37, 38, 39, 40, 41, 42, 103, 104, 105, 106, 107, 108, 97, 98, 99, 100, 101, 102, 91, 92, 93, 94, 95, 96, 85, 86, 87, 88, 89, 90, 79, 80, 81, 82, 83, 84, 73, 74, 75, 76, 77, 78, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 18, 17, 16, 15, 14, 13, 24, 23, 22, 21, 20, 19, 30, 29, 28, 27, 26, 25, 36, 35, 34, 33, 32, 31),
    "reflect-x z z" : (0, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 18, 17, 16, 15, 14, 13, 24, 23, 22, 21, 20, 19, 30, 29, 28, 27, 26, 25, 36, 35, 34, 33, 32, 31, 114, 113, 112, 111, 110, 109, 120, 119, 118, 117, 116, 115, 126, 125, 124, 123, 122, 121, 132, 131, 130, 129, 128, 127, 138, 137, 136, 135, 134, 133, 144, 143, 142, 141, 140, 139, 78, 77, 76, 75, 74, 73, 84, 83, 82, 81, 80, 79, 90, 89, 88, 87, 86, 85, 96, 95, 94, 93, 92, 91, 102, 101, 100, 99, 98, 97, 108, 107, 106, 105, 104, 103, 42, 41, 40, 39, 38, 37, 48, 47, 46, 45, 44, 43, 54, 53, 52, 51, 50, 49, 60, 59, 58, 57, 56, 55, 66, 65, 64, 63, 62, 61, 72, 71, 70, 69, 68, 67, 150, 149, 148, 147, 146, 145, 156, 155, 154, 153, 152, 151, 162, 161, 160, 159, 158, 157, 168, 167, 166, 165, 164, 163, 174, 173, 172, 171, 170, 169, 180, 179, 178, 177, 176, 175, 186, 185, 184, 183, 182, 181, 192, 191, 190, 189, 188, 187, 198, 197, 196, 195, 194, 193, 204, 203, 202, 201, 200, 199, 210, 209, 208, 207, 206, 205, 216, 215, 214, 213, 212, 211),
    "reflect-x x y" : (0, 73, 79, 85, 91, 97, 103, 74, 80, 86, 92, 98, 104, 75, 81, 87, 93, 99, 105, 76, 82, 88, 94, 100, 106, 77, 83, 89, 95, 101, 107, 78, 84, 90, 96, 102, 108, 31, 32, 33, 34, 35, 36, 25, 26, 27, 28, 29, 30, 19, 20, 21, 22, 23, 24, 13, 14, 15, 16, 17, 18, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 109, 115, 121, 127, 133, 139, 110, 116, 122, 128, 134, 140, 111, 117, 123, 129, 135, 141, 112, 118, 124, 130, 136, 142, 113, 119, 125, 131, 137, 143, 114, 120, 126, 132, 138, 144, 186, 185, 184, 183, 182, 181, 192, 191, 190, 189, 188, 187, 198, 197, 196, 195, 194, 193, 204, 203, 202, 201, 200, 199, 210, 209, 208, 207, 206, 205, 216, 215, 214, 213, 212, 211, 72, 66, 60, 54, 48, 42, 71, 65, 59, 53, 47, 41, 70, 64, 58, 52, 46, 40, 69, 63, 57, 51, 45, 39, 68, 62, 56, 50, 44, 38, 67, 61, 55, 49, 43, 37, 145, 151, 157, 163, 169, 175, 146, 152, 158, 164, 170, 176, 147, 153, 159, 165, 171, 177, 148, 154, 160, 166, 172, 178, 149, 155, 161, 167, 173, 179, 150, 156, 162, 168, 174, 180),
    "reflect-x x y'" : (0, 108, 102, 96, 90, 84, 78, 107, 101, 95, 89, 83, 77, 106, 100, 94, 88, 82, 76, 105, 99, 93, 87, 81, 75, 104, 98, 92, 86, 80, 74, 103, 97, 91, 85, 79, 73, 186, 185, 184, 183, 182, 181, 192, 191, 190, 189, 188, 187, 198, 197, 196, 195, 194, 193, 204, 203, 202, 201, 200, 199, 210, 209, 208, 207, 206, 205, 216, 215, 214, 213, 212, 211, 72, 66, 60, 54, 48, 42, 71, 65, 59, 53, 47, 41, 70, 64, 58, 52, 46, 40, 69, 63, 57, 51, 45, 39, 68, 62, 56, 50, 44, 38, 67, 61, 55, 49, 43, 37, 31, 32, 33, 34, 35, 36, 25, 26, 27, 28, 29, 30, 19, 20, 21, 22, 23, 24, 13, 14, 15, 16, 17, 18, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 109, 115, 121, 127, 133, 139, 110, 116, 122, 128, 134, 140, 111, 117, 123, 129, 135, 141, 112, 118, 124, 130, 136, 142, 113, 119, 125, 131, 137, 143, 114, 120, 126, 132, 138, 144, 180, 174, 168, 162, 156, 150, 179, 173, 167, 161, 155, 149, 178, 172, 166, 160, 154, 148, 177, 171, 165, 159, 153, 147, 176, 170, 164, 158, 152, 146, 175, 169, 163, 157, 151, 145),
    "reflect-x x z" : (0, 67, 68, 69, 70, 71, 72, 61, 62, 63, 64, 65, 66, 55, 56, 57, 58, 59, 60, 49, 50, 51, 52, 53, 54, 43, 44, 45, 46, 47, 48, 37, 38, 39, 40, 41, 42, 180, 174, 168, 162, 156, 150, 179, 173, 167, 161, 155, 149, 178, 172, 166, 160, 154, 148, 177, 171, 165, 159, 153, 147, 176, 170, 164, 158, 152, 146, 175, 169, 163, 157, 151, 145, 1, 7, 13, 19, 25, 31, 2, 8, 14, 20, 26, 32, 3, 9, 15, 21, 27, 33, 4, 10, 16, 22, 28, 34, 5, 11, 17, 23, 29, 35, 6, 12, 18, 24, 30, 36, 73, 79, 85, 91, 97, 103, 74, 80, 86, 92, 98, 104, 75, 81, 87, 93, 99, 105, 76, 82, 88, 94, 100, 106, 77, 83, 89, 95, 101, 107, 78, 84, 90, 96, 102, 108, 181, 187, 193, 199, 205, 211, 182, 188, 194, 200, 206, 212, 183, 189, 195, 201, 207, 213, 184, 190, 196, 202, 208, 214, 185, 191, 197, 203, 209, 215, 186, 192, 198, 204, 210, 216, 114, 113, 112, 111, 110, 109, 120, 119, 118, 117, 116, 115, 126, 125, 124, 123, 122, 121, 132, 131, 130, 129, 128, 127, 138, 137, 136, 135, 134, 133, 144, 143, 142, 141, 140, 139),
    "reflect-x x z'" : (0, 139, 140, 141, 142, 143, 144, 133, 134, 135, 136, 137, 138, 127, 128, 129, 130, 131, 132, 121, 122, 123, 124, 125, 126, 115, 116, 117, 118, 119, 120, 109, 110, 111, 112, 113, 114, 108, 102, 96, 90, 84, 78, 107, 101, 95, 89, 83, 77, 106, 100, 94, 88, 82, 76, 105, 99, 93, 87, 81, 75, 104, 98, 92, 86, 80, 74, 103, 97, 91, 85, 79, 73, 36, 30, 24, 18, 12, 6, 35, 29, 23, 17, 11, 5, 34, 28, 22, 16, 10, 4, 33, 27, 21, 15, 9, 3, 32, 26, 20, 14, 8, 2, 31, 25, 19, 13, 7, 1, 145, 151, 157, 163, 169, 175, 146, 152, 158, 164, 170, 176, 147, 153, 159, 165, 171, 177, 148, 154, 160, 166, 172, 178, 149, 155, 161, 167, 173, 179, 150, 156, 162, 168, 174, 180, 216, 210, 204, 198, 192, 186, 215, 209, 203, 197, 191, 185, 214, 208, 202, 196, 190, 184, 213, 207, 201, 195, 189, 183, 212, 206, 200, 194, 188, 182, 211, 205, 199, 193, 187, 181, 42, 41, 40, 39, 38, 37, 48, 47, 46, 45, 44, 43, 54, 53, 52, 51, 50, 49, 60, 59, 58, 57, 56, 55, 66, 65, 64, 63, 62, 61, 72, 71, 70, 69, 68, 67),
    "reflect-x x y y" : (0, 78, 77, 76, 75, 74, 73, 84, 83, 82, 81, 80, 79, 90, 89, 88, 87, 86, 85, 96, 95, 94, 93, 92, 91, 102, 101, 100, 99, 98, 97, 108, 107, 106, 105, 104, 103, 109, 115, 121, 127, 133, 139, 110, 116, 122, 128, 134, 140, 111, 117, 123, 129, 135, 141, 112, 118, 124, 130, 136, 142, 113, 119, 125, 131, 137, 143, 114, 120, 126, 132, 138, 144, 186, 185, 184, 183, 182, 181, 192, 191, 190, 189, 188, 187, 198, 197, 196, 195, 194, 193, 204, 203, 202, 201, 200, 199, 210, 209, 208, 207, 206, 205, 216, 215, 214, 213, 212, 211, 72, 66, 60, 54, 48, 42, 71, 65, 59, 53, 47, 41, 70, 64, 58, 52, 46, 40, 69, 63, 57, 51, 45, 39, 68, 62, 56, 50, 44, 38, 67, 61, 55, 49, 43, 37, 31, 32, 33, 34, 35, 36, 25, 26, 27, 28, 29, 30, 19, 20, 21, 22, 23, 24, 13, 14, 15, 16, 17, 18, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 175, 176, 177, 178, 179, 180, 169, 170, 171, 172, 173, 174, 163, 164, 165, 166, 167, 168, 157, 158, 159, 160, 161, 162, 151, 152, 153, 154, 155, 156, 145, 146, 147, 148, 149, 150),
    "reflect-x x z z" : (0, 175, 176, 177, 178, 179, 180, 169, 170, 171, 172, 173, 174, 163, 164, 165, 166, 167, 168, 157, 158, 159, 160, 161, 162, 151, 152, 153, 154, 155, 156, 145, 146, 147, 148, 149, 150, 144, 138, 132, 126, 120, 114, 143, 137, 131, 125, 119, 113, 142, 136, 130, 124, 118, 112, 141, 135, 129, 123, 117, 111, 140, 134, 128, 122, 116, 110, 139, 133, 127, 121, 115, 109, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 18, 17, 16, 15, 14, 13, 24, 23, 22, 21, 20, 19, 30, 29, 28, 27, 26, 25, 36, 35, 34, 33, 32, 31, 37, 43, 49, 55, 61, 67, 38, 44, 50, 56, 62, 68, 39, 45, 51, 57, 63, 69, 40, 46, 52, 58, 64, 70, 41, 47, 53, 59, 65, 71, 42, 48, 54, 60, 66, 72, 211, 212, 213, 214, 215, 216, 205, 206, 207, 208, 209, 210, 199, 200, 201, 202, 203, 204, 193, 194, 195, 196, 197, 198, 187, 188, 189, 190, 191, 192, 181, 182, 183, 184, 185, 186, 78, 77, 76, 75, 74, 73, 84, 83, 82, 81, 80, 79, 90, 89, 88, 87, 86, 85, 96, 95, 94, 93, 92, 91, 102, 101, 100, 99, 98, 97, 108, 107, 106, 105, 104, 103),
    "reflect-x x' y" : (0, 180, 174, 168, 162, 156, 150, 179, 173, 167, 161, 155, 149, 178, 172, 166, 160, 154, 148, 177, 171, 165, 159, 153, 147, 176, 170, 164, 158, 152, 146, 175, 169, 163, 157, 151, 145, 211, 212, 213, 214, 215, 216, 205, 206, 207, 208, 209, 210, 199, 200, 201, 202, 203, 204, 193, 194, 195, 196, 197, 198, 187, 188, 189, 190, 191, 192, 181, 182, 183, 184, 185, 186, 144, 138, 132, 126, 120, 114, 143, 137, 131, 125, 119, 113, 142, 136, 130, 124, 118, 112, 141, 135, 129, 123, 117, 111, 140, 134, 128, 122, 116, 110, 139, 133, 127, 121, 115, 109, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 18, 17, 16, 15, 14, 13, 24, 23, 22, 21, 20, 19, 30, 29, 28, 27, 26, 25, 36, 35, 34, 33, 32, 31, 37, 43, 49, 55, 61, 67, 38, 44, 50, 56, 62, 68, 39, 45, 51, 57, 63, 69, 40, 46, 52, 58, 64, 70, 41, 47, 53, 59, 65, 71, 42, 48, 54, 60, 66, 72, 108, 102, 96, 90, 84, 78, 107, 101, 95, 89, 83, 77, 106, 100, 94, 88, 82, 76, 105, 99, 93, 87, 81, 75, 104, 98, 92, 86, 80, 74, 103, 97, 91, 85, 79, 73),
    "reflect-x x' y'" : (0, 145, 151, 157, 163, 169, 175, 146, 152, 158, 164, 170, 176, 147, 153, 159, 165, 171, 177, 148, 154, 160, 166, 172, 178, 149, 155, 161, 167, 173, 179, 150, 156, 162, 168, 174, 180, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 18, 17, 16, 15, 14, 13, 24, 23, 22, 21, 20, 19, 30, 29, 28, 27, 26, 25, 36, 35, 34, 33, 32, 31, 37, 43, 49, 55, 61, 67, 38, 44, 50, 56, 62, 68, 39, 45, 51, 57, 63, 69, 40, 46, 52, 58, 64, 70, 41, 47, 53, 59, 65, 71, 42, 48, 54, 60, 66, 72, 211, 212, 213, 214, 215, 216, 205, 206, 207, 208, 209, 210, 199, 200, 201, 202, 203, 204, 193, 194, 195, 196, 197, 198, 187, 188, 189, 190, 191, 192, 181, 182, 183, 184, 185, 186, 144, 138, 132, 126, 120, 114, 143, 137, 131, 125, 119, 113, 142, 136, 130, 124, 118, 112, 141, 135, 129, 123, 117, 111, 140, 134, 128, 122, 116, 110, 139, 133, 127, 121, 115, 109, 73, 79, 85, 91, 97, 103, 74, 80, 86, 92, 98, 104, 75, 81, 87, 93, 99, 105, 76, 82, 88, 94, 100, 106, 77, 83, 89, 95, 101, 107, 78, 84, 90, 96, 102, 108),
    "reflect-x x' z" : (0, 42, 41, 40, 39, 38, 37, 48, 47, 46, 45, 44, 43, 54, 53, 52, 51, 50, 49, 60, 59, 58, 57, 56, 55, 66, 65, 64, 63, 62, 61, 72, 71, 70, 69, 68, 67, 73, 79, 85, 91, 97, 103, 74, 80, 86, 92, 98, 104, 75, 81, 87, 93, 99, 105, 76, 82, 88, 94, 100, 106, 77, 83, 89, 95, 101, 107, 78, 84, 90, 96, 102, 108, 181, 187, 193, 199, 205, 211, 182, 188, 194, 200, 206, 212, 183, 189, 195, 201, 207, 213, 184, 190, 196, 202, 208, 214, 185, 191, 197, 203, 209, 215, 186, 192, 198, 204, 210, 216, 180, 174, 168, 162, 156, 150, 179, 173, 167, 161, 155, 149, 178, 172, 166, 160, 154, 148, 177, 171, 165, 159, 153, 147, 176, 170, 164, 158, 152, 146, 175, 169, 163, 157, 151, 145, 1, 7, 13, 19, 25, 31, 2, 8, 14, 20, 26, 32, 3, 9, 15, 21, 27, 33, 4, 10, 16, 22, 28, 34, 5, 11, 17, 23, 29, 35, 6, 12, 18, 24, 30, 36, 139, 140, 141, 142, 143, 144, 133, 134, 135, 136, 137, 138, 127, 128, 129, 130, 131, 132, 121, 122, 123, 124, 125, 126, 115, 116, 117, 118, 119, 120, 109, 110, 111, 112, 113, 114),
    "reflect-x x' z'" : (0, 114, 113, 112, 111, 110, 109, 120, 119, 118, 117, 116, 115, 126, 125, 124, 123, 122, 121, 132, 131, 130, 129, 128, 127, 138, 137, 136, 135, 134, 133, 144, 143, 142, 141, 140, 139, 145, 151, 157, 163, 169, 175, 146, 152, 158, 164, 170, 176, 147, 153, 159, 165, 171, 177, 148, 154, 160, 166, 172, 178, 149, 155, 161, 167, 173, 179, 150, 156, 162, 168, 174, 180, 216, 210, 204, 198, 192, 186, 215, 209, 203, 197, 191, 185, 214, 208, 202, 196, 190, 184, 213, 207, 201, 195, 189, 183, 212, 206, 200, 194, 188, 182, 211, 205, 199, 193, 187, 181, 108, 102, 96, 90, 84, 78, 107, 101, 95, 89, 83, 77, 106, 100, 94, 88, 82, 76, 105, 99, 93, 87, 81, 75, 104, 98, 92, 86, 80, 74, 103, 97, 91, 85, 79, 73, 36, 30, 24, 18, 12, 6, 35, 29, 23, 17, 11, 5, 34, 28, 22, 16, 10, 4, 33, 27, 21, 15, 9, 3, 32, 26, 20, 14, 8, 2, 31, 25, 19, 13, 7, 1, 67, 68, 69, 70, 71, 72, 61, 62, 63, 64, 65, 66, 55, 56, 57, 58, 59, 60, 49, 50, 51, 52, 53, 54, 43, 44, 45, 46, 47, 48, 37, 38, 39, 40, 41, 42),
    "reflect-x y x x" : (0, 36, 30, 24, 18, 12, 6, 35, 29, 23, 17, 11, 5, 34, 28, 22, 16, 10, 4, 33, 27, 21, 15, 9, 3, 32, 26, 20, 14, 8, 2, 31, 25, 19, 13, 7, 1, 78, 77, 76, 75, 74, 73, 84, 83, 82, 81, 80, 79, 90, 89, 88, 87, 86, 85, 96, 95, 94, 93, 92, 91, 102, 101, 100, 99, 98, 97, 108, 107, 106, 105, 104, 103, 42, 41, 40, 39, 38, 37, 48, 47, 46, 45, 44, 43, 54, 53, 52, 51, 50, 49, 60, 59, 58, 57, 56, 55, 66, 65, 64, 63, 62, 61, 72, 71, 70, 69, 68, 67, 150, 149, 148, 147, 146, 145, 156, 155, 154, 153, 152, 151, 162, 161, 160, 159, 158, 157, 168, 167, 166, 165, 164, 163, 174, 173, 172, 171, 170, 169, 180, 179, 178, 177, 176, 175, 114, 113, 112, 111, 110, 109, 120, 119, 118, 117, 116, 115, 126, 125, 124, 123, 122, 121, 132, 131, 130, 129, 128, 127, 138, 137, 136, 135, 134, 133, 144, 143, 142, 141, 140, 139, 181, 187, 193, 199, 205, 211, 182, 188, 194, 200, 206, 212, 183, 189, 195, 201, 207, 213, 184, 190, 196, 202, 208, 214, 185, 191, 197, 203, 209, 215, 186, 192, 198, 204, 210, 216),
    "reflect-x y z z" : (0, 1, 7, 13, 19, 25, 31, 2, 8, 14, 20, 26, 32, 3, 9, 15, 21, 27, 33, 4, 10, 16, 22, 28, 34, 5, 11, 17, 23, 29, 35, 6, 12, 18, 24, 30, 36, 150, 149, 148, 147, 146, 145, 156, 155, 154, 153, 152, 151, 162, 161, 160, 159, 158, 157, 168, 167, 166, 165, 164, 163, 174, 173, 172, 171, 170, 169, 180, 179, 178, 177, 176, 175, 114, 113, 112, 111, 110, 109, 120, 119, 118, 117, 116, 115, 126, 125, 124, 123, 122, 121, 132, 131, 130, 129, 128, 127, 138, 137, 136, 135, 134, 133, 144, 143, 142, 141, 140, 139, 78, 77, 76, 75, 74, 73, 84, 83, 82, 81, 80, 79, 90, 89, 88, 87, 86, 85, 96, 95, 94, 93, 92, 91, 102, 101, 100, 99, 98, 97, 108, 107, 106, 105, 104, 103, 42, 41, 40, 39, 38, 37, 48, 47, 46, 45, 44, 43, 54, 53, 52, 51, 50, 49, 60, 59, 58, 57, 56, 55, 66, 65, 64, 63, 62, 61, 72, 71, 70, 69, 68, 67, 216, 210, 204, 198, 192, 186, 215, 209, 203, 197, 191, 185, 214, 208, 202, 196, 190, 184, 213, 207, 201, 195, 189, 183, 212, 206, 200, 194, 188, 182, 211, 205, 199, 193, 187, 181),
    "reflect-x z x x" : (0, 109, 115, 121, 127, 133, 139, 110, 116, 122, 128, 134, 140, 111, 117, 123, 129, 135, 141, 112, 118, 124, 130, 136, 142, 113, 119, 125, 131, 137, 143, 114, 120, 126, 132, 138, 144, 36, 30, 24, 18, 12, 6, 35, 29, 23, 17, 11, 5, 34, 28, 22, 16, 10, 4, 33, 27, 21, 15, 9, 3, 32, 26, 20, 14, 8, 2, 31, 25, 19, 13, 7, 1, 145, 151, 157, 163, 169, 175, 146, 152, 158, 164, 170, 176, 147, 153, 159, 165, 171, 177, 148, 154, 160, 166, 172, 178, 149, 155, 161, 167, 173, 179, 150, 156, 162, 168, 174, 180, 216, 210, 204, 198, 192, 186, 215, 209, 203, 197, 191, 185, 214, 208, 202, 196, 190, 184, 213, 207, 201, 195, 189, 183, 212, 206, 200, 194, 188, 182, 211, 205, 199, 193, 187, 181, 108, 102, 96, 90, 84, 78, 107, 101, 95, 89, 83, 77, 106, 100, 94, 88, 82, 76, 105, 99, 93, 87, 81, 75, 104, 98, 92, 86, 80, 74, 103, 97, 91, 85, 79, 73, 37, 43, 49, 55, 61, 67, 38, 44, 50, 56, 62, 68, 39, 45, 51, 57, 63, 69, 40, 46, 52, 58, 64, 70, 41, 47, 53, 59, 65, 71, 42, 48, 54, 60, 66, 72),
    "reflect-x z y y" : (0, 72, 66, 60, 54, 48, 42, 71, 65, 59, 53, 47, 41, 70, 64, 58, 52, 46, 40, 69, 63, 57, 51, 45, 39, 68, 62, 56, 50, 44, 38, 67, 61, 55, 49, 43, 37, 181, 187, 193, 199, 205, 211, 182, 188, 194, 200, 206, 212, 183, 189, 195, 201, 207, 213, 184, 190, 196, 202, 208, 214, 185, 191, 197, 203, 209, 215, 186, 192, 198, 204, 210, 216, 180, 174, 168, 162, 156, 150, 179, 173, 167, 161, 155, 149, 178, 172, 166, 160, 154, 148, 177, 171, 165, 159, 153, 147, 176, 170, 164, 158, 152, 146, 175, 169, 163, 157, 151, 145, 1, 7, 13, 19, 25, 31, 2, 8, 14, 20, 26, 32, 3, 9, 15, 21, 27, 33, 4, 10, 16, 22, 28, 34, 5, 11, 17, 23, 29, 35, 6, 12, 18, 24, 30, 36, 73, 79, 85, 91, 97, 103, 74, 80, 86, 92, 98, 104, 75, 81, 87, 93, 99, 105, 76, 82, 88, 94, 100, 106, 77, 83, 89, 95, 101, 107, 78, 84, 90, 96, 102, 108, 144, 138, 132, 126, 120, 114, 143, 137, 131, 125, 119, 113, 142, 136, 130, 124, 118, 112, 141, 135, 129, 123, 117, 111, 140, 134, 128, 122, 116, 110, 139, 133, 127, 121, 115, 109),
}

def rotate_666(cube, step):
    return [cube[x] for x in swaps_666[step]]
