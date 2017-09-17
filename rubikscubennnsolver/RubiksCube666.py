
from collections import OrderedDict
from pprint import pformat
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

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCube.__init__(self, state, order, colormap)

        if debug:
            log.setLevel(logging.DEBUG)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

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
                                                      True,  # state_hex
                                                      linecount=735471)

        '''
        lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt
        lookup-table-6x6x6-step22-UD-oblique-edge-pairing-right-only.txt
        ===============================================================
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
        '''
        self.lt_UD_oblique_edge_pairing_left_only = LookupTable(self,
                                                                'lookup-table-6x6x6-step21-UD-oblique-edge-pairing-left-only.txt',
                                                                '666-UD-oblique-edge-pairing-left-only',
                                                                '990000000099',
                                                                True, # state_hex
                                                                linecount=12870)

        self.lt_UD_oblique_edge_pairing_right_only = LookupTable(self,
                                                                'lookup-table-6x6x6-step22-UD-oblique-edge-pairing-right-only.txt',
                                                                '666-UD-oblique-edge-pairing-right-only',
                                                                '660000000066',
                                                                True, # state_hex
                                                                linecount=12870)

        '''
        Now pair the UD oblique edges so that we can reduce the 6x6x6 centers to a 5x5x5
        (24!/(8!*16!))^2 is 540,917,591,841 so this is too large for us to build so use
        IDA and build it 8 steps deep.

        Our prune tables will be to solve on the left or right oblique edges. Each of these
        tables are 24!/(8!*16!) or 735,471
        735471/540917591841 is 0.0000013596729171

        Originally I did what is described above but the IDA search took 4 minutes
        (on my laptop) for some cubes...I can only imagine how long that would
        take on a 300Mhz EV3.  To speed this up I did something unusual here...I
        rebuilt the step20 table but restricted moves so that UD obliques can
        only move to sides UFDB. The cube will be very scrambled though and
        there will be UD obliques on sides LR.  What I do is "fake move" these
        obliques to side UDFB so that I can use the step20 table.  At that point
        there will only be UD obliques on sides ULDR so I then do a rotate_y()
        one time to make LR free of UD obliques again. Then I do another lookup
        in the step20 table.

        I only build the table to 9-deep, it would have 165 million entries if
        I built it the whole way out but that would be too large tou check into
        the repo so I use IDA.

        lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt
        =====================================================
        1 steps has 3 entries (0 percent, 0.00x previous step)
        2 steps has 29 entries (0 percent, 9.67x previous step)
        3 steps has 286 entries (0 percent, 9.86x previous step)
        4 steps has 2,052 entries (0 percent, 7.17x previous step)
        5 steps has 16,348 entries (0 percent, 7.97x previous step)
        6 steps has 127,859 entries (0 percent, 7.82x previous step)
        7 steps has 844,248 entries (3 percent, 6.60x previous step)
        8 steps has 4,623,585 entries (18 percent, 5.48x previous step)
        9 steps has 19,019,322 entries (77 percent, 4.11x previous step)

        Total: 24,633,732 entries
        '''
        self.lt_UD_oblique_edge_pairing = LookupTableIDA(self,
                                                         'lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt',
                                                         '666-UD-oblique-edge-pairing',
                                                         'ff00000000ff',
                                                         True, # state_hex
                                                         moves_6x6x6,

                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", # These would break up the staged UD inner x-centers
                                                          "Fw", "Fw'", "Bw", "Bw'",
                                                          "3Uw", "3Uw'", "3Dw", "3Dw'", "Uw", "Uw'", "Dw", "Dw'"),

                                                         # prune tables
                                                         (self.lt_UD_oblique_edge_pairing_left_only,
                                                          self.lt_UD_oblique_edge_pairing_right_only),
                                                         linecount=24633732)

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
                                                      True, # state_hex
                                                      linecount=12870)

        '''
        lookup-table-6x6x6-step41-LR-oblique-pairing-left-only.txt
        lookup-table-6x6x6-step42-LR-oblique-pairing-right-only.txt
        ==========================================================
        1 steps has 3 entries (0 percent, 0.00x previous step)
        2 steps has 29 entries (0 percent, 9.67x previous step)
        3 steps has 238 entries (1 percent, 8.21x previous step)
        4 steps has 742 entries (5 percent, 3.12x previous step)
        5 steps has 1836 entries (14 percent, 2.47x previous step)
        6 steps has 4405 entries (34 percent, 2.40x previous step)
        7 steps has 3774 entries (29 percent, 0.86x previous step)
        8 steps has 1721 entries (13 percent, 0.46x previous step)
        9 steps has 122 entries (0 percent, 0.07x previous step)

        Total: 12870 entries
        '''
        self.lt_LR_oblique_edge_pairing_left_only = LookupTable(self,
                                                                'lookup-table-6x6x6-step41-LR-oblique-pairing-left-only.txt',
                                                                '666-LR-oblique-edge-pairing-left-only',
                                                                '99009900',
                                                                True, # state_hex
                                                                linecount=12870)

        self.lt_LR_oblique_edge_pairing_right_only = LookupTable(self,
                                                                'lookup-table-6x6x6-step42-LR-oblique-pairing-right-only.txt',
                                                                '666-LR-oblique-edge-pairing-right-only',
                                                                '66006600',
                                                                True, # state_hex
                                                                linecount=12870)
        '''
        (16!/(8!*8!))^2 is 165,636,900
        I only built this 8 deep to keep the table in the repo small thus the IDA

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
        self.lt_LR_oblique_edge_pairing = LookupTableIDA(self,
                                                         'lookup-table-6x6x6-step40-LR-oblique-pairing.txt',
                                                         '666-LR-oblique-edge-pairing',
                                                         'ff00ff00',
                                                         True, # state_hex
                                                         moves_6x6x6,

                                                         # These would break up the staged UD inner x-centers
                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", # do not mess up UD x-centers
                                                          "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'",         # do not mess up UD oblique pairs
                                                          "3Uw", "3Uw'", "3Dw", "3Dw'"),                              # do not mess up LR x-centers

                                                         # prune tables
                                                         (self.lt_LR_oblique_edge_pairing_left_only,
                                                          self.lt_LR_oblique_edge_pairing_right_only),
                                                         linecount=5614410)

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
                                                                         '666-UD-centers-oblique-edges-solve',
                                                                         'xUUxUUUUUUUUxUUxxDDxDDDDDDDDxDDx',
                                                                         False, # state_hex
                                                                         linecount=343000)

        '''
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
        '''
        self.lt_LR_solve_inner_x_centers_and_oblique_edges = LookupTable(self,
                                                                         'lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt',
                                                                         '666-LR-centers-oblique-edges-solve',
                                                                         'xLLxLLLLLLLLxLLxxxxxxFFxxFFxxxxxxRRxRRRRRRRRxRRxxxxxxBBxxBBxxxxx',
                                                                         False, # state_hex
                                                                         linecount=24010034)


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
                                                         '666-LFRB-centers-oblique-edges-solve',
                                                         'xLLxLLLLLLLLxLLxxFFxFFFFFFFFxFFxxRRxRRRRRRRRxRRxxBBxBBBBBBBBxBBx',
                                                         False, # state_hex
                                                         moves_6x6x6,

                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
                                                          "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
                                                          "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2",                               # do not mess up solved UD
                                                          "L", "L'", "L2", "R", "R'", "R2"), # do not mess up LR sides that we staged via self.lt_LR_solve_inner_x_centers_and_oblique_edges.solve()

                                                         # prune tables
                                                         (self.lt_LR_solve_inner_x_centers_and_oblique_edges,),
                                                         linecount=25679911)

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

        # See the comments where self.lt_UD_oblique_edge_pairing is declared for
        # an explanation on what is happening here
        for x in range(2):
            original_state = self.state[:]
            original_solution = self.solution[:]
            original_solution_len = len(self.solution)

            self.fake_move_UD_to_UFDB()
            self.lt_UD_oblique_edge_pairing.solve()

            tmp_solution = self.solution[original_solution_len:]

            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in tmp_solution:
                self.rotate(step)

            if x == 0:
                self.rotate_y()
            else:
                self.rotate_y_reverse()

        log.info("UD oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def group_centers_guts(self):
        self.lt_init()
        self.group_centers_stage_UD()

        self.lt_LR_inner_x_centers_stage.solve()
        log.info("LR inner x-center staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

        self.lt_LR_oblique_edge_pairing.solve()
        log.info("LR oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Reduce the centers to 5x5x5 centers
        # - solve the UD inner x-centers and pair the UD oblique edges
        # - solve the LR inner x-centers and pair the LR oblique edges
        # - solve the FB inner x-centers and pair the FB oblique edges
        self.lt_UD_solve_inner_x_centers_and_oblique_edges.solve()
        log.info("UD inner x-center solved, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

        self.lt_LR_solve_inner_x_centers_and_oblique_edges.solve() # speed up IDA
        log.info("LR inner x-center and oblique edges prune table solved, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

        self.lt_LFRB_solve_inner_x_centers_and_oblique_edges.solve()
        log.info("LFRB inner x-center and oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # At this point the 6x6x6 centers have been reduced to 5x5x5 centers
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.lt_init()
        self.populate_fake_555_for_ULFRBD(fake_555)
        fake_555.group_centers_guts()

        for step in fake_555.solution:
            self.rotate(step)

        log.info("Took %d steps to solve centers" % self.get_solution_len_minus_rotates(self.solution))

    def pair_inside_edges_via_444(self):
        fake_444 = RubiksCube444(solved_4x4x4, 'URFDLB')
        fake_444.lt_init()

        # The corners don't matter but it does make troubleshooting easier if they match
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
            elif step in ("Uw", "Uw'", "Uw2",
                          "Lw", "Lw'", "Lw2",
                          "Fw", "Fw'", "Fw2",
                          "Rw", "Rw'", "Rw2",
                          "Bw", "Bw'", "Bw2",
                          "Dw", "Dw'", "Dw2"):
                step = '3' + step

            # log.warning("fake_444 step %s" % step)
            self.rotate(step)

        log.info("Inside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def pair_outside_edges_via_555(self):
        fake_555 = RubiksCube555(solved_5x5x5, 'URFDLB')
        fake_555.lt_init()

        # The corners matter for avoiding PLL
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
        fake_555.avoid_pll = True
        fake_555.group_edges()

        for step in fake_555.solution:
            if step == 'EDGES_GROUPED':
                continue

            if step.startswith('5'):
                step = '6' + step[1:]
            elif step.startswith('3'):
                step = '4' + step[1:]

            self.rotate(step)

        log.info("Outside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def group_edges(self):
        """
        Create a fake 444 to pair the inside edges
        Create a fake 555 to pair the outside edges
        """

        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        self.lt_init()
        self.pair_inside_edges_via_444()
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
