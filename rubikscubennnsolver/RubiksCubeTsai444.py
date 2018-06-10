#!/usr/bin/env python3

from rubikscubennnsolver.RubiksCube444 import (
    RubiksCube444,
    LookupTable444Edges,
    moves_4x4x4,
    centers_444,
    edges_444,
    wings_444,
    UD_centers_444,
    LR_centers_444,
    UFBD_centers_444,
    rotate_444,
    reflect_x_444
)
from rubikscubennnsolver.RubiksCube444Misc import (
    high_edges_444,
    low_edges_444,
    tsai_phase2_orient_edges_444
)
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA
from pprint import pformat
import logging
import sys

log = logging.getLogger(__name__)

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


class LookupTable444TsaiPhase1(LookupTable):
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
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable444TsaiPhase2Centers(LookupTable):
    """
    lookup-table-4x4x4-step61-centers.txt
    =====================================
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
        result = []

        for index in centers_444:
            x = parent_state[index]

            if x in ('L', 'F', 'R', 'U'):
                result.append(x)
            elif x == 'B':
                result.append('F')
            elif x == 'D':
                result.append('U')

        result = ''.join(result)
        return result


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
    'LRRLRLLR'))

class LookupTableIDA444TsaiPhase2(LookupTableIDA):

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step60-tsai-phase2-dummy.txt',
            '111111111111_10425376a8b9ecfdhgkiljnm',
            moves_4x4x4,
            ("Fw", "Fw'", "Bw", "Bw'",
             "Uw", "Uw'", "Dw", "Dw'", # illegal_moves
             "Bw2", "Dw2", "Lw", "Lw'", "Lw2"), # TPR also restricts these

            # prune tables
            (parent.lt_tsai_phase2_centers,),
            linecount=0,
            max_depth=99)

    def state(self):
        babel = {
            'L' : 'L',
            'F' : 'F',
            'R' : 'R',
            'B' : 'F',
            'D' : 'U',
            'U' : 'U',
        }
        parent_state = self.parent.state

        result = [
            # Upper
            parent_state[2], parent_state[3],
            parent_state[5], babel[parent_state[6]], babel[parent_state[7]], parent_state[8],
            parent_state[9], babel[parent_state[10]], babel[parent_state[11]], parent_state[12],
            parent_state[14], parent_state[15],

            # Left
            parent_state[18], parent_state[19],
            parent_state[21], babel[parent_state[22]], babel[parent_state[23]], parent_state[24],
            parent_state[25], babel[parent_state[26]], babel[parent_state[27]], parent_state[28],
            parent_state[30], parent_state[31],

            # Front
            parent_state[34], parent_state[35],
            parent_state[37], babel[parent_state[38]], babel[parent_state[39]], parent_state[40],
            parent_state[41], babel[parent_state[42]], babel[parent_state[43]], parent_state[44],
            parent_state[46], parent_state[47],

            # Right
            parent_state[50], parent_state[51],
            parent_state[53], babel[parent_state[54]], babel[parent_state[55]], parent_state[56],
            parent_state[57], babel[parent_state[58]], babel[parent_state[59]], parent_state[60],
            parent_state[62], parent_state[63],

            # Back
            parent_state[66], parent_state[67],
            parent_state[69], babel[parent_state[70]], babel[parent_state[71]], parent_state[72],
            parent_state[73], babel[parent_state[74]], babel[parent_state[75]], parent_state[76],
            parent_state[78], parent_state[79],

            # Down
            parent_state[82], parent_state[83],
            parent_state[85], babel[parent_state[86]], babel[parent_state[87]], parent_state[88],
            parent_state[89], babel[parent_state[90]], babel[parent_state[91]], parent_state[92],
            parent_state[94], parent_state[95],
        ]

        result = ''.join(result)
        return result

    def search_complete(self, state, steps_to_here):
        parent_state = self.parent.state

        # Are UD and FB staged? Check UD, if it is staged FB has to be staged too.
        for x in UD_centers_444:
            if parent_state[x] not in ('U', 'D'):
                return False

        # Are the LR sides in 1 of the 12 states we want?
        LR_centers = [parent_state[x] for x in LR_centers_444]
        LR_centers = ''.join(LR_centers)

        if LR_centers not in tsai_phase2_LR_center_targets:
            return False

        if not self.parent.edges_possibly_oriented():
            return False

        p3_edges_cost = self.parent.lt_tsai_phase3_edges_solve.steps_cost()

        if p3_edges_cost == 0:
            return False

        p4_edges_cost = self.parent.lt_tsai_phase4_edges.steps_cost()

        # Avoid phase2 solutions that are going to lead to longer phase4 solutions
        # TODO Once the entire table has been built you can drop the == 0 check.
        if p4_edges_cost == 0 or p4_edges_cost > 9:
            log.info("%s: found solution but edges are not in phase4 table" % self)
            return False

        # rotate_xxx() is very fast but it does not append the
        # steps to the solution so put the cube back in original state
        # and execute the steps via a normal rotate() call
        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]

        for step in steps_to_here:
            self.parent.rotate(step)

        return True


def edges_high_low_recolor_444(state):
    """
    Look at all of the high edges and find the low edge for each.
    Return a string that represents where all the low edge siblings live in relation to their high edge counterpart.
    """
    #assert len(state) == 97, "Invalid state %s, len is %d" % (state, len(state))
    low_edge_map = {}

    for (low_edge_index, square_index, partner_index) in low_edges_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        #assert square_value != partner_value, "both squares are %s" % square_value
        wing_str = ''.join(sorted([square_value, partner_value]))
        low_edge_index = str(hex(low_edge_index))[2:]
        state[square_index] = low_edge_index
        state[partner_index] = low_edge_index

        #assert wing_str not in low_edge_map, "We have two %s wings, one at high_index %s %s and one at high_index %s (%d, %d), state %s" %\
        #    (wing_str,
        #     low_edge_map[wing_str],
        #     pformat(low_edges_444[int(low_edge_map[wing_str])]),
        #     low_edge_index,
        #     square_index, partner_index,
        #     ''.join(state[1:]))

        # save low_edge_index in hex and chop the leading 0x via [2:]
        low_edge_map[wing_str] = low_edge_index

    #assert len(low_edge_map.keys()) == 12, "Invalid low_edge_map\n%s\n" % pformat(low_edge_map)

    for (high_edge_index, square_index, partner_index) in high_edges_444:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))
        state[square_index] = low_edge_map[wing_str]
        state[partner_index] = low_edge_map[wing_str]

    return state


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


class LookupTable444TsaiPhase3Edges(LookupTable):
    """
    lookup-table-4x4x4-step71-tsai-phase3-edges.txt
    - without symmetry
    - we use the copy with symmetry I just left this here for the history
    ======================================================
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


    lookup-table-4x4x4-step71-tsai-phase3-edges.txt
    ======================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 7 entries (0 percent, 2.33x previous step)
    3 steps has 24 entries (0 percent, 3.43x previous step)
    4 steps has 103 entries (0 percent, 4.29x previous step)
    5 steps has 619 entries (0 percent, 6.01x previous step)
    6 steps has 4,287 entries (0 percent, 6.93x previous step)
    7 steps has 28,697 entries (0 percent, 6.69x previous step)
    8 steps has 187,493 entries (1 percent, 6.53x previous step)
    9 steps has 1,087,267 entries (7 percent, 5.80x previous step)
    10 steps has 4,323,558 entries (28 percent, 3.98x previous step)
    11 steps has 7,657,009 entries (51 percent, 1.77x previous step)
    12 steps has 1,708,625 entries (11 percent, 0.22x previous step)
    13 steps has 1,448 entries (0 percent, 0.00x previous step)

    Total: 14,999,140 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step71-tsai-phase3-edges.txt',
            '213098ba6574', # this is the same with/without symmetry
            #linecount=239500800, # without symmetry
            linecount=14999140,   # with symmetry
            max_depth=13)

    def state(self):
        parent_state = self.parent.state
        original_state = list('x' + ''.join(parent_state[1:]))

        # Without symmetry
        '''
        state = original_state[:]
        state = edges_high_low_recolor_444(state[:])

        # record the state of all edges
        state = ''.join(state)
        state = ''.join((state[2],   state[9],  state[8],  state[15],
                         state[25], state[24],
                         state[57], state[56],
                         state[82], state[89], state[88], state[95]))
        return state
        '''

        # With symmetry
        results = []

        for seq in symmetry_rotations_tsai_phase3_444:
            state = original_state[:]

            for step in seq.split():
                if step == 'reflect-x':
                    state = reflect_x_444(state[:])
                else:
                    state = rotate_444(state[:], step)

            state = edges_high_low_recolor_444(state[:])

            # record the state of all edges
            state = ''.join((state[2],   state[9],  state[8],  state[15],
                             state[25], state[24],
                             state[57], state[56],
                             state[82], state[89], state[88], state[95]))
            results.append(state)

        results = sorted(results)
        return results[0]


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


symmetry_rotations_tsai_phase3_444 =\
    ("",
     "y y",
     "x",
     "x y y",
     "x'",
     "x' y y",
     "x x",
     "x x y y",
     "reflect-x",
     "reflect-x y y",
     "reflect-x x",
     "reflect-x x y y",
     "reflect-x x'",
     "reflect-x x' y y",
     "reflect-x x x",
     "reflect-x x x y y")

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
            moves_4x4x4,

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


class LookupTable444TsaiPhase4Edges(LookupTable):
    """
    Stage edges into three L4E groups. Our edges have been oriented into high/low
    groups (12 in each) so this table will have (12!/(4!*4!*4!))^2 entries.

    lookup-table-4x4x4-step400-edges-stage.txt
    ==========================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 42 entries (0 percent, 8.40x previous step)
    3 steps has 352 entries (0 percent, 8.38x previous step)
    4 steps has 3202 entries (0 percent, 9.10x previous step)
    5 steps has 27410 entries (0 percent, 8.56x previous step)
    6 steps has 213613 entries (0 percent, 7.79x previous step)
    7 steps has 1727326 entries (1 percent, 8.09x previous step)
    8 steps has 13028086 entries (13 percent, 7.54x previous step)
    9 steps has 80892742 entries (84 percent, 6.21x previous step)

    Total: 95892778 entries

    This is building on LJs machine, it will have 1.2 billion entries
    so will have to store it as CostOnly
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step400-edges-stage.txt',
            'FFUUUUFFUULLLLUUFFLLLLFFUULLLLUUFFLLLLFFFFUUUUFF',
            linecount=95892778,
            max_depth=9)

    def state(self):
        parent_state = self.parent.state
        result = []
        #result = ''.join([parent_state[square_index] for square_index in UFBD_centers_444])

        for square_index in edges_444:
            # store this in a table...would be faster
            side = self.parent.get_side_for_index(square_index)
            partner_index = side.get_wing_partner(square_index)

            square_value = parent_state[square_index]
            partner_value = parent_state[partner_index]
            wing_str = ''.join([square_value, partner_value])
            result.append(edge_map_to_ULF[wing_str])

        result = ''.join(result)
        return result


class LookupTable444TsaiPhase4Centers(LookupTable):
    """
    lookup-table-4x4x4-step500-tsai-phase4-centers.txt
    ==================================================
    1 steps has 384 entries (7 percent, 0.00x previous step)
    2 steps has 484 entries (9 percent, 1.26x previous step)
    3 steps has 768 entries (15 percent, 1.59x previous step)
    4 steps has 1152 entries (23 percent, 1.50x previous step)
    5 steps has 1088 entries (22 percent, 0.94x previous step)
    6 steps has 832 entries (16 percent, 0.76x previous step)
    7 steps has 192 entries (3 percent, 0.23x previous step)

    Total: 4900 entries
    Average: 4.089796 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step500-tsai-phase4-centers.txt',
            ('UUUUFFFFBBBBDDDD',
             'UUUUFFBBFFBBDDDD',
             'UUUUFFBBBBFFDDDD',
             'UUUUFBFBFBFBDDDD',
             'UUUUFBFBBFBFDDDD',
             'UUUUFBBFBFFBDDDD',
             'UUUUBFFBFBBFDDDD',
             'UUUUBFBFFBFBDDDD',
             'UUUUBFBFBFBFDDDD',
             'UUUUBBFFFFBBDDDD',
             'UUUUBBFFBBFFDDDD',
             'UUUUBBBBFFFFDDDD',
             'UUDDFFFFBBBBUUDD',
             'UUDDFFFFBBBBDDUU',
             'UUDDFFBBFFBBUUDD',
             'UUDDFFBBFFBBDDUU',
             'UUDDFFBBBBFFUUDD',
             'UUDDFFBBBBFFDDUU',
             'UUDDFBFBFBFBUUDD',
             'UUDDFBFBFBFBDDUU',
             'UUDDFBFBBFBFUUDD',
             'UUDDFBFBBFBFDDUU',
             'UUDDFBBFBFFBUUDD',
             'UUDDFBBFBFFBDDUU',
             'UUDDBFFBFBBFUUDD',
             'UUDDBFFBFBBFDDUU',
             'UUDDBFBFFBFBUUDD',
             'UUDDBFBFFBFBDDUU',
             'UUDDBFBFBFBFUUDD',
             'UUDDBFBFBFBFDDUU',
             'UUDDBBFFFFBBUUDD',
             'UUDDBBFFFFBBDDUU',
             'UUDDBBFFBBFFUUDD',
             'UUDDBBFFBBFFDDUU',
             'UUDDBBBBFFFFUUDD',
             'UUDDBBBBFFFFDDUU',
             'UDUDFFFFBBBBUDUD',
             'UDUDFFFFBBBBDUDU',
             'UDUDFFBBFFBBUDUD',
             'UDUDFFBBFFBBDUDU',
             'UDUDFFBBBBFFUDUD',
             'UDUDFFBBBBFFDUDU',
             'UDUDFBFBFBFBUDUD',
             'UDUDFBFBFBFBDUDU',
             'UDUDFBFBBFBFUDUD',
             'UDUDFBFBBFBFDUDU',
             'UDUDFBBFBFFBUDUD',
             'UDUDFBBFBFFBDUDU',
             'UDUDBFFBFBBFUDUD',
             'UDUDBFFBFBBFDUDU',
             'UDUDBFBFFBFBUDUD',
             'UDUDBFBFFBFBDUDU',
             'UDUDBFBFBFBFUDUD',
             'UDUDBFBFBFBFDUDU',
             'UDUDBBFFFFBBUDUD',
             'UDUDBBFFFFBBDUDU',
             'UDUDBBFFBBFFUDUD',
             'UDUDBBFFBBFFDUDU',
             'UDUDBBBBFFFFUDUD',
             'UDUDBBBBFFFFDUDU',
             'UDDUFFFFBBBBDUUD',
             'UDDUFFBBFFBBDUUD',
             'UDDUFFBBBBFFDUUD',
             'UDDUFBFBFBFBDUUD',
             'UDDUFBFBBFBFDUUD',
             'UDDUFBBFBFFBDUUD',
             'UDDUBFFBFBBFDUUD',
             'UDDUBFBFFBFBDUUD',
             'UDDUBFBFBFBFDUUD',
             'UDDUBBFFFFBBDUUD',
             'UDDUBBFFBBFFDUUD',
             'UDDUBBBBFFFFDUUD',
             'DUUDFFFFBBBBUDDU',
             'DUUDFFBBFFBBUDDU',
             'DUUDFFBBBBFFUDDU',
             'DUUDFBFBFBFBUDDU',
             'DUUDFBFBBFBFUDDU',
             'DUUDFBBFBFFBUDDU',
             'DUUDBFFBFBBFUDDU',
             'DUUDBFBFFBFBUDDU',
             'DUUDBFBFBFBFUDDU',
             'DUUDBBFFFFBBUDDU',
             'DUUDBBFFBBFFUDDU',
             'DUUDBBBBFFFFUDDU',
             'DUDUFFFFBBBBUDUD',
             'DUDUFFFFBBBBDUDU',
             'DUDUFFBBFFBBUDUD',
             'DUDUFFBBFFBBDUDU',
             'DUDUFFBBBBFFUDUD',
             'DUDUFFBBBBFFDUDU',
             'DUDUFBFBFBFBUDUD',
             'DUDUFBFBFBFBDUDU',
             'DUDUFBFBBFBFUDUD',
             'DUDUFBFBBFBFDUDU',
             'DUDUFBBFBFFBUDUD',
             'DUDUFBBFBFFBDUDU',
             'DUDUBFFBFBBFUDUD',
             'DUDUBFFBFBBFDUDU',
             'DUDUBFBFFBFBUDUD',
             'DUDUBFBFFBFBDUDU',
             'DUDUBFBFBFBFUDUD',
             'DUDUBFBFBFBFDUDU',
             'DUDUBBFFFFBBUDUD',
             'DUDUBBFFFFBBDUDU',
             'DUDUBBFFBBFFUDUD',
             'DUDUBBFFBBFFDUDU',
             'DUDUBBBBFFFFUDUD',
             'DUDUBBBBFFFFDUDU',
             'DDUUFFFFBBBBUUDD',
             'DDUUFFFFBBBBDDUU',
             'DDUUFFBBFFBBUUDD',
             'DDUUFFBBFFBBDDUU',
             'DDUUFFBBBBFFUUDD',
             'DDUUFFBBBBFFDDUU',
             'DDUUFBFBFBFBUUDD',
             'DDUUFBFBFBFBDDUU',
             'DDUUFBFBBFBFUUDD',
             'DDUUFBFBBFBFDDUU',
             'DDUUFBBFBFFBUUDD',
             'DDUUFBBFBFFBDDUU',
             'DDUUBFFBFBBFUUDD',
             'DDUUBFFBFBBFDDUU',
             'DDUUBFBFFBFBUUDD',
             'DDUUBFBFFBFBDDUU',
             'DDUUBFBFBFBFUUDD',
             'DDUUBFBFBFBFDDUU',
             'DDUUBBFFFFBBUUDD',
             'DDUUBBFFFFBBDDUU',
             'DDUUBBFFBBFFUUDD',
             'DDUUBBFFBBFFDDUU',
             'DDUUBBBBFFFFUUDD',
             'DDUUBBBBFFFFDDUU',
             'DDDDFFFFBBBBUUUU',
             'DDDDFFBBFFBBUUUU',
             'DDDDFFBBBBFFUUUU',
             'DDDDFBFBFBFBUUUU',
             'DDDDFBFBBFBFUUUU',
             'DDDDFBBFBFFBUUUU',
             'DDDDBFFBFBBFUUUU',
             'DDDDBFBFFBFBUUUU',
             'DDDDBFBFBFBFUUUU',
             'DDDDBBFFFFBBUUUU',
             'DDDDBBFFBBFFUUUU',
             'DDDDBBBBFFFFUUUU'),
            linecount=4900,
            max_depth=7)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[square_index] for square_index in UFBD_centers_444])
        return result


class LookupTableIDA444TsaiPhase4(LookupTableIDA):

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step60-tsai-phase2-dummy.txt',
            'TBD',
            moves_4x4x4,

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
            (parent.lt_tsai_phase4_edges,
             parent.lt_tsai_phase4_centers),

            linecount=0,
            max_depth=99)

    def state(self):
        return self.parent.lt_tsai_phase4_centers.state() + self.parent.lt_tsai_phase4_edges.state()

    def search_complete(self, state, steps_to_here):
        if (self.parent.lt_tsai_phase4_centers.state() in self.parent.lt_tsai_phase4_centers.state_target and
            self.parent.lt_tsai_phase4_edges.state() in self.parent.lt_tsai_phase4_edges.state_target and
            self.parent.edges_solveable_via_half_turns()):

            # rotate_xxx() is very fast but it does not append the
            # steps to the solution so put the cube back in original state
            # and execute the steps via a normal rotate() call
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]

            for step in steps_to_here:
                self.parent.rotate(step)

            return True
        else:
            return False


class LookupTable444TsaiPhase5Edges(LookupTable):
    """
    lookup-table-4x4x4-step602-tsai-phase5-edges.txt
    ================================================
    1 steps has 4 entries (6 percent, 0.00x previous step)
    2 steps has 12 entries (18 percent, 3.00x previous step)
    3 steps has 24 entries (37 percent, 2.00x previous step)
    4 steps has 17 entries (26 percent, 0.71x previous step)
    5 steps has 7 entries (10 percent, 0.41x previous step)

    Total: 64 entries
    Average: 3.171875 moves
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step602-tsai-phase5-edges.txt',
            '10425376a8b9ecfdhgkiljnm',
            linecount=64,
            max_depth=5)

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        edges_state = ''.join([state[square_index] for square_index in wings_444])
        return edges_state


class LookupTable444TsaiPhase5Centers(LookupTable):
    """
    lookup-table-4x4x4-step601-tsai-phase5-centers.txt
    ==================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 51 entries (2 percent, 7.29x previous step)
    3 steps has 276 entries (15 percent, 5.41x previous step)
    4 steps has 599 entries (34 percent, 2.17x previous step)
    5 steps has 494 entries (28 percent, 0.82x previous step)
    6 steps has 261 entries (15 percent, 0.53x previous step)
    7 steps has 40 entries (2 percent, 0.15x previous step)

    Total: 1728 entries
    Average: 4.426505 moves
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step601-tsai-phase5-centers.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD',
            linecount=1728,
            max_depth=7)

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        centers_state = ''.join([state[square_index] for square_index in centers_444])
        return centers_state


class LookupTableIDA444TsaiPhase5(LookupTableIDA):
    """
    lookup-table-4x4x4-step600-tsai-phase5.txt
    ==========================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 51 entries (0 percent, 7.29x previous step)
    3 steps has 288 entries (0 percent, 5.65x previous step)
    4 steps has 911 entries (0 percent, 3.16x previous step)
    5 steps has 2682 entries (2 percent, 2.94x previous step)
    6 steps has 7629 entries (6 percent, 2.84x previous step)
    7 steps has 16504 entries (14 percent, 2.16x previous step)
    8 steps has 27996 entries (25 percent, 1.70x previous step)
    9 steps has 31052 entries (28 percent, 1.11x previous step)
    10 steps has 19408 entries (17 percent, 0.63x previous step)
    11 steps has 3864 entries (3 percent, 0.20x previous step)
    12 steps has 200 entries (0 percent, 0.05x previous step)

    Total: 110592 entries
    Average: 8.334681 moves
    """
    # TODO we need to rebuild this but account for OLL and PLL...right now the only
    # reason we are doing IDA is to avoid OLL/PLL. I only built this 6-deep.

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step600-tsai-phase5.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD10425376a8b9ecfdhgkiljnm',
            moves_4x4x4,

            # illegal moves
            ("Uw", "Uw'",
             "Lw", "Lw'",
             "Fw", "Fw'",
             "Rw", "Rw'",
             "Bw", "Bw'",
             "Dw", "Dw'",
             "U", "U'",
             "L", "L'",
             "F", "F'",
             "R", "R'",
             "B", "B'",
             "D", "D'"),

            # prune tables
            (parent.lt_tsai_phase5_edges,
             parent.lt_tsai_phase5_centers),

            linecount=11568,
            max_depth=6)

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])
        centers_state = ''.join([state[square_index] for square_index in centers_444])
        edges_state = ''.join([state[square_index] for square_index in wings_444])
        return centers_state + edges_state


class RubiksCubeTsai444(RubiksCube444):

    def __init__(self, state, order, colormap=None, avoid_pll=True, debug=False):
        RubiksCube444.__init__(self, state, order, colormap, debug)
        self.edge_mapping = {}

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # ==============
        # Phase 1 tables
        # ==============
        # Stage LR centers
        self.lt_tsai_phase1 = LookupTable444TsaiPhase1(self)

        # =============
        # Phase2 tables
        # =============
        # - orient the edges into high/low groups
        # - solve LR centers to one of 12 states
        # - stage UD and FB centers
        self.lt_tsai_phase2_centers = LookupTable444TsaiPhase2Centers(self)
        self.lt_tsai_phase2_centers.preload_cache()
        self.lt_tsai_phase2 = LookupTableIDA444TsaiPhase2(self)


        # =============
        # Phase3 tables
        # =============
        '''
        self.lt_tsai_phase3_edges_solve = LookupTable444TsaiPhase3Edges(self)
        #self.lt_tsai_phase3_edges_solve.preload_cache()
        self.lt_tsai_phase3_centers_solve = LookupTable444TsaiPhase3CentersSolve(self)
        #self.lt_tsai_phase3_centers_solve.preload_cache()
        self.lt_tsai_phase3 = LookupTableIDA444TsaiPhase3(self)
        #self.lt_tsai_phase3.preload_cache()
        #self.lt_tsai_phase3.ida_all_the_way = True
        '''

        # For tsai this tables is only used if the centers have already been solved
        # For non-tsai it is always used
        self.lt_edges = LookupTable444Edges(self)

        # =============
        # Phase4 tables
        # =============
        self.lt_tsai_phase4_centers = LookupTable444TsaiPhase4Centers(self)
        self.lt_tsai_phase4_centers.preload_cache()
        self.lt_tsai_phase4_edges = LookupTable444TsaiPhase4Edges(self)
        #self.lt_tsai_phase4_edges.preload_cache()
        self.lt_tsai_phase4 = LookupTableIDA444TsaiPhase4(self)

        # =============
        # Phase5 tables
        # =============
        self.lt_tsai_phase5_centers = LookupTable444TsaiPhase5Centers(self)
        self.lt_tsai_phase5_centers.preload_cache()
        self.lt_tsai_phase5_edges = LookupTable444TsaiPhase5Edges(self)
        self.lt_tsai_phase5_edges.preload_cache()
        self.lt_tsai_phase5 = LookupTableIDA444TsaiPhase5(self)
        self.lt_tsai_phase5.preload_cache()
        self.lt_tsai_phase5.avoid_oll = True
        self.lt_tsai_phase5.avoid_pll = True
        self.lt_tsai_phase5.ida_all_the_way = True

    def tsai_phase2_orient_edges_state(self, edges_to_flip, return_hex):
        state = self.state
        result = []

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

        for (x, y) in (
                (2, 67), (3, 66), (5, 18), (8, 51), (9, 19), (12, 50), (14, 34),
                (15, 35), (18, 5), (19, 9), (21, 72), (24, 37), (25, 76), (28, 41),
                (30, 89), (31, 85), (34, 14), (35, 15), (37, 24), (40, 53), (41, 28),
                (44, 57), (46, 82), (47, 83), (50, 12), (51, 8), (53, 40), (56, 69),
                (57, 44), (60, 73), (62, 88), (63, 92), (66, 3), (67, 2), (69, 56),
                (72, 21), (73, 60), (76, 25), (78, 95), (79, 94), (82, 46), (83, 47),
                (85, 31), (88, 62), (89, 30), (92, 63), (94, 79), (95, 78)):
            state_x = state[x]
            state_y = state[y]
            wing_str = wing_str_map[''.join((state_x, state_y))]
            high_low = tsai_phase2_orient_edges_444[(x, y, state_x, state_y)]

            if wing_str in edges_to_flip:
                if high_low == 'U':
                    high_low = 'D'
                else:
                    high_low = 'U'

            if return_hex:
                high_low = high_low.replace('D', '0').replace('U', '1')

            result.append(high_low)

        result = ''.join(result)

        if return_hex:
            return "%012x" % int(result, 2)
        else:
            return result

    def tsai_phase2_orient_edges_print(self):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()

        orient_edge_state = list(self.tsai_phase2_orient_edges_state(self.edge_mapping, return_hex=False))
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
        self.lt_tsai_phase1.solve()
        self.print_cube()
        log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Test the phase2 prune tables
        #self.lt_tsai_phase2_centers.solve()
        #self.tsai_phase2_orient_edges_print()
        #self.print_cube()
        #sys.exit(0)

        log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_tsai_phase2.avoid_oll = True
        self.lt_tsai_phase2.avoid_pll = True
        self.lt_tsai_phase2.solve()
        self.print_cube()
        #self.tsai_phase2_orient_edges_print()
        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # This is the old way...saving for a rainy day
        '''
        # Testing the phase3 prune tables
        #self.lt_tsai_phase3_edges_solve.solve()
        #self.lt_tsai_phase3_centers_solve.solve()
        #self.tsai_phase2_orient_edges_print()
        #self.print_cube()

        log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_tsai_phase3.avoid_oll = True
        self.lt_tsai_phase3.avoid_pll = True
        self.lt_tsai_phase3.solve()
        self.print_cube()
        log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        '''

        # Test the phase4 prune tables
        #self.lt_tsai_phase4_centers.solve()
        #self.lt_tsai_phase4_edges.solve()
        #self.print_cube()
        #sys.exit(0)

        log.info("%s: Start of Phase4, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_tsai_phase4.solve()
        self.print_cube()
        log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: End of Phase4, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Testing the phase5 prune tables
        #self.lt_tsai_phase5_centers.solve()
        #self.lt_tsai_phase5_edges.solve()
        #self.print_cube()
        #sys.exit(0)

        log.info("%s: Start of Phase5, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_tsai_phase5.solve()
        self.print_cube()
        log.info("%s: End of Phase5, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Are we setup to skip phase1 of 3x3x3?
        '''
        from rubikscubennnsolver.RubiksCube333 import RubiksCube333
        kociemba_string_333 = self.get_kociemba_string(False)
        cube_333 = RubiksCube333(kociemba_string_333, order='URFDLB')
        #cube_333.print_cube()
        cube_333.lt_init()

        log.info("%s: edges %s, steps %s" %
            (cube_333.lt_phase1_edges,
             cube_333.lt_phase1_edges.state(),
             pformat(cube_333.lt_phase1_edges.steps())))

        log.info("%s: corners %s, steps %s" %
            (cube_333.lt_phase1_corners,
             cube_333.lt_phase1_corners.state(),
             pformat(cube_333.lt_phase1_corners.steps())))
        sys.exit(0)
        '''


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
