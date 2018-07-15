#!/usr/bin/env python3

from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.RubiksCube444 import (
    RubiksCube444,
    LookupTable444Edges,
    moves_444,
    centers_444,
    corners_444,
    edges_444,
    edges_partner_444,
    wings_444,
    UD_centers_444,
    LR_centers_444,
    FB_centers_444,
    UFBD_centers_444,
    rotate_444,
    LookupTable444UDCentersStageCostOnly,
    LookupTable444LRCentersStageCostOnly,
    LookupTable444FBCentersStageCostOnly,
)
from rubikscubennnsolver.RubiksCube444Misc import (
    high_edges_444,
    low_edges_444,
    tsai_phase2_orient_edges_444,
    tsai_edge_mapping_combinations,
)
from rubikscubennnsolver.LookupTable import (
    LookupTable,
    LookupTableHashCostOnly,
    LookupTableIDA,
)
from pyhashxx import hashxx
from pprint import pformat
from random import randint
import logging
import resource
import sys

log = logging.getLogger(__name__)

edges_for_high_low_recolor_444 = (
    2, 9, 8, 15,
    25, 24,
    57, 56,
    82, 89, 88, 95
)

edge_map_to_ULF = {
    # U edges
    'UL' : 'U',
    'LU' : 'U',
    'LD' : 'U',
    'DL' : 'U',
    'RD' : 'U',
    'DR' : 'U',
    'UR' : 'U',
    'RU' : 'U',

    # L edges
    'BL' : 'L',
    'LB' : 'L',
    'FL' : 'L',
    'LF' : 'L',
    'FR' : 'L',
    'RF' : 'L',
    'BR' : 'L',
    'RB' : 'L',

    # F edges
    'UB' : 'F',
    'BU' : 'F',
    'UF' : 'F',
    'FU' : 'F',
    'FD' : 'F',
    'DF' : 'F',
    'DB' : 'F',
    'BD' : 'F',
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


class LookupTableIDA444TsaiPhase0(LookupTableIDA):
    """
    lookup-table-4x4x4-step01-tsai-phase0.txt
    =========================================
    1 steps has 432 entries (0 percent, 0.00x previous step)
    2 steps has 6,696 entries (0 percent, 15.50x previous step)
    3 steps has 119,112 entries (5 percent, 17.79x previous step)
    4 steps has 2,155,128 entries (94 percent, 18.09x previous step)

    Total: 2,281,368 entries
    """

    UD_center_targets = set((
        'UUUUDDDD',
        'DDDDUUUU',
        'UUDDDDUU',
        'UUDDUUDD',
        'DDUUDDUU',
        'DDUUUUDD',
        'DUDUDUDU',
        'DUDUUDUD',
        'UDUDDUDU',
        'UDUDUDUD',
        'DUUDUDDU',
        'UDDUDUUD'
    ))

    LR_center_targets = set((
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
        'LRRLRLLR'
    ))

    FB_center_targets = set((
        'FFFFBBBB',
        'BBBBFFFF',
        'FFBBBBFF',
        'FFBBFFBB',
        'BBFFBBFF',
        'BBFFFFBB',
        'BFBFBFBF',
        'BFBFFBFB',
        'FBFBBFBF',
        'FBFBFBFB',
        'BFFBFBBF',
        'FBBFBFFB'
    ))

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step01-tsai-phase0.txt',
            'TBD',
            moves_444,

            # illegal moves
            ("Lw", "Lw'", "Lw2",
             "Bw", "Bw'", "Bw2",
             "Dw", "Dw'", "Dw2"),
            (parent.lt_UD_centers_stage,
             parent.lt_LR_centers_stage,
             parent.lt_FB_centers_stage),
            linecount=2281368,
            max_depth=4,
            exit_asap=False,
            filesize=203041752)

    def preload_cache_dict(self):
        log.warning("%s: begin preload cache dict" % self)
        memory_pre = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        len_centers_444 = len(centers_444)
        self.cache = {}

        with open(self.filename, 'r') as fh:
            for line in fh:
                (state, steps) = line.rstrip().split(':')
                #centers = bytes(state[0:len_centers_444], 'ascii')
                centers = state[0:len_centers_444]

                if centers not in self.cache:
                    self.cache[centers] = []

                # Store this as a string, not a list.  It takes more than 2x the memory to store steps.split()
                # For solving a 7x7x7 this is the difference in requiring 3G of RAM vs 7G!!.
                self.cache[centers].append(steps)

        self.preloaded_cache_dict = True
        memory_post = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory_post - memory_pre
        log.warning("{}: end preload cache dict ({:,} bytes)".format(self, memory_delta))
        #log.info("cache:\n%s\n" % pformat(self.cache))

    def state(self):
        parent_state = self.parent.state
        centers = ''.join([parent_state[x] for x in centers_444])
        edges = ''.join([parent_state[x] for x in edges_444])
        return centers + edges

    def search_complete(self, state, steps_to_here):
        parent_state = self.parent.state
        tmp_state = self.parent.state[:]

        UD_primary_centers = ''.join([parent_state[x] if parent_state[x] in ('U', 'D') else 'L' if parent_state[x] in ('L', 'R') else 'F' for x in centers_444])
        LR_primary_centers = ''.join([parent_state[x] if parent_state[x] in ('L', 'R') else 'F' if parent_state[x] in ('F', 'B') else 'U' for x in centers_444])
        FB_primary_centers = ''.join([parent_state[x] if parent_state[x] in ('F', 'B') else 'L' if parent_state[x] in ('L', 'R') else 'U' for x in centers_444])
        #log.info("UD_primary_centers: %s" % UD_primary_centers)
        #log.info("LR_primary_centers: %s" % LR_primary_centers)
        #log.info("FB_primary_centers: %s" % FB_primary_centers)

        for centers in (UD_primary_centers, LR_primary_centers, FB_primary_centers):
            centers_solutions = self.cache.get(centers, [])

            for centers_solution in centers_solutions:
                self.parent.state = tmp_state[:]
                centers_solution = centers_solution.split()

                for step in centers_solution:
                    self.parent.state = self.rotate_xxx(self.parent.state[:], step)

                # Are edges split into high/low groups?
                if self.parent.edges_oriented_into_high_low_groups():

                    # rotate_xxx() is very fast but it does not append the
                    # steps to the solution so put the cube back in original state
                    # and execute the steps via a normal rotate() call
                    self.parent.state = self.original_state[:]
                    self.parent.solution = self.original_solution[:]

                    for step in steps_to_here + centers_solution:
                        self.parent.rotate(step)

                    return True

        self.parent.state = tmp_state[:]
        return False


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


class LookupTable444TsaiPhase3EdgesFull(LookupTableHashCostOnly):
    """
    Used once upon a time to troubleshoot edges_oriented_into_high_low_groups()
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step71-tsai-phase3-edges.txt',
            '10425376a8b9ecfdhgkiljnm',
            linecount=239500800,
            max_depth=13)

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        edges_state = ''.join([state[square_index] for square_index in wings_444])
        return edges_state


class LookupTable444TsaiPhase3Edges(LookupTableHashCostOnly):
    """
    lookup-table-4x4x4-step71-tsai-phase3-edges.txt
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
    Average: 10.635709 moves
    """

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step71-tsai-phase3-edges.hash-cost-only.txt',
            '10425376a8b9ecfdhgkiljnm',
            linecount=239500800,
            max_depth=13,
            bucketcount=479001629)
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step71-tsai-phase3-edges.txt',
            '10425376a8b9ecfdhgkiljnm',
            linecount=239500800,
            max_depth=13)
        '''

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        edges_state = ''.join([state[square_index] for square_index in wings_444])
        return edges_state


class LookupTable444TsaiPhase3CentersSolve(LookupTable):
    """
    lookup-table-4x4x4-step72-tsai-phase3-centers.txt
    =================================================
    1 steps has 96 entries (0 percent, 0.00x previous step)
    2 steps has 816 entries (0 percent, 8.50x previous step)
    3 steps has 5,712 entries (1 percent, 7.00x previous step)
    4 steps has 24,288 entries (6 percent, 4.25x previous step)
    5 steps has 63,528 entries (18 percent, 2.62x previous step)
    6 steps has 99,720 entries (28 percent, 1.57x previous step)
    7 steps has 98,352 entries (27 percent, 0.99x previous step)
    8 steps has 52,608 entries (14 percent, 0.53x previous step)
    9 steps has 7,680 entries (2 percent, 0.15x previous step)

    Total: 352,800 entries
    Average: 6.27 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step72-tsai-phase3-centers.txt',
            ('BBBBDDDDLLLLUUUURRRRFFFF',
             'BBBBLLLLUUUURRRRDDDDFFFF',
             'BBBBRRRRDDDDLLLLUUUUFFFF',
             'BBBBUUUURRRRDDDDLLLLFFFF',
             'DDDDBBBBRRRRFFFFLLLLUUUU',
             'DDDDFFFFLLLLBBBBRRRRUUUU',
             'DDDDLLLLBBBBRRRRFFFFUUUU',
             'DDDDRRRRFFFFLLLLBBBBUUUU',
             'FFFFDDDDRRRRUUUULLLLBBBB',
             'FFFFLLLLDDDDRRRRUUUUBBBB',
             'FFFFRRRRUUUULLLLDDDDBBBB',
             'FFFFUUUULLLLDDDDRRRRBBBB',
             'LLLLBBBBDDDDFFFFUUUURRRR',
             'LLLLDDDDFFFFUUUUBBBBRRRR',
             'LLLLFFFFUUUUBBBBDDDDRRRR',
             'LLLLUUUUBBBBDDDDFFFFRRRR',
             'RRRRBBBBUUUUFFFFDDDDLLLL',
             'RRRRDDDDBBBBUUUUFFFFLLLL',
             'RRRRFFFFDDDDBBBBUUUULLLL',
             'RRRRUUUUFFFFDDDDBBBBLLLL',
             'UUUUBBBBLLLLFFFFRRRRDDDD',
             'UUUUFFFFRRRRBBBBLLLLDDDD',
             'UUUULLLLFFFFRRRRBBBBDDDD',
             'UUUURRRRBBBBLLLLFFFFDDDD'),
            linecount=352800,
            max_depth=9,
            filesize=20109600)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[square_index] for square_index in centers_444])
        return result


class LookupTableIDA444TsaiPhase3(LookupTableIDA):
    """
    lookup-table-4x4x4-step70-tsai-phase3.txt
    =========================================
    1 steps has 96 entries (0 percent, 0.00x previous step)
    2 steps has 816 entries (0 percent, 8.50x previous step)
    3 steps has 8,544 entries (0 percent, 10.47x previous step)
    4 steps has 84,192 entries (0 percent, 9.85x previous step)
    5 steps has 804,312 entries (9 percent, 9.55x previous step)
    6 steps has 7,741,752 entries (89 percent, 9.63x previous step)

    Total: 8,639,712 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step70-tsai-phase3.txt',
            ('BBBBDDDDLLLLUUUURRRRFFFF10425376a8b9ecfdhgkiljnm',
             'BBBBLLLLUUUURRRRDDDDFFFF10425376a8b9ecfdhgkiljnm',
             'BBBBRRRRDDDDLLLLUUUUFFFF10425376a8b9ecfdhgkiljnm',
             'BBBBUUUURRRRDDDDLLLLFFFF10425376a8b9ecfdhgkiljnm',
             'DDDDBBBBRRRRFFFFLLLLUUUU10425376a8b9ecfdhgkiljnm',
             'DDDDFFFFLLLLBBBBRRRRUUUU10425376a8b9ecfdhgkiljnm',
             'DDDDLLLLBBBBRRRRFFFFUUUU10425376a8b9ecfdhgkiljnm',
             'DDDDRRRRFFFFLLLLBBBBUUUU10425376a8b9ecfdhgkiljnm',
             'FFFFDDDDRRRRUUUULLLLBBBB10425376a8b9ecfdhgkiljnm',
             'FFFFLLLLDDDDRRRRUUUUBBBB10425376a8b9ecfdhgkiljnm',
             'FFFFRRRRUUUULLLLDDDDBBBB10425376a8b9ecfdhgkiljnm',
             'FFFFUUUULLLLDDDDRRRRBBBB10425376a8b9ecfdhgkiljnm',
             'LLLLBBBBDDDDFFFFUUUURRRR10425376a8b9ecfdhgkiljnm',
             'LLLLDDDDFFFFUUUUBBBBRRRR10425376a8b9ecfdhgkiljnm',
             'LLLLFFFFUUUUBBBBDDDDRRRR10425376a8b9ecfdhgkiljnm',
             'LLLLUUUUBBBBDDDDFFFFRRRR10425376a8b9ecfdhgkiljnm',
             'RRRRBBBBUUUUFFFFDDDDLLLL10425376a8b9ecfdhgkiljnm',
             'RRRRDDDDBBBBUUUUFFFFLLLL10425376a8b9ecfdhgkiljnm',
             'RRRRFFFFDDDDBBBBUUUULLLL10425376a8b9ecfdhgkiljnm',
             'RRRRUUUUFFFFDDDDBBBBLLLL10425376a8b9ecfdhgkiljnm',
             'UUUUBBBBLLLLFFFFRRRRDDDD10425376a8b9ecfdhgkiljnm',
             'UUUUFFFFRRRRBBBBLLLLDDDD10425376a8b9ecfdhgkiljnm',
             'UUUULLLLFFFFRRRRBBBBDDDD10425376a8b9ecfdhgkiljnm',
             'UUUURRRRBBBBLLLLFFFFDDDD10425376a8b9ecfdhgkiljnm'),
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
            (parent.lt_tsai_phase3_edges_solve,
             parent.lt_tsai_phase3_centers_solve),

            linecount=8639712,
            max_depth=6,
            exit_asap=False,
            filesize=622059264)

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        centers_state = ''.join([state[square_index] for square_index in centers_444])
        edges_state = ''.join([state[square_index] for square_index in wings_444])
        return centers_state + edges_state


class LookupTableIDA444TsaiPhase4(LookupTable):

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-tsai-phase4-solve-333-dummy.txt',
            'TBD',
            linecount=0,
            max_depth=99)

    def state(self):
        pass

    def ida_heuristic(self):
        tmp_state = self.parent.state[:]
        tmp_solution = self.parent.solution[:]

        # dwalton
        self.parent.rotate_U_to_U()
        self.parent.rotate_F_to_F()
        self.parent.solve_333()
        result = self.parent.get_solution_len_minus_rotates(self.parent.solution) - self.parent.get_solution_len_minus_rotates(tmp_solution)

        self.parent.state = tmp_state
        self.parent.solution = tmp_solution
        return result

    def ida_heuristic_total(self):
        return self.ida_heuristic()


tsai_phase2_orient_edges_tuples = (
    (2, 67), (3, 66), (5, 18), (8, 51), (9, 19), (12, 50), (14, 34), (15, 35),
    (18, 5), (19, 9), (21, 72), (24, 37), (25, 76), (28, 41), (30, 89), (31, 85),
    (34, 14), (35, 15), (37, 24), (40, 53), (41, 28), (44, 57), (46, 82), (47, 83),
    (50, 12), (51, 8), (53, 40), (56, 69), (57, 44), (60, 73), (62, 88), (63, 92),
    (66, 3), (67, 2), (69, 56), (72, 21), (73, 60), (76, 25), (78, 95), (79, 94),
    (82, 46), (83, 47), (85, 31), (88, 62), (89, 30), (92, 63), (94, 79), (95, 78)
)


class RubiksCubeTsai444(RubiksCube444):

    def __init__(self, state, order, colormap=None, avoid_pll=True, debug=False):
        RubiksCube444.__init__(self, state, order, colormap, debug)
        self.edge_mapping = {}

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_UD_centers_stage = LookupTable444UDCentersStageCostOnly(self)
        self.lt_LR_centers_stage = LookupTable444LRCentersStageCostOnly(self)
        self.lt_FB_centers_stage = LookupTable444FBCentersStageCostOnly(self)
        self.lt_tsai_phase0 = LookupTableIDA444TsaiPhase0(self)
        self.lt_tsai_phase0.preload_cache_dict()

        # =============
        # Phase3 tables
        # =============
        #self.lt_tsai_phase3_edges_solve_full = LookupTable444TsaiPhase3EdgesFull(self)
        self.lt_tsai_phase3_edges_solve = LookupTable444TsaiPhase3Edges(self)
        self.lt_tsai_phase3_centers_solve = LookupTable444TsaiPhase3CentersSolve(self)
        self.lt_tsai_phase3 = LookupTableIDA444TsaiPhase3(self)
        self.lt_tsai_phase3_centers_solve.preload_cache_dict()
        self.lt_tsai_phase3.preload_cache_set()

        self.lt_tsai_phase4 = LookupTableIDA444TsaiPhase4(self)

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

    def build_tsai_phase2_orient_edges_444(self):
        state = self.state
        new_tsai_phase2_orient_edges_444 = {}

        for x in range(1000000):

            # make random moves
            step = moves_444[randint(0, len(moves_444)-1)]
            self.rotate(step)

            for (x, y) in tsai_phase2_orient_edges_tuples:
                state_x = self.state[x]
                state_y = self.state[y]
                wing_str = wing_str_sort_map[''.join((state_x, state_y))]
                wing_tuple = (x, y, state_x, state_y)

                if wing_tuple not in new_tsai_phase2_orient_edges_444:
                    new_tsai_phase2_orient_edges_444[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str)

        print("new tsai_phase2_orient_edges_444\n\n%s\n\n" % pformat(new_tsai_phase2_orient_edges_444))
        log.info("new_tsai_phase2_orient_edges_444 has %d entries" % len(new_tsai_phase2_orient_edges_444))
        sys.exit(0)

    def tsai_phase2_orient_edges_state(self, edges_to_flip):
        state = self.state

        if edges_to_flip:
            result = []
            for (x, y) in tsai_phase2_orient_edges_tuples:
                state_x = state[x]
                state_y = state[y]
                high_low = tsai_phase2_orient_edges_444[(x, y, state_x, state_y)]
                wing_str = wing_str_sort_map[''.join((state_x, state_y))]

                if wing_str in edges_to_flip:
                    if high_low == 'U':
                        high_low = 'D'
                    else:
                        high_low = 'U'

                result.append(high_low)
        else:
            result = [tsai_phase2_orient_edges_444[(x, y, state[x], state[y])] for (x, y) in tsai_phase2_orient_edges_tuples]

        result = ''.join(result)
        return result

    def tsai_phase2_orient_edges_print(self):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()

        orient_edge_state = list(self.tsai_phase2_orient_edges_state(self.edge_mapping))
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
            high_low = tsai_phase2_orient_edges_444[(x, y, state_x, state_y)]
            wing_str_high_low[wing_str].append(high_low)

        for (_, x, y) in low_edges_444:
            state_x = state[x]
            state_y = state[y]
            wing_str = wing_str_sort_map[''.join((state_x, state_y))]
            high_low = tsai_phase2_orient_edges_444[(x, y, state_x, state_y)]
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

    def edges_oriented_into_high_low_groups(self, debug=False):
        """
        Return True if edges are split into high/low groups
        """
        if not self.edges_possibly_oriented_into_high_low_groups(debug):
            if debug:
                log.info("edges_oriented_into_high_low_groups False: edges_possibly_oriented_into_high_low_groups returned False")
            return False

        DU_wing_strs = self.get_flipped_edges()

        # edge swaps must be even...not technially true but if they are odd it would lead to PLL
        if len(DU_wing_strs) % 2 == 0:
            edges_state = self.tsai_phase2_orient_edges_state(DU_wing_strs)

            if edges_state == 'UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU' and self.edge_swaps_even(False, 0, False):
                self.edge_mapping = DU_wing_strs
                return True

            if debug:
                log.info("edges_oriented_into_high_low_groups False: edges_state" % edges_state)
                log.info("edges_oriented_into_high_low_groups False: edge_swaps_even %s" % self.edge_swaps_even(False, 0, False))

        else:
            if debug:
                log.info("edges_oriented_into_high_low_groups False: DU_wing_strs %s is not even" % pformat(DU_wing_strs))

        return False

    def solve(self):

        if self.solved():
            return

        self.lt_init()

        # save cube state
        self.original_state = self.state[:]
        self.original_solution = self.solution[:]

        log.info("%s: Start of Phase0, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        if self.rotate_for_best_centers_staging():
            log.info("rotated cube for easier centers staging")
            self.print_cube()

        self.lt_tsai_phase0.next_phase = self.lt_tsai_phase3
        self.lt_tsai_phase0.solve()
        self.print_cube()
        self.edges_oriented_into_high_low_groups() # redefine edge_mapping
        log.info("%s: edge_mapping %s" % (self, pformat(self.edge_mapping)))
        self.tsai_phase2_orient_edges_print()
        log.info("kociemba: %s" % self.get_kociemba_string(True))
        #log.info("%s: solution %s" % (self, ' '.join(self.solution)))
        log.info("%s: End of Phase0, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Testing the phase3 prune tables
        #self.lt_tsai_phase3_edges_solve.solve()
        #self.lt_tsai_phase3_centers_solve.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        # dwalton
        log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_tsai_phase3.next_phase = self.lt_tsai_phase4
        self.lt_tsai_phase3.avoid_oll = True
        self.lt_tsai_phase3.avoid_pll = True
        self.lt_tsai_phase3.solve()

        if self.state[6] != 'U' or self.state[38] != 'F':
            self.print_cube()
            self.rotate_U_to_U()
            self.rotate_F_to_F()

        self.print_cube()
        log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        self.solution.append('CENTERS_SOLVED')

        self.solve_333()
        self.compress_solution()


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
