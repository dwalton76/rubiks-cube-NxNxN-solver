#!/usr/bin/env python3

from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.LookupTable import (
    get_characters_common_count,
    steps_on_same_face_and_layer,
    LookupTable,
    LookupTableIDA,
)
from pprint import pformat
import logging
import sys

log = logging.getLogger(__name__)


moves_4x4x4 = ("U", "U'", "U2", "Uw", "Uw'", "Uw2",
               "L", "L'", "L2", "Lw", "Lw'", "Lw2",
               "F" , "F'", "F2", "Fw", "Fw'", "Fw2",
               "R" , "R'", "R2", "Rw", "Rw'", "Rw2",
               "B" , "B'", "B2", "Bw", "Bw'", "Bw2",
               "D" , "D'", "D2", "Dw", "Dw'", "Dw2")

solved_4x4x4 = 'UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB'

centers_444 = (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91)

UD_centers_444 = (6, 7, 10, 11, 86, 87, 90, 91)

LR_centers_444 = (22, 23, 26, 27, 54, 55, 58, 59)

edges_444 = (
    2, 3, 5, 8, 9, 12, 14, 15,      # Upper
    18, 19, 21, 24, 25, 28, 30, 31, # Left
    34, 35, 37, 40, 41, 44, 46, 47, # Front
    50, 51, 53, 56, 57, 60, 62, 63, # Right
    66, 67, 69, 72, 73, 76, 78, 79, # Back
    82, 83, 85, 88, 89, 92, 94, 95) # Down

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

centers_solved_states_444 = set()
centers_solved_states_444.add('UUUULLLLFFFFRRRRBBBBDDDD')
centers_solved_states_444.add('UUUUFFFFRRRRBBBBLLLLDDDD')
centers_solved_states_444.add('UUUURRRRBBBBLLLLFFFFDDDD')
centers_solved_states_444.add('UUUUBBBBLLLLFFFFRRRRDDDD')
centers_solved_states_444.add('DDDDLLLLBBBBRRRRFFFFUUUU')
centers_solved_states_444.add('DDDDBBBBRRRRFFFFLLLLUUUU')
centers_solved_states_444.add('DDDDRRRRFFFFLLLLBBBBUUUU')
centers_solved_states_444.add('DDDDFFFFLLLLBBBBRRRRUUUU')
centers_solved_states_444.add('LLLLUUUUBBBBDDDDFFFFRRRR')
centers_solved_states_444.add('LLLLBBBBDDDDFFFFUUUURRRR')
centers_solved_states_444.add('LLLLDDDDFFFFUUUUBBBBRRRR')
centers_solved_states_444.add('LLLLFFFFUUUUBBBBDDDDRRRR')
centers_solved_states_444.add('FFFFLLLLDDDDRRRRUUUUBBBB')
centers_solved_states_444.add('FFFFDDDDRRRRUUUULLLLBBBB')
centers_solved_states_444.add('FFFFRRRRUUUULLLLDDDDBBBB')
centers_solved_states_444.add('FFFFUUUULLLLDDDDRRRRBBBB')
centers_solved_states_444.add('RRRRDDDDBBBBUUUUFFFFLLLL')
centers_solved_states_444.add('RRRRBBBBUUUUFFFFDDDDLLLL')
centers_solved_states_444.add('RRRRUUUUFFFFDDDDBBBBLLLL')
centers_solved_states_444.add('RRRRFFFFDDDDBBBBUUUULLLL')
centers_solved_states_444.add('BBBBUUUURRRRDDDDLLLLFFFF')
centers_solved_states_444.add('BBBBRRRRDDDDLLLLUUUUFFFF')
centers_solved_states_444.add('BBBBDDDDLLLLUUUURRRRFFFF')
centers_solved_states_444.add('BBBBLLLLUUUURRRRDDDDFFFF')

def centers_solved_444(state):
    if state[0:24] in centers_solved_states_444:
        return True
    return False



def get_best_entry(foo):
    # TODO this can only track wings since it is only used by 4x4x4
    best_entry = None
    best_paired_edges = None
    best_paired_wings = None
    best_steps_len = None

    for (paired_edges, paired_wings, steps_len, state) in foo:
        if (best_entry is None or
            paired_edges > best_paired_edges or
            (paired_edges == best_paired_edges and paired_wings > best_paired_wings) or
            (paired_edges == best_paired_edges and paired_wings == best_paired_wings and steps_len < best_steps_len)):

            best_entry = (paired_edges, paired_wings, steps_len, state)
            best_paired_edges = paired_edges
            best_paired_wings = paired_wings
            best_steps_len = steps_len
    return best_entry


def get_edges_paired_binary_signature(state):
    """
    The facelets are numbered:

                  - 02 03 -
                 05  - -  08
                 09  - -  12
                  - 14 15 -

     - 18 19 -    - 34 35 -    - 50 51 -    - 66 67 -
    21  - -  24  37  - -  40  53  - -  56  69  - -  72
    25  - -  28  41  - -  44  57  - -  60  73  - -  76
     - 30 31 -    - 46 47 -    - 62 63 -    - 78 79 -

                  - 82 83 -
                 85  - -  88
                 89  - -  92
                  - 94 95 -


    The wings are labeled 0123456789abcdefghijklmn

                  -  0 1  -
                  2  - -  3
                  4  - -  5
                  -  6 7 -

     -  2 4  -    -  6 7  -    -  5 3  -    -  1 0  -
     8  - -  9    9  - -  c    c  - -  d    d  - -  8
     a  - -  b    b  - -  e    e  - -  f    f  - -  a
     -  k i  -    -  g h  -    -  j l  -    -  n m  -

                  -  g h  -
                  i  - -  j
                  k  - -  l
                  -  m n  -

    'state' goes wing by # wing and records the location of where the sibling wing is located.

    state: 10425376a8b9ecfdhgkiljnm

    index: 000000000011111111112222
           012345678901234567890123

    get_edges_paired_binary_signature('10425376a8b9ecfdhgkiljnm')
    111111111111

    get_edges_paired_binary_signature('7ad9nlg0j14cbm2i6kfh85e3')
    000000000000
    """
    result = []

    # Upper
    if state[0] == '1':
        result.append('1')
    else:
        result.append('0')

    if state[2] == '4':
        result.append('1')
    else:
        result.append('0')

    if state[4] == '5':
        result.append('1')
    else:
        result.append('0')

    if state[6] == '7':
        result.append('1')
    else:
        result.append('0')

    # Left
    if state[8] == 'a':
        result.append('1')
    else:
        result.append('0')

    if state[10] == 'b':
        result.append('1')
    else:
        result.append('0')

    # Right
    if state[12] == 'e':
        result.append('1')
    else:
        result.append('0')

    if state[14] == 'f':
        result.append('1')
    else:
        result.append('0')

    # Down
    if state[16] == 'h':
        result.append('1')
    else:
        result.append('0')

    if state[18] == 'k':
        result.append('1')
    else:
        result.append('0')

    if state[20] == 'l':
        result.append('1')
    else:
        result.append('0')

    if state[22] == 'n':
        result.append('1')
    else:
        result.append('0')

    return ''.join(result)


'''
lookup-table-4x4x4-step11-UD-centers-stage.txt
lookup-table-4x4x4-step12-LR-centers-stage.txt
lookup-table-4x4x4-step13-FB-centers-stage.txt
==============================================
1 steps has 3 entries (0 percent, 0.00x previous step)
2 steps has 36 entries (0 percent, 12.00x previous step)
3 steps has 484 entries (0 percent, 13.44x previous step)
4 steps has 5,408 entries (0 percent, 11.17x previous step)
5 steps has 48,955 entries (6 percent, 9.05x previous step)
6 steps has 242,011 entries (32 percent, 4.94x previous step)
7 steps has 362,453 entries (49 percent, 1.50x previous step)
8 steps has 75,955 entries (10 percent, 0.21x previous step)
9 steps has 166 entries (0 percent, 0.00x previous step)

Total: 735,471 entries
'''
class LookupTable444UDCentersStage(LookupTable):

    def __init__(self, parent):

        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step11-UD-centers-stage.txt',
            'f0000f',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('U', 'D') else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable444LRCentersStage(LookupTable):

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step12-LR-centers-stage.txt',
            '0f0f00',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable444FBCentersStage(LookupTable):

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step13-FB-centers-stage.txt',
            '00f0f0',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('F', 'B') else '0' for x in centers_444])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA444ULFRBDCentersStage(LookupTableIDA):
    """
    lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt
    ==================================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 54 entries (0 percent, 13.50x previous step)
    3 steps has 726 entries (0 percent, 13.44x previous step)
    4 steps has 9,300 entries (0 percent, 12.81x previous step)
    5 steps has 121,407 entries (7 percent, 13.05x previous step)
    6 steps has 1,586,554 entries (92 percent, 13.07x previous step)

    Total: 1,718,045 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt',
            'UUUULLLLFFFFLLLLFFFFUUUU',
            moves_4x4x4,

            # illegal_moves...ignoring these increases the average solution
            # by less than 1 move but makes the IDA search about 20x faster
            ("Lw", "Lw'", "Lw2",
             "Bw", "Bw'", "Bw2",
             "Dw", "Dw'", "Dw2"),

            # prune tables
            (parent.lt_UD_centers_stage,
             parent.lt_LR_centers_stage,
             parent.lt_FB_centers_stage),
            linecount=1718045)

    def state(self):
        parent_state = self.parent.state
        result = []

        for index in centers_444:
            x = parent_state[index]

            if x in ('L', 'F', 'U'):
                result.append(x)
            elif x == 'R':
                result.append('L')
            elif x == 'B':
                result.append('F')
            elif x == 'D':
                result.append('U')

        result = ''.join(result)
        return result


class LookupTable444ULFRBDCentersSolve(LookupTable):
    """
    lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt
    ==================================================
    1 steps has 96 entries (0 percent, 0.00x previous step)
    2 steps has 1,008 entries (0 percent, 10.50x previous step)
    3 steps has 8,208 entries (0 percent, 8.14x previous step)
    4 steps has 41,712 entries (2 percent, 5.08x previous step)
    5 steps has 145,560 entries (7 percent, 3.49x previous step)
    6 steps has 321,576 entries (15 percent, 2.21x previous step)
    7 steps has 514,896 entries (25 percent, 1.60x previous step)
    8 steps has 496,560 entries (24 percent, 0.96x previous step)
    9 steps has 324,096 entries (15 percent, 0.65x previous step)
    10 steps has 177,408 entries (8 percent, 0.55x previous step)
    11 steps has 26,880 entries (1 percent, 0.15x previous step)

    Total: 2,058,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD',
            linecount=2058000)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in centers_444])
        return result


class LookupTable444ULFRBDCentersSolveEdgesStage(LookupTableIDA):

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step60-tsai-phase2-dummy.txt',
            'TBD',
            moves_4x4x4,
            ("Rw", "Rw'", "Lw", "Lw'",
             "Fw", "Fw'", "Bw", "Bw'",
             "Uw", "Uw'", "Dw", "Dw'"),

            # prune tables
            (parent.lt_ULFRBD_centers_solve,),
            linecount=0)

    def state(self):
        state = edges_recolor_pattern_444(self.parent.state[:])

        edges = ''.join([state[square_index] for square_index in wings_444])
        centers = ''.join([state[x] for x in centers_444])

        return centers + edges

    def search_complete(self, state, steps_to_here):

        if centers_solved_444(state) and self.parent.solve_all_edges_444(use_bfs=False, apply_steps_if_found=False):

            # rotate_xxx() is very fast but it does not append the
            # steps to the solution so put the cube back in original state
            # and execute the steps via a normal rotate() call
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]

            for step in steps_to_here:
                self.parent.rotate(step)

            '''
            if self.avoid_oll and self.parent.center_solution_leads_to_oll_parity():
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
                log.info("%s: IDA found match but it leads to OLL" % self)
                return False

            if self.avoid_pll and self.parent.edge_solution_leads_to_pll_parity():
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
                log.info("%s: IDA found match but it leads to PLL" % self)
                return False
            '''

            return True

        return False



"""
lookup-table-4x4x4-step201-UD-centers-solve.txt
lookup-table-4x4x4-step202-LR-centers-solve.txt
lookup-table-4x4x4-step203-FB-centers-solve.txt
===============================================
1 steps has 7 entries (0 percent, 0.00x previous step)
2 steps has 84 entries (0 percent, 12.00x previous step)
3 steps has 1118 entries (0 percent, 13.31x previous step)
4 steps has 14208 entries (0 percent, 12.71x previous step)
5 steps has 163085 entries (0 percent, 11.48x previous step)
6 steps has 1586257 entries (3 percent, 9.73x previous step)
7 steps has 10286840 entries (19 percent, 6.48x previous step)
8 steps has 26985405 entries (52 percent, 2.62x previous step)
9 steps has 12258437 entries (23 percent, 0.45x previous step)
10 steps has 187529 entries (0 percent, 0.02x previous step)

Total: 51482970 entries
Average: 7.973232 moves
"""
class LookupTable444UDCentersSolveUnstaged(LookupTable):

    def __init__(self, parent):

        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step201-UD-centers-solve.txt',
            'UUUUxxxxxxxxxxxxxxxxDDDD',
            linecount=51482970)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] if parent_state[x] in ('U', 'D') else 'x' for x in centers_444])
        return result


class LookupTable444LRCentersSolveUnstaged(LookupTable):

    def __init__(self, parent):

        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step202-LR-centers-solve.txt',
            'xxxxLLLLxxxxRRRRxxxxxxxx',
            linecount=51482970)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] if parent_state[x] in ('L', 'R') else 'x' for x in centers_444])
        return result


class LookupTable444FBCentersSolveUnstaged(LookupTable):

    def __init__(self, parent):

        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step203-FB-centers-solve.txt',
            'xxxxxxxxFFFFxxxxBBBBxxxx',
            linecount=51482970)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] if parent_state[x] in ('F', 'B') else 'x' for x in centers_444])
        return result


class LookupTableIDA444ULFRBDCentersSolveUnstaged(LookupTableIDA):
    """
    lookup-table-4x4x4-step200-ULFRBD-centers-solve-unstaged.txt
    ============================================================
    1 steps has 10 entries (0 percent, 0.00x previous step)
    2 steps has 162 entries (0 percent, 16.20x previous step)
    3 steps has 2,427 entries (0 percent, 14.98x previous step)
    4 steps has 35,830 entries (0 percent, 14.76x previous step)
    5 steps has 527,561 entries (0 percent, 14.72x previous step)
    6 steps has 7,683,218 entries (6 percent, 14.56x previous step)
    7 steps has 111,158,950 entries (93 percent, 14.47x previous step)

    Total: 119,408,158 entries
    Average: 6.925831 moves
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step200-ULFRBD-centers-solve-unstaged.txt',
            'UUUULLLLFFFFRRRRBBBBDDDD',
            moves_4x4x4,

            # illegal_moves...ignoring these increases the average solution
            # a little but makes the IDA search much faster
            ("Lw", "Lw'", "Lw2",
             "Bw", "Bw'", "Bw2",
             "Dw", "Dw'", "Dw2"),

            # prune tables
            (parent.lt_UD_centers_solve_unstaged,
             parent.lt_LR_centers_solve_unstaged,
             parent.lt_FB_centers_solve_unstaged),
            linecount=119408158)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in centers_444])
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


class LookupTable444Edges(LookupTable):
    """
    lookup-table-4x4x4-step110-edges.txt (10-deep)
    ==============================================
    2 steps has 1 entries (0 percent, 0.00x previous step)
    5 steps has 432 entries (0 percent, 432.00x previous step)
    6 steps has 2,053 entries (0 percent, 4.75x previous step)
    7 steps has 15,475 entries (0 percent, 7.54x previous step)
    8 steps has 151,530 entries (2 percent, 9.79x previous step)
    9 steps has 991,027 entries (13 percent, 6.54x previous step)
    10 steps has 6,203,073 entries (84 percent, 6.26x previous step)

    Total: 7,363,591 entries
    Average: 9.816544 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-4x4x4-step110-edges.txt',
            '111111111111_10425376a8b9ecfdhgkiljnm',
            linecount=7363591) # 10-deep


class RubiksCube444(RubiksCube):

    def __init__(self, state, order, colormap=None, avoid_pll=True, debug=False):
        RubiksCube.__init__(self, state, order, colormap, debug)
        self.avoid_pll = avoid_pll

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
        corners = (1, 4, 13, 16,
                   17, 20, 29, 32,
                   33, 36, 45, 48,
                   49, 52, 61, 64,
                   65, 68, 77, 80,
                   81, 84, 93, 96)

        centers = (6, 7, 10, 11,
                   22, 23, 26, 27,
                   38, 39, 42, 43,
                   54, 55, 58, 59,
                   70, 71, 74, 75,
                   86, 87, 90, 91)

        edge_orbit_0 = (2, 3, 8, 12, 15, 14, 9, 5,
                        18, 19, 24, 28, 31, 30, 25, 21,
                        34, 35, 40, 44, 47, 46, 41, 37,
                        50, 51, 56, 60, 62, 63, 57, 53,
                        66, 67, 72, 76, 79, 78, 73, 69,
                        82, 83, 88, 92, 95, 94, 89, 85)

        self._sanity_check('corners', corners, 4)
        self._sanity_check('centers', centers, 4)
        self._sanity_check('edge-orbit-0', edge_orbit_0, 8)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # ==============
        # Phase 1 tables
        # ==============
        # prune tables
        self.lt_UD_centers_stage = LookupTable444UDCentersStage(self)
        self.lt_LR_centers_stage = LookupTable444LRCentersStage(self)
        self.lt_FB_centers_stage = LookupTable444FBCentersStage(self)

        # Stage all centers via IDA
        self.lt_ULFRBD_centers_stage = LookupTableIDA444ULFRBDCentersStage(self)

        # =============
        # Phase2 tables
        # =============
        self.lt_ULFRBD_centers_solve = LookupTable444ULFRBDCentersSolve(self)
        self.lt_ULFRBD_centers_solve_edges_stage = LookupTable444ULFRBDCentersSolveEdgesStage(self)
        self.lt_ULFRBD_centers_solve_edges_stage.avoid_pll = True
        self.lt_ULFRBD_centers_solve_edges_stage.avoid_oll = True

        # Experiment
        #self.lt_UD_centers_solve_unstaged = LookupTable444UDCentersSolveUnstaged(self)
        #self.lt_LR_centers_solve_unstaged = LookupTable444LRCentersSolveUnstaged(self)
        #self.lt_FB_centers_solve_unstaged = LookupTable444FBCentersSolveUnstaged(self)
        #self.lt_ULFRBD_centers_solve_unstaged = LookupTableIDA444ULFRBDCentersSolveUnstaged(self)
        #self.lt_ULFRBD_centers_solve_unstaged.avoid_oll = True

        # Edges table
        self.lt_edges = LookupTable444Edges(self)

    def group_centers_guts(self):
        self.lt_init()

        # If the centers are already solve then return and let group_edges() pair the edges
        if self.centers_solved():
            return

        '''
        Experiment to try solving all centers without staging...the IDA search takes
        way too long and the tables required are huge. For my main test cube it found
        a centers solution of 18 steps but took about 6m to do so.  My normal centers
        solver where I stage first, then solve, takes a few seconds and finds a solution
        21 steps long.

        # test the prune tables
        #self.lt_UD_centers_solve_unstaged.solve()
        #self.lt_LR_centers_solve_unstaged.solve()
        #self.lt_FB_centers_solve_unstaged.solve()
        #self.print_cube()
        #sys.exit(0)

        log.info("%s: Start of Phase1" % self)
        self.lt_ULFRBD_centers_solve_unstaged.solve()
        self.print_cube()
        log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        return
        '''

        log.info("%s: Start of Phase1" % self)
        self.lt_ULFRBD_centers_stage.avoid_oll = True
        #self.lt_ULFRBD_centers_stage.ida_all_the_way = True
        self.lt_ULFRBD_centers_stage.solve()
        self.print_cube()
        log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

        log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.lt_ULFRBD_centers_solve.solve()
        #self.lt_ULFRBD_centers_solve_edges_stage.solve()
        self.print_cube()
        log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")

    def solve_all_edges_444(self, use_bfs, apply_steps_if_found):

        # Remember what things looked like
        original_state = self.state[:]
        original_solution = self.solution[:]

        outer_layer_moves = (
            "U", "U'", "U2",
            "L", "L'", "L2",
            "F", "F'", "F2",
            "R", "R'", "R2",
            "B", "B'", "B2",
            "D", "D'", "D2",
        )
        pre_steps_to_try = []
        pre_steps_to_try.append([])

        if use_bfs:
            for step in outer_layer_moves:
                pre_steps_to_try.append([step,])

            for step1 in outer_layer_moves:
                for step2 in outer_layer_moves:
                    if not steps_on_same_face_and_layer(step1, step2):
                        pre_steps_to_try.append([step1, step2])

            for step1 in outer_layer_moves:
                for step2 in outer_layer_moves:
                    if not steps_on_same_face_and_layer(step1, step2):

                        for step3 in outer_layer_moves:
                            if not steps_on_same_face_and_layer(step2, step3):
                                pre_steps_to_try.append([step1, step2, step3])

            '''
            for step1 in outer_layer_moves:
                for step2 in outer_layer_moves:
                    if not steps_on_same_face_and_layer(step1, step2):
                        for step3 in outer_layer_moves:
                            if not steps_on_same_face_and_layer(step2, step3):
                                for step4 in outer_layer_moves:
                                    if not steps_on_same_face_and_layer(step3, step4):
                                        pre_steps_to_try.append([step1, step2, step3, step4])

            '''
            log.warning("%d pre_steps_to_try" % len(pre_steps_to_try))

        for pre_steps in pre_steps_to_try:
            #log.info("solve_all_edges_444 trying pre_steps %s" % ' '.join(pre_steps))

            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in pre_steps:
                self.rotate(step)

            state = edges_recolor_pattern_444(self.state[:])

            edges_state = ''.join([state[square_index] for square_index in wings_444])
            signature = get_edges_paired_binary_signature(edges_state)
            signature_width = len(signature) + 1
            edges_state = signature + '_' + edges_state


            # If our state is in lookup-table-4x4x4-step100-edges.txt then execute
            # those steps and we are done
            steps = self.lt_edges.steps(edges_state)

            if steps is not None:

                if apply_steps_if_found:
                    for step in steps:
                        self.rotate(step)
                else:
                    self.state = original_state[:]
                    self.solution = original_solution[:]

                return True

        self.state = original_state[:]
        self.solution = original_solution[:]

        return False

    def solve_edges_six_then_six(self):

        if self.edges_paired():
            return True

        state = edges_recolor_pattern_444(self.state[:])

        edges_state = ''.join([state[square_index] for square_index in wings_444])
        signature = get_edges_paired_binary_signature(edges_state)
        signature_width = len(signature) + 1
        edges_state = signature + '_' + edges_state

        # If our state is in lookup-table-4x4x4-step100-edges.txt then execute
        # those steps and we are done
        steps = self.lt_edges.steps(edges_state)

        if steps is not None:
            for step in steps:
                self.rotate(step)
                return True

        # If we are here then we need to look through lookup-table-4x4x4-step100-edges.txt
        # to find the line whose state is the closest match to our own. This allows us to
        # pair some of our unpaired edges and make some progress even though our current
        # state isn't in the lookup table.
        MAX_WING_PAIRS = 12
        MAX_EDGES = 12

        # It takes 12 steps to solve PLL
        PLL_PENALTY = 12

        STATE_TARGET = '111111111111_10425376a8b9ecfdhgkiljnm'

        original_state = self.state[:]
        original_solution = self.solution[:]
        loop_count = 0

        while not self.edges_paired():

            # How many edges are paired?
            pre_non_paired_edges_count = self.get_non_paired_edges_count()
            pre_paired_edges_count = MAX_WING_PAIRS - pre_non_paired_edges_count

            state = edges_recolor_pattern_444(self.state[:])

            edges_state = ''.join([state[square_index] for square_index in wings_444])
            signature = get_edges_paired_binary_signature(edges_state)
            signature_width = len(signature) + 1
            edges_state = signature + '_' + edges_state

            log.info("solve_edges_six_then_six loop %d: signature %s" % (loop_count, signature))

            # Find all of the 'loose' matching entries in our lookup table. 'loose' means the
            # entry will not unpair any of our already paired wings.
            loose_matching_entry = []
            max_wing_pair_count = None

            # This runs much faster (than find_edge_entries_with_loose_signature) because
            # it is only looking over the signatures that are an exact match instead of a
            # loose match. It produces slightly longer solutions but in about 1/6 the time.
            log.debug("%s: find_edge_entries_with_signature start" % self)
            lines_to_examine = self.lt_edges.find_edge_entries_with_signature(signature)
            log.debug("%s: find_edge_entries_with_signature end (found %d)" % (self, len(lines_to_examine)))

            for line in lines_to_examine:
                (phase1_state, phase1_steps) = line.split(':')

                common_count = get_characters_common_count(edges_state,
                                                           phase1_state,
                                                           signature_width)
                wing_pair_count = int(common_count/2)

                # Only bother with this entry if it will pair more wings than are currently paired
                if wing_pair_count > pre_paired_edges_count:

                    if max_wing_pair_count is None:
                        loose_matching_entry.append((wing_pair_count, line))
                        max_wing_pair_count = wing_pair_count

                    elif wing_pair_count > max_wing_pair_count:
                        #loose_matching_entry = []
                        loose_matching_entry.append((wing_pair_count, line))
                        max_wing_pair_count = wing_pair_count

                    elif wing_pair_count == max_wing_pair_count or wing_pair_count >= 4:
                        loose_matching_entry.append((wing_pair_count, line))

            #log.warning("pre_paired_edges_count %d, loose_matching_entry %d" % (pre_paired_edges_count, len(loose_matching_entry)))
            #log.warning("pre_paired_edges_count %d, loose_matching_entry(%d):\n%s\n" %
            #    (pre_paired_edges_count, len(loose_matching_entry), pformat(loose_matching_entry)))
            best_score_states = []

            # Now run through each state:steps in loose_matching_entry
            for (wing_pair_count, line) in loose_matching_entry:
                self.state = original_state[:]
                self.solution = original_solution[:]

                (phase1_edges_state_fake, phase1_steps) = line.split(':')
                phase1_steps = phase1_steps.split()

                # Apply the phase1 steps
                for step in phase1_steps:
                    self.rotate(step)

                phase1_state = edges_recolor_pattern_444(self.state[:])
                phase1_edges_state = ''.join([phase1_state[square_index] for square_index in wings_444])
                phase1_signature = get_edges_paired_binary_signature(phase1_edges_state)
                phase1_edges_state = phase1_signature + '_' + phase1_edges_state

                # If that got us to our state_target then phase1 alone paired all
                # of the edges...this is unlikely
                if phase1_edges_state == STATE_TARGET:
                    if self.edge_solution_leads_to_pll_parity():
                        #best_score_states.append((MAX_EDGES, MAX_WING_PAIRS, len(phase1_steps) + PLL_PENALTY, phase1_steps[:]))
                        pass
                    else:
                        best_score_states.append((MAX_EDGES, MAX_WING_PAIRS, len(phase1_steps), phase1_steps[:]))

                else:
                    # phase1_steps did not pair all edges so do another lookup and execute those steps
                    phase2_steps = self.lt_edges.steps(phase1_edges_state)

                    if phase2_steps is not None:
                        for step in phase2_steps:
                            self.rotate(step)

                        phase2_state = edges_recolor_pattern_444(self.state[:])
                        phase2_edges_state = ''.join([phase2_state[square_index] for square_index in wings_444])
                        phase2_signature = get_edges_paired_binary_signature(phase2_edges_state)
                        phase2_edges_state = phase2_signature + '_' + phase2_edges_state
                        phase12_steps = phase1_steps + phase2_steps

                        if phase2_edges_state == STATE_TARGET:

                            if self.edge_solution_leads_to_pll_parity():
                                #best_score_states.append((MAX_EDGES, MAX_WING_PAIRS, len(phase12_steps) + PLL_PENALTY, phase12_steps[:]))
                                pass
                            else:
                                best_score_states.append((MAX_EDGES, MAX_WING_PAIRS, len(phase12_steps), phase12_steps[:]))
                        else:
                            post_non_paired_edges_count = self.get_non_paired_edges_count()
                            paired_edges_count = MAX_WING_PAIRS - post_non_paired_edges_count

                            best_score_states.append((paired_edges_count, paired_edges_count, len(phase12_steps), phase12_steps[:]))
                    else:
                        post_non_paired_edges_count = self.get_non_paired_edges_count()
                        paired_edges_count = MAX_WING_PAIRS - post_non_paired_edges_count

                        best_score_states.append((paired_edges_count, paired_edges_count, len(phase1_steps), phase1_steps[:]))

                #log.info("HERE 10 %s: %s, %s, phase1_edges_state %s, phase2 steps %s" %
                #    (self, wing_pair_count, line, phase1_edges_state, pformat(phase2_steps)))

            #log.info("best_score_states:\n%s" % pformat(best_score_states))
            best_entry = get_best_entry(best_score_states)
            #log.info("best_entry: %s" % pformat(best_entry))

            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in best_entry[3]:
                self.rotate(step)

            original_state = self.state[:]
            original_solution = self.solution[:]

            log.info("solve_edges_six_then_six loop %d: went from %d edges to %d edges in %d moves" %
                (loop_count, pre_paired_edges_count, best_entry[0], len(best_entry[3])))
            loop_count += 1

    def group_edges(self):

        if self.edges_paired():
            self.solution.append('EDGES_GROUPED')
            return

        self.lt_init()

        # use_bfs needs more testing...I'm not sure it buys us much
        if not self.solve_all_edges_444(use_bfs=False, apply_steps_if_found=True):
            self.solve_edges_six_then_six()

        log.info("%s: edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.solution.append('EDGES_GROUPED')


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
