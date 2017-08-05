
from collections import OrderedDict
from pprint import pformat
from rubikscubennnsolver import RubiksCube, ImplementThis
from rubikscubennnsolver.RubiksSide import Side, SolveError
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, moves_4x4x4, solved_4x4x4
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA, NoSteps, NoIDASolution
import datetime as dt
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

    def __init__(self, kociemba_string, colormap=None, debug=False):
        RubiksCube.__init__(self, kociemba_string, colormap)
        self.use_pair_outside_edges = False

        # This will be True when an even cube is using the 555 edge solver
        # to pair an orbit of edges
        self.avoid_pll = False

        if debug:
            log.setLevel(logging.DEBUG)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        '''
        lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.txt
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
        '''
        self.lt_UD_T_centers_stage = LookupTable(self,
                                                 'lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.txt',
                                                 '555-UD-T-centers-stage',
                                                 '174000000000ba',
                                                 True, # state_hex
                                                 True, # prune table
                                                 modulo=735473)

        '''
        lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.txt
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
        self.lt_UD_X_centers_stage = LookupTable(self,
                                                 'lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.txt',
                                                 '555-UD-X-centers-stage',
                                                 '2aa00000000155',
                                                 True, # state_hex
                                                 True, # prune table
                                                 modulo=735473)

        self.lt_UD_centers_stage_UFDB_only = LookupTable(self,
                                                 'lookup-table-5x5x5-step13-UD-centers-stage-UFDB-only.txt',
                                                 '555-UD-centers-stage-UFDB-only',
                                                 'TBD',
                                                 True, # state_hex
                                                 True, # prune table
                                                 6,    # max depth of this partial prune table
                                                 modulo=7033619)

        # Not used right now...if we use these we tend to prune too aggresively which forces us to get
        # to IDA threshold of 10 at which point we are exploring tons of branches and it slows us down
        '''
        self.lt_UD_centers_stage_ULDR_only = LookupTable(self,
                                                 'lookup-table-5x5x5-step14-UD-centers-stage-ULDR-only.txt',
                                                 '555-UD-centers-stage-ULDR-only',
                                                 'TBD',
                                                 True, # state_hex
                                                 True, # prune table
                                                 6)    # max depth of this partial prune table

        self.lt_UD_centers_stage_LFRB_only = LookupTable(self,
                                                 'lookup-table-5x5x5-step15-UD-centers-stage-LFRB-only.txt',
                                                 '555-UD-centers-stage-LFRB-only',
                                                 'TBD',
                                                 True, # state_hex
                                                 True, # prune table
                                                 6)    # max depth of this partial prune table
        '''

        '''
        There are 4 T-centers and 4 X-centers so (24!/(8! * 16!))^2 is 540,917,591,841
        We cannot build a table that large so we will build it 7 moves deep and use
        IDA with T-centers and X-centers as our prune tables. Both the T-centers and
        X-centers prune tables will have 735,471 entries, 735,471/540,917,591,841
        is 0.0000013596729171 which is a decent percentage for IDA.

        I ended up building this out to 7-deep, there are another ~312 million entries at 7 steps
        so 328 million total

        lookup-table-5x5x5-step10-UD-centers-stage.txt
        ==============================================
        1 steps has 5 entries (0 percent)
        2 steps has 98 entries (0 percent)
        3 steps has 2,036 entries (0 percent)
        4 steps has 41,096 entries (0 percent)
        5 steps has 824,950 entries (0 percent)
        6 steps has 16,300,291 entries (4 percent)

        Total: 17,168,476 entries
        '''
        self.lt_UD_centers_stage = LookupTableIDA(self,
                                                 'lookup-table-5x5x5-step10-UD-centers-stage.txt',
                                                 '555-UD-centers-stage',
                                                 '3fe000000001ff', # UUUUUUUUUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxUUUUUUUUU
                                                 True, # state_hex
                                                 moves_5x5x5,
                                                 (), # illegal_moves

                                                 # prune tables
                                                 (self.lt_UD_T_centers_stage,
                                                  self.lt_UD_X_centers_stage,
                                                  #self.lt_UD_centers_stage_ULDR_only,
                                                  #self.lt_UD_centers_stage_LFRB_only,
                                                  self.lt_UD_centers_stage_UFDB_only),
                                                 max_depth=6,
                                                 modulo=17168477) # modulo

        '''
        lookup-table-5x5x5-step21-LR-centers-stage-x-center-only.txt
        ============================================================
        1 steps has 3 entries (0 percent, 0.00x previous step)
        2 steps has 29 entries (0 percent, 9.67x previous step)
        3 steps has 234 entries (1 percent, 8.07x previous step)
        4 steps has 1,246 entries (9 percent, 5.32x previous step)
        5 steps has 4,466 entries (34 percent, 3.58x previous step)
        6 steps has 6,236 entries (48 percent, 1.40x previous step)
        7 steps has 656 entries (5 percent, 0.11x previous step)

        Total: 12,870 entries
        '''
        self.lt_LR_centers_stage_x_center_only = LookupTable(self,
                                                             'lookup-table-5x5x5-step21-LR-centers-stage-x-center-only.txt',
                                                             '555-LR-centers-stage-on-LFRB-x-center-only',
                                                             'aa802aa00',
                                                             True, # state_hex
                                                             True, # prune table
                                                             modulo=12889)

        '''
        lookup-table-5x5x5-step22-LR-centers-stage-t-center-only.txt
        ============================================================
        1 steps has 3 entries (0 percent, 0.00x previous step)
        2 steps has 25 entries (0 percent, 8.33x previous step)
        3 steps has 210 entries (1 percent, 8.40x previous step)
        4 steps has 722 entries (5 percent, 3.44x previous step)
        5 steps has 1,752 entries (13 percent, 2.43x previous step)
        6 steps has 4,033 entries (31 percent, 2.30x previous step)
        7 steps has 4,014 entries (31 percent, 1.00x previous step)
        8 steps has 1,977 entries (15 percent, 0.49x previous step)
        9 steps has 134 entries (1 percent, 0.07x previous step)

        Total: 12,870 entries
        '''
        self.lt_LR_centers_stage_t_center_only = LookupTable(self,
                                                             'lookup-table-5x5x5-step22-LR-centers-stage-t-center-only.txt',
                                                             '555-LR-centers-stage-on-LFRB-t-center-only',
                                                             '5d0017400',
                                                             True, # state_hex
                                                             True, # prune table
                                                             modulo=12889)

        '''
        Stage LR centers to sides L or R, this will automagically stage
        the F and B centers to sides F or B. 4 T-centers and 4 X-centers
        on 4 sides (ignore U and D since they are solved) but we treat
        L and R as one color so 8! on the bottom.
        (16!/(8! * 8!)))^2 is 165,636,900

        The copy of this table that is checked in to the repo only goes to 7-deep thus the need for IDA.
        If you build the table out the entire way we'll never use the prune tables and you will get
        a hit on the first lookup.

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
        self.lt_LR_centers_stage = LookupTableIDA(self,
                                                  'lookup-table-5x5x5-step20-LR-centers-stage.txt',
                                                  '555-LR-centers-stage-on-LFRB',
                                                  'ff803fe00', # LLLLLLLLLxxxxxxxxxLLLLLLLLLxxxxxxxxx
                                                  True, # state_hex
                                                  moves_5x5x5,
                                                  ("Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'"), # illegal moves

                                                  # prune tables
                                                  (self.lt_LR_centers_stage_x_center_only,
                                                   self.lt_LR_centers_stage_t_center_only),
                                                  max_depth=7,
                                                  modulo=3805253)

        '''
        lookup-table-5x5x5-step31-UD-centers-solve.txt
        lookup-table-5x5x5-step32-LR-centers-solve.txt
        lookup-table-5x5x5-step33-FB-centers-solve.txt
        ==============================================
        1 steps has 5 entries (0 percent, 0.00x previous step)
        2 steps has 22 entries (0 percent, 4.40x previous step)
        3 steps has 82 entries (1 percent, 3.73x previous step)
        4 steps has 292 entries (5 percent, 3.56x previous step)
        5 steps has 986 entries (20 percent, 3.38x previous step)
        6 steps has 2,001 entries (40 percent, 2.03x previous step)
        7 steps has 1,312 entries (26 percent, 0.66x previous step)
        8 steps has 200 entries (4 percent, 0.15x previous step)

        Total: 4900 entries
        '''
        self.lt_UD_centers_solve = LookupTable(self,
                                               'lookup-table-5x5x5-step31-UD-centers-solve.txt',
                                               '555-UD-centers-solve-on-all',
                                               'UUUUUUUUUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxDDDDDDDDD',
                                               False, # state_hex
                                               True, # prune table
                                               modulo=4903)

        self.lt_LR_centers_solve = LookupTable(self,
                                               'lookup-table-5x5x5-step32-LR-centers-solve.txt',
                                               '555-LR-centers-solve-on-all',
                                               'xxxxxxxxxLLLLLLLLLxxxxxxxxxRRRRRRRRRxxxxxxxxxxxxxxxxxx',
                                               False, # state_hex
                                               True, # prune table
                                               modulo=4903)

        self.lt_FB_centers_solve = LookupTable(self,
                                               'lookup-table-5x5x5-step33-FB-centers-solve.txt',
                                               '555-FB-centers-solve-on-all',
                                               'xxxxxxxxxxxxxxxxxxFFFFFFFFFxxxxxxxxxBBBBBBBBBxxxxxxxxx',
                                               False, # state_hex
                                               True, # prune table
                                               modulo=4903)

        '''
        Would be 117,649,000,000...I built it 7-deep

        lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt
        ==================================================
        1 steps has 7 entries (0 percent, 0.00x previous step)
        2 steps has 99 entries (0 percent, 14.14x previous step)
        3 steps has 1,134 entries (0 percent, 11.45x previous step)
        4 steps has 12,183 entries (0 percent, 10.74x previous step)
        5 steps has 128,730 entries (0 percent, 10.57x previous step)
        6 steps has 1,291,295 entries (9 percent, 10.03x previous step)
        7 steps has 12,250,688 entries (89 percent, 9.49x previous step)

        Total: 13,684,136 entries
        '''
        self.lt_ULFRB_centers_solve = LookupTableIDA(self,
                                                    'lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt',
                                                    '555-ULFRBD-centers-solve',
                                                    'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD',
                                                    False, # state_hex
                                                    moves_5x5x5,

                                                    # These moves would destroy the staged centers
                                                    ("Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'"),

                                                    # prune tables
                                                    (self.lt_UD_centers_solve,
                                                     self.lt_LR_centers_solve,
                                                     self.lt_FB_centers_solve),
                                                    max_depth=7,
                                                    modulo=13684141)

        '''
        lookup-table-5x5x5-step90-edges-slice-forward.txt
        =================================================
        1 steps has 7 entries (0 percent)
        2 steps has 42 entries (0 percent)
        3 steps has 299 entries (3 percent)
        4 steps has 1,306 entries (16 percent)
        5 steps has 3,449 entries (43 percent)
        6 steps has 2,617 entries (33 percent)
        7 steps has 200 entries (2 percent)

        Total: 7920 entries
        '''
        self.lt_edge_slice_forward = LookupTable(self,
                                                 'lookup-table-5x5x5-step90-edges-slice-forward.txt',
                                                 '555-edges-slice-forward',
                                                 'TBD',
                                                 False, # state hex
                                                 False, # prune table
                                                 modulo=7927)

        '''
        lookup-table-5x5x5-step91-edges-slice-backward.txt
        ==================================================
        1 steps has 1 entries (0 percent)
        3 steps has 36 entries (0 percent)
        4 steps has 66 entries (0 percent)
        5 steps has 334 entries (4 percent)
        6 steps has 1,369 entries (17 percent)
        7 steps has 3,505 entries (44 percent)
        8 steps has 2,539 entries (32 percent)
        9 steps has 69 entries (0 percent)

        Total: 7919 entries
        '''
        self.lt_edge_slice_backward = LookupTable(self,
                                                  'lookup-table-5x5x5-step91-edges-slice-backward.txt',
                                                  '555-edges-slice-backward',
                                                  'TBD',
                                                  False, # state hex
                                                  False, # prune table
                                                  modulo=7919)

    def group_centers_guts(self):
        self.lt_init()
        self.rotate_U_to_U()

        # Stage UD centers
        try:
            self.lt_UD_centers_stage.solve(8)
        except NoIDASolution:
            original_state = self.state[:]
            original_solution = self.solution[:]
            self.lt_UD_T_centers_stage.solve() # speed up IDA

            try:
                self.lt_UD_centers_stage.solve(8)
            except NoIDASolution:
                self.state = original_state
                self.solution = original_solution

                self.lt_UD_X_centers_stage.solve() # speed up IDA
                self.lt_UD_centers_stage.solve(99)

        log.info("Took %d steps to stage UD centers" % len(self.solution))


        # Stage LR centers
        self.lt_LR_centers_stage.solve(99)
        log.info("Took %d steps to stage ULFRBD centers" % len(self.solution))


        # All centers are staged so solve them
        try:
            self.lt_ULFRB_centers_solve.solve(8)
        except NoIDASolution:
            self.lt_UD_centers_solve.solve() # speed up IDA
            self.lt_ULFRB_centers_solve.solve(99)
        log.info("Took %d steps to solve ULFRBD centers" % len(self.solution))
        #self.print_cube()
        #sys.exit(0)

    def find_moves_to_stage_slice_backward_555(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_backward.steps(state)

    def get_sister_wings_slice_backward_555(self):
        results = (None, None, None, None)
        max_pair_on_slice_back = 0

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

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

            for sister_wing1_use_first_neighbor in (True, False):
                neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])

                if sister_wing1_use_first_neighbor:
                    sister_wing1_neighbor = neighbors[0]
                else:
                    sister_wing1_neighbor = neighbors[1]

                for sister_wing2_reverse in (True, False):
                    sister_wing2 = self.get_wing_in_middle_of_edge(sister_wing1_neighbor)

                    if sister_wing2_reverse:
                        sister_wing2 = tuple(list(reversed(sister_wing2)))
                    sister_wing2_side = self.get_side_for_index(sister_wing2[0])

                    #log.info("sister_wing1_use_first_neighbor %s, sister_wing2 %s on %s" %
                    #     (sister_wing1_use_first_neighbor, pformat(sister_wing2), sister_wing2_side))

                    for sister_wing2_use_first_neighbor in (True, False):
                        neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])

                        if sister_wing2_use_first_neighbor:
                            sister_wing2_neighbor = neighbors[0]
                        else:
                            sister_wing2_neighbor = neighbors[1]

                        for sister_wing3_reverse in (True, False):
                            sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor)

                            if sister_wing3_reverse:
                                sister_wing3 = tuple(list(reversed(sister_wing3)))

                            #log.info("sister_wing2_use_first_neighbor %s, sister_wing3 %s" %
                            #    (sister_wing2_use_first_neighbor, pformat(sister_wing3)))

                            steps = self.find_moves_to_stage_slice_backward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

                            if steps:
                                pre_non_paired_wings_count = self.get_non_paired_wings_count()
                                for step in steps:
                                    self.rotate(step)

                                # 3Uw' Uw
                                if self.use_pair_outside_edges:
                                    self.rotate("Uw")
                                self.rotate("Dw'")
                                self.rotate_y_reverse()

                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # F-east must pair
                                if self.state[70] == self.state[65] and self.state[91] == self.state[86]:
                                    will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                else:
                                    will_pair_on_slice_count = 0

                                #log.info("get_sister_wings_slice_backward_555() will_pair_on_slice_count %d via %s" %
                                #    (will_pair_on_slice_count, ' '.join(steps)))

                                # restore cube state
                                self.state = original_state[:]
                                self.solution = original_solution[:]

                                if will_pair_on_slice_count > max_pair_on_slice_back:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3)
                                    max_pair_on_slice_back = will_pair_on_slice_count

        # log.info("max_pair_on_slice_back is %d" % max_pair_on_slice_back)
        return results

    def prep_for_slice_back_555(self):

        (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

        if target_wing is None:
            log.info("prep_for_slice_back_555() failed...get_sister_wings_slice_backward_555")
            #raise SolveError("prep_for_slice_back_555() failed...get_sister_wings_slice_backward_555")
            return False

        steps = self.find_moves_to_stage_slice_backward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True
        else:
            log.info("prep_for_slice_back_555() failed...no steps")
            return False

    def get_sister_wings_slice_forward_555(self, pre_non_paired_edges_count, pre_non_paired_wings_count):
        results = (None, None, None, None, None)
        max_pair_on_slice_forward = 0

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

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
            #log.info("sister_wing1 %s, reverse %s, %s" % (pformat(sister_wing1), sister_wing1_reverse, sister_wing1_side))

            for sister_wing1_use_first_neighbor in (True, False):
                neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])

                if sister_wing1_use_first_neighbor:
                    sister_wing1_neighbor = neighbors[0]
                else:
                    sister_wing1_neighbor = neighbors[1]

                for sister_wing2_reverse in (True, False):
                    sister_wing2 = self.get_wing_in_middle_of_edge(sister_wing1_neighbor)

                    if sister_wing2_reverse:
                        sister_wing2 = tuple(list(reversed(sister_wing2)))
                    sister_wing2_side = self.get_side_for_index(sister_wing2[0])

                    #log.info("sister_wing1_use_first_neighbor %s, sister_wing2 %s, reverse %s, %s" %
                    #   (sister_wing1_use_first_neighbor, pformat(sister_wing2), sister_wing2_reverse, sister_wing2_side))

                    for sister_wing2_use_first_neighbor in (True, False):
                        neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])

                        if sister_wing2_use_first_neighbor:
                            sister_wing2_neighbor = neighbors[0]
                        else:
                            sister_wing2_neighbor = neighbors[1]

                        for sister_wing3_reverse in (True, False):

                            # If we are pairing the last 4, 5 or 6 edges then we need sister_wing3 to
                            # be any unpaired edge that allows us to only pair 2 edges on the slice forward
                            if pre_non_paired_edges_count in (4, 5, 6):

                                # We need sister_wing3 to be any unpaired edge that allows us
                                # to only pair 2 on the slice forward
                                for wing in self.get_non_paired_wings():
                                    if (wing[0] not in (target_wing, sister_wing1, sister_wing2, sister_wing3, (40, 61), (61, 40)) and
                                        wing[1] not in (target_wing, sister_wing1, sister_wing2, sister_wing3, (40, 61), (61, 40))):
                                        sister_wing3 = wing[1]
                                        break
                            else:
                                sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor)

                            if sister_wing3_reverse:
                                sister_wing3 = tuple(list(reversed(sister_wing3)))

                            state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
                            steps = self.lt_edge_slice_forward.steps(state)

                            #log.info("sister_wing2_use_first_neighbor %s, sister_wing3 %s, reverse %s, state %s, steps %s" %
                            #    (sister_wing2_use_first_neighbor, pformat(sister_wing3), sister_wing3_reverse, state, "True" if steps else "False"))

                            if steps:
                                log.info("target_wing %s, sister_wing1 %s, sister_wing2 %s, sister_wing3 %s" %
                                    (pformat(target_wing), pformat(sister_wing1), pformat(sister_wing2), pformat(sister_wing3)))

                                for step in steps:
                                    self.rotate(step)

                                # 3Uw Uw'
                                if self.use_pair_outside_edges:
                                    self.rotate("Uw'")

                                self.rotate("Dw")
                                self.rotate_y()
                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # F-west must pair
                                if self.state[66] == self.state[61] and self.state[45] == self.state[40]:
                                    will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                else:
                                    will_pair_on_slice_count = 0

                                # restore cube state
                                self.state = original_state[:]
                                self.solution = original_solution[:]

                                if will_pair_on_slice_count > max_pair_on_slice_forward:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3, steps)
                                    max_pair_on_slice_forward = will_pair_on_slice_count

        #if pre_non_paired_edges_count in (4, 5, 6):
        #    if max_pair_on_slice_forward != 2:
        #        raise SolveError("Should pair 2 on slice forward but will pair %d" % max_pair_on_slice_forward)

        #log.info("max_pair_on_slice_forward is %d" % max_pair_on_slice_forward)
        #if max_pair_on_slice_forward != 3:
        #    raise SolveError("Could not find sister wings for 5x5x5 slice forward (max_pair_on_slice_forward %d)" % max_pair_on_slice_forward)
        return results

    def rotate_unpaired_wing_to_bottom_of_F_east(self):
        """
        Rotate an unpaired wing to the bottom of F-east (one that can be sliced back)
        """
        for x in xrange(3):
            if self.state[65] == self.state[70] and self.state[86] == self.state[91]:
                self.rotate_y()
            else:
                if self.prep_for_slice_back_555():
                    return True

        return False

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
        fake_444.group_edges()

        for step in fake_444.solution:
            if step == 'EDGES_GROUPED':
                continue

            if step.startswith('4'):
                step = '5' + step[1:]
            elif step.startswith('3'):
                raise ImplementThis('4x4x4 steps starts with 3')
            self.rotate(step)

        log.warning("Outside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def get_two_edge_pattern_id(self):

        def colors_in(squares):
            results = []
            for x in squares:
                results.append(self.state[x])
            return sorted(list(set(results)))

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
        #log.info("edges_of_interest_state: %s" % edges_of_interest_state)

        # 1, 5, 6, 7, and 8 are the scenarios where the outsided wings are paired...so these are the only ones
        # you hit if you use the 4x4x4 edge solver to pair all of the outside wings first. 1 and 5 are handled
        # via pair_checkboard_edge_555() which has been called by now so we do not need to look for those two scenarios here.
        #
        # See https://i.imgur.com/wsTqj.png for these patterns

        # No 6 - Exchange places and flip both centers
        if edges_of_interest_state in ('010202020101', '010232323101', '010222222101', '000121212000', '010121212101'):
            pattern_id = 6
            self.rotate_x_reverse()
            self.rotate_z()

        # No 7 - Exchange places, no flipping
        elif edges_of_interest_state in ('010232101323', '010202101020', '010222101222', '010121101212', '000121000212'):
            pattern_id = 7

        # No 8 regular - Exchange places, flip one center
        # The one that has to flip is at U-south
        elif edges_of_interest_state in ('010232303121', '010121202111', '010222202121', '000121202010', '010202000121'):
            pattern_id = 8

        # No 8 - Exchange places, flip one center
        # The one that has to flip is at U-north, it needs to be at U-south
        elif edges_of_interest_state in ('010232121303', '000121010202', '010121111202', '010202121000', '010222121202'):
            self.rotate_y()
            self.rotate_y()
            pattern_id = 8

        # No 2 regular
        elif edges_of_interest_state in ('001222110222', '010222101222', '001220110002', '000112000221', '001112110221', '001223110332'):
            pattern_id = 2

        # No 2 but the one at U-south needs to flip around
        elif edges_of_interest_state in ('011122112001', '011233223001', '011200220001', '011222222001', '000122112000'):
            self.rotate("F")
            self.rotate("U'")
            self.rotate("R")
            self.rotate_y()
            pattern_id = 2

        # No 2 but the one at U-north needs to flip around
        elif edges_of_interest_state in ('001220200011', '001223233011', '001222222011', '001112122011', '000112122000'):
            self.rotate("U")
            self.rotate("R")
            self.rotate("U'")
            self.rotate("B")
            pattern_id = 2

        # No 2 that just needs to be rotated around 180 degrees
        elif edges_of_interest_state in ('011222100222', '011122100211', '011200100022', '011233100322', '000122000211'):
            self.rotate_y()
            self.rotate_y()
            pattern_id = 2

        # No 3 regular
        elif edges_of_interest_state in ('001223213031', '000112102020', '001222212021', '001220210001', '001112112021'):
            pattern_id = 3
            self.rotate_x_reverse()
            self.rotate_z()

        # No 3 where it just needs to be rotated down and counter clockwise
        elif edges_of_interest_state in ('010102122000', '011102122011', '012103133022', '012101111022', '012100100022'):
            self.rotate_x_reverse()
            self.rotate_z_reverse()
            pattern_id = 3

        # No 3 where it just needs to be rotated down, clockwise and the F-east edge needs to be flipped
        elif edges_of_interest_state in ('001220100012', '001223130312', '000112020201', '001112120211', '001222120212'):
            self.rotate_x_reverse()
            self.rotate_z()
            self.rotate("R")
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
            pattern_id = 3

        # No 3 where it just needs to be rotated down, counter clockwise and the F-east edge needs to be flipped
        elif edges_of_interest_state in ('012221200122', '012321200133', '012121200111', '001210100022', '010201000122'):
            self.rotate_x_reverse()
            self.rotate_z_reverse()
            self.rotate("R")
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
            pattern_id = 3

        # No 4 regular, rotate down and counter clockwise
        elif edges_of_interest_state in ('011233203021', '000122102010', '011200200021', '011122102011', '011222202021'):
            pattern_id = 4
            self.rotate_x_reverse()
            self.rotate_z_reverse()

        # No 4 where it needs to be rotated down and clockwise
        elif edges_of_interest_state in ('010201221000', '001210220001', '012321331002', '012221221002', '012121111002'):
            self.rotate_x_reverse()
            self.rotate_z()
            pattern_id = 4

        # No 4 where it needs to be rotated down, clockwise and F-west needs to be flipped
        elif edges_of_interest_state in ('012103220331', '012100220001', '010102000221', '011102110221', '012101220111'):
            self.rotate_x_reverse()
            self.rotate_z()
            self.rotate("L'")
            self.rotate("F")
            self.rotate("U'")
            self.rotate("F'")
            pattern_id = 4

        # No 4 where it needs to be rotated down, counter clockwise and F-west needs to be flipped
        elif edges_of_interest_state in ('011233120302', '011122110201', '000122010201', '011222120202', '011200120002'):
            self.rotate_x_reverse()
            self.rotate_z_reverse()
            self.rotate("L'")
            self.rotate("F")
            self.rotate("U'")
            self.rotate("F'")
            pattern_id = 4

        # No 9 regular
        elif edges_of_interest_state in ('001210200021', '012221201022', '010201201020', '012121101012', '012321301032'):
            pattern_id = 9

        # No 9 where U-north needs to be flipped
        elif edges_of_interest_state in ('001210120002', '012221220102', '012121210101', '012321230103', '010201020102'):
            self.rotate("U")
            self.rotate("R")
            self.rotate("U'")
            self.rotate("B")
            pattern_id = 9

        # No 10 regular
        elif edges_of_interest_state in ('012103123032', '012100120002', '011102112021', '012101121012', '010102102020'):
            pattern_id = 10

        # No 10 where U-north needs to be flipped
        elif edges_of_interest_state in ('011102120211', '012100200021', '012103230321', '012101210121', '010102020201'):
            self.rotate("U")
            self.rotate("R")
            self.rotate("U'")
            self.rotate("B")
            pattern_id = 10

        else:
            self.print_cube()
            raise SolveError("Could not determine 5x5x5 last two edges pattern ID for %s" % edges_of_interest_state)

        return pattern_id

    def position_last_two_edges_555(self):
        """
        One unpaired edge is at F-west, position it and its sister edge to U-north and U-south
        """
        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        if not self.sideL.west_edge_paired():
            self.rotate_z()

        elif not self.sideB.south_edge_paired():
            self.rotate("B'")
            self.rotate_z()

        elif not self.sideR.south_edge_paired():
            self.rotate("D")
            self.rotate("B'")
            self.rotate_z()

        elif not self.sideU.north_edge_paired():
            self.rotate("F")

        elif not self.sideU.east_edge_paired():
            self.rotate("R'")
            self.rotate_x()
            self.rotate_y_reverse()

        elif not self.sideU.south_edge_paired():
            self.rotate("U2")
            self.rotate("F")

        elif not self.sideF.south_edge_paired():
            self.rotate("D2")
            self.rotate("B'")
            self.rotate_z()

        elif not self.sideL.south_edge_paired():
            self.rotate("D'")
            self.rotate("B'")
            self.rotate_z()

        elif not self.sideL.north_edge_paired():
            self.rotate("U")
            self.rotate("F")

        elif not self.sideR.west_edge_paired():
            self.rotate_z_reverse()
            self.rotate_x()

        elif not self.sideR.east_edge_paired():
            self.rotate("R2")
            self.rotate_z_reverse()
            self.rotate_x()

        else:
            raise ImplementThis("sister_wing1 %s" % pformat(sister_wing1))

        # Assert that U-north and U-south are not paired
        if self.sideU.north_edge_paired():
            raise SolveError("U-north should not be paired, sister_wing1 %s" % pformat(sister_wing1))

        if self.sideU.north_edge_paired():
            raise SolveError("U-south should not be paired, sister_wing1 %s" % pformat(sister_wing1))

    def position_sister_edges_555(self):
        """
        One unpaired edge is at F-west, position it and its sister edge to U-north and U-south
        """
        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        target_wing = self.sideF.edge_west_pos[1]
        sister_wing = self.get_wings(target_wing, remove_if_in_same_edge=True)[0]
        sister_wing_side = self.get_side_for_index(sister_wing[0])

        if sister_wing[0] in self.sideL.edge_west_pos or sister_wing[0] in self.sideB.edge_east_pos:
            self.rotate_z()

        elif sister_wing[0] in self.sideB.edge_south_pos or sister_wing[0] in self.sideD.edge_south_pos:
            self.rotate("B'")
            self.rotate_z()

        elif sister_wing[0] in self.sideR.edge_south_pos or sister_wing[0] in self.sideD.edge_east_pos:
            self.rotate("D")
            self.rotate("B'")
            self.rotate_z()

        elif sister_wing[0] in self.sideU.edge_north_pos or sister_wing[0] in self.sideB.edge_north_pos:
            self.rotate("F")

        elif sister_wing[0] in self.sideU.edge_east_pos or sister_wing[0] in self.sideL.edge_north_pos:
            self.rotate("R'")
            self.rotate_x()
            self.rotate_y_reverse()

        elif sister_wing[0] in self.sideU.edge_south_pos or sister_wing[0] in self.sideF.edge_north_pos:
            self.rotate("U2")
            self.rotate("F")

        elif sister_wing[0] in self.sideF.edge_south_pos or sister_wing[0] in self.sideD.edge_north_pos:
            self.rotate("D2")
            self.rotate("B'")
            self.rotate_z()

        elif sister_wing[0] in self.sideL.edge_south_pos or sister_wing[0] in self.sideD.edge_west_pos:
            self.rotate("D'")
            self.rotate("B'")
            self.rotate_z()

        elif sister_wing[0] in self.sideL.edge_north_pos or sister_wing[0] in self.sideU.edge_west_pos:
            self.rotate("U")
            self.rotate("F")

        elif sister_wing[0] in self.sideR.edge_west_pos or sister_wing[0] in self.sideF.edge_east_pos:
            self.rotate_z_reverse()
            self.rotate_x()

        elif sister_wing[0] in self.sideR.edge_east_pos or sister_wing[0] in self.sideB.edge_west_pos:
            self.rotate("R2")
            self.rotate_z_reverse()
            self.rotate_x()

        else:
            raise ImplementThis("sister_wing %s" % pformat(sister_wing))

        # Assert that U-north and U-south are not paired
        if self.sideU.north_edge_paired():
            raise SolveError("U-north should not be paired, sister_wing1 %s" % pformat(sister_wing1))

        if self.sideU.north_edge_paired():
            raise SolveError("U-south should not be paired, sister_wing1 %s" % pformat(sister_wing1))

    def all_colors_on_two_edges(self):
        target_wing = self.sideF.edge_west_pos[0]
        sister_wings = self.get_wings(target_wing, remove_if_in_same_edge=True)

        if not sister_wings:
            raise SolveError("We should not be here")

        if len(sister_wings) > 1:
            #log.info("F-west sister_wings %s" % pformat(sister_wings))
            return False

        sister_wing = sister_wings[0]
        target_edge_colors = self.get_edge_colors(target_wing)
        sister_wing_edge_colors = self.get_edge_colors(sister_wing[0])
        combined_edge_colors = list(set(target_edge_colors + sister_wing_edge_colors))
        #log.info("F-west combined_edge_colors %s" % pformat(combined_edge_colors))

        if len(combined_edge_colors) == 2:
            #log.info("all_colors_on_two_edges target %s" % pformat(target_wing))
            #log.info("all_colors_on_two_edges sister_wing %s" % pformat(sister_wing))
            #log.info("all_colors_on_two_edges target_edge_colors %s" % pformat(target_edge_colors))
            #log.info("all_colors_on_two_edges sister_wing_edge_colors %s" % pformat(sister_wing_edge_colors))
            #log.info("all_colors_on_two_edges combined %s" % pformat(combined_edge_colors))
            return True

        return False

    def pair_two_sister_edges_555(self, pre_solution_len, pre_non_paired_wings_count, pre_non_paired_edges_count):
        """
        This only works when there are only two colors of wings to work with. This
        is always the case for the last two edges but it can happen prior to that
        as well.
        """
        if pre_non_paired_edges_count == 2:
            self.position_last_two_edges_555()
            all_edges_should_pair = True
        else:
            if self.all_colors_on_two_edges():
                self.position_sister_edges_555()
                all_edges_should_pair = False
            else:
                return False

        pattern_id = self.get_two_edge_pattern_id()
        # log.info("pattern_id: %d" % pattern_id)

        # No 2 on https://imgur.com/r/all/wsTqj
        # 12 moves, pairs 2
        if pattern_id == 2:
            expected_pair_count = 2

            for step in "Lw' U2 Lw' U2 F2 Lw' F2 Rw U2 Rw' U2 Lw2".split():
                self.rotate(step)

        # No 3 on https://imgur.com/r/all/wsTqj
        # 7 moves, pairs 3
        elif pattern_id == 3:
            expected_pair_count = 3

            for step in "Dw R F' U R' F Dw'".split():
                self.rotate(step)

        # No 4 on https://imgur.com/r/all/wsTqj
        # 9 moves, pairs 4
        elif pattern_id == 4:
            expected_pair_count = 3

            for step in "Dw' L' U' L F' L F L' Dw".split():
                self.rotate(step)

        # 6, 7, and 8 are the scenarios where the outsided wings are paired...so these are
        # the only ones you hit if you use the 4x4x4 edge solver to pair all of the outside
        # wings first.
        #
        # No 6 on https://imgur.com/r/all/wsTqj
        # 8 moves, pairs 4
        elif pattern_id == 6:
            expected_pair_count = 4

            for step in "Uw2 Rw2 F2 Uw2 U2 F2 Rw2 Uw2".split():
                self.rotate(step)

        # No 7 on https://imgur.com/r/all/wsTqj
        # 10 moves, pairs 4
        elif pattern_id == 7:
            expected_pair_count = 4

            for step in "F2 Rw D2 Rw' F2 U2 F2 Lw B2 Lw'".split():
                self.rotate(step)

        # No 8 on https://imgur.com/r/all/wsTqj
        # 14 moves, pairs 4
        elif pattern_id == 8:
            expected_pair_count = 4

            for step in "Rw2 B2 Rw' U2 Rw' U2 B2 Rw' B2 Rw B2 Rw' B2 Rw2".split():
                self.rotate(step)

        # No 9 on https://imgur.com/r/all/wsTqj
        # 13 moves, pairs 4
        elif pattern_id == 9:
            expected_pair_count = 4

            for step in "Lw U2 Lw2 U2 Lw' U2 Lw U2 Lw' U2 Lw2 U2 Lw".split():
                self.rotate(step)

        # No 10 on https://imgur.com/r/all/wsTqj
        # 13 moves, pairs 4
        elif pattern_id == 10:
            expected_pair_count = 4

            for step in "Rw' U2 Rw2 U2 Rw U2 Rw' U2 Rw U2 Rw2 U2 Rw'".split():
                self.rotate(step)

        else:
            raise SolveError("unexpected pattern_id %d" % pattern_id)

        post_solution_len = self.get_solution_len_minus_rotates(self.solution)
        post_non_paired_edges_count = self.get_non_paired_edges_count()
        post_non_paired_wings_count = self.get_non_paired_wings_count()
        wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count

        log.info("pair_two_sister_edges_555() paired %d wings in %d moves (%d left to pair, %d steps in)" %
            (wings_paired,
             post_solution_len - pre_solution_len,
             post_non_paired_wings_count,
             post_solution_len))

        if wings_paired < expected_pair_count:
            raise SolveError("Paired %d wings, expected to pair %d, pattern_id %d" % (wings_paired, expected_pair_count, pattern_id))

        if all_edges_should_pair and post_non_paired_edges_count:
            raise SolveError("All edges should be paired")

        return True

    def pair_four_or_six_wings_555(self, wing_to_pair, pre_non_paired_edges_count):
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        log.info("pair_four_or_six_wings_555()")
        # log.info("PREP-FOR-3Uw-SLICE (begin)")

        (target_wing, sister_wing1, sister_wing2, sister_wing3, steps) = self.get_sister_wings_slice_forward_555(pre_non_paired_edges_count, original_non_paired_wings_count)

        if target_wing is None:
            log.info("pair_four_or_six_wings_555() failed...get_sister_wings_slice_forward_555")
            #raise SolveError("pair_four_or_six_wings_555() failed...get_sister_wings_slice_forward_555")
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        # log.info("PREP-FOR-3Uw-SLICE (end)....SLICE (begin), %d left to pair" % self.get_non_paired_wings_count())
        # 3Uw Uw'
        if self.use_pair_outside_edges:
            self.rotate("Uw'")
        self.rotate("Dw")
        self.rotate_y()

        #log.info("SLICE (end), %d left to pair" % self.get_non_paired_wings_count())
        post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_four_or_six_wings_555() paired %d wings in %d moves on slice forward (%d left to pair, %d steps in)" %
            (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len))

        # setup for slice back
        placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

        # We paired all 8 wings on the slice forward so rotate the edges from U and D onto L and F and check again
        if not placed_unpaired_wing:
            self.rotate("R")
            self.rotate("L'")
            self.rotate("U")
            self.rotate("D")
            self.rotate("R'")
            self.rotate("L")
            placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

            if not placed_unpaired_wing:
                log.info("pair_four_or_six_wings_555() failed...no unpaired wings to move to F-east")
                return False

        #log.info("PREP-FOR-3Uw'-SLICE-BACK (end)...SLICE BACK (begin), %d left to pair" % self.get_non_paired_wings_count())
        # 3Uw' Uw
        if self.use_pair_outside_edges:
            self.rotate("Uw")
        self.rotate("Dw'")
        self.rotate_y()

        #log.info("SLICE BACK (end), %d left to pair" % self.get_non_paired_wings_count())
        #self.verify_all_centers_solved()

        post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)
        wings_paired = post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count

        log.info("pair_four_or_six_wings_555() paired %d wings in %d moves on slice back (%d left to pair, %d steps in)" %
            (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len - post_slice_forward_solution_len,
             post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len))

        if wings_paired < 1:
            raise SolveError("Paired %d wings" % wings_paired)

        return True

    def pair_checkboard_edge_555(self, pre_solution_len, pre_non_paired_wings_count):
        """
        We need to rotate the middle wing in place, this is needed when it is next to
        its two sister wings but is just rotated the wrong way

        No 1 is when there is only one edge like this, No 5 is when there are two. Ideally
        we want the No 5 scenario as it pairs two wings in 9 moves where No 1 pairs 1 wing
        in 15 moves.
        """

        if (self.state[35] == self.state[45] and
            self.state[56] == self.state[66] and
            self.state[56] == self.state[40] and
            self.state[35] == self.state[61]):
            is_checkerboard = True
        else:
            is_checkerboard = False

        if is_checkerboard:
            expected_pair_count = None

            # F-east
            if self.state[60] == self.state[86] and self.state[81] == self.state[65] and self.state[60] == self.state[70] and self.state[81] == self.state[91]:
                pattern_id = 5
                expected_pair_count = 4

            # L-east
            elif self.state[31] == self.state[115] and self.state[36] == self.state[110] and self.state[31] == self.state[41] and self.state[110] == self.state[120]:
                self.rotate_y_reverse()
                pattern_id = 5
                expected_pair_count = 4

            # U-east
            elif self.state[10] == self.state[78] and self.state[15] == self.state[79] and self.state[10] == self.state[20] and self.state[77] == self.state[79]:
                self.rotate("R'")
                pattern_id = 5
                expected_pair_count = 4

            # D-east
            elif self.state[135] == self.state[98] and self.state[140] == self.state[97] and self.state[135] == self.state[145] and self.state[97] == self.state[99]:
                self.rotate("R")
                pattern_id = 5
                expected_pair_count = 4

            # R-east
            elif self.state[85] == self.state[111] and self.state[90] == self.state[106] and self.state[85] == self.state[95] and self.state[106] == self.state[116]:
                self.rotate("R2")
                pattern_id = 5
                expected_pair_count = 4

            # U-north
            elif self.state[2] == self.state[103] and self.state[3] == self.state[104] and self.state[2] == self.state[4] and self.state[102] == self.state[104]:
                self.rotate("U")
                self.rotate("R'")
                pattern_id = 5
                expected_pair_count = 4

            # U-south
            elif self.state[52] == self.state[23] and self.state[22] == self.state[53] and self.state[52] == self.state[54] and self.state[22] == self.state[24]:
                self.rotate("U'")
                self.rotate("R'")
                pattern_id = 5
                expected_pair_count = 4

            # U-west
            elif self.state[6] == self.state[28] and self.state[11] == self.state[27] and self.state[6] == self.state[16] and self.state[27] == self.state[29]:
                self.rotate("U2")
                self.rotate("R'")
                pattern_id = 5
                expected_pair_count = 4

            # D-north
            elif self.state[72] == self.state[128] and self.state[73] == self.state[127] and self.state[72] == self.state[74] and self.state[127] == self.state[129]:
                self.rotate("D")
                self.rotate("R")
                pattern_id = 5
                expected_pair_count = 4

            # D-south
            elif self.state[147] == self.state[123] and self.state[148] == self.state[124] and self.state[147] == self.state[149] and self.state[122] == self.state[124]:
                self.rotate("D'")
                self.rotate("R")
                pattern_id = 5
                expected_pair_count = 4

            # D-west
            elif self.state[131] == self.state[48] and self.state[136] == self.state[49] and self.state[131] == self.state[141] and self.state[47] == self.state[49]:
                self.rotate("D2")
                self.rotate("R")
                pattern_id = 5
                expected_pair_count = 4

            else:
                expected_pair_count = 2

                # Move any unpaired edge to F-east so we can use pattern_id 5 instead and save ourselves 6 steps
                # It must be an edge without any paired wings.
                if self.sideR.west_edge_non_paired_wings_count() == 2:
                    pattern_id = 5

                elif self.sideL.west_edge_non_paired_wings_count() == 2:
                    self.rotate_y_reverse()
                    self.rotate_z()
                    self.rotate_z()
                    pattern_id = 5

                elif self.sideR.north_edge_non_paired_wings_count() == 2:
                    self.rotate("R'")
                    pattern_id = 5

                elif self.sideR.east_edge_non_paired_wings_count() == 2:
                    self.rotate("R2")
                    pattern_id = 5

                elif self.sideR.south_edge_non_paired_wings_count() == 2:
                    self.rotate("R")
                    pattern_id = 5

                elif self.sideD.north_edge_non_paired_wings_count() == 2:
                    self.rotate("D")
                    self.rotate("R")
                    pattern_id = 5

                elif self.sideD.south_edge_non_paired_wings_count() == 2:
                    self.rotate("D'")
                    self.rotate("R")
                    pattern_id = 5

                elif self.sideD.east_edge_non_paired_wings_count() == 2:
                    self.rotate("D2")
                    self.rotate("R")
                    pattern_id = 5

                elif self.sideU.north_edge_non_paired_wings_count() == 2:
                    self.rotate("U")
                    self.rotate("R'")
                    pattern_id = 5

                elif self.sideU.west_edge_non_paired_wings_count() == 2:
                    self.rotate("U2")
                    self.rotate("R'")
                    pattern_id = 5

                elif self.sideU.south_edge_non_paired_wings_count() == 2:
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

            post_solution_len = self.get_solution_len_minus_rotates(self.solution)
            post_non_paired_edges_count = self.get_non_paired_edges_count()
            post_non_paired_wings_count = self.get_non_paired_wings_count()
            wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count

            log.info("pair_checkboard_edge_555() paired %d wings in %d moves (%d left to pair, %d steps in)" %
                (wings_paired,
                 post_solution_len - pre_solution_len,
                 post_non_paired_wings_count,
                 post_solution_len))

            if not self.use_pair_outside_edges:
                expected_pair_count = int(expected_pair_count/2)

            if wings_paired < expected_pair_count:
                raise SolveError("Paired %d wings, expected to pair %d, pattern_id %d" % (wings_paired, expected_pair_count, pattern_id))

            return True

        return False

    def pair_one_wing_555(self):
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        log.info("pair_one_wing_555() called (%d left to pair, %d steps in)" % (original_non_paired_wings_count, original_solution_len))

        # Work with the edge at the bottom of F-west
        target_wing = self.sideF.edge_west_pos[-1]
        target_wing_value = self.get_wing_value(target_wing)
        sister_wings = self.get_wings(target_wing)
        checkerboard = False

        # This is the scenario where the center edge is beside its two siblings it
        # just needs to be flipped in place.
        if not sister_wings:
            raise SolveError("We should not be here")


        # Is this a checkerboard?
        if (40, 61) in sister_wings:
            checkerboard = True
            sister_wing = (40, 61)

        elif (61, 40) in sister_wings:
            checkerboard = True
            sister_wing = (61, 40)

        else:
            # Pick the sister_wing that is in the middle of the edge
            for x in sister_wings:
                if x in ((3, 103), (103, 3),
                         (11, 28), (28, 11),
                         (15, 78), (78, 15),
                         (23, 53), (53, 23),
                         (36, 115), (115, 36),
                         (40, 61), (61, 40),
                         (65, 86), (86, 65),
                         (48, 136), (136, 48),
                         (73, 128), (128, 73),
                         (90, 111), (111, 90),
                         (98, 140), (140, 98),
                         (123, 148), (148, 123)):
                    sister_wing = x
                    break

            else:
                self.print_cube()
                raise SolveError("Could not find sister wing in the middle: %s" % pformat(sister_wings))

        if checkerboard:
            # Flip one middle wing in place
            # No 1 at https://i.imgur.com/wsTqj.png
            self.rotate_x()
            self.rotate_y_reverse()
            for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                self.rotate(step)
            return True

        else:

            # Move sister wing to F-east...TODO this needs to be smart enough to move it there
            # so that it doesn't need to be flipped once it is there.  The 4x4x4 edge pairing has this logic.
            self.move_wing_to_F_east(sister_wing)

            # We must have a sister wing at (65, 86)
            sister_wings_on_FR_edge = self.get_wings_on_edge(target_wing, 'F', 'R')
            if (65, 86) not in sister_wings_on_FR_edge:
                self.print_cube()
                log.info("sister_wings_on_FR_edge %s" % pformat(sister_wings_on_FR_edge))
                raise SolveError("sister wing should be on FR edge")

            sister_wing = (65, 86)
            sister_wing_value = self.get_wing_value(sister_wing)

            # The sister wing is in the right location but does it need to be flipped?
            if target_wing_value != sister_wing_value:
                for step in ("R", "U'", "B'", "R2"):
                    self.rotate(step)

            if sister_wing[0] == 65:
                # 3Uw Uw'
                if self.use_pair_outside_edges:
                    self.rotate("Uw'")
                self.rotate("Dw")
                self.rotate_y()

                placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

                # We paired all 8 wings on the slice forward so rotate the edges from U and D onto L and F and check again
                if not placed_unpaired_wing:
                    self.rotate("R")
                    self.rotate("L'")
                    self.rotate("U")
                    self.rotate("D")
                    self.rotate("R'")
                    self.rotate("L")
                    placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

                    if not placed_unpaired_wing:
                        log.info("pair_four_or_six_wings_555() failed...no unpaired wings to move to F-east")
                        return False

                #log.info("PREP-FOR-3Uw'-SLICE-BACK (end)...SLICE BACK (begin), %d left to pair" % self.get_non_paired_wings_count())
                #self.print_cube()

                # 3Uw' Uw
                if self.use_pair_outside_edges:
                    self.rotate("Uw")
                self.rotate("Dw'")
                self.rotate_y_reverse()

                #log.info("SLICE BACK (end), %d left to pair" % self.get_non_paired_wings_count())
                #self.verify_all_centers_solved()

            else:
                raise SolveError("sister_wing %s is in the wrong position" % str(sister_wing))

            current_non_paired_wings_count = self.get_non_paired_wings_count()
        wings_paired = original_non_paired_wings_count - current_non_paired_wings_count
        log.info("pair_one_wing_555() paired %d wings, added %d steps" % (wings_paired, self.get_solution_len_minus_rotates(self.solution) - original_solution_len))

        if self.use_pair_outside_edges:
            if self.state[35] != self.state[45] or self.state[56] != self.state[66]:
                raise SolveError("outside edges have been broken")

        if wings_paired < 1:
            return False
            #raise SolveError("Paired %d wings" % wings_paired)
        else:
            return True

    def pair_edge(self, edge_to_pair):

        #log.info("pair_edge() with edge_to_pair %s" % pformat(edge_to_pair))
        pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
        pre_non_paired_edges_count = self.get_non_paired_edges_count()
        pre_non_paired_wings_count = self.get_non_paired_wings_count()
        self.rotate_edge_to_F_west(edge_to_pair[0])

        # We need to rotate this around so the two unpaired wings are at the bottom of F-west
        if self.state[40] == self.state[45] and self.state[61] == self.state[66]:
            self.rotate_z()
            self.rotate_z()
            self.rotate_y()

        log.info("pair_edge() for %s (%d wings and %d edges left to pair)" % (pformat(edge_to_pair), pre_non_paired_wings_count, pre_non_paired_edges_count))

        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        if self.use_pair_outside_edges:
            if self.state[35] != self.state[45] or self.state[56] != self.state[66]:
                raise SolveError("outside edges have been broken")

        if self.pair_checkboard_edge_555(pre_solution_len, pre_non_paired_wings_count):
            return True

        # Pair two sister edges...all colors involved live on two edges so this
        # is just like solving the last two edges
        if self.pair_two_sister_edges_555(pre_solution_len, pre_non_paired_wings_count, pre_non_paired_edges_count):
            return True

        original_state = self.state[:]
        original_solution = self.solution[:]

        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        if pre_non_paired_edges_count >= 4:
            if self.pair_four_or_six_wings_555(edge_to_pair[0], pre_non_paired_edges_count):
                return True
            else:
                self.state = original_state[:]
                self.solution = original_solution[:]

        # TODO now we need to try to pair 4 at a time
        if self.pair_one_wing_555():
            return True
        else:
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

    def group_edges_recursive(self, depth, edge_to_pair):

        # Should we both going down this branch or should we prune it?
        pre_non_paired_wings_count = len(self.get_non_paired_wings())
        pre_non_paired_edges_count = len(self.get_non_paired_edges())
        edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len
        edge_paired = False

        log.info("")
        log.info("group_edges_recursive(%d) called with edge_to_pair %s (%d edges and %d wings left to pair, min solution len %s, current solution len %d)" %
            (depth,
             pformat(edge_to_pair),
             pre_non_paired_edges_count,
             pre_non_paired_wings_count,
             self.min_edge_solution_len,
             edge_solution_len))

        # Should we continue down this branch or should we prune it? An estimate
        # of 2.5 moves to pair an edge is a good target to hit so if the current number of
        # steps plus 2.5 * pre_non_paired_wings_count is greater than our current minimum
        # there isn't any point in continuing down this branch so prune it and save
        # some CPU cycles.
        #
        # I use 4 here just to make it run faster...this adds 4-6 moves on average but
        # it runs about 20x faster than using 2.5
        estimate_per_wing = 3.5

        # 9 moves is the least number of moves I know of that will pair the last 2 wings
        if pre_non_paired_wings_count == 2:
            estimated_solution_len = edge_solution_len + 9
        elif pre_non_paired_wings_count == 3:
            estimated_solution_len = edge_solution_len + 7
        elif pre_non_paired_wings_count == 4:
            estimated_solution_len = edge_solution_len + 8
        else:
            estimated_solution_len = edge_solution_len + (estimate_per_wing * pre_non_paired_wings_count)

        if estimated_solution_len >= self.min_edge_solution_len:
            log.info("PRUNE: %s non-paired wings, estimated_solution_len %d, %s + (%s * %d) > %s" %
                (pre_non_paired_wings_count, estimated_solution_len, edge_solution_len, estimate_per_wing, pre_non_paired_wings_count, self.min_edge_solution_len))
            return False

        # The only time this will be None is on the initial call
        if edge_to_pair:
            edge_paired = self.pair_edge(edge_to_pair)
        else:
            edge_paired = True

        non_paired_edges = self.get_non_paired_edges()

        # call group_edges_recursive for each edge left to pair
        if non_paired_edges:
            post_non_paired_wings_count = len(self.get_non_paired_wings())
            edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len
            wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count
            original_state = self.state[:]
            original_solution = self.solution[:]

            if edge_paired and edge_solution_len < self.min_edge_solution_len:
                log.info("group_edges_recursive(%d) paired %d" % (depth, wings_paired))
                for edge in non_paired_edges:
                    self.group_edges_recursive(depth+1, edge)
                    self.state = original_state[:]
                    self.solution = original_solution[:]
        else:

            # There are no edges left to pair, note how many steps it took pair them all
            edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len

            # Remember the solution that pairs all edges in the least number of moves
            if edge_solution_len < self.min_edge_solution_len:
                self.min_edge_solution_len = edge_solution_len
                self.min_edge_solution = self.solution[:]
                self.min_edge_solution_state = self.state[:]
                log.warning("NEW MIN: edges paired in %d steps" % self.min_edge_solution_len)
            #else:
            #    log.info("LOST   : edges paired in %s vs MIN %d steps" % (edge_solution_len, self.min_edge_solution_len))

            return True

    def group_edges(self):

        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        depth = 0
        self.lt_init()

        if self.use_pair_outside_edges:
            self.pair_outside_edges()
            self.print_cube()
            log.info('outside edges paired, %d steps in' % self.get_solution_len_minus_rotates(self.solution))

        self.center_solution_len = self.get_solution_len_minus_rotates(self.solution)

        # TODO Trying to find a way to speed up edge pairing...this needs more work
        '''
        for x in xrange(55, 100, 10):
            self.min_edge_solution_len = x
            self.min_edge_solution = None
            self.min_edge_solution_state = None

            self.group_edges_recursive(depth, None)

            if self.min_edge_solution:
                break
            raise SolveError("did not find edge solution")
        '''

        self.min_edge_solution_len = 9999
        self.min_edge_solution = None
        self.min_edge_solution_state = None
        self.group_edges_recursive(depth, None)
        self.state = self.min_edge_solution_state[:]
        self.solution = self.min_edge_solution[:]
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
