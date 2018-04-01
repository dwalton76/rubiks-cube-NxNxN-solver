
from rubikscubennnsolver.RubiksCubeNNNOddEdges import RubiksCubeNNNOddEdges
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_5x5x5
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_6x6x6, moves_6x6x6
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA
import logging
import sys

log = logging.getLogger(__name__)

moves_7x7x7 = moves_6x6x6
solved_7x7x7 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

step80_centers_777 = (
    # Left
    59, 60, 61,
    65, 66, 67, 68, 69,
    72, 73, 74, 75, 76,
    79, 80, 81, 82, 83,
    87, 88, 89,

    # Front
    108, 109, 110,
    114, 115, 116, 117, 118,
    121, 122, 123, 124, 125,
    128, 129, 130, 131, 132,
    136, 137, 138,

    # Right
    157, 158, 159,
    163, 164, 165, 166, 167,
    170, 171, 172, 173, 174,
    177, 178, 179, 180, 181,
    185, 186, 187,

    # Back
    206, 207, 208,
    212, 213, 214, 215, 216,
    219, 220, 221, 222, 223,
    226, 227, 228, 229, 230,
    234, 235, 236,
)


class LookupTable777UDObliqueEdgePairingMiddleOnly(LookupTable):
    """
    24!/(8!*16!) is 735,471

    lookup-table-7x7x7-step11-UD-oblique-edge-pairing-middle-only.txt
    =================================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 66 entries (0 percent, 13.20x previous step)
    3 steps has 850 entries (0 percent, 12.88x previous step)
    4 steps has 8,753 entries (1 percent, 10.30x previous step)
    5 steps has 67,758 entries (9 percent, 7.74x previous step)
    6 steps has 243,959 entries (33 percent, 3.60x previous step)
    7 steps has 257,410 entries (34 percent, 1.06x previous step)
    8 steps has 135,684 entries (18 percent, 0.53x previous step)
    9 steps has 20,177 entries (2 percent, 0.15x previous step)
    10 steps has 801 entries (0 percent, 0.04x previous step)
    11 steps has 8 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step11-UD-oblique-edge-pairing-middle-only.txt',
            '462000000000000462',
            linecount=735471,
            max_depth=11)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            'x', parent_state[11], 'x',
            'x', 'x',
            parent_state[23], parent_state[27],
            'x', 'x',
            'x', parent_state[39], 'x',

            # Left
            'x', parent_state[60], 'x',
            'x', 'x',
            parent_state[72], parent_state[76],
            'x', 'x',
            'x', parent_state[88], 'x',

            # Front
            'x', parent_state[109], 'x',
            'x', 'x',
            parent_state[121], parent_state[125],
            'x', 'x',
            'x', parent_state[137], 'x',

            # Right
            'x', parent_state[158], 'x',
            'x', 'x',
            parent_state[170], parent_state[174],
            'x', 'x',
            'x', parent_state[186], 'x',

            # Back
            'x', parent_state[207], 'x',
            'x', 'x',
            parent_state[219], parent_state[223],
            'x', 'x',
            'x', parent_state[235], 'x',

            # Down
            'x', parent_state[256], 'x',
            'x', 'x',
            parent_state[268], parent_state[272],
            'x', 'x',
            'x', parent_state[284], 'x'
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable777UDObliqueEdgePairingLeftOnly(LookupTable):
    """
    24!/(8!*16!) is 735,471

    lookup-table-7x7x7-step12-UD-oblique-edge-pairing-left-only.txt
    ===============================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 66 entries (0 percent, 13.20x previous step)
    3 steps has 850 entries (0 percent, 12.88x previous step)
    4 steps has 8,753 entries (1 percent, 10.30x previous step)
    5 steps has 67,758 entries (9 percent, 7.74x previous step)
    6 steps has 243,959 entries (33 percent, 3.60x previous step)
    7 steps has 257,410 entries (34 percent, 1.06x previous step)
    8 steps has 135,684 entries (18 percent, 0.53x previous step)
    9 steps has 20,177 entries (2 percent, 0.15x previous step)
    10 steps has 801 entries (0 percent, 0.04x previous step)
    11 steps has 8 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step12-UD-oblique-edge-pairing-left-only.txt',
            '891000000000000891',
            linecount=735471,
            max_depth=11)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            parent_state[10], 'x', 'x',
            'x', parent_state[20],
            'x', 'x',
            parent_state[30], 'x',
            'x', 'x', parent_state[40],

            # Left
            parent_state[59], 'x', 'x',
            'x', parent_state[69],
            'x', 'x',
            parent_state[79], 'x',
            'x', 'x', parent_state[89],

            # Front
            parent_state[108], 'x', 'x',
            'x', parent_state[118],
            'x', 'x',
            parent_state[128], 'x',
            'x', 'x', parent_state[138],

            # Right
            parent_state[157], 'x', 'x',
            'x', parent_state[167],
            'x', 'x',
            parent_state[177], 'x',
            'x', 'x', parent_state[187],

            # Back
            parent_state[206], 'x', 'x',
            'x', parent_state[216],
            'x', 'x',
            parent_state[226], 'x',
            'x', 'x', parent_state[236],

            # Down
            parent_state[255], 'x', 'x',
            'x', parent_state[265],
            'x', 'x',
            parent_state[275], 'x',
            'x', 'x', parent_state[285]
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable777UDObliqueEdgePairingRightOnly(LookupTable):
    """
    24!/(8!*16!) is 735,471

    lookup-table-7x7x7-step13-UD-oblique-edge-pairing-right-only.txt
    =================================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 66 entries (0 percent, 13.20x previous step)
    3 steps has 850 entries (0 percent, 12.88x previous step)
    4 steps has 8,753 entries (1 percent, 10.30x previous step)
    5 steps has 67,758 entries (9 percent, 7.74x previous step)
    6 steps has 243,959 entries (33 percent, 3.60x previous step)
    7 steps has 257,410 entries (34 percent, 1.06x previous step)
    8 steps has 135,684 entries (18 percent, 0.53x previous step)
    9 steps has 20,177 entries (2 percent, 0.15x previous step)
    10 steps has 801 entries (0 percent, 0.04x previous step)
    11 steps has 8 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step13-UD-oblique-edge-pairing-right-only.txt',
            '30c00000000000030c',
            linecount=735471,
            max_depth=11)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            'x', 'x', parent_state[12],
            parent_state[16], 'x',
            'x', 'x',
            'x', parent_state[34],
            parent_state[38], 'x', 'x',

            # Left
            'x', 'x', parent_state[61],
            parent_state[65], 'x',
            'x', 'x',
            'x', parent_state[83],
            parent_state[87], 'x', 'x',

            # Front
            'x', 'x', parent_state[110],
            parent_state[114], 'x',
            'x', 'x',
            'x', parent_state[132],
            parent_state[136], 'x', 'x',

            # Right
            'x', 'x', parent_state[159],
            parent_state[163], 'x',
            'x', 'x',
            'x', parent_state[181],
            parent_state[185], 'x', 'x',

            # Back
            'x', 'x', parent_state[208],
            parent_state[212], 'x',
            'x', 'x',
            'x', parent_state[230],
            parent_state[234], 'x', 'x',

            # Down
            'x', 'x', parent_state[257],
            parent_state[261], 'x',
            'x', 'x',
            'x', parent_state[279],
            parent_state[283], 'x', 'x',
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA777UDObliqueEdgePairing(LookupTableIDA):
    """
    6-deep

    lookup-table-7x7x7-step10-UD-oblique-edge-pairing.txt
    =====================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 66 entries (0 percent, 13.20x previous step)
    3 steps has 916 entries (0 percent, 13.88x previous step)
    4 steps has 10,132 entries (0 percent, 11.06x previous step)
    5 steps has 92,070 entries (1 percent, 9.09x previous step)
    6 steps has 558,938 entries (9 percent, 6.07x previous step)
    7 steps has 3,861,196 entries (64 percent, 6.91x previous step)
    8 steps has 1,366,153 entries (22 percent, 0.35x previous step)
    9 steps has 71,939 entries (1 percent, 0.05x previous step)
    10 steps has 158 entries (0 percent, 0.00x previous step)

    Total: 5,961,573 entries

    7-deep is 845M gzipped
    lookup-table-7x7x7-step10-UD-oblique-edge-pairing.txt
    =====================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 66 entries (0 percent, 13.20x previous step)
    3 steps has 916 entries (0 percent, 13.88x previous step)
    4 steps has 10,132 entries (0 percent, 11.06x previous step)
    5 steps has 92,070 entries (0 percent, 9.09x previous step)
    6 steps has 558,938 entries (0 percent, 6.07x previous step)
    7 steps has 4,163,342 entries (4 percent, 7.45x previous step)
    8 steps has 53,921,753 entries (56 percent, 12.95x previous step)
    9 steps has 33,108,789 entries (34 percent, 0.61x previous step)
    10 steps has 3,448,937 entries (3 percent, 0.10x previous step)
    11 steps has 49,979 entries (0 percent, 0.01x previous step)

    Total: 95,354,927 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step10-UD-oblique-edge-pairing.txt',
            'fff000000000000fff',
            moves_7x7x7,

            # do not mess up UD 5x5x5 centers
            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'"),

            # prune tables
            (parent.lt_UD_oblique_edge_pairing_middle_only,
             parent.lt_UD_oblique_edge_pairing_left_only,
             parent.lt_UD_oblique_edge_pairing_right_only),

            linecount=5961573,
            max_depth=6)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            parent_state[10], parent_state[11], parent_state[12],
            parent_state[16], parent_state[20],
            parent_state[23], parent_state[27],
            parent_state[30], parent_state[34],
            parent_state[38], parent_state[39], parent_state[40],

            # Left
            parent_state[59], parent_state[60], parent_state[61],
            parent_state[65], parent_state[69],
            parent_state[72], parent_state[76],
            parent_state[79], parent_state[83],
            parent_state[87], parent_state[88], parent_state[89],

            # Front
            parent_state[108], parent_state[109], parent_state[110],
            parent_state[114], parent_state[118],
            parent_state[121], parent_state[125],
            parent_state[128], parent_state[132],
            parent_state[136], parent_state[137], parent_state[138],

            # Right
            parent_state[157], parent_state[158], parent_state[159],
            parent_state[163], parent_state[167],
            parent_state[170], parent_state[174],
            parent_state[177], parent_state[181],
            parent_state[185], parent_state[186], parent_state[187],

            # Back
            parent_state[206], parent_state[207], parent_state[208],
            parent_state[212], parent_state[216],
            parent_state[219], parent_state[223],
            parent_state[226], parent_state[230],
            parent_state[234], parent_state[235], parent_state[236],

            # Down
            parent_state[255], parent_state[256], parent_state[257],
            parent_state[261], parent_state[265],
            parent_state[268], parent_state[272],
            parent_state[275], parent_state[279],
            parent_state[283], parent_state[284], parent_state[285],
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable777LRObliqueEdgePairingMiddleOnly(LookupTable):
    """
    lookup-table-7x7x7-step21-LR-oblique-edge-pairing-middle-only.txt
    =================================================================
    1 steps has 2 entries (0 percent, 0.00x previous step)
    2 steps has 26 entries (0 percent, 13.00x previous step)
    3 steps has 190 entries (1 percent, 7.31x previous step)
    4 steps has 612 entries (4 percent, 3.22x previous step)
    5 steps has 1,513 entries (11 percent, 2.47x previous step)
    6 steps has 3,370 entries (26 percent, 2.23x previous step)
    7 steps has 4,066 entries (31 percent, 1.21x previous step)
    8 steps has 2,258 entries (17 percent, 0.56x previous step)
    9 steps has 803 entries (6 percent, 0.36x previous step)
    10 steps has 30 entries (0 percent, 0.04x previous step)

    Total: 12,870 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step21-LR-oblique-edge-pairing-middle-only.txt',
            '462000462000',
            linecount=12870,
            max_depth=10)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', parent_state[60], 'x',
            'x', 'x',
            parent_state[72], parent_state[76],
            'x', 'x',
            'x', parent_state[88], 'x',

            # Front
            'x', parent_state[109], 'x',
            'x', 'x',
            parent_state[121], parent_state[125],
            'x', 'x',
            'x', parent_state[137], 'x',

            # Right
            'x', parent_state[158], 'x',
            'x', 'x',
            parent_state[170], parent_state[174],
            'x', 'x',
            'x', parent_state[186], 'x',

            # Back
            'x', parent_state[207], 'x',
            'x', 'x',
            parent_state[219], parent_state[223],
            'x', 'x',
            'x', parent_state[235], 'x'
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable777LRObliqueEdgePairingLeftOnly(LookupTable):
    """
    lookup-table-7x7x7-step22-LR-oblique-edge-pairing-left-only.txt
    ===============================================================
    1 steps has 2 entries (0 percent, 0.00x previous step)
    2 steps has 26 entries (0 percent, 13.00x previous step)
    3 steps has 210 entries (1 percent, 8.08x previous step)
    4 steps has 722 entries (5 percent, 3.44x previous step)
    5 steps has 1,752 entries (13 percent, 2.43x previous step)
    6 steps has 4,033 entries (31 percent, 2.30x previous step)
    7 steps has 4,014 entries (31 percent, 1.00x previous step)
    8 steps has 1,977 entries (15 percent, 0.49x previous step)
    9 steps has 134 entries (1 percent, 0.07x previous step)

    Total: 12,870 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step22-LR-oblique-edge-pairing-left-only.txt',
            '891000891000',
            linecount=12870,
            max_depth=9)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            parent_state[59], 'x', 'x',
            'x', parent_state[69],
            'x', 'x',
            parent_state[79], 'x',
            'x', 'x', parent_state[89],

            # Front
            parent_state[108], 'x', 'x',
            'x', parent_state[118],
            'x', 'x',
            parent_state[128], 'x',
            'x', 'x', parent_state[138],

            # Right
            parent_state[157], 'x', 'x',
            'x', parent_state[167],
            'x', 'x',
            parent_state[177], 'x',
            'x', 'x', parent_state[187],

            # Back
            parent_state[206], 'x', 'x',
            'x', parent_state[216],
            'x', 'x',
            parent_state[226], 'x',
            'x', 'x', parent_state[236]
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable777LRObliqueEdgePairingRightOnly(LookupTable):
    """
    lookup-table-7x7x7-step23-LR-oblique-edge-pairing-right-only.txt
    ================================================================
    1 steps has 2 entries (0 percent, 0.00x previous step)
    2 steps has 26 entries (0 percent, 13.00x previous step)
    3 steps has 210 entries (1 percent, 8.08x previous step)
    4 steps has 722 entries (5 percent, 3.44x previous step)
    5 steps has 1,752 entries (13 percent, 2.43x previous step)
    6 steps has 4,033 entries (31 percent, 2.30x previous step)
    7 steps has 4,014 entries (31 percent, 1.00x previous step)
    8 steps has 1,977 entries (15 percent, 0.49x previous step)
    9 steps has 134 entries (1 percent, 0.07x previous step)

    Total: 12,870 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step23-LR-oblique-edge-pairing-right-only.txt',
            '30c00030c000',
            linecount=12870,
            max_depth=9)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', 'x', parent_state[61],
            parent_state[65], 'x',
            'x', 'x',
            'x', parent_state[83],
            parent_state[87], 'x', 'x',

            # Front
            'x', 'x', parent_state[110],
            parent_state[114], 'x',
            'x', 'x',
            'x', parent_state[132],
            parent_state[136], 'x', 'x',

            # Right
            'x', 'x', parent_state[159],
            parent_state[163], 'x',
            'x', 'x',
            'x', parent_state[181],
            parent_state[185], 'x', 'x',

            # Back
            'x', 'x', parent_state[208],
            parent_state[212], 'x',
            'x', 'x',
            'x', parent_state[230],
            parent_state[234], 'x', 'x'
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA777LRObliqueEdgePairing(LookupTableIDA):
    """
    8-deep
    lookup-table-7x7x7-step20-LR-oblique-edge-pairing.txt
    =====================================================
    1 steps has 2 entries (0 percent, 0.00x previous step)
    2 steps has 26 entries (0 percent, 13.00x previous step)
    3 steps has 214 entries (0 percent, 8.23x previous step)
    4 steps has 806 entries (0 percent, 3.77x previous step)
    5 steps has 3,006 entries (0 percent, 3.73x previous step)
    6 steps has 15,990 entries (0 percent, 5.32x previous step)
    7 steps has 87,030 entries (1 percent, 5.44x previous step)
    8 steps has 455,114 entries (9 percent, 5.23x previous step)
    9 steps has 1,784,216 entries (35 percent, 3.92x previous step)
    10 steps has 2,208,423 entries (43 percent, 1.24x previous step)
    11 steps has 469,086 entries (9 percent, 0.21x previous step)
    12 steps has 20,267 entries (0 percent, 0.04x previous step)
    13 steps has 100 entries (0 percent, 0.00x previous step)

    Total: 5,044,280 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step20-LR-oblique-edge-pairing.txt',
            'fff000fff000',
            moves_7x7x7,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", # do not mess up UD 5x5x5 centers
             "Rw",  "Rw'",  "Lw",  "Lw'",  "Fw",  "Fw'",  "Bw",  "Bw'", # do not mess up UD oblique edges
             "3Uw", "3Uw'", "3Dw", "3Dw'"),

            # prune tables
            (parent.lt_LR_oblique_edge_pairing_middle_only,
             parent.lt_LR_oblique_edge_pairing_left_only,
             parent.lt_LR_oblique_edge_pairing_right_only),

            linecount=5044280,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            parent_state[59], parent_state[60], parent_state[61],
            parent_state[65], parent_state[69],
            parent_state[72], parent_state[76],
            parent_state[79], parent_state[83],
            parent_state[87], parent_state[88], parent_state[89],

            # Front
            parent_state[108], parent_state[109], parent_state[110],
            parent_state[114], parent_state[118],
            parent_state[121], parent_state[125],
            parent_state[128], parent_state[132],
            parent_state[136], parent_state[137], parent_state[138],

            # Right
            parent_state[157], parent_state[158], parent_state[159],
            parent_state[163], parent_state[167],
            parent_state[170], parent_state[174],
            parent_state[177], parent_state[181],
            parent_state[185], parent_state[186], parent_state[187],

            # Back
            parent_state[206], parent_state[207], parent_state[208],
            parent_state[212], parent_state[216],
            parent_state[219], parent_state[223],
            parent_state[226], parent_state[230],
            parent_state[234], parent_state[235], parent_state[236]
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable777UDSolveInnerCentersAndObliqueEdgesCenterOnly(LookupTable):
    """
    lookup-table-7x7x7-step51-UD-solve-inner-center-and-oblique-edges-center-only.txt
    =================================================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 22 entries (0 percent, 4.40x previous step)
    3 steps has 82 entries (1 percent, 3.73x previous step)
    4 steps has 292 entries (5 percent, 3.56x previous step)
    5 steps has 986 entries (20 percent, 3.38x previous step)
    6 steps has 2,001 entries (40 percent, 2.03x previous step)
    7 steps has 1,312 entries (26 percent, 0.66x previous step)
    8 steps has 200 entries (4 percent, 0.15x previous step)

    Total: 4,900 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step51-UD-solve-inner-center-and-oblique-edges-center-only.txt',
            'xxxxxxUUUxxUxUxxUUUxxxxxxxxxxxxDDDxxDxDxxDDDxxxxxx',
            linecount=4900,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            'xxxxx',
            'x', parent_state[17], parent_state[18], parent_state[19], 'x',
            'x', parent_state[24], 'x', parent_state[26], 'x',
            'x', parent_state[31], parent_state[32], parent_state[33], 'x',
            'xxxxx',

            # Down
            'xxxxx',
            'x', parent_state[262], parent_state[263], parent_state[264], 'x',
            'x', parent_state[269], 'x', parent_state[271], 'x',
            'x', parent_state[276], parent_state[277], parent_state[278], 'x',
            'xxxxx'
        ]

        result = ''.join(result)
        return result


class LookupTable777UDSolveInnerCentersAndObliqueEdgesEdgesOnly(LookupTable):
    """
    lookup-table-7x7x7-step52-UD-solve-inner-center-and-oblique-edges-edges-only.txt
    ================================================================================
    1 steps has 294 entries (0 percent, 0.00x previous step)
    2 steps has 1,392 entries (0 percent, 4.73x previous step)
    3 steps has 6,112 entries (1 percent, 4.39x previous step)
    4 steps has 23,304 entries (6 percent, 3.81x previous step)
    5 steps has 71,086 entries (20 percent, 3.05x previous step)
    6 steps has 137,528 entries (40 percent, 1.93x previous step)
    7 steps has 92,192 entries (26 percent, 0.67x previous step)
    8 steps has 11,068 entries (3 percent, 0.12x previous step)
    9 steps has 24 entries (0 percent, 0.00x previous step)

    Total: 343,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step52-UD-solve-inner-center-and-oblique-edges-edges-only.txt',
            ('xUUUxUxxxUUxxxUUxxxUxUUUxxDDDxDxxxDDxxxDDxxxDxDDDx',
             'xUUUxUxxxUUxxxUUxxxUxDDDxxUUUxDxxxDDxxxDDxxxDxDDDx',
             'xUUUxUxxxUUxxxUUxxxUxDDDxxDDDxUxxxDUxxxDUxxxDxDDDx',
             'xUUUxUxxxUUxxxUUxxxUxDDDxxDDDxDxxxUDxxxUDxxxUxDDDx',
             'xUUUxUxxxUUxxxUUxxxUxDDDxxDDDxDxxxDDxxxDDxxxDxUUUx',
             'xUUUxUxxxDUxxxDUxxxDxUUUxxUUUxDxxxDDxxxDDxxxDxDDDx',
             'xUUUxUxxxDUxxxDUxxxDxUUUxxDDDxUxxxDUxxxDUxxxDxDDDx',
             'xUUUxUxxxDUxxxDUxxxDxUUUxxDDDxDxxxUDxxxUDxxxUxDDDx',
             'xUUUxUxxxDUxxxDUxxxDxUUUxxDDDxDxxxDDxxxDDxxxDxUUUx',
             'xUUUxUxxxDUxxxDUxxxDxDDDxxUUUxUxxxDUxxxDUxxxDxDDDx',
             'xUUUxUxxxDUxxxDUxxxDxDDDxxUUUxDxxxUDxxxUDxxxUxDDDx',
             'xUUUxUxxxDUxxxDUxxxDxDDDxxUUUxDxxxDDxxxDDxxxDxUUUx',
             'xUUUxUxxxDUxxxDUxxxDxDDDxxDDDxUxxxUUxxxUUxxxUxDDDx',
             'xUUUxUxxxDUxxxDUxxxDxDDDxxDDDxUxxxDUxxxDUxxxDxUUUx',
             'xUUUxUxxxDUxxxDUxxxDxDDDxxDDDxDxxxUDxxxUDxxxUxUUUx',
             'xUUUxDxxxUDxxxUDxxxUxUUUxxUUUxDxxxDDxxxDDxxxDxDDDx',
             'xUUUxDxxxUDxxxUDxxxUxUUUxxDDDxUxxxDUxxxDUxxxDxDDDx',
             'xUUUxDxxxUDxxxUDxxxUxUUUxxDDDxDxxxUDxxxUDxxxUxDDDx',
             'xUUUxDxxxUDxxxUDxxxUxUUUxxDDDxDxxxDDxxxDDxxxDxUUUx',
             'xUUUxDxxxUDxxxUDxxxUxDDDxxUUUxUxxxDUxxxDUxxxDxDDDx',
             'xUUUxDxxxUDxxxUDxxxUxDDDxxUUUxDxxxUDxxxUDxxxUxDDDx',
             'xUUUxDxxxUDxxxUDxxxUxDDDxxUUUxDxxxDDxxxDDxxxDxUUUx',
             'xUUUxDxxxUDxxxUDxxxUxDDDxxDDDxUxxxUUxxxUUxxxUxDDDx',
             'xUUUxDxxxUDxxxUDxxxUxDDDxxDDDxUxxxDUxxxDUxxxDxUUUx',
             'xUUUxDxxxUDxxxUDxxxUxDDDxxDDDxDxxxUDxxxUDxxxUxUUUx',
             'xUUUxDxxxDDxxxDDxxxDxUUUxxUUUxUxxxDUxxxDUxxxDxDDDx',
             'xUUUxDxxxDDxxxDDxxxDxUUUxxUUUxDxxxUDxxxUDxxxUxDDDx',
             'xUUUxDxxxDDxxxDDxxxDxUUUxxUUUxDxxxDDxxxDDxxxDxUUUx',
             'xUUUxDxxxDDxxxDDxxxDxUUUxxDDDxUxxxUUxxxUUxxxUxDDDx',
             'xUUUxDxxxDDxxxDDxxxDxUUUxxDDDxUxxxDUxxxDUxxxDxUUUx',
             'xUUUxDxxxDDxxxDDxxxDxUUUxxDDDxDxxxUDxxxUDxxxUxUUUx',
             'xUUUxDxxxDDxxxDDxxxDxDDDxxUUUxUxxxUUxxxUUxxxUxDDDx',
             'xUUUxDxxxDDxxxDDxxxDxDDDxxUUUxUxxxDUxxxDUxxxDxUUUx',
             'xUUUxDxxxDDxxxDDxxxDxDDDxxUUUxDxxxUDxxxUDxxxUxUUUx',
             'xUUUxDxxxDDxxxDDxxxDxDDDxxDDDxUxxxUUxxxUUxxxUxUUUx',
             'xDDDxUxxxUUxxxUUxxxUxUUUxxUUUxDxxxDDxxxDDxxxDxDDDx',
             'xDDDxUxxxUUxxxUUxxxUxUUUxxDDDxUxxxDUxxxDUxxxDxDDDx',
             'xDDDxUxxxUUxxxUUxxxUxUUUxxDDDxDxxxUDxxxUDxxxUxDDDx',
             'xDDDxUxxxUUxxxUUxxxUxUUUxxDDDxDxxxDDxxxDDxxxDxUUUx',
             'xDDDxUxxxUUxxxUUxxxUxDDDxxUUUxUxxxDUxxxDUxxxDxDDDx',
             'xDDDxUxxxUUxxxUUxxxUxDDDxxUUUxDxxxUDxxxUDxxxUxDDDx',
             'xDDDxUxxxUUxxxUUxxxUxDDDxxUUUxDxxxDDxxxDDxxxDxUUUx',
             'xDDDxUxxxUUxxxUUxxxUxDDDxxDDDxUxxxUUxxxUUxxxUxDDDx',
             'xDDDxUxxxUUxxxUUxxxUxDDDxxDDDxUxxxDUxxxDUxxxDxUUUx',
             'xDDDxUxxxUUxxxUUxxxUxDDDxxDDDxDxxxUDxxxUDxxxUxUUUx',
             'xDDDxUxxxDUxxxDUxxxDxUUUxxUUUxUxxxDUxxxDUxxxDxDDDx',
             'xDDDxUxxxDUxxxDUxxxDxUUUxxUUUxDxxxUDxxxUDxxxUxDDDx',
             'xDDDxUxxxDUxxxDUxxxDxUUUxxUUUxDxxxDDxxxDDxxxDxUUUx',
             'xDDDxUxxxDUxxxDUxxxDxUUUxxDDDxUxxxUUxxxUUxxxUxDDDx',
             'xDDDxUxxxDUxxxDUxxxDxUUUxxDDDxUxxxDUxxxDUxxxDxUUUx',
             'xDDDxUxxxDUxxxDUxxxDxUUUxxDDDxDxxxUDxxxUDxxxUxUUUx',
             'xDDDxUxxxDUxxxDUxxxDxDDDxxUUUxUxxxUUxxxUUxxxUxDDDx',
             'xDDDxUxxxDUxxxDUxxxDxDDDxxUUUxUxxxDUxxxDUxxxDxUUUx',
             'xDDDxUxxxDUxxxDUxxxDxDDDxxUUUxDxxxUDxxxUDxxxUxUUUx',
             'xDDDxUxxxDUxxxDUxxxDxDDDxxDDDxUxxxUUxxxUUxxxUxUUUx',
             'xDDDxDxxxUDxxxUDxxxUxUUUxxUUUxUxxxDUxxxDUxxxDxDDDx',
             'xDDDxDxxxUDxxxUDxxxUxUUUxxUUUxDxxxUDxxxUDxxxUxDDDx',
             'xDDDxDxxxUDxxxUDxxxUxUUUxxUUUxDxxxDDxxxDDxxxDxUUUx',
             'xDDDxDxxxUDxxxUDxxxUxUUUxxDDDxUxxxUUxxxUUxxxUxDDDx',
             'xDDDxDxxxUDxxxUDxxxUxUUUxxDDDxUxxxDUxxxDUxxxDxUUUx',
             'xDDDxDxxxUDxxxUDxxxUxUUUxxDDDxDxxxUDxxxUDxxxUxUUUx',
             'xDDDxDxxxUDxxxUDxxxUxDDDxxUUUxUxxxUUxxxUUxxxUxDDDx',
             'xDDDxDxxxUDxxxUDxxxUxDDDxxUUUxUxxxDUxxxDUxxxDxUUUx',
             'xDDDxDxxxUDxxxUDxxxUxDDDxxUUUxDxxxUDxxxUDxxxUxUUUx',
             'xDDDxDxxxUDxxxUDxxxUxDDDxxDDDxUxxxUUxxxUUxxxUxUUUx',
             'xDDDxDxxxDDxxxDDxxxDxUUUxxUUUxUxxxUUxxxUUxxxUxDDDx',
             'xDDDxDxxxDDxxxDDxxxDxUUUxxUUUxUxxxDUxxxDUxxxDxUUUx',
             'xDDDxDxxxDDxxxDDxxxDxUUUxxUUUxDxxxUDxxxUDxxxUxUUUx',
             'xDDDxDxxxDDxxxDDxxxDxUUUxxDDDxUxxxUUxxxUUxxxUxUUUx',
             'xDDDxDxxxDDxxxDDxxxDxDDDxxUUUxUxxxUUxxxUUxxxUxUUUx'),
            linecount=343000,
            max_depth=9)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            'x', parent_state[10], parent_state[11], parent_state[12], 'x',
            parent_state[16], 'xxx', parent_state[20],
            parent_state[23], 'xxx', parent_state[27],
            parent_state[30], 'xxx', parent_state[34],
            'x', parent_state[38], parent_state[39], parent_state[40], 'x',

            # Down
            'x', parent_state[255], parent_state[256], parent_state[257], 'x',
            parent_state[261], 'xxx', parent_state[265],
            parent_state[268], 'xxx', parent_state[272],
            parent_state[275], 'xxx', parent_state[279],
            'x', parent_state[283], parent_state[284], parent_state[285], 'x'
        ]

        result = ''.join(result)
        return result


class LookupTableIDA777UDSolveInnerCentersAndObliqueEdges(LookupTableIDA):
    """
    I built this 6-deep for all 70 tables and merged them together into the following

    lookup-table-7x7x7-step50-UD-solve-inner-center-and-oblique-edges.txt
    =====================================================================
    1 steps has 350 entries (0 percent, 0.00x previous step)
    2 steps has 2036 entries (0 percent, 5.82x previous step)
    3 steps has 13108 entries (0 percent, 6.44x previous step)
    4 steps has 86624 entries (2 percent, 6.61x previous step)
    5 steps has 560132 entries (13 percent, 6.47x previous step)
    6 steps has 3456952 entries (83 percent, 6.17x previous step)

    Total: 4119202 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step50-UD-solve-inner-center-and-oblique-edges.txt',
            ('xUUUxUUUUUUUUUUUUUUUxUUUxxDDDxDDDDDDDDDDDDDDDxDDDx',
             'xUUUxUUUUUUUUUUUUUUUxDDDxxUUUxDDDDDDDDDDDDDDDxDDDx',
             'xUUUxUUUUUUUUUUUUUUUxDDDxxDDDxUDDDDUDDDDUDDDDxDDDx',
             'xUUUxUUUUUUUUUUUUUUUxDDDxxDDDxDDDDUDDDDUDDDDUxDDDx',
             'xUUUxUUUUUUUUUUUUUUUxDDDxxDDDxDDDDDDDDDDDDDDDxUUUx',
             'xUUUxUUUUDUUUUDUUUUDxUUUxxUUUxDDDDDDDDDDDDDDDxDDDx',
             'xUUUxUUUUDUUUUDUUUUDxUUUxxDDDxUDDDDUDDDDUDDDDxDDDx',
             'xUUUxUUUUDUUUUDUUUUDxUUUxxDDDxDDDDUDDDDUDDDDUxDDDx',
             'xUUUxUUUUDUUUUDUUUUDxUUUxxDDDxDDDDDDDDDDDDDDDxUUUx',
             'xUUUxUUUUDUUUUDUUUUDxDDDxxUUUxUDDDDUDDDDUDDDDxDDDx',
             'xUUUxUUUUDUUUUDUUUUDxDDDxxUUUxDDDDUDDDDUDDDDUxDDDx',
             'xUUUxUUUUDUUUUDUUUUDxDDDxxUUUxDDDDDDDDDDDDDDDxUUUx',
             'xUUUxUUUUDUUUUDUUUUDxDDDxxDDDxUDDDUUDDDUUDDDUxDDDx',
             'xUUUxUUUUDUUUUDUUUUDxDDDxxDDDxUDDDDUDDDDUDDDDxUUUx',
             'xUUUxUUUUDUUUUDUUUUDxDDDxxDDDxDDDDUDDDDUDDDDUxUUUx',
             'xUUUxDUUUUDUUUUDUUUUxUUUxxUUUxDDDDDDDDDDDDDDDxDDDx',
             'xUUUxDUUUUDUUUUDUUUUxUUUxxDDDxUDDDDUDDDDUDDDDxDDDx',
             'xUUUxDUUUUDUUUUDUUUUxUUUxxDDDxDDDDUDDDDUDDDDUxDDDx',
             'xUUUxDUUUUDUUUUDUUUUxUUUxxDDDxDDDDDDDDDDDDDDDxUUUx',
             'xUUUxDUUUUDUUUUDUUUUxDDDxxUUUxUDDDDUDDDDUDDDDxDDDx',
             'xUUUxDUUUUDUUUUDUUUUxDDDxxUUUxDDDDUDDDDUDDDDUxDDDx',
             'xUUUxDUUUUDUUUUDUUUUxDDDxxUUUxDDDDDDDDDDDDDDDxUUUx',
             'xUUUxDUUUUDUUUUDUUUUxDDDxxDDDxUDDDUUDDDUUDDDUxDDDx',
             'xUUUxDUUUUDUUUUDUUUUxDDDxxDDDxUDDDDUDDDDUDDDDxUUUx',
             'xUUUxDUUUUDUUUUDUUUUxDDDxxDDDxDDDDUDDDDUDDDDUxUUUx',
             'xUUUxDUUUDDUUUDDUUUDxUUUxxUUUxUDDDDUDDDDUDDDDxDDDx',
             'xUUUxDUUUDDUUUDDUUUDxUUUxxUUUxDDDDUDDDDUDDDDUxDDDx',
             'xUUUxDUUUDDUUUDDUUUDxUUUxxUUUxDDDDDDDDDDDDDDDxUUUx',
             'xUUUxDUUUDDUUUDDUUUDxUUUxxDDDxUDDDUUDDDUUDDDUxDDDx',
             'xUUUxDUUUDDUUUDDUUUDxUUUxxDDDxUDDDDUDDDDUDDDDxUUUx',
             'xUUUxDUUUDDUUUDDUUUDxUUUxxDDDxDDDDUDDDDUDDDDUxUUUx',
             'xUUUxDUUUDDUUUDDUUUDxDDDxxUUUxUDDDUUDDDUUDDDUxDDDx',
             'xUUUxDUUUDDUUUDDUUUDxDDDxxUUUxUDDDDUDDDDUDDDDxUUUx',
             'xUUUxDUUUDDUUUDDUUUDxDDDxxUUUxDDDDUDDDDUDDDDUxUUUx',
             'xUUUxDUUUDDUUUDDUUUDxDDDxxDDDxUDDDUUDDDUUDDDUxUUUx',
             'xDDDxUUUUUUUUUUUUUUUxUUUxxUUUxDDDDDDDDDDDDDDDxDDDx',
             'xDDDxUUUUUUUUUUUUUUUxUUUxxDDDxUDDDDUDDDDUDDDDxDDDx',
             'xDDDxUUUUUUUUUUUUUUUxUUUxxDDDxDDDDUDDDDUDDDDUxDDDx',
             'xDDDxUUUUUUUUUUUUUUUxUUUxxDDDxDDDDDDDDDDDDDDDxUUUx',
             'xDDDxUUUUUUUUUUUUUUUxDDDxxUUUxUDDDDUDDDDUDDDDxDDDx',
             'xDDDxUUUUUUUUUUUUUUUxDDDxxUUUxDDDDUDDDDUDDDDUxDDDx',
             'xDDDxUUUUUUUUUUUUUUUxDDDxxUUUxDDDDDDDDDDDDDDDxUUUx',
             'xDDDxUUUUUUUUUUUUUUUxDDDxxDDDxUDDDUUDDDUUDDDUxDDDx',
             'xDDDxUUUUUUUUUUUUUUUxDDDxxDDDxUDDDDUDDDDUDDDDxUUUx',
             'xDDDxUUUUUUUUUUUUUUUxDDDxxDDDxDDDDUDDDDUDDDDUxUUUx',
             'xDDDxUUUUDUUUUDUUUUDxUUUxxUUUxUDDDDUDDDDUDDDDxDDDx',
             'xDDDxUUUUDUUUUDUUUUDxUUUxxUUUxDDDDUDDDDUDDDDUxDDDx',
             'xDDDxUUUUDUUUUDUUUUDxUUUxxUUUxDDDDDDDDDDDDDDDxUUUx',
             'xDDDxUUUUDUUUUDUUUUDxUUUxxDDDxUDDDUUDDDUUDDDUxDDDx',
             'xDDDxUUUUDUUUUDUUUUDxUUUxxDDDxUDDDDUDDDDUDDDDxUUUx',
             'xDDDxUUUUDUUUUDUUUUDxUUUxxDDDxDDDDUDDDDUDDDDUxUUUx',
             'xDDDxUUUUDUUUUDUUUUDxDDDxxUUUxUDDDUUDDDUUDDDUxDDDx',
             'xDDDxUUUUDUUUUDUUUUDxDDDxxUUUxUDDDDUDDDDUDDDDxUUUx',
             'xDDDxUUUUDUUUUDUUUUDxDDDxxUUUxDDDDUDDDDUDDDDUxUUUx',
             'xDDDxUUUUDUUUUDUUUUDxDDDxxDDDxUDDDUUDDDUUDDDUxUUUx',
             'xDDDxDUUUUDUUUUDUUUUxUUUxxUUUxUDDDDUDDDDUDDDDxDDDx',
             'xDDDxDUUUUDUUUUDUUUUxUUUxxUUUxDDDDUDDDDUDDDDUxDDDx',
             'xDDDxDUUUUDUUUUDUUUUxUUUxxUUUxDDDDDDDDDDDDDDDxUUUx',
             'xDDDxDUUUUDUUUUDUUUUxUUUxxDDDxUDDDUUDDDUUDDDUxDDDx',
             'xDDDxDUUUUDUUUUDUUUUxUUUxxDDDxUDDDDUDDDDUDDDDxUUUx',
             'xDDDxDUUUUDUUUUDUUUUxUUUxxDDDxDDDDUDDDDUDDDDUxUUUx',
             'xDDDxDUUUUDUUUUDUUUUxDDDxxUUUxUDDDUUDDDUUDDDUxDDDx',
             'xDDDxDUUUUDUUUUDUUUUxDDDxxUUUxUDDDDUDDDDUDDDDxUUUx',
             'xDDDxDUUUUDUUUUDUUUUxDDDxxUUUxDDDDUDDDDUDDDDUxUUUx',
             'xDDDxDUUUUDUUUUDUUUUxDDDxxDDDxUDDDUUDDDUUDDDUxUUUx',
             'xDDDxDUUUDDUUUDDUUUDxUUUxxUUUxUDDDUUDDDUUDDDUxDDDx',
             'xDDDxDUUUDDUUUDDUUUDxUUUxxUUUxUDDDDUDDDDUDDDDxUUUx',
             'xDDDxDUUUDDUUUDDUUUDxUUUxxUUUxDDDDUDDDDUDDDDUxUUUx',
             'xDDDxDUUUDDUUUDDUUUDxUUUxxDDDxUDDDUUDDDUUDDDUxUUUx',
             'xDDDxDUUUDDUUUDDUUUDxDDDxxUUUxUDDDUUDDDUUDDDUxUUUx'),
            moves_7x7x7,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
             "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'"),            # do not mess up staged centers

            # prune tables
            (parent.lt_UD_solve_inner_centers_and_oblique_edges_center_only,
             parent.lt_UD_solve_inner_centers_and_oblique_edges_edges_only),

            linecount=4119202,
            max_depth=6)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            'x', parent_state[10], parent_state[11], parent_state[12], 'x',
            parent_state[16], parent_state[17], parent_state[18], parent_state[19], parent_state[20],
            parent_state[23], parent_state[24], parent_state[25], parent_state[26], parent_state[27],
            parent_state[30], parent_state[31], parent_state[32], parent_state[33], parent_state[34],
            'x', parent_state[38], parent_state[39], parent_state[40], 'x',

            # Down
            'x', parent_state[255], parent_state[256], parent_state[257], 'x',
            parent_state[261], parent_state[262], parent_state[263], parent_state[264], parent_state[265],
            parent_state[268], parent_state[269], parent_state[270], parent_state[271], parent_state[272],
            parent_state[275], parent_state[276], parent_state[277], parent_state[278], parent_state[279],
            'x', parent_state[283], parent_state[284], parent_state[285], 'x'
        ]

        result = ''.join(result)
        return result


class LookupTable777LRSolveInnerXCenterTCenterMiddleObliqueEdge(LookupTable):
    """
    lookup-table-7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges.txt
    ==================================================================================
    1 steps has 210 entries (0 percent, 0.00x previous step)
    2 steps has 770 entries (0 percent, 3.67x previous step)
    3 steps has 1,540 entries (0 percent, 2.00x previous step)
    4 steps has 5,950 entries (1 percent, 3.86x previous step)
    5 steps has 15,400 entries (4 percent, 2.59x previous step)
    6 steps has 44,310 entries (12 percent, 2.88x previous step)
    7 steps has 82,600 entries (24 percent, 1.86x previous step)
    8 steps has 120,960 entries (35 percent, 1.46x previous step)
    9 steps has 62,160 entries (18 percent, 0.51x previous step)
    10 steps has 8,820 entries (2 percent, 0.14x previous step)
    11 steps has 280 entries (0 percent, 0.03x previous step)

    Total: 343,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges.txt',
            ('xxLxxxLLLxLLLLLxLLLxxxLxxxxRxxxRRRxRRRRRxRRRxxxRxx',
             'xxLxxxLLLxLLLLLxLLLxxxRxxxxLxxxRRRxRRRRRxRRRxxxRxx',
             'xxLxxxLLLxLLLLLxLLLxxxRxxxxRxxxRRRxLRRRRxRRRxxxRxx',
             'xxLxxxLLLxLLLLLxLLLxxxRxxxxRxxxRRRxRRRRLxRRRxxxRxx',
             'xxLxxxLLLxLLLLLxLLLxxxRxxxxRxxxRRRxRRRRRxRRRxxxLxx',
             'xxLxxxLLLxLLLLRxLLLxxxLxxxxLxxxRRRxRRRRRxRRRxxxRxx',
             'xxLxxxLLLxLLLLRxLLLxxxLxxxxRxxxRRRxLRRRRxRRRxxxRxx',
             'xxLxxxLLLxLLLLRxLLLxxxLxxxxRxxxRRRxRRRRLxRRRxxxRxx',
             'xxLxxxLLLxLLLLRxLLLxxxLxxxxRxxxRRRxRRRRRxRRRxxxLxx',
             'xxLxxxLLLxLLLLRxLLLxxxRxxxxLxxxRRRxLRRRRxRRRxxxRxx',
             'xxLxxxLLLxLLLLRxLLLxxxRxxxxLxxxRRRxRRRRLxRRRxxxRxx',
             'xxLxxxLLLxLLLLRxLLLxxxRxxxxLxxxRRRxRRRRRxRRRxxxLxx',
             'xxLxxxLLLxLLLLRxLLLxxxRxxxxRxxxRRRxLRRRLxRRRxxxRxx',
             'xxLxxxLLLxLLLLRxLLLxxxRxxxxRxxxRRRxLRRRRxRRRxxxLxx',
             'xxLxxxLLLxLLLLRxLLLxxxRxxxxRxxxRRRxRRRRLxRRRxxxLxx',
             'xxLxxxLLLxRLLLLxLLLxxxLxxxxLxxxRRRxRRRRRxRRRxxxRxx',
             'xxLxxxLLLxRLLLLxLLLxxxLxxxxRxxxRRRxLRRRRxRRRxxxRxx',
             'xxLxxxLLLxRLLLLxLLLxxxLxxxxRxxxRRRxRRRRLxRRRxxxRxx',
             'xxLxxxLLLxRLLLLxLLLxxxLxxxxRxxxRRRxRRRRRxRRRxxxLxx',
             'xxLxxxLLLxRLLLLxLLLxxxRxxxxLxxxRRRxLRRRRxRRRxxxRxx',
             'xxLxxxLLLxRLLLLxLLLxxxRxxxxLxxxRRRxRRRRLxRRRxxxRxx',
             'xxLxxxLLLxRLLLLxLLLxxxRxxxxLxxxRRRxRRRRRxRRRxxxLxx',
             'xxLxxxLLLxRLLLLxLLLxxxRxxxxRxxxRRRxLRRRLxRRRxxxRxx',
             'xxLxxxLLLxRLLLLxLLLxxxRxxxxRxxxRRRxLRRRRxRRRxxxLxx',
             'xxLxxxLLLxRLLLLxLLLxxxRxxxxRxxxRRRxRRRRLxRRRxxxLxx',
             'xxLxxxLLLxRLLLRxLLLxxxLxxxxLxxxRRRxLRRRRxRRRxxxRxx',
             'xxLxxxLLLxRLLLRxLLLxxxLxxxxLxxxRRRxRRRRLxRRRxxxRxx',
             'xxLxxxLLLxRLLLRxLLLxxxLxxxxLxxxRRRxRRRRRxRRRxxxLxx',
             'xxLxxxLLLxRLLLRxLLLxxxLxxxxRxxxRRRxLRRRLxRRRxxxRxx',
             'xxLxxxLLLxRLLLRxLLLxxxLxxxxRxxxRRRxLRRRRxRRRxxxLxx',
             'xxLxxxLLLxRLLLRxLLLxxxLxxxxRxxxRRRxRRRRLxRRRxxxLxx',
             'xxLxxxLLLxRLLLRxLLLxxxRxxxxLxxxRRRxLRRRLxRRRxxxRxx',
             'xxLxxxLLLxRLLLRxLLLxxxRxxxxLxxxRRRxLRRRRxRRRxxxLxx',
             'xxLxxxLLLxRLLLRxLLLxxxRxxxxLxxxRRRxRRRRLxRRRxxxLxx',
             'xxLxxxLLLxRLLLRxLLLxxxRxxxxRxxxRRRxLRRRLxRRRxxxLxx',
             'xxRxxxLLLxLLLLLxLLLxxxLxxxxLxxxRRRxRRRRRxRRRxxxRxx',
             'xxRxxxLLLxLLLLLxLLLxxxLxxxxRxxxRRRxLRRRRxRRRxxxRxx',
             'xxRxxxLLLxLLLLLxLLLxxxLxxxxRxxxRRRxRRRRLxRRRxxxRxx',
             'xxRxxxLLLxLLLLLxLLLxxxLxxxxRxxxRRRxRRRRRxRRRxxxLxx',
             'xxRxxxLLLxLLLLLxLLLxxxRxxxxLxxxRRRxLRRRRxRRRxxxRxx',
             'xxRxxxLLLxLLLLLxLLLxxxRxxxxLxxxRRRxRRRRLxRRRxxxRxx',
             'xxRxxxLLLxLLLLLxLLLxxxRxxxxLxxxRRRxRRRRRxRRRxxxLxx',
             'xxRxxxLLLxLLLLLxLLLxxxRxxxxRxxxRRRxLRRRLxRRRxxxRxx',
             'xxRxxxLLLxLLLLLxLLLxxxRxxxxRxxxRRRxLRRRRxRRRxxxLxx',
             'xxRxxxLLLxLLLLLxLLLxxxRxxxxRxxxRRRxRRRRLxRRRxxxLxx',
             'xxRxxxLLLxLLLLRxLLLxxxLxxxxLxxxRRRxLRRRRxRRRxxxRxx',
             'xxRxxxLLLxLLLLRxLLLxxxLxxxxLxxxRRRxRRRRLxRRRxxxRxx',
             'xxRxxxLLLxLLLLRxLLLxxxLxxxxLxxxRRRxRRRRRxRRRxxxLxx',
             'xxRxxxLLLxLLLLRxLLLxxxLxxxxRxxxRRRxLRRRLxRRRxxxRxx',
             'xxRxxxLLLxLLLLRxLLLxxxLxxxxRxxxRRRxLRRRRxRRRxxxLxx',
             'xxRxxxLLLxLLLLRxLLLxxxLxxxxRxxxRRRxRRRRLxRRRxxxLxx',
             'xxRxxxLLLxLLLLRxLLLxxxRxxxxLxxxRRRxLRRRLxRRRxxxRxx',
             'xxRxxxLLLxLLLLRxLLLxxxRxxxxLxxxRRRxLRRRRxRRRxxxLxx',
             'xxRxxxLLLxLLLLRxLLLxxxRxxxxLxxxRRRxRRRRLxRRRxxxLxx',
             'xxRxxxLLLxLLLLRxLLLxxxRxxxxRxxxRRRxLRRRLxRRRxxxLxx',
             'xxRxxxLLLxRLLLLxLLLxxxLxxxxLxxxRRRxLRRRRxRRRxxxRxx',
             'xxRxxxLLLxRLLLLxLLLxxxLxxxxLxxxRRRxRRRRLxRRRxxxRxx',
             'xxRxxxLLLxRLLLLxLLLxxxLxxxxLxxxRRRxRRRRRxRRRxxxLxx',
             'xxRxxxLLLxRLLLLxLLLxxxLxxxxRxxxRRRxLRRRLxRRRxxxRxx',
             'xxRxxxLLLxRLLLLxLLLxxxLxxxxRxxxRRRxLRRRRxRRRxxxLxx',
             'xxRxxxLLLxRLLLLxLLLxxxLxxxxRxxxRRRxRRRRLxRRRxxxLxx',
             'xxRxxxLLLxRLLLLxLLLxxxRxxxxLxxxRRRxLRRRLxRRRxxxRxx',
             'xxRxxxLLLxRLLLLxLLLxxxRxxxxLxxxRRRxLRRRRxRRRxxxLxx',
             'xxRxxxLLLxRLLLLxLLLxxxRxxxxLxxxRRRxRRRRLxRRRxxxLxx',
             'xxRxxxLLLxRLLLLxLLLxxxRxxxxRxxxRRRxLRRRLxRRRxxxLxx',
             'xxRxxxLLLxRLLLRxLLLxxxLxxxxLxxxRRRxLRRRLxRRRxxxRxx',
             'xxRxxxLLLxRLLLRxLLLxxxLxxxxLxxxRRRxLRRRRxRRRxxxLxx',
             'xxRxxxLLLxRLLLRxLLLxxxLxxxxLxxxRRRxRRRRLxRRRxxxLxx',
             'xxRxxxLLLxRLLLRxLLLxxxLxxxxRxxxRRRxLRRRLxRRRxxxLxx',
             'xxRxxxLLLxRLLLRxLLLxxxRxxxxLxxxRRRxLRRRLxRRRxxxLxx'),
            linecount=343000,
            max_depth=11)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'xx', parent_state[60], 'xx',
            'x', parent_state[66], parent_state[67], parent_state[68], 'x',
            parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76],
            'x', parent_state[80], parent_state[81], parent_state[82], 'x',
            'xx', parent_state[88], 'xx',

            # Right
            'xx', parent_state[158], 'xx',
            'x', parent_state[164], parent_state[165], parent_state[166], 'x',
            parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174],
            'x', parent_state[178], parent_state[179], parent_state[180], 'x',
            'xx', parent_state[186], 'xx'
        ]

        result = ['x' if x in ('U', 'D', 'F', 'B') else x for x in result]
        result = ''.join(result)

        return result


class LookupTable777LRSolveObliqueEdge(LookupTable):
    """
    lookup-table-7x7x7-step62-LR-oblique-edges.txt
    ==============================================
    1 steps has 182 entries (0 percent, 0.00x previous step)
    2 steps has 616 entries (0 percent, 3.38x previous step)
    3 steps has 2,044 entries (0 percent, 3.32x previous step)
    4 steps has 8,576 entries (2 percent, 4.20x previous step)
    5 steps has 21,516 entries (6 percent, 2.51x previous step)
    6 steps has 60,392 entries (17 percent, 2.81x previous step)
    7 steps has 105,050 entries (30 percent, 1.74x previous step)
    8 steps has 106,464 entries (31 percent, 1.01x previous step)
    9 steps has 35,772 entries (10 percent, 0.34x previous step)
    10 steps has 2,368 entries (0 percent, 0.07x previous step)
    11 steps has 20 entries (0 percent, 0.01x previous step)

    Total: 343,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step62-LR-oblique-edges.txt',
            ('xLLLxLxxxLLxxxLLxxxLxLLLxxRRRxRxxxRRxxxRRxxxRxRRRx',
             'xLLLxLxxxLLxxxLLxxxLxRRRxxLLLxRxxxRRxxxRRxxxRxRRRx',
             'xLLLxLxxxLLxxxLLxxxLxRRRxxRRRxLxxxRLxxxRLxxxRxRRRx',
             'xLLLxLxxxLLxxxLLxxxLxRRRxxRRRxRxxxLRxxxLRxxxLxRRRx',
             'xLLLxLxxxLLxxxLLxxxLxRRRxxRRRxRxxxRRxxxRRxxxRxLLLx',
             'xLLLxLxxxRLxxxRLxxxRxLLLxxLLLxRxxxRRxxxRRxxxRxRRRx',
             'xLLLxLxxxRLxxxRLxxxRxLLLxxRRRxLxxxRLxxxRLxxxRxRRRx',
             'xLLLxLxxxRLxxxRLxxxRxLLLxxRRRxRxxxLRxxxLRxxxLxRRRx',
             'xLLLxLxxxRLxxxRLxxxRxLLLxxRRRxRxxxRRxxxRRxxxRxLLLx',
             'xLLLxLxxxRLxxxRLxxxRxRRRxxLLLxLxxxRLxxxRLxxxRxRRRx',
             'xLLLxLxxxRLxxxRLxxxRxRRRxxLLLxRxxxLRxxxLRxxxLxRRRx',
             'xLLLxLxxxRLxxxRLxxxRxRRRxxLLLxRxxxRRxxxRRxxxRxLLLx',
             'xLLLxLxxxRLxxxRLxxxRxRRRxxRRRxLxxxLLxxxLLxxxLxRRRx',
             'xLLLxLxxxRLxxxRLxxxRxRRRxxRRRxLxxxRLxxxRLxxxRxLLLx',
             'xLLLxLxxxRLxxxRLxxxRxRRRxxRRRxRxxxLRxxxLRxxxLxLLLx',
             'xLLLxRxxxLRxxxLRxxxLxLLLxxLLLxRxxxRRxxxRRxxxRxRRRx',
             'xLLLxRxxxLRxxxLRxxxLxLLLxxRRRxLxxxRLxxxRLxxxRxRRRx',
             'xLLLxRxxxLRxxxLRxxxLxLLLxxRRRxRxxxLRxxxLRxxxLxRRRx',
             'xLLLxRxxxLRxxxLRxxxLxLLLxxRRRxRxxxRRxxxRRxxxRxLLLx',
             'xLLLxRxxxLRxxxLRxxxLxRRRxxLLLxLxxxRLxxxRLxxxRxRRRx',
             'xLLLxRxxxLRxxxLRxxxLxRRRxxLLLxRxxxLRxxxLRxxxLxRRRx',
             'xLLLxRxxxLRxxxLRxxxLxRRRxxLLLxRxxxRRxxxRRxxxRxLLLx',
             'xLLLxRxxxLRxxxLRxxxLxRRRxxRRRxLxxxLLxxxLLxxxLxRRRx',
             'xLLLxRxxxLRxxxLRxxxLxRRRxxRRRxLxxxRLxxxRLxxxRxLLLx',
             'xLLLxRxxxLRxxxLRxxxLxRRRxxRRRxRxxxLRxxxLRxxxLxLLLx',
             'xLLLxRxxxRRxxxRRxxxRxLLLxxLLLxLxxxRLxxxRLxxxRxRRRx',
             'xLLLxRxxxRRxxxRRxxxRxLLLxxLLLxRxxxLRxxxLRxxxLxRRRx',
             'xLLLxRxxxRRxxxRRxxxRxLLLxxLLLxRxxxRRxxxRRxxxRxLLLx',
             'xLLLxRxxxRRxxxRRxxxRxLLLxxRRRxLxxxLLxxxLLxxxLxRRRx',
             'xLLLxRxxxRRxxxRRxxxRxLLLxxRRRxLxxxRLxxxRLxxxRxLLLx',
             'xLLLxRxxxRRxxxRRxxxRxLLLxxRRRxRxxxLRxxxLRxxxLxLLLx',
             'xLLLxRxxxRRxxxRRxxxRxRRRxxLLLxLxxxLLxxxLLxxxLxRRRx',
             'xLLLxRxxxRRxxxRRxxxRxRRRxxLLLxLxxxRLxxxRLxxxRxLLLx',
             'xLLLxRxxxRRxxxRRxxxRxRRRxxLLLxRxxxLRxxxLRxxxLxLLLx',
             'xLLLxRxxxRRxxxRRxxxRxRRRxxRRRxLxxxLLxxxLLxxxLxLLLx',
             'xRRRxLxxxLLxxxLLxxxLxLLLxxLLLxRxxxRRxxxRRxxxRxRRRx',
             'xRRRxLxxxLLxxxLLxxxLxLLLxxRRRxLxxxRLxxxRLxxxRxRRRx',
             'xRRRxLxxxLLxxxLLxxxLxLLLxxRRRxRxxxLRxxxLRxxxLxRRRx',
             'xRRRxLxxxLLxxxLLxxxLxLLLxxRRRxRxxxRRxxxRRxxxRxLLLx',
             'xRRRxLxxxLLxxxLLxxxLxRRRxxLLLxLxxxRLxxxRLxxxRxRRRx',
             'xRRRxLxxxLLxxxLLxxxLxRRRxxLLLxRxxxLRxxxLRxxxLxRRRx',
             'xRRRxLxxxLLxxxLLxxxLxRRRxxLLLxRxxxRRxxxRRxxxRxLLLx',
             'xRRRxLxxxLLxxxLLxxxLxRRRxxRRRxLxxxLLxxxLLxxxLxRRRx',
             'xRRRxLxxxLLxxxLLxxxLxRRRxxRRRxLxxxRLxxxRLxxxRxLLLx',
             'xRRRxLxxxLLxxxLLxxxLxRRRxxRRRxRxxxLRxxxLRxxxLxLLLx',
             'xRRRxLxxxRLxxxRLxxxRxLLLxxLLLxLxxxRLxxxRLxxxRxRRRx',
             'xRRRxLxxxRLxxxRLxxxRxLLLxxLLLxRxxxLRxxxLRxxxLxRRRx',
             'xRRRxLxxxRLxxxRLxxxRxLLLxxLLLxRxxxRRxxxRRxxxRxLLLx',
             'xRRRxLxxxRLxxxRLxxxRxLLLxxRRRxLxxxLLxxxLLxxxLxRRRx',
             'xRRRxLxxxRLxxxRLxxxRxLLLxxRRRxLxxxRLxxxRLxxxRxLLLx',
             'xRRRxLxxxRLxxxRLxxxRxLLLxxRRRxRxxxLRxxxLRxxxLxLLLx',
             'xRRRxLxxxRLxxxRLxxxRxRRRxxLLLxLxxxLLxxxLLxxxLxRRRx',
             'xRRRxLxxxRLxxxRLxxxRxRRRxxLLLxLxxxRLxxxRLxxxRxLLLx',
             'xRRRxLxxxRLxxxRLxxxRxRRRxxLLLxRxxxLRxxxLRxxxLxLLLx',
             'xRRRxLxxxRLxxxRLxxxRxRRRxxRRRxLxxxLLxxxLLxxxLxLLLx',
             'xRRRxRxxxLRxxxLRxxxLxLLLxxLLLxLxxxRLxxxRLxxxRxRRRx',
             'xRRRxRxxxLRxxxLRxxxLxLLLxxLLLxRxxxLRxxxLRxxxLxRRRx',
             'xRRRxRxxxLRxxxLRxxxLxLLLxxLLLxRxxxRRxxxRRxxxRxLLLx',
             'xRRRxRxxxLRxxxLRxxxLxLLLxxRRRxLxxxLLxxxLLxxxLxRRRx',
             'xRRRxRxxxLRxxxLRxxxLxLLLxxRRRxLxxxRLxxxRLxxxRxLLLx',
             'xRRRxRxxxLRxxxLRxxxLxLLLxxRRRxRxxxLRxxxLRxxxLxLLLx',
             'xRRRxRxxxLRxxxLRxxxLxRRRxxLLLxLxxxLLxxxLLxxxLxRRRx',
             'xRRRxRxxxLRxxxLRxxxLxRRRxxLLLxLxxxRLxxxRLxxxRxLLLx',
             'xRRRxRxxxLRxxxLRxxxLxRRRxxLLLxRxxxLRxxxLRxxxLxLLLx',
             'xRRRxRxxxLRxxxLRxxxLxRRRxxRRRxLxxxLLxxxLLxxxLxLLLx',
             'xRRRxRxxxRRxxxRRxxxRxLLLxxLLLxLxxxLLxxxLLxxxLxRRRx',
             'xRRRxRxxxRRxxxRRxxxRxLLLxxLLLxLxxxRLxxxRLxxxRxLLLx',
             'xRRRxRxxxRRxxxRRxxxRxLLLxxLLLxRxxxLRxxxLRxxxLxLLLx',
             'xRRRxRxxxRRxxxRRxxxRxLLLxxRRRxLxxxLLxxxLLxxxLxLLLx',
             'xRRRxRxxxRRxxxRRxxxRxRRRxxLLLxLxxxLLxxxLLxxxLxLLLx'),
            linecount=343000,
            max_depth=11)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', parent_state[59], parent_state[60], parent_state[61], 'x',
            parent_state[65], 'xxx', parent_state[69],
            parent_state[72], 'xxx', parent_state[76],
            parent_state[79], 'xxx', parent_state[83],
            'x', parent_state[87], parent_state[88], parent_state[89], 'x',

            # Right
            'x', parent_state[157], parent_state[158], parent_state[159], 'x',
            parent_state[163], 'xxx', parent_state[167],
            parent_state[170], 'xxx', parent_state[174],
            parent_state[177], 'xxx', parent_state[181],
            'x', parent_state[185], parent_state[186], parent_state[187], 'x'
        ]

        result = ''.join(['x' if x in ('U', 'D', 'F', 'B') else x for x in result])

        return result


class LookupTableIDA777LRSolveInnerCentersAndObliqueEdges(LookupTableIDA):
    """
    lookup-table-7x7x7-step60-LR-solve-inner-center-and-oblique-edges.txt
    =====================================================================
    1 steps has 210 entries (0 percent, 0.00x previous step)
    2 steps has 770 entries (0 percent, 3.67x previous step)
    3 steps has 2,828 entries (0 percent, 3.67x previous step)
    4 steps has 15,158 entries (0 percent, 5.36x previous step)
    5 steps has 63,008 entries (0 percent, 4.16x previous step)
    6 steps has 290,588 entries (4 percent, 4.61x previous step)
    7 steps has 1,232,594 entries (17 percent, 4.24x previous step)
    8 steps has 5,266,642 entries (76 percent, 4.27x previous step)

    Total: 6,871,798 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step60-LR-solve-inner-center-and-oblique-edges.txt',
            ('xLLLxLLLLLLLLLLLLLLLxLLLxxRRRxRRRRRRRRRRRRRRRxRRRx',
             'xLLLxLLLLLLLLLLLLLLLxRRRxxLLLxRRRRRRRRRRRRRRRxRRRx',
             'xLLLxLLLLLLLLLLLLLLLxRRRxxRRRxLRRRRLRRRRLRRRRxRRRx',
             'xLLLxLLLLLLLLLLLLLLLxRRRxxRRRxRRRRLRRRRLRRRRLxRRRx',
             'xLLLxLLLLLLLLLLLLLLLxRRRxxRRRxRRRRRRRRRRRRRRRxLLLx',
             'xLLLxLLLLRLLLLRLLLLRxLLLxxLLLxRRRRRRRRRRRRRRRxRRRx',
             'xLLLxLLLLRLLLLRLLLLRxLLLxxRRRxLRRRRLRRRRLRRRRxRRRx',
             'xLLLxLLLLRLLLLRLLLLRxLLLxxRRRxRRRRLRRRRLRRRRLxRRRx',
             'xLLLxLLLLRLLLLRLLLLRxLLLxxRRRxRRRRRRRRRRRRRRRxLLLx',
             'xLLLxLLLLRLLLLRLLLLRxRRRxxLLLxLRRRRLRRRRLRRRRxRRRx',
             'xLLLxLLLLRLLLLRLLLLRxRRRxxLLLxRRRRLRRRRLRRRRLxRRRx',
             'xLLLxLLLLRLLLLRLLLLRxRRRxxLLLxRRRRRRRRRRRRRRRxLLLx',
             'xLLLxLLLLRLLLLRLLLLRxRRRxxRRRxLRRRLLRRRLLRRRLxRRRx',
             'xLLLxLLLLRLLLLRLLLLRxRRRxxRRRxLRRRRLRRRRLRRRRxLLLx',
             'xLLLxLLLLRLLLLRLLLLRxRRRxxRRRxRRRRLRRRRLRRRRLxLLLx',
             'xLLLxRLLLLRLLLLRLLLLxLLLxxLLLxRRRRRRRRRRRRRRRxRRRx',
             'xLLLxRLLLLRLLLLRLLLLxLLLxxRRRxLRRRRLRRRRLRRRRxRRRx',
             'xLLLxRLLLLRLLLLRLLLLxLLLxxRRRxRRRRLRRRRLRRRRLxRRRx',
             'xLLLxRLLLLRLLLLRLLLLxLLLxxRRRxRRRRRRRRRRRRRRRxLLLx',
             'xLLLxRLLLLRLLLLRLLLLxRRRxxLLLxLRRRRLRRRRLRRRRxRRRx',
             'xLLLxRLLLLRLLLLRLLLLxRRRxxLLLxRRRRLRRRRLRRRRLxRRRx',
             'xLLLxRLLLLRLLLLRLLLLxRRRxxLLLxRRRRRRRRRRRRRRRxLLLx',
             'xLLLxRLLLLRLLLLRLLLLxRRRxxRRRxLRRRLLRRRLLRRRLxRRRx',
             'xLLLxRLLLLRLLLLRLLLLxRRRxxRRRxLRRRRLRRRRLRRRRxLLLx',
             'xLLLxRLLLLRLLLLRLLLLxRRRxxRRRxRRRRLRRRRLRRRRLxLLLx',
             'xLLLxRLLLRRLLLRRLLLRxLLLxxLLLxLRRRRLRRRRLRRRRxRRRx',
             'xLLLxRLLLRRLLLRRLLLRxLLLxxLLLxRRRRLRRRRLRRRRLxRRRx',
             'xLLLxRLLLRRLLLRRLLLRxLLLxxLLLxRRRRRRRRRRRRRRRxLLLx',
             'xLLLxRLLLRRLLLRRLLLRxLLLxxRRRxLRRRLLRRRLLRRRLxRRRx',
             'xLLLxRLLLRRLLLRRLLLRxLLLxxRRRxLRRRRLRRRRLRRRRxLLLx',
             'xLLLxRLLLRRLLLRRLLLRxLLLxxRRRxRRRRLRRRRLRRRRLxLLLx',
             'xLLLxRLLLRRLLLRRLLLRxRRRxxLLLxLRRRLLRRRLLRRRLxRRRx',
             'xLLLxRLLLRRLLLRRLLLRxRRRxxLLLxLRRRRLRRRRLRRRRxLLLx',
             'xLLLxRLLLRRLLLRRLLLRxRRRxxLLLxRRRRLRRRRLRRRRLxLLLx',
             'xLLLxRLLLRRLLLRRLLLRxRRRxxRRRxLRRRLLRRRLLRRRLxLLLx',
             'xRRRxLLLLLLLLLLLLLLLxLLLxxLLLxRRRRRRRRRRRRRRRxRRRx',
             'xRRRxLLLLLLLLLLLLLLLxLLLxxRRRxLRRRRLRRRRLRRRRxRRRx',
             'xRRRxLLLLLLLLLLLLLLLxLLLxxRRRxRRRRLRRRRLRRRRLxRRRx',
             'xRRRxLLLLLLLLLLLLLLLxLLLxxRRRxRRRRRRRRRRRRRRRxLLLx',
             'xRRRxLLLLLLLLLLLLLLLxRRRxxLLLxLRRRRLRRRRLRRRRxRRRx',
             'xRRRxLLLLLLLLLLLLLLLxRRRxxLLLxRRRRLRRRRLRRRRLxRRRx',
             'xRRRxLLLLLLLLLLLLLLLxRRRxxLLLxRRRRRRRRRRRRRRRxLLLx',
             'xRRRxLLLLLLLLLLLLLLLxRRRxxRRRxLRRRLLRRRLLRRRLxRRRx',
             'xRRRxLLLLLLLLLLLLLLLxRRRxxRRRxLRRRRLRRRRLRRRRxLLLx',
             'xRRRxLLLLLLLLLLLLLLLxRRRxxRRRxRRRRLRRRRLRRRRLxLLLx',
             'xRRRxLLLLRLLLLRLLLLRxLLLxxLLLxLRRRRLRRRRLRRRRxRRRx',
             'xRRRxLLLLRLLLLRLLLLRxLLLxxLLLxRRRRLRRRRLRRRRLxRRRx',
             'xRRRxLLLLRLLLLRLLLLRxLLLxxLLLxRRRRRRRRRRRRRRRxLLLx',
             'xRRRxLLLLRLLLLRLLLLRxLLLxxRRRxLRRRLLRRRLLRRRLxRRRx',
             'xRRRxLLLLRLLLLRLLLLRxLLLxxRRRxLRRRRLRRRRLRRRRxLLLx',
             'xRRRxLLLLRLLLLRLLLLRxLLLxxRRRxRRRRLRRRRLRRRRLxLLLx',
             'xRRRxLLLLRLLLLRLLLLRxRRRxxLLLxLRRRLLRRRLLRRRLxRRRx',
             'xRRRxLLLLRLLLLRLLLLRxRRRxxLLLxLRRRRLRRRRLRRRRxLLLx',
             'xRRRxLLLLRLLLLRLLLLRxRRRxxLLLxRRRRLRRRRLRRRRLxLLLx',
             'xRRRxLLLLRLLLLRLLLLRxRRRxxRRRxLRRRLLRRRLLRRRLxLLLx',
             'xRRRxRLLLLRLLLLRLLLLxLLLxxLLLxLRRRRLRRRRLRRRRxRRRx',
             'xRRRxRLLLLRLLLLRLLLLxLLLxxLLLxRRRRLRRRRLRRRRLxRRRx',
             'xRRRxRLLLLRLLLLRLLLLxLLLxxLLLxRRRRRRRRRRRRRRRxLLLx',
             'xRRRxRLLLLRLLLLRLLLLxLLLxxRRRxLRRRLLRRRLLRRRLxRRRx',
             'xRRRxRLLLLRLLLLRLLLLxLLLxxRRRxLRRRRLRRRRLRRRRxLLLx',
             'xRRRxRLLLLRLLLLRLLLLxLLLxxRRRxRRRRLRRRRLRRRRLxLLLx',
             'xRRRxRLLLLRLLLLRLLLLxRRRxxLLLxLRRRLLRRRLLRRRLxRRRx',
             'xRRRxRLLLLRLLLLRLLLLxRRRxxLLLxLRRRRLRRRRLRRRRxLLLx',
             'xRRRxRLLLLRLLLLRLLLLxRRRxxLLLxRRRRLRRRRLRRRRLxLLLx',
             'xRRRxRLLLLRLLLLRLLLLxRRRxxRRRxLRRRLLRRRLLRRRLxLLLx',
             'xRRRxRLLLRRLLLRRLLLRxLLLxxLLLxLRRRLLRRRLLRRRLxRRRx',
             'xRRRxRLLLRRLLLRRLLLRxLLLxxLLLxLRRRRLRRRRLRRRRxLLLx',
             'xRRRxRLLLRRLLLRRLLLRxLLLxxLLLxRRRRLRRRRLRRRRLxLLLx',
             'xRRRxRLLLRRLLLRRLLLRxLLLxxRRRxLRRRLLRRRLLRRRLxLLLx',
             'xRRRxRLLLRRLLLRRLLLRxRRRxxLLLxLRRRLLRRRLLRRRLxLLLx'),
            moves_7x7x7,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
             "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
             "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2",                               # do not mess up solved UD
             "F", "F'", "F2", "B", "B'", "B2"),                                                        # no point rotating F or B here

            # prune tables
            (parent.lt_LR_solve_inner_x_center_t_center_middle_oblique_edge,
             parent.lt_LR_solve_oblique_edge),
            linecount=6871798,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            'x', parent_state[59], parent_state[60], parent_state[61], 'x',
            parent_state[65], parent_state[66], parent_state[67], parent_state[68], parent_state[69],
            parent_state[72], parent_state[73], parent_state[74], parent_state[75], parent_state[76],
            parent_state[79], parent_state[80], parent_state[81], parent_state[82], parent_state[83],
            'x', parent_state[87], parent_state[88], parent_state[89], 'x',

            # Right
            'x', parent_state[157], parent_state[158], parent_state[159], 'x',
            parent_state[163], parent_state[164], parent_state[165], parent_state[166], parent_state[167],
            parent_state[170], parent_state[171], parent_state[172], parent_state[173], parent_state[174],
            parent_state[177], parent_state[178], parent_state[179], parent_state[180], parent_state[181],
            'x', parent_state[185], parent_state[186], parent_state[187], 'x'
        ]

        result = ''.join(['x' if x in ('U', 'D', 'F', 'B') else x for x in result])

        return result


class LookupTable777FBSolveInnerXCenterTCenterMiddleObliqueEdge(LookupTable):
    """
    lookup-table-7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges.txt
    =================================================================================
    1 steps has 210 entries (0 percent, 0.00x previous step)
    2 steps has 770 entries (0 percent, 3.67x previous step)
    3 steps has 1,540 entries (0 percent, 2.00x previous step)
    4 steps has 5,950 entries (1 percent, 3.86x previous step)
    5 steps has 15,400 entries (4 percent, 2.59x previous step)
    6 steps has 44,310 entries (12 percent, 2.88x previous step)
    7 steps has 82,600 entries (24 percent, 1.86x previous step)
    8 steps has 120,960 entries (35 percent, 1.46x previous step)
    9 steps has 62,160 entries (18 percent, 0.51x previous step)
    10 steps has 8,820 entries (2 percent, 0.14x previous step)
    11 steps has 280 entries (0 percent, 0.03x previous step)

    Total: 343,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges.txt',
            ('xxFxxxFFFxFFFFFxFFFxxxFxxxxBxxxBBBxBBBBBxBBBxxxBxx',
             'xxFxxxFFFxFFFFFxFFFxxxBxxxxFxxxBBBxBBBBBxBBBxxxBxx',
             'xxFxxxFFFxFFFFFxFFFxxxBxxxxBxxxBBBxFBBBBxBBBxxxBxx',
             'xxFxxxFFFxFFFFFxFFFxxxBxxxxBxxxBBBxBBBBFxBBBxxxBxx',
             'xxFxxxFFFxFFFFFxFFFxxxBxxxxBxxxBBBxBBBBBxBBBxxxFxx',
             'xxFxxxFFFxFFFFBxFFFxxxFxxxxFxxxBBBxBBBBBxBBBxxxBxx',
             'xxFxxxFFFxFFFFBxFFFxxxFxxxxBxxxBBBxFBBBBxBBBxxxBxx',
             'xxFxxxFFFxFFFFBxFFFxxxFxxxxBxxxBBBxBBBBFxBBBxxxBxx',
             'xxFxxxFFFxFFFFBxFFFxxxFxxxxBxxxBBBxBBBBBxBBBxxxFxx',
             'xxFxxxFFFxFFFFBxFFFxxxBxxxxFxxxBBBxFBBBBxBBBxxxBxx',
             'xxFxxxFFFxFFFFBxFFFxxxBxxxxFxxxBBBxBBBBFxBBBxxxBxx',
             'xxFxxxFFFxFFFFBxFFFxxxBxxxxFxxxBBBxBBBBBxBBBxxxFxx',
             'xxFxxxFFFxFFFFBxFFFxxxBxxxxBxxxBBBxFBBBFxBBBxxxBxx',
             'xxFxxxFFFxFFFFBxFFFxxxBxxxxBxxxBBBxFBBBBxBBBxxxFxx',
             'xxFxxxFFFxFFFFBxFFFxxxBxxxxBxxxBBBxBBBBFxBBBxxxFxx',
             'xxFxxxFFFxBFFFFxFFFxxxFxxxxFxxxBBBxBBBBBxBBBxxxBxx',
             'xxFxxxFFFxBFFFFxFFFxxxFxxxxBxxxBBBxFBBBBxBBBxxxBxx',
             'xxFxxxFFFxBFFFFxFFFxxxFxxxxBxxxBBBxBBBBFxBBBxxxBxx',
             'xxFxxxFFFxBFFFFxFFFxxxFxxxxBxxxBBBxBBBBBxBBBxxxFxx',
             'xxFxxxFFFxBFFFFxFFFxxxBxxxxFxxxBBBxFBBBBxBBBxxxBxx',
             'xxFxxxFFFxBFFFFxFFFxxxBxxxxFxxxBBBxBBBBFxBBBxxxBxx',
             'xxFxxxFFFxBFFFFxFFFxxxBxxxxFxxxBBBxBBBBBxBBBxxxFxx',
             'xxFxxxFFFxBFFFFxFFFxxxBxxxxBxxxBBBxFBBBFxBBBxxxBxx',
             'xxFxxxFFFxBFFFFxFFFxxxBxxxxBxxxBBBxFBBBBxBBBxxxFxx',
             'xxFxxxFFFxBFFFFxFFFxxxBxxxxBxxxBBBxBBBBFxBBBxxxFxx',
             'xxFxxxFFFxBFFFBxFFFxxxFxxxxFxxxBBBxFBBBBxBBBxxxBxx',
             'xxFxxxFFFxBFFFBxFFFxxxFxxxxFxxxBBBxBBBBFxBBBxxxBxx',
             'xxFxxxFFFxBFFFBxFFFxxxFxxxxFxxxBBBxBBBBBxBBBxxxFxx',
             'xxFxxxFFFxBFFFBxFFFxxxFxxxxBxxxBBBxFBBBFxBBBxxxBxx',
             'xxFxxxFFFxBFFFBxFFFxxxFxxxxBxxxBBBxFBBBBxBBBxxxFxx',
             'xxFxxxFFFxBFFFBxFFFxxxFxxxxBxxxBBBxBBBBFxBBBxxxFxx',
             'xxFxxxFFFxBFFFBxFFFxxxBxxxxFxxxBBBxFBBBFxBBBxxxBxx',
             'xxFxxxFFFxBFFFBxFFFxxxBxxxxFxxxBBBxFBBBBxBBBxxxFxx',
             'xxFxxxFFFxBFFFBxFFFxxxBxxxxFxxxBBBxBBBBFxBBBxxxFxx',
             'xxFxxxFFFxBFFFBxFFFxxxBxxxxBxxxBBBxFBBBFxBBBxxxFxx',
             'xxBxxxFFFxFFFFFxFFFxxxFxxxxFxxxBBBxBBBBBxBBBxxxBxx',
             'xxBxxxFFFxFFFFFxFFFxxxFxxxxBxxxBBBxFBBBBxBBBxxxBxx',
             'xxBxxxFFFxFFFFFxFFFxxxFxxxxBxxxBBBxBBBBFxBBBxxxBxx',
             'xxBxxxFFFxFFFFFxFFFxxxFxxxxBxxxBBBxBBBBBxBBBxxxFxx',
             'xxBxxxFFFxFFFFFxFFFxxxBxxxxFxxxBBBxFBBBBxBBBxxxBxx',
             'xxBxxxFFFxFFFFFxFFFxxxBxxxxFxxxBBBxBBBBFxBBBxxxBxx',
             'xxBxxxFFFxFFFFFxFFFxxxBxxxxFxxxBBBxBBBBBxBBBxxxFxx',
             'xxBxxxFFFxFFFFFxFFFxxxBxxxxBxxxBBBxFBBBFxBBBxxxBxx',
             'xxBxxxFFFxFFFFFxFFFxxxBxxxxBxxxBBBxFBBBBxBBBxxxFxx',
             'xxBxxxFFFxFFFFFxFFFxxxBxxxxBxxxBBBxBBBBFxBBBxxxFxx',
             'xxBxxxFFFxFFFFBxFFFxxxFxxxxFxxxBBBxFBBBBxBBBxxxBxx',
             'xxBxxxFFFxFFFFBxFFFxxxFxxxxFxxxBBBxBBBBFxBBBxxxBxx',
             'xxBxxxFFFxFFFFBxFFFxxxFxxxxFxxxBBBxBBBBBxBBBxxxFxx',
             'xxBxxxFFFxFFFFBxFFFxxxFxxxxBxxxBBBxFBBBFxBBBxxxBxx',
             'xxBxxxFFFxFFFFBxFFFxxxFxxxxBxxxBBBxFBBBBxBBBxxxFxx',
             'xxBxxxFFFxFFFFBxFFFxxxFxxxxBxxxBBBxBBBBFxBBBxxxFxx',
             'xxBxxxFFFxFFFFBxFFFxxxBxxxxFxxxBBBxFBBBFxBBBxxxBxx',
             'xxBxxxFFFxFFFFBxFFFxxxBxxxxFxxxBBBxFBBBBxBBBxxxFxx',
             'xxBxxxFFFxFFFFBxFFFxxxBxxxxFxxxBBBxBBBBFxBBBxxxFxx',
             'xxBxxxFFFxFFFFBxFFFxxxBxxxxBxxxBBBxFBBBFxBBBxxxFxx',
             'xxBxxxFFFxBFFFFxFFFxxxFxxxxFxxxBBBxFBBBBxBBBxxxBxx',
             'xxBxxxFFFxBFFFFxFFFxxxFxxxxFxxxBBBxBBBBFxBBBxxxBxx',
             'xxBxxxFFFxBFFFFxFFFxxxFxxxxFxxxBBBxBBBBBxBBBxxxFxx',
             'xxBxxxFFFxBFFFFxFFFxxxFxxxxBxxxBBBxFBBBFxBBBxxxBxx',
             'xxBxxxFFFxBFFFFxFFFxxxFxxxxBxxxBBBxFBBBBxBBBxxxFxx',
             'xxBxxxFFFxBFFFFxFFFxxxFxxxxBxxxBBBxBBBBFxBBBxxxFxx',
             'xxBxxxFFFxBFFFFxFFFxxxBxxxxFxxxBBBxFBBBFxBBBxxxBxx',
             'xxBxxxFFFxBFFFFxFFFxxxBxxxxFxxxBBBxFBBBBxBBBxxxFxx',
             'xxBxxxFFFxBFFFFxFFFxxxBxxxxFxxxBBBxBBBBFxBBBxxxFxx',
             'xxBxxxFFFxBFFFFxFFFxxxBxxxxBxxxBBBxFBBBFxBBBxxxFxx',
             'xxBxxxFFFxBFFFBxFFFxxxFxxxxFxxxBBBxFBBBFxBBBxxxBxx',
             'xxBxxxFFFxBFFFBxFFFxxxFxxxxFxxxBBBxFBBBBxBBBxxxFxx',
             'xxBxxxFFFxBFFFBxFFFxxxFxxxxFxxxBBBxBBBBFxBBBxxxFxx',
             'xxBxxxFFFxBFFFBxFFFxxxFxxxxBxxxBBBxFBBBFxBBBxxxFxx',
             'xxBxxxFFFxBFFFBxFFFxxxBxxxxFxxxBBBxFBBBFxBBBxxxFxx'),
            linecount=343000,
            max_depth=11)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Front
            'xx', parent_state[109], 'xx',
            'x', parent_state[115], parent_state[116], parent_state[117], 'x',
            parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125],
            'x', parent_state[129], parent_state[130], parent_state[131], 'x',
            'xx', parent_state[137], 'xx',

            # Back
            'xx', parent_state[207], 'xx',
            'x', parent_state[213], parent_state[214], parent_state[215], 'x',
            parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223],
            'x', parent_state[227], parent_state[228], parent_state[229], 'x',
            'xx', parent_state[235], 'xx'
        ]

        result = ['x' if x in ('U', 'D', 'L', 'R') else x for x in result]
        result = ''.join(result)

        return result


class LookupTable777FBSolveObliqueEdge(LookupTable):
    """
    lookup-table-7x7x7-step72-FB-oblique-edges.txt
    ==============================================
    1 steps has 182 entries (0 percent, 0.00x previous step)
    2 steps has 616 entries (0 percent, 3.38x previous step)
    3 steps has 2,044 entries (0 percent, 3.32x previous step)
    4 steps has 8,576 entries (2 percent, 4.20x previous step)
    5 steps has 21,516 entries (6 percent, 2.51x previous step)
    6 steps has 60,392 entries (17 percent, 2.81x previous step)
    7 steps has 105,050 entries (30 percent, 1.74x previous step)
    8 steps has 106,464 entries (31 percent, 1.01x previous step)
    9 steps has 35,772 entries (10 percent, 0.34x previous step)
    10 steps has 2,368 entries (0 percent, 0.07x previous step)
    11 steps has 20 entries (0 percent, 0.01x previous step)

    Total: 343,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step72-FB-oblique-edges.txt',
            ('xFFFxFxxxFFxxxFFxxxFxFFFxxBBBxBxxxBBxxxBBxxxBxBBBx',
             'xFFFxFxxxFFxxxFFxxxFxBBBxxFFFxBxxxBBxxxBBxxxBxBBBx',
             'xFFFxFxxxFFxxxFFxxxFxBBBxxBBBxFxxxBFxxxBFxxxBxBBBx',
             'xFFFxFxxxFFxxxFFxxxFxBBBxxBBBxBxxxFBxxxFBxxxFxBBBx',
             'xFFFxFxxxFFxxxFFxxxFxBBBxxBBBxBxxxBBxxxBBxxxBxFFFx',
             'xFFFxFxxxBFxxxBFxxxBxFFFxxFFFxBxxxBBxxxBBxxxBxBBBx',
             'xFFFxFxxxBFxxxBFxxxBxFFFxxBBBxFxxxBFxxxBFxxxBxBBBx',
             'xFFFxFxxxBFxxxBFxxxBxFFFxxBBBxBxxxFBxxxFBxxxFxBBBx',
             'xFFFxFxxxBFxxxBFxxxBxFFFxxBBBxBxxxBBxxxBBxxxBxFFFx',
             'xFFFxFxxxBFxxxBFxxxBxBBBxxFFFxFxxxBFxxxBFxxxBxBBBx',
             'xFFFxFxxxBFxxxBFxxxBxBBBxxFFFxBxxxFBxxxFBxxxFxBBBx',
             'xFFFxFxxxBFxxxBFxxxBxBBBxxFFFxBxxxBBxxxBBxxxBxFFFx',
             'xFFFxFxxxBFxxxBFxxxBxBBBxxBBBxFxxxFFxxxFFxxxFxBBBx',
             'xFFFxFxxxBFxxxBFxxxBxBBBxxBBBxFxxxBFxxxBFxxxBxFFFx',
             'xFFFxFxxxBFxxxBFxxxBxBBBxxBBBxBxxxFBxxxFBxxxFxFFFx',
             'xFFFxBxxxFBxxxFBxxxFxFFFxxFFFxBxxxBBxxxBBxxxBxBBBx',
             'xFFFxBxxxFBxxxFBxxxFxFFFxxBBBxFxxxBFxxxBFxxxBxBBBx',
             'xFFFxBxxxFBxxxFBxxxFxFFFxxBBBxBxxxFBxxxFBxxxFxBBBx',
             'xFFFxBxxxFBxxxFBxxxFxFFFxxBBBxBxxxBBxxxBBxxxBxFFFx',
             'xFFFxBxxxFBxxxFBxxxFxBBBxxFFFxFxxxBFxxxBFxxxBxBBBx',
             'xFFFxBxxxFBxxxFBxxxFxBBBxxFFFxBxxxFBxxxFBxxxFxBBBx',
             'xFFFxBxxxFBxxxFBxxxFxBBBxxFFFxBxxxBBxxxBBxxxBxFFFx',
             'xFFFxBxxxFBxxxFBxxxFxBBBxxBBBxFxxxFFxxxFFxxxFxBBBx',
             'xFFFxBxxxFBxxxFBxxxFxBBBxxBBBxFxxxBFxxxBFxxxBxFFFx',
             'xFFFxBxxxFBxxxFBxxxFxBBBxxBBBxBxxxFBxxxFBxxxFxFFFx',
             'xFFFxBxxxBBxxxBBxxxBxFFFxxFFFxFxxxBFxxxBFxxxBxBBBx',
             'xFFFxBxxxBBxxxBBxxxBxFFFxxFFFxBxxxFBxxxFBxxxFxBBBx',
             'xFFFxBxxxBBxxxBBxxxBxFFFxxFFFxBxxxBBxxxBBxxxBxFFFx',
             'xFFFxBxxxBBxxxBBxxxBxFFFxxBBBxFxxxFFxxxFFxxxFxBBBx',
             'xFFFxBxxxBBxxxBBxxxBxFFFxxBBBxFxxxBFxxxBFxxxBxFFFx',
             'xFFFxBxxxBBxxxBBxxxBxFFFxxBBBxBxxxFBxxxFBxxxFxFFFx',
             'xFFFxBxxxBBxxxBBxxxBxBBBxxFFFxFxxxFFxxxFFxxxFxBBBx',
             'xFFFxBxxxBBxxxBBxxxBxBBBxxFFFxFxxxBFxxxBFxxxBxFFFx',
             'xFFFxBxxxBBxxxBBxxxBxBBBxxFFFxBxxxFBxxxFBxxxFxFFFx',
             'xFFFxBxxxBBxxxBBxxxBxBBBxxBBBxFxxxFFxxxFFxxxFxFFFx',
             'xBBBxFxxxFFxxxFFxxxFxFFFxxFFFxBxxxBBxxxBBxxxBxBBBx',
             'xBBBxFxxxFFxxxFFxxxFxFFFxxBBBxFxxxBFxxxBFxxxBxBBBx',
             'xBBBxFxxxFFxxxFFxxxFxFFFxxBBBxBxxxFBxxxFBxxxFxBBBx',
             'xBBBxFxxxFFxxxFFxxxFxFFFxxBBBxBxxxBBxxxBBxxxBxFFFx',
             'xBBBxFxxxFFxxxFFxxxFxBBBxxFFFxFxxxBFxxxBFxxxBxBBBx',
             'xBBBxFxxxFFxxxFFxxxFxBBBxxFFFxBxxxFBxxxFBxxxFxBBBx',
             'xBBBxFxxxFFxxxFFxxxFxBBBxxFFFxBxxxBBxxxBBxxxBxFFFx',
             'xBBBxFxxxFFxxxFFxxxFxBBBxxBBBxFxxxFFxxxFFxxxFxBBBx',
             'xBBBxFxxxFFxxxFFxxxFxBBBxxBBBxFxxxBFxxxBFxxxBxFFFx',
             'xBBBxFxxxFFxxxFFxxxFxBBBxxBBBxBxxxFBxxxFBxxxFxFFFx',
             'xBBBxFxxxBFxxxBFxxxBxFFFxxFFFxFxxxBFxxxBFxxxBxBBBx',
             'xBBBxFxxxBFxxxBFxxxBxFFFxxFFFxBxxxFBxxxFBxxxFxBBBx',
             'xBBBxFxxxBFxxxBFxxxBxFFFxxFFFxBxxxBBxxxBBxxxBxFFFx',
             'xBBBxFxxxBFxxxBFxxxBxFFFxxBBBxFxxxFFxxxFFxxxFxBBBx',
             'xBBBxFxxxBFxxxBFxxxBxFFFxxBBBxFxxxBFxxxBFxxxBxFFFx',
             'xBBBxFxxxBFxxxBFxxxBxFFFxxBBBxBxxxFBxxxFBxxxFxFFFx',
             'xBBBxFxxxBFxxxBFxxxBxBBBxxFFFxFxxxFFxxxFFxxxFxBBBx',
             'xBBBxFxxxBFxxxBFxxxBxBBBxxFFFxFxxxBFxxxBFxxxBxFFFx',
             'xBBBxFxxxBFxxxBFxxxBxBBBxxFFFxBxxxFBxxxFBxxxFxFFFx',
             'xBBBxFxxxBFxxxBFxxxBxBBBxxBBBxFxxxFFxxxFFxxxFxFFFx',
             'xBBBxBxxxFBxxxFBxxxFxFFFxxFFFxFxxxBFxxxBFxxxBxBBBx',
             'xBBBxBxxxFBxxxFBxxxFxFFFxxFFFxBxxxFBxxxFBxxxFxBBBx',
             'xBBBxBxxxFBxxxFBxxxFxFFFxxFFFxBxxxBBxxxBBxxxBxFFFx',
             'xBBBxBxxxFBxxxFBxxxFxFFFxxBBBxFxxxFFxxxFFxxxFxBBBx',
             'xBBBxBxxxFBxxxFBxxxFxFFFxxBBBxFxxxBFxxxBFxxxBxFFFx',
             'xBBBxBxxxFBxxxFBxxxFxFFFxxBBBxBxxxFBxxxFBxxxFxFFFx',
             'xBBBxBxxxFBxxxFBxxxFxBBBxxFFFxFxxxFFxxxFFxxxFxBBBx',
             'xBBBxBxxxFBxxxFBxxxFxBBBxxFFFxFxxxBFxxxBFxxxBxFFFx',
             'xBBBxBxxxFBxxxFBxxxFxBBBxxFFFxBxxxFBxxxFBxxxFxFFFx',
             'xBBBxBxxxFBxxxFBxxxFxBBBxxBBBxFxxxFFxxxFFxxxFxFFFx',
             'xBBBxBxxxBBxxxBBxxxBxFFFxxFFFxFxxxFFxxxFFxxxFxBBBx',
             'xBBBxBxxxBBxxxBBxxxBxFFFxxFFFxFxxxBFxxxBFxxxBxFFFx',
             'xBBBxBxxxBBxxxBBxxxBxFFFxxFFFxBxxxFBxxxFBxxxFxFFFx',
             'xBBBxBxxxBBxxxBBxxxBxFFFxxBBBxFxxxFFxxxFFxxxFxFFFx',
             'xBBBxBxxxBBxxxBBxxxBxBBBxxFFFxFxxxFFxxxFFxxxFxFFFx'),
            linecount=343000,
            max_depth=11)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Front
            'x', parent_state[108], parent_state[109], parent_state[110], 'x',
            parent_state[114], 'xxx', parent_state[118],
            parent_state[121], 'xxx', parent_state[125],
            parent_state[128], 'xxx', parent_state[132],
            'x', parent_state[136], parent_state[137], parent_state[138], 'x',

            # Back
            'x', parent_state[206], parent_state[207], parent_state[208], 'x',
            parent_state[212], 'xxx', parent_state[216],
            parent_state[219], 'xxx', parent_state[223],
            parent_state[226], 'xxx', parent_state[230],
            'x', parent_state[234], parent_state[235], parent_state[236], 'x'
        ]

        result = ['x' if x in ('U', 'D', 'L', 'R') else x for x in result]
        result = ''.join(result)

        return result


class LookupTableIDA777FBSolveInnerCentersAndObliqueEdges(LookupTableIDA):
    """
    lookup-table-7x7x7-step70-FB-solve-inner-center-and-oblique-edges.txt
    =====================================================================
    1 steps has 210 entries (0 percent, 0.00x previous step)
    2 steps has 770 entries (0 percent, 3.67x previous step)
    3 steps has 2,828 entries (0 percent, 3.67x previous step)
    4 steps has 15,158 entries (0 percent, 5.36x previous step)
    5 steps has 63,008 entries (0 percent, 4.16x previous step)
    6 steps has 290,588 entries (4 percent, 4.61x previous step)
    7 steps has 1,232,594 entries (17 percent, 4.24x previous step)
    8 steps has 5,266,642 entries (76 percent, 4.27x previous step)

    Total: 6,871,798 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step70-FB-solve-inner-center-and-oblique-edges.txt',
            ('xFFFxFFFFFFFFFFFFFFFxFFFxxBBBxBBBBBBBBBBBBBBBxBBBx',
             'xFFFxFFFFFFFFFFFFFFFxBBBxxFFFxBBBBBBBBBBBBBBBxBBBx',
             'xFFFxFFFFFFFFFFFFFFFxBBBxxBBBxFBBBBFBBBBFBBBBxBBBx',
             'xFFFxFFFFFFFFFFFFFFFxBBBxxBBBxBBBBFBBBBFBBBBFxBBBx',
             'xFFFxFFFFFFFFFFFFFFFxBBBxxBBBxBBBBBBBBBBBBBBBxFFFx',
             'xFFFxFFFFBFFFFBFFFFBxFFFxxFFFxBBBBBBBBBBBBBBBxBBBx',
             'xFFFxFFFFBFFFFBFFFFBxFFFxxBBBxFBBBBFBBBBFBBBBxBBBx',
             'xFFFxFFFFBFFFFBFFFFBxFFFxxBBBxBBBBFBBBBFBBBBFxBBBx',
             'xFFFxFFFFBFFFFBFFFFBxFFFxxBBBxBBBBBBBBBBBBBBBxFFFx',
             'xFFFxFFFFBFFFFBFFFFBxBBBxxFFFxFBBBBFBBBBFBBBBxBBBx',
             'xFFFxFFFFBFFFFBFFFFBxBBBxxFFFxBBBBFBBBBFBBBBFxBBBx',
             'xFFFxFFFFBFFFFBFFFFBxBBBxxFFFxBBBBBBBBBBBBBBBxFFFx',
             'xFFFxFFFFBFFFFBFFFFBxBBBxxBBBxFBBBFFBBBFFBBBFxBBBx',
             'xFFFxFFFFBFFFFBFFFFBxBBBxxBBBxFBBBBFBBBBFBBBBxFFFx',
             'xFFFxFFFFBFFFFBFFFFBxBBBxxBBBxBBBBFBBBBFBBBBFxFFFx',
             'xFFFxBFFFFBFFFFBFFFFxFFFxxFFFxBBBBBBBBBBBBBBBxBBBx',
             'xFFFxBFFFFBFFFFBFFFFxFFFxxBBBxFBBBBFBBBBFBBBBxBBBx',
             'xFFFxBFFFFBFFFFBFFFFxFFFxxBBBxBBBBFBBBBFBBBBFxBBBx',
             'xFFFxBFFFFBFFFFBFFFFxFFFxxBBBxBBBBBBBBBBBBBBBxFFFx',
             'xFFFxBFFFFBFFFFBFFFFxBBBxxFFFxFBBBBFBBBBFBBBBxBBBx',
             'xFFFxBFFFFBFFFFBFFFFxBBBxxFFFxBBBBFBBBBFBBBBFxBBBx',
             'xFFFxBFFFFBFFFFBFFFFxBBBxxFFFxBBBBBBBBBBBBBBBxFFFx',
             'xFFFxBFFFFBFFFFBFFFFxBBBxxBBBxFBBBFFBBBFFBBBFxBBBx',
             'xFFFxBFFFFBFFFFBFFFFxBBBxxBBBxFBBBBFBBBBFBBBBxFFFx',
             'xFFFxBFFFFBFFFFBFFFFxBBBxxBBBxBBBBFBBBBFBBBBFxFFFx',
             'xFFFxBFFFBBFFFBBFFFBxFFFxxFFFxFBBBBFBBBBFBBBBxBBBx',
             'xFFFxBFFFBBFFFBBFFFBxFFFxxFFFxBBBBFBBBBFBBBBFxBBBx',
             'xFFFxBFFFBBFFFBBFFFBxFFFxxFFFxBBBBBBBBBBBBBBBxFFFx',
             'xFFFxBFFFBBFFFBBFFFBxFFFxxBBBxFBBBFFBBBFFBBBFxBBBx',
             'xFFFxBFFFBBFFFBBFFFBxFFFxxBBBxFBBBBFBBBBFBBBBxFFFx',
             'xFFFxBFFFBBFFFBBFFFBxFFFxxBBBxBBBBFBBBBFBBBBFxFFFx',
             'xFFFxBFFFBBFFFBBFFFBxBBBxxFFFxFBBBFFBBBFFBBBFxBBBx',
             'xFFFxBFFFBBFFFBBFFFBxBBBxxFFFxFBBBBFBBBBFBBBBxFFFx',
             'xFFFxBFFFBBFFFBBFFFBxBBBxxFFFxBBBBFBBBBFBBBBFxFFFx',
             'xFFFxBFFFBBFFFBBFFFBxBBBxxBBBxFBBBFFBBBFFBBBFxFFFx',
             'xBBBxFFFFFFFFFFFFFFFxFFFxxFFFxBBBBBBBBBBBBBBBxBBBx',
             'xBBBxFFFFFFFFFFFFFFFxFFFxxBBBxFBBBBFBBBBFBBBBxBBBx',
             'xBBBxFFFFFFFFFFFFFFFxFFFxxBBBxBBBBFBBBBFBBBBFxBBBx',
             'xBBBxFFFFFFFFFFFFFFFxFFFxxBBBxBBBBBBBBBBBBBBBxFFFx',
             'xBBBxFFFFFFFFFFFFFFFxBBBxxFFFxFBBBBFBBBBFBBBBxBBBx',
             'xBBBxFFFFFFFFFFFFFFFxBBBxxFFFxBBBBFBBBBFBBBBFxBBBx',
             'xBBBxFFFFFFFFFFFFFFFxBBBxxFFFxBBBBBBBBBBBBBBBxFFFx',
             'xBBBxFFFFFFFFFFFFFFFxBBBxxBBBxFBBBFFBBBFFBBBFxBBBx',
             'xBBBxFFFFFFFFFFFFFFFxBBBxxBBBxFBBBBFBBBBFBBBBxFFFx',
             'xBBBxFFFFFFFFFFFFFFFxBBBxxBBBxBBBBFBBBBFBBBBFxFFFx',
             'xBBBxFFFFBFFFFBFFFFBxFFFxxFFFxFBBBBFBBBBFBBBBxBBBx',
             'xBBBxFFFFBFFFFBFFFFBxFFFxxFFFxBBBBFBBBBFBBBBFxBBBx',
             'xBBBxFFFFBFFFFBFFFFBxFFFxxFFFxBBBBBBBBBBBBBBBxFFFx',
             'xBBBxFFFFBFFFFBFFFFBxFFFxxBBBxFBBBFFBBBFFBBBFxBBBx',
             'xBBBxFFFFBFFFFBFFFFBxFFFxxBBBxFBBBBFBBBBFBBBBxFFFx',
             'xBBBxFFFFBFFFFBFFFFBxFFFxxBBBxBBBBFBBBBFBBBBFxFFFx',
             'xBBBxFFFFBFFFFBFFFFBxBBBxxFFFxFBBBFFBBBFFBBBFxBBBx',
             'xBBBxFFFFBFFFFBFFFFBxBBBxxFFFxFBBBBFBBBBFBBBBxFFFx',
             'xBBBxFFFFBFFFFBFFFFBxBBBxxFFFxBBBBFBBBBFBBBBFxFFFx',
             'xBBBxFFFFBFFFFBFFFFBxBBBxxBBBxFBBBFFBBBFFBBBFxFFFx',
             'xBBBxBFFFFBFFFFBFFFFxFFFxxFFFxFBBBBFBBBBFBBBBxBBBx',
             'xBBBxBFFFFBFFFFBFFFFxFFFxxFFFxBBBBFBBBBFBBBBFxBBBx',
             'xBBBxBFFFFBFFFFBFFFFxFFFxxFFFxBBBBBBBBBBBBBBBxFFFx',
             'xBBBxBFFFFBFFFFBFFFFxFFFxxBBBxFBBBFFBBBFFBBBFxBBBx',
             'xBBBxBFFFFBFFFFBFFFFxFFFxxBBBxFBBBBFBBBBFBBBBxFFFx',
             'xBBBxBFFFFBFFFFBFFFFxFFFxxBBBxBBBBFBBBBFBBBBFxFFFx',
             'xBBBxBFFFFBFFFFBFFFFxBBBxxFFFxFBBBFFBBBFFBBBFxBBBx',
             'xBBBxBFFFFBFFFFBFFFFxBBBxxFFFxFBBBBFBBBBFBBBBxFFFx',
             'xBBBxBFFFFBFFFFBFFFFxBBBxxFFFxBBBBFBBBBFBBBBFxFFFx',
             'xBBBxBFFFFBFFFFBFFFFxBBBxxBBBxFBBBFFBBBFFBBBFxFFFx',
             'xBBBxBFFFBBFFFBBFFFBxFFFxxFFFxFBBBFFBBBFFBBBFxBBBx',
             'xBBBxBFFFBBFFFBBFFFBxFFFxxFFFxFBBBBFBBBBFBBBBxFFFx',
             'xBBBxBFFFBBFFFBBFFFBxFFFxxFFFxBBBBFBBBBFBBBBFxFFFx',
             'xBBBxBFFFBBFFFBBFFFBxFFFxxBBBxFBBBFFBBBFFBBBFxFFFx',
             'xBBBxBFFFBBFFFBBFFFBxBBBxxFFFxFBBBFFBBBFFBBBFxFFFx'),
            moves_7x7x7,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
             "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
             "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2",                               # do not mess up solved UD
             "L", "L'", "L2", "R", "R'", "R2"),                                                        # no point rotating L or R here

            # prune tables
            (parent.lt_FB_solve_inner_x_center_t_center_middle_oblique_edge,
             parent.lt_FB_solve_oblique_edge),
            linecount=6871798,
            max_depth=8)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Front
            'x', parent_state[108], parent_state[109], parent_state[110], 'x',
            parent_state[114], parent_state[115], parent_state[116], parent_state[117], parent_state[118],
            parent_state[121], parent_state[122], parent_state[123], parent_state[124], parent_state[125],
            parent_state[128], parent_state[129], parent_state[130], parent_state[131], parent_state[132],
            'x', parent_state[136], parent_state[137], parent_state[138], 'x',

            # Back
            'x', parent_state[206], parent_state[207], parent_state[208], 'x',
            parent_state[212], parent_state[213], parent_state[214], parent_state[215], parent_state[216],
            parent_state[219], parent_state[220], parent_state[221], parent_state[222], parent_state[223],
            parent_state[226], parent_state[227], parent_state[228], parent_state[229], parent_state[230],
            'x', parent_state[234], parent_state[235], parent_state[236], 'x'
        ]

        result = ['x' if x in ('U', 'D', 'L', 'R') else x for x in result]
        result = ''.join(result)

        return result


class LookupTableIDA777LFRBSolveInnerCenters(LookupTable):
    """
    lookup-table-7x7x7-step81-LFRB-solve-inner-centers.txt
    ======================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 25 entries (0 percent, 8.33x previous step)
    3 steps has 146 entries (0 percent, 5.84x previous step)
    4 steps has 544 entries (0 percent, 3.73x previous step)
    5 steps has 2,772 entries (0 percent, 5.10x previous step)
    6 steps has 13,681 entries (0 percent, 4.94x previous step)
    7 steps has 57,790 entries (0 percent, 4.22x previous step)
    8 steps has 227,221 entries (0 percent, 3.93x previous step)
    9 steps has 797,842 entries (3 percent, 3.51x previous step)
    10 steps has 2,318,392 entries (9 percent, 2.91x previous step)
    11 steps has 5,327,072 entries (22 percent, 2.30x previous step)
    12 steps has 7,922,750 entries (32 percent, 1.49x previous step)
    13 steps has 5,770,345 entries (24 percent, 0.73x previous step)
    14 steps has 1,498,471 entries (6 percent, 0.26x previous step)
    15 steps has 71,950 entries (0 percent, 0.05x previous step)
    16 steps has 998 entries (0 percent, 0.01x previous step)
    17 steps has 3 entries (0 percent, 0.00x previous step)

    Total: 24,010,005 entries
    Average: 11.805268 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step81-LFRB-solve-inner-centers.txt',
            'LLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBB',
            linecount=24010005,
            max_depth=17)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            parent_state[66], parent_state[67], parent_state[68],
            parent_state[73], parent_state[74], parent_state[75],
            parent_state[80], parent_state[81], parent_state[82],

            # Front
            parent_state[115], parent_state[116], parent_state[117],
            parent_state[122], parent_state[123], parent_state[124],
            parent_state[129], parent_state[130], parent_state[131],

            # Right
            parent_state[164], parent_state[165], parent_state[166],
            parent_state[171], parent_state[172], parent_state[173],
            parent_state[178], parent_state[179], parent_state[180],

            # Back
            parent_state[213], parent_state[214], parent_state[215],
            parent_state[220], parent_state[221], parent_state[222],
            parent_state[227], parent_state[228], parent_state[229],
        ]

        result = ''.join(result)
        return result


class LookupTableIDA777LFRBSolveInnerCentersAndObliqueEdges(LookupTableIDA):
    """
    lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt
    =======================================================================
    1 steps has 2,993 entries (0 percent, 0.00x previous step)
    2 steps has 19,085 entries (0 percent, 6.38x previous step)
    3 steps has 148,529 entries (0 percent, 7.78x previous step)
    4 steps has 1,054,714 entries (1 percent, 7.10x previous step)
    5 steps has 7,566,773 entries (11 percent, 7.17x previous step)
    6 steps has 54,349,943 entries (86 percent, 7.18x previous step)

    Total: 63,142,037 entries
    Average: 5.838252 moves
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt',
            lt_LFRB_solve_inner_centers_and_oblique_edges_state_targets, # There are 4900 of them
            moves_7x7x7,

            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
             "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers

             # 6-deep partial
             "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2",                               # do not mess up solved UD
             "L", "L'", "L2", "R", "R'", "R2"),                                                        # Do not mess up LRs reduced to 5x5x5 centers

            # prune tables
            (parent.lt_LR_solve_inner_x_center_t_center_middle_oblique_edge,
             parent.lt_LR_solve_oblique_edge,
             parent.lt_FB_solve_inner_x_center_t_center_middle_oblique_edge,
             parent.lt_FB_solve_oblique_edge,
             parent.lt_LFRB_solve_inner_centers,

             parent.lt_LR_solve_inner_centers_and_oblique_edges,
             parent.lt_FB_solve_inner_centers_and_oblique_edges,
            ),

            linecount=63142037,  # 6-deep partial
            max_depth=6)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'F') else '0' for x in step80_centers_777])

        # Convert to hex
        return self.hex_format % int(result, 2)


class RubiksCube777(RubiksCubeNNNOddEdges):
    """
    For 7x7x7 centers
    - stage the UD inside 9 centers via 5x5x5
    - UD oblique edges
        - pair the two outside oblique edges via 6x6x6
        - build a lookup table to pair the middle oblique edges with the two
          outside oblique edges. The restriction being that if you do a 3Lw move
          you must also do a 3Rw' in order to keep the two outside oblique edges
          paired up...so it is a slice of the layer in the middle. This table
          should be (24!/(8!*16!))^2 or 540,917,591,800 so use IDA.
    - stage the rest of the UD centers via 5x5x5
    - stage the LR inside 9 centers via 5x5x5
    - LR oblique edges...use the same strategy as UD oblique edges
    - stage the rest of the LR centers via 5x5x5

    - solve the UD centers...this is (8!/(4!*4!))^6 or 117 billion so use IDA
    - solve the LR centers
    - solve the LR and FB centers

    For 7x7x7 edges
    - pair the middle 3 wings for each side via 5x5x5
    - pair the outer 2 wings with the paired middle 3 wings via 5x5x5


    Inheritance model
    -----------------
            RubiksCube
                |
        RubiksCubeNNNOddEdges
           /            \
    RubiksCubeNNNOdd RubiksCube777

    """

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
        edge_orbit_0 = (2, 6, 14, 42, 48, 44, 36, 8,
                        51, 55, 63, 91, 97, 93, 85, 57,
                        100, 104, 112, 140, 146, 142, 134, 106,
                        149, 153, 161, 189, 195, 191, 183, 155,
                        198, 202, 210, 238, 244, 240, 232, 204,
                        247, 251, 259, 287, 293, 289, 281, 253)

        edge_orbit_1 = (3, 5, 21, 35, 47, 45, 29, 15,
                        52, 54, 70, 84, 96, 94, 78, 64,
                        101, 103, 119, 133, 145, 143, 127, 113,
                        150, 152, 168, 182, 194, 192, 176, 162,
                        199, 201, 217, 231, 243, 241, 225, 211,
                        248, 250, 266, 280, 292, 290, 274, 260)

        edge_orbit_2 = (4, 28, 46, 22,
                        53, 77, 95, 71,
                        102, 126, 144, 120,
                        151, 175, 193, 169,
                        200, 224, 242, 218,
                        249, 273, 291, 267)

        corners = (1, 7, 43, 49,
                   50, 56, 92, 98,
                   99, 105, 141, 147,
                   148, 154, 190, 196,
                   197, 203, 239, 245,
                   246, 252, 288, 294)

        left_oblique_edge = (10, 20, 40, 30,
                             59, 69, 89, 79,
                             108, 118, 138, 128,
                             157, 167, 187, 177,
                             206, 216, 236, 226,
                             255, 265, 285, 275)

        right_oblique_edge = (12, 34, 38, 16,
                              61, 83, 87, 65,
                              110, 132, 136, 114,
                              159, 181, 185, 163,
                              208, 230, 234, 212,
                              257, 279, 283, 261)

        outside_x_centers = (9, 13, 37, 41,
                             58, 62, 86, 90,
                             107, 111, 135, 139,
                             156, 160, 184, 188,
                             205, 209, 233, 237,
                             254, 258, 282, 286)

        inside_x_centers = (17, 19, 31, 33,
                            66, 68, 80, 82,
                            115, 117, 129, 131,
                            164, 166, 178, 180,
                            213, 215, 227, 229,
                            262, 264, 276, 278)

        outside_t_centers = (11, 23, 27, 39,
                             60, 72, 76, 88,
                             109, 121, 125, 137,
                             158, 170, 174, 186,
                             207, 219, 223, 235,
                             256, 268, 272, 284)

        inside_t_centers = (18, 24, 26, 32,
                            67, 73, 75, 81,
                            116, 122, 124, 130,
                            165, 171, 173, 179,
                            214, 220, 222, 228,
                            263, 269, 271, 277)

        centers = (25, 74, 123, 172, 221, 270)

        self._sanity_check('edge-orbit-0', edge_orbit_0, 8)
        self._sanity_check('edge-orbit-1', edge_orbit_1, 8)
        self._sanity_check('edge-orbit-2', edge_orbit_2, 4)
        self._sanity_check('corners', corners, 4)
        self._sanity_check('left-oblique', left_oblique_edge, 4)
        self._sanity_check('right-oblique', right_oblique_edge, 4)
        self._sanity_check('outside x-centers', outside_x_centers, 4)
        self._sanity_check('inside x-centers', inside_x_centers, 4)
        self._sanity_check('outside t-centers', outside_t_centers, 4)
        self._sanity_check('inside t-centers', inside_t_centers, 4)
        self._sanity_check('centers', centers, 1)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_UD_oblique_edge_pairing_middle_only = LookupTable777UDObliqueEdgePairingMiddleOnly(self)
        self.lt_UD_oblique_edge_pairing_left_only = LookupTable777UDObliqueEdgePairingLeftOnly(self)
        self.lt_UD_oblique_edge_pairing_right_only = LookupTable777UDObliqueEdgePairingRightOnly(self)
        self.lt_UD_oblique_edge_pairing = LookupTableIDA777UDObliqueEdgePairing(self)

        self.lt_LR_oblique_edge_pairing_middle_only = LookupTable777LRObliqueEdgePairingMiddleOnly(self)
        self.lt_LR_oblique_edge_pairing_left_only = LookupTable777LRObliqueEdgePairingLeftOnly(self)
        self.lt_LR_oblique_edge_pairing_right_only = LookupTable777LRObliqueEdgePairingRightOnly(self)
        self.lt_LR_oblique_edge_pairing = LookupTableIDA777LRObliqueEdgePairing(self)

        self.lt_UD_solve_inner_centers_and_oblique_edges_center_only = LookupTable777UDSolveInnerCentersAndObliqueEdgesCenterOnly(self)
        self.lt_UD_solve_inner_centers_and_oblique_edges_edges_only = LookupTable777UDSolveInnerCentersAndObliqueEdgesEdgesOnly(self)
        self.lt_UD_solve_inner_centers_and_oblique_edges = LookupTableIDA777UDSolveInnerCentersAndObliqueEdges(self)

        self.lt_LR_solve_inner_x_center_t_center_middle_oblique_edge = LookupTable777LRSolveInnerXCenterTCenterMiddleObliqueEdge(self)
        self.lt_LR_solve_oblique_edge = LookupTable777LRSolveObliqueEdge(self)
        self.lt_LR_solve_inner_centers_and_oblique_edges = LookupTableIDA777LRSolveInnerCentersAndObliqueEdges(self)

        self.lt_FB_solve_inner_x_center_t_center_middle_oblique_edge = LookupTable777FBSolveInnerXCenterTCenterMiddleObliqueEdge(self)
        self.lt_FB_solve_oblique_edge = LookupTable777FBSolveObliqueEdge(self)
        self.lt_FB_solve_inner_centers_and_oblique_edges = LookupTableIDA777FBSolveInnerCentersAndObliqueEdges(self)

        self.lt_LFRB_solve_inner_centers = LookupTableIDA777LFRBSolveInnerCenters(self)
        self.lt_LFRB_solve_inner_centers_and_oblique_edges = LookupTableIDA777LFRBSolveInnerCentersAndObliqueEdges(self)

    def create_fake_555_for_LR_t_centers(self):

        # Create a fake 5x5x5 to stage the UD inner 5x5x5 centers
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.lt_init()

        for x in range(1, 151):
            fake_555.state[x] = 'x'

        # Left
        fake_555.state[33] = self.state[60]
        fake_555.state[37] = self.state[72]
        fake_555.state[39] = self.state[76]
        fake_555.state[43] = self.state[88]

        # Right
        fake_555.state[83] = self.state[158]
        fake_555.state[87] = self.state[170]
        fake_555.state[89] = self.state[174]
        fake_555.state[93] = self.state[186]

        return fake_555

    def create_fake_555_from_inside_centers(self):

        # Create a fake 5x5x5 to stage the UD inner 5x5x5 centers
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.lt_init()

        for x in range(1, 151):
            fake_555.state[x] = 'x'

        # Upper
        fake_555.state[7] = self.state[17]
        fake_555.state[8] = self.state[18]
        fake_555.state[9] = self.state[19]
        fake_555.state[12] = self.state[24]
        fake_555.state[13] = self.state[25]
        fake_555.state[14] = self.state[26]
        fake_555.state[17] = self.state[31]
        fake_555.state[18] = self.state[32]
        fake_555.state[19] = self.state[33]

        # Left
        fake_555.state[32] = self.state[66]
        fake_555.state[33] = self.state[67]
        fake_555.state[34] = self.state[68]
        fake_555.state[37] = self.state[73]
        fake_555.state[38] = self.state[74]
        fake_555.state[39] = self.state[75]
        fake_555.state[42] = self.state[80]
        fake_555.state[43] = self.state[81]
        fake_555.state[44] = self.state[82]

        # Front
        fake_555.state[57] = self.state[115]
        fake_555.state[58] = self.state[116]
        fake_555.state[59] = self.state[117]
        fake_555.state[62] = self.state[122]
        fake_555.state[63] = self.state[123]
        fake_555.state[64] = self.state[124]
        fake_555.state[67] = self.state[129]
        fake_555.state[68] = self.state[130]
        fake_555.state[69] = self.state[131]

        # Right
        fake_555.state[82] = self.state[164]
        fake_555.state[83] = self.state[165]
        fake_555.state[84] = self.state[166]
        fake_555.state[87] = self.state[171]
        fake_555.state[88] = self.state[172]
        fake_555.state[89] = self.state[173]
        fake_555.state[92] = self.state[178]
        fake_555.state[93] = self.state[179]
        fake_555.state[94] = self.state[180]

        # Back
        fake_555.state[107] = self.state[213]
        fake_555.state[108] = self.state[214]
        fake_555.state[109] = self.state[215]
        fake_555.state[112] = self.state[220]
        fake_555.state[113] = self.state[221]
        fake_555.state[114] = self.state[222]
        fake_555.state[117] = self.state[227]
        fake_555.state[118] = self.state[228]
        fake_555.state[119] = self.state[229]

        # Down
        fake_555.state[132] = self.state[262]
        fake_555.state[133] = self.state[263]
        fake_555.state[134] = self.state[264]
        fake_555.state[137] = self.state[269]
        fake_555.state[138] = self.state[270]
        fake_555.state[139] = self.state[271]
        fake_555.state[142] = self.state[276]
        fake_555.state[143] = self.state[277]
        fake_555.state[144] = self.state[278]
        fake_555.sanity_check()

        return fake_555

    def create_fake_555_from_outside_centers(self):

        # Create a fake 5x5x5 to solve 7x7x7 centers (they have been reduced to a 5x5x5)
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.lt_init()

        for x in range(1, 151):
            fake_555.state[x] = 'x'

        # Upper
        fake_555.state[7] = self.state[9]
        fake_555.state[8] = self.state[11]
        fake_555.state[9] = self.state[13]
        fake_555.state[12] = self.state[23]
        fake_555.state[13] = self.state[25]
        fake_555.state[14] = self.state[27]
        fake_555.state[17] = self.state[37]
        fake_555.state[18] = self.state[39]
        fake_555.state[19] = self.state[41]

        # Left
        fake_555.state[32] = self.state[58]
        fake_555.state[33] = self.state[60]
        fake_555.state[34] = self.state[62]
        fake_555.state[37] = self.state[72]
        fake_555.state[38] = self.state[74]
        fake_555.state[39] = self.state[76]
        fake_555.state[42] = self.state[86]
        fake_555.state[43] = self.state[88]
        fake_555.state[44] = self.state[90]

        # Front
        fake_555.state[57] = self.state[107]
        fake_555.state[58] = self.state[109]
        fake_555.state[59] = self.state[111]
        fake_555.state[62] = self.state[121]
        fake_555.state[63] = self.state[123]
        fake_555.state[64] = self.state[125]
        fake_555.state[67] = self.state[135]
        fake_555.state[68] = self.state[137]
        fake_555.state[69] = self.state[139]

        # Right
        fake_555.state[82] = self.state[156]
        fake_555.state[83] = self.state[158]
        fake_555.state[84] = self.state[160]
        fake_555.state[87] = self.state[170]
        fake_555.state[88] = self.state[172]
        fake_555.state[89] = self.state[174]
        fake_555.state[92] = self.state[184]
        fake_555.state[93] = self.state[186]
        fake_555.state[94] = self.state[188]

        # Back
        fake_555.state[107] = self.state[205]
        fake_555.state[108] = self.state[207]
        fake_555.state[109] = self.state[209]
        fake_555.state[112] = self.state[219]
        fake_555.state[113] = self.state[221]
        fake_555.state[114] = self.state[223]
        fake_555.state[117] = self.state[233]
        fake_555.state[118] = self.state[235]
        fake_555.state[119] = self.state[237]

        # Down
        fake_555.state[132] = self.state[254]
        fake_555.state[133] = self.state[256]
        fake_555.state[134] = self.state[258]
        fake_555.state[137] = self.state[268]
        fake_555.state[138] = self.state[270]
        fake_555.state[139] = self.state[272]
        fake_555.state[142] = self.state[282]
        fake_555.state[143] = self.state[284]
        fake_555.state[144] = self.state[286]
        fake_555.sanity_check()

        return fake_555

    def group_inside_UD_centers(self):
        fake_555 = self.create_fake_555_from_inside_centers()
        fake_555.group_centers_stage_UD()

        for step in fake_555.solution:

            if step.startswith('5'):
                step = '7' + step[1:]
            elif step.startswith('3'):
                step = '4' + step[1:]
            elif 'w' in step:
                step = '3' + step

            self.rotate(step)

    def group_inside_LR_centers(self):
        fake_555 = self.create_fake_555_from_inside_centers()
        fake_555.lt_LR_centers_stage.solve()

        for step in fake_555.solution:

            if step.startswith('5'):
                step = '7' + step[1:]
            elif step.startswith('3'):
                raise Exception("5x5x5 solution has 3 wide turn")
            elif 'w' in step:
                step = '3' + step

            self.rotate(step)

    def solve_reduced_555_centers(self):
        fake_555 = self.create_fake_555_from_outside_centers()
        fake_555.group_centers()

        for step in fake_555.solution:

            if step == 'CENTERS_SOLVED':
                continue

            if step.startswith('5'):
                step = '7' + step[1:]

            elif step.startswith('3'):
                raise Exception("5x5x5 solution has 3 wide turn")

            self.rotate(step)

    def solve_reduced_555_t_centers(self):
        fake_555 = self.create_fake_555_from_outside_centers()
        fake_555.lt_ULFRBD_t_centers_solve.solve()

        for step in fake_555.solution:

            if step == 'CENTERS_SOLVED':
                continue

            if step.startswith('5'):
                step = '7' + step[1:]

            elif step.startswith('3'):
                raise Exception("5x5x5 solution has 3 wide turn")

            self.rotate(step)

    def create_fake_666_centers(self):

        # Create a fake 6x6x6 to stage the outside UD oblique edges
        fake_666 = RubiksCube666(solved_6x6x6, 'URFDLB')
        fake_666.lt_init()

        for x in range(1, 217):
            fake_666.state[x] = 'x'

        # Upper
        fake_666.state[8] = self.state[9]
        fake_666.state[9] = self.state[10]
        fake_666.state[10] = self.state[12]
        fake_666.state[11] = self.state[13]

        fake_666.state[14] = self.state[16]
        fake_666.state[15] = self.state[17]
        fake_666.state[16] = self.state[19]
        fake_666.state[17] = self.state[20]

        fake_666.state[20] = self.state[30]
        fake_666.state[21] = self.state[31]
        fake_666.state[22] = self.state[33]
        fake_666.state[23] = self.state[34]

        fake_666.state[26] = self.state[37]
        fake_666.state[27] = self.state[38]
        fake_666.state[28] = self.state[40]
        fake_666.state[29] = self.state[41]

        # Left
        fake_666.state[44] = self.state[58]
        fake_666.state[45] = self.state[59]
        fake_666.state[46] = self.state[61]
        fake_666.state[47] = self.state[62]
        fake_666.state[50] = self.state[65]
        fake_666.state[51] = self.state[66]
        fake_666.state[52] = self.state[68]
        fake_666.state[53] = self.state[69]
        fake_666.state[56] = self.state[79]
        fake_666.state[57] = self.state[80]
        fake_666.state[58] = self.state[82]
        fake_666.state[59] = self.state[83]
        fake_666.state[62] = self.state[86]
        fake_666.state[63] = self.state[87]
        fake_666.state[64] = self.state[89]
        fake_666.state[65] = self.state[90]

        # Front
        fake_666.state[80] = self.state[107]
        fake_666.state[81] = self.state[108]
        fake_666.state[82] = self.state[110]
        fake_666.state[83] = self.state[111]
        fake_666.state[86] = self.state[114]
        fake_666.state[87] = self.state[115]
        fake_666.state[88] = self.state[117]
        fake_666.state[89] = self.state[118]
        fake_666.state[92] = self.state[128]
        fake_666.state[93] = self.state[129]
        fake_666.state[94] = self.state[131]
        fake_666.state[95] = self.state[132]
        fake_666.state[98] = self.state[135]
        fake_666.state[99] = self.state[136]
        fake_666.state[100] = self.state[138]
        fake_666.state[101] = self.state[139]

        # Right
        fake_666.state[116] = self.state[156]
        fake_666.state[117] = self.state[157]
        fake_666.state[118] = self.state[159]
        fake_666.state[119] = self.state[160]
        fake_666.state[122] = self.state[163]
        fake_666.state[123] = self.state[164]
        fake_666.state[124] = self.state[166]
        fake_666.state[125] = self.state[167]
        fake_666.state[128] = self.state[177]
        fake_666.state[129] = self.state[178]
        fake_666.state[130] = self.state[180]
        fake_666.state[131] = self.state[181]
        fake_666.state[134] = self.state[184]
        fake_666.state[135] = self.state[185]
        fake_666.state[136] = self.state[187]
        fake_666.state[137] = self.state[188]

        # Back
        fake_666.state[152] = self.state[205]
        fake_666.state[153] = self.state[206]
        fake_666.state[154] = self.state[208]
        fake_666.state[155] = self.state[209]
        fake_666.state[158] = self.state[212]
        fake_666.state[159] = self.state[213]
        fake_666.state[160] = self.state[215]
        fake_666.state[161] = self.state[216]
        fake_666.state[164] = self.state[226]
        fake_666.state[165] = self.state[227]
        fake_666.state[166] = self.state[229]
        fake_666.state[167] = self.state[230]
        fake_666.state[170] = self.state[233]
        fake_666.state[171] = self.state[234]
        fake_666.state[172] = self.state[236]
        fake_666.state[173] = self.state[237]

        # Down
        fake_666.state[188] = self.state[254]
        fake_666.state[189] = self.state[255]
        fake_666.state[190] = self.state[257]
        fake_666.state[191] = self.state[258]
        fake_666.state[194] = self.state[261]
        fake_666.state[195] = self.state[262]
        fake_666.state[196] = self.state[264]
        fake_666.state[197] = self.state[265]
        fake_666.state[200] = self.state[275]
        fake_666.state[201] = self.state[276]
        fake_666.state[202] = self.state[278]
        fake_666.state[203] = self.state[279]
        fake_666.state[206] = self.state[282]
        fake_666.state[207] = self.state[283]
        fake_666.state[208] = self.state[285]
        fake_666.state[209] = self.state[286]
        fake_666.sanity_check()

        return fake_666

    def group_outside_UD_oblique_edges(self):
        fake_666 = self.create_fake_666_centers()
        fake_666.stage_oblique_edges_UD()

        for step in fake_666.solution:

            if step.startswith('6'):
                step = '7' + step[1:]

            self.rotate(step)

        self.rotate_U_to_U()
        self.rotate_F_to_F()

    def group_outside_LR_oblique_edges(self):
        fake_666 = self.create_fake_666_centers()
        fake_666.stage_oblique_edges_LR()

        for step in fake_666.solution:

            if step.startswith('6'):
                step = '7' + step[1:]

            self.rotate(step)

        self.rotate_U_to_U()
        self.rotate_F_to_F()

    def group_centers_guts(self, oblique_edges_only=False):
        self.lt_init()

        # Uses 5x5x5 solver to stage the inner x-centers and inner t-centers for UD
        self.group_inside_UD_centers()
        self.print_cube()
        log.info("%s: Inside UD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Uses 6x6x6 solver to pair the "outside" oblique edges for UD
        self.group_outside_UD_oblique_edges()
        self.print_cube()
        log.info("%s: Outside UD oblique edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Test the prune tables
        #self.lt_UD_oblique_edge_pairing_middle_only.solve()
        #self.lt_UD_oblique_edge_pairing_left_only.solve()
        #self.lt_UD_oblique_edge_pairing_right_only.solve()
        #self.print_cube()
        #sys.exit(0)

        # Now stage the "inside" oblique UD edges with the already staged outside oblique UD edges
        self.lt_UD_oblique_edge_pairing.solve()
        self.print_cube()
        log.info("%s: UD oblique edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Uses 5x5x5 solver to stage the inner x-centers and inner t-centers for LR
        self.group_inside_LR_centers()
        self.print_cube()
        log.info("%s: Inside LR centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Uses 6x6x6 solver to pair the "outside" oblique edges for LR
        self.group_outside_LR_oblique_edges()
        self.print_cube()
        log.info("%s: Outside LR oblique edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Test the prune tables
        #self.lt_LR_oblique_edge_pairing_middle_only.solve()
        #self.lt_LR_oblique_edge_pairing_left_only.solve()
        #self.lt_LR_oblique_edge_pairing_right_only.solve()
        #self.print_cube()
        #sys.exit(0)

        # Now stage the "inside" oblique LR edges with the already staged outside oblique LR edges
        self.lt_LR_oblique_edge_pairing.solve()
        self.print_cube()
        log.info("%s: LR oblique edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Test pruning tables
        #self.lt_UD_solve_inner_centers_and_oblique_edges_center_only.solve()
        #self.lt_UD_solve_inner_centers_and_oblique_edges_edges_only.solve()
        #log.info("%s: UD inner-centers solved, UD oblique edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #self.print_cube()
        #sys.exit(0)

        self.lt_UD_solve_inner_centers_and_oblique_edges.solve()
        self.print_cube()
        log.info("%s: UD centers reduced to 5x5x5 centers, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #log.info("state: %s" % self.get_kociemba_string(True))
        log.info("")
        log.info("")
        log.info("")
        log.info("")


        # Test prune tables
        #self.lt_LFRB_solve_inner_centers.solve()
        #self.lt_LR_solve_inner_x_center_t_center_middle_oblique_edge.solve()
        #self.lt_LR_solve_oblique_edge.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        # Reduce LFRB centers to 5x5x5 via

        # uncomment if using 6-deep partial table
        # Reduce LR centers to 5x5x5 by solving the inner x-centers, t-centers and oblique edges
        self.lt_LR_solve_inner_centers_and_oblique_edges.solve()
        self.print_cube()
        log.info("%s: LR inner-centers solved and oblique edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Solve the LR t-centers...this speeds up the step80 IDA a good bit because the centers of
        # sides L and R do not get as scrambled while solving FB if LR t-centers are already solved.
        fake_555 = self.create_fake_555_for_LR_t_centers()
        fake_555.lt_LR_t_centers_solve.solve()

        for step in fake_555.solution:
            if step.startswith('5'):
                step = '7' + step[1:]
            elif step.startswith('3'):
                step = '4' + step[1:]
            self.rotate(step)

        self.print_cube()
        log.info("%s: LR outer t-centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Test prune tables
        #self.lt_FB_solve_inner_x_center_t_center_middle_oblique_edge.solve()
        #self.lt_FB_solve_oblique_edge.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        '''
        # Reduce FB centers to 5x5x5 by solving the inner x-centers, t-centers and oblique edges
        self.lt_FB_solve_inner_centers_and_oblique_edges.solve()
        self.print_cube()
        log.info("%s: FB inner-centers solved and oblique edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        '''

        # Reduce LRFB centers to 5x5x5 by solving the inner x-centers, t-centers and oblique edges
        self.lt_LFRB_solve_inner_centers_and_oblique_edges.solve()
        self.print_cube()
        log.info("%s: LFRB centers reduced to 5x5x5 centers, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Centers are now reduced to 5x5x5 centers
        if oblique_edges_only:

            # If we are here it is because a larger cube is using the 7x7x7 solver to
            # solve their centers. We must "solve" the t-centers in this scenario.
            self.solve_reduced_555_t_centers()
            self.print_cube()
            log.info("%s: Took %d steps to solve oblique edges and t-centers" % (self, self.get_solution_len_minus_rotates(self.solution)))
        else:
            self.solve_reduced_555_centers()
            self.print_cube()
            log.info("%s: Took %d steps to solve centers" % (self, self.get_solution_len_minus_rotates(self.solution)))



# There are 4900 of them so I put them at the bottom of the file
lt_LFRB_solve_inner_centers_and_oblique_edges_state_targets = (
    '0e7380739c3c631fe318f',
    '0e7380739dfc631e2318f',
    '0e7380739dfc631fc210f',
    '0e7380739dfc631fe1087',
    '0e7380739dfc631fe3188',
    '0e73807bde3c631e2318f',
    '0e73807bde3c631fc210f',
    '0e73807bde3c631fe1087',
    '0e73807bde3c631fe3188',
    '0e73807bdffc631e0210f',
    '0e73807bdffc631e21087',
    '0e73807bdffc631e23188',
    '0e73807bdffc631fc0007',
    '0e73807bdffc631fc2108',
    '0e73807bdffc631fe1080',
    '0e7380f7bc3c631e2318f',
    '0e7380f7bc3c631fc210f',
    '0e7380f7bc3c631fe1087',
    '0e7380f7bc3c631fe3188',
    '0e7380f7bdfc631e0210f',
    '0e7380f7bdfc631e21087',
    '0e7380f7bdfc631e23188',
    '0e7380f7bdfc631fc0007',
    '0e7380f7bdfc631fc2108',
    '0e7380f7bdfc631fe1080',
    '0e7380fffe3c631e0210f',
    '0e7380fffe3c631e21087',
    '0e7380fffe3c631e23188',
    '0e7380fffe3c631fc0007',
    '0e7380fffe3c631fc2108',
    '0e7380fffe3c631fe1080',
    '0e7380fffffc631e00007',
    '0e7380fffffc631e02108',
    '0e7380fffffc631e21080',
    '0e7380fffffc631fc0000',
    '0e7387739c3c631e2318f',
    '0e7387739c3c631fc210f',
    '0e7387739c3c631fe1087',
    '0e7387739c3c631fe3188',
    '0e7387739dfc631e0210f',
    '0e7387739dfc631e21087',
    '0e7387739dfc631e23188',
    '0e7387739dfc631fc0007',
    '0e7387739dfc631fc2108',
    '0e7387739dfc631fe1080',
    '0e73877bde3c631e0210f',
    '0e73877bde3c631e21087',
    '0e73877bde3c631e23188',
    '0e73877bde3c631fc0007',
    '0e73877bde3c631fc2108',
    '0e73877bde3c631fe1080',
    '0e73877bdffc631e00007',
    '0e73877bdffc631e02108',
    '0e73877bdffc631e21080',
    '0e73877bdffc631fc0000',
    '0e7387f7bc3c631e0210f',
    '0e7387f7bc3c631e21087',
    '0e7387f7bc3c631e23188',
    '0e7387f7bc3c631fc0007',
    '0e7387f7bc3c631fc2108',
    '0e7387f7bc3c631fe1080',
    '0e7387f7bdfc631e00007',
    '0e7387f7bdfc631e02108',
    '0e7387f7bdfc631e21080',
    '0e7387f7bdfc631fc0000',
    '0e7387fffe3c631e00007',
    '0e7387fffe3c631e02108',
    '0e7387fffe3c631e21080',
    '0e7387fffe3c631fc0000',
    '0e7387fffffc631e00000',
    '0e73b8739c04631fe318f',
    '0e73b8739c38421fe318f',
    '0e73b8739c3c210fe318f',
    '0e73b8739c3c6311e318f',
    '0e73b8739dc4631e2318f',
    '0e73b8739dc4631fc210f',
    '0e73b8739dc4631fe1087',
    '0e73b8739dc4631fe3188',
    '0e73b8739df8421e2318f',
    '0e73b8739df8421fc210f',
    '0e73b8739df8421fe1087',
    '0e73b8739df8421fe3188',
    '0e73b8739dfc210e2318f',
    '0e73b8739dfc210fc210f',
    '0e73b8739dfc210fe1087',
    '0e73b8739dfc210fe3188',
    '0e73b8739dfc63102318f',
    '0e73b8739dfc6311c210f',
    '0e73b8739dfc6311e1087',
    '0e73b8739dfc6311e3188',
    '0e73b87bde04631e2318f',
    '0e73b87bde04631fc210f',
    '0e73b87bde04631fe1087',
    '0e73b87bde04631fe3188',
    '0e73b87bde38421e2318f',
    '0e73b87bde38421fc210f',
    '0e73b87bde38421fe1087',
    '0e73b87bde38421fe3188',
    '0e73b87bde3c210e2318f',
    '0e73b87bde3c210fc210f',
    '0e73b87bde3c210fe1087',
    '0e73b87bde3c210fe3188',
    '0e73b87bde3c63102318f',
    '0e73b87bde3c6311c210f',
    '0e73b87bde3c6311e1087',
    '0e73b87bde3c6311e3188',
    '0e73b87bdfc4631e0210f',
    '0e73b87bdfc4631e21087',
    '0e73b87bdfc4631e23188',
    '0e73b87bdfc4631fc0007',
    '0e73b87bdfc4631fc2108',
    '0e73b87bdfc4631fe1080',
    '0e73b87bdff8421e0210f',
    '0e73b87bdff8421e21087',
    '0e73b87bdff8421e23188',
    '0e73b87bdff8421fc0007',
    '0e73b87bdff8421fc2108',
    '0e73b87bdff8421fe1080',
    '0e73b87bdffc210e0210f',
    '0e73b87bdffc210e21087',
    '0e73b87bdffc210e23188',
    '0e73b87bdffc210fc0007',
    '0e73b87bdffc210fc2108',
    '0e73b87bdffc210fe1080',
    '0e73b87bdffc63100210f',
    '0e73b87bdffc631021087',
    '0e73b87bdffc631023188',
    '0e73b87bdffc6311c0007',
    '0e73b87bdffc6311c2108',
    '0e73b87bdffc6311e1080',
    '0e73b8f7bc04631e2318f',
    '0e73b8f7bc04631fc210f',
    '0e73b8f7bc04631fe1087',
    '0e73b8f7bc04631fe3188',
    '0e73b8f7bc38421e2318f',
    '0e73b8f7bc38421fc210f',
    '0e73b8f7bc38421fe1087',
    '0e73b8f7bc38421fe3188',
    '0e73b8f7bc3c210e2318f',
    '0e73b8f7bc3c210fc210f',
    '0e73b8f7bc3c210fe1087',
    '0e73b8f7bc3c210fe3188',
    '0e73b8f7bc3c63102318f',
    '0e73b8f7bc3c6311c210f',
    '0e73b8f7bc3c6311e1087',
    '0e73b8f7bc3c6311e3188',
    '0e73b8f7bdc4631e0210f',
    '0e73b8f7bdc4631e21087',
    '0e73b8f7bdc4631e23188',
    '0e73b8f7bdc4631fc0007',
    '0e73b8f7bdc4631fc2108',
    '0e73b8f7bdc4631fe1080',
    '0e73b8f7bdf8421e0210f',
    '0e73b8f7bdf8421e21087',
    '0e73b8f7bdf8421e23188',
    '0e73b8f7bdf8421fc0007',
    '0e73b8f7bdf8421fc2108',
    '0e73b8f7bdf8421fe1080',
    '0e73b8f7bdfc210e0210f',
    '0e73b8f7bdfc210e21087',
    '0e73b8f7bdfc210e23188',
    '0e73b8f7bdfc210fc0007',
    '0e73b8f7bdfc210fc2108',
    '0e73b8f7bdfc210fe1080',
    '0e73b8f7bdfc63100210f',
    '0e73b8f7bdfc631021087',
    '0e73b8f7bdfc631023188',
    '0e73b8f7bdfc6311c0007',
    '0e73b8f7bdfc6311c2108',
    '0e73b8f7bdfc6311e1080',
    '0e73b8fffe04631e0210f',
    '0e73b8fffe04631e21087',
    '0e73b8fffe04631e23188',
    '0e73b8fffe04631fc0007',
    '0e73b8fffe04631fc2108',
    '0e73b8fffe04631fe1080',
    '0e73b8fffe38421e0210f',
    '0e73b8fffe38421e21087',
    '0e73b8fffe38421e23188',
    '0e73b8fffe38421fc0007',
    '0e73b8fffe38421fc2108',
    '0e73b8fffe38421fe1080',
    '0e73b8fffe3c210e0210f',
    '0e73b8fffe3c210e21087',
    '0e73b8fffe3c210e23188',
    '0e73b8fffe3c210fc0007',
    '0e73b8fffe3c210fc2108',
    '0e73b8fffe3c210fe1080',
    '0e73b8fffe3c63100210f',
    '0e73b8fffe3c631021087',
    '0e73b8fffe3c631023188',
    '0e73b8fffe3c6311c0007',
    '0e73b8fffe3c6311c2108',
    '0e73b8fffe3c6311e1080',
    '0e73b8ffffc4631e00007',
    '0e73b8ffffc4631e02108',
    '0e73b8ffffc4631e21080',
    '0e73b8ffffc4631fc0000',
    '0e73b8fffff8421e00007',
    '0e73b8fffff8421e02108',
    '0e73b8fffff8421e21080',
    '0e73b8fffff8421fc0000',
    '0e73b8fffffc210e00007',
    '0e73b8fffffc210e02108',
    '0e73b8fffffc210e21080',
    '0e73b8fffffc210fc0000',
    '0e73b8fffffc631000007',
    '0e73b8fffffc631002108',
    '0e73b8fffffc631021080',
    '0e73b8fffffc6311c0000',
    '0e73bf739c04631e2318f',
    '0e73bf739c04631fc210f',
    '0e73bf739c04631fe1087',
    '0e73bf739c04631fe3188',
    '0e73bf739c38421e2318f',
    '0e73bf739c38421fc210f',
    '0e73bf739c38421fe1087',
    '0e73bf739c38421fe3188',
    '0e73bf739c3c210e2318f',
    '0e73bf739c3c210fc210f',
    '0e73bf739c3c210fe1087',
    '0e73bf739c3c210fe3188',
    '0e73bf739c3c63102318f',
    '0e73bf739c3c6311c210f',
    '0e73bf739c3c6311e1087',
    '0e73bf739c3c6311e3188',
    '0e73bf739dc4631e0210f',
    '0e73bf739dc4631e21087',
    '0e73bf739dc4631e23188',
    '0e73bf739dc4631fc0007',
    '0e73bf739dc4631fc2108',
    '0e73bf739dc4631fe1080',
    '0e73bf739df8421e0210f',
    '0e73bf739df8421e21087',
    '0e73bf739df8421e23188',
    '0e73bf739df8421fc0007',
    '0e73bf739df8421fc2108',
    '0e73bf739df8421fe1080',
    '0e73bf739dfc210e0210f',
    '0e73bf739dfc210e21087',
    '0e73bf739dfc210e23188',
    '0e73bf739dfc210fc0007',
    '0e73bf739dfc210fc2108',
    '0e73bf739dfc210fe1080',
    '0e73bf739dfc63100210f',
    '0e73bf739dfc631021087',
    '0e73bf739dfc631023188',
    '0e73bf739dfc6311c0007',
    '0e73bf739dfc6311c2108',
    '0e73bf739dfc6311e1080',
    '0e73bf7bde04631e0210f',
    '0e73bf7bde04631e21087',
    '0e73bf7bde04631e23188',
    '0e73bf7bde04631fc0007',
    '0e73bf7bde04631fc2108',
    '0e73bf7bde04631fe1080',
    '0e73bf7bde38421e0210f',
    '0e73bf7bde38421e21087',
    '0e73bf7bde38421e23188',
    '0e73bf7bde38421fc0007',
    '0e73bf7bde38421fc2108',
    '0e73bf7bde38421fe1080',
    '0e73bf7bde3c210e0210f',
    '0e73bf7bde3c210e21087',
    '0e73bf7bde3c210e23188',
    '0e73bf7bde3c210fc0007',
    '0e73bf7bde3c210fc2108',
    '0e73bf7bde3c210fe1080',
    '0e73bf7bde3c63100210f',
    '0e73bf7bde3c631021087',
    '0e73bf7bde3c631023188',
    '0e73bf7bde3c6311c0007',
    '0e73bf7bde3c6311c2108',
    '0e73bf7bde3c6311e1080',
    '0e73bf7bdfc4631e00007',
    '0e73bf7bdfc4631e02108',
    '0e73bf7bdfc4631e21080',
    '0e73bf7bdfc4631fc0000',
    '0e73bf7bdff8421e00007',
    '0e73bf7bdff8421e02108',
    '0e73bf7bdff8421e21080',
    '0e73bf7bdff8421fc0000',
    '0e73bf7bdffc210e00007',
    '0e73bf7bdffc210e02108',
    '0e73bf7bdffc210e21080',
    '0e73bf7bdffc210fc0000',
    '0e73bf7bdffc631000007',
    '0e73bf7bdffc631002108',
    '0e73bf7bdffc631021080',
    '0e73bf7bdffc6311c0000',
    '0e73bff7bc04631e0210f',
    '0e73bff7bc04631e21087',
    '0e73bff7bc04631e23188',
    '0e73bff7bc04631fc0007',
    '0e73bff7bc04631fc2108',
    '0e73bff7bc04631fe1080',
    '0e73bff7bc38421e0210f',
    '0e73bff7bc38421e21087',
    '0e73bff7bc38421e23188',
    '0e73bff7bc38421fc0007',
    '0e73bff7bc38421fc2108',
    '0e73bff7bc38421fe1080',
    '0e73bff7bc3c210e0210f',
    '0e73bff7bc3c210e21087',
    '0e73bff7bc3c210e23188',
    '0e73bff7bc3c210fc0007',
    '0e73bff7bc3c210fc2108',
    '0e73bff7bc3c210fe1080',
    '0e73bff7bc3c63100210f',
    '0e73bff7bc3c631021087',
    '0e73bff7bc3c631023188',
    '0e73bff7bc3c6311c0007',
    '0e73bff7bc3c6311c2108',
    '0e73bff7bc3c6311e1080',
    '0e73bff7bdc4631e00007',
    '0e73bff7bdc4631e02108',
    '0e73bff7bdc4631e21080',
    '0e73bff7bdc4631fc0000',
    '0e73bff7bdf8421e00007',
    '0e73bff7bdf8421e02108',
    '0e73bff7bdf8421e21080',
    '0e73bff7bdf8421fc0000',
    '0e73bff7bdfc210e00007',
    '0e73bff7bdfc210e02108',
    '0e73bff7bdfc210e21080',
    '0e73bff7bdfc210fc0000',
    '0e73bff7bdfc631000007',
    '0e73bff7bdfc631002108',
    '0e73bff7bdfc631021080',
    '0e73bff7bdfc6311c0000',
    '0e73bffffe04631e00007',
    '0e73bffffe04631e02108',
    '0e73bffffe04631e21080',
    '0e73bffffe04631fc0000',
    '0e73bffffe38421e00007',
    '0e73bffffe38421e02108',
    '0e73bffffe38421e21080',
    '0e73bffffe38421fc0000',
    '0e73bffffe3c210e00007',
    '0e73bffffe3c210e02108',
    '0e73bffffe3c210e21080',
    '0e73bffffe3c210fc0000',
    '0e73bffffe3c631000007',
    '0e73bffffe3c631002108',
    '0e73bffffe3c631021080',
    '0e73bffffe3c6311c0000',
    '0e73bfffffc4631e00000',
    '0e73bffffff8421e00000',
    '0e73bffffffc210e00000',
    '0e73bffffffc631000000',
    '0f7bc0739c04631fe318f',
    '0f7bc0739c38421fe318f',
    '0f7bc0739c3c210fe318f',
    '0f7bc0739c3c6311e318f',
    '0f7bc0739dc4631e2318f',
    '0f7bc0739dc4631fc210f',
    '0f7bc0739dc4631fe1087',
    '0f7bc0739dc4631fe3188',
    '0f7bc0739df8421e2318f',
    '0f7bc0739df8421fc210f',
    '0f7bc0739df8421fe1087',
    '0f7bc0739df8421fe3188',
    '0f7bc0739dfc210e2318f',
    '0f7bc0739dfc210fc210f',
    '0f7bc0739dfc210fe1087',
    '0f7bc0739dfc210fe3188',
    '0f7bc0739dfc63102318f',
    '0f7bc0739dfc6311c210f',
    '0f7bc0739dfc6311e1087',
    '0f7bc0739dfc6311e3188',
    '0f7bc07bde04631e2318f',
    '0f7bc07bde04631fc210f',
    '0f7bc07bde04631fe1087',
    '0f7bc07bde04631fe3188',
    '0f7bc07bde38421e2318f',
    '0f7bc07bde38421fc210f',
    '0f7bc07bde38421fe1087',
    '0f7bc07bde38421fe3188',
    '0f7bc07bde3c210e2318f',
    '0f7bc07bde3c210fc210f',
    '0f7bc07bde3c210fe1087',
    '0f7bc07bde3c210fe3188',
    '0f7bc07bde3c63102318f',
    '0f7bc07bde3c6311c210f',
    '0f7bc07bde3c6311e1087',
    '0f7bc07bde3c6311e3188',
    '0f7bc07bdfc4631e0210f',
    '0f7bc07bdfc4631e21087',
    '0f7bc07bdfc4631e23188',
    '0f7bc07bdfc4631fc0007',
    '0f7bc07bdfc4631fc2108',
    '0f7bc07bdfc4631fe1080',
    '0f7bc07bdff8421e0210f',
    '0f7bc07bdff8421e21087',
    '0f7bc07bdff8421e23188',
    '0f7bc07bdff8421fc0007',
    '0f7bc07bdff8421fc2108',
    '0f7bc07bdff8421fe1080',
    '0f7bc07bdffc210e0210f',
    '0f7bc07bdffc210e21087',
    '0f7bc07bdffc210e23188',
    '0f7bc07bdffc210fc0007',
    '0f7bc07bdffc210fc2108',
    '0f7bc07bdffc210fe1080',
    '0f7bc07bdffc63100210f',
    '0f7bc07bdffc631021087',
    '0f7bc07bdffc631023188',
    '0f7bc07bdffc6311c0007',
    '0f7bc07bdffc6311c2108',
    '0f7bc07bdffc6311e1080',
    '0f7bc0f7bc04631e2318f',
    '0f7bc0f7bc04631fc210f',
    '0f7bc0f7bc04631fe1087',
    '0f7bc0f7bc04631fe3188',
    '0f7bc0f7bc38421e2318f',
    '0f7bc0f7bc38421fc210f',
    '0f7bc0f7bc38421fe1087',
    '0f7bc0f7bc38421fe3188',
    '0f7bc0f7bc3c210e2318f',
    '0f7bc0f7bc3c210fc210f',
    '0f7bc0f7bc3c210fe1087',
    '0f7bc0f7bc3c210fe3188',
    '0f7bc0f7bc3c63102318f',
    '0f7bc0f7bc3c6311c210f',
    '0f7bc0f7bc3c6311e1087',
    '0f7bc0f7bc3c6311e3188',
    '0f7bc0f7bdc4631e0210f',
    '0f7bc0f7bdc4631e21087',
    '0f7bc0f7bdc4631e23188',
    '0f7bc0f7bdc4631fc0007',
    '0f7bc0f7bdc4631fc2108',
    '0f7bc0f7bdc4631fe1080',
    '0f7bc0f7bdf8421e0210f',
    '0f7bc0f7bdf8421e21087',
    '0f7bc0f7bdf8421e23188',
    '0f7bc0f7bdf8421fc0007',
    '0f7bc0f7bdf8421fc2108',
    '0f7bc0f7bdf8421fe1080',
    '0f7bc0f7bdfc210e0210f',
    '0f7bc0f7bdfc210e21087',
    '0f7bc0f7bdfc210e23188',
    '0f7bc0f7bdfc210fc0007',
    '0f7bc0f7bdfc210fc2108',
    '0f7bc0f7bdfc210fe1080',
    '0f7bc0f7bdfc63100210f',
    '0f7bc0f7bdfc631021087',
    '0f7bc0f7bdfc631023188',
    '0f7bc0f7bdfc6311c0007',
    '0f7bc0f7bdfc6311c2108',
    '0f7bc0f7bdfc6311e1080',
    '0f7bc0fffe04631e0210f',
    '0f7bc0fffe04631e21087',
    '0f7bc0fffe04631e23188',
    '0f7bc0fffe04631fc0007',
    '0f7bc0fffe04631fc2108',
    '0f7bc0fffe04631fe1080',
    '0f7bc0fffe38421e0210f',
    '0f7bc0fffe38421e21087',
    '0f7bc0fffe38421e23188',
    '0f7bc0fffe38421fc0007',
    '0f7bc0fffe38421fc2108',
    '0f7bc0fffe38421fe1080',
    '0f7bc0fffe3c210e0210f',
    '0f7bc0fffe3c210e21087',
    '0f7bc0fffe3c210e23188',
    '0f7bc0fffe3c210fc0007',
    '0f7bc0fffe3c210fc2108',
    '0f7bc0fffe3c210fe1080',
    '0f7bc0fffe3c63100210f',
    '0f7bc0fffe3c631021087',
    '0f7bc0fffe3c631023188',
    '0f7bc0fffe3c6311c0007',
    '0f7bc0fffe3c6311c2108',
    '0f7bc0fffe3c6311e1080',
    '0f7bc0ffffc4631e00007',
    '0f7bc0ffffc4631e02108',
    '0f7bc0ffffc4631e21080',
    '0f7bc0ffffc4631fc0000',
    '0f7bc0fffff8421e00007',
    '0f7bc0fffff8421e02108',
    '0f7bc0fffff8421e21080',
    '0f7bc0fffff8421fc0000',
    '0f7bc0fffffc210e00007',
    '0f7bc0fffffc210e02108',
    '0f7bc0fffffc210e21080',
    '0f7bc0fffffc210fc0000',
    '0f7bc0fffffc631000007',
    '0f7bc0fffffc631002108',
    '0f7bc0fffffc631021080',
    '0f7bc0fffffc6311c0000',
    '0f7bc7739c04631e2318f',
    '0f7bc7739c04631fc210f',
    '0f7bc7739c04631fe1087',
    '0f7bc7739c04631fe3188',
    '0f7bc7739c38421e2318f',
    '0f7bc7739c38421fc210f',
    '0f7bc7739c38421fe1087',
    '0f7bc7739c38421fe3188',
    '0f7bc7739c3c210e2318f',
    '0f7bc7739c3c210fc210f',
    '0f7bc7739c3c210fe1087',
    '0f7bc7739c3c210fe3188',
    '0f7bc7739c3c63102318f',
    '0f7bc7739c3c6311c210f',
    '0f7bc7739c3c6311e1087',
    '0f7bc7739c3c6311e3188',
    '0f7bc7739dc4631e0210f',
    '0f7bc7739dc4631e21087',
    '0f7bc7739dc4631e23188',
    '0f7bc7739dc4631fc0007',
    '0f7bc7739dc4631fc2108',
    '0f7bc7739dc4631fe1080',
    '0f7bc7739df8421e0210f',
    '0f7bc7739df8421e21087',
    '0f7bc7739df8421e23188',
    '0f7bc7739df8421fc0007',
    '0f7bc7739df8421fc2108',
    '0f7bc7739df8421fe1080',
    '0f7bc7739dfc210e0210f',
    '0f7bc7739dfc210e21087',
    '0f7bc7739dfc210e23188',
    '0f7bc7739dfc210fc0007',
    '0f7bc7739dfc210fc2108',
    '0f7bc7739dfc210fe1080',
    '0f7bc7739dfc63100210f',
    '0f7bc7739dfc631021087',
    '0f7bc7739dfc631023188',
    '0f7bc7739dfc6311c0007',
    '0f7bc7739dfc6311c2108',
    '0f7bc7739dfc6311e1080',
    '0f7bc77bde04631e0210f',
    '0f7bc77bde04631e21087',
    '0f7bc77bde04631e23188',
    '0f7bc77bde04631fc0007',
    '0f7bc77bde04631fc2108',
    '0f7bc77bde04631fe1080',
    '0f7bc77bde38421e0210f',
    '0f7bc77bde38421e21087',
    '0f7bc77bde38421e23188',
    '0f7bc77bde38421fc0007',
    '0f7bc77bde38421fc2108',
    '0f7bc77bde38421fe1080',
    '0f7bc77bde3c210e0210f',
    '0f7bc77bde3c210e21087',
    '0f7bc77bde3c210e23188',
    '0f7bc77bde3c210fc0007',
    '0f7bc77bde3c210fc2108',
    '0f7bc77bde3c210fe1080',
    '0f7bc77bde3c63100210f',
    '0f7bc77bde3c631021087',
    '0f7bc77bde3c631023188',
    '0f7bc77bde3c6311c0007',
    '0f7bc77bde3c6311c2108',
    '0f7bc77bde3c6311e1080',
    '0f7bc77bdfc4631e00007',
    '0f7bc77bdfc4631e02108',
    '0f7bc77bdfc4631e21080',
    '0f7bc77bdfc4631fc0000',
    '0f7bc77bdff8421e00007',
    '0f7bc77bdff8421e02108',
    '0f7bc77bdff8421e21080',
    '0f7bc77bdff8421fc0000',
    '0f7bc77bdffc210e00007',
    '0f7bc77bdffc210e02108',
    '0f7bc77bdffc210e21080',
    '0f7bc77bdffc210fc0000',
    '0f7bc77bdffc631000007',
    '0f7bc77bdffc631002108',
    '0f7bc77bdffc631021080',
    '0f7bc77bdffc6311c0000',
    '0f7bc7f7bc04631e0210f',
    '0f7bc7f7bc04631e21087',
    '0f7bc7f7bc04631e23188',
    '0f7bc7f7bc04631fc0007',
    '0f7bc7f7bc04631fc2108',
    '0f7bc7f7bc04631fe1080',
    '0f7bc7f7bc38421e0210f',
    '0f7bc7f7bc38421e21087',
    '0f7bc7f7bc38421e23188',
    '0f7bc7f7bc38421fc0007',
    '0f7bc7f7bc38421fc2108',
    '0f7bc7f7bc38421fe1080',
    '0f7bc7f7bc3c210e0210f',
    '0f7bc7f7bc3c210e21087',
    '0f7bc7f7bc3c210e23188',
    '0f7bc7f7bc3c210fc0007',
    '0f7bc7f7bc3c210fc2108',
    '0f7bc7f7bc3c210fe1080',
    '0f7bc7f7bc3c63100210f',
    '0f7bc7f7bc3c631021087',
    '0f7bc7f7bc3c631023188',
    '0f7bc7f7bc3c6311c0007',
    '0f7bc7f7bc3c6311c2108',
    '0f7bc7f7bc3c6311e1080',
    '0f7bc7f7bdc4631e00007',
    '0f7bc7f7bdc4631e02108',
    '0f7bc7f7bdc4631e21080',
    '0f7bc7f7bdc4631fc0000',
    '0f7bc7f7bdf8421e00007',
    '0f7bc7f7bdf8421e02108',
    '0f7bc7f7bdf8421e21080',
    '0f7bc7f7bdf8421fc0000',
    '0f7bc7f7bdfc210e00007',
    '0f7bc7f7bdfc210e02108',
    '0f7bc7f7bdfc210e21080',
    '0f7bc7f7bdfc210fc0000',
    '0f7bc7f7bdfc631000007',
    '0f7bc7f7bdfc631002108',
    '0f7bc7f7bdfc631021080',
    '0f7bc7f7bdfc6311c0000',
    '0f7bc7fffe04631e00007',
    '0f7bc7fffe04631e02108',
    '0f7bc7fffe04631e21080',
    '0f7bc7fffe04631fc0000',
    '0f7bc7fffe38421e00007',
    '0f7bc7fffe38421e02108',
    '0f7bc7fffe38421e21080',
    '0f7bc7fffe38421fc0000',
    '0f7bc7fffe3c210e00007',
    '0f7bc7fffe3c210e02108',
    '0f7bc7fffe3c210e21080',
    '0f7bc7fffe3c210fc0000',
    '0f7bc7fffe3c631000007',
    '0f7bc7fffe3c631002108',
    '0f7bc7fffe3c631021080',
    '0f7bc7fffe3c6311c0000',
    '0f7bc7ffffc4631e00000',
    '0f7bc7fffff8421e00000',
    '0f7bc7fffffc210e00000',
    '0f7bc7fffffc631000000',
    '0f7bf8739c00421fe318f',
    '0f7bf8739c04210fe318f',
    '0f7bf8739c046311e318f',
    '0f7bf8739c38000fe318f',
    '0f7bf8739c384211e318f',
    '0f7bf8739c3c2101e318f',
    '0f7bf8739dc0421e2318f',
    '0f7bf8739dc0421fc210f',
    '0f7bf8739dc0421fe1087',
    '0f7bf8739dc0421fe3188',
    '0f7bf8739dc4210e2318f',
    '0f7bf8739dc4210fc210f',
    '0f7bf8739dc4210fe1087',
    '0f7bf8739dc4210fe3188',
    '0f7bf8739dc463102318f',
    '0f7bf8739dc46311c210f',
    '0f7bf8739dc46311e1087',
    '0f7bf8739dc46311e3188',
    '0f7bf8739df8000e2318f',
    '0f7bf8739df8000fc210f',
    '0f7bf8739df8000fe1087',
    '0f7bf8739df8000fe3188',
    '0f7bf8739df842102318f',
    '0f7bf8739df84211c210f',
    '0f7bf8739df84211e1087',
    '0f7bf8739df84211e3188',
    '0f7bf8739dfc21002318f',
    '0f7bf8739dfc2101c210f',
    '0f7bf8739dfc2101e1087',
    '0f7bf8739dfc2101e3188',
    '0f7bf87bde00421e2318f',
    '0f7bf87bde00421fc210f',
    '0f7bf87bde00421fe1087',
    '0f7bf87bde00421fe3188',
    '0f7bf87bde04210e2318f',
    '0f7bf87bde04210fc210f',
    '0f7bf87bde04210fe1087',
    '0f7bf87bde04210fe3188',
    '0f7bf87bde0463102318f',
    '0f7bf87bde046311c210f',
    '0f7bf87bde046311e1087',
    '0f7bf87bde046311e3188',
    '0f7bf87bde38000e2318f',
    '0f7bf87bde38000fc210f',
    '0f7bf87bde38000fe1087',
    '0f7bf87bde38000fe3188',
    '0f7bf87bde3842102318f',
    '0f7bf87bde384211c210f',
    '0f7bf87bde384211e1087',
    '0f7bf87bde384211e3188',
    '0f7bf87bde3c21002318f',
    '0f7bf87bde3c2101c210f',
    '0f7bf87bde3c2101e1087',
    '0f7bf87bde3c2101e3188',
    '0f7bf87bdfc0421e0210f',
    '0f7bf87bdfc0421e21087',
    '0f7bf87bdfc0421e23188',
    '0f7bf87bdfc0421fc0007',
    '0f7bf87bdfc0421fc2108',
    '0f7bf87bdfc0421fe1080',
    '0f7bf87bdfc4210e0210f',
    '0f7bf87bdfc4210e21087',
    '0f7bf87bdfc4210e23188',
    '0f7bf87bdfc4210fc0007',
    '0f7bf87bdfc4210fc2108',
    '0f7bf87bdfc4210fe1080',
    '0f7bf87bdfc463100210f',
    '0f7bf87bdfc4631021087',
    '0f7bf87bdfc4631023188',
    '0f7bf87bdfc46311c0007',
    '0f7bf87bdfc46311c2108',
    '0f7bf87bdfc46311e1080',
    '0f7bf87bdff8000e0210f',
    '0f7bf87bdff8000e21087',
    '0f7bf87bdff8000e23188',
    '0f7bf87bdff8000fc0007',
    '0f7bf87bdff8000fc2108',
    '0f7bf87bdff8000fe1080',
    '0f7bf87bdff842100210f',
    '0f7bf87bdff8421021087',
    '0f7bf87bdff8421023188',
    '0f7bf87bdff84211c0007',
    '0f7bf87bdff84211c2108',
    '0f7bf87bdff84211e1080',
    '0f7bf87bdffc21000210f',
    '0f7bf87bdffc210021087',
    '0f7bf87bdffc210023188',
    '0f7bf87bdffc2101c0007',
    '0f7bf87bdffc2101c2108',
    '0f7bf87bdffc2101e1080',
    '0f7bf8f7bc00421e2318f',
    '0f7bf8f7bc00421fc210f',
    '0f7bf8f7bc00421fe1087',
    '0f7bf8f7bc00421fe3188',
    '0f7bf8f7bc04210e2318f',
    '0f7bf8f7bc04210fc210f',
    '0f7bf8f7bc04210fe1087',
    '0f7bf8f7bc04210fe3188',
    '0f7bf8f7bc0463102318f',
    '0f7bf8f7bc046311c210f',
    '0f7bf8f7bc046311e1087',
    '0f7bf8f7bc046311e3188',
    '0f7bf8f7bc38000e2318f',
    '0f7bf8f7bc38000fc210f',
    '0f7bf8f7bc38000fe1087',
    '0f7bf8f7bc38000fe3188',
    '0f7bf8f7bc3842102318f',
    '0f7bf8f7bc384211c210f',
    '0f7bf8f7bc384211e1087',
    '0f7bf8f7bc384211e3188',
    '0f7bf8f7bc3c21002318f',
    '0f7bf8f7bc3c2101c210f',
    '0f7bf8f7bc3c2101e1087',
    '0f7bf8f7bc3c2101e3188',
    '0f7bf8f7bdc0421e0210f',
    '0f7bf8f7bdc0421e21087',
    '0f7bf8f7bdc0421e23188',
    '0f7bf8f7bdc0421fc0007',
    '0f7bf8f7bdc0421fc2108',
    '0f7bf8f7bdc0421fe1080',
    '0f7bf8f7bdc4210e0210f',
    '0f7bf8f7bdc4210e21087',
    '0f7bf8f7bdc4210e23188',
    '0f7bf8f7bdc4210fc0007',
    '0f7bf8f7bdc4210fc2108',
    '0f7bf8f7bdc4210fe1080',
    '0f7bf8f7bdc463100210f',
    '0f7bf8f7bdc4631021087',
    '0f7bf8f7bdc4631023188',
    '0f7bf8f7bdc46311c0007',
    '0f7bf8f7bdc46311c2108',
    '0f7bf8f7bdc46311e1080',
    '0f7bf8f7bdf8000e0210f',
    '0f7bf8f7bdf8000e21087',
    '0f7bf8f7bdf8000e23188',
    '0f7bf8f7bdf8000fc0007',
    '0f7bf8f7bdf8000fc2108',
    '0f7bf8f7bdf8000fe1080',
    '0f7bf8f7bdf842100210f',
    '0f7bf8f7bdf8421021087',
    '0f7bf8f7bdf8421023188',
    '0f7bf8f7bdf84211c0007',
    '0f7bf8f7bdf84211c2108',
    '0f7bf8f7bdf84211e1080',
    '0f7bf8f7bdfc21000210f',
    '0f7bf8f7bdfc210021087',
    '0f7bf8f7bdfc210023188',
    '0f7bf8f7bdfc2101c0007',
    '0f7bf8f7bdfc2101c2108',
    '0f7bf8f7bdfc2101e1080',
    '0f7bf8fffe00421e0210f',
    '0f7bf8fffe00421e21087',
    '0f7bf8fffe00421e23188',
    '0f7bf8fffe00421fc0007',
    '0f7bf8fffe00421fc2108',
    '0f7bf8fffe00421fe1080',
    '0f7bf8fffe04210e0210f',
    '0f7bf8fffe04210e21087',
    '0f7bf8fffe04210e23188',
    '0f7bf8fffe04210fc0007',
    '0f7bf8fffe04210fc2108',
    '0f7bf8fffe04210fe1080',
    '0f7bf8fffe0463100210f',
    '0f7bf8fffe04631021087',
    '0f7bf8fffe04631023188',
    '0f7bf8fffe046311c0007',
    '0f7bf8fffe046311c2108',
    '0f7bf8fffe046311e1080',
    '0f7bf8fffe38000e0210f',
    '0f7bf8fffe38000e21087',
    '0f7bf8fffe38000e23188',
    '0f7bf8fffe38000fc0007',
    '0f7bf8fffe38000fc2108',
    '0f7bf8fffe38000fe1080',
    '0f7bf8fffe3842100210f',
    '0f7bf8fffe38421021087',
    '0f7bf8fffe38421023188',
    '0f7bf8fffe384211c0007',
    '0f7bf8fffe384211c2108',
    '0f7bf8fffe384211e1080',
    '0f7bf8fffe3c21000210f',
    '0f7bf8fffe3c210021087',
    '0f7bf8fffe3c210023188',
    '0f7bf8fffe3c2101c0007',
    '0f7bf8fffe3c2101c2108',
    '0f7bf8fffe3c2101e1080',
    '0f7bf8ffffc0421e00007',
    '0f7bf8ffffc0421e02108',
    '0f7bf8ffffc0421e21080',
    '0f7bf8ffffc0421fc0000',
    '0f7bf8ffffc4210e00007',
    '0f7bf8ffffc4210e02108',
    '0f7bf8ffffc4210e21080',
    '0f7bf8ffffc4210fc0000',
    '0f7bf8ffffc4631000007',
    '0f7bf8ffffc4631002108',
    '0f7bf8ffffc4631021080',
    '0f7bf8ffffc46311c0000',
    '0f7bf8fffff8000e00007',
    '0f7bf8fffff8000e02108',
    '0f7bf8fffff8000e21080',
    '0f7bf8fffff8000fc0000',
    '0f7bf8fffff8421000007',
    '0f7bf8fffff8421002108',
    '0f7bf8fffff8421021080',
    '0f7bf8fffff84211c0000',
    '0f7bf8fffffc210000007',
    '0f7bf8fffffc210002108',
    '0f7bf8fffffc210021080',
    '0f7bf8fffffc2101c0000',
    '0f7bff739c00421e2318f',
    '0f7bff739c00421fc210f',
    '0f7bff739c00421fe1087',
    '0f7bff739c00421fe3188',
    '0f7bff739c04210e2318f',
    '0f7bff739c04210fc210f',
    '0f7bff739c04210fe1087',
    '0f7bff739c04210fe3188',
    '0f7bff739c0463102318f',
    '0f7bff739c046311c210f',
    '0f7bff739c046311e1087',
    '0f7bff739c046311e3188',
    '0f7bff739c38000e2318f',
    '0f7bff739c38000fc210f',
    '0f7bff739c38000fe1087',
    '0f7bff739c38000fe3188',
    '0f7bff739c3842102318f',
    '0f7bff739c384211c210f',
    '0f7bff739c384211e1087',
    '0f7bff739c384211e3188',
    '0f7bff739c3c21002318f',
    '0f7bff739c3c2101c210f',
    '0f7bff739c3c2101e1087',
    '0f7bff739c3c2101e3188',
    '0f7bff739dc0421e0210f',
    '0f7bff739dc0421e21087',
    '0f7bff739dc0421e23188',
    '0f7bff739dc0421fc0007',
    '0f7bff739dc0421fc2108',
    '0f7bff739dc0421fe1080',
    '0f7bff739dc4210e0210f',
    '0f7bff739dc4210e21087',
    '0f7bff739dc4210e23188',
    '0f7bff739dc4210fc0007',
    '0f7bff739dc4210fc2108',
    '0f7bff739dc4210fe1080',
    '0f7bff739dc463100210f',
    '0f7bff739dc4631021087',
    '0f7bff739dc4631023188',
    '0f7bff739dc46311c0007',
    '0f7bff739dc46311c2108',
    '0f7bff739dc46311e1080',
    '0f7bff739df8000e0210f',
    '0f7bff739df8000e21087',
    '0f7bff739df8000e23188',
    '0f7bff739df8000fc0007',
    '0f7bff739df8000fc2108',
    '0f7bff739df8000fe1080',
    '0f7bff739df842100210f',
    '0f7bff739df8421021087',
    '0f7bff739df8421023188',
    '0f7bff739df84211c0007',
    '0f7bff739df84211c2108',
    '0f7bff739df84211e1080',
    '0f7bff739dfc21000210f',
    '0f7bff739dfc210021087',
    '0f7bff739dfc210023188',
    '0f7bff739dfc2101c0007',
    '0f7bff739dfc2101c2108',
    '0f7bff739dfc2101e1080',
    '0f7bff7bde00421e0210f',
    '0f7bff7bde00421e21087',
    '0f7bff7bde00421e23188',
    '0f7bff7bde00421fc0007',
    '0f7bff7bde00421fc2108',
    '0f7bff7bde00421fe1080',
    '0f7bff7bde04210e0210f',
    '0f7bff7bde04210e21087',
    '0f7bff7bde04210e23188',
    '0f7bff7bde04210fc0007',
    '0f7bff7bde04210fc2108',
    '0f7bff7bde04210fe1080',
    '0f7bff7bde0463100210f',
    '0f7bff7bde04631021087',
    '0f7bff7bde04631023188',
    '0f7bff7bde046311c0007',
    '0f7bff7bde046311c2108',
    '0f7bff7bde046311e1080',
    '0f7bff7bde38000e0210f',
    '0f7bff7bde38000e21087',
    '0f7bff7bde38000e23188',
    '0f7bff7bde38000fc0007',
    '0f7bff7bde38000fc2108',
    '0f7bff7bde38000fe1080',
    '0f7bff7bde3842100210f',
    '0f7bff7bde38421021087',
    '0f7bff7bde38421023188',
    '0f7bff7bde384211c0007',
    '0f7bff7bde384211c2108',
    '0f7bff7bde384211e1080',
    '0f7bff7bde3c21000210f',
    '0f7bff7bde3c210021087',
    '0f7bff7bde3c210023188',
    '0f7bff7bde3c2101c0007',
    '0f7bff7bde3c2101c2108',
    '0f7bff7bde3c2101e1080',
    '0f7bff7bdfc0421e00007',
    '0f7bff7bdfc0421e02108',
    '0f7bff7bdfc0421e21080',
    '0f7bff7bdfc0421fc0000',
    '0f7bff7bdfc4210e00007',
    '0f7bff7bdfc4210e02108',
    '0f7bff7bdfc4210e21080',
    '0f7bff7bdfc4210fc0000',
    '0f7bff7bdfc4631000007',
    '0f7bff7bdfc4631002108',
    '0f7bff7bdfc4631021080',
    '0f7bff7bdfc46311c0000',
    '0f7bff7bdff8000e00007',
    '0f7bff7bdff8000e02108',
    '0f7bff7bdff8000e21080',
    '0f7bff7bdff8000fc0000',
    '0f7bff7bdff8421000007',
    '0f7bff7bdff8421002108',
    '0f7bff7bdff8421021080',
    '0f7bff7bdff84211c0000',
    '0f7bff7bdffc210000007',
    '0f7bff7bdffc210002108',
    '0f7bff7bdffc210021080',
    '0f7bff7bdffc2101c0000',
    '0f7bfff7bc00421e0210f',
    '0f7bfff7bc00421e21087',
    '0f7bfff7bc00421e23188',
    '0f7bfff7bc00421fc0007',
    '0f7bfff7bc00421fc2108',
    '0f7bfff7bc00421fe1080',
    '0f7bfff7bc04210e0210f',
    '0f7bfff7bc04210e21087',
    '0f7bfff7bc04210e23188',
    '0f7bfff7bc04210fc0007',
    '0f7bfff7bc04210fc2108',
    '0f7bfff7bc04210fe1080',
    '0f7bfff7bc0463100210f',
    '0f7bfff7bc04631021087',
    '0f7bfff7bc04631023188',
    '0f7bfff7bc046311c0007',
    '0f7bfff7bc046311c2108',
    '0f7bfff7bc046311e1080',
    '0f7bfff7bc38000e0210f',
    '0f7bfff7bc38000e21087',
    '0f7bfff7bc38000e23188',
    '0f7bfff7bc38000fc0007',
    '0f7bfff7bc38000fc2108',
    '0f7bfff7bc38000fe1080',
    '0f7bfff7bc3842100210f',
    '0f7bfff7bc38421021087',
    '0f7bfff7bc38421023188',
    '0f7bfff7bc384211c0007',
    '0f7bfff7bc384211c2108',
    '0f7bfff7bc384211e1080',
    '0f7bfff7bc3c21000210f',
    '0f7bfff7bc3c210021087',
    '0f7bfff7bc3c210023188',
    '0f7bfff7bc3c2101c0007',
    '0f7bfff7bc3c2101c2108',
    '0f7bfff7bc3c2101e1080',
    '0f7bfff7bdc0421e00007',
    '0f7bfff7bdc0421e02108',
    '0f7bfff7bdc0421e21080',
    '0f7bfff7bdc0421fc0000',
    '0f7bfff7bdc4210e00007',
    '0f7bfff7bdc4210e02108',
    '0f7bfff7bdc4210e21080',
    '0f7bfff7bdc4210fc0000',
    '0f7bfff7bdc4631000007',
    '0f7bfff7bdc4631002108',
    '0f7bfff7bdc4631021080',
    '0f7bfff7bdc46311c0000',
    '0f7bfff7bdf8000e00007',
    '0f7bfff7bdf8000e02108',
    '0f7bfff7bdf8000e21080',
    '0f7bfff7bdf8000fc0000',
    '0f7bfff7bdf8421000007',
    '0f7bfff7bdf8421002108',
    '0f7bfff7bdf8421021080',
    '0f7bfff7bdf84211c0000',
    '0f7bfff7bdfc210000007',
    '0f7bfff7bdfc210002108',
    '0f7bfff7bdfc210021080',
    '0f7bfff7bdfc2101c0000',
    '0f7bfffffe00421e00007',
    '0f7bfffffe00421e02108',
    '0f7bfffffe00421e21080',
    '0f7bfffffe00421fc0000',
    '0f7bfffffe04210e00007',
    '0f7bfffffe04210e02108',
    '0f7bfffffe04210e21080',
    '0f7bfffffe04210fc0000',
    '0f7bfffffe04631000007',
    '0f7bfffffe04631002108',
    '0f7bfffffe04631021080',
    '0f7bfffffe046311c0000',
    '0f7bfffffe38000e00007',
    '0f7bfffffe38000e02108',
    '0f7bfffffe38000e21080',
    '0f7bfffffe38000fc0000',
    '0f7bfffffe38421000007',
    '0f7bfffffe38421002108',
    '0f7bfffffe38421021080',
    '0f7bfffffe384211c0000',
    '0f7bfffffe3c210000007',
    '0f7bfffffe3c210002108',
    '0f7bfffffe3c210021080',
    '0f7bfffffe3c2101c0000',
    '0f7bffffffc0421e00000',
    '0f7bffffffc4210e00000',
    '0f7bffffffc4631000000',
    '0f7bfffffff8000e00000',
    '0f7bfffffff8421000000',
    '0f7bfffffffc210000000',
    '1ef780739c04631fe318f',
    '1ef780739c38421fe318f',
    '1ef780739c3c210fe318f',
    '1ef780739c3c6311e318f',
    '1ef780739dc4631e2318f',
    '1ef780739dc4631fc210f',
    '1ef780739dc4631fe1087',
    '1ef780739dc4631fe3188',
    '1ef780739df8421e2318f',
    '1ef780739df8421fc210f',
    '1ef780739df8421fe1087',
    '1ef780739df8421fe3188',
    '1ef780739dfc210e2318f',
    '1ef780739dfc210fc210f',
    '1ef780739dfc210fe1087',
    '1ef780739dfc210fe3188',
    '1ef780739dfc63102318f',
    '1ef780739dfc6311c210f',
    '1ef780739dfc6311e1087',
    '1ef780739dfc6311e3188',
    '1ef7807bde04631e2318f',
    '1ef7807bde04631fc210f',
    '1ef7807bde04631fe1087',
    '1ef7807bde04631fe3188',
    '1ef7807bde38421e2318f',
    '1ef7807bde38421fc210f',
    '1ef7807bde38421fe1087',
    '1ef7807bde38421fe3188',
    '1ef7807bde3c210e2318f',
    '1ef7807bde3c210fc210f',
    '1ef7807bde3c210fe1087',
    '1ef7807bde3c210fe3188',
    '1ef7807bde3c63102318f',
    '1ef7807bde3c6311c210f',
    '1ef7807bde3c6311e1087',
    '1ef7807bde3c6311e3188',
    '1ef7807bdfc4631e0210f',
    '1ef7807bdfc4631e21087',
    '1ef7807bdfc4631e23188',
    '1ef7807bdfc4631fc0007',
    '1ef7807bdfc4631fc2108',
    '1ef7807bdfc4631fe1080',
    '1ef7807bdff8421e0210f',
    '1ef7807bdff8421e21087',
    '1ef7807bdff8421e23188',
    '1ef7807bdff8421fc0007',
    '1ef7807bdff8421fc2108',
    '1ef7807bdff8421fe1080',
    '1ef7807bdffc210e0210f',
    '1ef7807bdffc210e21087',
    '1ef7807bdffc210e23188',
    '1ef7807bdffc210fc0007',
    '1ef7807bdffc210fc2108',
    '1ef7807bdffc210fe1080',
    '1ef7807bdffc63100210f',
    '1ef7807bdffc631021087',
    '1ef7807bdffc631023188',
    '1ef7807bdffc6311c0007',
    '1ef7807bdffc6311c2108',
    '1ef7807bdffc6311e1080',
    '1ef780f7bc04631e2318f',
    '1ef780f7bc04631fc210f',
    '1ef780f7bc04631fe1087',
    '1ef780f7bc04631fe3188',
    '1ef780f7bc38421e2318f',
    '1ef780f7bc38421fc210f',
    '1ef780f7bc38421fe1087',
    '1ef780f7bc38421fe3188',
    '1ef780f7bc3c210e2318f',
    '1ef780f7bc3c210fc210f',
    '1ef780f7bc3c210fe1087',
    '1ef780f7bc3c210fe3188',
    '1ef780f7bc3c63102318f',
    '1ef780f7bc3c6311c210f',
    '1ef780f7bc3c6311e1087',
    '1ef780f7bc3c6311e3188',
    '1ef780f7bdc4631e0210f',
    '1ef780f7bdc4631e21087',
    '1ef780f7bdc4631e23188',
    '1ef780f7bdc4631fc0007',
    '1ef780f7bdc4631fc2108',
    '1ef780f7bdc4631fe1080',
    '1ef780f7bdf8421e0210f',
    '1ef780f7bdf8421e21087',
    '1ef780f7bdf8421e23188',
    '1ef780f7bdf8421fc0007',
    '1ef780f7bdf8421fc2108',
    '1ef780f7bdf8421fe1080',
    '1ef780f7bdfc210e0210f',
    '1ef780f7bdfc210e21087',
    '1ef780f7bdfc210e23188',
    '1ef780f7bdfc210fc0007',
    '1ef780f7bdfc210fc2108',
    '1ef780f7bdfc210fe1080',
    '1ef780f7bdfc63100210f',
    '1ef780f7bdfc631021087',
    '1ef780f7bdfc631023188',
    '1ef780f7bdfc6311c0007',
    '1ef780f7bdfc6311c2108',
    '1ef780f7bdfc6311e1080',
    '1ef780fffe04631e0210f',
    '1ef780fffe04631e21087',
    '1ef780fffe04631e23188',
    '1ef780fffe04631fc0007',
    '1ef780fffe04631fc2108',
    '1ef780fffe04631fe1080',
    '1ef780fffe38421e0210f',
    '1ef780fffe38421e21087',
    '1ef780fffe38421e23188',
    '1ef780fffe38421fc0007',
    '1ef780fffe38421fc2108',
    '1ef780fffe38421fe1080',
    '1ef780fffe3c210e0210f',
    '1ef780fffe3c210e21087',
    '1ef780fffe3c210e23188',
    '1ef780fffe3c210fc0007',
    '1ef780fffe3c210fc2108',
    '1ef780fffe3c210fe1080',
    '1ef780fffe3c63100210f',
    '1ef780fffe3c631021087',
    '1ef780fffe3c631023188',
    '1ef780fffe3c6311c0007',
    '1ef780fffe3c6311c2108',
    '1ef780fffe3c6311e1080',
    '1ef780ffffc4631e00007',
    '1ef780ffffc4631e02108',
    '1ef780ffffc4631e21080',
    '1ef780ffffc4631fc0000',
    '1ef780fffff8421e00007',
    '1ef780fffff8421e02108',
    '1ef780fffff8421e21080',
    '1ef780fffff8421fc0000',
    '1ef780fffffc210e00007',
    '1ef780fffffc210e02108',
    '1ef780fffffc210e21080',
    '1ef780fffffc210fc0000',
    '1ef780fffffc631000007',
    '1ef780fffffc631002108',
    '1ef780fffffc631021080',
    '1ef780fffffc6311c0000',
    '1ef787739c04631e2318f',
    '1ef787739c04631fc210f',
    '1ef787739c04631fe1087',
    '1ef787739c04631fe3188',
    '1ef787739c38421e2318f',
    '1ef787739c38421fc210f',
    '1ef787739c38421fe1087',
    '1ef787739c38421fe3188',
    '1ef787739c3c210e2318f',
    '1ef787739c3c210fc210f',
    '1ef787739c3c210fe1087',
    '1ef787739c3c210fe3188',
    '1ef787739c3c63102318f',
    '1ef787739c3c6311c210f',
    '1ef787739c3c6311e1087',
    '1ef787739c3c6311e3188',
    '1ef787739dc4631e0210f',
    '1ef787739dc4631e21087',
    '1ef787739dc4631e23188',
    '1ef787739dc4631fc0007',
    '1ef787739dc4631fc2108',
    '1ef787739dc4631fe1080',
    '1ef787739df8421e0210f',
    '1ef787739df8421e21087',
    '1ef787739df8421e23188',
    '1ef787739df8421fc0007',
    '1ef787739df8421fc2108',
    '1ef787739df8421fe1080',
    '1ef787739dfc210e0210f',
    '1ef787739dfc210e21087',
    '1ef787739dfc210e23188',
    '1ef787739dfc210fc0007',
    '1ef787739dfc210fc2108',
    '1ef787739dfc210fe1080',
    '1ef787739dfc63100210f',
    '1ef787739dfc631021087',
    '1ef787739dfc631023188',
    '1ef787739dfc6311c0007',
    '1ef787739dfc6311c2108',
    '1ef787739dfc6311e1080',
    '1ef7877bde04631e0210f',
    '1ef7877bde04631e21087',
    '1ef7877bde04631e23188',
    '1ef7877bde04631fc0007',
    '1ef7877bde04631fc2108',
    '1ef7877bde04631fe1080',
    '1ef7877bde38421e0210f',
    '1ef7877bde38421e21087',
    '1ef7877bde38421e23188',
    '1ef7877bde38421fc0007',
    '1ef7877bde38421fc2108',
    '1ef7877bde38421fe1080',
    '1ef7877bde3c210e0210f',
    '1ef7877bde3c210e21087',
    '1ef7877bde3c210e23188',
    '1ef7877bde3c210fc0007',
    '1ef7877bde3c210fc2108',
    '1ef7877bde3c210fe1080',
    '1ef7877bde3c63100210f',
    '1ef7877bde3c631021087',
    '1ef7877bde3c631023188',
    '1ef7877bde3c6311c0007',
    '1ef7877bde3c6311c2108',
    '1ef7877bde3c6311e1080',
    '1ef7877bdfc4631e00007',
    '1ef7877bdfc4631e02108',
    '1ef7877bdfc4631e21080',
    '1ef7877bdfc4631fc0000',
    '1ef7877bdff8421e00007',
    '1ef7877bdff8421e02108',
    '1ef7877bdff8421e21080',
    '1ef7877bdff8421fc0000',
    '1ef7877bdffc210e00007',
    '1ef7877bdffc210e02108',
    '1ef7877bdffc210e21080',
    '1ef7877bdffc210fc0000',
    '1ef7877bdffc631000007',
    '1ef7877bdffc631002108',
    '1ef7877bdffc631021080',
    '1ef7877bdffc6311c0000',
    '1ef787f7bc04631e0210f',
    '1ef787f7bc04631e21087',
    '1ef787f7bc04631e23188',
    '1ef787f7bc04631fc0007',
    '1ef787f7bc04631fc2108',
    '1ef787f7bc04631fe1080',
    '1ef787f7bc38421e0210f',
    '1ef787f7bc38421e21087',
    '1ef787f7bc38421e23188',
    '1ef787f7bc38421fc0007',
    '1ef787f7bc38421fc2108',
    '1ef787f7bc38421fe1080',
    '1ef787f7bc3c210e0210f',
    '1ef787f7bc3c210e21087',
    '1ef787f7bc3c210e23188',
    '1ef787f7bc3c210fc0007',
    '1ef787f7bc3c210fc2108',
    '1ef787f7bc3c210fe1080',
    '1ef787f7bc3c63100210f',
    '1ef787f7bc3c631021087',
    '1ef787f7bc3c631023188',
    '1ef787f7bc3c6311c0007',
    '1ef787f7bc3c6311c2108',
    '1ef787f7bc3c6311e1080',
    '1ef787f7bdc4631e00007',
    '1ef787f7bdc4631e02108',
    '1ef787f7bdc4631e21080',
    '1ef787f7bdc4631fc0000',
    '1ef787f7bdf8421e00007',
    '1ef787f7bdf8421e02108',
    '1ef787f7bdf8421e21080',
    '1ef787f7bdf8421fc0000',
    '1ef787f7bdfc210e00007',
    '1ef787f7bdfc210e02108',
    '1ef787f7bdfc210e21080',
    '1ef787f7bdfc210fc0000',
    '1ef787f7bdfc631000007',
    '1ef787f7bdfc631002108',
    '1ef787f7bdfc631021080',
    '1ef787f7bdfc6311c0000',
    '1ef787fffe04631e00007',
    '1ef787fffe04631e02108',
    '1ef787fffe04631e21080',
    '1ef787fffe04631fc0000',
    '1ef787fffe38421e00007',
    '1ef787fffe38421e02108',
    '1ef787fffe38421e21080',
    '1ef787fffe38421fc0000',
    '1ef787fffe3c210e00007',
    '1ef787fffe3c210e02108',
    '1ef787fffe3c210e21080',
    '1ef787fffe3c210fc0000',
    '1ef787fffe3c631000007',
    '1ef787fffe3c631002108',
    '1ef787fffe3c631021080',
    '1ef787fffe3c6311c0000',
    '1ef787ffffc4631e00000',
    '1ef787fffff8421e00000',
    '1ef787fffffc210e00000',
    '1ef787fffffc631000000',
    '1ef7b8739c00421fe318f',
    '1ef7b8739c04210fe318f',
    '1ef7b8739c046311e318f',
    '1ef7b8739c38000fe318f',
    '1ef7b8739c384211e318f',
    '1ef7b8739c3c2101e318f',
    '1ef7b8739dc0421e2318f',
    '1ef7b8739dc0421fc210f',
    '1ef7b8739dc0421fe1087',
    '1ef7b8739dc0421fe3188',
    '1ef7b8739dc4210e2318f',
    '1ef7b8739dc4210fc210f',
    '1ef7b8739dc4210fe1087',
    '1ef7b8739dc4210fe3188',
    '1ef7b8739dc463102318f',
    '1ef7b8739dc46311c210f',
    '1ef7b8739dc46311e1087',
    '1ef7b8739dc46311e3188',
    '1ef7b8739df8000e2318f',
    '1ef7b8739df8000fc210f',
    '1ef7b8739df8000fe1087',
    '1ef7b8739df8000fe3188',
    '1ef7b8739df842102318f',
    '1ef7b8739df84211c210f',
    '1ef7b8739df84211e1087',
    '1ef7b8739df84211e3188',
    '1ef7b8739dfc21002318f',
    '1ef7b8739dfc2101c210f',
    '1ef7b8739dfc2101e1087',
    '1ef7b8739dfc2101e3188',
    '1ef7b87bde00421e2318f',
    '1ef7b87bde00421fc210f',
    '1ef7b87bde00421fe1087',
    '1ef7b87bde00421fe3188',
    '1ef7b87bde04210e2318f',
    '1ef7b87bde04210fc210f',
    '1ef7b87bde04210fe1087',
    '1ef7b87bde04210fe3188',
    '1ef7b87bde0463102318f',
    '1ef7b87bde046311c210f',
    '1ef7b87bde046311e1087',
    '1ef7b87bde046311e3188',
    '1ef7b87bde38000e2318f',
    '1ef7b87bde38000fc210f',
    '1ef7b87bde38000fe1087',
    '1ef7b87bde38000fe3188',
    '1ef7b87bde3842102318f',
    '1ef7b87bde384211c210f',
    '1ef7b87bde384211e1087',
    '1ef7b87bde384211e3188',
    '1ef7b87bde3c21002318f',
    '1ef7b87bde3c2101c210f',
    '1ef7b87bde3c2101e1087',
    '1ef7b87bde3c2101e3188',
    '1ef7b87bdfc0421e0210f',
    '1ef7b87bdfc0421e21087',
    '1ef7b87bdfc0421e23188',
    '1ef7b87bdfc0421fc0007',
    '1ef7b87bdfc0421fc2108',
    '1ef7b87bdfc0421fe1080',
    '1ef7b87bdfc4210e0210f',
    '1ef7b87bdfc4210e21087',
    '1ef7b87bdfc4210e23188',
    '1ef7b87bdfc4210fc0007',
    '1ef7b87bdfc4210fc2108',
    '1ef7b87bdfc4210fe1080',
    '1ef7b87bdfc463100210f',
    '1ef7b87bdfc4631021087',
    '1ef7b87bdfc4631023188',
    '1ef7b87bdfc46311c0007',
    '1ef7b87bdfc46311c2108',
    '1ef7b87bdfc46311e1080',
    '1ef7b87bdff8000e0210f',
    '1ef7b87bdff8000e21087',
    '1ef7b87bdff8000e23188',
    '1ef7b87bdff8000fc0007',
    '1ef7b87bdff8000fc2108',
    '1ef7b87bdff8000fe1080',
    '1ef7b87bdff842100210f',
    '1ef7b87bdff8421021087',
    '1ef7b87bdff8421023188',
    '1ef7b87bdff84211c0007',
    '1ef7b87bdff84211c2108',
    '1ef7b87bdff84211e1080',
    '1ef7b87bdffc21000210f',
    '1ef7b87bdffc210021087',
    '1ef7b87bdffc210023188',
    '1ef7b87bdffc2101c0007',
    '1ef7b87bdffc2101c2108',
    '1ef7b87bdffc2101e1080',
    '1ef7b8f7bc00421e2318f',
    '1ef7b8f7bc00421fc210f',
    '1ef7b8f7bc00421fe1087',
    '1ef7b8f7bc00421fe3188',
    '1ef7b8f7bc04210e2318f',
    '1ef7b8f7bc04210fc210f',
    '1ef7b8f7bc04210fe1087',
    '1ef7b8f7bc04210fe3188',
    '1ef7b8f7bc0463102318f',
    '1ef7b8f7bc046311c210f',
    '1ef7b8f7bc046311e1087',
    '1ef7b8f7bc046311e3188',
    '1ef7b8f7bc38000e2318f',
    '1ef7b8f7bc38000fc210f',
    '1ef7b8f7bc38000fe1087',
    '1ef7b8f7bc38000fe3188',
    '1ef7b8f7bc3842102318f',
    '1ef7b8f7bc384211c210f',
    '1ef7b8f7bc384211e1087',
    '1ef7b8f7bc384211e3188',
    '1ef7b8f7bc3c21002318f',
    '1ef7b8f7bc3c2101c210f',
    '1ef7b8f7bc3c2101e1087',
    '1ef7b8f7bc3c2101e3188',
    '1ef7b8f7bdc0421e0210f',
    '1ef7b8f7bdc0421e21087',
    '1ef7b8f7bdc0421e23188',
    '1ef7b8f7bdc0421fc0007',
    '1ef7b8f7bdc0421fc2108',
    '1ef7b8f7bdc0421fe1080',
    '1ef7b8f7bdc4210e0210f',
    '1ef7b8f7bdc4210e21087',
    '1ef7b8f7bdc4210e23188',
    '1ef7b8f7bdc4210fc0007',
    '1ef7b8f7bdc4210fc2108',
    '1ef7b8f7bdc4210fe1080',
    '1ef7b8f7bdc463100210f',
    '1ef7b8f7bdc4631021087',
    '1ef7b8f7bdc4631023188',
    '1ef7b8f7bdc46311c0007',
    '1ef7b8f7bdc46311c2108',
    '1ef7b8f7bdc46311e1080',
    '1ef7b8f7bdf8000e0210f',
    '1ef7b8f7bdf8000e21087',
    '1ef7b8f7bdf8000e23188',
    '1ef7b8f7bdf8000fc0007',
    '1ef7b8f7bdf8000fc2108',
    '1ef7b8f7bdf8000fe1080',
    '1ef7b8f7bdf842100210f',
    '1ef7b8f7bdf8421021087',
    '1ef7b8f7bdf8421023188',
    '1ef7b8f7bdf84211c0007',
    '1ef7b8f7bdf84211c2108',
    '1ef7b8f7bdf84211e1080',
    '1ef7b8f7bdfc21000210f',
    '1ef7b8f7bdfc210021087',
    '1ef7b8f7bdfc210023188',
    '1ef7b8f7bdfc2101c0007',
    '1ef7b8f7bdfc2101c2108',
    '1ef7b8f7bdfc2101e1080',
    '1ef7b8fffe00421e0210f',
    '1ef7b8fffe00421e21087',
    '1ef7b8fffe00421e23188',
    '1ef7b8fffe00421fc0007',
    '1ef7b8fffe00421fc2108',
    '1ef7b8fffe00421fe1080',
    '1ef7b8fffe04210e0210f',
    '1ef7b8fffe04210e21087',
    '1ef7b8fffe04210e23188',
    '1ef7b8fffe04210fc0007',
    '1ef7b8fffe04210fc2108',
    '1ef7b8fffe04210fe1080',
    '1ef7b8fffe0463100210f',
    '1ef7b8fffe04631021087',
    '1ef7b8fffe04631023188',
    '1ef7b8fffe046311c0007',
    '1ef7b8fffe046311c2108',
    '1ef7b8fffe046311e1080',
    '1ef7b8fffe38000e0210f',
    '1ef7b8fffe38000e21087',
    '1ef7b8fffe38000e23188',
    '1ef7b8fffe38000fc0007',
    '1ef7b8fffe38000fc2108',
    '1ef7b8fffe38000fe1080',
    '1ef7b8fffe3842100210f',
    '1ef7b8fffe38421021087',
    '1ef7b8fffe38421023188',
    '1ef7b8fffe384211c0007',
    '1ef7b8fffe384211c2108',
    '1ef7b8fffe384211e1080',
    '1ef7b8fffe3c21000210f',
    '1ef7b8fffe3c210021087',
    '1ef7b8fffe3c210023188',
    '1ef7b8fffe3c2101c0007',
    '1ef7b8fffe3c2101c2108',
    '1ef7b8fffe3c2101e1080',
    '1ef7b8ffffc0421e00007',
    '1ef7b8ffffc0421e02108',
    '1ef7b8ffffc0421e21080',
    '1ef7b8ffffc0421fc0000',
    '1ef7b8ffffc4210e00007',
    '1ef7b8ffffc4210e02108',
    '1ef7b8ffffc4210e21080',
    '1ef7b8ffffc4210fc0000',
    '1ef7b8ffffc4631000007',
    '1ef7b8ffffc4631002108',
    '1ef7b8ffffc4631021080',
    '1ef7b8ffffc46311c0000',
    '1ef7b8fffff8000e00007',
    '1ef7b8fffff8000e02108',
    '1ef7b8fffff8000e21080',
    '1ef7b8fffff8000fc0000',
    '1ef7b8fffff8421000007',
    '1ef7b8fffff8421002108',
    '1ef7b8fffff8421021080',
    '1ef7b8fffff84211c0000',
    '1ef7b8fffffc210000007',
    '1ef7b8fffffc210002108',
    '1ef7b8fffffc210021080',
    '1ef7b8fffffc2101c0000',
    '1ef7bf739c00421e2318f',
    '1ef7bf739c00421fc210f',
    '1ef7bf739c00421fe1087',
    '1ef7bf739c00421fe3188',
    '1ef7bf739c04210e2318f',
    '1ef7bf739c04210fc210f',
    '1ef7bf739c04210fe1087',
    '1ef7bf739c04210fe3188',
    '1ef7bf739c0463102318f',
    '1ef7bf739c046311c210f',
    '1ef7bf739c046311e1087',
    '1ef7bf739c046311e3188',
    '1ef7bf739c38000e2318f',
    '1ef7bf739c38000fc210f',
    '1ef7bf739c38000fe1087',
    '1ef7bf739c38000fe3188',
    '1ef7bf739c3842102318f',
    '1ef7bf739c384211c210f',
    '1ef7bf739c384211e1087',
    '1ef7bf739c384211e3188',
    '1ef7bf739c3c21002318f',
    '1ef7bf739c3c2101c210f',
    '1ef7bf739c3c2101e1087',
    '1ef7bf739c3c2101e3188',
    '1ef7bf739dc0421e0210f',
    '1ef7bf739dc0421e21087',
    '1ef7bf739dc0421e23188',
    '1ef7bf739dc0421fc0007',
    '1ef7bf739dc0421fc2108',
    '1ef7bf739dc0421fe1080',
    '1ef7bf739dc4210e0210f',
    '1ef7bf739dc4210e21087',
    '1ef7bf739dc4210e23188',
    '1ef7bf739dc4210fc0007',
    '1ef7bf739dc4210fc2108',
    '1ef7bf739dc4210fe1080',
    '1ef7bf739dc463100210f',
    '1ef7bf739dc4631021087',
    '1ef7bf739dc4631023188',
    '1ef7bf739dc46311c0007',
    '1ef7bf739dc46311c2108',
    '1ef7bf739dc46311e1080',
    '1ef7bf739df8000e0210f',
    '1ef7bf739df8000e21087',
    '1ef7bf739df8000e23188',
    '1ef7bf739df8000fc0007',
    '1ef7bf739df8000fc2108',
    '1ef7bf739df8000fe1080',
    '1ef7bf739df842100210f',
    '1ef7bf739df8421021087',
    '1ef7bf739df8421023188',
    '1ef7bf739df84211c0007',
    '1ef7bf739df84211c2108',
    '1ef7bf739df84211e1080',
    '1ef7bf739dfc21000210f',
    '1ef7bf739dfc210021087',
    '1ef7bf739dfc210023188',
    '1ef7bf739dfc2101c0007',
    '1ef7bf739dfc2101c2108',
    '1ef7bf739dfc2101e1080',
    '1ef7bf7bde00421e0210f',
    '1ef7bf7bde00421e21087',
    '1ef7bf7bde00421e23188',
    '1ef7bf7bde00421fc0007',
    '1ef7bf7bde00421fc2108',
    '1ef7bf7bde00421fe1080',
    '1ef7bf7bde04210e0210f',
    '1ef7bf7bde04210e21087',
    '1ef7bf7bde04210e23188',
    '1ef7bf7bde04210fc0007',
    '1ef7bf7bde04210fc2108',
    '1ef7bf7bde04210fe1080',
    '1ef7bf7bde0463100210f',
    '1ef7bf7bde04631021087',
    '1ef7bf7bde04631023188',
    '1ef7bf7bde046311c0007',
    '1ef7bf7bde046311c2108',
    '1ef7bf7bde046311e1080',
    '1ef7bf7bde38000e0210f',
    '1ef7bf7bde38000e21087',
    '1ef7bf7bde38000e23188',
    '1ef7bf7bde38000fc0007',
    '1ef7bf7bde38000fc2108',
    '1ef7bf7bde38000fe1080',
    '1ef7bf7bde3842100210f',
    '1ef7bf7bde38421021087',
    '1ef7bf7bde38421023188',
    '1ef7bf7bde384211c0007',
    '1ef7bf7bde384211c2108',
    '1ef7bf7bde384211e1080',
    '1ef7bf7bde3c21000210f',
    '1ef7bf7bde3c210021087',
    '1ef7bf7bde3c210023188',
    '1ef7bf7bde3c2101c0007',
    '1ef7bf7bde3c2101c2108',
    '1ef7bf7bde3c2101e1080',
    '1ef7bf7bdfc0421e00007',
    '1ef7bf7bdfc0421e02108',
    '1ef7bf7bdfc0421e21080',
    '1ef7bf7bdfc0421fc0000',
    '1ef7bf7bdfc4210e00007',
    '1ef7bf7bdfc4210e02108',
    '1ef7bf7bdfc4210e21080',
    '1ef7bf7bdfc4210fc0000',
    '1ef7bf7bdfc4631000007',
    '1ef7bf7bdfc4631002108',
    '1ef7bf7bdfc4631021080',
    '1ef7bf7bdfc46311c0000',
    '1ef7bf7bdff8000e00007',
    '1ef7bf7bdff8000e02108',
    '1ef7bf7bdff8000e21080',
    '1ef7bf7bdff8000fc0000',
    '1ef7bf7bdff8421000007',
    '1ef7bf7bdff8421002108',
    '1ef7bf7bdff8421021080',
    '1ef7bf7bdff84211c0000',
    '1ef7bf7bdffc210000007',
    '1ef7bf7bdffc210002108',
    '1ef7bf7bdffc210021080',
    '1ef7bf7bdffc2101c0000',
    '1ef7bff7bc00421e0210f',
    '1ef7bff7bc00421e21087',
    '1ef7bff7bc00421e23188',
    '1ef7bff7bc00421fc0007',
    '1ef7bff7bc00421fc2108',
    '1ef7bff7bc00421fe1080',
    '1ef7bff7bc04210e0210f',
    '1ef7bff7bc04210e21087',
    '1ef7bff7bc04210e23188',
    '1ef7bff7bc04210fc0007',
    '1ef7bff7bc04210fc2108',
    '1ef7bff7bc04210fe1080',
    '1ef7bff7bc0463100210f',
    '1ef7bff7bc04631021087',
    '1ef7bff7bc04631023188',
    '1ef7bff7bc046311c0007',
    '1ef7bff7bc046311c2108',
    '1ef7bff7bc046311e1080',
    '1ef7bff7bc38000e0210f',
    '1ef7bff7bc38000e21087',
    '1ef7bff7bc38000e23188',
    '1ef7bff7bc38000fc0007',
    '1ef7bff7bc38000fc2108',
    '1ef7bff7bc38000fe1080',
    '1ef7bff7bc3842100210f',
    '1ef7bff7bc38421021087',
    '1ef7bff7bc38421023188',
    '1ef7bff7bc384211c0007',
    '1ef7bff7bc384211c2108',
    '1ef7bff7bc384211e1080',
    '1ef7bff7bc3c21000210f',
    '1ef7bff7bc3c210021087',
    '1ef7bff7bc3c210023188',
    '1ef7bff7bc3c2101c0007',
    '1ef7bff7bc3c2101c2108',
    '1ef7bff7bc3c2101e1080',
    '1ef7bff7bdc0421e00007',
    '1ef7bff7bdc0421e02108',
    '1ef7bff7bdc0421e21080',
    '1ef7bff7bdc0421fc0000',
    '1ef7bff7bdc4210e00007',
    '1ef7bff7bdc4210e02108',
    '1ef7bff7bdc4210e21080',
    '1ef7bff7bdc4210fc0000',
    '1ef7bff7bdc4631000007',
    '1ef7bff7bdc4631002108',
    '1ef7bff7bdc4631021080',
    '1ef7bff7bdc46311c0000',
    '1ef7bff7bdf8000e00007',
    '1ef7bff7bdf8000e02108',
    '1ef7bff7bdf8000e21080',
    '1ef7bff7bdf8000fc0000',
    '1ef7bff7bdf8421000007',
    '1ef7bff7bdf8421002108',
    '1ef7bff7bdf8421021080',
    '1ef7bff7bdf84211c0000',
    '1ef7bff7bdfc210000007',
    '1ef7bff7bdfc210002108',
    '1ef7bff7bdfc210021080',
    '1ef7bff7bdfc2101c0000',
    '1ef7bffffe00421e00007',
    '1ef7bffffe00421e02108',
    '1ef7bffffe00421e21080',
    '1ef7bffffe00421fc0000',
    '1ef7bffffe04210e00007',
    '1ef7bffffe04210e02108',
    '1ef7bffffe04210e21080',
    '1ef7bffffe04210fc0000',
    '1ef7bffffe04631000007',
    '1ef7bffffe04631002108',
    '1ef7bffffe04631021080',
    '1ef7bffffe046311c0000',
    '1ef7bffffe38000e00007',
    '1ef7bffffe38000e02108',
    '1ef7bffffe38000e21080',
    '1ef7bffffe38000fc0000',
    '1ef7bffffe38421000007',
    '1ef7bffffe38421002108',
    '1ef7bffffe38421021080',
    '1ef7bffffe384211c0000',
    '1ef7bffffe3c210000007',
    '1ef7bffffe3c210002108',
    '1ef7bffffe3c210021080',
    '1ef7bffffe3c2101c0000',
    '1ef7bfffffc0421e00000',
    '1ef7bfffffc4210e00000',
    '1ef7bfffffc4631000000',
    '1ef7bffffff8000e00000',
    '1ef7bffffff8421000000',
    '1ef7bffffffc210000000',
    '1fffc0739c00421fe318f',
    '1fffc0739c04210fe318f',
    '1fffc0739c046311e318f',
    '1fffc0739c38000fe318f',
    '1fffc0739c384211e318f',
    '1fffc0739c3c2101e318f',
    '1fffc0739dc0421e2318f',
    '1fffc0739dc0421fc210f',
    '1fffc0739dc0421fe1087',
    '1fffc0739dc0421fe3188',
    '1fffc0739dc4210e2318f',
    '1fffc0739dc4210fc210f',
    '1fffc0739dc4210fe1087',
    '1fffc0739dc4210fe3188',
    '1fffc0739dc463102318f',
    '1fffc0739dc46311c210f',
    '1fffc0739dc46311e1087',
    '1fffc0739dc46311e3188',
    '1fffc0739df8000e2318f',
    '1fffc0739df8000fc210f',
    '1fffc0739df8000fe1087',
    '1fffc0739df8000fe3188',
    '1fffc0739df842102318f',
    '1fffc0739df84211c210f',
    '1fffc0739df84211e1087',
    '1fffc0739df84211e3188',
    '1fffc0739dfc21002318f',
    '1fffc0739dfc2101c210f',
    '1fffc0739dfc2101e1087',
    '1fffc0739dfc2101e3188',
    '1fffc07bde00421e2318f',
    '1fffc07bde00421fc210f',
    '1fffc07bde00421fe1087',
    '1fffc07bde00421fe3188',
    '1fffc07bde04210e2318f',
    '1fffc07bde04210fc210f',
    '1fffc07bde04210fe1087',
    '1fffc07bde04210fe3188',
    '1fffc07bde0463102318f',
    '1fffc07bde046311c210f',
    '1fffc07bde046311e1087',
    '1fffc07bde046311e3188',
    '1fffc07bde38000e2318f',
    '1fffc07bde38000fc210f',
    '1fffc07bde38000fe1087',
    '1fffc07bde38000fe3188',
    '1fffc07bde3842102318f',
    '1fffc07bde384211c210f',
    '1fffc07bde384211e1087',
    '1fffc07bde384211e3188',
    '1fffc07bde3c21002318f',
    '1fffc07bde3c2101c210f',
    '1fffc07bde3c2101e1087',
    '1fffc07bde3c2101e3188',
    '1fffc07bdfc0421e0210f',
    '1fffc07bdfc0421e21087',
    '1fffc07bdfc0421e23188',
    '1fffc07bdfc0421fc0007',
    '1fffc07bdfc0421fc2108',
    '1fffc07bdfc0421fe1080',
    '1fffc07bdfc4210e0210f',
    '1fffc07bdfc4210e21087',
    '1fffc07bdfc4210e23188',
    '1fffc07bdfc4210fc0007',
    '1fffc07bdfc4210fc2108',
    '1fffc07bdfc4210fe1080',
    '1fffc07bdfc463100210f',
    '1fffc07bdfc4631021087',
    '1fffc07bdfc4631023188',
    '1fffc07bdfc46311c0007',
    '1fffc07bdfc46311c2108',
    '1fffc07bdfc46311e1080',
    '1fffc07bdff8000e0210f',
    '1fffc07bdff8000e21087',
    '1fffc07bdff8000e23188',
    '1fffc07bdff8000fc0007',
    '1fffc07bdff8000fc2108',
    '1fffc07bdff8000fe1080',
    '1fffc07bdff842100210f',
    '1fffc07bdff8421021087',
    '1fffc07bdff8421023188',
    '1fffc07bdff84211c0007',
    '1fffc07bdff84211c2108',
    '1fffc07bdff84211e1080',
    '1fffc07bdffc21000210f',
    '1fffc07bdffc210021087',
    '1fffc07bdffc210023188',
    '1fffc07bdffc2101c0007',
    '1fffc07bdffc2101c2108',
    '1fffc07bdffc2101e1080',
    '1fffc0f7bc00421e2318f',
    '1fffc0f7bc00421fc210f',
    '1fffc0f7bc00421fe1087',
    '1fffc0f7bc00421fe3188',
    '1fffc0f7bc04210e2318f',
    '1fffc0f7bc04210fc210f',
    '1fffc0f7bc04210fe1087',
    '1fffc0f7bc04210fe3188',
    '1fffc0f7bc0463102318f',
    '1fffc0f7bc046311c210f',
    '1fffc0f7bc046311e1087',
    '1fffc0f7bc046311e3188',
    '1fffc0f7bc38000e2318f',
    '1fffc0f7bc38000fc210f',
    '1fffc0f7bc38000fe1087',
    '1fffc0f7bc38000fe3188',
    '1fffc0f7bc3842102318f',
    '1fffc0f7bc384211c210f',
    '1fffc0f7bc384211e1087',
    '1fffc0f7bc384211e3188',
    '1fffc0f7bc3c21002318f',
    '1fffc0f7bc3c2101c210f',
    '1fffc0f7bc3c2101e1087',
    '1fffc0f7bc3c2101e3188',
    '1fffc0f7bdc0421e0210f',
    '1fffc0f7bdc0421e21087',
    '1fffc0f7bdc0421e23188',
    '1fffc0f7bdc0421fc0007',
    '1fffc0f7bdc0421fc2108',
    '1fffc0f7bdc0421fe1080',
    '1fffc0f7bdc4210e0210f',
    '1fffc0f7bdc4210e21087',
    '1fffc0f7bdc4210e23188',
    '1fffc0f7bdc4210fc0007',
    '1fffc0f7bdc4210fc2108',
    '1fffc0f7bdc4210fe1080',
    '1fffc0f7bdc463100210f',
    '1fffc0f7bdc4631021087',
    '1fffc0f7bdc4631023188',
    '1fffc0f7bdc46311c0007',
    '1fffc0f7bdc46311c2108',
    '1fffc0f7bdc46311e1080',
    '1fffc0f7bdf8000e0210f',
    '1fffc0f7bdf8000e21087',
    '1fffc0f7bdf8000e23188',
    '1fffc0f7bdf8000fc0007',
    '1fffc0f7bdf8000fc2108',
    '1fffc0f7bdf8000fe1080',
    '1fffc0f7bdf842100210f',
    '1fffc0f7bdf8421021087',
    '1fffc0f7bdf8421023188',
    '1fffc0f7bdf84211c0007',
    '1fffc0f7bdf84211c2108',
    '1fffc0f7bdf84211e1080',
    '1fffc0f7bdfc21000210f',
    '1fffc0f7bdfc210021087',
    '1fffc0f7bdfc210023188',
    '1fffc0f7bdfc2101c0007',
    '1fffc0f7bdfc2101c2108',
    '1fffc0f7bdfc2101e1080',
    '1fffc0fffe00421e0210f',
    '1fffc0fffe00421e21087',
    '1fffc0fffe00421e23188',
    '1fffc0fffe00421fc0007',
    '1fffc0fffe00421fc2108',
    '1fffc0fffe00421fe1080',
    '1fffc0fffe04210e0210f',
    '1fffc0fffe04210e21087',
    '1fffc0fffe04210e23188',
    '1fffc0fffe04210fc0007',
    '1fffc0fffe04210fc2108',
    '1fffc0fffe04210fe1080',
    '1fffc0fffe0463100210f',
    '1fffc0fffe04631021087',
    '1fffc0fffe04631023188',
    '1fffc0fffe046311c0007',
    '1fffc0fffe046311c2108',
    '1fffc0fffe046311e1080',
    '1fffc0fffe38000e0210f',
    '1fffc0fffe38000e21087',
    '1fffc0fffe38000e23188',
    '1fffc0fffe38000fc0007',
    '1fffc0fffe38000fc2108',
    '1fffc0fffe38000fe1080',
    '1fffc0fffe3842100210f',
    '1fffc0fffe38421021087',
    '1fffc0fffe38421023188',
    '1fffc0fffe384211c0007',
    '1fffc0fffe384211c2108',
    '1fffc0fffe384211e1080',
    '1fffc0fffe3c21000210f',
    '1fffc0fffe3c210021087',
    '1fffc0fffe3c210023188',
    '1fffc0fffe3c2101c0007',
    '1fffc0fffe3c2101c2108',
    '1fffc0fffe3c2101e1080',
    '1fffc0ffffc0421e00007',
    '1fffc0ffffc0421e02108',
    '1fffc0ffffc0421e21080',
    '1fffc0ffffc0421fc0000',
    '1fffc0ffffc4210e00007',
    '1fffc0ffffc4210e02108',
    '1fffc0ffffc4210e21080',
    '1fffc0ffffc4210fc0000',
    '1fffc0ffffc4631000007',
    '1fffc0ffffc4631002108',
    '1fffc0ffffc4631021080',
    '1fffc0ffffc46311c0000',
    '1fffc0fffff8000e00007',
    '1fffc0fffff8000e02108',
    '1fffc0fffff8000e21080',
    '1fffc0fffff8000fc0000',
    '1fffc0fffff8421000007',
    '1fffc0fffff8421002108',
    '1fffc0fffff8421021080',
    '1fffc0fffff84211c0000',
    '1fffc0fffffc210000007',
    '1fffc0fffffc210002108',
    '1fffc0fffffc210021080',
    '1fffc0fffffc2101c0000',
    '1fffc7739c00421e2318f',
    '1fffc7739c00421fc210f',
    '1fffc7739c00421fe1087',
    '1fffc7739c00421fe3188',
    '1fffc7739c04210e2318f',
    '1fffc7739c04210fc210f',
    '1fffc7739c04210fe1087',
    '1fffc7739c04210fe3188',
    '1fffc7739c0463102318f',
    '1fffc7739c046311c210f',
    '1fffc7739c046311e1087',
    '1fffc7739c046311e3188',
    '1fffc7739c38000e2318f',
    '1fffc7739c38000fc210f',
    '1fffc7739c38000fe1087',
    '1fffc7739c38000fe3188',
    '1fffc7739c3842102318f',
    '1fffc7739c384211c210f',
    '1fffc7739c384211e1087',
    '1fffc7739c384211e3188',
    '1fffc7739c3c21002318f',
    '1fffc7739c3c2101c210f',
    '1fffc7739c3c2101e1087',
    '1fffc7739c3c2101e3188',
    '1fffc7739dc0421e0210f',
    '1fffc7739dc0421e21087',
    '1fffc7739dc0421e23188',
    '1fffc7739dc0421fc0007',
    '1fffc7739dc0421fc2108',
    '1fffc7739dc0421fe1080',
    '1fffc7739dc4210e0210f',
    '1fffc7739dc4210e21087',
    '1fffc7739dc4210e23188',
    '1fffc7739dc4210fc0007',
    '1fffc7739dc4210fc2108',
    '1fffc7739dc4210fe1080',
    '1fffc7739dc463100210f',
    '1fffc7739dc4631021087',
    '1fffc7739dc4631023188',
    '1fffc7739dc46311c0007',
    '1fffc7739dc46311c2108',
    '1fffc7739dc46311e1080',
    '1fffc7739df8000e0210f',
    '1fffc7739df8000e21087',
    '1fffc7739df8000e23188',
    '1fffc7739df8000fc0007',
    '1fffc7739df8000fc2108',
    '1fffc7739df8000fe1080',
    '1fffc7739df842100210f',
    '1fffc7739df8421021087',
    '1fffc7739df8421023188',
    '1fffc7739df84211c0007',
    '1fffc7739df84211c2108',
    '1fffc7739df84211e1080',
    '1fffc7739dfc21000210f',
    '1fffc7739dfc210021087',
    '1fffc7739dfc210023188',
    '1fffc7739dfc2101c0007',
    '1fffc7739dfc2101c2108',
    '1fffc7739dfc2101e1080',
    '1fffc77bde00421e0210f',
    '1fffc77bde00421e21087',
    '1fffc77bde00421e23188',
    '1fffc77bde00421fc0007',
    '1fffc77bde00421fc2108',
    '1fffc77bde00421fe1080',
    '1fffc77bde04210e0210f',
    '1fffc77bde04210e21087',
    '1fffc77bde04210e23188',
    '1fffc77bde04210fc0007',
    '1fffc77bde04210fc2108',
    '1fffc77bde04210fe1080',
    '1fffc77bde0463100210f',
    '1fffc77bde04631021087',
    '1fffc77bde04631023188',
    '1fffc77bde046311c0007',
    '1fffc77bde046311c2108',
    '1fffc77bde046311e1080',
    '1fffc77bde38000e0210f',
    '1fffc77bde38000e21087',
    '1fffc77bde38000e23188',
    '1fffc77bde38000fc0007',
    '1fffc77bde38000fc2108',
    '1fffc77bde38000fe1080',
    '1fffc77bde3842100210f',
    '1fffc77bde38421021087',
    '1fffc77bde38421023188',
    '1fffc77bde384211c0007',
    '1fffc77bde384211c2108',
    '1fffc77bde384211e1080',
    '1fffc77bde3c21000210f',
    '1fffc77bde3c210021087',
    '1fffc77bde3c210023188',
    '1fffc77bde3c2101c0007',
    '1fffc77bde3c2101c2108',
    '1fffc77bde3c2101e1080',
    '1fffc77bdfc0421e00007',
    '1fffc77bdfc0421e02108',
    '1fffc77bdfc0421e21080',
    '1fffc77bdfc0421fc0000',
    '1fffc77bdfc4210e00007',
    '1fffc77bdfc4210e02108',
    '1fffc77bdfc4210e21080',
    '1fffc77bdfc4210fc0000',
    '1fffc77bdfc4631000007',
    '1fffc77bdfc4631002108',
    '1fffc77bdfc4631021080',
    '1fffc77bdfc46311c0000',
    '1fffc77bdff8000e00007',
    '1fffc77bdff8000e02108',
    '1fffc77bdff8000e21080',
    '1fffc77bdff8000fc0000',
    '1fffc77bdff8421000007',
    '1fffc77bdff8421002108',
    '1fffc77bdff8421021080',
    '1fffc77bdff84211c0000',
    '1fffc77bdffc210000007',
    '1fffc77bdffc210002108',
    '1fffc77bdffc210021080',
    '1fffc77bdffc2101c0000',
    '1fffc7f7bc00421e0210f',
    '1fffc7f7bc00421e21087',
    '1fffc7f7bc00421e23188',
    '1fffc7f7bc00421fc0007',
    '1fffc7f7bc00421fc2108',
    '1fffc7f7bc00421fe1080',
    '1fffc7f7bc04210e0210f',
    '1fffc7f7bc04210e21087',
    '1fffc7f7bc04210e23188',
    '1fffc7f7bc04210fc0007',
    '1fffc7f7bc04210fc2108',
    '1fffc7f7bc04210fe1080',
    '1fffc7f7bc0463100210f',
    '1fffc7f7bc04631021087',
    '1fffc7f7bc04631023188',
    '1fffc7f7bc046311c0007',
    '1fffc7f7bc046311c2108',
    '1fffc7f7bc046311e1080',
    '1fffc7f7bc38000e0210f',
    '1fffc7f7bc38000e21087',
    '1fffc7f7bc38000e23188',
    '1fffc7f7bc38000fc0007',
    '1fffc7f7bc38000fc2108',
    '1fffc7f7bc38000fe1080',
    '1fffc7f7bc3842100210f',
    '1fffc7f7bc38421021087',
    '1fffc7f7bc38421023188',
    '1fffc7f7bc384211c0007',
    '1fffc7f7bc384211c2108',
    '1fffc7f7bc384211e1080',
    '1fffc7f7bc3c21000210f',
    '1fffc7f7bc3c210021087',
    '1fffc7f7bc3c210023188',
    '1fffc7f7bc3c2101c0007',
    '1fffc7f7bc3c2101c2108',
    '1fffc7f7bc3c2101e1080',
    '1fffc7f7bdc0421e00007',
    '1fffc7f7bdc0421e02108',
    '1fffc7f7bdc0421e21080',
    '1fffc7f7bdc0421fc0000',
    '1fffc7f7bdc4210e00007',
    '1fffc7f7bdc4210e02108',
    '1fffc7f7bdc4210e21080',
    '1fffc7f7bdc4210fc0000',
    '1fffc7f7bdc4631000007',
    '1fffc7f7bdc4631002108',
    '1fffc7f7bdc4631021080',
    '1fffc7f7bdc46311c0000',
    '1fffc7f7bdf8000e00007',
    '1fffc7f7bdf8000e02108',
    '1fffc7f7bdf8000e21080',
    '1fffc7f7bdf8000fc0000',
    '1fffc7f7bdf8421000007',
    '1fffc7f7bdf8421002108',
    '1fffc7f7bdf8421021080',
    '1fffc7f7bdf84211c0000',
    '1fffc7f7bdfc210000007',
    '1fffc7f7bdfc210002108',
    '1fffc7f7bdfc210021080',
    '1fffc7f7bdfc2101c0000',
    '1fffc7fffe00421e00007',
    '1fffc7fffe00421e02108',
    '1fffc7fffe00421e21080',
    '1fffc7fffe00421fc0000',
    '1fffc7fffe04210e00007',
    '1fffc7fffe04210e02108',
    '1fffc7fffe04210e21080',
    '1fffc7fffe04210fc0000',
    '1fffc7fffe04631000007',
    '1fffc7fffe04631002108',
    '1fffc7fffe04631021080',
    '1fffc7fffe046311c0000',
    '1fffc7fffe38000e00007',
    '1fffc7fffe38000e02108',
    '1fffc7fffe38000e21080',
    '1fffc7fffe38000fc0000',
    '1fffc7fffe38421000007',
    '1fffc7fffe38421002108',
    '1fffc7fffe38421021080',
    '1fffc7fffe384211c0000',
    '1fffc7fffe3c210000007',
    '1fffc7fffe3c210002108',
    '1fffc7fffe3c210021080',
    '1fffc7fffe3c2101c0000',
    '1fffc7ffffc0421e00000',
    '1fffc7ffffc4210e00000',
    '1fffc7ffffc4631000000',
    '1fffc7fffff8000e00000',
    '1fffc7fffff8421000000',
    '1fffc7fffffc210000000',
    '1ffff8739c00000fe318f',
    '1ffff8739c004211e318f',
    '1ffff8739c042101e318f',
    '1ffff8739c380001e318f',
    '1ffff8739dc0000e2318f',
    '1ffff8739dc0000fc210f',
    '1ffff8739dc0000fe1087',
    '1ffff8739dc0000fe3188',
    '1ffff8739dc042102318f',
    '1ffff8739dc04211c210f',
    '1ffff8739dc04211e1087',
    '1ffff8739dc04211e3188',
    '1ffff8739dc421002318f',
    '1ffff8739dc42101c210f',
    '1ffff8739dc42101e1087',
    '1ffff8739dc42101e3188',
    '1ffff8739df800002318f',
    '1ffff8739df80001c210f',
    '1ffff8739df80001e1087',
    '1ffff8739df80001e3188',
    '1ffff87bde00000e2318f',
    '1ffff87bde00000fc210f',
    '1ffff87bde00000fe1087',
    '1ffff87bde00000fe3188',
    '1ffff87bde0042102318f',
    '1ffff87bde004211c210f',
    '1ffff87bde004211e1087',
    '1ffff87bde004211e3188',
    '1ffff87bde0421002318f',
    '1ffff87bde042101c210f',
    '1ffff87bde042101e1087',
    '1ffff87bde042101e3188',
    '1ffff87bde3800002318f',
    '1ffff87bde380001c210f',
    '1ffff87bde380001e1087',
    '1ffff87bde380001e3188',
    '1ffff87bdfc0000e0210f',
    '1ffff87bdfc0000e21087',
    '1ffff87bdfc0000e23188',
    '1ffff87bdfc0000fc0007',
    '1ffff87bdfc0000fc2108',
    '1ffff87bdfc0000fe1080',
    '1ffff87bdfc042100210f',
    '1ffff87bdfc0421021087',
    '1ffff87bdfc0421023188',
    '1ffff87bdfc04211c0007',
    '1ffff87bdfc04211c2108',
    '1ffff87bdfc04211e1080',
    '1ffff87bdfc421000210f',
    '1ffff87bdfc4210021087',
    '1ffff87bdfc4210023188',
    '1ffff87bdfc42101c0007',
    '1ffff87bdfc42101c2108',
    '1ffff87bdfc42101e1080',
    '1ffff87bdff800000210f',
    '1ffff87bdff8000021087',
    '1ffff87bdff8000023188',
    '1ffff87bdff80001c0007',
    '1ffff87bdff80001c2108',
    '1ffff87bdff80001e1080',
    '1ffff8f7bc00000e2318f',
    '1ffff8f7bc00000fc210f',
    '1ffff8f7bc00000fe1087',
    '1ffff8f7bc00000fe3188',
    '1ffff8f7bc0042102318f',
    '1ffff8f7bc004211c210f',
    '1ffff8f7bc004211e1087',
    '1ffff8f7bc004211e3188',
    '1ffff8f7bc0421002318f',
    '1ffff8f7bc042101c210f',
    '1ffff8f7bc042101e1087',
    '1ffff8f7bc042101e3188',
    '1ffff8f7bc3800002318f',
    '1ffff8f7bc380001c210f',
    '1ffff8f7bc380001e1087',
    '1ffff8f7bc380001e3188',
    '1ffff8f7bdc0000e0210f',
    '1ffff8f7bdc0000e21087',
    '1ffff8f7bdc0000e23188',
    '1ffff8f7bdc0000fc0007',
    '1ffff8f7bdc0000fc2108',
    '1ffff8f7bdc0000fe1080',
    '1ffff8f7bdc042100210f',
    '1ffff8f7bdc0421021087',
    '1ffff8f7bdc0421023188',
    '1ffff8f7bdc04211c0007',
    '1ffff8f7bdc04211c2108',
    '1ffff8f7bdc04211e1080',
    '1ffff8f7bdc421000210f',
    '1ffff8f7bdc4210021087',
    '1ffff8f7bdc4210023188',
    '1ffff8f7bdc42101c0007',
    '1ffff8f7bdc42101c2108',
    '1ffff8f7bdc42101e1080',
    '1ffff8f7bdf800000210f',
    '1ffff8f7bdf8000021087',
    '1ffff8f7bdf8000023188',
    '1ffff8f7bdf80001c0007',
    '1ffff8f7bdf80001c2108',
    '1ffff8f7bdf80001e1080',
    '1ffff8fffe00000e0210f',
    '1ffff8fffe00000e21087',
    '1ffff8fffe00000e23188',
    '1ffff8fffe00000fc0007',
    '1ffff8fffe00000fc2108',
    '1ffff8fffe00000fe1080',
    '1ffff8fffe0042100210f',
    '1ffff8fffe00421021087',
    '1ffff8fffe00421023188',
    '1ffff8fffe004211c0007',
    '1ffff8fffe004211c2108',
    '1ffff8fffe004211e1080',
    '1ffff8fffe0421000210f',
    '1ffff8fffe04210021087',
    '1ffff8fffe04210023188',
    '1ffff8fffe042101c0007',
    '1ffff8fffe042101c2108',
    '1ffff8fffe042101e1080',
    '1ffff8fffe3800000210f',
    '1ffff8fffe38000021087',
    '1ffff8fffe38000023188',
    '1ffff8fffe380001c0007',
    '1ffff8fffe380001c2108',
    '1ffff8fffe380001e1080',
    '1ffff8ffffc0000e00007',
    '1ffff8ffffc0000e02108',
    '1ffff8ffffc0000e21080',
    '1ffff8ffffc0000fc0000',
    '1ffff8ffffc0421000007',
    '1ffff8ffffc0421002108',
    '1ffff8ffffc0421021080',
    '1ffff8ffffc04211c0000',
    '1ffff8ffffc4210000007',
    '1ffff8ffffc4210002108',
    '1ffff8ffffc4210021080',
    '1ffff8ffffc42101c0000',
    '1ffff8fffff8000000007',
    '1ffff8fffff8000002108',
    '1ffff8fffff8000021080',
    '1ffff8fffff80001c0000',
    '1fffff739c00000e2318f',
    '1fffff739c00000fc210f',
    '1fffff739c00000fe1087',
    '1fffff739c00000fe3188',
    '1fffff739c0042102318f',
    '1fffff739c004211c210f',
    '1fffff739c004211e1087',
    '1fffff739c004211e3188',
    '1fffff739c0421002318f',
    '1fffff739c042101c210f',
    '1fffff739c042101e1087',
    '1fffff739c042101e3188',
    '1fffff739c3800002318f',
    '1fffff739c380001c210f',
    '1fffff739c380001e1087',
    '1fffff739c380001e3188',
    '1fffff739dc0000e0210f',
    '1fffff739dc0000e21087',
    '1fffff739dc0000e23188',
    '1fffff739dc0000fc0007',
    '1fffff739dc0000fc2108',
    '1fffff739dc0000fe1080',
    '1fffff739dc042100210f',
    '1fffff739dc0421021087',
    '1fffff739dc0421023188',
    '1fffff739dc04211c0007',
    '1fffff739dc04211c2108',
    '1fffff739dc04211e1080',
    '1fffff739dc421000210f',
    '1fffff739dc4210021087',
    '1fffff739dc4210023188',
    '1fffff739dc42101c0007',
    '1fffff739dc42101c2108',
    '1fffff739dc42101e1080',
    '1fffff739df800000210f',
    '1fffff739df8000021087',
    '1fffff739df8000023188',
    '1fffff739df80001c0007',
    '1fffff739df80001c2108',
    '1fffff739df80001e1080',
    '1fffff7bde00000e0210f',
    '1fffff7bde00000e21087',
    '1fffff7bde00000e23188',
    '1fffff7bde00000fc0007',
    '1fffff7bde00000fc2108',
    '1fffff7bde00000fe1080',
    '1fffff7bde0042100210f',
    '1fffff7bde00421021087',
    '1fffff7bde00421023188',
    '1fffff7bde004211c0007',
    '1fffff7bde004211c2108',
    '1fffff7bde004211e1080',
    '1fffff7bde0421000210f',
    '1fffff7bde04210021087',
    '1fffff7bde04210023188',
    '1fffff7bde042101c0007',
    '1fffff7bde042101c2108',
    '1fffff7bde042101e1080',
    '1fffff7bde3800000210f',
    '1fffff7bde38000021087',
    '1fffff7bde38000023188',
    '1fffff7bde380001c0007',
    '1fffff7bde380001c2108',
    '1fffff7bde380001e1080',
    '1fffff7bdfc0000e00007',
    '1fffff7bdfc0000e02108',
    '1fffff7bdfc0000e21080',
    '1fffff7bdfc0000fc0000',
    '1fffff7bdfc0421000007',
    '1fffff7bdfc0421002108',
    '1fffff7bdfc0421021080',
    '1fffff7bdfc04211c0000',
    '1fffff7bdfc4210000007',
    '1fffff7bdfc4210002108',
    '1fffff7bdfc4210021080',
    '1fffff7bdfc42101c0000',
    '1fffff7bdff8000000007',
    '1fffff7bdff8000002108',
    '1fffff7bdff8000021080',
    '1fffff7bdff80001c0000',
    '1ffffff7bc00000e0210f',
    '1ffffff7bc00000e21087',
    '1ffffff7bc00000e23188',
    '1ffffff7bc00000fc0007',
    '1ffffff7bc00000fc2108',
    '1ffffff7bc00000fe1080',
    '1ffffff7bc0042100210f',
    '1ffffff7bc00421021087',
    '1ffffff7bc00421023188',
    '1ffffff7bc004211c0007',
    '1ffffff7bc004211c2108',
    '1ffffff7bc004211e1080',
    '1ffffff7bc0421000210f',
    '1ffffff7bc04210021087',
    '1ffffff7bc04210023188',
    '1ffffff7bc042101c0007',
    '1ffffff7bc042101c2108',
    '1ffffff7bc042101e1080',
    '1ffffff7bc3800000210f',
    '1ffffff7bc38000021087',
    '1ffffff7bc38000023188',
    '1ffffff7bc380001c0007',
    '1ffffff7bc380001c2108',
    '1ffffff7bc380001e1080',
    '1ffffff7bdc0000e00007',
    '1ffffff7bdc0000e02108',
    '1ffffff7bdc0000e21080',
    '1ffffff7bdc0000fc0000',
    '1ffffff7bdc0421000007',
    '1ffffff7bdc0421002108',
    '1ffffff7bdc0421021080',
    '1ffffff7bdc04211c0000',
    '1ffffff7bdc4210000007',
    '1ffffff7bdc4210002108',
    '1ffffff7bdc4210021080',
    '1ffffff7bdc42101c0000',
    '1ffffff7bdf8000000007',
    '1ffffff7bdf8000002108',
    '1ffffff7bdf8000021080',
    '1ffffff7bdf80001c0000',
    '1ffffffffe00000e00007',
    '1ffffffffe00000e02108',
    '1ffffffffe00000e21080',
    '1ffffffffe00000fc0000',
    '1ffffffffe00421000007',
    '1ffffffffe00421002108',
    '1ffffffffe00421021080',
    '1ffffffffe004211c0000',
    '1ffffffffe04210000007',
    '1ffffffffe04210002108',
    '1ffffffffe04210021080',
    '1ffffffffe042101c0000',
    '1ffffffffe38000000007',
    '1ffffffffe38000002108',
    '1ffffffffe38000021080',
    '1ffffffffe380001c0000',
    '1fffffffffc0000e00000',
    '1fffffffffc0421000000',
    '1fffffffffc4210000000',
    '1ffffffffff8000000000',
    'ee7380739c04631fe318f',
    'ee7380739c38421fe318f',
    'ee7380739c3c210fe318f',
    'ee7380739c3c6311e318f',
    'ee7380739dc4631e2318f',
    'ee7380739dc4631fc210f',
    'ee7380739dc4631fe1087',
    'ee7380739dc4631fe3188',
    'ee7380739df8421e2318f',
    'ee7380739df8421fc210f',
    'ee7380739df8421fe1087',
    'ee7380739df8421fe3188',
    'ee7380739dfc210e2318f',
    'ee7380739dfc210fc210f',
    'ee7380739dfc210fe1087',
    'ee7380739dfc210fe3188',
    'ee7380739dfc63102318f',
    'ee7380739dfc6311c210f',
    'ee7380739dfc6311e1087',
    'ee7380739dfc6311e3188',
    'ee73807bde04631e2318f',
    'ee73807bde04631fc210f',
    'ee73807bde04631fe1087',
    'ee73807bde04631fe3188',
    'ee73807bde38421e2318f',
    'ee73807bde38421fc210f',
    'ee73807bde38421fe1087',
    'ee73807bde38421fe3188',
    'ee73807bde3c210e2318f',
    'ee73807bde3c210fc210f',
    'ee73807bde3c210fe1087',
    'ee73807bde3c210fe3188',
    'ee73807bde3c63102318f',
    'ee73807bde3c6311c210f',
    'ee73807bde3c6311e1087',
    'ee73807bde3c6311e3188',
    'ee73807bdfc4631e0210f',
    'ee73807bdfc4631e21087',
    'ee73807bdfc4631e23188',
    'ee73807bdfc4631fc0007',
    'ee73807bdfc4631fc2108',
    'ee73807bdfc4631fe1080',
    'ee73807bdff8421e0210f',
    'ee73807bdff8421e21087',
    'ee73807bdff8421e23188',
    'ee73807bdff8421fc0007',
    'ee73807bdff8421fc2108',
    'ee73807bdff8421fe1080',
    'ee73807bdffc210e0210f',
    'ee73807bdffc210e21087',
    'ee73807bdffc210e23188',
    'ee73807bdffc210fc0007',
    'ee73807bdffc210fc2108',
    'ee73807bdffc210fe1080',
    'ee73807bdffc63100210f',
    'ee73807bdffc631021087',
    'ee73807bdffc631023188',
    'ee73807bdffc6311c0007',
    'ee73807bdffc6311c2108',
    'ee73807bdffc6311e1080',
    'ee7380f7bc04631e2318f',
    'ee7380f7bc04631fc210f',
    'ee7380f7bc04631fe1087',
    'ee7380f7bc04631fe3188',
    'ee7380f7bc38421e2318f',
    'ee7380f7bc38421fc210f',
    'ee7380f7bc38421fe1087',
    'ee7380f7bc38421fe3188',
    'ee7380f7bc3c210e2318f',
    'ee7380f7bc3c210fc210f',
    'ee7380f7bc3c210fe1087',
    'ee7380f7bc3c210fe3188',
    'ee7380f7bc3c63102318f',
    'ee7380f7bc3c6311c210f',
    'ee7380f7bc3c6311e1087',
    'ee7380f7bc3c6311e3188',
    'ee7380f7bdc4631e0210f',
    'ee7380f7bdc4631e21087',
    'ee7380f7bdc4631e23188',
    'ee7380f7bdc4631fc0007',
    'ee7380f7bdc4631fc2108',
    'ee7380f7bdc4631fe1080',
    'ee7380f7bdf8421e0210f',
    'ee7380f7bdf8421e21087',
    'ee7380f7bdf8421e23188',
    'ee7380f7bdf8421fc0007',
    'ee7380f7bdf8421fc2108',
    'ee7380f7bdf8421fe1080',
    'ee7380f7bdfc210e0210f',
    'ee7380f7bdfc210e21087',
    'ee7380f7bdfc210e23188',
    'ee7380f7bdfc210fc0007',
    'ee7380f7bdfc210fc2108',
    'ee7380f7bdfc210fe1080',
    'ee7380f7bdfc63100210f',
    'ee7380f7bdfc631021087',
    'ee7380f7bdfc631023188',
    'ee7380f7bdfc6311c0007',
    'ee7380f7bdfc6311c2108',
    'ee7380f7bdfc6311e1080',
    'ee7380fffe04631e0210f',
    'ee7380fffe04631e21087',
    'ee7380fffe04631e23188',
    'ee7380fffe04631fc0007',
    'ee7380fffe04631fc2108',
    'ee7380fffe04631fe1080',
    'ee7380fffe38421e0210f',
    'ee7380fffe38421e21087',
    'ee7380fffe38421e23188',
    'ee7380fffe38421fc0007',
    'ee7380fffe38421fc2108',
    'ee7380fffe38421fe1080',
    'ee7380fffe3c210e0210f',
    'ee7380fffe3c210e21087',
    'ee7380fffe3c210e23188',
    'ee7380fffe3c210fc0007',
    'ee7380fffe3c210fc2108',
    'ee7380fffe3c210fe1080',
    'ee7380fffe3c63100210f',
    'ee7380fffe3c631021087',
    'ee7380fffe3c631023188',
    'ee7380fffe3c6311c0007',
    'ee7380fffe3c6311c2108',
    'ee7380fffe3c6311e1080',
    'ee7380ffffc4631e00007',
    'ee7380ffffc4631e02108',
    'ee7380ffffc4631e21080',
    'ee7380ffffc4631fc0000',
    'ee7380fffff8421e00007',
    'ee7380fffff8421e02108',
    'ee7380fffff8421e21080',
    'ee7380fffff8421fc0000',
    'ee7380fffffc210e00007',
    'ee7380fffffc210e02108',
    'ee7380fffffc210e21080',
    'ee7380fffffc210fc0000',
    'ee7380fffffc631000007',
    'ee7380fffffc631002108',
    'ee7380fffffc631021080',
    'ee7380fffffc6311c0000',
    'ee7387739c04631e2318f',
    'ee7387739c04631fc210f',
    'ee7387739c04631fe1087',
    'ee7387739c04631fe3188',
    'ee7387739c38421e2318f',
    'ee7387739c38421fc210f',
    'ee7387739c38421fe1087',
    'ee7387739c38421fe3188',
    'ee7387739c3c210e2318f',
    'ee7387739c3c210fc210f',
    'ee7387739c3c210fe1087',
    'ee7387739c3c210fe3188',
    'ee7387739c3c63102318f',
    'ee7387739c3c6311c210f',
    'ee7387739c3c6311e1087',
    'ee7387739c3c6311e3188',
    'ee7387739dc4631e0210f',
    'ee7387739dc4631e21087',
    'ee7387739dc4631e23188',
    'ee7387739dc4631fc0007',
    'ee7387739dc4631fc2108',
    'ee7387739dc4631fe1080',
    'ee7387739df8421e0210f',
    'ee7387739df8421e21087',
    'ee7387739df8421e23188',
    'ee7387739df8421fc0007',
    'ee7387739df8421fc2108',
    'ee7387739df8421fe1080',
    'ee7387739dfc210e0210f',
    'ee7387739dfc210e21087',
    'ee7387739dfc210e23188',
    'ee7387739dfc210fc0007',
    'ee7387739dfc210fc2108',
    'ee7387739dfc210fe1080',
    'ee7387739dfc63100210f',
    'ee7387739dfc631021087',
    'ee7387739dfc631023188',
    'ee7387739dfc6311c0007',
    'ee7387739dfc6311c2108',
    'ee7387739dfc6311e1080',
    'ee73877bde04631e0210f',
    'ee73877bde04631e21087',
    'ee73877bde04631e23188',
    'ee73877bde04631fc0007',
    'ee73877bde04631fc2108',
    'ee73877bde04631fe1080',
    'ee73877bde38421e0210f',
    'ee73877bde38421e21087',
    'ee73877bde38421e23188',
    'ee73877bde38421fc0007',
    'ee73877bde38421fc2108',
    'ee73877bde38421fe1080',
    'ee73877bde3c210e0210f',
    'ee73877bde3c210e21087',
    'ee73877bde3c210e23188',
    'ee73877bde3c210fc0007',
    'ee73877bde3c210fc2108',
    'ee73877bde3c210fe1080',
    'ee73877bde3c63100210f',
    'ee73877bde3c631021087',
    'ee73877bde3c631023188',
    'ee73877bde3c6311c0007',
    'ee73877bde3c6311c2108',
    'ee73877bde3c6311e1080',
    'ee73877bdfc4631e00007',
    'ee73877bdfc4631e02108',
    'ee73877bdfc4631e21080',
    'ee73877bdfc4631fc0000',
    'ee73877bdff8421e00007',
    'ee73877bdff8421e02108',
    'ee73877bdff8421e21080',
    'ee73877bdff8421fc0000',
    'ee73877bdffc210e00007',
    'ee73877bdffc210e02108',
    'ee73877bdffc210e21080',
    'ee73877bdffc210fc0000',
    'ee73877bdffc631000007',
    'ee73877bdffc631002108',
    'ee73877bdffc631021080',
    'ee73877bdffc6311c0000',
    'ee7387f7bc04631e0210f',
    'ee7387f7bc04631e21087',
    'ee7387f7bc04631e23188',
    'ee7387f7bc04631fc0007',
    'ee7387f7bc04631fc2108',
    'ee7387f7bc04631fe1080',
    'ee7387f7bc38421e0210f',
    'ee7387f7bc38421e21087',
    'ee7387f7bc38421e23188',
    'ee7387f7bc38421fc0007',
    'ee7387f7bc38421fc2108',
    'ee7387f7bc38421fe1080',
    'ee7387f7bc3c210e0210f',
    'ee7387f7bc3c210e21087',
    'ee7387f7bc3c210e23188',
    'ee7387f7bc3c210fc0007',
    'ee7387f7bc3c210fc2108',
    'ee7387f7bc3c210fe1080',
    'ee7387f7bc3c63100210f',
    'ee7387f7bc3c631021087',
    'ee7387f7bc3c631023188',
    'ee7387f7bc3c6311c0007',
    'ee7387f7bc3c6311c2108',
    'ee7387f7bc3c6311e1080',
    'ee7387f7bdc4631e00007',
    'ee7387f7bdc4631e02108',
    'ee7387f7bdc4631e21080',
    'ee7387f7bdc4631fc0000',
    'ee7387f7bdf8421e00007',
    'ee7387f7bdf8421e02108',
    'ee7387f7bdf8421e21080',
    'ee7387f7bdf8421fc0000',
    'ee7387f7bdfc210e00007',
    'ee7387f7bdfc210e02108',
    'ee7387f7bdfc210e21080',
    'ee7387f7bdfc210fc0000',
    'ee7387f7bdfc631000007',
    'ee7387f7bdfc631002108',
    'ee7387f7bdfc631021080',
    'ee7387f7bdfc6311c0000',
    'ee7387fffe04631e00007',
    'ee7387fffe04631e02108',
    'ee7387fffe04631e21080',
    'ee7387fffe04631fc0000',
    'ee7387fffe38421e00007',
    'ee7387fffe38421e02108',
    'ee7387fffe38421e21080',
    'ee7387fffe38421fc0000',
    'ee7387fffe3c210e00007',
    'ee7387fffe3c210e02108',
    'ee7387fffe3c210e21080',
    'ee7387fffe3c210fc0000',
    'ee7387fffe3c631000007',
    'ee7387fffe3c631002108',
    'ee7387fffe3c631021080',
    'ee7387fffe3c6311c0000',
    'ee7387ffffc4631e00000',
    'ee7387fffff8421e00000',
    'ee7387fffffc210e00000',
    'ee7387fffffc631000000',
    'ee73b8739c00421fe318f',
    'ee73b8739c04210fe318f',
    'ee73b8739c046311e318f',
    'ee73b8739c38000fe318f',
    'ee73b8739c384211e318f',
    'ee73b8739c3c2101e318f',
    'ee73b8739dc0421e2318f',
    'ee73b8739dc0421fc210f',
    'ee73b8739dc0421fe1087',
    'ee73b8739dc0421fe3188',
    'ee73b8739dc4210e2318f',
    'ee73b8739dc4210fc210f',
    'ee73b8739dc4210fe1087',
    'ee73b8739dc4210fe3188',
    'ee73b8739dc463102318f',
    'ee73b8739dc46311c210f',
    'ee73b8739dc46311e1087',
    'ee73b8739dc46311e3188',
    'ee73b8739df8000e2318f',
    'ee73b8739df8000fc210f',
    'ee73b8739df8000fe1087',
    'ee73b8739df8000fe3188',
    'ee73b8739df842102318f',
    'ee73b8739df84211c210f',
    'ee73b8739df84211e1087',
    'ee73b8739df84211e3188',
    'ee73b8739dfc21002318f',
    'ee73b8739dfc2101c210f',
    'ee73b8739dfc2101e1087',
    'ee73b8739dfc2101e3188',
    'ee73b87bde00421e2318f',
    'ee73b87bde00421fc210f',
    'ee73b87bde00421fe1087',
    'ee73b87bde00421fe3188',
    'ee73b87bde04210e2318f',
    'ee73b87bde04210fc210f',
    'ee73b87bde04210fe1087',
    'ee73b87bde04210fe3188',
    'ee73b87bde0463102318f',
    'ee73b87bde046311c210f',
    'ee73b87bde046311e1087',
    'ee73b87bde046311e3188',
    'ee73b87bde38000e2318f',
    'ee73b87bde38000fc210f',
    'ee73b87bde38000fe1087',
    'ee73b87bde38000fe3188',
    'ee73b87bde3842102318f',
    'ee73b87bde384211c210f',
    'ee73b87bde384211e1087',
    'ee73b87bde384211e3188',
    'ee73b87bde3c21002318f',
    'ee73b87bde3c2101c210f',
    'ee73b87bde3c2101e1087',
    'ee73b87bde3c2101e3188',
    'ee73b87bdfc0421e0210f',
    'ee73b87bdfc0421e21087',
    'ee73b87bdfc0421e23188',
    'ee73b87bdfc0421fc0007',
    'ee73b87bdfc0421fc2108',
    'ee73b87bdfc0421fe1080',
    'ee73b87bdfc4210e0210f',
    'ee73b87bdfc4210e21087',
    'ee73b87bdfc4210e23188',
    'ee73b87bdfc4210fc0007',
    'ee73b87bdfc4210fc2108',
    'ee73b87bdfc4210fe1080',
    'ee73b87bdfc463100210f',
    'ee73b87bdfc4631021087',
    'ee73b87bdfc4631023188',
    'ee73b87bdfc46311c0007',
    'ee73b87bdfc46311c2108',
    'ee73b87bdfc46311e1080',
    'ee73b87bdff8000e0210f',
    'ee73b87bdff8000e21087',
    'ee73b87bdff8000e23188',
    'ee73b87bdff8000fc0007',
    'ee73b87bdff8000fc2108',
    'ee73b87bdff8000fe1080',
    'ee73b87bdff842100210f',
    'ee73b87bdff8421021087',
    'ee73b87bdff8421023188',
    'ee73b87bdff84211c0007',
    'ee73b87bdff84211c2108',
    'ee73b87bdff84211e1080',
    'ee73b87bdffc21000210f',
    'ee73b87bdffc210021087',
    'ee73b87bdffc210023188',
    'ee73b87bdffc2101c0007',
    'ee73b87bdffc2101c2108',
    'ee73b87bdffc2101e1080',
    'ee73b8f7bc00421e2318f',
    'ee73b8f7bc00421fc210f',
    'ee73b8f7bc00421fe1087',
    'ee73b8f7bc00421fe3188',
    'ee73b8f7bc04210e2318f',
    'ee73b8f7bc04210fc210f',
    'ee73b8f7bc04210fe1087',
    'ee73b8f7bc04210fe3188',
    'ee73b8f7bc0463102318f',
    'ee73b8f7bc046311c210f',
    'ee73b8f7bc046311e1087',
    'ee73b8f7bc046311e3188',
    'ee73b8f7bc38000e2318f',
    'ee73b8f7bc38000fc210f',
    'ee73b8f7bc38000fe1087',
    'ee73b8f7bc38000fe3188',
    'ee73b8f7bc3842102318f',
    'ee73b8f7bc384211c210f',
    'ee73b8f7bc384211e1087',
    'ee73b8f7bc384211e3188',
    'ee73b8f7bc3c21002318f',
    'ee73b8f7bc3c2101c210f',
    'ee73b8f7bc3c2101e1087',
    'ee73b8f7bc3c2101e3188',
    'ee73b8f7bdc0421e0210f',
    'ee73b8f7bdc0421e21087',
    'ee73b8f7bdc0421e23188',
    'ee73b8f7bdc0421fc0007',
    'ee73b8f7bdc0421fc2108',
    'ee73b8f7bdc0421fe1080',
    'ee73b8f7bdc4210e0210f',
    'ee73b8f7bdc4210e21087',
    'ee73b8f7bdc4210e23188',
    'ee73b8f7bdc4210fc0007',
    'ee73b8f7bdc4210fc2108',
    'ee73b8f7bdc4210fe1080',
    'ee73b8f7bdc463100210f',
    'ee73b8f7bdc4631021087',
    'ee73b8f7bdc4631023188',
    'ee73b8f7bdc46311c0007',
    'ee73b8f7bdc46311c2108',
    'ee73b8f7bdc46311e1080',
    'ee73b8f7bdf8000e0210f',
    'ee73b8f7bdf8000e21087',
    'ee73b8f7bdf8000e23188',
    'ee73b8f7bdf8000fc0007',
    'ee73b8f7bdf8000fc2108',
    'ee73b8f7bdf8000fe1080',
    'ee73b8f7bdf842100210f',
    'ee73b8f7bdf8421021087',
    'ee73b8f7bdf8421023188',
    'ee73b8f7bdf84211c0007',
    'ee73b8f7bdf84211c2108',
    'ee73b8f7bdf84211e1080',
    'ee73b8f7bdfc21000210f',
    'ee73b8f7bdfc210021087',
    'ee73b8f7bdfc210023188',
    'ee73b8f7bdfc2101c0007',
    'ee73b8f7bdfc2101c2108',
    'ee73b8f7bdfc2101e1080',
    'ee73b8fffe00421e0210f',
    'ee73b8fffe00421e21087',
    'ee73b8fffe00421e23188',
    'ee73b8fffe00421fc0007',
    'ee73b8fffe00421fc2108',
    'ee73b8fffe00421fe1080',
    'ee73b8fffe04210e0210f',
    'ee73b8fffe04210e21087',
    'ee73b8fffe04210e23188',
    'ee73b8fffe04210fc0007',
    'ee73b8fffe04210fc2108',
    'ee73b8fffe04210fe1080',
    'ee73b8fffe0463100210f',
    'ee73b8fffe04631021087',
    'ee73b8fffe04631023188',
    'ee73b8fffe046311c0007',
    'ee73b8fffe046311c2108',
    'ee73b8fffe046311e1080',
    'ee73b8fffe38000e0210f',
    'ee73b8fffe38000e21087',
    'ee73b8fffe38000e23188',
    'ee73b8fffe38000fc0007',
    'ee73b8fffe38000fc2108',
    'ee73b8fffe38000fe1080',
    'ee73b8fffe3842100210f',
    'ee73b8fffe38421021087',
    'ee73b8fffe38421023188',
    'ee73b8fffe384211c0007',
    'ee73b8fffe384211c2108',
    'ee73b8fffe384211e1080',
    'ee73b8fffe3c21000210f',
    'ee73b8fffe3c210021087',
    'ee73b8fffe3c210023188',
    'ee73b8fffe3c2101c0007',
    'ee73b8fffe3c2101c2108',
    'ee73b8fffe3c2101e1080',
    'ee73b8ffffc0421e00007',
    'ee73b8ffffc0421e02108',
    'ee73b8ffffc0421e21080',
    'ee73b8ffffc0421fc0000',
    'ee73b8ffffc4210e00007',
    'ee73b8ffffc4210e02108',
    'ee73b8ffffc4210e21080',
    'ee73b8ffffc4210fc0000',
    'ee73b8ffffc4631000007',
    'ee73b8ffffc4631002108',
    'ee73b8ffffc4631021080',
    'ee73b8ffffc46311c0000',
    'ee73b8fffff8000e00007',
    'ee73b8fffff8000e02108',
    'ee73b8fffff8000e21080',
    'ee73b8fffff8000fc0000',
    'ee73b8fffff8421000007',
    'ee73b8fffff8421002108',
    'ee73b8fffff8421021080',
    'ee73b8fffff84211c0000',
    'ee73b8fffffc210000007',
    'ee73b8fffffc210002108',
    'ee73b8fffffc210021080',
    'ee73b8fffffc2101c0000',
    'ee73bf739c00421e2318f',
    'ee73bf739c00421fc210f',
    'ee73bf739c00421fe1087',
    'ee73bf739c00421fe3188',
    'ee73bf739c04210e2318f',
    'ee73bf739c04210fc210f',
    'ee73bf739c04210fe1087',
    'ee73bf739c04210fe3188',
    'ee73bf739c0463102318f',
    'ee73bf739c046311c210f',
    'ee73bf739c046311e1087',
    'ee73bf739c046311e3188',
    'ee73bf739c38000e2318f',
    'ee73bf739c38000fc210f',
    'ee73bf739c38000fe1087',
    'ee73bf739c38000fe3188',
    'ee73bf739c3842102318f',
    'ee73bf739c384211c210f',
    'ee73bf739c384211e1087',
    'ee73bf739c384211e3188',
    'ee73bf739c3c21002318f',
    'ee73bf739c3c2101c210f',
    'ee73bf739c3c2101e1087',
    'ee73bf739c3c2101e3188',
    'ee73bf739dc0421e0210f',
    'ee73bf739dc0421e21087',
    'ee73bf739dc0421e23188',
    'ee73bf739dc0421fc0007',
    'ee73bf739dc0421fc2108',
    'ee73bf739dc0421fe1080',
    'ee73bf739dc4210e0210f',
    'ee73bf739dc4210e21087',
    'ee73bf739dc4210e23188',
    'ee73bf739dc4210fc0007',
    'ee73bf739dc4210fc2108',
    'ee73bf739dc4210fe1080',
    'ee73bf739dc463100210f',
    'ee73bf739dc4631021087',
    'ee73bf739dc4631023188',
    'ee73bf739dc46311c0007',
    'ee73bf739dc46311c2108',
    'ee73bf739dc46311e1080',
    'ee73bf739df8000e0210f',
    'ee73bf739df8000e21087',
    'ee73bf739df8000e23188',
    'ee73bf739df8000fc0007',
    'ee73bf739df8000fc2108',
    'ee73bf739df8000fe1080',
    'ee73bf739df842100210f',
    'ee73bf739df8421021087',
    'ee73bf739df8421023188',
    'ee73bf739df84211c0007',
    'ee73bf739df84211c2108',
    'ee73bf739df84211e1080',
    'ee73bf739dfc21000210f',
    'ee73bf739dfc210021087',
    'ee73bf739dfc210023188',
    'ee73bf739dfc2101c0007',
    'ee73bf739dfc2101c2108',
    'ee73bf739dfc2101e1080',
    'ee73bf7bde00421e0210f',
    'ee73bf7bde00421e21087',
    'ee73bf7bde00421e23188',
    'ee73bf7bde00421fc0007',
    'ee73bf7bde00421fc2108',
    'ee73bf7bde00421fe1080',
    'ee73bf7bde04210e0210f',
    'ee73bf7bde04210e21087',
    'ee73bf7bde04210e23188',
    'ee73bf7bde04210fc0007',
    'ee73bf7bde04210fc2108',
    'ee73bf7bde04210fe1080',
    'ee73bf7bde0463100210f',
    'ee73bf7bde04631021087',
    'ee73bf7bde04631023188',
    'ee73bf7bde046311c0007',
    'ee73bf7bde046311c2108',
    'ee73bf7bde046311e1080',
    'ee73bf7bde38000e0210f',
    'ee73bf7bde38000e21087',
    'ee73bf7bde38000e23188',
    'ee73bf7bde38000fc0007',
    'ee73bf7bde38000fc2108',
    'ee73bf7bde38000fe1080',
    'ee73bf7bde3842100210f',
    'ee73bf7bde38421021087',
    'ee73bf7bde38421023188',
    'ee73bf7bde384211c0007',
    'ee73bf7bde384211c2108',
    'ee73bf7bde384211e1080',
    'ee73bf7bde3c21000210f',
    'ee73bf7bde3c210021087',
    'ee73bf7bde3c210023188',
    'ee73bf7bde3c2101c0007',
    'ee73bf7bde3c2101c2108',
    'ee73bf7bde3c2101e1080',
    'ee73bf7bdfc0421e00007',
    'ee73bf7bdfc0421e02108',
    'ee73bf7bdfc0421e21080',
    'ee73bf7bdfc0421fc0000',
    'ee73bf7bdfc4210e00007',
    'ee73bf7bdfc4210e02108',
    'ee73bf7bdfc4210e21080',
    'ee73bf7bdfc4210fc0000',
    'ee73bf7bdfc4631000007',
    'ee73bf7bdfc4631002108',
    'ee73bf7bdfc4631021080',
    'ee73bf7bdfc46311c0000',
    'ee73bf7bdff8000e00007',
    'ee73bf7bdff8000e02108',
    'ee73bf7bdff8000e21080',
    'ee73bf7bdff8000fc0000',
    'ee73bf7bdff8421000007',
    'ee73bf7bdff8421002108',
    'ee73bf7bdff8421021080',
    'ee73bf7bdff84211c0000',
    'ee73bf7bdffc210000007',
    'ee73bf7bdffc210002108',
    'ee73bf7bdffc210021080',
    'ee73bf7bdffc2101c0000',
    'ee73bff7bc00421e0210f',
    'ee73bff7bc00421e21087',
    'ee73bff7bc00421e23188',
    'ee73bff7bc00421fc0007',
    'ee73bff7bc00421fc2108',
    'ee73bff7bc00421fe1080',
    'ee73bff7bc04210e0210f',
    'ee73bff7bc04210e21087',
    'ee73bff7bc04210e23188',
    'ee73bff7bc04210fc0007',
    'ee73bff7bc04210fc2108',
    'ee73bff7bc04210fe1080',
    'ee73bff7bc0463100210f',
    'ee73bff7bc04631021087',
    'ee73bff7bc04631023188',
    'ee73bff7bc046311c0007',
    'ee73bff7bc046311c2108',
    'ee73bff7bc046311e1080',
    'ee73bff7bc38000e0210f',
    'ee73bff7bc38000e21087',
    'ee73bff7bc38000e23188',
    'ee73bff7bc38000fc0007',
    'ee73bff7bc38000fc2108',
    'ee73bff7bc38000fe1080',
    'ee73bff7bc3842100210f',
    'ee73bff7bc38421021087',
    'ee73bff7bc38421023188',
    'ee73bff7bc384211c0007',
    'ee73bff7bc384211c2108',
    'ee73bff7bc384211e1080',
    'ee73bff7bc3c21000210f',
    'ee73bff7bc3c210021087',
    'ee73bff7bc3c210023188',
    'ee73bff7bc3c2101c0007',
    'ee73bff7bc3c2101c2108',
    'ee73bff7bc3c2101e1080',
    'ee73bff7bdc0421e00007',
    'ee73bff7bdc0421e02108',
    'ee73bff7bdc0421e21080',
    'ee73bff7bdc0421fc0000',
    'ee73bff7bdc4210e00007',
    'ee73bff7bdc4210e02108',
    'ee73bff7bdc4210e21080',
    'ee73bff7bdc4210fc0000',
    'ee73bff7bdc4631000007',
    'ee73bff7bdc4631002108',
    'ee73bff7bdc4631021080',
    'ee73bff7bdc46311c0000',
    'ee73bff7bdf8000e00007',
    'ee73bff7bdf8000e02108',
    'ee73bff7bdf8000e21080',
    'ee73bff7bdf8000fc0000',
    'ee73bff7bdf8421000007',
    'ee73bff7bdf8421002108',
    'ee73bff7bdf8421021080',
    'ee73bff7bdf84211c0000',
    'ee73bff7bdfc210000007',
    'ee73bff7bdfc210002108',
    'ee73bff7bdfc210021080',
    'ee73bff7bdfc2101c0000',
    'ee73bffffe00421e00007',
    'ee73bffffe00421e02108',
    'ee73bffffe00421e21080',
    'ee73bffffe00421fc0000',
    'ee73bffffe04210e00007',
    'ee73bffffe04210e02108',
    'ee73bffffe04210e21080',
    'ee73bffffe04210fc0000',
    'ee73bffffe04631000007',
    'ee73bffffe04631002108',
    'ee73bffffe04631021080',
    'ee73bffffe046311c0000',
    'ee73bffffe38000e00007',
    'ee73bffffe38000e02108',
    'ee73bffffe38000e21080',
    'ee73bffffe38000fc0000',
    'ee73bffffe38421000007',
    'ee73bffffe38421002108',
    'ee73bffffe38421021080',
    'ee73bffffe384211c0000',
    'ee73bffffe3c210000007',
    'ee73bffffe3c210002108',
    'ee73bffffe3c210021080',
    'ee73bffffe3c2101c0000',
    'ee73bfffffc0421e00000',
    'ee73bfffffc4210e00000',
    'ee73bfffffc4631000000',
    'ee73bffffff8000e00000',
    'ee73bffffff8421000000',
    'ee73bffffffc210000000',
    'ef7bc0739c00421fe318f',
    'ef7bc0739c04210fe318f',
    'ef7bc0739c046311e318f',
    'ef7bc0739c38000fe318f',
    'ef7bc0739c384211e318f',
    'ef7bc0739c3c2101e318f',
    'ef7bc0739dc0421e2318f',
    'ef7bc0739dc0421fc210f',
    'ef7bc0739dc0421fe1087',
    'ef7bc0739dc0421fe3188',
    'ef7bc0739dc4210e2318f',
    'ef7bc0739dc4210fc210f',
    'ef7bc0739dc4210fe1087',
    'ef7bc0739dc4210fe3188',
    'ef7bc0739dc463102318f',
    'ef7bc0739dc46311c210f',
    'ef7bc0739dc46311e1087',
    'ef7bc0739dc46311e3188',
    'ef7bc0739df8000e2318f',
    'ef7bc0739df8000fc210f',
    'ef7bc0739df8000fe1087',
    'ef7bc0739df8000fe3188',
    'ef7bc0739df842102318f',
    'ef7bc0739df84211c210f',
    'ef7bc0739df84211e1087',
    'ef7bc0739df84211e3188',
    'ef7bc0739dfc21002318f',
    'ef7bc0739dfc2101c210f',
    'ef7bc0739dfc2101e1087',
    'ef7bc0739dfc2101e3188',
    'ef7bc07bde00421e2318f',
    'ef7bc07bde00421fc210f',
    'ef7bc07bde00421fe1087',
    'ef7bc07bde00421fe3188',
    'ef7bc07bde04210e2318f',
    'ef7bc07bde04210fc210f',
    'ef7bc07bde04210fe1087',
    'ef7bc07bde04210fe3188',
    'ef7bc07bde0463102318f',
    'ef7bc07bde046311c210f',
    'ef7bc07bde046311e1087',
    'ef7bc07bde046311e3188',
    'ef7bc07bde38000e2318f',
    'ef7bc07bde38000fc210f',
    'ef7bc07bde38000fe1087',
    'ef7bc07bde38000fe3188',
    'ef7bc07bde3842102318f',
    'ef7bc07bde384211c210f',
    'ef7bc07bde384211e1087',
    'ef7bc07bde384211e3188',
    'ef7bc07bde3c21002318f',
    'ef7bc07bde3c2101c210f',
    'ef7bc07bde3c2101e1087',
    'ef7bc07bde3c2101e3188',
    'ef7bc07bdfc0421e0210f',
    'ef7bc07bdfc0421e21087',
    'ef7bc07bdfc0421e23188',
    'ef7bc07bdfc0421fc0007',
    'ef7bc07bdfc0421fc2108',
    'ef7bc07bdfc0421fe1080',
    'ef7bc07bdfc4210e0210f',
    'ef7bc07bdfc4210e21087',
    'ef7bc07bdfc4210e23188',
    'ef7bc07bdfc4210fc0007',
    'ef7bc07bdfc4210fc2108',
    'ef7bc07bdfc4210fe1080',
    'ef7bc07bdfc463100210f',
    'ef7bc07bdfc4631021087',
    'ef7bc07bdfc4631023188',
    'ef7bc07bdfc46311c0007',
    'ef7bc07bdfc46311c2108',
    'ef7bc07bdfc46311e1080',
    'ef7bc07bdff8000e0210f',
    'ef7bc07bdff8000e21087',
    'ef7bc07bdff8000e23188',
    'ef7bc07bdff8000fc0007',
    'ef7bc07bdff8000fc2108',
    'ef7bc07bdff8000fe1080',
    'ef7bc07bdff842100210f',
    'ef7bc07bdff8421021087',
    'ef7bc07bdff8421023188',
    'ef7bc07bdff84211c0007',
    'ef7bc07bdff84211c2108',
    'ef7bc07bdff84211e1080',
    'ef7bc07bdffc21000210f',
    'ef7bc07bdffc210021087',
    'ef7bc07bdffc210023188',
    'ef7bc07bdffc2101c0007',
    'ef7bc07bdffc2101c2108',
    'ef7bc07bdffc2101e1080',
    'ef7bc0f7bc00421e2318f',
    'ef7bc0f7bc00421fc210f',
    'ef7bc0f7bc00421fe1087',
    'ef7bc0f7bc00421fe3188',
    'ef7bc0f7bc04210e2318f',
    'ef7bc0f7bc04210fc210f',
    'ef7bc0f7bc04210fe1087',
    'ef7bc0f7bc04210fe3188',
    'ef7bc0f7bc0463102318f',
    'ef7bc0f7bc046311c210f',
    'ef7bc0f7bc046311e1087',
    'ef7bc0f7bc046311e3188',
    'ef7bc0f7bc38000e2318f',
    'ef7bc0f7bc38000fc210f',
    'ef7bc0f7bc38000fe1087',
    'ef7bc0f7bc38000fe3188',
    'ef7bc0f7bc3842102318f',
    'ef7bc0f7bc384211c210f',
    'ef7bc0f7bc384211e1087',
    'ef7bc0f7bc384211e3188',
    'ef7bc0f7bc3c21002318f',
    'ef7bc0f7bc3c2101c210f',
    'ef7bc0f7bc3c2101e1087',
    'ef7bc0f7bc3c2101e3188',
    'ef7bc0f7bdc0421e0210f',
    'ef7bc0f7bdc0421e21087',
    'ef7bc0f7bdc0421e23188',
    'ef7bc0f7bdc0421fc0007',
    'ef7bc0f7bdc0421fc2108',
    'ef7bc0f7bdc0421fe1080',
    'ef7bc0f7bdc4210e0210f',
    'ef7bc0f7bdc4210e21087',
    'ef7bc0f7bdc4210e23188',
    'ef7bc0f7bdc4210fc0007',
    'ef7bc0f7bdc4210fc2108',
    'ef7bc0f7bdc4210fe1080',
    'ef7bc0f7bdc463100210f',
    'ef7bc0f7bdc4631021087',
    'ef7bc0f7bdc4631023188',
    'ef7bc0f7bdc46311c0007',
    'ef7bc0f7bdc46311c2108',
    'ef7bc0f7bdc46311e1080',
    'ef7bc0f7bdf8000e0210f',
    'ef7bc0f7bdf8000e21087',
    'ef7bc0f7bdf8000e23188',
    'ef7bc0f7bdf8000fc0007',
    'ef7bc0f7bdf8000fc2108',
    'ef7bc0f7bdf8000fe1080',
    'ef7bc0f7bdf842100210f',
    'ef7bc0f7bdf8421021087',
    'ef7bc0f7bdf8421023188',
    'ef7bc0f7bdf84211c0007',
    'ef7bc0f7bdf84211c2108',
    'ef7bc0f7bdf84211e1080',
    'ef7bc0f7bdfc21000210f',
    'ef7bc0f7bdfc210021087',
    'ef7bc0f7bdfc210023188',
    'ef7bc0f7bdfc2101c0007',
    'ef7bc0f7bdfc2101c2108',
    'ef7bc0f7bdfc2101e1080',
    'ef7bc0fffe00421e0210f',
    'ef7bc0fffe00421e21087',
    'ef7bc0fffe00421e23188',
    'ef7bc0fffe00421fc0007',
    'ef7bc0fffe00421fc2108',
    'ef7bc0fffe00421fe1080',
    'ef7bc0fffe04210e0210f',
    'ef7bc0fffe04210e21087',
    'ef7bc0fffe04210e23188',
    'ef7bc0fffe04210fc0007',
    'ef7bc0fffe04210fc2108',
    'ef7bc0fffe04210fe1080',
    'ef7bc0fffe0463100210f',
    'ef7bc0fffe04631021087',
    'ef7bc0fffe04631023188',
    'ef7bc0fffe046311c0007',
    'ef7bc0fffe046311c2108',
    'ef7bc0fffe046311e1080',
    'ef7bc0fffe38000e0210f',
    'ef7bc0fffe38000e21087',
    'ef7bc0fffe38000e23188',
    'ef7bc0fffe38000fc0007',
    'ef7bc0fffe38000fc2108',
    'ef7bc0fffe38000fe1080',
    'ef7bc0fffe3842100210f',
    'ef7bc0fffe38421021087',
    'ef7bc0fffe38421023188',
    'ef7bc0fffe384211c0007',
    'ef7bc0fffe384211c2108',
    'ef7bc0fffe384211e1080',
    'ef7bc0fffe3c21000210f',
    'ef7bc0fffe3c210021087',
    'ef7bc0fffe3c210023188',
    'ef7bc0fffe3c2101c0007',
    'ef7bc0fffe3c2101c2108',
    'ef7bc0fffe3c2101e1080',
    'ef7bc0ffffc0421e00007',
    'ef7bc0ffffc0421e02108',
    'ef7bc0ffffc0421e21080',
    'ef7bc0ffffc0421fc0000',
    'ef7bc0ffffc4210e00007',
    'ef7bc0ffffc4210e02108',
    'ef7bc0ffffc4210e21080',
    'ef7bc0ffffc4210fc0000',
    'ef7bc0ffffc4631000007',
    'ef7bc0ffffc4631002108',
    'ef7bc0ffffc4631021080',
    'ef7bc0ffffc46311c0000',
    'ef7bc0fffff8000e00007',
    'ef7bc0fffff8000e02108',
    'ef7bc0fffff8000e21080',
    'ef7bc0fffff8000fc0000',
    'ef7bc0fffff8421000007',
    'ef7bc0fffff8421002108',
    'ef7bc0fffff8421021080',
    'ef7bc0fffff84211c0000',
    'ef7bc0fffffc210000007',
    'ef7bc0fffffc210002108',
    'ef7bc0fffffc210021080',
    'ef7bc0fffffc2101c0000',
    'ef7bc7739c00421e2318f',
    'ef7bc7739c00421fc210f',
    'ef7bc7739c00421fe1087',
    'ef7bc7739c00421fe3188',
    'ef7bc7739c04210e2318f',
    'ef7bc7739c04210fc210f',
    'ef7bc7739c04210fe1087',
    'ef7bc7739c04210fe3188',
    'ef7bc7739c0463102318f',
    'ef7bc7739c046311c210f',
    'ef7bc7739c046311e1087',
    'ef7bc7739c046311e3188',
    'ef7bc7739c38000e2318f',
    'ef7bc7739c38000fc210f',
    'ef7bc7739c38000fe1087',
    'ef7bc7739c38000fe3188',
    'ef7bc7739c3842102318f',
    'ef7bc7739c384211c210f',
    'ef7bc7739c384211e1087',
    'ef7bc7739c384211e3188',
    'ef7bc7739c3c21002318f',
    'ef7bc7739c3c2101c210f',
    'ef7bc7739c3c2101e1087',
    'ef7bc7739c3c2101e3188',
    'ef7bc7739dc0421e0210f',
    'ef7bc7739dc0421e21087',
    'ef7bc7739dc0421e23188',
    'ef7bc7739dc0421fc0007',
    'ef7bc7739dc0421fc2108',
    'ef7bc7739dc0421fe1080',
    'ef7bc7739dc4210e0210f',
    'ef7bc7739dc4210e21087',
    'ef7bc7739dc4210e23188',
    'ef7bc7739dc4210fc0007',
    'ef7bc7739dc4210fc2108',
    'ef7bc7739dc4210fe1080',
    'ef7bc7739dc463100210f',
    'ef7bc7739dc4631021087',
    'ef7bc7739dc4631023188',
    'ef7bc7739dc46311c0007',
    'ef7bc7739dc46311c2108',
    'ef7bc7739dc46311e1080',
    'ef7bc7739df8000e0210f',
    'ef7bc7739df8000e21087',
    'ef7bc7739df8000e23188',
    'ef7bc7739df8000fc0007',
    'ef7bc7739df8000fc2108',
    'ef7bc7739df8000fe1080',
    'ef7bc7739df842100210f',
    'ef7bc7739df8421021087',
    'ef7bc7739df8421023188',
    'ef7bc7739df84211c0007',
    'ef7bc7739df84211c2108',
    'ef7bc7739df84211e1080',
    'ef7bc7739dfc21000210f',
    'ef7bc7739dfc210021087',
    'ef7bc7739dfc210023188',
    'ef7bc7739dfc2101c0007',
    'ef7bc7739dfc2101c2108',
    'ef7bc7739dfc2101e1080',
    'ef7bc77bde00421e0210f',
    'ef7bc77bde00421e21087',
    'ef7bc77bde00421e23188',
    'ef7bc77bde00421fc0007',
    'ef7bc77bde00421fc2108',
    'ef7bc77bde00421fe1080',
    'ef7bc77bde04210e0210f',
    'ef7bc77bde04210e21087',
    'ef7bc77bde04210e23188',
    'ef7bc77bde04210fc0007',
    'ef7bc77bde04210fc2108',
    'ef7bc77bde04210fe1080',
    'ef7bc77bde0463100210f',
    'ef7bc77bde04631021087',
    'ef7bc77bde04631023188',
    'ef7bc77bde046311c0007',
    'ef7bc77bde046311c2108',
    'ef7bc77bde046311e1080',
    'ef7bc77bde38000e0210f',
    'ef7bc77bde38000e21087',
    'ef7bc77bde38000e23188',
    'ef7bc77bde38000fc0007',
    'ef7bc77bde38000fc2108',
    'ef7bc77bde38000fe1080',
    'ef7bc77bde3842100210f',
    'ef7bc77bde38421021087',
    'ef7bc77bde38421023188',
    'ef7bc77bde384211c0007',
    'ef7bc77bde384211c2108',
    'ef7bc77bde384211e1080',
    'ef7bc77bde3c21000210f',
    'ef7bc77bde3c210021087',
    'ef7bc77bde3c210023188',
    'ef7bc77bde3c2101c0007',
    'ef7bc77bde3c2101c2108',
    'ef7bc77bde3c2101e1080',
    'ef7bc77bdfc0421e00007',
    'ef7bc77bdfc0421e02108',
    'ef7bc77bdfc0421e21080',
    'ef7bc77bdfc0421fc0000',
    'ef7bc77bdfc4210e00007',
    'ef7bc77bdfc4210e02108',
    'ef7bc77bdfc4210e21080',
    'ef7bc77bdfc4210fc0000',
    'ef7bc77bdfc4631000007',
    'ef7bc77bdfc4631002108',
    'ef7bc77bdfc4631021080',
    'ef7bc77bdfc46311c0000',
    'ef7bc77bdff8000e00007',
    'ef7bc77bdff8000e02108',
    'ef7bc77bdff8000e21080',
    'ef7bc77bdff8000fc0000',
    'ef7bc77bdff8421000007',
    'ef7bc77bdff8421002108',
    'ef7bc77bdff8421021080',
    'ef7bc77bdff84211c0000',
    'ef7bc77bdffc210000007',
    'ef7bc77bdffc210002108',
    'ef7bc77bdffc210021080',
    'ef7bc77bdffc2101c0000',
    'ef7bc7f7bc00421e0210f',
    'ef7bc7f7bc00421e21087',
    'ef7bc7f7bc00421e23188',
    'ef7bc7f7bc00421fc0007',
    'ef7bc7f7bc00421fc2108',
    'ef7bc7f7bc00421fe1080',
    'ef7bc7f7bc04210e0210f',
    'ef7bc7f7bc04210e21087',
    'ef7bc7f7bc04210e23188',
    'ef7bc7f7bc04210fc0007',
    'ef7bc7f7bc04210fc2108',
    'ef7bc7f7bc04210fe1080',
    'ef7bc7f7bc0463100210f',
    'ef7bc7f7bc04631021087',
    'ef7bc7f7bc04631023188',
    'ef7bc7f7bc046311c0007',
    'ef7bc7f7bc046311c2108',
    'ef7bc7f7bc046311e1080',
    'ef7bc7f7bc38000e0210f',
    'ef7bc7f7bc38000e21087',
    'ef7bc7f7bc38000e23188',
    'ef7bc7f7bc38000fc0007',
    'ef7bc7f7bc38000fc2108',
    'ef7bc7f7bc38000fe1080',
    'ef7bc7f7bc3842100210f',
    'ef7bc7f7bc38421021087',
    'ef7bc7f7bc38421023188',
    'ef7bc7f7bc384211c0007',
    'ef7bc7f7bc384211c2108',
    'ef7bc7f7bc384211e1080',
    'ef7bc7f7bc3c21000210f',
    'ef7bc7f7bc3c210021087',
    'ef7bc7f7bc3c210023188',
    'ef7bc7f7bc3c2101c0007',
    'ef7bc7f7bc3c2101c2108',
    'ef7bc7f7bc3c2101e1080',
    'ef7bc7f7bdc0421e00007',
    'ef7bc7f7bdc0421e02108',
    'ef7bc7f7bdc0421e21080',
    'ef7bc7f7bdc0421fc0000',
    'ef7bc7f7bdc4210e00007',
    'ef7bc7f7bdc4210e02108',
    'ef7bc7f7bdc4210e21080',
    'ef7bc7f7bdc4210fc0000',
    'ef7bc7f7bdc4631000007',
    'ef7bc7f7bdc4631002108',
    'ef7bc7f7bdc4631021080',
    'ef7bc7f7bdc46311c0000',
    'ef7bc7f7bdf8000e00007',
    'ef7bc7f7bdf8000e02108',
    'ef7bc7f7bdf8000e21080',
    'ef7bc7f7bdf8000fc0000',
    'ef7bc7f7bdf8421000007',
    'ef7bc7f7bdf8421002108',
    'ef7bc7f7bdf8421021080',
    'ef7bc7f7bdf84211c0000',
    'ef7bc7f7bdfc210000007',
    'ef7bc7f7bdfc210002108',
    'ef7bc7f7bdfc210021080',
    'ef7bc7f7bdfc2101c0000',
    'ef7bc7fffe00421e00007',
    'ef7bc7fffe00421e02108',
    'ef7bc7fffe00421e21080',
    'ef7bc7fffe00421fc0000',
    'ef7bc7fffe04210e00007',
    'ef7bc7fffe04210e02108',
    'ef7bc7fffe04210e21080',
    'ef7bc7fffe04210fc0000',
    'ef7bc7fffe04631000007',
    'ef7bc7fffe04631002108',
    'ef7bc7fffe04631021080',
    'ef7bc7fffe046311c0000',
    'ef7bc7fffe38000e00007',
    'ef7bc7fffe38000e02108',
    'ef7bc7fffe38000e21080',
    'ef7bc7fffe38000fc0000',
    'ef7bc7fffe38421000007',
    'ef7bc7fffe38421002108',
    'ef7bc7fffe38421021080',
    'ef7bc7fffe384211c0000',
    'ef7bc7fffe3c210000007',
    'ef7bc7fffe3c210002108',
    'ef7bc7fffe3c210021080',
    'ef7bc7fffe3c2101c0000',
    'ef7bc7ffffc0421e00000',
    'ef7bc7ffffc4210e00000',
    'ef7bc7ffffc4631000000',
    'ef7bc7fffff8000e00000',
    'ef7bc7fffff8421000000',
    'ef7bc7fffffc210000000',
    'ef7bf8739c00000fe318f',
    'ef7bf8739c004211e318f',
    'ef7bf8739c042101e318f',
    'ef7bf8739c380001e318f',
    'ef7bf8739dc0000e2318f',
    'ef7bf8739dc0000fc210f',
    'ef7bf8739dc0000fe1087',
    'ef7bf8739dc0000fe3188',
    'ef7bf8739dc042102318f',
    'ef7bf8739dc04211c210f',
    'ef7bf8739dc04211e1087',
    'ef7bf8739dc04211e3188',
    'ef7bf8739dc421002318f',
    'ef7bf8739dc42101c210f',
    'ef7bf8739dc42101e1087',
    'ef7bf8739dc42101e3188',
    'ef7bf8739df800002318f',
    'ef7bf8739df80001c210f',
    'ef7bf8739df80001e1087',
    'ef7bf8739df80001e3188',
    'ef7bf87bde00000e2318f',
    'ef7bf87bde00000fc210f',
    'ef7bf87bde00000fe1087',
    'ef7bf87bde00000fe3188',
    'ef7bf87bde0042102318f',
    'ef7bf87bde004211c210f',
    'ef7bf87bde004211e1087',
    'ef7bf87bde004211e3188',
    'ef7bf87bde0421002318f',
    'ef7bf87bde042101c210f',
    'ef7bf87bde042101e1087',
    'ef7bf87bde042101e3188',
    'ef7bf87bde3800002318f',
    'ef7bf87bde380001c210f',
    'ef7bf87bde380001e1087',
    'ef7bf87bde380001e3188',
    'ef7bf87bdfc0000e0210f',
    'ef7bf87bdfc0000e21087',
    'ef7bf87bdfc0000e23188',
    'ef7bf87bdfc0000fc0007',
    'ef7bf87bdfc0000fc2108',
    'ef7bf87bdfc0000fe1080',
    'ef7bf87bdfc042100210f',
    'ef7bf87bdfc0421021087',
    'ef7bf87bdfc0421023188',
    'ef7bf87bdfc04211c0007',
    'ef7bf87bdfc04211c2108',
    'ef7bf87bdfc04211e1080',
    'ef7bf87bdfc421000210f',
    'ef7bf87bdfc4210021087',
    'ef7bf87bdfc4210023188',
    'ef7bf87bdfc42101c0007',
    'ef7bf87bdfc42101c2108',
    'ef7bf87bdfc42101e1080',
    'ef7bf87bdff800000210f',
    'ef7bf87bdff8000021087',
    'ef7bf87bdff8000023188',
    'ef7bf87bdff80001c0007',
    'ef7bf87bdff80001c2108',
    'ef7bf87bdff80001e1080',
    'ef7bf8f7bc00000e2318f',
    'ef7bf8f7bc00000fc210f',
    'ef7bf8f7bc00000fe1087',
    'ef7bf8f7bc00000fe3188',
    'ef7bf8f7bc0042102318f',
    'ef7bf8f7bc004211c210f',
    'ef7bf8f7bc004211e1087',
    'ef7bf8f7bc004211e3188',
    'ef7bf8f7bc0421002318f',
    'ef7bf8f7bc042101c210f',
    'ef7bf8f7bc042101e1087',
    'ef7bf8f7bc042101e3188',
    'ef7bf8f7bc3800002318f',
    'ef7bf8f7bc380001c210f',
    'ef7bf8f7bc380001e1087',
    'ef7bf8f7bc380001e3188',
    'ef7bf8f7bdc0000e0210f',
    'ef7bf8f7bdc0000e21087',
    'ef7bf8f7bdc0000e23188',
    'ef7bf8f7bdc0000fc0007',
    'ef7bf8f7bdc0000fc2108',
    'ef7bf8f7bdc0000fe1080',
    'ef7bf8f7bdc042100210f',
    'ef7bf8f7bdc0421021087',
    'ef7bf8f7bdc0421023188',
    'ef7bf8f7bdc04211c0007',
    'ef7bf8f7bdc04211c2108',
    'ef7bf8f7bdc04211e1080',
    'ef7bf8f7bdc421000210f',
    'ef7bf8f7bdc4210021087',
    'ef7bf8f7bdc4210023188',
    'ef7bf8f7bdc42101c0007',
    'ef7bf8f7bdc42101c2108',
    'ef7bf8f7bdc42101e1080',
    'ef7bf8f7bdf800000210f',
    'ef7bf8f7bdf8000021087',
    'ef7bf8f7bdf8000023188',
    'ef7bf8f7bdf80001c0007',
    'ef7bf8f7bdf80001c2108',
    'ef7bf8f7bdf80001e1080',
    'ef7bf8fffe00000e0210f',
    'ef7bf8fffe00000e21087',
    'ef7bf8fffe00000e23188',
    'ef7bf8fffe00000fc0007',
    'ef7bf8fffe00000fc2108',
    'ef7bf8fffe00000fe1080',
    'ef7bf8fffe0042100210f',
    'ef7bf8fffe00421021087',
    'ef7bf8fffe00421023188',
    'ef7bf8fffe004211c0007',
    'ef7bf8fffe004211c2108',
    'ef7bf8fffe004211e1080',
    'ef7bf8fffe0421000210f',
    'ef7bf8fffe04210021087',
    'ef7bf8fffe04210023188',
    'ef7bf8fffe042101c0007',
    'ef7bf8fffe042101c2108',
    'ef7bf8fffe042101e1080',
    'ef7bf8fffe3800000210f',
    'ef7bf8fffe38000021087',
    'ef7bf8fffe38000023188',
    'ef7bf8fffe380001c0007',
    'ef7bf8fffe380001c2108',
    'ef7bf8fffe380001e1080',
    'ef7bf8ffffc0000e00007',
    'ef7bf8ffffc0000e02108',
    'ef7bf8ffffc0000e21080',
    'ef7bf8ffffc0000fc0000',
    'ef7bf8ffffc0421000007',
    'ef7bf8ffffc0421002108',
    'ef7bf8ffffc0421021080',
    'ef7bf8ffffc04211c0000',
    'ef7bf8ffffc4210000007',
    'ef7bf8ffffc4210002108',
    'ef7bf8ffffc4210021080',
    'ef7bf8ffffc42101c0000',
    'ef7bf8fffff8000000007',
    'ef7bf8fffff8000002108',
    'ef7bf8fffff8000021080',
    'ef7bf8fffff80001c0000',
    'ef7bff739c00000e2318f',
    'ef7bff739c00000fc210f',
    'ef7bff739c00000fe1087',
    'ef7bff739c00000fe3188',
    'ef7bff739c0042102318f',
    'ef7bff739c004211c210f',
    'ef7bff739c004211e1087',
    'ef7bff739c004211e3188',
    'ef7bff739c0421002318f',
    'ef7bff739c042101c210f',
    'ef7bff739c042101e1087',
    'ef7bff739c042101e3188',
    'ef7bff739c3800002318f',
    'ef7bff739c380001c210f',
    'ef7bff739c380001e1087',
    'ef7bff739c380001e3188',
    'ef7bff739dc0000e0210f',
    'ef7bff739dc0000e21087',
    'ef7bff739dc0000e23188',
    'ef7bff739dc0000fc0007',
    'ef7bff739dc0000fc2108',
    'ef7bff739dc0000fe1080',
    'ef7bff739dc042100210f',
    'ef7bff739dc0421021087',
    'ef7bff739dc0421023188',
    'ef7bff739dc04211c0007',
    'ef7bff739dc04211c2108',
    'ef7bff739dc04211e1080',
    'ef7bff739dc421000210f',
    'ef7bff739dc4210021087',
    'ef7bff739dc4210023188',
    'ef7bff739dc42101c0007',
    'ef7bff739dc42101c2108',
    'ef7bff739dc42101e1080',
    'ef7bff739df800000210f',
    'ef7bff739df8000021087',
    'ef7bff739df8000023188',
    'ef7bff739df80001c0007',
    'ef7bff739df80001c2108',
    'ef7bff739df80001e1080',
    'ef7bff7bde00000e0210f',
    'ef7bff7bde00000e21087',
    'ef7bff7bde00000e23188',
    'ef7bff7bde00000fc0007',
    'ef7bff7bde00000fc2108',
    'ef7bff7bde00000fe1080',
    'ef7bff7bde0042100210f',
    'ef7bff7bde00421021087',
    'ef7bff7bde00421023188',
    'ef7bff7bde004211c0007',
    'ef7bff7bde004211c2108',
    'ef7bff7bde004211e1080',
    'ef7bff7bde0421000210f',
    'ef7bff7bde04210021087',
    'ef7bff7bde04210023188',
    'ef7bff7bde042101c0007',
    'ef7bff7bde042101c2108',
    'ef7bff7bde042101e1080',
    'ef7bff7bde3800000210f',
    'ef7bff7bde38000021087',
    'ef7bff7bde38000023188',
    'ef7bff7bde380001c0007',
    'ef7bff7bde380001c2108',
    'ef7bff7bde380001e1080',
    'ef7bff7bdfc0000e00007',
    'ef7bff7bdfc0000e02108',
    'ef7bff7bdfc0000e21080',
    'ef7bff7bdfc0000fc0000',
    'ef7bff7bdfc0421000007',
    'ef7bff7bdfc0421002108',
    'ef7bff7bdfc0421021080',
    'ef7bff7bdfc04211c0000',
    'ef7bff7bdfc4210000007',
    'ef7bff7bdfc4210002108',
    'ef7bff7bdfc4210021080',
    'ef7bff7bdfc42101c0000',
    'ef7bff7bdff8000000007',
    'ef7bff7bdff8000002108',
    'ef7bff7bdff8000021080',
    'ef7bff7bdff80001c0000',
    'ef7bfff7bc00000e0210f',
    'ef7bfff7bc00000e21087',
    'ef7bfff7bc00000e23188',
    'ef7bfff7bc00000fc0007',
    'ef7bfff7bc00000fc2108',
    'ef7bfff7bc00000fe1080',
    'ef7bfff7bc0042100210f',
    'ef7bfff7bc00421021087',
    'ef7bfff7bc00421023188',
    'ef7bfff7bc004211c0007',
    'ef7bfff7bc004211c2108',
    'ef7bfff7bc004211e1080',
    'ef7bfff7bc0421000210f',
    'ef7bfff7bc04210021087',
    'ef7bfff7bc04210023188',
    'ef7bfff7bc042101c0007',
    'ef7bfff7bc042101c2108',
    'ef7bfff7bc042101e1080',
    'ef7bfff7bc3800000210f',
    'ef7bfff7bc38000021087',
    'ef7bfff7bc38000023188',
    'ef7bfff7bc380001c0007',
    'ef7bfff7bc380001c2108',
    'ef7bfff7bc380001e1080',
    'ef7bfff7bdc0000e00007',
    'ef7bfff7bdc0000e02108',
    'ef7bfff7bdc0000e21080',
    'ef7bfff7bdc0000fc0000',
    'ef7bfff7bdc0421000007',
    'ef7bfff7bdc0421002108',
    'ef7bfff7bdc0421021080',
    'ef7bfff7bdc04211c0000',
    'ef7bfff7bdc4210000007',
    'ef7bfff7bdc4210002108',
    'ef7bfff7bdc4210021080',
    'ef7bfff7bdc42101c0000',
    'ef7bfff7bdf8000000007',
    'ef7bfff7bdf8000002108',
    'ef7bfff7bdf8000021080',
    'ef7bfff7bdf80001c0000',
    'ef7bfffffe00000e00007',
    'ef7bfffffe00000e02108',
    'ef7bfffffe00000e21080',
    'ef7bfffffe00000fc0000',
    'ef7bfffffe00421000007',
    'ef7bfffffe00421002108',
    'ef7bfffffe00421021080',
    'ef7bfffffe004211c0000',
    'ef7bfffffe04210000007',
    'ef7bfffffe04210002108',
    'ef7bfffffe04210021080',
    'ef7bfffffe042101c0000',
    'ef7bfffffe38000000007',
    'ef7bfffffe38000002108',
    'ef7bfffffe38000021080',
    'ef7bfffffe380001c0000',
    'ef7bffffffc0000e00000',
    'ef7bffffffc0421000000',
    'ef7bffffffc4210000000',
    'ef7bfffffff8000000000',
    'fef780739c00421fe318f',
    'fef780739c04210fe318f',
    'fef780739c046311e318f',
    'fef780739c38000fe318f',
    'fef780739c384211e318f',
    'fef780739c3c2101e318f',
    'fef780739dc0421e2318f',
    'fef780739dc0421fc210f',
    'fef780739dc0421fe1087',
    'fef780739dc0421fe3188',
    'fef780739dc4210e2318f',
    'fef780739dc4210fc210f',
    'fef780739dc4210fe1087',
    'fef780739dc4210fe3188',
    'fef780739dc463102318f',
    'fef780739dc46311c210f',
    'fef780739dc46311e1087',
    'fef780739dc46311e3188',
    'fef780739df8000e2318f',
    'fef780739df8000fc210f',
    'fef780739df8000fe1087',
    'fef780739df8000fe3188',
    'fef780739df842102318f',
    'fef780739df84211c210f',
    'fef780739df84211e1087',
    'fef780739df84211e3188',
    'fef780739dfc21002318f',
    'fef780739dfc2101c210f',
    'fef780739dfc2101e1087',
    'fef780739dfc2101e3188',
    'fef7807bde00421e2318f',
    'fef7807bde00421fc210f',
    'fef7807bde00421fe1087',
    'fef7807bde00421fe3188',
    'fef7807bde04210e2318f',
    'fef7807bde04210fc210f',
    'fef7807bde04210fe1087',
    'fef7807bde04210fe3188',
    'fef7807bde0463102318f',
    'fef7807bde046311c210f',
    'fef7807bde046311e1087',
    'fef7807bde046311e3188',
    'fef7807bde38000e2318f',
    'fef7807bde38000fc210f',
    'fef7807bde38000fe1087',
    'fef7807bde38000fe3188',
    'fef7807bde3842102318f',
    'fef7807bde384211c210f',
    'fef7807bde384211e1087',
    'fef7807bde384211e3188',
    'fef7807bde3c21002318f',
    'fef7807bde3c2101c210f',
    'fef7807bde3c2101e1087',
    'fef7807bde3c2101e3188',
    'fef7807bdfc0421e0210f',
    'fef7807bdfc0421e21087',
    'fef7807bdfc0421e23188',
    'fef7807bdfc0421fc0007',
    'fef7807bdfc0421fc2108',
    'fef7807bdfc0421fe1080',
    'fef7807bdfc4210e0210f',
    'fef7807bdfc4210e21087',
    'fef7807bdfc4210e23188',
    'fef7807bdfc4210fc0007',
    'fef7807bdfc4210fc2108',
    'fef7807bdfc4210fe1080',
    'fef7807bdfc463100210f',
    'fef7807bdfc4631021087',
    'fef7807bdfc4631023188',
    'fef7807bdfc46311c0007',
    'fef7807bdfc46311c2108',
    'fef7807bdfc46311e1080',
    'fef7807bdff8000e0210f',
    'fef7807bdff8000e21087',
    'fef7807bdff8000e23188',
    'fef7807bdff8000fc0007',
    'fef7807bdff8000fc2108',
    'fef7807bdff8000fe1080',
    'fef7807bdff842100210f',
    'fef7807bdff8421021087',
    'fef7807bdff8421023188',
    'fef7807bdff84211c0007',
    'fef7807bdff84211c2108',
    'fef7807bdff84211e1080',
    'fef7807bdffc21000210f',
    'fef7807bdffc210021087',
    'fef7807bdffc210023188',
    'fef7807bdffc2101c0007',
    'fef7807bdffc2101c2108',
    'fef7807bdffc2101e1080',
    'fef780f7bc00421e2318f',
    'fef780f7bc00421fc210f',
    'fef780f7bc00421fe1087',
    'fef780f7bc00421fe3188',
    'fef780f7bc04210e2318f',
    'fef780f7bc04210fc210f',
    'fef780f7bc04210fe1087',
    'fef780f7bc04210fe3188',
    'fef780f7bc0463102318f',
    'fef780f7bc046311c210f',
    'fef780f7bc046311e1087',
    'fef780f7bc046311e3188',
    'fef780f7bc38000e2318f',
    'fef780f7bc38000fc210f',
    'fef780f7bc38000fe1087',
    'fef780f7bc38000fe3188',
    'fef780f7bc3842102318f',
    'fef780f7bc384211c210f',
    'fef780f7bc384211e1087',
    'fef780f7bc384211e3188',
    'fef780f7bc3c21002318f',
    'fef780f7bc3c2101c210f',
    'fef780f7bc3c2101e1087',
    'fef780f7bc3c2101e3188',
    'fef780f7bdc0421e0210f',
    'fef780f7bdc0421e21087',
    'fef780f7bdc0421e23188',
    'fef780f7bdc0421fc0007',
    'fef780f7bdc0421fc2108',
    'fef780f7bdc0421fe1080',
    'fef780f7bdc4210e0210f',
    'fef780f7bdc4210e21087',
    'fef780f7bdc4210e23188',
    'fef780f7bdc4210fc0007',
    'fef780f7bdc4210fc2108',
    'fef780f7bdc4210fe1080',
    'fef780f7bdc463100210f',
    'fef780f7bdc4631021087',
    'fef780f7bdc4631023188',
    'fef780f7bdc46311c0007',
    'fef780f7bdc46311c2108',
    'fef780f7bdc46311e1080',
    'fef780f7bdf8000e0210f',
    'fef780f7bdf8000e21087',
    'fef780f7bdf8000e23188',
    'fef780f7bdf8000fc0007',
    'fef780f7bdf8000fc2108',
    'fef780f7bdf8000fe1080',
    'fef780f7bdf842100210f',
    'fef780f7bdf8421021087',
    'fef780f7bdf8421023188',
    'fef780f7bdf84211c0007',
    'fef780f7bdf84211c2108',
    'fef780f7bdf84211e1080',
    'fef780f7bdfc21000210f',
    'fef780f7bdfc210021087',
    'fef780f7bdfc210023188',
    'fef780f7bdfc2101c0007',
    'fef780f7bdfc2101c2108',
    'fef780f7bdfc2101e1080',
    'fef780fffe00421e0210f',
    'fef780fffe00421e21087',
    'fef780fffe00421e23188',
    'fef780fffe00421fc0007',
    'fef780fffe00421fc2108',
    'fef780fffe00421fe1080',
    'fef780fffe04210e0210f',
    'fef780fffe04210e21087',
    'fef780fffe04210e23188',
    'fef780fffe04210fc0007',
    'fef780fffe04210fc2108',
    'fef780fffe04210fe1080',
    'fef780fffe0463100210f',
    'fef780fffe04631021087',
    'fef780fffe04631023188',
    'fef780fffe046311c0007',
    'fef780fffe046311c2108',
    'fef780fffe046311e1080',
    'fef780fffe38000e0210f',
    'fef780fffe38000e21087',
    'fef780fffe38000e23188',
    'fef780fffe38000fc0007',
    'fef780fffe38000fc2108',
    'fef780fffe38000fe1080',
    'fef780fffe3842100210f',
    'fef780fffe38421021087',
    'fef780fffe38421023188',
    'fef780fffe384211c0007',
    'fef780fffe384211c2108',
    'fef780fffe384211e1080',
    'fef780fffe3c21000210f',
    'fef780fffe3c210021087',
    'fef780fffe3c210023188',
    'fef780fffe3c2101c0007',
    'fef780fffe3c2101c2108',
    'fef780fffe3c2101e1080',
    'fef780ffffc0421e00007',
    'fef780ffffc0421e02108',
    'fef780ffffc0421e21080',
    'fef780ffffc0421fc0000',
    'fef780ffffc4210e00007',
    'fef780ffffc4210e02108',
    'fef780ffffc4210e21080',
    'fef780ffffc4210fc0000',
    'fef780ffffc4631000007',
    'fef780ffffc4631002108',
    'fef780ffffc4631021080',
    'fef780ffffc46311c0000',
    'fef780fffff8000e00007',
    'fef780fffff8000e02108',
    'fef780fffff8000e21080',
    'fef780fffff8000fc0000',
    'fef780fffff8421000007',
    'fef780fffff8421002108',
    'fef780fffff8421021080',
    'fef780fffff84211c0000',
    'fef780fffffc210000007',
    'fef780fffffc210002108',
    'fef780fffffc210021080',
    'fef780fffffc2101c0000',
    'fef787739c00421e2318f',
    'fef787739c00421fc210f',
    'fef787739c00421fe1087',
    'fef787739c00421fe3188',
    'fef787739c04210e2318f',
    'fef787739c04210fc210f',
    'fef787739c04210fe1087',
    'fef787739c04210fe3188',
    'fef787739c0463102318f',
    'fef787739c046311c210f',
    'fef787739c046311e1087',
    'fef787739c046311e3188',
    'fef787739c38000e2318f',
    'fef787739c38000fc210f',
    'fef787739c38000fe1087',
    'fef787739c38000fe3188',
    'fef787739c3842102318f',
    'fef787739c384211c210f',
    'fef787739c384211e1087',
    'fef787739c384211e3188',
    'fef787739c3c21002318f',
    'fef787739c3c2101c210f',
    'fef787739c3c2101e1087',
    'fef787739c3c2101e3188',
    'fef787739dc0421e0210f',
    'fef787739dc0421e21087',
    'fef787739dc0421e23188',
    'fef787739dc0421fc0007',
    'fef787739dc0421fc2108',
    'fef787739dc0421fe1080',
    'fef787739dc4210e0210f',
    'fef787739dc4210e21087',
    'fef787739dc4210e23188',
    'fef787739dc4210fc0007',
    'fef787739dc4210fc2108',
    'fef787739dc4210fe1080',
    'fef787739dc463100210f',
    'fef787739dc4631021087',
    'fef787739dc4631023188',
    'fef787739dc46311c0007',
    'fef787739dc46311c2108',
    'fef787739dc46311e1080',
    'fef787739df8000e0210f',
    'fef787739df8000e21087',
    'fef787739df8000e23188',
    'fef787739df8000fc0007',
    'fef787739df8000fc2108',
    'fef787739df8000fe1080',
    'fef787739df842100210f',
    'fef787739df8421021087',
    'fef787739df8421023188',
    'fef787739df84211c0007',
    'fef787739df84211c2108',
    'fef787739df84211e1080',
    'fef787739dfc21000210f',
    'fef787739dfc210021087',
    'fef787739dfc210023188',
    'fef787739dfc2101c0007',
    'fef787739dfc2101c2108',
    'fef787739dfc2101e1080',
    'fef7877bde00421e0210f',
    'fef7877bde00421e21087',
    'fef7877bde00421e23188',
    'fef7877bde00421fc0007',
    'fef7877bde00421fc2108',
    'fef7877bde00421fe1080',
    'fef7877bde04210e0210f',
    'fef7877bde04210e21087',
    'fef7877bde04210e23188',
    'fef7877bde04210fc0007',
    'fef7877bde04210fc2108',
    'fef7877bde04210fe1080',
    'fef7877bde0463100210f',
    'fef7877bde04631021087',
    'fef7877bde04631023188',
    'fef7877bde046311c0007',
    'fef7877bde046311c2108',
    'fef7877bde046311e1080',
    'fef7877bde38000e0210f',
    'fef7877bde38000e21087',
    'fef7877bde38000e23188',
    'fef7877bde38000fc0007',
    'fef7877bde38000fc2108',
    'fef7877bde38000fe1080',
    'fef7877bde3842100210f',
    'fef7877bde38421021087',
    'fef7877bde38421023188',
    'fef7877bde384211c0007',
    'fef7877bde384211c2108',
    'fef7877bde384211e1080',
    'fef7877bde3c21000210f',
    'fef7877bde3c210021087',
    'fef7877bde3c210023188',
    'fef7877bde3c2101c0007',
    'fef7877bde3c2101c2108',
    'fef7877bde3c2101e1080',
    'fef7877bdfc0421e00007',
    'fef7877bdfc0421e02108',
    'fef7877bdfc0421e21080',
    'fef7877bdfc0421fc0000',
    'fef7877bdfc4210e00007',
    'fef7877bdfc4210e02108',
    'fef7877bdfc4210e21080',
    'fef7877bdfc4210fc0000',
    'fef7877bdfc4631000007',
    'fef7877bdfc4631002108',
    'fef7877bdfc4631021080',
    'fef7877bdfc46311c0000',
    'fef7877bdff8000e00007',
    'fef7877bdff8000e02108',
    'fef7877bdff8000e21080',
    'fef7877bdff8000fc0000',
    'fef7877bdff8421000007',
    'fef7877bdff8421002108',
    'fef7877bdff8421021080',
    'fef7877bdff84211c0000',
    'fef7877bdffc210000007',
    'fef7877bdffc210002108',
    'fef7877bdffc210021080',
    'fef7877bdffc2101c0000',
    'fef787f7bc00421e0210f',
    'fef787f7bc00421e21087',
    'fef787f7bc00421e23188',
    'fef787f7bc00421fc0007',
    'fef787f7bc00421fc2108',
    'fef787f7bc00421fe1080',
    'fef787f7bc04210e0210f',
    'fef787f7bc04210e21087',
    'fef787f7bc04210e23188',
    'fef787f7bc04210fc0007',
    'fef787f7bc04210fc2108',
    'fef787f7bc04210fe1080',
    'fef787f7bc0463100210f',
    'fef787f7bc04631021087',
    'fef787f7bc04631023188',
    'fef787f7bc046311c0007',
    'fef787f7bc046311c2108',
    'fef787f7bc046311e1080',
    'fef787f7bc38000e0210f',
    'fef787f7bc38000e21087',
    'fef787f7bc38000e23188',
    'fef787f7bc38000fc0007',
    'fef787f7bc38000fc2108',
    'fef787f7bc38000fe1080',
    'fef787f7bc3842100210f',
    'fef787f7bc38421021087',
    'fef787f7bc38421023188',
    'fef787f7bc384211c0007',
    'fef787f7bc384211c2108',
    'fef787f7bc384211e1080',
    'fef787f7bc3c21000210f',
    'fef787f7bc3c210021087',
    'fef787f7bc3c210023188',
    'fef787f7bc3c2101c0007',
    'fef787f7bc3c2101c2108',
    'fef787f7bc3c2101e1080',
    'fef787f7bdc0421e00007',
    'fef787f7bdc0421e02108',
    'fef787f7bdc0421e21080',
    'fef787f7bdc0421fc0000',
    'fef787f7bdc4210e00007',
    'fef787f7bdc4210e02108',
    'fef787f7bdc4210e21080',
    'fef787f7bdc4210fc0000',
    'fef787f7bdc4631000007',
    'fef787f7bdc4631002108',
    'fef787f7bdc4631021080',
    'fef787f7bdc46311c0000',
    'fef787f7bdf8000e00007',
    'fef787f7bdf8000e02108',
    'fef787f7bdf8000e21080',
    'fef787f7bdf8000fc0000',
    'fef787f7bdf8421000007',
    'fef787f7bdf8421002108',
    'fef787f7bdf8421021080',
    'fef787f7bdf84211c0000',
    'fef787f7bdfc210000007',
    'fef787f7bdfc210002108',
    'fef787f7bdfc210021080',
    'fef787f7bdfc2101c0000',
    'fef787fffe00421e00007',
    'fef787fffe00421e02108',
    'fef787fffe00421e21080',
    'fef787fffe00421fc0000',
    'fef787fffe04210e00007',
    'fef787fffe04210e02108',
    'fef787fffe04210e21080',
    'fef787fffe04210fc0000',
    'fef787fffe04631000007',
    'fef787fffe04631002108',
    'fef787fffe04631021080',
    'fef787fffe046311c0000',
    'fef787fffe38000e00007',
    'fef787fffe38000e02108',
    'fef787fffe38000e21080',
    'fef787fffe38000fc0000',
    'fef787fffe38421000007',
    'fef787fffe38421002108',
    'fef787fffe38421021080',
    'fef787fffe384211c0000',
    'fef787fffe3c210000007',
    'fef787fffe3c210002108',
    'fef787fffe3c210021080',
    'fef787fffe3c2101c0000',
    'fef787ffffc0421e00000',
    'fef787ffffc4210e00000',
    'fef787ffffc4631000000',
    'fef787fffff8000e00000',
    'fef787fffff8421000000',
    'fef787fffffc210000000',
    'fef7b8739c00000fe318f',
    'fef7b8739c004211e318f',
    'fef7b8739c042101e318f',
    'fef7b8739c380001e318f',
    'fef7b8739dc0000e2318f',
    'fef7b8739dc0000fc210f',
    'fef7b8739dc0000fe1087',
    'fef7b8739dc0000fe3188',
    'fef7b8739dc042102318f',
    'fef7b8739dc04211c210f',
    'fef7b8739dc04211e1087',
    'fef7b8739dc04211e3188',
    'fef7b8739dc421002318f',
    'fef7b8739dc42101c210f',
    'fef7b8739dc42101e1087',
    'fef7b8739dc42101e3188',
    'fef7b8739df800002318f',
    'fef7b8739df80001c210f',
    'fef7b8739df80001e1087',
    'fef7b8739df80001e3188',
    'fef7b87bde00000e2318f',
    'fef7b87bde00000fc210f',
    'fef7b87bde00000fe1087',
    'fef7b87bde00000fe3188',
    'fef7b87bde0042102318f',
    'fef7b87bde004211c210f',
    'fef7b87bde004211e1087',
    'fef7b87bde004211e3188',
    'fef7b87bde0421002318f',
    'fef7b87bde042101c210f',
    'fef7b87bde042101e1087',
    'fef7b87bde042101e3188',
    'fef7b87bde3800002318f',
    'fef7b87bde380001c210f',
    'fef7b87bde380001e1087',
    'fef7b87bde380001e3188',
    'fef7b87bdfc0000e0210f',
    'fef7b87bdfc0000e21087',
    'fef7b87bdfc0000e23188',
    'fef7b87bdfc0000fc0007',
    'fef7b87bdfc0000fc2108',
    'fef7b87bdfc0000fe1080',
    'fef7b87bdfc042100210f',
    'fef7b87bdfc0421021087',
    'fef7b87bdfc0421023188',
    'fef7b87bdfc04211c0007',
    'fef7b87bdfc04211c2108',
    'fef7b87bdfc04211e1080',
    'fef7b87bdfc421000210f',
    'fef7b87bdfc4210021087',
    'fef7b87bdfc4210023188',
    'fef7b87bdfc42101c0007',
    'fef7b87bdfc42101c2108',
    'fef7b87bdfc42101e1080',
    'fef7b87bdff800000210f',
    'fef7b87bdff8000021087',
    'fef7b87bdff8000023188',
    'fef7b87bdff80001c0007',
    'fef7b87bdff80001c2108',
    'fef7b87bdff80001e1080',
    'fef7b8f7bc00000e2318f',
    'fef7b8f7bc00000fc210f',
    'fef7b8f7bc00000fe1087',
    'fef7b8f7bc00000fe3188',
    'fef7b8f7bc0042102318f',
    'fef7b8f7bc004211c210f',
    'fef7b8f7bc004211e1087',
    'fef7b8f7bc004211e3188',
    'fef7b8f7bc0421002318f',
    'fef7b8f7bc042101c210f',
    'fef7b8f7bc042101e1087',
    'fef7b8f7bc042101e3188',
    'fef7b8f7bc3800002318f',
    'fef7b8f7bc380001c210f',
    'fef7b8f7bc380001e1087',
    'fef7b8f7bc380001e3188',
    'fef7b8f7bdc0000e0210f',
    'fef7b8f7bdc0000e21087',
    'fef7b8f7bdc0000e23188',
    'fef7b8f7bdc0000fc0007',
    'fef7b8f7bdc0000fc2108',
    'fef7b8f7bdc0000fe1080',
    'fef7b8f7bdc042100210f',
    'fef7b8f7bdc0421021087',
    'fef7b8f7bdc0421023188',
    'fef7b8f7bdc04211c0007',
    'fef7b8f7bdc04211c2108',
    'fef7b8f7bdc04211e1080',
    'fef7b8f7bdc421000210f',
    'fef7b8f7bdc4210021087',
    'fef7b8f7bdc4210023188',
    'fef7b8f7bdc42101c0007',
    'fef7b8f7bdc42101c2108',
    'fef7b8f7bdc42101e1080',
    'fef7b8f7bdf800000210f',
    'fef7b8f7bdf8000021087',
    'fef7b8f7bdf8000023188',
    'fef7b8f7bdf80001c0007',
    'fef7b8f7bdf80001c2108',
    'fef7b8f7bdf80001e1080',
    'fef7b8fffe00000e0210f',
    'fef7b8fffe00000e21087',
    'fef7b8fffe00000e23188',
    'fef7b8fffe00000fc0007',
    'fef7b8fffe00000fc2108',
    'fef7b8fffe00000fe1080',
    'fef7b8fffe0042100210f',
    'fef7b8fffe00421021087',
    'fef7b8fffe00421023188',
    'fef7b8fffe004211c0007',
    'fef7b8fffe004211c2108',
    'fef7b8fffe004211e1080',
    'fef7b8fffe0421000210f',
    'fef7b8fffe04210021087',
    'fef7b8fffe04210023188',
    'fef7b8fffe042101c0007',
    'fef7b8fffe042101c2108',
    'fef7b8fffe042101e1080',
    'fef7b8fffe3800000210f',
    'fef7b8fffe38000021087',
    'fef7b8fffe38000023188',
    'fef7b8fffe380001c0007',
    'fef7b8fffe380001c2108',
    'fef7b8fffe380001e1080',
    'fef7b8ffffc0000e00007',
    'fef7b8ffffc0000e02108',
    'fef7b8ffffc0000e21080',
    'fef7b8ffffc0000fc0000',
    'fef7b8ffffc0421000007',
    'fef7b8ffffc0421002108',
    'fef7b8ffffc0421021080',
    'fef7b8ffffc04211c0000',
    'fef7b8ffffc4210000007',
    'fef7b8ffffc4210002108',
    'fef7b8ffffc4210021080',
    'fef7b8ffffc42101c0000',
    'fef7b8fffff8000000007',
    'fef7b8fffff8000002108',
    'fef7b8fffff8000021080',
    'fef7b8fffff80001c0000',
    'fef7bf739c00000e2318f',
    'fef7bf739c00000fc210f',
    'fef7bf739c00000fe1087',
    'fef7bf739c00000fe3188',
    'fef7bf739c0042102318f',
    'fef7bf739c004211c210f',
    'fef7bf739c004211e1087',
    'fef7bf739c004211e3188',
    'fef7bf739c0421002318f',
    'fef7bf739c042101c210f',
    'fef7bf739c042101e1087',
    'fef7bf739c042101e3188',
    'fef7bf739c3800002318f',
    'fef7bf739c380001c210f',
    'fef7bf739c380001e1087',
    'fef7bf739c380001e3188',
    'fef7bf739dc0000e0210f',
    'fef7bf739dc0000e21087',
    'fef7bf739dc0000e23188',
    'fef7bf739dc0000fc0007',
    'fef7bf739dc0000fc2108',
    'fef7bf739dc0000fe1080',
    'fef7bf739dc042100210f',
    'fef7bf739dc0421021087',
    'fef7bf739dc0421023188',
    'fef7bf739dc04211c0007',
    'fef7bf739dc04211c2108',
    'fef7bf739dc04211e1080',
    'fef7bf739dc421000210f',
    'fef7bf739dc4210021087',
    'fef7bf739dc4210023188',
    'fef7bf739dc42101c0007',
    'fef7bf739dc42101c2108',
    'fef7bf739dc42101e1080',
    'fef7bf739df800000210f',
    'fef7bf739df8000021087',
    'fef7bf739df8000023188',
    'fef7bf739df80001c0007',
    'fef7bf739df80001c2108',
    'fef7bf739df80001e1080',
    'fef7bf7bde00000e0210f',
    'fef7bf7bde00000e21087',
    'fef7bf7bde00000e23188',
    'fef7bf7bde00000fc0007',
    'fef7bf7bde00000fc2108',
    'fef7bf7bde00000fe1080',
    'fef7bf7bde0042100210f',
    'fef7bf7bde00421021087',
    'fef7bf7bde00421023188',
    'fef7bf7bde004211c0007',
    'fef7bf7bde004211c2108',
    'fef7bf7bde004211e1080',
    'fef7bf7bde0421000210f',
    'fef7bf7bde04210021087',
    'fef7bf7bde04210023188',
    'fef7bf7bde042101c0007',
    'fef7bf7bde042101c2108',
    'fef7bf7bde042101e1080',
    'fef7bf7bde3800000210f',
    'fef7bf7bde38000021087',
    'fef7bf7bde38000023188',
    'fef7bf7bde380001c0007',
    'fef7bf7bde380001c2108',
    'fef7bf7bde380001e1080',
    'fef7bf7bdfc0000e00007',
    'fef7bf7bdfc0000e02108',
    'fef7bf7bdfc0000e21080',
    'fef7bf7bdfc0000fc0000',
    'fef7bf7bdfc0421000007',
    'fef7bf7bdfc0421002108',
    'fef7bf7bdfc0421021080',
    'fef7bf7bdfc04211c0000',
    'fef7bf7bdfc4210000007',
    'fef7bf7bdfc4210002108',
    'fef7bf7bdfc4210021080',
    'fef7bf7bdfc42101c0000',
    'fef7bf7bdff8000000007',
    'fef7bf7bdff8000002108',
    'fef7bf7bdff8000021080',
    'fef7bf7bdff80001c0000',
    'fef7bff7bc00000e0210f',
    'fef7bff7bc00000e21087',
    'fef7bff7bc00000e23188',
    'fef7bff7bc00000fc0007',
    'fef7bff7bc00000fc2108',
    'fef7bff7bc00000fe1080',
    'fef7bff7bc0042100210f',
    'fef7bff7bc00421021087',
    'fef7bff7bc00421023188',
    'fef7bff7bc004211c0007',
    'fef7bff7bc004211c2108',
    'fef7bff7bc004211e1080',
    'fef7bff7bc0421000210f',
    'fef7bff7bc04210021087',
    'fef7bff7bc04210023188',
    'fef7bff7bc042101c0007',
    'fef7bff7bc042101c2108',
    'fef7bff7bc042101e1080',
    'fef7bff7bc3800000210f',
    'fef7bff7bc38000021087',
    'fef7bff7bc38000023188',
    'fef7bff7bc380001c0007',
    'fef7bff7bc380001c2108',
    'fef7bff7bc380001e1080',
    'fef7bff7bdc0000e00007',
    'fef7bff7bdc0000e02108',
    'fef7bff7bdc0000e21080',
    'fef7bff7bdc0000fc0000',
    'fef7bff7bdc0421000007',
    'fef7bff7bdc0421002108',
    'fef7bff7bdc0421021080',
    'fef7bff7bdc04211c0000',
    'fef7bff7bdc4210000007',
    'fef7bff7bdc4210002108',
    'fef7bff7bdc4210021080',
    'fef7bff7bdc42101c0000',
    'fef7bff7bdf8000000007',
    'fef7bff7bdf8000002108',
    'fef7bff7bdf8000021080',
    'fef7bff7bdf80001c0000',
    'fef7bffffe00000e00007',
    'fef7bffffe00000e02108',
    'fef7bffffe00000e21080',
    'fef7bffffe00000fc0000',
    'fef7bffffe00421000007',
    'fef7bffffe00421002108',
    'fef7bffffe00421021080',
    'fef7bffffe004211c0000',
    'fef7bffffe04210000007',
    'fef7bffffe04210002108',
    'fef7bffffe04210021080',
    'fef7bffffe042101c0000',
    'fef7bffffe38000000007',
    'fef7bffffe38000002108',
    'fef7bffffe38000021080',
    'fef7bffffe380001c0000',
    'fef7bfffffc0000e00000',
    'fef7bfffffc0421000000',
    'fef7bfffffc4210000000',
    'fef7bffffff8000000000',
    'ffffc0739c00000fe318f',
    'ffffc0739c004211e318f',
    'ffffc0739c042101e318f',
    'ffffc0739c380001e318f',
    'ffffc0739dc0000e2318f',
    'ffffc0739dc0000fc210f',
    'ffffc0739dc0000fe1087',
    'ffffc0739dc0000fe3188',
    'ffffc0739dc042102318f',
    'ffffc0739dc04211c210f',
    'ffffc0739dc04211e1087',
    'ffffc0739dc04211e3188',
    'ffffc0739dc421002318f',
    'ffffc0739dc42101c210f',
    'ffffc0739dc42101e1087',
    'ffffc0739dc42101e3188',
    'ffffc0739df800002318f',
    'ffffc0739df80001c210f',
    'ffffc0739df80001e1087',
    'ffffc0739df80001e3188',
    'ffffc07bde00000e2318f',
    'ffffc07bde00000fc210f',
    'ffffc07bde00000fe1087',
    'ffffc07bde00000fe3188',
    'ffffc07bde0042102318f',
    'ffffc07bde004211c210f',
    'ffffc07bde004211e1087',
    'ffffc07bde004211e3188',
    'ffffc07bde0421002318f',
    'ffffc07bde042101c210f',
    'ffffc07bde042101e1087',
    'ffffc07bde042101e3188',
    'ffffc07bde3800002318f',
    'ffffc07bde380001c210f',
    'ffffc07bde380001e1087',
    'ffffc07bde380001e3188',
    'ffffc07bdfc0000e0210f',
    'ffffc07bdfc0000e21087',
    'ffffc07bdfc0000e23188',
    'ffffc07bdfc0000fc0007',
    'ffffc07bdfc0000fc2108',
    'ffffc07bdfc0000fe1080',
    'ffffc07bdfc042100210f',
    'ffffc07bdfc0421021087',
    'ffffc07bdfc0421023188',
    'ffffc07bdfc04211c0007',
    'ffffc07bdfc04211c2108',
    'ffffc07bdfc04211e1080',
    'ffffc07bdfc421000210f',
    'ffffc07bdfc4210021087',
    'ffffc07bdfc4210023188',
    'ffffc07bdfc42101c0007',
    'ffffc07bdfc42101c2108',
    'ffffc07bdfc42101e1080',
    'ffffc07bdff800000210f',
    'ffffc07bdff8000021087',
    'ffffc07bdff8000023188',
    'ffffc07bdff80001c0007',
    'ffffc07bdff80001c2108',
    'ffffc07bdff80001e1080',
    'ffffc0f7bc00000e2318f',
    'ffffc0f7bc00000fc210f',
    'ffffc0f7bc00000fe1087',
    'ffffc0f7bc00000fe3188',
    'ffffc0f7bc0042102318f',
    'ffffc0f7bc004211c210f',
    'ffffc0f7bc004211e1087',
    'ffffc0f7bc004211e3188',
    'ffffc0f7bc0421002318f',
    'ffffc0f7bc042101c210f',
    'ffffc0f7bc042101e1087',
    'ffffc0f7bc042101e3188',
    'ffffc0f7bc3800002318f',
    'ffffc0f7bc380001c210f',
    'ffffc0f7bc380001e1087',
    'ffffc0f7bc380001e3188',
    'ffffc0f7bdc0000e0210f',
    'ffffc0f7bdc0000e21087',
    'ffffc0f7bdc0000e23188',
    'ffffc0f7bdc0000fc0007',
    'ffffc0f7bdc0000fc2108',
    'ffffc0f7bdc0000fe1080',
    'ffffc0f7bdc042100210f',
    'ffffc0f7bdc0421021087',
    'ffffc0f7bdc0421023188',
    'ffffc0f7bdc04211c0007',
    'ffffc0f7bdc04211c2108',
    'ffffc0f7bdc04211e1080',
    'ffffc0f7bdc421000210f',
    'ffffc0f7bdc4210021087',
    'ffffc0f7bdc4210023188',
    'ffffc0f7bdc42101c0007',
    'ffffc0f7bdc42101c2108',
    'ffffc0f7bdc42101e1080',
    'ffffc0f7bdf800000210f',
    'ffffc0f7bdf8000021087',
    'ffffc0f7bdf8000023188',
    'ffffc0f7bdf80001c0007',
    'ffffc0f7bdf80001c2108',
    'ffffc0f7bdf80001e1080',
    'ffffc0fffe00000e0210f',
    'ffffc0fffe00000e21087',
    'ffffc0fffe00000e23188',
    'ffffc0fffe00000fc0007',
    'ffffc0fffe00000fc2108',
    'ffffc0fffe00000fe1080',
    'ffffc0fffe0042100210f',
    'ffffc0fffe00421021087',
    'ffffc0fffe00421023188',
    'ffffc0fffe004211c0007',
    'ffffc0fffe004211c2108',
    'ffffc0fffe004211e1080',
    'ffffc0fffe0421000210f',
    'ffffc0fffe04210021087',
    'ffffc0fffe04210023188',
    'ffffc0fffe042101c0007',
    'ffffc0fffe042101c2108',
    'ffffc0fffe042101e1080',
    'ffffc0fffe3800000210f',
    'ffffc0fffe38000021087',
    'ffffc0fffe38000023188',
    'ffffc0fffe380001c0007',
    'ffffc0fffe380001c2108',
    'ffffc0fffe380001e1080',
    'ffffc0ffffc0000e00007',
    'ffffc0ffffc0000e02108',
    'ffffc0ffffc0000e21080',
    'ffffc0ffffc0000fc0000',
    'ffffc0ffffc0421000007',
    'ffffc0ffffc0421002108',
    'ffffc0ffffc0421021080',
    'ffffc0ffffc04211c0000',
    'ffffc0ffffc4210000007',
    'ffffc0ffffc4210002108',
    'ffffc0ffffc4210021080',
    'ffffc0ffffc42101c0000',
    'ffffc0fffff8000000007',
    'ffffc0fffff8000002108',
    'ffffc0fffff8000021080',
    'ffffc0fffff80001c0000',
    'ffffc7739c00000e2318f',
    'ffffc7739c00000fc210f',
    'ffffc7739c00000fe1087',
    'ffffc7739c00000fe3188',
    'ffffc7739c0042102318f',
    'ffffc7739c004211c210f',
    'ffffc7739c004211e1087',
    'ffffc7739c004211e3188',
    'ffffc7739c0421002318f',
    'ffffc7739c042101c210f',
    'ffffc7739c042101e1087',
    'ffffc7739c042101e3188',
    'ffffc7739c3800002318f',
    'ffffc7739c380001c210f',
    'ffffc7739c380001e1087',
    'ffffc7739c380001e3188',
    'ffffc7739dc0000e0210f',
    'ffffc7739dc0000e21087',
    'ffffc7739dc0000e23188',
    'ffffc7739dc0000fc0007',
    'ffffc7739dc0000fc2108',
    'ffffc7739dc0000fe1080',
    'ffffc7739dc042100210f',
    'ffffc7739dc0421021087',
    'ffffc7739dc0421023188',
    'ffffc7739dc04211c0007',
    'ffffc7739dc04211c2108',
    'ffffc7739dc04211e1080',
    'ffffc7739dc421000210f',
    'ffffc7739dc4210021087',
    'ffffc7739dc4210023188',
    'ffffc7739dc42101c0007',
    'ffffc7739dc42101c2108',
    'ffffc7739dc42101e1080',
    'ffffc7739df800000210f',
    'ffffc7739df8000021087',
    'ffffc7739df8000023188',
    'ffffc7739df80001c0007',
    'ffffc7739df80001c2108',
    'ffffc7739df80001e1080',
    'ffffc77bde00000e0210f',
    'ffffc77bde00000e21087',
    'ffffc77bde00000e23188',
    'ffffc77bde00000fc0007',
    'ffffc77bde00000fc2108',
    'ffffc77bde00000fe1080',
    'ffffc77bde0042100210f',
    'ffffc77bde00421021087',
    'ffffc77bde00421023188',
    'ffffc77bde004211c0007',
    'ffffc77bde004211c2108',
    'ffffc77bde004211e1080',
    'ffffc77bde0421000210f',
    'ffffc77bde04210021087',
    'ffffc77bde04210023188',
    'ffffc77bde042101c0007',
    'ffffc77bde042101c2108',
    'ffffc77bde042101e1080',
    'ffffc77bde3800000210f',
    'ffffc77bde38000021087',
    'ffffc77bde38000023188',
    'ffffc77bde380001c0007',
    'ffffc77bde380001c2108',
    'ffffc77bde380001e1080',
    'ffffc77bdfc0000e00007',
    'ffffc77bdfc0000e02108',
    'ffffc77bdfc0000e21080',
    'ffffc77bdfc0000fc0000',
    'ffffc77bdfc0421000007',
    'ffffc77bdfc0421002108',
    'ffffc77bdfc0421021080',
    'ffffc77bdfc04211c0000',
    'ffffc77bdfc4210000007',
    'ffffc77bdfc4210002108',
    'ffffc77bdfc4210021080',
    'ffffc77bdfc42101c0000',
    'ffffc77bdff8000000007',
    'ffffc77bdff8000002108',
    'ffffc77bdff8000021080',
    'ffffc77bdff80001c0000',
    'ffffc7f7bc00000e0210f',
    'ffffc7f7bc00000e21087',
    'ffffc7f7bc00000e23188',
    'ffffc7f7bc00000fc0007',
    'ffffc7f7bc00000fc2108',
    'ffffc7f7bc00000fe1080',
    'ffffc7f7bc0042100210f',
    'ffffc7f7bc00421021087',
    'ffffc7f7bc00421023188',
    'ffffc7f7bc004211c0007',
    'ffffc7f7bc004211c2108',
    'ffffc7f7bc004211e1080',
    'ffffc7f7bc0421000210f',
    'ffffc7f7bc04210021087',
    'ffffc7f7bc04210023188',
    'ffffc7f7bc042101c0007',
    'ffffc7f7bc042101c2108',
    'ffffc7f7bc042101e1080',
    'ffffc7f7bc3800000210f',
    'ffffc7f7bc38000021087',
    'ffffc7f7bc38000023188',
    'ffffc7f7bc380001c0007',
    'ffffc7f7bc380001c2108',
    'ffffc7f7bc380001e1080',
    'ffffc7f7bdc0000e00007',
    'ffffc7f7bdc0000e02108',
    'ffffc7f7bdc0000e21080',
    'ffffc7f7bdc0000fc0000',
    'ffffc7f7bdc0421000007',
    'ffffc7f7bdc0421002108',
    'ffffc7f7bdc0421021080',
    'ffffc7f7bdc04211c0000',
    'ffffc7f7bdc4210000007',
    'ffffc7f7bdc4210002108',
    'ffffc7f7bdc4210021080',
    'ffffc7f7bdc42101c0000',
    'ffffc7f7bdf8000000007',
    'ffffc7f7bdf8000002108',
    'ffffc7f7bdf8000021080',
    'ffffc7f7bdf80001c0000',
    'ffffc7fffe00000e00007',
    'ffffc7fffe00000e02108',
    'ffffc7fffe00000e21080',
    'ffffc7fffe00000fc0000',
    'ffffc7fffe00421000007',
    'ffffc7fffe00421002108',
    'ffffc7fffe00421021080',
    'ffffc7fffe004211c0000',
    'ffffc7fffe04210000007',
    'ffffc7fffe04210002108',
    'ffffc7fffe04210021080',
    'ffffc7fffe042101c0000',
    'ffffc7fffe38000000007',
    'ffffc7fffe38000002108',
    'ffffc7fffe38000021080',
    'ffffc7fffe380001c0000',
    'ffffc7ffffc0000e00000',
    'ffffc7ffffc0421000000',
    'ffffc7ffffc4210000000',
    'ffffc7fffff8000000000',
    'fffff8739c000001e318f',
    'fffff8739dc000002318f',
    'fffff8739dc00001c210f',
    'fffff8739dc00001e1087',
    'fffff8739dc00001e3188',
    'fffff87bde0000002318f',
    'fffff87bde000001c210f',
    'fffff87bde000001e1087',
    'fffff87bde000001e3188',
    'fffff87bdfc000000210f',
    'fffff87bdfc0000021087',
    'fffff87bdfc0000023188',
    'fffff87bdfc00001c0007',
    'fffff87bdfc00001c2108',
    'fffff87bdfc00001e1080',
    'fffff8f7bc0000002318f',
    'fffff8f7bc000001c210f',
    'fffff8f7bc000001e1087',
    'fffff8f7bc000001e3188',
    'fffff8f7bdc000000210f',
    'fffff8f7bdc0000021087',
    'fffff8f7bdc0000023188',
    'fffff8f7bdc00001c0007',
    'fffff8f7bdc00001c2108',
    'fffff8f7bdc00001e1080',
    'fffff8fffe0000000210f',
    'fffff8fffe00000021087',
    'fffff8fffe00000023188',
    'fffff8fffe000001c0007',
    'fffff8fffe000001c2108',
    'fffff8fffe000001e1080',
    'fffff8ffffc0000000007',
    'fffff8ffffc0000002108',
    'fffff8ffffc0000021080',
    'fffff8ffffc00001c0000',
    'ffffff739c0000002318f',
    'ffffff739c000001c210f',
    'ffffff739c000001e1087',
    'ffffff739c000001e3188',
    'ffffff739dc000000210f',
    'ffffff739dc0000021087',
    'ffffff739dc0000023188',
    'ffffff739dc00001c0007',
    'ffffff739dc00001c2108',
    'ffffff739dc00001e1080',
    'ffffff7bde0000000210f',
    'ffffff7bde00000021087',
    'ffffff7bde00000023188',
    'ffffff7bde000001c0007',
    'ffffff7bde000001c2108',
    'ffffff7bde000001e1080',
    'ffffff7bdfc0000000007',
    'ffffff7bdfc0000002108',
    'ffffff7bdfc0000021080',
    'ffffff7bdfc00001c0000',
    'fffffff7bc0000000210f',
    'fffffff7bc00000021087',
    'fffffff7bc00000023188',
    'fffffff7bc000001c0007',
    'fffffff7bc000001c2108',
    'fffffff7bc000001e1080',
    'fffffff7bdc0000000007',
    'fffffff7bdc0000002108',
    'fffffff7bdc0000021080',
    'fffffff7bdc00001c0000',
    'fffffffffe00000000007',
    'fffffffffe00000002108',
    'fffffffffe00000021080',
    'fffffffffe000001c0000',
    'ffffffffffc0000000000',
)

def rotate_777_U(cube):
    return [cube[0],cube[43],cube[36],cube[29],cube[22],cube[15],cube[8],cube[1],cube[44],cube[37],cube[30],cube[23],cube[16],cube[9],cube[2],cube[45],cube[38],cube[31],cube[24],cube[17],cube[10],cube[3],cube[46],cube[39],cube[32],cube[25],cube[18],cube[11],cube[4],cube[47],cube[40],cube[33],cube[26],cube[19],cube[12],cube[5],cube[48],cube[41],cube[34],cube[27],cube[20],cube[13],cube[6],cube[49],cube[42],cube[35],cube[28],cube[21],cube[14],cube[7]] + cube[99:106] + cube[57:99] + cube[148:155] + cube[106:148] + cube[197:204] + cube[155:197] + cube[50:57] + cube[204:295]

def rotate_777_U_prime(cube):
    return [cube[0],cube[7],cube[14],cube[21],cube[28],cube[35],cube[42],cube[49],cube[6],cube[13],cube[20],cube[27],cube[34],cube[41],cube[48],cube[5],cube[12],cube[19],cube[26],cube[33],cube[40],cube[47],cube[4],cube[11],cube[18],cube[25],cube[32],cube[39],cube[46],cube[3],cube[10],cube[17],cube[24],cube[31],cube[38],cube[45],cube[2],cube[9],cube[16],cube[23],cube[30],cube[37],cube[44],cube[1],cube[8],cube[15],cube[22],cube[29],cube[36],cube[43]] + cube[197:204] + cube[57:99] + cube[50:57] + cube[106:148] + cube[99:106] + cube[155:197] + cube[148:155] + cube[204:295]

def rotate_777_U2(cube):
    return [cube[0],cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]] + cube[148:155] + cube[57:99] + cube[197:204] + cube[106:148] + cube[50:57] + cube[155:197] + cube[99:106] + cube[204:295]

def rotate_777_Uw(cube):
    return [cube[0],cube[43],cube[36],cube[29],cube[22],cube[15],cube[8],cube[1],cube[44],cube[37],cube[30],cube[23],cube[16],cube[9],cube[2],cube[45],cube[38],cube[31],cube[24],cube[17],cube[10],cube[3],cube[46],cube[39],cube[32],cube[25],cube[18],cube[11],cube[4],cube[47],cube[40],cube[33],cube[26],cube[19],cube[12],cube[5],cube[48],cube[41],cube[34],cube[27],cube[20],cube[13],cube[6],cube[49],cube[42],cube[35],cube[28],cube[21],cube[14],cube[7]] + cube[99:113] + cube[64:99] + cube[148:162] + cube[113:148] + cube[197:211] + cube[162:197] + cube[50:64] + cube[211:295]

def rotate_777_Uw_prime(cube):
    return [cube[0],cube[7],cube[14],cube[21],cube[28],cube[35],cube[42],cube[49],cube[6],cube[13],cube[20],cube[27],cube[34],cube[41],cube[48],cube[5],cube[12],cube[19],cube[26],cube[33],cube[40],cube[47],cube[4],cube[11],cube[18],cube[25],cube[32],cube[39],cube[46],cube[3],cube[10],cube[17],cube[24],cube[31],cube[38],cube[45],cube[2],cube[9],cube[16],cube[23],cube[30],cube[37],cube[44],cube[1],cube[8],cube[15],cube[22],cube[29],cube[36],cube[43]] + cube[197:211] + cube[64:99] + cube[50:64] + cube[113:148] + cube[99:113] + cube[162:197] + cube[148:162] + cube[211:295]

def rotate_777_Uw2(cube):
    return [cube[0],cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]] + cube[148:162] + cube[64:99] + cube[197:211] + cube[113:148] + cube[50:64] + cube[162:197] + cube[99:113] + cube[211:295]

def rotate_777_3Uw(cube):
    return [cube[0],cube[43],cube[36],cube[29],cube[22],cube[15],cube[8],cube[1],cube[44],cube[37],cube[30],cube[23],cube[16],cube[9],cube[2],cube[45],cube[38],cube[31],cube[24],cube[17],cube[10],cube[3],cube[46],cube[39],cube[32],cube[25],cube[18],cube[11],cube[4],cube[47],cube[40],cube[33],cube[26],cube[19],cube[12],cube[5],cube[48],cube[41],cube[34],cube[27],cube[20],cube[13],cube[6],cube[49],cube[42],cube[35],cube[28],cube[21],cube[14],cube[7]] + cube[99:120] + cube[71:99] + cube[148:169] + cube[120:148] + cube[197:218] + cube[169:197] + cube[50:71] + cube[218:295]

def rotate_777_3Uw_prime(cube):
    return [cube[0],cube[7],cube[14],cube[21],cube[28],cube[35],cube[42],cube[49],cube[6],cube[13],cube[20],cube[27],cube[34],cube[41],cube[48],cube[5],cube[12],cube[19],cube[26],cube[33],cube[40],cube[47],cube[4],cube[11],cube[18],cube[25],cube[32],cube[39],cube[46],cube[3],cube[10],cube[17],cube[24],cube[31],cube[38],cube[45],cube[2],cube[9],cube[16],cube[23],cube[30],cube[37],cube[44],cube[1],cube[8],cube[15],cube[22],cube[29],cube[36],cube[43]] + cube[197:218] + cube[71:99] + cube[50:71] + cube[120:148] + cube[99:120] + cube[169:197] + cube[148:169] + cube[218:295]

def rotate_777_3Uw2(cube):
    return [cube[0],cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]] + cube[148:169] + cube[71:99] + cube[197:218] + cube[120:148] + cube[50:71] + cube[169:197] + cube[99:120] + cube[218:295]

def rotate_777_L(cube):
    return [cube[0],cube[245]] + cube[2:8] + [cube[238]] + cube[9:15] + [cube[231]] + cube[16:22] + [cube[224]] + cube[23:29] + [cube[217]] + cube[30:36] + [cube[210]] + cube[37:43] + [cube[203]] + cube[44:50] + [cube[92],cube[85],cube[78],cube[71],cube[64],cube[57],cube[50],cube[93],cube[86],cube[79],cube[72],cube[65],cube[58],cube[51],cube[94],cube[87],cube[80],cube[73],cube[66],cube[59],cube[52],cube[95],cube[88],cube[81],cube[74],cube[67],cube[60],cube[53],cube[96],cube[89],cube[82],cube[75],cube[68],cube[61],cube[54],cube[97],cube[90],cube[83],cube[76],cube[69],cube[62],cube[55],cube[98],cube[91],cube[84],cube[77],cube[70],cube[63],cube[56],cube[1]] + cube[100:106] + [cube[8]] + cube[107:113] + [cube[15]] + cube[114:120] + [cube[22]] + cube[121:127] + [cube[29]] + cube[128:134] + [cube[36]] + cube[135:141] + [cube[43]] + cube[142:203] + [cube[288]] + cube[204:210] + [cube[281]] + cube[211:217] + [cube[274]] + cube[218:224] + [cube[267]] + cube[225:231] + [cube[260]] + cube[232:238] + [cube[253]] + cube[239:245] + [cube[246],cube[99]] + cube[247:253] + [cube[106]] + cube[254:260] + [cube[113]] + cube[261:267] + [cube[120]] + cube[268:274] + [cube[127]] + cube[275:281] + [cube[134]] + cube[282:288] + [cube[141]] + cube[289:295]

def rotate_777_L_prime(cube):
    return [cube[0],cube[99]] + cube[2:8] + [cube[106]] + cube[9:15] + [cube[113]] + cube[16:22] + [cube[120]] + cube[23:29] + [cube[127]] + cube[30:36] + [cube[134]] + cube[37:43] + [cube[141]] + cube[44:50] + [cube[56],cube[63],cube[70],cube[77],cube[84],cube[91],cube[98],cube[55],cube[62],cube[69],cube[76],cube[83],cube[90],cube[97],cube[54],cube[61],cube[68],cube[75],cube[82],cube[89],cube[96],cube[53],cube[60],cube[67],cube[74],cube[81],cube[88],cube[95],cube[52],cube[59],cube[66],cube[73],cube[80],cube[87],cube[94],cube[51],cube[58],cube[65],cube[72],cube[79],cube[86],cube[93],cube[50],cube[57],cube[64],cube[71],cube[78],cube[85],cube[92],cube[246]] + cube[100:106] + [cube[253]] + cube[107:113] + [cube[260]] + cube[114:120] + [cube[267]] + cube[121:127] + [cube[274]] + cube[128:134] + [cube[281]] + cube[135:141] + [cube[288]] + cube[142:203] + [cube[43]] + cube[204:210] + [cube[36]] + cube[211:217] + [cube[29]] + cube[218:224] + [cube[22]] + cube[225:231] + [cube[15]] + cube[232:238] + [cube[8]] + cube[239:245] + [cube[1],cube[245]] + cube[247:253] + [cube[238]] + cube[254:260] + [cube[231]] + cube[261:267] + [cube[224]] + cube[268:274] + [cube[217]] + cube[275:281] + [cube[210]] + cube[282:288] + [cube[203]] + cube[289:295]

def rotate_777_L2(cube):
    return [cube[0],cube[246]] + cube[2:8] + [cube[253]] + cube[9:15] + [cube[260]] + cube[16:22] + [cube[267]] + cube[23:29] + [cube[274]] + cube[30:36] + [cube[281]] + cube[37:43] + [cube[288]] + cube[44:50] + [cube[98],cube[97],cube[96],cube[95],cube[94],cube[93],cube[92],cube[91],cube[90],cube[89],cube[88],cube[87],cube[86],cube[85],cube[84],cube[83],cube[82],cube[81],cube[80],cube[79],cube[78],cube[77],cube[76],cube[75],cube[74],cube[73],cube[72],cube[71],cube[70],cube[69],cube[68],cube[67],cube[66],cube[65],cube[64],cube[63],cube[62],cube[61],cube[60],cube[59],cube[58],cube[57],cube[56],cube[55],cube[54],cube[53],cube[52],cube[51],cube[50],cube[245]] + cube[100:106] + [cube[238]] + cube[107:113] + [cube[231]] + cube[114:120] + [cube[224]] + cube[121:127] + [cube[217]] + cube[128:134] + [cube[210]] + cube[135:141] + [cube[203]] + cube[142:203] + [cube[141]] + cube[204:210] + [cube[134]] + cube[211:217] + [cube[127]] + cube[218:224] + [cube[120]] + cube[225:231] + [cube[113]] + cube[232:238] + [cube[106]] + cube[239:245] + [cube[99],cube[1]] + cube[247:253] + [cube[8]] + cube[254:260] + [cube[15]] + cube[261:267] + [cube[22]] + cube[268:274] + [cube[29]] + cube[275:281] + [cube[36]] + cube[282:288] + [cube[43]] + cube[289:295]

def rotate_777_Lw(cube):
    return [cube[0],cube[245],cube[244]] + cube[3:8] + [cube[238],cube[237]] + cube[10:15] + [cube[231],cube[230]] + cube[17:22] + [cube[224],cube[223]] + cube[24:29] + [cube[217],cube[216]] + cube[31:36] + [cube[210],cube[209]] + cube[38:43] + [cube[203],cube[202]] + cube[45:50] + [cube[92],cube[85],cube[78],cube[71],cube[64],cube[57],cube[50],cube[93],cube[86],cube[79],cube[72],cube[65],cube[58],cube[51],cube[94],cube[87],cube[80],cube[73],cube[66],cube[59],cube[52],cube[95],cube[88],cube[81],cube[74],cube[67],cube[60],cube[53],cube[96],cube[89],cube[82],cube[75],cube[68],cube[61],cube[54],cube[97],cube[90],cube[83],cube[76],cube[69],cube[62],cube[55],cube[98],cube[91],cube[84],cube[77],cube[70],cube[63],cube[56]] + cube[1:3] + cube[101:106] + cube[8:10] + cube[108:113] + cube[15:17] + cube[115:120] + cube[22:24] + cube[122:127] + cube[29:31] + cube[129:134] + cube[36:38] + cube[136:141] + cube[43:45] + cube[143:202] + [cube[289],cube[288]] + cube[204:209] + [cube[282],cube[281]] + cube[211:216] + [cube[275],cube[274]] + cube[218:223] + [cube[268],cube[267]] + cube[225:230] + [cube[261],cube[260]] + cube[232:237] + [cube[254],cube[253]] + cube[239:244] + [cube[247],cube[246]] + cube[99:101] + cube[248:253] + cube[106:108] + cube[255:260] + cube[113:115] + cube[262:267] + cube[120:122] + cube[269:274] + cube[127:129] + cube[276:281] + cube[134:136] + cube[283:288] + cube[141:143] + cube[290:295]

def rotate_777_Lw_prime(cube):
    return [cube[0]] + cube[99:101] + cube[3:8] + cube[106:108] + cube[10:15] + cube[113:115] + cube[17:22] + cube[120:122] + cube[24:29] + cube[127:129] + cube[31:36] + cube[134:136] + cube[38:43] + cube[141:143] + cube[45:50] + [cube[56],cube[63],cube[70],cube[77],cube[84],cube[91],cube[98],cube[55],cube[62],cube[69],cube[76],cube[83],cube[90],cube[97],cube[54],cube[61],cube[68],cube[75],cube[82],cube[89],cube[96],cube[53],cube[60],cube[67],cube[74],cube[81],cube[88],cube[95],cube[52],cube[59],cube[66],cube[73],cube[80],cube[87],cube[94],cube[51],cube[58],cube[65],cube[72],cube[79],cube[86],cube[93],cube[50],cube[57],cube[64],cube[71],cube[78],cube[85],cube[92]] + cube[246:248] + cube[101:106] + cube[253:255] + cube[108:113] + cube[260:262] + cube[115:120] + cube[267:269] + cube[122:127] + cube[274:276] + cube[129:134] + cube[281:283] + cube[136:141] + cube[288:290] + cube[143:202] + [cube[44],cube[43]] + cube[204:209] + [cube[37],cube[36]] + cube[211:216] + [cube[30],cube[29]] + cube[218:223] + [cube[23],cube[22]] + cube[225:230] + [cube[16],cube[15]] + cube[232:237] + [cube[9],cube[8]] + cube[239:244] + [cube[2],cube[1],cube[245],cube[244]] + cube[248:253] + [cube[238],cube[237]] + cube[255:260] + [cube[231],cube[230]] + cube[262:267] + [cube[224],cube[223]] + cube[269:274] + [cube[217],cube[216]] + cube[276:281] + [cube[210],cube[209]] + cube[283:288] + [cube[203],cube[202]] + cube[290:295]

def rotate_777_Lw2(cube):
    return [cube[0]] + cube[246:248] + cube[3:8] + cube[253:255] + cube[10:15] + cube[260:262] + cube[17:22] + cube[267:269] + cube[24:29] + cube[274:276] + cube[31:36] + cube[281:283] + cube[38:43] + cube[288:290] + cube[45:50] + [cube[98],cube[97],cube[96],cube[95],cube[94],cube[93],cube[92],cube[91],cube[90],cube[89],cube[88],cube[87],cube[86],cube[85],cube[84],cube[83],cube[82],cube[81],cube[80],cube[79],cube[78],cube[77],cube[76],cube[75],cube[74],cube[73],cube[72],cube[71],cube[70],cube[69],cube[68],cube[67],cube[66],cube[65],cube[64],cube[63],cube[62],cube[61],cube[60],cube[59],cube[58],cube[57],cube[56],cube[55],cube[54],cube[53],cube[52],cube[51],cube[50],cube[245],cube[244]] + cube[101:106] + [cube[238],cube[237]] + cube[108:113] + [cube[231],cube[230]] + cube[115:120] + [cube[224],cube[223]] + cube[122:127] + [cube[217],cube[216]] + cube[129:134] + [cube[210],cube[209]] + cube[136:141] + [cube[203],cube[202]] + cube[143:202] + [cube[142],cube[141]] + cube[204:209] + [cube[135],cube[134]] + cube[211:216] + [cube[128],cube[127]] + cube[218:223] + [cube[121],cube[120]] + cube[225:230] + [cube[114],cube[113]] + cube[232:237] + [cube[107],cube[106]] + cube[239:244] + [cube[100],cube[99]] + cube[1:3] + cube[248:253] + cube[8:10] + cube[255:260] + cube[15:17] + cube[262:267] + cube[22:24] + cube[269:274] + cube[29:31] + cube[276:281] + cube[36:38] + cube[283:288] + cube[43:45] + cube[290:295]

def rotate_777_3Lw(cube):
    return [cube[0],cube[245],cube[244],cube[243]] + cube[4:8] + [cube[238],cube[237],cube[236]] + cube[11:15] + [cube[231],cube[230],cube[229]] + cube[18:22] + [cube[224],cube[223],cube[222]] + cube[25:29] + [cube[217],cube[216],cube[215]] + cube[32:36] + [cube[210],cube[209],cube[208]] + cube[39:43] + [cube[203],cube[202],cube[201]] + cube[46:50] + [cube[92],cube[85],cube[78],cube[71],cube[64],cube[57],cube[50],cube[93],cube[86],cube[79],cube[72],cube[65],cube[58],cube[51],cube[94],cube[87],cube[80],cube[73],cube[66],cube[59],cube[52],cube[95],cube[88],cube[81],cube[74],cube[67],cube[60],cube[53],cube[96],cube[89],cube[82],cube[75],cube[68],cube[61],cube[54],cube[97],cube[90],cube[83],cube[76],cube[69],cube[62],cube[55],cube[98],cube[91],cube[84],cube[77],cube[70],cube[63],cube[56]] + cube[1:4] + cube[102:106] + cube[8:11] + cube[109:113] + cube[15:18] + cube[116:120] + cube[22:25] + cube[123:127] + cube[29:32] + cube[130:134] + cube[36:39] + cube[137:141] + cube[43:46] + cube[144:201] + [cube[290],cube[289],cube[288]] + cube[204:208] + [cube[283],cube[282],cube[281]] + cube[211:215] + [cube[276],cube[275],cube[274]] + cube[218:222] + [cube[269],cube[268],cube[267]] + cube[225:229] + [cube[262],cube[261],cube[260]] + cube[232:236] + [cube[255],cube[254],cube[253]] + cube[239:243] + [cube[248],cube[247],cube[246]] + cube[99:102] + cube[249:253] + cube[106:109] + cube[256:260] + cube[113:116] + cube[263:267] + cube[120:123] + cube[270:274] + cube[127:130] + cube[277:281] + cube[134:137] + cube[284:288] + cube[141:144] + cube[291:295]

def rotate_777_3Lw_prime(cube):
    return [cube[0]] + cube[99:102] + cube[4:8] + cube[106:109] + cube[11:15] + cube[113:116] + cube[18:22] + cube[120:123] + cube[25:29] + cube[127:130] + cube[32:36] + cube[134:137] + cube[39:43] + cube[141:144] + cube[46:50] + [cube[56],cube[63],cube[70],cube[77],cube[84],cube[91],cube[98],cube[55],cube[62],cube[69],cube[76],cube[83],cube[90],cube[97],cube[54],cube[61],cube[68],cube[75],cube[82],cube[89],cube[96],cube[53],cube[60],cube[67],cube[74],cube[81],cube[88],cube[95],cube[52],cube[59],cube[66],cube[73],cube[80],cube[87],cube[94],cube[51],cube[58],cube[65],cube[72],cube[79],cube[86],cube[93],cube[50],cube[57],cube[64],cube[71],cube[78],cube[85],cube[92]] + cube[246:249] + cube[102:106] + cube[253:256] + cube[109:113] + cube[260:263] + cube[116:120] + cube[267:270] + cube[123:127] + cube[274:277] + cube[130:134] + cube[281:284] + cube[137:141] + cube[288:291] + cube[144:201] + [cube[45],cube[44],cube[43]] + cube[204:208] + [cube[38],cube[37],cube[36]] + cube[211:215] + [cube[31],cube[30],cube[29]] + cube[218:222] + [cube[24],cube[23],cube[22]] + cube[225:229] + [cube[17],cube[16],cube[15]] + cube[232:236] + [cube[10],cube[9],cube[8]] + cube[239:243] + [cube[3],cube[2],cube[1],cube[245],cube[244],cube[243]] + cube[249:253] + [cube[238],cube[237],cube[236]] + cube[256:260] + [cube[231],cube[230],cube[229]] + cube[263:267] + [cube[224],cube[223],cube[222]] + cube[270:274] + [cube[217],cube[216],cube[215]] + cube[277:281] + [cube[210],cube[209],cube[208]] + cube[284:288] + [cube[203],cube[202],cube[201]] + cube[291:295]

def rotate_777_3Lw2(cube):
    return [cube[0]] + cube[246:249] + cube[4:8] + cube[253:256] + cube[11:15] + cube[260:263] + cube[18:22] + cube[267:270] + cube[25:29] + cube[274:277] + cube[32:36] + cube[281:284] + cube[39:43] + cube[288:291] + cube[46:50] + [cube[98],cube[97],cube[96],cube[95],cube[94],cube[93],cube[92],cube[91],cube[90],cube[89],cube[88],cube[87],cube[86],cube[85],cube[84],cube[83],cube[82],cube[81],cube[80],cube[79],cube[78],cube[77],cube[76],cube[75],cube[74],cube[73],cube[72],cube[71],cube[70],cube[69],cube[68],cube[67],cube[66],cube[65],cube[64],cube[63],cube[62],cube[61],cube[60],cube[59],cube[58],cube[57],cube[56],cube[55],cube[54],cube[53],cube[52],cube[51],cube[50],cube[245],cube[244],cube[243]] + cube[102:106] + [cube[238],cube[237],cube[236]] + cube[109:113] + [cube[231],cube[230],cube[229]] + cube[116:120] + [cube[224],cube[223],cube[222]] + cube[123:127] + [cube[217],cube[216],cube[215]] + cube[130:134] + [cube[210],cube[209],cube[208]] + cube[137:141] + [cube[203],cube[202],cube[201]] + cube[144:201] + [cube[143],cube[142],cube[141]] + cube[204:208] + [cube[136],cube[135],cube[134]] + cube[211:215] + [cube[129],cube[128],cube[127]] + cube[218:222] + [cube[122],cube[121],cube[120]] + cube[225:229] + [cube[115],cube[114],cube[113]] + cube[232:236] + [cube[108],cube[107],cube[106]] + cube[239:243] + [cube[101],cube[100],cube[99]] + cube[1:4] + cube[249:253] + cube[8:11] + cube[256:260] + cube[15:18] + cube[263:267] + cube[22:25] + cube[270:274] + cube[29:32] + cube[277:281] + cube[36:39] + cube[284:288] + cube[43:46] + cube[291:295]

def rotate_777_F(cube):
    return cube[0:43] + [cube[98],cube[91],cube[84],cube[77],cube[70],cube[63],cube[56]] + cube[50:56] + [cube[246]] + cube[57:63] + [cube[247]] + cube[64:70] + [cube[248]] + cube[71:77] + [cube[249]] + cube[78:84] + [cube[250]] + cube[85:91] + [cube[251]] + cube[92:98] + [cube[252],cube[141],cube[134],cube[127],cube[120],cube[113],cube[106],cube[99],cube[142],cube[135],cube[128],cube[121],cube[114],cube[107],cube[100],cube[143],cube[136],cube[129],cube[122],cube[115],cube[108],cube[101],cube[144],cube[137],cube[130],cube[123],cube[116],cube[109],cube[102],cube[145],cube[138],cube[131],cube[124],cube[117],cube[110],cube[103],cube[146],cube[139],cube[132],cube[125],cube[118],cube[111],cube[104],cube[147],cube[140],cube[133],cube[126],cube[119],cube[112],cube[105],cube[43]] + cube[149:155] + [cube[44]] + cube[156:162] + [cube[45]] + cube[163:169] + [cube[46]] + cube[170:176] + [cube[47]] + cube[177:183] + [cube[48]] + cube[184:190] + [cube[49]] + cube[191:246] + [cube[190],cube[183],cube[176],cube[169],cube[162],cube[155],cube[148]] + cube[253:295]

def rotate_777_F_prime(cube):
    return cube[0:43] + [cube[148],cube[155],cube[162],cube[169],cube[176],cube[183],cube[190]] + cube[50:56] + [cube[49]] + cube[57:63] + [cube[48]] + cube[64:70] + [cube[47]] + cube[71:77] + [cube[46]] + cube[78:84] + [cube[45]] + cube[85:91] + [cube[44]] + cube[92:98] + [cube[43],cube[105],cube[112],cube[119],cube[126],cube[133],cube[140],cube[147],cube[104],cube[111],cube[118],cube[125],cube[132],cube[139],cube[146],cube[103],cube[110],cube[117],cube[124],cube[131],cube[138],cube[145],cube[102],cube[109],cube[116],cube[123],cube[130],cube[137],cube[144],cube[101],cube[108],cube[115],cube[122],cube[129],cube[136],cube[143],cube[100],cube[107],cube[114],cube[121],cube[128],cube[135],cube[142],cube[99],cube[106],cube[113],cube[120],cube[127],cube[134],cube[141],cube[252]] + cube[149:155] + [cube[251]] + cube[156:162] + [cube[250]] + cube[163:169] + [cube[249]] + cube[170:176] + [cube[248]] + cube[177:183] + [cube[247]] + cube[184:190] + [cube[246]] + cube[191:246] + [cube[56],cube[63],cube[70],cube[77],cube[84],cube[91],cube[98]] + cube[253:295]

def rotate_777_F2(cube):
    return cube[0:43] + [cube[252],cube[251],cube[250],cube[249],cube[248],cube[247],cube[246]] + cube[50:56] + [cube[190]] + cube[57:63] + [cube[183]] + cube[64:70] + [cube[176]] + cube[71:77] + [cube[169]] + cube[78:84] + [cube[162]] + cube[85:91] + [cube[155]] + cube[92:98] + [cube[148],cube[147],cube[146],cube[145],cube[144],cube[143],cube[142],cube[141],cube[140],cube[139],cube[138],cube[137],cube[136],cube[135],cube[134],cube[133],cube[132],cube[131],cube[130],cube[129],cube[128],cube[127],cube[126],cube[125],cube[124],cube[123],cube[122],cube[121],cube[120],cube[119],cube[118],cube[117],cube[116],cube[115],cube[114],cube[113],cube[112],cube[111],cube[110],cube[109],cube[108],cube[107],cube[106],cube[105],cube[104],cube[103],cube[102],cube[101],cube[100],cube[99],cube[98]] + cube[149:155] + [cube[91]] + cube[156:162] + [cube[84]] + cube[163:169] + [cube[77]] + cube[170:176] + [cube[70]] + cube[177:183] + [cube[63]] + cube[184:190] + [cube[56]] + cube[191:246] + [cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43]] + cube[253:295]

def rotate_777_Fw(cube):
    return cube[0:36] + [cube[97],cube[90],cube[83],cube[76],cube[69],cube[62],cube[55],cube[98],cube[91],cube[84],cube[77],cube[70],cube[63],cube[56]] + cube[50:55] + [cube[253],cube[246]] + cube[57:62] + [cube[254],cube[247]] + cube[64:69] + [cube[255],cube[248]] + cube[71:76] + [cube[256],cube[249]] + cube[78:83] + [cube[257],cube[250]] + cube[85:90] + [cube[258],cube[251]] + cube[92:97] + [cube[259],cube[252],cube[141],cube[134],cube[127],cube[120],cube[113],cube[106],cube[99],cube[142],cube[135],cube[128],cube[121],cube[114],cube[107],cube[100],cube[143],cube[136],cube[129],cube[122],cube[115],cube[108],cube[101],cube[144],cube[137],cube[130],cube[123],cube[116],cube[109],cube[102],cube[145],cube[138],cube[131],cube[124],cube[117],cube[110],cube[103],cube[146],cube[139],cube[132],cube[125],cube[118],cube[111],cube[104],cube[147],cube[140],cube[133],cube[126],cube[119],cube[112],cube[105],cube[43],cube[36]] + cube[150:155] + [cube[44],cube[37]] + cube[157:162] + [cube[45],cube[38]] + cube[164:169] + [cube[46],cube[39]] + cube[171:176] + [cube[47],cube[40]] + cube[178:183] + [cube[48],cube[41]] + cube[185:190] + [cube[49],cube[42]] + cube[192:246] + [cube[190],cube[183],cube[176],cube[169],cube[162],cube[155],cube[148],cube[191],cube[184],cube[177],cube[170],cube[163],cube[156],cube[149]] + cube[260:295]

def rotate_777_Fw_prime(cube):
    return cube[0:36] + [cube[149],cube[156],cube[163],cube[170],cube[177],cube[184],cube[191],cube[148],cube[155],cube[162],cube[169],cube[176],cube[183],cube[190]] + cube[50:55] + [cube[42],cube[49]] + cube[57:62] + [cube[41],cube[48]] + cube[64:69] + [cube[40],cube[47]] + cube[71:76] + [cube[39],cube[46]] + cube[78:83] + [cube[38],cube[45]] + cube[85:90] + [cube[37],cube[44]] + cube[92:97] + [cube[36],cube[43],cube[105],cube[112],cube[119],cube[126],cube[133],cube[140],cube[147],cube[104],cube[111],cube[118],cube[125],cube[132],cube[139],cube[146],cube[103],cube[110],cube[117],cube[124],cube[131],cube[138],cube[145],cube[102],cube[109],cube[116],cube[123],cube[130],cube[137],cube[144],cube[101],cube[108],cube[115],cube[122],cube[129],cube[136],cube[143],cube[100],cube[107],cube[114],cube[121],cube[128],cube[135],cube[142],cube[99],cube[106],cube[113],cube[120],cube[127],cube[134],cube[141],cube[252],cube[259]] + cube[150:155] + [cube[251],cube[258]] + cube[157:162] + [cube[250],cube[257]] + cube[164:169] + [cube[249],cube[256]] + cube[171:176] + [cube[248],cube[255]] + cube[178:183] + [cube[247],cube[254]] + cube[185:190] + [cube[246],cube[253]] + cube[192:246] + [cube[56],cube[63],cube[70],cube[77],cube[84],cube[91],cube[98],cube[55],cube[62],cube[69],cube[76],cube[83],cube[90],cube[97]] + cube[260:295]

def rotate_777_Fw2(cube):
    return cube[0:36] + [cube[259],cube[258],cube[257],cube[256],cube[255],cube[254],cube[253],cube[252],cube[251],cube[250],cube[249],cube[248],cube[247],cube[246]] + cube[50:55] + [cube[191],cube[190]] + cube[57:62] + [cube[184],cube[183]] + cube[64:69] + [cube[177],cube[176]] + cube[71:76] + [cube[170],cube[169]] + cube[78:83] + [cube[163],cube[162]] + cube[85:90] + [cube[156],cube[155]] + cube[92:97] + [cube[149],cube[148],cube[147],cube[146],cube[145],cube[144],cube[143],cube[142],cube[141],cube[140],cube[139],cube[138],cube[137],cube[136],cube[135],cube[134],cube[133],cube[132],cube[131],cube[130],cube[129],cube[128],cube[127],cube[126],cube[125],cube[124],cube[123],cube[122],cube[121],cube[120],cube[119],cube[118],cube[117],cube[116],cube[115],cube[114],cube[113],cube[112],cube[111],cube[110],cube[109],cube[108],cube[107],cube[106],cube[105],cube[104],cube[103],cube[102],cube[101],cube[100],cube[99],cube[98],cube[97]] + cube[150:155] + [cube[91],cube[90]] + cube[157:162] + [cube[84],cube[83]] + cube[164:169] + [cube[77],cube[76]] + cube[171:176] + [cube[70],cube[69]] + cube[178:183] + [cube[63],cube[62]] + cube[185:190] + [cube[56],cube[55]] + cube[192:246] + [cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[36]] + cube[260:295]

def rotate_777_3Fw(cube):
    return cube[0:29] + [cube[96],cube[89],cube[82],cube[75],cube[68],cube[61],cube[54],cube[97],cube[90],cube[83],cube[76],cube[69],cube[62],cube[55],cube[98],cube[91],cube[84],cube[77],cube[70],cube[63],cube[56]] + cube[50:54] + [cube[260],cube[253],cube[246]] + cube[57:61] + [cube[261],cube[254],cube[247]] + cube[64:68] + [cube[262],cube[255],cube[248]] + cube[71:75] + [cube[263],cube[256],cube[249]] + cube[78:82] + [cube[264],cube[257],cube[250]] + cube[85:89] + [cube[265],cube[258],cube[251]] + cube[92:96] + [cube[266],cube[259],cube[252],cube[141],cube[134],cube[127],cube[120],cube[113],cube[106],cube[99],cube[142],cube[135],cube[128],cube[121],cube[114],cube[107],cube[100],cube[143],cube[136],cube[129],cube[122],cube[115],cube[108],cube[101],cube[144],cube[137],cube[130],cube[123],cube[116],cube[109],cube[102],cube[145],cube[138],cube[131],cube[124],cube[117],cube[110],cube[103],cube[146],cube[139],cube[132],cube[125],cube[118],cube[111],cube[104],cube[147],cube[140],cube[133],cube[126],cube[119],cube[112],cube[105],cube[43],cube[36],cube[29]] + cube[151:155] + [cube[44],cube[37],cube[30]] + cube[158:162] + [cube[45],cube[38],cube[31]] + cube[165:169] + [cube[46],cube[39],cube[32]] + cube[172:176] + [cube[47],cube[40],cube[33]] + cube[179:183] + [cube[48],cube[41],cube[34]] + cube[186:190] + [cube[49],cube[42],cube[35]] + cube[193:246] + [cube[190],cube[183],cube[176],cube[169],cube[162],cube[155],cube[148],cube[191],cube[184],cube[177],cube[170],cube[163],cube[156],cube[149],cube[192],cube[185],cube[178],cube[171],cube[164],cube[157],cube[150]] + cube[267:295]

def rotate_777_3Fw_prime(cube):
    return cube[0:29] + [cube[150],cube[157],cube[164],cube[171],cube[178],cube[185],cube[192],cube[149],cube[156],cube[163],cube[170],cube[177],cube[184],cube[191],cube[148],cube[155],cube[162],cube[169],cube[176],cube[183],cube[190]] + cube[50:54] + [cube[35],cube[42],cube[49]] + cube[57:61] + [cube[34],cube[41],cube[48]] + cube[64:68] + [cube[33],cube[40],cube[47]] + cube[71:75] + [cube[32],cube[39],cube[46]] + cube[78:82] + [cube[31],cube[38],cube[45]] + cube[85:89] + [cube[30],cube[37],cube[44]] + cube[92:96] + [cube[29],cube[36],cube[43],cube[105],cube[112],cube[119],cube[126],cube[133],cube[140],cube[147],cube[104],cube[111],cube[118],cube[125],cube[132],cube[139],cube[146],cube[103],cube[110],cube[117],cube[124],cube[131],cube[138],cube[145],cube[102],cube[109],cube[116],cube[123],cube[130],cube[137],cube[144],cube[101],cube[108],cube[115],cube[122],cube[129],cube[136],cube[143],cube[100],cube[107],cube[114],cube[121],cube[128],cube[135],cube[142],cube[99],cube[106],cube[113],cube[120],cube[127],cube[134],cube[141],cube[252],cube[259],cube[266]] + cube[151:155] + [cube[251],cube[258],cube[265]] + cube[158:162] + [cube[250],cube[257],cube[264]] + cube[165:169] + [cube[249],cube[256],cube[263]] + cube[172:176] + [cube[248],cube[255],cube[262]] + cube[179:183] + [cube[247],cube[254],cube[261]] + cube[186:190] + [cube[246],cube[253],cube[260]] + cube[193:246] + [cube[56],cube[63],cube[70],cube[77],cube[84],cube[91],cube[98],cube[55],cube[62],cube[69],cube[76],cube[83],cube[90],cube[97],cube[54],cube[61],cube[68],cube[75],cube[82],cube[89],cube[96]] + cube[267:295]

def rotate_777_3Fw2(cube):
    return cube[0:29] + [cube[266],cube[265],cube[264],cube[263],cube[262],cube[261],cube[260],cube[259],cube[258],cube[257],cube[256],cube[255],cube[254],cube[253],cube[252],cube[251],cube[250],cube[249],cube[248],cube[247],cube[246]] + cube[50:54] + [cube[192],cube[191],cube[190]] + cube[57:61] + [cube[185],cube[184],cube[183]] + cube[64:68] + [cube[178],cube[177],cube[176]] + cube[71:75] + [cube[171],cube[170],cube[169]] + cube[78:82] + [cube[164],cube[163],cube[162]] + cube[85:89] + [cube[157],cube[156],cube[155]] + cube[92:96] + [cube[150],cube[149],cube[148],cube[147],cube[146],cube[145],cube[144],cube[143],cube[142],cube[141],cube[140],cube[139],cube[138],cube[137],cube[136],cube[135],cube[134],cube[133],cube[132],cube[131],cube[130],cube[129],cube[128],cube[127],cube[126],cube[125],cube[124],cube[123],cube[122],cube[121],cube[120],cube[119],cube[118],cube[117],cube[116],cube[115],cube[114],cube[113],cube[112],cube[111],cube[110],cube[109],cube[108],cube[107],cube[106],cube[105],cube[104],cube[103],cube[102],cube[101],cube[100],cube[99],cube[98],cube[97],cube[96]] + cube[151:155] + [cube[91],cube[90],cube[89]] + cube[158:162] + [cube[84],cube[83],cube[82]] + cube[165:169] + [cube[77],cube[76],cube[75]] + cube[172:176] + [cube[70],cube[69],cube[68]] + cube[179:183] + [cube[63],cube[62],cube[61]] + cube[186:190] + [cube[56],cube[55],cube[54]] + cube[193:246] + [cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29]] + cube[267:295]

def rotate_777_R(cube):
    return cube[0:7] + [cube[105]] + cube[8:14] + [cube[112]] + cube[15:21] + [cube[119]] + cube[22:28] + [cube[126]] + cube[29:35] + [cube[133]] + cube[36:42] + [cube[140]] + cube[43:49] + [cube[147]] + cube[50:105] + [cube[252]] + cube[106:112] + [cube[259]] + cube[113:119] + [cube[266]] + cube[120:126] + [cube[273]] + cube[127:133] + [cube[280]] + cube[134:140] + [cube[287]] + cube[141:147] + [cube[294],cube[190],cube[183],cube[176],cube[169],cube[162],cube[155],cube[148],cube[191],cube[184],cube[177],cube[170],cube[163],cube[156],cube[149],cube[192],cube[185],cube[178],cube[171],cube[164],cube[157],cube[150],cube[193],cube[186],cube[179],cube[172],cube[165],cube[158],cube[151],cube[194],cube[187],cube[180],cube[173],cube[166],cube[159],cube[152],cube[195],cube[188],cube[181],cube[174],cube[167],cube[160],cube[153],cube[196],cube[189],cube[182],cube[175],cube[168],cube[161],cube[154],cube[49]] + cube[198:204] + [cube[42]] + cube[205:211] + [cube[35]] + cube[212:218] + [cube[28]] + cube[219:225] + [cube[21]] + cube[226:232] + [cube[14]] + cube[233:239] + [cube[7]] + cube[240:252] + [cube[239]] + cube[253:259] + [cube[232]] + cube[260:266] + [cube[225]] + cube[267:273] + [cube[218]] + cube[274:280] + [cube[211]] + cube[281:287] + [cube[204]] + cube[288:294] + [cube[197]]

def rotate_777_R_prime(cube):
    return cube[0:7] + [cube[239]] + cube[8:14] + [cube[232]] + cube[15:21] + [cube[225]] + cube[22:28] + [cube[218]] + cube[29:35] + [cube[211]] + cube[36:42] + [cube[204]] + cube[43:49] + [cube[197]] + cube[50:105] + [cube[7]] + cube[106:112] + [cube[14]] + cube[113:119] + [cube[21]] + cube[120:126] + [cube[28]] + cube[127:133] + [cube[35]] + cube[134:140] + [cube[42]] + cube[141:147] + [cube[49],cube[154],cube[161],cube[168],cube[175],cube[182],cube[189],cube[196],cube[153],cube[160],cube[167],cube[174],cube[181],cube[188],cube[195],cube[152],cube[159],cube[166],cube[173],cube[180],cube[187],cube[194],cube[151],cube[158],cube[165],cube[172],cube[179],cube[186],cube[193],cube[150],cube[157],cube[164],cube[171],cube[178],cube[185],cube[192],cube[149],cube[156],cube[163],cube[170],cube[177],cube[184],cube[191],cube[148],cube[155],cube[162],cube[169],cube[176],cube[183],cube[190],cube[294]] + cube[198:204] + [cube[287]] + cube[205:211] + [cube[280]] + cube[212:218] + [cube[273]] + cube[219:225] + [cube[266]] + cube[226:232] + [cube[259]] + cube[233:239] + [cube[252]] + cube[240:252] + [cube[105]] + cube[253:259] + [cube[112]] + cube[260:266] + [cube[119]] + cube[267:273] + [cube[126]] + cube[274:280] + [cube[133]] + cube[281:287] + [cube[140]] + cube[288:294] + [cube[147]]

def rotate_777_R2(cube):
    return cube[0:7] + [cube[252]] + cube[8:14] + [cube[259]] + cube[15:21] + [cube[266]] + cube[22:28] + [cube[273]] + cube[29:35] + [cube[280]] + cube[36:42] + [cube[287]] + cube[43:49] + [cube[294]] + cube[50:105] + [cube[239]] + cube[106:112] + [cube[232]] + cube[113:119] + [cube[225]] + cube[120:126] + [cube[218]] + cube[127:133] + [cube[211]] + cube[134:140] + [cube[204]] + cube[141:147] + [cube[197],cube[196],cube[195],cube[194],cube[193],cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181],cube[180],cube[179],cube[178],cube[177],cube[176],cube[175],cube[174],cube[173],cube[172],cube[171],cube[170],cube[169],cube[168],cube[167],cube[166],cube[165],cube[164],cube[163],cube[162],cube[161],cube[160],cube[159],cube[158],cube[157],cube[156],cube[155],cube[154],cube[153],cube[152],cube[151],cube[150],cube[149],cube[148],cube[147]] + cube[198:204] + [cube[140]] + cube[205:211] + [cube[133]] + cube[212:218] + [cube[126]] + cube[219:225] + [cube[119]] + cube[226:232] + [cube[112]] + cube[233:239] + [cube[105]] + cube[240:252] + [cube[7]] + cube[253:259] + [cube[14]] + cube[260:266] + [cube[21]] + cube[267:273] + [cube[28]] + cube[274:280] + [cube[35]] + cube[281:287] + [cube[42]] + cube[288:294] + [cube[49]]

def rotate_777_Rw(cube):
    return cube[0:6] + cube[104:106] + cube[8:13] + cube[111:113] + cube[15:20] + cube[118:120] + cube[22:27] + cube[125:127] + cube[29:34] + cube[132:134] + cube[36:41] + cube[139:141] + cube[43:48] + cube[146:148] + cube[50:104] + cube[251:253] + cube[106:111] + cube[258:260] + cube[113:118] + cube[265:267] + cube[120:125] + cube[272:274] + cube[127:132] + cube[279:281] + cube[134:139] + cube[286:288] + cube[141:146] + cube[293:295] + [cube[190],cube[183],cube[176],cube[169],cube[162],cube[155],cube[148],cube[191],cube[184],cube[177],cube[170],cube[163],cube[156],cube[149],cube[192],cube[185],cube[178],cube[171],cube[164],cube[157],cube[150],cube[193],cube[186],cube[179],cube[172],cube[165],cube[158],cube[151],cube[194],cube[187],cube[180],cube[173],cube[166],cube[159],cube[152],cube[195],cube[188],cube[181],cube[174],cube[167],cube[160],cube[153],cube[196],cube[189],cube[182],cube[175],cube[168],cube[161],cube[154],cube[49],cube[48]] + cube[199:204] + [cube[42],cube[41]] + cube[206:211] + [cube[35],cube[34]] + cube[213:218] + [cube[28],cube[27]] + cube[220:225] + [cube[21],cube[20]] + cube[227:232] + [cube[14],cube[13]] + cube[234:239] + [cube[7],cube[6]] + cube[241:251] + [cube[240],cube[239]] + cube[253:258] + [cube[233],cube[232]] + cube[260:265] + [cube[226],cube[225]] + cube[267:272] + [cube[219],cube[218]] + cube[274:279] + [cube[212],cube[211]] + cube[281:286] + [cube[205],cube[204]] + cube[288:293] + [cube[198],cube[197]]

def rotate_777_Rw_prime(cube):
    return cube[0:6] + [cube[240],cube[239]] + cube[8:13] + [cube[233],cube[232]] + cube[15:20] + [cube[226],cube[225]] + cube[22:27] + [cube[219],cube[218]] + cube[29:34] + [cube[212],cube[211]] + cube[36:41] + [cube[205],cube[204]] + cube[43:48] + [cube[198],cube[197]] + cube[50:104] + cube[6:8] + cube[106:111] + cube[13:15] + cube[113:118] + cube[20:22] + cube[120:125] + cube[27:29] + cube[127:132] + cube[34:36] + cube[134:139] + cube[41:43] + cube[141:146] + cube[48:50] + [cube[154],cube[161],cube[168],cube[175],cube[182],cube[189],cube[196],cube[153],cube[160],cube[167],cube[174],cube[181],cube[188],cube[195],cube[152],cube[159],cube[166],cube[173],cube[180],cube[187],cube[194],cube[151],cube[158],cube[165],cube[172],cube[179],cube[186],cube[193],cube[150],cube[157],cube[164],cube[171],cube[178],cube[185],cube[192],cube[149],cube[156],cube[163],cube[170],cube[177],cube[184],cube[191],cube[148],cube[155],cube[162],cube[169],cube[176],cube[183],cube[190],cube[294],cube[293]] + cube[199:204] + [cube[287],cube[286]] + cube[206:211] + [cube[280],cube[279]] + cube[213:218] + [cube[273],cube[272]] + cube[220:225] + [cube[266],cube[265]] + cube[227:232] + [cube[259],cube[258]] + cube[234:239] + [cube[252],cube[251]] + cube[241:251] + cube[104:106] + cube[253:258] + cube[111:113] + cube[260:265] + cube[118:120] + cube[267:272] + cube[125:127] + cube[274:279] + cube[132:134] + cube[281:286] + cube[139:141] + cube[288:293] + cube[146:148]

def rotate_777_Rw2(cube):
    return cube[0:6] + cube[251:253] + cube[8:13] + cube[258:260] + cube[15:20] + cube[265:267] + cube[22:27] + cube[272:274] + cube[29:34] + cube[279:281] + cube[36:41] + cube[286:288] + cube[43:48] + cube[293:295] + cube[50:104] + [cube[240],cube[239]] + cube[106:111] + [cube[233],cube[232]] + cube[113:118] + [cube[226],cube[225]] + cube[120:125] + [cube[219],cube[218]] + cube[127:132] + [cube[212],cube[211]] + cube[134:139] + [cube[205],cube[204]] + cube[141:146] + [cube[198],cube[197],cube[196],cube[195],cube[194],cube[193],cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181],cube[180],cube[179],cube[178],cube[177],cube[176],cube[175],cube[174],cube[173],cube[172],cube[171],cube[170],cube[169],cube[168],cube[167],cube[166],cube[165],cube[164],cube[163],cube[162],cube[161],cube[160],cube[159],cube[158],cube[157],cube[156],cube[155],cube[154],cube[153],cube[152],cube[151],cube[150],cube[149],cube[148],cube[147],cube[146]] + cube[199:204] + [cube[140],cube[139]] + cube[206:211] + [cube[133],cube[132]] + cube[213:218] + [cube[126],cube[125]] + cube[220:225] + [cube[119],cube[118]] + cube[227:232] + [cube[112],cube[111]] + cube[234:239] + [cube[105],cube[104]] + cube[241:251] + cube[6:8] + cube[253:258] + cube[13:15] + cube[260:265] + cube[20:22] + cube[267:272] + cube[27:29] + cube[274:279] + cube[34:36] + cube[281:286] + cube[41:43] + cube[288:293] + cube[48:50]

def rotate_777_3Rw(cube):
    return cube[0:5] + cube[103:106] + cube[8:12] + cube[110:113] + cube[15:19] + cube[117:120] + cube[22:26] + cube[124:127] + cube[29:33] + cube[131:134] + cube[36:40] + cube[138:141] + cube[43:47] + cube[145:148] + cube[50:103] + cube[250:253] + cube[106:110] + cube[257:260] + cube[113:117] + cube[264:267] + cube[120:124] + cube[271:274] + cube[127:131] + cube[278:281] + cube[134:138] + cube[285:288] + cube[141:145] + cube[292:295] + [cube[190],cube[183],cube[176],cube[169],cube[162],cube[155],cube[148],cube[191],cube[184],cube[177],cube[170],cube[163],cube[156],cube[149],cube[192],cube[185],cube[178],cube[171],cube[164],cube[157],cube[150],cube[193],cube[186],cube[179],cube[172],cube[165],cube[158],cube[151],cube[194],cube[187],cube[180],cube[173],cube[166],cube[159],cube[152],cube[195],cube[188],cube[181],cube[174],cube[167],cube[160],cube[153],cube[196],cube[189],cube[182],cube[175],cube[168],cube[161],cube[154],cube[49],cube[48],cube[47]] + cube[200:204] + [cube[42],cube[41],cube[40]] + cube[207:211] + [cube[35],cube[34],cube[33]] + cube[214:218] + [cube[28],cube[27],cube[26]] + cube[221:225] + [cube[21],cube[20],cube[19]] + cube[228:232] + [cube[14],cube[13],cube[12]] + cube[235:239] + [cube[7],cube[6],cube[5]] + cube[242:250] + [cube[241],cube[240],cube[239]] + cube[253:257] + [cube[234],cube[233],cube[232]] + cube[260:264] + [cube[227],cube[226],cube[225]] + cube[267:271] + [cube[220],cube[219],cube[218]] + cube[274:278] + [cube[213],cube[212],cube[211]] + cube[281:285] + [cube[206],cube[205],cube[204]] + cube[288:292] + [cube[199],cube[198],cube[197]]

def rotate_777_3Rw_prime(cube):
    return cube[0:5] + [cube[241],cube[240],cube[239]] + cube[8:12] + [cube[234],cube[233],cube[232]] + cube[15:19] + [cube[227],cube[226],cube[225]] + cube[22:26] + [cube[220],cube[219],cube[218]] + cube[29:33] + [cube[213],cube[212],cube[211]] + cube[36:40] + [cube[206],cube[205],cube[204]] + cube[43:47] + [cube[199],cube[198],cube[197]] + cube[50:103] + cube[5:8] + cube[106:110] + cube[12:15] + cube[113:117] + cube[19:22] + cube[120:124] + cube[26:29] + cube[127:131] + cube[33:36] + cube[134:138] + cube[40:43] + cube[141:145] + cube[47:50] + [cube[154],cube[161],cube[168],cube[175],cube[182],cube[189],cube[196],cube[153],cube[160],cube[167],cube[174],cube[181],cube[188],cube[195],cube[152],cube[159],cube[166],cube[173],cube[180],cube[187],cube[194],cube[151],cube[158],cube[165],cube[172],cube[179],cube[186],cube[193],cube[150],cube[157],cube[164],cube[171],cube[178],cube[185],cube[192],cube[149],cube[156],cube[163],cube[170],cube[177],cube[184],cube[191],cube[148],cube[155],cube[162],cube[169],cube[176],cube[183],cube[190],cube[294],cube[293],cube[292]] + cube[200:204] + [cube[287],cube[286],cube[285]] + cube[207:211] + [cube[280],cube[279],cube[278]] + cube[214:218] + [cube[273],cube[272],cube[271]] + cube[221:225] + [cube[266],cube[265],cube[264]] + cube[228:232] + [cube[259],cube[258],cube[257]] + cube[235:239] + [cube[252],cube[251],cube[250]] + cube[242:250] + cube[103:106] + cube[253:257] + cube[110:113] + cube[260:264] + cube[117:120] + cube[267:271] + cube[124:127] + cube[274:278] + cube[131:134] + cube[281:285] + cube[138:141] + cube[288:292] + cube[145:148]

def rotate_777_3Rw2(cube):
    return cube[0:5] + cube[250:253] + cube[8:12] + cube[257:260] + cube[15:19] + cube[264:267] + cube[22:26] + cube[271:274] + cube[29:33] + cube[278:281] + cube[36:40] + cube[285:288] + cube[43:47] + cube[292:295] + cube[50:103] + [cube[241],cube[240],cube[239]] + cube[106:110] + [cube[234],cube[233],cube[232]] + cube[113:117] + [cube[227],cube[226],cube[225]] + cube[120:124] + [cube[220],cube[219],cube[218]] + cube[127:131] + [cube[213],cube[212],cube[211]] + cube[134:138] + [cube[206],cube[205],cube[204]] + cube[141:145] + [cube[199],cube[198],cube[197],cube[196],cube[195],cube[194],cube[193],cube[192],cube[191],cube[190],cube[189],cube[188],cube[187],cube[186],cube[185],cube[184],cube[183],cube[182],cube[181],cube[180],cube[179],cube[178],cube[177],cube[176],cube[175],cube[174],cube[173],cube[172],cube[171],cube[170],cube[169],cube[168],cube[167],cube[166],cube[165],cube[164],cube[163],cube[162],cube[161],cube[160],cube[159],cube[158],cube[157],cube[156],cube[155],cube[154],cube[153],cube[152],cube[151],cube[150],cube[149],cube[148],cube[147],cube[146],cube[145]] + cube[200:204] + [cube[140],cube[139],cube[138]] + cube[207:211] + [cube[133],cube[132],cube[131]] + cube[214:218] + [cube[126],cube[125],cube[124]] + cube[221:225] + [cube[119],cube[118],cube[117]] + cube[228:232] + [cube[112],cube[111],cube[110]] + cube[235:239] + [cube[105],cube[104],cube[103]] + cube[242:250] + cube[5:8] + cube[253:257] + cube[12:15] + cube[260:264] + cube[19:22] + cube[267:271] + cube[26:29] + cube[274:278] + cube[33:36] + cube[281:285] + cube[40:43] + cube[288:292] + cube[47:50]

def rotate_777_B(cube):
    return [cube[0],cube[154],cube[161],cube[168],cube[175],cube[182],cube[189],cube[196]] + cube[8:50] + [cube[7]] + cube[51:57] + [cube[6]] + cube[58:64] + [cube[5]] + cube[65:71] + [cube[4]] + cube[72:78] + [cube[3]] + cube[79:85] + [cube[2]] + cube[86:92] + [cube[1]] + cube[93:154] + [cube[294]] + cube[155:161] + [cube[293]] + cube[162:168] + [cube[292]] + cube[169:175] + [cube[291]] + cube[176:182] + [cube[290]] + cube[183:189] + [cube[289]] + cube[190:196] + [cube[288],cube[239],cube[232],cube[225],cube[218],cube[211],cube[204],cube[197],cube[240],cube[233],cube[226],cube[219],cube[212],cube[205],cube[198],cube[241],cube[234],cube[227],cube[220],cube[213],cube[206],cube[199],cube[242],cube[235],cube[228],cube[221],cube[214],cube[207],cube[200],cube[243],cube[236],cube[229],cube[222],cube[215],cube[208],cube[201],cube[244],cube[237],cube[230],cube[223],cube[216],cube[209],cube[202],cube[245],cube[238],cube[231],cube[224],cube[217],cube[210],cube[203]] + cube[246:288] + [cube[50],cube[57],cube[64],cube[71],cube[78],cube[85],cube[92]]

def rotate_777_B_prime(cube):
    return [cube[0],cube[92],cube[85],cube[78],cube[71],cube[64],cube[57],cube[50]] + cube[8:50] + [cube[288]] + cube[51:57] + [cube[289]] + cube[58:64] + [cube[290]] + cube[65:71] + [cube[291]] + cube[72:78] + [cube[292]] + cube[79:85] + [cube[293]] + cube[86:92] + [cube[294]] + cube[93:154] + [cube[1]] + cube[155:161] + [cube[2]] + cube[162:168] + [cube[3]] + cube[169:175] + [cube[4]] + cube[176:182] + [cube[5]] + cube[183:189] + [cube[6]] + cube[190:196] + [cube[7],cube[203],cube[210],cube[217],cube[224],cube[231],cube[238],cube[245],cube[202],cube[209],cube[216],cube[223],cube[230],cube[237],cube[244],cube[201],cube[208],cube[215],cube[222],cube[229],cube[236],cube[243],cube[200],cube[207],cube[214],cube[221],cube[228],cube[235],cube[242],cube[199],cube[206],cube[213],cube[220],cube[227],cube[234],cube[241],cube[198],cube[205],cube[212],cube[219],cube[226],cube[233],cube[240],cube[197],cube[204],cube[211],cube[218],cube[225],cube[232],cube[239]] + cube[246:288] + [cube[196],cube[189],cube[182],cube[175],cube[168],cube[161],cube[154]]

def rotate_777_B2(cube):
    return [cube[0],cube[294],cube[293],cube[292],cube[291],cube[290],cube[289],cube[288]] + cube[8:50] + [cube[196]] + cube[51:57] + [cube[189]] + cube[58:64] + [cube[182]] + cube[65:71] + [cube[175]] + cube[72:78] + [cube[168]] + cube[79:85] + [cube[161]] + cube[86:92] + [cube[154]] + cube[93:154] + [cube[92]] + cube[155:161] + [cube[85]] + cube[162:168] + [cube[78]] + cube[169:175] + [cube[71]] + cube[176:182] + [cube[64]] + cube[183:189] + [cube[57]] + cube[190:196] + [cube[50],cube[245],cube[244],cube[243],cube[242],cube[241],cube[240],cube[239],cube[238],cube[237],cube[236],cube[235],cube[234],cube[233],cube[232],cube[231],cube[230],cube[229],cube[228],cube[227],cube[226],cube[225],cube[224],cube[223],cube[222],cube[221],cube[220],cube[219],cube[218],cube[217],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197]] + cube[246:288] + [cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]]

def rotate_777_Bw(cube):
    return [cube[0],cube[154],cube[161],cube[168],cube[175],cube[182],cube[189],cube[196],cube[153],cube[160],cube[167],cube[174],cube[181],cube[188],cube[195]] + cube[15:50] + [cube[7],cube[14]] + cube[52:57] + [cube[6],cube[13]] + cube[59:64] + [cube[5],cube[12]] + cube[66:71] + [cube[4],cube[11]] + cube[73:78] + [cube[3],cube[10]] + cube[80:85] + [cube[2],cube[9]] + cube[87:92] + [cube[1],cube[8]] + cube[94:153] + [cube[287],cube[294]] + cube[155:160] + [cube[286],cube[293]] + cube[162:167] + [cube[285],cube[292]] + cube[169:174] + [cube[284],cube[291]] + cube[176:181] + [cube[283],cube[290]] + cube[183:188] + [cube[282],cube[289]] + cube[190:195] + [cube[281],cube[288],cube[239],cube[232],cube[225],cube[218],cube[211],cube[204],cube[197],cube[240],cube[233],cube[226],cube[219],cube[212],cube[205],cube[198],cube[241],cube[234],cube[227],cube[220],cube[213],cube[206],cube[199],cube[242],cube[235],cube[228],cube[221],cube[214],cube[207],cube[200],cube[243],cube[236],cube[229],cube[222],cube[215],cube[208],cube[201],cube[244],cube[237],cube[230],cube[223],cube[216],cube[209],cube[202],cube[245],cube[238],cube[231],cube[224],cube[217],cube[210],cube[203]] + cube[246:281] + [cube[51],cube[58],cube[65],cube[72],cube[79],cube[86],cube[93],cube[50],cube[57],cube[64],cube[71],cube[78],cube[85],cube[92]]

def rotate_777_Bw_prime(cube):
    return [cube[0],cube[92],cube[85],cube[78],cube[71],cube[64],cube[57],cube[50],cube[93],cube[86],cube[79],cube[72],cube[65],cube[58],cube[51]] + cube[15:50] + [cube[288],cube[281]] + cube[52:57] + [cube[289],cube[282]] + cube[59:64] + [cube[290],cube[283]] + cube[66:71] + [cube[291],cube[284]] + cube[73:78] + [cube[292],cube[285]] + cube[80:85] + [cube[293],cube[286]] + cube[87:92] + [cube[294],cube[287]] + cube[94:153] + [cube[8],cube[1]] + cube[155:160] + [cube[9],cube[2]] + cube[162:167] + [cube[10],cube[3]] + cube[169:174] + [cube[11],cube[4]] + cube[176:181] + [cube[12],cube[5]] + cube[183:188] + [cube[13],cube[6]] + cube[190:195] + [cube[14],cube[7],cube[203],cube[210],cube[217],cube[224],cube[231],cube[238],cube[245],cube[202],cube[209],cube[216],cube[223],cube[230],cube[237],cube[244],cube[201],cube[208],cube[215],cube[222],cube[229],cube[236],cube[243],cube[200],cube[207],cube[214],cube[221],cube[228],cube[235],cube[242],cube[199],cube[206],cube[213],cube[220],cube[227],cube[234],cube[241],cube[198],cube[205],cube[212],cube[219],cube[226],cube[233],cube[240],cube[197],cube[204],cube[211],cube[218],cube[225],cube[232],cube[239]] + cube[246:281] + [cube[195],cube[188],cube[181],cube[174],cube[167],cube[160],cube[153],cube[196],cube[189],cube[182],cube[175],cube[168],cube[161],cube[154]]

def rotate_777_Bw2(cube):
    return [cube[0],cube[294],cube[293],cube[292],cube[291],cube[290],cube[289],cube[288],cube[287],cube[286],cube[285],cube[284],cube[283],cube[282],cube[281]] + cube[15:50] + [cube[196],cube[195]] + cube[52:57] + [cube[189],cube[188]] + cube[59:64] + [cube[182],cube[181]] + cube[66:71] + [cube[175],cube[174]] + cube[73:78] + [cube[168],cube[167]] + cube[80:85] + [cube[161],cube[160]] + cube[87:92] + [cube[154],cube[153]] + cube[94:153] + [cube[93],cube[92]] + cube[155:160] + [cube[86],cube[85]] + cube[162:167] + [cube[79],cube[78]] + cube[169:174] + [cube[72],cube[71]] + cube[176:181] + [cube[65],cube[64]] + cube[183:188] + [cube[58],cube[57]] + cube[190:195] + [cube[51],cube[50],cube[245],cube[244],cube[243],cube[242],cube[241],cube[240],cube[239],cube[238],cube[237],cube[236],cube[235],cube[234],cube[233],cube[232],cube[231],cube[230],cube[229],cube[228],cube[227],cube[226],cube[225],cube[224],cube[223],cube[222],cube[221],cube[220],cube[219],cube[218],cube[217],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197]] + cube[246:281] + [cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]]

def rotate_777_3Bw(cube):
    return [cube[0],cube[154],cube[161],cube[168],cube[175],cube[182],cube[189],cube[196],cube[153],cube[160],cube[167],cube[174],cube[181],cube[188],cube[195],cube[152],cube[159],cube[166],cube[173],cube[180],cube[187],cube[194]] + cube[22:50] + [cube[7],cube[14],cube[21]] + cube[53:57] + [cube[6],cube[13],cube[20]] + cube[60:64] + [cube[5],cube[12],cube[19]] + cube[67:71] + [cube[4],cube[11],cube[18]] + cube[74:78] + [cube[3],cube[10],cube[17]] + cube[81:85] + [cube[2],cube[9],cube[16]] + cube[88:92] + [cube[1],cube[8],cube[15]] + cube[95:152] + [cube[280],cube[287],cube[294]] + cube[155:159] + [cube[279],cube[286],cube[293]] + cube[162:166] + [cube[278],cube[285],cube[292]] + cube[169:173] + [cube[277],cube[284],cube[291]] + cube[176:180] + [cube[276],cube[283],cube[290]] + cube[183:187] + [cube[275],cube[282],cube[289]] + cube[190:194] + [cube[274],cube[281],cube[288],cube[239],cube[232],cube[225],cube[218],cube[211],cube[204],cube[197],cube[240],cube[233],cube[226],cube[219],cube[212],cube[205],cube[198],cube[241],cube[234],cube[227],cube[220],cube[213],cube[206],cube[199],cube[242],cube[235],cube[228],cube[221],cube[214],cube[207],cube[200],cube[243],cube[236],cube[229],cube[222],cube[215],cube[208],cube[201],cube[244],cube[237],cube[230],cube[223],cube[216],cube[209],cube[202],cube[245],cube[238],cube[231],cube[224],cube[217],cube[210],cube[203]] + cube[246:274] + [cube[52],cube[59],cube[66],cube[73],cube[80],cube[87],cube[94],cube[51],cube[58],cube[65],cube[72],cube[79],cube[86],cube[93],cube[50],cube[57],cube[64],cube[71],cube[78],cube[85],cube[92]]

def rotate_777_3Bw_prime(cube):
    return [cube[0],cube[92],cube[85],cube[78],cube[71],cube[64],cube[57],cube[50],cube[93],cube[86],cube[79],cube[72],cube[65],cube[58],cube[51],cube[94],cube[87],cube[80],cube[73],cube[66],cube[59],cube[52]] + cube[22:50] + [cube[288],cube[281],cube[274]] + cube[53:57] + [cube[289],cube[282],cube[275]] + cube[60:64] + [cube[290],cube[283],cube[276]] + cube[67:71] + [cube[291],cube[284],cube[277]] + cube[74:78] + [cube[292],cube[285],cube[278]] + cube[81:85] + [cube[293],cube[286],cube[279]] + cube[88:92] + [cube[294],cube[287],cube[280]] + cube[95:152] + [cube[15],cube[8],cube[1]] + cube[155:159] + [cube[16],cube[9],cube[2]] + cube[162:166] + [cube[17],cube[10],cube[3]] + cube[169:173] + [cube[18],cube[11],cube[4]] + cube[176:180] + [cube[19],cube[12],cube[5]] + cube[183:187] + [cube[20],cube[13],cube[6]] + cube[190:194] + [cube[21],cube[14],cube[7],cube[203],cube[210],cube[217],cube[224],cube[231],cube[238],cube[245],cube[202],cube[209],cube[216],cube[223],cube[230],cube[237],cube[244],cube[201],cube[208],cube[215],cube[222],cube[229],cube[236],cube[243],cube[200],cube[207],cube[214],cube[221],cube[228],cube[235],cube[242],cube[199],cube[206],cube[213],cube[220],cube[227],cube[234],cube[241],cube[198],cube[205],cube[212],cube[219],cube[226],cube[233],cube[240],cube[197],cube[204],cube[211],cube[218],cube[225],cube[232],cube[239]] + cube[246:274] + [cube[194],cube[187],cube[180],cube[173],cube[166],cube[159],cube[152],cube[195],cube[188],cube[181],cube[174],cube[167],cube[160],cube[153],cube[196],cube[189],cube[182],cube[175],cube[168],cube[161],cube[154]]

def rotate_777_3Bw2(cube):
    return [cube[0],cube[294],cube[293],cube[292],cube[291],cube[290],cube[289],cube[288],cube[287],cube[286],cube[285],cube[284],cube[283],cube[282],cube[281],cube[280],cube[279],cube[278],cube[277],cube[276],cube[275],cube[274]] + cube[22:50] + [cube[196],cube[195],cube[194]] + cube[53:57] + [cube[189],cube[188],cube[187]] + cube[60:64] + [cube[182],cube[181],cube[180]] + cube[67:71] + [cube[175],cube[174],cube[173]] + cube[74:78] + [cube[168],cube[167],cube[166]] + cube[81:85] + [cube[161],cube[160],cube[159]] + cube[88:92] + [cube[154],cube[153],cube[152]] + cube[95:152] + [cube[94],cube[93],cube[92]] + cube[155:159] + [cube[87],cube[86],cube[85]] + cube[162:166] + [cube[80],cube[79],cube[78]] + cube[169:173] + [cube[73],cube[72],cube[71]] + cube[176:180] + [cube[66],cube[65],cube[64]] + cube[183:187] + [cube[59],cube[58],cube[57]] + cube[190:194] + [cube[52],cube[51],cube[50],cube[245],cube[244],cube[243],cube[242],cube[241],cube[240],cube[239],cube[238],cube[237],cube[236],cube[235],cube[234],cube[233],cube[232],cube[231],cube[230],cube[229],cube[228],cube[227],cube[226],cube[225],cube[224],cube[223],cube[222],cube[221],cube[220],cube[219],cube[218],cube[217],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197]] + cube[246:274] + [cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]]

def rotate_777_D(cube):
    return cube[0:92] + cube[239:246] + cube[99:141] + cube[92:99] + cube[148:190] + cube[141:148] + cube[197:239] + cube[190:197] + [cube[288],cube[281],cube[274],cube[267],cube[260],cube[253],cube[246],cube[289],cube[282],cube[275],cube[268],cube[261],cube[254],cube[247],cube[290],cube[283],cube[276],cube[269],cube[262],cube[255],cube[248],cube[291],cube[284],cube[277],cube[270],cube[263],cube[256],cube[249],cube[292],cube[285],cube[278],cube[271],cube[264],cube[257],cube[250],cube[293],cube[286],cube[279],cube[272],cube[265],cube[258],cube[251],cube[294],cube[287],cube[280],cube[273],cube[266],cube[259],cube[252]]

def rotate_777_D_prime(cube):
    return cube[0:92] + cube[141:148] + cube[99:141] + cube[190:197] + cube[148:190] + cube[239:246] + cube[197:239] + cube[92:99] + [cube[252],cube[259],cube[266],cube[273],cube[280],cube[287],cube[294],cube[251],cube[258],cube[265],cube[272],cube[279],cube[286],cube[293],cube[250],cube[257],cube[264],cube[271],cube[278],cube[285],cube[292],cube[249],cube[256],cube[263],cube[270],cube[277],cube[284],cube[291],cube[248],cube[255],cube[262],cube[269],cube[276],cube[283],cube[290],cube[247],cube[254],cube[261],cube[268],cube[275],cube[282],cube[289],cube[246],cube[253],cube[260],cube[267],cube[274],cube[281],cube[288]]

def rotate_777_D2(cube):
    return cube[0:92] + cube[190:197] + cube[99:141] + cube[239:246] + cube[148:190] + cube[92:99] + cube[197:239] + cube[141:148] + [cube[294],cube[293],cube[292],cube[291],cube[290],cube[289],cube[288],cube[287],cube[286],cube[285],cube[284],cube[283],cube[282],cube[281],cube[280],cube[279],cube[278],cube[277],cube[276],cube[275],cube[274],cube[273],cube[272],cube[271],cube[270],cube[269],cube[268],cube[267],cube[266],cube[265],cube[264],cube[263],cube[262],cube[261],cube[260],cube[259],cube[258],cube[257],cube[256],cube[255],cube[254],cube[253],cube[252],cube[251],cube[250],cube[249],cube[248],cube[247],cube[246]]

def rotate_777_Dw(cube):
    return cube[0:85] + cube[232:246] + cube[99:134] + cube[85:99] + cube[148:183] + cube[134:148] + cube[197:232] + cube[183:197] + [cube[288],cube[281],cube[274],cube[267],cube[260],cube[253],cube[246],cube[289],cube[282],cube[275],cube[268],cube[261],cube[254],cube[247],cube[290],cube[283],cube[276],cube[269],cube[262],cube[255],cube[248],cube[291],cube[284],cube[277],cube[270],cube[263],cube[256],cube[249],cube[292],cube[285],cube[278],cube[271],cube[264],cube[257],cube[250],cube[293],cube[286],cube[279],cube[272],cube[265],cube[258],cube[251],cube[294],cube[287],cube[280],cube[273],cube[266],cube[259],cube[252]]

def rotate_777_Dw_prime(cube):
    return cube[0:85] + cube[134:148] + cube[99:134] + cube[183:197] + cube[148:183] + cube[232:246] + cube[197:232] + cube[85:99] + [cube[252],cube[259],cube[266],cube[273],cube[280],cube[287],cube[294],cube[251],cube[258],cube[265],cube[272],cube[279],cube[286],cube[293],cube[250],cube[257],cube[264],cube[271],cube[278],cube[285],cube[292],cube[249],cube[256],cube[263],cube[270],cube[277],cube[284],cube[291],cube[248],cube[255],cube[262],cube[269],cube[276],cube[283],cube[290],cube[247],cube[254],cube[261],cube[268],cube[275],cube[282],cube[289],cube[246],cube[253],cube[260],cube[267],cube[274],cube[281],cube[288]]

def rotate_777_Dw2(cube):
    return cube[0:85] + cube[183:197] + cube[99:134] + cube[232:246] + cube[148:183] + cube[85:99] + cube[197:232] + cube[134:148] + [cube[294],cube[293],cube[292],cube[291],cube[290],cube[289],cube[288],cube[287],cube[286],cube[285],cube[284],cube[283],cube[282],cube[281],cube[280],cube[279],cube[278],cube[277],cube[276],cube[275],cube[274],cube[273],cube[272],cube[271],cube[270],cube[269],cube[268],cube[267],cube[266],cube[265],cube[264],cube[263],cube[262],cube[261],cube[260],cube[259],cube[258],cube[257],cube[256],cube[255],cube[254],cube[253],cube[252],cube[251],cube[250],cube[249],cube[248],cube[247],cube[246]]

def rotate_777_3Dw(cube):
    return cube[0:78] + cube[225:246] + cube[99:127] + cube[78:99] + cube[148:176] + cube[127:148] + cube[197:225] + cube[176:197] + [cube[288],cube[281],cube[274],cube[267],cube[260],cube[253],cube[246],cube[289],cube[282],cube[275],cube[268],cube[261],cube[254],cube[247],cube[290],cube[283],cube[276],cube[269],cube[262],cube[255],cube[248],cube[291],cube[284],cube[277],cube[270],cube[263],cube[256],cube[249],cube[292],cube[285],cube[278],cube[271],cube[264],cube[257],cube[250],cube[293],cube[286],cube[279],cube[272],cube[265],cube[258],cube[251],cube[294],cube[287],cube[280],cube[273],cube[266],cube[259],cube[252]]

def rotate_777_3Dw_prime(cube):
    return cube[0:78] + cube[127:148] + cube[99:127] + cube[176:197] + cube[148:176] + cube[225:246] + cube[197:225] + cube[78:99] + [cube[252],cube[259],cube[266],cube[273],cube[280],cube[287],cube[294],cube[251],cube[258],cube[265],cube[272],cube[279],cube[286],cube[293],cube[250],cube[257],cube[264],cube[271],cube[278],cube[285],cube[292],cube[249],cube[256],cube[263],cube[270],cube[277],cube[284],cube[291],cube[248],cube[255],cube[262],cube[269],cube[276],cube[283],cube[290],cube[247],cube[254],cube[261],cube[268],cube[275],cube[282],cube[289],cube[246],cube[253],cube[260],cube[267],cube[274],cube[281],cube[288]]

def rotate_777_3Dw2(cube):
    return cube[0:78] + cube[176:197] + cube[99:127] + cube[225:246] + cube[148:176] + cube[78:99] + cube[197:225] + cube[127:148] + [cube[294],cube[293],cube[292],cube[291],cube[290],cube[289],cube[288],cube[287],cube[286],cube[285],cube[284],cube[283],cube[282],cube[281],cube[280],cube[279],cube[278],cube[277],cube[276],cube[275],cube[274],cube[273],cube[272],cube[271],cube[270],cube[269],cube[268],cube[267],cube[266],cube[265],cube[264],cube[263],cube[262],cube[261],cube[260],cube[259],cube[258],cube[257],cube[256],cube[255],cube[254],cube[253],cube[252],cube[251],cube[250],cube[249],cube[248],cube[247],cube[246]]

def rotate_777_x(cube):
    return [cube[0]] + cube[99:148] + [cube[56],cube[63],cube[70],cube[77],cube[84],cube[91],cube[98],cube[55],cube[62],cube[69],cube[76],cube[83],cube[90],cube[97],cube[54],cube[61],cube[68],cube[75],cube[82],cube[89],cube[96],cube[53],cube[60],cube[67],cube[74],cube[81],cube[88],cube[95],cube[52],cube[59],cube[66],cube[73],cube[80],cube[87],cube[94],cube[51],cube[58],cube[65],cube[72],cube[79],cube[86],cube[93],cube[50],cube[57],cube[64],cube[71],cube[78],cube[85],cube[92]] + cube[246:295] + [cube[190],cube[183],cube[176],cube[169],cube[162],cube[155],cube[148],cube[191],cube[184],cube[177],cube[170],cube[163],cube[156],cube[149],cube[192],cube[185],cube[178],cube[171],cube[164],cube[157],cube[150],cube[193],cube[186],cube[179],cube[172],cube[165],cube[158],cube[151],cube[194],cube[187],cube[180],cube[173],cube[166],cube[159],cube[152],cube[195],cube[188],cube[181],cube[174],cube[167],cube[160],cube[153],cube[196],cube[189],cube[182],cube[175],cube[168],cube[161],cube[154],cube[49],cube[48],cube[47],cube[46],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1],cube[245],cube[244],cube[243],cube[242],cube[241],cube[240],cube[239],cube[238],cube[237],cube[236],cube[235],cube[234],cube[233],cube[232],cube[231],cube[230],cube[229],cube[228],cube[227],cube[226],cube[225],cube[224],cube[223],cube[222],cube[221],cube[220],cube[219],cube[218],cube[217],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197]]

def rotate_777_x_prime(cube):
    return [cube[0],cube[245],cube[244],cube[243],cube[242],cube[241],cube[240],cube[239],cube[238],cube[237],cube[236],cube[235],cube[234],cube[233],cube[232],cube[231],cube[230],cube[229],cube[228],cube[227],cube[226],cube[225],cube[224],cube[223],cube[222],cube[221],cube[220],cube[219],cube[218],cube[217],cube[216],cube[215],cube[214],cube[213],cube[212],cube[211],cube[210],cube[209],cube[208],cube[207],cube[206],cube[205],cube[204],cube[203],cube[202],cube[201],cube[200],cube[199],cube[198],cube[197],cube[92],cube[85],cube[78],cube[71],cube[64],cube[57],cube[50],cube[93],cube[86],cube[79],cube[72],cube[65],cube[58],cube[51],cube[94],cube[87],cube[80],cube[73],cube[66],cube[59],cube[52],cube[95],cube[88],cube[81],cube[74],cube[67],cube[60],cube[53],cube[96],cube[89],cube[82],cube[75],cube[68],cube[61],cube[54],cube[97],cube[90],cube[83],cube[76],cube[69],cube[62],cube[55],cube[98],cube[91],cube[84],cube[77],cube[70],cube[63],cube[56]] + cube[1:50] + [cube[154],cube[161],cube[168],cube[175],cube[182],cube[189],cube[196],cube[153],cube[160],cube[167],cube[174],cube[181],cube[188],cube[195],cube[152],cube[159],cube[166],cube[173],cube[180],cube[187],cube[194],cube[151],cube[158],cube[165],cube[172],cube[179],cube[186],cube[193],cube[150],cube[157],cube[164],cube[171],cube[178],cube[185],cube[192],cube[149],cube[156],cube[163],cube[170],cube[177],cube[184],cube[191],cube[148],cube[155],cube[162],cube[169],cube[176],cube[183],cube[190],cube[294],cube[293],cube[292],cube[291],cube[290],cube[289],cube[288],cube[287],cube[286],cube[285],cube[284],cube[283],cube[282],cube[281],cube[280],cube[279],cube[278],cube[277],cube[276],cube[275],cube[274],cube[273],cube[272],cube[271],cube[270],cube[269],cube[268],cube[267],cube[266],cube[265],cube[264],cube[263],cube[262],cube[261],cube[260],cube[259],cube[258],cube[257],cube[256],cube[255],cube[254],cube[253],cube[252],cube[251],cube[250],cube[249],cube[248],cube[247],cube[246]] + cube[99:148]

def rotate_777_y(cube):
    return [cube[0],cube[43],cube[36],cube[29],cube[22],cube[15],cube[8],cube[1],cube[44],cube[37],cube[30],cube[23],cube[16],cube[9],cube[2],cube[45],cube[38],cube[31],cube[24],cube[17],cube[10],cube[3],cube[46],cube[39],cube[32],cube[25],cube[18],cube[11],cube[4],cube[47],cube[40],cube[33],cube[26],cube[19],cube[12],cube[5],cube[48],cube[41],cube[34],cube[27],cube[20],cube[13],cube[6],cube[49],cube[42],cube[35],cube[28],cube[21],cube[14],cube[7]] + cube[99:246] + cube[50:99] + [cube[252],cube[259],cube[266],cube[273],cube[280],cube[287],cube[294],cube[251],cube[258],cube[265],cube[272],cube[279],cube[286],cube[293],cube[250],cube[257],cube[264],cube[271],cube[278],cube[285],cube[292],cube[249],cube[256],cube[263],cube[270],cube[277],cube[284],cube[291],cube[248],cube[255],cube[262],cube[269],cube[276],cube[283],cube[290],cube[247],cube[254],cube[261],cube[268],cube[275],cube[282],cube[289],cube[246],cube[253],cube[260],cube[267],cube[274],cube[281],cube[288]]

def rotate_777_y_prime(cube):
    return [cube[0],cube[7],cube[14],cube[21],cube[28],cube[35],cube[42],cube[49],cube[6],cube[13],cube[20],cube[27],cube[34],cube[41],cube[48],cube[5],cube[12],cube[19],cube[26],cube[33],cube[40],cube[47],cube[4],cube[11],cube[18],cube[25],cube[32],cube[39],cube[46],cube[3],cube[10],cube[17],cube[24],cube[31],cube[38],cube[45],cube[2],cube[9],cube[16],cube[23],cube[30],cube[37],cube[44],cube[1],cube[8],cube[15],cube[22],cube[29],cube[36],cube[43]] + cube[197:246] + cube[50:197] + [cube[288],cube[281],cube[274],cube[267],cube[260],cube[253],cube[246],cube[289],cube[282],cube[275],cube[268],cube[261],cube[254],cube[247],cube[290],cube[283],cube[276],cube[269],cube[262],cube[255],cube[248],cube[291],cube[284],cube[277],cube[270],cube[263],cube[256],cube[249],cube[292],cube[285],cube[278],cube[271],cube[264],cube[257],cube[250],cube[293],cube[286],cube[279],cube[272],cube[265],cube[258],cube[251],cube[294],cube[287],cube[280],cube[273],cube[266],cube[259],cube[252]]

def rotate_777_z(cube):
    return [cube[0],cube[92],cube[85],cube[78],cube[71],cube[64],cube[57],cube[50],cube[93],cube[86],cube[79],cube[72],cube[65],cube[58],cube[51],cube[94],cube[87],cube[80],cube[73],cube[66],cube[59],cube[52],cube[95],cube[88],cube[81],cube[74],cube[67],cube[60],cube[53],cube[96],cube[89],cube[82],cube[75],cube[68],cube[61],cube[54],cube[97],cube[90],cube[83],cube[76],cube[69],cube[62],cube[55],cube[98],cube[91],cube[84],cube[77],cube[70],cube[63],cube[56],cube[288],cube[281],cube[274],cube[267],cube[260],cube[253],cube[246],cube[289],cube[282],cube[275],cube[268],cube[261],cube[254],cube[247],cube[290],cube[283],cube[276],cube[269],cube[262],cube[255],cube[248],cube[291],cube[284],cube[277],cube[270],cube[263],cube[256],cube[249],cube[292],cube[285],cube[278],cube[271],cube[264],cube[257],cube[250],cube[293],cube[286],cube[279],cube[272],cube[265],cube[258],cube[251],cube[294],cube[287],cube[280],cube[273],cube[266],cube[259],cube[252],cube[141],cube[134],cube[127],cube[120],cube[113],cube[106],cube[99],cube[142],cube[135],cube[128],cube[121],cube[114],cube[107],cube[100],cube[143],cube[136],cube[129],cube[122],cube[115],cube[108],cube[101],cube[144],cube[137],cube[130],cube[123],cube[116],cube[109],cube[102],cube[145],cube[138],cube[131],cube[124],cube[117],cube[110],cube[103],cube[146],cube[139],cube[132],cube[125],cube[118],cube[111],cube[104],cube[147],cube[140],cube[133],cube[126],cube[119],cube[112],cube[105],cube[43],cube[36],cube[29],cube[22],cube[15],cube[8],cube[1],cube[44],cube[37],cube[30],cube[23],cube[16],cube[9],cube[2],cube[45],cube[38],cube[31],cube[24],cube[17],cube[10],cube[3],cube[46],cube[39],cube[32],cube[25],cube[18],cube[11],cube[4],cube[47],cube[40],cube[33],cube[26],cube[19],cube[12],cube[5],cube[48],cube[41],cube[34],cube[27],cube[20],cube[13],cube[6],cube[49],cube[42],cube[35],cube[28],cube[21],cube[14],cube[7],cube[203],cube[210],cube[217],cube[224],cube[231],cube[238],cube[245],cube[202],cube[209],cube[216],cube[223],cube[230],cube[237],cube[244],cube[201],cube[208],cube[215],cube[222],cube[229],cube[236],cube[243],cube[200],cube[207],cube[214],cube[221],cube[228],cube[235],cube[242],cube[199],cube[206],cube[213],cube[220],cube[227],cube[234],cube[241],cube[198],cube[205],cube[212],cube[219],cube[226],cube[233],cube[240],cube[197],cube[204],cube[211],cube[218],cube[225],cube[232],cube[239],cube[190],cube[183],cube[176],cube[169],cube[162],cube[155],cube[148],cube[191],cube[184],cube[177],cube[170],cube[163],cube[156],cube[149],cube[192],cube[185],cube[178],cube[171],cube[164],cube[157],cube[150],cube[193],cube[186],cube[179],cube[172],cube[165],cube[158],cube[151],cube[194],cube[187],cube[180],cube[173],cube[166],cube[159],cube[152],cube[195],cube[188],cube[181],cube[174],cube[167],cube[160],cube[153],cube[196],cube[189],cube[182],cube[175],cube[168],cube[161],cube[154]]

def rotate_777_z_prime(cube):
    return [cube[0],cube[154],cube[161],cube[168],cube[175],cube[182],cube[189],cube[196],cube[153],cube[160],cube[167],cube[174],cube[181],cube[188],cube[195],cube[152],cube[159],cube[166],cube[173],cube[180],cube[187],cube[194],cube[151],cube[158],cube[165],cube[172],cube[179],cube[186],cube[193],cube[150],cube[157],cube[164],cube[171],cube[178],cube[185],cube[192],cube[149],cube[156],cube[163],cube[170],cube[177],cube[184],cube[191],cube[148],cube[155],cube[162],cube[169],cube[176],cube[183],cube[190],cube[7],cube[14],cube[21],cube[28],cube[35],cube[42],cube[49],cube[6],cube[13],cube[20],cube[27],cube[34],cube[41],cube[48],cube[5],cube[12],cube[19],cube[26],cube[33],cube[40],cube[47],cube[4],cube[11],cube[18],cube[25],cube[32],cube[39],cube[46],cube[3],cube[10],cube[17],cube[24],cube[31],cube[38],cube[45],cube[2],cube[9],cube[16],cube[23],cube[30],cube[37],cube[44],cube[1],cube[8],cube[15],cube[22],cube[29],cube[36],cube[43],cube[105],cube[112],cube[119],cube[126],cube[133],cube[140],cube[147],cube[104],cube[111],cube[118],cube[125],cube[132],cube[139],cube[146],cube[103],cube[110],cube[117],cube[124],cube[131],cube[138],cube[145],cube[102],cube[109],cube[116],cube[123],cube[130],cube[137],cube[144],cube[101],cube[108],cube[115],cube[122],cube[129],cube[136],cube[143],cube[100],cube[107],cube[114],cube[121],cube[128],cube[135],cube[142],cube[99],cube[106],cube[113],cube[120],cube[127],cube[134],cube[141],cube[252],cube[259],cube[266],cube[273],cube[280],cube[287],cube[294],cube[251],cube[258],cube[265],cube[272],cube[279],cube[286],cube[293],cube[250],cube[257],cube[264],cube[271],cube[278],cube[285],cube[292],cube[249],cube[256],cube[263],cube[270],cube[277],cube[284],cube[291],cube[248],cube[255],cube[262],cube[269],cube[276],cube[283],cube[290],cube[247],cube[254],cube[261],cube[268],cube[275],cube[282],cube[289],cube[246],cube[253],cube[260],cube[267],cube[274],cube[281],cube[288],cube[239],cube[232],cube[225],cube[218],cube[211],cube[204],cube[197],cube[240],cube[233],cube[226],cube[219],cube[212],cube[205],cube[198],cube[241],cube[234],cube[227],cube[220],cube[213],cube[206],cube[199],cube[242],cube[235],cube[228],cube[221],cube[214],cube[207],cube[200],cube[243],cube[236],cube[229],cube[222],cube[215],cube[208],cube[201],cube[244],cube[237],cube[230],cube[223],cube[216],cube[209],cube[202],cube[245],cube[238],cube[231],cube[224],cube[217],cube[210],cube[203],cube[56],cube[63],cube[70],cube[77],cube[84],cube[91],cube[98],cube[55],cube[62],cube[69],cube[76],cube[83],cube[90],cube[97],cube[54],cube[61],cube[68],cube[75],cube[82],cube[89],cube[96],cube[53],cube[60],cube[67],cube[74],cube[81],cube[88],cube[95],cube[52],cube[59],cube[66],cube[73],cube[80],cube[87],cube[94],cube[51],cube[58],cube[65],cube[72],cube[79],cube[86],cube[93],cube[50],cube[57],cube[64],cube[71],cube[78],cube[85],cube[92]]

rotate_mapper_777 = {
    "3Bw" : rotate_777_3Bw,
    "3Bw'" : rotate_777_3Bw_prime,
    "3Bw2" : rotate_777_3Bw2,
    "3Dw" : rotate_777_3Dw,
    "3Dw'" : rotate_777_3Dw_prime,
    "3Dw2" : rotate_777_3Dw2,
    "3Fw" : rotate_777_3Fw,
    "3Fw'" : rotate_777_3Fw_prime,
    "3Fw2" : rotate_777_3Fw2,
    "3Lw" : rotate_777_3Lw,
    "3Lw'" : rotate_777_3Lw_prime,
    "3Lw2" : rotate_777_3Lw2,
    "3Rw" : rotate_777_3Rw,
    "3Rw'" : rotate_777_3Rw_prime,
    "3Rw2" : rotate_777_3Rw2,
    "3Uw" : rotate_777_3Uw,
    "3Uw'" : rotate_777_3Uw_prime,
    "3Uw2" : rotate_777_3Uw2,
    "B" : rotate_777_B,
    "B'" : rotate_777_B_prime,
    "B2" : rotate_777_B2,
    "Bw" : rotate_777_Bw,
    "Bw'" : rotate_777_Bw_prime,
    "Bw2" : rotate_777_Bw2,
    "D" : rotate_777_D,
    "D'" : rotate_777_D_prime,
    "D2" : rotate_777_D2,
    "Dw" : rotate_777_Dw,
    "Dw'" : rotate_777_Dw_prime,
    "Dw2" : rotate_777_Dw2,
    "F" : rotate_777_F,
    "F'" : rotate_777_F_prime,
    "F2" : rotate_777_F2,
    "Fw" : rotate_777_Fw,
    "Fw'" : rotate_777_Fw_prime,
    "Fw2" : rotate_777_Fw2,
    "L" : rotate_777_L,
    "L'" : rotate_777_L_prime,
    "L2" : rotate_777_L2,
    "Lw" : rotate_777_Lw,
    "Lw'" : rotate_777_Lw_prime,
    "Lw2" : rotate_777_Lw2,
    "R" : rotate_777_R,
    "R'" : rotate_777_R_prime,
    "R2" : rotate_777_R2,
    "Rw" : rotate_777_Rw,
    "Rw'" : rotate_777_Rw_prime,
    "Rw2" : rotate_777_Rw2,
    "U" : rotate_777_U,
    "U'" : rotate_777_U_prime,
    "U2" : rotate_777_U2,
    "Uw" : rotate_777_Uw,
    "Uw'" : rotate_777_Uw_prime,
    "Uw2" : rotate_777_Uw2,
    "x" : rotate_777_x,
    "x'" : rotate_777_x_prime,
    "y" : rotate_777_y,
    "y'" : rotate_777_y_prime,
    "z" : rotate_777_z,
    "z'" : rotate_777_z_prime,
}

def rotate_777(cube, step):
    return rotate_mapper_777[step](cube)
