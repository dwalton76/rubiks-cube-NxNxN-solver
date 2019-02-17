#!/usr/bin/env python3

from rubikscubennnsolver import RubiksCube, NotSolving, wing_str_map, wing_strs_all
from rubikscubennnsolver.misc import pre_steps_to_try, get_swap_count
from rubikscubennnsolver.LookupTable import (
    get_characters_common_count,
    steps_on_same_face_and_layer,
    LookupTable,
    LookupTableCostOnly,
    LookupTableIDA,
    LookupTableHashCostOnly,
    LookupTableIDAViaC,
    NoSteps,
)
from rubikscubennnsolver.RubiksCube444Misc import (
    high_edges_444,
    low_edges_444,
    highlow_edge_mapping_combinations,
    highlow_edge_values,
    step161_index,
    step162_index,
)
from rubikscubennnsolver.RubiksSide import SolveError
from pprint import pformat
import itertools
import logging
import sys

log = logging.getLogger(__name__)

moves_444 = (
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

solved_444 = 'UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB'

centers_444 = (
    6, 7, 10, 11,   # Upper
    22, 23, 26, 27, # Left
    38, 39, 42, 43, # Front
    54, 55, 58, 59, # Right
    70, 71, 74, 75, # Back
    86, 87, 90, 91  # Down
)

LFRB_centers_444 = (
    22, 23, 26, 27, # Left
    38, 39, 42, 43, # Front
    54, 55, 58, 59, # Right
    70, 71, 74, 75, # Back
)

LR_centers_444 = (
    22, 23, 26, 27, # Left
    54, 55, 58, 59  # Right
)

corners_444 = (
    1, 4, 13, 16,
    17, 20, 29, 32,
    33, 36, 45, 48,
    49, 52, 61, 64,
    65, 68, 77, 80,
    81, 84, 93, 96
)

edges_444 = (
    2, 3, 5, 8, 9, 12, 14, 15,      # Upper
    18, 19, 21, 24, 25, 28, 30, 31, # Left
    34, 35, 37, 40, 41, 44, 46, 47, # Front
    50, 51, 53, 56, 57, 60, 62, 63, # Right
    66, 67, 69, 72, 73, 76, 78, 79, # Back
    82, 83, 85, 88, 89, 92, 94, 95  # Down
)

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

edges_partner_444 = {
    2: 67,
    3: 66,
    5: 18,
    8: 51,
    9: 19,
    12: 50,
    14: 34,
    15: 35,
    18: 5,
    19: 9,
    21: 72,
    24: 37,
    25: 76,
    28: 41,
    30: 89,
    31: 85,
    34: 14,
    35: 15,
    37: 24,
    40: 53,
    41: 28,
    44: 57,
    46: 82,
    47: 83,
    50: 12,
    51: 8,
    53: 40,
    56: 69,
    57: 44,
    60: 73,
    62: 88,
    63: 92,
    66: 3,
    67: 2,
    69: 56,
    72: 21,
    73: 60,
    76: 25,
    78: 95,
    79: 94,
    82: 46,
    83: 47,
    85: 31,
    88: 62,
    89: 30,
    92: 63,
    94: 79,
    95: 78
}

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
    ('n', 95, 78)
)

symmetry_rotations_tsai_phase3_444 = (\
    (),
    ('x',),
    ("x'",),
    ('x', 'x'),
    ('y', 'y'),
    ('z', 'z'),
    ('x', 'y', 'y'),
    ('x', 'z', 'z'),
    ('reflect-x',),
    ('reflect-x', 'x'),
    ('reflect-x', "x'"),
    ('reflect-x', 'x', 'x'),
    ('reflect-x', 'y', 'y'),
    ('reflect-x', 'z', 'z'),
    ('reflect-x', 'x', 'y', 'y'),
    ('reflect-x', 'x', 'z', 'z'),
)


def edges_recolor_pattern_444(state, only_colors=[]):

    edge_map = {
        'UB' : [],
        'UL' : [],
        'UR' : [],
        'UF' : [],
        'LB' : [],
        'LF' : [],
        'RB' : [],
        'RF' : [],
        'DB' : [],
        'DL' : [],
        'DR' : [],
        'DF' : [],
        '--' : [],
    }

    # Record the two edge_indexes for each of the 12 edges
    for (edge_index, square_index, partner_index) in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = wing_str_map[square_value + partner_value]
        edge_map[wing_str].append(edge_index)

    # Where is the other wing_str like us?
    for (edge_index, square_index, partner_index) in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = wing_str_map[square_value + partner_value]

        if only_colors and wing_str not in only_colors:
            state[square_index] = '-'
            state[partner_index] = '-'
        else:
            if wing_str == '--':
                state[square_index] = '-'
                state[partner_index] = '-'
            else:
                for tmp_index in edge_map[wing_str]:
                    if tmp_index != edge_index:
                        state[square_index] = tmp_index
                        state[partner_index] = tmp_index
                        break
                else:
                    raise Exception("could not find tmp_index")

    return ''.join(state)


# ===============================
# --fast, --normal, --slow tables
# ===============================
class LookupTable444HighLowEdgesEdges(LookupTable):
    """
    lookup-table-4x4x4-step21-highlow-edges-edges.txt
    =================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
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

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step21-highlow-edges-edges.txt',
            'UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
            linecount=2704156,
            max_depth=10,
            filesize=227149104)


class LookupTable444HighLowEdgesCenters(LookupTable):
    """
    lookup-table-4x4x4-step22-highlow-edges-centers.txt
    ===================================================
    1 steps has 22 entries (31 percent, 0.00x previous step)
    2 steps has 16 entries (22 percent, 0.73x previous step)
    3 steps has 16 entries (22 percent, 1.00x previous step)
    4 steps has 16 entries (22 percent, 1.00x previous step)

    Total: 70 entries
    Average: 2.37 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step22-highlow-edges-centers.txt',
            ('LLLLRRRR',
             'LLRRLLRR',
             'LLRRRRLL',
             'LRLRLRLR',
             'LRLRRLRL',
             'LRRLRLLR',
             'RLLRLRRL',
             'RLRLLRLR',
             'RLRLRLRL',
             'RRLLLLRR',
             'RRLLRRLL',
             'RRRRLLLL'),
            linecount=70,
            max_depth=4,
            filesize=1610)


class LookupTableIDA444HighLowEdges(LookupTableIDA):
    """
    lookup-table-4x4x4-step20-highlow-edges.txt
    ===========================================
    1 steps has 36 entries (0 percent, 0.00x previous step)
    2 steps has 348 entries (0 percent, 9.67x previous step)
    3 steps has 3,416 entries (0 percent, 9.82x previous step)
    4 steps has 26,260 entries (1 percent, 7.69x previous step)
    5 steps has 226,852 entries (9 percent, 8.64x previous step)
    6 steps has 2,048,086 entries (88 percent, 9.03x previous step)

    Total: 2,304,998 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step20-highlow-edges.txt',
            ('LLLLRRRRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'LLRRLLRRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'LLRRRRLLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'LRLRLRLRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'LRLRRLRLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'LRRLRLLRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'RLLRLRRLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'RLRLLRLRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'RLRLRLRLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'RRLLLLRRUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'RRLLRRLLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
             'RRRRLLLLUDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU'),
            moves_444,

            ("Uw", "Uw'",
             "Dw", "Dw'",
             "Fw", "Fw'",
             "Bw", "Bw'",
             "Lw", "Lw'",
             "Rw", "Rw'"),

            linecount=2304998,
            max_depth=6,
            filesize=182094842)

    def state(self):
        parent_state = self.parent.state
        LR_centers = ''.join([parent_state[x] for x in LR_centers_444])
        edges = self.parent.highlow_edges_state(self.parent.edge_mapping)
        return LR_centers + edges

    def ida_heuristic(self):
        parent_state = self.parent.state
        LR_centers = ''.join([parent_state[x] for x in LR_centers_444])
        edges_state = self.parent.highlow_edges_state(self.parent.edge_mapping)
        lt_state = LR_centers + edges_state

        cost_to_goal = max(
            self.parent.lt_highlow_edges_edges.heuristic(edges_state),
            self.parent.lt_highlow_edges_centers.heuristic(LR_centers),
        )

        return (lt_state, cost_to_goal)


# =============
# --fast tables
# =============
class LookupTable444UDCentersStage(LookupTable):
    """
    lookup-table-4x4x4-step110-UD-centers-stage.txt
    ===============================================
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

    state_targets = (
        'xxxxxxxxUUUUxxxxUUUUxxxx',
        'xxxxUUUUxxxxUUUUxxxxxxxx',
        'UUUUxxxxxxxxxxxxxxxxUUUU',
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step110-UD-centers-stage.txt',
            self.state_targets,
            linecount=735471,
            max_depth=8,
            filesize=39715434)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join(['U' if parent_state[x] in ('U', 'D') else 'x' for x in centers_444])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable444LRFBCentersStageEven(LookupTable):
    """
    lookup-table-4x4x4-step120-LRFB-centers-stage-even.txt
    ======================================================
    1 steps has 2 entries (0 percent, 0.00x previous step)
    3 steps has 56 entries (0 percent, 28.00x previous step)
    4 steps has 594 entries (4 percent, 10.61x previous step)
    5 steps has 3,878 entries (30 percent, 6.53x previous step)
    6 steps has 7,032 entries (54 percent, 1.81x previous step)
    7 steps has 1,212 entries (9 percent, 0.17x previous step)
    8 steps has 96 entries (0 percent, 0.08x previous step)

    Total: 12,870 entries
    Average: 5.70 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step120-LRFB-centers-stage-even.txt',
            ('LLLLxxxxLLLLxxxx',
             'xxxxLLLLxxxxLLLL'),
            linecount=12870,
            max_depth=7,
            filesize=592020)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join(['L' if parent_state[x] in ('L', 'R') else 'x' for x in LFRB_centers_444])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTable444LRFBCentersStageOdd(LookupTable):
    """
    lookup-table-4x4x4-step120-LRFB-centers-stage-odd.txt
    =====================================================
    1 steps has 2 entries (0 percent, 0.00x previous step)
    2 steps has 28 entries (0 percent, 14.00x previous step)
    3 steps has 178 entries (1 percent, 6.36x previous step)
    4 steps has 710 entries (5 percent, 3.99x previous step)
    5 steps has 1,690 entries (13 percent, 2.38x previous step)
    6 steps has 5,284 entries (41 percent, 3.13x previous step)
    7 steps has 4,890 entries (37 percent, 0.93x previous step)
    8 steps has 88 entries (0 percent, 0.02x previous step)

    Total: 12,870 entries
    Average: 6.10 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step120-LRFB-centers-stage-odd.txt',
            ('LLLLxxxxLLLLxxxx',
             'xxxxLLLLxxxxLLLL'),
            linecount=12870,
            max_depth=7,
            filesize=579150)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join(['L' if parent_state[x] in ('L', 'R') else 'x' for x in LFRB_centers_444])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)



class LookupTable444LRFBCentersSolve(LookupTable):
    """
    lookup-table-4x4x4-step130-LRFB-centers-solve.txt
    =================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 63 entries (1 percent, 9.00x previous step)
    3 steps has 310 entries (6 percent, 4.92x previous step)
    4 steps has 820 entries (16 percent, 2.65x previous step)
    5 steps has 1,168 entries (23 percent, 1.42x previous step)
    6 steps has 1,316 entries (26 percent, 1.13x previous step)
    7 steps has 992 entries (20 percent, 0.75x previous step)
    8 steps has 224 entries (4 percent, 0.23x previous step)

    Total: 4,900 entries
    Average: 5.47 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step130-LRFB-centers-solve.txt',
            'LLLLFFFFRRRRBBBB',
            linecount=4900,
            max_depth=8,
            filesize=220500)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join([parent_state[x] for x in LFRB_centers_444])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


# These step140 classes/tables were used by utils/build-444-edges-step150.py to
# IDA all 5.8 million 4-edge cases to build the step150 table
class LookupTable444FirstFourEdgesEdgesOnly(LookupTableHashCostOnly):
    """
    lookup-table-4x4x4-step141.txt
    =============================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 27 entries (0 percent, 6.75x previous step)
    3 steps has 216 entries (0 percent, 8.00x previous step)
    4 steps has 1,418 entries (0 percent, 6.56x previous step)
    5 steps has 9,623 entries (0 percent, 6.79x previous step)
    6 steps has 63,448 entries (1 percent, 6.59x previous step)
    7 steps has 365,270 entries (6 percent, 5.76x previous step)
    8 steps has 1,548,382 entries (26 percent, 4.24x previous step)
    9 steps has 3,061,324 entries (52 percent, 1.98x previous step)
    10 steps has 830,336 entries (14 percent, 0.27x previous step)
    11 steps has 552 entries (0 percent, 0.00x previous step)

    Total: 5,880,600 entries
    Average: 8.71 moves
    """

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step141.txt',
            '--------a8b9ecfd--------',
            linecount=5880600,
            max_depth=11,
            filesize=370477800)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step141.hash-cost-only.txt',
            '--------a8b9ecfd--------',
            linecount=1,
            max_depth=11,
            bucketcount=5880601,
            filesize=5880602)

    def ida_heuristic(self):
        parent_state = self.parent.state
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        state = edges_recolor_pattern_444(parent_state[:], self.only_colors)
        edges_state = ''.join([state[index] for index in wings_444])
        cost_to_goal = self.heuristic(edges_state)
        #log.info("%s: %s cost_to_goal %s" % (self, edges_state, cost_to_goal))
        return (edges_state, cost_to_goal)


class LookupTable444FirstFourEdgesCentersOnly(LookupTable):
    """
    lookup-table-4x4x4-step142.txt
    ==============================
    1 steps has 116 entries (13 percent, 0.00x previous step)
    2 steps has 212 entries (25 percent, 1.83x previous step)
    3 steps has 288 entries (34 percent, 1.36x previous step)
    4 steps has 192 entries (22 percent, 0.67x previous step)
    5 steps has 32 entries (3 percent, 0.17x previous step)

    Total: 840 entries
    Average: 2.78 moves
    """

    state_targets = (
        'LLLLBBBBRRRRFFFF', 'LLLLBFBFRRRRBFBF', 'LLLLBFBFRRRRFBFB', 'LLLLFBFBRRRRBFBF',
        'LLLLFBFBRRRRFBFB', 'LLLLFFFFRRRRBBBB', 'LRLRBBBBLRLRFFFF', 'LRLRBBBBRLRLFFFF',
        'LRLRBFBFLRLRBFBF', 'LRLRBFBFLRLRFBFB', 'LRLRBFBFRLRLBFBF', 'LRLRBFBFRLRLFBFB',
        'LRLRFBFBLRLRBFBF', 'LRLRFBFBLRLRFBFB', 'LRLRFBFBRLRLBFBF', 'LRLRFBFBRLRLFBFB',
        'LRLRFFFFLRLRBBBB', 'LRLRFFFFRLRLBBBB', 'RLRLBBBBLRLRFFFF', 'RLRLBBBBRLRLFFFF',
        'RLRLBFBFLRLRBFBF', 'RLRLBFBFLRLRFBFB', 'RLRLBFBFRLRLBFBF', 'RLRLBFBFRLRLFBFB',
        'RLRLFBFBLRLRBFBF', 'RLRLFBFBLRLRFBFB', 'RLRLFBFBRLRLBFBF', 'RLRLFBFBRLRLFBFB',
        'RLRLFFFFLRLRBBBB', 'RLRLFFFFRLRLBBBB', 'RRRRBBBBLLLLFFFF', 'RRRRBFBFLLLLBFBF',
        'RRRRBFBFLLLLFBFB', 'RRRRFBFBLLLLBFBF', 'RRRRFBFBLLLLFBFB', 'RRRRFFFFLLLLBBBB'
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step142.txt',
            self.state_targets,
            linecount=840,
            max_depth=5,
            filesize=29400)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join([parent_state[x] for x in LFRB_centers_444])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA444FirstFourEdges(LookupTableIDA):
    """
    lookup-table-4x4x4-step140.txt
    =============================
    1 steps has 144 entries (0 percent, 0.00x previous step)
    2 steps has 1,020 entries (0 percent, 7.08x previous step)
    3 steps has 8,448 entries (1 percent, 8.28x previous step)
    4 steps has 64,172 entries (11 percent, 7.60x previous step)
    5 steps has 494,692 entries (87 percent, 7.71x previous step)

    Total: 568,476 entries
    Average: 4.85 moves
    """

    state_targets = (
        'LLLLBBBBRRRRFFFF--------a8b9ecfd--------',
        'LLLLBFBFRRRRBFBF--------a8b9ecfd--------',
        'LLLLBFBFRRRRFBFB--------a8b9ecfd--------',
        'LLLLFBFBRRRRBFBF--------a8b9ecfd--------',
        'LLLLFBFBRRRRFBFB--------a8b9ecfd--------',
        'LLLLFFFFRRRRBBBB--------a8b9ecfd--------',
        'LRLRBBBBLRLRFFFF--------a8b9ecfd--------',
        'LRLRBBBBRLRLFFFF--------a8b9ecfd--------',
        'LRLRBFBFLRLRBFBF--------a8b9ecfd--------',
        'LRLRBFBFLRLRFBFB--------a8b9ecfd--------',
        'LRLRBFBFRLRLBFBF--------a8b9ecfd--------',
        'LRLRBFBFRLRLFBFB--------a8b9ecfd--------',
        'LRLRFBFBLRLRBFBF--------a8b9ecfd--------',
        'LRLRFBFBLRLRFBFB--------a8b9ecfd--------',
        'LRLRFBFBRLRLBFBF--------a8b9ecfd--------',
        'LRLRFBFBRLRLFBFB--------a8b9ecfd--------',
        'LRLRFFFFLRLRBBBB--------a8b9ecfd--------',
        'LRLRFFFFRLRLBBBB--------a8b9ecfd--------',
        'RLRLBBBBLRLRFFFF--------a8b9ecfd--------',
        'RLRLBBBBRLRLFFFF--------a8b9ecfd--------',
        'RLRLBFBFLRLRBFBF--------a8b9ecfd--------',
        'RLRLBFBFLRLRFBFB--------a8b9ecfd--------',
        'RLRLBFBFRLRLBFBF--------a8b9ecfd--------',
        'RLRLBFBFRLRLFBFB--------a8b9ecfd--------',
        'RLRLFBFBLRLRBFBF--------a8b9ecfd--------',
        'RLRLFBFBLRLRFBFB--------a8b9ecfd--------',
        'RLRLFBFBRLRLBFBF--------a8b9ecfd--------',
        'RLRLFBFBRLRLFBFB--------a8b9ecfd--------',
        'RLRLFFFFLRLRBBBB--------a8b9ecfd--------',
        'RLRLFFFFRLRLBBBB--------a8b9ecfd--------',
        'RRRRBBBBLLLLFFFF--------a8b9ecfd--------',
        'RRRRBFBFLLLLBFBF--------a8b9ecfd--------',
        'RRRRBFBFLLLLFBFB--------a8b9ecfd--------',
        'RRRRFBFBLLLLBFBF--------a8b9ecfd--------',
        'RRRRFBFBLLLLFBFB--------a8b9ecfd--------',
        'RRRRFFFFLLLLBBBB--------a8b9ecfd--------'
    )

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step140.txt',
            self.state_targets,
            moves_444,

            # illegal moves
            ("Uw", "Uw'",
             "Lw", "Lw'",
             "Fw", "Fw'",
             "Rw", "Rw'",
             "Bw", "Bw'",
             "Dw", "Dw'",
             "L", "L'",
             "R", "R'"),

            linecount=568476,
            max_depth=5,
            filesize=34108560,

            #linecount=4453748,
            #max_depth=6,
            #filesize=280586124,
        )


    def ida_heuristic(self):
        (edges_state, edges_cost_to_goal) = self.parent.lt_pair_first_four_edges_edges_only.ida_heuristic()
        (centers_state, centers_cost_to_goal) = self.parent.lt_pair_first_four_edges_centers_only.ida_heuristic()
        cost_to_goal = max(centers_cost_to_goal, edges_cost_to_goal)
        lt_state = centers_state + edges_state

        if cost_to_goal > 0:
            steps = self.steps(lt_state)

            if steps:
                cost_to_goal = len(steps)
            else:
                cost_to_goal = max(cost_to_goal, self.max_depth + 1)

        return (lt_state, cost_to_goal)


class LookupTable444FirstFourEdges(LookupTable):
    """
    lookup-table-4x4x4-step150.txt
    ==============================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 17 entries (0 percent, 5.67x previous step)
    3 steps has 112 entries (0 percent, 6.59x previous step)
    4 steps has 380 entries (0 percent, 3.39x previous step)
    5 steps has 1,493 entries (0 percent, 3.93x previous step)
    6 steps has 7,833 entries (0 percent, 5.25x previous step)
    7 steps has 37,972 entries (0 percent, 4.85x previous step)
    8 steps has 188,240 entries (3 percent, 4.96x previous step)
    9 steps has 892,232 entries (15 percent, 4.74x previous step)
    10 steps has 2,971,620 entries (50 percent, 3.33x previous step)
    11 steps has 1,775,802 entries (30 percent, 0.60x previous step)
    12 steps has 4,896 entries (0 percent, 0.00x previous step)

    Total: 5,880,600 entries
    Average: 10.06 moves
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step150.txt',
            '--------a8b9ecfd--------',
            linecount=5880600,
            max_depth=12,
            filesize=388119600,
        )

    def ida_heuristic(self):
        parent_state = self.parent.state
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        state = edges_recolor_pattern_444(parent_state[:], self.only_colors)
        edges_state = ''.join([state[index] for index in wings_444])
        cost_to_goal = self.heuristic(edges_state)
        # log.info("%s: %s,  %s cost_to_goal %s" % (self, pformat(self.only_colors), edges_state, cost_to_goal))
        return (edges_state, cost_to_goal)



class LookupTable444LastEightEdges(LookupTable):
    """
    Originally this phase used an IDA search where
    - the step160 table was 7-deep
    - step161 was the edges prune table
    - step162 was the centers prune table

    lookup-table-4x4x4-step160.txt
    ==============================
    1 steps has 12 entries (0 percent, 0.00x previous step)
    2 steps has 72 entries (0 percent, 6.00x previous step)
    3 steps has 492 entries (0 percent, 6.83x previous step)
    4 steps has 3,012 entries (0 percent, 6.12x previous step)
    5 steps has 17,300 entries (0 percent, 5.74x previous step)
    6 steps has 92,360 entries (0 percent, 5.34x previous step)
    7 steps has 488,720 entries (0 percent, 5.29x previous step)
    8 steps has 2,355,400 entries (4 percent, 4.82x previous step)
    9 steps has 9,416,496 entries (18 percent, 4.00x previous step)
    10 steps has 22,811,984 entries (44 percent, 2.42x previous step)
    11 steps has 15,092,664 entries (29 percent, 0.66x previous step)
    12 steps has 524,688 entries (1 percent, 0.03x previous step)

    Total: 50,803,200 entries
    Average: 10.00 moves


    lookup-table-4x4x4-step161.txt
    ==============================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 10 entries (0 percent, 3.33x previous step)
    3 steps has 36 entries (0 percent, 3.60x previous step)
    4 steps has 165 entries (0 percent, 4.58x previous step)
    5 steps has 606 entries (3 percent, 3.67x previous step)
    6 steps has 1,937 entries (9 percent, 3.20x previous step)
    7 steps has 5,172 entries (25 percent, 2.67x previous step)
    8 steps has 7,719 entries (38 percent, 1.49x previous step)
    9 steps has 4,344 entries (21 percent, 0.56x previous step)
    10 steps has 168 entries (0 percent, 0.04x previous step)

    Total: 20,160 entries
    Average: 7.65 moves


    lookup-table-4x4x4-step162.txt
    ==============================
    1 steps has 12 entries (0 percent, 0.00x previous step)
    2 steps has 72 entries (2 percent, 6.00x previous step)
    3 steps has 348 entries (13 percent, 4.83x previous step)
    4 steps has 820 entries (32 percent, 2.36x previous step)
    5 steps has 804 entries (31 percent, 0.98x previous step)
    6 steps has 464 entries (18 percent, 0.58x previous step)

    Total: 2,520 entries
    Average: 4.48 moves

    In an effort to make this solver run faster on a raspberry pi I decided to move
    away from IDA here and build out all 50 million entries...I did and the file
    was 4.4G!! The step160 table entries were in the form

        UUUURRRRBBBBLLLLFFFFDDDD10425376a8b9ecfdhgkiljnm

    where there were 2,520 center states and 20,160 edges states.  This means we can
    use the centers state and edges state as perfect hash via this formula:

        centers_state = state_to_find[0:24]
        edges_state = state_to_find[24:]
        centers_index = step162_index[centers_state]
        edges_index = step161_index[edges_state]
        index = (centers_index * 20160) + edges_index

    so we took step160.txt, took the first move for each state, abbreviated that step
    to a single character (moves_444 has 36 entries so 0-9 and a-z were used), and
    wrote one character per state to lookup-table-4x4x4-step160-perfect-hash.txt.
    """

    state_targets = (
        'DDDDLLLLBBBBRRRRFFFFUUUU10425376a8b9ecfdhgkiljnm',
        'DDDDRRRRFFFFLLLLBBBBUUUU10425376a8b9ecfdhgkiljnm',
        'UUUULLLLFFFFRRRRBBBBDDDD10425376a8b9ecfdhgkiljnm',
        'UUUURRRRBBBBLLLLFFFFDDDD10425376a8b9ecfdhgkiljnm'
    )

    # See utils/444-convert-step160-to-perfect-hash.py for the reverse of this
    # that was used to build lookup-table-4x4x4-step160-perfect-hash.txt
    abbr_to_move_444 = {
        "0" : "U",
        "1" : "U'",
        "2" : "U2",
        "3" : "Uw",
        "4" : "Uw'",
        "5" : "Uw2",
        "6" : "L",
        "7" : "L'",
        "8" : "L2",
        "9" : "Lw",
        "a" : "Lw'",
        "b" : "Lw2",
        "c" : "F",
        "d" : "F'",
        "e" : "F2",
        "f" : "Fw",
        "g" : "Fw'",
        "h" : "Fw2",
        "i" : "R",
        "j" : "R'",
        "k" : "R2",
        "l" : "Rw",
        "m" : "Rw'",
        "n" : "Rw2",
        "o" : "B",
        "p" : "B'",
        "q" : "B2",
        "r" : "Bw",
        "s" : "Bw'",
        "t" : "Bw2",
        "u" : "D",
        "v" : "D'",
        "w" : "D2",
        "x" : "Dw",
        "y" : "Dw'",
        "z" : "Dw2",
    }

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step160-perfect-hash.txt',
            self.state_targets,
            linecount=50803200,
            max_depth=12,
            filesize=50803200)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = edges_recolor_pattern_444(parent_state[:])
        edges_state = ''.join([state[index] for index in wings_444])
        centers_state = ''.join([parent_state[x] for x in centers_444])
        lt_state = centers_state + edges_state

        cost_to_goal = self.heuristic(lt_state)
        return (lt_state, cost_to_goal)

    def steps(self, state_to_find):
        """
        This uses a perfect hash to jump straight to the entry we want
        """
        centers_state = state_to_find[0:24]
        edges_state = state_to_find[24:]
        centers_index = step162_index[centers_state]
        edges_index = step161_index[edges_state]

        # There are 20160 edge states
        index = (centers_index * 20160) + edges_index

        step_abbr = chr(self.cache_string[index])
        step = self.abbr_to_move_444[step_abbr]
        return [step]


# ======================
# --normal/--slow tables
# ======================
class LookupTableIDA444ULFRBDCentersStage(LookupTableIDAViaC):
    """
    lookup-table-4x4x4-step11-UD-centers-stage.txt
    lookup-table-4x4x4-step12-LR-centers-stage.txt
    lookup-table-4x4x4-step13-FB-centers-stage.txt
    ==============================================
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


    lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt
    ==================================================
    1 steps has 24 entries (0 percent, 0.00x previous step)
    2 steps has 324 entries (0 percent, 13.50x previous step)
    3 steps has 4,302 entries (0 percent, 13.28x previous step)
    4 steps has 53,730 entries (7 percent, 12.49x previous step)
    5 steps has 697,806 entries (92 percent, 12.99x previous step)

    Total: 756,186 entries
    """

    def __init__(self, parent):

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (('lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt', 1576260, '4696649132d2d5895ccb294eea4e25f5'), # 4-deep
             ('lookup-table-4x4x4-step11-UD-centers-stage.cost-only.txt', 16711681, '504553715ca5632e90a81c9ecd4aa749'),
             ('lookup-table-4x4x4-step12-LR-centers-stage.cost-only.txt', 16711681, '504553715ca5632e90a81c9ecd4aa749'),
             ('lookup-table-4x4x4-step13-FB-centers-stage.cost-only.txt', 16711681, '504553715ca5632e90a81c9ecd4aa749')),
            '4x4x4-centers-stage' # C_ida_type
        )

        self.recolor_positions = centers_444
        self.recolor_map = {
            'D' : 'U',
            'R' : 'L',
            'B' : 'F',
        }
        self.nuke_corners = True


class LookupTableIDA444Reduce333(LookupTableIDAViaC):
    """
    lookup-table-4x4x4-step31-reduce333-edges.txt
    =============================================
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
    Average: 10.635709 moves


    lookup-table-4x4x4-step32-reduce333-centers.txt
    ===============================================
    1 steps has 16 entries (0 percent, 0.00x previous step)
    2 steps has 136 entries (0 percent, 8.50x previous step)
    3 steps has 952 entries (1 percent, 7.00x previous step)
    4 steps has 4,048 entries (6 percent, 4.25x previous step)
    5 steps has 10,588 entries (18 percent, 2.62x previous step)
    6 steps has 16,620 entries (28 percent, 1.57x previous step)
    7 steps has 16,392 entries (27 percent, 0.99x previous step)
    8 steps has 8,768 entries (14 percent, 0.53x previous step)
    9 steps has 1,280 entries (2 percent, 0.15x previous step)

    Total: 58,800 entries
    Average: 6.27 moves


    lookup-table-4x4x4-step30-reduce333.txt
    =======================================
    1 steps has 16 entries (0 percent, 0.00x previous step)
    2 steps has 136 entries (0 percent, 8.50x previous step)
    3 steps has 1,424 entries (0 percent, 10.47x previous step)
    4 steps has 14,032 entries (0 percent, 9.85x previous step)
    5 steps has 134,052 entries (9 percent, 9.55x previous step)
    6 steps has 1,290,292 entries (89 percent, 9.63x previous step)

    Total: 1,439,952 entries
    """

    def __init__(self, parent):

        LookupTableIDAViaC.__init__(
            self,
            parent,
            # Needed tables and their md5 signatures
            (('lookup-table-4x4x4-step30-reduce333.txt', 73437552, '82fbc3414d07e53448d0746d96e25ebd'), # 6-deep
             ('lookup-table-4x4x4-step31-reduce333-edges.hash-cost-only.txt', 239500848, '20ac2ed7ca369c3b5183f836f5d99262'),
             ('lookup-table-4x4x4-step32-reduce333-centers.hash-cost-only.txt', None, '3f990fc1fb6bf506d81ba65f03ad74f6')),
            '4x4x4-reduce-333' # C_ida_type
        )


class RubiksCube444(RubiksCube):

    instantiated = False

    reduce333_orient_edges_tuples = (
        (2, 67), (3, 66), (5, 18), (8, 51), (9, 19), (12, 50), (14, 34), (15, 35),
        (18, 5), (19, 9), (21, 72), (24, 37), (25, 76), (28, 41), (30, 89), (31, 85),
        (34, 14), (35, 15), (37, 24), (40, 53), (41, 28), (44, 57), (46, 82), (47, 83),
        (50, 12), (51, 8), (53, 40), (56, 69), (57, 44), (60, 73), (62, 88), (63, 92),
        (66, 3), (67, 2), (69, 56), (72, 21), (73, 60), (76, 25), (78, 95), (79, 94),
        (82, 46), (83, 47), (85, 31), (88, 62), (89, 30), (92, 63), (94, 79), (95, 78)
    )

    def __init__(self, state, order, colormap=None, avoid_pll=True, debug=False):
        RubiksCube.__init__(self, state, order, colormap, debug)
        self.avoid_pll = avoid_pll

        if RubiksCube444.instantiated:
            #raise Exception("Another 4x4x4 instance is being created")
            log.warning("Another 4x4x4 instance is being created")
        else:
            RubiksCube444.instantiated = True

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
        edge_orbit_0 = (2, 3, 8, 12, 15, 14, 9, 5,
                        18, 19, 24, 28, 31, 30, 25, 21,
                        34, 35, 40, 44, 47, 46, 41, 37,
                        50, 51, 56, 60, 62, 63, 57, 53,
                        66, 67, 72, 76, 79, 78, 73, 69,
                        82, 83, 88, 92, 95, 94, 89, 85)

        self._sanity_check('corners', corners_444, 4)
        self._sanity_check('centers', centers_444, 4)
        self._sanity_check('edge-orbit-0', edge_orbit_0, 8)

    def highlow_edges_state(self, edges_to_flip):
        state = self.state

        if edges_to_flip:
            result = []
            for (x, y) in self.reduce333_orient_edges_tuples:
                state_x = state[x]
                state_y = state[y]
                high_low = highlow_edge_values[(x, y, state_x, state_y)]
                wing_str = wing_str_map[state_x + state_y]

                if wing_str in edges_to_flip:
                    if high_low == 'U':
                        high_low = 'D'
                    else:
                        high_low = 'U'

                result.append(high_low)
        else:
            result = [highlow_edge_values[(x, y, state[x], state[y])] for (x, y) in self.reduce333_orient_edges_tuples]

        result = ''.join(result)
        return result

    def highlow_edges_print(self):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()

        orient_edge_state = list(self.highlow_edges_state(self.edge_mapping))
        orient_edge_state_index = 0
        for side in list(self.sides.values()):
            for square_index in side.edge_pos:
                self.state[square_index] = orient_edge_state[orient_edge_state_index]
                orient_edge_state_index += 1
        self.print_cube()

        self.state = original_state[:]
        self.solution = original_solution[:]

    def edges_possibly_oriented_into_high_low_groups(self, debug=False):
        """
        Return True if edges "might" be oriented into high/low groups
        """
        state = self.state
        wing_strs_found = set()

        for (low_edge_index, square_index, partner_index) in low_edges_444:
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in wing_strs_found:
                if debug:
                    log.info("edges_possibly_oriented_into_high_low_groups: wing_str %s already in wing_strs_found %s" % (wing_str, pformat(wing_strs_found)))
                    log.info("low_edges_444: %s" % pformat(low_edges_444))
                return False
            else:
                wing_strs_found.add(wing_str)

        return True

    def edges_oriented_into_high_low_groups(self, debug=False):
        """
        Return True if edges are split into high/low groups
        """
        if not self.edges_possibly_oriented_into_high_low_groups(debug):
            if debug:
                log.info("edges_oriented_into_high_low_groups False: edges_possibly_oriented_into_high_low_groups returned False")
            return False

        DU_wing_strs = self.get_flipped_edges()
        edges_state = self.highlow_edges_state(DU_wing_strs)

        # edge swaps must be even...not technially true but if they are odd it would lead to PLL
        if len(DU_wing_strs) % 2 == 0:

            if edges_state == 'UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU' and self.edge_swaps_even(False, 0, False):
                self.edge_mapping = DU_wing_strs
                return True

            if debug:
                log.info("edges_oriented_into_high_low_groups False: DU_wing_strs %s" % pformat(DU_wing_strs))
                log.info("edges_oriented_into_high_low_groups False: edges_state %s" % edges_state)
                log.info("edges_oriented_into_high_low_groups False: edge_swaps_even %s" % self.edge_swaps_even(False, 0, False))

        else:
            if edges_state == 'UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU' and self.edge_swaps_odd(False, 0, False):
                self.edge_mapping = DU_wing_strs
                return True

            if debug:
                log.info("edges_oriented_into_high_low_groups False: DU_wing_strs %s" % pformat(DU_wing_strs))
                log.info("edges_oriented_into_high_low_groups False: edges_state %s" % edges_state)
                log.info("edges_oriented_into_high_low_groups False: edge_swaps_odd %s" % self.edge_swaps_odd(False, 0, False))

        return False

    def get_flipped_edges(self):
        wing_str_high_low = {
            'UB' : [],
            'UL' : [],
            'UR' : [],
            'UF' : [],
            'LB' : [],
            'LF' : [],
            'RB' : [],
            'RF' : [],
            'DB' : [],
            'DL' : [],
            'DR' : [],
            'DF' : [],
        }
        state = self.state

        for (_, x, y) in high_edges_444:
            state_x = state[x]
            state_y = state[y]
            wing_str = wing_str_map[state_x + state_y]
            high_low = highlow_edge_values[(x, y, state_x, state_y)]
            wing_str_high_low[wing_str].append(high_low)

        for (_, x, y) in low_edges_444:
            state_x = state[x]
            state_y = state[y]
            wing_str = wing_str_map[state_x + state_y]
            high_low = highlow_edge_values[(x, y, state_x, state_y)]
            wing_str_high_low[wing_str].append(high_low)

        DU_wing_strs = set()

        for (wing_str, high_low) in wing_str_high_low.items():
            if high_low == ['U', 'D']:
                pass
            elif high_low == ['D', 'U']:
                DU_wing_strs.add(wing_str)
            else:
                return False

        return DU_wing_strs

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        if self.cpu_mode in ("normal", "slow"):
            self.lt_ULFRBD_centers_stage = LookupTableIDA444ULFRBDCentersStage(self)
            self.lt_ULFRBD_centers_stage.avoid_oll = 0 # avoid OLL on orbit 0

            self.lt_highlow_edges_centers = LookupTable444HighLowEdgesCenters(self)
            self.lt_highlow_edges_edges = LookupTable444HighLowEdgesEdges(self)
            self.lt_highlow_edges = LookupTableIDA444HighLowEdges(self)

            self.lt_reduce333 = LookupTableIDA444Reduce333(self)

        elif self.cpu_mode == "fast":
            self.lt_UD_centers_stage = LookupTable444UDCentersStage(self)
            self.lt_LFRB_centers_stage_even = LookupTable444LRFBCentersStageEven(self)
            self.lt_LFRB_centers_stage_odd = LookupTable444LRFBCentersStageOdd(self)

            self.lt_highlow_edges_centers = LookupTable444HighLowEdgesCenters(self)
            self.lt_highlow_edges_edges = LookupTable444HighLowEdgesEdges(self)
            self.lt_highlow_edges = LookupTableIDA444HighLowEdges(self)

            self.lt_lfrb_centers = LookupTable444LRFBCentersSolve(self)
            self.lt_pair_first_four_edges_non_ida = LookupTable444FirstFourEdges(self)
            #self.lt_pair_first_four_edges_non_ida.preload_cache_string()
            self.lt_pair_last_eight_edges = LookupTable444LastEightEdges(self)
            self.lt_pair_last_eight_edges.preload_cache_string()

        else:
            raise Exception("Invalid cpu_mode %s" % self.cpu_mode)

    def tsai_phase2(self):
        # Pick the best edge_mapping
        # - an edge_mapping that gives us a hit in the phase2 table is ideal
        #     - pick the best among those
        # - if not pick the one that has the lowest edges_cost
        # - build the phase2 table out to 7-deep to help here
        original_state = self.state[:]
        original_solution = self.solution[:]
        phase1_solution_len = len(self.solution)
        log.info("%s: Start of find best edge_mapping" % self)

        for pre_steps in pre_steps_to_try:
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in pre_steps:
                self.rotate(step)

            tmp_state = self.state[:]
            tmp_solution = self.solution[:]

            # Build a list of all 2048 states we need to find in the step20-highlow-edges table.
            # We do this so we can leverage binary_search_multiple() which runs about a million
            # times faster than binary searching for all 2048 states one at a time. This allows
            # us to NOT load this file into memory.
            high_low_states_to_find = []
            edge_mapping_for_phase2_state = {}
            count = 0

            for (edges_to_flip_count, edges_to_flip_sets) in highlow_edge_mapping_combinations.items():
                for edge_mapping in edges_to_flip_sets:
                    self.state[:] = tmp_state[:]
                    self.solution[:] = tmp_solution[:]

                    self.edge_mapping = edge_mapping
                    phase2_state = self.lt_highlow_edges.state()
                    edge_mapping_for_phase2_state[phase2_state] = edge_mapping
                    high_low_states_to_find.append(phase2_state)
                    count += 1

                    # If we evaluate all 2048 of them on a pi3 it takes about 1500ms which ends
                    # up being a huge chunk of the total solve time.  Checking the first 25% will
                    # get us a reasonably short solution.
                    if self.cpu_mode == "fast" and count >= 512:
                        break

            log.info("%s: edge_mapping binary_search_multiple %d high_low_states_to_find begin" % (self, len(high_low_states_to_find)))
            high_low_states = self.lt_highlow_edges.binary_search_multiple(high_low_states_to_find)
            log.info("%s: edge_mapping binary_search_multiple %d high_low_states_to_find end" % (self, len(high_low_states_to_find)))
            min_edge_mapping = None
            min_phase2_cost = None
            min_phase2_steps = None

            for (phase2_state, phase2_steps) in sorted(high_low_states.items()):
                self.state = tmp_state[:]
                self.solution = tmp_solution[:]
                phase2_steps = phase2_steps.split()
                phase2_cost = len(phase2_steps)

                if min_phase2_cost is None or phase2_cost < min_phase2_cost:
                    min_phase2_cost = phase2_cost
                    min_edge_mapping = edge_mapping_for_phase2_state[phase2_state]
                    min_phase2_steps = list(pre_steps) + phase2_steps[:]
                    log.info("%s: using edge_mapping %s, phase2 cost %s" % (self, min_edge_mapping, phase2_cost))

            if min_edge_mapping:
                if pre_steps:
                    log.info("pre-steps %s required to find a hit" % ' '.join(pre_steps))
                break
        else:
            assert False, "write some code to find the best edge_mapping when there is no phase2 hit"

        log.info("%s: End of find best edge_mapping" % self)

        self.state = original_state[:]
        self.solution = original_solution[:]
        self.edge_mapping = min_edge_mapping

        # Test the prune tables
        #self.lt_highlow_edges_centers.solve()
        #self.lt_highlow_edges_edges.solve()
        #self.print_cube()
        #self.highlow_edges_print()
        #sys.exit(0)

        log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #self.lt_highlow_edges.solve()
        for step in min_phase2_steps:
            self.rotate(step)
        self.solution.append("COMMENT_%d_steps_444_phase2" % self.get_solution_len_minus_rotates(self.solution[phase1_solution_len:]))
        self.print_cube()
        self.highlow_edges_print()
        log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def reduce_333_normal(self):

        log.info("%s: Start of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        if not self.centers_staged():
            self.print_cube()
            self.lt_ULFRBD_centers_stage.solve()
            self.rotate_for_best_centers_staging()
            self.print_cube()

        if self.rotate_for_best_centers_staging():
            self.print_cube()

        #orbits_with_oll = self.center_solution_leads_to_oll_parity()
        #log.info("%s: orbits_with_oll %s" % (self, pformat(orbits_with_oll)))
        phase1_solution_len = len(self.solution)
        self.solution.append("COMMENT_%d_steps_444_phase1" % self.get_solution_len_minus_rotates(self.solution))
        log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # This can happen on the large NNN cubes that are using 444 to pair their inside orbit of edges.
        # We need the edge swaps to be even for our edges lookup table to work.
        if self.edge_swaps_odd(False, 0, False):
            log.warning("%s: edge swaps are odd, running prevent_OLL to correct" % self)
            self.prevent_OLL()
            self.print_cube()
            self.solution.append("COMMENT_%d_steps_prevent_OLL" % self.get_solution_len_minus_rotates(self.solution[phase1_solution_len:]))
            log.info("%s: End of prevent_OLL, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.tsai_phase2()
        phase2_solution_len = len(self.solution)

        # Pair all 12 edges and solve the centers in one phase
        # Testing the phase3 prune tables
        #self.lt_reduce333_edges_solve.solve()
        #self.lt_reduce333_centers_solve.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_reduce333.avoid_pll = True
        self.lt_reduce333.solve()

        if self.state[6] != 'U' or self.state[38] != 'F':
            self.rotate_U_to_U()
            self.rotate_F_to_F()

        self.print_cube()
        self.solution.append("COMMENT_%d_steps_444_phase3" % self.get_solution_len_minus_rotates(self.solution[phase2_solution_len:]))
        log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        self.solution.append('CENTERS_SOLVED')
        self.solution.append('EDGES_GROUPED')

    def reduce_333_fast(self):
        self.lt_UD_centers_stage.solve()
        self.rotate_for_best_centers_staging()
        self.print_cube()
        UD_stage_solution_len = len(self.solution)
        self.solution.append("COMMENT_%d_steps_UD_staged" % self.get_solution_len_minus_rotates(self.solution))
        log.info("%s: UD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

        # Avoid OLL, we want an even number of edge swaps after this phase
        if self.edge_swaps_odd(False, 0, False):
            self.lt_LFRB_centers_stage_odd.solve()
        else:
            self.lt_LFRB_centers_stage_even.solve()

        self.rotate_for_best_centers_solving()
        self.print_cube()
        LRFB_stage_solution_len = len(self.solution)
        self.solution.append("COMMENT_%d_steps_LRFB_staged" % self.get_solution_len_minus_rotates(self.solution[UD_stage_solution_len:]))
        log.info("%s: LR FB centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

        # This can happen on the large NNN cubes that are using 444 to pair their inside orbit of edges.
        # We need the edge swaps to be even for our edges lookup table to work.
        if self.edge_swaps_odd(False, 0, False):
            log.warning("%s: edge swaps are odd, running prevent_OLL to correct" % self)
            self.prevent_OLL()
            self.print_cube()
            self.solution.append("COMMENT_%d_steps_prevent_OLL" % self.get_solution_len_minus_rotates(self.solution[LRFB_stage_solution_len:]))
            log.info("%s: End of prevent_OLL, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        self.tsai_phase2()
        phase2_solution_len = len(self.solution)

        self.lt_lfrb_centers.solve()
        self.print_cube()
        LFRB_solve_solution_len = len(self.solution)
        self.solution.append("COMMENT_%d_steps_LFRB_solve" % self.get_solution_len_minus_rotates(self.solution[phase2_solution_len:]))
        log.info("%s: LFRB centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

        # Which 4-edges can we pair in the least number of moves?
        min_cost = None
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(original_solution)

        for four_wing_str_combo in itertools.combinations(wing_strs_all, 4):
            self.state = original_state[:]
            self.solution = original_solution[:]

            self.lt_pair_first_four_edges_non_ida.only_colors = four_wing_str_combo
            self.lt_pair_first_four_edges_non_ida.solve()
            first_four_edges_solution_len = len(self.solution)
            self.solution.append("COMMENT_%d_steps_4_edges_paired" % self.get_solution_len_minus_rotates(self.solution[LFRB_solve_solution_len:]))

            self.lt_pair_last_eight_edges.solve()
            last_eight_edges_solution_len = len(self.solution)
            self.solution.append("COMMENT_%d_steps_8_edges_paired" % self.get_solution_len_minus_rotates(self.solution[first_four_edges_solution_len:]))

            if self.edge_solution_leads_to_pll_parity():
                continue

            tmp_cost = len(self.solution) - original_solution_len

            if min_cost is None or tmp_cost < min_cost:
                log.info("%s: %s cost is %d (NEW MIN)" % (self, pformat(four_wing_str_combo), tmp_cost))
                min_cost = tmp_cost
                min_cost_state = self.state[:]
                min_cost_solution = self.solution[:]

                # It isn't going to get much better than this so go ahead and break out of the loop
                # if min_cost <= 17:
                #    break

                # For --fast the goal is to return "a" solution ASAP so go ahead and break out of the loop
                break
            else:
                log.info("%s: %s cost is %d" % (self, pformat(four_wing_str_combo), tmp_cost))

        self.state = min_cost_state
        self.solution = min_cost_solution

        self.print_cube()
        log.info("%s: reduced to 3x3x3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

        if self.state[6] != 'U' or self.state[38] != 'F':
            self.rotate_U_to_U()
            self.rotate_F_to_F()
            self.print_cube()

        self.solution.append('CENTERS_SOLVED')
        self.solution.append('EDGES_GROUPED')

    def reduce_333(self):

        # save cube state
        self.original_state = self.state[:]
        self.original_solution = self.solution[:]

        #log.info("kociemba: %s" % self.get_kociemba_string(True))

        if self.cpu_mode in ("normal", "slow"):
            self.reduce_333_normal()
        elif self.cpu_mode == "fast":
            self.reduce_333_fast()
        else:
            raise Exception("Unsupported cpu_mode {}".format(self.cpu_mode))


swaps_444 = {'2B': (0, 1, 2, 3, 4, 51, 55, 59, 63, 9, 10, 11, 12, 13, 14, 15, 16, 17, 8, 19, 20, 21, 7, 23, 24, 25, 6, 27, 28, 29, 5, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 92, 52, 53, 54, 91, 56, 57, 58, 90, 60, 61, 62, 89, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 18, 22, 26, 30, 93, 94, 95, 96),
 "2B'": (0, 1, 2, 3, 4, 30, 26, 22, 18, 9, 10, 11, 12, 13, 14, 15, 16, 17, 89, 19, 20, 21, 90, 23, 24, 25, 91, 27, 28, 29, 92, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 5, 52, 53, 54, 6, 56, 57, 58, 7, 60, 61, 62, 8, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 63, 59, 55, 51, 93, 94, 95, 96),
 '2B2': (0, 1, 2, 3, 4, 92, 91, 90, 89, 9, 10, 11, 12, 13, 14, 15, 16, 17, 63, 19, 20, 21, 59, 23, 24, 25, 55, 27, 28, 29, 51, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 30, 52, 53, 54, 26, 56, 57, 58, 22, 60, 61, 62, 18, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 8, 7, 6, 5, 93, 94, 95, 96),
 '2D': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 73, 74, 75, 76, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 25, 26, 27, 28, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 41, 42, 43, 44, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 57, 58, 59, 60, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 "2D'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 41, 42, 43, 44, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 57, 58, 59, 60, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 73, 74, 75, 76, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 25, 26, 27, 28, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 '2D2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 57, 58, 59, 60, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 73, 74, 75, 76, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 25, 26, 27, 28, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 41, 42, 43, 44, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 '2F': (0, 1, 2, 3, 4, 5, 6, 7, 8, 31, 27, 23, 19, 13, 14, 15, 16, 17, 18, 85, 20, 21, 22, 86, 24, 25, 26, 87, 28, 29, 30, 88, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 9, 51, 52, 53, 10, 55, 56, 57, 11, 59, 60, 61, 12, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 62, 58, 54, 50, 89, 90, 91, 92, 93, 94, 95, 96),
 "2F'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 50, 54, 58, 62, 13, 14, 15, 16, 17, 18, 12, 20, 21, 22, 11, 24, 25, 26, 10, 28, 29, 30, 9, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 88, 51, 52, 53, 87, 55, 56, 57, 86, 59, 60, 61, 85, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 19, 23, 27, 31, 89, 90, 91, 92, 93, 94, 95, 96),
 '2F2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 88, 87, 86, 85, 13, 14, 15, 16, 17, 18, 62, 20, 21, 22, 58, 24, 25, 26, 54, 28, 29, 30, 50, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 31, 51, 52, 53, 27, 55, 56, 57, 23, 59, 60, 61, 19, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 12, 11, 10, 9, 89, 90, 91, 92, 93, 94, 95, 96),
 '2L': (0, 1, 79, 3, 4, 5, 75, 7, 8, 9, 71, 11, 12, 13, 67, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 2, 35, 36, 37, 6, 39, 40, 41, 10, 43, 44, 45, 14, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 94, 68, 69, 70, 90, 72, 73, 74, 86, 76, 77, 78, 82, 80, 81, 34, 83, 84, 85, 38, 87, 88, 89, 42, 91, 92, 93, 46, 95, 96),
 "2L'": (0, 1, 34, 3, 4, 5, 38, 7, 8, 9, 42, 11, 12, 13, 46, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 82, 35, 36, 37, 86, 39, 40, 41, 90, 43, 44, 45, 94, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 14, 68, 69, 70, 10, 72, 73, 74, 6, 76, 77, 78, 2, 80, 81, 79, 83, 84, 85, 75, 87, 88, 89, 71, 91, 92, 93, 67, 95, 96),
 '2L2': (0, 1, 82, 3, 4, 5, 86, 7, 8, 9, 90, 11, 12, 13, 94, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 79, 35, 36, 37, 75, 39, 40, 41, 71, 43, 44, 45, 67, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 46, 68, 69, 70, 42, 72, 73, 74, 38, 76, 77, 78, 34, 80, 81, 2, 83, 84, 85, 6, 87, 88, 89, 10, 91, 92, 93, 14, 95, 96),
 '2R': (0, 1, 2, 35, 4, 5, 6, 39, 8, 9, 10, 43, 12, 13, 14, 47, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 83, 36, 37, 38, 87, 40, 41, 42, 91, 44, 45, 46, 95, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 15, 67, 68, 69, 11, 71, 72, 73, 7, 75, 76, 77, 3, 79, 80, 81, 82, 78, 84, 85, 86, 74, 88, 89, 90, 70, 92, 93, 94, 66, 96),
 "2R'": (0, 1, 2, 78, 4, 5, 6, 74, 8, 9, 10, 70, 12, 13, 14, 66, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 3, 36, 37, 38, 7, 40, 41, 42, 11, 44, 45, 46, 15, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 95, 67, 68, 69, 91, 71, 72, 73, 87, 75, 76, 77, 83, 79, 80, 81, 82, 35, 84, 85, 86, 39, 88, 89, 90, 43, 92, 93, 94, 47, 96),
 '2R2': (0, 1, 2, 83, 4, 5, 6, 87, 8, 9, 10, 91, 12, 13, 14, 95, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 78, 36, 37, 38, 74, 40, 41, 42, 70, 44, 45, 46, 66, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 47, 67, 68, 69, 43, 71, 72, 73, 39, 75, 76, 77, 35, 79, 80, 81, 82, 3, 84, 85, 86, 7, 88, 89, 90, 11, 92, 93, 94, 15, 96),
 '2U': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 37, 38, 39, 40, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 53, 54, 55, 56, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 69, 70, 71, 72, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 21, 22, 23, 24, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 "2U'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 69, 70, 71, 72, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 37, 38, 39, 40, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 53, 54, 55, 56, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 '2U2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 53, 54, 55, 56, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 69, 70, 71, 72, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 21, 22, 23, 24, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 37, 38, 39, 40, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 'B': (0, 52, 56, 60, 64, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 4, 18, 19, 20, 3, 22, 23, 24, 2, 26, 27, 28, 1, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 96, 53, 54, 55, 95, 57, 58, 59, 94, 61, 62, 63, 93, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 17, 21, 25, 29),
 "B'": (0, 29, 25, 21, 17, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 93, 18, 19, 20, 94, 22, 23, 24, 95, 26, 27, 28, 96, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 1, 53, 54, 55, 2, 57, 58, 59, 3, 61, 62, 63, 4, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 64, 60, 56, 52),
 'B2': (0, 96, 95, 94, 93, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 64, 18, 19, 20, 60, 22, 23, 24, 56, 26, 27, 28, 52, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 29, 53, 54, 55, 25, 57, 58, 59, 21, 61, 62, 63, 17, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 4, 3, 2, 1),
 'Bw': (0, 52, 56, 60, 64, 51, 55, 59, 63, 9, 10, 11, 12, 13, 14, 15, 16, 4, 8, 19, 20, 3, 7, 23, 24, 2, 6, 27, 28, 1, 5, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 92, 96, 53, 54, 91, 95, 57, 58, 90, 94, 61, 62, 89, 93, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 81, 82, 83, 84, 85, 86, 87, 88, 18, 22, 26, 30, 17, 21, 25, 29),
 "Bw'": (0, 29, 25, 21, 17, 30, 26, 22, 18, 9, 10, 11, 12, 13, 14, 15, 16, 93, 89, 19, 20, 94, 90, 23, 24, 95, 91, 27, 28, 96, 92, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 5, 1, 53, 54, 6, 2, 57, 58, 7, 3, 61, 62, 8, 4, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77, 81, 82, 83, 84, 85, 86, 87, 88, 63, 59, 55, 51, 64, 60, 56, 52),
 'Bw2': (0, 96, 95, 94, 93, 92, 91, 90, 89, 9, 10, 11, 12, 13, 14, 15, 16, 64, 63, 19, 20, 60, 59, 23, 24, 56, 55, 27, 28, 52, 51, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 30, 29, 53, 54, 26, 25, 57, 58, 22, 21, 61, 62, 18, 17, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 81, 82, 83, 84, 85, 86, 87, 88, 8, 7, 6, 5, 4, 3, 2, 1),
 'D': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 77, 78, 79, 80, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 29, 30, 31, 32, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 45, 46, 47, 48, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 61, 62, 63, 64, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84),
 "D'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 45, 46, 47, 48, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 61, 62, 63, 64, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 77, 78, 79, 80, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 29, 30, 31, 32, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93),
 'D2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 61, 62, 63, 64, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 77, 78, 79, 80, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 29, 30, 31, 32, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 45, 46, 47, 48, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81),
 'Dw': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 73, 74, 75, 76, 77, 78, 79, 80, 33, 34, 35, 36, 37, 38, 39, 40, 25, 26, 27, 28, 29, 30, 31, 32, 49, 50, 51, 52, 53, 54, 55, 56, 41, 42, 43, 44, 45, 46, 47, 48, 65, 66, 67, 68, 69, 70, 71, 72, 57, 58, 59, 60, 61, 62, 63, 64, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84),
 "Dw'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 41, 42, 43, 44, 45, 46, 47, 48, 33, 34, 35, 36, 37, 38, 39, 40, 57, 58, 59, 60, 61, 62, 63, 64, 49, 50, 51, 52, 53, 54, 55, 56, 73, 74, 75, 76, 77, 78, 79, 80, 65, 66, 67, 68, 69, 70, 71, 72, 25, 26, 27, 28, 29, 30, 31, 32, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93),
 'Dw2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 57, 58, 59, 60, 61, 62, 63, 64, 33, 34, 35, 36, 37, 38, 39, 40, 73, 74, 75, 76, 77, 78, 79, 80, 49, 50, 51, 52, 53, 54, 55, 56, 25, 26, 27, 28, 29, 30, 31, 32, 65, 66, 67, 68, 69, 70, 71, 72, 41, 42, 43, 44, 45, 46, 47, 48, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81),
 'F': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 32, 28, 24, 20, 17, 18, 19, 81, 21, 22, 23, 82, 25, 26, 27, 83, 29, 30, 31, 84, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36, 13, 50, 51, 52, 14, 54, 55, 56, 15, 58, 59, 60, 16, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 61, 57, 53, 49, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 "F'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 49, 53, 57, 61, 17, 18, 19, 16, 21, 22, 23, 15, 25, 26, 27, 14, 29, 30, 31, 13, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45, 84, 50, 51, 52, 83, 54, 55, 56, 82, 58, 59, 60, 81, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 20, 24, 28, 32, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 'F2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 84, 83, 82, 81, 17, 18, 19, 61, 21, 22, 23, 57, 25, 26, 27, 53, 29, 30, 31, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 50, 51, 52, 28, 54, 55, 56, 24, 58, 59, 60, 20, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 16, 15, 14, 13, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 'Fw': (0, 1, 2, 3, 4, 5, 6, 7, 8, 31, 27, 23, 19, 32, 28, 24, 20, 17, 18, 85, 81, 21, 22, 86, 82, 25, 26, 87, 83, 29, 30, 88, 84, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36, 13, 9, 51, 52, 14, 10, 55, 56, 15, 11, 59, 60, 16, 12, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 61, 57, 53, 49, 62, 58, 54, 50, 89, 90, 91, 92, 93, 94, 95, 96),
 "Fw'": (0, 1, 2, 3, 4, 5, 6, 7, 8, 50, 54, 58, 62, 49, 53, 57, 61, 17, 18, 12, 16, 21, 22, 11, 15, 25, 26, 10, 14, 29, 30, 9, 13, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45, 84, 88, 51, 52, 83, 87, 55, 56, 82, 86, 59, 60, 81, 85, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 20, 24, 28, 32, 19, 23, 27, 31, 89, 90, 91, 92, 93, 94, 95, 96),
 'Fw2': (0, 1, 2, 3, 4, 5, 6, 7, 8, 88, 87, 86, 85, 84, 83, 82, 81, 17, 18, 62, 61, 21, 22, 58, 57, 25, 26, 54, 53, 29, 30, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 51, 52, 28, 27, 55, 56, 24, 23, 59, 60, 20, 19, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 16, 15, 14, 13, 12, 11, 10, 9, 89, 90, 91, 92, 93, 94, 95, 96),
 'L': (0, 80, 2, 3, 4, 76, 6, 7, 8, 72, 10, 11, 12, 68, 14, 15, 16, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20, 1, 34, 35, 36, 5, 38, 39, 40, 9, 42, 43, 44, 13, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 93, 69, 70, 71, 89, 73, 74, 75, 85, 77, 78, 79, 81, 33, 82, 83, 84, 37, 86, 87, 88, 41, 90, 91, 92, 45, 94, 95, 96),
 "L'": (0, 33, 2, 3, 4, 37, 6, 7, 8, 41, 10, 11, 12, 45, 14, 15, 16, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29, 81, 34, 35, 36, 85, 38, 39, 40, 89, 42, 43, 44, 93, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 13, 69, 70, 71, 9, 73, 74, 75, 5, 77, 78, 79, 1, 80, 82, 83, 84, 76, 86, 87, 88, 72, 90, 91, 92, 68, 94, 95, 96),
 'L2': (0, 81, 2, 3, 4, 85, 6, 7, 8, 89, 10, 11, 12, 93, 14, 15, 16, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 80, 34, 35, 36, 76, 38, 39, 40, 72, 42, 43, 44, 68, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 45, 69, 70, 71, 41, 73, 74, 75, 37, 77, 78, 79, 33, 1, 82, 83, 84, 5, 86, 87, 88, 9, 90, 91, 92, 13, 94, 95, 96),
 'Lw': (0, 80, 79, 3, 4, 76, 75, 7, 8, 72, 71, 11, 12, 68, 67, 15, 16, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20, 1, 2, 35, 36, 5, 6, 39, 40, 9, 10, 43, 44, 13, 14, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 94, 93, 69, 70, 90, 89, 73, 74, 86, 85, 77, 78, 82, 81, 33, 34, 83, 84, 37, 38, 87, 88, 41, 42, 91, 92, 45, 46, 95, 96),
 "Lw'": (0, 33, 34, 3, 4, 37, 38, 7, 8, 41, 42, 11, 12, 45, 46, 15, 16, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29, 81, 82, 35, 36, 85, 86, 39, 40, 89, 90, 43, 44, 93, 94, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 14, 13, 69, 70, 10, 9, 73, 74, 6, 5, 77, 78, 2, 1, 80, 79, 83, 84, 76, 75, 87, 88, 72, 71, 91, 92, 68, 67, 95, 96),
 'Lw2': (0, 81, 82, 3, 4, 85, 86, 7, 8, 89, 90, 11, 12, 93, 94, 15, 16, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 80, 79, 35, 36, 76, 75, 39, 40, 72, 71, 43, 44, 68, 67, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 46, 45, 69, 70, 42, 41, 73, 74, 38, 37, 77, 78, 34, 33, 1, 2, 83, 84, 5, 6, 87, 88, 9, 10, 91, 92, 13, 14, 95, 96),
 'R': (0, 1, 2, 3, 36, 5, 6, 7, 40, 9, 10, 11, 44, 13, 14, 15, 48, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 84, 37, 38, 39, 88, 41, 42, 43, 92, 45, 46, 47, 96, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52, 16, 66, 67, 68, 12, 70, 71, 72, 8, 74, 75, 76, 4, 78, 79, 80, 81, 82, 83, 77, 85, 86, 87, 73, 89, 90, 91, 69, 93, 94, 95, 65),
 "R'": (0, 1, 2, 3, 77, 5, 6, 7, 73, 9, 10, 11, 69, 13, 14, 15, 65, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 4, 37, 38, 39, 8, 41, 42, 43, 12, 45, 46, 47, 16, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61, 96, 66, 67, 68, 92, 70, 71, 72, 88, 74, 75, 76, 84, 78, 79, 80, 81, 82, 83, 36, 85, 86, 87, 40, 89, 90, 91, 44, 93, 94, 95, 48),
 'R2': (0, 1, 2, 3, 84, 5, 6, 7, 88, 9, 10, 11, 92, 13, 14, 15, 96, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 77, 37, 38, 39, 73, 41, 42, 43, 69, 45, 46, 47, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 66, 67, 68, 44, 70, 71, 72, 40, 74, 75, 76, 36, 78, 79, 80, 81, 82, 83, 4, 85, 86, 87, 8, 89, 90, 91, 12, 93, 94, 95, 16),
 'Rw': (0, 1, 2, 35, 36, 5, 6, 39, 40, 9, 10, 43, 44, 13, 14, 47, 48, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 83, 84, 37, 38, 87, 88, 41, 42, 91, 92, 45, 46, 95, 96, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52, 16, 15, 67, 68, 12, 11, 71, 72, 8, 7, 75, 76, 4, 3, 79, 80, 81, 82, 78, 77, 85, 86, 74, 73, 89, 90, 70, 69, 93, 94, 66, 65),
 "Rw'": (0, 1, 2, 78, 77, 5, 6, 74, 73, 9, 10, 70, 69, 13, 14, 66, 65, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 3, 4, 37, 38, 7, 8, 41, 42, 11, 12, 45, 46, 15, 16, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61, 96, 95, 67, 68, 92, 91, 71, 72, 88, 87, 75, 76, 84, 83, 79, 80, 81, 82, 35, 36, 85, 86, 39, 40, 89, 90, 43, 44, 93, 94, 47, 48),
 'Rw2': (0, 1, 2, 83, 84, 5, 6, 87, 88, 9, 10, 91, 92, 13, 14, 95, 96, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 78, 77, 37, 38, 74, 73, 41, 42, 70, 69, 45, 46, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 67, 68, 44, 43, 71, 72, 40, 39, 75, 76, 36, 35, 79, 80, 81, 82, 3, 4, 85, 86, 7, 8, 89, 90, 11, 12, 93, 94, 15, 16),
 'U': (0, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 49, 50, 51, 52, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 65, 66, 67, 68, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 17, 18, 19, 20, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 "U'": (0, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 65, 66, 67, 68, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 17, 18, 19, 20, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 33, 34, 35, 36, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 49, 50, 51, 52, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 'U2': (0, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 49, 50, 51, 52, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 65, 66, 67, 68, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 17, 18, 19, 20, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 33, 34, 35, 36, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 'Uw': (0, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 33, 34, 35, 36, 37, 38, 39, 40, 25, 26, 27, 28, 29, 30, 31, 32, 49, 50, 51, 52, 53, 54, 55, 56, 41, 42, 43, 44, 45, 46, 47, 48, 65, 66, 67, 68, 69, 70, 71, 72, 57, 58, 59, 60, 61, 62, 63, 64, 17, 18, 19, 20, 21, 22, 23, 24, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 "Uw'": (0, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 65, 66, 67, 68, 69, 70, 71, 72, 25, 26, 27, 28, 29, 30, 31, 32, 17, 18, 19, 20, 21, 22, 23, 24, 41, 42, 43, 44, 45, 46, 47, 48, 33, 34, 35, 36, 37, 38, 39, 40, 57, 58, 59, 60, 61, 62, 63, 64, 49, 50, 51, 52, 53, 54, 55, 56, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 'Uw2': (0, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 49, 50, 51, 52, 53, 54, 55, 56, 25, 26, 27, 28, 29, 30, 31, 32, 65, 66, 67, 68, 69, 70, 71, 72, 41, 42, 43, 44, 45, 46, 47, 48, 17, 18, 19, 20, 21, 22, 23, 24, 57, 58, 59, 60, 61, 62, 63, 64, 33, 34, 35, 36, 37, 38, 39, 40, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96),
 'x': (0, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65),
 "x'": (0, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48),
 'x2': (0, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16),
 'y': (0, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93),
 "y'": (0, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84),
 'y2': (0, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81),
 'z': (0, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52),
 "z'": (0, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29),
 'z2': (0, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)}

def rotate_444(cube, step):
    return [cube[x] for x in swaps_444[step]]
