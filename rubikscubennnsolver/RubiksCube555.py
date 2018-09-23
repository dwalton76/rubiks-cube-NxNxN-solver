#!/usr/bin/env python3

from rubikscubennnsolver import RubiksCube, NotSolving, wing_str_map, wing_strs_all
from rubikscubennnsolver.misc import pre_steps_to_try, pre_steps_stage_l4e, wing_str_combos_two, wing_str_combos_four
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.LookupTable import (
    steps_on_same_face_and_layer,
    LookupTable,
    LookupTableCostOnly,
    LookupTableHashCostOnly,
    LookupTableIDA,
    LookupTableIDAViaC,
    NoIDASolution,
    NoPruneTableState,
    NoSteps,
)
from pprint import pformat
from random import randint
import os
import itertools
import logging
import subprocess
import sys

log = logging.getLogger(__name__)

moves_555 = (
    "U", "U'", "U2", "Uw", "Uw'", "Uw2",
    "L", "L'", "L2", "Lw", "Lw'", "Lw2",
    "F" , "F'", "F2", "Fw", "Fw'", "Fw2",
    "R" , "R'", "R2", "Rw", "Rw'", "Rw2",
    "B" , "B'", "B2", "Bw", "Bw'", "Bw2",
    "D" , "D'", "D2", "Dw", "Dw'", "Dw2",

    # slices...not used for now
    # "2U", "2U'", "2U2", "2D", "2D'", "2D2",
    # "2L", "2L'", "2L2", "2R", "2R'", "2R2",
    # "2F", "2F'", "2F2", "2B", "2B'", "2B2"
)
solved_555 = 'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB'


centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19, # Upper
    32, 33, 34, 37, 38, 39, 42, 43, 44, # Left
    57, 58, 59, 62, 63, 64, 67, 68, 69, # Front
    82, 83, 84, 87, 88, 89, 92, 93, 94, # Right
    107, 108, 109, 112, 113, 114, 117, 118, 119, # Back
    132, 133, 134, 137, 138, 139, 142, 143, 144  # Down
)

UD_centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19, # Upper
    132, 133, 134, 137, 138, 139, 142, 143, 144  # Down
)

LR_centers_555 = (
    32, 33, 34, 37, 38, 39, 42, 43, 44, # Left
    82, 83, 84, 87, 88, 89, 92, 93, 94  # Right
)

FB_centers_555 = (
    57, 58, 59, 62, 63, 64, 67, 68, 69, # Front
    107, 108, 109, 112, 113, 114, 117, 118, 119 # Back
)

UFBD_centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19, # Upper
    57, 58, 59, 62, 63, 64, 67, 68, 69, # Front
    107, 108, 109, 112, 113, 114, 117, 118, 119, # Back
    132, 133, 134, 137, 138, 139, 142, 143, 144  # Down
)

ULRD_centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19, # Upper
    32, 33, 34, 37, 38, 39, 42, 43, 44, # Left
    82, 83, 84, 87, 88, 89, 92, 93, 94, # Right
    132, 133, 134, 137, 138, 139, 142, 143, 144  # Down
)

LFRB_centers_555 = (
    32, 33, 34, 37, 38, 39, 42, 43, 44, # Left
    57, 58, 59, 62, 63, 64, 67, 68, 69, # Front
    82, 83, 84, 87, 88, 89, 92, 93, 94, # Right
    107, 108, 109, 112, 113, 114, 117, 118, 119 # Back
)

LFRB_x_centers_555 = (
    32, 34, 38, 42, 44, # Left
    57, 59, 63, 67, 69, # Front
    82, 84, 88, 92, 94, # Right
    107, 109, 113, 117, 119, # Back
)

LFRB_t_centers_555 = (
    33, 37, 38, 39, 43, # Left
    58, 62, 63, 64, 68, # Front
    83, 87, 88, 89, 93, # Right
    108, 112, 113, 114, 118, # Back
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

set_edges_555 = set(edges_555)

wings_555= (
    2, 3, 4, # Upper
    6, 11, 16,
    10, 15, 20,
    22, 23, 24,

    31, 36, 41, # Left
    35, 40, 45,

    81, 86, 91, # Right
    85, 90, 95,

    127, 128, 129, # Down
    131, 136, 141,
    135, 140, 145,
    147, 148, 149
)

l4e_wings_555 = (
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


wings_for_edges_pattern_555 = (
    2, 3, 4, # Upper
    6, 11, 16,
    10, 15, 20,
    22, 23, 24,

    31, 36, 41, # Left
    35, 40, 45,

    81, 86, 91, # Right
    85, 90, 95,

    127, 128, 129, # Down
    131, 136, 141,
    135, 140, 145,
    147, 148, 149
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
    27: 6,
    28: 11,
    29: 16,
    31: 110,
    35: 56,
    36: 115,
    40: 61,
    41: 120,
    45: 66,
    47: 141,
    48: 136,
    49: 131,
    52: 22,
    53: 23,
    54: 24,
    56: 35,
    60: 81,
    61: 40,
    65: 86,
    66: 45,
    70: 91,
    72: 127,
    73: 128,
    74: 129,
    77: 20,
    78: 15,
    79: 10,
    81: 60,
    85: 106,
    86: 65,
    90: 111,
    91: 70,
    95: 116,
    97: 135,
    98: 140,
    99: 145,
    102: 4,
    103: 3,
    104: 2,
    106: 85,
    110: 31,
    111: 90,
    115: 36,
    116: 95,
    120: 41,
    122: 149,
    123: 148,
    124: 147,
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


edges_recolor_tuples_555 = (
    ('0', 2, 104), # upper
    ('1', 4, 102),
    ('2', 6, 27),
    ('3', 10, 79),
    ('4', 16, 29),
    ('5', 20, 77),
    ('6', 22, 52),
    ('7', 24, 54),

    ('8', 31, 110), # left
    ('9', 35, 56),
    ('a', 41, 120),
    ('b', 45, 66),

    ('c', 81, 60), # right
    ('d', 85, 106),
    ('e', 91, 70),
    ('f', 95, 116),

    ('g', 127, 72), # down
    ('h', 129, 74),
    ('i', 131, 49),
    ('j', 135, 97),
    ('k', 141, 47),
    ('l', 145, 99),
    ('m', 147, 124),
    ('n', 149, 122)
)


midges_recolor_tuples_555 = (
    ('o', 3, 103), # upper
    ('p', 11, 28),
    ('q', 15, 78),
    ('r', 23, 53),

    ('s', 36, 115), # left
    ('t', 40, 61),

    ('u', 86, 65),  # right
    ('v', 90, 111),

    ('w', 128, 73), # down
    ('x', 136, 48),
    ('y', 140, 98),
    ('z', 148, 123)
)

midge_indexes = (
    3, 11, 15, 23, # Upper
    28, 36, 40, 48, # Left
    53, 61, 65, 73, # Front
    78, 86, 90, 98, # Right
    103, 111, 115, 123, # Back
    128, 136, 140, 148, # Down
)

wings_for_recolor_555= (
    ('0', 2, 104),  # upper
    ('1', 4, 102),
    ('2', 6, 27),
    ('3', 10, 79),
    ('4', 16, 29),
    ('5', 20, 77),
    ('6', 22, 52),
    ('7', 24, 54),

    ('8', 31, 110), # left
    ('9', 35, 56),
    ('a', 41, 120),
    ('b', 45, 66),

    ('c', 81, 60), # right
    ('d', 85, 106),
    ('e', 91, 70),
    ('f', 95, 116),

    ('g', 127, 72), # down
    ('h', 129, 74),
    ('i', 131, 49),
    ('j', 135, 97),
    ('k', 141, 47),
    ('l', 145, 99),
    ('m', 147, 124),
    ('n', 149, 122)
)


def edges_recolor_pattern_555(state, only_colors=[], uppercase_paired_edges=False):
    midges_map = {
        'UB': None,
        'UL': None,
        'UR': None,
        'UF': None,
        'LB': None,
        'LF': None,
        'RB': None,
        'RF': None,
        'DB': None,
        'DL': None,
        'DR': None,
        'DF': None,
        '--': None,
    }

    paired_edges_indexes = []

    if uppercase_paired_edges:
        for (s1, s2, s3) in (
            (2, 3, 4), # Upper
            (6, 11, 16),
            (10, 15, 20),
            (22, 23, 24),

            (31, 36, 41), # Left
            (35, 40, 45),

            (81, 86, 91), # Right
            (85, 90, 95),

            (127, 128, 129), # Down
            (131, 136, 141),
            (135, 140, 145),
            (147, 148, 149)):

            s1_value = state[s1]
            s2_value = state[s2]
            s3_value = state[s3]

            p1 = edges_partner_555[s1]
            p2 = edges_partner_555[s2]
            p3 = edges_partner_555[s3]

            p1_value = state[p1]
            p2_value = state[p2]
            p3_value = state[p3]

            if (s1_value != "-" and
                s1_value == s2_value and s2_value == s3_value and
                p1_value == p2_value and p2_value == p3_value):
                paired_edges_indexes.extend([s1, s2, s3, p1, p2, p3])

    for (edge_index, square_index, partner_index) in midges_recolor_tuples_555:
        square_value = state[square_index]
        partner_value = state[partner_index]

        if square_value == '-' or partner_value == '-':
            pass
        else:
            wing_str = wing_str_map[square_value + partner_value]
            midges_map[wing_str] = edge_index

            if only_colors and wing_str not in only_colors:
                state[square_index] = '-'
                state[partner_index] = '-'

            else:
                high_low = tsai_phase3_orient_edges_555[(square_index, partner_index, square_value, partner_value)]

                # If the edge is paired always use an uppercase letter to represent this edge
                if uppercase_paired_edges and square_index in paired_edges_indexes:
                    state[square_index] = midges_map[wing_str].upper()
                    state[partner_index] = midges_map[wing_str].upper()

                # If this is a high wing use the uppercase of the midge edge_index
                elif high_low == 'U':
                    state[square_index] = midges_map[wing_str].upper()
                    state[partner_index] = midges_map[wing_str].upper()

                # If this is a low wing use the lowercase of the midge edge_index
                elif high_low == 'D':
                    state[square_index] = midges_map[wing_str]
                    state[partner_index] = midges_map[wing_str]

                else:
                    raise Exception("(%s, %s, %s, %) high_low is %s" % (square_index, partner_index, square_value, partner_value, high_low))

    # Where is the midge for each high/low wing?
    for (edge_index, square_index, partner_index) in edges_recolor_tuples_555:
        square_value = state[square_index]
        partner_value = state[partner_index]

        if square_value == '-' or partner_value == '-':
            pass
        else:
            wing_str = wing_str_map[square_value + partner_value]

            if only_colors and wing_str not in only_colors:
                state[square_index] = '-'
                state[partner_index] = '-'

            # If the edge is paired always use an uppercase letter to represent this edge
            elif uppercase_paired_edges and square_index in paired_edges_indexes:
                state[square_index] = midges_map[wing_str].upper()
                state[partner_index] = midges_map[wing_str].upper()

            else:
                high_low = tsai_phase3_orient_edges_555[(square_index, partner_index, square_value, partner_value)]

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


class NoEdgeSolution(Exception):
    pass


class LookupTable555UDTCenterStage(LookupTable):
    """
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
    Average: 6.31 moves
    """

    t_centers_555 = (
        8, 12, 14, 18,
        33, 37, 39, 43,
        58, 62, 64, 68,
        83, 87, 89, 93,
        108, 112, 114, 118,
        133, 137, 139, 143
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.txt',
            'f0000f',
            linecount=735471,
            max_depth=8,
            filesize=27947898)

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in self.t_centers_555])
        return (self.hex_format % int(result, 2), 0)


class LookupTableIDA555UDCentersStage(LookupTableIDAViaC):
    """
    lookup-table-5x5x5-step10-UD-centers-stage.txt
    ==============================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 98 entries (0 percent, 19.60x previous step)
    3 steps has 2,036 entries (0 percent, 20.78x previous step)
    4 steps has 41,096 entries (4 percent, 20.18x previous step)
    5 steps has 824,950 entries (95 percent, 20.07x previous step)

    Total: 868,185 entries
    """

    def __init__(self, parent):

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (('lookup-table-5x5x5-step10-UD-centers-stage.txt', '343288ec28eeaaa2a02dede2c1485c10'),
             ('lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.cost-only.txt', '95464b63ec32f831c0f844916f3bbee9'),
             ('lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.cost-only.txt', '19679794a853d38a7d36be0f03fe1c3b')),
            '5x5x5-UD-centers-stage' # C_ida_type
        )

        self.recolor_positions = centers_555
        self.recolor_map = {
            'L' : 'x',
            'F' : 'x',
            'R' : 'x',
            'B' : 'x',
            'D' : 'U',
        }
        self.nuke_corners = True


class LookupTable555LRTCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step21-LR-t-centers-stage.txt
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

    LFRB_t_centers_555 = (
        33, 37, 39, 43,
        58, 62, 64, 68,
        83, 87, 89, 93,
        108, 112, 114, 118
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step21-LR-t-centers-stage.txt',
            'f0f0',
            linecount=12870,
            max_depth=9,
            filesize=476190)

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in self.LFRB_t_centers_555])
        return (self.hex_format % int(result, 2), 0)


class LookupTableIDA555LRCentersStage(LookupTableIDAViaC):
    """
    lookup-table-5x5x5-step20-LR-centers-stage.txt
    ==============================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 33 entries (0 percent, 11.00x previous step)
    3 steps has 374 entries (0 percent, 11.33x previous step)
    4 steps has 3,838 entries (0 percent, 10.26x previous step)
    5 steps has 39,254 entries (0 percent, 10.23x previous step)
    6 steps has 387,357 entries (0 percent, 9.87x previous step)
    7 steps has 3,374,380 entries (2 percent, 8.71x previous step)
    8 steps has 20,851,334 entries (12 percent, 6.18x previous step)
    9 steps has 65,556,972 entries (39 percent, 3.14x previous step)
    10 steps has 66,986,957 entries (40 percent, 1.02x previous step)
    11 steps has 8,423,610 entries (5 percent, 0.13x previous step)
    12 steps has 12,788 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 9.33 moves
    I only built this 6-deep


    lookup-table-5x5x5-step21-LR-t-centers-stage.txt
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


    lookup-table-5x5x5-step22-LR-x-centers-stage.txt
    ================================================
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

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (('lookup-table-5x5x5-step20-LR-centers-stage.txt', '9d982346d89494107f5a77323625c428'),
             ('lookup-table-5x5x5-step21-LR-t-centers-stage.cost-only.txt', '8fa5217b28c7aeb9e04684ae3f5bebee'),
             ('lookup-table-5x5x5-step22-LR-x-centers-stage.cost-only.txt', '4e4d8a8ec35d0c999ce7c51b6681bc4e')),
            '5x5x5-LR-centers-stage' # C_ida_type
        )

        self.recolor_positions = centers_555
        self.recolor_map = {
            'L' : 'L',
            'F' : 'F',
            'R' : 'L',
            'B' : 'F',
            'D' : 'x',
            'U' : 'x',
        }
        self.nuke_corners = True


class LookupTable555LRCenterStage(LookupTableHashCostOnly):
    """
    lookup-table-5x5x5-step20-LR-centers-stage.txt
    ==============================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 33 entries (0 percent, 11.00x previous step)
    3 steps has 374 entries (0 percent, 11.33x previous step)
    4 steps has 3,838 entries (0 percent, 10.26x previous step)
    5 steps has 39,254 entries (0 percent, 10.23x previous step)
    6 steps has 387,357 entries (0 percent, 9.87x previous step)
    7 steps has 3,374,380 entries (2 percent, 8.71x previous step)
    8 steps has 20,851,334 entries (12 percent, 6.18x previous step)
    9 steps has 65,556,972 entries (39 percent, 3.14x previous step)
    10 steps has 66,986,957 entries (40 percent, 1.02x previous step)
    11 steps has 8,423,610 entries (5 percent, 0.13x previous step)
    12 steps has 12,788 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 9.33 moves
    """

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step20-LR-centers-stage.hash-cost-only.txt',
            'ff803fe00',
            linecount=1,
            max_depth=12,
            bucketcount=165636907,
            filesize=165636908)

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        state = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in LFRB_centers_555])
        state = self.hex_format % int(state, 2)
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555ULFRBDCentersSolve(LookupTableIDAViaC):
    """
    24,010,000/117,649,000,000 is 0.000 204 so this will be a fast IDA search

    lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt
    ==================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 99 entries (0 percent, 14.14x previous step)
    3 steps has 1,134 entries (0 percent, 11.45x previous step)
    4 steps has 12,183 entries (0 percent, 10.74x previous step)
    5 steps has 128,730 entries (8 percent, 10.57x previous step)
    6 steps has 1,291,295 entries (90 percent, 10.03x previous step)

    Total: 1,433,448 entries


    lookup-table-5x5x5-step31-UL-centers-solve.txt
    lookup-table-5x5x5-step32-UF-centers-solve.txt
    lookup-table-5x5x5-step33-LF-centers-solve.txt
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
    Average: 9.25 moves
    """

    def __init__(self, parent):

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (('lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt', '5a0bad50c3e650dbd2677e29aba17eca'),
             ('lookup-table-5x5x5-step31-UL-centers-solve.hash-cost-only.txt', 'b9e47314dbbb37690d4aed370b3b2245'),
             ('lookup-table-5x5x5-step32-UF-centers-solve.hash-cost-only.txt', '966f865fffe4b5c2ce7301767c3f19f7'),
             ('lookup-table-5x5x5-step33-LF-centers-solve.hash-cost-only.txt', '7ea2ddf0e97094cc8f5d9c11df0176fe')),
            '5x5x5-centers-solve' # C_ida_type
        )

        self.recolor_positions = centers_555
        self.recolor_map = {
            'D' : 'x',
            'R' : 'x',
            'B' : 'x',
        }
        self.nuke_corners = True
        self.nuke_edges = True


class LookupTable555TCenterSolve(LookupTable):
    """
    This is only used when a cube larger than 7x7x7 is being solved. This is a non-hex
    build of the step32 table.

    lookup-table-5x5x5-step33-ULFRBD-t-centers-solve.txt
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
    Average: 6.23 moves
    """

    t_centers_555 = (
        8, 12, 14, 18,
        33, 37, 39, 43,
        58, 62, 64, 68,
        83, 87, 89, 93,
        108, 112, 114, 118,
        133, 137, 139, 143
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step33-ULFRBD-t-centers-solve.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD',
            linecount=343000,
            filesize=19551000,
        )

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.t_centers_555])
        return (result, 0)


class LookupTable555LRCenterStage432XCentersOnly(LookupTable):
    """
    lookup-table-5x5x5-step41-LR-centers-stage-432-x-centers-only.txt
    =================================================================
    1 steps has 46 entries (0 percent, 0.00x previous step)
    2 steps has 400 entries (0 percent, 8.70x previous step)
    3 steps has 3,490 entries (0 percent, 8.72x previous step)
    4 steps has 22,972 entries (2 percent, 6.58x previous step)
    5 steps has 119,852 entries (13 percent, 5.22x previous step)
    6 steps has 403,964 entries (44 percent, 3.37x previous step)
    7 steps has 345,232 entries (38 percent, 0.85x previous step)
    8 steps has 4,944 entries (0 percent, 0.01x previous step)

    Total: 900,900 entries
    Average: 6.20 moves
    """

    state_targets = (
        'LLLLLFFFFFRRRRRFFFFF',
        'LLLRRFFFFFLLRRRFFFFF',
        'LLLRRFFFFFRRRLLFFFFF',
        'LRLLRFFFFFLRRLRFFFFF',
        'LRLLRFFFFFRLRRLFFFFF',
        'LRLRLFFFFFRLRLRFFFFF',
        'RLLLRFFFFFLRRRLFFFFF',
        'RLLRLFFFFFLRRLRFFFFF',
        'RLLRLFFFFFRLRRLFFFFF',
        'RRLLLFFFFFLLRRRFFFFF',
        'RRLLLFFFFFRRRLLFFFFF',
        'RRLRRFFFFFLLRLLFFFFF'
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step41-LR-centers-stage-432-x-centers-only.txt',
            self.state_targets,
            linecount=900900,
            max_depth=8,
            filesize=45945900)

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        state = ''.join(['F' if parent_state[x] == 'B' else parent_state[x] for x in LFRB_x_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555LRCenterStage432TCentersOnly(LookupTable):
    """
    lookup-table-5x5x5-step42-LR-centers-stage-432-t-centers-only.txt
    =================================================================
    1 steps has 126 entries (0 percent, 0.00x previous step)
    2 steps has 968 entries (0 percent, 7.68x previous step)
    3 steps has 8,554 entries (0 percent, 8.84x previous step)
    4 steps has 38,220 entries (4 percent, 4.47x previous step)
    5 steps has 108,556 entries (12 percent, 2.84x previous step)
    6 steps has 270,972 entries (30 percent, 2.50x previous step)
    7 steps has 294,466 entries (32 percent, 1.09x previous step)
    8 steps has 164,936 entries (18 percent, 0.56x previous step)
    9 steps has 14,070 entries (1 percent, 0.09x previous step)
    10 steps has 32 entries (0 percent, 0.00x previous step)

    Total: 900,900 entries
    Average: 6.50 moves
    """

    state_targets = (
        'LLLLLFFFFFRRRRRFFFFF', 'LLLLRFFFFFLRRRRFFFFF', 'LLLLRFFFFFRRRRLFFFFF', 'LLLRLFFFFFRLRRRFFFFF',
        'LLLRLFFFFFRRRLRFFFFF', 'LLLRRFFFFFLLRRRFFFFF', 'LLLRRFFFFFLRRLRFFFFF', 'LLLRRFFFFFRLRRLFFFFF',
        'LLLRRFFFFFRRRLLFFFFF', 'LRLLLFFFFFRLRRRFFFFF', 'LRLLLFFFFFRRRLRFFFFF', 'LRLLRFFFFFLLRRRFFFFF',
        'LRLLRFFFFFLRRLRFFFFF', 'LRLLRFFFFFRLRRLFFFFF', 'LRLLRFFFFFRRRLLFFFFF', 'LRLRLFFFFFRLRLRFFFFF',
        'LRLRRFFFFFLLRLRFFFFF', 'LRLRRFFFFFRLRLLFFFFF', 'RLLLLFFFFFLRRRRFFFFF', 'RLLLLFFFFFRRRRLFFFFF',
        'RLLLRFFFFFLRRRLFFFFF', 'RLLRLFFFFFLLRRRFFFFF', 'RLLRLFFFFFLRRLRFFFFF', 'RLLRLFFFFFRLRRLFFFFF',
        'RLLRLFFFFFRRRLLFFFFF', 'RLLRRFFFFFLLRRLFFFFF', 'RLLRRFFFFFLRRLLFFFFF', 'RRLLLFFFFFLLRRRFFFFF',
        'RRLLLFFFFFLRRLRFFFFF', 'RRLLLFFFFFRLRRLFFFFF', 'RRLLLFFFFFRRRLLFFFFF', 'RRLLRFFFFFLLRRLFFFFF',
        'RRLLRFFFFFLRRLLFFFFF', 'RRLRLFFFFFLLRLRFFFFF', 'RRLRLFFFFFRLRLLFFFFF', 'RRLRRFFFFFLLRLLFFFFF'
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step42-LR-centers-stage-432-t-centers-only.txt',
            self.state_targets,
            linecount=900900,
            max_depth=10,
            filesize=48648600)

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        state = ''.join(['F' if parent_state[x] == 'B' else parent_state[x] for x in LFRB_t_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555LRCenterStage432(LookupTableIDA):
    """
    lookup-table-5x5x5-step40-LR-centers-stage-432.txt
    ==================================================
    1 steps has 1,692 entries (0 percent, 0.00x previous step)
    2 steps has 16,832 entries (0 percent, 9.95x previous step)
    3 steps has 194,000 entries (0 percent, 11.53x previous step)
    4 steps has 2,138,044 entries (8 percent, 11.02x previous step)
    5 steps has 23,791,796 entries (91 percent, 11.13x previous step)

    Total: 26,142,364 entries
    """

    state_targets = (
        'LLLLLLLLLFFFFFFFFFRRRRRRRRRFFFFFFFFF', 'LLLLLLLRLFFFFFFFFFRLRRRRRRRFFFFFFFFF', 'LLLLLLLRLFFFFFFFFFRRRRRRRLRFFFFFFFFF',
        'LLLLLLRLRFFFFFFFFFLRLRRRRRRFFFFFFFFF', 'LLLLLLRLRFFFFFFFFFRRRRRRLRLFFFFFFFFF', 'LLLLLLRRRFFFFFFFFFLLLRRRRRRFFFFFFFFF',
        'LLLLLLRRRFFFFFFFFFLRLRRRRLRFFFFFFFFF', 'LLLLLLRRRFFFFFFFFFRLRRRRLRLFFFFFFFFF', 'LLLLLLRRRFFFFFFFFFRRRRRRLLLFFFFFFFFF',
        'LLLLLRLLLFFFFFFFFFRRRLRRRRRFFFFFFFFF', 'LLLLLRLLLFFFFFFFFFRRRRRLRRRFFFFFFFFF', 'LLLLLRLRLFFFFFFFFFRLRLRRRRRFFFFFFFFF',
        'LLLLLRLRLFFFFFFFFFRLRRRLRRRFFFFFFFFF', 'LLLLLRLRLFFFFFFFFFRRRLRRRLRFFFFFFFFF', 'LLLLLRLRLFFFFFFFFFRRRRRLRLRFFFFFFFFF',
        'LLLLLRRLRFFFFFFFFFLRLLRRRRRFFFFFFFFF', 'LLLLLRRLRFFFFFFFFFLRLRRLRRRFFFFFFFFF', 'LLLLLRRLRFFFFFFFFFRRRLRRLRLFFFFFFFFF',
        'LLLLLRRLRFFFFFFFFFRRRRRLLRLFFFFFFFFF', 'LLLLLRRRRFFFFFFFFFLLLLRRRRRFFFFFFFFF', 'LLLLLRRRRFFFFFFFFFLLLRRLRRRFFFFFFFFF',
        'LLLLLRRRRFFFFFFFFFLRLLRRRLRFFFFFFFFF', 'LLLLLRRRRFFFFFFFFFLRLRRLRLRFFFFFFFFF', 'LLLLLRRRRFFFFFFFFFRLRLRRLRLFFFFFFFFF',
        'LLLLLRRRRFFFFFFFFFRLRRRLLRLFFFFFFFFF', 'LLLLLRRRRFFFFFFFFFRRRLRRLLLFFFFFFFFF', 'LLLLLRRRRFFFFFFFFFRRRRRLLLLFFFFFFFFF',
        'LLLRLLLLLFFFFFFFFFRRRLRRRRRFFFFFFFFF', 'LLLRLLLLLFFFFFFFFFRRRRRLRRRFFFFFFFFF', 'LLLRLLLRLFFFFFFFFFRLRLRRRRRFFFFFFFFF',
        'LLLRLLLRLFFFFFFFFFRLRRRLRRRFFFFFFFFF', 'LLLRLLLRLFFFFFFFFFRRRLRRRLRFFFFFFFFF', 'LLLRLLLRLFFFFFFFFFRRRRRLRLRFFFFFFFFF',
        'LLLRLLRLRFFFFFFFFFLRLLRRRRRFFFFFFFFF', 'LLLRLLRLRFFFFFFFFFLRLRRLRRRFFFFFFFFF', 'LLLRLLRLRFFFFFFFFFRRRLRRLRLFFFFFFFFF',
        'LLLRLLRLRFFFFFFFFFRRRRRLLRLFFFFFFFFF', 'LLLRLLRRRFFFFFFFFFLLLLRRRRRFFFFFFFFF', 'LLLRLLRRRFFFFFFFFFLLLRRLRRRFFFFFFFFF',
        'LLLRLLRRRFFFFFFFFFLRLLRRRLRFFFFFFFFF', 'LLLRLLRRRFFFFFFFFFLRLRRLRLRFFFFFFFFF', 'LLLRLLRRRFFFFFFFFFRLRLRRLRLFFFFFFFFF',
        'LLLRLLRRRFFFFFFFFFRLRRRLLRLFFFFFFFFF', 'LLLRLLRRRFFFFFFFFFRRRLRRLLLFFFFFFFFF', 'LLLRLLRRRFFFFFFFFFRRRRRLLLLFFFFFFFFF',
        'LLLRLRLLLFFFFFFFFFRRRLRLRRRFFFFFFFFF', 'LLLRLRLRLFFFFFFFFFRLRLRLRRRFFFFFFFFF', 'LLLRLRLRLFFFFFFFFFRRRLRLRLRFFFFFFFFF',
        'LLLRLRRLRFFFFFFFFFLRLLRLRRRFFFFFFFFF', 'LLLRLRRLRFFFFFFFFFRRRLRLLRLFFFFFFFFF', 'LLLRLRRRRFFFFFFFFFLLLLRLRRRFFFFFFFFF',
        'LLLRLRRRRFFFFFFFFFLRLLRLRLRFFFFFFFFF', 'LLLRLRRRRFFFFFFFFFRLRLRLLRLFFFFFFFFF', 'LLLRLRRRRFFFFFFFFFRRRLRLLLLFFFFFFFFF',
        'LLRLLLLLRFFFFFFFFFLRRRRRLRRFFFFFFFFF', 'LLRLLLLLRFFFFFFFFFRRLRRRRRLFFFFFFFFF', 'LLRLLLLRRFFFFFFFFFLLRRRRLRRFFFFFFFFF',
        'LLRLLLLRRFFFFFFFFFLRRRRRLLRFFFFFFFFF', 'LLRLLLLRRFFFFFFFFFRLLRRRRRLFFFFFFFFF', 'LLRLLLLRRFFFFFFFFFRRLRRRRLLFFFFFFFFF',
        'LLRLLLRLLFFFFFFFFFRRLRRRLRRFFFFFFFFF', 'LLRLLLRRLFFFFFFFFFRLLRRRLRRFFFFFFFFF', 'LLRLLLRRLFFFFFFFFFRRLRRRLLRFFFFFFFFF',
        'LLRLLRLLRFFFFFFFFFLRRLRRLRRFFFFFFFFF', 'LLRLLRLLRFFFFFFFFFLRRRRLLRRFFFFFFFFF', 'LLRLLRLLRFFFFFFFFFRRLLRRRRLFFFFFFFFF',
        'LLRLLRLLRFFFFFFFFFRRLRRLRRLFFFFFFFFF', 'LLRLLRLRRFFFFFFFFFLLRLRRLRRFFFFFFFFF', 'LLRLLRLRRFFFFFFFFFLLRRRLLRRFFFFFFFFF',
        'LLRLLRLRRFFFFFFFFFLRRLRRLLRFFFFFFFFF', 'LLRLLRLRRFFFFFFFFFLRRRRLLLRFFFFFFFFF', 'LLRLLRLRRFFFFFFFFFRLLLRRRRLFFFFFFFFF',
        'LLRLLRLRRFFFFFFFFFRLLRRLRRLFFFFFFFFF', 'LLRLLRLRRFFFFFFFFFRRLLRRRLLFFFFFFFFF', 'LLRLLRLRRFFFFFFFFFRRLRRLRLLFFFFFFFFF',
        'LLRLLRRLLFFFFFFFFFRRLLRRLRRFFFFFFFFF', 'LLRLLRRLLFFFFFFFFFRRLRRLLRRFFFFFFFFF', 'LLRLLRRRLFFFFFFFFFRLLLRRLRRFFFFFFFFF',
        'LLRLLRRRLFFFFFFFFFRLLRRLLRRFFFFFFFFF', 'LLRLLRRRLFFFFFFFFFRRLLRRLLRFFFFFFFFF', 'LLRLLRRRLFFFFFFFFFRRLRRLLLRFFFFFFFFF',
        'LLRRLLLLRFFFFFFFFFLRRLRRLRRFFFFFFFFF', 'LLRRLLLLRFFFFFFFFFLRRRRLLRRFFFFFFFFF', 'LLRRLLLLRFFFFFFFFFRRLLRRRRLFFFFFFFFF',
        'LLRRLLLLRFFFFFFFFFRRLRRLRRLFFFFFFFFF', 'LLRRLLLRRFFFFFFFFFLLRLRRLRRFFFFFFFFF', 'LLRRLLLRRFFFFFFFFFLLRRRLLRRFFFFFFFFF',
        'LLRRLLLRRFFFFFFFFFLRRLRRLLRFFFFFFFFF', 'LLRRLLLRRFFFFFFFFFLRRRRLLLRFFFFFFFFF', 'LLRRLLLRRFFFFFFFFFRLLLRRRRLFFFFFFFFF',
        'LLRRLLLRRFFFFFFFFFRLLRRLRRLFFFFFFFFF', 'LLRRLLLRRFFFFFFFFFRRLLRRRLLFFFFFFFFF', 'LLRRLLLRRFFFFFFFFFRRLRRLRLLFFFFFFFFF',
        'LLRRLLRLLFFFFFFFFFRRLLRRLRRFFFFFFFFF', 'LLRRLLRLLFFFFFFFFFRRLRRLLRRFFFFFFFFF', 'LLRRLLRRLFFFFFFFFFRLLLRRLRRFFFFFFFFF',
        'LLRRLLRRLFFFFFFFFFRLLRRLLRRFFFFFFFFF', 'LLRRLLRRLFFFFFFFFFRRLLRRLLRFFFFFFFFF', 'LLRRLLRRLFFFFFFFFFRRLRRLLLRFFFFFFFFF',
        'LLRRLRLLRFFFFFFFFFLRRLRLLRRFFFFFFFFF', 'LLRRLRLLRFFFFFFFFFRRLLRLRRLFFFFFFFFF', 'LLRRLRLRRFFFFFFFFFLLRLRLLRRFFFFFFFFF',
        'LLRRLRLRRFFFFFFFFFLRRLRLLLRFFFFFFFFF', 'LLRRLRLRRFFFFFFFFFRLLLRLRRLFFFFFFFFF', 'LLRRLRLRRFFFFFFFFFRRLLRLRLLFFFFFFFFF',
        'LLRRLRRLLFFFFFFFFFRRLLRLLRRFFFFFFFFF', 'LLRRLRRRLFFFFFFFFFRLLLRLLRRFFFFFFFFF', 'LLRRLRRRLFFFFFFFFFRRLLRLLLRFFFFFFFFF',
        'LRLLLLLLLFFFFFFFFFRLRRRRRRRFFFFFFFFF', 'LRLLLLLLLFFFFFFFFFRRRRRRRLRFFFFFFFFF', 'LRLLLLLRLFFFFFFFFFRLRRRRRLRFFFFFFFFF',
        'LRLLLLRLRFFFFFFFFFLLLRRRRRRFFFFFFFFF', 'LRLLLLRLRFFFFFFFFFLRLRRRRLRFFFFFFFFF', 'LRLLLLRLRFFFFFFFFFRLRRRRLRLFFFFFFFFF',
        'LRLLLLRLRFFFFFFFFFRRRRRRLLLFFFFFFFFF', 'LRLLLLRRRFFFFFFFFFLLLRRRRLRFFFFFFFFF', 'LRLLLLRRRFFFFFFFFFRLRRRRLLLFFFFFFFFF',
        'LRLLLRLLLFFFFFFFFFRLRLRRRRRFFFFFFFFF', 'LRLLLRLLLFFFFFFFFFRLRRRLRRRFFFFFFFFF', 'LRLLLRLLLFFFFFFFFFRRRLRRRLRFFFFFFFFF',
        'LRLLLRLLLFFFFFFFFFRRRRRLRLRFFFFFFFFF', 'LRLLLRLRLFFFFFFFFFRLRLRRRLRFFFFFFFFF', 'LRLLLRLRLFFFFFFFFFRLRRRLRLRFFFFFFFFF',
        'LRLLLRRLRFFFFFFFFFLLLLRRRRRFFFFFFFFF', 'LRLLLRRLRFFFFFFFFFLLLRRLRRRFFFFFFFFF', 'LRLLLRRLRFFFFFFFFFLRLLRRRLRFFFFFFFFF',
        'LRLLLRRLRFFFFFFFFFLRLRRLRLRFFFFFFFFF', 'LRLLLRRLRFFFFFFFFFRLRLRRLRLFFFFFFFFF', 'LRLLLRRLRFFFFFFFFFRLRRRLLRLFFFFFFFFF',
        'LRLLLRRLRFFFFFFFFFRRRLRRLLLFFFFFFFFF', 'LRLLLRRLRFFFFFFFFFRRRRRLLLLFFFFFFFFF', 'LRLLLRRRRFFFFFFFFFLLLLRRRLRFFFFFFFFF',
        'LRLLLRRRRFFFFFFFFFLLLRRLRLRFFFFFFFFF', 'LRLLLRRRRFFFFFFFFFRLRLRRLLLFFFFFFFFF', 'LRLLLRRRRFFFFFFFFFRLRRRLLLLFFFFFFFFF',
        'LRLRLLLLLFFFFFFFFFRLRLRRRRRFFFFFFFFF', 'LRLRLLLLLFFFFFFFFFRLRRRLRRRFFFFFFFFF', 'LRLRLLLLLFFFFFFFFFRRRLRRRLRFFFFFFFFF',
        'LRLRLLLLLFFFFFFFFFRRRRRLRLRFFFFFFFFF', 'LRLRLLLRLFFFFFFFFFRLRLRRRLRFFFFFFFFF', 'LRLRLLLRLFFFFFFFFFRLRRRLRLRFFFFFFFFF',
        'LRLRLLRLRFFFFFFFFFLLLLRRRRRFFFFFFFFF', 'LRLRLLRLRFFFFFFFFFLLLRRLRRRFFFFFFFFF', 'LRLRLLRLRFFFFFFFFFLRLLRRRLRFFFFFFFFF',
        'LRLRLLRLRFFFFFFFFFLRLRRLRLRFFFFFFFFF', 'LRLRLLRLRFFFFFFFFFRLRLRRLRLFFFFFFFFF', 'LRLRLLRLRFFFFFFFFFRLRRRLLRLFFFFFFFFF',
        'LRLRLLRLRFFFFFFFFFRRRLRRLLLFFFFFFFFF', 'LRLRLLRLRFFFFFFFFFRRRRRLLLLFFFFFFFFF', 'LRLRLLRRRFFFFFFFFFLLLLRRRLRFFFFFFFFF',
        'LRLRLLRRRFFFFFFFFFLLLRRLRLRFFFFFFFFF', 'LRLRLLRRRFFFFFFFFFRLRLRRLLLFFFFFFFFF', 'LRLRLLRRRFFFFFFFFFRLRRRLLLLFFFFFFFFF',
        'LRLRLRLLLFFFFFFFFFRLRLRLRRRFFFFFFFFF', 'LRLRLRLLLFFFFFFFFFRRRLRLRLRFFFFFFFFF', 'LRLRLRLRLFFFFFFFFFRLRLRLRLRFFFFFFFFF',
        'LRLRLRRLRFFFFFFFFFLLLLRLRRRFFFFFFFFF', 'LRLRLRRLRFFFFFFFFFLRLLRLRLRFFFFFFFFF', 'LRLRLRRLRFFFFFFFFFRLRLRLLRLFFFFFFFFF',
        'LRLRLRRLRFFFFFFFFFRRRLRLLLLFFFFFFFFF', 'LRLRLRRRRFFFFFFFFFLLLLRLRLRFFFFFFFFF', 'LRLRLRRRRFFFFFFFFFRLRLRLLLLFFFFFFFFF',
        'LRRLLLLLRFFFFFFFFFLLRRRRLRRFFFFFFFFF', 'LRRLLLLLRFFFFFFFFFLRRRRRLLRFFFFFFFFF', 'LRRLLLLLRFFFFFFFFFRLLRRRRRLFFFFFFFFF',
        'LRRLLLLLRFFFFFFFFFRRLRRRRLLFFFFFFFFF', 'LRRLLLLRRFFFFFFFFFLLRRRRLLRFFFFFFFFF', 'LRRLLLLRRFFFFFFFFFRLLRRRRLLFFFFFFFFF',
        'LRRLLLRLLFFFFFFFFFRLLRRRLRRFFFFFFFFF', 'LRRLLLRLLFFFFFFFFFRRLRRRLLRFFFFFFFFF', 'LRRLLLRRLFFFFFFFFFRLLRRRLLRFFFFFFFFF',
        'LRRLLRLLRFFFFFFFFFLLRLRRLRRFFFFFFFFF', 'LRRLLRLLRFFFFFFFFFLLRRRLLRRFFFFFFFFF', 'LRRLLRLLRFFFFFFFFFLRRLRRLLRFFFFFFFFF',
        'LRRLLRLLRFFFFFFFFFLRRRRLLLRFFFFFFFFF', 'LRRLLRLLRFFFFFFFFFRLLLRRRRLFFFFFFFFF', 'LRRLLRLLRFFFFFFFFFRLLRRLRRLFFFFFFFFF',
        'LRRLLRLLRFFFFFFFFFRRLLRRRLLFFFFFFFFF', 'LRRLLRLLRFFFFFFFFFRRLRRLRLLFFFFFFFFF', 'LRRLLRLRRFFFFFFFFFLLRLRRLLRFFFFFFFFF',
        'LRRLLRLRRFFFFFFFFFLLRRRLLLRFFFFFFFFF', 'LRRLLRLRRFFFFFFFFFRLLLRRRLLFFFFFFFFF', 'LRRLLRLRRFFFFFFFFFRLLRRLRLLFFFFFFFFF',
        'LRRLLRRLLFFFFFFFFFRLLLRRLRRFFFFFFFFF', 'LRRLLRRLLFFFFFFFFFRLLRRLLRRFFFFFFFFF', 'LRRLLRRLLFFFFFFFFFRRLLRRLLRFFFFFFFFF',
        'LRRLLRRLLFFFFFFFFFRRLRRLLLRFFFFFFFFF', 'LRRLLRRRLFFFFFFFFFRLLLRRLLRFFFFFFFFF', 'LRRLLRRRLFFFFFFFFFRLLRRLLLRFFFFFFFFF',
        'LRRRLLLLRFFFFFFFFFLLRLRRLRRFFFFFFFFF', 'LRRRLLLLRFFFFFFFFFLLRRRLLRRFFFFFFFFF', 'LRRRLLLLRFFFFFFFFFLRRLRRLLRFFFFFFFFF',
        'LRRRLLLLRFFFFFFFFFLRRRRLLLRFFFFFFFFF', 'LRRRLLLLRFFFFFFFFFRLLLRRRRLFFFFFFFFF', 'LRRRLLLLRFFFFFFFFFRLLRRLRRLFFFFFFFFF',
        'LRRRLLLLRFFFFFFFFFRRLLRRRLLFFFFFFFFF', 'LRRRLLLLRFFFFFFFFFRRLRRLRLLFFFFFFFFF', 'LRRRLLLRRFFFFFFFFFLLRLRRLLRFFFFFFFFF',
        'LRRRLLLRRFFFFFFFFFLLRRRLLLRFFFFFFFFF', 'LRRRLLLRRFFFFFFFFFRLLLRRRLLFFFFFFFFF', 'LRRRLLLRRFFFFFFFFFRLLRRLRLLFFFFFFFFF',
        'LRRRLLRLLFFFFFFFFFRLLLRRLRRFFFFFFFFF', 'LRRRLLRLLFFFFFFFFFRLLRRLLRRFFFFFFFFF', 'LRRRLLRLLFFFFFFFFFRRLLRRLLRFFFFFFFFF',
        'LRRRLLRLLFFFFFFFFFRRLRRLLLRFFFFFFFFF', 'LRRRLLRRLFFFFFFFFFRLLLRRLLRFFFFFFFFF', 'LRRRLLRRLFFFFFFFFFRLLRRLLLRFFFFFFFFF',
        'LRRRLRLLRFFFFFFFFFLLRLRLLRRFFFFFFFFF', 'LRRRLRLLRFFFFFFFFFLRRLRLLLRFFFFFFFFF', 'LRRRLRLLRFFFFFFFFFRLLLRLRRLFFFFFFFFF',
        'LRRRLRLLRFFFFFFFFFRRLLRLRLLFFFFFFFFF', 'LRRRLRLRRFFFFFFFFFLLRLRLLLRFFFFFFFFF', 'LRRRLRLRRFFFFFFFFFRLLLRLRLLFFFFFFFFF',
        'LRRRLRRLLFFFFFFFFFRLLLRLLRRFFFFFFFFF', 'LRRRLRRLLFFFFFFFFFRRLLRLLLRFFFFFFFFF', 'LRRRLRRRLFFFFFFFFFRLLLRLLLRFFFFFFFFF',
        'RLLLLLLLRFFFFFFFFFLRRRRRRRLFFFFFFFFF', 'RLLLLLLRRFFFFFFFFFLLRRRRRRLFFFFFFFFF', 'RLLLLLLRRFFFFFFFFFLRRRRRRLLFFFFFFFFF',
        'RLLLLLRLLFFFFFFFFFLRRRRRLRRFFFFFFFFF', 'RLLLLLRLLFFFFFFFFFRRLRRRRRLFFFFFFFFF', 'RLLLLLRRLFFFFFFFFFLLRRRRLRRFFFFFFFFF',
        'RLLLLLRRLFFFFFFFFFLRRRRRLLRFFFFFFFFF', 'RLLLLLRRLFFFFFFFFFRLLRRRRRLFFFFFFFFF', 'RLLLLLRRLFFFFFFFFFRRLRRRRLLFFFFFFFFF',
        'RLLLLRLLRFFFFFFFFFLRRLRRRRLFFFFFFFFF', 'RLLLLRLLRFFFFFFFFFLRRRRLRRLFFFFFFFFF', 'RLLLLRLRRFFFFFFFFFLLRLRRRRLFFFFFFFFF',
        'RLLLLRLRRFFFFFFFFFLLRRRLRRLFFFFFFFFF', 'RLLLLRLRRFFFFFFFFFLRRLRRRLLFFFFFFFFF', 'RLLLLRLRRFFFFFFFFFLRRRRLRLLFFFFFFFFF',
        'RLLLLRRLLFFFFFFFFFLRRLRRLRRFFFFFFFFF', 'RLLLLRRLLFFFFFFFFFLRRRRLLRRFFFFFFFFF', 'RLLLLRRLLFFFFFFFFFRRLLRRRRLFFFFFFFFF',
        'RLLLLRRLLFFFFFFFFFRRLRRLRRLFFFFFFFFF', 'RLLLLRRRLFFFFFFFFFLLRLRRLRRFFFFFFFFF', 'RLLLLRRRLFFFFFFFFFLLRRRLLRRFFFFFFFFF',
        'RLLLLRRRLFFFFFFFFFLRRLRRLLRFFFFFFFFF', 'RLLLLRRRLFFFFFFFFFLRRRRLLLRFFFFFFFFF', 'RLLLLRRRLFFFFFFFFFRLLLRRRRLFFFFFFFFF',
        'RLLLLRRRLFFFFFFFFFRLLRRLRRLFFFFFFFFF', 'RLLLLRRRLFFFFFFFFFRRLLRRRLLFFFFFFFFF', 'RLLLLRRRLFFFFFFFFFRRLRRLRLLFFFFFFFFF',
        'RLLRLLLLRFFFFFFFFFLRRLRRRRLFFFFFFFFF', 'RLLRLLLLRFFFFFFFFFLRRRRLRRLFFFFFFFFF', 'RLLRLLLRRFFFFFFFFFLLRLRRRRLFFFFFFFFF',
        'RLLRLLLRRFFFFFFFFFLLRRRLRRLFFFFFFFFF', 'RLLRLLLRRFFFFFFFFFLRRLRRRLLFFFFFFFFF', 'RLLRLLLRRFFFFFFFFFLRRRRLRLLFFFFFFFFF',
        'RLLRLLRLLFFFFFFFFFLRRLRRLRRFFFFFFFFF', 'RLLRLLRLLFFFFFFFFFLRRRRLLRRFFFFFFFFF', 'RLLRLLRLLFFFFFFFFFRRLLRRRRLFFFFFFFFF',
        'RLLRLLRLLFFFFFFFFFRRLRRLRRLFFFFFFFFF', 'RLLRLLRRLFFFFFFFFFLLRLRRLRRFFFFFFFFF', 'RLLRLLRRLFFFFFFFFFLLRRRLLRRFFFFFFFFF',
        'RLLRLLRRLFFFFFFFFFLRRLRRLLRFFFFFFFFF', 'RLLRLLRRLFFFFFFFFFLRRRRLLLRFFFFFFFFF', 'RLLRLLRRLFFFFFFFFFRLLLRRRRLFFFFFFFFF',
        'RLLRLLRRLFFFFFFFFFRLLRRLRRLFFFFFFFFF', 'RLLRLLRRLFFFFFFFFFRRLLRRRLLFFFFFFFFF', 'RLLRLLRRLFFFFFFFFFRRLRRLRLLFFFFFFFFF',
        'RLLRLRLLRFFFFFFFFFLRRLRLRRLFFFFFFFFF', 'RLLRLRLRRFFFFFFFFFLLRLRLRRLFFFFFFFFF', 'RLLRLRLRRFFFFFFFFFLRRLRLRLLFFFFFFFFF',
        'RLLRLRRLLFFFFFFFFFLRRLRLLRRFFFFFFFFF', 'RLLRLRRLLFFFFFFFFFRRLLRLRRLFFFFFFFFF', 'RLLRLRRRLFFFFFFFFFLLRLRLLRRFFFFFFFFF',
        'RLLRLRRRLFFFFFFFFFLRRLRLLLRFFFFFFFFF', 'RLLRLRRRLFFFFFFFFFRLLLRLRRLFFFFFFFFF', 'RLLRLRRRLFFFFFFFFFRRLLRLRLLFFFFFFFFF',
        'RLRLLLLLLFFFFFFFFFLRLRRRRRRFFFFFFFFF', 'RLRLLLLLLFFFFFFFFFRRRRRRLRLFFFFFFFFF', 'RLRLLLLRLFFFFFFFFFLLLRRRRRRFFFFFFFFF',
        'RLRLLLLRLFFFFFFFFFLRLRRRRLRFFFFFFFFF', 'RLRLLLLRLFFFFFFFFFRLRRRRLRLFFFFFFFFF', 'RLRLLLLRLFFFFFFFFFRRRRRRLLLFFFFFFFFF',
        'RLRLLLRLRFFFFFFFFFLRLRRRLRLFFFFFFFFF', 'RLRLLLRRRFFFFFFFFFLLLRRRLRLFFFFFFFFF', 'RLRLLLRRRFFFFFFFFFLRLRRRLLLFFFFFFFFF',
        'RLRLLRLLLFFFFFFFFFLRLLRRRRRFFFFFFFFF', 'RLRLLRLLLFFFFFFFFFLRLRRLRRRFFFFFFFFF', 'RLRLLRLLLFFFFFFFFFRRRLRRLRLFFFFFFFFF',
        'RLRLLRLLLFFFFFFFFFRRRRRLLRLFFFFFFFFF', 'RLRLLRLRLFFFFFFFFFLLLLRRRRRFFFFFFFFF', 'RLRLLRLRLFFFFFFFFFLLLRRLRRRFFFFFFFFF',
        'RLRLLRLRLFFFFFFFFFLRLLRRRLRFFFFFFFFF', 'RLRLLRLRLFFFFFFFFFLRLRRLRLRFFFFFFFFF', 'RLRLLRLRLFFFFFFFFFRLRLRRLRLFFFFFFFFF',
        'RLRLLRLRLFFFFFFFFFRLRRRLLRLFFFFFFFFF', 'RLRLLRLRLFFFFFFFFFRRRLRRLLLFFFFFFFFF', 'RLRLLRLRLFFFFFFFFFRRRRRLLLLFFFFFFFFF',
        'RLRLLRRLRFFFFFFFFFLRLLRRLRLFFFFFFFFF', 'RLRLLRRLRFFFFFFFFFLRLRRLLRLFFFFFFFFF', 'RLRLLRRRRFFFFFFFFFLLLLRRLRLFFFFFFFFF',
        'RLRLLRRRRFFFFFFFFFLLLRRLLRLFFFFFFFFF', 'RLRLLRRRRFFFFFFFFFLRLLRRLLLFFFFFFFFF', 'RLRLLRRRRFFFFFFFFFLRLRRLLLLFFFFFFFFF',
        'RLRRLLLLLFFFFFFFFFLRLLRRRRRFFFFFFFFF', 'RLRRLLLLLFFFFFFFFFLRLRRLRRRFFFFFFFFF', 'RLRRLLLLLFFFFFFFFFRRRLRRLRLFFFFFFFFF',
        'RLRRLLLLLFFFFFFFFFRRRRRLLRLFFFFFFFFF', 'RLRRLLLRLFFFFFFFFFLLLLRRRRRFFFFFFFFF', 'RLRRLLLRLFFFFFFFFFLLLRRLRRRFFFFFFFFF',
        'RLRRLLLRLFFFFFFFFFLRLLRRRLRFFFFFFFFF', 'RLRRLLLRLFFFFFFFFFLRLRRLRLRFFFFFFFFF', 'RLRRLLLRLFFFFFFFFFRLRLRRLRLFFFFFFFFF',
        'RLRRLLLRLFFFFFFFFFRLRRRLLRLFFFFFFFFF', 'RLRRLLLRLFFFFFFFFFRRRLRRLLLFFFFFFFFF', 'RLRRLLLRLFFFFFFFFFRRRRRLLLLFFFFFFFFF',
        'RLRRLLRLRFFFFFFFFFLRLLRRLRLFFFFFFFFF', 'RLRRLLRLRFFFFFFFFFLRLRRLLRLFFFFFFFFF', 'RLRRLLRRRFFFFFFFFFLLLLRRLRLFFFFFFFFF',
        'RLRRLLRRRFFFFFFFFFLLLRRLLRLFFFFFFFFF', 'RLRRLLRRRFFFFFFFFFLRLLRRLLLFFFFFFFFF', 'RLRRLLRRRFFFFFFFFFLRLRRLLLLFFFFFFFFF',
        'RLRRLRLLLFFFFFFFFFLRLLRLRRRFFFFFFFFF', 'RLRRLRLLLFFFFFFFFFRRRLRLLRLFFFFFFFFF', 'RLRRLRLRLFFFFFFFFFLLLLRLRRRFFFFFFFFF',
        'RLRRLRLRLFFFFFFFFFLRLLRLRLRFFFFFFFFF', 'RLRRLRLRLFFFFFFFFFRLRLRLLRLFFFFFFFFF', 'RLRRLRLRLFFFFFFFFFRRRLRLLLLFFFFFFFFF',
        'RLRRLRRLRFFFFFFFFFLRLLRLLRLFFFFFFFFF', 'RLRRLRRRRFFFFFFFFFLLLLRLLRLFFFFFFFFF', 'RLRRLRRRRFFFFFFFFFLRLLRLLLLFFFFFFFFF',
        'RRLLLLLLRFFFFFFFFFLLRRRRRRLFFFFFFFFF', 'RRLLLLLLRFFFFFFFFFLRRRRRRLLFFFFFFFFF', 'RRLLLLLRRFFFFFFFFFLLRRRRRLLFFFFFFFFF',
        'RRLLLLRLLFFFFFFFFFLLRRRRLRRFFFFFFFFF', 'RRLLLLRLLFFFFFFFFFLRRRRRLLRFFFFFFFFF', 'RRLLLLRLLFFFFFFFFFRLLRRRRRLFFFFFFFFF',
        'RRLLLLRLLFFFFFFFFFRRLRRRRLLFFFFFFFFF', 'RRLLLLRRLFFFFFFFFFLLRRRRLLRFFFFFFFFF', 'RRLLLLRRLFFFFFFFFFRLLRRRRLLFFFFFFFFF',
        'RRLLLRLLRFFFFFFFFFLLRLRRRRLFFFFFFFFF', 'RRLLLRLLRFFFFFFFFFLLRRRLRRLFFFFFFFFF', 'RRLLLRLLRFFFFFFFFFLRRLRRRLLFFFFFFFFF',
        'RRLLLRLLRFFFFFFFFFLRRRRLRLLFFFFFFFFF', 'RRLLLRLRRFFFFFFFFFLLRLRRRLLFFFFFFFFF', 'RRLLLRLRRFFFFFFFFFLLRRRLRLLFFFFFFFFF',
        'RRLLLRRLLFFFFFFFFFLLRLRRLRRFFFFFFFFF', 'RRLLLRRLLFFFFFFFFFLLRRRLLRRFFFFFFFFF', 'RRLLLRRLLFFFFFFFFFLRRLRRLLRFFFFFFFFF',
        'RRLLLRRLLFFFFFFFFFLRRRRLLLRFFFFFFFFF', 'RRLLLRRLLFFFFFFFFFRLLLRRRRLFFFFFFFFF', 'RRLLLRRLLFFFFFFFFFRLLRRLRRLFFFFFFFFF',
        'RRLLLRRLLFFFFFFFFFRRLLRRRLLFFFFFFFFF', 'RRLLLRRLLFFFFFFFFFRRLRRLRLLFFFFFFFFF', 'RRLLLRRRLFFFFFFFFFLLRLRRLLRFFFFFFFFF',
        'RRLLLRRRLFFFFFFFFFLLRRRLLLRFFFFFFFFF', 'RRLLLRRRLFFFFFFFFFRLLLRRRLLFFFFFFFFF', 'RRLLLRRRLFFFFFFFFFRLLRRLRLLFFFFFFFFF',
        'RRLRLLLLRFFFFFFFFFLLRLRRRRLFFFFFFFFF', 'RRLRLLLLRFFFFFFFFFLLRRRLRRLFFFFFFFFF', 'RRLRLLLLRFFFFFFFFFLRRLRRRLLFFFFFFFFF',
        'RRLRLLLLRFFFFFFFFFLRRRRLRLLFFFFFFFFF', 'RRLRLLLRRFFFFFFFFFLLRLRRRLLFFFFFFFFF', 'RRLRLLLRRFFFFFFFFFLLRRRLRLLFFFFFFFFF',
        'RRLRLLRLLFFFFFFFFFLLRLRRLRRFFFFFFFFF', 'RRLRLLRLLFFFFFFFFFLLRRRLLRRFFFFFFFFF', 'RRLRLLRLLFFFFFFFFFLRRLRRLLRFFFFFFFFF',
        'RRLRLLRLLFFFFFFFFFLRRRRLLLRFFFFFFFFF', 'RRLRLLRLLFFFFFFFFFRLLLRRRRLFFFFFFFFF', 'RRLRLLRLLFFFFFFFFFRLLRRLRRLFFFFFFFFF',
        'RRLRLLRLLFFFFFFFFFRRLLRRRLLFFFFFFFFF', 'RRLRLLRLLFFFFFFFFFRRLRRLRLLFFFFFFFFF', 'RRLRLLRRLFFFFFFFFFLLRLRRLLRFFFFFFFFF',
        'RRLRLLRRLFFFFFFFFFLLRRRLLLRFFFFFFFFF', 'RRLRLLRRLFFFFFFFFFRLLLRRRLLFFFFFFFFF', 'RRLRLLRRLFFFFFFFFFRLLRRLRLLFFFFFFFFF',
        'RRLRLRLLRFFFFFFFFFLLRLRLRRLFFFFFFFFF', 'RRLRLRLLRFFFFFFFFFLRRLRLRLLFFFFFFFFF', 'RRLRLRLRRFFFFFFFFFLLRLRLRLLFFFFFFFFF',
        'RRLRLRRLLFFFFFFFFFLLRLRLLRRFFFFFFFFF', 'RRLRLRRLLFFFFFFFFFLRRLRLLLRFFFFFFFFF', 'RRLRLRRLLFFFFFFFFFRLLLRLRRLFFFFFFFFF',
        'RRLRLRRLLFFFFFFFFFRRLLRLRLLFFFFFFFFF', 'RRLRLRRRLFFFFFFFFFLLRLRLLLRFFFFFFFFF', 'RRLRLRRRLFFFFFFFFFRLLLRLRLLFFFFFFFFF',
        'RRRLLLLLLFFFFFFFFFLLLRRRRRRFFFFFFFFF', 'RRRLLLLLLFFFFFFFFFLRLRRRRLRFFFFFFFFF', 'RRRLLLLLLFFFFFFFFFRLRRRRLRLFFFFFFFFF',
        'RRRLLLLLLFFFFFFFFFRRRRRRLLLFFFFFFFFF', 'RRRLLLLRLFFFFFFFFFLLLRRRRLRFFFFFFFFF', 'RRRLLLLRLFFFFFFFFFRLRRRRLLLFFFFFFFFF',
        'RRRLLLRLRFFFFFFFFFLLLRRRLRLFFFFFFFFF', 'RRRLLLRLRFFFFFFFFFLRLRRRLLLFFFFFFFFF', 'RRRLLLRRRFFFFFFFFFLLLRRRLLLFFFFFFFFF',
        'RRRLLRLLLFFFFFFFFFLLLLRRRRRFFFFFFFFF', 'RRRLLRLLLFFFFFFFFFLLLRRLRRRFFFFFFFFF', 'RRRLLRLLLFFFFFFFFFLRLLRRRLRFFFFFFFFF',
        'RRRLLRLLLFFFFFFFFFLRLRRLRLRFFFFFFFFF', 'RRRLLRLLLFFFFFFFFFRLRLRRLRLFFFFFFFFF', 'RRRLLRLLLFFFFFFFFFRLRRRLLRLFFFFFFFFF',
        'RRRLLRLLLFFFFFFFFFRRRLRRLLLFFFFFFFFF', 'RRRLLRLLLFFFFFFFFFRRRRRLLLLFFFFFFFFF', 'RRRLLRLRLFFFFFFFFFLLLLRRRLRFFFFFFFFF',
        'RRRLLRLRLFFFFFFFFFLLLRRLRLRFFFFFFFFF', 'RRRLLRLRLFFFFFFFFFRLRLRRLLLFFFFFFFFF', 'RRRLLRLRLFFFFFFFFFRLRRRLLLLFFFFFFFFF',
        'RRRLLRRLRFFFFFFFFFLLLLRRLRLFFFFFFFFF', 'RRRLLRRLRFFFFFFFFFLLLRRLLRLFFFFFFFFF', 'RRRLLRRLRFFFFFFFFFLRLLRRLLLFFFFFFFFF',
        'RRRLLRRLRFFFFFFFFFLRLRRLLLLFFFFFFFFF', 'RRRLLRRRRFFFFFFFFFLLLLRRLLLFFFFFFFFF', 'RRRLLRRRRFFFFFFFFFLLLRRLLLLFFFFFFFFF',
        'RRRRLLLLLFFFFFFFFFLLLLRRRRRFFFFFFFFF', 'RRRRLLLLLFFFFFFFFFLLLRRLRRRFFFFFFFFF', 'RRRRLLLLLFFFFFFFFFLRLLRRRLRFFFFFFFFF',
        'RRRRLLLLLFFFFFFFFFLRLRRLRLRFFFFFFFFF', 'RRRRLLLLLFFFFFFFFFRLRLRRLRLFFFFFFFFF', 'RRRRLLLLLFFFFFFFFFRLRRRLLRLFFFFFFFFF',
        'RRRRLLLLLFFFFFFFFFRRRLRRLLLFFFFFFFFF', 'RRRRLLLLLFFFFFFFFFRRRRRLLLLFFFFFFFFF', 'RRRRLLLRLFFFFFFFFFLLLLRRRLRFFFFFFFFF',
        'RRRRLLLRLFFFFFFFFFLLLRRLRLRFFFFFFFFF', 'RRRRLLLRLFFFFFFFFFRLRLRRLLLFFFFFFFFF', 'RRRRLLLRLFFFFFFFFFRLRRRLLLLFFFFFFFFF',
        'RRRRLLRLRFFFFFFFFFLLLLRRLRLFFFFFFFFF', 'RRRRLLRLRFFFFFFFFFLLLRRLLRLFFFFFFFFF', 'RRRRLLRLRFFFFFFFFFLRLLRRLLLFFFFFFFFF',
        'RRRRLLRLRFFFFFFFFFLRLRRLLLLFFFFFFFFF', 'RRRRLLRRRFFFFFFFFFLLLLRRLLLFFFFFFFFF', 'RRRRLLRRRFFFFFFFFFLLLRRLLLLFFFFFFFFF',
        'RRRRLRLLLFFFFFFFFFLLLLRLRRRFFFFFFFFF', 'RRRRLRLLLFFFFFFFFFLRLLRLRLRFFFFFFFFF', 'RRRRLRLLLFFFFFFFFFRLRLRLLRLFFFFFFFFF',
        'RRRRLRLLLFFFFFFFFFRRRLRLLLLFFFFFFFFF', 'RRRRLRLRLFFFFFFFFFLLLLRLRLRFFFFFFFFF', 'RRRRLRLRLFFFFFFFFFRLRLRLLLLFFFFFFFFF',
        'RRRRLRRLRFFFFFFFFFLLLLRLLRLFFFFFFFFF', 'RRRRLRRLRFFFFFFFFFLRLLRLLLLFFFFFFFFF', 'RRRRLRRRRFFFFFFFFFLLLLRLLLLFFFFFFFFF',
    )

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step40-LR-centers-stage-432.txt',
            self.state_targets,
            moves_555,

            # illegal moves
            ("Fw", "Fw'",
             "Bw", "Bw'",
             "Lw", "Lw'",
             "Rw", "Rw'"),

            # prune tables
            (parent.lt_LR_centers_stage_pt,
             parent.lt_LR_432_x_centers_only,
             parent.lt_LR_432_t_centers_only),
            linecount=26142364,
            max_depth=5,
            filesize=1490114748)

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        lt_state = ''.join(['F' if parent_state[x] == 'B' else parent_state[x] for x in LFRB_centers_555])

        (_, LR_stage_cost_to_goal) = self.parent.lt_LR_centers_stage_pt.ida_heuristic(ida_threshold)
        (_, LR_432_x_centers_cost_to_goal) = self.parent.lt_LR_432_x_centers_only.ida_heuristic(ida_threshold)
        (_, LR_432_t_centers_cost_to_goal) = self.parent.lt_LR_432_t_centers_only.ida_heuristic(ida_threshold)

        cost_to_goal = max(LR_stage_cost_to_goal, LR_432_x_centers_cost_to_goal, LR_432_t_centers_cost_to_goal)

        #self.parent.print_cube()
        #log.info("%s: lt_state %s, cost_to_goal %d, LR_stage_cost_to_goal %d, LR_432_x_centers_cost_to_goal %d, LR_432_t_centers_cost_to_goal %d" %
        #    (self, lt_state, cost_to_goal,
        #     LR_stage_cost_to_goal, LR_432_x_centers_cost_to_goal, LR_432_t_centers_cost_to_goal))
        return (lt_state, cost_to_goal)


class LookupTable555StageFirstFourEdges(LookupTable):
    """
    lookup-table-5x5x5-step100-stage-first-four-edges.txt
    =====================================================
    1 steps has 9 entries (0 percent, 0.00x previous step)
    2 steps has 72 entries (0 percent, 8.00x previous step)
    3 steps has 330 entries (0 percent, 4.58x previous step)
    4 steps has 84 entries (0 percent, 0.25x previous step)
    5 steps has 1,152 entries (0 percent, 13.71x previous step)
    6 steps has 10,200 entries (0 percent, 8.85x previous step)
    7 steps has 53,040 entries (0 percent, 5.20x previous step)
    8 steps has 187,296 entries (2 percent, 3.53x previous step)
    9 steps has 1,357,482 entries (18 percent, 7.25x previous step)
    10 steps has 5,779,878 entries (78 percent, 4.26x previous step)

    Total: 7,389,543 entries

    There is no need to build this any deeper...building it to 10-deep
    takes about 2 days on a 12-core machine.
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step100-stage-first-four-edges.txt',
            'TBD',
            linecount=7389543,
            filesize=421203951,
        )

    def state(self, wing_strs_to_stage):
        state = self.parent.state[:]

        for square_index in l4e_wings_555:
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in wing_strs_to_stage:
                state[square_index] = '1'
                state[partner_index] = '1'
            else:
                state[square_index] = '0'
                state[partner_index] = '0'

        edges_state = ''.join([state[square_index] for square_index in edges_555])
        edges_state = int(edges_state, 2)
        edges_state = self.hex_format % edges_state
        return edges_state


class LookupTable555EdgesSolveSecondFourEdgesOnly(LookupTable):
    """
    lookup-table-5x5x5-step241-solve-second-four-edges-edges-only.txt
    =================================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 30 entries (0 percent, 6.00x previous step)
    3 steps has 200 entries (0 percent, 6.67x previous step)
    4 steps has 1,296 entries (0 percent, 6.48x previous step)
    5 steps has 8,187 entries (0 percent, 6.32x previous step)
    6 steps has 49,334 entries (0 percent, 6.03x previous step)
    7 steps has 283,026 entries (0 percent, 5.74x previous step)
    8 steps has 1,528,102 entries (0 percent, 5.40x previous step)
    9 steps has 7,504,518 entries (3 percent, 4.91x previous step)
    10 steps has 30,068,326 entries (15 percent, 4.01x previous step)
    11 steps has 76,791,716 entries (38 percent, 2.55x previous step)
    12 steps has 72,115,012 entries (36 percent, 0.94x previous step)
    13 steps has 9,182,472 entries (4 percent, 0.13x previous step)
    14 steps has 35,776 entries (0 percent, 0.00x previous step)

    Total: 197,568,000 entries
    Average: 11.20 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step241-solve-second-four-edges-edges-only.txt',
            'OOo------rRR------------WWw------zZZ',
            linecount=197568000,
            max_depth=14,
            filesize=17188416000)

    def ida_heuristic(self, ida_threshold):
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        parent_state = self.parent.state
        state = edges_recolor_pattern_555(parent_state[:], self.only_colors)
        state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555EdgesSolveSecondFourEdgesOnlyHashCostOnly(LookupTableHashCostOnly):

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step241-solve-second-four-edges-edges-only.hash-cost-only.txt',
            'OOo------rRR------------WWw------zZZ',
            linecount=1,
            max_depth=14,
            bucketcount=197568011,
            filesize=197568012)

    def ida_heuristic(self, ida_threshold):
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        parent_state = self.parent.state
        state = edges_recolor_pattern_555(parent_state[:], self.only_colors)
        state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555ULFRBDCenterSolveSecondFour(LookupTable):
    """
    lookup-table-5x5x5-step242-ULFRBD-centers-solve.txt
    ===================================================
    1 steps has 168 entries (0 percent, 0.00x previous step)
    2 steps has 1,002 entries (0 percent, 5.96x previous step)
    3 steps has 5,544 entries (3 percent, 5.53x previous step)
    4 steps has 22,632 entries (12 percent, 4.08x previous step)
    5 steps has 67,770 entries (38 percent, 2.99x previous step)
    6 steps has 69,180 entries (39 percent, 1.02x previous step)
    7 steps has 10,056 entries (5 percent, 0.15x previous step)
    8 steps has 48 entries (0 percent, 0.00x previous step)

    Total: 176,400 entries
    Average: 5.29 moves
    """

    state_targets = (
        'DDDUUUDDDLLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBUUUDDDUUU',
        'DDDUUUDDDLLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDUUU',
        'DDDUUUDDDLLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDUUU',
        'DDDUUUDDDRLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDUUU',
        'DDDUUUDDDRLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDUUU',
        'DDDUUUDDDRLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBUUUDDDUUU',
        'DDDUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDUUU',
        'DDDUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBUUUDDDDDD',
        'DDDUUUUUULLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDUUU',
        'DDDUUUUUULLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDDDD',
        'DDDUUUUUULLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDUUU',
        'DDDUUUUUULLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDDDD',
        'DDDUUUUUURLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDUUU',
        'DDDUUUUUURLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDDDD',
        'DDDUUUUUURLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDUUU',
        'DDDUUUUUURLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDDDD',
        'DDDUUUUUURLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBDDDDDDUUU',
        'DDDUUUUUURLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBUUUDDDDDD',
        'UUUUUUDDDLLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDUUU',
        'UUUUUUDDDLLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBUUUDDDDDD',
        'UUUUUUDDDLLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDUUU',
        'UUUUUUDDDLLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDDDD',
        'UUUUUUDDDLLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDUUU',
        'UUUUUUDDDLLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDDDD',
        'UUUUUUDDDRLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDUUU',
        'UUUUUUDDDRLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDDDD',
        'UUUUUUDDDRLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDUUU',
        'UUUUUUDDDRLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDDDD',
        'UUUUUUDDDRLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBDDDDDDUUU',
        'UUUUUUDDDRLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBUUUDDDDDD',
        'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD',
        'UUUUUUUUULLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDDDD',
        'UUUUUUUUULLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDDDD',
        'UUUUUUUUURLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDDDD',
        'UUUUUUUUURLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDDDD',
        'UUUUUUUUURLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBDDDDDDDDD'
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step242-ULFRBD-centers-solve.txt',
            self.state_targets,
            linecount=176400,
            max_depth=8,
            filesize=14817600)

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        state = ''.join([parent_state[x] for x in centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555EdgesSolveSecondFour(LookupTableIDA):
    """
    lookup-table-5x5x5-step240-solve-second-four-edges.txt
    ======================================================
    1 steps has 180 entries (0 percent, 0.00x previous step)
    2 steps has 1,368 entries (0 percent, 7.60x previous step)
    3 steps has 11,436 entries (0 percent, 8.36x previous step)
    4 steps has 95,508 entries (1 percent, 8.35x previous step)
    5 steps has 807,948 entries (10 percent, 8.46x previous step)
    6 steps has 6,704,652 entries (87 percent, 8.30x previous step)

    Total: 7,621,092 entries
    """
    state_targets = (
        'DDDUUUDDDLLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBUUUDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUDDDLLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUDDDLLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUDDDRLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUDDDRLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUDDDRLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBUUUDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'DDDUUUUUULLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUUUULLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'DDDUUUUUULLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUUUULLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'DDDUUUUUURLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUUUURLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'DDDUUUUUURLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUUUURLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'DDDUUUUUURLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'DDDUUUUUURLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDLLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDLLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDLLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDLLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDLLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDLLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDRLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDRLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDRLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDRLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDRLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBDDDDDDUUUOOo------rRR------------WWw------zZZ',
        'UUUUUUDDDRLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBUUUDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUUUULLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUUUULLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUUUURLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBBDDDDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUUUURLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBBDDDDDDDDDOOo------rRR------------WWw------zZZ',
        'UUUUUUUUURLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBBDDDDDDDDDOOo------rRR------------WWw------zZZ',
    )

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step240-solve-second-four-edges.txt',
            self.state_targets,
            moves_555,

            # illegal moves
            (),

            # prune tables
            (parent.lt_step241_ht,
             parent.lt_step242),
            linecount=7621092,
            max_depth=6,
            filesize=868804488,
            legal_moves = (
                "U", "U'", "U2",
                "D", "D'", "D2",
                "L2", "F2", "R2", "B2",
                "Lw2", "Fw2", "Rw2", "Bw2",
            )
        )

    def ida_heuristic(self, ida_threshold):

        (edges_state, edges_cost) = self.parent.lt_step241_ht.ida_heuristic(ida_threshold)
        (centers_state, centers_cost) = self.parent.lt_step242.ida_heuristic(ida_threshold)

        lt_state = centers_state + edges_state
        cost_to_goal = max(edges_cost, centers_cost)
        #log.info("%s: lt_state %s, cost_to_goal %d, edges_cost %d, centers_cost %d" % (self, lt_state, cost_to_goal, edges_cost, centers_cost))

        return (lt_state, cost_to_goal)



class LookupTable555StageSecondFourEdges(LookupTable):
    """
    lookup-table-5x5x5-step102-stage-second-four-edges.txt
    ======================================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 8 entries (0 percent, 2.00x previous step)
    3 steps has 30 entries (0 percent, 3.75x previous step)
    4 steps has 28 entries (0 percent, 0.93x previous step)
    5 steps has 64 entries (0 percent, 2.29x previous step)
    6 steps has 400 entries (0 percent, 6.25x previous step)
    7 steps has 1,224 entries (0 percent, 3.06x previous step)
    8 steps has 3,864 entries (2 percent, 3.16x previous step)
    9 steps has 13,630 entries (8 percent, 3.53x previous step)
    10 steps has 45,090 entries (29 percent, 3.31x previous step)
    11 steps has 90,482 entries (58 percent, 2.01x previous step)

    Total: 154,824 entries

    This should have (16!/(8!*8!)) * (8!/(4!*4!)) or 900,900 entries
    if you built it out the entire way. We do not need to build it that deep
    though, we can try enough edge color combinations to find a hit
    in 11-deep.
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step101-stage-second-four-edges.txt',
            'TBD',
            linecount=154824,
            filesize=9289440)

    def state(self, wing_strs_to_stage):
        state = self.parent.state[:]

        for square_index in l4e_wings_555:
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in wing_strs_to_stage:
                state[square_index] = '1'
                state[partner_index] = '1'
            else:
                state[square_index] = '0'
                state[partner_index] = '0'

        edges_state = ''.join([state[square_index] for square_index in edges_555])
        edges_state = int(edges_state, 2)
        edges_state = self.hex_format % edges_state
        return edges_state


class LookupTable555EdgesLastFourXPlaneEdgesOnly(LookupTable):
    """
    lookup-table-5x5x5-step221-edges-last-four-x-plane-edges-only.txt
    =================================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 21 entries (0 percent, 3.00x previous step)
    3 steps has 90 entries (0 percent, 4.29x previous step)
    4 steps has 358 entries (0 percent, 3.98x previous step)
    5 steps has 1,204 entries (2 percent, 3.36x previous step)
    6 steps has 2,656 entries (6 percent, 2.21x previous step)
    7 steps has 6,084 entries (15 percent, 2.29x previous step)
    8 steps has 6,652 entries (16 percent, 1.09x previous step)
    9 steps has 9,016 entries (22 percent, 1.36x previous step)
    10 steps has 7,576 entries (18 percent, 0.84x previous step)
    11 steps has 5,480 entries (13 percent, 0.72x previous step)
    12 steps has 984 entries (2 percent, 0.18x previous step)
    13 steps has 192 entries (0 percent, 0.20x previous step)

    Total: 40,320 entries
    Average: 8.71 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step221-edges-last-four-x-plane-edges-only.txt',
            '------------sSSTTtuUUVVv------------',
            linecount=40320,
            max_depth=13,
            filesize=3346560)

    def ida_heuristic(self, ida_threshold):
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        state = edges_recolor_pattern_555(self.parent.state[:], self.only_colors)
        edges_state = ''.join([state[index] for index in wings_for_edges_pattern_555])

        cost_to_goal = self.heuristic(edges_state)
        return (edges_state, cost_to_goal)


class LookupTable555EdgesLastFourXPlaneCentersOnly(LookupTable):
    """
    lookup-table-5x5x5-step222-edges-last-four-x-plane-centers-only.txt
    ===================================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 33 entries (1 percent, 4.71x previous step)
    3 steps has 162 entries (6 percent, 4.91x previous step)
    4 steps has 504 entries (20 percent, 3.11x previous step)
    5 steps has 1,182 entries (46 percent, 2.35x previous step)
    6 steps has 632 entries (25 percent, 0.53x previous step)

    Total: 2,520 entries
    Average: 4.87 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step222-edges-last-four-x-plane-centers-only.txt',
            'LLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBB',
            linecount=2520,
            max_depth=6,
            filesize=146160)

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        state = ''.join([parent_state[x] for x in LFRB_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555EdgesLastFourXPlane(LookupTableIDA):
    """
    lookup-table-5x5x5-step220-edges-last-four-x-plane.txt
    ======================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 33 entries (0 percent, 4.71x previous step)
    3 steps has 230 entries (0 percent, 6.97x previous step)
    4 steps has 1,414 entries (0 percent, 6.15x previous step)
    5 steps has 8,768 entries (0 percent, 6.20x previous step)
    6 steps has 50,346 entries (2 percent, 5.74x previous step)
    7 steps has 280,506 entries (16 percent, 5.57x previous step)
    8 steps has 1,410,870 entries (80 percent, 5.03x previous step)

    Total: 1,752,174 entries
    Average: 7.76 moves
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step220-edges-last-four-x-plane.txt',
            ('LLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBB------------sSSTTtuUUVVv------------', ),
            moves_555,
            # illegal moves
            (),

            # prune tables
            (parent.lt_edges_pair_last_four_edges_only,
             parent.lt_edges_pair_last_four_centers_only),
            linecount=1752174,
            max_depth=8,
            filesize=180473922,
            legal_moves = (
                "L2", "F2", "R2", "B2",
                "Uw", "Uw'", "Uw2",
                "Dw", "Dw'", "Dw2",
            )
        )

    def ida_heuristic(self, ida_threshold):
        parent_state = self.parent.state
        (edges_state, edges_cost) = self.parent.lt_edges_pair_last_four_edges_only.ida_heuristic(ida_threshold)
        (centers_state, centers_cost) = self.parent.lt_edges_pair_last_four_centers_only.ida_heuristic(ida_threshold)
        lt_state = centers_state + edges_state
        cost_to_goal = max(edges_cost, centers_cost)
        return (lt_state, cost_to_goal)



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

    reduce333_orient_edges_tuples = (
        (2, 104), (3, 103), (4, 102), (6, 27), (10, 79), (11, 28), (15, 78), (16, 29), (20, 77), (22, 52), (23, 53), (24, 54),
        (27, 6), (28, 11), (29, 16), (31, 110), (35, 56), (36, 115), (40, 61), (41, 120), (45, 66), (47, 141), (48, 136), (49, 131),
        (52, 22), (53, 23), (54, 24), (56, 35), (60, 81), (61, 40), (65, 86), (66, 45), (70, 91), (72, 127), (73, 128), (74, 129),
        (77, 20), (78, 15), (79, 10), (81, 60), (85, 106), (86, 65), (90, 111), (91, 70), (95, 116), (97, 135), (98, 140), (99, 145),
        (102, 4), (103, 3), (104, 2), (106, 85), (110, 31), (111, 90), (115, 36), (116, 95), (120, 41), (122, 149), (123, 148), (124, 147),
        (127, 72), (128, 73), (129, 74), (131, 49), (135, 97), (136, 48), (140, 98), (141, 47), (145, 99), (147, 124), (148, 123), (149, 122)
    )

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCube.__init__(self, state, order, colormap)

        # This will be True when an even cube is using the 555 edge solver
        # to pair an orbit of edges
        self.avoid_pll = False

        if RubiksCube555.instantiated:
            #raise Exception("Another 5x5x5 instance is being created")
            #log.warning("Another 5x5x5 instance is being created")
            pass
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

    def get_x_plane_wing_strs(self):
        state = self.state
        edges_in_plane = set()

        for square_index in (31, 36, 41, 35, 40, 45, 81, 86, 91, 85, 90, 95):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            edges_in_plane.add(wing_str)
        return edges_in_plane

    def l4e_in_x_plane_paired(self):
        if (self.sideL.west_edge_paired() and
            self.sideL.east_edge_paired() and
            self.sideR.west_edge_paired() and
            self.sideR.east_edge_paired()):
            return True
        return False

    def l4e_in_x_plane(self):
        state = self.state
        edges_in_plane = set()

        for square_index in (31, 36, 41, 35, 40, 45, 81, 86, 91, 85, 90, 95):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            edges_in_plane.add(wing_str)

        #log.info("l4e_in_x_plane %s" % pformat(edges_in_plane))
        return len(edges_in_plane) == 4

    def l4e_in_y_plane_paired(self):
        if (self.sideU.north_edge_paired() and
            self.sideU.south_edge_paired() and
            self.sideD.north_edge_paired() and
            self.sideD.south_edge_paired()):
            return True
        return False

    def l4e_in_y_plane(self):
        state = self.state
        edges_in_plane = set()

        for square_index in (2, 3, 4, 22, 23, 24, 127, 128, 129, 147, 148, 149):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            edges_in_plane.add(wing_str)

        #log.info("l4e_in_y_plane %s" % pformat(edges_in_plane))
        return len(edges_in_plane) == 4

    def l4e_in_z_plane_paired(self):
        if (self.sideU.west_edge_paired() and
            self.sideU.east_edge_paired() and
            self.sideD.west_edge_paired() and
            self.sideD.east_edge_paired()):
            return True
        return False

    def l4e_in_z_plane(self):
        state = self.state
        edges_in_plane = set()

        for square_index in (6, 11, 16, 10, 15, 20, 131, 136, 141, 135, 140, 145):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            edges_in_plane.add(wing_str)

        #log.info("l4e_in_z_plane %s" % pformat(edges_in_plane))
        return len(edges_in_plane) == 4

    def get_paired_wings_count(self):
        return 24 - self.get_non_paired_wings_count()

    def LR_centers_colors(self):
        return set([self.state[x] for x in LR_centers_555])

    def FB_centers_colors(self):
        return set([self.state[x] for x in FB_centers_555])

    def UFBD_centers_colors(self):
        return set([self.state[x] for x in UFBD_centers_555])

    def UFBD_centers_color_count(self):
        return len(self.UFBD_centers_colors)

    def ULRD_centers_colors(self):
        return set([self.state[x] for x in ULRD_centers_555])

    def ULRD_centers_color_count(self):
        return len(self.ULRD_centers_colors)

    def LFRB_centers_colors(self):
        return set([self.state[x] for x in LFRB_centers_555])

    def LFRB_centers_color_count(self):
        return len(self.LFRB_centers_colors)

    def LFRB_centers_horizontal_bars(self):
        state = self.state

        for (a, b, c) in (
            (32, 33, 34),
            (37, 38, 39),
            (42, 43, 44),

            (57, 58, 59),
            (62, 63, 64),
            (67, 68, 69),

            (82, 83, 84),
            (87, 88, 89),
            (92, 93, 94),

            (107, 108, 109),
            (112, 113, 114),
            (117, 118, 119)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def LFRB_centers_vertical_bars(self):
        state = self.state

        for (a, b, c) in (
            (32, 37, 42),
            (33, 38, 43),
            (34, 39, 44),

            (57, 62, 67),
            (58, 63, 68),
            (59, 64, 69),

            (82, 87, 92),
            (83, 88, 93),
            (84, 89, 94),

            (107, 112, 117),
            (108, 113, 118),
            (109, 114, 119)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def U_centers_vertical_bars(self):
        state = self.state

        for (a, b, c) in (
            (7, 12, 17),
            (8, 13, 18),
            (9, 14, 19)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def D_centers_vertical_bars(self):
        state = self.state

        for (a, b, c) in (
            (132, 137, 142),
            (133, 138, 143),
            (134, 139, 144)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def UD_centers_vertical_bars(self):
        state = self.state

        for (a, b, c) in (
            (7, 12, 17),
            (8, 13, 18),
            (9, 14, 19),

            (132, 137, 142),
            (133, 138, 143),
            (134, 139, 144)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def UFBD_centers_vertical_bars(self):
        state = self.state

        for (a, b, c) in (
            (7, 12, 17),
            (8, 13, 18),
            (9, 14, 19),

            (57, 62, 67),
            (58, 63, 68),
            (59, 64, 69),

            (132, 137, 142),
            (133, 138, 143),
            (134, 139, 144),

            (107, 112, 117),
            (108, 113, 118),
            (109, 114, 119)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def L_centers_vertical_bars(self):
        state = self.state

        for (a, b, c) in (
            (32, 37, 42),
            (33, 38, 43),
            (34, 39, 44)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def R_centers_vertical_bars(self):
        state = self.state

        for (a, b, c) in (
            (82, 87, 92),
            (83, 88, 93),
            (84, 89, 94)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def LR_centers_vertical_bars(self):
        return self.L_centers_vertical_bars() and self.R_centers_vertical_bars()

    def L_centers_horizontal_bars(self):
        state = self.state

        for (a, b, c) in (
            (32, 33, 34),
            (37, 38, 39),
            (42, 43, 44)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def R_centers_horizontal_bars(self):
        state = self.state

        for (a, b, c) in (
            (82, 83, 84),
            (87, 88, 89),
            (92, 93, 94)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def LR_centers_horizontal_bars(self):
        return self.L_centers_horizontal_bars() and self.R_centers_horizontal_bars()

    def L_centers_bars(self):
        return self.L_centers_horizontal_bars() or self.L_centers_vertical_bars()

    def R_centers_bars(self):
        return self.R_centers_horizontal_bars() or self.R_centers_vertical_bars()

    def FB_centers_horizontal_bars(self):
        state = self.state

        for (a, b, c) in (
            (57, 58, 59),
            (62, 63, 64),
            (67, 68, 69),

            (107, 108, 109),
            (112, 113, 114),
            (117, 118, 119)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def FB_centers_vertical_bars(self):
        state = self.state

        for (a, b, c) in (
            (57, 62, 67),
            (58, 63, 68),
            (59, 64, 69),

            (107, 112, 117),
            (108, 113, 118),
            (109, 114, 119)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def U_centers_horizontal_bars(self):
        state = self.state

        for (a, b, c) in (
            (7, 8, 9),
            (12, 13, 14),
            (17, 18, 19)):

            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def D_centers_horizontal_bars(self):
        state = self.state

        for (a, b, c) in (
            (132, 133, 134),
            (137, 138, 139),
            (142, 143, 144)):
            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def UD_centers_horizontal_bars(self):
        state = self.state

        for (a, b, c) in (
            (7, 8, 9),
            (12, 13, 14),
            (17, 18, 19),

            (132, 133, 134),
            (137, 138, 139),
            (142, 143, 144)):
            if state[a] != state[b] or state[b] != state[c] or state[a] != state[c]:
                return False

        return True

    def sanity_check(self):
        centers = (13, 38, 63, 88, 113, 138)

        self._sanity_check('edge-orbit-0', edge_orbit_0_555, 8)
        self._sanity_check('edge-orbit-1', edge_orbit_1_555, 4)
        self._sanity_check('corners', corners_555, 4)
        #self._sanity_check('x-centers', x_centers_555, 4)
        #self._sanity_check('t-centers', t_centers_555, 4)
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
        self.lt_UD_centers_stage = LookupTableIDA555UDCentersStage(self)
        self.lt_LR_T_centers_stage = LookupTable555LRTCenterStage(self)
        self.lt_LR_centers_stage = LookupTableIDA555LRCentersStage(self)
        self.lt_ULFRBD_centers_solve = LookupTableIDA555ULFRBDCentersSolve(self)

        self.lt_LR_centers_stage_pt = LookupTable555LRCenterStage(self)
        self.lt_LR_432_x_centers_only = LookupTable555LRCenterStage432XCentersOnly(self)
        self.lt_LR_432_t_centers_only = LookupTable555LRCenterStage432TCentersOnly(self)
        self.lt_LR_432_centers_stage = LookupTableIDA555LRCenterStage432(self)
        self.lt_LR_432_x_centers_only.preload_cache_string()
        self.lt_LR_432_t_centers_only.preload_cache_string()

        self.lt_step241 = LookupTable555EdgesSolveSecondFourEdgesOnly(self)
        self.lt_step241_ht = LookupTable555EdgesSolveSecondFourEdgesOnlyHashCostOnly(self)
        self.lt_step242 = LookupTable555ULFRBDCenterSolveSecondFour(self)
        self.lt_step240 = LookupTableIDA555EdgesSolveSecondFour(self)
        self.lt_step242.preload_cache_dict()

        self.lt_edges_stage_first_four = LookupTable555StageFirstFourEdges(self)
        self.lt_edges_stage_second_four = LookupTable555StageSecondFourEdges(self)

        self.lt_edges_pair_last_four_edges_only = LookupTable555EdgesLastFourXPlaneEdgesOnly(self)
        self.lt_edges_pair_last_four_centers_only = LookupTable555EdgesLastFourXPlaneCentersOnly(self)
        self.lt_edges_pair_last_four = LookupTableIDA555EdgesLastFourXPlane(self)
        self.lt_edges_pair_last_four_edges_only.preload_cache_dict()
        self.lt_edges_pair_last_four_centers_only.preload_cache_dict()
        self.lt_edges_pair_last_four.preload_cache_dict()

        '''
        self.lt_edges_solve_second_four = LookupTable555SolveSecondFourEdges(self)

        if self.min_memory:
            self.lt_edges_stage_second_four.preload_cache_string()
        else:
            self.lt_edges_stage_second_four.preload_cache_dict()
        '''

        self.lt_ULFRBD_t_centers_solve = LookupTable555TCenterSolve(self)

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

        if x in midge_indexes or y in midge_indexes:
            is_midge = True
        else:
            is_midge = False

        # Now move that wing to its home edge
        if wing_str.startswith('U'):

            if wing_str == 'UB':
                self.move_wing_to_U_north(x)

                if is_midge:
                    high_edge_index = 3
                    low_edge_index = 103
                else:
                    high_edge_index = 2
                    low_edge_index = 4

            elif wing_str == 'UL':
                self.move_wing_to_U_west(x)

                if is_midge:
                    high_edge_index = 11
                    low_edge_index = 28
                else:
                    high_edge_index = 16
                    low_edge_index = 6

            elif wing_str == 'UR':
                self.move_wing_to_U_east(x)

                if is_midge:
                    high_edge_index = 15
                    low_edge_index = 78
                else:
                    high_edge_index = 10
                    low_edge_index = 20

            elif wing_str == 'UF':
                self.move_wing_to_U_south(x)

                if is_midge:
                    high_edge_index = 23
                    low_edge_index = 53
                else:
                    high_edge_index = 24
                    low_edge_index = 22

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if is_midge:
                if self.state[high_edge_index] == 'U':
                    result = 'U'
                elif self.state[low_edge_index] == 'U':
                    result = 'D'
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s" %
                        (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index], is_midge))
            else:
                if self.state[high_edge_index] == 'U':
                    result = 'U'
                elif self.state[low_edge_index] == 'U':
                    result = 'D'
                elif self.state[high_edge_index] == '.':
                    result = 'U'
                elif self.state[low_edge_index] == '.':
                    result = 'D'
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s" %
                        (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index], is_midge))

        elif wing_str.startswith('L'):

            if wing_str == 'LB':
                self.move_wing_to_L_west(x)

                if is_midge:
                    high_edge_index = 36
                    low_edge_index = 115
                else:
                    high_edge_index = 41
                    low_edge_index = 31

            elif wing_str == 'LF':
                self.move_wing_to_L_east(x)

                if is_midge:
                    high_edge_index = 40
                    low_edge_index = 61
                else:
                    high_edge_index = 35
                    low_edge_index = 45

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if is_midge:
                if self.state[high_edge_index] == 'L':
                    result = 'U'
                elif self.state[low_edge_index] == 'L':
                    result = 'D'
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s" %
                        (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index], is_midge))
            else:
                if self.state[high_edge_index] == 'L':
                    result = 'U'
                elif self.state[low_edge_index] == 'L':
                    result = 'D'
                elif self.state[high_edge_index] == '.':
                    result = 'U'
                elif self.state[low_edge_index] == '.':
                    result = 'D'
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                        (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        elif wing_str.startswith('R'):

            if wing_str == 'RB':
                self.move_wing_to_R_east(x)

                if is_midge:
                    high_edge_index = 90
                    low_edge_index = 111
                else:
                    high_edge_index = 85
                    low_edge_index = 95

            elif wing_str == 'RF':
                self.move_wing_to_R_west(x)

                if is_midge:
                    high_edge_index = 86
                    low_edge_index = 65
                else:
                    high_edge_index = 91
                    low_edge_index = 81

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if is_midge:
                if self.state[high_edge_index] == 'R':
                    result = 'U'
                elif self.state[low_edge_index] == 'R':
                    result = 'D'
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s" %
                        (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index], is_midge))
            else:
                if self.state[high_edge_index] == 'R':
                    result = 'U'
                elif self.state[low_edge_index] == 'R':
                    result = 'D'
                elif self.state[high_edge_index] == '.':
                    result = 'U'
                elif self.state[low_edge_index] == '.':
                    result = 'D'
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                        (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        elif wing_str.startswith('D'):
            if wing_str == 'DB':
                self.move_wing_to_D_south(x)

                if is_midge:
                    high_edge_index = 148
                    low_edge_index = 123
                else:
                    high_edge_index = 149
                    low_edge_index = 147

            elif wing_str == 'DL':
                self.move_wing_to_D_west(x)

                if is_midge:
                    high_edge_index = 136
                    low_edge_index = 48
                else:
                    high_edge_index = 141
                    low_edge_index = 131

            elif wing_str == 'DR':
                self.move_wing_to_D_east(x)

                if is_midge:
                    high_edge_index = 140
                    low_edge_index = 98
                else:
                    high_edge_index = 135
                    low_edge_index = 145

            elif wing_str == 'DF':
                self.move_wing_to_D_north(x)

                if is_midge:
                    high_edge_index = 128
                    low_edge_index = 73
                else:
                    high_edge_index = 127
                    low_edge_index = 129

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if is_midge:
                if self.state[high_edge_index] == 'D':
                    result = 'U'
                elif self.state[low_edge_index] == 'D':
                    result = 'D'
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s" %
                        (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index], is_midge))
            else:
                if self.state[high_edge_index] == 'D':
                    result = 'U'
                elif self.state[low_edge_index] == 'D':
                    result = 'D'
                elif self.state[high_edge_index] == '.':
                    result = 'U'
                elif self.state[low_edge_index] == '.':
                    result = 'D'
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                        (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        else:
            raise Exception("invalid wing_str %s" % wing_str)

        self.state = original_state[:]
        self.solution = original_solution[:]

        assert result in ('U', 'D')
        return result

    def build_highlow_edge_values(self):
        state = self.state
        new_highlow_edge_values = {}

        for x in range(1000000):

            # make random moves
            step = moves_555[randint(0, len(moves_555)-1)]

            if "w" in step:
                continue

            self.rotate(step)

            for (x, y) in self.reduce333_orient_edges_tuples:
                state_x = self.state[x]
                state_y = self.state[y]
                wing_str = wing_str_map[state_x + state_y]
                wing_tuple = (x, y, state_x, state_y)

                if wing_tuple not in new_highlow_edge_values:
                    new_highlow_edge_values[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str)

        print("new highlow_edge_values\n\n%s\n\n" % pformat(new_highlow_edge_values))
        log.info("new_highlow_edge_values has %d entries" % len(new_highlow_edge_values))
        sys.exit(0)

    def group_centers_stage_UD(self):
        """
        Stage UD centers.  The 7x7x7 uses this that is why it is in its own method.
        """
        self.lt_UD_centers_stage.solve()
        self.print_cube()
        log.info("%s: UD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_centers_stage_LR(self):
        """
        Stage LR centers.  The 6x6x6 uses this that is why it is in its own method.
        """
        # Stage LR centers
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        # Test the prune tables
        #self.lt_LR_T_centers_stage.solve()
        #self.lt_LR_X_centers_stage.solve()
        #self.print_cube()

        self.lt_LR_centers_stage.solve()
        self.print_cube()
        log.info("%s: ULFRBD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_centers_stage_LR_to_432(self):
        """
        """
        # Stage LR centers
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        # Test the prune tables
        #self.lt_LR_T_centers_stage.solve()
        #self.lt_LR_X_centers_stage.solve()
        #self.print_cube()

        self.lt_LR_432_centers_stage.solve()
        self.print_cube()
        log.info("%s: LR centers staged to one of 432 states, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_centers_guts(self):
        self.lt_init()
        self.group_centers_stage_UD()
        self.group_centers_stage_LR()
        #self.group_centers_stage_LR_to_432()

        # All centers are staged, solve them
        self.lt_ULFRBD_centers_solve.solve()
        #self.lt_ULFRBD_centers_solve_432.solve()
        self.print_cube()
        log.info("%s: ULFRBD centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def x_plane_has_paired_edge(self):
        if (self.sideL.west_edge_paired() or
            self.sideL.east_edge_paired() or
            self.sideR.west_edge_paired() or
            self.sideR.east_edge_paired()):
            return True
        return False

    def y_plane_has_paired_edge(self):
        if (self.sideF.north_edge_paired() or
            self.sideF.south_edge_paired() or
            self.sideB.north_edge_paired() or
            self.sideB.south_edge_paired()):
            return True
        return False

    def z_plane_has_paired_edge(self):
        if (self.sideU.west_edge_paired() or
            self.sideU.east_edge_paired() or
            self.sideD.west_edge_paired() or
            self.sideD.east_edge_paired()):
            return True
        return False

    def x_plane_has_LB_LF_RB_RF_edge(self):
        state = self.state
        LB_LF_RB_RF = set(('LB', 'LF', 'RB', 'RF'))

        for square_index in (36, 40, 86, 90):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in LB_LF_RB_RF:
                return True

        return False

    def y_plane_has_LB_LF_RB_RF_edge(self):
        state = self.state
        LB_LF_RB_RF = set(('LB', 'LF', 'RB', 'RF'))

        for square_index in (3, 23, 128, 148):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in LB_LF_RB_RF:
                return True

        return False

    def y_plane_has_DL_DR_edge(self):
        state = self.state
        DL_DR = set(('DL', 'DR'))

        for square_index in (3, 23, 128, 148):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in DL_DR:
                return True

        return False

    def z_plane_has_LB_LF_RB_RF_edge(self):
        state = self.state
        LB_LF_RB_RF = set(('LB', 'LF', 'RB', 'RF'))

        for square_index in (11, 15, 136, 140):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in LB_LF_RB_RF:
                return True

        return False

    def edges_flip_to_original_orientation(self):
        state = edges_recolor_pattern_555(self.state[:])
        edges_state = ''.join([state[index] for index in wings_for_edges_pattern_555])

        to_flip = []

        # 000 000 000 011 111 111 112 222 222 222 333 333
        # 012 345 678 901 234 567 890 123 456 789 012 345
        # Roo rPz Qqw qrP Sss TTt Uuu VVv ZwW Xxx YYy pzO
        #  ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^
        #  UB  UL  UR  UD  LB  LF  RF  RB  DF  DL  DR  DB
        for (edge_state_index, square_index, partner_index) in (
                (1, 3, 103),     # UB
                (4, 11, 28),     # UL
                (7, 15, 78),     # UR
                (10, 23, 53),    # UF
                (13, 36, 115),   # LB
                (16, 40, 61),    # LF
                (19, 86, 65),    # RF
                (22, 90, 111),   # RB
                (25, 128, 73),   # DF
                (28, 136, 48),   # DL
                (31, 140, 98),   # DR
                (34, 148, 123)): # DB

            if edges_state[edge_state_index].islower():
                square_value = self.state[square_index]
                partner_value = self.state[partner_index]
                wing_str = wing_str_map[square_value + partner_value]
                to_flip.append(wing_str)

        #log.info("%s: edges_flip_to_original_orientation %s" % (self, pformat(to_flip)))

        for square_index in wings_for_edges_pattern_555:
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in to_flip:
                self.state[square_index] = partner_value
                self.state[partner_index] = square_value

    def stage_first_four_edges_555(self):
        """
        There are 495 different permutations of 4-edges out of 12-edges, use the one
        that gives us the shortest solution for getting 4-edges staged to LB, LF, RF, RB
        """

        # return if they are already staged
        if self.l4e_in_x_plane():
            log.info("%s: first L4E group in x-plane" % self)
            return

        if self.l4e_in_y_plane():
            log.info("%s: first L4E group in y-plane, moving to x-plane" % self)
            self.rotate("z")
            return

        if self.l4e_in_z_plane():
            log.info("%s: first L4E group in z-plane, moving to x-plane" % self)
            self.rotate("x")
            return

        min_solution_len = None
        min_solution_steps = None

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
        # sequences put the cube in a state such that one of the 495 edge permutations does find
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
        original_solution_len = len(self.solution)

        for pre_steps in pre_steps_to_try:

            # do those steps
            for wing_strs in stage_first_four_edges_wing_str_combos:
                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in pre_steps:
                    self.rotate(step)

                state = self.lt_edges_stage_first_four.state(wing_strs)
                steps = self.lt_edges_stage_first_four.steps(state)

                if steps:

                    # Stage the 4-edges so we can pick the wing_strs whose solution will be the shortest
                    for step in steps:
                        self.rotate(step)

                    if self.l4e_in_x_plane() and not self.l4e_in_x_plane_paired():
                        pass
                    elif self.l4e_in_y_plane() and not self.l4e_in_y_plane_paired():
                        # dwalton remove this...temporary while we work on "pair 2nd L4E without staging"
                        continue
                        self.rotate("z")
                    elif self.l4e_in_z_plane() and not self.l4e_in_z_plane_paired():
                        # dwalton remove this...temporary while we work on "pair 2nd L4E without staging"
                        continue
                        self.rotate("x")
                    else:
                        raise Exception("L4E group but where?")

                    if not self.l4e_in_x_plane():
                        self.print_cube()
                        raise Exception("There should be an L4E group in x-plane but there is not")

                    solution_steps = self.solution[original_solution_len:]
                    solution_len = self.get_solution_len_minus_rotates(solution_steps)

                    if not self.second_l4e_solveable_without_staging():
                        log.info("%s: first four %s can be staged in %d steps but 2nd L4E would not be solveable" % (self, wing_strs, solution_len))
                        continue

                    if min_solution_len is None or solution_len < min_solution_len:
                        log.info("%s: first four %s can be staged in %d steps (NEW MIN)" % (self, wing_strs, solution_len))
                        min_solution_len = solution_len
                        min_solution_steps = solution_steps
                        break
                    else:
                        log.info("%s: first four %s can be staged in %d steps" % (self, wing_strs, solution_len))

            if min_solution_len is not None:
                #if pre_steps:
                #    log.info("pre-steps %s required to find a hit" % ' '.join(pre_steps))
                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in min_solution_steps:
                    self.rotate(step)

                if not self.l4e_in_x_plane():
                    self.print_cube()
                    raise Exception("There should be an L4E group in x-plane but there is not")
                break
        else:
            raise NoEdgeSolution("Could not find 4-edges to stage")

        log.info("%s: first four edges staged to x-plane, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def stage_second_four_edges_555(self):
        """
        The first four edges have been staged to LB, LF, RF, RB. Stage the next four
        edges to UB, UF, DF, DB (this in turn stages the final four edges).

        Since there are 8-edges there are 70 different combinations of edges we can
        choose to stage to UB, UF, DF, DB. Walk through all 70 combinations and see
        which one leads to the shortest solution.
        """

        # return if they are already staged
        if self.l4e_in_y_plane() and self.l4e_in_z_plane():
            return

        first_four_wing_strs = list(self.get_x_plane_wing_strs())
        wing_strs_for_second_four = []

        log.info("first_four_wing_strs %s" % pformat(first_four_wing_strs))

        for wing_str in wing_strs_all:
            if wing_str not in first_four_wing_strs:
                wing_strs_for_second_four.append(wing_str)

        log.info("wing_strs_for_second_four %s" % pformat(wing_strs_for_second_four))
        assert len(wing_strs_for_second_four) == 8
        min_solution_len = None
        min_solution_steps = None

        # Remember what things looked like
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)

        for pre_steps in pre_steps_to_try:

            for wing_strs in itertools.combinations(wing_strs_for_second_four, 4):
                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in pre_steps:
                    self.rotate(step)

                state = self.lt_edges_stage_second_four.state(wing_strs)
                steps = self.lt_edges_stage_second_four.steps(state)
                #log.info("%s: pre_steps %s, wing_strs %s, state %s, steps %s" % (
                #    self, pformat(pre_steps), wing_strs, state, pformat(steps)))

                if steps:

                    for step in steps:
                        self.rotate(step)

                    solution_steps = self.solution[original_solution_len:]
                    solution_len = self.get_solution_len_minus_rotates(solution_steps)

                    if min_solution_len is None or solution_len < min_solution_len:
                        min_solution_len = solution_len
                        min_solution_steps = solution_steps
                        log.info("%s: second four %s can be staged in %d steps (NEW MIN)" % (self, wing_strs, solution_len))
                    else:
                        log.info("%s: second four %s can be staged in %d steps" % (self, wing_strs, solution_len))

                    self.state = original_state[:]
                    self.solution = original_solution[:]

            if min_solution_len is not None:
                if pre_steps:
                    log.info("pre-steps %s required to find a hit" % ' '.join(pre_steps))

                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in min_solution_steps:
                    self.rotate(step)

                break

        self.state = original_state[:]
        self.solution = original_solution[:]

        if min_solution_len is None:
            raise SolveError("Could not find 4-edges to stage")
        else:
            for step in min_solution_steps:
                self.rotate(step)

    def place_first_four_paired_edges_in_x_plane(self):

        if self.l4e_in_x_plane_paired():
            log.info("%s: 4 paired edges in x-plane" % (self))
            return

        if self.l4e_in_y_plane_paired():
            log.info("%s: 4 paired edges in y-plane, moving to x-plane" % (self))
            self.rotate("z")
            return

        if self.l4e_in_z_plane_paired():
            log.info("%s: 4 paired edges in z-plane, moving to x-plane" % (self))
            self.rotate("x")
            return

        original_state = self.state[:]
        original_solution = self.solution[:]

        # Traverse a table of moves that place L4E in one of three planes
        for pre_steps in pre_steps_stage_l4e:
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in pre_steps:
                self.rotate(step)

            if self.l4e_in_x_plane_paired():
                log.info("%s: %s puts 4 paired edges in x-plane" % (self, "".join(pre_steps)))
                return

            if self.l4e_in_y_plane_paired():
                log.info("%s: %s puts 4 paired edges in y-plane" % (self, "".join(pre_steps)))
                self.rotate("z")
                return

            if self.l4e_in_z_plane() and not self.l4e_in_z_plane_paired():
                log.info("%s: %s puts 4 paired edges in z-plane" % (self, "".join(pre_steps)))
                self.rotate("x")
                return

        raise Exception("We should not be here")

    def pair_first_four_edges_via_l4e(self):
        paired_edges_count = self.get_paired_edges_count()

        # If there are already 4 paired edges all we need to do is put them in the x-plane
        if paired_edges_count >= 4:
            self.place_first_four_paired_edges_in_x_plane()
            log.info("%s: first four edges already paired, moved to x-plane, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # We do not have 4 paired edges, stage a L4E group to the x-plane and pair them via the L4E table
        else:
            self.stage_first_four_edges_555()
            self.pair_l4e_edges_in_x_plane()

    def get_y_plane_z_plane_wing_strs(self):
        result = []

        # The 4 paired edges are in the x-plane so look at midges in the y-plane and z-plane
        for square_index in (3, 11, 15, 23, 128, 136, 140, 148):
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            result.append(wing_str)

        return result

    def second_l4e_solveable_without_staging(self):
        """
        Return True if there is a wing_str_combo among the y-plane and z-plane
        edges that can be solved via our step241 table
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.edges_flip_to_original_orientation()
        eight_unpaired_wing_strs = self.get_y_plane_z_plane_wing_strs()
        states_to_find = []

        for wing_str_combo in itertools.combinations(eight_unpaired_wing_strs, 4):
            self.lt_step241.only_colors = wing_str_combo
            (edges_state, _) = self.lt_step241.ida_heuristic(99)
            states_to_find.append(edges_state)

        results = self.lt_step241.binary_search_multiple(states_to_find)
        self.lt_step241.only_colors = ()
        self.lt_step241_ht.only_colors = ()
        self.state = original_state[:]
        self.solution = original_solution[:]

        if results:
            return True
        else:
            return False

    def pair_second_four_edges_exp(self):
        paired_edges_count = self.get_paired_edges_count()

        if paired_edges_count >= 8:
            log.info("%s: second four edges already paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        else:
            #self.rotate_U_to_U()
            #self.rotate_F_to_F()
            original_state = self.state[:]
            original_solution = self.solution[:]
            original_solution_len = len(self.solution)
            original_paired_edges_count = self.get_paired_edges_count()

            self.edges_flip_to_original_orientation()
            post_edges_flip_state = self.state[:]
            eight_unpaired_wing_strs = self.get_y_plane_z_plane_wing_strs()

            # Find a wing_str_combo that is solveable
            for wing_str_combo in itertools.combinations(eight_unpaired_wing_strs, 4):
                self.lt_step241.only_colors = wing_str_combo
                self.lt_step241_ht.only_colors = wing_str_combo

                try:
                    self.lt_step241.solve()
                    self.state = post_edges_flip_state[:]
                    self.solution = original_solution[:]
                    #log.info("%s: pair_second_four_edges_exp wing_str_combo %s" % (self, pformat(wing_str_combo)))
                    break
                except NoSteps:
                    #log.info("%s: pair_second_four_edges_exp wing_str_combo %s (NO_STEPS)" % (self, pformat(wing_str_combo)))
                    continue
            else:
                raise SolveError("%s: None of the 2nd L4E wing_str_combo are solvable" % self)

            self.lt_step240.solve()
            second_l4e_solution = self.solution[original_solution_len:]
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in second_l4e_solution:
                self.rotate(step)

            self.print_cube()
            paired_edges_count = self.get_paired_edges_count()
            delta_paired_edges_count = paired_edges_count - original_paired_edges_count
            assert delta_paired_edges_count >= 4, "4-edges should have paired but only %d are paired" % delta_paired_edges_count
            log.info("%s: second four edges %s paired, %d steps in" % (
                (self, pformat(self.lt_step241.only_colors), self.get_solution_len_minus_rotates(self.solution))))
            self.lt_step241.only_colors = ()
            self.lt_step241_ht.only_colors = ()

    def pair_second_four_edges(self):
        paired_edges_count = self.get_paired_edges_count()

        if paired_edges_count >= 8:
            log.info("%s: second four edges already paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            return
        else:
            self.stage_second_four_edges_555()
            self.rotate("x")
            log.info("%s: second four edges L4E staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.pair_l4e_edges_in_x_plane()
            self.print_cube()
            #log.info("kociemba: %s" % self.get_kociemba_string(True))
            log.info("%s: second four edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def stage_final_four_edges_in_x_plane(self):
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Traverse a table of moves that place L4E in one of three planes
        # and then rotate that plane to the x-plane
        for pre_steps in pre_steps_stage_l4e:
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in pre_steps:
                self.rotate(step)

            if self.l4e_in_x_plane() and not self.l4e_in_x_plane_paired():
                if pre_steps:
                    log.info("%s: %s puts L4E group in x-plane" % (self, "".join(pre_steps)))
                else:
                    log.info("%s: L4E group in x-plane" % self)
                break

            elif self.l4e_in_y_plane() and not self.l4e_in_y_plane_paired():
                if pre_steps:
                    log.info("%s: %s puts L4E group in y-plane, moving to x-plane" % (self, "".join(pre_steps)))
                else:
                    log.info("%s: L4E group in y-plane, moving to x-plane" % self)
                self.rotate("z")
                break

            elif self.l4e_in_z_plane() and not self.l4e_in_z_plane_paired():
                if pre_steps:
                    log.info("%s: %s puts L4E group in z-plane" % (self, "".join(pre_steps)))
                else:
                    log.info("%s: L4E group in z-plane, moving to x-plane" % self)
                self.rotate("x")
                break

        log.info("%s: final four edges placed in x-plane, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def pair_l4e_edges_in_x_plane(self):

        if not self.l4e_in_x_plane():
            raise SolveError("There must be a L4E group of edges in the x-plane")

        if self.l4e_in_x_plane_paired():
            log.info("%s: x-plane edges already paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            return

        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)
        original_paired_edges_count = self.get_paired_edges_count()

        # The 4 paired edges are in the x-plane
        only_colors = []
        for square_index in (36, 40, 86, 90):
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            only_colors.append(wing_str)
        self.lt_edges_pair_last_four_edges_only.only_colors = only_colors
        self.lt_edges_pair_last_four.only_colors = only_colors

        # Recolor the centers in the x-plane to LFRB since LFRB was used to build our tables
        centers_recolor = {
            self.state[38] : "L",
            self.state[63] : "F",
            self.state[88] : "R",
            self.state[113] : "B",
        }

        for x in LFRB_centers_555:
            self.state[x] = centers_recolor[self.state[x]]

        # Recolor the edges to they are all oriented using their original orientation.
        # We do this because our tables were built will all edges at their original orientation.
        self.edges_flip_to_original_orientation()

        #log.info("%s: only_colors %s" % (self, pformat(only_colors)))
        #log.info("%s: centers_recolor %s" % (self, pformat(centers_recolor)))

        # Now we can solve
        self.lt_edges_pair_last_four.solve()

        # Put the cube back the way it was (to undo all of the recoloring we did) and apply the solution
        l4e_solution = self.solution[original_solution_len:]
        self.state = original_state[:]
        self.solution = original_solution[:]

        for step in l4e_solution:
            self.rotate(step)

        self.print_cube()
        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        paired_edges_count = self.get_paired_edges_count()
        delta_paired_edges_count = paired_edges_count - original_paired_edges_count
        assert delta_paired_edges_count >= 4, "4-edges should have paired but only %d are paired" % delta_paired_edges_count
        log.info("%s: x-plane edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_edges(self):
        paired_edges_count = self.get_paired_edges_count()

        if paired_edges_count == 12:
            return

        self.lt_init()
        self.pair_first_four_edges_via_l4e() # 55 steps at end
        log.info("kociemba: %s" % self.get_kociemba_string(True))

        #self.pair_second_four_edges() # 75 steps at end
        self.pair_second_four_edges_exp()
        self.stage_final_four_edges_in_x_plane()
        self.pair_l4e_edges_in_x_plane()
        self.rotate_U_to_U()
        self.rotate_F_to_F()
        self.print_cube()
        sys.exit(0)


tsai_phase3_orient_edges_555 = {
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
    (3, 103, 'B', 'D'): 'D',
    (3, 103, 'B', 'L'): 'D',
    (3, 103, 'B', 'R'): 'D',
    (3, 103, 'B', 'U'): 'D',
    (3, 103, 'D', 'B'): 'U',
    (3, 103, 'D', 'F'): 'U',
    (3, 103, 'D', 'L'): 'U',
    (3, 103, 'D', 'R'): 'U',
    (3, 103, 'F', 'D'): 'D',
    (3, 103, 'F', 'L'): 'D',
    (3, 103, 'F', 'R'): 'D',
    (3, 103, 'F', 'U'): 'D',
    (3, 103, 'L', 'B'): 'U',
    (3, 103, 'L', 'D'): 'D',
    (3, 103, 'L', 'F'): 'U',
    (3, 103, 'L', 'U'): 'D',
    (3, 103, 'R', 'B'): 'U',
    (3, 103, 'R', 'D'): 'D',
    (3, 103, 'R', 'F'): 'U',
    (3, 103, 'R', 'U'): 'D',
    (3, 103, 'U', 'B'): 'U',
    (3, 103, 'U', 'F'): 'U',
    (3, 103, 'U', 'L'): 'U',
    (3, 103, 'U', 'R'): 'U',
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
    (11, 28, 'B', 'D'): 'D',
    (11, 28, 'B', 'L'): 'D',
    (11, 28, 'B', 'R'): 'D',
    (11, 28, 'B', 'U'): 'D',
    (11, 28, 'D', 'B'): 'U',
    (11, 28, 'D', 'F'): 'U',
    (11, 28, 'D', 'L'): 'U',
    (11, 28, 'D', 'R'): 'U',
    (11, 28, 'F', 'D'): 'D',
    (11, 28, 'F', 'L'): 'D',
    (11, 28, 'F', 'R'): 'D',
    (11, 28, 'F', 'U'): 'D',
    (11, 28, 'L', 'B'): 'U',
    (11, 28, 'L', 'D'): 'D',
    (11, 28, 'L', 'F'): 'U',
    (11, 28, 'L', 'U'): 'D',
    (11, 28, 'R', 'B'): 'U',
    (11, 28, 'R', 'D'): 'D',
    (11, 28, 'R', 'F'): 'U',
    (11, 28, 'R', 'U'): 'D',
    (11, 28, 'U', 'B'): 'U',
    (11, 28, 'U', 'F'): 'U',
    (11, 28, 'U', 'L'): 'U',
    (11, 28, 'U', 'R'): 'U',
    (15, 78, 'B', 'D'): 'D',
    (15, 78, 'B', 'L'): 'D',
    (15, 78, 'B', 'R'): 'D',
    (15, 78, 'B', 'U'): 'D',
    (15, 78, 'D', 'B'): 'U',
    (15, 78, 'D', 'F'): 'U',
    (15, 78, 'D', 'L'): 'U',
    (15, 78, 'D', 'R'): 'U',
    (15, 78, 'F', 'D'): 'D',
    (15, 78, 'F', 'L'): 'D',
    (15, 78, 'F', 'R'): 'D',
    (15, 78, 'F', 'U'): 'D',
    (15, 78, 'L', 'B'): 'U',
    (15, 78, 'L', 'D'): 'D',
    (15, 78, 'L', 'F'): 'U',
    (15, 78, 'L', 'U'): 'D',
    (15, 78, 'R', 'B'): 'U',
    (15, 78, 'R', 'D'): 'D',
    (15, 78, 'R', 'F'): 'U',
    (15, 78, 'R', 'U'): 'D',
    (15, 78, 'U', 'B'): 'U',
    (15, 78, 'U', 'F'): 'U',
    (15, 78, 'U', 'L'): 'U',
    (15, 78, 'U', 'R'): 'U',
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
    (23, 53, 'B', 'D'): 'D',
    (23, 53, 'B', 'L'): 'D',
    (23, 53, 'B', 'R'): 'D',
    (23, 53, 'B', 'U'): 'D',
    (23, 53, 'D', 'B'): 'U',
    (23, 53, 'D', 'F'): 'U',
    (23, 53, 'D', 'L'): 'U',
    (23, 53, 'D', 'R'): 'U',
    (23, 53, 'F', 'D'): 'D',
    (23, 53, 'F', 'L'): 'D',
    (23, 53, 'F', 'R'): 'D',
    (23, 53, 'F', 'U'): 'D',
    (23, 53, 'L', 'B'): 'U',
    (23, 53, 'L', 'D'): 'D',
    (23, 53, 'L', 'F'): 'U',
    (23, 53, 'L', 'U'): 'D',
    (23, 53, 'R', 'B'): 'U',
    (23, 53, 'R', 'D'): 'D',
    (23, 53, 'R', 'F'): 'U',
    (23, 53, 'R', 'U'): 'D',
    (23, 53, 'U', 'B'): 'U',
    (23, 53, 'U', 'F'): 'U',
    (23, 53, 'U', 'L'): 'U',
    (23, 53, 'U', 'R'): 'U',
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
    (28, 11, 'B', 'D'): 'U',
    (28, 11, 'B', 'L'): 'U',
    (28, 11, 'B', 'R'): 'U',
    (28, 11, 'B', 'U'): 'U',
    (28, 11, 'D', 'B'): 'D',
    (28, 11, 'D', 'F'): 'D',
    (28, 11, 'D', 'L'): 'D',
    (28, 11, 'D', 'R'): 'D',
    (28, 11, 'F', 'D'): 'U',
    (28, 11, 'F', 'L'): 'U',
    (28, 11, 'F', 'R'): 'U',
    (28, 11, 'F', 'U'): 'U',
    (28, 11, 'L', 'B'): 'D',
    (28, 11, 'L', 'D'): 'U',
    (28, 11, 'L', 'F'): 'D',
    (28, 11, 'L', 'U'): 'U',
    (28, 11, 'R', 'B'): 'D',
    (28, 11, 'R', 'D'): 'U',
    (28, 11, 'R', 'F'): 'D',
    (28, 11, 'R', 'U'): 'U',
    (28, 11, 'U', 'B'): 'D',
    (28, 11, 'U', 'F'): 'D',
    (28, 11, 'U', 'L'): 'D',
    (28, 11, 'U', 'R'): 'D',
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
    (36, 115, 'B', 'D'): 'D',
    (36, 115, 'B', 'L'): 'D',
    (36, 115, 'B', 'R'): 'D',
    (36, 115, 'B', 'U'): 'D',
    (36, 115, 'D', 'B'): 'U',
    (36, 115, 'D', 'F'): 'U',
    (36, 115, 'D', 'L'): 'U',
    (36, 115, 'D', 'R'): 'U',
    (36, 115, 'F', 'D'): 'D',
    (36, 115, 'F', 'L'): 'D',
    (36, 115, 'F', 'R'): 'D',
    (36, 115, 'F', 'U'): 'D',
    (36, 115, 'L', 'B'): 'U',
    (36, 115, 'L', 'D'): 'D',
    (36, 115, 'L', 'F'): 'U',
    (36, 115, 'L', 'U'): 'D',
    (36, 115, 'R', 'B'): 'U',
    (36, 115, 'R', 'D'): 'D',
    (36, 115, 'R', 'F'): 'U',
    (36, 115, 'R', 'U'): 'D',
    (36, 115, 'U', 'B'): 'U',
    (36, 115, 'U', 'F'): 'U',
    (36, 115, 'U', 'L'): 'U',
    (36, 115, 'U', 'R'): 'U',
    (40, 61, 'B', 'D'): 'D',
    (40, 61, 'B', 'L'): 'D',
    (40, 61, 'B', 'R'): 'D',
    (40, 61, 'B', 'U'): 'D',
    (40, 61, 'D', 'B'): 'U',
    (40, 61, 'D', 'F'): 'U',
    (40, 61, 'D', 'L'): 'U',
    (40, 61, 'D', 'R'): 'U',
    (40, 61, 'F', 'D'): 'D',
    (40, 61, 'F', 'L'): 'D',
    (40, 61, 'F', 'R'): 'D',
    (40, 61, 'F', 'U'): 'D',
    (40, 61, 'L', 'B'): 'U',
    (40, 61, 'L', 'D'): 'D',
    (40, 61, 'L', 'F'): 'U',
    (40, 61, 'L', 'U'): 'D',
    (40, 61, 'R', 'B'): 'U',
    (40, 61, 'R', 'D'): 'D',
    (40, 61, 'R', 'F'): 'U',
    (40, 61, 'R', 'U'): 'D',
    (40, 61, 'U', 'B'): 'U',
    (40, 61, 'U', 'F'): 'U',
    (40, 61, 'U', 'L'): 'U',
    (40, 61, 'U', 'R'): 'U',
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
    (48, 136, 'B', 'D'): 'U',
    (48, 136, 'B', 'L'): 'U',
    (48, 136, 'B', 'R'): 'U',
    (48, 136, 'B', 'U'): 'U',
    (48, 136, 'D', 'B'): 'D',
    (48, 136, 'D', 'F'): 'D',
    (48, 136, 'D', 'L'): 'D',
    (48, 136, 'D', 'R'): 'D',
    (48, 136, 'F', 'D'): 'U',
    (48, 136, 'F', 'L'): 'U',
    (48, 136, 'F', 'R'): 'U',
    (48, 136, 'F', 'U'): 'U',
    (48, 136, 'L', 'B'): 'D',
    (48, 136, 'L', 'D'): 'U',
    (48, 136, 'L', 'F'): 'D',
    (48, 136, 'L', 'U'): 'U',
    (48, 136, 'R', 'B'): 'D',
    (48, 136, 'R', 'D'): 'U',
    (48, 136, 'R', 'F'): 'D',
    (48, 136, 'R', 'U'): 'U',
    (48, 136, 'U', 'B'): 'D',
    (48, 136, 'U', 'F'): 'D',
    (48, 136, 'U', 'L'): 'D',
    (48, 136, 'U', 'R'): 'D',
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
    (53, 23, 'B', 'D'): 'U',
    (53, 23, 'B', 'L'): 'U',
    (53, 23, 'B', 'R'): 'U',
    (53, 23, 'B', 'U'): 'U',
    (53, 23, 'D', 'B'): 'D',
    (53, 23, 'D', 'F'): 'D',
    (53, 23, 'D', 'L'): 'D',
    (53, 23, 'D', 'R'): 'D',
    (53, 23, 'F', 'D'): 'U',
    (53, 23, 'F', 'L'): 'U',
    (53, 23, 'F', 'R'): 'U',
    (53, 23, 'F', 'U'): 'U',
    (53, 23, 'L', 'B'): 'D',
    (53, 23, 'L', 'D'): 'U',
    (53, 23, 'L', 'F'): 'D',
    (53, 23, 'L', 'U'): 'U',
    (53, 23, 'R', 'B'): 'D',
    (53, 23, 'R', 'D'): 'U',
    (53, 23, 'R', 'F'): 'D',
    (53, 23, 'R', 'U'): 'U',
    (53, 23, 'U', 'B'): 'D',
    (53, 23, 'U', 'F'): 'D',
    (53, 23, 'U', 'L'): 'D',
    (53, 23, 'U', 'R'): 'D',
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
    (61, 40, 'B', 'D'): 'U',
    (61, 40, 'B', 'L'): 'U',
    (61, 40, 'B', 'R'): 'U',
    (61, 40, 'B', 'U'): 'U',
    (61, 40, 'D', 'B'): 'D',
    (61, 40, 'D', 'F'): 'D',
    (61, 40, 'D', 'L'): 'D',
    (61, 40, 'D', 'R'): 'D',
    (61, 40, 'F', 'D'): 'U',
    (61, 40, 'F', 'L'): 'U',
    (61, 40, 'F', 'R'): 'U',
    (61, 40, 'F', 'U'): 'U',
    (61, 40, 'L', 'B'): 'D',
    (61, 40, 'L', 'D'): 'U',
    (61, 40, 'L', 'F'): 'D',
    (61, 40, 'L', 'U'): 'U',
    (61, 40, 'R', 'B'): 'D',
    (61, 40, 'R', 'D'): 'U',
    (61, 40, 'R', 'F'): 'D',
    (61, 40, 'R', 'U'): 'U',
    (61, 40, 'U', 'B'): 'D',
    (61, 40, 'U', 'F'): 'D',
    (61, 40, 'U', 'L'): 'D',
    (61, 40, 'U', 'R'): 'D',
    (65, 86, 'B', 'D'): 'U',
    (65, 86, 'B', 'L'): 'U',
    (65, 86, 'B', 'R'): 'U',
    (65, 86, 'B', 'U'): 'U',
    (65, 86, 'D', 'B'): 'D',
    (65, 86, 'D', 'F'): 'D',
    (65, 86, 'D', 'L'): 'D',
    (65, 86, 'D', 'R'): 'D',
    (65, 86, 'F', 'D'): 'U',
    (65, 86, 'F', 'L'): 'U',
    (65, 86, 'F', 'R'): 'U',
    (65, 86, 'F', 'U'): 'U',
    (65, 86, 'L', 'B'): 'D',
    (65, 86, 'L', 'D'): 'U',
    (65, 86, 'L', 'F'): 'D',
    (65, 86, 'L', 'U'): 'U',
    (65, 86, 'R', 'B'): 'D',
    (65, 86, 'R', 'D'): 'U',
    (65, 86, 'R', 'F'): 'D',
    (65, 86, 'R', 'U'): 'U',
    (65, 86, 'U', 'B'): 'D',
    (65, 86, 'U', 'F'): 'D',
    (65, 86, 'U', 'L'): 'D',
    (65, 86, 'U', 'R'): 'D',
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
    (73, 128, 'B', 'D'): 'U',
    (73, 128, 'B', 'L'): 'U',
    (73, 128, 'B', 'R'): 'U',
    (73, 128, 'B', 'U'): 'U',
    (73, 128, 'D', 'B'): 'D',
    (73, 128, 'D', 'F'): 'D',
    (73, 128, 'D', 'L'): 'D',
    (73, 128, 'D', 'R'): 'D',
    (73, 128, 'F', 'D'): 'U',
    (73, 128, 'F', 'L'): 'U',
    (73, 128, 'F', 'R'): 'U',
    (73, 128, 'F', 'U'): 'U',
    (73, 128, 'L', 'B'): 'D',
    (73, 128, 'L', 'D'): 'U',
    (73, 128, 'L', 'F'): 'D',
    (73, 128, 'L', 'U'): 'U',
    (73, 128, 'R', 'B'): 'D',
    (73, 128, 'R', 'D'): 'U',
    (73, 128, 'R', 'F'): 'D',
    (73, 128, 'R', 'U'): 'U',
    (73, 128, 'U', 'B'): 'D',
    (73, 128, 'U', 'F'): 'D',
    (73, 128, 'U', 'L'): 'D',
    (73, 128, 'U', 'R'): 'D',
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
    (78, 15, 'B', 'D'): 'U',
    (78, 15, 'B', 'L'): 'U',
    (78, 15, 'B', 'R'): 'U',
    (78, 15, 'B', 'U'): 'U',
    (78, 15, 'D', 'B'): 'D',
    (78, 15, 'D', 'F'): 'D',
    (78, 15, 'D', 'L'): 'D',
    (78, 15, 'D', 'R'): 'D',
    (78, 15, 'F', 'D'): 'U',
    (78, 15, 'F', 'L'): 'U',
    (78, 15, 'F', 'R'): 'U',
    (78, 15, 'F', 'U'): 'U',
    (78, 15, 'L', 'B'): 'D',
    (78, 15, 'L', 'D'): 'U',
    (78, 15, 'L', 'F'): 'D',
    (78, 15, 'L', 'U'): 'U',
    (78, 15, 'R', 'B'): 'D',
    (78, 15, 'R', 'D'): 'U',
    (78, 15, 'R', 'F'): 'D',
    (78, 15, 'R', 'U'): 'U',
    (78, 15, 'U', 'B'): 'D',
    (78, 15, 'U', 'F'): 'D',
    (78, 15, 'U', 'L'): 'D',
    (78, 15, 'U', 'R'): 'D',
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
    (86, 65, 'B', 'D'): 'D',
    (86, 65, 'B', 'L'): 'D',
    (86, 65, 'B', 'R'): 'D',
    (86, 65, 'B', 'U'): 'D',
    (86, 65, 'D', 'B'): 'U',
    (86, 65, 'D', 'F'): 'U',
    (86, 65, 'D', 'L'): 'U',
    (86, 65, 'D', 'R'): 'U',
    (86, 65, 'F', 'D'): 'D',
    (86, 65, 'F', 'L'): 'D',
    (86, 65, 'F', 'R'): 'D',
    (86, 65, 'F', 'U'): 'D',
    (86, 65, 'L', 'B'): 'U',
    (86, 65, 'L', 'D'): 'D',
    (86, 65, 'L', 'F'): 'U',
    (86, 65, 'L', 'U'): 'D',
    (86, 65, 'R', 'B'): 'U',
    (86, 65, 'R', 'D'): 'D',
    (86, 65, 'R', 'F'): 'U',
    (86, 65, 'R', 'U'): 'D',
    (86, 65, 'U', 'B'): 'U',
    (86, 65, 'U', 'F'): 'U',
    (86, 65, 'U', 'L'): 'U',
    (86, 65, 'U', 'R'): 'U',
    (90, 111, 'B', 'D'): 'D',
    (90, 111, 'B', 'L'): 'D',
    (90, 111, 'B', 'R'): 'D',
    (90, 111, 'B', 'U'): 'D',
    (90, 111, 'D', 'B'): 'U',
    (90, 111, 'D', 'F'): 'U',
    (90, 111, 'D', 'L'): 'U',
    (90, 111, 'D', 'R'): 'U',
    (90, 111, 'F', 'D'): 'D',
    (90, 111, 'F', 'L'): 'D',
    (90, 111, 'F', 'R'): 'D',
    (90, 111, 'F', 'U'): 'D',
    (90, 111, 'L', 'B'): 'U',
    (90, 111, 'L', 'D'): 'D',
    (90, 111, 'L', 'F'): 'U',
    (90, 111, 'L', 'U'): 'D',
    (90, 111, 'R', 'B'): 'U',
    (90, 111, 'R', 'D'): 'D',
    (90, 111, 'R', 'F'): 'U',
    (90, 111, 'R', 'U'): 'D',
    (90, 111, 'U', 'B'): 'U',
    (90, 111, 'U', 'F'): 'U',
    (90, 111, 'U', 'L'): 'U',
    (90, 111, 'U', 'R'): 'U',
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
    (98, 140, 'B', 'D'): 'U',
    (98, 140, 'B', 'L'): 'U',
    (98, 140, 'B', 'R'): 'U',
    (98, 140, 'B', 'U'): 'U',
    (98, 140, 'D', 'B'): 'D',
    (98, 140, 'D', 'F'): 'D',
    (98, 140, 'D', 'L'): 'D',
    (98, 140, 'D', 'R'): 'D',
    (98, 140, 'F', 'D'): 'U',
    (98, 140, 'F', 'L'): 'U',
    (98, 140, 'F', 'R'): 'U',
    (98, 140, 'F', 'U'): 'U',
    (98, 140, 'L', 'B'): 'D',
    (98, 140, 'L', 'D'): 'U',
    (98, 140, 'L', 'F'): 'D',
    (98, 140, 'L', 'U'): 'U',
    (98, 140, 'R', 'B'): 'D',
    (98, 140, 'R', 'D'): 'U',
    (98, 140, 'R', 'F'): 'D',
    (98, 140, 'R', 'U'): 'U',
    (98, 140, 'U', 'B'): 'D',
    (98, 140, 'U', 'F'): 'D',
    (98, 140, 'U', 'L'): 'D',
    (98, 140, 'U', 'R'): 'D',
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
    (103, 3, 'B', 'D'): 'U',
    (103, 3, 'B', 'L'): 'U',
    (103, 3, 'B', 'R'): 'U',
    (103, 3, 'B', 'U'): 'U',
    (103, 3, 'D', 'B'): 'D',
    (103, 3, 'D', 'F'): 'D',
    (103, 3, 'D', 'L'): 'D',
    (103, 3, 'D', 'R'): 'D',
    (103, 3, 'F', 'D'): 'U',
    (103, 3, 'F', 'L'): 'U',
    (103, 3, 'F', 'R'): 'U',
    (103, 3, 'F', 'U'): 'U',
    (103, 3, 'L', 'B'): 'D',
    (103, 3, 'L', 'D'): 'U',
    (103, 3, 'L', 'F'): 'D',
    (103, 3, 'L', 'U'): 'U',
    (103, 3, 'R', 'B'): 'D',
    (103, 3, 'R', 'D'): 'U',
    (103, 3, 'R', 'F'): 'D',
    (103, 3, 'R', 'U'): 'U',
    (103, 3, 'U', 'B'): 'D',
    (103, 3, 'U', 'F'): 'D',
    (103, 3, 'U', 'L'): 'D',
    (103, 3, 'U', 'R'): 'D',
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
    (111, 90, 'B', 'D'): 'U',
    (111, 90, 'B', 'L'): 'U',
    (111, 90, 'B', 'R'): 'U',
    (111, 90, 'B', 'U'): 'U',
    (111, 90, 'D', 'B'): 'D',
    (111, 90, 'D', 'F'): 'D',
    (111, 90, 'D', 'L'): 'D',
    (111, 90, 'D', 'R'): 'D',
    (111, 90, 'F', 'D'): 'U',
    (111, 90, 'F', 'L'): 'U',
    (111, 90, 'F', 'R'): 'U',
    (111, 90, 'F', 'U'): 'U',
    (111, 90, 'L', 'B'): 'D',
    (111, 90, 'L', 'D'): 'U',
    (111, 90, 'L', 'F'): 'D',
    (111, 90, 'L', 'U'): 'U',
    (111, 90, 'R', 'B'): 'D',
    (111, 90, 'R', 'D'): 'U',
    (111, 90, 'R', 'F'): 'D',
    (111, 90, 'R', 'U'): 'U',
    (111, 90, 'U', 'B'): 'D',
    (111, 90, 'U', 'F'): 'D',
    (111, 90, 'U', 'L'): 'D',
    (111, 90, 'U', 'R'): 'D',
    (115, 36, 'B', 'D'): 'U',
    (115, 36, 'B', 'L'): 'U',
    (115, 36, 'B', 'R'): 'U',
    (115, 36, 'B', 'U'): 'U',
    (115, 36, 'D', 'B'): 'D',
    (115, 36, 'D', 'F'): 'D',
    (115, 36, 'D', 'L'): 'D',
    (115, 36, 'D', 'R'): 'D',
    (115, 36, 'F', 'D'): 'U',
    (115, 36, 'F', 'L'): 'U',
    (115, 36, 'F', 'R'): 'U',
    (115, 36, 'F', 'U'): 'U',
    (115, 36, 'L', 'B'): 'D',
    (115, 36, 'L', 'D'): 'U',
    (115, 36, 'L', 'F'): 'D',
    (115, 36, 'L', 'U'): 'U',
    (115, 36, 'R', 'B'): 'D',
    (115, 36, 'R', 'D'): 'U',
    (115, 36, 'R', 'F'): 'D',
    (115, 36, 'R', 'U'): 'U',
    (115, 36, 'U', 'B'): 'D',
    (115, 36, 'U', 'F'): 'D',
    (115, 36, 'U', 'L'): 'D',
    (115, 36, 'U', 'R'): 'D',
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
    (123, 148, 'B', 'D'): 'U',
    (123, 148, 'B', 'L'): 'U',
    (123, 148, 'B', 'R'): 'U',
    (123, 148, 'B', 'U'): 'U',
    (123, 148, 'D', 'B'): 'D',
    (123, 148, 'D', 'F'): 'D',
    (123, 148, 'D', 'L'): 'D',
    (123, 148, 'D', 'R'): 'D',
    (123, 148, 'F', 'D'): 'U',
    (123, 148, 'F', 'L'): 'U',
    (123, 148, 'F', 'R'): 'U',
    (123, 148, 'F', 'U'): 'U',
    (123, 148, 'L', 'B'): 'D',
    (123, 148, 'L', 'D'): 'U',
    (123, 148, 'L', 'F'): 'D',
    (123, 148, 'L', 'U'): 'U',
    (123, 148, 'R', 'B'): 'D',
    (123, 148, 'R', 'D'): 'U',
    (123, 148, 'R', 'F'): 'D',
    (123, 148, 'R', 'U'): 'U',
    (123, 148, 'U', 'B'): 'D',
    (123, 148, 'U', 'F'): 'D',
    (123, 148, 'U', 'L'): 'D',
    (123, 148, 'U', 'R'): 'D',
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
    (128, 73, 'B', 'D'): 'D',
    (128, 73, 'B', 'L'): 'D',
    (128, 73, 'B', 'R'): 'D',
    (128, 73, 'B', 'U'): 'D',
    (128, 73, 'D', 'B'): 'U',
    (128, 73, 'D', 'F'): 'U',
    (128, 73, 'D', 'L'): 'U',
    (128, 73, 'D', 'R'): 'U',
    (128, 73, 'F', 'D'): 'D',
    (128, 73, 'F', 'L'): 'D',
    (128, 73, 'F', 'R'): 'D',
    (128, 73, 'F', 'U'): 'D',
    (128, 73, 'L', 'B'): 'U',
    (128, 73, 'L', 'D'): 'D',
    (128, 73, 'L', 'F'): 'U',
    (128, 73, 'L', 'U'): 'D',
    (128, 73, 'R', 'B'): 'U',
    (128, 73, 'R', 'D'): 'D',
    (128, 73, 'R', 'F'): 'U',
    (128, 73, 'R', 'U'): 'D',
    (128, 73, 'U', 'B'): 'U',
    (128, 73, 'U', 'F'): 'U',
    (128, 73, 'U', 'L'): 'U',
    (128, 73, 'U', 'R'): 'U',
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
    (136, 48, 'B', 'D'): 'D',
    (136, 48, 'B', 'L'): 'D',
    (136, 48, 'B', 'R'): 'D',
    (136, 48, 'B', 'U'): 'D',
    (136, 48, 'D', 'B'): 'U',
    (136, 48, 'D', 'F'): 'U',
    (136, 48, 'D', 'L'): 'U',
    (136, 48, 'D', 'R'): 'U',
    (136, 48, 'F', 'D'): 'D',
    (136, 48, 'F', 'L'): 'D',
    (136, 48, 'F', 'R'): 'D',
    (136, 48, 'F', 'U'): 'D',
    (136, 48, 'L', 'B'): 'U',
    (136, 48, 'L', 'D'): 'D',
    (136, 48, 'L', 'F'): 'U',
    (136, 48, 'L', 'U'): 'D',
    (136, 48, 'R', 'B'): 'U',
    (136, 48, 'R', 'D'): 'D',
    (136, 48, 'R', 'F'): 'U',
    (136, 48, 'R', 'U'): 'D',
    (136, 48, 'U', 'B'): 'U',
    (136, 48, 'U', 'F'): 'U',
    (136, 48, 'U', 'L'): 'U',
    (136, 48, 'U', 'R'): 'U',
    (140, 98, 'B', 'D'): 'D',
    (140, 98, 'B', 'L'): 'D',
    (140, 98, 'B', 'R'): 'D',
    (140, 98, 'B', 'U'): 'D',
    (140, 98, 'D', 'B'): 'U',
    (140, 98, 'D', 'F'): 'U',
    (140, 98, 'D', 'L'): 'U',
    (140, 98, 'D', 'R'): 'U',
    (140, 98, 'F', 'D'): 'D',
    (140, 98, 'F', 'L'): 'D',
    (140, 98, 'F', 'R'): 'D',
    (140, 98, 'F', 'U'): 'D',
    (140, 98, 'L', 'B'): 'U',
    (140, 98, 'L', 'D'): 'D',
    (140, 98, 'L', 'F'): 'U',
    (140, 98, 'L', 'U'): 'D',
    (140, 98, 'R', 'B'): 'U',
    (140, 98, 'R', 'D'): 'D',
    (140, 98, 'R', 'F'): 'U',
    (140, 98, 'R', 'U'): 'D',
    (140, 98, 'U', 'B'): 'U',
    (140, 98, 'U', 'F'): 'U',
    (140, 98, 'U', 'L'): 'U',
    (140, 98, 'U', 'R'): 'U',
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
    (148, 123, 'B', 'D'): 'D',
    (148, 123, 'B', 'L'): 'D',
    (148, 123, 'B', 'R'): 'D',
    (148, 123, 'B', 'U'): 'D',
    (148, 123, 'D', 'B'): 'U',
    (148, 123, 'D', 'F'): 'U',
    (148, 123, 'D', 'L'): 'U',
    (148, 123, 'D', 'R'): 'U',
    (148, 123, 'F', 'D'): 'D',
    (148, 123, 'F', 'L'): 'D',
    (148, 123, 'F', 'R'): 'D',
    (148, 123, 'F', 'U'): 'D',
    (148, 123, 'L', 'B'): 'U',
    (148, 123, 'L', 'D'): 'D',
    (148, 123, 'L', 'F'): 'U',
    (148, 123, 'L', 'U'): 'D',
    (148, 123, 'R', 'B'): 'U',
    (148, 123, 'R', 'D'): 'D',
    (148, 123, 'R', 'F'): 'U',
    (148, 123, 'R', 'U'): 'D',
    (148, 123, 'U', 'B'): 'U',
    (148, 123, 'U', 'F'): 'U',
    (148, 123, 'U', 'L'): 'U',
    (148, 123, 'U', 'R'): 'U',
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
    (149, 122, 'U', 'R'): 'U',
}

stage_first_four_edges_wing_str_combos = (
    ('DB', 'LB', 'RB', 'UB'),
    ('DB', 'LB', 'RB', 'DF'),
    ('DB', 'LB', 'RB', 'DL'),
    ('DB', 'LB', 'RB', 'DR'),
    ('DB', 'LB', 'RB', 'LF'),
    ('DB', 'LB', 'RB', 'RF'),
    ('DB', 'LB', 'RB', 'UF'),
    ('DB', 'LB', 'RB', 'UL'),
    ('DB', 'LB', 'RB', 'UR'),
    ('DB', 'LB', 'UB', 'DF'),
    ('DB', 'LB', 'UB', 'DL'),
    ('DB', 'LB', 'UB', 'DR'),
    ('DB', 'LB', 'UB', 'LF'),
    ('DB', 'LB', 'UB', 'RF'),
    ('DB', 'LB', 'UB', 'UF'),
    ('DB', 'LB', 'UB', 'UL'),
    ('DB', 'LB', 'UB', 'UR'),
    ('DB', 'LB', 'DF', 'DL'),
    ('DB', 'LB', 'DF', 'DR'),
    ('DB', 'LB', 'DF', 'LF'),
    ('DB', 'LB', 'DF', 'RF'),
    ('DB', 'LB', 'DF', 'UF'),
    ('DB', 'LB', 'DF', 'UL'),
    ('DB', 'LB', 'DF', 'UR'),
    ('DB', 'LB', 'DL', 'DR'),
    ('DB', 'LB', 'DL', 'LF'),
    ('DB', 'LB', 'DL', 'RF'),
    ('DB', 'LB', 'DL', 'UF'),
    ('DB', 'LB', 'DL', 'UL'),
    ('DB', 'LB', 'DL', 'UR'),
    ('DB', 'LB', 'DR', 'LF'),
    ('DB', 'LB', 'DR', 'RF'),
    ('DB', 'LB', 'DR', 'UF'),
    ('DB', 'LB', 'DR', 'UL'),
    ('DB', 'LB', 'DR', 'UR'),
    ('DB', 'LB', 'LF', 'RF'),
    ('DB', 'LB', 'LF', 'UF'),
    ('DB', 'LB', 'LF', 'UL'),
    ('DB', 'LB', 'LF', 'UR'),
    ('DB', 'LB', 'RF', 'UF'),
    ('DB', 'LB', 'RF', 'UL'),
    ('DB', 'LB', 'RF', 'UR'),
    ('DB', 'LB', 'UF', 'UL'),
    ('DB', 'LB', 'UF', 'UR'),
    ('DB', 'LB', 'UL', 'UR'),
    ('DB', 'RB', 'UB', 'DF'),
    ('DB', 'RB', 'UB', 'DL'),
    ('DB', 'RB', 'UB', 'DR'),
    ('DB', 'RB', 'UB', 'LF'),
    ('DB', 'RB', 'UB', 'RF'),
    ('DB', 'RB', 'UB', 'UF'),
    ('DB', 'RB', 'UB', 'UL'),
    ('DB', 'RB', 'UB', 'UR'),
    ('DB', 'RB', 'DF', 'DL'),
    ('DB', 'RB', 'DF', 'DR'),
    ('DB', 'RB', 'DF', 'LF'),
    ('DB', 'RB', 'DF', 'RF'),
    ('DB', 'RB', 'DF', 'UF'),
    ('DB', 'RB', 'DF', 'UL'),
    ('DB', 'RB', 'DF', 'UR'),
    ('DB', 'RB', 'DL', 'DR'),
    ('DB', 'RB', 'DL', 'LF'),
    ('DB', 'RB', 'DL', 'RF'),
    ('DB', 'RB', 'DL', 'UF'),
    ('DB', 'RB', 'DL', 'UL'),
    ('DB', 'RB', 'DL', 'UR'),
    ('DB', 'RB', 'DR', 'LF'),
    ('DB', 'RB', 'DR', 'RF'),
    ('DB', 'RB', 'DR', 'UF'),
    ('DB', 'RB', 'DR', 'UL'),
    ('DB', 'RB', 'DR', 'UR'),
    ('DB', 'RB', 'LF', 'RF'),
    ('DB', 'RB', 'LF', 'UF'),
    ('DB', 'RB', 'LF', 'UL'),
    ('DB', 'RB', 'LF', 'UR'),
    ('DB', 'RB', 'RF', 'UF'),
    ('DB', 'RB', 'RF', 'UL'),
    ('DB', 'RB', 'RF', 'UR'),
    ('DB', 'RB', 'UF', 'UL'),
    ('DB', 'RB', 'UF', 'UR'),
    ('DB', 'RB', 'UL', 'UR'),
    ('DB', 'UB', 'DF', 'DL'),
    ('DB', 'UB', 'DF', 'DR'),
    ('DB', 'UB', 'DF', 'LF'),
    ('DB', 'UB', 'DF', 'RF'),
    ('DB', 'UB', 'DF', 'UF'),
    ('DB', 'UB', 'DF', 'UL'),
    ('DB', 'UB', 'DF', 'UR'),
    ('DB', 'UB', 'DL', 'DR'),
    ('DB', 'UB', 'DL', 'LF'),
    ('DB', 'UB', 'DL', 'RF'),
    ('DB', 'UB', 'DL', 'UF'),
    ('DB', 'UB', 'DL', 'UL'),
    ('DB', 'UB', 'DL', 'UR'),
    ('DB', 'UB', 'DR', 'LF'),
    ('DB', 'UB', 'DR', 'RF'),
    ('DB', 'UB', 'DR', 'UF'),
    ('DB', 'UB', 'DR', 'UL'),
    ('DB', 'UB', 'DR', 'UR'),
    ('DB', 'UB', 'LF', 'RF'),
    ('DB', 'UB', 'LF', 'UF'),
    ('DB', 'UB', 'LF', 'UL'),
    ('DB', 'UB', 'LF', 'UR'),
    ('DB', 'UB', 'RF', 'UF'),
    ('DB', 'UB', 'RF', 'UL'),
    ('DB', 'UB', 'RF', 'UR'),
    ('DB', 'UB', 'UF', 'UL'),
    ('DB', 'UB', 'UF', 'UR'),
    ('DB', 'UB', 'UL', 'UR'),
    ('DB', 'DF', 'DL', 'DR'),
    ('DB', 'DF', 'DL', 'LF'),
    ('DB', 'DF', 'DL', 'RF'),
    ('DB', 'DF', 'DL', 'UF'),
    ('DB', 'DF', 'DL', 'UL'),
    ('DB', 'DF', 'DL', 'UR'),
    ('DB', 'DF', 'DR', 'LF'),
    ('DB', 'DF', 'DR', 'RF'),
    ('DB', 'DF', 'DR', 'UF'),
    ('DB', 'DF', 'DR', 'UL'),
    ('DB', 'DF', 'DR', 'UR'),
    ('DB', 'DF', 'LF', 'RF'),
    ('DB', 'DF', 'LF', 'UF'),
    ('DB', 'DF', 'LF', 'UL'),
    ('DB', 'DF', 'LF', 'UR'),
    ('DB', 'DF', 'RF', 'UF'),
    ('DB', 'DF', 'RF', 'UL'),
    ('DB', 'DF', 'RF', 'UR'),
    ('DB', 'DF', 'UF', 'UL'),
    ('DB', 'DF', 'UF', 'UR'),
    ('DB', 'DF', 'UL', 'UR'),
    ('DB', 'DL', 'DR', 'LF'),
    ('DB', 'DL', 'DR', 'RF'),
    ('DB', 'DL', 'DR', 'UF'),
    ('DB', 'DL', 'DR', 'UL'),
    ('DB', 'DL', 'DR', 'UR'),
    ('DB', 'DL', 'LF', 'RF'),
    ('DB', 'DL', 'LF', 'UF'),
    ('DB', 'DL', 'LF', 'UL'),
    ('DB', 'DL', 'LF', 'UR'),
    ('DB', 'DL', 'RF', 'UF'),
    ('DB', 'DL', 'RF', 'UL'),
    ('DB', 'DL', 'RF', 'UR'),
    ('DB', 'DL', 'UF', 'UL'),
    ('DB', 'DL', 'UF', 'UR'),
    ('DB', 'DL', 'UL', 'UR'),
    ('DB', 'DR', 'LF', 'RF'),
    ('DB', 'DR', 'LF', 'UF'),
    ('DB', 'DR', 'LF', 'UL'),
    ('DB', 'DR', 'LF', 'UR'),
    ('DB', 'DR', 'RF', 'UF'),
    ('DB', 'DR', 'RF', 'UL'),
    ('DB', 'DR', 'RF', 'UR'),
    ('DB', 'DR', 'UF', 'UL'),
    ('DB', 'DR', 'UF', 'UR'),
    ('DB', 'DR', 'UL', 'UR'),
    ('DB', 'LF', 'RF', 'UF'),
    ('DB', 'LF', 'RF', 'UL'),
    ('DB', 'LF', 'RF', 'UR'),
    ('DB', 'LF', 'UF', 'UL'),
    ('DB', 'LF', 'UF', 'UR'),
    ('DB', 'LF', 'UL', 'UR'),
    ('DB', 'RF', 'UF', 'UL'),
    ('DB', 'RF', 'UF', 'UR'),
    ('DB', 'RF', 'UL', 'UR'),
    ('DB', 'UF', 'UL', 'UR'),
    ('LB', 'RB', 'UB', 'DF'),
    ('LB', 'RB', 'UB', 'DL'),
    ('LB', 'RB', 'UB', 'DR'),
    ('LB', 'RB', 'UB', 'LF'),
    ('LB', 'RB', 'UB', 'RF'),
    ('LB', 'RB', 'UB', 'UF'),
    ('LB', 'RB', 'UB', 'UL'),
    ('LB', 'RB', 'UB', 'UR'),
    ('LB', 'RB', 'DF', 'DL'),
    ('LB', 'RB', 'DF', 'DR'),
    ('LB', 'RB', 'DF', 'LF'),
    ('LB', 'RB', 'DF', 'RF'),
    ('LB', 'RB', 'DF', 'UF'),
    ('LB', 'RB', 'DF', 'UL'),
    ('LB', 'RB', 'DF', 'UR'),
    ('LB', 'RB', 'DL', 'DR'),
    ('LB', 'RB', 'DL', 'LF'),
    ('LB', 'RB', 'DL', 'RF'),
    ('LB', 'RB', 'DL', 'UF'),
    ('LB', 'RB', 'DL', 'UL'),
    ('LB', 'RB', 'DL', 'UR'),
    ('LB', 'RB', 'DR', 'LF'),
    ('LB', 'RB', 'DR', 'RF'),
    ('LB', 'RB', 'DR', 'UF'),
    ('LB', 'RB', 'DR', 'UL'),
    ('LB', 'RB', 'DR', 'UR'),
    ('LB', 'RB', 'LF', 'RF'),
    ('LB', 'RB', 'LF', 'UF'),
    ('LB', 'RB', 'LF', 'UL'),
    ('LB', 'RB', 'LF', 'UR'),
    ('LB', 'RB', 'RF', 'UF'),
    ('LB', 'RB', 'RF', 'UL'),
    ('LB', 'RB', 'RF', 'UR'),
    ('LB', 'RB', 'UF', 'UL'),
    ('LB', 'RB', 'UF', 'UR'),
    ('LB', 'RB', 'UL', 'UR'),
    ('LB', 'UB', 'DF', 'DL'),
    ('LB', 'UB', 'DF', 'DR'),
    ('LB', 'UB', 'DF', 'LF'),
    ('LB', 'UB', 'DF', 'RF'),
    ('LB', 'UB', 'DF', 'UF'),
    ('LB', 'UB', 'DF', 'UL'),
    ('LB', 'UB', 'DF', 'UR'),
    ('LB', 'UB', 'DL', 'DR'),
    ('LB', 'UB', 'DL', 'LF'),
    ('LB', 'UB', 'DL', 'RF'),
    ('LB', 'UB', 'DL', 'UF'),
    ('LB', 'UB', 'DL', 'UL'),
    ('LB', 'UB', 'DL', 'UR'),
    ('LB', 'UB', 'DR', 'LF'),
    ('LB', 'UB', 'DR', 'RF'),
    ('LB', 'UB', 'DR', 'UF'),
    ('LB', 'UB', 'DR', 'UL'),
    ('LB', 'UB', 'DR', 'UR'),
    ('LB', 'UB', 'LF', 'RF'),
    ('LB', 'UB', 'LF', 'UF'),
    ('LB', 'UB', 'LF', 'UL'),
    ('LB', 'UB', 'LF', 'UR'),
    ('LB', 'UB', 'RF', 'UF'),
    ('LB', 'UB', 'RF', 'UL'),
    ('LB', 'UB', 'RF', 'UR'),
    ('LB', 'UB', 'UF', 'UL'),
    ('LB', 'UB', 'UF', 'UR'),
    ('LB', 'UB', 'UL', 'UR'),
    ('LB', 'DF', 'DL', 'DR'),
    ('LB', 'DF', 'DL', 'LF'),
    ('LB', 'DF', 'DL', 'RF'),
    ('LB', 'DF', 'DL', 'UF'),
    ('LB', 'DF', 'DL', 'UL'),
    ('LB', 'DF', 'DL', 'UR'),
    ('LB', 'DF', 'DR', 'LF'),
    ('LB', 'DF', 'DR', 'RF'),
    ('LB', 'DF', 'DR', 'UF'),
    ('LB', 'DF', 'DR', 'UL'),
    ('LB', 'DF', 'DR', 'UR'),
    ('LB', 'DF', 'LF', 'RF'),
    ('LB', 'DF', 'LF', 'UF'),
    ('LB', 'DF', 'LF', 'UL'),
    ('LB', 'DF', 'LF', 'UR'),
    ('LB', 'DF', 'RF', 'UF'),
    ('LB', 'DF', 'RF', 'UL'),
    ('LB', 'DF', 'RF', 'UR'),
    ('LB', 'DF', 'UF', 'UL'),
    ('LB', 'DF', 'UF', 'UR'),
    ('LB', 'DF', 'UL', 'UR'),
    ('LB', 'DL', 'DR', 'LF'),
    ('LB', 'DL', 'DR', 'RF'),
    ('LB', 'DL', 'DR', 'UF'),
    ('LB', 'DL', 'DR', 'UL'),
    ('LB', 'DL', 'DR', 'UR'),
    ('LB', 'DL', 'LF', 'RF'),
    ('LB', 'DL', 'LF', 'UF'),
    ('LB', 'DL', 'LF', 'UL'),
    ('LB', 'DL', 'LF', 'UR'),
    ('LB', 'DL', 'RF', 'UF'),
    ('LB', 'DL', 'RF', 'UL'),
    ('LB', 'DL', 'RF', 'UR'),
    ('LB', 'DL', 'UF', 'UL'),
    ('LB', 'DL', 'UF', 'UR'),
    ('LB', 'DL', 'UL', 'UR'),
    ('LB', 'DR', 'LF', 'RF'),
    ('LB', 'DR', 'LF', 'UF'),
    ('LB', 'DR', 'LF', 'UL'),
    ('LB', 'DR', 'LF', 'UR'),
    ('LB', 'DR', 'RF', 'UF'),
    ('LB', 'DR', 'RF', 'UL'),
    ('LB', 'DR', 'RF', 'UR'),
    ('LB', 'DR', 'UF', 'UL'),
    ('LB', 'DR', 'UF', 'UR'),
    ('LB', 'DR', 'UL', 'UR'),
    ('LB', 'LF', 'RF', 'UF'),
    ('LB', 'LF', 'RF', 'UL'),
    ('LB', 'LF', 'RF', 'UR'),
    ('LB', 'LF', 'UF', 'UL'),
    ('LB', 'LF', 'UF', 'UR'),
    ('LB', 'LF', 'UL', 'UR'),
    ('LB', 'RF', 'UF', 'UL'),
    ('LB', 'RF', 'UF', 'UR'),
    ('LB', 'RF', 'UL', 'UR'),
    ('LB', 'UF', 'UL', 'UR'),
    ('RB', 'UB', 'DF', 'DL'),
    ('RB', 'UB', 'DF', 'DR'),
    ('RB', 'UB', 'DF', 'LF'),
    ('RB', 'UB', 'DF', 'RF'),
    ('RB', 'UB', 'DF', 'UF'),
    ('RB', 'UB', 'DF', 'UL'),
    ('RB', 'UB', 'DF', 'UR'),
    ('RB', 'UB', 'DL', 'DR'),
    ('RB', 'UB', 'DL', 'LF'),
    ('RB', 'UB', 'DL', 'RF'),
    ('RB', 'UB', 'DL', 'UF'),
    ('RB', 'UB', 'DL', 'UL'),
    ('RB', 'UB', 'DL', 'UR'),
    ('RB', 'UB', 'DR', 'LF'),
    ('RB', 'UB', 'DR', 'RF'),
    ('RB', 'UB', 'DR', 'UF'),
    ('RB', 'UB', 'DR', 'UL'),
    ('RB', 'UB', 'DR', 'UR'),
    ('RB', 'UB', 'LF', 'RF'),
    ('RB', 'UB', 'LF', 'UF'),
    ('RB', 'UB', 'LF', 'UL'),
    ('RB', 'UB', 'LF', 'UR'),
    ('RB', 'UB', 'RF', 'UF'),
    ('RB', 'UB', 'RF', 'UL'),
    ('RB', 'UB', 'RF', 'UR'),
    ('RB', 'UB', 'UF', 'UL'),
    ('RB', 'UB', 'UF', 'UR'),
    ('RB', 'UB', 'UL', 'UR'),
    ('RB', 'DF', 'DL', 'DR'),
    ('RB', 'DF', 'DL', 'LF'),
    ('RB', 'DF', 'DL', 'RF'),
    ('RB', 'DF', 'DL', 'UF'),
    ('RB', 'DF', 'DL', 'UL'),
    ('RB', 'DF', 'DL', 'UR'),
    ('RB', 'DF', 'DR', 'LF'),
    ('RB', 'DF', 'DR', 'RF'),
    ('RB', 'DF', 'DR', 'UF'),
    ('RB', 'DF', 'DR', 'UL'),
    ('RB', 'DF', 'DR', 'UR'),
    ('RB', 'DF', 'LF', 'RF'),
    ('RB', 'DF', 'LF', 'UF'),
    ('RB', 'DF', 'LF', 'UL'),
    ('RB', 'DF', 'LF', 'UR'),
    ('RB', 'DF', 'RF', 'UF'),
    ('RB', 'DF', 'RF', 'UL'),
    ('RB', 'DF', 'RF', 'UR'),
    ('RB', 'DF', 'UF', 'UL'),
    ('RB', 'DF', 'UF', 'UR'),
    ('RB', 'DF', 'UL', 'UR'),
    ('RB', 'DL', 'DR', 'LF'),
    ('RB', 'DL', 'DR', 'RF'),
    ('RB', 'DL', 'DR', 'UF'),
    ('RB', 'DL', 'DR', 'UL'),
    ('RB', 'DL', 'DR', 'UR'),
    ('RB', 'DL', 'LF', 'RF'),
    ('RB', 'DL', 'LF', 'UF'),
    ('RB', 'DL', 'LF', 'UL'),
    ('RB', 'DL', 'LF', 'UR'),
    ('RB', 'DL', 'RF', 'UF'),
    ('RB', 'DL', 'RF', 'UL'),
    ('RB', 'DL', 'RF', 'UR'),
    ('RB', 'DL', 'UF', 'UL'),
    ('RB', 'DL', 'UF', 'UR'),
    ('RB', 'DL', 'UL', 'UR'),
    ('RB', 'DR', 'LF', 'RF'),
    ('RB', 'DR', 'LF', 'UF'),
    ('RB', 'DR', 'LF', 'UL'),
    ('RB', 'DR', 'LF', 'UR'),
    ('RB', 'DR', 'RF', 'UF'),
    ('RB', 'DR', 'RF', 'UL'),
    ('RB', 'DR', 'RF', 'UR'),
    ('RB', 'DR', 'UF', 'UL'),
    ('RB', 'DR', 'UF', 'UR'),
    ('RB', 'DR', 'UL', 'UR'),
    ('RB', 'LF', 'RF', 'UF'),
    ('RB', 'LF', 'RF', 'UL'),
    ('RB', 'LF', 'RF', 'UR'),
    ('RB', 'LF', 'UF', 'UL'),
    ('RB', 'LF', 'UF', 'UR'),
    ('RB', 'LF', 'UL', 'UR'),
    ('RB', 'RF', 'UF', 'UL'),
    ('RB', 'RF', 'UF', 'UR'),
    ('RB', 'RF', 'UL', 'UR'),
    ('RB', 'UF', 'UL', 'UR'),
    ('UB', 'DF', 'DL', 'DR'),
    ('UB', 'DF', 'DL', 'LF'),
    ('UB', 'DF', 'DL', 'RF'),
    ('UB', 'DF', 'DL', 'UF'),
    ('UB', 'DF', 'DL', 'UL'),
    ('UB', 'DF', 'DL', 'UR'),
    ('UB', 'DF', 'DR', 'LF'),
    ('UB', 'DF', 'DR', 'RF'),
    ('UB', 'DF', 'DR', 'UF'),
    ('UB', 'DF', 'DR', 'UL'),
    ('UB', 'DF', 'DR', 'UR'),
    ('UB', 'DF', 'LF', 'RF'),
    ('UB', 'DF', 'LF', 'UF'),
    ('UB', 'DF', 'LF', 'UL'),
    ('UB', 'DF', 'LF', 'UR'),
    ('UB', 'DF', 'RF', 'UF'),
    ('UB', 'DF', 'RF', 'UL'),
    ('UB', 'DF', 'RF', 'UR'),
    ('UB', 'DF', 'UF', 'UL'),
    ('UB', 'DF', 'UF', 'UR'),
    ('UB', 'DF', 'UL', 'UR'),
    ('UB', 'DL', 'DR', 'LF'),
    ('UB', 'DL', 'DR', 'RF'),
    ('UB', 'DL', 'DR', 'UF'),
    ('UB', 'DL', 'DR', 'UL'),
    ('UB', 'DL', 'DR', 'UR'),
    ('UB', 'DL', 'LF', 'RF'),
    ('UB', 'DL', 'LF', 'UF'),
    ('UB', 'DL', 'LF', 'UL'),
    ('UB', 'DL', 'LF', 'UR'),
    ('UB', 'DL', 'RF', 'UF'),
    ('UB', 'DL', 'RF', 'UL'),
    ('UB', 'DL', 'RF', 'UR'),
    ('UB', 'DL', 'UF', 'UL'),
    ('UB', 'DL', 'UF', 'UR'),
    ('UB', 'DL', 'UL', 'UR'),
    ('UB', 'DR', 'LF', 'RF'),
    ('UB', 'DR', 'LF', 'UF'),
    ('UB', 'DR', 'LF', 'UL'),
    ('UB', 'DR', 'LF', 'UR'),
    ('UB', 'DR', 'RF', 'UF'),
    ('UB', 'DR', 'RF', 'UL'),
    ('UB', 'DR', 'RF', 'UR'),
    ('UB', 'DR', 'UF', 'UL'),
    ('UB', 'DR', 'UF', 'UR'),
    ('UB', 'DR', 'UL', 'UR'),
    ('UB', 'LF', 'RF', 'UF'),
    ('UB', 'LF', 'RF', 'UL'),
    ('UB', 'LF', 'RF', 'UR'),
    ('UB', 'LF', 'UF', 'UL'),
    ('UB', 'LF', 'UF', 'UR'),
    ('UB', 'LF', 'UL', 'UR'),
    ('UB', 'RF', 'UF', 'UL'),
    ('UB', 'RF', 'UF', 'UR'),
    ('UB', 'RF', 'UL', 'UR'),
    ('UB', 'UF', 'UL', 'UR'),
    ('DF', 'DL', 'DR', 'LF'),
    ('DF', 'DL', 'DR', 'RF'),
    ('DF', 'DL', 'DR', 'UF'),
    ('DF', 'DL', 'DR', 'UL'),
    ('DF', 'DL', 'DR', 'UR'),
    ('DF', 'DL', 'LF', 'RF'),
    ('DF', 'DL', 'LF', 'UF'),
    ('DF', 'DL', 'LF', 'UL'),
    ('DF', 'DL', 'LF', 'UR'),
    ('DF', 'DL', 'RF', 'UF'),
    ('DF', 'DL', 'RF', 'UL'),
    ('DF', 'DL', 'RF', 'UR'),
    ('DF', 'DL', 'UF', 'UL'),
    ('DF', 'DL', 'UF', 'UR'),
    ('DF', 'DL', 'UL', 'UR'),
    ('DF', 'DR', 'LF', 'RF'),
    ('DF', 'DR', 'LF', 'UF'),
    ('DF', 'DR', 'LF', 'UL'),
    ('DF', 'DR', 'LF', 'UR'),
    ('DF', 'DR', 'RF', 'UF'),
    ('DF', 'DR', 'RF', 'UL'),
    ('DF', 'DR', 'RF', 'UR'),
    ('DF', 'DR', 'UF', 'UL'),
    ('DF', 'DR', 'UF', 'UR'),
    ('DF', 'DR', 'UL', 'UR'),
    ('DF', 'LF', 'RF', 'UF'),
    ('DF', 'LF', 'RF', 'UL'),
    ('DF', 'LF', 'RF', 'UR'),
    ('DF', 'LF', 'UF', 'UL'),
    ('DF', 'LF', 'UF', 'UR'),
    ('DF', 'LF', 'UL', 'UR'),
    ('DF', 'RF', 'UF', 'UL'),
    ('DF', 'RF', 'UF', 'UR'),
    ('DF', 'RF', 'UL', 'UR'),
    ('DF', 'UF', 'UL', 'UR'),
    ('DL', 'DR', 'LF', 'RF'),
    ('DL', 'DR', 'LF', 'UF'),
    ('DL', 'DR', 'LF', 'UL'),
    ('DL', 'DR', 'LF', 'UR'),
    ('DL', 'DR', 'RF', 'UF'),
    ('DL', 'DR', 'RF', 'UL'),
    ('DL', 'DR', 'RF', 'UR'),
    ('DL', 'DR', 'UF', 'UL'),
    ('DL', 'DR', 'UF', 'UR'),
    ('DL', 'DR', 'UL', 'UR'),
    ('DL', 'LF', 'RF', 'UF'),
    ('DL', 'LF', 'RF', 'UL'),
    ('DL', 'LF', 'RF', 'UR'),
    ('DL', 'LF', 'UF', 'UL'),
    ('DL', 'LF', 'UF', 'UR'),
    ('DL', 'LF', 'UL', 'UR'),
    ('DL', 'RF', 'UF', 'UL'),
    ('DL', 'RF', 'UF', 'UR'),
    ('DL', 'RF', 'UL', 'UR'),
    ('DL', 'UF', 'UL', 'UR'),
    ('DR', 'LF', 'RF', 'UF'),
    ('DR', 'LF', 'RF', 'UL'),
    ('DR', 'LF', 'RF', 'UR'),
    ('DR', 'LF', 'UF', 'UL'),
    ('DR', 'LF', 'UF', 'UR'),
    ('DR', 'LF', 'UL', 'UR'),
    ('DR', 'RF', 'UF', 'UL'),
    ('DR', 'RF', 'UF', 'UR'),
    ('DR', 'RF', 'UL', 'UR'),
    ('DR', 'UF', 'UL', 'UR'),
    ('LF', 'RF', 'UF', 'UL'),
    ('LF', 'RF', 'UF', 'UR'),
    ('LF', 'RF', 'UL', 'UR'),
    ('LF', 'UF', 'UL', 'UR'),
    ('RF', 'UF', 'UL', 'UR'),
)


swaps_555 = {'2B': (0, 1, 2, 3, 4, 5, 79, 84, 89, 94, 99, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 10, 28, 29, 30, 31, 9, 33, 34, 35, 36, 8, 38, 39, 40, 41, 7, 43, 44, 45, 46, 6, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 145, 80, 81, 82, 83, 144, 85, 86, 87, 88, 143, 90, 91, 92, 93, 142, 95, 96, 97, 98, 141, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 27, 32, 37, 42, 47, 146, 147, 148, 149, 150),
 "2B'": (0, 1, 2, 3, 4, 5, 47, 42, 37, 32, 27, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 141, 28, 29, 30, 31, 142, 33, 34, 35, 36, 143, 38, 39, 40, 41, 144, 43, 44, 45, 46, 145, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 6, 80, 81, 82, 83, 7, 85, 86, 87, 88, 8, 90, 91, 92, 93, 9, 95, 96, 97, 98, 10, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 99, 94, 89, 84, 79, 146, 147, 148, 149, 150),
 '2B2': (0, 1, 2, 3, 4, 5, 145, 144, 143, 142, 141, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 99, 28, 29, 30, 31, 94, 33, 34, 35, 36, 89, 38, 39, 40, 41, 84, 43, 44, 45, 46, 79, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 47, 80, 81, 82, 83, 42, 85, 86, 87, 88, 37, 90, 91, 92, 93, 32, 95, 96, 97, 98, 27, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 10, 9, 8, 7, 6, 146, 147, 148, 149, 150),
 '2D': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 116, 117, 118, 119, 120, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 41, 42, 43, 44, 45, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 66, 67, 68, 69, 70, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 91, 92, 93, 94, 95, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "2D'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 66, 67, 68, 69, 70, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 91, 92, 93, 94, 95, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 116, 117, 118, 119, 120, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 41, 42, 43, 44, 45, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '2D2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 91, 92, 93, 94, 95, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 116, 117, 118, 119, 120, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 41, 42, 43, 44, 45, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 66, 67, 68, 69, 70, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '2F': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 49, 44, 39, 34, 29, 21, 22, 23, 24, 25, 26, 27, 28, 131, 30, 31, 32, 33, 132, 35, 36, 37, 38, 133, 40, 41, 42, 43, 134, 45, 46, 47, 48, 135, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 16, 78, 79, 80, 81, 17, 83, 84, 85, 86, 18, 88, 89, 90, 91, 19, 93, 94, 95, 96, 20, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 97, 92, 87, 82, 77, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "2F'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 77, 82, 87, 92, 97, 21, 22, 23, 24, 25, 26, 27, 28, 20, 30, 31, 32, 33, 19, 35, 36, 37, 38, 18, 40, 41, 42, 43, 17, 45, 46, 47, 48, 16, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 135, 78, 79, 80, 81, 134, 83, 84, 85, 86, 133, 88, 89, 90, 91, 132, 93, 94, 95, 96, 131, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 29, 34, 39, 44, 49, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '2F2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 135, 134, 133, 132, 131, 21, 22, 23, 24, 25, 26, 27, 28, 97, 30, 31, 32, 33, 92, 35, 36, 37, 38, 87, 40, 41, 42, 43, 82, 45, 46, 47, 48, 77, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 49, 78, 79, 80, 81, 44, 83, 84, 85, 86, 39, 88, 89, 90, 91, 34, 93, 94, 95, 96, 29, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 20, 19, 18, 17, 16, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '2L': (0, 1, 124, 3, 4, 5, 6, 119, 8, 9, 10, 11, 114, 13, 14, 15, 16, 109, 18, 19, 20, 21, 104, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 2, 53, 54, 55, 56, 7, 58, 59, 60, 61, 12, 63, 64, 65, 66, 17, 68, 69, 70, 71, 22, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 147, 105, 106, 107, 108, 142, 110, 111, 112, 113, 137, 115, 116, 117, 118, 132, 120, 121, 122, 123, 127, 125, 126, 52, 128, 129, 130, 131, 57, 133, 134, 135, 136, 62, 138, 139, 140, 141, 67, 143, 144, 145, 146, 72, 148, 149, 150),
 "2L'": (0, 1, 52, 3, 4, 5, 6, 57, 8, 9, 10, 11, 62, 13, 14, 15, 16, 67, 18, 19, 20, 21, 72, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 127, 53, 54, 55, 56, 132, 58, 59, 60, 61, 137, 63, 64, 65, 66, 142, 68, 69, 70, 71, 147, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 22, 105, 106, 107, 108, 17, 110, 111, 112, 113, 12, 115, 116, 117, 118, 7, 120, 121, 122, 123, 2, 125, 126, 124, 128, 129, 130, 131, 119, 133, 134, 135, 136, 114, 138, 139, 140, 141, 109, 143, 144, 145, 146, 104, 148, 149, 150),
 '2L2': (0, 1, 127, 3, 4, 5, 6, 132, 8, 9, 10, 11, 137, 13, 14, 15, 16, 142, 18, 19, 20, 21, 147, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 124, 53, 54, 55, 56, 119, 58, 59, 60, 61, 114, 63, 64, 65, 66, 109, 68, 69, 70, 71, 104, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 72, 105, 106, 107, 108, 67, 110, 111, 112, 113, 62, 115, 116, 117, 118, 57, 120, 121, 122, 123, 52, 125, 126, 2, 128, 129, 130, 131, 7, 133, 134, 135, 136, 12, 138, 139, 140, 141, 17, 143, 144, 145, 146, 22, 148, 149, 150),
 '2R': (0, 1, 2, 3, 54, 5, 6, 7, 8, 59, 10, 11, 12, 13, 64, 15, 16, 17, 18, 69, 20, 21, 22, 23, 74, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 129, 55, 56, 57, 58, 134, 60, 61, 62, 63, 139, 65, 66, 67, 68, 144, 70, 71, 72, 73, 149, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 24, 103, 104, 105, 106, 19, 108, 109, 110, 111, 14, 113, 114, 115, 116, 9, 118, 119, 120, 121, 4, 123, 124, 125, 126, 127, 128, 122, 130, 131, 132, 133, 117, 135, 136, 137, 138, 112, 140, 141, 142, 143, 107, 145, 146, 147, 148, 102, 150),
 "2R'": (0, 1, 2, 3, 122, 5, 6, 7, 8, 117, 10, 11, 12, 13, 112, 15, 16, 17, 18, 107, 20, 21, 22, 23, 102, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 4, 55, 56, 57, 58, 9, 60, 61, 62, 63, 14, 65, 66, 67, 68, 19, 70, 71, 72, 73, 24, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 149, 103, 104, 105, 106, 144, 108, 109, 110, 111, 139, 113, 114, 115, 116, 134, 118, 119, 120, 121, 129, 123, 124, 125, 126, 127, 128, 54, 130, 131, 132, 133, 59, 135, 136, 137, 138, 64, 140, 141, 142, 143, 69, 145, 146, 147, 148, 74, 150),
 '2R2': (0, 1, 2, 3, 129, 5, 6, 7, 8, 134, 10, 11, 12, 13, 139, 15, 16, 17, 18, 144, 20, 21, 22, 23, 149, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 122, 55, 56, 57, 58, 117, 60, 61, 62, 63, 112, 65, 66, 67, 68, 107, 70, 71, 72, 73, 102, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 74, 103, 104, 105, 106, 69, 108, 109, 110, 111, 64, 113, 114, 115, 116, 59, 118, 119, 120, 121, 54, 123, 124, 125, 126, 127, 128, 4, 130, 131, 132, 133, 9, 135, 136, 137, 138, 14, 140, 141, 142, 143, 19, 145, 146, 147, 148, 24, 150),
 '2U': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 56, 57, 58, 59, 60, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 81, 82, 83, 84, 85, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 106, 107, 108, 109, 110, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 31, 32, 33, 34, 35, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "2U'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 106, 107, 108, 109, 110, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 31, 32, 33, 34, 35, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 56, 57, 58, 59, 60, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 81, 82, 83, 84, 85, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '2U2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 81, 82, 83, 84, 85, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 106, 107, 108, 109, 110, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 31, 32, 33, 34, 35, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 56, 57, 58, 59, 60, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '3F': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 48, 43, 38, 33, 28, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 136, 29, 30, 31, 32, 137, 34, 35, 36, 37, 138, 39, 40, 41, 42, 139, 44, 45, 46, 47, 140, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 11, 79, 80, 81, 82, 12, 84, 85, 86, 87, 13, 89, 90, 91, 92, 14, 94, 95, 96, 97, 15, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 98, 93, 88, 83, 78, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "3F'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 78, 83, 88, 93, 98, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 15, 29, 30, 31, 32, 14, 34, 35, 36, 37, 13, 39, 40, 41, 42, 12, 44, 45, 46, 47, 11, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 140, 79, 80, 81, 82, 139, 84, 85, 86, 87, 138, 89, 90, 91, 92, 137, 94, 95, 96, 97, 136, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 28, 33, 38, 43, 48, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '3F2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 140, 139, 138, 137, 136, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 98, 29, 30, 31, 32, 93, 34, 35, 36, 37, 88, 39, 40, 41, 42, 83, 44, 45, 46, 47, 78, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 48, 79, 80, 81, 82, 43, 84, 85, 86, 87, 38, 89, 90, 91, 92, 33, 94, 95, 96, 97, 28, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 15, 14, 13, 12, 11, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '3L': (0, 1, 2, 123, 4, 5, 6, 7, 118, 9, 10, 11, 12, 113, 14, 15, 16, 17, 108, 19, 20, 21, 22, 103, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 3, 54, 55, 56, 57, 8, 59, 60, 61, 62, 13, 64, 65, 66, 67, 18, 69, 70, 71, 72, 23, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 148, 104, 105, 106, 107, 143, 109, 110, 111, 112, 138, 114, 115, 116, 117, 133, 119, 120, 121, 122, 128, 124, 125, 126, 127, 53, 129, 130, 131, 132, 58, 134, 135, 136, 137, 63, 139, 140, 141, 142, 68, 144, 145, 146, 147, 73, 149, 150),
 "3L'": (0, 1, 2, 53, 4, 5, 6, 7, 58, 9, 10, 11, 12, 63, 14, 15, 16, 17, 68, 19, 20, 21, 22, 73, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 128, 54, 55, 56, 57, 133, 59, 60, 61, 62, 138, 64, 65, 66, 67, 143, 69, 70, 71, 72, 148, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 23, 104, 105, 106, 107, 18, 109, 110, 111, 112, 13, 114, 115, 116, 117, 8, 119, 120, 121, 122, 3, 124, 125, 126, 127, 123, 129, 130, 131, 132, 118, 134, 135, 136, 137, 113, 139, 140, 141, 142, 108, 144, 145, 146, 147, 103, 149, 150),
 '3L2': (0, 1, 2, 128, 4, 5, 6, 7, 133, 9, 10, 11, 12, 138, 14, 15, 16, 17, 143, 19, 20, 21, 22, 148, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 123, 54, 55, 56, 57, 118, 59, 60, 61, 62, 113, 64, 65, 66, 67, 108, 69, 70, 71, 72, 103, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 73, 104, 105, 106, 107, 68, 109, 110, 111, 112, 63, 114, 115, 116, 117, 58, 119, 120, 121, 122, 53, 124, 125, 126, 127, 3, 129, 130, 131, 132, 8, 134, 135, 136, 137, 13, 139, 140, 141, 142, 18, 144, 145, 146, 147, 23, 149, 150),
 '3U': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 61, 62, 63, 64, 65, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 86, 87, 88, 89, 90, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 111, 112, 113, 114, 115, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 36, 37, 38, 39, 40, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 "3U'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 111, 112, 113, 114, 115, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 36, 37, 38, 39, 40, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 61, 62, 63, 64, 65, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 86, 87, 88, 89, 90, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 '3U2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 86, 87, 88, 89, 90, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 111, 112, 113, 114, 115, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 36, 37, 38, 39, 40, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 61, 62, 63, 64, 65, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150),
 'B': (0, 80, 85, 90, 95, 100, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 5, 27, 28, 29, 30, 4, 32, 33, 34, 35, 3, 37, 38, 39, 40, 2, 42, 43, 44, 45, 1, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 150, 81, 82, 83, 84, 149, 86, 87, 88, 89, 148, 91, 92, 93, 94, 147, 96, 97, 98, 99, 146, 121, 116, 111, 106, 101, 122, 117, 112, 107, 102, 123, 118, 113, 108, 103, 124, 119, 114, 109, 104, 125, 120, 115, 110, 105, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 26, 31, 36, 41, 46),
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
 'x2': (0, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25),
 'y': (0, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146),
 "y'": (0, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130),
 'y2': (0, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126),
 'z': (0, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130, 71, 66, 61, 56, 51, 72, 67, 62, 57, 52, 73, 68, 63, 58, 53, 74, 69, 64, 59, 54, 75, 70, 65, 60, 55, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 105, 110, 115, 120, 125, 104, 109, 114, 119, 124, 103, 108, 113, 118, 123, 102, 107, 112, 117, 122, 101, 106, 111, 116, 121, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80),
 "z'": (0, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 55, 60, 65, 70, 75, 54, 59, 64, 69, 74, 53, 58, 63, 68, 73, 52, 57, 62, 67, 72, 51, 56, 61, 66, 71, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146, 121, 116, 111, 106, 101, 122, 117, 112, 107, 102, 123, 118, 113, 108, 103, 124, 119, 114, 109, 104, 125, 120, 115, 110, 105, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46),
 'z2': (0, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)}

def rotate_555(cube, step):
    return [cube[x] for x in swaps_555[step]]
