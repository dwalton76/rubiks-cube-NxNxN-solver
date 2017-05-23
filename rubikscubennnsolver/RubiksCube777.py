
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis, steps_cancel_out, convert_state_to_hex, LookupTable, LookupTableIDA
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_5x5x5
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_6x6x6, moves_6x6x6
from rubikscubennnsolver.RubiksSide import Side, SolveError
import logging
import math
import os
import random
import re
import subprocess
import sys

log = logging.getLogger(__name__)

moves_7x7x7 = moves_6x6x6
solved_7x7x7 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'


class RubiksCube777(RubiksCube):
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

    dwalton can we use a 5x5x5 to solve the staged centers? Would need to
        - create solid pairs of the oblique edges (8!/(4!*4!))^3 or 343,000
        - solve the 4 inner x-centers and t-centers...(8!/(4!*4!))^2 or 4900
        - so (8!/(4!*4!))^5 or 1,680,700,000
        - use IDA with two prune tables

    - solve the UD centers...this is (8!/(4!*4!))^6 or 117 billion so use IDA
    - solve the LR centers
    - solve the LR and FB centers

    For 7x7x7 edges
    - pair the middle 3 wings for each side via 5x5x5
    - pair the outer 2 wings with the paired middle 3 wings via 5x5x5
    """

    def __init__(self, kociemba_string, debug=False):
        RubiksCube.__init__(self, kociemba_string)

        if debug:
            log.setLevel(logging.DEBUG)

    def lt_init(self):
        '''
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
        '''
        self.lt_UD_oblique_edge_pairing_middle_only = LookupTable(self,
                                                                  'lookup-table-7x7x7-step11-UD-oblique-edge-pairing-middle-only.txt',
                                                                  '777-UD-oblique-edge-pairing-middle-only',
                                                                  'TBD',
                                                                  True) # state_hex

        '''
        24!/(8!*16!) is 735,471

        lookup-table-7x7x7-step12-UD-oblique-edge-pairing-outside-only.txt
        ==================================================================
        1 steps has 4 entries (0 percent, 0.00x previous step)
        2 steps has 67 entries (0 percent, 16.75x previous step)
        3 steps has 900 entries (0 percent, 13.43x previous step)
        4 steps has 9,626 entries (1 percent, 10.70x previous step)
        5 steps has 80,202 entries (10 percent, 8.33x previous step)
        6 steps has 329,202 entries (44 percent, 4.10x previous step)
        7 steps has 302,146 entries (41 percent, 0.92x previous step)
        8 steps has 13,324 entries (1 percent, 0.04x previous step)

        Total: 735,471 entries
        '''
        self.lt_UD_oblique_edge_pairing_outside_only = LookupTable(self,
                                                                   'lookup-table-7x7x7-step12-UD-oblique-edge-pairing-outside-only.txt',
                                                                   '777-UD-oblique-edge-pairing-outside-only',
                                                                   'TBD',
                                                                   True) # state_hex
        '''
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
        '''
        self.lt_UD_oblique_edge_pairing = LookupTableIDA(self,
                                                         'lookup-table-7x7x7-step10-UD-oblique-edge-pairing.txt',
                                                         '777-UD-oblique-edge-pairing',
                                                         '1d18c5c0000000000000000000000000e8c62e',
                                                         True, # state_hex
                                                         moves_7x7x7,

                                                         # do not mess up UD 5x5x5 centers
                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'"),

                                                         # prune tables
                                                         (self.lt_UD_oblique_edge_pairing_middle_only,
                                                          self.lt_UD_oblique_edge_pairing_outside_only))

        '''
        lookup-table-7x7x7-step21-UD-centers-reduce-to-5x5x5-oblique-only.txt
        =====================================================================
        1 steps has 9 entries (0 percent, 0.00x previous step)
        2 steps has 48 entries (0 percent, 5.33x previous step)
        3 steps has 276 entries (0 percent, 5.75x previous step)
        4 steps has 1572 entries (0 percent, 5.70x previous step)
        5 steps has 8134 entries (2 percent, 5.17x previous step)
        6 steps has 33187 entries (9 percent, 4.08x previous step)
        7 steps has 94826 entries (27 percent, 2.86x previous step)
        8 steps has 141440 entries (41 percent, 1.49x previous step)
        9 steps has 59620 entries (17 percent, 0.42x previous step)
        10 steps has 3808 entries (1 percent, 0.06x previous step)
        11 steps has 80 entries (0 percent, 0.02x previous step)

        Total: 343000 entries
        '''
        self.lt_UD_centers_to_555_oblique_only = LookupTable(self,
                                                             'lookup-table-7x7x7-step21-UD-centers-reduce-to-5x5x5-oblique-only.txt',
                                                             '777-UD-centers-reduce-to-555-oblique-only',
                                                             'TBD',
                                                             False) # state_hex

        '''
        lookup-table-7x7x7-step22-UD-centers-reduce-to-5x5x5-center-only.txt
        ====================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 22 entries (0 percent, 4.40x previous step)
        3 steps has 82 entries (1 percent, 3.73x previous step)
        4 steps has 292 entries (5 percent, 3.56x previous step)
        5 steps has 986 entries (20 percent, 3.38x previous step)
        6 steps has 2001 entries (40 percent, 2.03x previous step)
        7 steps has 1312 entries (26 percent, 0.66x previous step)
        8 steps has 200 entries (4 percent, 0.15x previous step)

        Total: 4900 entries
        '''
        self.lt_UD_centers_to_555_center_only = LookupTable(self,
                                                            'lookup-table-7x7x7-step22-UD-centers-reduce-to-5x5x5-center-only.txt',
                                                             '777-UD-centers-reduce-to-555-center-only',
                                                            'TBD',
                                                            False) # state_hex

        '''
        dwalton something here does not look right...I only built part of this tables but
        the numbers are dropping like crazy when it should have 1,680,700,000 entries if
        you built it out the whole way. Need to investigate.

        - create solid pairs of the oblique edges (8!/(4!*4!))^3 or 343,000
        - solve the 4 inner x-centers and t-centers...(8!/(4!*4!))^2 or 4900
        - so (8!/(4!*4!))^5 or 1,680,700,000
        - use IDA with two prune tables

        lookup-table-7x7x7-step20-UD-centers-reduce-to-5x5x5.txt
        ========================================================
        1 steps has 9 entries (0 percent, 0.00x previous step)
        2 steps has 64 entries (0 percent, 7.11x previous step)
        3 steps has 412 entries (0 percent, 6.44x previous step)
        4 steps has 2,643 entries (0 percent, 6.42x previous step)
        5 steps has 17,408 entries (0 percent, 6.59x previous step)
        6 steps has 110,881 entries (0 percent, 6.37x previous step)
        7 steps has 688,216 entries (0 percent, 6.21x previous step)
        8 steps has 4,078,714 entries (4 percent, 5.93x previous step)
        9 steps has 22,258,476 entries (27 percent, 5.46x previous step)
        10 steps has 37,673,279 entries (45 percent, 1.69x previous step)
        11 steps has 17,119,723 entries (20 percent, 0.45x previous step)

        Total: 81,949,825 entries
        '''
        self.lt_UD_centers_to_555 = LookupTableIDA(self,
                                                   'lookup-table-7x7x7-step20-UD-centers-reduce-to-5x5x5.txt',
                                                   '777-UD-centers-reduce-to-555',
                                                   'TBD',
                                                   False, # state_hex
                                                   moves_7x7x7,

                                                   ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", # do not mess up UD 5x5x5 centers
                                                    "Rw",  "Rw'",  "Lw",  "Lw'",  "Fw",  "Fw'",  "Bw",  "Bw'"), # do not mess up UD oblique edges

                                                   # prune tables
                                                   (self.lt_UD_centers_to_555_oblique_only,
                                                    self.lt_UD_centers_to_555_center_only))


    def create_fake_555_centers(self):

        # Create a fake 5x5x5 to stage the UD inner 5x5x5 centers
        fake_555 = RubiksCube555(solved_5x5x5)
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

        return fake_555

    def group_inside_UD_centers(self):
        fake_555 = self.create_fake_555_centers()
        fake_555.lt_UD_centers_stage.solve()

        for step in fake_555.solution:

            if step.startswith('5'):
                step = '7' + step[1:]
            elif step.startswith('3'):
                step = '4' + step[1:]
            elif 'w' in step:
                step = '3' + step

            self.rotate(step)

    def create_fake_666_centers(self):

        # Create a fake 6x6x6 to stage the outside UD oblique edges
        fake_666 = RubiksCube666(solved_6x6x6)
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

        self.print_cube()
        fake_666.print_cube()
        return fake_666

    def group_outside_UD_oblique_edges(self):
        fake_666 = self.create_fake_666_centers()
        fake_666.lt_UD_oblique_edge_pairing_right_only.solve()
        fake_666.lt_UD_oblique_edge_pairing.solve()

        for step in fake_666.solution:

            if step.startswith('6'):
                step = '7' + step[1:]

            self.rotate(step)

    def group_centers_guts(self):
        self.lt_init()
        self.group_inside_UD_centers()
        #self.print_cube()

        self.group_outside_UD_oblique_edges()
        #self.print_cube()

        self.lt_UD_oblique_edge_pairing.solve()
        #self.print_cube()


        self.lt_UD_centers_to_555.solve()
        self.print_cube()
        log.info("UD staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        # dwalton
        sys.exit(0)

    def group_edges(self):
        """
        """
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
