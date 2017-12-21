
from collections import OrderedDict
from pprint import pformat
from rubikscubennnsolver.RubiksCubeNNNEvenEdges import RubiksCubeNNNEvenEdges
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_4x4x4
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_5x5x5
from rubikscubennnsolver.RubiksSide import Side, SolveError
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA
import logging
import math
import os
import random
import re
import subprocess
import sys

log = logging.getLogger(__name__)


moves_6x6x6 = ("U", "U'", "U2", "Uw", "Uw'", "Uw2", "3Uw", "3Uw'", "3Uw2",
               "L", "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2",
               "F" , "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2",
               "R" , "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2",
               "B" , "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2",
               "D" , "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2")
solved_6x6x6 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'


class LookupTable666UDInnerXCenterStage(LookupTable):
    """
    Stage the inner X-centers
    24!/(8!*16!) is 735,471

    lookup-table-6x6x6-step10-UD-inner-x-centers-stage.txt
    ======================================================
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
            'lookup-table-6x6x6-step10-UD-inner-x-centers-stage.txt',
            '066000000000000000000660',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            'x', 'x', 'x', 'x',
            'x', parent_state[15], parent_state[16], 'x',
            'x', parent_state[21], parent_state[22], 'x',
            'x', 'x', 'x', 'x',

            # Left
            'x', 'x', 'x', 'x',
            'x', parent_state[51], parent_state[52], 'x',
            'x', parent_state[57], parent_state[58], 'x',
            'x', 'x', 'x', 'x',

            # Front
            'x', 'x', 'x', 'x',
            'x', parent_state[87], parent_state[88], 'x',
            'x', parent_state[93], parent_state[94], 'x',
            'x', 'x', 'x', 'x',

            # Right
            'x', 'x', 'x', 'x',
            'x', parent_state[123], parent_state[124], 'x',
            'x', parent_state[129], parent_state[130], 'x',
            'x', 'x', 'x', 'x',

            # Back
            'x', 'x', 'x', 'x',
            'x', parent_state[159], parent_state[160], 'x',
            'x', parent_state[165], parent_state[166], 'x',
            'x', 'x', 'x', 'x',

            # Down
            'x', 'x', 'x', 'x',
            'x', parent_state[195], parent_state[196], 'x',
            'x', parent_state[201], parent_state[202], 'x',
            'x', 'x', 'x', 'x'
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable666UDObliqueEdgePairingLeftOnly(LookupTable):
    """
    lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt
    ===============================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 82 entries (0 percent, 16.40x previous step)
    3 steps has 1,198 entries (0 percent, 14.61x previous step)
    4 steps has 13,818 entries (1 percent, 11.53x previous step)
    5 steps has 115,638 entries (15 percent, 8.37x previous step)
    6 steps has 399,478 entries (54 percent, 3.45x previous step)
    7 steps has 204,612 entries (27 percent, 0.51x previous step)
    8 steps has 640 entries (0 percent, 0.00x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt',
            '990000000099',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            parent_state[9], 'x',
            'x', parent_state[17],
            parent_state[20], 'x',
            'x', parent_state[28],

            # Left
            parent_state[45], 'x',
            'x', parent_state[53],
            parent_state[56], 'x',
            'x', parent_state[64],

            # Front
            parent_state[81], 'x',
            'x', parent_state[89],
            parent_state[92], 'x',
            'x', parent_state[100],

            # Right
            parent_state[117], 'x',
            'x', parent_state[125],
            parent_state[128], 'x',
            'x', parent_state[136],

            # Back
            parent_state[153], 'x',
            'x', parent_state[161],
            parent_state[164], 'x',
            'x', parent_state[172],

            # Down
            parent_state[189], 'x',
            'x', parent_state[197],
            parent_state[200], 'x',
            'x', parent_state[208],
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable666UDObliqueEdgePairingRightOnly(LookupTable):
    """
    lookup-table-6x6x6-step22-UD-oblique-edge-pairing-right-only.txt
    ================================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 82 entries (0 percent, 16.40x previous step)
    3 steps has 1,198 entries (0 percent, 14.61x previous step)
    4 steps has 13,818 entries (1 percent, 11.53x previous step)
    5 steps has 115,638 entries (15 percent, 8.37x previous step)
    6 steps has 399,478 entries (54 percent, 3.45x previous step)
    7 steps has 204,612 entries (27 percent, 0.51x previous step)
    8 steps has 640 entries (0 percent, 0.00x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step22-UD-oblique-edge-pairing-right-only.txt',
            '660000000066',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            'x', parent_state[10],
            parent_state[14], 'x',
            'x', parent_state[23],
            parent_state[27], 'x',

            # Left
            'x', parent_state[46],
            parent_state[50], 'x',
            'x', parent_state[59],
            parent_state[63], 'x',


            # Front
            'x', parent_state[82],
            parent_state[86], 'x',
            'x', parent_state[95],
            parent_state[99], 'x',

            # Right
            'x', parent_state[118],
            parent_state[122], 'x',
            'x', parent_state[131],
            parent_state[135], 'x',

            # Back
            'x', parent_state[154],
            parent_state[158], 'x',
            'x', parent_state[167],
            parent_state[171], 'x',

            # Down
            'x', parent_state[190],
            parent_state[194], 'x',
            'x', parent_state[203],
            parent_state[207], 'x',
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA666UDObliqueEdgePairing(LookupTableIDA):
    """
    Now pair the UD oblique edges so that we can reduce the 6x6x6 centers to a 5x5x5
    (24!/(8!*16!))^2 is 540,917,591,841 so this is too large for us to build so use
    IDA and build it 8 steps deep.

    Our prune tables will be to solve on the left or right oblique edges. Each of these
    tables are 24!/(8!*16!) or 735,471
    735471/540917591841 is 0.000 001 3596729171

    This IDA search can take a few dozen seconds

    lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt
    =====================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 82 entries (0 percent, 16.40x previous step)
    3 steps has 1,434 entries (0 percent, 17.49x previous step)
    4 steps has 24,198 entries (0 percent, 16.87x previous step)
    5 steps has 405,916 entries (5 percent, 16.77x previous step)
    6 steps has 6,839,392 entries (94 percent, 16.85x previous step)

    Total: 7,271,027 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt',
            'ff00000000ff',
            moves_6x6x6,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", # These would break up the staged UD inner x-centers
             "3Lw", "3Lw'", "3Lw2",        # can skip these for 6x6x6 cubes
             "3Dw", "3Dw'", "3Dw2",
             "3Bw", "3Bw'", "3Bw2"),

            # prune tables
            (parent.lt_UD_oblique_edge_pairing_left_only,
             parent.lt_UD_oblique_edge_pairing_right_only),
            linecount=7271027)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            parent_state[9], parent_state[10],
            parent_state[14], parent_state[17],
            parent_state[20], parent_state[23],
            parent_state[27], parent_state[28],

            # Left
            parent_state[45], parent_state[46],
            parent_state[50], parent_state[53],
            parent_state[56], parent_state[59],
            parent_state[63], parent_state[64],

            # Front
            parent_state[81], parent_state[82],
            parent_state[86], parent_state[89],
            parent_state[92], parent_state[95],
            parent_state[99], parent_state[100],

            # Right
            parent_state[117], parent_state[118],
            parent_state[122], parent_state[125],
            parent_state[128], parent_state[131],
            parent_state[135], parent_state[136],

            # Back
            parent_state[153], parent_state[154],
            parent_state[158], parent_state[161],
            parent_state[164], parent_state[167],
            parent_state[171], parent_state[172],

            # Down
            parent_state[189], parent_state[190],
            parent_state[194], parent_state[197],
            parent_state[200], parent_state[203],
            parent_state[207], parent_state[208],
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable666LRInnerXCenters(LookupTable):
    """
    lookup-table-6x6x6-step30-LR-inner-x-centers-stage.txt
    ======================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
    3 steps has 234 entries (1 percent, 8.07x previous step)
    4 steps has 1,246 entries (9 percent, 5.32x previous step)
    5 steps has 4,466 entries (34 percent, 3.58x previous step)
    6 steps has 6,236 entries (48 percent, 1.40x previous step)
    7 steps has 656 entries (5 percent, 0.11x previous step)

    Total: 12,870 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step30-LR-inner-x-centers-stage.txt',
            '0660000006600000',
            linecount=12870)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', 'x', 'x', 'x',
            'x', parent_state[51], parent_state[52], 'x',
            'x', parent_state[57], parent_state[58], 'x',
            'x', 'x', 'x', 'x',

            # Front
            'x', 'x', 'x', 'x',
            'x', parent_state[87], parent_state[88], 'x',
            'x', parent_state[93], parent_state[94], 'x',
            'x', 'x', 'x', 'x',

            # Right
            'x', 'x', 'x', 'x',
            'x', parent_state[123], parent_state[124], 'x',
            'x', parent_state[129], parent_state[130], 'x',
            'x', 'x', 'x', 'x',

            # Back
            'x', 'x', 'x', 'x',
            'x', parent_state[159], parent_state[160], 'x',
            'x', parent_state[165], parent_state[166], 'x',
            'x', 'x', 'x', 'x',
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable666LRObliqueEdgePairingLeftOnly(LookupTable):
    """
    lookup-table-6x6x6-step41-LR-oblique-pairing-left-only.txt
    ==========================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
    3 steps has 238 entries (1 percent, 8.21x previous step)
    4 steps has 742 entries (5 percent, 3.12x previous step)
    5 steps has 1,836 entries (14 percent, 2.47x previous step)
    6 steps has 4,405 entries (34 percent, 2.40x previous step)
    7 steps has 3,774 entries (29 percent, 0.86x previous step)
    8 steps has 1,721 entries (13 percent, 0.46x previous step)
    9 steps has 122 entries (0 percent, 0.07x previous step)

    Total: 12,870 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step41-LR-oblique-pairing-left-only.txt',
            '4182000041820000',
            linecount=12870)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', parent_state[45], 'x', 'x',
            'x', 'x', 'x', parent_state[53],
            parent_state[56], 'x', 'x', 'x',
            'x', 'x', parent_state[64], 'x',

            # Front
            'x', parent_state[81], 'x', 'x',
            'x', 'x', 'x', parent_state[89],
            parent_state[92], 'x', 'x', 'x',
            'x', 'x', parent_state[100], 'x',

            # Right
            'x', parent_state[117], 'x', 'x',
            'x', 'x', 'x', parent_state[125],
            parent_state[128], 'x', 'x', 'x',
            'x', 'x', parent_state[136], 'x',

            # Back
            'x', parent_state[153], 'x', 'x',
            'x', 'x', 'x', parent_state[161],
            parent_state[164], 'x', 'x', 'x',
            'x', 'x', parent_state[172], 'x',
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable666LRObliqueEdgePairingRightOnly(LookupTable):
    """
    lookup-table-6x6x6-step42-LR-oblique-pairing-right-only.txt
    ===========================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
    3 steps has 238 entries (1 percent, 8.21x previous step)
    4 steps has 742 entries (5 percent, 3.12x previous step)
    5 steps has 1,836 entries (14 percent, 2.47x previous step)
    6 steps has 4,405 entries (34 percent, 2.40x previous step)
    7 steps has 3,774 entries (29 percent, 0.86x previous step)
    8 steps has 1,721 entries (13 percent, 0.46x previous step)
    9 steps has 122 entries (0 percent, 0.07x previous step)

    Total: 12,870 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step42-LR-oblique-pairing-right-only.txt',
            '2814000028140000',
            linecount=12870)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', 'x', parent_state[46], 'x',
             parent_state[50], 'x', 'x', 'x',
            'x', 'x', 'x', parent_state[59],
            'x', parent_state[63], 'x', 'x',

            # Front
            'x', 'x', parent_state[82], 'x',
            parent_state[86], 'x', 'x', 'x',
            'x', 'x', 'x', parent_state[95],
            'x', parent_state[99], 'x', 'x',

            # Right
            'x', 'x', parent_state[118], 'x',
            parent_state[122], 'x', 'x', 'x',
            'x', 'x', 'x', parent_state[131],
            'x', parent_state[135], 'x', 'x',

            # Back
            'x', 'x', parent_state[154], 'x',
            parent_state[158], 'x', 'x', 'x',
            'x', 'x', 'x', parent_state[167],
            'x', parent_state[171], 'x', 'x',
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA666LRObliqueEdgePairing(LookupTableIDA):
    """
    lookup-table-6x6x6-step40-LR-oblique-pairing.txt
    ================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
    3 steps has 286 entries (0 percent, 9.86x previous step)
    4 steps has 2052 entries (0 percent, 7.17x previous step)
    5 steps has 16348 entries (1 percent, 7.97x previous step)
    6 steps has 127859 entries (12 percent, 7.82x previous step)
    7 steps has 844248 entries (85 percent, 6.60x previous step)

    Total: 990825 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step40-LR-oblique-pairing.txt',
            '6996000069960000',
            moves_6x6x6,

            # These would break up the staged UD inner x-centers
            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", # do not mess up UD x-centers
             "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'",         # do not mess up UD oblique pairs
             "3Uw", "3Uw'", "3Dw", "3Dw'", "3Fw", "3Fw'", "3Bw", "3Bw'", # do not mess up LR x-centers
             "3Lw", "3Lw'", "3Lw2",        # can skip these for 6x6x6 cubes
             "3Dw", "3Dw'", "3Dw2",
             "3Bw", "3Bw'", "3Bw2"),

            # prune tables
            (parent.lt_LR_oblique_edge_pairing_left_only,
             parent.lt_LR_oblique_edge_pairing_right_only),
            linecount=990825)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', parent_state[45], parent_state[46], 'x',
            parent_state[50], 'x', 'x', parent_state[53],
            parent_state[56], 'x', 'x', parent_state[59],
            'x', parent_state[63], parent_state[64], 'x',

            # Front
            'x', parent_state[81], parent_state[82], 'x',
            parent_state[86], 'x', 'x', parent_state[89],
            parent_state[92], 'x', 'x', parent_state[95],
            'x', parent_state[99], parent_state[100], 'x',

            # Right
            'x', parent_state[117], parent_state[118], 'x',
            parent_state[122], 'x', 'x', parent_state[125],
            parent_state[128], 'x', 'x', parent_state[131],
            'x', parent_state[135], parent_state[136], 'x',

            # Back
            'x', parent_state[153], parent_state[154], 'x',
            parent_state[158], 'x', 'x', parent_state[161],
            parent_state[164], 'x', 'x', parent_state[167],
            'x', parent_state[171], parent_state[172], 'x',
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable666UDInnerXCenterAndObliqueEdges(LookupTable):
    """
    This will solve the UD inner x-centers and pair the UD oblique edges.

    lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt
    =======================================================================
    1 steps has 350 entries (0 percent, 0.00x previous step)
    2 steps has 1,358 entries (0 percent, 3.88x previous step)
    3 steps has 5,148 entries (1 percent, 3.79x previous step)
    4 steps has 21,684 entries (6 percent, 4.21x previous step)
    5 steps has 75,104 entries (21 percent, 3.46x previous step)
    6 steps has 134,420 entries (39 percent, 1.79x previous step)
    7 steps has 91,784 entries (26 percent, 0.68x previous step)
    8 steps has 13,152 entries (3 percent, 0.14x previous step)

    Total: 343,000 entries
    """

    # TODO this pairs and solves the UD oblique edges, we need to build
    # the 70 tables that let them go anywhere on sides U or D
    # These are building now
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt',
            ('xDDxDUUDDUUDxDDxxUUxUDDUUDDUxUUx',
             'xDDxDUUDDUUDxUUxxDDxUDDUUDDUxUUx',
             'xDDxDUUDDUUDxUUxxUUxDDDUDDDUxUUx',
             'xDDxDUUDDUUDxUUxxUUxUDDDUDDDxUUx',
             'xDDxDUUDDUUDxUUxxUUxUDDUUDDUxDDx',
             'xDDxDUUUDUUUxDDxxDDxUDDUUDDUxUUx',
             'xDDxDUUUDUUUxDDxxUUxDDDUDDDUxUUx',
             'xDDxDUUUDUUUxDDxxUUxUDDDUDDDxUUx',
             'xDDxDUUUDUUUxDDxxUUxUDDUUDDUxDDx',
             'xDDxDUUUDUUUxUUxxDDxDDDUDDDUxUUx',
             'xDDxDUUUDUUUxUUxxDDxUDDDUDDDxUUx',
             'xDDxDUUUDUUUxUUxxDDxUDDUUDDUxDDx',
             'xDDxDUUUDUUUxUUxxUUxDDDDDDDDxUUx',
             'xDDxDUUUDUUUxUUxxUUxDDDUDDDUxDDx',
             'xDDxDUUUDUUUxUUxxUUxUDDDUDDDxDDx',
             'xDDxUUUDUUUDxDDxxDDxUDDUUDDUxUUx',
             'xDDxUUUDUUUDxDDxxUUxDDDUDDDUxUUx',
             'xDDxUUUDUUUDxDDxxUUxUDDDUDDDxUUx',
             'xDDxUUUDUUUDxDDxxUUxUDDUUDDUxDDx',
             'xDDxUUUDUUUDxUUxxDDxDDDUDDDUxUUx',
             'xDDxUUUDUUUDxUUxxDDxUDDDUDDDxUUx',
             'xDDxUUUDUUUDxUUxxDDxUDDUUDDUxDDx',
             'xDDxUUUDUUUDxUUxxUUxDDDDDDDDxUUx',
             'xDDxUUUDUUUDxUUxxUUxDDDUDDDUxDDx',
             'xDDxUUUDUUUDxUUxxUUxUDDDUDDDxDDx',
             'xDDxUUUUUUUUxDDxxDDxDDDUDDDUxUUx',
             'xDDxUUUUUUUUxDDxxDDxUDDDUDDDxUUx',
             'xDDxUUUUUUUUxDDxxDDxUDDUUDDUxDDx',
             'xDDxUUUUUUUUxDDxxUUxDDDDDDDDxUUx',
             'xDDxUUUUUUUUxDDxxUUxDDDUDDDUxDDx',
             'xDDxUUUUUUUUxDDxxUUxUDDDUDDDxDDx',
             'xDDxUUUUUUUUxUUxxDDxDDDDDDDDxUUx',
             'xDDxUUUUUUUUxUUxxDDxDDDUDDDUxDDx',
             'xDDxUUUUUUUUxUUxxDDxUDDDUDDDxDDx',
             'xDDxUUUUUUUUxUUxxUUxDDDDDDDDxDDx',
             'xUUxDUUDDUUDxDDxxDDxUDDUUDDUxUUx',
             'xUUxDUUDDUUDxDDxxUUxDDDUDDDUxUUx',
             'xUUxDUUDDUUDxDDxxUUxUDDDUDDDxUUx',
             'xUUxDUUDDUUDxDDxxUUxUDDUUDDUxDDx',
             'xUUxDUUDDUUDxUUxxDDxDDDUDDDUxUUx',
             'xUUxDUUDDUUDxUUxxDDxUDDDUDDDxUUx',
             'xUUxDUUDDUUDxUUxxDDxUDDUUDDUxDDx',
             'xUUxDUUDDUUDxUUxxUUxDDDDDDDDxUUx',
             'xUUxDUUDDUUDxUUxxUUxDDDUDDDUxDDx',
             'xUUxDUUDDUUDxUUxxUUxUDDDUDDDxDDx',
             'xUUxDUUUDUUUxDDxxDDxDDDUDDDUxUUx',
             'xUUxDUUUDUUUxDDxxDDxUDDDUDDDxUUx',
             'xUUxDUUUDUUUxDDxxDDxUDDUUDDUxDDx',
             'xUUxDUUUDUUUxDDxxUUxDDDDDDDDxUUx',
             'xUUxDUUUDUUUxDDxxUUxDDDUDDDUxDDx',
             'xUUxDUUUDUUUxDDxxUUxUDDDUDDDxDDx',
             'xUUxDUUUDUUUxUUxxDDxDDDDDDDDxUUx',
             'xUUxDUUUDUUUxUUxxDDxDDDUDDDUxDDx',
             'xUUxDUUUDUUUxUUxxDDxUDDDUDDDxDDx',
             'xUUxDUUUDUUUxUUxxUUxDDDDDDDDxDDx',
             'xUUxUUUDUUUDxDDxxDDxDDDUDDDUxUUx',
             'xUUxUUUDUUUDxDDxxDDxUDDDUDDDxUUx',
             'xUUxUUUDUUUDxDDxxDDxUDDUUDDUxDDx',
             'xUUxUUUDUUUDxDDxxUUxDDDDDDDDxUUx',
             'xUUxUUUDUUUDxDDxxUUxDDDUDDDUxDDx',
             'xUUxUUUDUUUDxDDxxUUxUDDDUDDDxDDx',
             'xUUxUUUDUUUDxUUxxDDxDDDDDDDDxUUx',
             'xUUxUUUDUUUDxUUxxDDxDDDUDDDUxDDx',
             'xUUxUUUDUUUDxUUxxDDxUDDDUDDDxDDx',
             'xUUxUUUDUUUDxUUxxUUxDDDDDDDDxDDx',
             'xUUxUUUUUUUUxDDxxDDxDDDDDDDDxUUx',
             'xUUxUUUUUUUUxDDxxDDxDDDUDDDUxDDx',
             'xUUxUUUUUUUUxDDxxDDxUDDDUDDDxDDx',
             'xUUxUUUUUUUUxDDxxUUxDDDDDDDDxDDx',
             'xUUxUUUUUUUUxUUxxDDxDDDDDDDDxDDx'),
            linecount=343000)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            'x', parent_state[9], parent_state[10], 'x',
            parent_state[14], parent_state[15], parent_state[16], parent_state[17],
            parent_state[20], parent_state[21], parent_state[22], parent_state[23],
            'x', parent_state[27], parent_state[28], 'x',

            # Down
            'x', parent_state[189], parent_state[190], 'x',
            parent_state[194], parent_state[195], parent_state[196], parent_state[197],
            parent_state[200], parent_state[201], parent_state[202], parent_state[203],
            'x', parent_state[207], parent_state[208], 'x'
        ]

        result = ''.join(result)
        return result


class LookupTable666LRInnerXCenterAndObliqueEdges(LookupTable):
    """
    lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt
    ========================================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 40 entries (0 percent, 8.00x previous step)
    3 steps has 228 entries (0 percent, 5.70x previous step)
    4 steps has 1,142 entries (0 percent, 5.01x previous step)
    5 steps has 5,240 entries (0 percent, 4.59x previous step)
    6 steps has 20,914 entries (0 percent, 3.99x previous step)
    7 steps has 78,886 entries (0 percent, 3.77x previous step)
    8 steps has 272,733 entries (1 percent, 3.46x previous step)
    9 steps has 844,382 entries (3 percent, 3.10x previous step)
    10 steps has 2,204,738 entries (9 percent, 2.61x previous step)
    11 steps has 4,507,592 entries (18 percent, 2.04x previous step)
    12 steps has 6,560,576 entries (27 percent, 1.46x previous step)
    13 steps has 6,029,508 entries (25 percent, 0.92x previous step)
    14 steps has 2,918,224 entries (12 percent, 0.48x previous step)
    15 steps has 545,008 entries (2 percent, 0.19x previous step)
    16 steps has 20,784 entries (0 percent, 0.04x previous step)
    17 steps has 34 entries (0 percent, 0.00x previous step)

    Total: 24,010,034 entries
    """

    # TODO we would have to build 70 of these and merge them...that might take a week or two
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt',
            'xLLxLLLLLLLLxLLxxxxxxFFxxFFxxxxxxRRxRRRRRRRRxRRxxxxxxBBxxBBxxxxx',
            linecount=24010034)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', parent_state[45], parent_state[46], 'x',
            parent_state[50], parent_state[51], parent_state[52], parent_state[53],
            parent_state[56], parent_state[57], parent_state[58], parent_state[59],
            'x', parent_state[63], parent_state[64], 'x',

            # Front
            'xxxx',
            'x', parent_state[87], parent_state[88], 'x',
            'x', parent_state[93], parent_state[94], 'x',
            'xxxx',

            # Right
            'x', parent_state[117], parent_state[118], 'x',
            parent_state[122], parent_state[123], parent_state[124], parent_state[125],
            parent_state[128], parent_state[129], parent_state[130], parent_state[131],
            'x', parent_state[135], parent_state[136], 'x',

            # Back
            'xxxx',
            'x', parent_state[159], parent_state[160], 'x',
            'x', parent_state[165], parent_state[166], 'x',
            'xxxx'
        ]

        result = ''.join(result)
        return result


class LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(LookupTableIDA):
    """
    lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt
    ==========================================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 54 entries (0 percent, 10.80x previous step)
    3 steps has 420 entries (0 percent, 7.78x previous step)
    4 steps has 2,703 entries (0 percent, 6.44x previous step)
    5 steps has 18,740 entries (0 percent, 6.93x previous step)
    6 steps has 118,707 entries (0 percent, 6.33x previous step)
    7 steps has 707,156 entries (2 percent, 5.96x previous step)
    8 steps has 3,945,650 entries (15 percent, 5.58x previous step)
    9 steps has 20,886,476 entries (81 percent, 5.29x previous step)

    Total: 25,679,911 entries
    """

    # TODO this pairs and solves the LR and FB oblique edges, we need to build
    # the 4900 tables that let them go anywhere on sides U or D
    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt',
            'xLLxLLLLLLLLxLLxxFFxFFFFFFFFxFFxxRRxRRRRRRRRxRRxxBBxBBBBBBBBxBBx',
            moves_6x6x6,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
             "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
             "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2"),                              # do not mess up solved UD

            # prune tables
            (parent.lt_LR_solve_inner_x_centers_and_oblique_edges,),
            linecount=25679911)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', parent_state[45], parent_state[46], 'x',
            parent_state[50], parent_state[51], parent_state[52], parent_state[53],
            parent_state[56], parent_state[57], parent_state[58], parent_state[59],
            'x', parent_state[63], parent_state[64], 'x',

            # Front
            'x', parent_state[81], parent_state[82], 'x',
            parent_state[86], parent_state[87], parent_state[88], parent_state[89],
            parent_state[92], parent_state[93], parent_state[94], parent_state[95],
            'x', parent_state[99], parent_state[100], 'x',

            # Right
            'x', parent_state[117], parent_state[118], 'x',
            parent_state[122], parent_state[123], parent_state[124], parent_state[125],
            parent_state[128], parent_state[129], parent_state[130], parent_state[131],
            'x', parent_state[135], parent_state[136], 'x',

            # Back
            'x', parent_state[153], parent_state[154], 'x',
            parent_state[158], parent_state[159], parent_state[160], parent_state[161],
            parent_state[164], parent_state[165], parent_state[166], parent_state[167],
            'x', parent_state[171], parent_state[172], 'x'
        ]

        result = ''.join(result)
        return result


class RubiksCube666(RubiksCubeNNNEvenEdges):
    """
    6x6x6 strategy
    - stage UD centers to sides U or D (use IDA)
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3

    Inheritance model
    -----------------
            RubiksCube
                |
        RubiksCubeNNNEvenEdges
           /            \
    RubiksCubeNNNEven RubiksCube666
    """

    def sanity_check(self):
        edge_orbit_0 = (2, 5, 12, 30, 35, 32, 25, 7,
                        38, 41, 48, 66, 71, 68, 61, 43,
                        74, 77, 84, 102, 107, 104, 97, 79,
                        110, 113, 120, 138, 143, 140, 133, 115,
                        146, 149, 156, 174, 179, 176, 169, 151,
                        182, 185, 192, 210, 215, 212, 205, 187)

        edge_orbit_1 = (3, 4, 18, 24, 34, 33, 19, 13,
                        39, 40, 54, 60, 70, 69, 55, 49,
                        75, 76, 90, 96, 106, 105, 91, 85,
                        111, 112, 126, 132, 142, 141, 127, 121,
                        147, 148, 162, 168, 178, 177, 163, 157,
                        183, 184, 198, 204, 214, 213, 199, 193)

        corners = (1, 6, 31, 36,
                   37, 42, 67, 72,
                   73, 78, 103, 108,
                   109, 114, 139, 144,
                   145, 150, 175, 180,
                   181, 186, 211, 216)

        left_oblique_edge = (9, 17, 28, 20,
                             45, 53, 64, 56,
                             81, 89, 100, 92,
                             117, 125, 136, 128,
                             153, 161, 172, 164,
                             189, 197, 208, 200)

        right_oblique_edge = (10, 23, 27, 14,
                              46, 59, 63, 50,
                              82, 95, 99, 86,
                              118, 131, 135, 122,
                              154, 167, 171, 158,
                              190, 203, 207, 194)

        outside_x_centers = (8, 11, 26, 29,
                             44, 47, 62, 65,
                             80, 83, 98, 101,
                             116, 119, 134, 137,
                             152, 155, 170, 173,
                             188, 191, 206, 209)

        inside_x_centers = (15, 16, 21, 22,
                            51, 52, 57, 58,
                            87, 88, 93, 94,
                            123, 124, 129, 130,
                            159, 160, 165, 166,
                            195, 196, 201, 202)

        self._sanity_check('edge-orbit-0', edge_orbit_0, 8)
        self._sanity_check('edge-orbit-1', edge_orbit_1, 8)
        self._sanity_check('corners', corners, 4)
        self._sanity_check('left-oblique', left_oblique_edge, 4)
        self._sanity_check('right-oblique', right_oblique_edge, 4)
        self._sanity_check('outside x-center', outside_x_centers, 4)
        self._sanity_check('inside x-center', inside_x_centers, 4)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_UD_inner_x_centers_stage = LookupTable666UDInnerXCenterStage(self)

        self.lt_UD_oblique_edge_pairing_left_only = LookupTable666UDObliqueEdgePairingLeftOnly(self)
        self.lt_UD_oblique_edge_pairing_right_only = LookupTable666UDObliqueEdgePairingRightOnly(self)
        self.lt_UD_oblique_edge_pairing = LookupTableIDA666UDObliqueEdgePairing(self)

        self.lt_LR_inner_x_centers = LookupTable666LRInnerXCenters(self)

        self.lt_LR_oblique_edge_pairing_left_only = LookupTable666LRObliqueEdgePairingLeftOnly(self)
        self.lt_LR_oblique_edge_pairing_right_only = LookupTable666LRObliqueEdgePairingRightOnly(self)
        self.lt_LR_oblique_edge_pairing = LookupTableIDA666LRObliqueEdgePairing(self)

        self.lt_UD_solve_inner_x_centers_and_oblique_edges = LookupTable666UDInnerXCenterAndObliqueEdges(self)
        self.lt_LR_solve_inner_x_centers_and_oblique_edges = LookupTable666LRInnerXCenterAndObliqueEdges(self)
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges = LookupTableIDA666LFRBInnerXCenterAndObliqueEdges(self)

    def populate_fake_555_for_ULFRBD(self, fake_555):

        for x in range(1, 151):
            fake_555.state[x] = 'x'

        # Upper
        fake_555.state[7] = self.state[8]
        fake_555.state[8] = self.state[9]
        fake_555.state[9] = self.state[11]
        fake_555.state[12] = self.state[14]
        fake_555.state[13] = self.state[15]
        fake_555.state[14] = self.state[17]
        fake_555.state[17] = self.state[26]
        fake_555.state[18] = self.state[27]
        fake_555.state[19] = self.state[29]

        # Left
        fake_555.state[32] = self.state[44]
        fake_555.state[33] = self.state[45]
        fake_555.state[34] = self.state[47]
        fake_555.state[37] = self.state[50]
        fake_555.state[38] = self.state[51]
        fake_555.state[39] = self.state[53]
        fake_555.state[42] = self.state[62]
        fake_555.state[43] = self.state[63]
        fake_555.state[44] = self.state[65]

        # Front
        fake_555.state[57] = self.state[80]
        fake_555.state[58] = self.state[81]
        fake_555.state[59] = self.state[83]
        fake_555.state[62] = self.state[86]
        fake_555.state[63] = self.state[87]
        fake_555.state[64] = self.state[89]
        fake_555.state[67] = self.state[98]
        fake_555.state[68] = self.state[99]
        fake_555.state[69] = self.state[101]

        # Right
        fake_555.state[82] = self.state[116]
        fake_555.state[83] = self.state[117]
        fake_555.state[84] = self.state[119]
        fake_555.state[87] = self.state[122]
        fake_555.state[88] = self.state[123]
        fake_555.state[89] = self.state[125]
        fake_555.state[92] = self.state[134]
        fake_555.state[93] = self.state[135]
        fake_555.state[94] = self.state[137]

        # Back
        fake_555.state[107] = self.state[152]
        fake_555.state[108] = self.state[153]
        fake_555.state[109] = self.state[155]
        fake_555.state[112] = self.state[158]
        fake_555.state[113] = self.state[159]
        fake_555.state[114] = self.state[161]
        fake_555.state[117] = self.state[170]
        fake_555.state[118] = self.state[171]
        fake_555.state[119] = self.state[173]

        # Down
        fake_555.state[132] = self.state[188]
        fake_555.state[133] = self.state[189]
        fake_555.state[134] = self.state[191]
        fake_555.state[137] = self.state[194]
        fake_555.state[138] = self.state[195]
        fake_555.state[139] = self.state[197]
        fake_555.state[142] = self.state[206]
        fake_555.state[143] = self.state[207]
        fake_555.state[144] = self.state[209]
        fake_555.sanity_check()

    def fake_move_UD_to_UFDB(self):

        # How many UD squares are on sides LR? We need to "fake move" those to somewhere on FB for our lookup table to work.
        left_fake_move_count = 0
        right_fake_move_count = 0

        for square_index in (45, 53, 64, 56, 117, 125, 136, 128):
            if self.state[square_index] in ('U', 'D'):
                self.state[square_index] = 'L'
                left_fake_move_count += 1

        for square_index in (46, 59, 63, 50, 118, 131, 135, 122):
            if self.state[square_index] in ('U', 'D'):
                self.state[square_index] = 'L'
                right_fake_move_count += 1

        if left_fake_move_count > 0:
            for square_index in (9, 17, 28, 20, 189, 197, 208, 200, 81, 89, 100, 92, 153, 161, 172, 164):
                if self.state[square_index] not in ('U', 'D'):
                    self.state[square_index] = 'U'
                    left_fake_move_count -= 1

                    if not left_fake_move_count:
                        break

        if right_fake_move_count > 0:
            for square_index in (10, 23, 27, 14, 190, 203, 207, 194, 82, 95, 99, 86, 154, 167, 171, 158):
                if self.state[square_index] not in ('U', 'D'):
                    self.state[square_index] = 'U'
                    right_fake_move_count -= 1

                    if not right_fake_move_count:
                        break

    def group_centers_stage_UD(self):
        self.lt_UD_inner_x_centers_stage.solve()
        log.info("UD inner x-centers staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

        # Test the prune tables
        #self.lt_UD_oblique_edge_pairing_left_only.solve()
        #self.lt_UD_oblique_edge_pairing_right_only.solve()
        #self.print_cube()
        #sys.exit(0)

        self.lt_UD_oblique_edge_pairing.solve()
        log.info("UD oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        log.info("")

    def group_centers_guts(self, oblique_edges_only=False):
        self.lt_init()

        self.group_centers_stage_UD()

        # Stage LR which in turn stages FB
        log.info("LR inner x-centers staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Test the prune tables
        #self.lt_LR_oblique_edge_pairing_left_only.solve()
        #self.lt_LR_oblique_edge_pairing_right_only.solve()
        #self.print_cube()
        #sys.exit(0)

        self.lt_LR_oblique_edge_pairing.solve()
        log.info("LR oblique edges staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        # At this point all of the inner x-centers and oblique edges are staged

        # Could we simply stage all 6x6x6 sides and solve the centers?
        # At this point inside x-centers and outside t-centers are staged.
        # We would need to reduce the centers to 5x5x5 to stage outside
        # x-centers.
        #
        # At that point all sides would be staged and there would be 4 groups
        # of 8!/(4!*4!) per side so to solve ULF (which would also solve RBD)
        # would be (8!/(4!*4!))^12 or 13,841,287,201,000,000,000,000
        #
        # Needless to say this is not feasible :(
        #
        # I brainstorm about this because for one of my 6x6x6 test cubes it takes
        # us 42 steps to get to here and 109 steps to solve the centers....that
        # is a lot of steps.

        # Could we simply stage all 6x6x6 sides and solve the centers?
        # At this point inside x-centers and outside t-centers are staged.
        # We would need to reduce the centers to 5x5x5 to stage outside
        # x-centers.
        #
        # At that point all sides would be staged and there would be 4 groups
        # of 8!/(4!*4!) per side so to solve ULF (which would also solve RBD)
        # would be (8!/(4!*4!))^12 or 13,841,287,201,000,000,000,000
        #
        # Needless to say this is not feasible :(
        #
        # I brainstorm about this because for one of my 6x6x6 test cubes it takes
        # us 42 steps to get to here and 109 steps to solve the centers....that
        # is a lot of steps.

        # Reduce the centers to 5x5x5 centers
        # - solve the UD inner x-centers and pair the UD oblique edges
        # - solve the LR inner x-centers and pair the LR oblique edges
        # - solve the FB inner x-centers and pair the FB oblique edges
        self.lt_UD_solve_inner_x_centers_and_oblique_edges.solve()
        log.info("UD inner x-center solved and oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # dwalton
        log.info("kociemba: %s" % self.get_kociemba_string(True))
        sys.exit(0)

        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.solve()
        log.info("LFRB inner x-center and oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        if oblique_edges_only:
            log.info("Took %d steps to resolve oblique edges" % self.get_solution_len_minus_rotates(self.solution))
            return

        # At this point the 6x6x6 centers have been reduced to 5x5x5 centers
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.cpu_mode = self.cpu_mode
        fake_555.lt_init()
        self.populate_fake_555_for_ULFRBD(fake_555)
        fake_555.group_centers_guts()

        for step in fake_555.solution:
            self.rotate(step)

        log.info("Took %d steps to solve centers" % self.get_solution_len_minus_rotates(self.solution))
        sys.exit(0)

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
