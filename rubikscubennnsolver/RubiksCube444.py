#!/usr/bin/env python3

from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.LookupTable import (
    get_characters_common_count,
    steps_on_same_face_and_layer,
    LookupTable,
    LookupTableCostOnly,
    LookupTableIDA,
    LookupTableHashCostOnly,
)
from rubikscubennnsolver.RubiksCube444Misc import (
    high_edges_444,
    low_edges_444,
    highlow_edge_mapping_combinations,
    highlow_edge_values,
)
from rubikscubennnsolver.cLibrary import ida_heuristic_states_step10_444
from pprint import pformat
import logging
import sys

log = logging.getLogger(__name__)

moves_444 = (
    "U", "U'", "U2", "Uw", "Uw'", "Uw2",
    "L", "L'", "L2", "Lw", "Lw'", "Lw2",
    "F" , "F'", "F2", "Fw", "Fw'", "Fw2",
    "R" , "R'", "R2", "Rw", "Rw'", "Rw2",
    "B" , "B'", "B2", "Bw", "Bw'", "Bw2",
    "D" , "D'", "D2", "Dw", "Dw'", "Dw2"
)

solved_444 = 'UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB'

LR_centers_444 = (
    22, 23, 26, 27,
    54, 55, 58, 59
)

centers_444 = (
    6, 7, 10, 11,
    22, 23, 26, 27,
    38, 39, 42, 43,
    54, 55, 58, 59,
    70, 71, 74, 75,
    86, 87, 90, 91
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

wing_str_sort_map = {
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


class LookupTable444UDCentersStageCostOnly(LookupTableCostOnly):
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
    """

    def __init__(self, parent):

        LookupTableCostOnly.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step11-UD-centers-stage.cost-only.txt',
            0xf0000f,
            linecount=735471,
            max_depth=8,
            filesize=16711681)


class LookupTable444LRCentersStageCostOnly(LookupTableCostOnly):

    def __init__(self, parent):
        LookupTableCostOnly.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step12-LR-centers-stage.cost-only.txt',
            0x0f0f00,
            linecount=735471,
            max_depth=8,
            filesize=16711681)


class LookupTable444FBCentersStageCostOnly(LookupTableCostOnly):

    def __init__(self, parent):
        LookupTableCostOnly.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step13-FB-centers-stage.cost-only.txt',
            0x00f0f0,
            linecount=735471,
            max_depth=8,
            filesize=16711681)


class LookupTableIDA444ULFRBDCentersStage(LookupTableIDA):
    """
    lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt
    ==================================================
    1 steps has 24 entries (0 percent, 0.00x previous step)
    2 steps has 324 entries (0 percent, 13.50x previous step)
    3 steps has 4,302 entries (0 percent, 13.28x previous step)
    4 steps has 53,730 entries (7 percent, 12.49x previous step)
    5 steps has 697,806 entries (92 percent, 12.99x previous step)

    Total: 756,186 entries
    Average: 4.92 moves
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt',
            ('FFFFLLLLUUUULLLLUUUUFFFF',
             'FFFFUUUULLLLUUUULLLLFFFF',
             'LLLLFFFFUUUUFFFFUUUULLLL',
             'LLLLUUUUFFFFUUUUFFFFLLLL',
             'UUUUFFFFLLLLFFFFLLLLUUUU',
             'UUUULLLLFFFFLLLLFFFFUUUU'),
            moves_444,

            # illegal_moves...ignoring these increases the average solution
            # by less than 1 move but makes the IDA search about 20x faster
            ("Lw", "Lw'", "Lw2",
             "Bw", "Bw'", "Bw2",
             "Dw", "Dw'", "Dw2"),

            # prune tables
            (parent.lt_UD_centers_stage,
             parent.lt_LR_centers_stage,
             parent.lt_FB_centers_stage),
            linecount=756186,
            max_depth=5,
            filesize=21929394)

        self.recolor_positions = centers_444
        self.recolor_map = {
            'D' : 'U',
            'R' : 'L',
            'B' : 'F',
        }
        self.nuke_corners = True

    def ida_heuristic(self):
        parent = self.parent
        (lt_state, UD_state, LR_state, FB_state) = ida_heuristic_states_step10_444(parent.state, centers_444)

        cost_to_goal = max(
            parent.lt_UD_centers_stage.heuristic(UD_state),
            parent.lt_LR_centers_stage.heuristic(LR_state),
            parent.lt_FB_centers_stage.heuristic(FB_state),
        )

        return (lt_state, cost_to_goal)


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
    4 steps has 26,260 entries (0 percent, 7.69x previous step)
    5 steps has 226,852 entries (1 percent, 8.64x previous step)
    6 steps has 2,048,086 entries (11 percent, 9.03x previous step)

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

            (parent.lt_highlow_edges_edges,
             parent.lt_highlow_edges_centers),
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


def edges_recolor_pattern_444(state):

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
    }

    # Record the two edge_indexes for each of the 12 edges
    for (edge_index, square_index, partner_index) in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = wing_str_sort_map[''.join((square_value, partner_value))]
        edge_map[wing_str].append(edge_index)

    # Where is the other wing_str like us?
    for (edge_index, square_index, partner_index) in wings_for_edges_recolor_pattern_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = wing_str_sort_map[''.join((square_value, partner_value))]

        for tmp_index in edge_map[wing_str]:
            if tmp_index != edge_index:
                state[square_index] = tmp_index
                state[partner_index] = tmp_index
                break
        else:
            raise Exception("could not find tmp_index")

    return ''.join(state)


class LookupTable444Reduce333Edges(LookupTableHashCostOnly):
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
    """

    def __init__(self, parent):

        # Provides an option for running the 444 solver on ~300M
        if parent.min_memory:
            filename = 'lookup-table-4x4x4-step31-reduce333-edges.hash-cost-only.txt.half-buckets'
            bucketcount = 119750417
            filesize = 119750418
        else:
            filename = 'lookup-table-4x4x4-step31-reduce333-edges.hash-cost-only.txt'
            bucketcount = 239500847
            filesize = 239500848

        LookupTableHashCostOnly.__init__(
            self,
            parent,
            filename,
            '10425376a8b9ecfdhgkiljnm',
            linecount=239500800,
            max_depth=13,
            bucketcount=bucketcount,
            filesize=filesize)

        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step31-reduce333-edges.txt',
            '10425376a8b9ecfdhgkiljnm',
            linecount=239500800,
            max_depth=13,
            filesize=479001630)
        '''


class LookupTable444Reduce333CentersSolve(LookupTable):
    """
    lookup-table-4x4x4-step32-reduce333-centers.txt
    ===============================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 83 entries (0 percent, 11.86x previous step)
    3 steps has 724 entries (1 percent, 8.72x previous step)
    4 steps has 3,851 entries (6 percent, 5.32x previous step)
    5 steps has 10,426 entries (17 percent, 2.71x previous step)
    6 steps has 16,693 entries (28 percent, 1.60x previous step)
    7 steps has 16,616 entries (28 percent, 1.00x previous step)
    8 steps has 8,928 entries (15 percent, 0.54x previous step)
    9 steps has 1,472 entries (2 percent, 0.16x previous step)

    Total: 58,800 entries
    Average: 6.31 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step32-reduce333-centers.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD',
            linecount=58800,
            max_depth=9,
            filesize=3351600)


class LookupTableIDA444Reduce333(LookupTableIDA):
    """
    lookup-table-4x4x4-step30-reduce333.txt
    =======================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 83 entries (0 percent, 11.86x previous step)
    3 steps has 960 entries (0 percent, 11.57x previous step)
    4 steps has 10,303 entries (0 percent, 10.73x previous step)
    5 steps has 107,490 entries (8 percent, 10.43x previous step)
    6 steps has 1,124,449 entries (90 percent, 10.46x previous step)

    Total: 1,243,292 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step30-reduce333.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD10425376a8b9ecfdhgkiljnm',
            moves_444,

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
            (parent.lt_reduce333_edges_solve,
             parent.lt_reduce333_centers_solve),

            linecount=1243292,
            max_depth=6,
            filesize=65894476)

    def ida_heuristic(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        centers_state = ''.join([state[square_index] for square_index in centers_444])
        edges_state = ''.join([state[square_index] for square_index in wings_444])
        lt_state = centers_state + edges_state

        cost_to_goal = max(
            self.parent.lt_reduce333_centers_solve.heuristic(centers_state),
            self.parent.lt_reduce333_edges_solve.heuristic(edges_state),
        )

        return (lt_state, cost_to_goal)


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
                low_edge_index = 3

            elif wing_str == 'UL':
                self.move_wing_to_U_west(x)
                high_edge_index = 9
                low_edge_index = 5

            elif wing_str == 'UR':
                self.move_wing_to_U_east(x)
                high_edge_index = 8
                low_edge_index = 12

            elif wing_str == 'UF':
                self.move_wing_to_U_south(x)
                high_edge_index = 15
                low_edge_index = 14

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
                high_edge_index = 25
                low_edge_index = 21

            elif wing_str == 'LF':
                self.move_wing_to_L_east(x)
                high_edge_index = 24
                low_edge_index = 28

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
                high_edge_index = 56
                low_edge_index = 60

            elif wing_str == 'RF':
                self.move_wing_to_R_west(x)
                high_edge_index = 57
                low_edge_index = 53

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
                high_edge_index = 95
                low_edge_index = 94

            elif wing_str == 'DL':
                self.move_wing_to_D_west(x)
                high_edge_index = 89
                low_edge_index = 85

            elif wing_str == 'DR':
                self.move_wing_to_D_east(x)
                high_edge_index = 88
                low_edge_index = 92

            elif wing_str == 'DF':
                self.move_wing_to_D_north(x)
                high_edge_index = 82
                low_edge_index = 83

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

    def build_highlow_edge_values(self):
        state = self.state
        new_highlow_edge_values = {}

        for x in range(1000000):

            # make random moves
            step = moves_444[randint(0, len(moves_444)-1)]
            self.rotate(step)

            for (x, y) in self.reduce333_orient_edges_tuples:
                state_x = self.state[x]
                state_y = self.state[y]
                wing_str = wing_str_sort_map[''.join((state_x, state_y))]
                wing_tuple = (x, y, state_x, state_y)

                if wing_tuple not in new_highlow_edge_values:
                    new_highlow_edge_values[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str)

        print("new highlow_edge_values\n\n%s\n\n" % pformat(new_highlow_edge_values))
        log.info("new_highlow_edge_values has %d entries" % len(new_highlow_edge_values))
        sys.exit(0)

    def highlow_edges_state(self, edges_to_flip):
        state = self.state

        if edges_to_flip:
            result = []
            for (x, y) in self.reduce333_orient_edges_tuples:
                state_x = state[x]
                state_y = state[y]
                high_low = highlow_edge_values[(x, y, state_x, state_y)]
                wing_str = wing_str_sort_map[''.join((state_x, state_y))]

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
            wing_str = wing_str_sort_map[''.join((square_value, partner_value))]

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
            wing_str = wing_str_sort_map[''.join((state_x, state_y))]
            high_low = highlow_edge_values[(x, y, state_x, state_y)]
            wing_str_high_low[wing_str].append(high_low)

        for (_, x, y) in low_edges_444:
            state_x = state[x]
            state_y = state[y]
            wing_str = wing_str_sort_map[''.join((state_x, state_y))]
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

        self.lt_UD_centers_stage = LookupTable444UDCentersStageCostOnly(self)
        self.lt_LR_centers_stage = LookupTable444LRCentersStageCostOnly(self)
        self.lt_FB_centers_stage = LookupTable444FBCentersStageCostOnly(self)
        self.lt_ULFRBD_centers_stage = LookupTableIDA444ULFRBDCentersStage(self)
        self.lt_ULFRBD_centers_stage.avoid_oll = True
        self.lt_ULFRBD_centers_stage.preload_cache_string()

        self.lt_highlow_edges_centers = LookupTable444HighLowEdgesCenters(self)
        self.lt_highlow_edges_edges = LookupTable444HighLowEdgesEdges(self)
        self.lt_highlow_edges = LookupTableIDA444HighLowEdges(self)

        self.lt_reduce333_edges_solve = LookupTable444Reduce333Edges(self)
        self.lt_reduce333_centers_solve = LookupTable444Reduce333CentersSolve(self)
        self.lt_reduce333 = LookupTableIDA444Reduce333(self)
        self.lt_reduce333_centers_solve.preload_cache_dict()
        self.lt_reduce333.preload_cache_string()

    def group_centers_guts(self):
        self.lt_init()

        # save cube state
        self.original_state = self.state[:]
        self.original_solution = self.solution[:]

        # FUULURFFRLRBDDDULUDFLFBBFUURRRUBLBLBDLUBDBULDDRDFLFBBRDBFDBLRBLDULUFFRLRDLDBBRLRUFFRUBFDUDFRLFRU
        # is a good test cube for ida_all_the_way
        #self.lt_ULFRBD_centers_stage.ida_all_the_way = True

        log.info("%s: Start of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_ULFRBD_centers_stage.solve()
        self.print_cube()

        if self.rotate_for_best_centers_staging():
            self.print_cube()
        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # This can happen on the large NNN cubes that are using 444 to pair their inside orbit of edges.
        # We need the edge swaps to be even for our edges lookup table to work.
        if self.edge_swaps_odd(False, 0, False):
            log.warning("%s: edge swaps are odd, running prevent_OLL to correct" % self)
            self.prevent_OLL()
            self.print_cube()
            log.info("%s: End of prevent_OLL, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Pick the best edge_mapping
        # - an edge_mapping that gives us a hit in the phase2 table is ideal
        #     - pick the best among those
        # - if not pick the one that has the lowest edges_cost
        # - build the phase2 table out to 7-deep to help here
        # - this needs to consider the heuristic for phase3
        min_phase23_cost = None
        tmp_state = self.state[:]
        tmp_solution = self.solution[:]
        log.info("%s: Start of find best edge_mapping" % self)

        # Build a list of all 2048 states we need to find in the step20-highlow-edges table.
        # We do this so we can leverage binary_search_multiple() which runs about a million
        # times faster than binary searching for all 2048 states one at a time. This allows
        # us to NOT load this file into memory.
        high_low_states_to_find = []
        edge_mapping_for_phase2_state = {}

        for (edges_to_flip_count, edges_to_flip_sets) in highlow_edge_mapping_combinations.items():
            for edge_mapping in edges_to_flip_sets:
                self.state[:] = tmp_state[:]
                self.solution[:] = tmp_solution[:]

                self.edge_mapping = edge_mapping
                phase2_state = self.lt_highlow_edges.state()
                edge_mapping_for_phase2_state[phase2_state] = edge_mapping
                high_low_states_to_find.append(phase2_state)

        high_low_states = self.lt_highlow_edges.binary_search_multiple(high_low_states_to_find)

        for (phase2_state, phase2_steps) in sorted(high_low_states.items()):
            self.state = tmp_state[:]
            self.solution = tmp_solution[:]
            phase2_steps = phase2_steps.split()
            phase2_cost = len(phase2_steps)

            for step in phase2_steps:
                self.rotate(step)

            (_, phase3_cost) = self.lt_reduce333.ida_heuristic()
            phase23_cost = phase2_cost + phase3_cost

            if min_phase23_cost is None or phase23_cost < min_phase23_cost:
                min_phase23_cost = phase23_cost
                min_edge_mapping = edge_mapping_for_phase2_state[phase2_state]
                log.info("%s: using edge_mapping %s, phase2+3 cost %s" % (self, min_edge_mapping, phase23_cost))

        if min_edge_mapping is None:
            assert False, "write some code to find the best edge_mapping when there is no phase2 hit"
        log.info("%s: End of find best edge_mapping" % self)

        self.state = tmp_state[:]
        self.solution = tmp_solution[:]
        self.edge_mapping = min_edge_mapping

        # Test the prune tables
        #self.lt_highlow_edges_centers.solve()
        #self.lt_highlow_edges_edges.solve()
        #self.print_cube()
        #self.highlow_edges_print()
        #sys.exit(0)

        log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_highlow_edges.next_phase = self.lt_reduce333
        self.lt_highlow_edges.solve()
        self.print_cube()
        self.highlow_edges_print()
        log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Testing the phase3 prune tables
        #self.lt_reduce333_edges_solve.solve()
        #self.lt_reduce333_centers_solve.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_reduce333.avoid_oll = True
        self.lt_reduce333.avoid_pll = True
        self.lt_reduce333.solve()

        if self.state[6] != 'U' or self.state[38] != 'F':
            self.print_cube()
            self.rotate_U_to_U()
            self.rotate_F_to_F()

        self.print_cube()
        log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

    def group_edges(self):
        self.group_centers_guts()
        log.info("%s: edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))


swaps_444 = {'B': (0, 52, 56, 60, 64, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 4, 18, 19, 20, 3, 22, 23, 24, 2, 26, 27, 28, 1, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 96, 53, 54, 55, 95, 57, 58, 59, 94, 61, 62, 63, 93, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 17, 21, 25, 29),
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
 'y': (0, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93),
 "y'": (0, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84),
 'z': (0, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52),
 "z'": (0, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29),
    "x x" : (0, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16),
    "y y" : (0, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81),
    "z z" : (0, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1),
    "x y" : (0, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68),
    "x y'" : (0, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77),
    "x z" : (0, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49),
    "x z'" : (0, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17),
    "x y y" : (0, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80),
    "x z z" : (0, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33),
    "x' y" : (0, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45),
    "x' y'" : (0, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36),
    "x' z" : (0, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64),
    "x' z'" : (0, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32),
    "y x x" : (0, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4),
    "y z z" : (0, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13),
    "z x x" : (0, 61, 57, 53, 49, 62, 58, 54, 50, 63, 59, 55, 51, 64, 60, 56, 52, 84, 88, 92, 96, 83, 87, 91, 95, 82, 86, 90, 94, 81, 85, 89, 93, 77, 73, 69, 65, 78, 74, 70, 66, 79, 75, 71, 67, 80, 76, 72, 68, 4, 8, 12, 16, 3, 7, 11, 15, 2, 6, 10, 14, 1, 5, 9, 13, 36, 40, 44, 48, 35, 39, 43, 47, 34, 38, 42, 46, 33, 37, 41, 45, 29, 25, 21, 17, 30, 26, 22, 18, 31, 27, 23, 19, 32, 28, 24, 20),
    "z y y" : (0, 20, 24, 28, 32, 19, 23, 27, 31, 18, 22, 26, 30, 17, 21, 25, 29, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3, 16, 12, 8, 4, 68, 72, 76, 80, 67, 71, 75, 79, 66, 70, 74, 78, 65, 69, 73, 77, 93, 89, 85, 81, 94, 90, 86, 82, 95, 91, 87, 83, 96, 92, 88, 84, 45, 41, 37, 33, 46, 42, 38, 34, 47, 43, 39, 35, 48, 44, 40, 36, 52, 56, 60, 64, 51, 55, 59, 63, 50, 54, 58, 62, 49, 53, 57, 61),
    "reflect-x" : (0, 93, 94, 95, 96, 89, 90, 91, 92, 85, 86, 87, 88, 81, 82, 83, 84, 29, 30, 31, 32, 25, 26, 27, 28, 21, 22, 23, 24, 17, 18, 19, 20, 45, 46, 47, 48, 41, 42, 43, 44, 37, 38, 39, 40, 33, 34, 35, 36, 61, 62, 63, 64, 57, 58, 59, 60, 53, 54, 55, 56, 49, 50, 51, 52, 77, 78, 79, 80, 73, 74, 75, 76, 69, 70, 71, 72, 65, 66, 67, 68, 13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4),
    "reflect-x x" : (0, 45, 46, 47, 48, 41, 42, 43, 44, 37, 38, 39, 40, 33, 34, 35, 36, 32, 28, 24, 20, 31, 27, 23, 19, 30, 26, 22, 18, 29, 25, 21, 17, 13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4, 49, 53, 57, 61, 50, 54, 58, 62, 51, 55, 59, 63, 52, 56, 60, 64, 84, 83, 82, 81, 88, 87, 86, 85, 92, 91, 90, 89, 96, 95, 94, 93, 68, 67, 66, 65, 72, 71, 70, 69, 76, 75, 74, 73, 80, 79, 78, 77),
    "reflect-x x'" : (0, 68, 67, 66, 65, 72, 71, 70, 69, 76, 75, 74, 73, 80, 79, 78, 77, 17, 21, 25, 29, 18, 22, 26, 30, 19, 23, 27, 31, 20, 24, 28, 32, 93, 94, 95, 96, 89, 90, 91, 92, 85, 86, 87, 88, 81, 82, 83, 84, 64, 60, 56, 52, 63, 59, 55, 51, 62, 58, 54, 50, 61, 57, 53, 49, 4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13, 45, 46, 47, 48, 41, 42, 43, 44, 37, 38, 39, 40, 33, 34, 35, 36),
    "reflect-x y" : (0, 81, 85, 89, 93, 82, 86, 90, 94, 83, 87, 91, 95, 84, 88, 92, 96, 45, 46, 47, 48, 41, 42, 43, 44, 37, 38, 39, 40, 33, 34, 35, 36, 61, 62, 63, 64, 57, 58, 59, 60, 53, 54, 55, 56, 49, 50, 51, 52, 77, 78, 79, 80, 73, 74, 75, 76, 69, 70, 71, 72, 65, 66, 67, 68, 29, 30, 31, 32, 25, 26, 27, 28, 21, 22, 23, 24, 17, 18, 19, 20, 16, 12, 8, 4, 15, 11, 7, 3, 14, 10, 6, 2, 13, 9, 5, 1),
    "reflect-x y'" : (0, 96, 92, 88, 84, 95, 91, 87, 83, 94, 90, 86, 82, 93, 89, 85, 81, 77, 78, 79, 80, 73, 74, 75, 76, 69, 70, 71, 72, 65, 66, 67, 68, 29, 30, 31, 32, 25, 26, 27, 28, 21, 22, 23, 24, 17, 18, 19, 20, 45, 46, 47, 48, 41, 42, 43, 44, 37, 38, 39, 40, 33, 34, 35, 36, 61, 62, 63, 64, 57, 58, 59, 60, 53, 54, 55, 56, 49, 50, 51, 52, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16),
    "reflect-x z" : (0, 17, 21, 25, 29, 18, 22, 26, 30, 19, 23, 27, 31, 20, 24, 28, 32, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16, 33, 37, 41, 45, 34, 38, 42, 46, 35, 39, 43, 47, 36, 40, 44, 48, 81, 85, 89, 93, 82, 86, 90, 94, 83, 87, 91, 95, 84, 88, 92, 96, 80, 76, 72, 68, 79, 75, 71, 67, 78, 74, 70, 66, 77, 73, 69, 65, 49, 53, 57, 61, 50, 54, 58, 62, 51, 55, 59, 63, 52, 56, 60, 64),
    "reflect-x z'" : (0, 64, 60, 56, 52, 63, 59, 55, 51, 62, 58, 54, 50, 61, 57, 53, 49, 96, 92, 88, 84, 95, 91, 87, 83, 94, 90, 86, 82, 93, 89, 85, 81, 48, 44, 40, 36, 47, 43, 39, 35, 46, 42, 38, 34, 45, 41, 37, 33, 16, 12, 8, 4, 15, 11, 7, 3, 14, 10, 6, 2, 13, 9, 5, 1, 65, 69, 73, 77, 66, 70, 74, 78, 67, 71, 75, 79, 68, 72, 76, 80, 32, 28, 24, 20, 31, 27, 23, 19, 30, 26, 22, 18, 29, 25, 21, 17),
    "reflect-x x x" : (0, 13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4, 20, 19, 18, 17, 24, 23, 22, 21, 28, 27, 26, 25, 32, 31, 30, 29, 68, 67, 66, 65, 72, 71, 70, 69, 76, 75, 74, 73, 80, 79, 78, 77, 52, 51, 50, 49, 56, 55, 54, 53, 60, 59, 58, 57, 64, 63, 62, 61, 36, 35, 34, 33, 40, 39, 38, 37, 44, 43, 42, 41, 48, 47, 46, 45, 93, 94, 95, 96, 89, 90, 91, 92, 85, 86, 87, 88, 81, 82, 83, 84),
    "reflect-x y y" : (0, 84, 83, 82, 81, 88, 87, 86, 85, 92, 91, 90, 89, 96, 95, 94, 93, 61, 62, 63, 64, 57, 58, 59, 60, 53, 54, 55, 56, 49, 50, 51, 52, 77, 78, 79, 80, 73, 74, 75, 76, 69, 70, 71, 72, 65, 66, 67, 68, 29, 30, 31, 32, 25, 26, 27, 28, 21, 22, 23, 24, 17, 18, 19, 20, 45, 46, 47, 48, 41, 42, 43, 44, 37, 38, 39, 40, 33, 34, 35, 36, 4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13),
    "reflect-x z z" : (0, 4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13, 52, 51, 50, 49, 56, 55, 54, 53, 60, 59, 58, 57, 64, 63, 62, 61, 36, 35, 34, 33, 40, 39, 38, 37, 44, 43, 42, 41, 48, 47, 46, 45, 20, 19, 18, 17, 24, 23, 22, 21, 28, 27, 26, 25, 32, 31, 30, 29, 68, 67, 66, 65, 72, 71, 70, 69, 76, 75, 74, 73, 80, 79, 78, 77, 84, 83, 82, 81, 88, 87, 86, 85, 92, 91, 90, 89, 96, 95, 94, 93),
    "reflect-x x y" : (0, 33, 37, 41, 45, 34, 38, 42, 46, 35, 39, 43, 47, 36, 40, 44, 48, 13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4, 49, 53, 57, 61, 50, 54, 58, 62, 51, 55, 59, 63, 52, 56, 60, 64, 84, 83, 82, 81, 88, 87, 86, 85, 92, 91, 90, 89, 96, 95, 94, 93, 32, 28, 24, 20, 31, 27, 23, 19, 30, 26, 22, 18, 29, 25, 21, 17, 65, 69, 73, 77, 66, 70, 74, 78, 67, 71, 75, 79, 68, 72, 76, 80),
    "reflect-x x y'" : (0, 48, 44, 40, 36, 47, 43, 39, 35, 46, 42, 38, 34, 45, 41, 37, 33, 84, 83, 82, 81, 88, 87, 86, 85, 92, 91, 90, 89, 96, 95, 94, 93, 32, 28, 24, 20, 31, 27, 23, 19, 30, 26, 22, 18, 29, 25, 21, 17, 13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4, 49, 53, 57, 61, 50, 54, 58, 62, 51, 55, 59, 63, 52, 56, 60, 64, 80, 76, 72, 68, 79, 75, 71, 67, 78, 74, 70, 66, 77, 73, 69, 65),
    "reflect-x x z" : (0, 29, 30, 31, 32, 25, 26, 27, 28, 21, 22, 23, 24, 17, 18, 19, 20, 80, 76, 72, 68, 79, 75, 71, 67, 78, 74, 70, 66, 77, 73, 69, 65, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16, 33, 37, 41, 45, 34, 38, 42, 46, 35, 39, 43, 47, 36, 40, 44, 48, 81, 85, 89, 93, 82, 86, 90, 94, 83, 87, 91, 95, 84, 88, 92, 96, 52, 51, 50, 49, 56, 55, 54, 53, 60, 59, 58, 57, 64, 63, 62, 61),
    "reflect-x x z'" : (0, 61, 62, 63, 64, 57, 58, 59, 60, 53, 54, 55, 56, 49, 50, 51, 52, 48, 44, 40, 36, 47, 43, 39, 35, 46, 42, 38, 34, 45, 41, 37, 33, 16, 12, 8, 4, 15, 11, 7, 3, 14, 10, 6, 2, 13, 9, 5, 1, 65, 69, 73, 77, 66, 70, 74, 78, 67, 71, 75, 79, 68, 72, 76, 80, 96, 92, 88, 84, 95, 91, 87, 83, 94, 90, 86, 82, 93, 89, 85, 81, 20, 19, 18, 17, 24, 23, 22, 21, 28, 27, 26, 25, 32, 31, 30, 29),
    "reflect-x x y y" : (0, 36, 35, 34, 33, 40, 39, 38, 37, 44, 43, 42, 41, 48, 47, 46, 45, 49, 53, 57, 61, 50, 54, 58, 62, 51, 55, 59, 63, 52, 56, 60, 64, 84, 83, 82, 81, 88, 87, 86, 85, 92, 91, 90, 89, 96, 95, 94, 93, 32, 28, 24, 20, 31, 27, 23, 19, 30, 26, 22, 18, 29, 25, 21, 17, 13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4, 77, 78, 79, 80, 73, 74, 75, 76, 69, 70, 71, 72, 65, 66, 67, 68),
    "reflect-x x z z" : (0, 77, 78, 79, 80, 73, 74, 75, 76, 69, 70, 71, 72, 65, 66, 67, 68, 64, 60, 56, 52, 63, 59, 55, 51, 62, 58, 54, 50, 61, 57, 53, 49, 4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13, 17, 21, 25, 29, 18, 22, 26, 30, 19, 23, 27, 31, 20, 24, 28, 32, 93, 94, 95, 96, 89, 90, 91, 92, 85, 86, 87, 88, 81, 82, 83, 84, 36, 35, 34, 33, 40, 39, 38, 37, 44, 43, 42, 41, 48, 47, 46, 45),
    "reflect-x x' y" : (0, 80, 76, 72, 68, 79, 75, 71, 67, 78, 74, 70, 66, 77, 73, 69, 65, 93, 94, 95, 96, 89, 90, 91, 92, 85, 86, 87, 88, 81, 82, 83, 84, 64, 60, 56, 52, 63, 59, 55, 51, 62, 58, 54, 50, 61, 57, 53, 49, 4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13, 17, 21, 25, 29, 18, 22, 26, 30, 19, 23, 27, 31, 20, 24, 28, 32, 48, 44, 40, 36, 47, 43, 39, 35, 46, 42, 38, 34, 45, 41, 37, 33),
    "reflect-x x' y'" : (0, 65, 69, 73, 77, 66, 70, 74, 78, 67, 71, 75, 79, 68, 72, 76, 80, 4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13, 17, 21, 25, 29, 18, 22, 26, 30, 19, 23, 27, 31, 20, 24, 28, 32, 93, 94, 95, 96, 89, 90, 91, 92, 85, 86, 87, 88, 81, 82, 83, 84, 64, 60, 56, 52, 63, 59, 55, 51, 62, 58, 54, 50, 61, 57, 53, 49, 33, 37, 41, 45, 34, 38, 42, 46, 35, 39, 43, 47, 36, 40, 44, 48),
    "reflect-x x' z" : (0, 20, 19, 18, 17, 24, 23, 22, 21, 28, 27, 26, 25, 32, 31, 30, 29, 33, 37, 41, 45, 34, 38, 42, 46, 35, 39, 43, 47, 36, 40, 44, 48, 81, 85, 89, 93, 82, 86, 90, 94, 83, 87, 91, 95, 84, 88, 92, 96, 80, 76, 72, 68, 79, 75, 71, 67, 78, 74, 70, 66, 77, 73, 69, 65, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16, 61, 62, 63, 64, 57, 58, 59, 60, 53, 54, 55, 56, 49, 50, 51, 52),
    "reflect-x x' z'" : (0, 52, 51, 50, 49, 56, 55, 54, 53, 60, 59, 58, 57, 64, 63, 62, 61, 65, 69, 73, 77, 66, 70, 74, 78, 67, 71, 75, 79, 68, 72, 76, 80, 96, 92, 88, 84, 95, 91, 87, 83, 94, 90, 86, 82, 93, 89, 85, 81, 48, 44, 40, 36, 47, 43, 39, 35, 46, 42, 38, 34, 45, 41, 37, 33, 16, 12, 8, 4, 15, 11, 7, 3, 14, 10, 6, 2, 13, 9, 5, 1, 29, 30, 31, 32, 25, 26, 27, 28, 21, 22, 23, 24, 17, 18, 19, 20),
    "reflect-x y x x" : (0, 16, 12, 8, 4, 15, 11, 7, 3, 14, 10, 6, 2, 13, 9, 5, 1, 36, 35, 34, 33, 40, 39, 38, 37, 44, 43, 42, 41, 48, 47, 46, 45, 20, 19, 18, 17, 24, 23, 22, 21, 28, 27, 26, 25, 32, 31, 30, 29, 68, 67, 66, 65, 72, 71, 70, 69, 76, 75, 74, 73, 80, 79, 78, 77, 52, 51, 50, 49, 56, 55, 54, 53, 60, 59, 58, 57, 64, 63, 62, 61, 81, 85, 89, 93, 82, 86, 90, 94, 83, 87, 91, 95, 84, 88, 92, 96),
    "reflect-x y z z" : (0, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16, 68, 67, 66, 65, 72, 71, 70, 69, 76, 75, 74, 73, 80, 79, 78, 77, 52, 51, 50, 49, 56, 55, 54, 53, 60, 59, 58, 57, 64, 63, 62, 61, 36, 35, 34, 33, 40, 39, 38, 37, 44, 43, 42, 41, 48, 47, 46, 45, 20, 19, 18, 17, 24, 23, 22, 21, 28, 27, 26, 25, 32, 31, 30, 29, 96, 92, 88, 84, 95, 91, 87, 83, 94, 90, 86, 82, 93, 89, 85, 81),
    "reflect-x z x x" : (0, 49, 53, 57, 61, 50, 54, 58, 62, 51, 55, 59, 63, 52, 56, 60, 64, 16, 12, 8, 4, 15, 11, 7, 3, 14, 10, 6, 2, 13, 9, 5, 1, 65, 69, 73, 77, 66, 70, 74, 78, 67, 71, 75, 79, 68, 72, 76, 80, 96, 92, 88, 84, 95, 91, 87, 83, 94, 90, 86, 82, 93, 89, 85, 81, 48, 44, 40, 36, 47, 43, 39, 35, 46, 42, 38, 34, 45, 41, 37, 33, 17, 21, 25, 29, 18, 22, 26, 30, 19, 23, 27, 31, 20, 24, 28, 32),
    "reflect-x z y y" : (0, 32, 28, 24, 20, 31, 27, 23, 19, 30, 26, 22, 18, 29, 25, 21, 17, 81, 85, 89, 93, 82, 86, 90, 94, 83, 87, 91, 95, 84, 88, 92, 96, 80, 76, 72, 68, 79, 75, 71, 67, 78, 74, 70, 66, 77, 73, 69, 65, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16, 33, 37, 41, 45, 34, 38, 42, 46, 35, 39, 43, 47, 36, 40, 44, 48, 64, 60, 56, 52, 63, 59, 55, 51, 62, 58, 54, 50, 61, 57, 53, 49),
    "reflect-y" : (0, 13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4, 20, 19, 18, 17, 24, 23, 22, 21, 28, 27, 26, 25, 32, 31, 30, 29, 68, 67, 66, 65, 72, 71, 70, 69, 76, 75, 74, 73, 80, 79, 78, 77, 52, 51, 50, 49, 56, 55, 54, 53, 60, 59, 58, 57, 64, 63, 62, 61, 36, 35, 34, 33, 40, 39, 38, 37, 44, 43, 42, 41, 48, 47, 46, 45, 93, 94, 95, 96, 89, 90, 91, 92, 85, 86, 87, 88, 81, 82, 83, 84),
    "reflect-z" : (0, 4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13, 52, 51, 50, 49, 56, 55, 54, 53, 60, 59, 58, 57, 64, 63, 62, 61, 36, 35, 34, 33, 40, 39, 38, 37, 44, 43, 42, 41, 48, 47, 46, 45, 20, 19, 18, 17, 24, 23, 22, 21, 28, 27, 26, 25, 32, 31, 30, 29, 68, 67, 66, 65, 72, 71, 70, 69, 76, 75, 74, 73, 80, 79, 78, 77, 84, 83, 82, 81, 88, 87, 86, 85, 92, 91, 90, 89, 96, 95, 94, 93),
}

def rotate_444(cube, step):
    return [cube[x] for x in swaps_444[step]]
