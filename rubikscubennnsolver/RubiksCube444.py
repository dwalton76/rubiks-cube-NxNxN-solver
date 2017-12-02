
from copy import copy
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.LookupTable import (
    LookupTable,
    LookupTableIDA,
    NoSteps,
    NoIDASolution,
)
from subprocess import check_output
from pprint import pformat
import itertools
import logging
import sys

log = logging.getLogger(__name__)


moves_4x4x4 = ("U", "U'", "U2", "Uw", "Uw'", "Uw2",
               "L", "L'", "L2", "Lw", "Lw'", "Lw2",
               "F" , "F'", "F2", "Fw", "Fw'", "Fw2",
               "R" , "R'", "R2", "Rw", "Rw'", "Rw2",
               "B" , "B'", "B2", "Bw", "Bw'", "Bw2",
               "D" , "D'", "D2", "Dw", "Dw'", "Dw2")
solved_4x4x4 = 'UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB'


# Move a wing to (44, 57)
lookup_table_444_last_two_edges_place_F_east = {
    (2, 67)  : "B' R2",
    (3, 66)  : "U R'",
    (5, 18)  : "U2 R'",
    (9, 19)  : "U B' R2",
    (14, 34) : "U' R'",
    (15, 35) : "U F' U' F",
    (8, 51)  : "F' U F",
    (12, 50) : "R'",
    (21, 72) : "B' U R'",
    (25, 76) : "B2 R2",
    (30, 89) : "F D F'",
    (31, 85) : "D2 R",
    (40, 53) : "R U' B' R2",
    (44, 57) : "",
    (46, 82) : "D F D' F'",
    (47, 83) : "D R",
    (56, 69) : "R2",
    (60, 73) : "B U R'",
    (62, 88) : "F D' F'",
    (63, 92) : "R",
    (78, 95) : "B R2",
    (79, 94) : "D' R",
}


# Move a wing to (40, 53)
lookup_table_444_sister_wing_to_F_east = {
    (2, 67)  : "U R'",
    (3, 66)  : "B' R2",
    (5, 18)  : "U B' R2",
    (9, 19)  : "U2 R'",
    (14, 34) : "L F L'",
    (15, 35) : "U' R'",
    (8, 51)  : "R'",
    (12, 50) : "F' U F",
    (21, 72) : "B2 R2",
    (25, 76) : "B D' R",
    (30, 89) : "D2 R",
    (31, 85) : "F D F'",
    (40, 53) : "",
    (44, 57) : "F D F' R",
    (46, 82) : "D R",
    (47, 83) : "D2 B R2",
    (56, 69) : "B U R'",
    (60, 73) : "R2",
    (62, 88) : "R",
    (63, 92) : "F D' F'",
    (78, 95) : "D' R",
    (79, 94) : "B R2",
}


# Move a wing to (5, 18)
lookup_table_444_sister_wing_to_U_west = {
    (2, 67)  : "L' B L",
    (3, 66)  : "U'",
    (5, 18)  : "",
    (9, 19)  : "L' B' L U'",
    (14, 34) : "U",
    (15, 35) : "F' L' F",
    (8, 51)  : "U' B F L F'",
    (12, 50) : "U2",
    (21, 72) : "B' U'",
    (25, 76) : "L U L' U'",
    (30, 89) : "L B' L' U'",
    (31, 85) : "D' B2 U'",
    (37, 24) : None,
    #(40, 53) : "",
    #(44, 57) : "",
    (46, 82) : "F L' F'",
    (47, 83) : "D2 B2 U'",
    (56, 69) : "R' U2 R",
    (60, 73) : "B U'",
    (62, 88) : "R' B R U'",
    (63, 92) : "D B2 U'",
    (78, 95) : "B2 U'",
    (79, 94) : "B2 U'",
}


class RubiksCube444(RubiksCube):

    def __init__(self, state, order, colormap=None, avoid_pll=True, debug=False):
        RubiksCube.__init__(self, state, order, colormap, debug)
        self.avoid_pll = avoid_pll
        self.edge_mapping = {}

        if debug:
            log.setLevel(logging.DEBUG)

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
        corners = (1, 4, 13, 16,
                   17, 20, 29, 32,
                   33, 36, 45, 48,
                   49, 52, 61, 64,
                   65, 68, 77, 80,
                   81, 84, 93, 96)

        centers = (6, 7, 10, 11,
                   22, 23, 26, 27,
                   38, 39, 42, 43,
                   54, 55, 58, 59,
                   70, 71, 74, 75,
                   86, 87, 90, 91)

        edge_orbit_0 = (2, 3, 8, 12, 15, 14, 9, 5,
                        18, 19, 24, 28, 31, 30, 25, 21,
                        34, 35, 40, 44, 47, 46, 41, 37,
                        50, 51, 56, 60, 62, 63, 57, 53,
                        66, 67, 72, 76, 79, 78, 73, 69,
                        82, 83, 88, 92, 95, 94, 89, 85)

        self._sanity_check('corners', corners, 4)
        self._sanity_check('centers', centers, 4)
        self._sanity_check('edge-orbit-0', edge_orbit_0, 8)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # brainstorm
        # Today we typically stage all centers and then solve them
        # - Staging is 24!/(8! * 8! * 8!) or 9,465,511,770
        # - We have three prune tables (UD, LR, and FB) of 24!/(8! * 16!) or 735,471
        #
        # option #1 - solve all centers at once
        # - would be 24!/(4! * 4! * 4! * 4! * 4! * 4!) or 3,246,670,537,110,000
        # - three prune tables (UD, LR, and FB) of 24!/(4! * 4! * 16!) or 51,482,970
        # - 51,482,970 / 3,246,670,537,110,000 is 0.000 000 015 8571587, IDA might take a few hours
        # - I've done this before and it removes ~6 steps when solving centers. We
        #   currently average 64 steps to solve a 4x4x4 but the tsai solver averages 55....so
        #   this would take a few hours to run but solutions still wouldn't be as short as
        #   the tsai solver.
        # - feasible but not worth it
        #
        #
        # option #2 - combine tsai phases 1 and 2
        # - this would be staging UD, FB centers, solving LR centers and orienting all edges
        # - orienting edges is 2,704,156
        # - centers is 24!/(4! * 4! * 8! * 8!) or 662,585,823,900
        # - so would be 662,585,823,900 * 2,704,156 or 1,791,735,431,214,128,400
        # - 2,704,156 / 1,791,735,431,214,128,400 or 0.000 000 000 001 5092, IDA might take weeks
        # - 662,585,823,900 / 1,791,735,431,214,128,400 or 0.000 000 369 8011505, IDA would be
        #   fast but that is with a 662 billion entry prune table
        # - a LR prune table would be 24!/(4! * 4! * 16!) or 51,482,970
        #   - 51,482,970 / 1,791,735,431,214,128,400 or 0.000 000 000 028 7336, IDA might take weeks
        # - a UDFB prune table would be 24!/(8! * 8! * 8!) or 9,465,511,770
        #   - 9,465,511,770 / 1,791,735,431,214,128,400 or 0.000 000 005 2828736, IDA would take a few hours
        #     9 billion would be a huge prune table
        # - probably not feasible


        # There are four CPU "modes" we can run in:
        #
        # min    : Uses the least CPU but produces a longer solution.
        #          This will stage UD centers first, then LFRB centers.
        #
        # normal : Uses a middle ground of CPU and produces not the shortest or longest solution.
        #          This will stage all centers at once.
        #
        # max    : Uses more CPU and produce a shorter solution
        #          This will stage all centers at once.
        #
        # tsai   : Uses the most CPU but produces the shortest solution

        # ==============
        # Phase 1 tables
        # ==============
        '''
        lookup-table-4x4x4-step11-UD-centers-stage.txt
        lookup-table-4x4x4-step12-LR-centers-stage.txt
        lookup-table-4x4x4-step13-FB-centers-stage.txt
        ==============================================
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
        if self.cpu_mode == 'min':

            # Stage UD centers
            self.lt_UD_centers_stage = LookupTable(self,
                                                   'lookup-table-4x4x4-step11-UD-centers-stage.txt',
                                                  '444-UD-centers-stage',
                                                  'f0000f',
                                                   True, # state hex
                                                   linecount=735471)

        elif self.cpu_mode in ('normal', 'max'):

            # Stage all centers via IDA
            self.lt_UD_centers_stage = LookupTable(self,
                                                   'lookup-table-4x4x4-step11-UD-centers-stage.txt',
                                                  '444-UD-centers-stage',
                                                  'f0000f',
                                                   True, # state hex
                                                   linecount=735471)

            self.lt_LR_centers_stage = LookupTable(self,
                                                   'lookup-table-4x4x4-step12-LR-centers-stage.txt',
                                                   '444-LR-centers-stage',
                                                   '0f0f00',
                                                    True, # state hex
                                                    linecount=735471)

            self.lt_FB_centers_stage = LookupTable(self,
                                                   'lookup-table-4x4x4-step13-FB-centers-stage.txt',
                                                   '444-FB-centers-stage',
                                                   '00f0f0',
                                                    True, # state hex
                                                    linecount=735471)

            '''
            lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt
            ==================================================
            1 steps has 7 entries (0 percent, 0.00x previous step)
            2 steps has 135 entries (0 percent, 19.29x previous step)
            3 steps has 2,286 entries (0 percent, 16.93x previous step)
            4 steps has 36,728 entries (0 percent, 16.07x previous step)
            5 steps has 562,932 entries (6 percent, 15.33x previous step)
            6 steps has 8,047,054 entries (93 percent, 14.29x previous step)

            Total: 8,649,142 entries
            '''
            self.lt_ULFRBD_centers_stage = LookupTableIDA(self,
                                                   'lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt',
                                                   '444-ULFRBD-centers-stage',
                                                   'UUUULLLLFFFFLLLLFFFFUUUU',
                                                    False, # state hex
                                                    moves_4x4x4,
                                                    (), # illegal_moves

                                                    # prune tables
                                                    (self.lt_UD_centers_stage,
                                                     self.lt_LR_centers_stage,
                                                     self.lt_FB_centers_stage),
                                                    linecount=8649142)

            # Built via stats/crunch-stats-444-centers-stage.py
            lt_ULFRBD_centers_stage_heuristic_stats_min = {
                (2, 2, 3) : 5,
                (2, 3, 2) : 5,
                (3, 2, 2) : 5,
                (3, 3, 3) : 4,
                (3, 5, 6) : 7,
                (3, 6, 5) : 7,
                (3, 6, 7) : 9,
                (3, 7, 6) : 9,
                (4, 4, 4) : 5,
                (4, 4, 6) : 7,
                (4, 5, 7) : 8,
                (4, 6, 4) : 7,
                (4, 6, 5) : 7,
                (4, 6, 7) : 10,
                (4, 7, 6) : 8,
                (4, 7, 7) : 10,
                (5, 5, 5) : 6,
                (5, 5, 7) : 8,
                (5, 6, 3) : 7,
                (5, 6, 4) : 7,
                (5, 7, 5) : 8,
                (5, 7, 6) : 8,
                (5, 7, 7) : 8,
                (6, 2, 6) : 7,
                (6, 3, 5) : 7,
                (6, 4, 4) : 7,
                (6, 5, 5) : 7,
                (6, 6, 6) : 7,
                (6, 6, 7) : 8,
                (6, 6, 8) : 11,
                (6, 7, 5) : 8,
                (6, 7, 7) : 8,
                (7, 3, 6) : 8,
                (7, 4, 6) : 8,
                (7, 4, 7) : 9,
                (7, 5, 4) : 9,
                (7, 5, 5) : 8,
                (7, 5, 7) : 9,
                (7, 5, 8) : 11,
                (7, 6, 7) : 9,
                (7, 7, 5) : 8,
                (7, 7, 6) : 9,
                (7, 7, 7) : 9,
            }

            lt_ULFRBD_centers_stage_heuristic_stats_median = {
                (2, 2, 3) : 5,
                (2, 3, 2) : 5,
                (2, 4, 3) : 5,
                (2, 6, 6) : 7,
                (3, 2, 2) : 5,
                (3, 3, 3) : 6,
                (3, 5, 6) : 7,
                (3, 6, 5) : 7,
                (3, 6, 6) : 8,
                (3, 6, 7) : 9,
                (3, 7, 6) : 9,
                (4, 2, 3) : 5,
                (4, 3, 4) : 5,
                (4, 4, 4) : 6,
                (4, 4, 5) : 6,
                (4, 4, 6) : 8,
                (4, 5, 4) : 6,
                (4, 5, 5) : 6,
                (4, 5, 6) : 7,
                (4, 5, 7) : 9,
                (4, 6, 4) : 7,
                (4, 6, 5) : 8,
                (4, 6, 6) : 8,
                (4, 6, 7) : 10,
                (4, 7, 6) : 10,
                (4, 7, 7) : 10,
                (5, 3, 4) : 6,
                (5, 4, 5) : 6,
                (5, 4, 6) : 7,
                (5, 5, 3) : 6,
                (5, 5, 4) : 6,
                (5, 5, 5) : 7,
                (5, 5, 6) : 8,
                (5, 5, 7) : 9,
                (5, 6, 3) : 7,
                (5, 6, 4) : 8,
                (5, 6, 5) : 8,
                (5, 6, 6) : 8,
                (5, 6, 7) : 9,
                (5, 7, 5) : 9,
                (5, 7, 6) : 9,
                (5, 7, 7) : 10,
                (6, 2, 6) : 7,
                (6, 3, 5) : 8,
                (6, 3, 6) : 7,
                (6, 4, 4) : 8,
                (6, 4, 5) : 7,
                (6, 4, 6) : 7,
                (6, 4, 7) : 9,
                (6, 5, 3) : 8,
                (6, 5, 4) : 8,
                (6, 5, 5) : 8,
                (6, 5, 6) : 9,
                (6, 5, 7) : 9,
                (6, 6, 3) : 8,
                (6, 6, 4) : 8,
                (6, 6, 5) : 9,
                (6, 6, 6) : 9,
                (6, 6, 7) : 10,
                (6, 6, 8) : 11,
                (6, 7, 4) : 9,
                (6, 7, 5) : 9,
                (6, 7, 6) : 10,
                (6, 7, 7) : 10,
                (7, 3, 6) : 8,
                (7, 4, 5) : 9,
                (7, 4, 6) : 8,
                (7, 4, 7) : 9,
                (7, 5, 4) : 9,
                (7, 5, 5) : 10,
                (7, 5, 6) : 9,
                (7, 5, 7) : 10,
                (7, 5, 8) : 11,
                (7, 6, 4) : 8,
                (7, 6, 5) : 10,
                (7, 6, 6) : 10,
                (7, 6, 7) : 10,
                (7, 7, 5) : 10,
                (7, 7, 6) : 10,
                (7, 7, 7) : 10,
            }

            self.lt_ULFRBD_centers_stage.heuristic_stats = lt_ULFRBD_centers_stage_heuristic_stats_min
            self.lt_ULFRBD_centers_stage.heuristic_stats = lt_ULFRBD_centers_stage_heuristic_stats_median

        elif self.cpu_mode == 'tsai':

            # Stage LR centers
            self.lt_LR_centers_stage = LookupTable(self,
                                                   'lookup-table-4x4x4-step12-LR-centers-stage.txt',
                                                   '444-LR-centers-stage',
                                                   '0f0f00',
                                                    True, # state hex
                                                    linecount=735471)

        else:
            raise Exception("We should not be here, cpu_mode %s" % self.cpu_mode)

        # =============
        # Phase2 tables
        # =============
        if self.cpu_mode == 'min':

            # Stage LR and FB centers
            '''
            lookup-table-4x4x4-step20-LFRB-centers-stage.txt
            ================================================
            1 steps has 3 entries (0 percent, 0.00x previous step)
            2 steps has 29 entries (0 percent, 9.67x previous step)
            3 steps has 234 entries (1 percent, 8.07x previous step)
            4 steps has 1246 entries (9 percent, 5.32x previous step)
            5 steps has 4466 entries (34 percent, 3.58x previous step)
            6 steps has 6236 entries (48 percent, 1.40x previous step)
            7 steps has 656 entries (5 percent, 0.11x previous step)

            Total: 12870 entries
            '''
            self.lt_LFRB_centers_stage = LookupTable(self,
                                                   'lookup-table-4x4x4-step20-LFRB-centers-stage.txt',
                                                   '444-LFRB-centers-stage',
                                                   'xxxxLLLLFFFFLLLLFFFFxxxx',
                                                    False, # state hex
                                                    linecount=12870)

        elif self.cpu_mode in ('normal', 'max'):

            # Solve staged centers
            '''
            lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt
            ==================================================
            1 steps has 7 entries (0 percent)
            2 steps has 99 entries (0 percent)
            3 steps has 996 entries (0 percent)
            4 steps has 6,477 entries (1 percent)
            5 steps has 23,540 entries (6 percent)
            6 steps has 53,537 entries (15 percent)
            7 steps has 86,464 entries (25 percent)
            8 steps has 83,240 entries (24 percent)
            9 steps has 54,592 entries (15 percent)
            10 steps has 29,568 entries (8 percent)
            11 steps has 4,480 entries (1 percent)

            Total: 343,000 entries
            '''
            self.lt_ULFRBD_centers_solve = LookupTable(self,
                                                       'lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt',
                                                       '444-ULFRBD-centers-solve',
                                                       'UUUULLLLFFFFRRRRBBBBDDDD',
                                                       False, # state hex
                                                       linecount=343000)

        elif self.cpu_mode == 'tsai':
            # - orient the edges into high/low groups
            # - solve LR centers to one of 12 states
            # - stage UD and FB centers
            self.orient_edges = tsai_phase2_orient_edges

            '''
            lookup-table-4x4x4-step61-centers.txt
            =====================================
            1 steps has 46 entries (0 percent, 0.00x previous step)
            2 steps has 384 entries (0 percent, 8.35x previous step)
            3 steps has 3,354 entries (0 percent, 8.73x previous step)
            4 steps has 22,324 entries (2 percent, 6.66x previous step)
            5 steps has 113,276 entries (12 percent, 5.07x previous step)
            6 steps has 338,860 entries (37 percent, 2.99x previous step)
            7 steps has 388,352 entries (43 percent, 1.15x previous step)
            8 steps has 34,048 entries (3 percent, 0.09x previous step)
            9 steps has 256 entries (0 percent, 0.01x previous step)

            Total: 900,900 entries
            '''
            self.lt_tsai_phase2_centers = LookupTable(self,
                                                      'lookup-table-4x4x4-step61-centers.txt',
                                                      '444-tsai-phase2-centers',
                                                      ('UUUULLLLFFFFRRRRFFFFUUUU',
                                                       'UUUURRRRFFFFLLLLFFFFUUUU',
                                                       'UUUULLRRFFFFRRLLFFFFUUUU',
                                                       'UUUULLRRFFFFLLRRFFFFUUUU',
                                                       'UUUURRLLFFFFRRLLFFFFUUUU',
                                                       'UUUURRLLFFFFLLRRFFFFUUUU',
                                                       'UUUURLRLFFFFRLRLFFFFUUUU',
                                                       'UUUURLRLFFFFLRLRFFFFUUUU',
                                                       'UUUULRLRFFFFRLRLFFFFUUUU',
                                                       'UUUULRLRFFFFLRLRFFFFUUUU',
                                                       'UUUURLLRFFFFLRRLFFFFUUUU',
                                                       'UUUULRRLFFFFRLLRFFFFUUUU'),
                                                      False, # state hex
                                                      linecount=900900)

            '''
            lookup-table-4x4x4-step62-edges.txt
            ===================================
            1 steps has 5 entries (0 percent, 0.00x previous step)
            2 steps has 62 entries (0 percent, 12.40x previous step)
            3 steps has 906 entries (0 percent, 14.61x previous step)
            4 steps has 11,163 entries (0 percent, 12.32x previous step)
            5 steps has 127,148 entries (4 percent, 11.39x previous step)
            6 steps has 889,398 entries (32 percent, 6.99x previous step)
            7 steps has 1,553,434 entries (57 percent, 1.75x previous step)
            8 steps has 122,040 entries (4 percent, 0.08x previous step)

            Total: 2,704,156 entries
            '''
            self.lt_tsai_phase2_edges = LookupTsaiPhase2Edges(self,
                                                              'lookup-table-4x4x4-step62-edges.txt',
                                                              '444-tsai-phase2-edges',
                                                              'UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
                                                              False, # state hex
                                                              linecount=2704156)

            self.lt_tsai_phase2 = LookupTsaiPhase2IDA(self,
                                                      'lookup-table-4x4x4-step60-dummy.txt',
                                                      '444-tsai-phase2',
                                                      'TBD',
                                                      False, # state_hex
                                                      moves_4x4x4,
                                                      ("Fw", "Fw'", "Bw", "Bw'",
                                                       "Uw", "Uw'", "Dw", "Dw'"), # illegal_moves

                                                      # prune tables
                                                      (self.lt_tsai_phase2_centers,),
                                                      #(self.lt_tsai_phase2_centers,
                                                      # self.lt_tsai_phase2_edges),
                                                      linecount=0)

        else:
            raise Exception("We should not be here, cpu_mode %s" % self.cpu_mode)

        # =============
        # Phase3 tables
        # =============
        if self.cpu_mode == 'min':

            # Solve staged centers
            '''
            lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt
            ==================================================
            1 steps has 7 entries (0 percent)
            2 steps has 99 entries (0 percent)
            3 steps has 996 entries (0 percent)
            4 steps has 6,477 entries (1 percent)
            5 steps has 23,540 entries (6 percent)
            6 steps has 53,537 entries (15 percent)
            7 steps has 86,464 entries (25 percent)
            8 steps has 83,240 entries (24 percent)
            9 steps has 54,592 entries (15 percent)
            10 steps has 29,568 entries (8 percent)
            11 steps has 4,480 entries (1 percent)

            Total: 343,000 entries
            '''
            self.lt_ULFRBD_centers_solve = LookupTable(self,
                                                       'lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt',
                                                       '444-ULFRBD-centers-solve',
                                                       'UUUULLLLFFFFRRRRBBBBDDDD',
                                                       False, # state hex
                                                       linecount=343000)

        elif self.cpu_mode in ('normal', 'max'):
            pass

        elif self.cpu_mode == 'tsai':

            '''
            lookup-table-4x4x4-step71-tsai-phase3-edges.txt
            - without symmetry
            - we use the copy with symmetry I just left this here for the history
            ===============================================
            1 steps has 4 entries (0 percent, 0.00x previous step)
            2 steps has 20 entries (0 percent, 5.00x previous step)
            3 steps has 140 entries (0 percent, 7.00x previous step)
            4 steps has 1,141 entries (0 percent, 8.15x previous step)
            5 steps has 8,059 entries (0 percent, 7.06x previous step)
            6 steps has 62,188 entries (0 percent, 7.72x previous step)
            7 steps has 442,293 entries (0 percent, 7.11x previous step)
            8 steps has 2,958,583 entries (1 percent, 6.69x previous step)
            9 steps has 17,286,512 entries (7 percent, 5.84x previous step)
            10 steps has 69,004,356 entries (28 percent, 3.99x previous step)
            11 steps has 122,416,936 entries (51 percent, 1.77x previous step)
            12 steps has 27,298,296 entries (11 percent, 0.22x previous step)
            13 steps has 22,272 entries (0 percent, 0.00x previous step)

            Total: 239,500,800 entries


            lookup-table-4x4x4-step71-tsai-phase3-edges.txt
            - with symmetry
            ===============================================
            1 steps has 3 entries (0 percent, 0.00x previous step)
            2 steps has 7 entries (0 percent, 2.33x previous step)
            3 steps has 24 entries (0 percent, 3.43x previous step)
            4 steps has 103 entries (0 percent, 4.29x previous step)
            5 steps has 619 entries (0 percent, 6.01x previous step)
            6 steps has 4,287 entries (0 percent, 6.93x previous step)
            7 steps has 28,697 entries (0 percent, 6.69x previous step)
            8 steps has 187,493 entries (1 percent, 6.53x previous step)
            9 steps has 1,087,267 entries (7 percent, 5.80x previous step)
            10 steps has 4,323,558 entries (28 percent, 3.98x previous step)
            11 steps has 7,657,009 entries (51 percent, 1.77x previous step)
            12 steps has 1,708,625 entries (11 percent, 0.22x previous step)
            13 steps has 1,448 entries (0 percent, 0.00x previous step)

            Total: 14,999,140 entries
            '''
            self.lt_tsai_phase3_edges_solve = LookupTable(self,
                                                          'lookup-table-4x4x4-step71-tsai-phase3-edges.txt',
                                                          '444-phase3-edges',
                                                          '213098ba6574',
                                                          False, # state hex
                                                          linecount=14999140)

            '''
            lookup-table-4x4x4-step72-tsai-phase3-centers.txt
            =================================================
            1 steps has 7 entries (0 percent, 0.00x previous step)
            2 steps has 83 entries (0 percent, 11.86x previous step)
            3 steps has 724 entries (1 percent, 8.72x previous step)
            4 steps has 3851 entries (6 percent, 5.32x previous step)
            5 steps has 10,426 entries (17 percent, 2.71x previous step)
            6 steps has 16,693 entries (28 percent, 1.60x previous step)
            7 steps has 16,616 entries (28 percent, 1.00x previous step)
            8 steps has 8,928 entries (15 percent, 0.54x previous step)
            9 steps has 1,472 entries (2 percent, 0.16x previous step)

            Total: 58,800 entries
            '''
            self.lt_tsai_phase3_centers_solve = LookupTable(self,
                                                           'lookup-table-4x4x4-step72-tsai-phase3-centers.txt',
                                                           '444-ULFRBD-centers-solve',
                                                           'UUUULLLLFFFFRRRRBBBBDDDD',
                                                           False, # state hex
                                                           linecount=58800)
            '''
            If you build this to 8-deep it adds 119,166,578 which makes it too big to
            check into the repo

            lookup-table-4x4x4-step70-tsai-phase3.txt
            ==========================================
            1 steps has 7 entries (0 percent, 0.00x previous step)
            2 steps has 83 entries (0 percent, 11.86x previous step)
            3 steps has 960 entries (0 percent, 11.57x previous step)
            4 steps has 10,303 entries (0 percent, 10.73x previous step)
            5 steps has 107,474 entries (0 percent, 10.43x previous step)
            6 steps has 1,124,149 entries (8 percent, 10.46x previous step)
            7 steps has 11,660,824 entries (90 percent, 10.37x previous step)

            Total: 12,903,800 entries
            '''
            self.lt_tsai_phase3 = LookupTableIDA(self,
                                                 'lookup-table-4x4x4-step70-tsai-phase3.txt',
                                                 '444-tsai-phase3',
                                                 '001UU31UU322118LL98LL955229BBa9BBa4433aRRbaRRb7700bFF8bFF866445DD75DD766',
                                                 False, # state_hex
                                                 moves_4x4x4,
                                                 ("Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",
                                                  "Rw", "Rw'", "Lw", "Lw'", "R", "R'", "L", "L'"), # illegal_moves

                                                 # prune tables
                                                 (self.lt_tsai_phase3_edges_solve,
                                                  self.lt_tsai_phase3_centers_solve),
                                                 linecount=12903800)
            lt_tsai_phase3_heuristic_stats_min = {}
            lt_tsai_phase3_heuristic_stats_median = {}

            #self.lt_tsai_phase3.heuristic_stats = lt_tsai_phase3_heuristic_stats_min
            self.lt_tsai_phase3.heuristic_stats = lt_tsai_phase3_heuristic_stats_median

        else:
            raise Exception("We should not be here, cpu_mode %s" % self.cpu_mode)


        # For tsai these two tables are only used if the centers have already been solved
        # For non-tsai they are always used
        '''
        22*20*18 is 7920

        lookup-table-4x4x4-step40-edges-slice-forward.txt
        =================================================
        1 steps has 7 entries (0 percent)
        2 steps has 42 entries (0 percent)
        3 steps has 299 entries (3 percent)
        4 steps has 1,306 entries (16 percent)
        5 steps has 3,449 entries (43 percent)
        6 steps has 2,617 entries (33 percent)
        7 steps has 200 entries (2 percent)

        Total: 7,920 entries
        '''
        self.lt_edge_slice_forward = LookupTable(self,
                                                 'lookup-table-4x4x4-step40-edges-slice-forward.txt',
                                                 '444-edges-slice-forward',
                                                 'EDGES',
                                                 False, # state hex
                                                 linecount=7920)

        '''
        22*20*18 is 7920
        No idea why I am one entry short (should be 7920 total)...oh well

        lookup-table-4x4x4-step50-edges-slice-backward.txt
        ==================================================
        1 steps has 1 entries (0 percent)
        3 steps has 36 entries (0 percent)
        4 steps has 66 entries (0 percent)
        5 steps has 334 entries (4 percent)
        6 steps has 1,369 entries (17 percent)
        7 steps has 3,505 entries (44 percent)
        8 steps has 2,539 entries (32 percent)
        9 steps has 69 entries (0 percent)

        Total: 7,919 entries
        '''
        self.lt_edge_slice_backward = LookupTable(self,
                                                  'lookup-table-4x4x4-step50-edges-slice-backward.txt',
                                                  '444-edges-slice-backward',
                                                  'EDGES',
                                                  False, # state hex
                                                  linecount=7919)

    def tsai_phase2_orient_edges_state(self, edges_to_flip):
        state = self.state
        result = []

        wing_str_map = {
            'UB' : 'UB',
            'BU' : 'UB',
            'UL' : 'UL',
            'LU' : 'UL',
            'UR' : 'UR',
            'RU' : 'UR',
            'UF' : 'UF',
            'FU' : 'UF',
            'LB' : 'LB',
            'BL' : 'LB',
            'LF' : 'LF',
            'FL' : 'LF',
            'RB' : 'RB',
            'BR' : 'RB',
            'RF' : 'RF',
            'FR' : 'RF',
            'DB' : 'DB',
            'BD' : 'DB',
            'DL' : 'DL',
            'LD' : 'DL',
            'DR' : 'DR',
            'RD' : 'DR',
            'DF' : 'DF',
            'FD' : 'DF',
        }

        for (x, y) in (
                (2, 67), (3, 66), (5, 18), (8, 51), (9, 19), (12, 50), (14, 34),
                (15, 35), (18, 5), (19, 9), (21, 72), (24, 37), (25, 76), (28, 41),
                (30, 89), (31, 85), (34, 14), (35, 15), (37, 24), (40, 53), (41, 28),
                (44, 57), (46, 82), (47, 83), (50, 12), (51, 8), (53, 40), (56, 69),
                (57, 44), (60, 73), (62, 88), (63, 92), (66, 3), (67, 2), (69, 56),
                (72, 21), (73, 60), (76, 25), (78, 95), (79, 94), (82, 46), (83, 47),
                (85, 31), (88, 62), (89, 30), (92, 63), (94, 79), (95, 78)):
            state_x = state[x]
            state_y = state[y]
            wing_str = wing_str_map[''.join((state_x, state_y))]
            high_low = tsai_phase2_orient_edges[(x, y, state_x, state_y)]

            if wing_str in edges_to_flip:
                if high_low == 'U':
                    high_low = 'D'
                else:
                    high_low = 'U'

            result.append(high_low)

        return ''.join(result)

    def tsai_phase2_orient_edges_print(self):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()

        orient_edge_state = list(self.tsai_phase2_orient_edges_state(self.edge_mapping))
        orient_edge_state_index = 0
        for side in list(self.sides.values()):
            for square_index in side.edge_pos:
                self.state[square_index] = orient_edge_state[orient_edge_state_index]
                orient_edge_state_index += 1
        self.print_cube()

        self.state = original_state[:]
        self.solution = original_solution[:]

    def group_centers_guts(self):
        self.lt_init()

        # The non-tsai solver will only solve the centers here
        if self.cpu_mode == 'min':

            # If the centers are already solve then return and let group_edges() pair the edges
            if self.centers_solved():
                self.solution.append('CENTERS_SOLVED')
                return

            log.info("%s: Start of Phase1" % self)
            self.lt_UD_centers_stage.solve()
            self.print_cube()
            log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

            log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_LFRB_centers_stage.solve()
            self.print_cube()
            log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

            log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_ULFRBD_centers_solve.solve()
            self.print_cube()
            log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

        elif self.cpu_mode in ('normal', 'max'):

            # If the centers are already solve then return and let group_edges() pair the edges
            if self.centers_solved():
                self.solution.append('CENTERS_SOLVED')
                return

            log.info("%s: Start of Phase1" % self)
            self.lt_ULFRBD_centers_stage.avoid_oll = True
            self.lt_ULFRBD_centers_stage.solve()
            log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

            log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_ULFRBD_centers_solve.solve()
            self.print_cube()
            log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

        # The tsai will solve the centers and pair the edges
        elif self.cpu_mode == 'tsai':

            # save cube state
            original_state = self.state[:]
            original_solution = self.solution[:]

            # Collect phase1 options
            phase1_options = []
            phase1_options_states = []

            for upper_side_name in ('U', 'D', 'L', 'F', 'R', 'B'):
                for front_side_name in ('F', 'R', 'B', 'L', 'U', 'D'):
                    for transform in ("", "x", "x'", "y", "y'", "z", "z'"):

                        if transform == "":
                            pass
                        elif transform == "x":
                            self.transform_x()
                        elif transform == "x'":
                            self.transform_x_prime()
                        elif transform == "y":
                            self.transform_y()
                        elif transform == "y'":
                            self.transform_y_prime()
                        elif transform == "z":
                            self.transform_z()
                        elif transform == "z'":
                            self.transform_z_prime()
                        else:
                            raise Exception("Implement transform %s" % transform)

                        if self.rotate_to_side(upper_side_name, front_side_name):
                            self.lt_LR_centers_stage.solve()

                            # 168, 104
                            if self.state in phase1_options_states:
                                log.warning("%s %s %-2s would add a duplicate cube state" % (upper_side_name, front_side_name, transform))
                            else:
                                phase1_options.append((upper_side_name, front_side_name, transform, self.state[:], self.solution[:]))
                                phase1_options_states.append(self.state[:])

                            self.state = original_state[:]
                            self.solution = original_solution[:]

            # Print all the permutations
            for (upper_side_name, front_side_name, transform, tmp_state, tmp_solution) in phase1_options:
                log.info("%s %s %-2s - %d phase1 steps" % (upper_side_name, front_side_name, transform, self.get_solution_len_minus_rotates(tmp_solution)))
            log.info("%s: %d phase1 options" % (self, len(phase1_options)))

            min_solution_len = None
            min_solution = None
            min_state = None

            for init_max_ida_threshold in range(8, 99):
                for (upper_side_name, front_side_name, transform, tmp_state, tmp_solution) in phase1_options:
                    self.state = tmp_state[:]
                    self.solution = tmp_solution[:]

                    # Test the prune table
                    #self.lt_tsai_phase2_edges.solve()
                    #self.lt_tsai_phase2_centers.solve()
                    #self.tsai_phase2_orient_edges_print()
                    #self.print_cube()
                    #sys.exit(0)

                    if min_solution_len is None:
                        max_ida_threshold = init_max_ida_threshold
                        log.info("%s: max_ida_threshold (%d)" % (self, max_ida_threshold))
                    else:
                        phase1_solution_length = self.get_solution_len_minus_rotates(tmp_solution)
                        max_ida_threshold = min_solution_len - phase1_solution_length - 1
                        log.info("%s: max_ida_threshold (%d) = min_solution_len (%d) - phase1_solution_length (%d) - 1" %
                            (self, max_ida_threshold, min_solution_len, phase1_solution_length))

                    try:
                        self.lt_tsai_phase2.solve(max_ida_threshold=max_ida_threshold)
                    except NoIDASolution:
                        log.info("%s: NOT NEW MIN, no solution, min %s\n\n\n\n\n" % (self, min_solution_len))
                        continue

                    solution_len = self.get_solution_len_minus_rotates(self.solution)

                    if min_solution_len is None or solution_len < min_solution_len:
                        min_solution_len = solution_len
                        min_state = self.state[:]
                        min_solution = self.solution[:]
                        log.warning("%s: NEW MIN %d (%s, %s %-2s)\n\n\n\n\n" % (self, min_solution_len, upper_side_name, front_side_name, transform))
                    else:
                        log.info("%s: NOT NEW MIN, this one %d, min %d\n\n\n\n\n" % (self, solution_len, min_solution_len))

                    # This is pretty good, we might be able to find a shorter one but it would take us a while.
                    # If we are ever able to speed up phase2 IDA via an edges prune table then we can probably
                    # remove this.
                    if min_solution_len <= 15:
                        break

                if min_solution_len is not None:
                    break

            self.state = min_state[:]
            self.solution = min_solution[:]
            self.print_cube()

            log.info("%s: End of Phase1/2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

            # Testing the phase3 prune tables
            #self.lt_tsai_phase3_edges_solve.solve()
            #self.lt_tsai_phase3_centers_solve.solve()
            #self.print_cube()
            #sys.exit(0)

            log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            #self.lt_tsai_phase3.avoid_oll = True
            self.lt_tsai_phase3.avoid_pll = True
            self.lt_tsai_phase3.solve()
            self.print_cube()
            log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

        self.solution.append('CENTERS_SOLVED')

    def edge_string_to_find(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = []
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in sorted(side.edge_pos):

                if square_index in (target_wing[0], target_wing[1]):
                    state.append('A')

                elif square_index in (sister_wing1[0], sister_wing1[1]):
                    state.append('B')

                elif square_index in (sister_wing2[0], sister_wing2[1]):
                    state.append('C')

                elif square_index in (sister_wing3[0], sister_wing3[1]):
                    state.append('D')

                else:
                    state.append('x')

        return ''.join(state)

    def find_moves_to_stage_slice_forward_444(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        """
        target_wing must go in spot 41
        sister_wing1 must go in spot (40, 53)
        sister_wing2 must go in spot (56, 69)
        sister_wing3 must go in spot (72, 21)
        """
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_forward.steps(state)

    def find_moves_to_stage_slice_backward_444(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        """
        target_wing must go in spot (44, 57)
        sister_wing1 must go in spot (24, 37)
        sister_wing2 must go in spot (72, 21))
        sister_wing3 must go in spot (56, 69)
        """
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_backward.steps(state)

    def prep_for_slice_back_444(self):

        # Now set things up so that when we slice back we pair another 3 edges.
        # Work with the wing on the bottom of F-east
        target_wing = self.sideF.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        target_wing_partner_index = 57
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]
        steps = self.find_moves_to_stage_slice_backward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True

        # If we are here it means the unpaired edge on F-east needs to be swapped with
        # its sister_wing1. In other words F-east and sister-wing1 have the same two
        # sets of colors and the two of them together would create two paired edges if
        # we swapped their wings.
        #
        # As a work-around, move some other unpaired edge into F-east. There are no
        # guarantees we won't hit the exact same problem with that edge but that doesn't
        # happen too often.

        if not self.sideU.north_edge_paired() and self.sideU.has_wing(sister_wing1) != 'north':
            self.rotate("F'")
            self.rotate("U2")
            self.rotate("F")
        elif not self.sideU.east_edge_paired() and self.sideU.has_wing(sister_wing1) != 'east':
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
        elif not self.sideU.west_edge_paired() and self.sideU.has_wing(sister_wing1) != 'west':
            self.rotate("F'")
            self.rotate("U'")
            self.rotate("F")
        elif not self.sideD.south_edge_paired() and self.sideD.has_wing(sister_wing1) != 'south':
            self.rotate("F")
            self.rotate("D2")
            self.rotate("F'")
        elif not self.sideD.east_edge_paired() and self.sideD.has_wing(sister_wing1) != 'east':
            self.rotate("F")
            self.rotate("D'")
            self.rotate("F'")
        elif not self.sideD.west_edge_paired() and self.sideD.has_wing(sister_wing1) != 'west':
            self.rotate("F")
            self.rotate("D")
            self.rotate("F'")
        # Look for these last since they take 4 steps instead of 3
        elif not self.sideU.south_edge_paired() and self.sideU.has_wing(sister_wing1) != 'south':
            self.rotate("U'")
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
        elif not self.sideD.north_edge_paired() and self.sideD.has_wing(sister_wing1) != 'north':
            self.rotate("D")
            self.rotate("F")
            self.rotate("D'")
            self.rotate("F'")
        else:
            # If we are here we are down to two unpaired wings
            return False

        if self.sideF.east_edge_paired():
            raise SolveError("F-east should not be paired")

        target_wing = self.sideF.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        target_wing_partner_index = 57
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]
        steps = self.find_moves_to_stage_slice_backward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True
        else:
            return False

    def pair_six_edges_444(self, wing_to_pair):
        """
        Sections are:
        - PREP-FOR-Uw-SLICE
        - Uw
        - PREP-FOR-REVERSE-Uw-SLICE
        - Uw'
        """

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        self.rotate_edge_to_F_west(wing_to_pair)
        #log.info("PREP-FOR-Uw-SLICE (begin)")
        #self.print_cube()

        # Work with the wing at the bottom of the F-west edge
        # Move the sister wing to the top of F-east
        target_wing = self.sideF.edge_west_pos[-1]
        target_wing_partner_index = 28
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]

        steps = self.find_moves_to_stage_slice_forward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if not steps:
            log.info("pair_six_edges_444()    could not find steps to slice forward")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        #log.info("PREP-FOR-Uw-SLICE (end)....SLICE (begin)")
        #self.print_cube()
        self.rotate("Uw")
        #log.info("SLICE (end)")
        #self.print_cube()

        post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_edges_444()    paired %d wings in %d moves on slice forward (%d left to pair)" %
            (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_wings_count))

        if self.sideL.west_edge_paired():

            # The stars aligned and we paired 4 at once so we cannot rotate L-west around
            # to F-east, move an unpaired edge to F-east. This preserves the LFRB centers
            # for the slice back.
            if not self.sideU.north_edge_paired():
                self.rotate("F'")
                self.rotate("U2")
                self.rotate("F")
            elif not self.sideU.east_edge_paired():
                self.rotate("F'")
                self.rotate("U")
                self.rotate("F")
            elif not self.sideU.west_edge_paired():
                self.rotate("F'")
                self.rotate("U'")
                self.rotate("F")
            elif not self.sideD.south_edge_paired():
                self.rotate("F")
                self.rotate("D2")
                self.rotate("F'")
            elif not self.sideD.east_edge_paired():
                self.rotate("F")
                self.rotate("D'")
                self.rotate("F'")
            elif not self.sideD.west_edge_paired():
                self.rotate("F")
                self.rotate("D")
                self.rotate("F'")
            # Look for these last since they take 4 steps instead of 3
            elif not self.sideU.south_edge_paired():
                self.rotate("U'")
                self.rotate("F'")
                self.rotate("U")
                self.rotate("F")
            elif not self.sideD.north_edge_paired():
                self.rotate("D")
                self.rotate("F")
                self.rotate("D'")
                self.rotate("F'")
            else:
                raise SolveError("Did not find an unpaired edge")

        else:
            self.rotate_y()
            self.rotate_y()

        if self.sideF.east_edge_paired():
            log.warning("F-east should not be paired")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        if not self.prep_for_slice_back_444():
            log.warning("cannot slice back")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        #log.info("PREP-FOR-Uw'-SLICE-BACK (end)...SLICE BACK (begin)")
        #self.print_cube()
        self.rotate("Uw'")
        #log.info("SLICE BACK (end)")
        #self.print_cube()

        post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_edges_444()    paired %d wings in %d moves on slice back (%d left to pair)" %
            (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len - post_slice_forward_solution_len,
             post_slice_back_non_paired_wings_count))

        return True

    def pair_last_six_edges_444(self):
        """
        Sections are:
        - PREP-FOR-Uw-SLICE
        - Uw
        - PREP-FOR-REVERSE-Uw-SLICE
        - Uw'
        """
        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_non_paired_edges = self.get_non_paired_edges()

        min_solution_len = None
        min_solution_state = None
        min_solution = None

        for wing_to_pair in original_non_paired_edges:
            self.state = original_state[:]
            self.solution = original_solution[:]
            self.rotate_edge_to_F_west(wing_to_pair[0])

            # Work with the wing at the bottom of the F-west edge
            # Move the sister wing to the top of F-east
            target_wing = self.sideF.edge_west_pos[-1]
            target_wing_partner_index = 28
            sister_wing1 = self.get_wings(target_wing)[0]
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])
            sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
            sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
            sister_wing2_side = self.get_side_for_index(sister_wing2[0])
            sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
            sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]

            #log.info("target_wing: %s" % target_wing)
            #log.info("sister_wing1 %s on %s, neighbor %s" % (sister_wing1, sister_wing1_side, sister_wing1_neighbor))
            #log.info("sister_wing2 %s on %s, neighbor %s" % (sister_wing2, sister_wing2_side, sister_wing2_neighbor))
            #log.info("sister_wing3 %s" % pformat(sister_wing3))

            sister_wing3_candidates = []

            # We need sister_wing3 to be any unpaired edge that allows us
            # to only pair 2 on the slice forward
            for wing in self.get_non_paired_wings():
                if (wing[0] not in (target_wing, sister_wing1, sister_wing2, sister_wing3) and
                    wing[1] not in (target_wing, sister_wing1, sister_wing2, sister_wing3)):
                    sister_wing3_candidates.append(wing[1])

            min_sister_wing3_steps_len = None
            min_sister_wing3_steps = None
            min_sister_wing3 = None

            for x in sister_wing3_candidates:
                steps = self.find_moves_to_stage_slice_forward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, x)

                if steps:
                    steps_len = len(steps)

                    if min_sister_wing3_steps_len is None or steps_len < min_sister_wing3_steps_len:
                        min_sister_wing3_steps_len = steps_len
                        min_sister_wing3_steps = steps
                        min_sister_wing3 = x

            sister_wing3 = min_sister_wing3
            steps = min_sister_wing3_steps
            #log.info("sister_wing3 %s" % pformat(sister_wing3))

            if not steps:
                log.info("pair_last_six_edges_444() cannot slice back (no steps found)")
                continue

            for step in steps:
                self.rotate(step)

            # At this point we are setup to slice forward and pair 2 edges
            #log.info("PREP-FOR-Uw-SLICE (end)....SLICE (begin)")
            #self.print_cube()
            self.rotate("Uw")
            #log.info("SLICE (end)")
            #self.print_cube()

            post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
            post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

            log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice forward (%d left to pair)" %
                (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
                 post_slice_forward_solution_len - original_solution_len,
                 post_slice_forward_non_paired_wings_count))

            if self.sideF.east_edge_paired():
                for x in range(3):
                    self.rotate_y()
                    if not self.sideF.east_edge_paired():
                        break

            if self.sideF.east_edge_paired():
                log.info("pair_last_six_edges_444() cannot slice back (F-east paired)")
                continue

            if not self.prep_for_slice_back_444():
                log.info("pair_last_six_edges_444() cannot slice back (prep failed)")
                continue

            self.rotate("Uw'")

            post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
            post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

            if min_solution_len is None or post_slice_back_solution_len < min_solution_len:
                min_solution_len = post_slice_back_solution_len
                min_solution_state = self.state[:]
                min_solution = self.solution[:]
                log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice back (%d left to pair) (NEW MIN %d)" %
                    (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - post_slice_forward_solution_len,
                    post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - original_solution_len))
            else:
                log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice back (%d left to pair)" %
                    (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - post_slice_forward_solution_len,
                    post_slice_back_non_paired_wings_count))

        if min_solution_len:
            self.state = min_solution_state
            self.solution = min_solution
            return True
        else:
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

    def pair_four_edges_444(self, edge):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        if original_non_paired_wings_count < 4:
            raise SolveError("pair_four_edges_444() requires at least 4 unpaired edges")

        self.rotate_edge_to_F_west(edge)

        # Work with the wing at the bottom of the F-west edge
        target_wing = self.sideF.edge_west_pos[-1]

        # Move the sister wing to F east
        sister_wing = self.get_wings(target_wing)[0]
        steps = lookup_table_444_sister_wing_to_F_east[sister_wing]

        for step in steps.split():
            self.rotate(step)

        self.rotate("Uw")

        if not self.sideR.west_edge_paired():
            pass
        elif not self.sideB.west_edge_paired():
            self.rotate_y()
        elif not self.sideL.west_edge_paired():
            self.rotate_y()
            self.rotate_y()

        if not self.prep_for_slice_back_444():
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        self.rotate("Uw'")

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_four_edges_444()    paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count >= original_non_paired_wings_count:
            raise SolveError("Went from %d to %d non_paired_edges" %
                (original_non_paired_wings_count, current_non_paired_wings_count))

        return True

    def pair_two_edges_444(self, edge):
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        if original_non_paired_wings_count == 2:
            raise SolveError("pair_last_two_edges_444() should be used when there are only 2 edges left")

        self.rotate_edge_to_F_west(edge)

        # Work with the wing at the bottom of the F-west edge
        target_wing = self.sideF.edge_west_pos[-1]

        # Move the sister wing to F east...this uses a small lookup table
        # that I built manually. This puts the sister wing at F-east in the correct
        # orientation (it will not need to be flipped). We used to just move the
        # sister wing to F-east but then sometimes we would need to "R U' B' R2"
        # to flip it around.
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_F_east:
            log.warning("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'F-east')
            raise ImplementThis("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_F_east[sister_wing]

        for step in steps.split():
            self.rotate(step)

        # Now that that two edges on F are in place, put an unpaired edge at U-west.
        # The unpaired edge that we place at U-west should contain the
        # sister wing of the wing that is at the bottom of F-east. This
        # will allow us to pair two wings at once.
        wing_bottom_F_east = self.sideF.edge_east_pos[-1]
        sister_wing_bottom_F_east = self.get_wings(wing_bottom_F_east)[0]

        if sister_wing_bottom_F_east not in lookup_table_444_sister_wing_to_U_west:
            raise ImplementThis("sister_wing_bottom_F_east %s" % pformat(sister_wing_bottom_F_east))

        steps = lookup_table_444_sister_wing_to_U_west[sister_wing_bottom_F_east]

        # If steps is None it means sister_wing_bottom_F_east is at (37, 24)
        # which is the top wing on F-west. If that is the case call
        # pair_last_two_edges_444()
        if steps == None:
            self.state = original_state[:]
            self.solution = original_solution[:]
            #self.print_cube()
            self.pair_last_two_edges_444(edge)
        else:
            for step in steps.split():
                self.rotate(step)

            for step in ("Uw", "L'", "U'", "L", "Uw'"):
                self.rotate(step)

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_two_edges_444()    paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count < original_non_paired_wings_count:
            return True

        raise SolveError("Went from %d to %d non_paired_edges" %
            (original_non_paired_wings_count, current_non_paired_wings_count))

    def pair_last_two_edges_444(self, edge):
        """
        At one point I looked into using two lookup tables to do this:
        - the first to stage edges to F-west and F-east
        - the second to solve the two staged edges

        The first stage took 1 or steps and the 2nd stage took either 7 or 10, it
        was 10 if the wing at F-east was turned the wrong way and needed to be
        rotated around. It wasn't worth it...what I have below works just fine and
        takes between 7 to 11 steps total.
        """
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        # rotate unpaired edge to F-west
        self.rotate_edge_to_F_west(edge)

        pos1 = self.sideF.edge_west_pos[-1]

        # Put the other unpaired edge on F east...this uses a small lookup table
        # that I built manually. This puts the sister wing at F-east in the correct
        # orientation (it will not need to be flipped). We used to just move the
        # sister wing to F-east but then sometimes we would need to "R F' U R' F"
        # to flip it around.
        sister_wing = self.get_wings(pos1)[0]

        steps = lookup_table_444_last_two_edges_place_F_east[sister_wing]
        for step in steps.split():
            self.rotate(step)

        # "Solving the last 4 edge blocks" in
        # http://www.rubiksplace.com/cubes/4x4/
        for step in ("Dw", "R", "F'", "U", "R'", "F", "Dw'"):
            self.rotate(step)

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_last_two_edges_444() paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if original_non_paired_wings_count == 2:
            if current_non_paired_wings_count:
                raise SolveError("Failed to pair last two edges")

    def pair_edge(self, edge_to_pair):
        """
        Pair a specific edge
        """
        pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
        pre_non_paired_edges_count = self.get_non_paired_edges_count()
        log.info("pair_edge() for %s (%d wings left to pair)" % (pformat(edge_to_pair), pre_non_paired_edges_count))

        if pre_non_paired_edges_count > 6:
            if not self.pair_six_edges_444(edge_to_pair[0]):
                log.info("pair_six_edges_444()    returned False")

                if not self.pair_four_edges_444(edge_to_pair[0]):
                    log.info("pair_four_edges_444() returned False")
                    self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count == 6:
            if not self.pair_last_six_edges_444():
                log.info("pair_last_six_edges_444() returned False")

                if not self.pair_four_edges_444(edge_to_pair[0]):
                    log.info("pair_four_edges_444() returned False")
                    self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count >= 4:
            if not self.pair_four_edges_444(edge_to_pair[0]):
                log.info("pair_four_edges_444() returned False")
                self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count == 2:
            self.pair_last_two_edges_444(edge_to_pair[0])

        # The scenario where you have 3 unpaired edges
        elif pre_non_paired_edges_count > 2:
            self.pair_two_edges_444(edge_to_pair[0])

        post_non_paired_edges_count = self.get_non_paired_edges_count()
        edges_paired = pre_non_paired_edges_count - post_non_paired_edges_count

        if edges_paired < 1:
            raise SolveError("Paired %d edges" % edges_paired)

        return True

    def group_edges_recursive(self, depth, edge_to_pair):
        """
        """
        pre_non_paired_wings_count = len(self.get_non_paired_wings())
        pre_non_paired_edges_count = len(self.get_non_paired_edges())
        edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len

        log.info("")
        log.info("group_edges_recursive(%d) called with edge_to_pair %s (%d edges and %d wings left to pair, min solution len %s, current solution len %d)" %
                (depth,
                 pformat(edge_to_pair),
                 pre_non_paired_edges_count,
                 pre_non_paired_wings_count,
                 self.min_edge_solution_len,
                 edge_solution_len))

        # Should we continue down this branch or should we prune it? An estimate
        # of 2 moves to pair an edge is a low estimate so if the current number of
        # steps plus 2 * pre_non_paired_wings_count is greater than our current minimum
        # there isn't any point in continuing down this branch so prune it and save
        # some CPU cycles.

        if self.cpu_mode == 'min':
            estimate_per_wing = 3.0
        else:
            estimate_per_wing = 2.0

        estimated_solution_len = edge_solution_len + (estimate_per_wing * pre_non_paired_wings_count)

        if estimated_solution_len >= self.min_edge_solution_len:
            #log.warning("PRUNE: %s + (2 * %d) > %s" % (edge_solution_len, non_paired_wings_count, self.min_edge_solution_len))
            return False

        # The only time this will be None is on the initial call to group_edges_recursive()
        if edge_to_pair:
            self.pair_edge(edge_to_pair)

        non_paired_edges = self.get_non_paired_edges()

        if non_paired_edges:
            original_state = self.state[:]
            original_solution = self.solution[:]

            # call group_edges_recursive() for each non-paired edge
            for edge in non_paired_edges:
                self.group_edges_recursive(depth+1, edge)
                self.state = original_state[:]
                self.solution = original_solution[:]

        else:

            # If you solve 3x3x3 and then resolve PLL it takes 12 steps but if we avoid it here
            # it only takes 7 steps. If we are pairing the outside edges of a 5x5x5 self.avoid_pll
            # will be False.
            if self.avoid_pll and self.edge_solution_leads_to_pll_parity():
                for step in "Rw2 U2 F2 Rw2 F2 U2 Rw2".split():
                    self.rotate(step)

            # There are no edges left to pair, note how many steps it took pair them all
            edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len

            # Remember the solution that pairs all edges in the least number of moves
            if edge_solution_len < self.min_edge_solution_len:
                self.min_edge_solution_len = edge_solution_len
                self.min_edge_solution = self.solution[:]
                self.min_edge_solution_state = self.state[:]
                log.warning("NEW MIN: edges paired in %d steps" % self.min_edge_solution_len)

            return True

    def group_edges(self):
        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        depth = 0
        self.lt_init()
        self.center_solution_len = self.get_solution_len_minus_rotates(self.solution)
        self.min_edge_solution_len = 9999
        self.min_edge_solution = None
        self.min_edge_solution_state = None

        # group_edges_recursive() is where the magic happens
        self.group_edges_recursive(depth, None)
        self.state = self.min_edge_solution_state[:]
        self.solution = self.min_edge_solution[:]
        self.solution.append('EDGES_GROUPED')


class LookupTsaiPhase2Edges(LookupTable):
    """
    This is an experiment that needs more work....it is not used yet
    """

    def state(self):
        centers_cost = self.parent.lt_tsai_phase2_centers.steps_cost()
        min_edges_cost = None
        min_edges_state = None

        for uu_dd_count in tsai_edge_mapping_combinations.keys():
            if uu_dd_count <= 4:
                for edges_to_flip in tsai_edge_mapping_combinations[uu_dd_count]:
                    edges_state = self.parent.tsai_phase2_orient_edges_state(edges_to_flip)
                    edges_cost = self.steps_cost(edges_state)

                    if edges_cost <= centers_cost:
                        return edges_state

                    if min_edges_cost is None or edges_cost < min_edges_cost:
                        min_edges_cost = edges_cost
                        min_edges_state = edges_state

        return min_edges_state


class LookupTsaiPhase2IDA(LookupTableIDA):

    def ida_search_complete(self, state, steps_to_here):

        # Are UD and FB staged?
        for side in (self.parent.sideU, self.parent.sideD):
            for square_index in side.center_pos:
                if self.parent.state[square_index] not in ('U', 'D'):
                    return False

        # Are the LR sides in 1 of the 12 states we want?
        LR_center_targets = set(('LLLLRRRR',
                                 'RRRRLLLL',
                                 'LLRRRRLL',
                                 'LLRRLLRR',
                                 'RRLLRRLL',
                                 'RRLLLLRR',
                                 'RLRLRLRL',
                                 'RLRLLRLR',
                                 'LRLRRLRL',
                                 'LRLRLRLR',
                                 'RLLRLRRL',
                                 'LRRLRLLR'))

        LR_centers = []
        for side in (self.parent.sideL, self.parent.sideR):
            for square_index in side.center_pos:
                LR_centers.append(self.parent.state[square_index])
        LR_centers = ''.join(LR_centers)

        if LR_centers not in LR_center_targets:
            return False

        # If we are here then our centers are all good...check the edges.
        # If the edges are not in lt_tsai_phase3_edges_solve it may throw a KeyError
        try:
            if self.parent.lt_tsai_phase3_edges_solve.steps() is not None and self.parent.edge_swaps_even(False, None, False):

                # rotate_xxx() is very fast but it does not append the
                # steps to the solution so put the cube back in original state
                # and execute the steps via a normal rotate() call
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]

                for step in steps_to_here:
                    self.parent.rotate(step)

                return True

        except KeyError:
            pass

        return False


tsai_phase2_orient_edges = {
    (2, 67, 'B', 'D'): 'D',
    (2, 67, 'B', 'L'): 'D',
    (2, 67, 'B', 'R'): 'D',
    (2, 67, 'B', 'U'): 'D',
    (2, 67, 'D', 'B'): 'U',
    (2, 67, 'D', 'F'): 'U',
    (2, 67, 'D', 'L'): 'U',
    (2, 67, 'D', 'R'): 'U',
    (2, 67, 'F', 'D'): 'D',
    (2, 67, 'F', 'L'): 'D',
    (2, 67, 'F', 'R'): 'D',
    (2, 67, 'F', 'U'): 'D',
    (2, 67, 'L', 'B'): 'U',
    (2, 67, 'L', 'D'): 'D',
    (2, 67, 'L', 'F'): 'U',
    (2, 67, 'L', 'U'): 'D',
    (2, 67, 'R', 'B'): 'U',
    (2, 67, 'R', 'D'): 'D',
    (2, 67, 'R', 'F'): 'U',
    (2, 67, 'R', 'U'): 'D',
    (2, 67, 'U', 'B'): 'U',
    (2, 67, 'U', 'F'): 'U',
    (2, 67, 'U', 'L'): 'U',
    (2, 67, 'U', 'R'): 'U',
    (3, 66, 'B', 'D'): 'U',
    (3, 66, 'B', 'L'): 'U',
    (3, 66, 'B', 'R'): 'U',
    (3, 66, 'B', 'U'): 'U',
    (3, 66, 'D', 'B'): 'D',
    (3, 66, 'D', 'F'): 'D',
    (3, 66, 'D', 'L'): 'D',
    (3, 66, 'D', 'R'): 'D',
    (3, 66, 'F', 'D'): 'U',
    (3, 66, 'F', 'L'): 'U',
    (3, 66, 'F', 'R'): 'U',
    (3, 66, 'F', 'U'): 'U',
    (3, 66, 'L', 'B'): 'D',
    (3, 66, 'L', 'D'): 'U',
    (3, 66, 'L', 'F'): 'D',
    (3, 66, 'L', 'U'): 'U',
    (3, 66, 'R', 'B'): 'D',
    (3, 66, 'R', 'D'): 'U',
    (3, 66, 'R', 'F'): 'D',
    (3, 66, 'R', 'U'): 'U',
    (3, 66, 'U', 'B'): 'D',
    (3, 66, 'U', 'F'): 'D',
    (3, 66, 'U', 'L'): 'D',
    (3, 66, 'U', 'R'): 'D',
    (5, 18, 'B', 'D'): 'U',
    (5, 18, 'B', 'L'): 'U',
    (5, 18, 'B', 'R'): 'U',
    (5, 18, 'B', 'U'): 'U',
    (5, 18, 'D', 'B'): 'D',
    (5, 18, 'D', 'F'): 'D',
    (5, 18, 'D', 'L'): 'D',
    (5, 18, 'D', 'R'): 'D',
    (5, 18, 'F', 'D'): 'U',
    (5, 18, 'F', 'L'): 'U',
    (5, 18, 'F', 'R'): 'U',
    (5, 18, 'F', 'U'): 'U',
    (5, 18, 'L', 'B'): 'D',
    (5, 18, 'L', 'D'): 'U',
    (5, 18, 'L', 'F'): 'D',
    (5, 18, 'L', 'U'): 'U',
    (5, 18, 'R', 'B'): 'D',
    (5, 18, 'R', 'D'): 'U',
    (5, 18, 'R', 'F'): 'D',
    (5, 18, 'R', 'U'): 'U',
    (5, 18, 'U', 'B'): 'D',
    (5, 18, 'U', 'F'): 'D',
    (5, 18, 'U', 'L'): 'D',
    (5, 18, 'U', 'R'): 'D',
    (8, 51, 'B', 'D'): 'D',
    (8, 51, 'B', 'L'): 'D',
    (8, 51, 'B', 'R'): 'D',
    (8, 51, 'B', 'U'): 'D',
    (8, 51, 'D', 'B'): 'U',
    (8, 51, 'D', 'F'): 'U',
    (8, 51, 'D', 'L'): 'U',
    (8, 51, 'D', 'R'): 'U',
    (8, 51, 'F', 'D'): 'D',
    (8, 51, 'F', 'L'): 'D',
    (8, 51, 'F', 'R'): 'D',
    (8, 51, 'F', 'U'): 'D',
    (8, 51, 'L', 'B'): 'U',
    (8, 51, 'L', 'D'): 'D',
    (8, 51, 'L', 'F'): 'U',
    (8, 51, 'L', 'U'): 'D',
    (8, 51, 'R', 'B'): 'U',
    (8, 51, 'R', 'D'): 'D',
    (8, 51, 'R', 'F'): 'U',
    (8, 51, 'R', 'U'): 'D',
    (8, 51, 'U', 'B'): 'U',
    (8, 51, 'U', 'F'): 'U',
    (8, 51, 'U', 'L'): 'U',
    (8, 51, 'U', 'R'): 'U',
    (9, 19, 'B', 'D'): 'D',
    (9, 19, 'B', 'L'): 'D',
    (9, 19, 'B', 'R'): 'D',
    (9, 19, 'B', 'U'): 'D',
    (9, 19, 'D', 'B'): 'U',
    (9, 19, 'D', 'F'): 'U',
    (9, 19, 'D', 'L'): 'U',
    (9, 19, 'D', 'R'): 'U',
    (9, 19, 'F', 'D'): 'D',
    (9, 19, 'F', 'L'): 'D',
    (9, 19, 'F', 'R'): 'D',
    (9, 19, 'F', 'U'): 'D',
    (9, 19, 'L', 'B'): 'U',
    (9, 19, 'L', 'D'): 'D',
    (9, 19, 'L', 'F'): 'U',
    (9, 19, 'L', 'U'): 'D',
    (9, 19, 'R', 'B'): 'U',
    (9, 19, 'R', 'D'): 'D',
    (9, 19, 'R', 'F'): 'U',
    (9, 19, 'R', 'U'): 'D',
    (9, 19, 'U', 'B'): 'U',
    (9, 19, 'U', 'F'): 'U',
    (9, 19, 'U', 'L'): 'U',
    (9, 19, 'U', 'R'): 'U',
    (12, 50, 'B', 'D'): 'U',
    (12, 50, 'B', 'L'): 'U',
    (12, 50, 'B', 'R'): 'U',
    (12, 50, 'B', 'U'): 'U',
    (12, 50, 'D', 'B'): 'D',
    (12, 50, 'D', 'F'): 'D',
    (12, 50, 'D', 'L'): 'D',
    (12, 50, 'D', 'R'): 'D',
    (12, 50, 'F', 'D'): 'U',
    (12, 50, 'F', 'L'): 'U',
    (12, 50, 'F', 'R'): 'U',
    (12, 50, 'F', 'U'): 'U',
    (12, 50, 'L', 'B'): 'D',
    (12, 50, 'L', 'D'): 'U',
    (12, 50, 'L', 'F'): 'D',
    (12, 50, 'L', 'U'): 'U',
    (12, 50, 'R', 'B'): 'D',
    (12, 50, 'R', 'D'): 'U',
    (12, 50, 'R', 'F'): 'D',
    (12, 50, 'R', 'U'): 'U',
    (12, 50, 'U', 'B'): 'D',
    (12, 50, 'U', 'F'): 'D',
    (12, 50, 'U', 'L'): 'D',
    (12, 50, 'U', 'R'): 'D',
    (14, 34, 'B', 'D'): 'U',
    (14, 34, 'B', 'L'): 'U',
    (14, 34, 'B', 'R'): 'U',
    (14, 34, 'B', 'U'): 'U',
    (14, 34, 'D', 'B'): 'D',
    (14, 34, 'D', 'F'): 'D',
    (14, 34, 'D', 'L'): 'D',
    (14, 34, 'D', 'R'): 'D',
    (14, 34, 'F', 'D'): 'U',
    (14, 34, 'F', 'L'): 'U',
    (14, 34, 'F', 'R'): 'U',
    (14, 34, 'F', 'U'): 'U',
    (14, 34, 'L', 'B'): 'D',
    (14, 34, 'L', 'D'): 'U',
    (14, 34, 'L', 'F'): 'D',
    (14, 34, 'L', 'U'): 'U',
    (14, 34, 'R', 'B'): 'D',
    (14, 34, 'R', 'D'): 'U',
    (14, 34, 'R', 'F'): 'D',
    (14, 34, 'R', 'U'): 'U',
    (14, 34, 'U', 'B'): 'D',
    (14, 34, 'U', 'F'): 'D',
    (14, 34, 'U', 'L'): 'D',
    (14, 34, 'U', 'R'): 'D',
    (15, 35, 'B', 'D'): 'D',
    (15, 35, 'B', 'L'): 'D',
    (15, 35, 'B', 'R'): 'D',
    (15, 35, 'B', 'U'): 'D',
    (15, 35, 'D', 'B'): 'U',
    (15, 35, 'D', 'F'): 'U',
    (15, 35, 'D', 'L'): 'U',
    (15, 35, 'D', 'R'): 'U',
    (15, 35, 'F', 'D'): 'D',
    (15, 35, 'F', 'L'): 'D',
    (15, 35, 'F', 'R'): 'D',
    (15, 35, 'F', 'U'): 'D',
    (15, 35, 'L', 'B'): 'U',
    (15, 35, 'L', 'D'): 'D',
    (15, 35, 'L', 'F'): 'U',
    (15, 35, 'L', 'U'): 'D',
    (15, 35, 'R', 'B'): 'U',
    (15, 35, 'R', 'D'): 'D',
    (15, 35, 'R', 'F'): 'U',
    (15, 35, 'R', 'U'): 'D',
    (15, 35, 'U', 'B'): 'U',
    (15, 35, 'U', 'F'): 'U',
    (15, 35, 'U', 'L'): 'U',
    (15, 35, 'U', 'R'): 'U',
    (18, 5, 'B', 'D'): 'D',
    (18, 5, 'B', 'L'): 'D',
    (18, 5, 'B', 'R'): 'D',
    (18, 5, 'B', 'U'): 'D',
    (18, 5, 'D', 'B'): 'U',
    (18, 5, 'D', 'F'): 'U',
    (18, 5, 'D', 'L'): 'U',
    (18, 5, 'D', 'R'): 'U',
    (18, 5, 'F', 'D'): 'D',
    (18, 5, 'F', 'L'): 'D',
    (18, 5, 'F', 'R'): 'D',
    (18, 5, 'F', 'U'): 'D',
    (18, 5, 'L', 'B'): 'U',
    (18, 5, 'L', 'D'): 'D',
    (18, 5, 'L', 'F'): 'U',
    (18, 5, 'L', 'U'): 'D',
    (18, 5, 'R', 'B'): 'U',
    (18, 5, 'R', 'D'): 'D',
    (18, 5, 'R', 'F'): 'U',
    (18, 5, 'R', 'U'): 'D',
    (18, 5, 'U', 'B'): 'U',
    (18, 5, 'U', 'F'): 'U',
    (18, 5, 'U', 'L'): 'U',
    (18, 5, 'U', 'R'): 'U',
    (19, 9, 'B', 'D'): 'U',
    (19, 9, 'B', 'L'): 'U',
    (19, 9, 'B', 'R'): 'U',
    (19, 9, 'B', 'U'): 'U',
    (19, 9, 'D', 'B'): 'D',
    (19, 9, 'D', 'F'): 'D',
    (19, 9, 'D', 'L'): 'D',
    (19, 9, 'D', 'R'): 'D',
    (19, 9, 'F', 'D'): 'U',
    (19, 9, 'F', 'L'): 'U',
    (19, 9, 'F', 'R'): 'U',
    (19, 9, 'F', 'U'): 'U',
    (19, 9, 'L', 'B'): 'D',
    (19, 9, 'L', 'D'): 'U',
    (19, 9, 'L', 'F'): 'D',
    (19, 9, 'L', 'U'): 'U',
    (19, 9, 'R', 'B'): 'D',
    (19, 9, 'R', 'D'): 'U',
    (19, 9, 'R', 'F'): 'D',
    (19, 9, 'R', 'U'): 'U',
    (19, 9, 'U', 'B'): 'D',
    (19, 9, 'U', 'F'): 'D',
    (19, 9, 'U', 'L'): 'D',
    (19, 9, 'U', 'R'): 'D',
    (21, 72, 'B', 'D'): 'U',
    (21, 72, 'B', 'L'): 'U',
    (21, 72, 'B', 'R'): 'U',
    (21, 72, 'B', 'U'): 'U',
    (21, 72, 'D', 'B'): 'D',
    (21, 72, 'D', 'F'): 'D',
    (21, 72, 'D', 'L'): 'D',
    (21, 72, 'D', 'R'): 'D',
    (21, 72, 'F', 'D'): 'U',
    (21, 72, 'F', 'L'): 'U',
    (21, 72, 'F', 'R'): 'U',
    (21, 72, 'F', 'U'): 'U',
    (21, 72, 'L', 'B'): 'D',
    (21, 72, 'L', 'D'): 'U',
    (21, 72, 'L', 'F'): 'D',
    (21, 72, 'L', 'U'): 'U',
    (21, 72, 'R', 'B'): 'D',
    (21, 72, 'R', 'D'): 'U',
    (21, 72, 'R', 'F'): 'D',
    (21, 72, 'R', 'U'): 'U',
    (21, 72, 'U', 'B'): 'D',
    (21, 72, 'U', 'F'): 'D',
    (21, 72, 'U', 'L'): 'D',
    (21, 72, 'U', 'R'): 'D',
    (24, 37, 'B', 'D'): 'D',
    (24, 37, 'B', 'L'): 'D',
    (24, 37, 'B', 'R'): 'D',
    (24, 37, 'B', 'U'): 'D',
    (24, 37, 'D', 'B'): 'U',
    (24, 37, 'D', 'F'): 'U',
    (24, 37, 'D', 'L'): 'U',
    (24, 37, 'D', 'R'): 'U',
    (24, 37, 'F', 'D'): 'D',
    (24, 37, 'F', 'L'): 'D',
    (24, 37, 'F', 'R'): 'D',
    (24, 37, 'F', 'U'): 'D',
    (24, 37, 'L', 'B'): 'U',
    (24, 37, 'L', 'D'): 'D',
    (24, 37, 'L', 'F'): 'U',
    (24, 37, 'L', 'U'): 'D',
    (24, 37, 'R', 'B'): 'U',
    (24, 37, 'R', 'D'): 'D',
    (24, 37, 'R', 'F'): 'U',
    (24, 37, 'R', 'U'): 'D',
    (24, 37, 'U', 'B'): 'U',
    (24, 37, 'U', 'F'): 'U',
    (24, 37, 'U', 'L'): 'U',
    (24, 37, 'U', 'R'): 'U',
    (25, 76, 'B', 'D'): 'D',
    (25, 76, 'B', 'L'): 'D',
    (25, 76, 'B', 'R'): 'D',
    (25, 76, 'B', 'U'): 'D',
    (25, 76, 'D', 'B'): 'U',
    (25, 76, 'D', 'F'): 'U',
    (25, 76, 'D', 'L'): 'U',
    (25, 76, 'D', 'R'): 'U',
    (25, 76, 'F', 'D'): 'D',
    (25, 76, 'F', 'L'): 'D',
    (25, 76, 'F', 'R'): 'D',
    (25, 76, 'F', 'U'): 'D',
    (25, 76, 'L', 'B'): 'U',
    (25, 76, 'L', 'D'): 'D',
    (25, 76, 'L', 'F'): 'U',
    (25, 76, 'L', 'U'): 'D',
    (25, 76, 'R', 'B'): 'U',
    (25, 76, 'R', 'D'): 'D',
    (25, 76, 'R', 'F'): 'U',
    (25, 76, 'R', 'U'): 'D',
    (25, 76, 'U', 'B'): 'U',
    (25, 76, 'U', 'F'): 'U',
    (25, 76, 'U', 'L'): 'U',
    (25, 76, 'U', 'R'): 'U',
    (28, 41, 'B', 'D'): 'U',
    (28, 41, 'B', 'L'): 'U',
    (28, 41, 'B', 'R'): 'U',
    (28, 41, 'B', 'U'): 'U',
    (28, 41, 'D', 'B'): 'D',
    (28, 41, 'D', 'F'): 'D',
    (28, 41, 'D', 'L'): 'D',
    (28, 41, 'D', 'R'): 'D',
    (28, 41, 'F', 'D'): 'U',
    (28, 41, 'F', 'L'): 'U',
    (28, 41, 'F', 'R'): 'U',
    (28, 41, 'F', 'U'): 'U',
    (28, 41, 'L', 'B'): 'D',
    (28, 41, 'L', 'D'): 'U',
    (28, 41, 'L', 'F'): 'D',
    (28, 41, 'L', 'U'): 'U',
    (28, 41, 'R', 'B'): 'D',
    (28, 41, 'R', 'D'): 'U',
    (28, 41, 'R', 'F'): 'D',
    (28, 41, 'R', 'U'): 'U',
    (28, 41, 'U', 'B'): 'D',
    (28, 41, 'U', 'F'): 'D',
    (28, 41, 'U', 'L'): 'D',
    (28, 41, 'U', 'R'): 'D',
    (30, 89, 'B', 'D'): 'U',
    (30, 89, 'B', 'L'): 'U',
    (30, 89, 'B', 'R'): 'U',
    (30, 89, 'B', 'U'): 'U',
    (30, 89, 'D', 'B'): 'D',
    (30, 89, 'D', 'F'): 'D',
    (30, 89, 'D', 'L'): 'D',
    (30, 89, 'D', 'R'): 'D',
    (30, 89, 'F', 'D'): 'U',
    (30, 89, 'F', 'L'): 'U',
    (30, 89, 'F', 'R'): 'U',
    (30, 89, 'F', 'U'): 'U',
    (30, 89, 'L', 'B'): 'D',
    (30, 89, 'L', 'D'): 'U',
    (30, 89, 'L', 'F'): 'D',
    (30, 89, 'L', 'U'): 'U',
    (30, 89, 'R', 'B'): 'D',
    (30, 89, 'R', 'D'): 'U',
    (30, 89, 'R', 'F'): 'D',
    (30, 89, 'R', 'U'): 'U',
    (30, 89, 'U', 'B'): 'D',
    (30, 89, 'U', 'F'): 'D',
    (30, 89, 'U', 'L'): 'D',
    (30, 89, 'U', 'R'): 'D',
    (31, 85, 'B', 'D'): 'D',
    (31, 85, 'B', 'L'): 'D',
    (31, 85, 'B', 'R'): 'D',
    (31, 85, 'B', 'U'): 'D',
    (31, 85, 'D', 'B'): 'U',
    (31, 85, 'D', 'F'): 'U',
    (31, 85, 'D', 'L'): 'U',
    (31, 85, 'D', 'R'): 'U',
    (31, 85, 'F', 'D'): 'D',
    (31, 85, 'F', 'L'): 'D',
    (31, 85, 'F', 'R'): 'D',
    (31, 85, 'F', 'U'): 'D',
    (31, 85, 'L', 'B'): 'U',
    (31, 85, 'L', 'D'): 'D',
    (31, 85, 'L', 'F'): 'U',
    (31, 85, 'L', 'U'): 'D',
    (31, 85, 'R', 'B'): 'U',
    (31, 85, 'R', 'D'): 'D',
    (31, 85, 'R', 'F'): 'U',
    (31, 85, 'R', 'U'): 'D',
    (31, 85, 'U', 'B'): 'U',
    (31, 85, 'U', 'F'): 'U',
    (31, 85, 'U', 'L'): 'U',
    (31, 85, 'U', 'R'): 'U',
    (34, 14, 'B', 'D'): 'D',
    (34, 14, 'B', 'L'): 'D',
    (34, 14, 'B', 'R'): 'D',
    (34, 14, 'B', 'U'): 'D',
    (34, 14, 'D', 'B'): 'U',
    (34, 14, 'D', 'F'): 'U',
    (34, 14, 'D', 'L'): 'U',
    (34, 14, 'D', 'R'): 'U',
    (34, 14, 'F', 'D'): 'D',
    (34, 14, 'F', 'L'): 'D',
    (34, 14, 'F', 'R'): 'D',
    (34, 14, 'F', 'U'): 'D',
    (34, 14, 'L', 'B'): 'U',
    (34, 14, 'L', 'D'): 'D',
    (34, 14, 'L', 'F'): 'U',
    (34, 14, 'L', 'U'): 'D',
    (34, 14, 'R', 'B'): 'U',
    (34, 14, 'R', 'D'): 'D',
    (34, 14, 'R', 'F'): 'U',
    (34, 14, 'R', 'U'): 'D',
    (34, 14, 'U', 'B'): 'U',
    (34, 14, 'U', 'F'): 'U',
    (34, 14, 'U', 'L'): 'U',
    (34, 14, 'U', 'R'): 'U',
    (35, 15, 'B', 'D'): 'U',
    (35, 15, 'B', 'L'): 'U',
    (35, 15, 'B', 'R'): 'U',
    (35, 15, 'B', 'U'): 'U',
    (35, 15, 'D', 'B'): 'D',
    (35, 15, 'D', 'F'): 'D',
    (35, 15, 'D', 'L'): 'D',
    (35, 15, 'D', 'R'): 'D',
    (35, 15, 'F', 'D'): 'U',
    (35, 15, 'F', 'L'): 'U',
    (35, 15, 'F', 'R'): 'U',
    (35, 15, 'F', 'U'): 'U',
    (35, 15, 'L', 'B'): 'D',
    (35, 15, 'L', 'D'): 'U',
    (35, 15, 'L', 'F'): 'D',
    (35, 15, 'L', 'U'): 'U',
    (35, 15, 'R', 'B'): 'D',
    (35, 15, 'R', 'D'): 'U',
    (35, 15, 'R', 'F'): 'D',
    (35, 15, 'R', 'U'): 'U',
    (35, 15, 'U', 'B'): 'D',
    (35, 15, 'U', 'F'): 'D',
    (35, 15, 'U', 'L'): 'D',
    (35, 15, 'U', 'R'): 'D',
    (37, 24, 'B', 'D'): 'U',
    (37, 24, 'B', 'L'): 'U',
    (37, 24, 'B', 'R'): 'U',
    (37, 24, 'B', 'U'): 'U',
    (37, 24, 'D', 'B'): 'D',
    (37, 24, 'D', 'F'): 'D',
    (37, 24, 'D', 'L'): 'D',
    (37, 24, 'D', 'R'): 'D',
    (37, 24, 'F', 'D'): 'U',
    (37, 24, 'F', 'L'): 'U',
    (37, 24, 'F', 'R'): 'U',
    (37, 24, 'F', 'U'): 'U',
    (37, 24, 'L', 'B'): 'D',
    (37, 24, 'L', 'D'): 'U',
    (37, 24, 'L', 'F'): 'D',
    (37, 24, 'L', 'U'): 'U',
    (37, 24, 'R', 'B'): 'D',
    (37, 24, 'R', 'D'): 'U',
    (37, 24, 'R', 'F'): 'D',
    (37, 24, 'R', 'U'): 'U',
    (37, 24, 'U', 'B'): 'D',
    (37, 24, 'U', 'F'): 'D',
    (37, 24, 'U', 'L'): 'D',
    (37, 24, 'U', 'R'): 'D',
    (40, 53, 'B', 'D'): 'D',
    (40, 53, 'B', 'L'): 'D',
    (40, 53, 'B', 'R'): 'D',
    (40, 53, 'B', 'U'): 'D',
    (40, 53, 'D', 'B'): 'U',
    (40, 53, 'D', 'F'): 'U',
    (40, 53, 'D', 'L'): 'U',
    (40, 53, 'D', 'R'): 'U',
    (40, 53, 'F', 'D'): 'D',
    (40, 53, 'F', 'L'): 'D',
    (40, 53, 'F', 'R'): 'D',
    (40, 53, 'F', 'U'): 'D',
    (40, 53, 'L', 'B'): 'U',
    (40, 53, 'L', 'D'): 'D',
    (40, 53, 'L', 'F'): 'U',
    (40, 53, 'L', 'U'): 'D',
    (40, 53, 'R', 'B'): 'U',
    (40, 53, 'R', 'D'): 'D',
    (40, 53, 'R', 'F'): 'U',
    (40, 53, 'R', 'U'): 'D',
    (40, 53, 'U', 'B'): 'U',
    (40, 53, 'U', 'F'): 'U',
    (40, 53, 'U', 'L'): 'U',
    (40, 53, 'U', 'R'): 'U',
    (41, 28, 'B', 'D'): 'D',
    (41, 28, 'B', 'L'): 'D',
    (41, 28, 'B', 'R'): 'D',
    (41, 28, 'B', 'U'): 'D',
    (41, 28, 'D', 'B'): 'U',
    (41, 28, 'D', 'F'): 'U',
    (41, 28, 'D', 'L'): 'U',
    (41, 28, 'D', 'R'): 'U',
    (41, 28, 'F', 'D'): 'D',
    (41, 28, 'F', 'L'): 'D',
    (41, 28, 'F', 'R'): 'D',
    (41, 28, 'F', 'U'): 'D',
    (41, 28, 'L', 'B'): 'U',
    (41, 28, 'L', 'D'): 'D',
    (41, 28, 'L', 'F'): 'U',
    (41, 28, 'L', 'U'): 'D',
    (41, 28, 'R', 'B'): 'U',
    (41, 28, 'R', 'D'): 'D',
    (41, 28, 'R', 'F'): 'U',
    (41, 28, 'R', 'U'): 'D',
    (41, 28, 'U', 'B'): 'U',
    (41, 28, 'U', 'F'): 'U',
    (41, 28, 'U', 'L'): 'U',
    (41, 28, 'U', 'R'): 'U',
    (44, 57, 'B', 'D'): 'U',
    (44, 57, 'B', 'L'): 'U',
    (44, 57, 'B', 'R'): 'U',
    (44, 57, 'B', 'U'): 'U',
    (44, 57, 'D', 'B'): 'D',
    (44, 57, 'D', 'F'): 'D',
    (44, 57, 'D', 'L'): 'D',
    (44, 57, 'D', 'R'): 'D',
    (44, 57, 'F', 'D'): 'U',
    (44, 57, 'F', 'L'): 'U',
    (44, 57, 'F', 'R'): 'U',
    (44, 57, 'F', 'U'): 'U',
    (44, 57, 'L', 'B'): 'D',
    (44, 57, 'L', 'D'): 'U',
    (44, 57, 'L', 'F'): 'D',
    (44, 57, 'L', 'U'): 'U',
    (44, 57, 'R', 'B'): 'D',
    (44, 57, 'R', 'D'): 'U',
    (44, 57, 'R', 'F'): 'D',
    (44, 57, 'R', 'U'): 'U',
    (44, 57, 'U', 'B'): 'D',
    (44, 57, 'U', 'F'): 'D',
    (44, 57, 'U', 'L'): 'D',
    (44, 57, 'U', 'R'): 'D',
    (46, 82, 'B', 'D'): 'U',
    (46, 82, 'B', 'L'): 'U',
    (46, 82, 'B', 'R'): 'U',
    (46, 82, 'B', 'U'): 'U',
    (46, 82, 'D', 'B'): 'D',
    (46, 82, 'D', 'F'): 'D',
    (46, 82, 'D', 'L'): 'D',
    (46, 82, 'D', 'R'): 'D',
    (46, 82, 'F', 'D'): 'U',
    (46, 82, 'F', 'L'): 'U',
    (46, 82, 'F', 'R'): 'U',
    (46, 82, 'F', 'U'): 'U',
    (46, 82, 'L', 'B'): 'D',
    (46, 82, 'L', 'D'): 'U',
    (46, 82, 'L', 'F'): 'D',
    (46, 82, 'L', 'U'): 'U',
    (46, 82, 'R', 'B'): 'D',
    (46, 82, 'R', 'D'): 'U',
    (46, 82, 'R', 'F'): 'D',
    (46, 82, 'R', 'U'): 'U',
    (46, 82, 'U', 'B'): 'D',
    (46, 82, 'U', 'F'): 'D',
    (46, 82, 'U', 'L'): 'D',
    (46, 82, 'U', 'R'): 'D',
    (47, 83, 'B', 'D'): 'D',
    (47, 83, 'B', 'L'): 'D',
    (47, 83, 'B', 'R'): 'D',
    (47, 83, 'B', 'U'): 'D',
    (47, 83, 'D', 'B'): 'U',
    (47, 83, 'D', 'F'): 'U',
    (47, 83, 'D', 'L'): 'U',
    (47, 83, 'D', 'R'): 'U',
    (47, 83, 'F', 'D'): 'D',
    (47, 83, 'F', 'L'): 'D',
    (47, 83, 'F', 'R'): 'D',
    (47, 83, 'F', 'U'): 'D',
    (47, 83, 'L', 'B'): 'U',
    (47, 83, 'L', 'D'): 'D',
    (47, 83, 'L', 'F'): 'U',
    (47, 83, 'L', 'U'): 'D',
    (47, 83, 'R', 'B'): 'U',
    (47, 83, 'R', 'D'): 'D',
    (47, 83, 'R', 'F'): 'U',
    (47, 83, 'R', 'U'): 'D',
    (47, 83, 'U', 'B'): 'U',
    (47, 83, 'U', 'F'): 'U',
    (47, 83, 'U', 'L'): 'U',
    (47, 83, 'U', 'R'): 'U',
    (50, 12, 'B', 'D'): 'D',
    (50, 12, 'B', 'L'): 'D',
    (50, 12, 'B', 'R'): 'D',
    (50, 12, 'B', 'U'): 'D',
    (50, 12, 'D', 'B'): 'U',
    (50, 12, 'D', 'F'): 'U',
    (50, 12, 'D', 'L'): 'U',
    (50, 12, 'D', 'R'): 'U',
    (50, 12, 'F', 'D'): 'D',
    (50, 12, 'F', 'L'): 'D',
    (50, 12, 'F', 'R'): 'D',
    (50, 12, 'F', 'U'): 'D',
    (50, 12, 'L', 'B'): 'U',
    (50, 12, 'L', 'D'): 'D',
    (50, 12, 'L', 'F'): 'U',
    (50, 12, 'L', 'U'): 'D',
    (50, 12, 'R', 'B'): 'U',
    (50, 12, 'R', 'D'): 'D',
    (50, 12, 'R', 'F'): 'U',
    (50, 12, 'R', 'U'): 'D',
    (50, 12, 'U', 'B'): 'U',
    (50, 12, 'U', 'F'): 'U',
    (50, 12, 'U', 'L'): 'U',
    (50, 12, 'U', 'R'): 'U',
    (51, 8, 'B', 'D'): 'U',
    (51, 8, 'B', 'L'): 'U',
    (51, 8, 'B', 'R'): 'U',
    (51, 8, 'B', 'U'): 'U',
    (51, 8, 'D', 'B'): 'D',
    (51, 8, 'D', 'F'): 'D',
    (51, 8, 'D', 'L'): 'D',
    (51, 8, 'D', 'R'): 'D',
    (51, 8, 'F', 'D'): 'U',
    (51, 8, 'F', 'L'): 'U',
    (51, 8, 'F', 'R'): 'U',
    (51, 8, 'F', 'U'): 'U',
    (51, 8, 'L', 'B'): 'D',
    (51, 8, 'L', 'D'): 'U',
    (51, 8, 'L', 'F'): 'D',
    (51, 8, 'L', 'U'): 'U',
    (51, 8, 'R', 'B'): 'D',
    (51, 8, 'R', 'D'): 'U',
    (51, 8, 'R', 'F'): 'D',
    (51, 8, 'R', 'U'): 'U',
    (51, 8, 'U', 'B'): 'D',
    (51, 8, 'U', 'F'): 'D',
    (51, 8, 'U', 'L'): 'D',
    (51, 8, 'U', 'R'): 'D',
    (53, 40, 'B', 'D'): 'U',
    (53, 40, 'B', 'L'): 'U',
    (53, 40, 'B', 'R'): 'U',
    (53, 40, 'B', 'U'): 'U',
    (53, 40, 'D', 'B'): 'D',
    (53, 40, 'D', 'F'): 'D',
    (53, 40, 'D', 'L'): 'D',
    (53, 40, 'D', 'R'): 'D',
    (53, 40, 'F', 'D'): 'U',
    (53, 40, 'F', 'L'): 'U',
    (53, 40, 'F', 'R'): 'U',
    (53, 40, 'F', 'U'): 'U',
    (53, 40, 'L', 'B'): 'D',
    (53, 40, 'L', 'D'): 'U',
    (53, 40, 'L', 'F'): 'D',
    (53, 40, 'L', 'U'): 'U',
    (53, 40, 'R', 'B'): 'D',
    (53, 40, 'R', 'D'): 'U',
    (53, 40, 'R', 'F'): 'D',
    (53, 40, 'R', 'U'): 'U',
    (53, 40, 'U', 'B'): 'D',
    (53, 40, 'U', 'F'): 'D',
    (53, 40, 'U', 'L'): 'D',
    (53, 40, 'U', 'R'): 'D',
    (56, 69, 'B', 'D'): 'D',
    (56, 69, 'B', 'L'): 'D',
    (56, 69, 'B', 'R'): 'D',
    (56, 69, 'B', 'U'): 'D',
    (56, 69, 'D', 'B'): 'U',
    (56, 69, 'D', 'F'): 'U',
    (56, 69, 'D', 'L'): 'U',
    (56, 69, 'D', 'R'): 'U',
    (56, 69, 'F', 'D'): 'D',
    (56, 69, 'F', 'L'): 'D',
    (56, 69, 'F', 'R'): 'D',
    (56, 69, 'F', 'U'): 'D',
    (56, 69, 'L', 'B'): 'U',
    (56, 69, 'L', 'D'): 'D',
    (56, 69, 'L', 'F'): 'U',
    (56, 69, 'L', 'U'): 'D',
    (56, 69, 'R', 'B'): 'U',
    (56, 69, 'R', 'D'): 'D',
    (56, 69, 'R', 'F'): 'U',
    (56, 69, 'R', 'U'): 'D',
    (56, 69, 'U', 'B'): 'U',
    (56, 69, 'U', 'F'): 'U',
    (56, 69, 'U', 'L'): 'U',
    (56, 69, 'U', 'R'): 'U',
    (57, 44, 'B', 'D'): 'D',
    (57, 44, 'B', 'L'): 'D',
    (57, 44, 'B', 'R'): 'D',
    (57, 44, 'B', 'U'): 'D',
    (57, 44, 'D', 'B'): 'U',
    (57, 44, 'D', 'F'): 'U',
    (57, 44, 'D', 'L'): 'U',
    (57, 44, 'D', 'R'): 'U',
    (57, 44, 'F', 'D'): 'D',
    (57, 44, 'F', 'L'): 'D',
    (57, 44, 'F', 'R'): 'D',
    (57, 44, 'F', 'U'): 'D',
    (57, 44, 'L', 'B'): 'U',
    (57, 44, 'L', 'D'): 'D',
    (57, 44, 'L', 'F'): 'U',
    (57, 44, 'L', 'U'): 'D',
    (57, 44, 'R', 'B'): 'U',
    (57, 44, 'R', 'D'): 'D',
    (57, 44, 'R', 'F'): 'U',
    (57, 44, 'R', 'U'): 'D',
    (57, 44, 'U', 'B'): 'U',
    (57, 44, 'U', 'F'): 'U',
    (57, 44, 'U', 'L'): 'U',
    (57, 44, 'U', 'R'): 'U',
    (60, 73, 'B', 'D'): 'U',
    (60, 73, 'B', 'L'): 'U',
    (60, 73, 'B', 'R'): 'U',
    (60, 73, 'B', 'U'): 'U',
    (60, 73, 'D', 'B'): 'D',
    (60, 73, 'D', 'F'): 'D',
    (60, 73, 'D', 'L'): 'D',
    (60, 73, 'D', 'R'): 'D',
    (60, 73, 'F', 'D'): 'U',
    (60, 73, 'F', 'L'): 'U',
    (60, 73, 'F', 'R'): 'U',
    (60, 73, 'F', 'U'): 'U',
    (60, 73, 'L', 'B'): 'D',
    (60, 73, 'L', 'D'): 'U',
    (60, 73, 'L', 'F'): 'D',
    (60, 73, 'L', 'U'): 'U',
    (60, 73, 'R', 'B'): 'D',
    (60, 73, 'R', 'D'): 'U',
    (60, 73, 'R', 'F'): 'D',
    (60, 73, 'R', 'U'): 'U',
    (60, 73, 'U', 'B'): 'D',
    (60, 73, 'U', 'F'): 'D',
    (60, 73, 'U', 'L'): 'D',
    (60, 73, 'U', 'R'): 'D',
    (62, 88, 'B', 'D'): 'U',
    (62, 88, 'B', 'L'): 'U',
    (62, 88, 'B', 'R'): 'U',
    (62, 88, 'B', 'U'): 'U',
    (62, 88, 'D', 'B'): 'D',
    (62, 88, 'D', 'F'): 'D',
    (62, 88, 'D', 'L'): 'D',
    (62, 88, 'D', 'R'): 'D',
    (62, 88, 'F', 'D'): 'U',
    (62, 88, 'F', 'L'): 'U',
    (62, 88, 'F', 'R'): 'U',
    (62, 88, 'F', 'U'): 'U',
    (62, 88, 'L', 'B'): 'D',
    (62, 88, 'L', 'D'): 'U',
    (62, 88, 'L', 'F'): 'D',
    (62, 88, 'L', 'U'): 'U',
    (62, 88, 'R', 'B'): 'D',
    (62, 88, 'R', 'D'): 'U',
    (62, 88, 'R', 'F'): 'D',
    (62, 88, 'R', 'U'): 'U',
    (62, 88, 'U', 'B'): 'D',
    (62, 88, 'U', 'F'): 'D',
    (62, 88, 'U', 'L'): 'D',
    (62, 88, 'U', 'R'): 'D',
    (63, 92, 'B', 'D'): 'D',
    (63, 92, 'B', 'L'): 'D',
    (63, 92, 'B', 'R'): 'D',
    (63, 92, 'B', 'U'): 'D',
    (63, 92, 'D', 'B'): 'U',
    (63, 92, 'D', 'F'): 'U',
    (63, 92, 'D', 'L'): 'U',
    (63, 92, 'D', 'R'): 'U',
    (63, 92, 'F', 'D'): 'D',
    (63, 92, 'F', 'L'): 'D',
    (63, 92, 'F', 'R'): 'D',
    (63, 92, 'F', 'U'): 'D',
    (63, 92, 'L', 'B'): 'U',
    (63, 92, 'L', 'D'): 'D',
    (63, 92, 'L', 'F'): 'U',
    (63, 92, 'L', 'U'): 'D',
    (63, 92, 'R', 'B'): 'U',
    (63, 92, 'R', 'D'): 'D',
    (63, 92, 'R', 'F'): 'U',
    (63, 92, 'R', 'U'): 'D',
    (63, 92, 'U', 'B'): 'U',
    (63, 92, 'U', 'F'): 'U',
    (63, 92, 'U', 'L'): 'U',
    (63, 92, 'U', 'R'): 'U',
    (66, 3, 'B', 'D'): 'D',
    (66, 3, 'B', 'L'): 'D',
    (66, 3, 'B', 'R'): 'D',
    (66, 3, 'B', 'U'): 'D',
    (66, 3, 'D', 'B'): 'U',
    (66, 3, 'D', 'F'): 'U',
    (66, 3, 'D', 'L'): 'U',
    (66, 3, 'D', 'R'): 'U',
    (66, 3, 'F', 'D'): 'D',
    (66, 3, 'F', 'L'): 'D',
    (66, 3, 'F', 'R'): 'D',
    (66, 3, 'F', 'U'): 'D',
    (66, 3, 'L', 'B'): 'U',
    (66, 3, 'L', 'D'): 'D',
    (66, 3, 'L', 'F'): 'U',
    (66, 3, 'L', 'U'): 'D',
    (66, 3, 'R', 'B'): 'U',
    (66, 3, 'R', 'D'): 'D',
    (66, 3, 'R', 'F'): 'U',
    (66, 3, 'R', 'U'): 'D',
    (66, 3, 'U', 'B'): 'U',
    (66, 3, 'U', 'F'): 'U',
    (66, 3, 'U', 'L'): 'U',
    (66, 3, 'U', 'R'): 'U',
    (67, 2, 'B', 'D'): 'U',
    (67, 2, 'B', 'L'): 'U',
    (67, 2, 'B', 'R'): 'U',
    (67, 2, 'B', 'U'): 'U',
    (67, 2, 'D', 'B'): 'D',
    (67, 2, 'D', 'F'): 'D',
    (67, 2, 'D', 'L'): 'D',
    (67, 2, 'D', 'R'): 'D',
    (67, 2, 'F', 'D'): 'U',
    (67, 2, 'F', 'L'): 'U',
    (67, 2, 'F', 'R'): 'U',
    (67, 2, 'F', 'U'): 'U',
    (67, 2, 'L', 'B'): 'D',
    (67, 2, 'L', 'D'): 'U',
    (67, 2, 'L', 'F'): 'D',
    (67, 2, 'L', 'U'): 'U',
    (67, 2, 'R', 'B'): 'D',
    (67, 2, 'R', 'D'): 'U',
    (67, 2, 'R', 'F'): 'D',
    (67, 2, 'R', 'U'): 'U',
    (67, 2, 'U', 'B'): 'D',
    (67, 2, 'U', 'F'): 'D',
    (67, 2, 'U', 'L'): 'D',
    (67, 2, 'U', 'R'): 'D',
    (69, 56, 'B', 'D'): 'U',
    (69, 56, 'B', 'L'): 'U',
    (69, 56, 'B', 'R'): 'U',
    (69, 56, 'B', 'U'): 'U',
    (69, 56, 'D', 'B'): 'D',
    (69, 56, 'D', 'F'): 'D',
    (69, 56, 'D', 'L'): 'D',
    (69, 56, 'D', 'R'): 'D',
    (69, 56, 'F', 'D'): 'U',
    (69, 56, 'F', 'L'): 'U',
    (69, 56, 'F', 'R'): 'U',
    (69, 56, 'F', 'U'): 'U',
    (69, 56, 'L', 'B'): 'D',
    (69, 56, 'L', 'D'): 'U',
    (69, 56, 'L', 'F'): 'D',
    (69, 56, 'L', 'U'): 'U',
    (69, 56, 'R', 'B'): 'D',
    (69, 56, 'R', 'D'): 'U',
    (69, 56, 'R', 'F'): 'D',
    (69, 56, 'R', 'U'): 'U',
    (69, 56, 'U', 'B'): 'D',
    (69, 56, 'U', 'F'): 'D',
    (69, 56, 'U', 'L'): 'D',
    (69, 56, 'U', 'R'): 'D',
    (72, 21, 'B', 'D'): 'D',
    (72, 21, 'B', 'L'): 'D',
    (72, 21, 'B', 'R'): 'D',
    (72, 21, 'B', 'U'): 'D',
    (72, 21, 'D', 'B'): 'U',
    (72, 21, 'D', 'F'): 'U',
    (72, 21, 'D', 'L'): 'U',
    (72, 21, 'D', 'R'): 'U',
    (72, 21, 'F', 'D'): 'D',
    (72, 21, 'F', 'L'): 'D',
    (72, 21, 'F', 'R'): 'D',
    (72, 21, 'F', 'U'): 'D',
    (72, 21, 'L', 'B'): 'U',
    (72, 21, 'L', 'D'): 'D',
    (72, 21, 'L', 'F'): 'U',
    (72, 21, 'L', 'U'): 'D',
    (72, 21, 'R', 'B'): 'U',
    (72, 21, 'R', 'D'): 'D',
    (72, 21, 'R', 'F'): 'U',
    (72, 21, 'R', 'U'): 'D',
    (72, 21, 'U', 'B'): 'U',
    (72, 21, 'U', 'F'): 'U',
    (72, 21, 'U', 'L'): 'U',
    (72, 21, 'U', 'R'): 'U',
    (73, 60, 'B', 'D'): 'D',
    (73, 60, 'B', 'L'): 'D',
    (73, 60, 'B', 'R'): 'D',
    (73, 60, 'B', 'U'): 'D',
    (73, 60, 'D', 'B'): 'U',
    (73, 60, 'D', 'F'): 'U',
    (73, 60, 'D', 'L'): 'U',
    (73, 60, 'D', 'R'): 'U',
    (73, 60, 'F', 'D'): 'D',
    (73, 60, 'F', 'L'): 'D',
    (73, 60, 'F', 'R'): 'D',
    (73, 60, 'F', 'U'): 'D',
    (73, 60, 'L', 'B'): 'U',
    (73, 60, 'L', 'D'): 'D',
    (73, 60, 'L', 'F'): 'U',
    (73, 60, 'L', 'U'): 'D',
    (73, 60, 'R', 'B'): 'U',
    (73, 60, 'R', 'D'): 'D',
    (73, 60, 'R', 'F'): 'U',
    (73, 60, 'R', 'U'): 'D',
    (73, 60, 'U', 'B'): 'U',
    (73, 60, 'U', 'F'): 'U',
    (73, 60, 'U', 'L'): 'U',
    (73, 60, 'U', 'R'): 'U',
    (76, 25, 'B', 'D'): 'U',
    (76, 25, 'B', 'L'): 'U',
    (76, 25, 'B', 'R'): 'U',
    (76, 25, 'B', 'U'): 'U',
    (76, 25, 'D', 'B'): 'D',
    (76, 25, 'D', 'F'): 'D',
    (76, 25, 'D', 'L'): 'D',
    (76, 25, 'D', 'R'): 'D',
    (76, 25, 'F', 'D'): 'U',
    (76, 25, 'F', 'L'): 'U',
    (76, 25, 'F', 'R'): 'U',
    (76, 25, 'F', 'U'): 'U',
    (76, 25, 'L', 'B'): 'D',
    (76, 25, 'L', 'D'): 'U',
    (76, 25, 'L', 'F'): 'D',
    (76, 25, 'L', 'U'): 'U',
    (76, 25, 'R', 'B'): 'D',
    (76, 25, 'R', 'D'): 'U',
    (76, 25, 'R', 'F'): 'D',
    (76, 25, 'R', 'U'): 'U',
    (76, 25, 'U', 'B'): 'D',
    (76, 25, 'U', 'F'): 'D',
    (76, 25, 'U', 'L'): 'D',
    (76, 25, 'U', 'R'): 'D',
    (78, 95, 'B', 'D'): 'U',
    (78, 95, 'B', 'L'): 'U',
    (78, 95, 'B', 'R'): 'U',
    (78, 95, 'B', 'U'): 'U',
    (78, 95, 'D', 'B'): 'D',
    (78, 95, 'D', 'F'): 'D',
    (78, 95, 'D', 'L'): 'D',
    (78, 95, 'D', 'R'): 'D',
    (78, 95, 'F', 'D'): 'U',
    (78, 95, 'F', 'L'): 'U',
    (78, 95, 'F', 'R'): 'U',
    (78, 95, 'F', 'U'): 'U',
    (78, 95, 'L', 'B'): 'D',
    (78, 95, 'L', 'D'): 'U',
    (78, 95, 'L', 'F'): 'D',
    (78, 95, 'L', 'U'): 'U',
    (78, 95, 'R', 'B'): 'D',
    (78, 95, 'R', 'D'): 'U',
    (78, 95, 'R', 'F'): 'D',
    (78, 95, 'R', 'U'): 'U',
    (78, 95, 'U', 'B'): 'D',
    (78, 95, 'U', 'F'): 'D',
    (78, 95, 'U', 'L'): 'D',
    (78, 95, 'U', 'R'): 'D',
    (79, 94, 'B', 'D'): 'D',
    (79, 94, 'B', 'L'): 'D',
    (79, 94, 'B', 'R'): 'D',
    (79, 94, 'B', 'U'): 'D',
    (79, 94, 'D', 'B'): 'U',
    (79, 94, 'D', 'F'): 'U',
    (79, 94, 'D', 'L'): 'U',
    (79, 94, 'D', 'R'): 'U',
    (79, 94, 'F', 'D'): 'D',
    (79, 94, 'F', 'L'): 'D',
    (79, 94, 'F', 'R'): 'D',
    (79, 94, 'F', 'U'): 'D',
    (79, 94, 'L', 'B'): 'U',
    (79, 94, 'L', 'D'): 'D',
    (79, 94, 'L', 'F'): 'U',
    (79, 94, 'L', 'U'): 'D',
    (79, 94, 'R', 'B'): 'U',
    (79, 94, 'R', 'D'): 'D',
    (79, 94, 'R', 'F'): 'U',
    (79, 94, 'R', 'U'): 'D',
    (79, 94, 'U', 'B'): 'U',
    (79, 94, 'U', 'F'): 'U',
    (79, 94, 'U', 'L'): 'U',
    (79, 94, 'U', 'R'): 'U',
    (82, 46, 'B', 'D'): 'D',
    (82, 46, 'B', 'L'): 'D',
    (82, 46, 'B', 'R'): 'D',
    (82, 46, 'B', 'U'): 'D',
    (82, 46, 'D', 'B'): 'U',
    (82, 46, 'D', 'F'): 'U',
    (82, 46, 'D', 'L'): 'U',
    (82, 46, 'D', 'R'): 'U',
    (82, 46, 'F', 'D'): 'D',
    (82, 46, 'F', 'L'): 'D',
    (82, 46, 'F', 'R'): 'D',
    (82, 46, 'F', 'U'): 'D',
    (82, 46, 'L', 'B'): 'U',
    (82, 46, 'L', 'D'): 'D',
    (82, 46, 'L', 'F'): 'U',
    (82, 46, 'L', 'U'): 'D',
    (82, 46, 'R', 'B'): 'U',
    (82, 46, 'R', 'D'): 'D',
    (82, 46, 'R', 'F'): 'U',
    (82, 46, 'R', 'U'): 'D',
    (82, 46, 'U', 'B'): 'U',
    (82, 46, 'U', 'F'): 'U',
    (82, 46, 'U', 'L'): 'U',
    (82, 46, 'U', 'R'): 'U',
    (83, 47, 'B', 'D'): 'U',
    (83, 47, 'B', 'L'): 'U',
    (83, 47, 'B', 'R'): 'U',
    (83, 47, 'B', 'U'): 'U',
    (83, 47, 'D', 'B'): 'D',
    (83, 47, 'D', 'F'): 'D',
    (83, 47, 'D', 'L'): 'D',
    (83, 47, 'D', 'R'): 'D',
    (83, 47, 'F', 'D'): 'U',
    (83, 47, 'F', 'L'): 'U',
    (83, 47, 'F', 'R'): 'U',
    (83, 47, 'F', 'U'): 'U',
    (83, 47, 'L', 'B'): 'D',
    (83, 47, 'L', 'D'): 'U',
    (83, 47, 'L', 'F'): 'D',
    (83, 47, 'L', 'U'): 'U',
    (83, 47, 'R', 'B'): 'D',
    (83, 47, 'R', 'D'): 'U',
    (83, 47, 'R', 'F'): 'D',
    (83, 47, 'R', 'U'): 'U',
    (83, 47, 'U', 'B'): 'D',
    (83, 47, 'U', 'F'): 'D',
    (83, 47, 'U', 'L'): 'D',
    (83, 47, 'U', 'R'): 'D',
    (85, 31, 'B', 'D'): 'U',
    (85, 31, 'B', 'L'): 'U',
    (85, 31, 'B', 'R'): 'U',
    (85, 31, 'B', 'U'): 'U',
    (85, 31, 'D', 'B'): 'D',
    (85, 31, 'D', 'F'): 'D',
    (85, 31, 'D', 'L'): 'D',
    (85, 31, 'D', 'R'): 'D',
    (85, 31, 'F', 'D'): 'U',
    (85, 31, 'F', 'L'): 'U',
    (85, 31, 'F', 'R'): 'U',
    (85, 31, 'F', 'U'): 'U',
    (85, 31, 'L', 'B'): 'D',
    (85, 31, 'L', 'D'): 'U',
    (85, 31, 'L', 'F'): 'D',
    (85, 31, 'L', 'U'): 'U',
    (85, 31, 'R', 'B'): 'D',
    (85, 31, 'R', 'D'): 'U',
    (85, 31, 'R', 'F'): 'D',
    (85, 31, 'R', 'U'): 'U',
    (85, 31, 'U', 'B'): 'D',
    (85, 31, 'U', 'F'): 'D',
    (85, 31, 'U', 'L'): 'D',
    (85, 31, 'U', 'R'): 'D',
    (88, 62, 'B', 'D'): 'D',
    (88, 62, 'B', 'L'): 'D',
    (88, 62, 'B', 'R'): 'D',
    (88, 62, 'B', 'U'): 'D',
    (88, 62, 'D', 'B'): 'U',
    (88, 62, 'D', 'F'): 'U',
    (88, 62, 'D', 'L'): 'U',
    (88, 62, 'D', 'R'): 'U',
    (88, 62, 'F', 'D'): 'D',
    (88, 62, 'F', 'L'): 'D',
    (88, 62, 'F', 'R'): 'D',
    (88, 62, 'F', 'U'): 'D',
    (88, 62, 'L', 'B'): 'U',
    (88, 62, 'L', 'D'): 'D',
    (88, 62, 'L', 'F'): 'U',
    (88, 62, 'L', 'U'): 'D',
    (88, 62, 'R', 'B'): 'U',
    (88, 62, 'R', 'D'): 'D',
    (88, 62, 'R', 'F'): 'U',
    (88, 62, 'R', 'U'): 'D',
    (88, 62, 'U', 'B'): 'U',
    (88, 62, 'U', 'F'): 'U',
    (88, 62, 'U', 'L'): 'U',
    (88, 62, 'U', 'R'): 'U',
    (89, 30, 'B', 'D'): 'D',
    (89, 30, 'B', 'L'): 'D',
    (89, 30, 'B', 'R'): 'D',
    (89, 30, 'B', 'U'): 'D',
    (89, 30, 'D', 'B'): 'U',
    (89, 30, 'D', 'F'): 'U',
    (89, 30, 'D', 'L'): 'U',
    (89, 30, 'D', 'R'): 'U',
    (89, 30, 'F', 'D'): 'D',
    (89, 30, 'F', 'L'): 'D',
    (89, 30, 'F', 'R'): 'D',
    (89, 30, 'F', 'U'): 'D',
    (89, 30, 'L', 'B'): 'U',
    (89, 30, 'L', 'D'): 'D',
    (89, 30, 'L', 'F'): 'U',
    (89, 30, 'L', 'U'): 'D',
    (89, 30, 'R', 'B'): 'U',
    (89, 30, 'R', 'D'): 'D',
    (89, 30, 'R', 'F'): 'U',
    (89, 30, 'R', 'U'): 'D',
    (89, 30, 'U', 'B'): 'U',
    (89, 30, 'U', 'F'): 'U',
    (89, 30, 'U', 'L'): 'U',
    (89, 30, 'U', 'R'): 'U',
    (92, 63, 'B', 'D'): 'U',
    (92, 63, 'B', 'L'): 'U',
    (92, 63, 'B', 'R'): 'U',
    (92, 63, 'B', 'U'): 'U',
    (92, 63, 'D', 'B'): 'D',
    (92, 63, 'D', 'F'): 'D',
    (92, 63, 'D', 'L'): 'D',
    (92, 63, 'D', 'R'): 'D',
    (92, 63, 'F', 'D'): 'U',
    (92, 63, 'F', 'L'): 'U',
    (92, 63, 'F', 'R'): 'U',
    (92, 63, 'F', 'U'): 'U',
    (92, 63, 'L', 'B'): 'D',
    (92, 63, 'L', 'D'): 'U',
    (92, 63, 'L', 'F'): 'D',
    (92, 63, 'L', 'U'): 'U',
    (92, 63, 'R', 'B'): 'D',
    (92, 63, 'R', 'D'): 'U',
    (92, 63, 'R', 'F'): 'D',
    (92, 63, 'R', 'U'): 'U',
    (92, 63, 'U', 'B'): 'D',
    (92, 63, 'U', 'F'): 'D',
    (92, 63, 'U', 'L'): 'D',
    (92, 63, 'U', 'R'): 'D',
    (94, 79, 'B', 'D'): 'U',
    (94, 79, 'B', 'L'): 'U',
    (94, 79, 'B', 'R'): 'U',
    (94, 79, 'B', 'U'): 'U',
    (94, 79, 'D', 'B'): 'D',
    (94, 79, 'D', 'F'): 'D',
    (94, 79, 'D', 'L'): 'D',
    (94, 79, 'D', 'R'): 'D',
    (94, 79, 'F', 'D'): 'U',
    (94, 79, 'F', 'L'): 'U',
    (94, 79, 'F', 'R'): 'U',
    (94, 79, 'F', 'U'): 'U',
    (94, 79, 'L', 'B'): 'D',
    (94, 79, 'L', 'D'): 'U',
    (94, 79, 'L', 'F'): 'D',
    (94, 79, 'L', 'U'): 'U',
    (94, 79, 'R', 'B'): 'D',
    (94, 79, 'R', 'D'): 'U',
    (94, 79, 'R', 'F'): 'D',
    (94, 79, 'R', 'U'): 'U',
    (94, 79, 'U', 'B'): 'D',
    (94, 79, 'U', 'F'): 'D',
    (94, 79, 'U', 'L'): 'D',
    (94, 79, 'U', 'R'): 'D',
    (95, 78, 'B', 'D'): 'D',
    (95, 78, 'B', 'L'): 'D',
    (95, 78, 'B', 'R'): 'D',
    (95, 78, 'B', 'U'): 'D',
    (95, 78, 'D', 'B'): 'U',
    (95, 78, 'D', 'F'): 'U',
    (95, 78, 'D', 'L'): 'U',
    (95, 78, 'D', 'R'): 'U',
    (95, 78, 'F', 'D'): 'D',
    (95, 78, 'F', 'L'): 'D',
    (95, 78, 'F', 'R'): 'D',
    (95, 78, 'F', 'U'): 'D',
    (95, 78, 'L', 'B'): 'U',
    (95, 78, 'L', 'D'): 'D',
    (95, 78, 'L', 'F'): 'U',
    (95, 78, 'L', 'U'): 'D',
    (95, 78, 'R', 'B'): 'U',
    (95, 78, 'R', 'D'): 'D',
    (95, 78, 'R', 'F'): 'U',
    (95, 78, 'R', 'U'): 'D',
    (95, 78, 'U', 'B'): 'U',
    (95, 78, 'U', 'F'): 'U',
    (95, 78, 'U', 'L'): 'U',
    (95, 78, 'U', 'R'): 'U'
}


tsai_edge_mapping_combinations = {
    0 : (set()),
    2 : (
        set(('UB', 'UL')),
        set(('UB', 'UR')),
        set(('UB', 'UF')),
        set(('UB', 'LB')),
        set(('UB', 'LF')),
        set(('UB', 'RB')),
        set(('UB', 'RF')),
        set(('UB', 'DB')),
        set(('UB', 'DL')),
        set(('UB', 'DR')),
        set(('UB', 'DF')),
        set(('UL', 'UR')),
        set(('UL', 'UF')),
        set(('UL', 'LB')),
        set(('UL', 'LF')),
        set(('UL', 'RB')),
        set(('UL', 'RF')),
        set(('UL', 'DB')),
        set(('UL', 'DL')),
        set(('UL', 'DR')),
        set(('UL', 'DF')),
        set(('UR', 'UF')),
        set(('UR', 'LB')),
        set(('UR', 'LF')),
        set(('UR', 'RB')),
        set(('UR', 'RF')),
        set(('UR', 'DB')),
        set(('UR', 'DL')),
        set(('UR', 'DR')),
        set(('UR', 'DF')),
        set(('UF', 'LB')),
        set(('UF', 'LF')),
        set(('UF', 'RB')),
        set(('UF', 'RF')),
        set(('UF', 'DB')),
        set(('UF', 'DL')),
        set(('UF', 'DR')),
        set(('UF', 'DF')),
        set(('LB', 'LF')),
        set(('LB', 'RB')),
        set(('LB', 'RF')),
        set(('LB', 'DB')),
        set(('LB', 'DL')),
        set(('LB', 'DR')),
        set(('LB', 'DF')),
        set(('LF', 'RB')),
        set(('LF', 'RF')),
        set(('LF', 'DB')),
        set(('LF', 'DL')),
        set(('LF', 'DR')),
        set(('LF', 'DF')),
        set(('RB', 'RF')),
        set(('RB', 'DB')),
        set(('RB', 'DL')),
        set(('RB', 'DR')),
        set(('RB', 'DF')),
        set(('RF', 'DB')),
        set(('RF', 'DL')),
        set(('RF', 'DR')),
        set(('RF', 'DF')),
        set(('DB', 'DL')),
        set(('DB', 'DR')),
        set(('DB', 'DF')),
        set(('DL', 'DR')),
        set(('DL', 'DF')),
        set(('DR', 'DF')),
    ),
    4 : (
        set(('UB', 'UL', 'UR', 'UF')),
        set(('UB', 'UL', 'UR', 'LB')),
        set(('UB', 'UL', 'UR', 'LF')),
        set(('UB', 'UL', 'UR', 'RB')),
        set(('UB', 'UL', 'UR', 'RF')),
        set(('UB', 'UL', 'UR', 'DB')),
        set(('UB', 'UL', 'UR', 'DL')),
        set(('UB', 'UL', 'UR', 'DR')),
        set(('UB', 'UL', 'UR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB')),
        set(('UB', 'UL', 'UF', 'LF')),
        set(('UB', 'UL', 'UF', 'RB')),
        set(('UB', 'UL', 'UF', 'RF')),
        set(('UB', 'UL', 'UF', 'DB')),
        set(('UB', 'UL', 'UF', 'DL')),
        set(('UB', 'UL', 'UF', 'DR')),
        set(('UB', 'UL', 'UF', 'DF')),
        set(('UB', 'UL', 'LB', 'LF')),
        set(('UB', 'UL', 'LB', 'RB')),
        set(('UB', 'UL', 'LB', 'RF')),
        set(('UB', 'UL', 'LB', 'DB')),
        set(('UB', 'UL', 'LB', 'DL')),
        set(('UB', 'UL', 'LB', 'DR')),
        set(('UB', 'UL', 'LB', 'DF')),
        set(('UB', 'UL', 'LF', 'RB')),
        set(('UB', 'UL', 'LF', 'RF')),
        set(('UB', 'UL', 'LF', 'DB')),
        set(('UB', 'UL', 'LF', 'DL')),
        set(('UB', 'UL', 'LF', 'DR')),
        set(('UB', 'UL', 'LF', 'DF')),
        set(('UB', 'UL', 'RB', 'RF')),
        set(('UB', 'UL', 'RB', 'DB')),
        set(('UB', 'UL', 'RB', 'DL')),
        set(('UB', 'UL', 'RB', 'DR')),
        set(('UB', 'UL', 'RB', 'DF')),
        set(('UB', 'UL', 'RF', 'DB')),
        set(('UB', 'UL', 'RF', 'DL')),
        set(('UB', 'UL', 'RF', 'DR')),
        set(('UB', 'UL', 'RF', 'DF')),
        set(('UB', 'UL', 'DB', 'DL')),
        set(('UB', 'UL', 'DB', 'DR')),
        set(('UB', 'UL', 'DB', 'DF')),
        set(('UB', 'UL', 'DL', 'DR')),
        set(('UB', 'UL', 'DL', 'DF')),
        set(('UB', 'UL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB')),
        set(('UB', 'UR', 'UF', 'LF')),
        set(('UB', 'UR', 'UF', 'RB')),
        set(('UB', 'UR', 'UF', 'RF')),
        set(('UB', 'UR', 'UF', 'DB')),
        set(('UB', 'UR', 'UF', 'DL')),
        set(('UB', 'UR', 'UF', 'DR')),
        set(('UB', 'UR', 'UF', 'DF')),
        set(('UB', 'UR', 'LB', 'LF')),
        set(('UB', 'UR', 'LB', 'RB')),
        set(('UB', 'UR', 'LB', 'RF')),
        set(('UB', 'UR', 'LB', 'DB')),
        set(('UB', 'UR', 'LB', 'DL')),
        set(('UB', 'UR', 'LB', 'DR')),
        set(('UB', 'UR', 'LB', 'DF')),
        set(('UB', 'UR', 'LF', 'RB')),
        set(('UB', 'UR', 'LF', 'RF')),
        set(('UB', 'UR', 'LF', 'DB')),
        set(('UB', 'UR', 'LF', 'DL')),
        set(('UB', 'UR', 'LF', 'DR')),
        set(('UB', 'UR', 'LF', 'DF')),
        set(('UB', 'UR', 'RB', 'RF')),
        set(('UB', 'UR', 'RB', 'DB')),
        set(('UB', 'UR', 'RB', 'DL')),
        set(('UB', 'UR', 'RB', 'DR')),
        set(('UB', 'UR', 'RB', 'DF')),
        set(('UB', 'UR', 'RF', 'DB')),
        set(('UB', 'UR', 'RF', 'DL')),
        set(('UB', 'UR', 'RF', 'DR')),
        set(('UB', 'UR', 'RF', 'DF')),
        set(('UB', 'UR', 'DB', 'DL')),
        set(('UB', 'UR', 'DB', 'DR')),
        set(('UB', 'UR', 'DB', 'DF')),
        set(('UB', 'UR', 'DL', 'DR')),
        set(('UB', 'UR', 'DL', 'DF')),
        set(('UB', 'UR', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF')),
        set(('UB', 'UF', 'LB', 'RB')),
        set(('UB', 'UF', 'LB', 'RF')),
        set(('UB', 'UF', 'LB', 'DB')),
        set(('UB', 'UF', 'LB', 'DL')),
        set(('UB', 'UF', 'LB', 'DR')),
        set(('UB', 'UF', 'LB', 'DF')),
        set(('UB', 'UF', 'LF', 'RB')),
        set(('UB', 'UF', 'LF', 'RF')),
        set(('UB', 'UF', 'LF', 'DB')),
        set(('UB', 'UF', 'LF', 'DL')),
        set(('UB', 'UF', 'LF', 'DR')),
        set(('UB', 'UF', 'LF', 'DF')),
        set(('UB', 'UF', 'RB', 'RF')),
        set(('UB', 'UF', 'RB', 'DB')),
        set(('UB', 'UF', 'RB', 'DL')),
        set(('UB', 'UF', 'RB', 'DR')),
        set(('UB', 'UF', 'RB', 'DF')),
        set(('UB', 'UF', 'RF', 'DB')),
        set(('UB', 'UF', 'RF', 'DL')),
        set(('UB', 'UF', 'RF', 'DR')),
        set(('UB', 'UF', 'RF', 'DF')),
        set(('UB', 'UF', 'DB', 'DL')),
        set(('UB', 'UF', 'DB', 'DR')),
        set(('UB', 'UF', 'DB', 'DF')),
        set(('UB', 'UF', 'DL', 'DR')),
        set(('UB', 'UF', 'DL', 'DF')),
        set(('UB', 'UF', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'RB')),
        set(('UB', 'LB', 'LF', 'RF')),
        set(('UB', 'LB', 'LF', 'DB')),
        set(('UB', 'LB', 'LF', 'DL')),
        set(('UB', 'LB', 'LF', 'DR')),
        set(('UB', 'LB', 'LF', 'DF')),
        set(('UB', 'LB', 'RB', 'RF')),
        set(('UB', 'LB', 'RB', 'DB')),
        set(('UB', 'LB', 'RB', 'DL')),
        set(('UB', 'LB', 'RB', 'DR')),
        set(('UB', 'LB', 'RB', 'DF')),
        set(('UB', 'LB', 'RF', 'DB')),
        set(('UB', 'LB', 'RF', 'DL')),
        set(('UB', 'LB', 'RF', 'DR')),
        set(('UB', 'LB', 'RF', 'DF')),
        set(('UB', 'LB', 'DB', 'DL')),
        set(('UB', 'LB', 'DB', 'DR')),
        set(('UB', 'LB', 'DB', 'DF')),
        set(('UB', 'LB', 'DL', 'DR')),
        set(('UB', 'LB', 'DL', 'DF')),
        set(('UB', 'LB', 'DR', 'DF')),
        set(('UB', 'LF', 'RB', 'RF')),
        set(('UB', 'LF', 'RB', 'DB')),
        set(('UB', 'LF', 'RB', 'DL')),
        set(('UB', 'LF', 'RB', 'DR')),
        set(('UB', 'LF', 'RB', 'DF')),
        set(('UB', 'LF', 'RF', 'DB')),
        set(('UB', 'LF', 'RF', 'DL')),
        set(('UB', 'LF', 'RF', 'DR')),
        set(('UB', 'LF', 'RF', 'DF')),
        set(('UB', 'LF', 'DB', 'DL')),
        set(('UB', 'LF', 'DB', 'DR')),
        set(('UB', 'LF', 'DB', 'DF')),
        set(('UB', 'LF', 'DL', 'DR')),
        set(('UB', 'LF', 'DL', 'DF')),
        set(('UB', 'LF', 'DR', 'DF')),
        set(('UB', 'RB', 'RF', 'DB')),
        set(('UB', 'RB', 'RF', 'DL')),
        set(('UB', 'RB', 'RF', 'DR')),
        set(('UB', 'RB', 'RF', 'DF')),
        set(('UB', 'RB', 'DB', 'DL')),
        set(('UB', 'RB', 'DB', 'DR')),
        set(('UB', 'RB', 'DB', 'DF')),
        set(('UB', 'RB', 'DL', 'DR')),
        set(('UB', 'RB', 'DL', 'DF')),
        set(('UB', 'RB', 'DR', 'DF')),
        set(('UB', 'RF', 'DB', 'DL')),
        set(('UB', 'RF', 'DB', 'DR')),
        set(('UB', 'RF', 'DB', 'DF')),
        set(('UB', 'RF', 'DL', 'DR')),
        set(('UB', 'RF', 'DL', 'DF')),
        set(('UB', 'RF', 'DR', 'DF')),
        set(('UB', 'DB', 'DL', 'DR')),
        set(('UB', 'DB', 'DL', 'DF')),
        set(('UB', 'DB', 'DR', 'DF')),
        set(('UB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB')),
        set(('UL', 'UR', 'UF', 'LF')),
        set(('UL', 'UR', 'UF', 'RB')),
        set(('UL', 'UR', 'UF', 'RF')),
        set(('UL', 'UR', 'UF', 'DB')),
        set(('UL', 'UR', 'UF', 'DL')),
        set(('UL', 'UR', 'UF', 'DR')),
        set(('UL', 'UR', 'UF', 'DF')),
        set(('UL', 'UR', 'LB', 'LF')),
        set(('UL', 'UR', 'LB', 'RB')),
        set(('UL', 'UR', 'LB', 'RF')),
        set(('UL', 'UR', 'LB', 'DB')),
        set(('UL', 'UR', 'LB', 'DL')),
        set(('UL', 'UR', 'LB', 'DR')),
        set(('UL', 'UR', 'LB', 'DF')),
        set(('UL', 'UR', 'LF', 'RB')),
        set(('UL', 'UR', 'LF', 'RF')),
        set(('UL', 'UR', 'LF', 'DB')),
        set(('UL', 'UR', 'LF', 'DL')),
        set(('UL', 'UR', 'LF', 'DR')),
        set(('UL', 'UR', 'LF', 'DF')),
        set(('UL', 'UR', 'RB', 'RF')),
        set(('UL', 'UR', 'RB', 'DB')),
        set(('UL', 'UR', 'RB', 'DL')),
        set(('UL', 'UR', 'RB', 'DR')),
        set(('UL', 'UR', 'RB', 'DF')),
        set(('UL', 'UR', 'RF', 'DB')),
        set(('UL', 'UR', 'RF', 'DL')),
        set(('UL', 'UR', 'RF', 'DR')),
        set(('UL', 'UR', 'RF', 'DF')),
        set(('UL', 'UR', 'DB', 'DL')),
        set(('UL', 'UR', 'DB', 'DR')),
        set(('UL', 'UR', 'DB', 'DF')),
        set(('UL', 'UR', 'DL', 'DR')),
        set(('UL', 'UR', 'DL', 'DF')),
        set(('UL', 'UR', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF')),
        set(('UL', 'UF', 'LB', 'RB')),
        set(('UL', 'UF', 'LB', 'RF')),
        set(('UL', 'UF', 'LB', 'DB')),
        set(('UL', 'UF', 'LB', 'DL')),
        set(('UL', 'UF', 'LB', 'DR')),
        set(('UL', 'UF', 'LB', 'DF')),
        set(('UL', 'UF', 'LF', 'RB')),
        set(('UL', 'UF', 'LF', 'RF')),
        set(('UL', 'UF', 'LF', 'DB')),
        set(('UL', 'UF', 'LF', 'DL')),
        set(('UL', 'UF', 'LF', 'DR')),
        set(('UL', 'UF', 'LF', 'DF')),
        set(('UL', 'UF', 'RB', 'RF')),
        set(('UL', 'UF', 'RB', 'DB')),
        set(('UL', 'UF', 'RB', 'DL')),
        set(('UL', 'UF', 'RB', 'DR')),
        set(('UL', 'UF', 'RB', 'DF')),
        set(('UL', 'UF', 'RF', 'DB')),
        set(('UL', 'UF', 'RF', 'DL')),
        set(('UL', 'UF', 'RF', 'DR')),
        set(('UL', 'UF', 'RF', 'DF')),
        set(('UL', 'UF', 'DB', 'DL')),
        set(('UL', 'UF', 'DB', 'DR')),
        set(('UL', 'UF', 'DB', 'DF')),
        set(('UL', 'UF', 'DL', 'DR')),
        set(('UL', 'UF', 'DL', 'DF')),
        set(('UL', 'UF', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'RB')),
        set(('UL', 'LB', 'LF', 'RF')),
        set(('UL', 'LB', 'LF', 'DB')),
        set(('UL', 'LB', 'LF', 'DL')),
        set(('UL', 'LB', 'LF', 'DR')),
        set(('UL', 'LB', 'LF', 'DF')),
        set(('UL', 'LB', 'RB', 'RF')),
        set(('UL', 'LB', 'RB', 'DB')),
        set(('UL', 'LB', 'RB', 'DL')),
        set(('UL', 'LB', 'RB', 'DR')),
        set(('UL', 'LB', 'RB', 'DF')),
        set(('UL', 'LB', 'RF', 'DB')),
        set(('UL', 'LB', 'RF', 'DL')),
        set(('UL', 'LB', 'RF', 'DR')),
        set(('UL', 'LB', 'RF', 'DF')),
        set(('UL', 'LB', 'DB', 'DL')),
        set(('UL', 'LB', 'DB', 'DR')),
        set(('UL', 'LB', 'DB', 'DF')),
        set(('UL', 'LB', 'DL', 'DR')),
        set(('UL', 'LB', 'DL', 'DF')),
        set(('UL', 'LB', 'DR', 'DF')),
        set(('UL', 'LF', 'RB', 'RF')),
        set(('UL', 'LF', 'RB', 'DB')),
        set(('UL', 'LF', 'RB', 'DL')),
        set(('UL', 'LF', 'RB', 'DR')),
        set(('UL', 'LF', 'RB', 'DF')),
        set(('UL', 'LF', 'RF', 'DB')),
        set(('UL', 'LF', 'RF', 'DL')),
        set(('UL', 'LF', 'RF', 'DR')),
        set(('UL', 'LF', 'RF', 'DF')),
        set(('UL', 'LF', 'DB', 'DL')),
        set(('UL', 'LF', 'DB', 'DR')),
        set(('UL', 'LF', 'DB', 'DF')),
        set(('UL', 'LF', 'DL', 'DR')),
        set(('UL', 'LF', 'DL', 'DF')),
        set(('UL', 'LF', 'DR', 'DF')),
        set(('UL', 'RB', 'RF', 'DB')),
        set(('UL', 'RB', 'RF', 'DL')),
        set(('UL', 'RB', 'RF', 'DR')),
        set(('UL', 'RB', 'RF', 'DF')),
        set(('UL', 'RB', 'DB', 'DL')),
        set(('UL', 'RB', 'DB', 'DR')),
        set(('UL', 'RB', 'DB', 'DF')),
        set(('UL', 'RB', 'DL', 'DR')),
        set(('UL', 'RB', 'DL', 'DF')),
        set(('UL', 'RB', 'DR', 'DF')),
        set(('UL', 'RF', 'DB', 'DL')),
        set(('UL', 'RF', 'DB', 'DR')),
        set(('UL', 'RF', 'DB', 'DF')),
        set(('UL', 'RF', 'DL', 'DR')),
        set(('UL', 'RF', 'DL', 'DF')),
        set(('UL', 'RF', 'DR', 'DF')),
        set(('UL', 'DB', 'DL', 'DR')),
        set(('UL', 'DB', 'DL', 'DF')),
        set(('UL', 'DB', 'DR', 'DF')),
        set(('UL', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF')),
        set(('UR', 'UF', 'LB', 'RB')),
        set(('UR', 'UF', 'LB', 'RF')),
        set(('UR', 'UF', 'LB', 'DB')),
        set(('UR', 'UF', 'LB', 'DL')),
        set(('UR', 'UF', 'LB', 'DR')),
        set(('UR', 'UF', 'LB', 'DF')),
        set(('UR', 'UF', 'LF', 'RB')),
        set(('UR', 'UF', 'LF', 'RF')),
        set(('UR', 'UF', 'LF', 'DB')),
        set(('UR', 'UF', 'LF', 'DL')),
        set(('UR', 'UF', 'LF', 'DR')),
        set(('UR', 'UF', 'LF', 'DF')),
        set(('UR', 'UF', 'RB', 'RF')),
        set(('UR', 'UF', 'RB', 'DB')),
        set(('UR', 'UF', 'RB', 'DL')),
        set(('UR', 'UF', 'RB', 'DR')),
        set(('UR', 'UF', 'RB', 'DF')),
        set(('UR', 'UF', 'RF', 'DB')),
        set(('UR', 'UF', 'RF', 'DL')),
        set(('UR', 'UF', 'RF', 'DR')),
        set(('UR', 'UF', 'RF', 'DF')),
        set(('UR', 'UF', 'DB', 'DL')),
        set(('UR', 'UF', 'DB', 'DR')),
        set(('UR', 'UF', 'DB', 'DF')),
        set(('UR', 'UF', 'DL', 'DR')),
        set(('UR', 'UF', 'DL', 'DF')),
        set(('UR', 'UF', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'RB')),
        set(('UR', 'LB', 'LF', 'RF')),
        set(('UR', 'LB', 'LF', 'DB')),
        set(('UR', 'LB', 'LF', 'DL')),
        set(('UR', 'LB', 'LF', 'DR')),
        set(('UR', 'LB', 'LF', 'DF')),
        set(('UR', 'LB', 'RB', 'RF')),
        set(('UR', 'LB', 'RB', 'DB')),
        set(('UR', 'LB', 'RB', 'DL')),
        set(('UR', 'LB', 'RB', 'DR')),
        set(('UR', 'LB', 'RB', 'DF')),
        set(('UR', 'LB', 'RF', 'DB')),
        set(('UR', 'LB', 'RF', 'DL')),
        set(('UR', 'LB', 'RF', 'DR')),
        set(('UR', 'LB', 'RF', 'DF')),
        set(('UR', 'LB', 'DB', 'DL')),
        set(('UR', 'LB', 'DB', 'DR')),
        set(('UR', 'LB', 'DB', 'DF')),
        set(('UR', 'LB', 'DL', 'DR')),
        set(('UR', 'LB', 'DL', 'DF')),
        set(('UR', 'LB', 'DR', 'DF')),
        set(('UR', 'LF', 'RB', 'RF')),
        set(('UR', 'LF', 'RB', 'DB')),
        set(('UR', 'LF', 'RB', 'DL')),
        set(('UR', 'LF', 'RB', 'DR')),
        set(('UR', 'LF', 'RB', 'DF')),
        set(('UR', 'LF', 'RF', 'DB')),
        set(('UR', 'LF', 'RF', 'DL')),
        set(('UR', 'LF', 'RF', 'DR')),
        set(('UR', 'LF', 'RF', 'DF')),
        set(('UR', 'LF', 'DB', 'DL')),
        set(('UR', 'LF', 'DB', 'DR')),
        set(('UR', 'LF', 'DB', 'DF')),
        set(('UR', 'LF', 'DL', 'DR')),
        set(('UR', 'LF', 'DL', 'DF')),
        set(('UR', 'LF', 'DR', 'DF')),
        set(('UR', 'RB', 'RF', 'DB')),
        set(('UR', 'RB', 'RF', 'DL')),
        set(('UR', 'RB', 'RF', 'DR')),
        set(('UR', 'RB', 'RF', 'DF')),
        set(('UR', 'RB', 'DB', 'DL')),
        set(('UR', 'RB', 'DB', 'DR')),
        set(('UR', 'RB', 'DB', 'DF')),
        set(('UR', 'RB', 'DL', 'DR')),
        set(('UR', 'RB', 'DL', 'DF')),
        set(('UR', 'RB', 'DR', 'DF')),
        set(('UR', 'RF', 'DB', 'DL')),
        set(('UR', 'RF', 'DB', 'DR')),
        set(('UR', 'RF', 'DB', 'DF')),
        set(('UR', 'RF', 'DL', 'DR')),
        set(('UR', 'RF', 'DL', 'DF')),
        set(('UR', 'RF', 'DR', 'DF')),
        set(('UR', 'DB', 'DL', 'DR')),
        set(('UR', 'DB', 'DL', 'DF')),
        set(('UR', 'DB', 'DR', 'DF')),
        set(('UR', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'RB')),
        set(('UF', 'LB', 'LF', 'RF')),
        set(('UF', 'LB', 'LF', 'DB')),
        set(('UF', 'LB', 'LF', 'DL')),
        set(('UF', 'LB', 'LF', 'DR')),
        set(('UF', 'LB', 'LF', 'DF')),
        set(('UF', 'LB', 'RB', 'RF')),
        set(('UF', 'LB', 'RB', 'DB')),
        set(('UF', 'LB', 'RB', 'DL')),
        set(('UF', 'LB', 'RB', 'DR')),
        set(('UF', 'LB', 'RB', 'DF')),
        set(('UF', 'LB', 'RF', 'DB')),
        set(('UF', 'LB', 'RF', 'DL')),
        set(('UF', 'LB', 'RF', 'DR')),
        set(('UF', 'LB', 'RF', 'DF')),
        set(('UF', 'LB', 'DB', 'DL')),
        set(('UF', 'LB', 'DB', 'DR')),
        set(('UF', 'LB', 'DB', 'DF')),
        set(('UF', 'LB', 'DL', 'DR')),
        set(('UF', 'LB', 'DL', 'DF')),
        set(('UF', 'LB', 'DR', 'DF')),
        set(('UF', 'LF', 'RB', 'RF')),
        set(('UF', 'LF', 'RB', 'DB')),
        set(('UF', 'LF', 'RB', 'DL')),
        set(('UF', 'LF', 'RB', 'DR')),
        set(('UF', 'LF', 'RB', 'DF')),
        set(('UF', 'LF', 'RF', 'DB')),
        set(('UF', 'LF', 'RF', 'DL')),
        set(('UF', 'LF', 'RF', 'DR')),
        set(('UF', 'LF', 'RF', 'DF')),
        set(('UF', 'LF', 'DB', 'DL')),
        set(('UF', 'LF', 'DB', 'DR')),
        set(('UF', 'LF', 'DB', 'DF')),
        set(('UF', 'LF', 'DL', 'DR')),
        set(('UF', 'LF', 'DL', 'DF')),
        set(('UF', 'LF', 'DR', 'DF')),
        set(('UF', 'RB', 'RF', 'DB')),
        set(('UF', 'RB', 'RF', 'DL')),
        set(('UF', 'RB', 'RF', 'DR')),
        set(('UF', 'RB', 'RF', 'DF')),
        set(('UF', 'RB', 'DB', 'DL')),
        set(('UF', 'RB', 'DB', 'DR')),
        set(('UF', 'RB', 'DB', 'DF')),
        set(('UF', 'RB', 'DL', 'DR')),
        set(('UF', 'RB', 'DL', 'DF')),
        set(('UF', 'RB', 'DR', 'DF')),
        set(('UF', 'RF', 'DB', 'DL')),
        set(('UF', 'RF', 'DB', 'DR')),
        set(('UF', 'RF', 'DB', 'DF')),
        set(('UF', 'RF', 'DL', 'DR')),
        set(('UF', 'RF', 'DL', 'DF')),
        set(('UF', 'RF', 'DR', 'DF')),
        set(('UF', 'DB', 'DL', 'DR')),
        set(('UF', 'DB', 'DL', 'DF')),
        set(('UF', 'DB', 'DR', 'DF')),
        set(('UF', 'DL', 'DR', 'DF')),
        set(('LB', 'LF', 'RB', 'RF')),
        set(('LB', 'LF', 'RB', 'DB')),
        set(('LB', 'LF', 'RB', 'DL')),
        set(('LB', 'LF', 'RB', 'DR')),
        set(('LB', 'LF', 'RB', 'DF')),
        set(('LB', 'LF', 'RF', 'DB')),
        set(('LB', 'LF', 'RF', 'DL')),
        set(('LB', 'LF', 'RF', 'DR')),
        set(('LB', 'LF', 'RF', 'DF')),
        set(('LB', 'LF', 'DB', 'DL')),
        set(('LB', 'LF', 'DB', 'DR')),
        set(('LB', 'LF', 'DB', 'DF')),
        set(('LB', 'LF', 'DL', 'DR')),
        set(('LB', 'LF', 'DL', 'DF')),
        set(('LB', 'LF', 'DR', 'DF')),
        set(('LB', 'RB', 'RF', 'DB')),
        set(('LB', 'RB', 'RF', 'DL')),
        set(('LB', 'RB', 'RF', 'DR')),
        set(('LB', 'RB', 'RF', 'DF')),
        set(('LB', 'RB', 'DB', 'DL')),
        set(('LB', 'RB', 'DB', 'DR')),
        set(('LB', 'RB', 'DB', 'DF')),
        set(('LB', 'RB', 'DL', 'DR')),
        set(('LB', 'RB', 'DL', 'DF')),
        set(('LB', 'RB', 'DR', 'DF')),
        set(('LB', 'RF', 'DB', 'DL')),
        set(('LB', 'RF', 'DB', 'DR')),
        set(('LB', 'RF', 'DB', 'DF')),
        set(('LB', 'RF', 'DL', 'DR')),
        set(('LB', 'RF', 'DL', 'DF')),
        set(('LB', 'RF', 'DR', 'DF')),
        set(('LB', 'DB', 'DL', 'DR')),
        set(('LB', 'DB', 'DL', 'DF')),
        set(('LB', 'DB', 'DR', 'DF')),
        set(('LB', 'DL', 'DR', 'DF')),
        set(('LF', 'RB', 'RF', 'DB')),
        set(('LF', 'RB', 'RF', 'DL')),
        set(('LF', 'RB', 'RF', 'DR')),
        set(('LF', 'RB', 'RF', 'DF')),
        set(('LF', 'RB', 'DB', 'DL')),
        set(('LF', 'RB', 'DB', 'DR')),
        set(('LF', 'RB', 'DB', 'DF')),
        set(('LF', 'RB', 'DL', 'DR')),
        set(('LF', 'RB', 'DL', 'DF')),
        set(('LF', 'RB', 'DR', 'DF')),
        set(('LF', 'RF', 'DB', 'DL')),
        set(('LF', 'RF', 'DB', 'DR')),
        set(('LF', 'RF', 'DB', 'DF')),
        set(('LF', 'RF', 'DL', 'DR')),
        set(('LF', 'RF', 'DL', 'DF')),
        set(('LF', 'RF', 'DR', 'DF')),
        set(('LF', 'DB', 'DL', 'DR')),
        set(('LF', 'DB', 'DL', 'DF')),
        set(('LF', 'DB', 'DR', 'DF')),
        set(('LF', 'DL', 'DR', 'DF')),
        set(('RB', 'RF', 'DB', 'DL')),
        set(('RB', 'RF', 'DB', 'DR')),
        set(('RB', 'RF', 'DB', 'DF')),
        set(('RB', 'RF', 'DL', 'DR')),
        set(('RB', 'RF', 'DL', 'DF')),
        set(('RB', 'RF', 'DR', 'DF')),
        set(('RB', 'DB', 'DL', 'DR')),
        set(('RB', 'DB', 'DL', 'DF')),
        set(('RB', 'DB', 'DR', 'DF')),
        set(('RB', 'DL', 'DR', 'DF')),
        set(('RF', 'DB', 'DL', 'DR')),
        set(('RF', 'DB', 'DL', 'DF')),
        set(('RF', 'DB', 'DR', 'DF')),
        set(('RF', 'DL', 'DR', 'DF')),
        set(('DB', 'DL', 'DR', 'DF')),
    ),
    6 : (
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'DB')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'DB')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'RF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'DB')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RF', 'DB')),
        set(('UB', 'UL', 'UR', 'UF', 'RF', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'RF', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'RF', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'DB')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'DL')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'RF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'DB')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'DL')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RF', 'DB')),
        set(('UB', 'UL', 'UR', 'LB', 'RF', 'DL')),
        set(('UB', 'UL', 'UR', 'LB', 'RF', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'RF', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'LB', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'RF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'DB')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'DL')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'DR')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RF', 'DB')),
        set(('UB', 'UL', 'UR', 'LF', 'RF', 'DL')),
        set(('UB', 'UL', 'UR', 'LF', 'RF', 'DR')),
        set(('UB', 'UL', 'UR', 'LF', 'RF', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'LF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'LF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'RB', 'RF', 'DB')),
        set(('UB', 'UL', 'UR', 'RB', 'RF', 'DL')),
        set(('UB', 'UL', 'UR', 'RB', 'RF', 'DR')),
        set(('UB', 'UL', 'UR', 'RB', 'RF', 'DF')),
        set(('UB', 'UL', 'UR', 'RB', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'RB', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'RB', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'RB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'RB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'RB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'DB')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'DL')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'RF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'DB')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'DL')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RF', 'DB')),
        set(('UB', 'UL', 'UF', 'LB', 'RF', 'DL')),
        set(('UB', 'UL', 'UF', 'LB', 'RF', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'RF', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'DB', 'DL')),
        set(('UB', 'UL', 'UF', 'LB', 'DB', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'DB', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'RF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'DB')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'DL')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'DR')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RF', 'DB')),
        set(('UB', 'UL', 'UF', 'LF', 'RF', 'DL')),
        set(('UB', 'UL', 'UF', 'LF', 'RF', 'DR')),
        set(('UB', 'UL', 'UF', 'LF', 'RF', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'DB', 'DL')),
        set(('UB', 'UL', 'UF', 'LF', 'DB', 'DR')),
        set(('UB', 'UL', 'UF', 'LF', 'DB', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LF', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'RB', 'RF', 'DB')),
        set(('UB', 'UL', 'UF', 'RB', 'RF', 'DL')),
        set(('UB', 'UL', 'UF', 'RB', 'RF', 'DR')),
        set(('UB', 'UL', 'UF', 'RB', 'RF', 'DF')),
        set(('UB', 'UL', 'UF', 'RB', 'DB', 'DL')),
        set(('UB', 'UL', 'UF', 'RB', 'DB', 'DR')),
        set(('UB', 'UL', 'UF', 'RB', 'DB', 'DF')),
        set(('UB', 'UL', 'UF', 'RB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'RB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'RB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UF', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UF', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UF', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'RF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'DB')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'DL')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'DR')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RF', 'DB')),
        set(('UB', 'UL', 'LB', 'LF', 'RF', 'DL')),
        set(('UB', 'UL', 'LB', 'LF', 'RF', 'DR')),
        set(('UB', 'UL', 'LB', 'LF', 'RF', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'DB', 'DL')),
        set(('UB', 'UL', 'LB', 'LF', 'DB', 'DR')),
        set(('UB', 'UL', 'LB', 'LF', 'DB', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'DL', 'DR')),
        set(('UB', 'UL', 'LB', 'LF', 'DL', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'RB', 'RF', 'DB')),
        set(('UB', 'UL', 'LB', 'RB', 'RF', 'DL')),
        set(('UB', 'UL', 'LB', 'RB', 'RF', 'DR')),
        set(('UB', 'UL', 'LB', 'RB', 'RF', 'DF')),
        set(('UB', 'UL', 'LB', 'RB', 'DB', 'DL')),
        set(('UB', 'UL', 'LB', 'RB', 'DB', 'DR')),
        set(('UB', 'UL', 'LB', 'RB', 'DB', 'DF')),
        set(('UB', 'UL', 'LB', 'RB', 'DL', 'DR')),
        set(('UB', 'UL', 'LB', 'RB', 'DL', 'DF')),
        set(('UB', 'UL', 'LB', 'RB', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'LB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'LB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'LB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'LB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'LB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'LB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'LB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LF', 'RB', 'RF', 'DB')),
        set(('UB', 'UL', 'LF', 'RB', 'RF', 'DL')),
        set(('UB', 'UL', 'LF', 'RB', 'RF', 'DR')),
        set(('UB', 'UL', 'LF', 'RB', 'RF', 'DF')),
        set(('UB', 'UL', 'LF', 'RB', 'DB', 'DL')),
        set(('UB', 'UL', 'LF', 'RB', 'DB', 'DR')),
        set(('UB', 'UL', 'LF', 'RB', 'DB', 'DF')),
        set(('UB', 'UL', 'LF', 'RB', 'DL', 'DR')),
        set(('UB', 'UL', 'LF', 'RB', 'DL', 'DF')),
        set(('UB', 'UL', 'LF', 'RB', 'DR', 'DF')),
        set(('UB', 'UL', 'LF', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'LF', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'LF', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'LF', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'LF', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'LF', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'LF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'LF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'LF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'LF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'DB')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'DL')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'RF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'DB')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'DL')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RF', 'DB')),
        set(('UB', 'UR', 'UF', 'LB', 'RF', 'DL')),
        set(('UB', 'UR', 'UF', 'LB', 'RF', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'RF', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'DB', 'DL')),
        set(('UB', 'UR', 'UF', 'LB', 'DB', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'DB', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'RF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'DB')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'DL')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'DR')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RF', 'DB')),
        set(('UB', 'UR', 'UF', 'LF', 'RF', 'DL')),
        set(('UB', 'UR', 'UF', 'LF', 'RF', 'DR')),
        set(('UB', 'UR', 'UF', 'LF', 'RF', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'DB', 'DL')),
        set(('UB', 'UR', 'UF', 'LF', 'DB', 'DR')),
        set(('UB', 'UR', 'UF', 'LF', 'DB', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LF', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'RB', 'RF', 'DB')),
        set(('UB', 'UR', 'UF', 'RB', 'RF', 'DL')),
        set(('UB', 'UR', 'UF', 'RB', 'RF', 'DR')),
        set(('UB', 'UR', 'UF', 'RB', 'RF', 'DF')),
        set(('UB', 'UR', 'UF', 'RB', 'DB', 'DL')),
        set(('UB', 'UR', 'UF', 'RB', 'DB', 'DR')),
        set(('UB', 'UR', 'UF', 'RB', 'DB', 'DF')),
        set(('UB', 'UR', 'UF', 'RB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'RB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'RB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'RF', 'DB', 'DL')),
        set(('UB', 'UR', 'UF', 'RF', 'DB', 'DR')),
        set(('UB', 'UR', 'UF', 'RF', 'DB', 'DF')),
        set(('UB', 'UR', 'UF', 'RF', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'RF', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'RF', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'RF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'DB')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'DL')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'DR')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RF', 'DB')),
        set(('UB', 'UR', 'LB', 'LF', 'RF', 'DL')),
        set(('UB', 'UR', 'LB', 'LF', 'RF', 'DR')),
        set(('UB', 'UR', 'LB', 'LF', 'RF', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'DB', 'DL')),
        set(('UB', 'UR', 'LB', 'LF', 'DB', 'DR')),
        set(('UB', 'UR', 'LB', 'LF', 'DB', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'DL', 'DR')),
        set(('UB', 'UR', 'LB', 'LF', 'DL', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'RB', 'RF', 'DB')),
        set(('UB', 'UR', 'LB', 'RB', 'RF', 'DL')),
        set(('UB', 'UR', 'LB', 'RB', 'RF', 'DR')),
        set(('UB', 'UR', 'LB', 'RB', 'RF', 'DF')),
        set(('UB', 'UR', 'LB', 'RB', 'DB', 'DL')),
        set(('UB', 'UR', 'LB', 'RB', 'DB', 'DR')),
        set(('UB', 'UR', 'LB', 'RB', 'DB', 'DF')),
        set(('UB', 'UR', 'LB', 'RB', 'DL', 'DR')),
        set(('UB', 'UR', 'LB', 'RB', 'DL', 'DF')),
        set(('UB', 'UR', 'LB', 'RB', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'RF', 'DB', 'DL')),
        set(('UB', 'UR', 'LB', 'RF', 'DB', 'DR')),
        set(('UB', 'UR', 'LB', 'RF', 'DB', 'DF')),
        set(('UB', 'UR', 'LB', 'RF', 'DL', 'DR')),
        set(('UB', 'UR', 'LB', 'RF', 'DL', 'DF')),
        set(('UB', 'UR', 'LB', 'RF', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'LB', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'LB', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LF', 'RB', 'RF', 'DB')),
        set(('UB', 'UR', 'LF', 'RB', 'RF', 'DL')),
        set(('UB', 'UR', 'LF', 'RB', 'RF', 'DR')),
        set(('UB', 'UR', 'LF', 'RB', 'RF', 'DF')),
        set(('UB', 'UR', 'LF', 'RB', 'DB', 'DL')),
        set(('UB', 'UR', 'LF', 'RB', 'DB', 'DR')),
        set(('UB', 'UR', 'LF', 'RB', 'DB', 'DF')),
        set(('UB', 'UR', 'LF', 'RB', 'DL', 'DR')),
        set(('UB', 'UR', 'LF', 'RB', 'DL', 'DF')),
        set(('UB', 'UR', 'LF', 'RB', 'DR', 'DF')),
        set(('UB', 'UR', 'LF', 'RF', 'DB', 'DL')),
        set(('UB', 'UR', 'LF', 'RF', 'DB', 'DR')),
        set(('UB', 'UR', 'LF', 'RF', 'DB', 'DF')),
        set(('UB', 'UR', 'LF', 'RF', 'DL', 'DR')),
        set(('UB', 'UR', 'LF', 'RF', 'DL', 'DF')),
        set(('UB', 'UR', 'LF', 'RF', 'DR', 'DF')),
        set(('UB', 'UR', 'LF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'LF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'LF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'LF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UR', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UR', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UR', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UR', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UR', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UR', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'RF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'DB')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'DL')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'DR')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RF', 'DB')),
        set(('UB', 'UF', 'LB', 'LF', 'RF', 'DL')),
        set(('UB', 'UF', 'LB', 'LF', 'RF', 'DR')),
        set(('UB', 'UF', 'LB', 'LF', 'RF', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'DB', 'DL')),
        set(('UB', 'UF', 'LB', 'LF', 'DB', 'DR')),
        set(('UB', 'UF', 'LB', 'LF', 'DB', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'DL', 'DR')),
        set(('UB', 'UF', 'LB', 'LF', 'DL', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'RB', 'RF', 'DB')),
        set(('UB', 'UF', 'LB', 'RB', 'RF', 'DL')),
        set(('UB', 'UF', 'LB', 'RB', 'RF', 'DR')),
        set(('UB', 'UF', 'LB', 'RB', 'RF', 'DF')),
        set(('UB', 'UF', 'LB', 'RB', 'DB', 'DL')),
        set(('UB', 'UF', 'LB', 'RB', 'DB', 'DR')),
        set(('UB', 'UF', 'LB', 'RB', 'DB', 'DF')),
        set(('UB', 'UF', 'LB', 'RB', 'DL', 'DR')),
        set(('UB', 'UF', 'LB', 'RB', 'DL', 'DF')),
        set(('UB', 'UF', 'LB', 'RB', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'RF', 'DB', 'DL')),
        set(('UB', 'UF', 'LB', 'RF', 'DB', 'DR')),
        set(('UB', 'UF', 'LB', 'RF', 'DB', 'DF')),
        set(('UB', 'UF', 'LB', 'RF', 'DL', 'DR')),
        set(('UB', 'UF', 'LB', 'RF', 'DL', 'DF')),
        set(('UB', 'UF', 'LB', 'RF', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'DB', 'DL', 'DR')),
        set(('UB', 'UF', 'LB', 'DB', 'DL', 'DF')),
        set(('UB', 'UF', 'LB', 'DB', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LF', 'RB', 'RF', 'DB')),
        set(('UB', 'UF', 'LF', 'RB', 'RF', 'DL')),
        set(('UB', 'UF', 'LF', 'RB', 'RF', 'DR')),
        set(('UB', 'UF', 'LF', 'RB', 'RF', 'DF')),
        set(('UB', 'UF', 'LF', 'RB', 'DB', 'DL')),
        set(('UB', 'UF', 'LF', 'RB', 'DB', 'DR')),
        set(('UB', 'UF', 'LF', 'RB', 'DB', 'DF')),
        set(('UB', 'UF', 'LF', 'RB', 'DL', 'DR')),
        set(('UB', 'UF', 'LF', 'RB', 'DL', 'DF')),
        set(('UB', 'UF', 'LF', 'RB', 'DR', 'DF')),
        set(('UB', 'UF', 'LF', 'RF', 'DB', 'DL')),
        set(('UB', 'UF', 'LF', 'RF', 'DB', 'DR')),
        set(('UB', 'UF', 'LF', 'RF', 'DB', 'DF')),
        set(('UB', 'UF', 'LF', 'RF', 'DL', 'DR')),
        set(('UB', 'UF', 'LF', 'RF', 'DL', 'DF')),
        set(('UB', 'UF', 'LF', 'RF', 'DR', 'DF')),
        set(('UB', 'UF', 'LF', 'DB', 'DL', 'DR')),
        set(('UB', 'UF', 'LF', 'DB', 'DL', 'DF')),
        set(('UB', 'UF', 'LF', 'DB', 'DR', 'DF')),
        set(('UB', 'UF', 'LF', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'RB', 'RF', 'DB')),
        set(('UB', 'LB', 'LF', 'RB', 'RF', 'DL')),
        set(('UB', 'LB', 'LF', 'RB', 'RF', 'DR')),
        set(('UB', 'LB', 'LF', 'RB', 'RF', 'DF')),
        set(('UB', 'LB', 'LF', 'RB', 'DB', 'DL')),
        set(('UB', 'LB', 'LF', 'RB', 'DB', 'DR')),
        set(('UB', 'LB', 'LF', 'RB', 'DB', 'DF')),
        set(('UB', 'LB', 'LF', 'RB', 'DL', 'DR')),
        set(('UB', 'LB', 'LF', 'RB', 'DL', 'DF')),
        set(('UB', 'LB', 'LF', 'RB', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'RF', 'DB', 'DL')),
        set(('UB', 'LB', 'LF', 'RF', 'DB', 'DR')),
        set(('UB', 'LB', 'LF', 'RF', 'DB', 'DF')),
        set(('UB', 'LB', 'LF', 'RF', 'DL', 'DR')),
        set(('UB', 'LB', 'LF', 'RF', 'DL', 'DF')),
        set(('UB', 'LB', 'LF', 'RF', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'DB', 'DL', 'DR')),
        set(('UB', 'LB', 'LF', 'DB', 'DL', 'DF')),
        set(('UB', 'LB', 'LF', 'DB', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'DL', 'DR', 'DF')),
        set(('UB', 'LB', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'LB', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'LB', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'LB', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'LB', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'LB', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'LB', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'LB', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'LB', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'LB', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'LB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'LB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'LB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'LB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'LB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'DB')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'DL')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'RF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'DB')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'DL')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RF', 'DB')),
        set(('UL', 'UR', 'UF', 'LB', 'RF', 'DL')),
        set(('UL', 'UR', 'UF', 'LB', 'RF', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'RF', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'DB', 'DL')),
        set(('UL', 'UR', 'UF', 'LB', 'DB', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'DB', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'RF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'DB')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'DL')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'DR')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RF', 'DB')),
        set(('UL', 'UR', 'UF', 'LF', 'RF', 'DL')),
        set(('UL', 'UR', 'UF', 'LF', 'RF', 'DR')),
        set(('UL', 'UR', 'UF', 'LF', 'RF', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'DB', 'DL')),
        set(('UL', 'UR', 'UF', 'LF', 'DB', 'DR')),
        set(('UL', 'UR', 'UF', 'LF', 'DB', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LF', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'RB', 'RF', 'DB')),
        set(('UL', 'UR', 'UF', 'RB', 'RF', 'DL')),
        set(('UL', 'UR', 'UF', 'RB', 'RF', 'DR')),
        set(('UL', 'UR', 'UF', 'RB', 'RF', 'DF')),
        set(('UL', 'UR', 'UF', 'RB', 'DB', 'DL')),
        set(('UL', 'UR', 'UF', 'RB', 'DB', 'DR')),
        set(('UL', 'UR', 'UF', 'RB', 'DB', 'DF')),
        set(('UL', 'UR', 'UF', 'RB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'RB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'RB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'RF', 'DB', 'DL')),
        set(('UL', 'UR', 'UF', 'RF', 'DB', 'DR')),
        set(('UL', 'UR', 'UF', 'RF', 'DB', 'DF')),
        set(('UL', 'UR', 'UF', 'RF', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'RF', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'RF', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'RF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'DB')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'DL')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'DR')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RF', 'DB')),
        set(('UL', 'UR', 'LB', 'LF', 'RF', 'DL')),
        set(('UL', 'UR', 'LB', 'LF', 'RF', 'DR')),
        set(('UL', 'UR', 'LB', 'LF', 'RF', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'DB', 'DL')),
        set(('UL', 'UR', 'LB', 'LF', 'DB', 'DR')),
        set(('UL', 'UR', 'LB', 'LF', 'DB', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'DL', 'DR')),
        set(('UL', 'UR', 'LB', 'LF', 'DL', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'RB', 'RF', 'DB')),
        set(('UL', 'UR', 'LB', 'RB', 'RF', 'DL')),
        set(('UL', 'UR', 'LB', 'RB', 'RF', 'DR')),
        set(('UL', 'UR', 'LB', 'RB', 'RF', 'DF')),
        set(('UL', 'UR', 'LB', 'RB', 'DB', 'DL')),
        set(('UL', 'UR', 'LB', 'RB', 'DB', 'DR')),
        set(('UL', 'UR', 'LB', 'RB', 'DB', 'DF')),
        set(('UL', 'UR', 'LB', 'RB', 'DL', 'DR')),
        set(('UL', 'UR', 'LB', 'RB', 'DL', 'DF')),
        set(('UL', 'UR', 'LB', 'RB', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'RF', 'DB', 'DL')),
        set(('UL', 'UR', 'LB', 'RF', 'DB', 'DR')),
        set(('UL', 'UR', 'LB', 'RF', 'DB', 'DF')),
        set(('UL', 'UR', 'LB', 'RF', 'DL', 'DR')),
        set(('UL', 'UR', 'LB', 'RF', 'DL', 'DF')),
        set(('UL', 'UR', 'LB', 'RF', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'LB', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'LB', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LF', 'RB', 'RF', 'DB')),
        set(('UL', 'UR', 'LF', 'RB', 'RF', 'DL')),
        set(('UL', 'UR', 'LF', 'RB', 'RF', 'DR')),
        set(('UL', 'UR', 'LF', 'RB', 'RF', 'DF')),
        set(('UL', 'UR', 'LF', 'RB', 'DB', 'DL')),
        set(('UL', 'UR', 'LF', 'RB', 'DB', 'DR')),
        set(('UL', 'UR', 'LF', 'RB', 'DB', 'DF')),
        set(('UL', 'UR', 'LF', 'RB', 'DL', 'DR')),
        set(('UL', 'UR', 'LF', 'RB', 'DL', 'DF')),
        set(('UL', 'UR', 'LF', 'RB', 'DR', 'DF')),
        set(('UL', 'UR', 'LF', 'RF', 'DB', 'DL')),
        set(('UL', 'UR', 'LF', 'RF', 'DB', 'DR')),
        set(('UL', 'UR', 'LF', 'RF', 'DB', 'DF')),
        set(('UL', 'UR', 'LF', 'RF', 'DL', 'DR')),
        set(('UL', 'UR', 'LF', 'RF', 'DL', 'DF')),
        set(('UL', 'UR', 'LF', 'RF', 'DR', 'DF')),
        set(('UL', 'UR', 'LF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'LF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'LF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'LF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'RB', 'RF', 'DB', 'DL')),
        set(('UL', 'UR', 'RB', 'RF', 'DB', 'DR')),
        set(('UL', 'UR', 'RB', 'RF', 'DB', 'DF')),
        set(('UL', 'UR', 'RB', 'RF', 'DL', 'DR')),
        set(('UL', 'UR', 'RB', 'RF', 'DL', 'DF')),
        set(('UL', 'UR', 'RB', 'RF', 'DR', 'DF')),
        set(('UL', 'UR', 'RB', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'RB', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'RB', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'RB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'RF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'DB')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'DL')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'DR')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RF', 'DB')),
        set(('UL', 'UF', 'LB', 'LF', 'RF', 'DL')),
        set(('UL', 'UF', 'LB', 'LF', 'RF', 'DR')),
        set(('UL', 'UF', 'LB', 'LF', 'RF', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'DB', 'DL')),
        set(('UL', 'UF', 'LB', 'LF', 'DB', 'DR')),
        set(('UL', 'UF', 'LB', 'LF', 'DB', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'DL', 'DR')),
        set(('UL', 'UF', 'LB', 'LF', 'DL', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'RB', 'RF', 'DB')),
        set(('UL', 'UF', 'LB', 'RB', 'RF', 'DL')),
        set(('UL', 'UF', 'LB', 'RB', 'RF', 'DR')),
        set(('UL', 'UF', 'LB', 'RB', 'RF', 'DF')),
        set(('UL', 'UF', 'LB', 'RB', 'DB', 'DL')),
        set(('UL', 'UF', 'LB', 'RB', 'DB', 'DR')),
        set(('UL', 'UF', 'LB', 'RB', 'DB', 'DF')),
        set(('UL', 'UF', 'LB', 'RB', 'DL', 'DR')),
        set(('UL', 'UF', 'LB', 'RB', 'DL', 'DF')),
        set(('UL', 'UF', 'LB', 'RB', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'RF', 'DB', 'DL')),
        set(('UL', 'UF', 'LB', 'RF', 'DB', 'DR')),
        set(('UL', 'UF', 'LB', 'RF', 'DB', 'DF')),
        set(('UL', 'UF', 'LB', 'RF', 'DL', 'DR')),
        set(('UL', 'UF', 'LB', 'RF', 'DL', 'DF')),
        set(('UL', 'UF', 'LB', 'RF', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'DB', 'DL', 'DR')),
        set(('UL', 'UF', 'LB', 'DB', 'DL', 'DF')),
        set(('UL', 'UF', 'LB', 'DB', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LF', 'RB', 'RF', 'DB')),
        set(('UL', 'UF', 'LF', 'RB', 'RF', 'DL')),
        set(('UL', 'UF', 'LF', 'RB', 'RF', 'DR')),
        set(('UL', 'UF', 'LF', 'RB', 'RF', 'DF')),
        set(('UL', 'UF', 'LF', 'RB', 'DB', 'DL')),
        set(('UL', 'UF', 'LF', 'RB', 'DB', 'DR')),
        set(('UL', 'UF', 'LF', 'RB', 'DB', 'DF')),
        set(('UL', 'UF', 'LF', 'RB', 'DL', 'DR')),
        set(('UL', 'UF', 'LF', 'RB', 'DL', 'DF')),
        set(('UL', 'UF', 'LF', 'RB', 'DR', 'DF')),
        set(('UL', 'UF', 'LF', 'RF', 'DB', 'DL')),
        set(('UL', 'UF', 'LF', 'RF', 'DB', 'DR')),
        set(('UL', 'UF', 'LF', 'RF', 'DB', 'DF')),
        set(('UL', 'UF', 'LF', 'RF', 'DL', 'DR')),
        set(('UL', 'UF', 'LF', 'RF', 'DL', 'DF')),
        set(('UL', 'UF', 'LF', 'RF', 'DR', 'DF')),
        set(('UL', 'UF', 'LF', 'DB', 'DL', 'DR')),
        set(('UL', 'UF', 'LF', 'DB', 'DL', 'DF')),
        set(('UL', 'UF', 'LF', 'DB', 'DR', 'DF')),
        set(('UL', 'UF', 'LF', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'RB', 'RF', 'DB', 'DL')),
        set(('UL', 'UF', 'RB', 'RF', 'DB', 'DR')),
        set(('UL', 'UF', 'RB', 'RF', 'DB', 'DF')),
        set(('UL', 'UF', 'RB', 'RF', 'DL', 'DR')),
        set(('UL', 'UF', 'RB', 'RF', 'DL', 'DF')),
        set(('UL', 'UF', 'RB', 'RF', 'DR', 'DF')),
        set(('UL', 'UF', 'RB', 'DB', 'DL', 'DR')),
        set(('UL', 'UF', 'RB', 'DB', 'DL', 'DF')),
        set(('UL', 'UF', 'RB', 'DB', 'DR', 'DF')),
        set(('UL', 'UF', 'RB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UF', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UF', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UF', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'RB', 'RF', 'DB')),
        set(('UL', 'LB', 'LF', 'RB', 'RF', 'DL')),
        set(('UL', 'LB', 'LF', 'RB', 'RF', 'DR')),
        set(('UL', 'LB', 'LF', 'RB', 'RF', 'DF')),
        set(('UL', 'LB', 'LF', 'RB', 'DB', 'DL')),
        set(('UL', 'LB', 'LF', 'RB', 'DB', 'DR')),
        set(('UL', 'LB', 'LF', 'RB', 'DB', 'DF')),
        set(('UL', 'LB', 'LF', 'RB', 'DL', 'DR')),
        set(('UL', 'LB', 'LF', 'RB', 'DL', 'DF')),
        set(('UL', 'LB', 'LF', 'RB', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'RF', 'DB', 'DL')),
        set(('UL', 'LB', 'LF', 'RF', 'DB', 'DR')),
        set(('UL', 'LB', 'LF', 'RF', 'DB', 'DF')),
        set(('UL', 'LB', 'LF', 'RF', 'DL', 'DR')),
        set(('UL', 'LB', 'LF', 'RF', 'DL', 'DF')),
        set(('UL', 'LB', 'LF', 'RF', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'DB', 'DL', 'DR')),
        set(('UL', 'LB', 'LF', 'DB', 'DL', 'DF')),
        set(('UL', 'LB', 'LF', 'DB', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'DL', 'DR', 'DF')),
        set(('UL', 'LB', 'RB', 'RF', 'DB', 'DL')),
        set(('UL', 'LB', 'RB', 'RF', 'DB', 'DR')),
        set(('UL', 'LB', 'RB', 'RF', 'DB', 'DF')),
        set(('UL', 'LB', 'RB', 'RF', 'DL', 'DR')),
        set(('UL', 'LB', 'RB', 'RF', 'DL', 'DF')),
        set(('UL', 'LB', 'RB', 'RF', 'DR', 'DF')),
        set(('UL', 'LB', 'RB', 'DB', 'DL', 'DR')),
        set(('UL', 'LB', 'RB', 'DB', 'DL', 'DF')),
        set(('UL', 'LB', 'RB', 'DB', 'DR', 'DF')),
        set(('UL', 'LB', 'RB', 'DL', 'DR', 'DF')),
        set(('UL', 'LB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'LB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'LB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'LB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'LB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UL', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UL', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UL', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UL', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UL', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UL', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UL', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UL', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UL', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UL', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'RF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'DB')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'DL')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'DR')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RF', 'DB')),
        set(('UR', 'UF', 'LB', 'LF', 'RF', 'DL')),
        set(('UR', 'UF', 'LB', 'LF', 'RF', 'DR')),
        set(('UR', 'UF', 'LB', 'LF', 'RF', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'DB', 'DL')),
        set(('UR', 'UF', 'LB', 'LF', 'DB', 'DR')),
        set(('UR', 'UF', 'LB', 'LF', 'DB', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'DL', 'DR')),
        set(('UR', 'UF', 'LB', 'LF', 'DL', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'RB', 'RF', 'DB')),
        set(('UR', 'UF', 'LB', 'RB', 'RF', 'DL')),
        set(('UR', 'UF', 'LB', 'RB', 'RF', 'DR')),
        set(('UR', 'UF', 'LB', 'RB', 'RF', 'DF')),
        set(('UR', 'UF', 'LB', 'RB', 'DB', 'DL')),
        set(('UR', 'UF', 'LB', 'RB', 'DB', 'DR')),
        set(('UR', 'UF', 'LB', 'RB', 'DB', 'DF')),
        set(('UR', 'UF', 'LB', 'RB', 'DL', 'DR')),
        set(('UR', 'UF', 'LB', 'RB', 'DL', 'DF')),
        set(('UR', 'UF', 'LB', 'RB', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'RF', 'DB', 'DL')),
        set(('UR', 'UF', 'LB', 'RF', 'DB', 'DR')),
        set(('UR', 'UF', 'LB', 'RF', 'DB', 'DF')),
        set(('UR', 'UF', 'LB', 'RF', 'DL', 'DR')),
        set(('UR', 'UF', 'LB', 'RF', 'DL', 'DF')),
        set(('UR', 'UF', 'LB', 'RF', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'DB', 'DL', 'DR')),
        set(('UR', 'UF', 'LB', 'DB', 'DL', 'DF')),
        set(('UR', 'UF', 'LB', 'DB', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LF', 'RB', 'RF', 'DB')),
        set(('UR', 'UF', 'LF', 'RB', 'RF', 'DL')),
        set(('UR', 'UF', 'LF', 'RB', 'RF', 'DR')),
        set(('UR', 'UF', 'LF', 'RB', 'RF', 'DF')),
        set(('UR', 'UF', 'LF', 'RB', 'DB', 'DL')),
        set(('UR', 'UF', 'LF', 'RB', 'DB', 'DR')),
        set(('UR', 'UF', 'LF', 'RB', 'DB', 'DF')),
        set(('UR', 'UF', 'LF', 'RB', 'DL', 'DR')),
        set(('UR', 'UF', 'LF', 'RB', 'DL', 'DF')),
        set(('UR', 'UF', 'LF', 'RB', 'DR', 'DF')),
        set(('UR', 'UF', 'LF', 'RF', 'DB', 'DL')),
        set(('UR', 'UF', 'LF', 'RF', 'DB', 'DR')),
        set(('UR', 'UF', 'LF', 'RF', 'DB', 'DF')),
        set(('UR', 'UF', 'LF', 'RF', 'DL', 'DR')),
        set(('UR', 'UF', 'LF', 'RF', 'DL', 'DF')),
        set(('UR', 'UF', 'LF', 'RF', 'DR', 'DF')),
        set(('UR', 'UF', 'LF', 'DB', 'DL', 'DR')),
        set(('UR', 'UF', 'LF', 'DB', 'DL', 'DF')),
        set(('UR', 'UF', 'LF', 'DB', 'DR', 'DF')),
        set(('UR', 'UF', 'LF', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'RB', 'RF', 'DB', 'DL')),
        set(('UR', 'UF', 'RB', 'RF', 'DB', 'DR')),
        set(('UR', 'UF', 'RB', 'RF', 'DB', 'DF')),
        set(('UR', 'UF', 'RB', 'RF', 'DL', 'DR')),
        set(('UR', 'UF', 'RB', 'RF', 'DL', 'DF')),
        set(('UR', 'UF', 'RB', 'RF', 'DR', 'DF')),
        set(('UR', 'UF', 'RB', 'DB', 'DL', 'DR')),
        set(('UR', 'UF', 'RB', 'DB', 'DL', 'DF')),
        set(('UR', 'UF', 'RB', 'DB', 'DR', 'DF')),
        set(('UR', 'UF', 'RB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'RF', 'DB', 'DL', 'DR')),
        set(('UR', 'UF', 'RF', 'DB', 'DL', 'DF')),
        set(('UR', 'UF', 'RF', 'DB', 'DR', 'DF')),
        set(('UR', 'UF', 'RF', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'RB', 'RF', 'DB')),
        set(('UR', 'LB', 'LF', 'RB', 'RF', 'DL')),
        set(('UR', 'LB', 'LF', 'RB', 'RF', 'DR')),
        set(('UR', 'LB', 'LF', 'RB', 'RF', 'DF')),
        set(('UR', 'LB', 'LF', 'RB', 'DB', 'DL')),
        set(('UR', 'LB', 'LF', 'RB', 'DB', 'DR')),
        set(('UR', 'LB', 'LF', 'RB', 'DB', 'DF')),
        set(('UR', 'LB', 'LF', 'RB', 'DL', 'DR')),
        set(('UR', 'LB', 'LF', 'RB', 'DL', 'DF')),
        set(('UR', 'LB', 'LF', 'RB', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'RF', 'DB', 'DL')),
        set(('UR', 'LB', 'LF', 'RF', 'DB', 'DR')),
        set(('UR', 'LB', 'LF', 'RF', 'DB', 'DF')),
        set(('UR', 'LB', 'LF', 'RF', 'DL', 'DR')),
        set(('UR', 'LB', 'LF', 'RF', 'DL', 'DF')),
        set(('UR', 'LB', 'LF', 'RF', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'DB', 'DL', 'DR')),
        set(('UR', 'LB', 'LF', 'DB', 'DL', 'DF')),
        set(('UR', 'LB', 'LF', 'DB', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'DL', 'DR', 'DF')),
        set(('UR', 'LB', 'RB', 'RF', 'DB', 'DL')),
        set(('UR', 'LB', 'RB', 'RF', 'DB', 'DR')),
        set(('UR', 'LB', 'RB', 'RF', 'DB', 'DF')),
        set(('UR', 'LB', 'RB', 'RF', 'DL', 'DR')),
        set(('UR', 'LB', 'RB', 'RF', 'DL', 'DF')),
        set(('UR', 'LB', 'RB', 'RF', 'DR', 'DF')),
        set(('UR', 'LB', 'RB', 'DB', 'DL', 'DR')),
        set(('UR', 'LB', 'RB', 'DB', 'DL', 'DF')),
        set(('UR', 'LB', 'RB', 'DB', 'DR', 'DF')),
        set(('UR', 'LB', 'RB', 'DL', 'DR', 'DF')),
        set(('UR', 'LB', 'RF', 'DB', 'DL', 'DR')),
        set(('UR', 'LB', 'RF', 'DB', 'DL', 'DF')),
        set(('UR', 'LB', 'RF', 'DB', 'DR', 'DF')),
        set(('UR', 'LB', 'RF', 'DL', 'DR', 'DF')),
        set(('UR', 'LB', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UR', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UR', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UR', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UR', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UR', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UR', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UR', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UR', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UR', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UR', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UR', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UR', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UR', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UR', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UR', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UR', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UR', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UR', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'RB', 'RF', 'DB')),
        set(('UF', 'LB', 'LF', 'RB', 'RF', 'DL')),
        set(('UF', 'LB', 'LF', 'RB', 'RF', 'DR')),
        set(('UF', 'LB', 'LF', 'RB', 'RF', 'DF')),
        set(('UF', 'LB', 'LF', 'RB', 'DB', 'DL')),
        set(('UF', 'LB', 'LF', 'RB', 'DB', 'DR')),
        set(('UF', 'LB', 'LF', 'RB', 'DB', 'DF')),
        set(('UF', 'LB', 'LF', 'RB', 'DL', 'DR')),
        set(('UF', 'LB', 'LF', 'RB', 'DL', 'DF')),
        set(('UF', 'LB', 'LF', 'RB', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'RF', 'DB', 'DL')),
        set(('UF', 'LB', 'LF', 'RF', 'DB', 'DR')),
        set(('UF', 'LB', 'LF', 'RF', 'DB', 'DF')),
        set(('UF', 'LB', 'LF', 'RF', 'DL', 'DR')),
        set(('UF', 'LB', 'LF', 'RF', 'DL', 'DF')),
        set(('UF', 'LB', 'LF', 'RF', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'DB', 'DL', 'DR')),
        set(('UF', 'LB', 'LF', 'DB', 'DL', 'DF')),
        set(('UF', 'LB', 'LF', 'DB', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'RB', 'RF', 'DB', 'DL')),
        set(('UF', 'LB', 'RB', 'RF', 'DB', 'DR')),
        set(('UF', 'LB', 'RB', 'RF', 'DB', 'DF')),
        set(('UF', 'LB', 'RB', 'RF', 'DL', 'DR')),
        set(('UF', 'LB', 'RB', 'RF', 'DL', 'DF')),
        set(('UF', 'LB', 'RB', 'RF', 'DR', 'DF')),
        set(('UF', 'LB', 'RB', 'DB', 'DL', 'DR')),
        set(('UF', 'LB', 'RB', 'DB', 'DL', 'DF')),
        set(('UF', 'LB', 'RB', 'DB', 'DR', 'DF')),
        set(('UF', 'LB', 'RB', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'RF', 'DB', 'DL', 'DR')),
        set(('UF', 'LB', 'RF', 'DB', 'DL', 'DF')),
        set(('UF', 'LB', 'RF', 'DB', 'DR', 'DF')),
        set(('UF', 'LB', 'RF', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'DB', 'DL', 'DR', 'DF')),
        set(('UF', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UF', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UF', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UF', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UF', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UF', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UF', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UF', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UF', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UF', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UF', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UF', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UF', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UF', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UF', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('LB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('LB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('LB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('LB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('LB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('LB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('LB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('LB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('LB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('LB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('LB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('LB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('LB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('LB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('LB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('LB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('LB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('LB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('LB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('LB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('LB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
    ),
    8 : (
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DL')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'DB', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'DB', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'LB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'LB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'LB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RF', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RF', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RF', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'LB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'LB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'LB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UF', 'LB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UF', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UF', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'LB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'LB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'LB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UF', 'LB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UF', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UF', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UR', 'UF', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
    ),
    10: (
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'UF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UR', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UL', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UB', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'LF', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LB', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'UF', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UR', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UL', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
        set(('UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),
    ),
    12 : (set(('UB', 'UL', 'UR', 'UF', 'LB', 'LF', 'RB', 'RF', 'DB', 'DL', 'DR', 'DF')),)
}


# Code below here is no longer used...saving it for a rainy day
'''
    def find_moves_to_reach_state(self, wing_to_move, target_face_side):
        """
        This was used to build the lookup_table_444_last_two_edges_place_F_east, etc lookup tables
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        orig_f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
        orig_f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
        orig_f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
        orig_f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])

        orig_r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
        orig_r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])
        orig_r_east_top = self.get_wing_value(self.sideR.edge_east_pos[0])
        orig_r_east_bottom = self.get_wing_value(self.sideR.edge_east_pos[1])

        orig_b_west_top = self.get_wing_value(self.sideB.edge_west_pos[0])
        orig_b_west_bottom = self.get_wing_value(self.sideB.edge_west_pos[1])
        orig_b_east_top = self.get_wing_value(self.sideB.edge_east_pos[0])
        orig_b_east_bottom = self.get_wing_value(self.sideB.edge_east_pos[1])

        orig_l_west_top = self.get_wing_value(self.sideL.edge_west_pos[0])
        orig_l_west_bottom = self.get_wing_value(self.sideL.edge_west_pos[1])
        orig_l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
        orig_l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])

        orig_center_corner_state = self.get_center_corner_state()
        wing_to_move_value = sorted(self.get_wing_value(wing_to_move))

        filename = 'utils/all_3x3x3_moves_6_deep.txt'
        with open(filename, 'r') as fh:
            self.print_cube()
            count = 0
            for line in fh:
                count += 1
                steps = line.strip().split()

                for step in steps:
                    self.rotate(step)

                if count % 10000 == 0:
                    log.info("count %d, step len %d" % (count, len(steps)))

                # For SLICE-FORWARD
                if target_face_side == 'F-east':
                    # Find sequence that moves wing_to_move to (40, 53)
                    # F-west must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])

                    f_east_top = sorted(self.get_wing_value(self.sideF.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        f_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'R-east':
                    # Find sequence that moves wing_to_move to (56, 69)
                    # F-west and R-west must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
                    r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
                    r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])

                    r_east_top = sorted(self.get_wing_value(self.sideR.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        r_west_top == orig_r_west_top and
                        r_west_bottom == orig_r_west_bottom and
                        r_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'B-east':
                    # Find sequence that moves wing_to_move to (21, 72)
                    # F-west, R-west, and B-west edges must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
                    r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
                    r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])
                    b_west_top = self.get_wing_value(self.sideB.edge_west_pos[0])
                    b_west_bottom = self.get_wing_value(self.sideB.edge_west_pos[1])

                    b_east_top = sorted(self.get_wing_value(self.sideB.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        r_west_top == orig_r_west_top and
                        r_west_bottom == orig_r_west_bottom and
                        b_west_top == orig_b_west_top and
                        b_west_bottom == orig_b_west_bottom and
                        b_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                # For SLICE-BACK
                elif target_face_side == 'F-west':
                    # Find sequence that moves wing_to_move to (24, 37)
                    # F-east must not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    f_west_top = sorted(self.get_wing_value(self.sideF.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        f_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'L-west':
                    # Find sequence that moves wing_to_move to (21, 72)
                    # F-east and L-east ust not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])
                    l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
                    l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    l_west_top = sorted(self.get_wing_value(self.sideL.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        l_east_top == orig_l_east_top and
                        l_east_bottom == orig_l_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        l_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'B-west':
                    # Find sequence that moves wing_to_move to (56, 69)
                    # F-east, L-east and B-east must not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])
                    l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
                    l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])
                    b_east_top = self.get_wing_value(self.sideB.edge_east_pos[0])
                    b_east_bottom = self.get_wing_value(self.sideB.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    b_west_top = sorted(self.get_wing_value(self.sideB.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        l_east_top == orig_l_east_top and
                        l_east_bottom == orig_l_east_bottom and
                        b_east_top == orig_b_east_top and
                        b_east_bottom == orig_b_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        b_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                else:
                    raise ImplementThis("target_face_side %s" % target_face_side)

                self.state = original_state[:]
                self.solution = original_solution[:]

                if found_solution:
                    log.warning("solution to move %s to %s is %s" % (wing_to_move, target_face_side, ' '.join(steps)))
                    sys.exit(1)

            log.warning("Explored %d moves in %s but did not find a solution" % (count, filename))
            sys.exit(1)

lookup_table_444_sister_wing_to_R_east = {
    (2, 67)  : "B'", # U-north
    (3, 66)  : "R' U R", # U-north
    (5, 18)  : "L' B2 L", # U-west
    (9, 19)  : "U B'", # U-west
    (14, 34) : "R' U' R", # U-south
    (15, 35) : "U2 B'", # U-south
    (8, 51)  : "U' B'", # U-east
    (12, 50) : "F R F'", # U-east
    (21, 72) : "B R D' R'", # L-west
    (25, 76) : "B2", # L-west
    (37, 24) : None, # L-east
    #(41, 28) : "", # L-east
    #(40, 53) : "", # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "D", # R-east
    (60, 73) : "B R' U R", # R-east
    (46, 82) : "D2 B", # D-north
    (47, 83) : "R D R'", # D-north
    (30, 89) : "D' B", # D-west
    (31, 85) : "L B2 L'", # D-west
    (78, 95) : "B", # D-south
    (79, 94) : "R D' R'", # D-south
    (62, 88) : "D B", # D-east
    (63, 92) : "D B", # D-east
}

lookup_table_444_sister_wing_to_B_east = {
    (2, 67)  : "L U' L'", # U-north
    (3, 66)  : "R B R'", # U-north
    (5, 18)  : "B' U B", # U-west
    (9, 19)  : "F L' F'", # U-west
    (14, 34) : "B' U2 B", # U-south
    (15, 35) : "L U L'", # U-south
    (8, 51)  : "L U2 L'", # U-east
    (12, 50) : "B' U' B", # U-east
    (21, 72) : "D", # L-west
    (25, 76) : "B L' D B' L", # L-west
    (37, 24) : None, # L-east
    #(41, 28) : "", # L-east
    #(40, 53) : "", # R-west
    (44, 57) : None, # R-west
    #(56, 69) : "", # R-east
    #(60, 73) : "", # R-east
    (46, 82) : "L' D' L", # D-north
    (47, 83) : "B D2 B'", # D-north
    (30, 89) : "F L F'", # D-west
    (31, 85) : "B D' B'", # D-west
    (78, 95) : "L' D L", # D-south
    (79, 94) : "R B' R'", # D-south
    (62, 88) : "L' D2 L", # D-east
    (63, 92) : "B D B'", # D-east
}

lookup_table_444_sister_wing_to_F_west = {
    (2, 67)  : "F U2 F'", # U-north
    (3, 66)  : "L' U' L", # U-north
    (5, 18)  : "L F L' F'", # U-west
    (9, 19)  : "F U' F'", # U-west
    (14, 34) : "L' U L", # U-south
    (15, 35) : "F' L F L'", # U-south
    (8, 51)  : "F U F'", # U-east
    (12, 50) : "L' U2 L", # U-east
    (21, 72) : "B L D B' L'", # L-west
    (25, 76) : "B L2 B' L2", # L-west
    (37, 24) : "D", # L-east
    (41, 28) : "F L' U F' L", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "L2 B2 L2 B2", # R-east
    (60, 73) : "B L' U' B' L", # R-east
    (46, 82) : "D F' D' F", # D-north
    (47, 83) : "L D' L'", # D-north
    (30, 89) : "F' D F", # D-west
    (31, 85) : "D L D' L'", # D-west
    (78, 95) : "F' D2 F", # D-south
    (79, 94) : "L D L'", # D-south
    (62, 88) : "F' D' F", # D-east
    (63, 92) : "L D2 L'", # D-east
}

lookup_table_444_sister_wing_to_L_west = {
    (2, 67)  : "L U' L'", # U-north
    (3, 66)  : "B L B' L'", # U-north
    (5, 18)  : "B' U B", # U-west
    (9, 19)  : "L' B L B'", # U-west
    (14, 34) : "B' U2 B", # U-south
    (15, 35) : "L U L'", # U-south
    (8, 51)  : "L U2 L'", # U-east
    (12, 50) : "B' U' B", # U-east
    (21, 72) : "D", # L-west
    (25, 76) : "B L' D B' L", # L-west
    #(37, 24) : "", # L-east
    #(41, 28) : "", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "B L U' B' L'", # R-east
    (60, 73) : "B2 L B2 L'", # R-east
    (46, 82) : "L' D' L", # D-north
    (47, 83) : "B D2 B'", # D-north
    (30, 89) : "D L' D' L", # D-west
    (31, 85) : "B D' B'", # D-west
    (78, 95) : "L' D L", # D-south
    (79, 94) : "B' L B L'", # D-south
    (62, 88) : "L' D2 L", # D-east
    (63, 92) : "B D B'", # D-east
}

lookup_table_444_sister_wing_to_B_west = {
    (2, 67)  : "B' R B R'", # U-north
    (3, 66)  : "R' U R", # U-north
    (5, 18)  : "R' U2 R", # U-west
    (9, 19)  : "B U B'", # U-west
    (14, 34) : "R' U' R", # U-south
    (15, 35) : "B U2 B'", # U-south
    (8, 51)  : "B U' B'", # U-east
    (12, 50) : "R B R' B'", # U-east
    #(21, 72) : "", # L-west
    #(25, 76) : "", # L-west
    #(37, 24) : "", # L-east
    #(41, 28) : "", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "D", # R-east
    (60, 73) : "B R' U B' R", # R-east
    (46, 82) : "B' D2 B", # D-north
    (47, 83) : "R D R'", # D-north
    (30, 89) : "B' D' B", # D-west
    (31, 85) : "R D2 R'", # D-west
    (78, 95) : "B R B' R'", # D-south
    (79, 94) : "R D' R'", # D-south
    (62, 88) : "B' D B", # D-east
    (63, 92) : "D R D' R'", # D-east
}


Used to build the 12 self.lt_tsai_phase2 state_target strings

table1
======
 UD
DxxU
UxxD
 DU

 DU
DLLU
ULLD
 UD

 DU
UFFD
DFFU
 UD

 DU
DRRU
URRD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDLLUULLDUDDUUFFDDFFUUDDUDRRUURRDUDDUUFFDDFFUUDUDDxxUUxxDDU


table2
======
 UD
DxxU
UxxD
 DU

 DU
DRRU
URRD
 UD

 DU
UFFD
DFFU
 UD

 DU
DLLU
ULLD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDRRUURRDUDDUUFFDDFFUUDDUDLLUULLDUDDUUFFDDFFUUDUDDxxUUxxDDU


table3
======
 UD
DxxU
UxxD
 DU

 DU
DLLU
URRD
 UD

 DU
UFFD
DFFU
 UD

 DU
DRRU
ULLD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDLLUURRDUDDUUFFDDFFUUDDUDRRUULLDUDDUUFFDDFFUUDUDDxxUUxxDDU


table4
======
 UD
DxxU
UxxD
 DU

 DU
DLLU
URRD
 UD

 DU
UFFD
DFFU
 UD

 DU
DLLU
URRD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDLLUURRDUDDUUFFDDFFUUDDUDLLUURRDUDDUUFFDDFFUUDUDDxxUUxxDDU


table5
======
 UD
DxxU
UxxD
 DU

 DU
DRRU
ULLD
 UD

 DU
UFFD
DFFU
 UD

 DU
DRRU
ULLD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDRRUULLDUDDUUFFDDFFUUDDUDRRUULLDUDDUUFFDDFFUUDUDDxxUUxxDDU



table6
======
 UD
DxxU
UxxD
 DU

 DU
DRRU
ULLD
 UD

 DU
UFFD
DFFU
 UD

 DU
DLLU
URRD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDRRUULLDUDDUUFFDDFFUUDDUDLLUURRDUDDUUFFDDFFUUDUDDxxUUxxDDU


table7
======
 UD
DxxU
UxxD
 DU

 DU
DRLU
URLD
 UD

 DU
UFFD
DFFU
 UD

 DU
DRLU
URLD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDRLUURLDUDDUUFFDDFFUUDDUDRLUURLDUDDUUFFDDFFUUDUDDxxUUxxDDU


table8
======
 UD
DxxU
UxxD
 DU

 DU
DRLU
URLD
 UD

 DU
UFFD
DFFU
 UD

 DU
DLRU
ULRD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDRLUURLDUDDUUFFDDFFUUDDUDLRUULRDUDDUUFFDDFFUUDUDDxxUUxxDDU


table9
======
 UD
DxxU
UxxD
 DU

 DU
DLRU
ULRD
 UD

 DU
UFFD
DFFU
 UD

 DU
DRLU
URLD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDLRUULRDUDDUUFFDDFFUUDDUDRLUURLDUDDUUFFDDFFUUDUDDxxUUxxDDU


table10
======
 UD
DxxU
UxxD
 DU

 DU
DLRU
ULRD
 UD

 DU
UFFD
DFFU
 UD

 DU
DLRU
ULRD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDLRUULRDUDDUUFFDDFFUUDDUDLRUULRDUDDUUFFDDFFUUDUDDxxUUxxDDU


table11
======
 UD
DxxU
UxxD
 DU

 DU
DRLU
ULRD
 UD

 DU
UFFD
DFFU
 UD

 DU
DLRU
URLD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDRLUULRDUDDUUFFDDFFUUDDUDLRUURLDUDDUUFFDDFFUUDUDDxxUUxxDDU


table12
======
 UD
DxxU
UxxD
 DU

 DU
DLRU
URLD
 UD

 DU
UFFD
DFFU
 UD

 DU
DRLU
ULRD
 UD

 DU
UFFD
DFFU
 UD

 UD
DxxU
UxxD
 DU

UDDxxUUxxDDUDUDLRUURLDUDDUUFFDDFFUUDDUDRLUULRDUDDUUFFDDFFUUDUDDxxUUxxDDU
'''
