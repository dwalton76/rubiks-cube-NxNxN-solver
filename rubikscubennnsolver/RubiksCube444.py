
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA, NoSteps
from subprocess import check_output
from pprint import pformat
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
    """
    4x4x4 strategy
    phase 1 - stage all centers
    phase 2 - orient edges into high/low groups and solve LR centers to one of 12 positions
    phase 3 - solve all centers and pair all edges
    """

    def __init__(self, state, order, colormap=None, avoid_pll=True, debug=False, use_tsai=False):
        RubiksCube.__init__(self, state, order, colormap, debug)
        self.avoid_pll = avoid_pll
        self.use_tsai = use_tsai

        if debug:
            log.setLevel(logging.DEBUG)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # There are three "modes" we can run in:
        # --ev3   : Uses the least CPU but produces a longer solution.
        #           This will stage UD centers first, then LFRB centers.
        #
        # --tsai  : Uses the most CPU but produces the shortest solution
        #           This will stage all centers at once.
        #
        # default : Uses a middle ground of CPU and produces not the shortest or longest solution.
        #           This will stage all centers at once.

        # ==============
        # Phase 1 tables
        # ==============
        # All three modes use self.lt_UD_centers_stage
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
        self.lt_UD_centers_stage = LookupTable(self,
                                               'lookup-table-4x4x4-step11-UD-centers-stage.txt',
                                               '444-UD-centers-stage',
                                               'f0000f',
                                                True, # state hex
                                                linecount=735471)

        # --tsai and default use the step10, step12 and step13 tables
        if self.use_tsai or not self.ev3:
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

        # only --ev3 uses the step20 table
        elif self.ev3:
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

        else:
            raise Exception("We should not be here")

        # ==============
        # Phase 2 tables
        # ==============
        if self.use_tsai:
            '''
            lookup-table-4x4x4-step61-orient-edges.txt
            ===========================================
            1 steps has 3 entries (0 percent, 0.00x previous step)
            2 steps has 29 entries (0 percent, 9.67x previous step)
            3 steps has 278 entries (0 percent, 9.59x previous step)
            4 steps has 1,934 entries (0 percent, 6.96x previous step)
            5 steps has 15,640 entries (0 percent, 8.09x previous step)
            6 steps has 124,249 entries (4 percent, 7.94x previous step)
            7 steps has 609,241 entries (22 percent, 4.90x previous step)
            8 steps has 1,224,098 entries (45 percent, 2.01x previous step)
            9 steps has 688,124 entries (25 percent, 0.56x previous step)
            10 steps has 40,560 entries (1 percent, 0.06x previous step)

            Total: 2,704,156 entries
            '''
            self.lt_orient_edges = LookupTable(self,
                                               'lookup-table-4x4x4-step61-orient-edges.txt',
                                               '444-orient-edges-tsai',
                                               'UDDUUDDUDUDUUDUDDUUDDUUDDUDUUDUDDUUDDUUDUDDUUDDU',
                                               False, # state hex
                                               linecount=2704156)

            '''
            lookup-table-4x4x4-step62-LR-centers-table1.txt
            ===============================================
            1 steps has 22 entries (31 percent, 0.00x previous step)
            2 steps has 16 entries (22 percent, 0.73x previous step)
            3 steps has 16 entries (22 percent, 1.00x previous step)
            4 steps has 16 entries (22 percent, 1.00x previous step)

            Total: 70 entries
            '''
            self.lt_LR_centers_solve = LookupTable(self,
                                                   'lookup-table-4x4x4-step62-LR-centers.txt',
                                                   '444-LR-centers-solve-tsai',
                                                   ('xxxxLLLLxxxxRRRRxxxxxxxx', ),
                                                    False, # state hex
                                                    linecount=70)

            '''
            lookup-table-4x4x4-step60-phase2-tsai.txt
            ==========================================
            1 steps has 36 entries (0 percent, 0.00x previous step)
            2 steps has 348 entries (0 percent, 9.67x previous step)
            3 steps has 3,416 entries (0 percent, 9.82x previous step)
            4 steps has 26,260 entries (1 percent, 7.69x previous step)
            5 steps has 226,852 entries (9 percent, 8.64x previous step)
            6 steps has 2,048,086 entries (88 percent, 9.03x previous step)

            Total: 2,304,998 entries

            See the bottom of this file for notes on how the 12 state_target
            strings were constructed
            '''
            self.lt_phase2_tsai = LookupTableIDA(self,
                                                 'lookup-table-4x4x4-step60-phase2-tsai.txt',
                                                 '444-phase2-tsai',
                                                 ('UDDxxUUxxDDUDUDLLUULLDUDDUUFFDDFFUUDDUDRRUURRDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDRRUURRDUDDUUFFDDFFUUDDUDLLUULLDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDLLUURRDUDDUUFFDDFFUUDDUDRRUULLDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDLLUURRDUDDUUFFDDFFUUDDUDLLUURRDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDRRUULLDUDDUUFFDDFFUUDDUDRRUULLDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDRRUULLDUDDUUFFDDFFUUDDUDLLUURRDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDRLUURLDUDDUUFFDDFFUUDDUDRLUURLDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDRLUURLDUDDUUFFDDFFUUDDUDLRUULRDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDLRUULRDUDDUUFFDDFFUUDDUDRLUURLDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDLRUULRDUDDUUFFDDFFUUDDUDLRUULRDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDRLUULRDUDDUUFFDDFFUUDDUDLRUURLDUDDUUFFDDFFUUDUDDxxUUxxDDU',
                                                  'UDDxxUUxxDDUDUDLRUURLDUDDUUFFDDFFUUDDUDRLUULRDUDDUUFFDDFFUUDUDDxxUUxxDDU'),
                                                 False, # state_hex
                                                 moves_4x4x4,
                                                 ("Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'", "Rw", "Rw'", "Lw", "Lw'"), # illegal_moves

                                                 # prune tables
                                                 (self.lt_orient_edges,
                                                  self.lt_LR_centers_solve),
                                                 linecount=2304998)

            # Phase 3
            '''
            lookup-table-4x4x4-step71-phase3-edges-tsai.txt
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


            lookup-table-4x4x4-step71-phase3-edges-tsai.txt
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
            self.lt_phase3_tsai_edges_solve = LookupTable(self,
                                                          'lookup-table-4x4x4-step71-phase3-edges-tsai.txt',
                                                          '444-phase3-edges',
                                                          '0123456789ab',
                                                          False, # state hex
                                                          linecount=14999140)

            '''
            lookup-table-4x4x4-step72-phase3-centers-tsai.txt
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
            self.lt_phase3_tsai_centers_solve = LookupTable(self,
                                                          'lookup-table-4x4x4-step72-phase3-centers-tsai.txt',
                                                          '444-ULFRBD-centers-solve',
                                                          'UUUULLLLFFFFRRRRBBBBDDDD',
                                                          False, # state hex
                                                          linecount=58800)

            '''
            If you build this to 8-deep it adds 119,166,578 which makes it too big to
            check into the repo

            lookup-table-4x4x4-step70-phase3-tsai.txt
            ==========================================
            1 steps has 7 entries (0 percent, 0.00x previous step)
            2 steps has 83 entries (0 percent, 11.86x previous step)
            3 steps has 960 entries (0 percent, 11.57x previous step)
            4 steps has 10,303 entries (0 percent, 10.73x previous step)
            5 steps has 107,474 entries (0 percent, 10.43x previous step)
            6 steps has 1,124,149 entries (8 percent, 10.46x previous step)
            7 steps has 11,660,818 entries (90 percent, 10.37x previous step)

            Total: 12,903,794 entries
            '''
            self.lt_phase3_tsai = LookupTableIDA(self,
                                                 'lookup-table-4x4x4-step70-phase3-tsai.txt',
                                                 '444-phase3-tsai',
                                                 '001UU21UU233114LL54LL599335FF65FF688226RR76RR7aa007BB47BB4bb889DDa9DDabb',
                                                 False, # state_hex
                                                 moves_4x4x4,
                                                 ("Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",
                                                  "Rw", "Rw'", "Lw", "Lw'", "R", "R'", "L", "L'"), # illegal_moves

                                                 # prune tables
                                                 (self.lt_phase3_tsai_edges_solve,
                                                  self.lt_phase3_tsai_centers_solve),
                                                 linecount=12903794)
            lt_phase3_tsai_heuristic_stats_min = {
                (1, 2) : 4,
                (2, 1) : 5,
                (3, 1) : 7,
                (5, 1) : 6,
                (5, 7) : 9,
                (6, 1) : 12,
                (6, 2) : 9,
                (6, 7) : 9,
                (6, 8) : 10,
                (7, 1) : 13,
                (7, 7) : 9,
                (7, 8) : 10,
                (8, 2) : 13,
                (8, 3) : 11,
                (8, 4) : 9,
                (8, 6) : 9,
                (8, 7) : 9,
                (8, 8) : 10,
                (9, 3) : 12,
                (9, 4) : 10,
                (9, 5) : 10,
                (9, 7) : 10,
                (9, 8) : 11,
                (10, 3) : 13,
                (10, 4) : 12,
                (10, 6) : 11,
                (10, 7) : 11,
                (10, 8) : 11,
                (10, 9) : 12,
                (11, 3) : 14,
                (11, 4) : 12,
                (11, 6) : 13,
                (11, 7) : 12,
                (11, 8) : 13,
                (11, 9) : 14,
                (12, 3) : 16,
                (12, 4) : 14,
                (12, 5) : 14,
                (12, 6) : 14,
                (12, 7) : 14,
                (12, 8) : 15,
                (12, 9) : 19,
                (13, 4) : 16,
                (13, 8) : 17,
            }

            lt_phase3_tsai_heuristic_stats_median = {
                (1, 2) : 4,
                (2, 1) : 7,
                (2, 3) : 4,
                (2, 5) : 6,
                (3, 1) : 7,
                (3, 4) : 5,
                (3, 5) : 6,
                (4, 1) : 6,
                (4, 2) : 5,
                (4, 3) : 5,
                (4, 4) : 7,
                (4, 5) : 7,
                (4, 6) : 7,
                (5, 1) : 8,
                (5, 2) : 6,
                (5, 3) : 6,
                (5, 4) : 7,
                (5, 5) : 8,
                (5, 6) : 9,
                (5, 7) : 10,
                (6, 1) : 12,
                (6, 2) : 10,
                (6, 3) : 9,
                (6, 4) : 9,
                (6, 5) : 9,
                (6, 6) : 10,
                (6, 7) : 10,
                (6, 8) : 11,
                (7, 1) : 13,
                (7, 3) : 11,
                (7, 4) : 11,
                (7, 5) : 11,
                (7, 6) : 11,
                (7, 7) : 11,
                (7, 8) : 12,
                (8, 2) : 13,
                (8, 3) : 13,
                (8, 4) : 12,
                (8, 5) : 12,
                (8, 6) : 12,
                (8, 7) : 12,
                (8, 8) : 12,
                (9, 3) : 13,
                (9, 4) : 13,
                (9, 5) : 13,
                (9, 6) : 13,
                (9, 7) : 13,
                (9, 8) : 13,
                (10, 3) : 15,
                (10, 4) : 14,
                (10, 5) : 14,
                (10, 6) : 14,
                (10, 7) : 14,
                (10, 8) : 15,
                (10, 9) : 15,
                (11, 3) : 16,
                (11, 4) : 15,
                (11, 5) : 16,
                (11, 6) : 15,
                (11, 7) : 16,
                (11, 8) : 16,
                (11, 9) : 15,
                (12, 3) : 16,
                (12, 4) : 16,
                (12, 5) : 16,
                (12, 6) : 16,
                (12, 7) : 17,
                (12, 8) : 16,
                (12, 9) : 19,
                (13, 4) : 16,
                (13, 8) : 17,
            }
            #self.lt_phase3_tsai.heuristic_stats = lt_phase3_tsai_heuristic_stats_min
            self.lt_phase3_tsai.heuristic_stats = lt_phase3_tsai_heuristic_stats_median

        else:

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

        self.orient_edges = {
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

    def group_centers_guts(self):
        self.lt_init()

        # If the centers are already solve then return and let group_edges() pair the edges
        if self.centers_solved():
            self.solution.append('CENTERS_SOLVED')
            return

        # Made some pics to try to explain lookup tables on facebook
        #
        #self.print_cube()
        #for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
        #    for square in side.edge_pos:
        #        self.state[square] = 'x'
        #    for square in side.corner_pos:
        #        self.state[square] = 'x'
        #self.print_cube()

        # The tsai will solve the centers and pair the edges
        if self.use_tsai:

            self.lt_ULFRBD_centers_stage.solve()
            self.print_cube()
            log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

            # Testing the phase2 prune tables
            #self.lt_orient_edges.solve()
            #self.lt_LR_centers_solve.solve()
            #self.print_cube()
            #sys.exit(0)

            log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_phase2_tsai.solve()
            self.print_cube()
            log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

            # Testing the phase3 prune tables
            #self.lt_phase3_tsai_edges_solve.solve()
            #self.lt_phase3_tsai_centers_solve.solve()
            #self.print_cube()
            #sys.exit(0)

            log.info("%s: Start of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_phase3_tsai.avoid_oll = True
            self.lt_phase3_tsai.avoid_pll = True
            self.lt_phase3_tsai.solve()
            self.print_cube()
            log.info("%s: End of Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

        # The non-tsai solver will only solve the centers here
        else:
            if self.ev3:
                self.lt_UD_centers_stage.solve()
                self.rotate_for_best_centers_staging()
                self.lt_LFRB_centers_stage.solve()
            else:
                self.lt_ULFRBD_centers_stage.avoid_oll = True
                self.lt_ULFRBD_centers_stage.solve()

            self.print_cube()
            log.info("%s: End of Phase1, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

            log.info("%s: Start of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.rotate_for_best_centers_solving()
            self.lt_ULFRBD_centers_solve.solve()
            self.print_cube()
            log.info("%s: End of Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            log.info("")

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
        #self.verify_all_centers_solved()

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

        if self.ev3:
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
'''


'''
Used to build the 12 self.lt_phase2_tsai state_target strings

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
