#!/usr/bin/env python3

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
    get_characters_common_count,
    stage_first_four_edges_wing_str_combos,
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
edges_444 = (
    2, 3, 5, 8, 9, 12, 14, 15,      # Upper
    18, 19, 21, 24, 25, 28, 30, 31, # Left
    34, 35, 37, 40, 41, 44, 46, 47, # Front
    50, 51, 53, 56, 57, 60, 62, 63, # Right
    66, 67, 69, 72, 73, 76, 78, 79, # Back
    82, 83, 85, 88, 89, 92, 94, 95) # Down

wings_444 = (
    2, 3,   # Upper
    5, 9,
    8, 12,
    14, 15,
    21, 25, # Left
    24, 28,
    53, 57, # Right
    56, 60,
    82, 83, # Back
    85, 89,
    88, 92,
    94, 95
)

def get_best_entry(foo):
    # TODO this can only track wings since it is only used by 4x4x4
    best_entry = None
    best_paired_edges = None
    best_paired_wings = None
    best_steps_len = None

    for (paired_edges, paired_wings, steps_len, state) in foo:
        if (best_entry is None or
            paired_edges > best_paired_edges or
            (paired_edges == best_paired_edges and paired_wings > best_paired_wings) or
            (paired_edges == best_paired_edges and paired_wings == best_paired_wings and steps_len < best_steps_len)):

            best_entry = (paired_edges, paired_wings, steps_len, state)
            best_paired_edges = paired_edges
            best_paired_wings = paired_wings
            best_steps_len = steps_len
    return best_entry


def get_edges_paired_binary_signature(state):
    """
    The facelets are numbered:

                  - 02 03 -
                 05  - -  08
                 09  - -  12
                  - 14 15 -

     - 18 19 -    - 34 35 -    - 50 51 -    - 66 67 -
    21  - -  24  37  - -  40  53  - -  56  69  - -  72
    25  - -  28  41  - -  44  57  - -  60  73  - -  76
     - 30 31 -    - 46 47 -    - 62 63 -    - 78 79 -

                  - 82 83 -
                 85  - -  88
                 89  - -  92
                  - 94 95 -


    The wings are labeled 0123456789abcdefghijklmn

                  -  0 1  -
                  2  - -  3
                  4  - -  5
                  -  6 7 -

     -  2 4  -    -  6 7  -    -  5 3  -    -  1 0  -
     8  - -  9    9  - -  c    c  - -  d    d  - -  8
     a  - -  b    b  - -  e    e  - -  f    f  - -  a
     -  k i  -    -  g h  -    -  j l  -    -  n m  -

                  -  g h  -
                  i  - -  j
                  k  - -  l
                  -  m n  -

    'state' goes wing by # wing and records the location of where the sibling wing is located.

    state: 10425376a8b9ecfdhgkiljnm

    index: 000000000011111111112222
           012345678901234567890123

    get_edges_paired_binary_signature('10425376a8b9ecfdhgkiljnm')
    111111111111

    get_edges_paired_binary_signature('7ad9nlg0j14cbm2i6kfh85e3')
    000000000000
    """
    result = []

    # Upper
    if state[0] == '1':
        result.append('1')
    else:
        result.append('0')

    if state[2] == '4':
        result.append('1')
    else:
        result.append('0')

    if state[4] == '5':
        result.append('1')
    else:
        result.append('0')

    if state[6] == '7':
        result.append('1')
    else:
        result.append('0')

    # Left
    if state[8] == 'a':
        result.append('1')
    else:
        result.append('0')

    if state[10] == 'b':
        result.append('1')
    else:
        result.append('0')

    # Right
    if state[12] == 'e':
        result.append('1')
    else:
        result.append('0')

    if state[14] == 'f':
        result.append('1')
    else:
        result.append('0')

    # Down
    if state[16] == 'h':
        result.append('1')
    else:
        result.append('0')

    if state[18] == 'k':
        result.append('1')
    else:
        result.append('0')

    if state[20] == 'l':
        result.append('1')
    else:
        result.append('0')

    if state[22] == 'n':
        result.append('1')
    else:
        result.append('0')

    return ''.join(result)


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
    1 steps has 96 entries (0 percent, 0.00x previous step)
    2 steps has 1,008 entries (0 percent, 10.50x previous step)
    3 steps has 8,208 entries (0 percent, 8.14x previous step)
    4 steps has 41,712 entries (2 percent, 5.08x previous step)
    5 steps has 145,560 entries (7 percent, 3.49x previous step)
    6 steps has 321,576 entries (15 percent, 2.21x previous step)
    7 steps has 514,896 entries (25 percent, 1.60x previous step)
    8 steps has 496,560 entries (24 percent, 0.96x previous step)
    9 steps has 324,096 entries (15 percent, 0.65x previous step)
    10 steps has 177,408 entries (8 percent, 0.55x previous step)
    11 steps has 26,880 entries (1 percent, 0.15x previous step)

    Total: 2,058,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD',
            linecount=2058000)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in centers_444])
        return result


class LookupTable444TsaiPhase1(LookupTable):
    """
    lookup-table-4x4x4-step50-tsai-phase1.txt
    =========================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 82 entries (0 percent, 16.40x previous step)
    3 steps has 1,206 entries (0 percent, 14.71x previous step)
    4 steps has 14,116 entries (1 percent, 11.70x previous step)
    5 steps has 123,404 entries (16 percent, 8.74x previous step)
    6 steps has 422,508 entries (57 percent, 3.42x previous step)
    7 steps has 173,254 entries (23 percent, 0.41x previous step)
    8 steps has 896 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step50-tsai-phase1.txt',
            '0f0f00',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in centers_444])

        # Convert to hex
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
            '111111111111_10425376a8b9ecfdhgkiljnm',
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

                #log.warning("phase3_edges state %s, steps %s" % (
                #    self.parent.lt_tsai_phase3_edges_solve.state(),
                #    ' '.join(self.parent.lt_tsai_phase3_edges_solve.steps())))

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


wings_for_edges_recolor_pattern_444 = (
    ('0', 2, 67),  # upper
    ('1', 3, 66),
    ('2', 5, 18),
    ('3', 8, 51),
    ('4', 9, 19),
    ('5', 12, 50),
    ('6', 14, 34),
    ('7', 15, 35),

    ('8', 21, 72), # left
    ('9', 24, 37),
    ('a', 25, 76),
    ('b', 28, 41),

    ('c', 53, 40), # right
    ('d', 56, 69),
    ('e', 57, 44),
    ('f', 60, 73),

    ('g', 82, 46), # down
    ('h', 83, 47),
    ('i', 85, 31),
    ('j', 88, 62),
    ('k', 89, 30),
    ('l', 92, 63),
    ('m', 94, 79),
    ('n', 95, 78))


def edges_recolor_pattern_444(state):
    edge_map = {
        'BD': [],
        'BL': [],
        'BR': [],
        'BU': [],
        'DF': [],
        'DL': [],
        'DR': [],
        'FL': [],
        'FR': [],
        'FU': [],
        'LU': [],
        'RU': []
    }

    # Record the two edge_indexes for each of the 12 edges
    for (edge_index, square_index, partner_index) in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))
        edge_map[wing_str].append(edge_index)

    # Where is the other wing_str like us?
    for (edge_index, square_index, partner_index) in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))

        for tmp_index in edge_map[wing_str]:
            if tmp_index != edge_index:
                state[square_index] = tmp_index
                state[partner_index] = tmp_index
                break
        else:
            raise Exception("could not find tmp_index")

    return ''.join(state)


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
    lookup-table-4x4x4-step70-tsai-phase3.txt
    ==========================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 34 entries (0 percent, 8.50x previous step)
    3 steps has 371 entries (0 percent, 10.91x previous step)
    4 steps has 3,834 entries (0 percent, 10.33x previous step)
    5 steps has 38,705 entries (0 percent, 10.10x previous step)
    6 steps has 385,795 entries (8 percent, 9.97x previous step)
    7 steps has 3,884,999 entries (90 percent, 10.07x previous step)

    Total: 4,313,742 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step70-tsai-phase3.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD10425376a8b9ecfdhgkiljnm',
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
            linecount=4313742)

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        centers_state = ''.join([state[square_index] for square_index in centers_444])
        edges_state = ''.join([state[square_index] for square_index in wings_444])
        return centers_state + edges_state


class LookupTable444Edges(LookupTable):
    """
    lookup-table-4x4x4-step100-edges.txt (10-deep)
    ==============================================
    2 steps has 1 entries (0 percent, 0.00x previous step)
    5 steps has 432 entries (0 percent, 432.00x previous step)
    6 steps has 2,053 entries (0 percent, 4.75x previous step)
    7 steps has 15,475 entries (0 percent, 7.54x previous step)
    8 steps has 151,530 entries (2 percent, 9.79x previous step)
    9 steps has 991,027 entries (13 percent, 6.54x previous step)
    10 steps has 6,203,073 entries (84 percent, 6.26x previous step)

    Total: 7,363,591 entries
    Average: 9.816544 moves


    lookup-table-4x4x4-step100-edges.txt (11-deep)
    ==============================================
    2 steps has 1 entries (0 percent, 0.00x previous step)
    5 steps has 432 entries (0 percent, 432.00x previous step)
    6 steps has 2053 entries (0 percent, 4.75x previous step)
    7 steps has 15475 entries (0 percent, 7.54x previous step)
    8 steps has 151530 entries (0 percent, 9.79x previous step)
    9 steps has 991027 entries (2 percent, 6.54x previous step)
    10 steps has 6203073 entries (17 percent, 6.26x previous step)
    11 steps has 27990511 entries (79 percent, 4.51x previous step)

    Total: 35354102 entries
    Average: 10.753509 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step100-edges.txt',
            '111111111111_10425376a8b9ecfdhgkiljnm',
            linecount=7363591) # 10-deep
            #linecount=35354102) # 11-deep


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
            self.lt_tsai_phase1 = LookupTable444TsaiPhase1(self)

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
            self.lt_tsai_phase3 = LookupTableIDA444TsaiPhase3(self)

        else:
            raise Exception("We should not be here, cpu_mode %s" % self.cpu_mode)

        # For tsai this tables is only used if the centers have already been solved
        # For non-tsai it is always used
        self.lt_edges = LookupTable444Edges(self)

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
            self.print_cube()
            log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
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

            log.info("%s: Start of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_tsai_phase1.solve()
            self.print_cube()
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

            log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_tsai_phase3.avoid_oll = True
            self.lt_tsai_phase3.avoid_pll = True
            self.lt_tsai_phase3.solve()
            self.print_cube()
            log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

    def solve_edges_six_then_six(self):

        if self.edges_paired():
            return True

        state = edges_recolor_pattern_444(self.state[:])

        edges_state = ''.join([state[square_index] for square_index in wings_444])
        signature = get_edges_paired_binary_signature(edges_state)
        signature_width = len(signature) + 1
        edges_state = signature + '_' + edges_state

        # If our state is in lookup-table-4x4x4-step100-edges.txt then execute
        # those steps and we are done
        steps = self.lt_edges.steps(edges_state)

        if steps is not None:
            for step in steps:
                self.rotate(step)
                return True

        # If we are here then we need to look through lookup-table-4x4x4-step100-edges.txt
        # to find the line whose state is the closest match to our own. This allows us to
        # pair some of our unpaired edges and make some progress even though our current
        # state isn't in the lookup table.
        MAX_WING_PAIRS = 12
        MAX_EDGES = 12

        # It takes 12 steps to solve PLL
        PLL_PENALTY = 12

        STATE_TARGET = '111111111111_10425376a8b9ecfdhgkiljnm'

        original_state = self.state[:]
        original_solution = self.solution[:]
        loop_count = 0

        while not self.edges_paired():

            # How many edges are paired?
            pre_non_paired_edges_count = self.get_non_paired_edges_count()
            pre_paired_edges_count = MAX_WING_PAIRS - pre_non_paired_edges_count

            state = edges_recolor_pattern_444(self.state[:])

            edges_state = ''.join([state[square_index] for square_index in wings_444])
            signature = get_edges_paired_binary_signature(edges_state)
            signature_width = len(signature) + 1
            edges_state = signature + '_' + edges_state

            log.info("solve_edges_six_then_six loop %d: signature %s" % (loop_count, signature))

            # Find all of the 'loose' matching entries in our lookup table. 'loose' means the
            # entry will not unpair any of our already paired wings.
            loose_matching_entry = []
            max_wing_pair_count = None

            # This runs much faster (than find_edge_entries_with_loose_signature) because
            # it is only looking over the signatures that are an exact match instead of a
            # loose match. It produces slightly longer solutions but in about 1/6 the time.
            log.debug("%s: find_edge_entries_with_signature start" % self)
            lines_to_examine = self.lt_edges.find_edge_entries_with_signature(signature)
            log.debug("%s: find_edge_entries_with_signature end (found %d)" % (self, len(lines_to_examine)))

            for line in lines_to_examine:
                (phase1_state, phase1_steps) = line.split(':')

                common_count = get_characters_common_count(edges_state,
                                                           phase1_state,
                                                           signature_width)
                wing_pair_count = int(common_count/2)

                # Only bother with this entry if it will pair more wings than are currently paired
                if wing_pair_count > pre_paired_edges_count:

                    if max_wing_pair_count is None:
                        loose_matching_entry.append((wing_pair_count, line))
                        max_wing_pair_count = wing_pair_count

                    elif wing_pair_count > max_wing_pair_count:
                        #loose_matching_entry = []
                        loose_matching_entry.append((wing_pair_count, line))
                        max_wing_pair_count = wing_pair_count

                    elif wing_pair_count == max_wing_pair_count or wing_pair_count >= 4:
                        loose_matching_entry.append((wing_pair_count, line))

            #log.warning("pre_paired_edges_count %d, loose_matching_entry %d" % (pre_paired_edges_count, len(loose_matching_entry)))
            #log.warning("pre_paired_edges_count %d, loose_matching_entry(%d):\n%s\n" %
            #    (pre_paired_edges_count, len(loose_matching_entry), pformat(loose_matching_entry)))
            best_score_states = []

            # Now run through each state:steps in loose_matching_entry
            for (wing_pair_count, line) in loose_matching_entry:
                self.state = original_state[:]
                self.solution = original_solution[:]

                (phase1_edges_state_fake, phase1_steps) = line.split(':')
                phase1_steps = phase1_steps.split()

                # Apply the phase1 steps
                for step in phase1_steps:
                    self.rotate(step)

                phase1_state = edges_recolor_pattern_444(self.state[:])
                phase1_edges_state = ''.join([phase1_state[square_index] for square_index in wings_444])
                phase1_signature = get_edges_paired_binary_signature(phase1_edges_state)
                phase1_edges_state = phase1_signature + '_' + phase1_edges_state

                # If that got us to our state_target then phase1 alone paired all
                # of the edges...this is unlikely
                if phase1_edges_state == STATE_TARGET:
                    if self.edge_solution_leads_to_pll_parity():
                        #best_score_states.append((MAX_EDGES, MAX_WING_PAIRS, len(phase1_steps) + PLL_PENALTY, phase1_steps[:]))
                        pass
                    else:
                        best_score_states.append((MAX_EDGES, MAX_WING_PAIRS, len(phase1_steps), phase1_steps[:]))

                else:
                    # phase1_steps did not pair all edges so do another lookup and execute those steps
                    phase2_steps = self.lt_edges.steps(phase1_edges_state)

                    if phase2_steps is not None:
                        for step in phase2_steps:
                            self.rotate(step)

                        phase2_state = edges_recolor_pattern_444(self.state[:])
                        phase2_edges_state = ''.join([phase2_state[square_index] for square_index in wings_444])
                        phase2_signature = get_edges_paired_binary_signature(phase2_edges_state)
                        phase2_edges_state = phase2_signature + '_' + phase2_edges_state
                        phase12_steps = phase1_steps + phase2_steps

                        if phase2_edges_state == STATE_TARGET:

                            if self.edge_solution_leads_to_pll_parity():
                                #best_score_states.append((MAX_EDGES, MAX_WING_PAIRS, len(phase12_steps) + PLL_PENALTY, phase12_steps[:]))
                                pass
                            else:
                                best_score_states.append((MAX_EDGES, MAX_WING_PAIRS, len(phase12_steps), phase12_steps[:]))
                        else:
                            post_non_paired_edges_count = self.get_non_paired_edges_count()
                            paired_edges_count = MAX_WING_PAIRS - post_non_paired_edges_count

                            best_score_states.append((paired_edges_count, paired_edges_count, len(phase12_steps), phase12_steps[:]))
                    else:
                        post_non_paired_edges_count = self.get_non_paired_edges_count()
                        paired_edges_count = MAX_WING_PAIRS - post_non_paired_edges_count

                        best_score_states.append((paired_edges_count, paired_edges_count, len(phase1_steps), phase1_steps[:]))

                #log.info("HERE 10 %s: %s, %s, phase1_edges_state %s, phase2 steps %s" %
                #    (self, wing_pair_count, line, phase1_edges_state, pformat(phase2_steps)))

            #log.info("best_score_states:\n%s" % pformat(best_score_states))
            best_entry = get_best_entry(best_score_states)
            #log.info("best_entry: %s" % pformat(best_entry))

            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in best_entry[3]:
                self.rotate(step)

            original_state = self.state[:]
            original_solution = self.solution[:]

            log.info("solve_edges_six_then_six loop %d: went from %d edges to %d edges in %d moves" %
                (loop_count, pre_paired_edges_count, best_entry[0], len(best_entry[3])))
            loop_count += 1

    def group_edges(self):

        if self.edges_paired():
            self.solution.append('EDGES_GROUPED')
            return

        self.lt_init()
        self.solve_edges_six_then_six()

        log.info("%s: edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.solution.append('EDGES_GROUPED')


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
