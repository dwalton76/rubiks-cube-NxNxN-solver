"""
5x5x5 solver: reduce the cube to a 3x3x3, then finish with the 3x3x3 solver.

A 5x5x5 has 54 centers (nine per face: four t-centers, four x-centers, and a
fixed middle), 24 wings (the outer edge orbit), 12 midges (the inner edge
orbit), and 8 corners. Reduction pairs each wing with its midge and solves the
centers so the remaining puzzle is a 3x3x3. ``RubiksCube555.reduce_333`` runs
six phases; ``solve_333`` then solves the paired cube.

Each IDA phase is guided by prune tables. Phases 1+2+3+4+5 use dedicated C solvers
over dense ranked costs and are searched as a portfolio: many solutions of the
earlier phase are collected, later phases are solved from those endpoints, and
the shortest combined path is kept. Phases 4+5+6 do the same.

Phase 1 - stage LR centers
    Put all eight LR t-centers and eight LR x-centers onto the L and R faces
    (they need not be solved). ``group_centers_phase1_and_2`` takes a portfolio
    of optimal LR-staging solutions (default 64). Endpoints are grouped by
    whether orbit-0 wide turns would cause OLL parity, because phase 2 must use
    a matching even/odd constraint.

Phase 2 - stage FB (and UD) centers
    Stage the FB t-centers and x-centers onto FB, which also puts the
    remaining centers onto UD. Quarter-turn wide moves that would unstage LR
    are illegal. Orbit-0 OLL is avoided so the later 3x3x3 solve is not left
    with that parity. The search keeps the shortest phase-1 plus phase-2 pair.

Phase 3 - EO the wings and midges; LR centers to 1-of-432
    Split the 24 wings and 12 midges into high/low groups. Each of the 12
    edges can be in its final orientation or not, but only an even number may
    be flipped, so there are 2048 legal EO permutations. All of them are
    searched and the shortest is kept. LR centers are reduced to one of 432
    shapes along the way.

Phases 4 and 5 - pair four edges on the x-plane; LR/FB centers to vertical bars
    Phase 4 ranks the high wing, midge, and low wing locations as three
    C(12,4) coordinates. One C invocation searches all 495 four-edge choices;
    ``pair_edges`` only keeps choices that finish in fewer than three moves.
    Phase 5 then pairs the x-plane high wings, low wings, and midges and puts
    the LR and FB centers into vertical bars. Its ranked C solver uses a center
    table plus FB-center/high-edge/midge and FB-center/low-edge/midge tables.
    A large portfolio of phase-5 solutions (default 500) is passed to phase 6.

Phase 6 - pair the last eight edges and solve the centers
    Pair the remaining wings with their midges and fully solve all 54 centers.
    Another perfect-hash table covers the last-eight-edges pairing. This phase
    pairs whatever sits in the y-plane and z-plane, so it requires the four
    edges already paired to be the ones in the x-plane. Prefixes (phase 4 plus
    5) are grouped by length so the search can minimize the total, not just the
    phase-6 suffix.

Larger cubes that have already reduced to a 5x5x5 reuse the phase-1 and
phase-2 ranked solvers (``lt_LR_centers_stage``, ``lt_FB_centers_stage``,
and ``lt_LR_t_centers_stage_ida``) without going through this six-phase
reduction. Their remaining centers are solved by the 6x6/7x7 daisy searches,
not by a separate 5x5 center-solve IDA.
"""

# standard libraries
import itertools
import logging
import os
import re
import subprocess
import tempfile
from math import comb

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube, reverse_steps, wing_str_map, wing_strs_all
from rubikscubennnsolver.LookupTable import LookupTable, NoIDASolution, download_file_if_needed
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
PHASE1_T_CENTERS_TABLE_555 = (
    "lookup-tables/lookup-table-5x5x5-step11-LR-centers-stage-t-center-only.cost-only.bin"
)
PHASE1_X_CENTERS_TABLE_555 = (
    "lookup-tables/lookup-table-5x5x5-step12-LR-centers-stage-x-center-only.cost-only.bin"
)
PHASE2_T_CENTERS_TABLE_555 = "lookup-tables/lookup-table-5x5x5-step21-FB-t-centers-stage.cost-only.bin"
PHASE2_X_CENTERS_TABLE_555 = "lookup-tables/lookup-table-5x5x5-step22-FB-x-centers-stage.cost-only.bin"
PHASE3_LR_CENTERS_TABLE_555 = "lookup-tables/lookup-table-5x5x5-step901-LR-center-stage.cost-only.bin"
PHASE3_EO_OUTER_TABLE_555 = "lookup-tables/lookup-table-5x5x5-step902-EO-outer-orbit.cost-only.bin"
PHASE3_EO_INNER_TABLE_555 = "lookup-tables/lookup-table-5x5x5-step903-EO-inner-orbit.cost-only.bin"
PHASE4_EDGES_TABLE_555 = "lookup-tables/lookup-table-5x5x5-step40-phase4.cost-only.bin"

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

LR_t_centers_555 = (
    33, 37, 39, 43,  # Left
    83, 87, 89, 93,  # Right
)

LR_x_centers_555 = (
    32, 34, 42, 44,  # Left
    82, 84, 92, 94,  # Right
)

FB_centers_555 = (
    57, 58, 59, 62, 63, 64, 67, 68, 69,  # Front
    107, 108, 109, 112, 113, 114, 117, 118, 119,  # Back
)

FB_t_centers_555 = (
    58, 62, 64, 68,  # Front
    108, 112, 114, 118,  # Back
)

FB_x_centers_555 = (
    57, 59, 67, 69,  # Front
    107, 109, 117, 119,  # Back
)

# x-plane union y-plane: the four parked edges stay in this 8-slot orbit under phase-5 moves.
PHASE5_XY_HIGH_SQUARES_555 = (2, 24, 35, 41, 85, 91, 127, 149)
PHASE5_XY_MIDGE_SQUARES_555 = (3, 23, 36, 40, 86, 90, 128, 148)
PHASE5_XY_LOW_SQUARES_555 = (4, 22, 31, 45, 81, 95, 129, 147)

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

t_centers_without_middles_555 = (
    8, 12, 14, 18,  # Upper
    33, 37, 39, 43,  # Left
    58, 62, 64, 68,  # Front
    83, 87, 89, 93,  # Right
    108, 112, 114, 118,  # Back
    133, 137, 139, 143,  # Down
)

x_centers_without_middles_555 = (
    7, 9, 17, 19,  # Upper
    32, 34, 42, 44,  # Left
    57, 59, 67, 69,  # Front
    82, 84, 92, 94,  # Right
    107, 109, 117, 119,  # Back
    132, 134, 142, 144,  # Down
)

outer_orbit_indexes = (
    0, 2, 3, 4, 7, 8, 9,
    11, 12, 14, 15, 16, 19, 20,
    21, 23, 24, 26, 27, 28, 31,
    32, 33, 35, 36, 38, 39, 40,
    43, 44, 45, 47, 48, 50, 51,
    52, 55, 56, 57, 59, 60, 62,
    63, 64, 67, 68, 69, 71,
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

PHASE4_HIGH_EDGE_SQUARES_555 = tuple(square for square, _ in high_edges_555)
PHASE4_HIGH_EDGE_PARTNERS_555 = tuple(partner for _, partner in high_edges_555)
PHASE4_MIDGE_SQUARES_555 = tuple(square for _, square, _ in midges_recolor_tuples_555)
PHASE4_MIDGE_PARTNERS_555 = tuple(partner for _, _, partner in midges_recolor_tuples_555)
PHASE4_LOW_EDGE_SQUARES_555 = tuple(square for square, _ in low_edges_555)
PHASE4_LOW_EDGE_PARTNERS_555 = tuple(partner for _, partner in low_edges_555)

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

PHASE3_OUTER_WING_SQUARES_555 = tuple(square for _, square, _ in wings_for_recolor_555)
PHASE3_OUTER_WING_PARTNERS_555 = tuple(partner for _, _, partner in wings_for_recolor_555)

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

PHASE3_INNER_MIDGE_SQUARES_555 = tuple(pair[0][0] for pair in MIDGE_TUPLES_555)
PHASE3_INNER_MIDGE_PARTNERS_555 = tuple(pair[0][1] for pair in MIDGE_TUPLES_555)

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
        for s1, s2, s3 in (
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

    for edge_index, square_index, partner_index in midges_recolor_tuples_555:
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
    for _, square_index, partner_index in edges_recolor_tuples_555:
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


# fmt: off
PHASE2_ILLEGAL_MOVES = (
    "Uw", "Uw'",
    "Fw", "Fw'",
    "Bw", "Bw'",
    "Dw", "Dw'",
)

PHASE3_ILLEGAL_MOVES = (
    "Uw", "Uw'",
    "Dw", "Dw'",
    "Fw", "Fw'",
    "Bw", "Bw'",
    "Lw", "Lw'",
    "Rw", "Rw'",
)

PHASE5_ILLEGAL_MOVES = (
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
)

PHASE6_ILLEGAL_MOVES = (
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
)

# fmt: on


class NoEdgeSolution(Exception):
    pass


class RankedCenterCoordinate555:
    """One dense binary center coordinate used by a dedicated 5x5 IDA."""

    def __init__(self, parent, filename, squares, selected_colors):
        self.parent = parent
        self.filename = filename
        self.squares = tuple(squares)
        self.selected_colors = tuple(selected_colors)

    def rank(self):
        selected_remaining = sum(self.parent.state[square] in self.selected_colors for square in self.squares)
        rank = 0

        if selected_remaining != 8:
            raise SolveError(f"{self}: expected 8 selected centers, found {selected_remaining}")
        for position, square in enumerate(self.squares):
            positions_after = len(self.squares) - position - 1
            if self.parent.state[square] in self.selected_colors:
                selected_remaining -= 1
            elif selected_remaining:
                rank += comb(positions_after, selected_remaining - 1)

        return rank


class LookupTableIDA555RankedCenters:
    """Shared process and output handling for the two dedicated center solvers."""

    avoid_oll = None

    def _parity_args(self):
        if self.avoid_oll is None:
            return []
        if self.avoid_oll != 0:
            raise SolveError(f"{self}: only orbit-0 parity is supported")
        if 0 in self.parent.center_solution_leads_to_oll_parity():
            return ["--orbit0-need-odd-w"]
        return ["--orbit0-need-even-w"]

    def _run(self, cmd):
        logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
        output = subprocess.check_output(cmd).decode("utf-8")
        self.parent.solve_via_c_output = f"\n{' '.join(cmd)}\n{output}\n"
        logger.info("\n%s\n", output)
        return output

    def solve_via_c(self, **kwargs):
        solution = self.solutions_via_c(**kwargs)[0][0]
        for step in solution:
            self.parent.rotate(step)


# ==================================================
# phase 1
# stage LR centers
# ==================================================
class LookupTable555LRTCenterStage(RankedCenterCoordinate555):
    """
    24! / (8! * 16!) = 735,471 states

               . . . . .
               . . x . .
               . x . x .
               . . x . .
               . . . . .

    . . . . .  . . . . .  . . . . .  . . . . .
    . . L . .  . . x . .  . . L . .  . . x . .
    . L . L .  . x . x .  . L . L .  . x . x .
    . . L . .  . . x . .  . . L . .  . . x . .
    . . . . .  . . . . .  . . . . .  . . . . .

               . . . . .
               . . x . .
               . x . x .
               . . x . .
               . . . . .

    lookup-table-5x5x5-step11-LR-centers-stage-t-center-only.cost-only.bin
    =====================================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 4 entries (0 percent, 4.00x previous step)
    2 steps has 66 entries (0 percent, 16.50x previous step)
    3 steps has 900 entries (0 percent, 13.64x previous step)
    4 steps has 9,626 entries (1 percent, 10.70x previous step)
    5 steps has 80,202 entries (10 percent, 8.33x previous step)
    6 steps has 329,202 entries (44 percent, 4.10x previous step)
    7 steps has 302,146 entries (41 percent, 0.92x previous step)
    8 steps has 13,324 entries (1 percent, 0.04x previous step)

    Total: 735,471 entries
    Average: 6.31 moves
    """

    def __init__(self, parent, build_state_index=False):
        del build_state_index
        RankedCenterCoordinate555.__init__(
            self,
            parent,
            PHASE1_T_CENTERS_TABLE_555,
            t_centers_without_middles_555,
            ("L", "R"),
        )


class LookupTable555LRXCenterStage(RankedCenterCoordinate555):
    """
    24! / (8! * 16!) = 735,471 states

               . . . . .
               . x . x .
               . . . . .
               . x . x .
               . . . . .

    . . . . .  . . . . .  . . . . .  . . . . .
    . L . L .  . x . x .  . L . L .  . x . x .
    . . . . .  . . . . .  . . . . .  . . . . .
    . L . L .  . x . x .  . L . L .  . x . x .
    . . . . .  . . . . .  . . . . .  . . . . .

               . . . . .
               . x . x .
               . . . . .
               . x . x .
               . . . . .

    lookup-table-5x5x5-step12-LR-centers-stage-x-center-only.cost-only.bin
    =====================================================================
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

    def __init__(self, parent, build_state_index=False):
        del build_state_index
        super().__init__(
            parent,
            PHASE1_X_CENTERS_TABLE_555,
            x_centers_without_middles_555,
            ("L", "R"),
        )


class LookupTableIDA555LRCenterStage(LookupTableIDA555RankedCenters):
    def __init__(self, parent):
        self.parent = parent
        self.prune_tables = (parent.lt_LR_t_centers_stage, parent.lt_LR_x_centers_stage)

    def solutions_via_c(
        self,
        pt_states=(),
        min_ida_threshold=None,
        max_ida_threshold=None,
        solution_count=1,
        **_kwargs,
    ):
        if pt_states:
            raise SolveError("5x5 phase 1 does not accept pre-ranked roots")
        download_file_if_needed(PHASE1_T_CENTERS_TABLE_555)
        download_file_if_needed(PHASE1_X_CENTERS_TABLE_555)
        cmd = [
            "./ida_search_555_phase1",
            "--kociemba",
            self.parent.get_kociemba_string(True),
            "--t-center-cost",
            PHASE1_T_CENTERS_TABLE_555,
            "--x-center-cost",
            PHASE1_X_CENTERS_TABLE_555,
        ]
        if min_ida_threshold is not None:
            cmd.extend(("--min-ida-threshold", str(min_ida_threshold)))
        if max_ida_threshold is not None:
            cmd.extend(("--max-ida-threshold", str(max_ida_threshold)))
        if solution_count != 1:
            cmd.extend(("--solution-count", str(solution_count)))
        output = self._run(cmd)
        solutions = []
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                solutions.append((tuple(line.split(":", 1)[1].strip().split()), (None,) * 5))
        if not solutions:
            raise NoIDASolution(f"Did not find SOLUTION line in\n{output}\n")
        return solutions


class LookupTableIDA555LRTCenterStage(LookupTableIDA555RankedCenters):
    """LR t-center staging IDA used by 7x7/NNNOdd after they have reduced to a 5x5x5."""

    def __init__(self, parent):
        self.parent = parent
        self.prune_tables = (parent.lt_LR_t_centers_stage,)

    def solutions_via_c(
        self,
        pt_states=(),
        min_ida_threshold=None,
        max_ida_threshold=None,
        solution_count=1,
        **_kwargs,
    ):
        if pt_states:
            raise SolveError("5x5 phase 1 t-center search does not accept pre-ranked roots")
        download_file_if_needed(PHASE1_T_CENTERS_TABLE_555)
        cmd = [
            "./ida_search_555_phase1",
            "--kociemba",
            self.parent.get_kociemba_string(True),
            "--t-center-cost",
            PHASE1_T_CENTERS_TABLE_555,
            "--t-centers-only",
        ]
        if min_ida_threshold is not None:
            cmd.extend(("--min-ida-threshold", str(min_ida_threshold)))
        if max_ida_threshold is not None:
            cmd.extend(("--max-ida-threshold", str(max_ida_threshold)))
        if solution_count != 1:
            cmd.extend(("--solution-count", str(solution_count)))
        output = self._run(cmd)
        solutions = []
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                solutions.append((tuple(line.split(":", 1)[1].strip().split()), (None,) * 5))
        if not solutions:
            raise NoIDASolution(f"Did not find SOLUTION line in\n{output}\n")
        return solutions


# ==================================================
# phase 2
# stage FB (and UD) centers
# ==================================================
class LookupTable555FBTCenterStage(RankedCenterCoordinate555):
    """
    16! / (8! * 8!) = 12,870 states

               . . . . .
               . . x . .
               . x . x .
               . . x . .
               . . . . .

    . . . . .  . . . . .  . . . . .  . . . . .
    . . . . .  . . F . .  . . . . .  . . F . .
    . . . . .  . F . F .  . . . . .  . F . F .
    . . . . .  . . F . .  . . . . .  . . F . .
    . . . . .  . . . . .  . . . . .  . . . . .

               . . . . .
               . . x . .
               . x . x .
               . . x . .
               . . . . .

    lookup-table-5x5x5-step21-FB-t-centers-stage.cost-only.bin
    =========================================================
    0 steps has 1 entries (0 percent, 0.00x previous step)
    1 steps has 2 entries (0 percent, 2.00x previous step)
    2 steps has 25 entries (0 percent, 12.50x previous step)
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
        del build_state_index
        super().__init__(
            parent,
            PHASE2_T_CENTERS_TABLE_555,
            UFBD_t_centers_555,
            ("F", "B"),
        )


class LookupTable555FBXCenterStage(RankedCenterCoordinate555):
    """
    16! / (8! * 8!) = 12,870 states

               . . . . .
               . x . x .
               . . . . .
               . x . x .
               . . . . .

    . . . . .  . . . . .  . . . . .  . . . . .
    . . . . .  . F . F .  . . . . .  . F . F .
    . . . . .  . . . . .  . . . . .  . . . . .
    . . . . .  . F . F .  . . . . .  . F . F .
    . . . . .  . . . . .  . . . . .  . . . . .

               . . . . .
               . x . x .
               . . . . .
               . x . x .
               . . . . .

    lookup-table-5x5x5-step22-FB-x-centers-stage.cost-only.bin
    =========================================================
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
        del build_state_index
        super().__init__(
            parent,
            PHASE2_X_CENTERS_TABLE_555,
            UFBD_x_centers_555,
            ("F", "B"),
        )


class LookupTableIDA555FBCentersStage(LookupTableIDA555RankedCenters):
    def __init__(self, parent):
        self.parent = parent
        self.prune_tables = (parent.lt_FB_t_centers_stage, parent.lt_FB_x_centers_stage)
        self.avoid_oll = 0

    def solutions_via_c(
        self,
        pt_states=(),
        min_ida_threshold=None,
        max_ida_threshold=None,
        solution_count=1,
        **_kwargs,
    ):
        roots_filename = None
        roots = []
        download_file_if_needed(PHASE2_T_CENTERS_TABLE_555)
        download_file_if_needed(PHASE2_X_CENTERS_TABLE_555)
        cmd = [
            "./ida_search_555_phase2",
            "--t-center-cost",
            PHASE2_T_CENTERS_TABLE_555,
            "--x-center-cost",
            PHASE2_X_CENTERS_TABLE_555,
            *self._parity_args(),
        ]
        try:
            if pt_states:
                roots = sorted(set(tuple(root[:2]) for root in pt_states))
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as roots_file:
                    roots_filename = roots_file.name
                    for root_id, (t_rank, x_rank) in enumerate(roots):
                        roots_file.write(f"{root_id},{t_rank},{x_rank}\n")
                cmd.extend(("--roots-file", roots_filename))
            else:
                roots = [(self.prune_tables[0].rank(), self.prune_tables[1].rank())]
                cmd.extend(("--kociemba", self.parent.get_kociemba_string(True)))
            if min_ida_threshold is not None:
                cmd.extend(("--min-ida-threshold", str(min_ida_threshold)))
            if max_ida_threshold is not None:
                cmd.extend(("--max-ida-threshold", str(max_ida_threshold)))
            if solution_count != 1:
                cmd.extend(("--solution-count", str(solution_count)))
            output = self._run(cmd)
        finally:
            if roots_filename is not None:
                os.unlink(roots_filename)

        solutions = []
        solution_re = re.compile(r"^SOLUTION ROOT (\d+) \(\d+ steps\):(.*)$")
        for line in output.splitlines():
            match = solution_re.match(line)
            if match:
                root = roots[int(match.group(1))]
                solution = tuple(match.group(2).strip().split())
                solutions.append((len(solution), solution, root + (None, None, None)))
        if not solutions:
            raise NoIDASolution(f"Did not find SOLUTION line in\n{output}\n")
        solutions.sort()
        return [(solution, states) for _, solution, states in solutions]


# ==================================================
# phase 3
# EO the wings and midges; LR centers to 1-of-432
# ==================================================
class LookupTable555Phase3LRCenterStage:
    """
       (8! / (4! * 4!))^2 = 4,900 states

                  . . . . .
                  . . . . .
                  . . . . .
                  . . . . .
                  . . . . .

    . . . . .  . . . . .  . . . . .  . . . . .
    . L L L .  . . . . .  . R R R .  . . . . .
    . L . L .  . . . . .  . R . R .  . . . . .
    . L L L .  . . . . .  . R R R .  . . . . .
    . . . . .  . . . . .  . . . . .  . . . . .

                  . . . . .
                  . . . . .
                  . . . . .
                  . . . . .
                  . . . . .

       lookup-table-5x5x5-step901-LR-center-stage.cost-only.bin
       ========================================================
       0 steps has 432 entries (8 percent, 0.00x previous step)
       1 steps has 396 entries (8 percent, 0.92x previous step)
       2 steps has 1,064 entries (21 percent, 2.69x previous step)
       3 steps has 1,692 entries (34 percent, 1.59x previous step)
       4 steps has 1,220 entries (24 percent, 0.72x previous step)
       5 steps has 96 entries (1 percent, 0.08x previous step)

       Total: 4,900 entries
       Average: 2.64 moves
    """

    def __init__(self, parent, build_state_index=False):
        del build_state_index
        self.parent = parent
        self.filename = PHASE3_LR_CENTERS_TABLE_555

    def _group_rank(self, squares):
        selected_remaining = sum(self.parent.state[square] == "L" for square in squares)
        rank = 0

        if selected_remaining != 4:
            raise SolveError(f"{self}: expected 4 L stickers, found {selected_remaining}")
        for position, square in enumerate(squares):
            positions_after = len(squares) - position - 1
            if self.parent.state[square] == "L":
                selected_remaining -= 1
            elif selected_remaining:
                rank += comb(positions_after, selected_remaining - 1)
        return rank

    def rank(self):
        return self._group_rank(LR_t_centers_555) * 70 + self._group_rank(LR_x_centers_555)


class LookupTable555EdgeOrientOuterOrbit:
    """
       24! / (12! * 12!) = 2,704,156 states

                  . U . D .
                  D . . . U
                  . . . . .
                  U . . . D
                  . D . U .

    . D . U .  . D . U .  . D . U .  . D . U .
    D . . . U  U . . . D  D . . . U  U . . . D
    . . . . .  . . . . .  . . . . .  . . . . .
    U . . . D  D . . . U  U . . . D  D . . . U
    . U . D .  . U . D .  . U . D .  . U . D .

                  . U . D .
                  D . . . U
                  . . . . .
                  U . . . D
                  . D . U .

       lookup-table-5x5x5-step902-EO-outer-orbit.cost-only.bin
       ======================================================
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

    def __init__(self, parent, build_state_index=False):
        del build_state_index
        self.parent = parent
        self.filename = PHASE3_EO_OUTER_TABLE_555

    def highlow_by_square(self):
        return dict(
            zip(
                (square for square, _ in self.parent.reduce333_orient_edges_tuples),
                self.parent.highlow_edges_state(),
            )
        )

    def rank(self):
        highlow = self.highlow_by_square()
        selected_remaining = 12
        rank = 0

        for position, square in enumerate(PHASE3_OUTER_WING_SQUARES_555):
            positions_after = 23 - position
            if highlow[square] == "D":
                selected_remaining -= 1
            elif selected_remaining:
                rank += comb(positions_after, selected_remaining - 1)
        if selected_remaining:
            raise SolveError(f"{self}: expected 12 D wings, found {12 - selected_remaining}")
        return rank


class LookupTable555EdgeOrientInnerOrbit:
    """
       2^12 = 4,096 dense ranks; 2,048 even-parity states are reachable

                  . . U . .
                  . . . . .
                  U . . . U
                  . . . . .
                  . . U . .

    . . U . .  . . U . .  . . U . .  . . U . .
    . . . . .  . . . . .  . . . . .  . . . . .
    U . . . U  U . . . U  U . . . U  U . . . U
    . . . . .  . . . . .  . . . . .  . . . . .
    . . U . .  . . U . .  . . U . .  . . U . .

                  . . U . .
                  . . . . .
                  U . . . U
                  . . . . .
                  . . U . .

       lookup-table-5x5x5-step903-EO-inner-orbit.cost-only.bin
       ======================================================
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
        (3, 103): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (11, 28): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (23, 53): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (15, 78): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (36, 115): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (40, 61): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (86, 65): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (90, 111): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (128, 73): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (136, 48): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (140, 98): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
        (148, 123): ["UB", "UL", "UR", "UF", "LB", "LF", "RB", "RF", "DB", "DL", "DR", "DF"],
    }

    def __init__(self, parent, build_state_index=False):
        del build_state_index
        self.parent = parent
        self.filename = PHASE3_EO_INNER_TABLE_555

    def rank(self):
        parent_state = self.parent.state
        rank = 0
        for index, (square, partner) in enumerate(zip(PHASE3_INNER_MIDGE_SQUARES_555, PHASE3_INNER_MIDGE_PARTNERS_555)):
            edge_str = parent_state[square] + parent_state[partner]
            oriented = edge_str in self.midge_states.get((square, partner), ())
            if not oriented:
                rank |= 1 << index
        return rank


class LookupTableIDA555LRCenterStageEOBothOrbits(LookupTableIDA555RankedCenters):
    def __init__(self, parent):
        self.parent = parent
        self.prune_tables = (
            parent.lt_phase3_lr_center_stage,
            parent.lt_phase3_eo_outer_orbit,
            parent.lt_phase3_eo_inner_orbit,
        )

    def solutions_via_c(
        self,
        pt_states=(),
        min_ida_threshold=None,
        max_ida_threshold=None,
        solution_count=1,
        **_kwargs,
    ):
        roots_filename = None
        roots = []
        download_file_if_needed(PHASE3_LR_CENTERS_TABLE_555)
        download_file_if_needed(PHASE3_EO_OUTER_TABLE_555)
        download_file_if_needed(PHASE3_EO_INNER_TABLE_555)
        cmd = [
            "./ida_search_555_phase3",
            "--lr-center-cost",
            PHASE3_LR_CENTERS_TABLE_555,
            "--eo-outer-cost",
            PHASE3_EO_OUTER_TABLE_555,
            "--eo-inner-cost",
            PHASE3_EO_INNER_TABLE_555,
        ]
        try:
            if not pt_states:
                pt_states = [
                    (
                        self.prune_tables[0].rank(),
                        self.prune_tables[1].rank(),
                        self.prune_tables[2].rank(),
                    )
                ]
            roots = list(pt_states)
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as roots_file:
                roots_filename = roots_file.name
                for root_id, (lr_rank, outer_rank, inner_rank) in enumerate(roots):
                    roots_file.write(f"{root_id},{lr_rank},{outer_rank},{inner_rank}\n")
            cmd.extend(("--roots-file", roots_filename))
            if min_ida_threshold is not None:
                cmd.extend(("--min-ida-threshold", str(min_ida_threshold)))
            if max_ida_threshold is not None:
                cmd.extend(("--max-ida-threshold", str(max_ida_threshold)))
            if solution_count != 1:
                cmd.extend(("--solution-count", str(solution_count)))
            output = self._run(cmd)
        finally:
            if roots_filename is not None:
                os.unlink(roots_filename)

        solutions = []
        solution_re = re.compile(r"^SOLUTION ROOT (\d+) \(\d+ steps\):(.*)$")
        for line in output.splitlines():
            match = solution_re.match(line)
            if match:
                root = roots[int(match.group(1))]
                solution = tuple(match.group(2).strip().split())
                solutions.append((len(solution), solution, root + (None, None)))
        if not solutions:
            raise NoIDASolution(f"Did not find SOLUTION line in\n{output}\n")
        solutions.sort()
        return [(solution, states) for _, solution, states in solutions]


# ==================================================
# phase 4
# park four edges on the x-plane
# ==================================================
class LookupTable555Phase4:
    """
               . x x x .
               x . . . x
               x . . . x
               x . . . x
               . x x x .

    . x x x .  . x x x .  . x x x .  . x x x .
    L . . . L  L . . . L  L . . . L  L . . . L
    L . . . L  L . . . L  L . . . L  L . . . L
    L . . . L  L . . . L  L . . . L  L . . . L
    . x x x .  . x x x .  . x x x .  . x x x .

               . x x x .
               x . . . x
               x . . . x
               x . . . x
               . x x x .

    lookup-table-5x5x5-step40-phase4.cost-only.bin
    ==============================================
    0 steps has 343,000 entries (0 percent, 0.00x previous step)
    1 steps has 679,250 entries (0 percent, 1.98x previous step)
    2 steps has 6,276,787 entries (5 percent, 9.24x previous step)
    3 steps has 25,090,688 entries (20 percent, 4.00x previous step)
    4 steps has 50,710,890 entries (41 percent, 2.02x previous step)
    5 steps has 34,813,744 entries (28 percent, 0.69x previous step)
    6 steps has 3,360,706 entries (2 percent, 0.10x previous step)
    7 steps has 12,310 entries (0 percent, 0.00x previous step)

    Total: 121,287,375 entries
    Average: 4.00 moves
    """

    def __init__(self, parent):
        self.parent = parent
        self.filename = PHASE4_EDGES_TABLE_555
        self.wing_strs = None
        self.solution_by_wing_strs = {}

    @staticmethod
    def _combination_rank(selected):
        remaining = 4
        rank = 0

        if sum(selected) != remaining:
            raise SolveError(f"phase-4 orbit must contain four selected edges, found {sum(selected)}")
        for position, is_selected in enumerate(selected):
            positions_after = len(selected) - position - 1
            if is_selected:
                remaining -= 1
            elif remaining:
                rank += comb(positions_after, remaining - 1)
        return rank

    def rank(self, wing_strs=None):
        selected = set(wing_strs if wing_strs is not None else self.wing_strs)
        rank = 0

        if len(selected) != 4:
            raise SolveError(f"phase 4 needs four distinct edges, found {len(selected)}")
        for squares, partners in (
            (PHASE4_HIGH_EDGE_SQUARES_555, PHASE4_HIGH_EDGE_PARTNERS_555),
            (PHASE4_MIDGE_SQUARES_555, PHASE4_MIDGE_PARTNERS_555),
            (PHASE4_LOW_EDGE_SQUARES_555, PHASE4_LOW_EDGE_PARTNERS_555),
        ):
            orbit_selected = []
            for square, partner in zip(squares, partners):
                edge = wing_str_map[self.parent.state[square] + self.parent.state[partner]]
                orbit_selected.append(edge in selected)
            rank = (rank * 495) + self._combination_rank(orbit_selected)
        return rank

    def solutions_via_c(self, wing_str_combos, max_ida_threshold=2):
        download_file_if_needed(self.filename)
        combos = [tuple(sorted(combo)) for combo in wing_str_combos]
        roots_filename = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as roots_file:
                roots_filename = roots_file.name
                for root_id, combo in enumerate(combos):
                    roots_file.write(f"{root_id},{self.rank(combo)}\n")
            cmd = [
                "./ida_search_555_phase4",
                "--roots-file",
                roots_filename,
                "--cost-table",
                self.filename,
                "--max-ida-threshold",
                str(max_ida_threshold),
            ]
            logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
            process = subprocess.run(cmd, capture_output=True, text=True)
            output = process.stdout
            self.parent.solve_via_c_output = f"\n{' '.join(cmd)}\n{output}\n"
            if process.returncode not in (0, 1):
                raise SolveError(f"{' '.join(cmd)} failed:\n{output}\n{process.stderr}")
        finally:
            if roots_filename is not None:
                os.unlink(roots_filename)

        results = []
        for line in output.splitlines():
            match = re.match(r"^SOLUTION ROOT (\d+) \((\d+) steps\):(.*)$", line)
            if not match:
                continue
            combo = combos[int(match.group(1))]
            solution = tuple(match.group(3).split())
            self.solution_by_wing_strs[combo] = solution
            results.append((len(solution), list(combo), solution))
        results.sort()
        return results

    def solve(self, print_steps=False) -> bool:
        combo = tuple(sorted(self.wing_strs))
        if combo not in self.solution_by_wing_strs:
            self.solutions_via_c((combo,))
        steps = self.solution_by_wing_strs.get(combo)
        if steps is None:
            return False
        for step in steps:
            self.parent.rotate(step)
            if print_steps:
                logger.info(f"{self}: step {step}")
        return True


# ==================================================
# phase 5
# pair those four edges; LR/FB centers to vertical bars
# ==================================================
class LookupTableIDA555Phase5:
    """Dedicated ranked phase-5 portfolio search."""

    centers_filename = "lookup-tables/lookup-table-5x5x5-step51-phase5-centers.cost-only.bin"
    high_filename = "lookup-tables/lookup-table-5x5x5-step55-phase5-fb-centers-high-edge-and-midge.cost-only.bin"
    low_filename = "lookup-tables/lookup-table-5x5x5-step57-phase5-fb-centers-low-edge-and-midge.cost-only.bin"

    def __init__(self, parent):
        self.parent = parent

    @staticmethod
    def _multiset_rank(state, symbols, counts):
        remaining = list(counts)
        permutations = 1
        slots = sum(counts)

        for count in counts:
            permutations *= comb(slots, count)
            slots -= count

        rank = 0
        for position, char in enumerate(state):
            slots = len(state) - position
            try:
                symbol_index = symbols.index(char)
            except ValueError as error:
                raise SolveError(f"phase-5 rank contains unknown symbol {char!r}") from error
            if not remaining[symbol_index]:
                raise SolveError(f"phase-5 rank contains too many {char!r} symbols")
            for smaller in range(symbol_index):
                rank += permutations * remaining[smaller] // slots
            permutations = permutations * remaining[symbol_index] // slots
            remaining[symbol_index] -= 1

        if any(remaining):
            raise SolveError("phase-5 rank has the wrong symbol counts")
        return rank

    def _binary_rank(self, squares, selected):
        state = ["L" if self.parent.state[square] in selected else "x" for square in squares]
        return self._multiset_rank(state, "Lx", (4, 4))

    def _fb_ranks(self):
        return (
            self._binary_rank(FB_t_centers_555, {"B"}),
            self._binary_rank(FB_x_centers_555, {"B"}),
        )

    def _combo_rank(self, wing_strs, wing_squares):
        selected = tuple(sorted(wing_strs))
        if len(selected) != 4 or len(set(selected)) != 4:
            raise SolveError(f"phase 5 needs four distinct edges, found {len(set(selected))}")

        label_by_edge = {edge: chr(ord("A") + index) for index, edge in enumerate(selected)}

        def edge_at(square):
            partner = edges_partner_555[square]
            return wing_str_map[self.parent.state[square] + self.parent.state[partner]]

        wing_state = "".join(label_by_edge.get(edge_at(square), "x") for square in wing_squares)
        midge_state = "".join(
            "L" if edge_at(square) in label_by_edge else "x" for square in PHASE5_XY_MIDGE_SQUARES_555
        )
        fb_t_rank, fb_x_rank = self._fb_ranks()
        wing_rank = self._multiset_rank(wing_state, "ABCDx", (1, 1, 1, 1, 4))
        midge_rank = self._multiset_rank(midge_state, "Lx", (4, 4))
        return (((fb_t_rank * 70) + fb_x_rank) * 1680 + wing_rank) * 70 + midge_rank

    def _midge_rank(self, wing_strs):
        selected = tuple(sorted(wing_strs))
        label_by_edge = {edge: chr(ord("A") + index) for index, edge in enumerate(selected)}
        state = []
        for square in PHASE5_XY_MIDGE_SQUARES_555:
            partner = edges_partner_555[square]
            edge = wing_str_map[self.parent.state[square] + self.parent.state[partner]]
            state.append(label_by_edge.get(edge, "x"))
        return self._multiset_rank(state, "ABCDx", (1, 1, 1, 1, 4))

    def ranks(self, wing_strs):
        lr_t_rank = self._binary_rank(LR_t_centers_555, {"L"})
        lr_x_rank = self._binary_rank(LR_x_centers_555, {"L"})
        fb_t_rank, fb_x_rank = self._fb_ranks()
        centers_rank = (((lr_t_rank * 70) + lr_x_rank) * 70 + fb_t_rank) * 70 + fb_x_rank
        return (
            centers_rank,
            self._combo_rank(wing_strs, PHASE5_XY_HIGH_SQUARES_555),
            self._combo_rank(wing_strs, PHASE5_XY_LOW_SQUARES_555),
            self._midge_rank(wing_strs),
        )

    def solutions_via_c(self, pt_states, solution_count=1, find_extra=False, max_ida_threshold=None):
        for filename in (self.centers_filename, self.high_filename, self.low_filename):
            download_file_if_needed(filename)

        roots = sorted(set(pt_states))
        roots_filename = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as roots_file:
                roots_filename = roots_file.name
                for root_id, root in enumerate(roots):
                    roots_file.write(f"{root_id},{root[0]},{root[1]},{root[2]},{root[3]}\n")

            cmd = [
                "./ida_search_555_phase5",
                "--roots-file",
                roots_filename,
                "--centers-cost",
                self.centers_filename,
                "--high-combo-cost",
                self.high_filename,
                "--low-combo-cost",
                self.low_filename,
                "--solution-count",
                str(solution_count),
            ]
            if find_extra:
                cmd.append("--find-extra")
            if max_ida_threshold is not None:
                cmd.extend(("--max-ida-threshold", str(max_ida_threshold)))

            logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
            process = subprocess.run(cmd, capture_output=True, text=True)
            output = process.stdout
            self.parent.solve_via_c_output = f"\n{' '.join(cmd)}\n{output}\n"
            if process.returncode not in (0, 1):
                raise SolveError(f"{' '.join(cmd)} failed:\n{output}\n{process.stderr}")
        finally:
            if roots_filename is not None:
                os.unlink(roots_filename)

        solutions = []
        pattern = re.compile(r"^SOLUTION ROOT (\d+) \((\d+) steps\):(.*)$")
        for line in output.splitlines():
            match = pattern.match(line)
            if match:
                root_id = int(match.group(1))
                solution = tuple(match.group(3).strip().split())
                solutions.append((len(solution), solution, roots[root_id]))

        if not solutions:
            raise NoIDASolution(f"Did not find SOLUTION line in\n{output}\n")
        solutions.sort()
        return [(solution, root) for _, solution, root in solutions]


# ==================================================
# phase 6
# pair the last eight edges and solve the centers
# ==================================================
class LookupTable555Phase6Centers(LookupTable):
    """
    6 * 6 * 4,900 = 176,400 states

               . . . . .
               . U U U .
               . U U U .
               . U U U .
               . . . . .

    . . . . .  . . . . .  . . . . .  . . . . .
    . L L L .  . F F F .  . R R R .  . B B B .
    . L L L .  . F F F .  . R R R .  . B B B .
    . L L L .  . F F F .  . R R R .  . B B B .
    . . . . .  . . . . .  . . . . .  . . . . .

               . . . . .
               . D D D .
               . D D D .
               . D D D .
               . . . . .

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
            illegal_moves=PHASE6_ILLEGAL_MOVES,
            use_state_index=True,
            build_state_index=build_state_index,
        )

    def state(self):
        parent_state = self.parent.state
        return "".join([parent_state[x] for x in centers_555])

    def populate_cube_from_state(self, state, cube, steps_to_solve):
        state = list(state)

        for pos, pos_state in zip(centers_555, state):
            cube[pos] = pos_state


class LookupTable555Phase6HighEdgeMidge(LookupTable):
    """
    8! = 40,320 states

               . U U - .
               - . . . U
               U . . . U
               U . . . -
               . - U U .

    . - L L .  . - F F .  . - R R .  . - B B .
    - . . . -  - . . . -  - . . . -  - . . . -
    - . . . -  - . . . -  - . . . -  - . . . -
    - . . . -  - . . . -  - . . . -  - . . . -
    . L L - .  . F F - .  . R R - .  . B B - .

               . D D - .
               - . . . D
               D . . . D
               D . . . -
               . - D D .

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
            illegal_moves=PHASE6_ILLEGAL_MOVES,
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
    8! = 40,320 states

               . - U U .
               U . . . -
               U . . . U
               - . . . U
               . U U - .

    . L L - .  . F F - .  . R R - .  . B B - .
    - . . . -  - . . . -  - . . . -  - . . . -
    - . . . -  - . . . -  - . . . -  - . . . -
    - . . . -  - . . . -  - . . . -  - . . . -
    . - L L .  . - F F .  . - R R .  . - B B .

               . - D D .
               D . . . -
               D . . . D
               - . . . D
               . D D - .

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
            illegal_moves=PHASE6_ILLEGAL_MOVES,
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


class LookupTableIDA555Phase6(LookupTableIDAViaGraph):
    """
    Pair the last eight edges and solve the centers
    """

    def __init__(self, parent):
        LookupTableIDAViaGraph.__init__(
            self,
            parent,
            all_moves=moves_555,
            illegal_moves=PHASE6_ILLEGAL_MOVES,
            prune_tables=(parent.lt_phase6_high_edge_midge, parent.lt_phase6_low_edge_midge, parent.lt_phase6_centers),
            # parent.lt_phase6_high_edge_midge and parent.lt_phase6_low_edge_midge are used to
            # compute the lookup index in the perfect hash file
            perfect_hash01_filename="lookup-table-5x5x5-step501-pair-last-eight-edges-edges-only.pt-state-perfect-hash",
            pt1_state_max=40320,
        )


class RubiksCube555(RubiksCube):
    """
    5x5x5 reduction: stage LR then FB centers, EO the edges, park and pair four
    x-plane edges, pair the last eight while solving the centers, then finish
    as a 3x3x3. See the module docstring for the six phases.
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

        # phase 1 - stage LR centers
        # t-center and x-center prune tables plus the IDA that reduce_333 searches.
        # lt_LR_t_centers_stage_ida is for larger cubes that have reduced to 555.
        self.lt_LR_t_centers_stage = LookupTable555LRTCenterStage(self)
        self.lt_LR_x_centers_stage = LookupTable555LRXCenterStage(self)
        self.lt_LR_centers_stage = LookupTableIDA555LRCenterStage(self)
        self.lt_LR_t_centers_stage_ida = LookupTableIDA555LRTCenterStage(self)

        # phase 2 - stage FB (and UD) centers
        self.lt_FB_t_centers_stage = LookupTable555FBTCenterStage(self)
        self.lt_FB_x_centers_stage = LookupTable555FBXCenterStage(self)
        self.lt_FB_centers_stage = LookupTableIDA555FBCentersStage(self)
        self.lt_FB_centers_stage.avoid_oll = 0

        # phase 3 - EO the wings and midges; LR centers to 1-of-432
        self.lt_phase3_lr_center_stage = LookupTable555Phase3LRCenterStage(self)
        self.lt_phase3_eo_outer_orbit = LookupTable555EdgeOrientOuterOrbit(self)
        self.lt_phase3_eo_inner_orbit = LookupTable555EdgeOrientInnerOrbit(self)
        self.lt_phase3 = LookupTableIDA555LRCenterStageEOBothOrbits(self)

        # phase 4 - park four edges on the x-plane
        self.lt_phase4 = LookupTable555Phase4(self)

        # phase 5 - pair those four edges; LR/FB centers to vertical bars
        self.lt_phase5 = LookupTableIDA555Phase5(self)

        # phase 6 - pair the last eight edges and solve the centers
        self.lt_phase6_centers = LookupTable555Phase6Centers(self)
        self.lt_phase6_high_edge_midge = LookupTable555Phase6HighEdgeMidge(self)
        self.lt_phase6_low_edge_midge = LookupTable555Phase6LowEdgeMidge(self)
        self.lt_phase6 = LookupTableIDA555Phase6(self)

    def highlow_edges_state(self):
        state = self.state
        result = []

        for x, y in self.reduce333_orient_edges_tuples:
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
        for edge_state_index, square_index, partner_index in (
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

    def eo_edges(self):
        """
        Our goal is to get the edges split into high/low groups but we do not care what
        the final orientation is of the edges. Each edge can either be in its final
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

        for _, square_index, partner_index in midges_recolor_tuples_555:
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            wing_strs.append(wing_str)

        # build a list of all possible EO permutations...an even number of edges must be high
        for num in range(4096):
            bits = str(bin(num)).lstrip("0b").zfill(12)
            if bits.count("1") % 2 == 0:
                permutations.append(list(map(int, bits)))

        pt_state_indexes = []
        for permutation in permutations:
            must_be_uppercase = []
            must_be_lowercase = []
            self.state = original_state[:]

            for wing_str, uppercase in zip(wing_strs, permutation):
                if uppercase:
                    must_be_uppercase.append(wing_str)
                else:
                    must_be_lowercase.append(wing_str)

            self.edges_flip_orientation(must_be_uppercase, must_be_lowercase)
            pt_state_indexes.append(
                (
                    self.lt_phase3_lr_center_stage.rank(),
                    self.lt_phase3_eo_outer_orbit.rank(),
                    self.lt_phase3_eo_inner_orbit.rank(),
                )
            )

        self.state = original_state[:]
        self.solution = original_solution[:]
        self.lt_phase3.solve_via_c(pt_states=pt_state_indexes)

        self.print_cube_add_comment("Phase 3: edges EOed into high/low groups", tmp_solution_len)
        self.post_eo_state = self.state[:]
        self.post_eo_solution = self.solution[:]

        # re-color the cube so that the edges are oriented correctly so we can
        # pair 4-edges then 8-edges. After all edge pairing is done we will uncolor
        # the cube and re-apply the solution.
        self.edges_flip_orientation(wing_strs, [])

    def find_first_four_edges_to_pair(self):
        """
        Rank all 12!/(4!*8!) = 495 four-edge combinations by phase-4 cost.
        Phase 4 parks the chosen four on the x-plane so phase 5 can pair them.
        """
        combos = itertools.combinations(wing_strs_all, 4)
        solutions = self.lt_phase4.solutions_via_c(combos, max_ida_threshold=2)
        return [(length, combo) for length, combo, _solution in solutions]

    def group_centers_phase1_and_2(self) -> None:
        """
        Find up to 64 optimal phase-1 LR-center solutions, then solve phase 2
        from all distinct endpoints and keep the pair with the shortest total
        solution. Phase-1 endpoints are grouped by orbit-0 parity because phase
        2 must use a different wide-turn parity constraint for each group.
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if self.centers_staged():
            return

        original_state = self.state[:]
        original_solution = self.solution[:]
        phase1_comment_start = len(self.solution)

        if self.LR_centers_staged():
            phase1_solutions = [((), (None, None, None, None, None))]
        else:
            phase1_solutions = self.lt_LR_centers_stage.solutions_via_c(solution_count=64)

        phase2_roots_by_parity = {}
        phase1_solution_by_root = {}
        representative_state_by_parity = {}
        logger.info("found %d optimal phase-1 solutions", len(phase1_solutions))

        for phase1_solution, _ in phase1_solutions:
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in phase1_solution:
                self.rotate(step)

            phase2_root = tuple(pt.rank() for pt in self.lt_FB_centers_stage.prune_tables)
            orbit0_has_oll = 0 in self.center_solution_leads_to_oll_parity()
            root_key = (orbit0_has_oll, phase2_root)

            if root_key not in phase1_solution_by_root:
                phase2_roots_by_parity.setdefault(orbit0_has_oll, []).append(phase2_root)
                phase1_solution_by_root[root_key] = phase1_solution
                representative_state_by_parity.setdefault(
                    orbit0_has_oll,
                    (self.state[:], self.solution[:]),
                )

        logger.info(
            "phase-1 portfolio has %d distinct phase-2 roots in %d parity groups",
            len(phase1_solution_by_root),
            len(phase2_roots_by_parity),
        )

        best = None
        for orbit0_has_oll, phase2_roots in phase2_roots_by_parity.items():
            representative_state, representative_solution = representative_state_by_parity[orbit0_has_oll]
            self.state = representative_state[:]
            self.solution = representative_solution[:]

            phase2_solution, phase2_states = self.lt_FB_centers_stage.solutions_via_c(pt_states=phase2_roots)[0]
            phase2_root = tuple(phase2_states[: len(self.lt_FB_centers_stage.prune_tables)])
            phase1_solution = phase1_solution_by_root[orbit0_has_oll, phase2_root]
            candidate = (
                len(phase1_solution) + len(phase2_solution),
                len(phase2_solution),
                phase1_solution,
                phase2_solution,
            )

            if best is None or candidate < best:
                best = candidate

        if best is None:
            raise SolveError("could not solve phase 2 from any phase-1 portfolio endpoint")

        _, _, best_phase1_solution, best_phase2_solution = best
        self.state = original_state[:]
        self.solution = original_solution[:]

        for step in best_phase1_solution:
            self.rotate(step)

        self.print_cube_add_comment("Phase 1: LR centers staged", phase1_comment_start)

        phase2_comment_start = len(self.solution)
        for step in best_phase2_solution:
            self.rotate(step)

        if not self.LR_centers_staged() or not self.FB_centers_staged():
            raise SolveError("phase-1 portfolio did not stage LR and FB centers")

        logger.info(
            "selected phase-1 length %d and phase-2 length %d (%d total)",
            len(best_phase1_solution),
            len(best_phase2_solution),
            len(best_phase1_solution) + len(best_phase2_solution),
        )
        self.print_cube_add_comment("Phase 2: UD FB centers staged", phase2_comment_start)

    def pair_edges(self):
        """
        Phases 4+5+6: park four edges on the x-plane, pair them while putting
        LR/FB centers into vertical bars, then pair the last eight and solve
        the centers. Keep the shortest combined path across the portfolio.
        """
        # We need the edge swaps to be even for our phase6 lookup tables to work.
        if self.edge_swaps_odd(False, 0, False):
            raise SolveError(f"{self} edge swaps are odd, cannot pair edges")

        # phase 4
        # phase 5
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(original_solution)
        phase5_roots = []
        phase5_root_to_wing_str_combo = {}

        for phase4_solution_len, wing_str_combo in self.find_first_four_edges_to_pair():
            if phase4_solution_len >= 3:
                break
            self.state = original_state[:]
            self.solution = original_solution[:]

            self.lt_phase4.wing_strs = wing_str_combo
            self.lt_phase4.solve()
            self.edges_flip_orientation(wing_str_combo, [])

            phase5_root = self.lt_phase5.ranks(wing_str_combo)
            phase5_root_to_wing_str_combo[phase5_root] = wing_str_combo
            phase5_roots.append(phase5_root)

        self.state = original_state[:]
        self.solution = original_solution[:]
        phase5_solutions = self.lt_phase5.solutions_via_c(pt_states=phase5_roots, solution_count=500, find_extra=True)

        # phase 6
        phase6_pt_state_indexes_to_prefix = {}

        for phase5_solution, phase5_root in phase5_solutions:
            wing_str_combo = phase5_root_to_wing_str_combo[phase5_root]
            self.state = original_state[:]
            self.solution = original_solution[:]

            self.lt_phase4.wing_strs = wing_str_combo
            self.lt_phase4.solve()
            phase4_solution = self.solution[original_solution_len:]

            self.edges_flip_orientation(wing_strs_all, [])

            for step in phase5_solution:
                self.rotate(step)

            if not self.x_plane_edges_paired():
                continue

            yz_plane_edges = tuple(list(self.get_y_plane_wing_strs()) + list(self.get_z_plane_wing_strs()))
            self.lt_phase6_high_edge_midge.ida_graph_node = None
            self.lt_phase6_low_edge_midge.ida_graph_node = None
            self.lt_phase6_high_edge_midge.wing_strs = yz_plane_edges
            self.lt_phase6_low_edge_midge.wing_strs = yz_plane_edges
            wing_str_combo_pt_state_indexes = tuple([pt.state_index() for pt in self.lt_phase6.prune_tables])

            # Several phase-4/phase-5 pairs can lead to the same phase-6 state. Since
            # they all share the same phase-6 cost from here on, keep the cheapest one.
            prefix_len = len(phase4_solution) + len(phase5_solution)
            previous_prefix = phase6_pt_state_indexes_to_prefix.get(wing_str_combo_pt_state_indexes)

            if previous_prefix is None:
                phase6_pt_state_indexes_to_prefix[wing_str_combo_pt_state_indexes] = (
                    phase4_solution,
                    phase5_solution,
                )
            elif prefix_len < len(previous_prefix[0]) + len(previous_prefix[1]):
                phase6_pt_state_indexes_to_prefix[wing_str_combo_pt_state_indexes] = (
                    phase4_solution,
                    phase5_solution,
                )

        # Phase 6's C search returns the first root that solves at the minimum
        # threshold, which ignores how expensive the phase-4/phase-5 prefix was.
        # Search each prefix-length group separately and keep the cheapest total.
        roots_by_prefix_len = {}
        for root, (phase4_solution, phase5_solution) in phase6_pt_state_indexes_to_prefix.items():
            prefix_len = len(phase4_solution) + len(phase5_solution)
            roots_by_prefix_len.setdefault(prefix_len, []).append(root)

        if not roots_by_prefix_len:
            raise SolveError("no ranked phase-5 solution paired the x-plane edges")

        best = None
        for prefix_len, roots in sorted(roots_by_prefix_len.items()):
            if best is not None and prefix_len >= best[0]:
                break

            phase6_solution, phase6_states = self.lt_phase6.solutions_via_c(pt_states=roots)[0]
            root = tuple(phase6_states[: len(self.lt_phase6.prune_tables)])
            phase4_solution, phase5_solution = phase6_pt_state_indexes_to_prefix[root]
            candidate = (
                prefix_len + len(phase6_solution),
                len(phase6_solution),
                phase4_solution,
                phase5_solution,
                phase6_solution,
            )

            if best is None or candidate < best:
                best = candidate

        if best is None:
            raise SolveError("could not solve phase 6 from any phase-4/5 portfolio endpoint")

        _, _, phase4_solution, phase5_solution, phase6_solution = best
        logger.info(
            "phases 4, 5, and 6 lengths %d + %d + %d (%d total) from %d prefix-length groups",
            len(phase4_solution),
            len(phase5_solution),
            len(phase6_solution),
            len(phase4_solution) + len(phase5_solution) + len(phase6_solution),
            len(roots_by_prefix_len),
        )

        # apply the solution
        self.state = self.post_eo_state
        self.solution = self.post_eo_solution[:]

        # phase 4
        tmp_solution_len = len(self.solution)
        for step in phase4_solution:
            self.rotate(step)

        self.print_cube_add_comment("Phase 4: four edges prepped for pairing", tmp_solution_len)

        # phase 5
        tmp_solution_len = len(self.solution)

        for step in phase5_solution:
            self.rotate(step)

        if not self.x_plane_edges_paired():
            raise SolveError("phase 5 did not pair the x-plane edges")
        self.print_cube_add_comment("Phase 5: x-plane edges paired, LR FB centers vertical bars", tmp_solution_len)

        # phase 6
        tmp_solution_len = len(self.solution)

        for step in phase6_solution:
            self.rotate(step)

        if not self.edges_paired() or not self.centers_solved():
            raise SolveError("phase 6 did not pair all edges and solve all centers")
        self.print_cube_add_comment("Phase 6: last eight edges paired, centers solved", tmp_solution_len)

    def reduce_333(self):
        """Stage centers, EO, pair edges, and solve centers so the cube is a 3x3x3."""
        self.lt_init()

        if self.centers_solved() and self.edges_paired():
            return

        self.rotate_U_to_U()
        self.rotate_F_to_F()

        self.group_centers_phase1_and_2()

        # phase 3
        self.eo_edges()

        # phases 4 5 and 6
        self.pair_edges()


def rotate_555(cube, step):
    return [cube[x] for x in swaps_555[step]]
