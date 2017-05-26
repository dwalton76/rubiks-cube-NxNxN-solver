
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis
from rubikscubennnsolver.RubiksSide import Side, SolveError
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, moves_4x4x4, solved_4x4x4
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA, NoSteps
import logging
import math
import os
import random
import re
import subprocess
import sys

log = logging.getLogger(__name__)

moves_5x5x5 = moves_4x4x4
solved_5x5x5 = 'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB'


class RubiksCube555(RubiksCube):
    """
    5x5x5 strategy
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

        self.lt_UD_T_centers_stage = None

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # Use big tables
        if os.path.exists('lookup-table-5x5x5-step11-UD-T-centers-stage.txt'):

            '''
            There are 4 T-centers and 4 X-centers so (24!/(8! * 16!))^2 is 540,917,591,841
            We cannot build a table that large so we will build it 7 moves deep and use
            IDA with T-centers and X-centers as our prune tables. Both the T-centers and
            X-centers prune tables will have 735,471 entries, 735,471/540,917,591,841
            is 0.0000013596729171 which is a decent percentage for IDA.

            lookup-table-5x5x5-step10-UD-centers-stage.txt
            ==============================================
            1 steps has 5 entries (0 percent)
            2 steps has 98 entries (0 percent)
            3 steps has 2,036 entries (0 percent)
            4 steps has 41,096 entries (0 percent)
            5 steps has 824,950 entries (0 percent)
            6 steps has 16,300,291 entries (4 percent)
            7 steps has 311,709,304 entries (94 percent)

            Total: 328,877,780 entries


            lookup-table-5x5x5-step11-UD-T-centers-stage.txt
            ================================================
            T-centers - 24!/(16! * 8!) is 735,471

            1 steps has 5 entries (0 percent)
            2 steps has 66 entries (0 percent)
            3 steps has 900 entries (0 percent)
            4 steps has 9,626 entries (1 percent)
            5 steps has 80,202 entries (10 percent)
            6 steps has 329,202 entries (44 percent)
            7 steps has 302,146 entries (41 percent)
            8 steps has 13,324 entries (1 percent)

            Total: 735,471 entries


            lookup-table-5x5x5-step12-UD-X-centers-stage.txt
            ================================================
            X-centers - 24!/(16! * 8!) is 735,471

            1 steps has 5 entries (0 percent)
            2 steps has 82 entries (0 percent)
            3 steps has 1,206 entries (0 percent)
            4 steps has 14,116 entries (1 percent)
            5 steps has 123,404 entries (16 percent)
            6 steps has 422,508 entries (57 percent)
            7 steps has 173,254 entries (23 percent)
            8 steps has 896 entries (0 percent)

            Total: 735,471 entries
            '''
            self.lt_UD_T_centers_stage = LookupTable(self,
                                                     'lookup-table-5x5x5-step11-UD-T-centers-stage.txt',
                                                     'UD-T-centers-stage',
                                                     None,
                                                     False) # state_hex

            self.lt_UD_X_centers_stage = LookupTable(self,
                                                     'lookup-table-5x5x5-step12-UD-X-centers-stage.txt',
                                                     'UD-X-centers-stage',
                                                     None,
                                                     False) # state_hex

            self.lt_UD_centers_stage = LookupTableIDA(self,
                                                     'lookup-table-5x5x5-step10-UD-centers-stage.txt',
                                                     'UD-centers-stage',
                                                     '3fe000000001ff', # UUUUUUUUUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxUUUUUUUUU
                                                     True, # state_hex
                                                     moves_5x5x5,
                                                     (), # illegal_moves

                                                     # prune tables
                                                     (self.lt_UD_T_centers_stage,
                                                      self.lt_UD_X_centers_stage))


            '''
            Stage LR centers to sides L or R, this will automagically stage
            the F and B centers to sides F or B. 4 T-centers and 4 X-centers
            on 4 sides (ignore U and D since they are solved) but we treat
            L and R as one color so 8! on the bottom.
            (16!/(8! * 8!)))^2 is 165,636,900

            lookup-table-5x5x5-step20-LR-centers-stage.txt
            ==============================================
            1 steps has 3 entries (0 percent)
            2 steps has 33 entries (0 percent)
            3 steps has 374 entries (0 percent)
            4 steps has 3,838 entries (0 percent)
            5 steps has 39,254 entries (0 percent)
            6 steps has 387,357 entries (0 percent)
            7 steps has 3,374,380 entries (2 percent)
            8 steps has 20,851,334 entries (12 percent)
            9 steps has 65,556,972 entries (39 percent)
            10 steps has 66,986,957 entries (40 percent)
            11 steps has 8,423,610 entries (5 percent)
            12 steps has 12,788 entries (0 percent)

            Total: 165,636,900 entries
            '''
            self.lt_LR_centers_stage = LookupTable(self,
                                                   'lookup-table-5x5x5-step20-LR-centers-stage.txt',
                                                   'LR-centers-stage',
                                                   'ff803fe00', # LLLLLLLLLxxxxxxxxxLLLLLLLLLxxxxxxxxx
                                                   True) # state_hex

            '''
            The centers are all staged so there are (8!/(4! * 4!))^6 or 117,649,000,000
            permutations to solve the centers. This is too large for us to build so use
            IDA and build the table 8 steps deep. A table to solve only the UDLR sides
            will be our prune table.

            lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt
            ==================================================
            1 steps has 7 entries (0 percent)
            2 steps has 99 entries (0 percent)
            3 steps has 1,134 entries (0 percent)
            4 steps has 12,183 entries (0 percent)
            5 steps has 128,730 entries (0 percent)
            6 steps has 1,291,295 entries (1 percent)
            7 steps has 12,250,688 entries (10 percent)
            8 steps has 106,661,150 entries (88 percent)

            Total: 120,345,286 entries


            Our UDLR prune table is (8!/(4! * 4!))^4 or 24,010,000
            24,010,000/117,649,000,000 is 0.0002040816326531 which is a very good percentage
            for IDA, the search should be very fast

            lookup-table-5x5x5-step31-UDLR-centers-solve.txt
            ================================================
            1 steps has 7 entries (0 percent)
            2 steps has 71 entries (0 percent)
            3 steps has 630 entries (0 percent)
            4 steps has 4,639 entries (0 percent)
            5 steps has 32,060 entries (0 percent)
            6 steps has 198,779 entries (0 percent)
            7 steps has 1,011,284 entries (4 percent)
            8 steps has 3,826,966 entries (15 percent)
            9 steps has 8,611,512 entries (35 percent)
            10 steps has 8,194,244 entries (34 percent)
            11 steps has 2,062,640 entries (8 percent)
            12 steps has 67,152 entries (0 percent)
            13 steps has 16 entries (0 percent)

            Total: 24,010,000 entries
            '''
            self.lt_UDLR_centers_solve = LookupTable(self,
                                                     'lookup-table-5x5x5-step31-UDLR-centers-solve.txt',
                                                     'UDLR-centers-solve',
                                                     'TBD',
                                                     False) # state_hex

            self.lt_ULFRB_centers_solve = LookupTableIDA(self,
                                                        'lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt',
                                                        'ULFRBD-centers-solve',
                                                        'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD',
                                                        False, # state_hex
                                                        moves_5x5x5,

                                                        # These moves would destroy the staged centers
                                                        ("Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'"),

                                                        # prune tables
                                                        (self.lt_UDLR_centers_solve, ))

        # Use small tables
        # This isn't working yet, the lookup-table-5x5x5-step40-UD-centers-stage-to-UFDB.txt table doesn't work
        else:
            self.lt_UD_centers_stage_to_UFDB = LookupTable(self,
                                                           'lookup-table-5x5x5-step40-UD-centers-stage-to-UFDB.txt',
                                                           'UD-centers-on-LR',
                                                           '00000',
                                                           True) # state_hex

            self.lt_UD_centers_stage_from_UFDB_x_center_only = LookupTable(self,
                                                           'lookup-table-5x5x5-step51-UD-centers-stage-from-UFDB-x-center-only.txt',
                                                           'UD-centers-on-UFDB-x-center-only',
                                                           'aa802aa00',
                                                           True) # state_hex

            self.lt_UD_centers_stage_from_UFDB_t_center_only = LookupTable(self,
                                                           'lookup-table-5x5x5-step52-UD-centers-stage-from-UFDB-t-center-only.txt',
                                                           'UD-centers-on-UFDB-t-center-only',
                                                           'TBD',
                                                           True) # state_hex

            self.lt_UD_centers_stage_from_UFDB = LookupTableIDA(self,
                                                        'lookup-table-5x5x5-step50-UD-centers-stage-from-UFDB.txt',
                                                        'UD-centers-on-UFDB',
                                                        'TBD',
                                                        True, # state_hex
                                                        moves_5x5x5,

                                                        # do not move back to LR
                                                        ("Uw", "Uw'", "Dw", "Dw'", "Fw", "Fw'", "Bw", "Bw'"),

                                                        # prune tables
                                                        (self.lt_UD_centers_stage_from_UFDB_x_center_only,
                                                         self.lt_UD_centers_stage_from_UFDB_t_center_only))


        '''
        lookup-table-5x5x5-step90-edges-slice-forward.txt
        =================================================
        1 steps has 7 entries (0 percent)
        2 steps has 42 entries (0 percent)
        3 steps has 299 entries (3 percent)
        4 steps has 1306 entries (16 percent)
        5 steps has 3449 entries (43 percent)
        6 steps has 2617 entries (33 percent)
        7 steps has 200 entries (2 percent)

        Total: 7920 entries
        '''
        self.lt_edge_slice_forward = LookupTable(self,
                                                 'lookup-table-5x5x5-step90-edges-slice-forward.txt',
                                                 '555-edges-slice-forward',
                                                 None)

        '''
        lookup-table-5x5x5-step91-edges-slice-backward.txt
        ==================================================
        1 steps has 1 entries (0 percent)
        3 steps has 36 entries (0 percent)
        4 steps has 66 entries (0 percent)
        5 steps has 334 entries (4 percent)
        6 steps has 1369 entries (17 percent)
        7 steps has 3505 entries (44 percent)
        8 steps has 2539 entries (32 percent)
        9 steps has 69 entries (0 percent)

        Total: 7919 entries
        '''
        self.lt_edge_slice_backward = LookupTable(self,
                                                  'lookup-table-5x5x5-step91-edges-slice-backward.txt',
                                                  '555-edges-slice-backward',
                                                  None)

        '''
        lookup-table-5x5x5-step92-edges-stage-last-four.txt
        ===================================================
        1 steps has 5 entries (1 percent, 0.00x previous step)
        2 steps has 50 entries (10 percent, 10.00x previous step)
        3 steps has 286 entries (57 percent, 5.72x previous step)
        4 steps has 152 entries (30 percent, 0.53x previous step)
        5 steps has 2 entries (0 percent, 0.01x previous step)

        Total: 495 entries

        lookup-table-5x5x5-step93-edges-solve-last-four.txt
        ===================================================
        5 steps has 4 entries (0 percent, 0.00x previous step)
        6 steps has 95 entries (0 percent, 23.75x previous step)
        7 steps has 398 entries (1 percent, 4.19x previous step)
        8 steps has 1217 entries (5 percent, 3.06x previous step)
        9 steps has 4778 entries (19 percent, 3.93x previous step)
        10 steps has 17436 entries (72 percent, 3.65x previous step)

        Total: 23928 entries
        '''
        self.lt_edges_stage_last_four = LookupTable(self,
                                                    'lookup-table-5x5x5-step92-edges-stage-last-four.txt',
                                                    '555-edges-stage-last-four',
                                                    'xxxxxxxxxxxxxxxLLLLLLxxxxxxLLLLLLxxxxxxLLLLLLxxxxxxLLLLLLxxxxxxxxxxxxxxx')

        self.lt_edges_solve_last_four = LookupTable(self,
                                                    'lookup-table-5x5x5-step93-edges-solve-last-four.txt',
                                                    '555-edges-solve-last-four',
                                                    'TBD')


    def group_centers_guts(self):
        self.lt_init()
        self.rotate_U_to_U()

        # Use big tables
        if self.lt_UD_T_centers_stage:
            self.lt_UD_centers_stage.solve()
            log.info("Took %d steps to stage UD centers" % len(self.solution))

            self.lt_LR_centers_stage.solve()
            log.info("Took %d steps to stage ULFRBD centers" % len(self.solution))

            self.lt_ULFRB_centers_solve.solve()
            log.info("Took %d steps to solve ULFRBD centers" % len(self.solution))


        # Use small tables
        else:
            self.lt_UD_centers_stage_to_UFDB.solve()

            log.info("HERE 10")
            self.print_cube()
            #self.print_solution()
            #sys.exit(0)

            self.lt_UD_centers_stage_from_UFDB_x_center_only.solve()
            log.info("HERE 20")
            self.print_cube()
            self.print_solution()

            self.lt_UD_centers_stage_from_UFDB_t_center_only.solve()
            self.print_cube()
            sys.exit(0)

            self.lt_UD_centers_stage_from_UFDB.solve()

    def pair_last_four_edges_555(self, edge):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        # rotate unpaired edge to F-west
        self.rotate_edge_to_F_west(edge)

        try:
            self.lt_edges_stage_last_four.solve()
            self.lt_edges_solve_last_four.solve()
            raise Exception("inspect this one...it worked :)")
        except NoSteps as e:
            # raise e

            # restore cube state
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        # experiment with rotating around...it didn't help (didn't think it would)
        '''
        for x in range(6):
            try:
                self.lt_edges_stage_last_four.solve()
                self.lt_edges_solve_last_four.solve()
                raise Exception("inspect this one")
                break
            except NoSteps as e:
                if x == 3:
                    self.rotate_x()
                    self.rotate_x()
                else:
                    self.rotate_y()
        else:
            raise e
            # restore cube state
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False
        '''

        current_solution_len = self.get_solution_len_minus_rotates(self.solution)
        current_non_paired_wings_count = self.get_non_paired_wings_count()

        log.info("pair_last_four_edges_555() paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count:
            raise SolveError("Failed to pair last four edges")

        return True

    def find_moves_to_stage_slice_forward_555(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_forward.steps(state)


    def find_moves_to_stage_slice_backward_555(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_backward.steps(state)

    def get_sister_wings_slice_backward_555(self):
        results = (None, None, None, None)
        max_pair_on_slice_back = 0

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        # Work with the wing at the bottom of the F-east edge
        # Move the sister wing to F-west
        target_wing = (self.sideF.edge_east_pos[-1], self.sideR.edge_west_pos[-1])

        # Do we need to reverse sister_wing1?
        for sister_wing1_reverse in (True, False):
            sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0])

            if sister_wing1_reverse:
                sister_wing1 = tuple(list(reversed(sister_wing1)))
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])
            sister_wing2 = None
            sister_wing3 = None
            #log.info("sister_wing1 %s on %s" % (pformat(sister_wing1), sister_wing1_side))

            neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])
            sister_wing1_neighbor = neighbors[0]

            for sister_wing2_reverse in (True, False):
                sister_wing2 = self.get_wing_in_middle_of_edge(sister_wing1_neighbor)

                if sister_wing2_reverse:
                    sister_wing2 = tuple(list(reversed(sister_wing2)))
                sister_wing2_side = self.get_side_for_index(sister_wing2[0])

                neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])
                sister_wing2_neighbor = neighbors[0]

                for sister_wing3_reverse in (True, False):
                    sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor)

                    if sister_wing3_reverse:
                        sister_wing3 = tuple(list(reversed(sister_wing3)))

                    steps = self.find_moves_to_stage_slice_backward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

                    if steps:
                        pre_non_paired_edges_count = self.get_non_paired_edges_count()
                        for step in steps:
                            self.rotate(step)
                        # 3Uw' Uw
                        self.rotate("Uw")
                        self.rotate("Dw'")
                        self.rotate_y_reverse()
                        post_non_paired_edges_count = self.get_non_paired_edges_count()

                        # F-east must pair
                        if self.state[70] == self.state[65] and self.state[91] == self.state[86]:
                            will_pair_on_slice_count = pre_non_paired_edges_count - post_non_paired_edges_count
                        else:
                            will_pair_on_slice_count = 0

                        # log.info("get_sister_wings_slice_backward_555() will_pair_on_slice_count %d via %s" %
                        #    (will_pair_on_slice_count, ' '.join(steps)))

                        # restore cube state
                        self.state = copy(original_state)
                        self.solution = copy(original_solution)

                        if will_pair_on_slice_count > max_pair_on_slice_back:
                            results = (target_wing, sister_wing1, sister_wing2, sister_wing3)
                            max_pair_on_slice_back = will_pair_on_slice_count

        # log.info("max_pair_on_slice_back is %d" % max_pair_on_slice_back)
        return results

    def prep_for_slice_back_555(self):

        (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

        if target_wing is None:

            # experiment
            '''
            # save cube state
            original_state = copy(self.state)
            original_solution = copy(self.solution)

            if target_wing is None and not self.sideU.north_edge_paired():
                self.rotate("R")
                self.rotate("U")
                self.rotate("R'")

                (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

                if target_wing is None:
                    # restore cube state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

            if target_wing is None and not self.sideU.south_edge_paired():
                self.rotate("R")
                self.rotate("U'")
                self.rotate("R'")

                (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

                if target_wing is None:
                    # restore cube state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

            if target_wing is None and not self.sideU.west_edge_paired():
                self.rotate("R")
                self.rotate("U2")
                self.rotate("R'")

                (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

                if target_wing is None:
                    # restore cube state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

            if target_wing is None and not self.sideU.east_edge_paired():
                self.rotate("U'")
                self.rotate("R")
                self.rotate("U")
                self.rotate("R'")

                (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

                if target_wing is None:
                    # restore cube state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

            if target_wing is None and not self.sideD.north_edge_paired():
                self.rotate("R'")
                self.rotate("D")
                self.rotate("R")

                (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

                if target_wing is None:
                    # restore cube state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

            if target_wing is None and not self.sideD.south_edge_paired():
                self.rotate("R'")
                self.rotate("D'")
                self.rotate("R")

                (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

                if target_wing is None:
                    # restore cube state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

            if target_wing is None and not self.sideD.west_edge_paired():
                self.rotate("R'")
                self.rotate("D2")
                self.rotate("R")

                (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

                if target_wing is None:
                    # restore cube state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

            if target_wing is None and not self.sideD.east_edge_paired():
                self.rotate("D'")
                self.rotate("R'")
                self.rotate("D")
                self.rotate("R")

                (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

                if target_wing is None:
                    # restore cube state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

            #if target_wing:
            #    raise SolveError("it worked")
            '''

            # This is not a cube where we can place three edges to be paired on the slice back :(

            # Uncomment this if you want to try out putting any three unpaired
            # edges in place for the slice back. This doesn't work very well
            # though because you end up spending moves to put edges in place that
            # aren't paired on the slice back...so the three you paired on the
            # slice forward end up having a really have move count.
            #
            # Put any three unpaired edges in place
            '''
            target_wing = (self.sideF.edge_east_pos[-1], self.sideR.edge_west_pos[-1])

            for wing in self.get_non_paired_wings():
                if wing == target_wing:
                    continue

                wing_side = self.get_side_for_index(wing[0][0])

                if wing_side.wing_is_middle_of_edge(wing[0][0]):
                    if sister_wing1 is None:
                        sister_wing1 = wing[0]
                    elif sister_wing2 is None:
                        sister_wing2 = wing[0]
                    elif sister_wing3 is None:
                        sister_wing3 = wing[0]
                        break
            '''

            if not sister_wing1 or not sister_wing2 or not sister_wing3:
                log.info("prep_for_slice_back_555() failed...get_sister_wings_slice_backward_555")
                return False

        steps = self.find_moves_to_stage_slice_backward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True
        else:
            log.info("prep_for_slice_back_555() failed...no steps")
            return False

    def get_sister_wings_slice_forward_555(self, pre_non_paired_edges_count):
        results = (None, None, None, None)
        max_pair_on_slice_forward = 0

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        # Work with the wing at the bottom of the F-west edge
        # Move the sister wing to F-east
        target_wing = (self.sideL.edge_east_pos[-1], self.sideF.edge_west_pos[-1])

        for sister_wing1_reverse in (True, False):
            sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0])

            if sister_wing1_reverse:
                sister_wing1 = tuple(list(reversed(sister_wing1)))
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])
            sister_wing2 = None
            sister_wing3 = None

            neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])
            sister_wing1_neighbor = neighbors[0]

            for sister_wing2_reverse in (True, False):
                sister_wing2 = self.get_wing_in_middle_of_edge(sister_wing1_neighbor)

                if sister_wing2_reverse:
                    sister_wing2 = tuple(list(reversed(sister_wing2)))
                sister_wing2_side = self.get_side_for_index(sister_wing2[0])

                neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])
                sister_wing2_neighbor = neighbors[0]

                for sister_wing3_reverse in (True, False):

                    # If we are pairing the last three edges then we need sister_wing3 to
                    # be any unpaired edge that allows us to only pair 2 on the slice forward
                    #
                    if pre_non_paired_edges_count == 3:

                        # We need sister_wing3 to be any unpaired edge that allows us
                        # to only pair 2 on the slice forward
                        for wing in self.get_non_paired_wings():
                            if (wing[0] not in (target_wing, sister_wing1, sister_wing2, sister_wing3) and
                                wing[1] not in (target_wing, sister_wing1, sister_wing2, sister_wing3)):
                                sister_wing3 = wing[1]
                                break
                    else:
                        sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor)

                    if sister_wing3_reverse:
                        sister_wing3 = tuple(list(reversed(sister_wing3)))

                    steps = self.find_moves_to_stage_slice_forward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

                    if steps:
                        for step in steps:
                            self.rotate(step)
                        # 3Uw Uw'
                        self.rotate("Uw'")
                        self.rotate("Dw")
                        self.rotate_y()
                        post_non_paired_edges_count = self.get_non_paired_edges_count()

                        # F-west must pair
                        if self.state[66] == self.state[61] and self.state[45] == self.state[40]:
                            will_pair_on_slice_count = pre_non_paired_edges_count - post_non_paired_edges_count
                        else:
                            will_pair_on_slice_count = 0

                        # restore cube state
                        self.state = copy(original_state)
                        self.solution = copy(original_solution)

                        if will_pair_on_slice_count > max_pair_on_slice_forward:
                            results = (target_wing, sister_wing1, sister_wing2, sister_wing3)
                            max_pair_on_slice_forward = will_pair_on_slice_count

        #log.info("max_pair_on_slice_forward is %d" % max_pair_on_slice_forward)
        #if max_pair_on_slice_forward != 3:
        #    raise SolveError("Could not find sister wings for 5x5x5 slice forward (max_pair_on_slice_forward %d)" % max_pair_on_slice_forward)
        return results

    def rotate_unpaired_wing_to_bottom_of_F_east(self):
        """
        Rotate an unpaired wing to the bottom of F-east (one that can be sliced back)
        """
        for x in range(3):
            if self.state[70] == self.state[65] and self.state[91] == self.state[86]:
                self.rotate_y()
            else:
                if self.prep_for_slice_back_555():
                    return True

        return False

    def flip_two_edge_elements(self):
        middle_wing = (self.sideL.edge_east_pos[1], self.sideF.edge_west_pos[1])
        target_wing = (self.sideL.edge_east_pos[-1], self.sideF.edge_west_pos[-1])
        sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0])
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])
        sister_wing1_neighbor = neighbors[0]
        middle_wing_value = sorted(self.get_wing_value(middle_wing))
        sister_wing_value = sorted(self.get_wing_value(sister_wing1_neighbor))

        if middle_wing_value == sister_wing_value:

            if sister_wing1 == (36, 115):
                self.rotate_z()

            elif sister_wing1 == (123, 148):
                self.rotate("B'")
                self.rotate_z()

            elif sister_wing1 == (98, 140):
                self.rotate("D")
                self.rotate("B'")
                self.rotate_z()

            elif sister_wing1 == (3, 103):
                self.rotate("F")

            elif sister_wing1 == (15, 78):
                self.rotate("R'")
                self.rotate_x()
                self.rotate_y_reverse()

            elif sister_wing1 == (23, 53):
                self.rotate("U2")
                self.rotate("F")

            elif sister_wing1 == (73, 128):
                self.rotate("D2")
                self.rotate("B'")
                self.rotate_z()

            elif sister_wing1 == (48, 136):
                self.rotate("D'")
                self.rotate("B'")
                self.rotate_z()

            elif sister_wing1 == (11, 28):
                self.rotate("U")
                self.rotate("F")

            elif sister_wing1 == (65, 86):
                self.rotate_z_reverse()
                self.rotate_x()

            elif sister_wing1 == (90, 111):
                self.rotate("R2")
                self.rotate_z_reverse()
                self.rotate_x()

            else:
                raise ImplementThis("sister_wing1 %s" % pformat(sister_wing1))

            return True

        return False

    def get_two_edge_pattern_id(self):

        # Build a string that represents the pattern of colors for the U-south and U-north edges
        edges_of_interest = [52, 53, 54, 22, 23, 24, 2, 3, 4, 104, 103, 102]
        sides_in_edges_of_interest = []
        edges_of_interest_state = []

        for square_index in edges_of_interest:
            value = self.state[square_index]
            edges_of_interest_state.append(value)

            if value not in sides_in_edges_of_interest:
                sides_in_edges_of_interest.append(value)

        edges_of_interest_state = ''.join(edges_of_interest_state)
        for (index, value) in enumerate(sides_in_edges_of_interest):
            edges_of_interest_state = edges_of_interest_state.replace(value, str(index))

        # log.info("edges_of_interest_state: %s" % edges_of_interest_state)

        # Exchange places and flip both centers
        if edges_of_interest_state in ('010202020101', '010232323101', '010222222101', '000121212000', '010121212101'):
            pattern_id = 6
            self.rotate_x_reverse()
            self.rotate_z()

        # Exchange places, no flipping
        elif edges_of_interest_state in ('010232101323', '010202101020', '010222101222', '010121101212', '000121000212'):
            pattern_id = 7

        # Exchange places, flip one center
        # The one that has to flip is at U-north, it needs to be at U-south
        elif edges_of_interest_state in ('010232121303', '000121010202', '010121111202', '010202121000', '010222121202'):
            self.rotate_y()
            self.rotate_y()
            pattern_id = 8

        # Exchange places, flip one center
        # The one that has to flip is at U-south
        elif edges_of_interest_state in ('010232303121', '010121202111', '010222202121', '000121202010', '010202000121'):
            pattern_id = 8

        else:
            raise SolveError("Could not determine 5x5x5 last two edges pattern ID for %s" % edges_of_interest_state)

        return pattern_id

    def pair_multiple_edges_555(self, wing_to_pair, pre_non_paired_edges_count):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_edges_count = self.get_non_paired_edges_count()
        self.rotate_edge_to_F_west(wing_to_pair)

        log.info("")
        log.info("pair_multiple_edges_555() with wing_to_pair %s, (%d left to pair, %d steps in)" %
            (pformat(wing_to_pair), original_non_paired_edges_count, original_solution_len))

        if self.state[35] != self.state[45] or self.state[56] != self.state[66]:
            raise SolveError("outside edges have been broken")

        if pre_non_paired_edges_count == 4 and self.pair_last_four_edges_555((45, 66)):
            post_slice_forward_non_paired_edges_count = self.get_non_paired_edges_count()
            post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

            log.info("pair_multiple_edges_555()    paired %d edges in %d moves via pair_last_four_edges_555 (%d left to pair, %d steps in)" %
                (original_non_paired_edges_count - post_slice_forward_non_paired_edges_count,
                 post_slice_forward_solution_len - original_solution_len,
                 post_slice_forward_non_paired_edges_count,
                 post_slice_forward_solution_len))
            return True

        if pre_non_paired_edges_count == 5 and self.pair_one_edge_555((45, 66)):
            post_slice_forward_non_paired_edges_count = self.get_non_paired_edges_count()
            post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

            log.info("pair_multiple_edges_555()    paired %d edges in %d moves via pair_one_edge_555 (%d left to pair, %d steps in)" %
                (original_non_paired_edges_count - post_slice_forward_non_paired_edges_count,
                 post_slice_forward_solution_len - original_solution_len,
                 post_slice_forward_non_paired_edges_count,
                 post_slice_forward_solution_len))

            return True

            # TODO
            # Use the following once the lookup table for pair_last_four_edges_555 is more complete
            if original_non_paired_edges_count - post_slice_forward_non_paired_edges_count == 1:
                return True
            return False

        # We need to rotate the middle wing in place, this is needed when it is next to
        # its two sister wings but is just rotated the wrong way
        #
        # No 1 is when there is only one edge like this, No 5 is when there are two. Ideally
        # we want the No 5 scenario as it pairs two wings in 9 moves where No 1 pairs 1 wing
        # in 15 moves.
        if self.state[56] == self.state[40] and self.state[35] == self.state[61]:

            # U-north
            if self.state[2] == self.state[103] and self.state[3] == self.state[104]:
                self.rotate("U")
                self.rotate("R'")
                pattern_id = 5

            # U-east
            elif self.state[10] == self.state[78] and self.state[15] == self.state[79]:
                self.rotate("R'")
                pattern_id = 5

            # U-south
            elif self.state[52] == self.state[23] and self.state[22] == self.state[53]:
                self.rotate("U'")
                self.rotate("R'")
                pattern_id = 5

            # U-west
            elif self.state[6] == self.state[28] and self.state[11] == self.state[27]:
                self.rotate("U2")
                self.rotate("R'")
                pattern_id = 5

            # L-east
            elif self.state[31] == self.state[115] and self.state[36] == self.state[110]:
                self.rotate_y_reverse()
                pattern_id = 5

            # F-east
            elif self.state[60] == self.state[86] and self.state[81] == self.state[65]:
                pattern_id = 5

            # R-east
            elif self.state[85] == self.state[111] and self.state[90] == self.state[106]:
                self.rotate("R2")
                pattern_id = 5

            # D-north
            elif self.state[72] == self.state[128] and self.state[73] == self.state[127]:
                self.rotate("D")
                self.rotate("R")
                pattern_id = 5

            # D-east
            elif self.state[135] == self.state[98] and self.state[140] == self.state[97]:
                self.rotate("R")
                pattern_id = 5

            # D-south
            elif self.state[147] == self.state[123] and self.state[148] == self.state[124]:
                self.rotate("D'")
                self.rotate("R")
                pattern_id = 5

            # D-west
            elif self.state[131] == self.state[48] and self.state[136] == self.state[49]:
                self.rotate("D2")
                self.rotate("R")
                pattern_id = 5

            else:

                # Move any unpaired edge to F-east so we can use pattern_id 5 instead and save ourselves 6 steps
                if not self.sideR.west_edge_paired():
                    pattern_id = 5

                elif not self.sideL.west_edge_paired():
                    self.rotate_y_reverse()
                    self.rotate_z()
                    self.rotate_z()
                    pattern_id = 5

                elif not self.sideR.north_edge_paired():
                    self.rotate("R'")
                    pattern_id = 5

                elif not self.sideR.east_edge_paired():
                    self.rotate("R2")
                    pattern_id = 5

                elif not self.sideR.south_edge_paired():
                    self.rotate("R")
                    pattern_id = 5

                elif not self.sideD.north_edge_paired():
                    self.rotate("D")
                    self.rotate("R")
                    pattern_id = 5

                elif not self.sideD.south_edge_paired():
                    self.rotate("D'")
                    self.rotate("R")
                    pattern_id = 5

                elif not self.sideD.east_edge_paired():
                    self.rotate("D2")
                    self.rotate("R")
                    pattern_id = 5

                elif not self.sideU.north_edge_paired():
                    self.rotate("U")
                    self.rotate("R'")
                    pattern_id = 5

                elif not self.sideU.west_edge_paired():
                    self.rotate("U2")
                    self.rotate("R'")
                    pattern_id = 5

                elif not self.sideU.south_edge_paired():
                    self.rotate("U'")
                    self.rotate("R'")
                    pattern_id = 5

                else:
                    pattern_id = 1

            # Flip one middle wing in place
            # No 1 at https://i.imgur.com/wsTqj.png
            if pattern_id == 1:
                self.rotate_x()
                self.rotate_y_reverse()

                for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                    self.rotate(step)

            # Flip two middle wings in place
            # No 5 at https://i.imgur.com/wsTqj.png
            elif pattern_id == 5:
                for step in "Dw Uw' R F' U R' F Dw' Uw".split():
                    self.rotate(step)

            post_slice_forward_non_paired_edges_count = self.get_non_paired_edges_count()
            post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)
            edges_paired = original_non_paired_edges_count - post_slice_forward_non_paired_edges_count

            log.info("pair_multiple_edges_555()    paired %d edges in %d moves on flip edge element(s) in place (%d left to pair, %d steps in)" %
                (edges_paired,
                 post_slice_forward_solution_len - original_solution_len,
                 post_slice_forward_non_paired_edges_count,
                 post_slice_forward_solution_len))

            if edges_paired < 1:
                raise SolveError("Failed to pair edges, pattern_id %d" % pattern_id)

            return True

        # Flip two edge elements
        # No 7 at https://i.imgur.com/wsTqj.png
        if self.flip_two_edge_elements():

            pattern_id = self.get_two_edge_pattern_id()

            # No 6 on https://imgur.com/r/all/wsTqj
            # Exchange places and flip both centers
            # 8 moves
            if pattern_id == 6:
                for step in "Uw2 Rw2 F2 Uw2 U2 F2 Rw2 Uw2".split():
                    self.rotate(step)

            # No 7 on https://imgur.com/r/all/wsTqj
            # Exchange places, no flipping
            # 10 moves
            elif pattern_id == 7:
                for step in "F2 Rw D2 Rw' F2 U2 F2 Lw B2 Lw'".split():
                    self.rotate(step)

            # No 8 on https://imgur.com/r/all/wsTqj
            # Exchange places, flip one center
            # 14 moves
            elif pattern_id == 8:
                for step in "Rw2 B2 Rw' U2 Rw' U2 B2 Rw' B2 Rw B2 Rw' B2 Rw2".split():
                    self.rotate(step)

            else:
                raise SolveError("unexpected pattern_id %d" % pattern_id)

            post_slice_forward_non_paired_edges_count = self.get_non_paired_edges_count()
            post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)
            edges_paired = original_non_paired_edges_count - post_slice_forward_non_paired_edges_count

            log.info("pair_multiple_edges_555()    paired %d edges in %d moves on swap two middle elements pattern %d (%d left to pair, %d steps in)" %
                (edges_paired,
                 post_slice_forward_solution_len - original_solution_len,
                 pattern_id,
                 post_slice_forward_non_paired_edges_count,
                 post_slice_forward_solution_len))

            if edges_paired < 2:
                raise SolveError("should have paired 2 edges but only paired %d" % edges_paired)
            return True

        #log.info("PREP-FOR-3Uw-SLICE (begin)")
        #self.print_cube()
        (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_forward_555(pre_non_paired_edges_count)

        if target_wing is None:
            log.info("pair_multiple_edges_555() failed...get_sister_wings_slice_forward_555")
            # raise Exception("pair_multiple_edges_555() failed...get_sister_wings_slice_forward_555")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        steps = self.find_moves_to_stage_slice_forward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if not steps:
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        #log.info("PREP-FOR-3Uw-SLICE (end)....SLICE (begin), %d left to pair" % self.get_non_paired_edges_count())
        #self.print_cube()
        self.rotate("Uw'")
        self.rotate("Dw")
        self.rotate_y()
        #log.info("SLICE (end), %d left to pair" % self.get_non_paired_edges_count())
        #self.print_cube()

        post_slice_forward_non_paired_edges_count = self.get_non_paired_edges_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_multiple_edges_555()    paired %d edges in %d moves on slice forward (%d left to pair, %d steps in)" %
            (original_non_paired_edges_count - post_slice_forward_non_paired_edges_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_edges_count,
             post_slice_forward_solution_len))

        placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

        if not placed_unpaired_wing:

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
                # This can happen if we pair the final four wings on the slice forward
                log.info("Did not find an unpaired edge")
                self.state = copy(original_state)
                self.solution = copy(original_solution)
                return False

            placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()
            if not placed_unpaired_wing:
                self.state = copy(original_state)
                self.solution = copy(original_solution)
                return False

        #log.info("PREP-FOR-3Uw'-SLICE-BACK (end)...SLICE BACK (begin), %d left to pair" % self.get_non_paired_edges_count())
        #self.print_cube()
        self.rotate("Uw")
        self.rotate("Dw'")
        self.rotate_y_reverse()

        #log.info("SLICE BACK (end), %d left to pair" % self.get_non_paired_edges_count())
        #self.print_cube()
        self.verify_all_centers_solved()

        post_slice_back_non_paired_edges_count = self.get_non_paired_edges_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_multiple_edges_555()    paired %d edges in %d moves on slice back (%d left to pair, %d steps in)" %
            (post_slice_forward_non_paired_edges_count - post_slice_back_non_paired_edges_count,
             post_slice_back_solution_len - post_slice_forward_solution_len,
             post_slice_back_non_paired_edges_count,
             post_slice_back_solution_len))

        return True

    def pair_one_edge_555(self, edge):
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_edges_count = self.get_non_paired_edges_count()
        self.rotate_edge_to_F_west(edge)

        if self.state[35] != self.state[45] or self.state[56] != self.state[66]:
            raise SolveError("outside edges have been broken")

        log.info("pair_one_edge_555() called (%d left to pair, %d steps in)" % (original_non_paired_edges_count, original_solution_len))

        # Work with the edge at the bottom of the F west side
        target_wing = self.sideF.edge_west_pos[-1]
        target_wing_value = self.get_wing_value(target_wing)

        # Move sister wing to F-east
        sister_wings = self.get_wings(target_wing, remove_if_in_same_edge=True)

        # This is the scenario where the center edge is beside its two siblings it
        # just needs to be flipped in place.
        if not sister_wings:
            self.print_cube()
            self.rotate_x()
            self.rotate_y_reverse()
            self.print_cube()

            for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                self.rotate(step)
            return True

        sister_wing = sister_wings[0]
        self.move_wing_to_F_east(sister_wing)

        # The sister wing is in the right location but does it need to be flipped?
        sister_wing = self.get_wings_on_edge(target_wing, 'F', 'R')[0]
        sister_wing_value = self.get_wing_value(sister_wing)

        if target_wing_value != sister_wing_value:

            for step in ("R", "U'", "B'", "R2"):
                self.rotate(step)
            sister_wing = self.get_wings_on_edge(target_wing, 'F', 'R')[0]
            sister_wing_value = self.get_wing_value(sister_wing)

        # If there are no unpaired wings on U,B or D then we cannot pair this wing
        # without breaking some other already paired wing.
        if (self.sideU.all_edges_paired() and
            self.sideB.all_edges_paired() and
            self.sideD.all_edges_paired()):
            return False

        else:
            # Now that that two edges on F are in place, put an unpaired wing at U-west
            self.make_U_west_have_unpaired_wing()

        if sister_wing[0] == 65:
            # 3Uw Uw'
            self.rotate("Uw'")
            self.rotate("Dw")
            self.rotate_y()

            for step in "U' L' U L".split():
                self.rotate(step)

            # 3Uw' Uw
            self.rotate("Uw")
            self.rotate("Dw'")
            self.rotate_y_reverse()
        else:
            raise SolveError("sister_wing %s is in the wrong position" % str(sister_wing))

        current_non_paired_edges_count = self.get_non_paired_edges_count()
        edges_paired = original_non_paired_edges_count - current_non_paired_edges_count
        log.info("pair_one_edge_555() paired %d edges, added %d steps" %
            (edges_paired, self.get_solution_len_minus_rotates(self.solution) - original_solution_len))

        if edges_paired <= 0:
            raise SolveError("went from %d to %d" % (original_non_paired_edges_count, current_non_paired_edges_count))
        return True

    def pair_outside_edges(self):
        fake_444 = RubiksCube444(solved_4x4x4)
        fake_444.lt_init()

        # The corners don't matter but it does make troubleshooting easier if they match
        fake_444.state[1] = self.state[1]
        fake_444.state[4] = self.state[5]
        fake_444.state[13] = self.state[21]
        fake_444.state[16] = self.state[25]
        fake_444.state[17] = self.state[26]
        fake_444.state[20] = self.state[30]
        fake_444.state[29] = self.state[46]
        fake_444.state[32] = self.state[50]
        fake_444.state[33] = self.state[51]
        fake_444.state[36] = self.state[55]
        fake_444.state[45] = self.state[71]
        fake_444.state[48] = self.state[75]
        fake_444.state[49] = self.state[76]
        fake_444.state[52] = self.state[80]
        fake_444.state[61] = self.state[96]
        fake_444.state[64] = self.state[100]
        fake_444.state[65] = self.state[101]
        fake_444.state[68] = self.state[105]
        fake_444.state[77] = self.state[121]
        fake_444.state[80] = self.state[125]
        fake_444.state[81] = self.state[126]
        fake_444.state[84] = self.state[130]
        fake_444.state[93] = self.state[146]
        fake_444.state[96] = self.state[150]

        # Upper
        fake_444.state[2] = self.state[2]
        fake_444.state[3] = self.state[4]
        fake_444.state[5] = self.state[6]
        fake_444.state[8] = self.state[10]
        fake_444.state[9] = self.state[16]
        fake_444.state[12] = self.state[20]
        fake_444.state[14] = self.state[22]
        fake_444.state[15] = self.state[24]

        # Left
        fake_444.state[18] = self.state[27]
        fake_444.state[19] = self.state[29]
        fake_444.state[21] = self.state[31]
        fake_444.state[24] = self.state[35]
        fake_444.state[25] = self.state[41]
        fake_444.state[28] = self.state[45]
        fake_444.state[30] = self.state[47]
        fake_444.state[31] = self.state[49]

        # Front
        fake_444.state[34] = self.state[52]
        fake_444.state[35] = self.state[54]
        fake_444.state[37] = self.state[56]
        fake_444.state[40] = self.state[60]
        fake_444.state[41] = self.state[66]
        fake_444.state[44] = self.state[70]
        fake_444.state[46] = self.state[72]
        fake_444.state[47] = self.state[74]

        # Right
        fake_444.state[50] = self.state[77]
        fake_444.state[51] = self.state[79]
        fake_444.state[53] = self.state[81]
        fake_444.state[56] = self.state[85]
        fake_444.state[57] = self.state[91]
        fake_444.state[60] = self.state[95]
        fake_444.state[62] = self.state[97]
        fake_444.state[63] = self.state[99]

        # Back
        fake_444.state[66] = self.state[102]
        fake_444.state[67] = self.state[104]
        fake_444.state[69] = self.state[106]
        fake_444.state[72] = self.state[110]
        fake_444.state[73] = self.state[116]
        fake_444.state[76] = self.state[120]
        fake_444.state[78] = self.state[122]
        fake_444.state[79] = self.state[124]

        # Down
        fake_444.state[82] = self.state[127]
        fake_444.state[83] = self.state[129]
        fake_444.state[85] = self.state[131]
        fake_444.state[88] = self.state[135]
        fake_444.state[89] = self.state[141]
        fake_444.state[92] = self.state[145]
        fake_444.state[94] = self.state[147]
        fake_444.state[95] = self.state[149]

        #self.print_cube()
        #fake_444.print_cube()
        fake_444.group_edges()

        for step in fake_444.solution:
            if step == 'EDGES_GROUPED':
                continue

            if step.startswith('4'):
                step = '5' + step[1:]
            elif step.startswith('3'):
                raise ImplementThis('4x4x4 steps starts with 3')

            self.rotate(step)

        #self.print_cube()
        log.warning("Outside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def group_edges(self):
        self.lt_init()

        self.pair_outside_edges()
        #self.print_cube()

        original_non_paired_edges = self.get_non_paired_edges()
        if not original_non_paired_edges:
            self.solution.append('EDGES_GROUPED')
            return
        original_non_paired_edges_count = len(original_non_paired_edges)

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        # There are 12 edges, cycle through all 12 in terms of which edge we try to pair first.
        min_solution_length = None
        min_solution_state = None
        min_solution = None

        # If you are working on improving edge pairing it is a little easier to
        # troubleshoot if you are not cycling through all 12 edges as your
        # "init_wing_to_pair" so set the following to False.
        #
        # NOTE: I set this to False because if it is True it takes a long time
        # to compute the solution on a beaglebone black
        use_init_wing_to_pair = False

        for init_wing_to_pair in original_non_paired_edges:
            # log.info("init_wing_to_pair %20s" % pformat(init_wing_to_pair))

            if use_init_wing_to_pair:
                if self.pair_multiple_edges_555(init_wing_to_pair[0], original_non_paired_edges_count):
                    pass
                elif self.pair_one_edge_555(init_wing_to_pair[0]):
                    pass
                else:
                    raise SolveError("Could not pair a single edge")

            while True:
                non_paired_edges = self.get_non_paired_edges()
                pre_non_paired_edges_count = len(non_paired_edges)
                pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
                log.info("")
                log.info("")
                log.info("")
                log.warning("%d steps in, %d edges left to pair" % (pre_solution_len, pre_non_paired_edges_count))

                if pre_non_paired_edges_count == 0:
                    break

                # cycle through the unpaired wings and find the wing where pair_multiple_edges_555
                # pairs the most in the least number of moves
                tmp_state = copy(self.state)
                tmp_solution = copy(self.solution)

                min_moves_per_paired_wing = None
                max_edges_paired = None
                max_edges_paired_wing_to_pair = None
                max_wing_solution_len = None

                for foo in non_paired_edges:
                    wing_to_pair = foo[0]

                    if self.pair_multiple_edges_555(wing_to_pair, pre_non_paired_edges_count):

                        post_non_paired_edges_count = self.get_non_paired_edges_count()
                        edges_paired = pre_non_paired_edges_count - post_non_paired_edges_count
                        post_solution_len = self.get_solution_len_minus_rotates(self.solution)
                        wing_solution_len = post_solution_len - pre_solution_len

                        if edges_paired > 0:
                            moves_per_paired_wing = float(wing_solution_len/edges_paired)

                            if (min_moves_per_paired_wing is None or
                                moves_per_paired_wing < min_moves_per_paired_wing or
                                (moves_per_paired_wing == min_moves_per_paired_wing and edges_paired > max_edges_paired)):
                                max_edges_paired = edges_paired
                                max_edges_paired_wing_to_pair = wing_to_pair
                                max_wing_solution_len = wing_solution_len
                                min_moves_per_paired_wing = moves_per_paired_wing

                    # Restore state
                    self.state = copy(tmp_state)
                    self.solution = copy(tmp_solution)

                if max_edges_paired:
                    wing_to_pair = max_edges_paired_wing_to_pair
                    log.info("Using %s as next wing_to_pair will pair %d edges in %d moves" % (wing_to_pair, max_edges_paired, max_wing_solution_len))
                    self.pair_multiple_edges_555(wing_to_pair, pre_non_paired_edges_count)

                # see which wing we can pair two at a time with the least moves
                else:
                    log.warning("There are no wings where pair_multiple_edges_555 will return True")

                    for foo in non_paired_edges:
                        wing_to_pair = foo[0]

                        if self.pair_one_edge_555(wing_to_pair):
                            post_non_paired_edges_count = self.get_non_paired_edges_count()
                            edges_paired = pre_non_paired_edges_count - post_non_paired_edges_count
                            post_solution_len = self.get_solution_len_minus_rotates(self.solution)
                            wing_solution_len = post_solution_len - pre_solution_len

                            if (max_edges_paired is None or
                                edges_paired > max_edges_paired or
                                (edges_paired == max_edges_paired and wing_solution_len < max_wing_solution_len)):
                                max_edges_paired = edges_paired
                                max_edges_paired_wing_to_pair = wing_to_pair
                                max_wing_solution_len = wing_solution_len

                        # Restore state
                        self.state = copy(tmp_state)
                        self.solution = copy(tmp_solution)

                    if max_edges_paired_wing_to_pair is None:
                        raise SolveError("pair_one_edge_555 failed")

                    wing_to_pair = max_edges_paired_wing_to_pair
                    log.info("Using %s as next wing_to_pair will pair %s wings in %s moves" % (wing_to_pair, max_edges_paired, max_wing_solution_len))
                    self.pair_one_edge_555(wing_to_pair)

            solution_len_minus_rotates = self.get_solution_len_minus_rotates(self.solution)
            new_min = False

            if min_solution_length is None:
                new_min = True
            elif solution_len_minus_rotates < min_solution_length:
                new_min = True

            if new_min:
                min_solution_length = solution_len_minus_rotates
                min_solution_state = copy(self.state)
                min_solution = copy(self.solution)
                log.warning("edges solution length %d (NEW MIN)" % (solution_len_minus_rotates - original_solution_len))
            else:
                log.info("edges solution length %d" % (solution_len_minus_rotates - original_solution_len))
            log.info('')

            # restore state
            self.state = copy(original_state)
            self.solution = copy(original_solution)

            if not use_init_wing_to_pair:
                break

        self.state = copy(min_solution_state)
        self.solution = copy(min_solution)

        if self.get_non_paired_edges_count():
            raise SolveError("All edges should be resolved")

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
