
from collections import OrderedDict
from pprint import pformat
from rubikscubennnsolver import RubiksCube, ImplementThis
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_5x5x5
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_6x6x6, moves_6x6x6
from rubikscubennnsolver.RubiksSide import Side, SolveError
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA, NoIDASolution
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

    - solve the UD centers...this is (8!/(4!*4!))^6 or 117 billion so use IDA
    - solve the LR centers
    - solve the LR and FB centers

    For 7x7x7 edges
    - pair the middle 3 wings for each side via 5x5x5
    - pair the outer 2 wings with the paired middle 3 wings via 5x5x5
    """

    def __init__(self, kociemba_string, colormap=None, debug=False):
        RubiksCube.__init__(self, kociemba_string, colormap)

        if debug:
            log.setLevel(logging.DEBUG)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        '''
        24!/(8!*16!) is 735,471

        lookup-table-7x7x7-step11-UD-oblique-edge-pairing-middle-only.txt
        lookup-table-7x7x7-step12-UD-oblique-edge-pairing-left-only.txt
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
        '''
        self.lt_UD_oblique_edge_pairing_middle_only = LookupTable(self,
                                                                  'lookup-table-7x7x7-step11-UD-oblique-edge-pairing-middle-only.txt',
                                                                  '777-UD-oblique-edge-pairing-middle-only',
                                                                  '08088080000000000000000000000000404404',
                                                                  True, # state_hex
                                                                  True) # prune table

        self.lt_UD_oblique_edge_pairing_left_only = LookupTable(self,
                                                                   'lookup-table-7x7x7-step12-UD-oblique-edge-pairing-left-only.txt',
                                                                   '777-UD-oblique-edge-pairing-left-only',
                                                                   '10104040000000000000000000000000808202',
                                                                   True, # state_hex
                                                                   True) # prune table

        self.lt_UD_oblique_edge_pairing_right_only = LookupTable(self,
                                                                   'lookup-table-7x7x7-step13-UD-oblique-edge-pairing-right-only.txt',
                                                                   '777-UD-oblique-edge-pairing-right-only',
                                                                   '05000500000000000000000000000000280028',
                                                                   True, # state_hex
                                                                   True) # prune table


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
                                                          self.lt_UD_oblique_edge_pairing_left_only,
                                                          self.lt_UD_oblique_edge_pairing_right_only))

        self.lt_LR_oblique_edge_pairing_middle_only = LookupTable(self,
                                                      'lookup-table-7x7x7-step21-LR-oblique-edge-pairing-middle-only.txt',
                                                      '777-LR-oblique-edge-pairing-middle-only',
                                                      '2022020000000808808000000',
                                                      True, # state_hex
                                                      True) # prune table

        self.lt_LR_oblique_edge_pairing_left_only = LookupTable(self,
                                                      'lookup-table-7x7x7-step22-LR-oblique-edge-pairing-left-only.txt',
                                                      '777-LR-oblique-edge-pairing-left-only',
                                                      '4041010000001010404000000',
                                                      True, # state_hex
                                                      True) # prune table

        self.lt_LR_oblique_edge_pairing_right_only = LookupTable(self,
                                                      'lookup-table-7x7x7-step23-LR-oblique-edge-pairing-right-only.txt',
                                                      '777-LR-oblique-edge-pairing-right-only',
                                                      '1400140000000500050000000',
                                                      True, # state_hex
                                                      True) # prune table

        '''
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
        '''
        self.lt_LR_oblique_edge_pairing = LookupTableIDA(self,
                                                      'lookup-table-7x7x7-step20-LR-oblique-edge-pairing.txt',
                                                      '777-LR-oblique-edge-pairing',
                                                      '7463170000001d18c5c000000',
                                                      True, # state_hex
                                                      moves_7x7x7,

                                                      ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", # do not mess up UD 5x5x5 centers
                                                       "Rw",  "Rw'",  "Lw",  "Lw'",  "Fw",  "Fw'",  "Bw",  "Bw'", # do not mess up UD oblique edges
                                                       "3Uw", "3Uw'", "3Dw", "3Dw'"),

                                                      # prune tables
                                                      (self.lt_LR_oblique_edge_pairing_middle_only,
                                                       self.lt_LR_oblique_edge_pairing_left_only,
                                                       self.lt_LR_oblique_edge_pairing_right_only))


        '''
        lookup-table-7x7x7-step51-UD-solve-inner-center-and-oblique-edges-center-only.txt
        =================================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 22 entries (0 percent, 4.40x previous step)
        3 steps has 82 entries (1 percent, 3.73x previous step)
        4 steps has 292 entries (5 percent, 3.56x previous step)
        5 steps has 986 entries (20 percent, 3.38x previous step)
        6 steps has 2001 entries (40 percent, 2.03x previous step)
        7 steps has 1312 entries (26 percent, 0.66x previous step)
        8 steps has 200 entries (4 percent, 0.15x previous step)

        Total: 4900 entries

        lookup-table-7x7x7-step52-UD-solve-inner-center-and-oblique-edges-edges-only.txt
        ================================================================================
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
        self.lt_UD_solve_inner_centers_and_oblique_edges_center_only = LookupTable(self,
                                                                         'lookup-table-7x7x7-step51-UD-solve-inner-center-and-oblique-edges-center-only.txt',
                                                                         '777-UD-centers-oblique-edges-solve-center-only',
                                                                         'xxxxxxUUUxxUxUxxUUUxxxxxxxxxxxxDDDxxDxDxxDDDxxxxxx',
                                                                         False, # state_hex
                                                                         True)  # prune table

        self.lt_UD_solve_inner_centers_and_oblique_edges_edges_only = LookupTable(self,
                                                                         'lookup-table-7x7x7-step52-UD-solve-inner-center-and-oblique-edges-edges-only.txt',
                                                                         '777-UD-centers-oblique-edges-solve-edges-only',
                                                                         'xUUUxUxxxUUxxxUUxxxUxUUUxxDDDxDxxxDDxxxDDxxxDxDDDx',
                                                                         False, # state_hex
                                                                         True)  # prune table

        '''
        lookup-table-7x7x7-step50-UD-solve-inner-center-and-oblique-edges.txt
        =====================================================================
        1 steps has 9 entries (0 percent, 0.00x previous step)
        2 steps has 64 entries (0 percent, 7.11x previous step)
        3 steps has 412 entries (0 percent, 6.44x previous step)
        4 steps has 2643 entries (0 percent, 6.42x previous step)
        5 steps has 17,408 entries (0 percent, 6.59x previous step)
        6 steps has 110,881 entries (0 percent, 6.37x previous step)
        7 steps has 688,216 entries (2 percent, 6.21x previous step)
        8 steps has 4,078,714 entries (15 percent, 5.93x previous step)
        9 steps has 22,258,476 entries (81 percent, 5.46x previous step)

        Total: 27,156,823 entries
        '''
        self.lt_UD_solve_inner_centers_and_oblique_edges = LookupTableIDA(self,
                                                                         'lookup-table-7x7x7-step50-UD-solve-inner-center-and-oblique-edges.txt',
                                                                         '777-UD-centers-oblique-edges-solve',
                                                                         'xUUUxUUUUUUUUUUUUUUUxUUUxxDDDxDDDDDDDDDDDDDDDxDDDx',
                                                                         False, # state_hex
                                                                         moves_7x7x7,

                                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
                                                                          "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'"),            # do not mess up staged centers

                                                                         # prune tables
                                                                        (self.lt_UD_solve_inner_centers_and_oblique_edges_center_only,
                                                                         self.lt_UD_solve_inner_centers_and_oblique_edges_edges_only))

        '''
        lookup-table-7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges.txt
        ==================================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 88 entries (0 percent, 3.38x previous step)
        4 steps has 339 entries (0 percent, 3.85x previous step)
        5 steps has 1,130 entries (0 percent, 3.33x previous step)
        6 steps has 3,767 entries (1 percent, 3.33x previous step)
        7 steps has 11,254 entries (3 percent, 2.99x previous step)
        8 steps has 29,390 entries (8 percent, 2.61x previous step)
        9 steps has 62,492 entries (18 percent, 2.13x previous step)
        10 steps has 95,642 entries (27 percent, 1.53x previous step)
        11 steps has 88,567 entries (25 percent, 0.93x previous step)
        12 steps has 41,637 entries (12 percent, 0.47x previous step)
        13 steps has 8,211 entries (2 percent, 0.20x previous step)
        14 steps has 444 entries (0 percent, 0.05x previous step)
        15 steps has 8 entries (0 percent, 0.02x previous step)

        Total: 343,000 entries
        '''
        self.lt_LR_solve_inner_x_center_t_center_middle_oblique_edge = LookupTable(self,
                        'lookup-table-7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges.txt',
                        '777-LR-inner-x-center-t-center-and-middle-oblique-edges-LR-solve',
                        'xxLxxxLLLxLLLLLxLLLxxxLxxxxRxxxRRRxRRRRRxRRRxxxRxx',
                        False, # state_hex
                        True)  # prune table

        '''
        lookup-table-7x7x7-step62-LR-oblique-edges.txt
        ==============================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 96 entries (0 percent, 3.69x previous step)
        4 steps has 435 entries (0 percent, 4.53x previous step)
        5 steps has 1,778 entries (0 percent, 4.09x previous step)
        6 steps has 7,001 entries (2 percent, 3.94x previous step)
        7 steps has 22,728 entries (6 percent, 3.25x previous step)
        8 steps has 63,683 entries (18 percent, 2.80x previous step)
        9 steps has 117,320 entries (34 percent, 1.84x previous step)
        10 steps has 103,428 entries (30 percent, 0.88x previous step)
        11 steps has 25,078 entries (7 percent, 0.24x previous step)
        12 steps has 1,406 entries (0 percent, 0.06x previous step)
        13 steps has 16 entries (0 percent, 0.01x previous step)

        Total: 343,000 entries
        '''
        self.lt_LR_solve_oblique_edge = LookupTable(self,
                        'lookup-table-7x7x7-step62-LR-oblique-edges.txt',
                        '777-LR-oblique-edges-LR-solve',
                        'xLLLxLxxxLLxxxLLxxxLxLLLxxRRRxRxxxRRxxxRRxxxRxRRRx',
                        False, # state_hex
                        True)  # prune table

        '''
        lookup-table-7x7x7-step60-LR-solve-inner-center-and-oblique-edges.txt
        =====================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 96 entries (0 percent, 3.69x previous step)
        4 steps has 463 entries (0 percent, 4.82x previous step)
        5 steps has 2,084 entries (0 percent, 4.50x previous step)
        6 steps has 9,819 entries (0 percent, 4.71x previous step)
        7 steps has 43,314 entries (0 percent, 4.41x previous step)
        8 steps has 192,016 entries (1 percent, 4.43x previous step)
        9 steps has 822,604 entries (4 percent, 4.28x previous step)
        10 steps has 3,440,953 entries (18 percent, 4.18x previous step)
        11 steps has 13,643,789 entries (75 percent, 3.97x previous step)

        Total: 18,155,169 entries
        '''
        self.lt_LR_solve_inner_centers_and_oblique_edges = LookupTableIDA(self,
                                                         'lookup-table-7x7x7-step60-LR-solve-inner-center-and-oblique-edges.txt',
                                                         '777-LR-centers-oblique-edges-LR-solve',
                                                         'xLLLxLLLLLLLLLLLLLLLxLLLxxRRRxRRRRRRRRRRRRRRRxRRRx',

                                                         False, # state_hex
                                                         moves_7x7x7,

                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
                                                          "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
                                                          "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2"),                              # do not mess up solved UD

                                                         # prune tables
                                                         (self.lt_LR_solve_inner_x_center_t_center_middle_oblique_edge,
                                                          self.lt_LR_solve_oblique_edge))

        '''
        lookup-table-7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges.txt
        =================================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 88 entries (0 percent, 3.38x previous step)
        4 steps has 339 entries (0 percent, 3.85x previous step)
        5 steps has 1,130 entries (0 percent, 3.33x previous step)
        6 steps has 3,767 entries (1 percent, 3.33x previous step)
        7 steps has 11,254 entries (3 percent, 2.99x previous step)
        8 steps has 29,390 entries (8 percent, 2.61x previous step)
        9 steps has 62,492 entries (18 percent, 2.13x previous step)
        10 steps has 95,642 entries (27 percent, 1.53x previous step)
        11 steps has 88,567 entries (25 percent, 0.93x previous step)
        12 steps has 41,637 entries (12 percent, 0.47x previous step)
        13 steps has 8,211 entries (2 percent, 0.20x previous step)
        14 steps has 444 entries (0 percent, 0.05x previous step)
        15 steps has 8 entries (0 percent, 0.02x previous step)

        Total: 343,000 entries
        '''
        self.lt_FB_solve_inner_x_center_t_center_middle_oblique_edge = LookupTable(self,
                        'lookup-table-7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges.txt',
                        '777-FB-inner-x-center-t-center-and-middle-oblique-edges-FB-solve',
                        'xxFxxxFFFxFFFFFxFFFxxxFxxxxBxxxBBBxBBBBBxBBBxxxBxx',
                        False, # state_hex
                        True)  # prune table

        '''
        lookup-table-7x7x7-step72-FB-oblique-edges.txt
        ==============================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 96 entries (0 percent, 3.69x previous step)
        4 steps has 435 entries (0 percent, 4.53x previous step)
        5 steps has 1778 entries (0 percent, 4.09x previous step)
        6 steps has 7001 entries (2 percent, 3.94x previous step)
        7 steps has 22728 entries (6 percent, 3.25x previous step)
        8 steps has 63683 entries (18 percent, 2.80x previous step)
        9 steps has 117320 entries (34 percent, 1.84x previous step)
        10 steps has 103428 entries (30 percent, 0.88x previous step)
        11 steps has 25078 entries (7 percent, 0.24x previous step)
        12 steps has 1406 entries (0 percent, 0.06x previous step)
        13 steps has 16 entries (0 percent, 0.01x previous step)

        Total: 343000 entries
        '''
        self.lt_FB_solve_oblique_edge = LookupTable(self,
                        'lookup-table-7x7x7-step72-FB-oblique-edges.txt',
                        '777-FB-oblique-edges-FB-solve',
                        'xFFFxFxxxFFxxxFFxxxFxFFFxxBBBxBxxxBBxxxBBxxxBxBBBx',
                        False, # state_hex
                        True)  # prune table

        '''
        lookup-table-7x7x7-step70-FB-solve-inner-center-and-oblique-edges.txt
        =====================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 26 entries (0 percent, 5.20x previous step)
        3 steps has 96 entries (0 percent, 3.69x previous step)
        4 steps has 463 entries (0 percent, 4.82x previous step)
        5 steps has 2084 entries (0 percent, 4.50x previous step)
        6 steps has 9819 entries (0 percent, 4.71x previous step)
        7 steps has 43314 entries (0 percent, 4.41x previous step)
        8 steps has 192016 entries (1 percent, 4.43x previous step)
        9 steps has 822604 entries (4 percent, 4.28x previous step)
        10 steps has 3440953 entries (18 percent, 4.18x previous step)
        11 steps has 13643789 entries (75 percent, 3.97x previous step)

        Total: 18155169 entries
        '''
        self.lt_FB_solve_inner_centers_and_oblique_edges = LookupTableIDA(self,
                                                         'lookup-table-7x7x7-step70-FB-solve-inner-center-and-oblique-edges.txt',
                                                         '777-FB-centers-oblique-edges-FB-solve',
                                                         'xFFFxFFFFFFFFFFFFFFFxFFFxxBBBxBBBBBBBBBBBBBBBxBBBx',

                                                         False, # state_hex
                                                         moves_7x7x7,

                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
                                                          "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
                                                          "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2",                               # do not mess up solved UD
                                                          "L", "L'", "L2", "R", "R'", "R2"), # Do not mess up LRs reduced to 5x5x5 centers...dwalton is this needed?

                                                         # prune tables
                                                         (self.lt_FB_solve_inner_x_center_t_center_middle_oblique_edge,
                                                          self.lt_FB_solve_oblique_edge))

        '''
        lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt
        =======================================================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 54 entries (0 percent, 10.80x previous step)
        3 steps has 440 entries (0 percent, 8.15x previous step)
        4 steps has 3037 entries (0 percent, 6.90x previous step)
        5 steps has 23908 entries (0 percent, 7.87x previous step)
        6 steps has 182,804 entries (0 percent, 7.65x previous step)
        7 steps has 1,358,752 entries (1 percent, 7.43x previous step)
        8 steps has 10,002,315 entries (7 percent, 7.36x previous step)
        9 steps has 73,566,946 entries (56 percent, 7.35x previous step)
        10 steps has 44,068,381 entries (34 percent, 0.60x previous step)

        Total: 129,206,642 entries
        '''
        self.lt_LFRB_solve_inner_centers_and_oblique_edges = LookupTableIDA(self,
                                                         'lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt',
                                                         '777-LFRB-centers-oblique-edges-solve',
                                                         'xLLLxLLLLLLLLLLLLLLLxLLLxxFFFxFFFFFFFFFFFFFFFxFFFxxRRRxRRRRRRRRRRRRRRRxRRRxxBBBxBBBBBBBBBBBBBBBxBBBx',

                                                         False, # state_hex
                                                         moves_7x7x7,

                                                         ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
                                                          "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
                                                          "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2",                               # do not mess up solved UD
                                                          "L", "L'", "L2", "R", "R'", "R2"), # Do not mess up LRs reduced to 5x5x5 centers

                                                         # prune tables
                                                         (self.lt_LR_solve_inner_x_center_t_center_middle_oblique_edge,
                                                          self.lt_LR_solve_oblique_edge,
                                                          self.lt_FB_solve_inner_x_center_t_center_middle_oblique_edge,
                                                          self.lt_FB_solve_oblique_edge))

    def create_fake_555_from_inside_centers(self):

        # Create a fake 5x5x5 to stage the UD inner 5x5x5 centers
        fake_555 = RubiksCube555(solved_5x5x5)
        fake_555.lt_init()

        for x in xrange(1, 151):
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

    def create_fake_555_from_outside_centers(self):

        # Create a fake 5x5x5 to solve 7x7x7 centers (they have been reduced to a 5x5x5)
        fake_555 = RubiksCube555(solved_5x5x5)
        fake_555.lt_init()

        for x in xrange(1, 151):
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

        return fake_555

    def group_inside_UD_centers(self):
        fake_555 = self.create_fake_555_from_inside_centers()

        try:
            fake_555.lt_UD_centers_stage.solve(7)
        except NoIDASolution:
            fake_555.lt_UD_T_centers_stage.solve() # speed up IDA
            fake_555.lt_UD_centers_stage.solve(99)

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
        fake_555.lt_LR_centers_stage.solve(99)

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
        #self.print_cube()
        #fake_555.print_cube()
        fake_555.group_centers()

        for step in fake_555.solution:

            if step == 'CENTERS_SOLVED':
                continue

            if step.startswith('5'):
                step = '7' + step[1:]

            elif step.startswith('3'):
                raise Exception("5x5x5 solution has 3 wide turn")

            self.rotate(step)

        #self.print_cube()
        #fake_555.print_cube()

    def create_fake_666_centers(self):

        # Create a fake 6x6x6 to stage the outside UD oblique edges
        fake_666 = RubiksCube666(solved_6x6x6)
        fake_666.lt_init()

        for x in xrange(1, 217):
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

        #self.print_cube()
        #fake_666.print_cube()
        return fake_666

    def group_outside_UD_oblique_edges(self):
        fake_666 = self.create_fake_666_centers()

        try:
            fake_666.lt_UD_oblique_edge_pairing.solve(7)
        except NoIDASolution:
            fake_666.lt_UD_oblique_edge_pairing_left_only.solve() # speed up IDA
            fake_666.lt_UD_oblique_edge_pairing.solve(99)

        for step in fake_666.solution:

            if step.startswith('6'):
                step = '7' + step[1:]

            self.rotate(step)

    def group_outside_LR_oblique_edges(self):
        fake_666 = self.create_fake_666_centers()
        fake_666.lt_LR_oblique_edge_pairing.solve(99)

        for step in fake_666.solution:

            if step.startswith('6'):
                step = '7' + step[1:]

            self.rotate(step)

    def group_centers_guts(self):
        self.lt_init()

        # Uses 5x5x5 solver so stage the inner x-centers and inner t-centers for UD
        self.group_inside_UD_centers()

        # Uses 6x6x6 solver to pair the "outside" oblique edges for UD
        self.group_outside_UD_oblique_edges()
        log.info("Inside UD centers and outside UD oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Now pair the "inside" oblique edge with the already paired outside oblique edges...for UD
        #self.lt_UD_oblique_edge_pairing_middle_only.solve # speed up IDA
        self.lt_UD_oblique_edge_pairing.solve(99)
        log.info("UD oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Uses 5x5x5 solver so stage the inner x-centers and inner t-centers for LR
        self.group_inside_LR_centers()
        log.info('post group_inside_LR_centers')
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Uses 6x6x6 solver to pair the "outside" oblique edges for LR
        self.group_outside_LR_oblique_edges()
        log.info('post group_outside_LR_oblique_edges')
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Now pair the "inside" oblique edge with the already paired outside oblique edges...for LR
        #self.lt_LR_oblique_edge_pairing_middle_only.solve() # speed up IDA
        self.lt_LR_oblique_edge_pairing.solve(99)
        log.info("inner x-center and oblique edges staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Reduce UD centers to 5x5x5 by solving the inner x-centers, t-centers and oblique edges
        self.lt_UD_solve_inner_centers_and_oblique_edges.solve(99)
        log.info("UD inner-centers solved, UD oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Reduce LFRB centers to 5x5x5 via
        # Reduce LR centers to 5x5x5 by solving the inner x-centers, t-centers and oblique edges
        self.lt_LR_solve_inner_centers_and_oblique_edges.solve(99)
        log.info("LR inner-centers solved, UD oblique edges paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Reduce LR centers to 5x5x5 by solving the inner x-centers, t-centers and oblique edges
        self.lt_FB_solve_inner_centers_and_oblique_edges.solve(99)
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Reduce LRFB centers to 5x5x5 by solving the inner x-centers, t-centers and oblique edges
        self.lt_LFRB_solve_inner_centers_and_oblique_edges.solve(99)
        log.info("LFRB centers reduced to 5x5x5 centers, %d steps in" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        log.info("")
        log.info("")
        log.info("")
        log.info("")

        # Centers are now reduced to 5x5x5 centers
        self.solve_reduced_555_centers()
        log.info("Took %d steps to solve centers" % self.get_solution_len_minus_rotates(self.solution))
        self.print_cube()
        #sys.exit(0)

    def pair_inside_edges(self):
        fake_555 = RubiksCube555(solved_5x5x5)
        fake_555.lt_init()

        # Upper
        fake_555.state[2] = self.state[3]
        fake_555.state[3] = self.state[4]
        fake_555.state[4] = self.state[5]
        fake_555.state[6] = self.state[15]
        fake_555.state[11] = self.state[22]
        fake_555.state[16] = self.state[29]
        fake_555.state[10] = self.state[21]
        fake_555.state[15] = self.state[28]
        fake_555.state[20] = self.state[35]
        fake_555.state[22] = self.state[45]
        fake_555.state[23] = self.state[46]
        fake_555.state[24] = self.state[47]

        # Left
        fake_555.state[27] = self.state[52]
        fake_555.state[28] = self.state[53]
        fake_555.state[29] = self.state[54]
        fake_555.state[31] = self.state[64]
        fake_555.state[36] = self.state[71]
        fake_555.state[41] = self.state[78]
        fake_555.state[35] = self.state[70]
        fake_555.state[40] = self.state[77]
        fake_555.state[45] = self.state[84]
        fake_555.state[47] = self.state[94]
        fake_555.state[48] = self.state[95]
        fake_555.state[49] = self.state[96]

        # Front
        fake_555.state[52] = self.state[101]
        fake_555.state[53] = self.state[102]
        fake_555.state[54] = self.state[103]
        fake_555.state[56] = self.state[113]
        fake_555.state[61] = self.state[120]
        fake_555.state[66] = self.state[127]
        fake_555.state[60] = self.state[119]
        fake_555.state[65] = self.state[126]
        fake_555.state[70] = self.state[133]
        fake_555.state[72] = self.state[143]
        fake_555.state[73] = self.state[144]
        fake_555.state[74] = self.state[145]

        # Right
        fake_555.state[77] = self.state[150]
        fake_555.state[78] = self.state[151]
        fake_555.state[79] = self.state[152]
        fake_555.state[81] = self.state[162]
        fake_555.state[86] = self.state[169]
        fake_555.state[91] = self.state[176]
        fake_555.state[85] = self.state[168]
        fake_555.state[90] = self.state[175]
        fake_555.state[95] = self.state[182]
        fake_555.state[97] = self.state[192]
        fake_555.state[98] = self.state[193]
        fake_555.state[99] = self.state[194]

        # Back
        fake_555.state[102] = self.state[199]
        fake_555.state[103] = self.state[200]
        fake_555.state[104] = self.state[201]
        fake_555.state[106] = self.state[211]
        fake_555.state[111] = self.state[218]
        fake_555.state[116] = self.state[225]
        fake_555.state[110] = self.state[217]
        fake_555.state[115] = self.state[224]
        fake_555.state[120] = self.state[231]
        fake_555.state[122] = self.state[241]
        fake_555.state[123] = self.state[242]
        fake_555.state[124] = self.state[243]

        # Down
        fake_555.state[127] = self.state[248]
        fake_555.state[128] = self.state[249]
        fake_555.state[129] = self.state[250]
        fake_555.state[131] = self.state[260]
        fake_555.state[136] = self.state[267]
        fake_555.state[141] = self.state[274]
        fake_555.state[135] = self.state[266]
        fake_555.state[140] = self.state[273]
        fake_555.state[145] = self.state[280]
        fake_555.state[147] = self.state[290]
        fake_555.state[148] = self.state[291]
        fake_555.state[149] = self.state[292]
        fake_555.group_edges()

        for step in fake_555.solution:
            if step == 'EDGES_GROUPED':
                continue

            original_step = step
            if step.startswith('5'):
                step = '7' + step[1:]
            elif step in ("Uw", "Uw'", "Uw2",
                          "Lw", "Lw'", "Lw2",
                          "Fw", "Fw'", "Fw2",
                          "Rw", "Rw'", "Rw2",
                          "Bw", "Bw'", "Bw2",
                          "Dw", "Dw'", "Dw2"):
                step = '3' + step

            self.rotate(step)

        log.info("Inside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def pair_outside_edges(self):
        fake_555 = RubiksCube555(solved_5x5x5)
        fake_555.lt_init()

        # Upper
        fake_555.state[2] = self.state[2]
        fake_555.state[3] = self.state[4]
        fake_555.state[4] = self.state[6]
        fake_555.state[6] = self.state[8]
        fake_555.state[11] = self.state[22]
        fake_555.state[16] = self.state[36]
        fake_555.state[10] = self.state[14]
        fake_555.state[15] = self.state[28]
        fake_555.state[20] = self.state[42]
        fake_555.state[22] = self.state[44]
        fake_555.state[23] = self.state[46]
        fake_555.state[24] = self.state[48]

        # Left
        fake_555.state[27] = self.state[51]
        fake_555.state[28] = self.state[53]
        fake_555.state[29] = self.state[55]
        fake_555.state[31] = self.state[57]
        fake_555.state[36] = self.state[71]
        fake_555.state[41] = self.state[85]
        fake_555.state[35] = self.state[63]
        fake_555.state[40] = self.state[77]
        fake_555.state[45] = self.state[91]
        fake_555.state[47] = self.state[93]
        fake_555.state[48] = self.state[95]
        fake_555.state[49] = self.state[97]

        # Front
        fake_555.state[52] = self.state[100]
        fake_555.state[53] = self.state[102]
        fake_555.state[54] = self.state[104]
        fake_555.state[56] = self.state[106]
        fake_555.state[61] = self.state[120]
        fake_555.state[66] = self.state[134]
        fake_555.state[60] = self.state[112]
        fake_555.state[65] = self.state[126]
        fake_555.state[70] = self.state[140]
        fake_555.state[72] = self.state[142]
        fake_555.state[73] = self.state[144]
        fake_555.state[74] = self.state[146]

        # Right
        fake_555.state[77] = self.state[149]
        fake_555.state[78] = self.state[151]
        fake_555.state[79] = self.state[153]
        fake_555.state[81] = self.state[155]
        fake_555.state[86] = self.state[169]
        fake_555.state[91] = self.state[183]
        fake_555.state[85] = self.state[161]
        fake_555.state[90] = self.state[175]
        fake_555.state[95] = self.state[189]
        fake_555.state[97] = self.state[191]
        fake_555.state[98] = self.state[193]
        fake_555.state[99] = self.state[195]

        # Back
        fake_555.state[102] = self.state[198]
        fake_555.state[103] = self.state[200]
        fake_555.state[104] = self.state[202]
        fake_555.state[106] = self.state[204]
        fake_555.state[111] = self.state[218]
        fake_555.state[116] = self.state[232]
        fake_555.state[110] = self.state[210]
        fake_555.state[115] = self.state[224]
        fake_555.state[120] = self.state[238]
        fake_555.state[122] = self.state[240]
        fake_555.state[123] = self.state[242]
        fake_555.state[124] = self.state[244]

        # Down
        fake_555.state[127] = self.state[247]
        fake_555.state[128] = self.state[249]
        fake_555.state[129] = self.state[251]
        fake_555.state[131] = self.state[253]
        fake_555.state[136] = self.state[267]
        fake_555.state[141] = self.state[281]
        fake_555.state[135] = self.state[259]
        fake_555.state[140] = self.state[273]
        fake_555.state[145] = self.state[287]
        fake_555.state[147] = self.state[289]
        fake_555.state[148] = self.state[291]
        fake_555.state[149] = self.state[293]
        fake_555.group_edges()

        for step in fake_555.solution:
            if step == 'EDGES_GROUPED':
                continue

            if step.startswith('5'):
                step = '7' + step[1:]
            self.rotate(step)

        self.print_cube()
        log.info("Outside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def group_edges(self):

        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        self.pair_inside_edges()
        self.pair_outside_edges()
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


    '''
2017-06-27 00:07:28,725   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 1) did not find a match, took 0ms (0ms to rotate 22, 0ms to search primary table)
2017-06-27 00:07:28,725   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 1) rotates for prune tables are complete
2017-06-27 00:07:28,727   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 1) explore 11 branches from here (took 1ms to search prune tables)
2017-06-27 00:07:28,727   LookupTable.py     INFO:
2017-06-27 00:07:28,733   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 25 states (another 73 were cached) in 1ms, 25 guts calls, 1120945 avg left->right range, guts_cache has 55 entries
2017-06-27 00:07:28,733   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 2) did not find a match, took 6ms (4ms to rotate 239, 2ms to search primary table)
2017-06-27 00:07:28,735   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 2) rotates for prune tables are complete
2017-06-27 00:07:28,736   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 13 states (another 57 were cached) in 0ms, 13 guts calls, 58404 avg left->right range, guts_cache has 34 entries
2017-06-27 00:07:28,739   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 2) explore 68 branches from here (took 5ms to search prune tables)
2017-06-27 00:07:28,741   LookupTable.py     INFO:
2017-06-27 00:07:28,786   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 267 states (another 388 were cached) in 9ms, 267 guts calls, 115340 avg left->right range, guts_cache has 48 entries
2017-06-27 00:07:28,787   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 3) did not find a match, took 47ms (33ms to rotate 1480, 11ms to search primary table)
2017-06-27 00:07:28,795   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 3) rotates for prune tables are complete
2017-06-27 00:07:28,803   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 143 states (another 144 were cached) in 6ms, 143 guts calls, 8449 avg left->right range, guts_cache has 35 entries
2017-06-27 00:07:28,807   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 3) explore 293 branches from here (took 20ms to search prune tables)
2017-06-27 00:07:28,813   LookupTable.py     INFO:
2017-06-27 00:07:29,025   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 1468 states (another 1212 were cached) in 42ms, 1468 guts calls, 34152 avg left->right range, guts_cache has 25 entries
2017-06-27 00:07:29,027   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 4) did not find a match, took 219ms (167ms to rotate 6374, 46ms to search primary table)
2017-06-27 00:07:29,075   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 4) rotates for prune tables are complete
2017-06-27 00:07:29,080   LookupTable.py     INFO: 7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges: found 44 states (another 192 were cached) in 1ms, 44 guts calls, 21388 avg left->right range, guts_cache has 16 entries
2017-06-27 00:07:29,099   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 333 states (another 297 were cached) in 15ms, 333 guts calls, 4291 avg left->right range, guts_cache has 34 entries
2017-06-27 00:07:29,114   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 4) explore 718 branches from here (took 87ms to search prune tables)
2017-06-27 00:07:29,128   LookupTable.py     INFO:
2017-06-27 00:07:29,784   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 4155 states (another 2460 were cached) in 95ms, 4155 guts calls, 15053 avg left->right range, guts_cache has 5 entries
2017-06-27 00:07:29,788   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 5) did not find a match, took 673ms (552ms to rotate 15587, 107ms to search primary table)
2017-06-27 00:07:29,880   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 5) rotates for prune tables are complete
2017-06-27 00:07:29,892   LookupTable.py     INFO: 7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges: found 225 states (another 317 were cached) in 6ms, 225 guts calls, 5310 avg left->right range, guts_cache has 17 entries
2017-06-27 00:07:29,919   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 513 states (another 433 were cached) in 18ms, 513 guts calls, 2981 avg left->right range, guts_cache has 21 entries
2017-06-27 00:07:29,950   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 5) explore 1201 branches from here (took 161ms to search prune tables)
2017-06-27 00:07:29,971   LookupTable.py     INFO:
2017-06-27 00:07:31,154   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 8335 states (another 4556 were cached) in 172ms, 8335 guts calls, 8282 avg left->right range, guts_cache has 10 entries
2017-06-27 00:07:31,162   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 6) did not find a match, took 1211ms (993ms to rotate 26101, 197ms to search primary table)
2017-06-27 00:07:31,357   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 6) rotates for prune tables are complete
2017-06-27 00:07:31,378   LookupTable.py     INFO: 7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges: found 136 states (another 740 were cached) in 6ms, 136 guts calls, 8951 avg left->right range, guts_cache has 18 entries
2017-06-27 00:07:31,415   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 619 states (another 576 were cached) in 22ms, 619 guts calls, 2532 avg left->right range, guts_cache has 7 entries
2017-06-27 00:07:31,480   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 6) explore 2196 branches from here (took 317ms to search prune tables)
2017-06-27 00:07:31,521   LookupTable.py     INFO:
2017-06-27 00:07:34,027   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 16215 states (another 8439 were cached) in 332ms, 16215 guts calls, 6176 avg left->right range, guts_cache has 13 entries
2017-06-27 00:07:34,043   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 7) did not find a match, took 0:00:02.563471 (0:00:02.131635 to rotate 47896, 389ms to search primary table)
2017-06-27 00:07:34,473   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 7) rotates for prune tables are complete
2017-06-27 00:07:34,536   LookupTable.py     INFO: 7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges: found 1107 states (another 851 were cached) in 33ms, 1107 guts calls, 1472 avg left->right range, guts_cache has 5 entries
2017-06-27 00:07:34,582   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 633 states (another 673 were cached) in 19ms, 633 guts calls, 2411 avg left->right range, guts_cache has 7 entries
2017-06-27 00:07:34,690   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 7) explore 3901 branches from here (took 646ms to search prune tables)
2017-06-27 00:07:34,767   LookupTable.py     INFO:
2017-06-27 00:07:39,469   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 31037 states (another 11786 were cached) in 474ms, 31037 guts calls, 2534 avg left->right range, guts_cache has 26 entries
2017-06-27 00:07:39,499   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 8) did not find a match, took 0:00:04.807653 (0:00:04.159629 to rotate 84786, 572ms to search primary table)
2017-06-27 00:07:40,337   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 8) rotates for prune tables are complete
2017-06-27 00:07:40,401   LookupTable.py     INFO: 7x7x7-step61-LR-inner-x-center-t-center-and-middle-oblique-edges: found 294 states (another 1082 were cached) in 14ms, 294 guts calls, 4432 avg left->right range, guts_cache has 14 entries
2017-06-27 00:07:40,464   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 381 states (another 520 were cached) in 12ms, 381 guts calls, 3533 avg left->right range, guts_cache has 11 entries
2017-06-27 00:07:40,663   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 8) explore 2484 branches from here (took 1163ms to search prune tables)
2017-06-27 00:07:40,712   LookupTable.py     INFO:
2017-06-27 00:07:44,072   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 17204 states (another 9429 were cached) in 325ms, 17204 guts calls, 3841 avg left->right range, guts_cache has 32 entries
2017-06-27 00:07:44,096   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 9) did not find a match, took 0:00:03.432848 (0:00:02.988046 to rotate 53826, 396ms to search primary table)
2017-06-27 00:07:44,553   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 9) rotates for prune tables are complete
2017-06-27 00:07:44,616   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 71 states (another 310 were cached) in 3ms, 71 guts calls, 14186 avg left->right range, guts_cache has 26 entries
2017-06-27 00:07:44,739   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 9) explore 1939 branches from here (took 642ms to search prune tables)
2017-06-27 00:07:44,775   LookupTable.py     INFO:
2017-06-27 00:07:47,886   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 13831 states (another 5061 were cached) in 190ms, 13831 guts calls, 3964 avg left->right range, guts_cache has 43 entries
2017-06-27 00:07:47,901   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 10) did not find a match, took 0:00:03.161235 (0:00:02.889931 to rotate 42030, 235ms to search primary table)
2017-06-27 00:07:48,226   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 10) rotates for prune tables are complete
2017-06-27 00:07:48,275   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 12 states (another 107 were cached) in 0ms, 12 guts calls, 50017 avg left->right range, guts_cache has 22 entries
2017-06-27 00:07:48,390   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 10) explore 418 branches from here (took 489ms to search prune tables)
2017-06-27 00:07:48,402   LookupTable.py     INFO:
2017-06-27 00:07:49,096   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 3951 states (another 1888 were cached) in 12ms, 990 guts calls, 12090 avg left->right range, guts_cache has 63 entries
2017-06-27 00:07:49,101   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 11), took 710ms (671ms to rotate 9092, 27ms to search primary table)
2017-06-27 00:07:49,101   LookupTable.py  WARNING: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 11 (max step 11), found match in 0:00:22.945597, steps F Uw2 B' 3Uw2 Dw2 B2 3Uw2 F B Uw2 F, state 4079/9092 in states_to_check




2017-06-27 00:04:03,440   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 1) did not find a match, took 0ms (0ms to rotate 16, 0ms to search primary table)
2017-06-27 00:04:03,440   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 1) rotates for prune tables are complete
2017-06-27 00:04:03,460   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 1) explore 11 branches from here (took 19ms to search prune tables)
2017-06-27 00:04:03,460   LookupTable.py     INFO:
2017-06-27 00:04:03,463   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 2) did not find a match, took 3ms (2ms to rotate 173, 0ms to search primary table)
2017-06-27 00:04:03,465   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 2) rotates for prune tables are complete
2017-06-27 00:04:03,478   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 2) explore 74 branches from here (took 15ms to search prune tables)
2017-06-27 00:04:03,480   LookupTable.py     INFO:
2017-06-27 00:04:03,515   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 3) did not find a match, took 36ms (34ms to rotate 1170, 0ms to search primary table)
2017-06-27 00:04:03,528   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 3) rotates for prune tables are complete
2017-06-27 00:04:03,541   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 3) explore 460 branches from here (took 26ms to search prune tables)
2017-06-27 00:04:03,548   LookupTable.py     INFO:
2017-06-27 00:04:03,756   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 121 states (another 2675 were cached) in 10ms, 121 guts calls, 232727 avg left->right range, guts_cache has 27 entries
2017-06-27 00:04:03,758   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 4) did not find a match, took 216ms (193ms to rotate 7275, 17ms to search primary table)
2017-06-27 00:04:03,844   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 4) rotates for prune tables are complete
2017-06-27 00:04:03,861   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 91 states (another 1561 were cached) in 3ms, 91 guts calls, 11927 avg left->right range, guts_cache has 30 entries
2017-06-27 00:04:03,870   LookupTable.py     INFO: 7x7x7-step72-FB-oblique-edges: found 52 states (another 1707 were cached) in 2ms, 52 guts calls, 20047 avg left->right range, guts_cache has 22 entries
2017-06-27 00:04:03,899   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 4) explore 2613 branches from here (took 140ms to search prune tables)
2017-06-27 00:04:03,935   LookupTable.py     INFO:
2017-06-27 00:04:05,461   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 4190 states (another 11212 were cached) in 91ms, 4190 guts calls, 7647 avg left->right range, guts_cache has 17 entries
2017-06-27 00:04:05,477   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 5) did not find a match, took 1578ms (1405ms to rotate 41335, 135ms to search primary table)
2017-06-27 00:04:05,948   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 5) rotates for prune tables are complete
2017-06-27 00:04:06,099   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 1807 states (another 4820 were cached) in 65ms, 1807 guts calls, 1029 avg left->right range, guts_cache has 17 entries
2017-06-27 00:04:06,191   LookupTable.py     INFO: 7x7x7-step72-FB-oblique-edges: found 1557 states (another 5698 were cached) in 55ms, 1557 guts calls, 1384 avg left->right range, guts_cache has 29 entries
2017-06-27 00:04:06,297   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 5) explore 9096 branches from here (took 819ms to search prune tables)
2017-06-27 00:04:06,425   LookupTable.py     INFO:
2017-06-27 00:04:12,553   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 30053 states (another 25016 were cached) in 326ms, 30053 guts calls, 1120 avg left->right range, guts_cache has 22 entries
2017-06-27 00:04:12,598   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 6) did not find a match, took 0:00:06.301128 (0:00:05.671549 to rotate 143839, 501ms to search primary table)
2017-06-27 00:04:14,278   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 6) rotates for prune tables are complete
2017-06-27 00:04:14,898   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 7070 states (another 8882 were cached) in 333ms, 7070 guts calls, 371 avg left->right range, guts_cache has 24 entries
2017-06-27 00:04:15,297   LookupTable.py     INFO: 7x7x7-step72-FB-oblique-edges: found 9197 states (another 10564 were cached) in 287ms, 9197 guts calls, 236 avg left->right range, guts_cache has 11 entries
2017-06-27 00:04:15,664   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 6) explore 12148 branches from here (took 0:00:03.065532 to search prune tables)
2017-06-27 00:04:15,856   LookupTable.py     INFO:
2017-06-27 00:04:26,958   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 50586 states (another 33966 were cached) in 543ms, 50586 guts calls, 680 avg left->right range, guts_cache has 23 entries
2017-06-27 00:04:27,026   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 7) did not find a match, took 0:00:11.358797 (0:00:10.349378 to rotate 192023, 820ms to search primary table)
2017-06-27 00:04:30,318   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 7) rotates for prune tables are complete
2017-06-27 00:04:30,957   LookupTable.py     INFO: 7x7x7-step71-FB-inner-x-center-t-center-and-middle-oblique-edges: found 7549 states (another 10707 were cached) in 212ms, 7549 guts calls, 277 avg left->right range, guts_cache has 4 entries
2017-06-27 00:04:31,473   LookupTable.py     INFO: 7x7x7-step72-FB-oblique-edges: found 10761 states (another 14486 were cached) in 310ms, 10761 guts calls, 224 avg left->right range, guts_cache has 7 entries
2017-06-27 00:04:31,986   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 7) explore 7538 branches from here (took 0:00:04.958917 to search prune tables)
2017-06-27 00:04:32,122   LookupTable.py     INFO:
2017-06-27 00:04:40,291   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: found 35320 states (another 24097 were cached) in 352ms, 24593 guts calls, 1225 avg left->right range, guts_cache has 34 entries
2017-06-27 00:04:40,325   LookupTable.py     INFO: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 8), took 0:00:08.338393 (0:00:07.706158 to rotate 119201, 496ms to search primary table)
2017-06-27 00:04:40,325   LookupTable.py  WARNING: 7x7x7-step70-LFRB-solve-inner-center-and-oblique-edges: IDA threshold 14 (max step 8), found match in 0:00:47.706497, steps F2 Uw2 B 3Uw2 3Dw2 B 3Uw2 B2, state 74289/119201 in states_to_check
    '''
