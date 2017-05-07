
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis, steps_cancel_out, convert_state_to_hex, LookupTable, LookupTableIDA
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_4x4x4
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
          outside oblique edges. The restriction being that if you do a 3L move
          you must also do a 3R' in order to keep the two outside oblique edges
          paired up. So it is a slice of the layer in the middle. This table
          should be (24!/(8!*16!))^2
    - stage the rest of the UD centers via 5x5x5
    - stage the LR inside 9 centers via 5x5x5
    - LR oblique edges...use the same strategy as UD oblique edges
    - stage the rest of the LR centers via 5x5x5
    - solve the UD centers...this is (8!/(4!*4!))^6 or 117 billion
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
        lookup-table-7x7x7-step10-UD-oblique-edge-pairing.txt
        =====================================================
        '''

        '''
        24!/(8!*16!) is 735,471

        lookup-table-7x7x7-step11-UD-oblique-edge-pairing-middle-only.txt
        =================================================================
        1 steps has 5 entries (0 percent)
        2 steps has 64 entries (0 percent)
        3 steps has 820 entries (0 percent)
        4 steps has 8,504 entries (1 percent)
        5 steps has 66,983 entries (9 percent)
        6 steps has 260,716 entries (35 percent)
        7 steps has 254,717 entries (34 percent)
        8 steps has 136,861 entries (18 percent)
        9 steps has 6,801 entries (0 percent)

        Total: 735,471 entries
        '''
        self.lt_UD_oblique_edge_pairing_middle_only = LookupTable(self,
                                                                  'lookup-table-7x7x7-step11-UD-oblique-edge-pairing-middle-only.txt',
                                                                  '777-UD-oblique-edge-pairing-middle-only',
                                                                  'TBD', #
                                                                  True) # state_hex

        '''
        24!/(8!*16!) is 735,471

        lookup-table-7x7x7-step12-UD-oblique-edge-pairing-outside-only.txt
        ==================================================================
        1 steps has 5 entries (0 percent)
        2 steps has 66 entries (0 percent)
        3 steps has 894 entries (0 percent)
        4 steps has 9,629 entries (0 percent)
        5 steps has 80,576 entries (5 percent)
        6 steps has 336,775 entries (23 percent)
        7 steps has 374,788 entries (26 percent)
        8 steps has 319,824 entries (22 percent)
        9 steps has 279,940 entries (19 percent)
        10 steps has 12,166 entries (0 percent)

        Total: 1,414,663 entries
        '''
        self.lt_UD_oblique_edge_pairing_outside_only = LookupTable(self,
                                                                   'lookup-table-7x7x7-step12-UD-oblique-edge-pairing-outside-only.txt',
                                                                   '777-UD-oblique-edge-pairing-outside-only',
                                                                   'TBD', #
                                                                   True) # state_hex

    def create_fake_555_centers(self):

        # Create a fake 5x5x5 to stage the UD inner 5x5x5 centers
        fake_555 = RubiksCube555(solved_5x5x5)

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

        # dwalton
        for step in fake_555.solution:

            if step.startswith('5'):
                step = '7' + step[1:]
            elif step.startswith('3'):
                step = '4' + step[1:]
            elif 'w' in step:
                step = '3' + step

            self.rotate(step)

    def group_centers_guts(self):
        self.lt_init()
        self.group_inside_UD_centers()

        self.print_cube()
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
