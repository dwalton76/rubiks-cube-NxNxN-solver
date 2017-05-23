
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis, steps_cancel_out, convert_state_to_hex
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
        lookup-table-6x6x6-step50-UD-centers-solve.txt
        ==============================================
        (8!/(4!*4!))^4 is 24,010,000

        1 steps has 9 entries (0 percent, 0.00x previous step)
        2 steps has 51 entries (0 percent, 5.67x previous step)
        3 steps has 312 entries (0 percent, 6.12x previous step)
        4 steps has 1,836 entries (0 percent, 5.88x previous step)
        5 steps has 10,304 entries (0 percent, 5.61x previous step)
        6 steps has 53,430 entries (0 percent, 5.19x previous step)
        7 steps has 260,212 entries (1 percent, 4.87x previous step)
        8 steps has 1,168,198 entries (4 percent, 4.49x previous step)
        9 steps has 4,332,400 entries (18 percent, 3.71x previous step)
        10 steps has 9,780,512 entries (40 percent, 2.26x previous step)
        11 steps has 7,457,368 entries (31 percent, 0.76x previous step)
        12 steps has 936,888 entries (3 percent, 0.13x previous step)
        13 steps has 8,480 entries (0 percent, 0.01x previous step)

        Total: 24,010,000 entries
        '''
        self.lt_UD_centers_solve = LookupTable(self,
                                               'lookup-table-6x6x6-step50-UD-centers-solve.txt',
                                               'UD-centers-solve',
                                               'UUUUUUUUUUUUUUUUDDDDDDDDDDDDDDDD',
                                               False) # state_hex


        '''
        lookup-table-6x6x6-step61-LR-centers-solve.txt
        ==============================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 94 entries (0 percent, 3.62x previous step)
        4 steps has 440 entries (0 percent, 4.68x previous step)
        5 steps has 1,680 entries (0 percent, 3.82x previous step)
        6 steps has 7,026 entries (0 percent, 4.18x previous step)
        7 steps has 26,072 entries (0 percent, 3.71x previous step)
        8 steps has 98,147 entries (0 percent, 3.76x previous step)
        9 steps has 349,870 entries (1 percent, 3.56x previous step)
        10 steps has 1,180,438 entries (4 percent, 3.37x previous step)
        11 steps has 3,429,688 entries (14 percent, 2.91x previous step)
        12 steps has 7,384,342 entries (30 percent, 2.15x previous step)
        13 steps has 8,471,512 entries (35 percent, 1.15x previous step)
        14 steps has 2,936,552 entries (12 percent, 0.35x previous step)
        15 steps has 123,980 entries (0 percent, 0.04x previous step)
        16 steps has 128 entries (0 percent, 0.00x previous step)

        Total: 24,010,000 entries
        '''
        self.lt_LR_centers_solve = LookupTable(self,
                                               'lookup-table-6x6x6-step61-LR-centers-solve.txt',
                                               'LR-centers-solve',
                                               'LLLLLLLLLLLLLLLLRRRRRRRRRRRRRRRR',
                                               False) # state_hex

        '''
        (8!/(4!*4!))^8 is 576,480,100,000,000 so we must use IDA
        24010000/576480100000000 is 0.0000000416493128

        lookup-table-6x6x6-step60-LFRB-centers-solve.txt
        ================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 54 entries (0 percent, 10.80x previous step)
        3 steps has 420 entries (0 percent, 7.78x previous step)
        4 steps has 2,903 entries (0 percent, 6.91x previous step)
        5 steps has 21,388 entries (0 percent, 7.37x previous step)
        6 steps has 145,567 entries (0 percent, 6.81x previous step)
        7 steps has 951,636 entries (2 percent, 6.54x previous step)
        8 steps has 6,082,238 entries (13 percent, 6.39x previous step)
        9 steps has 38,169,564 entries (84 percent, 6.28x previous step)

        Total: 45,373,775 entries


        lookup-table-6x6x6-step62-FB-centers-solve.txt
        ==============================================
        1 steps has 5 entries (0 percent)
        2 steps has 26 entries (0 percent)
        3 steps has 94 entries (0 percent)
        4 steps has 440 entries (0 percent)
        5 steps has 1,680 entries (0 percent)
        6 steps has 7,026 entries (0 percent)
        7 steps has 26,072 entries (0 percent)
        8 steps has 98,147 entries (0 percent)
        9 steps has 349,870 entries (1 percent)
        10 steps has 1,180,438 entries (4 percent)
        11 steps has 3,429,688 entries (14 percent)
        12 steps has 7,384,342 entries (30 percent)
        13 steps has 8,471,512 entries (35 percent)
        14 steps has 2,936,552 entries (12 percent)
        15 steps has 123,980 entries (0 percent)
        16 steps has 128 entries (0 percent)

        Total: 24,010,000 entries
        '''
        self.lt_FB_centers_solve = LookupTable(self,
                                               'lookup-table-6x6x6-step62-FB-centers-solve.txt',
                                               'FB-centers-solve',
                                               'FFFFFFFFFFFFFFFFBBBBBBBBBBBBBBBB',
                                               False) # state_hex

        self.lt_LFRB_centers_solve = LookupTableIDA(self,
                                                    'lookup-table-6x6x6-step60-LFRB-centers-solve.txt',
                                                    'LFRB-centers-solve',
                                                    'LLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBB',

                                                    False, # state_hex
                                                    moves_6x6x6,

                                                    ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
                                                     "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
                                                     "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2"),                              # do not mess up solved UD

                                                    # prune tables
                                                    (self.lt_LR_centers_solve,
                                                     self.lt_FB_centers_solve))

    def populate_fake_555_for_UD(self, fake_555):
        for x in range(1, 151):
            fake_555.state[x] = 'x'

        # The UD t-centers are staged
        fake_555.state[8] = "U"
        fake_555.state[12] = "U"
        fake_555.state[13] = "U"
        fake_555.state[14] = "U"
        fake_555.state[18] = "U"

        fake_555.state[133] = "U"
        fake_555.state[137] = "U"
        fake_555.state[138] = "U"
        fake_555.state[139] = "U"
        fake_555.state[143] = "U"

        # Upper
        if self.state[8] in ("U", "D"):
            fake_555.state[7] = "U"
        if self.state[11] in ("U", "D"):
            fake_555.state[9] = "U"
        if self.state[26] in ("U", "D"):
            fake_555.state[17] = "U"
        if self.state[29] in ("U", "D"):
            fake_555.state[19] = "U"

        # Left
        if self.state[44] in ("U", "D"):
            fake_555.state[32] = "U"
        if self.state[47] in ("U", "D"):
            fake_555.state[34] = "U"
        if self.state[62] in ("U", "D"):
            fake_555.state[42] = "U"
        if self.state[65] in ("U", "D"):
            fake_555.state[44] = "U"

        # Front
        if self.state[80] in ("U", "D"):
            fake_555.state[57] = "U"
        if self.state[83] in ("U", "D"):
            fake_555.state[59] = "U"
        if self.state[98] in ("U", "D"):
            fake_555.state[67] = "U"
        if self.state[101] in ("U", "D"):
            fake_555.state[69] = "U"

        # Right
        if self.state[116] in ("U", "D"):
            fake_555.state[82] = "U"
        if self.state[119] in ("U", "D"):
            fake_555.state[84] = "U"
        if self.state[134] in ("U", "D"):
            fake_555.state[92] = "U"
        if self.state[137] in ("U", "D"):
            fake_555.state[94] = "U"

        # Back
        if self.state[152] in ("U", "D"):
            fake_555.state[107] = "U"
        if self.state[155] in ("U", "D"):
            fake_555.state[109] = "U"
        if self.state[170] in ("U", "D"):
            fake_555.state[117] = "U"
        if self.state[173] in ("U", "D"):
            fake_555.state[119] = "U"

        # Down
        if self.state[188] in ("U", "D"):
            fake_555.state[132] = "U"
        if self.state[191] in ("U", "D"):
            fake_555.state[134] = "U"
        if self.state[206] in ("U", "D"):
            fake_555.state[142] = "U"
        if self.state[209] in ("U", "D"):
            fake_555.state[144] = "U"

    def populate_fake_555_for_LR(self, fake_555):
        for x in range(1, 151):
            fake_555.state[x] = 'x'

        # The LR t-centers are staged
        fake_555.state[33] = "L"
        fake_555.state[37] = "L"
        fake_555.state[38] = "L"
        fake_555.state[39] = "L"
        fake_555.state[43] = "L"

        fake_555.state[83] = "L"
        fake_555.state[87] = "L"
        fake_555.state[88] = "L"
        fake_555.state[89] = "L"
        fake_555.state[93] = "L"

        # Upper
        if self.state[8] in ("L", "R"):
            fake_555.state[7] = "L"
        if self.state[11] in ("L", "R"):
            fake_555.state[9] = "L"
        if self.state[26] in ("L", "R"):
            fake_555.state[17] = "L"
        if self.state[29] in ("L", "R"):
            fake_555.state[19] = "L"

        # Left
        if self.state[44] in ("L", "R"):
            fake_555.state[32] = "L"
        if self.state[47] in ("L", "R"):
            fake_555.state[34] = "L"
        if self.state[62] in ("L", "R"):
            fake_555.state[42] = "L"
        if self.state[65] in ("L", "R"):
            fake_555.state[44] = "L"

        # Front
        if self.state[80] in ("L", "R"):
            fake_555.state[57] = "L"
        if self.state[83] in ("L", "R"):
            fake_555.state[59] = "L"
        if self.state[98] in ("L", "R"):
            fake_555.state[67] = "L"
        if self.state[101] in ("L", "R"):
            fake_555.state[69] = "L"

        # Right
        if self.state[116] in ("L", "R"):
            fake_555.state[82] = "L"
        if self.state[119] in ("L", "R"):
            fake_555.state[84] = "L"
        if self.state[134] in ("L", "R"):
            fake_555.state[92] = "L"
        if self.state[137] in ("L", "R"):
            fake_555.state[94] = "L"

        # Back
        if self.state[152] in ("L", "R"):
            fake_555.state[107] = "L"
        if self.state[155] in ("L", "R"):
            fake_555.state[109] = "L"
        if self.state[170] in ("L", "R"):
            fake_555.state[117] = "L"
        if self.state[173] in ("L", "R"):
            fake_555.state[119] = "L"

        # Down
        if self.state[188] in ("L", "R"):
            fake_555.state[132] = "L"
        if self.state[191] in ("L", "R"):
            fake_555.state[134] = "L"
        if self.state[206] in ("L", "R"):
            fake_555.state[142] = "L"
        if self.state[209] in ("L", "R"):
            fake_555.state[144] = "L"

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

        # At this point we can treat UD centers like 5x5x5 centers
        # Create a dummy 5x5x5 cube object that we can use to find the steps to
        # solve the UD centers
        fake_555 = RubiksCube555(solved_5x5x5)
        fake_555.lt_init()
        self.populate_fake_555_for_UD(fake_555)
        fake_555.lt_UD_centers_stage.solve()

        for step in fake_555.solution:
            self.rotate(step)
        log.info("UD staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        #self.print_cube()

        self.lt_LR_inner_x_centers_stage.solve()
        self.lt_LR_oblique_edge_pairing.solve()

        log.info("Took %d steps to stage UD centers and LR inner-x-centers and oblique pairs" % self.get_solution_len_minus_rotates(self.solution))
        #self.print_cube()


        # At this point we can treat UD centers like 5x5x5 centers
        # Create a dummy 5x5x5 cube object that we can use to figure out what steps to
        fake_555 = RubiksCube555(solved_5x5x5)
        fake_555.lt_init()
        self.populate_fake_555_for_LR(fake_555)

        fake_555.lt_LR_centers_stage.solve()
        for step in fake_555.solution:
            self.rotate(step)
        log.info("Took %d steps to stage ULFRBD centers" % self.get_solution_len_minus_rotates(self.solution))
        #self.print_cube()


        self.lt_UD_centers_solve.solve()
        log.info("Took %d steps to solve UD centers" % self.get_solution_len_minus_rotates(self.solution))
        #self.print_cube()


        self.lt_LR_centers_solve.solve()
        log.info("Took %d steps to solve LR centers" % self.get_solution_len_minus_rotates(self.solution))
        #self.print_cube()


        self.lt_LFRB_centers_solve.solve()
        log.info("Took %d steps to solve centers" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()

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

    def pair_outside_edges(self):
        """
        This is not used at the moment...maybe someday
        """
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
        fake_444.state[2] = self.state[2]
        fake_444.state[3] = self.state[5]
        fake_444.state[5] = self.state[7]
        fake_444.state[8] = self.state[12]
        fake_444.state[9] = self.state[25]
        fake_444.state[12] = self.state[30]
        fake_444.state[14] = self.state[32]
        fake_444.state[15] = self.state[35]

        # Left
        fake_444.state[18] = self.state[38]
        fake_444.state[19] = self.state[41]
        fake_444.state[21] = self.state[43]
        fake_444.state[24] = self.state[48]
        fake_444.state[25] = self.state[61]
        fake_444.state[28] = self.state[66]
        fake_444.state[30] = self.state[68]
        fake_444.state[31] = self.state[71]

        # Front
        fake_444.state[34] = self.state[74]
        fake_444.state[35] = self.state[77]
        fake_444.state[37] = self.state[79]
        fake_444.state[40] = self.state[84]
        fake_444.state[41] = self.state[97]
        fake_444.state[44] = self.state[102]
        fake_444.state[46] = self.state[104]
        fake_444.state[47] = self.state[107]

        # Right
        fake_444.state[50] = self.state[110]
        fake_444.state[51] = self.state[113]
        fake_444.state[53] = self.state[115]
        fake_444.state[56] = self.state[120]
        fake_444.state[57] = self.state[133]
        fake_444.state[60] = self.state[138]
        fake_444.state[62] = self.state[140]
        fake_444.state[63] = self.state[143]

        # Back
        fake_444.state[66] = self.state[146]
        fake_444.state[67] = self.state[149]
        fake_444.state[69] = self.state[151]
        fake_444.state[72] = self.state[156]
        fake_444.state[73] = self.state[169]
        fake_444.state[76] = self.state[174]
        fake_444.state[78] = self.state[176]
        fake_444.state[79] = self.state[179]

        # Down
        fake_444.state[82] = self.state[182]
        fake_444.state[83] = self.state[185]
        fake_444.state[85] = self.state[187]
        fake_444.state[88] = self.state[192]
        fake_444.state[89] = self.state[205]
        fake_444.state[92] = self.state[210]
        fake_444.state[94] = self.state[212]
        fake_444.state[95] = self.state[215]

        fake_444.group_edges()

        for step in fake_444.solution:
            if step == 'EDGES_GROUPED':
                continue

            if step.startswith('4'):
                step = '6' + step[1:]
            elif step.startswith('3'):
                raise ImplementThis('4x4x4 steps starts with 3')

            self.rotate(step)

        self.print_cube()
        log.warning("Outside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def pair_outside_edges_via_555(self):
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
        self.pair_outside_edges_via_555()
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

