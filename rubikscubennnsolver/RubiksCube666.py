
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

        '''
        lookup-table-6x6x6-step70-edges-slice-forward.txt
        =================================================
        1 steps has 13 entries (0 percent)
        2 steps has 138 entries (0 percent)
        3 steps has 1,440 entries (0 percent)
        4 steps has 11,009 entries (5 percent)
        5 steps has 51,100 entries (26 percent)
        6 steps has 96,002 entries (50 percent)
        7 steps has 30,338 entries (15 percent)
        8 steps has 40 entries (0 percent)

        Total: 190,080 entries
        '''
        self.lt_edge_slice_forward = LookupTable(self,
                                                 'lookup-table-6x6x6-step70-edges-slice-forward.txt',
                                                 '666-edges-slice-forward',
                                                 None)

        '''
        lookup-table-6x6x6-step80-edges-slice-backward.txt
        ==================================================
        1 steps has 13 entries (0 percent)
        2 steps has 138 entries (0 percent)
        3 steps has 1,440 entries (0 percent)
        4 steps has 11,009 entries (5 percent)
        5 steps has 51,100 entries (26 percent)
        6 steps has 96,002 entries (50 percent)
        7 steps has 30,338 entries (15 percent)
        8 steps has 40 entries (0 percent)

        Total: 190,080 entries
        '''
        self.lt_edge_slice_backward = LookupTable(self,
                                                  'lookup-table-6x6x6-step80-edges-slice-backward.txt',
                                                  '666-edges-slice-backward',
                                                  None)


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
        #self.print_cube()

        self.lt_LR_inner_x_centers_stage.solve()
        self.lt_LR_oblique_edge_pairing.solve()

        log.info("Took %d steps to stage UD centers and LR inner-x-centers and oblique pairs" % len(self.solution))
        #self.print_cube()


        # At this point we can treat UD centers like 5x5x5 centers
        # Create a dummy 5x5x5 cube object that we can use to figure out what steps to
        fake_555 = RubiksCube555(solved_5x5x5)
        self.populate_fake_555_for_LR(fake_555)

        fake_555.lt_LR_centers_stage.solve()
        for step in fake_555.solution:
            self.rotate(step)
        log.info("Took %d steps to stage ULFRBD centers" % len(self.solution))
        #self.print_cube()


        self.lt_UD_centers_solve.solve()
        log.info("Took %d steps to solve UD centers" % len(self.solution))
        #self.print_cube()


        self.lt_LR_centers_solve.solve()
        log.info("Took %d steps to solve LR centers" % len(self.solution))
        #self.print_cube()

        self.lt_LFRB_centers_solve.solve()
        log.info("Took %d steps to solve centers" % len(self.solution))
        self.print_cube()

    def find_moves_to_stage_slice_forward_666(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        steps = self.lt_edge_slice_forward.steps(state)
        #log.info('slice forward for state %s, steps %s' % (state, pformat(steps)))
        return steps

    def find_moves_to_stage_slice_backward_666(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        steps = self.lt_edge_slice_backward.steps(state)
        #log.info('slice backward for state %s, steps %s' % (state, pformat(steps)))
        return steps

    def get_sister_wings_slice_backward_666(self):
        results = (None, None, None, None)
        max_pair_on_slice_back = 0

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        # Work with the wing at the bottom of the F-east edge
        # Move the sister wing to F-west
        target_wing = (self.sideF.edge_east_pos[-1], self.sideR.edge_west_pos[-1])
        target_wing_side = self.get_side_for_index(target_wing[0])

        # Do we need to reverse sister_wing1?
        for sister_wing1_reverse in (True, False):
            sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0], remove_if_in_same_edge=True)

            if sister_wing1_reverse:
                sister_wing1 = tuple(list(reversed(sister_wing1)))
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])

            sister_wing2 = None
            sister_wing3 = None
            log.info("target_wing %s on %s" % (pformat(target_wing), target_wing_side))
            log.info("sister_wing1 %s on %s" % (pformat(sister_wing1), sister_wing1_side))

            for sister_wing1_use_first_neighbor in (True, False):
                neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])

                if sister_wing1_use_first_neighbor:
                    sister_wing1_neighbor = neighbors[0]
                else:
                    sister_wing1_neighbor = neighbors[1]

                for sister_wing2_reverse in (True, False):
                    sister_wing2 = self.get_wing_in_middle_of_edge(sister_wing1_neighbor, remove_if_in_same_edge=True)

                    if sister_wing2_reverse:
                        sister_wing2 = tuple(list(reversed(sister_wing2)))
                    sister_wing2_side = self.get_side_for_index(sister_wing2[0])

                    log.info("sister_wing1_use_first_neighbor %s, sister_wing2 %s on %s" %
                        (sister_wing1_use_first_neighbor, pformat(sister_wing2), sister_wing2_side))

                    for sister_wing2_use_first_neighbor in (True, False):
                        neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])

                        if sister_wing2_use_first_neighbor:
                            sister_wing2_neighbor = neighbors[0]
                        else:
                            sister_wing2_neighbor = neighbors[1]

                        for sister_wing3_reverse in (True, False):
                            sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor, remove_if_in_same_edge=True)

                            if sister_wing3 is None:
                                continue
                                # dwalton dig into this
                                # raise SolveError("sister_wing3 is None")

                            if sister_wing3_reverse:
                                sister_wing3 = tuple(list(reversed(sister_wing3)))
                            sister_wing3_side = self.get_side_for_index(sister_wing3[0])

                            log.info("sister_wing2_use_first_neighbor %s, sister_wing3 %s on %s" %
                                (sister_wing2_use_first_neighbor, pformat(sister_wing3), sister_wing3_side))

                            steps = self.find_moves_to_stage_slice_backward_666(target_wing, sister_wing1, sister_wing2, sister_wing3)

                            if steps:
                                pre_non_paired_wings_count = self.get_non_paired_wings_count()
                                for step in steps:
                                    self.rotate(step)
                                self.rotate("4Uw'")
                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # F-east must pair
                                if self.state[96] == self.state[102] and self.state[127] == self.state[133]:
                                    will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                else:
                                    will_pair_on_slice_count = 0

                                # log.info("get_sister_wings_slice_backward_666() will_pair_on_slice_count %d via %s" %
                                #    (will_pair_on_slice_count, ' '.join(steps)))

                                # restore cube state
                                self.state = copy(original_state)
                                self.solution = copy(original_solution)

                                if will_pair_on_slice_count > max_pair_on_slice_back:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3)
                                    max_pair_on_slice_back = will_pair_on_slice_count

        # log.info("max_pair_on_slice_back is %d" % max_pair_on_slice_back)
        return results

    def prep_for_slice_back_666(self):

        (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_666()

        if target_wing is None:
            log.info("prep_for_slice_back_666() failed...get_sister_wings_slice_backward_666")
            return False

        steps = self.find_moves_to_stage_slice_backward_666(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True
        else:
            log.info("prep_for_slice_back_666() failed...no steps")
            return False

    def get_sister_wings_slice_forward_666(self, pre_non_paired_wings_count):
        results = (None, None, None, None)
        max_pair_on_slice_forward = 0
        log.info("get_sister_wings_slice_forward_666 called with pre_non_paired_wings_count %d" % pre_non_paired_wings_count)

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        # Work with the wing at the bottom of the F-west edge
        # Move the sister wing to F-east
        target_wing = (self.sideL.edge_east_pos[-1], self.sideF.edge_west_pos[-1])
        target_wing_side = self.get_side_for_index(target_wing[0])

        for sister_wing1_reverse in (True, False):
            sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0], remove_if_in_same_edge=True)

            if sister_wing1_reverse:
                sister_wing1 = tuple(list(reversed(sister_wing1)))
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])

            sister_wing2 = None
            sister_wing3 = None
            log.info("target_wing %s on %s" % (pformat(target_wing), target_wing_side))
            log.info("sister_wing1 %s, reverse %s, %s" % (pformat(sister_wing1), sister_wing1_reverse, sister_wing1_side))
            #raise SolveError('dwalton')

            for sister_wing1_use_first_neighbor in (True, False):
                neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])

                if sister_wing1_use_first_neighbor:
                    sister_wing1_neighbor = neighbors[0]
                else:
                    sister_wing1_neighbor = neighbors[1]

                for sister_wing2_reverse in (True, False):
                    sister_wing2 = self.get_wing_in_middle_of_edge(sister_wing1_neighbor, remove_if_in_same_edge=True)

                    # Is this neeeded? 555 does not have this.
                    #if sister_wing2 is None:
                    #    continue

                    if sister_wing2_reverse:
                        log.info("sister_wing2: %s" % pformat(sister_wing2))
                        sister_wing2 = tuple(list(reversed(sister_wing2)))
                    sister_wing2_side = self.get_side_for_index(sister_wing2[0])

                    log.info("sister_wing1_use_first_neighbor %s, sister_wing2 %s, reverse %s, %s" %
                       (sister_wing1_use_first_neighbor, pformat(sister_wing2), sister_wing2_reverse, sister_wing2_side))

                    for sister_wing2_use_first_neighbor in (True, False):
                        neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])

                        if sister_wing2_use_first_neighbor:
                            sister_wing2_neighbor = neighbors[0]
                        else:
                            sister_wing2_neighbor = neighbors[1]

                        for sister_wing3_reverse in (True, False):

                            # If we are pairing the last six wings then we need sister_wing3 to
                            # be any unpaired edge that allows us to only pair 2 on the slice forward
                            if pre_non_paired_wings_count == 6:

                                # We need sister_wing3 to be any unpaired edge that allows us
                                # to only pair 2 on the slice forward
                                for wing in self.get_non_paired_wings():
                                    if (wing[0] not in (target_wing, sister_wing1, sister_wing2, sister_wing3) and
                                        wing[1] not in (target_wing, sister_wing1, sister_wing2, sister_wing3)):
                                        sister_wing3 = wing[1]
                                        break
                            else:
                                sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor, remove_if_in_same_edge=True)

                            # Is this neeeded? 555 does not have this.
                            #if sister_wing3 is None:
                            #    continue

                            if sister_wing3_reverse:
                                sister_wing3 = tuple(list(reversed(sister_wing3)))
                            sister_wing3_side = self.get_side_for_index(sister_wing3[0])

                            log.info("sister_wing2_use_first_neighbor %s, sister_wing3 %s, reverse %s, %s" %
                                (sister_wing2_use_first_neighbor, pformat(sister_wing3), sister_wing3_reverse, sister_wing3_side))
                            steps = self.find_moves_to_stage_slice_forward_666(target_wing, sister_wing1, sister_wing2, sister_wing3)

                            if steps:
                                log.info("target_wing %s, sister_wing1 %s, sister_wing2 %s, sister_wing3 %s" %
                                    (pformat(target_wing), pformat(sister_wing1), pformat(sister_wing2), pformat(sister_wing3)))

                                # pre_non_paired_wings_count = self.get_non_paired_wings_count()
                                for step in steps:
                                    self.rotate(step)
                                self.rotate("4Uw")
                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # F-west must pair
                                if self.state[91] == self.state[97] and self.state[60] == self.state[66]:
                                    will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                    log.warning("will_pair_on_slice_count %d" % will_pair_on_slice_count)
                                else:
                                    will_pair_on_slice_count = 0
                                    log.warning("F-west will not pair")

                                # restore cube state
                                self.state = copy(original_state)
                                self.solution = copy(original_solution)

                                if will_pair_on_slice_count > max_pair_on_slice_forward:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3)
                                    max_pair_on_slice_forward = will_pair_on_slice_count

        log.warning("max_pair_on_slice_forward is %d" % max_pair_on_slice_forward)
        #if max_pair_on_slice_forward != 3:
        #    raise SolveError("Could not find sister wings for 5x5x5 slice forward (max_pair_on_slice_forward %d)" % max_pair_on_slice_forward)

        log.info("get_sister_wings_slice_forward_666 returning %s" % pformat(results))
        return results

    def rotate_unpaired_wing_to_bottom_of_F_east(self):
        """
        Rotate an unpaired wing to the bottom of F-east (one that can be sliced back)
        """
        for flip in (False, True):

            if flip:
                self.rotate_x()
                self.rotate_x()

            for x in range(3):
                if self.state[96] == self.state[102] and self.state[127] == self.state[133]:
                    self.rotate_y()
                else:
                    if self.prep_for_slice_back_666():
                        return (True, flip)

        self.rotate_x()
        self.rotate_x()
        return (False, flip)

    def pair_six_wings_666(self, wing_to_pair, pre_non_paired_wings_count, flip):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        self.rotate_edge_to_F_west(wing_to_pair)

        if flip:
            self.rotate_z()
            self.rotate_z()
            self.rotate_y()

        # We need the unpaired wing to be at the bottom, if it isn't don't worry
        # it will be when pair_six_wings_666 is called for the same wing but with
        # the opposite 'flip' value.
        if self.state[91] == self.state[97] and self.state[60] == self.state[66]:
            return False

        log.info("")
        log.info("pair_six_wings_666() with wing_to_pair %s, flip %s (%d left to pair, %d steps in)" % (pformat(wing_to_pair), flip, original_non_paired_wings_count, original_solution_len))
        # log.info("PREP-FOR-4Uw-SLICE (begin)")
        # self.print_cube()

        (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_forward_666(pre_non_paired_wings_count)

        if target_wing is None:
            log.info("pair_six_wings_666() failed...get_sister_wings_slice_forward_666")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            raise SolveError("dwalton remove me")
            return False

        steps = self.find_moves_to_stage_slice_forward_666(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if not steps:
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        log.info("PREP-FOR-4Uw-SLICE (end)....SLICE (begin), %d left to pair" % self.get_non_paired_wings_count())
        self.print_cube()
        self.rotate("4Uw")
        log.info("SLICE (end), %d left to pair" % self.get_non_paired_wings_count())
        self.print_cube()

        post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_wings_666()    paired %d wings in %d moves on slice forward (%d left to pair, %d steps in)" %
            (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len))

        (placed_unpaired_wing, flip) = self.rotate_unpaired_wing_to_bottom_of_F_east()

        if not placed_unpaired_wing:
            # dwalton
            raise SolveError("here 20")

            # TODO there are some steps to save here...we only need to move one wing
            # The stars aligned and we paired 4 at once so we have to move those
            # four out of the way via this six step sequence
            for step in "L R' D U L' R".split():
                self.rotate(step)

            (placed_unpaired_wing, flip) = self.rotate_unpaired_wing_to_bottom_of_F_east()
            if not placed_unpaired_wing:
                self.state = copy(original_state)
                self.solution = copy(original_solution)
                return False

        # TODO remove these two checks after running the 50 test cubes
        if self.sideF.east_edge_paired():
            raise SolveError("pair_six_wings_666() failed (F-east should not be paired)")

        if self.state[96] == self.state[102] and self.state[127] == self.state[133]:
            raise SolveError("Need to rotate this around...but then we may need to 2Uw' instead of 4Uw'")

        log.info("PREP-FOR-4Uw'-SLICE-BACK (end)...SLICE BACK (begin), %d left to pair" % self.get_non_paired_wings_count())
        self.print_cube()

        if flip:
            raise ImplementThis("flip is True how much should we rotate")
            self.rotate("2Uw'")
        else:
            self.rotate("4Uw'")

        #log.info("SLICE BACK (end), %d left to pair" % self.get_non_paired_wings_count())
        #self.print_cube()
        self.verify_all_centers_solved()

        post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_wings_666()    paired %d wings in %d moves on slice back (%d left to pair, %d steps in)" %
            (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len - post_slice_forward_solution_len,
             post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len))

        return True

    def group_edges(self):
        """
        Reduce the edges to a 4x4x4
        Create a fake 4x4x4 to solve from there
        """
        # dwalton

        while True:
            non_paired_edges = self.get_non_paired_edges()
            len_non_paired_edges = len(non_paired_edges)
            pre_non_paired_wings_count = self.get_non_paired_wings_count()
            pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
            log.info("")
            log.info("")
            log.info("")
            log.warning("%d steps in, %d wings left to pair over %d edges" % (pre_solution_len, pre_non_paired_wings_count, len_non_paired_edges))

            if pre_non_paired_wings_count == 0:
                break

            # cycle through the unpaired wings and find the wing where pair_six_wings_666
            # pairs the most in the least number of moves
            tmp_state = copy(self.state)
            tmp_solution = copy(self.solution)

            min_moves_per_paired_wing = None
            max_wings_paired = None
            max_wings_paired_wing_to_pair = None
            max_wing_solution_len = None
            max_wings_flip = False

            if len_non_paired_edges >= 4 and pre_non_paired_wings_count > 4:
                for flip in (False, True):
                    for foo in non_paired_edges:
                        wing_to_pair = foo[0]

                        if self.pair_six_wings_666(wing_to_pair, pre_non_paired_wings_count, flip):
                            post_non_paired_wings_count = self.get_non_paired_wings_count()
                            wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count
                            post_solution_len = self.get_solution_len_minus_rotates(self.solution)
                            wing_solution_len = post_solution_len - pre_solution_len

                            if wings_paired > 0:
                                moves_per_paired_wing = float(wing_solution_len/wings_paired)

                                if (min_moves_per_paired_wing is None or
                                    moves_per_paired_wing < min_moves_per_paired_wing or
                                    (moves_per_paired_wing == min_moves_per_paired_wing and wings_paired > max_wings_paired)):
                                    max_wings_paired = wings_paired
                                    max_wings_paired_wing_to_pair = wing_to_pair
                                    max_wing_solution_len = wing_solution_len
                                    max_wings_flip = flip
                                    min_moves_per_paired_wing = moves_per_paired_wing

                        # Restore state
                        self.state = copy(tmp_state)
                        self.solution = copy(tmp_solution)

            if max_wings_paired:
                wing_to_pair = max_wings_paired_wing_to_pair
                log.info("Using %s as next wing_to_pair will pair %d wings in %d moves" % (wing_to_pair, max_wings_paired, max_wing_solution_len))
                self.pair_six_wings_666(wing_to_pair, pre_non_paired_wings_count, max_wings_flip)

            # see which wing we can pair two at a time with the least moves
            else:
                if len_non_paired_edges >= 4:
                    log.warning("There are no wings where pair_six_wings_666 will return True")

                if len_non_paired_edges > 2:
                    # TODO - this scenario needs work, we spend a ton of moves here

                    for flip in (False, True):
                        for foo in non_paired_edges:
                            wing_to_pair = foo[0]

                            if self.pair_one_wing_666(wing_to_pair, flip):
                                post_non_paired_wings_count = self.get_non_paired_wings_count()
                                wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count
                                post_solution_len = self.get_solution_len_minus_rotates(self.solution)
                                wing_solution_len = post_solution_len - pre_solution_len

                                if (max_wings_paired is None or
                                    wings_paired > max_wings_paired or
                                    (wings_paired == max_wings_paired and wing_solution_len < max_wing_solution_len)):
                                    max_wings_paired = wings_paired
                                    max_wings_paired_wing_to_pair = wing_to_pair
                                    max_wing_solution_len = wing_solution_len
                                    max_wing_flip = flip

                            # Restore state
                            self.state = copy(tmp_state)
                            self.solution = copy(tmp_solution)

                    if max_wings_paired_wing_to_pair is None:
                        raise SolveError("FOO")

                    wing_to_pair = max_wings_paired_wing_to_pair
                    log.info("Using %s as next wing_to_pair will pair %s wings in %s moves" % (wing_to_pair, max_wings_paired, max_wing_solution_len))
                    self.pair_one_wing_666(wing_to_pair, max_wing_flip)

                else:
                    self.pair_last_two_edges_666()

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

