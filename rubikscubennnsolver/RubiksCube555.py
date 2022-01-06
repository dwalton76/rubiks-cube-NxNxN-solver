# standard libraries
import itertools
import logging
from typing import List

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube, reverse_steps, wing_str_map, wing_strs_all
from rubikscubennnsolver.LookupTable import LookupTable
from rubikscubennnsolver.LookupTableIDAViaGraph import LookupTableIDAViaGraph
from rubikscubennnsolver.misc import SolveError
from rubikscubennnsolver.RubiksCubeHighLow import highlow_edge_values_555
from rubikscubennnsolver.swaps import swaps_555

logger = logging.getLogger(__name__)

# fmt: off
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

dead_centers = [13, 38, 63, 88, 113, 138]

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

UFBD_t_centers_555 = (
    8, 12, 14, 18,  # Upper
    58, 62, 64, 68,  # Front
    108, 112, 114, 118,  # Back
    133, 137, 139, 143,  # Down
)

UFBD_x_centers_555 = (
    7, 9, 17, 19,  # Upper
    57, 59, 67, 69,  # Front
    107, 109, 117, 119,  # Back
    132, 134, 142, 144,  # Down
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


"""
000 000 000 011 111 111 112 222 222 222 333 333
012 345 678 901 234 567 890 123 456 789 012 345
OOo pPP QQq rRR sSS TTt uUU VVv WWw xXX YYy zZZ
 ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^
 UB  UL  UR  UD  LB  LF  RF  RB  DF  DL  DR  DB
"""
edge_orbit_0_555 = (
    2, 4, 10, 20, 24, 22, 16, 6,  # Upper
    27, 29, 35, 45, 49, 47, 41, 31,  # Left
    52, 54, 60, 70, 74, 72, 66, 56,  # Front
    77, 79, 85, 95, 99, 97, 91, 81,  # Right
    102, 104, 110, 120, 124, 122, 116, 106,  # Back
    127, 129, 135, 145, 149, 147, 141, 131,  # Down
)

edge_orbit_1_555 = (
    3, 15, 23, 11,  # Upper
    28, 40, 48, 36,  # Left
    53, 65, 73, 61,  # Front
    78, 90, 98, 86,  # Right
    103, 115, 123, 111,  # Back
    128, 140, 148, 136,  # Down
)

corners_555 = (
    1, 5, 21, 25,  # Upper
    26, 30, 46, 50,  # Left
    51, 55, 71, 75,  # Front
    76, 80, 96, 100,  # Right
    101, 105, 121, 125,  # Back
    126, 130, 146, 150,  # Down
)

edges_555 = (
    2, 3, 4, 6, 10, 11, 15, 16, 20, 22, 23, 24,  # Upper
    27, 28, 29, 31, 35, 36, 40, 41, 45, 47, 48, 49,  # Left
    52, 53, 54, 56, 60, 61, 65, 66, 70, 72, 73, 74,  # Front
    77, 78, 79, 81, 85, 86, 90, 91, 95, 97, 98, 99,  # Right
    102, 103, 104, 106, 110, 111, 115, 116, 120, 122, 123, 124,  # Back
    127, 128, 129, 131, 135, 136, 140, 141, 145, 147, 148, 149,  # Down
)

set_edges_555 = set(edges_555)

wings_555 = (
    2, 3, 4, 6, 11, 16, 10, 15, 20, 22, 23, 24,  # Upper
    31, 36, 41, 35, 40, 45,  # Left
    81, 86, 91, 85, 90, 95,  # Right
    127, 128, 129, 131, 136, 141, 135, 140, 145, 147, 148, 149,  # Down
)

l4e_wings_555 = (
    2, 3, 4, 6, 11, 16, 10, 15, 20, 22, 23, 24,  # Upper
    31, 36, 41, 35, 40, 45,  # Left
    81, 86, 91, 85, 90, 95,  # Right
    127, 128, 129, 131, 136, 141, 135, 140, 145, 147, 148, 149,  # Down
)

wings_for_edges_pattern_555 = (
    2, 3, 4, 6, 11, 16, 10, 15, 20, 22, 23, 24,  # Upper
    31, 36, 41, 35, 40, 45,  # Left
    81, 86, 91, 85, 90, 95,  # Right
    127, 128, 129, 131, 136, 141, 135, 140, 145, 147, 148, 149,  # Down
)

high_wings_and_midges_555 = (
    2, 3, 11, 16, 10, 15, 23, 24,  # Upper
    36, 41, 35, 40,  # Left
    86, 91, 85, 90,  # Right
    127, 128, 136, 141, 135, 140, 148, 149,  # Down
)

low_wings_and_midges_555 = (
    3, 4, 6, 11, 15, 20, 22, 23,  # Upper
    31, 36, 40, 45,  # Left
    81, 86, 90, 95,  # Right
    128, 129, 131, 136, 140, 145, 147, 148,  # Down
)

high_edges_555 = (
    (2, 104),  # Upper
    (10, 79),
    (24, 54),
    (16, 29),
    (35, 56),  # Left
    (41, 120),
    (85, 106),  # Right
    (91, 70),
    (127, 72),  # Down
    (135, 97),
    (149, 122),
    (141, 47),
)

low_edges_555 = (
    (4, 102),  # Upper
    (20, 77),
    (22, 52),
    (6, 27),
    (31, 110),  # Left
    (45, 66),
    (81, 60),  # Right
    (95, 116),
    (129, 74),  # Down
    (145, 99),
    (147, 124),
    (131, 49),
)


edges_partner_555 = {
    2: 104,  # Upper
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
    27: 6,  # Left
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
    52: 22,  # Front
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
    77: 20,  # Right
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
    102: 4,  # Back
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
    127: 72,  # Down
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


edges_recolor_tuples_555 = (
    ("0", 2, 104),  # Upper
    ("1", 4, 102),
    ("2", 6, 27),
    ("3", 10, 79),
    ("4", 16, 29),
    ("5", 20, 77),
    ("6", 22, 52),
    ("7", 24, 54),
    ("8", 31, 110),  # Left
    ("9", 35, 56),
    ("a", 41, 120),
    ("b", 45, 66),
    ("c", 81, 60),  # Right
    ("d", 85, 106),
    ("e", 91, 70),
    ("f", 95, 116),
    ("g", 127, 72),  # Down
    ("h", 129, 74),
    ("i", 131, 49),
    ("j", 135, 97),
    ("k", 141, 47),
    ("l", 145, 99),
    ("m", 147, 124),
    ("n", 149, 122),
)

midges_recolor_tuples_555 = (
    ("o", 3, 103),  # Upper
    ("p", 11, 28),
    ("q", 15, 78),
    ("r", 23, 53),
    ("s", 36, 115),  # Left
    ("t", 40, 61),
    ("u", 86, 65),  # Right
    ("v", 90, 111),
    ("w", 128, 73),  # Down
    ("x", 136, 48),
    ("y", 140, 98),
    ("z", 148, 123),
)

midge_indexes = (
    3, 11, 15, 23,  # Upper
    28, 36, 40, 48,  # Left
    53, 61, 65, 73,  # Front
    78, 86, 90, 98,  # Right
    103, 111, 115, 123,  # Back
    128, 136, 140, 148,  # Down
)

wings_for_recolor_555 = (
    ("0", 2, 104),  # Upper
    ("1", 4, 102),
    ("2", 6, 27),
    ("3", 10, 79),
    ("4", 16, 29),
    ("5", 20, 77),
    ("6", 22, 52),
    ("7", 24, 54),
    ("8", 31, 110),  # Left
    ("9", 35, 56),
    ("a", 41, 120),
    ("b", 45, 66),
    ("c", 81, 60),  # Right
    ("d", 85, 106),
    ("e", 91, 70),
    ("f", 95, 116),
    ("g", 127, 72),  # Down
    ("h", 129, 74),
    ("i", 131, 49),
    ("j", 135, 97),
    ("k", 141, 47),
    ("l", 145, 99),
    ("m", 147, 124),
    ("n", 149, 122),
)

MIDGE_TUPLES_555 = (
    ((3, 103), (103, 3)),  # Upper
    ((11, 28), (28, 11)),
    ((15, 78), (78, 15)),
    ((23, 53), (53, 23)),
    ((36, 115), (115, 36)),  # Left
    ((40, 61), (61, 40)),
    ((86, 65), (65, 86)),  # Right
    ((90, 111), (111, 90)),
    ((128, 73), (73, 128)),  # Down
    ((136, 48), (48, 136)),
    ((140, 98), (98, 140)),
    ((148, 123), (123, 148)),
)

LR_centers_and_midges_555 = (
    3, 11, 15, 23,  # Upper
    28, 32, 33, 34, 36, 37, 38, 39, 40, 42, 43, 44, 48,  # Left
    53, 61, 65, 73,  # Front
    78, 82, 83, 84, 86, 87, 88, 89, 90, 92, 93, 94, 98,  # Right
    103, 111, 115, 123,  # Back
    128, 136, 140, 148,  # Down
)
# fmt: on


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
                high_low = highlow_edge_values_555[(square_index, partner_index, square_value, partner_value)]

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
                high_low = highlow_edge_values_555[(square_index, partner_index, square_value, partner_value)]

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


# phase 1
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

    # fmt: off
    t_centers_555 = (
        8, 12, 14, 18,  # Upper
        33, 37, 39, 43,  # Left
        58, 62, 64, 68,  # Front
        83, 87, 89, 93,  # Right
        108, 112, 114, 118,  # Back
        133, 137, 139, 143,  # Down
    )
    # fmt: on

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step11-LR-centers-stage-t-center-only.txt",
            "0f0f00",
            linecount=735471,
            max_depth=8,
            legal_moves=moves_555,
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        LR_colors = (parent_state[38], parent_state[88])

        if LR_colors == (".", "."):
            LR_colors = ("L", "R")

        state = "".join(["1" if parent_state[x] in LR_colors else "0" for x in self.t_centers_555])
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

    # fmt: off
    x_centers_555 = (
        7, 9, 17, 19,  # Upper
        32, 34, 42, 44,  # Left
        57, 59, 67, 69,  # Front
        82, 84, 92, 94,  # Right
        107, 109, 117, 119,  # Back
        132, 134, 142, 144,  # Down
    )
    # fmt: on

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step12-LR-centers-stage-x-center-only.txt",
            "0f0f00",
            linecount=735471,
            max_depth=8,
            legal_moves=moves_555,
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        LR_colors = (parent_state[38], parent_state[88])

        if LR_colors == (".", "."):
            LR_colors = ("L", "R")

        state = "".join(["1" if parent_state[x] in LR_colors else "0" for x in self.x_centers_555])
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
            prune_tables=(parent.lt_LR_t_centers_stage, parent.lt_LR_x_centers_stage),
            centers_only=True,
            # C_ida_type="5x5x5-lr-centers-stage",
        )


class LookupTableIDA555LRTCenterStage(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=(),
            prune_tables=(parent.lt_LR_t_centers_stage,),
            centers_only=True,
        )


# phase 2
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

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step21-FB-t-centers-stage.txt",
            "0ff0",
            linecount=12870,
            max_depth=9,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Fw", "Fw'", "Bw", "Bw'", "Dw", "Dw'"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        FB_colors = (parent_state[63], parent_state[113])

        if FB_colors == (".", "."):
            FB_colors = ("F", "B")

        state = "".join(["1" if parent_state[x] in FB_colors else "0" for x in UFBD_t_centers_555])
        return self.hex_format % int(state, 2)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        binary_state = bin(int(state, 16))[2:].zfill(16)

        for (pos, pos_state) in zip(UFBD_t_centers_555, binary_state):
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

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step22-FB-x-centers-stage.txt",
            "0ff0",
            linecount=12870,
            max_depth=7,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Fw", "Fw'", "Bw", "Bw'", "Dw", "Dw'"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        FB_colors = (parent_state[63], parent_state[113])

        if FB_colors == (".", "."):
            FB_colors = ("F", "B")

        state = "".join(["1" if parent_state[x] in FB_colors else "0" for x in UFBD_x_centers_555])
        return self.hex_format % int(state, 2)

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        binary_state = bin(int(state, 16))[2:].zfill(16)

        for (pos, pos_state) in zip(UFBD_x_centers_555, binary_state):
            if pos_state == "0":
                cube[pos] = "x"
            else:
                cube[pos] = "F"


class LookupTable555Phase2LRCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step23-LR-center-stage.txt
    =============================================
    0 steps has 27 entries (0 percent, 0.00x previous step)
    1 steps has 801 entries (16 percent, 29.67x previous step)
    2 steps has 1,064 entries (21 percent, 1.33x previous step)
    3 steps has 1,692 entries (34 percent, 1.59x previous step)
    4 steps has 1,220 entries (24 percent, 0.72x previous step)
    5 steps has 96 entries (1 percent, 0.08x previous step)

    Total: 4,900 entries
    Average: 2.73 moves
    """

    state_targets = (
        "LLLLLLLLLRRRRRRRRR",
        "LLLLLLLRLRLRRRRRRR",
        "LLLLLLLRLRRRRRRRLR",
        "LLLLLLRLRLRLRRRRRR",
        "LLLLLLRLRRRRRRRLRL",
        "LLLLLLRRRLLLRRRRRR",
        "LLLLLLRRRLRLRRRRLR",
        "LLLLLLRRRRLRRRRLRL",
        "LLLLLLRRRRRRRRRLLL",
        "LLLLLRLLLRRRLRRRRR",
        "LLLLLRLLLRRRRRLRRR",
        "LLLLLRLRLRLRLRRRRR",
        "LLLLLRLRLRLRRRLRRR",
        "LLLLLRLRLRRRLRRRLR",
        "LLLLLRLRLRRRRRLRLR",
        "LLLLLRRLRLRLLRRRRR",
        "LLLLLRRLRLRLRRLRRR",
        "LLLLLRRLRRRRLRRLRL",
        "LLLLLRRLRRRRRRLLRL",
        "LLLLLRRRRLLLLRRRRR",
        "LLLLLRRRRLLLRRLRRR",
        "LLLLLRRRRLRLLRRRLR",
        "LLLLLRRRRLRLRRLRLR",
        "LLLLLRRRRRLRLRRLRL",
        "LLLLLRRRRRLRRRLLRL",
        "LLLLLRRRRRRRLRRLLL",
        "LLLLLRRRRRRRRRLLLL",
        "LLLRLLLLLRRRLRRRRR",
        "LLLRLLLLLRRRRRLRRR",
        "LLLRLLLRLRLRLRRRRR",
        "LLLRLLLRLRLRRRLRRR",
        "LLLRLLLRLRRRLRRRLR",
        "LLLRLLLRLRRRRRLRLR",
        "LLLRLLRLRLRLLRRRRR",
        "LLLRLLRLRLRLRRLRRR",
        "LLLRLLRLRRRRLRRLRL",
        "LLLRLLRLRRRRRRLLRL",
        "LLLRLLRRRLLLLRRRRR",
        "LLLRLLRRRLLLRRLRRR",
        "LLLRLLRRRLRLLRRRLR",
        "LLLRLLRRRLRLRRLRLR",
        "LLLRLLRRRRLRLRRLRL",
        "LLLRLLRRRRLRRRLLRL",
        "LLLRLLRRRRRRLRRLLL",
        "LLLRLLRRRRRRRRLLLL",
        "LLLRLRLLLRRRLRLRRR",
        "LLLRLRLRLRLRLRLRRR",
        "LLLRLRLRLRRRLRLRLR",
        "LLLRLRRLRLRLLRLRRR",
        "LLLRLRRLRRRRLRLLRL",
        "LLLRLRRRRLLLLRLRRR",
        "LLLRLRRRRLRLLRLRLR",
        "LLLRLRRRRRLRLRLLRL",
        "LLLRLRRRRRRRLRLLLL",
        "LLRLLLLLRLRRRRRLRR",
        "LLRLLLLLRRRLRRRRRL",
        "LLRLLLLRRLLRRRRLRR",
        "LLRLLLLRRLRRRRRLLR",
        "LLRLLLLRRRLLRRRRRL",
        "LLRLLLLRRRRLRRRRLL",
        "LLRLLLRLLRRLRRRLRR",
        "LLRLLLRRLRLLRRRLRR",
        "LLRLLLRRLRRLRRRLLR",
        "LLRLLRLLRLRRLRRLRR",
        "LLRLLRLLRLRRRRLLRR",
        "LLRLLRLLRRRLLRRRRL",
        "LLRLLRLLRRRLRRLRRL",
        "LLRLLRLRRLLRLRRLRR",
        "LLRLLRLRRLLRRRLLRR",
        "LLRLLRLRRLRRLRRLLR",
        "LLRLLRLRRLRRRRLLLR",
        "LLRLLRLRRRLLLRRRRL",
        "LLRLLRLRRRLLRRLRRL",
        "LLRLLRLRRRRLLRRRLL",
        "LLRLLRLRRRRLRRLRLL",
        "LLRLLRRLLRRLLRRLRR",
        "LLRLLRRLLRRLRRLLRR",
        "LLRLLRRRLRLLLRRLRR",
        "LLRLLRRRLRLLRRLLRR",
        "LLRLLRRRLRRLLRRLLR",
        "LLRLLRRRLRRLRRLLLR",
        "LLRRLLLLRLRRLRRLRR",
        "LLRRLLLLRLRRRRLLRR",
        "LLRRLLLLRRRLLRRRRL",
        "LLRRLLLLRRRLRRLRRL",
        "LLRRLLLRRLLRLRRLRR",
        "LLRRLLLRRLLRRRLLRR",
        "LLRRLLLRRLRRLRRLLR",
        "LLRRLLLRRLRRRRLLLR",
        "LLRRLLLRRRLLLRRRRL",
        "LLRRLLLRRRLLRRLRRL",
        "LLRRLLLRRRRLLRRRLL",
        "LLRRLLLRRRRLRRLRLL",
        "LLRRLLRLLRRLLRRLRR",
        "LLRRLLRLLRRLRRLLRR",
        "LLRRLLRRLRLLLRRLRR",
        "LLRRLLRRLRLLRRLLRR",
        "LLRRLLRRLRRLLRRLLR",
        "LLRRLLRRLRRLRRLLLR",
        "LLRRLRLLRLRRLRLLRR",
        "LLRRLRLLRRRLLRLRRL",
        "LLRRLRLRRLLRLRLLRR",
        "LLRRLRLRRLRRLRLLLR",
        "LLRRLRLRRRLLLRLRRL",
        "LLRRLRLRRRRLLRLRLL",
        "LLRRLRRLLRRLLRLLRR",
        "LLRRLRRRLRLLLRLLRR",
        "LLRRLRRRLRRLLRLLLR",
        "LRLLLLLLLRLRRRRRRR",
        "LRLLLLLLLRRRRRRRLR",
        "LRLLLLLRLRLRRRRRLR",
        "LRLLLLRLRLLLRRRRRR",
        "LRLLLLRLRLRLRRRRLR",
        "LRLLLLRLRRLRRRRLRL",
        "LRLLLLRLRRRRRRRLLL",
        "LRLLLLRRRLLLRRRRLR",
        "LRLLLLRRRRLRRRRLLL",
        "LRLLLRLLLRLRLRRRRR",
        "LRLLLRLLLRLRRRLRRR",
        "LRLLLRLLLRRRLRRRLR",
        "LRLLLRLLLRRRRRLRLR",
        "LRLLLRLRLRLRLRRRLR",
        "LRLLLRLRLRLRRRLRLR",
        "LRLLLRRLRLLLLRRRRR",
        "LRLLLRRLRLLLRRLRRR",
        "LRLLLRRLRLRLLRRRLR",
        "LRLLLRRLRLRLRRLRLR",
        "LRLLLRRLRRLRLRRLRL",
        "LRLLLRRLRRLRRRLLRL",
        "LRLLLRRLRRRRLRRLLL",
        "LRLLLRRLRRRRRRLLLL",
        "LRLLLRRRRLLLLRRRLR",
        "LRLLLRRRRLLLRRLRLR",
        "LRLLLRRRRRLRLRRLLL",
        "LRLLLRRRRRLRRRLLLL",
        "LRLRLLLLLRLRLRRRRR",
        "LRLRLLLLLRLRRRLRRR",
        "LRLRLLLLLRRRLRRRLR",
        "LRLRLLLLLRRRRRLRLR",
        "LRLRLLLRLRLRLRRRLR",
        "LRLRLLLRLRLRRRLRLR",
        "LRLRLLRLRLLLLRRRRR",
        "LRLRLLRLRLLLRRLRRR",
        "LRLRLLRLRLRLLRRRLR",
        "LRLRLLRLRLRLRRLRLR",
        "LRLRLLRLRRLRLRRLRL",
        "LRLRLLRLRRLRRRLLRL",
        "LRLRLLRLRRRRLRRLLL",
        "LRLRLLRLRRRRRRLLLL",
        "LRLRLLRRRLLLLRRRLR",
        "LRLRLLRRRLLLRRLRLR",
        "LRLRLLRRRRLRLRRLLL",
        "LRLRLLRRRRLRRRLLLL",
        "LRLRLRLLLRLRLRLRRR",
        "LRLRLRLLLRRRLRLRLR",
        "LRLRLRLRLRLRLRLRLR",
        "LRLRLRRLRLLLLRLRRR",
        "LRLRLRRLRLRLLRLRLR",
        "LRLRLRRLRRLRLRLLRL",
        "LRLRLRRLRRRRLRLLLL",
        "LRLRLRRRRLLLLRLRLR",
        "LRLRLRRRRRLRLRLLLL",
        "LRRLLLLLRLLRRRRLRR",
        "LRRLLLLLRLRRRRRLLR",
        "LRRLLLLLRRLLRRRRRL",
        "LRRLLLLLRRRLRRRRLL",
        "LRRLLLLRRLLRRRRLLR",
        "LRRLLLLRRRLLRRRRLL",
        "LRRLLLRLLRLLRRRLRR",
        "LRRLLLRLLRRLRRRLLR",
        "LRRLLLRRLRLLRRRLLR",
        "LRRLLRLLRLLRLRRLRR",
        "LRRLLRLLRLLRRRLLRR",
        "LRRLLRLLRLRRLRRLLR",
        "LRRLLRLLRLRRRRLLLR",
        "LRRLLRLLRRLLLRRRRL",
        "LRRLLRLLRRLLRRLRRL",
        "LRRLLRLLRRRLLRRRLL",
        "LRRLLRLLRRRLRRLRLL",
        "LRRLLRLRRLLRLRRLLR",
        "LRRLLRLRRLLRRRLLLR",
        "LRRLLRLRRRLLLRRRLL",
        "LRRLLRLRRRLLRRLRLL",
        "LRRLLRRLLRLLLRRLRR",
        "LRRLLRRLLRLLRRLLRR",
        "LRRLLRRLLRRLLRRLLR",
        "LRRLLRRLLRRLRRLLLR",
        "LRRLLRRRLRLLLRRLLR",
        "LRRLLRRRLRLLRRLLLR",
        "LRRRLLLLRLLRLRRLRR",
        "LRRRLLLLRLLRRRLLRR",
        "LRRRLLLLRLRRLRRLLR",
        "LRRRLLLLRLRRRRLLLR",
        "LRRRLLLLRRLLLRRRRL",
        "LRRRLLLLRRLLRRLRRL",
        "LRRRLLLLRRRLLRRRLL",
        "LRRRLLLLRRRLRRLRLL",
        "LRRRLLLRRLLRLRRLLR",
        "LRRRLLLRRLLRRRLLLR",
        "LRRRLLLRRRLLLRRRLL",
        "LRRRLLLRRRLLRRLRLL",
        "LRRRLLRLLRLLLRRLRR",
        "LRRRLLRLLRLLRRLLRR",
        "LRRRLLRLLRRLLRRLLR",
        "LRRRLLRLLRRLRRLLLR",
        "LRRRLLRRLRLLLRRLLR",
        "LRRRLLRRLRLLRRLLLR",
        "LRRRLRLLRLLRLRLLRR",
        "LRRRLRLLRLRRLRLLLR",
        "LRRRLRLLRRLLLRLRRL",
        "LRRRLRLLRRRLLRLRLL",
        "LRRRLRLRRLLRLRLLLR",
        "LRRRLRLRRRLLLRLRLL",
        "LRRRLRRLLRLLLRLLRR",
        "LRRRLRRLLRRLLRLLLR",
        "LRRRLRRRLRLLLRLLLR",
        "RLLLLLLLRLRRRRRRRL",
        "RLLLLLLRRLLRRRRRRL",
        "RLLLLLLRRLRRRRRRLL",
        "RLLLLLRLLLRRRRRLRR",
        "RLLLLLRLLRRLRRRRRL",
        "RLLLLLRRLLLRRRRLRR",
        "RLLLLLRRLLRRRRRLLR",
        "RLLLLLRRLRLLRRRRRL",
        "RLLLLLRRLRRLRRRRLL",
        "RLLLLRLLRLRRLRRRRL",
        "RLLLLRLLRLRRRRLRRL",
        "RLLLLRLRRLLRLRRRRL",
        "RLLLLRLRRLLRRRLRRL",
        "RLLLLRLRRLRRLRRRLL",
        "RLLLLRLRRLRRRRLRLL",
        "RLLLLRRLLLRRLRRLRR",
        "RLLLLRRLLLRRRRLLRR",
        "RLLLLRRLLRRLLRRRRL",
        "RLLLLRRLLRRLRRLRRL",
        "RLLLLRRRLLLRLRRLRR",
        "RLLLLRRRLLLRRRLLRR",
        "RLLLLRRRLLRRLRRLLR",
        "RLLLLRRRLLRRRRLLLR",
        "RLLLLRRRLRLLLRRRRL",
        "RLLLLRRRLRLLRRLRRL",
        "RLLLLRRRLRRLLRRRLL",
        "RLLLLRRRLRRLRRLRLL",
        "RLLRLLLLRLRRLRRRRL",
        "RLLRLLLLRLRRRRLRRL",
        "RLLRLLLRRLLRLRRRRL",
        "RLLRLLLRRLLRRRLRRL",
        "RLLRLLLRRLRRLRRRLL",
        "RLLRLLLRRLRRRRLRLL",
        "RLLRLLRLLLRRLRRLRR",
        "RLLRLLRLLLRRRRLLRR",
        "RLLRLLRLLRRLLRRRRL",
        "RLLRLLRLLRRLRRLRRL",
        "RLLRLLRRLLLRLRRLRR",
        "RLLRLLRRLLLRRRLLRR",
        "RLLRLLRRLLRRLRRLLR",
        "RLLRLLRRLLRRRRLLLR",
        "RLLRLLRRLRLLLRRRRL",
        "RLLRLLRRLRLLRRLRRL",
        "RLLRLLRRLRRLLRRRLL",
        "RLLRLLRRLRRLRRLRLL",
        "RLLRLRLLRLRRLRLRRL",
        "RLLRLRLRRLLRLRLRRL",
        "RLLRLRLRRLRRLRLRLL",
        "RLLRLRRLLLRRLRLLRR",
        "RLLRLRRLLRRLLRLRRL",
        "RLLRLRRRLLLRLRLLRR",
        "RLLRLRRRLLRRLRLLLR",
        "RLLRLRRRLRLLLRLRRL",
        "RLLRLRRRLRRLLRLRLL",
        "RLRLLLLLLLRLRRRRRR",
        "RLRLLLLLLRRRRRRLRL",
        "RLRLLLLRLLLLRRRRRR",
        "RLRLLLLRLLRLRRRRLR",
        "RLRLLLLRLRLRRRRLRL",
        "RLRLLLLRLRRRRRRLLL",
        "RLRLLLRLRLRLRRRLRL",
        "RLRLLLRRRLLLRRRLRL",
        "RLRLLLRRRLRLRRRLLL",
        "RLRLLRLLLLRLLRRRRR",
        "RLRLLRLLLLRLRRLRRR",
        "RLRLLRLLLRRRLRRLRL",
        "RLRLLRLLLRRRRRLLRL",
        "RLRLLRLRLLLLLRRRRR",
        "RLRLLRLRLLLLRRLRRR",
        "RLRLLRLRLLRLLRRRLR",
        "RLRLLRLRLLRLRRLRLR",
        "RLRLLRLRLRLRLRRLRL",
        "RLRLLRLRLRLRRRLLRL",
        "RLRLLRLRLRRRLRRLLL",
        "RLRLLRLRLRRRRRLLLL",
        "RLRLLRRLRLRLLRRLRL",
        "RLRLLRRLRLRLRRLLRL",
        "RLRLLRRRRLLLLRRLRL",
        "RLRLLRRRRLLLRRLLRL",
        "RLRLLRRRRLRLLRRLLL",
        "RLRLLRRRRLRLRRLLLL",
        "RLRRLLLLLLRLLRRRRR",
        "RLRRLLLLLLRLRRLRRR",
        "RLRRLLLLLRRRLRRLRL",
        "RLRRLLLLLRRRRRLLRL",
        "RLRRLLLRLLLLLRRRRR",
        "RLRRLLLRLLLLRRLRRR",
        "RLRRLLLRLLRLLRRRLR",
        "RLRRLLLRLLRLRRLRLR",
        "RLRRLLLRLRLRLRRLRL",
        "RLRRLLLRLRLRRRLLRL",
        "RLRRLLLRLRRRLRRLLL",
        "RLRRLLLRLRRRRRLLLL",
        "RLRRLLRLRLRLLRRLRL",
        "RLRRLLRLRLRLRRLLRL",
        "RLRRLLRRRLLLLRRLRL",
        "RLRRLLRRRLLLRRLLRL",
        "RLRRLLRRRLRLLRRLLL",
        "RLRRLLRRRLRLRRLLLL",
        "RLRRLRLLLLRLLRLRRR",
        "RLRRLRLLLRRRLRLLRL",
        "RLRRLRLRLLLLLRLRRR",
        "RLRRLRLRLLRLLRLRLR",
        "RLRRLRLRLRLRLRLLRL",
        "RLRRLRLRLRRRLRLLLL",
        "RLRRLRRLRLRLLRLLRL",
        "RLRRLRRRRLLLLRLLRL",
        "RLRRLRRRRLRLLRLLLL",
        "RRLLLLLLRLLRRRRRRL",
        "RRLLLLLLRLRRRRRRLL",
        "RRLLLLLRRLLRRRRRLL",
        "RRLLLLRLLLLRRRRLRR",
        "RRLLLLRLLLRRRRRLLR",
        "RRLLLLRLLRLLRRRRRL",
        "RRLLLLRLLRRLRRRRLL",
        "RRLLLLRRLLLRRRRLLR",
        "RRLLLLRRLRLLRRRRLL",
        "RRLLLRLLRLLRLRRRRL",
        "RRLLLRLLRLLRRRLRRL",
        "RRLLLRLLRLRRLRRRLL",
        "RRLLLRLLRLRRRRLRLL",
        "RRLLLRLRRLLRLRRRLL",
        "RRLLLRLRRLLRRRLRLL",
        "RRLLLRRLLLLRLRRLRR",
        "RRLLLRRLLLLRRRLLRR",
        "RRLLLRRLLLRRLRRLLR",
        "RRLLLRRLLLRRRRLLLR",
        "RRLLLRRLLRLLLRRRRL",
        "RRLLLRRLLRLLRRLRRL",
        "RRLLLRRLLRRLLRRRLL",
        "RRLLLRRLLRRLRRLRLL",
        "RRLLLRRRLLLRLRRLLR",
        "RRLLLRRRLLLRRRLLLR",
        "RRLLLRRRLRLLLRRRLL",
        "RRLLLRRRLRLLRRLRLL",
        "RRLRLLLLRLLRLRRRRL",
        "RRLRLLLLRLLRRRLRRL",
        "RRLRLLLLRLRRLRRRLL",
        "RRLRLLLLRLRRRRLRLL",
        "RRLRLLLRRLLRLRRRLL",
        "RRLRLLLRRLLRRRLRLL",
        "RRLRLLRLLLLRLRRLRR",
        "RRLRLLRLLLLRRRLLRR",
        "RRLRLLRLLLRRLRRLLR",
        "RRLRLLRLLLRRRRLLLR",
        "RRLRLLRLLRLLLRRRRL",
        "RRLRLLRLLRLLRRLRRL",
        "RRLRLLRLLRRLLRRRLL",
        "RRLRLLRLLRRLRRLRLL",
        "RRLRLLRRLLLRLRRLLR",
        "RRLRLLRRLLLRRRLLLR",
        "RRLRLLRRLRLLLRRRLL",
        "RRLRLLRRLRLLRRLRLL",
        "RRLRLRLLRLLRLRLRRL",
        "RRLRLRLLRLRRLRLRLL",
        "RRLRLRLRRLLRLRLRLL",
        "RRLRLRRLLLLRLRLLRR",
        "RRLRLRRLLLRRLRLLLR",
        "RRLRLRRLLRLLLRLRRL",
        "RRLRLRRLLRRLLRLRLL",
        "RRLRLRRRLLLRLRLLLR",
        "RRLRLRRRLRLLLRLRLL",
        "RRRLLLLLLLLLRRRRRR",
        "RRRLLLLLLLRLRRRRLR",
        "RRRLLLLLLRLRRRRLRL",
        "RRRLLLLLLRRRRRRLLL",
        "RRRLLLLRLLLLRRRRLR",
        "RRRLLLLRLRLRRRRLLL",
        "RRRLLLRLRLLLRRRLRL",
        "RRRLLLRLRLRLRRRLLL",
        "RRRLLLRRRLLLRRRLLL",
        "RRRLLRLLLLLLLRRRRR",
        "RRRLLRLLLLLLRRLRRR",
        "RRRLLRLLLLRLLRRRLR",
        "RRRLLRLLLLRLRRLRLR",
        "RRRLLRLLLRLRLRRLRL",
        "RRRLLRLLLRLRRRLLRL",
        "RRRLLRLLLRRRLRRLLL",
        "RRRLLRLLLRRRRRLLLL",
        "RRRLLRLRLLLLLRRRLR",
        "RRRLLRLRLLLLRRLRLR",
        "RRRLLRLRLRLRLRRLLL",
        "RRRLLRLRLRLRRRLLLL",
        "RRRLLRRLRLLLLRRLRL",
        "RRRLLRRLRLLLRRLLRL",
        "RRRLLRRLRLRLLRRLLL",
        "RRRLLRRLRLRLRRLLLL",
        "RRRLLRRRRLLLLRRLLL",
        "RRRLLRRRRLLLRRLLLL",
        "RRRRLLLLLLLLLRRRRR",
        "RRRRLLLLLLLLRRLRRR",
        "RRRRLLLLLLRLLRRRLR",
        "RRRRLLLLLLRLRRLRLR",
        "RRRRLLLLLRLRLRRLRL",
        "RRRRLLLLLRLRRRLLRL",
        "RRRRLLLLLRRRLRRLLL",
        "RRRRLLLLLRRRRRLLLL",
        "RRRRLLLRLLLLLRRRLR",
        "RRRRLLLRLLLLRRLRLR",
        "RRRRLLLRLRLRLRRLLL",
        "RRRRLLLRLRLRRRLLLL",
        "RRRRLLRLRLLLLRRLRL",
        "RRRRLLRLRLLLRRLLRL",
        "RRRRLLRLRLRLLRRLLL",
        "RRRRLLRLRLRLRRLLLL",
        "RRRRLLRRRLLLLRRLLL",
        "RRRRLLRRRLLLRRLLLL",
        "RRRRLRLLLLLLLRLRRR",
        "RRRRLRLLLLRLLRLRLR",
        "RRRRLRLLLRLRLRLLRL",
        "RRRRLRLLLRRRLRLLLL",
        "RRRRLRLRLLLLLRLRLR",
        "RRRRLRLRLRLRLRLLLL",
        "RRRRLRRLRLLLLRLLRL",
        "RRRRLRRLRLRLLRLLLL",
        "RRRRLRRRRLLLLRLLLL",
    )

    # fmt: off
    LR_centers_555 = (
        32, 33, 34, 37, 38, 39, 42, 43, 44,  # Left
        82, 83, 84, 87, 88, 89, 92, 93, 94,  # Right
    )
    # fmt: on

    def __init__(self, parent, build_state_index: bool = False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step23-LR-center-stage.txt",
            self.state_targets,
            linecount=4900,
            max_depth=5,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Fw", "Fw'", "Bw", "Bw'", "Dw", "Dw'"),
            use_state_index=True,
            build_state_index=build_state_index,
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
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Fw", "Fw'", "Bw", "Bw'", "Dw", "Dw'"),
            prune_tables=[
                parent.lt_FB_t_centers_stage,
                parent.lt_FB_x_centers_stage,
            ],
            centers_only=True,
        )
        # fmt: on


class LookupTableIDA555FBCentersStageLRCentersSpecial(LookupTableIDAViaGraph):
    def __init__(self, parent):
        # fmt: off
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Fw", "Fw'", "Bw", "Bw'", "Dw", "Dw'"),
            prune_tables=[
                parent.lt_FB_t_centers_stage,
                parent.lt_FB_x_centers_stage,
                parent.lt_phase2_lr_center_stage,
            ],
            centers_only=True,
        )
        # fmt: on


class LookupTableIDA555UDTCenterStage(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Fw", "Fw'", "Bw", "Bw'", "Dw", "Dw'"),
            prune_tables=(parent.lt_FB_t_centers_stage,),
            centers_only=True,
        )


# phase 3
class LookupTable555Phase3LRCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step901-LR-center-stage.txt
    ==============================================
    0 steps has 27 entries (0 percent, 0.00x previous step)
    1 steps has 801 entries (16 percent, 29.67x previous step)
    2 steps has 1,064 entries (21 percent, 1.33x previous step)
    3 steps has 1,692 entries (34 percent, 1.59x previous step)
    4 steps has 1,220 entries (24 percent, 0.72x previous step)
    5 steps has 96 entries (1 percent, 0.08x previous step)

    Total: 4,900 entries
    Average: 2.73 moves
    """

    state_targets = (
        "LLLLLLLLLRRRRRRRRR",
        "LLLLLLLRLRLRRRRRRR",
        "LLLLLLLRLRRRRRRRLR",
        "LLLLLLRLRLRLRRRRRR",
        "LLLLLLRLRRRRRRRLRL",
        "LLLLLLRRRLLLRRRRRR",
        "LLLLLLRRRLRLRRRRLR",
        "LLLLLLRRRRLRRRRLRL",
        "LLLLLLRRRRRRRRRLLL",
        "LLLLLRLLLRRRLRRRRR",
        "LLLLLRLLLRRRRRLRRR",
        "LLLLLRLRLRLRLRRRRR",
        "LLLLLRLRLRLRRRLRRR",
        "LLLLLRLRLRRRLRRRLR",
        "LLLLLRLRLRRRRRLRLR",
        "LLLLLRRLRLRLLRRRRR",
        "LLLLLRRLRLRLRRLRRR",
        "LLLLLRRLRRRRLRRLRL",
        "LLLLLRRLRRRRRRLLRL",
        "LLLLLRRRRLLLLRRRRR",
        "LLLLLRRRRLLLRRLRRR",
        "LLLLLRRRRLRLLRRRLR",
        "LLLLLRRRRLRLRRLRLR",
        "LLLLLRRRRRLRLRRLRL",
        "LLLLLRRRRRLRRRLLRL",
        "LLLLLRRRRRRRLRRLLL",
        "LLLLLRRRRRRRRRLLLL",
        "LLLRLLLLLRRRLRRRRR",
        "LLLRLLLLLRRRRRLRRR",
        "LLLRLLLRLRLRLRRRRR",
        "LLLRLLLRLRLRRRLRRR",
        "LLLRLLLRLRRRLRRRLR",
        "LLLRLLLRLRRRRRLRLR",
        "LLLRLLRLRLRLLRRRRR",
        "LLLRLLRLRLRLRRLRRR",
        "LLLRLLRLRRRRLRRLRL",
        "LLLRLLRLRRRRRRLLRL",
        "LLLRLLRRRLLLLRRRRR",
        "LLLRLLRRRLLLRRLRRR",
        "LLLRLLRRRLRLLRRRLR",
        "LLLRLLRRRLRLRRLRLR",
        "LLLRLLRRRRLRLRRLRL",
        "LLLRLLRRRRLRRRLLRL",
        "LLLRLLRRRRRRLRRLLL",
        "LLLRLLRRRRRRRRLLLL",
        "LLLRLRLLLRRRLRLRRR",
        "LLLRLRLRLRLRLRLRRR",
        "LLLRLRLRLRRRLRLRLR",
        "LLLRLRRLRLRLLRLRRR",
        "LLLRLRRLRRRRLRLLRL",
        "LLLRLRRRRLLLLRLRRR",
        "LLLRLRRRRLRLLRLRLR",
        "LLLRLRRRRRLRLRLLRL",
        "LLLRLRRRRRRRLRLLLL",
        "LLRLLLLLRLRRRRRLRR",
        "LLRLLLLLRRRLRRRRRL",
        "LLRLLLLRRLLRRRRLRR",
        "LLRLLLLRRLRRRRRLLR",
        "LLRLLLLRRRLLRRRRRL",
        "LLRLLLLRRRRLRRRRLL",
        "LLRLLLRLLRRLRRRLRR",
        "LLRLLLRRLRLLRRRLRR",
        "LLRLLLRRLRRLRRRLLR",
        "LLRLLRLLRLRRLRRLRR",
        "LLRLLRLLRLRRRRLLRR",
        "LLRLLRLLRRRLLRRRRL",
        "LLRLLRLLRRRLRRLRRL",
        "LLRLLRLRRLLRLRRLRR",
        "LLRLLRLRRLLRRRLLRR",
        "LLRLLRLRRLRRLRRLLR",
        "LLRLLRLRRLRRRRLLLR",
        "LLRLLRLRRRLLLRRRRL",
        "LLRLLRLRRRLLRRLRRL",
        "LLRLLRLRRRRLLRRRLL",
        "LLRLLRLRRRRLRRLRLL",
        "LLRLLRRLLRRLLRRLRR",
        "LLRLLRRLLRRLRRLLRR",
        "LLRLLRRRLRLLLRRLRR",
        "LLRLLRRRLRLLRRLLRR",
        "LLRLLRRRLRRLLRRLLR",
        "LLRLLRRRLRRLRRLLLR",
        "LLRRLLLLRLRRLRRLRR",
        "LLRRLLLLRLRRRRLLRR",
        "LLRRLLLLRRRLLRRRRL",
        "LLRRLLLLRRRLRRLRRL",
        "LLRRLLLRRLLRLRRLRR",
        "LLRRLLLRRLLRRRLLRR",
        "LLRRLLLRRLRRLRRLLR",
        "LLRRLLLRRLRRRRLLLR",
        "LLRRLLLRRRLLLRRRRL",
        "LLRRLLLRRRLLRRLRRL",
        "LLRRLLLRRRRLLRRRLL",
        "LLRRLLLRRRRLRRLRLL",
        "LLRRLLRLLRRLLRRLRR",
        "LLRRLLRLLRRLRRLLRR",
        "LLRRLLRRLRLLLRRLRR",
        "LLRRLLRRLRLLRRLLRR",
        "LLRRLLRRLRRLLRRLLR",
        "LLRRLLRRLRRLRRLLLR",
        "LLRRLRLLRLRRLRLLRR",
        "LLRRLRLLRRRLLRLRRL",
        "LLRRLRLRRLLRLRLLRR",
        "LLRRLRLRRLRRLRLLLR",
        "LLRRLRLRRRLLLRLRRL",
        "LLRRLRLRRRRLLRLRLL",
        "LLRRLRRLLRRLLRLLRR",
        "LLRRLRRRLRLLLRLLRR",
        "LLRRLRRRLRRLLRLLLR",
        "LRLLLLLLLRLRRRRRRR",
        "LRLLLLLLLRRRRRRRLR",
        "LRLLLLLRLRLRRRRRLR",
        "LRLLLLRLRLLLRRRRRR",
        "LRLLLLRLRLRLRRRRLR",
        "LRLLLLRLRRLRRRRLRL",
        "LRLLLLRLRRRRRRRLLL",
        "LRLLLLRRRLLLRRRRLR",
        "LRLLLLRRRRLRRRRLLL",
        "LRLLLRLLLRLRLRRRRR",
        "LRLLLRLLLRLRRRLRRR",
        "LRLLLRLLLRRRLRRRLR",
        "LRLLLRLLLRRRRRLRLR",
        "LRLLLRLRLRLRLRRRLR",
        "LRLLLRLRLRLRRRLRLR",
        "LRLLLRRLRLLLLRRRRR",
        "LRLLLRRLRLLLRRLRRR",
        "LRLLLRRLRLRLLRRRLR",
        "LRLLLRRLRLRLRRLRLR",
        "LRLLLRRLRRLRLRRLRL",
        "LRLLLRRLRRLRRRLLRL",
        "LRLLLRRLRRRRLRRLLL",
        "LRLLLRRLRRRRRRLLLL",
        "LRLLLRRRRLLLLRRRLR",
        "LRLLLRRRRLLLRRLRLR",
        "LRLLLRRRRRLRLRRLLL",
        "LRLLLRRRRRLRRRLLLL",
        "LRLRLLLLLRLRLRRRRR",
        "LRLRLLLLLRLRRRLRRR",
        "LRLRLLLLLRRRLRRRLR",
        "LRLRLLLLLRRRRRLRLR",
        "LRLRLLLRLRLRLRRRLR",
        "LRLRLLLRLRLRRRLRLR",
        "LRLRLLRLRLLLLRRRRR",
        "LRLRLLRLRLLLRRLRRR",
        "LRLRLLRLRLRLLRRRLR",
        "LRLRLLRLRLRLRRLRLR",
        "LRLRLLRLRRLRLRRLRL",
        "LRLRLLRLRRLRRRLLRL",
        "LRLRLLRLRRRRLRRLLL",
        "LRLRLLRLRRRRRRLLLL",
        "LRLRLLRRRLLLLRRRLR",
        "LRLRLLRRRLLLRRLRLR",
        "LRLRLLRRRRLRLRRLLL",
        "LRLRLLRRRRLRRRLLLL",
        "LRLRLRLLLRLRLRLRRR",
        "LRLRLRLLLRRRLRLRLR",
        "LRLRLRLRLRLRLRLRLR",
        "LRLRLRRLRLLLLRLRRR",
        "LRLRLRRLRLRLLRLRLR",
        "LRLRLRRLRRLRLRLLRL",
        "LRLRLRRLRRRRLRLLLL",
        "LRLRLRRRRLLLLRLRLR",
        "LRLRLRRRRRLRLRLLLL",
        "LRRLLLLLRLLRRRRLRR",
        "LRRLLLLLRLRRRRRLLR",
        "LRRLLLLLRRLLRRRRRL",
        "LRRLLLLLRRRLRRRRLL",
        "LRRLLLLRRLLRRRRLLR",
        "LRRLLLLRRRLLRRRRLL",
        "LRRLLLRLLRLLRRRLRR",
        "LRRLLLRLLRRLRRRLLR",
        "LRRLLLRRLRLLRRRLLR",
        "LRRLLRLLRLLRLRRLRR",
        "LRRLLRLLRLLRRRLLRR",
        "LRRLLRLLRLRRLRRLLR",
        "LRRLLRLLRLRRRRLLLR",
        "LRRLLRLLRRLLLRRRRL",
        "LRRLLRLLRRLLRRLRRL",
        "LRRLLRLLRRRLLRRRLL",
        "LRRLLRLLRRRLRRLRLL",
        "LRRLLRLRRLLRLRRLLR",
        "LRRLLRLRRLLRRRLLLR",
        "LRRLLRLRRRLLLRRRLL",
        "LRRLLRLRRRLLRRLRLL",
        "LRRLLRRLLRLLLRRLRR",
        "LRRLLRRLLRLLRRLLRR",
        "LRRLLRRLLRRLLRRLLR",
        "LRRLLRRLLRRLRRLLLR",
        "LRRLLRRRLRLLLRRLLR",
        "LRRLLRRRLRLLRRLLLR",
        "LRRRLLLLRLLRLRRLRR",
        "LRRRLLLLRLLRRRLLRR",
        "LRRRLLLLRLRRLRRLLR",
        "LRRRLLLLRLRRRRLLLR",
        "LRRRLLLLRRLLLRRRRL",
        "LRRRLLLLRRLLRRLRRL",
        "LRRRLLLLRRRLLRRRLL",
        "LRRRLLLLRRRLRRLRLL",
        "LRRRLLLRRLLRLRRLLR",
        "LRRRLLLRRLLRRRLLLR",
        "LRRRLLLRRRLLLRRRLL",
        "LRRRLLLRRRLLRRLRLL",
        "LRRRLLRLLRLLLRRLRR",
        "LRRRLLRLLRLLRRLLRR",
        "LRRRLLRLLRRLLRRLLR",
        "LRRRLLRLLRRLRRLLLR",
        "LRRRLLRRLRLLLRRLLR",
        "LRRRLLRRLRLLRRLLLR",
        "LRRRLRLLRLLRLRLLRR",
        "LRRRLRLLRLRRLRLLLR",
        "LRRRLRLLRRLLLRLRRL",
        "LRRRLRLLRRRLLRLRLL",
        "LRRRLRLRRLLRLRLLLR",
        "LRRRLRLRRRLLLRLRLL",
        "LRRRLRRLLRLLLRLLRR",
        "LRRRLRRLLRRLLRLLLR",
        "LRRRLRRRLRLLLRLLLR",
        "RLLLLLLLRLRRRRRRRL",
        "RLLLLLLRRLLRRRRRRL",
        "RLLLLLLRRLRRRRRRLL",
        "RLLLLLRLLLRRRRRLRR",
        "RLLLLLRLLRRLRRRRRL",
        "RLLLLLRRLLLRRRRLRR",
        "RLLLLLRRLLRRRRRLLR",
        "RLLLLLRRLRLLRRRRRL",
        "RLLLLLRRLRRLRRRRLL",
        "RLLLLRLLRLRRLRRRRL",
        "RLLLLRLLRLRRRRLRRL",
        "RLLLLRLRRLLRLRRRRL",
        "RLLLLRLRRLLRRRLRRL",
        "RLLLLRLRRLRRLRRRLL",
        "RLLLLRLRRLRRRRLRLL",
        "RLLLLRRLLLRRLRRLRR",
        "RLLLLRRLLLRRRRLLRR",
        "RLLLLRRLLRRLLRRRRL",
        "RLLLLRRLLRRLRRLRRL",
        "RLLLLRRRLLLRLRRLRR",
        "RLLLLRRRLLLRRRLLRR",
        "RLLLLRRRLLRRLRRLLR",
        "RLLLLRRRLLRRRRLLLR",
        "RLLLLRRRLRLLLRRRRL",
        "RLLLLRRRLRLLRRLRRL",
        "RLLLLRRRLRRLLRRRLL",
        "RLLLLRRRLRRLRRLRLL",
        "RLLRLLLLRLRRLRRRRL",
        "RLLRLLLLRLRRRRLRRL",
        "RLLRLLLRRLLRLRRRRL",
        "RLLRLLLRRLLRRRLRRL",
        "RLLRLLLRRLRRLRRRLL",
        "RLLRLLLRRLRRRRLRLL",
        "RLLRLLRLLLRRLRRLRR",
        "RLLRLLRLLLRRRRLLRR",
        "RLLRLLRLLRRLLRRRRL",
        "RLLRLLRLLRRLRRLRRL",
        "RLLRLLRRLLLRLRRLRR",
        "RLLRLLRRLLLRRRLLRR",
        "RLLRLLRRLLRRLRRLLR",
        "RLLRLLRRLLRRRRLLLR",
        "RLLRLLRRLRLLLRRRRL",
        "RLLRLLRRLRLLRRLRRL",
        "RLLRLLRRLRRLLRRRLL",
        "RLLRLLRRLRRLRRLRLL",
        "RLLRLRLLRLRRLRLRRL",
        "RLLRLRLRRLLRLRLRRL",
        "RLLRLRLRRLRRLRLRLL",
        "RLLRLRRLLLRRLRLLRR",
        "RLLRLRRLLRRLLRLRRL",
        "RLLRLRRRLLLRLRLLRR",
        "RLLRLRRRLLRRLRLLLR",
        "RLLRLRRRLRLLLRLRRL",
        "RLLRLRRRLRRLLRLRLL",
        "RLRLLLLLLLRLRRRRRR",
        "RLRLLLLLLRRRRRRLRL",
        "RLRLLLLRLLLLRRRRRR",
        "RLRLLLLRLLRLRRRRLR",
        "RLRLLLLRLRLRRRRLRL",
        "RLRLLLLRLRRRRRRLLL",
        "RLRLLLRLRLRLRRRLRL",
        "RLRLLLRRRLLLRRRLRL",
        "RLRLLLRRRLRLRRRLLL",
        "RLRLLRLLLLRLLRRRRR",
        "RLRLLRLLLLRLRRLRRR",
        "RLRLLRLLLRRRLRRLRL",
        "RLRLLRLLLRRRRRLLRL",
        "RLRLLRLRLLLLLRRRRR",
        "RLRLLRLRLLLLRRLRRR",
        "RLRLLRLRLLRLLRRRLR",
        "RLRLLRLRLLRLRRLRLR",
        "RLRLLRLRLRLRLRRLRL",
        "RLRLLRLRLRLRRRLLRL",
        "RLRLLRLRLRRRLRRLLL",
        "RLRLLRLRLRRRRRLLLL",
        "RLRLLRRLRLRLLRRLRL",
        "RLRLLRRLRLRLRRLLRL",
        "RLRLLRRRRLLLLRRLRL",
        "RLRLLRRRRLLLRRLLRL",
        "RLRLLRRRRLRLLRRLLL",
        "RLRLLRRRRLRLRRLLLL",
        "RLRRLLLLLLRLLRRRRR",
        "RLRRLLLLLLRLRRLRRR",
        "RLRRLLLLLRRRLRRLRL",
        "RLRRLLLLLRRRRRLLRL",
        "RLRRLLLRLLLLLRRRRR",
        "RLRRLLLRLLLLRRLRRR",
        "RLRRLLLRLLRLLRRRLR",
        "RLRRLLLRLLRLRRLRLR",
        "RLRRLLLRLRLRLRRLRL",
        "RLRRLLLRLRLRRRLLRL",
        "RLRRLLLRLRRRLRRLLL",
        "RLRRLLLRLRRRRRLLLL",
        "RLRRLLRLRLRLLRRLRL",
        "RLRRLLRLRLRLRRLLRL",
        "RLRRLLRRRLLLLRRLRL",
        "RLRRLLRRRLLLRRLLRL",
        "RLRRLLRRRLRLLRRLLL",
        "RLRRLLRRRLRLRRLLLL",
        "RLRRLRLLLLRLLRLRRR",
        "RLRRLRLLLRRRLRLLRL",
        "RLRRLRLRLLLLLRLRRR",
        "RLRRLRLRLLRLLRLRLR",
        "RLRRLRLRLRLRLRLLRL",
        "RLRRLRLRLRRRLRLLLL",
        "RLRRLRRLRLRLLRLLRL",
        "RLRRLRRRRLLLLRLLRL",
        "RLRRLRRRRLRLLRLLLL",
        "RRLLLLLLRLLRRRRRRL",
        "RRLLLLLLRLRRRRRRLL",
        "RRLLLLLRRLLRRRRRLL",
        "RRLLLLRLLLLRRRRLRR",
        "RRLLLLRLLLRRRRRLLR",
        "RRLLLLRLLRLLRRRRRL",
        "RRLLLLRLLRRLRRRRLL",
        "RRLLLLRRLLLRRRRLLR",
        "RRLLLLRRLRLLRRRRLL",
        "RRLLLRLLRLLRLRRRRL",
        "RRLLLRLLRLLRRRLRRL",
        "RRLLLRLLRLRRLRRRLL",
        "RRLLLRLLRLRRRRLRLL",
        "RRLLLRLRRLLRLRRRLL",
        "RRLLLRLRRLLRRRLRLL",
        "RRLLLRRLLLLRLRRLRR",
        "RRLLLRRLLLLRRRLLRR",
        "RRLLLRRLLLRRLRRLLR",
        "RRLLLRRLLLRRRRLLLR",
        "RRLLLRRLLRLLLRRRRL",
        "RRLLLRRLLRLLRRLRRL",
        "RRLLLRRLLRRLLRRRLL",
        "RRLLLRRLLRRLRRLRLL",
        "RRLLLRRRLLLRLRRLLR",
        "RRLLLRRRLLLRRRLLLR",
        "RRLLLRRRLRLLLRRRLL",
        "RRLLLRRRLRLLRRLRLL",
        "RRLRLLLLRLLRLRRRRL",
        "RRLRLLLLRLLRRRLRRL",
        "RRLRLLLLRLRRLRRRLL",
        "RRLRLLLLRLRRRRLRLL",
        "RRLRLLLRRLLRLRRRLL",
        "RRLRLLLRRLLRRRLRLL",
        "RRLRLLRLLLLRLRRLRR",
        "RRLRLLRLLLLRRRLLRR",
        "RRLRLLRLLLRRLRRLLR",
        "RRLRLLRLLLRRRRLLLR",
        "RRLRLLRLLRLLLRRRRL",
        "RRLRLLRLLRLLRRLRRL",
        "RRLRLLRLLRRLLRRRLL",
        "RRLRLLRLLRRLRRLRLL",
        "RRLRLLRRLLLRLRRLLR",
        "RRLRLLRRLLLRRRLLLR",
        "RRLRLLRRLRLLLRRRLL",
        "RRLRLLRRLRLLRRLRLL",
        "RRLRLRLLRLLRLRLRRL",
        "RRLRLRLLRLRRLRLRLL",
        "RRLRLRLRRLLRLRLRLL",
        "RRLRLRRLLLLRLRLLRR",
        "RRLRLRRLLLRRLRLLLR",
        "RRLRLRRLLRLLLRLRRL",
        "RRLRLRRLLRRLLRLRLL",
        "RRLRLRRRLLLRLRLLLR",
        "RRLRLRRRLRLLLRLRLL",
        "RRRLLLLLLLLLRRRRRR",
        "RRRLLLLLLLRLRRRRLR",
        "RRRLLLLLLRLRRRRLRL",
        "RRRLLLLLLRRRRRRLLL",
        "RRRLLLLRLLLLRRRRLR",
        "RRRLLLLRLRLRRRRLLL",
        "RRRLLLRLRLLLRRRLRL",
        "RRRLLLRLRLRLRRRLLL",
        "RRRLLLRRRLLLRRRLLL",
        "RRRLLRLLLLLLLRRRRR",
        "RRRLLRLLLLLLRRLRRR",
        "RRRLLRLLLLRLLRRRLR",
        "RRRLLRLLLLRLRRLRLR",
        "RRRLLRLLLRLRLRRLRL",
        "RRRLLRLLLRLRRRLLRL",
        "RRRLLRLLLRRRLRRLLL",
        "RRRLLRLLLRRRRRLLLL",
        "RRRLLRLRLLLLLRRRLR",
        "RRRLLRLRLLLLRRLRLR",
        "RRRLLRLRLRLRLRRLLL",
        "RRRLLRLRLRLRRRLLLL",
        "RRRLLRRLRLLLLRRLRL",
        "RRRLLRRLRLLLRRLLRL",
        "RRRLLRRLRLRLLRRLLL",
        "RRRLLRRLRLRLRRLLLL",
        "RRRLLRRRRLLLLRRLLL",
        "RRRLLRRRRLLLRRLLLL",
        "RRRRLLLLLLLLLRRRRR",
        "RRRRLLLLLLLLRRLRRR",
        "RRRRLLLLLLRLLRRRLR",
        "RRRRLLLLLLRLRRLRLR",
        "RRRRLLLLLRLRLRRLRL",
        "RRRRLLLLLRLRRRLLRL",
        "RRRRLLLLLRRRLRRLLL",
        "RRRRLLLLLRRRRRLLLL",
        "RRRRLLLRLLLLLRRRLR",
        "RRRRLLLRLLLLRRLRLR",
        "RRRRLLLRLRLRLRRLLL",
        "RRRRLLLRLRLRRRLLLL",
        "RRRRLLRLRLLLLRRLRL",
        "RRRRLLRLRLLLRRLLRL",
        "RRRRLLRLRLRLLRRLLL",
        "RRRRLLRLRLRLRRLLLL",
        "RRRRLLRRRLLLLRRLLL",
        "RRRRLLRRRLLLRRLLLL",
        "RRRRLRLLLLLLLRLRRR",
        "RRRRLRLLLLRLLRLRLR",
        "RRRRLRLLLRLRLRLLRL",
        "RRRRLRLLLRRRLRLLLL",
        "RRRRLRLRLLLLLRLRLR",
        "RRRRLRLRLRLRLRLLLL",
        "RRRRLRRLRLLLLRLLRL",
        "RRRRLRRLRLRLLRLLLL",
        "RRRRLRRRRLLLLRLLLL",
    )

    # fmt: off
    LR_centers_555 = (
        32, 33, 34, 37, 38, 39, 42, 43, 44,  # Left
        82, 83, 84, 87, 88, 89, 92, 93, 94,  # Right
    )
    # fmt: on

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step901-LR-center-stage.txt",
            self.state_targets,
            linecount=4900,
            max_depth=5,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_centers_555, state):
            cube[pos] = pos_state


class LookupTable555EdgeOrientOuterOrbit(LookupTable):
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

    # fmt: off
    outer_orbit_indexes = (
        0, 2, 3, 4, 7, 8, 9,
        11, 12, 14, 15, 16, 19, 20,
        21, 23, 24, 26, 27, 28, 31,
        32, 33, 35, 36, 38, 39, 40,
        43, 44, 45, 47, 48, 50, 51,
        52, 55, 56, 57, 59, 60, 62,
        63, 64, 67, 68, 69, 71,
    )
    # fmt: on

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step902-EO-outer-orbit.txt",
            "UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU",
            linecount=2704156,
            max_depth=10,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        eo_state_both_orbits = self.parent.highlow_edges_state()
        return "".join([eo_state_both_orbits[x] for x in self.outer_orbit_indexes])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ["x"]
        self.parent.state.extend(
            list(
                "UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"
            )
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()

        # nuke the midges
        for edge_pos in edge_orbit_1_555:
            self.parent.state[edge_pos] = "."

        for step in steps_to_scramble:
            self.parent.rotate(step)

    def ida_heuristic(self):
        state = self.state()
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable555EdgeOrientInnerOrbit(LookupTable):
    """
    lookup-table-5x5x5-step903-EO-inner-orbit.txt
    =============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 25 entries (1 percent, 12.50x previous step)
    3 steps has 202 entries (9 percent, 8.08x previous step)
    4 steps has 620 entries (30 percent, 3.07x previous step)
    5 steps has 900 entries (43 percent, 1.45x previous step)
    6 steps has 285 entries (13 percent, 0.32x previous step)
    7 steps has 13 entries (0 percent, 0.05x previous step)

    Total: 2,048 entries
    Average: 4.61 moves
    """

    midge_states = {
        (3, 103): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],  # Upper
        (11, 28): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (23, 53): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (15, 78): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (36, 115): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],  # Left
        (40, 61): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (86, 65): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],  # Right
        (90, 111): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (128, 73): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],  # Down
        (136, 48): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (140, 98): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (148, 123): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
    }

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step903-EO-inner-orbit.txt",
            "UUUUUUUUUUUUUUUUUUUUUUUU",
            linecount=2048,
            max_depth=7,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            use_state_index=True,
            build_state_index=build_state_index,
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

        return "".join([lt_state[x] for x in midge_indexes])

    def populate_cube_from_state(self, state, cube, steps_to_solve):

        # populate the midges
        steps_to_solve = steps_to_solve.split()
        steps_to_scramble = reverse_steps(steps_to_solve)

        self.parent.state = ["x"]
        self.parent.state.extend(
            list(
                "UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"
            )
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()

        # nuke the outer orbit of edges
        for edge_pos in edge_orbit_0_555:
            self.parent.state[edge_pos] = "."

        for step in steps_to_scramble:
            self.parent.rotate(step)


class LookupTableIDA555LRCenterStageEOBothOrbits(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            prune_tables=(
                parent.lt_phase3_lr_center_stage,
                parent.lt_phase3_eo_outer_orbit,
                parent.lt_phase3_eo_inner_orbit,
            ),
        )


# phase 4
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
            self, parent, "lookup-table-5x5x5-step40-phase4.txt", "TBD", linecount=32389725, max_depth=3
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
                    self.parent.state[square_index] = "L"
                    self.parent.state[partner_index] = "L"
                else:
                    self.parent.state[square_index] = "x"
                    self.parent.state[partner_index] = "x"

        state = "".join(["1" if parent_state[x] == "L" else "0" for x in edges_555])
        state = self.hex_format % int(state, 2)
        cost_to_goal = self.heuristic(state)
        self.parent.state = original_state
        # logger.info("%s: state %s, cost_to_goal %s" % (self, state, cost_to_goal))
        return (state, cost_to_goal)

    def solve(self, print_steps=False) -> bool:
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
                    logger.info(f"{self}: step {step}")
            return True
        else:
            return False


# phase 5
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
        "LLLLLLLLLBFBBFBBFBRRRRRRRRRFBFFBFFBF",
        "LLLLLLLLLBFFBFFBFFRRRRRRRRRBBFBBFBBF",
        "LLLLLLLLLBFFBFFBFFRRRRRRRRRFBBFBBFBB",
        "LLLLLLLLLFFBFFBFFBRRRRRRRRRBBFBBFBBF",
        "LLLLLLLLLFFBFFBFFBRRRRRRRRRFBBFBBFBB",
        "LLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBB",
        "LLRLLRLLRBFBBFBBFBLRRLRRLRRFBFFBFFBF",
        "LLRLLRLLRBFBBFBBFBRRLRRLRRLFBFFBFFBF",
        "LLRLLRLLRBFFBFFBFFLRRLRRLRRBBFBBFBBF",
        "LLRLLRLLRBFFBFFBFFLRRLRRLRRFBBFBBFBB",
        "LLRLLRLLRBFFBFFBFFRRLRRLRRLBBFBBFBBF",
        "LLRLLRLLRBFFBFFBFFRRLRRLRRLFBBFBBFBB",
        "LLRLLRLLRFFBFFBFFBLRRLRRLRRBBFBBFBBF",
        "LLRLLRLLRFFBFFBFFBLRRLRRLRRFBBFBBFBB",
        "LLRLLRLLRFFBFFBFFBRRLRRLRRLBBFBBFBBF",
        "LLRLLRLLRFFBFFBFFBRRLRRLRRLFBBFBBFBB",
        "LLRLLRLLRFFFFFFFFFLRRLRRLRRBBBBBBBBB",
        "LLRLLRLLRFFFFFFFFFRRLRRLRRLBBBBBBBBB",
        "RLLRLLRLLBFBBFBBFBLRRLRRLRRFBFFBFFBF",
        "RLLRLLRLLBFBBFBBFBRRLRRLRRLFBFFBFFBF",
        "RLLRLLRLLBFFBFFBFFLRRLRRLRRBBFBBFBBF",
        "RLLRLLRLLBFFBFFBFFLRRLRRLRRFBBFBBFBB",
        "RLLRLLRLLBFFBFFBFFRRLRRLRRLBBFBBFBBF",
        "RLLRLLRLLBFFBFFBFFRRLRRLRRLFBBFBBFBB",
        "RLLRLLRLLFFBFFBFFBLRRLRRLRRBBFBBFBBF",
        "RLLRLLRLLFFBFFBFFBLRRLRRLRRFBBFBBFBB",
        "RLLRLLRLLFFBFFBFFBRRLRRLRRLBBFBBFBBF",
        "RLLRLLRLLFFBFFBFFBRRLRRLRRLFBBFBBFBB",
        "RLLRLLRLLFFFFFFFFFLRRLRRLRRBBBBBBBBB",
        "RLLRLLRLLFFFFFFFFFRRLRRLRRLBBBBBBBBB",
        "RLRRLRRLRBFBBFBBFBLRLLRLLRLFBFFBFFBF",
        "RLRRLRRLRBFFBFFBFFLRLLRLLRLBBFBBFBBF",
        "RLRRLRRLRBFFBFFBFFLRLLRLLRLFBBFBBFBB",
        "RLRRLRRLRFFBFFBFFBLRLLRLLRLBBFBBFBBF",
        "RLRRLRRLRFFBFFBFFBLRLLRLLRLFBBFBBFBB",
        "RLRRLRRLRFFFFFFFFFLRLLRLLRLBBBBBBBBB",
    )

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step51-phase5-centers.txt",
            self.state_targets,
            linecount=2116800,
            max_depth=10,
            all_moves=moves_555,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Dw", "Dw'",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "U", "U'", "D", "D'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in LFRB_centers_555])

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

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step53-phase5-high-edge-and-midge.txt",
            "-------------SSTT--UUVV-------------",
            linecount=117600,
            max_depth=10,
            all_moves=moves_555,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Dw", "Dw'",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "U", "U'", "D", "D'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
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

        self.parent.state = ["x"]
        self.parent.state.extend(
            list(
                "UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"
            )
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        self.parent.nuke_edges_low()
        self.parent.nuke_edges_in_y_plane()
        self.parent.nuke_edges_in_z_plane()

        for step in steps_to_scramble:
            self.parent.rotate(step)


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

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step56-phase5-fb-centers.txt",
            self.state_targets,
            linecount=4900,
            max_depth=7,
            all_moves=moves_555,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Dw", "Dw'",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "U", "U'", "D", "D'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
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

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step54-phase5-low-edge-and-midge.txt",
            "------------sS--TtuU--Vv------------",
            linecount=117600,
            max_depth=10,
            all_moves=moves_555,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Dw", "Dw'",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "U", "U'", "D", "D'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
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

        self.parent.state = ["x"]
        self.parent.state.extend(
            list(
                "UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"
            )
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        self.parent.nuke_edges_high()
        self.parent.nuke_edges_in_y_plane()
        self.parent.nuke_edges_in_z_plane()

        for step in steps_to_scramble:
            self.parent.rotate(step)


class LookupTableIDA555Phase5(LookupTableIDAViaGraph):
    # There could be 4 perfect hashes for this phase
    # - LR centers x high-edge-and-midge - this would be small as there are only 432 LR center states
    # - LR centers x low-edge-and-midge - this would be small as there are only 432 LR center states
    # - FB centers x high-edge-and-midge
    # - FB centers x low-edge-and-midge
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Dw", "Dw'",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "U", "U'", "D", "D'",
            ),
            # fmt: on
            prune_tables=(
                parent.lt_phase5_fb_centers,
                parent.lt_phase5_high_edge_midge,
                parent.lt_phase5_low_edge_midge,
                parent.lt_phase5_centers,
            ),
            # parent.lt_phase5_fb_centers and parent.lt_phase5_high_edge_midge are used to
            # compute the lookup index in the step55 perfect hash file
            #
            # parent.lt_phase5_fb_centers and parent.lt_phase5_low_edge_midge are used to
            # compute the lookup index in the step57 perfect hash file
            perfect_hash01_filename="lookup-table-5x5x5-step55-phase5-fb-centers-high-edge-and-midge.pt-state-perfect-hash",
            perfect_hash02_filename="lookup-table-5x5x5-step57-phase5-fb-centers-low-edge-and-midge.pt-state-perfect-hash",
            pt1_state_max=117600,
            pt2_state_max=117600,
        )


# phase 6
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

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step61-phase6-centers.txt",
            "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD",
            linecount=176400,
            max_depth=9,
            all_moves=moves_555,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Uw2", "Dw", "Dw'", "Dw2",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "F", "F'", "B", "B'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in centers_555])

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

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step62-phase6-high-edge-midge.txt",
            "OO--PPQQ--RR------------WW--XXYY--ZZ",
            linecount=40320,
            max_depth=10,
            all_moves=moves_555,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Uw2", "Dw", "Dw'", "Dw2",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "F", "F'", "B", "B'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
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

        self.parent.state = ["x"]
        self.parent.state.extend(
            list(
                "UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"
            )
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        self.parent.nuke_edges_low()
        self.parent.nuke_edges_in_x_plane()

        for step in steps_to_scramble:
            self.parent.rotate(step)


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

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step63-phase6-low-edge-midge.txt",
            "-OopP--QqrR--------------WwxX--YyzZ-",
            linecount=40320,
            max_depth=10,
            all_moves=moves_555,
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Uw2", "Dw", "Dw'", "Dw2",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "F", "F'", "B", "B'",
            ),
            # fmt: on
            use_state_index=True,
            build_state_index=build_state_index,
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

        self.parent.state = ["x"]
        self.parent.state.extend(
            list(
                "UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD"
            )
        )
        self.parent.nuke_corners()
        self.parent.nuke_centers()
        self.parent.nuke_edges_high()
        self.parent.nuke_edges_in_x_plane()

        for step in steps_to_scramble:
            self.parent.rotate(step)


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
            # fmt: off
            illegal_moves=(
                "Uw", "Uw'", "Uw2", "Dw", "Dw'", "Dw2",
                "Fw", "Fw'", "Bw", "Bw'",
                "Lw", "Lw'", "Rw", "Rw'",
                "L", "L'", "R", "R'",
                "F", "F'", "B", "B'",
            ),
            # fmt: on
            prune_tables=(parent.lt_phase6_high_edge_midge, parent.lt_phase6_low_edge_midge, parent.lt_phase6_centers),
            # parent.lt_phase6_high_edge_midge and parent.lt_phase6_low_edge_midge are used to
            # compute the lookup index in the perfect hash file
            perfect_hash01_filename="lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.pt-state-perfect-hash",
            pt1_state_max=40320,
        )


class LookupTable555UDCenterSolve(LookupTable):
    """
    lookup-table-5x5x5-step34-UD-centers-solve.txt
    ==============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 6 entries (0 percent, 6.00x previous step)
    2 steps has 71 entries (0 percent, 11.83x previous step)
    3 steps has 560 entries (0 percent, 7.89x previous step)
    4 steps has 3,136 entries (0 percent, 5.60x previous step)
    5 steps has 15,246 entries (4 percent, 4.86x previous step)
    6 steps has 58,108 entries (16 percent, 3.81x previous step)
    7 steps has 130,214 entries (37 percent, 2.24x previous step)
    8 steps has 109,626 entries (31 percent, 0.84x previous step)
    9 steps has 24,832 entries (7 percent, 0.23x previous step)
    10 steps has 1,200 entries (0 percent, 0.05x previous step)

    Total: 343,000 entries
    Average: 7.18 moves
    """

    # fmt: off
    UD_centers_LR_t_centers_555 = sorted([
        7, 8, 9, 12, 13, 14, 17, 18, 19,  # Upper
        33, 37, 39, 43,  # Left
        83, 87, 89, 93,  # Right
        132, 133, 134, 137, 138, 139, 142, 143, 144,  # Down
    ])
    # fmt: on

    state_targets = ("UUUUUUUUULLLLRRRRDDDDDDDDD",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step34-UD-centers-solve.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.UD_centers_LR_t_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.UD_centers_LR_t_centers_555, state):
            cube[pos] = pos_state


class LookupTable555LRCenterSolve(LookupTable):
    """
    lookup-table-5x5x5-step35-LR-centers-solve.txt
    ==============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 6 entries (0 percent, 6.00x previous step)
    2 steps has 67 entries (0 percent, 11.17x previous step)
    3 steps has 476 entries (0 percent, 7.10x previous step)
    4 steps has 2,571 entries (0 percent, 5.40x previous step)
    5 steps has 11,792 entries (3 percent, 4.59x previous step)
    6 steps has 43,263 entries (12 percent, 3.67x previous step)
    7 steps has 98,148 entries (28 percent, 2.27x previous step)
    8 steps has 111,960 entries (32 percent, 1.14x previous step)
    9 steps has 61,836 entries (18 percent, 0.55x previous step)
    10 steps has 12,336 entries (3 percent, 0.20x previous step)
    11 steps has 544 entries (0 percent, 0.04x previous step)

    Total: 343,000 entries
    Average: 7.58 moves
    """

    # fmt: off
    LR_centers_FB_x_centers_555 = sorted([
        32, 33, 34, 37, 38, 39, 42, 43, 44,  # Left
        57, 59, 67, 69,  # Front
        107, 109, 117, 119,  # Back
        82, 83, 84, 87, 88, 89, 92, 93, 94,  # Right
    ])
    # fmt: on

    state_targets = ("LLLLLLLLLFFFFRRRRRRRRRBBBB",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step35-LR-centers-solve.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.LR_centers_FB_x_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.LR_centers_FB_x_centers_555, state):
            cube[pos] = pos_state


class LookupTable555FBCenterSolve(LookupTable):
    """
    lookup-table-5x5x5-step36-FB-centers-solve.txt
    ==============================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 6 entries (0 percent, 6.00x previous step)
    2 steps has 71 entries (0 percent, 11.83x previous step)
    3 steps has 560 entries (0 percent, 7.89x previous step)
    4 steps has 3,136 entries (0 percent, 5.60x previous step)
    5 steps has 15,246 entries (4 percent, 4.86x previous step)
    6 steps has 58,108 entries (16 percent, 3.81x previous step)
    7 steps has 130,214 entries (37 percent, 2.24x previous step)
    8 steps has 109,626 entries (31 percent, 0.84x previous step)
    9 steps has 24,832 entries (7 percent, 0.23x previous step)
    10 steps has 1,200 entries (0 percent, 0.05x previous step)

    Total: 343,000 entries
    Average: 7.18 moves
    """

    # fmt: off
    FB_centers_UD_t_centers_555 = sorted([
        8, 12, 14, 18,  # Upper
        57, 58, 59, 62, 63, 64, 67, 68, 69,  # Front
        107, 108, 109, 112, 113, 114, 117, 118, 119,  # Back
        133, 137, 139, 143,  # Down
    ])
    # fmt: on

    state_targets = ("UUUUFFFFFFFFFBBBBBBBBBDDDD",)

    def __init__(self, parent, build_state_index=False):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step36-FB-centers-solve.txt",
            self.state_targets,
            linecount=343000,
            max_depth=10,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in self.FB_centers_UD_t_centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for (pos, pos_state) in zip(self.FB_centers_UD_t_centers_555, state):
            cube[pos] = pos_state


class LookupTableIDA555ULFRBDCentersSolve(LookupTableIDAViaGraph):
    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'", "Lw", "Lw'", "Rw", "Rw'"),
            prune_tables=(parent.lt_UD_centers_solve, parent.lt_LR_centers_solve, parent.lt_FB_centers_solve),
        )


class LookupTable555TCenterSolve(LookupTable):
    """
    This is only used when a cube larger than 7x7x7 is being solved

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

    # fmt: off
    t_centers_555 = (
        8, 12, 14, 18,
        33, 37, 39, 43,
        58, 62, 64, 68,
        83, 87, 89, 93,
        108, 112, 114, 118,
        133, 137, 139, 143,
    )
    # fmt: on

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            "lookup-table-5x5x5-step33-ULFRBD-t-centers-solve.txt",
            "UUUULLLLFFFFRRRRBBBBDDDD",
            linecount=343000,
        )

    def ida_heuristic(self):
        parent_state = self.parent.state
        result = "".join([parent_state[x] for x in self.t_centers_555])
        return (result, 0)


class RubiksCube555(RubiksCube):
    """
    5x5x5 strategy
    - stage UD centers to sides U or D (use IDA)
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3
    """

    reduce333_orient_edges_tuples = (
        (2, 104),
        (3, 103),
        (4, 102),
        (6, 27),
        (10, 79),
        (11, 28),
        (15, 78),
        (16, 29),
        (20, 77),
        (22, 52),
        (23, 53),
        (24, 54),  # Upper
        (27, 6),
        (28, 11),
        (29, 16),
        (31, 110),
        (35, 56),
        (36, 115),
        (40, 61),
        (41, 120),
        (45, 66),
        (47, 141),
        (48, 136),
        (49, 131),  # Left
        (52, 22),
        (53, 23),
        (54, 24),
        (56, 35),
        (60, 81),
        (61, 40),
        (65, 86),
        (66, 45),
        (70, 91),
        (72, 127),
        (73, 128),
        (74, 129),  # Front
        (77, 20),
        (78, 15),
        (79, 10),
        (81, 60),
        (85, 106),
        (86, 65),
        (90, 111),
        (91, 70),
        (95, 116),
        (97, 135),
        (98, 140),
        (99, 145),  # Right
        (102, 4),
        (103, 3),
        (104, 2),
        (106, 85),
        (110, 31),
        (111, 90),
        (115, 36),
        (116, 95),
        (120, 41),
        (122, 149),
        (123, 148),
        (124, 147),  # Back
        (127, 72),
        (128, 73),
        (129, 74),
        (131, 49),
        (135, 97),
        (136, 48),
        (140, 98),
        (141, 47),
        (145, 99),
        (147, 124),
        (148, 123),
        (149, 122),  # Down
    )

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

        # phase 1
        self.lt_LR_t_centers_stage = LookupTable555LRTCenterStage(self)
        self.lt_LR_x_centers_stage = LookupTable555LRXCenterStage(self)
        self.lt_LR_centers_stage = LookupTableIDA555LRCenterStage(self)
        self.lt_LR_t_centers_stage_ida = LookupTableIDA555LRTCenterStage(self)

        # phase 2
        self.lt_FB_t_centers_stage = LookupTable555FBTCenterStage(self)
        self.lt_FB_x_centers_stage = LookupTable555FBXCenterStage(self)
        self.lt_phase2_lr_center_stage = LookupTable555Phase2LRCenterStage(self)
        self.lt_FB_centers_stage = LookupTableIDA555FBCentersStage(self)
        self.lt_FB_centers_stage.avoid_oll = 0

        self.lt_UD_t_centers_stage_ida = LookupTableIDA555UDTCenterStage(self)

        self.lt_FB_centers_stage_LR_centers_special = LookupTableIDA555FBCentersStageLRCentersSpecial(self)
        self.lt_FB_centers_stage_LR_centers_special.avoid_oll = 0

        # phase 3
        self.lt_phase3_lr_center_stage = LookupTable555Phase3LRCenterStage(self)
        self.lt_phase3_eo_outer_orbit = LookupTable555EdgeOrientOuterOrbit(self)
        self.lt_phase3_eo_inner_orbit = LookupTable555EdgeOrientInnerOrbit(self)
        self.lt_phase3 = LookupTableIDA555LRCenterStageEOBothOrbits(self)

        # phase 4
        self.lt_phase4 = LookupTable555Phase4(self)

        # phase 5
        self.lt_phase5_centers = LookupTable555Phase5Centers(self)
        self.lt_phase5_high_edge_midge = LookupTable555Phase5HighEdgeMidge(self)
        self.lt_phase5_low_edge_midge = LookupTable555Phase5LowEdgeMidge(self)
        self.lt_phase5_fb_centers = LookupTable555Phase5FBCenters(self)
        self.lt_phase5 = LookupTableIDA555Phase5(self)

        # phase 6
        self.lt_phase6_centers = LookupTable555Phase6Centers(self)
        self.lt_phase6_high_edge_midge = LookupTable555Phase6HighEdgeMidge(self)
        self.lt_phase6_low_edge_midge = LookupTable555Phase6LowEdgeMidge(self)
        self.lt_phase6 = LookupTableIDA555Phase6(self)

        # for larger cubes that have reduced to 555
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
        self.print_cube(f"{self}: high/low edges")

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
            (34, 148, 123),  # DB
        ):

            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if must_be_uppercase or must_be_lowercase:
                # logger.info("must_be_uppercase %s, must_be_lowercase %s" % (must_be_uppercase, must_be_lowercase))

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

    def group_centers_stage_LR(self):
        """
        Stage LR centers
        """

        if not self.LR_centers_staged():
            tmp_solution_len = len(self.solution)
            self.lt_LR_centers_stage.solve_via_c()
            self.print_cube_add_comment("LR centers staged", tmp_solution_len)

    def group_centers_stage_FB(self, max_ida_threshold: int = None):
        """
        Stage FB centers
        """
        if self.FB_centers_staged():
            if self.edge_swaps_odd(False, 0, False):
                self.prevent_OLL()
        else:
            tmp_solution_len = len(self.solution)
            self.lt_FB_centers_stage.solve_via_c(max_ida_threshold=max_ida_threshold)
            self.print_cube_add_comment("UD FB centers staged", tmp_solution_len)

    def group_centers_stage_UD(self, max_ida_threshold: int = None):
        self.group_centers_stage_FB(max_ida_threshold=max_ida_threshold)

    def eo_edges(self):
        """
        Our goal is to get the edges split into high/low groups but we do not care what
        the final orienation is of the edges. Each edge can either be in its final
        orientation or not so there are (2^12)/2 or 2048 possible permutations.  The /2
        is because there cannot be an odd number of edges not in their final orientation.
        """
        logger.info("eo_edges called")
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

        # build a list of all possible EO permutations...an even number of edges must be high
        for num in range(4096):
            num = str(bin(num)).lstrip("0b").zfill(12)
            if num.count("1") % 2 == 0:
                permutations.append(list(map(int, num)))

        # Put all 2048 starting states in a file and point ida-via-graph
        # at the file so it can solve all of them and apply the one that is the shortest.
        lr_center_stage_states = []
        eo_outer_orbit_states = []
        eo_inner_orbit_states = []

        for permutation in permutations:
            must_be_uppercase = []
            must_be_lowercase = []
            self.state = original_state[:]

            for (wing_str, uppercase) in zip(wing_strs, permutation):
                if uppercase:
                    must_be_uppercase.append(wing_str)
                else:
                    must_be_lowercase.append(wing_str)

            # logger.info("%s: %s permutation %s" % (self, index, "".join(map(str, permutation))))
            self.edges_flip_orientation(must_be_uppercase, must_be_lowercase)

            # build lists of the states that we need to find state_indexes for
            lr_center_stage_states.append(self.lt_phase3_lr_center_stage.state())
            eo_outer_orbit_states.append(self.lt_phase3_eo_outer_orbit.state())
            eo_inner_orbit_states.append(self.lt_phase3_eo_inner_orbit.state())

        # now we have a huge list of states to lookup, do a binary search on multiple states at once (this is drastically faster
        # than binary searching for them individually).  state_index_multiple() will return a dict where the state is the key
        # and the state_index is the value.
        lr_center_stage_eo_inner_orbit_state_indexes = self.lt_phase3_lr_center_stage.state_index_multiple(
            lr_center_stage_states
        )
        eo_outer_orbit_state_indexes = self.lt_phase3_eo_outer_orbit.state_index_multiple(eo_outer_orbit_states)
        eo_inner_orbit_state_indexes = self.lt_phase3_eo_inner_orbit.state_index_multiple(eo_inner_orbit_states)

        # build a list of tuples of the state indexes
        pt_state_indexes = []
        for (lr_center_stage_eo_inner_orbit_state, eo_outer_orbit_state, eo_inner_orbit_state) in zip(
            lr_center_stage_states, eo_outer_orbit_states, eo_inner_orbit_states
        ):
            pt_state_indexes.append(
                (
                    lr_center_stage_eo_inner_orbit_state_indexes[lr_center_stage_eo_inner_orbit_state],
                    eo_outer_orbit_state_indexes[eo_outer_orbit_state],
                    eo_inner_orbit_state_indexes[eo_inner_orbit_state],
                )
            )

        self.state = original_state[:]
        self.solution = original_solution[:]

        # When solve_via_c is passed pt_state_indexes (2048 lines of states in this case), it will try all 2048 of them
        # to find the state that has the shortest solution.
        self.lt_phase3.solve_via_c(pt_states=pt_state_indexes)

        self.print_cube_add_comment("edges EOed into high/low groups", tmp_solution_len)
        self.post_eo_state = self.state[:]
        self.post_eo_solution = self.solution[:]

        # re-color the cube so that the edges are oriented correctly so we can
        # pair 4-edges then 8-edges. After all edge pairing is done we will uncolor
        # the cube and re-apply the solution.
        self.edges_flip_orientation(wing_strs, [])
        self.highlow_edges_print()

    def high_edge_midge_pair_count(self, target_wing_str=[]):
        count = 0
        it = iter(high_wings_and_midges_555)

        for index1 in it:
            index2 = next(it)
            index1_value = self.state[index1]
            index2_value = self.state[index2]
            index1_partner = edges_partner_555[index1]
            index2_partner = edges_partner_555[index2]
            index1_partner_value = self.state[index1_partner]
            index2_partner_value = self.state[index2_partner]

            if index1_value == index2_value and index1_partner_value == index2_partner_value:

                if target_wing_str:
                    index1_wing_str = wing_str_map[index1_value + index1_partner_value]
                    # index2_wing_str = wing_str_map[index2_value + index2_partner_value]

                    if index1_wing_str in target_wing_str:
                        count += 1
                else:
                    count += 1

        return count

    def low_edge_midge_pair_count(self, target_wing_str=[]):
        count = 0
        it = iter(low_wings_and_midges_555)

        for index1 in it:
            index2 = next(it)
            index1_value = self.state[index1]
            index2_value = self.state[index2]
            index1_partner = edges_partner_555[index1]
            index2_partner = edges_partner_555[index2]
            index1_partner_value = self.state[index1_partner]
            index2_partner_value = self.state[index2_partner]

            if index1_value == index2_value and index1_partner_value == index2_partner_value:
                if target_wing_str:
                    index1_wing_str = wing_str_map[index1_value + index1_partner_value]
                    # index2_wing_str = wing_str_map[index2_value + index2_partner_value]

                    if index1_wing_str in target_wing_str:
                        count += 1
                else:
                    count += 1

        return count

    def find_first_four_edges_to_pair(self):
        """
        phase-5 requires a 4-edge combo where none of the edges are in the z-plane.
        phase-4 will put a 4-edge combo into that state. There are 12!/(4!*8!) or 495
        different 4-edge combinations.  Try them all and see which one has the lowest
        phase-4 cost.
        """
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)
        results = []

        for (wing_str_index, wing_str_combo) in enumerate(itertools.combinations(wing_strs_all, 4)):
            wing_str_combo = sorted(wing_str_combo)
            self.state = original_state[:]
            self.solution = original_solution[:]
            self.lt_phase4.wing_strs = wing_str_combo

            if self.lt_phase4.solve():
                phase4_solution = self.solution[original_solution_len:]
                phase4_solution_len = len(phase4_solution)
                results.append((phase4_solution_len, wing_str_combo))
                logger.debug(
                    f"{wing_str_index+1}/495 {wing_str_combo} phase-4 solution length is {phase4_solution_len}"
                )
            else:
                logger.debug(f"{wing_str_index+1}/495 {wing_str_combo} phase-4 solution length is >= 4 ")

        self.lt_phase4.fh_txt_cache = {}
        self.state = original_state[:]
        self.solution = original_solution[:]
        results.sort()
        return results

    def pair_first_four_edges(self, phase4_wing_str_combo: List[str]):
        tmp_solution_len = len(self.solution)
        self.lt_phase4.wing_strs = phase4_wing_str_combo
        self.lt_phase4.solve()
        self.print_cube_add_comment("4-edges prepped for pairing", tmp_solution_len)

        original_state = self.state[:]
        original_solution = self.solution[:]
        tmp_solution_len = len(self.solution)

        self.edges_flip_orientation(phase4_wing_str_combo, [])
        self.lt_phase5_high_edge_midge.wing_strs = phase4_wing_str_combo
        self.lt_phase5_low_edge_midge.wing_strs = phase4_wing_str_combo
        self.lt_phase5.solve_via_c()

        pair_four_edge_solution = self.solution[tmp_solution_len:]
        self.state = original_state[:]
        self.solution = original_solution[:]

        for step in pair_four_edge_solution:
            self.rotate(step)

        self.print_cube_add_comment("x-plane edges paired, LR FB centers vertical bars", tmp_solution_len)

    def pair_last_eight_edges(self, call_print_cube: bool = True):
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(original_solution)
        tmp_solution_len = len(self.solution)

        # We need the edge swaps to be even for our edges lookup table to work.
        if self.edge_swaps_odd(False, 0, False):
            raise SolveError("edge swaps are odd, cannot pair last 8-edges")

        self.edges_flip_orientation(wing_strs_all, [])

        yz_plane_edges = tuple(list(self.get_y_plane_wing_strs()) + list(self.get_z_plane_wing_strs()))
        self.lt_phase6_high_edge_midge.ida_graph_node = None
        self.lt_phase6_low_edge_midge.ida_graph_node = None
        self.lt_phase6_high_edge_midge.wing_strs = yz_plane_edges
        self.lt_phase6_low_edge_midge.wing_strs = yz_plane_edges
        self.lt_phase6.solve_via_c()

        pair_eight_edge_solution = self.solution[original_solution_len:]
        self.state = original_state[:]
        self.solution = original_solution[:]

        for step in pair_eight_edge_solution:
            self.rotate(step)

        self.print_cube_add_comment("last eight edges paired, centers solved", tmp_solution_len)

    def group_centers_phase1_and_2(self) -> None:
        """
        phase1 stages the centers on sides L and R
        phase2 stages the centers on sides F and B and put the LR centers in one of 495 states that can
            be solved without L L' R R'...this is prep work for phase 3

        TODO this needs more work
        BLBFRUFRDDFBUULBRLBRRLDLDLFURFLUBUDRRRDDFDFBBLUFRUFFBBFBLLLDBDFBDBLFDUUFRFBLDUDDURFDRBBDFUUFUBFBDLULDLRRUDFDFULLLUUBUDRLURLBBDURFRBULBRFRBRDRRULDFLFLR

        results in "5x5x5 edge swaps are odd, cannot pair edges"
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if self.centers_staged():
            return

        original_state = self.state[:]
        original_solution = self.solution[:]
        tmp_solution_len = len(self.solution)

        # find multiple phase1 solutions
        phase1_solutions = self.lt_LR_centers_stage.solutions_via_c(solution_count=100)
        pt_state_indexes = []
        pt_state_indexes_LR_centers_special = []
        phase2_pt_state_indexes_to_phase1_solution = {}
        logger.info(f"found {len(phase1_solutions)} phase1 solutions")

        # find the phase2 solution for each phase1 solution
        for phase1_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) in phase1_solutions:
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in phase1_solution:
                self.rotate(step)

            # stage the LR centers
            phase2_pt_state_indexes = tuple([pt.state_index() for pt in self.lt_FB_centers_stage.prune_tables])
            pt_state_indexes.append(phase2_pt_state_indexes)
            phase2_pt_state_indexes_to_phase1_solution[phase2_pt_state_indexes] = phase1_solution

            # stage the LR centers and put them into one of 495 states solveable with L L' R R'
            phase2_pt_state_indexes = tuple(
                [pt.state_index() for pt in self.lt_FB_centers_stage_LR_centers_special.prune_tables]
            )
            pt_state_indexes_LR_centers_special.append(phase2_pt_state_indexes)
            phase2_pt_state_indexes_to_phase1_solution[phase2_pt_state_indexes] = phase1_solution

        self.state = original_state[:]
        self.solution = original_solution[:]

        # stage the FB centers
        phase2_solutions = self.lt_FB_centers_stage.solutions_via_c(pt_states=pt_state_indexes, solution_count=1)
        phase2_solution = phase2_solutions[0][0]

        # stage the FB centers and put LR centers into one of 495 states solveable with L L' R R'
        phase2_solutions_lr_centers_special = self.lt_FB_centers_stage_LR_centers_special.solutions_via_c(
            pt_states=pt_state_indexes_LR_centers_special, solution_count=1
        )
        phase2_solution_lr_centers_special = phase2_solutions_lr_centers_special[0][0]

        # if we can put the LR centers into one of 495 states without adding to the move count, make it so
        if len(phase2_solution_lr_centers_special) <= len(phase2_solution):
            min_phase2_solution, (
                pt0_state,
                pt1_state,
                pt2_state,
                pt3_state,
                pt4_state,
            ) = phase2_solutions_lr_centers_special[0]
            min_phase1_solution = phase2_pt_state_indexes_to_phase1_solution[pt0_state, pt1_state, pt2_state]
        else:
            min_phase2_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) = phase2_solutions[0]
            min_phase1_solution = phase2_pt_state_indexes_to_phase1_solution[pt0_state, pt1_state]

        logger.info(
            f"phase2 solution length {len(phase2_solution)}, phase2_lr_centers_special solution length {len(phase2_solution_lr_centers_special)}"
        )

        for step in min_phase1_solution:
            self.rotate(step)

        self.print_cube_add_comment("LR centers staged", tmp_solution_len)

        tmp_solution_len = len(self.solution)
        for step in min_phase2_solution:
            self.rotate(step)

        self.print_cube_add_comment("UD FB centers staged", tmp_solution_len)

    def pair_edges(self):

        # We need the edge swaps to be even for our phase6 lookup tables to work.
        if self.edge_swaps_odd(False, 0, False):
            raise SolveError(f"{self} edge swaps are odd, cannot pair edges")

        # phase 4
        # phase 5
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(original_solution)
        pt_state_indexes = []
        phase5_pt_state_indexes_to_wing_str_combo = {}

        for phase4_solution_len, wing_str_combo in self.find_first_four_edges_to_pair():
            if phase4_solution_len >= 3:
                break
            self.state = original_state[:]
            self.solution = original_solution[:]

            self.lt_phase4.wing_strs = wing_str_combo
            self.lt_phase4.solve()
            self.edges_flip_orientation(wing_str_combo, [])

            self.lt_phase5_high_edge_midge.wing_strs = wing_str_combo
            self.lt_phase5_low_edge_midge.wing_strs = wing_str_combo
            wing_str_combo_pt_state_indexes = tuple([pt.state_index() for pt in self.lt_phase5.prune_tables])
            phase5_pt_state_indexes_to_wing_str_combo[wing_str_combo_pt_state_indexes] = wing_str_combo
            pt_state_indexes.append(wing_str_combo_pt_state_indexes)

        self.state = original_state[:]
        self.solution = original_solution[:]
        phase5_solutions = self.lt_phase5.solutions_via_c(pt_states=pt_state_indexes, solution_count=500)

        # phase 6
        pt_state_indexes = []
        phase6_pt_state_indexes_to_phase4_solution = {}
        phase6_pt_state_indexes_to_phase5_solution = {}

        for phase5_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) in phase5_solutions:
            wing_str_combo = phase5_pt_state_indexes_to_wing_str_combo[(pt0_state, pt1_state, pt2_state, pt3_state)]
            self.state = original_state[:]
            self.solution = original_solution[:]

            self.lt_phase4.wing_strs = wing_str_combo
            self.lt_phase4.solve()
            phase4_solution = self.solution[original_solution_len:]

            self.edges_flip_orientation(wing_strs_all, [])
            self.lt_phase5_high_edge_midge.wing_strs = wing_str_combo
            self.lt_phase5_low_edge_midge.wing_strs = wing_str_combo

            for step in phase5_solution:
                self.rotate(step)

            yz_plane_edges = tuple(list(self.get_y_plane_wing_strs()) + list(self.get_z_plane_wing_strs()))
            self.lt_phase6_high_edge_midge.ida_graph_node = None
            self.lt_phase6_low_edge_midge.ida_graph_node = None
            self.lt_phase6_high_edge_midge.wing_strs = yz_plane_edges
            self.lt_phase6_low_edge_midge.wing_strs = yz_plane_edges
            wing_str_combo_pt_state_indexes = tuple([pt.state_index() for pt in self.lt_phase6.prune_tables])
            phase6_pt_state_indexes_to_phase4_solution[wing_str_combo_pt_state_indexes] = phase4_solution
            phase6_pt_state_indexes_to_phase5_solution[wing_str_combo_pt_state_indexes] = phase5_solution
            pt_state_indexes.append(wing_str_combo_pt_state_indexes)

        phase6_solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state) = self.lt_phase6.solutions_via_c(
            pt_states=pt_state_indexes
        )[0]
        phase4_solution = phase6_pt_state_indexes_to_phase4_solution[(pt0_state, pt1_state, pt2_state)]
        phase5_solution = phase6_pt_state_indexes_to_phase5_solution[(pt0_state, pt1_state, pt2_state)]

        # apply the solution
        self.state = self.post_eo_state
        self.solution = self.post_eo_solution[:]

        # phase 4
        tmp_solution_len = len(self.solution)
        for step in phase4_solution:
            self.rotate(step)

        self.print_cube_add_comment("4-edges prepped for pairing", tmp_solution_len)

        # phase 5
        tmp_solution_len = len(self.solution)

        for step in phase5_solution:
            self.rotate(step)

        self.print_cube_add_comment("x-plane edges paired, LR FB centers vertical bars", tmp_solution_len)

        # phase 6
        tmp_solution_len = len(self.solution)

        for step in phase6_solution:
            self.rotate(step)

        self.print_cube_add_comment("last eight edges paired, centers solved", tmp_solution_len)

    def reduce_333(self):
        self.lt_init()

        if self.centers_solved() and self.edges_paired():
            return

        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if False:
            self.group_centers_phase1_and_2()

        else:
            # phase 1
            self.group_centers_stage_LR()

            # phase 2
            self.group_centers_stage_FB()

        # phase 3
        self.eo_edges()

        # phases 4 5 and 6
        self.pair_edges()


def rotate_555(cube, step):
    return [cube[x] for x in swaps_555[step]]
