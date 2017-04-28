
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis, steps_cancel_out, convert_state_to_hex, LookupTable, LookupTableIDA
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_5x5x5
from rubikscubennnsolver.RubiksSide import Side, SolveError
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

    def __init__(self, kociemba_string):
        RubiksCube.__init__(self, kociemba_string)

        '''
        Stage the inner X-centers
        24!/(8!*16!) is 735,471

        lookup-table-6x6x6-step10-UD-inner-x-centers-stage.txt
        ======================================================
        1 steps has 5 entries (0 percent)
        2 steps has 80 entries (0 percent)
        3 steps has 1,160 entries (0 percent)
        4 steps has 13,726 entries (1 percent)
        5 steps has 121,796 entries (16 percent)
        6 steps has 423,136 entries (57 percent)
        7 steps has 174,656 entries (23 percent)
        8 steps has 912 entries (0 percent)

        Total: 735,471 entries
        '''
        self.lt_UD_inner_x_centers_stage = LookupTable(self,
                                                      'lookup-table-6x6x6-step10-UD-inner-x-centers-stage.txt',
                                                      '666-UD-inner-X-centers-stage',
                                                      'xxxxxUUxxUUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxUUxxUUxxxxx', #
                                                      False) # state_hex

        '''
        Now pair the UD oblique edges so that we can reduce the 6x6x6 centers to a 5x5x5
        (24!/(8!*16!))^2 is 540,917,591,841 so this is too large for us to build so use
        IDA and build it 7 steps deep.

        Our prune tables will be so solve on the left or right oblique edges. Each of these
        tables are 24!/(8!*16!) or 735,471
        735471/540917591841 is 0.0000013596729171

        lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt
        =====================================================

        1 steps has 5 entries (0 percent)
        2 steps has 82 entries (0 percent)
        3 steps has 1434 entries (0 percent)
        4 steps has 24,198 entries (0 percent)
        5 steps has 405,916 entries (0 percent)
        6 steps has 6,839,392 entries (5 percent)
        7 steps has 116,031,874 entries (94 percent)

        Total: 123,302,901 entries


        lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt
        ===============================================================
        1 steps has 5 entries (0 percent)
        2 steps has 82 entries (0 percent)
        3 steps has 1,198 entries (0 percent)
        4 steps has 13,818 entries (1 percent)
        5 steps has 115,638 entries (15 percent)
        6 steps has 399,478 entries (54 percent)
        7 steps has 204,612 entries (27 percent)
        8 steps has 640 entries (0 percent)

        Total: 735,471 entries


        lookup-table-6x6x6-step22-UD-oblique-edge-pairing-right-only.txt
        ================================================================
        1 steps has 5 entries (0 percent)
        2 steps has 82 entries (0 percent)
        3 steps has 1,198 entries (0 percent)
        4 steps has 13,818 entries (1 percent)
        5 steps has 115,638 entries (15 percent)
        6 steps has 399,478 entries (54 percent)
        7 steps has 204,612 entries (27 percent)
        8 steps has 640 entries (0 percent)

        Total: 735,471 entries
        '''
        self.lt_UD_oblique_edge_pairing_left_only = LookupTable(self,
                                                                'lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt',
                                                                '666-UD-oblique-edge-pairing-left-only',
                                                                'xUxxxxxUUxxxxxUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxUxxxxxUUxxxxxUx',
                                                                False) # state_hex

        self.lt_UD_oblique_edge_pairing_right_only = LookupTable(self,
                                                                'lookup-table-6x6x6-step22-UD-oblique-edge-pairing-right-only.txt',
                                                                '666-UD-oblique-edge-pairing-right-only',
                                                                'xxUxUxxxxxxUxUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxUxUxxxxxxUxUxx',
                                                                False) # state_hex

        self.lt_UD_oblique_edge_pairing = LookupTableIDA(self,
                                                         'lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt',
                                                         '666-UD-oblique-edge-pairing',

                                                         # xUUxUxxUUxxUxUUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxUUxUxxUUxxUxUUx
                                                         '699600000000000000006996',

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
                                                      'xxxxxxxxxxxxxxxxxxxxxLLxxLLxxxxxxxxxxxxxxxxxxxxxxxxxxLLxxLLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                                                      False) # state_hex

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
        7 steps has 844,265 entries (0 percent)
        8 steps has 4,623,635 entries (2 percent)
        9 steps has 19,020,012 entries (11 percent)
        10 steps has 47,546,288 entries (28 percent)
        11 steps has 61,806,216 entries (37 percent)
        12 steps has 28,890,242 entries (17 percent)
        13 steps has 2,722,462 entries (1 percent)
        14 steps has 40,242 entries (0 percent)
        15 steps has 148 entries (0 percent)

        Total: 165,640,087 entries
        '''
        self.lt_LR_oblique_edge_pairing = LookupTable(self,
                                                      'lookup-table-6x6x6-step40-LR-oblique-pairing.txt',
                                                      '666-LR-oblique-edge-pairing',
                                                      '6996000069960000',
                                                      True) # state_hex


        '''
        lookup-table-6x6x6-step50-UD-centers-solve.txt
        ==============================================
        (8!/(4!*4!))^4 is 24,010,000

        1 steps has 8 entries (0 percent)
        2 steps has 47 entries (0 percent)
        3 steps has 283 entries (0 percent)
        4 steps has 1,690 entries (0 percent)
        5 steps has 9,675 entries (0 percent)
        6 steps has 51,350 entries (0 percent)
        7 steps has 255,725 entries (1 percent)
        8 steps has 1,165,284 entries (4 percent)
        9 steps has 4,337,586 entries (18 percent)
        10 steps has 9,785,424 entries (40 percent)
        11 steps has 7,457,560 entries (31 percent)
        12 steps has 936,888 entries (3 percent)
        13 steps has 8,480 entries (0 percent)

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
        1 steps has 7 entries (0 percent)
        2 steps has 41 entries (0 percent)
        3 steps has 230 entries (0 percent)
        4 steps has 1,308 entries (0 percent)
        5 steps has 7,234 entries (0 percent)
        6 steps has 36,454 entries (0 percent)
        7 steps has 175,690 entries (0 percent)
        8 steps has 800,122 entries (3 percent)
        9 steps has 3,117,090 entries (12 percent)
        10 steps has 8,125,772 entries (33 percent)
        11 steps has 9,093,004 entries (37 percent)
        12 steps has 2,594,984 entries (10 percent)
        13 steps has 58,064 entries (0 percent)

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
        1 steps has 5 entries (0 percent)
        2 steps has 54 entries (0 percent)
        3 steps has 420 entries (0 percent)
        4 steps has 2,903 entries (0 percent)
        5 steps has 21,388 entries (0 percent)
        6 steps has 145,567 entries (0 percent)
        7 steps has 951,636 entries (2 percent)
        8 steps has 6,082,238 entries (13 percent)
        9 steps has 38,169,564 entries (84 percent)

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
        16 steps has 141 entries (0 percent)
        17 steps has 4 entries (0 percent)

        Total: 24,010,017 entries
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
        self.lt_UD_inner_x_centers_stage.solve()

        # If you uncomment these the IDA search will go much faster but at the tradeoff
        # of adding moves to the solution (increases from 83 to 93 in our base example).
        #
        # These are our two prune tables so if we go ahead and solve for one of them we
        # get the cube in a state that is much closer to being a match for the table we
        # are doing and IDA search against.
        #self.lt_UD_oblique_edge_pairing_left_only.solve()
        self.lt_UD_oblique_edge_pairing_right_only.solve()
        self.lt_UD_oblique_edge_pairing.solve()

        # At this point we can treat UD centers like 5x5x5 centers
        # Create a dummy 5x5x5 cube object that we can use to figure out what steps to
        fake_555 = RubiksCube555(solved_5x5x5)
        self.populate_fake_555_for_UD(fake_555)
        fake_555.lt_UD_centers_stage.solve()

        for step in fake_555.solution:
            self.rotate(step)
        log.info("UD staged, %d steps in" % len(self.solution))
        self.print_cube()

        self.lt_LR_inner_x_centers_stage.solve()
        self.lt_LR_oblique_edge_pairing.solve()

        log.info("Took %d steps to stage UD centers and LR inner-x-centers and oblique pairs" % len(self.solution))
        self.print_cube()


        # At this point we can treat UD centers like 5x5x5 centers
        # Create a dummy 5x5x5 cube object that we can use to figure out what steps to
        fake_555 = RubiksCube555(solved_5x5x5)
        self.populate_fake_555_for_LR(fake_555)

        fake_555.lt_LR_centers_stage.solve()
        for step in fake_555.solution:
            self.rotate(step)
        log.info("Took %d steps to stage ULFRBD centers" % len(self.solution))
        self.print_cube()


        self.lt_UD_centers_solve.solve()
        log.info("Took %d steps to solve UD centers" % len(self.solution))
        self.print_cube()


        self.lt_LR_centers_solve.solve()
        log.info("Took %d steps to solve LR centers" % len(self.solution))
        self.print_cube()

        self.lt_LFRB_centers_solve.solve()
        log.info("Took %d steps to solve centers" % len(self.solution))
        self.print_cube()
        sys.exit(0)
