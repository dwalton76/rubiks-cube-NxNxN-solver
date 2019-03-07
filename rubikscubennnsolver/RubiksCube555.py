#!/usr/bin/env python3

from rubikscubennnsolver import RubiksCube, NotSolving, wing_str_map, wing_strs_all
from rubikscubennnsolver.misc import pre_steps_to_try
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444

# This will consume about 200M when you import it
from rubikscubennnsolver.RubiksCube555HighLowEdges import highlow_edge_values

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

MIN_EO_COUNT_FOR_STAGE_LR_432 = 5

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

x_centers_555 = (
    7, 9, 13, 17, 19, # Upper
    32, 34, 38, 42, 44, # Left
    57, 59, 63, 67, 69, # Front
    82, 84, 88, 92, 94, # Right
    107, 109, 113, 117, 119, # Back
    132, 134, 138, 142, 144, # Down
)

t_centers_555 = (
    8, 12, 13, 14, 18, # Upper
    33, 37, 38, 39, 43, # Left
    58, 62, 63, 64, 68, # Front
    83, 87, 88, 89, 93, # Right
    108, 112, 113, 114, 118, # Back
    133, 137, 138, 139, 143, # Down
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

wings_555 = (
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

high_edges_555 = (
    (2, 104),
    (10, 79),
    (24, 54),
    (16, 29),

    (35, 56),
    (41, 120),
    (85, 106),
    (91, 70),

    (127, 72),
    (135, 97),
    (149, 122),
    (141, 47),
)

low_edges_555 = (
    (4, 102),
    (20, 77),
    (22, 52),
    (6, 27),

    (31, 110),
    (45, 66),

    (81, 60),
    (95, 116),

    (129, 74),
    (145, 99),
    (147, 124),
    (131, 49),
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
                high_low = highlow_edge_values[(square_index, partner_index, square_value, partner_value)]

                # If the edge is paired always use an uppercase letter to represent this edge
                if uppercase_paired_edges and square_index in paired_edges_indexes:
                    state[square_index] = midges_map[wing_str].upper()
                    state[partner_index] = midges_map[wing_str].upper()

                # If this is a high wing use the uppercase of the midge edge_index
                elif high_low == 'U':
                    state[square_index] = midges_map[wing_str].upper()
                    state[partner_index] = midges_map[wing_str].upper()

                # If this is a low wing use the lowercase of the midge edge_index
                # high_low will be 'D' here
                else:
                    state[square_index] = midges_map[wing_str]
                    state[partner_index] = midges_map[wing_str]

    # Where is the midge for each high/low wing?
    for (_, square_index, partner_index) in edges_recolor_tuples_555:
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
                high_low = highlow_edge_values[(square_index, partner_index, square_value, partner_value)]

                # If this is a high wing use the uppercase of the midge edge_index
                if high_low == 'U':
                    state[square_index] = midges_map[wing_str].upper()
                    state[partner_index] = midges_map[wing_str].upper()

                # If this is a low wing use the lowercase of the midge edge_index
                # high_low will be 'D' here
                else:
                    state[square_index] = midges_map[wing_str]
                    state[partner_index] = midges_map[wing_str]

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

    def ida_heuristic(self):
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
            (('lookup-table-5x5x5-step10-UD-centers-stage.txt', 14759145, '343288ec28eeaaa2a02dede2c1485c10'),
             ('lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.cost-only.txt', 16711681, '95464b63ec32f831c0f844916f3bbee9'),
             ('lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.cost-only.txt', 16711681, '19679794a853d38a7d36be0f03fe1c3b')),
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

    def ida_heuristic(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in self.LFRB_t_centers_555])
        return (self.hex_format % int(result, 2), 0)


class LookupTable555LRTCenterStageOdd(LookupTable):
    """
    lookup-table-5x5x5-step21-LR-t-centers-stage-odd.txt
    ====================================================
    1 steps has 2 entries (0 percent, 0.00x previous step)
    2 steps has 24 entries (0 percent, 12.00x previous step)
    3 steps has 142 entries (1 percent, 5.92x previous step)
    4 steps has 412 entries (3 percent, 2.90x previous step)
    5 steps has 946 entries (7 percent, 2.30x previous step)
    6 steps has 3,412 entries (26 percent, 3.61x previous step)
    7 steps has 4,957 entries (38 percent, 1.45x previous step)
    8 steps has 2,692 entries (20 percent, 0.54x previous step)
    9 steps has 275 entries (2 percent, 0.10x previous step)
    10 steps has 8 entries (0 percent, 0.03x previous step)

    Total: 12,870 entries
    Average: 6.69 moves
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
            'lookup-table-5x5x5-step21-LR-t-centers-stage-odd.txt',
            'f0f0',
            linecount=12870,
            max_depth=10,
            filesize=514800)

    def ida_heuristic(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in self.LFRB_t_centers_555])
        return (self.hex_format % int(result, 2), 0)


class LookupTable555LRTCenterStageEven(LookupTable):
    """
    lookup-table-5x5x5-step21-LR-t-centers-stage-even.txt
    =====================================================
    1 steps has 1 entries (0 percent, 0.00x previous step)
    2 steps has 1 entries (0 percent, 1.00x previous step)
    3 steps has 68 entries (0 percent, 68.00x previous step)
    4 steps has 512 entries (3 percent, 7.53x previous step)
    5 steps has 1,968 entries (15 percent, 3.84x previous step)
    6 steps has 3,771 entries (29 percent, 1.92x previous step)
    7 steps has 3,396 entries (26 percent, 0.90x previous step)
    8 steps has 2,619 entries (20 percent, 0.77x previous step)
    9 steps has 532 entries (4 percent, 0.20x previous step)
    10 steps has 2 entries (0 percent, 0.00x previous step)

    Total: 12,870 entries
    Average: 6.55 moves
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
            'lookup-table-5x5x5-step21-LR-t-centers-stage-even.txt',
            'f0f0',
            linecount=12870,
            max_depth=10,
            filesize=501930)

    def ida_heuristic(self):
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
            #(('lookup-table-5x5x5-step20-LR-centers-stage.txt', 5170308, '3d13c62d7a982023d0376f56ecdf2812'),  # 6-deep
            (('lookup-table-5x5x5-step20-LR-centers-stage.txt', 522024, 'ae9ec50e8857e89f475f7d85b34a77b3'),  # 5-deep
             ('lookup-table-5x5x5-step21-LR-t-centers-stage.cost-only.txt', None, '8fa5217b28c7aeb9e04684ae3f5bebee'),
             ('lookup-table-5x5x5-step22-LR-x-centers-stage.cost-only.txt', None, '4e4d8a8ec35d0c999ce7c51b6681bc4e')),
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

    def ida_heuristic(self):
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
            #(('lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt', 24368616, '5a0bad50c3e650dbd2677e29aba17eca'), # 6-deep
            (('lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt', 2416601, 'ac39d8406d55e7ddf9f0967a35fddd00'), # 5-deep
             ('lookup-table-5x5x5-step31-UL-centers-solve.hash-cost-only.txt', 24010032, 'b9e47314dbbb37690d4aed370b3b2245'),
             ('lookup-table-5x5x5-step32-UF-centers-solve.hash-cost-only.txt', 24010032, '966f865fffe4b5c2ce7301767c3f19f7'),
             ('lookup-table-5x5x5-step33-LF-centers-solve.hash-cost-only.txt', 24010032, '7ea2ddf0e97094cc8f5d9c11df0176fe')),
            '5x5x5-centers-solve' # C_ida_type
        )

        self.recolor_positions = centers_555
        self.recolor_map = {
            'D' : 'x',
            'R' : 'x',
            'B' : 'x',
        }
        self.nuke_corners = True
        #self.nuke_edges = True


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

    def ida_heuristic(self):
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

    def ida_heuristic(self):
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

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join(['F' if parent_state[x] == 'B' else parent_state[x] for x in LFRB_t_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555LRCenterStage432PairOneEdge(LookupTable):
    """
    lookup-table-5x5x5-step43-LR-centers-stage-432-pair-one-edge.txt
    ================================================================
    1 steps has 18 entries (0 percent, 0.00x previous step)
    2 steps has 84 entries (2 percent, 4.67x previous step)
    3 steps has 344 entries (9 percent, 4.10x previous step)
    4 steps has 938 entries (27 percent, 2.73x previous step)
    5 steps has 1,572 entries (45 percent, 1.68x previous step)
    6 steps has 500 entries (14 percent, 0.32x previous step)

    Total: 3,456 entries
    Average: 4.58 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step43-LR-centers-stage-432-pair-one-edge.txt',
            ('---------Rrr------------------------',
             '---------rRR------------------------'),
            linecount=3456,
            max_depth=6,
            filesize=203904)

    def ida_heuristic(self):
        assert self.only_colors and len(self.only_colors) == 1, "You must specify which 1-edge"
        state = edges_recolor_pattern_555(self.parent.state[:], self.only_colors)
        state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555LRCenterStage432(LookupTableIDA):
    """
    lookup-table-5x5x5-step40-LR-centers-stage-432.txt
    ==================================================
    1 steps has 1,692 entries (0 percent, 0.00x previous step)
    2 steps has 16,832 entries (0 percent, 9.95x previous step)
    3 steps has 194,000 entries (8 percent, 11.53x previous step)
    4 steps has 2,138,044 entries (90 percent, 11.02x previous step)

    Total: 2,350,568 entries
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

            linecount=2350568,
            max_depth=4,
            filesize=133982376,
        )

    def search_complete(self, state, steps_to_here):
        if LookupTableIDA.search_complete(self, state, steps_to_here):
            pairable_count = len(self.parent.edges_pairable_without_LR())

            # Technically we only need 4-edges to be in high/low groups but that leaves us
            # zero wiggle room for the next phase, we will HAVE to pair those 4-edges and
            # if we hit some bad luck they could take a higher number of moves than is typical
            # to pair.  If we have 6-edges in high/low groups though that leaves us 15 permutations
            # of 4-edges to choose from..
            if pairable_count >= MIN_EO_COUNT_FOR_STAGE_LR_432:
                #log.info("%s: found solution where %d-edges (min %d-edges) are EOed" % (self, pairable_count, MIN_EO_COUNT_FOR_STAGE_LR_432))
                return True
            else:
                #log.info("%s: found solution but only %d-edges are EOed" % (self, pairable_count))
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
                return False
        else:
            return False

    def ida_heuristic(self):
        parent_state = self.parent.state
        lt_state = ''.join(['F' if parent_state[x] == 'B' else parent_state[x] for x in LFRB_centers_555])

        (_, LR_stage_cost_to_goal) = self.parent.lt_LR_centers_stage_pt.ida_heuristic()
        (_, LR_432_x_centers_cost_to_goal) = self.parent.lt_LR_432_x_centers_only.ida_heuristic()
        (_, LR_432_t_centers_cost_to_goal) = self.parent.lt_LR_432_t_centers_only.ida_heuristic()

        cost_to_goal = max(LR_stage_cost_to_goal, LR_432_x_centers_cost_to_goal, LR_432_t_centers_cost_to_goal)

        if cost_to_goal > 0:
            steps = self.steps(lt_state)

            if steps:
                cost_to_goal = len(steps)
            else:
                cost_to_goal = max(cost_to_goal, self.max_depth + 1)

        #self.parent.print_cube()
        #log.info("%s: lt_state %s, cost_to_goal %d, LR_stage_cost_to_goal %d, LR_432_x_centers_cost_to_goal %d, LR_432_t_centers_cost_to_goal %d" %
        #    (self, lt_state, cost_to_goal,
        #     LR_stage_cost_to_goal, LR_432_x_centers_cost_to_goal, LR_432_t_centers_cost_to_goal))
        return (lt_state, cost_to_goal)


#class LookupTable555EdgesZPlaneEdgesOnly(LookupTable):
class LookupTable555EdgesZPlaneEdgesOnly(LookupTableHashCostOnly):
    """
    lookup-table-5x5x5-step341-edges-z-plane-edges-only.txt
    =======================================================
    1 steps has 20 entries (0 percent, 0.00x previous step)
    2 steps has 136 entries (0 percent, 6.80x previous step)
    3 steps has 1,080 entries (0 percent, 7.94x previous step)
    4 steps has 9,588 entries (0 percent, 8.88x previous step)
    5 steps has 76,960 entries (0 percent, 8.03x previous step)
    6 steps has 572,044 entries (0 percent, 7.43x previous step)
    7 steps has 3,771,232 entries (0 percent, 6.59x previous step)
    8 steps has 20,862,480 entries (5 percent, 5.53x previous step)
    9 steps has 83,953,652 entries (21 percent, 4.02x previous step)
    10 steps has 178,801,180 entries (46 percent, 2.13x previous step)
    11 steps has 93,704,032 entries (24 percent, 0.52x previous step)
    12 steps has 1,575,596 entries (0 percent, 0.02x previous step)

    Total: 383,328,000 entries
    Average: 9.89 moves
    """

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step341-edges-z-plane-edges-only.txt',
            ('---pPPQQq------------------xXX------',
             '------QQq------------------xXXYYy---',
             '---pPP---------------------xXXYYy---',
             '---pPPQQq---------------------YYy---'),
            linecount=383328000,
            max_depth=12,
            filesize=31432896000)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step341-edges-z-plane-edges-only.hash-cost-only.txt',
            '---pPPQQq------------------xXX------',
            linecount=1,
            max_depth=12,
            bucketcount=383328041,
            filesize=383328042)

    def ida_heuristic(self):
        assert self.only_colors and len(self.only_colors) == 3, "You must specify which 3-edges"
        parent_state = self.parent.state
        state = edges_recolor_pattern_555(parent_state[:], self.only_colors)
        state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555EdgesZPlaneCentersOnly(LookupTable):
    """
    lookup-table-5x5x5-step342-edges-z-plane-centers-only.txt
    =========================================================
    1 steps has 18 entries (4 percent, 0.00x previous step)
    2 steps has 38 entries (8 percent, 2.11x previous step)
    3 steps has 74 entries (17 percent, 1.95x previous step)
    4 steps has 108 entries (25 percent, 1.46x previous step)
    5 steps has 102 entries (23 percent, 0.94x previous step)
    6 steps has 52 entries (12 percent, 0.51x previous step)
    7 steps has 40 entries (9 percent, 0.77x previous step)

    Total: 432 entries
    Average: 4.28 moves
    """

    state_targets = (
        'LLLLLLLLLRRRRRRRRR',
        'LLLLLLRRRLLLRRRRRR',
        'LLLLLLRRRRRRRRRLLL',
        'RRRLLLLLLLLLRRRRRR',
        'RRRLLLLLLRRRRRRLLL',
        'RRRLLLRRRLLLRRRLLL'
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step342-edges-z-plane-centers-only.txt',
            self.state_targets,
            linecount=432,
            max_depth=7,
            filesize=19872)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join([parent_state[x] for x in LR_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555EdgesZPlane(LookupTableIDA):
    """
    lookup-table-5x5x5-step340-edges-z-plane.txt
    ============================================
    1 steps has 30 entries (0 percent, 0.00x previous step)
    2 steps has 264 entries (0 percent, 8.80x previous step)
    3 steps has 2,764 entries (0 percent, 10.47x previous step)
    4 steps has 29,276 entries (0 percent, 10.59x previous step)
    5 steps has 319,486 entries (8 percent, 10.91x previous step)
    6 steps has 3,457,886 entries (90 percent, 10.82x previous step)

    Total: 3,809,706 entries
    """

    state_targets = (
        'LLLLLLLLLRRRRRRRRR---pPPQQq------------------xXXYYy---',
        'LLLLLLRRRLLLRRRRRR---pPPQQq------------------xXXYYy---',
        'LLLLLLRRRRRRRRRLLL---pPPQQq------------------xXXYYy---',
        'RRRLLLLLLLLLRRRRRR---pPPQQq------------------xXXYYy---',
        'RRRLLLLLLRRRRRRLLL---pPPQQq------------------xXXYYy---',
        'RRRLLLRRRLLLRRRLLL---pPPQQq------------------xXXYYy---',
    )

    heuristic_stats = {
        (0, 1): 1,
        (0, 2): 2,
        (0, 3): 3,
        (0, 4): 4,
        (0, 5): 5,
        (0, 6): 6,
        (0, 7): 7,
        (0, 8): 8,
        (0, 9): 9,
        (0, 10): 12,
        (1, 1): 1,
        (1, 2): 2,
        (1, 3): 3,
        (1, 4): 4,
        (1, 5): 5,
        (1, 6): 6,
        (1, 7): 7,
        (1, 8): 8,
        (1, 9): 9,
        (1, 10): 11,
        (1, 11): 12,
        (2, 1): 3,
        (2, 2): 2,
        (2, 3): 3,
        (2, 4): 4,
        (2, 5): 5,
        (2, 6): 6,
        (2, 7): 7,
        (2, 8): 8,
        (2, 9): 10,
        (2, 10): 11,
        (2, 11): 12,
        (3, 2): 4,
        (3, 3): 3,
        (3, 4): 4,
        (3, 5): 5,
        (3, 6): 6,
        (3, 7): 7,
        (3, 8): 8,
        (3, 9): 10,
        (3, 10): 12,
        (3, 11): 12,
        (4, 3): 6,
        (4, 4): 5,
        (4, 5): 6,
        (4, 6): 6,
        (4, 7): 7,
        (4, 8): 8,
        (4, 9): 10,
        (4, 10): 12,
        (4, 11): 13,
        (5, 4): 6,
        (5, 5): 7,
        (5, 6): 7,
        (5, 7): 8,
        (5, 8): 9,
        (5, 9): 11,
        (5, 10): 12,
        (5, 11): 13,
        (6, 5): 8,
        (6, 6): 8,
        (6, 7): 8,
        (6, 8): 9,
        (6, 9): 11,
        (6, 10): 13,
        (6, 11): 14,
        (7, 7): 10,
        (7, 8): 9,
        (7, 9): 12,
        (7, 10): 14,
        (7, 11): 13
    }

    # For cube LLFBRBFUDULBULBBDDUBBBBLDFDULDLURFBDFRLDUFDBRLDUFBLURFRFRDRBULFBLLLBURUFRFURDDLBULLLRLRDFRDRBBRUDFDUFRBUDULFDUFULDFRBRBULLUFFBLRDDDDFRRBUBRLBUUFFRRDFF
    # 2 : 14 moves in 42s
    # 1 : 14 moves in 8s
    # 0 : 15 moves in 4s

    # FRFFBLUUFLFFUDLFLUDBRFBLLFUDBRRUULDUDRLBLFBDDUDRRLFDLFDUULUUFRFRLDRBLDDRUBRBFRDBLDBFFUBDDBDFFRFLUDFURBRUUUBDBLBRLLLBRUDBFLFULDUDBDRRRLRDFBLURBFBRBLRBU
    # 2 : 14 moves in 14s
    # 1 : 14 moves in 8s
    # 0 : 14 moves in 800ms
    heuristic_stats_error = 0

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step340-edges-z-plane.txt',
            self.state_targets,
            moves_555,

            # illegal moves
            ("Fw", "Fw'",
             "Bw", "Bw'",
             "Lw", "Lw'",
             "Rw", "Rw'",
             "Uw", "Uw'",
             "Dw", "Dw'",
             "L", "L'",
             "R", "R'",
            ),

            linecount=3809706,
            max_depth=6,
            filesize=297157068,
        )

        if self.parent.cpu_mode == "slow":
            LookupTableIDA555EdgesZPlane.heuristic_stats_error = 1
        elif self.parent.cpu_mode == "normal":
            LookupTableIDA555EdgesZPlane.heuristic_stats_error = 0
        elif self.parent.cpu_mode == "fast":
            LookupTableIDA555EdgesZPlane.heuristic_stats_error = 0

    def ida_heuristic_tuple(self):
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        state = edges_recolor_pattern_555(self.parent.state[:], self.only_colors)
        edges_state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        (centers_state, centers_cost_to_goal) = self.parent.lt_edges_z_plane_centers_only.ida_heuristic()
        lt_state = centers_state + edges_state

        three_wing_cost_to_goal = []

        for three_wing_str_combo in itertools.combinations(self.only_colors, 3):
            self.parent.lt_edges_z_plane_edges_only.only_colors = three_wing_str_combo
            (_, tmp_cost_to_goal) = self.parent.lt_edges_z_plane_edges_only.ida_heuristic()
            three_wing_cost_to_goal.append(tmp_cost_to_goal)

        edges_cost_to_goal = max(three_wing_cost_to_goal)

        return (centers_cost_to_goal, edges_cost_to_goal)

    def search_complete(self, state, steps_to_here):
        if LookupTableIDA.search_complete(self, state, steps_to_here):

            # If we are not finding a solution for a "fewest move challenge" then go ahead
            # and return True here and do not worry about trying to find a solution that
            # allows us to skip step350.
            if not self.parent.cpu_mode == "slow":
                return True

            # Are the edges in a state in the step351 table?  We must flip the edges around
            # to their native orientation in order to check.
            tmp_state = self.parent.state[:]
            self.parent.edges_flip_to_original_orientation(self.parent.get_y_plane_wing_strs(), self.parent.get_x_plane_z_plane_wing_strs())
            (eo_state, eo_steps) = self.parent.lt_x_plane_y_plane_orient_edges_edges_only.ida_heuristic()
            #log.info("%s: step351 EO state %s, EO steps %s, state_target %s" %
            #    (self, eo_state, pformat(eo_steps), bool(eo_state in self.lt_x_plane_y_plane_orient_edges_edges_only.state_target)))
            self.parent.state = tmp_state[:]

            # return True if the EO state for step351 is at one of its state targets. This allows us
            # to avoid step350 completely.
            if eo_state in self.parent.lt_x_plane_y_plane_orient_edges_edges_only.state_target:
                log.info("%s: found solution where edges are EOed per step351" % self)
                return True
            else:
                #log.info("%s: found solution but edges are not EOed per step351" % self)
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
                return False
        else:
            return False

    def ida_heuristic(self):
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        state = edges_recolor_pattern_555(self.parent.state[:], self.only_colors)
        edges_state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        (centers_state, centers_cost_to_goal) = self.parent.lt_edges_z_plane_centers_only.ida_heuristic()

        three_wing_cost_to_goal = []

        for three_wing_str_combo in itertools.combinations(self.only_colors, 3):
            self.parent.lt_edges_z_plane_edges_only.only_colors = three_wing_str_combo
            (_, tmp_cost_to_goal) = self.parent.lt_edges_z_plane_edges_only.ida_heuristic()
            three_wing_cost_to_goal.append(tmp_cost_to_goal)

        edges_cost_to_goal = max(three_wing_cost_to_goal)
        cost_to_goal = max(centers_cost_to_goal, edges_cost_to_goal)
        lt_state = centers_state + edges_state

        if cost_to_goal > 0:
            steps = self.steps(lt_state)

            if steps:
                cost_to_goal = len(steps)
            else:
                heuristic_stats_cost = self.heuristic_stats.get((centers_cost_to_goal, edges_cost_to_goal), 0)
                cost_to_goal = max(centers_cost_to_goal, edges_cost_to_goal,
                    self.max_depth + 1, heuristic_stats_cost - self.heuristic_stats_error)

            if lt_state in self.state_targets:
                cost_to_goal = 0

        #log.info("%s: lt_state %s, cost_to_goal %d, centers_cost_to_goal %d, edges_cost_to_goal %d, three_wing_cost_to_goal %s" % (
        #    self, lt_state, cost_to_goal, centers_cost_to_goal, edges_cost_to_goal, pformat(three_wing_cost_to_goal)))
        return (lt_state, cost_to_goal)


class LookupTable555XPlaneYPlaneEdgesOrientEdgesOnly(LookupTable):
    """
    starting-states-lookup-table-5x5x5-step351-x-plane-y-plane-edges-orient-edges-only.txt
    ======================================================================================
    1 steps has 678,720 entries (75 percent, 0.00x previous step)
    2 steps has 212,100 entries (23 percent, 0.31x previous step)
    3 steps has 8,960 entries (0 percent, 0.04x previous step)
    4 steps has 1,120 entries (0 percent, 0.12x previous step)

    Total: 900,900 entries
    Average: 1.26 moves

    The average is actually 0.87 moves because 343,000 of the 678,720 in "1 step" are
    state targets so those are "0 step".
    """

    def __init__(self, parent):
        from rubikscubennnsolver.RubiksCube555StartingStates import starting_states_step351

        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step351-x-plane-y-plane-edges-orient-edges-only.txt',
            starting_states_step351,
            linecount=900900,
            max_depth=4,
            filesize=79279200)

    def ida_heuristic(self):
        state = self.parent.highlow_edges_state()
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555XPlaneYPlaneEdgesOrientCentersOnly(LookupTable):
    """
    lookup-table-5x5x5-step352-x-plane-y-plane-edges-orient-centers-only.txt
    ========================================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 23 entries (0 percent, 7.67x previous step)
    3 steps has 234 entries (0 percent, 10.17x previous step)
    4 steps has 1,845 entries (0 percent, 7.88x previous step)
    5 steps has 13,782 entries (0 percent, 7.47x previous step)
    6 steps has 98,191 entries (1 percent, 7.12x previous step)
    7 steps has 559,026 entries (8 percent, 5.69x previous step)
    8 steps has 1,951,300 entries (30 percent, 3.49x previous step)
    9 steps has 2,896,714 entries (45 percent, 1.48x previous step)
    10 steps has 840,858 entries (13 percent, 0.29x previous step)
    11 steps has 8,674 entries (0 percent, 0.01x previous step)

    Total: 6,370,650 entries
    Average: 8.60 moves
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step352-x-plane-y-plane-edges-orient-centers-only.txt',
            'UUUUUUUUUFFFFFFFFFFFFFFFFFFUUUUUUUUU',
            linecount=6370650,
            max_depth=11,
            filesize=509652000)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join(['U' if parent_state[x] in ('U', 'D') else 'F' for x in UFBD_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555XPlaneYPlaneEdgesOrientCentersOnlyHashTable(LookupTableHashCostOnly):
    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step352-x-plane-y-plane-edges-orient-centers-only.hash-cost-only.txt',
            'UUUUUUUUUFFFFFFFFFFFFFFFFFFUUUUUUUUU',
            linecount=1,
            max_depth=11,
            bucketcount=6370667,
            filesize=6370668)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join(['U' if parent_state[x] in ('U', 'D') else 'F' for x in UFBD_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555XPlaneYPlaneEdgesOrientPairOneEdge(LookupTable):
    """
    lookup-table-5x5x5-step353-x-plane-y-plane-edges-orient-pair-one-edge.txt
    =========================================================================
    1 steps has 7 entries (1 percent, 0.00x previous step)
    2 steps has 28 entries (5 percent, 4.00x previous step)
    3 steps has 90 entries (17 percent, 3.21x previous step)
    4 steps has 195 entries (38 percent, 2.17x previous step)
    5 steps has 184 entries (35 percent, 0.94x previous step)
    6 steps has 8 entries (1 percent, 0.04x previous step)

    Total: 512 entries
    Average: 4.06 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step353-x-plane-y-plane-edges-orient-pair-one-edge.txt',
            '---------rRR------------------------',
            linecount=512,
            max_depth=6,
            filesize=29696)

    def ida_heuristic(self):
        assert self.only_colors and len(self.only_colors) == 1, "You must specify which 1-edge"
        state = edges_recolor_pattern_555(self.parent.state[:], self.only_colors)
        state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555XPlaneYPlaneEdgesOrient(LookupTableIDA):
    """
    lookup-table-5x5x5-step350-x-plane-y-plane-edges-orient.txt
    ===========================================================
    1 steps has 1,029,000 entries (11 percent, 0.00x previous step)
    2 steps has 7,889,000 entries (88 percent, 7.67x previous step)

    Total: 8,918,000 entries
    """

    def __init__(self, parent):
        from rubikscubennnsolver.RubiksCube555StartingStates import starting_states_step350

        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step350-x-plane-y-plane-edges-orient.txt',
            starting_states_step350,
            moves_555,
            # illegal moves
            (),

            #linecount=1029000,
            #max_depth=1,
            #filesize=120393000,

            linecount=8918000,
            max_depth=2,
            filesize=1043406000,

            legal_moves=(
                "F", "F'", "F2",
                "B", "B'", "B2",
                "L2", "R2", "U2", "B2",

                "Uw2", "Dw2",
                "Lw2", "Rw2",

                "2U2", "2D2",
                "2L", "2L'", "2L2",
                "2R", "2R'", "2R2",
            )
        )

    def ida_heuristic(self):
        parent_state = self.parent.state
        (edges_state, edges_cost_to_goal) = self.parent.lt_x_plane_y_plane_orient_edges_edges_only.ida_heuristic()
        (centers_state, centers_cost_to_goal) = self.parent.lt_x_plane_y_plane_orient_edges_centers_only_ht.ida_heuristic()

        lt_state = centers_state + edges_state
        cost_to_goal = max(centers_cost_to_goal, edges_cost_to_goal)

        if cost_to_goal > 0:
            steps = self.steps(lt_state)

            if steps:
                cost_to_goal = len(steps)
            else:
                cost_to_goal = max(cost_to_goal, self.max_depth + 1)

        return (lt_state, cost_to_goal)


class LookupTable555XPlaneYPlaneEdgesOrientFBCentersEdgesOnly(LookupTable):
    """
    lookup-table-5x5x5-step361-x-plane-y-plane-edges-orient-fb-centers-edges-only.txt
    =================================================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 15 entries (0 percent, 5.00x previous step)
    3 steps has 78 entries (0 percent, 5.20x previous step)
    4 steps has 414 entries (0 percent, 5.31x previous step)
    5 steps has 2,206 entries (0 percent, 5.33x previous step)
    6 steps has 10,506 entries (3 percent, 4.76x previous step)
    7 steps has 39,298 entries (11 percent, 3.74x previous step)
    8 steps has 100,432 entries (29 percent, 2.56x previous step)
    9 steps has 137,320 entries (40 percent, 1.37x previous step)
    10 steps has 49,592 entries (14 percent, 0.36x previous step)
    11 steps has 3,136 entries (0 percent, 0.06x previous step)

    Total: 343,000 entries
    Average: 8.52 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step361-x-plane-y-plane-edges-orient-fb-centers-edges-only.txt',
            'UUDUDDDDUDUUUDDUDDDDUDDUDUUDUDDUDUUDUDDUDDDDUDDUDUUDUDDUDUUDUUDUDDDDUDUU',
            linecount=343000,
            max_depth=11,
            filesize=38416000)

    def ida_heuristic(self):
        state = self.parent.highlow_edges_state()
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555XPlaneYPlaneEdgesOrientFBCentersOnly(LookupTable):
    """
    lookup-table-5x5x5-step362-x-plane-y-plane-edges-orient-fb-centers-only.txt
    ===========================================================================
    1 steps has 28 entries (0 percent, 0.00x previous step)
    2 steps has 110 entries (2 percent, 3.93x previous step)
    3 steps has 396 entries (8 percent, 3.60x previous step)
    4 steps has 1,196 entries (24 percent, 3.02x previous step)
    5 steps has 2,102 entries (42 percent, 1.76x previous step)
    6 steps has 1,016 entries (20 percent, 0.48x previous step)
    7 steps has 52 entries (1 percent, 0.05x previous step)

    Total: 4,900 entries
    Average: 4.73 moves
    """

    state_targets = (
        'BFBBFBBFBFBFFBFFBF',
        'BFFBFFBFFBBFBBFBBF',
        'BFFBFFBFFFBBFBBFBB',
        'FFBFFBFFBBBFBBFBBF',
        'FFBFFBFFBFBBFBBFBB',
        'FFFFFFFFFBBBBBBBBB'
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step362-x-plane-y-plane-edges-orient-fb-centers-only.txt',
            self.state_targets,
            linecount=4900,
            max_depth=7,
            filesize=220500)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join([parent_state[x] for x in FB_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555XPlaneYPlaneEdgesOrientFBCenters(LookupTableIDA):
    """
    lookup-table-5x5x5-step360-x-plane-y-plane-edges-orient-fb-centers.txt
    ======================================================================
    1 steps has 30 entries (0 percent, 0.00x previous step)
    2 steps has 176 entries (0 percent, 5.87x previous step)
    3 steps has 1,182 entries (0 percent, 6.72x previous step)
    4 steps has 7,684 entries (0 percent, 6.50x previous step)
    5 steps has 49,668 entries (2 percent, 6.46x previous step)
    6 steps has 317,818 entries (13 percent, 6.40x previous step)
    7 steps has 1,982,008 entries (84 percent, 6.24x previous step)

    Total: 2,358,566 entries
    """

    state_targets = (
        'BFBBFBBFBFBFFBFFBFUUDUDDDDUDUUUDDUDDDDUDDUDUUDUDDUDUUDUDDUDDDDUDDUDUUDUDDUDUUDUUDUDDDDUDUU',
        'BFFBFFBFFBBFBBFBBFUUDUDDDDUDUUUDDUDDDDUDDUDUUDUDDUDUUDUDDUDDDDUDDUDUUDUDDUDUUDUUDUDDDDUDUU',
        'BFFBFFBFFFBBFBBFBBUUDUDDDDUDUUUDDUDDDDUDDUDUUDUDDUDUUDUDDUDDDDUDDUDUUDUDDUDUUDUUDUDDDDUDUU',
        'FFBFFBFFBBBFBBFBBFUUDUDDDDUDUUUDDUDDDDUDDUDUUDUDDUDUUDUDDUDDDDUDDUDUUDUDDUDUUDUUDUDDDDUDUU',
        'FFBFFBFFBFBBFBBFBBUUDUDDDDUDUUUDDUDDDDUDDUDUUDUDDUDUUDUDDUDDDDUDDUDUUDUDDUDUUDUUDUDDDDUDUU',
        'FFFFFFFFFBBBBBBBBBUUDUDDDDUDUUUDDUDDDDUDDUDUUDUDDUDUUDUDDUDDDDUDDUDUUDUDDUDUUDUUDUDDDDUDUU'
    )

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step360-x-plane-y-plane-edges-orient-fb-centers.txt',
            self.state_targets,
            moves_555,
            # illegal moves
            (),

            linecount=2358566,
            max_depth=7,
            filesize=278310788,

            legal_moves=(
                "F", "F'", "F2",
                "B", "B'", "B2",
                "L2", "R2", "U2", "B2",

                "Uw2", "Dw2",
                "Lw2", "Rw2",
            )
        )

    def ida_heuristic(self):
        parent_state = self.parent.state
        (edges_state, edges_cost_to_goal) = self.parent.lt_x_plane_y_plane_orient_edges_fb_centers_edges_only.ida_heuristic()
        (centers_state, centers_cost_to_goal) = self.parent.lt_x_plane_y_plane_orient_edges_fb_centers_centers_only.ida_heuristic()

        lt_state = centers_state + edges_state
        cost_to_goal = max(centers_cost_to_goal, edges_cost_to_goal)

        if cost_to_goal > 0:
            steps = self.steps(lt_state)

            if steps:
                cost_to_goal = len(steps)
            else:
                cost_to_goal = max(cost_to_goal, self.max_depth + 1)

        return (lt_state, cost_to_goal)



#class LookupTable555PairLastEightEdgesEdgesOnly(LookupTable):
class LookupTable555PairLastEightEdgesEdgesOnly(LookupTableHashCostOnly):
    """
    lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.txt
    ===============================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 26 entries (0 percent, 5.20x previous step)
    3 steps has 156 entries (0 percent, 6.00x previous step)
    4 steps has 999 entries (0 percent, 6.40x previous step)
    5 steps has 5,892 entries (0 percent, 5.90x previous step)
    6 steps has 36,376 entries (0 percent, 6.17x previous step)
    7 steps has 222,480 entries (0 percent, 6.12x previous step)
    8 steps has 1,301,886 entries (0 percent, 5.85x previous step)
    9 steps has 7,238,228 entries (0 percent, 5.56x previous step)
    10 steps has 36,410,756 entries (4 percent, 5.03x previous step)
    11 steps has 144,974,952 entries (17 percent, 3.98x previous step)
    12 steps has 343,690,470 entries (42 percent, 2.37x previous step)
    13 steps has 262,142,742 entries (32 percent, 0.76x previous step)
    14 steps has 16,825,016 entries (2 percent, 0.06x previous step)
    15 steps has 1,216 entries (0 percent, 0.00x previous step)

    Total: 812,851,200 entries
    Average: 12.06 moves
    """

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.txt',
            'OOopPPQQqrRR------------WWwxXXYYyzZZ',
            linecount=812851200,
            max_depth=15,
            filesize=73969459200)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.hash-cost-only.txt',
            'OOopPPQQqrRR------------WWwxXXYYyzZZ',
            linecount=1,
            max_depth=15,
            bucketcount=812851219,
            filesize=812851220)

    def ida_heuristic(self):
        assert self.only_colors and len(self.only_colors) == 8, "You must specify which 8-edges"
        state = edges_recolor_pattern_555(self.parent.state[:], self.only_colors)
        state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


#class LookupTable555PairLastEightEdgesCentersOnly(LookupTableHashCostOnly):
class LookupTable555PairLastEightEdgesCentersOnly(LookupTable):
    """
    lookup-table-5x5x5-step502-pair-last-eight-edges-centers-only.txt
    =================================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 42 entries (0 percent, 8.40x previous step)
    3 steps has 280 entries (0 percent, 6.67x previous step)
    4 steps has 1,691 entries (0 percent, 6.04x previous step)
    5 steps has 8,806 entries (4 percent, 5.21x previous step)
    6 steps has 36,264 entries (20 percent, 4.12x previous step)
    7 steps has 77,966 entries (44 percent, 2.15x previous step)
    8 steps has 46,518 entries (26 percent, 0.60x previous step)
    9 steps has 4,828 entries (2 percent, 0.10x previous step)

    Total: 176,400 entries
    Average: 6.98 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step502-pair-last-eight-edges-centers-only.txt',
            'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD',
            linecount=176400,
            max_depth=9,
            filesize=15699600)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step502-pair-last-eight-edges-centers-only.hash-cost-only.txt',
            'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD',
            linecount=1,
            max_depth=9,
            bucketcount=176401,
            filesize=176402)
        '''

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join([parent_state[x] for x in centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555PairLastEightEdges(LookupTableIDA):
    """
    lookup-table-5x5x5-step500-pair-last-eight-edges.txt
    ====================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 42 entries (0 percent, 8.40x previous step)
    3 steps has 380 entries (0 percent, 9.05x previous step)
    4 steps has 3,425 entries (0 percent, 9.01x previous step)
    5 steps has 29,807 entries (1 percent, 8.70x previous step)
    6 steps has 259,083 entries (10 percent, 8.69x previous step)
    7 steps has 2,235,143 entries (88 percent, 8.63x previous step)

    Total: 2,527,885 entries
    """

    heuristic_stats = {
        (0, 0): 0,
        (1, 1): 1,
        (1, 2): 7,
        (1, 3): 8,
        (1, 4): 5,
        (1, 5): 5,
        (1, 6): 6,
        (2, 1): 4,
        (2, 2): 2,
        (2, 3): 3,
        (2, 4): 4,
        (2, 5): 6,
        (2, 6): 7,
        (2, 7): 7,
        (2, 9): 14,
        (2, 12): 17,
        (3, 0): 5,
        (3, 1): 3,
        (3, 2): 3,
        (3, 3): 3,
        (3, 4): 4,
        (3, 5): 6,
        (3, 6): 7,
        (3, 7): 8,
        (3, 8): 12,
        (3, 9): 13,
        (3, 10): 14,
        (3, 11): 14,
        (3, 13): 15,
        (4, 0): 4,
        (4, 1): 5,
        (4, 2): 4,
        (4, 3): 5,
        (4, 4): 4,
        (4, 5): 6,
        (4, 6): 7,
        (4, 7): 9,
        (4, 8): 11,
        (4, 9): 12,
        (4, 10): 14,
        (4, 11): 15,
        (4, 12): 15,
        (4, 13): 18,
        (5, 1): 5,
        (5, 2): 6,
        (5, 3): 5,
        (5, 4): 6,
        (5, 5): 7,
        (5, 6): 8,
        (5, 7): 9,
        (5, 8): 11,
        (5, 9): 12,
        (5, 10): 14,
        (5, 11): 15,
        (5, 12): 16,
        (5, 13): 18,
        (6, 2): 6,
        (6, 3): 7,
        (6, 4): 6,
        (6, 5): 8,
        (6, 6): 9,
        (6, 7): 9,
        (6, 8): 11,
        (6, 9): 12,
        (6, 10): 14,
        (6, 11): 15,
        (6, 12): 16,
        (6, 13): 17,
        (6, 14): 16,
        (7, 3): 7,
        (7, 4): 8,
        (7, 5): 8,
        (7, 6): 9,
        (7, 7): 10,
        (7, 8): 11,
        (7, 9): 12,
        (7, 10): 14,
        (7, 11): 15,
        (7, 12): 16,
        (7, 13): 17,
        (7, 14): 17,
        (8, 6): 11,
        (8, 7): 12,
        (8, 8): 12,
        (8, 9): 13,
        (8, 10): 14,
        (8, 11): 15,
        (8, 12): 16,
        (8, 13): 17,
        (8, 14): 17,
        (9, 7): 12,
        (9, 8): 13,
        (9, 9): 12,
        (9, 10): 14,
        (9, 11): 15,
        (9, 12): 16,
        (9, 13): 16
    }

    # The higher this number the less you honor the heuristic_stats
    # -  0 uses the heuristic_stats exactly as reported
    # -  1 subtracts 1 from the heuristic_stats value
    # - 99 disables heuristic_stats
    #
    # You want to put this as high as you can but low enough
    # to still speed up the slow IDA searches.
    #
    # LLFBRBFUDULBULBBDDUBBBBLDFDULDLURFBDFRLDUFDBRLDUFBLURFRFRDRBULFBLLLBURUFRFURDDLBULLLRLRDFRDRBBRUDFDUFRBUDULFDUFULDFRBRBULLUFFBLRDDDDFRRBUBRLBUUFFRRDFF
    # 99 : gave up after 5min
    #  3 : 17 moves in 1m 21s
    #  2 : 17 moves in 25s
    #  1 : 17 moves in 4s
    #  0 : 17 moves in 800ms
    #
    # BDBULBULFRDLUFDBBBUBDLRFBRRRDFUBLBBLBRURRFUULDBUDLRFBUUFLBRBFRFFDLLUDURFBULFRLRBFRDBUDDDFRDFFULFDFFDUDFDBDRBLLURLDLBDULBDFBUUULURLRDRRLFDBRLUDLFLFRUFR
    #  3 : 17 moves in 2m 45s
    #  2 : 17 moves in 25s
    #  1 : 17 moves in 3.4s
    #  0 : 18 moves in 5s
    #
    # FRFFBLUUFLFFUDLFLUDBRFBLLFUDBRRUULDUDRLBLFBDDUDRRLFDLFDUULUUFRFRLDRBLDDRUBRBFRDBLDBFFUBDDBDFFRFLUDFURBRUUUBDBLBRLLLBRUDBFLFULDUDBDRRRLRDFBLURBFBRBLRBU
    #  3 : 16 moves in 5s
    #  2 : 16 moves in 600ms
    #  1 : 17 moves in 900ms
    #  0 : 18 moves in 1200ms
    heuristic_stats_error = 0

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step500-pair-last-eight-edges.txt',
            'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDDOOopPPQQqrRR------------WWwxXXYYyzZZ',
            moves_555,
            # illegal moves
            ("Fw", "Fw'",
             "Bw", "Bw'",
             "Lw", "Lw'",
             "Rw", "Rw'",
             "Uw", "Uw'", "Uw2",
             "Dw", "Dw'", "Dw2",
             "L", "L'",
             "R", "R'",
             "F", "F'",
             "B", "B'",
            ),

            linecount=2527885,
            max_depth=7,
            filesize=300818315,
        )

        if self.parent.cpu_mode == "slow":
            LookupTableIDA555PairLastEightEdges.heuristic_stats_error = 2
        elif self.parent.cpu_mode == "normal":
            LookupTableIDA555PairLastEightEdges.heuristic_stats_error = 1
        elif self.parent.cpu_mode == "fast":
            LookupTableIDA555PairLastEightEdges.heuristic_stats_error = 0

    def ida_heuristic_tuple(self):
        (edges_state, edges_cost_to_goal) = self.parent.lt_pair_last_eight_edges_edges_only.ida_heuristic()
        (centers_state, centers_cost_to_goal) = self.parent.lt_pair_last_eight_edges_centers_only.ida_heuristic()
        return (centers_cost_to_goal, edges_cost_to_goal)

    def ida_heuristic(self):
        parent_state = self.parent.state
        (edges_state, edges_cost_to_goal) = self.parent.lt_pair_last_eight_edges_edges_only.ida_heuristic()
        (centers_state, centers_cost_to_goal) = self.parent.lt_pair_last_eight_edges_centers_only.ida_heuristic()
        cost_to_goal = max(centers_cost_to_goal, edges_cost_to_goal)
        lt_state = centers_state + edges_state

        if cost_to_goal > 0:
            steps = self.steps(lt_state)

            if steps:
                cost_to_goal = len(steps)
            else:
                heuristic_stats_cost = self.heuristic_stats.get((centers_cost_to_goal, edges_cost_to_goal), 0)
                cost_to_goal = max(centers_cost_to_goal, edges_cost_to_goal,
                    self.max_depth + 1, heuristic_stats_cost - self.heuristic_stats_error)

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
        (2, 104), (3, 103), (4, 102), (6, 27), (10, 79), (11, 28), (15, 78), (16, 29), (20, 77), (22, 52), (23, 53), (24, 54),                # Upper
        (27, 6), (28, 11), (29, 16), (31, 110), (35, 56), (36, 115), (40, 61), (41, 120), (45, 66), (47, 141), (48, 136), (49, 131),          # Left
        (52, 22), (53, 23), (54, 24), (56, 35), (60, 81), (61, 40), (65, 86), (66, 45), (70, 91), (72, 127), (73, 128), (74, 129),            # Front
        (77, 20), (78, 15), (79, 10), (81, 60), (85, 106), (86, 65), (90, 111), (91, 70), (95, 116), (97, 135), (98, 140), (99, 145),         # Right
        (102, 4), (103, 3), (104, 2), (106, 85), (110, 31), (111, 90), (115, 36), (116, 95), (120, 41), (122, 149), (123, 148), (124, 147),   # Back
        (127, 72), (128, 73), (129, 74), (131, 49), (135, 97), (136, 48), (140, 98), (141, 47), (145, 99), (147, 124), (148, 123), (149, 122) # Down
    )

    reduce333_orient_edges_x_plane_y_plane_tuples = (
        (2, 104), (4, 102), (22, 52), (24, 54),                                                  # Upper
        (31, 110), (35, 56), (41, 120), (45, 66),                                                # Left
        (52, 22), (54, 24), (56, 35), (60, 81), (66, 45), (70, 91), (72, 127), (74, 129),        # Front
        (81, 60), (85, 106), (91, 70), (95, 116),                                                # Right
        (102, 4), (104, 2), (106, 85), (110, 31), (116, 95), (120, 41), (122, 149), (124, 147),  # Back
        (127, 72), (129, 74), (147, 124), (149, 122)                                             # Down
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

    def x_plane_edges_are_l4e(self):
        state = self.state
        edges_in_plane = set()

        for square_index in (31, 36, 41, 35, 40, 45, 81, 86, 91, 85, 90, 95):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            edges_in_plane.add(wing_str)

        return len(edges_in_plane) == 4

    def y_plane_edges_are_l4e(self):
        state = self.state
        edges_in_plane = set()

        for square_index in (2, 3, 4, 22, 23, 24, 127, 128, 129, 147, 148, 149):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            edges_in_plane.add(wing_str)

        return len(edges_in_plane) == 4

    def z_plane_edges_are_l4e(self):
        state = self.state
        edges_in_plane = set()

        for square_index in (6, 11, 16, 10, 15, 20, 131, 136, 141, 135, 140, 145):
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            edges_in_plane.add(wing_str)

        return len(edges_in_plane) == 4

    def sanity_check(self):
        centers = (13, 38, 63, 88, 113, 138)

        self._sanity_check('edge-orbit-0', edge_orbit_0_555, 8)
        self._sanity_check('edge-orbit-1', edge_orbit_1_555, 4)
        self._sanity_check('corners', corners_555, 4)
        #self._sanity_check('x-centers', x_centers_555, 4)
        #self._sanity_check('t-centers', t_centers_555, 4)
        self._sanity_check('centers', centers, 1)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_UD_T_centers_stage = LookupTable555UDTCenterStage(self)
        self.lt_UD_centers_stage = LookupTableIDA555UDCentersStage(self)
        self.lt_LR_T_centers_stage = LookupTable555LRTCenterStage(self)
        self.lt_LR_T_centers_stage_odd = LookupTable555LRTCenterStageOdd(self)
        self.lt_LR_T_centers_stage_even = LookupTable555LRTCenterStageEven(self)
        self.lt_LR_centers_stage = LookupTableIDA555LRCentersStage(self)
        self.lt_ULFRBD_centers_solve = LookupTableIDA555ULFRBDCentersSolve(self)
        self.lt_ULFRBD_t_centers_solve = LookupTable555TCenterSolve(self)
        self.lt_LR_T_centers_stage_odd.preload_cache_string()
        self.lt_LR_T_centers_stage_even.preload_cache_string()

        self.lt_LR_432_pair_one_edge = LookupTable555LRCenterStage432PairOneEdge(self)
        self.lt_LR_centers_stage_pt = LookupTable555LRCenterStage(self)
        self.lt_LR_432_x_centers_only = LookupTable555LRCenterStage432XCentersOnly(self)
        self.lt_LR_432_t_centers_only = LookupTable555LRCenterStage432TCentersOnly(self)
        self.lt_LR_432_centers_stage = LookupTableIDA555LRCenterStage432(self)
        self.lt_LR_432_pair_one_edge.preload_cache_dict()
        self.lt_LR_432_x_centers_only.preload_cache_string()
        self.lt_LR_432_t_centers_only.preload_cache_string()
        self.lt_LR_432_centers_stage.preload_cache_string()

        self.lt_edges_z_plane_edges_only = LookupTable555EdgesZPlaneEdgesOnly(self)
        self.lt_edges_z_plane_centers_only = LookupTable555EdgesZPlaneCentersOnly(self)
        self.lt_edges_z_plane = LookupTableIDA555EdgesZPlane(self)
        self.lt_edges_z_plane_centers_only.preload_cache_dict()
        self.lt_edges_z_plane.preload_cache_string()

        self.lt_x_plane_y_plane_orient_edges_edges_only = LookupTable555XPlaneYPlaneEdgesOrientEdgesOnly(self)
        self.lt_x_plane_y_plane_orient_edges_centers_only = LookupTable555XPlaneYPlaneEdgesOrientCentersOnly(self)
        self.lt_x_plane_y_plane_orient_edges_centers_only_ht = LookupTable555XPlaneYPlaneEdgesOrientCentersOnlyHashTable(self)
        self.lt_x_plane_y_plane_orient_edges_pair_one_edge = LookupTable555XPlaneYPlaneEdgesOrientPairOneEdge(self)
        self.lt_x_plane_y_plane_orient_edges = LookupTableIDA555XPlaneYPlaneEdgesOrient(self)
        self.lt_x_plane_y_plane_orient_edges_edges_only.preload_cache_dict()
        self.lt_x_plane_y_plane_orient_edges.preload_cache_string()
        self.lt_x_plane_y_plane_orient_edges_pair_one_edge.preload_cache_dict()
        self.lt_x_plane_y_plane_orient_edges_centers_only.preload_cache_string()

        self.lt_x_plane_y_plane_orient_edges_fb_centers_edges_only = LookupTable555XPlaneYPlaneEdgesOrientFBCentersEdgesOnly(self)
        self.lt_x_plane_y_plane_orient_edges_fb_centers_centers_only = LookupTable555XPlaneYPlaneEdgesOrientFBCentersOnly(self)
        self.lt_x_plane_y_plane_orient_edges_fb_centers = LookupTableIDA555XPlaneYPlaneEdgesOrientFBCenters(self)
        self.lt_x_plane_y_plane_orient_edges_fb_centers_edges_only.preload_cache_dict()
        self.lt_x_plane_y_plane_orient_edges_fb_centers_centers_only.preload_cache_dict()
        self.lt_x_plane_y_plane_orient_edges_fb_centers.preload_cache_string()

        self.lt_pair_last_eight_edges_edges_only = LookupTable555PairLastEightEdgesEdgesOnly(self)
        self.lt_pair_last_eight_edges_centers_only = LookupTable555PairLastEightEdgesCentersOnly(self)
        self.lt_pair_last_eight_edges = LookupTableIDA555PairLastEightEdges(self)
        self.lt_pair_last_eight_edges_centers_only.preload_cache_dict()
        self.lt_pair_last_eight_edges.preload_cache_string()
        #self.lt_pair_last_eight_edges.preload_cache_dict()

    def highlow_edges_state(self):
        state = self.state
        result = [highlow_edge_values[(x, y, state[x], state[y])] for (x, y) in self.reduce333_orient_edges_tuples]
        result = ''.join(result)
        return result

    def highlow_edges_print(self):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()

        orient_edge_state = list(self.highlow_edges_state())
        orient_edge_state_index = 0
        for side in list(self.sides.values()):
            for square_index in side.edge_pos:
                self.state[square_index] = orient_edge_state[orient_edge_state_index]
                orient_edge_state_index += 1
        self.print_cube()

        self.state = original_state[:]
        self.solution = original_solution[:]

    def print_eo_state(self):
        tmp_state = self.state[:]
        self.edges_flip_to_original_orientation(self.get_y_plane_wing_strs(), self.get_x_plane_z_plane_wing_strs())

        (eo_state, eo_steps) = self.lt_x_plane_y_plane_orient_edges_edges_only.ida_heuristic()
        log.info("%s: step351 EO state %s, EO steps %s, state_target %s" %
            (self, eo_state, pformat(eo_steps), bool(eo_state in self.lt_x_plane_y_plane_orient_edges_edges_only.state_target)))

        (eo_state, eo_steps) = self.lt_x_plane_y_plane_orient_edges_fb_centers_edges_only.ida_heuristic()
        log.info("%s: step361 EO state %s, EO steps %s, state_target %s" %
            (self, eo_state, pformat(eo_steps), bool(eo_state in self.lt_x_plane_y_plane_orient_edges_fb_centers_edges_only.state_target)))

        self.state = tmp_state[:]

    def group_centers_stage_UD(self):
        """
        Stage UD centers
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if not self.UD_centers_staged():
            tmp_solution_len = len(self.solution)
            self.lt_UD_centers_stage.solve()
            self.print_cube()
            self.solution.append("COMMENT_%d_steps_555_UD_centers_staged" % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:]))

        log.info("%s: UD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_centers_stage_LR(self):
        """
        Stage LR centers
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if not self.UD_centers_staged():
            raise SolveError("UD centers must be staged to stage LR centers")

        # Test the prune tables
        #self.lt_LR_T_centers_stage.solve()
        #self.lt_LR_X_centers_stage.solve()
        #self.print_cube()

        if not self.LR_centers_staged():
            tmp_solution_len = len(self.solution)
            self.lt_LR_centers_stage.solve()
            self.print_cube()
            self.solution.append("COMMENT_%d_steps_555_LR_centers_staged" % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:]))
        log.info("%s: ULFRBD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def group_centers_stage_LR_to_432(self):
        """
        Stage LR centers to one of 432 states that can be solved with L L' R R'
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        # Test the prune tables
        #self.lt_LR_T_centers_stage.solve()
        #self.lt_LR_X_centers_stage.solve()
        #self.print_cube()

        tmp_solution_len = len(self.solution)
        self.lt_LR_432_centers_stage.avoid_oll = 0
        self.lt_LR_432_centers_stage.solve()
        self.print_cube()
        self.solution.append("COMMENT_%d_steps_555_LR_centers_staged" % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:]))

        pairable_count = len(self.edges_pairable_without_LR())
        orbits_with_oll_parity = self.center_solution_leads_to_oll_parity()
        log.info("%s: LR centers staged to one of 432 states, %d-edges EOed (%d min), orbits with OLL %s, %d steps in" %
            (self, pairable_count, MIN_EO_COUNT_FOR_STAGE_LR_432, pformat(orbits_with_oll_parity), self.get_solution_len_minus_rotates(self.solution)))

    def edges_pairable_without_LR(self):
        """
        Return the wing_strs that can be paired without L L' R R'
        """
        state = self.state
        original_state = self.state[:]
        original_solution = self.solution[:]
        pairable = []

        for wing_str in wing_strs_all:
            self.lt_LR_432_pair_one_edge.only_colors = set([wing_str, ])
            self.state = original_state[:]
            self.solution = original_solution[:]

            try:
                self.lt_LR_432_pair_one_edge.solve()
                #log.info("%s: wing_str %s can be paired without L L' R R'" % (self, wing_str))
                pairable.append(wing_str)
            except NoSteps:
                pass

        self.lt_LR_432_pair_one_edge.only_colors = set()
        self.state = original_state[:]
        self.solution = original_solution[:]

        #log.info("%s: pairable %s (%d of them)" % (
        #    self, pformat(pairable), len(pairable)))
        return tuple(sorted(pairable))

    def edges_pairable_without_LRFB(self):
        """
        Return the wing_strs that can be paired without L L' R R' F F' B B'
        """
        state = self.state
        original_state = self.state[:]
        original_solution = self.solution[:]
        pairable = []

        for wing_str in self.get_y_plane_z_plane_wing_strs():
            self.lt_x_plane_y_plane_orient_edges_pair_one_edge.only_colors = set([wing_str, ])
            self.state = original_state[:]
            self.solution = original_solution[:]

            try:
                self.lt_x_plane_y_plane_orient_edges_pair_one_edge.solve()
                #log.info("%s: wing_str %s can be paired without L L' R R' F F' B B'" % (self, wing_str))
                pairable.append(wing_str)
            except NoSteps:
                #log.info("%s: wing_str %s can NOT be paired without L L' R R' F F' B B'" % (self, wing_str))
                pass

        self.lt_x_plane_y_plane_orient_edges_pair_one_edge.only_colors = set()
        self.state = original_state[:]
        self.solution = original_solution[:]

        #log.info("%s: pairable %s (%d of them)" % (
        #    self, pformat(pairable), len(pairable)))
        return tuple(sorted(pairable))

    def edges_flip_to_original_orientation(self, must_be_uppercase=[], must_be_lowercase=[]):
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

            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if must_be_uppercase or must_be_lowercase:
                #log.info("must_be_uppercase %s, must_be_lowercase %s" % (must_be_uppercase, must_be_lowercase))

                if wing_str in must_be_uppercase and edges_state[edge_state_index].islower():
                    to_flip.append(wing_str)
                elif wing_str in must_be_lowercase and edges_state[edge_state_index].isupper():
                    to_flip.append(wing_str)
            else:
                if edges_state[edge_state_index].islower():
                    to_flip.append(wing_str)

        for square_index in wings_for_edges_pattern_555:
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in to_flip:
                self.state[square_index] = partner_value
                self.state[partner_index] = square_value

    def get_x_plane_z_plane_wing_strs(self):
        result = []

        # The 4 paired edges are in the x-plane so look at midges in the y-plane and z-plane
        for square_index in (36, 40, 86, 90, 11, 15, 136, 140):
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            result.append(wing_str)

        return set(result)

    def get_x_plane_wing_strs(self):
        result = []

        for square_index in (36, 40, 86, 90):
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            result.append(wing_str)

        return set(result)

    def get_y_plane_wing_strs(self):
        result = []

        for square_index in (3, 23, 128, 148):
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            result.append(wing_str)

        return set(result)

    def get_z_plane_wing_strs(self):
        result = []

        for square_index in (11, 15, 136, 140):
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            result.append(wing_str)

        return set(result)

    def get_y_plane_z_plane_wing_strs(self):
        result = []

        # The 4 paired edges are in the x-plane so look at midges in the y-plane and z-plane
        for square_index in (3, 11, 15, 23, 128, 136, 140, 148):
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            result.append(wing_str)

        return set(result)

    def pair_z_plane_edges(self):
        """
        When we staged the LR centers to one of 432 states we did so such that there
        are at least MIN_EO_COUNT_FOR_STAGE_LR_432 edges that can be paired without
        L L' R R'. Those will be the "pairable" edges below. Find the combination of
        4-edges that has the lowest cost_to_goal, pair those edges and place them in
        the z-plane.  This phase also puts the LR centers into horizontal bars.
        """
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(original_solution)

        self.edges_flip_to_original_orientation()

        #paired_edges_count = self.get_paired_edges_count()
        #log.info("%s: %d-edges are already paired" % (self, paired_edges_count))

        # Are the z-plane edges already paired?
        if self.z_plane_edges_paired():
            min_wing_str_combo = self.get_z_plane_wing_strs()

        # TODO what if there are 4-paired edges somewhere?  We should use those
        else:
            pairable = self.edges_pairable_without_LR()
            log.info("%s: z-plane pairable edges %s" % (self, pformat(pairable)))

            min_cost_to_goal = None
            min_wing_str_combo = None

            # Which combination of 4-edges has the lowest cost_to_goal?
            for wing_str_combo in itertools.combinations(pairable, 4):
                wing_str_combo = sorted(wing_str_combo)

                #debug = bool(wing_str_combo == ['LF', 'RB', 'UB', 'UF'])
                debug = False

                if debug:
                    log.info("wing_str_combo: %s" % pformat(wing_str_combo))
                three_wing_cost_to_goal = []

                for three_wing_str_combo in itertools.combinations(wing_str_combo, 3):
                    self.lt_edges_z_plane_edges_only.only_colors = three_wing_str_combo
                    (_, tmp_cost_to_goal) = self.lt_edges_z_plane_edges_only.ida_heuristic()

                    if debug:
                        log.info("three_wing_str_combo: %s cost_to_goal %d" % (pformat(three_wing_str_combo), tmp_cost_to_goal))
                    three_wing_cost_to_goal.append(tmp_cost_to_goal)

                cost_to_goal = max(three_wing_cost_to_goal)

                if min_cost_to_goal is None or cost_to_goal < min_cost_to_goal:
                    min_cost_to_goal = cost_to_goal
                    min_wing_str_combo = wing_str_combo
                    log.info("z-plane wing_str_combo %s, cost_to_goal %d (NEW MIN)" % (pformat(wing_str_combo), cost_to_goal))
                #else:
                #    log.info("z-plane wing_str_combo %s, cost_to_goal %d" % (pformat(wing_str_combo), cost_to_goal))

        self.lt_edges_z_plane.only_colors = min_wing_str_combo
        self.lt_edges_z_plane.solve()
        z_plane_edges_solution = self.solution[original_solution_len:]

        # Now put the cube back to the original state before we flipped all of
        # the edges to their native orientation, then apply the solution we found.
        self.state = original_state[:]
        self.solution = original_solution[:]
        tmp_solution_len = len(self.solution)

        for step in z_plane_edges_solution:
            self.rotate(step)

        self.print_cube()
        self.print_eo_state()
        self.solution.append("COMMENT_%d_steps_555_LR_horizontal_bars_and_z_plane_edges_paired" % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:]))
        log.info("%s: LR centers in horizontal bars, z-plane edges paired, %d steps in" % (self,
             self.get_solution_len_minus_rotates(self.solution)))

    def pair_last_eight_edges(self):
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(original_solution)

        self.edges_flip_to_original_orientation(self.get_y_plane_wing_strs(), self.get_x_plane_z_plane_wing_strs())

        tmp_solution_len = len(self.solution)
        #self.lt_x_plane_y_plane_orient_edges_edges_only.solve()
        #self.lt_x_plane_y_plane_orient_edges_centers_only.solve()
        #self.lt_x_plane_y_plane_orient_edges.avoid_oll = 0

        self.lt_x_plane_y_plane_orient_edges.solve()
        #self.print_cube()
        #self.highlow_edges_print()
        #log.info("%s: 8-edges EOed, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        if len(self.solution) > tmp_solution_len:
            self.solution.append("COMMENT_%d_steps_555_edges_partially_EOed" % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:]))

        log.info("%s: UD and FB centers staged, edges partially EOed, %d steps in" % (self,
            self.get_solution_len_minus_rotates(self.solution)))

        tmp_solution_len = len(self.solution)
        self.lt_x_plane_y_plane_orient_edges_fb_centers.solve()

        tmp_state = self.state[:]
        tmp_solution = self.solution[:]
        min_LR_cost = None
        min_LR_moves = None

        # Of  L,R  L,R'  L',R  L',R'  which sets up better for the next phase?
        for (L_move, R_move) in (
                ("L", "R"),
                ("L", "R'"),
                ("L'", "R"),
                ("L'", "R'")):
            self.rotate(L_move)
            self.rotate(R_move)

            self.lt_pair_last_eight_edges_edges_only.only_colors = self.get_y_plane_z_plane_wing_strs()
            #(_, last_eight_edges_cost) = self.lt_pair_last_eight_edges_edges_only.ida_heuristic()
            (_, last_eight_edges_cost) = self.lt_pair_last_eight_edges.ida_heuristic()

            if min_LR_cost is None or last_eight_edges_cost < min_LR_cost:
                log.info("%s: %s %s leads to last-eight-edges cost %d (NEW MIN)" % (self, L_move, R_move, last_eight_edges_cost))
                min_LR_cost = last_eight_edges_cost
                min_LR_moves = (L_move, R_move)
            else:
                log.info("%s: %s %s leads to last-eight-edges cost %d" % (self, L_move, R_move, last_eight_edges_cost))
            self.state = tmp_state[:]
            self.solution = tmp_solution[:]

        for step in min_LR_moves:
            self.rotate(step)

        pairable_count = len(self.edges_pairable_without_LRFB())
        self.print_cube()
        self.highlow_edges_print()
        self.solution.append("COMMENT_%d_steps_555_FB_vertical_bars_and_edges_EOed" % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:]))
        log.info("%s: LR and FB vertical bars, x-plane paired, %d-edges EOed, %d steps in" % (self,
            pairable_count, self.get_solution_len_minus_rotates(self.solution)))
        assert pairable_count == 8

        tmp_solution_len = len(self.solution)
        self.lt_pair_last_eight_edges_edges_only.only_colors = self.get_y_plane_z_plane_wing_strs()
        #self.lt_pair_last_eight_edges_edges_only.solve()
        #self.lt_pair_last_eight_edges_centers_only.solve()
        self.lt_pair_last_eight_edges.solve()

        # Now put the cube back to the original state before we flipped all of
        # the edges to their native orientation, then apply the solution we found.
        last_eight_edges_solution = self.solution[original_solution_len:]
        self.state = original_state[:]
        self.solution = original_solution[:]

        for step in last_eight_edges_solution:
            if step.startswith('COMMENT'):
                self.solution.append(step)
            else:
                self.rotate(step)

        self.print_cube()
        self.solution.append("COMMENT_%d_steps_555_last_eight_edges_paired" % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:]))
        log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def reduce_333(self):
        self.lt_init()
        #log.info("%s: kociemba %s" % (self, self.get_kociemba_string(True)))

        if not self.centers_solved() or not self.edges_paired():
            self.group_centers_stage_UD()
            self.group_centers_stage_LR_to_432()
            self.pair_z_plane_edges()
            self.pair_last_eight_edges()

        self.solution.append('CENTERS_SOLVED')
        self.solution.append('EDGES_GROUPED')


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
