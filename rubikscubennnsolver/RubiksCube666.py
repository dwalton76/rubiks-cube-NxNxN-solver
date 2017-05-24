
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis
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


class RubiksCube666(RubiksCube):
    """
    6x6x6 strategy
    - stage UD centers to sides U or D (use IDA)
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3
    """

    def __init__(self, kociemba_string, debug=False):
        RubiksCube.__init__(self, kociemba_string)

        if debug:
            log.setLevel(logging.DEBUG)

    def lt_init(self):
        '''
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
        '''
        self.lt_UD_inner_x_centers_stage = LookupTable(self,
                                                      'lookup-table-6x6x6-step10-UD-inner-x-centers-stage.txt',
                                                      '666-UD-inner-X-centers-stage',
                                                      '066000000000000000000660',
                                                      True) # state_hex

        '''
        Now pair the UD oblique edges so that we can reduce the 6x6x6 centers to a 5x5x5
        (24!/(8!*16!))^2 is 540,917,591,841 so this is too large for us to build so use
        IDA and build it 8 steps deep.

        Our prune tables will be to solve on the left or right oblique edges. Each of these
        tables are 24!/(8!*16!) or 735,471
        735471/540917591841 is 0.0000013596729171

        lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt
        =====================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 82 entries (0 percent, 16.40x previous step)
        3 steps has 1,434 entries (0 percent, 17.49x previous step)
        4 steps has 24,198 entries (0 percent, 16.87x previous step)
        5 steps has 405,916 entries (0 percent, 16.77x previous step)
        6 steps has 6,839,392 entries (5 percent, 16.85x previous step)
        7 steps has 116,031,874 entries (94 percent, 16.97x previous step)

        Total: 123,302,901 entries


        lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt
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
        '''
        self.lt_UD_oblique_edge_pairing_left_only = LookupTable(self,
                                                                'lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt',
                                                                '666-UD-oblique-edge-pairing-left-only',
                                                                '990000000099',
                                                                True) # state_hex

        self.lt_UD_oblique_edge_pairing_right_only = LookupTable(self,
                                                                'lookup-table-6x6x6-step22-UD-oblique-edge-pairing-right-only.txt',
                                                                '666-UD-oblique-edge-pairing-right-only',
                                                                '660000000066',
                                                                True) # state_hex

        self.lt_UD_oblique_edge_pairing = LookupTableIDA(self,
                                                         'lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt',
                                                         '666-UD-oblique-edge-pairing',

                                                         # xUUxUxxUUxxUxUUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxUUxUxxUUxxUxUUx
                                                         'ff00000000ff',

                                                         True, # state_hex
                                                         moves_6x6x6,

                                                         # These would break up the staged UD inner x-centers
                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'"),

                                                         # prune tables
                                                         (self.lt_UD_oblique_edge_pairing_left_only,
                                                          self.lt_UD_oblique_edge_pairing_right_only))
        '''
        16!/(8!*8!) is 12,870

        lookup-table-6x6x6-step30-LR-inner-x-centers-stage.txt
        ======================================================
        1 steps has 3 entries (0 percent)
        2 steps has 29 entries (0 percent)
        3 steps has 234 entries (1 percent)
        4 steps has 1,246 entries (9 percent)
        5 steps has 4,466 entries (34 percent)
        6 steps has 6,236 entries (48 percent)
        7 steps has 656 entries (5 percent)

        Total: 12,870 entries
        '''
        self.lt_LR_inner_x_centers_stage = LookupTable(self,
                                                      'lookup-table-6x6x6-step30-LR-inner-x-centers-stage.txt',
                                                      '666-LR-inner-X-centers-stage',
                                                      '000006600000066000000000',
                                                      True) # state_hex

        '''
        (16!/(8!*8!))^2 is 165,636,900

        lookup-table-6x6x6-step40-LR-oblique-pairing.txt
        ================================================
        1 steps has 3 entries (0 percent)
        2 steps has 29 entries (0 percent)
        3 steps has 286 entries (0 percent)
        4 steps has 2,052 entries (0 percent)
        5 steps has 16,348 entries (0 percent)
        6 steps has 127,859 entries (0 percent)
        7 steps has 844,248 entries (0 percent)
        8 steps has 4,623,585 entries (2 percent)
        9 steps has 19,019,322 entries (11 percent)
        10 steps has 47,544,426 entries (28 percent)
        11 steps has 61,805,656 entries (37 percent)
        12 steps has 28,890,234 entries (17 percent)
        13 steps has 2,722,462 entries (1 percent)
        14 steps has 40,242 entries (0 percent)
        15 steps has 148 entries (0 percent)

        Total: 165,636,900 entries
        '''
        self.lt_LR_oblique_edge_pairing = LookupTable(self,
                                                      'lookup-table-6x6x6-step40-LR-oblique-pairing.txt',
                                                      '666-LR-oblique-edge-pairing',
                                                      'ff00ff00',
                                                      True) # state_hex

        '''
        lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt
        ========================================================================
        1 steps has 9 entries (0 percent, 0.00x previous step)
        2 steps has 47 entries (0 percent, 5.22x previous step)
        3 steps has 232 entries (0 percent, 4.94x previous step)
        4 steps has 1,001 entries (0 percent, 4.31x previous step)
        5 steps has 4,266 entries (1 percent, 4.26x previous step)
        6 steps has 16,697 entries (4 percent, 3.91x previous step)
        7 steps has 52,894 entries (15 percent, 3.17x previous step)
        8 steps has 114,134 entries (33 percent, 2.16x previous step)
        9 steps has 113,888 entries (33 percent, 1.00x previous step)
        10 steps has 37,136 entries (10 percent, 0.33x previous step)
        11 steps has 2,696 entries (0 percent, 0.07x previous step)

        Total: 343,000 entries
        '''
        self.lt_UD_solve_inner_x_centers_and_oblique_edges = LookupTable(self,
                                                                         'lookup-table-6x6x6-step50-UD-solve-inner-x-center-and-oblique-edges.txt',
                                                                         'UD-centers-oblique-edges-solve',
                                                                         'xUUxUUUUUUUUxUUxxDDxDDDDDDDDxDDx',
                                                                         False) # state_hex

        '''
        lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt
        ========================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 86 entries (0 percent, 3.31x previous step)
        4 steps has 356 entries (0 percent, 4.14x previous step)
        5 steps has 1,186 entries (0 percent, 3.33x previous step)
        6 steps has 4,264 entries (1 percent, 3.60x previous step)
        7 steps has 12,946 entries (3 percent, 3.04x previous step)
        8 steps has 35,741 entries (10 percent, 2.76x previous step)
        9 steps has 77,322 entries (22 percent, 2.16x previous step)
        10 steps has 111,116 entries (32 percent, 1.44x previous step)
        11 steps has 80,988 entries (23 percent, 0.73x previous step)
        12 steps has 18,436 entries (5 percent, 0.23x previous step)
        13 steps has 528 entries (0 percent, 0.03x previous step)

        Total: 343,000 entries
        '''
        self.lt_LR_solve_inner_x_centers_and_oblique_edges = LookupTable(self,
                                                                         'lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt',
                                                                         'LR-centers-oblique-edges-solve',
                                                                         'xLLxLLLLLLLLxLLxxRRxRRRRRRRRxRRx',
                                                                         False) # state_hex

        '''
        lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt
        ========================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 86 entries (0 percent, 3.31x previous step)
        4 steps has 356 entries (0 percent, 4.14x previous step)
        5 steps has 1,186 entries (0 percent, 3.33x previous step)
        6 steps has 4,264 entries (1 percent, 3.60x previous step)
        7 steps has 12,946 entries (3 percent, 3.04x previous step)
        8 steps has 35,741 entries (10 percent, 2.76x previous step)
        9 steps has 77,322 entries (22 percent, 2.16x previous step)
        10 steps has 111,116 entries (32 percent, 1.44x previous step)
        11 steps has 80,988 entries (23 percent, 0.73x previous step)
        12 steps has 18,436 entries (5 percent, 0.23x previous step)
        13 steps has 528 entries (0 percent, 0.03x previous step)

        Total: 343,000 entries
        '''
        self.lt_FB_solve_inner_x_centers_and_oblique_edges = LookupTable(self,
                                                                         'lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.txt',
                                                                         'FB-centers-oblique-edges-solve',
                                                                         'xFFxFFFFFFFFxFFxxBBxBBBBBBBBxBBx',
                                                                         False) # state_hex

        '''
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
        '''
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges = LookupTableIDA(self,
                                                         'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt',
                                                         'LFRB-centers-oblique-edges-solve',
                                                         'xLLxLLLLLLLLxLLxxFFxFFFFFFFFxFFxxRRxRRRRRRRRxRRxxBBxBBBBBBBBxBBx',

                                                         False, # state_hex
                                                         moves_6x6x6,

                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
                                                          "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
                                                          "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2"),                              # do not mess up solved UD

                                                         # prune tables
                                                         (self.lt_LR_solve_inner_x_centers_and_oblique_edges,
                                                          self.lt_FB_solve_inner_x_centers_and_oblique_edges))

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

    def group_centers_guts(self):
        self.lt_init()
        self.lt_UD_inner_x_centers_stage.solve()

        # These are our two prune tables so if we go ahead and solve for one of them we
        # get the cube in a state that is much closer to being a match for the table we
        # are doing an IDA search against.
        #
        # This isn't technically required but it makes a HUGE difference in how fast we
        # can find a solution...like 160s vs 10s kind of difference.
        #self.lt_UD_oblique_edge_pairing_left_only.solve()
        self.lt_UD_oblique_edge_pairing_right_only.solve()
        self.lt_UD_oblique_edge_pairing.solve()
        self.lt_LR_inner_x_centers_stage.solve()
        self.lt_LR_oblique_edge_pairing.solve()
        log.info("inner x-center and oblique edges staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        #self.print_cube()

        # dwalton reference for 7x7x7

        # Reduce the centers to 5x5x5 centers
        # - solve the UD centers and pair the UD oblique edges
        # - solve the LR centers and pair the LR oblique edges
        # - solve the FB centers and pair the FB oblique edges
        self.lt_UD_solve_inner_x_centers_and_oblique_edges.solve()
        log.info("UD inner x-center and oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        #self.print_cube()

        self.lt_LR_solve_inner_x_centers_and_oblique_edges.solve()
        #self.lt_FB_solve_inner_x_centers_and_oblique_edges.solve()
        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.solve()
        log.info("LRFB inner x-center and oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        # self.print_cube()

        # At this point the 6x6x6 centers have been reduced to 5x5x5 centers
        fake_555 = RubiksCube555(solved_5x5x5)
        fake_555.lt_init()
        self.populate_fake_555_for_ULFRBD(fake_555)
        #fake_555.print_cube()
        fake_555.group_centers_guts()

        for step in fake_555.solution:
            self.rotate(step)

        log.info("Took %d steps to solve centers" % self.get_solution_len_minus_rotates(self.solution))
        # self.print_cube()

    def pair_inside_edges(self):
        fake_444 = RubiksCube444(solved_4x4x4)
        fake_444.lt_init()

        # The corners don't matter but it does make troubleshooting easier if they match
        '''
        fake_444.state[1] = self.state[1]
        fake_444.state[4] = self.state[6]
        fake_444.state[13] = self.state[31]
        fake_444.state[16] = self.state[36]
        fake_444.state[17] = self.state[37]
        fake_444.state[20] = self.state[42]
        fake_444.state[29] = self.state[67]
        fake_444.state[32] = self.state[72]
        fake_444.state[33] = self.state[73]
        fake_444.state[36] = self.state[78]
        fake_444.state[45] = self.state[103]
        fake_444.state[48] = self.state[108]
        fake_444.state[49] = self.state[109]
        fake_444.state[52] = self.state[114]
        fake_444.state[61] = self.state[139]
        fake_444.state[64] = self.state[144]
        fake_444.state[65] = self.state[145]
        fake_444.state[68] = self.state[150]
        fake_444.state[77] = self.state[175]
        fake_444.state[80] = self.state[180]
        fake_444.state[81] = self.state[181]
        fake_444.state[84] = self.state[186]
        fake_444.state[93] = self.state[211]
        fake_444.state[96] = self.state[216]
        '''

        # Upper
        fake_444.state[2] = self.state[3]
        fake_444.state[3] = self.state[4]
        fake_444.state[5] = self.state[13]
        fake_444.state[8] = self.state[18]
        fake_444.state[9] = self.state[19]
        fake_444.state[12] = self.state[24]
        fake_444.state[14] = self.state[33]
        fake_444.state[15] = self.state[34]

        # Left
        fake_444.state[18] = self.state[39]
        fake_444.state[19] = self.state[40]
        fake_444.state[21] = self.state[49]
        fake_444.state[24] = self.state[54]
        fake_444.state[25] = self.state[55]
        fake_444.state[28] = self.state[60]
        fake_444.state[30] = self.state[69]
        fake_444.state[31] = self.state[70]

        # Front
        fake_444.state[34] = self.state[75]
        fake_444.state[35] = self.state[76]
        fake_444.state[37] = self.state[85]
        fake_444.state[40] = self.state[90]
        fake_444.state[41] = self.state[91]
        fake_444.state[44] = self.state[96]
        fake_444.state[46] = self.state[105]
        fake_444.state[47] = self.state[106]

        # Right
        fake_444.state[50] = self.state[111]
        fake_444.state[51] = self.state[112]
        fake_444.state[53] = self.state[121]
        fake_444.state[56] = self.state[126]
        fake_444.state[57] = self.state[127]
        fake_444.state[60] = self.state[132]
        fake_444.state[62] = self.state[141]
        fake_444.state[63] = self.state[142]

        # Back
        fake_444.state[66] = self.state[147]
        fake_444.state[67] = self.state[148]
        fake_444.state[69] = self.state[157]
        fake_444.state[72] = self.state[162]
        fake_444.state[73] = self.state[163]
        fake_444.state[76] = self.state[168]
        fake_444.state[78] = self.state[177]
        fake_444.state[79] = self.state[178]

        # Down
        fake_444.state[82] = self.state[183]
        fake_444.state[83] = self.state[184]
        fake_444.state[85] = self.state[193]
        fake_444.state[88] = self.state[198]
        fake_444.state[89] = self.state[199]
        fake_444.state[92] = self.state[204]
        fake_444.state[94] = self.state[213]
        fake_444.state[95] = self.state[214]

        fake_444.group_edges()

        for step in fake_444.solution:
            if step == 'EDGES_GROUPED':
                continue

            if step.startswith('4'):
                step = '6' + step[1:]
            elif step.startswith('3'):
                raise ImplementThis('4x4x4 steps starts with 3')
            elif step.startswith('Uw') or step.startswith('Dw'):
                step = '3' + step

            # log.warning("fake_444 step %s" % step)
            self.rotate(step)

        self.print_cube()
        log.warning("Inside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def pair_edges_via_555(self):
        fake_555 = RubiksCube555(solved_5x5x5)
        fake_555.lt_init()

        # The corners don't matter but it does make troubleshooting easier if they match
        '''
        fake_555.state[1] = self.state[1]
        fake_555.state[5] = self.state[6]
        fake_555.state[21] = self.state[31]
        fake_555.state[25] = self.state[36]
        fake_555.state[26] = self.state[37]
        fake_555.state[30] = self.state[42]
        fake_555.state[46] = self.state[67]
        fake_555.state[50] = self.state[72]
        fake_555.state[51] = self.state[73]
        fake_555.state[55] = self.state[78]
        fake_555.state[71] = self.state[103]
        fake_555.state[75] = self.state[108]
        fake_555.state[76] = self.state[109]
        fake_555.state[80] = self.state[114]
        fake_555.state[96] = self.state[139]
        fake_555.state[100] = self.state[144]
        fake_555.state[101] = self.state[145]
        fake_555.state[105] = self.state[150]
        fake_555.state[121] = self.state[175]
        fake_555.state[125] = self.state[180]
        fake_555.state[126] = self.state[181]
        fake_555.state[130] = self.state[186]
        fake_555.state[146] = self.state[211]
        fake_555.state[150] = self.state[216]
        '''

        # Upper
        fake_555.state[2] = self.state[2]
        fake_555.state[3] = self.state[3]
        fake_555.state[4] = self.state[5]
        fake_555.state[6] = self.state[7]
        fake_555.state[10] = self.state[12]
        fake_555.state[11] = self.state[13]
        fake_555.state[15] = self.state[18]
        fake_555.state[16] = self.state[25]
        fake_555.state[20] = self.state[30]
        fake_555.state[22] = self.state[32]
        fake_555.state[23] = self.state[33]
        fake_555.state[24] = self.state[35]

        # Left
        fake_555.state[27] = self.state[38]
        fake_555.state[28] = self.state[39]
        fake_555.state[29] = self.state[41]
        fake_555.state[31] = self.state[43]
        fake_555.state[35] = self.state[48]
        fake_555.state[36] = self.state[49]
        fake_555.state[40] = self.state[54]
        fake_555.state[41] = self.state[61]
        fake_555.state[45] = self.state[66]
        fake_555.state[47] = self.state[68]
        fake_555.state[48] = self.state[69]
        fake_555.state[49] = self.state[71]

        # Front
        fake_555.state[52] = self.state[74]
        fake_555.state[53] = self.state[75]
        fake_555.state[54] = self.state[77]
        fake_555.state[56] = self.state[79]
        fake_555.state[60] = self.state[84]
        fake_555.state[61] = self.state[85]
        fake_555.state[65] = self.state[90]
        fake_555.state[66] = self.state[97]
        fake_555.state[70] = self.state[102]
        fake_555.state[72] = self.state[104]
        fake_555.state[73] = self.state[105]
        fake_555.state[74] = self.state[107]

        # Right
        fake_555.state[77] = self.state[110]
        fake_555.state[78] = self.state[111]
        fake_555.state[79] = self.state[113]
        fake_555.state[81] = self.state[115]
        fake_555.state[85] = self.state[120]
        fake_555.state[86] = self.state[121]
        fake_555.state[90] = self.state[126]
        fake_555.state[91] = self.state[133]
        fake_555.state[95] = self.state[138]
        fake_555.state[97] = self.state[140]
        fake_555.state[98] = self.state[141]
        fake_555.state[99] = self.state[143]

        # Back
        fake_555.state[102] = self.state[146]
        fake_555.state[103] = self.state[147]
        fake_555.state[104] = self.state[149]
        fake_555.state[106] = self.state[151]
        fake_555.state[110] = self.state[156]
        fake_555.state[111] = self.state[157]
        fake_555.state[115] = self.state[162]
        fake_555.state[116] = self.state[169]
        fake_555.state[120] = self.state[174]
        fake_555.state[122] = self.state[176]
        fake_555.state[123] = self.state[177]
        fake_555.state[124] = self.state[179]

        # Down
        fake_555.state[127] = self.state[182]
        fake_555.state[128] = self.state[183]
        fake_555.state[129] = self.state[185]
        fake_555.state[131] = self.state[187]
        fake_555.state[135] = self.state[192]
        fake_555.state[136] = self.state[193]
        fake_555.state[140] = self.state[198]
        fake_555.state[141] = self.state[205]
        fake_555.state[145] = self.state[210]
        fake_555.state[147] = self.state[212]
        fake_555.state[148] = self.state[213]
        fake_555.state[149] = self.state[215]

        #self.print_cube()
        #fake_555.print_cube()
        fake_555.group_edges()

        for step in fake_555.solution:
            if step == 'EDGES_GROUPED':
                continue

            if step.startswith('5'):
                step = '6' + step[1:]
            elif step.startswith('3'):
                step = '4' + step[1:]

            self.rotate(step)

        self.print_cube()
        log.warning("Outside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def group_edges(self):
        """
        Create a fake 444 to pair the inside edges
        Create a fake 555 to pair the outside edges
        """
        self.pair_inside_edges()
        self.pair_edges_via_555()
        self.solution.append('EDGES_GROUPED')

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
