#!/usr/bin/env python3

from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.misc import pre_steps_to_try
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.RubiksCube444 import moves_444
from rubikscubennnsolver.LookupTable import (
    steps_on_same_face_and_layer,
    LookupTable,
    LookupTableHashCostOnly,
    LookupTableIDA,
)
import itertools
import logging
import sys

log = logging.getLogger(__name__)

moves_555 = moves_444
solved_555 = 'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB'

centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19,
    32, 33, 34, 37, 38, 39, 42, 43, 44,
    57, 58, 59, 62, 63, 64, 67, 68, 69,
    82, 83, 84, 87, 88, 89, 92, 93, 94,
    107, 108, 109, 112, 113, 114, 117, 118, 119,
    132, 133, 134, 137, 138, 139, 142, 143, 144
)

LFRB_centers_555 = (
    32, 33, 34, 37, 38, 39, 42, 43, 44,
    57, 58, 59, 62, 63, 64, 67, 68, 69,
    82, 83, 84, 87, 88, 89, 92, 93, 94,
    107, 108, 109, 112, 113, 114, 117, 118, 119
)

edge_orbit_0_555 = (
    2, 4, 10, 20, 24, 22, 16, 6,
    27, 29, 35, 45, 49, 47, 41, 31,
    52, 54, 60, 70, 74, 72, 66, 56,
    77, 79, 85, 95, 99, 97, 91, 81,
    102, 104, 110, 120, 124, 122, 116, 106,
    127, 129, 135, 145, 149, 147, 141, 131
)

edge_orbit_1_555 = (
    3, 15, 23, 11,
    28, 40, 48, 36,
    53, 65, 73, 61,
    78, 90, 98, 86,
    103, 115, 123, 111,
    128, 140, 148, 136
)

corners_555 = (
    1, 5, 21, 25,
    26, 30, 46, 50,
    51, 55, 71, 75,
    76, 80, 96, 100,
    101, 105, 121, 125,
    126, 130, 146, 150
)

x_centers_555 = (
    7, 9, 17, 19,
    32, 34, 42, 44,
    57, 59, 67, 69,
    82, 84, 92, 94,
    107, 109, 117, 119,
    132, 134, 142, 144
)

t_centers_555 = (
    8, 12, 14, 18,
    33, 37, 39, 43,
    58, 62, 64, 68,
    83, 87, 89, 93,
    108, 112, 114, 118,
    133, 137, 139, 143
)

LFRB_t_centers_555 = (
    33, 37, 39, 43,
    58, 62, 64, 68,
    83, 87, 89, 93,
    108, 112, 114, 118
)

edges_555 = (
    2, 3, 4,
    6, 10,
    11, 15,
    16, 20,
    22, 23, 24,

    27, 28, 29,
    31, 35,
    36, 40,
    41, 45,
    47, 48, 49,

    52, 53, 54,
    56, 60,
    61, 65,
    66, 70,
    72, 73, 74,

    77, 78, 79,
    81, 85,
    86, 90,
    91, 95,
    97, 98, 99,

    102, 103, 104,
    106, 110,
    111, 115,
    116, 120,
    122, 123, 124,

    127, 128, 129,
    131, 135,
    136, 140,
    141, 145,
    147, 148, 149
)

wings_555 = (
    2, 3, 4,       # Upper
    6, 11, 16,
    10, 15, 20,
    22, 23, 24,
    31, 36, 41,    # Left
    35, 40, 45,
    81, 86, 91,    # Right
    85, 90, 95,
    127, 128, 129, # Down
    131, 136, 141,
    135, 140, 145,
    147, 148, 149
)


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


wing_strs_all = (
    'BD',
    'BL',
    'BR',
    'BU',
    'DF',
    'DL',
    'DR',
    'FL',
    'FR',
    'FU',
    'LU',
    'RU'
)


edges_partner_555 = {
    2: 104,
    3: 103,
    4: 102,
    6: 27,
    10: 79,
    11: 28,
    15: 78,
    16: 29,
    20: 77,
    22: 52,
    23: 53,
    24: 54,
    31: 110,
    35: 56,
    36: 115,
    40: 61,
    41: 120,
    45: 66,
    81: 60,
    85: 106,
    86: 65,
    90: 111,
    91: 70,
    95: 116,
    127: 72,
    128: 73,
    129: 74,
    131: 49,
    135: 97,
    136: 48,
    140: 98,
    141: 47,
    145: 99,
    147: 124,
    148: 123,
    149: 122
}


rotations_24 = (
    (),
    ("y",),
    ("y'",),
    ("y", "y"),

    ("x", "x"),
    ("x", "x", "y"),
    ("x", "x", "y'"),
    ("x", "x", "y", "y"),

    ("y'", "x"),
    ("y'", "x", "y"),
    ("y'", "x", "y'"),
    ("y'", "x", "y", "y"),

    ("x",),
    ("x", "y"),
    ("x", "y'"),
    ("x", "y", "y"),

    ("y", "x"),
    ("y", "x", "y"),
    ("y", "x", "y'"),
    ("y", "x", "y", "y"),

    ("x'",),
    ("x'", "y"),
    ("x'", "y'"),
    ("x'", "y", "y")
)


class NoEdgeSolution(Exception):
    pass


class LookupTable555UDTCenterStage(LookupTable):
    """
    There are 4 T-centers and 4 X-centers so (24!/(8! * 16!))^2 is 540,917,591,841
    We cannot build a table that large so we will build it 7 moves deep and use
    IDA with T-centers and X-centers as our prune tables. Both the T-centers and
    X-centers prune tables will have 735,471 entries, 735,471/540,917,591,841
    is 0.000 001 3596729171 which is a decent percentage for IDA.

    lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.txt
    ============================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 66 entries (0 percent, 13.20x previous step)
    3 steps has 900 entries (0 percent, 13.64x previous step)
    4 steps has 9,626 entries (1 percent, 10.70x previous step)
    5 steps has 80,202 entries (10 percent, 8.33x previous step)
    6 steps has 329,202 entries (44 percent, 4.10x previous step)
    7 steps has 302,146 entries (41 percent, 0.92x previous step)
    8 steps has 13,324 entries (1 percent, 0.04x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.txt',
            'f0000f',
            linecount=735471,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in t_centers_555])
        return self.hex_format % int(result, 2)


class LookupTable555UDXCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.txt
    ============================================================
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
            'lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.txt',
            'f0000f',
            linecount=735471,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in x_centers_555])
        return self.hex_format % int(result, 2)


class LookupTableIDA555UDCentersStage(LookupTableIDA):
    """
    lookup-table-5x5x5-step10-UD-centers-stage.txt
    ==============================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 98 entries (0 percent, 19.60x previous step)
    3 steps has 2,036 entries (0 percent, 20.78x previous step)
    4 steps has 41,096 entries (0 percent, 20.18x previous step)
    5 steps has 824,950 entries (4 percent, 20.07x previous step)
    6 steps has 16,300,291 entries (94 percent, 19.76x previous step)

    Total: 17,168,476 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step10-UD-centers-stage.txt',
            '3fe000000001ff',
            moves_555,
            (), # illegal_moves

            # prune tables
            (parent.lt_UD_T_centers_stage,
             parent.lt_UD_X_centers_stage),

            linecount=17168476,
            max_depth=6,
            filesize=669570564)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in centers_555])
        return self.hex_format % int(result, 2)


class LookupTable555LRCentersStage(LookupTable):
    """
    lookup-table-5x5x5-step20-LR-centers-stage.txt
    ==============================================
    1 steps has 3 entries (0 percent)
    2 steps has 33 entries (0 percent)
    3 steps has 374 entries (0 percent)
    4 steps has 3,838 entries (0 percent)
    5 steps has 39,254 entries (0 percent)
    6 steps has 387,357 entries (0 percent)
    7 steps has 3,374,380 entries (2 percent)
    8 steps has 20,851,334 entries (12 percent)
    9 steps has 65,556,972 entries (39 percent)
    10 steps has 66,986,957 entries (40 percent)
    11 steps has 8,423,610 entries (5 percent)
    12 steps has 12,788 entries (0 percent)

    Total: 165,636,900 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step20-LR-centers-stage.txt',
            'ff803fe00',
            linecount=165636900)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in LFRB_centers_555])
        return self.hex_format % int(result, 2)


class LookupTable555LRTCenterStage(LookupTable):
    """
    This is only used when an NxNxN even cube is solving the plus sign
    by reducing to a 6x6x6 which in turn reduces to a 5x5x5.

    lookup-table-5x5x5-step21-LR-t-centers-solve.txt
    ================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 25 entries (0 percent, 8.33x previous step)
    3 steps has 210 entries (1 percent, 8.40x previous step)
    4 steps has 722 entries (5 percent, 3.44x previous step)
    5 steps has 1,752 entries (13 percent, 2.43x previous step)
    6 steps has 4,033 entries (31 percent, 2.30x previous step)
    7 steps has 4,014 entries (31 percent, 1.00x previous step)
    8 steps has 1,977 entries (15 percent, 0.49x previous step)
    9 steps has 134 entries (1 percent, 0.07x previous step)

    Total: 12,870 entries
    Average: 6.34 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step21-LR-t-centers-solve.txt',
            'f0f0',
            linecount=12870,
            max_depth=9)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in LFRB_t_centers_555])
        return self.hex_format % int(result, 2)


class LookupTableULCentersSolve(LookupTableHashCostOnly):
    """
    This tables solves sides U and L which in turn also solve D and R.  When
    the table was built the Ls were replaced with Us so that we were left with
    only 'U' and 'x' squares so that we could save the states in hex which
    makes the table take up much less disk space.

    lookup-table-5x5x5-step31-UL-centers-solve.txt
    ==============================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 71 entries (0 percent, 10.14x previous step)
    3 steps has 630 entries (0 percent, 8.87x previous step)
    4 steps has 4,639 entries (0 percent, 7.36x previous step)
    5 steps has 32,060 entries (0 percent, 6.91x previous step)
    6 steps has 198,779 entries (0 percent, 6.20x previous step)
    7 steps has 1,011,284 entries (4 percent, 5.09x previous step)
    8 steps has 3,826,966 entries (15 percent, 3.78x previous step)
    9 steps has 8,611,512 entries (35 percent, 2.25x previous step)
    10 steps has 8,194,244 entries (34 percent, 0.95x previous step)
    11 steps has 2,062,640 entries (8 percent, 0.25x previous step)
    12 steps has 67,152 entries (0 percent, 0.03x previous step)
    13 steps has 16 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    """

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step31-UL-centers-solve.hash-cost-only.txt',
            '3ffff000000000',
            linecount=24010000,
            max_depth=13,
            bucketcount=48020003)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'L') else '0' for x in centers_555])
        return self.hex_format % int(result, 2)


class LookupTableUFCentersSolve(LookupTableHashCostOnly):
    """
    This tables solves sides U and F which in turn also solve D and B.  When
    the table was built the Fs were replaced with Us so that we were left with
    only 'U' and 'x' squares so that we could save the states in hex which
    makes the table take up much less disk space.

    lookup-table-5x5x5-step33-UF-centers-solve.txt
    ==============================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 71 entries (0 percent, 10.14x previous step)
    3 steps has 630 entries (0 percent, 8.87x previous step)
    4 steps has 4,639 entries (0 percent, 7.36x previous step)
    5 steps has 32,060 entries (0 percent, 6.91x previous step)
    6 steps has 198,779 entries (0 percent, 6.20x previous step)
    7 steps has 1,011,284 entries (4 percent, 5.09x previous step)
    8 steps has 3,826,966 entries (15 percent, 3.78x previous step)
    9 steps has 8,611,512 entries (35 percent, 2.25x previous step)
    10 steps has 8,194,244 entries (34 percent, 0.95x previous step)
    11 steps has 2,062,640 entries (8 percent, 0.25x previous step)
    12 steps has 67,152 entries (0 percent, 0.03x previous step)
    13 steps has 16 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    """

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step33-UF-centers-solve.hash-cost-only.txt',
            '3fe00ff8000000',
            linecount=24010000,
            max_depth=13,
            bucketcount=48020003)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'F') else '0' for x in centers_555])
        return self.hex_format % int(result, 2)


class LookupTableIDA555ULFRBDCentersSolve(LookupTableIDA):
    """
    24,010,000/117,649,000,000 is 0.000204082 so this will be a fast IDA search

    lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt
    ==================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 99 entries (0 percent, 14.14x previous step)
    3 steps has 1,134 entries (0 percent, 11.45x previous step)
    4 steps has 12,183 entries (8 percent, 10.74x previous step)
    5 steps has 128,730 entries (90 percent, 10.57x previous step)

    Total: 142,153 entries
    Average: 4.90 moves
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt',
            'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD',
            moves_555,

            # These moves would destroy the staged centers
            ("Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'"),

            # prune tables
            (parent.lt_UL_centers_solve,
             parent.lt_UF_centers_solve),
            linecount=142153,
            max_depth=5,
            filesize=10661475)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in centers_555])
        return result


LR_edges_recolor_tuples_555 = (
    ('8', 31, 110), # left
    ('9', 35, 56),
    ('a', 41, 120),
    ('b', 45, 66),

    ('c', 81, 60), # right
    ('d', 85, 106),
    ('e', 91, 70),
    ('f', 95, 116),
)

LR_midges_recolor_tuples_555 = (
    ('s', 36, 115), # left
    ('t', 40, 61),
    ('u', 86, 65),  # right
    ('v', 90, 111),
)

def LR_edges_recolor_pattern_555(state):
    midges_map = {
        'BD': None,
        'BL': None,
        'BR': None,
        'BU': None,
        'DF': None,
        'DL': None,
        'DR': None,
        'FL': None,
        'FR': None,
        'FU': None,
        'LU': None,
        'RU': None
    }

    for (edge_index, square_index, partner_index) in LR_midges_recolor_tuples_555:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))
        midges_map[wing_str] = edge_index

        # We need to indicate which way the midge is rotated.  If the square_index contains
        # U, D, L, or R use the uppercase of the edge_index, if not use the lowercase of the
        # edge_index.
        if square_value == 'L':
            state[square_index] = edge_index.upper()
            state[partner_index] = edge_index.upper()
        elif partner_value == 'L':
            state[square_index] = edge_index
            state[partner_index] = edge_index
        elif square_value == 'R':
            state[square_index] = edge_index.upper()
            state[partner_index] = edge_index.upper()
        elif partner_value == 'R':
            state[square_index] = edge_index
            state[partner_index] = edge_index
        else:
            raise Exception("We should not be here")

    # Where is the midge for each high/low wing?
    for (edge_index, square_index, partner_index) in LR_edges_recolor_tuples_555:
        square_value = state[square_index]
        partner_value = state[partner_index]

        high_low = tsai_phase2_orient_edges_555[(square_index, partner_index, square_value, partner_value)]
        wing_str = ''.join(sorted([square_value, partner_value]))

        # If this is a high wing use the uppercase of the midge edge_index
        if high_low == 'U':
            state[square_index] = midges_map[wing_str].upper()
            state[partner_index] = midges_map[wing_str].upper()

        # If this is a low wing use the lowercase of the midge edge_index
        elif high_low == 'D':
            state[square_index] = midges_map[wing_str]
            state[partner_index] = midges_map[wing_str]

        else:
            raise Exception("(%s, %s, %s, %) high_low is %s" % (square_index, partner_index, square_value, partner_value, high_low))

    return ''.join(state)


class LookupTable555StageFirstFourEdges(LookupTable):
    """
    lookup-table-5x5x5-step100-stage-first-four-edges.txt
    =====================================================
    5 steps has 384 entries (0 percent, 0.00x previous step)
    6 steps has 5,032 entries (0 percent, 13.10x previous step)
    7 steps has 40,712 entries (0 percent, 8.09x previous step)
    8 steps has 136,236 entries (2 percent, 3.35x previous step)
    9 steps has 1,034,328 entries (19 percent, 7.59x previous step)
    10 steps has 3,997,220 entries (76 percent, 3.86x previous step)

    Total: 5,213,912 entries
    Average: 9.721709 moves

    There is no need to build this any deeper...that and building it
    to 10-deep took about 2 days on a 12-core machine.
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step100-stage-first-four-edges.txt',
            'TBD',
            linecount=5213912)

    def state(self, wing_strs_to_stage):
        state = self.parent.state[:]

        for square_index in wings_555:
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = ''.join(sorted([square_value, partner_value]))

            if wing_str in wing_strs_to_stage:
                state[square_index] = 'L'
                state[partner_index] = 'L'
            else:
                state[square_index] = 'x'
                state[partner_index] = 'x'

        edges_state = ''.join([state[square_index] for square_index in wings_555])
        return edges_state


class LookupTable555StageSecondFourEdges(LookupTable):
    """
    lookup-table-5x5x5-step101-stage-second-four-edges.txt
    ======================================================
    5 steps has 32 entries (0 percent, 0.00x previous step)
    6 steps has 304 entries (0 percent, 9.50x previous step)
    7 steps has 1,208 entries (0 percent, 3.97x previous step)
    8 steps has 3,612 entries (1 percent, 2.99x previous step)
    9 steps has 12,856 entries (3 percent, 3.56x previous step)
    10 steps has 42,688 entries (12 percent, 3.32x previous step)
    11 steps has 89,194 entries (26 percent, 2.09x previous step)
    12 steps has 113,508 entries (33 percent, 1.27x previous step)
    13 steps has 74,720 entries (22 percent, 0.66x previous step)

    Total: 338,122 entries
    Average: 11.523977 moves

    This table should have 900,900 entries but I only built it
    13-deep...that is deep enough for what we need
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step101-stage-second-four-edges.txt',
            'TBD',
            linecount=338122)

    def state(self, wing_strs_to_stage):
        state = self.parent.state[:]

        for square_index in wings_555:
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = ''.join(sorted([square_value, partner_value]))

            if wing_str in wing_strs_to_stage:
                state[square_index] = 'U'
                state[partner_index] = 'U'
            else:
                state[square_index] = 'x'
                state[partner_index] = 'x'

        edges_state = ''.join([state[square_index] for square_index in wings_555])
        return edges_state


class LookupTable555PairLastFourEdges(LookupTable):
    """
    lookup-table-5x5x5-step102-pair-last-four-edges.txt
    ===================================================
    5 steps has 10 entries (0 percent, 0.00x previous step)
    6 steps has 45 entries (0 percent, 4.50x previous step)
    7 steps has 196 entries (0 percent, 4.36x previous step)
    8 steps has 452 entries (1 percent, 2.31x previous step)
    9 steps has 1,556 entries (3 percent, 3.44x previous step)
    10 steps has 3,740 entries (9 percent, 2.40x previous step)
    11 steps has 10,188 entries (25 percent, 2.72x previous step)
    12 steps has 16,778 entries (41 percent, 1.65x previous step)
    13 steps has 6,866 entries (17 percent, 0.41x previous step)
    14 steps has 488 entries (1 percent, 0.07x previous step)

    Total: 40,319 entries
    Average: 11.562936 moves
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step102-pair-last-four-edges.txt',
            'sSSTTtuUUVVv',
            linecount=40319)

    def state(self):
        parent_state = self.parent.state[:]

        # The lookup table was built using LB, LF, RF, and RB so we must re-color the
        # 4 colors currently on LB, LF, RF, and RB to really be LB, LF, RF, and RB
        LR_remap = {}
        LR_remap[(parent_state[36], parent_state[115])] = 'LB'
        LR_remap[(parent_state[115], parent_state[36])] = 'BL'

        LR_remap[(parent_state[40], parent_state[61])]  = 'LF'
        LR_remap[(parent_state[61], parent_state[40])]  = 'FL'

        LR_remap[(parent_state[86], parent_state[65])]  = 'RF'
        LR_remap[(parent_state[65], parent_state[86])]  = 'FR'

        LR_remap[(parent_state[90], parent_state[111])] = 'RB'
        LR_remap[(parent_state[111], parent_state[90])] = 'BR'

        #self.parent.print_cube()
        #log.info("LR_remap\n%s\n" % pformat(LR_remap))

        for (edge_index, square_index, partner_index) in LR_midges_recolor_tuples_555:
            square_value = parent_state[square_index]
            partner_value = parent_state[partner_index]

            if (square_value, partner_value) in LR_remap:
                parent_state[square_index] = LR_remap[(square_value, partner_value)][0]
                parent_state[partner_index] = LR_remap[(square_value, partner_value)][1]

            elif (partner_value, square_value) in LR_remap:
                parent_state[square_index] = LR_remap[(partner_value, square_value)][0]
                parent_state[partner_index] = LR_remap[(partner_value, square_value)][1]

        for (edge_index, square_index, partner_index) in LR_edges_recolor_tuples_555:
            square_value = parent_state[square_index]
            partner_value = parent_state[partner_index]

            if (square_value, partner_value) in LR_remap:
                parent_state[square_index] = LR_remap[(square_value, partner_value)][0]
                parent_state[partner_index] = LR_remap[(square_value, partner_value)][1]

            elif (partner_value, square_value) in LR_remap:
                parent_state[square_index] = LR_remap[(partner_value, square_value)][0]
                parent_state[partner_index] = LR_remap[(partner_value, square_value)][1]

        state = LR_edges_recolor_pattern_555(parent_state[:])

        result = ''.join(state[index] for index in (31, 36, 41, 35, 40, 45, 81, 86, 91, 85, 90, 95))
        return result


class LookupTable555TCenterSolve(LookupTable):
    """
    This is only used when a cube larger than 7x7x7 is being solved

    lookup-table-5x5x5-step32-ULFRBD-t-centers-solve.txt
    ====================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 99 entries (0 percent, 14.14x previous step)
    3 steps has 1,038 entries (0 percent, 10.48x previous step)
    4 steps has 8,463 entries (2 percent, 8.15x previous step)
    5 steps has 47,986 entries (13 percent, 5.67x previous step)
    6 steps has 146,658 entries (42 percent, 3.06x previous step)
    7 steps has 128,914 entries (37 percent, 0.88x previous step)
    8 steps has 9,835 entries (2 percent, 0.08x previous step)

    Total: 343,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step32-ULFRBD-t-centers-solve.txt',
            'xUxUUUxUxxLxLLLxLxxFxFFFxFxxRxRRRxRxxBxBBBxBxxDxDDDxDx',
            linecount=343000)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            'x', parent_state[8], 'x',
            parent_state[12], parent_state[13], parent_state[14],
            'x', parent_state[18], 'x',

            # Left
            'x', parent_state[33], 'x',
            parent_state[37], parent_state[38], parent_state[39],
            'x', parent_state[43], 'x',

            # Front
            'x', parent_state[58], 'x',
            parent_state[62], parent_state[63], parent_state[64],
            'x', parent_state[68], 'x',

            # Right
            'x', parent_state[83], 'x',
            parent_state[87], parent_state[88], parent_state[89],
            'x', parent_state[93], 'x',

            # Back
            'x', parent_state[108], 'x',
            parent_state[112], parent_state[113], parent_state[114],
            'x', parent_state[118], 'x',

            # Down
            'x', parent_state[133], 'x',
            parent_state[137], parent_state[138], parent_state[139],
            'x', parent_state[143], 'x'
        ]

        result = ''.join(result)
        return result


class LookupTable555LRTCenterSolve(LookupTable):
    """
    Only used by 7x7x7 to speed up its step80 IDA search

    lookup-table-5x5x5-step40-LR-t-centers-solve.txt
    ================================================
    1 steps has 5 entries (7 percent, 0.00x previous step)
    2 steps has 18 entries (25 percent, 3.60x previous step)
    3 steps has 34 entries (48 percent, 1.89x previous step)
    4 steps has 13 entries (18 percent, 0.38x previous step)

    Total: 70 entries
    Average: 2.785714 moves
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step40-LR-t-centers-solve.txt',
            'LLLLRRRR',
            linecount=70)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Left
            parent_state[33],
            parent_state[37], parent_state[39],
            parent_state[43],

            # Right
            parent_state[83],
            parent_state[87], parent_state[89],
            parent_state[93],
        ]

        result = ''.join(result)
        return result


class RubiksCube555(RubiksCube):
    """
    5x5x5 strategy
    - stage UD centers to sides U or D (use IDA)
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3
    """
    instantiated = False

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCube.__init__(self, state, order, colormap)

        # This will be True when an even cube is using the 555 edge solver
        # to pair an orbit of edges
        self.avoid_pll = False

        if RubiksCube555.instantiated:
            #raise Exception("Another 5x5x5 instance is being created")
            log.warning("Another 5x5x5 instance is being created")
        else:
            RubiksCube555.instantiated = True

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
        centers = (13, 38, 63, 88, 113, 138)

        self._sanity_check('edge-orbit-0', edge_orbit_0_555, 8)
        self._sanity_check('edge-orbit-1', edge_orbit_1_555, 4)
        self._sanity_check('corners', corners_555, 4)
        self._sanity_check('x-centers', x_centers_555, 4)
        self._sanity_check('t-centers', t_centers_555, 4)
        self._sanity_check('centers', centers, 1)

    def rotate(self, step):
        """
        The 5x5x5 solver calls rotate() much more than other solvers, this is
        due to the edge-pairing code.  In order to speed up edge-pairing use
        the faster rotate_555() instead of RubiksCube.rotate()
        """
        self.state = rotate_555(self.state[:], step)
        self.solution.append(step)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_UD_T_centers_stage = LookupTable555UDTCenterStage(self)
        self.lt_UD_X_centers_stage = LookupTable555UDXCenterStage(self)
        self.lt_UD_centers_stage = LookupTableIDA555UDCentersStage(self)
        self.lt_UD_T_centers_stage.preload_cache_dict()
        self.lt_UD_X_centers_stage.preload_cache_dict()

        # Some stats for the various ways we can preload lt_UD_centers_stage
        #
        # list
        # Memory : 1,142,951,936 bytes
        # 22989 nodes-per-sec
        #
        # dict
        # Memory : 2,799,235,072 bytes
        # 29441 nodes-per-sec
        #
        # set
        # Memory : 2,139,684,864 bytes
        # 28203 nodes-per-sec
        #
        #self.lt_UD_centers_stage.preload_cache_list()
        #self.lt_UD_centers_stage.preload_cache_dict()
        self.lt_UD_centers_stage.preload_cache_set()

        self.lt_LR_centers_stage = LookupTable555LRCentersStage(self)

        self.lt_UL_centers_solve = LookupTableULCentersSolve(self)
        self.lt_UF_centers_solve = LookupTableUFCentersSolve(self)
        self.lt_ULFRB_centers_solve = LookupTableIDA555ULFRBDCentersSolve(self)
        self.lt_ULFRB_centers_solve.preload_cache_dict()

        self.lt_edges_stage_first_four = LookupTable555StageFirstFourEdges(self)
        self.lt_edges_stage_second_four = LookupTable555StageSecondFourEdges(self)
        self.lt_edges_stage_second_four.preload_cache_dict()
        self.lt_edges_pair_last_four = LookupTable555PairLastFourEdges(self)
        self.lt_edges_pair_last_four.preload_cache_dict()

        self.lt_ULFRBD_t_centers_solve = LookupTable555TCenterSolve(self)

        self.lt_LR_T_centers_stage = LookupTable555LRTCenterStage(self)
        self.lt_LR_T_centers_solve = LookupTable555LRTCenterSolve(self)

    def high_low_state(self, x, y, state_x, state_y, wing_str):
        """
        Return U if this is a high edge, D if it is a low edge
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Nuke everything except the one wing we are interested in
        self.nuke_corners()
        self.nuke_centers()
        self.nuke_edges()

        self.state[x] = state_x
        self.state[y] = state_y

        # Now move that wing to its home edge
        if wing_str.startswith('U'):

            if wing_str == 'UB':
                self.move_wing_to_U_north(x)
                high_edge_index = 2
                low_edge_index = 4

            elif wing_str == 'UL':
                self.move_wing_to_U_west(x)
                high_edge_index = 16
                low_edge_index = 6

            elif wing_str == 'UR':
                self.move_wing_to_U_east(x)
                high_edge_index = 10
                low_edge_index = 20

            elif wing_str == 'UF':
                self.move_wing_to_U_south(x)
                high_edge_index = 24
                low_edge_index = 22

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == 'U':
                result = 'U'
            elif self.state[low_edge_index] == 'U':
                result = 'D'
            elif self.state[high_edge_index] == 'x':
                result = 'U'
            elif self.state[low_edge_index] == 'x':
                result = 'D'
            else:
                self.print_cube()
                raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                    (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        elif wing_str.startswith('L'):

            if wing_str == 'LB':
                self.move_wing_to_L_west(x)
                high_edge_index = 41
                low_edge_index = 31

            elif wing_str == 'LF':
                self.move_wing_to_L_east(x)
                high_edge_index = 35
                low_edge_index = 45

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == 'L':
                result = 'U'
            elif self.state[low_edge_index] == 'L':
                result = 'D'
            elif self.state[high_edge_index] == 'x':
                result = 'U'
            elif self.state[low_edge_index] == 'x':
                result = 'D'
            else:
                self.print_cube()
                raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                    (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        elif wing_str.startswith('R'):

            if wing_str == 'RB':
                self.move_wing_to_R_east(x)
                high_edge_index = 85
                low_edge_index = 95

            elif wing_str == 'RF':
                self.move_wing_to_R_west(x)
                high_edge_index = 91
                low_edge_index = 81

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == 'R':
                result = 'U'
            elif self.state[low_edge_index] == 'R':
                result = 'D'
            elif self.state[high_edge_index] == 'x':
                result = 'U'
            elif self.state[low_edge_index] == 'x':
                result = 'D'
            else:
                self.print_cube()
                raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                    (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        elif wing_str.startswith('D'):
            if wing_str == 'DB':
                self.move_wing_to_D_south(x)
                high_edge_index = 149
                low_edge_index = 147

            elif wing_str == 'DL':
                self.move_wing_to_D_west(x)
                high_edge_index = 141
                low_edge_index = 131

            elif wing_str == 'DR':
                self.move_wing_to_D_east(x)
                high_edge_index = 135
                low_edge_index = 145

            elif wing_str == 'DF':
                self.move_wing_to_D_north(x)
                high_edge_index = 127
                low_edge_index = 129

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == 'D':
                result = 'U'
            elif self.state[low_edge_index] == 'D':
                result = 'D'
            elif self.state[high_edge_index] == 'x':
                result = 'U'
            elif self.state[low_edge_index] == 'x':
                result = 'D'
            else:
                self.print_cube()
                raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                    (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        else:
            raise Exception("invalid wing_str %s" % wing_str)

        self.state = original_state[:]
        self.solution = original_solution[:]

        assert result in ('U', 'D')
        return result

    def group_centers_stage_UD(self):
        """
        Stage UD centers.  The 7x7x7 uses this that is why it is in its own method.
        """
        # Test the prune tables
        #self.lt_UD_T_centers_stage.solve()
        #self.lt_UD_X_centers_stage.solve()

        self.lt_UD_centers_stage.solve()
        #self.print_cube()
        log.info("%s: UD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_centers_stage_LR(self):
        """
        Stage LR centers.  The 6x6x6 uses this that is why it is in its own method.
        """
        # Stage LR centers
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        self.lt_LR_centers_stage.solve()
        #self.print_cube()
        log.info("%s: ULFRBD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_centers_guts(self):
        self.lt_init()

        self.group_centers_stage_UD()
        self.group_centers_stage_LR()

        # All centers are staged, solve them
        self.lt_ULFRB_centers_solve.solve()
        log.info("%s: ULFRBD centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        #self.print_cube()

    def stage_first_four_edges_555(self):
        """
        There are 495 different permutations of 4-edges out of 12-edges, use the one
        that gives us the shortest solution for getting 4-edges staged to LB, LF, RF, RB
        """

        # return if they are already paired
        if (self.sideL.west_edge_paired() and self.sideL.east_edge_paired and
            self.sideR.west_edge_paired() and self.sideR.east_edge_paired):
            return

        min_solution_len = None
        min_solution_steps = None
        min_solution_wing_strs = None

        # The table for staging the first 4-edges would have 364,058,145 if built to completion.
        # Building that table the entire way is difficult though because this is a table where
        # the centers must be kept solved...so this involves building out a HUGE table and only
        # keeping the entries where the centers are solved.  To build one deep enough to find
        # all 364,058,145 entries needed that also have solved centers would probably take a
        # few months and more drive space than I have access to.
        #
        # To avoid building such a massive table we only build the table out 10-deep which gives
        # us a few million entries.  We then try all 495 permutations of 4-edges out of 12-edges
        # looking for one that does have a hit.  Most of the time this is all that is needed and
        # we can find a hit.  On the off chance that we cannot though we need a way to find a solution
        # so what we do is try all outer layer moves up to 3 moves deep and see if any of those
        # sequences put the cube in a state such that one of the 495 edge permurtations does find
        # a hit. I have yet to find a cube that cannot be solved with this approach but if I did
        # the pre_steps_to_try could be expanded to 4-deep.

        # Ran this once to generate pre_steps_to_try
        '''
        outer_layer_moves = (
            "U", "U'", "U2",
            "L", "L'", "L2",
            "F", "F'", "F2",
            "R", "R'", "R2",
            "B", "B'", "B2",
            "D", "D'", "D2",
        )
        pre_steps_to_try = []
        pre_steps_to_try.append([])

        for step in outer_layer_moves:
            pre_steps_to_try.append((step,))

        for step1 in outer_layer_moves:
            for step2 in outer_layer_moves:
                if not steps_on_same_face_and_layer(step1, step2):
                    pre_steps_to_try.append((step1, step2))

        for step1 in outer_layer_moves:
            for step2 in outer_layer_moves:
                if not steps_on_same_face_and_layer(step1, step2):

                    for step3 in outer_layer_moves:
                        if not steps_on_same_face_and_layer(step2, step3):
                            pre_steps_to_try.append((step1, step2, step3))

        from pprint import pformat
        log.info("pre_steps_to_try: %d" % len(pre_steps_to_try))
        log.info("pre_steps_to_try:\n%s\n" % pformat(pre_steps_to_try))
        sys.exit(0)

        # uncomment this if we ever find a cube that raises the
        # "Could not find 4-edges to stage" NoEdgeSolution exception below
        for step1 in outer_layer_moves:
            for step2 in outer_layer_moves:
                if not steps_on_same_face_and_layer(step1, step2):
                    for step3 in outer_layer_moves:
                        if not steps_on_same_face_and_layer(step2, step3):
                            for step4 in outer_layer_moves:
                                if not steps_on_same_face_and_layer(step3, step4):
                                    pre_steps_to_try.append([step1, step2, step3, step4])
        '''

        # Remember what things looked like
        original_state = self.state[:]
        original_solution = self.solution[:]

        for pre_steps in pre_steps_to_try:

            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in pre_steps:
                self.rotate(step)

            # do those steps
            for wing_strs in stage_first_four_edges_wing_str_combos:
                state = self.lt_edges_stage_first_four.state(wing_strs)
                steps = self.lt_edges_stage_first_four.steps(state)

                if steps:
                    log.info("%s: first four %s can be staged in %d steps" % (self, wing_strs, len(steps)))

                    if min_solution_len is None or len(steps) < min_solution_len:
                        min_solution_len = len(steps)
                        min_solution_steps = steps[:]
                        min_solution_wing_strs = wing_strs

            if min_solution_len is not None:
                if pre_steps:
                    log.warning("pre-steps %s required to find a hit" % ' '.join(pre_steps))

                self.stage_first_four_wing_strs = min_solution_wing_strs

                for step in min_solution_steps:
                    self.rotate(step)

                break
        else:
            raise NoEdgeSolution("Could not find 4-edges to stage")

    def stage_second_four_edges_555(self):
        """
        The first four edges have been staged to LB, LF, RF, RB. Stage the next four
        edges to UB, UF, DF, DB (this in turn stages the final four edges).

        Since there are 8-edges there are 70 different combinations of edges we can
        choose to stage to UB, UF, DF, DB. Walk through all 70 combinations and see
        which one leads to the shortest solution.  This accounts for the number of
        steps that will be needed in solve_staged_edges_555().
        """

        # return if they are already paired
        if (self.sideU.north_edge_paired() and self.sideU.south_edge_paired and
            self.sideD.north_edge_paired() and self.sideD.south_edge_paired):
            return

        # Remember what things looked like
        original_state = self.state[:]
        original_solution = self.solution[:]

        wing_strs_for_second_four = []

        for wing_str in wing_strs_all:
            if wing_str not in self.stage_first_four_wing_strs:
                wing_strs_for_second_four.append(wing_str)

        min_solution_len = None
        min_solution_steps = None

        for wing_strs in itertools.combinations(wing_strs_for_second_four, 4):
            state = self.lt_edges_stage_second_four.state(wing_strs)
            steps = self.lt_edges_stage_second_four.steps(state)

            if steps:

                for step in steps:
                    self.rotate(step)

                self.solve_staged_edges_555(False)
                solution_len = self.get_solution_len_minus_rotates(self.solution)
                log.info("%s: second four %s can be staged in %d steps (edges pair in %d steps)" % (self, wing_strs, len(steps), solution_len))

                if min_solution_len is None or solution_len < min_solution_len:
                    min_solution_len = solution_len
                    min_solution_steps = steps[:]
                    log.info("NEW MIN: %s steps" % solution_len)

                self.state = original_state[:]
                self.solution = original_solution[:]

        self.state = original_state[:]
        self.solution = original_solution[:]


        if min_solution_len is None:
            raise SolveError("Could not find 4-edges to stage")
        else:
            for step in min_solution_steps:
                self.rotate(step)

    def solve_staged_edges_555(self, log_msgs):
        """
        All edges are staged so that we can use the L4E table on each.  The order
        that the edges are solved in can make a small difference in move count.

        We only need to rotate the cube around a few ways (opening rotation), solve
        all three planes of edges and see which opening rotation results in the
        lowest move count.
        """

        # Remember what things looked like
        original_state = self.state[:]
        original_solution = self.solution[:]

        min_solution_len = None
        min_solution_steps = None

        for steps in rotations_24:

            for step in steps:
                self.rotate(step)

            self.lt_edges_pair_last_four.solve()

            self.rotate("x")
            self.lt_edges_pair_last_four.solve()

            self.rotate("z'")
            self.lt_edges_pair_last_four.solve()

            solution_len = self.get_solution_len_minus_rotates(self.solution)

            if min_solution_len is None or solution_len < min_solution_len:
                min_solution_len = solution_len
                min_solution_steps = steps[:]

            self.state = original_state[:]
            self.solution = original_solution[:]

        for step in min_solution_steps:
            self.rotate(step)

        self.lt_edges_pair_last_four.solve()

        if log_msgs:
            #self.print_cube()
            log.info("%s: first four edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))


        self.rotate("x")
        self.lt_edges_pair_last_four.solve()

        if log_msgs:
            #self.print_cube()
            log.info("%s: second four edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))


        self.rotate("z'")
        self.lt_edges_pair_last_four.solve()

        if log_msgs:
            self.print_cube()
            log.info("%s: all edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_edges(self):

        if self.edges_paired():
            self.solution.append('EDGES_GROUPED')
            return

        self.lt_init()

        #self.print_cube()
        self.stage_first_four_edges_555()
        self.print_cube()
        log.info("%s: first four edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.stage_second_four_edges_555()
        self.print_cube()
        log.info("%s: all edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.solve_staged_edges_555(True)

        # 9x9x9 test cube with old way took 83s and 164 moves to pair edges
        # 9x9x9 test cube with new way took 23s and 153 moves to pair edges
        log.info("%s: edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.solution.append('EDGES_GROUPED')


tsai_phase2_orient_edges_555 = {
    (2, 104, 'B', 'D'): 'D',
    (2, 104, 'B', 'L'): 'D',
    (2, 104, 'B', 'R'): 'D',
    (2, 104, 'B', 'U'): 'D',
    (2, 104, 'D', 'B'): 'U',
    (2, 104, 'D', 'F'): 'U',
    (2, 104, 'D', 'L'): 'U',
    (2, 104, 'D', 'R'): 'U',
    (2, 104, 'F', 'D'): 'D',
    (2, 104, 'F', 'L'): 'D',
    (2, 104, 'F', 'R'): 'D',
    (2, 104, 'F', 'U'): 'D',
    (2, 104, 'L', 'B'): 'U',
    (2, 104, 'L', 'D'): 'D',
    (2, 104, 'L', 'F'): 'U',
    (2, 104, 'L', 'U'): 'D',
    (2, 104, 'R', 'B'): 'U',
    (2, 104, 'R', 'D'): 'D',
    (2, 104, 'R', 'F'): 'U',
    (2, 104, 'R', 'U'): 'D',
    (2, 104, 'U', 'B'): 'U',
    (2, 104, 'U', 'F'): 'U',
    (2, 104, 'U', 'L'): 'U',
    (2, 104, 'U', 'R'): 'U',
    (4, 102, 'B', 'D'): 'U',
    (4, 102, 'B', 'L'): 'U',
    (4, 102, 'B', 'R'): 'U',
    (4, 102, 'B', 'U'): 'U',
    (4, 102, 'D', 'B'): 'D',
    (4, 102, 'D', 'F'): 'D',
    (4, 102, 'D', 'L'): 'D',
    (4, 102, 'D', 'R'): 'D',
    (4, 102, 'F', 'D'): 'U',
    (4, 102, 'F', 'L'): 'U',
    (4, 102, 'F', 'R'): 'U',
    (4, 102, 'F', 'U'): 'U',
    (4, 102, 'L', 'B'): 'D',
    (4, 102, 'L', 'D'): 'U',
    (4, 102, 'L', 'F'): 'D',
    (4, 102, 'L', 'U'): 'U',
    (4, 102, 'R', 'B'): 'D',
    (4, 102, 'R', 'D'): 'U',
    (4, 102, 'R', 'F'): 'D',
    (4, 102, 'R', 'U'): 'U',
    (4, 102, 'U', 'B'): 'D',
    (4, 102, 'U', 'F'): 'D',
    (4, 102, 'U', 'L'): 'D',
    (4, 102, 'U', 'R'): 'D',
    (6, 27, 'B', 'D'): 'U',
    (6, 27, 'B', 'L'): 'U',
    (6, 27, 'B', 'R'): 'U',
    (6, 27, 'B', 'U'): 'U',
    (6, 27, 'D', 'B'): 'D',
    (6, 27, 'D', 'F'): 'D',
    (6, 27, 'D', 'L'): 'D',
    (6, 27, 'D', 'R'): 'D',
    (6, 27, 'F', 'D'): 'U',
    (6, 27, 'F', 'L'): 'U',
    (6, 27, 'F', 'R'): 'U',
    (6, 27, 'F', 'U'): 'U',
    (6, 27, 'L', 'B'): 'D',
    (6, 27, 'L', 'D'): 'U',
    (6, 27, 'L', 'F'): 'D',
    (6, 27, 'L', 'U'): 'U',
    (6, 27, 'R', 'B'): 'D',
    (6, 27, 'R', 'D'): 'U',
    (6, 27, 'R', 'F'): 'D',
    (6, 27, 'R', 'U'): 'U',
    (6, 27, 'U', 'B'): 'D',
    (6, 27, 'U', 'F'): 'D',
    (6, 27, 'U', 'L'): 'D',
    (6, 27, 'U', 'R'): 'D',
    (10, 79, 'B', 'D'): 'D',
    (10, 79, 'B', 'L'): 'D',
    (10, 79, 'B', 'R'): 'D',
    (10, 79, 'B', 'U'): 'D',
    (10, 79, 'D', 'B'): 'U',
    (10, 79, 'D', 'F'): 'U',
    (10, 79, 'D', 'L'): 'U',
    (10, 79, 'D', 'R'): 'U',
    (10, 79, 'F', 'D'): 'D',
    (10, 79, 'F', 'L'): 'D',
    (10, 79, 'F', 'R'): 'D',
    (10, 79, 'F', 'U'): 'D',
    (10, 79, 'L', 'B'): 'U',
    (10, 79, 'L', 'D'): 'D',
    (10, 79, 'L', 'F'): 'U',
    (10, 79, 'L', 'U'): 'D',
    (10, 79, 'R', 'B'): 'U',
    (10, 79, 'R', 'D'): 'D',
    (10, 79, 'R', 'F'): 'U',
    (10, 79, 'R', 'U'): 'D',
    (10, 79, 'U', 'B'): 'U',
    (10, 79, 'U', 'F'): 'U',
    (10, 79, 'U', 'L'): 'U',
    (10, 79, 'U', 'R'): 'U',
    (16, 29, 'B', 'D'): 'D',
    (16, 29, 'B', 'L'): 'D',
    (16, 29, 'B', 'R'): 'D',
    (16, 29, 'B', 'U'): 'D',
    (16, 29, 'D', 'B'): 'U',
    (16, 29, 'D', 'F'): 'U',
    (16, 29, 'D', 'L'): 'U',
    (16, 29, 'D', 'R'): 'U',
    (16, 29, 'F', 'D'): 'D',
    (16, 29, 'F', 'L'): 'D',
    (16, 29, 'F', 'R'): 'D',
    (16, 29, 'F', 'U'): 'D',
    (16, 29, 'L', 'B'): 'U',
    (16, 29, 'L', 'D'): 'D',
    (16, 29, 'L', 'F'): 'U',
    (16, 29, 'L', 'U'): 'D',
    (16, 29, 'R', 'B'): 'U',
    (16, 29, 'R', 'D'): 'D',
    (16, 29, 'R', 'F'): 'U',
    (16, 29, 'R', 'U'): 'D',
    (16, 29, 'U', 'B'): 'U',
    (16, 29, 'U', 'F'): 'U',
    (16, 29, 'U', 'L'): 'U',
    (16, 29, 'U', 'R'): 'U',
    (20, 77, 'B', 'D'): 'U',
    (20, 77, 'B', 'L'): 'U',
    (20, 77, 'B', 'R'): 'U',
    (20, 77, 'B', 'U'): 'U',
    (20, 77, 'D', 'B'): 'D',
    (20, 77, 'D', 'F'): 'D',
    (20, 77, 'D', 'L'): 'D',
    (20, 77, 'D', 'R'): 'D',
    (20, 77, 'F', 'D'): 'U',
    (20, 77, 'F', 'L'): 'U',
    (20, 77, 'F', 'R'): 'U',
    (20, 77, 'F', 'U'): 'U',
    (20, 77, 'L', 'B'): 'D',
    (20, 77, 'L', 'D'): 'U',
    (20, 77, 'L', 'F'): 'D',
    (20, 77, 'L', 'U'): 'U',
    (20, 77, 'R', 'B'): 'D',
    (20, 77, 'R', 'D'): 'U',
    (20, 77, 'R', 'F'): 'D',
    (20, 77, 'R', 'U'): 'U',
    (20, 77, 'U', 'B'): 'D',
    (20, 77, 'U', 'F'): 'D',
    (20, 77, 'U', 'L'): 'D',
    (20, 77, 'U', 'R'): 'D',
    (22, 52, 'B', 'D'): 'U',
    (22, 52, 'B', 'L'): 'U',
    (22, 52, 'B', 'R'): 'U',
    (22, 52, 'B', 'U'): 'U',
    (22, 52, 'D', 'B'): 'D',
    (22, 52, 'D', 'F'): 'D',
    (22, 52, 'D', 'L'): 'D',
    (22, 52, 'D', 'R'): 'D',
    (22, 52, 'F', 'D'): 'U',
    (22, 52, 'F', 'L'): 'U',
    (22, 52, 'F', 'R'): 'U',
    (22, 52, 'F', 'U'): 'U',
    (22, 52, 'L', 'B'): 'D',
    (22, 52, 'L', 'D'): 'U',
    (22, 52, 'L', 'F'): 'D',
    (22, 52, 'L', 'U'): 'U',
    (22, 52, 'R', 'B'): 'D',
    (22, 52, 'R', 'D'): 'U',
    (22, 52, 'R', 'F'): 'D',
    (22, 52, 'R', 'U'): 'U',
    (22, 52, 'U', 'B'): 'D',
    (22, 52, 'U', 'F'): 'D',
    (22, 52, 'U', 'L'): 'D',
    (22, 52, 'U', 'R'): 'D',
    (24, 54, 'B', 'D'): 'D',
    (24, 54, 'B', 'L'): 'D',
    (24, 54, 'B', 'R'): 'D',
    (24, 54, 'B', 'U'): 'D',
    (24, 54, 'D', 'B'): 'U',
    (24, 54, 'D', 'F'): 'U',
    (24, 54, 'D', 'L'): 'U',
    (24, 54, 'D', 'R'): 'U',
    (24, 54, 'F', 'D'): 'D',
    (24, 54, 'F', 'L'): 'D',
    (24, 54, 'F', 'R'): 'D',
    (24, 54, 'F', 'U'): 'D',
    (24, 54, 'L', 'B'): 'U',
    (24, 54, 'L', 'D'): 'D',
    (24, 54, 'L', 'F'): 'U',
    (24, 54, 'L', 'U'): 'D',
    (24, 54, 'R', 'B'): 'U',
    (24, 54, 'R', 'D'): 'D',
    (24, 54, 'R', 'F'): 'U',
    (24, 54, 'R', 'U'): 'D',
    (24, 54, 'U', 'B'): 'U',
    (24, 54, 'U', 'F'): 'U',
    (24, 54, 'U', 'L'): 'U',
    (24, 54, 'U', 'R'): 'U',
    (27, 6, 'B', 'D'): 'D',
    (27, 6, 'B', 'L'): 'D',
    (27, 6, 'B', 'R'): 'D',
    (27, 6, 'B', 'U'): 'D',
    (27, 6, 'D', 'B'): 'U',
    (27, 6, 'D', 'F'): 'U',
    (27, 6, 'D', 'L'): 'U',
    (27, 6, 'D', 'R'): 'U',
    (27, 6, 'F', 'D'): 'D',
    (27, 6, 'F', 'L'): 'D',
    (27, 6, 'F', 'R'): 'D',
    (27, 6, 'F', 'U'): 'D',
    (27, 6, 'L', 'B'): 'U',
    (27, 6, 'L', 'D'): 'D',
    (27, 6, 'L', 'F'): 'U',
    (27, 6, 'L', 'U'): 'D',
    (27, 6, 'R', 'B'): 'U',
    (27, 6, 'R', 'D'): 'D',
    (27, 6, 'R', 'F'): 'U',
    (27, 6, 'R', 'U'): 'D',
    (27, 6, 'U', 'B'): 'U',
    (27, 6, 'U', 'F'): 'U',
    (27, 6, 'U', 'L'): 'U',
    (27, 6, 'U', 'R'): 'U',
    (29, 16, 'B', 'D'): 'U',
    (29, 16, 'B', 'L'): 'U',
    (29, 16, 'B', 'R'): 'U',
    (29, 16, 'B', 'U'): 'U',
    (29, 16, 'D', 'B'): 'D',
    (29, 16, 'D', 'F'): 'D',
    (29, 16, 'D', 'L'): 'D',
    (29, 16, 'D', 'R'): 'D',
    (29, 16, 'F', 'D'): 'U',
    (29, 16, 'F', 'L'): 'U',
    (29, 16, 'F', 'R'): 'U',
    (29, 16, 'F', 'U'): 'U',
    (29, 16, 'L', 'B'): 'D',
    (29, 16, 'L', 'D'): 'U',
    (29, 16, 'L', 'F'): 'D',
    (29, 16, 'L', 'U'): 'U',
    (29, 16, 'R', 'B'): 'D',
    (29, 16, 'R', 'D'): 'U',
    (29, 16, 'R', 'F'): 'D',
    (29, 16, 'R', 'U'): 'U',
    (29, 16, 'U', 'B'): 'D',
    (29, 16, 'U', 'F'): 'D',
    (29, 16, 'U', 'L'): 'D',
    (29, 16, 'U', 'R'): 'D',
    (31, 110, 'B', 'D'): 'U',
    (31, 110, 'B', 'L'): 'U',
    (31, 110, 'B', 'R'): 'U',
    (31, 110, 'B', 'U'): 'U',
    (31, 110, 'D', 'B'): 'D',
    (31, 110, 'D', 'F'): 'D',
    (31, 110, 'D', 'L'): 'D',
    (31, 110, 'D', 'R'): 'D',
    (31, 110, 'F', 'D'): 'U',
    (31, 110, 'F', 'L'): 'U',
    (31, 110, 'F', 'R'): 'U',
    (31, 110, 'F', 'U'): 'U',
    (31, 110, 'L', 'B'): 'D',
    (31, 110, 'L', 'D'): 'U',
    (31, 110, 'L', 'F'): 'D',
    (31, 110, 'L', 'U'): 'U',
    (31, 110, 'R', 'B'): 'D',
    (31, 110, 'R', 'D'): 'U',
    (31, 110, 'R', 'F'): 'D',
    (31, 110, 'R', 'U'): 'U',
    (31, 110, 'U', 'B'): 'D',
    (31, 110, 'U', 'F'): 'D',
    (31, 110, 'U', 'L'): 'D',
    (31, 110, 'U', 'R'): 'D',
    (35, 56, 'B', 'D'): 'D',
    (35, 56, 'B', 'L'): 'D',
    (35, 56, 'B', 'R'): 'D',
    (35, 56, 'B', 'U'): 'D',
    (35, 56, 'D', 'B'): 'U',
    (35, 56, 'D', 'F'): 'U',
    (35, 56, 'D', 'L'): 'U',
    (35, 56, 'D', 'R'): 'U',
    (35, 56, 'F', 'D'): 'D',
    (35, 56, 'F', 'L'): 'D',
    (35, 56, 'F', 'R'): 'D',
    (35, 56, 'F', 'U'): 'D',
    (35, 56, 'L', 'B'): 'U',
    (35, 56, 'L', 'D'): 'D',
    (35, 56, 'L', 'F'): 'U',
    (35, 56, 'L', 'U'): 'D',
    (35, 56, 'R', 'B'): 'U',
    (35, 56, 'R', 'D'): 'D',
    (35, 56, 'R', 'F'): 'U',
    (35, 56, 'R', 'U'): 'D',
    (35, 56, 'U', 'B'): 'U',
    (35, 56, 'U', 'F'): 'U',
    (35, 56, 'U', 'L'): 'U',
    (35, 56, 'U', 'R'): 'U',
    (41, 120, 'B', 'D'): 'D',
    (41, 120, 'B', 'L'): 'D',
    (41, 120, 'B', 'R'): 'D',
    (41, 120, 'B', 'U'): 'D',
    (41, 120, 'D', 'B'): 'U',
    (41, 120, 'D', 'F'): 'U',
    (41, 120, 'D', 'L'): 'U',
    (41, 120, 'D', 'R'): 'U',
    (41, 120, 'F', 'D'): 'D',
    (41, 120, 'F', 'L'): 'D',
    (41, 120, 'F', 'R'): 'D',
    (41, 120, 'F', 'U'): 'D',
    (41, 120, 'L', 'B'): 'U',
    (41, 120, 'L', 'D'): 'D',
    (41, 120, 'L', 'F'): 'U',
    (41, 120, 'L', 'U'): 'D',
    (41, 120, 'R', 'B'): 'U',
    (41, 120, 'R', 'D'): 'D',
    (41, 120, 'R', 'F'): 'U',
    (41, 120, 'R', 'U'): 'D',
    (41, 120, 'U', 'B'): 'U',
    (41, 120, 'U', 'F'): 'U',
    (41, 120, 'U', 'L'): 'U',
    (41, 120, 'U', 'R'): 'U',
    (45, 66, 'B', 'D'): 'U',
    (45, 66, 'B', 'L'): 'U',
    (45, 66, 'B', 'R'): 'U',
    (45, 66, 'B', 'U'): 'U',
    (45, 66, 'D', 'B'): 'D',
    (45, 66, 'D', 'F'): 'D',
    (45, 66, 'D', 'L'): 'D',
    (45, 66, 'D', 'R'): 'D',
    (45, 66, 'F', 'D'): 'U',
    (45, 66, 'F', 'L'): 'U',
    (45, 66, 'F', 'R'): 'U',
    (45, 66, 'F', 'U'): 'U',
    (45, 66, 'L', 'B'): 'D',
    (45, 66, 'L', 'D'): 'U',
    (45, 66, 'L', 'F'): 'D',
    (45, 66, 'L', 'U'): 'U',
    (45, 66, 'R', 'B'): 'D',
    (45, 66, 'R', 'D'): 'U',
    (45, 66, 'R', 'F'): 'D',
    (45, 66, 'R', 'U'): 'U',
    (45, 66, 'U', 'B'): 'D',
    (45, 66, 'U', 'F'): 'D',
    (45, 66, 'U', 'L'): 'D',
    (45, 66, 'U', 'R'): 'D',
    (47, 141, 'B', 'D'): 'U',
    (47, 141, 'B', 'L'): 'U',
    (47, 141, 'B', 'R'): 'U',
    (47, 141, 'B', 'U'): 'U',
    (47, 141, 'D', 'B'): 'D',
    (47, 141, 'D', 'F'): 'D',
    (47, 141, 'D', 'L'): 'D',
    (47, 141, 'D', 'R'): 'D',
    (47, 141, 'F', 'D'): 'U',
    (47, 141, 'F', 'L'): 'U',
    (47, 141, 'F', 'R'): 'U',
    (47, 141, 'F', 'U'): 'U',
    (47, 141, 'L', 'B'): 'D',
    (47, 141, 'L', 'D'): 'U',
    (47, 141, 'L', 'F'): 'D',
    (47, 141, 'L', 'U'): 'U',
    (47, 141, 'R', 'B'): 'D',
    (47, 141, 'R', 'D'): 'U',
    (47, 141, 'R', 'F'): 'D',
    (47, 141, 'R', 'U'): 'U',
    (47, 141, 'U', 'B'): 'D',
    (47, 141, 'U', 'F'): 'D',
    (47, 141, 'U', 'L'): 'D',
    (47, 141, 'U', 'R'): 'D',
    (49, 131, 'B', 'D'): 'D',
    (49, 131, 'B', 'L'): 'D',
    (49, 131, 'B', 'R'): 'D',
    (49, 131, 'B', 'U'): 'D',
    (49, 131, 'D', 'B'): 'U',
    (49, 131, 'D', 'F'): 'U',
    (49, 131, 'D', 'L'): 'U',
    (49, 131, 'D', 'R'): 'U',
    (49, 131, 'F', 'D'): 'D',
    (49, 131, 'F', 'L'): 'D',
    (49, 131, 'F', 'R'): 'D',
    (49, 131, 'F', 'U'): 'D',
    (49, 131, 'L', 'B'): 'U',
    (49, 131, 'L', 'D'): 'D',
    (49, 131, 'L', 'F'): 'U',
    (49, 131, 'L', 'U'): 'D',
    (49, 131, 'R', 'B'): 'U',
    (49, 131, 'R', 'D'): 'D',
    (49, 131, 'R', 'F'): 'U',
    (49, 131, 'R', 'U'): 'D',
    (49, 131, 'U', 'B'): 'U',
    (49, 131, 'U', 'F'): 'U',
    (49, 131, 'U', 'L'): 'U',
    (49, 131, 'U', 'R'): 'U',
    (52, 22, 'B', 'D'): 'D',
    (52, 22, 'B', 'L'): 'D',
    (52, 22, 'B', 'R'): 'D',
    (52, 22, 'B', 'U'): 'D',
    (52, 22, 'D', 'B'): 'U',
    (52, 22, 'D', 'F'): 'U',
    (52, 22, 'D', 'L'): 'U',
    (52, 22, 'D', 'R'): 'U',
    (52, 22, 'F', 'D'): 'D',
    (52, 22, 'F', 'L'): 'D',
    (52, 22, 'F', 'R'): 'D',
    (52, 22, 'F', 'U'): 'D',
    (52, 22, 'L', 'B'): 'U',
    (52, 22, 'L', 'D'): 'D',
    (52, 22, 'L', 'F'): 'U',
    (52, 22, 'L', 'U'): 'D',
    (52, 22, 'R', 'B'): 'U',
    (52, 22, 'R', 'D'): 'D',
    (52, 22, 'R', 'F'): 'U',
    (52, 22, 'R', 'U'): 'D',
    (52, 22, 'U', 'B'): 'U',
    (52, 22, 'U', 'F'): 'U',
    (52, 22, 'U', 'L'): 'U',
    (52, 22, 'U', 'R'): 'U',
    (54, 24, 'B', 'D'): 'U',
    (54, 24, 'B', 'L'): 'U',
    (54, 24, 'B', 'R'): 'U',
    (54, 24, 'B', 'U'): 'U',
    (54, 24, 'D', 'B'): 'D',
    (54, 24, 'D', 'F'): 'D',
    (54, 24, 'D', 'L'): 'D',
    (54, 24, 'D', 'R'): 'D',
    (54, 24, 'F', 'D'): 'U',
    (54, 24, 'F', 'L'): 'U',
    (54, 24, 'F', 'R'): 'U',
    (54, 24, 'F', 'U'): 'U',
    (54, 24, 'L', 'B'): 'D',
    (54, 24, 'L', 'D'): 'U',
    (54, 24, 'L', 'F'): 'D',
    (54, 24, 'L', 'U'): 'U',
    (54, 24, 'R', 'B'): 'D',
    (54, 24, 'R', 'D'): 'U',
    (54, 24, 'R', 'F'): 'D',
    (54, 24, 'R', 'U'): 'U',
    (54, 24, 'U', 'B'): 'D',
    (54, 24, 'U', 'F'): 'D',
    (54, 24, 'U', 'L'): 'D',
    (54, 24, 'U', 'R'): 'D',
    (56, 35, 'B', 'D'): 'U',
    (56, 35, 'B', 'L'): 'U',
    (56, 35, 'B', 'R'): 'U',
    (56, 35, 'B', 'U'): 'U',
    (56, 35, 'D', 'B'): 'D',
    (56, 35, 'D', 'F'): 'D',
    (56, 35, 'D', 'L'): 'D',
    (56, 35, 'D', 'R'): 'D',
    (56, 35, 'F', 'D'): 'U',
    (56, 35, 'F', 'L'): 'U',
    (56, 35, 'F', 'R'): 'U',
    (56, 35, 'F', 'U'): 'U',
    (56, 35, 'L', 'B'): 'D',
    (56, 35, 'L', 'D'): 'U',
    (56, 35, 'L', 'F'): 'D',
    (56, 35, 'L', 'U'): 'U',
    (56, 35, 'R', 'B'): 'D',
    (56, 35, 'R', 'D'): 'U',
    (56, 35, 'R', 'F'): 'D',
    (56, 35, 'R', 'U'): 'U',
    (56, 35, 'U', 'B'): 'D',
    (56, 35, 'U', 'F'): 'D',
    (56, 35, 'U', 'L'): 'D',
    (56, 35, 'U', 'R'): 'D',
    (60, 81, 'B', 'D'): 'D',
    (60, 81, 'B', 'L'): 'D',
    (60, 81, 'B', 'R'): 'D',
    (60, 81, 'B', 'U'): 'D',
    (60, 81, 'D', 'B'): 'U',
    (60, 81, 'D', 'F'): 'U',
    (60, 81, 'D', 'L'): 'U',
    (60, 81, 'D', 'R'): 'U',
    (60, 81, 'F', 'D'): 'D',
    (60, 81, 'F', 'L'): 'D',
    (60, 81, 'F', 'R'): 'D',
    (60, 81, 'F', 'U'): 'D',
    (60, 81, 'L', 'B'): 'U',
    (60, 81, 'L', 'D'): 'D',
    (60, 81, 'L', 'F'): 'U',
    (60, 81, 'L', 'U'): 'D',
    (60, 81, 'R', 'B'): 'U',
    (60, 81, 'R', 'D'): 'D',
    (60, 81, 'R', 'F'): 'U',
    (60, 81, 'R', 'U'): 'D',
    (60, 81, 'U', 'B'): 'U',
    (60, 81, 'U', 'F'): 'U',
    (60, 81, 'U', 'L'): 'U',
    (60, 81, 'U', 'R'): 'U',
    (66, 45, 'B', 'D'): 'D',
    (66, 45, 'B', 'L'): 'D',
    (66, 45, 'B', 'R'): 'D',
    (66, 45, 'B', 'U'): 'D',
    (66, 45, 'D', 'B'): 'U',
    (66, 45, 'D', 'F'): 'U',
    (66, 45, 'D', 'L'): 'U',
    (66, 45, 'D', 'R'): 'U',
    (66, 45, 'F', 'D'): 'D',
    (66, 45, 'F', 'L'): 'D',
    (66, 45, 'F', 'R'): 'D',
    (66, 45, 'F', 'U'): 'D',
    (66, 45, 'L', 'B'): 'U',
    (66, 45, 'L', 'D'): 'D',
    (66, 45, 'L', 'F'): 'U',
    (66, 45, 'L', 'U'): 'D',
    (66, 45, 'R', 'B'): 'U',
    (66, 45, 'R', 'D'): 'D',
    (66, 45, 'R', 'F'): 'U',
    (66, 45, 'R', 'U'): 'D',
    (66, 45, 'U', 'B'): 'U',
    (66, 45, 'U', 'F'): 'U',
    (66, 45, 'U', 'L'): 'U',
    (66, 45, 'U', 'R'): 'U',
    (70, 91, 'B', 'D'): 'U',
    (70, 91, 'B', 'L'): 'U',
    (70, 91, 'B', 'R'): 'U',
    (70, 91, 'B', 'U'): 'U',
    (70, 91, 'D', 'B'): 'D',
    (70, 91, 'D', 'F'): 'D',
    (70, 91, 'D', 'L'): 'D',
    (70, 91, 'D', 'R'): 'D',
    (70, 91, 'F', 'D'): 'U',
    (70, 91, 'F', 'L'): 'U',
    (70, 91, 'F', 'R'): 'U',
    (70, 91, 'F', 'U'): 'U',
    (70, 91, 'L', 'B'): 'D',
    (70, 91, 'L', 'D'): 'U',
    (70, 91, 'L', 'F'): 'D',
    (70, 91, 'L', 'U'): 'U',
    (70, 91, 'R', 'B'): 'D',
    (70, 91, 'R', 'D'): 'U',
    (70, 91, 'R', 'F'): 'D',
    (70, 91, 'R', 'U'): 'U',
    (70, 91, 'U', 'B'): 'D',
    (70, 91, 'U', 'F'): 'D',
    (70, 91, 'U', 'L'): 'D',
    (70, 91, 'U', 'R'): 'D',
    (72, 127, 'B', 'D'): 'U',
    (72, 127, 'B', 'L'): 'U',
    (72, 127, 'B', 'R'): 'U',
    (72, 127, 'B', 'U'): 'U',
    (72, 127, 'D', 'B'): 'D',
    (72, 127, 'D', 'F'): 'D',
    (72, 127, 'D', 'L'): 'D',
    (72, 127, 'D', 'R'): 'D',
    (72, 127, 'F', 'D'): 'U',
    (72, 127, 'F', 'L'): 'U',
    (72, 127, 'F', 'R'): 'U',
    (72, 127, 'F', 'U'): 'U',
    (72, 127, 'L', 'B'): 'D',
    (72, 127, 'L', 'D'): 'U',
    (72, 127, 'L', 'F'): 'D',
    (72, 127, 'L', 'U'): 'U',
    (72, 127, 'R', 'B'): 'D',
    (72, 127, 'R', 'D'): 'U',
    (72, 127, 'R', 'F'): 'D',
    (72, 127, 'R', 'U'): 'U',
    (72, 127, 'U', 'B'): 'D',
    (72, 127, 'U', 'F'): 'D',
    (72, 127, 'U', 'L'): 'D',
    (72, 127, 'U', 'R'): 'D',
    (74, 129, 'B', 'D'): 'D',
    (74, 129, 'B', 'L'): 'D',
    (74, 129, 'B', 'R'): 'D',
    (74, 129, 'B', 'U'): 'D',
    (74, 129, 'D', 'B'): 'U',
    (74, 129, 'D', 'F'): 'U',
    (74, 129, 'D', 'L'): 'U',
    (74, 129, 'D', 'R'): 'U',
    (74, 129, 'F', 'D'): 'D',
    (74, 129, 'F', 'L'): 'D',
    (74, 129, 'F', 'R'): 'D',
    (74, 129, 'F', 'U'): 'D',
    (74, 129, 'L', 'B'): 'U',
    (74, 129, 'L', 'D'): 'D',
    (74, 129, 'L', 'F'): 'U',
    (74, 129, 'L', 'U'): 'D',
    (74, 129, 'R', 'B'): 'U',
    (74, 129, 'R', 'D'): 'D',
    (74, 129, 'R', 'F'): 'U',
    (74, 129, 'R', 'U'): 'D',
    (74, 129, 'U', 'B'): 'U',
    (74, 129, 'U', 'F'): 'U',
    (74, 129, 'U', 'L'): 'U',
    (74, 129, 'U', 'R'): 'U',
    (77, 20, 'B', 'D'): 'D',
    (77, 20, 'B', 'L'): 'D',
    (77, 20, 'B', 'R'): 'D',
    (77, 20, 'B', 'U'): 'D',
    (77, 20, 'D', 'B'): 'U',
    (77, 20, 'D', 'F'): 'U',
    (77, 20, 'D', 'L'): 'U',
    (77, 20, 'D', 'R'): 'U',
    (77, 20, 'F', 'D'): 'D',
    (77, 20, 'F', 'L'): 'D',
    (77, 20, 'F', 'R'): 'D',
    (77, 20, 'F', 'U'): 'D',
    (77, 20, 'L', 'B'): 'U',
    (77, 20, 'L', 'D'): 'D',
    (77, 20, 'L', 'F'): 'U',
    (77, 20, 'L', 'U'): 'D',
    (77, 20, 'R', 'B'): 'U',
    (77, 20, 'R', 'D'): 'D',
    (77, 20, 'R', 'F'): 'U',
    (77, 20, 'R', 'U'): 'D',
    (77, 20, 'U', 'B'): 'U',
    (77, 20, 'U', 'F'): 'U',
    (77, 20, 'U', 'L'): 'U',
    (77, 20, 'U', 'R'): 'U',
    (79, 10, 'B', 'D'): 'U',
    (79, 10, 'B', 'L'): 'U',
    (79, 10, 'B', 'R'): 'U',
    (79, 10, 'B', 'U'): 'U',
    (79, 10, 'D', 'B'): 'D',
    (79, 10, 'D', 'F'): 'D',
    (79, 10, 'D', 'L'): 'D',
    (79, 10, 'D', 'R'): 'D',
    (79, 10, 'F', 'D'): 'U',
    (79, 10, 'F', 'L'): 'U',
    (79, 10, 'F', 'R'): 'U',
    (79, 10, 'F', 'U'): 'U',
    (79, 10, 'L', 'B'): 'D',
    (79, 10, 'L', 'D'): 'U',
    (79, 10, 'L', 'F'): 'D',
    (79, 10, 'L', 'U'): 'U',
    (79, 10, 'R', 'B'): 'D',
    (79, 10, 'R', 'D'): 'U',
    (79, 10, 'R', 'F'): 'D',
    (79, 10, 'R', 'U'): 'U',
    (79, 10, 'U', 'B'): 'D',
    (79, 10, 'U', 'F'): 'D',
    (79, 10, 'U', 'L'): 'D',
    (79, 10, 'U', 'R'): 'D',
    (81, 60, 'B', 'D'): 'U',
    (81, 60, 'B', 'L'): 'U',
    (81, 60, 'B', 'R'): 'U',
    (81, 60, 'B', 'U'): 'U',
    (81, 60, 'D', 'B'): 'D',
    (81, 60, 'D', 'F'): 'D',
    (81, 60, 'D', 'L'): 'D',
    (81, 60, 'D', 'R'): 'D',
    (81, 60, 'F', 'D'): 'U',
    (81, 60, 'F', 'L'): 'U',
    (81, 60, 'F', 'R'): 'U',
    (81, 60, 'F', 'U'): 'U',
    (81, 60, 'L', 'B'): 'D',
    (81, 60, 'L', 'D'): 'U',
    (81, 60, 'L', 'F'): 'D',
    (81, 60, 'L', 'U'): 'U',
    (81, 60, 'R', 'B'): 'D',
    (81, 60, 'R', 'D'): 'U',
    (81, 60, 'R', 'F'): 'D',
    (81, 60, 'R', 'U'): 'U',
    (81, 60, 'U', 'B'): 'D',
    (81, 60, 'U', 'F'): 'D',
    (81, 60, 'U', 'L'): 'D',
    (81, 60, 'U', 'R'): 'D',
    (85, 106, 'B', 'D'): 'D',
    (85, 106, 'B', 'L'): 'D',
    (85, 106, 'B', 'R'): 'D',
    (85, 106, 'B', 'U'): 'D',
    (85, 106, 'D', 'B'): 'U',
    (85, 106, 'D', 'F'): 'U',
    (85, 106, 'D', 'L'): 'U',
    (85, 106, 'D', 'R'): 'U',
    (85, 106, 'F', 'D'): 'D',
    (85, 106, 'F', 'L'): 'D',
    (85, 106, 'F', 'R'): 'D',
    (85, 106, 'F', 'U'): 'D',
    (85, 106, 'L', 'B'): 'U',
    (85, 106, 'L', 'D'): 'D',
    (85, 106, 'L', 'F'): 'U',
    (85, 106, 'L', 'U'): 'D',
    (85, 106, 'R', 'B'): 'U',
    (85, 106, 'R', 'D'): 'D',
    (85, 106, 'R', 'F'): 'U',
    (85, 106, 'R', 'U'): 'D',
    (85, 106, 'U', 'B'): 'U',
    (85, 106, 'U', 'F'): 'U',
    (85, 106, 'U', 'L'): 'U',
    (85, 106, 'U', 'R'): 'U',
    (91, 70, 'B', 'D'): 'D',
    (91, 70, 'B', 'L'): 'D',
    (91, 70, 'B', 'R'): 'D',
    (91, 70, 'B', 'U'): 'D',
    (91, 70, 'D', 'B'): 'U',
    (91, 70, 'D', 'F'): 'U',
    (91, 70, 'D', 'L'): 'U',
    (91, 70, 'D', 'R'): 'U',
    (91, 70, 'F', 'D'): 'D',
    (91, 70, 'F', 'L'): 'D',
    (91, 70, 'F', 'R'): 'D',
    (91, 70, 'F', 'U'): 'D',
    (91, 70, 'L', 'B'): 'U',
    (91, 70, 'L', 'D'): 'D',
    (91, 70, 'L', 'F'): 'U',
    (91, 70, 'L', 'U'): 'D',
    (91, 70, 'R', 'B'): 'U',
    (91, 70, 'R', 'D'): 'D',
    (91, 70, 'R', 'F'): 'U',
    (91, 70, 'R', 'U'): 'D',
    (91, 70, 'U', 'B'): 'U',
    (91, 70, 'U', 'F'): 'U',
    (91, 70, 'U', 'L'): 'U',
    (91, 70, 'U', 'R'): 'U',
    (95, 116, 'B', 'D'): 'U',
    (95, 116, 'B', 'L'): 'U',
    (95, 116, 'B', 'R'): 'U',
    (95, 116, 'B', 'U'): 'U',
    (95, 116, 'D', 'B'): 'D',
    (95, 116, 'D', 'F'): 'D',
    (95, 116, 'D', 'L'): 'D',
    (95, 116, 'D', 'R'): 'D',
    (95, 116, 'F', 'D'): 'U',
    (95, 116, 'F', 'L'): 'U',
    (95, 116, 'F', 'R'): 'U',
    (95, 116, 'F', 'U'): 'U',
    (95, 116, 'L', 'B'): 'D',
    (95, 116, 'L', 'D'): 'U',
    (95, 116, 'L', 'F'): 'D',
    (95, 116, 'L', 'U'): 'U',
    (95, 116, 'R', 'B'): 'D',
    (95, 116, 'R', 'D'): 'U',
    (95, 116, 'R', 'F'): 'D',
    (95, 116, 'R', 'U'): 'U',
    (95, 116, 'U', 'B'): 'D',
    (95, 116, 'U', 'F'): 'D',
    (95, 116, 'U', 'L'): 'D',
    (95, 116, 'U', 'R'): 'D',
    (97, 135, 'B', 'D'): 'U',
    (97, 135, 'B', 'L'): 'U',
    (97, 135, 'B', 'R'): 'U',
    (97, 135, 'B', 'U'): 'U',
    (97, 135, 'D', 'B'): 'D',
    (97, 135, 'D', 'F'): 'D',
    (97, 135, 'D', 'L'): 'D',
    (97, 135, 'D', 'R'): 'D',
    (97, 135, 'F', 'D'): 'U',
    (97, 135, 'F', 'L'): 'U',
    (97, 135, 'F', 'R'): 'U',
    (97, 135, 'F', 'U'): 'U',
    (97, 135, 'L', 'B'): 'D',
    (97, 135, 'L', 'D'): 'U',
    (97, 135, 'L', 'F'): 'D',
    (97, 135, 'L', 'U'): 'U',
    (97, 135, 'R', 'B'): 'D',
    (97, 135, 'R', 'D'): 'U',
    (97, 135, 'R', 'F'): 'D',
    (97, 135, 'R', 'U'): 'U',
    (97, 135, 'U', 'B'): 'D',
    (97, 135, 'U', 'F'): 'D',
    (97, 135, 'U', 'L'): 'D',
    (97, 135, 'U', 'R'): 'D',
    (99, 145, 'B', 'D'): 'D',
    (99, 145, 'B', 'L'): 'D',
    (99, 145, 'B', 'R'): 'D',
    (99, 145, 'B', 'U'): 'D',
    (99, 145, 'D', 'B'): 'U',
    (99, 145, 'D', 'F'): 'U',
    (99, 145, 'D', 'L'): 'U',
    (99, 145, 'D', 'R'): 'U',
    (99, 145, 'F', 'D'): 'D',
    (99, 145, 'F', 'L'): 'D',
    (99, 145, 'F', 'R'): 'D',
    (99, 145, 'F', 'U'): 'D',
    (99, 145, 'L', 'B'): 'U',
    (99, 145, 'L', 'D'): 'D',
    (99, 145, 'L', 'F'): 'U',
    (99, 145, 'L', 'U'): 'D',
    (99, 145, 'R', 'B'): 'U',
    (99, 145, 'R', 'D'): 'D',
    (99, 145, 'R', 'F'): 'U',
    (99, 145, 'R', 'U'): 'D',
    (99, 145, 'U', 'B'): 'U',
    (99, 145, 'U', 'F'): 'U',
    (99, 145, 'U', 'L'): 'U',
    (99, 145, 'U', 'R'): 'U',
    (102, 4, 'B', 'D'): 'D',
    (102, 4, 'B', 'L'): 'D',
    (102, 4, 'B', 'R'): 'D',
    (102, 4, 'B', 'U'): 'D',
    (102, 4, 'D', 'B'): 'U',
    (102, 4, 'D', 'F'): 'U',
    (102, 4, 'D', 'L'): 'U',
    (102, 4, 'D', 'R'): 'U',
    (102, 4, 'F', 'D'): 'D',
    (102, 4, 'F', 'L'): 'D',
    (102, 4, 'F', 'R'): 'D',
    (102, 4, 'F', 'U'): 'D',
    (102, 4, 'L', 'B'): 'U',
    (102, 4, 'L', 'D'): 'D',
    (102, 4, 'L', 'F'): 'U',
    (102, 4, 'L', 'U'): 'D',
    (102, 4, 'R', 'B'): 'U',
    (102, 4, 'R', 'D'): 'D',
    (102, 4, 'R', 'F'): 'U',
    (102, 4, 'R', 'U'): 'D',
    (102, 4, 'U', 'B'): 'U',
    (102, 4, 'U', 'F'): 'U',
    (102, 4, 'U', 'L'): 'U',
    (102, 4, 'U', 'R'): 'U',
    (104, 2, 'B', 'D'): 'U',
    (104, 2, 'B', 'L'): 'U',
    (104, 2, 'B', 'R'): 'U',
    (104, 2, 'B', 'U'): 'U',
    (104, 2, 'D', 'B'): 'D',
    (104, 2, 'D', 'F'): 'D',
    (104, 2, 'D', 'L'): 'D',
    (104, 2, 'D', 'R'): 'D',
    (104, 2, 'F', 'D'): 'U',
    (104, 2, 'F', 'L'): 'U',
    (104, 2, 'F', 'R'): 'U',
    (104, 2, 'F', 'U'): 'U',
    (104, 2, 'L', 'B'): 'D',
    (104, 2, 'L', 'D'): 'U',
    (104, 2, 'L', 'F'): 'D',
    (104, 2, 'L', 'U'): 'U',
    (104, 2, 'R', 'B'): 'D',
    (104, 2, 'R', 'D'): 'U',
    (104, 2, 'R', 'F'): 'D',
    (104, 2, 'R', 'U'): 'U',
    (104, 2, 'U', 'B'): 'D',
    (104, 2, 'U', 'F'): 'D',
    (104, 2, 'U', 'L'): 'D',
    (104, 2, 'U', 'R'): 'D',
    (106, 85, 'B', 'D'): 'U',
    (106, 85, 'B', 'L'): 'U',
    (106, 85, 'B', 'R'): 'U',
    (106, 85, 'B', 'U'): 'U',
    (106, 85, 'D', 'B'): 'D',
    (106, 85, 'D', 'F'): 'D',
    (106, 85, 'D', 'L'): 'D',
    (106, 85, 'D', 'R'): 'D',
    (106, 85, 'F', 'D'): 'U',
    (106, 85, 'F', 'L'): 'U',
    (106, 85, 'F', 'R'): 'U',
    (106, 85, 'F', 'U'): 'U',
    (106, 85, 'L', 'B'): 'D',
    (106, 85, 'L', 'D'): 'U',
    (106, 85, 'L', 'F'): 'D',
    (106, 85, 'L', 'U'): 'U',
    (106, 85, 'R', 'B'): 'D',
    (106, 85, 'R', 'D'): 'U',
    (106, 85, 'R', 'F'): 'D',
    (106, 85, 'R', 'U'): 'U',
    (106, 85, 'U', 'B'): 'D',
    (106, 85, 'U', 'F'): 'D',
    (106, 85, 'U', 'L'): 'D',
    (106, 85, 'U', 'R'): 'D',
    (110, 31, 'B', 'D'): 'D',
    (110, 31, 'B', 'L'): 'D',
    (110, 31, 'B', 'R'): 'D',
    (110, 31, 'B', 'U'): 'D',
    (110, 31, 'D', 'B'): 'U',
    (110, 31, 'D', 'F'): 'U',
    (110, 31, 'D', 'L'): 'U',
    (110, 31, 'D', 'R'): 'U',
    (110, 31, 'F', 'D'): 'D',
    (110, 31, 'F', 'L'): 'D',
    (110, 31, 'F', 'R'): 'D',
    (110, 31, 'F', 'U'): 'D',
    (110, 31, 'L', 'B'): 'U',
    (110, 31, 'L', 'D'): 'D',
    (110, 31, 'L', 'F'): 'U',
    (110, 31, 'L', 'U'): 'D',
    (110, 31, 'R', 'B'): 'U',
    (110, 31, 'R', 'D'): 'D',
    (110, 31, 'R', 'F'): 'U',
    (110, 31, 'R', 'U'): 'D',
    (110, 31, 'U', 'B'): 'U',
    (110, 31, 'U', 'F'): 'U',
    (110, 31, 'U', 'L'): 'U',
    (110, 31, 'U', 'R'): 'U',
    (116, 95, 'B', 'D'): 'D',
    (116, 95, 'B', 'L'): 'D',
    (116, 95, 'B', 'R'): 'D',
    (116, 95, 'B', 'U'): 'D',
    (116, 95, 'D', 'B'): 'U',
    (116, 95, 'D', 'F'): 'U',
    (116, 95, 'D', 'L'): 'U',
    (116, 95, 'D', 'R'): 'U',
    (116, 95, 'F', 'D'): 'D',
    (116, 95, 'F', 'L'): 'D',
    (116, 95, 'F', 'R'): 'D',
    (116, 95, 'F', 'U'): 'D',
    (116, 95, 'L', 'B'): 'U',
    (116, 95, 'L', 'D'): 'D',
    (116, 95, 'L', 'F'): 'U',
    (116, 95, 'L', 'U'): 'D',
    (116, 95, 'R', 'B'): 'U',
    (116, 95, 'R', 'D'): 'D',
    (116, 95, 'R', 'F'): 'U',
    (116, 95, 'R', 'U'): 'D',
    (116, 95, 'U', 'B'): 'U',
    (116, 95, 'U', 'F'): 'U',
    (116, 95, 'U', 'L'): 'U',
    (116, 95, 'U', 'R'): 'U',
    (120, 41, 'B', 'D'): 'U',
    (120, 41, 'B', 'L'): 'U',
    (120, 41, 'B', 'R'): 'U',
    (120, 41, 'B', 'U'): 'U',
    (120, 41, 'D', 'B'): 'D',
    (120, 41, 'D', 'F'): 'D',
    (120, 41, 'D', 'L'): 'D',
    (120, 41, 'D', 'R'): 'D',
    (120, 41, 'F', 'D'): 'U',
    (120, 41, 'F', 'L'): 'U',
    (120, 41, 'F', 'R'): 'U',
    (120, 41, 'F', 'U'): 'U',
    (120, 41, 'L', 'B'): 'D',
    (120, 41, 'L', 'D'): 'U',
    (120, 41, 'L', 'F'): 'D',
    (120, 41, 'L', 'U'): 'U',
    (120, 41, 'R', 'B'): 'D',
    (120, 41, 'R', 'D'): 'U',
    (120, 41, 'R', 'F'): 'D',
    (120, 41, 'R', 'U'): 'U',
    (120, 41, 'U', 'B'): 'D',
    (120, 41, 'U', 'F'): 'D',
    (120, 41, 'U', 'L'): 'D',
    (120, 41, 'U', 'R'): 'D',
    (122, 149, 'B', 'D'): 'U',
    (122, 149, 'B', 'L'): 'U',
    (122, 149, 'B', 'R'): 'U',
    (122, 149, 'B', 'U'): 'U',
    (122, 149, 'D', 'B'): 'D',
    (122, 149, 'D', 'F'): 'D',
    (122, 149, 'D', 'L'): 'D',
    (122, 149, 'D', 'R'): 'D',
    (122, 149, 'F', 'D'): 'U',
    (122, 149, 'F', 'L'): 'U',
    (122, 149, 'F', 'R'): 'U',
    (122, 149, 'F', 'U'): 'U',
    (122, 149, 'L', 'B'): 'D',
    (122, 149, 'L', 'D'): 'U',
    (122, 149, 'L', 'F'): 'D',
    (122, 149, 'L', 'U'): 'U',
    (122, 149, 'R', 'B'): 'D',
    (122, 149, 'R', 'D'): 'U',
    (122, 149, 'R', 'F'): 'D',
    (122, 149, 'R', 'U'): 'U',
    (122, 149, 'U', 'B'): 'D',
    (122, 149, 'U', 'F'): 'D',
    (122, 149, 'U', 'L'): 'D',
    (122, 149, 'U', 'R'): 'D',
    (124, 147, 'B', 'D'): 'D',
    (124, 147, 'B', 'L'): 'D',
    (124, 147, 'B', 'R'): 'D',
    (124, 147, 'B', 'U'): 'D',
    (124, 147, 'D', 'B'): 'U',
    (124, 147, 'D', 'F'): 'U',
    (124, 147, 'D', 'L'): 'U',
    (124, 147, 'D', 'R'): 'U',
    (124, 147, 'F', 'D'): 'D',
    (124, 147, 'F', 'L'): 'D',
    (124, 147, 'F', 'R'): 'D',
    (124, 147, 'F', 'U'): 'D',
    (124, 147, 'L', 'B'): 'U',
    (124, 147, 'L', 'D'): 'D',
    (124, 147, 'L', 'F'): 'U',
    (124, 147, 'L', 'U'): 'D',
    (124, 147, 'R', 'B'): 'U',
    (124, 147, 'R', 'D'): 'D',
    (124, 147, 'R', 'F'): 'U',
    (124, 147, 'R', 'U'): 'D',
    (124, 147, 'U', 'B'): 'U',
    (124, 147, 'U', 'F'): 'U',
    (124, 147, 'U', 'L'): 'U',
    (124, 147, 'U', 'R'): 'U',
    (127, 72, 'B', 'D'): 'D',
    (127, 72, 'B', 'L'): 'D',
    (127, 72, 'B', 'R'): 'D',
    (127, 72, 'B', 'U'): 'D',
    (127, 72, 'D', 'B'): 'U',
    (127, 72, 'D', 'F'): 'U',
    (127, 72, 'D', 'L'): 'U',
    (127, 72, 'D', 'R'): 'U',
    (127, 72, 'F', 'D'): 'D',
    (127, 72, 'F', 'L'): 'D',
    (127, 72, 'F', 'R'): 'D',
    (127, 72, 'F', 'U'): 'D',
    (127, 72, 'L', 'B'): 'U',
    (127, 72, 'L', 'D'): 'D',
    (127, 72, 'L', 'F'): 'U',
    (127, 72, 'L', 'U'): 'D',
    (127, 72, 'R', 'B'): 'U',
    (127, 72, 'R', 'D'): 'D',
    (127, 72, 'R', 'F'): 'U',
    (127, 72, 'R', 'U'): 'D',
    (127, 72, 'U', 'B'): 'U',
    (127, 72, 'U', 'F'): 'U',
    (127, 72, 'U', 'L'): 'U',
    (127, 72, 'U', 'R'): 'U',
    (129, 74, 'B', 'D'): 'U',
    (129, 74, 'B', 'L'): 'U',
    (129, 74, 'B', 'R'): 'U',
    (129, 74, 'B', 'U'): 'U',
    (129, 74, 'D', 'B'): 'D',
    (129, 74, 'D', 'F'): 'D',
    (129, 74, 'D', 'L'): 'D',
    (129, 74, 'D', 'R'): 'D',
    (129, 74, 'F', 'D'): 'U',
    (129, 74, 'F', 'L'): 'U',
    (129, 74, 'F', 'R'): 'U',
    (129, 74, 'F', 'U'): 'U',
    (129, 74, 'L', 'B'): 'D',
    (129, 74, 'L', 'D'): 'U',
    (129, 74, 'L', 'F'): 'D',
    (129, 74, 'L', 'U'): 'U',
    (129, 74, 'R', 'B'): 'D',
    (129, 74, 'R', 'D'): 'U',
    (129, 74, 'R', 'F'): 'D',
    (129, 74, 'R', 'U'): 'U',
    (129, 74, 'U', 'B'): 'D',
    (129, 74, 'U', 'F'): 'D',
    (129, 74, 'U', 'L'): 'D',
    (129, 74, 'U', 'R'): 'D',
    (131, 49, 'B', 'D'): 'U',
    (131, 49, 'B', 'L'): 'U',
    (131, 49, 'B', 'R'): 'U',
    (131, 49, 'B', 'U'): 'U',
    (131, 49, 'D', 'B'): 'D',
    (131, 49, 'D', 'F'): 'D',
    (131, 49, 'D', 'L'): 'D',
    (131, 49, 'D', 'R'): 'D',
    (131, 49, 'F', 'D'): 'U',
    (131, 49, 'F', 'L'): 'U',
    (131, 49, 'F', 'R'): 'U',
    (131, 49, 'F', 'U'): 'U',
    (131, 49, 'L', 'B'): 'D',
    (131, 49, 'L', 'D'): 'U',
    (131, 49, 'L', 'F'): 'D',
    (131, 49, 'L', 'U'): 'U',
    (131, 49, 'R', 'B'): 'D',
    (131, 49, 'R', 'D'): 'U',
    (131, 49, 'R', 'F'): 'D',
    (131, 49, 'R', 'U'): 'U',
    (131, 49, 'U', 'B'): 'D',
    (131, 49, 'U', 'F'): 'D',
    (131, 49, 'U', 'L'): 'D',
    (131, 49, 'U', 'R'): 'D',
    (135, 97, 'B', 'D'): 'D',
    (135, 97, 'B', 'L'): 'D',
    (135, 97, 'B', 'R'): 'D',
    (135, 97, 'B', 'U'): 'D',
    (135, 97, 'D', 'B'): 'U',
    (135, 97, 'D', 'F'): 'U',
    (135, 97, 'D', 'L'): 'U',
    (135, 97, 'D', 'R'): 'U',
    (135, 97, 'F', 'D'): 'D',
    (135, 97, 'F', 'L'): 'D',
    (135, 97, 'F', 'R'): 'D',
    (135, 97, 'F', 'U'): 'D',
    (135, 97, 'L', 'B'): 'U',
    (135, 97, 'L', 'D'): 'D',
    (135, 97, 'L', 'F'): 'U',
    (135, 97, 'L', 'U'): 'D',
    (135, 97, 'R', 'B'): 'U',
    (135, 97, 'R', 'D'): 'D',
    (135, 97, 'R', 'F'): 'U',
    (135, 97, 'R', 'U'): 'D',
    (135, 97, 'U', 'B'): 'U',
    (135, 97, 'U', 'F'): 'U',
    (135, 97, 'U', 'L'): 'U',
    (135, 97, 'U', 'R'): 'U',
    (141, 47, 'B', 'D'): 'D',
    (141, 47, 'B', 'L'): 'D',
    (141, 47, 'B', 'R'): 'D',
    (141, 47, 'B', 'U'): 'D',
    (141, 47, 'D', 'B'): 'U',
    (141, 47, 'D', 'F'): 'U',
    (141, 47, 'D', 'L'): 'U',
    (141, 47, 'D', 'R'): 'U',
    (141, 47, 'F', 'D'): 'D',
    (141, 47, 'F', 'L'): 'D',
    (141, 47, 'F', 'R'): 'D',
    (141, 47, 'F', 'U'): 'D',
    (141, 47, 'L', 'B'): 'U',
    (141, 47, 'L', 'D'): 'D',
    (141, 47, 'L', 'F'): 'U',
    (141, 47, 'L', 'U'): 'D',
    (141, 47, 'R', 'B'): 'U',
    (141, 47, 'R', 'D'): 'D',
    (141, 47, 'R', 'F'): 'U',
    (141, 47, 'R', 'U'): 'D',
    (141, 47, 'U', 'B'): 'U',
    (141, 47, 'U', 'F'): 'U',
    (141, 47, 'U', 'L'): 'U',
    (141, 47, 'U', 'R'): 'U',
    (145, 99, 'B', 'D'): 'U',
    (145, 99, 'B', 'L'): 'U',
    (145, 99, 'B', 'R'): 'U',
    (145, 99, 'B', 'U'): 'U',
    (145, 99, 'D', 'B'): 'D',
    (145, 99, 'D', 'F'): 'D',
    (145, 99, 'D', 'L'): 'D',
    (145, 99, 'D', 'R'): 'D',
    (145, 99, 'F', 'D'): 'U',
    (145, 99, 'F', 'L'): 'U',
    (145, 99, 'F', 'R'): 'U',
    (145, 99, 'F', 'U'): 'U',
    (145, 99, 'L', 'B'): 'D',
    (145, 99, 'L', 'D'): 'U',
    (145, 99, 'L', 'F'): 'D',
    (145, 99, 'L', 'U'): 'U',
    (145, 99, 'R', 'B'): 'D',
    (145, 99, 'R', 'D'): 'U',
    (145, 99, 'R', 'F'): 'D',
    (145, 99, 'R', 'U'): 'U',
    (145, 99, 'U', 'B'): 'D',
    (145, 99, 'U', 'F'): 'D',
    (145, 99, 'U', 'L'): 'D',
    (145, 99, 'U', 'R'): 'D',
    (147, 124, 'B', 'D'): 'U',
    (147, 124, 'B', 'L'): 'U',
    (147, 124, 'B', 'R'): 'U',
    (147, 124, 'B', 'U'): 'U',
    (147, 124, 'D', 'B'): 'D',
    (147, 124, 'D', 'F'): 'D',
    (147, 124, 'D', 'L'): 'D',
    (147, 124, 'D', 'R'): 'D',
    (147, 124, 'F', 'D'): 'U',
    (147, 124, 'F', 'L'): 'U',
    (147, 124, 'F', 'R'): 'U',
    (147, 124, 'F', 'U'): 'U',
    (147, 124, 'L', 'B'): 'D',
    (147, 124, 'L', 'D'): 'U',
    (147, 124, 'L', 'F'): 'D',
    (147, 124, 'L', 'U'): 'U',
    (147, 124, 'R', 'B'): 'D',
    (147, 124, 'R', 'D'): 'U',
    (147, 124, 'R', 'F'): 'D',
    (147, 124, 'R', 'U'): 'U',
    (147, 124, 'U', 'B'): 'D',
    (147, 124, 'U', 'F'): 'D',
    (147, 124, 'U', 'L'): 'D',
    (147, 124, 'U', 'R'): 'D',
    (149, 122, 'B', 'D'): 'D',
    (149, 122, 'B', 'L'): 'D',
    (149, 122, 'B', 'R'): 'D',
    (149, 122, 'B', 'U'): 'D',
    (149, 122, 'D', 'B'): 'U',
    (149, 122, 'D', 'F'): 'U',
    (149, 122, 'D', 'L'): 'U',
    (149, 122, 'D', 'R'): 'U',
    (149, 122, 'F', 'D'): 'D',
    (149, 122, 'F', 'L'): 'D',
    (149, 122, 'F', 'R'): 'D',
    (149, 122, 'F', 'U'): 'D',
    (149, 122, 'L', 'B'): 'U',
    (149, 122, 'L', 'D'): 'D',
    (149, 122, 'L', 'F'): 'U',
    (149, 122, 'L', 'U'): 'D',
    (149, 122, 'R', 'B'): 'U',
    (149, 122, 'R', 'D'): 'D',
    (149, 122, 'R', 'F'): 'U',
    (149, 122, 'R', 'U'): 'D',
    (149, 122, 'U', 'B'): 'U',
    (149, 122, 'U', 'F'): 'U',
    (149, 122, 'U', 'L'): 'U',
    (149, 122, 'U', 'R'): 'U'
}

stage_first_four_edges_wing_str_combos = (
    ('BD', 'BL', 'BR', 'BU'),
    ('BD', 'BL', 'BR', 'DF'),
    ('BD', 'BL', 'BR', 'DL'),
    ('BD', 'BL', 'BR', 'DR'),
    ('BD', 'BL', 'BR', 'FL'),
    ('BD', 'BL', 'BR', 'FR'),
    ('BD', 'BL', 'BR', 'FU'),
    ('BD', 'BL', 'BR', 'LU'),
    ('BD', 'BL', 'BR', 'RU'),
    ('BD', 'BL', 'BU', 'DF'),
    ('BD', 'BL', 'BU', 'DL'),
    ('BD', 'BL', 'BU', 'DR'),
    ('BD', 'BL', 'BU', 'FL'),
    ('BD', 'BL', 'BU', 'FR'),
    ('BD', 'BL', 'BU', 'FU'),
    ('BD', 'BL', 'BU', 'LU'),
    ('BD', 'BL', 'BU', 'RU'),
    ('BD', 'BL', 'DF', 'DL'),
    ('BD', 'BL', 'DF', 'DR'),
    ('BD', 'BL', 'DF', 'FL'),
    ('BD', 'BL', 'DF', 'FR'),
    ('BD', 'BL', 'DF', 'FU'),
    ('BD', 'BL', 'DF', 'LU'),
    ('BD', 'BL', 'DF', 'RU'),
    ('BD', 'BL', 'DL', 'DR'),
    ('BD', 'BL', 'DL', 'FL'),
    ('BD', 'BL', 'DL', 'FR'),
    ('BD', 'BL', 'DL', 'FU'),
    ('BD', 'BL', 'DL', 'LU'),
    ('BD', 'BL', 'DL', 'RU'),
    ('BD', 'BL', 'DR', 'FL'),
    ('BD', 'BL', 'DR', 'FR'),
    ('BD', 'BL', 'DR', 'FU'),
    ('BD', 'BL', 'DR', 'LU'),
    ('BD', 'BL', 'DR', 'RU'),
    ('BD', 'BL', 'FL', 'FR'),
    ('BD', 'BL', 'FL', 'FU'),
    ('BD', 'BL', 'FL', 'LU'),
    ('BD', 'BL', 'FL', 'RU'),
    ('BD', 'BL', 'FR', 'FU'),
    ('BD', 'BL', 'FR', 'LU'),
    ('BD', 'BL', 'FR', 'RU'),
    ('BD', 'BL', 'FU', 'LU'),
    ('BD', 'BL', 'FU', 'RU'),
    ('BD', 'BL', 'LU', 'RU'),
    ('BD', 'BR', 'BU', 'DF'),
    ('BD', 'BR', 'BU', 'DL'),
    ('BD', 'BR', 'BU', 'DR'),
    ('BD', 'BR', 'BU', 'FL'),
    ('BD', 'BR', 'BU', 'FR'),
    ('BD', 'BR', 'BU', 'FU'),
    ('BD', 'BR', 'BU', 'LU'),
    ('BD', 'BR', 'BU', 'RU'),
    ('BD', 'BR', 'DF', 'DL'),
    ('BD', 'BR', 'DF', 'DR'),
    ('BD', 'BR', 'DF', 'FL'),
    ('BD', 'BR', 'DF', 'FR'),
    ('BD', 'BR', 'DF', 'FU'),
    ('BD', 'BR', 'DF', 'LU'),
    ('BD', 'BR', 'DF', 'RU'),
    ('BD', 'BR', 'DL', 'DR'),
    ('BD', 'BR', 'DL', 'FL'),
    ('BD', 'BR', 'DL', 'FR'),
    ('BD', 'BR', 'DL', 'FU'),
    ('BD', 'BR', 'DL', 'LU'),
    ('BD', 'BR', 'DL', 'RU'),
    ('BD', 'BR', 'DR', 'FL'),
    ('BD', 'BR', 'DR', 'FR'),
    ('BD', 'BR', 'DR', 'FU'),
    ('BD', 'BR', 'DR', 'LU'),
    ('BD', 'BR', 'DR', 'RU'),
    ('BD', 'BR', 'FL', 'FR'),
    ('BD', 'BR', 'FL', 'FU'),
    ('BD', 'BR', 'FL', 'LU'),
    ('BD', 'BR', 'FL', 'RU'),
    ('BD', 'BR', 'FR', 'FU'),
    ('BD', 'BR', 'FR', 'LU'),
    ('BD', 'BR', 'FR', 'RU'),
    ('BD', 'BR', 'FU', 'LU'),
    ('BD', 'BR', 'FU', 'RU'),
    ('BD', 'BR', 'LU', 'RU'),
    ('BD', 'BU', 'DF', 'DL'),
    ('BD', 'BU', 'DF', 'DR'),
    ('BD', 'BU', 'DF', 'FL'),
    ('BD', 'BU', 'DF', 'FR'),
    ('BD', 'BU', 'DF', 'FU'),
    ('BD', 'BU', 'DF', 'LU'),
    ('BD', 'BU', 'DF', 'RU'),
    ('BD', 'BU', 'DL', 'DR'),
    ('BD', 'BU', 'DL', 'FL'),
    ('BD', 'BU', 'DL', 'FR'),
    ('BD', 'BU', 'DL', 'FU'),
    ('BD', 'BU', 'DL', 'LU'),
    ('BD', 'BU', 'DL', 'RU'),
    ('BD', 'BU', 'DR', 'FL'),
    ('BD', 'BU', 'DR', 'FR'),
    ('BD', 'BU', 'DR', 'FU'),
    ('BD', 'BU', 'DR', 'LU'),
    ('BD', 'BU', 'DR', 'RU'),
    ('BD', 'BU', 'FL', 'FR'),
    ('BD', 'BU', 'FL', 'FU'),
    ('BD', 'BU', 'FL', 'LU'),
    ('BD', 'BU', 'FL', 'RU'),
    ('BD', 'BU', 'FR', 'FU'),
    ('BD', 'BU', 'FR', 'LU'),
    ('BD', 'BU', 'FR', 'RU'),
    ('BD', 'BU', 'FU', 'LU'),
    ('BD', 'BU', 'FU', 'RU'),
    ('BD', 'BU', 'LU', 'RU'),
    ('BD', 'DF', 'DL', 'DR'),
    ('BD', 'DF', 'DL', 'FL'),
    ('BD', 'DF', 'DL', 'FR'),
    ('BD', 'DF', 'DL', 'FU'),
    ('BD', 'DF', 'DL', 'LU'),
    ('BD', 'DF', 'DL', 'RU'),
    ('BD', 'DF', 'DR', 'FL'),
    ('BD', 'DF', 'DR', 'FR'),
    ('BD', 'DF', 'DR', 'FU'),
    ('BD', 'DF', 'DR', 'LU'),
    ('BD', 'DF', 'DR', 'RU'),
    ('BD', 'DF', 'FL', 'FR'),
    ('BD', 'DF', 'FL', 'FU'),
    ('BD', 'DF', 'FL', 'LU'),
    ('BD', 'DF', 'FL', 'RU'),
    ('BD', 'DF', 'FR', 'FU'),
    ('BD', 'DF', 'FR', 'LU'),
    ('BD', 'DF', 'FR', 'RU'),
    ('BD', 'DF', 'FU', 'LU'),
    ('BD', 'DF', 'FU', 'RU'),
    ('BD', 'DF', 'LU', 'RU'),
    ('BD', 'DL', 'DR', 'FL'),
    ('BD', 'DL', 'DR', 'FR'),
    ('BD', 'DL', 'DR', 'FU'),
    ('BD', 'DL', 'DR', 'LU'),
    ('BD', 'DL', 'DR', 'RU'),
    ('BD', 'DL', 'FL', 'FR'),
    ('BD', 'DL', 'FL', 'FU'),
    ('BD', 'DL', 'FL', 'LU'),
    ('BD', 'DL', 'FL', 'RU'),
    ('BD', 'DL', 'FR', 'FU'),
    ('BD', 'DL', 'FR', 'LU'),
    ('BD', 'DL', 'FR', 'RU'),
    ('BD', 'DL', 'FU', 'LU'),
    ('BD', 'DL', 'FU', 'RU'),
    ('BD', 'DL', 'LU', 'RU'),
    ('BD', 'DR', 'FL', 'FR'),
    ('BD', 'DR', 'FL', 'FU'),
    ('BD', 'DR', 'FL', 'LU'),
    ('BD', 'DR', 'FL', 'RU'),
    ('BD', 'DR', 'FR', 'FU'),
    ('BD', 'DR', 'FR', 'LU'),
    ('BD', 'DR', 'FR', 'RU'),
    ('BD', 'DR', 'FU', 'LU'),
    ('BD', 'DR', 'FU', 'RU'),
    ('BD', 'DR', 'LU', 'RU'),
    ('BD', 'FL', 'FR', 'FU'),
    ('BD', 'FL', 'FR', 'LU'),
    ('BD', 'FL', 'FR', 'RU'),
    ('BD', 'FL', 'FU', 'LU'),
    ('BD', 'FL', 'FU', 'RU'),
    ('BD', 'FL', 'LU', 'RU'),
    ('BD', 'FR', 'FU', 'LU'),
    ('BD', 'FR', 'FU', 'RU'),
    ('BD', 'FR', 'LU', 'RU'),
    ('BD', 'FU', 'LU', 'RU'),
    ('BL', 'BR', 'BU', 'DF'),
    ('BL', 'BR', 'BU', 'DL'),
    ('BL', 'BR', 'BU', 'DR'),
    ('BL', 'BR', 'BU', 'FL'),
    ('BL', 'BR', 'BU', 'FR'),
    ('BL', 'BR', 'BU', 'FU'),
    ('BL', 'BR', 'BU', 'LU'),
    ('BL', 'BR', 'BU', 'RU'),
    ('BL', 'BR', 'DF', 'DL'),
    ('BL', 'BR', 'DF', 'DR'),
    ('BL', 'BR', 'DF', 'FL'),
    ('BL', 'BR', 'DF', 'FR'),
    ('BL', 'BR', 'DF', 'FU'),
    ('BL', 'BR', 'DF', 'LU'),
    ('BL', 'BR', 'DF', 'RU'),
    ('BL', 'BR', 'DL', 'DR'),
    ('BL', 'BR', 'DL', 'FL'),
    ('BL', 'BR', 'DL', 'FR'),
    ('BL', 'BR', 'DL', 'FU'),
    ('BL', 'BR', 'DL', 'LU'),
    ('BL', 'BR', 'DL', 'RU'),
    ('BL', 'BR', 'DR', 'FL'),
    ('BL', 'BR', 'DR', 'FR'),
    ('BL', 'BR', 'DR', 'FU'),
    ('BL', 'BR', 'DR', 'LU'),
    ('BL', 'BR', 'DR', 'RU'),
    ('BL', 'BR', 'FL', 'FR'),
    ('BL', 'BR', 'FL', 'FU'),
    ('BL', 'BR', 'FL', 'LU'),
    ('BL', 'BR', 'FL', 'RU'),
    ('BL', 'BR', 'FR', 'FU'),
    ('BL', 'BR', 'FR', 'LU'),
    ('BL', 'BR', 'FR', 'RU'),
    ('BL', 'BR', 'FU', 'LU'),
    ('BL', 'BR', 'FU', 'RU'),
    ('BL', 'BR', 'LU', 'RU'),
    ('BL', 'BU', 'DF', 'DL'),
    ('BL', 'BU', 'DF', 'DR'),
    ('BL', 'BU', 'DF', 'FL'),
    ('BL', 'BU', 'DF', 'FR'),
    ('BL', 'BU', 'DF', 'FU'),
    ('BL', 'BU', 'DF', 'LU'),
    ('BL', 'BU', 'DF', 'RU'),
    ('BL', 'BU', 'DL', 'DR'),
    ('BL', 'BU', 'DL', 'FL'),
    ('BL', 'BU', 'DL', 'FR'),
    ('BL', 'BU', 'DL', 'FU'),
    ('BL', 'BU', 'DL', 'LU'),
    ('BL', 'BU', 'DL', 'RU'),
    ('BL', 'BU', 'DR', 'FL'),
    ('BL', 'BU', 'DR', 'FR'),
    ('BL', 'BU', 'DR', 'FU'),
    ('BL', 'BU', 'DR', 'LU'),
    ('BL', 'BU', 'DR', 'RU'),
    ('BL', 'BU', 'FL', 'FR'),
    ('BL', 'BU', 'FL', 'FU'),
    ('BL', 'BU', 'FL', 'LU'),
    ('BL', 'BU', 'FL', 'RU'),
    ('BL', 'BU', 'FR', 'FU'),
    ('BL', 'BU', 'FR', 'LU'),
    ('BL', 'BU', 'FR', 'RU'),
    ('BL', 'BU', 'FU', 'LU'),
    ('BL', 'BU', 'FU', 'RU'),
    ('BL', 'BU', 'LU', 'RU'),
    ('BL', 'DF', 'DL', 'DR'),
    ('BL', 'DF', 'DL', 'FL'),
    ('BL', 'DF', 'DL', 'FR'),
    ('BL', 'DF', 'DL', 'FU'),
    ('BL', 'DF', 'DL', 'LU'),
    ('BL', 'DF', 'DL', 'RU'),
    ('BL', 'DF', 'DR', 'FL'),
    ('BL', 'DF', 'DR', 'FR'),
    ('BL', 'DF', 'DR', 'FU'),
    ('BL', 'DF', 'DR', 'LU'),
    ('BL', 'DF', 'DR', 'RU'),
    ('BL', 'DF', 'FL', 'FR'),
    ('BL', 'DF', 'FL', 'FU'),
    ('BL', 'DF', 'FL', 'LU'),
    ('BL', 'DF', 'FL', 'RU'),
    ('BL', 'DF', 'FR', 'FU'),
    ('BL', 'DF', 'FR', 'LU'),
    ('BL', 'DF', 'FR', 'RU'),
    ('BL', 'DF', 'FU', 'LU'),
    ('BL', 'DF', 'FU', 'RU'),
    ('BL', 'DF', 'LU', 'RU'),
    ('BL', 'DL', 'DR', 'FL'),
    ('BL', 'DL', 'DR', 'FR'),
    ('BL', 'DL', 'DR', 'FU'),
    ('BL', 'DL', 'DR', 'LU'),
    ('BL', 'DL', 'DR', 'RU'),
    ('BL', 'DL', 'FL', 'FR'),
    ('BL', 'DL', 'FL', 'FU'),
    ('BL', 'DL', 'FL', 'LU'),
    ('BL', 'DL', 'FL', 'RU'),
    ('BL', 'DL', 'FR', 'FU'),
    ('BL', 'DL', 'FR', 'LU'),
    ('BL', 'DL', 'FR', 'RU'),
    ('BL', 'DL', 'FU', 'LU'),
    ('BL', 'DL', 'FU', 'RU'),
    ('BL', 'DL', 'LU', 'RU'),
    ('BL', 'DR', 'FL', 'FR'),
    ('BL', 'DR', 'FL', 'FU'),
    ('BL', 'DR', 'FL', 'LU'),
    ('BL', 'DR', 'FL', 'RU'),
    ('BL', 'DR', 'FR', 'FU'),
    ('BL', 'DR', 'FR', 'LU'),
    ('BL', 'DR', 'FR', 'RU'),
    ('BL', 'DR', 'FU', 'LU'),
    ('BL', 'DR', 'FU', 'RU'),
    ('BL', 'DR', 'LU', 'RU'),
    ('BL', 'FL', 'FR', 'FU'),
    ('BL', 'FL', 'FR', 'LU'),
    ('BL', 'FL', 'FR', 'RU'),
    ('BL', 'FL', 'FU', 'LU'),
    ('BL', 'FL', 'FU', 'RU'),
    ('BL', 'FL', 'LU', 'RU'),
    ('BL', 'FR', 'FU', 'LU'),
    ('BL', 'FR', 'FU', 'RU'),
    ('BL', 'FR', 'LU', 'RU'),
    ('BL', 'FU', 'LU', 'RU'),
    ('BR', 'BU', 'DF', 'DL'),
    ('BR', 'BU', 'DF', 'DR'),
    ('BR', 'BU', 'DF', 'FL'),
    ('BR', 'BU', 'DF', 'FR'),
    ('BR', 'BU', 'DF', 'FU'),
    ('BR', 'BU', 'DF', 'LU'),
    ('BR', 'BU', 'DF', 'RU'),
    ('BR', 'BU', 'DL', 'DR'),
    ('BR', 'BU', 'DL', 'FL'),
    ('BR', 'BU', 'DL', 'FR'),
    ('BR', 'BU', 'DL', 'FU'),
    ('BR', 'BU', 'DL', 'LU'),
    ('BR', 'BU', 'DL', 'RU'),
    ('BR', 'BU', 'DR', 'FL'),
    ('BR', 'BU', 'DR', 'FR'),
    ('BR', 'BU', 'DR', 'FU'),
    ('BR', 'BU', 'DR', 'LU'),
    ('BR', 'BU', 'DR', 'RU'),
    ('BR', 'BU', 'FL', 'FR'),
    ('BR', 'BU', 'FL', 'FU'),
    ('BR', 'BU', 'FL', 'LU'),
    ('BR', 'BU', 'FL', 'RU'),
    ('BR', 'BU', 'FR', 'FU'),
    ('BR', 'BU', 'FR', 'LU'),
    ('BR', 'BU', 'FR', 'RU'),
    ('BR', 'BU', 'FU', 'LU'),
    ('BR', 'BU', 'FU', 'RU'),
    ('BR', 'BU', 'LU', 'RU'),
    ('BR', 'DF', 'DL', 'DR'),
    ('BR', 'DF', 'DL', 'FL'),
    ('BR', 'DF', 'DL', 'FR'),
    ('BR', 'DF', 'DL', 'FU'),
    ('BR', 'DF', 'DL', 'LU'),
    ('BR', 'DF', 'DL', 'RU'),
    ('BR', 'DF', 'DR', 'FL'),
    ('BR', 'DF', 'DR', 'FR'),
    ('BR', 'DF', 'DR', 'FU'),
    ('BR', 'DF', 'DR', 'LU'),
    ('BR', 'DF', 'DR', 'RU'),
    ('BR', 'DF', 'FL', 'FR'),
    ('BR', 'DF', 'FL', 'FU'),
    ('BR', 'DF', 'FL', 'LU'),
    ('BR', 'DF', 'FL', 'RU'),
    ('BR', 'DF', 'FR', 'FU'),
    ('BR', 'DF', 'FR', 'LU'),
    ('BR', 'DF', 'FR', 'RU'),
    ('BR', 'DF', 'FU', 'LU'),
    ('BR', 'DF', 'FU', 'RU'),
    ('BR', 'DF', 'LU', 'RU'),
    ('BR', 'DL', 'DR', 'FL'),
    ('BR', 'DL', 'DR', 'FR'),
    ('BR', 'DL', 'DR', 'FU'),
    ('BR', 'DL', 'DR', 'LU'),
    ('BR', 'DL', 'DR', 'RU'),
    ('BR', 'DL', 'FL', 'FR'),
    ('BR', 'DL', 'FL', 'FU'),
    ('BR', 'DL', 'FL', 'LU'),
    ('BR', 'DL', 'FL', 'RU'),
    ('BR', 'DL', 'FR', 'FU'),
    ('BR', 'DL', 'FR', 'LU'),
    ('BR', 'DL', 'FR', 'RU'),
    ('BR', 'DL', 'FU', 'LU'),
    ('BR', 'DL', 'FU', 'RU'),
    ('BR', 'DL', 'LU', 'RU'),
    ('BR', 'DR', 'FL', 'FR'),
    ('BR', 'DR', 'FL', 'FU'),
    ('BR', 'DR', 'FL', 'LU'),
    ('BR', 'DR', 'FL', 'RU'),
    ('BR', 'DR', 'FR', 'FU'),
    ('BR', 'DR', 'FR', 'LU'),
    ('BR', 'DR', 'FR', 'RU'),
    ('BR', 'DR', 'FU', 'LU'),
    ('BR', 'DR', 'FU', 'RU'),
    ('BR', 'DR', 'LU', 'RU'),
    ('BR', 'FL', 'FR', 'FU'),
    ('BR', 'FL', 'FR', 'LU'),
    ('BR', 'FL', 'FR', 'RU'),
    ('BR', 'FL', 'FU', 'LU'),
    ('BR', 'FL', 'FU', 'RU'),
    ('BR', 'FL', 'LU', 'RU'),
    ('BR', 'FR', 'FU', 'LU'),
    ('BR', 'FR', 'FU', 'RU'),
    ('BR', 'FR', 'LU', 'RU'),
    ('BR', 'FU', 'LU', 'RU'),
    ('BU', 'DF', 'DL', 'DR'),
    ('BU', 'DF', 'DL', 'FL'),
    ('BU', 'DF', 'DL', 'FR'),
    ('BU', 'DF', 'DL', 'FU'),
    ('BU', 'DF', 'DL', 'LU'),
    ('BU', 'DF', 'DL', 'RU'),
    ('BU', 'DF', 'DR', 'FL'),
    ('BU', 'DF', 'DR', 'FR'),
    ('BU', 'DF', 'DR', 'FU'),
    ('BU', 'DF', 'DR', 'LU'),
    ('BU', 'DF', 'DR', 'RU'),
    ('BU', 'DF', 'FL', 'FR'),
    ('BU', 'DF', 'FL', 'FU'),
    ('BU', 'DF', 'FL', 'LU'),
    ('BU', 'DF', 'FL', 'RU'),
    ('BU', 'DF', 'FR', 'FU'),
    ('BU', 'DF', 'FR', 'LU'),
    ('BU', 'DF', 'FR', 'RU'),
    ('BU', 'DF', 'FU', 'LU'),
    ('BU', 'DF', 'FU', 'RU'),
    ('BU', 'DF', 'LU', 'RU'),
    ('BU', 'DL', 'DR', 'FL'),
    ('BU', 'DL', 'DR', 'FR'),
    ('BU', 'DL', 'DR', 'FU'),
    ('BU', 'DL', 'DR', 'LU'),
    ('BU', 'DL', 'DR', 'RU'),
    ('BU', 'DL', 'FL', 'FR'),
    ('BU', 'DL', 'FL', 'FU'),
    ('BU', 'DL', 'FL', 'LU'),
    ('BU', 'DL', 'FL', 'RU'),
    ('BU', 'DL', 'FR', 'FU'),
    ('BU', 'DL', 'FR', 'LU'),
    ('BU', 'DL', 'FR', 'RU'),
    ('BU', 'DL', 'FU', 'LU'),
    ('BU', 'DL', 'FU', 'RU'),
    ('BU', 'DL', 'LU', 'RU'),
    ('BU', 'DR', 'FL', 'FR'),
    ('BU', 'DR', 'FL', 'FU'),
    ('BU', 'DR', 'FL', 'LU'),
    ('BU', 'DR', 'FL', 'RU'),
    ('BU', 'DR', 'FR', 'FU'),
    ('BU', 'DR', 'FR', 'LU'),
    ('BU', 'DR', 'FR', 'RU'),
    ('BU', 'DR', 'FU', 'LU'),
    ('BU', 'DR', 'FU', 'RU'),
    ('BU', 'DR', 'LU', 'RU'),
    ('BU', 'FL', 'FR', 'FU'),
    ('BU', 'FL', 'FR', 'LU'),
    ('BU', 'FL', 'FR', 'RU'),
    ('BU', 'FL', 'FU', 'LU'),
    ('BU', 'FL', 'FU', 'RU'),
    ('BU', 'FL', 'LU', 'RU'),
    ('BU', 'FR', 'FU', 'LU'),
    ('BU', 'FR', 'FU', 'RU'),
    ('BU', 'FR', 'LU', 'RU'),
    ('BU', 'FU', 'LU', 'RU'),
    ('DF', 'DL', 'DR', 'FL'),
    ('DF', 'DL', 'DR', 'FR'),
    ('DF', 'DL', 'DR', 'FU'),
    ('DF', 'DL', 'DR', 'LU'),
    ('DF', 'DL', 'DR', 'RU'),
    ('DF', 'DL', 'FL', 'FR'),
    ('DF', 'DL', 'FL', 'FU'),
    ('DF', 'DL', 'FL', 'LU'),
    ('DF', 'DL', 'FL', 'RU'),
    ('DF', 'DL', 'FR', 'FU'),
    ('DF', 'DL', 'FR', 'LU'),
    ('DF', 'DL', 'FR', 'RU'),
    ('DF', 'DL', 'FU', 'LU'),
    ('DF', 'DL', 'FU', 'RU'),
    ('DF', 'DL', 'LU', 'RU'),
    ('DF', 'DR', 'FL', 'FR'),
    ('DF', 'DR', 'FL', 'FU'),
    ('DF', 'DR', 'FL', 'LU'),
    ('DF', 'DR', 'FL', 'RU'),
    ('DF', 'DR', 'FR', 'FU'),
    ('DF', 'DR', 'FR', 'LU'),
    ('DF', 'DR', 'FR', 'RU'),
    ('DF', 'DR', 'FU', 'LU'),
    ('DF', 'DR', 'FU', 'RU'),
    ('DF', 'DR', 'LU', 'RU'),
    ('DF', 'FL', 'FR', 'FU'),
    ('DF', 'FL', 'FR', 'LU'),
    ('DF', 'FL', 'FR', 'RU'),
    ('DF', 'FL', 'FU', 'LU'),
    ('DF', 'FL', 'FU', 'RU'),
    ('DF', 'FL', 'LU', 'RU'),
    ('DF', 'FR', 'FU', 'LU'),
    ('DF', 'FR', 'FU', 'RU'),
    ('DF', 'FR', 'LU', 'RU'),
    ('DF', 'FU', 'LU', 'RU'),
    ('DL', 'DR', 'FL', 'FR'),
    ('DL', 'DR', 'FL', 'FU'),
    ('DL', 'DR', 'FL', 'LU'),
    ('DL', 'DR', 'FL', 'RU'),
    ('DL', 'DR', 'FR', 'FU'),
    ('DL', 'DR', 'FR', 'LU'),
    ('DL', 'DR', 'FR', 'RU'),
    ('DL', 'DR', 'FU', 'LU'),
    ('DL', 'DR', 'FU', 'RU'),
    ('DL', 'DR', 'LU', 'RU'),
    ('DL', 'FL', 'FR', 'FU'),
    ('DL', 'FL', 'FR', 'LU'),
    ('DL', 'FL', 'FR', 'RU'),
    ('DL', 'FL', 'FU', 'LU'),
    ('DL', 'FL', 'FU', 'RU'),
    ('DL', 'FL', 'LU', 'RU'),
    ('DL', 'FR', 'FU', 'LU'),
    ('DL', 'FR', 'FU', 'RU'),
    ('DL', 'FR', 'LU', 'RU'),
    ('DL', 'FU', 'LU', 'RU'),
    ('DR', 'FL', 'FR', 'FU'),
    ('DR', 'FL', 'FR', 'LU'),
    ('DR', 'FL', 'FR', 'RU'),
    ('DR', 'FL', 'FU', 'LU'),
    ('DR', 'FL', 'FU', 'RU'),
    ('DR', 'FL', 'LU', 'RU'),
    ('DR', 'FR', 'FU', 'LU'),
    ('DR', 'FR', 'FU', 'RU'),
    ('DR', 'FR', 'LU', 'RU'),
    ('DR', 'FU', 'LU', 'RU'),
    ('FL', 'FR', 'FU', 'LU'),
    ('FL', 'FR', 'FU', 'RU'),
    ('FL', 'FR', 'LU', 'RU'),
    ('FL', 'FU', 'LU', 'RU'),
    ('FR', 'FU', 'LU', 'RU'),
)

swaps_555 = {'B': (0, 80, 85, 90, 95, 100, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 5, 27, 28, 29, 30, 4, 32, 33, 34, 35, 3, 37, 38, 39, 40, 2, 42, 43, 44, 45, 1, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 150, 81, 82, 83, 84, 149, 86, 87, 88, 89, 148, 91, 92, 93, 94, 147, 96, 97, 98, 99, 146, 121, 116, 111, 106, 101, 122, 117, 112, 107, 102, 123, 118, 113, 108, 103, 124, 119, 114, 109, 104, 125, 120, 115, 110, 105, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 26, 31, 36, 41, 46),
 "B'": (0, 46, 41, 36, 31, 26, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 146, 27, 28, 29, 30, 147, 32, 33, 34, 35, 148, 37, 38, 39, 40, 149, 42, 43, 44, 45, 150, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 1, 81, 82, 83, 84, 2, 86, 87, 88, 89, 3, 91, 92, 93, 94, 4, 96, 97, 98, 99, 5, 105, 110, 115, 120, 125, 104, 109, 114, 119, 124, 103, 108, 113, 118, 123, 102, 107, 112, 117, 122, 101, 106, 111, 116, 121, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 100, 95, 90, 85, 80),
 'B2': (0, 150, 149, 148, 147, 146, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 100, 27, 28, 29, 30, 95, 32, 33, 34, 35, 90, 37, 38, 39, 40, 85, 42, 43, 44, 45, 80, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 46, 81, 82, 83, 84, 41, 86, 87, 88, 89, 36, 91, 92, 93, 94, 31, 96, 97, 98, 99, 26, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 5, 4, 3, 2, 1),
 'Bw': (0, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 5, 10, 28, 29, 30, 4, 9, 33, 34, 35, 3, 8, 38, 39, 40, 2, 7, 43, 44, 45, 1, 6, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 145, 150, 81, 82, 83, 144, 149, 86, 87, 88, 143, 148, 91, 92, 93, 142, 147, 96, 97, 98, 141, 146, 121, 116, 111, 106, 101, 122, 117, 112, 107, 102, 123, 118, 113, 108, 103, 124, 119, 114, 109, 104, 125, 120, 115, 110, 105, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46),
 "Bw'": (0, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 146, 141, 28, 29, 30, 147, 142, 33, 34, 35, 148, 143, 38, 39, 40, 149, 144, 43, 44, 45, 150, 145, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 6, 1, 81, 82, 83, 7, 2, 86, 87, 88, 8, 3, 91, 92, 93, 9, 4, 96, 97, 98, 10, 5, 105, 110, 115, 120, 125, 104, 109, 114, 119, 124, 103, 108, 113, 118, 123, 102, 107, 112, 117, 122, 101, 106, 111, 116, 121, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80),
 'Bw2': (0, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 100, 99, 28, 29, 30, 95, 94, 33, 34, 35, 90, 89, 38, 39, 40, 85, 84, 43, 44, 45, 80, 79, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 47, 46, 81, 82, 83, 42, 41, 86, 87, 88, 37, 36, 91, 92, 93, 32, 31, 96, 97, 98, 27, 26, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1),
 'D': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 121, 122, 123, 124, 125, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 46, 47, 48, 49, 50, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 71, 72, 73, 74, 75, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 96, 97, 98, 99, 100, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130),
 "D'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 71, 72, 73, 74, 75, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 96, 97, 98, 99, 100, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 121, 122, 123, 124, 125, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 46, 47, 48, 49, 50, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146),
 'D2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 96, 97, 98, 99, 100, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 121, 122, 123, 124, 125, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 46, 47, 48, 49, 50, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 71, 72, 73, 74, 75, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126),
 'Dw': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130),
 "Dw'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146),
 'Dw2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126),
 'F': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 50, 45, 40, 35, 30, 26, 27, 28, 29, 126, 31, 32, 33, 34, 127, 36, 37, 38, 39, 128, 41, 42, 43, 44, 129, 46, 47, 48, 49, 130, 71, 66, 61, 56, 51, 72, 67, 62, 57, 52, 73, 68, 63, 58, 53, 74, 69, 64, 59, 54, 75, 70, 65, 60, 55, 21, 77, 78, 79, 80, 22, 82, 83, 84, 85, 23, 87, 88, 89, 90, 24, 92, 93, 94, 95, 25, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 96, 91, 86, 81, 76, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "F'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 76, 81, 86, 91, 96, 26, 27, 28, 29, 25, 31, 32, 33, 34, 24, 36, 37, 38, 39, 23, 41, 42, 43, 44, 22, 46, 47, 48, 49, 21, 55, 60, 65, 70, 75, 54, 59, 64, 69, 74, 53, 58, 63, 68, 73, 52, 57, 62, 67, 72, 51, 56, 61, 66, 71, 130, 77, 78, 79, 80, 129, 82, 83, 84, 85, 128, 87, 88, 89, 90, 127, 92, 93, 94, 95, 126, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 30, 35, 40, 45, 50, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'F2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 130, 129, 128, 127, 126, 26, 27, 28, 29, 96, 31, 32, 33, 34, 91, 36, 37, 38, 39, 86, 41, 42, 43, 44, 81, 46, 47, 48, 49, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 77, 78, 79, 80, 45, 82, 83, 84, 85, 40, 87, 88, 89, 90, 35, 92, 93, 94, 95, 30, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 25, 24, 23, 22, 21, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'Fw': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 26, 27, 28, 131, 126, 31, 32, 33, 132, 127, 36, 37, 38, 133, 128, 41, 42, 43, 134, 129, 46, 47, 48, 135, 130, 71, 66, 61, 56, 51, 72, 67, 62, 57, 52, 73, 68, 63, 58, 53, 74, 69, 64, 59, 54, 75, 70, 65, 60, 55, 21, 16, 78, 79, 80, 22, 17, 83, 84, 85, 23, 18, 88, 89, 90, 24, 19, 93, 94, 95, 25, 20, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "Fw'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 26, 27, 28, 20, 25, 31, 32, 33, 19, 24, 36, 37, 38, 18, 23, 41, 42, 43, 17, 22, 46, 47, 48, 16, 21, 55, 60, 65, 70, 75, 54, 59, 64, 69, 74, 53, 58, 63, 68, 73, 52, 57, 62, 67, 72, 51, 56, 61, 66, 71, 130, 135, 78, 79, 80, 129, 134, 83, 84, 85, 128, 133, 88, 89, 90, 127, 132, 93, 94, 95, 126, 131, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'Fw2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 26, 27, 28, 97, 96, 31, 32, 33, 92, 91, 36, 37, 38, 87, 86, 41, 42, 43, 82, 81, 46, 47, 48, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 78, 79, 80, 45, 44, 83, 84, 85, 40, 39, 88, 89, 90, 35, 34, 93, 94, 95, 30, 29, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'L': (0, 125, 2, 3, 4, 5, 120, 7, 8, 9, 10, 115, 12, 13, 14, 15, 110, 17, 18, 19, 20, 105, 22, 23, 24, 25, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 1, 52, 53, 54, 55, 6, 57, 58, 59, 60, 11, 62, 63, 64, 65, 16, 67, 68, 69, 70, 21, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 146, 106, 107, 108, 109, 141, 111, 112, 113, 114, 136, 116, 117, 118, 119, 131, 121, 122, 123, 124, 126, 51, 127, 128, 129, 130, 56, 132, 133, 134, 135, 61, 137, 138, 139, 140, 66, 142, 143, 144, 145, 71, 147, 148, 149, 150),
 "L'": (0, 51, 2, 3, 4, 5, 56, 7, 8, 9, 10, 61, 12, 13, 14, 15, 66, 17, 18, 19, 20, 71, 22, 23, 24, 25, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46, 126, 52, 53, 54, 55, 131, 57, 58, 59, 60, 136, 62, 63, 64, 65, 141, 67, 68, 69, 70, 146, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 21, 106, 107, 108, 109, 16, 111, 112, 113, 114, 11, 116, 117, 118, 119, 6, 121, 122, 123, 124, 1, 125, 127, 128, 129, 130, 120, 132, 133, 134, 135, 115, 137, 138, 139, 140, 110, 142, 143, 144, 145, 105, 147, 148, 149, 150),
 'L2': (0, 126, 2, 3, 4, 5, 131, 7, 8, 9, 10, 136, 12, 13, 14, 15, 141, 17, 18, 19, 20, 146, 22, 23, 24, 25, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 125, 52, 53, 54, 55, 120, 57, 58, 59, 60, 115, 62, 63, 64, 65, 110, 67, 68, 69, 70, 105, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 71, 106, 107, 108, 109, 66, 111, 112, 113, 114, 61, 116, 117, 118, 119, 56, 121, 122, 123, 124, 51, 1, 127, 128, 129, 130, 6, 132, 133, 134, 135, 11, 137, 138, 139, 140, 16, 142, 143, 144, 145, 21, 147, 148, 149, 150),
 'Lw': (0, 125, 124, 3, 4, 5, 120, 119, 8, 9, 10, 115, 114, 13, 14, 15, 110, 109, 18, 19, 20, 105, 104, 23, 24, 25, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 1, 2, 53, 54, 55, 6, 7, 58, 59, 60, 11, 12, 63, 64, 65, 16, 17, 68, 69, 70, 21, 22, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 147, 146, 106, 107, 108, 142, 141, 111, 112, 113, 137, 136, 116, 117, 118, 132, 131, 121, 122, 123, 127, 126, 51, 52, 128, 129, 130, 56, 57, 133, 134, 135, 61, 62, 138, 139, 140, 66, 67, 143, 144, 145, 71, 72, 148, 149, 150),
 "Lw'": (0, 51, 52, 3, 4, 5, 56, 57, 8, 9, 10, 61, 62, 13, 14, 15, 66, 67, 18, 19, 20, 71, 72, 23, 24, 25, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46, 126, 127, 53, 54, 55, 131, 132, 58, 59, 60, 136, 137, 63, 64, 65, 141, 142, 68, 69, 70, 146, 147, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 22, 21, 106, 107, 108, 17, 16, 111, 112, 113, 12, 11, 116, 117, 118, 7, 6, 121, 122, 123, 2, 1, 125, 124, 128, 129, 130, 120, 119, 133, 134, 135, 115, 114, 138, 139, 140, 110, 109, 143, 144, 145, 105, 104, 148, 149, 150),
 'Lw2': (0, 126, 127, 3, 4, 5, 131, 132, 8, 9, 10, 136, 137, 13, 14, 15, 141, 142, 18, 19, 20, 146, 147, 23, 24, 25, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 125, 124, 53, 54, 55, 120, 119, 58, 59, 60, 115, 114, 63, 64, 65, 110, 109, 68, 69, 70, 105, 104, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 72, 71, 106, 107, 108, 67, 66, 111, 112, 113, 62, 61, 116, 117, 118, 57, 56, 121, 122, 123, 52, 51, 1, 2, 128, 129, 130, 6, 7, 133, 134, 135, 11, 12, 138, 139, 140, 16, 17, 143, 144, 145, 21, 22, 148, 149, 150),
 'R': (0, 1, 2, 3, 4, 55, 6, 7, 8, 9, 60, 11, 12, 13, 14, 65, 16, 17, 18, 19, 70, 21, 22, 23, 24, 75, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 130, 56, 57, 58, 59, 135, 61, 62, 63, 64, 140, 66, 67, 68, 69, 145, 71, 72, 73, 74, 150, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80, 25, 102, 103, 104, 105, 20, 107, 108, 109, 110, 15, 112, 113, 114, 115, 10, 117, 118, 119, 120, 5, 122, 123, 124, 125, 126, 127, 128, 129, 121, 131, 132, 133, 134, 116, 136, 137, 138, 139, 111, 141, 142, 143, 144, 106, 146, 147, 148, 149, 101),
 "R'": (0, 1, 2, 3, 4, 121, 6, 7, 8, 9, 116, 11, 12, 13, 14, 111, 16, 17, 18, 19, 106, 21, 22, 23, 24, 101, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 5, 56, 57, 58, 59, 10, 61, 62, 63, 64, 15, 66, 67, 68, 69, 20, 71, 72, 73, 74, 25, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 150, 102, 103, 104, 105, 145, 107, 108, 109, 110, 140, 112, 113, 114, 115, 135, 117, 118, 119, 120, 130, 122, 123, 124, 125, 126, 127, 128, 129, 55, 131, 132, 133, 134, 60, 136, 137, 138, 139, 65, 141, 142, 143, 144, 70, 146, 147, 148, 149, 75),
 'R2': (0, 1, 2, 3, 4, 130, 6, 7, 8, 9, 135, 11, 12, 13, 14, 140, 16, 17, 18, 19, 145, 21, 22, 23, 24, 150, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 121, 56, 57, 58, 59, 116, 61, 62, 63, 64, 111, 66, 67, 68, 69, 106, 71, 72, 73, 74, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 102, 103, 104, 105, 70, 107, 108, 109, 110, 65, 112, 113, 114, 115, 60, 117, 118, 119, 120, 55, 122, 123, 124, 125, 126, 127, 128, 129, 5, 131, 132, 133, 134, 10, 136, 137, 138, 139, 15, 141, 142, 143, 144, 20, 146, 147, 148, 149, 25),
 'Rw': (0, 1, 2, 3, 54, 55, 6, 7, 8, 59, 60, 11, 12, 13, 64, 65, 16, 17, 18, 69, 70, 21, 22, 23, 74, 75, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 129, 130, 56, 57, 58, 134, 135, 61, 62, 63, 139, 140, 66, 67, 68, 144, 145, 71, 72, 73, 149, 150, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80, 25, 24, 103, 104, 105, 20, 19, 108, 109, 110, 15, 14, 113, 114, 115, 10, 9, 118, 119, 120, 5, 4, 123, 124, 125, 126, 127, 128, 122, 121, 131, 132, 133, 117, 116, 136, 137, 138, 112, 111, 141, 142, 143, 107, 106, 146, 147, 148, 102, 101),
 "Rw'": (0, 1, 2, 3, 122, 121, 6, 7, 8, 117, 116, 11, 12, 13, 112, 111, 16, 17, 18, 107, 106, 21, 22, 23, 102, 101, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 4, 5, 56, 57, 58, 9, 10, 61, 62, 63, 14, 15, 66, 67, 68, 19, 20, 71, 72, 73, 24, 25, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 150, 149, 103, 104, 105, 145, 144, 108, 109, 110, 140, 139, 113, 114, 115, 135, 134, 118, 119, 120, 130, 129, 123, 124, 125, 126, 127, 128, 54, 55, 131, 132, 133, 59, 60, 136, 137, 138, 64, 65, 141, 142, 143, 69, 70, 146, 147, 148, 74, 75),
 'Rw2': (0, 1, 2, 3, 129, 130, 6, 7, 8, 134, 135, 11, 12, 13, 139, 140, 16, 17, 18, 144, 145, 21, 22, 23, 149, 150, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 122, 121, 56, 57, 58, 117, 116, 61, 62, 63, 112, 111, 66, 67, 68, 107, 106, 71, 72, 73, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 103, 104, 105, 70, 69, 108, 109, 110, 65, 64, 113, 114, 115, 60, 59, 118, 119, 120, 55, 54, 123, 124, 125, 126, 127, 128, 4, 5, 131, 132, 133, 9, 10, 136, 137, 138, 14, 15, 141, 142, 143, 19, 20, 146, 147, 148, 24, 25),
 'U': (0, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 51, 52, 53, 54, 55, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 76, 77, 78, 79, 80, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 101, 102, 103, 104, 105, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 26, 27, 28, 29, 30, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "U'": (0, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 101, 102, 103, 104, 105, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 26, 27, 28, 29, 30, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 51, 52, 53, 54, 55, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 76, 77, 78, 79, 80, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'U2': (0, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 76, 77, 78, 79, 80, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 101, 102, 103, 104, 105, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 26, 27, 28, 29, 30, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 51, 52, 53, 54, 55, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'Uw': (0, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "Uw'": (0, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'Uw2': (0, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'x': (0, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101),
 "x'": (0, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75),
 'y': (0, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146),
 "y'": (0, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130),
 'z': (0, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130, 71, 66, 61, 56, 51, 72, 67, 62, 57, 52, 73, 68, 63, 58, 53, 74, 69, 64, 59, 54, 75, 70, 65, 60, 55, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 105, 110, 115, 120, 125, 104, 109, 114, 119, 124, 103, 108, 113, 118, 123, 102, 107, 112, 117, 122, 101, 106, 111, 116, 121, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80),
 "z'": (0, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 55, 60, 65, 70, 75, 54, 59, 64, 69, 74, 53, 58, 63, 68, 73, 52, 57, 62, 67, 72, 51, 56, 61, 66, 71, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146, 121, 116, 111, 106, 101, 122, 117, 112, 107, 102, 123, 118, 113, 108, 103, 124, 119, 114, 109, 104, 125, 120, 115, 110, 105, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46)}

def rotate_555(cube, step):
    return [cube[x] for x in swaps_555[step]]
