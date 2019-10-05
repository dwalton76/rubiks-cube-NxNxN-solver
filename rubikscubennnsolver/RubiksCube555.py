from rubikscubennnsolver import RubiksCube, wing_str_map, wing_strs_all, reverse_steps
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.LookupTable import (
    LookupTable,
    LookupTableIDA,
    LookupTableIDAViaC,
    NoIDASolution,
    NoSteps,
)
from rubikscubennnsolver.misc import SolveError
from rubikscubennnsolver.RubiksCubeHighLow import highlow_edge_values_555
from pprint import pformat
import itertools
import logging
import sys
import subprocess

log = logging.getLogger(__name__)

moves_555 = (
    "U", "U'", "U2", "Uw", "Uw'", "Uw2",
    "L", "L'", "L2", "Lw", "Lw'", "Lw2",
    "F", "F'", "F2", "Fw", "Fw'", "Fw2",
    "R", "R'", "R2", "Rw", "Rw'", "Rw2",
    "B", "B'", "B2", "Bw", "Bw'", "Bw2",
    "D", "D'", "D2", "Dw", "Dw'", "Dw2",
    # slices...not used for now
    # "2U", "2U'", "2U2", "2D", "2D'", "2D2",
    # "2L", "2L'", "2L2", "2R", "2R'", "2R2",
    # "2F", "2F'", "2F2", "2B", "2B'", "2B2"
)
solved_555 = "UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB"


centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19,  # Upper
    32, 33, 34, 37, 38, 39, 42, 43, 44,  # Left
    57, 58, 59, 62, 63, 64, 67, 68, 69,  # Front
    82, 83, 84, 87, 88, 89, 92, 93, 94,  # Right
    107, 108, 109, 112, 113, 114, 117, 118, 119,  # Back
    132, 133, 134, 137, 138, 139, 142, 143, 144,  # Down
)

x_centers_555 = (
    7, 9, 13, 17, 19,  # Upper
    32, 34, 38, 42, 44,  # Left
    57, 59, 63, 67, 69,  # Front
    82, 84, 88, 92, 94,  # Right
    107, 109, 113, 117, 119,  # Back
    132, 134, 138, 142, 144,  # Down
)

t_centers_555 = (
    8, 12, 13, 14, 18,  # Upper
    33, 37, 38, 39, 43,  # Left
    58, 62, 63, 64, 68,  # Front
    83, 87, 88, 89, 93,  # Right
    108, 112, 113, 114, 118,  # Back
    133, 137, 138, 139, 143,  # Down
)

UD_centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19,  # Upper
    132, 133, 134, 137, 138, 139, 142, 143, 144,  # Down
)

LR_centers_555 = (
    32, 33, 34, 37, 38, 39, 42, 43, 44,  # Left
    82, 83, 84, 87, 88, 89, 92, 93, 94,  # Right
)

FB_centers_555 = (
    57, 58, 59, 62, 63, 64, 67, 68, 69,  # Front
    107, 108, 109, 112, 113, 114, 117, 118, 119,  # Back
)

UFBD_centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19,  # Upper
    57, 58, 59, 62, 63, 64, 67, 68, 69,  # Front
    107, 108, 109, 112, 113, 114, 117, 118, 119,  # Back
    132, 133, 134, 137, 138, 139, 142, 143, 144,  # Down
)

ULRD_centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19,  # Upper
    32, 33, 34, 37, 38, 39, 42, 43, 44,  # Left
    82, 83, 84, 87, 88, 89, 92, 93, 94,  # Right
    132, 133, 134, 137, 138, 139, 142, 143, 144,  # Down
)

LFRB_centers_555 = (
    32, 33, 34, 37, 38, 39, 42, 43, 44,  # Left
    57, 58, 59, 62, 63, 64, 67, 68, 69,  # Front
    82, 83, 84, 87, 88, 89, 92, 93, 94,  # Right
    107, 108, 109, 112, 113, 114, 117, 118, 119,  # Back
)

LFRB_x_centers_555 = (
    32, 34, 38, 42, 44,  # Left
    57, 59, 63, 67, 69,  # Front
    82, 84, 88, 92, 94,  # Right
    107, 109, 113, 117, 119,  # Back
)

LFRB_t_centers_555 = (
    33, 37, 38, 39, 43,  # Left
    58, 62, 63, 64, 68,  # Front
    83, 87, 88, 89, 93,  # Right
    108, 112, 113, 114, 118,  # Back
)


'''
000 000 000 011 111 111 112 222 222 222 333 333
012 345 678 901 234 567 890 123 456 789 012 345
OOo pPP QQq rRR sSS TTt uUU VVv WWw xXX YYy zZZ
 ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^
 UB  UL  UR  UD  LB  LF  RF  RB  DF  DL  DR  DB
'''
edge_orbit_0_555 = (
    2, 4, 10, 20, 24, 22, 16, 6,
    27, 29, 35, 45, 49, 47, 41, 31,
    52, 54, 60, 70, 74, 72, 66, 56,
    77, 79, 85, 95, 99, 97, 91, 81,
    102, 104, 110, 120, 124, 122, 116, 106,
    127, 129, 135, 145, 149, 147, 141, 131,
)

edge_orbit_1_555 = (
    3, 15, 23, 11,
    28, 40, 48, 36,
    53, 65, 73, 61,
    78, 90, 98, 86,
    103, 115, 123, 111,
    128, 140, 148, 136,
)

corners_555 = (
    1, 5, 21, 25,
    26, 30, 46, 50,
    51, 55, 71, 75,
    76, 80, 96, 100,
    101, 105, 121, 125,
    126, 130, 146, 150,
)

edges_555 = (
    2, 3, 4, 6, 10, 11, 15, 16, 20, 22, 23, 24,
    27, 28, 29, 31, 35, 36, 40, 41, 45, 47, 48, 49,
    52, 53, 54, 56, 60, 61, 65, 66, 70, 72, 73, 74,
    77, 78, 79, 81, 85, 86, 90, 91, 95, 97, 98, 99,
    102, 103, 104, 106, 110, 111, 115, 116, 120, 122, 123, 124,
    127, 128, 129, 131, 135, 136, 140, 141, 145, 147, 148, 149,
)

set_edges_555 = set(edges_555)

wings_555 = (
    # Upper
    2, 3, 4,
    6, 11, 16,
    10, 15, 20,
    22, 23, 24,

    # Left
    31, 36, 41,
    35, 40, 45,

    # Right
    81, 86, 91,
    85, 90, 95,

    # Down
    127, 128, 129,
    131, 136, 141,
    135, 140, 145,
    147, 148, 149,
)

l4e_wings_555 = (
    # Upper
    2, 3, 4,
    6, 11, 16,
    10, 15, 20,
    22, 23, 24,

    # Left
    31, 36, 41,
    35, 40, 45,

    # Right
    81, 86, 91,
    85, 90, 95,

    # Down
    127, 128, 129,
    131, 136, 141,
    135, 140, 145,
    147, 148, 149,
)


wings_for_edges_pattern_555 = (
    # Upper
    2, 3, 4,
    6, 11, 16,
    10, 15, 20,
    22, 23, 24,

    # Left
    31, 36, 41,
    35, 40, 45,

    # Right
    81, 86, 91,
    85, 90, 95,

    # Down
    127, 128, 129,
    131, 136, 141,
    135, 140, 145,
    147, 148, 149,
)

high_wings_and_midges_555 = (
    # Upper
    2, 3, 11, 16, 10, 15, 23, 24,

    # Left
    36, 41, 35, 40,

    # Right
    86, 91, 85, 90,

    # Down
    127, 128, 136, 141, 135, 140, 148, 149
)

low_wings_and_midges_555 = (
    # Upper
    3, 4, 6, 11, 15, 20, 22, 23,

    # Left
    31, 36, 40, 45,

    # Right
    81, 86, 90, 95,

    # Down
    128, 129, 131, 136, 140, 145, 147, 148
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
    149: 122,
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
    ("x'", "y", "y"),
)


edges_recolor_tuples_555 = (
    ("0", 2, 104),  # upper
    ("1", 4, 102),
    ("2", 6, 27),
    ("3", 10, 79),
    ("4", 16, 29),
    ("5", 20, 77),
    ("6", 22, 52),
    ("7", 24, 54),
    ("8", 31, 110),  # left
    ("9", 35, 56),
    ("a", 41, 120),
    ("b", 45, 66),
    ("c", 81, 60),  # right
    ("d", 85, 106),
    ("e", 91, 70),
    ("f", 95, 116),
    ("g", 127, 72),  # down
    ("h", 129, 74),
    ("i", 131, 49),
    ("j", 135, 97),
    ("k", 141, 47),
    ("l", 145, 99),
    ("m", 147, 124),
    ("n", 149, 122),
)

midges_recolor_tuples_555 = (
    ("o", 3, 103),  # upper
    ("p", 11, 28),
    ("q", 15, 78),
    ("r", 23, 53),
    ("s", 36, 115),  # left
    ("t", 40, 61),
    ("u", 86, 65),  # right
    ("v", 90, 111),
    ("w", 128, 73),  # down
    ("x", 136, 48),
    ("y", 140, 98),
    ("z", 148, 123),
)

midge_indexes = (
    3,
    11,
    15,
    23,  # Upper
    28,
    36,
    40,
    48,  # Left
    53,
    61,
    65,
    73,  # Front
    78,
    86,
    90,
    98,  # Right
    103,
    111,
    115,
    123,  # Back
    128,
    136,
    140,
    148,  # Down
)

wings_for_recolor_555 = (
    ("0", 2, 104),  # upper
    ("1", 4, 102),
    ("2", 6, 27),
    ("3", 10, 79),
    ("4", 16, 29),
    ("5", 20, 77),
    ("6", 22, 52),
    ("7", 24, 54),
    ("8", 31, 110),  # left
    ("9", 35, 56),
    ("a", 41, 120),
    ("b", 45, 66),
    ("c", 81, 60),  # right
    ("d", 85, 106),
    ("e", 91, 70),
    ("f", 95, 116),
    ("g", 127, 72),  # down
    ("h", 129, 74),
    ("i", 131, 49),
    ("j", 135, 97),
    ("k", 141, 47),
    ("l", 145, 99),
    ("m", 147, 124),
    ("n", 149, 122),
)

MIDGE_TUPLES_555 = (
    ((3, 103), (103, 3)),
    ((11, 28), (28, 11)),
    ((15, 78), (78, 15)),
    ((23, 53), (53, 23)),

    ((36, 115), (115, 36)),
    ((40, 61), (61, 40)),
    ((86, 65), (65, 86)),
    ((90, 111), (111, 90)),

    ((128, 73), (73, 128)),
    ((136, 48), (48, 136)),
    ((140, 98), (98, 140)),
    ((148, 123), (123, 148)),
)


def edges_recolor_pattern_555(state, only_colors=[], uppercase_paired_edges=False):
    midges_map = {
        "UB": None,
        "UL": None,
        "UR": None,
        "UF": None,
        "LB": None,
        "LF": None,
        "RB": None,
        "RF": None,
        "DB": None,
        "DL": None,
        "DR": None,
        "DF": None,
        "--": None,
    }

    paired_edges_indexes = []

    if uppercase_paired_edges:
        for (s1, s2, s3) in (
            (2, 3, 4),  # Upper
            (6, 11, 16),
            (10, 15, 20),
            (22, 23, 24),
            (31, 36, 41),  # Left
            (35, 40, 45),
            (81, 86, 91),  # Right
            (85, 90, 95),
            (127, 128, 129),  # Down
            (131, 136, 141),
            (135, 140, 145),
            (147, 148, 149),
        ):

            s1_value = state[s1]
            s2_value = state[s2]
            s3_value = state[s3]

            p1 = edges_partner_555[s1]
            p2 = edges_partner_555[s2]
            p3 = edges_partner_555[s3]

            p1_value = state[p1]
            p2_value = state[p2]
            p3_value = state[p3]

            if (
                s1_value != "-"
                and s1_value == s2_value
                and s2_value == s3_value
                and p1_value == p2_value
                and p2_value == p3_value
            ):
                paired_edges_indexes.extend([s1, s2, s3, p1, p2, p3])

    for (edge_index, square_index, partner_index) in midges_recolor_tuples_555:
        square_value = state[square_index]
        partner_value = state[partner_index]

        if square_value == "-" or partner_value == "-":
            pass
        elif square_value == "." and partner_value == ".":
            pass
        else:
            wing_str = wing_str_map[square_value + partner_value]
            midges_map[wing_str] = edge_index

            if only_colors and wing_str not in only_colors:
                state[square_index] = "-"
                state[partner_index] = "-"

            else:
                high_low = highlow_edge_values_555[
                    (square_index, partner_index, square_value, partner_value)
                ]

                # If the edge is paired always use an uppercase letter to represent this edge
                if uppercase_paired_edges and square_index in paired_edges_indexes:
                    state[square_index] = midges_map[wing_str].upper()
                    state[partner_index] = midges_map[wing_str].upper()

                # If this is a high wing use the uppercase of the midge edge_index
                elif high_low == "U":
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

        if square_value == "-" or partner_value == "-":
            pass
        elif square_value == "." and partner_value == ".":
            pass
        else:
            wing_str = wing_str_map[square_value + partner_value]

            if only_colors and wing_str not in only_colors:
                state[square_index] = "-"
                state[partner_index] = "-"

            # If the edge is paired always use an uppercase letter to represent this edge
            elif uppercase_paired_edges and square_index in paired_edges_indexes:
                state[square_index] = midges_map[wing_str].upper()
                state[partner_index] = midges_map[wing_str].upper()

            else:
                high_low = highlow_edge_values_555[
                    (square_index, partner_index, square_value, partner_value)
                ]

                # If this is a high wing use the uppercase of the midge edge_index
                if high_low == "U":
                    state[square_index] = midges_map[wing_str].upper()
                    state[partner_index] = midges_map[wing_str].upper()

                # If this is a low wing use the lowercase of the midge edge_index
                # high_low will be 'D' here
                else:
                    state[square_index] = midges_map[wing_str]
                    state[partner_index] = midges_map[wing_str]

    return "".join(state)


class NoEdgeSolution(Exception):
    pass


class LookupTable555LRTCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step11-LR-centers-stage-t-center-only.txt
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
        133, 137, 139, 143,
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step11-LR-centers-stage-t-center-only.txt",
            "0f0f00",
            linecount=735471,
            max_depth=8,
            filesize=27947898,
            legal_moves=moves_555,
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        state = "".join(["1" if parent_state[x] in ("L", "R") else "0" for x in self.t_centers_555])
        return self.hex_format % int(state, 2)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        binary_state = bin(int(state, 16))[2:].zfill(24)

        for (pos, pos_state) in zip(self.t_centers_555, binary_state):
            if pos_state == "0":
                cube[pos] = "x"
            else:
                cube[pos] = "L"


class LookupTable555LRXCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step12-LR-centers-stage-x-center-only.txt
    ============================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 82 entries (0 percent, 20.50x previous step)
    3 steps has 1,206 entries (0 percent, 14.71x previous step)
    4 steps has 14,116 entries (1 percent, 11.70x previous step)
    5 steps has 123,404 entries (16 percent, 8.74x previous step)
    6 steps has 422,508 entries (57 percent, 3.42x previous step)
    7 steps has 173,254 entries (23 percent, 0.41x previous step)
    8 steps has 896 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    Average: 6.03 moves
    """

    x_centers_555 = (
        7, 9, 17, 19,  # Upper
        32, 34, 42, 44,  # Left
        57, 59, 67, 69,  # Front
        82, 84, 92, 94,  # Right
        107, 109, 117, 119,  # Back
        132, 134, 142, 144,  # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step12-LR-centers-stage-x-center-only.txt",
            "0f0f00",
            linecount=735471,
            max_depth=8,
            filesize=27212427,
            legal_moves=moves_555,
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        state = "".join(["1" if parent_state[x] in ("L", "R") else "0" for x in self.x_centers_555])
        return self.hex_format % int(state, 2)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        binary_state = bin(int(state, 16))[2:].zfill(24)

        for (pos, pos_state) in zip(self.x_centers_555, binary_state):
            if pos_state == "0":
                cube[pos] = "x"
            else:
                cube[pos] = "L"


class LookupTableIDA555LRCenterStage(LookupTableIDAViaGraph):

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=(),
            prune_tables=(
                parent.lt_LR_t_centers_stage,
                parent.lt_LR_x_centers_stage,
            ),
            multiplier=1.2,
        )


class LookupTable555FBTCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step21-FB-t-centers-stage.txt
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

    UFBD_t_centers_555 = (
        8, 12, 14, 18,
        58, 62, 64, 68,
        108, 112, 114, 118,
        133, 137, 139, 143,
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step21-FB-t-centers-stage.txt",
            "0ff0",
            linecount=12870,
            max_depth=9,
            filesize=476190,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        state = "".join(["1" if parent_state[x] in ("F", "B") else "0" for x in self.UFBD_t_centers_555])
        return self.hex_format % int(state, 2)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        binary_state = bin(int(state, 16))[2:].zfill(16)

        for (pos, pos_state) in zip(self.UFBD_t_centers_555, binary_state):
            if pos_state == "0":
                cube[pos] = "x"
            else:
                cube[pos] = "F"


class LookupTable555FBXCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step22-FB-x-centers-stage.txt
    ================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 29 entries (0 percent, 14.50x previous step)
    3 steps has 234 entries (1 percent, 8.07x previous step)
    4 steps has 1,246 entries (9 percent, 5.32x previous step)
    5 steps has 4,466 entries (34 percent, 3.58x previous step)
    6 steps has 6,236 entries (48 percent, 1.40x previous step)
    7 steps has 656 entries (5 percent, 0.11x previous step)

    Total: 12,870 entries
    Average: 5.45 moves
    """

    UFBD_x_centers_555 = (
        7, 9, 17, 19,  # Upper
        57, 59, 67, 69,  # Front
        107, 109, 117, 119,  # Back
        132, 134, 142, 144,  # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step22-FB-x-centers-stage.txt",
            "0ff0",
            linecount=12870,
            max_depth=7,
            filesize=411840,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        state = "".join(["1" if parent_state[x] in ("F", "B") else "0" for x in self.UFBD_x_centers_555])
        return self.hex_format % int(state, 2)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        binary_state = bin(int(state, 16))[2:].zfill(16)

        for (pos, pos_state) in zip(self.UFBD_x_centers_555, binary_state):
            if pos_state == "0":
                cube[pos] = "x"
            else:
                cube[pos] = "F"


class LookupTable555FBCenterStageLRCenter432(LookupTable):
    """
    lookup-table-5x5x5-step23-LR-centers.txt
    ========================================
    0 steps has 72 entries (1 percent, 0.00x previous step)
    1 steps has 756 entries (15 percent, 10.50x previous step)
    2 steps has 1,064 entries (21 percent, 1.41x previous step)
    3 steps has 1,692 entries (34 percent, 1.59x previous step)
    4 steps has 1,220 entries (24 percent, 0.72x previous step)
    5 steps has 96 entries (1 percent, 0.08x previous step)

    Total: 4,900 entries
    Average: 2.72 moves
    """

    LR_centers_555 = (
        32, 33, 34, 37, 38, 39, 42, 43, 44,  # Left
        82, 83, 84, 87, 88, 89, 92, 93, 94,  # Right
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step23-LR-centers.txt',
            'TBD',
            linecount=4900,
            max_depth=5,
            filesize=181300,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_centers_555, state):
            cube[pos] = pos_state


class LookupTableIDA555FBCentersStage(LookupTableIDAViaGraph):

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
            ),

            prune_tables=[
                parent.lt_FB_centers_stage_LR_centers_432,
                parent.lt_FB_t_centers_stage,
                parent.lt_FB_x_centers_stage,
            ],
            perfect_hash_filename="lookup-table-5x5x5-step20-FB-centers-stage.pt-state-perfect-hash",
            pt2_state_max=12870,
        )


class LookupTable555UDCenterSolve(LookupTable):
    """
    lookup-table-5x5x5-step34-UD-centers-solve.txt
    ==============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 22 entries (0 percent, 5.50x previous step)
    3 steps has 82 entries (1 percent, 3.73x previous step)
    4 steps has 292 entries (5 percent, 3.56x previous step)
    5 steps has 986 entries (20 percent, 3.38x previous step)
    6 steps has 2,001 entries (40 percent, 2.03x previous step)
    7 steps has 1,312 entries (26 percent, 0.66x previous step)
    8 steps has 200 entries (4 percent, 0.15x previous step)

    Total: 4,900 entries
    Average: 5.96 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step34-UD-centers-solve.txt',
            'TBD',
            linecount=4900,
            max_depth=8,
            filesize=240100,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        return ''.join([parent_state[x] for x in UD_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(UD_centers_555, state):
            cube[pos] = pos_state


class LookupTable555LRCenterSolve(LookupTable):
    """
    lookup-table-5x5x5-step35-LR-centers-solve.txt
    ==============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 22 entries (0 percent, 5.50x previous step)
    3 steps has 82 entries (1 percent, 3.73x previous step)
    4 steps has 292 entries (5 percent, 3.56x previous step)
    5 steps has 986 entries (20 percent, 3.38x previous step)
    6 steps has 2,001 entries (40 percent, 2.03x previous step)
    7 steps has 1,312 entries (26 percent, 0.66x previous step)
    8 steps has 200 entries (4 percent, 0.15x previous step)

    Total: 4,900 entries
    Average: 5.96 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step35-LR-centers-solve.txt',
            'TBD',
            linecount=4900,
            max_depth=8,
            filesize=240100,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        return ''.join([parent_state[x] for x in LR_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(LR_centers_555, state):
            cube[pos] = pos_state


class LookupTable555FBCenterSolve(LookupTable):
    """
    lookup-table-5x5x5-step36-FB-centers-solve.txt
    ==============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 22 entries (0 percent, 5.50x previous step)
    3 steps has 82 entries (1 percent, 3.73x previous step)
    4 steps has 292 entries (5 percent, 3.56x previous step)
    5 steps has 986 entries (20 percent, 3.38x previous step)
    6 steps has 2,001 entries (40 percent, 2.03x previous step)
    7 steps has 1,312 entries (26 percent, 0.66x previous step)
    8 steps has 200 entries (4 percent, 0.15x previous step)

    Total: 4,900 entries
    Average: 5.96 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step36-FB-centers-solve.txt',
            'TBD',
            linecount=4900,
            max_depth=8,
            filesize=240100,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        return ''.join([parent_state[x] for x in FB_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(FB_centers_555, state):
            cube[pos] = pos_state


class LookupTableIDA555ULFRBDCentersSolve(LookupTableIDAViaGraph):

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
            ),
            prune_tables=(
                parent.lt_UD_centers_solve,
                parent.lt_LR_centers_solve,
                parent.lt_FB_centers_solve,
            ),
            multiplier=1.2,
        )


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
        133, 137, 139, 143,
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step33-ULFRBD-t-centers-solve.txt",
            "UUUULLLLFFFFRRRRBBBBDDDD",
            linecount=343000,
            filesize=19551000,
        )

    def ida_heuristic(self):
        parent_state = self.parent.state
        result = "".join([parent_state[x] for x in self.t_centers_555])
        return (result, 0)


class LookupTable555LRCenterStageEOInnerOrbit(LookupTable):
    """
    LR centers 4900 x EO inner-orbit 2048 = 10,035,200 states

    lookup-table-5x5x5-step901-LR-center-stage-EO-inner-orbit.txt
    =============================================================
    0 steps has 78 entries (0 percent, 0.00x previous step)
    1 steps has 1,218 entries (0 percent, 15.62x previous step)
    2 steps has 13,968 entries (0 percent, 11.47x previous step)
    3 steps has 138,784 entries (1 percent, 9.94x previous step)
    4 steps has 760,136 entries (7 percent, 5.48x previous step)
    5 steps has 2,581,608 entries (25 percent, 3.40x previous step)
    6 steps has 4,277,276 entries (42 percent, 1.66x previous step)
    7 steps has 2,072,720 entries (20 percent, 0.48x previous step)
    8 steps has 186,780 entries (1 percent, 0.09x previous step)
    9 steps has 2,632 entries (0 percent, 0.01x previous step)

    Total: 10,035,200 entries
    Average: 5.79 moves
    """

    state_targets = (
        'UUUUULLLULLLULLLUUUUUURRRURRRURRRUUUUUUUUU',
        'UUUUULLLULLLULRLUUUUUURLRURRRURRRUUUUUUUUU',
        'UUUUULLLULLLULRLUUUUUURRRURRRURLRUUUUUUUUU',
        'UUUUULLLULLLURLRUUUUUULRLURRRURRRUUUUUUUUU',
        'UUUUULLLULLLURLRUUUUUURRRURRRULRLUUUUUUUUU',
        'UUUUULLLULLLURRRUUUUUULLLURRRURRRUUUUUUUUU',
        'UUUUULLLULLLURRRUUUUUULRLURRRURLRUUUUUUUUU',
        'UUUUULLLULLLURRRUUUUUURLRURRRULRLUUUUUUUUU',
        'UUUUULLLULLLURRRUUUUUURRRURRRULLLUUUUUUUUU',
        'UUUUULLLULLRULLLUUUUUURRRULRRURRRUUUUUUUUU',
        'UUUUULLLULLRULLLUUUUUURRRURRLURRRUUUUUUUUU',
        'UUUUULLLULLRULRLUUUUUURLRULRRURRRUUUUUUUUU',
        'UUUUULLLULLRULRLUUUUUURLRURRLURRRUUUUUUUUU',
        'UUUUULLLULLRULRLUUUUUURRRULRRURLRUUUUUUUUU',
        'UUUUULLLULLRULRLUUUUUURRRURRLURLRUUUUUUUUU',
        'UUUUULLLULLRURLRUUUUUULRLULRRURRRUUUUUUUUU',
        'UUUUULLLULLRURLRUUUUUULRLURRLURRRUUUUUUUUU',
        'UUUUULLLULLRURLRUUUUUURRRULRRULRLUUUUUUUUU',
        'UUUUULLLULLRURLRUUUUUURRRURRLULRLUUUUUUUUU',
        'UUUUULLLULLRURRRUUUUUULLLULRRURRRUUUUUUUUU',
        'UUUUULLLULLRURRRUUUUUULLLURRLURRRUUUUUUUUU',
        'UUUUULLLULLRURRRUUUUUULRLULRRURLRUUUUUUUUU',
        'UUUUULLLULLRURRRUUUUUULRLURRLURLRUUUUUUUUU',
        'UUUUULLLULLRURRRUUUUUURLRULRRULRLUUUUUUUUU',
        'UUUUULLLULLRURRRUUUUUURLRURRLULRLUUUUUUUUU',
        'UUUUULLLULLRURRRUUUUUURRRULRRULLLUUUUUUUUU',
        'UUUUULLLULLRURRRUUUUUURRRURRLULLLUUUUUUUUU',
        'UUUUULLLURLLULLLUUUUUURRRULRRURRRUUUUUUUUU',
        'UUUUULLLURLLULLLUUUUUURRRURRLURRRUUUUUUUUU',
        'UUUUULLLURLLULRLUUUUUURLRULRRURRRUUUUUUUUU',
        'UUUUULLLURLLULRLUUUUUURLRURRLURRRUUUUUUUUU',
        'UUUUULLLURLLULRLUUUUUURRRULRRURLRUUUUUUUUU',
        'UUUUULLLURLLULRLUUUUUURRRURRLURLRUUUUUUUUU',
        'UUUUULLLURLLURLRUUUUUULRLULRRURRRUUUUUUUUU',
        'UUUUULLLURLLURLRUUUUUULRLURRLURRRUUUUUUUUU',
        'UUUUULLLURLLURLRUUUUUURRRULRRULRLUUUUUUUUU',
        'UUUUULLLURLLURLRUUUUUURRRURRLULRLUUUUUUUUU',
        'UUUUULLLURLLURRRUUUUUULLLULRRURRRUUUUUUUUU',
        'UUUUULLLURLLURRRUUUUUULLLURRLURRRUUUUUUUUU',
        'UUUUULLLURLLURRRUUUUUULRLULRRURLRUUUUUUUUU',
        'UUUUULLLURLLURRRUUUUUULRLURRLURLRUUUUUUUUU',
        'UUUUULLLURLLURRRUUUUUURLRULRRULRLUUUUUUUUU',
        'UUUUULLLURLLURRRUUUUUURLRURRLULRLUUUUUUUUU',
        'UUUUULLLURLLURRRUUUUUURRRULRRULLLUUUUUUUUU',
        'UUUUULLLURLLURRRUUUUUURRRURRLULLLUUUUUUUUU',
        'UUUUULLLURLRULLLUUUUUURRRULRLURRRUUUUUUUUU',
        'UUUUULLLURLRULRLUUUUUURLRULRLURRRUUUUUUUUU',
        'UUUUULLLURLRULRLUUUUUURRRULRLURLRUUUUUUUUU',
        'UUUUULLLURLRURLRUUUUUULRLULRLURRRUUUUUUUUU',
        'UUUUULLLURLRURLRUUUUUURRRULRLULRLUUUUUUUUU',
        'UUUUULLLURLRURRRUUUUUULLLULRLURRRUUUUUUUUU',
        'UUUUULLLURLRURRRUUUUUULRLULRLURLRUUUUUUUUU',
        'UUUUULLLURLRURRRUUUUUURLRULRLULRLUUUUUUUUU',
        'UUUUULLLURLRURRRUUUUUURRRULRLULLLUUUUUUUUU',
        'UUUUULLRULLLULLRUUUUUULRRURRRULRRUUUUUUUUU',
        'UUUUULLRULLLULLRUUUUUURRLURRRURRLUUUUUUUUU',
        'UUUUULLRULLLULRRUUUUUULLRURRRULRRUUUUUUUUU',
        'UUUUULLRULLLULRRUUUUUULRRURRRULLRUUUUUUUUU',
        'UUUUULLRULLLULRRUUUUUURLLURRRURRLUUUUUUUUU',
        'UUUUULLRULLLULRRUUUUUURRLURRRURLLUUUUUUUUU',
        'UUUUULLRULLLURLLUUUUUURRLURRRULRRUUUUUUUUU',
        'UUUUULLRULLLURRLUUUUUURLLURRRULRRUUUUUUUUU',
        'UUUUULLRULLLURRLUUUUUURRLURRRULLRUUUUUUUUU',
        'UUUUULLRULLRULLRUUUUUULRRULRRULRRUUUUUUUUU',
        'UUUUULLRULLRULLRUUUUUULRRURRLULRRUUUUUUUUU',
        'UUUUULLRULLRULLRUUUUUURRLULRRURRLUUUUUUUUU',
        'UUUUULLRULLRULLRUUUUUURRLURRLURRLUUUUUUUUU',
        'UUUUULLRULLRULRRUUUUUULLRULRRULRRUUUUUUUUU',
        'UUUUULLRULLRULRRUUUUUULLRURRLULRRUUUUUUUUU',
        'UUUUULLRULLRULRRUUUUUULRRULRRULLRUUUUUUUUU',
        'UUUUULLRULLRULRRUUUUUULRRURRLULLRUUUUUUUUU',
        'UUUUULLRULLRULRRUUUUUURLLULRRURRLUUUUUUUUU',
        'UUUUULLRULLRULRRUUUUUURLLURRLURRLUUUUUUUUU',
        'UUUUULLRULLRULRRUUUUUURRLULRRURLLUUUUUUUUU',
        'UUUUULLRULLRULRRUUUUUURRLURRLURLLUUUUUUUUU',
        'UUUUULLRULLRURLLUUUUUURRLULRRULRRUUUUUUUUU',
        'UUUUULLRULLRURLLUUUUUURRLURRLULRRUUUUUUUUU',
        'UUUUULLRULLRURRLUUUUUURLLULRRULRRUUUUUUUUU',
        'UUUUULLRULLRURRLUUUUUURLLURRLULRRUUUUUUUUU',
        'UUUUULLRULLRURRLUUUUUURRLULRRULLRUUUUUUUUU',
        'UUUUULLRULLRURRLUUUUUURRLURRLULLRUUUUUUUUU',
        'UUUUULLRURLLULLRUUUUUULRRULRRULRRUUUUUUUUU',
        'UUUUULLRURLLULLRUUUUUULRRURRLULRRUUUUUUUUU',
        'UUUUULLRURLLULLRUUUUUURRLULRRURRLUUUUUUUUU',
        'UUUUULLRURLLULLRUUUUUURRLURRLURRLUUUUUUUUU',
        'UUUUULLRURLLULRRUUUUUULLRULRRULRRUUUUUUUUU',
        'UUUUULLRURLLULRRUUUUUULLRURRLULRRUUUUUUUUU',
        'UUUUULLRURLLULRRUUUUUULRRULRRULLRUUUUUUUUU',
        'UUUUULLRURLLULRRUUUUUULRRURRLULLRUUUUUUUUU',
        'UUUUULLRURLLULRRUUUUUURLLULRRURRLUUUUUUUUU',
        'UUUUULLRURLLULRRUUUUUURLLURRLURRLUUUUUUUUU',
        'UUUUULLRURLLULRRUUUUUURRLULRRURLLUUUUUUUUU',
        'UUUUULLRURLLULRRUUUUUURRLURRLURLLUUUUUUUUU',
        'UUUUULLRURLLURLLUUUUUURRLULRRULRRUUUUUUUUU',
        'UUUUULLRURLLURLLUUUUUURRLURRLULRRUUUUUUUUU',
        'UUUUULLRURLLURRLUUUUUURLLULRRULRRUUUUUUUUU',
        'UUUUULLRURLLURRLUUUUUURLLURRLULRRUUUUUUUUU',
        'UUUUULLRURLLURRLUUUUUURRLULRRULLRUUUUUUUUU',
        'UUUUULLRURLLURRLUUUUUURRLURRLULLRUUUUUUUUU',
        'UUUUULLRURLRULLRUUUUUULRRULRLULRRUUUUUUUUU',
        'UUUUULLRURLRULLRUUUUUURRLULRLURRLUUUUUUUUU',
        'UUUUULLRURLRULRRUUUUUULLRULRLULRRUUUUUUUUU',
        'UUUUULLRURLRULRRUUUUUULRRULRLULLRUUUUUUUUU',
        'UUUUULLRURLRULRRUUUUUURLLULRLURRLUUUUUUUUU',
        'UUUUULLRURLRULRRUUUUUURRLULRLURLLUUUUUUUUU',
        'UUUUULLRURLRURLLUUUUUURRLULRLULRRUUUUUUUUU',
        'UUUUULLRURLRURRLUUUUUURLLULRLULRRUUUUUUUUU',
        'UUUUULLRURLRURRLUUUUUURRLULRLULLRUUUUUUUUU',
        'UUUUULRLULLLULLLUUUUUURLRURRRURRRUUUUUUUUU',
        'UUUUULRLULLLULLLUUUUUURRRURRRURLRUUUUUUUUU',
        'UUUUULRLULLLULRLUUUUUURLRURRRURLRUUUUUUUUU',
        'UUUUULRLULLLURLRUUUUUULLLURRRURRRUUUUUUUUU',
        'UUUUULRLULLLURLRUUUUUULRLURRRURLRUUUUUUUUU',
        'UUUUULRLULLLURLRUUUUUURLRURRRULRLUUUUUUUUU',
        'UUUUULRLULLLURLRUUUUUURRRURRRULLLUUUUUUUUU',
        'UUUUULRLULLLURRRUUUUUULLLURRRURLRUUUUUUUUU',
        'UUUUULRLULLLURRRUUUUUURLRURRRULLLUUUUUUUUU',
        'UUUUULRLULLRULLLUUUUUURLRULRRURRRUUUUUUUUU',
        'UUUUULRLULLRULLLUUUUUURLRURRLURRRUUUUUUUUU',
        'UUUUULRLULLRULLLUUUUUURRRULRRURLRUUUUUUUUU',
        'UUUUULRLULLRULLLUUUUUURRRURRLURLRUUUUUUUUU',
        'UUUUULRLULLRULRLUUUUUURLRULRRURLRUUUUUUUUU',
        'UUUUULRLULLRULRLUUUUUURLRURRLURLRUUUUUUUUU',
        'UUUUULRLULLRURLRUUUUUULLLULRRURRRUUUUUUUUU',
        'UUUUULRLULLRURLRUUUUUULLLURRLURRRUUUUUUUUU',
        'UUUUULRLULLRURLRUUUUUULRLULRRURLRUUUUUUUUU',
        'UUUUULRLULLRURLRUUUUUULRLURRLURLRUUUUUUUUU',
        'UUUUULRLULLRURLRUUUUUURLRULRRULRLUUUUUUUUU',
        'UUUUULRLULLRURLRUUUUUURLRURRLULRLUUUUUUUUU',
        'UUUUULRLULLRURLRUUUUUURRRULRRULLLUUUUUUUUU',
        'UUUUULRLULLRURLRUUUUUURRRURRLULLLUUUUUUUUU',
        'UUUUULRLULLRURRRUUUUUULLLULRRURLRUUUUUUUUU',
        'UUUUULRLULLRURRRUUUUUULLLURRLURLRUUUUUUUUU',
        'UUUUULRLULLRURRRUUUUUURLRULRRULLLUUUUUUUUU',
        'UUUUULRLULLRURRRUUUUUURLRURRLULLLUUUUUUUUU',
        'UUUUULRLURLLULLLUUUUUURLRULRRURRRUUUUUUUUU',
        'UUUUULRLURLLULLLUUUUUURLRURRLURRRUUUUUUUUU',
        'UUUUULRLURLLULLLUUUUUURRRULRRURLRUUUUUUUUU',
        'UUUUULRLURLLULLLUUUUUURRRURRLURLRUUUUUUUUU',
        'UUUUULRLURLLULRLUUUUUURLRULRRURLRUUUUUUUUU',
        'UUUUULRLURLLULRLUUUUUURLRURRLURLRUUUUUUUUU',
        'UUUUULRLURLLURLRUUUUUULLLULRRURRRUUUUUUUUU',
        'UUUUULRLURLLURLRUUUUUULLLURRLURRRUUUUUUUUU',
        'UUUUULRLURLLURLRUUUUUULRLULRRURLRUUUUUUUUU',
        'UUUUULRLURLLURLRUUUUUULRLURRLURLRUUUUUUUUU',
        'UUUUULRLURLLURLRUUUUUURLRULRRULRLUUUUUUUUU',
        'UUUUULRLURLLURLRUUUUUURLRURRLULRLUUUUUUUUU',
        'UUUUULRLURLLURLRUUUUUURRRULRRULLLUUUUUUUUU',
        'UUUUULRLURLLURLRUUUUUURRRURRLULLLUUUUUUUUU',
        'UUUUULRLURLLURRRUUUUUULLLULRRURLRUUUUUUUUU',
        'UUUUULRLURLLURRRUUUUUULLLURRLURLRUUUUUUUUU',
        'UUUUULRLURLLURRRUUUUUURLRULRRULLLUUUUUUUUU',
        'UUUUULRLURLLURRRUUUUUURLRURRLULLLUUUUUUUUU',
        'UUUUULRLURLRULLLUUUUUURLRULRLURRRUUUUUUUUU',
        'UUUUULRLURLRULLLUUUUUURRRULRLURLRUUUUUUUUU',
        'UUUUULRLURLRULRLUUUUUURLRULRLURLRUUUUUUUUU',
        'UUUUULRLURLRURLRUUUUUULLLULRLURRRUUUUUUUUU',
        'UUUUULRLURLRURLRUUUUUULRLULRLURLRUUUUUUUUU',
        'UUUUULRLURLRURLRUUUUUURLRULRLULRLUUUUUUUUU',
        'UUUUULRLURLRURLRUUUUUURRRULRLULLLUUUUUUUUU',
        'UUUUULRLURLRURRRUUUUUULLLULRLURLRUUUUUUUUU',
        'UUUUULRLURLRURRRUUUUUURLRULRLULLLUUUUUUUUU',
        'UUUUULRRULLLULLRUUUUUULLRURRRULRRUUUUUUUUU',
        'UUUUULRRULLLULLRUUUUUULRRURRRULLRUUUUUUUUU',
        'UUUUULRRULLLULLRUUUUUURLLURRRURRLUUUUUUUUU',
        'UUUUULRRULLLULLRUUUUUURRLURRRURLLUUUUUUUUU',
        'UUUUULRRULLLULRRUUUUUULLRURRRULLRUUUUUUUUU',
        'UUUUULRRULLLULRRUUUUUURLLURRRURLLUUUUUUUUU',
        'UUUUULRRULLLURLLUUUUUURLLURRRULRRUUUUUUUUU',
        'UUUUULRRULLLURLLUUUUUURRLURRRULLRUUUUUUUUU',
        'UUUUULRRULLLURRLUUUUUURLLURRRULLRUUUUUUUUU',
        'UUUUULRRULLRULLRUUUUUULLRULRRULRRUUUUUUUUU',
        'UUUUULRRULLRULLRUUUUUULLRURRLULRRUUUUUUUUU',
        'UUUUULRRULLRULLRUUUUUULRRULRRULLRUUUUUUUUU',
        'UUUUULRRULLRULLRUUUUUULRRURRLULLRUUUUUUUUU',
        'UUUUULRRULLRULLRUUUUUURLLULRRURRLUUUUUUUUU',
        'UUUUULRRULLRULLRUUUUUURLLURRLURRLUUUUUUUUU',
        'UUUUULRRULLRULLRUUUUUURRLULRRURLLUUUUUUUUU',
        'UUUUULRRULLRULLRUUUUUURRLURRLURLLUUUUUUUUU',
        'UUUUULRRULLRULRRUUUUUULLRULRRULLRUUUUUUUUU',
        'UUUUULRRULLRULRRUUUUUULLRURRLULLRUUUUUUUUU',
        'UUUUULRRULLRULRRUUUUUURLLULRRURLLUUUUUUUUU',
        'UUUUULRRULLRULRRUUUUUURLLURRLURLLUUUUUUUUU',
        'UUUUULRRULLRURLLUUUUUURLLULRRULRRUUUUUUUUU',
        'UUUUULRRULLRURLLUUUUUURLLURRLULRRUUUUUUUUU',
        'UUUUULRRULLRURLLUUUUUURRLULRRULLRUUUUUUUUU',
        'UUUUULRRULLRURLLUUUUUURRLURRLULLRUUUUUUUUU',
        'UUUUULRRULLRURRLUUUUUURLLULRRULLRUUUUUUUUU',
        'UUUUULRRULLRURRLUUUUUURLLURRLULLRUUUUUUUUU',
        'UUUUULRRURLLULLRUUUUUULLRULRRULRRUUUUUUUUU',
        'UUUUULRRURLLULLRUUUUUULLRURRLULRRUUUUUUUUU',
        'UUUUULRRURLLULLRUUUUUULRRULRRULLRUUUUUUUUU',
        'UUUUULRRURLLULLRUUUUUULRRURRLULLRUUUUUUUUU',
        'UUUUULRRURLLULLRUUUUUURLLULRRURRLUUUUUUUUU',
        'UUUUULRRURLLULLRUUUUUURLLURRLURRLUUUUUUUUU',
        'UUUUULRRURLLULLRUUUUUURRLULRRURLLUUUUUUUUU',
        'UUUUULRRURLLULLRUUUUUURRLURRLURLLUUUUUUUUU',
        'UUUUULRRURLLULRRUUUUUULLRULRRULLRUUUUUUUUU',
        'UUUUULRRURLLULRRUUUUUULLRURRLULLRUUUUUUUUU',
        'UUUUULRRURLLULRRUUUUUURLLULRRURLLUUUUUUUUU',
        'UUUUULRRURLLULRRUUUUUURLLURRLURLLUUUUUUUUU',
        'UUUUULRRURLLURLLUUUUUURLLULRRULRRUUUUUUUUU',
        'UUUUULRRURLLURLLUUUUUURLLURRLULRRUUUUUUUUU',
        'UUUUULRRURLLURLLUUUUUURRLULRRULLRUUUUUUUUU',
        'UUUUULRRURLLURLLUUUUUURRLURRLULLRUUUUUUUUU',
        'UUUUULRRURLLURRLUUUUUURLLULRRULLRUUUUUUUUU',
        'UUUUULRRURLLURRLUUUUUURLLURRLULLRUUUUUUUUU',
        'UUUUULRRURLRULLRUUUUUULLRULRLULRRUUUUUUUUU',
        'UUUUULRRURLRULLRUUUUUULRRULRLULLRUUUUUUUUU',
        'UUUUULRRURLRULLRUUUUUURLLULRLURRLUUUUUUUUU',
        'UUUUULRRURLRULLRUUUUUURRLULRLURLLUUUUUUUUU',
        'UUUUULRRURLRULRRUUUUUULLRULRLULLRUUUUUUUUU',
        'UUUUULRRURLRULRRUUUUUURLLULRLURLLUUUUUUUUU',
        'UUUUULRRURLRURLLUUUUUURLLULRLULRRUUUUUUUUU',
        'UUUUULRRURLRURLLUUUUUURRLULRLULLRUUUUUUUUU',
        'UUUUULRRURLRURRLUUUUUURLLULRLULLRUUUUUUUUU',
        'UUUUURLLULLLULLRUUUUUULRRURRRURRLUUUUUUUUU',
        'UUUUURLLULLLULRRUUUUUULLRURRRURRLUUUUUUUUU',
        'UUUUURLLULLLULRRUUUUUULRRURRRURLLUUUUUUUUU',
        'UUUUURLLULLLURLLUUUUUULRRURRRULRRUUUUUUUUU',
        'UUUUURLLULLLURLLUUUUUURRLURRRURRLUUUUUUUUU',
        'UUUUURLLULLLURRLUUUUUULLRURRRULRRUUUUUUUUU',
        'UUUUURLLULLLURRLUUUUUULRRURRRULLRUUUUUUUUU',
        'UUUUURLLULLLURRLUUUUUURLLURRRURRLUUUUUUUUU',
        'UUUUURLLULLLURRLUUUUUURRLURRRURLLUUUUUUUUU',
        'UUUUURLLULLRULLRUUUUUULRRULRRURRLUUUUUUUUU',
        'UUUUURLLULLRULLRUUUUUULRRURRLURRLUUUUUUUUU',
        'UUUUURLLULLRULRRUUUUUULLRULRRURRLUUUUUUUUU',
        'UUUUURLLULLRULRRUUUUUULLRURRLURRLUUUUUUUUU',
        'UUUUURLLULLRULRRUUUUUULRRULRRURLLUUUUUUUUU',
        'UUUUURLLULLRULRRUUUUUULRRURRLURLLUUUUUUUUU',
        'UUUUURLLULLRURLLUUUUUULRRULRRULRRUUUUUUUUU',
        'UUUUURLLULLRURLLUUUUUULRRURRLULRRUUUUUUUUU',
        'UUUUURLLULLRURLLUUUUUURRLULRRURRLUUUUUUUUU',
        'UUUUURLLULLRURLLUUUUUURRLURRLURRLUUUUUUUUU',
        'UUUUURLLULLRURRLUUUUUULLRULRRULRRUUUUUUUUU',
        'UUUUURLLULLRURRLUUUUUULLRURRLULRRUUUUUUUUU',
        'UUUUURLLULLRURRLUUUUUULRRULRRULLRUUUUUUUUU',
        'UUUUURLLULLRURRLUUUUUULRRURRLULLRUUUUUUUUU',
        'UUUUURLLULLRURRLUUUUUURLLULRRURRLUUUUUUUUU',
        'UUUUURLLULLRURRLUUUUUURLLURRLURRLUUUUUUUUU',
        'UUUUURLLULLRURRLUUUUUURRLULRRURLLUUUUUUUUU',
        'UUUUURLLULLRURRLUUUUUURRLURRLURLLUUUUUUUUU',
        'UUUUURLLURLLULLRUUUUUULRRULRRURRLUUUUUUUUU',
        'UUUUURLLURLLULLRUUUUUULRRURRLURRLUUUUUUUUU',
        'UUUUURLLURLLULRRUUUUUULLRULRRURRLUUUUUUUUU',
        'UUUUURLLURLLULRRUUUUUULLRURRLURRLUUUUUUUUU',
        'UUUUURLLURLLULRRUUUUUULRRULRRURLLUUUUUUUUU',
        'UUUUURLLURLLULRRUUUUUULRRURRLURLLUUUUUUUUU',
        'UUUUURLLURLLURLLUUUUUULRRULRRULRRUUUUUUUUU',
        'UUUUURLLURLLURLLUUUUUULRRURRLULRRUUUUUUUUU',
        'UUUUURLLURLLURLLUUUUUURRLULRRURRLUUUUUUUUU',
        'UUUUURLLURLLURLLUUUUUURRLURRLURRLUUUUUUUUU',
        'UUUUURLLURLLURRLUUUUUULLRULRRULRRUUUUUUUUU',
        'UUUUURLLURLLURRLUUUUUULLRURRLULRRUUUUUUUUU',
        'UUUUURLLURLLURRLUUUUUULRRULRRULLRUUUUUUUUU',
        'UUUUURLLURLLURRLUUUUUULRRURRLULLRUUUUUUUUU',
        'UUUUURLLURLLURRLUUUUUURLLULRRURRLUUUUUUUUU',
        'UUUUURLLURLLURRLUUUUUURLLURRLURRLUUUUUUUUU',
        'UUUUURLLURLLURRLUUUUUURRLULRRURLLUUUUUUUUU',
        'UUUUURLLURLLURRLUUUUUURRLURRLURLLUUUUUUUUU',
        'UUUUURLLURLRULLRUUUUUULRRULRLURRLUUUUUUUUU',
        'UUUUURLLURLRULRRUUUUUULLRULRLURRLUUUUUUUUU',
        'UUUUURLLURLRULRRUUUUUULRRULRLURLLUUUUUUUUU',
        'UUUUURLLURLRURLLUUUUUULRRULRLULRRUUUUUUUUU',
        'UUUUURLLURLRURLLUUUUUURRLULRLURRLUUUUUUUUU',
        'UUUUURLLURLRURRLUUUUUULLRULRLULRRUUUUUUUUU',
        'UUUUURLLURLRURRLUUUUUULRRULRLULLRUUUUUUUUU',
        'UUUUURLLURLRURRLUUUUUURLLULRLURRLUUUUUUUUU',
        'UUUUURLLURLRURRLUUUUUURRLULRLURLLUUUUUUUUU',
        'UUUUURLRULLLULLLUUUUUULRLURRRURRRUUUUUUUUU',
        'UUUUURLRULLLULLLUUUUUURRRURRRULRLUUUUUUUUU',
        'UUUUURLRULLLULRLUUUUUULLLURRRURRRUUUUUUUUU',
        'UUUUURLRULLLULRLUUUUUULRLURRRURLRUUUUUUUUU',
        'UUUUURLRULLLULRLUUUUUURLRURRRULRLUUUUUUUUU',
        'UUUUURLRULLLULRLUUUUUURRRURRRULLLUUUUUUUUU',
        'UUUUURLRULLLURLRUUUUUULRLURRRULRLUUUUUUUUU',
        'UUUUURLRULLLURRRUUUUUULLLURRRULRLUUUUUUUUU',
        'UUUUURLRULLLURRRUUUUUULRLURRRULLLUUUUUUUUU',
        'UUUUURLRULLRULLLUUUUUULRLULRRURRRUUUUUUUUU',
        'UUUUURLRULLRULLLUUUUUULRLURRLURRRUUUUUUUUU',
        'UUUUURLRULLRULLLUUUUUURRRULRRULRLUUUUUUUUU',
        'UUUUURLRULLRULLLUUUUUURRRURRLULRLUUUUUUUUU',
        'UUUUURLRULLRULRLUUUUUULLLULRRURRRUUUUUUUUU',
        'UUUUURLRULLRULRLUUUUUULLLURRLURRRUUUUUUUUU',
        'UUUUURLRULLRULRLUUUUUULRLULRRURLRUUUUUUUUU',
        'UUUUURLRULLRULRLUUUUUULRLURRLURLRUUUUUUUUU',
        'UUUUURLRULLRULRLUUUUUURLRULRRULRLUUUUUUUUU',
        'UUUUURLRULLRULRLUUUUUURLRURRLULRLUUUUUUUUU',
        'UUUUURLRULLRULRLUUUUUURRRULRRULLLUUUUUUUUU',
        'UUUUURLRULLRULRLUUUUUURRRURRLULLLUUUUUUUUU',
        'UUUUURLRULLRURLRUUUUUULRLULRRULRLUUUUUUUUU',
        'UUUUURLRULLRURLRUUUUUULRLURRLULRLUUUUUUUUU',
        'UUUUURLRULLRURRRUUUUUULLLULRRULRLUUUUUUUUU',
        'UUUUURLRULLRURRRUUUUUULLLURRLULRLUUUUUUUUU',
        'UUUUURLRULLRURRRUUUUUULRLULRRULLLUUUUUUUUU',
        'UUUUURLRULLRURRRUUUUUULRLURRLULLLUUUUUUUUU',
        'UUUUURLRURLLULLLUUUUUULRLULRRURRRUUUUUUUUU',
        'UUUUURLRURLLULLLUUUUUULRLURRLURRRUUUUUUUUU',
        'UUUUURLRURLLULLLUUUUUURRRULRRULRLUUUUUUUUU',
        'UUUUURLRURLLULLLUUUUUURRRURRLULRLUUUUUUUUU',
        'UUUUURLRURLLULRLUUUUUULLLULRRURRRUUUUUUUUU',
        'UUUUURLRURLLULRLUUUUUULLLURRLURRRUUUUUUUUU',
        'UUUUURLRURLLULRLUUUUUULRLULRRURLRUUUUUUUUU',
        'UUUUURLRURLLULRLUUUUUULRLURRLURLRUUUUUUUUU',
        'UUUUURLRURLLULRLUUUUUURLRULRRULRLUUUUUUUUU',
        'UUUUURLRURLLULRLUUUUUURLRURRLULRLUUUUUUUUU',
        'UUUUURLRURLLULRLUUUUUURRRULRRULLLUUUUUUUUU',
        'UUUUURLRURLLULRLUUUUUURRRURRLULLLUUUUUUUUU',
        'UUUUURLRURLLURLRUUUUUULRLULRRULRLUUUUUUUUU',
        'UUUUURLRURLLURLRUUUUUULRLURRLULRLUUUUUUUUU',
        'UUUUURLRURLLURRRUUUUUULLLULRRULRLUUUUUUUUU',
        'UUUUURLRURLLURRRUUUUUULLLURRLULRLUUUUUUUUU',
        'UUUUURLRURLLURRRUUUUUULRLULRRULLLUUUUUUUUU',
        'UUUUURLRURLLURRRUUUUUULRLURRLULLLUUUUUUUUU',
        'UUUUURLRURLRULLLUUUUUULRLULRLURRRUUUUUUUUU',
        'UUUUURLRURLRULLLUUUUUURRRULRLULRLUUUUUUUUU',
        'UUUUURLRURLRULRLUUUUUULLLULRLURRRUUUUUUUUU',
        'UUUUURLRURLRULRLUUUUUULRLULRLURLRUUUUUUUUU',
        'UUUUURLRURLRULRLUUUUUURLRULRLULRLUUUUUUUUU',
        'UUUUURLRURLRULRLUUUUUURRRULRLULLLUUUUUUUUU',
        'UUUUURLRURLRURLRUUUUUULRLULRLULRLUUUUUUUUU',
        'UUUUURLRURLRURRRUUUUUULLLULRLULRLUUUUUUUUU',
        'UUUUURLRURLRURRRUUUUUULRLULRLULLLUUUUUUUUU',
        'UUUUURRLULLLULLRUUUUUULLRURRRURRLUUUUUUUUU',
        'UUUUURRLULLLULLRUUUUUULRRURRRURLLUUUUUUUUU',
        'UUUUURRLULLLULRRUUUUUULLRURRRURLLUUUUUUUUU',
        'UUUUURRLULLLURLLUUUUUULLRURRRULRRUUUUUUUUU',
        'UUUUURRLULLLURLLUUUUUULRRURRRULLRUUUUUUUUU',
        'UUUUURRLULLLURLLUUUUUURLLURRRURRLUUUUUUUUU',
        'UUUUURRLULLLURLLUUUUUURRLURRRURLLUUUUUUUUU',
        'UUUUURRLULLLURRLUUUUUULLRURRRULLRUUUUUUUUU',
        'UUUUURRLULLLURRLUUUUUURLLURRRURLLUUUUUUUUU',
        'UUUUURRLULLRULLRUUUUUULLRULRRURRLUUUUUUUUU',
        'UUUUURRLULLRULLRUUUUUULLRURRLURRLUUUUUUUUU',
        'UUUUURRLULLRULLRUUUUUULRRULRRURLLUUUUUUUUU',
        'UUUUURRLULLRULLRUUUUUULRRURRLURLLUUUUUUUUU',
        'UUUUURRLULLRULRRUUUUUULLRULRRURLLUUUUUUUUU',
        'UUUUURRLULLRULRRUUUUUULLRURRLURLLUUUUUUUUU',
        'UUUUURRLULLRURLLUUUUUULLRULRRULRRUUUUUUUUU',
        'UUUUURRLULLRURLLUUUUUULLRURRLULRRUUUUUUUUU',
        'UUUUURRLULLRURLLUUUUUULRRULRRULLRUUUUUUUUU',
        'UUUUURRLULLRURLLUUUUUULRRURRLULLRUUUUUUUUU',
        'UUUUURRLULLRURLLUUUUUURLLULRRURRLUUUUUUUUU',
        'UUUUURRLULLRURLLUUUUUURLLURRLURRLUUUUUUUUU',
        'UUUUURRLULLRURLLUUUUUURRLULRRURLLUUUUUUUUU',
        'UUUUURRLULLRURLLUUUUUURRLURRLURLLUUUUUUUUU',
        'UUUUURRLULLRURRLUUUUUULLRULRRULLRUUUUUUUUU',
        'UUUUURRLULLRURRLUUUUUULLRURRLULLRUUUUUUUUU',
        'UUUUURRLULLRURRLUUUUUURLLULRRURLLUUUUUUUUU',
        'UUUUURRLULLRURRLUUUUUURLLURRLURLLUUUUUUUUU',
        'UUUUURRLURLLULLRUUUUUULLRULRRURRLUUUUUUUUU',
        'UUUUURRLURLLULLRUUUUUULLRURRLURRLUUUUUUUUU',
        'UUUUURRLURLLULLRUUUUUULRRULRRURLLUUUUUUUUU',
        'UUUUURRLURLLULLRUUUUUULRRURRLURLLUUUUUUUUU',
        'UUUUURRLURLLULRRUUUUUULLRULRRURLLUUUUUUUUU',
        'UUUUURRLURLLULRRUUUUUULLRURRLURLLUUUUUUUUU',
        'UUUUURRLURLLURLLUUUUUULLRULRRULRRUUUUUUUUU',
        'UUUUURRLURLLURLLUUUUUULLRURRLULRRUUUUUUUUU',
        'UUUUURRLURLLURLLUUUUUULRRULRRULLRUUUUUUUUU',
        'UUUUURRLURLLURLLUUUUUULRRURRLULLRUUUUUUUUU',
        'UUUUURRLURLLURLLUUUUUURLLULRRURRLUUUUUUUUU',
        'UUUUURRLURLLURLLUUUUUURLLURRLURRLUUUUUUUUU',
        'UUUUURRLURLLURLLUUUUUURRLULRRURLLUUUUUUUUU',
        'UUUUURRLURLLURLLUUUUUURRLURRLURLLUUUUUUUUU',
        'UUUUURRLURLLURRLUUUUUULLRULRRULLRUUUUUUUUU',
        'UUUUURRLURLLURRLUUUUUULLRURRLULLRUUUUUUUUU',
        'UUUUURRLURLLURRLUUUUUURLLULRRURLLUUUUUUUUU',
        'UUUUURRLURLLURRLUUUUUURLLURRLURLLUUUUUUUUU',
        'UUUUURRLURLRULLRUUUUUULLRULRLURRLUUUUUUUUU',
        'UUUUURRLURLRULLRUUUUUULRRULRLURLLUUUUUUUUU',
        'UUUUURRLURLRULRRUUUUUULLRULRLURLLUUUUUUUUU',
        'UUUUURRLURLRURLLUUUUUULLRULRLULRRUUUUUUUUU',
        'UUUUURRLURLRURLLUUUUUULRRULRLULLRUUUUUUUUU',
        'UUUUURRLURLRURLLUUUUUURLLULRLURRLUUUUUUUUU',
        'UUUUURRLURLRURLLUUUUUURRLULRLURLLUUUUUUUUU',
        'UUUUURRLURLRURRLUUUUUULLRULRLULLRUUUUUUUUU',
        'UUUUURRLURLRURRLUUUUUURLLULRLURLLUUUUUUUUU',
        'UUUUURRRULLLULLLUUUUUULLLURRRURRRUUUUUUUUU',
        'UUUUURRRULLLULLLUUUUUULRLURRRURLRUUUUUUUUU',
        'UUUUURRRULLLULLLUUUUUURLRURRRULRLUUUUUUUUU',
        'UUUUURRRULLLULLLUUUUUURRRURRRULLLUUUUUUUUU',
        'UUUUURRRULLLULRLUUUUUULLLURRRURLRUUUUUUUUU',
        'UUUUURRRULLLULRLUUUUUURLRURRRULLLUUUUUUUUU',
        'UUUUURRRULLLURLRUUUUUULLLURRRULRLUUUUUUUUU',
        'UUUUURRRULLLURLRUUUUUULRLURRRULLLUUUUUUUUU',
        'UUUUURRRULLLURRRUUUUUULLLURRRULLLUUUUUUUUU',
        'UUUUURRRULLRULLLUUUUUULLLULRRURRRUUUUUUUUU',
        'UUUUURRRULLRULLLUUUUUULLLURRLURRRUUUUUUUUU',
        'UUUUURRRULLRULLLUUUUUULRLULRRURLRUUUUUUUUU',
        'UUUUURRRULLRULLLUUUUUULRLURRLURLRUUUUUUUUU',
        'UUUUURRRULLRULLLUUUUUURLRULRRULRLUUUUUUUUU',
        'UUUUURRRULLRULLLUUUUUURLRURRLULRLUUUUUUUUU',
        'UUUUURRRULLRULLLUUUUUURRRULRRULLLUUUUUUUUU',
        'UUUUURRRULLRULLLUUUUUURRRURRLULLLUUUUUUUUU',
        'UUUUURRRULLRULRLUUUUUULLLULRRURLRUUUUUUUUU',
        'UUUUURRRULLRULRLUUUUUULLLURRLURLRUUUUUUUUU',
        'UUUUURRRULLRULRLUUUUUURLRULRRULLLUUUUUUUUU',
        'UUUUURRRULLRULRLUUUUUURLRURRLULLLUUUUUUUUU',
        'UUUUURRRULLRURLRUUUUUULLLULRRULRLUUUUUUUUU',
        'UUUUURRRULLRURLRUUUUUULLLURRLULRLUUUUUUUUU',
        'UUUUURRRULLRURLRUUUUUULRLULRRULLLUUUUUUUUU',
        'UUUUURRRULLRURLRUUUUUULRLURRLULLLUUUUUUUUU',
        'UUUUURRRULLRURRRUUUUUULLLULRRULLLUUUUUUUUU',
        'UUUUURRRULLRURRRUUUUUULLLURRLULLLUUUUUUUUU',
        'UUUUURRRURLLULLLUUUUUULLLULRRURRRUUUUUUUUU',
        'UUUUURRRURLLULLLUUUUUULLLURRLURRRUUUUUUUUU',
        'UUUUURRRURLLULLLUUUUUULRLULRRURLRUUUUUUUUU',
        'UUUUURRRURLLULLLUUUUUULRLURRLURLRUUUUUUUUU',
        'UUUUURRRURLLULLLUUUUUURLRULRRULRLUUUUUUUUU',
        'UUUUURRRURLLULLLUUUUUURLRURRLULRLUUUUUUUUU',
        'UUUUURRRURLLULLLUUUUUURRRULRRULLLUUUUUUUUU',
        'UUUUURRRURLLULLLUUUUUURRRURRLULLLUUUUUUUUU',
        'UUUUURRRURLLULRLUUUUUULLLULRRURLRUUUUUUUUU',
        'UUUUURRRURLLULRLUUUUUULLLURRLURLRUUUUUUUUU',
        'UUUUURRRURLLULRLUUUUUURLRULRRULLLUUUUUUUUU',
        'UUUUURRRURLLULRLUUUUUURLRURRLULLLUUUUUUUUU',
        'UUUUURRRURLLURLRUUUUUULLLULRRULRLUUUUUUUUU',
        'UUUUURRRURLLURLRUUUUUULLLURRLULRLUUUUUUUUU',
        'UUUUURRRURLLURLRUUUUUULRLULRRULLLUUUUUUUUU',
        'UUUUURRRURLLURLRUUUUUULRLURRLULLLUUUUUUUUU',
        'UUUUURRRURLLURRRUUUUUULLLULRRULLLUUUUUUUUU',
        'UUUUURRRURLLURRRUUUUUULLLURRLULLLUUUUUUUUU',
        'UUUUURRRURLRULLLUUUUUULLLULRLURRRUUUUUUUUU',
        'UUUUURRRURLRULLLUUUUUULRLULRLURLRUUUUUUUUU',
        'UUUUURRRURLRULLLUUUUUURLRULRLULRLUUUUUUUUU',
        'UUUUURRRURLRULLLUUUUUURRRULRLULLLUUUUUUUUU',
        'UUUUURRRURLRULRLUUUUUULLLULRLURLRUUUUUUUUU',
        'UUUUURRRURLRULRLUUUUUURLRULRLULLLUUUUUUUUU',
        'UUUUURRRURLRURLRUUUUUULLLULRLULRLUUUUUUUUU',
        'UUUUURRRURLRURLRUUUUUULRLULRLULLLUUUUUUUUU',
        'UUUUURRRURLRURRRUUUUUULLLULRLULLLUUUUUUUUU'
    )

    midge_states = {
        (3, 103): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (11, 28): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (23, 53): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (15, 78): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],

        (36, 115): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (40, 61): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (86, 65): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (90, 111): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],

        (128, 73): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (136, 48): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (140, 98): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
        (148, 123): ['UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF'],
    }

    LR_centers_and_midges_555 = (
        3, 11, 15, 23,
        28, 32, 33, 34, 36, 37, 38, 39, 40, 42, 43, 44, 48,
        53, 61, 65, 73,
        78, 82, 83, 84, 86, 87, 88, 89, 90, 92, 93, 94, 98,
        103, 111, 115, 123,
        128, 136, 140, 148
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step901-LR-center-stage-EO-inner-orbit.txt',
            self.state_targets,
            linecount=10035200,
            max_depth=9,
            filesize=732569600,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
            ),
            use_state_index=True,
        )

    def state(self):
        lt_state = self.parent.state[:]

        for edge_position in MIDGE_TUPLES_555:
            for (e0, e1) in edge_position:
                edge_str = lt_state[e0] + lt_state[e1]

                if edge_str in self.midge_states.get((e0, e1), ()):
                    lt_state[e0] = "U"
                    lt_state[e1] = "U"
                    break
            else:
                lt_state[e0] = "D"
                lt_state[e1] = "D"

        return "".join([lt_state[x] for x in self.LR_centers_and_midges_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):

        # populate the midges
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ['x']
        self.parent.state.extend(list("UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"))
        self.parent.nuke_corners()
        self.parent.nuke_centers_specific(UD_centers_555)
        self.parent.nuke_centers_specific(FB_centers_555)

        # nuke the wings
        for edge_pos in edge_orbit_0_555:
            self.parent.state[edge_pos] = '.'

        for step in steps_to_scramble:
            self.parent.rotate(step)

        # populate the LR centers
        state = list(state)

        for (pos, pos_state) in zip(self.LR_centers_and_midges_555, state):
            if pos in LR_centers_555:
                self.parent.state[pos] = pos_state

        cube = self.parent.state[:]


class LookupTableIDA555EdgeOrientOuterOrbit(LookupTable):
    """
    lookup-table-5x5x5-step902-EO-outer-orbit.txt
    =============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 29 entries (0 percent, 14.50x previous step)
    3 steps has 278 entries (0 percent, 9.59x previous step)
    4 steps has 1,934 entries (0 percent, 6.96x previous step)
    5 steps has 15,640 entries (0 percent, 8.09x previous step)
    6 steps has 124,249 entries (4 percent, 7.94x previous step)
    7 steps has 609,241 entries (22 percent, 4.90x previous step)
    8 steps has 1,224,098 entries (45 percent, 2.01x previous step)
    9 steps has 688,124 entries (25 percent, 0.56x previous step)
    10 steps has 40,560 entries (1 percent, 0.06x previous step)

    Total: 2,704,156 entries
    Average: 7.95 moves
    """

    outer_orbit_indexes = (
        0, 2, 3, 4, 7, 8, 9, 11,
        12, 14, 15, 16, 19, 20, 21, 23,
        24, 26, 27, 28, 31, 32, 33, 35,
        36, 38, 39, 40, 43, 44, 45, 47,
        48, 50, 51, 52, 55, 56, 57, 59,
        60, 62, 63, 64, 67, 68, 69, 71,
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step902-EO-outer-orbit.txt",
            "UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
            linecount=2704156,
            max_depth=10,
            filesize=227149104,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
            ),
            use_state_index=True,
        )

    def state(self):
        eo_state_both_orbits = self.parent.highlow_edges_state()
        return "".join([eo_state_both_orbits[x] for x in self.outer_orbit_indexes])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ['x']
        self.parent.state.extend(list("UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"))
        self.parent.nuke_corners()
        self.parent.nuke_centers()

        # nuke the midges
        for edge_pos in edge_orbit_1_555:
            self.parent.state[edge_pos] = '.'

        for step in steps_to_scramble:
            self.parent.rotate(step)

        cube = self.parent.state[:]

    def ida_heuristic(self):
        state = self.state()
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555EdgeOrientBothOrbits(LookupTable):
    """
    lookup-table-5x5x5-step904-EO-both-orbits.txt
    =============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 33 entries (0 percent, 16.50x previous step)
    3 steps has 382 entries (0 percent, 11.58x previous step)
    4 steps has 4,040 entries (0 percent, 10.58x previous step)
    5 steps has 47,502 entries (0 percent, 11.76x previous step)
    6 steps has 541,439 entries (9 percent, 11.40x previous step)
    7 steps has 5,353,259 entries (90 percent, 9.89x previous step)
    Total: 5,946,658 entries

    extrapolate from here

    8 steps has 48,661,124 entries (9.09x previous step)
    9 steps has 403,400,717 entries (8.29x previous step)
    10 steps has 3,021,471,370 entries (7.49x previous step)
    11 steps has 2,058,631,619 entries (0.68x previous step)

    Average: 10.270569142070691
    Total  : 5,538,111,488
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step904-EO-both-orbits.txt',
            'TBD',
            linecount=5946658,
            max_depth=7,
            filesize=588719142)

    def state(self):
        return self.parent.highlow_edges_state()

    def ida_heuristic(self):
        state = self.parent.highlow_edges_state()
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555LRCenterStageEOBothOrbits(LookupTableIDAViaGraph):

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
            ),
            prune_tables=(
                parent.lt_phase3_lr_center_stage_eo_inner_orbit,
                parent.lt_phase3_eo_outer_orbit,
            ),
        )


class LookupTable555Phase4(LookupTable):
    """
    lookup-table-5x5x5-step40-phase4.txt
    ====================================
    0 steps has 4,239 entries (0 percent, 0.00x previous step)
    1 steps has 1,018,011 entries (0 percent, 240.15x previous step)
    2 steps has 6,276,787 entries (5 percent, 6.17x previous step)
    3 steps has 25,090,688 entries (20 percent, 4.00x previous step)

    The full table was 5.1G and I didn't need to keep that deep so I kept
    up to 3-deep. Here are the remaining distributions.

    4 steps has 50,710,890 entries (41 percent, 2.02x previous step)
    5 steps has 34,813,744 entries (28 percent, 0.69x previous step)
    6 steps has 3,360,706 entries (2 percent, 0.10x previous step)
    7 steps has 12,310 entries (0 percent, 0.00x previous step)

    Total: 121,287,375 entries
    Average: 4.01 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step40-phase4.txt',
            'TBD',
            linecount=32389725,
            max_depth=3,
            filesize=971691750,
        )
        self.wing_strs = None

    def ida_heuristic(self):
        assert self.wing_strs
        original_state = self.parent.state[:]
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        parent_state = self.parent.state

        for square_index in wings_for_edges_pattern_555:
            partner_index = edges_partner_555[square_index]
            square_value = parent_state[square_index]
            partner_value = parent_state[partner_index]
            wing_str = square_value + partner_value

            if not (wing_str == "LL" or wing_str == "xx"):
                wing_str = wing_str_map[square_value + partner_value]

                if wing_str in self.wing_strs:
                    self.parent.state[square_index] = 'L'
                    self.parent.state[partner_index] = 'L'
                else:
                    self.parent.state[square_index] = 'x'
                    self.parent.state[partner_index] = 'x'

        state = ''.join(['1' if parent_state[x] == 'L' else '0' for x in edges_555])
        state = self.hex_format % int(state, 2)
        cost_to_goal = self.heuristic(state)
        self.parent.state = original_state
        #log.info("%s: state %s, cost_to_goal %s" % (self, state, cost_to_goal))
        return (state, cost_to_goal)

    def solve(self, print_steps=False):
        """
        We override the normal solve() so that we do not have to enter all 343,000
        state_targets for this class.
        """
        (state, _cost_to_goal) = self.ida_heuristic()
        steps = self.steps(state)

        if steps:
            for step in steps:
                self.parent.rotate(step)
                if print_steps:
                    log.info("%s: step %s" % (self, step))


class LookupTable555Phase5Centers(LookupTable):
    """
    lookup-table-5x5x5-step51-phase5-centers.txt
    ============================================
    0 steps has 7 entries (0 percent, 0.00x previous step)
    1 steps has 161 entries (0 percent, 23.00x previous step)
    2 steps has 1,146 entries (0 percent, 7.12x previous step)
    3 steps has 7,176 entries (0 percent, 6.26x previous step)
    4 steps has 36,836 entries (1 percent, 5.13x previous step)
    5 steps has 171,754 entries (8 percent, 4.66x previous step)
    6 steps has 503,484 entries (23 percent, 2.93x previous step)
    7 steps has 749,808 entries (35 percent, 1.49x previous step)
    8 steps has 483,736 entries (22 percent, 0.65x previous step)
    9 steps has 158,924 entries (7 percent, 0.33x previous step)
    10 steps has 3,768 entries (0 percent, 0.02x previous step)

    Total: 2,116,800 entries
    Average: 6.91 moves
    """

    state_targets = (
        'LLLLLLLLLBFBBFBBFBRRRRRRRRRFBFFBFFBF',
        'LLLLLLLLLBFFBFFBFFRRRRRRRRRBBFBBFBBF',
        'LLLLLLLLLBFFBFFBFFRRRRRRRRRFBBFBBFBB',
        'LLLLLLLLLFFBFFBFFBRRRRRRRRRBBFBBFBBF',
        'LLLLLLLLLFFBFFBFFBRRRRRRRRRFBBFBBFBB',
        'LLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBB',
        'LLRLLRLLRBFBBFBBFBLRRLRRLRRFBFFBFFBF',
        'LLRLLRLLRBFBBFBBFBRRLRRLRRLFBFFBFFBF',
        'LLRLLRLLRBFFBFFBFFLRRLRRLRRBBFBBFBBF',
        'LLRLLRLLRBFFBFFBFFLRRLRRLRRFBBFBBFBB',
        'LLRLLRLLRBFFBFFBFFRRLRRLRRLBBFBBFBBF',
        'LLRLLRLLRBFFBFFBFFRRLRRLRRLFBBFBBFBB',
        'LLRLLRLLRFFBFFBFFBLRRLRRLRRBBFBBFBBF',
        'LLRLLRLLRFFBFFBFFBLRRLRRLRRFBBFBBFBB',
        'LLRLLRLLRFFBFFBFFBRRLRRLRRLBBFBBFBBF',
        'LLRLLRLLRFFBFFBFFBRRLRRLRRLFBBFBBFBB',
        'LLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBB',
        'LLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBB',
        'RLLRLLRLLBFBBFBBFBLRRLRRLRRFBFFBFFBF',
        'RLLRLLRLLBFBBFBBFBRRLRRLRRLFBFFBFFBF',
        'RLLRLLRLLBFFBFFBFFLRRLRRLRRBBFBBFBBF',
        'RLLRLLRLLBFFBFFBFFLRRLRRLRRFBBFBBFBB',
        'RLLRLLRLLBFFBFFBFFRRLRRLRRLBBFBBFBBF',
        'RLLRLLRLLBFFBFFBFFRRLRRLRRLFBBFBBFBB',
        'RLLRLLRLLFFBFFBFFBLRRLRRLRRBBFBBFBBF',
        'RLLRLLRLLFFBFFBFFBLRRLRRLRRFBBFBBFBB',
        'RLLRLLRLLFFBFFBFFBRRLRRLRRLBBFBBFBBF',
        'RLLRLLRLLFFBFFBFFBRRLRRLRRLFBBFBBFBB',
        'RLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBB',
        'RLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBB',
        'RLRRLRRLRBFBBFBBFBLRLLRLLRLFBFFBFFBF',
        'RLRRLRRLRBFFBFFBFFLRLLRLLRLBBFBBFBBF',
        'RLRRLRRLRBFFBFFBFFLRLLRLLRLFBBFBBFBB',
        'RLRRLRRLRFFBFFBFFBLRLLRLLRLBBFBBFBBF',
        'RLRRLRRLRFFBFFBFFBLRLLRLLRLFBBFBBFBB',
        'RLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBB'
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step51-phase5-centers.txt',
            self.state_targets,
            linecount=2116800,
            max_depth=10,
            filesize=160876800,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "U", "U'",
                "D", "D'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        return ''.join([parent_state[x] for x in LFRB_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(LFRB_centers_555, state):
            cube[pos] = pos_state


class LookupTable555Phase5HighEdgeMidge(LookupTable):
    """
    lookup-table-5x5x5-step53-phase5-high-edge-and-midge.txt
    ========================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 30 entries (0 percent, 6.00x previous step)
    3 steps has 184 entries (0 percent, 6.13x previous step)
    4 steps has 992 entries (0 percent, 5.39x previous step)
    5 steps has 4,845 entries (4 percent, 4.88x previous step)
    6 steps has 17,792 entries (15 percent, 3.67x previous step)
    7 steps has 40,048 entries (34 percent, 2.25x previous step)
    8 steps has 43,400 entries (36 percent, 1.08x previous step)
    9 steps has 10,252 entries (8 percent, 0.24x previous step)
    10 steps has 52 entries (0 percent, 0.01x previous step)

    Total: 117,600 entries
    Average: 7.28 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step53-phase5-high-edge-and-midge.txt',
            '-------------SSTT--UUVV-------------',
            linecount=117600,
            max_depth=10,
            filesize=8820000,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "U", "U'",
                "D", "D'",
            ),
            use_state_index=True,
        )
        self.wing_strs = ("LB", "LF", "RB", "RF")

    def state(self):
        parent_state = self.parent.state
        state = edges_recolor_pattern_555(parent_state[:], self.wing_strs)

        result = []
        for index in wings_for_edges_pattern_555:
            if state[index] == "." or index not in high_wings_and_midges_555:
                result.append("-")
            else:
                result.append(state[index])

        return "".join(result)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ['x']
        self.parent.state.extend(list("UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"))
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        self.parent.nuke_edges_low()
        self.parent.nuke_edges_in_y_plane()
        self.parent.nuke_edges_in_z_plane()
        parent_state = self.parent.state

        for step in steps_to_scramble:
            self.parent.rotate(step)

        cube = self.parent.state[:]


# Only used to create a perfect hash file
'''
class LookupTable555Phase5FBCentersHighEdgeMidge(LookupTableIDAViaGraph):
    """
    lookup-table-5x5x5-step55-phase5-fb-centers-high-edge-and-midge.txt
    ===================================================================
    1 steps has 30 entries (0 percent, 0.00x previous step)
    2 steps has 216 entries (0 percent, 7.20x previous step)
    3 steps has 1,622 entries (0 percent, 7.51x previous step)
    4 steps has 11,198 entries (0 percent, 6.90x previous step)
    5 steps has 75,990 entries (0 percent, 6.79x previous step)
    6 steps has 498,774 entries (0 percent, 6.56x previous step)
    7 steps has 3,105,912 entries (0 percent, 6.23x previous step)
    8 steps has 17,585,391 entries (3 percent, 5.66x previous step)
    9 steps has 81,079,954 entries (14 percent, 4.61x previous step)
    10 steps has 230,361,431 entries (39 percent, 2.84x previous step)
    11 steps has 220,472,982 entries (38 percent, 0.96x previous step)
    12 steps has 23,022,104 entries (3 percent, 0.10x previous step)
    13 steps has 24,396 entries (0 percent, 0.00x previous step)

    Total: 576,240,000 entries
    Average: 10.24 moves
    """

    state_targets = (
        "BFBBFBBFBFBFFBFFBF-------------SSTT--UUVV-------------",
        "BFFBFFBFFBBFBBFBBF-------------SSTT--UUVV-------------",
        "BFFBFFBFFFBBFBBFBB-------------SSTT--UUVV-------------",
        "FFBFFBFFBBBFBBFBBF-------------SSTT--UUVV-------------",
        "FFBFFBFFBFBBFBBFBB-------------SSTT--UUVV-------------",
        "FFFFFFFFFBBBBBBBBB-------------SSTT--UUVV-------------",
    )

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            filename='lookup-table-5x5x5-step55-phase5-fb-centers-high-edge-and-midge.txt',
            state_target=self.state_targets,
            linecount=576240000,
            max_depth=13,
            filesize=59928960000,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "U", "U'",
                "D", "D'",
            ),
            prune_tables=(
                parent.lt_phase5_fb_centers,
                parent.lt_phase5_high_edge_midge,
            ),
        )

    def build_ida_graph_set_cube_state(self, state, steps_to_scramble):
        # Use the normal approach for populating the edges state
        self.parent.re_init()
        for step in steps_to_scramble:
            self.parent.rotate(step)

        # The FB centers have multiple goal states though so set those explicitly
        FB_state = state[0:18]
        for (pos, x) in zip(FB_centers_555, FB_state):
            self.parent.state[pos] = x


class LookupTable555Phase5FBCentersLowEdgeMidge(LookupTableIDAViaGraph):
    """
    lookup-table-5x5x5-step57-phase5-fb-centers-low-edge-and-midge.txt
    ==================================================================
    1 steps has 30 entries (0 percent, 0.00x previous step)
    2 steps has 216 entries (0 percent, 7.20x previous step)
    3 steps has 1,622 entries (0 percent, 7.51x previous step)
    4 steps has 11,198 entries (0 percent, 6.90x previous step)
    5 steps has 75,990 entries (0 percent, 6.79x previous step)
    6 steps has 498,774 entries (0 percent, 6.56x previous step)
    7 steps has 3,105,912 entries (0 percent, 6.23x previous step)
    8 steps has 17,585,391 entries (3 percent, 5.66x previous step)
    9 steps has 81,079,954 entries (14 percent, 4.61x previous step)
    10 steps has 230,361,431 entries (39 percent, 2.84x previous step)
    11 steps has 220,472,982 entries (38 percent, 0.96x previous step)
    12 steps has 23,022,104 entries (3 percent, 0.10x previous step)
    13 steps has 24,396 entries (0 percent, 0.00x previous step)

    Total: 576,240,000 entries
    Average: 10.24 moves
    """

    state_targets = (
        "BFBBFBBFBFBFFBFFBF------------sS--TtuU--Vv------------",
        "BFFBFFBFFBBFBBFBBF------------sS--TtuU--Vv------------",
        "BFFBFFBFFFBBFBBFBB------------sS--TtuU--Vv------------",
        "FFBFFBFFBBBFBBFBBF------------sS--TtuU--Vv------------",
        "FFBFFBFFBFBBFBBFBB------------sS--TtuU--Vv------------",
        "FFFFFFFFFBBBBBBBBB------------sS--TtuU--Vv------------",
    )

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            filename='lookup-table-5x5x5-step57-phase5-fb-centers-low-edge-and-midge.txt',
            state_target=self.state_targets,
            linecount=576240000,
            max_depth=13,
            filesize=59928960000,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "U", "U'",
                "D", "D'",
            ),
            prune_tables=(
                parent.lt_phase5_fb_centers,
                parent.lt_phase5_low_edge_midge,
            ),
        )

    def build_ida_graph_set_cube_state(self, state, steps_to_scramble):
        # Use the normal approach for populating the edges state
        self.parent.re_init()
        for step in steps_to_scramble:
            self.parent.rotate(step)

        # The FB centers have multiple goal states though so set those explicitly
        FB_state = state[0:18]
        for (pos, x) in zip(FB_centers_555, FB_state):
            self.parent.state[pos] = x
'''

class LookupTable555Phase5FBCenters(LookupTable):
    """
    lookup-table-5x5x5-step56-phase5-fb-centers.txt
    ===============================================
    0 steps has 4 entries (0 percent, 0.00x previous step)
    1 steps has 24 entries (0 percent, 6.00x previous step)
    2 steps has 110 entries (2 percent, 4.58x previous step)
    3 steps has 396 entries (8 percent, 3.60x previous step)
    4 steps has 1,196 entries (24 percent, 3.02x previous step)
    5 steps has 2,102 entries (42 percent, 1.76x previous step)
    6 steps has 1,016 entries (20 percent, 0.48x previous step)
    7 steps has 52 entries (1 percent, 0.05x previous step)

    Total: 4,900 entries
    Average: 4.73 moves
    """

    state_targets = (
        "BFBBFBBFBFBFFBFFBF",
        "BFFBFFBFFBBFBBFBBF",
        "BFFBFFBFFFBBFBBFBB",
        "FFBFFBFFBBBFBBFBBF",
        "FFBFFBFFBFBBFBBFBB",
        "FFFFFFFFFBBBBBBBBB",
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step56-phase5-fb-centers.txt',
            self.state_targets,
            linecount=4900,
            max_depth=7,
            filesize=220500,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "U", "U'",
                "D", "D'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in FB_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(FB_centers_555, state):
            cube[pos] = pos_state


class LookupTable555Phase5LowEdgeMidge(LookupTable):
    """
    lookup-table-5x5x5-step54-phase5-low-edge-and-midge.txt
    =======================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 30 entries (0 percent, 6.00x previous step)
    3 steps has 184 entries (0 percent, 6.13x previous step)
    4 steps has 992 entries (0 percent, 5.39x previous step)
    5 steps has 4,845 entries (4 percent, 4.88x previous step)
    6 steps has 17,792 entries (15 percent, 3.67x previous step)
    7 steps has 40,048 entries (34 percent, 2.25x previous step)
    8 steps has 43,400 entries (36 percent, 1.08x previous step)
    9 steps has 10,252 entries (8 percent, 0.24x previous step)
    10 steps has 52 entries (0 percent, 0.01x previous step)

    Total: 117,600 entries
    Average: 7.28 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step54-phase5-low-edge-and-midge.txt',
            '------------sS--TtuU--Vv------------',
            linecount=117600,
            max_depth=10,
            filesize=8702400,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "U", "U'",
                "D", "D'",
            ),
            use_state_index=True,
        )
        self.wing_strs = ("LB", "LF", "RB", "RF")

    def state(self):
        parent_state = self.parent.state
        state = edges_recolor_pattern_555(parent_state[:], self.wing_strs)

        result = []
        for index in wings_for_edges_pattern_555:
            if state[index] == "." or index not in low_wings_and_midges_555:
                result.append("-")
            else:
                result.append(state[index])

        return "".join(result)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ['x']
        self.parent.state.extend(list("UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"))
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        self.parent.nuke_edges_high()
        self.parent.nuke_edges_in_y_plane()
        self.parent.nuke_edges_in_z_plane()
        parent_state = self.parent.state

        for step in steps_to_scramble:
            self.parent.rotate(step)

        cube = self.parent.state[:]


class LookupTableIDA555Phase5(LookupTableIDAViaGraph):

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'",
                "Dw", "Dw'",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "U", "U'",
                "D", "D'",
            ),
            prune_tables=(
                parent.lt_phase5_centers,
                parent.lt_phase5_fb_centers,
                parent.lt_phase5_high_edge_midge,
                parent.lt_phase5_low_edge_midge,
            ),
            perfect_hash_filename="lookup-table-5x5x5-step55-phase5-fb-centers-high-edge-and-midge.pt-state-perfect-hash",
            pt2_state_max=117600,
        )


class LookupTable555Phase6Centers(LookupTable):
    """
    lookup-table-5x5x5-step61-phase6-centers.txt
    ============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 42 entries (0 percent, 10.50x previous step)
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
            'lookup-table-5x5x5-step61-phase6-centers.txt',
            'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD',
            linecount=176400,
            max_depth=9,
            filesize=15699600,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'", "Uw2",
                "Dw", "Dw'", "Dw2",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "F", "F'",
                "B", "B'",
            ),
            use_state_index=True,
        )

    def state(self):
        parent_state = self.parent.state
        return ''.join([parent_state[x] for x in centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(centers_555, state):
            cube[pos] = pos_state


class LookupTable555Phase6HighEdgeMidge(LookupTable):
    """
    lookup-table-5x5x5-step62-phase6-high-edge-midge.txt
    ====================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 26 entries (0 percent, 5.20x previous step)
    3 steps has 128 entries (0 percent, 4.92x previous step)
    4 steps has 511 entries (1 percent, 3.99x previous step)
    5 steps has 1,772 entries (4 percent, 3.47x previous step)
    6 steps has 5,404 entries (13 percent, 3.05x previous step)
    7 steps has 11,596 entries (28 percent, 2.15x previous step)
    8 steps has 14,656 entries (36 percent, 1.26x previous step)
    9 steps has 6,146 entries (15 percent, 0.42x previous step)
    10 steps has 76 entries (0 percent, 0.01x previous step)

    Total: 40,320 entries
    Average: 7.40 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step62-phase6-high-edge-midge.txt',
            'OO--PPQQ--RR------------WW--XXYY--ZZ',
            linecount=40320,
            max_depth=10,
            filesize=2983680,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'", "Uw2",
                "Dw", "Dw'", "Dw2",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "F", "F'",
                "B", "B'",
            ),
            use_state_index=True,
        )
        self.wing_strs = ("UB", "UL", "UR", "UF", "DB", "DL", "DR", "DF")

    def state(self):
        parent_state = self.parent.state
        state = edges_recolor_pattern_555(parent_state[:], self.wing_strs)

        result = []
        for index in wings_for_edges_pattern_555:
            if state[index] == "." or index not in high_wings_and_midges_555:
                result.append("-")
            else:
                result.append(state[index])

        return "".join(result)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ['x']
        self.parent.state.extend(list("UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"))
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        self.parent.nuke_edges_low()
        self.parent.nuke_edges_in_x_plane()
        parent_state = self.parent.state

        for step in steps_to_scramble:
            self.parent.rotate(step)

        cube = self.parent.state[:]


class LookupTable555Phase6LowEdgeMidge(LookupTable):
    """
    lookup-table-5x5x5-step63-phase6-low-edge-midge.txt
    ===================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 26 entries (0 percent, 5.20x previous step)
    3 steps has 128 entries (0 percent, 4.92x previous step)
    4 steps has 511 entries (1 percent, 3.99x previous step)
    5 steps has 1,772 entries (4 percent, 3.47x previous step)
    6 steps has 5,404 entries (13 percent, 3.05x previous step)
    7 steps has 11,596 entries (28 percent, 2.15x previous step)
    8 steps has 14,656 entries (36 percent, 1.26x previous step)
    9 steps has 6,146 entries (15 percent, 0.42x previous step)
    10 steps has 76 entries (0 percent, 0.01x previous step)

    Total: 40,320 entries
    Average: 7.40 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step63-phase6-low-edge-midge.txt',
            '-OopP--QqrR--------------WwxX--YyzZ-',
            linecount=40320,
            max_depth=10,
            filesize=2983680,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'", "Uw2",
                "Dw", "Dw'", "Dw2",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "F", "F'",
                "B", "B'",
            ),
            use_state_index=True,
        )
        self.wing_strs = ("UB", "UL", "UR", "UF", "DB", "DL", "DR", "DF")

    def state(self):
        parent_state = self.parent.state
        state = edges_recolor_pattern_555(parent_state[:], self.wing_strs)

        result = []
        for index in wings_for_edges_pattern_555:
            if state[index] == "." or index not in low_wings_and_midges_555:
                result.append("-")
            else:
                result.append(state[index])

        return "".join(result)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ['x']
        self.parent.state.extend(list("UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"))
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        self.parent.nuke_edges_high()
        self.parent.nuke_edges_in_x_plane()
        parent_state = self.parent.state

        for step in steps_to_scramble:
            self.parent.rotate(step)

        cube = self.parent.state[:]


'''
class LookupTableIDA555Phase6Edges(LookupTableIDAViaGraph):
    """
    This was used to build lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.pt-state
    which was then converted to lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.pt-state-perfect-hash

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
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            state_target='OOopPPQQqrRR------------WWwxXXYYyzZZ',
            filename='lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.txt',
            filesize=634035456,
            max_depth=9,
            linecount=8806048,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'", "Uw2",
                "Dw", "Dw'", "Dw2",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "F", "F'",
                "B", "B'",
            ),
            prune_tables=(
                parent.lt_phase6_high_edge_midge,
                parent.lt_phase6_low_edge_midge,
            ),
        )
'''


class LookupTableIDA555Phase6(LookupTableIDAViaGraph):
    """
    Pair the last eight edges and solve the centers
    """

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=(
                "Uw", "Uw'", "Uw2",
                "Dw", "Dw'", "Dw2",
                "Fw", "Fw'",
                "Bw", "Bw'",
                "Lw", "Lw'",
                "Rw", "Rw'",
                "L", "L'",
                "R", "R'",
                "F", "F'",
                "B", "B'",
            ),
            prune_tables=(
                parent.lt_phase6_centers,
                parent.lt_phase6_high_edge_midge,
                parent.lt_phase6_low_edge_midge,
            ),
            multiplier=1.2,
            perfect_hash_filename="lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.pt-state-perfect-hash",
            pt2_state_max=40320,
        )


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
        (2, 104), (3, 103), (4, 102), (6, 27), (10, 79), (11, 28), (15, 78), (16, 29), (20, 77), (22, 52), (23, 53), (24, 54),  # Upper
        (27, 6), (28, 11), (29, 16), (31, 110), (35, 56), (36, 115), (40, 61), (41, 120), (45, 66), (47, 141), (48, 136), (49, 131),  # Left
        (52, 22), (53, 23), (54, 24), (56, 35), (60, 81), (61, 40), (65, 86), (66, 45), (70, 91), (72, 127), (73, 128), (74, 129),  # Front
        (77, 20), (78, 15), (79, 10), (81, 60), (85, 106), (86, 65), (90, 111), (91, 70), (95, 116), (97, 135), (98, 140), (99, 145),  # Right
        (102, 4), (103, 3), (104, 2), (106, 85), (110, 31), (111, 90), (115, 36), (116, 95), (120, 41), (122, 149), (123, 148), (124, 147),  # Back
        (127, 72), (128, 73), (129, 74), (131, 49), (135, 97), (136, 48), (140, 98), (141, 47), (145, 99), (147, 124), (148, 123), (149, 122),  # Down
    )

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCube.__init__(self, state, order, colormap)

        # This will be True when an even cube is using the 555 edge solver
        # to pair an orbit of edges
        self.avoid_pll = False

        if RubiksCube555.instantiated:
            # raise Exception("Another 5x5x5 instance is being created")
            # log.warning("Another 5x5x5 instance is being created")
            pass
        else:
            RubiksCube555.instantiated = True

        if debug:
            log.setLevel(logging.DEBUG)

    def phase(self):
        if self._phase is None:
            self._phase = "Stage UD centers"
            return self._phase

        if self._phase == "Stage UD centers":
            if self.UD_centers_staged():
                self._phase = "Stage LR centers"
            return self._phase

        if self._phase == "Stage LR centers":
            if self.LR_centers_staged():
                self._phase = "Solve Centers"

        if self._phase == "Solve Centers":
            if self.centers_solved():
                self._phase = "Pair Edges"

        if self._phase == "Pair Edges":
            if not self.get_non_paired_edges():
                self._phase = "Solve 3x3x3"

        return self._phase

    def nuke_centers_specific(self, centers):
        for square_index in centers:
            self.state[square_index] = "."

    def nuke_edges_specific(self, edges):
        for square_index in edges:
            partner_index = edges_partner_555[square_index]
            self.state[square_index] = "."
            self.state[partner_index] = "."

    def nuke_edges_high(self):
        high_edges = (2, 10, 24, 16, 35, 41, 85, 91, 127, 135, 149, 141)
        self.nuke_edges_specific(high_edges)

    def nuke_edges_low(self):
        low_edges = (4, 20, 22, 6, 31, 45, 81, 95, 129, 145, 147, 131)
        self.nuke_edges_specific(low_edges)

    def nuke_edges_in_x_plane(self):
        x_plane_edges = (31, 36, 41, 35, 40, 45, 81, 86, 91, 85, 90, 95)
        self.nuke_edges_specific(x_plane_edges)

    def nuke_edges_in_y_plane(self):
        y_plane_edges = (2, 3, 4, 22, 23, 24, 127, 128, 129, 147, 148, 149)
        self.nuke_edges_specific(y_plane_edges)

    def nuke_edges_in_z_plane(self):
        z_plane_edges = (6, 11, 16, 10, 15, 20, 131, 136, 141, 135, 140, 145)
        self.nuke_edges_specific(z_plane_edges)

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

        self._sanity_check("edge-orbit-0", edge_orbit_0_555, 8)
        self._sanity_check("edge-orbit-1", edge_orbit_1_555, 4)
        self._sanity_check("corners", corners_555, 4)
        # self._sanity_check('x-centers', x_centers_555, 4)
        # self._sanity_check('t-centers', t_centers_555, 4)
        self._sanity_check("centers", centers, 1)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_LR_t_centers_stage = LookupTable555LRTCenterStage(self)
        self.lt_LR_x_centers_stage = LookupTable555LRXCenterStage(self)
        self.lt_LR_centers_stage = LookupTableIDA555LRCenterStage(self)

        self.lt_FB_t_centers_stage = LookupTable555FBTCenterStage(self)
        self.lt_FB_x_centers_stage = LookupTable555FBXCenterStage(self)
        self.lt_FB_centers_stage_LR_centers_432 = LookupTable555FBCenterStageLRCenter432(self)
        self.lt_FB_centers_stage = LookupTableIDA555FBCentersStage(self)
        self.lt_FB_centers_stage.avoid_oll = 0

        self.lt_phase3_lr_center_stage_eo_inner_orbit = LookupTable555LRCenterStageEOInnerOrbit(self)
        self.lt_phase3_eo_outer_orbit = LookupTableIDA555EdgeOrientOuterOrbit(self)
        self.lt_phase3_eo_both_orbits = LookupTable555EdgeOrientBothOrbits(self)
        self.lt_phase3 = LookupTableIDA555LRCenterStageEOBothOrbits(self)

        self.lt_phase4 = LookupTable555Phase4(self)

        self.lt_phase5_centers = LookupTable555Phase5Centers(self)
        self.lt_phase5_high_edge_midge = LookupTable555Phase5HighEdgeMidge(self)
        self.lt_phase5_low_edge_midge = LookupTable555Phase5LowEdgeMidge(self)
        self.lt_phase5_fb_centers = LookupTable555Phase5FBCenters(self)
        self.lt_phase5 = LookupTableIDA555Phase5(self)

        self.lt_phase6_centers = LookupTable555Phase6Centers(self)
        self.lt_phase6_high_edge_midge = LookupTable555Phase6HighEdgeMidge(self)
        self.lt_phase6_low_edge_midge = LookupTable555Phase6LowEdgeMidge(self)
        self.lt_phase6 = LookupTableIDA555Phase6(self)

        self.lt_UD_centers_solve = LookupTable555UDCenterSolve(self)
        self.lt_LR_centers_solve = LookupTable555LRCenterSolve(self)
        self.lt_FB_centers_solve = LookupTable555FBCenterSolve(self)
        self.lt_ULFRBD_centers_solve = LookupTableIDA555ULFRBDCentersSolve(self)
        self.lt_ULFRBD_t_centers_solve = LookupTable555TCenterSolve(self)

    def highlow_edges_state(self):
        state = self.state
        result = []

        for (x, y) in self.reduce333_orient_edges_tuples:
            try:
                result.append(highlow_edge_values_555[(x, y, state[x], state[y])])
            except KeyError:
                result.append(".")

        result = "".join(result)
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

    def edges_flip_orientation(self, must_be_uppercase=[], must_be_lowercase=[]):
        state = edges_recolor_pattern_555(self.state[:])
        edges_state = "".join([state[index] for index in wings_for_edges_pattern_555])

        to_flip = []

        # 000 000 000 011 111 111 112 222 222 222 333 333
        # 012 345 678 901 234 567 890 123 456 789 012 345
        # Roo rPz Qqw qrP Sss TTt Uuu VVv ZwW Xxx YYy pzO
        #  ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^
        #  UB  UL  UR  UD  LB  LF  RF  RB  DF  DL  DR  DB
        for (edge_state_index, square_index, partner_index) in (
            (1, 3, 103),  # UB
            (4, 11, 28),  # UL
            (7, 15, 78),  # UR
            (10, 23, 53),  # UF
            (13, 36, 115),  # LB
            (16, 40, 61),  # LF
            (19, 86, 65),  # RF
            (22, 90, 111),  # RB
            (25, 128, 73),  # DF
            (28, 136, 48),  # DL
            (31, 140, 98),  # DR
            (34, 148, 123), # DB
        ):

            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if must_be_uppercase or must_be_lowercase:
                # log.info("must_be_uppercase %s, must_be_lowercase %s" % (must_be_uppercase, must_be_lowercase))

                if (wing_str in must_be_uppercase and edges_state[edge_state_index].islower()):
                    to_flip.append(wing_str)
                elif (wing_str in must_be_lowercase and edges_state[edge_state_index].isupper()):
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

    def group_centers_stage_LR(self):
        """
        Stage LR centers
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if not self.LR_centers_staged():
            tmp_solution_len = len(self.solution)
            self.lt_LR_centers_stage.solve_via_c()
            self.print_cube()
            self.solution.append(
                "COMMENT_%d_steps_555_LR_centers_staged"
                % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
            )

        log.info(
            "%s: LR centers staged, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

    def group_centers_stage_FB(self):
        """
        Stage FB centers
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if not self.FB_centers_staged():
            tmp_solution_len = len(self.solution)
            self.lt_FB_centers_stage.solve_via_c()
            self.print_cube()
            self.solution.append(
                "COMMENT_%d_steps_555_FB_centers_staged"
                % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
            )
        else:
            try:
                if self.edge_swaps_odd(False, 0, False):
                    self.prevent_OLL()
            # This can happen when large NxNxN cubes are using us but they have not
            # populated the edges on their fake_555 object
            except ValueError:
                pass

        log.info(
            "%s: FB centers staged, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

    def eo_edges(self):
        """
        Our goal is to get the edges split into high/low groups but we do not
        care what the final orienation is of the edges. Each edge can either
        be in its final orientation or not so there are (2^12)/2 or 2048 possible
        permutations.  The /2 is because there cannot be an odd number of edges
        not in their final orientation.
        """
        permutations = []
        original_state = self.state[:]
        original_solution = self.solution[:]
        tmp_solution_len = len(self.solution)

        # Build a list of the wing strings at each midge
        wing_strs = []

        for (_, square_index, partner_index) in midges_recolor_tuples_555:
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = square_value + partner_value
            wing_str = wing_str_map[square_value + partner_value]
            wing_strs.append(wing_str)
        log.info(f"wing_strs: {wing_strs}")

        # build a list of all possible EO permutations...an even number of edges must be high
        for num in range(4096):
            num = str(bin(num)).lstrip("0b").zfill(12)
            if num.count("1") % 2 == 0:
                permutations.append(list(map(int, num)))

        # Put all 2048 starting states in a file and point ida-via-graph
        # at the file so it can solve all of them and apply the one that is the shortest.
        pt_states = []

        for (index, permutation) in enumerate(permutations):
            must_be_uppercase = []
            must_be_lowercase = []
            self.state = original_state[:]

            for (wing_str, uppercase) in zip(wing_strs, permutation):
                if uppercase:
                    must_be_uppercase.append(wing_str)
                else:
                    must_be_lowercase.append(wing_str)

            #log.info("%s: %s permutation %s" % (self, index, "".join(map(str, permutation))))
            self.edges_flip_orientation(must_be_uppercase, must_be_lowercase)

            pt_states.append((
                0,
                self.lt_phase3_lr_center_stage_eo_inner_orbit.state_index(),
                self.lt_phase3_eo_outer_orbit.state_index()
            ))

        self.state = original_state[:]
        self.solution = original_solution[:]

        for x in range(9, 30):
            try:
                self.lt_phase3.solve_via_c(max_ida_threshold=x, pt_states=pt_states)
                break
            except NoIDASolution:
                pass

        # re-color the cube so that the edges are oriented correctly so we can
        # pair 4-edges then 8-edges. After all edge pairing is done we will uncolor
        # the cube and re-apply the solution.
        self.post_eo_state = self.state[:]
        self.post_eo_solution = self.solution[:]
        self.edges_flip_orientation(wing_strs, [])

        self.highlow_edges_print()
        self.print_cube()
        log.info("%s: end of phase 3, edges EOed, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.solution.append(
            "COMMENT_%d_steps_555_edges_EOed"
                % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

    def find_first_four_edges_to_pair(self):

        # In order to make phase5 much faster we need to arrange one group of 4-edges
        # so that none of them are in the z-plane.  This is the job of phase4.  There
        # are 12!/(4!*8!) or 495 different 4-edge combinations.  Try them all and see
        # which one has the lowest phase4 cost.
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)
        costs = []

        # Put all 495 wing_str states in a file and point ida-via-graph
        # at the file so it can solve all of them and apply the one that is the shortest.
        pt_states = []
        line_index_pre_steps = {}

        for (wing_str_index, wing_str_combo) in enumerate(itertools.combinations(wing_strs_all, 4)):
            self.state = original_state[:]
            self.solution = original_solution[:]

            wing_str_combo = sorted(wing_str_combo)
            self.lt_phase4.wing_strs = wing_str_combo
            (_state, cost_to_stage) = self.lt_phase4.ida_heuristic()
            self.lt_phase4.solve()
            phase4_solution = self.solution[original_solution_len:]
            phase4_solution_len = len(phase4_solution)
            line_index_pre_steps[wing_str_index] = phase4_solution

            self.edges_flip_orientation(wing_str_combo, [])

            self.lt_phase5_high_edge_midge.wing_strs = wing_str_combo
            self.lt_phase5_low_edge_midge.wing_strs = wing_str_combo

            try:
                pt_states.append((
                    phase4_solution_len,
                    self.lt_phase5_centers.state_index(),
                    self.lt_phase5_fb_centers.state_index(),
                    self.lt_phase5_high_edge_midge.state_index(),
                    self.lt_phase5_low_edge_midge.state_index(),
                ))
            except TypeError:
                pt_states.append((99, 0, 0, 0, 0))

        self.state = original_state[:]
        self.solution = original_solution[:]

        for x in range(12, 30):
            try:
                min_wing_str_combo_index = self.lt_phase5.solve_via_c(max_ida_threshold=x, pt_states=pt_states, line_index_pre_steps=line_index_pre_steps)
                break
            except NoIDASolution:
                pass

        min_wing_str_combo = list(itertools.combinations(wing_strs_all, 4))[min_wing_str_combo_index]
        self.state = original_state[:]
        self.solution = original_solution[:]
        return min_wing_str_combo

    def pair_first_four_edges(self):
        min_wing_str_combo = self.find_first_four_edges_to_pair()
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)

        self.state = original_state[:]
        self.solution = original_solution[:]
        self.lt_phase4.wing_strs = min_wing_str_combo
        self.lt_phase4.solve(True)
        self.print_cube()
        log.info("%s: end of phase 4, first four edges in x-plane and y-plane, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.solution.append(
            "COMMENT_%d_steps_555_first_four_edges_staged"
                % self.get_solution_len_minus_rotates(self.solution[original_solution_len:])
        )

        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)

        self.edges_flip_orientation(min_wing_str_combo, [])
        self.lt_phase5_high_edge_midge.wing_strs = min_wing_str_combo
        self.lt_phase5_low_edge_midge.wing_strs = min_wing_str_combo
        self.lt_phase5.solve_via_c()

        pair_four_edge_solution = self.solution[original_solution_len:]
        self.state = original_state[:]
        self.solution = original_solution[:]

        for step in pair_four_edge_solution:
            self.rotate(step)

        self.print_cube()
        log.info("%s: kociemba %s" % (self, self.get_kociemba_string(True)))
        log.info("%s: end of phase 5, x-plane edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.solution.append(
            "COMMENT_%d_steps_555_first_four_edges_paired"
                % self.get_solution_len_minus_rotates(self.solution[original_solution_len:])
        )

    def pair_last_eight_edges(self, max_ida=99):
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(original_solution)
        tmp_solution_len = len(self.solution)

        # We need the edge swaps to be even for our edges lookup table to work.
        if self.edge_swaps_odd(False, 0, False):
            raise SolveError("edge swaps are odd, cannot pair last 8-edges")

        self.edges_flip_orientation(wing_strs_all, [])
        #self.highlow_edges_print()
        #self.print_cube()

        yz_plane_edges = tuple(list(self.get_y_plane_wing_strs()) + list(self.get_z_plane_wing_strs()))
        self.lt_phase6_high_edge_midge.ida_graph_node = None
        self.lt_phase6_low_edge_midge.ida_graph_node = None
        self.lt_phase6_high_edge_midge.wing_strs = yz_plane_edges
        self.lt_phase6_low_edge_midge.wing_strs = yz_plane_edges

        # Test the prune tables
        #self.lt_phase6_high_edge_midge.load_ida_graph()
        #self.lt_phase6_high_edge_midge.solve()
        #self.lt_phase6_low_edge_midge.load_ida_graph()
        #self.lt_phase6_low_edge_midge.solve()
        #self.print_cube()
        #sys.exit(0)
        self.lt_phase6.solve_via_c(max_ida)

        pair_eight_edge_solution = self.solution[original_solution_len:]
        self.state = original_state[:]
        self.solution = original_solution[:]

        for step in pair_eight_edge_solution:
            self.rotate(step)

        self.print_cube()
        self.solution.append(
            "COMMENT_%d_steps_555_last_eight_edges_paired"
            % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:])
        )

        log.info("%s: reduced to 3x3x3, %d steps in"
            % (self, self.get_solution_len_minus_rotates(self.solution))
        )

    def reduce_333(self):
        self.lt_init()
        # log.info("%s: kociemba %s" % (self, self.get_kociemba_string(True)))

        if not self.centers_solved() or not self.edges_paired():
            self.group_centers_stage_LR()
            self.group_centers_stage_FB()
            self.eo_edges()
            self.pair_first_four_edges()
            self.pair_last_eight_edges()

            edges_solution = self.solution[len(self.post_eo_solution):]
            self.state = self.post_eo_state
            self.solution = self.post_eo_solution[:len(self.post_eo_solution)]

            for step in edges_solution:
                if step.startswith("COMMENT"):
                    self.solution.append(step)
                else:
                    self.rotate(step)

        self.solution.append("CENTERS_SOLVED")
        self.solution.append("EDGES_GROUPED")


swaps_555 = {"2B": (0, 1, 2, 3, 4, 5, 79, 84, 89, 94, 99, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 10, 28, 29, 30, 31, 9, 33, 34, 35, 36, 8, 38, 39, 40, 41, 7, 43, 44, 45, 46, 6, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 145, 80, 81, 82, 83, 144, 85, 86, 87, 88, 143, 90, 91, 92, 93, 142, 95, 96, 97, 98, 141, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 27, 32, 37, 42, 47, 146, 147, 148, 149, 150,), "2B'": (0, 1, 2, 3, 4, 5, 47, 42, 37, 32, 27, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 141, 28, 29, 30, 31, 142, 33, 34, 35, 36, 143, 38, 39, 40, 41, 144, 43, 44, 45, 46, 145, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 6, 80, 81, 82, 83, 7, 85, 86, 87, 88, 8, 90, 91, 92, 93, 9, 95, 96, 97, 98, 10, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 99, 94, 89, 84, 79, 146, 147, 148, 149, 150,), "2B2": (0, 1, 2, 3, 4, 5, 145, 144, 143, 142, 141, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 99, 28, 29, 30, 31, 94, 33, 34, 35, 36, 89, 38, 39, 40, 41, 84, 43, 44, 45, 46, 79, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 47, 80, 81, 82, 83, 42, 85, 86, 87, 88, 37, 90, 91, 92, 93, 32, 95, 96, 97, 98, 27, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 10, 9, 8, 7, 6, 146, 147, 148, 149, 150,), "2D": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 116, 117, 118, 119, 120, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 41, 42, 43, 44, 45, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 66, 67, 68, 69, 70, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 91, 92, 93, 94, 95, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "2D'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 66, 67, 68, 69, 70, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 91, 92, 93, 94, 95, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 116, 117, 118, 119, 120, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 41, 42, 43, 44, 45, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "2D2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 91, 92, 93, 94, 95, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 116, 117, 118, 119, 120, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 41, 42, 43, 44, 45, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 66, 67, 68, 69, 70, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "2F": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 49, 44, 39, 34, 29, 21, 22, 23, 24, 25, 26, 27, 28, 131, 30, 31, 32, 33, 132, 35, 36, 37, 38, 133, 40, 41, 42, 43, 134, 45, 46, 47, 48, 135, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 16, 78, 79, 80, 81, 17, 83, 84, 85, 86, 18, 88, 89, 90, 91, 19, 93, 94, 95, 96, 20, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 97, 92, 87, 82, 77, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "2F'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 77, 82, 87, 92, 97, 21, 22, 23, 24, 25, 26, 27, 28, 20, 30, 31, 32, 33, 19, 35, 36, 37, 38, 18, 40, 41, 42, 43, 17, 45, 46, 47, 48, 16, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 135, 78, 79, 80, 81, 134, 83, 84, 85, 86, 133, 88, 89, 90, 91, 132, 93, 94, 95, 96, 131, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 29, 34, 39, 44, 49, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "2F2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 135, 134, 133, 132, 131, 21, 22, 23, 24, 25, 26, 27, 28, 97, 30, 31, 32, 33, 92, 35, 36, 37, 38, 87, 40, 41, 42, 43, 82, 45, 46, 47, 48, 77, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 49, 78, 79, 80, 81, 44, 83, 84, 85, 86, 39, 88, 89, 90, 91, 34, 93, 94, 95, 96, 29, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 20, 19, 18, 17, 16, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "2L": ( 0, 1, 124, 3, 4, 5, 6, 119, 8, 9, 10, 11, 114, 13, 14, 15, 16, 109, 18, 19, 20, 21, 104, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 2, 53, 54, 55, 56, 7, 58, 59, 60, 61, 12, 63, 64, 65, 66, 17, 68, 69, 70, 71, 22, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 147, 105, 106, 107, 108, 142, 110, 111, 112, 113, 137, 115, 116, 117, 118, 132, 120, 121, 122, 123, 127, 125, 126, 52, 128, 129, 130, 131, 57, 133, 134, 135, 136, 62, 138, 139, 140, 141, 67, 143, 144, 145, 146, 72, 148, 149, 150,), "2L'": ( 0, 1, 52, 3, 4, 5, 6, 57, 8, 9, 10, 11, 62, 13, 14, 15, 16, 67, 18, 19, 20, 21, 72, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 127, 53, 54, 55, 56, 132, 58, 59, 60, 61, 137, 63, 64, 65, 66, 142, 68, 69, 70, 71, 147, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 22, 105, 106, 107, 108, 17, 110, 111, 112, 113, 12, 115, 116, 117, 118, 7, 120, 121, 122, 123, 2, 125, 126, 124, 128, 129, 130, 131, 119, 133, 134, 135, 136, 114, 138, 139, 140, 141, 109, 143, 144, 145, 146, 104, 148, 149, 150,), "2L2": ( 0, 1, 127, 3, 4, 5, 6, 132, 8, 9, 10, 11, 137, 13, 14, 15, 16, 142, 18, 19, 20, 21, 147, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 124, 53, 54, 55, 56, 119, 58, 59, 60, 61, 114, 63, 64, 65, 66, 109, 68, 69, 70, 71, 104, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 72, 105, 106, 107, 108, 67, 110, 111, 112, 113, 62, 115, 116, 117, 118, 57, 120, 121, 122, 123, 52, 125, 126, 2, 128, 129, 130, 131, 7, 133, 134, 135, 136, 12, 138, 139, 140, 141, 17, 143, 144, 145, 146, 22, 148, 149, 150,), "2R": ( 0, 1, 2, 3, 54, 5, 6, 7, 8, 59, 10, 11, 12, 13, 64, 15, 16, 17, 18, 69, 20, 21, 22, 23, 74, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 129, 55, 56, 57, 58, 134, 60, 61, 62, 63, 139, 65, 66, 67, 68, 144, 70, 71, 72, 73, 149, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 24, 103, 104, 105, 106, 19, 108, 109, 110, 111, 14, 113, 114, 115, 116, 9, 118, 119, 120, 121, 4, 123, 124, 125, 126, 127, 128, 122, 130, 131, 132, 133, 117, 135, 136, 137, 138, 112, 140, 141, 142, 143, 107, 145, 146, 147, 148, 102, 150,), "2R'": ( 0, 1, 2, 3, 122, 5, 6, 7, 8, 117, 10, 11, 12, 13, 112, 15, 16, 17, 18, 107, 20, 21, 22, 23, 102, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 4, 55, 56, 57, 58, 9, 60, 61, 62, 63, 14, 65, 66, 67, 68, 19, 70, 71, 72, 73, 24, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 149, 103, 104, 105, 106, 144, 108, 109, 110, 111, 139, 113, 114, 115, 116, 134, 118, 119, 120, 121, 129, 123, 124, 125, 126, 127, 128, 54, 130, 131, 132, 133, 59, 135, 136, 137, 138, 64, 140, 141, 142, 143, 69, 145, 146, 147, 148, 74, 150,), "2R2": ( 0, 1, 2, 3, 129, 5, 6, 7, 8, 134, 10, 11, 12, 13, 139, 15, 16, 17, 18, 144, 20, 21, 22, 23, 149, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 122, 55, 56, 57, 58, 117, 60, 61, 62, 63, 112, 65, 66, 67, 68, 107, 70, 71, 72, 73, 102, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 74, 103, 104, 105, 106, 69, 108, 109, 110, 111, 64, 113, 114, 115, 116, 59, 118, 119, 120, 121, 54, 123, 124, 125, 126, 127, 128, 4, 130, 131, 132, 133, 9, 135, 136, 137, 138, 14, 140, 141, 142, 143, 19, 145, 146, 147, 148, 24, 150,), "2U": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 56, 57, 58, 59, 60, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 81, 82, 83, 84, 85, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 106, 107, 108, 109, 110, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 31, 32, 33, 34, 35, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "2U'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 106, 107, 108, 109, 110, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 31, 32, 33, 34, 35, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 56, 57, 58, 59, 60, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 81, 82, 83, 84, 85, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "2U2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 81, 82, 83, 84, 85, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 106, 107, 108, 109, 110, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 31, 32, 33, 34, 35, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 56, 57, 58, 59, 60, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "3F": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 48, 43, 38, 33, 28, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 136, 29, 30, 31, 32, 137, 34, 35, 36, 37, 138, 39, 40, 41, 42, 139, 44, 45, 46, 47, 140, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 11, 79, 80, 81, 82, 12, 84, 85, 86, 87, 13, 89, 90, 91, 92, 14, 94, 95, 96, 97, 15, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 98, 93, 88, 83, 78, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "3F'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 78, 83, 88, 93, 98, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 15, 29, 30, 31, 32, 14, 34, 35, 36, 37, 13, 39, 40, 41, 42, 12, 44, 45, 46, 47, 11, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 140, 79, 80, 81, 82, 139, 84, 85, 86, 87, 138, 89, 90, 91, 92, 137, 94, 95, 96, 97, 136, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 28, 33, 38, 43, 48, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "3F2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 140, 139, 138, 137, 136, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 98, 29, 30, 31, 32, 93, 34, 35, 36, 37, 88, 39, 40, 41, 42, 83, 44, 45, 46, 47, 78, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 48, 79, 80, 81, 82, 43, 84, 85, 86, 87, 38, 89, 90, 91, 92, 33, 94, 95, 96, 97, 28, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 15, 14, 13, 12, 11, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "3L": ( 0, 1, 2, 123, 4, 5, 6, 7, 118, 9, 10, 11, 12, 113, 14, 15, 16, 17, 108, 19, 20, 21, 22, 103, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 3, 54, 55, 56, 57, 8, 59, 60, 61, 62, 13, 64, 65, 66, 67, 18, 69, 70, 71, 72, 23, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 148, 104, 105, 106, 107, 143, 109, 110, 111, 112, 138, 114, 115, 116, 117, 133, 119, 120, 121, 122, 128, 124, 125, 126, 127, 53, 129, 130, 131, 132, 58, 134, 135, 136, 137, 63, 139, 140, 141, 142, 68, 144, 145, 146, 147, 73, 149, 150,), "3L'": ( 0, 1, 2, 53, 4, 5, 6, 7, 58, 9, 10, 11, 12, 63, 14, 15, 16, 17, 68, 19, 20, 21, 22, 73, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 128, 54, 55, 56, 57, 133, 59, 60, 61, 62, 138, 64, 65, 66, 67, 143, 69, 70, 71, 72, 148, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 23, 104, 105, 106, 107, 18, 109, 110, 111, 112, 13, 114, 115, 116, 117, 8, 119, 120, 121, 122, 3, 124, 125, 126, 127, 123, 129, 130, 131, 132, 118, 134, 135, 136, 137, 113, 139, 140, 141, 142, 108, 144, 145, 146, 147, 103, 149, 150,), "3L2": ( 0, 1, 2, 128, 4, 5, 6, 7, 133, 9, 10, 11, 12, 138, 14, 15, 16, 17, 143, 19, 20, 21, 22, 148, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 123, 54, 55, 56, 57, 118, 59, 60, 61, 62, 113, 64, 65, 66, 67, 108, 69, 70, 71, 72, 103, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 73, 104, 105, 106, 107, 68, 109, 110, 111, 112, 63, 114, 115, 116, 117, 58, 119, 120, 121, 122, 53, 124, 125, 126, 127, 3, 129, 130, 131, 132, 8, 134, 135, 136, 137, 13, 139, 140, 141, 142, 18, 144, 145, 146, 147, 23, 149, 150,), "3U": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 61, 62, 63, 64, 65, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 86, 87, 88, 89, 90, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 111, 112, 113, 114, 115, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 36, 37, 38, 39, 40, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "3U'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 111, 112, 113, 114, 115, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 36, 37, 38, 39, 40, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 61, 62, 63, 64, 65, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 86, 87, 88, 89, 90, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "3U2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 86, 87, 88, 89, 90, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 111, 112, 113, 114, 115, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 36, 37, 38, 39, 40, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 61, 62, 63, 64, 65, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "B": ( 0, 80, 85, 90, 95, 100, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 5, 27, 28, 29, 30, 4, 32, 33, 34, 35, 3, 37, 38, 39, 40, 2, 42, 43, 44, 45, 1, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 150, 81, 82, 83, 84, 149, 86, 87, 88, 89, 148, 91, 92, 93, 94, 147, 96, 97, 98, 99, 146, 121, 116, 111, 106, 101, 122, 117, 112, 107, 102, 123, 118, 113, 108, 103, 124, 119, 114, 109, 104, 125, 120, 115, 110, 105, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 26, 31, 36, 41, 46,), "B'": ( 0, 46, 41, 36, 31, 26, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 146, 27, 28, 29, 30, 147, 32, 33, 34, 35, 148, 37, 38, 39, 40, 149, 42, 43, 44, 45, 150, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 1, 81, 82, 83, 84, 2, 86, 87, 88, 89, 3, 91, 92, 93, 94, 4, 96, 97, 98, 99, 5, 105, 110, 115, 120, 125, 104, 109, 114, 119, 124, 103, 108, 113, 118, 123, 102, 107, 112, 117, 122, 101, 106, 111, 116, 121, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 100, 95, 90, 85, 80,), "B2": ( 0, 150, 149, 148, 147, 146, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 100, 27, 28, 29, 30, 95, 32, 33, 34, 35, 90, 37, 38, 39, 40, 85, 42, 43, 44, 45, 80, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 46, 81, 82, 83, 84, 41, 86, 87, 88, 89, 36, 91, 92, 93, 94, 31, 96, 97, 98, 99, 26, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 5, 4, 3, 2, 1,), "Bw": ( 0, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 5, 10, 28, 29, 30, 4, 9, 33, 34, 35, 3, 8, 38, 39, 40, 2, 7, 43, 44, 45, 1, 6, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 145, 150, 81, 82, 83, 144, 149, 86, 87, 88, 143, 148, 91, 92, 93, 142, 147, 96, 97, 98, 141, 146, 121, 116, 111, 106, 101, 122, 117, 112, 107, 102, 123, 118, 113, 108, 103, 124, 119, 114, 109, 104, 125, 120, 115, 110, 105, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46,), "Bw'": ( 0, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 146, 141, 28, 29, 30, 147, 142, 33, 34, 35, 148, 143, 38, 39, 40, 149, 144, 43, 44, 45, 150, 145, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 6, 1, 81, 82, 83, 7, 2, 86, 87, 88, 8, 3, 91, 92, 93, 9, 4, 96, 97, 98, 10, 5, 105, 110, 115, 120, 125, 104, 109, 114, 119, 124, 103, 108, 113, 118, 123, 102, 107, 112, 117, 122, 101, 106, 111, 116, 121, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80,), "Bw2": ( 0, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 100, 99, 28, 29, 30, 95, 94, 33, 34, 35, 90, 89, 38, 39, 40, 85, 84, 43, 44, 45, 80, 79, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 47, 46, 81, 82, 83, 42, 41, 86, 87, 88, 37, 36, 91, 92, 93, 32, 31, 96, 97, 98, 27, 26, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,), "D": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 121, 122, 123, 124, 125, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 46, 47, 48, 49, 50, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 71, 72, 73, 74, 75, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 96, 97, 98, 99, 100, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130,), "D'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 71, 72, 73, 74, 75, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 96, 97, 98, 99, 100, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 121, 122, 123, 124, 125, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 46, 47, 48, 49, 50, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146,), "D2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 96, 97, 98, 99, 100, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 121, 122, 123, 124, 125, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 46, 47, 48, 49, 50, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 71, 72, 73, 74, 75, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126,), "Dw": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130,), "Dw'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146,), "Dw2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126,), "F": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 50, 45, 40, 35, 30, 26, 27, 28, 29, 126, 31, 32, 33, 34, 127, 36, 37, 38, 39, 128, 41, 42, 43, 44, 129, 46, 47, 48, 49, 130, 71, 66, 61, 56, 51, 72, 67, 62, 57, 52, 73, 68, 63, 58, 53, 74, 69, 64, 59, 54, 75, 70, 65, 60, 55, 21, 77, 78, 79, 80, 22, 82, 83, 84, 85, 23, 87, 88, 89, 90, 24, 92, 93, 94, 95, 25, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 96, 91, 86, 81, 76, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "F'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 76, 81, 86, 91, 96, 26, 27, 28, 29, 25, 31, 32, 33, 34, 24, 36, 37, 38, 39, 23, 41, 42, 43, 44, 22, 46, 47, 48, 49, 21, 55, 60, 65, 70, 75, 54, 59, 64, 69, 74, 53, 58, 63, 68, 73, 52, 57, 62, 67, 72, 51, 56, 61, 66, 71, 130, 77, 78, 79, 80, 129, 82, 83, 84, 85, 128, 87, 88, 89, 90, 127, 92, 93, 94, 95, 126, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 30, 35, 40, 45, 50, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "F2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 130, 129, 128, 127, 126, 26, 27, 28, 29, 96, 31, 32, 33, 34, 91, 36, 37, 38, 39, 86, 41, 42, 43, 44, 81, 46, 47, 48, 49, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 77, 78, 79, 80, 45, 82, 83, 84, 85, 40, 87, 88, 89, 90, 35, 92, 93, 94, 95, 30, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 25, 24, 23, 22, 21, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "Fw": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 26, 27, 28, 131, 126, 31, 32, 33, 132, 127, 36, 37, 38, 133, 128, 41, 42, 43, 134, 129, 46, 47, 48, 135, 130, 71, 66, 61, 56, 51, 72, 67, 62, 57, 52, 73, 68, 63, 58, 53, 74, 69, 64, 59, 54, 75, 70, 65, 60, 55, 21, 16, 78, 79, 80, 22, 17, 83, 84, 85, 23, 18, 88, 89, 90, 24, 19, 93, 94, 95, 25, 20, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "Fw'": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 26, 27, 28, 20, 25, 31, 32, 33, 19, 24, 36, 37, 38, 18, 23, 41, 42, 43, 17, 22, 46, 47, 48, 16, 21, 55, 60, 65, 70, 75, 54, 59, 64, 69, 74, 53, 58, 63, 68, 73, 52, 57, 62, 67, 72, 51, 56, 61, 66, 71, 130, 135, 78, 79, 80, 129, 134, 83, 84, 85, 128, 133, 88, 89, 90, 127, 132, 93, 94, 95, 126, 131, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "Fw2": ( 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 26, 27, 28, 97, 96, 31, 32, 33, 92, 91, 36, 37, 38, 87, 86, 41, 42, 43, 82, 81, 46, 47, 48, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 78, 79, 80, 45, 44, 83, 84, 85, 40, 39, 88, 89, 90, 35, 34, 93, 94, 95, 30, 29, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "L": ( 0, 125, 2, 3, 4, 5, 120, 7, 8, 9, 10, 115, 12, 13, 14, 15, 110, 17, 18, 19, 20, 105, 22, 23, 24, 25, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 1, 52, 53, 54, 55, 6, 57, 58, 59, 60, 11, 62, 63, 64, 65, 16, 67, 68, 69, 70, 21, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 146, 106, 107, 108, 109, 141, 111, 112, 113, 114, 136, 116, 117, 118, 119, 131, 121, 122, 123, 124, 126, 51, 127, 128, 129, 130, 56, 132, 133, 134, 135, 61, 137, 138, 139, 140, 66, 142, 143, 144, 145, 71, 147, 148, 149, 150,), "L'": ( 0, 51, 2, 3, 4, 5, 56, 7, 8, 9, 10, 61, 12, 13, 14, 15, 66, 17, 18, 19, 20, 71, 22, 23, 24, 25, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46, 126, 52, 53, 54, 55, 131, 57, 58, 59, 60, 136, 62, 63, 64, 65, 141, 67, 68, 69, 70, 146, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 21, 106, 107, 108, 109, 16, 111, 112, 113, 114, 11, 116, 117, 118, 119, 6, 121, 122, 123, 124, 1, 125, 127, 128, 129, 130, 120, 132, 133, 134, 135, 115, 137, 138, 139, 140, 110, 142, 143, 144, 145, 105, 147, 148, 149, 150,), "L2": ( 0, 126, 2, 3, 4, 5, 131, 7, 8, 9, 10, 136, 12, 13, 14, 15, 141, 17, 18, 19, 20, 146, 22, 23, 24, 25, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 125, 52, 53, 54, 55, 120, 57, 58, 59, 60, 115, 62, 63, 64, 65, 110, 67, 68, 69, 70, 105, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 71, 106, 107, 108, 109, 66, 111, 112, 113, 114, 61, 116, 117, 118, 119, 56, 121, 122, 123, 124, 51, 1, 127, 128, 129, 130, 6, 132, 133, 134, 135, 11, 137, 138, 139, 140, 16, 142, 143, 144, 145, 21, 147, 148, 149, 150,), "Lw": ( 0, 125, 124, 3, 4, 5, 120, 119, 8, 9, 10, 115, 114, 13, 14, 15, 110, 109, 18, 19, 20, 105, 104, 23, 24, 25, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 1, 2, 53, 54, 55, 6, 7, 58, 59, 60, 11, 12, 63, 64, 65, 16, 17, 68, 69, 70, 21, 22, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 147, 146, 106, 107, 108, 142, 141, 111, 112, 113, 137, 136, 116, 117, 118, 132, 131, 121, 122, 123, 127, 126, 51, 52, 128, 129, 130, 56, 57, 133, 134, 135, 61, 62, 138, 139, 140, 66, 67, 143, 144, 145, 71, 72, 148, 149, 150,), "Lw'": ( 0, 51, 52, 3, 4, 5, 56, 57, 8, 9, 10, 61, 62, 13, 14, 15, 66, 67, 18, 19, 20, 71, 72, 23, 24, 25, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46, 126, 127, 53, 54, 55, 131, 132, 58, 59, 60, 136, 137, 63, 64, 65, 141, 142, 68, 69, 70, 146, 147, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 22, 21, 106, 107, 108, 17, 16, 111, 112, 113, 12, 11, 116, 117, 118, 7, 6, 121, 122, 123, 2, 1, 125, 124, 128, 129, 130, 120, 119, 133, 134, 135, 115, 114, 138, 139, 140, 110, 109, 143, 144, 145, 105, 104, 148, 149, 150,), "Lw2": ( 0, 126, 127, 3, 4, 5, 131, 132, 8, 9, 10, 136, 137, 13, 14, 15, 141, 142, 18, 19, 20, 146, 147, 23, 24, 25, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 125, 124, 53, 54, 55, 120, 119, 58, 59, 60, 115, 114, 63, 64, 65, 110, 109, 68, 69, 70, 105, 104, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 72, 71, 106, 107, 108, 67, 66, 111, 112, 113, 62, 61, 116, 117, 118, 57, 56, 121, 122, 123, 52, 51, 1, 2, 128, 129, 130, 6, 7, 133, 134, 135, 11, 12, 138, 139, 140, 16, 17, 143, 144, 145, 21, 22, 148, 149, 150,), "R": ( 0, 1, 2, 3, 4, 55, 6, 7, 8, 9, 60, 11, 12, 13, 14, 65, 16, 17, 18, 19, 70, 21, 22, 23, 24, 75, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 130, 56, 57, 58, 59, 135, 61, 62, 63, 64, 140, 66, 67, 68, 69, 145, 71, 72, 73, 74, 150, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80, 25, 102, 103, 104, 105, 20, 107, 108, 109, 110, 15, 112, 113, 114, 115, 10, 117, 118, 119, 120, 5, 122, 123, 124, 125, 126, 127, 128, 129, 121, 131, 132, 133, 134, 116, 136, 137, 138, 139, 111, 141, 142, 143, 144, 106, 146, 147, 148, 149, 101,), "R'": ( 0, 1, 2, 3, 4, 121, 6, 7, 8, 9, 116, 11, 12, 13, 14, 111, 16, 17, 18, 19, 106, 21, 22, 23, 24, 101, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 5, 56, 57, 58, 59, 10, 61, 62, 63, 64, 15, 66, 67, 68, 69, 20, 71, 72, 73, 74, 25, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 150, 102, 103, 104, 105, 145, 107, 108, 109, 110, 140, 112, 113, 114, 115, 135, 117, 118, 119, 120, 130, 122, 123, 124, 125, 126, 127, 128, 129, 55, 131, 132, 133, 134, 60, 136, 137, 138, 139, 65, 141, 142, 143, 144, 70, 146, 147, 148, 149, 75,), "R2": ( 0, 1, 2, 3, 4, 130, 6, 7, 8, 9, 135, 11, 12, 13, 14, 140, 16, 17, 18, 19, 145, 21, 22, 23, 24, 150, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 121, 56, 57, 58, 59, 116, 61, 62, 63, 64, 111, 66, 67, 68, 69, 106, 71, 72, 73, 74, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 102, 103, 104, 105, 70, 107, 108, 109, 110, 65, 112, 113, 114, 115, 60, 117, 118, 119, 120, 55, 122, 123, 124, 125, 126, 127, 128, 129, 5, 131, 132, 133, 134, 10, 136, 137, 138, 139, 15, 141, 142, 143, 144, 20, 146, 147, 148, 149, 25,), "Rw": ( 0, 1, 2, 3, 54, 55, 6, 7, 8, 59, 60, 11, 12, 13, 64, 65, 16, 17, 18, 69, 70, 21, 22, 23, 74, 75, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 129, 130, 56, 57, 58, 134, 135, 61, 62, 63, 139, 140, 66, 67, 68, 144, 145, 71, 72, 73, 149, 150, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80, 25, 24, 103, 104, 105, 20, 19, 108, 109, 110, 15, 14, 113, 114, 115, 10, 9, 118, 119, 120, 5, 4, 123, 124, 125, 126, 127, 128, 122, 121, 131, 132, 133, 117, 116, 136, 137, 138, 112, 111, 141, 142, 143, 107, 106, 146, 147, 148, 102, 101,), "Rw'": ( 0, 1, 2, 3, 122, 121, 6, 7, 8, 117, 116, 11, 12, 13, 112, 111, 16, 17, 18, 107, 106, 21, 22, 23, 102, 101, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 4, 5, 56, 57, 58, 9, 10, 61, 62, 63, 14, 15, 66, 67, 68, 19, 20, 71, 72, 73, 24, 25, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 150, 149, 103, 104, 105, 145, 144, 108, 109, 110, 140, 139, 113, 114, 115, 135, 134, 118, 119, 120, 130, 129, 123, 124, 125, 126, 127, 128, 54, 55, 131, 132, 133, 59, 60, 136, 137, 138, 64, 65, 141, 142, 143, 69, 70, 146, 147, 148, 74, 75,), "Rw2": ( 0, 1, 2, 3, 129, 130, 6, 7, 8, 134, 135, 11, 12, 13, 139, 140, 16, 17, 18, 144, 145, 21, 22, 23, 149, 150, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 122, 121, 56, 57, 58, 117, 116, 61, 62, 63, 112, 111, 66, 67, 68, 107, 106, 71, 72, 73, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 103, 104, 105, 70, 69, 108, 109, 110, 65, 64, 113, 114, 115, 60, 59, 118, 119, 120, 55, 54, 123, 124, 125, 126, 127, 128, 4, 5, 131, 132, 133, 9, 10, 136, 137, 138, 14, 15, 141, 142, 143, 19, 20, 146, 147, 148, 24, 25,), "U": ( 0, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 51, 52, 53, 54, 55, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 76, 77, 78, 79, 80, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 101, 102, 103, 104, 105, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 26, 27, 28, 29, 30, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "U'": ( 0, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 101, 102, 103, 104, 105, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 26, 27, 28, 29, 30, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 51, 52, 53, 54, 55, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 76, 77, 78, 79, 80, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "U2": ( 0, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 76, 77, 78, 79, 80, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 101, 102, 103, 104, 105, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 26, 27, 28, 29, 30, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 51, 52, 53, 54, 55, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "Uw": ( 0, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "Uw'": ( 0, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "Uw2": ( 0, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,), "x": ( 0, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101,), "x'": ( 0, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75,), "x2": ( 0, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,), "y": ( 0, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146,), "y'": ( 0, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130,), "y2": ( 0, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126,), "z": ( 0, 46, 41, 36, 31, 26, 47, 42, 37, 32, 27, 48, 43, 38, 33, 28, 49, 44, 39, 34, 29, 50, 45, 40, 35, 30, 146, 141, 136, 131, 126, 147, 142, 137, 132, 127, 148, 143, 138, 133, 128, 149, 144, 139, 134, 129, 150, 145, 140, 135, 130, 71, 66, 61, 56, 51, 72, 67, 62, 57, 52, 73, 68, 63, 58, 53, 74, 69, 64, 59, 54, 75, 70, 65, 60, 55, 21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5, 105, 110, 115, 120, 125, 104, 109, 114, 119, 124, 103, 108, 113, 118, 123, 102, 107, 112, 117, 122, 101, 106, 111, 116, 121, 96, 91, 86, 81, 76, 97, 92, 87, 82, 77, 98, 93, 88, 83, 78, 99, 94, 89, 84, 79, 100, 95, 90, 85, 80,), "z'": ( 0, 80, 85, 90, 95, 100, 79, 84, 89, 94, 99, 78, 83, 88, 93, 98, 77, 82, 87, 92, 97, 76, 81, 86, 91, 96, 5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21, 55, 60, 65, 70, 75, 54, 59, 64, 69, 74, 53, 58, 63, 68, 73, 52, 57, 62, 67, 72, 51, 56, 61, 66, 71, 130, 135, 140, 145, 150, 129, 134, 139, 144, 149, 128, 133, 138, 143, 148, 127, 132, 137, 142, 147, 126, 131, 136, 141, 146, 121, 116, 111, 106, 101, 122, 117, 112, 107, 102, 123, 118, 113, 108, 103, 124, 119, 114, 109, 104, 125, 120, 115, 110, 105, 30, 35, 40, 45, 50, 29, 34, 39, 44, 49, 28, 33, 38, 43, 48, 27, 32, 37, 42, 47, 26, 31, 36, 41, 46,), "z2": ( 0, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,), }

def rotate_555(cube, step):
    return [cube[x] for x in swaps_555[step]]
