from copy import copy
from pprint import pformat
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA
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


class RubiksCube444(RubiksCube):
    """
    4x4x4 strategy
    - stage UD centers to sides U or D
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers
    - pair edges
    - solve as 3x3x3
    """

    def __init__(self, kociemba_string, debug=False):
        RubiksCube.__init__(self, kociemba_string, debug)

        if debug:
            log.setLevel(logging.DEBUG)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        """
        lookup-tables init
        """

        '''
        24!/(16! * 8!) is 735,471

        lookup-table-4x4x4-step01-UD-centers-stage.txt
        ==============================================
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
        self.lt_UD_centers_stage = LookupTable(self,
                                               'lookup-table-4x4x4-step01-UD-centers-stage.txt',
                                               'UD-centers-stage',
                                               'UUUUxxxxxxxxxxxxxxxxUUUU',
                                                False,
                                                735471)


        '''
        16!/(8! * 8!) is 12,870

        lookup-table-4x4x4-step02-LR-centers-stage.txt
        ==============================================
        1 steps has 3 entries (0 percent)
        2 steps has 29 entries (0 percent)
        3 steps has 234 entries (1 percent)
        4 steps has 1,246 entries (9 percent)
        5 steps has 4,466 entries (34 percent)
        6 steps has 6,236 entries (48 percent)
        7 steps has 656 entries (5 percent)

        Total: 12,870 entries
        '''
        self.lt_LR_centers_stage = LookupTable(self,
                                               'lookup-table-4x4x4-step02-LR-centers-stage.txt',
                                               'LR-centers-stage',
                                               'LLLLxxxxLLLLxxxx',
                                                False,
                                                12870)


        '''
        (8!/(4! * 4!))^3 is 343,000

        lookup-table-4x4x4-step03-ULFRBD-centers-solve.txt
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
                                                   'lookup-table-4x4x4-step03-ULFRBD-centers-solve.txt',
                                                   'ULFRBD-centers-solve',
                                                   'UUUULLLLFFFFRRRRBBBBDDDD',
                                                   False,
                                                   343000)

        '''
        This is an experiment to see if I can solve all centers at once using IDA
        I let it run for about 5 minutes but it still didn't find a solution...need to let
        it run overnight. If that doesn't work build the step30 table out to 7-deep.


        lookup-table-4x4x4-step30-ULFRBD-centers-solve-not-staged.txt
        =============================================================
        1 steps has 19 entries (0 percent, 0.00x previous step)
        2 steps has 459 entries (0 percent, 24.16x previous step)
        3 steps has 10,272 entries (0 percent, 22.38x previous step)
        4 steps has 218,195 entries (0 percent, 21.24x previous step)
        5 steps has 4,384,602 entries (4 percent, 20.09x previous step)
        6 steps has 83,113,883 entries (94 percent, 18.96x previous step)

        Total: 87,727,430 entries


        lookup-table-4x4x4-step31-UD-centers-solve.txt
        lookup-table-4x4x4-step32-LR-centers-solve.txt
        lookup-table-4x4x4-step33-FB-centers-solve.txt
        ==============================================
        1 steps has 13 entries (0 percent, 0.00x previous step)
        2 steps has 205 entries (0 percent, 15.77x previous step)
        3 steps has 3,526 entries (0 percent, 17.20x previous step)
        4 steps has 53,778 entries (0 percent, 15.25x previous step)
        5 steps has 691,972 entries (1 percent, 12.87x previous step)
        6 steps has 6,685,690 entries (12 percent, 9.66x previous step)
        7 steps has 28,771,914 entries (55 percent, 4.30x previous step)
        8 steps has 15,187,532 entries (29 percent, 0.53x previous step)
        9 steps has 88,340 entries (0 percent, 0.01x previous step)

        Total: 51,482,970 entries
        '''
        self.lt_UD_centers_solve = LookupTable(self,
                                               'lookup-table-4x4x4-step31-UD-centers-solve.txt',
                                               'UD-centers-solve-on-all',
                                               'UUUUxxxxxxxxxxxxxxxxDDDD',
                                               False, # state_hex
                                               51482979)

        self.lt_LR_centers_solve = LookupTable(self,
                                               'lookup-table-4x4x4-step32-LR-centers-solve.txt',
                                               'LR-centers-solve-on-all',
                                               'xxxxLLLLxxxxRRRRxxxxxxxx',
                                               False, # state_hex
                                               51482970)

        self.lt_FB_centers_solve = LookupTable(self,
                                               'lookup-table-4x4x4-step33-FB-centers-solve.txt',
                                               'FB-centers-solve-on-all',
                                               'xxxxxxxxFFFFxxxxBBBBxxxx',
                                               False, # state_hex
                                               51482970)

        self.lt_ULFRBD_centers_solve_not_staged = LookupTableIDA(self,
                                                                'lookup-table-4x4x4-step30-ULFRBD-centers-solve-not-staged.txt',
                                                                'ULFRBD-centers-solve',
                                                                'UUUULLLLFFFFRRRRBBBBDDDD',
                                                                False, # state_hex
                                                                87727430,
                                                                moves_4x4x4,
                                                                (), # illegal_moves

                                                                # prune tables
                                                                (self.lt_UD_centers_solve,
                                                                 self.lt_LR_centers_solve,
                                                                 self.lt_FB_centers_solve))

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
                                                 'TBD',
                                                 False,
                                                 7920)

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
                                                  'TBD',
                                                  False,
                                                  7919)

    def group_centers_guts(self):
        self.lt_init()

        # The UD solve -> LFRB solve approach is only ~1 move shorter on average
        # than doing UD stage, LR stage, ULFRBD solve.  The UD solve -> LFRB
        # lookup tables are 5.6G where the UD stage, LR stage, ULFRBD solve
        # lookup tables are only 49M...we use the 49M tables so we can check
        # them into the github repo.
        self.lt_UD_centers_stage.solve()
        self.lt_LR_centers_stage.solve()
        self.lt_ULFRBD_centers_solve.solve()

        # experiment
        #self.lt_ULFRBD_centers_solve_not_staged.solve()

    def group_edges(self):
        self.lt_init()
        original_non_paired_edges = self.get_non_paired_edges()

        if not original_non_paired_edges:
            self.solution.append('EDGES_GROUPED')
            return

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        # There are 12 edges, cycle through all 12 in terms of which edge we try to pair first.
        # Remember the one that results in the shortest solution that is free of PLL parity.
        min_solution_length = None
        min_solution_state = None
        min_solution = None
        min_solution_has_pll = True

        # There are some cubes where I always hit PLL parity when I pair multiple
        # edges at a time, so try with this capability first and if we fail to find
        # a PLL free solution then turn it off.
        for pair_multiple_edges_at_once in (True, False):
            for init_wing_to_pair in original_non_paired_edges:
                log.info("init_wing_to_pair %20s" % pformat(init_wing_to_pair))

                while True:
                    non_paired_edges = self.get_non_paired_edges()
                    len_non_paired_edges = len(non_paired_edges)

                    if len_non_paired_edges == 0:
                        break

                    if init_wing_to_pair:
                        wing_to_pair = init_wing_to_pair[0]
                        init_wing_to_pair = None
                    else:
                        wing_to_pair = non_paired_edges[0][0]

                    if len_non_paired_edges > 6:
                        if not self.pair_six_edges_444(wing_to_pair):
                            log.info("pair_six_edges_444()    returned False")

                            if not self.pair_four_edges_444(wing_to_pair):
                                log.info("pair_four_edges_444() returned False")
                                self.pair_two_edges_444(wing_to_pair, pair_multiple_edges_at_once)

                    elif len_non_paired_edges == 6 and pair_multiple_edges_at_once:
                        if not self.pair_last_six_edges_444():
                            log.info("pair_last_six_edges_444() returned False")

                            if not self.pair_four_edges_444(wing_to_pair):
                                log.info("pair_four_edges_444() returned False")
                                self.pair_two_edges_444(wing_to_pair, pair_multiple_edges_at_once)

                    elif len_non_paired_edges >= 4:
                        if not self.pair_four_edges_444(wing_to_pair):
                            log.info("pair_four_edges_444() returned False")
                            self.pair_two_edges_444(wing_to_pair, pair_multiple_edges_at_once)

                    elif len_non_paired_edges == 2:
                        self.pair_last_two_edges_444(wing_to_pair)

                    # The scenario where you have 3 unpaired edges
                    elif len_non_paired_edges > 2:
                        self.pair_two_edges_444(wing_to_pair, pair_multiple_edges_at_once)

                    else:
                        break

                solution_len_minus_rotates = self.get_solution_len_minus_rotates(self.solution)
                leads_to_pll = self.edge_solution_leads_to_pll_parity()
                new_min = False

                if leads_to_pll:
                    log.info("edges solution length %d, leads to PLL parity" % (solution_len_minus_rotates - original_solution_len))

                if min_solution_length is None:
                    new_min = True

                elif min_solution_has_pll:
                    if leads_to_pll:
                        if solution_len_minus_rotates < min_solution_length:
                            new_min = True
                    else:
                        new_min = True

                elif not leads_to_pll and solution_len_minus_rotates < min_solution_length:
                    new_min = True

                if new_min:
                    min_solution_has_pll = leads_to_pll
                    min_solution_length = solution_len_minus_rotates
                    min_solution_state = copy(self.state)
                    min_solution = copy(self.solution)
                    log.warning("edges solution length %d (NEW MIN)" % (solution_len_minus_rotates - original_solution_len))
                else:
                    log.info("edges solution length %d" % (solution_len_minus_rotates - original_solution_len))
                log.info('')

                # Restore to original state
                self.state = copy(original_state)
                self.solution = copy(original_solution)

            # If we were able to find a PLL free solution when pair_multiple_edges_at_once
            # was True then break, there is not point trying with pair_multiple_edges_at_once
            # False since those solutions will all be longer
            if min_solution_length and not min_solution_has_pll:
                break
            else:
                log.warning("Could not find PLL free edge solution with pair_multiple_edges_at_once True")

        self.state = copy(min_solution_state)
        self.solution = copy(min_solution)

        if self.get_non_paired_edges_count():
            raise SolveError("All edges should be resolved")

        self.solution.append('EDGES_GROUPED')

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
        original_state = copy(self.state)
        original_solution = copy(self.solution)
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
            self.state = copy(original_state)
            self.solution = copy(original_solution)
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
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        if not self.prep_for_slice_back_444():
            #raise SolveError("cannot slice back")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
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
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_non_paired_edges = self.get_non_paired_edges()

        min_solution_len = None
        min_solution_state = None
        min_solution = None

        for wing_to_pair in original_non_paired_edges:
            self.state = copy(original_state)
            self.solution = copy(original_solution)
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
                min_solution_state = copy(self.state)
                min_solution = copy(self.solution)
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
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

    def pair_four_edges_444(self, edge):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
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
            self.state = copy(original_state)
            self.solution = copy(original_solution)
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

    def pair_two_edges_444(self, edge, pair_multiple_edges_at_once):
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

        # Now that that two edges on F are in place, put an unpaired edge at U-west
        if pair_multiple_edges_at_once:

            # The unpaired edge that we place at U-west should contain the
            # sister wing of the wing that is at the bottom of F-east. This
            # will allow us to pair two wings at once.
            wing_bottom_F_east = self.sideF.edge_east_pos[-1]
            sister_wing_bottom_F_east = self.get_wings(wing_bottom_F_east)[0]

            if sister_wing_bottom_F_east not in lookup_table_444_sister_wing_to_U_west:
                raise ImplementThis("sister_wing_bottom_F_east %s" % pformat(sister_wing_bottom_F_east))

            steps = lookup_table_444_sister_wing_to_U_west[sister_wing_bottom_F_east]

            # If steps is None it means sister_wing_bottom_F_east is at (37, 24)
            # which is the top wing on F-west. If that is the case we can't pair
            # two edges at once so just put some random unpaired edge at U-west
            if steps == None:
                self.make_U_west_have_unpaired_edge()
            else:
                for step in steps.split():
                    self.rotate(step)
        else:
            self.make_U_west_have_unpaired_edge()

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
        rotated around. It wasn't worth it...what I have below works just find and
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

        if current_non_paired_wings_count:
            raise SolveError("Failed to pair last two edges")

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


# Code below here is no longer...maybe I am saving it for a rainy day
'''
    def find_moves_to_reach_state(self, wing_to_move, target_face_side):
        """
        This was used to build the lookup_table_444_last_two_edges_place_F_east, etc lookup tables
        """
        original_state = copy(self.state)
        original_solution = copy(self.solution)

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

                self.state = copy(original_state)
                self.solution = copy(original_solution)

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
