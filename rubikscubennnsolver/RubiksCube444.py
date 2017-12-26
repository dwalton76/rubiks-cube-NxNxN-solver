
from copy import copy
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.RubiksCube444Misc import (
    lookup_table_444_last_two_edges_place_F_east,
    lookup_table_444_sister_wing_to_F_east,
    lookup_table_444_sister_wing_to_U_west,
    tsai_phase2_orient_edges_444,
    tsai_edge_mapping_combinations,
)
from rubikscubennnsolver.LookupTable import (
    LookupTable,
    LookupTableIDA,
    LookupTableAStar,
    NoSteps,
    NoIDASolution,
)
from rubikscubennnsolver.rotate_xxx import rotate_444
from subprocess import check_output
from pprint import pformat
import itertools
import logging
import sys

log = logging.getLogger(__name__)


moves_4x4x4 = ("U", "U'", "U2", "Uw", "Uw'", "Uw2",
               "L", "L'", "L2", "Lw", "Lw'", "Lw2",
               "F" , "F'", "F2", "Fw", "Fw'", "Fw2",
               "R" , "R'", "R2", "Rw", "Rw'", "Rw2",
               "B" , "B'", "B2", "Bw", "Bw'", "Bw2",
               "D" , "D'", "D2", "Dw", "Dw'", "Dw2")
solved_4x4x4 = 'UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB'
centers_444 = (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91)
UD_centers_444 = (6, 7, 10, 11, 86, 87, 90, 91)
LR_centers_444 = (22, 23, 26, 27, 54, 55, 58, 59)


'''
lookup-table-4x4x4-step11-UD-centers-stage.txt
lookup-table-4x4x4-step12-LR-centers-stage.txt
lookup-table-4x4x4-step13-FB-centers-stage.txt
==============================================
1 steps has 3 entries (0 percent, 0.00x previous step)
2 steps has 36 entries (0 percent, 12.00x previous step)
3 steps has 484 entries (0 percent, 13.44x previous step)
4 steps has 5,408 entries (0 percent, 11.17x previous step)
5 steps has 48,955 entries (6 percent, 9.05x previous step)
6 steps has 242,011 entries (32 percent, 4.94x previous step)
7 steps has 362,453 entries (49 percent, 1.50x previous step)
8 steps has 75,955 entries (10 percent, 0.21x previous step)
9 steps has 166 entries (0 percent, 0.00x previous step)

Total: 735,471 entries
'''
class LookupTable444UDCentersStage(LookupTable):

    def __init__(self, parent):

        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step11-UD-centers-stage.txt',
            'f0000f',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable444LRCentersStage(LookupTable):

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step12-LR-centers-stage.txt',
            '0f0f00',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable444FBCentersStage(LookupTable):

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step13-FB-centers-stage.txt',
            '00f0f0',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('F', 'B') else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA444ULFRBDCentersStage(LookupTableIDA):
    """
    lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt
    ==================================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 54 entries (0 percent, 13.50x previous step)
    3 steps has 726 entries (0 percent, 13.44x previous step)
    4 steps has 9,300 entries (0 percent, 12.81x previous step)
    5 steps has 121,407 entries (7 percent, 13.05x previous step)
    6 steps has 1,586,554 entries (92 percent, 13.07x previous step)

    Total: 1,718,045 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt',
            'UUUULLLLFFFFLLLLFFFFUUUU',
            moves_4x4x4,

            # illegal_moves...ignoring these increases the average solution
            # by less than 1 move but makes the IDA search about 20x faster
            ("Lw", "Lw'", "Lw2",
             "Bw", "Bw'", "Bw2",
             "Dw", "Dw'", "Dw2"),

            # prune tables
            (parent.lt_UD_centers_stage,
             parent.lt_LR_centers_stage,
             parent.lt_FB_centers_stage),
            linecount=1718045)

    def state(self):
        parent_state = self.parent.state
        result = []

        for index in centers_444:
            x = parent_state[index]

            if x in ('L', 'F', 'U'):
                result.append(x)
            elif x == 'R':
                result.append('L')
            elif x == 'B':
                result.append('F')
            elif x == 'D':
                result.append('U')

        result = ''.join(result)
        return result


class LookupTable444ULFRBDCentersSolve(LookupTable):
    """
    lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt
    ==================================================
    1 steps has 7 entries (0 percent)
    2 steps has 99 entries (0 percent)
    3 steps has 996 entries (0 percent)
    4 steps has 6,477 entries (1 percent)
    5 steps has 23,540 entries (6 percent)
    6 steps has 53,537 entries (15 percent)
    7 steps has 86,464 entries (25 percent)
    8 steps has 83,240 entries (24 percent)
    9 steps has 54,592 entries (15 percent)
    10 steps has 29,568 entries (8 percent)
    11 steps has 4,480 entries (1 percent)

    Total: 343,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD',
            linecount=343000)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in centers_444])
        return result


class LookupTable444TsaiPhase1Edges(LookupTable):
    """
    lookup-table-4x4x4-step51-tsai-phase1-edges.txt
    ====================================
    1 steps has 6 entries (0 percent, 0.00x previous step)
    2 steps has 89 entries (0 percent, 14.83x previous step)
    3 steps has 1,441 entries (0 percent, 16.19x previous step)
    4 steps has 22,955 entries (0 percent, 15.93x previous step)
    5 steps has 310,270 entries (11 percent, 13.52x previous step)
    6 steps has 1,799,686 entries (66 percent, 5.80x previous step)
    7 steps has 569,705 entries (21 percent, 0.32x previous step)
    8 steps has 4 entries (0 percent, 0.00x previous step)

    Total: 2,704,156 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step51-tsai-phase1-edges.txt',
            '995a665a6699',
            linecount=2704156)

    def state(self):
        return self.parent.tsai_phase2_orient_edges_state([], return_hex=True)


class LookupTable444TsaiPhase1Centers(LookupTable):
    """
    lookup-table-4x4x4-step52-tsai-phase1-centers.txt
    ======================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 36 entries (0 percent, 12.00x previous step)
    3 steps has 484 entries (0 percent, 13.44x previous step)
    4 steps has 5,408 entries (0 percent, 11.17x previous step)
    5 steps has 48,955 entries (6 percent, 9.05x previous step)
    6 steps has 242,011 entries (32 percent, 4.94x previous step)
    7 steps has 362,453 entries (49 percent, 1.50x previous step)
    8 steps has 75,955 entries (10 percent, 0.21x previous step)
    9 steps has 166 entries (0 percent, 0.00x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step52-tsai-phase1-centers.txt',
            '0f0f00',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable444TsaiPhase1(LookupTableIDA):
    """
    lookup-table-4x4x4-step50-tsai-phase1.txt
    ==============================
    1 steps has 6 entries (0 percent, 0.00x previous step)
    2 steps has 93 entries (0 percent, 15.50x previous step)
    3 steps has 1,627 entries (0 percent, 17.49x previous step)
    4 steps has 28,647 entries (0 percent, 17.61x previous step)
    5 steps has 515,604 entries (5 percent, 18.00x previous step)
    6 steps has 9,120,256 entries (94 percent, 17.69x previous step)

    Total: 9,666,233 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step50-tsai-phase1.txt',
            '8615fa6065fa606861',
            moves_4x4x4,

            ("Lw", "Lw'", "Lw2",
             "Bw", "Bw'", "Bw2",
             "Dw", "Dw'", "Dw2"),

            # prune tables
            (parent.lt_tsai_phase1_edges,
             parent.lt_tsai_phase1_centers),
            linecount=9666233)

    def state(self):
        babel_centers = {
            'L' : '1',
            'F' : '0',
            'R' : '1',
            'B' : '0',
            'D' : '0',
            'U' : '0',
        }

        babel_edges = {
            'U' : '1',
            'D' : '0',
        }

        orient_edges = tsai_phase2_orient_edges_444
        parent_state = self.parent.state

        result = [
            # Upper
            babel_edges[orient_edges[(2, 67, parent_state[2], parent_state[67])]],
            babel_edges[orient_edges[(3, 66, parent_state[3], parent_state[66])]],
            babel_edges[orient_edges[(5, 18, parent_state[5], parent_state[18])]],
            babel_centers[parent_state[6]],
            babel_centers[parent_state[7]],
            babel_edges[orient_edges[(8, 51, parent_state[8], parent_state[51])]],
            babel_edges[orient_edges[(9, 19, parent_state[9], parent_state[19])]],
            babel_centers[parent_state[10]],
            babel_centers[parent_state[11]],
            babel_edges[orient_edges[(12, 50, parent_state[12], parent_state[50])]],
            babel_edges[orient_edges[(14, 34, parent_state[14], parent_state[34])]],
            babel_edges[orient_edges[(15, 35, parent_state[15], parent_state[35])]],

            # Left
            babel_edges[orient_edges[(18, 5, parent_state[18], parent_state[5])]],
            babel_edges[orient_edges[(19, 9, parent_state[19], parent_state[9])]],
            babel_edges[orient_edges[(21, 72, parent_state[21], parent_state[72])]],
            babel_centers[parent_state[22]],
            babel_centers[parent_state[23]],
            babel_edges[orient_edges[(24, 37, parent_state[24], parent_state[37])]],
            babel_edges[orient_edges[(25, 76, parent_state[25], parent_state[76])]],
            babel_centers[parent_state[26]],
            babel_centers[parent_state[27]],
            babel_edges[orient_edges[(28, 41, parent_state[28], parent_state[41])]],
            babel_edges[orient_edges[(30, 89, parent_state[30], parent_state[89])]],
            babel_edges[orient_edges[(31, 85, parent_state[31], parent_state[85])]],

            # Front
            babel_edges[orient_edges[(34, 14, parent_state[34], parent_state[14])]],
            babel_edges[orient_edges[(35, 15, parent_state[35], parent_state[15])]],
            babel_edges[orient_edges[(37, 24, parent_state[37], parent_state[24])]],
            babel_centers[parent_state[38]],
            babel_centers[parent_state[39]],
            babel_edges[orient_edges[(40, 53, parent_state[40], parent_state[53])]],
            babel_edges[orient_edges[(41, 28, parent_state[41], parent_state[28])]],
            babel_centers[parent_state[42]],
            babel_centers[parent_state[43]],
            babel_edges[orient_edges[(44, 57, parent_state[44], parent_state[57])]],
            babel_edges[orient_edges[(46, 82, parent_state[46], parent_state[82])]],
            babel_edges[orient_edges[(47, 83, parent_state[47], parent_state[83])]],

            # Right
            babel_edges[orient_edges[(50, 12, parent_state[50], parent_state[12])]],
            babel_edges[orient_edges[(51, 8, parent_state[51], parent_state[8])]],
            babel_edges[orient_edges[(53, 40, parent_state[53], parent_state[40])]],
            babel_centers[parent_state[54]],
            babel_centers[parent_state[55]],
            babel_edges[orient_edges[(56, 69, parent_state[56], parent_state[69])]],
            babel_edges[orient_edges[(57, 44, parent_state[57], parent_state[44])]],
            babel_centers[parent_state[58]],
            babel_centers[parent_state[59]],
            babel_edges[orient_edges[(60, 73, parent_state[60], parent_state[73])]],
            babel_edges[orient_edges[(62, 88, parent_state[62], parent_state[88])]],
            babel_edges[orient_edges[(63, 92, parent_state[63], parent_state[92])]],

            # Back
            babel_edges[orient_edges[(66, 3, parent_state[66], parent_state[3])]],
            babel_edges[orient_edges[(67, 2, parent_state[67], parent_state[2])]],
            babel_edges[orient_edges[(69, 56, parent_state[69], parent_state[56])]],
            babel_centers[parent_state[70]],
            babel_centers[parent_state[71]],
            babel_edges[orient_edges[(72, 21, parent_state[72], parent_state[21])]],
            babel_edges[orient_edges[(73, 60, parent_state[73], parent_state[60])]],
            babel_centers[parent_state[74]],
            babel_centers[parent_state[75]],
            babel_edges[orient_edges[(76, 25, parent_state[76], parent_state[25])]],
            babel_edges[orient_edges[(78, 95, parent_state[78], parent_state[95])]],
            babel_edges[orient_edges[(79, 94, parent_state[79], parent_state[94])]],

            # Down
            babel_edges[orient_edges[(82, 46, parent_state[82], parent_state[46])]],
            babel_edges[orient_edges[(83, 47, parent_state[83], parent_state[47])]],
            babel_edges[orient_edges[(85, 31, parent_state[85], parent_state[31])]],
            babel_centers[parent_state[86]],
            babel_centers[parent_state[87]],
            babel_edges[orient_edges[(88, 62, parent_state[88], parent_state[62])]],
            babel_edges[orient_edges[(89, 30, parent_state[89], parent_state[30])]],
            babel_centers[parent_state[90]],
            babel_centers[parent_state[91]],
            babel_edges[orient_edges[(92, 63, parent_state[92], parent_state[63])]],
            babel_edges[orient_edges[(94, 79, parent_state[94], parent_state[79])]],
            babel_edges[orient_edges[(95, 78, parent_state[95], parent_state[78])]]
        ]

        result = ''.join(result)
        return self.hex_format % int(result, 2)


class LookupTable444TsaiPhase2Centers(LookupTable):
    """
    lookup-table-4x4x4-step61-centers.txt
    =====================================
    1 steps has 34 entries (0 percent, 0.00x previous step)
    2 steps has 194 entries (0 percent, 5.71x previous step)
    3 steps has 1,716 entries (0 percent, 8.85x previous step)
    4 steps has 12,206 entries (1 percent, 7.11x previous step)
    5 steps has 68,428 entries (7 percent, 5.61x previous step)
    6 steps has 247,370 entries (27 percent, 3.62x previous step)
    7 steps has 434,332 entries (48 percent, 1.76x previous step)
    8 steps has 135,034 entries (14 percent, 0.31x previous step)
    9 steps has 1,586 entries (0 percent, 0.01x previous step)

    Total: 900,900 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step61-tsai-phase2-centers.txt',
            ('UUUULLLLFFFFRRRRFFFFUUUU',
             'UUUURRRRFFFFLLLLFFFFUUUU',
             'UUUULLRRFFFFRRLLFFFFUUUU',
             'UUUULLRRFFFFLLRRFFFFUUUU',
             'UUUURRLLFFFFRRLLFFFFUUUU',
             'UUUURRLLFFFFLLRRFFFFUUUU',
             'UUUURLRLFFFFRLRLFFFFUUUU',
             'UUUURLRLFFFFLRLRFFFFUUUU',
             'UUUULRLRFFFFRLRLFFFFUUUU',
             'UUUULRLRFFFFLRLRFFFFUUUU',
             'UUUURLLRFFFFLRRLFFFFUUUU',
             'UUUULRRLFFFFRLLRFFFFUUUU'),
            linecount=900900)

    def state(self):
        parent_state = self.parent.state
        result = []

        for index in centers_444:
            x = parent_state[index]

            if x in ('L', 'F', 'R', 'U'):
                result.append(x)
            elif x == 'B':
                result.append('F')
            elif x == 'D':
                result.append('U')

        result = ''.join(result)
        return result


tsai_phase2_LR_center_targets = set((
    'LLLLRRRR',
    'RRRRLLLL',
    'LLRRRRLL',
    'LLRRLLRR',
    'RRLLRRLL',
    'RRLLLLRR',
    'RLRLRLRL',
    'RLRLLRLR',
    'LRLRRLRL',
    'LRLRLRLR',
    'RLLRLRRL',
    'LRRLRLLR'))

class LookupTableIDA444TsaiPhase2(LookupTableIDA):

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step60-tsai-phase2-dummy.txt',
            'TBD',
            moves_4x4x4,
            ("Fw", "Fw'", "Bw", "Bw'",
             "Uw", "Uw'", "Dw", "Dw'", # illegal_moves
             "Bw2", "Dw2", "Lw", "Lw'", "Lw2"), # TPR also restricts these

            # prune tables
            (parent.lt_tsai_phase2_centers,),
            linecount=0)

    def state(self):
        babel = {
            'L' : 'L',
            'F' : 'F',
            'R' : 'R',
            'B' : 'F',
            'D' : 'U',
            'U' : 'U',
        }
        parent_state = self.parent.state

        result = [
            # Upper
            parent_state[2], parent_state[3],
            parent_state[5], babel[parent_state[6]], babel[parent_state[7]], parent_state[8],
            parent_state[9], babel[parent_state[10]], babel[parent_state[11]], parent_state[12],
            parent_state[14], parent_state[15],

            # Left
            parent_state[18], parent_state[19],
            parent_state[21], babel[parent_state[22]], babel[parent_state[23]], parent_state[24],
            parent_state[25], babel[parent_state[26]], babel[parent_state[27]], parent_state[28],
            parent_state[30], parent_state[31],

            # Front
            parent_state[34], parent_state[35],
            parent_state[37], babel[parent_state[38]], babel[parent_state[39]], parent_state[40],
            parent_state[41], babel[parent_state[42]], babel[parent_state[43]], parent_state[44],
            parent_state[46], parent_state[47],

            # Right
            parent_state[50], parent_state[51],
            parent_state[53], babel[parent_state[54]], babel[parent_state[55]], parent_state[56],
            parent_state[57], babel[parent_state[58]], babel[parent_state[59]], parent_state[60],
            parent_state[62], parent_state[63],

            # Back
            parent_state[66], parent_state[67],
            parent_state[69], babel[parent_state[70]], babel[parent_state[71]], parent_state[72],
            parent_state[73], babel[parent_state[74]], babel[parent_state[75]], parent_state[76],
            parent_state[78], parent_state[79],

            # Down
            parent_state[82], parent_state[83],
            parent_state[85], babel[parent_state[86]], babel[parent_state[87]], parent_state[88],
            parent_state[89], babel[parent_state[90]], babel[parent_state[91]], parent_state[92],
            parent_state[94], parent_state[95],
        ]

        result = ''.join(result)
        return result

    def search_complete(self, state, steps_to_here):
        parent_state = self.parent.state

        # Are UD and FB staged? Check UD, if it is staged FB has to be staged too.
        for x in UD_centers_444:
            if parent_state[x] not in ('U', 'D'):
                return False

        # Are the LR sides in 1 of the 12 states we want?
        LR_centers = [parent_state[x] for x in LR_centers_444]
        LR_centers = ''.join(LR_centers)

        if LR_centers not in tsai_phase2_LR_center_targets:
            return False

        # If we are here then our centers are all good...check the edges.
        # If the edges are not in lt_tsai_phase3_edges_solve it may throw a KeyError
        try:
            if self.parent.lt_tsai_phase3_edges_solve.steps() is not None and self.parent.edge_swaps_even(False, None, False):

                # rotate_xxx() is very fast but it does not append the
                # steps to the solution so put the cube back in original state
                # and execute the steps via a normal rotate() call
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]

                for step in steps_to_here:
                    self.parent.rotate(step)

                return True

        except KeyError:
            pass

        return False


symmetry_rotations_tsai_phase3_444 =\
    ("",
     "y y",
     "x",
     "x y y",
     "x'",
     "x' y y",
     "x x",
     "x x y y",
     "reflect-x",
     "reflect-x y y",
     "reflect-x x",
     "reflect-x x y y",
     "reflect-x x'",
     "reflect-x x' y y",
     "reflect-x x x",
     "reflect-x x x y y")

# 12-23 are high edges, make these U (1)
# 0-11 are low edges, make these D (6)
# https://github.com/cs0x7f/TPR-4x4x4-Solver/blob/master/src/FullCube.java
high_edges_444 = ((14, 2, 67),  # upper
                  (13, 9, 19),
                  (15, 8, 51),
                  (12, 15, 35),
                  (21, 25, 76), # left
                  (20, 24, 37),
                  (23, 57, 44), # right
                  (22, 56, 69),
                  (18, 82, 46), # down
                  (17, 89, 30),
                  (19, 88, 62),
                  (16, 95, 78))

low_edges_444 = ((2, 3, 66),  # upper
                 (1, 5, 18),
                 (3, 12, 50),
                 (0, 14, 34),
                 (9, 21, 72), # left
                 (8, 28, 41),
                 (11, 53, 40), # right
                 (10, 60, 73),
                 (6, 83, 47), # down
                 (5, 85, 31),
                 (7, 92, 63),
                 (4, 94, 79))

def edges_high_low_recolor_444(state):
    """
    Look at all of the high edges and find the low edge for each.
    Return a string that represents where all the low edge siblings live in relation to their high edge counterpart.
    """
    #assert len(state) == 97, "Invalid state %s, len is %d" % (state, len(state))
    low_edge_map = {}

    for (low_edge_index, square_index, partner_index) in low_edges_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        #assert square_value != partner_value, "both squares are %s" % square_value
        wing_str = ''.join(sorted([square_value, partner_value]))
        low_edge_index = str(hex(low_edge_index))[2:]
        state[square_index] = low_edge_index
        state[partner_index] = low_edge_index

        #assert wing_str not in low_edge_map, "We have two %s wings, one at high_index %s %s and one at high_index %s (%d, %d), state %s" %\
        #    (wing_str,
        #     low_edge_map[wing_str],
        #     pformat(low_edges_444[int(low_edge_map[wing_str])]),
        #     low_edge_index,
        #     square_index, partner_index,
        #     ''.join(state[1:]))

        # save low_edge_index in hex and chop the leading 0x via [2:]
        low_edge_map[wing_str] = low_edge_index

    #assert len(low_edge_map.keys()) == 12, "Invalid low_edge_map\n%s\n" % pformat(low_edge_map)

    for (high_edge_index, square_index, partner_index) in high_edges_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))
        state[square_index] = low_edge_map[wing_str]
        state[partner_index] = low_edge_map[wing_str]
    return state

def reflect_x_444(cube):
    return [cube[0],
           cube[93], cube[94], cube[95], cube[96],
           cube[89], cube[90], cube[91], cube[92],
           cube[85], cube[86], cube[87], cube[88],
           cube[81], cube[82], cube[83], cube[84],
           cube[29], cube[30], cube[31], cube[32],
           cube[25], cube[26], cube[27], cube[28],
           cube[21], cube[22], cube[23], cube[24],
           cube[17], cube[18], cube[19], cube[20],
           cube[45], cube[46], cube[47], cube[48],
           cube[41], cube[42], cube[43], cube[44],
           cube[37], cube[38], cube[39], cube[40],
           cube[33], cube[34], cube[35], cube[36],
           cube[61], cube[62], cube[63], cube[64],
           cube[57], cube[58], cube[59], cube[60],
           cube[53], cube[54], cube[55], cube[56],
           cube[49], cube[50], cube[51], cube[52],
           cube[77], cube[78], cube[79], cube[80],
           cube[73], cube[74], cube[75], cube[76],
           cube[69], cube[70], cube[71], cube[72],
           cube[65], cube[66], cube[67], cube[68],
           cube[13], cube[14], cube[15], cube[16],
           cube[9], cube[10], cube[11], cube[12],
           cube[5], cube[6], cube[7], cube[8],
           cube[1], cube[2], cube[3], cube[4]]


class LookupTable444TsaiPhase3Edges(LookupTable):
    """
    lookup-table-4x4x4-step71-tsai-phase3-edges.txt
    - without symmetry
    - we use the copy with symmetry I just left this here for the history
    ===============================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 20 entries (0 percent, 5.00x previous step)
    3 steps has 140 entries (0 percent, 7.00x previous step)
    4 steps has 1,141 entries (0 percent, 8.15x previous step)
    5 steps has 8,059 entries (0 percent, 7.06x previous step)
    6 steps has 62,188 entries (0 percent, 7.72x previous step)
    7 steps has 442,293 entries (0 percent, 7.11x previous step)
    8 steps has 2,958,583 entries (1 percent, 6.69x previous step)
    9 steps has 17,286,512 entries (7 percent, 5.84x previous step)
    10 steps has 69,004,356 entries (28 percent, 3.99x previous step)
    11 steps has 122,416,936 entries (51 percent, 1.77x previous step)
    12 steps has 27,298,296 entries (11 percent, 0.22x previous step)
    13 steps has 22,272 entries (0 percent, 0.00x previous step)

    Total: 239,500,800 entries


    lookup-table-4x4x4-step71-tsai-phase3-edges.txt
    - with symmetry
    ===============================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 7 entries (0 percent, 2.33x previous step)
    3 steps has 24 entries (0 percent, 3.43x previous step)
    4 steps has 103 entries (0 percent, 4.29x previous step)
    5 steps has 619 entries (0 percent, 6.01x previous step)
    6 steps has 4,287 entries (0 percent, 6.93x previous step)
    7 steps has 28,697 entries (0 percent, 6.69x previous step)
    8 steps has 187,493 entries (1 percent, 6.53x previous step)
    9 steps has 1,087,267 entries (7 percent, 5.80x previous step)
    10 steps has 4,323,558 entries (28 percent, 3.98x previous step)
    11 steps has 7,657,009 entries (51 percent, 1.77x previous step)
    12 steps has 1,708,625 entries (11 percent, 0.22x previous step)
    13 steps has 1,448 entries (0 percent, 0.00x previous step)

    Total: 14,999,140 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step71-tsai-phase3-edges.txt',
            '213098ba6574',
            linecount=14999140)

    def state(self):
        parent_state = self.parent.state
        original_state = list('x' + ''.join(parent_state[1:]))
        results = []

        for seq in symmetry_rotations_tsai_phase3_444:
            state = original_state[:]

            for step in seq.split():
                if step == 'reflect-x':
                    state = reflect_x_444(state[:])
                else:
                    state = rotate_444(state[:], step)

            state = edges_high_low_recolor_444(state[:])

            # record the state of all edges
            state = ''.join(state)
            state = ''.join((state[2],   state[9],  state[8],  state[15],
                             state[25], state[24],
                             state[57], state[56],
                             state[82], state[89], state[88], state[95]))
            results.append(state[:])

        results = sorted(results)
        return results[0]


class LookupTable444TsaiPhase3CentersSolve(LookupTable):
    """
    lookup-table-4x4x4-step72-tsai-phase3-centers.txt
    =================================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 34 entries (0 percent, 8.50x previous step)
    3 steps has 247 entries (0 percent, 7.26x previous step)
    4 steps has 1,282 entries (2 percent, 5.19x previous step)
    5 steps has 4,844 entries (8 percent, 3.78x previous step)
    6 steps has 11,821 entries (20 percent, 2.44x previous step)
    7 steps has 17,486 entries (29 percent, 1.48x previous step)
    8 steps has 15,121 entries (25 percent, 0.86x previous step)
    9 steps has 6,889 entries (11 percent, 0.46x previous step)
    10 steps has 1,063 entries (1 percent, 0.15x previous step)
    11 steps has 9 entries (0 percent, 0.01x previous step)

    Total: 58,800 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step72-tsai-phase3-centers.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD',
            linecount=58800)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            parent_state[6],
            parent_state[7],
            parent_state[10],
            parent_state[11],

            # Left
            parent_state[22],
            parent_state[23],
            parent_state[26],
            parent_state[27],

            # Front
            parent_state[38],
            parent_state[39],
            parent_state[42],
            parent_state[43],

            # Right
            parent_state[54],
            parent_state[55],
            parent_state[58],
            parent_state[59],

            # Back
            parent_state[70],
            parent_state[71],
            parent_state[74],
            parent_state[75],

            # Down
            parent_state[86],
            parent_state[87],
            parent_state[90],
            parent_state[91]
        ]

        result = ''.join(result)
        return result


class LookupTableIDA444TsaiPhase3(LookupTableIDA):
    """
    If you build this to 8-deep it adds 119,166,578 which makes it too big to
    check into the repo

    lookup-table-4x4x4-step70-tsai-phase3.txt
    ==========================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 34 entries (0 percent, 8.50x previous step)
    3 steps has 371 entries (0 percent, 10.91x previous step)
    4 steps has 3,834 entries (0 percent, 10.33x previous step)
    5 steps has 38,705 entries (0 percent, 10.10x previous step)
    6 steps has 385,747 entries (0 percent, 9.97x previous step)
    7 steps has 3,884,435 entries (8 percent, 10.07x previous step)
    8 steps has 39,549,005 entries (90 percent, 10.18x previous step)

    Total: 43,862,135 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step70-tsai-phase3.txt',
            '001UU31UU322118LL98LL955229BBa9BBa4433aRRbaRRb7700bFF8bFF866445DD75DD766',
            moves_4x4x4,

            # illegal moves
            ("Fw", "Fw'",
             "Uw", "Uw'",
             "Rw", "Rw'",
             "Lw", "Lw'", "Lw2",
             "Bw", "Bw'", "Bw2",
             "Dw", "Dw'", "Dw2",
             "R", "R'",
             "L", "L'"),

            # prune tables
            (parent.lt_tsai_phase3_edges_solve,
             parent.lt_tsai_phase3_centers_solve),
            linecount=43862135)

    def state(self):
        parent_state = self.parent.state
        original_state = edges_high_low_recolor_444(parent_state[:])
        results = []

        for seq in symmetry_rotations_tsai_phase3_444:
            tmp_state = original_state[:]

            for step in seq.split():
                if step == 'reflect-x':
                    tmp_state = reflect_x_444(tmp_state[:])
                else:
                    tmp_state = rotate_444(tmp_state[:], step)

            # record the state of all edges and centers
            result = \
                tmp_state[2:4] + tmp_state[5:13] + tmp_state[14:16] +\
                tmp_state[18:20] + tmp_state[21:29] + tmp_state[30:32] +\
                tmp_state[34:36] + tmp_state[37:45] + tmp_state[46:48] +\
                tmp_state[50:52] + tmp_state[53:61] + tmp_state[62:64] +\
                tmp_state[66:68] + tmp_state[69:77] + tmp_state[78:80] +\
                tmp_state[82:84] + tmp_state[85:93] + tmp_state[94:96]

            result = ''.join(result)
            results.append(result[:])

        results = sorted(results)
        return results[0]


class LookupTable444EdgeSliceForward(LookupTable):
    """
    22*20*18 is 7920

    lookup-table-4x4x4-step80-edges-slice-forward.txt
    =================================================
    1 steps has 7 entries (0 percent)
    2 steps has 42 entries (0 percent)
    3 steps has 299 entries (3 percent)
    4 steps has 1,306 entries (16 percent)
    5 steps has 3,449 entries (43 percent)
    6 steps has 2,617 entries (33 percent)
    7 steps has 200 entries (2 percent)

    Total: 7,920 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step80-edges-slice-forward.txt',
            'EDGES',
            linecount=7920)

    def state(self):
        raise Exception("This should never be called")


class LookupTable444EdgesSliceBackward(LookupTable):
    """
    22*20*18 is 7920
    No idea why I am one entry short (should be 7920 total)...oh well

    lookup-table-4x4x4-step90-edges-slice-backward.txt
    ==================================================
    1 steps has 1 entries (0 percent)
    3 steps has 36 entries (0 percent)
    4 steps has 66 entries (0 percent)
    5 steps has 334 entries (4 percent)
    6 steps has 1,369 entries (17 percent)
    7 steps has 3,505 entries (44 percent)
    8 steps has 2,539 entries (32 percent)
    9 steps has 69 entries (0 percent)

    Total: 7,919 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step90-edges-slice-backward.txt',
            'EDGES',
            linecount=7919)

    def state(self):
        raise Exception("This should never be called")


class RubiksCube444(RubiksCube):

    def __init__(self, state, order, colormap=None, avoid_pll=True, debug=False):
        RubiksCube.__init__(self, state, order, colormap, debug)
        self.avoid_pll = avoid_pll
        self.edge_mapping = {}

        if debug:
            log.setLevel(logging.DEBUG)

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

    def sanity_check(self):
        corners = (1, 4, 13, 16,
                   17, 20, 29, 32,
                   33, 36, 45, 48,
                   49, 52, 61, 64,
                   65, 68, 77, 80,
                   81, 84, 93, 96)

        centers = (6, 7, 10, 11,
                   22, 23, 26, 27,
                   38, 39, 42, 43,
                   54, 55, 58, 59,
                   70, 71, 74, 75,
                   86, 87, 90, 91)

        edge_orbit_0 = (2, 3, 8, 12, 15, 14, 9, 5,
                        18, 19, 24, 28, 31, 30, 25, 21,
                        34, 35, 40, 44, 47, 46, 41, 37,
                        50, 51, 56, 60, 62, 63, 57, 53,
                        66, 67, 72, 76, 79, 78, 73, 69,
                        82, 83, 88, 92, 95, 94, 89, 85)

        self._sanity_check('corners', corners, 4)
        self._sanity_check('centers', centers, 4)
        self._sanity_check('edge-orbit-0', edge_orbit_0, 8)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # brainstorm
        # Today we typically stage all centers and then solve them
        # - Staging is 24!/(8! * 8! * 8!) or 9,465,511,770
        # - We have three prune tables (UD, LR, and FB) of 24!/(8! * 16!) or 735,471
        #
        # option #1 - solve all centers at once
        # - would be 24!/(4! * 4! * 4! * 4! * 4! * 4!) or 3,246,670,537,110,000
        # - three prune tables (UD, LR, and FB) of 24!/(4! * 4! * 16!) or 51,482,970
        # - 51,482,970 / 3,246,670,537,110,000 is 0.000 000 015 8571587, IDA might take a few hours
        # - I've done this before and it removes ~6 steps when solving centers. We
        #   currently average 64 steps to solve a 4x4x4 but the tsai solver averages 55....so
        #   this would take a few hours to run but solutions still wouldn't be as short as
        #   the tsai solver.
        # - feasible but not worth it
        #
        #
        # option #2 - combine tsai phases 1 and 2
        # - this would be staging UD, FB centers, solving LR centers and orienting all edges
        # - orienting edges is 2,704,156
        # - centers is 24!/(4! * 4! * 8! * 8!) or 662,585,823,900
        # - so would be 662,585,823,900 * 2,704,156 or 1,791,735,431,214,128,400
        # - 2,704,156 / 1,791,735,431,214,128,400 or 0.000 000 000 001 5092, IDA might take weeks
        # - 662,585,823,900 / 1,791,735,431,214,128,400 or 0.000 000 369 8011505, IDA would be
        #   fast but that is with a 662 billion entry prune table
        # - a LR prune table would be 24!/(4! * 4! * 16!) or 51,482,970
        #   - 51,482,970 / 1,791,735,431,214,128,400 or 0.000 000 000 028 7336, IDA might take weeks
        # - a UDFB prune table would be 24!/(8! * 8! * 8!) or 9,465,511,770
        #   - 9,465,511,770 / 1,791,735,431,214,128,400 or 0.000 000 005 2828736, IDA would take a few hours
        #     9 billion would be a huge prune table
        # - probably not feasible


        # There are three CPU "modes" we can run in:
        #
        # normal : Uses a middle ground of CPU and produces not the shortest or longest solution.
        #          This will stage all centers at once.
        #
        # max    : Uses more CPU and produce a shorter solution
        #          This will stage all centers at once.
        #
        # tsai   : Uses the most CPU but produces the shortest solution

        # ==============
        # Phase 1 tables
        # ==============
        if self.cpu_mode in ('normal', 'max'):

            # prune tables
            self.lt_UD_centers_stage = LookupTable444UDCentersStage(self)
            self.lt_LR_centers_stage = LookupTable444LRCentersStage(self)
            self.lt_FB_centers_stage = LookupTable444FBCentersStage(self)

            # Stage all centers via IDA
            self.lt_ULFRBD_centers_stage = LookupTableIDA444ULFRBDCentersStage(self)

        elif self.cpu_mode == 'tsai':

            # Stage LR centers
            self.lt_tsai_phase1_edges = LookupTable444TsaiPhase1Edges(self)
            self.lt_tsai_phase1_centers = LookupTable444TsaiPhase1Centers(self)
            self.lt_tsai_phase1 = LookupTable444TsaiPhase1(self)
            self.lt_tsai_phase1_centers.preload_cache()

        else:
            raise Exception("We should not be here, cpu_mode %s" % self.cpu_mode)

        # =============
        # Phase2 tables
        # =============
        if self.cpu_mode in ('normal', 'max'):
            self.lt_ULFRBD_centers_solve = LookupTable444ULFRBDCentersSolve(self)

        elif self.cpu_mode == 'tsai':
            # - orient the edges into high/low groups
            # - solve LR centers to one of 12 states
            # - stage UD and FB centers
            self.lt_tsai_phase2_centers = LookupTable444TsaiPhase2Centers(self)
            self.lt_tsai_phase2 = LookupTableIDA444TsaiPhase2(self)
            #self.lt_tsai_phase2_centers.preload_cache()

        else:
            raise Exception("We should not be here, cpu_mode %s" % self.cpu_mode)

        # =============
        # Phase3 tables
        # =============
        if self.cpu_mode in ('normal', 'max'):
            pass

        elif self.cpu_mode == 'tsai':

            # prune tables
            self.lt_tsai_phase3_edges_solve = LookupTable444TsaiPhase3Edges(self)
            self.lt_tsai_phase3_centers_solve = LookupTable444TsaiPhase3CentersSolve(self)

            #self.lt_tsai_phase3_edges_solve.preload_state_set()
            #self.lt_tsai_phase3_centers_solve.preload_cache()

            self.lt_tsai_phase3 = LookupTableIDA444TsaiPhase3(self)

        else:
            raise Exception("We should not be here, cpu_mode %s" % self.cpu_mode)


        # For tsai these two tables are only used if the centers have already been solved
        # For non-tsai they are always used
        self.lt_edge_slice_forward = LookupTable444EdgeSliceForward(self)
        self.lt_edge_slice_backward = LookupTable444EdgesSliceBackward(self)

    def tsai_phase2_orient_edges_state(self, edges_to_flip, return_hex):
        state = self.state
        result = []

        wing_str_map = {
            'UB' : 'UB',
            'BU' : 'UB',
            'UL' : 'UL',
            'LU' : 'UL',
            'UR' : 'UR',
            'RU' : 'UR',
            'UF' : 'UF',
            'FU' : 'UF',
            'LB' : 'LB',
            'BL' : 'LB',
            'LF' : 'LF',
            'FL' : 'LF',
            'RB' : 'RB',
            'BR' : 'RB',
            'RF' : 'RF',
            'FR' : 'RF',
            'DB' : 'DB',
            'BD' : 'DB',
            'DL' : 'DL',
            'LD' : 'DL',
            'DR' : 'DR',
            'RD' : 'DR',
            'DF' : 'DF',
            'FD' : 'DF',
        }

        for (x, y) in (
                (2, 67), (3, 66), (5, 18), (8, 51), (9, 19), (12, 50), (14, 34),
                (15, 35), (18, 5), (19, 9), (21, 72), (24, 37), (25, 76), (28, 41),
                (30, 89), (31, 85), (34, 14), (35, 15), (37, 24), (40, 53), (41, 28),
                (44, 57), (46, 82), (47, 83), (50, 12), (51, 8), (53, 40), (56, 69),
                (57, 44), (60, 73), (62, 88), (63, 92), (66, 3), (67, 2), (69, 56),
                (72, 21), (73, 60), (76, 25), (78, 95), (79, 94), (82, 46), (83, 47),
                (85, 31), (88, 62), (89, 30), (92, 63), (94, 79), (95, 78)):
            state_x = state[x]
            state_y = state[y]
            wing_str = wing_str_map[''.join((state_x, state_y))]
            high_low = tsai_phase2_orient_edges_444[(x, y, state_x, state_y)]

            if wing_str in edges_to_flip:
                if high_low == 'U':
                    high_low = 'D'
                else:
                    high_low = 'U'

            if return_hex:
                high_low = high_low.replace('D', '0').replace('U', '1')

            result.append(high_low)

        result = ''.join(result)

        if return_hex:
            return "%012x" % int(result, 2)
        else:
            return result

    def tsai_phase2_orient_edges_print(self):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()

        orient_edge_state = list(self.tsai_phase2_orient_edges_state(self.edge_mapping, return_hex=False))
        orient_edge_state_index = 0
        for side in list(self.sides.values()):
            for square_index in side.edge_pos:
                self.state[square_index] = orient_edge_state[orient_edge_state_index]
                orient_edge_state_index += 1
        self.print_cube()

        self.state = original_state[:]
        self.solution = original_solution[:]

    def group_centers_guts(self):
        self.lt_init()

        # The non-tsai solver will only solve the centers here
        if self.cpu_mode in ('normal', 'max'):

            # If the centers are already solve then return and let group_edges() pair the edges
            if self.centers_solved():
                return

            log.info("%s: Start of Phase1" % self)
            self.lt_ULFRBD_centers_stage.avoid_oll = True
            self.lt_ULFRBD_centers_stage.solve()
            log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.print_cube()
            log.info("")

            log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_ULFRBD_centers_solve.solve()
            self.print_cube()
            log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

        # The tsai will solve the centers and pair the edges
        elif self.cpu_mode == 'tsai':

            # save cube state
            original_state = self.state[:]
            original_solution = self.solution[:]

            # Test the prune tables
            #self.lt_tsai_phase1_centers.solve()
            #self.lt_tsai_phase1_edges.solve()
            #self.tsai_phase2_orient_edges_print()
            #self.print_cube()
            #sys.exit(0)

            log.info("%s: Start of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_tsai_phase1.solve()
            self.print_cube()
            #self.tsai_phase2_orient_edges_print()
            log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

            # Test the prune table
            #self.lt_tsai_phase2_centers.solve()
            #self.tsai_phase2_orient_edges_print()
            #self.print_cube()
            #sys.exit(0)

            log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_tsai_phase2.avoid_oll = True
            self.lt_tsai_phase2.avoid_pll = True
            self.lt_tsai_phase2.solve()
            self.print_cube()
            #self.tsai_phase2_orient_edges_print()
            log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

            # Testing the phase3 prune tables
            #self.lt_tsai_phase3_edges_solve.solve()
            #self.lt_tsai_phase3_centers_solve.solve()
            #self.tsai_phase2_orient_edges_print()
            #self.print_cube()
            #sys.exit(0)

            log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_tsai_phase3.avoid_oll = True
            self.lt_tsai_phase3.avoid_pll = True
            self.lt_tsai_phase3.solve()
            self.print_cube()
            log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

    def edge_string_to_find(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = []
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in sorted(side.edge_pos):

                if square_index in (target_wing[0], target_wing[1]):
                    state.append('A')

                elif square_index in (sister_wing1[0], sister_wing1[1]):
                    state.append('B')

                elif square_index in (sister_wing2[0], sister_wing2[1]):
                    state.append('C')

                elif square_index in (sister_wing3[0], sister_wing3[1]):
                    state.append('D')

                else:
                    state.append('x')

        return ''.join(state)

    def find_moves_to_stage_slice_forward_444(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        """
        target_wing must go in spot 41
        sister_wing1 must go in spot (40, 53)
        sister_wing2 must go in spot (56, 69)
        sister_wing3 must go in spot (72, 21)
        """
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_forward.steps(state)

    def find_moves_to_stage_slice_backward_444(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        """
        target_wing must go in spot (44, 57)
        sister_wing1 must go in spot (24, 37)
        sister_wing2 must go in spot (72, 21))
        sister_wing3 must go in spot (56, 69)
        """
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_backward.steps(state)

    def prep_for_slice_back_444(self):

        # Now set things up so that when we slice back we pair another 3 edges.
        # Work with the wing on the bottom of F-east
        target_wing = self.sideF.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        target_wing_partner_index = 57
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]
        steps = self.find_moves_to_stage_slice_backward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True

        # If we are here it means the unpaired edge on F-east needs to be swapped with
        # its sister_wing1. In other words F-east and sister-wing1 have the same two
        # sets of colors and the two of them together would create two paired edges if
        # we swapped their wings.
        #
        # As a work-around, move some other unpaired edge into F-east. There are no
        # guarantees we won't hit the exact same problem with that edge but that doesn't
        # happen too often.

        if not self.sideU.north_edge_paired() and self.sideU.has_wing(sister_wing1) != 'north':
            self.rotate("F'")
            self.rotate("U2")
            self.rotate("F")
        elif not self.sideU.east_edge_paired() and self.sideU.has_wing(sister_wing1) != 'east':
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
        elif not self.sideU.west_edge_paired() and self.sideU.has_wing(sister_wing1) != 'west':
            self.rotate("F'")
            self.rotate("U'")
            self.rotate("F")
        elif not self.sideD.south_edge_paired() and self.sideD.has_wing(sister_wing1) != 'south':
            self.rotate("F")
            self.rotate("D2")
            self.rotate("F'")
        elif not self.sideD.east_edge_paired() and self.sideD.has_wing(sister_wing1) != 'east':
            self.rotate("F")
            self.rotate("D'")
            self.rotate("F'")
        elif not self.sideD.west_edge_paired() and self.sideD.has_wing(sister_wing1) != 'west':
            self.rotate("F")
            self.rotate("D")
            self.rotate("F'")
        # Look for these last since they take 4 steps instead of 3
        elif not self.sideU.south_edge_paired() and self.sideU.has_wing(sister_wing1) != 'south':
            self.rotate("U'")
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
        elif not self.sideD.north_edge_paired() and self.sideD.has_wing(sister_wing1) != 'north':
            self.rotate("D")
            self.rotate("F")
            self.rotate("D'")
            self.rotate("F'")
        else:
            # If we are here we are down to two unpaired wings
            return False

        if self.sideF.east_edge_paired():
            raise SolveError("F-east should not be paired")

        target_wing = self.sideF.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        target_wing_partner_index = 57
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]
        steps = self.find_moves_to_stage_slice_backward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True
        else:
            return False

    def pair_six_edges_444(self, wing_to_pair):
        """
        Sections are:
        - PREP-FOR-Uw-SLICE
        - Uw
        - PREP-FOR-REVERSE-Uw-SLICE
        - Uw'
        """

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        self.rotate_edge_to_F_west(wing_to_pair)
        #log.info("PREP-FOR-Uw-SLICE (begin)")
        #self.print_cube()

        # Work with the wing at the bottom of the F-west edge
        # Move the sister wing to the top of F-east
        target_wing = self.sideF.edge_west_pos[-1]
        target_wing_partner_index = 28
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]

        steps = self.find_moves_to_stage_slice_forward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if not steps:
            log.info("pair_six_edges_444()    could not find steps to slice forward")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        #log.info("PREP-FOR-Uw-SLICE (end)....SLICE (begin)")
        #self.print_cube()
        self.rotate("Uw")
        #log.info("SLICE (end)")
        #self.print_cube()

        post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_edges_444()    paired %d wings in %d moves on slice forward (%d left to pair)" %
            (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_wings_count))

        if self.sideL.west_edge_paired():

            # The stars aligned and we paired 4 at once so we cannot rotate L-west around
            # to F-east, move an unpaired edge to F-east. This preserves the LFRB centers
            # for the slice back.
            if not self.sideU.north_edge_paired():
                self.rotate("F'")
                self.rotate("U2")
                self.rotate("F")
            elif not self.sideU.east_edge_paired():
                self.rotate("F'")
                self.rotate("U")
                self.rotate("F")
            elif not self.sideU.west_edge_paired():
                self.rotate("F'")
                self.rotate("U'")
                self.rotate("F")
            elif not self.sideD.south_edge_paired():
                self.rotate("F")
                self.rotate("D2")
                self.rotate("F'")
            elif not self.sideD.east_edge_paired():
                self.rotate("F")
                self.rotate("D'")
                self.rotate("F'")
            elif not self.sideD.west_edge_paired():
                self.rotate("F")
                self.rotate("D")
                self.rotate("F'")
            # Look for these last since they take 4 steps instead of 3
            elif not self.sideU.south_edge_paired():
                self.rotate("U'")
                self.rotate("F'")
                self.rotate("U")
                self.rotate("F")
            elif not self.sideD.north_edge_paired():
                self.rotate("D")
                self.rotate("F")
                self.rotate("D'")
                self.rotate("F'")
            else:
                raise SolveError("Did not find an unpaired edge")

        else:
            self.rotate_y()
            self.rotate_y()

        if self.sideF.east_edge_paired():
            log.warning("F-east should not be paired")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        if not self.prep_for_slice_back_444():
            log.warning("cannot slice back")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        #log.info("PREP-FOR-Uw'-SLICE-BACK (end)...SLICE BACK (begin)")
        #self.print_cube()
        self.rotate("Uw'")
        #log.info("SLICE BACK (end)")
        #self.print_cube()

        post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_edges_444()    paired %d wings in %d moves on slice back (%d left to pair)" %
            (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len - post_slice_forward_solution_len,
             post_slice_back_non_paired_wings_count))

        return True

    def pair_last_six_edges_444(self):
        """
        Sections are:
        - PREP-FOR-Uw-SLICE
        - Uw
        - PREP-FOR-REVERSE-Uw-SLICE
        - Uw'
        """
        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_non_paired_edges = self.get_non_paired_edges()

        min_solution_len = None
        min_solution_state = None
        min_solution = None

        for wing_to_pair in original_non_paired_edges:
            self.state = original_state[:]
            self.solution = original_solution[:]
            self.rotate_edge_to_F_west(wing_to_pair[0])

            # Work with the wing at the bottom of the F-west edge
            # Move the sister wing to the top of F-east
            target_wing = self.sideF.edge_west_pos[-1]
            target_wing_partner_index = 28
            sister_wing1 = self.get_wings(target_wing)[0]
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])
            sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
            sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
            sister_wing2_side = self.get_side_for_index(sister_wing2[0])
            sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
            sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]

            #log.info("target_wing: %s" % target_wing)
            #log.info("sister_wing1 %s on %s, neighbor %s" % (sister_wing1, sister_wing1_side, sister_wing1_neighbor))
            #log.info("sister_wing2 %s on %s, neighbor %s" % (sister_wing2, sister_wing2_side, sister_wing2_neighbor))
            #log.info("sister_wing3 %s" % pformat(sister_wing3))

            sister_wing3_candidates = []

            # We need sister_wing3 to be any unpaired edge that allows us
            # to only pair 2 on the slice forward
            for wing in self.get_non_paired_wings():
                if (wing[0] not in (target_wing, sister_wing1, sister_wing2, sister_wing3) and
                    wing[1] not in (target_wing, sister_wing1, sister_wing2, sister_wing3)):
                    sister_wing3_candidates.append(wing[1])

            min_sister_wing3_steps_len = None
            min_sister_wing3_steps = None
            min_sister_wing3 = None

            for x in sister_wing3_candidates:
                steps = self.find_moves_to_stage_slice_forward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, x)

                if steps:
                    steps_len = len(steps)

                    if min_sister_wing3_steps_len is None or steps_len < min_sister_wing3_steps_len:
                        min_sister_wing3_steps_len = steps_len
                        min_sister_wing3_steps = steps
                        min_sister_wing3 = x

            sister_wing3 = min_sister_wing3
            steps = min_sister_wing3_steps
            #log.info("sister_wing3 %s" % pformat(sister_wing3))

            if not steps:
                log.info("pair_last_six_edges_444() cannot slice back (no steps found)")
                continue

            for step in steps:
                self.rotate(step)

            # At this point we are setup to slice forward and pair 2 edges
            #log.info("PREP-FOR-Uw-SLICE (end)....SLICE (begin)")
            #self.print_cube()
            self.rotate("Uw")
            #log.info("SLICE (end)")
            #self.print_cube()

            post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
            post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

            log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice forward (%d left to pair)" %
                (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
                 post_slice_forward_solution_len - original_solution_len,
                 post_slice_forward_non_paired_wings_count))

            if self.sideF.east_edge_paired():
                for x in range(3):
                    self.rotate_y()
                    if not self.sideF.east_edge_paired():
                        break

            if self.sideF.east_edge_paired():
                log.info("pair_last_six_edges_444() cannot slice back (F-east paired)")
                continue

            if not self.prep_for_slice_back_444():
                log.info("pair_last_six_edges_444() cannot slice back (prep failed)")
                continue

            self.rotate("Uw'")

            post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
            post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

            if min_solution_len is None or post_slice_back_solution_len < min_solution_len:
                min_solution_len = post_slice_back_solution_len
                min_solution_state = self.state[:]
                min_solution = self.solution[:]
                log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice back (%d left to pair) (NEW MIN %d)" %
                    (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - post_slice_forward_solution_len,
                    post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - original_solution_len))
            else:
                log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice back (%d left to pair)" %
                    (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - post_slice_forward_solution_len,
                    post_slice_back_non_paired_wings_count))

        if min_solution_len:
            self.state = min_solution_state
            self.solution = min_solution
            return True
        else:
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

    def pair_four_edges_444(self, edge):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        if original_non_paired_wings_count < 4:
            raise SolveError("pair_four_edges_444() requires at least 4 unpaired edges")

        self.rotate_edge_to_F_west(edge)

        # Work with the wing at the bottom of the F-west edge
        target_wing = self.sideF.edge_west_pos[-1]

        # Move the sister wing to F east
        sister_wing = self.get_wings(target_wing)[0]
        steps = lookup_table_444_sister_wing_to_F_east[sister_wing]

        for step in steps.split():
            self.rotate(step)

        self.rotate("Uw")

        if not self.sideR.west_edge_paired():
            pass
        elif not self.sideB.west_edge_paired():
            self.rotate_y()
        elif not self.sideL.west_edge_paired():
            self.rotate_y()
            self.rotate_y()

        if not self.prep_for_slice_back_444():
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        self.rotate("Uw'")

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_four_edges_444()    paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count >= original_non_paired_wings_count:
            raise SolveError("Went from %d to %d non_paired_edges" %
                (original_non_paired_wings_count, current_non_paired_wings_count))

        return True

    def pair_two_edges_444(self, edge):
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        if original_non_paired_wings_count == 2:
            raise SolveError("pair_last_two_edges_444() should be used when there are only 2 edges left")

        self.rotate_edge_to_F_west(edge)

        # Work with the wing at the bottom of the F-west edge
        target_wing = self.sideF.edge_west_pos[-1]

        # Move the sister wing to F east...this uses a small lookup table
        # that I built manually. This puts the sister wing at F-east in the correct
        # orientation (it will not need to be flipped). We used to just move the
        # sister wing to F-east but then sometimes we would need to "R U' B' R2"
        # to flip it around.
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_F_east:
            log.warning("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'F-east')
            raise ImplementThis("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_F_east[sister_wing]

        for step in steps.split():
            self.rotate(step)

        # Now that that two edges on F are in place, put an unpaired edge at U-west.
        # The unpaired edge that we place at U-west should contain the
        # sister wing of the wing that is at the bottom of F-east. This
        # will allow us to pair two wings at once.
        wing_bottom_F_east = self.sideF.edge_east_pos[-1]
        sister_wing_bottom_F_east = self.get_wings(wing_bottom_F_east)[0]

        if sister_wing_bottom_F_east not in lookup_table_444_sister_wing_to_U_west:
            raise ImplementThis("sister_wing_bottom_F_east %s" % pformat(sister_wing_bottom_F_east))

        steps = lookup_table_444_sister_wing_to_U_west[sister_wing_bottom_F_east]

        # If steps is None it means sister_wing_bottom_F_east is at (37, 24)
        # which is the top wing on F-west. If that is the case call
        # pair_last_two_edges_444()
        if steps == None:
            self.state = original_state[:]
            self.solution = original_solution[:]
            #self.print_cube()
            self.pair_last_two_edges_444(edge)
        else:
            for step in steps.split():
                self.rotate(step)

            for step in ("Uw", "L'", "U'", "L", "Uw'"):
                self.rotate(step)

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_two_edges_444()    paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count < original_non_paired_wings_count:
            return True

        raise SolveError("Went from %d to %d non_paired_edges" %
            (original_non_paired_wings_count, current_non_paired_wings_count))

    def pair_last_two_edges_444(self, edge):
        """
        At one point I looked into using two lookup tables to do this:
        - the first to stage edges to F-west and F-east
        - the second to solve the two staged edges

        The first stage took 1 or steps and the 2nd stage took either 7 or 10, it
        was 10 if the wing at F-east was turned the wrong way and needed to be
        rotated around. It wasn't worth it...what I have below works just fine and
        takes between 7 to 11 steps total.
        """
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        # rotate unpaired edge to F-west
        self.rotate_edge_to_F_west(edge)

        pos1 = self.sideF.edge_west_pos[-1]

        # Put the other unpaired edge on F east...this uses a small lookup table
        # that I built manually. This puts the sister wing at F-east in the correct
        # orientation (it will not need to be flipped). We used to just move the
        # sister wing to F-east but then sometimes we would need to "R F' U R' F"
        # to flip it around.
        sister_wing = self.get_wings(pos1)[0]

        steps = lookup_table_444_last_two_edges_place_F_east[sister_wing]
        for step in steps.split():
            self.rotate(step)

        # "Solving the last 4 edge blocks" in
        # http://www.rubiksplace.com/cubes/4x4/
        for step in ("Dw", "R", "F'", "U", "R'", "F", "Dw'"):
            self.rotate(step)

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_last_two_edges_444() paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if original_non_paired_wings_count == 2:
            if current_non_paired_wings_count:
                raise SolveError("Failed to pair last two edges")

    def pair_edge(self, edge_to_pair):
        """
        Pair a specific edge
        """
        pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
        pre_non_paired_edges_count = self.get_non_paired_edges_count()
        log.info("pair_edge() for %s (%d wings left to pair)" % (pformat(edge_to_pair), pre_non_paired_edges_count))

        if pre_non_paired_edges_count > 6:
            if not self.pair_six_edges_444(edge_to_pair[0]):
                log.info("pair_six_edges_444()    returned False")

                if not self.pair_four_edges_444(edge_to_pair[0]):
                    log.info("pair_four_edges_444() returned False")
                    self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count == 6:
            if not self.pair_last_six_edges_444():
                log.info("pair_last_six_edges_444() returned False")

                if not self.pair_four_edges_444(edge_to_pair[0]):
                    log.info("pair_four_edges_444() returned False")
                    self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count >= 4:
            if not self.pair_four_edges_444(edge_to_pair[0]):
                log.info("pair_four_edges_444() returned False")
                self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count == 2:
            self.pair_last_two_edges_444(edge_to_pair[0])

        # The scenario where you have 3 unpaired edges
        elif pre_non_paired_edges_count > 2:
            self.pair_two_edges_444(edge_to_pair[0])

        post_non_paired_edges_count = self.get_non_paired_edges_count()
        edges_paired = pre_non_paired_edges_count - post_non_paired_edges_count

        if edges_paired < 1:
            raise SolveError("Paired %d edges" % edges_paired)

        return True

    def group_edges_recursive(self, depth, edge_to_pair):
        """
        """
        pre_non_paired_wings_count = len(self.get_non_paired_wings())
        pre_non_paired_edges_count = len(self.get_non_paired_edges())
        edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len

        log.info("")
        log.info("group_edges_recursive(%d) called with edge_to_pair %s (%d edges and %d wings left to pair, min solution len %s, current solution len %d)" %
                (depth,
                 pformat(edge_to_pair),
                 pre_non_paired_edges_count,
                 pre_non_paired_wings_count,
                 self.min_edge_solution_len,
                 edge_solution_len))

        # Should we continue down this branch or should we prune it? An estimate
        # of 2 moves to pair an edge is a low estimate so if the current number of
        # steps plus 2 * pre_non_paired_wings_count is greater than our current minimum
        # there isn't any point in continuing down this branch so prune it and save
        # some CPU cycles.
        estimate_per_wing = 2.0

        estimated_solution_len = edge_solution_len + (estimate_per_wing * pre_non_paired_wings_count)

        if estimated_solution_len >= self.min_edge_solution_len:
            #log.warning("PRUNE: %s + (2 * %d) > %s" % (edge_solution_len, non_paired_wings_count, self.min_edge_solution_len))
            return False

        # The only time this will be None is on the initial call to group_edges_recursive()
        if edge_to_pair:
            self.pair_edge(edge_to_pair)

        non_paired_edges = self.get_non_paired_edges()

        if non_paired_edges:
            original_state = self.state[:]
            original_solution = self.solution[:]

            # call group_edges_recursive() for each non-paired edge
            for edge in non_paired_edges:
                self.group_edges_recursive(depth+1, edge)
                self.state = original_state[:]
                self.solution = original_solution[:]

        else:

            # If you solve 3x3x3 and then resolve PLL it takes 12 steps but if we avoid it here
            # it only takes 7 steps. If we are pairing the outside edges of a 5x5x5 self.avoid_pll
            # will be False.
            if self.avoid_pll and self.edge_solution_leads_to_pll_parity():
                for step in "Rw2 U2 F2 Rw2 F2 U2 Rw2".split():
                    self.rotate(step)

            # There are no edges left to pair, note how many steps it took pair them all
            edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len

            # Remember the solution that pairs all edges in the least number of moves
            if edge_solution_len < self.min_edge_solution_len:
                self.min_edge_solution_len = edge_solution_len
                self.min_edge_solution = self.solution[:]
                self.min_edge_solution_state = self.state[:]
                log.warning("NEW MIN: edges paired in %d steps" % self.min_edge_solution_len)

            return True

    def group_edges(self):
        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        depth = 0
        self.lt_init()
        self.center_solution_len = self.get_solution_len_minus_rotates(self.solution)
        self.min_edge_solution_len = 9999
        self.min_edge_solution = None
        self.min_edge_solution_state = None

        # group_edges_recursive() is where the magic happens
        self.group_edges_recursive(depth, None)
        self.state = self.min_edge_solution_state[:]
        self.solution = self.min_edge_solution[:]
        self.solution.append('EDGES_GROUPED')
