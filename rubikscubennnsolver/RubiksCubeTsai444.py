#!/usr/bin/env python3

from rubikscubennnsolver.RubiksCube444 import (
    RubiksCube444,
    LookupTable444Edges,
    moves_4x4x4,
    centers_444,
    wings_444,
    UD_centers_444,
    LR_centers_444,
)
from rubikscubennnsolver.RubiksCube444Misc import tsai_phase2_orient_edges_444
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA
from rubikscubennnsolver.rotate_xxx import rotate_444
import logging

log = logging.getLogger(__name__)


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

            # dwalton how can we use an edge prune table here?
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

        # If we are here then our centers are all good...check the edges.
        # If the edges are not in lt_tsai_phase3_edges_solve it may throw a KeyError
        try:
            if self.parent.lt_tsai_phase3_edges_solve.steps() is not None and self.parent.edge_swaps_even(False, None, False):

                #log.warning("phase3_edges state %s, steps %s" % (
                #    self.parent.lt_tsai_phase3_edges_solve.state(),
                #    ' '.join(self.parent.lt_tsai_phase3_edges_solve.steps())))

                # rotate_xxx() is very fast but it does not append the
                # steps to the solution so put the cube back in original state
                # and execute the steps via a normal rotate() call
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]

                for step in steps_to_here:
                    self.parent.rotate(step)

                return True

        except KeyError:
            pass

        return False


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

# 12-23 are high edges, make these U (1)
# 0-11 are low edges, make these D (6)
# https://github.com/cs0x7f/TPR-4x4x4-Solver/blob/master/src/FullCube.java
high_edges_444 = ((14, 2, 67),  # upper
                  (13, 9, 19),
                  (15, 8, 51),
                  (12, 15, 35),
                  (21, 25, 76), # left
                  (20, 24, 37),
                  (23, 57, 44), # right
                  (22, 56, 69),
                  (18, 82, 46), # down
                  (17, 89, 30),
                  (19, 88, 62),
                  (16, 95, 78))


low_edges_444 = ((2, 3, 66),  # upper
                 (1, 5, 18),
                 (3, 12, 50),
                 (0, 14, 34),
                 (9, 21, 72), # left
                 (8, 28, 41),
                 (11, 53, 40), # right
                 (10, 60, 73),
                 (6, 83, 47), # down
                 (5, 85, 31),
                 (7, 92, 63),
                 (4, 94, 79))


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


def reflect_x_444(cube):
    return [cube[0],
           cube[93], cube[94], cube[95], cube[96],
           cube[89], cube[90], cube[91], cube[92],
           cube[85], cube[86], cube[87], cube[88],
           cube[81], cube[82], cube[83], cube[84],
           cube[29], cube[30], cube[31], cube[32],
           cube[25], cube[26], cube[27], cube[28],
           cube[21], cube[22], cube[23], cube[24],
           cube[17], cube[18], cube[19], cube[20],
           cube[45], cube[46], cube[47], cube[48],
           cube[41], cube[42], cube[43], cube[44],
           cube[37], cube[38], cube[39], cube[40],
           cube[33], cube[34], cube[35], cube[36],
           cube[61], cube[62], cube[63], cube[64],
           cube[57], cube[58], cube[59], cube[60],
           cube[53], cube[54], cube[55], cube[56],
           cube[49], cube[50], cube[51], cube[52],
           cube[77], cube[78], cube[79], cube[80],
           cube[73], cube[74], cube[75], cube[76],
           cube[69], cube[70], cube[71], cube[72],
           cube[65], cube[66], cube[67], cube[68],
           cube[13], cube[14], cube[15], cube[16],
           cube[9], cube[10], cube[11], cube[12],
           cube[5], cube[6], cube[7], cube[8],
           cube[1], cube[2], cube[3], cube[4]]


class LookupTable444TsaiPhase3Edges(LookupTable):
    """
    lookup-table-4x4x4-step71-tsai-phase3-edges.txt
    - without symmetry
    - we use the copy with symmetry I just left this here for the history
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


    lookup-table-4x4x4-step71-tsai-phase3-edges.txt
    - with symmetry
    ===============================================
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
            '213098ba6574',
            linecount=14999140,
            max_depth=13)

    def state(self):
        parent_state = self.parent.state
        original_state = list('x' + ''.join(parent_state[1:]))
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
            state = ''.join(state)
            state = ''.join((state[2],   state[9],  state[8],  state[15],
                             state[25], state[24],
                             state[57], state[56],
                             state[82], state[89], state[88], state[95]))
            results.append(state[:])

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

        result = [
            # Upper
            parent_state[6],
            parent_state[7],
            parent_state[10],
            parent_state[11],

            # Left
            parent_state[22],
            parent_state[23],
            parent_state[26],
            parent_state[27],

            # Front
            parent_state[38],
            parent_state[39],
            parent_state[42],
            parent_state[43],

            # Right
            parent_state[54],
            parent_state[55],
            parent_state[58],
            parent_state[59],

            # Back
            parent_state[70],
            parent_state[71],
            parent_state[74],
            parent_state[75],

            # Down
            parent_state[86],
            parent_state[87],
            parent_state[90],
            parent_state[91]
        ]

        result = ''.join(result)
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
            linecount=4313742,
            max_depth=7)

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
        self.lt_tsai_phase2 = LookupTableIDA444TsaiPhase2(self)


        # =============
        # Phase3 tables
        # =============
        self.lt_tsai_phase3_edges_solve = LookupTable444TsaiPhase3Edges(self)
        self.lt_tsai_phase3_centers_solve = LookupTable444TsaiPhase3CentersSolve(self)
        self.lt_tsai_phase3 = LookupTableIDA444TsaiPhase3(self)

        # For tsai this tables is only used if the centers have already been solved
        # For non-tsai it is always used
        self.lt_edges = LookupTable444Edges(self)

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

        # Test the prune table
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
        log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

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


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
