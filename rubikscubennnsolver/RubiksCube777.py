
from rubikscubennnsolver.RubiksCubeNNNOddEdges import RubiksCubeNNNOddEdges
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_666, moves_666
from rubikscubennnsolver.RubiksCube777Misc import (
    state_targets_step30,
    state_targets_step31,
    state_targets_step32,
)
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA, LookupTableHashCostOnly
import logging
import math
import sys

log = logging.getLogger(__name__)

moves_777 = moves_666
solved_777 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'


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
    ================================================================
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
    This is 5-deep...6-deep has 5 million entries which takes too much memory to preload

    lookup-table-7x7x7-step10-UD-oblique-edge-pairing.txt
    =====================================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 67 entries (0 percent, 16.75x previous step)
    3 steps has 916 entries (0 percent, 13.67x previous step)
    4 steps has 10,132 entries (2 percent, 11.06x previous step)
    5 steps has 92,068 entries (24 percent, 9.09x previous step)
    6 steps has 229,615 entries (60 percent, 2.49x previous step)
    7 steps has 46,431 entries (12 percent, 0.20x previous step)
    8 steps has 790 entries (0 percent, 0.02x previous step)

    Total: 380,023 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step10-UD-oblique-edge-pairing.txt',
            'fff000000000000fff',
            moves_777,

            # do not mess up UD 5x5x5 centers
            ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'"),

            # prune tables
            (parent.lt_UD_oblique_edge_pairing_middle_only,
             parent.lt_UD_oblique_edge_pairing_left_only,
             parent.lt_UD_oblique_edge_pairing_right_only),

            linecount=380023,
            max_depth=5,
            filesize=21661311)

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


class LookupTable777LROutsideObliqueEdgePairing(LookupTableHashCostOnly):
    """
    lookup-table-7x7x7-step31-stage-lr-oblique-edges.txt
    ====================================================
    1 steps has 45,158 entries (0 percent, 0.00x previous step)
    2 steps has 293,056 entries (0 percent, 6.49x previous step)
    3 steps has 2,056,784 entries (1 percent, 7.02x previous step)
    4 steps has 11,562,716 entries (6 percent, 5.62x previous step)
    5 steps has 43,269,568 entries (26 percent, 3.74x previous step)
    6 steps has 75,723,092 entries (45 percent, 1.75x previous step)
    7 steps has 31,697,280 entries (19 percent, 0.42x previous step)
    8 steps has 983,238 entries (0 percent, 0.03x previous step)
    9 steps has 5,992 entries (0 percent, 0.01x previous step)
    10 steps has 16 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 5.76 moves
    """
    LFRB_outside_oblique_edges_777 = (
        59, 61, 65, 69, 79, 83, 87, 89, # Left
        108, 110, 114, 118, 128, 132, 136, 138, # Front
        157, 159, 163, 167, 177, 181, 185, 187, # Right
        206, 208, 212, 216, 226, 230, 234, 236, # Back
    )

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step31-stage-lr-oblique-edges.hash-cost-only.txt',
            state_targets_step31,
            linecount=165636900,
            max_depth=10,
            bucketcount=331273823)

        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step31-stage-lr-oblique-edges.txt',
            state_targets_step31,
            linecount=165636900,
            max_depth=10)
        '''

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in self.LFRB_outside_oblique_edges_777])
        return self.hex_format % int(result, 2)


class LookupTable777LRLeftMiddleObliqueEdgePairing(LookupTableHashCostOnly):
    """
    lookup-table-7x7x7-step32-stage-lr-left-middle-oblique-edges.txt
    ================================================================
    1 steps has 60,390 entries (0 percent, 0.00x previous step)
    2 steps has 504,512 entries (0 percent, 8.35x previous step)
    3 steps has 3,164,712 entries (1 percent, 6.27x previous step)
    4 steps has 14,547,152 entries (8 percent, 4.60x previous step)
    5 steps has 39,862,724 entries (24 percent, 2.74x previous step)
    6 steps has 59,903,328 entries (36 percent, 1.50x previous step)
    7 steps has 38,877,292 entries (23 percent, 0.65x previous step)
    8 steps has 8,224,240 entries (4 percent, 0.21x previous step)
    9 steps has 486,440 entries (0 percent, 0.06x previous step)
    10 steps has 6,102 entries (0 percent, 0.01x previous step)
    11 steps has 8 entries (0 percent, 0.00x previous step)

    Total: 165,636,900 entries
    Average: 5.86 moves
    """
    LFRB_left_middle_oblique_edges_777 = (
        59, 60, 69, 72, 76, 79, 88, 89, # Left
        108, 109, 118, 121, 125, 128, 137, 138, # Front
        157, 158, 167, 170, 174, 177, 186, 187, # Right
        206, 207, 216, 219, 223, 226, 235, 236, # Back
    )

    def __init__(self, parent):
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step32-stage-lr-left-middle-oblique-edges.hash-cost-only.txt',
            state_targets_step32,
            linecount=165636900,
            max_depth=11,
            bucketcount=331273823)

        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step32-stage-lr-left-middle-oblique-edges.txt',
            state_targets_step32,
            linecount=165636900,
            max_depth=11)
        '''

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in self.LFRB_left_middle_oblique_edges_777])
        return self.hex_format % int(result, 2)


class LookupTable777LRRightMiddleObliqueEdgePairing(LookupTable777LRLeftMiddleObliqueEdgePairing):

    # The order here looks weird but this is so we can re-use the left-middle step32 prune table
    LFRB_right_middle_oblique_edges_777 = (
        61, 60, 65, 76, 72, 83, 88, 87, # Left
        110, 109, 114, 125, 121, 132, 137, 136, # Front
        159, 158, 163, 174, 170, 181, 186, 185, # Right
        208, 207, 212, 223, 219, 230, 235, 234, # Back
    )

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in self.LFRB_right_middle_oblique_edges_777])
        return self.hex_format % int(result, 2)


class LookupTable777LRObliqueEdgePairingInadmisibble(LookupTable):

    LFRB_oblique_edge_pairs_777 = (
        #(10, 11, 12), (16, 23, 30), (20, 27, 34), (38, 39, 40),             # Upper
        (59, 60, 61), (65, 72, 79), (69, 76, 83), (87, 88, 89),             # Left
        (108, 109, 110), (114, 121, 128), (118, 125, 132), (136, 137, 138), # Front
        (157, 158, 159), (163, 170, 177), (167, 174, 181), (185, 186, 187), # Right
        (206, 207, 208), (212, 219, 226), (216, 223, 230), (234, 235, 236), # Back
        #(255, 256, 257), (261, 268, 275), (265, 272, 279), (283, 284, 285), # Down
    )

    LFRB_left_oblique_edge_pairs_777 = (
        #(10, 11), (23, 30), (20, 27), (39, 40),         # Upper
        (59, 60), (72, 79), (69, 76), (88, 89),         # Left
        (108, 109), (121, 128), (118, 125), (137, 138), # Front
        (157, 158), (170, 177), (167, 174), (186, 187), # Right
        (206, 207), (219, 226), (216, 223), (235, 236), # Back
        #(255, 256), (268, 275), (265, 272), (284, 285), # Down
    )

    LFRB_right_oblique_edge_pairs_777 = (
        #(11, 12), (16, 23), (27, 34), (38, 39),         # Upper
        (60, 61), (65, 72), (76, 83), (87, 88),         # Left
        (109, 110), (114, 121), (125, 132), (136, 137), # Front
        (158, 159), (163, 170), (174, 181), (185, 186), # Right
        (207, 208), (212, 219), (223, 230), (234, 235), # Back
        #(256, 257), (261, 268), (272, 279), (283, 284), # Down
    )

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step34-stage-lr-oblique-edges-inadmissible-dummy.txt',
            'TBD',
            linecount=0,
            max_depth=4) # 4 is the max heuristic() can return

    def get_LR_unpaired_obliques_count(self):
        parent_state = self.parent.state
        paired_obliques = 0

        for (x, y, z) in self.LFRB_oblique_edge_pairs_777:
            if parent_state[x] in ('L', 'R') and parent_state[y] in ('L', 'R') and parent_state[z] in ('L', 'R'):
                paired_obliques += 1

        return 8 - paired_obliques

    def get_LR_left_unpaired_obliques_count(self):
        parent_state = self.parent.state
        paired_obliques = 0

        for (x, y) in self.LFRB_left_oblique_edge_pairs_777:
            if parent_state[x] in ('L', 'R') and parent_state[y] in ('L', 'R'):
                paired_obliques += 1

        return 8 - paired_obliques

    def get_LR_right_unpaired_obliques_count(self):
        parent_state = self.parent.state
        paired_obliques = 0

        for (x, y) in self.LFRB_right_oblique_edge_pairs_777:
            if parent_state[x] in ('L', 'R') and parent_state[y] in ('L', 'R'):
                paired_obliques += 1

        return 8 - paired_obliques

    def heuristic(self):
        LR_left_unpaired_obliques = self.get_LR_left_unpaired_obliques_count()
        LR_right_unpaired_obliques = self.get_LR_right_unpaired_obliques_count()

        # This returns 3 about 99% of the time
        result = max(math.ceil(LR_left_unpaired_obliques/2), math.ceil(LR_right_unpaired_obliques/2))
        #log.info("left %d, right %d, return %d" % (LR_left_unpaired_obliques, LR_right_unpaired_obliques, result))
        return result


class LookupTableIDA777LRObliqueEdgePairing(LookupTableIDA):
    """
    lookup-table-7x7x7-step30-stage-lr-oblique-edges.txt
    ====================================================
    1 steps has 77,446 entries (0 percent, 0.00x previous step)
    2 steps has 831,520 entries (8 percent, 10.74x previous step)
    3 steps has 9,010,776 entries (90 percent, 10.84x previous step)

    Total: 9,919,742 entries
    Average: 2.90 moves

    A good test cube for this is:
    LLDBLFDRRFDUBFLLLFLLDFLDUBRULFLFDRDRUBBUDBFLFRUBFLDBFRDRFLLRBDUUFRFURDDDBRRLDUDUBLRLLBUDRUDBUUUUBUUDLDFRURFFUFURRRDLBRFLLUFUULRUBRRURULFUBUURLDBRBDBFRLULLFLDLFRRDLRBFDBBFDDUDRBBUUFLBFBLRDDDBRFLBURFDDRBDRBRLURFUDDUFBBFBFLLRFFLLRDFDBBFBRFDLLURUFDDFLFDFBDFFUBDBRBUDDDBLFBLBRBRURFLBBULLDFURUBBLURFU

    Before adding the step32 table this took
    IDA explored 1996722 nodes in 0:01:08.574970, 29117 nodes-per-sec

    After step32 it takes
    IDA explored 603286 nodes in 0:00:24.398978, 24725 nodes-per-sec

    This is still slower than I would like, I need to dig into this more.
    """
    LFRB_oblique_edges_777 = (
        59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89, # Left
        108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138, # Front
        157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187, # Right
        206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236, # Back
    )

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step30-stage-lr-oblique-edges.txt',
            state_targets_step30,
            moves_777,

            ("3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged inner-x-centers
             "3Lw", "3Lw'", "3Rw", "3Rw'",
             "3Fw", "3Fw'", "3Bw", "3Bw'",
             "Rw", "Rw'", "Lw", "Lw'",     # do not mess up staged UD oblique pairs
             "Fw", "Fw'", "Bw", "Bw'"),

            # prune tables
            (parent.lt_LR_outside_oblique_edge_pairing,
             parent.lt_LR_left_middle_oblique_edge_pairing,
             parent.lt_LR_right_middle_oblique_edge_pairing,
             parent.lt_LR_oblique_edge_pairing_inadmissible),

            linecount=9919742,
            max_depth=3),

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] in ('L', 'R') else '0' for x in self.LFRB_oblique_edges_777])
        return self.hex_format % int(result, 2)


#class LookupTable777Step41(LookupTable):
class LookupTable777Step41(LookupTableHashCostOnly):
    """
    lookup-table-7x7x7-step41.txt
    =============================
    1 steps has 226 entries (0 percent, 0.00x previous step)
    2 steps has 1,433 entries (0 percent, 6.34x previous step)
    3 steps has 8,986 entries (0 percent, 6.27x previous step)
    4 steps has 54,072 entries (0 percent, 6.02x previous step)
    5 steps has 290,610 entries (1 percent, 5.37x previous step)
    6 steps has 1,339,251 entries (5 percent, 4.61x previous step)
    7 steps has 4,706,248 entries (19 percent, 3.51x previous step)
    8 steps has 9,659,696 entries (40 percent, 2.05x previous step)
    9 steps has 7,031,230 entries (29 percent, 0.73x previous step)
    10 steps has 907,920 entries (3 percent, 0.13x previous step)
    11 steps has 10,296 entries (0 percent, 0.01x previous step)
    12 steps has 32 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    Average: 8.01 moves
    """

    state_targets = (
        'LLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRR',
        'LLLLLLRLLLLLLLRLLRRLRRRRRRRLRRRRRR',
        'LLLLLLRLLLLLLLRLLRRRRRRLRRRRRRRLRR',
        'LLRLLLLLLLRLLLLLLRRLRRRRRRRLRRRRRR',
        'LLRLLLLLLLRLLLLLLRRRRRRLRRRRRRRLRR',
        'LLRLLLRLLLRLLLRLLRRLRRRLRRRLRRRLRR',
        'LRLLLRLLLRLLLRLLRLRRLRRRLRRRLRRRLR',
        'LRLLLRLLLRLLLRLLRRLRRRLRRRLRRRLRRL',
        'LRLLLRRLLRLLLRRLRLRLLRRRLRRLLRRRLR',
        'LRLLLRRLLRLLLRRLRLRRLRRLLRRRLRRLLR',
        'LRLLLRRLLRLLLRRLRRLLRRLRRRLLRRLRRL',
        'LRLLLRRLLRLLLRRLRRLRRRLLRRLRRRLLRL',
        'LRRLLRLLLRRLLRLLRLRLLRRRLRRLLRRRLR',
        'LRRLLRLLLRRLLRLLRLRRLRRLLRRRLRRLLR',
        'LRRLLRLLLRRLLRLLRRLLRRLRRRLLRRLRRL',
        'LRRLLRLLLRRLLRLLRRLRRRLLRRLRRRLLRL',
        'LRRLLRRLLRRLLRRLRLRLLRRLLRRLLRRLLR',
        'LRRLLRRLLRRLLRRLRRLLRRLLRRLLRRLLRL',
        'RLLRLLLRLLLRLLLRLLRRLRRRLRRRLRRRLR',
        'RLLRLLLRLLLRLLLRLRLRRRLRRRLRRRLRRL',
        'RLLRLLRRLLLRLLRRLLRLLRRRLRRLLRRRLR',
        'RLLRLLRRLLLRLLRRLLRRLRRLLRRRLRRLLR',
        'RLLRLLRRLLLRLLRRLRLLRRLRRRLLRRLRRL',
        'RLLRLLRRLLLRLLRRLRLRRRLLRRLRRRLLRL',
        'RLRRLLLRLLRRLLLRLLRLLRRRLRRLLRRRLR',
        'RLRRLLLRLLRRLLLRLLRRLRRLLRRRLRRLLR',
        'RLRRLLLRLLRRLLLRLRLLRRLRRRLLRRLRRL',
        'RLRRLLLRLLRRLLLRLRLRRRLLRRLRRRLLRL',
        'RLRRLLRRLLRRLLRRLLRLLRRLLRRLLRRLLR',
        'RLRRLLRRLLRRLLRRLRLLRRLLRRLLRRLLRL',
        'RRLRLRLRLRLRLRLRRLLRLRLRLRLRLRLRLL',
        'RRLRLRRRLRLRLRRRRLLLLRLRLRLLLRLRLL',
        'RRLRLRRRLRLRLRRRRLLRLRLLLRLRLRLLLL',
        'RRRRLRLRLRRRLRLRRLLLLRLRLRLLLRLRLL',
        'RRRRLRLRLRRRLRLRRLLRLRLLLRLRLRLLLL',
        'RRRRLRRRLRRRLRRRRLLLLRLLLRLLLRLLLL'
    )

    centers_step41_777 = (
        59, 61, 65, 66, 67, 68, 69, 73, 74, 75, 79, 80, 81, 82, 83, 87, 89, # Left
        157, 159, 163, 164, 165, 166, 167, 171, 172, 173, 177, 178, 179, 180, 181, 185, 187, # Right
    )

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step41.txt',
            self.state_targets,
            linecount=24010000,
            max_depth=12,
            filesize=2064860000)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step41.hash-cost-only.txt',
            self.state_targets,
            linecount=24010000,
            max_depth=12,
            bucketcount=48020003,
            filesize=48020004)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.centers_step41_777])
        return result


#class LookupTable777Step42(LookupTable):
class LookupTable777Step42(LookupTableHashCostOnly):
    """
    lookup-table-7x7x7-step42.txt
    =============================
    1 steps has 250 entries (0 percent, 0.00x previous step)
    2 steps has 1,845 entries (0 percent, 7.38x previous step)
    3 steps has 12,756 entries (0 percent, 6.91x previous step)
    4 steps has 82,273 entries (0 percent, 6.45x previous step)
    5 steps has 468,727 entries (1 percent, 5.70x previous step)
    6 steps has 2,158,967 entries (8 percent, 4.61x previous step)
    7 steps has 6,972,890 entries (29 percent, 3.23x previous step)
    8 steps has 10,557,164 entries (43 percent, 1.51x previous step)
    9 steps has 3,640,612 entries (15 percent, 0.34x previous step)
    10 steps has 114,304 entries (0 percent, 0.03x previous step)
    11 steps has 212 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    Average: 7.62 moves
    """

    state_targets = (
        'LLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRR',
        'LLLLLRLLLRLLLRLLLRRRLRRRLRRRLRRRRR',
        'LLLLLRLLLRLLLRLLLRRRRRLRRRLRRRLRRR',
        'LLLRLLLRLLLRLLLLLRRRLRRRLRRRLRRRRR',
        'LLLRLLLRLLLRLLLLLRRRRRLRRRLRRRLRRR',
        'LLLRLRLRLRLRLRLLLRRRLRLRLRLRLRLRRR',
        'LLRLLLLLLLRLLLLLRLRRRRRLRRRRRRRLRR',
        'LLRLLLLLLLRLLLLLRRRLRRRRRRRLRRRRRL',
        'LLRLLRLLLRRLLRLLRLRRLRRLLRRRLRRLRR',
        'LLRLLRLLLRRLLRLLRLRRRRLLRRLRRRLLRR',
        'LLRLLRLLLRRLLRLLRRRLLRRRLRRLLRRRRL',
        'LLRLLRLLLRRLLRLLRRRLRRLRRRLLRRLRRL',
        'LLRRLLLRLLRRLLLLRLRRLRRLLRRRLRRLRR',
        'LLRRLLLRLLRRLLLLRLRRRRLLRRLRRRLLRR',
        'LLRRLLLRLLRRLLLLRRRLLRRRLRRLLRRRRL',
        'LLRRLLLRLLRRLLLLRRRLRRLRRRLLRRLRRL',
        'LLRRLRLRLRRRLRLLRLRRLRLLLRLRLRLLRR',
        'LLRRLRLRLRRRLRLLRRRLLRLRLRLLLRLRRL',
        'RLLLLLRLLLLLLLRLLLRRRRRLRRRRRRRLRR',
        'RLLLLLRLLLLLLLRLLRRLRRRRRRRLRRRRRL',
        'RLLLLRRLLRLLLRRLLLRRLRRLLRRRLRRLRR',
        'RLLLLRRLLRLLLRRLLLRRRRLLRRLRRRLLRR',
        'RLLLLRRLLRLLLRRLLRRLLRRRLRRLLRRRRL',
        'RLLLLRRLLRLLLRRLLRRLRRLRRRLLRRLRRL',
        'RLLRLLRRLLLRLLRLLLRRLRRLLRRRLRRLRR',
        'RLLRLLRRLLLRLLRLLLRRRRLLRRLRRRLLRR',
        'RLLRLLRRLLLRLLRLLRRLLRRRLRRLLRRRRL',
        'RLLRLLRRLLLRLLRLLRRLRRLRRRLLRRLRRL',
        'RLLRLRRRLRLRLRRLLLRRLRLLLRLRLRLLRR',
        'RLLRLRRRLRLRLRRLLRRLLRLRLRLLLRLRRL',
        'RLRLLLRLLLRLLLRLRLRLRRRLRRRLRRRLRL',
        'RLRLLRRLLRRLLRRLRLRLLRRLLRRLLRRLRL',
        'RLRLLRRLLRRLLRRLRLRLRRLLRRLLRRLLRL',
        'RLRRLLRRLLRRLLRLRLRLLRRLLRRLLRRLRL',
        'RLRRLLRRLLRRLLRLRLRLRRLLRRLLRRLLRL',
        'RLRRLRRRLRRRLRRLRLRLLRLLLRLLLRLLRL'
    )

    centers_step42_777 = (
        58, 60, 62, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 86, 88, 90, # Left
        156, 158, 160, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 184, 186, 188, # Right
    )

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step42.txt',
            self.state_targets,
            linecount=24010000,
            max_depth=11,
            filesize=2040850000)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step42.hash-cost-only.txt',
            self.state_targets,
            linecount=24010000,
            max_depth=11,
            bucketcount=48020003,
            filesize=48020004)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.centers_step42_777])
        return result


class LookupTableIDA777Step40(LookupTableIDA):
    """
    lookup-table-7x7x7-step40.txt
    =============================
    1 steps has 250 entries (0 percent, 0.00x previous step)
    2 steps has 1,981 entries (0 percent, 7.92x previous step)
    3 steps has 15,782 entries (0 percent, 7.97x previous step)
    4 steps has 123,053 entries (1 percent, 7.80x previous step)
    5 steps has 931,072 entries (11 percent, 7.57x previous step)
    6 steps has 6,799,621 entries (86 percent, 7.30x previous step)

    Total: 7,871,759 entries
    """

    state_targets = (
        'LLLLLLLLLLLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRRRRRRRRRRR',
        'LLLLRLLLLRLLLLRLLLLRLLLLRLRRRRLRRRRLRRRRLRRRRLRRRR',
        'LLLLRLLLLRLLLLRLLLLRLLLLRRRRRLRRRRLRRRRLRRRRLRRRRL',
        'LLLRLLLLRLLLLRLLLLRLLLLRLRLRRRRLRRRRLRRRRLRRRRLRRR',
        'LLLRLLLLRLLLLRLLLLRLLLLRLRRRLRRRRLRRRRLRRRRLRRRRLR',
        'LLLRRLLLRRLLLRRLLLRRLLLRRLLRRRLLRRRLLRRRLLRRRLLRRR',
        'LLLRRLLLRRLLLRRLLLRRLLLRRLRRLRLRRLRLRRLRLRRLRLRRLR',
        'LLLRRLLLRRLLLRRLLLRRLLLRRRLRRLRLRRLRLRRLRLRRLRLRRL',
        'LLLRRLLLRRLLLRRLLLRRLLLRRRRRLLRRRLLRRRLLRRRLLRRRLL',
        'LRLLLLRLLLLRLLLLRLLLLRLLLRLRRRRLRRRRLRRRRLRRRRLRRR',
        'LRLLLLRLLLLRLLLLRLLLLRLLLRRRLRRRRLRRRRLRRRRLRRRRLR',
        'LRLLRLRLLRLRLLRLRLLRLRLLRLLRRRLLRRRLLRRRLLRRRLLRRR',
        'LRLLRLRLLRLRLLRLRLLRLRLLRLRRLRLRRLRLRRLRLRRLRLRRLR',
        'LRLLRLRLLRLRLLRLRLLRLRLLRRLRRLRLRRLRLRRLRLRRLRLRRL',
        'LRLLRLRLLRLRLLRLRLLRLRLLRRRRLLRRRLLRRRLLRRRLLRRRLL',
        'LRLRLLRLRLLRLRLLRLRLLRLRLRLRLRRLRLRRLRLRRLRLRRLRLR',
        'LRLRRLRLRRLRLRRLRLRRLRLRRLLRLRLLRLRLLRLRLLRLRLLRLR',
        'LRLRRLRLRRLRLRRLRLRRLRLRRRLRLLRLRLLRLRLLRLRLLRLRLL',
        'RLLLLRLLLLRLLLLRLLLLRLLLLLRRRRLRRRRLRRRRLRRRRLRRRR',
        'RLLLLRLLLLRLLLLRLLLLRLLLLRRRRLRRRRLRRRRLRRRRLRRRRL',
        'RLLLRRLLLRRLLLRRLLLRRLLLRLRRRLLRRRLLRRRLLRRRLLRRRL',
        'RLLRLRLLRLRLLRLRLLRLRLLRLLLRRRLLRRRLLRRRLLRRRLLRRR',
        'RLLRLRLLRLRLLRLRLLRLRLLRLLRRLRLRRLRLRRLRLRRLRLRRLR',
        'RLLRLRLLRLRLLRLRLLRLRLLRLRLRRLRLRRLRLRRLRLRRLRLRRL',
        'RLLRLRLLRLRLLRLRLLRLRLLRLRRRLLRRRLLRRRLLRRRLLRRRLL',
        'RLLRRRLLRRRLLRRRLLRRRLLRRLLRRLLLRRLLLRRLLLRRLLLRRL',
        'RLLRRRLLRRRLLRRRLLRRRLLRRLRRLLLRRLLLRRLLLRRLLLRRLL',
        'RRLLLRRLLLRRLLLRRLLLRRLLLLLRRRLLRRRLLRRRLLRRRLLRRR',
        'RRLLLRRLLLRRLLLRRLLLRRLLLLRRLRLRRLRLRRLRLRRLRLRRLR',
        'RRLLLRRLLLRRLLLRRLLLRRLLLRLRRLRLRRLRLRRLRLRRLRLRRL',
        'RRLLLRRLLLRRLLLRRLLLRRLLLRRRLLRRRLLRRRLLRRRLLRRRLL',
        'RRLLRRRLLRRRLLRRRLLRRRLLRLLRRLLLRRLLLRRLLLRRLLLRRL',
        'RRLLRRRLLRRRLLRRRLLRRRLLRLRRLLLRRLLLRRLLLRRLLLRRLL',
        'RRLRLRRLRLRRLRLRRLRLRRLRLLLRLRLLRLRLLRLRLLRLRLLRLR',
        'RRLRLRRLRLRRLRLRRLRLRRLRLRLRLLRLRLLRLRLLRLRLLRLRLL',
        'RRLRRRRLRRRRLRRRRLRRRRLRRLLRLLLLRLLLLRLLLLRLLLLRLL'
    )

    centers_step40_777 = (
        58, 59, 60, 61, 62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 86, 87, 88, 89, 90, # Left
        156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188, # Right
    )

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step40.txt',
            self.state_targets,
            moves_777,

            # illegal moves
            ("3Uw", "3Uw'", "3Uw2", "Uw", "Uw'", "Uw2",
             "3Lw", "3Lw'", "3Lw2", "Lw", "Lw'", "Lw2",
             "3Fw", "3Fw'", "Fw", "Fw'",
             "3Rw", "3Rw'", "3Rw2", "Rw", "Rw'", "Rw2",
             "3Bw", "3Bw'", "Bw", "Bw'",
             "3Dw", "3Dw'", "3Dw2", "Dw", "Dw'", "Dw2"),

            # prune tables
            (parent.lt_step41,
             parent.lt_step42),
            linecount=7871759,
            max_depth=6,
            filesize=440818504)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.centers_step40_777])
        return result


#class LookupTable777Step51(LookupTable):
class LookupTable777Step51(LookupTableHashCostOnly):
    """
    lookup-table-7x7x7-step51.txt
    =============================
    1 steps has 226 entries (0 percent, 0.00x previous step)
    2 steps has 1,433 entries (0 percent, 6.34x previous step)
    3 steps has 8,986 entries (0 percent, 6.27x previous step)
    4 steps has 54,072 entries (0 percent, 6.02x previous step)
    5 steps has 290,610 entries (1 percent, 5.37x previous step)
    6 steps has 1,339,251 entries (5 percent, 4.61x previous step)
    7 steps has 4,706,248 entries (19 percent, 3.51x previous step)
    8 steps has 9,659,696 entries (40 percent, 2.05x previous step)
    9 steps has 7,031,230 entries (29 percent, 0.73x previous step)
    10 steps has 907,920 entries (3 percent, 0.13x previous step)
    11 steps has 10,296 entries (0 percent, 0.01x previous step)
    12 steps has 32 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    Average: 8.01 moves
    """

    state_targets = (
        'DDDDUDDDUDDDUDDDDUUUUDUUUDUUUDUUUU',
        'DDDDUDUDUDDDUDUDDUUDUDUUUDUDUDUUUU',
        'DDDDUDUDUDDDUDUDDUUUUDUDUDUUUDUDUU',
        'DDUDUDDDUDUDUDDDDUUDUDUUUDUDUDUUUU',
        'DDUDUDDDUDUDUDDDDUUUUDUDUDUUUDUDUU',
        'DDUDUDUDUDUDUDUDDUUDUDUDUDUDUDUDUU',
        'DUDDUUDDUUDDUUDDUDUUDDUUDDUUDDUUDU',
        'DUDDUUDDUUDDUUDDUUDUUDDUUDDUUDDUUD',
        'DUDDUUUDUUDDUUUDUDUDDDUUDDUDDDUUDU',
        'DUDDUUUDUUDDUUUDUDUUDDUDDDUUDDUDDU',
        'DUDDUUUDUUDDUUUDUUDDUDDUUDDDUDDUUD',
        'DUDDUUUDUUDDUUUDUUDUUDDDUDDUUDDDUD',
        'DUUDUUDDUUUDUUDDUDUDDDUUDDUDDDUUDU',
        'DUUDUUDDUUUDUUDDUDUUDDUDDDUUDDUDDU',
        'DUUDUUDDUUUDUUDDUUDDUDDUUDDDUDDUUD',
        'DUUDUUDDUUUDUUDDUUDUUDDDUDDUUDDDUD',
        'DUUDUUUDUUUDUUUDUDUDDDUDDDUDDDUDDU',
        'DUUDUUUDUUUDUUUDUUDDUDDDUDDDUDDDUD',
        'UDDUUDDUUDDUUDDUDDUUDDUUDDUUDDUUDU',
        'UDDUUDDUUDDUUDDUDUDUUDDUUDDUUDDUUD',
        'UDDUUDUUUDDUUDUUDDUDDDUUDDUDDDUUDU',
        'UDDUUDUUUDDUUDUUDDUUDDUDDDUUDDUDDU',
        'UDDUUDUUUDDUUDUUDUDDUDDUUDDDUDDUUD',
        'UDDUUDUUUDDUUDUUDUDUUDDDUDDUUDDDUD',
        'UDUUUDDUUDUUUDDUDDUDDDUUDDUDDDUUDU',
        'UDUUUDDUUDUUUDDUDDUUDDUDDDUUDDUDDU',
        'UDUUUDDUUDUUUDDUDUDDUDDUUDDDUDDUUD',
        'UDUUUDDUUDUUUDDUDUDUUDDDUDDUUDDDUD',
        'UDUUUDUUUDUUUDUUDDUDDDUDDDUDDDUDDU',
        'UDUUUDUUUDUUUDUUDUDDUDDDUDDDUDDDUD',
        'UUDUUUDUUUDUUUDUUDDUDDDUDDDUDDDUDD',
        'UUDUUUUUUUDUUUUUUDDDDDDUDDDDDDDUDD',
        'UUDUUUUUUUDUUUUUUDDUDDDDDDDUDDDDDD',
        'UUUUUUDUUUUUUUDUUDDDDDDUDDDDDDDUDD',
        'UUUUUUDUUUUUUUDUUDDUDDDDDDDUDDDDDD',
        'UUUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDDD'
    )

    centers_step51_777 = (
        10, 12, 16, 17, 18, 19, 20, 24, 25, 26, 30, 31, 32, 33, 34, 38, 40, # Upper
        255, 257, 261, 262, 263, 264, 265, 269, 270, 271, 275, 276, 277, 278, 279, 283, 285, # Down
    )

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step51.txt',
            self.state_targets,
            linecount=24010000,
            max_depth=12,
            filesize=2064860000)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step51.hash-cost-only.txt',
            self.state_targets,
            linecount=24010000,
            max_depth=12,
            bucketcount=48020003,
            filesize=48020004)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.centers_step51_777])
        return result


#class LookupTable777Step52(LookupTable):
class LookupTable777Step52(LookupTableHashCostOnly):
    """
    lookup-table-7x7x7-step52.txt
    =============================
    1 steps has 250 entries (0 percent, 0.00x previous step)
    2 steps has 1,845 entries (0 percent, 7.38x previous step)
    3 steps has 12,756 entries (0 percent, 6.91x previous step)
    4 steps has 82,273 entries (0 percent, 6.45x previous step)
    5 steps has 468,727 entries (1 percent, 5.70x previous step)
    6 steps has 2,158,967 entries (8 percent, 4.61x previous step)
    7 steps has 6,972,890 entries (29 percent, 3.23x previous step)
    8 steps has 10,557,164 entries (43 percent, 1.51x previous step)
    9 steps has 3,640,612 entries (15 percent, 0.34x previous step)
    10 steps has 114,304 entries (0 percent, 0.03x previous step)
    11 steps has 212 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    Average: 7.62 moves
    """

    state_targets = (
        'DUDDUDDDUDDDUDDUDUDUUDUUUDUUUDUUDU',
        'DUDDUUDDUUDDUUDUDUDUDDUUDDUUDDUUDU',
        'DUDDUUDDUUDDUUDUDUDUUDDUUDDUUDDUDU',
        'DUDUUDDUUDDUUDDUDUDUDDUUDDUUDDUUDU',
        'DUDUUDDUUDDUUDDUDUDUUDDUUDDUUDDUDU',
        'DUDUUUDUUUDUUUDUDUDUDDDUDDDUDDDUDU',
        'DUUDUDDDUDUDUDDUUDDUUDUDUDUUUDUDDU',
        'DUUDUDDDUDUDUDDUUUDDUDUUUDUDUDUUDD',
        'DUUDUUDDUUUDUUDUUDDUDDUDDDUUDDUDDU',
        'DUUDUUDDUUUDUUDUUDDUUDDDUDDUUDDDDU',
        'DUUDUUDDUUUDUUDUUUDDDDUUDDUDDDUUDD',
        'DUUDUUDDUUUDUUDUUUDDUDDUUDDDUDDUDD',
        'DUUUUDDUUDUUUDDUUDDUDDUDDDUUDDUDDU',
        'DUUUUDDUUDUUUDDUUDDUUDDDUDDUUDDDDU',
        'DUUUUDDUUDUUUDDUUUDDDDUUDDUDDDUUDD',
        'DUUUUDDUUDUUUDDUUUDDUDDUUDDDUDDUDD',
        'DUUUUUDUUUUUUUDUUDDUDDDDDDDUDDDDDU',
        'DUUUUUDUUUUUUUDUUUDDDDDUDDDDDDDUDD',
        'UUDDUDUDUDDDUDUUDDDUUDUDUDUUUDUDDU',
        'UUDDUDUDUDDDUDUUDUDDUDUUUDUDUDUUDD',
        'UUDDUUUDUUDDUUUUDDDUDDUDDDUUDDUDDU',
        'UUDDUUUDUUDDUUUUDDDUUDDDUDDUUDDDDU',
        'UUDDUUUDUUDDUUUUDUDDDDUUDDUDDDUUDD',
        'UUDDUUUDUUDDUUUUDUDDUDDUUDDDUDDUDD',
        'UUDUUDUUUDDUUDUUDDDUDDUDDDUUDDUDDU',
        'UUDUUDUUUDDUUDUUDDDUUDDDUDDUUDDDDU',
        'UUDUUDUUUDDUUDUUDUDDDDUUDDUDDDUUDD',
        'UUDUUDUUUDDUUDUUDUDDUDDUUDDDUDDUDD',
        'UUDUUUUUUUDUUUUUDDDUDDDDDDDUDDDDDU',
        'UUDUUUUUUUDUUUUUDUDDDDDUDDDDDDDUDD',
        'UUUDUDUDUDUDUDUUUDDDUDUDUDUDUDUDDD',
        'UUUDUUUDUUUDUUUUUDDDDDUDDDUDDDUDDD',
        'UUUDUUUDUUUDUUUUUDDDUDDDUDDDUDDDDD',
        'UUUUUDUUUDUUUDUUUDDDDDUDDDUDDDUDDD',
        'UUUUUDUUUDUUUDUUUDDDUDDDUDDDUDDDDD',
        'UUUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDDD'
    )

    centers_step52_777 = (
        9, 11, 13, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 37, 39, 41, # Upper
        254, 256, 258, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 282, 284, 286, # Down
    )

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step52.txt',
            self.state_targets,
            linecount=24010000,
            max_depth=11,
            filesize=1992830000)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step52.hash-cost-only.txt',
            self.state_targets,
            linecount=24010000,
            max_depth=11,
            bucketcount=48020003,
            filesize=48020004)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.centers_step52_777])
        return result


class LookupTableIDA777Step50(LookupTableIDA):
    """
    lookup-table-7x7x7-step50.txt
    =============================
    1 steps has 250 entries (0 percent, 0.00x previous step)
    2 steps has 1,981 entries (0 percent, 7.92x previous step)
    3 steps has 15,782 entries (0 percent, 7.97x previous step)
    4 steps has 123,053 entries (1 percent, 7.80x previous step)
    5 steps has 931,072 entries (11 percent, 7.57x previous step)
    6 steps has 6,799,621 entries (86 percent, 7.30x previous step)

    Total: 7,871,759 entries
    """

    state_targets = (
        'DDUDDDDUDDDDUDDDDUDDDDUDDUUDUUUUDUUUUDUUUUDUUUUDUU',
        'DDUDUDDUDUDDUDUDDUDUDDUDUDUDUUDUDUUDUDUUDUDUUDUDUU',
        'DDUDUDDUDUDDUDUDDUDUDDUDUUUDUDUUDUDUUDUDUUDUDUUDUD',
        'DDUUDDDUUDDDUUDDDUUDDDUUDUDDUUUDDUUUDDUUUDDUUUDDUU',
        'DDUUDDDUUDDDUUDDDUUDDDUUDUUDDUUUDDUUUDDUUUDDUUUDDU',
        'DDUUUDDUUUDDUUUDDUUUDDUUUDDDUUDDDUUDDDUUDDDUUDDDUU',
        'DDUUUDDUUUDDUUUDDUUUDDUUUDUDDUDUDDUDUDDUDUDDUDUDDU',
        'DDUUUDDUUUDDUUUDDUUUDDUUUUDDUDUDDUDUDDUDUDDUDUDDUD',
        'DDUUUDDUUUDDUUUDDUUUDDUUUUUDDDUUDDDUUDDDUUDDDUUDDD',
        'DUUDDDUUDDDUUDDDUUDDDUUDDUDDUUUDDUUUDDUUUDDUUUDDUU',
        'DUUDDDUUDDDUUDDDUUDDDUUDDUUDDUUUDDUUUDDUUUDDUUUDDU',
        'DUUDUDUUDUDUUDUDUUDUDUUDUDDDUUDDDUUDDDUUDDDUUDDDUU',
        'DUUDUDUUDUDUUDUDUUDUDUUDUDUDDUDUDDUDUDDUDUDDUDUDDU',
        'DUUDUDUUDUDUUDUDUUDUDUUDUUDDUDUDDUDUDDUDUDDUDUDDUD',
        'DUUDUDUUDUDUUDUDUUDUDUUDUUUDDDUUDDDUUDDDUUDDDUUDDD',
        'DUUUDDUUUDDUUUDDUUUDDUUUDUDDDUUDDDUUDDDUUDDDUUDDDU',
        'DUUUUDUUUUDUUUUDUUUUDUUUUDDDDUDDDDUDDDDUDDDDUDDDDU',
        'DUUUUDUUUUDUUUUDUUUUDUUUUUDDDDUDDDDUDDDDUDDDDUDDDD',
        'UDUDDUDUDDUDUDDUDUDDUDUDDDUDUUDUDUUDUDUUDUDUUDUDUU',
        'UDUDDUDUDDUDUDDUDUDDUDUDDUUDUDUUDUDUUDUDUUDUDUUDUD',
        'UDUDUUDUDUUDUDUUDUDUUDUDUDUDUDDUDUDDUDUDDUDUDDUDUD',
        'UDUUDUDUUDUDUUDUDUUDUDUUDDDDUUDDDUUDDDUUDDDUUDDDUU',
        'UDUUDUDUUDUDUUDUDUUDUDUUDDUDDUDUDDUDUDDUDUDDUDUDDU',
        'UDUUDUDUUDUDUUDUDUUDUDUUDUDDUDUDDUDUDDUDUDDUDUDDUD',
        'UDUUDUDUUDUDUUDUDUUDUDUUDUUDDDUUDDDUUDDDUUDDDUUDDD',
        'UDUUUUDUUUUDUUUUDUUUUDUUUDDDUDDDDUDDDDUDDDDUDDDDUD',
        'UDUUUUDUUUUDUUUUDUUUUDUUUDUDDDDUDDDDUDDDDUDDDDUDDD',
        'UUUDDUUUDDUUUDDUUUDDUUUDDDDDUUDDDUUDDDUUDDDUUDDDUU',
        'UUUDDUUUDDUUUDDUUUDDUUUDDDUDDUDUDDUDUDDUDUDDUDUDDU',
        'UUUDDUUUDDUUUDDUUUDDUUUDDUDDUDUDDUDUDDUDUDDUDUDDUD',
        'UUUDDUUUDDUUUDDUUUDDUUUDDUUDDDUUDDDUUDDDUUDDDUUDDD',
        'UUUDUUUUDUUUUDUUUUDUUUUDUDDDUDDDDUDDDDUDDDDUDDDDUD',
        'UUUDUUUUDUUUUDUUUUDUUUUDUDUDDDDUDDDDUDDDDUDDDDUDDD',
        'UUUUDUUUUDUUUUDUUUUDUUUUDDDDDUDDDDUDDDDUDDDDUDDDDU',
        'UUUUDUUUUDUUUUDUUUUDUUUUDUDDDDUDDDDUDDDDUDDDDUDDDD',
        'UUUUUUUUUUUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDDDDDDDDDDD'
    )

    centers_step50_777 = (
        9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, # Upper
        254, 255, 256, 257, 258, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 282, 283, 284, 285, 286, # Down
    )

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step50.txt',
            self.state_targets,
            moves_777,
            # illegal moves
            # keep all centers staged
            ("3Uw", "3Uw'", "Uw", "Uw'",
             "3Lw", "3Lw'", "Lw", "Lw'",
             "3Fw", "3Fw'", "Fw", "Fw'",
             "3Rw", "3Rw'", "Rw", "Rw'",
             "3Bw", "3Bw'", "Bw", "Bw'",
             "3Dw", "3Dw'", "Dw", "Dw'",

            # keep LR in vertical bars
            "L", "L'", "R", "R'", "3Uw2", "3Dw2", "Uw2", "Dw2"),

            # prune tables
            (parent.lt_step51,
             parent.lt_step52),
            linecount=7871759,
            max_depth=6,
            filesize=440818504)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.centers_step50_777])
        return result


#class LookupTable777Step61(LookupTable):
class LookupTable777Step61(LookupTableHashCostOnly):
    """
    lookup-table-7x7x7-step61.txt
    =============================
    1 steps has 9 entries (0 percent, 0.00x previous step)
    2 steps has 56 entries (0 percent, 6.22x previous step)
    3 steps has 340 entries (0 percent, 6.07x previous step)
    4 steps has 1,965 entries (0 percent, 5.78x previous step)
    5 steps has 11,406 entries (0 percent, 5.80x previous step)
    6 steps has 63,151 entries (0 percent, 5.54x previous step)
    7 steps has 315,410 entries (1 percent, 4.99x previous step)
    8 steps has 1,351,508 entries (5 percent, 4.28x previous step)
    9 steps has 4,368,424 entries (18 percent, 3.23x previous step)
    10 steps has 8,741,185 entries (36 percent, 2.00x previous step)
    11 steps has 7,463,440 entries (31 percent, 0.85x previous step)
    12 steps has 1,634,978 entries (6 percent, 0.22x previous step)
    13 steps has 57,824 entries (0 percent, 0.04x previous step)
    14 steps has 304 entries (0 percent, 0.01x previous step)

    Total: 24,010,000 entries
    Average: 10.11 moves
    """

    state_indexes = (
        108, 110, 114, 115, 116, 117, 118, 122, 123, 124, 128, 129, 130, 131, 132, 136, 138, # Front
        206, 208, 212, 213, 214, 215, 216, 220, 221, 222, 226, 227, 228, 229, 230, 234, 236, # Back
    )

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step61.txt',
            'FFFFFFFFFFFFFFFFFBBBBBBBBBBBBBBBBB',
            linecount=24010000,
            max_depth=14,
            filesize=2280950000)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step61.hash-cost-only.txt',
            'FFFFFFFFFFFFFFFFFBBBBBBBBBBBBBBBBB',
            linecount=24010000,
            max_depth=14,
            bucketcount=48020003,
            filesize=48020004)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.state_indexes])
        return result


#class LookupTable777Step62(LookupTable):
class LookupTable777Step62(LookupTableHashCostOnly):
    """
    lookup-table-7x7x7-step62.txt
    =============================
    1 steps has 9 entries (0 percent, 0.00x previous step)
    2 steps has 68 entries (0 percent, 7.56x previous step)
    3 steps has 464 entries (0 percent, 6.82x previous step)
    4 steps has 3,080 entries (0 percent, 6.64x previous step)
    5 steps has 19,660 entries (0 percent, 6.38x previous step)
    6 steps has 113,360 entries (0 percent, 5.77x previous step)
    7 steps has 580,520 entries (2 percent, 5.12x previous step)
    8 steps has 2,435,981 entries (10 percent, 4.20x previous step)
    9 steps has 7,101,166 entries (29 percent, 2.92x previous step)
    10 steps has 9,808,434 entries (40 percent, 1.38x previous step)
    11 steps has 3,691,124 entries (15 percent, 0.38x previous step)
    12 steps has 252,402 entries (1 percent, 0.07x previous step)
    13 steps has 3,732 entries (0 percent, 0.01x previous step)

    Total: 24,010,000 entries
    Average: 9.58 moves
    """

    state_indexes = (
        107, 109, 111, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 135, 137, 139, # Front
        205, 207, 209, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 233, 235, 237, # Back
    )

    def __init__(self, parent):
        '''
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step62.txt',
            'FFFFFFFFFFFFFFFFFBBBBBBBBBBBBBBBBB',
            linecount=24010000,
            max_depth=13,
            filesize=)
        '''
        LookupTableHashCostOnly.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step62.hash-cost-only.txt',
            'FFFFFFFFFFFFFFFFFBBBBBBBBBBBBBBBBB',
            linecount=24010000,
            max_depth=13,
            bucketcount=48020003,
            filesize=48020004)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.state_indexes])
        return result


class LookupTableIDA777Step60(LookupTableIDA):
    """
    lookup-table-7x7x7-step60.txt
    =============================
    1 steps has 9 entries (0 percent, 0.00x previous step)
    2 steps has 108 entries (0 percent, 12.00x previous step)
    3 steps has 1,192 entries (0 percent, 11.04x previous step)
    4 steps has 12,762 entries (0 percent, 10.71x previous step)
    5 steps has 133,624 entries (0 percent, 10.47x previous step)
    6 steps has 1,382,900 entries (8 percent, 10.35x previous step)
    7 steps has 13,876,960 entries (90 percent, 10.03x previous step)

    Total: 15,407,555 entries
    """

    state_indexes = (
        9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, # Upper
        58, 59, 60, 61, 62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 86, 87, 88, 89, 90, # Left
        107, 108, 109, 110, 111, 114, 115, 116, 117, 118, 121, 122, 123, 124, 125, 128, 129, 130, 131, 132, 135, 136, 137, 138, 139, # Front
        156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188, # Right
        205, 206, 207, 208, 209, 212, 213, 214, 215, 216, 219, 220, 221, 222, 223, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237, # Back
        254, 255, 256, 257, 258, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 282, 283, 284, 285, 286, # Down
    )

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-7x7x7-step60.txt',
            'UUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDDDDDDDDDDD',
            moves_777,

            # illegal moves
            # keep all centers staged
            ("3Uw", "3Uw'", "Uw", "Uw'",
             "3Lw", "3Lw'", "Lw", "Lw'",
             "3Fw", "3Fw'", "Fw", "Fw'",
             "3Rw", "3Rw'", "Rw", "Rw'",
             "3Bw", "3Bw'", "Bw", "Bw'",
             "3Dw", "3Dw'", "Dw", "Dw'",

            # keep LR in horizontal bars
            "L", "L'", "R", "R'", "3Fw2", "3Bw2", "Fw2", "Bw2",

            # keep UD in vertical bars
            "U", "U'", "D", "D'"),

            # prune tables
            (parent.lt_step61,
             parent.lt_step62),
            linecount=15407555,
            max_depth=7,
            filesize=2403578580)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in self.state_indexes])
        return result


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

    instantiated = False

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCubeNNNOddEdges.__init__(self, state, order, colormap, debug)

        if RubiksCube777.instantiated:
            #raise Exception("Another 7x7x7 instance is being created")
            log.warning("Another 7x7x7 instance is being created")
        else:
            RubiksCube777.instantiated = True

    def get_fake_666(self):
        if self.fake_666 is None:
            self.fake_666 = RubiksCube666(solved_666, 'URFDLB')
            self.fake_666.lt_init()
        else:
            self.fake_666.re_init()
        return self.fake_666

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
        self.lt_UD_oblique_edge_pairing_middle_only.preload_cache()
        self.lt_UD_oblique_edge_pairing_left_only.preload_cache()
        self.lt_UD_oblique_edge_pairing_right_only.preload_cache()
        self.lt_UD_oblique_edge_pairing.preload_cache()

        self.lt_LR_outside_oblique_edge_pairing = LookupTable777LROutsideObliqueEdgePairing(self)
        self.lt_LR_left_middle_oblique_edge_pairing = LookupTable777LRLeftMiddleObliqueEdgePairing(self)
        self.lt_LR_right_middle_oblique_edge_pairing = LookupTable777LRRightMiddleObliqueEdgePairing(self)
        self.lt_LR_oblique_edge_pairing_inadmissible = LookupTable777LRObliqueEdgePairingInadmisibble(self)
        self.lt_LR_oblique_edge_pairing = LookupTableIDA777LRObliqueEdgePairing(self)
        self.lt_LR_oblique_edge_pairing.preload_cache()

        self.lt_step41 = LookupTable777Step41(self)
        self.lt_step42 = LookupTable777Step42(self)
        self.lt_step40 = LookupTableIDA777Step40(self)
        self.lt_step40.preload_cache()

        self.lt_step51 = LookupTable777Step51(self)
        self.lt_step52 = LookupTable777Step52(self)
        self.lt_step50 = LookupTableIDA777Step50(self)
        self.lt_step50.preload_cache()

        self.lt_step61 = LookupTable777Step61(self)
        self.lt_step62 = LookupTable777Step62(self)
        self.lt_step60 = LookupTableIDA777Step60(self)
        self.lt_step60.preload_cache()

    def create_fake_555_from_inside_centers(self):

        # Create a fake 5x5x5 to stage the UD inner 5x5x5 centers
        fake_555 = self.get_fake_555()
        fake_555.nuke_corners()
        fake_555.nuke_edges()
        fake_555.nuke_centers()

        for side_index in range(6):
            offset_555 = side_index * 25
            offset_777 = side_index * 49
            fake_555.state[7 + offset_555] = self.state[17 + offset_777]
            fake_555.state[8 + offset_555] = self.state[18 + offset_777]
            fake_555.state[9 + offset_555] = self.state[19 + offset_777]
            fake_555.state[12 + offset_555] = self.state[24 + offset_777]
            fake_555.state[13 + offset_555] = self.state[25 + offset_777]
            fake_555.state[14 + offset_555] = self.state[26 + offset_777]
            fake_555.state[17 + offset_555] = self.state[31 + offset_777]
            fake_555.state[18 + offset_555] = self.state[32 + offset_777]
            fake_555.state[19 + offset_555] = self.state[33 + offset_777]

    def create_fake_555_from_outside_centers(self):

        # Create a fake 5x5x5 to solve 7x7x7 centers (they have been reduced to a 5x5x5)
        fake_555 = self.get_fake_555()
        fake_555.nuke_corners()
        fake_555.nuke_edges()
        fake_555.nuke_centers()

        for side_index in range(6):
            offset_555 = side_index * 25
            offset_777 = side_index * 49
            fake_555.state[7 + offset_555] = self.state[9 + offset_777]
            fake_555.state[8 + offset_555] = self.state[11 + offset_777]
            fake_555.state[9 + offset_555] = self.state[13 + offset_777]
            fake_555.state[12 + offset_555] = self.state[23 + offset_777]
            fake_555.state[13 + offset_555] = self.state[25 + offset_777]
            fake_555.state[14 + offset_555] = self.state[27 + offset_777]
            fake_555.state[17 + offset_555] = self.state[37 + offset_777]
            fake_555.state[18 + offset_555] = self.state[39 + offset_777]
            fake_555.state[19 + offset_555] = self.state[41 + offset_777]

    def UD_inside_centers_staged(self):
        state = self.state

        for x in (17, 18, 19, 24, 25, 26, 31, 32, 33,
                  262, 263, 264, 269, 270, 271, 276, 277, 278):
            if state[x] not in ('U', 'D'):
                return False
        return True

    def group_inside_UD_centers(self):

        if self.UD_inside_centers_staged():
            return

        self.create_fake_555_from_inside_centers()
        self.fake_555.group_centers_stage_UD()

        for step in self.fake_555.solution:

            if step.startswith('5'):
                step = '7' + step[1:]
            elif step.startswith('3'):
                step = '4' + step[1:]
            elif 'w' in step:
                step = '3' + step

            self.rotate(step)

    def LR_inside_centers_staged(self):
        state = self.state

        for x in (66, 67, 68, 73, 74, 75, 80, 81, 82,
                  164, 165, 166, 171, 172, 173, 178, 179, 180):
            if state[x] not in ('L', 'R'):
                return False
        return True

    def group_inside_LR_centers(self):

        if self.LR_inside_centers_staged():
            return

        self.create_fake_555_from_inside_centers()
        self.fake_555.lt_LR_centers_stage.solve()

        for step in self.fake_555.solution:

            if step.startswith('5'):
                step = '7' + step[1:]
            elif step.startswith('3'):
                raise Exception("5x5x5 solution has 3 wide turn")
            elif 'w' in step:
                step = '3' + step

            self.rotate(step)

    def solve_reduced_555_centers(self):
        # TODO remove this
        self.create_fake_555_from_outside_centers()
        self.fake_555.group_centers()

        for step in self.fake_555.solution:

            if step == 'CENTERS_SOLVED':
                continue

            if step.startswith('5'):
                step = '7' + step[1:]

            elif step.startswith('3'):
                raise Exception("5x5x5 solution has 3 wide turn")

            self.rotate(step)

    def create_fake_666_centers(self):

        # Create a fake 6x6x6 to stage the outside UD oblique edges
        fake_666 = self.get_fake_666()

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

    def group_outside_UD_oblique_edges(self):
        self.create_fake_666_centers()
        self.fake_666.stage_UD_oblique_edges()

        for step in self.fake_666.solution:

            if step.startswith('6'):
                step = '7' + step[1:]

            self.rotate(step)

        self.rotate_U_to_U()
        self.rotate_F_to_F()

    def group_centers_guts(self):
        self.lt_init()

        # Uses 5x5x5 solver to stage the inner x-centers and inner t-centers for UD
        if not self.UD_centers_staged():
            self.group_inside_UD_centers()
            self.print_cube()
            log.info("%s: UD inner x-centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")
            log.info("")
            log.info("")
            log.info("")

            # Uses 6x6x6 solver to pair the "outside" oblique edges for UD
            self.group_outside_UD_oblique_edges()
            self.print_cube()
            log.info("%s: UD oblique edges (outside only) staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")
            log.info("")
            log.info("")
            log.info("")

            # Test the prune tables
            #self.lt_UD_oblique_edge_pairing_middle_only.solve()
            #self.lt_UD_oblique_edge_pairing_left_only.solve()
            #self.lt_UD_oblique_edge_pairing_right_only.solve()
            #self.print_cube()

            # Now stage the "inside" oblique UD edges with the already staged outside oblique UD edges
            self.lt_UD_oblique_edge_pairing.solve()
            self.print_cube()
            log.info("%s: UD oblique edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")
            log.info("")
            log.info("")
            log.info("")

            # Stage the UD centers
            self.create_fake_555_from_outside_centers()
            self.fake_555.group_centers_stage_UD()

            for step in self.fake_555.solution:
                if step.startswith('5'):
                    step = '7' + step[1:]
                elif step.startswith('3'):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

            self.print_cube()
            log.info("%s: UD centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")
            log.info("")
            log.info("")
            log.info("")

        if not self.LR_centers_staged():
            # Uses 5x5x5 solver to stage the inner x-centers
            self.group_inside_LR_centers()
            self.print_cube()
            log.info("%s: LR inner x-centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")
            log.info("")
            log.info("")
            log.info("")

            # Test the pruning tables
            #self.lt_LR_outside_oblique_edge_pairing.solve()
            #self.lt_LR_left_middle_oblique_edge_pairing.solve()
            #self.print_cube()
            #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            #sys.exit(0)

            self.lt_LR_oblique_edge_pairing.solve()
            self.print_cube()
            log.info("%s: LR oblique edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

            # Stage the LR centers
            self.create_fake_555_from_outside_centers()
            self.fake_555.group_centers_stage_LR()

            for step in self.fake_555.solution:
                if step.startswith('5'):
                    step = '7' + step[1:]
                elif step.startswith('3'):
                    raise Exception("5x5x5 solution has 3 wide turn")
                self.rotate(step)

            self.print_cube()
            log.info("%s: centers staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")
            log.info("")
            log.info("")
            log.info("")

        # Test the pruning tables
        #self.lt_step41.solve()
        #self.lt_step42.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        log.info("kociemba: %s" % self.get_kociemba_string(True))
        self.lt_step40.solve()
        self.print_cube()
        log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: LR centers vertical bars, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Test the pruning tables
        #self.lt_step51.solve()
        #self.lt_step52.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        self.lt_step50.solve()

        # Make the LR bars horizontal for the next phase
        self.rotate("L")
        self.rotate("R")
        self.print_cube()
        log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: LR centers horizontal bars, UD centers vertical bars, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # Test the pruning tables
        #self.lt_step61.solve()
        #self.lt_step62.solve()
        #self.print_cube()
        #log.info("%s: %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        #sys.exit(0)

        self.lt_step60.solve()
        self.print_cube()
        log.info("%s: centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))



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
