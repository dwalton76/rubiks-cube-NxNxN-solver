#!/usr/bin/env python3

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
    reflect_x_444
)
from rubikscubennnsolver.RubiksCube444Misc import (
    high_edges_444,
    low_edges_444,
    tsai_phase2_orient_edges_444
)
from rubikscubennnsolver.LookupTable import (
    LookupTable,
    LookupTableHashCostOnly,
    LookupTableIDA
)
from pyhashxx import hashxx
from pprint import pformat
from random import randint
import logging
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

class LookupTable444TsaiPhase1Centers(LookupTable):
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
    Average: 6.026431 moves
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step50-tsai-phase1.txt',
            '0f0f00',
            linecount=735471,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state
        LR = ('L', 'R')
        result = ''.join(['1' if parent_state[x] in LR else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA444TsaiPhase1(LookupTableIDA):

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step60-tsai-phase2-dummy.txt',
            '0f0f00',
            moves_444,
            # illegal moves
            (),
            # prune tables
            (parent.lt_tsai_phase1_centers,),
            linecount=0,
            max_depth=99)

    def state(self):
        return self.parent.lt_tsai_phase1_centers.state()

    def search_complete(self, state, steps_to_here):
        parent_state = self.parent.state
        LR = ('L', 'R')

        # Are LR centers staged?
        for x in LR_centers_444:
            if parent_state[x] not in LR:
                return False

        # About 30% of phase2 edge states and 30% of phase2 center states are
        # 6 moves or less so IDA until we find a phase1 solution that puts both
        # of those at <= 6 moves. We do this to speed up the phase2 search.
        if self.parent.lt_tsai_phase2_edges_lr_centers.steps_cost() > 7:
            #log.info("%s: phase2 edges cost %s" % (self, self.parent.lt_tsai_phase2_edges.steps_cost()))
            return False

        if self.parent.lt_tsai_phase2_centers.steps_cost() > 6:
            #log.info("%s: phase2 centers cost %s" % (self, self.parent.lt_tsai_phase2_centers.steps_cost()))
            return False

        # rotate_xxx() is very fast but it does not append the
        # steps to the solution so put the cube back in original state
        # and execute the steps via a normal rotate() call
        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]

        for step in steps_to_here:
            self.parent.rotate(step)

        return True


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
    'LRRLRLLR'
))


class LookupTable444TsaiPhase2Centers(LookupTable):
    """
    lookup-table-4x4x4-step61-tsai-phase2-centers.txt
    =================================================
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
    Average: 6.677349 moves
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
            linecount=900900,
            max_depth=9)

    def state(self):
        parent_state = self.parent.state
        ULFR = ('U', 'L', 'F', 'R')
        result = ''.join([parent_state[x] if parent_state[x] in ULFR else 'F' if parent_state[x] == 'B' else 'U' for x in centers_444])
        return result


#class LookupTable444TsaiPhase2EdgesLRCenters(LookupTable):
class LookupTable444TsaiPhase2EdgesLRCenters(LookupTableHashCostOnly):
    """
    lookup-table-4x4x4-step62-tsai-phase2-edges-and-LR-centers.txt
    ==============================================================
    1 steps has 48 entries (0 percent, 0.00x previous step)
    2 steps has 540 entries (0 percent, 11.25x previous step)
    3 steps has 7,308 entries (0 percent, 13.53x previous step)
    4 steps has 88,284 entries (0 percent, 12.08x previous step)
    5 steps has 1,085,824 entries (0 percent, 12.30x previous step)
    6 steps has 11,021,634 entries (5 percent, 10.15x previous step)
    7 steps has 63,017,888 entries (33 percent, 5.72x previous step)
    8 steps has 101,139,062 entries (53 percent, 1.60x previous step)
    9 steps has 12,929,280 entries (6 percent, 0.13x previous step)
    10 steps has 1,052 entries (0 percent, 0.00x previous step)

    Total: 189,290,920 entries
    Average: 7.60 moves
    """

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step62-tsai-phase2-edges-and-LR-centers.hash-cost-only.txt',
            ('UDDUUDDUDUDLLUULLDUDDUUDDUUDDUDRRUURRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLLUURRDUDDUUDDUUDDUDLLUURRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLLUURRDUDDUUDDUUDDUDRRUULLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLRUULRDUDDUUDDUUDDUDLRUULRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLRUULRDUDDUUDDUUDDUDRLUURLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLRUURLDUDDUUDDUUDDUDRLUULRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRLUULRDUDDUUDDUUDDUDLRUURLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRLUURLDUDDUUDDUUDDUDLRUULRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRLUURLDUDDUUDDUUDDUDRLUURLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRRUULLDUDDUUDDUUDDUDLLUURRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRRUULLDUDDUUDDUUDDUDRRUULLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRRUURRDUDDUUDDUUDDUDLLUULLDUDDUUDDUUDUDDUUDDU'),
            linecount=189290920,
            max_depth=10,
            bucketcount=378581849)
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step62-tsai-phase2-edges-and-LR-centers.txt',
            ('UDDUUDDUDUDLLUULLDUDDUUDDUUDDUDRRUURRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLLUURRDUDDUUDDUUDDUDLLUURRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLLUURRDUDDUUDDUUDDUDRRUULLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLRUULRDUDDUUDDUUDDUDLRUULRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLRUULRDUDDUUDDUUDDUDRLUURLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDLRUURLDUDDUUDDUUDDUDRLUULRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRLUULRDUDDUUDDUUDDUDLRUURLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRLUURLDUDDUUDDUUDDUDLRUULRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRLUURLDUDDUUDDUUDDUDRLUURLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRRUULLDUDDUUDDUUDDUDLLUURRDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRRUULLDUDDUUDDUUDDUDRRUULLDUDDUUDDUUDUDDUUDDU',
             'UDDUUDDUDUDRRUURRDUDDUUDDUUDDUDLLUULLDUDDUUDDUUDUDDUUDDU'),
            linecount=189290920,
            max_depth=10)
        '''

    def state(self):
        parent_state = self.parent.state

        edges = self.parent.tsai_phase2_orient_edges_state()
        U_edges = edges[0:8]
        L_edges = edges[8:16]
        F_edges = edges[16:24]
        R_edges = edges[24:32]
        B_edges = edges[32:40]
        D_edges = edges[40:48]

        centers = ''.join([parent_state[x] for x in LR_centers_444])

        result = ''.join([
                    U_edges,
                    ''.join([L_edges[0], L_edges[1],
                             L_edges[2], centers[0], centers[1], L_edges[3],
                             L_edges[4], centers[2], centers[3], L_edges[5],
                             L_edges[6], L_edges[7]]),
                    F_edges,
                    ''.join([R_edges[0], R_edges[1],
                             R_edges[2], centers[4], centers[5], R_edges[3],
                             R_edges[4], centers[6], centers[7], R_edges[5],
                             R_edges[6], R_edges[7]]),
                    B_edges,
                    D_edges])

        return result


class LookupTableIDA444TsaiPhase2(LookupTableIDA):
    """
    lookup-table-4x4x4-step60-tsai-phase2.txt
    =========================================
    1 steps has 48 entries (0 percent, 0.00x previous step)
    2 steps has 540 entries (0 percent, 11.25x previous step)
    3 steps has 7,356 entries (0 percent, 13.62x previous step)
    4 steps has 93,644 entries (6 percent, 12.73x previous step)
    5 steps has 1,317,948 entries (92 percent, 14.07x previous step)

    Total: 1,419,536 entries
    Average: 4.92 moves
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step60-tsai-phase2.txt',
            ('UDDUUUUUUDDUDUDLLUULLDUDDUUFFDDFFUUDDUDRRUURRDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDLLUURRDUDDUUFFDDFFUUDDUDLLUURRDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDLLUURRDUDDUUFFDDFFUUDDUDRRUULLDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDLRUULRDUDDUUFFDDFFUUDDUDLRUULRDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDLRUULRDUDDUUFFDDFFUUDDUDRLUURLDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDLRUURLDUDDUUFFDDFFUUDDUDRLUULRDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDRLUULRDUDDUUFFDDFFUUDDUDLRUURLDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDRLUURLDUDDUUFFDDFFUUDDUDLRUULRDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDRLUURLDUDDUUFFDDFFUUDDUDRLUURLDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDRRUULLDUDDUUFFDDFFUUDDUDLLUURRDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDRRUULLDUDDUUFFDDFFUUDDUDRRUULLDUDDUUFFDDFFUUDUDDUUUUUUDDU',
             'UDDUUUUUUDDUDUDRRUURRDUDDUUFFDDFFUUDDUDLLUULLDUDDUUFFDDFFUUDUDDUUUUUUDDU'),
            moves_444,
            ("Fw", "Fw'", "Bw", "Bw'",
             "Uw", "Uw'", "Dw", "Dw'", # illegal_moves
             "Bw2", "Dw2", "Lw", "Lw'", "Lw2"), # TPR also restricts these

            # prune tables
            (parent.lt_tsai_phase2_centers,
             parent.lt_tsai_phase2_edges_lr_centers),
            linecount=1419536,
            max_depth=5)

    def state(self):
        parent_state = self.parent.state

        edges = self.parent.tsai_phase2_orient_edges_state()
        U_edges = edges[0:8]
        L_edges = edges[8:16]
        F_edges = edges[16:24]
        R_edges = edges[24:32]
        B_edges = edges[32:40]
        D_edges = edges[40:48]

        centers = []

        for x in centers_444:
            if parent_state[x] in ('U', 'D'):
                centers.append('U')
            elif parent_state[x] in ('L', 'R'):
                centers.append(parent_state[x])
            elif parent_state[x] in ('F', 'B'):
                centers.append('F')

        result = ''.join([
                    ''.join([U_edges[0], U_edges[1],
                             U_edges[2], centers[0], centers[1], U_edges[3],
                             U_edges[4], centers[2], centers[3], U_edges[5],
                             U_edges[6], U_edges[7]]),

                    ''.join([L_edges[0], L_edges[1],
                             L_edges[2], centers[4], centers[5], L_edges[3],
                             L_edges[4], centers[6], centers[7], L_edges[5],
                             L_edges[6], L_edges[7]]),

                    ''.join([F_edges[0], F_edges[1],
                             F_edges[2], centers[8], centers[9], F_edges[3],
                             F_edges[4], centers[10], centers[11], F_edges[5],
                             F_edges[6], F_edges[7]]),

                    ''.join([R_edges[0], R_edges[1],
                             R_edges[2], centers[12], centers[13], R_edges[3],
                             R_edges[4], centers[14], centers[15], R_edges[5],
                             R_edges[6], R_edges[7]]),

                    ''.join([B_edges[0], B_edges[1],
                             B_edges[2], centers[16], centers[17], B_edges[3],
                             B_edges[4], centers[18], centers[19], B_edges[5],
                             B_edges[6], B_edges[7]]),

                    ''.join([D_edges[0], D_edges[1],
                             D_edges[2], centers[20], centers[21], D_edges[3],
                             D_edges[4], centers[22], centers[23], D_edges[5],
                             D_edges[6], D_edges[7]])
                    ])

        return result


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
            linecount=58800,
            max_depth=11)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[square_index] for square_index in centers_444])
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

            # linecount=43866828, # 8-deep
            linecount=4313742, # 7-deep
            max_depth=7)

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        centers_state = ''.join([state[square_index] for square_index in centers_444])
        edges_state = ''.join([state[square_index] for square_index in wings_444])
        return centers_state + edges_state


tsai_phase2_orient_edges_wing_str_map = {
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

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # ==============
        # Phase 1 tables
        # ==============
        # Stage LR centers
        self.lt_tsai_phase1_centers = LookupTable444TsaiPhase1Centers(self)
        self.lt_tsai_phase1_centers.preload_cache()
        self.lt_tsai_phase1 = LookupTableIDA444TsaiPhase1(self)

        # =============
        # Phase2 tables
        # =============
        # - orient the edges into high/low groups
        # - solve LR centers to one of 12 states
        # - stage UD and FB centers
        self.lt_tsai_phase2_centers = LookupTable444TsaiPhase2Centers(self)
        self.lt_tsai_phase2_centers.preload_cache()
        self.lt_tsai_phase2_edges_lr_centers = LookupTable444TsaiPhase2EdgesLRCenters(self)
        self.lt_tsai_phase2 = LookupTableIDA444TsaiPhase2(self)
        self.lt_tsai_phase2.preload_cache()

        # =============
        # Phase3 tables
        # =============
        self.lt_tsai_phase3_edges_solve = LookupTable444TsaiPhase3Edges(self)
        self.lt_tsai_phase3_centers_solve = LookupTable444TsaiPhase3CentersSolve(self)
        self.lt_tsai_phase3 = LookupTableIDA444TsaiPhase3(self)
        self.lt_tsai_phase3_centers_solve.preload_cache()
        self.lt_tsai_phase3.preload_cache()

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
                wing_str = wing_str_map[''.join((state_x, state_y))]
                wing_tuple = (x, y, state_x, state_y)

                if wing_tuple not in new_tsai_phase2_orient_edges_444:
                    new_tsai_phase2_orient_edges_444[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str)

        print("new tsai_phase2_orient_edges_444\n\n%s\n\n" % pformat(new_tsai_phase2_orient_edges_444))
        log.info("new_tsai_phase2_orient_edges_444 has %d entries" % len(new_tsai_phase2_orient_edges_444))
        sys.exit(0)

    def tsai_phase2_orient_edges_state(self):
        state = self.state
        result = [tsai_phase2_orient_edges_444[(x, y, state[x], state[y])] for (x, y) in tsai_phase2_orient_edges_tuples]
        result = ''.join(result)
        return result

    def tsai_phase2_orient_edges_print(self):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()

        orient_edge_state = list(self.tsai_phase2_orient_edges_state())
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

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        log.info("%s: Start of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_tsai_phase1_centers.solve()
        #self.lt_tsai_phase1.solve()
        self.print_cube()
        log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Test the phase2 prune tables
        #self.lt_tsai_phase2_centers.solve()
        #self.lt_tsai_phase2_edges_lr_centers.solve()
        #self.print_cube()
        #self.tsai_phase2_orient_edges_print()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_tsai_phase2.avoid_oll = True
        self.lt_tsai_phase2.solve()
        self.print_cube()
        self.tsai_phase2_orient_edges_print()
        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Testing the phase3 prune tables
        #self.lt_tsai_phase3_edges_solve.solve()
        #self.lt_tsai_phase3_centers_solve.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_tsai_phase3.avoid_oll = True
        self.lt_tsai_phase3.avoid_pll = True
        self.lt_tsai_phase3.solve()
        self.print_cube()
        log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
